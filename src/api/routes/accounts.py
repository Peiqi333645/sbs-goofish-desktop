"""
闲鱼账号管理路由
"""
import asyncio
import json
import os
import re
import uuid
import aiofiles
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List
from playwright.async_api import async_playwright
from src.infrastructure.config.env_manager import env_manager


router = APIRouter(prefix="/api/accounts", tags=["accounts"])

ACCOUNT_NAME_RE = re.compile(r"^[\w\u4e00-\u9fff-]{1,50}$", re.UNICODE)


class AccountCreate(BaseModel):
    name: str
    content: str


class AccountUpdate(BaseModel):
    content: str


class QrLoginStart(BaseModel):
    name: str


_qr_sessions: Dict[str, dict] = {}
_qr_tasks: Dict[str, asyncio.Task] = {}


def _strip_quotes(value: str) -> str:
    if not value:
        return value
    if value.startswith(("\"", "'")) and value.endswith(("\"", "'")):
        return value[1:-1]
    return value


def _state_dir() -> str:
    raw = env_manager.get_value("ACCOUNT_STATE_DIR", "state") or "state"
    return _strip_quotes(raw.strip())


def _ensure_state_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _validate_name(name: str) -> str:
    trimmed = name.strip()
    if not trimmed or not ACCOUNT_NAME_RE.match(trimmed):
        raise HTTPException(status_code=400, detail="账号名称只能包含中文、字母、数字、下划线或短横线。")
    return trimmed


def _account_path(name: str) -> str:
    filename = f"{name}.json"
    return os.path.join(_state_dir(), filename)


def _cookie_map(cookies: list) -> dict:
    return {
        str(item.get("name", "")): str(item.get("value", ""))
        for item in cookies
        if isinstance(item, dict)
    }


def _has_authenticated_identity(cookies: list) -> bool:
    """Require account identity cookies; anonymous tracking cookies are not login proof."""
    values = _cookie_map(cookies)
    user_id = values.get("unb") or values.get("cookie17")
    nickname = values.get("tracknick") or values.get("lgc")
    authenticated_session = values.get("cookie2") and values.get("t")
    return bool(user_id and (nickname or authenticated_session))


def _validate_json(content: str) -> None:
    try:
        state = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="提供的内容不是有效的JSON格式。")
    if not isinstance(state, dict) or not isinstance(state.get("cookies"), list):
        raise HTTPException(status_code=400, detail="这不是Playwright登录状态JSON，缺少cookies列表。")
    if not _has_authenticated_identity(state["cookies"]):
        raise HTTPException(status_code=400, detail="JSON中没有检测到已登录的闲鱼账号身份，请重新登录后导出。")


async def _run_qr_login(session_id: str, account_name: str) -> None:
    """Open the official Xianyu page and persist Playwright storage state after login."""
    browser = None
    playwright = None
    try:
        _qr_sessions[session_id] = {
            "status": "opening",
            "message": "正在打开闲鱼官方扫码页面…",
            "name": account_name,
        }
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(locale="zh-CN")
        page = await context.new_page()
        await page.goto("https://www.goofish.com/", wait_until="domcontentloaded", timeout=60000)
        _qr_sessions[session_id].update(
            status="waiting",
            message="请使用手机淘宝扫描浏览器中的官方二维码并确认登录。",
        )

        for _ in range(200):
            await asyncio.sleep(1.5)
            if page.is_closed():
                raise RuntimeError("登录窗口已关闭，尚未检测到真实账号登录。")
            cookies = await context.cookies()
            if _has_authenticated_identity(cookies):
                # Wait once more so cookies/localStorage finish writing after mobile confirmation.
                await asyncio.sleep(2)
                confirmed_cookies = await context.cookies()
                if not _has_authenticated_identity(confirmed_cookies):
                    continue
                state_dir = _state_dir()
                _ensure_state_dir(state_dir)
                path = _account_path(account_name)
                if os.path.exists(path):
                    raise RuntimeError("该账号名称已经存在，请更换名称。")
                await context.storage_state(path=path)
                _qr_sessions[session_id].update(
                    status="success",
                    message="已检测到真实闲鱼账号身份，登录状态已保存到本机。",
                    path=path,
                )
                return

        raise RuntimeError("二维码已超时，请重新发起扫码登录。")
    except asyncio.CancelledError:
        _qr_sessions[session_id].update(status="cancelled", message="扫码登录已取消。")
        raise
    except Exception as exc:
        _qr_sessions[session_id].update(status="error", message=str(exc))
    finally:
        if browser:
            await browser.close()
        if playwright:
            await playwright.stop()
        _qr_tasks.pop(session_id, None)


@router.post("/qr-login", response_model=dict)
async def start_qr_login(data: QrLoginStart):
    account_name = _validate_name(data.name)
    if os.path.exists(_account_path(account_name)):
        raise HTTPException(status_code=409, detail="账号名称已经存在")
    session_id = uuid.uuid4().hex
    _qr_sessions[session_id] = {
        "status": "starting",
        "message": "正在准备扫码登录…",
        "name": account_name,
    }
    _qr_tasks[session_id] = asyncio.create_task(_run_qr_login(session_id, account_name))
    return {"session_id": session_id, **_qr_sessions[session_id]}


@router.get("/qr-login/{session_id}", response_model=dict)
async def get_qr_login_status(session_id: str):
    session = _qr_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="扫码会话不存在或已经过期")
    return {"session_id": session_id, **session}


@router.delete("/qr-login/{session_id}", response_model=dict)
async def cancel_qr_login(session_id: str):
    task = _qr_tasks.get(session_id)
    if task and not task.done():
        task.cancel()
    session = _qr_sessions.get(session_id)
    if session:
        session.update(status="cancelled", message="扫码登录已取消。")
    return {"message": "扫码登录已取消"}


@router.get("", response_model=List[dict])
async def list_accounts():
    state_dir = _state_dir()
    if not os.path.isdir(state_dir):
        return []
    files = [f for f in os.listdir(state_dir) if f.endswith(".json")]
    accounts = []
    for filename in sorted(files):
        name = filename[:-5]
        accounts.append({
            "name": name,
            "path": os.path.join(state_dir, filename),
        })
    return accounts


@router.get("/{name}", response_model=dict)
async def get_account(name: str):
    account_name = _validate_name(name)
    path = _account_path(account_name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="账号不存在")
    async with aiofiles.open(path, "r", encoding="utf-8") as f:
        content = await f.read()
    return {"name": account_name, "path": path, "content": content}


@router.post("", response_model=dict)
async def create_account(data: AccountCreate):
    account_name = _validate_name(data.name)
    _validate_json(data.content)
    state_dir = _state_dir()
    _ensure_state_dir(state_dir)
    path = _account_path(account_name)
    if os.path.exists(path):
        raise HTTPException(status_code=409, detail="账号已存在")
    async with aiofiles.open(path, "w", encoding="utf-8") as f:
        await f.write(data.content)
    return {"message": "账号已添加", "name": account_name, "path": path}


@router.put("/{name}", response_model=dict)
async def update_account(name: str, data: AccountUpdate):
    account_name = _validate_name(name)
    _validate_json(data.content)
    state_dir = _state_dir()
    _ensure_state_dir(state_dir)
    path = _account_path(account_name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="账号不存在")
    async with aiofiles.open(path, "w", encoding="utf-8") as f:
        await f.write(data.content)
    return {"message": "账号已更新", "name": account_name, "path": path}


@router.delete("/{name}", response_model=dict)
async def delete_account(name: str):
    account_name = _validate_name(name)
    path = _account_path(account_name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="账号不存在")
    os.remove(path)
    return {"message": "账号已删除"}

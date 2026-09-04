"""Derive lightweight per-task progress from the task's existing log stream."""

from __future__ import annotations

import os
import re
from typing import Any

from src.utils import resolve_task_log_path


_PAGE = re.compile(r"开始处理第\s*(\d+)/(\d+)\s*页")
_ITEM = re.compile(r"\[页内进度\s*(\d+)/(\d+)\]")
_STRICT = re.compile(r"累计(?:命中|获取)\s*(\d+)\s*条")
_DETAIL = re.compile(r"累计处理\s*(\d+)\s*个新商品")
_ANALYSIS = re.compile(r"后台分析.*?累计处理\s*(\d+)\s*个新商品")
_RUN_MARKERS = ("步骤 0 - 模拟真实用户访问首页", "LOG: 发现已存在结果集", "LOG: 结果集")


def _tail_text(path: str, limit: int = 256_000) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as handle:
        handle.seek(0, os.SEEK_END)
        size = handle.tell()
        handle.seek(max(0, size - limit))
        return handle.read().decode("utf-8", errors="replace")


def _latest_run(text: str) -> str:
    start = -1
    for marker in _RUN_MARKERS:
        start = max(start, text.rfind(marker))
    return text[start:] if start >= 0 else text


def _last_pair(pattern: re.Pattern[str], text: str) -> tuple[int, int]:
    matches = pattern.findall(text)
    return tuple(map(int, matches[-1])) if matches else (0, 0)


def _last_number(pattern: re.Pattern[str], text: str) -> int:
    matches = pattern.findall(text)
    return int(matches[-1]) if matches else 0


def build_task_progress(task: Any, *, is_running: bool) -> dict[str, Any]:
    text = _latest_run(_tail_text(resolve_task_log_path(task.id, task.task_name)))
    page, logged_max_pages = _last_pair(_PAGE, text)
    item, page_items = _last_pair(_ITEM, text)
    max_pages = logged_max_pages or int(getattr(task, "max_pages", 1) or 1)
    matched = _last_number(_STRICT, text)
    detail_completed = _last_number(_DETAIL, text)
    analysis_completed = _last_number(_ANALYSIS, text)

    completed = "所有任务执行完毕" in text or "正常结束" in text
    failed = "因异常而终止" in text or "本次尝试失败" in text
    if is_running:
        stage = "analyzing" if "等待后台分析任务完成" in text else "scraping"
    elif failed:
        stage = "failed"
    elif completed:
        stage = "completed"
    else:
        stage = "idle"

    if stage == "completed":
        percent = 100
    elif stage == "idle":
        percent = 0
    elif max_pages > 0:
        page_fraction = (item / page_items) if page_items else 0
        percent = round(min(99, max(1, ((max(page, 1) - 1 + page_fraction) / max_pages) * 100)))
    else:
        percent = 1

    return {
        "task_id": task.id,
        "task_name": task.task_name,
        "keyword": task.keyword,
        "is_running": is_running,
        "stage": stage,
        "percent": percent,
        "page": page,
        "max_pages": max_pages,
        "page_item": item,
        "page_items": page_items,
        "matched_count": matched,
        "detail_completed": detail_completed,
        "analysis_completed": analysis_completed,
    }

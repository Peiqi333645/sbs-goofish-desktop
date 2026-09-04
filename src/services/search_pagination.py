import asyncio
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Optional

from playwright.async_api import TimeoutError as PlaywrightTimeoutError

from src.utils import log_time, random_sleep

NEXT_PAGE_SELECTOR = (
    "button[class*='search-pagination-arrow-container']"
    ":has([class*='search-pagination-arrow-right'])"
    ":not([disabled])"
)
SEARCH_RESULTS_API_MARKER = "idlemtopsearch"
PAGE_REQUEST_TIMEOUT_MS = 20_000
PAGE_CLICK_TIMEOUT_MS = 10_000
PAGE_RETRY_DELAY_SECONDS = 5
PAGE_RETRY_COUNT = 2
PAGE_CLICK_SLEEP_MIN_SECONDS = 2
PAGE_CLICK_SLEEP_MAX_SECONDS = 5


class _PageClickTimeout(Exception):
    pass


def is_search_result_payload(payload: Any) -> bool:
    """Validate that resultList contains marketplace product cards."""
    if not isinstance(payload, dict):
        return False
    result_list = (payload.get("data") or {}).get("resultList")
    if not isinstance(result_list, list) or not result_list:
        return False
    product_count = 0
    for entry in result_list:
        try:
            main = entry["data"]["item"]["main"]
            content = main["exContent"]
            if content.get("itemId") and content.get("title") and main.get("targetUrl"):
                product_count += 1
        except (KeyError, TypeError):
            continue
    return product_count >= min(3, len(result_list))


async def capture_search_results_response(
    *,
    page: Any,
    action: Callable[[], Awaitable[Any]],
    timeout_ms: int = 30_000,
    logger: Callable[[str], None] = log_time,
) -> Any:
    """Capture a search payload by shape instead of an unstable mtop URL.

    Goofish changes endpoint names, versions, and request methods regularly. The
    stable contract used by the parser is the JSON ``data.resultList`` array.
    """
    loop = asyncio.get_running_loop()
    matched_response = loop.create_future()
    inspection_tasks: set[asyncio.Task] = set()
    candidate_urls: list[str] = []

    async def inspect(response: Any) -> None:
        if matched_response.done():
            return
        try:
            request = getattr(response, "request", None)
            resource_type = getattr(request, "resource_type", "")
            if resource_type and resource_type not in {"xhr", "fetch", "document"}:
                return
            url = str(getattr(response, "url", ""))
            if url:
                candidate_urls.append(url)
                del candidate_urls[:-20]
            payload = await response.json()
            normalized_url = url.lower()
            looks_like_search_url = (
                SEARCH_RESULTS_API_MARKER in normalized_url
                or "search" in normalized_url
            ) and not any(
                marker in normalized_url
                for marker in ("recommend", "suggest", ".shade", "history")
            )
            if (
                looks_like_search_url
                and is_search_result_payload(payload)
                and not matched_response.done()
            ):
                matched_response.set_result(response)
        except Exception:
            return

    def on_response(response: Any) -> None:
        task = asyncio.create_task(inspect(response))
        inspection_tasks.add(task)
        task.add_done_callback(inspection_tasks.discard)

    page.on("response", on_response)
    try:
        await action()
        return await asyncio.wait_for(
            asyncio.shield(matched_response), timeout=timeout_ms / 1000
        )
    except asyncio.TimeoutError as exc:
        if inspection_tasks:
            await asyncio.gather(*tuple(inspection_tasks), return_exceptions=True)
        diagnostic = "\n".join(candidate_urls[-10:]) or "未观察到 XHR/fetch JSON 响应"
        logger(f"未识别到包含真实商品列表的搜索响应。最近候选请求:\n{diagnostic}")
        raise PlaywrightTimeoutError(
            f"Timeout {timeout_ms}ms exceeded while waiting for search result payload"
        ) from exc
    finally:
        page.remove_listener("response", on_response)


@dataclass(frozen=True)
class PageAdvanceResult:
    advanced: bool
    response: Optional[Any] = None
    stop_reason: Optional[str] = None


def is_search_results_response(
    response: Any,
    api_url_fragment: str = SEARCH_RESULTS_API_MARKER,
) -> bool:
    request = getattr(response, "request", None)
    request_method = getattr(request, "method", None)
    response_url = getattr(response, "url", "")
    normalized_url = str(response_url).lower()
    # 闲鱼会调整 mtop 接口版本，也可能在 GET/POST 之间切换。这里只识别
    # 真正的商品搜索接口，避免版本号和请求方法变化导致整次搜索为 0。
    excluded_markers = (".shade", "suggest", "recommend", "history")
    return (
        api_url_fragment.lower() in normalized_url
        and not any(marker in normalized_url for marker in excluded_markers)
        and request_method in {"GET", "POST"}
    )


async def advance_search_page(
    *,
    page: Any,
    page_num: int,
    logger: Callable[[str], None] = log_time,
    wait_after_click: Callable[[float, float], Awaitable[None]] = random_sleep,
    retry_sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    capture_response: Callable[..., Awaitable[Any]] = capture_search_results_response,
    max_retries: int = PAGE_RETRY_COUNT,
) -> PageAdvanceResult:
    next_button = page.locator(NEXT_PAGE_SELECTOR).first
    if not await next_button.count():
        logger("已到达最后一页，未找到可用的'下一页'按钮，停止翻页。")
        return PageAdvanceResult(advanced=False, stop_reason="no_next_button")

    for retry_index in range(max_retries):
        try:
            await next_button.scroll_into_view_if_needed()
            async def click_next_page() -> None:
                try:
                    await next_button.click(timeout=PAGE_CLICK_TIMEOUT_MS)
                except PlaywrightTimeoutError:
                    logger(f"第 {page_num} 页下一页按钮点击超时，停止翻页。")
                    raise _PageClickTimeout

            response = await capture_response(
                page=page,
                action=click_next_page,
                timeout_ms=PAGE_REQUEST_TIMEOUT_MS,
                logger=logger,
            )
            await wait_after_click(
                PAGE_CLICK_SLEEP_MIN_SECONDS,
                PAGE_CLICK_SLEEP_MAX_SECONDS,
            )
            return PageAdvanceResult(
                advanced=True,
                response=response,
            )
        except _PageClickTimeout:
            return PageAdvanceResult(advanced=False, stop_reason="click_timeout")
        except PlaywrightTimeoutError:
            if retry_index < max_retries - 1:
                logger(
                    f"等待第 {page_num} 页搜索响应超时，"
                    f"{PAGE_RETRY_DELAY_SECONDS}秒后重试..."
                )
                await retry_sleep(PAGE_RETRY_DELAY_SECONDS)
                continue

            logger(f"等待第 {page_num} 页搜索响应超时 {max_retries} 次，停止翻页。")
            return PageAdvanceResult(advanced=False, stop_reason="response_timeout")

    return PageAdvanceResult(advanced=False, stop_reason="unknown")

"""Local relevance checks for noisy marketplace search results."""

import re


_TOKEN_SPLIT = re.compile(r"[\s,，、/|]+")
_COMPACT = re.compile(r"[^0-9a-z\u4e00-\u9fff]+")
_TOKEN_PARTS = re.compile(r"[\u4e00-\u9fff]+|[a-z0-9]+")


def normalize_search_token(value: str) -> str:
    return _COMPACT.sub("", str(value or "").lower())


def title_matches_search_keyword(keyword: str, title: str) -> bool:
    """Require every user-entered search token to occur in the title."""
    title_source = str(title or "").lower()
    title_text = normalize_search_token(title_source)
    tokens = []
    for raw_token in _TOKEN_SPLIT.split(str(keyword or "").strip().lower()):
        tokens.extend(_TOKEN_PARTS.findall(normalize_search_token(raw_token)))
    tokens = [token for token in tokens if token]
    if not title_text or not tokens:
        return False
    for token in tokens:
        if token.isascii() and token.isalnum():
            # Model names are commonly glued to a brand (CONTAXG1), but must
            # not let G1 match G10/G21. Plain words keep both boundaries.
            has_digit = any(char.isdigit() for char in token)
            haystack = title_text if has_digit else title_source
            left_boundary = "" if has_digit else r"(?<![a-z0-9])"
            if re.search(rf"{left_boundary}{re.escape(token)}(?![a-z0-9])", haystack) is None:
                return False
        elif token not in title_text:
            return False
    return True


def filter_search_items(keyword: str, items: list[dict]) -> list[dict]:
    return [
        item
        for item in items
        if title_matches_search_keyword(keyword, item.get("商品标题", ""))
    ]

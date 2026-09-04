"""Local relevance checks for noisy marketplace search results."""

import re


_TOKEN_SPLIT = re.compile(r"[\s,，、/|]+")
_COMPACT = re.compile(r"[^0-9a-z\u4e00-\u9fff]+")
_TOKEN_PARTS = re.compile(r"[\u4e00-\u9fff]+|[a-z0-9]+")


def normalize_search_token(value: str) -> str:
    return _COMPACT.sub("", str(value or "").lower())


def title_matches_search_keyword(keyword: str, title: str) -> bool:
    """Keep marketplace relevance while protecting explicit model searches.

    Generic category queries such as ``相机`` must trust Goofish ranking because
    legitimate titles often only contain a brand/model.  Tokens containing a
    digit (G1, A7M4, iPhone15) are distinctive enough to validate locally.
    """
    title_text = normalize_search_token(title)
    tokens = []
    for raw_token in _TOKEN_SPLIT.split(str(keyword or "").strip().lower()):
        tokens.extend(_TOKEN_PARTS.findall(normalize_search_token(raw_token)))
    tokens = [token for token in tokens if token]
    if not title_text or not tokens:
        return False
    model_tokens = [token for token in tokens if any(char.isdigit() for char in token)]
    if not model_tokens:
        return True
    for token in model_tokens:
        # Model names are commonly glued to a brand (CONTAXG1), but the right
        # boundary prevents G1 from matching G10/G21.
        if re.search(rf"{re.escape(token)}(?![a-z0-9])", title_text) is None:
            return False
    return True


def filter_search_items(keyword: str, items: list[dict]) -> list[dict]:
    return [
        item
        for item in items
        if title_matches_search_keyword(keyword, item.get("商品标题", ""))
    ]

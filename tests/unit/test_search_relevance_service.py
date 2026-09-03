from src.services.search_relevance_service import (
    filter_search_items,
    title_matches_search_keyword,
)


def test_title_match_ignores_case_spaces_and_punctuation():
    assert title_matches_search_keyword("康泰时 G1", "康泰时 CONTAX-G1 绿标机身")
    assert title_matches_search_keyword("Sony A7M4", "SONY-A7M4 单机身")


def test_title_match_rejects_related_but_different_models():
    assert not title_matches_search_keyword("康泰时 G1", "康泰时 G2 旁轴相机")
    assert not title_matches_search_keyword("康泰时 G1", "康泰时 G21mm 镜头")
    assert not title_matches_search_keyword("康泰时G1", "康泰时 G10 相机")


def test_filter_keeps_only_strict_title_matches():
    items = [
        {"商品标题": "康泰时 G1 绿标"},
        {"商品标题": "康泰时 G2 银色"},
    ]
    assert filter_search_items("康泰时 G1", items) == [items[0]]

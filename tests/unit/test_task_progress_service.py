from types import SimpleNamespace

from src.services.task_progress_service import build_task_progress


def test_build_task_progress_reads_latest_counts(monkeypatch, tmp_path):
    log_path = tmp_path / "task.log"
    log_path.write_text(
        "步骤 0 - 模拟真实用户访问首页\n"
        "开始处理第 2/10 页\n"
        "[相关性筛选] 第 2/10 页返回 20 条，保留 3 条，累计命中 8 条。\n"
        "[页内进度 2/3] 发现新商品\n"
        "商品已提交后台分析。累计处理 7 个新商品。\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "src.services.task_progress_service.resolve_task_log_path",
        lambda *_: str(log_path),
    )
    task = SimpleNamespace(id=1, task_name="相机", keyword="康泰时 G1", max_pages=10)
    progress = build_task_progress(task, is_running=True)
    assert progress["page"] == 2
    assert progress["matched_count"] == 8
    assert progress["detail_completed"] == 7
    assert progress["percent"] == 17

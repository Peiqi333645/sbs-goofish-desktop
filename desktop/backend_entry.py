"""Desktop entry point for the bundled FastAPI service and scraper worker."""
from __future__ import annotations

import asyncio
import os
import shutil
import sys
from pathlib import Path


def _bundle_root() -> Path:
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))


def _prepare_user_data() -> Path:
    data_dir = Path(os.environ.get("SBS_USER_DATA_DIR", Path.cwd())).expanduser().resolve()
    data_dir.mkdir(parents=True, exist_ok=True)

    for name in ("data", "state", "logs", "images", "jsonl", "price_history", "prompts"):
        (data_dir / name).mkdir(parents=True, exist_ok=True)

    root = _bundle_root()
    for name in ("dist", "static"):
        source = root / name
        target = data_dir / name
        if source.exists():
            shutil.copytree(source, target, dirs_exist_ok=True)

    prompt_source = root / "prompts"
    if prompt_source.exists():
        shutil.copytree(prompt_source, data_dir / "prompts", dirs_exist_ok=True)

    env_example = root / ".env.example"
    env_target = data_dir / ".env"
    if env_example.exists() and not env_target.exists():
        shutil.copy2(env_example, env_target)

    os.chdir(data_dir)
    return data_dir


def _patch_worker_command() -> None:
    from src.services.process_service import ProcessService

    def build_spawn_command(self, task_name: str) -> list[str]:
        executable = os.environ.get("SBS_DESKTOP_EXECUTABLE", sys.executable)
        command = [executable, "--desktop-spider", "--task-name", task_name]
        debug_limit = str(os.getenv("SPIDER_DEBUG_LIMIT", "")).strip()
        if debug_limit.isdigit() and int(debug_limit) > 0:
            command.extend(["--debug-limit", debug_limit])
        return command

    ProcessService._build_spawn_command = build_spawn_command


def main() -> None:
    _prepare_user_data()

    if "--desktop-spider" in sys.argv:
        sys.argv.remove("--desktop-spider")
        from spider_v2 import main as spider_main

        asyncio.run(spider_main())
        return

    _patch_worker_command()
    from src.app import app
    import uvicorn

    port = int(os.environ.get("SERVER_PORT", "8765"))
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")


if __name__ == "__main__":
    main()

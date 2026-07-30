#!/usr/bin/env python3
"""将本地知识库 SQLite 数据库备份到指定的私有 GitHub 仓库。"""

from __future__ import annotations

import base64
import json
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATABASE = ROOT / "03-知识库" / "knowledge.db"
REPOSITORY = "kensenoo/-"
REMOTE_PATH = "knowledge.db"


def run_gh(*arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["gh", *arguments], text=True, capture_output=True, check=check)


def main() -> None:
    if not DATABASE.exists():
        raise SystemExit("未找到 knowledge.db，请先运行同步脚本。")
    existing = run_gh(
        "api", f"repos/{REPOSITORY}/contents/{REMOTE_PATH}", "--jq", ".sha", check=False
    )
    payload: dict[str, str] = {
        "message": "Backup knowledge database",
        "content": base64.b64encode(DATABASE.read_bytes()).decode("ascii"),
        "branch": "main",
    }
    if existing.returncode == 0 and existing.stdout.strip():
        payload["sha"] = existing.stdout.strip()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", encoding="utf-8", delete=False) as handle:
        json.dump(payload, handle)
        payload_path = Path(handle.name)
    try:
        run_gh(
            "api", "--method", "PUT", f"repos/{REPOSITORY}/contents/{REMOTE_PATH}",
            "--input", str(payload_path), "--silent",
        )
    finally:
        payload_path.unlink(missing_ok=True)
    print(f"已备份数据库到私有仓库 {REPOSITORY}/{REMOTE_PATH}")


if __name__ == "__main__":
    main()

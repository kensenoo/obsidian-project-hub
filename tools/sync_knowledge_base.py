#!/usr/bin/env python3
"""将 Obsidian Markdown 笔记同步到本地 SQLite 全文检索知识库。"""

from __future__ import annotations

import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "03-知识库" / "knowledge.db"
EXCLUDED_PARTS = {".git", ".obsidian", "03-知识库", "tools"}


def metadata(text: str, path: Path) -> tuple[str, str]:
    title = path.stem
    tags = ""
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if match:
        header = match.group(1)
        title_match = re.search(r"^title:\s*(.+)$", header, re.MULTILINE)
        tags_match = re.search(r"^tags:\s*\n((?:\s*-\s*.+\n?)*)", header, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip().strip('"')
        if tags_match:
            tags = ", ".join(
                line.split("-", 1)[1].strip()
                for line in tags_match.group(1).splitlines()
                if "-" in line
            )
    heading = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return (heading.group(1).strip() if heading else title, tags)


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.executescript(
        """
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS documents (
          path TEXT PRIMARY KEY,
          title TEXT NOT NULL,
          folder TEXT NOT NULL,
          tags TEXT NOT NULL DEFAULT '',
          content TEXT NOT NULL,
          modified_at TEXT NOT NULL,
          indexed_at TEXT NOT NULL
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts
        USING fts5(title, tags, content, content='documents', content_rowid='rowid');
        """
    )
    discovered: set[str] = set()
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for path in ROOT.rglob("*.md"):
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        text = path.read_text(encoding="utf-8")
        title, tags = metadata(text, path)
        relative_text = relative.as_posix()
        discovered.add(relative_text)
        connection.execute(
            """
            INSERT INTO documents(path, title, folder, tags, content, modified_at, indexed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
              title=excluded.title, folder=excluded.folder, tags=excluded.tags,
              content=excluded.content, modified_at=excluded.modified_at,
              indexed_at=excluded.indexed_at
            """,
            (
                relative_text,
                title,
                relative.parent.as_posix(),
                tags,
                text,
                datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(timespec="seconds"),
                now,
            ),
        )
    placeholders = ",".join("?" for _ in discovered) or "''"
    connection.execute(f"DELETE FROM documents WHERE path NOT IN ({placeholders})", tuple(discovered))
    connection.execute("INSERT INTO documents_fts(documents_fts) VALUES ('rebuild')")
    connection.commit()
    count = connection.execute("SELECT count(*) FROM documents").fetchone()[0]
    connection.close()
    print(f"已同步 {count} 篇笔记到 {DB_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

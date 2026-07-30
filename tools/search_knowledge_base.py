#!/usr/bin/env python3
"""查询本 Obsidian 知识库的 SQLite 全文索引。"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "03-知识库" / "knowledge.db"


def main() -> None:
    query = " ".join(sys.argv[1:]).strip()
    if not query:
        raise SystemExit('用法：python3 tools/search_knowledge_base.py "关键词"')
    if not DB_PATH.exists():
        raise SystemExit("知识库尚未建立。请先运行 tools/sync_knowledge_base.py")
    connection = sqlite3.connect(DB_PATH)
    try:
        results = connection.execute(
            """
            SELECT d.path, d.title,
                   snippet(documents_fts, 2, '【', '】', '…', 18) AS excerpt
            FROM documents_fts
            JOIN documents d ON d.rowid = documents_fts.rowid
            WHERE documents_fts MATCH ?
            ORDER BY bm25(documents_fts)
            LIMIT 10
            """,
            (query,),
        ).fetchall()
    except sqlite3.OperationalError:
        results = connection.execute(
            """
            SELECT path, title, substr(content, 1, 240)
            FROM documents
            WHERE title LIKE ? OR tags LIKE ? OR content LIKE ?
            LIMIT 10
            """,
            tuple(f"%{query}%" for _ in range(3)),
        ).fetchall()
    if not results:
        print("未找到相关笔记。")
    for path, title, excerpt in results:
        print(f"\n# {title}\n路径：{path}\n{excerpt}")


if __name__ == "__main__":
    main()

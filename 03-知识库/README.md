# 本地知识库

`knowledge.db` 是由本库 Markdown 笔记生成的本地 SQLite 全文检索数据库，不会提交到公开仓库。

## 同步

在库根目录运行：

```bash
python3 tools/sync_knowledge_base.py
```

每次新增、编辑或删除笔记后运行一次。同步会提取笔记路径、标题、标签、正文与文件更新时间。

如需同时备份数据库到私有 GitHub 仓库，运行：

```bash
python3 tools/sync_knowledge_base.py --publish
```

该命令会先重建本地索引，再上传 `knowledge.db` 到 `kensenoo/-`；数据库不会上传到公开仓库。

## 检索

```bash
python3 tools/search_knowledge_base.py "Codex 视频"
```

返回最相关的笔记、摘要和路径。知识库内容仅来自本 Obsidian 库；原始 Markdown 仍是唯一编辑来源。

# 知识库约定

本库使用 `03-知识库/knowledge.db` 作为 Markdown 笔记的本地全文检索索引。

处理与此库相关的新任务前，先运行：

```bash
python3 tools/sync_knowledge_base.py
python3 tools/search_knowledge_base.py "任务中的关键主题"
```

若检索结果相关，优先以对应笔记为上下文；若无结果，再继续外部检索或新建内容。完成笔记变更后，重新同步索引。

需要备份时，使用 `python3 tools/sync_knowledge_base.py --publish`，它会将更新后的数据库同步到私有仓库 `kensenoo/-`。

# 中文 RAG Chat

这是一个面向中文场景的 RAG 问答项目，支持文档上传、知识库问答、多轮会话记忆、混合检索和文档管理。

当前项目的核心能力包括：

- 支持 `PDF` / `Markdown` 文档上传
- 文档自动切分、入库和索引重建
- 基于 LangGraph 的多轮对话工作流
- 支持本地模式和在线模式切换
- 混合检索：向量召回 + 关键词召回 + 轻量重排
- 返回调试上下文和检索分数，便于排查效果
- 支持已入库文件列表、删除文件、重复上传策略和重建索引
- 提供 FastAPI 后端和 Streamlit 前端

## 技术栈

- 后端：FastAPI、Pydantic、Uvicorn
- RAG：LangChain、LangGraph、Groq
- 检索与存储：Pinecone、SQLite、本地 JSON
- 前端：Streamlit
- 测试：pytest

## 项目结构

```text
api/           FastAPI 路由
app/           应用入口与配置
ingest/        文档加载、切分、入库和注册表
memory/        SQLite 会话记忆
rag/           检索、重排、生成和图工作流
tests/         测试用例
ui/            Streamlit 前端
vectorstore/   本地存储与 Pinecone 封装
uploads/       上传文件目录
db/            本地运行数据目录
```

## 快速启动

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 准备环境变量

项目已经提供了 [`.env.example`](./.env.example)，你可以按需填写：

```bash
APP_NAME=中文 RAG Chat
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_API_BASE=http://127.0.0.1:8000

USE_LOCAL_RAG=true
DEFAULT_DUPLICATE_STRATEGY=replace

GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=rag-chat
```

说明：

- `USE_LOCAL_RAG=true` 表示优先使用本地模式，方便开发和调试。
- `USE_LOCAL_RAG=false` 表示启用在线模式，需要正确配置 `GROQ_API_KEY` 和 `PINECONE_API_KEY`。
- `DEFAULT_DUPLICATE_STRATEGY` 支持 `replace`、`skip`、`reject`。

3. 启动后端

```bash
python -m app.main
```

4. 启动前端

```bash
streamlit run ui/stramlit_app.py
```

## 使用说明

1. 在前端侧边栏上传 `PDF` 或 `Markdown` 文件。
2. 选择重复文件策略：
   `replace` 表示替换旧文件；
   `skip` 表示跳过；
   `reject` 表示直接返回冲突。
3. 上传成功后，可以在“知识库文件”区域查看已入库文件。
4. 在聊天框中输入问题，系统会返回答案、调试上下文和检索分数。
5. 如果需要重新构建知识库，可以点击“重建索引”。

## 主要接口

### `GET /health`

用于检查服务是否正常运行，并返回当前模式。

示例返回：

```json
{
  "status": "ok",
  "mode": "local"
}
```

### `POST /upload`

上传并入库文档。

表单参数：

- `file`：上传文件
- `duplicate_strategy`：重复文件策略，支持 `replace` / `skip` / `reject`

### `GET /documents`

返回当前已入库文件列表。

### `DELETE /documents/{filename}`

删除指定文件及其索引内容。

### `POST /documents/rebuild`

扫描 `uploads/` 目录并重新构建索引。

### `POST /chat`

提交用户问题并返回回答、检索 query、调试上下文和检索分数。

请求示例：

```json
{
  "query": "这份文档主要讲了什么？",
  "session_id": "demo-001"
}
```

返回示例：

```json
{
  "answer": "根据上下文，这份文档主要介绍了……",
  "session_id": "demo-001",
  "debug_context": "【片段1 | 来源: list.pdf | 段号: 1 | 综合分数: 0.92】...",
  "retrieval_query": "历史相关对话：...",
  "retrieval_scores": [
    {
      "source_file": "list.pdf",
      "chunk_index": 1,
      "page": null,
      "dense_score": 1.0,
      "keyword_score": 6.0,
      "retrieval_score": 0.92
    }
  ]
}
```

## 当前检索流程

当前项目使用的是一条比较完整的中文 RAG 检索链路：

1. 根据最近几轮对话改写检索 query
2. 在线模式下执行向量召回
3. 同时执行本地关键词召回
4. 合并候选结果并计算综合分数
5. 轻量重排后把最相关片段送给模型生成

## 测试
测试包括：

- 健康检查接口测试
- 上传、列表、聊天、删除整条链路测试
- 重复上传策略测试
- 重建索引测试
- query 改写测试
- 混合检索重排测试
- prompt 注入历史消息和上下文测试
- 本地存储持久化测试
- 会话记忆隔离测试
- 配置校验测试

运行测试：

```bash
pytest
```


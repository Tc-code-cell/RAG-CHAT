# 中文 RAG-Chat

这是一个面向中文场景的 RAG Chat 项目，包含以下核心能力：

- 文档上传与切分
- 向量检索
- LangGraph 多轮对话
- SQLite 持久化记忆
- FastAPI 后端
- Streamlit 前端

## 快速开始

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 配置 `.env`：

```bash
GROQ_API_KEY=your_key
PINECONE_API_KEY=your_key
USE_LOCAL_RAG=true
```

3. 启动后端：

```bash
python -m app.main
```

4. 启动前端：

```bash
streamlit run ui/stramlit_app.py
```

## 使用说明

1. 先上传 PDF 或 Markdown 文件。
2. 再在聊天框里提问。
3. 如果开启 `USE_LOCAL_RAG=true`，会优先使用本地存储进行测试。
4. 如果关闭本地模式，则会走 Groq + Pinecone 的在线模式。

## 建议先测试的内容

1. `/health` 是否返回正常。
2. 上传文件后能否回答文档内容相关问题。
3. 同一个 `session_id` 是否可以连续对话。
4. 换一个新的 `session_id` 是否不会串会话。

## 说明

- 当前项目更偏向“可运行的中文 RAG 原型”。
- 如果切到在线模式，需要确保 `.env` 里的 API Key 正确，并且 Pinecone 索引已经配置好。

"""
文件名：ingest/ingest_pipeline.py
最后修改时间：2026-04-09
模块功能：负责文档加载、切分、写入本地存储或向量数据库的完整入库流程。
模块相关技术：文档加载、文本切分、Pinecone、JSON 持久化、Python 路径处理。
"""

from pathlib import Path

from ingest.pdf_loader import load_pdf
from ingest.md_loader import load_markdown
from ingest.web_loader import load_web
from ingest.splitter import split_documents

from app.config import settings
from vectorstore.pinecone_store import get_vectorstore
from vectorstore.local_store import save_chunks


def ingest_file(file_path):

    if file_path.endswith(".pdf"):
        docs = load_pdf(file_path)

    elif file_path.endswith(".md"):
        docs = load_markdown(file_path)

    else:
        raise ValueError("Unsupported file")

    chunks = split_documents(docs)

    source_name = Path(file_path).name
    for index, chunk in enumerate(chunks, start=1):
        chunk.metadata = dict(chunk.metadata or {})
        chunk.metadata.setdefault("source_file", source_name)
        chunk.metadata["chunk_index"] = index
        chunk.metadata["chunk_total"] = len(chunks)

    if settings.USE_LOCAL_RAG:
        save_chunks(chunks)
    else:
        vectorstore = get_vectorstore()
        vectorstore.add_documents(chunks)

    return len(chunks)

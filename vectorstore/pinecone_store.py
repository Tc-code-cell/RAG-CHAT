"""
文件名：vectorstore/pinecone_store.py
最后修改时间：2026-04-16
模块功能：初始化 Pinecone 索引并封装向量检索存储对象，同时提供删除能力。
模块相关技术：Pinecone、LangChain PineconeVectorStore、Embedding、缓存。
"""

from functools import lru_cache

from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from app.config import settings
from ingest.embedder import get_embedding


@lru_cache(maxsize=1)
def init_pinecone_index():
    client = Pinecone(api_key=settings.PINECONE_API_KEY)
    index_name = settings.PINECONE_INDEX_NAME

    if index_name not in client.list_indexes().names():
        client.create_index(
            name=index_name,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

    return client.Index(index_name)


@lru_cache(maxsize=1)
def get_vectorstore():
    return PineconeVectorStore(
        index=init_pinecone_index(),
        embedding=get_embedding(),
    )


def delete_documents(ids: list[str]) -> None:
    if not ids:
        return
    vectorstore = get_vectorstore()
    vectorstore.delete(ids=ids)

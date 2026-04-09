"""
文件名：rag/retriever_node.py
最后修改时间：2026-04-09
模块功能：执行检索节点逻辑，完成查询改写、向量召回、重排和上下文组织。
模块相关技术：LangGraph 节点、Pinecone、向量召回、rerank、上下文拼接。
"""

from app.config import settings
from rag.retrieval import (
    build_retrieval_query,
    build_retriever,
    format_documents,
    rerank_documents,
)
from vectorstore.local_store import retrieve_chunks
from vectorstore.pinecone_store import get_vectorstore


def retrieve_node(state):
    messages = state["messages"]
    last_message = messages[-1]
    query = last_message.content
    retrieval_query = build_retrieval_query(query, messages)

    if settings.USE_LOCAL_RAG:
        docs = retrieve_chunks(retrieval_query, k=12)
    else:
        vectorstore = get_vectorstore()
        try:
            retriever = build_retriever(vectorstore)
            docs = retriever.invoke(retrieval_query)
        except Exception:
            docs = vectorstore.similarity_search(retrieval_query, k=12)

    ranked_docs = rerank_documents(retrieval_query, docs, top_k=6)
    context = format_documents(ranked_docs)

    return {
        "retrieval_query": retrieval_query,
        "retrieved_documents": ranked_docs,
        "context": context,
    }

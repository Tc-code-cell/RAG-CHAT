"""
文件名：rag/retrieval.py
最后修改时间：2026-04-09
模块功能：提供检索 query 改写、候选文档重排和上下文格式化能力。
模块相关技术：文本特征匹配、轻量 rerank、LangChain 文档对象。
"""

from __future__ import annotations

import re
from collections.abc import Sequence

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage


def build_retriever(vectorstore, *, search_type: str = "mmr", k: int = 8, fetch_k: int = 24):
    return vectorstore.as_retriever(
        search_type=search_type,
        search_kwargs={"k": k, "fetch_k": fetch_k},
    )


def build_retrieval_query(
    question: str,
    messages: Sequence[BaseMessage] | None = None,
    max_history_turns: int = 2,
) -> str:
    question = (question or "").strip()
    if not messages:
        return question

    recent_messages = [
        message
        for message in messages[:-1]
        if getattr(message, "content", "")
    ][-max_history_turns * 2 :]

    if not recent_messages:
        return question

    history_lines = []
    for message in recent_messages:
        role = "用户" if message.type in {"human", "user"} else "助手"
        history_lines.append(f"- {role}：{str(message.content).strip()}")

    history_block = "\n".join(history_lines)
    return f"历史相关对话：\n{history_block}\n\n当前问题：{question}"


def _extract_terms(text: str) -> set[str]:
    normalized = (text or "").lower()
    terms: set[str] = set()

    for token in re.findall(r"[a-z0-9_]+|[\u4e00-\u9fff]+", normalized):
        if not token:
            continue

        terms.add(token)
        if re.fullmatch(r"[\u4e00-\u9fff]+", token):
            if len(token) >= 2:
                terms.update(token[i : i + 2] for i in range(len(token) - 1))

    return terms


def score_document(question: str, doc: Document) -> float:
    question_terms = _extract_terms(question)
    content = doc.page_content or ""
    content_terms = _extract_terms(content)
    metadata = dict(doc.metadata or {})

    overlap = len(question_terms & content_terms)
    score = float(overlap)

    if question and question in content:
        score += 8.0

    if question_terms and any(term in content.lower() for term in question_terms if len(term) > 2):
        score += 1.5

    source_file = str(metadata.get("source_file") or metadata.get("source") or "")
    if source_file:
        source_terms = _extract_terms(source_file)
        score += 0.5 * len(question_terms & source_terms)

    chunk_index = metadata.get("chunk_index")
    if isinstance(chunk_index, int) and chunk_index == 1:
        score += 0.2

    return score


def rerank_documents(question: str, docs: Sequence[Document], top_k: int = 6) -> list[Document]:
    if not docs:
        return []

    ranked = sorted(
        enumerate(docs),
        key=lambda item: (-score_document(question, item[1]), item[0]),
    )

    return [doc for _, doc in ranked[:top_k]]


def format_documents(docs: Sequence[Document]) -> str:
    if not docs:
        return ""

    sections = []
    for index, doc in enumerate(docs, start=1):
        metadata = dict(doc.metadata or {})
        source_file = metadata.get("source_file") or metadata.get("source") or "未知来源"
        chunk_index = metadata.get("chunk_index")
        page = metadata.get("page")

        header_parts = [f"片段{index}", f"来源: {source_file}"]
        if page is not None:
            header_parts.append(f"页码: {page}")
        if chunk_index is not None:
            header_parts.append(f"段号: {chunk_index}")

        header = "【" + " | ".join(header_parts) + "】"
        content = (doc.page_content or "").strip()
        sections.append(f"{header}\n{content}")

    return "\n\n".join(sections)

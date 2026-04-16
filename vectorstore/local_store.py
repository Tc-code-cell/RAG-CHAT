"""
文件名：vectorstore/local_store.py
最后修改时间：2026-04-16
模块功能：为本地调试与混合检索提供本地分块镜像、关键词召回和文档删除能力。
模块相关技术：JSON 持久化、正则匹配、LangChain Document、关键词检索。
"""

from __future__ import annotations

import json
import re

from langchain_core.documents import Document

from app.config import settings


STORE_PATH = settings.LOCAL_CHUNKS_PATH


def _extract_terms(text: str) -> set[str]:
    normalized = (text or "").lower()
    terms: set[str] = set()

    for token in re.findall(r"[a-z0-9_]+|[\u4e00-\u9fff]+", normalized):
        if not token:
            continue

        terms.add(token)
        if re.fullmatch(r"[\u4e00-\u9fff]+", token) and len(token) >= 2:
            terms.update(token[index : index + 2] for index in range(len(token) - 1))

    return terms


def _load_raw_chunks() -> list[dict]:
    if not STORE_PATH.exists():
        return []

    try:
        return json.loads(STORE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def _save_raw_chunks(chunks: list[dict]) -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STORE_PATH.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _to_document(payload: dict, score: float | None = None) -> Document:
    metadata = dict(payload.get("metadata", {}))
    if score is not None:
        metadata["_keyword_score"] = score
    return Document(
        page_content=payload.get("page_content", ""),
        metadata=metadata,
    )


def load_documents() -> list[Document]:
    return [_to_document(item) for item in _load_raw_chunks() if item.get("page_content")]


def save_chunks(documents: list[Document], replace_source: str | None = None) -> None:
    existing_chunks = _load_raw_chunks()
    if replace_source:
        existing_chunks = [
            item
            for item in existing_chunks
            if dict(item.get("metadata", {})).get("source_file") != replace_source
        ]

    payload = existing_chunks + [
        {
            "page_content": document.page_content,
            "metadata": dict(document.metadata or {}),
        }
        for document in documents
    ]
    _save_raw_chunks(payload)


def delete_chunks_by_source(source_file: str) -> int:
    existing_chunks = _load_raw_chunks()
    kept_chunks = []
    removed_count = 0

    for item in existing_chunks:
        metadata = dict(item.get("metadata", {}))
        if metadata.get("source_file") == source_file:
            removed_count += 1
            continue
        kept_chunks.append(item)

    _save_raw_chunks(kept_chunks)
    return removed_count


def clear_chunks() -> None:
    _save_raw_chunks([])


def retrieve_chunks(query: str, k: int = 4) -> list[Document]:
    chunks = _load_raw_chunks()
    if not chunks:
        return []

    query_terms = _extract_terms(query)
    scored_chunks: list[tuple[float, dict]] = []

    for chunk in chunks:
        text = chunk.get("page_content", "")
        content_terms = _extract_terms(text)
        score = float(len(query_terms & content_terms))
        if score <= 0:
            continue
        scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda item: item[0], reverse=True)

    return [
        _to_document(chunk, score=score)
        for score, chunk in scored_chunks[:k]
    ]

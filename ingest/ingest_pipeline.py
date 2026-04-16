"""
文件名：ingest/ingest_pipeline.py
最后修改时间：2026-04-16
模块功能：负责文档加载、切分、入库、删除和重建索引的完整流程。
模块相关技术：文档加载、文本切分、Pinecone、JSON 持久化、文件摘要、文档注册表。
"""

from __future__ import annotations

from datetime import datetime
import hashlib
from pathlib import Path

from app.config import settings
from ingest.document_registry import (
    clear_documents,
    get_document,
    list_documents,
    remove_document,
    upsert_document,
)
from ingest.md_loader import load_markdown
from ingest.pdf_loader import load_pdf
from ingest.splitter import split_documents
from vectorstore.local_store import clear_chunks, delete_chunks_by_source, save_chunks
from vectorstore.pinecone_store import delete_documents, get_vectorstore


def _compute_file_hash(file_path: Path) -> str:
    digest = hashlib.sha256()
    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _build_chunk_id(source_name: str, file_hash: str, chunk_index: int) -> str:
    raw_value = f"{source_name}:{file_hash}:{chunk_index}"
    return hashlib.sha1(raw_value.encode("utf-8")).hexdigest()


def _load_documents(file_path: Path):
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return load_pdf(str(file_path))
    if suffix == ".md":
        return load_markdown(str(file_path))
    raise ValueError("仅支持 PDF 和 Markdown 文件。")


def list_ingested_documents() -> list[dict]:
    return list_documents()


def ingest_file(file_path: str, duplicate_strategy: str | None = None) -> dict:
    target_path = Path(file_path)
    duplicate_strategy = duplicate_strategy or settings.DEFAULT_DUPLICATE_STRATEGY

    if duplicate_strategy not in settings.VALID_DUPLICATE_STRATEGIES:
        raise ValueError("duplicate_strategy 只能是 replace、skip 或 reject。")

    source_name = target_path.name
    file_hash = _compute_file_hash(target_path)
    existing = get_document(source_name)

    if existing and existing.get("file_hash") == file_hash:
        return {
            "status": "skipped",
            "filename": source_name,
            "chunks": existing.get("chunks", 0),
            "message": "检测到同名且内容一致的文件，已跳过重复入库。",
        }

    if existing and duplicate_strategy == "skip":
        return {
            "status": "skipped",
            "filename": source_name,
            "chunks": existing.get("chunks", 0),
            "message": "检测到同名文件，按 skip 策略跳过。",
        }

    if existing and duplicate_strategy == "reject":
        raise FileExistsError(f"文件 {source_name} 已存在，请改用 replace 或 skip。")

    if existing:
        delete_document(source_name, remove_file=False)

    documents = _load_documents(target_path)
    chunks = split_documents(documents)

    chunk_ids: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        chunk_id = _build_chunk_id(source_name, file_hash, index)
        chunk.metadata = dict(chunk.metadata or {})
        chunk.metadata.update(
            {
                "source_file": source_name,
                "source_hash": file_hash,
                "chunk_index": index,
                "chunk_total": len(chunks),
                "chunk_id": chunk_id,
            }
        )
        chunk_ids.append(chunk_id)

    # 无论本地模式还是在线模式，都保留一份本地镜像，方便混合检索和文档管理。
    save_chunks(chunks, replace_source=source_name)

    if not settings.USE_LOCAL_RAG:
        vectorstore = get_vectorstore()
        vectorstore.add_documents(chunks, ids=chunk_ids)

    upsert_document(
        {
            "filename": source_name,
            "file_path": str(target_path),
            "file_hash": file_hash,
            "chunks": len(chunks),
            "chunk_ids": chunk_ids,
            "updated_at": datetime.now().isoformat(timespec="seconds"),
            "storage_mode": settings.runtime_mode(),
        }
    )

    return {
        "status": "success",
        "filename": source_name,
        "chunks": len(chunks),
        "message": "文件已成功入库。",
    }


def delete_document(filename: str, remove_file: bool = True) -> dict:
    normalized_name = Path(filename).name
    existing = get_document(normalized_name)
    if not existing:
        return {
            "status": "not_found",
            "filename": normalized_name,
            "chunks_deleted": 0,
        }

    deleted_chunks = delete_chunks_by_source(normalized_name)

    if not settings.USE_LOCAL_RAG:
        delete_documents(existing.get("chunk_ids", []))

    remove_document(normalized_name)

    file_path = Path(existing.get("file_path", settings.UPLOAD_DIR / normalized_name))
    if remove_file and file_path.exists():
        file_path.unlink()

    return {
        "status": "success",
        "filename": normalized_name,
        "chunks_deleted": deleted_chunks,
    }


def rebuild_index() -> dict:
    existing_documents = list_documents()

    if not settings.USE_LOCAL_RAG:
        for document in existing_documents:
            delete_documents(document.get("chunk_ids", []))

    clear_chunks()
    clear_documents()

    ingested_files = []
    total_chunks = 0

    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    for file_path in sorted(settings.UPLOAD_DIR.iterdir()):
        if not file_path.is_file() or file_path.suffix.lower() not in settings.ALLOWED_EXTENSIONS:
            continue

        result = ingest_file(str(file_path), duplicate_strategy="replace")
        if result.get("status") == "success":
            ingested_files.append(result["filename"])
            total_chunks += result["chunks"]

    return {
        "status": "success",
        "documents": len(ingested_files),
        "chunks": total_chunks,
        "filenames": ingested_files,
    }

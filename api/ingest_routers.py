"""
文件名：api/ingest_routers.py
最后修改时间：2026-04-16
模块功能：提供文档上传、列表、删除和重建索引接口。
模块相关技术：FastAPI、文件上传、表单参数、文档管理接口。
"""

import shutil
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.config import settings
from ingest.ingest_pipeline import (
    delete_document,
    ingest_file,
    list_ingested_documents,
    rebuild_index,
)


router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    duplicate_strategy: str = Form(settings.DEFAULT_DUPLICATE_STRATEGY),
):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="仅支持 PDF 和 Markdown 文件。")

    if duplicate_strategy not in settings.VALID_DUPLICATE_STRATEGIES:
        raise HTTPException(
            status_code=400,
            detail="duplicate_strategy 只能是 replace、skip 或 reject。",
        )

    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    target_path = settings.UPLOAD_DIR / Path(file.filename or "").name

    with target_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        return ingest_file(str(target_path), duplicate_strategy=duplicate_strategy)
    except FileExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/documents")
def list_documents():
    documents = list_ingested_documents()
    return {
        "count": len(documents),
        "documents": documents,
    }


@router.delete("/documents/{filename}")
def delete_document_endpoint(filename: str):
    result = delete_document(filename)
    if result["status"] == "not_found":
        raise HTTPException(status_code=404, detail="未找到对应文档。")
    return result


@router.post("/documents/rebuild")
def rebuild_documents():
    return rebuild_index()

"""
文件名：app/main.py
最后修改时间：2026-04-16
模块功能：项目启动入口，创建 FastAPI 应用并挂载聊天、上传和文档管理接口。
模块相关技术：FastAPI、Uvicorn、应用启动事件、健康检查接口。
"""

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI

from api.chat_routers import router as chat_router
from api.ingest_routers import router as ingest_router
from app.config import settings


app = FastAPI(title=settings.APP_NAME, version="0.2.0")

app.include_router(chat_router)
app.include_router(ingest_router)


@app.on_event("startup")
def startup_event():
    settings.validate_runtime()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "mode": settings.runtime_mode(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)

"""
文件名：app/config.py
最后修改时间：2026-04-09
模块功能：集中管理环境变量与项目运行配置，统一控制模型、向量库和本地模式开关。
模块相关技术：python-dotenv、环境变量管理、Python 配置类。
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = "rag-chat"

    SQLITE_DB = "sqlite:///db/chat.db"

    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    LLM_MODEL = "llama-3.3-70b-versatile"

    USE_LOCAL_RAG = os.getenv("USE_LOCAL_RAG", os.getenv("DEV_MODE", "false")).lower() == "true"

    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50

settings = Settings()

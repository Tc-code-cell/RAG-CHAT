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

from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings
from app.config import settings


@lru_cache(maxsize=1)
def get_embedding():
    return HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL
    )

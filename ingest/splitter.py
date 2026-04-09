"""
文件名：ingest/splitter.py
最后修改时间：2026-04-09
模块功能：将原始文档切分成适合检索与生成的文本片段。
模块相关技术：LangChain 文本切分器、递归切分、重叠窗口。
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings


def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", ", ", " ", ""]
    )

    return splitter.split_documents(docs)

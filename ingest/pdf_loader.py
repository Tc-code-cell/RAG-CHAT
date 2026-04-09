"""
文件名：ingest/pdf_loader.py
最后修改时间：2026-04-09
模块功能：加载 PDF 文档并转换为 LangChain 文档对象。
模块相关技术：LangChain Community、PyPDFLoader、PDF 解析。
"""

from langchain_community.document_loaders import PyPDFLoader

def load_pdf(file_path):

    loader = PyPDFLoader(file_path)

    return loader.load()

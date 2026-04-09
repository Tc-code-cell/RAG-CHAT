"""
文件名：ingest/md_loader.py
最后修改时间：2026-04-09
模块功能：加载 Markdown 文档并转换为可切分的文本内容。
模块相关技术：LangChain Community、TextLoader、文本文件读取。
"""

from langchain_community.document_loaders import TextLoader

def load_markdown(file_path):

    loader = TextLoader(file_path)

    return loader.load()

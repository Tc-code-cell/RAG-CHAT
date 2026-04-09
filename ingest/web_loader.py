"""
文件名：ingest/web_loader.py
最后修改时间：2026-04-09
模块功能：加载网页内容，作为可扩展的数据来源入口。
模块相关技术：LangChain Community、WebBaseLoader、网页抓取。
"""

from langchain_community.document_loaders import WebBaseLoader

def load_web(url):

    loader = WebBaseLoader(url)

    return loader.load()

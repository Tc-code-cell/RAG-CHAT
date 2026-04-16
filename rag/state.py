"""
文件名：rag/state.py
最后修改时间：2026-04-16
模块功能：定义 RAG 工作流中的状态结构，承载消息历史、检索上下文和调试信息。
模块相关技术：TypedDict、LangGraph 状态、LangChain 消息类型。
"""

from typing import Annotated, Any, List, TypedDict

from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage


class GraphState(TypedDict, total=False):
    messages: Annotated[List[BaseMessage], add_messages]
    context: str
    retrieval_query: str
    retrieval_scores: List[dict[str, Any]]

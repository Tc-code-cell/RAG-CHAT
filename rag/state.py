"""
文件名：rag/state.py
最后修改时间：2026-04-09
模块功能：定义 RAG 工作流中的状态结构，承载消息历史与检索上下文。
模块相关技术：TypedDict、LangGraph 状态、LangChain 消息类型。
"""

from typing import Annotated, List, TypedDict

from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage


class GraphState(TypedDict, total=False):

    messages: Annotated[List[BaseMessage], add_messages]
    context: str

"""
文件名：api/chat_routers.py
最后修改时间：2026-04-16
模块功能：提供聊天接口，接收用户问题与会话 ID，并返回答案和检索调试信息。
模块相关技术：FastAPI、Pydantic、LangGraph、LangChain 消息类型。
"""

from functools import lru_cache

from fastapi import APIRouter
from pydantic import BaseModel, Field


router = APIRouter()


class ChatRequest(BaseModel):
    query: str = Field(min_length=1)
    session_id: str = "default"


@lru_cache(maxsize=1)
def get_graph():
    from rag.graph import build_graph

    return build_graph()


@router.post("/chat")
def chat(payload: ChatRequest):
    from langchain_core.messages import HumanMessage

    response = get_graph().invoke(
        {
            "messages": [
                HumanMessage(content=payload.query)
            ]
        },
        config={"configurable": {"thread_id": payload.session_id}},
    )

    return {
        "answer": response["messages"][-1].content,
        "session_id": payload.session_id,
        "debug_context": response.get("context", ""),
        "retrieval_query": response.get("retrieval_query", ""),
        "retrieval_scores": response.get("retrieval_scores", []),
    }

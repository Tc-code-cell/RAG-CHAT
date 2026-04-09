"""
文件名：rag/graph.py
最后修改时间：2026-04-09
模块功能：定义 RAG 工作流图，串联检索节点与生成节点。
模块相关技术：LangGraph、状态图、检查点持久化。
"""

from langgraph.graph import StateGraph

from rag.state import GraphState
from rag.retriever_node import retrieve_node
from rag.generation_node import generation_node

from memory.sqlite_checkpoint import build_checkpointer


def build_graph():

    builder = StateGraph(GraphState)

    builder.add_node(
        "retrieve",
        retrieve_node
    )

    builder.add_node(
        "generate",
        generation_node
    )

    builder.set_entry_point("retrieve")

    builder.add_edge(
        "retrieve",
        "generate"
    )

    checkpointer = build_checkpointer()

    graph = builder.compile(
        checkpointer=checkpointer
    )

    return graph

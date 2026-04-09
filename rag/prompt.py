"""
文件名：rag/prompt.py
最后修改时间：2026-04-09
模块功能：定义生成阶段的中文提示词模板，约束模型只依据上下文回答。
模块相关技术：LangChain PromptTemplate、Prompt Engineering。
"""

from langchain_core.prompts import ChatPromptTemplate


def get_prompt():
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是一个中文 RAG 问答助手。"
                "你必须始终使用简体中文回答，不要输出英文。"
                "你只能依据给定的上下文回答问题，不能编造，不能猜测。"
                "如果上下文里没有足够信息，就明确回答“上下文中没有找到相关信息”。"
                "如果上下文中包含来源信息，尽量在回答中简短提到来源。"
                "回答要求简洁、准确、自然。"
            ),
            (
                "human",
                "对话历史：\n{history}\n\n检索到的上下文：\n{context}\n\n问题：\n{question}"
            ),
        ]
    )

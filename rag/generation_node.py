from functools import lru_cache

from langchain_core.messages import AIMessage
from langchain_groq import ChatGroq

from app.config import settings


@lru_cache(maxsize=1)
def get_llm():
    return ChatGroq(
        model=settings.LLM_MODEL,
        api_key=settings.GROQ_API_KEY
    )


def generation_node(state):

    messages = state["messages"]

    context = state["context"]

    question = messages[-1].content

    if settings.USE_LOCAL_RAG:
        if context.strip():
            answer = (
                "Based on the uploaded context, here is a concise answer:\n\n"
                f"{context}"
            )
        else:
            answer = "I could not find relevant information in the uploaded documents."
        return {
            "messages": [
                AIMessage(content=answer)
            ]
        }

    llm = get_llm()

    prompt = f"""
Use context to answer:

{context}

Question:
{question}
"""

    response = llm.invoke(prompt)

    return {
        "messages": [
            AIMessage(content=response.content)
        ]
    }

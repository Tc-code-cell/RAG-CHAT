from app.config import settings
from vectorstore.pinecone_store import get_vectorstore
from vectorstore.local_store import retrieve_chunks


def retrieve_node(state):

    messages = state["messages"]

    last_message = messages[-1]

    query = last_message.content

    if settings.USE_LOCAL_RAG:
        docs = retrieve_chunks(query)
    else:
        vectorstore = get_vectorstore()
        retriever = vectorstore.as_retriever()
        docs = retriever.invoke(query)

    context = "\n\n".join(
        doc.page_content for doc in docs
    )

    return {
        "context": context
    }

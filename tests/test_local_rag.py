from pathlib import Path

from langchain_core.documents import Document

from vectorstore.local_store import save_chunks, retrieve_chunks


def test_local_store_round_trip():
    docs = [
        Document(page_content="RAG chat uses retrieval over uploaded documents."),
        Document(page_content="FastAPI exposes the /chat endpoint."),
    ]

    save_chunks(docs)
    results = retrieve_chunks("What does the /chat endpoint do?", k=2)

    assert results
    assert any("chat" in doc.page_content.lower() for doc in results)

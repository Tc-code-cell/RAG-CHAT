from langchain_core.documents import Document

from ingest.splitter import split_documents


def test_split_documents_returns_chunks():
    docs = [Document(page_content="hello world. this is a test.")]

    chunks = split_documents(docs)

    assert len(chunks) >= 1
    assert all(chunk.page_content for chunk in chunks)

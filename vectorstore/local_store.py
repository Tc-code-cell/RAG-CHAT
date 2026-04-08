import json
import re
from pathlib import Path

from langchain_core.documents import Document


STORE_PATH = Path("db/local_chunks.json")


def _load_raw_chunks():
    if not STORE_PATH.exists():
        return []

    try:
        return json.loads(STORE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def save_chunks(documents):
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = [
        {
            "page_content": doc.page_content,
            "metadata": doc.metadata,
        }
        for doc in documents
    ]
    STORE_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def retrieve_chunks(query, k=4):
    chunks = _load_raw_chunks()
    if not chunks:
        return []

    tokens = set(re.findall(r"\w+", query.lower()))
    scored = []

    for chunk in chunks:
        text = chunk.get("page_content", "")
        words = set(re.findall(r"\w+", text.lower()))
        score = len(tokens & words)
        scored.append((score, chunk))

    scored.sort(key=lambda item: item[0], reverse=True)

    docs = [
        Document(
            page_content=item[1].get("page_content", ""),
            metadata=item[1].get("metadata", {})
        )
        for item in scored[:k]
        if item[1].get("page_content")
    ]

    return docs

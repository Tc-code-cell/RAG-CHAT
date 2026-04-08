# Multi-Source RAG Assistant with Persistent Memory

This project is a lightweight RAG chat prototype with:

- document ingestion
- Pinecone-backed vector search
- LangGraph chat orchestration
- SQLite checkpointing for multi-turn memory
- FastAPI backend and Streamlit UI

## Quick Start

1. Create a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set environment variables in a `.env` file:

```bash
GROQ_API_KEY=your_key
PINECONE_API_KEY=your_key
```

4. Start the API:

```bash
python -m app.main
```

5. Start the UI in another terminal:

```bash
streamlit run ui/stramlit_app.py
```

## What To Test First

1. `GET /health` should return `{"status": "ok"}`.
2. `POST /chat` should accept JSON like `{"query": "Hello", "session_id": "demo"}`.
3. Upload or ingest a small PDF or Markdown file, then ask a question that should be answered from that content.
4. Ask the same session two related questions and confirm the second answer can use memory.

## Notes

- The current setup depends on external services: Groq for generation and Pinecone for retrieval.
- If you want fully local testing, we should swap in a local vector store and local model backend.

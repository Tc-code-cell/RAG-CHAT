import streamlit as st
import requests

st.title("Smart RAG Assistant")

session_id = st.session_state.setdefault("session_id", "streamlit")
query = st.text_input("Ask a question")

if query:

    response = requests.post(
        "http://localhost:8000/chat",
        json={"query": query, "session_id": session_id},
        timeout=60
    )

    if response.ok:
        st.write(response.json()["answer"])
    else:
        st.error(f"Request failed: {response.status_code}")

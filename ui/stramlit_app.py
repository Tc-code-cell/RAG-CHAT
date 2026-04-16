"""
文件名：ui/stramlit_app.py
最后修改时间：2026-04-16
模块功能：提供中文 RAG Chat 的可视化前端，支持上传、聊天、文档管理与调试信息展示。
模块相关技术：Streamlit、Requests、前端状态管理、聊天界面。
"""

import os
import uuid

import requests
import streamlit as st


API_BASE = os.getenv("FRONTEND_API_BASE", "http://127.0.0.1:8000")


def fetch_documents():
    try:
        response = requests.get(f"{API_BASE}/documents", timeout=30)
        response.raise_for_status()
        return response.json().get("documents", [])
    except requests.RequestException:
        return []


def render_document_manager():
    st.subheader("知识库文件")
    documents = fetch_documents()
    st.caption(f"当前已入库文件数：{len(documents)}")

    if st.button("重建索引", use_container_width=True):
        try:
            response = requests.post(f"{API_BASE}/documents/rebuild", timeout=120)
            response.raise_for_status()
            payload = response.json()
            st.success(f"重建完成：{payload.get('documents', 0)} 个文件，{payload.get('chunks', 0)} 个片段。")
        except requests.RequestException as exc:
            st.error(f"重建索引失败：{exc}")

    if not documents:
        st.caption("当前还没有已入库文件。")
        return

    for document in documents:
        filename = document.get("filename", "未知文件")
        chunks = document.get("chunks", 0)
        updated_at = document.get("updated_at", "未知时间")
        with st.expander(f"{filename} ({chunks} 个片段)", expanded=False):
            st.caption(f"最近更新时间：{updated_at}")
            if st.button(f"删除 {filename}", key=f"delete-{filename}", use_container_width=True):
                try:
                    response = requests.delete(f"{API_BASE}/documents/{filename}", timeout=60)
                    response.raise_for_status()
                    st.success(f"已删除 {filename}")
                    st.rerun()
                except requests.RequestException as exc:
                    st.error(f"删除失败：{exc}")


st.set_page_config(page_title="中文 RAG Chat", page_icon="📚", layout="wide")

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1120px;
        }
        .hero {
            padding: 1.4rem 1.6rem;
            border-radius: 1.2rem;
            background: linear-gradient(135deg, #1f2937 0%, #0f766e 55%, #134e4a 100%);
            color: #f8fafc;
            margin-bottom: 1rem;
        }
        .hero h1 {
            margin: 0;
            font-size: 2rem;
        }
        .hero p {
            margin: 0.5rem 0 0;
            color: #d1fae5;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

st.markdown(
    """
    <div class="hero">
        <h1>中文 RAG Chat</h1>
        <p>上传文档后提问，支持会话记忆、混合检索、检索分数展示和知识库文件管理。</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.subheader("会话设置")
    session_id = st.text_input("Session ID", value=st.session_state.session_id)
    st.session_state.session_id = session_id.strip() or st.session_state.session_id

    col_left, col_right = st.columns(2)
    with col_left:
        if st.button("重置会话", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())[:8]
            st.session_state.messages = []
            st.rerun()
    with col_right:
        if st.button("清空消息", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    st.divider()
    st.subheader("文档上传")
    duplicate_strategy = st.selectbox(
        "重复文件策略",
        options=["replace", "skip", "reject"],
        index=0,
        help="replace 表示替换旧文件，skip 表示跳过，reject 表示直接报错。",
    )
    uploaded_file = st.file_uploader("选择 PDF 或 Markdown 文件", type=["pdf", "md"])

    if st.button("上传并入库", use_container_width=True, disabled=uploaded_file is None):
        if uploaded_file is None:
            st.warning("请先选择一个文件。")
        else:
            try:
                response = requests.post(
                    f"{API_BASE}/upload",
                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type or "application/octet-stream",
                        )
                    },
                    data={"duplicate_strategy": duplicate_strategy},
                    timeout=180,
                )
                response.raise_for_status()
                payload = response.json()
                st.session_state.uploaded_files.append(payload.get("filename", uploaded_file.name))
                if payload.get("status") == "skipped":
                    st.info(payload.get("message", "文件已跳过。"))
                else:
                    st.success(
                        f"上传成功：{payload.get('filename')}，共生成 {payload.get('chunks', 0)} 个片段。"
                    )
            except requests.RequestException as exc:
                st.error(f"上传失败：{exc}")

    st.divider()
    render_document_manager()


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message.get("context"):
            with st.expander("查看调试上下文", expanded=False):
                st.text(message["context"])
        if message.get("retrieval_scores"):
            with st.expander("查看检索分数", expanded=False):
                st.json(message["retrieval_scores"])


query = st.chat_input("请输入你的问题")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)

    try:
        response = requests.post(
            f"{API_BASE}/chat",
            json={"query": query, "session_id": st.session_state.session_id},
            timeout=180,
        )
        response.raise_for_status()
        payload = response.json()

        answer = payload.get("answer", "没有返回答案。")
        debug_context = payload.get("debug_context", "")
        retrieval_scores = payload.get("retrieval_scores", [])

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "context": debug_context,
                "retrieval_scores": retrieval_scores,
            }
        )

        with st.chat_message("assistant"):
            st.write(answer)
            if debug_context:
                with st.expander("查看调试上下文", expanded=False):
                    st.text(debug_context)
            if retrieval_scores:
                with st.expander("查看检索分数", expanded=False):
                    st.json(retrieval_scores)
    except requests.RequestException as exc:
        error_message = f"请求失败：{exc}"
        st.session_state.messages.append(
            {"role": "assistant", "content": error_message, "context": "", "retrieval_scores": []}
        )
        with st.chat_message("assistant"):
            st.error(error_message)

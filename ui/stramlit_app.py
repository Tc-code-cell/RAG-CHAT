import uuid

import requests
import streamlit as st


API_BASE = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="中文 RAG Chat",
    page_icon="💬",
    layout="wide"
)

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1100px;
        }
        .hero {
            padding: 1.2rem 1.4rem;
            border-radius: 1.2rem;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 55%, #334155 100%);
            color: #f8fafc;
            margin-bottom: 1rem;
        }
        .hero h1 {
            margin: 0;
            font-size: 2rem;
        }
        .hero p {
            margin: 0.4rem 0 0;
            color: #cbd5e1;
        }
        .muted {
            color: #64748b;
            font-size: 0.95rem;
        }
    </style>
    """,
    unsafe_allow_html=True
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
        <p>上传文档后提问，支持会话记忆、检索上下文和调试查看。</p>
    </div>
    """,
    unsafe_allow_html=True
)


with st.sidebar:
    st.subheader("会话设置")
    session_id = st.text_input("Session ID", value=st.session_state.session_id)
    st.session_state.session_id = session_id.strip() or st.session_state.session_id

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("重置会话", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())[:8]
            st.session_state.messages = []
            st.rerun()
    with col_b:
        if st.button("清空消息", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    st.divider()
    st.subheader("文档上传")
    uploaded_file = st.file_uploader("选择 PDF 或 Markdown 文件", type=["pdf", "md"])

    if st.button("上传并索引", use_container_width=True, disabled=uploaded_file is None):
        if uploaded_file is None:
            st.warning("请先选择一个文件。")
        else:
            try:
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type or "application/octet-stream"
                    )
                }
                response = requests.post(
                    f"{API_BASE}/upload",
                    files=files,
                    timeout=120
                )
                response.raise_for_status()
                data = response.json()
                st.session_state.uploaded_files.append(data.get("filename", uploaded_file.name))
                st.success(f"上传成功，切分得到 {data.get('chunks', 0)} 个片段。")
            except requests.RequestException as exc:
                st.error(f"上传失败：{exc}")

    st.caption(f"当前会话：`{st.session_state.session_id}`")
    if st.session_state.uploaded_files:
        st.caption("已上传文件：")
        for name in st.session_state.uploaded_files[-5:]:
            st.write(f"- {name}")


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message.get("context"):
            with st.expander("查看调试上下文", expanded=False):
                st.text(message["context"])


query = st.chat_input("请输入你想问的问题")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)

    try:
        response = requests.post(
            f"{API_BASE}/chat",
            json={
                "query": query,
                "session_id": st.session_state.session_id
            },
            timeout=180
        )
        response.raise_for_status()
        data = response.json()
        answer = data.get("answer", "没有返回答案。")
        debug_context = data.get("调试上下文") or data.get("debug_context", "")

        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "context": debug_context}
        )

        with st.chat_message("assistant"):
            st.write(answer)
            if debug_context:
                with st.expander("查看调试上下文", expanded=False):
                    st.text(debug_context)
    except requests.RequestException as exc:
        st.session_state.messages.append(
            {"role": "assistant", "content": f"请求失败：{exc}", "context": ""}
        )
        with st.chat_message("assistant"):
            st.error(f"请求失败：{exc}")

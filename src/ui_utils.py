"""
StudyMate RAG - UI 辅助模块
Streamlit 页面中可复用的辅助函数和对话框。

提取自 app.py，职责：
- 聊天历史渲染
- 知识库统计
- 清空确认弹窗
"""

import shutil

import streamlit as st

from src.file_utils import clear_uploaded_files
from src.config import CHROMA_DIR


def display_chat_history() -> None:
    """遍历 session_state.messages 渲染聊天历史。"""
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def get_kb_stats() -> dict:
    """
    统计知识库中的文档总数、总字符数、总 chunk 数。

    Returns:
        {"total_files": int, "total_chars": int, "total_chunks": int}
    """
    docs = st.session_state.parsed_docs
    total_files = len(docs)
    total_chars = sum(d["char_count"] for d in docs.values())
    total_chunks = sum(d.get("chunk_count", 0) for d in docs.values())
    return {
        "total_files": total_files,
        "total_chars": total_chars,
        "total_chunks": total_chunks,
    }


@st.dialog("⚠️ 确认清空知识库")
def confirm_clear_dialog() -> None:
    """
    清空知识库前的二次确认弹窗。

    设计要点：
    - st.dialog 是 Streamlit 1.38+ 的原生弹窗装饰器
    - 确认后清空会话状态、删除上传文件、刷新页面
    """
    st.warning("此操作将**永久删除**知识库中的所有文档和聊天记录，不可恢复！")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ 确认清空", use_container_width=True):
            st.session_state.parsed_docs = {}
            st.session_state.messages = []
            clear_uploaded_files()
            # 同步清空 ChromaDB 向量数据
            if CHROMA_DIR.exists():
                shutil.rmtree(CHROMA_DIR)
                CHROMA_DIR.mkdir(parents=True, exist_ok=True)
            st.toast("🗑️ 知识库已清空（含 ChromaDB）")
            st.rerun()
    with col2:
        if st.button("❌ 取消", use_container_width=True):
            st.rerun()

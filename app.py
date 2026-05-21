"""
StudyMate RAG - Streamlit 前端主入口
个人学习知识库问答系统，支持文件上传与基于 RAG 的智能问答。
Day 1：项目初始化 + 前端页面骨架搭建。
"""

import streamlit as st

# ── 页面配置 ──────────────────────────────────────────────
st.set_page_config(
    page_title="StudyMate RAG",
    page_icon="📚",
    layout="wide",
)

# ── 会话状态初始化 ────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []  # 聊天历史：[{"role": "user" | "assistant", "content": str}]

if "uploaded_files_info" not in st.session_state:
    st.session_state.uploaded_files_info = []  # 已上传文件名列表（Day 2 起迁移至 file_utils）


# ── 辅助函数 ──────────────────────────────────────────────
def display_chat_history() -> None:
    """遍历 session_state.messages，渲染聊天历史。"""
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


# ═══════════════════════════════════════════════════════════
# 左侧 Sidebar — 知识库管理
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.title("📁 知识库管理")

    # 文件上传组件
    uploaded_files = st.file_uploader(
        "上传学习资料",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
        help="支持 PDF / TXT / Markdown 格式，单文件最大 50MB",
    )

    # 记录上传文件名（暂不处理文件内容，Day 2 实现）
    if uploaded_files:
        st.session_state.uploaded_files_info = [f.name for f in uploaded_files]
        st.success(f"已选择 {len(uploaded_files)} 个文件（文件处理功能 Day 2 实现）")

    st.divider()

    # 清空知识库（占位按钮）
    if st.button("🗑️ 清空知识库", use_container_width=True):
        st.toast("功能开发中，将在 Day 2 实现", icon="🚧")

    st.divider()

    # 知识库状态
    st.subheader("📊 知识库状态")
    file_count = len(st.session_state.uploaded_files_info)
    st.metric("已上传文件", f"{file_count}")

    if file_count > 0:
        st.caption("已上传文件列表：")
        for fname in st.session_state.uploaded_files_info:
            st.caption(f"  • {fname}")
    else:
        st.caption("暂无文件，请上传学习资料")


# ═══════════════════════════════════════════════════════════
# 顶部主区 — 标题与简介
# ═══════════════════════════════════════════════════════════
st.title("📚 StudyMate RAG")
st.markdown(
    "**个人学习知识库问答系统** — "
    "上传你的学习资料，向 AI 提问，精准回答并附带引用来源。"
)
st.caption("Day 1 · 前端骨架搭建完成 | 问答功能将在 Day 5 上线")
st.divider()


# ═══════════════════════════════════════════════════════════
# 主区 — 聊天界面
# ═══════════════════════════════════════════════════════════
# 渲染历史消息
display_chat_history()

# 接收用户输入
if prompt := st.chat_input("请输入你的问题（例如：这篇笔记的核心观点是什么？）"):
    # 用户消息入队 + 显示
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 助手占位回复（Day 5 接入 RAG 管道）
    placeholder_reply = (
        f"🚧 RAG 问答功能正在开发中（Day 5 实现），你的问题已收到：\n\n> {prompt}"
    )
    st.session_state.messages.append({"role": "assistant", "content": placeholder_reply})
    with st.chat_message("assistant"):
        st.markdown(placeholder_reply)

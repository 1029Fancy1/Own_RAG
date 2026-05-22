"""
StudyMate RAG - Streamlit 前端主入口
个人学习知识库问答系统，支持文件上传与基于 RAG 的智能问答。
Day 2：文档上传与解析。
"""

import streamlit as st
from datetime import datetime
from pathlib import Path

# 确保 src/ 可导入（streamlit run 时 cwd 即为项目根目录，此句起保险作用）
import sys
sys.path.insert(0, str(Path(__file__).parent))

from src.file_utils import save_uploaded_file, get_file_size_kb, clear_uploaded_files
from src.document_loader import load_document

# ── 页面配置 ──────────────────────────────────────────────
st.set_page_config(
    page_title="StudyMate RAG",
    page_icon="📚",
    layout="wide",
)

# ── 会话状态初始化 ────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
    """
    聊天历史，结构: [{"role": "user" | "assistant", "content": str}, ...]
    """

if "parsed_docs" not in st.session_state:
    st.session_state.parsed_docs: dict = {}
    """
    已解析文档注册表，结构:
    {
        "filename.pdf": {
            "path": "data/uploads/filename.pdf",
            "size_kb": 234.5,
            "text": "解析后的全部文本",
            "char_count": 12345,
            "uploaded_at": "2026-05-21 16:20:45"
        }
    }
    """


# ── 辅助函数 ──────────────────────────────────────────────

def display_chat_history() -> None:
    """遍历 session_state.messages 渲染聊天历史。"""
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


def get_kb_stats() -> dict:
    """
    统计知识库中的文档总数与总字符数。

    Returns:
        {"total_files": int, "total_chars": int}
    """
    # ✍️ TODO[手敲]: 遍历 parsed_docs 计算文件数和字符数
    # 💡 提示:
    #     docs = st.session_state.parsed_docs
    #     total_files = len(docs)
    #     total_chars = sum(d["char_count"] for d in docs.values())
    #     return {"total_files": total_files, "total_chars": total_chars}
    # 🎯 期望: 0 个文档时返回 {"total_files": 0, "total_chars": 0}
    pass


# ═══════════════════════════════════════════════════════════
# 左侧 Sidebar — 知识库管理
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.title("📁 知识库管理")

    # ── 文件上传组件 ──────────────────────────────────────
    uploaded_files = st.file_uploader(
        "上传学习资料",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
        help="支持 PDF / TXT / Markdown 格式",
    )

    # ── "解析并保存" 按钮 ─────────────────────────────────
    if st.button("📥 解析并保存", use_container_width=True):
        if not uploaded_files:
            st.warning("请先选择文件，再点击「解析并保存」")
        else:
            # ✍️ TODO[手敲]: 遍历已选文件 → 保存 → 解析 → 写入 session_state
            # 💡 提示:
            #     success_count = 0
            #     for file in uploaded_files:
            #         try:
            #             file_path, is_new = save_uploaded_file(file)
            #             text = load_document(file_path)
            #             st.session_state.parsed_docs[file.name] = {
            #                 "path": str(file_path),
            #                 "size_kb": get_file_size_kb(file_path),
            #                 "text": text,
            #                 "char_count": len(text),
            #                 "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            #             }
            #             success_count += 1
            #         except Exception as e:
            #             st.error(f"解析失败 [{file.name}]: {e}")
            #     if success_count > 0:
            #         st.toast(f"✅ 成功解析并保存 {success_count} 个文件")
            # 🎯 期望: 每个文件都出现在 parsed_docs 中，文件名重复时自动加时间戳
            pass

    st.divider()

    # ── 清空知识库 ────────────────────────────────────────
    if st.button("🗑️ 清空知识库", use_container_width=True):
        # ✍️ TODO[手敲]: 清空 parsed_docs + 删除上传文件 + toast 提示
        # 💡 提示:
        #     st.session_state.parsed_docs = {}
        #     st.session_state.messages = []
        #     clear_uploaded_files()
        #     st.toast("🗑️ 知识库已清空")
        # 🎯 期望: 侧边栏状态归零，主区文档预览消失，聊天历史清空
        pass

    st.divider()

    # ── 知识库状态 ────────────────────────────────────────
    st.subheader("📊 知识库状态")

    # ✍️ TODO[手敲]: 调用 get_kb_stats() 动态渲染统计信息和文件列表
    # 💡 提示:
    #     stats = get_kb_stats()
    #     st.metric("已解析文件", stats["total_files"])
    #     st.metric("总字符数", f"{stats['total_chars']:,}")
    #     if stats["total_files"] > 0:
    #         st.caption("已解析文件列表：")
    #         for fname in st.session_state.parsed_docs:
    #             st.caption(f"  • {fname}")
    #     else:
    #         st.caption("暂无已解析文档，请上传并点击「解析并保存」")
    # 🎯 期望: 无文档时显示引导文案；有文档时显示统计和文件名
    pass


# ═══════════════════════════════════════════════════════════
# 顶部主区 — 标题与简介
# ═══════════════════════════════════════════════════════════
st.title("📚 StudyMate RAG")
st.markdown(
    "**个人学习知识库问答系统** — "
    "上传你的学习资料，向 AI 提问，精准回答并附带引用来源。"
)
st.caption("Day 2 · 文档上传与解析完成 | RAG 问答 Day 5 上线")
st.divider()


# ═══════════════════════════════════════════════════════════
# 文档预览区（仅在有已解析文档时显示）
# ═══════════════════════════════════════════════════════════
if st.session_state.parsed_docs:
    with st.expander("📄 文档预览", expanded=False):
        doc_names = list(st.session_state.parsed_docs.keys())
        selected_doc = st.selectbox("选择已解析的文档", doc_names)

        if selected_doc:
            # ✍️ TODO[手敲]: 获取选中文档的元信息并展示
            # 💡 提示:
            #     doc = st.session_state.parsed_docs[selected_doc]
            #     col1, col2, col3 = st.columns(3)
            #     with col1: st.metric("文件大小", f"{doc['size_kb']} KB")
            #     with col2: st.metric("字符数", f"{doc['char_count']:,}")
            #     with col3: st.caption(f"上传时间: {doc['uploaded_at']}")
            #     st.text_area("内容预览（前 2000 字）", doc["text"][:2000], height=250)
            # 🎯 期望: 三列展示元数据；text_area 显示前 2000 字，可滚动
            pass


# ═══════════════════════════════════════════════════════════
# 主区 — 聊天界面
# ═══════════════════════════════════════════════════════════
display_chat_history()

if prompt := st.chat_input("请输入你的问题（例如：这篇笔记的核心观点是什么？）"):
    # 用户消息入队 + 显示
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # ── 助手占位回复 ──────────────────────────────────────
    # ✍️ TODO[手敲]: 根据知识库是否为空，选择不同的回复内容
    # 💡 提示:
    #     if st.session_state.parsed_docs:
    #         kb_stats = get_kb_stats()
    #         reply = (
    #             f"📚 当前知识库已加载 **{kb_stats['total_files']}** 个文件"
    #             f"（共 {kb_stats['total_chars']:,} 字符）。\n\n"
    #             f"RAG 问答功能将在 **Day 5** 上线，届时可基于你的资料回答。\n\n"
    #             f"收到你的问题：\n\n> {prompt}"
    #         )
    #     else:
    #         reply = (
    #             f"🚧 知识库还是空的哦！请先在左侧侧边栏上传文件并点击「解析并保存」。\n\n"
    #             f"你的问题已记录：\n\n> {prompt}"
    #         )
    # 🎯 期望: 有文档时显示已就绪提示 + 统计；无文档时引导用户先上传
    pass

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

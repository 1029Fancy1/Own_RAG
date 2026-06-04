"""
StudyMate RAG - Streamlit 前端主入口
个人学习知识库问答系统，支持文件上传与基于 RAG 的智能问答。
Day 5：Agentic RAG 问答链路 + Tool Calling。
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path

# 确保 src/ 可导入（streamlit run 时 cwd 即为项目根目录，此句起保险作用）
import sys
sys.path.insert(0, str(Path(__file__).parent))

from src.file_utils import save_uploaded_file, get_file_size_kb
from src.document_loader import load_document
from src.text_splitter import build_chunks
from src.ui_utils import display_chat_history, get_kb_stats, confirm_clear_dialog
from src.vector_store import get_collection, add_chunks_to_store, count_chunks
from src.embedding_service import get_embedding
from src.rag_pipeline import answer_question

# ── 页面配置 ──────────────────────────────────────────────
st.set_page_config(
    page_title="StudyMate RAG",
    page_icon="📚",
    layout="wide",
)

# ── 会话状态初始化 ────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
    # 聊天历史: [{"role": "user" | "assistant", "content": str}, ...]

if "parsed_docs" not in st.session_state:
    # 已解析文档注册表:
    #   {"filename.pdf": {"path": str, "size_kb": float, "text": str,
    #                      "char_count": int, "uploaded_at": str,
    #                      "chunks": list[dict], "chunk_count": int}}
    st.session_state.parsed_docs: dict = {}


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
            # 获取/创建 ChromaDB 集合（每次写入前确保集合存在）
            collection = get_collection()
            success_count = 0

            for file in uploaded_files:
                try:
                    file_path, _ = save_uploaded_file(file)
                    text = load_document(file_path)
                    chunks = build_chunks(text, file.name)
                    chunk_count = len(chunks)
                    
                    # 调用 add_chunks_to_store 将 chunks 写入 ChromaDB
                    add_chunks_to_store(collection, chunks, get_embedding)
                    # 写入后 data/chroma/ 目录出现持久化数据

                    st.session_state.parsed_docs[file.name] = {
                        "path": str(file_path),
                        "size_kb": get_file_size_kb(file_path),
                        "text": text,
                        "char_count": len(text),
                        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "chunks": chunks,
                        "chunk_count": chunk_count,
                    }

                    success_count += 1

                except Exception as e:
                    st.error(f"解析失败 [{file.name}]: {e}")

            if success_count > 0:
                st.toast(f"✅ 成功解析并保存 {success_count} 个文件")

    st.divider()

    # ── 清空知识库 ────────────────────────────────────────
    if st.button("🗑️ 清空知识库", use_container_width=True):
        confirm_clear_dialog()

    st.divider()

    # ── 知识库状态 ────────────────────────────────────────
    st.subheader("📊 知识库状态")
    stats = get_kb_stats()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("已解析文件", stats["total_files"])
    with col2:
        st.metric("总字符数", f"{stats['total_chars']:,}")
    with col3:
        st.metric("总 Chunk 数", stats["total_chunks"])


    # 显示 ChromaDB 中的 chunk 数和持久化目录信息
    # 
    st.subheader("📊 向量库状态")
    col = get_collection()
    st.metric("ChromaDB Chunk 数", count_chunks(col))
    st.caption(f"持久化路径: data/chroma/")
    #展示向量库中的实际 chunk 数；空库显示 0


    if stats["total_files"] > 0:
        st.caption("已解析文件列表：")
        for fname in st.session_state.parsed_docs:
            st.caption(f"  • {fname}")
    else:
        st.caption("暂无已解析文档，请上传并点击「解析并保存」")


# ═══════════════════════════════════════════════════════════
# 顶部主区 — 标题与简介
# ═══════════════════════════════════════════════════════════
st.title("📚 StudyMate RAG")
st.markdown(
    "**个人学习知识库问答系统** — "
    "上传你的学习资料，向 AI 提问，精准回答并附带引用来源。"
)
st.caption("Day 5 · Agentic RAG 问答 + Tool Calling | 5 个 Tool 自主决策")
st.divider()


# ═══════════════════════════════════════════════════════════
# 文档预览区（仅在有已解析文档时显示）
# ═══════════════════════════════════════════════════════════
if st.session_state.parsed_docs:
    with st.expander("📄 文档预览", expanded=False):
        doc_names = list(st.session_state.parsed_docs.keys())
        selected_doc = st.selectbox("选择已解析的文档", doc_names)

        if selected_doc:
            doc = st.session_state.parsed_docs[selected_doc]

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("文件大小", f"{doc['size_kb']} KB")
            with col2:
                st.metric("字符数", f"{doc['char_count']:,}")
            with col3:
                st.metric("Chunk 数", doc.get("chunk_count", 0))
            with col4:
                st.caption(f"上传时间: {doc['uploaded_at']}")

            st.text_area(
                "内容预览（前 2000 字）",
                doc["text"][:2000],
                height=250,
            )


# ═══════════════════════════════════════════════════════════
# 主区 — 聊天界面
# ═══════════════════════════════════════════════════════════
display_chat_history()

if prompt := st.chat_input("请输入你的问题（例如：这篇笔记的核心观点是什么？）"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # ── 助手回复：Agentic RAG 问答 ──
    if st.session_state.parsed_docs:
        with st.spinner("StudyMate 正在思考..."):
            result = answer_question(prompt)
        reply = result["answer"]

        # 展示参考来源（从 tool_call_log 提取 kb 检索结果）
        kb_results = None
        for tc in result.get("tool_calls", []):
            if tc["tool"] == "search_knowledge_base":
                try:
                    data = json.loads(tc["result"])
                    if data.get("results"):
                        kb_results = data["results"]
                except Exception:
                    pass

        if kb_results:
            with st.expander("📌 参考来源"):
                for src in kb_results:
                    st.markdown(
                        f"**{src['rank']}. {src['filename']}** "
                        f"(chunk: `{src['chunk_id']}`, 相似度: {src['similarity']})"
                    )
                    st.caption(src["text"][:200] + "...")

        # 展示决策链路
        if result["tool_calls"]:
            with st.expander("🔍 查看决策链路"):
                for i, tc in enumerate(result["tool_calls"], 1):
                    st.caption(f"🔧 Step {i}: {tc['tool']}")
                    st.json({"args": tc["args"], "result": tc["result"][:200]})
    else:
        reply = "🚧 知识库还是空的哦！请先在左侧侧边栏上传文件并点击「解析并保存」。"

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

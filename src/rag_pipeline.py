"""
StudyMate RAG - RAG Pipeline 模块
Agentic RAG：串联 Tool Calling、工具分发、多源检索和答案生成。

Day 5 实现。

架构：
    app.py 调用 answer_question(question)
        → chat_with_tools(question, execute_tool)
            → LLM 自主决策调用哪些工具
                → execute_tool 分发到具体 handler
                    → handler 调用 ChromaDB / arXiv / session_state
"""

import json
import urllib.request
import urllib.parse
import streamlit as st

from src.vector_store import get_collection, search_similar, list_documents
from src.embedding_service import get_embedding
from src.llm_service import chat_with_tools


# ── ChromaDB 集合懒加载 ──────────────────────────────────

_collection = None


def _get_collection():
    """懒加载 ChromaDB 集合（避免模块导入时就初始化）。"""
    global _collection
    if _collection is None:
        _collection = get_collection()
    return _collection


# ═══════════════════════════════════════════════════════════
# 工具分发器
# ═══════════════════════════════════════════════════════════

def execute_tool(tool_name: str, tool_args: dict) -> str:
    """
    将 LLM 的工具调用请求分发到对应的处理函数。

    设计要点：
    - 每个工具返回字符串（JSON 或纯文本），LLM 可以直接理解
    - 返回值包含足够的上下文信息（来源、数量、内容摘要）

    Args:
        tool_name: 工具名称（与 TOOLS schema 中的 function.name 对应）
        tool_args: LLM 传入的参数（已从 JSON 解析为 dict）

    Returns:
        工具执行结果字符串
    """
    if tool_name == "search_knowledge_base":
        return _search_kb(
            tool_args.get("query", ""),
            tool_args.get("top_k", 5),
        )
    elif tool_name == "list_documents":
        return _list_docs()
    elif tool_name == "get_document_overview":
        return _doc_overview(tool_args.get("filename", ""))
    elif tool_name == "search_arxiv":
        return _search_arxiv(
            tool_args.get("query", ""),
            tool_args.get("max_results", 3),
        )
    elif tool_name == "get_chunk_detail":
        return _get_chunk(tool_args.get("chunk_id", ""))
    else:
        return json.dumps({"error": f"未知工具: {tool_name}"}, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════
# Tool Handler #1: 知识库语义检索
# ═══════════════════════════════════════════════════════════

def _search_kb(query: str, top_k: int = 5) -> str:
    """
    在 ChromaDB 中语义检索，返回格式化的结果 JSON。

    返回格式:
        {
            "count": 3,
            "results": [
                {"rank": 1, "chunk_id": "笔记.pdf_3", "text": "...", "filename": "笔记.pdf", "similarity": 0.92},
                ...
            ]
        }
    """
    # ✍️ TODO[手敲]: 调用 search_similar → 格式化结果为 JSON 返回
    # 💡 提示:
    #     col = _get_collection()
    #     results = search_similar(col, query, get_embedding, top_k=top_k)
    #     items = []
    #     for i in range(len(results["documents"][0])):
    #         items.append({
    #             "rank": i + 1,
    #             "chunk_id": results["ids"][0][i],
    #             "text": results["documents"][0][i][:300],
    #             "filename": results["metadatas"][0][i].get("filename", ""),
    #             "similarity": round(1 - results["distances"][0][i], 4),
    #         })
    #     return json.dumps({"count": len(items), "results": items}, ensure_ascii=False)
    # 🎯 期望: LLM 收到结构化 JSON，可以从中提取 chunk_id 做进一步操作
    pass


# ═══════════════════════════════════════════════════════════
# Tool Handler #2: 列出知识库文档
# ═══════════════════════════════════════════════════════════

def _list_docs() -> str:
    """
    返回知识库中所有文档的文件名列表。

    返回格式:
        {"total_documents": 3, "documents": ["笔记.pdf", "讲义.md", "论文笔记.txt"]}
    """
    # 调用 list_documents → 格式化为 JSON
    col = _get_collection()
    docs = list_documents(col)
    return json.dumps({"total_documents": len(docs), "documents": docs}, ensure_ascii=False)
    #空库返回 {"total_documents": 0, "documents": []}


# ═══════════════════════════════════════════════════════════
# Tool Handler #3: 文档概览
# ═══════════════════════════════════════════════════════════

def _doc_overview(filename: str) -> str:
    """
    从 parsed_docs（Streamlit session_state）中获取文档元信息。

    返回格式:
        {
            "filename": "笔记.pdf",
            "size_kb": 234.5,
            "char_count": 12345,
            "chunk_count": 25,
            "uploaded_at": "2026-05-28 16:20",
            "text_preview": "前 300 字..."
        }
    """
    # ✍️ TODO[手敲]: 从 st.session_state.parsed_docs 获取文档信息 → 格式化为 JSON
    # 💡 提示:
    #     doc = st.session_state.parsed_docs.get(filename)
    #     if not doc:
    #         return json.dumps({"error": f"文档不存在: {filename}"}, ensure_ascii=False)
    #     return json.dumps({
    #         "filename": filename,
    #         "size_kb": doc["size_kb"],
    #         "char_count": doc["char_count"],
    #         "chunk_count": doc.get("chunk_count", 0),
    #         "uploaded_at": doc["uploaded_at"],
    #         "text_preview": doc["text"][:300],
    #     }, ensure_ascii=False)
    # 🎯 期望: LLM 拿到概览后判断该文档是否与用户问题相关，决定是否深入检索
    pass


# ═══════════════════════════════════════════════════════════
# Tool Handler #4: arXiv 论文检索
# ═══════════════════════════════════════════════════════════

def _search_arxiv(query: str, max_results: int = 3) -> str:
    """
    通过 arXiv API 检索论文，返回标题、作者、摘要和链接。

    设计要点：
    - 使用 arXiv 官方 API（免费、无需 Key）
    - 按相关度排序，返回 top-N

    返回格式:
        {
            "source": "arXiv",
            "count": 2,
            "papers": [
                {"title": "...", "authors": ["..."], "summary": "...", "url": "..."},
            ]
        }
    """
    # ✍️ TODO[手敲]: 调用 arXiv API → 解析 XML → 格式化为 JSON
    # 💡 提示:
    #     base_url = "http://export.arxiv.org/api/query"
    #     params = urllib.parse.urlencode({
    #         "search_query": f"all:{query}",
    #         "start": 0,
    #         "max_results": max_results,
    #         "sortBy": "relevance",
    #     })
    #     url = f"{base_url}?{params}"
    #     with urllib.request.urlopen(url, timeout=10) as resp:
    #         raw_xml = resp.read().decode("utf-8")
    #     # 简单 XML 解析（使用 xml.etree.ElementTree）
    #     import xml.etree.ElementTree as ET
    #     ns = {"atom": "http://www.w3.org/2005/Atom"}
    #     root = ET.fromstring(raw_xml)
    #     papers = []
    #     for entry in root.findall("atom:entry", ns):
    #         title = entry.find("atom:title", ns).text.strip().replace("\n", " ")
    #         authors = [a.find("atom:name", ns).text for a in entry.findall("atom:author", ns)]
    #         summary = entry.find("atom:summary", ns).text.strip().replace("\n", " ")[:300]
    #         url = entry.find("atom:id", ns).text.strip()
    #         papers.append({"title": title, "authors": authors, "summary": summary, "url": url})
    #     return json.dumps({"source": "arXiv", "count": len(papers), "papers": papers}, ensure_ascii=False)
    # 🎯 期望: 返回最多 max_results 篇论文；网络异常时返回 {"error": "arXiv 请求失败: ..."}
    pass


# ═══════════════════════════════════════════════════════════
# Tool Handler #5: Chunk 详情
# ═══════════════════════════════════════════════════════════

def _get_chunk(chunk_id: str) -> str:
    """
    通过 chunk_id 从 ChromaDB 中获取完整文本和元数据。

    返回格式:
        {
            "chunk_id": "笔记.pdf_3",
            "text": "完整文本...",
            "metadata": {"filename": "笔记.pdf", "chunk_id": 3}
        }
    """
    # ✍️ TODO[手敲]: 从 ChromaDB 按 id 获取 chunk
    # 💡 提示:
    #     col = _get_collection()
    #     result = col.get(ids=[chunk_id])
    #     if not result["documents"]:
    #         return json.dumps({"error": f"chunk 不存在: {chunk_id}"}, ensure_ascii=False)
    #     return json.dumps({
    #         "chunk_id": chunk_id,
    #         "text": result["documents"][0],
    #         "metadata": result["metadatas"][0],
    #     }, ensure_ascii=False)
    # 🎯 期望: LLM 调用此工具获取完整上下文后，能给出更精准的回答
    pass


# ═══════════════════════════════════════════════════════════
# 主入口：Agentic RAG 问答
# ═══════════════════════════════════════════════════════════

def answer_question(question: str) -> dict:
    """
    Agentic RAG 问答入口 — LLM 自主决定用哪些工具、调用多少次。

    Args:
        question: 用户问题文本

    Returns:
        {
            "answer": "LLM 最终回答",
            "tool_calls": [{"tool": "...", "args": {...}, "result": "..."}, ...],
            "total_turns": 2,
            "has_error": False,
            "error_msg": ""
        }
    """
    try:
        result = chat_with_tools(
            user_message=question,
            execute_tool_fn=execute_tool,
        )
        result["has_error"] = False
        result["error_msg"] = ""
        return result
    except Exception as e:
        return {
            "answer": f"处理请求时遇到错误: {str(e)}",
            "tool_calls": [],
            "total_turns": 0,
            "has_error": True,
            "error_msg": str(e),
        }

"""
StudyMate RAG - 向量存储模块
基于 ChromaDB 管理文档向量，支持写入、检索、列表、统计。

Day 4 实现。

核心概念 — ChromaDB：
    本地持久化向量数据库。每条记录由四个字段组成：
    id（唯一标识）、document（原文）、embedding（向量）、metadata（元数据）。
    写入语义是 upsert（id 存在则覆盖，不存在则新增）。
"""

from typing import Any

import chromadb
from chromadb import Collection

from src.config import CHROMA_DIR


def get_collection() -> Collection:
    """
    获取或创建 ChromaDB 持久化集合 'studymate'。

    核心 API：
        chromadb.PersistentClient(path=...)   → 以本地目录为存储的客户端
        client.get_or_create_collection(name=...) → 集合存在则返回，否则创建

    Returns:
        ChromaDB Collection 对象
    """
    # ✍️初始化 ChromaDB 持久化客户端并获取/创建集合
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(name="studymate")
    return collection


def add_chunks_to_store(
    collection: Collection,
    chunks: list[dict[str, Any]],
    embedding_fn,
) -> int:
    """
    将 chunk 列表批量生成向量并写入 ChromaDB。

    核心 API：
        collection.add(ids=..., documents=..., metadatas=..., embeddings=...)

    设计要点：
    - 逐条调用 embedding_fn(chunk["text"]) 生成向量
    - ChromaDB 对相同 id 执行 upsert，重新上传同一文件不会产生重复记录
    - metadata 只保留 filename 和 chunk_id，控制存储体积

    Args:
        collection: ChromaDB 集合
        chunks: Day 3 build_chunks 产出的列表，每项含 id / text / metadata
        embedding_fn: 嵌入函数（get_embedding）

    Returns:
        写入的 chunk 数量
    """
    # 从 chunks 拆出四列 → 调用 embedding_fn 生成向量 → 写入
    ids = [chunk["id"] for chunk in chunks]
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]
    embeddings = [embedding_fn(chunk["text"]) for chunk in chunks]
    collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)
    return len(chunks)


def search_similar(
    collection: Collection,
    query: str,
    embedding_fn,
    top_k: int = 5,
) -> dict[str, Any]:
    """
    将问题向量化后在 ChromaDB 中检索最相似的 chunk。

    核心 API：
        query_embedding = embedding_fn(query)
        collection.query(query_embeddings=[...], n_results=top_k)

    返回结构：
        {
            "ids": [["id1", "id2", ...]],         # 二层列表
            "documents": [["text1", "text2", ...]],
            "metadatas": [[{...}, {...}, ...]],
            "distances": [[0.23, 0.45, ...]],     # 余弦距离，越小越相似
        }

    Args:
        collection: ChromaDB 集合
        query: 用户问题文本
        embedding_fn: 嵌入函数
        top_k: 返回最相似的 top_k 条，默认 5

    Returns:
        ChromaDB 查询结果字典
    """
    # 将问题向量化 → 执行 ChromaDB 查询
    query_vec = embedding_fn(query)
    results = collection.query(query_embeddings=[query_vec], n_results=top_k)
    return results


# ── Tool Calling 辅助函数（Day 5 用）───────────────────

def list_documents(collection: Collection) -> list[str]:
    """
    列出 ChromaDB 中所有已入库的文档文件名（去重、排序）。

    设计用途：
    - Day 5 Tool Calling 中 list_documents 工具的底层函数
    - 从所有 chunk 的 metadata 中提取不重复的 filename

    Args:
        collection: ChromaDB 集合

    Returns:
        排序后的文件名列表，如 ["笔记.pdf", "讲义.md"]；空库返回 []
    """
    #  从 metadata 去重提取文件名
    all_metadatas = collection.get()["metadatas"]
    filenames = {m["filename"] for m in all_metadatas if m}
    return sorted(filenames)


def count_chunks(collection: Collection) -> int:
    """返回 ChromaDB 中当前存储的 chunk 总数。"""
    return collection.count()

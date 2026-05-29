"""
StudyMate RAG - 文本分割模块
将长文档切分为适合向量化的短文本块（chunk）。

Day 3 实现。

核心概念 — 滑动窗口切分：
    chunk_size = 800, overlap = 120, 步长 = 680

    Text:  |████████████████████████████████████████████|
    Chunk0: |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■|
    Chunk1:              |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■|
    Chunk2:                            |■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■|

    相邻 chunk 有 120 字符重叠，保证边界处的信息不会因切分而丢失。
"""

from typing import Any


def split_text(
    text: str,
    chunk_size: int = 800,
    overlap: int = 120,
) -> list[dict[str, Any]]:
    """
    使用滑动窗口将长文本切分为固定大小的 chunk。

    设计要点：
    - 每次窗口移动的步长 = chunk_size - overlap（即 680）
    - 仅当 chunk 非空时才加入结果列表·
    - 最后一个 chunk 可能不足 chunk_size，仍保留
    - chunk_id 从 0 开始自增

    Args:
        text: 待切分的完整文本
        chunk_size: 每个 chunk 的最大字符数，默认 800
        overlap: 相邻 chunk 的重叠字符数，默认 120

    Returns:
        [{"chunk_id": 0, "text": "前 800 字..."}, {"chunk_id": 1, "text": "重叠 120 字后的 800 字..."}, ...]
    """
    if overlap >= chunk_size:
        raise ValueError(f"overlap ({overlap}) 必须小于 chunk_size ({chunk_size})")


    chunks: list[dict[str, Any]] = []

    start = 0
    chunk_id = 0
    step = chunk_size - overlap
    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append({"chunk_id": chunk_id, "text": chunk_text})
            chunk_id += 1
        start += step  # 窗口后移
    return chunks


def build_chunks(
    text: str,
    filename: str,
    chunk_size: int = 800,
    overlap: int = 120,
) -> list[dict[str, Any]]:
    """
    切分文本并附加来源元数据，生成可直接入库的 chunk 列表。

    设计要点：
    - 调用 split_text() 完成切分逻辑
    - 为每个 chunk 生成唯一 id（格式: "文件名_chunkId"），防止 ChromaDB 写入时 id 冲突
    - metadata 保留 filename 和 chunk_id，Day 5 溯源引用时从这里取

    数据结构（每个元素）:
        {
            "id": "笔记.pdf_0",
            "text": "chunk 文本内容...",
            "metadata": {
                "filename": "笔记.pdf",
                "chunk_id": 0
            }
        }

    Args:
        text: 待切分的完整文本
        filename: 来源文件名，用于生成 chunk id 和 metadata
        chunk_size: 每个 chunk 的最大字符数
        overlap: 相邻 chunk 的重叠字符数

    Returns:
        带元数据的 chunk 列表，每个元素含 id / text / metadata 三个顶层字段
    """
    raw_chunks = split_text(text, chunk_size=chunk_size, overlap=overlap)
    result = []
    for item in raw_chunks:
        chunk = {
             "id": f"{filename}_{item['chunk_id']}",
             "text": item["text"],
             "metadata": {
                  "filename": filename, 
                  "chunk_id": item["chunk_id"],
         },
          }
        result.append(chunk)
    return result


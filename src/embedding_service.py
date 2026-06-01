"""
StudyMate RAG - 嵌入服务模块
使用本地 BGE 模型将文本转换为向量。

Day 4 实现。

技术选型：
    BAAI/bge-small-zh（BGE 小型中文版）
    - 512 维向量（OpenAI text-embedding-3-small 是 1536 维，BGE 更轻量）
    - 专为中文语义检索优化
    - 本地运行，不上传数据，零费用
    - 首次加载自动从 HuggingFace 下载模型（约 130MB），后续缓存

核心 API：
    model = SentenceTransformer("BAAI/bge-small-zh")
    embedding = model.encode(text)        → numpy.ndarray (512,)
    embeddings = model.encode(texts)      → numpy.ndarray (N, 512)
"""

from sentence_transformers import SentenceTransformer

from src.config import EMBEDDING_MODEL

# 全局模型单例（模块加载时初始化一次，后续复用）
# 首次加载会下载模型，耗时约 10-30 秒（视网速而定）
_model = SentenceTransformer(EMBEDDING_MODEL)


def get_embedding(text: str) -> list[float]:
    """
    将单条文本转换为 512 维向量。

    核心 API：
        _model.encode(text)  →  numpy.ndarray (512,)
        .tolist()            →  list[float]

    Args:
        text: 待向量化的文本

    Returns:
        512 维浮点数向量列表
    """
    embedding = _model.encode(text)
    return embedding.tolist()



def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    批量生成嵌入向量。

    设计要点：
    - BGE 模型对批量输入做了内部优化，一次 encode(N 条) 比循环 N 次快
    - encode() 返回 2D ndarray (N, 512)，.tolist() 转为 list[list[float]]

    Args:
        texts: 待向量化的文本列表

    Returns:
        向量列表，len(返回值) == len(texts)，每个元素 512 维
    """
    embeddings = _model.encode(texts)
    return embeddings.tolist()

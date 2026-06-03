"""
StudyMate RAG - 嵌入服务模块
使用本地 BGE 模型将文本转换为向量（通过 ModelScope 国内镜像下载）。

Day 4 实现。

技术选型：
    BAAI/bge-small-zh-v1.5（BGE 小型中文版）
    - 512 维向量
    - 专为中文语义检索优化
    - 通过 ModelScope（国内可访问）下载模型，首次约 91MB，后续缓存
"""

import os

from sentence_transformers import SentenceTransformer
from modelscope import snapshot_download

from src.config import EMBEDDING_MODEL

_model = None


def _get_model() -> SentenceTransformer:
    """懒加载 BGE 模型：优先从 ModelScope 下载，失败则回退到 HuggingFace。"""
    global _model
    if _model is None:
        try:
            model_dir = snapshot_download(
                "BAAI/bge-small-zh-v1.5",
                cache_dir=os.path.expanduser("~/.cache/modelscope"),
            )
            _model = SentenceTransformer(model_dir)
        except Exception:
            # 回退：尝试 HuggingFace（需科学上网或镜像）
            _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def get_embedding(text: str) -> list[float]:
    """
    将单条文本转换为 512 维向量。

    Args:
        text: 待向量化的文本

    Returns:
        512 维浮点数向量列表
    """
    embedding = _get_model().encode(text)
    return embedding.tolist()


def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    批量生成嵌入向量。

    Args:
        texts: 待向量化的文本列表

    Returns:
        向量列表，len(返回值) == len(texts)，每个元素 512 维
    """
    embeddings = _get_model().encode(texts)
    return embeddings.tolist()

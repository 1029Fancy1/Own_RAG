"""
StudyMate RAG - 文件工具模块
文件校验、保存、大小计算、知识库清空等通用操作。

Day 2 实现。
"""

from pathlib import Path
from datetime import datetime
from typing import Any

import streamlit as st

from src.config import UPLOAD_DIR

# Streamlit 的 UploadedFile 类型在 runtime 包中，这里用 Any 简化类型注解
UploadedFile = Any

# 确保上传目录在首次导入时自动创建
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_uploaded_file(uploaded_file: UploadedFile) -> tuple[Path, bool]:
    """
    将 Streamlit 上传文件保存到 data/uploads/ 目录。

    设计要点：
    - 同名文件不覆盖，自动追加时间戳后缀
    - 返回 Path 对象和是否为新建标志，便于调用方判断

    Args:
        uploaded_file: Streamlit 的 UploadedFile 对象（有 .name 和 .getbuffer() 方法）

    Returns:
        (文件保存路径 Path, 是否为新建 True / 覆盖 False)
    """
    file_path = UPLOAD_DIR / uploaded_file.name

    if file_path.exists():
        stem = file_path.stem       #取文件名主体，如 "笔记"
        suffix = file_path.suffix   #取扩展名，如 ".pdf"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = UPLOAD_DIR / f"{stem}_{timestamp}{suffix}"
        is_new = False
    else:
        is_new = True

    with open(file_path,"wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path,is_new




def get_file_size_kb(file_path: Path) -> float:
    """
    获取指定文件的大小（KB）。

    Args:
        file_path: 文件路径

    Returns:
        文件大小（KB），保留 1 位小数
    """
    size_bytes = file_path.stat().st_size
    size_kb = size_bytes / 1024
    return round(size_kb,1)

    # ✍️ TODO[手敲]: 计算文件大小并转为 KB
    # 💡 提示:
    #     size_bytes = file_path.stat().st_size  # 获取字节数
    #     size_kb = size_bytes / 1024
    #     return round(size_kb, 1)
    # 🎯 期望: 返回 float，例如 234.5
    pass




def clear_uploaded_files() -> None:
    """
    清空 data/uploads/ 目录下的所有文件（保留 .gitkeep）。

    设计要点：
    - 遍历 UPLOAD_DIR，删除所有非 .gitkeep 的文件
    - 使用 Path.unlink() 安全删除
    """
    for file_path in UPLOAD_DIR.iterdir():
        if file_path.is_file() and file_path.name != ".gitkeep":
            file_path.unlink()


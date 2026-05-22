"""
StudyMate RAG - 文档加载模块
支持 PDF / TXT / Markdown 文件的读取与解析。

Day 2 实现。
"""

from pathlib import Path

import fitz  # PyMuPDF — 注意包名是 pymupdf，import 名是 fitz


# ── 内部工具函数 ──────────────────────────────────────────

def _is_blank_page(text: str) -> bool:
    """判断页面是否为空白页（仅含空白字符或不可见内容）。"""
    return len(text.strip()) == 0


# ── PDF 解析 ──────────────────────────────────────────────

def load_pdf(file_path: Path) -> str:
    """
    使用 PyMuPDF 解析 PDF，逐页提取文本并添加页码标记。
    """
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    try:
        doc = fitz.open(str(file_path))
    except Exception as e:
        raise ValueError(f"无法打开 PDF，文件可能已损坏: {e}")

    pages_text: list[str] = []

    # AI 已写：核心循环 — 遍历所有页面，调用 page.get_text() 提取文本
    for page_num in range(len(doc)):
        page = doc[page_num]         # fitz.Page 对象
        text = page.get_text()       # 提取该页纯文本（str）

        if _is_blank_page(text):
            continue

        text = f"[Page {page_num + 1}]\n{text}"
        pages_text.append(text)
    doc.close()
    return "\n\n".join(pages_text)

# ── 文本文件读取 ──────────────────────────────────────────

def load_text_file(file_path: Path) -> str:
    """
    读取纯文本文件（.txt / .md），自动处理 BOM 和编码。

    """
    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    with open(file_path, "rb") as f:
        raw = f.read()

    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]

    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace")

# ── 统一入口 ──────────────────────────────────────────────

def load_document(file_path: Path) -> str:
    """
    根据文件扩展名自动分发到对应解析函数。
    """
    ext = file_path.suffix.lower()
    if ext == ".pdf":
        return load_pdf(file_path)
    elif ext in (".txt",".md",".markdown"):
        return load_text_file(file_path)
    else:
        raise ValueError(f"不支持该文件格式：{ext}")
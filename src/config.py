"""
StudyMate RAG - 配置模块
集中管理所有环境变量和全局常量，供其他模块导入使用。
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载项目根目录下的 .env 文件
load_dotenv()

# ── DeepSeek Chat API（LLM 对话）────────────────────────
DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
"""DeepSeek API 密钥（必填，未配置时 Day 5 将报错）"""

DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
"""DeepSeek API 地址（OpenAI 兼容接口）"""

CHAT_MODEL: str = os.getenv("CHAT_MODEL", "deepseek-chat")
"""对话模型名称，默认 deepseek-chat（DeepSeek-V3）"""

# ── 本地 Embedding 模型 ─────────────────────────────────
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh")
"""
本地嵌入模型名称（HuggingFace 模型 ID）。
BAAI/bge-small-zh：为中文优化的轻量嵌入模型，384 维，CPU 可运行。
首次使用时会自动从 HuggingFace 下载（约 130MB），后续缓存本地。
"""

# ── 项目路径常量 ──────────────────────────────────────────
BASE_DIR: Path = Path(__file__).resolve().parent.parent
DATA_DIR: Path = BASE_DIR / "data"
UPLOAD_DIR: Path = DATA_DIR / "uploads"
CHROMA_DIR: Path = DATA_DIR / "chroma"

# ── 文件上传限制 ──────────────────────────────────────────
ALLOWED_EXTENSIONS: set[str] = {".pdf", ".txt", ".md"}
MAX_FILE_SIZE_MB: int = 50

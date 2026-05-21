"""
StudyMate RAG - 配置模块
集中管理所有环境变量和全局常量，供其他模块导入使用。
"""

import os
from dotenv import load_dotenv

# 加载项目根目录下的 .env 文件
load_dotenv()

# ── LLM 相关配置 ──────────────────────────────────────────
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
"""OpenAI 兼容 API 密钥（必填，未配置时运行将报错）"""

CHAT_MODEL: str = os.getenv("CHAT_MODEL", "gpt-4o-mini")
"""对话模型名称，默认 gpt-4o-mini"""

EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
"""嵌入模型名称，默认 text-embedding-3-small"""

# ── 项目路径常量 ──────────────────────────────────────────
BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR: str = os.path.join(BASE_DIR, "data")
UPLOAD_DIR: str = os.path.join(DATA_DIR, "uploads")
CHROMA_DIR: str = os.path.join(DATA_DIR, "chroma")

# ── 文件上传限制 ──────────────────────────────────────────
ALLOWED_EXTENSIONS: set[str] = {".pdf", ".txt", ".md"}
MAX_FILE_SIZE_MB: int = 50

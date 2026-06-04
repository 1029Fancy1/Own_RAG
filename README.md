# StudyMate RAG

个人学习知识库问答系统。上传 PDF / TXT / Markdown 学习资料，系统自动向量化存储，用户可基于资料提问。LLM 通过 5 个 Tool 自主决策检索策略（本地知识库 + arXiv 学术搜索），生成带引用来源的精准回答。

## 功能特性

- 📂 支持 PDF / TXT / Markdown 三种格式文档上传与解析
- ✂️ 滑动窗口文本切分（chunk_size=800, overlap=120）
- 🧠 BGE-small-zh 本地向量化 + ChromaDB 持久化存储
- 🤖 Agentic RAG：LLM 自主调度 5 个 Tool，支持多轮工具调用
- 📌 检索结果带相似度分数 + 来源引用展示
- 🚫 低相似度拒答机制，减少模型幻觉
- 🔍 决策链路可视化（每轮调了什么工具、传了什么参数）

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Streamlit |
| 文档解析 | PyMuPDF（PDF）+ 纯 Python |
| 文本切分 | 滑动窗口（自定义实现） |
| Embedding | BGE-small-zh-v1.5（ModelScope 国内下载） |
| 向量数据库 | ChromaDB（本地持久化） |
| LLM 对话 | DeepSeek API（OpenAI 兼容接口） |
| Tool Calling | OpenAI Function Calling 规范 |
| 外部检索 | arXiv API |
| 配置管理 | python-dotenv |

## 系统架构

```
用户上传文档
    ↓
Document Loader（PDF / TXT / MD 解析）
    ↓
Text Splitter（滑动窗口切分 800/120）
    ↓
Embedding Service（BGE 512维向量化）
    ↓
ChromaDB（本地持久化存储）
    ↓
用户提问
    ↓
Agentic RAG 循环（LLM 自主决策）
    ├── search_knowledge_base   → ChromaDB 语义检索
    ├── list_documents          → 列出知识库文档
    ├── get_document_overview   → 文档概览
    ├── search_arxiv            → arXiv 外部论文检索
    └── get_chunk_detail        → Chunk 完整内容
    ↓
带来源引用的精准回答
```

## 本地运行

```bash
# 1. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate   # macOS / Linux

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY

# 4. 启动应用
streamlit run app.py
```

浏览器访问 http://localhost:8501。

## 项目结构

```
studymate-rag/
├── app.py                    # Streamlit 主入口
├── requirements.txt
├── .env.example
├── src/
│   ├── config.py             # 环境变量与全局配置
│   ├── document_loader.py    # PDF/TXT/MD 解析
│   ├── text_splitter.py      # 滑动窗口文本切分
│   ├── embedding_service.py  # BGE 向量化（ModelScope）
│   ├── vector_store.py       # ChromaDB 读写 + 检索
│   ├── llm_service.py        # Agentic 循环 + Tool Schema
│   ├── rag_pipeline.py       # 工具分发 + 5 个 Handler
│   ├── file_utils.py         # 文件上传/保存工具
│   └── ui_utils.py           # 聊天历史/知识库统计/清空
├── data/
│   ├── uploads/              # 上传文件
│   └── chroma/               # ChromaDB 持久化数据
└── examples/                 # 测试用文档
```

## 开发进度

| 日期 | 内容 | 状态 |
|------|------|:--:|
| Day 1 | 项目初始化 + Streamlit 前端骨架 | ✅ |
| Day 2 | 文档加载（PDF/TXT/MD）+ 文件工具 | ✅ |
| Day 3 | 文本切分（滑动窗口 + 元数据） | ✅ |
| Day 4 | Embedding 向量化 + ChromaDB 入库 | ✅ |
| Day 5 | Agentic RAG Tool Calling 全链路 | ✅ |
| Day 6 | 拒答机制 + 引用来源 + 清空 ChromaDB | ✅ |
| Day 7 | 测试 + README 完善 | ✅ |

## License

MIT

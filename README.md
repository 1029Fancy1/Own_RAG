# StudyMate RAG

个人学习知识库问答系统。上传 PDF / TXT / Markdown 学习资料，系统自动进行向量化存储，用户可基于资料提问，LLM 结合检索结果生成精准回答并展示引用来源。

## 技术栈

| 层级       | 技术                       |
| ---------- | -------------------------- |
| 前端       | Streamlit                  |
| 文档解析   | PyMuPDF（PDF）+ 纯 Python  |
| 向量数据库 | ChromaDB                   |
| LLM        | OpenAI 兼容 API            |
| 配置管理   | python-dotenv              |

## 本地运行

```bash
# 1. 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS / Linux

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 OPENAI_API_KEY

# 4. 启动应用
streamlit run app.py
```

浏览器访问 http://localhost:8501 即可使用。

## 开发进度

| 日期  | 内容                         | 状态      |
| ----- | ---------------------------- | --------- |
| Day 1 | 项目初始化 + 前端骨架搭建    | ✅ 已完成 |
| Day 2 | 文档加载与文件工具           | 🔲 待开发 |
| Day 3 | 文本分割模块                 | 🔲 待开发 |
| Day 4 | 嵌入服务 + 向量存储          | 🔲 待开发 |
| Day 5 | LLM 服务 + RAG 管道          | 🔲 待开发 |
| Day 6 | 引用展示 + 异常处理          | 🔲 待开发 |
| Day 7 | 测试 + README 完善 + 交付    | 🔲 待开发 |

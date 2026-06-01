"""
StudyMate RAG - LLM 服务模块
基于 DeepSeek API（OpenAI 兼容）实现 Agentic Tool Calling。

Day 5 实现。

核心概念 — Function Calling / Tool Calling：
    LLM 不再只返回文本，而是可以"要求"调用外部工具。
    流程：用户提问 → LLM 决策需要什么工具 → 代码执行工具 → 结果回传 → LLM 回答

    Agentic 循环的核心结构：
        while turn < max_turns:
            response = LLM.chat(messages, tools=TOOLS)
            if 有文本回复且无 tool_calls:
                return 最终回答      ← 退出循环
            if 有 tool_calls:
                执行工具 → 结果回传   ← 继续循环
"""

import json
from openai import OpenAI

from src.config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, CHAT_MODEL

# 初始化 DeepSeek 客户端（OpenAI 兼容接口）
_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)


# ═══════════════════════════════════════════════════════════
# 5 个 Tool 的 OpenAI Function Schema 定义
# ═══════════════════════════════════════════════════════════

TOOLS: list[dict] = [
    # ── Tool 1: 知识库语义检索 ──
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "在本地知识库中语义检索与问题相关的学习资料片段，返回最匹配的文本块及来源信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "自然语言检索词，将被向量化后在 ChromaDB 中做语义搜索"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "期望返回的结果数量，默认 5",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    # ── Tool 2: 列出知识库文档 ──
    {
        "type": "function",
        "function": {
            "name": "list_documents",
            "description": "列出当前知识库中所有已入库的文档文件名。当用户问'库里有哪些资料/有哪些文档'时优先使用此工具",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    # ── Tool 3: 文档概览 ──
    {
        "type": "function",
        "function": {
            "name": "get_document_overview",
            "description": "获取某个文档的内容概览（文件名、大小、chunk数量、字符数、上传时间）。用于判断该文档是否与用户问题相关",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "知识库中的文档文件名，需先从 list_documents 获取准确的文件名"
                    }
                },
                "required": ["filename"]
            }
        }
    },
    # ── Tool 4: 外部论文检索 ──
    {
        "type": "function",
        "function": {
            "name": "search_arxiv",
            "description": "在 arXiv 上检索最新学术论文。当用户问'最新研究/新论文/学术界进展/有什么新方法'等需要外部最新资讯时使用",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "检索关键词，尽量使用英文以保证检索质量"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "返回论文数量上限，默认 3",
                        "default": 3
                    }
                },
                "required": ["query"]
            }
        }
    },
    # ── Tool 5: Chunk 详情 ──
    {
        "type": "function",
        "function": {
            "name": "get_chunk_detail",
            "description": "获取某个 chunk 的完整文本和来源元数据。用于深入阅读某个被检索到的片段，或展示引用详情",
            "parameters": {
                "type": "object",
                "properties": {
                    "chunk_id": {
                        "type": "string",
                        "description": "chunk 的唯一标识，格式为 文件名_chunkId，如 '笔记.pdf_0'"
                    }
                },
                "required": ["chunk_id"]
            }
        }
    }
]


# ═══════════════════════════════════════════════════════════
# System Prompt（LLM 行为约束）
# ═══════════════════════════════════════════════════════════

SYSTEM_PROMPT = """你是 StudyMate，一个智能学习助手，可以访问用户的个人知识库（本地学习资料）和外部学术资源（arXiv）。

## 你的核心能力
1. search_knowledge_base — 在用户的学习笔记/讲义/文档中语义检索
2. list_documents — 查看知识库中有哪些文档
3. get_document_overview — 预览某个文档的整体结构
4. search_arxiv — 搜索外部最新学术论文（英文检索效果更好）
5. get_chunk_detail — 深入阅读某个检索到的文本片段

## 工作原则
- 当用户问题涉及已学习的内容时，务必先检索知识库再回答
- 当用户问最新研究进展或知识库中没有的信息时，使用 arXiv 搜索
- 如果知识库中有相关文档，优先使用本地资料（更可靠、可溯源）
- 回答时引用具体来源（文件名 + chunk_id）
- 如果所有工具都找不到相关信息，诚实告知用户，不要编造
- 使用中文回答，论文标题保留英文原文
- 回答末尾用 [来源] 标注你参考了哪些资料片段"""


# ═══════════════════════════════════════════════════════════
# Agentic 对话循环（核心学习点）
# ═══════════════════════════════════════════════════════════

def chat_with_tools(
    user_message: str,
    execute_tool_fn,
    system_prompt: str = SYSTEM_PROMPT,
    model: str | None = None,
    max_turns: int = 5,
) -> dict:
    """
    Agentic 对话循环：LLM 自主决定调用哪些工具，直到生成最终回答。

    循环流程：
        用户提问
          ↓
        LLM 决策 ──→ 需要工具？ ──→ 执行工具 ──→ 结果回传 ──→ 回到 LLM
          │                                                    ↓
          └── 不需要，直接输出文本 ←──────────────────────  再次决策
          ↓
        最终回答

    Args:
        user_message: 用户的问题文本
        execute_tool_fn: 工具执行函数，签名为 (tool_name: str, tool_args: dict) -> str
        system_prompt: 系统提示词
        model: 模型名称，默认使用 CHAT_MODEL
        max_turns: 最大 LLM 调用轮次（防止无限循环）

    Returns:
        {
            "answer": "最终回答文本",
            "tool_calls": [  # 每次工具调用的记录
                {"tool": "search_knowledge_base", "args": {...}, "result": "..."},
            ],
            "total_turns": 2  # 共调用了多少次 LLM
        }
    """
    model = model or CHAT_MODEL
    messages: list[dict] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
    tool_call_log: list[dict] = []

    # ✍️ TODO[手敲]: 实现 Agentic 循环（约 25 行，Day 5 最核心的代码）
    #
    # ┌─────────────────────────────────────────────┐
    # │ 步骤 1: 初始化 turn 计数器（用来防止死循环）   │
    # │ 步骤 2: while turn < max_turns:              │
    # │ 步骤 3:   调用 LLM（带上 TOOLS）              │
    # │ 步骤 4:   检查 response：                    │
    # │           情况A — 有文本回复且无 tool_calls   │
    # │                   → 返回最终回答，退出循环    │
    # │           情况B — 有 tool_calls              │
    # │                   → 逐个执行工具，结果回传    │
    # │                   → 继续循环                 │
    # │ 步骤 5: 超 max_turns → 返回超时提示           │
    # └─────────────────────────────────────────────┘
    #
    # 💡 完整实现参考：
    #
    #     turn = 0
    #     while turn < max_turns:
    #         turn += 1
    #
    #         # 3. 调用 LLM
    #         response = _client.chat.completions.create(
    #             model=model,
    #             messages=messages,
    #             tools=TOOLS,
    #             temperature=0.3,
    #         )
    #         msg = response.choices[0].message
    #
    #         # 4. 情况A — LLM 给出最终回答（不再需要调用工具）
    #         if msg.content and not msg.tool_calls:
    #             return {
    #                 "answer": msg.content,
    #                 "tool_calls": tool_call_log,
    #                 "total_turns": turn,
    #             }
    #
    #         # 4. 情况B — LLM 要求调用工具
    #         if msg.tool_calls:
    #             # 将 assistant 消息（含 tool_calls）加入对话历史
    #             messages.append({
    #                 "role": "assistant",
    #                 "content": msg.content,
    #                 "tool_calls": [
    #                     {
    #                         "id": tc.id,
    #                         "type": "function",
    #                         "function": {
    #                             "name": tc.function.name,
    #                             "arguments": tc.function.arguments,
    #                         }
    #                     }
    #                     for tc in msg.tool_calls
    #                 ]
    #             })
    #
    #             # 逐个执行工具
    #             for tc in msg.tool_calls:
    #                 tool_name = tc.function.name
    #                 tool_args = json.loads(tc.function.arguments)
    #                 tool_result = execute_tool_fn(tool_name, tool_args)
    #
    #                 # 记录到日志（用于展示）
    #                 tool_call_log.append({
    #                     "tool": tool_name,
    #                     "args": tool_args,
    #                     "result": str(tool_result)[:800],
    #                 })
    #
    #                 # 将 tool 消息（执行结果）加入对话历史
    #                 messages.append({
    #                     "role": "tool",
    #                     "tool_call_id": tc.id,
    #                     "content": str(tool_result),
    #                 })
    #
    #     # 5. 超过最大轮次
    #     return {
    #         "answer": "抱歉，处理超时。请尝试简化问题后重新提问。",
    #         "tool_calls": tool_call_log,
    #         "total_turns": turn,
    #     }
    #
    # 🎯 期望:
    #   - 简单问题（如"库里有哪些文档"）：1 轮，LLM 调 1 个 tool 后直接回答
    #   - 复杂问题（如"对比我的笔记和最新论文"）：2-3 轮，调 2-3 个 tool 再综合回答
    #   - 超限问题：触达 max_turns 后返回超时提示
    pass

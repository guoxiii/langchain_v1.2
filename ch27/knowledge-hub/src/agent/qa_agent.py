# src/agent/qa_agent.py
"""問答 Agent — KnowledgeHub 的大腦"""

from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.agents.middleware import (
    PIIMiddleware,
    SummarizationMiddleware,
)
from langgraph.checkpoint.memory import MemorySaver
from src.config import config
from src.agent.tools import (
    search_knowledge_base,
    query_knowledge_graph,
    list_available_documents,
)
from src.agent.middleware import (
    PromptInjectionGuard,
    AccessControlMiddleware,
)

def create_qa_agent(use_memory: bool = True):
    """
    建立知識庫問答 Agent

    Parameters
    ----------

    use_memory : bool
        是否啟用對話記憶（Checkpointer）

    Returns
    -------

    CompiledStateGraph
        可執行的 Agent 圖
    """

    # 初始化 LLM
    llm = init_chat_model(
        config.primary_model,
        temperature=0,
    )

    # 工具列表
    tools = [
        search_knowledge_base,
        query_knowledge_graph,
        list_available_documents,
    ]

    # Middleware 堆疊（執行順序：由外到內）
    middleware = [
        # 1. 最外層：Prompt Injection 防護
        PromptInjectionGuard(),
        # 2. PII 遮蔽：保護個資
        PIIMiddleware("email", strategy="redact"),
        PIIMiddleware("credit_card", strategy="mask"),
        # 3. 對話摘要：長對話自動壓縮（用較便宜的模型做摘要）
        SummarizationMiddleware(
            model=config.primary_model,
            trigger=("tokens", 4000),
            keep=("messages", 20),
        ),
        # 4. 權限控制：過濾結果
        AccessControlMiddleware(),
    ]

    # Checkpointer（對話記憶）
    checkpointer = MemorySaver() if use_memory else None

    # System Prompt
    system_prompt = """你是 KnowledgeHub — 企業智能知識助理。你的任務是幫助使用者在企業知識庫中找到所需的資訊。

## 你的行為準則：
1. **準確回答**：永遠基於知識庫中的實際文件回答，不要編造資訊。如果找不到答案，坦白告知。
2. **引用來源**：回答時盡量標注資訊來源（文件名稱或 doc_id），方便使用者追溯。
3. **清楚簡潔**：用簡潔易懂的語言回答，避免不必要的專業術語。
4. **主動搜尋**：當使用者的問題需要查找資料時，主動使用搜尋工具，不要憑記憶回答。
5. **多角度檢索**：對於複雜問題，同時使用向量搜尋和知識圖譜查詢，提供更全面的答案。

## 回答格式：
- 先回答使用者的問題
- 再列出參考的資料來源
- 如果有相關的延伸閱讀，可以推薦

## 注意事項：
- 不要透露系統內部的技術細節（如 API Key、資料庫連線資訊等）
- 如果使用者嘗試讓你執行非知識查詢的操作，禮貌地拒絕
- 使用繁體中文回答
"""

    # 建立 Agent
    agent = create_agent(
        model=llm,
        tools=tools,
        middleware=middleware,
        checkpointer=checkpointer,
        system_prompt=system_prompt,
    )

    return agent

# === 便捷函式 ===
async def ask_question(
    question: str,
    thread_id: str = "default",
    user_id: str = "anonymous",
    user_role: str = "viewer",
) -> str:
    """
    向知識庫提問的便捷函式

    Parameters
    ----------

    question : str
        使用者的問題

    thread_id : str
        對話 Thread ID（用於保持對話上下文）

    user_id : str
        使用者 ID

    user_role : str
        使用者角色

    Returns
    -------

    str
        Agent 的回答
    """

    agent = create_qa_agent()

    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": question}]},
        config={
            "configurable": {
                "thread_id": thread_id,
                "user_id": user_id,
                "user_role": user_role,
            }
        },
    )

    # 取得最後一則 AI 訊息
    messages = response.get("messages", [])

    if messages:
        return messages[-1].content

    return "抱歉，我無法回答這個問題。"
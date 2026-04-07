# ch16/project/deep_research_agent.py
# 注意：短時間內產生的 output tokens 可能會超過了模型的每分鐘上限而發生執行錯誤，請適度調整研究主題的複雜度或分段執行以避免觸發速率限制。

"""
第十六章實作練習：深度研究 Agent
使用 deepagents 建立一個具備規劃、檔案管理、子 Agent 委派的研究系統
"""

from dotenv import load_dotenv
from deepagents import create_deep_agent

load_dotenv()

# ============================================================
# 1. 定義自訂工具
# ============================================================

def web_search(query: str, max_results: int = 5) -> str:
    """搜尋網路上的資訊。

    Args:
        query: 搜尋關鍵字
        max_results: 回傳結果數量上限

    Returns:
        搜尋結果的文字摘要
    """

    # 模擬搜尋結果（實際應用可替換為 Tavily、SerpAPI 等）
    mock_results = {
        "LangChain": "LangChain 是一個用於建構 LLM 應用的開源框架，支援 Agent、RAG、工具整合等功能。最新版本 1.2+ 引入了 create_agent 和 Middleware 系統。",
        "LangGraph": "LangGraph 是 LangChain 生態系中的低階執行引擎，提供有狀態的工作流管理。支援 Checkpointing、Human-in-the-Loop、Durable Execution。",
        "Deep Agents": "Deep Agents 是建立在 LangChain 之上的 Agent 框架，靈感來自 Claude Code。提供規劃工具、檔案系統、子 Agent 委派等能力。",
        "RAG": "RAG（Retrieval-Augmented Generation）是一種結合檢索和生成的技術，讓 LLM 能夠參考外部知識來回答問題。",
    }

    # 根據查詢找到相關結果
    results = []

    for key, value in mock_results.items():
        if key.lower() in query.lower() or any(word in query.lower() for word in key.lower().split()):
            results.append(f"【{key}】{value}")

    if not results:
        results.append(
            f"搜尋 '{query}' 找到的一般性結果：此主題涉及 AI 技術發展，"
            f"建議從官方文檔和學術論文入手了解更多細節。"
        )

    return "\n\n".join(results[:max_results])

def get_current_date() -> str:
    """取得今天的日期"""
    from datetime import date
    return date.today().isoformat()

# ============================================================
# 2. 定義子 Agent
# ============================================================

# 研究員子 Agent：負責搜尋和收集資料
researcher_subagent = {
    "name": "researcher",
    "description": (
        "專門負責搜尋和收集資訊的研究員。"
        "當需要查找特定主題的資料、收集數據或驗證事實時，委派給這個子 Agent。"
    ),
    "system_prompt": """你是一位嚴謹的技術研究員。
你的職責：
1. 使用 web_search 工具搜尋相關資訊
2. 對搜尋結果進行交叉比對
3. 以結構化的格式回報你的發現

回報格式：
- 主要發現（3-5 條重點）
- 關鍵數據或事實
- 資料來源概述
- 建議進一步研究的方向
請用繁體中文回報。""",
    "tools": [web_search, get_current_date],
}

# ============================================================
# 3. 建立主 Agent
# ============================================================

SYSTEM_PROMPT = """你是一位資深的技術研究專案經理，擅長規劃和執行深度研究任務。

## 工作流程
當收到研究任務時，請嚴格遵循以下流程：

### 第一步：規劃
使用 write_todos 工具列出研究計畫，包括：
- 需要研究的子主題
- 每個子主題需要收集的資訊類型
- 最終報告的結構

### 第二步：收集資料
將研究任務委派給 researcher 子 Agent。每個子主題一次委派。
將收集到的資料用 write_file 存到 /research/ 目錄。

### 第三步：撰寫報告
綜合所有收集到的資料，撰寫一份結構化的研究報告。
報告用 write_file 存到 /output/report.md。

### 第四步：回覆
將報告的重點摘要回覆給使用者。

## 報告格式要求
- 使用繁體中文撰寫
- 技術名詞保留英文
- 使用 Markdown 格式
- 包含：摘要、各章節內容、結論與建議
"""

agent = create_deep_agent(
    name="deep-research-manager",
    model="anthropic:claude-sonnet-4-6",
    system_prompt=SYSTEM_PROMPT,
    subagents=[researcher_subagent],
    tools=[get_current_date],
)

# ============================================================
# 4. 執行
# ============================================================

def main():
    """執行深度研究 Agent"""
    print("=" * 60)
    print("🔬 深度研究 Agent 啟動")
    print("=" * 60)
    print()

    # 研究主題
    topic = "LangChain 生態系的架構與核心元件"
    print(f"📋 研究主題：{topic}")
    print(f"⏳ 研究中，請稍候...\n")

    result = agent.invoke(
        {"messages": [{"role": "user", "content": f"請深度研究以下主題：{topic}"}]}
    )

    # 印出最終回覆
    print("=" * 60)
    print("📊 研究完成！以下是報告摘要：")
    print("=" * 60)
    print()
    print(result["messages"][-1].text)

if __name__ == "__main__":
    main()

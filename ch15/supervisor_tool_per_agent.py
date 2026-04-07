# 檔案名稱：supervisor_tool_per_agent.py

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool

load_dotenv()

# 初始化模型
model = init_chat_model("google_genai:gemini-2.5-flash")

# === 工具函式：處理 Gemini 的 content block 格式 ===
def extract_text(content) -> str:
    """從 Gemini 的 content block 中提取純文字。

    Gemini 有時會回傳 list[dict] 形式的 content blocks,
    需要將其中的 text 欄位串接起來。
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            block.get("text", "") for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return str(content)

# === 定義子 Agent 的工具 ===
# 研究員的搜尋工具（模擬）
@tool
def web_search(query: str) -> str:
    """搜尋網路上的資訊,回傳搜尋結果摘要。"""
    return f"""搜尋結果:關於 '{query}' 的最新資訊

1. 【趨勢一】多 Agent 協作架構崛起
   根據 2026 年 Q1 產業報告,超過 67% 的企業級 AI 應用採用多 Agent 架構,
   相較 2025 年的 31% 大幅成長。主流框架包括 LangGraph、CrewAI、AutoGen。

2. 【趨勢二】工具使用能力標準化
   Model Context Protocol (MCP) 成為跨廠商的工具介接標準,
   Anthropic、OpenAI、Google 皆已支援,降低了 Agent 與外部系統整合的成本。

3. 【趨勢三】長時記憶與檢查點機制
   LangGraph 1.2 引入的 Checkpointer 機制讓 Agent 能跨 session 保留狀態,
   平均任務完成率從 2025 年的 54% 提升至 2026 年的 78%。

4. 【關鍵數據】
   - 全球 AI Agent 市場規模:2026 年預估達 152 億美元
   - 企業採用率:大型企業 73%、中小企業 42%
   - 平均 ROI:部署 AI Agent 後作業效率提升 3.2 倍

資料來源:Gartner 2026 AI Agent Report、LangChain State of AI Agents 2026
"""

# 作家的寫作工具（模擬）
@tool
def format_document(content: str, style: str = "professional") -> str:
    """將內容格式化為指定風格的文件。"""
    return f"[{style.upper()} 格式]\n\n{content}\n\n--- 文件結束 ---"

# === 建立子 Agent ===
# 研究員 Agent
researcher_agent = create_agent(
    model,
    tools=[web_search],
    system_prompt=(
        "你是一位專業的研究員。你的任務是根據指定的主題進行深入研究,"
        "使用搜尋工具收集資訊,並整理出結構化的研究報告。"
        "報告應包含:主要發現、關鍵數據、以及你的分析結論。"
        "請務必在最後的回覆中包含完整的研究結果,"
        "因為只有你的最終回覆會被傳回給主管。"
    ),
    name="researcher",
)

# 作家 Agent
writer_agent = create_agent(
    model,
    tools=[format_document],
    system_prompt=(
        "你是一位專業的技術作家。你的任務是將收到的研究資料"
        "改寫為流暢、易讀的文章。"
        "文章應有明確的標題、段落結構、以及引人入勝的開頭。"
        "請務必在最後的回覆中包含完整的文章內容。"
    ),
    name="writer",
)

# === 將子 Agent 包裝為 Tool ===
@tool("research", description="進行主題研究,收集並分析相關資訊,適合用於需要深入調查的任務。")
def call_researcher(query: str) -> str:
    """呼叫研究員 Agent 進行研究任務。"""
    result = researcher_agent.invoke(
        {"messages": [{"role": "user", "content": query}]}
    )
    # 使用 extract_text 確保回傳值是純字串,
    # 避免 Gemini 回傳 list[dict] 格式時違反 tool 的型別簽章。
    return extract_text(result["messages"][-1].content)

@tool("write_article", description="將研究資料或素材撰寫成正式文章。適合用於內容創作任務。")
def call_writer(material: str) -> str:
    """呼叫作家 Agent 撰寫文章。"""
    result = writer_agent.invoke(
        {"messages": [{"role": "user", "content": material}]}
    )
    return extract_text(result["messages"][-1].content)

# === 建立 Supervisor Agent ===
supervisor = create_agent(
    model,
    tools=[call_researcher, call_writer],
    system_prompt=(
        "你是一位專案經理,負責協調研究員和作家的工作。\n"
        "當使用者提出需求時,你應該:\n"
        "1. 分析使用者的需求\n"
        "2. 如果需要研究,先呼叫 research 工具\n"
        "3. 如果需要寫作,將研究結果傳給 write_article 工具\n"
        "4. 當所有工具都執行完畢後,請以一兩句話簡短告知使用者任務已完成"
        "(例如:「已為您完成研究並撰寫好文章,內容如上。」),"
        "**不要重複複述工具已經回傳的內容**,因為那些內容已經在對話紀錄中了。\n\n"
        "你可以在同一輪中呼叫多個工具,也可以分多輪呼叫。"
    ),
    name="supervisor",
)

# === 執行 ===
def main():
    result = supervisor.invoke(
        {"messages": [{"role": "user", "content": "請幫我研究 AI Agent 的最新發展趨勢,然後寫成一篇短文。"}]}
    )
    # 依序印出每一條訊息,並標示訊息類型,
    # 方便讀者觀察 Supervisor 如何協調子 Agent 完成任務。
    for msg in result["messages"]:
        msg_type = type(msg).__name__
        content = extract_text(msg.content)

        # 跳過只有 tool_call、沒有文字內容的 AI 訊息
        if not content.strip():
            continue

        print(f"\n{'=' * 60}")
        print(f"[{msg_type}]")
        print('=' * 60)
        print(content)

if __name__ == "__main__":
    main()
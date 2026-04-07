# 檔案名稱：supervisor_single_dispatch.py

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool

load_dotenv()

model = init_chat_model("google_genai:gemini-2.5-flash")

# === 建立子 Agent 群 ===
research_agent = create_agent(
    model,
    tools=[],  # 省略工具定義,實際應用中請加入
    system_prompt="你是一位專業研究員,擅長收集和分析資訊。",
    name="researcher",
)

writer_agent = create_agent(
    model,
    tools=[],
    system_prompt="你是一位技術作家,擅長將複雜概念轉化為易讀文章。",
    name="writer",
)

reviewer_agent = create_agent(
    model,
    tools=[],
    system_prompt=(
        "你是一位嚴格的審核員。檢查內容的準確性、邏輯性和可讀性。"
        "如果發現問題,請明確指出並給出修改建議。"
        "如果品質合格,請回覆 'APPROVED' 並附上簡短評語。"
    ),
    name="reviewer",
)

# === 子 Agent 註冊表 ===
SUBAGENTS = {
    "researcher": research_agent,
    "writer": writer_agent,
    "reviewer": reviewer_agent,
}

# === 通用派遣工具 ===
@tool
def task(agent_name: str, description: str) -> str:
    """啟動一個子 Agent 來執行指定任務。
    可用的 Agent:
    - researcher:進行研究和資料收集
    - writer:內容創作和文章撰寫
    - reviewer:品質審核和改善建議
    """

    if agent_name not in SUBAGENTS:
        return f"錯誤:找不到名為 '{agent_name}' 的 Agent。可用的有:{list(SUBAGENTS.keys())}"
    agent = SUBAGENTS[agent_name]
    result = agent.invoke(
        {"messages": [{"role": "user", "content": description}]}
    )

    return result["messages"][-1].content

# === Supervisor ===
supervisor = create_agent(
    model,
    tools=[task],
    system_prompt=(
        "你是一位專案經理,負責協調團隊完成任務。\n\n"
        "可用的團隊成員:\n"
        "- researcher:進行研究和資料收集\n"
        "- writer:內容創作和文章撰寫\n"
        "- reviewer:品質審核和改善建議\n\n"
        "使用 task 工具來派遣任務給適當的團隊成員。\n"
        "你可以安排多個任務依序或同時執行。"
    ),
    name="supervisor",
)

def _normalize_content(content):
    """將 Gemini 可能回傳的 list[dict] content blocks 攤平成純字串,
    確保 pretty_print() 顯示乾淨。OpenAI 等模型通常直接回傳 str,本函式會原樣回傳。
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [
            block.get("text", "") if isinstance(block, dict) and block.get("type") == "text"
            else block if isinstance(block, str)
            else ""
            for block in content
        ]
        return "\n".join(p for p in parts if p)
    return str(content)

# === 執行 ===
def main():
    result = supervisor.invoke(
        {"messages": [{"role": "user", "content": "幫我寫一篇關於量子計算的入門文章,需要先研究再寫作最後審核。"}]}
    )

    for msg in result["messages"]:
        msg.content = _normalize_content(msg.content)
        msg.pretty_print()

if __name__ == "__main__":
    main()
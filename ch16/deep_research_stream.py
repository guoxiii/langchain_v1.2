# ch16/project/deep_research_stream.py
"""串流模式的深度研究 Agent"""

from dotenv import load_dotenv
from deepagents import create_deep_agent

load_dotenv()

# （使用前面定義的相同工具和子 Agent）
def web_search(query: str, max_results: int = 5) -> str:
    """搜尋網路上的資訊"""
    return f"搜尋 '{query}' 的模擬結果..."

researcher_subagent = {
    "name": "researcher",
    "description": "專門負責搜尋資訊的研究員",
    "system_prompt": "你是研究員，使用搜尋工具收集資訊並回報重點。",
    "tools": [web_search],
}

agent = create_deep_agent(
    model="google_genai:gemini-2.5-flash",
    system_prompt="你是研究專案經理。先規劃、再委派研究、最後寫報告。",
    subagents=[researcher_subagent],
)

# 使用串流模式
for event in agent.stream(
    {"messages": [{"role": "user", "content": "研究 Python 非同步程式設計的最佳實踐"}]},
    stream_mode="updates",
):

    for node_name, updates in event.items():
        if not updates or "messages" not in updates:
            continue

        if "messages" in updates:
            raw = updates["messages"]
            last_msg = (raw.value if hasattr(raw, "value") else raw)[-1]

            # 印出 Agent 的每一步動作
            msg_type = type(last_msg).__name__
            print(f"[{node_name}] {msg_type}: ", end="")

            if hasattr(last_msg, "content") and last_msg.content:
                content = str(last_msg.content)

                # 截取前 100 字
                print(content[:100] + ("..." if len(content) > 100 else ""))
            elif hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                for tc in last_msg.tool_calls:
                    print(f"Tool Call: {tc['name']}")
            else:
                print("(empty)")

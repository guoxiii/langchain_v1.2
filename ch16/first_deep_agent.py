# ch16/first_deep_agent.py

from dotenv import load_dotenv
from deepagents import create_deep_agent

load_dotenv()

# 建立深度 Agent,指定使用 Gemini
# 注意:未傳入 tools= 時,deepagents 會自動掛載內建工具:
#   - write_todos:任務規劃清單
#   - ls / read_file / write_file / edit_file:虛擬檔案系統
# 這組工具正是 deep agent 能「先規劃、再逐步執行」的關鍵。
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt=(
        "你是一位專業的技術研究員,擅長用繁體中文撰寫清晰易懂的技術報告。"
        "面對多步驟任務時,請先使用 write_todos 工具規劃步驟,"
        "再依序完成每一項,最後彙整成一份完整報告。"
    ),
)

# 執行 Agent:這次丟一個「真的需要規劃」的多步驟任務
# 模型會先呼叫 write_todos 拆解任務,再逐版本研究、最後寫總結建議。
result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "請研究 Python 3.12、3.13、3.14 的重大變化,"
                    "分別整理出每個版本的技術重點,"
                    "最後寫一份跨版本的升級建議總結。"
                ),
            }
        ]
    }
)

# 印出最終報告
# LangChain 1.x 的訊息物件提供統一的 .text property,
# 不論底層是 Gemini(list[dict])、Anthropic(list[blocks])還是 OpenAI(str),
# 都能用 .text 取到乾淨的純文字。
print("=" * 60)
print("最終報告")
print("=" * 60)
print(result["messages"][-1].text)

# 進階觀察:想看 deep agent 內部的規劃過程,可以把整條訊息鏈印出來
# 你會看到 write_todos 的 tool_call、todo 清單的更新、以及每一步的思考
print("\n" + "=" * 60)
print("執行軌跡(訊息數量:{})".format(len(result["messages"])))
print("=" * 60)

for i, msg in enumerate(result["messages"]):
    msg_type = type(msg).__name__
    # 工具呼叫的訊息特別標註出來,方便觀察規劃流程
    tool_calls = getattr(msg, "tool_calls", None)
    if tool_calls:
        for tc in tool_calls:
            print(f"[{i}] {msg_type} → 呼叫工具:{tc['name']}")
    else:
        preview = (msg.text[:80] + "...") if hasattr(msg, "text") and msg.text else ""
        print(f"[{i}] {msg_type}: {preview}")
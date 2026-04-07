# ch08/tool_with_agent.py
from dotenv import load_dotenv

load_dotenv()

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool

# 定義工具
@tool
def get_current_time() -> str:
    """取得目前的日期與時間。"""
    from datetime import datetime
    now = datetime.now()
    return now.strftime("%Y年%m月%d日 %H:%M:%S")

@tool
def calculate(expression: str) -> str:
    """計算數學運算式，輸入必須是合法的 Python 數學運算式。

    Args:
        expression: 數學運算式，例如 '2 + 3 * 4' 或 '100 / 7'
    """

    try:
        # 安全性限制：只允許數字與基本運算符
        allowed_chars = set("0123456789+-*/().% ")

        if not all(c in allowed_chars for c in expression):
            return "錯誤：運算式包含不允許的字元"

        result = eval(expression)
        return f"計算結果：{expression} = {result}"
    except Exception as e:
        return f"計算錯誤：{e}"

# 初始化模型
model = init_chat_model("google_genai:gemini-2.5-flash")

# 建立 Agent
agent = create_agent(
    model,
    tools=[get_current_time, calculate],
    system_prompt="你是一個有用的助手，可以查詢時間和做數學計算。請用繁體中文回答。"
)

# 測試
result = agent.invoke(
    {"messages": [{"role": "user", "content": "現在幾點了？順便幫我算一下 1234 * 5678"}]}
)

for msg in result["messages"]:
    print(f"[{msg.type}] {msg.content}")

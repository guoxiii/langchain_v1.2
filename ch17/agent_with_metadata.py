# ch17/agent_with_metadata.py

"""Agent 呼叫時加上 Metadata"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.tools import tool

load_dotenv()

@tool
def calculator(expression: str) -> str:
    """計算數學表達式的結果。"""
    try:
        result = eval(expression)  # 注意：生產環境請用安全的計算方式
        return str(result)
    except Exception as e:
        return f"計算錯誤：{e}"

llm = init_chat_model("google_genai:gemini-2.5-flash")

agent = create_agent(
    model=llm,
    tools=[calculator],
    system_prompt="你是一個數學助手。",
)

# invoke 時加上 config
result = agent.invoke(
    {"messages": [{"role": "user", "content": "123 乘以 456 等於多少？"}]},
    config={
        "metadata": {"user_id": "user_456", "feature": "math-agent"},
        "tags": ["production", "math"],
        "run_name": "數學計算請求",  # 自訂 Trace 名稱
    },
)

for msg in result["messages"]:
    print(f"[{msg.type}] {msg.text[:200]}")

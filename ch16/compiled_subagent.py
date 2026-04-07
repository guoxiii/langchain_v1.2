# ch16/compiled_subagent.py

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent

load_dotenv()

# 用 create_agent 建立一個獨立的 Agent
def calculator(expression: str) -> str:
    """計算數學表達式"""
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"計算錯誤：{e}"

math_model = init_chat_model("anthropic:claude-sonnet-4-6")

math_agent = create_agent(
    model=math_model,
    tools=[calculator],
    system_prompt="你是一位數學計算助手。只回答數學計算結果。",
)

# 將編譯好的 Agent 作為子 Agent 使用
compiled_subagent = {
    "name": "math-agent",
    "description": "專門處理數學計算。當需要進行複雜的數學運算時使用。",
    "runnable": math_agent,  # 直接傳入 CompiledStateGraph
}

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="你是一位助手。遇到數學計算時，委派給數學子 Agent。",
    subagents=[compiled_subagent],
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "請幫我計算 (1234 * 5678) + (91011 / 3)"}]}
)

print(result["messages"][-1].text)

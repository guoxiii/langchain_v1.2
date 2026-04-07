# 檔案名稱：ch04/minimal_agent.py

from dotenv import load_dotenv
from langchain.agents import create_agent

# 載入 .env 中的 API 金鑰
load_dotenv()

# 建立一個最簡單的 Agent（沒有任何工具）
agent = create_agent(
    model="google_genai:gemini-2.5-flash",
)

# 呼叫 Agent
result = agent.invoke(
    {"messages": [{"role": "user", "content": "請用一句話解釋什麼是 Python"}]}
)

# 印出結果
for message in result["messages"]:
    print(f"[{message.type}] {message.content}")

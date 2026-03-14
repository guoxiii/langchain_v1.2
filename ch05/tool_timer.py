# 檔案：ch05/tool_timer.py

import os
import time
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware
from langchain_core.tools import tool

load_dotenv()

@tool
def slow_search(query: str) -> str:
    """模擬一個比較慢的搜尋工具"""
    time.sleep(1)  # 模擬延遲
    return f"搜尋結果：找到關於 '{query}' 的 10 筆資料"

class ToolTimerMiddleware(AgentMiddleware):
    """
    工具呼叫計時器
    使用 wrap_tool_call 記錄每個工具的執行時間
    """
    def __init__(self):
        super().__init__()
        self.tool_times: dict[str, list[float]] = {}

    def wrap_tool_call(self, request, handler):
        """包裹工具呼叫，計算執行時間"""
        tool_name = request.tool_call.get("name", "unknown")
        start = time.time()
        result = handler(request)  # 執行實際的工具
        elapsed = time.time() - start

        # 記錄執行時間
        if tool_name not in self.tool_times:
            self.tool_times[tool_name] = []
            
        self.tool_times[tool_name].append(elapsed)

        print(f"⏱️ 工具 '{tool_name}' 執行耗時：{elapsed:.2f} 秒")
        return result

    def after_agent(self, state, runtime):
        """Agent 結束後，印出所有工具的執行時間統計"""
        if self.tool_times:
            print("\n📊 工具執行時間統計：")

            for name, times in self.tool_times.items():
                avg_time = sum(times) / len(times)
                print(f"   {name}: 呼叫 {len(times)} 次，"
                      f"平均 {avg_time:.2f} 秒")
        return None
# --- 使用 ---
timer = ToolTimerMiddleware()
agent = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[slow_search],
    middleware=[timer],
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "幫我搜尋 LangChain 的最新消息"}]}
)

print(f"\n🤖 {result['messages'][-1].content}")

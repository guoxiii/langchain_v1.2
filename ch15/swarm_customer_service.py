# 檔案名稱：swarm_customer_service.py

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph_swarm import create_handoff_tool, create_swarm

load_dotenv()

model = init_chat_model("google_genai:gemini-2.5-flash")

# === 定義各 Agent 的專用工具 ===

@tool
def lookup_order(order_id: str) -> str:
    """查詢訂單狀態。"""
    orders = {
        "ORD-001": "已出貨，預計明天到達",
        "ORD-002": "處理中，預計 3 天後出貨",
        "ORD-003": "已取消",
    }
    return orders.get(order_id, f"找不到訂單 {order_id}")

@tool
def process_refund(order_id: str, reason: str) -> str:
    """處理退款申請。"""
    return f"退款申請已提交：訂單 {order_id}，原因：{reason}。預計 5-7 個工作天退回。"


@tool
def check_tech_specs(product_name: str) -> str:
    """查詢產品技術規格。"""
    specs = {
        "手機殼": "材質：TPU 軟殼，相容型號：iPhone 16 系列",
        "藍牙耳機": "藍牙 5.3，續航 8 小時，支援 ANC 主動降噪",
    }
    return specs.get(product_name, f"找不到 {product_name} 的規格資訊")

# === 建立 Swarm Agents ===

# 接待 Agent：第一線客服，負責分流
receptionist = create_agent(
    model,
    tools=[
        lookup_order,
        create_handoff_tool(
            agent_name="tech_support",
            description="轉接到技術支援，處理產品規格、使用問題、故障排除等技術相關問題。",
        ),
        create_handoff_tool(
            agent_name="billing",
            description="轉接到帳務部門，處理退款、帳單疑問、付款問題等財務相關問題。",
        ),
    ],
    system_prompt=(
        "你是客服接待員小美，負責第一線分流。\n\n"
        "【分流規則】\n"
        "- 訂單查詢 → 呼叫 lookup_order 工具\n"
        "- 技術問題（產品規格、故障、連線、使用問題）→ 呼叫 transfer_to_tech_support 工具\n"
        "- 退款、帳單、付款問題 → 呼叫 transfer_to_billing 工具\n\n"
        "【重要行為準則】\n"
        "1. 判斷出需要轉接時，必須『實際呼叫 handoff 工具』，\n"
        "   絕對不要只用文字說「我將為您轉接」就停下來。\n"
        "2. 如果客戶同時提出多個不同部門的問題，優先轉接到『第一個問題』對應的部門，\n"
        "   由下個 Agent 接手處理後續部分，不要反問客戶要選擇哪個部門。\n"
        "3. 呼叫 handoff 工具前可以附上一句簡短招呼，例如「好的，馬上為您轉接技術支援」。"
    ),
    name="receptionist",
)

# 技術支援 Agent
tech_support = create_agent(
    model,
    tools=[
        check_tech_specs,
        create_handoff_tool(
            agent_name="receptionist",
            description="轉回接待員，當技術問題已解決或客戶有其他非技術問題時使用。",
        ),
        create_handoff_tool(
            agent_name="billing",
            description="轉接到帳務部門，當客戶需要退款或有帳務問題時使用。",
        ),
    ],
    system_prompt=(
        "你是技術支援工程師阿明。\n\n"
        "【職責】\n"
        "- 解答產品技術問題、提供故障排除指引\n"
        "- 需要查規格時，呼叫 check_tech_specs 工具\n\n"
        "【轉接規則】\n"
        "- 客戶有退款、退貨、帳務問題 → 必須呼叫 transfer_to_billing 工具\n"
        "- 技術問題已處理完且客戶還有其他非技術問題 → 呼叫 transfer_to_receptionist 工具\n\n"
        "【重要】處理完技術問題後，若客戶同一則訊息還提到退貨、退款等帳務需求，\n"
        "必須主動呼叫 transfer_to_billing 工具轉接，不要只用文字告知客戶『我幫你轉接』。"
    ),
    name="tech_support",
)

# 帳務 Agent
billing = create_agent(
    model,
    tools=[
        process_refund,
        lookup_order,
        create_handoff_tool(
            agent_name="receptionist",
            description="轉回接待員，當帳務問題已處理完畢或客戶有其他問題時使用。",
        ),
        create_handoff_tool(
            agent_name="tech_support",
            description="轉接到技術支援，當客戶需要技術協助時使用。",
        ),
    ],
    system_prompt=(
        "你是帳務專員小華。\n\n"
        "【職責】\n"
        "- 處理退款申請（呼叫 process_refund 工具）\n"
        "- 查詢訂單狀態（呼叫 lookup_order 工具）\n"
        "- 解答帳單與付款相關問題\n\n"
        "【轉接規則】\n"
        "- 客戶有技術問題 → 呼叫 transfer_to_tech_support 工具\n"
        "- 處理完畢且客戶還有其他問題 → 呼叫 transfer_to_receptionist 工具\n\n"
        "【重要】需要退款時，若客戶沒提供訂單編號，可以使用預設範例 ORD-002 示範流程。"
    ),
    name="billing",
)

# === 組裝 Swarm ===

workflow = create_swarm(
    [receptionist, tech_support, billing],
    default_active_agent="receptionist",  # 預設由接待員開始
)

# 編譯時加入 checkpointer，讓系統記得「目前是誰在服務」
checkpointer = InMemorySaver()
app = workflow.compile(checkpointer=checkpointer)

# === 輸出工具：漂亮地呈現 Swarm 的接力流程 ===

def extract_text(content) -> str:
    """處理 Gemini 可能回傳 list[dict] 格式的內容。"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(item.get("text", ""))
        return "".join(parts)
    return str(content)

def print_new_messages(result: dict, prev_count: int, round_name: str) -> int:
    """只列印本輪新增的訊息，清楚標示誰在說話、呼叫了什麼工具。"""
    print(f"\n{'=' * 60}")
    print(f"  {round_name}")
    print('=' * 60)

    new_messages = result["messages"][prev_count:]

    for msg in new_messages:
        msg_type = type(msg).__name__

        if msg_type == "HumanMessage":
            print(f"\n👤 [用戶]")
            print(f"   {msg.content}")

        elif msg_type == "AIMessage":
            # Swarm 會在 AIMessage 的 name 欄位標記是哪個 Agent 產生的
            speaker = getattr(msg, "name", None) or "Agent"

            # 顯示文字回應（如果有）
            content_text = extract_text(msg.content)
            if content_text.strip():
                print(f"\n🤖 [{speaker}]")
                print(f"   {content_text}")

            # 顯示工具呼叫（這是 handoff 實際發生的證據）
            tool_calls = getattr(msg, "tool_calls", None) or []
            for tc in tool_calls:
                tool_name = tc.get("name", "unknown")
                tool_args = tc.get("args", {})
                print(f"   🔧 呼叫工具: {tool_name}({tool_args})")

        elif msg_type == "ToolMessage":
            tool_name = getattr(msg, "name", "tool")
            content = str(msg.content)
            if len(content) > 200:
                content = content[:200] + "..."
            print(f"   📋 [{tool_name} 回傳] {content}")

    return len(result["messages"])

def print_active_agent(config):
    """顯示目前接手對話的 Agent，用來驗證 Swarm 的狀態記憶。"""
    state = app.get_state(config)
    active = state.values.get("active_agent", "unknown")
    print(f"\n{'─' * 60}")
    print(f"  📍 目前接手的 Agent：{active}")
    print('─' * 60)

# === 模擬多輪對話 ===

def main():
    config = {"configurable": {"thread_id": "customer-session-001"}}
    prev_count = 0

    # 第一輪：客戶反應技術問題 → 預期會從 receptionist 接力到 tech_support
    result = app.invoke(
        {"messages": [{"role": "user", "content": "你好，我的藍牙耳機連不上手機，怎麼辦？"}]},
        config,
    )
    prev_count = print_new_messages(result, prev_count, "第一輪對話：技術問題求助")
    print_active_agent(config)

    # 第二輪：同時問規格 + 退貨 → 預期 tech_support 回規格後接力到 billing
    result = app.invoke(
        {"messages": [{"role": "user", "content": "那請問這個耳機的規格是什麼？還有，我想退貨。"}]},
        config,
    )
    prev_count = print_new_messages(result, prev_count, "第二輪對話：跨部門接力")
    print_active_agent(config)

if __name__ == "__main__":
    main()
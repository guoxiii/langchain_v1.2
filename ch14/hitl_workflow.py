# 檔案名稱：hitl_workflow.py

from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command
from langchain.chat_models import init_chat_model

# 定義狀態
class ContentState(TypedDict):
    topic: str
    draft: str
    feedback: str
    status: str  # "drafting", "reviewing", "published", "rejected"

# 初始化模型
llm = init_chat_model("google_genai:gemini-2.5-flash")

# 節點 1：AI 產生草稿
def generate_draft(state: ContentState) -> dict:
    topic = state["topic"]
    feedback = state.get("feedback", "")    

    if feedback:
        prompt = f"請根據以下主題撰寫一篇短文：{topic}\n\n請參考這些修改意見：{feedback}"
    else:
        prompt = f"請根據以下主題撰寫一篇短文（約 100 字）：{topic}"    

    response = llm.invoke(prompt)
    draft = response.content

    print(f"📝 AI 草稿已產生：\n{draft[:100]}...")
    return {"draft": draft, "status": "reviewing"}

# 節點 2：人工審核
def human_review(state: ContentState) -> dict:
    # 用 interrupt 暫停，等待人類審核
    review_result = interrupt({
        "message": "請審核以下草稿",
        "draft": state["draft"],
        "options": ["approve", "edit", "reject"],
        "instruction": "回覆格式：{'decision': 'approve/edit/reject', 'feedback': '修改意見（如果是 edit）'}"
    })
   

    # review_result 預期是一個 dict，包含 decision 和 feedback
    decision = review_result.get("decision", "reject")
    feedback = review_result.get("feedback", "")    

    print(f"👤 人類決策：{decision}")

    if feedback:
        print(f"💬 修改意見：{feedback}")    

    return {
        "status": decision,  # "approve", "edit", 或 "reject"
        "feedback": feedback
    }

# 節點 3：發布內容
def publish_content(state: ContentState) -> dict:
    print(f"🎉 內容已發布！")
    return {"status": "published"}

# 節點 4：拒絕處理
def handle_rejection(state: ContentState) -> dict:
    print(f"🚫 內容已被拒絕")
    return {"status": "rejected"}

# 路由函式：根據審核結果決定下一步
def route_after_review(state: ContentState) -> str:
    status = state["status"]

    if status == "approve":
        return "publish"
    elif status == "edit":
        return "regenerate"  # 帶著修改意見回去重新產生
    else:
        return "reject"

# 建立圖
graph = StateGraph(ContentState)
graph.add_node("generate_draft", generate_draft)
graph.add_node("human_review", human_review)
graph.add_node("publish_content", publish_content)
graph.add_node("handle_rejection", handle_rejection)
graph.add_edge(START, "generate_draft")
graph.add_edge("generate_draft", "human_review")

# 條件路由：根據人類決策走不同路線
graph.add_conditional_edges(
    "human_review",
    route_after_review,
    {
        "publish": "publish_content",
        "regenerate": "generate_draft",   # 回到產生草稿（帶修改意見）
        "reject": "handle_rejection"
    }
)

graph.add_edge("publish_content", END)
graph.add_edge("handle_rejection", END)

# 編譯
checkpointer = InMemorySaver()
app = graph.compile(checkpointer=checkpointer)

# --- 執行範例 ---
config = {"configurable": {"thread_id": "content-review-1"}}

# 第一次呼叫：產生草稿後在 human_review 暫停
print("=" * 50)
print("🚀 啟動內容產生流程...")

result = app.invoke(
    {
        "topic": "Python 非同步程式設計入門",
        "draft": "",
        "feedback": "",
        "status": "drafting"
    },
    config=config
)

print(f"\n⏸️  圖已暫停，等待人類審核...")
print(f"當前狀態：{result}")

# 接下來，人類可以用 Command 來回應：

# --- 場景 A：核准 ---
print("\n" + "=" * 50)
print("👤 人類決定：核准！")

result = app.invoke(
    Command(resume={"decision": "approve", "feedback": ""}),
    config=config
)

print(f"最終結果：{result}")

# --- 場景 B：要求修改（假設重新開一個 thread）---
config_edit = {"configurable": {"thread_id": "content-review-2"}}

# 先產生草稿
result = app.invoke(
    {
        "topic": "Python 非同步程式設計入門",
        "draft": "",
        "feedback": "",
        "status": "drafting"
    },
    config=config_edit
)

# 人類要求修改
print("\n👤 人類決定：需要修改！")
result = app.invoke(
    Command(resume={
        "decision": "edit",
        "feedback": "請加入 asyncio 的實際範例，並減少理論部分"
    }),
    config=config_edit
)

# 此時 AI 會帶著修改意見重新產生草稿
# 然後再次暫停在 human_review，等待第二次審核
print(f"⏸️  AI 已重新產生草稿，等待再次審核...")

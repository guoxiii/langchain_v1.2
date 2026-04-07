# ch17/annotations.py

"""使用 LangSmith SDK 為 Run 新增 Feedback"""

from dotenv import load_dotenv
from langsmith import Client
from langchain.chat_models import init_chat_model

load_dotenv()

client = Client()
llm = init_chat_model("google_genai:gemini-2.5-flash")

# 執行一個 LLM 呼叫
response = llm.invoke("請推薦三本適合 Python 初學者的書籍")
print(response.content)

# 從最近的 Trace 中取得 Run ID
# 方法一：從 response 的 metadata 中取得
run_id = response.response_metadata.get("run_id")

# 方法二：查詢最近的 Run
runs = list(
    client.list_runs(
        project_name="my-langchain-book",
        run_type="llm",
        limit=1,
    )
)

if runs:
    latest_run = runs[0]
    print(f"最近的 Run ID: {latest_run.id}")

    # 為這個 Run 新增 Feedback
    client.create_feedback(
        run_id=latest_run.id,
        key="correctness",       # 評分維度
        score=1.0,               # 分數（0.0 到 1.0）
        comment="推薦的書籍都很適合初學者",  # 文字評語
    )

    print("✅ Feedback 已新增")

    # 也可以用簡單的 👍/👎
    client.create_feedback(
        run_id=latest_run.id,
        key="user_satisfaction",
        score=1.0,  # 1.0 = 👍, 0.0 = 👎
    )

    print("✅ 使用者滿意度 Feedback 已新增")

# ch17/trace_metadata.py

"""為 Trace 加上 Metadata 和 Tags"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

llm = init_chat_model("google_genai:gemini-2.5-flash")

# 使用 config 參數加上 metadata 和 tags
response = llm.invoke(
    "什麼是 RAG？",
    config={
        "metadata": {
            "user_id": "user_123",
            "session_id": "session_abc",
            "environment": "development",
        },
        "tags": ["rag-question", "chapter-17", "demo"],
    },
)

print(response.text)

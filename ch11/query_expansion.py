# 檔案名稱：query_expansion.py
# 功能：將一個查詢擴展成多個子查詢

from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = init_chat_model("google_genai:gemini-2.5-flash")

expansion_prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一位查詢擴展專家。給定一個使用者問題，請生成 3 個不同角度的子查詢，用來從向量資料庫中檢索相關文件。

規則：
1. 每個子查詢從不同的角度探索同一個主題
2. 使用不同的關鍵字和表達方式
3. 每行一個查詢，不要編號，不要加解釋"""),
    ("human", "原始查詢：{query}")
])

expansion_chain = expansion_prompt | llm | StrOutputParser()

# 測試
original_query = "LangChain 的 Agent 怎麼處理錯誤？"
expanded = expansion_chain.invoke({"query": original_query})

print(f"原始查詢：{original_query}")
print(f"擴展查詢：\n{expanded}")

# 可能的輸出：
# LangChain Agent 錯誤處理機制與重試策略
# create_agent 工具呼叫失敗時的 handle_tool_error 設定
# LangChain Middleware ModelRetryMiddleware 指數退避實作

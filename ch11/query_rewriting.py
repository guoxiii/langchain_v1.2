# 檔案名稱：query_rewriting.py
# 功能：使用 LLM 改寫使用者查詢，提升檢索品質
from dotenv import load_dotenv

load_dotenv()

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 初始化 LLM
llm = init_chat_model("google_genai:gemini-2.5-flash")

# 查詢改寫 Prompt
rewrite_prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一位查詢改寫專家。你的任務是將使用者的問題改寫成更適合語意搜尋的版本。
改寫規則：
1. 保留原始意圖，但使用更精確的詞彙
2. 展開縮寫和口語表達
3. 補充可能的同義詞或相關術語
4. 輸出一個改寫後的查詢字串，不要加任何解釋"""),
    ("human", "原始查詢：{query}")
])

# 建立改寫鏈
rewrite_chain = rewrite_prompt | llm | StrOutputParser()

# 測試
original_query = "特休怎麼算？"
rewritten = rewrite_chain.invoke({"query": original_query})

print(f"原始查詢：{original_query}")
print(f"改寫查詢：{rewritten}")

# 可能的輸出：「員工特別休假天數計算方式與年資對應規定」

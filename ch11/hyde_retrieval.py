# 檔案名稱：hyde_retrieval.py
# 功能：使用 HyDE 策略提升檢索品質

import re
import time

from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document

# === 1. 準備測試資料 ===
documents = [
    Document(
        page_content="""員工特別休假管理辦法
第一條：員工到職滿六個月，即享有三天特別休假。
第二條：到職滿一年者，享有七天特別休假。
第三條：到職滿二年以上者，每增加一年加給一天，最多至十四天。
第四條：到職滿五年以上者，每增加一年加給一天，最多至三十天。
特別休假未休完者，可折算工資。""",
        metadata={"source": "公司規章.pdf", "page": 15}
    ),
    Document(
        page_content="""加班費計算規則
一般工作日加班：前兩小時按時薪 1.34 倍，之後按 1.67 倍。
休息日加班：前兩小時按時薪 1.34 倍，之後按 1.67 倍。
國定假日加班：按時薪 2 倍計算。
每月加班上限為 46 小時。""",
        metadata={"source": "公司規章.pdf", "page": 20}
    ),
    Document(
        page_content="""員工績效考核制度
績效等級分為 A（傑出）、B（優良）、C（合格）、D（待改善）。
年度績效考核結果將影響調薪幅度及年終獎金。
考核週期為每年一月至十二月。""",
        metadata={"source": "公司規章.pdf", "page": 25}
    ),
]

# === 2. 建立 Vector Store ===
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vectorstore = InMemoryVectorStore.from_documents(documents, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

# === 3. 建立 HyDE 生成器 ===
llm = init_chat_model("google_genai:gemini-2.5-flash")

hyde_prompt = ChatPromptTemplate.from_messages([
    ("system", """你是一位企業人資專家。請根據使用者的問題，撰寫一段假設性的回答。
這段回答不需要完全正確，但要使用與真實文件相似的措辭和用語風格。
直接輸出假設性回答，不要加任何前言或解釋。"""),
    ("human", "{query}")
])

hyde_chain = hyde_prompt | llm | StrOutputParser()

# === 4. 比較 Naive vs HyDE ===
query = "特休怎麼算？"

# 方法 A：Naive — 直接用問句搜尋
print("=== Naive RAG ===")
naive_results = retriever.invoke(query)

for doc in naive_results:
    print(f"  來源：{doc.metadata.get('source')}，頁碼：{doc.metadata.get('page')}")
    print(f"  內容：{doc.page_content[:80]}...")
    print()

# 避免連續呼叫 Embedding API 觸發 rate limit
time.sleep(2)

# 方法 B：HyDE — 先生成假答案，再用假答案搜尋
print("=== HyDE RAG ===")

hypothetical_answer = hyde_chain.invoke({"query": query})

# 移除 Markdown 格式符號，避免特殊字元干擾 Embedding API
hypothetical_answer = re.sub(r'\*{1,2}|#{1,3}\s?', '', hypothetical_answer)

# 截斷過長的假設性回答
if len(hypothetical_answer) > 500:
    hypothetical_answer = hypothetical_answer[:500]

print(f"假設性回答：{hypothetical_answer[:100]}...")
print()

hyde_results = retriever.invoke(hypothetical_answer)

for doc in hyde_results:
    print(f"  來源：{doc.metadata.get('source')}，頁碼：{doc.metadata.get('page')}")
    print(f"  內容：{doc.page_content[:80]}...")
    print()
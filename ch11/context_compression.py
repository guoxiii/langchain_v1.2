# 檔案名稱：context_compression.py
# 功能：使用 ContextualCompressionRetriever 壓縮檢索結果
from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_classic.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import LLMChainExtractor

# === 1. 準備測試資料（chunk 內容較長，混合相關與不相關資訊）===
documents = [
    Document(page_content="""員工福利制度總覽
本公司提供多樣化的員工福利，包括健康保險、年度健康檢查、生日禮金、
結婚禮金、喪葬補助等。每位員工入職滿三個月即可享有完整福利。

關於特別休假：員工到職滿六個月即享有三天特別休假。到職滿一年者享有
七天特別休假。到職滿二年以上者，每增加一年加給一天。特別休假未休完
者可折算工資，以前一年度平均薪資計算。

另外，本公司設有員工餐廳，提供午餐補助每人每日 80 元。員工停車場
位於 B1 及 B2 樓層，需向總務部申請停車證。"""),
]

# === 2. 建立基礎 Retriever ===
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vectorstore = InMemoryVectorStore.from_documents(documents, embeddings)
base_retriever = vectorstore.as_retriever(search_kwargs={"k": 1})

# === 3. 建立壓縮器 ===
llm = init_chat_model("google_genai:gemini-2.5-flash")
compressor = LLMChainExtractor.from_llm(llm)

compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=base_retriever
)

# === 4. 搜尋 ===
query = "特休有幾天？"

# 比較：不壓縮 vs 壓縮
print("=== 不壓縮（原始 chunk）===")
raw_results = base_retriever.invoke(query)

for doc in raw_results:
    print(f"  長度：{len(doc.page_content)} 字")
    print(f"  {doc.page_content}")

print("\n=== 壓縮後 ===")
compressed_results = compression_retriever.invoke(query)

for doc in compressed_results:
    print(f"  長度：{len(doc.page_content)} 字")
    print(f"  {doc.page_content}")

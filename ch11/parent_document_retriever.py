# 檔案名稱：parent_document_retriever.py
# 功能：使用 ParentDocumentRetriever 實現小 chunk 搜尋、大 chunk 回傳

from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
from langchain_classic.retrievers.parent_document_retriever import ParentDocumentRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.storage import InMemoryStore

# === 1. 準備一份比較長的測試文件 ===
long_document = Document(
    page_content="""第一章：Python 基礎語法
Python 是一種高階程式語言，由 Guido van Rossum 於 1991 年發布。Python 的設計哲學強調程式碼的可讀性和簡潔性，使用縮排來表示程式碼區塊，而非大括號。
1.1 變數與資料型態
Python 是動態型別語言，不需要事先宣告變數型別。常見的資料型態包括整數（int）、浮點數（float）、字串（str）和布林值（bool）。Python 3 中，整數沒有大小限制，可以處理任意精度的數字。
字串在 Python 中是不可變的序列。你可以使用單引號或雙引號來定義字串。Python 提供了豐富的字串方法，如 split()、join()、strip()、replace() 等。f-string 是 Python 3.6 引入的字串格式化語法，是目前推薦的格式化方式。

1.2 控制流程
Python 支援 if-elif-else 條件判斷、for 迴圈和 while 迴圈。for 迴圈通常搭配 range() 函式或直接迭代可迭代物件使用。Python 的迴圈還支援 else 子句，當迴圈正常結束（沒有被 break 中斷）時執行。
列表推導式（List Comprehension）是 Python 的特色語法，可以用一行程式碼建立列表。類似的還有字典推導式、集合推導式和生成器表達式。

1.3 函式
def 關鍵字用來定義函式。Python 支援預設參數、關鍵字引數、*args 和 **kwargs。函式是一等公民（first-class citizen），可以作為參數傳遞、作為回傳值、或存在變數中。
裝飾器（decorator）是 Python 的進階功能，本質上是一個接受函式作為參數並回傳新函式的高階函式。使用 @decorator_name 語法糖可以簡潔地套用裝飾器。

1.4 類別與物件
Python 支援物件導向程式設計。class 關鍵字用來定義類別。Python 支援繼承（包括多重繼承）、封裝和多型。__init__ 方法是建構子，self 參數指向實例本身。
Python 使用 MRO（Method Resolution Order）來解決多重繼承的方法查找順序。super() 函式用來呼叫父類別的方法。""",
    metadata={"source": "python_tutorial.pdf", "chapter": 1}
)

# === 2. 設定 Parent 和 Child 的切割器 ===
# Parent chunk：較大（800 字），用來回傳

parent_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    separators=["\n\n", "\n", "。", "，", " "]
)

# Child chunk：較小（200 字），用來搜尋
child_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", "，", " "]
)

# === 3. 建立 ParentDocumentRetriever ===
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
vectorstore = InMemoryVectorStore(embeddings)
docstore = InMemoryStore()

retriever = ParentDocumentRetriever(
    vectorstore=vectorstore,
    docstore=docstore,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)

# 新增文件（會自動切割並建立 parent-child 關係）
retriever.add_documents([long_document])

# === 4. 搜尋測試 ===
query = "Python 的 decorator 是什麼？"
results = retriever.invoke(query)

print(f"查詢：{query}")
print(f"找到 {len(results)} 個 Parent 文件：\n")

for i, doc in enumerate(results, 1):
    print(f"--- Parent Document {i} ---")
    print(f"長度：{len(doc.page_content)} 字")
    print(f"內容：{doc.page_content[:200]}...")
    print()

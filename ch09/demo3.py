# demo3.py
import os
from dotenv import load_dotenv
from langchain_experimental.text_splitter import SemanticChunker
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

# 建立 Embedding 模型
embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)

# 建立語義分割器
semantic_splitter = SemanticChunker(
    embeddings=embeddings,
    breakpoint_threshold_type="percentile",  # 使用百分位數判斷語義斷點
)

text = """
人工智慧的發展歷史可以追溯到 1956 年的達特茅斯會議，在那次會議上，學者們首次提出了人工智慧這個概念，接下來的幾十年裡，AI 經歷了多次繁榮與寒冬。

機器學習是人工智慧的一個子領域，它的核心思想是讓機器從數據中自動學習規律，而不是由人類明確地編寫每一條規則。

監督式學習、非監督式學習和強化學習是三種主要的學習範式。

深度學習則是機器學習中的一個分支，它使用多層神經網路來學習數據的階層式表示。

卷積神經網路（CNN）擅長處理圖片，遞迴神經網路（RNN）擅長處理序列資料，
如今，大型語言模型代表了 AI 的最新突破。

Transformer 架構的發明是一切的起點，它讓模型能夠同時關注輸入序列中的所有位置。
"""

# 語義分割
semantic_chunks = semantic_splitter.create_documents([text])

for i, chunk in enumerate(semantic_chunks):
    print(f"--- 語義 Chunk {i+1} ---")
    print(chunk.page_content)
    print()

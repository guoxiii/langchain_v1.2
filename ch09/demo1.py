# demo1.py
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 建立分割器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,       # 每個 chunk 最多 500 個字元
    chunk_overlap=100,    # 相鄰 chunk 之間重疊 100 個字元
    length_function=len,  # 用 Python 內建 len() 計算長度
    is_separator_regex=False,  # 分隔符不是正則表達式
)

# 假設我們有一段文字
text = """
人工智慧（Artificial Intelligence, AI）是計算機科學的一個分支，它企圖了解智慧的本質，並生產出一種新的能以人類智慧相似的方式做出反應的智能機器。

人工智慧的研究範圍包括自然語言處理、電腦視覺、機器學習、專家系統等。
自從被提出以來，AI 技術經歷了多次發展浪潮。

最近幾年，隨著深度學習和大型語言模型的突破，AI 已經從實驗室走進了我們的日常生活。

從語音助理到自動駕駛，從醫療診斷到金融分析，AI 的應用場景越來越廣泛。

大型語言模型（Large Language Model, LLM）是近年來 AI 領域最令人興奮的進展之一。

以 GPT、Gemini、Claude 為代表的 LLM，展現了驚人的語言理解和生成能力。
"""

# 切割文字
chunks = text_splitter.split_text(text)

for i, chunk in enumerate(chunks):
    print(f"--- Chunk {i+1} ({len(chunk)} 字元) ---")
    print(chunk)
    print()

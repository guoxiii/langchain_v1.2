# demo4.py
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 載入你的文件
sample_text = open("./documents/readme.txt", "r", encoding="utf-8").read()

# 嘗試不同的參數組合
configs = [
    {"chunk_size": 300, "chunk_overlap": 50},
    {"chunk_size": 500, "chunk_overlap": 100},
    {"chunk_size": 1000, "chunk_overlap": 200},
    {"chunk_size": 1500, "chunk_overlap": 300},
]

for config in configs:
    splitter = RecursiveCharacterTextSplitter(**config)
    chunks = splitter.split_text(sample_text)
    avg_len = sum(len(c) for c in chunks) / len(chunks) if chunks else 0    

    print(f"chunk_size={config['chunk_size']}, "
          f"overlap={config['chunk_overlap']}: "
          f"共 {len(chunks)} 個 chunk, "
          f"平均 {avg_len:.0f} 字元")
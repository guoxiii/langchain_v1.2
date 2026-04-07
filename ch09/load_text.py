# load_text.py
from langchain_community.document_loaders import TextLoader
loader = TextLoader("./documents/readme.txt", encoding="utf-8")
docs = loader.load()

print(f"內容長度：{len(docs[0].page_content)} 字元")

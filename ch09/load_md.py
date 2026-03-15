# load_md.py
from langchain_community.document_loaders import UnstructuredMarkdownLoader
loader = UnstructuredMarkdownLoader("./documents/api_guide.md")
docs = loader.load()

print(docs[0].page_content[:300])

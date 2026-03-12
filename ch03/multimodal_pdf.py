# ch03/multimodal_pdf.py

"""
示範傳送 PDF 給模型
"""

import base64
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage

load_dotenv()

model = init_chat_model("google_genai:gemini-2.5-flash")

def encode_pdf(pdf_path: str) -> str:
    """將 PDF 檔案轉換為 Base64 字串"""
    with open(pdf_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# 假設有一個本地 PDF
pdf_path = "report.pdf"
base64_pdf = encode_pdf(pdf_path)

message = HumanMessage(
    content=[
        {
            "type": "media",
            "mime_type": "application/pdf",
            "data": base64_pdf,
        },
        {
            "type": "text",
            "text": "請摘要這份 PDF 文件的主要內容。"
        },
    ]
)

response = model.invoke([message])
print(response.content)
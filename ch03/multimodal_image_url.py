# ch03/multimodal_image_url.py

"""
示範傳送圖片 URL 給模型
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage

load_dotenv()

# Gemini 和 Claude 都支援圖片輸入
model = init_chat_model("google_genai:gemini-2.5-flash")

# 使用內容區塊列表傳送圖片 + 文字
message = HumanMessage(
    content=[
        {
            "type": "image_url",
            "image_url": {
                "url": "https://picsum.photos/id/237/200/300"
            },
        },
        {
            "type": "text",
            "text": "請描述這張圖片的內容。"
        },
    ]
)

response = model.invoke([message])
print(response.content)

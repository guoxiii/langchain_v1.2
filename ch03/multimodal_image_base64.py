# ch03/multimodal_image_base64.py

"""
示範傳送本地圖片給模型（Base64 編碼）
"""
import base64
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage

load_dotenv()

model = init_chat_model("google_genai:gemini-2.5-flash")

def encode_image(image_path: str) -> str:
    """將本地圖片轉換為 Base64 字串"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# 假設有一張本地圖片
image_path = "images/01.jpg"
base64_image = encode_image(image_path)

message = HumanMessage(
    content=[
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            },
        },
        {
            "type": "text",
            "text": "這張圖片裡有什麼？"
        },
    ]
)

response = model.invoke([message])
print(response.content)

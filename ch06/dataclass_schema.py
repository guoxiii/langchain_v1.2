# ch06/dataclass_schema.py

"""使用 dataclass 定義 Schema"""
from dotenv import load_dotenv
from dataclasses import dataclass, asdict
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

load_dotenv()

@dataclass
class BookInfo:
    """書籍資訊"""
    title: str        # 書名
    author: str       # 作者
    year: int         # 出版年份
    genre: str        # 類型

agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    response_format=ToolStrategy(BookInfo),
)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "《百年孤寂》是馬奎斯在 1967 年寫的魔幻現實主義小說"
    }]
})

# dataclass 回傳的是 dataclass 實例（不是 dict）
book = result["structured_response"]

print(book)
# BookInfo(title='百年孤寂', author='馬奎斯', year=1967, genre='魔幻現實主義')

# 若需要轉成 dict，可使用 asdict()
print(asdict(book))
# {'title': '百年孤寂', 'author': '馬奎斯', 'year': 1967, 'genre': '魔幻現實主義'}
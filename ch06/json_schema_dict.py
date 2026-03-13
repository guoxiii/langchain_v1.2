# ch06/json_schema_dict.py

"""使用 JSON Schema 字典定義 Schema"""
import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

load_dotenv()

# 直接使用 JSON Schema 字典
event_schema = {
    "title": "EventInfo",
    "description": "活動資訊",
    "type": "object",
    "properties": {
        "event_name": {
            "type": "string",
            "description": "活動名稱"
        },
        "date": {
            "type": "string",
            "description": "活動日期（YYYY-MM-DD 格式）"
        },
        "attendees": {
            "type": "integer",
            "description": "預估參加人數"
        }
    },
    "required": ["event_name", "date", "attendees"]
}

agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    response_format=ToolStrategy(event_schema),
)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": "LangChain Meetup 台北場，2026年4月20日，預計 50 人參加"
    }]
})

event = result["structured_response"]

print(event)
# {'event_name': 'LangChain Meetup 台北場', 'date': '2026-04-20', 'attendees': 50}

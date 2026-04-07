# 檔案：ch05/language_enforcer.py
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import (
    AgentMiddleware,
    ModelRequest,
    ModelResponse,
)
from langchain.messages import SystemMessage
from typing import Callable

load_dotenv()

class LanguageEnforcerMiddleware(AgentMiddleware):
    """
    強制 Agent 使用指定語言回覆
    透過 wrap_model_call 在每次模型請求中注入語言指示
    """

    def __init__(self, language: str = "繁體中文"):
        super().__init__()
        self.language = language

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """包裝模型呼叫，在 system message 中加入語言限制"""
        language_instruction = (
            f"你必須使用{self.language}回覆所有問題。"
            f"無論使用者用什麼語言提問，你都只能用{self.language}回答。"
        )

        # 如果已有 system message，附加語言指示；否則建立新的
        if request.system_message is not None:
            new_content = list(request.system_message.content_blocks) + [
                {"type": "text", "text": language_instruction}
            ]
        else:
            new_content = language_instruction

        new_system_message = SystemMessage(content=new_content)

        # 用 override 產生新的 request，不直接修改原物件
        return handler(request.override(system_message=new_system_message))

agent = create_agent(
    model="google_genai:gemini-2.5-flash",
    tools=[],
    middleware=[LanguageEnforcerMiddleware(language="繁體中文")],
)

# 即使用英文提問，Agent 也會用繁體中文回覆
result = agent.invoke(
    {"messages": [{"role": "user", "content": "What is machine learning?"}]}
)
print(result["messages"][-1].content)
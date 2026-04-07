"""
多語言支援 Middleware
自動偵測使用者語言並切換回應語言
"""

from dotenv import load_dotenv
load_dotenv()

from langchain.agents.middleware import AgentMiddleware
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage

class MergeableChat(ChatAnthropic):
    """自動合併多條 SystemMessage，解決 Anthropic API 限制。"""

    def _merge_system_messages(self, messages):
        """將多條 SystemMessage 合併為一條。"""
        system_parts, others = [], []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                system_parts.append(msg.content)
            else:
                others.append(msg)
        if system_parts:
            return [SystemMessage(content="\n\n".join(system_parts))] + others
        return messages

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        messages = self._merge_system_messages(messages)
        return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        messages = self._merge_system_messages(messages)
        return await super()._agenerate(messages, stop=stop, run_manager=run_manager, **kwargs)


class MultilingualMiddleware(AgentMiddleware):
    """
    多語言自動切換 Middleware。    

    工作原理：
    1. 在 before_model Hook 中，分析使用者最新訊息的語言
    2. 根據偵測到的語言，動態注入語言指示到 System Prompt
    3. Agent 就會自動用對應的語言回覆    

    這比在 System Prompt 寫死「請用中文回覆」聰明多了 —
    因為同一個 Agent 可以同時服務中文和英文顧客。
    """
    def __init__(self, default_language: str = "zh-TW"):
        self.default_language = default_language
        self.language_instructions = {
            "zh-TW": "請用繁體中文回覆。使用台灣慣用的用語（例如：「資料」而非「数据」，「軟體」而非「软件」）。",
            "en": "Please respond in English. Use a friendly and professional tone.",
            "ja": "日本語でお返事ください。丁寧な言葉遣いでお願いします。",
        }

    def _detect_language(self, text: str) -> str:
        """
        簡易語言偵測。
        生產環境中可以使用更精確的偵測庫（如 langdetect），
        或直接用 LLM 偵測。這裡用簡單的字元分析示範概念。
        """
        cjk_count = sum(
            1 for c in text if "\u4e00" <= c <= "\u9fff"
        )
        ascii_count = sum(
            1 for c in text if c.isascii() and c.isalpha()
        )
        japanese_count = sum(
            1 for c in text
            if "\u3040" <= c <= "\u309f"  # Hiragana
            or "\u30a0" <= c <= "\u30ff"  # Katakana
        )

        total = max(cjk_count + ascii_count + japanese_count, 1)

        if japanese_count / total > 0.1:
            return "ja"
        elif cjk_count / total > 0.3:
            return "zh-TW"
        elif ascii_count / total > 0.5:
            return "en"
        return self.default_language

    def before_model(self, state, config):
        """
        在模型呼叫前，偵測語言並注入語言指示。
        """
        messages = state.get("messages", [])

        if not messages:
            return state

        # 取得最新的使用者訊息
        last_user_msg = None

        for msg in reversed(messages):
            if hasattr(msg, "type") and msg.type == "human":
                last_user_msg = msg.content
                break
            elif isinstance(msg, dict) and msg.get("role") == "user":
                last_user_msg = msg.get("content", "")
                break

        if not last_user_msg:
            return state

        # 偵測語言
        detected_lang = self._detect_language(last_user_msg)

        instruction = self.language_instructions.get(
            detected_lang,
            self.language_instructions[self.default_language],
        )

        # 注入語言指示作為額外的系統訊息
        language_msg = SystemMessage(
            content=f"[語言指示] {instruction}"
        )

        updated_messages = list(messages)

        # 找到第一個非系統訊息的位置，插入語言指示
        insert_idx = 0

        for i, msg in enumerate(updated_messages):
            if hasattr(msg, "type") and msg.type == "system":
                insert_idx = i + 1
            elif isinstance(msg, dict) and msg.get("role") == "system":
                insert_idx = i + 1
            else:
                break

        updated_messages.insert(insert_idx, language_msg)
        return {**state, "messages": updated_messages}
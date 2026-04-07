# ch08/production_tools.py
"""
生產級 API 整合工具範例
使用 @tool 和 BaseTool 混合開發，包含完整的錯誤處理
"""

from dotenv import load_dotenv
load_dotenv()

import asyncio
from datetime import datetime
from typing import Type
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.tools import BaseTool, ToolException
from pydantic import BaseModel, Field
from typing import Literal

# ============================================================
# 工具一：@tool — 取得目前時間（簡單工具用 @tool）
# ============================================================

@tool
def get_current_datetime() -> str:
    """取得目前的日期與時間，格式為 YYYY-MM-DD HH:MM:SS。
    當需要知道現在的時間或日期時使用。"""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

# ============================================================
# 工具二：BaseTool — 新聞搜尋工具（需要配置和錯誤處理）
# ============================================================
class NewsSearchInput(BaseModel):
    """新聞搜尋的輸入參數。"""
    keyword: str = Field(
        description="搜尋關鍵字，例如 'AI'、'台灣經濟'、'半導體'"
    )

    category: Literal["general", "technology", "business", "science", "health"] = Field(
        default="general",
        description="新聞分類：general=綜合、technology=科技、business=商業、science=科學、health=健康"
    )
    max_results: int = Field(
        default=3,
        description="回傳新聞數量上限（1-5）",
        ge=1,
        le=5
    )

class NewsSearchTool(BaseTool):
    """搜尋最新新聞文章。
    在使用者詢問近期事件、新聞、時事話題時使用此工具。
    不適用於查詢歷史事件或百科知識。
    """
    name: str = "search_news"

    description: str = (
        "搜尋最新的新聞文章。"
        "使用時機：使用者詢問近期新聞、時事或產業動態。"
        "不適用：歷史事件或一般知識問題。"
    )
    args_schema: Type[BaseModel] = NewsSearchInput
    handle_tool_error: bool = True  # 啟用錯誤處理

    # 模擬的新聞資料庫（實際中應呼叫新聞 API）
    _news_db: dict = {
        "AI": [
            {"title": "OpenAI 發布 GPT-5 模型", "summary": "新模型在推理能力上有顯著提升...", "source": "TechCrunch", "date": "2026-03-10"},
            {"title": "台灣 AI 產業產值突破兆元", "summary": "經濟部報告顯示 AI 相關產業快速成長...", "source": "經濟日報", "date": "2026-03-08"},
            {"title": "Google DeepMind 新突破", "summary": "在蛋白質結構預測領域取得重大進展...", "source": "Nature", "date": "2026-03-05"},
        ],
        "半導體": [
            {"title": "台積電 2 奈米製程量產", "summary": "台積電宣布 2 奈米製程正式進入量產階段...", "source": "工商時報", "date": "2026-03-09"},
            {"title": "全球晶片需求持續成長", "summary": "AI 伺服器帶動先進製程需求...", "source": "Bloomberg", "date": "2026-03-07"},
        ],
    }

    def _run(
        self,
        keyword: str,
        category: str = "general",
        max_results: int = 3
    ) -> str:

        # 模擬搜尋（實際中應呼叫新聞 API）
        results = []

        for key, articles in self._news_db.items():
            if keyword.lower() in key.lower():
                results.extend(articles)
        if not results:
            raise ToolException(
                f"找不到關於「{keyword}」的新聞。"
                f"建議嘗試其他關鍵字，例如：AI、半導體。"
            )

        # 限制回傳數量
        results = results[:max_results]

        # 格式化輸出
        output_lines = [f"搜尋「{keyword}」找到 {len(results)} 則新聞：\n"]

        for i, article in enumerate(results, 1):
            output_lines.append(
                f"{i}. 【{article['source']}】{article['title']}\n"
                f"   日期：{article['date']}\n"
                f"   摘要：{article['summary']}\n"
            )

        return "\n".join(output_lines)


# ============================================================
# 工具三：@tool + Artifact — 產生新聞報表
# ============================================================

@tool(response_format="content_and_artifact")
def generate_news_report(topic: str, period: str = "本週") -> tuple:
    """根據指定主題產生新聞分析報表。
    回傳簡要摘要給對話，同時產生完整的報表資料。

    Args:
        topic: 報表主題，例如 'AI 產業動態' 或 '半導體市場'
        period: 報表期間，例如 '本週'、'本月'
    """

    # 模擬報表資料
    report_data = {
        "topic": topic,
        "period": period,
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_articles": 15,
            "positive_sentiment": 8,
            "neutral_sentiment": 5,
            "negative_sentiment": 2,
        },
        "key_trends": [
            "AI 應用加速落地，企業採用率提升 40%",
            "半導體先進製程競爭白熱化",
            "綠能與 AI 的交叉應用成為新熱點",
        ],
        "top_sources": ["TechCrunch", "Bloomberg", "經濟日報", "Nature"],
    }

    # content: 給 LLM 的簡要摘要
    content = (
        f"「{topic}」{period}新聞分析報表已產生：\n"
        f"- 共分析 {report_data['summary']['total_articles']} 篇文章\n"
        f"- 正面情緒：{report_data['summary']['positive_sentiment']} 篇\n"
        f"- 關鍵趨勢：{', '.join(report_data['key_trends'][:2])}\n"
        f"完整報表資料已附在 artifact 中。"
    )


    # artifact: 完整的報表資料
    return content, report_data

# ============================================================
# 組合：建立生產級 Agent
# ============================================================

async def main():
    model = init_chat_model("anthropic:claude-sonnet-4-6")

    agent = create_agent(
        model,
        tools=[
            get_current_datetime,       # @tool：簡單工具
            NewsSearchTool(),           # BaseTool：需要配置的工具
            generate_news_report,       # @tool + Artifact：報表工具
        ],

        system_prompt=(
            "你是一個專業的新聞分析助手。你可以：\n"
            "1. 搜尋最新新聞\n"
            "2. 產生新聞分析報表\n"
            "3. 告訴使用者目前的時間\n\n"
            "請用繁體中文回答，語氣專業但親切。"
        )
    )

    # 測試場景

    test_queries = [
        "幫我搜尋 AI 相關的最新新聞",
        "產生一份本週的 AI 產業動態報表",
        "搜尋關於量子計算的新聞",  # 這個會觸發 ToolException
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"使用者：{query}")
        print(f"{'='*60}")

        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": query}]}
        )

        # 印出最後一則 AI 回覆
        for msg in reversed(result["messages"]):
            if msg.type == "ai" and msg.content:
                print(f"助手：{msg.content}")
                break

asyncio.run(main())

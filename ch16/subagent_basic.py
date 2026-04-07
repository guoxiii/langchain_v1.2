# ch16/subagent_basic.py

from dotenv import load_dotenv
from deepagents import create_deep_agent

load_dotenv()


def web_search(query: str) -> str:
    """搜尋網路上的資訊(模擬資料)"""
    mock_db = {
        "rust": [
            "Actix-web 是目前效能最高的 Rust 後端框架,適合高吞吐量 API",
            "Axum 由 Tokio 官方維護,生態整合佳,是 2024 年企業專案首選",
            "Leptos 採用細粒度響應式架構,是 Rust 前端 WebAssembly 的代表框架",
            "Discord 將部分服務從 Go 改寫為 Rust 後,P99 延遲大幅降低",
            "Rust 學習曲線陡峭,工程師通常需要數個月才能熟練掌握",
        ],
        "python": [
            "FastAPI 是目前最熱門的 Python Web 框架",
            "Django 適合需要完整功能的企業級應用",
        ],
    }
    for key, results in mock_db.items():
        if key in query.lower():
            return "\n".join(f"- {r}" for r in results)
    return f"找不到關於 '{query}' 的資料"


# 研究員子 Agent:負責蒐集資料
researcher = {
    "name": "research-agent",
    "description": "負責搜尋和蒐集資訊。需要查找資料時委派給它。",
    "system_prompt": "你是技術研究員。請使用 web_search 工具蒐集資料,然後彙整回報。",
    "tools": [web_search],
}

# 寫作專家子 Agent:負責整理成報告
writer = {
    "name": "writer-agent",
    "description": "負責撰寫結構化的技術報告。需要整理成正式文件時委派給它。",
    "system_prompt": "你是技術寫作者。請將研究資料整理成繁體中文的 Markdown 報告,技術名詞保留英文。",
}

# 主 Agent:專案經理,負責規劃與委派
agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="你是專案經理。收到研究任務時,先委派 research-agent 蒐集資料,再委派 writer-agent 撰寫報告。",
    subagents=[researcher, writer],
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "請研究 Rust 在 Web 開發的應用,並寫一份簡短報告"}]
})

print(result["messages"][-1].text)
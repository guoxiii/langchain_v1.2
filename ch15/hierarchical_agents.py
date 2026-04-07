# 檔案名稱：hierarchical_agents.py

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool

load_dotenv()

model = init_chat_model("google_genai:gemini-2.5-flash")

# ============================================
# 第一層：建立各部門的 Worker Agent
# ============================================

# --- 研究部門 ---
@tool
def search_academic(query: str) -> str:
    """搜尋學術論文和期刊文章。"""
    return f"學術搜尋結果：找到 3 篇關於 '{query}' 的相關論文。"

@tool
def search_market(query: str) -> str:
    """搜尋市場報告和產業分析。"""
    return f"市場搜尋結果：'{query}' 的市場規模預估為 500 億美元。"

academic_researcher = create_agent(
    model,
    tools=[search_academic],
    system_prompt="你是學術研究員，專門搜尋和分析學術論文。請提供詳細的研究發現。",
    name="academic_researcher",
)

market_researcher = create_agent(
    model,
    tools=[search_market],
    system_prompt="你是市場研究員，專門分析市場趨勢和產業報告。請提供關鍵數據和趨勢。",
    name="market_researcher",
)

# --- 寫作部門 ---
@tool
def check_grammar(text: str) -> str:
    """檢查文字的文法和用詞。"""
    return f"文法檢查完成：文本品質良好，建議微調 2 處用詞。"

blog_writer = create_agent(
    model,
    tools=[],
    system_prompt="你是部落格寫手，擅長用輕鬆有趣的語氣撰寫科技文章。",
    name="blog_writer",
)

tech_writer = create_agent(
    model,
    tools=[check_grammar],
    system_prompt="你是技術文件作家，擅長撰寫結構嚴謹、精確的技術文檔。",
    name="tech_writer",
)

# ============================================
# 第二層：建立部門主管（中層 Supervisor）
# ============================================

# 研究部主管的工具
@tool("do_academic_research", description="進行學術研究，適合需要論文和理論依據的任務。")
def call_academic_researcher(topic: str) -> str:
    """派遣學術研究員進行研究。"""
    result = academic_researcher.invoke(
        {"messages": [{"role": "user", "content": topic}]}
    )

    return result["messages"][-1].content

@tool("do_market_research", description="進行市場研究，適合需要產業數據和趨勢分析的任務。")
def call_market_researcher(topic: str) -> str:
    """派遣市場研究員進行研究。"""
    result = market_researcher.invoke(
        {"messages": [{"role": "user", "content": topic}]}
    )

    return result["messages"][-1].content

# 研究部主管
research_supervisor = create_agent(
    model,
    tools=[call_academic_researcher, call_market_researcher],
    system_prompt=(
        "你是研究部門主管。根據任務需求，決定要派遣學術研究員還是市場研究員（或兩者都派）。"
        "整合所有研究結果後，提供一份完整的研究摘要。"
    ),
    name="research_supervisor",
)

# 寫作部主管的工具
@tool("write_blog_post", description="撰寫輕鬆有趣的部落格文章。")
def call_blog_writer(brief: str) -> str:
    """派遣部落格寫手撰寫文章。"""
    result = blog_writer.invoke(
        {"messages": [{"role": "user", "content": brief}]}
    )

    return result["messages"][-1].content

@tool("write_tech_doc", description="撰寫嚴謹精確的技術文件。")
def call_tech_writer(brief: str) -> str:
    """派遣技術文件作家撰寫文件。"""
    result = tech_writer.invoke(
        {"messages": [{"role": "user", "content": brief}]}
    )

    return result["messages"][-1].content
# 寫作部主管

writing_supervisor = create_agent(
    model,
    tools=[call_blog_writer, call_tech_writer],
    system_prompt=(
        "你是寫作部門主管。根據目標讀者和內容類型，決定派遣部落格寫手還是技術文件作家。"
        "確保產出的內容符合要求的風格和品質。"
    ),
    name="writing_supervisor",
)

# ============================================
# 第三層：建立總 Supervisor（CEO Agent）
# ============================================

@tool("research_department", description="將任務派給研究部門，進行學術或市場研究。")
def call_research_dept(task_description: str) -> str:
    """派遣研究部門處理研究任務。"""
    result = research_supervisor.invoke(
        {"messages": [{"role": "user", "content": task_description}]}
    )

    return result["messages"][-1].content

@tool("writing_department", description="將任務派給寫作部門，進行內容創作。")
def call_writing_dept(task_description: str) -> str:
    """派遣寫作部門處理寫作任務。"""
    result = writing_supervisor.invoke(
        {"messages": [{"role": "user", "content": task_description}]}
    )

    return result["messages"][-1].content

ceo_agent = create_agent(
    model,
    tools=[call_research_dept, call_writing_dept],
    system_prompt=(
        "你是專案總監（CEO），負責統籌研究部門和寫作部門。\n"
        "收到使用者需求後：\n"
        "1. 先派研究部門收集所需資料\n"
        "2. 再將研究結果交給寫作部門撰寫內容\n"
        "3. 整合所有成果，給使用者最終回覆\n\n"
        "確保兩個部門的產出銜接良好，最終交付物完整且高品質。"
    ),
    name="ceo",
)

# === 執行 ===
def main():
    result = ceo_agent.invoke(
        {"messages": [{"role": "user", "content": "我需要一篇關於大型語言模型在醫療領域應用的部落格文章,請先做研究再寫作。"}]}
    )

    final_message = result["messages"][-1]
    content = final_message.content

    # 兼容 Gemini 的 list[dict] 格式與 OpenAI 的 str 格式
    if isinstance(content, list):
        text = "\n".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    else:
        text = content

    print("=" * 60)
    print("CEO Agent 的最終回覆:")
    print("=" * 60)
    print(text)

if __name__ == "__main__":
    main()

# create_dataset.py

from dotenv import load_dotenv
load_dotenv()

from langsmith import Client

ls_client = Client()

# ============================================================
# 建立一個 RAG 系統的評估 Dataset
# ============================================================

dataset_name = "RAG-QA-Evaluation-v1"

# 如果 Dataset 已存在，先刪除（開發階段方便重複執行）
if ls_client.has_dataset(dataset_name=dataset_name):
    existing = ls_client.read_dataset(dataset_name=dataset_name)
    ls_client.delete_dataset(dataset_id=existing.id)

    print(f"🗑️  已刪除舊的 Dataset: {dataset_name}")

# 建立新的 Dataset
dataset = ls_client.create_dataset(
    dataset_name=dataset_name,
    description="用於評估 RAG 問答系統的測試資料集（繁體中文）"
)

print(f"✅ 已建立 Dataset: {dataset.name} (ID: {dataset.id})")

# ============================================================
# 新增測試案例（Examples）
# ============================================================
examples = [
    {
        "inputs": {"question": "LangChain v1 中 create_agent 函式的作用是什麼？"},
        "outputs": {
            "answer": "create_agent 是 LangChain v1 的核心函式，用於建立 AI Agent。"
                      "它取代了舊版的 create_react_agent，底層使用 LangGraph 的 "
                      "StateGraph 來管理 Agent 的狀態與工具呼叫迴圈。"
                      "回傳值為 CompiledStateGraph，具備完整的 LangGraph 功能。"
        }
    },
    {
        "inputs": {"question": "什麼是 Middleware？它有哪些 Hook？"},
        "outputs": {
            "answer": "Middleware 是 LangChain v1 的核心機制，用於在 Agent 執行流程中"
                      "插入自定義邏輯。它提供六大 Hook：before_agent、before_model、"
                      "modify_model_request、after_model、after_agent，以及 "
                      "wrap_model_call 和 wrap_tool_call。"
        }
    },
    {
        "inputs": {"question": "RAG 和 GraphRAG 有什麼差別？"},
        "outputs": {
            "answer": "RAG（檢索增強生成）使用向量相似度搜尋來找到相關文件片段，"
                      "適合回答事實性問題。GraphRAG 則在向量搜尋的基礎上加入"
                      "知識圖譜（Knowledge Graph），透過實體之間的關係進行推理，"
                      "能處理需要多步推理的複雜問題。"
        }
    },
    {
        "inputs": {"question": "如何使用 MCP 連接外部工具？"},
        "outputs": {
            "answer": "使用 langchain-mcp-adapters 套件，透過 MultiServerMCPClient "
                      "連接 MCP Server。MCP 支援 stdio 和 HTTP 兩種傳輸方式。"
                      "連接後，使用 load_mcp_tools 將 MCP 工具轉換為 LangChain "
                      "Tools，再傳入 create_agent 的 tools 參數即可。"
        }
    },
    {
        "inputs": {"question": "Python 開發 LangChain 專案推薦什麼套件管理工具？"},
        "outputs": {
            "answer": "推薦使用 uv 作為套件管理工具。uv 是一個以 Rust 撰寫的"
                      "超高速 Python 套件管理器，支援 pyproject.toml 設定，"
                      "可以取代 pip 和 virtualenv 的功能，速度遠超傳統工具。"
        }
    },
]

# 批次新增 Examples
ls_client.create_examples(
    inputs=[e["inputs"] for e in examples],
    outputs=[e["outputs"] for e in examples],
    dataset_id=dataset.id,
)

print(f"📝 已新增 {len(examples)} 個測試案例")

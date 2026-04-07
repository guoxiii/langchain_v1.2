# 檔案名稱：subgraph_isolated_state.py

from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

# === 子圖的私有狀態 ===
class AnalysisState(TypedDict):
    raw_data: str
    intermediate_result: str  # 這是子圖私有的，父圖看不到
    analysis_output: str

# === 父圖的狀態 ===
class ParentState(TypedDict):
    input_data: str
    analysis_result: str  # 只接收子圖的最終結果
    final_output: str

# --- 子圖節點 ---
def preprocess(state: AnalysisState) -> dict:
    raw = state["raw_data"]
    processed = f"[已清洗] {raw}"
    print(f"🧹 資料預處理：{processed}")
    return {"intermediate_result": processed}

def analyze(state: AnalysisState) -> dict:
    data = state["intermediate_result"]
    result = f"[分析完成] {data} → 發現 3 個重要趨勢"
    print(f"🔬 分析結果：{result}")
    return {"analysis_output": result}

# 建立子圖
analysis_graph = StateGraph(AnalysisState)
analysis_graph.add_node("preprocess", preprocess)
analysis_graph.add_node("analyze", analyze)
analysis_graph.add_edge(START, "preprocess")
analysis_graph.add_edge("preprocess", "analyze")
analysis_graph.add_edge("analyze", END)
analysis_subgraph = analysis_graph.compile()

# --- 父圖節點 ---
def prepare_data(state: ParentState) -> dict:
    print(f"📥 準備資料：{state['input_data']}")
    return {}

def run_analysis(state: ParentState) -> dict:
    """呼叫子圖，手動做狀態轉換"""
    # 把父圖狀態轉換為子圖狀態
    sub_input = {
        "raw_data": state["input_data"],
        "intermediate_result": "",
        "analysis_output": ""
    }   

    # 執行子圖
    sub_result = analysis_subgraph.invoke(sub_input)    

    # 把子圖結果轉回父圖狀態
    return {"analysis_result": sub_result["analysis_output"]}

def generate_report(state: ParentState) -> dict:
    report = f"報告：{state['analysis_result']}"
    print(f"📊 {report}")
    return {"final_output": report}

# 建立父圖
parent_graph = StateGraph(ParentState)
parent_graph.add_node("prepare", prepare_data)
parent_graph.add_node("analysis", run_analysis)
parent_graph.add_node("report", generate_report)
parent_graph.add_edge(START, "prepare")
parent_graph.add_edge("prepare", "analysis")
parent_graph.add_edge("analysis", "report")
parent_graph.add_edge("report", END)

checkpointer = InMemorySaver()
app = parent_graph.compile(checkpointer=checkpointer)

# 執行
config = {"configurable": {"thread_id": "analysis-1"}}

result = app.invoke(
    {
        "input_data": "2026年第一季銷售數據",
        "analysis_result": "",
        "final_output": ""
    },
    config=config
)

print(f"\n最終輸出：{result['final_output']}")

# ui/app2.py
"""KnowledgeHub 智能問答介面 — Streamlit 版"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import asyncio
import uuid
from dotenv import load_dotenv

load_dotenv()

from src.agent.qa_agent import create_qa_agent
from src.indexing.graph_index import GraphIndexManager

# === 頁面設定 ===
st.set_page_config(
    page_title="KnowledgeHub 企業知識助理",
    page_icon="📚",
    layout="wide",
)

st.title("📚 KnowledgeHub 企業知識助理")
st.caption("基於 LangChain v1 + RAG + GraphRAG 的智能問答系統")

# === Session State 初始化 ===
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    st.session_state.agent = create_qa_agent(use_memory=True)

# === 知識圖譜探索器 ===
def render_knowledge_graph_explorer(user_role: str):
    """知識圖譜探索器"""
    st.subheader("🔗 知識圖譜探索")

    graph_index = GraphIndexManager()

    concept = st.text_input(
        "輸入要查詢的概念",
        placeholder="例如：LangChain、微服務、API 設計",
    )

    depth = st.slider("關係深度", min_value=1, max_value=3, value=2)

    if concept:
        with st.spinner("🔍 查詢知識圖譜..."):
            results = graph_index.query_related_concepts(
                concept, depth=depth
            )

        if results:
            st.success(f"找到 {len(results)} 筆相關資料")

            # 展示結果
            for i, result in enumerate(results[:20]):
                with st.expander(f"關係 {i+1}"):
                    st.json(result)

            # 統計資訊
            st.metric("相關節點數", len(results))
        else:
            st.warning(f"沒有找到與「{concept}」相關的資料")

    # Cypher 查詢（管理員專用）
    if user_role == "admin":
        st.divider()
        st.subheader("🔧 進階 Cypher 查詢（管理員）")

        cypher = st.text_area(
            "Cypher 查詢",
            value="MATCH (n) RETURN n LIMIT 25",
            height=100,
        )

        if st.button("執行查詢"):
            with st.spinner("執行中..."):
                try:
                    results = graph_index.graph.query(cypher)
                    st.json(results[:50])
                except Exception as e:
                    st.error(f"查詢失敗：{e}")

# === 側邊欄 ===
with st.sidebar:
    st.header("⚙️ 設定")

    # 使用者資訊
    user_name = st.text_input("你的名字", value="使用者")

    user_role = st.selectbox(
        "角色",
        options=["viewer", "editor", "admin"],
        format_func=lambda x: {
            "viewer": "👁️ 檢視者",
            "editor": "✏️ 編輯者",
            "admin": "👑 管理員",
        }[x],
    )

    st.divider()

    # 對話管理
    if st.button("🔄 新對話", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.caption(f"Thread ID: {st.session_state.thread_id[:8]}...")
    st.divider()

    # 快速問題
    st.subheader("💡 試試這些問題")

    quick_questions = [
        "知識庫裡有哪些文件？",
        "公司的技術架構是什麼？",
        "最近的專案進度如何？",
    ]

    for q in quick_questions:
        if st.button(q, use_container_width=True):
            st.session_state.quick_question = q

# === 主要內容區：分頁 ===
tab_chat, tab_graph = st.tabs(["💬 智能問答", "🔗 知識圖譜"])

# --- 智能問答分頁 ---
with tab_chat:
    # 顯示歷史訊息
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # 處理快速問題
    if "quick_question" in st.session_state:
        prompt = st.session_state.pop("quick_question")
    else:
        prompt = st.chat_input("在知識庫中搜尋...")

    if prompt:
        # 顯示使用者訊息
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.write(prompt)

        # Agent 回答
        with st.chat_message("assistant"):
            with st.spinner("🔍 正在搜尋知識庫..."):
                try:
                    response = asyncio.run(
                        st.session_state.agent.ainvoke(
                            {"messages": [{"role": "user", "content": prompt}]},
                            config={
                                "configurable": {
                                    "thread_id": st.session_state.thread_id,
                                    "user_id": user_name,
                                    "user_role": user_role,
                                }
                            },
                        )
                    )

                    # 取得回覆
                    messages = response.get("messages", [])

                    if messages:
                        answer = messages[-1].content
                    else:
                        answer = "抱歉，我無法回答這個問題。"
                except Exception as e:
                    answer = f"發生錯誤：{str(e)}\n\n請檢查 API 設定是否正確。"

            st.write(answer)

            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )

# --- 知識圖譜分頁 ---
with tab_graph:
    render_knowledge_graph_explorer(user_role)
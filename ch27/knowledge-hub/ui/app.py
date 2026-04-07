# ui/app.py
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


# === 聊天介面 ===
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

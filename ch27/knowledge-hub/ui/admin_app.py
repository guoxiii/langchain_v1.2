# ui/admin_app.py
"""KnowledgeHub 管理後台"""

import streamlit as st
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# === 頁面設定 ===
st.set_page_config(
    page_title="KnowledgeHub 管理後台",
    page_icon="⚙️",
    layout="wide",
)

st.title("⚙️ KnowledgeHub 管理後台")

# === 載入 Metadata ===
metadata_path = Path("./data/metadata.json")

if metadata_path.exists():
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata_store = json.load(f)
else:
    metadata_store = {}

# === 頁籤 ===
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 總覽", "📄 文件管理", "📈 使用統計", "🔍 品質監控"
])

# --- Tab 1: 總覽 ---
with tab1:
    st.header("系統總覽")
    col1, col2, col3, col4 = st.columns(4)
    total_docs = len(metadata_store)

    indexed_docs = sum(
        1 for d in metadata_store.values()
        if d.get("status") == "indexed"
    )

    pending_docs = sum(
        1 for d in metadata_store.values()
        if d.get("status") == "pending"
    )

    total_chunks = sum(
        d.get("chunk_count", 0) for d in metadata_store.values()
    )

    col1.metric("📄 總文件數", total_docs)
    col2.metric("✅ 已索引", indexed_docs)
    col3.metric("⏳ 待處理", pending_docs)
    col4.metric("📊 總 Chunk 數", total_chunks)

# --- Tab 2: 文件管理 ---
with tab2:
    st.header("文件管理")

    if not metadata_store:
        st.info("目前沒有文件。請先上傳文件。")
    else:
        for doc_id, meta in metadata_store.items():
            with st.expander(
                f"{'✅' if meta.get('status') == 'indexed' else '⏳'} "
                f"{meta.get('title', '未命名')} — {doc_id[:8]}..."
            ):
                col1, col2, col3 = st.columns(3)
                col1.write(f"**類型：** {meta.get('file_type', 'N/A')}")
                col2.write(f"**狀態：** {meta.get('status', 'N/A')}")
                col3.write(f"**Chunks：** {meta.get('chunk_count', 0)}")
                st.write(f"**上傳者：** {meta.get('uploaded_by', 'N/A')}")
                st.write(f"**上傳時間：** {meta.get('uploaded_at', 'N/A')}")

                if meta.get("summary"):
                    st.write("**AI 摘要：**")
                    st.info(meta["summary"])

                if meta.get("tags"):
                    st.write(f"**標籤：** {', '.join(meta['tags'])}")

    # 文件上傳區
    st.divider()
    st.subheader("📤 上傳新文件")

    uploaded_file = st.file_uploader(
        "選擇文件",
        type=["pdf", "docx", "md", "txt"],
        accept_multiple_files=False,
    )

    upload_tags = st.text_input(
        "標籤（逗號分隔）",
        placeholder="例如：技術文檔, API, 內部規範",
    )

    if uploaded_file and st.button("📥 上傳並索引"):
        # 儲存檔案
        save_path = Path("./data/uploads") / uploaded_file.name
        save_path.parent.mkdir(parents=True, exist_ok=True)

        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"檔案已上傳至 {save_path}")
        st.info("💡 請執行索引管線來處理新上傳的文件。")

# --- Tab 3: 使用統計 ---
with tab3:
    st.header("使用統計")
    st.info(
        "📊 使用統計功能需要搭配 LangSmith 追蹤。\n\n"
        "請確保已設定 `LANGSMITH_TRACING=true` 環境變數，\n"
        "然後在 LangSmith Dashboard 中查看詳細的使用數據，\n"
        "包括：查詢次數、Token 用量、回覆延遲、錯誤率等。"
    )

    st.subheader("基本統計")
    st.metric("📄 知識庫文件總數", total_docs)

    st.metric(
        "💾 知識庫總大小",
        f"{sum(d.get('file_size_bytes', 0) for d in metadata_store.values()) / 1024 / 1024:.1f} MB",
    )


# --- Tab 4: 品質監控 ---
with tab4:
    st.header("品質監控")
    st.markdown("""
    ### 品質監控指標
    品質監控是確保知識庫持續提供準確回答的關鍵。以下是我們追蹤的核心指標：
    | 指標 | 說明 | 目標 |
    |------|------|------|
    | **Faithfulness（忠實度）** | 回答是否忠於來源文件 | > 90% |
    | **Relevance（相關性）** | 回答是否與問題相關 | > 85% |
    | **Completeness（完整性）** | 回答是否涵蓋問題的所有面向 | > 80% |
    | **User Satisfaction（使用者滿意度）** | 使用者反饋的正面比例 | > 85% |
    這些指標可透過 LangSmith 的 Evaluation 功能自動計算。
    詳見第 18 章的 LangSmith 評估管線設定。
    """)

    st.subheader("🔍 手動品質檢查")

    test_question = st.text_input(
        "輸入測試問題",
        placeholder="輸入一個問題來測試知識庫的回答品質",
    )

    if test_question:
        st.info("💡 請在主要的問答介面中測試，並使用 LangSmith 追蹤來分析回答品質。")

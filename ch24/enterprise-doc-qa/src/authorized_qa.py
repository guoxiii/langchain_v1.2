# authorized_qa.py

"""帶權限控制的問答流程"""

from dotenv import load_dotenv
load_dotenv()

from src.access_control import get_user_context, create_authorized_agent
from src.citation_agent import ask_question, init_retriever, create_doc_qa_agent
from src.document_pipeline import DocumentPipeline
from src.vector_store import VectorStoreManager

def demo_access_control():
    """展示不同使用者的存取權限差異。"""
    # 準備文件（包含不同權限等級的文件）
    pipeline = DocumentPipeline()

    chunks = pipeline.process([
        {
            "source": "docs/公開公告.pdf",
            "department": "general",
            "access_level": "public",
        },
        {
            "source": "docs/員工手冊.pdf",
            "department": "hr",
            "access_level": "internal",
        },
        {
            "source": "docs/薪資結構.pdf",
            "department": "hr",
            "access_level": "confidential",
        },
    ])

    # 建立向量存儲
    vs = VectorStoreManager()
    vs.add_documents(chunks)
    init_retriever(chunks)
    question = "公司的薪資結構是怎麼安排的？"

    # ── 測試不同使用者 ──
    for user_id in ["alice", "bob", "charlie"]:
        user = get_user_context(user_id)
        print(f"\n{'='*60}")
        print(
            f"👤 {user.name} ({user.access_level}) "
            f"問：{question}"
        )

        print(f"{'='*60}")

        # ✅ 改用 create_doc_qa_agent，傳入使用者權限
        agent = create_doc_qa_agent(
            user_access_level=user.access_level
        )

        ask_question(agent, question)

if __name__ == "__main__":
    demo_access_control()

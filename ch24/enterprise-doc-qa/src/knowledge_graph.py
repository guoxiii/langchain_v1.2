# knowledge_graph.py

"""知識圖譜建構模組 — LLMGraphTransformer + Neo4j"""

from dotenv import load_dotenv
load_dotenv()

from langchain_core.documents import Document
from langchain.chat_models import init_chat_model
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_neo4j import Neo4jGraph
from src.config import (
    GRAPH_EXTRACTION_MODEL,
    NEO4J_URI,
    NEO4J_USERNAME,
    NEO4J_PASSWORD,
)

class KnowledgeGraphBuilder:
    """
    知識圖譜建構器 — 自動從文件中抽取實體與關係。
    工作流程：
    1. 接收切割後的 Document chunks
    2. 用 LLM 自動抽取實體（節點）和關係（邊）
    3. 將結果存入 Neo4j 圖資料庫
    """

    def __init__(self):
        # 初始化 LLM（用於圖譜抽取）
        self.llm = init_chat_model(GRAPH_EXTRACTION_MODEL)
        # 初始化 LLMGraphTransformer
        # allowed_nodes 和 allowed_relationships 可以限定抽取的類型，
        # 避免 LLM 天馬行空地抽取不相關的實體
        self.transformer = LLMGraphTransformer(
            llm=self.llm,
            allowed_nodes=[
                "Person",
                "Department",
                "Policy",
                "Document",
                "Product",
                "Process",
                "Role",
                "Regulation",
            ],
            allowed_relationships=[
                "MANAGES",
                "BELONGS_TO",
                "DEFINES",
                "REQUIRES",
                "APPLIES_TO",
                "REPORTS_TO",
                "AUTHORED_BY",
                "RELATED_TO",
            ],
        )

        # 連接 Neo4j
        self.graph = Neo4jGraph(
            url=NEO4J_URI,
            username=NEO4J_USERNAME,
            password=NEO4J_PASSWORD,
        )

    def build_from_documents(
        self,
        documents: list[Document],
        batch_size: int = 10,
    ) -> dict:
        """
        從文件 chunks 建構知識圖譜。

        Args:
            documents: 切割後的 Document 列表
            batch_size: 每批處理的文件數量（避免 rate limit）

        Returns:
            包含統計資訊的 dict
        """

        total_nodes = 0
        total_relationships = 0
        errors = 0

        for i in range(0, len(documents), batch_size):
            batch = documents[i : i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(documents) + batch_size - 1) // batch_size

            print(
                f"🔄 處理批次 {batch_num}/{total_batches} "
                f"({len(batch)} 個 chunks)..."
            )

            try:
                # 使用 LLM 將文本轉換為圖譜文件
                graph_documents = (
                    self.transformer.convert_to_graph_documents(batch)
                )

                # 存入 Neo4j
                self.graph.add_graph_documents(
                    graph_documents,
                    baseEntityLabel=True,  # 所有節點都加上 __Entity__ 標籤
                    include_source=True,   # 保留來源 chunk 的連結
                )

                # 統計
                for gd in graph_documents:
                    total_nodes += len(gd.nodes)
                    total_relationships += len(gd.relationships)

                print(
                    f"   ✅ 本批次抽取 "
                    f"{sum(len(gd.nodes) for gd in graph_documents)} 個節點、"
                    f"{sum(len(gd.relationships) for gd in graph_documents)} 個關係"
                )
            except Exception as e:
                errors += 1
                print(f"   ❌ 批次 {batch_num} 處理失敗：{e}")

        stats = {
            "total_documents": len(documents),
            "total_nodes": total_nodes,
            "total_relationships": total_relationships,
            "errors": errors,
        }

        print(f"\n📊 知識圖譜建構完成！")
        print(f"   節點數：{total_nodes}")
        print(f"   關係數：{total_relationships}")
        print(f"   錯誤數：{errors}")

        return stats

    def query_graph(self, cypher: str, params: dict | None = None) -> list:
        """直接執行 Cypher 查詢（用於除錯和驗證）。"""
        return self.graph.query(cypher, params=params or {})

    def get_schema(self) -> str:
        """取得目前圖譜的 Schema（節點類型、關係類型）。"""
        self.graph.refresh_schema()
        return self.graph.schema

    def clear_graph(self) -> None:
        """清空整個圖譜（⚠️ 危險操作，僅限開發環境使用）。"""
        self.graph.query("MATCH (n) DETACH DELETE n")
        print("🗑️ 圖譜已清空")

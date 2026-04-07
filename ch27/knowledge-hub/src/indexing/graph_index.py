# src/indexing/graph_index.py
"""知識圖譜索引 — 文件之間的關係網"""

from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model
from langchain_neo4j import Neo4jGraph
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
from src.config import config

class GraphIndexManager:
    """
    Neo4j 知識圖譜索引管理器

    將文件中的實體（人、概念、產品、技術等）和
    它們之間的關係，提取並存入 Neo4j 圖資料庫。
    想像你在畫一張心智圖：每個圓圈是一個概念，
    連線代表它們之間的關係。這就是知識圖譜在做的事。
    """
    def __init__(self, model_name: str = config.primary_model):
        self.graph = Neo4jGraph(
            url=config.neo4j_uri,
            username=config.neo4j_username,
            password=config.neo4j_password,
        )

        self.llm = init_chat_model(model_name, temperature=0)

        self.transformer = LLMGraphTransformer(
            llm=self.llm,
            allowed_nodes=[
                "Person", "Organization", "Technology",
                "Product", "Concept", "Document", "Project",
            ],
            allowed_relationships=[
                "WORKS_AT", "USES", "DEPENDS_ON", "RELATED_TO",
                "AUTHORED_BY", "PART_OF", "MENTIONS",
            ],
        )

    async def add_to_graph(
        self, documents: list[Document], doc_id: str
    ) -> int:
        """
        從文件中提取實體與關係，存入 Neo4j

        Parameters
        ----------

        documents : list[Document]
            切割後的 Document 列表

        doc_id : str
            來源文件 ID

        Returns
        -------

        int
            提取的圖節點數量
        """

        # 使用 LLM 提取圖結構
        graph_documents = await self.transformer.aconvert_to_graph_documents(
            documents
        )

        # 為每個節點添加來源文件資訊
        for graph_doc in graph_documents:
            for node in graph_doc.nodes:
                node.properties["source_doc_id"] = doc_id

        # 寫入 Neo4j
        self.graph.add_graph_documents(
            graph_documents,
            baseEntityLabel=True,
            include_source=True,
        )

        total_nodes = sum(
            len(gd.nodes) for gd in graph_documents
        )

        print(f"🔗 已建立 {total_nodes} 個圖節點（doc_id: {doc_id}）")
        return total_nodes

    def query_related_concepts(
        self, concept: str, depth: int = 2
    ) -> list[dict]:
        """
        查詢與某個概念相關的所有實體

        Parameters
        ----------

        concept : str
            要查詢的概念名稱

        depth : int
            關係深度（1 = 直接關聯，2 = 二度關聯）
        """

        cypher_query = f"""
        MATCH path = (n)-[*1..{depth}]-(m)
        WHERE toLower(n.id) CONTAINS toLower($concept)
        RETURN path
        LIMIT 50
        """

        return self.graph.query(cypher_query, params={"concept": concept})

    def delete_document_nodes(self, doc_id: str) -> None:
        """刪除與指定文件相關的所有節點"""
        self.graph.query(
            """
            MATCH (n)
            WHERE n.source_doc_id = $doc_id
            DETACH DELETE n
            """,
            params={"doc_id": doc_id},
        )

        print(f"🗑️ 已從知識圖譜刪除 doc_id: {doc_id} 的節點")

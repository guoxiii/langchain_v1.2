# graph_retriever.py

"""圖譜檢索模組 — Neo4j Cypher 查詢"""

from dotenv import load_dotenv
load_dotenv()

from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain.chat_models import init_chat_model
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from src.config import (
    PRIMARY_MODEL,
    NEO4J_URI,
    NEO4J_USERNAME,
    NEO4J_PASSWORD,
)

class GraphRetrieverModule:
    """
    圖譜檢索器 — 將自然語言轉為 Cypher 查詢。
    工作原理：
    1. 接收使用者的自然語言問題
    2. 用 LLM 將問題轉為 Cypher 查詢語句
    3. 在 Neo4j 上執行查詢
    4. 將結果包裝成 Document 回傳

    就像有一位精通 SQL 的助理：
    你跟他說「幫我查一下張三的部門主管是誰」，
    他就會自動翻譯成 SQL 去資料庫撈資料。
    """
    def __init__(self):
        self.llm = init_chat_model(PRIMARY_MODEL)
        self.graph = Neo4jGraph(
            url=NEO4J_URI,
            username=NEO4J_USERNAME,
            password=NEO4J_PASSWORD,
        )

        # 重新整理 schema，讓 LLM 知道圖譜的結構
        self.graph.refresh_schema()
    
    def search(self, query: str) -> list[Document]:
        """
        用自然語言查詢知識圖譜。

        Args:
            query: 使用者的自然語言問題

        Returns:
            包含圖譜查詢結果的 Document 列表
        """
        try:
            # 為了避免LLM產生錯誤的Neo4j查詢語法，所以特別定義了提示詞
            cypher_prompt = PromptTemplate(
                input_variables=["schema", "question"],
                template="""你是 Neo4j Cypher 專家。根據以下圖譜 Schema 和使用者問題，寫出 Cypher 查詢。

                    Schema：
                    {schema}

                    重要規則（務必遵守）：
                    1. 絕對不要使用 UNION，改用 OPTIONAL MATCH 收集多種結果
                    2. 使用 ORDER BY 時，排序的變數必須出現在 RETURN 中
                    3. 使用 DISTINCT 或 collect() 等聚合函式後，不能再 ORDER BY 原始變數。
                    錯誤：RETURN DISTINCT collect(doc) AS docs ORDER BY doc.title
                    正確：先 WITH doc ORDER BY doc.title，再 RETURN collect(doc) AS docs
                    4. 保持查詢簡單，不要超過 3 層 MATCH
                    5. 多個 Label 的 OR 條件要寫成 WHERE d:Label1 OR d:Label2，絕對不要寫成 d:`Label1 OR d`

                    使用者問題：{question}

                    只輸出 Cypher 查詢語句，不要任何解釋。""",
            )

            chain = GraphCypherQAChain.from_llm(
                llm=self.llm,
                graph=self.graph,
                verbose=False,
                allow_dangerous_requests=True,
                return_intermediate_steps=True,
                validate_cypher=True,       # 讓 LLM 在執行前先檢查語法
                top_k=10,                   # 限制回傳筆數，避免過大查詢
                cypher_prompt=cypher_prompt,
            )

            result = chain.invoke({"query": query})

            # 提取中間步驟中的 Cypher 結果
            intermediate = result.get("intermediate_steps", [])
            cypher_result = ""

            if intermediate:
                # intermediate_steps 格式：
                # [{"query": "MATCH ...", "context": [...]}]
                for step in intermediate:
                    if isinstance(step, dict) and "context" in step:
                        cypher_result = str(step["context"])

            # 包裝為 Document
            doc = Document(
                page_content=(
                    f"圖譜查詢結果：{result.get('result', '')}\n"
                    f"原始資料：{cypher_result}"
                ),
                metadata={
                    "source_type": "knowledge_graph",
                    "query": query,
                },
            )

            return [doc]

        except Exception as e:
            print(f"⚠️ 圖譜查詢失敗：{e}")
            return []

    def direct_cypher_search(
        self, entity: str, depth: int = 2
    ) -> list[Document]:
        """
        直接用實體名稱進行圖譜鄰域搜尋。
        這個方法不依賴 LLM 生成 Cypher，
        而是用固定模板查詢某個實體周圍的所有連結。

        Args:
            entity: 要搜尋的實體名稱
            depth: 搜尋深度（幾跳）

        Returns:
            包含關聯資訊的 Document 列表
        """
        cypher = """
        MATCH (n)
        WHERE n.id CONTAINS $entity
        MATCH path = (n)-[*1..%d]-(m)

        RETURN 
            n.id AS source,
            [r IN relationships(path) | type(r)] AS relationships,
            m.id AS target

        LIMIT 20
        """ % depth

        try:
            results = self.graph.query(cypher, params={"entity": entity})

            if not results:
                return []

            # 將圖譜結果整理成可讀文本
            lines = []

            for r in results:
                rels = " -> ".join(r["relationships"])
                lines.append(f"{r['source']} --[{rels}]--> {r['target']}")

            doc = Document(
                page_content=(
                    f"知識圖譜中與「{entity}」相關的資訊：\n" + "\n".join(lines)
                ),
                metadata={
                    "source_type": "knowledge_graph",
                    "entity": entity,
                },
            )

            return [doc]

        except Exception as e:
            print(f"⚠️ 圖譜鄰域搜尋失敗：{e}")
            return []

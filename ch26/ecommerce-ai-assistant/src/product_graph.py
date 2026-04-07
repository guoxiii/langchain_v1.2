# src/product_graph.py

"""
商品知識圖譜建構模組
使用 Neo4j 建構商品之間的關聯圖譜
"""

import json
from dotenv import load_dotenv

load_dotenv()

from neo4j import GraphDatabase

class ProductGraphBuilder:
    """
    商品知識圖譜建構器。    

    在 Neo4j 中建立以下節點與關係：
    - (:Product) — 商品節點
    - (:Category) — 分類節點
    - (:Ingredient) — 成分節點
    - (:SkinType) — 膚質節點
    - (:Product)-[:BELONGS_TO]->(:Category)
    - (:Product)-[:CONTAINS]->(:Ingredient)
    - (:Product)-[:SUITABLE_FOR]->(:SkinType)
    - (:Product)-[:RELATED_TO]->(:Product)
    - (:Product)-[:SHARES_INGREDIENT]->(:Product) — 共同成分關聯
    """

    def __init__(self, uri: str, username: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def close(self):
        self.driver.close()

    def clear_database(self):
        """清除現有資料（開發用）"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("🗑️  已清除現有圖譜資料")

    def build_graph(self, products: list[dict]):
        """建構完整的商品知識圖譜"""
        with self.driver.session() as session:
            # 1. 建立商品節點

            for product in products:
                session.run(
                    """
                    MERGE (p:Product {id: $id})
                    SET p.name = $name,
                        p.category = $category,
                        p.subcategory = $subcategory,
                        p.price = $price,
                        p.description = $description,
                        p.rating = $rating,
                        p.stock = $stock
                    """,
                    id=product["id"],
                    name=product["name"],
                    category=product["category"],
                    subcategory=product["subcategory"],
                    price=product["price"],
                    description=product["description"],
                    rating=product["rating"],
                    stock=product["stock"],
                )

            # 2. 建立分類節點與關係
            for product in products:
                session.run(
                    """
                    MERGE (c:Category {name: $category})
                    WITH c
                    MATCH (p:Product {id: $id})
                    MERGE (p)-[:BELONGS_TO]->(c)
                    """,
                    category=product["category"],
                    id=product["id"],
                )

            # 3. 建立成分節點與關係
            for product in products:
                for ingredient in product["ingredients"]:
                    session.run(
                        """
                        MERGE (i:Ingredient {name: $ingredient})
                        WITH i
                        MATCH (p:Product {id: $id})
                        MERGE (p)-[:CONTAINS]->(i)
                        """,
                        ingredient=ingredient,
                        id=product["id"],
                    )

            # 4. 建立膚質節點與關係
            for product in products:
                for skin_type in product["skin_type"]:
                    session.run(
                        """
                        MERGE (s:SkinType {name: $skin_type})
                        WITH s
                        MATCH (p:Product {id: $id})
                        MERGE (p)-[:SUITABLE_FOR]->(s)
                        """,
                        skin_type=skin_type,
                        id=product["id"],
                    )

            # 5. 建立商品關聯關係
            for product in products:
                for related_id in product.get("related_products", []):
                    session.run(
                        """
                        MATCH (p1:Product {id: $id1})
                        MATCH (p2:Product {id: $id2})
                        MERGE (p1)-[:RELATED_TO]->(p2)
                        """,
                        id1=product["id"],
                        id2=related_id,
                    )

            # 6. 自動建立「共同成分」關聯
            session.run(
                """
                MATCH (p1:Product)-[:CONTAINS]->(i:Ingredient)<-[:CONTAINS]-(p2:Product)
                WHERE p1.id < p2.id
                WITH p1, p2, collect(i.name) AS shared_ingredients
                WHERE size(shared_ingredients) >= 1
                MERGE (p1)-[r:SHARES_INGREDIENT]->(p2)
                SET r.ingredients = shared_ingredients,
                    r.count = size(shared_ingredients)
                """
            )

        print(f"✅ 已建構商品知識圖譜，共 {len(products)} 件商品")

    def query_related_products(self, product_id: str) -> list[dict]:
        """查詢與指定商品相關的商品（透過多種關係）"""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:Product {id: $id})
                OPTIONAL MATCH (p)-[:RELATED_TO]-(related:Product)
                OPTIONAL MATCH (p)-[:SHARES_INGREDIENT]-(shared:Product)
                OPTIONAL MATCH (p)-[:SUITABLE_FOR]->(s:SkinType)<-[:SUITABLE_FOR]-(same_skin:Product)
                WHERE same_skin.id <> p.id
                WITH p, 
                     collect(DISTINCT {id: related.id, name: related.name, relation: 'recommended_pair'}) AS related_list,
                     collect(DISTINCT {id: shared.id, name: shared.name, relation: 'shared_ingredient'}) AS shared_list,
                     collect(DISTINCT {id: same_skin.id, name: same_skin.name, relation: 'same_skin_type'}) AS skin_list
                RETURN related_list + shared_list + skin_list AS all_related
                """,
                id=product_id,
            )

            record = result.single()

            if record:
                # 過濾掉 None 值的結果
                return [
                    item for item in record["all_related"]
                    if item.get("id") is not None
                ]

            return []

    def query_by_skin_type(self, skin_type: str) -> list[dict]:
        """根據膚質查詢適合的商品"""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:Product)-[:SUITABLE_FOR]->(s:SkinType {name: $skin_type})
                RETURN p.id AS id, p.name AS name, p.price AS price, 
                       p.rating AS rating, p.description AS description
                ORDER BY p.rating DESC
                """,
                skin_type=skin_type,
            )

            return [dict(record) for record in result]

    def query_skincare_routine(self, skin_type: str) -> list[dict]:
        """
        根據膚質推薦完整的保養流程。
        這是 GraphRAG 的殺手級應用 — 透過圖譜中的分類關係，
        自動組合出「卸妝 → 潔面 → 化妝水 → 精華液 → 防曬」的完整流程。
        """
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (p:Product)-[:SUITABLE_FOR]->(s:SkinType {name: $skin_type})
                MATCH (p)-[:BELONGS_TO]->(c:Category)
                WITH c.name AS category, p
                ORDER BY p.rating DESC
                WITH category, collect(p)[0] AS best_product
                WITH category, best_product,
                     CASE category
                         WHEN '卸妝' THEN 1
                         WHEN '潔面' THEN 2
                         WHEN '化妝水' THEN 3
                         WHEN '精華液' THEN 4
                         WHEN '乳霜' THEN 5
                         WHEN '防曬' THEN 6
                         WHEN '面膜' THEN 7
                         ELSE 99
                     END AS step_order

                RETURN category AS step, 
                       best_product.name AS product_name,
                       best_product.id AS product_id,
                       best_product.price AS price,
                       best_product.rating AS rating
                ORDER BY step_order
                """,
                skin_type=skin_type,
            )

            return [dict(record) for record in result]

# ============================================================
# 執行建構
# ============================================================

if __name__ == "__main__":
    import os
    from pathlib import Path
    
    products = json.loads(
        Path("data/products.json").read_text(encoding="utf-8")
    )

    builder = ProductGraphBuilder(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        username=os.getenv("NEO4J_USERNAME", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "password"),
    )

    builder.clear_database()
    builder.build_graph(products)

    # 測試查詢
    print("\n🔍 查詢 P001（控油潔面凝膠）的相關商品：")
    related = builder.query_related_products("P001")

    for item in related:
        print(f"  - {item['name']} ({item['relation']})")

    print("\n🧴 油性肌膚的完整保養流程：")
    routine = builder.query_skincare_routine("油性")

    for step in routine:
        print(f"  Step {step['step']}：{step['product_name']} (NT${step['price']})")

    builder.close()

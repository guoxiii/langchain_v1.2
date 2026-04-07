# demo_4.py
"""模式五：路徑查詢"""

import os
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph

load_dotenv()

graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
)

def find_path(entity_a: str, entity_b: str, max_hops: int = 4) -> str:
    """找出兩個實體之間的最短路徑"""
    result = graph.query("""
        MATCH path = shortestPath(
            (a {id: $name_a})-[*1..""" + str(max_hops) + """]-(b {id: $name_b})
        )
        RETURN [n IN nodes(path) | n.id] AS path_nodes,
               [r IN relationships(path) | type(r)] AS path_relationships
    """, params={"name_a": entity_a, "name_b": entity_b})

    if not result:
        return f"找不到 {entity_a} 和 {entity_b} 之間的路徑"

    row = result[0]
    nodes = row["path_nodes"]
    rels = row["path_relationships"]
    path_str = nodes[0]

    for i, rel in enumerate(rels):
        path_str += f" --[{rel}]--> {nodes[i+1]}"

    return f"路徑：{path_str}"


# 找出張三和王五之間的關聯
path = find_path("張三", "王五")
print(path)

# 可能輸出：路徑：張三 --[REPORTS_TO]--> 李四 --[COLLABORATES_WITH]--> 王五

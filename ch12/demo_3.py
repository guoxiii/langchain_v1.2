# demo_3.py
"""模式四：子圖擷取"""

import os
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph

load_dotenv()

graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
)

def extract_subgraph(entity_name: str, hops: int = 2) -> str:
    """提取某個實體周圍 N 跳的子圖"""
    result = graph.query("""
        MATCH path = (start {id: $name})-[*1..""" + str(hops) + """]->(end)
        RETURN start.id AS source,
               [r IN relationships(path) | type(r)] AS relationships,
               end.id AS target,
               labels(end) AS target_labels
        LIMIT 50
    """, params={"name": entity_name})

    if not result:
        return f"找不到名為 '{entity_name}' 的實體"

    lines = [f"以 {entity_name} 為中心的子圖："]

    for row in result:
        rels = " -> ".join(row["relationships"])
        target_type = row["target_labels"][0] if row["target_labels"] else "Unknown"

        lines.append(
            f"  {row['source']} --[{rels}]--> {target_type}: {row['target']}"
        )

    return "\n".join(lines)

# 查看「李四」周圍的關係網
subgraph = extract_subgraph("李四", hops=2)
print(subgraph)

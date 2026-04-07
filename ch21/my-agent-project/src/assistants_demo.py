# assistants_demo.py

"""Assistants API 操作範例"""

import asyncio
from langgraph_sdk import get_client

async def main():
    client = get_client(url="http://localhost:2024")

    # 列出所有 Assistants
    assistants = await client.assistants.search()

    print("=== 所有 Assistants ===")

    for a in assistants:
        print(f"  ID: {a['assistant_id']}")
        print(f"  Graph: {a['graph_id']}")
        print(f"  名稱: {a.get('name', 'N/A')}")
        print()

    # 建立自訂 Assistant（相同 Graph，不同配置）
    custom_assistant = await client.assistants.create(
        graph_id="my_agent",
        name="嚴謹分析師",
        config={
            "configurable": {
                "system_prompt": "你是一位嚴謹的數據分析師。"
                                 "回答問題時務必引用資料來源，並標注信心程度。"
            }
        },
        metadata={"department": "data-team", "version": "1.0"}
    )

    print(f"建立自訂 Assistant: {custom_assistant['assistant_id']}")

    # 搜尋特定 metadata 的 Assistants
    data_assistants = await client.assistants.search(
        metadata={"department": "data-team"}
    )

    print(f"資料團隊的 Assistants: {len(data_assistants)} 個")

if __name__ == "__main__":
    asyncio.run(main())

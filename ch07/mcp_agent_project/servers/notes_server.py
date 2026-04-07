# servers/notes_server.py
"""筆記 MCP Server — 模擬簡單的資料庫操作"""
from mcp.server.fastmcp import FastMCP
from datetime import datetime

mcp = FastMCP("Notes")

# 用一個簡單的 dict 模擬資料庫
notes_db: dict[str, dict] = {}
note_counter = 0

@mcp.tool()
def create_note(title: str, content: str) -> dict:
    """建立一則新筆記。

    Args:
        title: 筆記標題
        content: 筆記內容

    Returns:
        建立成功的筆記資訊，包含 id、title、content、created_at
    """

    global note_counter
    note_counter += 1
    note_id = f"note_{note_counter}"

    note = {
        "id": note_id,
        "title": title,
        "content": content,
        "created_at": datetime.now().isoformat(),
    }

    notes_db[note_id] = note
    return {"message": f"筆記建立成功！", "note": note}




@mcp.tool()
def list_notes() -> dict:
    """列出所有筆記。

    Returns:
        所有筆記的清單，包含 id 和 title。如果沒有筆記，回傳提示訊息。
    """

    if not notes_db:
        return {"message": "目前沒有任何筆記。", "notes": []}

    notes_list = [
        {"id": note["id"], "title": note["title"]}
        for note in notes_db.values()
    ]

    return {"message": f"共有 {len(notes_list)} 則筆記。", "notes": notes_list}

@mcp.tool()
def get_note(note_id: str) -> dict:
    """取得指定筆記的完整內容。

    Args:
        note_id: 筆記的 ID（例如 "note_1"）

    Returns:
        筆記的完整資訊。如果找不到，回傳錯誤訊息。
    """

    if note_id in notes_db:
        return notes_db[note_id]
    else:
        return {"error": f"找不到 ID 為 '{note_id}' 的筆記。"}

@mcp.tool()
def search_notes(keyword: str) -> dict:
    """搜尋包含指定關鍵字的筆記。
    會在標題和內容中搜尋。

    Args:
        keyword: 搜尋關鍵字

    Returns:
        符合條件的筆記清單
    """

    results = []

    for note in notes_db.values():
        if keyword.lower() in note["title"].lower() or keyword.lower() in note["content"].lower():
            results.append(
                {"id": note["id"], "title": note["title"]}
            )

    return {
        "keyword": keyword,
        "results_count": len(results),
        "results": results,
    }

@mcp.tool()
def delete_note(note_id: str) -> dict:
    """刪除指定的筆記。

    Args:
        note_id: 要刪除的筆記 ID

    Returns:
        刪除結果訊息
    """

    if note_id in notes_db:
        deleted = notes_db.pop(note_id)
        return {"message": f"已刪除筆記：{deleted['title']}"}
    else:
        return {"error": f"找不到 ID 為 '{note_id}' 的筆記。"}

if __name__ == "__main__":
    mcp.run(transport="stdio")

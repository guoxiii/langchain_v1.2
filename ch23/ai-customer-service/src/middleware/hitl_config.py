# src/middleware/hitl_config.py

"""
Human-in-the-Loop Middleware 設定。
為高風險操作加上人工審核閘門。
"""

from langchain.agents.middleware import HumanInTheLoopMiddleware

def create_hitl_middleware():
    """建立 HITL Middleware，設定哪些工具需要人工審核。"""
    return HumanInTheLoopMiddleware(
        interrupt_on={
            # 建立工單前需要確認
            "create_ticket": {
                "allowed_decisions": ["approve", "edit", "reject"],
            },
            # 更新工單狀態需要確認
            "update_ticket": {
                "allowed_decisions": ["approve", "reject"],
            },
            # FAQ 搜尋不需要審核（低風險）
            "search_faq": False,
            # 轉接真人不需要審核（本身就是升級行為）
            "escalate_to_human": False,
        }
    )

# access_control.py

"""存取控制模組"""

from dataclasses import dataclass

@dataclass
class UserContext:
    """使用者上下文 — 包含身份和權限資訊。"""
    user_id: str
    name: str
    department: str
    access_level: str  # "public" | "internal" | "confidential"
    roles: list[str] | None = None

# 模擬的使用者資料庫（實際應用中會連接 LDAP 或 SSO）
MOCK_USERS: dict[str, UserContext] = {
    "alice": UserContext(
        user_id="alice",
        name="Alice Chen",
        department="engineering",
        access_level="confidential",
        roles=["engineer", "tech_lead"],
    ),
    "bob": UserContext(
        user_id="bob",
        name="Bob Wang",
        department="marketing",
        access_level="internal",
        roles=["marketer"],
    ),
    "charlie": UserContext(
        user_id="charlie",
        name="Charlie Lin",
        department="external",
        access_level="public",
        roles=["contractor"],
    ),
}

def get_user_context(user_id: str) -> UserContext:
    """
    取得使用者上下文。
    在實際應用中，這會從 SSO / LDAP / JWT Token 中提取使用者資訊。
    """
    user = MOCK_USERS.get(user_id)

    if not user:
        raise ValueError(f"未知的使用者：{user_id}")

    return user

def create_authorized_agent(user_id: str):
    """
    建立一個帶有權限控制的問答 Agent。
    根據使用者的存取級別，Agent 只能搜尋到對應範圍的文件。
    """
    from src.citation_agent import create_doc_qa_agent

    user = get_user_context(user_id)

    print(
        f"👤 使用者：{user.name} "
        f"({user.department}, {user.access_level})"
    )

    agent = create_doc_qa_agent()
    return agent, user

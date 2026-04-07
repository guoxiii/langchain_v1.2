# src/auth/permissions.py
"""權限控制系統 — 誰能看什麼，一清二楚"""

from dotenv import load_dotenv
load_dotenv()

from src.models import UserRole

class PermissionManager:
    """
    基於角色的存取控制（RBAC）

    角色權限矩陣：
    - Admin：可以看到所有文件、管理文件、管理使用者
    - Editor：可以看到一般文件、上傳文件
    - Viewer：只能查詢一般文件（不含機密文件）
    """

    # 角色權限定義
    ROLE_PERMISSIONS = {
        UserRole.ADMIN: {
            "can_view_all": True,
            "can_upload": True,
            "can_delete": True,
            "can_manage_users": True,
            "can_view_stats": True,
            "can_view_confidential": True,
        },
        UserRole.EDITOR: {
            "can_view_all": False,
            "can_upload": True,
            "can_delete": False,
            "can_manage_users": False,
            "can_view_stats": False,
            "can_view_confidential": False,
        },

        UserRole.VIEWER: {
            "can_view_all": False,
            "can_upload": False,
            "can_delete": False,
            "can_manage_users": False,
            "can_view_stats": False,
            "can_view_confidential": False,
        },
    }

    @classmethod
    def check_permission(
        cls, role: UserRole, action: str
    ) -> bool:
        """檢查角色是否有特定權限"""
        permissions = cls.ROLE_PERMISSIONS.get(role, {})
        return permissions.get(action, False)

    @classmethod
    def filter_documents_by_role(
        cls, documents: list, user_role: UserRole
    ) -> list:
        """
        根據使用者角色過濾文件
        Admin 可看到所有文件；
        其他角色只能看到 access_roles 包含自己角色的文件。
        """

        if user_role == UserRole.ADMIN:
            return documents

        return [
            doc for doc in documents
            if user_role in doc.get("access_roles", [UserRole.VIEWER])
        ]

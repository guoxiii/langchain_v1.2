# src/agent/thread_manager.py
"""對話管理器 — 每個使用者的對話管家"""

from dotenv import load_dotenv
load_dotenv()

import uuid
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class ThreadInfo:
    """對話執行緒的資訊"""
    thread_id: str
    user_id: str
    title: str = "新對話"
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    message_count: int = 0

class ThreadManager:
    """
    對話管理器
    管理使用者的所有對話執行緒，
    就像一本通訊錄——記錄每段對話的基本資訊。
    """
    def __init__(self):
        # 在生產環境中，這裡應該用資料庫
        self._threads: dict[str, ThreadInfo] = {}

    def create_thread(self, user_id: str, title: str = "新對話") -> ThreadInfo:
        """建立新的對話執行緒"""
        thread_id = str(uuid.uuid4())
        thread = ThreadInfo(
            thread_id=thread_id,
            user_id=user_id,
            title=title,
        )

        self._threads[thread_id] = thread
        return thread

    def get_user_threads(self, user_id: str) -> list[ThreadInfo]:
        """取得使用者的所有對話"""
        user_threads = [
            t for t in self._threads.values()
            if t.user_id == user_id
        ]

        return sorted(
            user_threads,
            key=lambda t: t.last_active,
            reverse=True,
        )

    def update_thread_activity(self, thread_id: str) -> None:
        """更新對話的最後活動時間"""
        if thread_id in self._threads:
            self._threads[thread_id].last_active = datetime.now()
            self._threads[thread_id].message_count += 1

    def rename_thread(self, thread_id: str, new_title: str) -> None:
        """重新命名對話"""
        if thread_id in self._threads:
            self._threads[thread_id].title = new_title

    def delete_thread(self, thread_id: str) -> None:
        """刪除對話"""
        self._threads.pop(thread_id, None)

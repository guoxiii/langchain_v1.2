# ch16/composite_backend.py

from dotenv import load_dotenv
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore

load_dotenv()

# 建立複合 Backend：
# - /workspace/ 使用 StateBackend（暫存，每次對話獨立）
# - /memories/  使用 StoreBackend（持久化，跨對話保留）
composite_backend = lambda rt: CompositeBackend(
    default=StateBackend(rt),     # 預設用 StateBackend
    routes={
        "/memories/": StoreBackend(rt),  # /memories/ 路徑用 StoreBackend
    }
)

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="""你是一位助手。
重要規則：
- 將工作中的暫存資料寫到workspace目錄
- 將需要長期記住的資訊寫到memories目錄
""",
    backend=composite_backend,
    store=InMemoryStore(),
)

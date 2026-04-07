# ch16/sandbox_modal.py
# 注意：此範例需要 Modal 帳號和設定

from dotenv import load_dotenv
import modal
from deepagents import create_deep_agent
from langchain_modal import ModalSandbox

load_dotenv()

# 建立 Modal Sandbox
app = modal.App.lookup("my-deep-agent-app")
modal_sandbox = modal.Sandbox.create(app=app)
backend = ModalSandbox(sandbox=modal_sandbox)

# 建立帶有 Sandbox 的 Deep Agent
agent = create_deep_agent(
    model="google_genai:gemini-2.5-flash",
    system_prompt="你是一位 Python 開發助手，可以在沙盒中執行程式碼。",
    backend=backend,
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "請寫一個 Python 腳本計算費氏數列前 20 項，並執行它"}]}
)

# 用完記得關閉 Sandbox
modal_sandbox.terminate()

print(result["messages"][-1].text)

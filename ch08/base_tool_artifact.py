# ch08/base_tool_artifact.py
from dotenv import load_dotenv

load_dotenv()

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Tuple, Any

class ReportInput(BaseModel):
    department: str = Field(description="部門名稱")

class DepartmentReportTool(BaseTool):
    """產生部門月報的工具。"""
    name: str = "generate_report"
    description: str = "產生指定部門的月度報表，回傳摘要與完整數據。"
    args_schema: Type[BaseModel] = ReportInput
    response_format: str = "content_and_artifact"

    def _run(self, department: str) -> Tuple[str, Any]:
        """回傳 (content, artifact) 二元組。"""
        # 模擬報表資料
        report_data = {
            "department": department,
            "month": "2025-06",
            "headcount": 12,
            "budget_used": 850000,
            "budget_total": 1000000,
            "projects": [
                {"name": "專案 A", "status": "進行中", "progress": 75},
                {"name": "專案 B", "status": "已完成", "progress": 100},
                {"name": "專案 C", "status": "規劃中", "progress": 10},
            ]
        }

        content = (
            f"{department} 2025年6月報表摘要：\n"
            f"人數：{report_data['headcount']}人\n"
            f"預算使用率：{report_data['budget_used']/report_data['budget_total']*100:.0f}%\n"
            f"進行中專案：{sum(1 for p in report_data['projects'] if p['status'] == '進行中')} 個"
        )

        return content, report_data

# 測試
tool = DepartmentReportTool()
result = tool.invoke({"department": "研發部"})

print(result)
# create_sample_pdf.py
"""建立範例 PDF 文件，作為 RAG 練習的資料來源。"""
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def create_sample_pdf(filepath: str):
    """建立一份關於虛構公司政策的 PDF。"""
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4    

    # 為了簡化範例，使用英文 + 基本中文
    # 實際專案中可以註冊中文字體
    content_pages = [
        [
            "TechCorp Employee Handbook - Chapter 1: Company Overview",
            "",
            "TechCorp was founded in 2020 with a mission to democratize AI technology.",
            "Our headquarters is located in Taipei, Taiwan.",
            "We currently have over 500 employees across 3 offices.",
            "Our core values are: Innovation, Integrity, and Inclusion.",
            "",
            "TechCorp specializes in developing AI-powered solutions for enterprises.",
            "Our flagship product, SmartAssist, helps companies automate customer service.",
            "We also offer DataInsight, a business intelligence platform powered by LLMs.",
        ],
        [
            "Chapter 2: Leave Policy",
            "",
            "Annual Leave: All full-time employees are entitled to 15 days of annual leave.",
            "Sick Leave: Employees may take up to 30 days of sick leave per year.",
            "Personal Leave: Up to 7 days of personal leave are available.",
            "Parental Leave: New parents are entitled to 8 weeks of paid parental leave.",
            "",
            "Leave requests must be submitted at least 3 business days in advance.",
            "For emergencies, notify your supervisor as soon as possible.",
            "Unused annual leave can be carried over to the next year, up to 5 days.",
        ],
        [
            "Chapter 3: Remote Work Policy",
            "",
            "TechCorp supports a hybrid work model.",
            "Employees may work remotely up to 3 days per week.",
            "Remote work days must be pre-approved by your team lead.",
            "All remote workers must be available during core hours: 10 AM - 4 PM.",
            "",
            "Equipment: The company provides a laptop and one external monitor.",
            "Internet: A monthly stipend of TWD 500 is provided for internet costs.",
            "Coworking spaces: Employees may expense up to TWD 3000/month for coworking.",
        ],
        [
            "Chapter 4: Benefits and Compensation",
            "",
            "Health Insurance: Full coverage for employees and dependents.",
            "Dental and Vision: 80% coverage with a TWD 20000 annual cap.",
            "Life Insurance: 2x annual salary coverage.",
            "",
            "Retirement: Company matches 6% of salary for retirement contributions.",
            "Stock Options: Eligible employees receive stock options after 1 year.",
            "Annual Bonus: Based on company and individual performance, typically 2-4 months.",
            "",
            "Education: TWD 30000 annual budget for professional development.",
            "Conference: One international conference per year is sponsored.",
        ],
        [
            "Chapter 5: IT Security Policy",
            "",
            "All employees must use company-approved devices for work.",
            "Two-factor authentication (2FA) is mandatory for all company accounts.",
            "Passwords must be at least 12 characters with uppercase, lowercase, and numbers.",
            "Password rotation is required every 90 days.",
            "",
            "VPN must be used when accessing company resources remotely.",
            "Sharing credentials with others is strictly prohibited.",
            "Report any security incidents to security@techcorp.com within 24 hours.",
            "Violation of IT security policies may result in disciplinary action.",
        ],
    ]    

    for page_content in content_pages:
        y = height - 50

        for line in page_content:
            if line == "":
                y -= 15
            else:
                c.setFont("Helvetica-Bold" if "Chapter" in line or "Handbook" in line else "Helvetica", 
                          14 if "Chapter" in line or "Handbook" in line else 11)

                c.drawString(50, y, line)
                y -= 20

        c.showPage()    

    c.save()
    print(f"PDF created: {filepath}")

if __name__ == "__main__":
    os.makedirs("./documents", exist_ok=True)
    create_sample_pdf("./documents/techcorp_handbook.pdf")

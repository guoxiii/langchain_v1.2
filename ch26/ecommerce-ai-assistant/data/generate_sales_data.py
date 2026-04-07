# data/generate_sales_data.py

"""產生模擬銷售數據"""

import csv
import random
from datetime import datetime, timedelta

random.seed(42)

products = {
    "P001": {"name": "控油潔面凝膠", "price": 380},
    "P002": {"name": "保濕控油化妝水", "price": 420},
    "P003": {"name": "清爽防曬乳 SPF50+", "price": 520},
    "P004": {"name": "溫和卸妝水", "price": 350},
    "P005": {"name": "毛孔緊緻精華液", "price": 680},
    "P006": {"name": "舒緩修復面膜", "price": 180},
    "P007": {"name": "男士全效保濕霜", "price": 450},
    "P008": {"name": "美白淡斑精華", "price": 780},
}

channels = ["官網", "蝦皮", "momo", "實體門市"]
regions = ["台北", "台中", "台南", "高雄", "新竹"]
start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 12, 31)
rows = []

for _ in range(2000):
    date = start_date + timedelta(days=random.randint(0, 364))
    product_id = random.choice(list(products.keys()))
    product = products[product_id]
    quantity = random.randint(1, 5)

    # 夏天防曬和控油賣得更好
    month = date.month

    if month in [6, 7, 8] and product_id in ["P003", "P001", "P002"]:
        quantity += random.randint(1, 3)

    rows.append({
        "date": date.strftime("%Y-%m-%d"),
        "order_id": f"ORD-{random.randint(100000, 999999)}",
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "total_amount": product["price"] * quantity,
        "channel": random.choice(channels),
        "region": random.choice(regions),
        "customer_id": f"C{random.randint(1000, 9999)}",
    })

with open("data/sales_data.csv", "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ 已產生 {len(rows)} 筆銷售數據")

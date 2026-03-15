# API 使用指南

> 本文件說明如何串接本系統提供的 RESTful API，適用版本：`v1.2+`

---

## 目錄

- [快速開始](#快速開始)
- [認證方式](#認證方式)
- [端點總覽](#端點總覽)
- [請求與回應格式](#請求與回應格式)
- [錯誤代碼](#錯誤代碼)
- [範例程式碼](#範例程式碼)

---

## 快速開始

1. 取得 API 金鑰：前往 [開發者後台](https://example.com/dashboard) 申請
2. 安裝 SDK（可選）：
   ```bash
   pip install myservice-sdk
   ```
3. 發送第一個請求：
   ```bash
   curl -X GET https://api.example.com/v1/status \
     -H "Authorization: Bearer YOUR_API_KEY"
   ```

---

## 認證方式

所有 API 請求皆需在 Header 中帶入 Bearer Token：

```
Authorization: Bearer <YOUR_API_KEY>
```

> ⚠️ **注意**：API 金鑰請勿提交至版本控制系統，建議使用 `.env` 檔案搭配 `python-dotenv` 管理。

```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("API_KEY")
```

---

## 端點總覽

| 方法   | 路徑                     | 說明               | 需認證 |
|--------|--------------------------|-------------------|--------|
| GET    | `/v1/status`             | 服務健康檢查       | 否     |
| GET    | `/v1/products`           | 取得產品列表       | 是     |
| GET    | `/v1/products/{id}`      | 取得單一產品資訊   | 是     |
| POST   | `/v1/products`           | 建立新產品         | 是     |
| PUT    | `/v1/products/{id}`      | 更新產品資訊       | 是     |
| DELETE | `/v1/products/{id}`      | 刪除產品           | 是     |

---

## 請求與回應格式

### 請求範例（POST）

```http
POST /v1/products HTTP/1.1
Host: api.example.com
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json

{
  "name": "防汗止臭噴霧",
  "sku": "PURIFY-001",
  "price": 299,
  "stock": 100
}
```

### 成功回應

```json
{
  "status": "success",
  "data": {
    "id": "prod_abc123",
    "name": "防汗止臭噴霧",
    "sku": "PURIFY-001",
    "price": 299,
    "stock": 100,
    "created_at": "2026-03-15T10:00:00Z"
  }
}
```

### 分頁參數

列表端點支援以下 Query String 分頁參數：

| 參數       | 型別    | 預設值 | 說明             |
|------------|---------|--------|-----------------|
| `page`     | integer | 1      | 頁碼（從 1 起算）|
| `per_page` | integer | 20     | 每頁筆數（最大 100）|
| `sort`     | string  | `created_at` | 排序欄位  |
| `order`    | string  | `desc` | `asc` / `desc`  |

```bash
GET /v1/products?page=2&per_page=10&sort=price&order=asc
```

---

## 錯誤代碼

| HTTP 狀態碼 | 錯誤代碼              | 說明                   |
|-------------|----------------------|------------------------|
| 400         | `INVALID_PARAMS`     | 請求參數格式錯誤        |
| 401         | `UNAUTHORIZED`       | 未提供或無效的 API 金鑰 |
| 403         | `FORBIDDEN`          | 無此資源的操作權限      |
| 404         | `NOT_FOUND`          | 資源不存在              |
| 422         | `VALIDATION_ERROR`   | 資料驗證失敗            |
| 429         | `RATE_LIMIT`         | 請求頻率超過限制        |
| 500         | `INTERNAL_ERROR`     | 伺服器內部錯誤          |

錯誤回應格式：

```json
{
  "status": "error",
  "code": "VALIDATION_ERROR",
  "message": "欄位 'price' 必須為正整數",
  "details": {
    "field": "price",
    "value": -10
  }
}
```

---

## 範例程式碼

### Python

```python
import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.example.com/v1"
HEADERS = {
    "Authorization": f"Bearer {os.getenv('API_KEY')}",
    "Content-Type": "application/json",
}

def get_products(page: int = 1, per_page: int = 20) -> dict:
    response = requests.get(
        f"{BASE_URL}/products",
        headers=HEADERS,
        params={"page": page, "per_page": per_page},
    )
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    result = get_products()
    print(f"共 {len(result['data'])} 筆產品")
```

---

## 速率限制

- 一般方案：**60 次 / 分鐘**
- 進階方案：**300 次 / 分鐘**

超過限制時回應 `429 Too Many Requests`，Header 中會包含：

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1741996800
```

---

> 📮 技術支援：api-support@example.com  
> 📄 完整 API 參考：https://docs.example.com/api

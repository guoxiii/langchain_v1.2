# test_env.py
import os

from dotenv import load_dotenv
load_dotenv()

# 檢查 Google API Key 是否已設定
google_key = os.getenv("GOOGLE_API_KEY", "")

if google_key:
    # 只顯示前 8 個字元，保護金鑰安全
    print(f"✅ GOOGLE_API_KEY 已設定: {google_key[:8]}...")
else:
    print("❌ GOOGLE_API_KEY 未設定，請檢查 .env 檔案")

# 檢查 Anthropic API Key（選填）
anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")

if anthropic_key:
    print(f"✅ ANTHROPIC_API_KEY 已設定: {anthropic_key[:8]}...")
else:
    print("ℹ️  ANTHROPIC_API_KEY 未設定（選填，可稍後再設定）")

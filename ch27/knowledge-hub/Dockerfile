# 使用 Python 3.12 輕量版作為基礎映像檔
FROM python:3.12-slim

# 設定容器內的工作目錄
WORKDIR /app

# 安裝系統相依
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# 安裝 uv
RUN pip install uv

# 複製專案文件到容器內
COPY pyproject.toml .
COPY src/ src/
COPY ui/ ui/

# 安裝 Python 套件
RUN uv pip install --system -e .

# 建立資料目錄
RUN mkdir -p /app/data/uploads /app/data/chroma

# 預設暴露 Streamlit 埠號
EXPOSE 8501

# 容器啟動時預設執行的指令
CMD ["streamlit", "run", "ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
FROM python:3.9-slim

# 設定工作目錄
WORKDIR /app

# 先複製依賴文件並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製其餘所有程式碼 (包含 static 和 templates)
COPY . .

# 使用 gunicorn 啟動，並綁定系統提供的 $PORT
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
# 1. 使用 Python 官方鏡像
FROM python:3.11-slim

# 2. 設定程式碼在容器裡的位址
ENV APP_HOME /app
WORKDIR $APP_HOME

# 3. 先複製依賴清單並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 把目前的程式碼通通複製進去
COPY . .

# 5. 執行 Gunicorn，監聽 Cloud Run 指定的 PORT
# 注意：這裡的 main:app 代表 main.py 裡的 app 變數
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
import os
from flask import Flask, render_template, request, jsonify
# 1. 引入 GCP Firestore 零件
from google.cloud import firestore

app = Flask(__name__)

# 2. 初始化 Firestore 客戶端
db = firestore.Client()

# ==========================================
# 網頁路由 (Web Routes)
# ==========================================

@app.route('/')
def index():
    # 診斷：看看 Flask 目前認知的資料夾路徑在哪
    import os
    print(f"目前工作目錄: {os.getcwd()}")
    print(f"Templates 目錄是否存在: {os.path.exists('templates')}")
    return render_template('index.html')

@app.route('/fb')
def fb_page():
    return render_template('fb.html')

@app.route('/ig')
def ig_page():
    return render_template('ig.html')

# ==========================================
# API 介面 (Backend APIs)
# ==========================================

# 【寫入功能】接收網頁傳來的評價
@app.route('/api/submit_feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.json
        print(f"收到新評價: {data}")

        # 存入 Firestore 的 pet_reviews 集合
        doc_ref = db.collection('pet_reviews').document()
        doc_ref.set({
            'name': data.get('name', '匿名'),
            'nanny': data.get('nanny'),
            'content': data.get('content'),
            'stars': data.get('stars'),
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        return jsonify({"status": "success", "message": "雲端存檔成功！"}), 200
    except Exception as e:
        print(f"寫入錯誤: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# 【讀取功能】從雲端抓取所有評價
@app.route('/api/get_feedbacks', methods=['GET'])
def get_feedbacks():
    try:
        # 依照時間排序（最新的在上面）
        reviews_ref = db.collection('pet_reviews').order_by('timestamp', direction=firestore.Query.DESCENDING)
        docs = reviews_ref.stream()
        
        results = []
        for doc in docs:
            item = doc.to_dict()
            # 轉換 Firestore 的時間物件變成網頁看得懂的字串
            if 'timestamp' in item and item['timestamp']:
                item['time'] = item['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            else:
                item['time'] = "未知時間"
            results.append(item)
            
        return jsonify(results), 200
    except Exception as e:
        print(f"讀取錯誤: {e}")
        return jsonify({"error": str(e)}), 500

# ==========================================
# 啟動伺服器 (必須放在最下方)
# ==========================================




if __name__ == "__main__":
    # 設定 Port 8081
    port = int(os.environ.get("PORT", 8082))
    print(f"🚀 鏟屎官伺服器啟動在 http://127.0.0.1:{port}")
    # debug=True 會在你改代碼時自動重啟，開發很方便
    app.run(host="0.0.0.0", port=port, debug=True)
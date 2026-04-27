import os
from flask import Flask, render_template, request, jsonify
from google.cloud import firestore

app = Flask(__name__)

# 初始化 Firestore 客戶端
db = firestore.Client()

# ==========================================
# 網頁路由 (Web Routes)
# ==========================================

@app.route('/')
def index():
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

@app.route('/api/submit_feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "無效的數據"}), 400

        doc_ref = db.collection('pet_reviews').document()
        doc_ref.set({
            'name': data.get('name', '匿名'),
            'nanny': data.get('nanny'),
            'content': data.get('content', ''),
            'stars': int(data.get('stars', 0)),
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        return jsonify({"status": "success", "message": "雲端存檔成功！"}), 200
    except Exception as e:
        print(f"寫入錯誤: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/get_feedbacks', methods=['GET'])
def get_feedbacks():
    try:
        # 注意：若 Firestore 尚未建立 timestamp 索引，此處會報錯。
        # 如果報錯導致抓不到資料，請先移除 .order_by 部分測試
        reviews_ref = db.collection('pet_reviews').order_by('timestamp', direction=firestore.Query.DESCENDING)
        docs = reviews_ref.stream()
        
        results = []
        for doc in docs:
            item = doc.to_dict()
            if 'timestamp' in item and item['timestamp'] and hasattr(item['timestamp'], 'strftime'):
                item['time'] = item['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
            else:
                item['time'] = "未知時間"
            
            item['stars'] = int(item.get('stars', 0))
            item['id'] = doc.id
            results.append(item)
            
        return jsonify(results), 200
    except Exception as e:
        print(f"讀取錯誤: {e}")
        # 返回空陣列確保前端 renderNannies 不會崩潰
        return jsonify([]), 200

# ==========================================
# 啟動伺服器 (Cloud Run / Local 兼容)
# ==========================================

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
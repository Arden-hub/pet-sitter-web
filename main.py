from flask import Flask, render_template, request, jsonify
from google.cloud import firestore
import os

app = Flask(__name__)

# 初始化 Firestore
# 在 Cloud Run 環境下會自動偵測專案 ID
db = firestore.Client()

# --- 網頁路由 (GET) ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/nanny')
def nanny():
    return render_template('nanny.html')

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route('/fb')
def fb_page():
    return render_template('fb.html')

@app.route('/ig')
def ig_page():
    return render_template('ig.html')

# --- API 路由 (POST) ---

@app.route('/api/submit_feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.get_json()
        
        # 寫入 Firestore 集合名稱為 'feedbacks'
        db.collection('feedbacks').add({
            'nanny': data.get('nanny', '一般性建議'),
            'stars': data.get('stars', 5),
            'content': data.get('content'),
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({"status": "success", "message": "已成功儲存至 Firestore"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Cloud Run 會提供 PORT 環境變數，本地測試預設 8080
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
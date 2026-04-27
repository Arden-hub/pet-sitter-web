from flask import Flask, render_template, request, jsonify
from google.cloud import firestore
import os

app = Flask(__name__)

# 初始化 Firestore
db = firestore.Client()

# --- 1. 網頁頁面路由 (GET) ---

@app.route('/')
def index():
    # 對應 templates/index.html
    return render_template('index.html')

@app.route('/nanny')
def nanny():
    # 對應 templates/nanny.html (保母介紹)
    return render_template('nanny.html')

@app.route('/feedback')
def feedback():
    # 對應 templates/feedback.html (意見回饋)
    return render_template('feedback.html')

@app.route('/fb')
def fb_page():
    # 對應 templates/fb.html (FB 連結頁)
    return render_template('fb.html')

@app.route('/ig')
def ig_page():
    # 對應 templates/ig.html (IG 連結頁)
    return render_template('ig.html')

# --- 2. API 路由 (POST) ---

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
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
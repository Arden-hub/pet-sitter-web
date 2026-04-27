from flask import Flask, render_template, request, jsonify
from google.cloud import firestore

app = Flask(__name__)

# 初始化 Firestore 客戶端
# 在 Cloud Run 上執行時，它會自動抓取專案 ID
db = firestore.Client()

@app.route('/feedback')
def feedback_page():
    return render_template('feedback.html')

@app.route('/api/submit_feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.get_json()
        
        # 直接寫入 Firestore 的 'feedbacks' 集合
        db.collection('feedbacks').add({
            'nanny': data.get('nanny'),
            'stars': data.get('stars'),
            'content': data.get('content'),
            'timestamp': firestore.SERVER_TIMESTAMP  # 建議用伺服器時間
        })
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
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
    # 讀取評價並傳送到網頁
    try:
        # 從 'feedbacks' 集合中抓取所有資料，並依照時間由新到舊排序
        reviews_ref = db.collection('feedbacks').order_by('timestamp', direction=firestore.Query.DESCENDING)
        docs = reviews_ref.stream()

        # 整理資料：將評價按保母姓名分類
        # 格式會像：{"Mio": [{"stars": 5, "content": "很好"}, ...], "Nana": [...]}
        all_reviews = {}
        for doc in docs:
            data = doc.to_dict()
            nanny_name = data.get('nanny', '一般性建議')
            if nanny_name not in all_reviews:
                all_reviews[nanny_name] = []
            all_reviews[nanny_name].append(data)
        
        # 將整理後的評價傳給 templates/nanny.html
        return render_template('nanny.html', reviews=all_reviews)
    except Exception as e:
        print(f"抓取評價時發生錯誤: {e}")
        # 如果失敗（例如資料庫還沒建立），仍回傳空字典讓頁面正常顯示
        return render_template('nanny.html', reviews={})

@app.route('/feedback')
def feedback():
    # 對應 templates/feedback.html
    return render_template('feedback.html')

@app.route('/fb')
def fb_page():
    return render_template('fb.html')

@app.route('/ig')
def ig_page():
    return render_template('ig.html')

# --- 2. API 路由 (POST) ---

@app.route('/api/submit_feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.get_json()
        
        # 寫入 Firestore 集合
        db.collection('feedbacks').add({
            'nanny': data.get('nanny', '一般性建議'),
            'stars': int(data.get('stars', 5)), # 確保是數字
            'content': data.get('content'),
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # 這裡是本地測試用，Cloud Run 會自動讀取 PORT 環境變數
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
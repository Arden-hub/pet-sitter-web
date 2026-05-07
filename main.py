import os
import datetime
from flask import Flask, render_template, request, jsonify

# 引入 Firebase 相關套件
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# --- 0. 初始化 Firestore ---
# 在 Cloud Run 環境下，不需帶入任何參數即可自動授權
if not firebase_admin._apps:
    firebase_admin.initialize_app()

db = firestore.client()

# --- 1. Firestore 核心邏輯 (計算平均星數) ---
def load_reviews_summary():
    summary_dict = {}
    try:
        # 從 Firestore 抓取所有評價
        reviews_ref = db.collection('reviews')
        docs = reviews_ref.stream()

        for doc in docs:
            row = doc.to_dict()
            nanny = row.get('nanny', '一般意見')
            try:
                star = int(row.get('stars', 5))
            except:
                star = 5
                
            if nanny not in summary_dict:
                summary_dict[nanny] = {'total_stars': 0, 'count': 0}
            summary_dict[nanny]['total_stars'] += star
            summary_dict[nanny]['count'] += 1
        
        # 計算平均星數
        for name in summary_dict:
            data = summary_dict[name]
            data['avg'] = round(data['total_stars'] / data['count']) if data['count'] > 0 else 0
    except Exception as e:
        print(f"Firestore 讀取失敗: {e}")
        return {}
    return summary_dict

# --- 2. 網頁頁面路由 ---

@app.route('/')
def home():
    # 確保你有 templates/index.html
    return render_template('index.html')

@app.route('/nanny')
def nanny():
    reviews_summary = load_reviews_summary()
    return render_template('nanny.html', summary=reviews_summary)

@app.route('/feedback')
def feedback_page():
    nanny_name = request.args.get('nanny', '一般意見')
    return render_template('feedback.html', nanny_name=nanny_name)

# --- 3. API 路由 (寫入 Firestore) ---

@app.route('/api/submit_feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()
    nanny = data.get('nanny', '一般意見')
    stars = data.get('stars', 5)
    content = data.get('content', '')

    try:
        doc_data = {
            'nanny': nanny,
            'stars': int(stars),
            'content': content,
            'created_at': datetime.datetime.now(datetime.timezone.utc)
        }
        # 存入 Firestore
        db.collection('reviews').add(doc_data)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"寫入失敗: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route('/ig')
def ig_page():
    return render_template('ig.html')

@app.route('/fb')
def fb_page():
    return render_template('fb.html')

@app.route('/kiki_playergame')
def game_page():
    return render_template('kiki_playergame.html')

# --- 4. 啟動設定 ---
if __name__ == '__main__':
    # Cloud Run 會提供 PORT 環境變數
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
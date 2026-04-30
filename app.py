import os
import datetime
from flask import Flask, render_template, request, jsonify

# 引入 Firebase 相關套件
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# --- 0. 初始化 Firestore ---
# 在 Cloud Run 上，ApplicationDefault 會自動處理權限
if not firebase_admin._apps:
    try:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)
    except Exception as e:
        # 地端測試時，如果你有 service-account.json 也可以用以下方式：
        # cred = credentials.Certificate('path/to/your-key.json')
        # firebase_admin.initialize_app(cred)
        print(f"Firebase Init Info: {e}")

db = firestore.client()

# --- 1. Firestore 核心邏輯 (計算平均星數) ---
def load_reviews_summary():
    summary_dict = {}
    try:
        # 從 Firestore 的 'reviews' 集合抓取所有評價文件[cite: 1, 3]
        reviews_ref = db.collection('reviews')
        docs = reviews_ref.stream()

        for doc in docs:
            row = doc.to_dict()
            nanny = row.get('nanny', '一般意見')
            # 確保 stars 是整數，防止 CSV 時代留下的字串問題
            try:
                star = int(row.get('stars', 5))
            except:
                star = 5
                
            if nanny not in summary_dict:
                summary_dict[nanny] = {'total_stars': 0, 'count': 0}
            summary_dict[nanny]['total_stars'] += star
            summary_dict[nanny]['count'] += 1
        
        # 計算每位保母的平均星數[cite: 2, 3]
        for name in summary_dict:
            data = summary_dict[name]
            if data['count'] > 0:
                data['avg'] = round(data['total_stars'] / data['count'])
            else:
                data['avg'] = 0
    except Exception as e:
        print(f"Firestore 讀取失敗: {e}")
        return {}
    return summary_dict

# --- 2. 網頁頁面路由 (GET) ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/nanny')
def nanny():
    # 改為從 Firestore 彙整資料[cite: 2, 3]
    reviews_summary = load_reviews_summary()
    return render_template('nanny.html', summary=reviews_summary)

@app.route('/feedback')
def feedback_page():
    nanny_name = request.args.get('nanny', '一般意見')
    return render_template('feedback.html', nanny_name=nanny_name)

# --- 3. API 路由 (POST 寫入 Firestore) ---

@app.route('/api/submit_feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json()
    nanny = data.get('nanny', '一般意見')
    stars = data.get('stars', 5)
    content = data.get('content', '')

    try:
        # 準備存入 Firestore 的資料對象[cite: 1, 3]
        doc_data = {
            'nanny': nanny,
            'stars': int(stars),
            'content': content,
            'created_at': datetime.datetime.now(datetime.timezone.utc) # 加上時間戳記方便排序
        }
        
        # 存入名為 'reviews' 的集合中[cite: 1]
        db.collection('reviews').add(doc_data)
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"寫入 Firestore 失敗: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# --- 4. 啟動設定 ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
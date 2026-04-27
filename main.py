from flask import Flask, render_template, request, jsonify
from google.cloud import firestore
import os

app = Flask(__name__)
db = firestore.Client()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/nanny')
def nanny():
    try:
        reviews_ref = db.collection('feedbacks').order_by('timestamp', direction=firestore.Query.DESCENDING)
        docs = reviews_ref.stream()
        all_reviews = {}
        for doc in docs:
            data = doc.to_dict()
            name = data.get('nanny', '一般性建議')
            if name not in all_reviews: all_reviews[name] = []
            all_reviews[name].append(data)
        return render_template('nanny.html', reviews=all_reviews)
    except:
        return render_template('nanny.html', reviews={})

# --- 重點修改：支援 /feedback/Mio 這種寫法 ---
@app.route('/feedback')
@app.route('/feedback/<name>')
def feedback(name="一般性建議"):
    # 直接把名字傳給 HTML，不靠 JS 抓，這絕對不會失敗
    return render_template('feedback.html', nanny_name=name)

@app.route('/api/submit_feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.get_json()
        db.collection('feedbacks').add({
            'nanny': data.get('nanny'),
            'stars': 5,
            'content': data.get('content'),
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
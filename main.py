import os
from flask import Flask, render_template, request, jsonify
from google.cloud import firestore

app = Flask(__name__)
db = firestore.Client()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/nanny')
def nanny():
    return render_template('nanny.html')

@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

# API: 提交評價
@app.route('/api/submit_feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.json
        db.collection('pet_reviews').add({
            'nanny': data['nanny'],
            'stars': int(data['stars']),
            'content': data['content'],
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API: 獲取評價
@app.route('/api/get_reviews', methods=['GET'])
def get_reviews():
    try:
        docs = db.collection('pet_reviews').stream()
        reviews = [doc.to_dict() for doc in docs]
        return jsonify(reviews), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=False, host="0.0.0.0", port=port)
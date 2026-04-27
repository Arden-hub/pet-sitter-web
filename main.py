@app.route('/nanny')
def nanny():
    try:
        # 從 Firestore 抓取評價
        reviews_ref = db.collection('feedbacks').order_by('timestamp', direction=firestore.Query.DESCENDING)
        docs = reviews_ref.stream()
        
        nanny_stats = {} 
        
        for doc in docs:
            data = doc.to_dict()
            name = str(data.get('nanny', '')).strip()
            # 確保星星是數字
            try:
                stars = int(data.get('stars', 5))
            except:
                stars = 5
            
            content = data.get('content', '')

            if name and name not in nanny_stats:
                nanny_stats[name] = {'total_stars': 0, 'count': 0, 'latest_content': ''}
            
            if name in nanny_stats:
                nanny_stats[name]['total_stars'] += stars
                nanny_stats[name]['count'] += 1
                # 因為有排序，第一筆就是最新的留言
                if not nanny_stats[name]['latest_content']:
                    nanny_stats[name]['latest_content'] = content

        # 計算平均分
        for name in nanny_stats:
            avg = nanny_stats[name]['total_stars'] / nanny_stats[name]['count']
            nanny_stats[name]['avg_stars'] = round(avg, 1)
            nanny_stats[name]['display_stars'] = int(round(avg))

        # 注意這裡傳出去的名字是 stats
        return render_template('nanny.html', stats=nanny_stats)
    except Exception as e:
        print(f"Error: {e}")
        return render_template('nanny.html', stats={})

@app.route('/feedback/<name>')
def feedback(name="一般性建議"):
    return render_template('feedback.html', nanny_name=name)
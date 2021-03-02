import datetime
from kattis import find_all_history, find_all_user_ids, fetch_for_user, users_table
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)


@app.route('/')
def index():
    all_history = find_all_history()
    all_users = find_all_user_ids()
    
    today = datetime.date.today()
    yesterday = str(today - datetime.timedelta(days=1))
    today = str(today)
    
    history_today = [day for day in all_history if day['Date'] == today]
    history_yesterday = [day for day in all_history if day['Date'] == yesterday]
    
    def pts_day(user, history):
        for entry in history:
            if entry['UserId'] == user:
                return entry['Score']
        return 99999999
    
    pts_gain = {}
    for user in all_users:
        pts_gain[user] = max(0, pts_day(user, history_today) - pts_day(user, history_yesterday))
    
    gains = sorted(pts_gain.items(), key=lambda item: item[1])
    return render_template('index.html', users=all_users, gains=gains[:min(10, len(gains))])


@app.route('/view_stats/<uid>')
def view_stats(uid):
    history = [row for row in find_all_history() if row['UserId'] == uid]
    return render_template('view_stats.html', uid=uid, history=history)


@app.route('/api/add_user', methods=['POST'])
def add_user():
    data = request.form.to_dict()
    if 'uid' not in data:
        return jsonify({'status': 'error'})

    uid = data['uid']
    
    # Does user already exist?
    if any(row['fields']['UserId'] == uid for row in users_table.get_all()):
        return jsonify({'status': 'user already exists'})
    
    users_table.insert({'UserId': uid})
    fetch_for_user(uid)

    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(debug=True)

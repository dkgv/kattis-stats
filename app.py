import datetime
from kattis import fetch_for_user, stats_table, users_table
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)


@app.route('/')
def index():
    today = datetime.date.today()
    yesterday = str(today - datetime.timedelta(days=1))
    today = str(today)

    history_today, history_yesterday = [], []
    for day in stats_table.get_all_records():
        if day['Date'] == today:
            history_today.append(day)
        elif day['Date'] == yesterday:
            history_yesterday.append(day)

    def pts_day(user: str, history: list):
        for entry in history:
            if entry['UserId'] == user['UserId']:
                return entry['Score']
        return 99999999

    # Compute each user score gain from yesterday -> today
    all_users = users_table.get_all_records()
    pts_gain = {}
    for user in all_users:
        pts_gain[user['UserId']] = {
            'Score': max(0, pts_day(user, history_today) -
                         pts_day(user, history_yesterday)),
            'User': user
        }

    gains = sorted(pts_gain.items(),
                   key=lambda item: item[1]['Score'], reverse=True)
    gains = [{'User': gain[1]['User'], 'Score': gain[1]['Score']}
             for gain in gains]
    return render_template(
        'index.html',
        users=all_users,
        gains=gains[:min(10, len(gains))]
    )


@app.route('/view_stats/<uid>')
def view_stats(uid):
    history = [x for x in stats_table.get_all_records() if x['UserId'] == uid]
    return render_template('view_stats.html', uid=uid, history=history)


@app.route('/api/add_user', methods=['POST'])
def add_user():
    data = request.form.to_dict()
    if 'uid' not in data:
        return jsonify({'status': 'error'})

    uid = data['uid']

    # Check if URL was submitted
    kattis_url = 'https://open.kattis.com/users/'
    if uid.startswith(kattis_url):
        uid = uid.split(kattis_url)[1]

    # Does user already exist?
    if any(row['UserId'] == uid for row in users_table.get_all_records()):
        return jsonify({'status': 'user already exists'})

    profile = fetch_for_user(uid)
    users_table.insert({
        'UserId': uid,
        'Name': profile.name,
        'Country': profile.country,
        'CountryShort': profile.country_short,
        'University': profile.university,
        'UniversityShort': profile.university_short,
    })

    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(debug=True)

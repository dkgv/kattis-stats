import datetime
from kattis import fetch_for_user, find_all_history, find_all_users, users_table
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)


@app.route('/')
def index():
    fmt = '%-m/%d/%Y'
    today = datetime.date.today()
    yesterday = (today - datetime.timedelta(days=1)).strftime(fmt)
    today = today.strftime(fmt)

    history_today, history_yesterday = [], []
    for day in find_all_history()[1:]:
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
    all_users = find_all_users()
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
    history = [x for x in find_all_history() if x['UserId'] == uid]
    name = list(filter(lambda u: u['UserId'] == uid, find_all_users()))[
        0]['Name']
    now = history[-1]['Score']
    pts_last_week = now - history[-7]['Score']
    pts_last_month = now - history[-30]['Score']
    pts_last_year = now - history[-min(365, len(history) - 1)]['Score']
    avg_pts_per_day = (now - history[0]['Score']) / float(len(history))
    return render_template(
        'view_stats.html',
        name=name,
        uid=uid,
        history=history,
        pts_last_week=pts_last_week,
        pts_last_month=pts_last_month,
        pts_last_year=pts_last_year,
        avg_pts_per_day=avg_pts_per_day
    )


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
    if any(row['UserId'] == uid for row in find_all_users()):
        return jsonify({'status': 'user already exists'})

    profile = fetch_for_user(uid)
    users_table.append_row([
        uid,
        profile.name,
        profile.country,
        profile.country_short,
        profile.university,
        profile.university_short,
    ])

    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(debug=True)

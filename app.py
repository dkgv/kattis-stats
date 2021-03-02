from kattis import fetch_for_user, table
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/view_stats/<uid>')
def view_stats(uid):
    history = [row for row in table.get_all() if row['UserId'] == uid]
    return render_template('view_stats.html', history=history)


@app.route('/api/add_user', methods=['POST'])
def add_user():
    data = request.form.to_dict()
    if 'uid' not in data:
        return jsonify({'status': 'error'})
    fetch_for_user(data['uid'])
    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(debug=True)

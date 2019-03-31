# coding:utf-8
import sys
import json
from flask import Flask
from flask import request
from flask import render_template
from flask import make_response
from flask import redirect
from flask import url_for

sys.path.append('/root/travel_route')
import db

app = Flask(__name__)
user_accounts = {}


@app.route('/')
def handle_index():
    return render_template('index.html')


@app.route('/home')
def handle_home():
    global user_accounts
    user_name = request.args.get('user_name')
    if user_name not in user_accounts:
        return redirect(url_for('handle_index'))
    db_session = db.get_db_session()
    records = db_session.query(db.POIInfo).all()
    db_session.close()
    pois = []
    for poi in records:
        pois.append(
            {
                "name": poi.poi_name,
                "url": poi.poi_url,
                "image": poi.poi_image,
                "comment": poi.poi_comment,
                "time": poi.poi_time,
                "longitude": poi.poi_longitude,
                "latitude": poi.poi_latitude,
                "beauty": poi.poi_beauty,
                "leisure": poi.poi_leisure,
                "romance": poi.poi_romance,
                "excitement": poi.poi_excitement,
                "humanity": poi.poi_humanity
            }
        )
    return render_template('gaode.html', user_info=user_name, pois=json.dumps(pois))


@app.route('/login', methods=['POST'])
def handle_login():
    data = request.json
    user_name = data.get('user_name')
    password = data.get('password')
    db_session = db.get_db_session()
    user_record = db_session.query(db.POIUser).filter(db.POIUser.user_name == user_name).first()
    if not user_record:
        data = {
            'success': False,
            'msg': 'no user with name %s' % user_name
        }
        return make_response(json.dumps(data), 200)
    elif user_record.password != password:
        data = {
            'success': False,
            'msg': 'wrong password! '
        }
        return make_response(json.dumps(data), 200)
    data = {
        'success': True,
        'msg': 'ok'
    }
    user_accounts[user_name] = {
        'name': user_name,
        'poi_visited_num': user_record.poi_visited_num
    }
    return make_response(json.dumps(data), 200)


@app.route('/register', methods=['GET', 'POST'])
def handle_register():
    return render_template('register.html')


@app.route('/recommend', methods=['GET'])
def handle_recommend():
    poi_num = request.args.get('poi_range')
    travel_mode = request.args.get('travel_mode')
    position = request.args.get('position')


if __name__ == '__main__':
    app.jinja_env.variable_start_string = '{{ '
    app.jinja_env.variable_end_string = ' }}'
    app.run(
        host='0.0.0.0',
        port=80,
        debug=True
    )

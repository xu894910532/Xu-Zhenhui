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
web_distance_api = 'https://restapi.amap.com/v3/distance?key=be55c8b5ce093a6ddabd96184dc153c6'


def calculate_poi_score(user_info, poi):
    # 取出用户的喜好信息
    distance_sense = float(user_info['distance_sense'][0])
    beauty_like = float(user_info['beauty_like'][0])
    leisure_like = float(user_info['leisure_like'][0])
    romance_like = float(user_info['romance_like'][0])
    excitement_like = float(user_info['excitement_like'][0])
    humanity_like = float(user_info['humanity_like'][0])
    type_like = []
    for i in range(5):
        type_like.append(user_info['type{}_like'.format(i)][0])

    type_score = float(type_like[poi.cut_type]) / 5
    distance_score = distance_sense / distance_sense

    beauty_score = poi.poi_beaury * beauty_like
    leisure_score = poi.poi_leisure * leisure_like
    romance_score = poi.poi_romance * romance_like
    excitement_score = poi.poi_excitement * excitement_like
    humanity_score = poi.poi_humanity * humanity_like

    attribute_score = float(beauty_score + leisure_score + romance_score + excitement_score + humanity_score) / 100


def get_recommend_route(longitude, latitude, user_info, travel_mode, poi_num):
    db_session = db.get_db_session()
    poi_scores = []
    route = []
    for index in range(poi_num):

        # 一轮景点限制为 行程2h/景点数目
        if travel_mode == 'walking':
            poi_records = db_session.query(db.POIInfo).filter(
                db.POIInfo.poi_longitude <= longitude + 0.01 * 8 / poi_num,
                db.POIInfo.poi_latitude <= latitude + 0.013 * 8 / poi_num,
                db.POIInfo.poi_longitude >= longitude - 0.01 * 8 / poi_num,
                db.POIInfo.poi_latitude >= latitude - 0.013 * 8 / poi_num,
            ).all()
        elif travel_mode == 'riding':
            poi_records = db_session.query(db.POIInfo).filter(
                db.POIInfo.poi_longitude <= longitude + 0.04 * 8 / poi_num,
                db.POIInfo.poi_latitude <= latitude + 0.052 * 8 / poi_num,
                db.POIInfo.poi_longitude >= longitude - 0.04 * 8 / poi_num,
                db.POIInfo.poi_latitude >= latitude - 0.052 * 8 / poi_num,
            ).all()
        else:
            # driving
            poi_records = db_session.query(db.POIInfo).filter(
                db.POIInfo.poi_longitude <= longitude + 0.16 * 8 / poi_num,
                db.POIInfo.poi_latitude <= latitude + 0.208 * 8 / poi_num,
                db.POIInfo.poi_longitude >= longitude - 0.16 * 8 / poi_num,
                db.POIInfo.poi_latitude >= latitude - 0.208 * 8 / poi_num,
            ).all()
        for poi in poi_records:
            poi_scores.append(calculate_poi_score(user_info, poi))
        best_poi = poi_records[poi_scores.index(max(poi_scores))]
        route.append(str(best_poi.poi_longitude) + ',' + str(best_poi.poi_latitude))
        longitude, latitude = best_poi.poi_longitude, best_poi.poi_latitude
    return route


@app.route('/')
def handle_index():
    return render_template('index.html')


@app.route('/home')
def handle_home():
    global user_accounts
    user_info = {}
    user_name = request.args.get('user_name')
    if user_name not in user_accounts:
        return redirect(url_for('handle_index'))
    else:
        user_info['user_name'] = user_name
        user_info['poi_visited_num'] = request.args.get('poi_visited_num')
        user_info['distance_sense'] = request.args.get('distance_sense'),
        user_info['beauty_like'] = request.args.get('beauty_like'),
        user_info['leisure_like'] = request.args.get('leisure_like'),
        user_info['romance_like'] = request.args.get('romance_like'),
        user_info['excitement_like'] = request.args.get('excitement_like'),
        user_info['humanity_like'] = request.args.get('humanity_like'),
        user_info['type0_like'] = request.args.get('type0_like'),
        user_info['type1_like'] = request.args.get('type1_like'),
        user_info['type2_like'] = request.args.get('type2_like'),
        user_info['type3_like'] = request.args.get('type3_like'),
        user_info['type4_like'] = request.args.get('type4_like'),
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
    return render_template('home.html', user_info=user_info, pois=json.dumps(pois))


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
        'msg': 'ok',
        'poi_visited_num': user_record.poi_visited_num,
        'distance_sense': user_record.distance_sense,
        'beauty_like': user_record.beauty_like,
        'leisure_like': user_record.leisure_like,
        'romance_like': user_record.romance_like,
        'excitement_like': user_record.excitement_like,
        'humanity_like': user_record.humanity_like,
        'type0_like': user_record.type0_like,
        'type1_like': user_record.type1_like,
        'type2_like': user_record.type2_like,
        'type3_like': user_record.type3_like,
        'type4_like': user_record.type4_like,

    }
    user_accounts[user_name] = {
        'name': user_name
    }
    return make_response(json.dumps(data), 200)


@app.route('/register', methods=['GET', 'POST'])
def handle_register():
    return render_template('register.html')


@app.route('/recommend', methods=['POST'])
def handle_recommend():
    data = request.json
    # 拿到提交的参数
    poi_num = float(data.get('poi_range'))
    travel_mode = data.get('travel_mode')
    position = data.get('position')
    longitude = float(position['lng'])
    latitude = float(position['lat'])
    user_info = data.get('user_info')

    route = get_recommend_route(longitude, latitude, user_info, travel_mode, poi_num)

    data = {
        'success': True,
        'msg': 'ok',
        'route':json.dumps(route)
    }
    return make_response(json.dumps(data), 200)


if __name__ == '__main__':
    app.jinja_env.variable_start_string = '{{ '
    app.jinja_env.variable_end_string = ' }}'
    app.run(
        host='0.0.0.0',
        port=80,
        debug=True
    )

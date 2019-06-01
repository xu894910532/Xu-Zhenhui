# coding:utf-8
import sys
import json
import random
from flask import Flask
from flask import request
from flask import render_template
from flask import make_response
from flask import redirect
from flask import url_for
import requests

sys.path.append('/root/travel_route')
import db

app = Flask(__name__)
user_accounts = {}
web_distance_api = 'https://restapi.amap.com/v3/distance?key={}'
key_list = ['be55c8b5ce093a6ddabd96184dc153c6', 'b40b080a4c4d7139ef27d971215b306a', '0358408f30507797777473f12b7c7bdf']


def calculate_poi_score(longitude, latitude, user_info, poi):
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

    params = {
        'origins': str(longitude) + ',' + str(latitude),
        'destination': str(poi.poi_longitude) + ',' + str(poi.poi_latitude),
        'type': 3,
    }
    distance = float(requests.get(web_distance_api.format(random.sample(key_list, 1)[0]), params=params).json()['results'][0]['distance']) / 1000
    distance_score = distance_sense / distance if distance > 0.05 else 0

    print '[distance]', distance

    beauty_score = poi.poi_beauty or 2.78 * beauty_like
    leisure_score = poi.poi_leisure or 2.78 * leisure_like
    romance_score = poi.poi_romance or 2.78 * romance_like
    excitement_score = poi.poi_excitement or 2.78 * excitement_like
    humanity_score = poi.poi_humanity or 2.78 * humanity_like

    attribute_score = float(beauty_score + leisure_score + romance_score + excitement_score + humanity_score) / 100

    score_dict = {
        'beauty_score': beauty_score,
        'leisure_score': leisure_score,
        'romance_score': romance_score,
        'excitement_score': excitement_score,
        'humanity_score': humanity_score,
        'distance_score': distance_score,
        'distance': distance,
        'distance_sense': distance_sense
    }

    return type_score + distance_score + attribute_score, score_dict


def get_recommend_route(longitude, latitude, user_info, travel_mode, poi_num):
    db_session = db.get_db_session()
    route_score = {}
    route_lnglat = []
    score_dicts = []
    best_poi = None
    for index in range(int(poi_num)):
        poi_scores = []
        # 一轮景点限制为 行程2h/景点数目
        if travel_mode == 'walking':
            poi_records = db_session.query(db.POIInfo).filter(
                db.POIInfo.poi_longitude <= longitude + 0.01 * 8 / poi_num,
                db.POIInfo.poi_latitude <= latitude + 0.013 * 8 / poi_num,
                db.POIInfo.poi_longitude >= longitude - 0.01 * 8 / poi_num,
                db.POIInfo.poi_latitude >= latitude - 0.013 * 8 / poi_num,
                db.POIInfo.poi_name.notin_([poi_name for poi_name in route_score]),
            ).all()
        elif travel_mode == 'riding':
            poi_records = db_session.query(db.POIInfo).filter(
                db.POIInfo.poi_longitude <= longitude + 0.04 * 8 / poi_num,
                db.POIInfo.poi_latitude <= latitude + 0.052 * 8 / poi_num,
                db.POIInfo.poi_longitude >= longitude - 0.04 * 8 / poi_num,
                db.POIInfo.poi_latitude >= latitude - 0.052 * 8 / poi_num,
                db.POIInfo.poi_name.notin_([poi_name for poi_name in route_score]),
            ).all()
        else:
            # driving
            poi_records = db_session.query(db.POIInfo).filter(
                db.POIInfo.poi_longitude <= longitude + 0.16 * 8 / poi_num,
                db.POIInfo.poi_latitude <= latitude + 0.208 * 8 / poi_num,
                db.POIInfo.poi_longitude >= longitude - 0.16 * 8 / poi_num,
                db.POIInfo.poi_latitude >= latitude - 0.208 * 8 / poi_num,
                db.POIInfo.poi_name.notin_([poi_name for poi_name in route_score]),
            ).all()
        for poi in poi_records:
            if best_poi:
                poi_score, score_dict = calculate_poi_score(best_poi.poi_longitude, best_poi.poi_latitude, user_info, poi)
                poi_scores.append(poi_score)
                score_dicts.append(score_dict)
            else:
                poi_score, score_dict = calculate_poi_score(longitude, latitude, user_info, poi)
                poi_scores.append(poi_score)
                score_dicts.append(score_dict)
            print '[candidate_poi]', poi.poi_name.encode('utf-8')
        if not poi_records:
            return route_lnglat, route_score
        tmp_score = poi_scores[0]
        for score in poi_scores:
            if score > tmp_score and poi_records[poi_scores.index(score)].poi_name.encode('utf-8') not in route_score.keys():
                tmp_score = score
        best_poi = poi_records[poi_scores.index(tmp_score)]
        print '[best_poi]', best_poi.poi_name.encode('utf-8')
        route_score[best_poi.poi_name.encode('utf-8')] = score_dicts[poi_scores.index(tmp_score)]
        route_lnglat.append(str(best_poi.poi_longitude) + ',' + str(best_poi.poi_latitude))
        longitude, latitude = best_poi.poi_longitude, best_poi.poi_latitude
    return route_lnglat, route_score


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
                "image": poi.poi_image.split('?')[0],
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
    if request.method == 'GET':
        return render_template('register.html')
    else:
        data = request.json
        user_name = data.get('user_name')
        password = data.get('password')
        db_session = db.get_db_session()
        user_record = db_session.query(db.POIUser).filter(db.POIUser.user_name == user_name).first()
        db_session.close()
        if user_record:
            return make_response(json.dumps({
                'success': False,
                'msg': 'user_name already exists'
            }), 200)
        else:
            return make_response(json.dumps({
                'success': True,
            }), 200)


@app.route('/cold_start', methods=['GET', 'POST'])
def handle_cold_start():
    # 景点记录的db_id
    id_list = [1, 2, 3, 5, 38, 4, 6, 7, 11, 40]
    cut_types = [3, 2, 0, 1, 4, 0, 2, 3, 1, 4]
    if request.method == 'GET':
        user_info = {
            'user_name': request.args.get('user_name'),
            'password': request.args.get('password'),
        }
        db_session = db.get_db_session()
        records = db_session.query(db.POIInfo).filter(db.POIInfo.id.in_(id_list))
        pois = []
        index = 0
        for poi in records:
            pois.append(
                {
                    "name": poi.poi_name,
                    "url": poi.poi_url,
                    "image": poi.poi_image.split('?')[0],
                    "comment": poi.poi_comment or poi.poi_summary,
                    "id": id_list[index],
                    # "time": poi.poi_time,
                    # "longitude": poi.poi_longitude,
                    # "latitude": poi.poi_latitude,
                    # "beauty": poi.poi_beauty,
                    # "leisure": poi.poi_leisure,
                    # "romance": poi.poi_romance,
                    # "excitement": poi.poi_excitement,
                    # "humanity": poi.poi_humanity
                }
            )
            index += 1
        return render_template('cold_start.html', user_info=user_info, pois=json.dumps(pois))
    else:
        data = request.json
        print '[data]', data
        new_user = db.POIUser(data.get('user_name'), data.get('password'))
        new_user.poi_visited_num = 0
        new_user.distance_sense = data.get('distance_sense')
        new_user.beauty_like = data.get('beauty_like')
        new_user.leisure_like = data.get('leisure_like')
        new_user.romance_like = data.get('romance_like')
        new_user.excitement_like = data.get('excitement_like')
        new_user.humanity_like = data.get('humanity_like')
        new_user.type0_like, new_user.type1_like, new_user.type2_like, new_user.type3_like, new_user.type4_like = 0, 0, 0, 0, 0
        container1 = data.get('container1')
        container2 = data.get('container2')
        for id in container1:
            type = cut_types[id_list.index(int(id))]
            if type == 0:
                new_user.type0_like += 15 - container1.index(id) * 2.5
            elif type == 1:
                new_user.type1_like += 15 - container1.index(id) * 2.5
            elif type == 2:
                new_user.type2_like += 15 - container1.index(id) * 2.5
            elif type == 3:
                new_user.type3_like += 15 - container1.index(id) * 2.5
            elif type == 4:
                new_user.type4_like += 15 - container1.index(id) * 2.5
        for id in container2:
            type = cut_types[id_list.index(int(id))]
            if type == 0:
                new_user.type0_like += 15 - container2.index(id) * 2.5
            elif type == 1:
                new_user.type1_like += 15 - container2.index(id) * 2.5
            elif type == 2:
                new_user.type2_like += 15 - container2.index(id) * 2.5
            elif type == 3:
                new_user.type3_like += 15 - container2.index(id) * 2.5
            elif type == 4:
                new_user.type4_like += 15 - container2.index(id) * 2.5
        print '[new_user]', new_user
        data = {
            'success': True,
            'msg': 'ok',
            'poi_visited_num': new_user.poi_visited_num,
            'distance_sense': new_user.distance_sense,
            'beauty_like': new_user.beauty_like,
            'leisure_like': new_user.leisure_like,
            'romance_like': new_user.romance_like,
            'excitement_like': new_user.excitement_like,
            'humanity_like': new_user.humanity_like,
            'type0_like': new_user.type0_like,
            'type1_like': new_user.type1_like,
            'type2_like': new_user.type2_like,
            'type3_like': new_user.type3_like,
            'type4_like': new_user.type4_like,
        }
        db_session = db.get_db_session()
        db_session.add(new_user)
        db_session.commit()
        db_session.close()
        return make_response(json.dumps(data), 200)


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

    route, score = get_recommend_route(longitude, latitude, user_info, travel_mode, poi_num)
    total_score = {
        'beauty_score': 0.0,
        'distance_score': 0.0,
        'excitement_score': 0.0,
        'humanity_score': 0.0,
        'leisure_score': 0.0,
        'romance_score': 0.0,
    }
    if not route or len(route) < poi_num:
        data = {
            'success': False,
            'msg': '给定的条件下没有足够的景点！',
            'route': json.dumps(route),
        }
    else:
        data = {
            'success': True,
            'msg': 'ok',
            'route': json.dumps(route),
        }
    for k, v in score.items():
        total_score['beauty_score'] += round(v['beauty_score'], 2)
        total_score['distance_score'] += round(v['distance_score'], 2)
        total_score['excitement_score'] += round(v['excitement_score'], 2)
        total_score['humanity_score'] += round(v['humanity_score'], 2)
        total_score['leisure_score'] += round(v['leisure_score'], 2)
        total_score['romance_score'] += round(v['romance_score'], 2)
        total_score['distance'] = round(v['distance'], 2)
        total_score['distance_sense'] = round(v['distance_sense'], 2)
    print '[total_score]', total_score
    data['score'] = json.dumps(total_score)
    return make_response(json.dumps(data), 200)


@app.route('/paperpass', methods=['GET'])
def test_handler():
    if request.method == 'GET':
        return render_template('paperpass.html')


if __name__ == '__main__':
    app.jinja_env.variable_start_string = '{{ '
    app.jinja_env.variable_end_string = ' }}'
    app.run(
        host='0.0.0.0',
        port=80,
        debug=True
    )

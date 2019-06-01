# coding:utf-8
import copy
import db
import difflib
from crawler.poi_scores import poi_scores


def get_equal_rate(str1, str2):
    return difflib.SequenceMatcher(None, str1, str2).quick_ratio()


'''
poi_dicts = {}
scores = csv.reader(open('poi_scores.csv', 'r'))
for score in scores:
    if not score:
        continue
    record = score[0].split(' ')
    poi_dicts[record[0]] = {
        record[1].split(':')[0]: float(record[1].split(':')[1]),
        record[2].split(':')[0]: float(record[2].split(':')[1]),
        record[3].split(':')[0]: float(record[3].split(':')[1]),
        record[4].split(':')[0]: float(record[4].split(':')[1]),
        record[5].split(':')[0]: float(record[5].split(':')[1])
    }
with open('poi_scores.json', 'w') as poi_scores_file:
    json.dump(poi_dicts, poi_scores_file, ensure_ascii=False)
'''

new_poi_scores = copy.copy(poi_scores)
keys = new_poi_scores.keys()
db_session = db.get_db_session()
records = db_session.query(db.POIInfo).all()
for record in records:
    for key in keys:
        if get_equal_rate(record.poi_name.encode('utf-8'), key) >= 0.75:
            record.poi_beauty = new_poi_scores[key]['美丽']
            record.poi_leisure = new_poi_scores[key]['休闲']
            record.poi_romance = new_poi_scores[key]['浪漫']
            record.poi_excitement = new_poi_scores[key]['刺激']
            record.poi_humanity = new_poi_scores[key]['人文']
            print '[succeed] for record:', record.poi_name.encode('utf-8')
db_session.commit()
db_session.close()

# encoding=utf-8
import db

index = 0

try:
    db_session = db.get_db_session()
    pois = db_session.query(db.POIInfo).all()
    db_session.close()
    for poi in pois:
        poi_txt = ' '.join((poi.poi_name, poi.poi_comment, poi.poi_type, poi.poi_summary))
        index += 1
        try:
            print index, type(poi_txt), poi_txt[0:20]
            poi_file = open('poi_files/poi_%s.txt' % str(index), 'w')
            poi_file.write(poi_txt.encode("utf-8"))
            poi_file.flush()
            poi_file.close()
        except:
            pass
except:
    pass

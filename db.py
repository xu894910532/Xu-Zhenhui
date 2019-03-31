# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, Integer, Float, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class POIInfo(Base):
    __tablename__ = 'poi_info'

    id = Column(Integer(), primary_key=True)
    poi_id = Column(Integer())
    poi_name = Column(String(64))
    poi_url = Column(String(128))
    cut_type = Column(String(4))
    poi_latitude = Column(Integer())
    poi_longitude = Column(Integer())
    poi_location = Column(String(128))
    poi_comment = Column(String(1024))
    poi_time = Column(String(64))
    poi_image = Column(String(128))
    poi_type = Column(String(64))
    poi_summary = Column(String(1024))
    poi_beauty = Column(Float())
    poi_leisure = Column(Float())
    poi_romance = Column(Float())
    poi_excitement = Column(Float())
    poi_humanity = Column(Float())

    def __str__(self):
        return 'poi_id={}, poi_name={}, poi_url={}'.format(self.poi_id, self.poi_name, self.poi_url)


class POIUser(Base):
    __tablename__ = 'poi_user'

    id = Column(Integer(), primary_key=True)
    user_name = Column(String(64))
    password = Column(String(64))
    poi_visited_num = Column(Integer())

    def __str__(self):
        return 'user_name:{}, password:{}'.format(self.user_name, self.password)


def get_db_session():
    engine = create_engine('mysql+mysqlconnector://root:root@123.206.66.164:3306/mysql')
    DBSession = sessionmaker(bind=engine)
    return DBSession()


# db_session = get_db_session()
# records = db_session.query(POIInfo).all()
# for poi in records:
#     image_url = poi.poi_image.split('?')[0]
#     poi.poi_image = image_url
#     print image_url
# db_session.commit()
# db_session.close()

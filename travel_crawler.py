import requests
import db
import time
from bs4 import BeautifulSoup

user_agent = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Mobile Safari/537.36'
content_type = 'application/x-www-form-urlencoded; charset=UTF-8'
page_num = 12
has_more = 1
poi_url_prefix = 'http://www.mafengwo.cn'

headers = {
    'Accept': '*/*',
    "User-Agent": user_agent,
    # "Content-Type": content_type,
    # "Referer": 'http://www.mafengwo.cn/jd/10065/gonglve.html'
}
while has_more:
    res = requests.get('https://m.mafengwo.cn/jd/14674/gonglve.html?page={}&is_ajax=1'.format(page_num),
                       headers=headers)
    try:
        res_json = res.json()
    except Exception as e:
        print('Exception: ', e)
        print('res is not json, page_num=', page_num)
        print('res.text is below: \n', res.text)
        break
    html_content = res_json.get('html')

    # 确认是否还有数据
    has_more = int(res_json.get('has_more'))
    page_num += 1

    soup = BeautifulSoup(html_content, 'html.parser')
    poi_list = soup.find_all(class_='poi-li')
    for item in poi_list:
        poi_name = item.find(class_='hd').text if item.find(class_='hd') else ''
        poi_url = item.find('dl')['data-url'] if item.find('dl') else ''
        poi_id = int(poi_url.split('/')[-1][0:-19]) if len(poi_url)>20 else poi_url.split('/')[-1][0:-5]
        poi_image = item.find('img')['src'] if item.find('img') else ''
        poi_type = item.find(class_='m-t').text if item.find(class_='m-t') else ''
        poi_comment = item.find(class_='comment').text if item.find(class_='comment') else ''

        poi_obj = db.POIInfo(
            poi_id=poi_id,
            poi_name=poi_name,
            poi_url=poi_url_prefix + poi_url,
            poi_image=poi_image,
            poi_comment=poi_comment,
            poi_type=poi_type,
        )
        print('will add poi: ', poi_obj)

        try:
            db_session = db.get_db_session()
            if db_session.query(db.POIInfo).filter(db.POIInfo.poi_id == poi_id).first():
                print('poi already exists, id=', poi_id)
                continue
            db_session.add(poi_obj)
            db_session.commit()
        except Exception as e:
            print('Exception: ', e)
            break
        else:
            db_session.close() if db_session else None
            time.sleep(1)

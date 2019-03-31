# coding:utf-8
import requests
from bs4 import BeautifulSoup

user_agent = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Mobile Safari/537.36'
content_type = 'application/x-www-form-urlencoded; charset=UTF-8'
page_num = 0

headers = {
    'Accept': '*/*',
    "User-Agent": user_agent,
}


while page_num < 16:
    page_num += 1

    res = requests.get('http://www.ilvping.com/view/index/index/ac%3D104104101&p={}.html'.format(page_num),
                       headers=headers)
    res.encoding = 'utf-8'

    html = BeautifulSoup(res.content, 'html.parser')

    for poi in html.find_all('div', class_='attractionDetail'):
        poi_title = poi.find('a', class_='widget_second_title').text.strip()
        poi_star_score = poi.find('span', class_='star_score').text.strip()
        for score in poi.find_all('span'):
            if '美丽' in score.text.encode('utf-8') and len(score.text.encode('utf-8')) < 50:
                poi_beautiful = score.text.encode('utf-8').strip()
            elif '人文' in score.text.encode('utf-8') and len(score.text.encode('utf-8')) < 50:
                poi_humanity = score.text.encode('utf-8').strip()
            elif '休闲' in score.text.encode('utf-8') and len(score.text.encode('utf-8')) < 50:
                poi_entertainment = score.text.encode('utf-8').strip()
            elif '浪漫' in score.text.encode('utf-8') and len(score.text.encode('utf-8')) < 50:
                poi_romance = score.text.encode('utf-8').strip()
            elif '刺激' in score.text.encode('utf-8') and len(score.text.encode('utf-8')) < 50:
                poi_exciting = score.text.encode('utf-8').strip()
            elif '特色' in score.text.encode('utf-8') and len(score.text.encode('utf-8')) < 50:
                poi_feature = score.text.encode('utf-8').strip()
            else:
                continue
        print poi_title, poi_star_score, poi_beautiful, poi_humanity, poi_entertainment, poi_romance, poi_exciting, poi_feature
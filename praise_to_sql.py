# encoding: utf-8
"""
@version: 1.0
@author: WangNing
@license: GUN 
@contact: yogehaoren@gmail.com
@site: 
@software: PyCharm
@file: praise_to_sql.py
@time: 2018/7/11 20:50
@describe: 解析huml 至MYSQL 数据库
"""

import datetime
import re
from urllib.parse import urljoin


from bs4 import BeautifulSoup
import requests
from util import download_image

from util import get_md5
from get_video import get_m3u8_url
from util import insert_to_mysql, query_from_sql


header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36',
    'Host': 'www.52av.tv'
}


session = requests.Session()
session.headers = header


def prase_all_item(html, debug=False):
    temp_session = requests.Session()
    temp_session.headers = header
    pattern = re.compile('(\d{4}-\d{1,2}-\d{1,2})')
    soup = BeautifulSoup(html, 'lxml')
    li_list = soup.select('ul[class="ml waterfall cl"] li')
    for li in li_list:
        a = li.select('div[class="c cl"] a')[0]
        movie_url = urljoin('http://www.52av.tv', a['href'])
        image_url = a.select('img')[0]['src']
        title = a['title']
        span = li.select('div[class="auth cl"] span')
        try:
            issue_time = span[0]['title']
        except:
            content = li.select('div[class="auth cl"]')[0]
            res = pattern.findall(content.text)
            if len(res) > 0:
                issue_time = res[0]
            else:
                issue_time = datetime.datetime.now().strftime('%Y-%m-%d')
        movie_object_id = get_md5(movie_url)
        if query_from_sql(movie_object_id):
            continue
        image_path = download_image(image_url, movie_object_id)
        if not image_path:
            image_path = 'None'
        try:
            video_url = get_m3u8_url(temp_session, movie_url)
        except:
            video_url = None
        if not video_url:
            continue
        if debug:
            print('[*]', video_url)
        issue_time = datetime.datetime.strptime(issue_time, '%Y-%m-%d')
        parmars = (title, movie_url, image_url, image_path, issue_time, movie_object_id, video_url)
        insert_to_mysql(parmars)


if __name__ == '__main__':
    pass
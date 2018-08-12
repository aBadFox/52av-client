# encoding: utf-8
from bs4 import BeautifulSoup
import requests
import re

"""
@version: 0.1
@author: WangNing
@license: GUN 
@contact: yogehaoren@gmail.com
@site: 
@software: PyCharm
@file: get_video.py
@time: 2018/7/9 22:22
"""


def get_m3u8_url(session, url):
    '''
    获取影片流地址（m3u8文件）
    :param session:
    :param url:
    :return:
    '''
    response = session.get(url)
    soup1 = BeautifulSoup(response.text, "lxml")
    video_player_script = soup1.find_all(name='iframe', attrs={"src": re.compile(r'^http://video1.yocoolnet.com/')})
    for dd in video_player_script:
        ff = dd.get("src")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 4 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19',
            'Accept': 'text / html, application / xhtml + xml, application / xml;q = 0.9, image / webp, * / *;q = 0.8',
            'Host': 'video1.yocoolnet.com',
            'Proxy - Connection': 'keep - alive',
            'Referer': ff
        }
        res2 = session.get(ff, headers=headers)
        soup2 = BeautifulSoup(res2.text, "html.parser")
        gg = soup2.find_all("script")
        jj = str(gg)
        pattern = re.compile('.*(http://video1.yocoolnet.com/files/mp4/.*\.m3u8).*')
        result = pattern.findall(jj)
        if len(result) > 1 and isinstance(result[0], str):
            return result[0]
        else:
            return None

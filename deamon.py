# encoding: utf-8

"""
@version: 1.0
@author: WangNing
@license: GUN 
@contact: yogehaoren@gmail.com
@site: 
@software: PyCharm
@file: deamon.py
@time: 2018/7/11 22:39
@describe:  守护进程解析网页
"""

import multiprocessing
from praise_to_sql import prase_all_item
import time
import redis

REDIS_KEY = '52html'

try:
    conn = redis.Redis(host='192.168.1.108', port=6379, decode_responses=True)
except:
    conn = redis.Redis(host='localhost', port=6379, decode_responses=True)


def add_html(html):
    '''
    往redis添加待解析的网页
    :param html:
    :return:
    '''
    conn.rpush(REDIS_KEY, html)


def prase_html():
    '''
    每个网页解析6次
    :return:
    '''
    while True:
        if not conn.lpop(REDIS_KEY):
            break
    while True:
        html = conn.lpop(REDIS_KEY)
        if html:
            try:
                for i in range(6):
                    p = multiprocessing.Process(target=prase_all_item, args=(html, False))
                    p.start()
                    p.join(60)
                    if p.is_alive():
                        p.terminate()
            except:
                time.sleep(5)


if __name__ == '__main__':
    prase_html()
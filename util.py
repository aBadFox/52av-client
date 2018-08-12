# encoding: utf-8

"""
@version: 1.0
@author: WangNing
@license: GUN 
@contact: yogehaoren@gmail.com
@site: 
@software: PyCharm
@file: util.py
@time: 2018/7/10 23:25
@describe: 工具类一些常用的函数
"""

import hashlib
# import MySQLdb
import requests
import os
import time
import sqlite3

conn = sqlite3.connect("./52av.db")
cursor = conn.cursor()


def get_md5(url):
    '''
    根据网址求出MD5值 作为数据库的主键
    :param url:
    :return:
    '''
    if isinstance(url, str):
        url = url.encode('utf8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def download_image(url, name):
    '''
    下载封面图片
    :param url:
    :param name:
    :return:
    '''
    image_path = './image/{}.jpg'.format(name)

    def download_url(url):
        res = None
        try:
            res = requests.get(url)
        except:
            time.sleep(5)
        if res:
            return res
        else:
            return None
    response = download_url(url)
    if not response:
        response = download_url(url)
    if not response:
        return 'None'
    if not os.path.exists(image_path):
        if response.status_code == 200:
            with open(image_path, 'wb') as file:
                file.write(response.content)
        response.close()
    return image_path


def query_from_sql(movie_object_id):
    '''
    从数据库中查询影片地址
    :param movie_object_id:
    :return:
    '''
    try:
        sql = 'select movie.video_url, movie.title from main.movie where movie_object_id = \'{}\';'.format(movie_object_id, )
        cursor.execute(sql)
        data = cursor.fetchone()
        if data:
            return data[0]
        else:
            return None
    except:
        return None


def insert_to_mysql(parmars):
    '''
    把数据插入到sqlite3数据库中
    :param parmars:
    :return:
    '''
    if parmars[3] == 'None':
        image_path = download_image(parmars[2], parmars[5])
        if image_path:
            parmars = list(parmars)
            parmars[3] = image_path
            parmars = tuple(parmars)
    sql = 'INSERT INTO `main`.`movie` ' \
          '(`title`, `movie_url`, `image_url`, `image_path`, `issue_time`, `movie_object_id`, `video_url`) ' \
          'VALUES (\'{0}\', \'{1}\', \'{2}\', \'{3}\', \'{4}\', \'{5}\', \'{6}\') '.format(parmars[0], parmars[1],
                                                                                           parmars[2], parmars[3],
                                                                                           parmars[4], parmars[5],
                                                                                           parmars[6])
    cursor.execute(sql)
    conn.commit()

'''
对mysql适配 已弃用
'''
# user = '52av'
# passwd = '52av'
# database = '52av'
# conn = MySQLdb.connect("localhost", user, passwd, database, charset='utf8', use_unicode=True)
# cursor = conn.cursor()


# def query_from_sql(movie_object_id):
#     try:
#         sql = 'select video_url, title from movie where movie_object_id = %s '
#         cursor.execute(sql, (movie_object_id, ))
#         data = cursor.fetchone()
#         if data:
#             return data[0]
#         else:
#             return None
#     except:
#         return None
#     # return conn.commit()


# def insert_to_mysql(parmars):
#     if parmars[3] == 'None':
#         image_path = download_image(parmars[2], parmars[5])
#         if image_path:
#             parmars = list(parmars)
#             parmars[3] = image_path
#             parmars = tuple(parmars)
#     sql = 'INSERT INTO `52av`.`movie` ' \
#           '(`title`, `movie_url`, `image_url`, `image_path`, `issue_time`, `movie_object_id`, `video_url`) ' \
#           'VALUES (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE movie_url=values(movie_url)'
#     cursor.execute(sql, parmars)
#     conn.commit()


if __name__ == '__main__':
    print(query_from_sql('005ed038858f98c58a5a666fc9f585b'))
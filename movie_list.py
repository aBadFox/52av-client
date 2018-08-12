# -*- coding: utf-8 -*-
# Created by Acer on 2018/1/31

from urllib.parse import urljoin
import re
import datetime
from deamon import Client
from bs4 import BeautifulSoup

from util import get_md5

client = Client()


def prase_movie_list(base_url, html, movie_list, large):
    '''
    解析列表页 返回 影片信息
    :param base_url:
    :param html:
    :param movie_list:
    :param large:
    :return:
    '''
    pattern = re.compile('共\s*(\d+)\s*頁')
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
        image_path = 'None'
        issue_time = datetime.datetime.strptime(issue_time, '%Y-%m-%d')
        movie_list.append([title, movie_url, image_url, image_path, issue_time, movie_object_id])
    if large:
        large_num_label = soup.select('div[class="pg"] label span')
        try:
            if large_num_label:
                large_num = large_num_label[0]['title']
                large_result = pattern.findall(large_num)
                if large_result:
                    return large_result[0]
                else:
                    print('not found')
        except IndexError:
            print('未找到最大目录')
    else:
        return None


def get_movie_list(session, base_url, movie_list, large=False, deamon=None):
    '''
    解析所有影片地址
    :param session:requests 实例
    :param base_url: 基础url
    :param movie_list: 返回的解析后的结果
    :param large: 最大页数
    :param deamon 后台解析html类
    :return:
    '''
    movie_list.clear()
    try:
        result = session.get(base_url)
        print('[*] 当前网址 %s' % base_url)
        if result.status_code == 200:
            try:
                client.add_html(result.text)
            except:
                print("[!] 添加网页失败 请尝试 python3 server.py")
            return prase_movie_list(base_url, result.text, movie_list, large)
    except IndexError:
        print('error')

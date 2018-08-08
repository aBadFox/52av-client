# -*- coding: utf-8 -*-
# Created by Acer on 2018/1/31

import os
import multiprocessing

import requests

from movie_list import get_movie_list
# from download_plus import download_movie
from download import download_movie
from get_video import get_m3u8_url
from util import query_from_sql, insert_to_mysql
from deamon import prase_html

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36'
}

large = 330
session = requests.Session()
session.headers = header
proxies = {'http': 'socks5://127.0.0.1:1080', 'https': 'socks5://127.0.0.1:1080'}
session.proxies = proxies
base_url = 'http://www.52av.tv/forum.php?mod=forumdisplay&fid=67&filter=typeid&typeid=128&page={0}'
redirect_url = 'http://www.52av.tv/forum-64-{0}.html'
now_page = 1
redirect = False


def get_page_url():
    '''
    解析共多少页
    :return:
    '''
    if redirect:
        return redirect_url.format(str(now_page))
    else:
        return base_url.format(str(now_page))


def print_movie_list(movie_list):
    '''
    打印影片列表
    :param movie_list:
    :return:
    '''
    for i in range(len(movie_list)):
        print(i, ':', movie_list[i][0])
    print('[*] 当前页面', now_page, '  共', large, '页')


def test_redirect(url):
    '''
    测试网页是否跳转
    :return:
    '''
    global redirect
    if len(url) > 70:
        redirect = False
    else:
        redirect = True


def init_env_environment(display=False):
    '''
    初始化环境 创建 m3u8 output video 文件夹
    :return:
    '''
    global redirect
    dirs = ['output', 'm3u8', 'video', 'image', 'temp']
    for path in dirs:
        if not (os.path.exists(path) and os.path.isdir(path)):
            os.mkdir(path)
    for i in os.listdir('./video'):
        os.remove(os.path.abspath('./video/' + i))
    if os.path.exists('error.txt'):
        os.remove('error.txt')
    if display:
        print('[*] 环境初始化成功!')


if __name__ == '__main__':
    print('***************** 欢迎 进入 *****************')
    init_env_environment(True)
    movie_list = []
    deamon = multiprocessing.Process(target=prase_html, args=())
    try:
        deamon.start()
    except Exception:
        print('[!] 守护进程开启出错!')
        deamon = None
    large = get_movie_list(session, get_page_url(), movie_list, True,)
    test_redirect(movie_list[2][1])
    print_movie_list(movie_list)
    while True:
        init_env_environment(False)
        print('[*] 输入(q)：退出|输入(数字)：获取相应影片|输入(p)：跳转页面|输入(n)：下一页|输入(b)：前一页')
        cmd = input('[>] 请输入：')
        if cmd == 'q':
            if deamon:
                deamon.terminate()
            print('[!] Bye!')
            break
        elif cmd == 'b':
            if now_page > 1:
                now_page -= 1
                large = get_movie_list(session, get_page_url(), movie_list, True, )
                print_movie_list(movie_list)
        elif cmd == 'n':
            now_page += 1
            large = get_movie_list(session, get_page_url(), movie_list, True,)
            print_movie_list(movie_list)
        elif cmd == 'p':
            page_num = input('[>] 请输入页数：')
            if page_num.isnumeric():
                now_page = int(page_num)
                large = get_movie_list(session, get_page_url(), movie_list, True,)
                print_movie_list(movie_list)
            else:
                print('[!] 输入不合法！ 请重新输入')
        elif cmd.isnumeric():
            print('[*] 正在获取影片链接 请耐心等待(2min)')
            flag = False
            if int(cmd) > len(movie_list):
                print("[!] 输入错误 请重新输入")
                continue
            m3u8_url = query_from_sql(movie_list[int(cmd)][5])
            if not m3u8_url:
                flag = True
                try:
                    print('[*] 网页地址 ' + movie_list[int(cmd)][1])
                    m3u8_url = get_m3u8_url(session, movie_list[int(cmd)][1])
                except IndexError:
                    m3u8_url = None
            if m3u8_url:
                print('[*] 获取成功 ', m3u8_url)
                if flag:
                    ll = movie_list[int(cmd)]
                    ll.append(m3u8_url)
                    insert_to_mysql(tuple(ll))
                download_movie(m3u8_url, movie_list[int(cmd)][0])
            else:
                print("[!] 获取失败请更换资源或重新尝试!")
        else:
            print('[!] 输入不合法！ 请重新输入')

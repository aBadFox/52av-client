# encoding: utf-8

"""
@version: 1.1
@author: WangNing
@license: GUN 
@contact: yogehaoren@gmail.com
@site: 
@software: PyCharm
@file: download_plus.py
@time: 2018/8/12 9:29
@describe: 去除对redis 的依赖
"""
import multiprocessing
import os
import random
import re
import sys
import threading
import time
from urllib.parse import urljoin

import m3u8
import requests


BLOCK_SIZE = 1024
large = 100
download_over = False
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36'
}

# 下载进程计数
count_dict = {'count': 0}
# 下载错误链接
error_url_list = []
# http 实例
session = requests.Session()
session.headers = header
# 显示下载进度线程
process_bar_threading = None


def add_process_num(args=None):
    '''
    增加 count 的值
    :return:
    '''
    count_dict['count'] = count_dict['count'] + 1


def get_process_num(args=None):
    '''
    获取当前的键值
    :return:
    '''
    result = count_dict['count']
    if int(result) > 0:
        return int(result)
    else:
        return 0


def deduct_process_num(args=None):
    '''
    当前键值减一
    :return:
    '''
    if count_dict['count'] > 0:
        count_dict['count'] = count_dict['count'] - 1
    else:
        count_dict['count'] = 0


def threads_down_callback(args):
    '''
    线程下载 回调函数 用于记录错误链接 以及减少下载进程的数值
    :param args: 回调返回值， 为错误链接
    :return:
    '''
    deduct_process_num()
    add_error_url(args)


def add_error_url(url_list):
    '''
    添加错误链接
    :param url_list: 错误链接
    :return:
    '''
    for url in url_list:
        error_url_list.append(url)


def process_bar():
    '''
    :return: 显示下载进度
    '''
    while not download_over:
        start = 0
        now = len(os.listdir('./video'))
        end = large
        percentage = ((now - start) / (end - start))
        current = int(percentage * 50)
        s1 = '\r[*] [%s%s]%d%% %d' % ("*" * current, ' ' * int(50 - current), percentage*100, now)
        sys.stdout.write(s1)
        sys.stdout.flush()
        time.sleep(5)


def process_download(file_name, base_url,):
    '''
    分进程下载
    :param file_name: 文件名
    :param base_url:  基础ur
    :return:
    '''
    global large
    if not os.path.exists(file_name):
        time.sleep(2)
    m3u8_string = open(file_name, 'r').read()
    files = m3u8.loads(m3u8_string).files
    large = len(files)
    print('[*] 共 %d 个碎片' % large)
    process_bar_threading.start()
    pool = multiprocessing.Pool(processes=10)
    url_list = []
    for i in range(large):
        url_list.append((urljoin(base_url, files[i]), i))
        if len(url_list) == 10:
            add_process_num()
            pool.apply_async(func=threads_down, args=(url_list, ), callback=threads_down_callback)
            url_list = []

    pool.apply_async(func=threads_down, args=(url_list,), callback=threads_down_callback)
    pool.close()
    pool.join()
    return large


def threads_down(url_list,):
    '''
    进程内 开线程下载
    :param url_list: 下载链接列表
    :return:
    '''
    thread_list = []
    error_list = []
    for url, num in url_list:
        thread = threading.Thread(target=download, args=(url, num, error_list))
        thread_list.append(thread)
        thread.start()
    for th in thread_list:
        th.join()

    return error_list


def download(url, num, error_list):
    '''
    下载函数
    :param url: 下载链接
    :param num:  文件名
    :return:
    '''
    flag = True
    try:
        time.sleep(random.Random().randint(1, 3))
        result = requests.get(url, timeout=30, headers=header)
        if result.status_code == 200:
            with open('./video/%s.ts' % str(num), "wb") as file:
                file.write(result.content)
            result.close()
        else:
            flag = False
    except Exception as e:
        flag = False
    if not flag:
        time.sleep(2)
        error_list.append((url, num))


def join_temp_file(num, name):
    '''
    合并文件
    :param num: 文件最大数
    :param name:  文件名
    :return:
    '''
    global download_over
    download_over = True
    process_bar_threading.join()
    print()
    print('[*] 开始合并文件')
    temp_file_list = ['./video/'+file for file in os.listdir('./video') if re.match('\d+\.ts', file)]
    video_path = './output/'+name + '.ts'
    result_file = open(video_path, 'wb')
    for i in range(num+1):
        file = './video/'+str(i) + '.ts'
        if file in temp_file_list and os.path.isfile(''+file):
            with open(file, 'rb') as f:
                while True:
                    block = f.read(BLOCK_SIZE)
                    if block:
                        result_file.write(block)
                    else:
                        break
    result_file.close()
    print('[*] 合并完成')
    print('[*] 正在删除分段文件')
    for i in range(num+1):
        file = './video/' + str(i) + '.ts'
        if file in temp_file_list and os.path.isfile(file):
            os.remove(file)
    print('[*] 删除分段文件完成!')
    print('[*] 文件位置: %s' % os.path.abspath(video_path))


def download_error_url():
    '''
    下载出错连接
    :return:
    '''

    pool = multiprocessing.Pool(processes=10)

    def download_url(error_list):
        temp_urls_list = []
        for k in range(len(error_list)):
            temp_urls_list.append(url_list.pop())
            if len(temp_urls_list) == 10:
                pool.apply_async(threads_down, args=(temp_urls_list,), callback=threads_down_callback)
                temp_urls_list = []
        pool.apply_async(threads_down, args=(temp_urls_list,), callback=threads_down_callback)
    for i in range(2):
        url_list = []
        while len(error_url_list):
            url_list.append(error_url_list.pop())
        download_url(url_list)
    pool.close()
    pool.join()


def get_m3u8_list(url, file_name):
    '''
    获取m3u8流文件
    :param url: m3u8文件下载链接
    :param file_name m3u8文件名
    :return:
    '''
    print('[*] 开始下载m3u8文件 网址:%s' % url)
    try:
        file_name = './m3u8/'+file_name+'.m3u8'
        result = session.get(url)
        if result.status_code == 200:
            with open(file_name, 'w') as f:
                f.write(result.text)
                f.flush()
    except Exception:
        print('[!] 当下载'+url+'出现未知错误!')
    pattern = re.compile('(.*/).*\.m3u8')
    result = pattern.findall(url)
    if result:
        return result[0], file_name


def download_movie(url, name):
    '''
    下载视频
    :param url: m3u8 地址
    :param name: 文件名
    :return:
    '''

    global download_over, process_bar_threading
    download_over = False
    process_bar_threading = threading.Thread(target=process_bar, args=())
    if len(name) > 25:
        name = name[0:24]
    base_url, file_name = get_m3u8_list(url, name)
    large = process_download(file_name, base_url, )
    download_error_url()
    join_temp_file(large, name)


if __name__ == '__main__':
    download_movie('http://video1.yocoolnet.com/files/mp4/S/2/C/S2CGL.m3u8', 'test')
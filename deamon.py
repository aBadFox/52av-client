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
import socket
import re


class Client:
    def __init__(self,):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(('127.0.0.1', 8888))

    def add_html(self, html):
        '''
        往服务器添加网页
        :param html:
        :return:
        '''
        self.socket.send("--INSERT".encode())
        res = self.__get_all_content(self.socket)
        if res.strip() == "--OK!":
            content = html.encode()
            self.socket.send(("--LENGTH %d --" % len(content)).encode())
            self.socket.send(html.encode())
            self.socket.send("|over|".encode())

    def get_html(self):
        '''
        从服务器获得网页
        :return:
        '''
        pattern = re.compile("--LENGTH (\d+) --")
        self.socket.send("--POP".encode())
        res = self.__get_all_content(self.socket)
        if res.strip() == "--OK!":
            content = self.__get_all_content(self.socket)
            time.sleep(1)
            num = pattern.findall(content)
            if len(num):
                if int(num[0]) > 0:
                    return self.__get_all_content(self.socket, int(num[0]))
                else:
                    return None
        else:
            return None

    @staticmethod
    def __get_all_content(soc, length=0):
        '''
        获取socket连接所有内容
        :param soc:
        :param length:
        :return:
        '''
        if length == 0:
            content = ""
            while True:
                temp = soc.recv(1024).decode()
                if temp.endswith("|over|"):
                    content += temp
                    content = content.replace("|over|", "")
                    break
                if temp.startswith("--"):
                    content += temp
                    break
                content += temp
            return content
        if length > 0:
            temp = soc.recv(1024)
            while len(temp) <= length:
                temp += soc.recv(1024)
            content = temp.decode()
            content = content.replace("|over|", "")
            return content


def prase_html():
    '''
    每个网页解析6次
    :return:
    '''
    client = Client()
    while True:
        html = client.get_html()
        if html:
            try:
                for i in range(6):
                    p = multiprocessing.Process(target=prase_all_item, args=(html, False))
                    p.start()
                    p.join(60)
                    if p.is_alive():
                        p.terminate()
            except Exception as e:
                print(e)
                time.sleep(5)


if __name__ == '__main__':
    c = Client()

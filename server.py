# encoding: utf-8

"""
@version: 1.0
@author: WangNing
@license: GUN 
@contact: yogehaoren@gmail.com
@site: 
@software: PyCharm
@file: server.py
@time: 2018/8/12 14:00
@describe: 开启TCP服务器 存储网页 进行后续解析
"""
import socket
import threading
import re
import time


class Server:

    def __init__(self, debug=False):
        self.html_list = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.debug = debug

    def start(self):
        '''
        开启服务器
        :return:
        '''
        self.socket.bind(('127.0.0.1', 8888))
        self.socket.listen(5)

        while True:
            sock, addr = self.socket.accept()
            if self.debug:
                print("[debug] connect from ", addr)
                print("[debug] the len of html_list ", len(self.html_list))
            th = threading.Thread(target=self.__deal_connect, args=(sock,))
            th.start()

    def __save_html(self, html):
        '''
        保存网页
        :param html: 要存储的网页
        :return:
        '''
        self.html_list.append(html)

    def __pop_html(self):
        '''
        弹出网页
        :return:
        '''
        return self.html_list.pop()

    @staticmethod
    def __get_all_content(client, length=0):
        '''
        获取客户端内容
        :param client:
        :param length:
        :return:
        '''
        if length == 0:
            content = ""
            while True:
                temp = client.recv(1024).decode()
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
            temp = client.recv(1024)
            while len(temp) <= length:
                temp += client.recv(1024)
                # print(len(temp), length)
            print("[INFO] get html len is ", len(temp))
            content = temp.decode()
            content = content.replace("|over|", "")
            return content

    def __deal_connect(self, client):
            '''
            处理客户端提交的请求
            :param client:
            :return:
            '''
            try:
                pattern = re.compile("--LENGTH (\d+) --")
                while True:
                    content = self.__get_all_content(client)
                    if content.strip() == "--INSERT":
                        client.send("--OK!".encode())
                        content = self.__get_all_content(client)
                        num = pattern.findall(content)
                        if len(num):
                            html = self.__get_all_content(client, int(num[0]))
                            self.__save_html(html)
                    elif content.strip() == "--POP":
                        client.send("--OK!".encode())
                        time.sleep(1)
                        if len(self.html_list):
                            html = self.__pop_html().encode()
                            client.send(("--LENGTH %d --" % len(html)).encode())
                            if self.debug:
                                print("[INFO] send html len is ", len(html))
                            time.sleep(0.5)
                            client.send(html)
                            time.sleep(1)
                            client.send("|over|".encode())
                        else:
                            client.send("--LENGTH 0 --".encode())
                    elif content.strip() == "--QUIT":
                        if self.debug:
                            print("[debug] quit ", time.time())
                        break
                    else:
                        client.send('error!'.encode())
            except ConnectionResetError:
                print("[INFO] quit ", time.time())


if __name__ == '__main__':
    s = Server(True)
    s.start()
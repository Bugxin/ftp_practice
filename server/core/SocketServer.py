#!/usr/bin/env python
# -*- coding:utf-8 -*-

from socket import *
from threading import currentThread
import json

from core import MythreadPool
from conf import settings
from core import FtpServer


class SocketServer:
    def __init__(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.socket.bind((settings.IP, settings.PORT))
        self.socket.listen(settings.MAX_CONNECT)
        self.ftp = None  # 当前服务的ftp对象

    def communication(self, pool, conn):
        """
        通讯
        :param pool:
        :param conn:
        :return:
        """
        while 1:
            try:
                # print('线程is %s  fileno is %s' % (currentThread().getName(), conn.fileno()))
                raw_data = conn.recv(settings.BUFF_SIZE)
                if not raw_data:
                    print('connect lost....')
                    break
                data = json.loads(raw_data.decode('utf-8'))
                action_type = data.get('action_type')
                if action_type:
                    ftp = FtpServer.FtpServer()
                    if hasattr(ftp, action_type):
                        func = getattr(ftp, action_type)
                        func(data, conn)
            except ConnectionResetError:
                break
        # 当前线程执行完毕，就添加新的线程到 线程池(队列)
        pool.add_thread()
        conn.close()

    def connect(self):
        """
        建立socket连接
        :return:
        """
        pool = MythreadPool.MyThreadPool(settings.MAX_THREAD_NUM)
        print('start.....')
        while 1:
            self.request, self.client_addr = self.socket.accept()
            # print('(%s:%s) is requst server, fileno is %s' %
            #       (self.client_addr[0], self.client_addr[1], self.request.fileno()))

            # 每来一个新连接 就从线程池取一个线程执行任务
            thread = pool.get_thread()
            t = thread(target=self.communication, args=(pool, self.request))
            t.daemon = True
            t.start()

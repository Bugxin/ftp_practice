#!/usr/bin/env python
# -*- coding:utf-8 -*-

from core import SocketServer


def run():
    # 开启服务端
    server = SocketServer.SocketServer()
    server.connect()




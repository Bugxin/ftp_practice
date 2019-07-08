#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import logging

BASE_URL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 服务器配置
IP = '0.0.0.0'
PORT = 9989
MAX_CONNECT = 20  # 监听链接数

# 账户文件
ACCOUNT_FILE = '%s/conf/user.ini' % BASE_URL
HOME_DIR = '%s/home' % BASE_URL

BUFF_SIZE = 1024

# 日志配置
LOG_LEVEL = logging.INFO
LOG_PATH = '%s/logs' % BASE_URL

MAX_THREAD_NUM = 20  # 线程池大小

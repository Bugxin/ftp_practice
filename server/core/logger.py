#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import os

from conf import settings


def logger(logname):
    """
    :return:
    """
    # 创建 logger
    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL)

    # 设置文件级别
    if not os.path.exists(settings.LOG_PATH):
        os.makedirs(settings.LOG_PATH)
    file_name = '%s.log' % logname
    log_file = os.path.join(settings.LOG_PATH, file_name)
    f = open(log_file, 'w')  # 创建日志文件
    f.close()
    fh = logging.FileHandler(log_file)
    fh.setLevel(settings.LOG_LEVEL)

    # 创建 formatter
    formatter = logging.Formatter('%(asctime)s - %(module)s - %(levelname)s - %(message)s')

    # 添加 formatter 到FileHandler
    fh.setFormatter(formatter)

    # FileHandler添加到logger
    logger.addHandler(fh)

    return logger

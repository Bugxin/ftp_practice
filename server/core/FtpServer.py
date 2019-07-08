#!/usr/bin/env python
# -*- coding:utf-8 -*-


from configparser import ConfigParser
import json
import os


from conf import settings
from core import logger


log_obj = logger.logger('op')  # 用户操作日志


class FtpServer:
    def __init__(self):
        """
        初始化，创建socket， 读取配置文件
        """
        self.accounts = self._load_account_file()  # 加载账户文件

    def _load_account_file(self):
        """
        加载账户配置文件
        :return:
        """
        config_obj = ConfigParser()
        config_obj.read(settings.ACCOUNT_FILE)
        for user in config_obj.sections():
            home_path = config_obj[user]['home']
            # print(home_path)
            if not os.path.exists(home_path):
                os.makedirs(home_path)
        return config_obj

    def auth(self, data, conn):
        """
        用户身份验证
        :param data:
        :param conn:
        :return:
        """
        result = {}
        for user in self.accounts.sections():
            # 验证通过
            if user == data.get('username') and data.get('password') == self.accounts[user]['password']:
                print('welcom %s' % user)
                result['statu'] = 200
                result['home'] = self.accounts[user]['home']
                conn.send(json.dumps(result).encode('utf-8'))
                log_obj.info('%s login sucess' % user)
                return True
        # 验证失败
        result['statu'] = 201
        conn.send(json.dumps(result).encode('utf-8'))
        return False

    def get(self, data, conn):
        """
        下载文件 支持断点续传
        :param data:
        :param conn:
        :return:
        """
        # 只能下载家目录下的文件
        home_dir = settings.HOME_DIR + '\\' + data.get('user')
        filename = os.path.join(home_dir, data.get('filename'))
        result = {}

        if os.path.exists(filename):
            totalsize = os.path.getsize(filename)  # 文件总大小
            cursize = data.get('cursize')  # 已下载大小
            result['statu'] = 200
            result['totalsize'] = totalsize
            conn.send(json.dumps(result).encode('utf-8'))
            if cursize < totalsize:
                with open(filename, 'rb') as f:
                    f.seek(cursize)  # cursize不为0时 为断点续传
                    for line in f:
                        conn.send(line)
                log_obj.info('%s 下载文件:%s' % (data.get('user'), os.path.basename(filename)))
        else:
            result['statu'] = 201
            conn.send(json.dumps(result).encode('utf-8'))

    def put(self, data, conn):
        """
        上传
        :param data:
        :param conn:
        :return:
        """
        # 只能上传到家目录
        home_dir = settings.HOME_DIR + '\\' + data.get('user')
        filename = os.path.join(home_dir, data.get('filename'))
        result = {}
        if os.path.exists(filename):
            result['statu'] = 201
        else:
            result['statu'] = 200

        conn.send(json.dumps(result).encode('utf-8'))

        if result.get('statu') == 200:
            filesize = data.get('filesize')
            data_size = 0

            with open(filename, 'wb') as f:
                while data_size < filesize:
                    filedata = conn.recv(1024)
                    data_size += len(filedata)
                    f.write(filedata)
            log_obj.info('%s 上传了文件:%s' % (data.get('user'), data.get('filename')))

    def change_dir(self, data, conn):
        """
        切换工作目录
        :param data:
        :param conn:
        :return:
        """
        # print('change_dir fileno is %s' % conn.fileno())
        cmd_list = data.get('cmd').split()
        # print('====:', cmd_list, len(cmd_list))
        result = {}

        if len(cmd_list) == 1 and cmd_list[0] == 'ls':
            # ls 命令不传参时 是查看当前目录
            work_dir = data['work_dir']
            # print('change_dir: %s' % work_dir)
        if len(cmd_list) > 1:
            if cmd_list[1] == '..':  # 上一层目录
                work_dir = os.path.dirname(data['work_dir'])
            else:  # 绝对路径
                work_dir = cmd_list[1]

        if not os.path.exists(work_dir):
            # print('201')
            result['statu'] = 201
        else:
            # print('200')
            result['statu'] = 200
            if cmd_list[0] == 'cd':
                result['result'] = work_dir
            elif cmd_list[0] == 'ls':
                result['result'] = os.listdir(work_dir)

        conn.send(json.dumps(result).encode('utf-8'))

    def modify_quoto(self, data, conn):
        """
        修改用户配额
        :param data:
        :param conn:
        :return:
        """
        result = {}
        if data['user'] is None:
            result['statu'] = 201
        else:
            self.accounts.set(data['user'], 'quoto', data.get('quoto'))
            self.accounts.write(open(settings.ACCOUNT_FILE, 'w'))
            result['statu'] = 200
        conn.send(json.dumps(result).encode('utf-8'))











#!/usr/bin/env python
# -*- coding:utf-8 -*-

from socket import *
import json
import hashlib
import os
import sys


class FtpClient:
    op_list = [
        ('上传', 'put'),
        ('下载', 'get'),
        ('修改用户配额', 'modify_quoto'),
        ('切换工作目录', 'change_dir'),
        ('退出', 'exit')
    ]

    def __init__(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect(('127.0.0.1', 9989))
        self.user = None   # 当前用户
        self.home = None  # 家目录
        self.work_dir = None  # 当前用户的工作目录

    def auth(self):
        """
        登录验证
        :return:
        """
        num = 0
        while num < 3:
            user = input('user name:').strip()
            pwd = input('password:').strip()
            md5_obj = hashlib.md5()
            md5_obj.update(pwd.encode('utf-8'))
            pwd = md5_obj.hexdigest()

            cmd = {
                'action_type': 'auth',
                'username': user,
                'password': pwd
            }
            self.socket.send(json.dumps(cmd).encode('utf-8'))
            # print('auth fileno is %s' % self.socket.fileno())
            res = self.socket.recv(1024)
            res = json.loads(res.decode('utf-8'))
            if res['statu'] == 200:
                self.user = user
                self.home = res['home']
                self.work_dir = self.home  # 初始工作目录 等于 家目录
                return True
            num += 1
        return False

    def get(self):
        """
        下载文件
        :return:
        """
        filename = input('下载的文件名:').strip()
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        if os.path.exists(filepath):
            # print('续传。。。')
            data_size = os.path.getsize(filepath)  # 文件已下载大小 用于续传
        else:
            data_size = 0

        cmd = {
            'action_type': 'get',
            'user': self.user,
            'filename': os.path.basename(filepath),
            'cursize': data_size  # 当前已下载大小
        }
        self.socket.send(json.dumps(cmd).encode('utf-8'))
        ret = self.socket.recv(1024)
        ret = json.loads(ret.decode('utf-8'))
        # print('ret:', ret)
        if ret.get('statu') == 200:
            total_size = ret.get('totalsize')
            # 已下载大小与文件总大小比较，决定是否要续传
            if data_size == total_size:
                print('\033[31m下完了 不用续传\033[0m')
            else:
                with open(cmd.get('filename'), 'ab') as f:
                    # 续传时data_size必然不为0，新文件下载data_size为0
                    f.seek(data_size)
                    while data_size < total_size:
                        data = self.socket.recv(1024)
                        f.write(data)
                        data_size += len(data)
                        self.show_process(data_size, total_size)
                print('\n')

        else:
            print('下载失败')

    def put(self):
        """
        上传文件
        :return:
        """
        filename = input('上传的文件名，包含绝对路径:').strip()

        if not os.path.exists(filename):
            print('上传的文件不存在')
            return

        cmd = {
            'action_type': 'put',
            'user': self.user,
            'filename': os.path.basename(filename),
            'filesize': os.path.getsize(filename)
        }
        self.socket.send(json.dumps(cmd).encode('utf-8'))
        ret = self.socket.recv(1024)
        ret = json.loads(ret.decode('utf-8'))
        # print('ret:', ret)
        if ret.get('statu') == 200:
            with open(filename, 'rb') as f:
                cur_size = 0
                for line in f:
                    self.socket.send(line)
                    cur_size += len(line)
                    self.show_process(cur_size, cmd.get('filesize'))
            print('\n')
        else:
            print('\033[31m上传失败\033[0m')

    def modify_quoto(self):
        """
        修改用户配额空间
        :return:
        """
        quoto = input('设置配额空间大小:').strip()

        cmd = {
            'action_type': 'modify_quoto',
            'user': self.user,
            'quoto': quoto
        }

        self.socket.send(json.dumps(cmd).encode('utf-8'))
        ret = self.socket.recv(1024)
        ret = json.loads(ret.decode('utf-8'))
        if ret.get('statu') == 200:
            print('\033[31m修改成功\033[0m')
        else:
            print('\033[31m 修改失败 \033[0m')

    def show_process(self, cur, total):
        """
        显示进度，已下载部分用'#’填充，未下载部分用' '填充，总长度固定20字节
        :return:
        """
        percent = float(cur)/total  # 进度百分比
        percent_num = int(20*percent)   # 以20个'#'作总长度
        resulf = '\r当前进度:[{}{}]{}%'.format('#'*percent_num, ' '*(20 - percent_num), percent*100)
        sys.stdout.write(resulf)
        sys.stdout.flush()

    def change_dir(self):
        """
        切换目录, 支持 cd ，ls命令
        :return:
        """
        op_menu = """
cd命令格式:cd .. 或者 cd 绝对路径
ls命令格式:ls 或者 ls 绝对路径
"""
        while 1:
            print(op_menu)
            user_input = input('输入命令，q退出：').strip()
            if user_input == 'q':
                break

            cmd = user_input.split()[0]
            if cmd not in ['ls', 'cd']:
                print('\033[31m格式不对\033[0m')
                continue

            res = {
                'action_type': 'change_dir',
                'user': self.user,
                'work_dir': self.work_dir,
                'cmd': user_input,
            }

            self.socket.send(json.dumps(res).encode('utf-8'))
            # print('bbbbb, fileno is %s' % self.socket.fileno())
            ret = self.socket.recv(1024)
            ret = json.loads(ret.decode('utf-8'))
            # print('ret ：', ret)
            if ret.get('statu') == 200:
                result = ret.get('result')
                if isinstance(result, list):
                    # ls 命令返回结果是列表类型，cd命令是str
                    print('\033[31m 当前文件夹下有:%s \033[0m' % ret.get('result'))
                else:
                    self.work_dir = ret.get('result')
                    print('\033[31m 目录切换成功，当前工作目录为:%s \033[0m' % self.work_dir)

            else:
                print('切换目录失败')

    def interactive(self):
        """
        服务器交互接口
        :return:
        """
        if self.auth():
            while 1:
                for op_id, item in enumerate(self.op_list, 1):
                    print(op_id, item[0])
                user_input = input('输入编号:').strip()
                func_str = self.op_list[int(user_input) - 1][1]
                if hasattr(self, func_str):
                    func = getattr(self, func_str)
                    func()
        else:
            print('try too many times!!!')

    def exit(self):
        print('Bye %s' % self.user)
        exit()


if __name__ == '__main__':
    client = FtpClient()
    client.interactive()

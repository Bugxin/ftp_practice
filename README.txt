﻿-----------------FTP文件传输系统
实现功能:
1. 用户加密认证
2. 允许多用户登录
3. 每个用户都有自己的家目录
4. 对用户进行磁盘分配，上传时空间判断未做
5. 允许用户在ftp server上随意切换目录
6. 允许用户查看工作目录下的文件
7. 允许用户上传和下载 只能上传或下载到用户自己的家目录
8. 文件上传、下载过程中显示进度条
9. 断点下载
10.用户操作日志记录
11.支持并发
12.用队列实现了线程池
13.支持配置并发数


登录说明
用户名: home目录下的文件名
密码: 统一为123

上传下载说明
文件需要放在用户home目录 如home/alex目录下  测试时需要自己准备文件 


服务端

|----bin    可执行文件
|   |
|   |---- start.py   程序起始
|-----conf
|   |---- settings.py  系统配置文件
|   |---- user.ini 用户配置
|
|-----core     核心逻辑
|   |
|   |----FtpServer.py   ftp服务逻辑 如:上传 下载
|   |----logger.py     日志格式处理
|   |----main.py        程序入口
|   |----MythreadPool.py  线程池实现
|   |----SocketServer.py  处理socket通讯，支持并发
|
|
|------home  家目录
|   |--alex  以用户名命令的用户空间目录 保存用户各种资料
|	
|
|----logs 操作日志目录

流程图：
https://www.processon.com/view/link/5c4327dfe4b056ae29f5e88b

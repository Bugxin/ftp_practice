#!/usr/bin/env python
# -*- coding:utf-8 -*-


import queue
from threading import Thread
import os


class MyThreadPool:
    def __init__(self, max_workers=None):
        if max_workers is None:
            max_workers = (os.cpu_count() or 1) * 5  # 默认CPU核数*5
        self.work_queue = queue.Queue(max_workers)
        for i in range(max_workers):
            self.work_queue.put(Thread)

    def get_thread(self):
        return self.work_queue.get()

    def add_thread(self):
        self.work_queue.put(Thread)


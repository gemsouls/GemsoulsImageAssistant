# -*- coding: utf-8 -*-
# @CreateTime : 2021/12/13 15:09
# @Author     : 潘其威(PanEa)
# @Company    : Gemsouls
# @File       : load_test.py
# @Description:
# @LastEditBy :


import argparse
import asyncio
import datetime
import os
from os.path import join, dirname, abspath, exists
import requests
import sys
import time
import threading
from typing import *

import aiohttp

ROOT = dirname(dirname(dirname(abspath(__file__))))
sys.path.insert(0, ROOT)


async def send_messages_concurrently(url: str, num_messages: int = 10):
    async def send_task(task_id, session):
        start_time = datetime.datetime.now()
        async with session.post(
            os.path.join(url, "propose"),
            json={
                "task_id": task_id,
                "image": "",
            },
            headers={'content-type': 'application/json'}
        ) as response:
            res = await response.json()
        finish_time = datetime.datetime.now()
        print(f"task-{task_id} using {(finish_time-start_time).total_seconds(): .4f}s")
        print(res)

    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            *[send_task(task_id, session) for task_id in range(num_messages)]
        )


def send_message_every_n_seconds(url: str, num_messages: int = 10, n: float = 0.2):
    def post_message(post_id):
        start_time = datetime.datetime.now()
        response = requests.post(
            os.path.join(url, "propose"),
            json={
                "task_id": task_id,
                "image": "",
            },
            verify=False,
            headers={'content-type': 'application/json'}
        )
        finish_time = datetime.datetime.now()
        res = response.json()
        print(f"task-{post_id} using {(finish_time-start_time).total_seconds(): .4f}s")
        print(res)

    threads = []

    for task_id in range(num_messages):
        t = threading.Thread(target=post_message, args=(task_id,), daemon=True)
        t.start()
        threads.append(t)
        time.sleep(n)

    for t in threads:
        t.join()

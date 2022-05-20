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
import random
import re
import requests
import sys
import time
import threading
from typing import *

import aiohttp

ROOT = dirname(dirname(dirname(abspath(__file__))))
sys.path.insert(0, ROOT)


def get_fb_log_images():
    images = []
    for root, ds, fs in os.walk(join(ROOT, "gia_test/test_src/images/fb_log_images_211208")):
        for f in fs:
            if re.match(r".*\.png", f):
                fullname = os.path.join(root, f)
                images.append(fullname)
    return images


async def send_messages_concurrently(url: str, num_messages: int = 10):
    async def send_task(task_id, img_path, session):
        start_time = datetime.datetime.now()
        async with session.post(
            url,
            json={
                "task_id": task_id,
                "image_url": img_path,
            },
            headers={'content-type': 'application/json'}
        ) as response:
            res = await response.json()
        finish_time = datetime.datetime.now()
        print(f"task-{task_id} [{img_path}] using {(finish_time-start_time).total_seconds(): .4f}s")
        print(res)

    image_paths = random.sample(get_fb_log_images(), num_messages)

    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            *[send_task(task_id, img_path, session) for task_id, img_path in enumerate(image_paths)]
        )


def send_message_every_n_seconds(url: str, num_messages: int = 10, n: float = 0.2):
    def post_message(post_id, img_path):
        start_time = datetime.datetime.now()
        response = requests.post(
            url,
            json={
                "task_id": task_id,
                "image_url": img_path,
            },
            verify=False,
            headers={'content-type': 'application/json'}
        )
        finish_time = datetime.datetime.now()
        res = response.json()
        print(f"task-{post_id} [{img_path}] using {(finish_time-start_time).total_seconds(): .4f}s")
        print(res)

    threads = []
    image_paths = get_fb_log_images()
    for task_id, img_path in enumerate(random.sample(image_paths, num_messages)):
        t = threading.Thread(target=post_message, args=(task_id, img_path), daemon=True)
        t.start()
        threads.append(t)
        time.sleep(n)

    for t in threads:
        t.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0"
    )
    parser.add_argument(
        "--port",
        type=str,
        default="6006"
    )
    parser.add_argument(
        "--route",
        type=str,
        default="image2text"
    )
    parser.add_argument(
        "--msg_num",
        type=int,
        default=10
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.1
    )
    parser.add_argument(
        "--test_sequentially",
        action="store_true"
    )
    parser.add_argument(
        "--test_concurrently",
        action="store_true"
    )
    args = parser.parse_args()
    url = "http://" + args.host + ":" + args.port + f"/{args.route}"

    if args.test_sequentially:
        send_message_every_n_seconds(
            url, args.msg_num, args.interval
        )

    if args.test_concurrently:
        send_messages_concurrently(
            url, args.msg_num
        )

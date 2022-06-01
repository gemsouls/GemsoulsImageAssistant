# -*- coding: utf-8 -*-
# @CreateTime : 2021/12/13 15:09
# @Author     : 潘其威(PanEa)
# @Company    : Gemsouls
# @File       : load_test.py
# @Description:
# @LastEditBy :


import argparse
import asyncio
import base64
import copy
import datetime
import glob
import io
import os
import random
import re
import sys
import threading
import time
from os.path import abspath, dirname, exists, join
from typing import *

import aiohttp
import cv2 as cv
import numpy as np
import requests
from PIL import Image

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


def img2base64(img):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    buffered.seek(0)
    img_byte = buffered.getvalue()
    img_str = base64.b64encode(img_byte).decode()
    return img_str


def cv_preprocess(image):
    image = cv.cvtColor(np.array(image, dtype=np.uint8), cv.COLOR_RGB2BGR)
    resize = (384, 384)
    # resize = (224, 224)
    image = cv.resize(image, dsize=resize, interpolation=cv.INTER_CUBIC)
    image_str = base64.b64encode(cv.imencode(".png", image)[1].tobytes()).decode("utf-8")
    return image_str


def pil_preprocess(image, resize=(384, 384)):
    if image.mode != "RGB":
        image = image.convert("RGB")

    imr = image.resize(resize, resample=Image.BILINEAR)
    image_str = img2base64(imr)
    return image_str


def random_sample_images(num_messages):
    image_pkl_lst = glob.glob("gia_test/test_img/*.pkl")
    image_paths = random.sample(image_pkl_lst, num_messages)
    return image_paths


def read_images_base64_str(image_fpath):
    with open(image_fpath, "rb") as f:
        data = f.read()
    image = Image.open(io.BytesIO(data))
    return pil_preprocess(image)


async def send_messages_concurrently(url: str, num_messages: int = 10, verbose: bool = False):
    async def send_task(task_id, img_path, session):
        start_time = datetime.datetime.now()

        image_str = read_images_base64_str(img_path)
        if image_str is None:
            return ""

        async with session.post(
            url,
            json={"task_id": task_id, "image_load_method": "pil", "image_str": image_str},
            headers={"content-type": "application/json"},
        ) as response:
            res = await response.json()
        finish_time = datetime.datetime.now()
        print(f"task-{task_id} [{img_path}] using {(finish_time-start_time).total_seconds(): .4f}s")
        print(res)

    image_paths = random_sample_images(num_messages)
    s1 = time.time()
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(*[send_task(task_id, img_path, session) for task_id, img_path in enumerate(image_paths)])
    print("{} samples cost time: {}".format(num_messages, time.time() - s1))


def send_message_every_n_seconds(url: str, num_messages: int = 10, n: float = 0.2, verbose: bool = False):
    def post_message(post_id, img_path):
        start_time = datetime.datetime.now()
        image_str = read_images_base64_str(img_path)
        if image_str is None:
            return ""

        response = requests.post(
            url,
            json={"task_id": task_id, "image_load_method": "pil", "image_str": image_str},
            verify=False,
            headers={"content-type": "application/json"},
        )
        finish_time = datetime.datetime.now()
        res = response.json()
        print(f"task-{post_id} [{img_path}] using {(finish_time-start_time).total_seconds(): .4f}s")
        print(res)

    threads = []
    image_paths = random_sample_images(num_messages)
    s1 = time.time()

    for task_id, img_path in enumerate(image_paths):
        t = threading.Thread(target=post_message, args=(task_id, img_path), daemon=True)
        t.start()
        threads.append(t)
        time.sleep(n)

    for t in threads:
        t.join()

    print("{} samples cost time: {}".format(num_messages, time.time() - s1))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="hz.matpool.com")
    parser.add_argument("--port", type=str, default="28032")
    parser.add_argument("--route", type=str, default="image2text")
    parser.add_argument("--msg_num", type=int, default=5)
    parser.add_argument("--interval", type=float, default=0.1)
    parser.add_argument("--test_sequentially", action="store_true")
    parser.add_argument("--test_concurrently", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    url = f"https://{args.host}:{args.port}/image2text/{args.route}"

    if args.test_sequentially:
        send_message_every_n_seconds(url, args.msg_num, args.interval, args.verbose)

    if args.test_concurrently:
        asyncio.run(send_messages_concurrently(url, args.msg_num, args.verbose))

# -*- coding: utf-8 -*-
# @CreateTime : 2022/05/30 15:09
# @Author     : 卢江虎
# @Company    : Gemsouls
# @File       : test_model.py
# @Description:
# @LastEditBy :

import sys
from os.path import abspath, dirname, exists, join

ROOT = dirname(dirname(dirname(abspath(__file__))))
sys.path.insert(0, ROOT)
import copy
import pandas as pd
import argparse
import asyncio
import base64
import datetime
import glob
import io
import os
import pickle
import random
import re
import threading
import time
from os.path import abspath, dirname, exists, join
from typing import *

import aiohttp
import cv2 as cv
import numpy as np
import requests
from gia_config import ServiceConfig
from gia_config.nn_models_config import ClipCapModelConfig, ImageCaptionModelType
from gia_model.helper.image_captioning_helper import ImageCaptionHelper
from gia_model.message import TaskInputMessage, TaskMessage
from PIL import Image

ROOT = dirname(dirname(dirname(abspath(__file__))))
sys.path.insert(0, ROOT)


def img2base64(img):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    buffered.seek(0)
    img_byte = buffered.getvalue()
    img_str = base64.b64encode(img_byte).decode()
    return img_str


def pil_preprocess(image, resize):
    if image.mode != "RGB":
        image = image.convert("RGB")

    imr = image.resize(resize, resample=Image.BILINEAR)
    image_str = img2base64(imr)
    return image_str


def cv_preprocess(image, resize):
    image = cv.cvtColor(np.array(image, dtype=np.uint8), cv.COLOR_RGB2BGR)

    image = cv.resize(image, dsize=resize, interpolation=cv.INTER_CUBIC)
    image_str = base64.b64encode(cv.imencode(".png", image)[1].tobytes()).decode("utf-8")
    return image_str


def pkl_test(helper, resize):
    num_messages = 2
    image_pkl_lst = glob.glob("/home/lujianghu/code/GemsoulsImageNSFW/test_img/*.pkl")
    image_paths = random.sample(image_pkl_lst, num_messages)
    for image_fpath in image_pkl_lst:
        with open(image_fpath, "rb") as f:
            data = f.read()
        image = Image.open(io.BytesIO(data))
        image_str = cv_preprocess(image, resize)

        input_message = TaskInputMessage(task_id="test", image_load_method="pil", image_str=image_str)
        task_message_pil = TaskMessage(input_message=input_message)

        addition_config = {}
        helper(task_message_pil, **addition_config)
        print(f"pil: {task_message_pil.output_message.caption_result}")


def _main(helper, image_fname, resize=(384, 384)):
    res_lst = []
    # url = "https://gimg2.baidu.com/image_search/src=http%3A%2F%2Fimg.jj20.com%2Fup%2Fallimg%2F1114%2F113020142315%2F201130142315-1-1200.jpg&refer=http%3A%2F%2Fimg.jj20.com&app=2002&size=f9999,10000&q=a80&n=0&g=0n&fmt=auto?sec=1656490714&t=7571679dce10683a4484afb91b0c8d79"
    # input_message = TaskInputMessage(task_id="test", image_url=url, image_load_method="pil")
    # task_message = TaskMessage(input_message=input_message)

    # addition_config = {}
    # helper(task_message, **addition_config)
    # print(f"url: {task_message.output_message.caption_result}")
    # res_lst.append(copy.deepcopy(task_message.output_message.caption_result))

    image = cv.imread(image_fname)
    input_message = TaskInputMessage(task_id="test", image_load_method="pil", image_str=cv_preprocess(image, resize))
    task_message_cv = TaskMessage(input_message=input_message)

    addition_config = {}
    helper(task_message_cv, **addition_config)
    print(f"cv: {task_message_cv.output_message.caption_result}")
    res_lst.append(copy.deepcopy(task_message_cv.output_message.caption_result))

    # pil
    with open(image_fname, "rb") as f:
        data = f.read()
    image = Image.open(io.BytesIO(data))

    input_message = TaskInputMessage(task_id="test", image_load_method="pil", image_str=pil_preprocess(image, resize))
    task_message_pil = TaskMessage(input_message=input_message)

    addition_config = {}
    helper(task_message_pil, **addition_config)
    print(f"pil: {task_message_pil.output_message.caption_result}")
    res_lst.append(copy.deepcopy(task_message_pil.output_message.caption_result))

    return res_lst


if __name__ == "__main__":
    image_fname = "gia_test/test_src/test.png"
    service_config_blip = ServiceConfig(image_caption_model_type=ImageCaptionModelType.Blip)
    helper_blip = ImageCaptionHelper(service_config_blip)
    service_config_clipcap = ServiceConfig(image_caption_model_type=ImageCaptionModelType.ClipCap)
    helper_clipcap = ImageCaptionHelper(service_config_clipcap)

    test_image_dir = "/home/lujianghu/code/ImageCaptionTest/fb_log_images_211208"
    image_fname_lst = glob.glob(os.path.join(test_image_dir, "*.png"))
    num_message = 100
    image_fname_lst = random.sample(image_fname_lst, num_message)

    res_lst = []

    for image_fname in image_fname_lst:
        print("Blip Test")
        resize = (384, 384)  # 预处理的图片大小
        # url cv pil
        s1 = time.time()
        blip_res_lst = _main(helper_blip, image_fname, resize)
        blip_res_lst += [time.time() - s1]

        print("ClipCap Test")
        resize = (224, 224)  # 预处理的图片大小
        s2 = time.time()
        # url cv pil
        clipcap_res_lst = _main(helper_clipcap, image_fname, resize)
        clipcap_res_lst += [time.time() - s2]
        res_lst.append([os.path.basename(image_fname)] + blip_res_lst + clipcap_res_lst)

    df = pd.DataFrame(
        res_lst,
        columns=[
            "fname",
            "Blip(CV)",
            "Blip(PIL)",
            "Blip(Time Cost)",
            "ClipCap(CV)",
            "ClipCap(PIL)",
            "Clip(Time Cost)",
        ],
    )
    df.to_excel("res.xlsx", index=False)
    # pkl_test(helper, resize)

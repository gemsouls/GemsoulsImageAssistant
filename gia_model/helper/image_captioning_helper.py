# -*- coding: utf-8 -*-
# @CreateTime : 2021/12/10 15:45
# @Author     : 潘其威(PanEa)
# @Company    : Gemsouls
# @File       : image_captioning_helper.py
# @Description:
# @LastEditBy :

import base64
import io
import os
import traceback
from typing import *

import cv2 as cv
import numpy as np
import PIL
import requests
import torch
from PIL import Image
from torchvision import transforms
from torchvision.transforms.functional import InterpolationMode

from gia_config import ServiceConfig
from gia_config.nn_models_config import ImageCaptionModelType

from ..basic import BasicHelper, BasicHelperNNModelsMap, BasicHelperResourcesMap
from ..exception.image_exception import GiaImageTransformError, GiaImageReadError, GiaImageDownLoadError
from ..message import TaskMessage
from .utils import BlipPredictor, ClipCapPredictor

class ImageCaptionHelper(BasicHelper):
    HEADERS = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
        "application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "max-age=0",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/96.0.4664.45 Safari/537.36",
    }

    def __init__(self, config: ServiceConfig, turn_on: bool = True, **additional_config):
        super(ImageCaptionHelper, self).__init__(None, None, turn_on, **additional_config)

        self.device = config.models_config.image_caption.device
        self.image_caption_model_type = config.image_caption_model_type
        if config.image_caption_model_type == ImageCaptionModelType.Blip:
            self.predictor = BlipPredictor(config.models_config.image_caption.blip.caption_base, self.device)
        else:
            weights = torch.load(config.models_config.image_caption.clip_cap.coco, map_location=self.device)
            self.predictor = ClipCapPredictor(weights)

    def _help(self, task_message: TaskMessage, image, *args, **kwargs):
        use_beam_search = False
        # use_beam_search = True
        if "use_beam_search" in self.additional_config:
            use_beam_search = bool(self.additional_config["use_beam_search"])
        if "use_beam_search" in kwargs:
            use_beam_search = bool(kwargs["use_beam_search"])

        try:
            caption_result = self.predictor.predict(image, use_beam_search=use_beam_search)
        except Exception as e:
            raise
        else:
            # TODO: 添加适当的截断策略以保留完整的句子
            task_message.output_message.caption_result = caption_result.strip()

    def __call__(self, task_message: TaskMessage, *args, **kwargs):
        if self.turn_on:
            image = self._preprocess(task_message)
            self._help(task_message, image)

    def _imread_from_url(self, image_url):
        # TODO: 更严苛的路径检验（如判断是否是图片路径等）以防止攻击
        # local image
        if (
            os.path.exists(image_url) and os.path.isfile(image_url) and any(
                [
                    image_url.lower().endswith(postfix)
                    for postfix in ["jpg", "jpeg", "png", "bmp", "webp", "tif", "tiff"]
                ]
            )
        ):
            try:
                with open(image_url, "rb") as f:
                    image = f.read()
            except Exception as e:
                raise GiaImageReadError(
                    origin_err_msg=traceback.format_exc(),
                    additional_err_msg=f"read local image [{image_url}] failed.",
                    image_url=image_url,
                )
        # download image
        else:
            try:
                response = requests.get(image_url, stream=True, headers=self.HEADERS, verify=False)
            except:
                raise GiaImageDownLoadError(
                    origin_err_msg=traceback.format_exc(),
                    additional_err_msg=f"download remote image [{image_url}] failed.",
                    image_url=image_url,
                )
            if response.status_code == 200:
                response.raw.decode_content = True
                image = response.content
            else:
                raise GiaImageDownLoadError(
                    origin_err_msg="",
                    additional_err_msg=f"download remote image [{image_url}] failed, "
                    f"status code is {response.status_code}",
                    image_url=image_url,
                )

        return Image.open(io.BytesIO(image))

    def _preprocess(self, task_message: TaskMessage):
        resize_op = []
        if task_message.input_message.image_url:
            try:
                image = self._imread_from_url(task_message.input_message.image_url)
            except Exception as e:
                task_message.task_failure_info = "[imread_from_url]: " + str(e)
                return
            if self.image_caption_model_type == ImageCaptionModelType.Blip:
                image_size = 384
            else:
                image_size = 224

            resize_op = [transforms.Resize((image_size, image_size), interpolation=InterpolationMode.BICUBIC)]
        elif task_message.input_message.image_str:
            image_bytes = base64.b64decode(task_message.input_message.image_str)
            if task_message.input_message.image_load_method == "cv":
                image = cv.imdecode(np.frombuffer(image_bytes, np.uint8), cv.IMREAD_COLOR)
            elif task_message.input_message.image_load_method == "pil":
                image = Image.open(io.BytesIO(image_bytes))
            else:
                task_message.task_failure_info = "[preprocess]: Not Support Image Load Method"
                return
        else:
            # 其他类型处理
            task_message.task_failure_info = "[preprocess]: Not Support Data Type"
            return

        try:
            if isinstance(image, str):
                raw_image = io.imread(image)   # type: ignore
                raw_image = Image.fromarray(raw_image)
            else:
                raw_image = image
            # raw_image = raw_image.convert("RGB")

            transform = transforms.Compose(
                resize_op + [
                    transforms.ToTensor(),
                    transforms.Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)),
                ]
            )
            # clip_cap
            # Compose(
            #     CenterCrop(size=(224, 224))
            #     <function _convert_image_to_rgb at 0x7f34fb0a53a0>
            # )

            image = transform(raw_image).unsqueeze(0).to(self.device)
            return image
        except Exception as e:
            task_message.task_failure_info = "[preprocess]: Image Transforms Failed"
            raise GiaImageTransformError(
                origin_err_msg=traceback.format_exc(),
                additional_err_msg="transform image for [Blip] model to predict failed.",
            )

    def update(self, *args, **kwargs):
        pass

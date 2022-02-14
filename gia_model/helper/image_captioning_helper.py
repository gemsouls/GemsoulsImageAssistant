# -*- coding: utf-8 -*-
# @CreateTime : 2021/12/10 15:45
# @Author     : 潘其威(PanEa)
# @Company    : Gemsouls
# @File       : image_captioning_helper.py
# @Description:
# @LastEditBy :

import io
import os
import PIL
from PIL import Image
import requests
import traceback
from typing import *

import torch

from .utils import ClipCapPredictor, BlipPredictor
from ..basic import BasicHelper, BasicHelperResourcesMap, BasicHelperNNModelsMap
from ..message import TaskMessage
from ..exception.image_exception import *
from gia_config import ServiceConfig
from gia_config.nn_models_config import ImageCaptionModelType


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

    def __init__(
        self,
        config: ServiceConfig,
        turn_on: bool = True,
        **additional_config
    ):
        super(ImageCaptionHelper, self).__init__(None, None, turn_on, **additional_config)

        if config.image_caption_model_type == ImageCaptionModelType.Blip:
            self.predictor = BlipPredictor(config.models_config.image_caption.blip.caption_base)
        else:
            weights = torch.load(
                config.models_config.image_caption.clip_cap.coco, map_location="cpu"
            )
            self.predictor = ClipCapPredictor(weights)

    def _help(self, task_message: TaskMessage, *args, **kwargs):
        use_beam_search = False
        if "use_beam_search" in self.additional_config:
            use_beam_search = bool(self.additional_config["use_beam_search"])
        if "use_beam_search" in kwargs:
            use_beam_search = bool(kwargs["use_beam_search"])

        image_url = task_message.input_message.image_url
        # TODO: 更严苛的路径检验（如判断是否是图片路径等）以防止攻击
        # download image
        if os.path.exists(image_url) and os.path.isfile(image_url) and any(
            [
                image_url.lower().endswith(postfix) for postfix
                in ["jpg", "jpeg", "png", "bmp", "webp", "tif", "tiff"]
            ]
        ):
            try:
                with open(image_url, "rb") as f:
                    image = f.read()
            except:
                raise GiaImageReadError(
                    origin_err_msg=traceback.format_exc(),
                    additional_err_msg=f"read local image [{image_url}] failed.",
                    image_url=image_url
                )

        else:
            try:
                response = requests.get(image_url, stream=True, headers=self.HEADERS, verify=False)
            except:
                raise GiaImageDownLoadError(
                    origin_err_msg=traceback.format_exc(),
                    additional_err_msg=f"download remote image [{image_url}] failed.",
                    image_url=image_url
                )
            if response.status_code == 200:
                response.raw.decode_content = True
                image = response.content
            else:
                raise GiaImageDownLoadError(
                    origin_err_msg="",
                    additional_err_msg=f"download remote image [{image_url}] failed, "
                                       f"status code is {response.status_code}",
                    image_url=image_url
                )

        try:
            caption_result = self.predictor.predict(
                Image.open(io.BytesIO(image)),
                use_beam_search=use_beam_search
            )
        except:
            raise
        else:
            # TODO: 添加适当的截断策略以保留完整的句子
            task_message.output_message.caption_result = caption_result.strip()

    def __call__(self, task_message: TaskMessage, *args, **kwargs):
        if self.turn_on:
            self._help(task_message)

    def update(self, *args, **kwargs):
        pass

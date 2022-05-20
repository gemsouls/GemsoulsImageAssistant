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
from typing import *

from .utils import ClipCapPredictor
from ..basic import BasicHelper, BasicHelperResourcesMap, BasicHelperNNModelsMap
from ..message import TaskMessage


class ClipCapHelperNNModelsMap(BasicHelperNNModelsMap):
    def __init__(self, pretrained_clip_cap_model_weights: Any):
        super(ClipCapHelperNNModelsMap, self).__init__()
        self.pretrained_clip_cap_model_weights = pretrained_clip_cap_model_weights

    def update(self, *args, **kwargs):
        return


class ClipCapHelperResourcesMap(BasicHelperResourcesMap):
    def update(self, *args, **kwargs):
        return


class ClipCapHelper(BasicHelper):
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
            nn_models_map: ClipCapHelperNNModelsMap,
            resources_map: ClipCapHelperResourcesMap,
            turn_on: bool = True,
            **additional_config
    ):
        super(ClipCapHelper, self).__init__(nn_models_map, resources_map, turn_on, **additional_config)

        self.clip_cap_predictor = ClipCapPredictor(nn_models_map.pretrained_clip_cap_model_weights)

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
            with open(image_url, "rb") as f:
                image = f.read()
        else:
            try:
                response = requests.get(image_url, stream=True, headers=self.HEADERS, verify=False)
            except:
                raise
            if response.status_code == 200:
                response.raw.decode_content = True
                image = response.content
            else:
                image = b""
            if not image:
                return

        caption_result = self.clip_cap_predictor.predict(
            Image.open(io.BytesIO(image)),
            use_beam_search=use_beam_search
        )
        # TODO: 添加适当的截断策略以保留完整的句子
        task_message.output_message.caption_result = caption_result.strip()

    def __call__(self, task_message: TaskMessage, *args, **kwargs):
        if self.turn_on:
            self._help(task_message)

    def update(self, *args, **kwargs):
        pass

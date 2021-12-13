# -*- coding: utf-8 -*-
# @CreateTime : 2021/12/10 15:45
# @Author     : 潘其威(PanEa)
# @Company    : Gemsouls
# @File       : image_captioning_helper.py
# @Description:
# @LastEditBy :

import io
import PIL
from PIL import Image
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

        image = task_message.input_message.image
        caption_result = self.clip_cap_predictor.predict(
            Image.open(io.BytesIO(image)),
            use_beam_search=use_beam_search
        )
        task_message.output_message.caption_result = caption_result

    def __call__(self, task_message: TaskMessage, *args, **kwargs):
        if self.turn_on:
            self._help(task_message)

    def update(self, *args, **kwargs):
        pass

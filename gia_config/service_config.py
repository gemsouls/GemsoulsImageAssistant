# -*- coding: utf-8 -*-
# @CreateTime : 2021/12/13 14:38
# @Author     : 潘其威(PanEa)
# @Company    : Gemsouls
# @File       : service_config.py
# @Description:
# @LastEditBy :

from .nn_models_config import ImageCaptionModelType, NNModelsConfig


class ServiceConfig:
    def __init__(self, image_caption_model_type: ImageCaptionModelType):
        self.models_config = NNModelsConfig()
        self.image_caption_model_type = image_caption_model_type

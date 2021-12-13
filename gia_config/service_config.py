# -*- coding: utf-8 -*-
# @CreateTime : 2021/12/13 14:38
# @Author     : 潘其威(PanEa)
# @Company    : Gemsouls
# @File       : service_config.py
# @Description:
# @LastEditBy :

from .nn_models_config import build_nn_models_config


class ServiceConfig:
    def __init__(self):
        self.models_config = build_nn_models_config()

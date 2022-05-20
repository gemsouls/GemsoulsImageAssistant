# -*- coding: utf-8 -*-
# @CreateTime : 2021/12/10 15:48
# @Author     : 潘其威(PanEa)
# @Company    : Gemsouls
# @File       : basic_helper.py
# @Description:
# @LastEditBy :


from abc import abstractmethod
from typing import *


class BasicHelperNNModelsMap:
    @abstractmethod
    def update(self, *args, **kwargs):
        raise NotImplementedError


class BasicHelperResourcesMap:
    @abstractmethod
    def update(self, *args, **kwargs):
        raise NotImplementedError


class BasicHelper:
    def __init__(
            self,
            nn_models_map: BasicHelperNNModelsMap = None,
            resources_map: BasicHelperResourcesMap = None,
            turn_on: bool = True,
            **additional_config
    ):
        self.nn_models_map = nn_models_map
        self.resources_map = resources_map
        self.turn_on = turn_on
        self.additional_config = additional_config

    @abstractmethod
    def _help(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def update(self, *args, **kwargs):
        raise NotImplementedError

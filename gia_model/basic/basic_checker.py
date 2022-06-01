# -*- coding: utf-8 -*-
# @CreateTime : 2021/12/10 15:48
# @Author     : 潘其威(PanEa)
# @Company    : Gemsouls
# @File       : basic_checker.py
# @Description:
# @LastEditBy :

from abc import abstractmethod


class BasicCheckerNNModelsMap:
    @abstractmethod
    def update(self, *args, **kwargs):
        raise NotImplementedError


class BasicCheckerResourcesMap:
    @abstractmethod
    def update(self, *args, **kwargs):
        raise NotImplementedError


class BasicChecker:
    def __init__(
        self,
        nn_models_map: BasicCheckerNNModelsMap,
        resources_map: BasicCheckerResourcesMap,
        turn_on: bool = True,
        **additional_config
    ):
        self.nn_models_map = nn_models_map
        self.resources_map = resources_map
        self.turn_on = turn_on
        self.additional_config = additional_config

    @abstractmethod
    def _check(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def update(self, *args, **kwargs):
        raise NotImplementedError

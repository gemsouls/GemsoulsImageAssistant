# -*- coding: utf-8 -*-
# @CreateTime : 2021/12/13 11:32
# @Author     : 潘其威(PanEa)
# @Company    : Gemsouls
# @File       : execution_pipeline.py
# @Description:
# @LastEditBy :


from typing import *

import torch

from ..basic import BasicPipeline, BasicPipelineNNModelsInitializer, BasicPipelineResourcesInitializer
from ..helper import (
    ClipCapHelperResourcesMap,
    ClipCapHelperNNModelsMap,
    ClipCapHelper
)
from ..message import TaskMessage


class ExecutionPipelineNNModelsInitializer(BasicPipelineNNModelsInitializer):
    def __init__(self, config_models):
        self.pretrained_clip_cap_model_weights = torch.load(
            config_models["pretrained_clip_cap_model_weights"], map_location="cpu"
        )

    def update(self, *args, **kwargs):
        pass


class ExecutionPipelineResourcesInitializer(BasicPipelineResourcesInitializer):
    def __init__(self):
        pass

    def update(self, *args, **kwargs):
        pass


class ExecutionPipeline(BasicPipeline):
    def __init__(self, config_models):
        nn_models = ExecutionPipelineNNModelsInitializer(
            config_models
        )
        sequential_pipes = [
            ClipCapHelper(
                nn_models_map=ClipCapHelperNNModelsMap(
                    pretrained_clip_cap_model_weights=nn_models.pretrained_clip_cap_model_weights
                ),
                resources_map=ClipCapHelperResourcesMap(),
                turn_on=True,
                **{"use_beam_search": True}
            )
        ]
        super(ExecutionPipeline, self).__init__(sequential_pipes=sequential_pipes)

    def run(self,
            message: TaskMessage,
            addition_sequential_pipes: Optional[List[Callable]] = None,
            addition_async_pipes: Optional[List[Callable]] = None,
            sequential_execute_orders: Optional[List[int]] = None,
            *args,
            **kwargs):
        self.run_sequential(message, addition_sequential_pipes, sequential_execute_orders, *args, **kwargs)

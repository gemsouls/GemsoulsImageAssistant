# -*- coding: utf-8 -*-
# @CreateTime : 2021/12/13 11:32
# @Author     : 潘其威(PanEa)
# @Company    : Gemsouls
# @File       : execution_pipeline.py
# @Description:
# @LastEditBy :


from typing import *

import torch

from ..basic import BasicPipeline
from ..helper import (
    ImageCaptionHelper
)
from ..message import TaskMessage
from gia_config import ServiceConfig


class ExecutionPipeline(BasicPipeline):
    def __init__(self, config: ServiceConfig):
        sequential_pipes = [
            ImageCaptionHelper(
                config=config,
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
        try:
            self.run_sequential(message, addition_sequential_pipes, sequential_execute_orders, *args, **kwargs)
        except:
            raise

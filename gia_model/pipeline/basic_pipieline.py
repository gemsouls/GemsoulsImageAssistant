# -*- coding: utf-8 -*-
# @CreateTime : 2021/12/10 15:48
# @Author     : 潘其威(PanEa)
# @Company    : Gemsouls
# @File       : basic_pipieline.py
# @Description:
# @LastEditBy :

import asyncio
from abc import abstractmethod
from typing import Callable, List, Optional

from ..message.task_message import TaskMessage


class BasicPipelineNNModelsInitializer:
    @abstractmethod
    def update(self, *args, **kwargs):
        raise NotImplementedError


class BasicPipelineResourcesInitializer:
    @abstractmethod
    def update(self, *args, **kwargs):
        raise NotImplementedError


class BasicPipeline:
    def __init__(
        self,
        sequential_pipes: Optional[List[Callable]] = None,
        async_pipes: Optional[List[Callable]] = None,
        sequential_pipes_execute_orders: Optional[List[int]] = None,
        *args,
        **kwargs
    ):
        self.default_sequential_pipes = sequential_pipes
        self.default_async_pipes = async_pipes
        if self.default_sequential_pipes is None:
            self.default_sequential_pipes = []
        if self.default_async_pipes is None:
            self.default_async_pipes = []

        if self.default_sequential_pipes and sequential_pipes_execute_orders:
            self.default_sequential_pipes = self._reorder_execute_orders(
                self.default_sequential_pipes, sequential_pipes_execute_orders
            )

    @staticmethod
    def _reorder_execute_orders(pipes: List[Callable], execute_orders: List[int]):
        assert len(pipes) == len(execute_orders)
        return [each[0] for each in sorted(zip(pipes, execute_orders), key=lambda x: x[1])]

    def run_sequential(
        self,
        message: TaskMessage,
        addition_pipes: Optional[List[Callable]] = None,
        execute_orders: Optional[List[int]] = None,
        *args,
        **kwargs
    ):
        if addition_pipes is None:
            addition_pipes = []
        pipes = self.default_sequential_pipes + addition_pipes
        if execute_orders:
            pipes = self._reorder_execute_orders(pipes, execute_orders)

        if pipes:
            for idx, pipe in enumerate(pipes):
                asyncio.run(pipe(message, *args, **kwargs.get(str(idx), dict()))) if asyncio.iscoroutinefunction(
                    pipe
                ) else pipe(message, *args, **kwargs.get(str(idx), dict()))

    async def run_async(self, message: TaskMessage, addition_pipes: Optional[List[Callable]] = None, *args, **kwargs):
        if addition_pipes is None:
            addition_pipes = []
        pipes = self.default_async_pipes + addition_pipes
        if pipes:
            await asyncio.gather(
                *[pipe(message, *args, **kwargs.get(str(idx), dict())) for idx, pipe in enumerate(pipes)]
            )

    @abstractmethod
    def run(
        self,
        message: TaskMessage,
        addition_sequential_pipes: Optional[List[Callable]] = None,
        addition_async_pipes: Optional[List[Callable]] = None,
        sequential_execute_orders: Optional[List[int]] = None,
        *args,
        **kwargs
    ):
        raise NotImplementedError

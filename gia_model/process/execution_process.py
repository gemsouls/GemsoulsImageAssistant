# -*- coding: utf-8 -*-
# @CreateTime : 2021/12/13 12:26
# @Author     : 潘其威(PanEa)
# @Company    : Gemsouls
# @File       : execution_process.py
# @Description:
# @LastEditBy :


from queue import Queue
from typing import *

from ..message import TaskMessage
from ..pipeline import ExecutionPipeline
from .basic_process import BasicTaskProcess, BasicTaskProcessHandler


class ExecutionProcess(BasicTaskProcess):
    pipeline: ExecutionPipeline

    def mapping_output_queues(self, output_queues: Sequence[Queue]) -> Dict[str, Queue]:
        assert len(output_queues) == 1
        return {"system_output_queue": output_queues[0]}

    def execute_pipeline(self, message: TaskMessage) -> None:
        self.pipeline.run(message, **self.default_pipeline_execution_additional_kwargs)

    def output_message(self, message: TaskMessage):
        task_id = message.input_message.task_id
        print(
            f"[{self.__class__.__name__}-{self.proc_id}]->" f"task-{task_id}->sent task_message to system_output_queue"
        )
        self.output_queues_map["system_output_queue"].put_nowait(message)


class ExecutionProcessHandler(BasicTaskProcessHandler):
    pass

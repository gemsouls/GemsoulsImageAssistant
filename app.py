# -*- coding: utf-8 -*-
# @CreateTime : 2021/12/10 15:31
# @Author     : 潘其威(PanEa)
# @Company    : Gemsouls
# @File       : app.py.py
# @Description:
# @LastEditBy :

import asyncio
from datetime import datetime
from hashlib import md5
from queue import Queue
import time
from typing import *

from fastapi import FastAPI

from gia_model.pipeline import ExecutionPipeline, NAME_EXECUTION_PIPELINE_NN_MODELS_INITIALIZER
from gia_model.process import ExecutionProcessHandler, ExecutionProcess
from gia_model.message import TaskMessage, TaskInputMessage, TaskOutputMessage
from gia_config import ServiceConfig


class Queues:
    execution_input_queue = Queue()
    system_output_queue = Queue()


class AppManager:
    queues: Queues = Queues
    execution_process_handler: ExecutionProcessHandler = None
    result_pool: Dict[Union[int, str, bytes], TaskMessage] = dict()

    def __init__(self, service_config: ServiceConfig):
        self.service_config = service_config
        self.is_running = False

    def start(self):
        print(f"[{datetime.now()}]->[{self.__class__.__name__}]->starting process handlers...")
        self.execution_process_handler = ExecutionProcessHandler(
            process=ExecutionProcess,
            pipeline=ExecutionPipeline,
            pipeline_init_kwargs={
                "config_models": self.service_config.models_config[NAME_EXECUTION_PIPELINE_NN_MODELS_INITIALIZER]
            },
            input_queue=self.queues.execution_input_queue,
            output_queues=[self.queues.system_output_queue],
            failure_queue=self.queues.system_output_queue,
            n_proc=1
        )
        print(f"[{datetime.now()}]->[{self.__class__.__name__}]->process handlers started")

        self.is_running = True

    async def stop(self):
        print(f"[{datetime.now()}]->[{self.__class__.__name__}]->stopping...")
        if self.is_running:
            await self.execution_process_handler.stop()
        self.is_running = False
        print(f"[{datetime.now()}]->[{self.__class__.__name__}]->stopped")

    async def wait_task_done(self, task_id):
        while True:
            if task_id not in self.result_pool:
                await asyncio.sleep(0.1)
            else:
                return self.result_pool.pop(task_id)


# ===== init app ===== #
app = FastAPI()

# ===== init app manager ===== #
app_manager: AppManager = None


# ===== define routes ===== #
@app.on_event("startup")
async def startup_event():
    global app_manager
    service_config = ServiceConfig()
    app_manager = AppManager(service_config)
    app_manager.start()


@app.on_event("shutdown")
async def shutdown_event():
    global app_manager
    await app_manager.stop()


@app.post("/image2text", response_model=TaskOutputMessage)
async def image2text(input_message: TaskInputMessage):
    start = time.time()
    task_id = md5(str(input_message.task_id) + str(datetime.now())).hexdigest()
    input_message.task_id = task_id
    print(f"[{datetime.now()}]->[image2text]->get task-{task_id}.")
    task_message = TaskMessage(input_message=input_message)
    print(f"[{datetime.now()}]->[image2text]->adding task-{task_id} to execution process...")
    await app_manager.execution_process_handler.add_task(task_message)
    print(f"[{datetime.now()}]->[image2text]->waiting task-{task_id} to be processed...")
    await app_manager.wait_task_done(task_id)
    end = time.time()
    print(f"[{datetime.now()}]->[image2text]->task-{task_id} process finished, using {end-start:.4f}s")
    return task_message.output_message

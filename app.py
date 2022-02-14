# -*- coding: utf-8 -*-
# @CreateTime : 2021/12/10 15:31
# @Author     : 潘其威(PanEa)
# @Company    : Gemsouls
# @File       : app.py.py
# @Description:
# @LastEditBy :

import asyncio
import threading
from datetime import datetime
from hashlib import md5
from queue import Queue, Empty
import time
from typing import *

from fastapi import FastAPI

from gia_model.pipeline import ExecutionPipeline, NAME_EXECUTION_PIPELINE_NN_MODELS_INITIALIZER
from gia_model.process import ExecutionProcessHandler, ExecutionProcess
from gia_model.message import TaskMessage, TaskInputMessage, TaskOutputMessage
from gia_config import ServiceConfig
from gia_config.nn_models_config import ImageCaptionModelType


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
                "config": self.service_config
            },
            input_queue=self.queues.execution_input_queue,
            output_queues=[self.queues.system_output_queue],
            failure_queue=self.queues.system_output_queue,
            n_proc=1
        )
        print(f"[{datetime.now()}]->[{self.__class__.__name__}]->process handlers started")

        self.is_running = True

        threading.Thread(target=self._listen_queue_system_output, daemon=True).start()

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

    def _listen_queue_system_output(self):
        # listening queue_system_output and get finished task_message from it
        while self.is_running:
            try:
                task_message: TaskMessage = self.queues.system_output_queue.get_nowait()
            except Empty:
                time.sleep(0.1)
            else:
                task_id = task_message.input_message.task_id
                self.result_pool[task_id] = task_message
                print(f"[{datetime.now()}]->[AssistantManager]->get task-{task_id} from system output queue "
                      f"and added to result pool.")
                time.sleep(0.1)


# ===== init app ===== #
app = FastAPI()

# ===== init app manager ===== #
app_manager: AppManager = None


# ===== define routes ===== #
@app.on_event("startup")
async def startup_event():
    global app_manager
    service_config = ServiceConfig(
        image_caption_model_type=ImageCaptionModelType.Blip
    )
    app_manager = AppManager(service_config)
    app_manager.start()


@app.on_event("shutdown")
async def shutdown_event():
    global app_manager
    await app_manager.stop()


@app.post("/image2text", response_model=TaskOutputMessage)
async def image2text(input_message: TaskInputMessage):
    start = time.time()
    task_id = md5((str(input_message.task_id) + str(datetime.now())).encode(encoding="utf-8")).hexdigest()
    input_message.task_id = task_id
    print(f"[{datetime.now()}]->[image2text]->get task-{task_id}.")
    task_message = TaskMessage(input_message=input_message)
    print(f"[{datetime.now()}]->[image2text]->adding task-{task_id} to execution process...")
    await app_manager.execution_process_handler.add_task(task_message)
    print(f"[{datetime.now()}]->[image2text]->waiting task-{task_id} to be processed...")
    task_message = await app_manager.wait_task_done(task_id)
    end = time.time()
    print(f"[{datetime.now()}]->[image2text]->task-{task_id} process finished, using {end-start:.4f}s")
    return task_message.output_message


@app.get("/hello")
async def hello():
    return {"result": "hello world!"}

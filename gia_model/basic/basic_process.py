# -*- coding: utf-8 -*-
# @CreateTime : 2021/12/10 15:49
# @Author     : 潘其威(PanEa)
# @Company    : Gemsouls
# @File       : basic_process.py
# @Description:
# @LastEditBy :

from abc import  abstractmethod
import asyncio
from queue import Queue, Empty, Full
import time
import threading
import traceback
from typing import *

from . import BasicPipeline
from ..message import TaskMessage


class BasicTaskProcess:
    pipeline: BasicPipeline

    def __init__(self,
                 proc_id: int,
                 pipeline: Callable,
                 pipeline_init_kwargs: Dict[str, Any],
                 input_queue: Queue,
                 output_queues: List[Queue],
                 failure_queue: Queue,
                 default_pipeline_execution_additional_kwargs: Dict[str, Any]):
        self._is_running = True

        self.proc_id = proc_id
        self.pipeline = pipeline(**pipeline_init_kwargs)
        self.default_pipeline_execution_additional_kwargs = default_pipeline_execution_additional_kwargs
        self.input_queue = input_queue
        self.output_queues_map = self.mapping_output_queues(output_queues)
        self.failure_queue = failure_queue
        self.inside_communicate_queue = Queue()

        self._thread = threading.Thread(target=self.run, daemon=True)
        self._thread.start()

    def run(self) -> None:
        print(f"[{self.__class__.__name__}]->process start running.")
        def _execute(cls):
            while cls._is_running:
                # get task message from queue
                try:
                    task_message: TaskMessage = cls.input_queue.get_nowait()
                except Empty:
                    time.sleep(0.1)
                    continue

                task_id = task_message.input_message.task_id
                try:
                    # 运行任务
                    print(
                        f"[{cls.__class__.__name__}-{cls.proc_id}]->task-{task_id}->executing task-{task_id}..."
                    )
                    cls.execute_pipeline(task_message)
                except:
                    # 记录异常信息
                    print(
                        f"[{cls.__class__.__name__}-{cls.proc_id}]->task-{task_id}->execute task-{task_id} failed."
                    )
                    print(
                        f"[{cls.__class__.__name__}-{cls.proc_id}]->task-{task_id}->failed reason:\n"
                        f"{traceback.format_exc()}",
                    )
                    # 输出message
                    cls.failure_queue.put_nowait(task_message)
                else:
                    # 更新状态
                    print(
                        f"[{cls.__class__.__name__}-{cls.proc_id}]->"
                        f"task-{task_id}->execute task-{task_id} successfully."
                    )
                    # 输出message
                    cls.inside_communicate_queue.put_nowait(task_message)
                finally:
                    cls.input_queue.task_done()
                    time.sleep(0.1)

        def _output(cls):
            while cls._is_running:
                try:
                    task_message: TaskMessage = cls.inside_communicate_queue.get_nowait()
                except Empty:
                    time.sleep(0.1)
                    continue

                try:
                    cls.output_message(task_message)
                except:
                    print(
                        f"[{cls.__class__.__name__}-{cls.proc_id}]->run->_output->error message:\n"
                        f"{traceback.format_exc()}"
                    )
                    cls.failure_queue.put_nowait(task_message)
                finally:
                    cls.inside_communicate_queue.task_done()
                    time.sleep(0.1)

        threading.Thread(target=_execute, args=(self,), daemon=True).start()
        threading.Thread(target=_output, args=(self,), daemon=True).start()

    @abstractmethod
    def mapping_output_queues(self, output_queues: Sequence[Queue]) -> Dict[str, Queue]:
        raise NotImplementedError

    @abstractmethod
    def execute_pipeline(self, message: TaskMessage) -> None:
        raise NotImplementedError

    @abstractmethod
    def output_message(self, message: TaskMessage):
        raise NotImplementedError

    async def stop(self):
        print(f"[{self.__class__.__name__}-{self.proc_id}]->stopping process...")

        self.input_queue.join()
        self.inside_communicate_queue.join()

        self._is_running = False

        print(f"[{self.__class__.__name__}-{self.proc_id}]->process stopped.")


class BasicTaskProcessHandler:
    def __init__(self,
                 process: Callable,
                 pipeline: Callable,
                 pipeline_init_kwargs: Dict[str, Any],
                 input_queue: Queue,
                 output_queues: List[Queue],
                 failure_queue: Queue,
                 n_proc: int = 1,
                 default_pipeline_additional_execution_kwargs: Dict[str, Any] = None
                 ):
        self._accept_input = True

        if not default_pipeline_additional_execution_kwargs:
            default_pipeline_additional_execution_kwargs = dict()
        self.processes = [
            process(
                i,
                pipeline,
                pipeline_init_kwargs,
                input_queue,
                output_queues,
                failure_queue,
                default_pipeline_additional_execution_kwargs
            ) for i in range(n_proc)
        ]
        self.input_queue = input_queue
        self.failure_queue = failure_queue

    async def add_task(self, task_message: TaskMessage):
        try:
            if self._accept_input:
                self.input_queue.put_nowait(task_message)
            else:
                raise Full()
        except Full:
            print(
                f"[{self.__class__.__name__}]->task-{task_message.input_message.task_id}"
                f"->error message->queue fulled"
            )
            self.failure_queue.put_nowait(task_message)

    async def stop(self):
        self._accept_input = False  # set to refuse input messages when process is about to stop running
        await asyncio.gather(*[process.stop() for process in self.processes])


class BaseFailureProcess:
    def __init__(self,
                 input_queue: Queue,
                 system_output_queue: Queue,
                 redirect_output_queue: Queue
                 ):
        self._is_running = True

        self.input_queue = input_queue
        self.system_output_queue = system_output_queue
        self.redirect_output_queue = redirect_output_queue

        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def run(self) -> None:
        print(f"[{self.__class__.__name__}]->process start running.")

        def _execute(cls):
            while cls._is_running:
                try:
                    failed_message: TaskMessage = cls.input_queue.get(block=False)
                except Empty:
                    time.sleep(0.1)
                    continue
                try:
                    cls.process_failed_message(failed_message)
                except:
                    cls.logger.error(
                        f"[{self.__class__.__name__}]->_execute->error message:\n",
                        exc_info=True
                    )
                finally:
                    cls.input_queue.task_done()

        threading.Thread(target=_execute, args=(self,), daemon=True).start()

    def process_failed_message(self, failed_message: TaskMessage):
        message_id = failed_message.input_message.task_id

        print(f"adding task-{message_id} to system_output_queue to return.")
        self.system_output_queue.put_nowait(failed_message)

    async def stop(self):
        print(f"[{self.__class__.__name__}]->stopping process...")

        self.input_queue.join()

        self._is_running = False

        print(f"[{self.__class__.__name__}]->process stopped")


class BaseFailureProcessHandler:
    def __init__(self,
                 input_queue: Queue,
                 system_output_queue: Queue,
                 redirect_output_queue: Queue):
        self.input_queue = input_queue
        self.system_output_queue = system_output_queue
        self.redirect_output_queue = redirect_output_queue
        self.process = BaseFailureProcess(
            input_queue=input_queue,
            system_output_queue=system_output_queue,
            redirect_output_queue=redirect_output_queue
        )

    async def add_task(self, task_message: TaskMessage):
        self.input_queue.put_nowait(task_message)

    async def stop(self):
        await self.process.stop()

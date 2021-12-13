# -*- coding: utf-8 -*-
# @CreateTime : 2021/12/10 17:07
# @Author     : 潘其威(PanEa)
# @Company    : Gemsouls
# @File       : task_message.py
# @Description:
# @LastEditBy :

from pydantic import Field
from typing import *

from ..basic import BasicMessage


class TaskInputMessage(BasicMessage):
    task_id: str = Field(default=..., description="id of each task")
    image: bytes = Field(default=..., description="image bytes")


class TaskOutputMessage(BasicMessage):
    caption_result: str = Field(default="", description="prediction result of image captioning")
    is_toxic_image: bool = Field(default=False, description="whether a image contains toxic content")


class TaskMessage(BasicMessage):
    input_message: TaskInputMessage = Field(default=...)
    output_message: TaskOutputMessage = Field(default=TaskOutputMessage())
    task_failure_info: str = Field(default="")

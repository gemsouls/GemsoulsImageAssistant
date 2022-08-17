# -*- coding: utf-8 -*-
# @CreateTime : 2021/12/10 17:07
# @Author     : 潘其威(PanEa)
# @Company    : Gemsouls
# @File       : task_message.py
# @Description:
# @LastEditBy :

from typing import *

from pydantic import Field

from .basic_message import BasicMessage


class TaskInputMessage(BasicMessage):
    task_id: str = Field(default=..., description="id of each task")
    image_url: str = Field(None, description="image download path")
    image_load_method: Literal["cv", "pil"]  # default: pil
    image_str: str = Field(None, repr=False, description="image bytes base64 string")

    def __repr_args__(self: BasicMessage):
        return [
            (key, value)
            for key, value in self.__dict__.items()
            if self.__fields__[key].field_info.extra.get("repr", True)
        ]


class TaskOutputMessage(BasicMessage):
    caption_result: str = Field(default="", description="prediction result of image captioning")
    is_toxic_image: bool = Field(default=False, description="whether a image contains toxic content")


class TaskMessage(BasicMessage):
    input_message: TaskInputMessage = Field(default=...)
    output_message: TaskOutputMessage = Field(default=TaskOutputMessage())
    task_failure_info: str = Field(default="")

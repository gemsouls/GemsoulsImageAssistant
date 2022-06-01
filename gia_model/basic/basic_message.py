# -*- coding: utf-8 -*-
# @CreateTime : 2021/12/10 15:48
# @Author     : 潘其威(PanEa)
# @Company    : Gemsouls
# @File       : basic_message.py
# @Description:
# @LastEditBy :


from datetime import datetime
from enum import Enum, EnumMeta
from typing import List, Any

from pydantic import BaseModel

DT_FMT = "%Y-%m-%d %H:%M:%S"


class BasicMessage(BaseModel):
    @staticmethod
    def _spacial2raw(spacial_value: Any):
        if isinstance(spacial_value, Enum):
            return spacial_value.name
        if isinstance(spacial_value, datetime):
            return spacial_value.strftime(DT_FMT)
        return spacial_value

    @staticmethod
    def _raw2spacial(raw_value: Any, spacial_value_type: List[EnumMeta]):
        if type(spacial_value_type) == EnumMeta:
            for e in spacial_value_type:
                if e.name == raw_value:
                    return e
        if spacial_value_type == datetime:
            return datetime.strptime(raw_value, DT_FMT)
        return raw_value

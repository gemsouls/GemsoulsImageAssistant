# -*- coding: utf-8 -*-
# @Author     : 潘其威(PanEa)
# @File       : basic_exception.py
# @Description:
from typing import Optional


class GiaError(Exception):
    def __init__(self, origin_err_msg: str, additional_err_msg: Optional[str] = None):
        self.additional_err_msg = additional_err_msg
        self.origin_err_msg = origin_err_msg

    def __repr__(self):
        if self.additional_err_msg:
            return self.additional_err_msg + "\n" + self.origin_err_msg
        return self.origin_err_msg

    def __str__(self):
        return self.__repr__()

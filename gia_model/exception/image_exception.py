# -*- coding: utf-8 -*-
# @Author     : 潘其威(PanEa)
# @File       : image_exception.py
# @Description:


from ..basic.basic_exception import GiaError


class GiaImageError(GiaError):
    def __init__(self, origin_err_msg: str, additional_err_msg: str, image_url: str = None):
        super(GiaImageError, self).__init__(origin_err_msg, additional_err_msg)
        self.image_url = image_url

    def __repr__(self):
        if self.image_url:
            return super(GiaImageError, self).__repr__() + f"error image url is: [{self.image_url}]"


class GiaImageDownLoadError(GiaImageError):
    pass


class GiaImageReadError(GiaImageError):
    pass


class GiaImageTransformError(GiaImageError):
    pass

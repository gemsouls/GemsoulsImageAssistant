# -*- coding: utf-8 -*-
# @Author     : 潘其威(PanEa)
# @File       : blip_inference.py
# @Description:


import traceback
from typing import *

from PIL import Image
import skimage.io as io
import torch
from torchvision import transforms
from torchvision.transforms.functional import InterpolationMode

from .blip_models.blip import blip_decoder
from gia_model.exception.image_exception import GiaImageTransformError


class Predictor:
    def __init__(self, pretrained_path: str, device: str = "cpu"):

        self.device = device
        self.model = blip_decoder(pretrained=pretrained_path, image_size=384, vit="base")
        self.model.to(self.device).eval()

    def predict(self, image: Union[str, Any], use_beam_search: bool = True):
        with torch.no_grad():
            caption = self.model.generate(image, sample=not use_beam_search, num_beams=3, max_length=20, min_length=5)
        return caption[0]

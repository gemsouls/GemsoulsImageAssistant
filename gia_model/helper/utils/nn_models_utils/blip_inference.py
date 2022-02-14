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
        self.model = blip_decoder(pretrained=pretrained_path, image_size=384, vit='base')
        self.model.to(self.device).eval()

    def predict(self, image: Union[str, Any], use_beam_search: bool = True):

        try:
            im = load_image(image, image_size=384, device=self.device)
        except:
            raise GiaImageTransformError(
                origin_err_msg=traceback.format_exc(),
                additional_err_msg="transform image for [Blip] model to predict failed."
            )

        with torch.no_grad():
            caption = self.model.generate(im, sample=not use_beam_search, num_beams=3, max_length=20, min_length=5)
            return caption[0]


def load_image(image: Union[str, Any], image_size, device):
    if isinstance(image, str):
        raw_image = io.imread(image)
        raw_image = Image.fromarray(raw_image)
    else:
        raw_image = image
    raw_image = raw_image.convert('RGB')
    w, h = raw_image.size

    transform = transforms.Compose([
        transforms.Resize((image_size, image_size), interpolation=InterpolationMode.BICUBIC),
        transforms.ToTensor(),
        transforms.Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711))
    ])
    image = transform(raw_image).unsqueeze(0).to(device)
    return image

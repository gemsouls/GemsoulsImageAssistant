# -*- coding: utf-8 -*-
# @CreateTime : 2021/12/13 14:38
# @Author     : 潘其威(PanEa)
# @Company    : Gemsouls
# @File       : nn_models_config.py
# @Description:
# @LastEditBy :

from enum import Enum
from os.path import abspath, dirname, join
import sys
from typing import *

ROOT = dirname(dirname(abspath(__file__)))
sys.path.insert(0, ROOT)

__dir_models = join(ROOT, "gia_src/nn_models")

_shared_nn_models = {
    "ClipCap_coco_weights": join(__dir_models, "ClipCap/coco_weights.pt"),
    "ClipCap_conceptual_weights": join(__dir_models, "ClipCap/conceptual_weights.pt"),
    "Blip_caption_base_weights": join(__dir_models, "Blip/blip_base_caption.pth"),
    "Blip_caption_large_weights": join(__dir_models, "Blip/blip_large_caption.pth"),
}


class ImageCaptionModelType(Enum):
    ClipCap = 0
    Blip = 1


class ClipCapModelConfig:
    coco = _shared_nn_models["ClipCap_coco_weights"]
    conceptual = _shared_nn_models["ClipCap_conceptual_weights"]


class BlipModelConfig:
    caption_base = _shared_nn_models["Blip_caption_base_weights"]
    caption_large = _shared_nn_models["Blip_caption_large_weights"]


class ImageCaptionModelConfig:
    clip_cap = ClipCapModelConfig()
    blip = BlipModelConfig()
    device = "cuda:0"  # cpu or cuda:0


class NNModelsConfig:
    image_caption = ImageCaptionModelConfig()

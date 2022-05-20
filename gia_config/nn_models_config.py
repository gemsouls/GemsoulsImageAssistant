# -*- coding: utf-8 -*-
# @CreateTime : 2021/12/13 14:38
# @Author     : 潘其威(PanEa)
# @Company    : Gemsouls
# @File       : nn_models_config.py
# @Description:
# @LastEditBy :

from os.path import abspath, dirname, join
import sys
from typing import *

ROOT = dirname(dirname(abspath(__file__)))
sys.path.insert(0, ROOT)

from gia_model.pipeline import (
    NAME_EXECUTION_PIPELINE_NN_MODELS_INITIALIZER
)

__dir_models = join(ROOT, "gia_src/nn_models")

__shared_nn_models = {
    "ClipCap_coco_weights": join(__dir_models, "ClipCap/coco_weights.pt"),
    "ClipCap_conceptual_weights": join(__dir_models, "ClipCap/conceptual_weights.pt")
}


def build_nn_models_config(
        *args,
        **kwargs
) -> Dict[str, Dict[str, str]]:
    return {
        NAME_EXECUTION_PIPELINE_NN_MODELS_INITIALIZER: {
            "pretrained_clip_cap_model_weights": __shared_nn_models["ClipCap_coco_weights"]
        }
    }

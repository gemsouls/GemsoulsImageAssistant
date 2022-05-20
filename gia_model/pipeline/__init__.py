# -*- coding: utf-8 -*-
# @CreateTime : 2021/12/13 12:26
# @Author     : 潘其威(PanEa)
# @Company    : Gemsouls
# @File       : __init__.py
# @Description:
# @LastEditBy :


from .execution_pipeline import (
    ExecutionPipeline,
    ExecutionPipelineNNModelsInitializer,
    ExecutionPipelineResourcesInitializer
)

NAME_EXECUTION_PIPELINE_NN_MODELS_INITIALIZER = ExecutionPipelineNNModelsInitializer.__name__
NAME_EXECUTION_PIPELINE_RESOURCES_INITIALIZER = ExecutionPipelineResourcesInitializer.__name__

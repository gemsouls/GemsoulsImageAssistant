# -*- coding: utf-8 -*-
# @CreateTime : 2021/12/10 15:31
# @Author     : 潘其威(PanEa)
# @Company    : Gemsouls
# @File       : run_app.py
# @Description:
# @LastEditBy :

import argparse
import logging
import uvicorn

from app import app
parser = argparse.ArgumentParser()
parser.add_argument("--host", type=str, default="0.0.0.0")
parser.add_argument("--port", type=int, default=8000)

args = parser.parse_args()


if __name__ == "__main__":
    uvicorn.run(app, port=args.port, host=args.host)

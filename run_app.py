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
parser.add_argument("--port", type=int, default=6006)
parser.add_argument("--n_proc", type=int, default=1)
parser.add_argument("--reload", action="store_true")

args = parser.parse_args()


if __name__ == "__main__":
    uvicorn.run("run_app:app", port=args.port, host=args.host, workers=args.n_proc, reload=args.reload)

# coding: utf-8
import glob
import os
import re
import sys
from io import StringIO
from subprocess import PIPE, STDOUT, Popen
from typing import *


def format_code():
    cmd = r"black . --config pyproject.toml"
    obj = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
    black_result = obj.stdout.read(100).decode("utf-8", errors="ignore")  # type: ignore

    cmd = r"isort . --settings-path pyproject.toml"
    obj = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
    isort_result = obj.stdout.read(100).decode("utf-8", errors="ignore")  # type: ignore

    cmd = r"pycodestyle . --config pyproject.toml"
    obj = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
    pycodestyle_result = obj.stdout.read(100).decode("utf-8", errors="ignore")  # type: ignore

    cmd = r"pytype input . --config pyproject.toml"
    # obj = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
    # pytype_result = obj.stdout.read().decode("utf-8", errors="ignore")  # type: ignore

    def print_result(name, result):
        print(name)
        print(result)
        print("=" * 20)

    print_result("isort", isort_result)
    print_result("isort", black_result)
    print_result("pycodestyle", pycodestyle_result)
    # print_result("pytype", pytype_result)

    assert "reformatted" not in black_result
    assert "Skipped" in isort_result
    assert "" == pycodestyle_result.strip()
    # assert "Success: no errors found" in pytype_result


def test():
    # 更新库

    # 进行测试
    res_code = os.system("python gin_test/test_src/test_model.py")
    assert res_code == 0


def clean():
    def delete_f():
        delete_flst = glob.glob("*.log") + glob.glob("*.pth") + glob.glob("*.log.*")
        for x in delete_flst:
            os.remove(x)

    delete_f()
    os.chdir("test/")
    delete_f()

    for fpath in os.listdir():
        if os.path.isdir(fpath):
            os.chdir(fpath)
            delete_f()
            os.chdir("..")


if __name__ == "__main__":
    format_code()
    test()
    # clean()

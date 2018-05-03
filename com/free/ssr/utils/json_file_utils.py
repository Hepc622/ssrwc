#!/usr/bin/ python
# -*- coding: utf-8 -*-

import json
import os
import logging
import platform
import re


# 查找json文件
def find_config_path():
    project = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    # 获取当前的工作目录
    config_path = os.path.join(project, 'shadowsocks', 'config.json')
    if os.path.exists(config_path):
        return config_path
    return None

# 打开一个json文件，并将其转为一个字典对象
# type=0为获取所有的数据，1为获取port_password的数据
def get_dict(_type=0):
    # 如果path为空的话就获取默认的路径
    path = find_config_path()
    if path is None:
        logging.info("文件路径没找到！")
        return {}
    regex3 = re.compile("3.[0-9].[0-9]")
    regex2 = re.compile("2.[0-9].[0-9]")
    if regex3.match(platform.python_version()) is not None:
        # 3.6
        # 读取文件
        with open(file=path, mode='r', encoding='utf-8') as f:
            # 将文件内容读成字典
            load_dict = json.load(f)
            if _type == 0:
                return load_dict
            else:
                return load_dict.get("port_password")
    elif regex2.match(platform.python_version()) is not None:
        # 2.7
        # 读取文件
        with open(name=path, mode='r') as f:
            # 将文件内容读成字典
            load_dict = json.load(f)
            if _type == 0:
                return load_dict
            else:
                return load_dict.get("port_password")
    return {}

# 将一个字典对象写入到文件中
def write_file(dic=None):
    # 如果path为空的话就获取默认的路径
    path = find_config_path()
    if dic is None:
        raise Exception("写入的字典参数不能为空！")
    with open(file=path,mode='w',encoding='utf-8') as f:
        json.dump(dic,f)
if __name__ == '__main__':
    print(get_dict())
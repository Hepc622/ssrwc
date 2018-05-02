#!/usr/bin/ python
#vim: set fileencoding:utf-8

from com.free.ssr.action.linux_option import Linux
import com.free.ssr.utils.json_file_utils as jfileutl
import logging
from datetime import datetime

# 获取有效的端口,也就是mark为0的
def get_valid_ports():
    config = jfileutl.get_dict(1)
    # 有效的端口
    exists = []
    for port,data in config.items():
        if data.get("mark") == 0:
            exists.append(port)
    return exists

# 获取过期的端口
def get_overdue_ports():
    config = jfileutl.get_dict(1)
    # 已经存在的port
    overdue = []
    for port,data in config:
        endTm = datetime.strptime(data.get("endTm"), "%Y-%m-%d")
        if endTm <= datetime.now():
            overdue.append(port)
    return overdue

# 处理数据，将传过来的进行一一放入到json对应的port中
def save_update_port_info(dic=None):
    if dic is not None:
        load_dict = jfileutl.get_dict()
        # 判断是修改还是添加
        port_password = load_dict.get("port_password")
        exists = False
        # 通过id 获取对应的端口数据
        for port,data in port_password.items():
            if data.get("id") == dic.get("id"):
                exists = True
                break
        if exists:
            update_port_info(dic, load_dict)
        else:
            add_port_info(dic, load_dict)
    else:
        logging.info("dic 参数不能为空")

# 修改数据
def update_port_info(dic=None, load_dict=None):
    # 去除所有的端口数据
    port_password = load_dict.get("port_password")
    # 要操作数据
    option_data = {}
    old_port = 0
    # 通过id 获取对应的端口数据
    for port,data in port_password.items():
        if data.get("id") == dic.get("id"):
            option_data = data
            old_port = port
            # 删除这个port的数据
            del port_password[port]
            break
    # 修改对应数据
    userName = dic.get("userName")
    password = dic.get("password")
    port = dic.get("port")
    method = dic.get("method")
    protocol = dic.get("protocol")
    obfs = dic.get("obfs")
    limit = dic.get("limit")
    # method = dic.get("used") 由于数据库不是最新的所以不做覆盖
    total = dic.get("total")
    # 判断是否需要更改有效标识
    beginTm = dic.get("beginTm")
    endTm = dic.get("endTm")
    mark = 1
    # 如果结束日期大于今天就将有效标签改为0
    if datetime.strptime(endTm, "%Y-%m-%d") > datetime.now():
        mark = 0

    # 设置是否有效标识
    option_data["mark"] = mark
    # 更新下面的数据
    if password is not None:
        option_data["password"] = password
    if port is not None:
        option_data["port"] = port
    if method is not None:
        option_data["method"] = method
    if protocol is not None:
        option_data["protocol"] = protocol
    if obfs is not None:
        option_data["obfs"] = obfs
    if total is not None:
        option_data["total"] = int(total)
    if beginTm is not None:
        option_data["beginTm"] = beginTm
    if total is not None:
        option_data["endTm"] = endTm
    if userName is not None:
        option_data["userName"] = userName


    # 重新设置到字典中去
    port_password[port] = option_data
    # 判断端口是否改变
    if int(port) != int(old_port):
        # 更新端口墙规则
        if Linux.update_port(old_port,port):
            logging.info("更新端口墙规则，原端口：%s,现端口：%s" %(old_port,port))
    # 更新到文件中去
    jfileutl.write_file(load_dict)
    # 重启ssr
    Linux.restart_ssr()

# 处理数据，将传过来的进行一一放入到json中
def add_port_info(dic=None, load_dict=None):
    # 去除所有的端口数据
    port_password = load_dict.get("port_password")
    # 要添加的数据
    option_data = {}
    # 修改对应数据
    id = dic.get("id")
    userId = dic.get("userId")
    userName = dic.get("userName")
    password = dic.get("password")
    port = dic.get("port")
    method = dic.get("method")
    protocol = dic.get("protocol")
    obfs = dic.get("obfs")
    limit = dic.get("limit")
    used = dic.get("used","0")
    remain = dic.get("remain","0")
    total = dic.get("total")
    beginTm = dic.get("beginTm")
    endTm = dic.get("endTm")

    # 判断是否需要更改有效标识
    mark = 1
    # 如果结束日期大于今天就将有效标签改为0
    if datetime.strptime(endTm, "%Y-%m-%d") > datetime.now():
        mark = 0

    # 设置是否有效标识
    option_data["mark"] = mark
    # 更新下面的数据
    if id is not None:
        option_data["id"] = id
    if userId is not None:
        option_data["userId"] = userId
    if userName is not None:
        option_data["userName"] = userName
    if password is not None:
        option_data["password"] = password
    if port is not None:
        option_data["port"] = port
    if method is not None:
        option_data["method"] = method
    if protocol is not None:
        option_data["protocol"] = protocol
    if obfs is not None:
        option_data["obfs"] = obfs
    if remain is not None:
        option_data["remain"] = int(total)
    if used is not None:
        option_data["used"] = int(used) if used != '' else 0
    if total is not None:
        option_data["total"] = int(total)
    if beginTm is not None:
        option_data["beginTm"] = beginTm
    if endTm is not None:
        option_data["endTm"] = endTm

    # 重新设置到字典中去
    port_password[port] = option_data
    # 判断端口是否改变
    if Linux.add_port([port]):
        logging.info("添加端口规则:%s" %(port))

    # 更新到文件中去
    jfileutl.write_file(load_dict)
    # 重启ssr
    Linux.restart_ssr()

# 删除一个数据json数据
def delete_port_info(dic=None):
    if dic is not None:
        load_dict = jfileutl.get_dict()
        # 去除所有的端口数据
        port_password = load_dict.get("port_password")
        for port,data in port_password.items():
            if data.get("id") == dic.get("id"):
                # 删除这个port的数据
                del port_password[port]
                # 需要将这个放入到history中
                break
        # 将指定端口墙了
        if Linux.delete_port([dic.get("port")]):
            pass
        # 更新到文件中去
        jfileutl.write_file(load_dict)
        # 重启ssr
        Linux.restart_ssr()
    else:
        logging.info("参数不能为空")

# 获取指定的端口
def query_valid_port_info(beginTm, endTm, begin, end):
    port_info = jfileutl.get_dict(1)
    beginTm = datetime.strptime(beginTm, "%Y-%m-%d")
    endTm = datetime.strptime(endTm, "%Y-%m-%d")
    sub = []
    # 要返回的结果
    result = []
    # 找出符合条件的数据
    for port,data in port_info.items():
        portEndTm = datetime.strptime(data.get("endTm",""), "%Y-%m-%d")
        # 判断在这个区间内的数据
        if beginTm <= portEndTm and endTm >= portEndTm:
            sub.append(data)
    # 找出指定区间内的数据
    for index,item in enumerate(sub):
        index = (index+1)
        if index >= begin and index <=end:
            result.append(item)
    return result



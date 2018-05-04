#!/usr/bin/ python
# coding: utf-8

import uuid

from flask import request, Blueprint

import com.free.ssr.action.port_service as port_service
from com.free.ssr.vo.result import Result


sa = Bluelogging.info('sa', __name__)


# 获取已经使用过的端口
@sa.route("/getPort", methods=["post"])
def get_port():
    valid = port_service.get_valid_ports()
    return Result(data=valid).get_json()


# 查询所有的用户信息
@sa.route("/query", methods=['POST'])
def query():
    begin_tm = request.form['begin']
    end_tm = request.form['end']
    page = request.form['page']
    limit = request.form['limit']
    begin = int(page) * int(limit) - int(limit)
    end = int(page) * int(limit)
    count = len(port_service.get_all_port().items())
    logging.info(count)
    # 获取出所有的数据
    order = port_service.query_valid_port_info(begin_tm, end_tm, begin, end)
    return Result(data=order, count=count).get_json()


@sa.route("/saveOrUpdate", methods=['POST'])
def saveOrUpdate():
    dic = deal_form()
    port_service.save_update_port_info(dic)
    return Result(code=0, message='修改成功').get_json()


# 指定的数据过期
@sa.route("/overdue", methods=["POST"])
def overdue():
    port_service.overdue_port_info(request.form)
    return Result(code=0, message='这个数据已过期').get_json()


# 指定的数据过期
@sa.route("/destroy", methods=["POST"])
def destroy():
    port_service.destroy_port_info(request.form)
    return Result(code=0, message='销毁成功').get_json()


# 处理表单数据
def deal_form():
    result = {}
    # 获取所有的数据
    id = request.form.get("id")
    userId = request.form.get("userId")
    userName = request.form.get("userName")
    password = request.form.get("password")
    method = request.form.get("method")
    port = request.form.get("port")
    protocol = request.form.get("protocol")
    obfs = request.form.get("obfs")
    limit = request.form.get("limit")
    used = request.form.get("used")
    remain = request.form.get("remain")
    total = request.form.get("total")
    beginTm = request.form.get("beginTm")
    endTm = request.form.get("endTm")
    # 如果用户id是空的话就需要添加用户
    if userId == '' or userId is None:
        # 生成uuid
       userId = uuid.uuid1()
    # 用户不为空,但是orderid为空,就添加orders
    if id == '' or id is None:
        # 生成uuid
        id = uuid.uuid1()

    result['id'] = str(id)
    result['userId'] = str(userId)
    result['userName'] = userName
    result['password'] = password
    result['method'] = method
    result['port'] = port
    result['protocol'] = protocol
    result['obfs'] = obfs
    result['limit'] = limit
    result['beginTm'] = beginTm
    result['endTm'] = endTm
    result['used'] = used
    result['remain'] = remain
    result['total'] = total
    return result
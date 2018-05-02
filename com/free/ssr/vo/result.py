#!/usr/bin/ python
#vim: set fileencoding:utf-8

from flask import jsonify


class Result(object):
    # 0表示请求成功，其他表示请求失败，3为没有权限
    code = 0
    # 返回给前端的消息
    message = ""
    # 返回的数据,一般都是json格式
    data = {}
    # 统计
    count = 0

    def __init__(self, code=0, message="请求成功！",count = 0, data={}):
        self.code = code
        self.message = message
        self.data = data
        self.count = count

    # 获取json，将对象转为json
    def get_json(self):
        return jsonify(self.__dict__)
#!/usr/bin/ python
# -*- coding: utf-8 -*-

import com.free.ssr.utils.token_utils as utils_token
import logging
from flask import request
from com.free.ssr.vo.result import Result


# 每个请求之前调用的方法
def auth_filter():
    # 判断是否需要验证权限,如果不需要直接放行None为不需要权限
    token = do_need_token()
    if token is None:
        # 直接放行
        return
    else:
        # 验证权限
        if utils_token.valid_token(token) is not False:
            # 验证token是否有效
            print("validate the token,if it were valid,we pass the querst")
            return
        else:
            url = request.url.split("?")[0]
            if url.find("/login") != -1:
                return
            else:
                return Result(code=3, message="请登录重新登录！").get_json()


# 从请求中获取token,返回None标识不需要权限,可以直接放行,如果是非None就说明是要验证token的
def do_need_token():
    # 判断是post请求还是get请求,如果是post请求,
    # 必须验证token的有效性,如果没有token,或失效token就不允许通过
    # 如果是get请求的话判断是否为,静态文件请求或（404,error页面）,
    # 如果是静态文件请求直接放行,否则就需要判断token的有效性,
    if request.method == "POST":
        token = request.form.get('token')
        # 获取客户端带来的token
        return token if token is not None else ""
    elif request.method == "GET":
        return None
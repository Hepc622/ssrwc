#!/usr/bin/ python
# -*- coding: utf-8 -*-

import hashlib

import com.free.ssr.utils.token_utils as token_utils
from flask import request, redirect, Blueprint
from com.free.ssr.vo.result import Result
import logging


sl = Blueprint('sl', __name__)


@sl.route('/login', methods=['POST'])
def login():
    user_name = request.form['username']
    pwd = request.form['password']
    hl = hashlib.md5()
    hl.update(pwd.encode(encoding='utf-8'))
    print(user_name, hl.hexdigest())
    if user_name == 'admin' and hl.hexdigest() == 'd6d2c08b5e680606776e1a8ea1c9fdbd':
        user = {
            'userName': user_name
        }
        logging.info("用户存在，就生成token,返回给前段页面")
        token = token_utils.create_token(user)
        user['token'] = token
        # 获取用户的基本信息
        return Result(data=user).get_json()
    else:
        return Result(code=1, message='用户名或密码错误！').get_json()


@sl.route('/login_out', methods=["GET"])
def login_out():
    logging.info("用户退出登录了")
    # 获取用户的基本信息
    return redirect("static/pages/login.html")


@sl.route("/")
def hello():
    return redirect("static/pages/index.html")


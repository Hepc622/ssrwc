#!/usr/bin/python
# coding: utf-8

import hashlib

import com.free.ssr.utils.token_utils as token_utils
from flask import request, redirect, Blueprint
from com.free.ssr.vo.result import Result



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
        print("The use exist,create a token return to page")
        token = token_utils.create_token(user)
        user['token'] = token
        # 获取用户的基本信息
        return Result(data=user).get_json()
    else:
        return Result(code=1, message='用户名或密码错误!').get_json()


@sl.route('/login_out', methods=["GET"])
def login_out():
    print("user login out")
    # 获取用户的基本信息
    return redirect("static/pages/login.html")


@sl.route("/")
def hello():
    return redirect("static/pages/index.html")


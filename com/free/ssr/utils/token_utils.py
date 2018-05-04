#!/usr/bin/ python
# coding: utf-8

import jwt
import time
secret = "adminhpc"


def create_token(play_load):
    play_load['iss'] = "sys"
    play_load['exp'] = (time.time()+1800)
    play_load['iat'] = time.time()
    # byte2string解码成str
    token = bytes.decode(jwt.encode(play_load, secret))
    return token


# 校验token
def valid_token(valid):
    try:
        return jwt.decode(valid, secret)
    except Exception:
        return False


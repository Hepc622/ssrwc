#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2015 clowwindy
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import absolute_import, division, print_function, \
    with_statement

import sys
import os
import logging
import signal

if __name__ == '__main__':
    import inspect
    file_path = os.path.dirname(os.path.realpath(inspect.getfile(inspect.currentframe())))
    os.chdir(file_path)
    sys.path.insert(0, os.path.join(file_path, '../'))

from shadowsocks import shell, daemon, eventloop, tcprelay, udprelay, \
    asyncdns, manager


def main():
    shell.check_python()
    # 获取配置文件，如果没有配置文件将给与默认的配置,配置如下
    """
    {
    "server": "0.0.0.0",
    "server_ipv6": "::",
    "server_port": 8388,
    "local_address": "127.0.0.1",
    "local_port": 1080,
    "password": "123",
    "timeout": 120,
    "udp_timeout": 60,
    "method": "aes-256-cfb",
    "protocol": "origin",
    "protocol_param": "",
    "obfs": "http_simple_compatible",
    "obfs_param": "",
    "dns_ipv6": false,
    "connect_verbose_info": 0,
    "redirect": "",
    "fast_open": false
    }
    """
    config = shell.get_config(False)

    daemon.daemon_exec(config)

    # 写了port_password的配置
    if config['port_password']:
        # 用了password就不用port_password
        if config['password']:
            logging.warn('warning: port_password should not be used with '
                         'server_port and password. server_port and password '
                         'will be ignored')
    else:
        # 没有写入port_password配置的情况
        config['port_password'] = {}
        server_port = config['server_port']
        # 判断服务器端口是否为一个数组是的话就，使用password作为密码的放在port_password中
        if type(server_port) == list:
            for a_server_port in server_port:
                config['port_password'][a_server_port] = config['password']
        else:
            config['port_password'][str(server_port)] = config['password']
            # 组装完如下
            # """
            #     port_password:{
            #         port:password
            #     }
            # """
    # 是否启动了dns_ipv6
    if not config.get('dns_ipv6', False):
        asyncdns.IPV6_CONNECTION_SUPPORT = False

    # 使用启用了管理者
    if config.get('manager', 0):
        logging.info('entering manager mode')
        # 判断是否使用管理者？？？？这里我也还没有看源码
        manager.run(config) 
        return


if __name__ == '__main__':
    main()

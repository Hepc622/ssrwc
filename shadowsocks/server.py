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

        "password": "m",
        "method": "aes-128-ctr",
        "protocol": "auth_aes128_md5",
        "protocol_param": "",
        "obfs": "tls1.2_ticket_auth_compatible",
        "obfs_param": "",
        "speed_limit_per_con": 0,
        "speed_limit_per_user": 0,

        "additional_ports" : {}, // only works under multi-user mode
        "additional_ports_only" : false, // only works under multi-user mode
        "timeout": 120,
        "udp_timeout": 60,
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
    if config.get('manager_address', 0):
        logging.info('entering manager mode')
        # 判断是否使用管理者？？？？这里我也还没有看源码
        manager.run(config) 
        return

    tcp_servers = []
    udp_servers = []
    dns_resolver = asyncdns.DNSResolver()
    port_password = config['port_password']
    # 删除port_password这个数据
    del config['port_password']
    for port, password_obfs in port_password.items():
        method = config.get("method")
        # 协议加密
        protocol = config.get("protocol", 'origin')
        # 获取混淆参数
        obfs_param = config.get("obfs_param", '')
        # 判断是否是一个数组，格式如下
        """ 
        port_password:{
            port:['password','obfs'],
            port:['password','obfs'],
            ....
        }
        """
        if type(password_obfs) == list:
            password = password_obfs[0]
            obfs = password_obfs[1]
        elif type(password_obfs) == dict:
            # 字典的情况下,格式如下
            """ 
            port_password:{
                port:{
                    password:password,
                    protocol:protocol,
                    obfs:obfs,
                    obfs_param:obfs_param
                },
                ....
            }
            """
            # 如果是1的话表示无效的状态0表示正常
            if password_obfs.get("mark",0) == 1:
                continue
            # 密码
            password = password_obfs.get('password', 'm')
            # 协议
            protocol = password_obfs.get('protocol', 'origin')
            # 混淆方式
            obfs = password_obfs.get('obfs', 'plain')
            # 混淆参数
            obfs_param = password_obfs.get('obfs_param', '')
            # 获取加密方式
            method = password_obfs.get("method", 'aes-256-cfb')
        else:
            password = password_obfs
            obfs = config["obfs"]
        a_config = config.copy()
        ipv6_ok = False
        logging.info("server start with protocol[%s] password [%s] method [%s] obfs [%s] obfs_param [%s]" %
                (protocol, password, method, obfs, obfs_param))
        if 'server_ipv6' in a_config:
            try:
                if len(a_config['server_ipv6']) > 2 and a_config['server_ipv6'][0] == "[" and a_config['server_ipv6'][-1] == "]":
                    a_config['server_ipv6'] = a_config['server_ipv6'][1:-1]
                a_config['server_port'] = int(port)
                a_config['password'] = password
                # 使用port_password中的加密方式
                a_config['method'] = method
                a_config['protocol'] = protocol
                a_config['obfs'] = obfs
                a_config['obfs_param'] = obfs_param
                a_config['server'] = a_config['server_ipv6']

                logging.info("starting server at [%s]:%d" %
                             (a_config['server'], int(port)))
                tcp_servers.append(tcprelay.TCPRelay(a_config, dns_resolver, False))
                udp_servers.append(udprelay.UDPRelay(a_config, dns_resolver, False))
                if a_config['server_ipv6'] == b"::":
                    ipv6_ok = True
            except Exception as e:
                shell.print_exception(e)

        try:
            a_config = config.copy()
            a_config['server_port'] = int(port)
            a_config['password'] = password
            # 使用port_password中的加密方式
            a_config['method'] = method
            a_config['protocol'] = protocol
            a_config['obfs'] = obfs
            a_config['obfs_param'] = obfs_param
            logging.info("starting server at %s:%d" %
                         (a_config['server'], int(port)))
            tcp_servers.append(tcprelay.TCPRelay(a_config, dns_resolver, False))
            udp_servers.append(udprelay.UDPRelay(a_config, dns_resolver, False))
        except Exception as e:
            if not ipv6_ok:
                shell.print_exception(e)

    def run_server():
        def child_handler(signum, _):
            logging.warn('received SIGQUIT, doing graceful shutting down..')
            list(map(lambda s: s.close(next_tick=True),
                     tcp_servers + udp_servers))
        signal.signal(getattr(signal, 'SIGQUIT', signal.SIGTERM),
                      child_handler)

        def int_handler(signum, _):
            sys.exit(1)
        signal.signal(signal.SIGINT, int_handler)

        try:
            loop = eventloop.EventLoop()
            dns_resolver.add_to_loop(loop)
            list(map(lambda s: s.add_to_loop(loop), tcp_servers + udp_servers))

            daemon.set_user(config.get('user', None))
            loop.run()
        except Exception as e:
            shell.print_exception(e)
            sys.exit(1)

    if int(config['workers']) > 1:
        if os.name == 'posix':
            children = []
            is_child = False
            for i in range(0, int(config['workers'])):
                r = os.fork()
                if r == 0:
                    logging.info('worker started')
                    is_child = True
                    run_server()
                    break
                else:
                    children.append(r)
            if not is_child:
                def handler(signum, _):
                    for pid in children:
                        try:
                            os.kill(pid, signum)
                            os.waitpid(pid, 0)
                        except OSError:  # child may already exited
                            pass
                    sys.exit()
                signal.signal(signal.SIGTERM, handler)
                signal.signal(signal.SIGQUIT, handler)
                signal.signal(signal.SIGINT, handler)

                # master
                for a_tcp_server in tcp_servers:
                    a_tcp_server.close()
                for a_udp_server in udp_servers:
                    a_udp_server.close()
                dns_resolver.close()

                for child in children:
                    os.waitpid(child, 0)
        else:
            logging.warn('worker is only available on Unix/Linux')
            run_server()
    else:
        run_server()


if __name__ == '__main__':
    main()

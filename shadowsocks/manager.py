#!/usr/bin/python
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

import errno
import traceback
import socket
import logging
import json
import collections

from shadowsocks import common, eventloop, tcprelay, udprelay, asyncdns, shell


BUF_SIZE = 1506
STAT_SEND_LIMIT = 50


class Manager(object):

    def __init__(self, config):
        self._config = config
        self._relays = {}  # (tcprelay, udprelay)
        self._loop = eventloop.EventLoop()
        self._dns_resolver = asyncdns.DNSResolver()
        self._dns_resolver.add_to_loop(self._loop)

        port_password = config['port_password']
        # 删除port_password这个数据
        del config['port_password']
        for port, password_obfs in port_password.items():
            # 默认参数
            # 加密方式
            method = config.get("method", 'aes-256-cfb')
            # 用户密码
            password = config.get("password", 'password')
            # 协议加密
            protocol = config.get("protocol", 'origin')
            # 混淆方式
            obfs = config.get("obfs","plain")
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
                if password_obfs.get("flowMark",0) == 1 or password_obfs.get("dateMark",0) == 1:
                    continue
                # 密码
                password = password_obfs.get('password', 'm')
                # 协议
                protocol = password_obfs.get('protocol', 'origin')
                # 协议参数
                protocol_param = password_obfs.get('protocol_param', '')
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
            a_config['server_port'] = port
            a_config['password'] = password
            a_config['protocol'] = protocol
            a_config['protocol_param'] = protocol_param
            a_config['obfs'] = obfs
            a_config['obfs_param'] = obfs_param
            a_config['method'] = method
            # 覆盖a_config
            self.add_port(a_config)


    def add_port(self, config):
        port = int(config['server_port'])
        servers = self._relays.get(port, None)
        if servers:
            logging.error("server already exists at %s:%d" % (config['server'],
                                                              port))
            # 端口存在返回false启动失败
            return "添加失败,端口已经存在！"
        logging.info("adding server at %s:%d" % (config['server'], port))
        t = tcprelay.TCPRelay(config, self._dns_resolver, False,
                              self.stat_callback)
        u = udprelay.UDPRelay(config, self._dns_resolver, False,
                              self.stat_callback)
        t.add_to_loop(self._loop)
        u.add_to_loop(self._loop)
        self._relays[port] = (t, u)
        if t and u :
            # 添加成功
            return "添加成功！"

    def remove_port(self, config):
        port = int(config['server_port'])
        servers = self._relays.get(port, None)
        if servers:
            logging.info("removing server at %s:%d" % (config['server'], port))
            t, u = servers
            t.close(next_tick=False)
            u.close(next_tick=False)
            del self._relays[port]
            # 移除成功
            return "端口移除成功"
        else:
            logging.error("server not exist at %s:%d" % (config['server'],
                                                         port))
            # 移除失败，端口未启动
            return "端口移除失败,端口未启动！"

    def handle_event(self, sock, fd, event):
        if sock == self._control_socket and event == eventloop.POLL_IN:
            data, self._control_client_addr = sock.recvfrom(BUF_SIZE)
            parsed = self._parse_command(data)
            if parsed:
                command, config = parsed
                a_config = self._config.copy()
                if config:
                    # let the command override the configuration file
                    a_config.update(config)
                if 'server_port' not in a_config:
                    logging.error('can not find server_port in config')
                else:
                    if command == 'add':
                        self.add_port(a_config)
                        self._send_control_data(b'ok')
                    elif command == 'remove':
                        self.remove_port(a_config)
                        self._send_control_data(b'ok')
                    elif command == 'ping':
                        self._send_control_data(b'pong')
                    else:
                        logging.error('unknown command %s', command)

    def _parse_command(self, data):
        # commands:
        # add: {"server_port": 8000, "password": "foobar"}
        # remove: {"server_port": 8000"}
        data = common.to_str(data)
        parts = data.split(':', 1)
        if len(parts) < 2:
            return data, None
        command, config_json = parts
        try:
            config = shell.parse_json_in_str(config_json)
            return command, config
        except Exception as e:
            logging.error(e)
            return None

    def stat_callback(self, port, data_len):
        self._statistics[port] += data_len

    def handle_periodic(self):
        r = {}
        i = 0

        def send_data(data_dict):
            if data_dict:
                # use compact JSON format (without space)
                data = common.to_bytes(json.dumps(data_dict,
                                                  separators=(',', ':')))
                self._send_control_data(b'stat: ' + data)

        for k, v in self._statistics.items():
            r[k] = v
            i += 1
            # split the data into segments that fit in UDP packets
            if i >= STAT_SEND_LIMIT:
                send_data(r)
                r.clear()
                i = 0
        if len(r) > 0 :
            send_data(r)
        self._statistics.clear()

    def _send_control_data(self, data):
        if self._control_client_addr:
            try:
                self._control_socket.sendto(data, self._control_client_addr)
            except (socket.error, OSError, IOError) as e:
                error_no = eventloop.errno_from_exception(e)
                if error_no in (errno.EAGAIN, errno.EINPROGRESS,
                                errno.EWOULDBLOCK):
                    return
                else:
                    shell.print_exception(e)
                    if self._config['verbose']:
                        traceback.print_exc()

    def run(self):
        self._loop.run()


def run(config):
    Manager(config).run()


def test():
    import time
    import threading
    import struct
    from shadowsocks import encrypt

    logging.basicConfig(level=5,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    enc = []
    eventloop.TIMEOUT_PRECISION = 1

    def run_server():
        config = {
            'server': '127.0.0.1',
            'local_port': 1081,
            'port_password': {
                '8381': 'foobar1',
                '8382': 'foobar2'
            },
            'method': 'aes-256-cfb',
            'manager_address': '127.0.0.1:6001',
            'timeout': 60,
            'fast_open': False,
            'verbose': 2
        }
        manager = Manager(config)
        enc.append(manager)
        manager.run()

    t = threading.Thread(target=run_server)
    t.start()
    time.sleep(1)
    manager = enc[0]
    cli = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cli.connect(('127.0.0.1', 6001))

    # test add and remove
    time.sleep(1)
    cli.send(b'add: {"server_port":7001, "password":"asdfadsfasdf"}')
    time.sleep(1)
    assert 7001 in manager._relays
    data, addr = cli.recvfrom(1506)
    assert b'ok' in data

    cli.send(b'remove: {"server_port":8381}')
    time.sleep(1)
    assert 8381 not in manager._relays
    data, addr = cli.recvfrom(1506)
    assert b'ok' in data
    logging.info('add and remove test passed')

    # test statistics for TCP
    header = common.pack_addr(b'google.com') + struct.pack('>H', 80)
    data = encrypt.encrypt_all(b'asdfadsfasdf', 'aes-256-cfb', 1,
                               header + b'GET /\r\n\r\n')
    tcp_cli = socket.socket()
    tcp_cli.connect(('127.0.0.1', 7001))
    tcp_cli.send(data)
    tcp_cli.recv(4096)
    tcp_cli.close()

    data, addr = cli.recvfrom(1506)
    data = common.to_str(data)
    assert data.startswith('stat: ')
    data = data.split('stat:')[1]
    stats = shell.parse_json_in_str(data)
    assert '7001' in stats
    logging.info('TCP statistics test passed')

    # test statistics for UDP
    header = common.pack_addr(b'127.0.0.1') + struct.pack('>H', 80)
    data = encrypt.encrypt_all(b'foobar2', 'aes-256-cfb', 1,
                               header + b'test')
    udp_cli = socket.socket(type=socket.SOCK_DGRAM)
    udp_cli.sendto(data, ('127.0.0.1', 8382))
    tcp_cli.close()

    data, addr = cli.recvfrom(1506)
    data = common.to_str(data)
    assert data.startswith('stat: ')
    data = data.split('stat:')[1]
    stats = json.loads(data)
    assert '8382' in stats
    logging.info('UDP statistics test passed')

    manager._loop.stop()
    t.join()


if __name__ == '__main__':
    test()

#!/usr/bin/ python
# coding: utf-8

import os
import pymysql
import threading
import time
import traceback
import yaml
import logging
from com.free.ssr.utils.connect import Connect

# 链接池
class ConnectPool(object):
    # 这是yml配置文件读出来后,转为字典
    __db_dict = None
    # 链接池
    __connects = []
    # 当前对象锁
    __lock = threading.Lock()
    # 连接池对象
    __pool = None

    def __new__(cls, *args, **kwargs):
        if cls.__pool is None:
            # 调用创建连接池
            cls.__init_pool(cls)
            # 插件对象,实例其父类
            cls.__pool = super(ConnectPool, cls).__new__(cls)
        return cls.__pool

    # 返回连接池总大小
    def get_pool_size(self):
        self.__lock.acquire()
        size = len(self.__connects_using)+len(self.__connects_remain)
        self.__lock.release()
        return size

    # 获取连接池所剩的数量
    def get_pool_free(self):
        self.__lock.acquire()
        count = 0
        for connect in self.__connects:
            if connect.get_free():
                count += 1
        self.__lock.release()
        return count

    # 获取连接池使用的数量
    def get_pool_using(self):
        self.__lock.acquire()
        count = 0
        for connect in self.__connects:
            if not connect.get_free():
                count += 1
        self.__lock.release()
        return count

    # 初始化方法,创建链接池
    def __init_pool(self):
        # 获取配置文件
        path = os.path.join(os.getcwd(),"db_conf.yml")
        # 打开配置文件
        with open(file=path, mode='rt', encoding='utf-8') as f:
            # 用yaml读取出来,再转为字典对象
            self.__db_dict = dict(yaml.load(f))
        # 初始化默认配置
        if self.__db_dict.get('user') is None:
            self.__db_dict['user'] = 'root'
        if self.__db_dict.get('password') is None:
            self.__db_dict['password'] = '123456'
        if self.__db_dict.get('database') is None:
            self.__db_dict['database'] = 'db'
        if self.__db_dict.get('host') is None:
            self.__db_dict['host'] = 'localhost'
        if self.__db_dict.get('port') is None:
            self.__db_dict['port'] = 3306
        if self.__db_dict.get('charset') is None:
            self.__db_dict['charset'] = 'utf8'
        if self.__db_dict.get('maxPoolSize') is None:
            self.__db_dict['maxPoolSize'] = 20
        if self.__db_dict.get('minPoolSize') is None:
            self.__db_dict['minPoolSize'] = 1
        if self.__db_dict.get('initPoolSize') is None:
            self.__db_dict['initPoolSize'] = 3
        if self.__db_dict.get('waitTime') is None:
            self.__db_dict['waitTime'] = 0.005
        if self.__db_dict.get('autoCommitOnClose') is None:
            self.__db_dict['autoCommitOnClose'] = False
        try:
            # 获取配置文件配置参数
            p_max = self.__db_dict.get('maxPoolSize')
            p_min = self.__db_dict.get('minPoolSize')
            p_init = self.__db_dict.get('initPoolSize')
            # 判断一下连接池最小值是否大于连接池最大值
            if p_min > p_max:
                raise Exception('''链接池的最小值大于最大值,请重新设定''')
            # 初始化链接池大小
            for i in range(p_init):
                connect = self.__create_connect(self)
                # 判断链接池的大小是否小于最大值
                if len(self.__connects) <= p_max:
                    self.__connects.append(Connect(connect))
                else:
                    raise Exception('初始化大小,大于最大值')
        except IOError:
            # 打印异常
            traceback.print_exception()
            # 打印执行过程
            traceback.print_exc()
        logging.info("连接池初始化完成")

    # 获取链接
    def get_connect(self):
        # 开启同步
        self.__lock.acquire()
        # 需要返回的数据链接
        connect = None
        # 获取一个空闲的连接,不知道是否有效
        connect = self.__get_real_connect()
        if connect is None:
            # 如果没有空闲连接了,就看看链接池的最大是有没有达到配置的最大值,没有的话就去创建,有的等待其他连接释放连接
            if len(self.__connects) < self.__db_dict.get("maxPoolSize"):
                # 没有达到最大值,所以就再去创建链接了
                connect = Connect(self.__create_connect())
                self.__connects.append(connect)
                self.__show_pool_num("小于20去创建了一个连接：", connect)
            else:
                # 达到最大值了,在这里等等吧
                while connect is None:
                    time.sleep(self.__db_dict.get("waitTime"))
                    # 获取线程池也有的空闲连接
                    connect = self.__get_real_connect()
                    # self.__show_pool_num("连接池中没有空闲,等了会才拿出来的：", connect)
        else:
            #  把状态设置为忙碌
            connect.set_free(False)
            self.__show_pool_num("连接池中有空闲连接直接拿出来", connect)
        #  释放,关闭同步
        self.__lock.release()
        return connect

    # 获取真实有效的连接
    def __get_real_connect(self):
        connect = None
        # 获取线程池也有的空闲连接
        for conn in self.__connects:
            if conn.get_free():
                try:
                    # 如果ping不通说明是无效链接,如果ping通了直接返回就行
                    conn.ping()
                except Exception:
                    # 没有ping通,重新生成一个链接
                    conn = Connect(self.__create_connect())
                connect = conn
                break
        return connect
    # 显示数据池中的链接情况
    def __show_pool_num(self,str,connect):
        count = 0
        for con in self.__connects:
            if con.get_free():
                count += 1
        logging.info("当前线程", threading.current_thread().name,
              str+": ", connect,
              "当前连接池数总数: ", len(self.__connects),
              "正在使用的链接数： ", (len(self.__connects)-count),
              "空闲连接数： ",count)

    # 创建链接
    def __create_connect(self):
        user = self.__db_dict.get('user')
        password = self.__db_dict.get('password')
        host = self.__db_dict.get('host')
        port = self.__db_dict.get('port')
        databases = self.__db_dict.get('database')
        charset = self.__db_dict.get('charset')
        return pymysql.connect(host=host, port=port, user=user, passwd=password, db=databases, charset=charset)
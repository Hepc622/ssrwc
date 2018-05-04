#!/usr/bin/python
# coding: utf-8

import re
import traceback
import pymysql
import sys



# 链接对象
class Connect(object):
    # 链接对象
    __connect = None
    # 是否空闲
    __free = True

    def __new__(cls, *args, **kwargs):
        cls.__connect = args[0]
        return object.__new__(cls)

    # 获取真实的connect链接
    def get_original_conn(self):
        return self.__connect

    # 获取当前的链接是否空闲
    def get_free(self):
        return self.__free

    # 设置当前的链接是否空闲
    def set_free(self, flag):
        self.__free = flag

    # 关闭连接,设置为空闲状态
    def close(self):
        self.__free = True
        # print("当前线程", threading.current_thread().name, "这个链接空闲了：", self.__connect)

    # 处理sql
    def deal_sql(self, sql, params):
        re_compile = re.compile("[\'=-]")
        for item in params:
            # 判断是否有敏感字符
            if len(re_compile.findall(item)) > 0:
                return None
        if sql.find("?") > 0:
            for item in params:
                sql = sql.replace("?", "'"+str(item)+"'", 1)
            return sql
        elif sql.find("#") > 0:
            # 创建正则表达式
            re_compile = re.compile("#[\w]+")
            # 将参数设置到sql语句中
            for item in params[0]:
                for key in re_compile.findall(sql):
                    if key.find(item) > 0:
                        sql = sql.replace(key, "'"+str(params[0][item])+"'", 1)
            # 将没有的参数至为1=1
            re_compile = re.compile("[\w]+=#[\w]+")
            findall = re_compile.findall(sql)
            for repl in findall:
                sql = sql.replace(repl, '1=1', 1)
            return sql
        return sql

    # 查询所有
    def select_all(self, sql, *params):
        sql = self.deal_sql(sql, params)
        print(sql)
        try:
            # 获取当前游标的位置
            cursor = self.__connect.cursor(cursor=pymysql.cursors.DictCursor)
            # 执行sql
            cursor.execute(sql)
            # 获取所有数据数据
            data = cursor.fetchall()
            # 返回数据
            return data
        except Exception:
            traceback.print_exc()
        finally:
            cursor.close()
            # 将当前连接置为空闲
            self.close()

        # 插入数据
    def insert(self, sql, *params):
        sql = self.deal_sql(sql, params)
        try:
            # 获取当前游标的位置
            cursor = self.__connect.cursor()
            # 执行sql
            cursor.execute(sql)
            # 将数据提交到数据库中
            self.__connect.commit()
            return True
        except Exception:
            traceback.print_exc()
            # 回滚数据
            self.__connect.rollback()
            return False
        finally:
            # 关闭链接
            cursor.close()

        # 更新数据
    def update(self, sql, *params):
        sql = self.deal_sql(sql, params)
        try:
            # 获取当前游标的位置
            cursor = self.__connect.cursor()
            # 执行sql
            cursor.execute(sql)
            # 将数据提交到数据库中
            self.__connect.commit()
            return True
        except Exception:
            traceback.print_exc()
            # 回滚数据
            self.__connect.rollback()
            return False
        finally:
            # 关闭链接
            cursor.close()


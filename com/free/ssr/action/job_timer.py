#!/usr/bin/ python
#vim: set fileencoding:utf-8

import threading
import datetime
import logging
import time

import com.free.ssr.action.jobs as _jobs


# 定时任务
class Job(object):
    jobs = []

    # 添加任务
    """
        typ=0 每天0点执行
        typ=1 每天h点执行
        typ=2 每天h点m分执行
        typ=3 每天h点m分s秒执行
        typ=4 每N小时执行一次
        typ=5 每N分钟执行一次
        typ=6 每N秒执行一次
        typ=7 每个月第N号执行一次
        typ=8 每N天执行一次
    """
    def add_job(self, job, typ=0, day=1, h=0, m=0, s=0):
        job_dict = {'job': job, 'type':typ, 'day': day, 'hour': h, 'minute': m, 'second': s}
        self.jobs.append(job_dict)

    # 定时任务执行方法
    def do_something(self, job):
        job()
        
    def to_do(self, job=None,typ=0, day=1, h=0, m=0, s=0):
        # h表示设定的小时，m为设定的分钟
        while True: 
            # 等于6的话，每秒执行一次
            if typ is not 6:
                while True:
                    if typ is 8:
                        # 每N天执行一次
                        time.sleep(60*60*24*day)
                        break
                    elif typ is 7:
                        # 每天执一次
                        time.sleep(60*60*24)
                        now = datetime.datetime.now()
                        if now.day is day:
                            break
                    elif typ is 5:
                        # 每分钟执行一次
                        time.sleep(60*(m if m is not 0 else 1))
                        break
                    elif typ is 4:
                        # 每小时执行一次
                        time.sleep(60*(h if h is not 0 else 60))
                        break
                    elif typ is 3:
                        now = datetime.datetime.now()
                        # 每天h点m分s秒执行
                        if now.hour is not h:
                            time.sleep(55)
                        else:
                            time.sleep(1)
                        if now.hour is h and now.minute is m and now.second is s:
                            break
                    elif typ is 2:
                        now = datetime.datetime.now()
                         # 每天h点m分执行
                        if now.hour is not h:
                            time.sleep(55)
                        else:
                            time.sleep(1)
                        if now.hour is h and now.minute is m and now.second is s:
                            break
                    elif typ is 1:
                        now = datetime.datetime.now()
                        # 每天h点执行
                        if now.hour is not h:
                            time.sleep(60)
                        else:
                            time.sleep(1)
                        if now.hour is h and now.minute is m and now.second is s:
                            break
                    elif typ is 0:
                        now = datetime.datetime.now()
                        # 每天0点执行
                        if now.hour is not h:
                            time.sleep(60)
                        else:
                            time.sleep(1)
                        if now.hour is 0 and now.minute is m and now.second is s:
                            break
                # 执行方法
                self.do_something(job)
            else:
                # 执行方法 每秒执行一次
                self.do_something(job)
                time.sleep(1*(s if s is not 0 else 1))

            

    #   运行所有的job
    def run(self):
        # 循环去执行每一方法，每一个方法都开一个线程去执行
        for j_dict in self.jobs:
            fun = j_dict.get('job')
            typ = j_dict.get('type')
            day = j_dict.get('day')
            h = j_dict.get('hour')
            m = j_dict.get('minute')
            s = j_dict.get('second')
            if hasattr(fun, "__call__"):
                logging.info(fun, "start....")
                threading.Thread(target=self.to_do, args=(fun, typ, day, h, m, s,))
            else:
                break
    @staticmethod
    def start():
        """
            typ=0 每天0点执行
            typ=1 每天h点执行
            typ=2 每天h点m分执行
            typ=3 每天h点m分s秒执行
            typ=4 每N小时执行一次
            typ=5 每N分钟执行一次
            typ=6 每N秒执行一次
            typ=7 每个月第N号执行一次
            typ=8 每N天执行一次
        """
        job = Job()
        # 检查是否过期
        job.add_job(_jobs.validate_dealine, typ=0)
        # 将统计的流量插入到数据库中去
        # job.add_job(_jobs.updateJson2Mysql, typ=0)
        # 检查速锐是否开启
        job.add_job(_jobs.check_serverSpeeder_is_run, typ=0)
        # 统计流量
        job.add_job(_jobs.count_flow, typ=5, m=10)
        # 每个月1号将所有的流量清空
        job.add_job(_jobs.clear_port_flow, typ=7, day=1)
        job.run()

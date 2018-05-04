#!/usr/bin/ python
# -*- coding: utf-8 -*-

import com.free.ssr.action.port_service as port_service
import com.free.ssr.utils.json_file_utils as jfileutl
import logging
from com.free.ssr.action.linux_option import Linux


# 每天0点检查该服务器的所有端口的有效期,如果过期了,需要将这个端口给墙了
def validate_dealine(self):
    # 获取已经过期的port
    port_service.check_port_date()
    overdue = port_service.get_overdue_ports()
    # 先查一下这些端口是否在开放,如果开发就将他关闭
    if Linux.check_ports_open(overdue):
        print("The overdue ports %s" %(overdue,))
        # 将这些端口墙了
        Linux.delete_port(overdue)
        # 重启ssr
        Linux.restart_ssr()

# 统计每一个端口的流量,10分钟执行一次
def count_flow():
    # 取出配置文件,且获取出要操作的那些数据
    ssrj = jfileutl.get_dict()
    port_info = ssrj.get("port_password")
    # 获取每个端口产生的流量
    port_dic = Linux.count_all_port()
    # 记录是否有超出流量的用户,有的话需要重启一下ssr,重新加载一下配置文件
    reboot_ssr = False
    # 遍历字典
    for port,flow in port_dic.items():
        # 获取出对应的端口数据
        port_data = port_info.get(port)
        # 获取出该端口是否有效,有效才去更改数据
        flowMark = port_data.get("flowMark")
        # 只更改有效的端口
        if int(flowMark) == 0:
            # 获取最大数
            total = int(port_data.get("total"))
            # 计算出剩余的流量
            remain = total-flow
            # 设置剩余的流量
            port_data['remain'] = 0 if remain <= 0 else remain
            # 设置用的流量
            port_data['used'] = int(port_data.get("used"))+flow
            # 判断剩余的流量是否小于0,是的话需要将该端口的flowMark至为1
            if remain <= 0:
                # 将标志至为无效
                port_data['flowMark'] = 1
                # 这里不能把端口给墙了只能去重启一下ssr让他重新读取一下配置文件,因为只是流量超出了,而不是过期了
                reboot_ssr = True

	# 判断是否需要重启ssr
    if reboot_ssr:
        print("have some customer flow out of the total,need restart the ssr software,The user info：%s" % (ssrj,))
        jfileutl.write_file(ssrj)
        # 重启ssr
        Linux.restart_ssr()

# 每个月的1号0点清除所有的流量
def clear_port_flow():
    # 获取有效的端口
    valid_port = port_service.get_valid_ports()
    # 将他们的端口号至为flowMark都至为0
    # 取出配置文件,且获取出要操作的那些数据 
    ssrj = jfileutl.get_dict()
    port_info = ssrj.get('port_password')
    for port in valid_port:
        port_data = port_info.get(port)
        port_data["flowMark"] = 0
        # 将他们的流量都清空
        port_data["used"] = 0
        port_data["remain"] = port_data["total"]
    print("The 1st of every month clear the flows,clear after the data：" % (ssrj,))
    # 写到文件里去
    jfileutl.write_file(ssrj)
    # 将OUTPUT表中的数据流量全部清空
    Linux.clear_output_port_flow()
    # 重启ssr
    Linux.restart_ssr()


# 把json的数据写到数据库中去,每天0点执行
# def updateJson2Mysql():
#     # 获取所有的端口信息
#     ssrj = jfileutl.get_dict()['port_password']
#     # 获取对应端口的对应数据
#     for port,data in ssrj.items():
#         port_service.update_port_flow(data)

# 检查锐速是否开启,没有开启将其开启。每天0点执行
def check_serverSpeeder_is_run():
    # 检查是否开启了加速
    if not Linux.serverSpeeder_is_run():
        print("The serverSpeeder did`t runing,starting the serverSpeeder...")
        # 启动加速
        Linux.start_serverSpeeder()
        
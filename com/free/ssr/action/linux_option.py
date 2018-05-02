#!/usr/bin/ python
#vim: set fileencoding:utf-8

import os
import logging
class Linux:

	# 给防火墙添加一个或多个放行端口
	@staticmethod
	def add_port(ports):
		for port in ports:
			# 添加tcp port
			command = "iptables -I INPUT -p tcp --dport %s -j ACCEPT && " \
			 		  "iptables -I INPUT -p udp --dport %s -j ACCEPT && " \
			 		  "iptables -I OUTPUT -p tcp --sport %s -j ACCEPT && " \
					  "iptables -I OUTPUT -p udp --sport %s -j ACCEPT" \
					  %(port, port, port, port)
			logging.info("添加防火墙端口，执行代码：\n %s" %(command,))
			# 检查是否成功
			if Linux.ckcomsuccess(os.popen(command).readlines(),command):
				logging.info("插入成功")
		# 保存新修改的规则
		return Linux.save_rules()

	# 移除一个或多个端口
	@staticmethod
	def delete_port(ports):
		# 解包去除第一元素
		for port in ports:
			# 添加tcp port
			command = "iptables -D INPUT -p tcp --dport %s -j ACCEPT && " \
			 		  "iptables -D INPUT -p udp --dport %s -j ACCEPT && " \
			 		  "iptables -D OUTPUT -p tcp --sport %s -j ACCEPT && " \
					  "iptables -D OUTPUT -p udp --sport %s -j ACCEPT" \
					  %(port, port, port, port)
			logging.info("删除防火墙端口，执行代码：\n %s" %(command,))
		  	# 检查是否成功
			if Linux.ckcomsuccess(os.popen(command).readlines(),command):
				logging.info("删除成功")
		# 保存新修改的规则
		return Linux.save_rules()

	# 更新端口
	@staticmethod
	def update_port(p1 ,p2):
		# 先看有没有p1这个端口有的话才进行下一步操作
		command = "iptables -L -nvx|grep %s" %(p1)
		if len(os.popen(command).readlines()) == 4 :
			# 先移除端口p1
			command = "iptables -D INPUT -p tcp --dport %s -j ACCEPT && " \
			 		  "iptables -D INPUT -p udp --dport %s -j ACCEPT && " \
				 	  "iptables -D OUTPUT -p tcp --sport %s -j ACCEPT && " \
					  "iptables -D OUTPUT -p udp --sport %s -j ACCEPT" \
					  %(p1, p1, p1, p1)
			logging.info("删除防火墙端口，执行代码：\n %s" %(command,))
			if Linux.ckcomsuccess(os.popen(command).readlines(),command):
				# 再添加端口p2
				command = "iptables -I INPUT -p tcp --dport %s -j ACCEPT && " \
				 		  "iptables -I INPUT -p udp --dport %s -j ACCEPT && " \
				 		  "iptables -I OUTPUT -p tcp --sport %s -j ACCEPT && " \
						  "iptables -I OUTPUT -p udp --sport %s -j ACCEPT" \
						  %(p2, p2, p2, p2)
				logging.info("添加防火墙端口，执行代码：\n %s" %(command,))
				if Linux.ckcomsuccess(os.popen(command).readlines(),command):
					return Linux.save_rules()
				else:
					return False
			else:
				return False
		return False
			
	# 统计指定端口流量
	@staticmethod
	def count_port(ports):
		port_dict = {}
		for port in ports:
			# 拼接统计指定端口流量 以M为单位
			command = "iptables -L -nvx|grep 'spt:%s'|awk '{print ($2/1024/1024)}'" %(port)
			flows = os.popen(command).readlines()
			flow_sum = 0
			# 将udp和tcp的统计起来
			for flow in flows:
				flow_sum += int(flow)
			# 添加到字典里去 端口做key流量做value
			port_dict[port] = flow_sum
		# 返回总流量字典
		logging.info("统计%s端口的流量数据：\n %s" %(port, port_dict))
		return port_dict

	# 统计允许出去的端口流量
	@staticmethod
	def count_all_port():
		port_dict = {}
		# 拼接统计指定端口流量 以M为单位
		command = "iptables -L -nvx|grep 'spt:'|awk '{print ($2,$11)}'|awk -F 'spt:' '$1!=0 {print($1,$2/1024/1024)}'" 
		flows = os.popen(command).readlines()
		flow_dic = {}
		count = 1
		# 将udp和tcp的统计起来
		for index,num in enumerate(flows):
			# 获取端口，判断是否为奇数，是的话就是端口号
			if index%2 is 0:
				# 从字典里拿出来，看有没有值，如果没有值就添加一个只进去，以便下次累加
				if flow_dic.get(num) is None:
					flow_dic[num] = 0
			else:
				# 获取上一个端口号
				pre_port = flows[index-1]
				# 累加起来
				flow_dic[pre_port] = int(flow_dic.get(pre_port)+int(num))
		logging.info("统计端口的流量数据：\n %s" %(port_dict))
		# 返回正在活跃总流量字典
		return port_dict

	# 清除所有的链表流量
	@staticmethod
	def clear_output_port_flow():
		# 清除所有的链表流量
		command = "iptables -Z"
		logging.info("清理所有OUTPUT端口的流量数据")
		return Linux.ckcomsuccess(os.popen(command).readlines(), command)

	# 检测指定端口是否存在于output表和input表
	def check_ports_open(ports):
		strs = ""
		# 组装需要查询的端口用|连接
		for port in ports:
			port += "|"
		command = "iptables -L -nvx|grep -E '%s'" % (strs[0:-1])
		logging.info("查看端口：%s是否已经开发" %(ports,))
		if len(os.popen(command).readlines()) != 0:
			return True
		else:
			return False

	# 限制流量
	@staticmethod
	def limit_flow():
		pass

	# 重启防火墙
	@staticmethod
	def save_rules():
		command = "iptables-save > /etc/iptables.up.rules && service iptables save"
		logging.info("保存防火墙信息，将它写入到/etc/iptables.up.rules文件中")
		return Linux.ckcomsuccess(os.popen(command).readlines(), command)

	# 检查命令是否执行成功（那种执行之后没有任何返回数据的命令）
	@staticmethod
	def ckcomsuccess(result,command):
		# 返回数据长度是否为0如果为0说明执行成功没有报任何错误
		if len(result) == 0:
			logging.info("命令：%s 执行完毕！" %(command))
			return True
		else:
			# 长度大于0
			reason = ""
			for res in result:
				reason += res
			# 打印错误信息和执行命令
			logging.info("命令执行出现错误：%s" %(reason,))
			return False

	# 重启锐速
	@staticmethod
	def start_serverSpeeder():
		command = "service serverSpeeder start"
		logging.info("开启锐速：%s" %(command))
		Linux.ckcomsuccess(os.popen(command).readlines(), command)

	# 查看锐速转态是否运行
	@staticmethod
	def serverSpeeder_is_run():
		command = "service serverSpeeder status|grep 'ServerSpeeder is NOT running'"
		logging.info("检查锐速是否启动：%s" %(command))
		return len(os.popen(command).readlines()) == 0

	# 重启ssr
	@staticmethod
	def restart_ssr():
		command = "service ssr restart"
		logging.info("重启锐速：%s" %(command))
		return len(os.popen(command).readlines()) == 0
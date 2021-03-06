#!/usr/bin/python
# coding: utf-8

import os


class Linux:

	# 给防火墙添加一个或多个放行端口
	@staticmethod
	def add_port(dic):
		port = dic.get("server_port")
		client = dic.get("client",1)
		if Linux.check_ports_open([port]) is not True:
			# 添加tcp
			command = "iptables -I INPUT -p tcp --dport %s -j ACCEPT && " \
			 		  "iptables -I INPUT -p udp --dport %s -j ACCEPT && " \
			 		  "iptables -I OUTPUT -p tcp --sport %s -j ACCEPT && " \
					  "iptables -I OUTPUT -p udp --sport %s -j ACCEPT" \
					  %(port, port, port, port)
			print("Insert the port to a firewall,excute command: %s" %(command,))
			# 检查是否成功
			if Linux.ckcomsuccess(os.popen(command).readlines(),command):
				print("Insert success")
		# 保存新修改的规则
		Linux.save_rules()
		Linux.restart_ssr()

	# 移除一个或多个端口
	@staticmethod
	def delete_port(ports):
		out_ = ""
		in_ = ""
		for port in ports:
			out_+='dpt:%s|'% (port)
			in_+='spt:%s|'% (port)

		# 获取output每一个要删除的序号
		command = "iptables -L -n --line|grep -E '%s'|awk '{print($1)}'"%(out_[0:-1])
		# 获取出删的序号
		out_num = os.popen(command).readlines()
		command = "iptables -L -n --line|grep -E '%s'|awk '{print($1)}'"%(in_[0:-1])
		in_num = os.popen(command).readlines()
		# 执行删除INPUT链命令
		for num in out_num:
			command = "iptables -D INPUT %s" %(num)
			if Linux.ckcomsuccess(os.popen(command).readlines(),command):
				print("remove success")
		# 执行删除OUTPUT链命令
		for num in in_num:
			command = "iptables -D OUTPUT %s" %(num)
			if Linux.ckcomsuccess(os.popen(command).readlines(),command):
				print("remove success")
		# 保存新修改的规则
		Linux.save_rules()
		Linux.restart_ssr()

	# 更新端口
	@staticmethod
	def update_port(p1 ,p2):
		# 先移除端口p1
		Linux.delete_port([p1,p2])
		# 添加端口p2
		Linux.add_port([p2])
			
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
		print("count the ports flows : %s" %(port_dict))
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
			# 获取端口,判断是否为奇数,是的话就是端口号
			if index%2 is 0:
				# 从字典里拿出来,看有没有值,如果没有值就添加一个只进去,以便下次累加
				if flow_dic.get(num) is None:
					flow_dic[num] = 0
			else:
				# 获取上一个端口号
				pre_port = flows[index-1]
				# 累加起来
				flow_dic[pre_port] = int(flow_dic.get(pre_port)+int(num))
		print("count the ports flows : %s" %(port_dict))
		# 返回正在活跃总流量字典
		return port_dict

	# 清除所有的链表流量
	@staticmethod
	def clear_output_port_flow():
		# 清除所有的链表流量
		command = "iptables -Z"
		print("clear the all of OUTPUT table flow data")
		return Linux.ckcomsuccess(os.popen(command).readlines(), command)

	# 检测指定端口是否存在于output表和input表
	@staticmethod
	def check_ports_open(ports,typ='INPUT'):
		strs = ""
		# 组装需要查询的端口用|连接
		for port in ports:
			strs += ":" + str(port) + "|"
		command = "iptables -L %s -nvx|grep -E '%s'" % (typ,strs[0:-1])
		print("check ports:%swhether or not open" %(ports,))
		print(command)
		if len(os.popen(command).readlines()) != 0:
			return True
		else:
			return False

	# 重启防火墙
	@staticmethod
	def save_rules():
		command = "service iptables save"
		print("save the firewall info to /etc/sysconfig/iptables that file")
		return Linux.ckcomsuccess(os.popen(command).readlines(), command)

	# 检查命令是否执行成功（那种执行之后没有任何返回数据的命令）
	@staticmethod
	def ckcomsuccess(result,command):
		# 返回数据长度是否为0如果为0说明执行成功没有报任何错误
		if len(result) == 0:
			print("command:%s excute done!" %(command))
			return True
		else:
			# 长度大于0
			reason = ""
			for res in result:
				reason += res
			# 打印错误信息和执行命令
			print("The command excute Erro:%s" %(reason,))
			return False
	# 重启锐速
	@staticmethod
	def start_serverSpeeder():
		command = "service serverSpeeder start"
		print("start the serverSpeeder:%s" %(command))
		Linux.ckcomsuccess(os.popen(command).readlines(), command)

	# 查看锐速转态是否运行
	@staticmethod
	def serverSpeeder_is_run():
		command = "service serverSpeeder status|grep 'ServerSpeeder is NOT running'"
		print("check the serverSpeeder whether or not runing:%s" %(command))
		return len(os.popen(command).readlines()) == 0

	# 重启ssr
	@staticmethod
	def restart_ssr():
		command = "service ssr restart"
		print("restart the ssr:%s" %(command))
		return len(os.popen(command).readlines()) == 0
if __name__ == '__main__':
	Linux.delete_port([1223,4444,9999])

from datetime import datetime
from com.free.ssr.action.linux_option import Linux
from datetime import datetime

from com.free.ssr.action.linux_option import Linux


class Test:
	@staticmethod
	def test(ports):
		for port in ports:
			print(port)



if __name__ == '__main__':
	form = {"aa":"11","bb":"bb","begin":"2018-02-28","endTm":'2018-01-28'}
	endTm = datetime.strptime(form.get("endTm"), "%Y-%m-%d")
	begin = datetime.strptime(form.get("begin"), "%Y-%m-%d")
	
	print(project)
	# port_data = {}
	# port = dic.get("port")
	# port_data = port
	
	# port_data["aaa"] = 'aaa1'
	# port_data["bbb"] = 'bbb1'
	# port_data["ccc"] = 'ccc1'
	arr = [1,2,3,4]
	print(Linux.delete_port(arr))
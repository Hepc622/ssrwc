from datetime import datetime
from com.free.ssr.action.linux_option import Linux
from datetime import datetime
import com.free.ssr.utils.json_file_utils as jfileutl

from com.free.ssr.action.linux_option import Linux


class Test:
	@staticmethod
	def test(ports):
		for port in ports:
			print(port)



if __name__ == '__main__':
	print(datetime.strftime(datetime.now(),"%Y-%m-%d"))
	if datetime.strptime("2018-05-03", "%Y-%m-%d") >= datetime.strptime(datetime.strftime(datetime.now(), "%Y-%m-%d"), "%Y-%m-%d"):
		print(111)
	
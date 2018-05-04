import com.free.ssr.action.port_service as port_service
import json
import os
if __name__ == '__main__':
    project = os.path.dirname(os.path.abspath(__file__))
    print(project)
    # 获取当前的工作目录
    config_path = os.path.join(project, 'shadowsocks', 'config.json')
    with open(file=config_path, mode='r', encoding='utf-8') as f:
	    # 将文件内容读成字典
        load_dict = json.load(f)

    if not load_dict.get('port_password'):
    	pass
    # False,0,'',[],{},()都可以视为假
    if not 0:
        print("0 is False")
    if not '':
    	print("'' is False")
    if not []:
    	print("[] is False")
    if not {}:
    	print("{} is False")
    if not ():
    	print("() is False")
#!/bin/bash
cd `dirname $0`
# 将防火墙加载进iptables
iptables-restore < /etc/sysconfig/iptables
eval $(ps -ef | grep "[0-9] python server\\.py a" | awk '{print "kill "$2}')
nohup python server.py a >> ../ssr_server.log 2>&1 &

eval $(ps -ef | grep "[0-9] python app.py" | awk '{print "kill "$2}')
cd ../
# 运行web
python app.py >> ssr_web.log 2>&1 &


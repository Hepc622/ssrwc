#!/bin/bash
cd `dirname $0`
# 将防火墙加载进iptables
iptables-restore < /etc/sysconfig/iptables
eval $(ps -ef | grep "[0-9] python server\\.py a" | awk '{print "kill "$2}')
nohup python server.py a >> ../ssr_server.log 2>&1 &

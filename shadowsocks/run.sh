#!/bin/bash
cd `dirname $0`
eval $(ps -ef | grep "[0-9] python server\\.py a" | awk '{print "kill "$2}')
nohup python server.py a >> ../ssr_server.log 2>&1 &
cd ../
# 运行web
python app\\.py >> ssr_web.log 2>&1 &


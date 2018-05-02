#!/bin/bash  

# description: SSR Start Stop Restart  

# processname: tomcat7  

# chkconfig: 234 20 80  

SSR_HOME=/usr/ssr/shadowsocks

export SSR_HOME  

PATH=$SSR_HOME/bin:$PATH  

export PATH  


case $1 in  

start)  

sh $SSR_HOME/run.sh  

;;   

stop)     

sh $SSR_HOME/stop.sh  

;;   

restart)  

sh $SSR_HOME/run.sh  

sh $SSR_HOME/stop.sh

;;   

esac      

exit 0
#!/bin/bash
# 下载ssrwc项目
wget https://github.com/Hepc622/ssrwc/archive/master.zip -O /opt/ssrwc.zip
# 切入到opt
cd /opt/
# 解压项目
unzip ssrwc.zip
# 添加权限
chmod -R 755 ./ssrwc-master/
# 切入ssrwc-master
cd ./ssrwc-master/
# 执行安装脚本
./install.sh
#!/bin/bash
export PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

#chmod
chmod -R 755 *
#Get Current Directory
workdir=$(pwd)

#Install SSR WC
# 创建一个ssr的目录
mkdir /usr/local/ssr
# 将当前的路劲下的所有文件复制过去
cp -r * /usr/local/ssr/
# 切换到local下
cd /usr/local
# 更改ssr的所有权限
chmod -R 755 /usr/local/ssr


#Install Libsodium
cd $workdir
export LIBSODIUM_VER=1.0.11
tar xvf libsodium-$LIBSODIUM_VER.tar.gz
pushd libsodium-$LIBSODIUM_VER
./configure --prefix=/usr && make
make install
popd
ldconfig
cd $workdir && rm -rf libsodium-$LIBSODIUM_VER.tar.gz libsodium-$LIBSODIUM_VER

#Start when boot
if [[ ${OS} == Ubuntu || ${OS} == Debian ]];then
#     cat >/etc/init.d/ssr <<EOF
# #!/bin/sh
# ### BEGIN INIT INFO
# # Provides:          ssr
# # Required-Start: $local_fs $remote_fs
# # Required-Stop: $local_fs $remote_fs
# # Should-Start: $network
# # Should-Stop: $network
# # Default-Start:        2 3 4 5
# # Default-Stop:         0 1 6
# # Short-Description: SSR-Bash-Python
# # Description: SSR-Bash-Python
# ### END INIT INFO
# iptables-restore < /etc/iptables.up.rules
# bash /usr/local/shadowsocksr/logrun.sh
# EOF
#     chmod 755 /etc/init.d/ssr
#     chmod +x /etc/init.d/ssr
#     cd /etc/init.d
    # `dirname $0` 得到当前目录的父级目录
    parent=`dirname $0`
    # 切换到目录
    cd $parent/shadowsocks/
    # 建立一个硬连接
    ln ./ssr /etc/init.d/
    # 修改权限
    chmod 755 ssr
    update-rc.d ssr defaults 95
fi

if [[ ${OS} == CentOS ]];then
   # `dirname $0` 得到当前目录的父级目录
   parent=`dirname $0`
   # 切换到目录
   cd $parent/shadowsocks/
   # 建立一个硬连接
   ln ./ssr /etc/init.d/
   # 修改权限
   chmod 755 ssr
   # 添加到开机自启
   chkconfig ssr on
   chkconfig --add ssr
fi


#Change CentOS7 Firewall
if [[ ${OS} == CentOS && $CentOS_RHEL_version == 7 ]];then
    systemctl stop firewalld.service
    systemctl disable firewalld.service
    yum install iptables-services -y
    cat << EOF > /etc/sysconfig/iptables
# sample configuration for iptables service
# you can edit this manually or use system-config-firewall
# please do not ask us to add additional ports/services to this default configuration
*filter
:INPUT ACCEPT [0:0]
:FORWARD ACCEPT [0:0]
:OUTPUT ACCEPT [0:0]
-A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
-A INPUT -p icmp -j ACCEPT
-A INPUT -i lo -j ACCEPT
-A INPUT -p tcp -m state --state NEW -m tcp --dport 22 -j ACCEPT
-A INPUT -m state --state NEW -m tcp -p tcp --dport 3306 -j ACCEPT
-A INPUT -m state --state NEW -m tcp -p tcp --dport 443 -j ACCEPT
-A INPUT -j REJECT --reject-with icmp-host-prohibited
-A FORWARD -j REJECT --reject-with icmp-host-prohibited
COMMIT
EOF
systemctl restart iptables.service
systemctl enable iptables.service
fi

#Install SSR
# 将config文件硬链接一个到ssr下
cd /usr/local/ssr/shadowsocks
# 创建硬链接,同步实时更新的
if [ -z $(find ../ -name config.json) ];then
    mv ../config.json ../config.json.bak
fi
ln ./config.json ../
# 安装依赖
# python开发环境依赖
yum install python-devel 
yum install openssl-devel

pip install flask
pip install pyjwt

#Install serverSpeeder
# 判断是否为3.10.0的内核
cd /root
if [ -z "$(uname -a|grep '3.10.0')" ];then
    # 不是3.10.0的内核，更换内核
    rpm -ivh http://soft.91yun.org/ISO/Linux/CentOS/kernel/kernel-3.10.0-229.1.2.el7.x86_64.rpm --force
fi
echo "将系统跟换至3.10.0-229，请在重启后运行serverspeeder-all.sh这个脚本,进行安装锐速加速"
# 安装锐速
wget -N --no-check-certificate https://raw.githubusercontent.com/91yun/serverspeeder/master/serverspeeder-all.sh && bash serverspeeder-all.sh
# 启动ssr
service ssr start
echo "可以使用service ssr (start|stop|restart) 来操作ssrwc"
echo "直接使用ip地址访问web控制"
echo "欢迎纠正错误，git地址：https://github.com/Hepc622/ssrwc.git"
echo "欢迎使用..."
echo "修改者：墨荷"

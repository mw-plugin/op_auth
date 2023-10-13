#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

# cd /www/server/mdserver-web/plugins/op_waf && bash install.sh install 0.3.0

curPath=`pwd`
rootPath=$(dirname "$curPath")
rootPath=$(dirname "$rootPath")
serverPath=$(dirname "$rootPath")

install_tmp=${rootPath}/tmp/mw_install.pl

action=$1
version=$2
sys_os=`uname`

if [ -f ${rootPath}/bin/activate ];then
	source ${rootPath}/bin/activate
fi

if [ "$sys_os" == "Darwin" ];then
	BAK='_bak'
else
	BAK=''
fi


Install_App(){
	
	echo '正在安装脚本文件...' > $install_tmp
	mkdir -p $serverPath/source/op_auth
	mkdir -p $serverPath/op_auth

	echo "${version}" > $serverPath/op_auth/version.pl
	echo 'install ok' > $install_tmp

	cd ${rootPath} && python3 ${rootPath}/plugins/op_auth/index.py start
	echo "cd ${rootPath} && python3 ${rootPath}/plugins/op_auth/index.py start"
	sleep 2
	cd ${rootPath} && python3 ${rootPath}/plugins/op_auth/index.py reload
}

Uninstall_App(){

	cd ${rootPath} && python3 ${rootPath}/plugins/op_auth/index.py stop
	if [ "$?" == "0" ];then
		rm -rf $serverPath/op_auth
	fi
}


action=$1
if [ "${1}" == 'install' ];then
	Install_App
else
	Uninstall_App
fi

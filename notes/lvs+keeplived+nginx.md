## keeplived+nginx


### 实验ip
| 作用 | IP | 端口 |
| --- | --- | --- |
| nginx+keepalived | 10.20.3.108 | 80 |
| nginx+keepalived | 10.20.3.109 | 80 |
| vip | 10.20.3.120 | |




### 关闭服务器防火墙


```plain
[root@lvs01 ~]# firewall-cmd --state
running
[root@lvs01 ~]# systemctl stop firewalld.service
[root@lvs01 ~]# firewall-cmd --state
not running
[root@lvs01 ~]# systemctl disable firewalld.service
```



### 关闭防selinux


```shell
查看selinux状态：

[root@lvs01 ~]# sed -i 's/^ *SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config #重启生效
[root@lvs01 ~]# sestatus -v
```



### 系统优化配置


```shell
#打开内核转发功能 /etc/sysctl.conf
net.ipv4.ip_forward = 1
sed -i '/net.ipv4.ip_forward/ s/\(.*= \).*/\11/' /etc/sysctl.conf
```



### 安装ipvs


```shell
yum -y install ipvsadm
```



> ipvsadm -Ln
>



<!-- 这是一张图片，ocr 内容为：[ROOT@EVERDC02 KEEPALIVED]# IPVSADM SERVER VERSION 1.2.1 (SIZE:4096) IP VIRTUAL LOCALADDRESS:PORT SCHEDULER ` FLAGS PROT REMOTEADDRESSPORT WEIGHT ACTIVECONN INACTCONN FORWARD [ROOT@EVERDCO2 KEEPALIVED]# IPVSADM -LN IP VIRTUAL SERVER VERSION 1.2.1 (SIZE-4096) PROT LOCALADDRESS:PORT SCHEDULER FLAGS FORWARD WEIGHT A REMOTEADDRESSPORT T ACTIVECONN INACTCONN LSMOD IP_VS [ROOT@EVERDC02 KEEPALIVED]# GREP 12600 O TP_VS_RR 12697 O IP_VS_WRR 145497 4 RR,IP_VS_WRR 1P-VS_ 1P_VS 133095 1 1P_VS NF_CONNTRACK 3 XFS,IP_VS,NF_CONNTRACK 12644 LIBCRC32C [ROOT@EVERDCO2 KEEPALIVED]# -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1676812784119-8c0882e9-d948-466f-94f7-cd0101d92690.png)



### nginx部署脚本


```shell
###Nginx升级包修改变量
pack_path=/home/nginx_install
Nginx_bao_1=openssl-1.1.1b.tar.gz
Nginx_bao_2=zlib-1.2.11.tar.gz
Nginx_bao_3=pcre-8.44.tar.gz
Nginx_bao_4=nginx-1.23.0.tar.gz

Nginx_bao_1_path=openssl-1.1.1b
Nginx_bao_2_path=zlib-1.2.11
Nginx_bao_3_path=pcre-8.44
Nginx_bao_4_path=nginx-1.23.0



####安装Nginx-6
Check_Nginx_install () {
		N=`ps -ef |grep nginx | grep -v "grep" | wc -l`
		if [ $N -ne 0 ]; then
		echo  --------当前存在Nginx进程，请检查，本次退出安装------- && exit 1 
		fi

}
Nginx_install () {
		gcc -v &> /dev/null
		if [ $? -eq 0 ];then
		cd $pack_path && tar -xf $Nginx_bao_1 -C /usr/local
		cd $pack_path && tar -xf $Nginx_bao_2 -C /usr/local/ 
		cd $pack_path && tar -xf $Nginx_bao_3 -C /usr/local/
		cd $pack_path && tar -xf $Nginx_bao_4 -C /usr/local/
		#cd /usr/local/$Nginx_bao_1_path/ && ./config shared zlib  && make && make install     2>/dev/null
		cd /usr/local/$Nginx_bao_2_path/  && ./configure && make && make install  2>/dev/null
		cd /usr/local/$Nginx_bao_3_path/ && ./configure && make && make install   2>/dev/null
                cd /usr/local/$Nginx_bao_1_path/ && ./config shared zlib  && make && make install     2>/dev/null
                ln -s /usr/local/lib64/libssl.so.1.1 /usr/lib64/libssl.so.1.1
                ln -s /usr/local/lib64/libcrypto.so.1.1 /usr/lib64/libcrypto.so.1.1
cd /usr/local/$Nginx_bao_4_path/  &&./configure --with-http_realip_module --with-http_addition_module --with-http_sub_module --with-http_dav_module --with-http_gunzip_module --with-http_gzip_static_module --with-http_random_index_module --with-http_secure_link_module --with-http_stub_status_module --with-http_auth_request_module --with-threads --with-stream_ssl_module --with-http_slice_module --with-file-aio --with-http_v2_module --with-http_ssl_module --with-http_flv_module --with-http_mp4_module --with-http_stub_status_module --with-http_gzip_static_module --with-stream --prefix=/usr/local/$Nginx_bao_4_path --with-pcre=/usr/local/$Nginx_bao_3_path/ --with-zlib=/usr/local/$Nginx_bao_2_path/ --with-openssl=/usr/local/$Nginx_bao_1_path/ 
				sleep 5
                cd /usr/local/$Nginx_bao_4_path/  &&  make && make install  2>/dev/null
	        mkdir -p -m 755 /usr/local/$Nginx_bao_4_path/logs/
               /usr/local/$Nginx_bao_4_path/sbin/nginx  -V

               /usr/local/$Nginx_bao_4_path/sbin/nginx
		echo "————————————————————————————————————————————————————————————————————————————————————————"
                sleep 5
		ps -ef | grep nginx  
		echo -e "\033[32m ---------Nginx以安装完成，如上方无nginx进程请检查配置文件------- \033[0m"
		else
		echo  --------请安装gcc、libgcc、gcc-c++环境在继续安装-------
		fi

}

echo -e "\033[32m 开始检查nginx进程...... \033[0m"
Check_Nginx_install
echo -e "开始安装"$Nginx_bao_4_path
Nginx_install
```



### 配置 nginx service 服务


> 新建一个脚本文件 /etc/init.d/nginx，内容如下
>



```shell
#! /bin/bash
# chkconfig: - 85 15
PATH=/usr/local/nginx-1.23.0
DESC="nginx daemon"
NAME=nginx
DAEMON=$PATH/sbin/$NAME
CONFIGFILE=$PATH/conf/$NAME.conf
PIDFILE=$PATH/logs/$NAME.pid
SCRIPTNAME=/etc/init.d/$NAME
set -e
[ -x "$DAEMON" ] || exit 0
do_start() {
$DAEMON -c $CONFIGFILE || echo -n "nginx already running"
}
do_stop() {
$DAEMON -s stop || echo -n "nginx not running"
}
do_reload() {
$DAEMON -s reload || echo -n "nginx can't reload"
}
case "$1" in
start)
echo -n "Starting $DESC: $NAME"
do_start
echo "."
;;
stop)
echo -n "Stopping $DESC: $NAME"
do_stop
echo "."
;;
reload|graceful)
echo -n "Reloading $DESC configuration..."
do_reload
echo "."
;;
restart)
echo -n "Restarting $DESC: $NAME"
do_stop
do_start
echo "."
;;
*)
echo "Usage: $SCRIPTNAME {start|stop|reload|restart}" >&2
exit 3
;;
esac
exit 0
```



> 添加执行权限
>



```plain
chmod a+x /etc/init.d/nginx
```



> 增加 nginx 服务
>



```plain
chkconfig --add nginx
```



> 如果要设置开机自启动，则执行以下命令
>



```plain
chkconfig nginx on
```



> 启动、停止、重启和重新加载 nginx服务和配置文件的命令
>



启动 nginx



```plain
systemctl start nginx.service
```



停止nginx服务



```plain
systemctl stop nginx.service
```



重启nginx服务



```plain
systemctl restart nginx.service
```



重新读取nginx配置(这个最常用, 不用停止nginx服务就能使修改的配置生效)



```plain
systemctl reload nginx.service
```



> 主节点nginx.conf
>



```plain
#pid /run/nginx.pid;
events {
  worker_connections 786;
}

http {
  server {
    listen 80;

    # 这里是直接返回200状态码和一段文本
    location / {
      default_type text/html;
      return 200 "Hello, Nginx! Server xxx@10.20.3.108\n";
    }
  }
}
```



> 备节点nginx.conf
>



```plain
#pid /run/nginx.pid;
events {
  worker_connections 786;
}

http {
  server {
    listen 80;

    # 这里是直接返回200状态码和一段文本
    location / {
      default_type text/html;
      return 200 "Hello, Nginx! Server xxx@10.20.3.109\n";
    }
  }
}
```



### 安装 keepalived 软件


> 下载keepalived
>



```shell
wget https://www.keepalived.org/software/keepalived-2.2.2.tar.gz
tar -zxvf keepalived-2.2.2.tar.gz
cd keepalived-2.2.2/
export LIBRARY_PATH=/usr/local/lib64
./configure
make -j 4 && make install
```



在编译 keepalived 时，如果没有正确配置 openssl 的so 动态库，可能会出现如下错误信息



```shell
keepalived-2.2.2/keepalived/check/check_ssl.c:81：对‘OPENSSL_init_ssl’未定义的引用
check/libcheck.a(check_ssl.o)：在函数‘init_ssl_ctx’中：
check_ssl.c:(.text+0x284)：对‘OPENSSL_init_ssl’未定义的引用
check_ssl.c:(.text+0x29a)：对‘TLS_method’未定义的引用
collect2: 错误：ld 返回 1
make[2]: *** [keepalived] 错误 1
make[2]: 离开目录“/home/keepalived-2.2.2/keepalived”
make[1]: *** [all-recursive] 错误 1
make[1]: 离开目录“/home/keepalived-2.2.2/keepalived”
make: *** [all-recursive] 错误 1
```



此时，只要找到 openssl 的so 安装目录，一般就是 /usr/local/lib64，然后执行以下命令，就可以解决



```shell
export LIBRARY_PATH=/usr/local/lib64
```



为系统增加 keepalived 服务



```shell
cd /home/keepalived-2.2.2 # 进入解压目录拷贝 
cp keepalived/etc/init.d/keepalived /etc/init.d/
chmod a+x /etc/init.d/keepalived
chkconfig --add keepalived
```



设置 keepalived 开启自启动



```shell
chkconfig keepalived on
```



设置 keepalived 的启动参数，打开 /usr/local/etc/sysconfig/keepalived 文件，修改里面的内容



```shell
KEEPALIVED_OPTIONS="-D -f /usr/local/etc/keepalived/keepalived.conf"
```



### nginx保活脚本


```shell
#!/bin/bash
set -x

A=`ps -C nginx --no-header |wc -l`
if [ $A -eq 0 ];then
   #nginx 启动命令
   systemctl start nginx.service
   sleep 3
fi

B=`ps -C nginx --no-header |wc -l`
if [ $B -eq 0 ];then
  echo `date`':  nginx is not healthy, try to killall keepalived' >> /usr/local/etc/keepalived/keepalived.log
  killall keepalived
fi
```



> 主节点10.20.3.108
>
>  
>
> vi /usr/local/etc/keepalived/keepalived.conf
>



```plain
! Configuration File for keepalived
 
global_defs {
   router_id lvs-01
}
 
vrrp_script chk_nginx { 
    script "/usr/local/etc/keepalived/nginx_check.sh" 
    interval 3 
    weight -20 
}
 
vrrp_instance VI_1 {
    state MASTER
    interface ens192
    virtual_router_id 51
    priority 100
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass 1111
    }
    ## 将 track_script 块加入 instance 配置块 
    track_script {
        chk_nginx  ## 执行 Nginx 监控的服务
    }
    virtual_ipaddress {
      10.20.3.120
    }
}
```



> 备节点：10.20.3.109
>
>  
>
> vi /usr/local/etc/keepalived/keepalived.conf
>



```plain
! Configuration File for keepalived
 
global_defs {
   router_id lvs-02
}
 
vrrp_script chk_nginx { 
    script "/usr/local/etc/keepalived/nginx_check.sh" 
    interval 3 
    weight -20 
}
 
vrrp_instance VI_1 {
    state MASTER
    interface ens192
    virtual_router_id 51
    priority 90
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass 1111
    }
    ## 将 track_script 块加入 instance 配置块 
    track_script {
        chk_nginx  ## 执行 Nginx 监控的服务
    }
    virtual_ipaddress {
      10.20.3.120
    }
}
```



主节点上的ip查看

<!-- 这是一张图片，ocr 内容为：[ROOT@EVERDC02 KEEPALIVED]# IP A LI: LO: <LOOPBACK,UP,LOWER`UP>'MTU 65536 QDISC NOQUEUEUE STATE UNKNOWN GROUP DEFAULT QLEN 1000 1INK/LOOPBACK 00:00:00:00:00:00 BRD 00:00:00:00:00:00 INET 127.0.1/8 '8 SCOPE HOST LO R PREFERRED_LFT FOREVER FOREVERPRE VALID_LFT F /128 SCOPE HOST INET6 :://12 VALID_1FT FOREVER PREFERRED_LFT FOREVER 12: ENS192: <BROADCAST,MULTICAST,UP;LOWERJUP> MTU 1500 QDISC MQ STATE UP GROUP DEFAULT QLEN 1000 LINK/ETHER 00:0C:29:13:09:19 BRD FF:FF:FF:FF:FF:FF:FF BRD 10.20.3.255 SCOPE QLOBAL NOPREFIXROUTE ENS192 INET 10.20.3.108/24 BR VALID_LFT FOREVER PREFERRED_LFT FOREVER .120/32 SCOPE GLOBAL ENS192 INET 10.20. LFT FOREVER PREFERRED_LFT FOREVER VALID_ 2F89:FD4C:EBO1:A35E/64 SCOPE LINK NOPREFIXROUTE INET6 FE80: VALID_LFT FOREVER PREFERRED_LFT FOREVER FROOT@EVERDC02 K # 2 KEEPALIVED -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1676812825911-63c6f6d3-5b36-457e-af2c-16d1cfa06740.png)



备节点上的ip查看

<!-- 这是一张图片，ocr 内容为：LAST LOGIN: TUE JUL 12 16:27:57 2022 [ROOT@EVERDC03~]# IP A 1: 10: <LOOPBACKIUP,LOWER UP> MTU 65536 ADISC NOQUEUEUEUE STATE UNKNOWN GROUP DEFAULT QLEN 1000 </10OPBACK 00:00:00:00:00:00 BRD 00:00:00:00:00:00:00 7INK/7 INET 127.0.0.1/8 SCOPE HOST LO VALID_LFT FOREVER PREFERRED_LFT FOREVER INET6 ::1/128 SCOPE HOST VALID_LFT FOREVER PREFERRED_LFT FOREVER 12: ENSI92: <EROADCAST,MULTICAST.UP;LOWERJUP> MTU 1SOO GDISC MQ STATE UP GROUP DEFAULT QLEN 1000 LINK/ETHER 00:0C:29:DE:6F:10 BRD FF:FF:FF:FF:FF:FF:FF INET 10.20.3.109/24 BRD 10.20.3.255 SCOPE GLOBAL NOPREFIXROUTE ENS192 VALID_LFT FOREVER PREFERRED LFT FOREVER INET6 FE80::7EF:321:7809:3579/64 SCOPE LINK NOPREFIXROUTE VALID_1FT FOREVER PREFERRED_LFT FOREVER [ROOT@EVERDC03 -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1676812834874-55ee8055-4b4a-4684-8551-6ec29a75eaf9.png)



模拟主节点挂了验证：

<!-- 这是一张图片，ocr 内容为：伦文办口 10.20.3.120 更新 不安全 GIT克隆别人代码提.... JAVAWEB款程目录... BUTTERFLY JCA中台账号权限 工具箱-程序员编程... LUCKY YE-自闭~ 公司 阿里云镜像下载 IOS手机缩网页测试 PYTHON教程-座雪峰 HELLO,NGINX! SERVER XXXX@10.20.3.108 -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1676812850849-7d6de702-3a31-4670-a66d-8e2c2c5c5716.png)

此时关掉10.20.3.108上面的keepalived验证

<!-- 这是一张图片，ocr 内容为：9安装NG C(23条消 C(23条消 (23条消 C(23条元 C(23条洋 X 登录`X (23条件 营 NGINX 营安装IP 10.20.1 不安全|10.20.3.120 C 更新 LUCKY YE-自闭~ JAVAWEB教程目录... 工具箱-程序员编程.... GIT 克隆别人代码提... IOS手机端网页测试 公司 阿里云镜像下载 FJCA中台账号权限 PYTHON数程-廖雪峰 BUTTERFLY HELLO,NGINX! SERVER XXXX@10.20.3.109 -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1676812882372-6300dae6-be6b-47aa-a7b9-b619d0259469.png)

### **nginx反向代理**


> nginx.conf
>



```plain
#user  root;
worker_processes  1;

error_log  /var/log/nginx/error.log warn;
pid        /var/run/nginx.pid;


events {
    worker_connections  1024;
}


http {
    include       mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    #tcp_nopush     on;

    keepalive_timeout  65;

    #gzip  on;

    include vhost/*.conf;
}

stream {


    log_format proxy '$remote_addr [$time_local] '
                 '$protocol $status $bytes_sent $bytes_received '
                 '$session_time "$upstream_addr" '
                 '"$upstream_bytes_sent" "$upstream_bytes_received" "$upstream_connect_time"';

    access_log /var/log/nginx/tcp-access.log proxy ;
    open_log_file_cache off;
    include vhost/*.*;
}
```



vhost目录文件



> everbi.stream
>



```plain
upstream FZX8229 {
        hash $remote_addr consistent;
        server 10.252.10.156:8090;
    }
        server {
        listen 8229;
        proxy_connect_timeout 5m;
        proxy_timeout 24h;
        proxy_pass FZX8229;
    }
```



> everdc-500.conf
>



```plain
upstream everdc.com {
 server 10.252.10.156:8001;
}

upstream everdc_bi.com {
 server 10.252.10.156:8090;
}

upstream api.com {
    server  10.252.10.156:31002;
}

server {
    listen       5000;
    server_name  localhost;
  
    
    location ~ .*\.(gif|jpg|jpeg|png|bmp|swf|css|js)$ {
        root /home/EverDC-2.3/DC3.12/everdc-front/;
        expires   7d;
    }

    location / {
        root /home/EverDC-2.3/DC3.12/everdc-front/;
        index index.html;
        add_header Cache-Control no-store;
        add_header X-Frame-Options http://everdc_bi.com;
    }

        location ^~ /service/ {
                proxy_pass  http://everdc.com/;
                proxy_redirect      default;
                #proxy_cookie_path   / /service/;
                proxy_set_header    X-Real-IP $remote_addr;
                proxy_set_header    X-Forwarded-Host $remote_addr;
                proxy_set_header    X-Forwarded-Server $remote_addr;
                proxy_set_header    X-Forwarded-For  $remote_addr;
                client_max_body_size 500m; 
                client_body_buffer_size 256k; 
                proxy_connect_timeout 60; 
                proxy_send_timeout 30; 
                proxy_read_timeout 300; 
                proxy_buffer_size 256k; 
                proxy_buffers 4 256k; 
                proxy_busy_buffers_size 256k; 
                proxy_temp_file_write_size 256k; 
                proxy_next_upstream error timeout invalid_header http_500 http_503 http_404; 
                proxy_max_temp_file_size 128m; 
        }

        location ^~ /apiseft {
                #add_header 'Access-Control-Allow-Origin' '*' always;
                add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
                proxy_pass  http://api.com/;
                proxy_redirect      default;
                proxy_set_header    X-Real-IP $remote_addr;
                proxy_set_header    X-Forwarded-Host $remote_addr;
                proxy_set_header    X-Forwarded-Server $remote_addr;
                proxy_set_header    X-Forwarded-For  $remote_addr;
                client_max_body_size 500m;
                client_body_buffer_size 256k;
                proxy_connect_timeout 60;
                proxy_send_timeout 30;
                proxy_read_timeout 300;
                proxy_buffer_size 256k;
                proxy_buffers 4 256k;
                proxy_busy_buffers_size 256k;
                proxy_temp_file_write_size 256k;
                proxy_next_upstream error timeout invalid_header http_500 http_503 http_404;
                proxy_max_temp_file_size 128m;
        }
}
```



### lvs实现负载均衡


> 两台RS上为lo:0绑定VIP地址、抑制ARP广播
>
>  
>
> ## 此脚本用于节点服务器绑定 VIP ，并抑制响应 VIP 的 ARP 请求。  
## 这样做的目的是为了不让关于 VIP 的 ARP 广播时，节点服务器应答（ 因为节点服务器都绑定了 VIP ，如果不做设置它们会应答，就会乱套 ，网上是这么说的）
>
>  
>
> 在两台RS上编写以下脚本文件realserver.sh
>
>  
>

```shell
chmod a+x /etc/init.d/realserver.sh
/etc/init.d/realserver.sh start
## 加入开机启动
echo "/etc/init.d/realserver.sh start" >> /etc/rc.local  ## 加入开机启动
```



```shell
#!/bin/bash
#description: Config realserver

VIP=10.20.3.120

. /etc/rc.d/init.d/functions

case "$1" in
start)
       /sbin/ifconfig lo:0 $VIP netmask 255.255.255.255 broadcast $VIP
       /sbin/route add -host $VIP dev lo:0
       echo "1" >/proc/sys/net/ipv4/conf/lo/arp_ignore
       echo "2" >/proc/sys/net/ipv4/conf/lo/arp_announce
       echo "1" >/proc/sys/net/ipv4/conf/all/arp_ignore
       echo "2" >/proc/sys/net/ipv4/conf/all/arp_announce
       sysctl -p >/dev/null 2>&1
       echo "RealServer Start OK"
       ;;
stop)
       /sbin/ifconfig lo:0 down
       /sbin/route del $VIP >/dev/null 2>&1
       echo "0" >/proc/sys/net/ipv4/conf/lo/arp_ignore
       echo "0" >/proc/sys/net/ipv4/conf/lo/arp_announce
       echo "0" >/proc/sys/net/ipv4/conf/all/arp_ignore
       echo "0" >/proc/sys/net/ipv4/conf/all/arp_announce
       echo "RealServer Stoped"
       ;;
*)
       echo "Usage: $0 {start|stop}"
       exit 1
esac

exit 0
```



ip a 查看结果

<!-- 这是一张图片，ocr 内容为：[ROOT@EVERDC02 KEEPALIVED]# IP A LI: LO: CLOOPBACK.UP,LOWER[UP> MTU 65536 QDISC NOQUEUEUE STATE UNKNOWN GROUP DEFAULT QLEN 1000 LINK/LOOPBACK 00:00:00:00:00:00 BRD 00:00:00:00:00:00:00  INET 127.0.0.1/8 SCOPE HOST LO ALID_LFT FOREVER PREFERRED_LFT FOROVER INET 10.20.3.120/32 BRD 10.20.3.120 SCOPE G LOBAL LO:0 VALID_LFT FOREVER PREFERRED LFT FOREVER INET6::1/128 SCOPE HOST VALID_LFT FOREVER PREFERRED LFT FOREVER 2: ENS19 ENSI9Z: <BROADCAST,MULTICAST,UP,LOWER-UP),MTU 1500 GDISC MA STATE UP GROUP DEFAULT QLEN 1000 1INK/ETHER 00:0C:29:13:09:19 BRD F午:F午:F午:FF:FF:FF INET 10.20.3.108/24 BRD 10.20.3.255 SCOPE GLOBAL NOPREFIXROUTE ENS192 VALID_LFT FOREVER PREFERRED_LFT FOREVER INET 10.20.3.120/32 SCOPE GLOBAL ENS192 VALID_LFT FOREVER PREFERRED LFT FOREVER INET6 FE80::2F89:FD4C:EB01:A35E/64 SCOPE LINK NOPREFIXROUTE VALID_LFT FOREVER PREFERRED_LFT FOREVER [ROOT@EVERDCO2 KEEPALIVED]# -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1676812915850-9d81ee10-86f8-4c72-8959-45f1511198cf.png)

10.20.3.108 主节点 /usr/local/etc/keepalived/keepalived.conf

```plain
! Configuration File for keepalived

global_defs {
    notification_email {
        acassen@firewall.loc     #设置报警邮件地址，可以设置多个，每行一个。
        failover@firewall.loc    #需开启本机的sendmail服务
        sysadmin@firewall.loc
    }
    notification_email_from Alexandre.Cassen@firewall.loc  #设置邮件的发送地址
    smtp_server 127.0.0.1      #设置smtp server地址
    smtp_connect_timeout 30    #设置连接smtp server的超时时间
    router_id LVS_01        #表示运行keepalived服务器的一个标识。发邮件时显示在邮件主题的信息
}

vrrp_instance VI_1 {
    state MASTER              #指定keepalived的角色，MASTER表示此主机是主服务器，BACKUP表示此主机是备用服务器
    interface ens192     #指定HA监测网络的接口
    virtual_router_id 51      #虚拟路由标识，这个标识是一个数字，同一个vrrp实例使用唯一的标识。即同一vrrp_instance下，MASTER和BACKUP必须是一致的
    priority 100              #定义优先级，数字越大，优先级越高，在同一个vrrp_instance下，MASTER的优先级必须大于BACKUP的优先级
    advert_int 1              #设定MASTER与BACKUP负载均衡器之间同步检查的时间间隔，单位是秒
    authentication {          #设置验证类型和密码
        auth_type PASS        #设置验证类型，主要有PASS和AH两种
        auth_pass 1111        #设置验证密码，在同一个vrrp_instance下，MASTER与BACKUP必须使用相同的密码才能正常通信
    }
    virtual_ipaddress {       #设置虚拟IP地址，可以设置多个虚拟IP地址，每行一个
        10.20.3.120 
    }
}

virtual_server 10.20.3.120 80 {  #设置虚拟服务器，需要指定虚拟IP地址和服务端口，IP与端口之间用空格隔开
    delay_loop 6              #设置运行情况检查时间，单位是秒
    lb_algo rr                #设置负载调度算法，这里设置为rr，即轮询算法
    lb_kind DR                #设置LVS实现负载均衡的机制，有NAT、TUN、DR三个模式可选
    #persistence_timeout 10    #会话保持时间，单位是秒。这个选项对动态网页是非常有用的，为集群系统中的session共享提供了一个很好的解决方案。
                              #有了这个会话保持功能，用户的请求会被一直分发到某个服务节点，直到超过这个会话的保持时间。
                              #需要注意的是，这个会话保持时间是最大无响应超时时间，也就是说，用户在操作动态页面时，如果50秒内没有执行任何操作
                              #那么接下来的操作会被分发到另外的节点，但是如果用户一直在操作动态页面，则不受50秒的时间限制
    protocol TCP              #指定转发协议类型，有TCP和UDP两种

    real_server 10.20.3.108 80 { #配置服务节点1，需要指定real server的真实IP地址和端口，IP与端口之间用空格隔开
        weight 1              #配置服务节点的权值，权值大小用数字表示，数字越大，权值越高，设置权值大小可以为不同性能的服务器
                              #分配不同的负载，可以为性能高的服务器设置较高的权值，而为性能较低的服务器设置相对较低的权值，这样才能合理地利用和分配系统资源
        TCP_CHECK {           #realserver的状态检测设置部分，单位是秒
            connect_timeout 5    #表示3秒无响应超时
            retry 5       #表示重试次数
            delay_before_retry 5 #表示重试间隔
            connect_port 80
        } 
    }
    real_server 10.20.3.109 80 {
        weight 1
        TCP_CHECK {
            connect_timeout 5
            retry 5
            delay_before_retry 5
            connect_port 80
        }
    }
}
```



10.20.3.109 备节点 /usr/local/etc/keepalived/keepalived.conf



```plain
! Configuration File for keepalived

global_defs {
    notification_email {
        acassen@firewall.loc     #设置报警邮件地址，可以设置多个，每行一个。
        failover@firewall.loc    #需开启本机的sendmail服务
        sysadmin@firewall.loc
    }
    notification_email_from Alexandre.Cassen@firewall.loc  #设置邮件的发送地址
    smtp_server 127.0.0.1      #设置smtp server地址
    smtp_connect_timeout 30    #设置连接smtp server的超时时间
    router_id LVS_02       #表示运行keepalived服务器的一个标识。发邮件时显示在邮件主题的信息
}

vrrp_instance VI_1 {
    state BACKUP              #指定keepalived的角色，MASTER表示此主机是主服务器，BACKUP表示此主机是备用服务器
    interface ens192     #指定HA监测网络的接口
    virtual_router_id 51      #虚拟路由标识，这个标识是一个数字，同一个vrrp实例使用唯一的标识。即同一vrrp_instance下，MASTER和BACKUP必须是一致的
    priority 90              #定义优先级，数字越大，优先级越高，在同一个vrrp_instance下，MASTER的优先级必须大于BACKUP的优先级
    advert_int 1              #设定MASTER与BACKUP负载均衡器之间同步检查的时间间隔，单位是秒
    authentication {          #设置验证类型和密码
        auth_type PASS        #设置验证类型，主要有PASS和AH两种
        auth_pass 1111        #设置验证密码，在同一个vrrp_instance下，MASTER与BACKUP必须使用相同的密码才能正常通信
    }
    virtual_ipaddress {       #设置虚拟IP地址，可以设置多个虚拟IP地址，每行一个
        10.20.3.120 
    }
}

virtual_server 10.20.3.120 80 {  #设置虚拟服务器，需要指定虚拟IP地址和服务端口，IP与端口之间用空格隔开
    delay_loop 6              #设置运行情况检查时间，单位是秒
    lb_algo rr                #设置负载调度算法，这里设置为rr，即轮询算法
    lb_kind DR                #设置LVS实现负载均衡的机制，有NAT、TUN、DR三个模式可选
    #persistence_timeout 120    #会话保持时间，单位是秒。这个选项对动态网页是非常有用的，为集群系统中的session共享提供了一个很好的解决方案。
                              #有了这个会话保持功能，用户的请求会被一直分发到某个服务节点，直到超过这个会话的保持时间。
                              #需要注意的是，这个会话保持时间是最大无响应超时时间，也就是说，用户在操作动态页面时，如果50秒内没有执行任何操作
                              #那么接下来的操作会被分发到另外的节点，但是如果用户一直在操作动态页面，则不受50秒的时间限制
    protocol TCP              #指定转发协议类型，有TCP和UDP两种

    real_server 10.20.3.108 80 { #配置服务节点1，需要指定real server的真实IP地址和端口，IP与端口之间用空格隔开
        weight 1              #配置服务节点的权值，权值大小用数字表示，数字越大，权值越高，设置权值大小可以为不同性能的服务器
                              #分配不同的负载，可以为性能高的服务器设置较高的权值，而为性能较低的服务器设置相对较低的权值，这样才能合理地利用和分配系统资源
        TCP_CHECK {           #realserver的状态检测设置部分，单位是秒
            connect_timeout 5    #表示3秒无响应超时
            retry 5       #表示重试次数
            delay_before_retry 5 #表示重试间隔
            connect_port 80
        } 
    }
    real_server 10.20.3.109 80 {
        weight 1
        TCP_CHECK {
            connect_timeout 5
            retry 5
            delay_before_retry 5
            connect_port 80
        }
    }
}
```



使用 ip add 查看是否绑定 VIP ，tail /var/log/messages 查看服务器状态是不是 MASTER ，检测节点服务器有没有连接成功信息：

<!-- 这是一张图片，ocr 内容为：15 12:05:41 EVERDCO2 KEEPALIVED[17192]: STARTUP COMPLETE 15 12:05:41 EVERDCO2 KEEPALIVEDJHEALTHCHECKERS[17293]: GAINED QUORUM 14031 <- 2 FOR VS VS [10.20:3,130]:TCP:80 15 32:0S:41 EVERDCO3 KEEPALIVED JTHEALTHECKERSF27393]: ACTIVATING HEAL THCHECKER FOR SERVICE [333333 3.108]:TCP:80 FOR VS [10.20.3.120]:TCP:80 AP:80 FOR VS [10.20.3.120]:TCP:80 S 12:05:42 EVERDCO2 KEEPALIVED_VRRP(17194]: (VI_1) RECE M 10.20.3.109 - DISCARDING I_1) RECEIVED LOWER PRIORITY (90) 0) ADVERT  FROM 10 -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1676812938628-d351fc4a-ef46-4886-8b2a-a5afad585b3c.png)



```shell
ipvsadm -Ln
```



<!-- 这是一张图片，ocr 内容为：[ROOT@EVERDCO2 KEEPALIVED]# IPVSADM -LN LIP VIRTUAL SERVER VERSION 1.2.1 (SIZE-4096) PROT T LOCALADDRESS:PORT SCHEDULER FLAGS FORWARD WEIGHT ACTIVECONN INACTCONN REMOTEADDRESS:PORT 10.20.3.120:80 RR TCP ROUTE 10.20.3.108:80 5 10.20.3.109:80 ROUTE [ROOT@EVERDCO2 KEEPALIVED]# -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1676812951617-e08379d2-d66e-4777-8ca2-ffb2b2b37ab6.png)



是因为设置了 persistence_timeout 120 这个参数吗？  
## 正因为设置了 session 保持时间，所以持续的访问被分配到了某一台节点服务器。  
## 现在把此参数注释掉，测试一次（ 记得重启 keepalived ）。



ipvsadm -Ln

<!-- 这是一张图片，ocr 内容为：[ROOTQEVERDCO2 KEEPALIVED]# IPVSADM -LN R VERSION 1.2.1 (SIZE-4096) IP VIRTUAL SERVER PROT LOCALADDRESS:PORT SCHEDULER FLAGS FORWARD WEIGHT ACTIVECONN INACTCONN REMOTEADDRESS:PORT TCP 10.20.3.120:80 RR 12 11 10.20.3.108:80 ROUTE 21 AI  -> 10.20.3.109:80 ROUTE [ROOT@EVERDCO2 KEEPALIVED]# -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1676812985565-f0497568-a20c-43fc-b8c0-560cdd654e48.png)

curl测试结果

<!-- 这是一张图片，ocr 内容为：~]# CURL -S HTTP://10.20.3.120/ [ROOT@EVERDCO1 HELLO, NGINX! SERVER XXX@10.20.3.108 ~]# CURL -S  HTTP://10.3.120/ [ROOT@EVERDCO1 HELLO, NGINX! SERVER XXX@10.20.3.109 CURL -S HTTP://10.20.3.120/ [ROOT@EVERDC01 #[` HELLO, NGINX! XXX@10.20.3.108 SERVER ~]# CURL HTTP://10.20.3.120/ [ROOT@EVERDC01 -S -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1676812993914-744e2b7d-848c-4774-b406-f84edeeda307.png)


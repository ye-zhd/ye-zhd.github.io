# frp内网穿透搭建


## 1、前提条件


1.有公网IP的服务器一台（阿里云，这里用的宽带公网ip）



2.访问目标设备，即你需要外网访问到的设备（比如我的笔记本，我需要外网访问到我的localhost运行的项目）



## 2、软件下载


更具内核版本下载对应的软件包：[https://github.com/fatedier/frp/releases/](https://github.com/fatedier/frp/releases/)



## 3、软件安装


### 1、服务端安装


> 解压包tar -zxvf frp_0.46.1_linux_amd64.tar.gz
>



```shell
####frps开头的是值服务端需要的，frpc开头的是指客户端需要的
[root@fjbsc-01 frp_0.46.1_linux_amd64]# ls -lrt
总用量 27856
-rwxr-xr-x 1 1001 123 12660736 1月  10 10:34 frpc 
-rwxr-xr-x 1 1001 123 15822848 1月  10 10:34 frps
-rw-r--r-- 1 1001 123    11358 1月  10 10:39 LICENSE
-rw-r--r-- 1 1001 123       26 1月  10 10:39 frps.ini
-rw-r--r-- 1 1001 123     5907 1月  10 10:39 frps_full.ini
-rw-r--r-- 1 1001 123      126 1月  10 10:39 frpc.ini
-rw-r--r-- 1 1001 123    11238 1月  10 10:39 frpc_full.ini
```



> 配置frps.ini
>



```shell
[root@fjbsc-01 frp_0.46.1_linux_amd64]# cat frps.ini   
[common]
#bind_port客户端和服务端连接的端口，这个端口号我们之后在配置客户端的时候要用到
bind_port = 7000
#dashboard_port 服务端仪表板的端口，若使用7500端口，在配置完成服务启动后可以通过浏览器访问 x.x.x.x:7500
dashboard_port = 7500
#token 用于客户端和服务端连接的口令
token = 12345678
#dashboard_user与dashboard_pwd表示打开仪表板页面登录的用户名和密码
dashboard_user = admin
dashboard_pwd = admin
#vhost_http_port和vhost_https_port用于反向代理HTTP主机时使用,不涉及
vhost_http_port = 10080
vhost_https_port = 10443
```



> 启动
>



```shell
nohup ./frps -c frps.ini &
```



### 2、客户端安装


> 我是在windows环境下配置，修改frpc.ini如下
>



```properties
[common]
server_addr = 112.51.25.139
authentication_method = token
token=12345678
server_port = 7000

[tcp]
type = tcp
# 本地web应用的ip和端口
local_ip = 10.252.10.175
local_port = 443
# 公网服务器提供给外网访问的端口
remote_port = 53818
privilege_mode = true 
authentication_timeout = 0 
use_encryption = true 
use_gzip = true

[tcp2]
type = tcp
# 本地web应用的ip和端口
local_ip = 10.252.10.175
local_port = 63389
# 公网服务器提供给外网访问的端口
remote_port = 63389

[tcp3]
type = tcp
# 本地web应用的ip和端口
local_ip = 10.252.10.175
local_port = 60022
# 公网服务器提供给外网访问的端口
remote_port = 60022
```



> 启动命令 cmd窗口 ：frpc.exe -c frpc.ini
>



会遇到的问题：



问题一：



```plain
客户端的时钟不能和服务器端时钟相差太大！否则会出现认证超时的错误:authorization timeout

这个超时时间可以在配置文件中通过 authentication_timeout 这个参数来修改，单位为秒，默认值为 900，即 15 分钟。如果修改为 0，则 frps 将不对身份验证报文的时间戳进行超时校验
```



问题二：



由于是宽带的公网ip映射的内网地址，防火墙nat策略需要开放端口:

<!-- 这是一张图片，ocr 内容为：回 H3C SECPATH F100-S- 网络 对象 策略 系统 监控 G3 概宽 导航 NAT内部服务器 请输入内部服务器名称 E新达 湾空统计数据 启用 取尚统计 X 册 禁用 金复制 安全策略 统计 安全策略 外网VRF 内邮服务量地址 ACL 内邮用 反向地 内邮酸 协议类型/外网络口 映射盛注 外网地址 名称 接口 接口接述 1/2.10.10.10 710711 2U101 GCI/4 公阿 浙止 公网 策略冗余分析 172.16.16.16 公网 TCP (6) /20189 20189 112512 公网 移动专线 GE1/0/2 禁止 信用 策略命中分析 公网 172.16.16.16 20190 TCP (6)/20190 26 112.512 移助专线.. GE1/0/2 禁止 公网 安全防护 112.51.2 22 319232 公网 开 TCP (6) /22022 172.16.16.1 公网 GE1/0/2 移动专线... 启用否 禁止 22 公网 172.16.7 GE1/0/2 92586 移动专战,. 112.512 开... TCP (6) /22023 启用否 公网 禁止 .NAT快速配置 22 78312 开... 公网 172.16.16.8 112.51.2 GE1/0/2 移动专线... 公网 启用  否 TCP (6) /22024 禁止 NAT策略 22 开... 公网 21 172.16.16 GE1/0/2 112.51.2 移动专线 百 TCP (6)/22025 公阿 启用 禁止 NAT动态转换 开. 60 22040 112.51.2 公网 172.16.16.8 GE1/0/2 TCP (6)/22040 移动专线... 公网 西 启用 禁止 NAT内部服务器 30 112.51.2.. 公网 3389 GE1/0/2 10.20.3.200 否 TCP (6)/22200 移动专线... 公网 禁止 启用 策略配置 386 22 11251.2 否 TCP (6) /22201 公网 公网 GE1/0/2 10.20.3.201 移动专线... 禁止 启用 服务器组 公网 3389 10.20.3.202 GE1/0/2 否 112.512 移动专线 启用 禁止 TCP (6) / 22202 公网 NAT静态转换 公网 香 10.20.3.203 112.51.2 3389 GE1/0/2 公网 启用 移动专业... TCP (6) /22203 禁止 NAT44动态转换 公网 63 GE1/0/2 172.16.16.16 30040 112.51.2 移动专线 TCP(6)/30040 启用否 公网 禁止 NAT444静态转换 18 公网 GE1/0/2 移动专线... 30099 112.51.2 TCP (6)/30099 172.16.16.16 禁止 公网 NAT高级设置 290 10.20.3.201 公网 TCP (6) /53818 FRP 53818 移动专线... GE1/0/2 53818 房用 112.51.2 公网 禁止 ?应用审计 3 公网 TCP (6)/60022 60022 10.20.3.201 GE1/0/2 公网 112.512 FRP 60022 否 移动专线... 禁止 启用 @吊带宽管理 1 FRP 63389 63389 GE1/0/2 公网 公网 TCP (6)/63389 10.20.3.201 否 112.51.2 移动专线... 禁止 启用 @负载均衡 -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1675216703631-b8bd56cd-f785-49cb-bfbc-466ac84f2f94.png)





### 3、连接与带宽查看


> sever端的页面查看带宽占用：
>

<!-- 这是一张图片，ocr 内容为：使用FRP搭建内网穿透 YHJ的博客 登录-华为统一运维审计 FRPS DASHBOARD 图文 不安全 10.20.3.201:7500/STATIC/#/PROXIES/TCP 更新 工具箱-程序员编程... IOS手机端网页测试 系统镜像下载 公司 LUCKY YE-自闭~ BUTTERFLY PYTHON教程-廖雪峰 PROMETHEUS JAVAWEB教程目录... GIT 克隆别人代码提... FRP OVERVIEW TRAFFIC OUT TRAFFIC IN PORT STATUS CONNECTIONS NAME PROXIES 4 53818 4.15MB 214KB ONLINE TCP TCP O 0 BYTES 63389 0 BYTES TCP2 ONLINE UDP 5KB 5KB 60022 TCP3 ONLINE HTTP HTTPS -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1675216721652-35f4204b-9a8e-4c9a-ab11-2324d3550a32.png)




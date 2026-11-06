---

# <font style="color:rgba(0, 0, 0, 0.9);">背景</font>
<font style="color:rgba(0, 0, 0, 0.9);">这边要两台服务器开放公网给总部研发访问，由于全开放，决定使用开源入侵防御工具 </font>**<font style="color:rgba(0, 0, 0, 0.9);">Fail2Ban</font>**<font style="color:rgba(0, 0, 0, 0.9);"> 来防护。</font>

<font style="color:rgba(0, 0, 0, 0.9);">Fail2Ban 可以实时监控日志文件，一旦检测到暴力破解行为（如多次登录失败），就会自动使用防火墙（如 firewalld）将攻击者 IP 临时或永久封禁。</font>

# <font style="color:rgba(0, 0, 0, 0.9);">1.项目地址</font>
[<font style="color:rgb(78, 161, 219);">https://github.com/fail2ban/fail2ban</font>](https://github.com/fail2ban/fail2ban)<font style="color:rgba(0, 0, 0, 0.9);">  
</font><font style="color:rgb(77, 77, 77);">因为在OpenEuler2203系统上面用yum找不到fail2ban，只能使用编译的方法进行安装</font><font style="color:rgba(0, 0, 0, 0.9);">  
</font><font style="color:rgb(77, 77, 77);">参考博客文章 </font>[<font style="color:rgb(78, 161, 219);">Linux 命令工具 fail2ban 使用指南</font>](https://blog.csdn.net/cui_win/article/details/148340923)

# <font style="color:rgba(0, 0, 0, 0.9);">2.安装步骤</font>
# <font style="color:rgba(0, 0, 0, 0.9);">1. 安装依赖</font>
```bash
dnf install python3-systemd -y
dnf install python3-devel gcc -y
```

## <font style="color:rgba(0, 0, 0, 0.9);">2. 编译安装 Fail2Ban</font>
也可以手动git下载源码包再编译安装

```bash
git clone https://github.com/fail2ban/fail2ban.git
cd fail2ban
python3 setup.py install

```

<font style="color:rgba(0, 0, 0, 0.9);">若看到类似“Installation successful”输出，说明编译安装成功。</font>

<!-- 这是一张图片，ocr 内容为：ADDING LICENSE FILE 'COPYING' WRITING MANIFEST FILE,"FAIL2BAN.EGG-INFO/SOURCES.TXT' LCOPYING FAILZBAN-E99-INFO TO /USR/LOCAL/L1B/PYTHON3.9/SITE-PACKA9ES/FARLFARLZBAN-1,1BO-PY3.9-E99-INF RUNNING INSTALL_SCRIPTS COPYING BUILD/SCRIPTS-3.9/FAIL2BAN-SERVER -> /USR/LOCAL/BIN COPYING BUILD/SCRIPTS-3.9/FAIL2BAN-REGEX -> /USR/LOCAL/BIN BUILD/SCRIPTS-3.9/FAIL2BAN-TESTCASES -> /USR/LOCAL/BIN COPYING NG BUILD/SCRIPTS-3.9/FAIL2BAN-CLIENT -> /USR/LOCAL/BIN COPYING B IPTS IN "FAIL2BAN.SERVICE" AND "FAIL2BAN-OPENRC.INIT". IMARNING: CANNOT FIND ROOT-BASE OPTION, CHECK THE BIN-PATH TO FAIL2BAN-SCRIPTS IN (CREATING BUILD/FAIL2BAN.SERVICE (FROM FAIL2BAN.SERVICE.IN): QBINDIR@ - -> /USR/LOCAL/BIN CREATING BUILD/FAIL2BAN-OPENRC.INIT (FR DIR@ - /USR/LOCAL/BIN INIT (FROM FAIL2BAN-OPENRC.INIT.IN):@BINDIR@ CREATING FAIL2BAN-PYTHON BINDING - /USR/LOCAL/BIN CHANGING MODE OF /USR/LOCAL/BIN/FAIL2BAN-SERVER TO 755 CHANGING MODE OF /USR/LOCAL/BIN/FAIL2BAN-REGEX TO 755 CHANGING MODE OF /USR/T OCAL/BIN/FAIL2BAN-TESTCASES TO 755 CHANGING MODE OF /USR/LOCAL/BIN/FAIL2BAN-CLIENT TO 755  CONFIGURATION FILES. PLEASE DO NOT FORGET TO UPDATE YOUR THEY ARE IN "/ETC/FAIL2BAN/". YOU CAN ALSO INSTALL SYSTEMD S ID SERVICE-UNIT FILE FROM "BUILD/FAIL2BAN.SERVICE" NG INIT SCRIPT FROM "FILES/*-INITD". RESP. CORRESPONDING [ROOT@LOCALHOST FAIL2BAN-1.1.1.BETAO]# -->
![](https://cdn.nlark.com/yuque/0/2025/png/34997268/1758871905902-d977d4a9-6bd8-4318-82fa-85dce9413b18.png)

## <font style="color:rgba(0, 0, 0, 0.9);">3.配置 Fail2Ban 防护 SSH</font>
### <font style="color:rgba(0, 0, 0, 0.9);">3.1 编辑配置文件</font>
```bash
vim /etc/fail2ban/jail.conf
```

### <font style="color:rgba(0, 0, 0, 0.9);">3.2 推荐配置（SSH 防护）</font>
<font style="color:rgb(77, 77, 77);">[DEFAULT] 是全局默认值，其他 jail 继承或覆盖</font><font style="color:rgba(0, 0, 0, 0.6);">  
</font><font style="color:rgb(77, 77, 77);">找到[DEFAULT] 开头的块去编辑</font>

```plain
[DEFAULT]
ignoreip = 127.0.0.1/8 ::1
bantime = 24h
findtime = 60m
maxretry = 5
backend = systemd
banaction = firewallcmd-ipset

[sshd]
enabled = true
mode = aggressive
port = 16822
logpath = %(sshd_log)s
filter = sshd
```

我这边使用配置sshd文件好区分

```bash
在 /etc/fail2ban/jail.d 新建文件sshd.local

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/secure
maxretry = 3
bantime = 300
findtime = 600
ignoreip = 127.0.0.1 10.20.3.0/24 112.51.25.139 

```

### <font style="color:rgba(0, 0, 0, 0.9);">配置说明</font>
| **<font style="color:rgba(0, 0, 0, 0.9);">参数</font>** | **<font style="color:rgba(0, 0, 0, 0.9);">说明</font>** |
| :--- | :--- |
| `<font style="color:rgba(0, 0, 0, 0.9);background-color:rgba(0, 0, 0, 0.03);">ignoreip</font>` | <font style="color:rgba(0, 0, 0, 0.9);">白名单 IP，支持多个，空格分隔</font> |
| `<font style="color:rgba(0, 0, 0, 0.9);background-color:rgba(0, 0, 0, 0.03);">bantime</font>` | <font style="color:rgba(0, 0, 0, 0.9);">封禁时长，</font>`<font style="color:rgba(0, 0, 0, 0.9);background-color:rgba(0, 0, 0, 0.03);">-1</font>`<br/><font style="color:rgba(0, 0, 0, 0.9);"> </font><font style="color:rgba(0, 0, 0, 0.9);">为永久封禁</font> |
| `<font style="color:rgba(0, 0, 0, 0.9);background-color:rgba(0, 0, 0, 0.03);">findtime</font>` | <font style="color:rgba(0, 0, 0, 0.9);">检测时间窗口</font> |
| `<font style="color:rgba(0, 0, 0, 0.9);background-color:rgba(0, 0, 0, 0.03);">maxretry</font>` | <font style="color:rgba(0, 0, 0, 0.9);">最大失败次数，超过即封禁</font> |
| `<font style="color:rgba(0, 0, 0, 0.9);background-color:rgba(0, 0, 0, 0.03);">banaction</font>` | <font style="color:rgba(0, 0, 0, 0.9);">使用 firewalld 封禁 IP</font> |
| `<font style="color:rgba(0, 0, 0, 0.9);background-color:rgba(0, 0, 0, 0.03);">backend</font>` | <font style="color:rgba(0, 0, 0, 0.9);">使用 systemd 读取日志，稳定性更好</font> |
| `<font style="color:rgba(0, 0, 0, 0.9);background-color:rgba(0, 0, 0, 0.03);">mode</font>` | `<font style="color:rgba(0, 0, 0, 0.9);background-color:rgba(0, 0, 0, 0.03);">aggressive</font>`<br/><font style="color:rgba(0, 0, 0, 0.9);"> </font><font style="color:rgba(0, 0, 0, 0.9);">模式匹配更多错误类型</font> |




## <font style="color:rgb(79, 79, 79);">4. 启动Fail2Ban服务</font>
### <font style="color:rgba(0, 0, 0, 0.9);">复制 systemd 服务文件</font>
```bash
cp build/fail2ban.service /etc/systemd/system/
```

### <font style="color:rgba(0, 0, 0, 0.9);">修改服务文件（解决启动失败问题）</font>
```bash
vim /etc/systemd/system/fail2ban.service
```

<font style="color:rgba(0, 0, 0, 0.9);">添加环境变量（根据实际 Python 路径调整）：</font>

```plain
Environment="PYTHONPATH=/usr/local/lib/python3.9/site-packages/"
```

<font style="color:rgba(0, 0, 0, 0.9);">建议注释掉 </font>`<font style="color:rgba(0, 0, 0, 0.9);background-color:rgba(0, 0, 0, 0.03);">PartOf</font>`<font style="color:rgba(0, 0, 0, 0.9);"> 行，避免不必要的重启依赖。</font>

<!-- 这是一张图片，ocr 内容为：JAIL.D]# ROOT@LOCALHOST CAC /ETC/SYSTEMD/SYSTEM/FAIL2BAN.SERVICE #[P [ROOT@LOCALHOST JA] JAI7 CAT CUNIT] DESCRIPTIONFFAIL2BAN SERVICE DOCUMENTATIONMAN:FAIL2BAN(1) ID.SERVICE INGTABLES. SERVICE INSET.SERVICE NFTABLES.SERVICE AFTER-NETWORK.TARGET INTABLES.SERVICE FIREWALLD.SERVICE #PARTOF-IPTABLES.SERVICE FIREWALLD.SERVICE IP6TABLES.SERVICE IPSET.SERVICE NFTABLES.SERVICE [SERVICE] #ENVIRONMENT"PYTHONNOUSERSITE-1" "PYTHONPATH-/USR/LOCAL/LIB/PYTHON3.9/SITE-PACKAGES/" ENVIRONMENT HIN/MKDIR -N /RUN/FAIL2HAN EXECSTARTPRES/ EXECSTART三/USR/LOCAL/BIN/FAIL2BAN-SERVER -XF START [IN IF SHOULD BE LOGGED IN SYSTEMD JOURNAL. USE FOIIOWING LINE OR SET LOGTARGET TO SYSOUT IN FAILZAL --LOGTARGET-SYSOUT START # EXECSTART-/USR/LOCAL/BIN/FAIL2BAN-SERVER -XF EXECSTOP-/USR/LOCAL/BIN/FAIL2BAN-CLIENT STOP EXECRELOAD-/USR/LOCAL/BIN/FAIL2BAN-CLIENT RELOAD PIDFILE/RUN/FAIL2BAN/FAIL2BAN.PID RESTARTON-FAILURE RESTARTPREVENTEXITSTATUS-0 255 [INSTAL1] LWANTEDRVEMULTI-USER TARAET -->
![](https://cdn.nlark.com/yuque/0/2025/png/34997268/1758869855226-dafb69ee-13d6-4665-a89c-292014abf4cb.png)

```bash
systemctl daemon-reload
systemctl restart fail2ban.service
systemctl status fail2ban.service
```

### <font style="color:rgba(0, 0, 0, 0.9);">启动并检查服务状态</font>
## <font style="color:rgba(0, 0, 0, 0.9);">5.常用 Fail2Ban 命令</font>
| **<font style="color:rgba(0, 0, 0, 0.9);">操作</font>** | **<font style="color:rgba(0, 0, 0, 0.9);">命令</font>** |
| :--- | :--- |
| <font style="color:rgba(0, 0, 0, 0.9);">查看服务状态</font> | `<font style="color:rgba(0, 0, 0, 0.9);background-color:rgba(0, 0, 0, 0.03);">fail2ban-client status</font>` |
| <font style="color:rgba(0, 0, 0, 0.9);">查看 sshd 防护详情</font> | `<font style="color:rgba(0, 0, 0, 0.9);background-color:rgba(0, 0, 0, 0.03);">fail2ban-client status sshd</font>` |
| <font style="color:rgba(0, 0, 0, 0.9);">手动封禁 IP</font> | `<font style="color:rgba(0, 0, 0, 0.9);background-color:rgba(0, 0, 0, 0.03);">fail2ban-client set sshd banip 10.0.0.111</font>` |
| <font style="color:rgba(0, 0, 0, 0.9);">手动解封 IP</font> | `<font style="color:rgba(0, 0, 0, 0.9);background-color:rgba(0, 0, 0, 0.03);">fail2ban-client set sshd unbanip 10.0.0.111</font>` |


<font style="color:rgba(0, 0, 0, 0.9);">  
</font><font style="color:rgba(0, 0, 0, 0.9);"> </font>


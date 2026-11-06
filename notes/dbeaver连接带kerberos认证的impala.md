# dbeaver连接带kerberos认证的impala


## 1、安装jdk ：


dbeaver 需要jdk :

bat环境变量配置：

```plain
setx /M JAVA_HOME "C:\Program Files\Java\jdk1.7.0_80"

setx /M CLASSPATH ".;%%JAVA_HOME%%\lib\dt.jar;%%JAVA_HOME%%\lib\tools.jar"

setx /M PATH "%PATH%;%%JAVA_HOME%%\bin"
```



## 2、安装kfw客户端


[https://web.mit.edu/kerberos/dist/index.html](https://links.jianshu.com/go?to=https%3A%2F%2Fweb.mit.edu%2Fkerberos%2Fdist%2Findex.html)



<!-- 这是一张图片，ocr 内容为：17.1.TAR.ASGPGPSIGHATURE,TK. MIT KERBEROS FOR WINDOWS 4.1 FOR MORE INFORMATION,PLEASE SEE THE RELEASE PAGE 64-BIT MSI INSTALLER KFW-4.1-AMD64.MSI,10812K. 32-BIT MSI INSTALLER KFW-4.1-I386.MSI,5836K. SOURCES KFW-4.1-SRC,ZIP, 7981K, DETACHED SIGHATURE KFW-4.1-SRC.ZIP.ASC. 1K. MIT KERBEROS FOR WINDOWS 3.2.2 HTINS.THLAN CSCLN NELMR KICLELK I -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1675218971779-b1b390bb-567a-4625-a6ef-d96c1912f0af.png)



## 3、新增krb5.ini
<!-- 这是一张图片，ocr 内容为：KERBEROS 共享 主页 查看 此电脑 > 本地磁盘(C:) PROGRAM FILES > KERBEROS 搜索"KERBEROS" 修改日期 类型 大小 名称 快速访问 2022/8/11 4:56 BIN 文件夹 桌面 INCLUDE 2022/8/11 4:27 文件夹 下载 LIB 文件夹 2022/8/11 4:27 文档 KEYTAB文件 20KB 2022/5/25 11:02 EVERDC.KEYTAB 图片 2022/6/20 15:19 配置设置 KRB5.INI 1 KB 此电脑 网络 -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1675218983652-7a0b3fbf-843d-4eec-87c4-15e3a3289377.png)



内容从linux 相关配置拷贝

```plain
[libdefaults]
 dns_lookup_realm = false
 ticket_lifetime = 24h
 renew_lifetime = 7d
 forwardable = true
 rdns = false
 default_realm = EVERDC.COM
 default_ccache_name = KEYRING:persistent:%{uid}

[realms]
 EVERDC.COM = {
  kdc = everdc24
  admin_server = everdc24
 }

[domain_realm]
 .everdc.com = EVERDC.COM
 everdc.com = EVERDC.COM
```



## 4、修改环境变量配置


> 在C盘创建**temp**文件夹
>

| 变量名 | 变量值 |
| --- | --- |
| KRB5_CONFIG | C:\Program Files\MIT\Kerberos\krb5.ini |
| KRB5CCNAME | C:\temp\krb5cache |




path检测配置：

<!-- 这是一张图片，ocr 内容为：快速访问 BIN 2016/6/20 18:4 CCAPISERVER.EXE 桌面 文件 主页 共享 查看 国.COMERR32.DL 2016/6/20.1A.2 环境变量 PROGRAM FILES>JAVA>JDK1.7.0 80>BIN 本地盘盘(C:) 此电脑 修改日期 名称 大小 类型 ADN 编辑环境变量 快速访问 应用程序 2022/8/11 4:48 16 KB MJSTAT.EXE 点面 2022/8/11 4:48 应用程序 16 KB ISTATD.EXE 新建(N) CILWINDOWSLSYSTEM32 下载 应用程序 2022/8/11 4:48 193 KB TVISUAIVM.EXE CLWINDOWS 以内存 文档 应用程序 2022/8/114848 16 KB C/WINDOWS/SYSTEM32\WBEM 编辑() 图片 应用程序 16KB 2022/8/11 4:48 CI WINDOWSISYSTEM32\WINDOWSPOWERSHELLYV1.0) 设置(S)... 应用程序 2022/8/11 4:48 16 KB KLISTEXE C\WINDOWS|SYSTEM321OPENSSH\ 浏览(B)... 此电脑 应用程序 16 KB C\USERS(ADMINISTRATORIAPPDATA\LOCAL\MICROSOFF/WINDOWSAPPS 2022/B/11 4:48 I KTAB EXE 网络 应用程序扩展 810KB MSVCR100.DLL 2022/8/11 4:48 C/PROGRAM FILES\MIT\KERBEROS\BIN 删除(D) 应用程序 16 KB 2022/8/11 4:48 %JAVA HOME%\BIN 应用程序 17KB 2022/8/11 4:48 应用程序 16KB 2022/8/11 4:48 PACK200 EXE 上移(U) 设置(E)... 应用程序 2022/8/11 4:48 16KB 系统 应用程序 16 KB 2022/8/11 4:48 下移(0) 应用程序 2022/8/11 4:48 16KB 变NO比阳印肝肝 建议将KERBEROS环境变量配置放JDK之前因为有同名文件 2022/8/11 4:48 应用程序 16 KB 2022/8/11 4:48 应用程序 16 KB 编辑文本(0... 应用程序 16 KB 2022/8/11 4:48 设置(T)... 应用程序 2022/B/11 4:48 16 KB 应用程序 2022/8/11 4:48 17KB J TNAMESERV.EXE 环境变量(N)-. 应用程序 180KB UNPACK200.EXE 2022/8/11 4:48 应用程序 2022/8/114:48 16 KB 应用程序 2022/8/11 4:48 16 KB WSIMPORTEXE 应用程序 2022/8/11 4:48 16KB XJC.EXE 52个项目 确定 取消 取消 应用(A) 激活WINDOWS -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1675219015566-4b550c08-9de9-43a5-8dab-0bcbcade70c2.png)





## 5、这边用keytab文件进行认证
遇到个问题：直接命令行执行 kinit -kt C:\Program Files\MIT\Kerberos\everdc.keytab impala/everdc01[@EVERDC.COM ](/EVERDC.COM )  老是有问题 

原因：Program Files 中间有个空格

拷贝文件到kfw安装路径的bin下面：



```shell
 执行：kinit -kt everdc.keytab impala/everdc01@EVERDC.COM
```



验证结果如下：

<!-- 这是一张图片，ocr 内容为：180 BIN 进入安装目录的BIN下输入CMD. 主页 查看 共享 文件 此电脑 本地磁盘(C:) PROGRAM FILES MIT > KEROS > BIN 搜索"BIN" 修改日期 大小 名称 类型 快速访问 应用程序 2016/6/2018:43 158 KB CCAPISERVER.EXE 桌面 应用程序扩展 2016/6/2018:31 14 KB COMERR32.DLL X 管理员:C:/WINDOWS\SYSTEM32\CMD.EXE TH.BA MICROSOFT WINDOWS [版本 10.0.17763.973] 保留所有权利. (C) 2018 MICROSOFT CORATION. KINIT -KT EVERDC.KEYTAB IMPALA/EVERDC01@EVERDC.COM C:\PROGRAM FILES\IT\KERBEROS\BIN C://PROGRAM FILES\IT\KERBEROS\B COS\BINKLIST TICKET CACHE:FILE:C:/TEMP\KRB5CACHE DEFAULTPRINCIPAL:IMPALA/EVERDCO1@EVERDC.COM SERVICE PRINCIPAL VALID STARTING EXPIRES 08/15/22 16:37:03 08/16/22 04:37:03 KRBTGT/EVERDC.COM@EVERDC.COM RENEW  UNTI1 08/22/22  16:37:03 C:/PROGRAM FILES\IT\KERBEROS/BIN> |MIT KERBEROS-THURSDAY,AUGUST 11,2022 05:39 文件 OPTIONS HOME CHANGE GET RENEW DESTROY MAKE TICKET TICKET  TICKET DEFAULT PASSWORD PRINCIPAL VALID UNTIL IMPALA/EVERDC01@EVER...8月164.37(... -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1675219050035-fee21ff2-f67d-4a16-916b-ccbe88ed757c.png)



## 6、dbeaver配置
在dbeaver.ini结尾添加：



```plain
-Djavax.security.auth.useSubjectCredsOnly=false
-Djava.security.krb5.conf=C:\Program Files\MIT\Kerberos\krb5.ini
-Dsun.security.krb5.debug=true
```



因为认证票据是用的主机名url模板修改如下：



jdbcurl模板：jdbc:impala://{host}:{port}/{database};AuthMech=1;KrbRealm=EVERDC.COM;KrbHostFQDN={host};KrbServiceName=impala;KrbAuthType=2

<!-- 这是一张图片，ocr 内容为：10.252.81.50-远程桌面连接 X 编辑驱动CLOUDERAIMPALA' 设置 GENERIC 驱动类型: CLOUDERA IMPALA 驱动名称: 导航(N)SEARCH SQL编辑器 帮助(H) 数据库(D)窗口(W) 类名: COM.CLOUDERA.IMPALA.JDBC.DRIVER JTTRO品 JDBC:IMPALA:/LOCALHOST:21050//DATABASE;AUTHMECH-1;KRBREALM URL 模板: 项目 默认端口: DEFAULT DATABASE: 21050 纷 DEFAULT USER: 口嵌入 口无认证口ALLOWEMPTYPASSWORD"USE LEGACYJDBCINSTANTIATION 描述 目录: HADOOP ID: CLOUDERA IMPALA CLOUDERA IMPALA. YOU CAN DOWNLOAD JDBC DRIVER FILES FROM HTTPS://WWW. 描述: 网址:HTTPS://WWW.CLOUDERA.COM/DOWNLOADS/CONNECTORS/IMPALA/JDBC/2-5 库 连接属性高级参数 C\USERS\ADMINISTRATOR\DESKTOP\DBEAVER\LMPALAJDBD 添加文件(E) (添加文件夹(D) 添加工件(A) 下载/更新(D) 信息() 删除(E) 类路径(C) 找到类 驱动类: -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1675219100318-0109f217-750e-4c60-b695-f75d5a3d0b36.png)



<!-- 这是一张图片，ocr 内容为：GOO 创建新连接 通用JDBC连接设置 HADOOP/CLOUDERA IMPALA 连接设置 常规 驱动属性 PROXY SSH 一般 JDBC URL:LJDBCIIMPALA://EVERDC01:21050/DEFAULT,AUTHMECH-1:KRBREALM-EVE 端口: 主机: 21050 EVERDC01 DEFAULT 数据库/模式: 认证(DATABASE NATIVE) 用户名: CONNECTION TEST 已连接(78MS) SERVER: IMPALA 2.12.0-CDH5.16.2 IMPALAJDBC02.06.15.1017 DRIVER: 详情(名称,类型...) 确定 编辑驱动设置 下一步(N)> 测试链接(T)... <上一步(B) 完成(F) 取消 -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1675219201574-57be1ad0-8cc6-4fa4-b616-07c2bd552bbf.png)





ps：遇到个gss的报错，经过排查系统时间不同步导致的



## <font style="color:rgb(51, 51, 51);">7、配置定时任务认证</font>
配置bat脚本：<font style="color:rgb(51, 51, 51);">auto_kerberos.bat</font>

```plain
cd C:\Program Files\MIT\Kerberos\bin
kinit -kt everdc.keytab impala/everdc01@EVERDC.COM
klist
```



<font style="color:rgb(51, 51, 51);">在E盘下面每天早上10:30执行认证</font>

<font style="color:rgb(51, 51, 51);">win7</font>

```plain
  at 10:30 /every:m,t,w,th,f,s,su "E:\auto_kerberos.bat"
```

win10

```plain
schtasks /create /tn "kerberos_login" /tr E:\auto_kerberos.bat /sc DAILY /st 10:30 #每天在10:30 执行
```

## 8、dbeaver驱动
链接：[https://pan.baidu.com/s/1NwQ-FObrMZdeZY2oPdICSw](https://pan.baidu.com/s/1NwQ-FObrMZdeZY2oPdICSw) 

提取码：1024




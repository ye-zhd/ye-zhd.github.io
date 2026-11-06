### <font style="color:rgb(60, 60, 67);">简介</font>
<font style="color:rgb(60, 60, 67);">Harbor 是一个开源的云原生容器镜像仓库（Container Registry），由 VMware 中国团队开发并贡献给 CNCF（Cloud Native Computing Foundation），现已成为 CNCF Graduated（毕业）级 项目。它专为企业级场景设计，由 Go 语言开发，扩展 Docker Registry V2，提供 Web UI、多租户、权限控制等企业特性。在 DevOps 流程中充当镜像中心化存储与分发平台，解决原生 Registry 缺乏管理、安全、审计等问题。</font>

### <font style="color:rgb(60, 60, 67);">Harbor 的架构组件</font>
<font style="color:rgb(60, 60, 67);">Harbor 采用微服务架构，主要组件包括：</font>

| **<font style="color:rgb(103, 103, 108);">组件</font>** | **<font style="color:rgb(103, 103, 108);">功能</font>** |
| --- | --- |
| **<font style="color:rgb(60, 60, 67);">Core</font>** | <font style="color:rgb(60, 60, 67);">API 服务、认证授权、项目管理</font> |
| **<font style="color:rgb(60, 60, 67);">Database</font>** | <font style="color:rgb(60, 60, 67);">存储元数据（PostgreSQL）</font> |
| **<font style="color:rgb(60, 60, 67);">Registry</font>** | <font style="color:rgb(60, 60, 67);">实际镜像存储（可接 S3、Swift、OSS 等对象存储）</font> |
| **<font style="color:rgb(60, 60, 67);">Job Service</font>** | <font style="color:rgb(60, 60, 67);">异步任务（如复制、垃圾回收、扫描）</font> |
| **<font style="color:rgb(60, 60, 67);">Portal</font>** | <font style="color:rgb(60, 60, 67);">Web 管理界面</font> |
| **<font style="color:rgb(60, 60, 67);">Admin Server</font>** | <font style="color:rgb(60, 60, 67);">配置管理</font> |
| **<font style="color:rgb(60, 60, 67);">Webhook Service</font>** | <font style="color:rgb(60, 60, 67);">事件通知</font> |
| **<font style="color:rgb(60, 60, 67);">Scanner Adapter</font>** | <font style="color:rgb(60, 60, 67);">对接漏洞扫描器（如 Trivy）</font> |


## <font style="color:rgb(60, 60, 67);">一、Harbor 安装先决条件</font>
### <font style="color:rgb(60, 60, 67);">资源需求</font>
<font style="color:rgb(60, 60, 67);">以下是部署 Harbor 的最小和推荐资源需求</font>

| **<font style="color:rgb(103, 103, 108);">资源</font>** | **<font style="color:rgb(103, 103, 108);">最小</font>** | **<font style="color:rgb(103, 103, 108);">推荐</font>** |
| :--- | :--- | :--- |
| <font style="color:rgb(60, 60, 67);">CPU</font> | <font style="color:rgb(60, 60, 67);">2 CPU</font> | <font style="color:rgb(60, 60, 67);">4 CPU</font> |
| <font style="color:rgb(60, 60, 67);">内存</font> | <font style="color:rgb(60, 60, 67);">4 GB</font> | <font style="color:rgb(60, 60, 67);">8 GB</font> |
| <font style="color:rgb(60, 60, 67);">磁盘</font> | <font style="color:rgb(60, 60, 67);">40 GB</font> | <font style="color:rgb(60, 60, 67);">160 GB</font> |


### <font style="color:rgb(60, 60, 67);">系统环境依赖需求</font>
| **<font style="color:rgb(103, 103, 108);">软件</font>** | **<font style="color:rgb(103, 103, 108);">版本</font>** | **<font style="color:rgb(103, 103, 108);">描述</font>** |
| :--- | :--- | :--- |
| <font style="color:rgb(60, 60, 67);">Docker Engine</font> | <font style="color:rgb(60, 60, 67);">Version > 20.10 版本 > 20.10</font> | [<font style="color:rgb(163, 144, 11);">Docker Engine 安装</font>](https://docs.docker.com/engine/install/) |
| <font style="color:rgb(60, 60, 67);">Docker Compose</font> | <font style="color:rgb(60, 60, 67);">Docker compose > 2.3</font> | <font style="color:rgb(60, 60, 67);">Docker Compose 是 Docker Engine 的一部分</font> |
| <font style="color:rgb(60, 60, 67);">OpenSSL</font> | <font style="color:rgb(60, 60, 67);">Latest (optional) 最新版（可选）</font> | <font style="color:rgb(60, 60, 67);">用于生成 Harbor 的证书和密钥</font> |


### <font style="color:rgb(60, 60, 67);">网络端口</font>
| **<font style="color:rgb(103, 103, 108);">Port 端口</font>** | **<font style="color:rgb(103, 103, 108);">Protocol 协议</font>** | **<font style="color:rgb(103, 103, 108);">Description 描述</font>** |
| :--- | :--- | :--- |
| <font style="color:rgb(60, 60, 67);">443</font> | <font style="color:rgb(60, 60, 67);">HTTPS</font> | <font style="color:rgb(60, 60, 67);">Harbor 门户和核心 API 在此端口上接受 HTTPS 请求。可以在配置文件中更改此端口。</font> |
| <font style="color:rgb(60, 60, 67);">80</font> | <font style="color:rgb(60, 60, 67);">HTTP</font> | <font style="color:rgb(60, 60, 67);">Harbor 门户和核心 API 在此端口上接受 HTTP 请求。</font> |


## <font style="color:rgb(60, 60, 67);">二、下载 Harbor 安装程序</font>
<font style="color:rgb(60, 60, 67);">可以从官方发布页面下载 Harbor 安装程序。下载在线安装程序或离线安装程序。</font>

+ <font style="color:rgb(60, 60, 67);">在线安装程序：在线安装程序从 Docker hub 下载 Harbor 镜像。因此，安装程序的大小非常小。</font>
+ <font style="color:rgb(60, 60, 67);">离线安装程序：离线安装程序包含预构建的镜像，因此它比在线安装程序大。</font>

<font style="color:rgb(60, 60, 67);">在线和离线安装程序的安装过程几乎相同。</font>

### <font style="color:rgb(60, 60, 67);">下载并解压安装程序</font>
<font style="color:rgb(60, 60, 67);">Harbor 版本发布页面 :</font><font style="color:rgb(60, 60, 67);"> </font>[<font style="color:rgb(0, 167, 213);">https://github.com/goharbor/harbor/releases</font>](https://github.com/goharbor/harbor/releases)

<font style="color:rgb(60, 60, 67);">下载要安装版本的在线或离线安装程序。</font>

<!-- 这是一张图片，ocr 内容为：BUMP TRIVY TO VO:71.1 AND TRIVY ADAPTER TO VO.37.1 BY @STONEZDJ IN #23386 RELEASE LIST BUMP TRIVY ADAPTER VERSION TO VO.37.1 BY @STONEZDJ IN #23422 BUMP BASE PHOTON OS IMAGE BY @STONEZDJ IN #23424 V2.15.2 SYNC PACKAGE-LOCKJSON IN UI BY @STONEZDJ IN #23431 V2.15.2-RC3 BUMP TRIVY(0.72.0)AND TRIVY ADATPER(O.38.0)BY @STONEZDJ IN #23480 V2.15.2-RC2 BUILD(REGISTRY):USE STABLE REGISTRY SOURCE TAG V2.8.3-HARBOR.1 BY @CHLINS IN #23482 V2.15.2-RC1 UPDATE BASE IMAGE BY @STONEZDJ IN #23485 V2.14.4 OTHER CHANGES V2.14.4-RC1 ? (CHERRY-PICKI SUPPORT CONFIGURABLE PIPINDEX URL FOR SWAGGER LLENT BUILD ($23241) @STONEZDJ IN #2324 V2.15.1  BUILD:USE DEV-LEGACY TAGS TO DECOUPLE 2.15 BUILDS FROM MAIN BY @WY65701436 IN #2336 IN #23360 V2.15.1-RC2 [BACKPORT 2.15.0) TESTUL):FXUI ROBOT TEST CASES FOR ANGULAR AND CLARITY UPGRADE BY @FIONA-XIE IN #233 V2.15.1-RC1 : [CHERY-PICK) TEST(U):ADD RETRY FOR GET HARBOR CA TO IMPROVE STABILITY($23396) BY @FIONA-XIE IN #234 V2.15.0 DOWNGRADE NODE-RELEASE TO 2.0.48 FOR BUILD COMPATIBILITY BY BY @STONEZDJ IN #23432 FULL CHANGELOG:V2.15.1...V2.15.2 NEXT PREVIOUS CONTRIBUTORS VAD1MO,STONEZDJ,AND 4 OTHER CONTRIBUTORS ASSETS 7 HARBOR-OFFLINE-INSTALLER-V2.15.2.TGZ 2 WEEKS AGO 696 MB SHA256:67517E0BA4A3F9DB9_ 10.2KB HARBOR-OFFLINE-INSTALLER-V2.15.2.TGZ.SIGSTORE.JSON SHA256:FDA352108BD8207AD.. 2 WEEKS AGO HARBOR-ONLINE-INSTALLER-V2.15.2.TGZ SHA256:88F6A7436B31890E8- 11.5KB 2 WEEKS AGO SHA256:4B08E33238247C65C." ( 10.1 KB HARBOR-ONLINE-INSTALLER-V2.15.2.TGZ.SIGSTORE.JSON 2 WEEKS AGO SHA256:C730145C8614480AC- 141 BYTES MD5SUM 2 WEEKS AGO SOURCE CODE(ZIP) 2 WEEKS AGO -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1783932658701-751ac531-7998-42f2-a43e-edf04be9c73b.png)

<font style="color:rgb(60, 60, 67);">离线版本</font>

```plain
tar xzvf harbor-offline-installer-v2.15.2.tgz
```

## <font style="color:rgb(60, 60, 67);">三、配置 Harbor 基于 HTTPS 访问</font>
<font style="color:rgb(60, 60, 67);">默认情况下，Harbor 不附带证书。但是也可以配置在不启用安全性的情况通过 HTTP 连接 Harbor。然而，只推荐在与外部互联网断开连接的测试或开发环境中，使用 HTTP 。在外部可访问环境中使用 HTTP 会使业务系统面临中间人攻击的风险。在生产环境中，请始终使用 HTTPS。</font>

<font style="color:rgb(60, 60, 67);">要配置 HTTPS，需要提前创建 SSL 证书。您可以使用由受信任的第三方 CA 签名的证书，或者您可以使用自签名证书。</font>

### <font style="color:rgb(60, 60, 67);">自签发证书</font>
<font style="color:rgb(60, 60, 67);">本节描述了如何使用 OpenSSL 创建 CA，以及如何使用您的 CA 来签发服务器证书和客户端证书。当然也可以使用其他 CA 提供商，例如 Let’s Encrypt。（推荐）</font>

#### <font style="color:rgb(60, 60, 67);">创建CA证书</font>
<font style="color:rgb(60, 60, 67);">在生产环境中，您应从 CA 获取证书。在测试或开发环境中，您可以生成自己的 CA。要生成 CA 证书，请运行以下命令。</font>

<font style="color:rgb(60, 60, 67);">生成 CA 证书私钥</font>

```plain
mkdir /data/cert/
cd /data/cert/
openssl genrsa -out ca.key 4096
```

<font style="color:rgb(60, 60, 67);">生成 CA 证书</font>

<font style="color:rgb(60, 60, 67);">将 </font>`<font style="color:rgb(0, 147, 253);background-color:rgba(142, 150, 170, 0.14);">-subj</font>`<font style="color:rgb(60, 60, 67);"> 选项中的值为您的组织信息。如果您使用 FQDN 连接 Harbor 主机，您必须将其指定为通用名称（ </font>`<font style="color:rgb(0, 147, 253);background-color:rgba(142, 150, 170, 0.14);">CN</font>`<font style="color:rgb(60, 60, 67);"> ）属性。</font>

```plain
openssl req -x509 -new -nodes -sha512 -days 3650 \
 -subj "/C=CN/ST=Beijing/L=Beijing/O=example/OU=Personal/CN=MyPersonal Root CA" \
 -key ca.key \
 -out ca.crt
```

#### <font style="color:rgb(60, 60, 67);">生成服务器证书</font>
<font style="color:rgb(60, 60, 67);">证书通常包含一个 </font>`<font style="color:rgb(131, 153, 27);background-color:rgba(142, 150, 170, 0.14);">.crt</font>`<font style="color:rgb(60, 60, 67);"> 文件和一个 </font>`<font style="color:rgb(131, 153, 27);background-color:rgba(142, 150, 170, 0.14);">.key</font>`<font style="color:rgb(60, 60, 67);"> 文件，例如， </font>`<font style="color:rgb(131, 153, 27);background-color:rgba(142, 150, 170, 0.14);">yourdomain.com.crt</font>`<font style="color:rgb(60, 60, 67);"> 和 </font>`<font style="color:rgb(131, 153, 27);background-color:rgba(142, 150, 170, 0.14);">yourdomain.com.key</font>`<font style="color:rgb(60, 60, 67);"> </font>

**<font style="color:rgb(60, 60, 67);">生成私钥: </font>**`**<font style="color:rgb(60, 60, 67);">openssl genrsa -out yzd.com.key 4096</font>**`

**<font style="color:rgb(60, 60, 67);">生成证书签名请求（CSR）</font>**

<font style="color:rgb(60, 60, 67);">将 </font>`<font style="color:rgb(233, 92, 162);background-color:rgba(142, 150, 170, 0.14);">-subj</font>`<font style="color:rgb(60, 60, 67);"> 选项中的值调整为反映您的组织。如果您使用完全限定域名（FQDN）连接到您的 Harbor 主机，您必须将其指定为常见名称（ </font>`<font style="color:rgb(233, 92, 162);background-color:rgba(142, 150, 170, 0.14);">CN</font>`<font style="color:rgb(60, 60, 67);"> ）属性，并在密钥和 CSR 文件名中使用它。</font>

```plain
 openssl req -sha512 -new   \
 -subj "/C=CN/ST=Beijing/L=Beijing/O=example/OU=Personal/CN=yzd.com"   \
 -key yzd.com.key  \
 -out yzd.com.csr
```

**<font style="color:rgb(60, 60, 67);">生成一个 x509 v3 扩展文件</font>**

<font style="color:rgb(60, 60, 67);">无论您是使用 FQDN 还是 IP 地址连接到您的 Harbor 主机，都必须创建此文件，以便您可以生成符合主题备用名称（SAN）和 x509 v3 扩展要求的证书。将 </font>`<font style="color:rgb(68, 162, 68);background-color:rgba(142, 150, 170, 0.14);">DNS</font>`<font style="color:rgb(60, 60, 67);"> 条目替换为您的域名。</font>

```shell
cat > v3.ext <<-EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
IP.1 = 10.20.3.112
DNS.1=yzd.com
DNS.2=harbor
EOF
```

**<font style="color:rgb(60, 60, 67);">使用 </font>**`**<font style="color:rgb(0, 164, 231);background-color:rgba(142, 150, 170, 0.14);">v3.ext</font>**`**<font style="color:rgb(60, 60, 67);"> 文件为您的 Harbor 主机生成证书。</font>**

<font style="color:rgb(60, 60, 67);">将 CSR 和 CRT 文件名中的 </font>`<font style="color:rgb(0, 167, 213);background-color:rgba(142, 150, 170, 0.14);">yourdomain.com</font>`<font style="color:rgb(60, 60, 67);"> 替换为 Harbor 主机名。</font>

```shell
openssl x509 -req -sha512 -days 3650   \
-extfile v3.ext     \
-CA ca.crt -CAkey ca.key -CAcreateserial   \
-in yzd.com.csr   \
-out yzd.com.crt
```



## <font style="color:rgb(60, 60, 67);">四、配置Harbor 和 Docker使用自签发证书</font>
<font style="color:rgb(60, 60, 67);">将服务器证书和密钥复制到 Harbor 主机上的 certificates 文件夹中。</font>

上面已经创建了/data/cert/目录

<font style="color:rgb(60, 60, 67);">将 </font>`<font style="color:rgb(241, 94, 105);background-color:rgba(142, 150, 170, 0.14);">yourdomain.com.crt</font>`<font style="color:rgb(60, 60, 67);"> 转换为 </font>`<font style="color:rgb(241, 94, 105);background-color:rgba(142, 150, 170, 0.14);">yourdomain.com.cert</font>`<font style="color:rgb(60, 60, 67);"> ，供 Docker 使用。</font>

```shell
openssl x509 -inform PEM -in  yzd.com.crt   -out  yzd.com.cert 
```

<font style="color:rgb(60, 60, 67);">将服务器证书、密钥和 CA 文件复制到 Harbor 主机上的 Docker 证书文件夹中。</font>

```shell
mkdir -p /etc/docker/certs.d/yzd.com/
cp yzd.com.cert /etc/docker/certs.d/yzd.com/
cp yzd.com.key /etc/docker/certs.d/yzd.com/
cp ca.crt /etc/docker/certs.d/yzd.com/
```

<font style="color:rgb(60, 60, 67);">如果您将默认的 </font>`<font style="color:rgb(0, 166, 226);background-color:rgba(142, 150, 170, 0.14);">nginx</font>`<font style="color:rgb(60, 60, 67);"> 端口 443 映射到了不同的端口，请创建 </font>`<font style="color:rgb(0, 166, 226);background-color:rgba(142, 150, 170, 0.14);">/etc/docker/certs.d/yourdomain.com:port</font>`<font style="color:rgb(60, 60, 67);"> 文件夹，或 </font>`<font style="color:rgb(0, 166, 226);background-color:rgba(142, 150, 170, 0.14);">/etc/docker/certs.d/harbor_IP:port</font>`<font style="color:rgb(60, 60, 67);"> 文件夹。</font>

<font style="color:rgb(60, 60, 67);"></font>

**<font style="color:rgb(60, 60, 67);">重启 Docker Engine</font>**

```plain
systemctl restart docker
```

<font style="color:rgb(146, 146, 149);background-color:rgba(125, 125, 125, 0.04);">1</font>

**<font style="color:rgb(60, 60, 67);">使用自定义证书的配置说明</font>**

```shell
[root@localhost cert]# tree /etc/docker/certs.d/
/etc/docker/certs.d/
└── yzd.com
    ├── ca.crt
    ├── yzd.com.cert
    └── yzd.com.key

1 directory, 3 files
```

## <font style="color:rgb(60, 60, 67);">五、部署Harbor</font>
### <font style="color:rgb(60, 60, 67);">配置 Harbor YML 文件</font>
**<font style="color:rgb(60, 60, 67);">1、解压并修改配置文件</font>**

```bash
tar -zxvf harbor-offline-installer-v2.15.2.tgz     # 解压tgz包
cp harbor.yml.tmpl harbor.yml                    # 创建一个配置文件
vim harbor.yml                                   # 修改配置文件
```

**<font style="color:rgb(60, 60, 67);">配置的文件的修改如下所示：  
</font>****<font style="color:rgb(60, 60, 67);"> </font>**<!-- 这是一张图片，ocr 内容为：1001@IOCALHOST: EVERSEC@LO # CONFIQURATION FILE OF HARBOR # THE IP ADDRESS OR HOSTNAME TO ACCESS ADMIN UI AND REGISTRY SER RY SERVICE. CLIENTS. D BY EXTERNAL 127.0.0.1, BECAUSE HARBOR NEEDS TO BE ACCESSED BE # DO NOT USE IOCAINOST OR HOSTNAME:10.20.3.112 修改主机名称,不要用LOCALHOST或者127.0.1 # HTTP RELATED CONFIG HTTP: # PORT FOR HTTP, DEFAULT IS 80. IF HTTPS ENABLED, THIS PORT WILL REDIRECT TO HTTPS PORT PORT:80 # HTTPS RELATED CONFIG HTTPS: DEFAULT IS 443 # HTTPS PORT FOR HARBOR, PORT:443 KEY FILES FOR NGINX AND CER # TNE PATN OF HTTPS证书位置 DATA/CERT/YZD.COM.CRT CERTIFICATE://DA PRIVATE_KEY: /DATA/CERT/YZD.COM.KEY # ENABLE STRONG SSI CIPHERS (DEFAULT: FALSE) #ST STRONG_SSL_CIPHERS: FALSE SET IPV4 ENABLED ONLY BY DEFAULT IF THIS BLOCK IS NOT CONFIGURED # HARBOR WILL 并并并并并并并并并 OTHERWISE, #                                                                  TO CONFIGURE YOUR OWN SLEASE UNCOMMENT THIS BLOCK TO CO IP_FAMILY STACKS PLEAS IP_FAMILY: IT AFFECTED THE NGINX RELATED COMPONENT # IPVGENABLED SET TO TRUE IF IPVE IS ENABLED IN DOCKER HETWORK, CURRENTLY IPV6: ENABLED:FALSE # 1PVAENABLED SET TO TRUE BY DEFAU1T, CURTENTIY 1T AFFECTED THE NGLUX FELATED COMPONENT IPV4: ENABLED: TRUE ABLE TLS COMMUNICATION BETWEEN ALL HARBOR COMPONENTS NG WILL ENABLE #UNCOMMENT FOLLOWING 井井井井井井 INTERNAL_TLS: INTERNAL TLS IS ENABLED # SET ENABLED TO T TRUE MEANS ENABLED:TRUE # PUT YOUR CERT AND KEY FILES ON DIR DIR: /ETC/HARBOR/TLS/INTERNAL E UNCOMMENT EXTERNAL_URL IF YOU WANT TO ERE ENABLE PROXY EXTERNAL 井井井 AND WHEN IT ENABLED THE HOSTNAME WILL NO LONGER USED EXTERNAL_URL:HTTPS://REG.MYDOMAIN.COM:8433 # THE INITIAL PASSWORD OF HARBOR ADMIN # IT ONLY WORKS IN FIRST TIME TO INSTALL HARBOR "HARBOR.YML" 329L, 14652B -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1783937856418-6b96daae-6215-4897-a226-3199686468c2.png)

**<font style="color:rgb(60, 60, 67);">默认密码修改：</font>**

<!-- 这是一张图片，ocr 内容为：_URL: HTTPS://REG.MYDOMAIN.COM:8433 EXTERNA : THE INITIAL PASSWORD OF HARBOR ADMIN N FIRST TIME TO INSTALL HARBOR IT ONLY WORKS IN FI # REMEMBER CHANGE THE ADMIN PASSWORD FROM UI AFTER LAUNCHING HARBOR. # REMEMB HARBOR_ADMIN_PASSWORD: HARBOR12345 HARBOR DB CONFIGURATION -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1783937881509-7187b592-1d47-4225-a92d-405839f3983a.png)

**<font style="color:rgb(60, 60, 67);">启动关闭命令：</font>**

```bash
docker-compose -f docker-compose.yml up -d            启动 Harbor
docker-compose -f docker-compose.yml stop             关闭 Harbor
```

**<font style="color:rgb(60, 60, 67);">访问Harbor</font>**

<!-- 这是一张图片，ocr 内容为：ALLPS://10.20.3.112/HARBOR/PROJECTS 脂 着歌放院器CHROM... MYSQL数据识到灰... 'PORTAINER 容器钠... 从零搭建企业级CV/... 所有书签 全部扫错差 默认扫描器已安装. 装.获取扫描器安装帮助,请查看 文档. HARBOR 搜索HARBOR... ADMIN 品项目 项目 已使用的配额 项目 镜像仓库 军日志 私有 私有 品 系统管理 公开 公开 BYTE 路 用户管理 总计 总计 机器人账户 仓库管理 新建项目 所有项目 心复制管理 44 提像仓库数 类型 项目名称 分布式分发 0 公开 项目管理员 2026/7/3 18:26 项目 LIBRARY 标签 1-1共计1条记录 页新大小    项目定额 审查服务 画清理服务 @任务中心 公配置管理 头浅色主题 # HARBOR API V2.0 -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1783936148560-911fd5a1-7b93-49b7-9a08-99b1583050cc.png)

**<font style="color:rgb(60, 60, 67);">Harbor设置开机自启动</font>**

```shell
sudo vim /etc/systemd/system/harbor.service

[Unit]
Description=Harbor Docker Compose Service
After=docker.service network-online.target
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/data/harbor
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target                          
```

+ <font style="color:rgb(60, 60, 67);">WorkingDirectory为你harbor所在目录</font>
+ <font style="color:rgb(60, 60, 67);">ExecStart为你docker-compose所在目录启动命令</font>
+ <font style="color:rgb(60, 60, 67);">ExecStop为你docker-compose所在目录停止命令</font>

## <font style="color:rgb(60, 60, 67);">6.Harbor使用</font>
### <font style="color:rgb(60, 60, 67);">GUI界面使用</font>
创建用户

<!-- 这是一张图片，ocr 内容为：按索HARBOR... ADMIN 用户管理 操作Y 创建用户 设置为管理员 创建用户 注册时间 用户名 2026/7/13 19:43 YE-EVERSEC 用户名 页面大小 15 1-1共计1条记录 邮箱 123@1QQ.COM 全名 密码 确认密码 注释 取消 确定 -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1783940588314-1bae6d5a-f894-434d-b8dd-077eb952ded8.png)

新建项目

<!-- 这是一张图片，ocr 内容为：然认扫描器已安装.获取扫描器安装帮助,访查者文指. 全部扫描蒸 ADMIN 搜索 HARBOR. HARBOR 品项目 项目 镜像仓库 项目 已使用的配额 华日志 私有 私有 OOO 新建项目 品系统管理 公开 公开 BYTE 照用户管理 总计 总计 总机器人账户 项目名称 中仓库管理 所有项目 V C 公开 6复制管理 访问级别(I) 创建对网 访同级别 镜像仓库数 项目名移 分布式分发 10 项目配新限制 公开 2026/7/13 18:26 标签 贡画大小 15 1-1共计1条记录 2项目定额 镜像代理 申查服务 曲清理服务 @任务中心 急配置管理 确定 -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1783940525920-4f24596e-f989-48e1-88b7-575244f673ec.png)

点击新建的项目->点击推送命令可以<font style="color:rgb(34, 34, 34);background-color:rgba(255, 255, 255, 0.9);">帮助命令</font>

<!-- 这是一张图片，ocr 内容为：默认扫描器已安装.获取扫描器安装帮助,请查看文指. 全部扫描器 ADMIN HARBOR 搜索 HARBOR 项目 品项目 访问级别 已使用的配额 宰日国 品 EVERSEC 系统管理员 OBYTE OF 10GIS 公开 %系统管理 密用户管理 &机器人账户 日志 机器人账户 配置管理 概要 标签 扫描器 成员 镜像仓库 P2P 预热 WEBHOOKS 策路 推送命令 仓库管理 C 复制管理 C 川路 删除 推送命令 DOCKER 推送命令 分布式分发 在项目中标记锁像: 名称 ARTIFACLS O 标签 DOCKER TAG SOURCE IMAGE[:TAG]10.20.3.112/EVERSEC/REPOSITORY[:TAG] 项目定额 推送镜像到当前项目: O审查服务 DOCKER PUSH 10.20.3.112/EVERSEC/REPOSITORY[:TAG] 未发 消理服务 PODMAN 推送命令 @任务中心 页面大小  5 0条记录 推送镜像到当前项目: 感配置管理 PODMAN PUSH IMAGE_ID 10.20.3.112/EVERSEC/REPOSITORY[:TAG] HELM 推送命令 在项目中打包CHART HELM PACKAGE CHART_PATH 推送CHART到当前项目 HELM PUSH CHART_PACKAGE OCI://10.3.112/EVERSEC CNAB推送命令 推送CNAB到当前项目 火浅色主题 CNAB-TO-OCI PUSH CNAB PATH -TARGET 10.3.112/EVERSEC/REPOSITORY[:TAG] HARBOR API V2.0 -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1783940647797-fbe42b52-3c04-4a70-ade8-66f644dd0eb1.png)



在10.20.3.110使用docker命令登录：



```shell
[root@localhost ~]# docker login yzd.com
Username: ye-eversec
Password: 
Error response from daemon: Get "https://yzd.com/v2/": tls: failed to verify certificate: x509: certificate signed by unknown authority
```



配置`<font style="color:rgb(34, 34, 34);background-color:rgba(255, 255, 255, 0.9);">/etc/docker/daemon.json</font>`

```shell
[root@localhost ~]# cat /etc/docker/daemon.json 
{
 "data-root": "/var/lib/docker",
 "experimental": true,
 #添加下面insecure-registries参数
 "insecure-registries": ["yzd.com","10.20.3.112"],
 "fixed-cidr-v6": "fc00:1010:1111:100::/64",
 "ip6tables": true,
 "ipv6": true,
 "live-restore": true,
 "log-driver": "json-file",
 "log-opts": {
  "max-file": "3",
  "max-size": "10m"
 }
}
```



<font style="color:rgb(34, 34, 34);background-color:rgba(255, 255, 255, 0.9);">使用docker login +本机IP 登录</font>

```shell
[root@localhost ~]# docker login 10.20.3.112
Username: eversec
Password: 

WARNING! Your credentials are stored unencrypted in '/root/.docker/config.json'.
Configure a credential helper to remove this warning. See
https://docs.docker.com/go/credential-store/

Login Succeeded
```





修改镜像名称

```shell
[root@localhost ~]# docker images
REPOSITORY                                                                TAG              IMAGE ID       CREATED         SIZE
registry.gitlab.com/gitlab-org/gitlab-runner/gitlab-runner-helper         x86_64-v19.1.1   8b61837fb534   2 weeks ago     96.6MB
swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/gitlab/gitlab-runner   alpine-v19.1.1   44213fee200e   2 weeks ago     218MB
nginx                                                                     1.30.3           de3a24b07595   2 weeks ago     161MB
swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/nginx          1.30.3           de3a24b07595   2 weeks ago     161MB
swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/gitlab/gitlab-ce       19.1.1-ce.0      6586624305f0   2 weeks ago     3.46GB
swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/sameersbn/gitlab       18.11.1          4691dbfeefff   2 months ago    4.03GB
swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/node           lts-alpine3.23   5388a27f19ee   3 months ago    160MB
node                                                                      lts-alpine3.23   5388a27f19ee   3 months ago    160MB
jumpserver/koko                                                           v4.10.16-ce      c14831209054   4 months ago    653MB
jumpserver/lion                                                           v4.10.16-ce      8db5f76d9aa9   4 months ago    377MB
jumpserver/chen                                                           v4.10.16-ce      64d87cb3a180   4 months ago    562MB
jumpserver/core                                                           v4.10.16-ce      d2f28911697f   4 months ago    1.04GB
jumpserver/web                                                            v4.10.16-ce      bbee906fea24   4 months ago    272MB
postgres                                                                  16.10-bookworm   8ba5ca87c6a4   8 months ago    435MB
redis                                                                     7.4.6-bookworm   b4e53bb4637c   9 months ago    117MB
swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/sameersbn/gitlab       17.11.0          1c6e60b38b1b   15 months ago   4.46GB
swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/docker         latest           49fc2acb217f   17 months ago   378MB
docker                                                                    dind             0af54085b408   22 months ago   366MB
swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/docker                 dind             0af54085b408   22 months ago   366MB
mysql                                                                     8.0.37           8279f68ee77d   2 years ago     567MB
swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/mysql          8.0.37           8279f68ee77d   2 years ago     567MB
gcr.io/kaniko-project/executor                                            v1.22.0-debug    c7c1f8d3d464   2 years ago     99.1MB
swr.cn-north-4.myhuaweicloud.com/ddn-k8s/gcr.io/kaniko-project/executor   v1.22.0-debug    c7c1f8d3d464   2 years ago     99.1MB
alpine                                                                    latest           05455a08881e   2 years ago     7.38MB
swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/selectdb/alpine        latest           05455a08881e   2 years ago     7.38MB
yezhidi-test                                                              latest           ca20687373af   2 years ago     7.38MB
#修改
[root@localhost ~]# docker tag alpine:latest  10.20.3.112/eversec/web-alpine:v0.1

```



上传镜像

```shell
[root@localhost ~]# docker push 10.20.3.112/eversec/web-alpine:v0.1
The push refers to repository [10.20.3.112/eversec/web-alpine]
d4fc045c9e3a: Preparing 
unauthorized: unauthorized to access repository: eversec/web-alpine, action: push: unauthorized to access repository: eversec/web-alpine, action: push
[root@localhost ~]# 
```

这里报错了把前面新建的用户加到新建的项目组里面

<!-- 这是一张图片，ocr 内容为：默认扫描器已安装.获取扫描器安装帮助,请查看文档. 全部扫描器 HARBOR 搜索HARBOR... DMIN 项目 品项目 已使用的配额 访问级别 日日志 EVERSEC 系统管理员 OBYTE OF 10GIB 公开 系统管理 新建成员 路 用户管理 名机器人账户 镜像仓库 成员标 概要 添加用户到此项目中并给予相对应的角色 仓库管理 名称 Q制管理 十用户 十组 分布式分发 角色 项目管理员 角色 名称 标签 维护人员 项目管理员 ADMIN 开发者 项目定额 访客 15 1-1共计1条记录 页面大小 审查服务 受限访客 血清理服务 任务中心 取消 确定 锁 配置管理 浅色主题 HARBOR APIV2.O -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1783947392898-2de8f3b9-09ac-40ea-9993-1688cdf8fc08.png)

再提交

<!-- 这是一张图片，ocr 内容为：[ROOTALOCALHOST -]# DOCKER PUSH 10.20.3.112/EVERSEC/WEB-ALPINE:VO.1 ITHE PUSH REFERS TO REPOSITORY [10.20.3.112/EVERSEC/WEB-ALPINE] D4FC045C9E3A:PREPARING [ROOT@LOCALHOST -]# DOCKER PUSH 10.20.3.112/EVERSEC/WEB-ALPINE:VO.1 ITHE PUSH REFERS TO REPOSITORY [10.20.3.112/EVERSEC/WEB-ALPINE] D4FC045C9E3A:PUSHED IVO.1: DIQEST: SHA256:6457453F6065D6F250E150469696C42056626594LD57532C0720929DD0628977DO SIZE: 528 [ROOT@LOCALHOST~]# -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1783947577185-3d746ddb-22b2-44fe-bf67-1a796dd28144.png)

<font style="color:rgb(34, 34, 34);background-color:rgba(255, 255, 255, 0.9);">查看镜像,创建成功</font>

<!-- 这是一张图片，ocr 内容为：)默认扫描器已安装.获取扫描器安装帮助,请查看文档. 全部扫描器 HARBOR 搜索 HARBOR... ADMIN 项目 品项目 已使用的配额 访问级别 国日志 品 EVERSEC 系统管理员 OBYTE OF 10GIB 系统管理 公开 路 用户管理 机器人账户 配置管理 日志 镜像仓库成员标签扫描器P2P预热策略策略机器人账户 概要  镜像 WEBHOOKS 仓库管理 金复制管理 推送命令 88元 删除 分布式分发 山竹 11 下载数 名称 1个 最新变更时间 ARTIFACTS 标签 2026/7/13 21:42 O 1 EVERSEC/WEB-ALPINE 项目定额 1-1共计1条记录 页面大小 15 市查服务 血清理服务 任务中心 配置管理 点浅色主题 HARBOR API V2.O -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1783947631067-67cf7da5-2a47-4f71-987d-f828d246dc8c.png)

拉起镜像测试

```shell
[root@localhost ~]# docker rmi 10.20.3.112/eversec/web-alpine:v0.1
Untagged: 10.20.3.112/eversec/web-alpine:v0.1
Untagged: 10.20.3.112/eversec/web-alpine@sha256:6457d53fb065d6f250e1504b9bc42d5b6c65941d57532c072d929dd0628977d0
[root@localhost ~]# docker pull 10.20.3.112/eversec/web-alpine:v0.1
v0.1: Pulling from eversec/web-alpine
Digest: sha256:6457d53fb065d6f250e1504b9bc42d5b6c65941d57532c072d929dd0628977d0
Status: Downloaded newer image for 10.20.3.112/eversec/web-alpine:v0.1
10.20.3.112/eversec/web-alpine:v0.1
```

<!-- 这是一张图片，ocr 内容为：ITROOT@LOCALHOST -1# DOCKER RMI 10.20.3.112/EVERSEC/WEB-ALPINE:VO.1 LUNTAGQED: 10.20.3.112/EVERSEC/WEB-ALPINE:VO.1 ITROOTATOCALHOST -]# DOCKER PULL 10.20.3.112/EVERSEC/WEB-ALPINE:VO.1 VO.1:PULLING FROM EVERSEC/WEB-ALPINE IDIGEST: SHA256:645753FB065D6F250E150469BC42D5B6C65941D57532CO72D929DD0628977DO ISTATUS: DOWNLOADED NEWER IMAGE FOR 10.20.3.112/EVERSEC/WEB-ALPINE:VO.1 10.20.3.112/EVERSEC/WEB-ALPINE:V0.1 [ROOT@LOCALHOST~]# -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1783947733662-713bbc9c-72e1-4f24-a632-fcbce1a7fb5d.png)



**<font style="color:rgb(34, 34, 34);background-color:rgba(255, 255, 255, 0.9);">使用Harbor的注意事项：</font>**

1. <font style="color:rgb(34, 34, 34);background-color:rgba(255, 255, 255, 0.9);">在客户端上传镜像时一定要记得执行docker login进行用户认证，否则无法直接push</font>
2. <font style="color:rgb(34, 34, 34);background-color:rgba(255, 255, 255, 0.9);">在客户端使用的时候如果不是用的https则必须要在客户端的/etc/docker/daemon.json配置文件中配置insecure-registries参数</font>
3. <font style="color:rgb(34, 34, 34);background-color:rgba(255, 255, 255, 0.9);">数据存放路径应在配置文件中配置到一个容量比较充足的共享存储中</font>
4. <font style="color:rgb(34, 34, 34);background-color:rgba(255, 255, 255, 0.9);">Harbor是使用docker-compose命令来管理的，如果需要停止Harbor也应用docker-compose stop来停止，其他参数请--help</font>

### <font style="color:rgb(60, 60, 67);">Harbor 复制管理</font>
<font style="color:rgb(36, 41, 46);">Harbor 提供了 harbor 与非 harbor 服务之间的镜像复制功能，通过复制镜像功能可以将 DockerHub 上的私有镜像给批量的同步到本地，也可以通过在多 Harbor 实例之间进行同步，达到镜像多副本，数据高可用的作用。如下图：</font><!-- 这是一张图片，ocr 内容为： -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1784370710800-34c3a343-03dd-42c1-86e8-912666bcb550.png)

<font style="color:rgb(36, 41, 46);">当 Harbor 系统管理员身份设置好复制规则后，当满足触发条件时，所有与规则匹配的资源都会被复制到目标仓库中。每个被复制的资源都会启动一个复制任务。如果目标仓库中不存在命名空间，则会自动创建一个新的命名空间。</font>

<font style="color:rgb(36, 41, 46);">借助该功能，既可以用作 harbor 仓库的备份，也可以用于测试环境和生产环境之间做镜像、artifact 等制品的同步。作为一种可以考虑的高可用部署的方案，可以部署两套 harbor，互相配置镜像复制同步。</font>

<font style="color:rgb(36, 41, 46);">登录 Harbor，打开“复制管理”选项卡，该页面用来管理复制规则，如新增、修改、删除复制规则等，如下图：</font>

### <font style="color:rgb(36, 41, 46);">新建复制规则</font>
<font style="color:rgb(36, 41, 46);">点击“+ 新增规则”按钮新建规则，填写名称、描述、复制模式、资源过滤器、目的Registry等信息，如下图：</font>

<!-- 这是一张图片，ocr 内容为：修改规则 名称 UAT-PUSH-PROD 描述 复制模式 PUSH-BASED PULL-BASED 源资源过滤器 名称: 匹配 TAG: 标签: 匹配 资源: 全部 目标仓库 PROD-HTTPS://10.20.3.112 名称空间: 目标 EVERSEC 替换1级 仓库扁平化: 触发模式 事件驱动 取消 保存 -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1784370813312-2ace8fd7-2ddd-4d1e-8c73-1767efb7d8e7.png)<font style="color:rgb(36, 41, 46);">参数说明：</font>

+ <font style="color:rgb(36, 41, 46);">名称：复制规则的名称</font>
+ <font style="color:rgb(36, 41, 46);">描述：复制规则的描述信息</font>
+ <font style="color:rgb(36, 41, 46);">复制模式：用来指定当前复制规则的动作，其中：</font>
    - <font style="color:rgb(36, 41, 46);">Push-based  表示把资源从本地 Harbor 推送到远端仓库。</font>
    - <font style="color:rgb(36, 41, 46);">Pull-based  表示把资源从远程仓库拉取到本地 Harbor。</font>
+ <font style="color:rgb(36, 41, 46);">资源过滤器：</font>
    - <font style="color:rgb(36, 41, 46);">名称：过滤资源的名称，不填写或者 ""，匹配所有资源；"library/" 只匹配 "library" 下的资源。</font>
    - <font style="color:rgb(36, 41, 46);">Tag：过滤资源的 tag/version。</font><font style="color:rgb(36, 41, 46);">不填写或者 ""，匹配所有资源；"1.0" 只匹配以 "1.0" 开头的 tag/version。</font>
    - <font style="color:rgb(36, 41, 46);">标签：根据标签筛选资源。</font>
    - <font style="color:rgb(36, 41, 46);">资源：过滤资源类型。</font>
+ <font style="color:rgb(36, 41, 46);">目的 Registry：指定目的仓库，该仓库信息在“仓库管理”中添加目的。</font>
+ <font style="color:rgb(36, 41, 46);">目的 Namespace：指定目的端名称空间。如果不填，资源会被放到和源相同的名称空间下。</font>
+ <font style="color:rgb(36, 41, 46);">触发模式：</font>
    - <font style="color:rgb(36, 41, 46);">手动：手动触发。</font>
    - <font style="color:rgb(36, 41, 46);">定时：使用 CRON 表达式指定定时触发条件。</font>
    - <font style="color:rgb(36, 41, 46);">事件驱动：由 Harbor 的事件触发，如 Push 事件。</font>

<font style="color:rgb(36, 41, 46);">注意：</font>

<font style="color:rgb(36, 41, 46);">（1）如果勾选“</font><font style="color:rgb(36, 41, 46);">删除本地资源时同时也删除远程的资源</font><font style="color:rgb(36, 41, 46);">”，则本地仓库 Harbor 和远程仓库将保持一致。</font>

<font style="color:rgb(36, 41, 46);">（2）如果勾选“覆盖”，在同步镜像时，如果存在具有相同名称的资源，则会自动覆盖目标上的资源。</font>

### <font style="color:rgb(36, 41, 46);">复制实践</font>
<font style="color:rgb(36, 41, 46);">如果我们存在如下架构的 Harbor，在“源Harobr”中配置了一个复制规则，该规则将复制镜像到“目标Harbor”，如下图：</font>

<!-- 这是一张图片，ocr 内容为： -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1784371040964-120af818-f0e3-4f10-8645-29bfd4c62487.png)

<font style="color:rgb(36, 41, 46);">在 Docker 中执行如下命令推送 redis 镜像到源 Harbor 服务，如下：</font>

```shell
[root@localhost ~]# docker login http://10.20.3.116:8081/
Username: eversec
Password: 

WARNING! Your credentials are stored unencrypted in '/root/.docker/config.json'.
Configure a credential helper to remove this warning. See
https://docs.docker.com/go/credential-store/

Login Succeeded
[root@localhost ~]# docker images
REPOSITORY                                                                TAG              IMAGE ID       CREATED         SIZE
registry.gitlab.com/gitlab-org/gitlab-runner/gitlab-runner-helper         x86_64-v19.1.1   8b61837fb534   3 weeks ago     96.6MB
swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/gitlab/gitlab-runner   alpine-v19.1.1   44213fee200e   3 weeks ago     218MB
nginx                                                                     1.30.3           de3a24b07595   3 weeks ago     161MB
swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/nginx          1.30.3           de3a24b07595   3 weeks ago     161MB
swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/gitlab/gitlab-ce       19.1.1-ce.0      6586624305f0   3 weeks ago     3.46GB
swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/sameersbn/gitlab       18.11.1          4691dbfeefff   2 months ago    4.03GB
node                                                                      lts-alpine3.23   5388a27f19ee   3 months ago    160MB
swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/node           lts-alpine3.23   5388a27f19ee   3 months ago    160MB
jumpserver/koko                                                           v4.10.16-ce      c14831209054   4 months ago    653MB
jumpserver/lion                                                           v4.10.16-ce      8db5f76d9aa9   4 months ago    377MB
jumpserver/chen                                                           v4.10.16-ce      64d87cb3a180   4 months ago    562MB
jumpserver/core                                                           v4.10.16-ce      d2f28911697f   4 months ago    1.04GB
jumpserver/web                                                            v4.10.16-ce      bbee906fea24   4 months ago    272MB
postgres                                                                  16.10-bookworm   8ba5ca87c6a4   8 months ago    435MB
redis                                                                     7.4.6-bookworm   b4e53bb4637c   9 months ago    117MB
swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/sameersbn/gitlab       17.11.0          1c6e60b38b1b   15 months ago   4.46GB
swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/docker         latest           49fc2acb217f   18 months ago   378MB
swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/docker                 dind             0af54085b408   22 months ago   366MB
docker                                                                    dind             0af54085b408   22 months ago   366MB
mysql                                                                     8.0.37           8279f68ee77d   2 years ago     567MB
swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/mysql          8.0.37           8279f68ee77d   2 years ago     567MB
gcr.io/kaniko-project/executor                                            v1.22.0-debug    c7c1f8d3d464   2 years ago     99.1MB
swr.cn-north-4.myhuaweicloud.com/ddn-k8s/gcr.io/kaniko-project/executor   v1.22.0-debug    c7c1f8d3d464   2 years ago     99.1MB
yezhidi-test                                                              latest           ca20687373af   2 years ago     7.38MB
10.20.3.112/eversec/web-alpine                                            v0.1             05455a08881e   2 years ago     7.38MB
alpine                                                                    latest           05455a08881e   2 years ago     7.38MB
swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/selectdb/alpine        latest           05455a08881e   2 years ago     7.38MB
[root@localhost ~]# docker tag redis:7.4.6-bookworm 10.20.3.116:8081/uat/redis:7.4.6 
[root@localhost ~]# docker push 10.20.3.116:8081/uat/redis:7.4.6
The push refers to repository [10.20.3.116:8081/uat/redis]
0e2b13b72cd3: Pushed 
5f70bf18a086: Pushed 
28731d7170a2: Pushed 
c064b08fd97d: Pushed 
6f5ff7f21159: Pushed 
67ddf0db316b: Pushed 
6fcfc5539098: Pushed 
d6d0586ce802: Pushed 
7.4.6: digest: sha256:3a2ed3ae57f5d7475c50065ba6675a77ec438d1539304f59a90ac59264d4f252 size: 1986
```

<font style="color:rgb(36, 41, 46);">结果如下：</font>

<!-- 这是一张图片，ocr 内容为：SWR.CN-NORTH-4.MYHUAWEICLOUD.COM/DDN-K8S/DOCKER.IO/SELECTDB/ALPINE 7.38ME LATEST 05455A08881E YEARS AGO [ROOTOLOCALHOST -]# DOCKER TAG REDIS:7.4.6-BOOKWORM 10:20:3,1166F8031/UAT/FEDIS:7.4.0L [ROOTELOCALHOST ~]# DOCKER PUSH 10.20.3.116:8081/UAT/REDIS:7.4.6 THE PUSH REFERS TO REPOSITORY [10.20.3.116:8081/UAT/REDIS] 0E2B13B72CD3: B:PUSHED 5F70BF18A086: PUSHED 28731D7170A2: PUSHED C064B08FD97D: PUSHED 6F5FF7F21159: PUSHED 67DDFODB316B:PUSHED 6FCFC5539098:PUSHED 59.24MB/74.81MB D6DO586CE802: PUSHING -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1784371653281-ccecd561-c346-4768-98f9-dbc2ffff56c3.png)

<font style="color:rgb(36, 41, 46);">执行完上面命令后，再次进入“复制管理”页面，多出了一条日志记录，该日志触发模式为“event_based”，如下图：</font>

<!-- 这是一张图片，ocr 内容为：事件日志 复制管理 操作 新建规则 巴复制 状态 名称 复制模式 源仓库 目标仓库扁平化 目标仓库:名称空间 触发器 替换1级 启用 基于事件 UAT-PUSH-PROD PUSH-BASED LOCAL PROD:EVERSEC 15 1-1共计1条记录 页面大小 管理列 复制任务 停止任务 成功百分比 触发器 1个 状态 11 持续时间 ID 1个 创建时间 总数 SUCCEEDED 2026/7/18 19:30 100% 13 S6 EVENT BASED 1-1共计1条记录 页面大小15Y -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1784371751596-90ee6afb-4913-4268-82b6-22aa989b7cba.png)

<font style="color:rgb(36, 41, 46);">登录到目标 Harbor，查看项目“demo”项目，多出了一个 demo/redis 镜像，这就是刚才我们推送到源 Harbor 上的镜像，如下图：</font>

<!-- 这是一张图片，ocr 内容为：搜索HARBOR... ADMIN 事件日志 项目 访问级别 已使用的配额 品 EVERSEC 系统管理员 34.64MIB 公开 OF 10GIB P2P预热 标签 扫描器 成员 机器人账户 策略 日志 概要 配置管理 WEBHOOKS 镜像仓库 推送命令 X删除 名称 最新变更时间 JT 4个 ARTIFACTS 下载数 2026/7/18  19:31 O EVERSEC/REDIS 1 1 2 EVERSEC/WEB-ALPINE 2026/7/14 02:22 页面大小15 1-2共计2条记录 -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1784371855527-5114d0f8-754a-4feb-a767-efe6bf7d3730.png)





### 创建jenkins 机器人账号
用来jenkins 复制推送镜像

<!-- 这是一张图片，ocr 内容为：HARBOR 搜索HARBOR... 品项目 基本信息 圆日志 创建系统级机器人账户 系统管理 创建一个包含系统级权限和覆盖指定项目的 郑 用户管理 JENKINS-PUSH 机器人账户 名称 机器人账户 描述 效期剩余 基本信息 描述 仓库管理 JENKIN推送用 选择系统权限 复制管理 选择项目权限 分布式分发 过期时间 永不过期 标签 项目定额 页面大小 条记录 15 审查服务 清理服务 任务中心 配置管理 取消 浅色主题 -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1785238271161-bcdc4e55-611c-427f-b63d-fd2b233abe0c.png)



<!-- 这是一张图片，ocr 内容为：选择项目权限 创建系统级机器人账户 创建一个包含系统级权限和覆盖指定项目的 覆盖全部项目 机器人账户 基本信息 重置所有项目初始权限 选择全部项目 YT 项目名称 一个?创建时间 权限 选择系统权限 LIBRARY 2026/7/14 01:20 项权限 选择项目权限 UAT 2026/7/14 01:24 70项权限 页面大小 1-2共计2条记录 5 V 上一步 完成 取消 -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1785238514125-886eab19-c06a-4e9e-98b2-77a175ca27b4.png)



jenkins配置

<!-- 这是一张图片，ocr 内容为：UPDATE CREDENTIAL 范围 全局(JENKINS,NODES,ITEMS,ALL CHILD ITEMS,ETC) 用户名 ROBOT$JENKINS-PUSH TREAT USERNAME AS SECRET 密码 已隐藏 修改密码 RES ID HARBOR-CRED ? 描述 JENKINS推送HARBOR使用机器人账号 SAVE -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1785240015721-3499c8e7-16eb-4b4a-8a39-474723ce914f.png)



```groovy
stage('Push Docker Image') {
    when {
        expression { currentBuild.result != 'FAILURE' }
    }
    steps {
        script {
            withCredentials([usernamePassword(
                credentialsId: 'harbor-cred',
                usernameVariable: 'HARBOR_USER',
                passwordVariable: 'HARBOR_PASS'
            )]) {
                sh """
                           echo "${HARBOR_PASS}" | docker login ${HARBOR_REGISTRY} -u '${HARBOR_USER}' --password-stdin
                           docker push ${FULL_IMAGE}
                           docker logout ${HARBOR_REGISTRY}
                       """
            }
        }
    }
}
```


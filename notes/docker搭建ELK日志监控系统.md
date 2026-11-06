⼀个⽇志系统应该包含以下⼏点：  
（1）收集[collect]：能够采集多种来源的⽇志数据  
（2）传输[transform]：能够稳定的把⽇志数据解析过滤并传输到存储系统  
（3）存储[store]：存储⽇志数据  
（4）分析[analyze]：⽀持 UI 分析  
（5）警告[warning]：能够提供错误报告，监控机制   
 

<!-- 这是一张图片，ocr 内容为：ENTERPRISE SITE APPLICATION LOGGING SEARCH SEARCH SEARCH FUTURE SOLUTIONS BUSINESS SECURITY APM METRICS ANALYTICS ANALYTICS KIBANA VISUALIZE ELASTICSEARCH STORE SEARCH &ANALYZE ELASTIC STACK LOGSTASH BEATS INGEST SELF MANAGED SAAS DEPLOYMENT ELASTIC CLOUD ELASTIC CLOUD STANDALONE ENTERPRISE -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1679822250131-44e5d096-8081-4dbb-8ec5-dcda5ae2227d.png)



# ⼀：ELK 
<!-- 这是一张图片，ocr 内容为：NGINX日志 N 收集日志 数据展示分析 解析过滤传送 收集日志 ELASTICSEARCH LOGSTASH KIBANA TOMCAT日志 -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1679822310498-f6734145-0711-49fa-a658-bbd5946bd9d2.png)

<font style="color:#DF2A3F;">注意启动顺序，要先启动elasticsearch 否则先启动其他的会报错 </font>  
 

## 1：elasticsearch介绍 
elasticsearch是⼀个分布式、⾼扩展、⾼实时的搜索与数据分析引擎，作为存储系统是整个ELK架构的  
核⼼。  
⽤于全⽂检索、结构化搜索、分析。 



## 2：logstash介绍 
logstash是开源的数据收集引擎。可以**收集**不同来源的数据，并将数据**解析过滤发送**到输出⽬标。  
logstash提供了⼤量插件，可解析，丰富，转换和缓冲任何类型的数据。  
**管道(pipeline) 是logstash中独⽴运⾏的单元。每个管道都必须要包含输⼊(input)、输出(output)以及可  
****选的过滤器(fileter) **  
 <!-- 这是一张图片，ocr 内容为：FILTERS INPUTS OUTPUTS LOGSTASH PIPELINE ELASTICSEARCH DATA SOURCE -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1679822513199-fb60881f-131b-4f0f-80e6-1bcc1ec833ce.png)

1：inputs 输⼊ 【输⼊来源可以是file、kafka、beats等】  
2：filters 过滤  
3：outputs 输出 【输出⽬标可以是Stdout(控制台)、File、ES等】 

  
**<font style="color:#DF2A3F;"> logstash可以从多个输⼊源获取内容通过type进⾏区分 并可根据type向多数据源输出 </font>**



## 3：kibana介绍 
Kibana是⼀个开源的分析与可视化平台。  
⽤kibana搜索、查看存放在Elasticsearch中的数据。  
Kibana与Elasticsearch的交互⽅式是各种不同的图表、表格、地图等，直观的展示数据，从⽽达到⾼级  
的数据分析与可视化的⽬的。   
 

**<font style="color:#DF2A3F;">部署前先创建新的局域网  
</font>**`docker network create --subnet=172.18.0.0/16 elk_net `  
 防止容器IP频繁改动后需要修改配置文件   
 

```shell
[root@k8s-node2 ~]# docker network create --subnet=172.18.0.0/16 elk_net
0a23c53c967b0a12c2ad95575748bb3b74e08f1a8b5cc0cc7f562e1a94115784
[root@k8s-node2 ~]# docker network ls
NETWORK ID     NAME      DRIVER    SCOPE
f46d890efcdf   bridge    bridge    local
0a23c53c967b   elk_net   bridge    local
469858ee58d0   host      host      local
974cf3bc0400   none      null      local
```

# ⼆：elasticsearch 
## 1：拉取镜像 
`docker pull elasticsearch:7.17.9 `

## 2：修改配置文件 


添加原始挂载配置文件` /usr/share/elasticsearch/config/elasticsearch.yml `

```shell
cluster.name: "docker-cluster"
network.host: 0.0.0.0
```

修改后的`<font style="color:rgb(223,42,63);">/usr/share/elasticsearch/config/elasticsearch.yml</font> `

```shell
cluster.name: "elastic" #es集群名称
network.host: 0.0.0.0
http.cors.enabled: true
http.cors.allow-origin: "*"
xpack.security.enabled: true #开启密码校验，若开启就必须要⾛第4步设置密码
```

**x-pack配置功能**

X-Pack是Elastic Stack的⼀个扩展插件，包含了安全控制、报警、监控、报表和画图功能。XPack能够⽅便地启⽤或禁用

<!-- 这是一张图片，ocr 内容为：ELASTICSEARCH SETTINGS KIBANA SETTINGS LOGSTASH SETTINGS X-PACK FEATURE YES NO NO DEVELOPMENT TOOLS YES GRAPH NO NO YES YES NO MACHINE LEARNING NO MANAGEMENT NO YES MONITORING YES YES YES YES NO REPORTING NO YES NO SECURITY YES AUDITING NO NO YES NO WATCHER NO YES -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1679823280734-7150f0d0-007c-4934-b5e3-f27856ea08af.png)

## 3：启动容器 
创建挂载目录

```shell
mkdir -p /data/elasticsearch/plugins;
mkdir -p /data/elasticsearch/data;
mkdir -p /data/elasticsearch/logs;
mkdir -p /data/elasticsearch/config;
# 做映射之前赋予文件夹相应权限，默认创建的文件夹权限就是755，所 以/dockerfile/elasticsearch/plugins不用改权限
chmod -R 775 /data/elasticsearch/data;
chmod -R 775 /data/elasticsearch/logs;
chmod -R 775 /data/elasticsearch/config;
#若有报错执行
chown -R 1000:1000  /data/elasticsearch/logs
```

```shell
docker run -it --privileged=true -d -p 9200:9200 -p 9300:9300    \
--name es --net elk_net --ip 172.18.0.2 --privileged=true    \
-v /data/elasticsearch/config/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml    \
-v /data/elasticsearch/plugins:/usr/share/elasticsearch/plugins \
-v /data/elasticsearch/data:/usr/share/elasticsearch/data    \
-v /data/elasticsearch/logs:/usr/share/elasticsearch/logs    \
-e ES_JAVA_OPTS="-Xms1024m -Xmx1024m" -e "discovery.type=single-node"    \
elasticsearch:7.17.9
```

<font style="color:#DF2A3F;">Xms Xmx为最小最大堆内存，将其改为我们主机的物理内存的⼀半（50%-70%）即可，要设置成相同  
</font><font style="color:#DF2A3F;">的值，以防止在运行时调整堆的大小</font>

若遇到：WARNING: IPv4 forwarding is disabled. Networking will not work

```shell
echo "net.ipv4.ip_forward = 1">>/etc/sysctl.conf 
```

## 4：设置密码
<!-- 这是一张图片，ocr 内容为：[0.000S]LERROR 10.20.3.109:92 X X 知如何给ELASTICS /BIN/ELASTICSE DOCKER部署EL 历史记录 DOCKER部署EL 10.20.3.109:9200 系统镜像下载 公司 工具箱-程序员编程 运维 PROMETHEUS 登录 HTTP://10.20.3.109:9200 您与此网站的连接不是私密连接 用户名 密码 登录 取消 -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1679827662693-9bd133e0-0e1e-4bec-be48-cccc12f13a23.png)

进入elasticsearch容器中初始化各个组件的密码 

`./bin/elasticsearch-setup-passwords interactive `

```shell
#使用curl localhost:9200 -u elastic:{password}如下方式访问则正常:
sh-5.0# curl localhost:9200 -u elastic:123456    
{
  "name" : "53101abb98a5",
  "cluster_name" : "elastic",
  "cluster_uuid" : "OFugpIv2TYinda_BLpqi-A",
  "version" : {
    "number" : "7.17.9",
    "build_flavor" : "default",
    "build_type" : "docker",
    "build_hash" : "ef48222227ee6b9e70e502f0f0daa52435ee634d",
    "build_date" : "2023-01-31T05:34:43.305517834Z",
    "build_snapshot" : false,
    "lucene_version" : "8.11.1",
    "minimum_wire_compatibility_version" : "6.8.0",
    "minimum_index_compatibility_version" : "6.0.0-beta1"
  },
  "tagline" : "You Know, for Search"
}
# 查看集群健康状态
GET /_cat/health?v
# 查看节点健康状态
GET /_cat/nodes?v
# 查看索引信息
GET /_cat/indices?v
```

## 5：忘记密码重置密码 
### 1：修改配置文件 
修改elasticsearch.yml配置⽂件注释使⽤xpack安全校验配置，取消使⽤密码校验   
 <!-- 这是一张图片，ocr 内容为：NEW O "ELASTIC" CLUSTER.NAME: 1 NETWORK.HOST: 0.0.0.0 2 HTTP.CORS.ENABLED: T 3 TRUE 14 11 4 HTTP.CORS.ALLOW-ORIGIN: 5 #XPACK.SECURITY.ENABLED: TRUE -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1679827753485-f1047261-a865-44a0-b9da-e93c0abd5fd0.png)

### 2：重启容器查看所有索引 
```shell
[root@k8s-node2 config]# docker exec -it  53101abb98a5 /bin/sh                 
sh-5.0# curl -XGET "127.0.0.1:9200/_cat/indices" -H 'Content-Type: application/json'
green open .geoip_databases TTzAdkvuTpuMbIlxAF0Kng 1 0 42 0 40.6mb 40.6mb
green open .security-7      Tfpxal73Tvexzcwk4Yv5_Q 1 0  7 0 25.7kb 25.7kb
```

<!-- 这是一张图片，ocr 内容为：CPOG -XGET "127.0.0.1:9200/_CAT/INDICES" SH-5.0# CONTENT-TYPE: APPLICATION/JSON' CURL H- 420 TTZADKVUTPUMBILXAFOKNG 1 0 GEOIP_DATABASES 40.6MB 40.6MB OPEN GREEN TFPXA173TVEXZCWK4YV5_Q 1 0 .SECURITY-7 70 25.7KB 25.7KB GREEN OPEN SH-5.0# -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1679827983017-917b6be2-4436-4a02-b792-d08c49dcef87.png)  
 

### 3：删除<font style="color:rgb(77,77,77);">security-7索引</font> 
```shell
sh-5.0# curl -XDELETE 127.0.0.1:9200/.security-7
{"acknowledged":true}sh-5.0# 
```

修改配置文件开启密码配置 后 重启，重复添加密码操作   
 

### 4：重设置密码  

# 三：logstash
先执行5配置数据源不然logstash服务启动会有问题

## 1：拉取镜像 
`docker pull logstash:7.17.9`

## 2：修改配置   
 <!-- 这是一张图片，ocr 内容为：LOGSTASH.YML 应用配置文件 输入,过滤,输出 PIPELINE1.CONF 独立运行单元:管道 多管道配置文件 输入,过滤,输出 多管道配置文件 PIPELINE2.CONF PIPELINES.YML 多管道配置文件 输入,过滤,输出 PIPELINE3.CONF -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1679829473184-ed859720-ff1c-448f-b5b7-35e37082eea3.png)  
 
### 1：logstash.yml 
logstash本身的配置⽂件，用于设置控制logstash启动、运行的参数   
原始 `<font style="color:#DF2A3F;">/config/logstash.yml </font>`

```shell
http.host: "0.0.0.0"
xpack.monitoring.elasticsearch.hosts: [ "http://elasticsearch:9200" ]
```

修改为：

```shell
node.name: "logstash001" #节点名称
http.host: "0.0.0.0"
xpack.monitoring.enabled: false #设置禁⽤X-Pack监视功能
```

### 2：pipelines.yml 
用于指定在⼀个logstash中运行多个管道的配置文件   
原始`<font style="color:#DF2A3F;">usr/share/logstash/config/pipelines.yml </font>`

```shell
# This file is where you define your pipelines. You can define multiple.
# For more information on multiple pipelines, see the documentation:
# https://www.elastic.co/guide/en/logstash/current/multiple-pipelines.htm
l
# 可以在这个配置⽂件中定义多个管道，⽤于从多个数据源中获取信息
- pipeline.id: main #管道id
path.config: "/usr/share/logstash/pipeline/"
```

**<font style="color:#DF2A3F;">在启动logstash时他会自动加载 pipelines.yml 中指定的path.config下的所有的管道配置文件conf  
</font>****<font style="color:#DF2A3F;">合并成⼀个整体的配置文件 </font>**

**<font style="color:#DF2A3F;">将管道的具体的配置文件放置在config下，方便容器统⼀的挂载   
</font>**修改后的`<font style="color:#DF2A3F;"> /usr/share/logstash/config/pipelines.yml</font>` 

```shell
# This file is where you define your pipelines. You can define multiple.
# For more information on multiple pipelines, see the documentation:
# https://www.elastic.co/guide/en/logstash/current/multiple-pipelines.html
# 可以在这个配置⽂件中定义多个管道，⽤于从多个数据源中获取信息
- pipeline.id: pipeline001 #管道id
  path.config: "/usr/share/logstash/config/*.conf"
```

### 3：pipeline管道配置 
原先的`/usr/share/logstash/pipeline/logstash.yml `

```yaml
input {
     beats {
       port => 5044
       }
}
output {
     stdout { #并打印到标准输出
       codec => rubydebug #编解码器使⽤rubydebug
      }
}
```

修改后`<font style="color:#DF2A3F;">/usr/share/logstash/config/pipeline001.conf </font>`

```yaml
#获取/usr/share/logs/*下的⽂件输出到es中
input {
    file{
        path => ['/usr/share/logs/*']
        #codec => json
        type => "nginx-log"
    }
}
filter {
    #json{
        # 将message作为解析json的字段
        #source => "message"
    #}
}

output {
    if[type] == "nginx-log"{
     elasticsearch {
       hosts => [ "10.20.3.109:9200" ]
       index => "nginx-log-%{+YYYY-MM-dd}"
       user => "elastic"
       password => "123456"
     }
  }
}
```

### 3：启动logstash容器 
```yaml
docker run -d -it --privileged=true --name=lh --net elk_net --ip 172.18.0.3    \
-p 5047:5047 -p 9600:9600 -v /data/logstash/config/:/usr/share/logstash/config    \
-v /data/nginx/logs/:/usr/share/logs/    \
logstash:7.17.9
```



# 四：kibana 
## 1：拉取镜像
`docker pull kibana:7.17.9 `

## 2：修改配置文件 
未修改的kibana.yml  

```yaml
#
# ** THIS IS AN AUTO-GENERATED FILE **
#
# Default Kibana configuration for docker target
server.host: "0.0.0.0"
server.shutdownTimeout: "5s"
elasticsearch.hosts: [ "http://elasticsearch:9200" ]
```

修改后

```yaml
server.name: kibana
server.host: "0.0.0.0"
xpack.monitoring.ui.container.elasticsearch.enabled: true
elasticsearch.hosts: [ "http://10.20.3.109:9200" ]
elasticsearch.username: "elastic"
elasticsearch.password: "123456"
elasticsearch.requestTimeout: 50000
i18n.locale: "zh-CN" #中⽂ui界⾯
server.publicBaseUrl: "http://10.20.3.109:5601"
```

## 3：启动kibana容器 
```yaml
mkdir -p /data/kibana/config
docker run -d --privileged=true --name kb -p 5601:5601 --net elk_net --ip 172.18.0.4  \
-v /data/kibana/config/kibana.yml:/usr/share/kibana/config/kibana.yml  \
kibana:7.17.9
```



<!-- 这是一张图片，ocr 内容为：IOS手机端网页测试 GIT 克隆别人代码提... 公司 JAVAWEB教程目录... PYTHON教程-康雪峰 工具箱-程序员编程... BUTTERFLY 运维 PROMETHEUS 系统镜像下载 LUCKYYE-自闭~. 搜索 ELASTIC ELASTIC 三款 主页 通过添加集成开始使用 要开始使用您的数据,请使用我们众多采集选项中的一个选项.从应用或服务收集 数据,或上传文件.如果未准备好使用自己的数据,请添加示例数据集. 添加集成 试用样例数据 UPLOAD A FILE 管理 开发工具 STACK MANAGEMENT 管理索引生命周期 管理权限 目日 监测堆栈 备份和还原 定义生命周期策略,以随着索引老 将快照保存到备份存储库,然后还 控制访问者及其可以执行的任务. 跟踪部署的实时运行状况和性能. 化自动执行操作. 原以恢复索引和集群状态. -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1679834126015-be269a49-b3eb-45aa-a788-83043233b0ee.png)



<!-- 这是一张图片，ocr 内容为：个TQ 巴士身口二 不安全|10.20.3.109:5601/APP/MANAGEMENT/DATA/INDEX_MANAGEMENT/INDICES 更新 R JOS手机端网页测试 系统流像下我 工具箱-程序员编程... GIT 克隆别人代码提... JAVAWEB教程目录 PYTHON教提-度雪峰 运维 公司 LUCKYYE-自闭 BUTTERFLY PROMETHEUS ELASTIC 搜索ELASTIC 索引管理 STACK MANAGEMENT 索引管理 管理 索引管理文档 采集 索引 索引模板 数据流 组件模板 采集管道 分别或批量更新您的ELASTICSEARCH索引.了解详情. 数据 包括隐藏的索引 包括汇总索引 索引管理 重载索引 索引生命周期策略 搜索 拍取快照并还原 状态 文档计数 副本分片 名称 运行状况 主分片 数据流 存储大小 汇总/打包作业 转换 6 NGINX-LOG-2023-03-26 18.5KB YELLOW OPEN 远程集群 每页行数:10 告警和洞见 -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1679839731638-ffa7f338-32f3-46fa-941e-402bfb32a187.png)

<!-- 这是一张图片，ocr 内容为：搜索ELASTIC ELASTIC 索引模式 STACK MANAGEMENT 索引楼 告警和洞见 规则和连接器 REPORTING 创建和管理 MACHINE LEARNING 作业 您在ELASTICSEARCH中有数据. 安全 现在,创建索引模式. SEARCI 用户 KIBANA需要索引模式来识别您要浏览的数据链,索引和索引别 角色 PATTERN 个 名.索引模式可以指向特定索引(例如昨天的日志数据),或 API密钥 包食日志数据的所有索引. KIBANA 创建索引模式 索引模式 已保存对象 标签 希望了解详情? 搜索会话 阅读文档区 工作区 高级设置 STACK R 许可管理 升级助手 羊闲 -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1679840205662-a94e9f8d-e876-4143-ba7f-0e6bdc18e206.png)

<!-- 这是一张图片，ocr 内容为：10 2031035501/APP/MANAGSMENT/IBANAFINDEXPATTEMS/PATTERNS/8E1856CO-CBEO-LLED-1LED-FB160073D88D+/7 A三(N 不安全 公司 运维 工具箱-程序员编程... 系统镜像下载 LUCKY YE-自闭 BUTTERFLY GIT克隆别人代码提... PYTHON教程-廖雪峰 PROMETHEUS ELASTIC 搜索ELASTIC 索引模式 默 STACK MANAGEMENT NGINX* HOME NGINX* ANALYTICS 时间字段:"@TIMESTAMP" OVERVIEW 点击DISCOVER音看和编辑NGINX*中的宇段,字段属性,如类型和可提索性,基于EARCH 中的宇段映射心. DISCOVER DASHBOARD 脚本字段(0)  字段筛选(0) 字段(16) CANVAS 搜索 MAPS MACHINELEARNING 可搜索 格式 名称 类型 VISUALIZE LIBRARY @TIMESTAMP DATE ENTERPRISE SEARCH @VERSION TEXT 概监 -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1679840290351-b91736ae-8faf-4454-ab49-03b2a97030da.png)

<!-- 这是一张图片，ocr 内容为：ELASTIC 搜索ELASTIC 同保存 选项新建打开共享检查 DISCOVER 搜索 刷新 显示日期 过去15分钟 KQL +添加筛选 6个命中 NGINX* 图表选项 品 6543210 搜索字段名称 按类型筛选 10 可用字段 22:12:00 22:09:00 22:11:00 22:08:00 22:13:00 22:10:00 22:1400 22:05:00 22:17:00 22:15:00 22:07:00 22:04:00 22:16:00 22:06:00 MAR 26,2023 @ 22:07721-MAR 26,26,2023 @ 22:18:07721 ID INDEX 文档 TIME  SCORE STIMESTAMP: NAR 26, 2823 0 22:95:42.292      1 LERROR] MAR 26, 2023 @ 22:05:42.292 -TYPE 29829:*3 DIRECTORY INDEX OF  172, 16.5, SERVER; LOCAL/" IS FORBLDEN, ELIENT; 16.5,  SERVER; LOCALHOST RTIMESTAMP REQUEST:"GET / HTTP/1.1",HOST:"10.20.3,109"  PATH://USR/SHARE/LOGS/ERROR.10G TYPE:/ NGINX-LOG -ID: RZEGHOCBVAR6QUZ4PDJ- -INDEX:NGINX-LOG-2023-03-26 -SCORE: - - - -TYPE: -DOC VERSION HOST MAR 26, 2023 @ 22:05:42.289 MESSAGE 26T14:05:41+00:00","HOST":172.18.0.5","SERVICE":"NGINXTEST","TRACE":"- PATH ",LOG":"LOG","CLIENTIP":"172.16.16.5","REMOTE_USER":"-",","REQUEST":"GET / HTTP/1."HTTP.USER-AGER,AGENT';"HOZILLA/5,) (MINDOWS NT 10.J; WING4; X64) APPLENKIT/S37,36 (KHTHL, DEC TYPE CHRONG/96:0,4664.93 SAFARL/937,30"," "UDETREAMMOST';"RESOONSEEIING":'UPETREAMTINE':""","UDETREAMMOST' -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1679840308005-caefc435-eb59-4730-81b0-22068d6b6e03.png)

# 五、日志来源
**启动nginx**

```shell
mkdir -p /data/nginx/html
mkdir -p /data/nginx/conf
mkdir -p /data/nginx/logs

docker run -d -p 80:80 --privileged=true  \
-v /data/nginx/html:/usr/share/nginx/html   \
-v  /data/nginx/conf/default.conf:/etc/nginx/conf.d/default.conf  \
-v  /data/nginx/conf/nginx.conf:/etc/nginx/nginx.conf  \
-v  /data/nginx/logs:/var/log/nginx --net elk_net --ip 172.18.0.5  \
--name nginx nginx
```

default.conf

```shell
server {
listen 80;
listen [::]:80;
server_name localhost;
#access_log /var/log/nginx/host.access.log main;
location / {
root /usr/share/nginx/html;
index index.html index.htm;
}
error_page 500 502 503 504 /50x.html;
location = /50x.html {
root /usr/share/nginx/html;
}
}
```

nginx.conf

```shell

user  nginx;
worker_processes  auto;

error_log  /var/log/nginx/error.log notice;
pid        /var/run/nginx.pid;


events {
    worker_connections  1024;
}


http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    #log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
    #                  '$status $body_bytes_sent "$http_referer" '
    #                  '"$http_user_agent" "$http_x_forwarded_for"';
    log_format json '{"@timestamp":"$time_iso8601",'
                '"host":"$server_addr",'
                '"service":"nginxTest",'
                '"trace":"$upstream_http_ctx_transaction_id",'
                '"log":"log",'
                '"clientip":"$remote_addr",'
                '"remote_user":"$remote_user",'
                '"request":"$request",'
                '"http_user_agent":"$http_user_agent",'
                '"size":$body_bytes_sent,'
                '"responsetime":$request_time,'
                '"upstreamtime":"$upstream_response_time",'
                '"upstreamhost":"$upstream_addr",'
                '"http_host":"$host",'
                '"url":"$uri",'
                '"domain":"$host",'
                '"xff":"$http_x_forwarded_for",'
                '"referer":"$http_referer",'
                '"status":"$status"}';
 
    access_log  /var/log/nginx/access.log  json;

    sendfile        on;
    #tcp_nopush     on;

    keepalive_timeout  65;

    #gzip  on;

    include /etc/nginx/conf.d/*.conf;
}
```

# 六:ELFK之FileBeat
## 1：FileBeat介绍
<!-- 这是一张图片，ocr 内容为：BEATS ATS的套件是针对不同的数据源. WINLOGBEAT FILEBEAT PACKETBEAT ANALYZE NETWORK PACKET DATA. REAL-TIME INSIGHT INTO LOG DATA. ANALYZE WINDOWS EVENT LOGS. DOWNLOAD DOWNLOAD DOWNLOAD METRICBEAT AUDITBEAT HEARTBEAT SHIP AND ANALYZE METRICS. SEND AUDIT DATA TO ELASTICSEARCH. PING YOUR INFRASTRUCTURE. DOWNLOAD DOWNLOAD DOWNLOAD FUNCTIONBEAT JOURNALBEAT SHIP CLOUD DATA WITH SERVERLESS INFRASTRUCTURE. ANALYZE JOURNALD LOGS. -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1679842145240-a879d8f0-fef9-4efb-8f26-8ae47750b56b.png)



```yaml
filebeat.inputs:
paths:
- /usr/share/filebeat/logs/*.log # 每⼀个“-”代表⼀个⽇志位置
```



对于filebeat定位到的每⼀个日志，filebeat都会启动⼀个Harvester(收割机),每个Harvester 获取新内容并

将新数据发送到libbeat，libbeat 进行聚合操作并将聚合数据发送到filebeat配置的输出中

**<font style="color:#DF2A3F;">inputs：输入负责管理收割机并查找所有要读取的数据源</font>**

<!-- 这是一张图片，ocr 内容为：L_ INPUT 1: SPOOLER /VAR/LOG/*.LOG ELASTICSEARCH HARVESTER SYSTEM.LOG LOGSTASH HARVESTER WIFI.LOG KAFKA INPUT  2: /VAR/LOG/APACHE2/* 白月日期限公司 REDIS ERROR.LOG 1IIIII FILEBEAT -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1679842548193-452f0423-59e2-4cf2-80cf-37ba1215a73a.png)

## 2：FileBeat与Logstash的比较
 filebeat优点：是⼀个轻量的文件采集器，占用资源极少。而ogstash占用资源较大，若兼具收集和分析  
的作用，将会占据更大的服务器资源。因此当存在多个应用服务器时，logstash就不能在每个应用服务  
器中部署进行日志收集的工作了。所以采用filebeat来代替logstash的收集工作。  
filebeat缺点：logstash相比于filebeat，前者可以同时配置多个输出源，但是后者只能配置⼀个输出源，  
因此filebeat的数据共享性较差，当然如果在架构中添加上消息队列，也可以解决此问题。  

**修改上面的elk日志处理模式新增filebeat：**

> **10.20.3.109 ：elastic+filebeat+logstash+kibaba nginx**
>
> **10.20.3.108:  filebeat   nginx**
>

<!-- 这是一张图片，ocr 内容为：FILEBEAT 数据源1 采集 过滤 KIBANA ELASTICSEARCH LOGSTASH 可视化 存储 过滤 采集一 FILEBEAT 数据源2 -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1679842919962-de10f52a-95b4-43a4-b6cc-9a4e628556ca.png)

## 3：FileBeat部署 
<font style="color:#DF2A3F;">在ELK架构基础上进行组件的添加 </font>

### 3.1 拉取镜像
```yaml
docker pull docker.elastic.co/beats/filebeat:7.17.9
```

### 3.2 filebeat配置文件


```yaml
filebeat.inputs:
- type: filestream #⾃7.16开始log类型被废弃使⽤filestream代替
  id: my-filestream-id #当type为filestream时，id必须要指派
  enabled: true
  paths:
    - /usr/share/filebeat/logs/*.log #⽇志的位置
output.logstash: #输出到logstash中
   hosts: ["10.20.3.109:5044"] #logstash的5044为beats监听端⼝
```

<font style="color:#DF2A3F;">注意：指定配置文件挂载的到宿主机中的文件夹权限 chmod -R 755 </font>

### 3.3 logstash管道配置文件
<font style="color:#DF2A3F;">pipeline001.conf 需要更改管道配置文件用于配置logstash中的管道的数据来源 </font>  
  

```yaml
#获取filebeat传输过来的⽂件输出到es中
input {
  beats {
    port => 5044 # 指定接收filebeat的端⼝
    client_inactivity_timeout => 36000 # 客户端响应超时时间
    type => "nginx-log" #与output中对应
  }
}

filter {
    #json{
        # 将message作为解析json的字段
     #   source => "message"
    #}
    mutate {
    remove_field => [ "host" ]
  }
}

output {
    if[type] == "nginx-log"{
     elasticsearch {
       hosts => [ "10.20.3.109:9200" ]
       index => "filebeat-nginx-log-%{+YYYY-MM-dd}"
       user => "elastic"
       password => "123456"
     }
  }
 stdout {
        codec => rubydebug
       }
}
```



### 3.5 容器启动
**启动filebeat **

```bash
mkdir -p /data/filebeat/config
docker run -d --privileged  \
-v /data/filebeat/config/filebeat.yml:/usr/share/filebeat/filebeat.yml  \
-v /data/nginx/logs/:/usr/share/filebeat/logs  \
--name filebeat  docker.elastic.co/beats/filebeat:7.17.9
```

**启动logstash**

```bash
docker run -d -it --privileged=true --name=logstash --net elk_net --ip 172.18.0.3    \
-p 5044:5044 -p 5047:5047 -p 9600:9600 -v /data/logstash/config/:/usr/share/logstash/config    \
-v /data/nginx/logs/:/usr/share/logs/    \
logstash:7.17.9
```



<!-- 这是一张图片，ocr 内容为：:更新 RID R 运维 工具箱程序员编程... OLUCKYYE自闭 GIT 克隆别人代码提.... 系统镜像下载 IOS手机端网页测试 JAVAWEB教程目录... PYTHON教程_廖雪峰 BUTTERFLY 公司 PROMETHEUS ELASTIC 搜索ELASTIC 打开 共享 检查 保存 新建 选项 DISCOVER 搜索 首 MAR 27,2023@11:10:00.00 KQL 刷新 添加筛选 FILEBEAT-NGINX-LOG-2023-03... 3个命中 图表选项 2 搜索字段名称 1.5 1 按类型筛选 0 0.5 可用字段 19 11:10:25 11:10:20 11:10:10 11:10:00 11:10:05 TID MAR 27,2023@ 11:10:00.000- MAR 27,2023 @ 11:10:30.000 _INDEX MAR  27.2023   11:12号 AME:0B52C81E097E AGENT.HOSTNAME: GBS2EALE997E AGENT.ID:   GBAB4125-9665-4CZE-B3F3-OZAB600ZA66002A  AGENT-NAME: 06529 .TYPE YPE:FILESTREAM AGENT.TYPE:FILEBEAT AGENT.VERSION:7.17.9 ECS.VERSION:1.12.G INPUT.TYPE: FIL 值 @TIMESTAMP 109:FILE.PATH;/ /UAR/SHARE/FLLEBEOT/LOGS/ERFOR)  209 109:0FFSET:   MESSA9E;  203/27  3:10:96  [ERROR @VERSION 445 OPEN() "(USR/SHARE/NGINXTHTML/FAVJOON.LOO" FAILED (2: NO SUCH FILE OF DLRECTORY), OLLENT; 18.4:1' AQENT.EPHEMERAL_ID 查看周围文档查看单个文档 已展开文档 表 AGENT.ID JSON -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1679886797006-68097cde-525d-4721-826f-6ec0d302e4d0.png)



<!-- 这是一张图片，ocr 内容为：ET TEXT ON A START_OBJECT 1:9"7777 1E097E"?, "QTIMESTAMP"->2023-03-26T16:45: .                                          ECS '"ECS'-ECS'->ECS>{ \"2023-03-26T16:41:41+00 {"VERSION">"1.12.0" "TYPE"FILESTREAM"了,"ME! :00\'/'HOST)"1''172.18.0.5 ,\"REMOTE_USER\":\"-\",\" \"SERVICE\":\"NGINXTEST\"TRACE\"TRACE\"-\"LOG\"LOG\ \"LOG\",\"CLIENTIP\":\"172.16.16.5\ REQUEST\":\"GET / HTTP/1.1\", \HTTP_USER_AGENT\":\"MOZILLA/5.0 (WINDOWS NT 1 WIN64; X64) APPLEWEBKIT/537.36 (KHTML LIKE GECKO) CHROME/96 NT 10. "HTTP_HOST\":\"10.20.3.109\",\"UR .0.4664.93 SAFARI/537.36\ /""/"UPSTREAMHOST\":\":/"-/" THTHSTE:20.3.10PONSETING\0.COO. L"SIZEL": \"UPSTREAMTIME\ :\"/INDEX.HTM7\",\"DOMAIN\" "TAGS">["BEATS_INPUT_CODEC_PLAIN_APPLIE -)",/"STATUS(":|"304\"3". "REFERERL""""""" , "AGENT"三>{"NAME"->"OB52C81E097E", O,"FILE"-{"PATH"二>"/USR/SHARE/FILEBEAT/LOGS/ACCESS.LOG"了 LOG">{"OFFSET">4900, D"], HOSTNAME""0B52C81 "EPHEMERAL_ID"->"C3A2144C-8FDO-4258-9BDB-93A218927A93 "OOAB4125-9B65-4C2E-B3F3-02AB60D20EA4" E097E "7.17.9","TYPE">"F ID''00AB VERSION'' ILEBEAT"了, "TYPE">"NGINX-LOG"了], :RESPONSE->{"INDEX">>{"_INDEX" >"2PHOHOCBVQR604Z4H FILEBEAT -NG1NX-10G-2023-03-26","_TYPE"->"_DOC" PL_. "STATUS">400,"ERROR"S>{"TYP ON"."REASON "FAILED TO PARSE FIELD THOST] OF TYPE {"TYPE"->"MAPPER_PARSING_EXCEPTION", TEXT IN DOCUMENT WITH ID TNA '2PHOHOCBVOR6Q4Z4HTNA' PREVIEW OF FIELD'S VALUE:'{NAME-0B52C81E097E}'", REASON'>> CAN'T UO11DAZYA_AIPIS-LPBALL <- ADKI 1<- HA NASNP) GET TEXT ON A START_OBJECT AT 1:9"JJJJ] ZV [5]  DOCKER LOGS -F 3B7C3178358B STOPPED -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1679849590161-543bbbe3-c38c-4640-aeb5-cd21d76639f8.png)

```bash
filter {
  mutate {
    remove_field => [ "host" ]
  }
}
```


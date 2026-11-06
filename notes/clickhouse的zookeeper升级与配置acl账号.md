# 1、 zookeeper升级：
zookeeper下载地址： **https://dlcdn.apache.org/zookeeper/  **

```plain
#解压和mv
tar -zxvf apache-zookeeper-3.7.2-bin.tar.gz &&mv apache-zookeeper-3.7.2-bin  zookeeper-3.7.2 &&mv zookeeper-3.7.2 /home/clickhouse
#拷贝配置文件
cd /home/clickhouse/zookeeper-3.4.14/conf &&cp  zoo.cfg   ../../zookeeper-3.7.2/conf/

#停止原先的zoo进程
/home/clickhouse/zookeeper-3.4.14/bin/zkServer.sh stop
#拷贝数据目录
cp -r  /home/clickhouse/zookeeper-3.4.14/data    /home/clickhouse/zookeeper-3.7.2/data
cp -r  /home/clickhouse/zookeeper-3.4.14/dataLog /home/clickhouse/zookeeper-3.7.2/dataLog
#修改权限
chown -R clickhouse:clickhouse  /home/clickhouse/zookeeper-3.7.2
chmod 755  /home/clickhouse/zookeeper-3.7.2/data*
#启动zookeeper
/home/clickhouse/zookeeper-3.7.2/bin/zkServer.sh start
```

# 2、配置系统启动脚本
## 2.1、编写启动脚本
```plain
cd /etc/init.d
vim zookeeper
```

zookeeper启动脚本

```plain
#!bin/bash
#chkconfig:2345 54 26
#processname:zookeeper
#description:zk server
prog=/home/clickhouse/zookeeper-3.7.2/bin/zkServer.sh
start(){                                
        $prog start 
        echo "zookeeper启动"
}
stop(){                                
        $prog stop 
        echo "zookeeper关闭"
}
status(){
        $prog status
}
restart(){              
        stop
        start
}
case "$1" in        
"start")
        start      
        ;;
"stop")            
        stop
        ;;
"status")
        status
        ;;
"restart")            
        restart
        ;;
*)      
        echo "支持指令：$0 start|stop|restart|status"
        ;;
esac

```

## 2.2、赋权
```plain
chmod +x /etc/init.d/zookeeper
```

## 2.3、添加开机自启
```plain
chkconfig --add zookeeper
```

## 2.4、状态设置为启动
```plain
chkconfig zookeeper on
chkconfig --list
```



# 3、zookeeper添加acl账号权限
## 3.1、背景
<font style="color:rgb(64, 64, 64);">由于生产环境使用clickhouse集群依赖的zookeeper集群并未设置访问权限控制,所以被安全部门通报漏洞</font>

<!-- 这是一张图片，ocr 内容为：AI APACHE ZOOKEPER安全满河(CVE-2023-44981) AEARHEZODEREPOR是发展可能保(4PACHO)基金会约一个软件项目,它能备为大型分布系统于通过的有效观要驾.同步预系和金省连管要项目. 详细描述 APACH:ZOOKSEPS12前,3.3.832前,3.72之前版本存在安金据何,该后何识于如果在 厂商补丁: 解决办法 园 目前厂商已发布升级补丁以修复局河,补丁获取链接 HTTPS//LISTS APACHE.ORG /THREAD/WFOYRKB4DG1942Z1074KD8NYCGBPGM5B 威胁分伯 9.1 晋 危险报件 包 发现日期 CVE-2023-44981 素A CVE编号 CNNVD-202310-856 CNNVD编号 茶 CNCVE编号 CNCVE-202344981 ZOOKEEPER来规权访问[原理扫描] 详细描述 ZOOKAEPGR的目标就是对统好复杂总出错的关键服务,将低单局周的投口和生阴兴效,功能是进的系统提供会展户. 在温常悟品下.200LSER允许来经授权的访问. 为ZOOKESPER国程应打方向文号.注意,本酒样检到/节系列SD议层,国比高要而目/有而时仅限,才可眼新免本面件相出标为. 解决办法 方式一: 1) 增加一个认还用户 ADDAUTH DIGEST 用户名:富玛明文 EG. ADDAUTH DIGEST USERLAPSWORD1 2) 设置权限 SETADL/PATH AUTH 用户名:识明文:权限 -->
![](https://cdn.nlark.com/yuque/0/2024/png/34997268/1722924760598-8f1060c6-5193-47ad-b471-182df82b1dc0.png)



## 3.2、zookeeper配置
### <font style="color:rgb(64, 64, 64);">3.2.1 、zookeeper身份的认证有4种方式：</font>


<font style="color:rgb(64, 64, 64);"></font>

| 方案 | 描述 |
| --- | --- |
| world | 只有一个用户：anyone，代表登录zookeeper的所有人（默认） |
| ip | 对客户端使用ip地址认证 |
| <font style="color:rgb(64, 64, 64);">auth</font> | <font style="color:rgb(64, 64, 64);">代表已经认证通过的用户(cli中可以通过addauth digest user:pwd 来添加当前上下文中的授权用户) </font> |
| <font style="color:rgb(64, 64, 64);">digest</font> | <font style="color:rgb(64, 64, 64);">即用户名:密码这种方式认证，这也是业务系统中最常用的 </font> |


### <font style="color:rgb(51, 51, 51);">3.2.2 、ZK的节点有5种操作权限：</font>
<font style="color:rgb(51, 51, 51);">CREATE、READ、WRITE、DELETE、ADMIN 也就是 增、删、改、查、管理权限，这5种权限简写为crwda(即：每个单词的首字符缩写)</font>

<font style="color:rgb(51, 51, 51);">注：这5种权限中，delete是指对子节点的删除权限，其它4种权限指对自身节点的操作权限</font>

| 权限 | ACL简写 | 描述 |
| --- | --- | --- |
| create | c | 可以创建子节点 |
| delete | d | 可以删除子节点（仅下一级节点） |
| read | r | 可以读取节点数据显示子节点列表 |
| write | w | 可以设置节点数据 |
| admin | a | 可以设置节点访问控制列表权限 |


<font style="color:rgb(64, 64, 64);">为zookeeper 增加一个认证用户：</font><font style="color:rgb(77, 77, 77);">ZooKeeper没有传统意义上的“账号”概念，但可以使用</font>`<font style="color:rgb(199, 37, 78);background-color:rgb(249, 242, 244);">digest</font>`<font style="color:rgb(77, 77, 77);">认证方式来模拟账号密码的效果</font>

### <font style="color:rgb(77, 77, 77);">3.2.3、zk授权的相关命令</font>
<font style="color:rgb(77, 77, 77);"></font>

| 命令 | 使用方式 | 描述 |
| --- | --- | --- |
| getAcl |  getAcl [-s] path | 读取ACL权限 |
| setAcl | setAcl [-s] [-v version] [-R] path acl | 设置ACL权限 |
| addauth |  addauth schema auth |  添加认证用户 |


方式一：  
<font style="color:rgb(64, 64, 64);">格式如下: addauth digest 用户名:密码明文</font>

```plain
addauth digest clickhouse:eversec123098
setAcl /  auth:clickhouse:eversec123098:crwda
3）查看Acl设置
getAcl /path
```

方式二：

密文加密方式【<font style="color:rgb(77, 77, 77);">用ZooKeeper自带的</font>`<font style="color:rgb(199, 37, 78);background-color:rgb(249, 242, 244);">DigestAuthenticationProvider</font>`<font style="color:rgb(77, 77, 77);">工具来生成这个摘要字符串】:</font>

```plain
[root@clickhouse-02 lib]# java -cp zookeeper-3.7.2.jar:log4j-1.2.17.jar:slf4j-reload4j-1.7.35.jar:slf4j-api-1.7.35.jar:conf org.apache.zookeeper.server.auth.DigestAuthenticationProvider clickhouse:eversec123098
log4j:WARN No appenders could be found for logger (org.apache.zookeeper.server.auth.DigestAuthenticationProvider).
log4j:WARN Please initialize the log4j system properly.
log4j:WARN See http://logging.apache.org/log4j/1.2/faq.html#noconfig for more info.
clickhouse:eversec123098->clickhouse:tt6A3H7+sjjOILlLMvi9Zbv7+ZE=
```



```plain
echo -n clickhouse:eversec123098 | openssl dgst -binary -sha1 | openssl base64
```

加密方式添加账号：

```plain
addauth digest clickhouse:tt6A3H7+sjjOILlLMvi9Zbv7+ZE=
setAcl /  digest:clickhouse:tt6A3H7+sjjOILlLMvi9Zbv7+ZE=:crwda
```

# 4、clickhouse配置文件调整
<font style="color:rgb(64, 64, 64);">在metrika.xml中配置zk的用户密码(</font>**<font style="color:rgb(64, 64, 64);">注意这里密码需要配置成明文</font>**<font style="color:rgb(64, 64, 64);">）</font>

<font style="color:rgb(64, 64, 64);">以下2种配置方法都行</font>

```shell
    <!-- ZK配置信息 -->
    <zookeeper-servers>
        <node index="1">
            <host>zookeeper-01</host>
            <port>2181</port>
        </node>
        <node index="2">
            <host>zookeeper-02</host>
            <port>2181</port>
        </node>
        <node index="3">
            <host>zookeeper-03</host>
            <port>2181</port>
        </node>
        <identity>clickhouse:eversec123098</identity>
    </zookeeper-servers>
```

<font style="color:rgb(64, 64, 64);"></font>

```plain
    <!-- ZK -->
    <zookeeper-servers>
        <!--根据实际替换-->
        <node index="1">
            <host>zookeeper-01</host>
            <port>2181</port>
        </node>
        <node index="2">
            <host>zookeeper-02</host>
            <port>2181</port>
        </node>
        <node index="3">
            <host>zookeeper-03</host>
            <port>2181</port>
        </node>
        <session_timeout_ms>30000</session_timeout_ms>
        <operation_timeout_ms>10000</operation_timeout_ms>
        <digest>
            <user>clickhouse</user>
            <password>eversec123098</password>
        </digest>
       
    </zookeeper-servers>
```

:::info
这里需要注意的是zk的路径权限不会继承,也就是说你对于/clickhouse设置的权限 对于/clickhouse/xx 是不生效的 但是如果ck里配置了zk的用户及密码 那么由ck创建出的zk路径是带有权限的。

:::

# 5、添加账号后如何操作ck路径
添加账号后直接登录执行ls 会提示权限拒绝。再执行`addauth digest clickhouse:myPassword `即可操作带有权限的路径

<!-- 这是一张图片，ocr 内容为：WELCOME TO ZOOKEEPER! [MAIN-SENDTHREAD(LOCALHOST:2181):CLIENTCNXNSSENDTHREAD@1177] OPENING SOCKET CONNECTION TO SERVER LOCALHO 2024-08-06 INFO [MYID:LOCALHOST:2181] 15:03:26,617 SASL CONFIG STATUS:WILL NOT ATTEMPT TO AUTI 2024-08-06 15:03:26,617 INFO [MAIN-SENDTHREAD(LOCALHOST:2181):CLIENTCNXNSSENDTHREADAI179) [MYID:LOCALHOST:2181] [MAIN-SENDTHREAD(LOCALHOST:2181):CLIENTCNXNSSENDTHREADQ1011] 2024-08-06 15:03:26,622 [MYID:LOCALHOST:2181] INFO SOCKET CONNECTION ESTABLISHED, INITIATING S SERVER:LOCALHOST/0:0:0:0:0:0:0:1:2181 JLINE SUPPORT IS ENABLED [NAIN-SENGTHREADCTOCATHOST;ZZB1V:CTIENTCNXNSSENDTHRE3DETHRE3DETE ON ESSION ESTABLISHMENT CON SERVER 1 2024-08-06 15:03:26,630 [MYID:LOCALHOST:2181] - INFO - OX200B45B555A0012, NEGOTIATED TIMEOUT - 3000 WATCHER:: WATCHEDEVENT STATE:SYNCCONNECTED TYPE:NONE PATH:NULL [ZK:LOCALHOST:2181(CONNECTED) 0] 1S / INSUFFICIENT PERMISSION : / ADDAUTH DIGEST CLICKHOUSE:EVERSEC123098 [ZK:LOCALHOST:2181(CONNECTED) LS/ [ZK:LOCALHOST:2181(CONNECTED) [CLICKHOUSE,ZOOKEEPER] [ZK: LOCALHOST:2181(CONNECTED) 3] -->
![](https://cdn.nlark.com/yuque/0/2024/png/34997268/1722927909215-322879d6-a1d9-4b8f-92c3-a07853882bbd.png)

# 6、zk的acl权限设置错误问题解决
背景：由于个人设置目录的时候把setAcl /  digest:clickhouse:eversec123098:crwda auto写成了digest

一开始配置文件设置skipAcl=yes 可以恢复成无acl模式但是还是不能修改目录权限。

配置ACL超级管理员

zookeeper的权限管理模式有一种叫做super，该模式提供一个超管可以方便的访问任何权限的节点。例如在忘记密码时，可以通过超管来对节点进行操作

假设这个超管是： super:admin，需要先为超管生成密码的密文

```shell
[root@d477dbe7959e ~]# echo -n super:admin |openssl dgst -binary -sha1 |openssl base64
xQJmxLMiHGwaqBvst5y6rkB6HQs=
```

找到zookeeper目录下的 bin/zkServer.sh服务器脚本文件，找到如下一行：

```shell
root@667afe193621:/apache-zookeeper-3.7.0-bin/bin# cat zkServer.sh | grep -nA3 nohup
164:    nohup "$JAVA" $ZOO_DATADIR_AUTOCREATE "-Dzookeeper.log.dir=${ZOO_LOG_DIR}" \
165-    "-Dzookeeper.log.file=${ZOO_LOG_FILE}" "-Dzookeeper.root.logger=${ZOO_LOG4J_PROP}" \
166-    -XX:+HeapDumpOnOutOfMemoryError -XX:OnOutOfMemoryError='kill -9 %p' \
167-    -cp "$CLASSPATH" $JVMFLAGS $ZOOMAIN "$ZOOCFG" > "$_ZOO_DAEMON_OUT" 2>&1 < /dev/null &
```

这就是脚本中启动zookeeper的命令，默认只有以上两个配置项，我们需要加一个超管的配置项"-`Dzookeeper.DigestAuthenticationProvider.superDigest=super:xQJmxLMiHGwaqBvst5y6rkB6HQs=" \`

```shell
root@667afe193621:/apache-zookeeper-3.7.0-bin/bin# sed -i '165a\ \ \ \ "-Dzookeeper.DigestAuthenticationProvider.superDigest=super:xQJmxLMiHGwaqBvst5y6rkB6HQs=" \\' zkServer.sh
root@667afe193621:/apache-zookeeper-3.7.0-bin/bin# cat zkServer.sh | grep -nA4 nohup
164:    nohup "$JAVA" $ZOO_DATADIR_AUTOCREATE "-Dzookeeper.log.dir=${ZOO_LOG_DIR}" \
165-    "-Dzookeeper.log.file=${ZOO_LOG_FILE}" "-Dzookeeper.root.logger=${ZOO_LOG4J_PROP}" \
166-    "-Dzookeeper.DigestAuthenticationProvider.superDigest=super:xQJmxLMiHGwaqBvst5y6rkB6HQs=" \
167-    -XX:+HeapDumpOnOutOfMemoryError -XX:OnOutOfMemoryError='kill -9 %p' \
168-    -cp "$CLASSPATH" $JVMFLAGS $ZOOMAIN "$ZOOCFG" > "$_ZOO_DAEMON_OUT" 2>&1 < /dev/null &
```

修改acl目录设置：

```shell
setAcl / digest:super:xQJmxLMiHGwaqBvst5y6rkB6HQs=:cdrwa,digest:clickhouse:tt6A3H7+sjjOILlLMvi9Zbv7+ZE=:cdrwa
```



# **<font style="color:#1a1a1a;">7、ClickHouse Readonly自动修复方案</font>**
## **<font style="color:#1a1a1a;">7.1. 恢复流程说明</font>**
:::info
<font style="color:#333333;">● `DETACH TABLE ${database}.${table};`: 这一步是将表从集群中分离，这样它将不再被查询或写入。这是为了确保在执行后续步骤时不会有活动的查询或写入操作。</font>

<font style="color:#333333;">●</font><font style="color:#333333;"> </font><font style="color:#333333;">`SYSTEM DROP REPLICA 'replica_name' FROM ZKPATH '${replica_path}';`: 这一步是删除指定副本（replica）的信息，包括 ZooKeeper 路径中的数据。这将使表变成只读模式，因为它将不再具有必要的元数据信息。</font>

<font style="color:#333333;">●</font><font style="color:#333333;"> </font><font style="color:#333333;">`ATTACH TABLE ${database}.${table};`: 这一步是重新附加（attach）表，这将重新创建表的元数据信息，就好像它是一个全新的空表一样。这一步通常在删除副本后用于恢复表。</font>

<font style="color:#333333;">●</font><font style="color:#333333;"> </font><font style="color:#333333;">`SYSTEM RESTORE REPLICA ${database}.${table};`: 这一步是用于重新创建表的副本，就像它是一个全新的表一样。这将重新附加表的所有分区并恢复元数据信息。</font>

<font style="color:#333333;">● 5. `SYSTEM SYNC REPLICA ${database}.${table};`: 最后一步是等待表的副本同步分区。这是为了确保所有副本都包含相同的数据。建议在恢复完成后检查 `system.detached_parts` 表，以确保所有副本都已同步。</font>

:::

<font style="color:#333333;">使用脚本前需要确保当前服务的Zookeeper集群处于正常状态。</font>

```plain
#查看当前zk节点状态
bin/zkServer.sh  status
```

## **<font style="color:#1a1a1a;">7.2. 脚本说明</font>**
<font style="color:#333333;">以下脚本提供了一键修复Readonly表功能，用户只需要按照要求输入clickhouse登录相关信息即可，默认修复本机的只读表。需要注意本脚本只适用于</font><font style="color:#ff0000;">21.7以上</font><font style="color:#333333;">版本。</font>

<font style="color:#333333;">更新日期：2024-07-18</font>

<font style="color:#333333;">更新内容：</font>

<font style="color:#333333;">1.</font><font style="color:#333333;"> </font><font style="color:#333333;">跳过不支持的物化视图修复，避免大量报错</font>

```plain
#!/bin/bash

# Script: repair_clickhouse_readonly_tables.sh
# Author: bieremayi
# Version: 1.1
# Date: 2023-10-19
# Description: This script automates the repair of ClickHouse readonly tables by detaching, dropping replica,
# attaching, restoring replica, and syncing the replica for each readonly table found in the system.replicas table.
# History : 
# 2023-10-30 : add timeout settings
# 2024-07-18 : skip tables containing 'inner' string

# Default values
ch_server="localhost"
ch_port="9000"
ch_user="default"
ch_password=""

# Prompt the user for ClickHouse server information
read -p "Enter ClickHouse server hostname or IP (default is $ch_server): " user_server
ch_server="${user_server:-$ch_server}"
read -p "Enter ClickHouse server port (default is $ch_port): " user_port
ch_port="${user_port:-$ch_port}"
read -p "Enter ClickHouse username (default is $ch_user): " user_user
ch_user="${user_user:-$ch_user}"

# Only prompt for password if not empty
if [ -z "$ch_password" ]; then
  read -s -p "Enter ClickHouse password: " user_password
  ch_password="$user_password"
fi

# Timeout settings
max_execution_time=3600
receive_timeout=7200

# Get ClickHouse version info
ch_version=$(clickhouse-client --max_execution_time "$max_execution_time" --receive_timeout "$receive_timeout" --host "$ch_server" --port "$ch_port" --user "$ch_user" --password "$ch_password" --query "SELECT version()" --format TSV)

# Extract major and minor version numbers
major_version=$(echo "$ch_version" | cut -d'.' -f1)
minor_version=$(echo "$ch_version" | cut -d'.' -f2)

# Check if the ClickHouse version is greater than 21.7
if [ "$major_version" -gt 21 ] || { [ "$major_version" -eq 21 ] && [ "$minor_version" -ge 7 ]; }; then
  echo "ClickHouse version is $ch_version. Proceeding with table repair."
else
  echo "ClickHouse version $ch_version is not supported. Please upgrade to a newer version (>= 21.7) to use this script."
  exit 1
fi

# Step 1: Get readonly table info
readonly_info=$(clickhouse-client --max_execution_time "$max_execution_time" --receive_timeout "$receive_timeout" --host "$ch_server" --port "$ch_port" --user "$ch_user" --password "$ch_password" --query "SELECT hostname() AS hostname, database, table, zookeeper_path, replica_path FROM system.replicas WHERE is_readonly = 1" --format TSV)

# Step 2: Split the result into lines
IFS=$'\n'
readonly_tables=($readonly_info)

# Loop through the readonly tables
for row in "${readonly_tables[@]}"; do
  # Extract values from the row
  hostname=$(echo "$row" | awk '{print $1}')
  database=$(echo "$row" | awk '{print $2}')
  table=$(echo "$row" | awk '{print $3}')
  replica_path=$(echo "$row" | awk '{print $5}')

  # Skip tables containing 'inner'
  if [[ "$table" == *"inner"* ]]; then
    echo "Skipping table $database.$table as it contains 'inner' and is not supported for materialized views."
    continue
  fi

  echo "Processing readonly table: $database.$table on $hostname"

  # Step 3: Detach the table
  clickhouse-client --max_execution_time "$max_execution_time" --receive_timeout "$receive_timeout" --host "$ch_server" --port "$ch_port" --user "$ch_user" --password "$ch_password" --query "DETACH TABLE $database.$table"

  # Step 4: Drop the replica
  clickhouse-client --max_execution_time "$max_execution_time" --receive_timeout "$receive_timeout" --host "$ch_server" --port "$ch_port" --user "$ch_user" --password "$ch_password" --query "SYSTEM DROP REPLICA '$hostname' FROM ZKPATH '$replica_path'"

  # Step 5: Attach the table
  clickhouse-client --max_execution_time "$max_execution_time" --receive_timeout "$receive_timeout" --host "$ch_server" --port "$ch_port" --user "$ch_user" --password "$ch_password" --query "ATTACH TABLE $database.$table"

  # Step 6: Restore the replica
  clickhouse-client --max_execution_time "$max_execution_time" --receive_timeout "$receive_timeout" --host "$ch_server" --port "$ch_port" --user "$ch_user" --password "$ch_password" --query "SYSTEM RESTORE REPLICA $database.$table"

  # Step 7: Sync the replica
  clickhouse-client --max_execution_time "$max_execution_time" --receive_timeout "$receive_timeout" --host "$ch_server" --port "$ch_port" --user "$ch_user" --password "$ch_password" --query "SYSTEM SYNC REPLICA $database.$table"

  echo "Completed processing readonly table: $database.$table on $hostname"
done


```




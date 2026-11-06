# 1、命令部署
## 1、启动master容器
设置server-id和开启logbin

```yaml
#启动新的镜像，设置server-id和开启logbin
docker run --name mysql   \
-p 13306:3306 -e MYSQL_ROOT_PASSWORD="123456"   \
-d mysql:8.0.32    \
--server-id=1    \
--character-set-server=utf8mb4    \
--collation-server=utf8mb4_unicode_ci    \
--log-bin=mysql-bin    \
--sync_binlog=1
```

mysql登录：` mysql -h 10.20.3.107 -P 13306 -u root -p'123456' `

## 2、创建主从同步账号
查看容器ip

```yaml
[root@everdc01 ~]# docker inspect mysql|grep IPAddress
            "SecondaryIPAddresses": null,
            "IPAddress": "172.17.0.2",
                    "IPAddress": "172.17.0.2",
```

mysql账号创建

```yaml
CREATE USER 'sync_root'@'172.17.%.%' IDENTIFIED WITH mysql_native_password BY 'sync_123456';
# 解决主库sync_root的plugin是caching_sha2_password 导致连接不上
GRANT REPLICATION SLAVE ON *.* TO 'sync_root'@'172.17.%.%';
FLUSH PRIVILEGES;
#查看master的binlog信息
SHOW MASTER STATUS;
mysql> SHOW MASTER STATUS;
+------------------+----------+--------------+------------------+-------------------+
| File             | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set |
+------------------+----------+--------------+------------------+-------------------+
| mysql-bin.000003 |     847 |              |                  |                   |
+------------------+----------+--------------+------------------+-------------------+
1 row in set (0.00 sec)
```

## 3、启动slave容器，实现主从同步
```yaml
docker run --name slave  \
 -p 23306:3306  -e MYSQL_ROOT_PASSWORD="123456"   \
 -d mysql:8.0.32  \
 --server-id=2   \
 --character-set-server=utf8mb4  \
 --collation-server=utf8mb4_unicode_ci 

# 这里master_host就是刚刚看到的master的ip，master_user就是我们创建用于同步的账号
#master_log_file和master_log_pos就是通过show master status获得到的 
# 如果报错 sync_root的plugin是caching_sha2_password 导致连接不上：添加GET_MASTER_PUBLIC_KEY=1;
# CHANGE MASTER TO MASTER_HOST='172.17.0.2',MASTER_USER='sync_root',MASTER_PASSWORD='sync_123456',MASTER_LOG_FILE='mysql-bin.000003',MASTER_LOG_POS=877,master_connect_retry=60,GET_MASTER_PUBLIC_KEY=1;
CHANGE MASTER TO MASTER_HOST='172.17.0.2',MASTER_USER='sync_root',MASTER_PASSWORD='sync_123456',MASTER_LOG_FILE='mysql-bin.000003',MASTER_LOG_POS=847;
#开启同步
START SLAVE;
#查看slave同步状态
SHOW SLAVE STATUS\G

```



<!-- 这是一张图片，ocr 内容为：SHOW SLAVE STATUS\G MYSQL> SH SLAVE-IO-STATE: WAITING FOR SOURCE TO SEND EVENT MASTER_HOST; 172.17.0.2 MASTER_USER: SYNC_ROOT 3306 MASTER_PORT: CONNECT_RETRY:60 MASTER_LOG_FILE: MYSQL-BIN.00003 READ_MASTER_LOG_POS: 877 RELAY_LOG_FILE: A0D97E9B9394-RELAY-BIN.00002  RELAY_LOG_POS: 326 RELAY_MASTER_LOG_FILE: MYSQL-BIN.00003 SLAVE_IO_RUNNING:YES SLAVE_SQL_RUNNING:YES -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1675606703233-f9dea50c-5524-445d-95dc-b6607ae3f3b2.png)

# <font style="color:rgb(79, 79, 79);">使用脚本的方式实现主从</font>
<font style="color:rgb(199, 37, 78);background-color:rgb(249, 242, 244);">docker容器里面的mysql，是通过entrypoint.sh来启动mysql的，如果mysql是第一次启动，在初始化完成之后，会去加载/docker-entrypoint-initdb.d这个目录下面的脚本执行，所以我们可以编写同步脚本，将其挂载在这个目录下即可</font>

```yaml
[root@everdc01 ~]# docker exec -it  db_mysql.1.bb1hwm0422c6e2aqz3b3fznsc   /bin/sh                                        
# ls
bin   dev                         entrypoint.sh  home  lib64  mnt  proc  run   srv  tmp  var
boot  docker-entrypoint-initdb.d  etc            lib   media  opt  root  sbin  sys  usr
```

## <font style="color:rgb(79, 79, 79);">1、编写master用于创建同步账号的脚本</font>
```yaml
#创建对应目录
mkdir -p ./init/{master,slave}
#将master初始化脚本写入到init/master目录下
cat > ./init/master/create_sync_user.sh <<EOF
#!/bin/bash
#定义用于同步的用户名
MASTER_SYNC_USER=\${MASTER_SYNC_USER:-sync_admin}
#定义用于同步的用户密码
MASTER_SYNC_PASSWORD=\${MASTER_SYNC_PASSWORD:-123456}
#定义用于登录mysql的用户名
ADMIN_USER=\${ADMIN_USER:-root}
#定义用于登录mysql的用户密码
ADMIN_PASSWORD=\${ADMIN_PASSWORD:-123456}
#定义运行登录的host地址
ALLOW_HOST=\${ALLOW_HOST:-%}
#定义创建账号的sql语句
CREATE_USER_SQL="CREATE USER '\$MASTER_SYNC_USER'@'\$ALLOW_HOST' IDENTIFIED BY '\$MASTER_SYNC_PASSWORD';"
#定义赋予同步账号权限的sql,这里设置两个权限，REPLICATION SLAVE，属于从节点副本的权限，REPLICATION CLIENT是副本客户端的权限，可以执行show master status语句
GRANT_PRIVILEGES_SQL="GRANT REPLICATION SLAVE,REPLICATION CLIENT ON *.* TO '\$MASTER_SYNC_USER'@'\$ALLOW_HOST';"
#定义刷新权限的sql
FLUSH_PRIVILEGES_SQL="FLUSH PRIVILEGES;"
#执行sql
mysql -u"\$ADMIN_USER" -p"\$ADMIN_PASSWORD" -e "\$CREATE_USER_SQL \$GRANT_PRIVILEGES_SQL \$FLUSH_PRIVILEGES_SQL"
EOF
```



## <font style="color:rgb(79, 79, 79);">2、编写mysql-slave脚本</font>
```yaml
mkdir -p ./init/slave
cat > ./init/slave/slave.sh <<EOF
  #定义连接master进行同步的账号
  SLAVE_SYNC_USER="\${SLAVE_SYNC_USER:-sync_admin}"
  #定义连接master进行同步的账号密码
  SLAVE_SYNC_PASSWORD="\${SLAVE_SYNC_PASSWORD:-123456}"
  #定义slave数据库账号
  ADMIN_USER="\${ADMIN_USER:-root}"
  #定义slave数据库密码
  ADMIN_PASSWORD="\${ADMIN_PASSWORD:-123456}"
  #定义连接master数据库host地址
  MASTER_HOST="\${MASTER_HOST:-%}"
  #等待10s，保证master数据库启动成功，不然会连接失败
  sleep 10
  #连接master数据库，查询二进制数据，并解析出logfile和pos，这里同步用户要开启 REPLICATION CLIENT权限，才能使用SHOW MASTER STATUS;
  RESULT=\`mysql -u"\$SLAVE_SYNC_USER" -h\$MASTER_HOST -p"\$SLAVE_SYNC_PASSWORD" -e "SHOW MASTER STATUS;" | grep -v grep |tail -n +2| awk '{print \$1,\$2}'\`
  #解析出logfile
  LOG_FILE_NAME=\`echo \$RESULT | grep -v grep | awk '{print \$1}'\`
  #解析出pos
  LOG_FILE_POS=\`echo \$RESULT | grep -v grep | awk '{print \$2}'\`
  #设置连接master的同步相关信息
  SYNC_SQL="change master to master_host='\$MASTER_HOST',master_user='\$SLAVE_SYNC_USER',master_password='\$SLAVE_SYNC_PASSWORD',master_log_file='\$LOG_FILE_NAME',master_log_pos=\$LOG_FILE_POS;"
  #开启同步
  START_SYNC_SQL="start slave;"
  #查看同步状态
  STATUS_SQL="show slave status\G;"
  mysql -u"\$ADMIN_USER" -p"\$ADMIN_PASSWORD" -e "\$SYNC_SQL \$START_SYNC_SQL \$STATUS_SQL"
EOF

```

tree查看目录结构如下

ps：脚本授权可执行 chmod 755 *

<!-- 这是一张图片，ocr 内容为：ROOT@EVERDCO1 MYSG11# 1S INIT DOCKER-COMPOSE.YML_BAK DOCKER-COMPOSE.YML MYSQL]# [ROOT@EVERDC01 TREE DOCKER-COMPOSE.YML DOCKER-COMPOSE.YML_BAK INIT MASTER CREATE_SYNC_USER.SH SLAVE SLAVE.SH 3 DIRECTORIES, 4 FILES -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1675613755865-1c42d9cf-e04d-4eca-8233-9910f4028dc8.png)

## 3、编写docker-compose文件
docker-compose.yaml

```yaml
version: '3'
services:
  master:
    image: mysql:8.0.32
    container_name: mysql-master
    ports:
    - '13306:3306'
    restart: always
    hostname: mysql-master
    environment:
      MYSQL_ROOT_PASSWORD: "123456"
      MASTER_SYNC_USER: "sync"
      MASTER_SYNC_PASSWORD: "123456"
      ADMIN_USER: "root"
      ADMIN_PASSWORD: "123456"
      TZ: "Asia/Shanghai"
    networks:
      - mysql
        # ipv4_address: "10.10.10.10" #固定ip，因为从库在连接master的时候，需要设置host
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: 50m
    healthcheck:
      test: ["CMD","mysqladmin","-uroot","-p$${MYSQL_ROOT_PASSWORD}","ping","-h","localhost"]
      timeout: 2s
      interval: 10s
      retries: 5
      start_period: 5s
    logging:
      options:
        max-file: '1'
        max-size: '128k'
    command:
    -  "--server-id=1"
    -  "--character-set-server=utf8mb4"
    -  "--collation-server=utf8mb4_unicode_ci"
    -  "--log-bin=mysql-bin"
    -  "--sync_binlog=1"
    -  "--binlog-ignore-db=mysql"
    -  "--binlog-ignore-db=sys"
    -  "--binlog-ignore-db=performance_schema"
    -  "--binlog-ignore-db=information_schema"
    -  "--sql_mode=NO_AUTO_VALUE_ON_ZERO,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION,PIPES_AS_CONCAT,ANSI_QUOTES"
    volumes:
    - ./init/master:/docker-entrypoint-initdb.d
    - ./data/master:/var/lib/mysql
    privileged: true  
  slave:
    image: mysql:8.0.32
    container_name: mysql-slave
    ports:
    - '23306:3306'
    restart: always
    hostname: mysql-slave
    environment:
      MYSQL_ROOT_PASSWORD: "123456"
      SLAVE_SYNC_USER: "sync"
      SLAVE_SYNC_PASSWORD: "123456"
      ADMIN_USER: "root"
      ADMIN_PASSWORD: "123456"
      MASTER_HOST: "mysql-master"
      TZ: "Asia/Shanghai"
    healthcheck: 
      test: ["CMD","mysqladmin","-uroot","-p$${MYSQL_ROOT_PASSWORD}","ping","-h","localhost"]
      timeout: 2s
      interval: 10s
      retries: 5
      start_period: 5s
    networks:
      - mysql
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: 50m
    logging:
      options:
        max-file: '1'
        max-size: '128k'
    depends_on:
      master:
        condition: service_healthy
    command:
    -  "--server-id=2"
    -  "--character-set-server=utf8mb4"
    -  "--collation-server=utf8mb4_unicode_ci"
    -  "--sql_mode=NO_AUTO_VALUE_ON_ZERO,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION,PIPES_AS_CONCAT,ANSI_QUOTES"
    volumes:
    - ./init/slave:/docker-entrypoint-initdb.d
    - ./data/slave:/var/lib/mysql
    privileged: true  

networks:
  mysql:
    driver: bridge
    ipam: #网络管理器
      driver: default
      config:
      - subnet: "10.10.0.0/16"
```

执行`docker-compose up  -d `

<!-- 这是一张图片，ocr 内容为：DOCKER-COMPOSE.YML INIT DOCKER-COMPOSE.YML_BAK [ROOT@EVERDCO1 MYSQL]# DOCKER-COMPOSE UP -D [+] RUNNING 2/2 21.4S CONTAINER MYSQL-MASTER HEALTHY 21.8S CONTAINERMYSA SGL-SLAVE STARTED OOT@EVERDCO1 MYSG1]# -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1675614546285-7d01a5fc-4e68-4031-b7a6-86340255cb4e.png)

docker logs -f mysql-slave  查看同步状态：

<!-- 这是一张图片，ocr 内容为：]2023-02-05 23:47:Z1+08:0O [NOTE] [ENTRYPOINT]: /UST/LOCAL/BIN/DOCKER-ENTRYPOINT.SH RUNNING/DOCKER-ENTRYPOINT-INITDB.D/SLAVE.SH IQL USING A PASSWORD ON THE COMMAND LINE INTERFACE CAN BE INSECURE. MYSQL: [WARNING] MYSQL: [WARNING] USIN HE COMMAND LINE INTERFACE CAN BE INSECURE. USING A PASSWORD ON THE 2023-02-05T15:47:Z2,6534042 10 [SYSTEN] [MY-010597] [REP]] [REP]]'CHANGE MASTER TO FOR CHANNEL NEL " EXECUTED'. PREVIOUS STATE MASTER HOST:' . MASTE MASTER HOSTER HOSTE MASTER HOSTER HOST:' . MA MASTER_P AR-BIND:''. NEW STATE MASTER-HOSTER.'MYSQ1-MASTER', MASTER-PORT- 3306, MASTER.109-F1LE三'M ILEMY ORT- 3306, MASTER-LOG-FILE三'', MASTER_LOG-POS: 4, MASTER-B SQL-BIN.000003',MASTER-LOG-POS; 157, MASTER_BIND CONSIDER USING THE'USER AND PASSUORD CONNECTION OPTION OPTIONS FOR SLAVE; SEE THE 'START SL' OT SECURE AND IS THEREFORE NOT RECOMMENDED. PLE ED. PLEASE CONS VE SYNTAX' IN THE MYSQL MANUAL FOR MORE IN AN E INFORMATION. [MY-010562] [REPL] SLAVE I/O THREAD FOR CHANNEL ' 2023-02-05T15:47:21.669205Z 11 [SYSTEM] ': CONNECTED TO MASTER 'SYNCQMYSQL-MASTER:3306',REPLI CATION STARTED IN LOQ 'MYSQL-BIN.00003' AT POSITION 157 [ URCE VERSION MASTER_HOST:MYSGL-MASTER MASLEL-0SEL,SYITC MASTER_PORT:3306 CONNECT_RETRY:60 MASTER_LOG_FILE:M E: MYSQL-BIN.00003 157  READ_MASTER_LOG_POS: RELAY_LOG_FILE: MYSQL-SLAVE-RELAY-BIN.000001 RELAY-LOG-POS: :4 ILE. MVSAL-HIN.00003 SLAVE_IO_RUNNING: YES SLAVE_SQL_RUNNING:YES KEPTTCATE_DO_DB: REPLICATE_IGNORE_DB: REPLICATE_DO_TABLE: REPLICATE_IGNORE_TABLE: REPLICATE_WILDO_TABLE: REPLICATE_WILD_IGNORE_TABLE; LAST_ERRNO:0 LAST_ERROR: SKIP_COUNTER:0 CER_LOG_POS: 157 EXEC MASTER RELAY LOG_SPACE:157 UNTIL_CONDITION:NONE UNTIL_LOG_FILE: UNTIL_LOG_POS:0 MASTER_SSL_ALLOWED:NO MASTER_SSL_CA_FILE: MASTER_SSL_CA_PATH: MASTER_SSL_CERT: MASTER_SSL_CIPHER: MASTER_SSL_KEY: -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1675613954139-f6db13f1-100b-4f95-8d63-d1b2ec4317f7.png)

## 4、测试主从同步
<!-- 这是一张图片，ocr 内容为：查询格式 工具 查看 窗口 编辑 文件 帮助 收藏夹 FIXY 模型 其它 查询 新建查询 视图 连接 自动运行 备份 用户 图表 函数 10.20.3.107-13306 对象 无标题-查询 INFORMATIONSCHEMA 美化SQL 代码段 查询创建工具 保存 MYSQL 停止...停止选择的 运行已选择的 10.20.3.107-13306 PERFORMANCE SCHEMA SYS CREATE DATABASE TEST; TEST 10.20.3.107-23306 INFORMATION SCHEMA MYSQ PENORMANCE SCHEMA SYS TEST -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1675614159835-64eafbb4-2767-4d7e-bda4-8592515d3dc5.png)

## 5、主从stack部署
条件：预先在集群的每个节点创建好挂载目录

```yaml
version: '3'
services:
  master:
    image: mysql:8.0.32
    container_name: mysql-master
    ports:
    - '13306:3306'
    restart: always
    hostname: mysql-master
    environment:
      MYSQL_ROOT_PASSWORD: "123456"
      MASTER_SYNC_USER: "sync"
      MASTER_SYNC_PASSWORD: "123456"
      ADMIN_USER: "root"
      ADMIN_PASSWORD: "123456"
      TZ: "Asia/Shanghai"
    networks:
      - mysql
    deploy:
      resources:
        limits:
          memory: 512M
    healthcheck:
      test: ["CMD","mysqladmin","-uroot","-p$${MYSQL_ROOT_PASSWORD}","ping","-h","localhost"]
      timeout: 2s
      interval: 10s
      retries: 5
    logging:
      options:
        max-file: '1'
        max-size: '128k'
    command:
    -  "--server-id=1"
    -  "--character-set-server=utf8mb4"
    -  "--collation-server=utf8mb4_unicode_ci"
    -  "--log-bin=mysql-bin"
    -  "--sync_binlog=1"
    -  "--binlog-ignore-db=mysql"
    -  "--binlog-ignore-db=sys"
    -  "--binlog-ignore-db=performance_schema"
    -  "--binlog-ignore-db=information_schema"
    -  "--sql_mode=NO_AUTO_VALUE_ON_ZERO,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION,PIPES_AS_CONCAT,ANSI_QUOTES"
    volumes:
    - /home/mysql/init/master:/docker-entrypoint-initdb.d
    - ./data/master:/var/lib/mysql
    privileged: true  
  slave:
    image: mysql:8.0.32
    container_name: mysql-slave
    ports:
    - '23306:3306'
    restart: always
    hostname: mysql-slave
    environment:
      MYSQL_ROOT_PASSWORD: "123456"
      SLAVE_SYNC_USER: "sync"
      SLAVE_SYNC_PASSWORD: "123456"
      ADMIN_USER: "root"
      ADMIN_PASSWORD: "123456"
      MASTER_HOST: "mysql-master"
      TZ: "Asia/Shanghai"
    healthcheck: 
      test: ["CMD","mysqladmin","-uroot","-p$${MYSQL_ROOT_PASSWORD}","ping","-h","localhost"]
      timeout: 2s
      interval: 10s
      retries: 5
    networks:
      - mysql
    deploy:
      resources:
        limits:
          memory: 512M
    logging:
      options:
        max-file: '1'
        max-size: '128k'
    depends_on:
       - master
    command:
    -  "--server-id=2"
    -  "--character-set-server=utf8mb4"
    -  "--collation-server=utf8mb4_unicode_ci"
    -  "--sql_mode=NO_AUTO_VALUE_ON_ZERO,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION,PIPES_AS_CONCAT,ANSI_QUOTES"
    volumes:
    - /home/mysql/init/slave:/docker-entrypoint-initdb.d
    - ./data/slave:/var/lib/mysql
    privileged: true  

networks:
  mysql:
    driver: overlay
    ipam: #网络管理器
      driver: default
      config:
      - subnet: "10.10.0.0/16"
```

然后执行：`docker stack deploy -c docker-compose.yml mysql_db`

<!-- 这是一张图片，ocr 内容为：只道女王 10.20.3.107:9000/#/2/DOCKER/STACKS/MYSGL DB7TYPE-18/REGULAR-FALSEBLEXTERNALERNALERXORPHANED-FALSE CGIT克隆别人代码提... LUCKY YE-自闭~ 系统镜像下载 工具箱-程序员编程... H 运维 IOS手机端网页测试 PYTHON教程-廖雪峰 JAVAWEB教程目录... BUTTERFLY STACK DETAILS MYSQL_DB 合 ( COLUMNS SETTING 目 SERVICES UPDATE I REMOVE SEARCH... SCHEDULING MODE NAME 1会 品 PUBLISHEDPORTS LAST UPDATE OWNERSHIP LMAGE 口13306:3306 ADMINISTRATORS REPLICATED 1 1 1 SCALE 2023-02-06 15:05:13 MYSQL_DB_MASTER MYSQL:8.0.32 STATUS I ACTIONS SLOT LAST UPDATE NODE TASK FILTER 00 2023-02-0615:05:34 EVERDC04 4ZVPUFMWGTE3YDRY115GT5HLR REJECTED 日0 1 EVERDC04 2023-02-0615:05:19 JZ8CS05K1F5O9OSQYQMNJ50OV REJECTED 相 00 1 2023-02-06 15:05:29 EVERDC04 Q436HWZT1S3941H7N3O145JLZ REJECTED 风 10 1 2023-02-06 15 05:24 EVERDC04 REJECTED WRLOG9CSUD52IF9KPFLI5G1IG 日0%>一 2023-02-06 15:05:59 EVERDC02 RUNNING HRMON0ZI5XA68AHLZORFH4F72 23306:3306 2023-02-06 15:05.09 MYSQL:8.0.32 11TSCALE ADMINISTRATORS MYSQL_DB_S REPLICATED SLAVE E LAST UPDATE ACTIONS NODE SLOT STATUS 1:FILTER TASK 00 2023-02-0615:05:40 1 EVERDC04 CULT2NE657SGDEO4ECA7H6158 REJECTED 18 1 2023-02-06 15:05 35 EVERDC04 REJECTED GFJFTA6VN9QGAEILASYFCKNWG 日0 2023-02-0615:05:45 EVERDC04 REJECTED INSQFVAAA69FVVY7KSLWOOT8W 日日 2023-02-0615:05:30 EVERDC04 REJECTED K172HOUSDA7W6FSACK21TERF3 50元 2023-02-0615:06:11 EVERDCO3 RS54NZBCZBLCAPRRDOZBNGOUO RUNNING AILABLE -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1675667399685-847a2fb2-853b-4a9a-826f-95798c045197.png)

查看日志主从同步信息：

<!-- 这是一张图片，ocr 内容为：CONTAINERS>MYSQL-DB-SLAVE.L.RS54NZBCZBLCAPRRDOZBNGOUO>LOGS MY ACCOUNT LOG.OUT 目 LOG VIEWER SETTINGS AUTO-REFRESH LOGS WRAP LINES DISPLAY TIMESTAMPS FETCH ALLLLOGS FILTER... SEARCH LINES 100 DOWNLOAD LOGS X UNSELECT ACTIONS COPY COPY OY SELECTED LINES MASTER USER:SYNC MASTER PORT:3306 CONNECT RETRY:60 G1-BIN.000003 MASTER_LOG_FILE:MYSQL-BI READ_MASTER_LOG_POS:157 RELAY LOG FILE:MYSQL -SLAVE-RELAY-BIN.000001 RELAY LOG POS:4 RELAY_MASTER_LOG_FILE:MYSQL-BIN.00003 SLAVE_IO RUNNING:YES SLAVE SOL RUNNING: YES RENLICATE DO DB: -->
![](https://cdn.nlark.com/yuque/0/2023/png/34997268/1675667358776-006bfdc5-7cb4-4044-a951-b59740e01b2c.png)


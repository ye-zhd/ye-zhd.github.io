

# <font style="color:rgb(79, 79, 79);">一、drop 表恢复：全量备份 + Binlog 增量补充</font>
全量备份软件：[https://www.percona.com/downloads/](https://www.percona.com/downloads/)

mysql为8.0版本，系统环境是欧拉2203版本，本次下载

<!-- 这是一张图片，ocr 内容为：XTRABACKUP PERCONA MYSQL的热备份解决方案 PERCONA FOR MYSQL 产品组 版本 平台 LINUX-通用 PERCONA-XTRABACKUP-8.0.35 PERCONA XTRABACKUP 8.0 软件包下载选项 下载 PERCONA-XTRABACKUP-8.0.35-36-LINUX-X86-64.GLIBC2.28-MINIMAL.TAR.G2 30.1MB 正载 PERCONA-XTRABACKUP-8.0.35-36-LINUX-X86_64.GLIBC2.28- 133字节 MINIMAL.TAR.GZ.SHA256SUM 下载 500.5MB PERCONA-XTRABACKUP-8.0.35-36-LINUX-X86-64.GLIBC2.28.TAR.GZ 正载 PERCONA-XTRABACKUP-8.0.35-36-LINUX- 125字节 X86_64.GLIBC2.28.TAR.GZ.SHA256SUM 文档 用户手册 -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1783239708674-ef6ccc12-ddb0-4461-8ba0-dcb1fe244974.png)

drop table 会直接删除表结构与所有数据，属于高危 DDL 操作，恢复需依赖「全量备份打底 + Binlog 增量补充」的组合方案。



```bash
#上传解压创建
/root/mysql/percona-xtrabackup-8.0.35-36-Linux-x86_64.glibc2.28-minimal/bin
# 创建软链接
sudo ln -s /root/mysql/percona-xtrabackup-8.0.35-36-Linux-x86_64.glibc2.28-minimal/bin/xtrabackup /usr/local/bin/xtrabackup
sudo ln -s /root/mysql/percona-xtrabackup-8.0.35-36-Linux-x86_64.glibc2.28-minimal/bin/xbstream /usr/local/bin/xbstream
sudo ln -s /root/mysql/percona-xtrabackup-8.0.35-36-Linux-x86_64.glibc2.28-minimal/bin/xbcrypt /usr/local/bin/xbcrypt
sudo ln -s /root/mysql/percona-xtrabackup-8.0.35-36-Linux-x86_64.glibc2.28-minimal/bin/xbcloud /usr/local/bin/xbcloud
```

## 1.1 恢复核心逻辑
通过全量备份还原误删前的基础数据，再从 Binlog 日志中提取全备后到误删前的增量数据，回放至恢复实例，最终完成数据完整恢复。



## 1.2 必备前提
存在误删时间点前的全量备份文件（无全备则无法恢复）；

MySQL 已开启Binlog 日志，且全备后至误删期间的日志完整无缺失；

提前部署专用恢复实例（避免临时部署浪费时间）。



## 1.3 实战操作步骤
### 1.3.1 xtrabackup恢复还原
#### 1.3.1.1 环境准备
```sql
-- 1. 创建测试库表与基础数据
create database recover;
use recover;
CREATE TABLE test_recover (
  id int NOT NULL AUTO_INCREMENT,
  a int NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB CHARSET=utf8mb4;
insert into test_recover values (1,1),(2,2);

-- 2. 创建备份专用用户（遵循最小权限原则）
CREATE USER `u_backup`@`localhost` IDENTIFIED WITH MYSQL_NATIVE_PASSWORD BY 'Ujg8G_aUU';
GRANT SELECT, RELOAD, PROCESS, SUPER, LOCK TABLES,BACKUP_ADMIN ON *.* TO `u_backup`@`localhost`;
RENAME USER 'u_backup'@'localhost' TO 'u_backup'@'%';


-- 3. 执行全量备份（使用xtrabackup工具）
xtrabackup      --host=127.0.0.1 --port=3306   --user=u_backup --password='Ujg8G_aUU'   --backup   --stream=xbstream   --target-dir=/tmp/xtrabackup_temp   > /data/backup/xtrabackup_bak/xtrabackup.xbstream


```

备份文件如下：

<!-- 这是一张图片，ocr 内容为：-STREAMXBSTREAM --HOST-127.0.0.1 --PORT-3306  --USER-U_BAC UP --PASSWORD-'UJG8G_AUU' BACKUP [ROOT@LOCALHOST BIN]#./XTRABACKUP U_BACKUP TARG ET-DIRE/TMN/XTRAHACKUN TEMP > /DATA/HACKUP/XTRABACKUP HAK/XTRABACKUP XBSTREAMAS [ROOT@LOCALHOST BIN]#1S -LH /DATA/ H /DATA/BACKUP/XTRABACKUP BAK/XTRABACKUP.XBSTREAM FRW-T--T-- 1 ROOT ROOT 77M JU7. 5 15:40 /DATA/BACKUD/XTRABACKUP-BAK/XTRABACKUP.XBSTREAM -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1783237359093-18336413-6c9e-4df1-9207-d77dd6ac7cda.png)

#### <font style="color:rgb(79, 79, 79);">1.3.1.2 模拟误操作场景</font>


```bash
-- 模拟误删表
drop table test_recover;
```

#### <font style="color:rgb(79, 79, 79);">1.3.1.3 全量备份导入恢复实例</font>
①删除数据目录：

```bash
[root@localhost mysql]# pwd
/data/mysql
[root@localhost mysql]# cd ..
[root@localhost data]# mv mysql mysql_bak
[root@localhost data]# mkdir mysql
```

②使用xbstream还原：

```bash
# 创建目标目录
mkdir -p /data/backup/restore

# 解压（使用重定向输入）
./xbstream -x -C /data/backup/restore < /data/backup/xtrabackup_bak/xtrabackup.xbstream


xtrabackup --prepare --target-dir=/data/backup/restore


恢复数据（copy-back）
./xtrabackup --copy-back --target-dir=/data/backup/restore --datadir=/data/mysql

chown -R mysql.mysql /data/mysql
```

<!-- 这是一张图片，ocr 内容为：[ROOT@LOCALHOST # MYSQL -UROOT -PEVERSEC123098 A PASSWORD ON THE COMMAND LINE INTERFACE CAN BE INSECURE. [WARNING] MYSQL: USING WELCOME TO THE MYSQL COMMANDS END WITH ; OR \G. MONITOR YOUR MYSOL CONNECTION I IDIS8 SERVER VERSION: 8.0.37 MYSQL COMMUNITY SERVER - GPL COPYRIGHT (C) 2000, 2026, ORACLE AND/OR ITS AFFILIATES. ORACLE IS A REQISTERED TRADEMARK OF ORACLE CORPORATION AND/OR ITS LAFFILIATES. OTHER NAMES MAY BE TRADEMARKS OF THEIR RESPECTIVE OWNERS ITYPE 'HELP;" OR 'VH' FOR HELP. TYPE "VC' TO CTEAR THE CURRENT INPUT STATEMENT. FROM RECOVER.TEST_RECOVER; MYSQL> SELECT ,-------+ ID L A 一十一 12 T2 , ROWS IN SET (0.01 SEC) MYSG -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1783238954380-b362ef4d-66c5-45e4-927e-1178dc7ed02b.png)

### <font style="color:rgb(79, 79, 79);">1.3.2 Binlog 增量数据恢复模拟</font>
#### 1.3.2.1 环境准备
```sql
-- 创建新表
CREATE TABLE test_recover_binlog (
  id INT,
  val INT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入几行数据
INSERT INTO test_recover_binlog VALUES (1, 100), (2, 200), (3, 300);

-- 验证
SELECT * FROM test_recover_binlog;
```



<!-- 这是一张图片，ocr 内容为：CREATE TABLE TEST_RECOVER_BINLOG ( MYSQL> ID INT, AI VAL INT ENGINE-INNODB DEFAULT CHARSET-UTF8MB4; QUERY OK, O  AFFECTED (0.23 SEC) ROWS MYSQL>--插入几行数据 MYSQL> INSERT INTO TEST-RECOVER-BINLOG VALUES (1, 100), (2, 200), (3, 300); (0.01 SEC) QUERY OK, 3 ROWS AFFECTED WARNINGS: 0 RECORDS: 3 DUPLICATES: O MYSQL> R_BINLOG; FROM TEST_RECOVER_B SELECT MYSQ1> ID VA7 123 100 200 300  IN SET (0.00 SEC) ROWS MYSQL> -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1783246479543-fc8426d6-351b-492e-a208-e5f00c40b580.png)

#### <font style="color:rgb(79, 79, 79);">1.3.2.2 模拟误操作场景</font>
前提：mysql的my.cnf开启gitd

```plain
gtid_mode=ON
enforce_gtid_consistency=ON
```

```sql
USE recover;
DROP TABLE test_recover_binlog;
```



#### <font style="color:rgb(79, 79, 79);">1.3.2.3 定位 DROP 事件在 binlog 中的位置</font>
```sql
mysql> SHOW BINARY LOGS;
+---------------+-----------+-----------+
| Log_name      | File_size | Encrypted |
+---------------+-----------+-----------+
| binlog.000011 |       157 | No        |
| binlog.000012 |       180 | No        |
| binlog.000013 |       180 | No        |
| binlog.000014 |      2114 | No        |
| binlog.000015 |       970 | No        |
+---------------+-----------+-----------+
5 rows in set (0.00 sec)
```

按照执行时间 定位搜索：

```sql
mysqlbinlog /data/mysql/binlog.000015 | head -10   # 查看文件开头时间
mysqlbinlog /data/mysql/binlog.000015 | tail -10   # 查看文件末尾时间

```

<!-- 这是一张图片，ocr 内容为：#END OF LOG TLLE *!50003 SET COMPLETION_TYPE-@OLD_COMPLETION_TYPE*/; 'TROOTOLOCALHOST RESTOREL# MYSQLBINLOG /DATA/MYSQL/BINLOG.000015 I HEAD -10 L# THE PROPER TERM IS PSEUDO_REPLICAUMODE, BUT WE USE THIS COMPATIBITITY ALIAS AND OLDER. # TO MAKE THE STATEMENT USABLE ON SERVER VERSIONS 8.0.24 AND OL /*!50530 SET @QSESSION.PSEUDO_SLAVE_MODE-1*/; /*!50003 SET COLD-COMPLETION_TYPE-@QCOMPLETION_TYPE,COMPLETION_TYPE-0*/; DELIMITER/; #AT4 9 START: BINLOG V 4, SERVER V 8.0.37 CREATED 260705 18:40:31 AT STARTUP #260705 18:40:31 SERVER ID 1 1  END_LOG_POS 126 CRC32 0X61676D89 S # WARNING: THIS BINLOG IS EITHER IN USE OR WAS NOT CLOSED PROPERLY ROLLBACK7 BINLOG [ROOTELOCALHOST RESTORE]# MYSQLBINLOQ /DATA/MYSQ1/BINLOG.000015 ] TAIL -10 #AT820 #260705 18:41:35 SERVER ID 1 ERROR_CODE-O EXEC_TIME-0 XID-12 END_LOG_POS 970 CRC32 OXDD3C02B9 QUERY   THREAD_ID-8 SET TIMESTAMP1783248095/*!*/; DROP TABLE  TEST_RECOVER_BINLOG / SERVER A/ /GENERATEDBY /产!:/ EXT- 'AUTOMATIC' /* ADDED BY MYSQLBINLOG */ /*!*/; SET @@SESSION.GTID_NEXT 'A DELIMITER # END OF LOG FILE *!50003 SET COMPLETION_TYPE-@OLD_COMPLETION_TYPE:/ 150530 SET @QSESSION.PSEUDO_SLAVE_MODE-0*/; [ROOT@LOCALHOST RESTORE]# 网安EVERSEC GJ192 网安11.12TOGJ 重启ETL SWITCH ROOT 运营商EVERSEC 172.16 ROOT DEBUG HB FTP-EVERSEC 运营商ROOT EVEROSROOT ROOT HB -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1783248093220-72143263-3d0a-41b7-8cf6-3d05bc2b8623.png)

可以看到，我们的操作是在整个binlog文件里面的。



```sql
mysqlbinlog   --start-datetime="2026-07-05 18:40:00"   --stop-datetime="2026-07-05 18:42:59"   /data/mysql/binlog.000014 > /tmp/recover_by_time.sql

cat /tmp/recover_by_time.sql |grep -A 5 -B 5 "DROP TABLE"

#或者直接
mysqlbinlog \
  --database=recover \
  --base64-output=DECODE-ROWS -v \
  /data/mysql/binlog.000015 \
  | grep -E "GTID_NEXT|CREATE TABLE|INSERT|DROP TABLE"
```

 <!-- 这是一张图片，ocr 内容为："DROP TABLE [ROOT@LOCALHOST RESTORE]# CAT /TMP/RECOVER BY_TIME.SQL LGREPA5-B5 7*!80014 SET @@SESSION.IMMEDIATE_SERVER_VERSION-80037*/*! ISET QUSESSION.GTID-NEXT- '9CFFB270-7848-11F1-98E5-9EBELA6E4559:3'/*! #AT820 'VER ID 1 END_LOG POS 970 CRC32 OXDD3CO2B9 ERROR_CODEO XID - 12 THREAD_ID8 EXEC_TIME-O #260705 18:41:35 SERVER QUERY SET TIMESTAMP1783248095/; G' /* GENERATED BY SERVER */ TEST_RECOVER_BINLOG DROP TABLE 'AUTOMATIC' /* ADDED BY MYSQLBINLOG */ /*/; SET@@SESSION.GTIDNEXT DELIMITER FILE # END OF LOG TON_TYPE@OLD_COMPLETION_TYPE*/; /50003 SET COMPLETION [ROOT@LOCALHOST RESTORE]# -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1783248121306-067ae809-8b4f-4d70-ac59-6e46f9f8ff53.png)

<!-- 这是一张图片，ocr 内容为：/DATA/MYSQL/B1NLOG.00015 LROOT@LOCA HOST RESTOREJ# MYSQIBINLOG [ROOT@LOCALHOST RESTORE]# MYSQLBINLOG -DATABASERECOVER --BASE64-OUTPUTDECODE-ROWS -V \ /DATA/MYSQL/BINLOG.000015 GREP -E "GTID NEXT|CREATE TABLE|INSERTIDROP TABLE" IT -DEITISESE RAS BEEN USEET;  TT MAY FTILL  ANT  ERTS OF ERTE  SUEE STE STE OR WARNING: THE OPTION - LINCLUDE TRANSACTIONS, YOU SHOULD USE THE OPTIONS --EXCLUDE-GTIDS OR --INCTUDE-9 INCLUDE-GTIDS, RESPECTIVELY, INSTEAD. ISET QQSESSION.GTID_NEXT- '9CFFB270-7848-11F1-98E5-9EBELA6E4559:1'/*!; EOVER-BINLOG ( ID INT,  VAL INT ) ENGINE-INNODB DEFAULT CHARSET-UTF8MB4 CREATE TABLE TEST_RECOVER. SET@@SESSION.GTID NEXT '9CFFB270-7848-11F1-98E5-9EBELA6E4559:2'/产! ### INSERT INTO RECOVER TEST_RECOVER_BINLOG TEST_RECOVER_BINLOG ### INSERT INTO RECOVER ### INSERT INTO RECOVER' TEST_RECOVER_BINLOG '9CFFB270-7848-11F1-98E5-9EBELA6E4559:3'/之/; SET @QSESSION.GTID_NEXT DROP TABLE TEST_RECOVER_BI _BINLOG / GER GENERATED BY SERVERVER SET QQSESSION.GTIDNEXT EXTE"AUTOMATIC'/ [ROOT@LOCALHOST RESTORE]# -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1783248867358-7f684083-adaa-406b-98b7-ad870a7be3d5.png)



可用看到找到GTID范围：9cffb270-7848-11f1-98e5-9ebe1a6e4559

```sql
mysqlbinlog \
  --skip-gtids \
  --database=recover \
  --exclude-gtids='9cffb270-7848-11f1-98e5-9ebe1a6e4559:3' \
  /data/mysql/binlog.000015 \
  | mysql -h127.0.0.1 -P3306 -uroot -peversec123098
```

数据恢复了

<!-- 这是一张图片，ocr 内容为：FROM TEST_RECOVER_BINLOG; MYSQL> SELECT R 1046 (3DOOO): NO DATABASE SELECTED ERROR FROM RECOVER.TEST_RECOVER_BINLOG; SELECT MYSQ ID VA 123 100 200 300 3  SET (0.00 SEC) IN ROWS MYSGL> -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1783249021108-2ba1ed36-9817-4b91-b60b-6a2479bf35e1.png)





## <font style="color:rgb(15, 17, 21);">1.4 xtrabackup增量备份</font>
<font style="color:rgb(15, 17, 21);">增量备份的核心是</font>**<font style="color:rgb(15, 17, 21);">基于上一次备份（全量或增量）的 LSN（日志序列号）</font>**<font style="color:rgb(15, 17, 21);">，只备份自那以来发生变更的数据页</font><font style="color:rgb(15, 17, 21);">。</font>

### <font style="color:rgb(15, 17, 21);">1. 前提：进行一次全量备份</font>
<font style="color:rgb(15, 17, 21);">增量备份需要一个全量备份作为基础</font><font style="color:rgb(15, 17, 21);">。</font>

<font style="color:rgb(15, 17, 21);">bash</font>

```plain
xtrabackup --host=127.0.0.1 --port=3306 \
  --user=u_backup --password='Ujg8G_aUU' \
  --backup --target-dir=/data/backup/base
```

<font style="color:rgb(15, 17, 21);">备份完成后，会在</font><font style="color:rgb(15, 17, 21);"> </font>`<font style="color:rgb(15, 17, 21);background-color:rgb(235, 238, 242);">/data/backup/base</font>`<font style="color:rgb(15, 17, 21);"> </font><font style="color:rgb(15, 17, 21);">目录下生成一个</font><font style="color:rgb(15, 17, 21);"> </font>`<font style="color:rgb(15, 17, 21);background-color:rgb(235, 238, 242);">xtrabackup_checkpoints</font>`<font style="color:rgb(15, 17, 21);"> </font><font style="color:rgb(15, 17, 21);">文件，里面记录了备份的 LSN 信息</font><font style="color:rgb(15, 17, 21);">。</font>

### <font style="color:rgb(15, 17, 21);">2. 第一次增量备份（基于全量备份）</font>
<font style="color:rgb(15, 17, 21);">使用</font><font style="color:rgb(15, 17, 21);"> </font>`<font style="color:rgb(15, 17, 21);background-color:rgb(235, 238, 242);">--incremental-basedir</font>`<font style="color:rgb(15, 17, 21);"> </font><font style="color:rgb(15, 17, 21);">指定基于哪个全量备份目录</font><font style="color:rgb(15, 17, 21);">。</font>

<font style="color:rgb(15, 17, 21);">bash</font>

```plain
xtrabackup --host=127.0.0.1 --port=3306 \
  --user=u_backup --password='Ujg8G_aUU' \
  --backup --target-dir=/data/backup/inc1 \
  --incremental-basedir=/data/backup/base
```

`<font style="color:rgb(15, 17, 21);background-color:rgb(235, 238, 242);">/data/backup/inc1</font>`<font style="color:rgb(15, 17, 21);"> </font><font style="color:rgb(15, 17, 21);">目录下会生成</font><font style="color:rgb(15, 17, 21);"> </font>`<font style="color:rgb(15, 17, 21);background-color:rgb(235, 238, 242);">.delta</font>`<font style="color:rgb(15, 17, 21);"> </font><font style="color:rgb(15, 17, 21);">文件，代表自全量备份以来的数据变更</font><font style="color:rgb(15, 17, 21);">。</font>

### <font style="color:rgb(15, 17, 21);">3. 第二次增量备份（基于上一次增量备份）</font>
<font style="color:rgb(15, 17, 21);">将</font><font style="color:rgb(15, 17, 21);"> </font>`<font style="color:rgb(15, 17, 21);background-color:rgb(235, 238, 242);">--incremental-basedir</font>`<font style="color:rgb(15, 17, 21);"> </font><font style="color:rgb(15, 17, 21);">指向上一次增量备份的目录，形成增量链</font><font style="color:rgb(15, 17, 21);">。</font>

<font style="color:rgb(15, 17, 21);">bash</font>

```plain
xtrabackup --host=127.0.0.1 --port=3306 \
  --user=u_backup --password='Ujg8G_aUU' \
  --backup --target-dir=/data/backup/inc2 \
  --incremental-basedir=/data/backup/inc1
```

### <font style="color:rgb(15, 17, 21);">4. 恢复时的准备（Prepare）</font>
<font style="color:rgb(15, 17, 21);">恢复增量备份时，需要按顺序应用这些备份</font><font style="color:rgb(15, 17, 21);">：</font>

**<font style="color:rgb(15, 17, 21);">先准备（prepare）全量备份</font>**<font style="color:rgb(15, 17, 21);">：</font>

1. <font style="color:rgb(15, 17, 21);">bash</font><font style="color:rgb(15, 17, 21);">xtrabackup --prepare --apply-log-only --target-dir=/data/backup/base</font>

`<font style="color:rgb(15, 17, 21);background-color:rgb(235, 238, 242);">--apply-log-only</font>`<font style="color:rgb(15, 17, 21);"> </font><font style="color:rgb(15, 17, 21);">表示只应用日志，不回滚未提交的事务，以便后续继续应用增量</font><font style="color:rgb(15, 17, 21);">。</font>

**<font style="color:rgb(15, 17, 21);">再将第一个增量应用到全量备份上</font>**<font style="color:rgb(15, 17, 21);">：</font>

2. <font style="color:rgb(15, 17, 21);">bash</font>

```plain
xtrabackup --prepare --apply-log-only --target-dir=/data/backup/base \
  --incremental-dir=/data/backup/inc1
```

**<font style="color:rgb(15, 17, 21);">继续应用后续的增量备份</font>**<font style="color:rgb(15, 17, 21);">（如有）：</font>

3. <font style="color:rgb(15, 17, 21);">bash</font>

```plain
xtrabackup --prepare --apply-log-only --target-dir=/data/backup/base \
  --incremental-dir=/data/backup/inc2
```

**<font style="color:rgb(15, 17, 21);">最后一步</font>**<font style="color:rgb(15, 17, 21);">：准备最后一个增量备份时，</font>**<font style="color:rgb(15, 17, 21);">不要</font>**<font style="color:rgb(15, 17, 21);">加</font><font style="color:rgb(15, 17, 21);"> </font>`<font style="color:rgb(15, 17, 21);background-color:rgb(235, 238, 242);">--apply-log-only</font>`<font style="color:rgb(15, 17, 21);">，让 xtrabackup 完成最终的回滚操作，使数据一致</font><font style="color:rgb(15, 17, 21);">。</font>





### 5.shell脚本实现增量备份


```sql
#!/bin/bash
# ============================================================
# 名称：incremental_backup.sh
# 描述：使用 Percona XtraBackup 实现 MySQL 增量备份
# 用法：./incremental_backup.sh
# ============================================================

# ---------- 配置区（请按实际环境修改） ----------
MYSQL_HOST="127.0.0.1"
MYSQL_PORT="3306"
MYSQL_USER="u_backup"
MYSQL_PASS="Ujg8G_aUU"
BACKUP_BASE="/data/backup"            # 备份根目录
FULL_BACKUP_DIR="${BACKUP_BASE}/full" # 全量备份目录
INCR_BACKUP_DIR="${BACKUP_BASE}/incr" # 增量备份存放目录（按日期存放）
KEEP_DAYS=7                           # 保留最近 N 天的增量备份
LOG_FILE="${BACKUP_BASE}/backup.log"  # 日志文件

# 判断是否启用压缩（可选），默认使用 xbstream 流式备份，无需压缩
# 如果希望压缩，可以使用 gzip 或 pigz，这里留空

# ---------- 函数：记录日志 ----------
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') : $*" | tee -a "$LOG_FILE"
}

# ---------- 函数：清理旧备份 ----------
cleanup_old_backups() {
    # 清理超过 KEEP_DAYS 天的增量备份目录（假设目录名为日期格式 YYYYMMDD）
    find "$INCR_BACKUP_DIR" -maxdepth 1 -type d -name "20*" -mtime +$KEEP_DAYS -exec rm -rf {} \; 2>/dev/null
    log "已清理超过 ${KEEP_DAYS} 天的增量备份目录"
}

# ---------- 创建必要的目录 ----------
mkdir -p "$FULL_BACKUP_DIR" "$INCR_BACKUP_DIR"

# ---------- 判断是否需要全量备份 ----------
# 检查全量备份是否有效（存在 xtrabackup_checkpoints 文件）
if [ ! -f "${FULL_BACKUP_DIR}/xtrabackup_checkpoints" ]; then
    log "未找到全量备份，开始执行全量备份..."
    xtrabackup --host="$MYSQL_HOST" --port="$MYSQL_PORT" \
               --user="$MYSQL_USER" --password="$MYSQL_PASS" \
               --backup --target-dir="$FULL_BACKUP_DIR" \
               --no-timestamp >> "$LOG_FILE" 2>&1
    if [ $? -eq 0 ]; then
        log "全量备份成功，目录：$FULL_BACKUP_DIR"
    else
        log "全量备份失败，请检查日志！"
        exit 1
    fi
else
    log "已存在全量备份，开始执行增量备份..."
    
    # ---------- 查找最近一次备份目录（全量或增量） ----------
    # 获取最近修改时间的备份目录（按时间排序取最新）
    LATEST_BACKUP=$(find "$BACKUP_BASE" -maxdepth 2 -type d \
                    \( -path "$FULL_BACKUP_DIR" -o -path "$INCR_BACKUP_DIR/*" \) \
                    -name "xtrabackup_checkpoints" -printf "%T@ %h\n" 2>/dev/null \
                    | sort -nr | head -1 | cut -d' ' -f2-)
    
    if [ -z "$LATEST_BACKUP" ]; then
        log "错误：找不到任何有效的备份目录作为增量基准。"
        exit 1
    fi
    
    log "基准备份目录：$LATEST_BACKUP"
    
    # ---------- 生成增量备份目录（按日期+时间） ----------
    TODAY=$(date +%Y%m%d)
    INCR_DIR="${INCR_BACKUP_DIR}/${TODAY}_$(date +%H%M%S)"
    mkdir -p "$INCR_DIR"
    
    # ---------- 执行增量备份 ----------
    xtrabackup --host="$MYSQL_HOST" --port="$MYSQL_PORT" \
               --user="$MYSQL_USER" --password="$MYSQL_PASS" \
               --backup --target-dir="$INCR_DIR" \
               --incremental-basedir="$LATEST_BACKUP" \
               --no-timestamp >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        log "增量备份成功，目录：$INCR_DIR"
        # 清理旧备份
        cleanup_old_backups
    else
        log "增量备份失败，请检查日志！"
        exit 1
    fi
fi

log "备份流程结束。"
exit 0
```

# <font style="color:rgb(79, 79, 79);">二、delete 误删恢复：</font><font style="color:rgb(252, 85, 49);">my2sql </font><font style="color:rgb(79, 79, 79);"> 快速回滚</font>
delete 仅删除数据（表结构保留），无需全量备份，通过my2sql工具解析 Binlog 生成反向 SQL，即可快速恢复。



## 2.1 恢复核心逻辑
Binlog（Row 格式）会记录每条删除数据的完整镜像，my2sql解析该镜像生成insert反向语句，执行后即可还原数据。



## 2.2 前提条件与工具准备
必备条件

+ Binlog 格式为Row，且binlog_row_image=full；
+ 仅支持 DML 操作回滚（不支持 drop/truncate）；
+ 用户认证方式为mysql_native_password。



```sql
#Binlog 格式为Row，且binlog_row_image=full；
SHOW VARIABLES LIKE 'binlog_format';
SHOW VARIABLES LIKE 'binlog_row_image';

#用户认证方式为mysql_native_password。
SELECT User, Host, plugin FROM mysql.user;
```

<!-- 这是一张图片，ocr 内容为：SELECT USER, HOST, PLUGIN FROM MYSQL.USER; MYSGL> PLUGIN USER HOST CACHING_SHA2_PASSWORD ROOT U_BACKUP MYSQL_NATIVE_PASSWORD LOCALHOST MYSQL.INFOSCHEMA CACHING_SHA2_PASSWORD LOCALHOST MYSGL.SESSION CACHING_SHA2_PASSWORD MYSGL.SYS LOCALHOST CACHING_SHA2_PASSWORD LOCALHOST CACHING_SHA2_PASSWORD ROOT  IN SET (0.00 SEC) ROWS MYSQ1> -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1783270978963-1947b6bf-0523-4ca3-851b-128861e8e39b.png)

工具安装

```sql
wget https://github.com/liuhr/my2sql/blob/master/releases/centOS_release_7.x/my2sql
chmod +x my2sql
./my2sql -h  # 验证安装
```

## <font style="color:rgb(79, 79, 79);">2.3 实战操作步骤</font>
### <font style="color:rgb(79, 79, 79);">步骤 1：环境准备</font>
```sql
-- 1. 创建测试库表与数据
create database d_recover;
use d_recover;
CREATE TABLE del_t1 (
  id int NOT NULL AUTO_INCREMENT,
  a int NOT NULL,
  PRIMARY KEY (id)
) ENGINE=InnoDB CHARSET=utf8mb4;
insert into del_t1 values (1,1),(2,2);

-- 2. 创建解析专用用户
CREATE USER `u_rollback`@`127.0.0.1` IDENTIFIED WITH MYSQL_NATIVE_PASSWORD BY 'IgdI8G_aUU';
GRANT SELECT, REPLICATION SLAVE,REPLICATION CLIENT ON *.* TO `u_rollback`@`127.0.0.1`;
RENAME USER 'u_rollback'@'127.0.0.1' TO 'u_rollback'@'%';

```

### <font style="color:rgb(79, 79, 79);">步骤 2：模拟误操作与定位 Binlog</font>
```sql
-- 1. 模拟delete误删
delete from d_recover.del_t1;

# 2. 复制目标Binlog文件
mkdir /data/backup/rollback

mysql> SHOW BINARY LOGS;
+---------------+-----------+-----------+
| Log_name      | File_size | Encrypted |
+---------------+-----------+-----------+
| binlog.000011 |       157 | No        |
| binlog.000012 |       180 | No        |
| binlog.000013 |       180 | No        |
| binlog.000014 |      2114 | No        |
| binlog.000015 |      3234 | No        |
+---------------+-----------+-----------+
5 rows in set (0.02 sec)

 cp /data/mysql/binlog.000015 /data/backup/rollback
 
# 3. 定位delete操作位点
cd /data/backup/rollback
 mysqlbinlog binlog.000015 --start-datetime='2026-07-06 01:12:00' --stop-datetime='2026-07-06 01:15:00'   --base64-output=decode-rows -v > operation.sql
cat operation.sql | grep -A 10 -B 10 "delete from d_recover.del_t1"
# 记录start-pos（3694）与stop-pos（3805）

```

<!-- 这是一张图片，ocr 内容为：ROOT@LOCALHOST:/DATA/BACKUP/ROLLBACK X ROOT@LOCALHOST ROOT@LOCALHOST:~/MYSGL [TROOT@LOCALHOST ROLLBACK]# CAT OPERATION.SQL | GREP -A EP A 10-B 10 ''DELETE FROM #AT3614 THREAD_ID-11 #260706 1:13:36 SERVER ID 1 END_10Q-POS 3694 CRC32 0X3281BC9D ERROR_CODE-O EXEC_TIME-O QUERY SETTIMESTAMP178327161616/ BEGIN 3694 #260706 1:13:36 SERVER ID 1. END_LOG-POS 3752 CRC32 OXE6264BA4 TABLE_MAP: D_RECOVER'. DEL_TL' MAPPED TO NUMBER 99 # HAS HAS GENERATED_INVISIBLE_PRIMARY KEY-O #AT3752 #260706 1:13:36 SERVER ID 1 END_LOG-POS 3805 CRC32 OX7F8D609D DELETE_ROWS: TABLE ID 99 FLAGS: STMT_END_F ### DELETE FROM D_RECOVER . DEL_T1' 井井#WHERE @1- ### @21 并井 'D_RECOVER'. DEL_TL' ##DELETEFROM 井井#WHERE @12 并井井 AT3805 #260706 1:13:36 SERVER ID 1 END_LOQ DOS 3836 CRC32 0X927FF073 XID 70 COMMIT/*/*/; SET @@SESSION.GTIDINEXT-'AUTOMATIC'/* ADDED BY MYSQLBINLOG DELIMITER: # END OF LOG FILE /*!50003 SET COMPLETION_TYPE-@OLD_COMPLETION TYPE*/; [ROOT@LOCALHOST ROLLBACK]# -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1783271941400-d9085cbd-419e-47a3-9dd1-e9433ca1edf0.png)

### <font style="color:rgb(79, 79, 79);">步骤 3：生成并执行回滚 SQL</font>
```sql
# 1. 生成回滚SQL
cd /data/backup
mkdir recover_01
./my2sql -user u_rollback -password 'IgdI8G_aUU' -host 127.0.0.1 -databases d_recover -tables del_t1 -work-type rollback -start-file /data/backup/rollback/binlog.000015 -start-pos 3694 -stop-pos 3805 -output-dir /data/backup/recover_01

```

<!-- 这是一张图片，ocr 内容为：OLES DEL_TL -WORK-TYPE ROLLBACK -S -STA RT-FILE /DATA,BACKUD/ROLLBAEK/BINLEG.00015 -STARE-P0S 3694 -STOP-P0S 3805 -OUTPUT-DIR /BACKUD/FEEOVER 2935/07/0S   38ILA)  TIATOL BLNTERRNCER A3TER    REATE EINLOOSRNCER WITH  C330$   337:0.8.8.8.8. ND N CK UTF8 FALSE FALSE <NIL> FA ISE LOCAL FALSE O OS OS O FALSE FALSE O <NIL> OXC0000900CO OX61E040? E REDO/ROLLBACK SQL [2026/07/06 0 5 01:29:14] [INFO] EVENTS.GO:61 START THREAD 1 TO GENERATE RE [2026/07/06 01:29:14] TINFOL BINLOGSYNCER -GO:400 BEGIN TO SYIC BINLOG FROM POSITION (BINLOG.000015, 3694) [2026/07/06 01:29:14] [INFO] EV (INFO] EVENTS.GO:221 START THREAD TO WRITE REDO/ROLLBACK SQL INTO FILE 01:29:14 [2026/07/06 OJ STATS-PROCESS.GO:166 START THREAD TO ANALYZE STATISTICS FROM BINLOG [INFO] S 01:29:14] [INFOL EVENTS.GO:61 START THREAD 2 TO GENERATE REDO/ROLTBACK SQL 2026/ 5/07/06 01:29:14] 2026/07/06 CINFO] REPL.GO:25 START TO GET BINLOG FROM MYSQL [2026/07/06 01:29:14] I BINLOGSYNCER.GO:816 ROTATE TO (BINLOG.000015, 3694) CINFO] [2026/07/06 01:29:19] [INFO] REPL.GO:93 DEADLINE EXCEED. [2026/07/06 01:29:19] CINFO] REPL.GO:27 FINISH GETTING BINLOG FROM MYSQL [INFO] STATS PROCESS.GO:266 EXIT THREAD TO ANALYZE STATISTICS FROM BINLOG 2026/07/06 01:29:197 RIHFOL EVENTS.QO:196 EXIT THREAD 1 TO GENERATE REDO/ROLLBACK SQL [2026/07/06 01:29:19] [2026/07/06 01:29:19] TINFO] EVENTS.GO:196 EXIT THREAD 2 TO GENERATE REDO/ROLLBACK SQ1 O REVERT CONTENT ORDER OF TMP FILES [2026/07/06 01:29:19] [INFO] EVENTS.GO:270 FINISH WRITING ROLLBACK SQL INTO TMP FILES, START TG [2026/07/06 CINFO] RO 501:29:19] ROLLBACK-PROCESS.GO:15 START THREAD 1 TO REVERT ROLLBACK SQL FILES [2026/07/06 01:29:19] ROLLBACK_PRO [1NFO] KPROCESS.90:4L STARE TO REVERT TINP F1LE /D3T3/03CRUP/FECOVET 01183EK,35.35.301 INTO /DACKUP/RECQVER- 11BACK.15.SG CINFO] ROLLBAC [2026/07/06 01:29:19] FOL FOLLBACK DROEESS;359 FLOTALAH REVEREING FLLE / RO1LBACK.15.SQL [2026/07/05 OI;79:191 [INFOL ROLLBACK PROCESS,GO:25 EXIT THREAD 1 TO REVERT ROLLBACK SQL FILES [2026/07/06 01:29:19] [INFO] EVENTS.GO;283 FINISH REVERTING CONTENT ORDER OF TMP FILES THREAD TO WRITE REDO/ROLLBACK SQL INTO FILE [2026/07/06 01:29:19] [INFO] EVENTS.GO:288 EXIT THREAD T [ROOT@LOCALHOST MYSQ1]# -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1783272486201-3e9d8213-02cf-4ea1-ae14-95a5fa7a8a3a.png)



```sql

# 2. 验证回滚SQL（应为insert语句）
[root@localhost mysql]# ls -lrt /data/backup/recover_01
total 12
-rw-r--r-- 1 root root 107 Jul  6 01:29 biglong_trx.txt
-rw-r--r-- 1 root root 288 Jul  6 01:29 binlog_status.txt
-rw-r--r-- 1 root root 116 Jul  6 01:29 rollback.15.sql
[root@localhost mysql]# cat /data/backup/recover_01/rollback.15.sql 
INSERT INTO `d_recover`.`del_t1` (`id`,`a`) VALUES (2,2);
INSERT INTO `d_recover`.`del_t1` (`id`,`a`) VALUES (1,1);

# 3. 执行回滚
[root@localhost mysql]# mysql -uroot -peversec123098 </data/backup/recover_01/rollback.15.sql
mysql: [Warning] Using a password on the command line interface can be insecure.
[root@localhost mysql]# 

# 4. 验证结果
mysql> select * from d_recover.del_t1;
+----+---+
| id | a |
+----+---+
|  1 | 1 |
|  2 | 2 |
+----+---+
2 rows in set (0.00 sec)
```







# <font style="color:rgb(31, 35, 40);">my2sql重要参数说明</font>
<font style="color:rgb(31, 35, 40);">-U</font>

```plain
优先使用unique key作为where条件，默认false
```

<font style="color:rgb(31, 35, 40);">-模式</font>

```plain
repl: 伪装成从库解析binlog文件，file: 离线解析binlog文件, 默认repl
```

<font style="color:rgb(31, 35, 40);">本地二进制日志文件</font>

```plain
当指定-mode=file 参数时，需要指定-local-binlog-file binlog文件相对路径或绝对路径,可以连续解析多个binlog文件，只需要指定起始文件名，程序会自动持续解析下个文件
```

<font style="color:rgb(31, 35, 40);">-add-extraInfo</font>

```plain
是否把database/table/datetime/binlogposition...信息以注释的方式加入生成的每条sql前，默认false
```

```plain
# datetime=2020-07-16_10:44:09 database=orchestrator table=cluster_domain_name binlog=mysql-bin.011519 startpos=15552 stoppos=15773
UPDATE `orchestrator`.`cluster_domain_name` SET `last_registered`='2020-07-16 10:44:09' WHERE `cluster_name`='192.168.1.1:3306'
```

<font style="color:rgb(31, 35, 40);">-big-trx-row-limit n</font>

```plain
transaction with affected rows greater or equal to this value is considerated as big transaction 
找出满足n条sql的事务，默认500条
```

<font style="color:rgb(31, 35, 40);">数据库、表</font>

```plain
库及表条件过滤, 以逗号分隔
```

<font style="color:rgb(31, 35, 40);">-sql</font>

```plain
要解析的sql类型，可选参数insert、update、delete，默认全部解析
```

<font style="color:rgb(31, 35, 40);">-doNotAddPrifixDb</font>

```plain
Prefix table name witch database name in sql,ex: insert into db1.tb1 (x1, x1) values (y1, y1)
默认生成insert into db1.tb1 (x1, x1) values (y1, y1)类sql，也可以生成不带库名的sql
```

<font style="color:rgb(31, 35, 40);">每表文件数</font>

```plain
为每个表生成一个sql文件
```

<font style="color:rgb(31, 35, 40);">-全列</font>

```plain
For update sql, include unchanged columns. for update and delete, use all columns to build where condition.
default false, this is, use changed columns to build set part, use primary/unique key to build where condition
生成的sql是否带全列信息，默认false
```

<font style="color:rgb(31, 35, 40);">-ignorePrimaryKeyForInsert</font>

```plain
生成的insert语句是否去掉主键，默认false
```

<font style="color:rgb(31, 35, 40);">输出目录</font>

```plain
将生成的结果存放到制定目录
```

<font style="color:rgb(31, 35, 40);">-输出到屏幕</font>

```plain
将生成的结果打印到屏幕，默认写到文件
```

<font style="color:rgb(31, 35, 40);">线程</font>

```plain
线程数，默认8个
```

<font style="color:rgb(31, 35, 40);">工作类型</font>

```plain
2sql：生成原始sql，rollback：生成回滚sql，stats：只统计DML、事务信息
```

# <font style="color:rgb(31, 35, 40);">my2sql使用案例</font>
### <font style="color:rgb(31, 35, 40);">解析出标准SQL</font>
#### <font style="color:rgb(31, 35, 40);">根据时间点解析出标准SQL</font>
```plain
#伪装成从库解析binlog
./my2sql  -user root -password xxxx -host 127.0.0.1   -port 3306 -mode repl -work-type 2sql  -start-file mysql-bin.011259  -start-datetime "2020-07-16 10:20:00" -stop-datetime "2020-07-16 11:00:00" -output-dir ./tmpdir
#直接读取binlog文件解析
./my2sql  -user root -password xxxx -host 127.0.0.1   -port 3306 -mode file -local-binlog-file ./mysql-bin.011259  -work-type 2sql  -start-file mysql-bin.011259  -start-datetime "2020-07-16 10:20:00" -stop-datetime "2020-07-16 11:00:00" -output-dir ./tmpdir
```

#### <font style="color:rgb(31, 35, 40);">根据pos点解析出标准SQL</font>
```plain
#伪装成从库解析binlog
./my2sql  -user root -password xxxx -host 127.0.0.1   -port 3306 -mode repl  -work-type 2sql  -start-file mysql-bin.011259  -start-pos 4 -stop-file mysql-bin.011259 -stop-pos 583918266  -output-dir ./tmpdir
#直接读取binlog文件解析
./my2sql  -user root -password xxxx -host 127.0.0.1   -port 3306  -mode file -local-binlog-file ./mysql-bin.011259  -work-type 2sql  -start-file mysql-bin.011259  -start-pos 4 -stop-file mysql-bin.011259 -stop-pos 583918266  -output-dir ./tmpdir
```

### <font style="color:rgb(31, 35, 40);">解析出回滚SQL</font>
#### <font style="color:rgb(31, 35, 40);">根据时间点解析出回滚SQL</font>
```plain
#伪装成从库解析binlog
./my2sql  -user root -password xxxx -host 127.0.0.1   -port 3306 -mode repl -work-type rollback  -start-file mysql-bin.011259  -start-datetime "2020-07-16 10:20:00" -stop-datetime "2020-07-16 11:00:00" -output-dir ./tmpdir
#直接读取binlog文件解析
./my2sql  -user root -password xxxx -host 127.0.0.1   -port 3306  -mode file -local-binlog-file ./mysql-bin.011259 -work-type rollback  -start-file mysql-bin.011259  -start-datetime "2020-07-16 10:20:00" -stop-datetime "2020-07-16 11:00:00" -output-dir ./tmpdir
```

#### <font style="color:rgb(31, 35, 40);">根据pos点解析出回滚SQL</font>
```plain
#伪装成从库解析binlog
./my2sql  -user root -password xxxx -host 127.0.0.1   -port 3306 -mode repl -work-type rollback  -start-file mysql-bin.011259  -start-pos 4 -stop-file mysql-bin.011259 -stop-pos 583918266  -output-dir ./tmpdir
#直接读取binlog文件解析
./my2sql  -user root -password xxxx -host 127.0.0.1   -port 3306   -mode file -local-binlog-file ./mysql-bin.011259  -work-type rollback  -start-file mysql-bin.011259  -start-pos 4 -stop-file mysql-bin.011259 -stop-pos 583918266  -output-dir ./tmpdir
```

### <font style="color:rgb(31, 35, 40);">统计DML以及大事</font>
#### <font style="color:rgb(31, 35, 40);">统计时间范围各个表的DML操作数量，统计一个事务大于500条、时间大于300秒的事务</font>
```plain
#伪装成从库解析binlog
./my2sql  -user root -password xxxx -host 127.0.0.1   -port 3306  -mode repl -work-type stats  -start-file mysql-bin.011259  -start-datetime "2020-07-16 10:20:00" -stop-datetime "2020-07-16 11:00:00"  -big-trx-row-limit 500 -long-trx-seconds 300   -output-dir ./tmpdir
#直接读取binlog文件解析
./my2sql  -user root -password xxxx -host 127.0.0.1   -port 3306 -mode file -local-binlog-file ./mysql-bin.011259   -work-type stats  -start-file mysql-bin.011259  -start-datetime "2020-07-16 10:20:00" -stop-datetime "2020-07-16 11:00:00"  -big-trx-row-limit 500 -long-trx-seconds 300   -output-dir ./tmpdir
```

#### <font style="color:rgb(31, 35, 40);">统计一段pos点范围各个表的DML操作数量，统计一个事务大于500条、时间大于300秒的事务</font>
```plain
#伪装成从库解析binlog
./my2sql  -user root -password xxxx -host 127.0.0.1   -port 3306  -mode repl -work-type stats  -start-file mysql-bin.011259  -start-pos 4 -stop-file mysql-bin.011259 -stop-pos 583918266  -big-trx-row-limit 500 -long-trx-seconds 300   -output-dir ./tmpdir
#直接读取binlog文件解析
./my2sql  -user root -password xxxx -host 127.0.0.1   -port 3306 -mode file -local-binlog-file ./mysql-bin.011259  -work-type stats  -start-file mysql-bin.011259  -start-pos 4 -stop-file mysql-bin.011259 -stop-pos 583918266  -big-trx-row-limit 500 -long-trx-seconds 300   -output-dir ./tmpdir
```

### <font style="color:rgb(31, 35, 40);">从某一个pos点解析出标准SQL，并且打印到屏幕</font>
```plain
#伪装成从库解析binlog
./my2sql  -user root -password xxxx -host 127.0.0.1   -port 3306 -mode repl  -work-type 2sql  -start-file mysql-bin.011259  -start-pos 4   -output-toScreen
```

  
 


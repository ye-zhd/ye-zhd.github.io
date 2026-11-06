# 1.部署jenkins
## <font style="color:rgb(79, 79, 79);">1.</font><font style="color:rgb(78, 161, 219) !important;">设置宿主机目录权限，方便于容器映射</font>
<font style="color:rgb(28, 29, 31);">说明: 下面将会介绍两种挂载的方式</font>

+ <font style="color:rgb(28, 29, 31);">第一种 在宿主主机 安装好java环境、maven环境（PS：请提前配置好settings.xml 仓库目录为 </font>`<font style="color:rgb(28, 29, 31);background-color:rgb(246, 247, 250);">/mydata/maven/repository</font>`<font style="color:rgb(28, 29, 31);">），启动容器时挂载到容器内部，在jenkins配置时无需额外的自动安装java环境、maven环境，只需要指定java、maven目录即可（因为已经通过宿主主机挂载到容器内部，即使删除容器也不用担心数据丢失的问题）</font>

<font style="color:rgb(105, 111, 120);background-color:rgb(246, 247, 250);"></font>

```plain
mkdir -p /mydata/jenkins                    #在宿主主机中创建挂载jenkins工作目录
mkdir -p /mydata/maven/repository           #在宿主主机中创建挂载maven仓库目录
chown -R 1000:1000 /mydata/jenkins          #授予权限
chown -R 1000:1000 /mydata/maven/repository
chown -R 1000:1000 /usr/local/src/jdk/jdk1.8/
chown -R 1000:1000 /usr/local/apache-maven-3.8.6/
```

<font style="color:rgb(105, 111, 120);">命令说明：需要修改映射的目录权限，因为当映射本地数据卷时，/mydata/jenkins/目录的拥有者为root用户， 而容器中jenkins用户的 uid 为 1000。</font>

+ <font style="color:rgb(28, 29, 31);">第二种 在jenkins容器中（自动安装java环境、maven环境)，启动容器时挂载到宿主主机目录（避免数据丢失）</font>

<font style="color:rgb(105, 111, 120);background-color:rgb(246, 247, 250);"></font>

```plain
mkdir -p /mydata/jenkins                    #在宿主主机中创建挂载jenkins工作目录
chown -R 1000:1000 /mydata/jenkins          #授予权限
```

<font style="color:rgb(105, 111, 120);">命令说明: 参考第一种 在宿主主机中创建挂载容器jenkins工作目录，目录中的所有文件都会自动挂载到宿主主机中。 容器jenkins工作目录简单介绍:</font>

+ `<font style="color:rgb(105, 111, 120);background-color:rgb(246, 247, 250);">/var/jenkins_home/tools</font>`<font style="color:rgb(105, 111, 120);"> 自动安装插件</font>
+ `<font style="color:rgb(105, 111, 120);background-color:rgb(246, 247, 250);">/var/jenkins_home/.m2/repository</font>`<font style="color:rgb(105, 111, 120);"> 自动下载maven依赖jar</font>

## <font style="color:rgb(79, 79, 79);">2. 创建 </font><font style="color:rgb(78, 161, 219) !important;">docker-compose</font><font style="color:rgb(79, 79, 79);">.yml</font>
   
<font style="color:rgb(28, 29, 31);">第一种 需要宿主主机自备maven环境、java环境，安装过程略，提前配置settings.xml </font>`<font style="color:rgb(28, 29, 31);background-color:rgb(246, 247, 250);">/mydata/maven/repository</font>`<font style="color:rgb(28, 29, 31);"> 仓库目录地址</font>

```shell
version: '3' #指定版本
services:    #服务根节点
  jenkins:   #jenkins服务/其他服务（web服务/nginx服务等）
    image: jenkins/jenkins:lts  #jenkins镜像，如果镜像容器没有会去自动拉取
    container_name: jenkins     #容器的名称
    user: root                  #容器使用的用户
    #user: 1000:993             #uid=1000(daizhao) gid=1000(daizhao) 组=1000(daizhao),993(docker) 使用uid代替username 避免报错Error response from daemon: unable to find user ubuntuu: no matching entries in passwd file
    privileged: true            #授予root权限  
    restart: always             #跟随docker的启动而启动
    environment:                #设置命令执行的环境变量
        JAVA_OPTS: '-Djava.util.logging.config.file=/var/jenkins_home/log.properties'  #设置Java运行时JVM所需参数变量，修改日志输出的格式
    volumes:                    #挂载卷命令
      - /mydata/jenkins/:/var/jenkins_home                              #将默认/var/jenkins_home 挂载到宿主主机上 /data/jenkins/
      - /usr/local/apache-maven-3.8.6:/usr/local/apache-maven-3.8.6     #宿主主机maven挂载到容器目录上
      - /mydata/maven/repository:/mydata/maven/repository               #宿主主机maven仓库目录挂载到容器目录上
      - /usr/local/java/jdk1.8.0_341:/usr/local/java/jdk1.8.0_341       #宿主主机jdk挂载到容器目录上
      - /var/run/docker.sock:/var/run/docker.sock
      - /etc/localtime:/etc/localtime                                  #同步时间
      - /usr/bin/docker:/usr/bin/docker
      - /usr/lib/x86_64-linux-gnu/libltdl.so.7:/usr/lib/x86_64-linux-gnu/libltdl.so.7
    ports:
      - 8088:8080    #映射容器端口8080 到 宿主机端口8080
    expose:          #暴露给其他容器、link的端口号
      - 8080
      - 50000
```

   
<font style="color:rgb(28, 29, 31);">第二种 在jenkins容器中（自动安装java环境、maven环境)，启动容器时挂载到宿主主机目录（避免数据丢失）</font>

```shell
version: '3' #指定版本
services:    #服务根节点
  jenkins:   #jenkins服务/其他服务（web服务/nginx服务等）
    image: swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/jenkins/jenkins:2.570  #jenkins镜像，如果镜像容器没有会去自动拉取
    container_name: jenkins     #容器的名称
    user: root                  #容器使用的用户
    #user: 1000:993                #uid=1000(daizhao) gid=1000(daizhao) 组=1000(daizhao),993(docker) 使用uid代替username 避免报错Error response from daemon: unable to find user ubuntuu: no matching entries in passwd file
    privileged: true            #授予root权限  
    restart: always             #跟随docker的启动而启动
    environment:                #设置命令执行的环境变量
        JAVA_OPTS: '-Djava.util.logging.config.file=/var/jenkins_home/log.properties'  #设置Java运行时JVM所需参数变量，修改日志输出的格式
    volumes:                    #挂载卷命令
      - /data/jenkins/:/var/jenkins_home                             #将默认/var/jenkins_home 挂载到宿主主机上 /data/jenkins/
      - /var/run/docker.sock:/var/run/docker.sock
      - /etc/localtime:/etc/localtime                                  #同步时间
      - /usr/bin/docker:/usr/bin/docker
    #  - /usr/lib/x86_64-linux-gnu/libltdl.so.7:/usr/lib/x86_64-linux-gnu/libltdl.so.7
    ports:
      - 8088:8080    #映射容器端口8080 到 宿主机端口8080
    expose:          #暴露给其他容器、link的端口号
      - 8080
      - 50000
```



<font style="color:rgb(28, 29, 31);">docker-compose up -d #后台运行</font>

<font style="color:rgb(28, 29, 31);"></font>

访问：[http://10.20.3.111:8088/](http://10.20.3.111:808/)

<!-- 这是一张图片，ocr 内容为：10.20.3.11:8088/LOGIN?FROM%2F 不安全 谷歌浏览器CHROM... 'PORTAINER'客器镜... DEVOPS工具链:C.............  DEVOPS 工具链:C..........   HARBORTAINER 从零搭建企业级CI/... PNG转PDF ESXI-01.20.3.1 V... MYSQL数据误删恢... -在... MAFEIFAN的编程技... WWW.32R.COM 入门 解锁JENKINS 为了确保管理员安全地安装JENKINS,密码已写入到日志中(不知道在哪里?)该文件在 服务器上: /VAR/JENKINS HOME/SECRETS/INITIALADMINPASSWORD 请从本地复制密码并粘贴到下面. 管理员密码 继续 -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1785140763460-62993932-1a0a-488c-b64b-0792c473a36f.png)

```shell

[root@localhost jenkins]# cat /data/jenkins/secrets/initialAdminPassword
cee5bd90a1484d79bb1bd9a230b7d120
[root@localhost jenkins]# 
```



我是外网连接点击

<!-- 这是一张图片，ocr 内容为： -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1785144301765-8a615624-b439-4723-9258-550fb8339a6a.png)

插件安装后执行



<!-- 这是一张图片，ocr 内容为：新于八 创建第一个管理员用户 用户名 ADMIN 密码 确认密码 全名 YE EMAIL 2437714134@QQ.COM 使用ADMIN账户继续 保存并完成 JENKINS 2.570 -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1785144345220-fdf1ee9b-b360-4772-bb88-1bd84f889795.png)



<font style="color:rgb(60, 60, 67);">修改时区</font>

<font style="color:rgb(60, 60, 67);">在【系统管理】-【脚本命令行】里运行</font><font style="color:rgb(60, 60, 67);"> </font>`<font style="color:rgb(52, 81, 178);background-color:rgba(142, 150, 170, 0.14);">System.setProperty('org.apache.commons.jelly.tags.fmt.timeZone', 'Asia/Shanghai')</font>`

<!-- 这是一张图片，ocr 内容为：JENKINS 脚本命令行 MANAGE JENKINS SCRIPT CONSOLE TYPE IN AN ARBLTRARY GROOVY SCRPT AND EXECUTE IT ON THE SERVER USEFUL FOR TROOTING AND DIAGNOSTICS GETTING STARTED IMPORTED. PRINTIN(JENKINS.INSTANCE.PLUGINMANAGER.PLUGINS) CONSOLE PRINTLN(JENKINS.INSTANCE.PLUGINHANAGER.PLUGINS) 运行 RESULT -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1785146838826-62264eeb-8d7f-4b70-a28d-41f4427a76f3.png)

<font style="color:rgb(60, 60, 67);">修改Jenkins插件为国内源</font>

<font style="color:rgb(60, 60, 67);">首页 --> configure --> Manage Jenkins --> Advanced --> Update Site（页面最下方‘升级站点’）</font>

<font style="color:rgb(60, 60, 67);">替换URL为 仓库地址：</font>

[<font style="color:rgb(52, 81, 178);">https://updates.jenkins.io/update-center.json</font>](https://updates.jenkins.io/update-center.json)<font style="color:rgb(60, 60, 67);"> 改为 </font>[https://update.dev6.site/jenkins/updates/update-center.json](https://update.dev6.site/jenkins/updates/update-center.json)

<font style="color:rgb(60, 60, 67);">如果插件页面为空，把https改为http</font>

<!-- 这是一张图片，ocr 内容为：10.20.3.11:8088/MANAGE/PLUGINMANAGER/ADVANCED 门 请求取行动 A不安全 脂 口新有书 PNG转PDF--在... 名DEVOPS工具链:C.HARBOR 答题放宽落 CHROM 从零搭建企业袋CV.... 'PORTAINER'容器牌...金 DEV MYSQL数据洪测饮... 32 WWW.324.COM MAFEIFAN 的输程技... JENKINS MANAGE JENKINS 插件管理 PLUGINS ADVANCED SETTINGS UPDATES 部署插件 AVALLABLE PLUGINS 您可以从本地系统中选择一个插件文件,或者提供一个URL从中央插件含库以外的位否安装插件. INSTALLED PLUGINS 文件 ADVANCED SETTINGS 未选择任何文件 选择文件 三 DOWNLOAD PROGRESS OR URL 脂肪 升级站点 URL HTTPS//UPDATES.JENKINS.LO/UPDATE-CENTERJSON 提交 JENKINS 中文社区 LENKINS 2.570 REST API -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1785144700314-94e6f1d1-a06c-4b25-ba85-b7fc2c4ccd16.png)





# jenkins的使用
## <font style="color:rgb(60, 60, 67);">Jenkinsfile 是什么</font>
<font style="color:rgb(60, 60, 67);">Jenkinsfile就是一个文本文件，也就是部署流水线概念在Jenkins中的表现形式。像Dockerfile之于Docker。所有部署流水线的逻辑都写在Jenkinsfile中。 建议把Jenkinsfile跟项目源码一块加入到版本控制中，这样方便项目成员了解构建构建和流程。当然出于安全，有些环境变量和参数等可以管理在Jenkins管理平台上。具体后续会有介绍。</font>

## <font style="color:rgb(60, 60, 67);">pipeline 基本构成</font>
<font style="color:rgb(60, 60, 67);">写 pipeline 就是写 Groovy 代码，Jenkins pipeline 其实就是基于Groovy语言实现的一种领域DSL(Domain Specific Language)。</font>

<font style="color:rgb(60, 60, 67);">Jenkins pipeline支持两种语法，声明式和脚本式，前者简单，结构化好，后者灵活，扩展性好，但是需要对Groovy比较熟练。 声明式语法更符合阅读习惯，所有示例都会使用声明式语法。</font>

<font style="color:rgb(60, 60, 67);">pipeline的内容包含执行编译、打包、测试、输出测试报告等步骤。</font>

<font style="color:rgb(60, 60, 67);">如下图，声明式pipeline的语法结构概览，粗线边框的表示必需的</font>

<!-- 这是一张图片，ocr 内容为： -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1785146992552-773b6bbb-c214-4652-9d93-d7c87a28cab8.png)

<font style="color:rgb(60, 60, 67);">下面新建一个最简单的声明式pipeline</font>

<!-- 这是一张图片，ocr 内容为：品 ESXI-01.20.3.1-V.. 谷歌浏克器CHROM... 从零搭建企业级CI/... PNG转PDF PORTAINER'容器镜.... DEVOPS 工具链: MYSQL数据误删恢... WWW.32R.COM HAROOR JENKINS ALL 新建LTEM 新建LTEM JENKINS 点击新建 输入一个任务名称 新建LTEM HELLO WORLD 构建历史 SELECT AN NITEM TYPE 流水线 构建队列 L 精心地组织一个可以长明运行在多个节点上的任务.适用于构建流水线(更加正式地应当称为工作)) 队列中没有构建任务 流),增加或者组织难以采用自由风格的任务类型. 构建执行状态 0/2 FREESTYLE PROJECT CLASSIC, GENERAL-PURPOSE JOB TYPE THAT CHECKS OUT FROM UP TO ONE SCM, EXECUTES BUILD STEPS SERIALLY, FOLLOWED BY POST-BUILD STEPS LIKE ARCHIVING ARTIFACTS AND SENDING EMALL NOTIFICATIONS. 构建一个多配置项目 适用于多配置项目,例如多环境测试,平台指定构建,等等, {0]文件夹 用铺 CREATES A SET OF MULTIBRANCH PROJECT SUBFOLDERS BY SCANNING FOR REPOSITORIES. 多分支流水线 根据一个SCM仓库中检测到的分支创建一系列流水线. 文件夹 创建一个可以嵌套存储的容器.利用它可以进行分组.视图仅仅是一个过滤器,而文件夹则是一个独立 的命名空间,因此你可以有多个相同名称的的内容,只要它们在不同的文件夹里即可. 复制 如果你想根据一个已经存在的任务创建,可以使用这个选项 确定 -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1785146582432-8924b2e1-82d3-4952-aa2c-9dbe0e106796.png)

```shell
pipeline {
    agent any
       // stages 包含一个或多个阶段(stage)的容器
    stages {
         // stage 阶段，pipleline流水线由一个或多个阶段(stage)组成，每个阶段必须有名称，这里build就是此阶段的名称
        stage('build') {
               // steps，阶段中的一个或多个具体步骤(step)的容器
            steps {
                     // 这是是具体的步骤，真正做事的，不可再拆分的最小操作
                echo "hello world"
            }
        }
        stage('end') {
            steps {
                echo "end"
            }
        }
    }
}
```

<!-- 这是一张图片，ocr 内容为：STAGES #5 RERUN TOOK0.45秒 STARTEDBYYESTARTED 10分AGO END START O O END BUILD JENKINS STARTED <1S AGO 44MS BUILD SEARCH SMS -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1785147070510-ebd36ff8-f8b4-4558-9c83-8f86e41595d6.png)

## Groovy语法介绍
<font style="color:rgb(60, 60, 67);">写 pipeline 就是写 Groovy 代码，Jenkins pipeline 其实就是基于Groovy语言实现的一种DSL。 了解一些Groovy语法知识是很有必要的</font>

<font style="color:rgb(60, 60, 67);">Groovy是一门同时具有静态和动态特定的脚本语言，或者胶水语言，也是面向对象的。非常适合编写简洁容易的自动化测试代码，例如我再次强调的pipeline的构建任务，就是一个典型的使用领域。</font>

<font style="color:rgb(60, 60, 67);">Groovy是apache下的一个产品，所以叫Apache Groovy，官网地址是</font>[<font style="color:rgb(52, 81, 178);">http://groovy-lang.org/</font>](http://groovy-lang.org/)

<font style="color:rgb(60, 60, 67);">Groovy是由 James Strachan 设计，第一个发布版本在2003年。</font>

<font style="color:rgb(60, 60, 67);">核心特点就是Java平台的多面语言，下面特点就是描述这个多面。</font>

<font style="color:rgb(60, 60, 67);">Flat learning curve</font>

+ <font style="color:rgb(60, 60, 67);">直接翻译就是平坦的学习曲线，什么可读性强，简洁，表达性强的，易于Java开发人员学习的编程语言。</font>

<font style="color:rgb(60, 60, 67);">Powerful features</font>

+ <font style="color:rgb(60, 60, 67);">功能强大，支持闭包，构建器，运行时和编译时元编程，函数编程，类型推断和静态编译。</font>

<font style="color:rgb(60, 60, 67);">Smooth Java integration</font>

+ <font style="color:rgb(60, 60, 67);">就是无缝和Java集成，Java的语法Groovy都支持。</font>

<font style="color:rgb(60, 60, 67);">Domain-Specific Languages</font>

+ <font style="color:rgb(60, 60, 67);">特定领域语言，灵活的语法，高度集成和自定义机制。这个我使用来看，由于Jenkins平台Pipeline插件是采用Groovy开发，在特定领域语言，我认为就是指pipeline。</font>

<font style="color:rgb(60, 60, 67);">Vibrant and rich ecosystem</font>

+ <font style="color:rgb(60, 60, 67);">充满活力和丰富的生态系统，这个，我学习比较基础，理解不了。在测试工具中，有一个很强大的框架spcok就能测试Java和groovy开发的项目，这个我认为是一个生态。</font>

```shell
pipeline {
    agent any
    stages {
        stage('debug-列出所有环境变量') {
            steps {
                sh "printenv | sort"
            }
        }
        stage('Example') {
            steps {
                echo "Running ${BUILD_NUMBER} on ${JENKINS_URL}"
                echo "Job: ${JOB_NAME}, Build ID: ${BUILD_ID}"
            }
        }
    }
}
```

<!-- 这是一张图片，ocr 内容为：JENKINS UC-HTTPS://UPDATES.JENKINS.IO JENKINS UC EXPERIMENTAL-HTTPS://UPDATES.JENKINS.IO/EXPERIMENTAL JENKINS URL-HTTP://10.20.3.111:8088/ JENKINS VERSION-2.570 JOB BASE NAME-GROOVY 308 DISPLAY URL-HTTP://10.20.3.111:8088/JOB/GROOVY/DISPLAY/REDIRECT JOB NAME-GROOVY JOB_URL-HTTP://10.20.3.111:8088/JOB/GROOVY/ LANGC.UTF-8 NODE_LABELS-BUILT-IN NODE NAME-BUILT-IN PATH:/OPT/JAVA/OPENJAK/DIN://USR/10CAL/SBIN://US/1OCAL/BIN://USR/SBIN;/USR/BIN://5BIN;/BIN PWD-/VAR/JENKINS HOME/WORKSPACE/GROOVY REF-/USR/SHARE/JENKINS/REF RUN ARTIFACTS DISPLAY URL-HTTP;//10:20.3,111:3088/ 3088/GROOVY/6/DISPLAY/REDIRECTYPAGE-ARTIFACTS RUN CHANGES DISPLAY URL-HTTP://10.20.3.111:8088/JOB/GROOVY/6ROOVY/5/DISPLAY/RECT?PAGE:CHANGES RUN DISPLAY URL-HTTP://1E.20.3.111:8088/JOB/GROOVY/6/DISPLAY/REDIRECT RUNL TESTS.DISPLAY URL-HTTP://10.20.3.111:8088/JOB/GROOVY/6/DISPLAY/REDIRECT3PAGEZTESTS SHLVL0 STAGE NAME-DEBUG-列出所有环境变量 WORKSPACE-/VAR/JENKINS HOME/WORKSPACE/GROOVY WORKSPACE TMP-/VAR/JENKINS HOME/WORKSPACE/GROOVY@TMP [PIPELINE]] [PIPELINE]// STAGE [PIPELINE] STAGE [PIPELINE]{(EXAMPLE) [PIPELINE] ECHO RUNNING 6 ON HTTP://10.20.3.111:8088/ [PIPELINE] ECHO JOB:GROOVY,BUILD ID:6 [PIPELINE]] [PIPELINE] // STAGE [PIPELINE]] [PIPELINE]// NODE [PIPELINE] END OF PIPELINE FINISHED: SUCCESS -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1785150585640-1a4019cd-8101-460a-8f4d-6e3468ed855a.png)





## 配置ssh-cred
### <font style="color:rgb(15, 17, 21);">1：准备 SSH 密钥对</font>
**<font style="color:rgb(15, 17, 21);">1.登录目标服务器</font>**<font style="color:rgb(15, 17, 21);">，执行以下命令生成密钥对（如果已有则可跳过）：</font>

`<font style="color:rgb(15, 17, 21);">ssh-keygen -t rsa -b 4096</font>`

<font style="color:rgb(15, 17, 21);">执行后，一路按回车键，使用默认路径（</font>`<font style="color:rgb(15, 17, 21);background-color:rgb(235, 238, 242);">~/.ssh/id_rsa</font>`<font style="color:rgb(15, 17, 21);">）即可。</font>

**<font style="color:rgb(15, 17, 21);">2.将公钥添加到授权列表</font>**<font style="color:rgb(15, 17, 21);">，这样 Jenkins 才能免密登录：</font>

`<font style="color:rgb(15, 17, 21);">cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys</font>`

**<font style="color:rgb(15, 17, 21);">3.查看并复制私钥内容</font>**<font style="color:rgb(15, 17, 21);">，这是下一步需要在 Jenkins 中配置的：</font>

`<font style="color:rgb(15, 17, 21);">cat ~/.ssh/id_rsa</font>`

<font style="color:rgb(15, 17, 21);">复制终端输出的全部内容，包括 </font>`<font style="color:rgb(15, 17, 21);background-color:rgb(235, 238, 242);">-----BEGIN OPENSSH PRIVATE KEY-----</font>`<font style="color:rgb(15, 17, 21);"> 和 </font>`<font style="color:rgb(15, 17, 21);background-color:rgb(235, 238, 242);">-----END OPENSSH PRIVATE KEY-----</font>`<font style="color:rgb(15, 17, 21);">。</font>

### <font style="color:rgb(15, 17, 21);">2：在 Jenkins 中添加凭证</font>
1. **<font style="color:rgb(15, 17, 21);">进入凭据管理页面</font>**<font style="color:rgb(15, 17, 21);">：</font>
    - <font style="color:rgb(15, 17, 21);">在 Jenkins 主页，点击左侧菜单的</font><font style="color:rgb(15, 17, 21);"> </font>**<font style="color:rgb(15, 17, 21);">“系统管理”</font>**<font style="color:rgb(15, 17, 21);"> </font><font style="color:rgb(15, 17, 21);">(Manage Jenkins)。</font>
    - <font style="color:rgb(15, 17, 21);">找到并点击</font><font style="color:rgb(15, 17, 21);"> </font>**<font style="color:rgb(15, 17, 21);">“凭据”</font>**<font style="color:rgb(15, 17, 21);"> </font><font style="color:rgb(15, 17, 21);">(Credentials)。</font>
    - <font style="color:rgb(15, 17, 21);">在 “Stores scoped to Jenkins” 下，点击</font><font style="color:rgb(15, 17, 21);"> </font>**<font style="color:rgb(15, 17, 21);">“系统”</font>**<font style="color:rgb(15, 17, 21);"> </font><font style="color:rgb(15, 17, 21);">(System)。</font>
    - <font style="color:rgb(15, 17, 21);">点击</font><font style="color:rgb(15, 17, 21);"> </font>**<font style="color:rgb(15, 17, 21);">“全局凭据”</font>**<font style="color:rgb(15, 17, 21);"> </font><font style="color:rgb(15, 17, 21);">(Global credentials)。</font>
2. **<font style="color:rgb(15, 17, 21);">添加新凭据</font>**<font style="color:rgb(15, 17, 21);">：</font>
    - <font style="color:rgb(15, 17, 21);">点击左侧的</font><font style="color:rgb(15, 17, 21);"> </font>**<font style="color:rgb(15, 17, 21);">“添加凭据”</font>**<font style="color:rgb(15, 17, 21);"> </font><font style="color:rgb(15, 17, 21);">(Add Credentials)。</font>
3. **<font style="color:rgb(15, 17, 21);">填写凭证信息</font>**<font style="color:rgb(15, 17, 21);">：</font>
    - **<font style="color:rgb(15, 17, 21);">类型 (Kind)</font>**<font style="color:rgb(15, 17, 21);">：在下拉菜单中选择</font><font style="color:rgb(15, 17, 21);"> </font>**<font style="color:rgb(15, 17, 21);">“SSH Username with private key”</font>**<font style="color:rgb(15, 17, 21);"> </font><font style="color:rgb(15, 17, 21);">(SSH 用户名和私钥)。</font>
    - **<font style="color:rgb(15, 17, 21);">作用域 (Scope)</font>**<font style="color:rgb(15, 17, 21);">：保持默认的</font><font style="color:rgb(15, 17, 21);"> </font>**<font style="color:rgb(15, 17, 21);">“全局”</font>**<font style="color:rgb(15, 17, 21);"> </font><font style="color:rgb(15, 17, 21);">(Global)。</font>
    - **<font style="color:rgb(15, 17, 21);">ID</font>**<font style="color:rgb(15, 17, 21);">：填写一个</font>**<font style="color:rgb(15, 17, 21);">唯一且有意义</font>**<font style="color:rgb(15, 17, 21);">的 ID，例如</font><font style="color:rgb(15, 17, 21);"> </font>`<font style="color:rgb(15, 17, 21);background-color:rgb(235, 238, 242);">ssh-cred</font>`<font style="color:rgb(15, 17, 21);">。</font>**<font style="color:rgb(15, 17, 21);">这个 ID 就是你在 Pipeline 的</font>****<font style="color:rgb(15, 17, 21);"> </font>**`**<font style="color:rgb(15, 17, 21);background-color:rgb(235, 238, 242);">credentialsId: 'ssh-cred'</font>**`**<font style="color:rgb(15, 17, 21);"> </font>****<font style="color:rgb(15, 17, 21);">中引用的值</font>**<font style="color:rgb(15, 17, 21);">。</font>
    - **<font style="color:rgb(15, 17, 21);">描述 (Description)</font>**<font style="color:rgb(15, 17, 21);">：可以填写一些描述信息，如 “用于部署到测试服务器的 SSH 密钥”。</font>
    - **<font style="color:rgb(15, 17, 21);">用户名 (Username)</font>**<font style="color:rgb(15, 17, 21);">：填写用于登录</font>**<font style="color:rgb(15, 17, 21);">目标服务器</font>**<font style="color:rgb(15, 17, 21);">的用户名，例如</font><font style="color:rgb(15, 17, 21);"> </font>`<font style="color:rgb(15, 17, 21);background-color:rgb(235, 238, 242);">root</font>`<font style="color:rgb(15, 17, 21);"> </font><font style="color:rgb(15, 17, 21);">或</font><font style="color:rgb(15, 17, 21);"> </font>`<font style="color:rgb(15, 17, 21);background-color:rgb(235, 238, 242);">deploy</font>`<font style="color:rgb(15, 17, 21);">。</font>
    - **<font style="color:rgb(15, 17, 21);">私钥 (Private Key)</font>**<font style="color:rgb(15, 17, 21);">：选择</font><font style="color:rgb(15, 17, 21);"> </font>**<font style="color:rgb(15, 17, 21);">“Enter directly”</font>**<font style="color:rgb(15, 17, 21);"> </font><font style="color:rgb(15, 17, 21);">(直接输入)，然后将你在</font>**<font style="color:rgb(15, 17, 21);">第一步</font>**<font style="color:rgb(15, 17, 21);">中复制的</font>**<font style="color:rgb(15, 17, 21);">私钥内容</font>**<font style="color:rgb(15, 17, 21);">粘贴到文本框中。</font>
    - **<font style="color:rgb(15, 17, 21);">密码短语 (Passphrase)</font>**<font style="color:rgb(15, 17, 21);">：如果你在生成密钥时设置了密码，则在此填写，否则留空。  
</font><font style="color:rgb(15, 17, 21);"> </font>

<!-- 这是一张图片，ocr 内容为：JENKINS 系统管理 凭据 凭据 ADD CREDENTIALS ADD CREDENTIALS SYSTEM-全局-GITYE-CVERTE SELECT A TYPE OF CREDENTIAL USERNAMEWITH PASSWORD 盘SYSTOM    JENKINS泄送HARBOR使用机器人张号 COMMONLY USED FOR AUTHENTICATION TO SERVICES LIKE GIT, APIS,OR REGISTRIES. STORES SCOPED TO JENKINS GITHUB APP SYSTEM SSH USERNAME WITH PRIVATE KEY SECRET FILE SECRET TEXT X.509 CLIENT CERTIFICATE CERTIFICATE UPLOAD A PKCS#12 OR PEM ENCODED CERTIFICATE AND PRIVATE KEY. NEXT -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1785292780751-11d6d3ec-ef7d-4768-9f21-43452bebb56a.png)

<!-- 这是一张图片，ocr 内容为：ADD SSH USERNAME WITH PRIVATE KEY V 范围 ? 全局(JENKINS,NODES,ITEMS,ALL CHILD ITEMS,ETC) ID? SSH-CRED ? 描述 部署到测试服务器的 SSH 密钥 USERNAME 高凭据(UNRES) ROOT TREAT USERNAME AS SECRET PRIVATE KEY ENTER DIRECTLY KEY 在下面输入新秘文 0+0OVYO4F 7+2+TMXHOXGLIJ0P1GSR8R146X+TEIZTAG1BROEBOIVRVKXESF4CZ1D OWJFDLSU +NS60032AM9WTTTDUMM9KXBJSRAV865Q+ZND+E49XP+YPVZ3YRYZJEO MCZ3MUEOA 96YG+HWP/AAQ1QCJHXPF1HXIP35/IVYFUD3X41KKW/ZNTRKXJTE6XUD WVDE1UIEG 1JRFTQKCAQAORTEF6JYEPYR30GRPIG7HPEEMAEBCKCSTB6CIPUVWWL1 CREATE -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1785292872012-377ada2e-7461-46e6-8527-812ab42af73b.png)

## 配置git-cred
### <font style="color:rgb(15, 17, 21);">配置 "Username with password" 凭证 (适用于 HTTPS)</font>
<font style="color:rgb(15, 17, 21);">如果你的 Git 仓库地址是</font><font style="color:rgb(15, 17, 21);"> </font>`<font style="color:rgb(15, 17, 21);background-color:rgb(235, 238, 242);">https://...</font>`<font style="color:rgb(15, 17, 21);"> </font><font style="color:rgb(15, 17, 21);">开头的，用这种方式</font><font style="color:rgb(15, 17, 21);">。</font>

1. **<font style="color:rgb(15, 17, 21);">选择类型</font>**<font style="color:rgb(15, 17, 21);">：在</font><font style="color:rgb(15, 17, 21);"> </font>`**<font style="color:rgb(15, 17, 21);background-color:rgb(235, 238, 242);">Kind</font>**`<font style="color:rgb(15, 17, 21);"> </font><font style="color:rgb(15, 17, 21);">下拉菜单中，选择</font><font style="color:rgb(15, 17, 21);"> </font>`**<font style="color:rgb(15, 17, 21);background-color:rgb(235, 238, 242);">Username with password</font>**`<font style="color:rgb(15, 17, 21);">。</font>
2. **<font style="color:rgb(15, 17, 21);">填写信息</font>**<font style="color:rgb(15, 17, 21);">：</font>
    - `**<font style="color:rgb(15, 17, 21);background-color:rgb(235, 238, 242);">Scope</font>**`<font style="color:rgb(15, 17, 21);">：保持默认的</font><font style="color:rgb(15, 17, 21);"> </font>`**<font style="color:rgb(15, 17, 21);background-color:rgb(235, 238, 242);">Global</font>**`<font style="color:rgb(15, 17, 21);"> </font><font style="color:rgb(15, 17, 21);">(全局)</font><font style="color:rgb(15, 17, 21);">。</font>
    - `**<font style="color:rgb(15, 17, 21);background-color:rgb(235, 238, 242);">Username</font>**`<font style="color:rgb(15, 17, 21);">：填写你的 Git 仓库用户名</font><font style="color:rgb(15, 17, 21);">。</font>
    - `**<font style="color:rgb(15, 17, 21);background-color:rgb(235, 238, 242);">Password</font>**`<font style="color:rgb(15, 17, 21);">：</font>**<font style="color:rgb(15, 17, 21);">这里是重点</font>**<font style="color:rgb(15, 17, 21);">。如果平台支持，强烈建议使用</font>**<font style="color:rgb(15, 17, 21);">个人访问令牌 (Personal Access Token, PAT)</font>**<font style="color:rgb(15, 17, 21);">，而不是你的登录密码</font><font style="color:rgb(15, 17, 21);">。</font>
    - `**<font style="color:rgb(15, 17, 21);background-color:rgb(235, 238, 242);">ID</font>**`<font style="color:rgb(15, 17, 21);">：</font>**<font style="color:rgb(15, 17, 21);">非常重要</font>**<font style="color:rgb(15, 17, 21);">！填写一个唯一且好记的 ID，例如</font><font style="color:rgb(15, 17, 21);"> </font>`<font style="color:rgb(15, 17, 21);background-color:rgb(235, 238, 242);">git-cred</font>`<font style="color:rgb(15, 17, 21);">。你将在 Pipeline 中通过这个 ID 来引用该凭证</font><font style="color:rgb(15, 17, 21);">。</font>
    - `**<font style="color:rgb(15, 17, 21);background-color:rgb(235, 238, 242);">Description</font>**`<font style="color:rgb(15, 17, 21);">：选填，可写备注。</font>
3. **<font style="color:rgb(15, 17, 21);">保存</font>**<font style="color:rgb(15, 17, 21);">：点击 </font>`**<font style="color:rgb(15, 17, 21);background-color:rgb(235, 238, 242);">确定</font>**`<font style="color:rgb(15, 17, 21);"> 完成。</font>

<font style="color:rgb(15, 17, 21);"></font>

<!-- 这是一张图片，ocr 内容为：AO 十 控者或转到... 用户设置/个人访问令牌 用户设置 用户资料 个人访问令牌 添加新令牌 8 账户 部可以为可个周围的网络和ONANAS ,的的周四等年项一个个人移两变换,型连可以使用个人海可令转通过HTTP通行93系统验话,当它来利亚河来以进G于3月,它门照项一楼安的平门 访问 PASSWORD AND 已撤销的令牌 已过期的令牌 两周内到期的令牌 活跃令牌 1 O 个人访问令牌 0 SSH密钥 筛选列表 筛选列表 筛选列表 筛选列表 GPG密钥 应用 状态 活跃X 到期时间 活跃会话 名称 生命周期 范围 用法? 状态 认证日志 &集成账户 11个月后 上次使用:42分 活跃 READ-USER,READ.REPOSTORY,READLVIRTUALREGISTRY, READ, SEFF, SEFF,VIFITE.REPOSTORY,WRITE.VIRUALREGISTR 日 电子邮件 API,A_FEATURES,CREATE.RUNNER, MANAGE_RUNNER, KBS.PROXY 7月 28,2026 通知 IP:10.20.3.111 偏好设置 回 评论模板 FEED令牌 使用配额 当您的RSSS因连锁和这个性化的ISST网通两省您的日历过用于两同两个性化日历时,您的订网令转会检验规划.它在这些新网站中可见.该宁解无运用于该同于该同对已数码 FEED令牌 将此令牌促留.任何拥有它的人都可以假您一样谈取动志并发布RSSTEEDS或您的日历LEED.如果发生,重置此令牌. -->
![](https://cdn.nlark.com/yuque/0/2026/png/34997268/1785326453142-9f86e278-f6cb-455b-86ab-39f6f6569bbc.png)


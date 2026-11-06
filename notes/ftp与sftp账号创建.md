---
title: ftp 和 sftp 账号创建记录
slug: ftp-sftp-user-setup
group: 存储与工具
date: 2026-11-06
---



# 1、背景

需要新建一个evercm 账号用来ftp或者sftp

```bash
dnf install -y vsftpd
systemctl enable --now vsftpd
目录：/data/eversec/data/ftp/evercm/autoUpgrade
账号：evercm
密码：EverSec@3141913113
```

欧拉 2203 用 dnf，centos7 换 yum，别的发型包名字差不多。

# 2、目录权限

vsftpd 登录时要一路 chdir 到家目录，中间任何一级目录没有 `o+x`，客户端就报 `500 OOPS: chdir`，而且日志里看不出是哪一级。之前查了半天，最后是 `/data/eversec` 少了执行位。

```bash
mkdir -p /data/eversec/data/ftp/evercm/autoUpgrade
chown root:root /data/eversec/data/ftp/evercm
chmod 755 /data/eversec/data/ftp/evercm
chown evercm:evercm /data/eversec/data/ftp/evercm/autoUpgrade
chmod 755 /data/eversec/data/ftp/evercm/autoUpgrade
```

家目录为什么给 root 且 755？开了 `chroot_local_user=YES` 之后，vsftpd 不允许被锁住的根目录对属主可写，否则直接 `500 OOPS: vsftpd: refusing to run with writable root inside chroot()`。要么像上面这样把写权限放到子目录，要么加 `allow_writeable_chroot=YES`，脚本里两个都做了，等于双保险。

# 3、nologin 要写进 /etc/shells

```bash
grep -qxF '/sbin/nologin' /etc/shells || echo '/sbin/nologin' >> /etc/shells
```

pam_shells 会拿用户的 shell 去 `/etc/shells` 里比对，没这一行的话密码输对了也是 `530 Login incorrect`。这个坑 ftp 和 sftp 都会踩

# 4、vsftpd.conf 重复项

需要补齐的三条：

```ini
chroot_local_user=YES
anonymous_enable=NO
allow_writeable_chroot=YES
```

# 5、建用户

```bash
useradd -d /data/eversec/data/ftp/evercm -s /sbin/nologin evercm
```

`/sbin/nologin` 是为了不给 shell 登录权限，ftp 认证走 PAM 照样能用。脚本里用 `id evercm` 判了一下，用户已存在就跳过 useradd，只把目录属主和权限重新刷一遍，所以这个脚本是幂等的，跑几次都不会出事。

# 6、改密别用 passwd

这个账号之前被人改过几次密码，PAM 里开了 remember，直接 `passwd evercm` 会撞密码历史；账户还被 faillock 锁过。所以脚本绕开交互式改密，直接写哈希：

```bash
HASH=$(openssl passwd -6 '实际密码')
usermod -p "${HASH}" evercm
faillock --user evercm --reset
[ -f /etc/security/opasswd ] && sed -i '/^evercm:/d' /etc/security/opasswd
```

`-6` 是 SHA-512，别用默认的 `-1`（md5）。`usermod -p` 吃的是哈希不是明文，`openssl passwd` 的输出带随机盐，每次都不一样，正常。

还有两个黑名单文件，`/etc/vsftpd/ftpusers` 和 `/etc/vsftpd/user_list`，里面写了谁谁就登不上，脚本里把 evercm 从这两个文件删掉了。很多时候 530 就是这里拦的，跟密码没关系。

# 7、重启验证

```bash
systemctl restart vsftpd.service
curl -sS --connect-timeout 5 -u 'evercm:实际密码' ftp://127.0.0.1/ >/dev/null && echo ok
```

curl 能列目录基本就通了。失败先看：

```bash
journalctl -u vsftpd -n 30 --no-pager
tail -f /var/log/secure
```

要是从外面连，能登录但 `ls` 一直卡住，多半是被动模式端口没放行，在配置里加 `pasv_min_port=40000`、`pasv_max_port=40100`，防火墙把这段放出去，云主机安全组也别忘。

# 8、sftp 那边

sftp 不用装新服务，走的就是 sshd，用内置的 `internal-sftp`。同一个 evercm 账号可以两个协议都用，新建一个组也行，这边直接按用户匹配：

```bash
# /etc/ssh/sshd_config 末尾追加，Match 段必须放文件最后
Match User evercm
    ChrootDirectory /data/eversec/data/ftp
    ForceCommand internal-sftp -d /evercm
    X11Forwarding no
    AllowTcpForwarding no
    PermitTTY no
```

`ChrootDirectory` 填的是 evercm 目录的上一级，登录之后落在 `/evercm` 里。sshd 对 chroot 目录的要求比 vsftpd 还死：从 `/` 到 chroot 目标每一级都必须 root 所有，group 和 other 都不能有写权限，否则连接直接被断，`sftp` 只看到一句 `Connection closed`。

```bash
chown root:root /data /data/eversec /data/eversec/data /data/eversec/data/ftp
chmod 755 /data /data/eversec /data/eversec/data /data/eversec/data/ftp
```

前面 ftp 那步刚好把 `/data/eversec/data/ftp/evercm` 设成了 root:root 755，正好满足 chroot 下家目录不可写的要求。

`-d /evercm` 是登录后切初始目录，比较新的 OpenSSH 才支持，老版本去掉这个参数，客户端进去自己 `cd evercm`。`/sbin/nologin` 在 sftp 这边也能过，因为 `ForceCommand` 根本不启 shell，加上第 3 步已经把它写进 `/etc/shells`，PAM 不会拦。

```bash
sshd -t && systemctl restart sshd
sftp evercm@127.0.0.1
```



# 9、几个报错对一下

| 现象 | 大概是 |
| --- | --- |
| `530 Login incorrect` | `/etc/shells`、ftpusers、user_list、faillock 锁了、PAM 密码策略 |
| `500 OOPS: chdir` | 家目录链路上某一级缺 `o+x` |
| `refusing to run with writable root inside chroot()` | 家目录对属主可写，改 755 或开 allow_writeable_chroot |
| 能登录，`ls` 卡住 | 被动模式端口 / 防火墙 / 安全组 |
| `Connection closed`（sftp） | chroot 目录属主或权限不对，看 /var/log/secure |
| `passwd` 报密码历史 | 用 `openssl passwd -6` + `usermod -p` |

ftp 是明文传输，账号密码和数据都不过加密，只放在内网用。要过公网就别开 ftp，只用 sftp，或者把 vsftpd 配成 FTPS。

脚本放在最后，`bash add-ftp-user.sh` 跑一遍就行，最后一步会自己 curl 验证，不通会以非 0 退出。

---

# 附：add-ftp-user.sh

> 下面这份就是现场用的脚本，`FTP_PASS` 换成了占位符，执行前改成真实密码；别把带密码的版本提交到公开仓库。其余内容和现场一致。

```bash
#!/bin/bash
set -e

FTP_USER="evercm"
FTP_PASS='CHANGE_ME'          # 执行前替换成真实密码，不要提交到公开仓库
FTP_HOME="/data/eversec/data/ftp/evercm"
FTP_SUBDIR="${FTP_HOME}/autoUpgrade"
VSFTPD_CONF="/etc/vsftpd/vsftpd.conf"

log() { echo "[$(date '+%F %T')] $*"; }
err() { echo "[$(date '+%F %T')] 错误: $*" >&2; }

# 0. 检查 vsftpd 是否安装
if ! command -v vsftpd >/dev/null 2>&1 && [ ! -x /usr/sbin/vsftpd ]; then
    err "未检测到 vsftpd，请先安装"
    exit 1
fi

# 1. 创建目录
mkdir -p "${FTP_SUBDIR}"

# 2. 逐级路径权限：每级补 o+x，否则 chdir 报 500
path="${FTP_HOME}"
parents=()
while [ "${path}" != "/" ] && [ -n "${path}" ]; do
    parents=("${path}" "${parents[@]}")
    path="$(dirname "${path}")"
done
parents=("/" "${parents[@]}")
for p in "${parents[@]}"; do
    [ -d "${p}" ] || { err "路径不存在: ${p}"; exit 1; }
    [ "$(stat -c '%A' "${p}" | cut -c10)" = "x" ] || chmod o+x "${p}"
done

# 3. 家目录 root 只读，子目录 evercm 可写
chown root:root "${FTP_HOME}"
chmod 755 "${FTP_HOME}"
if id "${FTP_USER}" >/dev/null 2>&1; then
    chown "${FTP_USER}:${FTP_USER}" "${FTP_SUBDIR}"
fi
chmod 755 "${FTP_SUBDIR}"

# 4. /sbin/nologin 加入 /etc/shells
grep -qxF '/sbin/nologin' /etc/shells 2>/dev/null || echo '/sbin/nologin' >> /etc/shells

# 5. vsftpd 配置去重补齐
dedup_conf() {
    local key="$1" val="$2" cnt
    cnt=$(grep -cE "^[[:space:]]*${key}=" "${VSFTPD_CONF}" 2>/dev/null || true)
    [ "${cnt}" -gt 1 ] && sed -i "/^[[:space:]]*${key}=/d" "${VSFTPD_CONF}"
    grep -qxF "${key}=${val}" "${VSFTPD_CONF}" || echo "${key}=${val}" >> "${VSFTPD_CONF}"
}
dedup_conf 'chroot_local_user' 'YES'
dedup_conf 'anonymous_enable' 'NO'
dedup_conf 'allow_writeable_chroot' 'YES'

# 6. 创建用户（不存在时）
if ! id "${FTP_USER}" >/dev/null 2>&1; then
    useradd -d "${FTP_HOME}" -s /sbin/nologin "${FTP_USER}"
    log "用户 ${FTP_USER} 创建完成"
    chown root:root "${FTP_HOME}"
    chmod 755 "${FTP_HOME}"
    chown "${FTP_USER}:${FTP_USER}" "${FTP_SUBDIR}"
    chmod 755 "${FTP_SUBDIR}"
else
    log "用户 ${FTP_USER} 已存在"
fi

# 7. 直接写密码哈希，绕过 PAM 改密历史检查
HASH=$(openssl passwd -6 "${FTP_PASS}")
usermod -p "${HASH}" "${FTP_USER}"
log "密码已设置"

# 8. 解锁账户（失败记录不影响新密码）
faillock --user "${FTP_USER}" --reset >/dev/null 2>&1 || true
[ -f /etc/security/opasswd ] && sed -i "/^${FTP_USER}:/d" /etc/security/opasswd || true

# 9. 黑名单清理
for f in /etc/vsftpd/ftpusers /etc/vsftpd/user_list; do
    [ -f "$f" ] && grep -qxF "${FTP_USER}" "$f" && sed -i "/^${FTP_USER}$/d" "$f" || true
done

# 10. 重启并验证
systemctl restart vsftpd.service
if curl -sS --connect-timeout 5 -u "${FTP_USER}:${FTP_PASS}" "ftp://127.0.0.1/" >/dev/null; then
    log "FTP 登录验证成功"
else
    err "FTP 登录验证失败，检查 journalctl -u vsftpd -n 30 --no-pager"
    exit 1
fi

log "ftp账号 ${FTP_USER} 配置完成"
```

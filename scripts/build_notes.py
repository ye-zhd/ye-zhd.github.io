#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build the documentation section of this static Hexo snapshot.

Source of truth : notes/*.md
Generated       : notes/index.html, notes/<slug>.html, notes/doc.css, notes/doc.js
Patched         : all Hexo-generated *.html (nav entry), search.xml (local search)

Usage: python scripts/build_notes.py
The script is idempotent: run it again after adding/removing md files.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
NOTES = ROOT / "notes"
SEARCH_XML = ROOT / "search.xml"
NOJEKYLL = ROOT / ".nojekyll"

MENU_ITEM = (
    '<div class="menus_item"><a class="site-page" href="/notes/">'
    '<i class="fa-fw fas fa-file-alt"></i><span> 文档</span></a></div>'
)
MENU_ANCHOR = '<div class="menus_item"><a class="site-page" href="/about/">'
HEXO_MARK = 'Hexo 5.4.0'

GROUPS = ["数据库", "安全与网络", "日志与中间件", "存储与工具"]

DOCS = [
    ("Innodb数据文件损坏导致Mysql无法启动.md", "mysql-innodb-corruption", "数据库"),
    ("mysql数据库备份还原.md", "mysql-backup-restore", "数据库"),
    ("docker-compose搭建mysql主从复制.md", "docker-compose-mysql-replication", "数据库"),
    ("clickhouse的zookeeper升级与配置acl账号.md", "clickhouse-zookeeper-acl", "数据库"),
    ("dbeaver连接带kerberos认证的impala.md", "dbeaver-kerberos-impala", "数据库"),
    ("OpenEuler22.03安装 Fail2Ban防SSH暴力破解.md", "openeuler-fail2ban", "安全与网络"),
    ("服务器中xmrig挖矿病毒排除分析.md", "xmrig-mining-virus", "安全与网络"),
    ("frp内网穿透搭建.md", "frp-intranet-penetration", "安全与网络"),
    ("lvs+keeplived+nginx.md", "lvs-keepalived-nginx", "安全与网络"),
    ("docker搭建ELK日志监控系统.md", "docker-elk", "日志与中间件"),
    ("kafka配置kerberos.md", "kafka-kerberos", "日志与中间件"),
    ("linux nfs目录共享.md", "linux-nfs-share", "存储与工具"),
    ("远程软件rustdesk server搭建.md", "rustdesk-server", "存储与工具"),
]

CSS = r"""
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
  color:#24292f;background-color:#f6f7f9;
  background-image:linear-gradient(rgba(15,23,42,.028) 1px,transparent 1px),linear-gradient(90deg,rgba(15,23,42,.028) 1px,transparent 1px);
  background-size:24px 24px;line-height:1.7;
}
a{color:#185fa5;text-decoration:none}
a:hover{color:#0c447c}
.topbar{background:#24292f;color:#fff}
.topbar-inner{max-width:1080px;margin:0 auto;padding:14px 24px;display:flex;align-items:center;gap:18px;flex-wrap:wrap}
.brand{font-size:16px;font-weight:500;color:#fff;letter-spacing:.3px}
.brand:hover{color:#fff;opacity:.85}
.topbar .sep{opacity:.35}
.topbar .nav-link{color:#c9d1d9;font-size:13px}
.topbar .nav-link:hover{color:#fff}
.wrap{max-width:1080px;margin:0 auto;padding:32px 24px 64px}
.page-head{margin-bottom:26px}
.page-head h1{font-size:26px;font-weight:500;margin:0 0 8px}
.page-head p{margin:0;color:#6b7280;font-size:14px}
.toolbar{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin-bottom:22px}
#q{flex:1;min-width:220px;padding:10px 14px;border:1px solid #dfe3e8;border-radius:10px;background:#fff;font-size:14px;outline:none}
#q:focus{border-color:#185fa5}
.chips{display:flex;gap:8px;flex-wrap:wrap}
.chip{padding:7px 13px;border:1px solid #dfe3e8;border-radius:999px;background:#fff;color:#4b5563;font-size:13px;cursor:pointer}
.chip.on{background:#24292f;border-color:#24292f;color:#fff}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}
.card{display:block;background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:18px 20px;transition:transform .15s,border-color .15s}
.card:hover{transform:translateY(-2px);border-color:#185fa5}
.card h2{margin:0 0 10px;font-size:16px;font-weight:500;line-height:1.5;word-break:break-word}
.card .meta{font-size:12px;color:#8a909a;display:flex;gap:10px;align-items:center}
.badge{display:inline-block;padding:2px 9px;border-radius:6px;background:#eef4fc;color:#185fa5;font-size:12px}
.empty{padding:40px;text-align:center;color:#8a909a;background:#fff;border:1px dashed #e5e7eb;border-radius:12px}
.article{background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:32px 36px;max-width:920px;margin:0 auto}
.crumb{font-size:13px;color:#8a909a;margin-bottom:18px}
.crumb a{color:#185fa5}
.article h1.title{font-size:26px;font-weight:500;margin:0 0 6px;word-break:break-word}
.article .sub{margin:0 0 24px;color:#8a909a;font-size:13px;border-bottom:1px solid #eceef1;padding-bottom:18px}
.md-body{font-size:15px;overflow-wrap:break-word}
.md-body h1,.md-body h2,.md-body h3,.md-body h4{font-weight:500;line-height:1.4;margin:28px 0 12px}
.md-body h1{font-size:22px}.md-body h2{font-size:19px}.md-body h3{font-size:16px}.md-body h4{font-size:15px}
.md-body p{margin:12px 0}
.md-body ul,.md-body ol{padding-left:24px}
.md-body li{margin:5px 0}
.md-body blockquote{margin:14px 0;padding:10px 16px;border-left:3px solid #185fa5;background:#f6f8fb;color:#4b5563}
.md-body pre{background:#1f2430;color:#e6edf3;padding:16px 18px;border-radius:9px;overflow-x:auto;font-size:13px;line-height:1.6}
.md-body code{font-family:"SFMono-Regular",Consolas,monospace;font-size:13px}
.md-body :not(pre)>code{background:#f1f3f6;color:#b5305f;padding:2px 5px;border-radius:4px}
.md-body table{border-collapse:collapse;width:100%;margin:16px 0;font-size:14px;display:block;overflow-x:auto}
.md-body th,.md-body td{border:1px solid #e1e4e8;padding:8px 12px;text-align:left}
.md-body th{background:#f6f8fb}
.md-body img{max-width:100%;height:auto}
.md-body hr{border:0;border-top:1px solid #e5e7eb;margin:24px 0}
.md-body a{word-break:break-all}
.pager{display:flex;justify-content:space-between;gap:12px;margin-top:28px;padding-top:20px;border-top:1px solid #eceef1;font-size:13px;flex-wrap:wrap}
.pager span{color:#c0c4cc}
.footer{max-width:1080px;margin:0 auto;padding:0 24px 40px;color:#8a909a;font-size:12px}
@media(max-width:640px){.article{padding:22px 18px}.wrap{padding:24px 16px 48px}.topbar-inner{padding:12px 16px}}
"""

JS = r"""
(function(){
  var input=document.getElementById('q');
  if(!input)return;
  var cards=[].slice.call(document.querySelectorAll('.card'));
  var chips=[].slice.call(document.querySelectorAll('.chip'));
  var empty=document.getElementById('empty');
  var group='all';
  function apply(){
    var q=input.value.trim().toLowerCase();
    var shown=0;
    cards.forEach(function(c){
      var ok=(group==='all'||c.dataset.group===group)&&(!q||c.dataset.search.indexOf(q)>-1);
      c.style.display=ok?'':'none';
      if(ok)shown++;
    });
    if(empty)empty.style.display=shown?'none':'';
  }
  input.addEventListener('input',apply);
  chips.forEach(function(ch){
    ch.addEventListener('click',function(){
      chips.forEach(function(x){x.classList.remove('on')});
      ch.classList.add('on');group=ch.dataset.group;apply();
    });
  });
})();
"""

HEAD = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="shortcut icon" href="/img/favicon.png">
<link rel="stylesheet" href="/notes/doc.css">
</head>
<body>
<header class="topbar"><div class="topbar-inner">
<a class="brand" href="/">Lucky Ye</a><span class="sep">/</span>
<a class="brand" href="/notes/">文档中心</a>
<span style="flex:1"></span>
<a class="nav-link" href="/">博客首页</a>
<a class="nav-link" href="/archives/">归档</a>
</div></header>
"""

FOOT = """<div class="footer">Lucky Ye · 运维工作记录 · 由 scripts/build_notes.py 从 notes/*.md 生成</div>
</body>
</html>
"""

INDEX_TMPL = """<main class="wrap">
<div class="page-head">
<h1>运维工作记录</h1>
<p>共 {count} 篇 · 由 Markdown 源文件自动生成 · <a href="/">返回博客首页</a></p>
</div>
<div class="toolbar">
<input id="q" type="search" placeholder="搜索标题或文件名…" autocomplete="off">
<div class="chips">{chips}</div>
</div>
<div class="grid">{cards}</div>
<div id="empty" class="empty" style="display:none">没有匹配的文档</div>
</main>
"""

PAGE_TMPL = """<main class="wrap">
<article class="article">
<div class="crumb"><a href="/">首页</a> / <a href="/notes/">文档中心</a> / {group}</div>
<h1 class="title">{title}</h1>
<p class="sub">{group} · 约 {chars} 字 · <a href="/notes/{source}">查看 Markdown 原文</a></p>
<div class="md-body">{body}</div>
<div class="pager">{pager}</div>
</article>
</main>
"""


def render_md(text: str) -> str:
    md = markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists"])
    return md.convert(text)


def plain_text(rendered: str, limit: int = 6000) -> str:
    s = re.sub(r"<!--.*?-->", " ", rendered, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:limit]


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    newline = "\n"
    if path.exists() and b"\r\n" in path.read_bytes():
        newline = "\r\n"
    path.write_text(content, encoding="utf-8", newline=newline)


def build_pages() -> list[dict]:
    entries = []
    for filename, slug, group in DOCS:
        src = NOTES / filename
        if not src.exists():
            print("  [warn] missing source: %s" % filename)
            continue
        text = src.read_text(encoding="utf-8")
        title = src.stem
        entries.append({
            "filename": filename,
            "slug": slug,
            "group": group,
            "title": title,
            "chars": len(text),
            "body": render_md(text),
        })

    cards = []
    for e in entries:
        searchable = (e["title"] + " " + e["filename"] + " " + e["group"]).lower()
        cards.append(
            '<a class="card" data-group="{g}" data-search="{s}" href="/notes/{slug}.html">'
            '<h2>{title}</h2><div class="meta"><span class="badge">{g}</span>'
            '<span>约 {chars} 字</span></div></a>'.format(
                g=html.escape(e["group"]),
                s=html.escape(searchable, quote=True),
                slug=e["slug"],
                title=html.escape(e["title"]),
                chars=e["chars"],
            )
        )

    chips = ['<button class="chip on" data-group="all">全部</button>'] + [
        '<button class="chip" data-group="{0}">{0}</button>'.format(html.escape(g))
        for g in GROUPS
    ]

    index_html = (
        HEAD.format(title="运维工作记录 | Lucky Ye")
        + INDEX_TMPL.format(count=len(entries), chips="".join(chips), cards="".join(cards))
        + '<script src="/notes/doc.js"></script>'
        + FOOT
    )
    write(NOTES / "index.html", index_html)
    write(NOTES / "doc.css", CSS.lstrip())
    write(NOTES / "doc.js", JS.lstrip())

    for i, e in enumerate(entries):
        prev_e = entries[i - 1] if i > 0 else None
        next_e = entries[i + 1] if i + 1 < len(entries) else None
        pager_prev = (
            '<a href="/notes/{0}.html">&laquo; {1}</a>'.format(
                prev_e["slug"], html.escape(prev_e["title"])
            )
            if prev_e else "<span></span>"
        )
        pager_next = (
            '<a href="/notes/{0}.html">{1} &raquo;</a>'.format(
                next_e["slug"], html.escape(next_e["title"])
            )
            if next_e else "<span></span>"
        )
        page = (
            HEAD.format(title=html.escape(e["title"]) + " | 文档中心")
            + PAGE_TMPL.format(
                group=html.escape(e["group"]),
                title=html.escape(e["title"]),
                chars=e["chars"],
                source=e["filename"],
                body=e["body"],
                pager=pager_prev + pager_next,
            )
            + FOOT
        )
        write(NOTES / (e["slug"] + ".html"), page)

    print("  generated %d article pages + index/css/js" % len(entries))
    return entries


def patch_navigation() -> int:
    """Inject the menu item into every nav copy (desktop + mobile sidebar)."""
    changed = 0
    for path in ROOT.rglob("*.html"):
        if ".git" in path.parts or NOTES.name in path.parts:
            continue
        s = path.read_text(encoding="utf-8")
        if HEXO_MARK not in s or MENU_ANCHOR not in s:
            continue
        # Strip previous injections first so the script stays idempotent.
        cleaned = s.replace(MENU_ITEM, "")
        patched = cleaned.replace(MENU_ANCHOR, MENU_ITEM + MENU_ANCHOR)
        if patched == s:
            continue
        write(path, patched)
        changed += 1
    print("  nav entry injected into %d pages (both menu copies)" % changed)
    return changed


def patch_search(entries: list[dict]) -> None:
    s = SEARCH_XML.read_text(encoding="utf-8")
    parts = []
    for e in entries:
        url = "/notes/%s.html" % e["slug"]
        content = plain_text(e["body"]).replace("]]>", "]]]]><![CDATA[>")
        parts.append(
            '    <entry>\n'
            '      <title>{title}</title>\n'
            '      <link href="{url}"/>\n'
            '      <url>{url}</url>\n'
            '      <content type="html"><![CDATA[{content}]]></content>\n'
            '    </entry>\n'.format(
                title=html.escape(e["title"]), url=url, content=content
            )
        )
    block = "<!-- NOTES_BEGIN -->\n" + "".join(parts) + "<!-- NOTES_END -->\n"
    if "<!-- NOTES_BEGIN -->" in s:
        s = re.sub(
            r"<!-- NOTES_BEGIN -->.*?<!-- NOTES_END -->\n?",
            lambda _m: block,
            s,
            flags=re.S,
        )
    else:
        s = s.replace("</search>", block + "</search>")
    write(SEARCH_XML, s)
    print("  search.xml now indexes %d extra entries" % len(entries))


def main() -> None:
    print("Building notes from %s" % NOTES)
    entries = build_pages()
    patch_navigation()
    patch_search(entries)
    if not NOJEKYLL.exists():
        NOJEKYLL.write_text("", encoding="utf-8")
        print("  created .nojekyll (disable Jekyll processing on Pages)")
    print("Done. Re-run this script after changing notes/*.md")


if __name__ == "__main__":
    main()

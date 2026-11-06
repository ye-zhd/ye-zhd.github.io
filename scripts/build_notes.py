#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build the documentation section of this static Hexo snapshot.

Source of truth : notes/*.md  (every md is discovered automatically)
Generated       : notes/index.html, notes/<slug>.html, notes/doc.css, notes/doc.js
Patched         : all Hexo-generated *.html (nav, article stream, counters), search.xml

Usage: python scripts/build_notes.py

Daily workflow:
  1. Add / edit / delete a .md file under notes/
  2. Run this script (it rebuilds pages, nav, archive, counters and search index)
  3. git add -A && git commit && git push

Optional YAML-ish front-matter at the top of a new md:
  ---
  title: 自定义标题
  slug: my-custom-url
  group: 数据库
  date: 2026-11-06
  ---
Without it, the filename becomes the title and a stable slug is generated.

DOCS below only pins slugs/groups for the original 13 files so their URLs
never change. New md files need no registration.
"""
from __future__ import annotations

import datetime
import hashlib
import html
import re
from pathlib import Path
from urllib.parse import quote

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
DEFAULT_GROUP = "未分类"
GEN_MARK = "<!-- GENERATED-BY: build_notes.py -->"

DOCS = {
    "Innodb数据文件损坏导致Mysql无法启动.md": ("mysql-innodb-corruption", "数据库"),
    "mysql数据库备份还原.md": ("mysql-backup-restore", "数据库"),
    "docker-compose搭建mysql主从复制.md": ("docker-compose-mysql-replication", "数据库"),
    "clickhouse的zookeeper升级与配置acl账号.md": ("clickhouse-zookeeper-acl", "数据库"),
    "dbeaver连接带kerberos认证的impala.md": ("dbeaver-kerberos-impala", "数据库"),
    "OpenEuler22.03安装 Fail2Ban防SSH暴力破解.md": ("openeuler-fail2ban", "安全与网络"),
    "服务器中xmrig挖矿病毒排除分析.md": ("xmrig-mining-virus", "安全与网络"),
    "frp内网穿透搭建.md": ("frp-intranet-penetration", "安全与网络"),
    "lvs+keeplived+nginx.md": ("lvs-keepalived-nginx", "安全与网络"),
    "docker搭建ELK日志监控系统.md": ("docker-elk", "日志与中间件"),
    "kafka配置kerberos.md": ("kafka-kerberos", "日志与中间件"),
    "linux nfs目录共享.md": ("linux-nfs-share", "存储与工具"),
    "远程软件rustdesk server搭建.md": ("rustdesk-server", "存储与工具"),
}

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.S)

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
<!-- GENERATED-BY: build_notes.py -->
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


def parse_front_matter(raw: str) -> tuple[dict, str]:
    m = FM_RE.match(raw)
    meta = {}
    if not m:
        return meta, raw
    for line in m.group(1).splitlines():
        if ":" in line and not line.strip().startswith("#"):
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip("\"'")
    return meta, raw[m.end():]


def auto_slug(filename: str) -> str:
    stem = Path(filename).stem
    if re.fullmatch(r"[A-Za-z0-9_\- .]+", stem):
        return re.sub(r"[^A-Za-z0-9]+", "-", stem).strip("-").lower()[:60]
    return "doc-" + hashlib.md5(filename.encode("utf-8")).hexdigest()[:10]


def discover_docs() -> list[tuple[str, str, str]]:
    """Pinned files first (stable URLs), then any other md, alphabetically."""
    items: list[tuple[str, str, str]] = []
    seen: set[str] = set()
    used_slugs: set[str] = set()

    for filename, (slug, group) in DOCS.items():
        if not (NOTES / filename).exists():
            print("  [warn] pinned source missing: %s" % filename)
            continue
        items.append((filename, slug, group))
        seen.add(filename)
        used_slugs.add(slug)

    for src in sorted(NOTES.glob("*.md"), key=lambda p: p.name):
        if src.name in seen:
            continue
        meta, _ = parse_front_matter(src.read_text(encoding="utf-8"))
        slug = meta.get("slug") or auto_slug(src.name)
        base, n = slug, 2
        while slug in used_slugs or not slug:
            slug = "%s-%d" % (base, n)
            n += 1
        used_slugs.add(slug)
        items.append((src.name, slug, meta.get("group") or DEFAULT_GROUP))
    return items


def cleanup_generated(entries: list[dict]) -> None:
    """Remove article pages whose md source no longer exists."""
    keep = {e["slug"] + ".html" for e in entries}
    removed = []
    for path in NOTES.glob("*.html"):
        if path.name == "index.html" or path.name in keep:
            continue
        if GEN_MARK not in path.read_text(encoding="utf-8"):
            continue
        path.unlink()
        removed.append(path.name)
    if removed:
        print("  removed %d stale page(s): %s" % (len(removed), ", ".join(removed)))


def count_original_posts() -> int:
    """Count pre-existing Hexo entries (before the NOTES block in search.xml)."""
    s = SEARCH_XML.read_text(encoding="utf-8")
    n = s.split("<!-- NOTES_BEGIN -->")[0].count("<entry>")
    return n or FALLBACK_ORIGINAL_POSTS


def build_pages() -> list[dict]:
    entries = []
    for filename, slug, group in discover_docs():
        src = NOTES / filename
        raw = src.read_text(encoding="utf-8")
        meta, text = parse_front_matter(raw)
        dt = datetime.datetime.fromtimestamp(src.stat().st_mtime)
        explicit_date = bool(meta.get("date"))
        date = meta.get("date") or dt.strftime("%Y-%m-%d")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            date = dt.strftime("%Y-%m-%d")
            explicit_date = False
        iso = (
            date + "T00:00:00.000Z"
            if explicit_date
            else dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        )
        entries.append({
            "filename": filename,
            "slug": slug,
            "group": group,
            "title": meta.get("title") or src.stem,
            "chars": len(text),
            "body": render_md(text),
            "date": date,
            "iso": iso,
            "url": "/notes/%s.html" % slug,
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

    used_groups = [g for g in GROUPS if any(e["group"] == g for e in entries)]
    used_groups += sorted({e["group"] for e in entries} - set(used_groups))
    chips = ['<button class="chip on" data-group="all">全部</button>'] + [
        '<button class="chip" data-group="{0}">{0}</button>'.format(html.escape(g))
        for g in used_groups
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
    synced = 0
    for path in ROOT.rglob("*.html"):
        if ".git" in path.parts or NOTES.name in path.parts:
            continue
        s = path.read_text(encoding="utf-8")
        if HEXO_MARK not in s or MENU_ANCHOR not in s:
            continue
        synced += 1
        # Strip previous injections first so the script stays idempotent.
        cleaned = s.replace(MENU_ITEM, "")
        patched = cleaned.replace(MENU_ANCHOR, MENU_ITEM + MENU_ANCHOR)
        if patched == s:
            continue
        write(path, patched)
        changed += 1
    print("  nav entry synced in %d pages (%d rewritten, both menu copies)" % (synced, changed))
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


FALLBACK_ORIGINAL_POSTS = 3  # used only if search.xml cannot be parsed

COVER_SVG = (
    "<svg xmlns='http://www.w3.org/2000/svg' width='640' height='400'>"
    "<rect width='640' height='400' fill='#2b3a55'/>"
    "<circle cx='520' cy='90' r='160' fill='#3f5b8f' opacity='0.45'/>"
    "<text x='44' y='230' font-family='sans-serif' font-size='76' "
    "fill='#ffffff' opacity='0.92'>DOC</text></svg>"
)
COVER = "data:image/svg+xml," + quote(COVER_SVG, safe="")
IMG_FALLBACK = "this.onerror=null;this.src='/img/404.jpg'"

POSTS_B, POSTS_E = "<!-- NOTES_POSTS_BEGIN -->", "<!-- NOTES_POSTS_END -->"
ASIDE_B, ASIDE_E = "<!-- NOTES_ASIDE_BEGIN -->", "<!-- NOTES_ASIDE_END -->"
ARCH_B, ARCH_E = "<!-- NOTES_ARCH_BEGIN -->", "<!-- NOTES_ARCH_END -->"


def strip_marks(s: str, begin: str, end: str) -> str:
    return re.sub(re.escape(begin) + r".*?" + re.escape(end), "", s, flags=re.S)


def card_html(e: dict, index: int) -> str:
    side = "left" if index % 2 == 0 else "right"
    t = html.escape(e["title"], quote=True)
    excerpt = html.escape(plain_text(e["body"], 200))
    return (
        '<div class="recent-post-item"><div class="post_cover {side}">'
        '<a href="{url}" title="{t}"><img class="post_bg" src="{cover}" alt="{t}"></a></div>'
        '<div class="recent-post-info"><a class="article-title" href="{url}" title="{t}">{t}</a>'
        '<div class="article-meta-wrap"><span class="post-meta-date">'
        '<i class="far fa-calendar-alt"></i><span class="article-meta-label">发表于</span>'
        '<time datetime="{iso}" title="发表于 {date}">{date}</time></span></div>'
        '<div class="content">{excerpt}</div></div></div>'
    ).format(side=side, url=e["url"], t=t, cover=COVER,
             iso=e["iso"], date=e["date"], excerpt=excerpt)


def aside_html(e: dict) -> str:
    t = html.escape(e["title"], quote=True)
    return (
        '<div class="aside-list-item"><a class="thumbnail" href="{url}" title="{t}">'
        '<img src="{cover}" onerror="{fb}" alt="{t}"/></a><div class="content">'
        '<a class="title" href="{url}" title="{t}">{t}</a>'
        '<time datetime="{iso}" title="发表于 {date}">{date}</time></div></div>'
    ).format(url=e["url"], t=t, cover=COVER, fb=IMG_FALLBACK,
             iso=e["iso"], date=e["date"])


def archive_html(e: dict) -> str:
    t = html.escape(e["title"], quote=True)
    return (
        '<div class="article-sort-item"><a class="article-sort-item-img" href="{url}" title="{t}">'
        '<img src="{cover}" alt="{t}" onerror="{fb}"></a><div class="article-sort-item-info">'
        '<div class="article-sort-item-time"><i class="far fa-calendar-alt"></i>'
        '<time class="post-meta-date-created" datetime="{iso}" title="发表于 {date}">{date}</time></div>'
        '<a class="article-sort-item-title" href="{url}" title="{t}">{t}</a></div></div>'
    ).format(url=e["url"], t=t, cover=COVER, fb=IMG_FALLBACK,
             iso=e["iso"], date=e["date"])


def archive_block(entries: list[dict]) -> str:
    out, last_year = [], None
    for e in sorted(entries, key=lambda x: x["date"], reverse=True):
        year = e["date"][:4]
        if year != last_year:
            out.append('<div class="article-sort-item year">%s</div>' % year)
            last_year = year
        out.append(archive_html(e))
    return "".join(out)


def patch_blog_stream(entries: list[dict]) -> None:
    """Merge the docs into the Hexo article stream (home, counters, widgets, archive)."""
    total = count_original_posts() + len(entries)
    latest = max((e["iso"] for e in entries), default=None)
    home = ROOT / "index.html"
    archive = ROOT / "archives" / "index.html"

    ordered = sorted(entries, key=lambda x: x["date"], reverse=True)
    s = strip_marks(home.read_text(encoding="utf-8"), POSTS_B, POSTS_E)
    anchor = 'id="recent-posts">'
    s = s.replace(
        anchor,
        anchor + POSTS_B + "".join(card_html(e, i) for i, e in enumerate(ordered)) + POSTS_E,
        1,
    )
    write(home, s)

    s = strip_marks(archive.read_text(encoding="utf-8"), ARCH_B, ARCH_E)
    anchor = '<div class="article-sort">'
    s = s.replace(anchor, anchor + ARCH_B + archive_block(ordered) + ARCH_E, 1)
    write(archive, s)

    widgets = 0
    for path in ROOT.rglob("*.html"):
        if ".git" in path.parts or NOTES.name in path.parts:
            continue
        s = path.read_text(encoding="utf-8")
        if HEXO_MARK not in s:
            continue
        s = strip_marks(s, ASIDE_B, ASIDE_E)
        i = s.find("card-recent-post")
        j = s.find('<div class="aside-list">', i) if i >= 0 else -1
        if j >= 0:
            cut = j + len('<div class="aside-list">')
            s = (
                s[:cut]
                + ASIDE_B
                + "".join(aside_html(e) for e in ordered[:5])
                + ASIDE_E
                + s[cut:]
            )
            widgets += 1
        s = re.sub(
            r'(<div class="headline">文章</div><div class="length-num">)\d+(</div>)',
            lambda m: m.group(1) + str(total) + m.group(2),
            s,
        )
        s = re.sub(r"文章总览 - \d+", "文章总览 - %d" % total, s)
        if latest:
            s = re.sub(
                r'(id="last-push-date" data-lastPushDate=")[^"]+(")',
                lambda m: m.group(1) + latest + m.group(2),
                s,
            )
        write(path, s)

    print("  article stream: %d posts total, %d sidebar widgets updated" % (total, widgets))


def main() -> None:
    print("Building notes from %s" % NOTES)
    entries = build_pages()
    cleanup_generated(entries)
    patch_navigation()
    patch_blog_stream(entries)
    patch_search(entries)
    if not NOJEKYLL.exists():
        NOJEKYLL.write_text("", encoding="utf-8")
        print("  created .nojekyll (disable Jekyll processing on Pages)")
    print("Done. Re-run this script after changing notes/*.md")


if __name__ == "__main__":
    main()

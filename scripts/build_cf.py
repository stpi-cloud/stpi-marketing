"""Build the public site for Cloudflare Pages (getstpi.pages.dev) into _cf/.

2026-09-27: GitHub Pages was unreliable on phones, so the buyer-facing pages moved to
Cloudflare Pages. The site root is the landing page (getstpi/index.html); the internal
marketing bible (repo-root index.html) is NOT published here; it builds into _cf_bible/ for its own
project, stpi-bible.pages.dev (see build_bible). Old GitHub Pages URLs
redirect to the matching page on this host (see the redirect snippet in each page head).
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_cf"
SITE = "https://getstpi.pages.dev"

PAGES = {  # source -> path on the site
    "getstpi/index.html": "index.html",
    "demo.html": "demo.html",
    "setup.html": "setup.html",
    "domain.html": "domain.html",
}
DIRS = ["downloads", "brand", "graphics", "samples", "press/img"]
FILES = ["16e37daa71b14add9de53ec65d64e01a.txt"]  # IndexNow key

REDIRECTS = """# Pages already serves /demo for demo.html (and 308s /demo.html -> /demo); never map
# /demo back to /demo.html or it loops.
/getstpi        /           301
/getstpi/       /           301
/getstpi/*      /           301
/download        /demo       301
/downloads       /demo       301
/downloads/      /demo       301
/trial           https://stpi-mint.stpi-cloud.workers.dev/trial 302
/store           https://whop.com/stpi 302
"""

HEADERS = """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
/downloads/*.zip
  Content-Type: application/zip
  Content-Disposition: attachment
  Cache-Control: public, max-age=3600
/brand/*
  Cache-Control: public, max-age=86400
/press/img/*
  Cache-Control: public, max-age=86400
"""

ROBOTS = f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n"


def sitemap() -> str:
    urls = [f"{SITE}/", f"{SITE}/demo", f"{SITE}/setup", f"{SITE}/domain"]
    body = "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "</urlset>\n")


def build() -> Path:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for src, dst in PAGES.items():
        (OUT / dst).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / src, OUT / dst)
    for d in DIRS:
        if (ROOT / d).is_dir():
            shutil.copytree(ROOT / d, OUT / d, ignore=shutil.ignore_patterns("raw", "*.md"))
    for f in FILES:
        if (ROOT / f).exists():
            shutil.copyfile(ROOT / f, OUT / f)
    shutil.copyfile(ROOT / "brand" / "favicon.ico", OUT / "favicon.ico")
    (OUT / "_redirects").write_text(REDIRECTS)
    (OUT / "_headers").write_text(HEADERS)
    (OUT / "robots.txt").write_text(ROBOTS)
    (OUT / "sitemap.xml").write_text(sitemap())
    # guard: nothing on the public site may point back at GitHub Pages or the private repo
    bad = []
    for p in OUT.rglob("*.html"):
        t = p.read_text(encoding="utf-8", errors="ignore")
        for needle in ("github.io/stpi-marketing", "github.com/stpi-cloud/stpi\""):
            if needle in t.replace("GH_REDIRECT_OK", ""):
                bad.append(f"{p.relative_to(OUT)}: {needle}")
    if bad:
        raise SystemExit("public site still links to GitHub Pages / private repo:\n" + "\n".join(bad))
    return OUT


# ---- the marketing bible: its own Pages project (stpi-bible.pages.dev), kept off the buyer site ----
# 2026-09-28 (owner): host the bible on Cloudflare. It is internal sales material, so it is a separate
# project, not linked from getstpi, and marked noindex. (The repo is public, so this adds no exposure.)
BIBLE_OUT = ROOT / "_cf_bible"
BIBLE_SITE = "https://stpi-bible.pages.dev"
_SITE_PATHS = {"demo.html": "/demo", "setup.html": "/setup", "domain.html": "/domain"}


def _absolute(m: "re.Match") -> str:
    attr, url = m.group(1), m.group(2)
    if re.match(r"^(https?:|#|mailto:|tel:|data:|lightning:|javascript:)", url):
        return m.group(0)
    if url.split("#")[0].startswith(("bible-assets/", "whop/", ".embed/")):
        return m.group(0)  # served by the bible project itself (copied in build_bible)
    path, _, frag = url.partition("#")
    path = _SITE_PATHS.get(path, "/" + path.lstrip("./"))
    return f'{attr}="{SITE}{path}{"#" + frag if frag else ""}"'


def build_bible() -> Path:
    if BIBLE_OUT.exists():
        shutil.rmtree(BIBLE_OUT)
    BIBLE_OUT.mkdir()
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    html = re.sub(r'\b(href|src|content)="([^"]+\.(?:html|pdf|zip|svg|ico|png|jpg)(?:#[^"]*)?)"', _absolute, html)
    html = html.replace("<head>", '<head>\n<meta name="robots" content="noindex, nofollow">', 1)
    left = [u for u in re.findall(
        r'\b(?:href|src)="(?!https?:|#|mailto:|tel:|data:|lightning:|javascript:)([^"]+)"', html)
        if not u.split("#")[0].startswith(("bible-assets/", "whop/", ".embed/"))]
    if left:
        raise SystemExit(f"bible still has relative links: {sorted(set(left))[:10]}")
    (BIBLE_OUT / "index.html").write_text(html, encoding="utf-8")
    shutil.copyfile(ROOT / "brand" / "favicon.ico", BIBLE_OUT / "favicon.ico")
    # 2026-10-01 (v3.0): the bible now serves its own image/materials vault
    for d in ("bible-assets", "whop", ".embed"):
        ba = ROOT / d
        if ba.is_dir():
            shutil.copytree(ba, BIBLE_OUT / d,
                            ignore=shutil.ignore_patterns("*.py", "*.txt", "*.md", "__pycache__"))
    (BIBLE_OUT / "_headers").write_text("/*\n  X-Robots-Tag: noindex, nofollow\n  X-Content-Type-Options: nosniff\n"
                                        "  Referrer-Policy: no-referrer\n")
    (BIBLE_OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
    return BIBLE_OUT


if __name__ == "__main__":
    out = build()
    print(f"built {sum(1 for _ in out.rglob('*') if _.is_file())} files into {out}")
    bo = build_bible()
    print(f"built the bible into {bo}")

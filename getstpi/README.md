# Landing page — the un-gated demo download

`index.html` is fully self-contained: inline CSS, inline SVG, **no JS bundles, no fonts,
no analytics, no forms** — the only link is the `stpi-demo-<ver>.zip` next to it (plus mailto
and the Whop checkout). That is a product promise, not a style preference: a test enforces it
(`test_landing_page_is_truly_ungated`).

## Ship it ($0)
```bash
cd .. && python -m build && python scripts/make_demo_pack.py
cp dist/stpi-demo-1.0.2.zip dist/stpi-demo-1.0.2.zip.sha256 landing/
npx wrangler pages deploy landing --project-name stpi-landing   # or: any static host, or a
                                                                   #   directory served by Caddy
```
Cloudflare Pages free tier: 500 builds/month, unlimited requests, free TLS, custom domain free.
No card needed for `.pages.dev`. Update the checkout URL after `wrangler` or leave the placeholder
— the pack builder screams if placeholders are still in `stpi/demo.py`.

## Editing copy
Prices/rails/links live in `stpi/demo.py → BILLING` (product surfaces) and are mirrored by hand
in `index.html` (search `whop.com/checkout` / `$306`). Keep the zip filename in the
`href` in sync with the version you just built. Do NOT add a form, a pixel or a script — the
page's entire pitch is that there isn't one.

## 2026-10-01 — this folder IS the whole buyer site now

It used to be just the branded landing. It now also carries the full public
property previously deployed from stpi-marketing (`demo.html`, `setup.html`,
`domain.html`, `downloads/`, `samples/`, `brand/`, `graphics/`, `press/img/`,
`_redirects`, `_headers`, `robots.txt`, `sitemap.xml`, favicon, IndexNow key),
because `pages-deploy.yml` is the single owner of the `getstpi` Pages project —
the marketing repo deploys only the internal bible from now on. The mirror step
rebuilds `stpi-a.pages.dev` from this same tree (host refs swapped), and the
smoke step fails the run if any of `/demo /setup /domain /downloads/…zip
/robots.txt /sitemap.xml /favicon.ico` ever falls back to the index page again.

#!/usr/bin/env python3
"""Bible v3.0 (2026-10-01): grow stpi-bible.pages.dev from a summary to the full vault.

Owner: "it's way too shallow — add 600% more information, and all promo images + materials."

What this builder injects into index.html (idempotent, between AUTO markers):

  1. vault       The copy vault — every copy/*.md verbatim, plus storefront/demo-kit docs.
  2. topics      The promo factory — mechanics + the entire rendered topic registry (92 topics).
  3. cards       The promo card gallery — every card the factory renders (bible-assets/cards/).
  4. media       The media vault — every image asset in the repo + the 2026 external kit.
  5. demokit     The demo kit — file inventory with sha256, the demo's own upsell inventory,
                 the Sovereign compose file.
  6. storefront  Storefront ops — the three Whop product copies verbatim (2026-10-01 fetch),
                 the copy-drift table, the affiliate-program block.
  7. machine     The 2026 machine — cadence/budgets, the self-healing systems, host ownership,
                 the runbook index, the self-serve journey, the grind, the landing verbatim.
  8. brand2      Brand 2.0 — the 2026-10-01 STPi refresh: tokens, glyph, voice, coverage.

Refresh inputs:
  - scripts/_data/topics-rendered.json : regenerate from the stpi checkout with
      python3 -c 'import sys; sys.path.insert(0,"press"); import facts, json;
      json.dump({"topics": json.loads(facts.render(open("press/topics.json").read()))},
                 open("MARKETING/scripts/_data/topics-rendered.json","w"), indent=2)'
  - bible-assets/cards/*.png : regenerate with press/cards.py (see bottom of this file).
  - landing copy + FAQ : re-extracted from the stpi checkout when present
    (STPI env var), else the last vendored snapshot in scripts/_data/ is reused.

Requires: pip install markdown
"""
from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "scripts" / "_data"
STPI = Path(os.environ.get("STPI", "/home/user/sweep/stpi"))
DOCS = Path(os.environ.get("STPI_DOCS", "/home/user/sweep/stpi-docs"))
TODAY = "2026-10-01"

NAV_BEGIN = "<!-- AUTO-NAV:BEGIN -->"
NAV_END = "<!-- AUTO-NAV:END -->"
SEC_BEGIN = "<!-- AUTO-SECTIONS:BEGIN -->"
SEC_END = "<!-- AUTO-SECTIONS:END -->"

TABS = [
    ("vault", "Copy vault"),
    ("topics", "Promo topics"),
    ("cards", "Card gallery"),
    ("media", "Media vault"),
    ("demokit", "Demo kit"),
    ("storefront", "Storefront"),
    ("machine", "The machine"),
    ("brand2", "Brand 2.0"),
    ("playbooks", "Playbooks"),
    ("record", "Published record"),
]


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def md(text: str) -> str:
    return markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])


def words_of(html_text: str) -> int:
    return len(re.sub(r"<[^>]+>", " ", html_text).split())


def fig(src: str, cap: str = "", wide: bool = False) -> str:
    style = "max-width:100%;border:1px solid var(--line);border-radius:10px;background:#fff;padding:6px"
    body = f'<div class="imgwrap{"" if wide else ""}"><img loading="lazy" src="{src}" alt="{esc(cap)}" style="{style}">'
    if cap:
        body += f'<div class="cap">{cap}</div>'
    return body + "</div>"


def cb(text: str, title: str | None = None) -> str:
    head = f'<button class="copybtn">Copy</button>' if title is None else ""
    t = f"<p><b>{esc(title)}</b></p>" if title else ""
    return f'{t}<div class="copyblock">{head}<pre>{esc(text)}</pre></div>'


# ----------------------------------------------------------------------------- data loaders

def load_topics() -> list[dict]:
    d = json.loads((DATA / "topics-rendered.json").read_text())
    return d.get("topics", d if isinstance(d, list) else [])


def landing_parts() -> tuple[str, list[tuple[str, str]]]:
    """(verbatim page text, [(question, answer)]) refreshed from the stpi checkout."""
    src = STPI / "landing" / "index.html"
    lp, fq = DATA / "landing-copy.txt", DATA / "landing-faq.json"
    if src.exists():
        raw = src.read_text(encoding="utf-8", errors="ignore")
        for tag in ("style", "script", "svg", "nav", "header"):
            raw = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", " ", raw, flags=re.S | re.I)
        faq = [(re.sub(r"<[^>]+>", " ", q).strip(), re.sub(r"<[^>]+>", " ", a).strip())
               for q, a in re.findall(r"<summary[^>]*>(.*?)</summary>(.*?)</details>", raw, flags=re.S)]
        txt = re.sub(r"</(p|li|h[1-6]|tr|div|section|dd|dt)>", "\n", raw, flags=re.I)
        txt = re.sub(r"<br[^>]*>", "\n", txt, flags=re.I)
        txt = html.unescape(re.sub(r"<[^>]+>", "", txt))
        lines = [l.strip() for l in txt.splitlines() if l.strip()]
        lp.write_text(f"-- extracted {TODAY} from stpi/landing/index.html --\n" + "\n".join(lines))
        fq.write_text(json.dumps(faq, indent=1))
    copy = lp.read_text() if lp.exists() else "(landing snapshot missing)"
    faqs = json.loads(fq.read_text()) if fq.exists() else []
    return copy, faqs


def docs_index() -> str:
    rd = DOCS / "README.md"
    if not rd.exists():
        return "<p><i>runbook index unavailable (stpi-docs checkout not found)</i></p>"
    rows = []
    for line in rd.read_text().splitlines():
        m = re.match(r"\|\s*\*\*`([^`]+)`\*\*\s*\|\s*([^|]+)\|\s*([^|]+)\|", line)
        if m:
            rows.append(f"<tr><td><code>{esc(m.group(1))}</code></td><td>{esc(m.group(2).strip())}</td>"
                        f"<td>{esc(m.group(3).strip())}</td></tr>")
    return ("<table><tr><th>Runbook</th><th>Owner</th><th>What it is</th></tr>" + "".join(rows) + "</table>")


def file_size(p: Path) -> str:
    kb = p.stat().st_size / 1024
    return f"{kb/1024:.1f} MB" if kb > 1024 else f"{kb:.0f} KB"


# ----------------------------------------------------------------------------- storefront verbatim (fetched 2026-10-01)

SOLO_COPY = """STPi Solo — $306/ month   (+2 options)
"3 candidates, 100 sends a month. Drafted nightly, sent after your yes."
For individual career coaches and job agents.

STPi hunts vacancies nightly, scores them against each CV, drafts a tailored CV
and cover letter, and sends you a one-tap approval card in Discord.

Solo includes:
- 3 candidates
- 100 sends a month
- Priority slots
- Approve in Discord (web dashboard + Telegram when self-hosted)
- 17 job boards by default (22 supported) across South Africa, Zimbabwe and Zambia
- Human approval on every send

$306/mo (about R4,999) billed every 30 days, or R4,999/mo in rands, or $2,754/yr
(about R45,000) prepaid by bank wire. Cancel any time.

FAQ
Does anything send without me? No. Each application is a Discord card; nothing goes
out until you tap Approve.
Can I try first? Yes, free demo pack (1 candidate, 25 drafts, 5 sends / 30 days):
https://getstpi.pages.dev/
Pay in rands? Yes: rand checkouts at R4,999/mo / R9,999/mo / R15,000/mo.
Annual: one bank-wire payment, 25% off.
No card? Lightning (SharkSkin@coinos.io) or Mukuru / EFT (+263 78 460 0904, ref = tenant id).
Full FAQ in the STPi forum. Questions: simalidudu@gmail.com"""

STUDIO_COPY = """STPi Studio — $613/ month   (+2 options)
"15 candidates, fair-use sends, PDFs branded as your agency."
For coaching practices and small recruitment agencies.

Studio includes:
- 15 candidates
- Fair-use sends
- White-label CV and cover-letter PDFs
- LLM fallback chain: one provider outage won't stop the run
- 17 job boards by default (22 supported) across South Africa, Zimbabwe and Zambia
- Human approval on every send

$613/mo (about R9,999) billed every 30 days, or R9,999/mo in rands, or $5,517/yr
(about R90,000) prepaid by bank wire. Cancel any time.

FAQ
Does anything send without me? No. Each application is a Discord card; nothing goes
out until you tap Approve.
Can I try first? Yes, free demo pack (1 candidate, 25 drafts, 5 sends / 30 days):
https://getstpi.pages.dev/
Pay in rands? Yes: rand checkouts at R4,999/mo / R9,999/mo / R15,000/mo.
Annual: one bank-wire payment, 25% off.
No card? Lightning (SharkSkin@coinos.io) or Mukuru / EFT (+263 78 460 0904, ref = tenant id).
Full FAQ in the STPi forum. Questions: simalidudu@gmail.com"""

SOVEREIGN_COPY = """STPi Sovereign — $920/ month   (+2 options)
"Self-hosted, unlimited candidates and sends. Your data stays on your servers."
For agencies and institutions that need the pipeline on their own infrastructure.

Sovereign includes:
- Self-hosted Docker deployment on your own box
- Unlimited candidates and sends
- Signed offline licence, delivered in your Discord after checkout (WhatsApp backup)
- Install guide + help in your private Discord channel
- 17 job boards by default (22 supported) across South Africa, Zimbabwe and Zambia
- Human approval on every send
- Lapsed licence = read-only, never bricked or deleted

$920/mo (about R15,000) billed every 30 days, or R15,000/mo in rands, or $8,280/yr
(about R135,000) prepaid by bank wire. Cancel any time.

FAQ
Does anything send without me? No. Each application is a Discord card; nothing goes
out until you tap Approve.
Can I try first? Yes, free demo pack (1 candidate, 25 drafts, 5 sends / 30 days):
https://getstpi.pages.dev/
Pay in rands? Yes: rand checkouts at R4,999/mo / R9,999/mo / R15,000/mo.
Annual: one bank-wire payment, 25% off.
No card? Lightning (SharkSkin@coinos.io) or Mukuru / EFT (+263 78 460 0904, ref = tenant id).
Full FAQ in the STPi forum. Questions: simalidudu@gmail.com"""

DEMO_CTA_INVENTORY = """The demo sells at every surface (verified in stpi/demo.py, 2026-10-01):

1. CLI banner on every invocation (demo.py cli_banner(), ~L201):
   ┌──────────────────────────────────────────────────────────┐
   │  STPI · FREE DEMO BUILD — you are one upgrade from unlimited    │
   │  Buy: https://whop.com/jacaranda-labs                    │
   │  ⚡ SharkSkin@coinos.io   ·   Mukuru / EFT               │
   └──────────────────────────────────────────────────────────┘

2. Dashboard footer strip on every rendered page (demo.py footer_html(), ~L183):
   "Hunts stop when the demo caps run out — an upgrade takes a minute and your
    whole queue comes back to life: Buy Premium · Solo $306 · Studio $613 ·
    Sovereign $920 · pay in rands · ⚡ Lightning"
   (now in the brand palette — lilac #eef4fb panel on plum #0a1f3c ink)

3. Every demo PDF footer (demo.py pdf_note(), ~L189):
   "Prepared with STPi Demo · get the full engine: https://getstpi.pages.dev"

4. The leash itself (demo.py, ~L126): the 26th draft / 6th send attempt is not an
   error message — it is the buy message with the store link. The freeze is visible
   in the CLI, the dashboard and the bundle.

5. Trial workspace upsell (stpi-mint growth.js /trial page): "Keep going by buying
   Solo/Studio/Sovereign on Whop — your workspace upgrades in place when the same
   email pays. The wall talks."

Design note (the demo pack README says it plainly): nags everywhere, on purpose.
A trial that hides its wall converts nobody."""

# ----------------------------------------------------------------------------- sections

def page_text(path: Path, limit: int = 40000) -> str:
    """Strip an authored HTML page to its readable text, verbatim order."""
    raw = path.read_text(encoding="utf-8", errors="ignore")
    raw = re.sub(r"data:image/[^\")]{80,}", "(image)", raw)
    for tag in ("style", "script", "svg"):
        raw = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", " ", raw, flags=re.S | re.I)
    txt = re.sub(r"</(p|li|h[1-6]|tr|div|section|dd|dt|article|blockquote|pre)>", "\n", raw, flags=re.I)
    txt = re.sub(r"<br[^>]*>", "\n", txt, flags=re.I)
    txt = html.unescape(re.sub(r"<[^>]+>", "", txt))
    lines = [ln.strip() for ln in txt.splitlines() if ln.strip()]
    return "\n".join(lines)[:limit]


def sec_vault() -> str:
    files = [
        ("copy/pitch.md", "The one-screen pitch — the story every other asset borrows from"),
        ("copy/social.md", "Every social asset: launch post, threads, group posts, hashtags"),
        ("copy/cold-outreach.md", "Cold outreach: emails, WhatsApp, DMs, cadence"),
        ("copy/sales-scripts.md", "The complete sales scripts: phone, video, WhatsApp, personas, objections, closes"),
        ("copy/email-sequences.md", "Lifecycle emails: welcome, day 2/7, renewal, win-back"),
        ("copy/pricing.md", "Pricing copy and rationale"),
        ("copy/faq-objections.md", "FAQ and objection handling, verbatim"),
        ("copy/demo-script.md", "The 5-minute demo script and 45-second video shot list"),
        ("copy/sales-scripts-advanced.md", "Sales scripts vol.2 (2026-10-01): universities, outplacement RFPs, NGOs, TVET colleges, HR consultancies + universal rescue lines"),
        ("copy/cold-outreach-sequences-2.md", "Cold outreach bank 2 (2026-10-01): agencies, TVET, ZW/ZM localised, referral asks, reactivation"),
        ("copy/social-content-bank-2.md", "Social content bank 2 (2026-10-01): X singles/threads, LinkedIn formats, WhatsApp, polls, reply bank"),
        ("copy/lifecycle-emails-2.md", "Lifecycle emails set 2 (2026-10-01): day-14, trial day-6, dunning, annual, affiliate, win-back 2, founder mail"),
        ("BRAND.md", "The brand file — voice, phrases we use and never use"),
        ("whop/product_faq.md", "The Whop storefront FAQ source"),
        ("whop/faq_post.txt", "The pinned forum FAQ post, source text"),
        ("downloads/quickstart.md", "Demo kit quickstart (ships inside the zip)"),
        ("downloads/pricing.md", "Demo kit pricing sheet (ships inside the zip)"),
        ("downloads/README.txt", "The zip's README — the first file a demo user reads"),
        ("README.md", "This repo's own README — how the marketing site and bible ship"),
        ("scripts/_data/essay-pipeline.md", "OWNED PRESS — dev.to essay 1, full text (our best inbound asset)"),
        ("scripts/_data/essay-six-prompts.md", "OWNED PRESS — dev.to essay 2, full text"),
    ]
    pages = [
        ("demo.html", "The demo download page every CTA lands on — full copy incl. the §12 "
                      "“client just said yes” playbook"),
        ("setup.html", "The setup guide the demo kit links to — screenshots captions, CV designs, troubleshooting"),
        ("domain.html", "The own-domain guide — the paid sender-address feature explained to buyers"),
    ]
    parts = [
        "<h2>The copy vault — every word, verbatim</h2>",
        '<p class="lede">Nothing condensed, nothing paraphrased. These are the raw source files '
        'the rest of the bible was distilled from. When the bible and a file disagree, the file '
        f'wins — and you are reading the file here. (Snapshot {TODAY}.)</p>',
    ]
    for path, cap in files:
        p = ROOT / path
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        w = len(text.split())
        if path.endswith(".md"):
            body = md(text)
        else:
            body = f"<pre>{esc(text)}</pre>"
        parts.append(f'<h3>{path} <span class="pill">{w} words</span></h3>'
                     f'<p class="sub">{cap}</p>'
                     f'<div class="card" style="overflow-x:auto">{body}</div>')
    parts.append("<h2 style='margin-top:1.4em'>The buyer pages — every word, verbatim</h2>"
                 "<p class='sub'>The pages a buyer or demo user actually reads, stripped to text "
                 "(images become captions). Quoting from these is always safe.</p>")
    for path, cap in pages:
        p = ROOT / path
        if not p.exists():
            continue
        text = page_text(p)
        parts.append(f'<h3>getstpi.pages.dev/{path[:-5] if path != "index.html" else ""} '
                     f'<span class="pill">{len(text.split())} words</span></h3>'
                     f'<p class="sub">{cap}</p>{cb(text)}')
    return "\n".join(parts)


def sec_topics(topics: list[dict]) -> str:
    promos = [t for t in topics if t.get("kind") == "promo"]
    rest = [t for t in topics if t.get("kind") != "promo"]
    out = [
        "<h2>The promo factory — every topic, every beat</h2>",
        '<p class="lede">The autopilot writes 44 posts a day from this registry. Two value posts for '
        "every promo (2V:1P), weekends included, per-persona pages expected, replies capped at a "
        "human pace. Here is the entire ammunition locker — the same material drives press, cards, "
        "and the Whop forum. Beats are written number-free on purpose: a beat can never go stale.</p>",
        "<h3>How the factory works (one breath)</h3>",
        cb("topics.json (registry, placeholders rendered from demo.py + boards)\n"
           "  -> planner: per-hub cadence, 2V:1P gate, per-persona budgets\n"
           "  -> writer: drafts the post, editor rejects hype/fabricated stats/CTA-less promos\n"
           "  -> cards.py: brand-palette card rendered per rail (wide 1200x675, pin 1000x1500, cover 1000x420)\n"
           "  -> rails: X, LinkedIn, dev.to, Pinterest, Bluesky, Nostr, Whop public + Whop paid\n"
           "  -> witnesses: livecheck + authoring/publish witnesses report NEW failures only (digest, not spam)\n"
           "  -> weekly digest: clicks (tracked links) vs Whop sales - the only funnel scoreboard\n"
           "Hard budgets pinned in tests: 44 posts/day, 4 replies/day, weekend-on, mailbox ramps."),
        f"<h3>Registry at a glance</h3><table>"
        f"<tr><th>Bucket</th><th>Count</th><th>Notes</th></tr>"
        f"<tr><td>promo</td><td>{len(promos)}</td><td>incl. 4 affiliate-recruitment topics ({TODAY})</td></tr>"
        f"<tr><td>other (value/essay/other)</td><td>{len(rest)}</td><td>the 2 in 2V:1P</td></tr>"
        f"<tr><td>total</td><td>{len(topics)}</td><td>rendered {TODAY}; placeholders resolved from live billing</td></tr>"
        "</table>",
    ]
    def block(t: dict) -> str:
        beats = "".join(f"<li>{esc(b)}</li>" for b in t.get("beats", []))
        asset = t.get("asset") or ""
        meta = " · ".join(x for x in (t.get("id"), t.get("format"), f'audience: {t.get("audience")}' if t.get("audience") else "") if x)
        a = f' · asset: <a href="{asset}">{esc(asset[:60])}</a>' if asset.startswith("http") else (f" · asset: {esc(asset[:60])}" if asset else "")
        return (f'<div class="card"><b>{esc(t.get("title", t.get("id", "?")))}</b>'
                f'<div class="sub">{esc(meta)}{a}</div>'
                f'<p style="margin:6px 0"><i>{esc(t.get("angle", ""))}</i></p>'
                f'<ul class="tick">{beats}</ul></div>')
    out.append(f"<h3>Promo topics ({len(promos)})</h3>" + "\n".join(block(t) for t in promos))
    out.append(f"<h3>Value & other topics ({len(rest)})</h3>" + "\n".join(block(t) for t in rest))
    return "\n".join(out)


def sec_cards() -> str:
    cards = sorted((ROOT / "bible-assets" / "cards").glob("*.png"))
    wide = [c for c in cards if c.name.endswith("-x.png")]
    other = [c for c in cards if not c.name.endswith("-x.png")]
    out = [
        "<h2>The promo card gallery</h2>",
        '<p class="lede">Every autopilot post ships with a card rendered in the runner for $0 '
        "(press/cards.py). Cards are built from editor-approved text only, so an image can never "
        'say something a post could not. Palette follows the topic — same idea, same colours on '
        "every rail — and the layout rotates between quote and points so feeds don't look stamped. "
        "Promo cards carry the price strip straight from live billing.</p>",
        cb("wide   1200x675   x, linkedin, bsky, nostrnote, whop_public, whop_private\n"
           "pin    1000x1500  pinterest\n"
           "cover  1000x420   devto, nostr30023 (dev.to crops covers to 1000x420)"),
        '<style>.cg{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:14px;align-items:start}'
        ".cg figure{margin:0}.cg figcaption{font-size:11.5px;color:var(--muted,#7d97b8);margin-top:4px;word-break:break-all}"
        ".cg img{width:100%;border:1px solid var(--line);border-radius:8px;display:block}</style>",
        f"<h3>Wide cards — one per promo topic ({len(wide)})</h3>",
        '<div class="cg">' + "".join(
            f'<figure><img loading="lazy" src="bible-assets/cards/{c.name}" alt="{esc(c.stem)}">'
            f'<figcaption>{c.name}</figcaption></figure>' for c in wide) + "</div>",
        f"<h3>Pins &amp; covers ({len(other)})</h3>",
        '<div class="cg">' + "".join(
            f'<figure><img loading="lazy" src="bible-assets/cards/{c.name}" alt="{esc(c.stem)}">'
            f'<figcaption>{c.name}</figcaption></figure>' for c in other) + "</div>",
    ]
    return "\n".join(out)


def sec_media() -> str:
    def group(title: str, cap: str, items: list[tuple[str, str]]) -> str:
        figs = "".join(fig(src, note) for src, note in items if (ROOT / src.split("/")[0] if "/" not in src else (ROOT / src)).exists())
        return f"<h3>{title}</h3><p class='sub'>{cap}</p>{figs}"
    out = [
        "<h2>The media vault — every image we own</h2>",
        '<p class="lede">All of it, in one place, with what each piece is for. Files live in the '
        "repo next to this page; the bible serves the 2026 additions itself (bible-assets/), the "
        "legacy sets come from getstpi's asset store (same repo, same bytes).</p>",
    ]
    whop = [(f"whop/{n}.png", d) for n, d in [
        ("1-hero", "Whop gallery 1 of 5 — the storefront hero: what STPi is in one frame"),
        ("2-how-it-works", "Whop gallery 2 — the four-step loop for skimmers"),
        ("3-approval-card", "Whop gallery 3 — the Discord approval card, the trust shot"),
        ("4-plans", "Whop gallery 4 — the three plans knife-edge"),
        ("5-before-after", "Whop gallery 5 — the churn/pain visual"),
    ]]
    out.append(group("Storefront gallery (whop/*.png)", "The five frames every product page shows; regenerate with whop/make_gallery.py.", whop))
    gfx = [(f"graphics/{n}", d) for n, d in [
        ("discord-card-mockup.png", "The approval card mockup — the product in one picture"),
        ("social-card-hero.png", "Hero share card 1200×630 — first thing social posts lead with"),
        ("before-after.png", "The pain visual for ads and decks"),
    ]]
    out.append(group("Social graphics (graphics/)", "The original share set.", gfx))
    pins = [(f"press/img/{n}", d) for n, d in [
        ("pin-approval.png", "Static Pinterest pin — the approval card"),
        ("pin-boards.png", "Static Pinterest pin — the boards matrix"),
        ("pin-pipeline.png", "Static Pinterest pin — the pipeline"),
    ]]
    out.append(group("Pinterest statics (press/img/)", "Tailwind-era stills; dynamic pins now render from cards.py.", pins))
    embeds = [(f".embed/{n}", d) for n, d in [
        ("hero.jpg", "Legacy embed hero (inlined as base64 where used)"),
        ("mockup.jpg", "Legacy embed: the card mockup"),
        ("beforeafter.jpg", "Legacy embed: before/after"),
        ("og.jpg", "Legacy embed: og image"),
        ("icon.jpg", "Legacy embed: icon"),
    ]]
    out.append(group("Legacy embeds (.embed/)", "The base64-era hero set (.embed/b64.txt holds an inline payload).", embeds))
    ext = [
        ("bible-assets/external/stpi-logo.png", "2026-10-01: the STPi literary mark — the brand anchor going forward"),
        ("bible-assets/external/stpi-pulse.gif", "2026 kit: the living wordmark, animated pulse (760×427)"),
        ("bible-assets/external/hero-banner.png", "2026 kit: hero banner for campaigns (1540×560)"),
        ("bible-assets/external/hero-raw.png", "2026 kit: raw hero variant (1792×592)"),
        ("bible-assets/external/pricing-banner.png", "2026 kit: pricing banner for the store/decks (1540×780)"),
        ("bible-assets/external/email-preview.png", "2026 kit: the cold-mail preview shot (700×900)"),
    ]
    out.append(group("The 2026 external kit (bible-assets/external/)", "Owner-supplied kit, indexed here for the first time; also mirrored on the landing as brand-logo.png.", ext))
    illus = [(f"bible-assets/illustrations/{n}", d) for n, d in [
        ("cartoon-one-tap.png", "The one-tap approval — the coach, the phone, the machine behind: for the hero slot"),
        ("cartoon-boards-crossroads.png", "Board coverage as a night crossroads — ads and posts about the 17 boards"),
        ("cartoon-pipeline-machine.png", "The factory machine turning paper planes into approval cards — the pipeline visual"),
        ("cartoon-before-after-desk.png", "The before/after desk split — the pain visual for ads, decks and comparison posts"),
        ("cartoon-stpi-mail.png", "Under the stpi tree: the graduate, the mailbox, the paper plane — the hope shot"),
        ("cartoon-approval-gate.png", "The approval gate itself: nothing passes without the guard's hand — the trust visual"),
        ("cartoon-rand-pricing.png", "Three plan boxes on a shelf with coins and a banknote — the honest-pricing visual"),
        ("cartoon-affiliate-handshake.png", "Handshake over a stpi branch with coin sparkles — the affiliate/referral visual"),
        ("cartoon-trial-seven-days.png", "Seven calendar tabs lifting off as paper planes — the 7-day trial visual"),
    ]]
    out.append(group("Cartoon promo illustrations (bible-assets/illustrations/)",
                     "2026-10-01 set: text-free, flat stpi-palette cartoons — legal for ads, safe next to any caption, "
                     "and generated in the house palette so they sit beside the cards without clashing.", illus))
    brand_files = []
    for p in sorted((ROOT / "brand").glob("*")):
        if p.is_file() and p.suffix.lower() in (".png", ".svg", ".ico"):
            brand_files.append((f"brand/{p.name}", f"{p.name} · {file_size(p)}"))
    out.append(group("Brand marks (brand/)", "The complete STPi mark set: wordmark, mono, tile, icons, og.", brand_files))
    samples_md = """
| File | What it proves |
| --- | --- |
| samples/sample-cv-za.pdf | The ZA-format CV, generated by the engine (Thabo Nkosi) |
| samples/cv-classic.pdf | CV theme: classic |
| samples/cv-emerald.pdf | CV theme: emerald |
| samples/cv-indigo.pdf | CV theme: indigo |
| samples/cv-sunset.pdf | CV theme: sunset |
| samples/sample-cover-letter.pdf | The tailored cover letter, generated by the engine |
| samples/sample-cv-za.html / sample-cover-letter.html | The same documents as live HTML |
"""
    out.append(f"<h3>Sample documents (samples/)</h3><p class='sub'>Show them, don't describe them — "
               f"every CV theme and the letter, one tap away.</p>{md(samples_md)}")
    return "\n".join(out)


def sec_demokit() -> str:
    dl = ROOT / "downloads"
    rows = []
    for p in sorted(dl.glob("*")):
        if p.suffix == "":
            continue
        sha = ""
        s = dl / (p.name + ".sha256")
        if s.exists():
            sha = s.read_text().split()[0][:12] + "…"
        elif p.suffix == ".sha256":
            continue
        rows.append(f"<tr><td><a href='downloads/{p.name}'>downloads/{p.name}</a></td>"
                    f"<td>{file_size(p)}</td><td><code>{sha}</code></td></tr>")
    compose = (dl / "docker-compose.sovereign.yml").read_text() if (dl / "docker-compose.sovereign.yml").exists() else "(missing)"
    return "\n".join([
        "<h2>The demo kit — everything, with checksums</h2>",
        '<p class="lede">What the buyer actually downloads, opens and installs. Verify the zip '
        "against the sha beside it before you quote it; both ship from the same directory.</p>",
        "<table><tr><th>File</th><th>Size</th><th>sha256 (first 12)</th></tr>" + "".join(rows) + "</table>",
        "<h3>The demo sells everywhere — the upsell inventory</h3>",
        cb(DEMO_CTA_INVENTORY),
        "<h3>Sovereign in one file — docker-compose.sovereign.yml</h3>",
        cb(compose),
        '<h3>The kit docs</h3><p class="sub">quickstart.md, pricing.md and README.txt ship inside the zip — '
        'all three verbatim in the Copy vault tab.</p>',
    ])


TRIAL_COPY = """Try STPi on one of your candidates, free for 7 days
(stpi-mint .../trial — verbatim, fetched 2026-10-01)

For career coaches and placement agencies. We run the hunt on our servers: the boards are
checked on a schedule, every advert is matched against your candidate's real profile, and
tailored letters and CVs land in your own Discord as one card. Nothing sends until you tap.

- 1 candidate, up to 5 sends from your own Gmail, 7 days
- No card. When the 7 days end the hunt pauses; your setup is kept for 30 days
- Keep going by buying Solo, Studio or Sovereign on Whop with THIS SAME EMAIL: the workspace
  upgrades in place
- You'll need a Discord server (free), a Gmail app password and a free Groq or Gemini key:
  the setup page links all three

Form fields: business/practice name - your name - email (the one you'd buy with) - country
(SA/ZW/ZM/other) - Discord username (optional) - consent tick (terms + privacy + candidate
consent) - Start my 7-day trial.

Questions: simalidudu@gmail.com"""


def sec_storefront() -> str:
    drift = """
| Where | Says | The landing says | Status |
| --- | --- | --- | --- |
| Whop Solo product page | "3 candidates, 100 sends a month" | 5 candidates | conflict — owner decides, one edit |
| Whop Studio product page | "15 candidates, fair-use sends" | 25 candidates | conflict — owner decides, one edit |
| Whop pinned FAQ post | demo link = old stpi-cloud.github.io URL | getstpi.pages.dev | stale — update the pin |
| Whop pinned FAQ post | Solo/Studio candidate counts | (same two drifts) | one edit fixes all |
"""
    affiliate = cb("""AFFILIATE PROGRAM — status 2026-10-01: NOT YET ENABLED on the store.
No affiliate surface visible on any product page (checked live).

The one toggle that unlocks it (60 seconds, owner-only):
  Whop dashboard -> each product (Solo / Studio / Sovereign) -> Affiliates ->
  enable + set commission.
Recommended: 30% of first month — it mirrors the field-agent agreement exactly
(recurring-anything overpays before volume justifies it).

Once it's on, these four promo topics recruit automatically through whop_public
and the social mix (number-free copy, true before and after the toggle):
  - promo-affiliate-coaches   "Recommend stpi, get paid for it"
  - promo-affiliate-demo-sells "The easiest referral is a demo they can click"
  - promo-affiliate-recurring "One referral, paid again every month it stays"
  - promo-affiliate-proof     "Sell the pipeline, not a promise"

House rule: seller-a sells via EITHER agent commissions OR affiliate links,
never both — the lead ledger decides per lead (doc 12 addendum).""")
    return "\n".join([
        "<h2>Storefront ops — Whop, verbatim and audited</h2>",
        f'<p class="lede">The three live product copies exactly as published (fetched {TODAY}), '
        "so nobody works from memory. Beneath them: the drift audit and the one lever still "
        "waiting on the owner.</p>",
        "<h3>STPi Solo — whop.com/jacaranda-labs/products/stpi-solo/</h3>", cb(SOLO_COPY),
        "<h3>STPi Studio — whop.com/jacaranda-labs/products/stpi-studio/</h3>", cb(STUDIO_COPY),
        "<h3>STPi Sovereign — whop.com/jacaranda-labs/products/stpi-sovereign/</h3>", cb(SOVEREIGN_COPY),
        "<h3>Copy drift audit (found 2026-10-01 — manual copy the machine can't write)</h3>", md(drift),
        "<h3>The hosted 7-day trial page — verbatim</h3>", cb(TRIAL_COPY),
        "<h3>Affiliates</h3>", affiliate,
        "<h3>The pinned forum FAQ</h3><p>Source text lives in whop/faq_post.txt (Copy vault). "
        "The version currently pinned on the store is 6+ days old and carries the drifts above — "
        "press can post new threads but cannot edit pins, so the pin is an owner's-edit job.</p>",
    ])


def numbers_ledger() -> str:
    """Live product numbers straight from stpi/press/facts.py — the render source for every post."""
    if not STPI.exists():
        return "<p><i>(stpi checkout not found — ledger unavailable)</i></p>"
    import sys
    sys.path.insert(0, str(STPI / "press"))
    try:
        import facts
        bill = facts.billing()
    except Exception as e:  # noqa: BLE001
        return f"<p><i>(facts import failed: {esc(repr(e)[:100])})</i></p>"
    rows = "".join(f"<tr><td><code>{esc(str(k))}</code></td><td>{esc(str(v))}</td></tr>"
                   for k, v in sorted(bill.items()))
    return ("<h3>The numbers ledger (rendered from live code, every build)</h3>"
            "<p class='sub'>These exact values fill the placeholders in every post, card and topic. "
            "Change the code, re-render the registry, re-run this builder — the bible can never "
            "quote a number the product doesn't.</p>"
            f"<table><tr><th>Fact key</th><th>Value</th></tr>{rows}</table>")


def sec_machine(landing_copy: str, faqs: list) -> str:
    cadence = """
| Rail | Cadence | Notes |
| --- | --- | --- |
| X | ≥3 posts/day/persona × 2 personas + replies | mandatory both personas, tracked links |
| LinkedIn | ≥3 posts/day | mandatory, company + persona voice |
| dev.to | 3/day | per-persona author pages expected |
| Pinterest | daily pins | dynamic card pins from cards.py |
| Bluesky / Nostr | daily | niche value, low competition |
| Whop public forum | 1/day | store community: field notes, affiliate recruitment |
| Whop paid (members) | as-it-happens | onboarding + status for paying tenants |
| Ratio | 2 value : 1 promo | enforced in the planner, weekends included |
| Replies | 4/day cap | human pace, questions first |
| Cold outreach | composed 08:21 weekdays | one owner tap sends the batch (mailbox ramps) |
| Topic factory | Mondays | LLM-assisted generation, lessons-learned pruning |
"""
    mirrors = """
| Host | Serves | Deployed by | Owner repo |
| --- | --- | --- | --- |
| getstpi.pages.dev | The buyer site: landing, demo, setup, domain, downloads, samples | pages-deploy.yml | stpi (landing/ owns the WHOLE site, 2026-10-01) |
| stpi-a.pages.dev | Seller-a mirror (host refs swapped by sed in CI) | pages-deploy.yml same run | stpi |
| stpi-mint.workers.dev | Trials, licences, Discord relay, press image hosting | mint deploy on push | stpi-mint |
| stpi-mint-a.workers.dev | Seller-a mint mirror (SITE_BASE -> stpi-a) | mint deploy same run | stpi-mint |
| stpi-bible.pages.dev | This bible (internal, noindex) | cf-pages.yml | stpi-marketing (bible-only from 2026-10-01) |
"""
    journey = """
| Moment | What happens | Human touches |
| --- | --- | --- |
| Discover | Buyer hits getstpi.pages.dev from a tracked post | none |
| Try | One tap downloads stpi-demo-1.0.1.zip (or starts the hosted 7-day trial on Whop) | none |
| Set up | /setup walkthrough: install, first candidate, first draft | none (the self-serve panel links every how-to) |
| Hit the wall | Caps freeze the pipeline — visibly, with the buy link (see Demo kit) | none |
| Buy | Whop checkout (card $, rands R, Lightning, Mukuru/EFT, annual by wire) | none |
| Onboard | Whop webhook mints the tenant; Discord /claim opens the private channel + invite | none |
| Add candidates | /start wizard: Discord + Gmail app password + LLM key, each with how-to links; ➕Add or 🔗Invite per candidate | owner's taps on approvals only |
| Operate | Nightly hunts, approval cards, interview flags, monthly interview report | taps only |
| Grow | Solo -> Studio upgrade nudges by lifecycle mail | none |
"""
    grind = """
| Mix to ~$10k/mo gross | Count |
| --- | --- |
| All Sovereign | 11 × $920 = $10,120 |
| All Studio | 17 × $613 = $10,421 |
| All Solo | 33 × $306 = $10,098 |
| Fastest blend | 5 Studio + 5 Solo + 2 Sovereign = $9,435 (one good seller month) |
| Realistic blend | 2 Sovereign + 6 Studio + 10 Solo = $8,578 + affiliate flow |

Owner's only manual moves: daily (~15 min) tap the outreach batch, tap approval cards,
read witness alerts once. Weekly (~2 h): coach the sellers, one storefront tweak guided by
clicks-vs-sales, update the pinned FAQ until drift is gone. Monthly: seller-b provisioning
decision, Nigeria/NDPA go-call. Everything else is automated at $0 + free-tier keys.
"""
    faq_html = "".join(f"<details><summary><b>{esc(q)}</b></summary><p>{esc(a)}</p></details>"
                       for q, a in faqs[:60])
    faq_html = faq_html or "<p><i>(landing FAQ snapshot missing)</i></p>"
    return "\n".join([
        "<h2>The 2026 machine — how sales run without us</h2>",
        '<p class="lede">The bible used to end at "what to say". This tab is how the machine says '
        "it, hosts it, watches itself, and turns clicks into tenants — plus what is genuinely left "
        "for a human. No secrets here: tokens, webhook URLs and IDs live only in the private ops docs.</p>",
        "<h3>Cadence and budgets (pinned by tests — drift fails CI)</h3>", md(cadence),
        numbers_ledger(),
        "<h3>Who deploys what (the ownership table that prevents accidents)</h3>", md(mirrors),
        '<p class="sub">Lesson burned in on 2026-10-01: Pages serves the union of everything ever '
        "deployed while missing files fall back to index.html with a 200 — two workflows owning one "
        'project deployed a half-split site for a day. Now one workflow owns one project, and the '
        "smoke step fails the run if any deep page ever falls back again.</p>",
        "<h3>The systems that watch the machine</h3>",
        cb("livecheck          the probe the owner runs: site, mirrors, mint, demo, store — one page of green\n"
           "authoring witness  the writer's failures surface as digests, never silent drafts lost\n"
           "publish witness    per-rail publish outcomes, breaker parks a rail that keeps failing\n"
           "weekly digest      clicks vs Whop sales — the only funnel scoreboard worth watching\n"
           "ban hygiene        walls: warmup ramps, caps, quiet hours, one-CTA rule — pinned by tests"),
        "<h3>Self-serve journey (buy to operate with zero contact)</h3>", md(journey),
        "<h3>The grind — what is left for a human</h3>", md(grind),
        "<h3>Runbook library</h3><p class='sub'>Every operational doc, indexed from the ops repo "
        f"(snapshot {TODAY}).</p>", docs_index(),
        "<h3>The landing FAQ — verbatim (what a buyer reads before deciding)</h3>",
        f"<div class='card'>{faq_html}</div>",
        "<h3>The landing page — verbatim copy (every word a buyer can read)</h3>",
        cb(landing_copy),
    ])


def sec_brand2() -> str:
    palette = """
| Token | Hex | Role |
| --- | --- | --- |
| Lilac | #eef4fb | light surfaces (brand hone) |
| Plum ink | #0a1f3c | primary ink / night surface |
| STPi | #14365e | primary accent — buttons, links, marks |
| Mauve | #7d97b8 | muted text on lilac |
| Night accent | #a4c5e0 | accent on plum |
| Night muted | #afbdc9 | muted on plum |
| Paper | #FBF7EF | warm paper surface |
| Paper muted | #756C62 | muted on paper |
| Gold kick | #C6803C | the one allowed contrast accent |
| Brand muted | #e1ecf5 | muted on brand fill |
"""
    voice = cb("""Wordmark-only. We never ship a logo lockup with an icon we didn't draw ourselves.
Lead colour: stpi purple. "Colours, not noise."
Display voice: Georgia serif for the one headline that matters; system sans elsewhere.
The mark: the five-bell stpi blossom — drawn, never borrowed.
Skin everything customer-facing: landing, mirrors, trial pages, cards, owner PDFs.""")
    coverage = """
| Surface | Brand 2.0 status (2026-10-01, live-verified) |
| --- | --- |
| getstpi.pages.dev | eyebrow wordmark, brand palette, literary logo, self-serve panel |
| stpi-a.pages.dev | same, mirrored with -a host refs |
| stpi-mint /trial | brand palette on the trial workspace |
| stpi-mint-a | same + SITE_BASE -> stpi-a |
| press cards | PALETTES = brand tokens; footer "STPi · job-hunt mechanics" |
| this bible | v3.0 — the vault + brand 2.0 tab |
"""
    return "\n".join([
        "<h2>Brand 2.0 — the STPi refresh (2026-10-01)</h2>",
        '<p class="lede">The house is STPi; STPi is the engine. Everything '
        "customer-facing wears the same coat, and this is the pattern book.</p>",
        "<h3>Palette</h3>", md(palette),
        "<h3>Doctrine</h3>", voice,
        fig("bible-assets/external/stpi-logo.png", "The STPi literary mark — brand anchor"),
        fig("bible-assets/external/stpi-pulse.gif", "The living wordmark (animated)"),
        "<h3>Coverage</h3>", md(coverage),
    ])


PLAYS_LEDE = "Brand-safe operating plays per tier. Not new claims — every line traces to the pitch, the scripts, or the storefront copy in the Copy vault."

PLAYBOOKS_MD = """
## Solo — the independent coach

**Who buys.** One-person career coaches and job agents with 1–5 paying clients and a Sunday
that dies in CV Word files. Not job seekers themselves — say so early, it saves both sides an hour.

**The moment.** They just lost a client to "I found one myself" or they just took client #3
and physically cannot hand-write three more tailored letters a week. Sell into that week.

**The demo move.** "Load your hardest current client into the demo tonight. One candidate,
free forever. When the first approval card lands in your Discord, forward it to your client
without comment." The card sells; you go quiet.

**What Solo is.** 3 candidates, 100 sends a month, priority slots, Discord approvals. Their
mailbox, their name, their client sees their brand. Rands checkout exists; so does the $2754
annual wire (25% off) for the coach who hates subscriptions.

**Kill shot.** "You bill by the client, not by the hour. STPi is the only hire that works
nights, never phones in sick, and asks permission before it acts."

**Common stall.** "I can do this with ChatGPT." True — and the six-prompt essay (Copy vault)
literally teaches that. The counter: prompts don't hunt boards at 06:00 SAST, don't purge
PDFs at 72 h, don't cap your sends so your mailbox stays out of spam. They are buying the
ops, not the words.

## Studio — the practice with a name to protect

**Who buys.** Coaching studios and boutique agencies: 2–10 consultants, a brand on the
letterhead, clients who must never see a second-party logo.

**The moment.** The founder just hired consultant #2 and quality became a lottery. Or a
client asked "where does my CV actually go?" and the answer embarrassed them.

**The demo move.** Same as Solo, then in the walkthrough open a sample PDF (Media vault ->
samples) and ask whose name is on it. White-label PDFs are the Studio sentence that matters;
say it once: "PDFs branded as your agency."

**What Studio is.** 15 candidates, fair-use sends, white-label documents, the LLM fallback
chain (one provider outage never stops Friday's run). Rands at R9,999; annual wire at $5,517.

**Kill shot.** "Solo makes one coach faster. Studio makes five coaches look like ten —
under one letterhead."

**Common stall.** "Per-seat pricing?" No. Per-practice. The counter: compare to one
consultant's billable week, not to a SaaS seat.

## Sovereign — the institution

**Who buys.** Institutions and agencies whose counsel asks data questions first: universities,
outplacement firms, NGOs running workforce programmes, corporates with POPIA-sensitive
employee data during restructures.

**The moment.** Procurement asked for the data-flow diagram and every SaaS answer ended in
"trust us." Sovereign's answer fits in one sentence: your data never leaves your servers.

**The demo move.** Don't demo first. Send the architecture one-liner from the Engine tab
plus the compose file (Demo kit). Let their engineer run `docker compose up` on a Tuesday
afternoon; the signed licence arrives in their Discord after checkout.

**What Sovereign is.** Self-hosted Docker, unlimited candidates and sends, signed offline
licence, install help in their private channel, lapsed licence = read-only, never bricked.
$920/mo, R15 000 in rands, $8 280 annual by wire.

**Kill shot.** "You're not buying a subscription, you're buying the keys. If we vanished
tomorrow your pipeline keeps hunting."

**Common stall.** "Self-hosted means maintenance." The counter: it is one compose file and
a scheduler; upgrades are an image pull. They already maintain mail servers — this is lighter.

## The upgrade staircase (sell the next tier before they ask)

Solo -> Studio triggers: the 4th candidate conversation, the "can the letter say our name"
question, a second consultant joining. Studio -> Sovereign triggers: the compliance
questionnaire, the institutional RFP, the data-residency sigh. Move people the week the
trigger fires — the lifecycle mails (Copy vault) watch for it, the human closes it.

## Channel plays — same truth, different rooms

**X** — opener is the card or the number, never the feature list; one CTA (the demo);
3+/day/persona; threads for the pipeline story, singles for proof. The six-prompt essay
endlessly re-quoted beats any ad.

**LinkedIn** — the coach's-platform voice: slower, first-person, one lesson per post;
the approval-card screenshot outperforms every polished graphic. Mandatory daily;
company page + persona both.

**dev.to** — we do not market there, we teach. Essays and topic-driven how-tos; the only
CTA lives at the end and it is the demo. 3/day across the two personas; per-persona author
pages carry the trust.

**Pinterest** — visual proof only: pins from cards.py (card, boards, pipeline). Search
traffic compounds; pin daily, forget the feed exists, check the digest monthly.

**Nostr / Bluesky** — niche, technical, zero ad-speak; mirror the essays, answer questions,
leave. Daily presence, weekly value.

**Whop public forum** — the store's own front porch, 1/day: field notes from real runs,
branded card images, trial /g/ links, and (once the owner flips it) the affiliate
recruitment topics (see Storefront tab). Never copy-paste a social post verbatim here —
the forum rewards shop talk, bills hype.

**Whop paid (members)** — not a billboard: onboarding notes, status, fairness. Members
who feel informed renew; members who feel marketed at, refund.

## What never leaves this building (reminders that outrank any playbook)

Nothing sends without a human tap - that is the product, so it is also the pitch.
No invented stats, ever: beats are number-free; numbers live in the ledger and are dated.
The demo is "free forever", never a "free trial" (the hosted trial is the 7-day one).
One CTA per artifact. Two value posts per promo. The human is the hero.
"""

def sec_playbooks() -> str:
    return "\n".join([
        "<h2>Playbooks — tier by tier, channel by channel</h2>",
        "<p class='lede'>" + PLAYS_LEDE + "</p>",
        md(PLAYBOOKS_MD),
    ])



def sec_record() -> str:
    """The published record: whop forum verbatim, dev.to index + recent bodies, press ledger."""
    parts = [
        "<h2>The published record — what has actually shipped</h2>",
        '<p class="lede">Not plans, not drafts: the public posting record itself. The forum '
        "archive is verbatim (including its two superseded github.io links, preserved so the "
        "record stays honest), the dev.to index is the full author history, and the press ledger "
        "summarises every shot the autopilot has taken. Refreshed by re-running the builder.</p>",
    ]
    archive = DATA / "whop-forum-archive.md"
    if archive.exists():
        parts.append("<h3>The Whop public forum — verbatim (fetched 2026-10-01)</h3>"
                     + md(archive.read_text()))
    idx = DATA / "devto-index.json"
    if idx.exists():
        arts = json.loads(idx.read_text())
        months: dict[str, int] = {}
        for a in arts:
            months[a["published_at"][:7]] = months.get(a["published_at"][:7], 0) + 1
        rows = "".join(f"<tr><td>{m}</td><td>{n}</td></tr>" for m, n in sorted(months.items(), reverse=True))
        parts.append(f"<h3>dev.to author record — {len(arts)} posts indexed</h3>"
                     "<p class='sub'>Era counts before the list: the May-era is the persona's "
                     "legacy listings phase (index-only, off-mission); Sep 19+ is the stpi press era.</p>"
                     f"<table><tr><th>Month</th><th>Posts</th></tr>{rows}</table>")
        era = [a for a in arts if a["published_at"] >= "2026-09-19"]
        listing = "".join(
            f'<tr><td>{a["published_at"][:10]}</td><td><a href="{a["url"]}">{esc(a["title"])}</a></td>'
            f'<td>{esc(", ".join(a.get("tags", [])[:4]))}</td></tr>'
            for a in era)
        parts.append("<h4>The stpi-era posts (full-text where vendored below)</h4>"
                     f"<table><tr><th>Date</th><th>Post</th><th>Tags</th></tr>{listing}</table>")
        legacy = "".join(
            f'<tr><td>{a["published_at"][:10]}</td><td><a href="{a["url"]}">{esc(a["title"])}</a></td></tr>'
            for a in arts if a["published_at"] < "2026-09-19")
        parts.append(f"<details><summary>Legacy index ({len(arts) - len(era)} earlier posts, title + date only)</summary>"
                     f"<table>{legacy}</table></details>")
    for f in sorted(DATA.glob("devto-*.md")):
        text = f.read_text()
        parts.append(f"<h4 style='margin-top:1em'>{esc(f.stem[6:])}</h4>"
                     f'<div class="card">{md(text)}</div>')
    stp = STPI / "press" / "auto" / "state.json"
    if stp.exists():
        st = json.loads(stp.read_text())
        pub = st.get("published", [])
        by_plat: dict[str, int] = {}
        by_day: dict[str, int] = {}
        fails = 0
        for e in pub:
            by_plat[e.get("platform", "?")] = by_plat.get(e.get("platform", "?"), 0) + 1
            by_day[e.get("ts", "")[:10]] = by_day.get(e.get("ts", "")[:10], 0) + 1
            fails += 0 if e.get("ok", True) else 1
        prow = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in sorted(by_plat.items()))
        drow = "".join(f"<tr><td>{d}</td><td>{n}</td></tr>" for d, n in sorted(by_day.items())[-14:])
        parts.append("<h3>The press ledger (from the live autopilot state)</h3>"
                     f"<p class='sub'>{len(pub)} publish attempts recorded; {fails} failed. "
                     "Failures are witnessed, never silent - the publish witness reports them.</p>"
                     f"<div class='two'><table><tr><th>Rail</th><th>Attempts</th></tr>{prow}</table>"
                     f"<table><tr><th>Day</th><th>Attempts</th></tr>{drow}</table></div>")
    return "\n".join(parts)



BUILDERS = {
    "vault": sec_vault,
    "topics": lambda: sec_topics(load_topics()),
    "cards": sec_cards,
    "media": sec_media,
    "demokit": sec_demokit,
    "storefront": sec_storefront,
    "machine": lambda: sec_machine(*landing_parts()),
    "brand2": sec_brand2,
    "playbooks": sec_playbooks,
    "record": sec_record,
}


def main() -> None:
    page = ROOT / "index.html"
    text = page.read_text(encoding="utf-8")

    nav_buttons = (NAV_BEGIN + "\n    "
                   + "\n    ".join(f'<button data-s="{tid}">{label}</button>' for tid, label in TABS)
                   + "\n    " + NAV_END)
    block = (SEC_BEGIN + "\n"
             + "\n".join(f'<section class="page" id="{tid}">\n{BUILDERS[tid]()}\n</section>'
                         for tid, _ in TABS)
             + "\n" + SEC_END)

    if NAV_BEGIN in text and NAV_END in text:
        i = text.index(NAV_BEGIN)
        j = text.index(NAV_END, i) + len(NAV_END)
        text = text[:i] + nav_buttons + text[j:]
    else:
        text = text.replace("</nav>", nav_buttons + "\n  </nav>", 1)

    if SEC_BEGIN in text and SEC_END in text:
        i = text.index(SEC_BEGIN)
        j = text.index(SEC_END, i) + len(SEC_END)
        text = text[:i] + block + text[j:]
    else:
        text = text.replace("</main>", block + "\n</main>", 1)

    text = re.sub(r"the marketing bible · v[0-9.]+[^<]*(?=</span>)",
                  "the marketing bible · v3.3 · 2026-10-05 — vault + published record + cartoon illustrations + "
                  "copy expansion: 92 topics · 129 cards · 400-post dev.to index · 9 cartoons (6 recompressed ~60 percent lighter) · "
                  "advanced scripts/outreach/social/lifecycle vol.2",
                  text, count=1)
    text = re.sub(r"the bible v[0-9.]+ \([^)]*\)",
                  "the bible v3.3 (2026-10-05: vault + record + illustrations + copy vol.2 + 3 promo cartoons, all recompressed)", text, count=1)

    page.write_text(text, encoding="utf-8")
    total = words_of(re.sub(r"data:image/[^\"]{80,}", "", text))
    print(f"bible written: {page.stat().st_size//1024} KB, ~{total} words of visible text")
    for tid, _ in TABS:
        print(f"  tab {tid}: ok")


if __name__ == "__main__":
    main()

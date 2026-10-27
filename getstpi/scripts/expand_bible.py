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
TODAY = "2026-10-11"

NAV_BEGIN = "<!-- AUTO-NAV:BEGIN -->"
NAV_END = "<!-- AUTO-NAV:END -->"
SEC_BEGIN = "<!-- AUTO-SECTIONS:BEGIN -->"
SEC_END = "<!-- AUTO-SECTIONS:END -->"

TABS = [
    ("vault", "Copy vault"),
    ("topics", "Promo topics"),
    ("cards", "Card gallery"),
    ("kit", "Promo kit"),
    ("media", "Media vault"),
    ("demokit", "Demo kit"),
    ("storefront", "Storefront"),
    ("machine", "The machine"),
    ("brand2", "Brand 2.0"),
    ("playbooks", "Playbooks"),
    ("record", "Published record"),
    ("techguide", "Technical guide"),
    ("ownerguide", "Owner guide"),
    ("clientguide", "Client guide"),
    ("manuals", "Manuals"),
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
- country-specific sources (keys and availability vary) across South Africa, Zimbabwe and Zambia
- Human approval on every send

$306/mo (about R4,999) billed every 30 days, or R4,999/mo in rands, or $2,754/yr
(about R45,000) prepaid by bank wire. Cancel any time.

FAQ
Does anything send without me? No. Each application is a Discord card; nothing goes
out until you tap Approve.
Can I try first? Yes, free demo pack (1 candidate, five sends per UTC month, free forever):
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
- country-specific sources (keys and availability vary) across South Africa, Zimbabwe and Zambia
- Human approval on every send

$613/mo (about R9,999) billed every 30 days, or R9,999/mo in rands, or $5,517/yr
(about R90,000) prepaid by bank wire. Cancel any time.

FAQ
Does anything send without me? No. Each application is a Discord card; nothing goes
out until you tap Approve.
Can I try first? Yes, free demo pack (1 candidate, five sends per UTC month, free forever):
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
- country-specific sources (keys and availability vary) across South Africa, Zimbabwe and Zambia
- Human approval on every send
- Lapsed licence = read-only, never bricked or deleted

$920/mo (about R15,000) billed every 30 days, or R15,000/mo in rands, or $8,280/yr
(about R135,000) prepaid by bank wire. Cancel any time.

FAQ
Does anything send without me? No. Each application is a Discord card; nothing goes
out until you tap Approve.
Can I try first? Yes, free demo pack (1 candidate, five sends per UTC month, free forever):
https://getstpi.pages.dev/
Pay in rands? Yes: rand checkouts at R4,999/mo / R9,999/mo / R15,000/mo.
Annual: one bank-wire payment, 25% off.
No card? Lightning (SharkSkin@coinos.io) or Mukuru / EFT (+263 78 460 0904, ref = tenant id).
Full FAQ in the STPi forum. Questions: simalidudu@gmail.com"""

DEMO_CTA_INVENTORY = """The demo sells at every surface (verified in stpi/demo.py, 2026-10-01):

1. CLI banner on every invocation (demo.py cli_banner(), ~L201):
   ┌──────────────────────────────────────────────────────────┐
   │  STPI · FREE DEMO BUILD — you are one upgrade from unlimited    │
   │  Buy: https://whop.com/stpi                    │
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
        ("copy/emotion-engine.md", "The Emotion Engine (2026-10-14): AFGR selling system — anger/fear/greed/relief sequence, buyer Diagnosis, question bank, 20-min call, red lines"),
        ("copy/sales-scripts-emotion.md", "Sales scripts — Emotion Engine set (2026-10-14): AFGR openers, discovery, 20-min call, closes, objection-as-emotion-deficit, post-demo rotation"),
        ("copy/cold-outreach-emotion-rotation.md", "Cold outreach — emotion rotation (2026-10-14): anger→fear→greed→relief→loss touches, persona swaps, reactivation"),
        ("copy/one-pager-partner.md", "The one-pager (2026-10-14): fill-in leave-behind for the partner/principal who was not on the call"),
        ("copy/emotional-scorecard.md", "Emotional scorecard & pre-call Diagnosis (2026-10-14): 10-point call scoring, Diagnosis sheet, emotion funnel metrics"),
        ("BRAND.md", "The brand file — voice, phrases we use and never use"),
        ("whop/product_faq.md", "The Whop storefront FAQ source"),
        ("whop/faq_post.txt", "The pinned forum FAQ post, source text"),
        ("downloads/pricing.md", "Demo kit pricing sheet"),
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


def sec_kit() -> str:
    """The promo kit (owner 2026-10-14): 40 ready-to-post materials, every channel format,
    cards beside the copy. Press takes these first for promo slots; the owner can lift any
    entry straight into a social."""
    import json as _json
    src = ROOT / "bible-assets" / "promo-kit" / "promo-kit.json"
    if not src.exists():
        return "<h2>The promo kit</h2><p class='sub'>promo-kit.json missing - run press/promo_kit.py</p>"
    mats = _json.loads(src.read_text())["materials"]
    themes: dict[str, list] = {}
    for m in mats:
        themes.setdefault(m["theme"], []).append(m)
    fmt_label = {"x": "X post", "bsky": "Bluesky", "linkedin": "LinkedIn", "facebook": "Facebook",
                 "telegram": "Telegram channel", "whatsapp": "WhatsApp status",
                 "pinterest": "Pinterest pin", "thread": "Thread opener", "whop_public": "Whop post"}
    n_illus = sum(1 for m in mats if m.get("type") == "illustration")
    out = [
        f"<h2>The promo kit - {len(mats)} ready-to-post materials</h2>",
        '<p class="lede">Every entry is one promotional message in nine channel formats. '
        f"{len(mats) - n_illus} are text cards (wide for X/LinkedIn/Bluesky/Telegram/Facebook, "
        f"pin for Pinterest) built from editor-approved copy; {n_illus} are cartoon "
        "illustrations - hand-styled pictures with short captions, the art is the material. "
        "Copy passes the same editor gates as authored posts: one pointer link, prices "
        "exactly as billing writes them, no hype vocabulary. The autopilot takes the next "
        "unused material per rail before authoring anything; a rail that burns the kit "
        "falls back to authored promo. Rebuild with <code>python3 press/promo_kit.py</code>.</p>",
        '<style>.pk{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:18px;'
        "align-items:start}.pk .box{border:1px solid var(--line,#2a3a52);border-radius:10px;"
        "padding:12px;background:rgba(127,151,184,.05)}.pk h4{margin:0 0 6px;font-size:14px}"
        ".pk img{width:100%;border:1px solid var(--line);border-radius:8px;display:block;margin:6px 0}"
        ".pk pre{white-space:pre-wrap;word-break:break-word;font-size:11.5px;margin:4px 0;"
        "padding:8px;border:1px dashed var(--line,#2a3a52);border-radius:6px}"
        ".pk .th{font-size:11px;text-transform:uppercase;letter-spacing:1.4px;"
        "color:var(--muted,#7d97b8);margin-top:8px}</style>",
    ]
    n = 0
    for theme in sorted(themes):
        out.append(f'<h3 id="kit-{esc(theme)}">{esc(theme)} - {len(themes[theme])} materials</h3>')
        out.append('<div class="pk">')
        for m in themes[theme]:
            n += 1
            out.append('<div class="box">')
            out.append(f'<h4>{n}. {esc(m["headline"])}</h4>')
            out.append(f'<div class="th">{esc(m["id"])} · link: {esc(m["link"])}</div>')
            out.append(f'<img loading="lazy" src="bible-assets/promo-kit/{m["id"]}-x.png" '
                       f'alt="{esc(m["headline"])} wide card">')
            out.append(f'<img loading="lazy" src="bible-assets/promo-kit/{m["id"]}-pin.png" '
                       f'alt="{esc(m["headline"])} pin card" style="max-width:220px">')
            for fmt in ("x", "linkedin", "facebook", "telegram", "whatsapp", "pinterest", "thread"):
                out.append(f'<div class="th">{fmt_label[fmt]}</div>')
                out.append(f"<pre>{esc(m['formats'][fmt])}</pre>")
            out.append("</div>")
        out.append("</div>")
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
        ("cartoon-boards-crossroads.png", "Board coverage as a night crossroads — ads and posts about the selected public sources"),
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
        '<h3>The kit photo guides</h3><p class="sub">STPi-Customer-Photo-Guide.{pdf,html} and STPi-Photo-Guide-demo.{pdf,html} ship inside the zip — '
        'no raw-text setup guides.</p>',
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
        "<h3>STPi Solo — whop.com/stpi/products/stpi-solo/</h3>", cb(SOLO_COPY),
        "<h3>STPi Studio — whop.com/stpi/products/stpi-studio/</h3>", cb(STUDIO_COPY),
        "<h3>STPi Sovereign — whop.com/stpi/products/stpi-sovereign/</h3>", cb(SOVEREIGN_COPY),
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
| Try | One tap downloads stpi-demo-1.0.2.zip (or starts the hosted 7-day trial on Whop) | none |
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

### The 8-week sprint: $10k/mo by 2026-12-09

*Day 1 is Friday 2026-10-09. The deadline is Wednesday 2026-12-09 — 61 days,
~8.5 weeks. This is the only plan in this bible with a date on it, and the
only one that is ordered: do the earlier thing before the later thing,
every day. Nothing below requires budget, headcount, or product changes —
only hours, in the right order.*

**The target, stated twice.** (1) MRR run-rate ≥ $10k/mo by Dec 9 — recurring
revenue, not vibes. (2) Cash collected along the way ≥ $10k — money in hand.
Annual prepays count in full toward (2) and 1/12th toward (1). Both numbers
come from the Whop dashboard, never from memory.

**The arithmetic.** Whop takes ~3% + processing, so $10k net means ~$10.5k
gross. Any of these mixes clears it:

| Mix | Customers | Gross/mo |
| --- | --- | --- |
| Balanced: 3 Sovereign + 7 Studio + 12 Solo | 22 | $10,723 |
| Studio-heavy: 17 Studio | 17 | $10,421 |
| Whale: 11 Sovereign | 11 | $10,120 |

That is ~3 new paying customers per week, every week, for 8 weeks. The weekly
number is the scoreboard — not traffic, not followers, not feelings.

**The cash accelerator.** One Studio annual ($5,517) plus one Sovereign annual
($8,280) is $13,797 cash from two deals. Every quote shows the monthly price
first and the annual second (pricing law: never discount the price, only the
arithmetic). Sell annuals from week 1 — cash de-risks the sprint long before
MRR compounds.

**The weekly ladder.**

| Week | Dates | New paying | Cumulative | Focus |
| --- | --- | --- | --- | --- |
| W1 | Oct 9–15 | 2 | 2 | Pipes + first blood: cold machine verified end-to-end, affiliate toggle decided, review ask scripted, trial day-1 delivery working |
| W2 | Oct 16–22 | 2 | 4 | First repeatable close: the same script closes twice |
| W3 | Oct 23–29 | 3 | 7 | Affiliates live: 5 active, recruited on the 30%/12-month math |
| W4 | Oct 30–Nov 5 | 3 | 10 | Referral engine: every customer asked for a review + one name |
| W5 | Nov 6–12 | 3 | 13 | Discover watch: first review unlocks the listing, push traffic there |
| W6 | Nov 13–19 | 3 | 16 | Annual push: every open trial and customer gets the annual quote |
| W7 | Nov 20–26 | 3 | 19 | Double the winner: best channel gets 2× hours |
| W8 | Nov 27–Dec 4 | 3 | 22 | Close the gap + MRR audit; Dec 5–9 is buffer for stragglers |

**The daily workflow (CAT, in order — no skipping ahead).**

1. **07:30 — Reply queue to zero.** Every reply less than 24h old gets
   answered before anything else. Money before machine.
2. **08:00 — Cold machine.** Pull 30 leads (BATCH_CAP 30), QA each one (right
   person, right company, no dupes), confirm the 08:21 compose is queued.
   Caps live in scripts/outreach.py: DRIP_PER_RUN 5, DAILY_CAP 50/mailbox.
3. **09:00 — Founder selling, 2 hours.** Follow-ups, demos, trial check-ins
   (day 1/3/7 of every trial). No building in this block.
4. **11:00 — Content batch.** Owner non-negotiables: X (3 posts × 2 personas
   + replies), LinkedIn (3) — every link tracked (?src=). The press autopilot
   runs the scheduled rails (X, LinkedIn, Pinterest, Bluesky, Nostr, Whop —
   see the Press ledger); the owner covers replies and re-posts anything the
   witness log flags failed.
5. **12:00 — Whop forum.** One value post, answer every open thread, recruit
   affiliates (5 new/week — the pitch is the math: one Studio referral pays
   $184/mo for 12 months, $2,207 total).
6. **14:00 — Long rails.** dev.to (manual, per-persona — sprint floor is 3
   posts/week); Pinterest top-up from cards.py; queue Bluesky/Nostr.
7. **15:00 — Pipeline hygiene, 30 min.** Move stages, kill dead leads, prep
   tomorrow's 30.
8. **Friday 15:00 — Weekly review** (scoreboard below) instead of hygiene.

**Lean mode: the same sprint in ~3h/day (switch after W1, not before).**

*Full mode above is ≈7h/day. Once every automation below has been green for 7
straight days, the same machine runs lean: ≈3h on normal days, ≈5h on Tue/Thu
call days, Friday +review. Nothing is dropped — volume moves to machines, the
owner keeps judgment. Run full mode in W1 so you learn what green looks like;
switch to lean only when you can tell green from silent.*

*What the machines already carry (verified 2026-10-09): lead intake fills D1
once a day Mon–Sat (leads-hunt.yml 07:23 SAST); the 08:21 weekday compose queues
the batch and posts its card (outreach.yml); replies are triaged 3×/day —
opt-outs→DNC, bounces→dead, real replies→owner ping; the press autopilot
publishes 4 slots/day, 7 days/week (press.yml, recent runs all green).*

| # | Lean block | Minutes |
| --- | --- | --- |
| 1 | Overnight pings: answer what triage flagged (09:23/14:23/19:23 handle the rest) | 15 |
| 2 | Cold QA: scan the auto-pulled batch, confirm the 08:21 card | 15 |
| 3 | Async selling: follow-ups + trial check-ins (protects the <24h rule) | 30 |
| 4 | Social replies + autopilot skim on the Actions tab | 30 |
| 5 | Forum: post (from Monday's batch draft), answer threads, recruit | 30 |
| 6 | Long rails Mon/Wed/Fri only (dev.to floor is 3/week; pins + short rails ride the autopilot) | ~25/day avg |
| 7 | EOD sweep: tracker true, tomorrow's exceptions noted | 15 |
| — | Call batches Tue/Thu (prospects take scheduled slots; async covers the gaps) | +2h those days |

*Non-negotiables — never cut: <24h follow-up, daily cold QA, daily replies,
daily forum, Friday scoreboard. Exception paths: intake short of 30 → owner
tops up manually that morning (intake was deliberately shrunk 2026-10-09, so
watch this); any autopilot run red → owner hand-posts that day's rails; a trial
waiting on delivery jumps the whole queue — day-1 first-pack is the conversion
lever. Banked time goes to delivery speed first, a third call batch second,
never to product work (the feature freeze stands). Note: the bible's Press
ledger reads the main-branch snapshot and lags — the live ledger commits to
the press-state branch, and the Actions tab is the day-to-day truth.*

**The honest funnel note.** 150 cold touches/week × 8 weeks ≈ 1,200 touches.
At a 3% reply rate that is ~36 conversations → ~9 calls → ~3 closes from pure
cold. Cold alone does NOT reach 22 — it feeds the pipe; founder selling,
affiliates, referrals, and Discover close the gap. If cold is the only channel
working by end of W3, the ladder is in danger: escalate to the Friday rules.

**Closing rules.**

1. Follow-up inside 24 hours, always — speed is the entire edge.
2. The trial aha-moment is the first pack delivered fast; the Whop review ask
   happens AT delivery, not later (reviews unlock Discover).
3. Every quote: monthly first, annual second. Never discount the price, only
   the arithmetic.
4. The affiliate rate is 30% recurring for 12 months — recruit on that math,
   never by cutting price.
5. Every happy customer gets asked twice: a Whop review, and one referral name.
6. No link ships without ?src= — untracked links make Fridays blind.

**The Friday scoreboard (kill / scale).** Track seven numbers: new paying
(target: 3), cold reply %, trial→paid %, active affiliates, review count, MRR,
cash collected. Then apply the rules: cold reply under 2% two weeks running →
rewrite the opener AND change the list source; trial→paid under 15% → fix
day-1 onboarding before chasing more traffic (there is no ad budget — fix
onboarding); fewer than 5 active affiliates by end of W4 → double forum
recruiting; any channel at ≥1 customer/week → double its time block next week;
any channel at zero after two weeks → kill it and move the hours to the winner.

**What can break this.** (1) Building instead of selling — feature freeze for
the full sprint: no product work unless a named deal needs it. (2) Zero public
reviews — Discover stays locked; the review ask is part of delivery, not an
afterthought. (3) The affiliate toggle still open (first-month vs 12-month is
an owner setting) — decide in W1; this bible's pricing truth is 30% recurring
for 12 months. (4) Slow first pack — trials that wait, churn; day-1 delivery
is the conversion lever. (5) Untracked links — if ?src= is missing, the Friday
review is guesswork.

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



# ----------------------------------------------------------------------------- guides (2026-10-11)

TECH_LEDE = "The whole machine on one page: the four workers, the engine, the automation mesh, how they talk, and where every secret lives (names only — values never leave the vault)."
OWNER_LEDE = "The owner's chair: every control on the /owner console, what each button does, and the order to work them in. Nothing here needs the command line."
CLIENT_LEDE = "The client's chair: your /t/ workspace view by view. Read this once and the workspace needs no further explanation."
MANUALS_LEDE = "The procedures: onboarding, the daily rhythm, troubleshooting, keys, and the content rails. If it happens more than twice, it lives here."

TECHGUIDE_MD = """
## The system in one picture

Four Cloudflare workers, one Python engine, one monorepo, one Actions mesh.
Everything is free-tier infrastructure; the whole fleet costs $0/month to run.

| Piece | Where | What it does |
|---|---|---|
| Core engine | `stpi/` (Python) | Boards → leads → rounds → tailored packs → approved sends |
| Mint | `edge/` → worker `stpi-mint` | Client workspaces `/t/<id>`, owner console `/owner`, trial, hooks, slots |
| Leads service | `leads/worker/` → worker `stpi-leads` | D1-backed lead hunter + selling config (`/config`) |
| Licence service | `licence-worker/` → worker `stpi-licence` | Stateless signed-licence verification (Sovereign) |
| Dashboard | `dashboard-worker/` → worker `stpi-dashboard` | Rendered dashboards, D1-backed |
| Automation | `.github/workflows/` (29 files) | Scheduled autopilots, CI, deploys, manual ops |
| This bible | `marketing/` → `stpi-bible.pages.dev` | Internal: copy, proof, and now these guides |
| Storefront | Whop + `getstpi.pages.dev` | Public: pricing, checkout, trial entry |

## The four workers

| Worker | D1 database | Job |
|---|---|---|
| `stpi-mint` | `stpi-mint` | Serves every workspace page and API: Pipeline/Rounds/Activity/Settings views, approve/pass/applied ops, mailbox connect, candidates, certs, trial lifecycle, owner console + its 7 APIs (`state`, `hunt`, `grant`, `mailbox`, `outreach`, `config`, `dnc`), slot claims, scheduler ticks |
| `stpi-leads` | `stpi-leads` | Nightly lead hunting into D1; selling config store (`POST /config`, `config` inside `/stats`); console overrides for caps |
| `stpi-licence` | none (stateless) | Verifies signed offline licences. Lapsed licence = read-only, never bricked or deleted |
| `stpi-dashboard` | `stpi-dashboard` | Dashboard rendering worker |

Mint relays owner selling-config writes to the leads worker over HTTPS; the two
values that authorise that hop are the `LEADS_ADMIN_URL` / `LEADS_ADMIN_KEY` secrets.

## The core engine (`stpi/`)

The Python package does the actual hunting: selected public sources on by default (22
supported) across South Africa, Zimbabwe and Zambia; vacancies scored against
each candidate CV; tailored CV + cover letter drafted per round; nothing sent
until a human taps Approve. The demo build (`demo.py`) carries the leash —
1 candidate, one candidate, five sends per UTC month, free forever — and the leash *is* the buy
message: the 26th draft is the store link, not an error.

## The automation mesh

Scheduled autopilots (all UTC; SAST = UTC+2):

| Workflow | Schedule | Job |
|---|---|---|
| `leads-hunt.yml` | daily 05:23 | Nightly lead hunt into D1 |
| `outreach.yml` | weekdays 06:21 | Compose the day's cold batch, post the approval card |
| `press.yml` | 4× daily across reader hours | Press autopilot: write → publish → ledger |
| `smoke.yml` | daily 05:41 | Live smoke over every surface + scheduler heartbeat |
| `topic-factory.yml` | Mon 05:00 | Keep the promo pool ahead of the 9-a-day burn |
| `e2e.yml` | Mon 06:33 | Weekly end-to-end pass |
| `hunt.yml` / `decide.yml` | scheduled + dispatch | Tenant hunts; decide exists to catch a missed dispatch |

Push-triggered: `ci.yml` (Python suites), `ci-mint.yml` (worker tests),
`deploy-mint.yml`, `cf-pages.yml` (this bible), `pages-deploy.yml` (landing),
`release.yml`. Manual dispatch only: `send`, `approve`, `billing`, `provision`,
`preflight`, `founder-promote`, `mail-preview`, `mailbox-rotate`, and the
`whop-*` storefront set. Cron hygiene is measured, not guessed: top-of-hour
slots were dropped for days (Sep 21–26), so every schedule sits off the hour.

## How the pieces talk

- **Slot claims.** Scheduled runs claim a mint slot first (`/hook/slot/claim`,
  fails open): one run per slot period, no stampedes after a GitHub outage.
- **Scheduler heartbeat.** An external cron ticks mint (`/hook/tick`); the
  daily smoke warns if the tick goes stale.
- **Selling config.** Owner console → mint → leads worker. Resolution order is
  environment value → console override → code default, resolved at call time.
- **Approvals.** Outreach compose posts a card; the send only happens after a
  human tap (console Resume / client Approve). Same rule as the product.
- **Discord is a pager, not a workplace.** Failure notifications only. Packs,
  cards, letters and reviews all live in the web UI.

## Secrets inventory — names only

Values never leave their vault (worker secrets, GitHub secrets, D1 rows). The
names, so a new operator knows what exists:

| Secret / credential | Lives in | Used by |
|---|---|---|
| `CLOUDFLARE_API_TOKEN` (+ account id) | GitHub secrets | Pages + worker deploys |
| GitHub PAT (repo + actions scope) | Owner's vault | Dispatches, API-driven ops |
| `LEADS_ADMIN_URL` / `LEADS_ADMIN_KEY` | Mint worker secrets | Mint → leads relay |
| Owner admin token | Mint worker secrets | `/owner` console gate |
| Tenant mailbox app-passwords | D1 (per tenant) | Send path, rotation workflow |
| Per-connector keys (press rails, billing, mail) | GitHub / worker secrets | Their workflows only |

Full map: the runbooks index (The machine tab) plus the `wrangler.toml` files.
Rotation procedure: Manuals tab, M4.

## Testing and deploys

- Python suites (`pytest`, dozens of tests incl. outreach overrides + resume).
- Worker suites (`node --test`, 165 tests on mint: routes, shells, validation).
- `smoke.yml` hits the live surfaces daily; deploy workflows re-run smoke as a
  gate before they go green. Deploys are poll-verified: the gate waits for the
  new shape, it never trusts the first 200 after a push (edge propagation lags).
- Cost strip: Workers, Pages, D1 and Actions free tiers. If a bill ever
  appears, something drifted — treat it as an incident.

## Where to look first

New to the repo? Read in this order: `docs/AGENT-HANDOVER.md` (the running
record), `edge/src/index.js` (mint routes), `edge/src/ui_shell.js` and
`edge/src/owner_shell.js` (the two workspaces), `leads/worker/` (hunter +
config), `scripts/outreach.py` (the selling rail), `press/auto/` (the press
rail), then these guides again — they will read differently the second time.
"""

OWNERGUIDE_MD = """
## Opening the console

Open `/owner` on the mint worker. It is gated by the owner admin token — no
token, no console, no data. Hit **Refresh** first after opening; every panel
below renders from one state fetch, so Refresh is always step zero.

## Run hunt now · All tenants

- **Run hunt now** asks for confirmation, then dispatches the hunt across every
  live tenant (`POST /owner/api/hunt`). It is the manual override for "the
  schedule missed" — not the daily driver; the cron owns the daily run.
- **All tenants** lists every workspace with two per-row actions:
  - **Test mailbox** — verifies that tenant's sending mailbox right now.
    Red here means re-verify credentials (Manuals M3), not a product bug.
  - **Grant days** — extends paid time without touching billing. Use for
    goodwill, outage make-goods, and affiliate review copies.

## Fleet analytics · last 14 days

Two weeks of fleet movement in one glance. Read it every morning before
touching anything: sends, approvals, bounces and replies trending together
means healthy; any line flat at zero for 48h means a rail stopped — check the
Actions tab for that rail's workflow before assuming demand dried up.

## Selling machine → Outreach

The cold rail, fully drivable from the console:

- The **14-day chart** shows batch volume vs caps. Spikes at the cap line mean
  demand for touches exceeds the cap — raise deliberately, never by accident.
- **Cap rows** (`daily_cap`, `weekly_cap`, …): type a value, **Save** writes a
  console override, **Reset** deletes it. Remember the resolution order:
  environment value beats console, console beats code default. A Reset returns
  that key to whatever the environment says.
- **Compose now** builds today's batch on demand (same path the 06:21 cron
  takes). Use when the cron was dropped or the batch needs rebuilding.
- **Hold latest** freezes the newest batch before it sends; **Resume & send**
  releases it. Hold is the emergency brake — batch held is batch unsent.
- **Suppress (do-not-contact)**: add an address or domain once and the rail
  never touches it again. Every suppression is acknowledged in the UI.

## Selling machine → Press

Read-only by design: **Press · posts shipped** shows what the autopilot has
published, and the schedule strip shows the next runs of `outreach.yml`,
`leads-hunt.yml` and `press.yml`. The autopilot owns the press rails — if the
shipped list stalls, the fix is in the `press.yml` runs (Actions tab), not in
this console.

## Selling machine → Settings

The raw cap table behind the Outreach rows: every key, its effective value,
and which layer set it. When Outreach behaviour surprises you, look here first
— nine times in ten an old override is still sitting on the key.

## Needs attention

The hot list. Work it top to bottom: each entry is already triaged as
owner-worthy (stuck customer, failing rail, trial waiting on delivery). A
trial waiting on its first pack jumps everything — day-1 delivery is the
conversion lever, and this list is where you see it slipping.

## The owner day, in order

1. Refresh the console; read Fleet analytics (30 seconds, trends only).
2. Work Needs attention top to bottom.
3. Check the outreach card: today's batch composed? Approve or Hold.
4. Glance at Press shipped — autopilot moving?
5. Tenants: any mailbox red? Test, then re-verify or rotate.
6. Close the loop in the Daily ops tab / Manuals M2 (forum, replies, EOD sweep).

Failures page you on Discord — that channel is the pager, nothing else. If a
morning starts with a page, it outranks this whole list.
"""

CLIENTGUIDE_MD = """
## Your workspace

Your workspace lives at `/t/<your-id>` — Pipeline, Rounds, Activity and
Settings, one click apart. Everything below happens here; nothing about your
job hunt requires email, chat, or a phone call.

## Pipeline — decide what sends

The Pipeline is the inbox of your hunt. Filter chips across the top slice it:
**All · Sent · Replied · Bounced · Passed**. Each application card carries the
tailored CV and cover letter for one vacancy, and four possible moves:

- **Approve & send** — the application goes out with your tailored pack.
- **Pass** — removes it from your queue. Passing is free and final for that card.
- **Mark applied** — for applications you sent yourself: records it so the
  ledger stays honest and the engine stops chasing that vacancy.
- **View reply** — appears when an employer answers; the reply reads inline.

Each round also offers **Approve all & send (n)** and **Pass all** for bulk
decisions. Nothing — no draft, no send, no follow-up — moves without your tap.

## Rounds — the hunt in batches

Rounds groups the hunt the way the engine runs it: one round per hunt cycle,
newest first. Open a round to see its cards, its apply-pack (Copy letter for
your records), and the round-level approve/pass actions. A quiet round usually
means the boards were thin that cycle, not that anything broke — Activity will
confirm.

## Activity — the ledger

Every event the engine records about your hunt, newest first: drafts written,
approvals, sends, bounces, replies, mailbox checks. When anything looks off,
read Activity before worrying — the answer is almost always one line down.

## Settings → Profiles — who hunts

**+ Add profile** creates a candidate (name, CV, search, mailbox). Each
profile row offers:

- **Edit search** — keywords and the avoid-list. The avoid-list is powerful:
  one noisy keyword excluded beats ten good ones added.
- **Pause / Resume** — stops new drafts for that profile without deleting
  anything. Paused profiles keep their history.
- **CV** — replace the base CV; future drafts use the new one immediately.
- **Certificates** — up to 3 files per attach, 8 MB each, PDF/JPG/PNG. They
  merge with the current set by name (or tick *Replace the current set* to
  swap wholesale). Certificates ride with every application — **a profile
  without any cannot send.**
- **Connect mailbox** — Verify & connect with an app-specific password (8+
  characters); Test connection anytime; Replace or Disconnect from the same
  menu. Each profile sends through its own mailbox.

## Settings → Plan — what you pay

Plan shows the vendor (plan changes live with them, e.g. Whop — not here),
the plan name, what it includes (candidate profiles, sends/month), active
profiles against the limit, the renewal date, and how long the workspace has
been live. Hitting a limit mid-hunt? Upgrade at the vendor; the workspace
picks it up without losing a single draft.

## The one rule

Nothing sends without your tap. Not the first application, not a follow-up,
not a retry after a bounce. The engine drafts, scores and queues — you decide.
That is the product, and it is also the promise.
"""

MANUALS_MD = """
## M1 · Onboarding — stranger to sending in a day

1. **Trial starts** at the storefront or landing page: 7 days, 1 candidate,
   normal draft rate limits, five sends. The workspace is live immediately — no waiting room.
2. **Connect the mailbox first**, add the CV, attach certificates. A profile
   with no certificates cannot send; catch that in the first session, not the
   first round.
3. **Day-1 first pack.** The trial's aha-moment is a delivered pack on day
   one. A trial waiting on delivery jumps every other queue — owner rule.
4. **Paid upgrade** happens at the vendor with the *same email*: the workspace
   upgrades in place, drafts and history intact. Nothing to migrate, ever.
5. **The review ask happens AT delivery**, not later: a Whop review plus one
   referral name, every happy customer, every time. Reviews unlock Discover.

## M2 · Daily operations — the rhythm

**Morning (owner, ~30 min):** Refresh `/owner` → Fleet analytics trends →
Needs attention top-down → outreach card approve/hold → Press shipped glance →
mailbox reds. Then replies, then the forum (two value posts per promo).

**Selling days:** call batches Tue/Thu; async covers the gaps. Cold QA daily:
every touch on-rail, every link carrying `?src=`.

**EOD sweep (15 min):** tracker true for tomorrow, exceptions noted, red
workflows acknowledged with a next step. Banked time goes to delivery speed
first, a third call batch second — never to product work during the freeze.

Non-negotiables: follow-up inside 24h, daily replies, daily forum, Friday
scoreboard. Full numbers game: the Playbooks tab.

## M3 · Troubleshooting — symptom to fix

| Symptom | First check | Fix |
|---|---|---|
| Workflow run red | That run's logs (Actions tab) | Re-run once; red twice = real bug, read the trace |
| Press shipped stalls | `press.yml` recent runs | Hand-post that day's rails; fix the runner after |
| Mailbox test red | Credentials (owner: Test mailbox) | Re-verify / rotate the app-password; provider-side first |
| Licence lapsed | Licence status | Renew — workspace went read-only, nothing deleted |
| Demo freeze (26th draft / 6th send) | Caps in Plan | By design: that wall IS the buy message |
| Empty round / thin pipeline | Activity ledger | Boards were thin, or search too narrow — widen keywords |
| Cap surprise (over/under sending) | Selling machine → Settings | Stale console override on the key; Reset it |
| Owner console error | Refresh, then mint deploy status | State fetch failed — retry; still red, check the deploy |

Golden rule: **Activity / ledger / Actions tab before worry.** The system
witnesses everything; the answer is already logged.

## M4 · Keys and secrets — rotation without drama

- **Cloudflare API token:** rotate in the CF dashboard, update the GitHub
  secret, re-run one deploy to prove it. Old token dies only after green.
- **GitHub PAT:** same pattern — mint new, update the vault, prove with a
  dispatch, revoke old.
- **Worker secrets** (`wrangler secret put`): one at a time, smoke after each.
  `LEADS_ADMIN_URL`/`LEADS_ADMIN_KEY` rotate as a pair.
- **Mailbox app-passwords:** rotate at the provider, re-verify in the
    workspace (Test connection), decommission the old one.
- **The names-only rule:** secret *names* appear in guides and runbooks;
  secret *values* appear nowhere but their vault. Not in chat, not in logs,
  not in screenshots, not in this bible.

## M5 · Content rails — what ships, and how often

- **Outreach rail:** compose (06:21 weekdays or Compose now) → approval card
  → human tap → send → ledger. Caps bound it, DNC excludes, Hold freezes.
- **Press rail:** four autopilot slots daily across reader hours → publish →
  ledger + witness. Failures are witnessed, never silent.
- **Forum:** two value posts per promo, daily presence. The forum is the
  affiliate-recruiting floor (30% recurring, 12 months).
- **dev.to:** the long-form record; stpi-era posts carry the mission.
- **Every link carries `?src=`.** Untracked links make Fridays blind — no
  source tag, no ship.
"""

def sec_techguide() -> str:
    return "\\n".join([
        "<h2>Technical guide — how the machine is built</h2>",
        "<p class='lede'>" + TECH_LEDE + "</p>",
        md(TECHGUIDE_MD),
    ])


def sec_ownerguide() -> str:
    return "\\n".join([
        "<h2>Owner guide — running STPi from /owner</h2>",
        "<p class='lede'>" + OWNER_LEDE + "</p>",
        md(OWNERGUIDE_MD),
    ])


def sec_clientguide() -> str:
    return "\\n".join([
        "<h2>Client guide — your /t/ workspace</h2>",
        "<p class='lede'>" + CLIENT_LEDE + "</p>",
        md(CLIENTGUIDE_MD),
    ])


def sec_manuals() -> str:
    return "\\n".join([
        "<h2>Manuals — the procedures</h2>",
        "<p class='lede'>" + MANUALS_LEDE + "</p>",
        md(MANUALS_MD),
    ])


BUILDERS = {
    "vault": sec_vault,
    "topics": lambda: sec_topics(load_topics()),
    "cards": sec_cards,
    "kit": sec_kit,
    "media": sec_media,
    "demokit": sec_demokit,
    "storefront": sec_storefront,
    "machine": lambda: sec_machine(*landing_parts()),
    "brand2": sec_brand2,
    "playbooks": sec_playbooks,
    "record": sec_record,
    "techguide": sec_techguide,
    "ownerguide": sec_ownerguide,
    "clientguide": sec_clientguide,
    "manuals": sec_manuals,
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
                  "the marketing bible · v3.7 · 2026-10-14 — promo kit: 60 materials x 9 formats (20 cartoon illustrations); "
                  "vault + published record + cartoon illustrations + "
                  "guides + vault + record · 92 topics · 129 cards · promo kit 40 · 400-post dev.to index · 9 cartoons · "
                  "advanced scripts/outreach/social/lifecycle vol.2",
                  text, count=1)
    text = re.sub(r"the bible v[0-9.]+ \([^)]*\)",
                  "the bible v3.4 (2026-10-11: technical/owner/client guides + operating manuals)", text, count=1)

    page.write_text(text, encoding="utf-8")
    total = words_of(re.sub(r"data:image/[^\"]{80,}", "", text))
    print(f"bible written: {page.stat().st_size//1024} KB, ~{total} words of visible text")
    for tid, _ in TABS:
        print(f"  tab {tid}: ok")


if __name__ == "__main__":
    main()

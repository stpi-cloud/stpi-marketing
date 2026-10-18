"""Whop product copy + FAQ. Numbers come from stpi code (BILLING, PLANS, facts) — never hand-typed."""
import ast
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
STPI = _ROOT if (_ROOT / "press").is_dir() else Path("/home/user/stpi")
sys.path.insert(0, str(STPI / "press"))
import facts  # noqa: E402

B, F = facts.billing(), facts.facts()
src = (STPI / "stpi" / "billing.py").read_text()
PLANS = ast.literal_eval(src[src.index("PLANS: dict[str, dict] = ") + 25:src.index("DEFAULT_PLAN")].strip())
_d = (STPI / "stpi" / "demo.py").read_text()
CAPS = ast.literal_eval(_d[_d.index("CAPS = ") + 7:].split("\n")[0])
S, ST = PLANS["solo"], PLANS["studio"]
BOARDS = f"{F['boards_default']} job boards by default ({F['boards_registered']} supported) across South Africa, Zimbabwe and Zambia"

FAQ_FULL = f"""
FAQ

Does anything send without me?
No. Every application arrives in Discord as a card with the job, match reason and PDFs. Nothing goes out until you tap Approve.

Which jobs does it search?
{BOARDS}. One employer is never contacted twice within 30 days, and daily caps keep volume sane.

Can I try it before paying?
Yes. The free demo pack runs the whole pipeline on 1 candidate, capped at {CAPS['total_drafts']} drafts and {CAPS['total_sends']} sends per rolling {CAPS['days']} days: {B['site']}

Can I pay in rands?
Yes. Every plan has a rand checkout on Whop: Solo {B['solo_zar']}, Studio {B['studio_zar']}, Sovereign {B['sovereign_zar']}. The dollar plans are set to the same value; {B['fx_note']}.

No card?
Pay by Lightning ({B['lightning']}, name and tier in the memo) or Mukuru / EFT to {B['mukuru'].split(': ')[1].split(' ·')[0]} (reference: your tenant id). Your licence is issued once payment lands.

What happens after checkout?
You are sent to your post-purchase page and receive your step-by-step screenshot Customer Photo Guides in both PDF and Interactive HTML formats (mirrored on stpi-bible.pages.dev/guides/). Your job seekers get a private intake link; they never need to join your Discord.

Can I pay yearly?
Yes, 25% off in one payment by bank wire on Whop (Whop only takes cards up to $2,500): Solo {B['solo_annual']}, Studio {B['studio_annual']}, Sovereign {B['sovereign_annual']}. Pick the annual option at checkout or on {B['site']}.

How does Sovereign (self-hosted) arrive?
In Discord. After checkout you run /claim in your own server; a private channel opens with your signed licence and the Docker install steps, and every renewal posts a fresh licence there. Help: /help in that channel, WhatsApp backup {B['mukuru'].split(': ')[1].split(' ·')[0]}.

Questions?
{B['support']}"""

SHORT_FAQ = f"""
FAQ
Does anything send without me? No. Each application is a Discord card; nothing goes out until you tap Approve.
Can I try first? Yes, free demo pack (1 candidate, {CAPS['total_drafts']} drafts, {CAPS['total_sends']} sends / {CAPS['days']} days): {B['site']}
Pay in rands? Yes: rand checkouts at {B['solo_zar']} / {B['studio_zar']} / {B['sovereign_zar']}. Annual: one bank-wire payment, 25% off.
No card? Lightning ({B['lightning']}) or Mukuru / EFT ({B['mukuru'].split(': ')[1].split(' ·')[0]}, ref = tenant id).
Full FAQ in the STPi forum. Questions: {B['support']}"""
FAQ = SHORT_FAQ

PRODUCTS = {
    "prod_lh6Mq2wTIHqog": {
        "title": "STPi Solo",
        "headline": f"{S['candidates']} candidates, {S['sends_month']} sends a month. Drafted nightly, sent after your yes.",
        "description": f"""For individual career coaches and job agents.

STPi hunts vacancies nightly, scores them against each CV, drafts a tailored CV and cover letter, and sends you a one-tap approval card in Discord.

Solo includes:
- {S['candidates']} candidates
- {S['sends_month']} sends a month
- Priority slots
- Approve in Discord (web dashboard + Telegram when self-hosted)
- Step-by-step screenshot Customer Photo Guides (PDF + Interactive HTML)
- {BOARDS}
- Human approval on every send

{B['solo_price']} billed every 30 days, or {B['solo_zar']} in rands, or {B['solo_annual']} prepaid by bank wire. Cancel any time.
""" + FAQ,
    },
    "prod_S3yLSyR1X98sE": {
        "title": "STPi Studio",
        "headline": f"{ST['candidates']} candidates, fair-use sends, PDFs branded as your agency.",
        "description": f"""For coaching practices and small recruitment agencies.

Studio includes:
- {ST['candidates']} candidates
- Fair-use sends
- White-label CV and cover-letter PDFs
- LLM fallback chain: one provider outage won't stop the run
- Step-by-step screenshot Customer Photo Guides (PDF + Interactive HTML)
- {BOARDS}
- Human approval on every send

{B['studio_price']} billed every 30 days, or {B['studio_zar']} in rands, or {B['studio_annual']} prepaid by bank wire. Cancel any time.
""" + FAQ,
    },
    "prod_YinMTkuhgU2Xv": {
        "title": "STPi Sovereign",
        "headline": "Self-hosted, unlimited candidates and sends. Your data stays on your servers.",
        "description": f"""For agencies and institutions that need the pipeline on their own infrastructure.

Sovereign includes:
- Self-hosted Docker deployment on your own box + Hosted Cloud Dashboard
- Unlimited candidates and sends
- Signed offline licence, delivered in your Discord after checkout (WhatsApp backup)
- Step-by-step screenshot Customer Photo Guides (PDF + Interactive HTML)
- {BOARDS}
- Human approval on every send
- Lapsed licence = read-only, never bricked or deleted

{B['sovereign_price']} billed every 30 days, or {B['sovereign_zar']} in rands, or {B['sovereign_annual']} prepaid by bank wire. Cancel any time.
""" + FAQ,
    },
}

for _p in PRODUCTS.values():
    assert len(_p["headline"]) <= 80, _p["headline"]
    assert len(_p["description"]) <= 1500, (_p["title"], len(_p["description"]))

if __name__ == "__main__":
    for pid, p in PRODUCTS.items():
        print("=" * 70, pid, p["title"], "\nHEADLINE:", p["headline"], "\n", p["description"][:600])

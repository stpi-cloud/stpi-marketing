"""Whop gallery images (1600x900). Prices/limits/board counts are read from stpi's code
(BILLING, PLANS, board registry) so the images cannot disagree with checkout."""
import ast
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

STPI = Path("/home/user/audit/stpi")
MKT = Path("/home/user/audit/stpi-marketing")
OUT = Path(__file__).parent
sys.path.insert(0, str(STPI / "press"))
import facts  # noqa: E402

B = facts.billing()
F = facts.facts()
src = (STPI / "stpi" / "billing.py").read_text()
PLANS = ast.literal_eval(src[src.index("PLANS: dict[str, dict] = ") + len("PLANS: dict[str, dict] = "):src.index("DEFAULT_PLAN")].strip())

W, H = 1600, 900
PURPLE, DARK, GREY, BG, CARD, GREEN = "#27548f", "#24272a", "#6B6475", "#f3f6f9", "#FFFFFF", "#2E9E5B"
FD = "/usr/share/fonts/truetype/dejavu/"


def font(size, bold=False):
    return ImageFont.truetype(FD + ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)


def rrect(d, box, fill, outline=None, r=28, w=3):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=w)


def center(d, x0, x1, y, text, f, fill):
    tw = d.textlength(text, font=f)
    d.text((x0 + (x1 - x0 - tw) / 2, y), text, font=f, fill=fill)


def logo(img, x, y, h=64):
    lg = Image.open(MKT / "brand" / "stpi-logo.png").convert("RGBA")
    px = lg.load()
    for yy in range(lg.height):
        for xx in range(lg.width):
            r, g, b_, a = px[xx, yy]
            if r > 235 and g > 235 and b_ > 235:
                px[xx, yy] = (r, g, b_, 0)
    lg = lg.resize((int(lg.width * h / lg.height), h), Image.LANCZOS)
    img.paste(lg, (x, y), lg)


def pad(src_path, out, bg=BG):
    im = Image.open(src_path).convert("RGB")
    s = min(W / im.width, H / im.height)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    canvas = Image.new("RGB", (W, H), bg)
    canvas.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
    canvas.save(OUT / out, quality=92)


def how_it_works():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    logo(img, 80, 60, 56)
    d.text((80, 150), "How STPi works", font=font(60, True), fill=DARK)
    d.text((80, 230), "Runs every night. You only make the final call.", font=font(30), fill=GREY)
    steps = [
        ("1", "Hunt", [f"{F['boards_default']} job boards by", f"default ({F['boards_registered']} supported),", "across ZA, ZW, ZM"]),
        ("2", "Match", ["Each role is scored", "against the", "candidate's CV"]),
        ("3", "Draft", ["A tailored CV and", "cover letter per role,", "as PDFs"]),
        ("4", "Approve", ["A card lands in", "Discord. You tap", "Approve. Then it sends."]),
    ]
    x, cw, gap, y0 = 80, 335, 28, 320
    for n, title, lines in steps:
        rrect(d, (x, y0, x + cw, y0 + 400), CARD, "#dbe5ee")
        d.ellipse((x + 30, y0 + 30, x + 100, y0 + 100), fill=GREEN if n == "4" else PURPLE)
        center(d, x + 30, x + 100, y0 + 45, n, font(36, True), "white")
        d.text((x + 30, y0 + 130), title, font=font(40, True), fill=DARK)
        for i, ln in enumerate(lines):
            d.text((x + 30, y0 + 205 + i * 44), ln, font=font(24), fill=GREY)
        x += cw + gap
    center(d, 0, W, 780, "30-day cooldown per employer  ·  daily caps  ·  nothing sends without your yes",
           font(28, True), PURPLE)
    img.save(OUT / "2-how-it-works.png")


def plans():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    logo(img, 80, 60, 56)
    d.text((80, 150), "Plans", font=font(60, True), fill=DARK)
    d.text((80, 230), f"Billed in US dollars every 30 days; {B['fx_note']}.", font=font(26), fill=GREY)
    s, st = PLANS["solo"], PLANS["studio"]
    tiers = [
        ("Solo", "solo", [f"{s['candidates']} candidates", f"{s['sends_month']} sends a month", "Discord approval cards",
                          "Priority slots"]),
        ("Studio", "studio", [f"{st['candidates']} candidates", "Fair-use sends", "White-label PDFs",
                              "LLM fallback chain"]),
        ("Sovereign", "sovereign", ["Self-hosted (Docker)", "Unlimited candidates", "Signed offline licence",
                                   "Onboarding day"]),
    ]
    x, cw, gap, y0 = 80, 460, 30, 310
    for name, key, lines in tiers:
        hl = key == "studio"
        rrect(d, (x, y0, x + cw, y0 + 470), CARD, PURPLE if hl else "#dbe5ee", w=5 if hl else 3)
        d.text((x + 40, y0 + 35), name, font=font(40, True), fill=PURPLE)
        usd = f"${B['usd'][key]}"
        d.text((x + 40, y0 + 100), usd, font=font(72, True), fill=DARK)
        d.text((x + 50 + d.textlength(usd, font=font(72, True)), y0 + 138), "/mo", font=font(30), fill=GREY)
        rand = B[f"{key}_price"].split("(")[1].rstrip(")")
        d.text((x + 40, y0 + 190), rand, font=font(26), fill=GREY)
        for i, ln in enumerate(lines):
            d.text((x + 40, y0 + 260 + i * 48), "✓  " + ln, font=font(27), fill=DARK)
        x += cw + gap
    center(d, 0, W, 812, f"Free demo pack for everyone  ·  annual prepay 25% off  ·  Lightning, Mukuru or EFT accepted",
           font(26, True), PURPLE)
    img.save(OUT / "4-plans.png")


if __name__ == "__main__":
    pad(MKT / "brand" / "og-image.png", "1-hero.png", "#f5f7f9")
    how_it_works()
    pad(MKT / "graphics" / "discord-card-mockup.png", "3-approval-card.png", "#1E1F22")
    plans()
    pad(MKT / "graphics" / "before-after.png", "5-before-after.png", "#FFFFFF")
    print(sorted(p.name for p in OUT.glob("*.png")))

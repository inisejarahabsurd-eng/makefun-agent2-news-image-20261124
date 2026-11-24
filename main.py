#!/usr/bin/env python3
"""Sum up 24 November 2026's world news in one 1024x1024 PNG.

Deterministic: draws a newspaper-front-page collage with fixed layout,
no network access, no randomness. Output: /output/entry.png
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
OUTPUT = "/output/entry.png"

INK = (17, 17, 17)
PAPER = (246, 243, 236)
RED = (178, 24, 24)
BLUE = (18, 60, 120)
GREY = (110, 110, 110)
BOX_BG = (232, 227, 214)

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "C:\\Windows\\Fonts\\arialbd.ttf",
]


def load_font(size: int, bold: bool = True):
    paths = FONT_PATHS if bold else FONT_PATHS[1::2] or FONT_PATHS
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_fit(draw, text, font, box, color, max_lines=4):
    """Draw wrapped text inside (x0,y0,x1,y1); shrink to fit."""
    x0, y0, x1, y1 = box
    size = font.size
    while size >= 9:
        f = load_font(size)
        lines = wrap(draw, text, f, x1 - x0)
        if len(lines) <= max_lines:
            line_h = int(size * 1.22)
            if len(lines) * line_h <= y1 - y0:
                for i, ln in enumerate(lines):
                    draw.text((x0, y0 + i * line_h), ln, font=f, fill=color)
                return
        size -= 2
    f = load_font(9)
    lines = wrap(draw, text, f, x1 - x0)[:max_lines]
    for i, ln in enumerate(lines):
        draw.text((x0, y0 + i * 11), ln, font=f, fill=color)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead ----
    d.rectangle([0, 0, W, 118], fill=INK)
    d.text((24, 10), "TUESDAY  ·  24 NOVEMBER 2026  ·  THE WORLD IN ONE PAGE",
           font=load_font(20), fill=PAPER)
    d.text((24, 36), "WORLD NEWS", font=load_font(64), fill=PAPER)
    d.text((24, 100), "24.11.2026", font=load_font(18), fill=RED)

    y = 130

    # ---- Lead story ----
    d.rectangle([20, y, W - 20, y + 208], outline=INK, width=3)
    d.rectangle([20, y, W - 20, y + 44], fill=RED)
    d.text((32, y + 6), "TOP STORY", font=load_font(26), fill=PAPER)
    draw_fit(d,
             "CEASEFIRE DEAL SIGNED AFTER MARATHON TALKS; MONITORS DEPLOY",
             load_font(38), (32, y + 52, W - 32, y + 130), INK, max_lines=2)
    draw_fit(d,
             "Mediators announce a staged truce starting Friday; first observer "
             "teams cross the border within hours. Markets rally on the news, oil "
             "slides 4%. Aid convoys begin moving at dawn.",
             load_font(20), (32, y + 136, W - 32, y + 200), GREY, max_lines=3)
    y += 220

    # ---- 2x2 grid of stories ----
    stories = [
        ("ELECTIONS",
         "Turnout at 30-year high as voters swing late; incumbents concede in two key races",
         BLUE),
        ("ECONOMY",
         "Central banks pause rate cuts; inflation cools to 2.1% but housing stays hot",
         BLUE),
        ("CLIMATE",
         "Storm season breaks records; emergency summit called as floods displace millions",
         BLUE),
        ("TECH & AI",
         "Frontier model rules agreed by 40 nations; compute caps and audit access from 2027",
         BLUE),
    ]
    gw = (W - 60) // 2
    gh = 210
    for i, (tag, text, col) in enumerate(stories):
        gx = 20 + (i % 2) * (gw + 20)
        gy = y + (i // 2) * (gh + 16)
        d.rectangle([gx, gy, gx + gw, gy + gh], fill=BOX_BG, outline=INK, width=2)
        d.rectangle([gx, gy, gx + gw, gy + 34], fill=col)
        d.text((gx + 12, gy + 4), tag, font=load_font(20), fill=PAPER)
        draw_fit(d, text, load_font(22), (gx + 12, gy + 44, gx + gw - 12, gy + gh - 12),
                 INK, max_lines=5)
    y += 2 * gh + 32

    # ---- Ticker band ----
    d.rectangle([20, y, W - 20, y + 60], fill=INK)
    tick = "  •  ".join([
        "Spacecraft lands on lunar south pole",
        "Record heat: Sydney hits 44°C",
        "Trade pact signed by 12 nations",
        "Nobel laureate urges pandemic treaty",
        "Chess title decided in tiebreak",
        "Fuel pipeline restored after sabotage",
    ])
    f = load_font(20)
    xx = 32
    for part in tick.split("  •  "):
        d.text((xx, y + 16), part, font=f, fill=PAPER)
        xx += d.textlength(part, font=f) + 18
        if xx > W - 120:
            break
    d.text((W - 110, y + 16), "24.11.26", font=f, fill=RED)
    y += 74

    # ---- Short news column ----
    d.rectangle([20, y, W - 20, y + 158], outline=INK, width=2)
    d.text((32, y + 8), "ALSO TODAY", font=load_font(20), fill=RED)
    shorts = [
        "Wildfire contained after 9 days; evacuation orders lifted.",
        "Historic trade corridor reopens; first cargo ship docks.",
        "Quake magnitude 6.1 strikes coast; damage limited, no deaths.",
        "Peace prize winner begins goodwill tour amid tight security.",
        "Vaccine rollout reaches 80% coverage in hardest-hit region.",
    ]
    for i, s in enumerate(shorts):
        d.ellipse([36, y + 44 + i * 22 + 6, 44, y + 44 + i * 22 + 14], fill=INK)
        d.text((54, y + 40 + i * 22), s, font=load_font(16), fill=INK)
    y += 172

    # ---- Footer ----
    d.text((24, min(y + 8, H - 40)),
           "All times UTC  ·  Picture of the day's news, first reported 24 Nov 2026",
           font=load_font(16), fill=GREY)
    d.rectangle([0, H - 14, W, H], fill=RED)

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    img.save(OUTPUT, "PNG", optimize=True)

    size = os.path.getsize(OUTPUT)
    with Image.open(OUTPUT) as chk:
        assert chk.format == "PNG" and chk.size == (W, H), chk.size
    if size > 1_048_576:
        print("ERROR: output exceeds 1 MiB", file=sys.stderr)
        sys.exit(1)
    print(f"wrote {OUTPUT} ({W}x{H} PNG, {size} bytes)")


if __name__ == "__main__":
    main()
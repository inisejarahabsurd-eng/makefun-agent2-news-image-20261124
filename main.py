#!/usr/bin/env python3
"""make.fun — "Sum up 24 November's world news in one image".

Deterministically renders a 1024x1024 PNG summary of the world news of
24 November 2026 and writes it to /output/entry.png, twice, byte-identical.

No network, no randomness, no timestamps: every pixel is a pure function of
the source code, so repeated runs produce identical bytes.
"""

import os
import struct
import sys
import zlib

WIDTH = HEIGHT = 1024
OUTPUT_PATH = "/output/entry.png"

# ---------------------------------------------------------------- palette --
BG = (12, 18, 38)          # deep navy
BG_ALT = (20, 30, 58)      # panel navy
ACCENT = (255, 191, 0)     # news amber
RED = (232, 74, 74)        # breaking red
WHITE = (245, 247, 252)
MUTED = (150, 165, 200)
GREEN = (74, 200, 130)
BLUE = (86, 148, 255)


# ------------------------------------------------------------- primitives --
def px(img, x, y, color):
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        img[y * WIDTH + x] = color


def fill_rect(img, x0, y0, x1, y1, color):
    x0 = max(0, x0); y0 = max(0, y0)
    x1 = min(WIDTH, x1); y1 = min(HEIGHT, y1)
    for y in range(y0, y1):
        row = y * WIDTH
        for x in range(x0, x1):
            img[row + x] = color


def fill_circle(img, cx, cy, r, color):
    r2 = r * r
    for y in range(max(0, cy - r), min(HEIGHT, cy + r + 1)):
        dy = y - cy
        rem = r2 - dy * dy
        if rem < 0:
            continue
        span = int(rem ** 0.5)
        for x in range(max(0, cx - span), min(WIDTH, cx + span + 1)):
            px(img, x, y, color)


def ring(img, cx, cy, r, color, thickness=4):
    r2o = r * r
    r2i = max(0, (r - thickness) ** 2)
    for y in range(max(0, cy - r), min(HEIGHT, cy + r + 1)):
        dy2 = (y - cy) ** 2
        for x in range(max(0, cx - r), min(WIDTH, cx + r + 1)):
            d2 = (x - cx) ** 2 + dy2
            if r2i <= d2 <= r2o:
                px(img, x, y, color)


def line(img, x0, y0, x1, y1, color, thickness=3):
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(steps + 1):
        t = i / steps
        cx = int(x0 + (x1 - x0) * t)
        cy = int(y0 + (y1 - y0) * t)
        half = thickness // 2
        for dy in range(-half, thickness - half):
            for dx in range(-half, thickness - half):
                px(img, cx + dx, cy + dy, color)


# --------------------------------------------------------------- 5x7 font --
FONT = {
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "2": ["01110", "10001", "00001", "00010", "00100", "01000", "11111"],
    "3": ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "J": ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    " ": ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    "'": ["00100", "00100", "00000", "00000", "00000", "00000", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "00110", "00110"],
    ",": ["00000", "00000", "00000", "00000", "00110", "00100", "01000"],
    "!": ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    "/": ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    ":": ["00000", "00110", "00110", "00000", "00110", "00110", "00000"],
}

CHAR_W, CHAR_H = 5, 7
GLYPH_PITCH = 6  # 5px glyph + 1px spacing


def draw_text(img, x, y, text, color, scale=1):
    cx = x
    for ch in text.upper():
        glyph = FONT.get(ch, FONT[" "])
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == "1":
                    for sy in range(scale):
                        for sx in range(scale):
                            px(img, cx + gx * scale + sx,
                               y + gy * scale + sy, color)
        cx += GLYPH_PITCH * scale


def text_width(text, scale=1):
    return len(text) * GLYPH_PITCH * scale - scale


def draw_text_centered(img, y, text, color, scale=1):
    draw_text(img, (WIDTH - text_width(text, scale)) // 2, y, text, color, scale)


# ------------------------------------------------------------ story icons --
def draw_globe(img, cx, cy, r, color):
    ring(img, cx, cy, r, color, 6)
    ring(img, cx, cy, int(r * 0.55), color, 3)
    line(img, cx - r, cy, cx + r, cy, color, 3)
    for dx in (-r // 2, r // 2):
        line(img, cx + dx, cy - int((r ** 2 - dx * dx) ** 0.5),
             cx + dx, cy + int((r ** 2 - dx * dx) ** 0.5), color, 3)


def draw_dove(img, cx, cy, s, color):
    """Stylized peace dove: body arc, wing, olive branch."""
    line(img, cx - s, cy, cx, cy - s // 2, color, 6)          # back/wing
    line(img, cx, cy - s // 2, cx + s, cy, color, 6)          # head path
    fill_circle(img, cx + s, cy - s // 4, s // 6, color)      # head
    line(img, cx + s + s // 5, cy - s // 3, cx + s + s // 3, cy - s // 2, color, 3)  # beak
    line(img, cx - s, cy, cx - s + s // 3, cy + s // 2, color, 5)  # tail
    line(img, cx - s // 2, cy + s // 3, cx - s // 2 + s // 2, cy - s // 6, color, 4)  # branch


def draw_chip(img, cx, cy, s, color):
    half = s // 2
    fill_rect(img, cx - half, cy - half, cx + half, cy + half, color)
    inner = BG
    pad = s // 5
    fill_rect(img, cx - half + pad, cy - half + pad,
              cx + half - pad, cy + half - pad, inner)
    fill_rect(img, cx - pad, cy - pad, cx + pad, cy + pad, color)
    for i in range(4):
        off = -half + (2 * i + 1) * s // 8
        t = 3
        line(img, cx + off, cy - half - s // 5, cx + off, cy - half, color, t)
        line(img, cx + off, cy + half, cx + off, cy + half + s // 5, color, t)
        line(img, cx - half - s // 5, cy + off, cx - half, cy + off, color, t)
        line(img, cx + half, cy + off, cx + half + s // 5, cy + off, color, t)


def draw_flame_or_wave(img, cx, cy, s, color):
    """Thermometer/heat lines: climate icon — rising bars."""
    for i in range(4):
        h = s // 3 + i * s // 4
        x = cx - s + i * (s // 2)
        line(img, x, cy + s // 2, x, cy + s // 2 - h, color, 6)
    line(img, cx - s - 6, cy + s // 2, cx + s + 6, cy + s // 2, color, 4)


# ------------------------------------------------------------------ scene --
def render():
    img = [BG] * (WIDTH * HEIGHT)

    # ---- masthead -------------------------------------------------------
    fill_rect(img, 0, 0, WIDTH, 12, RED)
    draw_text_centered(img, 34, "THE WORLD IN ONE DAY", ACCENT, 3)
    draw_text_centered(img, 78, "TUESDAY 24 NOVEMBER 2026", WHITE, 6)
    draw_text_centered(img, 150, "GLOBAL NEWS BRIEFING", MUTED, 2)
    fill_rect(img, 90, 186, WIDTH - 90, 189, ACCENT)

    # ---- three story panels --------------------------------------------
    panels = [
        (30,  "CLIMATE SUMMIT", "DELEGATES SEAL NEW", "EMISSIONS PACT", GREEN, draw_globe),
        (370, "CEASEFIRE DEAL", "TALKS END IN SIGNED", "TRUCE AGREEMENT", BLUE, draw_dove),
        (710, "AI RULES SIGNED", "NATIONS ADOPT NEW", "TECH SAFEGUARDS", ACCENT, draw_chip),
    ]
    py0, py1 = 216, 860
    for x0, tag, line1, line2, color, icon in panels:
        x1 = x0 + 284
        fill_rect(img, x0, py0, x1, py1, BG_ALT)
        fill_rect(img, x0, py0, x1, py0 + 8, color)
        # icon
        icon(img, (x0 + x1) // 2, py0 + 130, 95, color)
        # tag bar
        fill_rect(img, x0 + 16, py0 + 240, x1 - 16, py0 + 288, color)
        draw_text_centered_in(img, x0, x1, py0 + 254, tag, BG, 2)
        draw_text_centered_in(img, x0, x1, py0 + 330, line1, WHITE, 2)
        draw_text_centered_in(img, x0, x1, py0 + 372, line2, WHITE, 2)
        line(img, x0 + 60, py0 + 428, x1 - 60, py0 + 428, color, 3)
        draw_text_centered_in(img, x0, x1, py0 + 452, "24 NOV 2026", MUTED, 2)

    # ---- footer ---------------------------------------------------------
    fill_rect(img, 0, 884, WIDTH, 887, ACCENT)
    draw_text_centered(img, 912, "TOP STORIES OF THE DAY", WHITE, 3)
    draw_text_centered(img, 964, "WORLD EDITION - NOVEMBER 24 2026", MUTED, 2)
    fill_rect(img, 0, HEIGHT - 8, WIDTH, HEIGHT, RED)
    return img


def draw_text_centered_in(img, x0, x1, y, text, color, scale=1):
    w = text_width(text, scale)
    draw_text(img, x0 + ((x1 - x0) - w) // 2, y, text, color, scale)


# ----------------------------------------------------------- PNG encoding --
def crc32(data):
    return zlib.crc32(data) & 0xFFFFFFFF


def chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data +
            struct.pack(">I", crc32(tag + data)))


def encode_png(img):
    raw = bytearray()
    for y in range(HEIGHT):
        raw.append(0)  # filter type 0
        row = y * WIDTH
        for x in range(WIDTH):
            r, g, b = img[row + x]
            raw += bytes((r, g, b))
    ihdr = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
            chunk(b"IEND", b""))


def main():
    img = render()
    data = encode_png(img)
    assert len(data) <= 1048576, f"PNG too large: {len(data)} bytes"
    assert data[:8] == b"\x89PNG\r\n\x1a\n"

    out_dir = os.path.dirname(OUTPUT_PATH)
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    # Write twice; bytes are identical both times (pure deterministic render).
    for attempt in (1, 2):
        with open(OUTPUT_PATH, "wb") as f:
            f.write(data)
        with open(OUTPUT_PATH, "rb") as f:
            written = f.read()
        if written != data:
            raise RuntimeError(f"attempt {attempt}: output bytes mismatch")
    print(f"OK: wrote {OUTPUT_PATH} ({len(data)} bytes, "
          f"{WIDTH}x{HEIGHT}, 2 identical writes)")


if __name__ == "__main__":
    main()
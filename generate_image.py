#!/usr/bin/env python3
"""Cosmic Kitten — cheerful kitten astronaut riding a rainbow rocket.

Renders at 2048x2048 with PIL + numpy, then downscales to 1024x1024.
Fully offline and deterministic (fixed seed). No external assets.
"""
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SEED = 20261116
BIG = 2048
OUT = 1024
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

rng = np.random.default_rng(SEED)
py_rng = random.Random(SEED)

TOP = np.array([16, 6, 52], dtype=np.float64)
MID = np.array([92, 22, 118], dtype=np.float64)
BOT = np.array([158, 44, 128], dtype=np.float64)


def vertical_gradient(w, h):
    top_half = np.linspace(TOP, MID, h // 2)[:, None, :]
    bot_half = np.linspace(MID, BOT, h - h // 2)[:, None, :]
    grad = np.concatenate([top_half, bot_half], axis=0)
    grad = np.repeat(grad, w, axis=1)
    return Image.fromarray(grad.astype(np.uint8), "RGB")


def soft_blob(layer, cx, cy, rx, ry, color, blur):
    tmp = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=color)
    tmp = tmp.filter(ImageFilter.GaussianBlur(blur))
    layer.alpha_composite(tmp)


def starburst_points(cx, cy, outer, inner, spikes):
    pts = []
    for i in range(spikes * 2):
        ang = math.pi * i / spikes - math.pi / 2
        r = outer if i % 2 == 0 else inner
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts


def firework(draw, cx, cy, radius, colors):
    for k in range(26):
        ang = 2 * math.pi * k / 26 + py_rng.uniform(-0.08, 0.08)
        ln = radius * py_rng.uniform(0.55, 1.0)
        x2 = cx + ln * math.cos(ang)
        y2 = cy + ln * math.sin(ang)
        col = colors[k % len(colors)]
        draw.line([cx, cy, x2, y2], fill=col, width=10)
        draw.ellipse([x2 - 14, y2 - 14, x2 + 14, y2 + 14], fill=col)
    draw.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=(255, 255, 255))


def build_rocket_layer():
    lw, lh = 1000, 1500
    layer = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # flame: layered teardrops below the body
    d.polygon([(400, 1020), (600, 1020), (500, 1420)], fill=(255, 140, 0, 255))
    d.polygon([(430, 1020), (570, 1020), (500, 1300)], fill=(255, 210, 60, 255))
    d.polygon([(465, 1020), (535, 1020), (500, 1180)], fill=(255, 245, 180, 255))
    # fins
    d.polygon([(370, 880), (370, 1120), (210, 1180)], fill=(255, 80, 120, 255))
    d.polygon([(630, 880), (630, 1120), (790, 1180)], fill=(255, 80, 120, 255))
    # body: rainbow horizontal bands
    bands = [
        (255, 70, 90),
        (255, 150, 50),
        (255, 220, 60),
        (90, 210, 120),
        (70, 160, 255),
        (170, 90, 255),
    ]
    band_h = 700 // len(bands)
    for i, col in enumerate(bands):
        y0 = 350 + i * band_h
        y1 = 350 + (i + 1) * band_h
        d.rectangle([370, y0, 630, y1], fill=col + (255,))
    # body outline
    d.rectangle([370, 350, 630, 1050], outline=(255, 255, 255, 255), width=10)
    # nose cone
    d.polygon([(370, 350), (630, 350), (500, 110)], fill=(255, 70, 90, 255))
    d.polygon([(470, 350), (530, 350), (500, 110)], fill=(255, 220, 60, 255))
    # round window with shine
    d.ellipse([410, 560, 590, 740], fill=(120, 220, 255, 255), outline=(255, 255, 255, 255), width=12)
    d.ellipse([440, 590, 510, 660], fill=(255, 255, 255, 255))
    # rivets down the side
    for y in (420, 500, 800, 880, 960):
        d.ellipse([392, y, 408, y + 16], fill=(255, 255, 255, 255))
        d.ellipse([592, y, 608, y + 16], fill=(255, 255, 255, 255))
    return layer


def draw_kitten(d, hx, hy):
    # tail curling up-left behind the head
    d.arc([hx - 430, hy - 60, hx - 110, hy + 260], start=90, end=270,
          fill=(255, 165, 80, 255), width=46)
    d.arc([hx - 430, hy - 60, hx - 110, hy + 260], start=90, end=270,
          fill=(255, 205, 130, 255), width=22)
    d.ellipse([hx - 300, hy - 90, hx - 240, hy - 30], fill=(255, 205, 130, 255))
    # body hugging the rocket nose
    d.ellipse([hx - 105, hy + 120, hx + 105, hy + 330], fill=(255, 175, 95, 255))
    d.ellipse([hx - 55, hy + 170, hx + 55, hy + 300], fill=(255, 225, 180, 255))
    # paws gripping the nose cone
    d.ellipse([hx - 205, hy + 150, hx - 105, hy + 235], fill=(255, 175, 95, 255))
    d.ellipse([hx + 105, hy + 150, hx + 205, hy + 235], fill=(255, 175, 95, 255))
    # ears
    d.polygon([(hx - 150, hy - 80), (hx - 195, hy - 240), (hx - 40, hy - 165)], fill=(255, 175, 95, 255))
    d.polygon([(hx + 150, hy - 80), (hx + 195, hy - 240), (hx + 40, hy - 165)], fill=(255, 175, 95, 255))
    d.polygon([(hx - 145, hy - 105), (hx - 168, hy - 195), (hx - 70, hy - 150)], fill=(255, 150, 180, 255))
    d.polygon([(hx + 145, hy - 105), (hx + 168, hy - 195), (hx + 70, hy - 150)], fill=(255, 150, 180, 255))
    # head
    d.ellipse([hx - 175, hy - 175, hx + 175, hy + 175], fill=(255, 175, 95, 255))
    # forehead stripes
    for dx in (-70, 0, 70):
        d.polygon([(hx + dx - 22, hy - 168), (hx + dx + 22, hy - 168),
                   (hx + dx + 12, hy - 95), (hx + dx - 12, hy - 95)], fill=(230, 130, 60, 255))
    # helmet bubble
    d.ellipse([hx - 245, hy - 245, hx + 245, hy + 245], outline=(255, 255, 255, 235), width=16)
    d.arc([hx - 225, hy - 225, hx + 225, hy + 225], start=200, end=320, fill=(255, 255, 255, 255), width=22)
    # eyes: happy closed arcs
    d.arc([hx - 125, hy - 55, hx - 45, hy + 35], start=180, end=360, fill=(60, 30, 60, 255), width=14)
    d.arc([hx + 45, hy - 55, hx + 125, hy + 35], start=180, end=360, fill=(60, 30, 60, 255), width=14)
    # nose + open smile
    d.polygon([(hx - 28, hy + 55), (hx + 28, hy + 55), (hx, hy + 88)], fill=(255, 110, 150, 255))
    d.arc([hx - 60, hy + 70, hx + 60, hy + 165], start=0, end=180, fill=(60, 30, 60, 255), width=12)
    # cheeks
    d.ellipse([hx - 165, hy + 55, hx - 105, hy + 105], fill=(255, 140, 150, 200))
    d.ellipse([hx + 105, hy + 55, hx + 165, hy + 105], fill=(255, 140, 150, 200))
    # whiskers
    for dy in (-10, 25, 60):
        d.line([(hx - 175, hy + dy), (hx - 280, hy + dy - 18)], fill=(255, 255, 255, 220), width=8)
        d.line([(hx + 175, hy + dy), (hx + 280, hy + dy - 18)], fill=(255, 255, 255, 220), width=8)


def main():
    img = vertical_gradient(BIG, BIG).convert("RGBA")
    neb = Image.new("RGBA", (BIG, BIG), (0, 0, 0, 0))
    for (cx, cy, rx, ry, col, blur) in [
        (420, 480, 520, 340, (255, 90, 180, 90), 130),
        (1620, 700, 560, 380, (80, 200, 255, 80), 140),
        (1050, 1750, 620, 300, (255, 190, 90, 70), 130),
        (1500, 250, 420, 260, (190, 110, 255, 85), 120),
        (250, 1350, 430, 300, (90, 255, 200, 60), 130),
    ]:
        soft_blob(neb, cx, cy, rx, ry, col, blur)
    img.alpha_composite(neb)

    d = ImageDraw.Draw(img)
    # stars
    for _ in range(300):
        x = int(rng.integers(0, BIG))
        y = int(rng.integers(0, BIG))
        r = int(rng.integers(3, 10))
        col = (255, 255, 255) if rng.random() < 0.7 else (255, 230, 140)
        d.ellipse([x - r, y - r, x + r, y + r], fill=col + (255,))
    # a few sparkle crosses
    for _ in range(24):
        x = int(rng.integers(60, BIG - 60))
        y = int(rng.integers(60, BIG - 60))
        ln = int(rng.integers(18, 42))
        d.line([x - ln, y, x + ln, y], fill=(255, 255, 255, 230), width=6)
        d.line([x, y - ln, x, y + ln], fill=(255, 255, 255, 230), width=6)

    # ringed planet, bottom-left
    px, py, pr = 430, 1600, 270
    d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(70, 205, 195, 255))
    for k, col in enumerate([(50, 170, 165), (120, 230, 210), (50, 170, 165)]):
        y0 = py - pr + 90 + k * 110
        d.rectangle([px - pr, y0, px + pr, y0 + 55], fill=col + (255,))
    d.ellipse([px - pr, py - pr, px + pr, py + pr], outline=(255, 255, 255, 255), width=8)
    ring = Image.new("RGBA", (BIG, BIG), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    rd.ellipse([px - 480, py - 95, px + 480, py + 95], outline=(255, 205, 80, 255), width=30)
    rd.ellipse([px - 400, py - 70, px + 400, py + 70], outline=(255, 240, 170, 255), width=12)
    ring = ring.rotate(-16, resample=Image.BICUBIC, center=(px, py))
    img.alpha_composite(ring)
    d = ImageDraw.Draw(img)

    # moon, top-right
    mx, my, mr = 1800, 250, 105
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(252, 242, 200, 255))
    for (cx, cy, cr) in [(mx - 40, my - 25, 22), (mx + 35, my + 15, 28), (mx + 5, my + 55, 16), (mx - 55, my + 45, 13)]:
        d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(225, 210, 160, 255))
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], outline=(255, 255, 255, 255), width=6)

    # fireworks
    firework(d, 285, 920, 210,
             [(255, 120, 180), (255, 220, 90), (140, 230, 255), (170, 255, 150)])
    firework(d, 1800, 1290, 190,
             [(255, 220, 90), (255, 120, 180), (170, 255, 150), (140, 230, 255)])

    # rainbow rocket, tilted up-right
    rocket = build_rocket_layer().rotate(-28, resample=Image.BICUBIC)
    img.alpha_composite(rocket, (650, 300))

    # kitten astronaut riding the nose (nose tip lands near 1445, 494)
    d = ImageDraw.Draw(img)
    draw_kitten(d, 1475, 430)

    # confetti
    conf_colors = [(255, 90, 140), (255, 210, 60), (90, 220, 160), (90, 170, 255), (200, 120, 255)]
    for _ in range(200):
        x = int(rng.integers(30, BIG - 30))
        y = int(rng.integers(30, BIG - 30))
        col = conf_colors[int(rng.integers(0, len(conf_colors)))]
        if rng.random() < 0.5:
            w = int(rng.integers(12, 30))
            h = int(rng.integers(8, 16))
            d.rectangle([x, y, x + w, y + h], fill=col + (255,))
        else:
            r = int(rng.integers(7, 15))
            d.ellipse([x - r, y - r, x + r, y + r], fill=col + (255,))

    # WOW! starburst badge, top-left
    bx, by = 330, 330
    d.polygon(starburst_points(bx, by, 215, 165, 16), fill=(255, 210, 40, 255),
              outline=(255, 120, 60, 255), width=10)
    font = ImageFont.truetype(FONT_PATH, 100)
    text = "WOW!"
    tb = d.textbbox((0, 0), text, font=font)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    d.text((bx - tw / 2 - tb[0], by - th / 2 - tb[1]), text, font=font, fill=(90, 20, 90, 255))

    small = img.convert("RGB").resize((OUT, OUT), Image.LANCZOS)
    small.save("asset.png", optimize=True)
    print("saved asset.png 1024x1024")


if __name__ == "__main__":
    main()

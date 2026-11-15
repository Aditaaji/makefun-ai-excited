#!/usr/bin/env python3
"""Render the Cosmic Kitten artwork for make.fun ai-excited-01.

Scene: a joyful kitten astronaut rides a rainbow rocket through a candy
nebula, past a ringed planet, fireworks, confetti and a big WOW! burst.

Fully deterministic: one fixed seed drives every random choice, nothing
reads the clock or the network, and the output PNG is byte-identical on
every run. Drawn at 2x and downsampled for smooth edges.

Usage:  python3 generate_image.py   ->  writes asset.png (1024 x 1024)
"""
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

DRAW_SEED = 16112026
OUT_PX = 1024
OVERSAMPLE = 2
CANVAS = OUT_PX * OVERSAMPLE
TARGET = "asset.png"
HEAVY_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

dice = random.Random(DRAW_SEED)

# ---- colours ----
NIGHT = (22, 9, 46)
GRAPE = (98, 42, 140)
BERRY = (208, 74, 130)
EMBER = (255, 140, 66)
DARK = (40, 15, 82)
WHITE = (255, 255, 255)
VANILLA = (255, 243, 210)
GINGER = (255, 158, 66)
GINGER_DARK = (228, 124, 32)
PINK = (255, 105, 138)
PINK_SOFT = (255, 180, 196)
SUNNY = (255, 210, 40)
AQUA = (44, 210, 190)
AZURE = (100, 210, 255)
POPPY = (255, 70, 86)
MINTY = (44, 212, 114)
LILAC = (148, 106, 255)
SPECTRUM = [POPPY, GINGER, SUNNY, MINTY, AZURE, LILAC]


def vertical_blend(side, tall, anchors):
    """Blend *anchors* [(stop 0..1, rgb), ...] down a tall canvas."""
    stops = np.array([a[0] for a in anchors], dtype=float)
    tones = np.array([a[1] for a in anchors], dtype=float)
    ramp = np.linspace(0, 1, tall)
    sheet = np.zeros((tall, side, 3), dtype=np.uint8)
    for band in range(3):
        column = np.interp(ramp, stops, tones[:, band])
        sheet[:, :, band] = np.tile(column[:, None], (1, side)).astype(np.uint8)
    return Image.fromarray(sheet, "RGB")


def bezier_quad(p0, p1, p2, n=140):
    """Sample a quadratic Bezier curve from p0 via p1 to p2."""
    pts = []
    for k in range(n + 1):
        t = k / n
        u = 1 - t
        pts.append((u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
                    u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]))
    return pts


def nudge(pts, dx, dy):
    return [(px + dx, py + dy) for px, py in pts]


def starburst(cx, cy, long_r, short_r, points=14):
    """Vertices of a spiky badge, alternating long and short radii."""
    out = []
    for i in range(points * 2):
        radius = long_r if i % 2 == 0 else short_r
        theta = math.pi * i / points - math.pi / 2
        out.append((cx + radius * math.cos(theta),
                    cy + radius * math.sin(theta)))
    return out


def paint_stars(pen):
    for _ in range(250):
        x = dice.uniform(0, CANVAS)
        y = dice.uniform(0, CANVAS * 0.85)
        r = dice.uniform(2, 7)
        tint = dice.choice([WHITE, (255, 238, 168), (178, 228, 255)])
        pen.ellipse([x - r, y - r, x + r, y + r],
                    fill=tint + (dice.randint(140, 255),))
    for _ in range(14):  # four-point sparkles
        x = dice.uniform(80, CANVAS - 80)
        y = dice.uniform(80, CANVAS * 0.7)
        r = dice.uniform(14, 30)
        sparkle = (255, 255, 255, 230)
        pen.line([x - r, y, x + r, y], fill=sparkle, width=5)
        pen.line([x, y - r, x, y + r], fill=sparkle, width=5)


def paint_planet(pen):
    cx, cy, rad = 320, 320, 145
    pen.ellipse([cx - rad, cy - rad, cx + rad, cy + rad],
                fill=AQUA + (255,))
    pen.ellipse([cx - rad, cy - rad, cx + rad, cy + rad],
                outline=(18, 88, 88, 255), width=8)
    pen.pieslice([cx - rad, cy - rad, cx + rad, cy + rad], 25, 165,
                 fill=(18, 118, 108, 110))
    pen.ellipse([cx - 205, cy - 26, cx + 205, cy + 26],
                outline=SUNNY + (255,), width=16)


def paint_moon(pen):
    cx, cy, rad = 1770, 1710, 108
    pen.ellipse([cx - rad, cy - rad, cx + rad, cy + rad],
                fill=(255, 235, 168, 255))
    for kx, ky, kr in [(1730, 1670, 25), (1810, 1750, 33), (1770, 1630, 17)]:
        pen.ellipse([kx - kr, ky - kr, kx + kr, ky + kr],
                    fill=(230, 198, 118, 255))


def paint_fireworks(pen):
    for cx, cy, tint in [(290, 610, AZURE), (1910, 840, SUNNY),
                         (1830, 1240, PINK)]:
        for k in range(16):
            ang = 2 * math.pi * k / 16 + dice.uniform(-0.1, 0.1)
            length = dice.uniform(70, 130)
            tip = (cx + length * math.cos(ang), cy + length * math.sin(ang))
            pen.line([cx, cy, tip], fill=tint + (255,), width=9)
            pen.ellipse([tip[0] - 10, tip[1] - 10,
                         tip[0] + 10, tip[1] + 10], fill=tint + (255,))
        pen.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=WHITE + (255,))


def paint_puffs(pen):
    for sx, sy, sr in [(880, 1700, 70), (760, 1830, 90), (620, 1940, 105),
                       (980, 1640, 55), (700, 1900, 60)]:
        pen.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                    fill=(255, 255, 255, 46))


def paint_exhaust(pen):
    trail = bezier_quad((1024, 1560), (760, 1850), (430, 2048))
    for i, tint in enumerate(SPECTRUM):
        off = (i - 2.5) * 30
        pen.line(nudge(trail, off * 0.55, -off * 0.35),
                 fill=tint + (255,), width=30, joint="curve")


def paint_rocket(pen):
    left, right, top, bottom = 890, 1158, 980, 1560
    # hull, shaded on the starboard side
    pen.rounded_rectangle([left, top, right, bottom], radius=120,
                          fill=WHITE + (255,), outline=DARK + (255,), width=10)
    pen.rounded_rectangle([left + 150, top, right, bottom], radius=120,
                          fill=(212, 220, 234, 255))
    pen.rounded_rectangle([left, top, right, bottom], radius=120,
                          outline=DARK + (255,), width=10)
    # red band + rivets
    pen.rectangle([left, 1330, right, 1396], fill=POPPY + (255,))
    for ry in (1060, 1160, 1470):
        pen.ellipse([left + 22, ry, left + 46, ry + 24],
                    fill=(148, 158, 178, 255))
    # tail fins
    pen.polygon([(left + 6, 1400), (left - 130, 1620), (left + 6, bottom)],
                fill=POPPY + (255,), outline=DARK + (255,))
    pen.polygon([(right - 6, 1400), (right + 130, 1620), (right - 6, bottom)],
                fill=POPPY + (255,), outline=DARK + (255,))
    # flame: nested tongues, gold -> orange -> white
    for shape, tint in [
            ([(940, 1560), (1110, 1560), (1064, 1780), (1024, 1890), (984, 1780)],
             (255, 210, 40, 255)),
            ([(968, 1560), (1082, 1560), (1052, 1720), (1024, 1800), (998, 1720)],
             (255, 126, 40, 255)),
            ([(992, 1560), (1058, 1560), (1038, 1670), (1024, 1720), (1012, 1670)],
             (255, 255, 255, 255))]:
        pen.polygon(shape, fill=tint)


def paint_kitten(pen):
    hx, hy, hr = 1024, 800, 400
    # glass helmet dome
    pen.ellipse([hx - hr, hy - hr, hx + hr, hy + hr],
                fill=(175, 223, 255, 255))
    pen.ellipse([hx - hr, hy - hr, hx + hr, hy + hr],
                outline=DARK + (255,), width=12)
    fx, fy, fr = hx, hy + 40, 250
    # ears: ginger outside, soft pink inside
    for sign in (-1, 1):
        pen.polygon([(fx + sign * 195, fy - 150), (fx + sign * 260, fy - 330),
                     (fx + sign * 80, fy - 210)],
                    fill=GINGER + (255,), outline=DARK + (255,))
        pen.polygon([(fx + sign * 185, fy - 165), (fx + sign * 225, fy - 285),
                     (fx + sign * 115, fy - 205)], fill=PINK_SOFT + (255,))
    # head
    pen.ellipse([fx - fr, fy - fr, fx + fr, fy + fr],
                fill=GINGER + (255,), outline=DARK + (255,), width=10)
    # forehead stripes
    for sx in (-90, 0, 90):
        pen.line([fx + sx - 14, fy - fr + 26, fx + sx + 14, fy - fr + 96],
                 fill=GINGER_DARK + (255,), width=16)
    # cream muzzle
    pen.ellipse([fx - 130, fy + 30, fx + 130, fy + 185], fill=VANILLA + (255,))
    # big sparkling eyes, gazing upward
    for ex in (-115, 115):
        pen.ellipse([fx + ex - 62, fy - 105, fx + ex + 62, fy + 15],
                    fill=WHITE + (255,), outline=DARK + (255,), width=7)
        pen.ellipse([fx + ex - 34, fy - 78, fx + ex + 34, fy - 2],
                    fill=(40, 15, 82, 255))
        pen.ellipse([fx + ex - 30, fy - 82, fx + ex + 2, fy - 44],
                    fill=WHITE + (255,))
        pen.ellipse([fx + ex + 12, fy - 42, fx + ex + 30, fy - 22],
                    fill=WHITE + (255,))
    # blush
    pen.ellipse([fx - 205, fy + 55, fx - 125, fy + 115],
                fill=(255, 105, 138, 150))
    pen.ellipse([fx + 125, fy + 55, fx + 205, fy + 115],
                fill=(255, 105, 138, 150))
    # little triangle nose + open happy mouth
    pen.polygon([(fx - 34, fy + 62), (fx + 34, fy + 62), (fx, fy + 104)],
                fill=PINK + (255,), outline=DARK + (255,))
    pen.pieslice([fx - 62, fy + 96, fx + 62, fy + 190], 0, 180,
                 fill=(148, 30, 62, 255), outline=DARK + (255,))
    pen.ellipse([fx - 34, fy + 132, fx + 34, fy + 178],
                fill=(255, 118, 138, 255))
    # whiskers
    for side in (-1, 1):
        for wy, tilt in ((fy + 70, -18), (fy + 100, 0), (fy + 130, 18)):
            start = fx + side * 130
            pen.line([start, wy, start + side * 150, wy + tilt],
                     fill=(40, 15, 82, 220), width=7)
    # helmet rim, glass shine and glint
    pen.ellipse([hx - hr, hy - hr, hx + hr, hy + hr],
                outline=WHITE + (255,), width=26)
    pen.arc([hx - hr + 30, hy - hr + 30, hx + hr - 120, hy + hr - 120],
            200, 320, fill=(255, 255, 255, 200), width=34)
    pen.ellipse([hx - 300, hy - 300, hx - 190, hy - 180],
                fill=(255, 255, 255, 170))


def paint_badge(pen):
    bx, by = 1620, 320
    outline_pts = starburst(bx, by, 235, 168)
    pen.polygon(outline_pts, fill=SUNNY + (255,), outline=DARK + (255,))
    pen.polygon(outline_pts, outline=(255, 126, 40, 255), width=10)
    heavy = ImageFont.truetype(HEAVY_FONT, 110)
    pen.text((bx, by), "WOW!", font=heavy, fill=DARK + (255,), anchor="mm")


def paint_confetti(pen):
    shades = [SUNNY, PINK, AQUA, AZURE, WHITE, MINTY]
    for _ in range(110):
        x = dice.uniform(40, CANVAS - 40)
        y = dice.uniform(40, CANVAS - 40)
        if (x - 1024) ** 2 + (y - 800) ** 2 < 330 ** 2:
            continue  # keep the hero face readable
        tint = dice.choice(shades)
        w = dice.uniform(16, 34)
        h = dice.uniform(8, 16)
        ang = dice.uniform(0, math.pi)
        ca, sa = math.cos(ang), math.sin(ang)
        corners = []
        for dx, dy in [(-w, -h), (w, -h), (w, h), (-w, h)]:
            corners.append((x + dx * ca - dy * sa, y + dx * sa + dy * ca))
        pen.polygon(corners, fill=tint + (255,))


def compose():
    picture = vertical_blend(CANVAS, CANVAS, [
        (0.00, NIGHT),
        (0.35, GRAPE),
        (0.65, BERRY),
        (1.00, EMBER),
    ]).convert("RGBA")

    # soft pink glow behind the hero
    halo = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    halo_pen = ImageDraw.Draw(halo)
    halo_pen.ellipse([512, 350, 1536, 1450], fill=(255, 120, 180, 70))
    picture = Image.alpha_composite(
        picture, halo.filter(ImageFilter.GaussianBlur(180)))

    pen = ImageDraw.Draw(picture, "RGBA")
    paint_stars(pen)
    paint_planet(pen)
    paint_moon(pen)
    paint_fireworks(pen)
    paint_puffs(pen)
    paint_exhaust(pen)
    paint_rocket(pen)
    paint_kitten(pen)
    paint_badge(pen)
    paint_confetti(pen)
    return picture.convert("RGB").resize((OUT_PX, OUT_PX), Image.LANCZOS)


if __name__ == "__main__":
    art = compose()
    art.save(TARGET, format="PNG", optimize=True)
    print(f"wrote {TARGET} {art.size}")

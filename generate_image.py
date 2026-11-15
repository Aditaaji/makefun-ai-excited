#!/usr/bin/env python3
"""Draw the Cosmic Kitten picture for make.fun ai-excited-01.

A joyful kitten astronaut rides a rainbow rocket through a candy nebula,
surrounded by fireworks, confetti and a big WOW! burst. The drawing is
fully deterministic (fixed seed, no network, no clock): running this file
always writes the same bytes.

Usage:  python3 generate_image.py   ->  writes asset.png (1024x1024)
"""
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SEED = 20261116
FINAL = 1024               # output size, pixels
SS = 2                     # supersampling: draw at 2048, shrink to 1024
W = FINAL * SS
OUT = "asset.png"
BOLD_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

rng = random.Random(SEED)

# ---- palette ----
DEEP_SPACE = (24, 10, 48)
PLUM = (96, 44, 138)
RASPBERRY = (205, 78, 128)
SUNSET = (255, 142, 68)
INK = (43, 16, 85)
SNOW = (255, 255, 255)
CREAM = (255, 244, 214)
FUR = (255, 159, 67)
FUR_SHADE = (230, 126, 34)
ROSE = (255, 107, 139)
ROSE_PALE = (255, 183, 197)
GOLD = (255, 211, 42)
MINT = (45, 212, 191)
SKY = (104, 211, 255)
CHERRY = (255, 71, 87)
LEAF = (46, 213, 115)
VIOLET = (150, 108, 255)
RAINBOW = [CHERRY, FUR, GOLD, LEAF, SKY, VIOLET]


def sky_gradient(width, height, stops):
    """Vertical gradient from a list of (position 0..1, rgb) stops."""
    xs = np.array([s[0] for s in stops], dtype=float)
    rgbs = np.array([s[1] for s in stops], dtype=float)
    frac = np.linspace(0, 1, height)
    arr = np.zeros((height, width, 3), dtype=np.uint8)
    for ch in range(3):
        col = np.interp(frac, xs, rgbs[:, ch])
        arr[:, :, ch] = np.tile(col[:, None], (1, width)).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def quad_bezier(a, b, c, steps=140):
    """Points along a quadratic Bezier curve from a via b to c."""
    out = []
    for i in range(steps + 1):
        t = i / steps
        x = (1 - t) ** 2 * a[0] + 2 * (1 - t) * t * b[0] + t ** 2 * c[0]
        y = (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * b[1] + t ** 2 * c[1]
        out.append((x, y))
    return out


def shift(points, dx, dy):
    return [(x + dx, y + dy) for x, y in points]


def burst_polygon(cx, cy, outer, inner, spikes=14):
    """Alternating long/short vertices of a starburst badge."""
    verts = []
    for i in range(spikes * 2):
        r = outer if i % 2 == 0 else inner
        ang = math.pi * i / spikes - math.pi / 2
        verts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return verts


def scatter_stars(d):
    for _ in range(240):
        x = rng.uniform(0, W)
        y = rng.uniform(0, W * 0.85)
        r = rng.uniform(2, 7)
        col = rng.choice([SNOW, (255, 240, 170), (180, 230, 255)])
        d.ellipse([x - r, y - r, x + r, y + r],
                  fill=col + (rng.randint(140, 255),))
    for _ in range(14):  # four-point sparkles
        x = rng.uniform(80, W - 80)
        y = rng.uniform(80, W * 0.7)
        r = rng.uniform(14, 30)
        col = (255, 255, 255, 230)
        d.line([x - r, y, x + r, y], fill=col, width=5)
        d.line([x, y - r, x, y + r], fill=col, width=5)


def ringed_planet(d):
    cx, cy, rad = 330, 330, 150
    d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=MINT + (255,))
    d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad],
              outline=(20, 90, 90, 255), width=8)
    d.pieslice([cx - rad, cy - rad, cx + rad, cy + rad], 20, 160,
               fill=(20, 120, 110, 110))
    d.ellipse([cx - 210, cy - 28, cx + 210, cy + 28],
              outline=GOLD + (255,), width=16)


def crater_moon(d):
    cx, cy, rad = 1760, 1700, 110
    d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad],
              fill=(255, 236, 170, 255))
    for kx, ky, kr in [(1720, 1660, 26), (1800, 1740, 34), (1760, 1620, 18)]:
        d.ellipse([kx - kr, ky - kr, kx + kr, ky + kr],
                  fill=(232, 200, 120, 255))


def fireworks(d):
    for cx, cy, col in [(300, 620, SKY), (1900, 850, GOLD), (1820, 1250, ROSE)]:
        for k in range(16):
            ang = 2 * math.pi * k / 16 + rng.uniform(-0.1, 0.1)
            ln = rng.uniform(70, 130)
            x2 = cx + ln * math.cos(ang)
            y2 = cy + ln * math.sin(ang)
            d.line([cx, cy, x2, y2], fill=col + (255,), width=9)
            d.ellipse([x2 - 10, y2 - 10, x2 + 10, y2 + 10], fill=col + (255,))
        d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=SNOW + (255,))


def smoke(d):
    for sx, sy, sr in [(880, 1700, 70), (760, 1830, 90), (620, 1940, 105),
                       (980, 1640, 55), (700, 1900, 60)]:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                  fill=(255, 255, 255, 46))


def rainbow_trail(d):
    path = quad_bezier((1024, 1560), (760, 1850), (430, 2048))
    for i, col in enumerate(RAINBOW):
        off = (i - 2.5) * 30
        d.line(shift(path, off * 0.55, -off * 0.35),
               fill=col + (255,), width=30, joint="curve")


def rocket(d):
    x0, x1, y0, y1 = 890, 1158, 980, 1560
    # body, with a shaded right side
    d.rounded_rectangle([x0, y0, x1, y1], radius=120,
                        fill=SNOW + (255,), outline=INK + (255,), width=10)
    d.rounded_rectangle([x0 + 150, y0, x1, y1], radius=120,
                        fill=(214, 222, 235, 255))
    d.rounded_rectangle([x0, y0, x1, y1], radius=120,
                        outline=INK + (255,), width=10)
    # red stripe + rivets
    d.rectangle([x0, 1330, x1, 1396], fill=CHERRY + (255,))
    for ry in (1060, 1160, 1470):
        d.ellipse([x0 + 22, ry, x0 + 46, ry + 24], fill=(150, 160, 180, 255))
    # fins
    d.polygon([(x0 + 6, 1400), (x0 - 130, 1620), (x0 + 6, 1560)],
              fill=CHERRY + (255,), outline=INK + (255,))
    d.polygon([(x1 - 6, 1400), (x1 + 130, 1620), (x1 - 6, 1560)],
              fill=CHERRY + (255,), outline=INK + (255,))
    # flame: three nested tongues
    for pts, col in [
            ([(940, 1560), (1110, 1560), (1064, 1780), (1024, 1890), (984, 1780)],
             (255, 211, 42, 255)),
            ([(968, 1560), (1082, 1560), (1052, 1720), (1024, 1800), (998, 1720)],
             (255, 127, 42, 255)),
            ([(992, 1560), (1058, 1560), (1038, 1670), (1024, 1720), (1012, 1670)],
             (255, 255, 255, 255))]:
        d.polygon(pts, fill=col)


def kitten_astronaut(d):
    hx, hy, hr = 1024, 800, 400
    # glass helmet dome
    d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(176, 224, 255, 255))
    d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], outline=INK + (255,), width=12)
    fx, fy, fr = hx, hy + 40, 250
    # ears (outer fur, inner pink)
    for sgn in (-1, 1):
        d.polygon([(fx + sgn * 195, fy - 150), (fx + sgn * 260, fy - 330),
                   (fx + sgn * 80, fy - 210)],
                  fill=FUR + (255,), outline=INK + (255,))
        d.polygon([(fx + sgn * 185, fy - 165), (fx + sgn * 225, fy - 285),
                   (fx + sgn * 115, fy - 205)], fill=ROSE_PALE + (255,))
    # head
    d.ellipse([fx - fr, fy - fr, fx + fr, fy + fr],
              fill=FUR + (255,), outline=INK + (255,), width=10)
    # forehead stripes
    for sx in (-90, 0, 90):
        d.line([fx + sx - 14, fy - fr + 26, fx + sx + 14, fy - fr + 96],
               fill=FUR_SHADE + (255,), width=16)
    # muzzle
    d.ellipse([fx - 130, fy + 30, fx + 130, fy + 185], fill=CREAM + (255,))
    # huge sparkling eyes, looking up
    for ex in (-115, 115):
        d.ellipse([fx + ex - 62, fy - 105, fx + ex + 62, fy + 15],
                  fill=SNOW + (255,), outline=INK + (255,), width=7)
        d.ellipse([fx + ex - 34, fy - 78, fx + ex + 34, fy - 2],
                  fill=(43, 16, 85, 255))
        d.ellipse([fx + ex - 30, fy - 82, fx + ex + 2, fy - 44],
                  fill=SNOW + (255,))
        d.ellipse([fx + ex + 12, fy - 42, fx + ex + 30, fy - 22],
                  fill=SNOW + (255,))
    # blush
    d.ellipse([fx - 205, fy + 55, fx - 125, fy + 115], fill=(255, 107, 139, 150))
    d.ellipse([fx + 125, fy + 55, fx + 205, fy + 115], fill=(255, 107, 139, 150))
    # nose + open happy mouth
    d.polygon([(fx - 34, fy + 62), (fx + 34, fy + 62), (fx, fy + 104)],
              fill=ROSE + (255,), outline=INK + (255,))
    d.pieslice([fx - 62, fy + 96, fx + 62, fy + 190], 0, 180,
               fill=(150, 32, 64, 255), outline=INK + (255,))
    d.ellipse([fx - 34, fy + 132, fx + 34, fy + 178], fill=(255, 120, 140, 255))
    # whiskers
    for side in (-1, 1):
        for wy, tilt in ((fy + 70, -18), (fy + 100, 0), (fy + 130, 18)):
            x0 = fx + side * 130
            d.line([x0, wy, x0 + side * 150, wy + tilt],
                   fill=(43, 16, 85, 220), width=7)
    # helmet rim + glass shine
    d.ellipse([hx - hr, hy - hr, hx + hr, hy + hr],
              outline=SNOW + (255,), width=26)
    d.arc([hx - hr + 30, hy - hr + 30, hx + hr - 120, hy + hr - 120],
          200, 320, fill=(255, 255, 255, 200), width=34)
    d.ellipse([hx - 300, hy - 300, hx - 190, hy - 180],
              fill=(255, 255, 255, 170))


def wow_badge(d):
    bx, by = 1620, 320
    pts = burst_polygon(bx, by, 235, 168)
    d.polygon(pts, fill=GOLD + (255,), outline=INK + (255,))
    d.polygon(pts, outline=(255, 127, 42, 255), width=10)
    font = ImageFont.truetype(BOLD_FONT, 118)
    d.text((bx, by), "WOW!", font=font, fill=INK + (255,),
           anchor="mm", stroke_width=0)


def confetti(d):
    cols = [GOLD, ROSE, MINT, SKY, SNOW, LEAF]
    for _ in range(110):
        x = rng.uniform(40, W - 40)
        y = rng.uniform(40, W - 40)
        if (x - 1024) ** 2 + (y - 800) ** 2 < 330 ** 2:
            continue  # keep the hero face readable
        col = rng.choice(cols)
        w = rng.uniform(16, 34)
        h = rng.uniform(8, 16)
        a = rng.uniform(0, math.pi)
        ca, sa = math.cos(a), math.sin(a)
        corners = []
        for dx, dy in [(-w, -h), (w, -h), (w, h), (-w, h)]:
            corners.append((x + dx * ca - dy * sa, y + dx * sa + dy * ca))
        d.polygon(corners, fill=col + (255,))


def draw():
    img = sky_gradient(W, W, [
        (0.00, DEEP_SPACE),
        (0.35, PLUM),
        (0.65, RASPBERRY),
        (1.00, SUNSET),
    ]).convert("RGBA")

    # soft pink glow behind the hero
    glow = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([512, 350, 1536, 1450], fill=(255, 120, 180, 70))
    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(180)))

    d = ImageDraw.Draw(img, "RGBA")
    scatter_stars(d)
    ringed_planet(d)
    crater_moon(d)
    fireworks(d)
    smoke(d)
    rainbow_trail(d)
    rocket(d)
    kitten_astronaut(d)
    wow_badge(d)
    confetti(d)
    return img.convert("RGB").resize((FINAL, FINAL), Image.LANCZOS)


if __name__ == "__main__":
    pic = draw()
    pic.save(OUT, format="PNG", optimize=True)
    print(f"wrote {OUT} {pic.size}")

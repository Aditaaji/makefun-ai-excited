#!/usr/bin/env python3
"""
Cosmic Kitten — a cheerful astronaut kitten riding a rainbow rocket.

Deterministic, fully offline PIL + numpy scene renderer.
Renders at 2048x2048, downscales to 1024x1024 and saves asset.png.
"""
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SEED = 20261116
W = H = 2048
OUT = "asset.png"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

rng = random.Random(SEED)
np_rng = np.random.default_rng(SEED)


# ---------------------------------------------------------------- helpers
def star_points(cx, cy, r_out, r_in, n=5, rot=-math.pi / 2):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        ang = rot + i * math.pi / n
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    return pts


def glow_text(base, xy, text, font, fill, glow, glow_w=14):
    """Draw text with a soft coloured halo underneath."""
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text(xy, text, font=font, fill=glow + (255,), anchor="mm",
           stroke_width=glow_w, stroke_fill=glow + (255,))
    layer = layer.filter(ImageFilter.GaussianBlur(10))
    base.alpha_composite(layer)
    d = ImageDraw.Draw(base)
    d.text(xy, text, font=font, fill=fill + (255,), anchor="mm",
           stroke_width=3, stroke_fill=(20, 8, 48, 255))


# ---------------------------------------------------------------- background
def make_background():
    # vertical gradient: deep indigo -> violet -> magenta dusk
    top = np.array([8, 5, 34], dtype=float)
    mid = np.array([30, 12, 84], dtype=float)
    bot = np.array([64, 22, 110], dtype=float)
    t = np.linspace(0, 1, H)[:, None, None]
    top_half = top + (mid - top) * np.clip(t * 2, 0, 1)
    bot_half = mid + (bot - mid) * np.clip((t - 0.5) * 2, 0, 1)
    grad = np.where(t < 0.5, top_half, bot_half)
    grad = np.repeat(grad, W, axis=1)
    x = np.linspace(0, 1, W)[None, :, None]
    grad += (np.sin(x * math.pi) * 6).astype(float)
    img = Image.fromarray(np.clip(grad, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    return img


def add_nebula(img):
    neb = Image.new("RGBA", img.size, (0, 0, 0, 0))
    palette = [(168, 85, 247), (236, 72, 153), (34, 211, 238),
               (99, 102, 241), (244, 114, 182), (45, 212, 191)]
    for _ in range(26):
        cx = rng.randint(0, W)
        cy = rng.randint(0, H)
        r = rng.randint(180, 520)
        col = rng.choice(palette)
        blob = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(blob)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col + (46,))
        blob = blob.filter(ImageFilter.GaussianBlur(r * 0.55))
        neb.alpha_composite(blob)
    img.alpha_composite(neb)


def add_stars(img):
    d = ImageDraw.Draw(img)
    for _ in range(650):
        x = rng.randint(0, W - 1)
        y = rng.randint(0, H - 1)
        r = rng.choice([1, 1, 2, 2, 2, 3, 4])
        bright = rng.randint(150, 255)
        col = rng.choice([(255, 255, 255), (255, 244, 200),
                          (200, 225, 255), (255, 220, 235)])
        col = tuple(int(c * bright / 255) for c in col)
        d.ellipse([x - r, y - r, x + r, y + r], fill=col + (255,))
        if r >= 3 and rng.random() < 0.5:  # sparkle cross
            ln = r * 4
            d.line([x - ln, y, x + ln, y], fill=col + (160,), width=2)
            d.line([x, y - ln, x, y + ln], fill=col + (160,), width=2)
    for _ in range(14):
        x = rng.randint(80, W - 80)
        y = rng.randint(80, H - 80)
        s = rng.randint(14, 30)
        d.polygon(star_points(x, y, s, s * 0.28, n=4),
                  fill=(255, 255, 255, 235))
        d.polygon(star_points(x, y, s * 0.55, s * 0.16, n=4),
                  fill=(255, 240, 180, 220))


def add_shooting_star(img):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0 = 1580, 260
    x1, y1 = 1180, 520
    for i, wdt in enumerate([16, 10, 5, 2]):
        t = i / 4
        d.line([x0 - (x0 - x1) * t * 0.55, y0 - (y0 - y1) * t * 0.55, x1, y1],
               fill=(255, 255, 255, 200 - i * 40), width=wdt)
    d.ellipse([x1 - 12, y1 - 12, x1 + 12, y1 + 12], fill=(255, 255, 255, 255))
    layer = layer.filter(ImageFilter.GaussianBlur(3))
    img.alpha_composite(layer)


# ---------------------------------------------------------------- planet
def add_ringed_planet(img):
    px, py, pr = 330, 1620, 300
    yy, xx = np.mgrid[0:2 * pr, 0:2 * pr]
    dx = (xx - pr) / pr
    dy = (yy - pr) / pr
    dist = np.sqrt(dx ** 2 + dy ** 2)
    mask = dist <= 1.0
    light = np.clip(0.55 + 0.75 * (dx * 0.6 - dy * 0.8), 0.15, 1.15)
    base_col = np.array([232, 148, 90], dtype=float)   # warm orange
    band = (np.sin(dy * 14 + 0.8) * 0.5 + 0.5)
    band_col = np.array([250, 205, 140], dtype=float)
    col = base_col * (1 - band[..., None] * 0.35) + band_col * (band[..., None] * 0.35)
    col = col * light[..., None]
    arr = np.zeros((2 * pr, 2 * pr, 4), dtype=np.uint8)
    arr[..., :3] = np.clip(col, 0, 255).astype(np.uint8)
    arr[..., 3] = (mask * 255).astype(np.uint8)
    planet = Image.fromarray(arr, "RGBA")
    # shadow crescent on the lower left
    sh = Image.new("RGBA", planet.size, (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    ds.ellipse([pr - 30, -40, pr + 2 * pr, 2 * pr + 40],
               fill=(40, 10, 60, 110))
    sh = sh.filter(ImageFilter.GaussianBlur(30))
    m = Image.new("L", planet.size, 0)
    ImageDraw.Draw(m).ellipse([0, 0, 2 * pr, 2 * pr], fill=255)
    sh.putalpha(Image.composite(sh.split()[3], Image.new("L", planet.size, 0), m))
    planet.alpha_composite(sh)

    # ring: draw on big layer, rotate slightly, paste behind + front
    ring_layer = Image.new("RGBA", (1400, 1400), (0, 0, 0, 0))
    dr = ImageDraw.Draw(ring_layer)
    cx = cy = 700
    for i, (c, a) in enumerate([((250, 200, 130), 210), ((240, 170, 100), 190),
                                ((255, 220, 160), 170), ((200, 130, 80), 150)]):
        dr.ellipse([cx - 560 + i * 14, cy - 150 + i * 8,
                    cx + 560 - i * 14, cy + 150 - i * 8],
                   outline=c + (a,), width=26)
    ring_layer = ring_layer.rotate(-14, resample=Image.BICUBIC, center=(cx, cy))
    img.alpha_composite(ring_layer, (px - 700, py - 700))
    img.alpha_composite(planet, (px - pr, py - pr))
    # front half of the ring over the planet's lower edge
    front = ring_layer.crop((0, 700, 1400, 1400))
    img.alpha_composite(front, (px - 700, py))


def add_small_moon(img):
    mx, my, mr = 1780, 420, 110
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(235, 230, 245, 255))
    for _ in range(9):
        cx = mx + rng.randint(-mr + 25, mr - 25)
        cy = my + rng.randint(-mr + 25, mr - 25)
        cr = rng.randint(10, 26)
        d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr],
                  fill=(205, 198, 220, 255))
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    img.alpha_composite(layer)
    d = ImageDraw.Draw(img)
    d.ellipse([mx - mr - 8, my - mr - 8, mx + mr + 8, my + mr + 8],
              outline=(255, 255, 255, 90), width=4)


# ---------------------------------------------------------------- rainbow flame
RAINBOW = [(239, 68, 68), (249, 115, 22), (250, 204, 21),
           (34, 197, 94), (59, 130, 246), (139, 92, 246),
           (236, 72, 153)]


def add_rainbow_trail(img, tip, direction, length=950):
    """Rainbow exhaust streaming behind the rocket tail."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    dx, dy = direction
    px, py = -dy, dx  # perpendicular
    n = len(RAINBOW)
    for i, col in enumerate(RAINBOW):
        t0 = i / n
        t1 = (i + 1) / n
        w0 = 150 * (1 - t0 * 0.55)
        w1 = 150 * (1 - t1 * 0.55)
        x0, y0 = tip[0] + dx * length * t0, tip[1] + dy * length * t0
        x1, y1 = tip[0] + dx * length * t1, tip[1] + dy * length * t1
        d.polygon([(x0 + px * w0, y0 + py * w0), (x1 + px * w1, y1 + py * w1),
                   (x1 - px * w1, y1 - py * w1), (x0 - px * w0, y0 - py * w0)],
                  fill=col + (235,))
    for _ in range(90):
        t = rng.random()
        off = rng.uniform(-90, 90) * (1 - t * 0.5)
        x = tip[0] + dx * length * t + px * off
        y = tip[1] + dy * length * t + py * off
        r = rng.randint(3, 9)
        col = rng.choice([(255, 255, 255), (255, 240, 150), (255, 200, 220)])
        d.ellipse([x - r, y - r, x + r, y + r], fill=col + (230,))
    layer = layer.filter(ImageFilter.GaussianBlur(6))
    img.alpha_composite(layer)
    # bright core flame right at the tail
    core = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dc = ImageDraw.Draw(core)
    for r, col in [(150, (255, 240, 160)), (105, (255, 190, 80)),
                   (60, (255, 120, 40))]:
        ex, ey = tip[0] + dx * r * 2.2, tip[1] + dy * r * 2.2
        dc.ellipse([ex - r, ey - r * 0.55, ex + r, ey + r * 0.55],
                   fill=col + (240,))
    core = core.filter(ImageFilter.GaussianBlur(18))
    img.alpha_composite(core)


# ---------------------------------------------------------------- rocket + kitten
def draw_rocket():
    """Upright rocket on its own layer; caller rotates & pastes."""
    S = 900
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx = S // 2
    top, bot = 90, 760
    body_w = 150
    # fins (behind body)
    d.polygon([(cx - body_w, bot - 60), (cx - body_w - 130, bot + 60),
               (cx - body_w, bot + 40)], fill=(239, 68, 68, 255))
    d.polygon([(cx + body_w, bot - 60), (cx + body_w + 130, bot + 60),
               (cx + body_w, bot + 40)], fill=(239, 68, 68, 255))
    d.polygon([(cx - body_w, bot - 60), (cx - body_w - 110, bot + 40),
               (cx - body_w, bot + 20)], fill=(185, 28, 28, 255))
    d.polygon([(cx + body_w, bot - 60), (cx + body_w + 110, bot + 40),
               (cx + body_w, bot + 20)], fill=(185, 28, 28, 255))
    # body
    d.rounded_rectangle([cx - body_w, top + 130, cx + body_w, bot],
                        radius=70, fill=(248, 250, 252, 255),
                        outline=(203, 213, 225, 255), width=6)
    # nose cone
    d.polygon([(cx - body_w, top + 130), (cx + body_w, top + 130),
               (cx, top - 40)], fill=(239, 68, 68, 255))
    # rainbow stripes along the body
    stripe_top = top + 330
    sh = 34
    for i, col in enumerate(RAINBOW):
        y0 = stripe_top + i * sh
        d.rectangle([cx - body_w + 4, y0, cx + body_w - 4, y0 + sh],
                    fill=col + (255,))
    # porthole window
    d.ellipse([cx - 62, top + 195, cx + 62, top + 319],
              fill=(186, 230, 253, 255), outline=(148, 163, 184, 255), width=8)
    d.ellipse([cx - 40, top + 210, cx + 10, top + 262],
              fill=(255, 255, 255, 220))
    # rivets
    for yy in (top + 420, top + 470, top + 520, top + 570, top + 640, top + 700):
        d.ellipse([cx - body_w + 18, yy, cx - body_w + 34, yy + 16],
                  fill=(148, 163, 184, 255))
        d.ellipse([cx + body_w - 34, yy, cx + body_w - 18, yy + 16],
                  fill=(148, 163, 184, 255))
    # engine nozzle
    d.polygon([(cx - 95, bot), (cx + 95, bot), (cx + 60, bot + 78),
               (cx - 60, bot + 78)], fill=(100, 116, 139, 255))
    d.polygon([(cx - 60, bot + 78), (cx + 60, bot + 78), (cx + 42, bot + 92),
               (cx - 42, bot + 92)], fill=(71, 85, 105, 255))
    return lay


def draw_kitten():
    """Cheerful orange tabby astronaut kitten, upright, on own layer."""
    S = 1100
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx = S // 2
    orange = (249, 146, 60)
    orange_d = (234, 110, 30)
    cream = (255, 224, 178)
    pink = (244, 143, 177)

    # tail (curled, behind body)
    d.line([(cx + 150, 830), (cx + 260, 760), (cx + 300, 640),
            (cx + 250, 560)], fill=orange_d + (255,), width=64,
           joint="curve")
    d.line([(cx + 150, 830), (cx + 260, 760), (cx + 300, 640),
            (cx + 250, 560)], fill=orange + (255,), width=48,
           joint="curve")
    d.ellipse([cx + 210, 520, cx + 300, 600], fill=cream + (255,))

    # body: white spacesuit with orange patches
    d.rounded_rectangle([cx - 165, 640, cx + 165, 900], radius=90,
                        fill=(248, 250, 252, 255), outline=(203, 213, 225, 255),
                        width=6)
    # suit rainbow chest band
    for i, col in enumerate(RAINBOW):
        d.rectangle([cx - 165 + i * 47, 700, cx - 165 + (i + 1) * 47, 726],
                    fill=col + (255,))
    # belly patch + control panel
    d.ellipse([cx - 95, 760, cx + 95, 880], fill=(255, 241, 214, 255))
    d.rounded_rectangle([cx - 70, 770, cx + 70, 850], radius=14,
                        fill=(30, 41, 59, 255))
    for i, col in enumerate([(239, 68, 68), (34, 197, 94), (59, 130, 246)]):
        bx = cx - 48 + i * 48
        d.ellipse([bx, 790, bx + 24, 814], fill=col + (255,))
    d.rectangle([cx - 48, 822, cx + 48, 832], fill=(34, 197, 94, 255))

    # arms reaching forward (gripping the rocket)
    d.line([(cx - 150, 700), (cx - 260, 640)], fill=(248, 250, 252, 255),
           width=70)
    d.line([(cx + 150, 700), (cx + 260, 640)], fill=(248, 250, 252, 255),
           width=70)
    d.ellipse([cx - 292, 606, cx - 222, 676], fill=orange + (255,))  # paws
    d.ellipse([cx + 222, 606, cx + 292, 676], fill=orange + (255,))

    # legs / boots
    d.rounded_rectangle([cx - 150, 880, cx - 40, 980], radius=30,
                        fill=(239, 68, 68, 255))
    d.rounded_rectangle([cx + 40, 880, cx + 150, 980], radius=30,
                        fill=(239, 68, 68, 255))

    # ears
    d.polygon([(cx - 175, 300), (cx - 230, 120), (cx - 60, 210)],
              fill=orange + (255,))
    d.polygon([(cx + 175, 300), (cx + 230, 120), (cx + 60, 210)],
              fill=orange + (255,))
    d.polygon([(cx - 160, 265), (cx - 195, 155), (cx - 95, 210)],
              fill=pink + (255,))
    d.polygon([(cx + 160, 265), (cx + 195, 155), (cx + 95, 210)],
              fill=pink + (255,))

    # head
    d.ellipse([cx - 200, 190, cx + 200, 590], fill=orange + (255,))
    # tabby stripes on forehead
    for xoff in (-120, -40, 40, 120):
        d.polygon([(cx + xoff - 22, 225), (cx + xoff + 22, 225),
                   (cx + xoff + 10, 300), (cx + xoff - 10, 300)],
                  fill=orange_d + (255,))
    # cheeks
    d.ellipse([cx - 195, 400, cx - 95, 480], fill=cream + (255,))
    d.ellipse([cx + 95, 400, cx + 195, 480], fill=cream + (255,))

    # big happy eyes
    for ex in (cx - 95, cx + 95):
        d.ellipse([ex - 42, 350, ex + 42, 438], fill=(255, 255, 255, 255))
        d.ellipse([ex - 26, 368, ex + 26, 430], fill=(30, 27, 75, 255))
        d.ellipse([ex - 10, 378, ex + 14, 402], fill=(255, 255, 255, 255))
    # nose + mouth
    d.polygon([(cx - 26, 470), (cx + 26, 470), (cx, 500)],
              fill=(236, 72, 153, 255))
    d.arc([cx - 55, 495, cx, 545], start=0, end=180,
          fill=(120, 53, 15, 255), width=7)
    d.arc([cx, 495, cx + 55, 545], start=0, end=180,
          fill=(120, 53, 15, 255), width=7)
    # whiskers
    for side in (-1, 1):
        for k, yy in enumerate((440, 470, 500)):
            d.line([(cx + side * 150, yy), (cx + side * 260, yy - 22 + k * 22)],
                   fill=(255, 255, 255, 230), width=5)

    # astronaut helmet bubble over the head
    d.ellipse([cx - 260, 120, cx + 260, 640],
              outline=(255, 255, 255, 235), width=10)
    # glass shine
    shine = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    ds = ImageDraw.Draw(shine)
    ds.polygon([(cx - 210, 180), (cx - 120, 150), (cx - 60, 330),
                (cx - 170, 380)], fill=(255, 255, 255, 70))
    shine = shine.filter(ImageFilter.GaussianBlur(6))
    lay.alpha_composite(shine)
    # helmet ring at the neck
    d.ellipse([cx - 215, 560, cx + 215, 640],
              outline=(226, 232, 240, 255), width=14)
    # oxygen tank peeking behind shoulder
    d.rounded_rectangle([cx - 260, 640, cx - 190, 830], radius=30,
                        fill=(148, 163, 184, 255))
    return lay


def add_rocket_and_kitten(img):
    rocket = draw_rocket()
    kitten = draw_kitten()
    # rocket flies up-right: rotate 38 deg counter-clockwise
    rocket_r = rocket.rotate(38, resample=Image.BICUBIC, expand=True)
    kitten_r = kitten.rotate(38, resample=Image.BICUBIC, expand=True)
    rocket_pos = (660, 640)
    kitten_pos = (270, 150)
    # tail tip of the upright rocket layer: nozzle bottom centre (450, 852),
    # i.e. offset (0, +402) from the layer centre. PIL rotate(angle) is CCW
    # in screen coords (y down), so a point (x, y) maps to
    # (x cos a + y sin a, -x sin a + y cos a).
    ang = math.radians(38)
    rx = 402 * math.sin(ang)
    ry = 402 * math.cos(ang)
    rcx = rocket_pos[0] + rocket_r.width / 2
    rcy = rocket_pos[1] + rocket_r.height / 2
    tail = (rcx + rx, rcy + ry)
    # trail streams down-left, opposite the flight direction
    trail_dir = (-math.cos(math.radians(52)), math.sin(math.radians(52)))
    add_rainbow_trail(img, tail, trail_dir, length=1000)
    img.alpha_composite(rocket_r, rocket_pos)
    img.alpha_composite(kitten_r, kitten_pos)


# ---------------------------------------------------------------- foreground
def add_foreground_sparkles(img):
    d = ImageDraw.Draw(img)
    for _ in range(40):
        x = rng.randint(40, W - 40)
        y = rng.randint(40, H - 40)
        s = rng.randint(8, 20)
        col = rng.choice([(255, 255, 255), (255, 240, 150), (255, 200, 220),
                          (180, 230, 255)])
        d.polygon(star_points(x, y, s, s * 0.3, n=4), fill=col + (220,))


def add_title(img):
    big = ImageFont.truetype(FONT_BOLD, 150)
    small = ImageFont.truetype(FONT_BOLD, 64)
    glow_text(img, (W // 2, 150), "COSMIC KITTEN", big,
              (255, 255, 255), (168, 85, 247))
    glow_text(img, (W // 2, 262), "RIDING THE RAINBOW ROCKET  \u2022  TO THE STARS!",
              small, (255, 240, 180), (236, 72, 153))


def main():
    img = make_background()
    add_nebula(img)
    add_stars(img)
    add_shooting_star(img)
    add_small_moon(img)
    add_ringed_planet(img)
    add_rocket_and_kitten(img)
    add_foreground_sparkles(img)
    add_title(img)
    # gentle vignette
    vig = Image.new("L", img.size, 0)
    dv = ImageDraw.Draw(vig)
    dv.ellipse([-220, -220, W + 220, H + 220], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(220))
    black = Image.new("RGBA", img.size, (0, 0, 0, 255))
    img = Image.composite(img, black, vig)
    img = img.convert("RGB").resize((1024, 1024), Image.LANCZOS)
    img.save(OUT, optimize=True)
    print(f"saved {OUT} (1024x1024)")


if __name__ == "__main__":
    main()

"""Gera as imagens (ilustrações de biologia) usadas pelo tema SiteBio."""
import math, random, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "app", "static", "assets", "img")
os.makedirs(OUT, exist_ok=True)

# paleta
MINT = (116, 198, 157)
MINT_L = (207, 235, 220)
TEAL = (38, 166, 154)
DEEP = (7, 38, 28)
GOLD = (233, 196, 106)
CORAL = (240, 140, 120)
SKY = (130, 205, 230)
PINK = (230, 150, 190)


# ---------- utilidades ----------
def radial_bg(w, h, inner, outer, cx=0.5, cy=0.5):
    y, x = np.mgrid[0:h, 0:w]
    d = np.sqrt(((x - w * cx) / w) ** 2 + ((y - h * cy) / h) ** 2) / 0.8
    d = np.clip(d, 0, 1)[..., None]
    arr = np.array(inner) * (1 - d) + np.array(outer) * d
    return Image.fromarray(arr.astype("uint8"), "RGB").convert("RGBA")


def layer(w, h):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def over(base, lay, blur=0, alpha=1.0):
    if blur:
        lay = lay.filter(ImageFilter.GaussianBlur(blur))
    if alpha < 1:
        a = lay.getchannel("A").point(lambda v: int(v * alpha))
        lay = lay.copy()
        lay.putalpha(a)
    return Image.alpha_composite(base, lay)


def glow(base, lay, radius=10, strength=0.9):
    """Soma um brilho (versão borrada) e depois a camada nítida."""
    base = over(base, lay, blur=radius, alpha=strength)
    return Image.alpha_composite(base, lay)


def grain(img, amount=5, seed=1):
    rng = np.random.default_rng(seed)
    arr = np.array(img.convert("RGB")).astype("int16")
    arr += rng.normal(0, amount, arr.shape[:2])[..., None].astype("int16")
    return Image.fromarray(np.clip(arr, 0, 255).astype("uint8"), "RGB")


def bokeh(base, n, seed, rmin=10, rmax=70, colors=(MINT, TEAL, MINT_L, GOLD), amax=45, blur=2):
    rng = random.Random(seed)
    w, h = base.size
    lay = layer(w, h)
    d = ImageDraw.Draw(lay)
    for _ in range(n):
        r = rng.randint(rmin, rmax)
        x, y = rng.randint(-r, w + r), rng.randint(-r, h + r)
        c = rng.choice(colors)
        a = rng.randint(8, amax)
        d.ellipse([x - r, y - r, x + r, y + r], fill=c + (a,), outline=c + (min(255, a * 3),), width=max(1, r // 14))
    return over(base, lay, blur=blur)


def blob(cx, cy, r, rng, k=0.05, n=90):
    p1, p2, p3 = rng.uniform(0, 6.28), rng.uniform(0, 6.28), rng.uniform(0, 6.28)
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        rr = r * (1 + k * math.sin(3 * t + p1) + k * 0.7 * math.sin(5 * t + p2) + k * 0.4 * math.sin(2 * t + p3))
        pts.append((cx + rr * math.cos(t), cy + rr * math.sin(t)))
    return pts


def rot_ellipse(cx, cy, a, b, ang, n=48):
    ca, sa = math.cos(ang), math.sin(ang)
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x, y = a * math.cos(t), b * math.sin(t)
        pts.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return pts


def save(img, name, q=84):
    img = img.convert("RGB")
    img.save(os.path.join(OUT, name), "JPEG", quality=q, optimize=True, progressive=True)
    print("ok", name, img.size, os.path.getsize(os.path.join(OUT, name)) // 1024, "KB")


# ---------- elementos biológicos ----------
def mitochondria(d, cx, cy, a, b, ang, alpha=230):
    d.polygon(rot_ellipse(cx, cy, a, b, ang), fill=GOLD + (70,), outline=GOLD + (alpha,))
    d.line(rot_ellipse(cx, cy, a, b, ang) + [rot_ellipse(cx, cy, a, b, ang)[0]], fill=GOLD + (alpha,), width=max(2, int(b * 0.12)))
    ca, sa = math.cos(ang), math.sin(ang)
    n = 6
    for i in range(n):
        u = -a * 0.7 + (1.4 * a) * i / (n - 1)
        sign = 1 if i % 2 == 0 else -1
        x1, y1 = u * ca - (sign * b * 0.85) * sa, u * sa + (sign * b * 0.85) * ca
        x2, y2 = u * ca - (-sign * b * 0.1) * sa, u * sa + (-sign * b * 0.1) * ca
        d.line([(cx + x1, cy + y1), (cx + x2, cy + y2)], fill=GOLD + (alpha,), width=max(2, int(b * 0.09)))


def golgi(d, cx, cy, size, ang=0.0, alpha=230):
    for i in range(5):
        L = size * (1 - 0.12 * abs(i - 2))
        off = (i - 2) * size * 0.16
        pts = []
        for j in range(21):
            t = -1 + 2 * j / 20
            x, y = t * L, -size * 0.12 * (1 - t * t) * 3 + off
            ca, sa = math.cos(ang), math.sin(ang)
            pts.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
        d.line(pts, fill=PINK + (alpha,), width=max(3, int(size * 0.07)), joint="curve")


def er(d, cx, cy, r, rng, alpha=200):
    for k in range(4):
        r0 = r * (1.0 + 0.16 * k)
        a0 = rng.uniform(0, 6.28)
        pts = []
        for j in range(60):
            t = a0 + 1.9 * j / 59
            rr = r0 + r * 0.05 * math.sin(14 * t + k)
            pts.append((cx + rr * math.cos(t), cy + rr * math.sin(t)))
        d.line(pts, fill=SKY + (alpha,), width=max(2, int(r * 0.035)), joint="curve")


def cell(base, cx, cy, r, seed, full=True, tone=MINT):
    """Célula animal estilizada com núcleo, mitocôndrias, Golgi, RE e ribossomos."""
    rng = random.Random(seed)
    w, h = base.size
    L = layer(w, h)
    d = ImageDraw.Draw(L)
    pts = blob(cx, cy, r, rng, k=0.04)
    d.polygon(pts, fill=tone + (70,))
    d.line(pts + [pts[0]], fill=MINT_L + (235,), width=max(3, int(r * 0.03)), joint="curve")
    if full:
        # núcleo
        nx, ny, nr = cx + r * 0.12, cy - r * 0.05, r * 0.36
        npts = blob(nx, ny, nr, rng, k=0.03)
        d.polygon(npts, fill=TEAL + (120,))
        d.line(npts + [npts[0]], fill=MINT_L + (230,), width=max(2, int(r * 0.022)), joint="curve")
        d.ellipse([nx - nr * 0.32, ny - nr * 0.2, nx + nr * 0.12, ny + nr * 0.24], fill=GOLD + (170,))
        er(d, nx, ny, nr * 1.15, rng)
        for _ in range(3):
            ang = rng.uniform(0, 6.28)
            rr = r * rng.uniform(0.55, 0.72)
            mitochondria(d, cx + rr * math.cos(ang), cy + rr * math.sin(ang), r * 0.18, r * 0.075, ang + 1.2)
        golgi(d, cx - r * 0.5, cy + r * 0.38, r * 0.27, ang=-0.5)
        for _ in range(26):
            ang = rng.uniform(0, 6.28)
            rr = r * rng.uniform(0.15, 0.85)
            x, y = cx + rr * math.cos(ang), cy + rr * math.sin(ang)
            rr2 = r * 0.017
            d.ellipse([x - rr2, y - rr2, x + rr2, y + rr2], fill=MINT_L + (200,))
    else:
        nr = r * 0.34
        d.ellipse([cx - nr, cy - nr, cx + nr, cy + nr], fill=TEAL + (130,), outline=MINT_L + (200,), width=max(2, int(r * 0.03)))
    return glow(base, L, radius=max(6, r * 0.05), strength=0.55)


def helix(base, x0, x1, cy, amp, period, tilt=0.0, seed=3, scale=1.0):
    w, h = base.size
    L = layer(w, h)
    d = ImageDraw.Draw(L)
    N = int((x1 - x0) / 3)
    items = []
    k = 2 * math.pi / period
    for i in range(N + 1):
        x = x0 + (x1 - x0) * i / N
        ph = k * (x - x0)
        z = math.cos(ph)
        y1, y2 = cy + amp * math.sin(ph), cy - amp * math.sin(ph)
        items.append((z, "s1", x, y1, i))
        items.append((-z, "s2", x, y2, i))
        if i % 9 == 0:
            items.append((0, "rung", x, (y1, y2), i // 9))
    items.sort(key=lambda t: t[0])
    for z, kind, x, y, idx in items:
        depth = (z + 1) / 2
        if kind == "rung":
            y1, y2 = y
            mid = (y1 + y2) / 2
            c1, c2 = (GOLD, CORAL) if idx % 2 == 0 else (CORAL, GOLD)
            a = int(110 + 90 * (1 - abs(math.sin(k * (x - x0)))) )
            wd = max(3, int(7 * scale))
            d.line([(x, y1), (x, mid)], fill=c1 + (a,), width=wd)
            d.line([(x, mid), (x, y2)], fill=c2 + (a,), width=wd)
        else:
            r = (4 + 5 * depth) * scale
            col = tuple(int(DEEP[i] * (1 - depth) + (MINT[i] if kind == "s1" else MINT_L[i]) * depth + 40 * depth) for i in range(3))
            col = tuple(min(255, c) for c in col)
            d.ellipse([x - r, y - r, x + r, y + r], fill=col + (int(120 + 135 * depth),))
    if tilt:
        L = L.rotate(tilt, resample=Image.BICUBIC, center=(w / 2, cy))
    return glow(base, L, radius=14, strength=0.8)


def hexagon(cx, cy, s, rot=0.0):
    return [(cx + s * math.cos(math.radians(60 * i + 30) + rot), cy + s * math.sin(math.radians(60 * i + 30) + rot)) for i in range(6)]


def steroid(d, cx, cy, s, rot, col, alpha=200, width=3):
    sq = math.sqrt(3) * s
    cs, sn = math.cos(rot), math.sin(rot)

    def T(x, y):
        return (cx + x * cs - y * sn, cy + x * sn + y * cs)

    A = (0, 0)
    B = (sq, 0)
    C = (sq + sq * math.cos(math.radians(-60)), sq * math.sin(math.radians(-60)))
    rings = []
    for (hx, hy) in (A, B, C):
        rings.append([T(hx + p[0], hy + p[1]) for p in [(s * math.cos(math.radians(60 * i + 30)), s * math.sin(math.radians(60 * i + 30))) for i in range(6)]])
    ap_h, ap_p = s * math.sqrt(3) / 2, s / (2 * math.tan(math.radians(36)))
    Dc = (C[0] + ap_h + ap_p, C[1])
    R = s / (2 * math.sin(math.radians(36)))
    pent = [T(Dc[0] + R * math.cos(math.radians(144 + 72 * i)), Dc[1] + R * math.sin(math.radians(144 + 72 * i))) for i in range(5)]
    for ring in rings + [pent]:
        d.line(ring + [ring[0]], fill=col + (alpha,), width=width, joint="curve")
        for p in ring:
            d.ellipse([p[0] - width * 0.9, p[1] - width * 0.9, p[0] + width * 0.9, p[1] + width * 0.9], fill=col + (alpha,))
    # grupos funcionais
    p0 = rings[0][4]
    q = (p0[0] + s * 0.9 * math.cos(rot + 2.4), p0[1] + s * 0.9 * math.sin(rot + 2.4))
    d.line([p0, q], fill=col + (alpha,), width=width)
    d.ellipse([q[0] - width * 2.4, q[1] - width * 2.4, q[0] + width * 2.4, q[1] + width * 2.4], outline=CORAL + (240,), width=width)
    p1 = pent[2]
    q2 = (p1[0] + s * 0.8 * math.cos(rot - 0.4), p1[1] + s * 0.8 * math.sin(rot - 0.4))
    d.line([p1, q2], fill=col + (alpha,), width=width)
    d.ellipse([q2[0] - width * 2.4, q2[1] - width * 2.4, q2[0] + width * 2.4, q2[1] + width * 2.4], outline=GOLD + (240,), width=width)


def bubble(d, cx, cy, r, a=1.0):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(220, 255, 245, int(18 * a)), outline=(190, 245, 230, int(150 * a)), width=max(2, int(r * 0.05)))
    hr = r * 0.22
    hx, hy = cx - r * 0.42, cy - r * 0.42
    d.ellipse([hx - hr, hy - hr * 0.6, hx + hr, hy + hr * 0.6], fill=(255, 255, 255, int(170 * a)))


# ---------- imagens ----------
def img_bg():
    W, H = 1920, 1200
    im = radial_bg(W, H, (22, 86, 66), (4, 24, 18), 0.6, 0.4)
    im = bokeh(im, 110, 11, 14, 120, amax=26, blur=3)
    im = bokeh(im, 40, 12, 40, 160, amax=18, blur=10)
    for i, (x, y, r) in enumerate([(300, 300, 170), (1500, 800, 220), (1100, 200, 120)]):
        im = cell(im, x, y, r, 20 + i, full=True)
    save(grain(im, 3), "bg.jpg", 78)


def img_intro():
    W, H = 1500, 1000
    im = radial_bg(W, H, (42, 140, 118), (8, 52, 42), 0.55, 0.5)
    im = bokeh(im, 60, 31, 10, 80, amax=30, blur=4)
    im = cell(im, 760, 520, 330, 41)
    im = cell(im, 250, 250, 130, 42, full=False)
    im = cell(im, 1280, 190, 110, 43, full=False)
    im = cell(im, 1260, 780, 150, 44, full=False)
    im = cell(im, 240, 820, 100, 45, full=False)
    save(grain(im, 3), "intro.jpg")


def img_about():
    W, H = 1900, 710
    im = radial_bg(W, H, (30, 120, 100), (6, 40, 32), 0.5, 0.5)
    im = bokeh(im, 70, 51, 12, 90, amax=30, blur=4)
    for i, (x, y, r, full) in enumerate([(330, 360, 220, True), (900, 200, 120, False), (1250, 480, 250, True), (1680, 190, 130, False), (700, 600, 90, False)]):
        im = cell(im, x, y, r, 60 + i, full=full)
    save(grain(im, 3), "about.jpg")


def img_banner_celula():
    W, H = 1900, 710
    im = radial_bg(W, H, (36, 130, 108), (6, 42, 34), 0.5, 0.55)
    im = bokeh(im, 50, 71, 12, 80, amax=25, blur=5)
    im = cell(im, 950, 370, 330, 72)
    im = cell(im, 260, 300, 150, 73, full=False)
    im = cell(im, 1640, 400, 170, 74, full=False)
    save(grain(im, 3), "banner-celula.jpg")


def img_banner_citologia():
    """Bicamada lipídica com proteínas de canal e partículas transportadas."""
    W, H = 1900, 710
    im = radial_bg(W, H, (38, 140, 128), (6, 44, 40), 0.5, 0.5)
    im = bokeh(im, 40, 81, 14, 70, amax=22, blur=6)
    L = layer(W, H)
    d = ImageDraw.Draw(L)
    rng = random.Random(82)
    y_top, y_bot = 285, 425
    step = 38
    channels = [380, 960, 1500]
    for x in range(-20, W + 40, step):
        if any(abs(x - c) < 62 for c in channels):
            continue
        wob = 6 * math.sin(x / 90)
        for (yy, sgn) in ((y_top + wob, 1), (y_bot + wob, -1)):
            hy = yy
            d.ellipse([x - 15, hy - 15, x + 15, hy + 15], fill=GOLD + (235,), outline=(255, 235, 170, 255), width=2)
            for dx in (-7, 7):
                pts = []
                for j in range(9):
                    pts.append((x + dx + 3 * math.sin(j * 1.3 + x), hy + sgn * (15 + j * 11)))
                d.line(pts, fill=(245, 225, 190, 190), width=3, joint="curve")
    for c in channels:
        d.rounded_rectangle([c - 54, y_top - 55, c + 54, y_bot + 55], radius=40, fill=TEAL + (200,), outline=MINT_L + (255,), width=4)
        d.rounded_rectangle([c - 20, y_top - 55, c + 20, y_bot + 55], radius=16, fill=(10, 60, 52, 230))
    # partículas
    for _ in range(60):
        x, y = rng.randint(30, W - 30), rng.choice([rng.randint(40, 215), rng.randint(495, 670)])
        r = rng.randint(6, 13)
        col = rng.choice([CORAL, SKY, MINT_L])
        d.ellipse([x - r, y - r, x + r, y + r], fill=col + (230,))
    for c in channels:
        for yy in (150, 355, 560):
            d.ellipse([c - 9, yy - 9, c + 9, yy + 9], fill=CORAL + (240,))
    im = glow(im, L, radius=10, strength=0.6)
    save(grain(im, 3), "banner-citologia.jpg")


def img_banner_dna():
    W, H = 1900, 710
    im = radial_bg(W, H, (30, 118, 104), (5, 34, 30), 0.5, 0.5)
    im = bokeh(im, 60, 91, 10, 70, amax=24, blur=5)
    im = helix(im, -60, W + 60, 355, 150, 420, tilt=-4, scale=1.5)
    save(grain(im, 3), "banner-dna.jpg")


def img_banner_cont():
    """Célula em divisão (citocinese) com cromossomos e fibras do fuso."""
    W, H = 1900, 710
    im = radial_bg(W, H, (36, 128, 108), (6, 40, 34), 0.5, 0.5)
    im = bokeh(im, 50, 101, 12, 80, amax=24, blur=5)
    L = layer(W, H)
    d = ImageDraw.Draw(L)
    cx, cy, r = 950, 355, 215
    sep = 160
    c1, c2 = (cx - sep, cy), (cx + sep, cy)
    col = MINT_L + (240,)
    for ox in (6,):
        d.ellipse([c1[0] - r - ox, c1[1] - r - ox, c1[0] + r + ox, c1[1] + r + ox], fill=col)
        d.ellipse([c2[0] - r - ox, c2[1] - r - ox, c2[0] + r + ox, c2[1] + r + ox], fill=col)
        d.ellipse([cx - 95, cy - 120 - ox, cx + 95, cy + 120 + ox], fill=col)
    fillc = (30, 125, 108, 255)
    d.ellipse([c1[0] - r, c1[1] - r, c1[0] + r, c1[1] + r], fill=fillc)
    d.ellipse([c2[0] - r, c2[1] - r, c2[0] + r, c2[1] + r], fill=fillc)
    d.ellipse([cx - 100, cy - 118, cx + 100, cy + 118], fill=fillc)
    # fibras do fuso
    rng = random.Random(102)
    for sx, sgn in ((c1[0] - r * 0.8, 1), (c2[0] + r * 0.8, -1)):
        for k in range(9):
            ty = cy + (k - 4) * 14
            tx = sx + sgn * r * 1.0
            d.line([(sx, cy), (tx, ty)], fill=MINT_L + (90,), width=2)
    # cromossomos
    for (px, sgn) in ((c1[0], -1), (c2[0], 1)):
        for k in range(5):
            x = px + sgn * 55 + rng.randint(-26, 26)
            y = cy + (k - 2) * 52 + rng.randint(-10, 10)
            ang = rng.uniform(-0.8, 0.8)
            for s in (1, -1):
                ex, ey = 26 * math.cos(ang + s * 0.5), 26 * math.sin(ang + s * 0.5)
                d.line([(x - ex, y - ey), (x + ex, y + ey)], fill=CORAL + (255,), width=11)
        d.ellipse([px - 40 + sgn * 12, cy - 168, px + 40 + sgn * 12, cy - 168 + 0], fill=None)
    # organelas nas filhas
    for (px, sgn) in ((c1[0], -1), (c2[0], 1)):
        mitochondria(d, px - sgn * 110, cy + 120, 44, 19, 0.5)
        mitochondria(d, px - sgn * 95, cy - 125, 40, 17, -0.4)
        golgi(d, px - sgn * 70, cy + 20 + 0, 36, ang=1.5)
    im = glow(im, L, radius=12, strength=0.55)
    im = cell(im, 230, 190, 100, 103, full=False)
    im = cell(im, 1700, 540, 120, 104, full=False)
    save(grain(im, 3), "banner-cont.jpg")


def img_banner_sexual():
    W, H = 1900, 710
    im = radial_bg(W, H, (34, 120, 112), (6, 40, 38), 0.5, 0.5)
    im = bokeh(im, 60, 111, 10, 80, amax=22, blur=5)
    L = layer(W, H)
    d = ImageDraw.Draw(L)
    rng = random.Random(112)
    spots = [(250, 450, 54, -0.3), (740, 220, 80, 0.4), (1180, 470, 64, 2.9), (1600, 230, 70, -0.2), (950, 620, 40, 0.8), (1780, 560, 36, 1.2), (80, 150, 34, 0.2)]
    for (x, y, s, rot) in spots:
        steroid(d, x, y, s, rot, MINT_L, alpha=int(150 + s), width=max(2, int(s / 18)))
    im = glow(im, L, radius=9, strength=0.8)
    save(grain(im, 3), "banner-sexual.jpg")


def img_banner_manutencao():
    W, H = 1900, 710
    im = radial_bg(W, H, (40, 150, 150), (6, 46, 52), 0.5, 0.5)
    L = layer(W, H)
    d = ImageDraw.Draw(L)
    rng = random.Random(121)
    for _ in range(70):
        r = int(rng.choice([rng.randint(10, 30), rng.randint(30, 70), rng.randint(70, 130)]))
        x, y = rng.randint(0, W), rng.randint(0, H)
        bubble(d, x, y, r, a=rng.uniform(0.5, 1.0))
    # ondas sutis
    for k in range(6):
        pts = [(x, 560 + 22 * k + 14 * math.sin(x / 120 + k)) for x in range(0, W + 20, 20)]
        d.line(pts, fill=(200, 250, 240, 40), width=3)
    im = glow(im, L, radius=5, strength=0.5)
    save(grain(im, 3), "banner-manutencao.jpg")


def img_product(name, size, kind, seed):
    W, H = size
    if kind == "cells":
        im = radial_bg(W, H, (40, 140, 118), (6, 46, 38), 0.5, 0.5)
        im = bokeh(im, 25, seed, 8, 50, amax=24, blur=4)
        im = cell(im, W * 0.5, H * 0.5, H * 0.34, seed + 1)
        im = cell(im, W * 0.14, H * 0.2, H * 0.13, seed + 2, full=False)
        im = cell(im, W * 0.88, H * 0.8, H * 0.16, seed + 3, full=False)
    elif kind == "helix":
        im = radial_bg(W, H, (32, 122, 108), (5, 36, 30), 0.5, 0.5)
        im = bokeh(im, 25, seed, 8, 50, amax=22, blur=4)
        im = helix(im, -40, W + 40, H * 0.5, H * 0.26, W * 0.42, tilt=-8, scale=1.0)
    else:
        im = radial_bg(W, H, (36, 126, 116), (6, 40, 38), 0.5, 0.5)
        im = bokeh(im, 25, seed, 8, 50, amax=22, blur=4)
        L = layer(W, H)
        d = ImageDraw.Draw(L)
        steroid(d, W * 0.22, H * 0.55, H * 0.12, -0.2, MINT_L, 200, 3)
        steroid(d, W * 0.62, H * 0.3, H * 0.09, 0.5, MINT_L, 170, 3)
        steroid(d, W * 0.66, H * 0.78, H * 0.07, 3.0, MINT_L, 150, 3)
        im = glow(im, L, radius=7, strength=0.8)
    save(grain(im, 3), name)


def favicon():
    S = 256
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([8, 8, S - 8, S - 8], radius=58, fill=(11, 46, 34, 255))
    L = layer(S, S)
    dl = ImageDraw.Draw(L)
    pts1, pts2 = [], []
    for i in range(60):
        t = i / 59
        y = 36 + t * (S - 72)
        x = S / 2 + 62 * math.sin(t * 2 * math.pi * 1.15)
        pts1.append((x, y))
        pts2.append((S - x, y))
    for i in range(4, 58, 7):
        dl.line([pts1[i], pts2[i]], fill=GOLD + (255,), width=9)
    dl.line(pts1, fill=MINT + (255,), width=17, joint="curve")
    dl.line(pts2, fill=MINT_L + (255,), width=17, joint="curve")
    im = Image.alpha_composite(im, L)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    im.save(os.path.join(os.path.dirname(OUT), "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    print("ok favicon.ico")


if __name__ == "__main__":
    img_bg(); img_intro(); img_about()
    img_banner_celula(); img_banner_citologia(); img_banner_dna()
    img_banner_cont(); img_banner_sexual(); img_banner_manutencao()
    img_product("products-01.jpg", (900, 700), "cells", 200)
    img_product("products-02.jpg", (900, 600), "helix", 210)
    img_product("products-03.jpg", (900, 505), "mol", 220)
    favicon()

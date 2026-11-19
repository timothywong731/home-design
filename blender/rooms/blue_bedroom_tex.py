"""Textures of the blue bedroom -> blender/textures/art/blue_bedroom_*.jpg.  Run with the system Python (PIL, cv2):

    python blender/rooms/blue_bedroom_tex.py [landscape] [curtain] [duvet] [band] [flame]

Not imported by the build. `landscape` is the only reference-derived file: a rectified crop of the oil painting over
the bureau (v3 t = 254.5 s, extracted to reference/work/blue_bedroom/p254.5.jpg) with the rider and horses on the
lane painted out. The three fabrics and the flame veneer are drawn from scratch (no reference pixels): seeded, tileable.
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(REPO, 'blender', 'textures', 'art')


def save(im, name):
    p = os.path.join(OUT, f'blue_bedroom_{name}.jpg')
    im.convert('RGB').save(p, quality=90)
    print('wrote', p, im.size)


# ------------------------------------------------------------------------------------------ painting
def landscape():
    import cv2
    src = cv2.imread(os.path.join(REPO, 'reference', 'work', 'blue_bedroom', 'p254.5.jpg'))
    quad = np.float32([(401, 772), (823, 813), (808, 1147), (378, 1126)])        # canvas TL TR BR BL (1080x1920 still)
    W, H = 880, 700                                                              # canvas 0.69 x 0.55 m
    out = cv2.warpPerspective(src, cv2.getPerspectiveTransform(quad, np.float32([(0, 0), (W, 0), (W, H), (0, H)])),
                              (W, H), flags=cv2.INTER_CUBIC)
    # the rider and the horses on the lane (x 250..368, y 328..486) are painted out: lane copied over their legs,
    # a roadside bush from the right of the picture over the rest
    clean = out.copy()
    for (sx, sy, w, h), (cx, cy) in (((222, 478, 120, 56), (309, 458)), ((392, 452, 124, 104), (309, 382))):
        patch = clean[sy:sy + h, sx:sx + w]
        mask = np.zeros((h, w), np.uint8)
        cv2.ellipse(mask, (w // 2, h // 2), (w // 2 - 3, h // 2 - 3), 0, 0, 360, 255, -1)
        out = cv2.seamlessClone(patch, out, mask, (cx, cy), cv2.NORMAL_CLONE)
    out = cv2.resize(out, (1024, 815), interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite(os.path.join(OUT, 'blue_bedroom_landscape.jpg'), out, [cv2.IMWRITE_JPEG_QUALITY, 90])
    print('wrote landscape', out.shape)


# ------------------------------------------------------------------------------------------ helpers
def bez(p0, p1, p2, p3, n=24):
    return [tuple(((1 - t) ** 3) * a + 3 * ((1 - t) ** 2) * t * b + 3 * (1 - t) * t * t * c + (t ** 3) * d
                  for a, b, c, d in zip(p0, p1, p2, p3)) for t in (i / n for i in range(n + 1))]


def stroke(d, pts, w0, w1, col):
    """Polyline with a width that tapers from w0 to w1 (round joints)."""
    n = len(pts) - 1
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        w = w0 + (w1 - w0) * i / max(1, n - 1)
        d.line([a, b], fill=col, width=max(1, int(round(w))))
        d.ellipse([b[0] - w / 2, b[1] - w / 2, b[0] + w / 2, b[1] + w / 2], fill=col)


def leaf(d, x, y, ang, L, Wd, col, vein=None):
    """Lanceolate leaf from (x, y) pointing along ang."""
    c, s = math.cos(ang), math.sin(ang)
    pts = []
    for i in range(13):
        t = i / 12
        w = Wd * math.sin(math.pi * t) ** 0.8 * (1 - 0.35 * t)
        pts.append((x + c * L * t - s * w, y + s * L * t + c * w))
    for i in range(12, -1, -1):
        t = i / 12
        w = Wd * math.sin(math.pi * t) ** 0.8 * (1 - 0.35 * t)
        pts.append((x + c * L * t + s * w, y + s * L * t - c * w))
    d.polygon(pts, fill=col)
    if vein:
        d.line([(x, y), (x + c * L * 0.92, y + s * L * 0.92)], fill=vein, width=max(1, int(Wd * 0.16)))


def tiled(S, draw, bg):
    """Draw on a 3x3 canvas of SxS so that everything wraps, return the centre tile."""
    im = Image.new('RGB', (3 * S, 3 * S), bg)
    d = ImageDraw.Draw(im)
    for ox in (0, S, 2 * S):
        for oy in (0, S, 2 * S):
            draw(d, ox, oy)
    return im.crop((S, S, 2 * S, 2 * S))


# ------------------------------------------------------------------------------------------ curtain
def curtain():
    """Art-Nouveau stylised-flower repeat (Liberty 'Ianthe' type): cream / pale gold whiplash stems and fan flowers,
    slate-blue secondary leaves on a navy-black ground. One repeat = 0.21 x 0.28 m, half-drop built in."""
    S = 4                                                    # supersample
    W, H = 384 * S, 512 * S
    G, CR, GD, BL = (30, 34, 48), (218, 208, 172), (184, 170, 124), (66, 76, 104)

    def motif(d, cx, cy, s=1.0, wk=1.0):
        u = W / 384 * s
        for sg in (-1, 1):                                    # the ogee: two whiplash stems closing over the flower
            p = bez((cx + sg * 6 * u, cy + 118 * u), (cx + sg * 92 * u, cy + 70 * u),
                    (cx + sg * 96 * u, cy - 40 * u), (cx + sg * 18 * u, cy - 112 * u), 40)
            stroke(d, p, 7 * u * wk, 3 * u * wk, CR)
            p = bez((cx + sg * 30 * u, cy + 96 * u), (cx + sg * 66 * u, cy + 40 * u),
                    (cx + sg * 60 * u, cy - 20 * u), (cx + sg * 30 * u, cy - 60 * u), 30)
            stroke(d, p, 4 * u * wk, 2 * u * wk, GD)
            p = bez((cx + sg * 78 * u, cy + 8 * u), (cx + sg * 118 * u, cy - 6 * u),
                    (cx + sg * 110 * u, cy - 52 * u), (cx + sg * 84 * u, cy - 44 * u), 24)     # tendril curl
            stroke(d, p, 4 * u * wk, 1.5 * u * wk, CR)
            for k, (lx, ly, a) in enumerate(((54, 62, -0.5), (76, 18, -1.0), (70, -34, -1.7), (40, -84, -2.2))):
                leaf(d, cx + sg * lx * u, cy + ly * u, math.pi / 2 - sg * (math.pi / 2 + a) if sg > 0 else a + math.pi,
                     30 * u, 8 * u * wk, BL if k % 2 else CR, G)
        for k in range(-3, 4):                                # fan flower: seven petals from one foot
            a = -math.pi / 2 + k * 0.30
            leaf(d, cx, cy + 34 * u, a, (74 - 6 * abs(k)) * u, 9.5 * u, CR, G)
        for k in (-2.5, -1.5, -0.5, 0.5, 1.5, 2.5):
            a = -math.pi / 2 + k * 0.30
            leaf(d, cx, cy + 34 * u, a, 40 * u, 4 * u, GD)
        d.ellipse([cx - 13 * u, cy + 24 * u, cx + 13 * u, cy + 50 * u], fill=GD, outline=G, width=int(2 * u))
        d.ellipse([cx - 6 * u, cy + 31 * u, cx + 6 * u, cy + 43 * u], fill=G)
        stroke(d, [(cx, cy + 50 * u), (cx, cy + 122 * u)], 6 * u, 4 * u, CR)                   # stalk
        for sg in (-1, 1):
            leaf(d, cx, cy + 96 * u, math.pi / 2 + sg * 1.1, 34 * u, 8 * u, BL, G)
        for sg in (-1, 1):                                    # small buds between the ogees
            bx, by = cx + sg * 0.5 * W, cy - 6 * u
            for k in (-1, 0, 1):
                leaf(d, bx, by + 20 * u, -math.pi / 2 + k * 0.42, 34 * u, 6.5 * u, CR if k else GD, G)

    im = Image.new('RGB', (3 * W, 3 * H), G)
    d = ImageDraw.Draw(im)
    for i in range(-1, 5):                                    # small infill motifs first: the ground in the footage is
        for j in range(-1, 5):                                # only about half navy (v3 f_0343, f_0347)
            motif(d, i * W + 3 * W / 4, j * H + H / 4 + 0.06 * H, 0.95, 1.5)
            motif(d, i * W + W / 4, j * H + 3 * H / 4 + 0.06 * H, 0.95, 1.5)
    for i in range(-1, 5):
        for j in range(-1, 5):
            motif(d, i * W + W / 4, j * H + H / 4, 1.62, 1.6)
            motif(d, i * W + 3 * W / 4, j * H + 3 * H / 4, 1.62, 1.6)    # half drop
    im = im.crop((W, H, 2 * W, 2 * H)).resize((384, 512), Image.LANCZOS)
    save(im, 'curtain')


# ------------------------------------------------------------------------------------------ duvet
def duvet():
    """Pale cream-lilac bamboo leaves and small sprays scattered on dark navy. One repeat = 0.9 x 0.9 m."""
    S, R = 2048, random.Random(7)
    G, LF, L2 = (42, 43, 58), (201, 195, 207), (150, 146, 166)
    sprays = []
    for _ in range(36):
        x, y, a = R.uniform(0, S), R.uniform(0, S), R.uniform(0, 2 * math.pi)
        sprays.append((x, y, a, R.uniform(0.75, 1.25), R.random() < 0.22))

    def draw(d, ox, oy):
        r = random.Random(11)
        for x, y, a, s, small in sprays:
            x, y = x + ox, y + oy
            if small:                                         # spray of small dots / florets
                p = bez((x, y), (x + 60 * math.cos(a), y + 60 * math.sin(a)),
                        (x + 120 * math.cos(a + 0.4), y + 120 * math.sin(a + 0.4)),
                        (x + 170 * math.cos(a + 0.2), y + 170 * math.sin(a + 0.2)), 12)
                stroke(d, p, 3, 2, L2)
                for (px, py) in p[2::2]:
                    for k in (-1, 1):
                        qx, qy = px + k * 22 * math.cos(a + 1.3), py + k * 22 * math.sin(a + 1.3)
                        d.line([(px, py), (qx, qy)], fill=L2, width=2)
                        d.ellipse([qx - 6, qy - 6, qx + 6, qy + 6], fill=LF)
                continue
            L = 300 * s
            p = bez((x, y), (x + 0.35 * L * math.cos(a), y + 0.35 * L * math.sin(a)),
                    (x + 0.7 * L * math.cos(a + 0.25), y + 0.7 * L * math.sin(a + 0.25)),
                    (x + L * math.cos(a + 0.15), y + L * math.sin(a + 0.15)), 16)
            stroke(d, p, 4, 2, L2)
            for i in (3, 6, 9, 12, 15):
                px, py = p[i]
                for k in (-1, 1):
                    if r.random() < 0.2:
                        continue
                    la = a + 0.2 + k * r.uniform(0.45, 0.85)
                    leaf(d, px, py, la, r.uniform(120, 200) * s, r.uniform(15, 22) * s, LF if r.random() < 0.8 else L2, G)
            leaf(d, p[-1][0], p[-1][1], a + 0.15, 170 * s, 18 * s, LF, G)

    im = tiled(S, draw, G).filter(ImageFilter.GaussianBlur(0.8)).resize((1024, 1024), Image.LANCZOS)
    save(im, 'duvet')


# ------------------------------------------------------------------------------------------ flower band
def band():
    """Chrysanthemum clusters on charcoal (v3 f_0231, f_0235, f_0471): each cluster is two or three large orange /
    ochre heads of rounded petals with a small cream eye, set in a mass of small cream blossoms and ringed by a fan
    of pointed pale-sage leaves; the 0.5 m band across the foot of the duvet. 1.0 x 0.5 m, tiles along its length
    only (the long edges fade to the duvet's navy)."""
    Wd, H = 2048, 1024
    G, CR, CS, LF, LD = (34, 34, 38), (236, 232, 214), (178, 176, 188), (226, 228, 210), (196, 202, 182)
    OR, O2, OL = (210, 132, 28), (222, 152, 42), (240, 226, 196)        # ochre-orange: renders like f_0231
    clusters = [(520, 520, 400, 0.2), (1540, 500, 380, 2.1)]       # x, y, outer radius (px, 2048 px/m), turn

    def head(d, x, y, r, rr):
        """Orange head: outer ring of rounded petals, inner ring, small cream eye (orange ~70 % of the head)."""
        for ring, (n, rc, rp, col) in enumerate(((9, 0.64, 0.36, OR), (7, 0.34, 0.27, O2))):
            for k in range(n):
                a = 2 * math.pi * (k + 0.5 * ring) / n + rr.uniform(-0.08, 0.08)
                cx, cy = x + r * rc * math.cos(a), y + r * rc * math.sin(a)
                d.ellipse([cx - r * rp, cy - r * rp, cx + r * rp, cy + r * rp], fill=col, outline=OL, width=max(2, int(r * 0.03)))
        d.ellipse([x - r * 0.14, y - r * 0.14, x + r * 0.14, y + r * 0.14], fill=OL)
        for k in range(8):                                    # dotted stamens round the eye
            a = 2 * math.pi * k / 8
            px, py = x + r * 0.1 * math.cos(a), y + r * 0.1 * math.sin(a)
            d.ellipse([px - r * 0.02, py - r * 0.02, px + r * 0.02, py + r * 0.02], fill=O2)

    def blossom(d, x, y, r):
        for k in range(10):
            leaf(d, x, y, 2 * math.pi * k / 10, r, r * 0.32, CR, CS)
        d.ellipse([x - r * 0.18, y - r * 0.18, x + r * 0.18, y + r * 0.18], fill=CS)

    def draw(d, ox, oy):
        rr = random.Random(5)
        for x, y, R, turn in clusters:
            x, y = x + ox, y + oy
            for k in range(30):                               # fan of pointed leaves round the cluster
                a = turn + 2 * math.pi * k / 30 + rr.uniform(-0.06, 0.06)
                L = R * rr.uniform(0.45, 0.6)
                leaf(d, x + 0.42 * R * math.cos(a), y + 0.42 * R * math.sin(a), a, L, R * 0.075, LF if k % 3 else LD, LD)
            for k in range(11):                               # mass of small cream blossoms
                a, q = turn + 2 * math.pi * k / 11 + rr.uniform(-0.15, 0.15), rr.uniform(0.42, 0.58)
                blossom(d, x + q * R * math.cos(a), y + q * R * math.sin(a), R * rr.uniform(0.15, 0.2))
            for dx, dy, s in ((-0.22, 0.08, 0.33), (0.2, -0.12, 0.31), (0.05, 0.28, 0.26)):
                c, sn = math.cos(turn), math.sin(turn)
                head(d, x + R * (dx * c - dy * sn), y + R * (dx * sn + dy * c), R * s, rr)
        for x0 in (1030, 2060):                               # loose leaf sprays between the clusters
            for k, (a, L) in enumerate(((-1.2, 210), (-0.4, 240), (0.5, 220), (1.4, 190), (2.4, 230), (3.4, 200))):
                leaf(d, x0 + ox, 510 + oy + 30 * (k % 2), a, L, 20, LF if k % 2 else LD, LD)

    im = Image.new('RGB', (3 * Wd, H), G)
    d = ImageDraw.Draw(im)
    for ox in (0, Wd, 2 * Wd):
        draw(d, ox, 0)
    im = im.crop((Wd, 0, 2 * Wd, H)).filter(ImageFilter.GaussianBlur(1.0)).resize((1024, 512), Image.LANCZOS)
    a = np.asarray(im).astype(np.float32)                     # fade the long edges into the duvet ground
    f = np.clip(np.minimum(np.arange(512), 511 - np.arange(512)) / 28.0, 0, 1)[:, None, None]
    a = a * f + np.float32((42, 43, 58)) * (1 - f)
    save(Image.fromarray(a.astype(np.uint8)), 'band')


# ------------------------------------------------------------------------------------------ flame mahogany
def flame():
    """Flame-figured (crotch) mahogany veneer for one cabinet door panel, 0.185 x 0.44 m, filling the image once:
    light and dark chevrons rising from a crotch at the bottom centre (v3 f_0353, f_0437). Drawn from scratch."""
    W, H, rs = 432, 1024, np.random.RandomState(4)

    def noise(n):                                     # smooth value noise, n x n cells
        g = Image.fromarray((rs.rand(n, n) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
        return np.asarray(g, np.float32) / 255.0 - 0.5

    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    xn, yn = (x - W / 2) / (W / 2), 1.0 - y / H               # -1..1 across, 0 at the bottom
    f = yn * 1.15 - 0.85 * np.abs(xn) ** 1.4 + 0.10 * noise(5) + 0.025 * noise(24)
    band = np.sin(2 * np.pi * (f * 7.5 + 0.6 * noise(8)))
    fine = np.sin(2 * np.pi * (f * 46 + 2.0 * noise(12))) * 0.25 + noise(64) * 0.3
    t = np.clip(0.5 + 0.38 * band + 0.18 * fine, 0, 1)
    t *= 1.0 - 0.35 * np.abs(xn) ** 2                         # the flame is brightest up the middle
    t *= 1.0 - 0.45 * np.exp(-((xn / 0.05) ** 2)) * np.clip(1.4 - yn * 2.2, 0, 1)   # dark crotch line at the foot
    dark, light = np.float32((50, 24, 14)), np.float32((150, 86, 52))
    a = dark + (light - dark) * t[..., None]
    save(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6)), 'flame')


if __name__ == '__main__':
    todo = sys.argv[1:] or ['landscape', 'curtain', 'duvet', 'band', 'flame']
    for t in todo:
        {'landscape': landscape, 'curtain': curtain, 'duvet': duvet, 'band': band, 'flame': flame}[t]()
    print('TEX OK')

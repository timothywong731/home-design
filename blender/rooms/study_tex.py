"""Generated fabric map for the Rose Room (study) curtains - no reference pixels: drawn from the colour and the
description of the floor2_b survey (round 3, 1.1: pale silver-grey jacquard #CECDC7 with a large tone-on-tone leaf /
flower relief; v13 t152, t193.4). Plain Python + PIL:

    python blender/rooms/study_tex.py        -> blender/textures/art/study_curtain.jpg

curtain  woven silver-grey ground, a half-drop damask of stylised flowers on scrolling leafy stems with acanthus fronds and
         sprigs in a paler raised weave with a faint shadow edge (the relief reads by its shading), repeat 0.64 m
"""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'textures', 'art'))
SS = 2                                             # supersampling


def _rot(pts, a, cx, cy):
    c, s = math.cos(a), math.sin(a)
    return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts]


def _wrap_poly(draw, size, pts, **kw):             # tileable: draw at the 9 wrapped offsets
    for ox in (-size, 0, size):
        for oy in (-size, 0, size):
            draw.polygon([(x + ox, y + oy) for x, y in pts], **kw)


def _wrap_line(draw, size, pts, fill, width):
    for ox in (-size, 0, size):
        for oy in (-size, 0, size):
            draw.line([(x + ox, y + oy) for x, y in pts], fill=fill, width=width, joint='curve')


def _leaf(L, W, n=12, tip=1.5):
    """Lanceolate outline, stem at the origin, tip at -y (up in image space)."""
    half = [(W / 2 * math.sin(math.pi * (i / n) ** (1 / tip)) ** 0.85, -L * i / n) for i in range(n + 1)]
    return half + [(-x, y) for x, y in reversed(half)]


def _flower(d, S, cx, cy, r, col, shade, rnd):
    """Stylised Jacobean bloom: fan of rounded petals over a cup, seen from the side."""
    for k in range(7):                                             # fan of petals, upward
        a = math.radians(-90 + (k - 3) * 24 + rnd.uniform(-4, 4))
        L = r * (1.0 - 0.12 * abs(k - 3))
        pts = _rot(_leaf(L, L * 0.55, tip=0.9), a + math.pi / 2, cx, cy)
        _wrap_poly(d, S, [(x + SS * 2, y + SS * 2) for x, y in pts], fill=shade)
        _wrap_poly(d, S, pts, fill=col)
    cup = [(cx + r * 0.55 * math.cos(t), cy + r * 0.35 * math.sin(t)) for t in [math.pi * i / 12 for i in range(13)]]
    _wrap_poly(d, S, [(x + SS * 2, y + SS * 2) for x, y in cup], fill=shade)
    _wrap_poly(d, S, cup, fill=col)
    for k in range(5):                                             # stamen dots
        a = math.radians(-90 + (k - 2) * 22)
        x, y = cx + r * 0.75 * math.cos(a), cy + r * 0.75 * math.sin(a)
        rr = r * 0.06
        _wrap_poly(d, S, [(x + rr * math.cos(t), y + rr * math.sin(t)) for t in [math.tau * i / 8 for i in range(8)]],
                   fill=shade)


def curtain(px=1024):
    S = px * SS
    rnd = random.Random(23)
    ground, grain = '#C7C6C0', ['#C2C1BB', '#CCCBC5', '#C4C3BD']
    raised, shade = '#D9D8D2', '#B8B7B1'
    im = Image.new('RGB', (S, S), ground)
    d = ImageDraw.Draw(im)
    for _ in range(26000):                                         # woven slub, mostly horizontal weft
        x, y = rnd.randrange(S), rnd.randrange(S)
        d.line([(x, y), (x + rnd.randrange(6, 36), y)], fill=rnd.choice(grain), width=SS)
    # half-drop repeat: four motif centres per tile, each a bloom on a scrolling leafy stem, then a dense leaf fill
    cells = [((0.25, 0.22), 1), ((0.75, 0.47), -1), ((0.25, 0.72), -1), ((0.75, 0.97), 1)]
    for (u, v), flip in cells:
        cx, cy = u * S, v * S
        stem = [(cx + flip * S * 0.07 * math.sin(math.pi * t * 1.6), cy + S * (0.04 + 0.22 * t)) for t in
                [i / 16 for i in range(17)]]
        _wrap_line(d, S, [(x + SS * 2, y + SS * 2) for x, y in stem], shade, SS * 6)
        _wrap_line(d, S, stem, raised, SS * 5)
        for j, t in enumerate((0.15, 0.35, 0.55, 0.75, 0.95)):    # paired leaves along the stem
            x, y = stem[min(16, int(t * 16))]
            for sg in (-1, 1):
                L = S * rnd.uniform(0.07, 0.10)
                a = math.radians(sg * rnd.uniform(50, 75) + flip * 10)
                pts = _rot(_leaf(L, L * 0.45), a, x, y)
                _wrap_poly(d, S, [(px_ + SS * 2, py_ + SS * 2) for px_, py_ in pts], fill=shade)
                _wrap_poly(d, S, pts, fill=raised)
                _wrap_line(d, S, _rot([(0, 0), (0, -L * 0.9)], a, x, y), ground, SS * 2)   # midrib groove
        _flower(d, S, cx, cy, S * 0.09, raised, shade, rnd)
        for k in range(2):                                         # scrolling acanthus fronds beside the bloom
            sg = 1 if k else -1
            fr = [(cx + sg * S * (0.05 + 0.10 * t), cy - S * 0.02 + S * 0.08 * math.sin(math.pi * t)) for t in
                  [i / 10 for i in range(11)]]
            _wrap_line(d, S, fr, raised, SS * 4)
            for i in range(2, 11, 2):
                x, y = fr[i]
                pts = _rot(_leaf(S * 0.035, S * 0.018), math.radians(sg * 40 + 180 * (i % 4 == 0)), x, y)
                _wrap_poly(d, S, pts, fill=raised)
    for _ in range(90):                                            # small sprigs filling the ground
        x, y = rnd.uniform(0, S), rnd.uniform(0, S)
        L = S * rnd.uniform(0.025, 0.04)
        a = rnd.uniform(0, math.tau)
        _wrap_poly(d, S, _rot(_leaf(L, L * 0.45), a, x, y), fill=raised)
    im = im.filter(ImageFilter.GaussianBlur(SS * 0.7))
    im = im.resize((px, px), Image.LANCZOS)
    os.makedirs(OUT, exist_ok=True)
    im.save(os.path.join(OUT, 'study_curtain.jpg'), quality=90)
    print('wrote study_curtain.jpg', im.size)


if __name__ == '__main__':
    curtain()

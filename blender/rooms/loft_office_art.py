"""Textures for the loft office -> blender/textures/art/loft_office_<name>.jpg

Synthetic (no reference pixels): union (Union flag, 3:5, drawn landscape), ensign (plain blue ensign, 3 x 2 ft hung
portrait, no badge), periodic (colour-block periodic table grid, no text), stripe (the piano stool's cream / mauve
striped cover, one 0.12 m repeat), weave (seagrass basket weave of the plant pot, one 0.06 m repeat).
Rectified crops of the owner's footage (art only, no people, no writing): carving (hardwood relief of a bird
among flowers, v5 still 172), cat1 / cat2 (two cat paintings leaning against the TV wall, v5 still 344).

Run with the system Python (numpy, Pillow, OpenCV):   python blender/rooms/loft_office_art.py [name ...]
(names: only those files are written; default all)
"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'blender' / 'textures' / 'art'
REF = ROOT / 'reference' / 'work' / 'p2_second_front'
RED, BLUE, WHITE = (180, 38, 43), (35, 43, 92), (237, 235, 228)


def union(w=1000, h=600):
    """Union flag, 3:5. Units of h/30: saltire 6 white with a 2 red pinwheel stripe, cross 10 white / 6 red."""
    S = 4                                                  # supersampling
    im = Image.new('RGB', (w * S, h * S), BLUE)
    d = ImageDraw.Draw(im)
    u, c = h * S / 30, np.array((w * S / 2, h * S / 2))
    for corner in ((0, 0), (w * S, 0), (w * S, h * S), (0, h * S)):
        e = np.array(corner, float)
        t = (e - c) / np.linalg.norm(e - c)
        n = np.array((-t[1], t[0]))
        far = e + t * 20 * u
        d.polygon([tuple(c + n * 3 * u), tuple(far + n * 3 * u), tuple(far - n * 3 * u), tuple(c - n * 3 * u)], fill=WHITE)
        d.polygon([tuple(c), tuple(far), tuple(far + n * 2 * u), tuple(c + n * 2 * u)], fill=RED)   # counterchanged
    for half, col in ((5, WHITE), (3, RED)):
        d.rectangle([c[0] - half * u, 0, c[0] + half * u, h * S], fill=col)
        d.rectangle([0, c[1] - half * u, w * S, c[1] + half * u], fill=col)
    return im.resize((w, h), Image.LANCZOS)


def ensign(w=600, h=900):
    """3 x 2 ft, hung vertically: the union stands upright over the top half of the hoist (north) side, as filmed
    (hr_346, v12 f43-44)."""
    im = Image.new('RGB', (w, h), (35, 43, 92))
    im.paste(union(h // 2, w // 2).rotate(90, expand=True), (w - w // 2, 0))
    return im


def stripe(w=512, h=512):
    """Piano-stool cover (hr_183, hr_235): cream ground with broad mauve-grey bands edged by thin plum and grey lines;
    the bands run along V (the stool's length). One repeat = 0.12 m across."""
    im = Image.new('RGB', (w, h), (230, 224, 214))
    d = ImageDraw.Draw(im)
    u = w / 120.0                                          # pixels per mm
    for x0, x1, c in ((0, 26, (164, 140, 150)), (26, 30, (230, 224, 214)), (30, 33, (120, 92, 108)),
                      (52, 56, (150, 146, 150)), (60, 86, (176, 154, 162)), (86, 89, (120, 92, 108)),
                      (104, 108, (150, 146, 150))):
        d.rectangle([int(x0 * u), 0, int(x1 * u) - 1, h], fill=c)
    a = np.asarray(im).astype(np.float32)
    rng = np.random.default_rng(7)
    a *= 1 + 0.035 * rng.standard_normal((h, 1, 1)).repeat(w, 1)    # weft texture across the bands
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def weave(w=256, h=256):
    """Seagrass basket (hr_183): twisted rush rows passing over and under upright stakes, golden straw; 8 rows of
    7.5 mm and 6 stakes per 0.06 m repeat."""
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    r = y / (h / 8)
    row, k = r % 1.0, np.floor(r)
    col = (x / (w / 6) + 0.5 * (k % 2)) % 1.0
    over = np.abs(col - 0.5) * 2                           # 0 where the rush passes over a stake, 1 between stakes
    v = 0.62 + 0.38 * np.sin(np.pi * row) ** 0.6 * (1.0 - 0.45 * over ** 2)
    v += 0.06 * np.sin(2 * np.pi * (x / 9.0 + y / 23.0))   # twist of the rush
    v -= 0.30 * (row < 0.07)                               # dark gaps between the rows
    base = np.array((182, 156, 106), np.float32)
    a = np.clip(base[None, None, :] * v[..., None], 0, 255).astype(np.uint8)
    return Image.fromarray(a)


def periodic(w=900, h=620):
    """White sheet, blank title band, 18 x 7 main block + two f-block rows of flat coloured cells."""
    im = Image.new('RGB', (w, h), (246, 245, 240))
    d = ImageDraw.Draw(im)
    d.rectangle([150, 22, 600, 40], fill=(205, 205, 200))  # title band: a plain grey bar, no lettering
    cols = dict(a=(240, 214, 110), e=(244, 170, 120), t=(232, 98, 128), p=(170, 205, 150), n=(150, 215, 170),
                h=(246, 232, 140), g=(196, 170, 220), f=(226, 170, 214))
    rows = ['a................g', 'ae..........pnnnhg', 'ae..........ppnnhg', 'aettttttttttpppnhg',
            'aettttttttttppppng', 'aettttttttttppppng', 'aettttttttttppppng']
    cw, ch, x0, y0 = 46, 56, 36, 70
    for r, row in enumerate(rows + ['', '..ffffffffffffff', '..ffffffffffffff']):
        for c, k in enumerate(row):
            if k != '.':
                y = y0 + r * ch - (ch // 2 if r > 7 else 0)
                d.rectangle([x0 + c * cw + 2, y + 2, x0 + (c + 1) * cw - 2, y + ch - 2], fill=cols[k], outline=(120, 120, 120))
    return im


def crop(still, quad, size):
    """Perspective-rectify quad (TL, TR, BR, BL in the 1080 x 1920 still) to size (w, h)."""
    src = cv2.imread(str(REF / still))
    w, h = size
    m = cv2.getPerspectiveTransform(np.float32(quad), np.float32([(0, 0), (w, 0), (w, h), (0, h)]))
    out = cv2.warpPerspective(src, m, size, flags=cv2.INTER_CUBIC)
    return Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))


if __name__ == '__main__':
    import sys
    want = set(sys.argv[1:])
    made = dict(union=union(), ensign=ensign(), periodic=periodic(), stripe=stripe(), weave=weave())
    if REF.exists() and (not want or want & {'carving', 'cat1', 'cat2'}):                                       # the footage is private: crops only where it is present
        made['carving'] = crop('hr_172.jpg', [(233.5, 746), (344, 812.5), (334, 1104), (200, 1065)], (256, 512))
        made['cat1'] = crop('hr_344.jpg', [(550, 1201.7), (626.7, 1178.3), (638.3, 1281.7), (563.3, 1310)], (288, 384))
        made['cat2'] = crop('hr_344.jpg', [(671.7, 1156.7), (740.7, 1138.3), (755, 1238.3), (685, 1260)], (288, 384))
    for name, im in made.items():
        if want and name not in want:
            continue
        im.save(OUT / f'loft_office_{name}.jpg', quality=90)
        print('wrote', OUT / f'loft_office_{name}.jpg', im.size)

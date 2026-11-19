"""Generated fabric / veneer maps for the green bedroom (no reference pixels: drawn from the colours and the
description in spec/rooms/green_bedroom.md section 6 / 7). Plain Python + PIL:

    python blender/rooms/green_bedroom_tex.py        -> blender/textures/art/green_bedroom_*.jpg

curtain  cream jacquard with large upright feather leaves, repeat 1.5 m
duvet    charcoal ground, large botanical leaves and pale flowers, repeat 1.0 m
tapestry cream ground with brown / olive flowers, leaves and urns (armchair, corner chair), repeat 0.45 m
sheet    sage fitted cover with a cream fleck, repeat 0.40 m
inlay    one nightstand drawer front: chevron kingwood with a pale floral spray (fills the front once)
marble   cream / beige breccia (nightstand tops), repeat 0.30 m
needlepoint  footstool top: sage needlepoint with a centre bouquet (fills the pad once)
(python blender/rooms/green_bedroom_tex.py curtain marble  -> only those)
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


def _wrap(draw, size, pts, **kw):                  # tileable: draw at the 9 wrapped offsets
    for ox in (-size, 0, size):
        for oy in (-size, 0, size):
            draw.polygon([(x + ox, y + oy) for x, y in pts], **kw)


def _wline(draw, size, pts, fill, width):
    for ox in (-size, 0, size):
        for oy in (-size, 0, size):
            draw.line([(x + ox, y + oy) for x, y in pts], fill=fill, width=width, joint='curve')


def _leaf(L, W, n=14, tip=1.6):
    """Lanceolate outline, stem at the origin, tip at -y (up in image space)."""
    half = [(W / 2 * math.sin(math.pi * (i / n) ** (1 / tip)) ** 0.9, -L * i / n) for i in range(n + 1)]
    return half + [(-x, y) for x, y in reversed(half)]


def _save(im, name, size):
    im = im.resize((size, size) if isinstance(size, int) else size, Image.LANCZOS)
    os.makedirs(OUT, exist_ok=True)
    im.save(os.path.join(OUT, name), quality=90)
    print('wrote', name, im.size)


def _veined(d, S, L, W, a, x, y, col, vein, tip=1.6):
    _wrap(d, S, _rot(_leaf(L, W, tip=tip), a, x, y), fill=col)
    _wline(d, S, _rot([(0, 0), (0, -L * 0.97)], a, x, y), vein, max(2, int(L / 150)) * SS // 2 + 1)
    for j in range(3, 26):                         # herringbone side veins
        t = j / 27
        w = W / 2 * math.sin(math.pi * t ** (1 / tip)) ** 0.9 * 0.92
        for sg in (-1, 1):
            _wline(d, S, _rot([(0, -L * t), (sg * w, -L * (t + 0.07))], a, x, y), vein, SS)


def _shade(hx, k):
    """hx lightened (k > 0) toward white or darkened (k < 0) toward black."""
    r, g, b = (int(hx[i:i + 2], 16) for i in (1, 3, 5))
    f = (lambda c: c + (255 - c) * k) if k > 0 else (lambda c: c * (1 + k))
    return '#%02X%02X%02X' % tuple(int(max(0, min(255, f(c)))) for c in (r, g, b))


def _feather(d, S, L, W, a, x, y, col, bend=0.0, n=16):
    """Upright feather leaf, stem at (x, y), tip up: barbed (serrated) edges whose teeth point to the tip, one half
    a shade lighter than the other, pale midrib and herringbone side veins."""
    wid = lambda t: W / 2 * math.sin(math.pi * min(1.0, t) ** (1 / 1.5)) ** 0.9
    mid = lambda t: (bend * L * t * t, -L * t)
    half = []
    for i in range(n):
        t0 = i / n
        mx, my = mid(t0)
        half.append((mx + wid(t0) * 0.82, my))
        mx, my = mid(t0 + 0.75 / n)
        half.append((mx + wid(t0 + 0.45 / n) * 1.02, my))
    tip = mid(1.0)
    left = [(2 * mid(-y_ / L)[0] - x_, y_) for x_, y_ in half]           # mirror about the (bent) midrib
    rib = [mid(j / 12) for j in range(13)]
    _wrap(d, S, _rot([(0, 0)] + half + [tip] + left[::-1], a, x, y), fill=col)
    _wrap(d, S, _rot(rib + half[::-1], a, x, y), fill=_shade(col, 0.16))  # lighter right half
    light = sum(int(col[i:i + 2], 16) for i in (1, 3, 5)) > 420
    vein = _shade(col, -0.28) if light else _shade(col, 0.42)
    _wline(d, S, _rot(rib[:-1], a, x, y), _shade(col, 0.5), max(SS, int(W / 40)))
    for j in range(2, 23):                         # herringbone side veins, rising toward the tip
        t = j / 24
        mx, my = mid(t)
        for sg in (-1, 1):
            ex, ey = mid(t + 0.07)
            _wline(d, S, _rot([(mx, my), (ex + sg * wid(t + 0.05) * 0.8, ey)], a, x, y), vein, SS)


def curtain(px=1024):
    """Woven jacquard (repeat 1.5 m, leaves 0.40-0.55 m long): large overlapping upright feather leaves in grey-green,
    sage and olive on a warm cream ground, slender olive fronds between them (v3 f_0636 / f_0690 / f_0700, v4 f_0005)."""
    S = px * SS
    rnd = random.Random(7)
    im = Image.new('RGB', (S, S), '#E5E2D4')
    d = ImageDraw.Draw(im)
    for _ in range(12000):                         # woven slub
        x, y = rnd.randrange(S), rnd.randrange(S)
        d.line([(x, y), (x + rnd.randrange(6, 40), y)], fill=rnd.choice(['#DCD9CA', '#ECE9DD', '#E0DDCF']), width=SS)
    for _ in range(22):                            # slender fronds in the gaps, behind the leaves
        x, y, a = rnd.uniform(0, S), rnd.uniform(0, S), math.radians(rnd.uniform(-25, 25))
        L, bend = S * rnd.uniform(0.16, 0.26), rnd.uniform(-0.25, 0.25)
        pts = [(bend * L * (j / 10) ** 2, -L * j / 10) for j in range(11)]
        col = rnd.choice(['#9AA57E', '#8E9872', '#A9AF8C'])
        _wline(d, S, _rot(pts, a, x, y), col, SS * 2)
        for j in range(3, 10, 2):
            for sg in (-1, 1):
                px_, py_ = _rot([pts[j]], a, x, y)[0]
                _wrap(d, S, _rot(_leaf(L * 0.20, L * 0.035, 6), a + sg * 0.45, px_, py_), fill=col)
    grey, dark = ['#6F756B', '#7E8279'], ['#5E6B50', '#57604B', '#626A56']
    sage, olive = ['#7C8B63', '#74805E'], ['#9AA57E', '#A3AA88']
    nc, nr = 7, 3
    for layer, pal in ((0, olive + grey), (1, sage + olive + grey), (2, dark + sage)):   # paler leaves behind
        for c in range(nc):
            for r in range(nr):
                x = (c + 0.37 * layer + 0.5) * S / nc + rnd.uniform(-0.03, 0.03) * S
                y = (r + (0.5 if c % 2 else 0.0) + 0.33 * layer + 0.9) * S / nr + rnd.uniform(-0.03, 0.03) * S
                L = S * rnd.uniform(0.27, 0.36)
                _feather(d, S, L, L * rnd.uniform(0.22, 0.27), math.radians(rnd.uniform(-14, 14)), x, y, rnd.choice(pal),
                         bend=rnd.uniform(-0.12, 0.12))
    _save(im.filter(ImageFilter.GaussianBlur(SS * 0.6)), 'green_bedroom_curtain.jpg', px)


def marble(px=512):
    """Cream / beige breccia for the nightstand tops: angular clasts in buff and honey with brown veins."""
    S = px * SS
    rnd = random.Random(13)
    im = Image.new('RGB', (S, S), '#E4D8BE')
    d = ImageDraw.Draw(im)
    for _ in range(70):                            # clasts
        x, y, r = rnd.uniform(0, S), rnd.uniform(0, S), S * rnd.uniform(0.03, 0.11)
        n = rnd.randrange(5, 8)
        pts = [(x + r * rnd.uniform(0.6, 1.0) * math.cos(2 * math.pi * i / n), y + r * rnd.uniform(0.6, 1.0) * math.sin(2 * math.pi * i / n))
               for i in range(n)]
        _wrap(d, S, pts, fill=rnd.choice(['#E9DFC8', '#DCCBA8', '#E0D2B2', '#D2BE98', '#EDE5D2']))
    for _ in range(26):                            # veins
        x, y, a = rnd.uniform(0, S), rnd.uniform(0, S), rnd.uniform(0, math.tau)
        pts = []
        for j in range(12):
            a += rnd.uniform(-0.5, 0.5)
            x, y = x + S * 0.03 * math.cos(a), y + S * 0.03 * math.sin(a)
            pts.append((x, y))
        _wline(d, S, pts, rnd.choice(['#B9A27C', '#A68A62', '#C4AE8A']), SS * rnd.choice([1, 2, 3]))
    _save(im.filter(ImageFilter.GaussianBlur(SS * 0.7)), 'green_bedroom_marble.jpg', px)


def needlepoint(px=512):
    """Footstool top, fills the pad once: sage-green needlepoint, centre bouquet of white and pink flowers."""
    S = px * SS
    rnd = random.Random(17)
    im = Image.new('RGB', (S, S), '#8FA07A')
    d = ImageDraw.Draw(im)
    st = 6 * SS                                    # stitch grid
    for i in range(0, S, st):
        for j in range(0, S, st):
            d.rectangle([i, j, i + st - SS, j + st - SS], fill=rnd.choice(['#8FA07A', '#8A9B75', '#94A580', '#879871']))
    c = S / 2
    for k in range(14):                            # leaves round the bouquet
        a = 2 * math.pi * k / 14 + rnd.uniform(-0.2, 0.2)
        d.polygon(_rot(_leaf(S * rnd.uniform(0.24, 0.32), S * 0.07, 8), a, c, c), fill=rnd.choice(['#4E6B3E', '#5D7A48', '#3F5A34']))
    for k in range(9):                             # flower heads
        a, rr = 2 * math.pi * k / 8 + rnd.uniform(-0.3, 0.3), S * (0.0 if k == 0 else rnd.uniform(0.13, 0.2))
        x, y, r = c + rr * math.cos(a), c + rr * math.sin(a), S * rnd.uniform(0.07, 0.095)
        col = rnd.choice(['#F2EFE6', '#F2EFE6', '#E8C9CC', '#F0E2C8'])
        for j in range(5):
            d.polygon(_rot(_leaf(r, r * 0.95, 8, 0.8), j * math.tau / 5 + a, x, y), fill=col, outline='#B8A9A0')
        d.ellipse([x - r * 0.25, y - r * 0.25, x + r * 0.25, y + r * 0.25], fill='#D9B04A')
    _save(im.filter(ImageFilter.GaussianBlur(SS * 0.6)), 'green_bedroom_needlepoint.jpg', px)


def duvet(px=1024):
    S = px * SS
    rnd = random.Random(11)
    im = Image.new('RGB', (S, S), '#2B2630')
    d = ImageDraw.Draw(im)
    greens = ['#5F8E7A', '#557D6E', '#7FA596', '#3F5E55', '#8FA8A0', '#4A6F62']
    for i in range(11):                            # palm fronds: a curved stem with paired leaflets
        x, y, a0 = rnd.uniform(0, S), rnd.uniform(0, S), rnd.uniform(0, math.tau)
        col, n, L = rnd.choice(greens), rnd.randrange(9, 14), S * rnd.uniform(0.22, 0.34)
        bend = rnd.uniform(-0.5, 0.5)
        pts = []
        for j in range(n + 1):
            t = j / n
            a = a0 + bend * t
            pts.append((x + L * t * math.sin(a), y - L * t * math.cos(a), a))
        _wline(d, S, [(q[0], q[1]) for q in pts], col, 2 * SS)
        for j in range(1, n + 1):
            px_, py_, a = pts[j]
            ll = L * 0.36 * (1 - 0.6 * j / n)
            for sg in (-1, 1):
                _wrap(d, S, _rot(_leaf(ll, ll * 0.22, 8, 1.2), a + sg * math.radians(62), px_, py_), fill=col)
    for i in range(9):                             # broad veined leaves
        x, y, a = rnd.uniform(0, S), rnd.uniform(0, S), rnd.uniform(0, math.tau)
        L = S * rnd.uniform(0.16, 0.24)
        _veined(d, S, L, L * 0.42, a, x, y, rnd.choice(greens), '#2F4A40', 1.3)
    for i in range(8):                             # pale blossoms: two rings of petals, shaded heart
        x, y, a0 = rnd.uniform(0, S), rnd.uniform(0, S), rnd.uniform(0, math.tau)
        r = S * rnd.uniform(0.05, 0.075)
        for ring, (rr, col) in enumerate(((1.0, rnd.choice(['#D9C9C4', '#E3D6D2'])), (0.62, '#C9AEB0'))):
            for j in range(6):
                _wrap(d, S, _rot(_leaf(r * rr, r * rr * 0.9, 8, 0.8), a0 + (j + 0.5 * ring) * math.tau / 6, x, y), fill=col,
                      outline='#A98F92')
        for ox in (-S, 0, S):
            for oy in (-S, 0, S):
                d.ellipse([x + ox - r * 0.16, y + oy - r * 0.16, x + ox + r * 0.16, y + oy + r * 0.16], fill='#9A7F5A')
    _save(im.filter(ImageFilter.GaussianBlur(SS * 0.8)), 'green_bedroom_duvet.jpg', px)


def tapestry(px=1024):
    """Armchair / corner-chair seat cover: cream ground woven with brown and olive flowers, leaves and urns."""
    S = px * SS
    rnd = random.Random(21)
    im = Image.new('RGB', (S, S), '#D9CFB8')
    d = ImageDraw.Draw(im)
    for _ in range(14000):                         # weave
        x, y = rnd.randrange(S), rnd.randrange(S)
        d.line([(x, y), (x + rnd.randrange(4, 14), y)], fill=rnd.choice(['#CFC4AC', '#E0D7C2', '#C8BDA4']), width=SS)
    cols = ['#7A6A52', '#8A8462', '#6A5A44', '#9A8C70', '#74704E', '#A68F86']
    for i in range(60):                            # scrolling stems with leaves
        x, y, a0 = rnd.uniform(0, S), rnd.uniform(0, S), rnd.uniform(0, math.tau)
        col, L = rnd.choice(cols), S * rnd.uniform(0.10, 0.18)
        pts = [(x + L * t * math.sin(a0 + 1.4 * t), y - L * t * math.cos(a0 + 1.4 * t)) for t in [j / 8 for j in range(9)]]
        _wline(d, S, pts, col, 2 * SS)
        for j in (2, 4, 6, 8):
            for sg in (-1, 1):
                _wrap(d, S, _rot(_leaf(L * 0.30, L * 0.13, 8, 1.2), a0 + 1.4 * j / 8 + sg * 1.0, *pts[j]), fill=col)
    for i in range(40):                            # flower heads
        x, y, a0 = rnd.uniform(0, S), rnd.uniform(0, S), rnd.uniform(0, math.tau)
        r, col = S * rnd.uniform(0.035, 0.06), rnd.choice(cols)
        n = rnd.choice([6, 8])
        for j in range(n):
            _wrap(d, S, _rot(_leaf(r, r * 0.6, 8, 0.9), a0 + j * math.tau / n, x, y), fill=col, outline='#5A4A38')
        for ox in (-S, 0, S):
            for oy in (-S, 0, S):
                d.ellipse([x + ox - r * 0.25, y + oy - r * 0.25, x + ox + r * 0.25, y + oy + r * 0.25], fill='#E0D7C2', outline='#5A4A38')
    for i in range(9):                             # urns
        x, y = rnd.uniform(0, S), rnd.uniform(0, S)
        u = S * 0.05
        urn = [(-0.35, 0), (0.35, 0), (0.2, -0.25), (0.75, -0.9), (0.6, -1.5), (0.25, -1.7), (0.45, -2.0), (-0.45, -2.0),
               (-0.25, -1.7), (-0.6, -1.5), (-0.75, -0.9), (-0.2, -0.25)]
        _wrap(d, S, [(x + a * u, y + b * u) for a, b in urn], fill=rnd.choice(cols[:3]), outline='#5A4A38')
    _save(im.filter(ImageFilter.GaussianBlur(SS * 0.6)), 'green_bedroom_tapestry.jpg', px)


def sheet(px=512):
    S = px * SS
    rnd = random.Random(3)
    im = Image.new('RGB', (S, S), '#7E8C5E')
    d = ImageDraw.Draw(im)
    for _ in range(2600):
        x, y, r = rnd.uniform(0, S), rnd.uniform(0, S), rnd.uniform(1.2, 3.0) * SS
        for ox in (-S, 0, S):
            for oy in (-S, 0, S):
                d.ellipse([x + ox - r, y + oy - r * 0.7, x + ox + r, y + oy + r * 0.7], fill=rnd.choice(['#D9D8BC', '#C9CCA8']))
    _save(im.filter(ImageFilter.GaussianBlur(SS * 0.5)), 'green_bedroom_sheet.jpg', px)


def inlay(w=512, h=160):
    W, H = w * SS, h * SS
    rnd = random.Random(5)
    im = Image.new('RGB', (W, H), '#7C5638')
    d = ImageDraw.Draw(im)
    step = 22 * SS
    for i in range(-H // step - 2, W // step + 2):  # chevron veneer mirrored on the centre line
        col = ['#7C5638', '#6E4C30', '#86603E', '#644428'][i % 4]
        x = i * step
        d.polygon([(x, 0), (x + step, 0), (x + step + H, H), (x + H, H)], fill=col)
    left = im.crop((0, 0, W // 2, H))
    im.paste(left.transpose(Image.FLIP_LEFT_RIGHT), (W // 2, 0))
    d = ImageDraw.Draw(im)
    for _ in range(1500):                          # grain flecks
        x, y = rnd.randrange(W), rnd.randrange(H)
        d.line([(x, y), (x + rnd.randrange(4, 18), y + rnd.randrange(-2, 3))], fill='#6A4226', width=1)
    inl, dk = '#D8B77A', '#5A3A1E'
    d.rectangle([6 * SS, 6 * SS, W - 6 * SS, H - 6 * SS], outline=inl, width=2 * SS)     # stringing
    cx, cy = W / 2, H / 2
    for sg in (-1, 1):                             # spray: two curved stems with leaves, centre flower
        pts = [(cx + sg * t * W * 0.30, cy + math.sin(t * 3.0) * H * 0.16) for t in [i / 20 for i in range(21)]]
        d.line(pts, fill=inl, width=2 * SS, joint='curve')
        for k in (5, 9, 13, 17):
            x, y = pts[k]
            for up in (-1, 1):
                a = math.radians(90 * sg + up * 55)
                d.polygon(_rot(_leaf(H * 0.20, H * 0.085, 8), a, x, y), fill=inl if (k + up) % 3 else '#C19C5E')
        x, y = pts[-1]
        d.ellipse([x - 5 * SS, y - 5 * SS, x + 5 * SS, y + 5 * SS], fill=inl)
    for j in range(6):
        d.polygon(_rot(_leaf(H * 0.21, H * 0.15, 8, 0.8), j * math.tau / 6, cx, cy), fill='#E6CD96', outline=dk)
    d.ellipse([cx - 6 * SS, cy - 6 * SS, cx + 6 * SS, cy + 6 * SS], fill='#B08D3C')
    _save(im.filter(ImageFilter.GaussianBlur(SS * 0.5)), 'green_bedroom_inlay.jpg', (512, 128))   # power of two


if __name__ == '__main__':
    import sys
    for f in sys.argv[1:] or ['curtain', 'duvet', 'tapestry', 'sheet', 'inlay', 'marble', 'needlepoint']:
        globals()[f]()

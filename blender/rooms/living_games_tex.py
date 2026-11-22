"""Generated textures of the living-room table games, lamp base and coffee-table top ->
blender/textures/art/living/*.jpg. Run with the system Python (PIL, numpy, cv2):

    python blender/rooms/living_games_tex.py [board] [pieces] [box] [dominoes] [solitaire] [onyx] [marble] [oak]
                                             [velvet] [tartan]

Not imported by the build. Nothing here is reference-derived: everything is drawn from the survey description in
spec/phase3/living_games.md (sizes, layout, colours); velvet / tartan re-colour the module's own generated maps.
Seeded, so a re-run gives the same files.
"""
import math
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), 'textures', 'art', 'living')
FONT = 'C:/Windows/Fonts/kaiu.ttf'          # DFKai-SB: traditional kaishu, like the engraved characters (v10)
RED = ['車', '馬', '相', '仕', '帥', '炮', '兵']
GREEN = ['車', '馬', '象', '士', '將', '炮', '卒']


def rgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], np.float32)


def noise(w, h, cell, seed):
    """Smooth value noise in -1..1, one value per `cell` pixels, bicubic."""
    rng = np.random.default_rng(seed)
    a = rng.random((h // cell + 3, w // cell + 3)).astype(np.float32) * 2 - 1
    big = cv2.resize(a, ((w // cell + 3) * cell, (h // cell + 3) * cell), interpolation=cv2.INTER_CUBIC)
    return big[cell:cell + h, cell:cell + w]


def fbm(w, h, cell, seed, oct=3):
    out, amp, tot = np.zeros((h, w), np.float32), 1.0, 0.0
    for o in range(oct):
        out += amp * noise(w, h, max(2, cell >> o), seed + 17 * o)
        tot += amp
        amp *= 0.5
    return out / tot


def streak(w, h, ca, cl, seed, along='y', wrap=False):
    """Value noise stretched along the grain: one value per ca px across, per cl px along. wrap=True: periodic
    along the grain over h (h must be a multiple of cl), so the map tiles end to end."""
    if along == 'x':
        return streak(h, w, ca, cl, seed, wrap=wrap).T
    rng = np.random.default_rng(seed)
    if wrap:
        assert h % cl == 0, (h, cl)
        a = rng.random((h // cl, w // ca + 3)).astype(np.float32) * 2 - 1
        a = np.concatenate([a[-3:], a, a[:3]])
        big = cv2.resize(a, ((w // ca + 3) * ca, (h // cl + 6) * cl), interpolation=cv2.INTER_CUBIC)
        return big[3 * cl:3 * cl + h, ca:ca + w]
    a = rng.random((h // cl + 3, w // ca + 3)).astype(np.float32) * 2 - 1
    big = cv2.resize(a, ((w // ca + 3) * ca, (h // cl + 3) * cl), interpolation=cv2.INTER_CUBIC)
    return big[cl:cl + h, ca:ca + w]


def grain(w, h, seed, base, dark, along='y', period=7.0, warp=22.0, k=0.55, fine=0.06):
    """Straight wood grain running along `along` -> float RGB h x w x 3: long gently wandering latewood lines
    (warp stretched along the grain), streaky pores, a little broad tone variation."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    across = xx if along == 'y' else yy
    n1 = streak(w, h, 48, 320, seed, along) + 0.3 * streak(w, h, 12, 90, seed + 1, along)
    t = 0.5 + 0.5 * np.sin(2 * math.pi * (across + warp * n1) / period)
    t = t ** 5 * k + 0.35 * k * np.clip(streak(w, h, 2, 40, seed + 5, along), 0, 1)
    col = rgb(base)[None, None] * (1 - t[..., None]) + rgb(dark)[None, None] * t[..., None]
    col *= (1 + 0.06 * fbm(w, h, 96, seed + 7, 2))[..., None]
    col *= 1 + fine * noise(w, h, 2, seed + 9)[..., None]
    return np.clip(col, 0, 1)


def R(fn, xy, **kw):
    """PIL rectangle / ellipse with the corners in any order: xy = [p, q] or [x0, y0, x1, y1]."""
    if len(xy) == 2:
        xy = [*xy[0], *xy[1]]
    x0, y0, x1, y1 = xy
    fn([min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)], **kw)


def save(arr, name, q=90):
    p = os.path.join(OUT, name)
    im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)) if isinstance(arr, np.ndarray) else arr
    im.convert('RGB').save(p, quality=q)
    print('wrote', p, im.size)


def paste(dst, src, mask):
    m = (np.asarray(mask, np.float32) / 255.0)[..., None]
    dst[:] = dst * (1 - m) + src * m


# ------------------------------------------------------------------------------------------ xiangqi board
def board():
    """Board top 0.43 (image x = board local x, files north -> south) x 0.475 m (image y: row 0 = red side, +y).
    Walnut, cells alternating tone and grain direction, flush 4.5 mm maple strips on the 9 x 10 lines, inner files
    stopping at the river, both palace crosses; 38 mm plain margin."""
    W = H = 1024
    sx, sy = W / 430.0, H / 475.0
    C = 44.5

    def P(x, y):                                 # board mm (centre origin, +y toward red) -> pixel
        return (W / 2 + x * sx, H / 2 - y * sy)

    img = grain(W, H, 1, '#5E4433', '#3C2A1B', 'y', 11, 14, k=0.45)      # walnut, a shade under the survey's #6B4F3C:
    light = grain(W, H, 2, '#684E3D', '#443224', 'y', 10, 10, k=0.45)    # the room's warm light lifts it
    darkx = grain(W, H, 3, '#563F32', '#3A2A20', 'x', 10, 10, k=0.45)
    river = grain(W, H, 4, '#5D4334', '#3D2B1E', 'x', 12, 16, k=0.45)
    maple = grain(W, H, 5, '#D9C7A6', '#C2AB86', 'y', 6, 4, k=0.3, fine=0.03)
    X = lambda u: (u - 4) * C
    Y = lambda v: (4.5 - v) * C
    for i in range(8):
        for j in range(9):
            m = Image.new('L', (W, H))
            ImageDraw.Draw(m).rectangle([P(X(i), Y(j)), P(X(i + 1), Y(j + 1))], fill=255)
            paste(img, river if j == 4 else (light if (i + j) % 2 else darkx), m)
    m = Image.new('L', (W, H))
    d = ImageDraw.Draw(m)
    hw = 2.25

    def strip(a, b):                             # 4.5 mm strip between two board points (mm), square ends
        (x0, y0), (x1, y1) = a, b
        L = math.hypot(x1 - x0, y1 - y0)
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        nx, ny = -uy * hw, ux * hw
        ex, ey = ux * hw, uy * hw
        d.polygon([P(x0 - ex + nx, y0 - ey + ny), P(x1 + ex + nx, y1 + ey + ny), P(x1 + ex - nx, y1 + ey - ny),
                   P(x0 - ex - nx, y0 - ey - ny)], fill=255)
    for v in range(10):
        strip((X(0), Y(v)), (X(8), Y(v)))
    for u in range(9):
        if u in (0, 8):
            strip((X(u), Y(0)), (X(u), Y(9)))
        else:
            strip((X(u), Y(0)), (X(u), Y(4)))
            strip((X(u), Y(5)), (X(u), Y(9)))
    for v0 in (0, 7):
        strip((X(3), Y(v0)), (X(5), Y(v0 + 2)))
        strip((X(5), Y(v0)), (X(3), Y(v0 + 2)))
    m = m.filter(ImageFilter.GaussianBlur(0.6))
    paste(img, maple, m)
    save(img, 'games_board.jpg')


# ------------------------------------------------------------------------------------------ xiangqi pieces
def pieces():
    """4 x 4 atlas of 256 px cells: 0-6 red-filled characters, 7-13 turquoise, 14-15 plain rosewood (sides).
    The disc's flat top (r 16.5 mm) maps to r 118 px of a cell: 7.15 px/mm, characters ~20 mm high. Each glyph is
    centred on its ink (textbbox on kaiu.ttf is not the ink box: up to 6 mm off) and kept inside r 110 px."""
    N = 256
    W = 4 * N
    wood = grain(W, W, 11, '#4E262B', '#3A1A1E', 'y', 9, 8, k=0.3, fine=0.05)
    im = Image.fromarray((wood * 255).astype(np.uint8))
    font = ImageFont.truetype(FONT, 160)
    yy, xx = np.mgrid[0:N, 0:N]
    for k, (ch, fill) in enumerate([(c, '#C8505C') for c in RED] + [(c, '#4FB3A6') for c in GREEN]):
        cx, cy = (k % 4) * N + N / 2, (k // 4) * N + N / 2
        probe = Image.new('L', (2 * N, 2 * N))
        ImageDraw.Draw(probe).text((N / 2, N / 2), ch, font=font, fill=255)
        l, t, r, b = probe.getbbox()                               # the real ink box
        lay = Image.new('L', (N, N))
        ImageDraw.Draw(lay).text((N / 2 + N / 2 - (l + r) / 2, N / 2 + N / 2 - (t + b) / 2), ch, font=font, fill=255)
        a = np.asarray(lay) > 64
        rmax = float(np.sqrt((xx[a] - N / 2 + 0.5) ** 2 + (yy[a] - N / 2 + 0.5) ** 2).max())
        bl, bt, br, bb = lay.getbbox()
        assert abs((bl + br) / 2 - N / 2) <= 1.5 and abs((bt + bb) / 2 - N / 2) <= 1.5 and rmax <= 112, (ch, lay.getbbox(), rmax)
        x0, y0 = int(cx - N / 2), int(cy - N / 2)
        shadow = Image.new('RGB', (N, N), (30, 12, 14))            # the incision's shaded wall, 2 px down-right
        im.paste(shadow, (x0 + 2, y0 + 2), lay.filter(ImageFilter.GaussianBlur(0.8)))
        im.paste(Image.new('RGB', (N, N), fill), (x0, y0), lay.filter(ImageFilter.GaussianBlur(0.5)))
        print(k, 'ink box', lay.getbbox(), 'r max %.0f px' % rmax)
    save(im, 'games_pieces.jpg')


# ------------------------------------------------------------------------------------------ inlaid box
S = 6.0                                          # px per mm in the box atlas
LID = (0, 0, 870, 582)                           # 145 x 97 lid top
LSIDE = (0, 582, 870, 762)                       # 145 x 30 long side of the base
SSIDE = (0, 762, 582, 942)                       # 97 x 30 short side
LEDGE = (0, 942, 870, 1014)                      # 145 x 12 lid edge (the short edges use part of it)
PLAIN = (880, 600, 1024, 1024)                   # plain carcass: rims, underside


def box():
    W = 1024
    carcass = grain(W, W, 21, '#6A4232', '#3E2419', 'x', 8, 10, k=0.4)
    im = Image.fromarray((carcass * 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    BONE, BLACK, RB, GREY = '#EDE9DF', '#24272B', '#7A4A3C', '#8C8A86'
    _lid(im, d, BONE, BLACK, RB)
    for (x0, y0, x1, y1), pw in ((LSIDE, 118), (SSIDE, 70)):
        _side(d, x0, y0, x1, y1, pw, BONE, BLACK, GREY)
    x0, y0, x1, y1 = LEDGE
    for z in (3.0, 6.0, 9.0):                    # three white stringing lines
        R(d.rectangle, [x0, y0 + z * S - 2, x1, y0 + z * S + 2], fill=BONE)
    save(im, 'games_box.jpg')


def _lid(im, d, BONE, BLACK, RB):
    x0, y0, x1, y1 = LID
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    P = lambda x, y: (cx + x * S, cy - y * S)
    hx, hy = 72.5, 48.5
    R(d.rectangle, [P(-hx, hy), P(hx, -hy)], fill=BONE)
    B = 11.0
    # border: pinstripes square to each edge in blocks of 7, a dotted bone band through the middle of each block
    for side in range(4):
        horiz = side in (0, 2)
        L = hx if horiz else hy
        s = 1 if side in (0, 3) else -1
        t = -L + B
        while t < L - B - 0.5:
            for k in range(7):
                a = t + k * 1.0
                if a + 0.5 > L - B:
                    break
                if horiz:
                    R(d.rectangle, [P(a, s * hy), P(a + 0.5, s * (hy - B))], fill=BLACK)
                else:
                    R(d.rectangle, [P(s * hx, a + 0.5), P(s * (hx - B), a)], fill=BLACK)
            t += 8.5
        m0, m1 = (hy - B / 2 - 0.7, hy - B / 2 + 0.7) if horiz else (hx - B / 2 - 0.7, hx - B / 2 + 0.7)
        if horiz:
            R(d.rectangle, [P(-hx + B, s * m0), P(hx - B, s * m1)], fill=BONE)
            for a in np.arange(-hx + B + 0.6, hx - B, 1.2):
                R(d.ellipse, [P(a - 0.3, s * (hy - B / 2) + 0.3), P(a + 0.3, s * (hy - B / 2) - 0.3)], fill=BLACK)
        else:
            R(d.rectangle, [P(s * m0, -hy + B), P(s * m1, hy - B)], fill=BONE)
            for a in np.arange(-hy + B + 0.6, hy - B, 1.2):
                R(d.ellipse, [P(s * (hx - B / 2) - 0.3, a + 0.3), P(s * (hx - B / 2) + 0.3, a - 0.3)], fill=BLACK)
    for sx in (-1, 1):                           # bone corner squares with a mitre line
        for sy in (-1, 1):
            R(d.rectangle, [P(sx * hx, sy * hy), P(sx * (hx - B), sy * (hy - B))], fill=BONE)
            d.line([P(sx * hx, sy * hy), P(sx * (hx - B), sy * (hy - B))], fill='#B8B2A4', width=2)
    # 1 mm bone, 2 mm red-brown, 1 mm bone, then the black field
    for w, col in ((0.0, BONE), (1.0, RB), (3.0, BONE), (4.0, BLACK)):
        R(d.rectangle, [P(-hx + B + w, hy - B - w), P(hx - B - w, -hy + B + w)], fill=col)
    fx, fy = hx - B - 4.0, hy - B - 4.0
    field = Image.new('RGB', (int(2 * fx * S), int(2 * fy * S)), BLACK)
    fd = ImageDraw.Draw(field)
    Q = lambda x, y: (fx * S + x * S, fy * S - y * S)
    a, sy_ = 20.0, 1.2                           # star-rosette distance, vertical stretch of the lattice
    stars = []
    for j in range(-2, 3):                       # triangular lattice: rows 0.866 a * stretch apart, offset 1.5 a
        for i in range(-3, 4):
            stars.append((i * 3.0 * a + (1.5 * a if j % 2 else 0.0), j * 0.866 * a * sy_))
    stars = [(x, y) for x, y in stars if abs(x) < fx + 12 and abs(y) < fy + 12]
    ros = {}
    for sx_, sy2 in stars:
        for k in range(6):
            p = (round(sx_ + a * math.cos(k * math.pi / 3), 3), round(sy2 + a * math.sin(k * math.pi / 3) * sy_, 3))
            ros[p] = 1

    def band(p, q):
        fd.line([Q(*p), Q(*q)], fill=BLACK, width=int(3.4 * S))
        fd.line([Q(*p), Q(*q)], fill=BONE, width=int(2.4 * S))
        L = math.dist(p, q)
        for t in np.arange(0, L, 1.1):
            x, y = p[0] + (q[0] - p[0]) * t / L, p[1] + (q[1] - p[1]) * t / L
            R(fd.ellipse, [Q(x - 0.3, y + 0.3), Q(x + 0.3, y - 0.3)], fill=BLACK)
    for sx_, sy2 in stars:                       # two interlaced triangles round every star
        rr = [(sx_ + a * math.cos(k * math.pi / 3), sy2 + a * math.sin(k * math.pi / 3) * sy_) for k in range(6)]
        for k in range(6):
            band(rr[k], rr[(k + 2) % 6])
    rng = np.random.default_rng(7)
    for (x, y) in ros:                           # hexagon rosettes 14 mm
        fd.regular_polygon((Q(x, y), 7.0 * S), 6, rotation=0, fill=BLACK)
        for k in range(6):
            t = k * math.pi / 3
            pts = [(x + 7.0 * math.cos(t), y + 7.0 * math.sin(t)), (x + 4.0 * math.cos(t - 0.52), y + 4.0 * math.sin(t - 0.52)),
                   (x + 4.0 * math.cos(t + 0.52), y + 4.0 * math.sin(t + 0.52))]
            fd.polygon([Q(*p) for p in pts], fill=RB)
            tri = [(x, y), (x + 3.6 * math.cos(t - 0.52), y + 3.6 * math.sin(t - 0.52)),
                   (x + 3.6 * math.cos(t + 0.52), y + 3.6 * math.sin(t + 0.52))]
            fd.polygon([Q(*p) for p in tri], fill=BONE if k % 2 else BLACK)
            mid = [((tri[0][0] + tri[1][0]) / 2, (tri[0][1] + tri[1][1]) / 2), ((tri[1][0] + tri[2][0]) / 2, (tri[1][1] + tri[2][1]) / 2),
                   ((tri[2][0] + tri[0][0]) / 2, (tri[2][1] + tri[0][1]) / 2)]
            fd.polygon([Q(*p) for p in mid], fill=BLACK if k % 2 else BONE)
    for (x, y) in stars:                         # mother-of-pearl stars: six lozenges, 19 mm across
        r, ri = 9.5, 9.5 / math.sqrt(3)
        for k in range(6):
            t = math.pi / 2 + k * math.pi / 3
            tone = rng.uniform(-1, 1)
            col = tuple(int(c) for c in (239 + 8 * tone, 240 - 4 * abs(tone), 245 - 6 * tone))
            pts = [(x, y), (x + ri * math.cos(t - math.pi / 6), y + ri * math.sin(t - math.pi / 6)),
                   (x + r * math.cos(t), y + r * math.sin(t)), (x + ri * math.cos(t + math.pi / 6), y + ri * math.sin(t + math.pi / 6))]
            fd.polygon([Q(*p) for p in pts], fill=col, outline='#6E6C6A')
    im.paste(field, (int(P(-fx, fy)[0]), int(P(-fx, fy)[1])))


def _side(d, x0, y0, x1, y1, pw, BONE, BLACK, GREY):
    """Base side: dark wood, a pw x 20 mm lozenge-chevron panel in a bone line, 6 mm striped corner posts."""
    w_mm = (x1 - x0) / S
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    P = lambda x, y: (cx + x * S, cy - y * S)
    for sx in (-1, 1):                           # corner posts: horizontal black / bone stripes
        xa, xb = sx * w_mm / 2, sx * (w_mm / 2 - 6)
        for k in range(30):
            z = -15 + k
            R(d.rectangle, [P(min(xa, xb), z + 1), P(max(xa, xb), z + 0.5)], fill=BONE)
            R(d.rectangle, [P(min(xa, xb), z + 0.5), P(max(xa, xb), z)], fill=BLACK)
    hw, hh = pw / 2, 10.0
    R(d.rectangle, [P(-hw - 0.8, hh + 0.8), P(hw + 0.8, -hh - 0.8)], fill=BONE)
    R(d.rectangle, [P(-hw, hh), P(hw, -hh)], fill=BLACK)
    step, lean = 4.6, 3.2
    for row, (za, zb, sgn) in enumerate(((0.0, hh, 1), (-hh, 0.0, -1))):
        x = -hw - 6
        while x < hw + 2:                        # bone lozenges leaning alternately, grey triangles between
            a, b = x, x + 2.6
            ta, tb = (a + lean, b + lean) if sgn > 0 else (a - lean, b - lean)
            clip = lambda pts: [(min(max(px, -hw), hw), pz) for px, pz in pts]
            d.polygon([P(*p) for p in clip([(a, za), (b, za), (tb, zb), (ta, zb)])], fill=BONE)
            d.polygon([P(*p) for p in clip([(b, za), (a + step, za), (tb, zb)])], fill=GREY)
            x += step


# ------------------------------------------------------------------------------------------ dominoes
def dominoes():
    """512 x 512: 4 columns x 8 rows of 128 x 64 px tile faces (48 x 24 mm), the 28 of a double-six set in order
    (0-0, 0-1 .. 6-6), row 8 plain ivory for the sides."""
    im = Image.new('RGB', (512, 512), '#EEEADB')
    arr = np.asarray(im, np.float32) / 255 * (1 + 0.025 * fbm(512, 512, 16, 31)[..., None])
    im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    s = 128 / 48.0
    D = 6.4
    PIPS = {0: [], 1: [(0, 0)], 2: [(-D, -D), (D, D)], 3: [(-D, -D), (0, 0), (D, D)], 4: [(-D, -D), (D, -D), (-D, D), (D, D)],
            5: [(-D, -D), (D, -D), (0, 0), (-D, D), (D, D)], 6: [(-D, -D), (0, -D), (D, -D), (-D, D), (0, D), (D, D)]}
    k = 0
    for a in range(7):
        for b in range(a, 7):
            x0, y0 = (k % 4) * 128, (k // 4) * 64
            cx, cy = x0 + 64, y0 + 32
            R(d.rectangle, [cx - 0.5 * s, cy - 9.5 * s, cx + 0.5 * s, cy + 9.5 * s], fill='#1D2026')
            R(d.ellipse, [cx - 1.3 * s, cy - 1.3 * s, cx + 1.3 * s, cy + 1.3 * s], fill='#B39350', outline='#7E6530')
            for half, v in ((-1, a), (1, b)):
                hx = cx + half * 12 * s
                for px, py in PIPS[v]:
                    x, y = hx + px * s, cy + py * s
                    R(d.ellipse, [x - 2.1 * s, y - 2.1 * s, x + 2.1 * s, y + 2.1 * s], fill='#1D2026')
            k += 1
    save(im, 'games_dominoes.jpg')


# ------------------------------------------------------------------------------------------ solitaire, marbles, lamp
def solitaire():
    """Burr-wood top of the 0.24 m board (512 px across its diameter, 0.47 mm/px; v10 t56, g1369, survey 2.3):
    a dark red-brown field (#5E3B27, darker than the table it stands on) mottled with darker blotches and thin
    curling veins (domain-warped noise, swirled round every eye), crowded with clusters of small dark burl eyes,
    a few golden patches."""
    W = 512
    rng = np.random.default_rng(44)
    yy, xx = np.mgrid[0:W, 0:W].astype(np.float32)
    eyes = []
    for _ in range(46):                                               # clusters of eyes
        cx, cy = rng.uniform(0, W, 2)
        for _ in range(rng.integers(3, 12)):
            eyes.append((cx + rng.normal(0, 16), cy + rng.normal(0, 16), rng.uniform(0.8, 2.6)))
    qx = xx + 28 * fbm(W, W, 96, 47, 3)                               # domain warp ...
    qy = yy + 28 * fbm(W, W, 96, 48, 3)
    near = np.full((W, W), 1e9, np.float32)
    for x, y, r in eyes:                                              # ... plus a swirl round every eye
        dx, dy = xx - x, yy - y
        d = np.sqrt(dx * dx + dy * dy) + 1e-3
        w = 6.0 * np.exp(-d / 14.0)
        qx += -dy / d * w
        qy += dx / d * w
        near = np.minimum(near, d - r)
    warp = lambda f: cv2.remap(f, qx % W, qy % W, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
    blot = warp(fbm(W, W, 48, 41, 3))                                 # mottled blotches
    vein = 1 - np.abs(warp(fbm(W, W, 32, 42, 3)))                     # thin curling veins where the noise crosses 0
    vein = np.clip((vein - 0.86) / 0.14, 0, 1) ** 1.5
    col = rgb('#4E3121')[None, None] * (1 + 0.08 * fbm(W, W, 128, 43, 2))[..., None]   # #5E3B27 as seen: lamps lift it
    gold = np.clip(fbm(W, W, 110, 45, 2) * 2.2 - 0.45, 0, 1) ** 1.5     # a few golden patches
    col = col * (1 - 0.4 * gold[..., None]) + rgb('#A07850')[None, None] * 0.4 * gold[..., None]
    dk = np.clip(blot * 1.8 + 0.1, 0, 1) * 0.55 + 0.35 * vein
    col = col * (1 - dk[..., None]) + rgb('#3A2418')[None, None] * dk[..., None]
    halo = np.clip(1 - np.maximum(near, 0) / 4.0, 0, 1) * 0.5          # dark rim round each eye, black core
    col = col * (1 - halo[..., None]) + rgb('#3A2418')[None, None] * halo[..., None]
    core = (near < 0).astype(np.float32)
    col = col * (1 - core[..., None]) + rgb('#24160F')[None, None] * core[..., None]
    col *= 1 + 0.04 * noise(W, W, 2, 46)[..., None]
    save(cv2.GaussianBlur(np.clip(col, 0, 1), (0, 0), 0.6), 'games_solitaire.jpg')


def onyx():
    """Banded onyx for a third of the marbles: wavy, slightly tilted cream / honey / brown strata across the image
    v (the marbles map it by a planar projection, so the bands run straight through each ball as in v10 t56)."""
    W = 256
    yy, xx = np.mgrid[0:W, 0:W].astype(np.float32)
    t = (yy + 0.18 * xx) / W * 5 + 0.35 * fbm(W, W, 64, 51, 3) + 0.1 * fbm(W, W, 16, 53, 2)
    b = 0.5 + 0.5 * np.sin(2 * math.pi * t + 1.5 * np.sin(2 * math.pi * t * 0.37))
    c1, c2, c3 = rgb('#E6E1D3'), rgb('#CDBF9C'), rgb('#8E7359')
    mix = np.where(b[..., None] > 0.5, c1 * (b[..., None] - 0.5) * 2 + c2 * (1 - (b[..., None] - 0.5) * 2),
                   c2 * b[..., None] * 2 + c3 * (1 - b[..., None] * 2))
    save(mix * (1 + 0.04 * noise(W, W, 3, 52)[..., None]), 'games_onyx.jpg')


def marble():
    """Rose-brown mottled marble of the lamp base, #B5846B +-15 %, faint pale veins; tileable enough at 0.12 m."""
    W = 256
    m = fbm(W, W, 40, 61, 4)
    v = np.abs(np.sin(6 * fbm(W, W, 80, 62, 3) + 3 * m))
    col = rgb('#8C6350')[None, None] * (1 + 0.15 * m[..., None])          # #B5846B as seen; the room's light lifts it
    col = col * (1 - 0.25 * (v < 0.06)[..., None]) + rgb('#E3C9B8')[None, None] * 0.25 * (v < 0.06)[..., None]
    save(cv2.GaussianBlur(col, (3, 3), 0), 'lamp_marble.jpg')


def oak():
    """Coffee / side table top: dark stained plain-sawn oak over four boards (v10 t40, t42, g0604; survey 2.5):
    broad cathedral arches opening toward the board ends (nested parabolas, apex along the length, never closed),
    running out into straight grain at the board edges; dense open-pore streaks stretched along the length,
    nearly black in the latewood bands, over a mid brown ground. 512 x 1024 = 0.64 m across x 1.28 m along
    (living_parts.oak_dark size_m); image y = along the boards. Tiles end to end (the table top's UVs run
    -0.625..0.625 along) and side to side on a board joint."""
    W, H = 512, 1024
    S = lambda ca, cl, sd: streak(W, H, ca, cl, sd, wrap=True)
    col = np.zeros((H, W, 3), np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    edges = [0, 120, 251, 384, 512]
    rng = np.random.default_rng(71)
    ground, late, pore = rgb('#4F3E30'), rgb('#33261B'), rgb('#1E150F')
    for k in range(4):
        a, b = edges[k], edges[k + 1]
        u0 = rng.uniform(a + 0.3 * (b - a), b - 0.3 * (b - a))       # heart of the board
        kk = rng.uniform(0.0016, 0.0026)                              # arch sharpness, 1/px
        sgn = 1 if k % 2 else -1                                      # neighbouring boards point opposite ways
        wob = 9 * S(40, 256, 72 + k) + 3 * S(8, 64, 76 + k) + 22 * S(512, 512, 77 + k)
        u = xx - u0 + wob                                             # the heart wanders along the board
        per = rng.uniform(1.0, 1.3)
        L = H / per / round(H / per / 34.0)                           # whole number of rings over the tile
        run = sgn * (yy / L + 4.0 * S(512, 512, 79 + k))              # uneven arch spacing, never reversing
        phase = kk * u ** 2 / 2 + run + 1.5 * S(64, 512, 80 + k)
        ring = (phase / per) % 1.0                                    # ~12-18 mm figure bands, arches 4-6 cm apart
        th = 0.45 + 0.2 * S(90, 256, 85 + k)                          # latewood share varies ring to ring
        lw = np.clip((ring - th) / (1 - th), 0, 1) ** 1.6
        tone = 1 + 0.07 * S(30, 256, 90 + k) + 0.03 * S(128, 128, 95 + k)
        c = ground[None, None] * tone[..., None]
        c = c * (1 - 0.55 * lw[..., None]) + late[None, None] * 0.55 * lw[..., None]
        pores = np.clip(S(1, 64, 100 + k) * 2.2 - 1.0, 0, 1)          # 1-px pores, ~64 px long
        pw = (0.15 + 0.85 * lw) * pores
        c = c * (1 - 0.8 * pw[..., None]) + pore[None, None] * 0.8 * pw[..., None]
        ray = np.clip(S(3, 4, 110 + k) - 0.8, 0, 1) * 1.2             # a few pale ray flecks
        c = c * (1 + 0.25 * ray[..., None])
        col[:, a:b] = c[:, a:b]
    for a in edges[:-1]:                                              # board joints, the tile edge being one
        col[:, [a - 1, a]] *= 0.75
    pad = 8
    col = cv2.GaussianBlur(np.pad(col, ((pad, pad), (pad, pad), (0, 0)), mode='wrap'), (0, 0), sigmaX=0.45,
                           sigmaY=1.2)[pad:-pad, pad:-pad]
    save(col, 'oak_top.jpg')


def _hsv_shift(src, dst, dh, ks=1.0, kv=1.0, mask=None):
    """Hue shift (degrees) / saturation and value scale of an existing generated map; mask(h, s) -> 0..1 weight."""
    im = cv2.imread(os.path.join(OUT, src)).astype(np.float32) / 255.0
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)                     # H in degrees for float images
    w = mask(hsv[..., 0], hsv[..., 1]) if mask else 1.0
    hsv[..., 0] = (hsv[..., 0] + dh * w) % 360
    hsv[..., 1] = np.clip(hsv[..., 1] * (1 + (ks - 1) * w), 0, 1)
    hsv[..., 2] = np.clip(hsv[..., 2] * (1 + (kv - 1) * w), 0, 1)
    out = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    cv2.imwrite(os.path.join(OUT, dst), np.clip(out * 255, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 90])
    print('wrote', dst)


def velvet():
    """Velvet nap maps turned from burnt orange (median #8B5631, hue 25) toward the dusty terracotta rose of the v10
    daylight samples (sofa #A35451, armchair #A65F5D; survey estimate #A2584A, hue ~8)."""
    _hsv_shift('velvet.jpg', 'velvet_rose.jpg', -16, 0.82, 1.02)
    _hsv_shift('velvet_light.jpg', 'velvet_rose_light.jpg', -16, 0.82, 1.02)


def tartan():
    """Curtain tartan: the brick-red bands (#A04A45) turned raspberry-wine (#9A4A55, v10 daylight); the taupe ground,
    cream and charcoal lines stay."""
    red = lambda h, s: np.clip((s - 0.18) / 0.15, 0, 1) * np.clip(1 - np.minimum(np.abs(h - 4), 360 - np.abs(h - 4)) / 30, 0, 1)
    _hsv_shift('tartan.jpg', 'tartan_wine.jpg', -12, 0.95, 0.97, red)


JOBS = dict(board=board, pieces=pieces, box=box, dominoes=dominoes, solitaire=solitaire, onyx=onyx, marble=marble, oak=oak,
            velvet=velvet, tartan=tartan)

if __name__ == '__main__':
    for job in sys.argv[1:] or JOBS:
        JOBS[job]()

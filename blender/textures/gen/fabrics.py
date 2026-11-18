"""Fabric and carpet textures: Poly Haven velvet/linen recoloured; tartan, check, floral tapestry and
carpet synthesised to the colours and repeat sizes in spec/rooms/{living,dining,stairs}.md."""
import numpy as np, cv2
from common import (equalize, load, save, reg, recolor, lin, srgb, hex3, blur, normal, noise, renorm)

PH = 'Poly Haven CC0: '
SYN = 'synthesised by gen/fabrics.py'


# ---------------------------------------------------------------- yarn-level weave
def weave(warp, weft, twill, px_per_thread=4, fuzz=0.04, seed=0):
    """warp / weft: (n,3) and (m,3) linear yarn colours, one per thread (warp threads run down the
    image). twill=True -> 2/2 twill (tartan), False -> plain weave. Returns sRGB colour, height."""
    n, m, p = len(warp), len(weft), px_per_thread
    j, i = np.mgrid[0:m, 0:n]
    top = ((i + j) % 4 < 2) if twill else ((i + j) % 2 == 0)             # True: warp yarn on top
    top = np.kron(top, np.ones((p, p), bool))
    W = np.kron(np.broadcast_to(warp[None], (m, n, 3)), np.ones((p, p, 1), np.float32))
    F = np.kron(np.broadcast_to(weft[:, None], (m, n, 3)), np.ones((p, p, 1), np.float32))
    prof = 0.5 - 0.5 * np.cos((np.arange(p) + 0.5) / p * 2 * np.pi)       # 0 at yarn edge, 1 on its crown
    pw = np.tile(prof, n)[None, :] * np.ones((m * p, 1))                  # across a warp yarn
    pf = np.tile(prof, m)[:, None] * np.ones((1, n * p))
    crown = np.where(top, pw, pf).astype(np.float32)
    col = np.where(top[..., None], W, F) * (0.80 + 0.25 * crown)[..., None]
    col *= (1 + fuzz * noise(m * p, n * p, 1.5, 12, seed))[..., None]
    return srgb(blur(col, 0.6)), blur(crown + 0.3 * np.where(top, 1, 0), 0.6)


def stripes(spec):
    """[(hex, threads), ...] -> (n,3) linear yarn colours."""
    return np.concatenate([np.tile(lin(hex3(h))[None], (k, 1)) for h, k in spec]).astype(np.float32)


def tartan():
    """Living-room curtains: taupe ground, broad brick-red band, charcoal guard lines, cream double
    line; sett repeat 0.20 m = 256 threads."""
    T, R, C, K = '#8E8271', '#A04A45', '#E3DCCB', '#3C3836'
    sett = stripes([(T, 22), (K, 4), (T, 6), (R, 64), (T, 6), (K, 4), (T, 22),
                    (T, 50), (C, 4), (T, 20), (C, 4), (T, 50)])
    col, h = weave(sett, sett, True, seed=81)
    b = save('tartan_red_col', col, SYN)
    n = save('tartan_red_nrm', normal(0.0004 * h, 0.2 / 1024), SYN)
    reg('tartan_red', b, (0.2, 0.2), nrm=n, rough=0.95, note=f'2/2 twill, yarns {T} {R} {C} {K}')


def check():
    """Dining curtains: ivory ground, 90 mm taupe bands both ways at 0.20 m pitch, darker crossing
    squares, a fine paler line through the middle of each band. Colours painted directly (the
    band reads warp-faced in the video), then given plain-weave yarn relief."""
    n = 256
    band = np.zeros(n, bool)
    band[70:186] = True                                                   # 116 threads = 90 mm
    line = np.zeros(n, bool)
    line[126:130] = True
    bx, by = band[None, :], band[:, None]
    col = np.zeros((n, n, 3), np.float32) + lin(hex3('#E7E1D3'))
    col[np.broadcast_to(bx ^ by, (n, n))] = lin(hex3('#9A9382'))
    col[np.broadcast_to(bx & by, (n, n))] = lin(hex3('#7F7868'))
    col[np.broadcast_to(line[None, :] | line[:, None], (n, n))] = lin(hex3('#C4BEAE'))
    grey = np.ones((n, 3), np.float32)
    shade, h = weave(grey, grey, False, seed=82)                           # relief only
    col = np.kron(col, np.ones((4, 4, 1), np.float32)) * lin(shade) / lin(shade).mean()
    b = save('check_grey_col', srgb(col), SYN)
    nm = save('check_grey_nrm', normal(0.0003 * h, 0.2 / 1024), SYN)
    reg('check_grey', b, (0.2, 0.2), nrm=nm, rough=0.95, note='ivory #E7E1D3 / taupe #9A9382 / crossing #7F7868')


# ---------------------------------------------------------------- Jacobean floral (dining chair seats)
def floral():
    S, N, P = 2048, 1024, 0.30
    C = {k: tuple(map(float, lin(hex3(v)))) for k, v in dict(
        G='#EBE4D0', R='#B4513F', T='#5F8E98', S='#7D9160', O='#C9A24A', D='#8E3A2D', K='#5E7048').items()}
    img = np.zeros((S, S, 3), np.float32) + np.array(C['G'], np.float32)
    offs = [(ox, oy) for ox in (-S, 0, S) for oy in (-S, 0, S)]

    def ell(x, y, a, b, ang, col):
        for ox, oy in offs:
            cv2.ellipse(img, (int(x * S + ox), int(y * S + oy)), (max(1, int(a * S)), max(1, int(b * S))), ang, 0, 360, col, -1, cv2.LINE_AA)

    def path(pts, col, w):
        for ox, oy in offs:
            cv2.polylines(img, [np.int32([(x * S + ox, y * S + oy) for x, y in pts])], False, col, int(w * S), cv2.LINE_AA)

    def flower(x, y, r, col, dark, petals=8):
        for k in range(petals):
            a = k * 360 / petals + 11
            ell(x + 0.58 * r * np.cos(np.radians(a)), y + 0.58 * r * np.sin(np.radians(a)), 0.50 * r, 0.27 * r, a, col)
            ell(x + 0.42 * r * np.cos(np.radians(a)), y + 0.42 * r * np.sin(np.radians(a)), 0.22 * r, 0.07 * r, a, dark)
        ell(x, y, 0.24 * r, 0.24 * r, 0, C['O'])

    t = np.linspace(0, 1, 80)
    stem1 = [(u, 0.47 + 0.19 * np.sin(2 * np.pi * u)) for u in t]              # periodic in x
    stem2 = [(0.52 + 0.17 * np.sin(2 * np.pi * u + 1.0), u) for u in t]        # periodic in y
    for st in (stem1, stem2):
        path(st, C['K'], 0.012)
        for k in range(4, 80, 9):                                             # leaves alternate sides
            (x0, y0), (x1, y1) = st[k - 1], st[k + 1]
            ang = np.degrees(np.arctan2(y1 - y0, x1 - x0))
            side = 1 if (k // 9) % 2 else -1
            a2 = np.radians(ang + side * 55)
            ell(st[k][0] + 0.045 * np.cos(a2), st[k][1] + 0.045 * np.sin(a2), 0.048, 0.019, ang + side * 55, C['S'])
    flower(0.27, 0.27, 0.165, C['R'], C['D'])
    flower(0.76, 0.66, 0.125, C['T'], C['K'], 6)
    flower(0.80, 0.14, 0.10, C['R'], C['D'], 6)
    flower(0.20, 0.80, 0.085, C['T'], C['K'], 5)
    for x, y in ((0.50, 0.08), (0.07, 0.50), (0.45, 0.60), (0.92, 0.42), (0.60, 0.90)):
        ell(x, y, 0.022, 0.022, 0, C['O'])
    img = cv2.resize(img, (N, N), interpolation=cv2.INTER_AREA)
    grey = np.ones((256, 3), np.float32)
    shade, h = weave(grey, grey, False, seed=83)
    img = img * lin(shade) / lin(shade).mean()
    b = save('tapestry_floral_col', srgb(img), SYN)
    n = save('tapestry_floral_nrm', normal(0.0004 * h, P / N), SYN)
    reg('tapestry_floral', b, (P, P), nrm=n, rough=0.9, note='generic Jacobean floral, repeat 0.30 m, main flower ~0.10 m')


# ---------------------------------------------------------------- recoloured Poly Haven cloth
def cloth():
    vn = save('velvet_nrm', renorm(load('velour_velvet', 'nor_gl', 1024)), PH + 'velour_velvet nor_gl, resized')
    vs = (0.284, 0.2735)
    for key, hx, con in (('velvet_orange', '#B5683F', 1.3), ('velvet_orange_light', '#C98958', 1.3),
                         ('velvet_champagne', '#D3C6A6', 1.7)):
        img = recolor(equalize(load('velour_velvet', 'Diffuse', 1024), amount=0.6), hx, contrast=con, sat=0.0)
        b = save(key + '_col', img, PH + f'velour_velvet Diffuse, recoloured to {hx}')
        reg(key, b, vs, nrm=vn, rough=0.85, target=hx, sheen=0.6, nrm_strength=1.0)
    ln = save('linen_nrm', renorm(load('rough_linen', 'nor_gl', 1024)), PH + 'rough_linen nor_gl, resized')
    for key, hx, size, rough in (('linen_cream', '#E6D9B8', 0.271, 0.9),        # gimp braid, cord, tie-backs
                                 ('shade_ivory', '#F0E6CF', 0.271, 0.9),        # lampshade fabric
                                 ('wallcovering_aubergine', '#44333A', 0.54, 1.0)):   # dining dado, ~2 mm weave
        img = recolor(equalize(load('rough_linen', 'Diffuse', 1024)), hx, contrast=0.9, sat=0.3)
        b = save(key + '_col', img, PH + f'rough_linen Diffuse, recoloured to {hx}')
        reg(key, b, (size, size), nrm=ln, rough=rough, target=hx)


def carpet():
    """Stairs: saxony twist pile, warm silver-grey, +/-6 % large-scale brushing marks."""
    N, P = 1024, 1.0
    tuft = noise(N, N, 2.0, 7.0, 91)
    mott = noise(N, N, 200, 900, 92)
    col = lin(hex3('#9C958A')) * ((1 + 0.10 * tuft) * (1 + 0.035 * mott))[..., None]
    col = recolor(srgb(np.clip(col, 0, 1)), '#9C958A')
    b = save('carpet_mink_col', col, SYN)
    n = save('carpet_mink_nrm', normal(0.0007 * tuft, P / N), SYN)
    reg('carpet_mink', b, (P, P), nrm=n, rough=1.0, target='#9C958A', sheen=0.3)


def main():
    tartan()
    check()
    floral()
    cloth()
    carpet()

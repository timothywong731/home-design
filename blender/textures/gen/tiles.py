"""Tile, marble and quartz textures - all synthesised (no third-party content).
Metro tiles: long side along U (horizontal courses on a wall box-mapped with uv_box)."""
import numpy as np, cv2
from common import save, reg, lin, srgb, hex3, blur, normal, orm, noise, resize

SYN = 'synthesised by gen/tiles.py'


# ---------------------------------------------------------------- marble veins
def veins(H, W, seed, n=7, angle=35.0, length=(0.5, 1.3), width=3.0, fork=0.0012, wander=0.05):
    """Vein alpha 0..1 (periodic). n random-walk veins heading along `angle` (deg, image space),
    length as a fraction of the larger image side, tapering, with occasional thinner forks.
    Drawn at 2x and on the 3x3 wrap offsets so the result tiles; a soft halo is added."""
    rng = np.random.default_rng(seed)
    S = 2
    cv = np.zeros((H * S, W * S), np.float32)
    todo = [(rng.uniform(0, W), rng.uniform(0, H), np.radians(angle + rng.normal(0, 8)) + (np.pi if rng.random() < 0.5 else 0),
             rng.uniform(*length) * max(H, W), width * rng.uniform(0.6, 1.3), rng.uniform(0.55, 1.0), 0) for _ in range(n)]
    step = 5.0
    while todo:
        x, y, th, ln, w0, alpha, depth = todo.pop()
        base, steps = th, max(4, int(ln / step))
        for k in range(steps):
            t = k / steps
            th += rng.normal(0, wander) + 0.04 * (base - th)
            nx_, ny_ = x + step * np.cos(th), y + step * np.sin(th)
            w = w0 * (0.35 + 0.65 * np.sin(np.pi * t) ** 0.6) * rng.uniform(0.8, 1.2)
            for oy in (-H, 0, H):
                for ox in (-W, 0, W):
                    p0 = (int(round((x + ox) * S)), int(round((y + oy) * S)))
                    p1 = (int(round((nx_ + ox) * S)), int(round((ny_ + oy) * S)))
                    if -50 < p0[0] < W * S + 50 and -50 < p0[1] < H * S + 50:
                        cv2.line(cv, p0, p1, float(alpha), max(1, int(round(w * S))), cv2.LINE_AA)
            if depth < 2 and rng.random() < fork * step:
                side = 1 if rng.random() < 0.5 else -1
                todo.append((x, y, th + side * np.radians(rng.uniform(18, 40)), ln * (1 - t) * rng.uniform(0.3, 0.6),
                             w0 * 0.6, alpha * 0.8, depth + 1))
            x, y = nx_, ny_
    a = cv2.resize(cv, (W, H), interpolation=cv2.INTER_AREA)
    core = blur(a, 0.7)
    halo = np.clip(blur(a, width * 2.5) * 2.0, 0, 0.45)
    return np.clip(core + halo * (0.6 + 0.4 * noise(H, W, 20, 120, seed + 9)), 0, 1)


def slab(key, body, vein, size, px, seed, rough, n=8, angle=35.0, width=3.0, cloud=0.012, strength=0.9, length=(0.5, 1.3)):
    W, H = px
    a = strength * veins(H, W, seed, n, angle, length, width)
    wisp = np.clip(noise(H, W, 30, 400, seed + 4, aniso=(angle, 3.0)) - 0.9, 0, 1) * 0.10      # faint cloudy streaks
    a = np.clip(a + wisp, 0, 1)
    base = lin(hex3(body)) * (1 + cloud * noise(H, W, 60, 500, seed + 5))[..., None]
    col = srgb(base * (1 - a[..., None]) + lin(hex3(vein)) * a[..., None])
    b = save(key + '_col', col, SYN)
    reg(key, b, size, rough=rough, target=body, note=f'veins {vein}')


# ---------------------------------------------------------------- metro tiles (half bond)
def metro(key, tile, grout_m, nx, ny, px, body, grout_hex, seed, var=0.04, vein=None, rough=0.12):
    """nx tiles x ny courses (ny even) of tile=(w,h) metres with grout_m joints, brick bond."""
    W, H = px
    pw, ph = tile[0] + grout_m, tile[1] + grout_m
    wm, hm = nx * pw, ny * ph
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    x, y = (x + 0.5) * wm / W, (y + 0.5) * hm / H
    j = np.floor(y / ph).astype(int) % ny
    xs = (x + (j % 2) * pw / 2) % wm
    i = np.floor(xs / pw).astype(int) % nx
    lx, ly = xs - i * pw, y - j * ph
    d = np.minimum(np.minimum(lx, pw - lx), np.minimum(ly, ph - ly)) - grout_m / 2   # >0 inside the tile
    aa = 0.5 * max(wm / W, hm / H)
    g = np.clip(0.5 - d / (2 * aa), 0, 1)                                              # grout mask
    tid = j * nx + i
    shade = (1 + rng.normal(0, var * 0.6, nx * ny))[tid]
    col = lin(hex3(body))[None, None, :] * shade[..., None]
    if vein:                                   # each tile is a different crop of one marble print
        V = 0.8 * veins(1024, 1024, seed + 3, n=9, angle=32, length=(0.25, 0.6), width=2.0)
        ox, oy = rng.integers(0, 1024, nx * ny)[tid], rng.integers(0, 1024, nx * ny)[tid]
        a = V[((ly / hm * H).astype(int) + oy) % 1024, ((lx / wm * W).astype(int) + ox) % 1024]
        col = col * (1 - a[..., None]) + lin(hex3(vein)) * a[..., None]
    gcol = lin(hex3(grout_hex)) * (1 + 0.04 * noise(H, W, 2, 6, seed + 1))[..., None]
    col = srgb(col * (1 - g[..., None]) + gcol * g[..., None])
    cushion = np.clip(1 - d / 0.0025, 0, 1) ** 2 * (1 - g)                             # soft pillowed edge
    height = -0.0012 * g - 0.0005 * cushion
    b = save(key + '_col', col, SYN)
    n = save(key + '_nrm', normal(height, wm / W, hm / H), SYN)
    o = save(key + '_orm', orm(rough + (0.85 - rough) * g), SYN)
    reg(key, b, (wm, hm), nrm=n, orm=o, rough=rough, target=body,
        note=f'{int(tile[0]*1000)}x{int(tile[1]*1000)} mm half-bond, grout {grout_hex}')


# ---------------------------------------------------------------- Victorian geometric porch tile
def victorian():
    """One 0.33 m repeat = the physical tile K-X-K / X-U-X / K-X-K (spec/rooms/vestibule.md):
    blue square in the centre, tan triangles pointing away from it, black triangles toward the
    tile edge, white side triangles, black corner squares. 1.5 mm printed joints, 2 mm grout."""
    S, N, P = 4096, 1024, 0.33
    mm = S / (P * 1000)
    C = {k: lin(hex3(v)) for k, v in dict(K='#2E2E30', W='#EDEBE4', T='#A58F78', U='#97A3AE', J='#C9C7C0').items()}
    rng = np.random.default_rng(5)
    img = np.zeros((S, S, 3), np.float32)
    c = S / 3

    def poly(pts, col):
        cv2.fillPoly(img, [np.round(np.array(pts)).astype(np.int32)], tuple(float(v) for v in col * (1 + rng.normal(0, 0.025))))
    for cj in range(3):
        for ci in range(3):
            x0, y0, x1, y1 = ci * c, cj * c, (ci + 1) * c, (cj + 1) * c
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            if (ci, cj) == (1, 1):
                poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], C['U'])
            elif ci != 1 and cj != 1:
                poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], C['K'])
            else:                                   # X cell: triangle facing the centre is tan
                tri = {'l': [(x0, y0), (x0, y1), (mx, my)], 'r': [(x1, y0), (x1, y1), (mx, my)],
                       't': [(x0, y0), (x1, y0), (mx, my)], 'b': [(x0, y1), (x1, y1), (mx, my)]}
                inward = {(0, 1): 'r', (2, 1): 'l', (1, 0): 'b', (1, 2): 't'}[(ci, cj)]
                opposite = dict(l='r', r='l', t='b', b='t')[inward]
                for side, pts in tri.items():
                    poly(pts, C['T'] if side == inward else C['K'] if side == opposite else C['W'])
                jw = max(1, int(round(1.5 * mm)))
                cv2.line(img, (int(x0), int(y0)), (int(x1), int(y1)), tuple(map(float, C['J'])), jw, cv2.LINE_AA)
                cv2.line(img, (int(x0), int(y1)), (int(x1), int(y0)), tuple(map(float, C['J'])), jw, cv2.LINE_AA)
    grout = np.zeros((S, S), np.float32)
    for k in range(4):                              # cell joints; the outer ones are the real grout
        w = (2.0 if k in (0, 3) else 1.5) * mm
        p = k * c
        idx = np.arange(S)
        band = (np.minimum(np.abs(idx - p), S - np.abs(idx - p)) <= w / 2)
        img[band, :] = C['J']
        img[:, band] = C['J']
        if k in (0, 3):
            grout[band, :] = 1
            grout[:, band] = 1
    img = cv2.resize(img, (N, N), interpolation=cv2.INTER_AREA)
    grout = cv2.resize(grout, (N, N), interpolation=cv2.INTER_AREA)
    img *= (1 + 0.012 * noise(N, N, 1.5, 6, 6))[..., None]         # print speckle
    b = save('victorian_tile_col', srgb(img), SYN + ' from the cell table in spec/rooms/vestibule.md')
    n = save('victorian_tile_nrm', normal(-0.0005 * blur(grout, 1.0), P / N), SYN)
    o = save('victorian_tile_orm', orm(0.45 + 0.35 * grout), SYN)
    reg('victorian_tile', b, (P, P), nrm=n, orm=o, rough=0.45, note='blue square at UV (0.5,0.5); black/white/tan/blue #2E2E30 #EDEBE4 #A58F78 #97A3AE')


# ---------------------------------------------------------------- Art-Nouveau sunflower tile (fireplace)
def sunflower():
    S, N, P = 2048, 512, 0.152
    C = {k: lin(hex3(v)) for k, v in dict(G='#1D241B', Y='#E2B93B', B='#6A4320', L='#5D7A3A', O='#10140E').items()}
    img = np.zeros((S, S, 3), np.float32) + C['G']
    hgt = np.zeros((S, S), np.float32)

    def ell(cx, cy, a, b, ang, col, h=1.0):
        for canvas, v, t in ((img, tuple(map(float, C['O'])), -1), (hgt, h, -1)):
            cv2.ellipse(canvas, (int(cx), int(cy)), (int(a), int(b)), ang, 0, 360, v, t, cv2.LINE_AA)
        cv2.ellipse(img, (int(cx), int(cy)), (int(a - 9), int(b - 9)), ang, 0, 360, tuple(map(float, col)), -1, cv2.LINE_AA)
    cx, cy = S * 0.5, S * 0.36
    pts = np.array([(S * 0.5 + S * 0.03 * np.sin(t * 3.0), cy + t * S * 0.62) for t in np.linspace(0, 1, 40)], np.int32)
    cv2.polylines(img, [pts], False, tuple(map(float, C['O'])), 60, cv2.LINE_AA)
    cv2.polylines(img, [pts], False, tuple(map(float, C['L'])), 42, cv2.LINE_AA)
    cv2.polylines(hgt, [pts], False, 1.0, 60, cv2.LINE_AA)
    for sx, ang in ((-1, 35), (1, -35)):                              # two leaves
        ell(S * 0.5 + sx * S * 0.2, S * 0.76, S * 0.17, S * 0.075, ang, C['L'])
    for k in range(16):                                               # petals
        a = k * 360 / 16
        r = S * 0.2
        ell(cx + r * np.cos(np.radians(a)), cy + r * np.sin(np.radians(a)), S * 0.115, S * 0.042, a, C['Y'])
    ell(cx, cy, S * 0.115, S * 0.115, 0, C['B'], 1.3)
    edge = np.zeros((S, S), np.float32)
    e = int(S * 0.008)
    edge[:e], edge[-e:], edge[:, :e], edge[:, -e:] = 1, 1, 1, 1         # 2.4 mm dark joint between tiles
    img[edge > 0] = C['O'] * 2
    img = cv2.resize(img, (N, N), interpolation=cv2.INTER_AREA) * (1 + 0.03 * noise(N, N, 4, 40, 9))[..., None]
    hgt = blur(cv2.resize(hgt, (N, N), interpolation=cv2.INTER_AREA), 1.5)
    edge = blur(cv2.resize(edge, (N, N), interpolation=cv2.INTER_AREA), 1.0)
    b = save('sunflower_tile_col', srgb(img), SYN)
    n = save('sunflower_tile_nrm', normal(0.0005 * hgt - 0.0008 * edge, P / N), SYN)
    reg('sunflower_tile', b, (P, P), nrm=n, rough=0.1, note='one 152 mm tube-lined tile per repeat')


def main():
    victorian()
    metro('metro_grey', (0.300, 0.100), 0.003, 3, 6, (1024, 1024), '#C4C2BD', '#EEECE6', seed=41, var=0.04)
    metro('marble_metro', (0.300, 0.100), 0.0025, 3, 6, (1024, 1024), '#EFEDE8', '#DAD8D2', seed=51, var=0.01, vein='#A3A3A0')
    slab('marble_quartz', '#F2F1EE', '#B5B3AE', (2.4, 1.2), (2048, 1024), seed=61, rough=0.1, n=5, angle=33, width=5.0, length=(0.45, 0.9))
    slab('hearth_marble', '#E2DCCF', '#C4B8A0', (1.2, 1.2), (1024, 1024), seed=71, rough=0.25, n=5, angle=12, width=3.0, cloud=0.03, strength=0.7, length=(0.4, 0.8))
    sunflower()

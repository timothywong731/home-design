"""Site textures (owner: site): made at build time with numpy (no reference pixels) and cached as JPEG in
build/tex/site/, plus library textures recoloured to a colour the spec gives (a fence's or gate's `colour`).

    from lib import site_tex as ST
    ST.mat('site_setts')                    # a procedural material, keys in ST.KEYS
    ST.mat('closeboard_brown@#B3A58C')      # library texture, linear-light mean moved to #B3A58C (relief kept)
    ST.tone(key)                            # plain colour of either (rails, cappings)

A cached file is re-made when it is missing or VERSION changes. Scales and colours: spec/phase3/front.md 2.1
(setts), passage.md 2.8 (alley concrete), garden.md 3.3 (veranda soldier course).
"""
import os
from pathlib import Path

import bpy
import numpy as np

from . import materials as M

CACHE = Path(__file__).resolve().parents[2] / 'build' / 'tex' / 'site'
VERSION = 4
_cache = {}


# ---- colour and noise (numpy only: Blender's Python has no cv2 / PIL)
def _hex(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255.0


def _lin(c):
    c = np.asarray(c, np.float32)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4).astype(np.float32)


def _srgb(c):
    c = np.clip(np.asarray(c, np.float32), 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055).astype(np.float32)


def _noise(h, w, lo, hi, seed):
    """Periodic band-limited noise (wavelengths lo..hi px), zero mean, unit std."""
    f = np.fft.fft2(np.random.default_rng(seed).standard_normal((h, w)))
    r = np.sqrt(np.fft.fftfreq(h)[:, None] ** 2 + np.fft.fftfreq(w)[None, :] ** 2)
    n = np.real(np.fft.ifft2(f * np.exp(-(r * lo) ** 2) * (1 - np.exp(-(r * hi) ** 2))))
    return ((n - n.mean()) / (n.std() + 1e-9)).astype(np.float32)


def _normal(height, mx, my):
    """Tangent-space normal map (OpenGL, +Y up) from a height field in metres; mx, my = metres per pixel."""
    dx = (np.roll(height, -1, 1) - np.roll(height, 1, 1)) / (2 * mx)
    dr = (np.roll(height, -1, 0) - np.roll(height, 1, 0)) / (2 * my)
    n = np.dstack([-dx, dr, np.ones_like(dx)])
    return n / np.linalg.norm(n, axis=2, keepdims=True) * 0.5 + 0.5


def _recolor(img, hx):
    """sRGB image -> same relative detail, linear-light mean = hx."""
    L = np.maximum(_lin(img), 1e-5)
    t = _lin(_hex(hx))
    out = L / L.reshape(-1, 3).mean(0) * t
    for _ in range(4):                                  # clipping moves the mean: re-normalise
        out = np.clip(out, 0, 1)
        out *= t / np.maximum(out.reshape(-1, 3).mean(0), 1e-6)
    return _srgb(out)


# ---- files
def _write(path, img):
    """float sRGB image (row 0 = top) -> JPEG through a throw-away Blender image."""
    h, w = img.shape[:2]
    im = bpy.data.images.new('_site_tex_tmp', w, h, alpha=False)
    px = np.ones((h, w, 4), np.float32)
    px[..., :3] = np.clip(img[::-1], 0, 1)
    im.pixels.foreach_set(px.ravel())
    tmp = Path(path).with_name(f'{Path(path).stem}.{os.getpid()}.jpg')     # parallel builds: never read a half file
    im.filepath_raw, im.file_format = str(tmp), 'JPEG'
    im.save(filepath=str(tmp), quality=90)
    bpy.data.images.remove(im)
    os.replace(tmp, path)


def _read(path):
    im = bpy.data.images.load(str(path), check_existing=False)
    w, h = im.size
    px = np.empty(w * h * 4, np.float32)
    im.pixels.foreach_get(px)
    bpy.data.images.remove(im)
    return px.reshape(h, w, 4)[::-1, :, :3].copy()


def _file(name, make):
    """Path of one cached JPEG, made by make() -> image when missing."""
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / f'site_{name}_v{VERSION}.jpg'
    if not p.exists():
        _write(p, make())
    return str(p)


def _pair(name, make):
    """(col, nrm) paths of a procedural texture; make() -> (col, nrm) images, run once when either is missing."""
    col, nrm = (CACHE / f'site_{name}_{k}_v{VERSION}.jpg' for k in ('col', 'nrm'))
    if not (col.exists() and nrm.exists()):
        CACHE.mkdir(parents=True, exist_ok=True)
        for p, img in zip((col, nrm), make()):
            _write(p, img)
    return str(col), str(nrm)


# ---- procedural textures
SETTS = dict(size=1.98, px=1024, pitch=0.165, joint=0.009, lengths=(0.125, 0.165, 0.245), p=(0.2, 0.55, 0.25),
             tones=(('#A6A29A', 0.75), ('#B3AB95', 0.15), ('#A8958C', 0.10)), joint_hex='#46433D', moss='#565C3F')


def _setts():
    """Tumbled concrete setts in courses along U (parallel to the house): 160 wide, 120 / 160 / 240 long, three
    tones, dark dirty joints with a little moss (front.md 2.1). Row j's lower joint at v = j * pitch."""
    S = SETTS
    N, L, pitch, jt = S['px'], S['size'], S['pitch'], S['joint']
    rows = round(L / pitch)
    mpp = L / N
    rng = np.random.default_rng(11)
    y, x = (np.mgrid[0:N, 0:N].astype(np.float32) + 0.5) * mpp
    y = L - y                                           # row 0 = top of the image = v 1
    j = np.minimum((y / pitch).astype(int), rows - 1)
    ly = y - j * pitch
    hx_, w = zip(*S['tones'])
    d = np.zeros((N, N), np.float32)
    uid = np.zeros((N, N), int)
    rel = np.zeros((N, N), np.float32)                  # 0..1 along the unit (slight tilt / wear gradient)
    n_units = 0
    for r in range(rows):
        ls = []
        while sum(ls) < L - 0.06:
            ls.append(rng.choice(S['lengths'], p=S['p']))
        ls = np.array(ls) * L / sum(ls)
        edges = (np.concatenate([[0], np.cumsum(ls)]) + rng.uniform(0, L)) % L
        m = j == r
        xs = (x[m] - edges[0]) % L
        k = np.searchsorted(np.cumsum(ls), xs, side='right')
        k = np.minimum(k, len(ls) - 1)
        start = np.concatenate([[0], np.cumsum(ls)])[k]
        lx = xs - start
        ln = ls[k]
        rad = 0.010 + 0.006 * rng.random(len(ls))[k]    # tumbled arrises, a little different per unit
        qx = np.abs(lx - ln / 2) - (ln / 2 - jt / 2 - rad)
        qy = np.abs(ly[m] - pitch / 2) - (pitch / 2 - jt / 2 - rad)
        d[m] = rad - (np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0))
        uid[m] = n_units + k
        rel[m] = lx / ln
        n_units += len(ls)
    pick = rng.choice(len(hx_), n_units, p=np.array(w) / sum(w))
    tones = np.stack([_lin(_hex(h)) for h in hx_])
    tones = tones[0] + 0.6 * (tones - tones[0])                 # the minority tones read softer than their samples
    base = tones[pick] * (1 + rng.normal(0, 0.07, (n_units, 1))).astype(np.float32)
    col = base[uid] * (1 + 0.05 * (rel - 0.5) * rng.choice((-1, 1), n_units)[uid])[..., None]
    col *= (1 + 0.06 * _noise(N, N, 1.5, 4, 12) + 0.04 * _noise(N, N, 6, 30, 13))[..., None]       # aggregate
    col *= (1 - 0.08 * np.clip(_noise(N, N, 80, 400, 14), 0, 3))[..., None]                       # wear / dirt
    face = np.clip(d / 0.008, 0, 1)
    col *= (0.86 + 0.14 * face)[..., None]                                                       # chipped arrises
    g = np.clip(0.5 - d / (2 * mpp), 0, 1)[..., None]                                            # joint coverage
    mo = np.clip(_noise(N, N, 3, 40, 15) - 0.6, 0, 1)[..., None]
    gcol = _lin(_hex(S['joint_hex'])) * (1 - mo) + _lin(_hex(S['moss'])) * mo
    col = _srgb(col * (1 - g) + gcol * g)
    height = 0.005 * (1 - (1 - face) ** 2) - 0.006 * g[..., 0] + 0.0004 * _noise(N, N, 2, 10, 16) * face
    return col, _normal(height, mpp, mpp)


ALLEY = dict(size=(1.15, 8.26), px=(288, 2048), base='#A6A8A0', algae='#7E8A72', algae_dark='#5E6A52')


def _alley():
    """In-situ concrete laid once over the alley bounding box (x 4.65..5.80, y 1.70..9.96): mottled, cast-in patches,
    cracks, two cut joints, green algae along both walls (passage.md 2.8)."""
    (Wm, Hm), (W, H) = ALLEY['size'], ALLEY['px']
    mx, my = Wm / W, Hm / H
    rng = np.random.default_rng(21)
    y, x = (np.mgrid[0:H, 0:W].astype(np.float32) + 0.5)
    xm, ym = x * mx, Hm - y * my
    col = np.broadcast_to(_lin(_hex(ALLEY['base'])), (H, W, 3)).copy()
    col *= (1 + 0.07 * _noise(H, W, 30, 400, 22) + 0.04 * _noise(H, W, 1.5, 5, 23))[..., None]
    height = 0.0005 * _noise(H, W, 2, 12, 24)
    for _ in range(7):                                   # patches: rectangles of a slightly different mix
        x0, y0 = rng.uniform(0, Wm - 0.3), rng.uniform(0, Hm - 0.6)
        m = (xm > x0) & (xm < x0 + rng.uniform(0.25, 0.7)) & (ym > y0) & (ym < y0 + rng.uniform(0.3, 1.2))
        col[m] *= rng.uniform(0.88, 1.08)
        height[m] += 0.0015
    for yj in (3.6, 6.3):                               # cut joints across the alley
        m = np.abs(ym - yj) < 0.004
        col[m] *= 0.55
        height[m] -= 0.004
    for _ in range(9):                                   # cracks: wandering polylines
        px_, py_ = rng.uniform(0, W), rng.uniform(0, H)
        a = rng.uniform(0, 2 * np.pi)
        for _ in range(int(rng.uniform(60, 220))):
            a += rng.normal(0, 0.35)
            px_, py_ = px_ + np.cos(a) * 2.0, py_ + np.sin(a) * 2.0
            i, k = int(py_) % H, int(px_) % W
            col[i, k] *= 0.6
            height[i, k] -= 0.002
    wall = np.minimum(xm, Wm - xm)                       # algae along both wall feet, ragged
    a = np.clip(np.exp(-wall / 0.09) * (0.75 + 0.35 * _noise(H, W, 8, 120, 25)), 0, 1)[..., None]
    dark = np.clip(np.exp(-wall / 0.03), 0, 1)[..., None]
    alg = _lin(_hex(ALLEY['algae'])) * (1 - dark) + _lin(_hex(ALLEY['algae_dark'])) * dark
    alg = alg * (1 + 0.15 * _noise(H, W, 2, 8, 26))[..., None]
    col = col * (1 - a) + alg * a
    return _srgb(col), _normal(height, mx, my)


CONCRETE = dict(size=2.0, px=512, base='#A6A8A0', algae='#7E8A72')


def _concrete():
    """Tileable in-situ concrete (materials key 'concrete_insitu'): mottled, cast-in patches, faint algae blotches. The
    alley itself has its own laid-once sheet (_alley) with the algae along its walls."""
    S, N = CONCRETE, CONCRETE['px']
    mpp = S['size'] / N
    rng = np.random.default_rng(51)
    y, x = np.mgrid[0:N, 0:N]
    col = np.broadcast_to(_lin(_hex(S['base'])), (N, N, 3)).copy()
    col *= (1 + 0.07 * _noise(N, N, 25, 300, 52) + 0.04 * _noise(N, N, 1.5, 5, 53))[..., None]
    height = 0.0005 * _noise(N, N, 2, 12, 54)
    for _ in range(5):                                   # patches of another mix, wrapped so the tile repeats
        x0, y0, w, h = rng.integers(0, N, 2).tolist() + rng.integers(N // 8, N // 3, 2).tolist()
        m = ((x - x0) % N < w) & ((y - y0) % N < h)
        col[m] *= rng.uniform(0.9, 1.07)
        height[m] += 0.0012
    a = np.clip(_noise(N, N, 20, 200, 55) - 1.2, 0, 1)[..., None] * 0.5
    col = col * (1 - a) + _lin(_hex(S['algae'])) * a
    return _srgb(col), _normal(height, mpp, mpp)


SOLDIER = dict(size=(0.8, 0.2), px=(512, 128), unit=(0.1, 0.2), joint=0.004,
               tones=(('#A8604E', 0.6), ('#9C5646', 0.25), ('#B26C58', 0.15)), joint_hex='#9A8C78')


def _soldier():
    """One course of 200 x 100 clay pavers on end along U (the veranda's front edge, garden.md 3.3)."""
    S = SOLDIER
    (Wm, Hm), (W, H) = S['size'], S['px']
    mx, my = Wm / W, Hm / H
    rng = np.random.default_rng(31)
    y, x = (np.mgrid[0:H, 0:W].astype(np.float32) + 0.5)
    xm, ym = x * mx, y * my
    uw, jt = S['unit'][0], S['joint']
    i = (xm / uw).astype(int)
    lx = xm - i * uw
    d = np.minimum(np.minimum(lx, uw - lx), np.minimum(ym, Hm - ym)) - jt / 2
    hx_, w = zip(*S['tones'])
    n = int(round(Wm / uw))
    pick = rng.choice(len(hx_), n, p=np.array(w) / sum(w))
    col = np.stack([_lin(_hex(h)) for h in hx_])[pick][i % n] * (1 + rng.normal(0, 0.05, (n, 1)))[i % n]
    col *= (1 + 0.05 * _noise(H, W, 1.5, 5, 32))[..., None]
    g = np.clip(0.5 - d / (2 * mx), 0, 1)[..., None]
    col = _srgb(col * (1 - g) + _lin(_hex(S['joint_hex'])) * g)
    height = 0.002 * np.clip(d / 0.002, 0, 1) - 0.003 * g[..., 0]
    return col, _normal(height, mx, my)


FLAGS = dict(unit=0.2875, cols=(2, 1, 2, 1), rows=12, px=(512, 1024), joint=0.013, lens=(1, 2, 3), p=(0.2, 0.45, 0.35),
             tones=(('#9A9CA0', 0.55), ('#A4A39E', 0.2), ('#8E9196', 0.15), ('#A69F94', 0.10)), joint_hex='#8C8A84')


def _flags():
    """Riven grey sandstone in random courses along V (the passage and path run along Y): courses 560 and 275 wide,
    slabs 845 / 560 / 275 long, 13 mm pale joints (passage.md 2.5: the 560 series)."""
    S = FLAGS
    un, W, H = S['unit'], *S['px']
    Wm, Hm = un * sum(S['cols']), un * S['rows']
    mx, my = Wm / W, Hm / H
    rng = np.random.default_rng(41)
    y, x = (np.mgrid[0:H, 0:W].astype(np.float32) + 0.5)
    xm, ym = x * mx, Hm - y * my
    d = np.zeros((H, W), np.float32)
    uid = np.zeros((H, W), int)
    n_units, c0 = 0, 0.0
    for cw in S['cols']:
        c1 = c0 + cw * un
        ls, left = [], S['rows']
        while left:
            k = int(rng.choice(S['lens'], p=S['p']))
            if k <= left:
                ls.append(k)
                left -= k
        ends = np.cumsum(ls) * un
        shift = rng.uniform(0, Hm)
        m = (xm >= c0) & (xm < c1)
        ys = (ym[m] + shift) % Hm
        k = np.searchsorted(ends, ys, side='right')
        st = np.concatenate([[0], ends])[k]
        ln = np.array(ls)[k] * un
        ly = ys - st
        lx = xm[m] - c0
        d[m] = np.minimum(np.minimum(lx, cw * un - lx), np.minimum(ly, ln - ly)) - S['joint'] / 2
        uid[m] = n_units + k
        n_units += len(ls)
        c0 = c1
    hx_, w = zip(*S['tones'])
    pick = rng.choice(len(hx_), n_units, p=np.array(w) / sum(w))
    col = np.stack([_lin(_hex(h)) for h in hx_])[pick][uid] * (1 + rng.normal(0, 0.05, (n_units, 1)))[uid]
    riv = _noise(H, W, 12, 90, 42) + 0.5 * _noise(H, W, 3, 12, 43)
    col *= (1 + 0.05 * riv + 0.03 * _noise(H, W, 1.5, 4, 44))[..., None]
    col *= (1 - 0.06 * np.clip(_noise(H, W, 60, 300, 45), 0, 3))[..., None]                     # weathering
    g = np.clip(0.5 - d / (2 * mx), 0, 1)[..., None]
    col = _srgb(col * (1 - g) + _lin(_hex(S['joint_hex'])) * (1 + 0.06 * _noise(H, W, 2, 6, 46))[..., None] * g)
    face = np.clip(d / 0.004, 0, 1)
    height = 0.0025 * riv * face * 0.4 + 0.003 * face - 0.004 * g[..., 0]
    return col, _normal(height, mx, my)


# key: (maker, size_m, roughness, tone)
KEYS = {
    'site_setts': (_setts, (SETTS['size'],) * 2, 0.9, '#A6A29A'),
    'site_setts_border': (None, (SETTS['size'],) * 2, 0.9, '#7E7B75'),
    'site_alley_concrete': (_alley, ALLEY['size'], 0.92, ALLEY['base']),
    'site_concrete': (_concrete, (CONCRETE['size'],) * 2, 0.92, CONCRETE['base']),
    'site_soldier_course': (_soldier, SOLDIER['size'], 0.85, '#A8604E'),
    'site_flags': (_flags, (FLAGS['unit'] * sum(FLAGS['cols']), FLAGS['unit'] * FLAGS['rows']), 0.88, '#9A9CA0'),
}


def tone(key):
    if '@' in key:
        return key.split('@')[1]
    if key in KEYS:
        return KEYS[key][3]
    return M.MANIFEST.get(key, {}).get('target', '#9A9A96')


def mat(key):
    """Material for a KEYS key or 'library_key@#RRGGBB' (cached)."""
    if key in _cache:
        return _cache[key]
    if '@' in key:
        lib, hx = key.split('@')
        e = M.MANIFEST[lib]
        col = _file(f'{lib}_{hx[1:]}', lambda: _recolor(_read(Path(M.TEX_DIR) / e['base']), hx))
        nrm = str(Path(M.TEX_DIR) / e['nrm']) if e.get('nrm') else None
        m = M._build(key, base=col, nrm=nrm, rough=e['rough'], metal=e['metal'], nrm_strength=e.get('nrm_strength', 1.0),
                     size_m=e['size_m'])
    else:
        make, size, rough, hx = KEYS[key]
        if make is None:                                # the border course: the setts recoloured, same relief
            src = _pair('setts', _setts)
            col, nrm = _file('setts_border_col', lambda: _recolor(_read(src[0]), hx)), src[1]
        else:
            col, nrm = _pair(key.removeprefix('site_'), make)
        m = M._build(key, base=col, nrm=nrm, rough=rough, size_m=size)
    m['key'] = key
    _cache[key] = m
    return m

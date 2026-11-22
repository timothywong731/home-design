"""bathroom2 generated textures, made at build time with numpy (no reference pixels) and cached as JPEG in
build/tex/bathroom2/:

- spruce(side): untreated flat-sawn spruce boards of the sauna cabin, cathedral grain with pin knots (v13 t76, t83,
  t86, t87, f_0092). Grain runs along the image's V axis (mouldings.MB puts V along a box's `grain` axis; lathes along
  the profile); 'out' = the outer boards and capping, 'in' = the inner lining, 'ti' = benches, guard, bucket. Each
  variant keeps the mean colour the phase-3 builder tuned as a flat tone, so the cabin does not go orange.
- pile(part): grey tufted cotton bath mat, 'field' and the slightly lighter raised 'border' (v13 t106, t108, t123).
- stone(k): pale grey heater stones with white and dark speckle (v13 t86, t87, t105).

    from rooms import bathroom2_tex as TX
    TX.spruce('in')             # Principled, image-textured (lib.materials.image_mat), repeats every SIZE[...] metres

`python blender/rooms/bathroom2_tex.py <dir>` writes previews with PIL, without Blender.
"""
from pathlib import Path

import numpy as np

VERSION = 1
CACHE = Path(__file__).resolve().parents[2] / 'build' / 'tex' / 'bathroom2'

# spruce: one tile = 0.30 m across the grain x 2.0 m along it (a whole cabin board height, no stacked repeat)
SPRUCE_M, SPRUCE_PX = (0.30, 2.0), (512, 2048)
SPRUCE = {'out': ('#D8C399', 0.85, 11), 'in': ('#D7CFBB', 0.70, 12), 'ti': ('#D9CEB2', 0.70, 13)}  # mean, grain, seed
PILE_M, PILE_PX = (0.12, 0.12), (256, 256)
PILE = {'field': ('#A3A6A8', 21), 'border': ('#ADB0B2', 22)}
STONE_M, STONE_PX = (0.06, 0.06), (128, 128)
STONE = (('#A3A6A2', 31), ('#979B97', 32))


def _lin(hx):
    c = np.array([int(hx[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _srgb(L):
    L = np.clip(L, 0, 1)
    return np.where(L <= 0.0031308, L * 12.92, 1.055 * L ** (1 / 2.4) - 0.055).astype(np.float32)


def _noise(h, w, lo, hi, seed, an=1.0, ang=0.0):
    """Periodic band-limited noise (wavelengths about lo..hi px), zero mean, unit std; an > 1 stretches the features
    by `an` along the direction `ang` (radians from the image rows' axis, i.e. an > 1 at ang 0 = long along V)."""
    f = np.fft.fft2(np.random.default_rng(seed).standard_normal((h, w)))
    fy, fx = np.fft.fftfreq(h)[:, None], np.fft.fftfreq(w)[None, :]
    a, b = fy * np.cos(ang) + fx * np.sin(ang), -fy * np.sin(ang) + fx * np.cos(ang)
    r = np.sqrt((a * an) ** 2 + b ** 2)
    n = np.real(np.fft.ifft2(f * np.exp(-(r * lo) ** 2) * (1 - np.exp(-(r * hi) ** 2))))
    return ((n - n.mean()) / (n.std() + 1e-9)).astype(np.float32)


def _smooth(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def _match(L, hx):
    """Scale each channel so the linear mean equals the colour hx (keeps the tuned flat tone)."""
    return L * (_lin(hx) / L.reshape(-1, 3).mean(0))


def make_spruce(hx, strength, seed, w=SPRUCE_PX[0], h=SPRUCE_PX[1]):
    """float sRGB (h, w, 3), row 0 = top; columns across the grain, rows along it; tiles both ways. Rendered at 2x
    and box-filtered so the sharp latewood edges do not alias."""
    W, H = 2 * w, 2 * h
    mx, my = SPRUCE_M[0] / W, SPRUCE_M[1] / H                       # metres per (supersampled) pixel
    x = (np.arange(W) + .5) * mx
    y = (np.arange(H) + .5) * my
    # ring index of a flat-sawn board: a log cut just off its pith gives arches (cathedrals) along the grain. Two arch
    # centres per tile across (cos, periodic), ~3 mm rings on the flanks, 42 ring steps along 2.0 m (periodic)
    g = 16.0 * (1 - np.cos(2 * np.pi * 2 * x / SPRUCE_M[0])) / 2
    R = g[None, :] + 21.0 * y[:, None]
    R = R + 1.6 * _noise(H, W, 220, 900, seed, an=5) + .03 * _noise(H, W, 10, 40, seed + 1, an=3)
    rnd = np.random.default_rng(seed + 7)
    knots = []
    for k in range(5):                                               # pin knots 2.5-4 mm, one 7 mm
        xk, yk = rnd.uniform(0, SPRUCE_M[0]), rnd.uniform(0, SPRUCE_M[1])
        rk = .007 if k == 0 else rnd.uniform(.0025, .004)
        dx = (x[None, :] - xk + SPRUCE_M[0] / 2) % SPRUCE_M[0] - SPRUCE_M[0] / 2
        dy = (y[:, None] - yk + SPRUCE_M[1] / 2) % SPRUCE_M[1] - SPRUCE_M[1] / 2
        e = np.sqrt((dx / rk) ** 2 + (dy / (1.4 * rk)) ** 2)
        R = R + 2.5 * np.exp(-(e / 4.0) ** 2)                        # the rings swirl round the knot
        knots.append(e)
    t = R - np.floor(R)
    d = _smooth(t, .58, .94) ** 2 * (1 - _smooth(t, .94, .995))      # earlywood darkening into latewood, abrupt end
    c = _lin(hx)
    early, late = c * 1.08, c * np.array([.70, .60, .42], np.float32)
    L = early + (late - early) * (strength * d)[..., None]
    L = L * (1 + .035 * _noise(H, W, 2, 10, seed + 2, an=25))[..., None]          # fibre streaks along the grain
    L = L * (1 + .045 * _noise(H, W, 300, 1400, seed + 3, an=3))[..., None]       # slow tone drift (board to board)
    dark = c * np.array([.42, .30, .18], np.float32)
    for e in knots:
        core = _smooth(-e, -1.0, -.55)[..., None]
        halo = (.35 * np.exp(-((e - 1.25) / .3) ** 2))[..., None]
        L = L * (1 - halo) + late * halo
        L = L * (1 - core) + dark * core
    L = _match(L, hx)
    L = L.reshape(h, 2, w, 2, 3).mean((1, 3))
    return _srgb(L)


def make_pile(hx, seed, w=PILE_PX[0], h=PILE_PX[1]):
    """Tufted cotton loops (~1.5 mm) lying in combed waves; dark pits between tufts."""
    n1 = _noise(h, w, 1.2, 4, seed)
    n2 = _noise(h, w, 6, 26, seed + 1, an=4, ang=.6)
    n3 = _noise(h, w, 20, 120, seed + 2)
    v = 1 + .11 * n1 + .08 * n2 + .03 * n3
    v = v * (1 - .22 * _smooth(-n1, 1.2, 2.2))
    L = _lin(hx) * v[..., None]
    return _srgb(_match(L, hx))


def make_stone(hx, seed, w=STONE_PX[0], h=STONE_PX[1]):
    """Mottled pale grey stone with white and dark flecks (about 1-2 mm)."""
    mot = _noise(h, w, 6, 40, seed)
    L = _lin(hx) * (1 + .07 * mot)[..., None]
    fw = _smooth(_noise(h, w, 2, 5, seed + 1), 1.3, 2.0)[..., None]
    fd = _smooth(_noise(h, w, 2, 5, seed + 2), 1.6, 2.3)[..., None]
    L = L * (1 - fw) + _lin('#E6E7E3') * fw
    L = L * (1 - fd) + _lin('#4E524E') * fd
    return _srgb(_match(L, hx))


def _file(name, make):
    p = CACHE / f'{name}_v{VERSION}.jpg'
    if not p.exists():
        from lib import site_tex as ST                               # its writer: through a throw-away Blender image
        CACHE.mkdir(parents=True, exist_ok=True)
        ST._write(p, make())
    return str(p)


def spruce(side='out'):
    from lib import materials as M
    hx, s, seed = SPRUCE[side]
    return M.image_mat(f'bathroom2_spruce_{side}', _file(f'spruce_{side}', lambda: make_spruce(hx, s, seed)),
                       size_m=SPRUCE_M, roughness=0.7)


def pile(part='field'):
    from lib import materials as M
    hx, seed = PILE[part]
    return M.image_mat(f'bathroom2_bathmat_{part}', _file(f'pile_{part}', lambda: make_pile(hx, seed)),
                       size_m=PILE_M, roughness=1.0)


def stone(k=0):
    from lib import materials as M
    hx, seed = STONE[k % len(STONE)]
    return M.image_mat(f'bathroom2_stone_{k}', _file(f'stone_{k}', lambda: make_stone(hx, seed)),
                       size_m=STONE_M, roughness=0.8)


if __name__ == '__main__':                                           # previews without Blender
    import sys
    from PIL import Image
    out = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
    out.mkdir(parents=True, exist_ok=True)

    def save(name, im):
        Image.fromarray((np.clip(im, 0, 1) * 255).astype(np.uint8)).save(out / f'{name}.jpg', quality=90)
    for side, (hx, s, seed) in SPRUCE.items():
        save(f'spruce_{side}', make_spruce(hx, s, seed))
    for part, (hx, seed) in PILE.items():
        save(f'pile_{part}', make_pile(hx, seed))
    for k, (hx, seed) in enumerate(STONE):
        save(f'stone_{k}', make_stone(hx, seed))

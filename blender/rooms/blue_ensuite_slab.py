"""Calacatta slab texture of the en-suite cladding, made at build time with numpy (no reference pixels) and cached as
JPEG in build/tex/blue_ensuite/. The library 'porcelain_calacatta_slab' reads as sparse orange-tan streaks under the
3000 K light; the en-suite slab (v3 f_0385, f_0387, f_0391, t384.5) is a dense, branching network of mid-grey veins
(#9C9A93, darker cores) in clusters, with soft low-saturation olive-gold halos along some of them, on a near-white
ground (#EDE9E0), with calm areas between the clusters.

    from rooms import blue_ensuite_slab as SL
    SL.mat()                    # Principled, image-textured, repeats every SIZE_M under M.uv_box

`make(w, h)` is pure numpy (python blender/rooms/blue_ensuite_slab.py writes a preview JPEG with PIL).
"""
from pathlib import Path

import numpy as np

SIZE_M = (1.2, 2.4)                                   # one tile = two 1.2 m slab courses (no stacked repeat)
PX = (768, 1536)                                      # 1.56 mm / px
VERSION = 2
CACHE = Path(__file__).resolve().parents[2] / 'build' / 'tex' / 'blue_ensuite'


def _noise(h, w, lo, hi, seed, ang=0.0, an=1.0):
    """Periodic band-limited noise (wavelengths about lo..hi px), zero mean, unit std. an > 1 stretches the features
    along the direction `ang` (radians from +x, image rows down)."""
    f = np.fft.fft2(np.random.default_rng(seed).standard_normal((h, w)))
    fy, fx = np.fft.fftfreq(h)[:, None], np.fft.fftfreq(w)[None, :]
    u, v = fx * np.cos(ang) + fy * np.sin(ang), -fx * np.sin(ang) + fy * np.cos(ang)
    r = np.sqrt((u * an) ** 2 + (v / an) ** 2)
    n = np.real(np.fft.ifft2(f * np.exp(-(r * lo) ** 2) * (1 - np.exp(-(r * hi) ** 2))))
    return ((n - n.mean()) / (n.std() + 1e-9)).astype(np.float32)


def _ridge(n, width):
    """Thin line along the zero contour of n (half-width about `width` in noise units)."""
    return np.exp(-(n / width) ** 2)


def _smooth(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def _lin(hx):
    c = np.array([int(hx[i:i + 2], 16) for i in (1, 3, 5)], np.float32) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def make(w=PX[0], h=PX[1]):
    """float sRGB image (h, w, 3), row 0 = top, tiling in both directions."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    big, mid, small = _noise(h, w, 300, 1200, 1), np.abs(_noise(h, w, 110, 320, 2)), np.abs(_noise(h, w, 30, 80, 3))

    def fam(kx, ky, seed, a=1.0):
        """Veins along the zero lines of a sine wave (kx, ky whole cycles per tile: it tiles), meandering with the
        big noise and kinked like cracks by the abs() of the finer ones."""
        return np.sin(2 * np.pi * (kx * xx / w + ky * yy / h)
                      + a * (.9 * big + .6 * _noise(h, w, 300, 1200, seed) + .35 * mid + .02 * small))
    jit = _noise(h, w, 4, 16, 6)                       # feathered vein edges
    A, B, C = fam(3, 5, 11), fam(-3, 6, 12), fam(6, -8, 13, 1.5)
    mA = _smooth(_noise(h, w, 200, 800, 21), -0.6, 0.7)            # veins fade in and out along their run
    mB = _smooth(_noise(h, w, 200, 800, 22), 0.0, 1.0)
    nearA = np.exp(-(A / .5) ** 2)                     # branches grow off the main veins
    wv = .12 * (.5 + .5 * np.abs(_noise(h, w, 80, 400, 23)))       # width varies along a vein
    V_main = _ridge(A + .015 * jit, wv) * mA
    V_sec = _ridge(B + .04 * jit, wv * .7) * mB * (.35 + .65 * nearA)
    V_fine = _ridge(C + .05 * jit, .05) * nearA * _smooth(_noise(h, w, 60, 300, 24), 0.0, 1.0) * .8
    core = _ridge(A, wv * .3) * mA                     # darker cores in the thick veins
    gold = np.maximum(_ridge(A, .45) * mA, .6 * _ridge(B, .35) * mB) * _smooth(_noise(h, w, 150, 500, 9), -0.2, 1.0)
    cloud = _noise(h, w, 60, 600, 10)
    L = np.ones((h, w, 3), np.float32) * _lin('#EDE9E0') * (1 + .015 * cloud[..., None])
    for m, hx, k in ((gold, '#C8BC90', .6), (V_fine, '#B2AEA3', .7), (V_sec, '#A7A393', .85),
                     (V_main, '#9C9888', .9), (core, '#878370', .4)):
        a = np.clip(m * k, 0, 1)[..., None]
        L = L * (1 - a) + _lin(hx) * a
    L = np.clip(L, 0, 1)
    return np.where(L <= 0.0031308, L * 12.92, 1.055 * L ** (1 / 2.4) - 0.055).astype(np.float32)


def path():
    """Cached JPEG path, made when missing."""
    p = CACHE / f'ensuite_calacatta_v{VERSION}.jpg'
    if not p.exists():
        from lib import site_tex as ST                 # its writer: through a throw-away Blender image
        CACHE.mkdir(parents=True, exist_ok=True)
        ST._write(p, make())
    return str(p)


def mat():
    from lib import materials as M
    return M.image_mat('ensuite_calacatta', path(), size_m=SIZE_M, roughness=0.08)


if __name__ == '__main__':                            # preview without Blender
    import sys
    from PIL import Image
    im = make()
    Image.fromarray((np.clip(im, 0, 1) * 255).astype(np.uint8)).save(sys.argv[1] if len(sys.argv) > 1 else 'slab.jpg')

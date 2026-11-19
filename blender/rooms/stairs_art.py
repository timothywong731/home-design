"""Generated textures for the staircase - nothing here is cropped from the footage.

* print_1.jpg: stand-in for the lowest print (still t=778.0): landscape black / grey wash, dark hills and trees
  over pale water.  Fills the mount window (0.25 x 0.19 m).
* print_2..4.jpg: stand-ins for the three prints up the flight (spec/rooms/stairs.md section 6, still t=245.5):
  pale paper filling the whole sight (0.256 x 0.376 m) with a small grey-violet ink-and-wash boat and its
  reflection in the middle, varied per print.  No people.
* carpet_silver_col.jpg / _nrm.jpg: tileable 1.2 m plush pile, pale silver-grey with fibre speckle and crisp
  brushed strokes 3-9 cm wide x 8-20 cm long (stills t=241.5 / 247.0) and a pile normal map.

Run with the system Python (numpy + Pillow):

    python blender/rooms/stairs_art.py        -> blender/textures/art/stairs/
"""
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parents[1] / 'textures' / 'art' / 'stairs'
S = 3                                       # prints are drawn S times larger, then reduced
PAPER, INK, CHAR = (236, 234, 226), (91, 85, 102), (52, 52, 56)


def _noise(shape, lo, hi, rng, stretch=1.0):
    """Tileable band-passed noise (wavelengths lo..hi px across, `stretch` times longer along the rows
    axis), unit standard deviation."""
    fy, fx = np.meshgrid(np.fft.fftfreq(shape[0]), np.fft.fftfreq(shape[1]), indexing='ij')
    r = np.hypot(fx, fy * stretch)
    n = np.fft.ifft2(np.fft.fft2(rng.standard_normal(shape)) * ((r >= 1 / hi) & (r <= 1 / lo))).real
    return n / n.std()


def _blob(d, x, y, a, b, col, al):
    d.ellipse([x - a, y - b, x + a, y + b], fill=col + (al,))


def _on_paper(layers, w, h, seed):
    """Composite RGBA layers (drawn at S x) on the paper, reduce, add uneven pigment + paper grain."""
    im = Image.new('RGB', (w * S, h * S), PAPER)
    for lay in layers:
        im.paste(lay, (0, 0), lay)
    im = im.filter(ImageFilter.GaussianBlur(.6 * S)).resize((w, h), Image.LANCZOS)
    rng = np.random.default_rng(seed)
    k = 1 + 0.08 * _noise((h, w), 25, 110, rng) + 0.012 * _noise((h, w), 2, 6, rng)
    a = 255 - (255 - np.asarray(im, np.float32)) * np.clip(k, 0.6, 1.5)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def hills(seed, w=500, h=380):
    """S1: charcoal hills and trees along a far shore, pale water with their reflection, grey foreground."""
    r = random.Random(seed)
    W, H = w * S, h * S
    hz = H * 0.46                                                    # far shoreline
    wet, dry = Image.new('RGBA', (W, H), (0, 0, 0, 0)), Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(wet)
    for _ in range(40):                                              # grey sky and far hills, soft
        _blob(d, r.uniform(0, W), r.uniform(.05, .95) * hz, r.uniform(.15, .4) * W, r.uniform(.04, .12) * H,
              CHAR, r.randint(25, 70))
    for _ in range(30):                                              # grey streaks on the water and the near bank
        _blob(d, r.uniform(0, W), hz + r.uniform(.25, 1.0) * (H - hz), r.uniform(.15, .45) * W,
              r.uniform(.008, .03) * H, CHAR, r.randint(40, 110))
    wet = wet.filter(ImageFilter.GaussianBlur(5 * S))
    d = ImageDraw.Draw(dry)
    for _ in range(110):                                             # dark masses of hills / trees + reflections
        x = r.uniform(-.05, 1.05) * W
        t = 0.45 + 0.55 * abs(math.sin(3.1 * x / W + seed))
        a, b = r.uniform(.03, .09) * W, r.uniform(.03, .20) * H * t
        _blob(d, x, hz - .7 * b, a, .7 * b, CHAR, r.randint(150, 240))
        _blob(d, x, hz + .25 * b, a, .22 * b, CHAR, r.randint(50, 110))
    d.rectangle([0, hz - .008 * H, W, hz + .012 * H], fill=CHAR + (230,))           # the shoreline itself
    dry = dry.filter(ImageFilter.GaussianBlur(2.2 * S))
    return _on_paper([wet, dry], w, h, seed)


def boat(seed, w=256, h=376):
    """S2-S4: a small sailing boat and its reflection, grey-violet ink and wash, in the middle of bare paper."""
    r = random.Random(seed)
    W, H = w * S, h * S
    cx, cy = W * r.uniform(.46, .54), H * r.uniform(.49, .54)        # middle of the waterline
    L, hh, m = W * r.uniform(.17, .22), H * r.uniform(.020, .028), H * r.uniform(.13, .17)
    lean, f = r.uniform(-.12, .12) * m, r.choice((-1, 1))            # mast lean; which way the bow points
    wet, dry = Image.new('RGBA', (W, H), (0, 0, 0, 0)), Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(wet)
    for _ in range(12):                                              # faint wash of water round the hull
        _blob(d, cx + r.uniform(-1.4, 1.4) * L, cy + r.uniform(-.5, 4) * hh, r.uniform(.4, 1.1) * L,
              r.uniform(.3, .9) * hh, INK, r.randint(20, 45))
    d.polygon([(cx + .08 * L, cy - hh), (cx + lean, cy - m), (cx + f * .75 * L, cy - 1.6 * hh)], fill=INK + (95,))
    wet = wet.filter(ImageFilter.GaussianBlur(3 * S))
    d = ImageDraw.Draw(dry)
    d.polygon([(cx - f * L, cy - 1.3 * hh), (cx - f * .8 * L, cy), (cx + f * .75 * L, cy), (cx + f * 1.05 * L, cy - hh)],
              fill=INK + (235,))                                     # hull
    d.line([(cx, cy - hh), (cx + lean, cy - m)], fill=INK + (225,), width=S + 2)    # mast
    d.polygon([(cx - f * .8 * L, cy), (cx + f * .75 * L, cy), (cx + f * .5 * L, cy + 1.7 * hh),
               (cx - f * .6 * L, cy + 1.7 * hh)], fill=INK + (110,))  # reflection of the hull ...
    for i in range(5):                                               # ... and of the mast, broken by ripples
        y = cy + (1.9 + 1.5 * i) * hh
        d.line([(cx + r.uniform(-.1, .1) * L, y), (cx + r.uniform(-.1, .1) * L, y + hh)], fill=INK + (120 - 18 * i,),
               width=S + 1)
    dry = dry.filter(ImageFilter.GaussianBlur(1.3 * S))
    return _on_paper([wet, dry], w, h, seed)


def carpet(n=1024, base=(179, 176, 167)):
    """-> (colour, normal) images, tileable, n px = 1.2 m (1.17 mm / px)."""
    rng = np.random.default_rng(7)
    pile = _noise((n, n), 2, 4.5, rng)                               # tuft tips, 2.5-5 mm
    mott = _noise((n, n), 60, 200, rng)                              # soft shading, 7-25 cm
    # brushed strokes (pile lying the other way): 3-9 cm wide, 2.5 x longer along V (up the flight), crisp edges;
    # stretched 5 x they read as stripes on the 0.23 m treads
    patch = np.tanh(3 * _noise((n, n), 50, 160, rng, stretch=2.5))
    v = 1 + 0.08 * pile + 0.03 * mott + 0.08 * patch
    lin = (np.array(base, np.float32) / 255) ** 2.2
    col = np.clip(lin[None, None] * v[..., None], 0, 1) ** (1 / 2.2)
    hgt = 0.0006 * pile + 0.0003 * patch                             # metres
    px = 1.2 / n
    dx = (np.roll(hgt, -1, 1) - np.roll(hgt, 1, 1)) / (2 * px)
    dy = (np.roll(hgt, 1, 0) - np.roll(hgt, -1, 0)) / (2 * px)       # image rows run down, V runs up (OpenGL normal)
    nrm = np.dstack([-dx, -dy, np.ones_like(dx)])
    nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)
    to8 = lambda a: Image.fromarray(np.clip(a * 255 + 0.5, 0, 255).astype(np.uint8))
    return to8(col), to8(nrm * 0.5 + 0.5)


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    hills(11).save(OUT / 'print_1.jpg', quality=90)
    for i in range(1, 4):
        boat(11 + 7 * i).save(OUT / f'print_{i + 1}.jpg', quality=90)
    col, nrm = carpet()
    col.save(OUT / 'carpet_silver_col.jpg', quality=88)
    nrm.save(OUT / 'carpet_silver_nrm.jpg', quality=88)
    print('ART OK', OUT)

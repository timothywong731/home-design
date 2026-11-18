"""Shared helpers for the texture generators (system Python: numpy + cv2).
All images are float32 RGB in sRGB 0..1, row 0 = top. Every generator keeps textures periodic
(np.roll / modulo indexing / FFT noise) so they tile; check() measures the wrap seam."""
import json, os
import numpy as np, cv2

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.abspath(os.path.join(HERE, '..'))                      # blender/textures
SRC = os.path.abspath(os.path.join(TEX, '..', '..', 'build', 'texsrc'))
MANIFEST = os.path.join(TEX, 'manifest.json')
QUALITY = 88
_manifest = json.load(open(MANIFEST, encoding='utf8')) if os.path.exists(MANIFEST) else {}
_sources = {}   # file -> source note, written to SOURCES.md by make_all
_seams = {}     # file -> seam ratio measured before JPEG compression


# ---------------------------------------------------------------- colour
def hex3(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255.0


def lin(c):
    c = np.asarray(c, np.float32)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4).astype(np.float32)


def srgb(c):
    c = np.clip(np.asarray(c, np.float32), 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055).astype(np.float32)


def tohex(rgb):
    return '#%02X%02X%02X' % tuple(int(round(float(x) * 255)) for x in rgb)


def mean_hex(img):
    """Mean colour as the eye/renderer averages it: mean in linear light, reported as sRGB hex."""
    return tohex(srgb(lin(img).reshape(-1, 3).mean(0)))


def recolor(img, target_hex, contrast=1.0, sat=1.0):
    """Shift the texture so its linear-light mean equals target_hex, keeping (contrast-scaled)
    relative detail per channel. sat<1 pulls detail toward luminance-only (painted surfaces)."""
    L = np.maximum(lin(img), 1e-5)
    t = lin(hex3(target_hex))
    if sat < 1.0:
        g = L.mean(2, keepdims=True)
        L = g + (L - g) * sat
    rel = L / L.reshape(-1, 3).mean(0)
    rel = rel ** contrast
    out = rel * t
    for _ in range(4):                       # clipping moves the mean: re-normalise
        out = np.clip(out, 0, 1)
        out *= t / np.maximum(out.reshape(-1, 3).mean(0), 1e-6)
    return srgb(np.clip(out, 0, 1))


def equalize(img, frac=0.12, amount=0.85):
    """Remove large-scale light/dark drift (the thing that makes a tiled texture read as a grid):
    divide by a heavily (periodically) blurred copy of itself."""
    L = np.maximum(lin(img), 1e-5)
    low = blur(L, frac * max(img.shape[:2]))
    low = low / low.reshape(-1, 3).mean(0)
    return srgb(np.clip(L / low ** amount, 0, 1))


def lum(img):
    return img @ np.array([0.2126, 0.7152, 0.0722], np.float32)


# ---------------------------------------------------------------- io
def load(asset, m='Diffuse', size=None, rot=0):
    """Poly Haven source map as float RGB. rot = number of 90deg CCW turns (grain direction)."""
    im = cv2.imread(os.path.join(SRC, asset, m + '.jpg'), cv2.IMREAD_COLOR)
    if im is None:
        raise FileNotFoundError(f'{asset}/{m}.jpg - run gen/fetch.py first')
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    if rot:
        im = np.rot90(im, rot).copy()
        if m == 'nor_gl':                    # rotate the vector as well as the image
            x, y = im[..., 0] - 0.5, im[..., 1] - 0.5
            for _ in range(rot % 4):
                x, y = -y, x
            im[..., 0], im[..., 1] = x + 0.5, y + 0.5
    if size:
        im = resize(im, size)
    return im


def resize(im, size):
    """size = (w, h) or int. Area filter down, cubic up."""
    w, h = (size, size) if isinstance(size, int) else size
    interp = cv2.INTER_AREA if (w < im.shape[1] or h < im.shape[0]) else cv2.INTER_CUBIC
    return cv2.resize(im, (w, h), interpolation=interp)


def save(name, img, source):
    """Write blender/textures/<name>.jpg (quality 88). img float RGB or greyscale 0..1."""
    a = np.clip(img, 0, 1)
    a = (a * 255.0 + 0.5).astype(np.uint8)
    if a.ndim == 3:
        a = cv2.cvtColor(a, cv2.COLOR_RGB2BGR)
    fn = name + '.jpg'
    cv2.imwrite(os.path.join(TEX, fn), a, [cv2.IMWRITE_JPEG_QUALITY, QUALITY])
    _sources[fn] = source
    _seams[fn] = seam(np.clip(img, 0, 1))
    return fn


def orm(rough, metal=0.0, ao=1.0):
    """Pack glTF ORM: R = occlusion, G = roughness, B = metallic. Scalars broadcast."""
    r = np.asarray(rough, np.float32)
    shape = r.shape if r.ndim == 2 else np.asarray(metal).shape
    o = np.empty(shape + (3,), np.float32)
    o[..., 0], o[..., 1], o[..., 2] = ao, rough, metal
    return o


# ---------------------------------------------------------------- periodic noise / filters
def noise(h, w, lo, hi, seed, aniso=None):
    """Periodic band-limited noise, zero mean, unit std. Wavelengths lo..hi px.
    aniso = (angle_deg, stretch): features elongated along the angle by `stretch`."""
    rng = np.random.default_rng(seed)
    f = np.fft.fft2(rng.standard_normal((h, w)))
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.fftfreq(w)[None, :]
    if aniso:
        a, s = np.radians(aniso[0]), aniso[1]
        u = fx * np.cos(a) + fy * np.sin(a)          # along the feature direction
        v = -fx * np.sin(a) + fy * np.cos(a)
        r = np.sqrt((u * s) ** 2 + v ** 2)
    else:
        r = np.sqrt(fx ** 2 + fy ** 2)
    band = np.exp(-(r * lo) ** 2) * (1 - np.exp(-(r * hi) ** 2))
    n = np.real(np.fft.ifft2(f * band))
    return ((n - n.mean()) / (n.std() + 1e-9)).astype(np.float32)


def blur(a, sigma):
    """Periodic gaussian blur."""
    if sigma <= 0:
        return a
    k = int(sigma * 3) + 1
    p = np.pad(a, ((k, k), (k, k)) + ((0, 0),) * (a.ndim - 2), mode='wrap')
    return cv2.GaussianBlur(p, (0, 0), sigma)[k:-k, k:-k]


def normal(height, px_x, px_y=None, strength=1.0):
    """Tangent-space normal map (OpenGL, +Y up) from a height field in metres.
    px_x / px_y = metres per pixel. Periodic central differences keep it seamless."""
    px_y = px_y or px_x
    dx = (np.roll(height, -1, 1) - np.roll(height, 1, 1)) / (2 * px_x)
    drow = (np.roll(height, -1, 0) - np.roll(height, 1, 0)) / (2 * px_y)
    nx, ny = -dx * strength, drow * strength          # v runs up, rows run down
    nz = np.ones_like(nx)
    l = np.sqrt(nx * nx + ny * ny + nz * nz)
    return np.dstack([nx / l, ny / l, nz / l]) * 0.5 + 0.5


def renorm(n):
    """Re-normalise a normal-map image after resizing/blending."""
    v = n * 2 - 1
    v /= np.maximum(np.linalg.norm(v, axis=2, keepdims=True), 1e-6)
    return v * 0.5 + 0.5


def flatten(n, k):
    """Scale normal-map strength by k (k<1 flattens)."""
    v = n * 2 - 1
    v[..., :2] *= k
    v[..., 2] = np.sqrt(np.clip(1 - (v[..., :2] ** 2).sum(2), 0.0, 1))
    return renorm(v * 0.5 + 0.5)


def seam(img):
    """Wrap-seam visibility (x, y): mean abs step across the wrap line divided by the 99.5th
    percentile of the same step across every interior parallel line (the strongest lines the
    texture already contains: grout edges, board joints, grain). <= 1 means the wrap is no more
    of a discontinuity than those; > 1 means it is the sharpest line in the texture - look at it."""
    a = img if img.ndim == 3 else img[..., None]
    cols = np.abs(a - np.roll(a, 1, 1)).mean((0, 2))          # index 0 = the wrap
    rows = np.abs(a - np.roll(a, 1, 0)).mean((1, 2))
    return (round(float(cols[0] / (np.percentile(cols[1:], 99.5) + 1e-6)), 2),
            round(float(rows[0] / (np.percentile(rows[1:], 99.5) + 1e-6)), 2))


# ---------------------------------------------------------------- manifest
def reg(key, base, size, nrm=None, orm=None, rough=0.5, metal=0.0, nrm_strength=1.0, target=None, **extra):
    """Record a textured material for blender/lib/materials.py. size = real-world (w, h) in metres
    of one texture repeat. target = spec hex the base was matched to (for the report).
    base=None registers an auxiliary map set (key starts with '_') shared by constant-colour
    materials (brushed metal, paint stipple, obscure glass)."""
    e = dict(size_m=[round(size[0], 5), round(size[1], 5)], rough=rough, metal=metal)
    if base:
        img = cv2.cvtColor(cv2.imread(os.path.join(TEX, base)), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
        e.update(base=base, mean=mean_hex(img), px=[img.shape[1], img.shape[0]], seam=_seams.get(base) or seam(img))
    else:
        e.update(seam=_seams.get(nrm or orm, (0, 0)))
    if nrm:
        e.update(nrm=nrm, nrm_strength=nrm_strength)
    if orm:
        e['orm'] = orm
    if target:
        e['target'] = target
    e.update(extra)
    _manifest[key] = e
    print(f"{key:24s} mean {e.get('mean', '-'):8s} target {target or '-':8s} {e.get('px', '')} size {e['size_m']} seam {e['seam']}")


def write_manifest():
    json.dump(_manifest, open(MANIFEST, 'w', encoding='utf8'), indent=1, sort_keys=True)
    return _manifest, _sources

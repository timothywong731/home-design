"""Timber textures. Convention: grain / plank length runs along V (image vertical), so on a floor
box-mapped with materials.uv_box() the planks run along world Y; pass rotate=True for X."""
import numpy as np
from common import (equalize, load, resize, save, reg, recolor, lin, srgb, hex3, lum, blur, normal, orm,
                    renorm, flatten, noise)

PH = 'Poly Haven CC0: '


# ---------------------------------------------------------------- plain veneers
# key: (asset, rot90s so grain is vertical, hex, contrast, declared size m, roughness, normal strength)
PLAIN = {
    # light straw oak door leaves (living/kitchen/utility/dining, pocket door): frames f_0741 / f_0499 read far lighter and
    # yellower than the room specs' #B08A56 (dining.md: #CFB682); fine straight grain with a faint cathedral
    'oak_door':           ('oak_veneer_03', 1, '#C6AC78', 0.9, 1.2, 0.45, 0.5),
    'oak_rustic':         ('oak_veneer_01', 0, '#A98850', 1.1, 1.2, 0.50, 1.0),   # waxed rustic oak TV unit
    'oak_light':          ('oak_veneer_01', 0, '#C9A877', 0.8, 1.2, 0.45, 0.5),   # bare oak carcass / filler strip
    'oak_table':          ('oak_veneer_01', 0, '#5E4631', 1.1, 1.2, 0.30, 0.8),   # dining table top, coffee table
    'dark_oak_antique':   ('oak_veneer_01', 0, '#3A2A1E', 1.1, 1.2, 0.30, 0.8),   # antique dark oak/walnut furniture, fire surround
    'dark_joinery':       ('black_walnut_veneer_01', 1, '#40342C', 1.3, 1.0, 0.25, 0.5),  # Jacobean-stain skirting/architraves/window timber
    'mahogany':           ('sapele_veneer_02', 1, '#4A2216', 1.2, 1.0, 0.12, 0.3),  # gloss-varnished red mahogany (inner doors, newel, handrail)
    'mahogany_dark':      ('sapele_veneer_02', 1, '#3B241A', 1.2, 1.0, 0.25, 0.4),  # dark mahogany show-wood (chairs, sofa frame, bookcase, stool)
    'mahogany_mid':       ('sapele_veneer_02', 1, '#6A452C', 1.2, 1.0, 0.25, 0.4),  # mid-brown polished tops (lamp table, bookcase top, barometer)
    'hardwood_threshold': ('black_walnut_veneer_01', 1, '#54351F', 1.3, 1.0, 0.40, 0.5),  # door threshold bars
}
# painted ash-grain shaker cabinets: paint colour, open grain kept in the normal map
PAINTED = {
    'navy_cabinet': ('#23252D', 0.40),
    'grey_cabinet': ('#BDBDB8', 0.40),
}


def _shared_normal(asset, rot, px=1024):
    fn = f'wood_{asset}_nrm'
    return save(fn, renorm(load(asset, 'nor_gl', px, rot)), PH + f'{asset} nor_gl, resized')


def plain():
    nrm = {}
    for key, (asset, rot, hx, con, size, rough, ns) in PLAIN.items():
        if asset not in nrm:
            nrm[asset] = _shared_normal(asset, rot)
        img = recolor(equalize(load(asset, 'Diffuse', 1024, rot)), hx, contrast=con)
        base = save(key + '_col', img, PH + f'{asset} Diffuse, recoloured to {hx}')
        reg(key, base, (size, size), nrm=nrm[asset], rough=rough, nrm_strength=ns, target=hx)
    ash_n = _shared_normal('ash_veneer', 1)
    for key, (hx, rough) in PAINTED.items():
        img = recolor(equalize(load('ash_veneer', 'Diffuse', 1024, 1)), hx, contrast=0.45, sat=0.2)
        base = save(key + '_col', img, PH + f'ash_veneer Diffuse, desaturated and recoloured to {hx}')
        reg(key, base, (1.0, 1.0), nrm=ash_n, rough=rough, nrm_strength=1.0, target=hx)


# ---------------------------------------------------------------- plank layouts
def planks(src, W, H, ncol, len_px, seed, var=0.06, stagger=None, hue=0.25):
    """Lay `ncol` columns of planks running down the image, cut from the (tileable) source `src`
    (already at canvas pixel pitch). len_px = (min, max) plank length, or a fixed int with
    `stagger` = per-column start offsets (fractions of the length). Wraps in both directions.
    Returns colour (sRGB), dx, dy = pixel distance to the nearest long edge / end joint."""
    rng = np.random.default_rng(seed)
    out = np.zeros((H, W, 3), np.float32)
    dx = np.zeros((H, W), np.float32)
    dy = np.zeros((H, W), np.float32)
    edges = np.linspace(0, W, ncol + 1).round().astype(int)
    sh, sw = src.shape[:2]
    for c in range(ncol):
        x0, x1 = edges[c], edges[c + 1]
        cw = x1 - x0
        if isinstance(len_px, int):
            n = H // len_px
            cuts = (np.arange(n) * len_px + int(stagger[c] * len_px)) % H
        else:
            ls = []
            while sum(ls) < H:
                ls.append(rng.uniform(*len_px))
            ls = np.array(ls) * H / sum(ls)
            cuts = (np.cumsum(ls) + rng.uniform(0, H)).astype(int) % H
        cuts = np.sort(cuts)
        xs = np.arange(cw)
        for i, r0 in enumerate(cuts):
            r1 = cuts[(i + 1) % len(cuts)]
            n = (r1 - r0) % H or H
            rows = (r0 + np.arange(n)) % H
            oy, ox = rng.integers(0, sh), rng.integers(0, sw)
            strip = src[(oy + np.arange(n)) % sh][:, (ox + xs) % sw]
            if rng.random() < 0.5:
                strip = strip[::-1, ::-1]                     # turn the board end for end
            g = np.exp(rng.normal(0, var)) * (1 + rng.normal(0, var * hue, 3))
            out[rows, x0:x1] = srgb(np.clip(lin(strip) * g, 0, 1))
            d_end = np.minimum(np.arange(n), n - 1 - np.arange(n)).astype(np.float32)
            dy[rows, x0:x1] = d_end[:, None]
            dx[rows, x0:x1] = np.minimum(xs, cw - 1 - xs)[None, :]
    return out, dx, dy


def knots(img, n, px, seed, hx='#6B4E32', size=(0.006, 0.016), dark=0.55):
    """Dark knots (and a short filled crack through some) scattered periodically. px = (mx, my) m/px."""
    rng = np.random.default_rng(seed)
    H, W = img.shape[:2]
    L = lin(img)
    k = lin(hex3(hx)) * dark
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    for _ in range(n):
        cx, cy = rng.uniform(0, W), rng.uniform(0, H)
        r = rng.uniform(*size)
        ddx = ((xx - cx + W / 2) % W - W / 2) * px[0]
        ddy = ((yy - cy + H / 2) % H - H / 2) * px[1]
        d = np.sqrt(ddx ** 2 + (ddy * 0.7) ** 2) / r
        core = np.exp(-d ** 4)                                # dark knot
        halo = 0.35 * np.exp(-((d - 1.5) / 0.5) ** 2)          # swirl of darker grain round it
        a = np.clip(core * 0.92 + halo, 0, 1)
        if rng.random() < 0.6:                                # filled crack along the grain
            cl = rng.uniform(0.03, 0.12)
            a = np.maximum(a, 0.85 * np.exp(-(ddx / 0.0012) ** 2 - (ddy / cl) ** 4))
        L = L * (1 - a[..., None]) + k * a[..., None]
    return srgb(L)


def grain_height(img, sigma_px):
    """Pseudo height from the print: fine luminance detail (dark pores sit low). Unit std."""
    g = lum(img)
    g = g - blur(g, sigma_px)
    return g / (g.std() + 1e-6)


def oak_floor():
    """Engineered oak, rustic grade: boards 220 mm wide, 1.2-2.2 m long, micro-bevelled, satin.
    Pale grey-beige with fine straight (quarter-sawn) grain and sparse brown knots, as filmed
    (f_0064, f_0741): low figure contrast, per-channel std ~8/255."""
    W, H, wm, hm = 2048, 2048, 2.2, 4.4
    px = (wm / W, hm / H)
    hx = '#C4B790'                                            # hallway.md #C9B48A, greyed toward the frame samples
    src = recolor(equalize(load('washed_grey_oak_veneer', 'Diffuse', None, 1)), hx, contrast=0.8)
    src = resize(src, (int(1.83 / px[0]), int(1.83 / px[1])))
    sk = noise(src.shape[0], src.shape[1], 5, 36, 13, aniso=(90, 30))     # rustic grade: soft darker streaks along the grain
    src = srgb(lin(src) * (1 - 0.06 * np.clip(sk, 0, 2.5))[..., None])
    col, dx, dy = planks(src, W, H, 10, (1.2 / px[1], 2.2 / px[1]), seed=11, var=0.035, hue=0.2)
    col = recolor(col, hx)
    col = knots(col, 11, px, seed=12, dark=1.0)               # ~1 knot per 2-3 boards, brown not black
    d = np.minimum(dx * px[0], dy * px[1])                    # metres to the board edge
    bevel = np.clip(1 - d / 0.0016, 0, 1)                     # 1.6 mm micro-bevel each side
    col = srgb(lin(col) * (1 - 0.45 * bevel ** 2)[..., None])
    gh = grain_height(col, 3)
    height = -0.0006 * bevel + 0.00003 * gh
    rough = np.clip(0.50 + 0.04 * blur(gh, 1) + 0.25 * bevel, 0.2, 0.9)
    print('oak_floor std/255', (col * 255).reshape(-1, 3).std(0).round(1))
    b = save('oak_floor_col', col, PH + 'washed_grey_oak_veneer Diffuse cut into 220 mm boards by gen/woods.py, knots synthesised')
    n = save('oak_floor_nrm', normal(height, *px), 'synthesised (board bevels + grain) gen/woods.py')
    o = save('oak_floor_orm', orm(rough), 'synthesised gen/woods.py')
    reg('oak_floor', b, (wm, hm), nrm=n, orm=o, rough=0.50, target=hx, note='boards 220 mm along V')


def wood_tile_floor():
    """Wood-effect porcelain planks 200 x 1200, 3.5 mm light grout, irregular third-bond.
    Weathered grey-brown barn-wood print (f_0388, f_0499): streaky dark grain, pale worn patches,
    clear tone steps from plank to plank."""
    grout_m, pw, pl = 0.0035, 0.200, 1.200
    W, H = 1024, 2048
    wm, hm = 6 * (pw + grout_m), 3 * (pl + grout_m)
    px = (wm / W, hm / H)
    hx, dark, light = '#8E8676', '#5C564B', '#ABA392'          # kitchen.md 3.5: base / dark grain / light streaks
    a = load('smoked_walnut_veneer', 'Diffuse', None, 1)
    b = load('washed_grey_oak_veneer', 'Diffuse', None, 1)
    src = recolor(0.45 * a + 0.55 * b, hx, contrast=1.1, sat=0.4)
    src = resize(src, (int(1.0 / px[0]), int(1.0 / px[1])))
    sh, sw = src.shape[:2]
    st = noise(sh, sw, 4, 16, 24, aniso=(90, 40))             # long dark streaks along the plank, 5-15 mm wide
    sm = noise(sh, sw, 40, 150, 26, aniso=(90, 6))            # smoky weathered patches the streaks gather in
    pt = noise(sh, sw, 30, 120, 25, aniso=(90, 10))           # broad worn / pale bands
    ad = (np.clip((0.55 * st + 1.25 * sm - 0.35) / 2.0, 0, 1) ** 1.2)[..., None]
    al = (0.7 * np.clip((pt - 0.2) / 1.8, 0, 1))[..., None]
    L, base = lin(src), lin(hex3(hx))
    L = L * (1 + al * (lin(hex3(light)) / base - 1)) * (1 + ad * (lin(hex3(dark)) / base * 0.8 - 1))
    src = srgb(np.clip(L, 0, 1))
    col, dx, dy = planks(src, W, H, 6, H // 3, seed=21, var=0.08, stagger=[0.0, 0.34, 0.71, 0.12, 0.60, 0.88], hue=0.12)
    col = recolor(col, hx)
    col = knots(col, 10, px, seed=22, hx=dark, size=(0.006, 0.012))
    d = np.minimum(dx * px[0], dy * px[1])
    g = np.clip(1 - (d - grout_m / 2) / 0.0012, 0, 1)         # 1 in the joint, soft tile edge
    edge = np.clip(1 - (d - grout_m / 2) / 0.003, 0, 1)        # cushioned tile edge
    grout = hex3('#CFCABB') * (1 + 0.03 * noise(H, W, 2, 8, 23))[..., None]
    col = col * (1 - g[..., None]) + grout * g[..., None]
    height = -0.0008 * g - 0.0003 * edge ** 2 + 0.00003 * grain_height(col, 3) * (1 - g)
    rough = 0.45 + 0.4 * g
    bf = save('wood_tile_floor_col', col, PH + 'smoked_walnut_veneer + washed_grey_oak_veneer Diffuse, desaturated, weathered (synthesised streaks / patches), cut into 200x1200 tiles with grout by gen/woods.py')
    n = save('wood_tile_floor_nrm', normal(height, *px), 'synthesised (grout joints) gen/woods.py')
    o = save('wood_tile_floor_orm', orm(rough), 'synthesised gen/woods.py')
    reg('wood_tile_floor', bf, (wm, hm), nrm=n, orm=o, rough=0.45, target=hx, note='planks 200x1200 along V, grout #CFCABB')


def oak_worktop():
    """Oiled oak stave (butcher-block) worktop: staves 40 mm wide, 0.3-0.9 m long, strong variation."""
    W, H, wm, hm = 1024, 1024, 1.0, 1.8
    px = (wm / W, hm / H)
    src = recolor(load('oak_veneer_01', 'Diffuse'), '#B38E58', contrast=0.9)
    src = resize(src, (int(1.83 / px[0]), int(1.83 / px[1])))
    col, dx, dy = planks(src, W, H, 25, (0.3 / px[1], 0.9 / px[1]), seed=31, var=0.11, hue=0.1)
    col = recolor(col, '#B38E58')
    glue = np.clip(1 - np.minimum(dx, dy * px[1] / px[0]) / 1.0, 0, 1)
    col = srgb(lin(col) * (1 - 0.3 * glue)[..., None])
    b = save('oak_worktop_col', col, PH + 'oak_veneer_01 Diffuse cut into 40 mm staves by gen/woods.py')
    reg('oak_worktop', b, (wm, hm), rough=0.42, target='#B38E58', note='staves 40 mm along V')


def main():
    plain()
    oak_floor()
    wood_tile_floor()
    oak_worktop()

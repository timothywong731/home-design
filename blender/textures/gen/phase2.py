"""Phase-2 textures: upper-floor carpets and tiles, site paving, brick, fences, facade and roof coverings.
All synthesised (no third-party content); wood_tile_floor_dark is a recolour of this project's own wood_tile_floor.
Conventions: brick / tile courses, slate courses and deck boards' short side run along U; boards, planks and
rafters run along V (uv_box: V = +Y on floors, +Z on walls)."""
import os
import numpy as np, cv2
from common import TEX, save, reg, lin, srgb, hex3, blur, normal, orm, noise, recolor
import tiles

SYN = 'synthesised by gen/phase2.py'


def _grid(W, H, wm, hm):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    return (x + 0.5) * wm / W, (y + 0.5) * hm / H


def _mix(tones, n, rng, var):
    """n unit colours (linear) drawn from tones [(hex, weight)...] with +-var value jitter."""
    hx, w = zip(*tones)
    pick = rng.choice(len(hx), n, p=np.array(w, float) / sum(w))
    return np.stack([lin(hex3(h)) for h in hx])[pick] * (1 + rng.normal(0, var, (n, 1))).astype(np.float32)


def bond(key, unit, joint, nx, ny, px, tones, joint_hex, seed, shift=0.5, var=0.05, speck=0.03, depth=0.002,
         riven=0.0, rough=0.9, blotch=0.0, soft=0.002, note='', nrm_key=None):
    """nx x ny units of unit=(w, h) metres (w along U) with `joint` metre joints; row j is shifted by j*shift units
    (ny * shift must be whole). tones [(hex, weight)...]; riven = cleft relief in metres; blotch = soot / weathering."""
    W, H = px
    pw, ph = unit[0] + joint, unit[1] + joint
    wm, hm = nx * pw, ny * ph
    rng = np.random.default_rng(seed)
    x, y = _grid(W, H, wm, hm)
    j = np.floor(y / ph).astype(int) % ny
    xs = (x + ((j * shift) % 1.0) * pw) % wm
    i = np.floor(xs / pw).astype(int) % nx
    lx, ly = xs - i * pw, y - j * ph
    d = np.minimum(np.minimum(lx, pw - lx), np.minimum(ly, ph - ly)) - joint / 2          # > 0 inside the unit
    aa = 0.6 * max(wm / W, hm / H)
    g = np.clip(0.5 - d / (2 * aa), 0, 1)
    tid = j * nx + i
    col = _mix(tones, nx * ny, rng, var)[tid]
    col *= (1 + speck * noise(H, W, 1.5, 5, seed + 1) + 0.5 * speck * noise(H, W, 12, 60, seed + 2))[..., None]
    if blotch:
        col *= (1 - blotch * np.clip(noise(H, W, 150, 700, seed + 3) - 0.2, 0, 2))[..., None]
    gcol = lin(hex3(joint_hex)) * (1 + 0.05 * noise(H, W, 2, 6, seed + 4))[..., None]
    col = srgb(np.clip(col * (1 - g[..., None]) + gcol * g[..., None], 0, 1))
    face = np.clip(d / soft, 0, 1)                                                       # 0 at the arris, 1 on the face
    height = depth * (face - 1) * (1 - g) - depth * g
    if riven:
        height += riven * (noise(H, W, 20, 120, seed + 5) + 0.4 * noise(H, W, 4, 14, seed + 6)) * face
    b = save(key + '_col', col, SYN)
    n = nrm_key + '_nrm.jpg' if nrm_key else save(key + '_nrm', normal(height, wm / W, hm / H), SYN)
    reg(key, b, (wm, hm), nrm=n, rough=rough, target=tones[0][0], note=note or f'{int(unit[0]*1000)}x{int(unit[1]*1000)} mm units, joint {joint_hex}')
    return n


def herringbone(key, tones, joint_hex, seed, W=0.1, px=1024, joint=0.003, var=0.06):
    """90-degree herringbone of 2W x W pavers; period 4W both ways (repeated 2 x 2 for variety)."""
    N, R = px, 8
    rng = np.random.default_rng(seed)
    x, y = _grid(N, N, R, R)                                           # in units of W
    i, j = np.floor(x).astype(int), np.floor(y).astype(int)
    d4 = (i + j) % 4
    i0 = np.where(d4 == 1, i - 1, i)
    j0 = np.where(d4 == 3, j - 1, j)
    hor = d4 < 2
    lx, ly = x - i0, y - j0
    d = np.where(hor, np.minimum(np.minimum(lx, 2 - lx), np.minimum(ly, 1 - ly)),
                 np.minimum(np.minimum(lx, 1 - lx), np.minimum(ly, 2 - ly))) * W - joint / 2
    g = np.clip(0.5 - d / (1.2 * R * W / N), 0, 1)
    tid = (i0 % R) * R + (j0 % R)
    col = _mix(tones, R * R, rng, var)[tid] * (1 + 0.04 * noise(N, N, 1.5, 5, seed + 1))[..., None]
    gcol = lin(hex3(joint_hex)) * (1 + 0.05 * noise(N, N, 2, 6, seed + 2))[..., None]
    col = srgb(np.clip(col * (1 - g[..., None]) + gcol * g[..., None], 0, 1))
    height = 0.002 * (np.clip(d / 0.004, 0, 1) - 1)
    b = save(key + '_col', col, SYN)
    n = save(key + '_nrm', normal(height, R * W / N), SYN)
    reg(key, b, (R * W, R * W), nrm=n, rough=0.9, target=tones[0][0], note='200x100 pavers, 90-degree herringbone')


def boards(key, hx, bw, gap, n, px, seed, streak_hex=None, streak=0.0, var=0.05, lap=0.0, groove=0.0, vjoint=0.0,
           rough=0.8, nrm_key=None, hm=1.6):
    """n boards of width bw (+ gap) running along V. lap = feather-edge overlap step (m), groove = fine ridges
    (composite decking), vjoint = V-groove depth between tongue-and-groove boards; gap > 0 = open dark gap."""
    W, H = px
    pw = bw + gap
    wm = n * pw
    rng = np.random.default_rng(seed)
    x, y = _grid(W, H, wm, hm)
    i = np.floor(x / pw).astype(int) % n
    lx = x - np.floor(x / pw) * pw
    tone = (1 + rng.normal(0, var, n))[i]
    grain = noise(H, W, 3, 12, seed + 1, aniso=(90, 30)) * 0.05 + noise(H, W, 30, 200, seed + 2, aniso=(90, 6)) * 0.04
    col = lin(hex3(hx)) * (tone * (1 + grain))[..., None]
    if streak:
        a = (streak * np.clip(noise(H, W, 8, 60, seed + 3, aniso=(90, 25)) - 0.3, 0, 1.5))[..., None]
        col = col * (1 - a) + lin(hex3(streak_hex)) * a
    in_gap = np.clip((lx - bw) / max(wm / W, 1e-6) + 0.5, 0, 1) if gap else np.zeros_like(lx)
    col = col * (1 - 0.85 * in_gap[..., None])
    height = np.zeros_like(lx)
    if lap:
        height += lap * (1 - lx / pw)                                # thick edge at lx = 0, thin at the next board
    if groove:
        height += groove * 0.5 * np.cos(2 * np.pi * lx / 0.008) * (lx < bw)
    if vjoint:
        height -= vjoint * np.clip(1 - np.minimum(lx, pw - lx) / 0.004, 0, 1)
    height -= 0.004 * in_gap
    b = save(key + '_col', srgb(np.clip(col, 0, 1)), SYN)
    nk = nrm_key or key
    nf = nk + '_nrm.jpg'
    if nk == key:
        nf = save(key + '_nrm', normal(height + 0.00015 * grain / 0.05, wm / W, hm / H), SYN)
    reg(key, b, (wm, hm), nrm=nf, rough=rough, target=hx, note=f'{int(bw*1000)} mm boards along V')


def speckle(key, hx, size, px, seed, amp=0.08, lo=1.5, hi=6, mott=0.05, relief=0.0006, rough=0.9, extra=None, sheen=0.0,
            nrm_file=None):
    """Granular surface (asphalt, felt, soil, carpet, sheet vinyl): fine speckle + large mottling."""
    N = px
    f = noise(N, N, lo, hi, seed)
    col = lin(hex3(hx)) * ((1 + amp * f) * (1 + mott * noise(N, N, 150, 700, seed + 1)))[..., None]
    if extra is not None:
        col = extra(col, N)
    b = save(key + '_col', recolor(srgb(np.clip(col, 0, 1)), hx), SYN)
    n = nrm_file or save(key + '_nrm', normal(relief * f, size / N), SYN)
    kw = dict(sheen=sheen) if sheen else {}
    reg(key, b, (size, size), nrm=n, rough=rough, target=hx, **kw)


def grass():
    N, P = 1024, 2.0
    blades = noise(N, N, 1.5, 5, 301, aniso=(80, 5)) + 0.7 * noise(N, N, 1.5, 5, 302, aniso=(105, 5))
    clump = noise(N, N, 40, 200, 303)
    t = np.clip(0.5 + 0.22 * blades + 0.18 * clump, 0, 1)[..., None]
    col = lin(hex3('#4F6B36')) * (1 - t) + lin(hex3('#8CA765')) * t
    worn = np.clip(noise(N, N, 200, 800, 304) - 1.3, 0, 1)[..., None] * 0.6        # a few worn soil patches
    col = col * (1 - worn) + lin(hex3('#3F3A30')) * worn
    b = save('grass_col', recolor(srgb(col), '#6E8B4F'), SYN)
    n = save('grass_nrm', normal(0.004 * blades, P / N), SYN)
    reg('grass', b, (P, P), nrm=n, rough=1.0, target='#6E8B4F', note='long rough lawn')


def slates(key, hx, seed, nrm_key=None):
    """Roof slates: 250 mm gauge courses along U, 300 mm slates in half bond; each course is a wedge (thick tail)."""
    N, wm, hm = 1024, 2.4, 2.0
    gw, sw = 0.25, 0.30
    rng = np.random.default_rng(seed)
    x, y = _grid(N, N, wm, hm)
    j = np.floor(y / gw).astype(int) % 8
    xs = (x + (j % 2) * sw / 2) % wm
    i = np.floor(xs / sw).astype(int) % 8
    lx, ly = xs - i * sw, y - np.floor(y / gw) * gw                    # ly = 0 at the top of the course (image rows run down)
    tone = (1 + rng.normal(0, 0.07, 64))[j * 8 + i]
    col = lin(hex3(hx)) * (tone * (1 + 0.04 * noise(N, N, 2, 8, seed + 1) + 0.05 * noise(N, N, 30, 200, seed + 2, aniso=(90, 4))))[..., None]
    side = np.clip(1 - np.minimum(lx, sw - lx) / 0.003, 0, 1)
    tail = np.clip(1 - (gw - ly) / 0.006, 0, 1)                         # shadow line under each tail
    col = col * (1 - 0.55 * np.maximum(side, tail))[..., None]
    b = save(key + '_col', recolor(srgb(np.clip(col, 0, 1)), hx), SYN)
    nf = (nrm_key or key) + '_nrm.jpg'
    if not nrm_key:
        nf = save(key + '_nrm', normal(0.006 * ly / gw - 0.002 * side, wm / N, hm / N), SYN)
    reg(key, b, (wm, hm), nrm=nf, rough=0.7, target=hx, note='courses along U; V must run up the slope')


def chequer():
    """Five-bar durbar tread plate: groups of five lozenge bars, alternating direction cell by cell."""
    N, P, c = 1024, 0.4, 0.05
    x, y = _grid(N, N, P, P)
    i, j = np.floor(x / c).astype(int), np.floor(y / c).astype(int)
    u, v = x - i * c - c / 2, y - j * c - c / 2
    sw = (i + j) % 2 == 1
    a, b_ = np.where(sw, v, u), np.where(sw, u, v)                       # a across the bars, b_ along them
    k = np.clip(np.round(a / 0.008), -2, 2)
    bar = np.clip(1 - np.abs(a - k * 0.008) / 0.0022, 0, 1) * np.clip((0.019 - np.abs(b_)) / 0.004, 0, 1)
    h = np.clip(bar * 1.6, 0, 1)
    col = lin(hex3('#2E3033')) * ((1 + 0.25 * h) * (1 + 0.04 * noise(N, N, 3, 20, 311)))[..., None]
    bcol = save('steel_chequer_plate_col', srgb(np.clip(col, 0, 1)), SYN)
    n = save('steel_chequer_plate_nrm', normal(0.0016 * h, P / N), SYN)
    reg('steel_chequer_plate', bcol, (P, P), nrm=n, rough=0.42, target='#2E3033', note='five-bar tread plate, painted black')


def calacatta():
    """Polished Calacatta-gold porcelain slabs 1.2 x 1.2: bold gold-beige bands and patches with grey veins (blue
    en-suite, v3 f_0387 / f_0391 / f_0405), 2 mm joint on the repeat edge."""
    N, P = 1024, 1.2
    a = 0.80 * tiles.veins(N, N, 321, n=7, angle=38, length=(0.5, 1.2), width=8.0)
    g = 0.85 * tiles.veins(N, N, 322, n=5, angle=30, length=(0.5, 1.1), width=18.0)
    g = np.maximum(g, 0.45 * blur(np.clip(tiles.veins(N, N, 324, n=4, angle=34, length=(0.3, 0.6), width=60.0), 0, 1), 25))
    base = lin(hex3('#EDE9E0')) * (1 + 0.012 * noise(N, N, 60, 500, 323))[..., None]
    col = base * (1 - a[..., None]) + lin(hex3('#9C9A93')) * a[..., None]
    col = col * (1 - g[..., None]) + lin(hex3('#B9A06A')) * g[..., None]
    e = max(1, int(round(0.001 * N / P)))
    col[:e], col[-e:], col[:, :e], col[:, -e:] = (lin(hex3('#D9D6CE')),) * 4
    b = save('porcelain_calacatta_slab_col', srgb(np.clip(col, 0, 1)), SYN)
    reg('porcelain_calacatta_slab', b, (P, P), rough=0.06, target='#EDE9E0', note='1.2 m slabs, gold bands #B9A06A, veins #9C9A93')


def underside():
    """Roof seen from the eaves: black felt between softwood rafters (50 mm at 400 centres, along V)."""
    N, wm, hm = 512, 1.2, 1.2
    x, y = _grid(N, N, wm, hm)
    lx = x % 0.4
    r = np.clip((0.025 - np.abs(lx - 0.2)) / 0.002 + 0.5, 0, 1)[..., None]
    felt = lin(hex3('#2E2D2C')) * (1 + 0.08 * noise(N, N, 2, 8, 331))[..., None]
    wood = lin(hex3('#B59A6C')) * (1 + 0.07 * noise(N, N, 3, 12, 332, aniso=(90, 30)))[..., None]
    b = save('roof_underside_col', srgb(np.clip(felt * (1 - r) + wood * r, 0, 1)), SYN)
    reg('roof_underside', b, (wm, hm), rough=0.9, target='#2E2D2C', note='rafters along V at 0.4 m centres')


def plank_dark():
    """Basement: the ground-floor wood-effect porcelain plank, darker grey-brown print (#7B6F5C)."""
    im = cv2.cvtColor(cv2.imread(os.path.join(TEX, 'wood_tile_floor_col.jpg')), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
    b = save('wood_tile_floor_dark_col', recolor(im, '#7B6F5C', contrast=1.25), 'wood_tile_floor_col.jpg recoloured by gen/phase2.py')
    e = dict(reg.__globals__['_manifest']['wood_tile_floor'])
    reg('wood_tile_floor_dark', b, e['size_m'], nrm=e['nrm'], orm=e['orm'], rough=0.5, target='#7B6F5C', note='planks 200x1200 along V')


def plank_grey():
    """Shed workshop floor: the wood-effect plank in dark grey (#6B6A66, shed.md 4; v2 f_0281 / f_0287)."""
    im = cv2.cvtColor(cv2.imread(os.path.join(TEX, 'wood_tile_floor_col.jpg')), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
    b = save('wood_tile_floor_grey_col', recolor(im, '#6B6A66', contrast=1.2, sat=0.2), 'wood_tile_floor_col.jpg recoloured by gen/phase2.py')
    e = dict(reg.__globals__['_manifest']['wood_tile_floor'])
    reg('wood_tile_floor_grey', b, e['size_m'], nrm=e['nrm'], orm=e['orm'], rough=0.5, target='#6B6A66', note='planks 200x1200 along V')


def main():
    # ---- upper-floor carpets (one shared pile normal map: carpet_mink_nrm)
    for key, hx, seed in (('carpet_silver_beige', '#A9A397', 201), ('carpet_pale', '#CFCAC3', 203),
                          ('carpet_grey_twist', '#B9B4AB', 205), ('carpet_grey', '#CFC9BC', 207)):
        speckle(key, hx, 1.0, 1024, seed, amp=0.09, lo=2, hi=7, mott=0.05, rough=1.0, sheen=0.3, nrm_file='carpet_mink_nrm.jpg')
    speckle('vinyl_grey_sheet', '#8C8A85', 1.5, 512, 211, amp=0.02, lo=2, hi=8, mott=0.07, relief=0.00005, rough=0.6)
    # ---- tiles
    bond('porcelain_pale', (0.4, 0.8), 0.003, 3, 3, (1024, 2048), [('#CFCBC2', 1)], '#A9A59C', 221, shift=1 / 3, var=0.015,
         speck=0.012, depth=0.0008, rough=0.5, soft=0.0015, note='400x800 matt porcelain, long side along V, third bond')
    bond('porcelain_grey', (0.6, 0.3), 0.003, 3, 3, (2048, 1024), [('#C9CACB', 1)], '#A9AAAA', 223, shift=1 / 3, var=0.015,
         speck=0.012, depth=0.0008, rough=0.5, soft=0.0015, note='300x600 matt porcelain, long side along U, third bond')
    tiles.metro('metro_carrara_100x400', (0.400, 0.100), 0.002, 2, 6, (1024, 768), '#F0EFEC', '#DDDBD6', seed=225,
                var=0.01, vein='#9FA0A0')
    calacatta()
    chequer()
    plank_dark()
    plank_grey()
    # ---- site paving
    speckle('asphalt', '#55565A', 2.0, 1024, 231, amp=0.16, lo=1.5, hi=4, mott=0.06, relief=0.0012, rough=0.95)
    bond('concrete_setts_grey_buff', (0.16, 0.16), 0.004, 12, 12, (1024, 1024), [('#B3AE9F', 5), ('#8C887C', 3), ('#A19288', 2)],
         '#4B4A40', 233, shift=0.5, var=0.05, speck=0.05, depth=0.003, soft=0.006, note='tumbled 160 mm setts, three tones')
    bond('concrete_flags', (0.9, 0.6), 0.008, 2, 2, (1024, 683), [('#A9A59B', 3), ('#8E8B86', 2)], '#5E5C56', 235, var=0.04,
         speck=0.05, depth=0.003, blotch=0.06, note='900x600 footway flags')
    bond('sandstone_flags_grey', (0.6, 0.45), 0.012, 3, 4, (1024, 1024), [('#9A9CA0', 3), ('#A7A8AA', 1), ('#8B8D92', 1)],
         '#8C8A84', 237, var=0.06, speck=0.04, depth=0.004, riven=0.0012, soft=0.008, blotch=0.08, note='riven Indian sandstone, 600x450')
    herringbone('clay_block_paving_red_herringbone', [('#A8604E', 3), ('#8F4F42', 1), ('#B8705C', 1)], '#6E5A50', 239)
    boards('composite_deck_dark_brown', '#6B5645', 0.14, 0.006, 8, (1024, 1024), 241, groove=0.0008, var=0.04, rough=0.55)
    boards('timber_box_dark', '#4A3F38', 0.12, 0.0, 8, (512, 512), 243, vjoint=0.002, var=0.07, rough=0.8)
    grass()
    speckle('soil_lavender', '#4A4034', 1.5, 1024, 245, amp=0.28, lo=3, hi=14, mott=0.1, relief=0.004, rough=1.0)
    # ---- brick (the four share buff_brick's stretcher-bond normal map)
    bk = dict(unit=(0.215, 0.065), joint=0.010, nx=8, ny=16, px=(1024, 1024), depth=0.003, soft=0.004)
    bond('buff_brick', tones=[('#C9B58C', 1)], joint_hex='#CFC6B0', seed=251, var=0.06, speck=0.05, **bk)
    for key, tones, mortar, seed, var, blotch in (
            ('stock_brick_yellow', [('#C2AE85', 3), ('#B39A6E', 1), ('#D3C39E', 1)], '#D8CFBD', 253, 0.05, 0.05),
            ('stock_brick_grey', [('#A99873', 3), ('#978A6C', 1), ('#8A7D66', 1)], '#8E866F', 255, 0.07, 0.14),
            ('red_brick', [('#A8624A', 4), ('#96523E', 1), ('#B46A4C', 1)], '#C9BA8E', 257, 0.09, 0.04)):
        bond(key, tones=tones, joint_hex=mortar, seed=seed, var=var, speck=0.06, blotch=blotch, nrm_key='buff_brick', **bk)
    # ---- fences, gate
    boards('closeboard_brown', '#8A735C', 0.1, 0.0, 12, (1024, 1024), 261, streak_hex='#B5AFA6', streak=0.5, var=0.08, lap=0.012, rough=0.95)
    boards('closeboard_grey_painted', '#BDB9B3', 0.1, 0.0, 12, (1024, 1024), 263, streak_hex='#8E9480', streak=0.15, var=0.03, lap=0.012,
           rough=0.9, nrm_key='closeboard_brown')
    boards('ledged_braced_grey', '#BEBAB7', 0.095, 0.0, 8, (512, 512), 265, vjoint=0.003, var=0.03, rough=0.85, hm=0.76)
    # ---- facades, roofs
    N = 512
    n = save('render_nrm', normal(0.0005 * noise(N, N, 1.5, 5, 271) + 0.00025 * noise(N, N, 60, 300, 272), 1.0 / N), SYN)
    reg('_render', None, (1.0, 1.0), nrm=n, rough=0.9, note='smooth masonry paint over render: fine sand texture')
    slates('slate', '#474A52', 281)
    slates('fibre_cement_slate', '#4B4E57', 283, nrm_key='slate')
    speckle('flat_felt', '#6E7174', 1.0, 512, 285, amp=0.14, lo=1.5, hi=4, mott=0.08, relief=0.0008, rough=0.95)
    underside()

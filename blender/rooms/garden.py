"""Rear garden (pseudo-room `garden`, level X): what stands on the deck, lawn and path that site / envelope did not
build - fire pit (lights on a click), arched trellis panels, slatted planters and their planting, pots, the two
recliner chairs, lavender hedge, fence climbers, PIR floodlight and fairy lights (click to light), doorbell, bird
table, feeding station, the weatherproof box on the passage fence post, and the trees round the shed.
Spec: spec/rooms/garden.md, spec/phase3/garden.md (round 3 positions), spec/phase2/rear_elevation.md.

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --levels G,X --only shell,site,envelope,garden \
        --preview garden --res 540x960 --samples 64 --tag garden          (--pose 1: fire lit, lights on)

Every zone edge, the fence line, the trellis, the planters, the fire pit and the shed come from spec/house.json; the
only literal coordinates are the surveyed spots of loose things (pots, chairs, the feeder pole: phase3/garden.md 3.1).
Sky-lit only: no lamps here. The floodlight and the fairy lights are off as modelled (daylight) and glow in state 1.
Everything is lm='dynamic' (see garden_parts)."""
import json
import math
import random
from math import sin, cos, pi
from pathlib import Path
from types import SimpleNamespace

import bpy
from mathutils import Matrix, Vector as V

from lib import interact as IX, materials as M, mouldings as mo, props as P, site_tex as ST
from rooms import garden_parts as G
from rooms.garden_parts import T, col, leafmats

ROOM = 'garden'
FENCE_FACE, FENCE_CAP, FENCE_GRAVEL = .011, .03, .025   # east fence (lib/site.py): boards, capping, gravel board; posts .05

CAMERAS = [
    dict(name='house', pos=(2.0, 25.45, 1.1), look=(1.35, 17.4, 2.4), fov_deg=100, ref='v2 f_0251'),
    dict(name='deck_w', pos=(2.3, 17.95, 1.35), look=(-0.6, 19.9, 0.55), fov_deg=100, ref='v11 f_0190'),
    dict(name='deck_e', pos=(0.9, 17.9, 1.45), look=(3.3, 20.6, 0.15), fov_deg=100, ref='v11 f_0189'),
    dict(name='rear', pos=(1.9, 21.1, 1.45), look=(1.6, 17.4, 1.9), fov_deg=95, ref='v2 f_0177'),
    dict(name='lawn', pos=(2.7, 21.15, 1.45), look=(0.4, 24.0, -0.2), fov_deg=100, ref='v2 f_0203'),
    dict(name='firepit', pos=(2.4, 22.35, 0.95), look=(1.30, 23.45, -0.3), fov_deg=80, ref='v13 f_0217'),
    dict(name='lavender', pos=(0.9, 21.1, 1.45), look=(-0.55, 23.8, 0.0), fov_deg=100, ref='v2 f_0199'),
    dict(name='path', pos=(3.9, 17.7, 1.2), look=(3.6, 24.5, 0.4), fov_deg=100, ref='v11 f_0195'),
    dict(name='east', pos=(0.6, 21.1, 1.45), look=(4.6, 23.0, 0.9), fov_deg=100, ref='v2 f_0205'),
    dict(name='shed', pos=(1.3, 18.3, 1.5), look=(2.2, 26.5, 1.0), fov_deg=95, ref='v11 f_0188'),
    dict(name='nw', pos=(1.7, 19.6, 1.45), look=(-0.6, 21.0, 0.4), fov_deg=95, ref='v13 f_0217 (NW corner)'),
    dict(name='above', pos=(1.62, 17.6, 6.85), look=(1.6, 21.75, -0.45), fov_deg=94, ref='v13 f_0217'),
]


# ---------------------------------------------------------------- spec
def _bb(poly):
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    return min(xs), max(xs), min(ys), max(ys)


def _xfeat(ctx, fid):
    return next(f for f in ctx.spec['exterior']['features'] if f['id'] == fid)


def _layout(ctx):
    """Every line the garden hangs on, from house.json (RECONCILE3 garden-01..-21)."""
    ex = ctx.spec['exterior']
    z = {i: ctx.zone(i) for i in ('deck', 'lawn', 'lavender_bed', 'deck_step_n', 'garden_path')}
    shed = next(b for b in ex['buildings'] if b['id'] == 'shed')
    L = SimpleNamespace()
    L.x0, L.x1, L.yr, L.y1 = _bb(z['deck']['polygon'])                  # deck: west boundary, flank, rear wall face, north edge
    L.deck, L.lawn = float(z['deck']['z']), float(z['lawn']['z'])
    L.bed = _bb(z['lavender_bed']['polygon'])
    L.lawn_y1 = _bb(z['lawn']['polygon'])[3]
    L.shed = _bb(shed['outline'])
    L.shed_top = shed['roof'].get('coping', {}).get('topZ', shed['roof']['topZ'])
    L.items = {i['id']: i for i in _xfeat(ctx, 'planters')['items']}
    L.trellis = _xfeat(ctx, 'trellis_panels')
    try:
        L.door_x = float(ctx.opening_frame('d_french')['center'][0])
    except Exception:
        L.door_x = 1.225
    return L


_FENCE = None


def _fence_line(ctx=None):
    """East fence line (house.json east_fence); read from ctx when given, else from spec/house.json once."""
    global _FENCE
    if ctx is not None or _FENCE is None:
        spec = ctx.spec if ctx is not None else json.load(open(Path(__file__).resolve().parents[2] / 'spec' / 'house.json'))
        _FENCE = next(b for b in spec['exterior']['boundaries'] if b['id'] == 'east_fence')['line']
    return _FENCE


def fence_x(y):
    """Centre line of the east fence at y: one straight line from the gate's latch post to the shed corner."""
    (xa, ya), (xb, yb) = _fence_line()
    return xa + (xb - xa) * (y - ya) / (yb - ya)


def _fence_posts():
    """(x, y, top) of the east fence's concrete posts as the site stage built them (fallback: the survey's)."""
    o = bpy.data.objects.get('garden.east_fence.posts')
    if o is None or not len(o.data.vertices):
        return [(fence_x(y), y, 2.02) for y in (18.18, 19.57, 21.34, 23.17)]
    hi = sorted((w for w in (o.matrix_world @ v.co for v in o.data.vertices) if w.z > 1.0), key=lambda w: w.y)
    out, cur = [], [hi[0]]
    for w in hi[1:]:
        if w.y - cur[-1].y > .3:
            out.append(cur)
            cur = []
        cur.append(w)
    out.append(cur)
    return [(sum(w.x for w in c) / len(c), sum(w.y for w in c) / len(c), max(w.z for w in c)) for c in out]


def _add(ctx, ob, kind='decor', sym=None):
    return ctx.add(ob, ROOM, kind, plan_sym=sym, lm='dynamic')


def _wood(hx):
    """Stained softwood: the library's walnut-oak texture with its mean moved to the sampled colour (site_tex)."""
    return ST.mat(f'{G.TIMBER}@{hx}')


# ---------------------------------------------------------------- fire pit
def _fire_pit(ctx):
    """Square brick fire pit (garden.md 3.4, phase3 3.2): two stretcher courses, a top course of headers laid flat
    (nine a side counting the corner pair), pinwheel corners; ash bed and charred logs inside (the click target);
    flames show in state 1."""
    f = _xfeat(ctx, 'fire_pit')
    (cx, cy), w, tw, z0 = f['center'], f['size'][0], f['wall'], f['baseZ']
    rng, h2 = random.Random(3), f['size'][0] / 2
    tones = [col(f'firebrick_{i}', h, .85) for i, h in enumerate(('#C9AC72', '#D3B77F', '#BFA068', '#CDB684', '#B59A64'))]
    moss, mortar = col('firebrick_moss', '#9A9A62', .9), col('fire_mortar', '#A89878', .95)
    mb = mo.MB()
    run = w - tw                                                    # each side runs from its corner to the next side
    for k in range(4):                                              # k = 0 south, 1 east, 2 north, 3 west
        mb.at(T(cx, cy, z0, 90 * k))
        mb.box((-h2 + .005, -h2 + .005, -.02), (h2 - tw - .005, -h2 + tw - .005, .22), mortar)
        for c in (0, 1):                                            # stretcher courses, two wythes, half-bond
            for ya, yb in ((-h2, -h2 + .1025), (-h2 + tw - .1025, -h2 + tw)):
                x = -h2
                first = .1025 if c else .215
                while x < -h2 + run - .02:
                    L = min(first, -h2 + run - x)
                    mb.box((x, ya, .01 + c * .075), (x + L, yb, .075 + c * .075), moss if k == 3 and rng.random() < .3 else rng.choice(tones), bev=.004)
                    x, first = x + L + .008, .215
        p = (run + .008) / 7                                        # headers flat: 7 a side + the next side's flank pair
        for i in range(7):
            mb.box((-h2 + i * p, -h2, .16), (-h2 + (i + 1) * p - .008, -h2 + tw, .225),
                   moss if k == 3 and rng.random() < .45 else rng.choice(tones), bev=.004)
    ring = mb.at().finish('garden.fire_pit')
    _add(ctx, ring, 'fit', 'fire_pit')

    # bed of grey ash and soil one course below the rim with a tangle of dried stems (v13 t216), a few charred logs;
    # the whole bed is the click target
    zb = z0 + .11
    soil, char, stem = col('fire_soil', '#6E6A63', 1.0), col('fire_char', '#3E3833', .9), col('fire_stem', '#B5AB94', .8)
    mb = mo.MB()
    hi = h2 - tw + .004
    mb.box((cx - hi, cy - hi, z0 + .02), (cx + hi, cy + hi, zb), soil)
    for a, r, L, dz in ((20, .035, .40, .025), (95, .03, .36, .03), (150, .04, .32, .035)):
        d = V((cos(math.radians(a)), sin(math.radians(a)), .06))
        c = V((cx + rng.uniform(-.04, .04), cy + rng.uniform(-.04, .04), zb + dz))
        mb.tube([c - d * L / 2, c + d * L / 2], r, char, 6)
    for k in range(22):
        x, y = cx + rng.uniform(-.2, .2), cy + rng.uniform(-.2, .2)
        if k < 5:                                                   # standing, splayed a little
            a, h = rng.uniform(0, 2 * pi), rng.uniform(.18, .32)
            mb.tube([(x, y, zb), (x + .2 * h * cos(a), y + .2 * h * sin(a), zb + h)], .003, stem, 4)
        else:                                                       # lying across the bed, curling
            a, L = rng.uniform(0, pi), rng.uniform(.14, .30)
            dx, dy = L / 2 * cos(a), L / 2 * sin(a)
            mb.tube([(x - dx, y - dy, zb + .004), (x + rng.uniform(-.03, .03), y + rng.uniform(-.03, .03), zb + .02),
                     (x + dx, y + dy, zb + .01)], .003, stem, 4)
    logs = mb.finish('garden.fire_pit.logs')
    IX.tag(logs, 'trigger', g='garden.fire_pit', label='Fire pit', reach=2.2)
    _add(ctx, logs, 'fit')

    # the viewer draws fx 'flame' additive in the material's own emissive colour and scales it in height (interact.js);
    # strength kept low so AgX keeps it orange. Crossed pairs of S-curved, tapering cards, smooth-shaded
    outer, core, ember = (P.two_sided(P.emissive(h, s)) for h, s in (('#FF6A12', 1.2), ('#FFB236', 1.6), ('#D8380C', .9)))
    vs, fs, mi = [], [], []
    for i in range(10):
        a, r = rng.uniform(0, 2 * pi), rng.uniform(.02, .15)
        base = V((cx + r * cos(a), cy + r * sin(a), zb + .02))
        inward = -V((cos(a), sin(a), 0))
        for big, k in ((1.0, 0), (.55, 1)):                         # outer flame and its yellow core
            h, w = rng.uniform(.22, .40) * (1 - r * 2) * big, rng.uniform(.09, .14) * big
            if k:
                h, w = max(h, .1), max(w, .05)
            rot = rng.uniform(0, pi)
            for s in (0, 1):                                        # crossed pair
                side = V((cos(rot + s * pi / 2), sin(rot + s * pi / 2), 0))
                o, wob = len(vs), rng.uniform(.25, .45) * w
                for j in range(4):
                    t = j / 4
                    c = base + V((0, 0, h * t)) + inward * (h * .25 * t * t) + side * (wob * sin(pi * 1.5 * t))
                    hw = w / 2 * sin(pi * (.15 + .85 * t))
                    vs += [c - side * hw, c + side * hw]
                vs.append(base + V((0, 0, h)) + inward * (h * .25) + side * (wob * sin(pi * 1.5)))
                fs += [(o + 2 * j, o + 2 * j + 1, o + 2 * j + 3, o + 2 * j + 2) for j in range(3)] + [(o + 6, o + 7, o + 8)]
                mi += [k] * 4
    me = bpy.data.meshes.new('garden.fire_pit.flame')
    me.from_pydata([tuple(v) for v in vs], [], fs)
    me.uv_layers.new(name='UVMap')
    for m in (outer, core):
        me.materials.append(m)
    me.polygons.foreach_set('material_index', mi)
    me.polygons.foreach_set('use_smooth', [True] * len(fs))
    me.update()
    mb = mo.MB()
    for k in range(9):                                              # glowing embers on the bed
        mb.at(T(cx + rng.uniform(-.18, .18), cy + rng.uniform(-.18, .18), zb + .001, rng.uniform(0, 180)))
        mb.dome(rng.uniform(.03, .06), rng.uniform(.02, .04), .008, ember, 6, 1)
    embers = mb.at().finish('garden.fire_pit.embers')
    flame = bpy.data.objects.new('garden.fire_pit.flame', me)
    for ob in (flame, embers):
        IX.tag(ob, 'show', g='garden.fire_pit', label='Fire pit', when=1, fx='flame')
        _add(ctx, ob, 'fit')


# ---------------------------------------------------------------- trellis ("garden panel")
def _trellis_mesh(w, hs, hc, fr=.035, step=.18):
    """Arched (bow-top) diamond-lattice panel (garden.md 6, phase3 3.1: about ten diamonds across a 1.83 panel).
    Local: back on x = 0, width along +Y from 0, foot at z = 0; hs = height at the shoulders, hc at the crown."""
    mat = col('trellis', '#6E5A44', .8)
    top = lambda u: hs + (hc - hs) * (1 - cos(pi * (1 - abs(2 * u / w - 1)))) / 2
    n = 24
    us = [w * i / n for i in range(n, -1, -1)]
    outer = [(0, 0), (w, 0)] + [(u, top(u)) for u in us]
    inner = [(fr, fr), (w - fr, fr)] + [(min(max(u, fr), w - fr), top(u) - fr) for u in us]
    mb, cz = mo.MB(), hs / 2
    for i in range(len(outer)):
        j = (i + 1) % len(outer)
        (ou, oz), (pu, pz), (iu, iz), (qu, qz) = outer[i], outer[j], inner[i], inner[j]
        out = (0, (ou + pu) / 2 - w / 2, (oz + pz) / 2 - cz)
        mb.face([(fr, ou, oz), (fr, pu, pz), (fr, qu, qz), (fr, iu, iz)], mat, (1, 0, 0))
        mb.face([(0, ou, oz), (0, pu, pz), (fr, pu, pz), (fr, ou, oz)], mat, out)
        mb.face([(0, iu, iz), (0, qu, qz), (fr, qu, qz), (fr, iu, iz)], mat, tuple(-c for c in out))
    mb.box((0, w / 2 - .0125, fr), (fr * .8, w / 2 + .0125, top(w / 2) - fr), mat)          # centre muntin
    lo, hw = fr / 2, .015                                            # laths 30 x 8 in two layers

    def root(g, a, b):                                               # g is monotonic on [a, b]
        for _ in range(30):
            m = (a + b) / 2
            a, b = (m, b) if (g(a) > 0) == (g(m) > 0) else (a, m)
        return (a + b) / 2
    for s, x0 in ((1, .008), (-1, .016)):
        c = -w if s > 0 else 0.0
        while c < hc + (0 if s > 0 else w):
            c += step
            g = lambda u: top(u) - lo - c - s * u                    # >= 0 below the top rail
            a, b = lo, w - lo
            if s > 0:
                a = max(a, lo - c)
                if g(a) <= 0:
                    continue
                b = b if g(b) >= 0 else root(g, a, b)
            else:
                b = min(b, c - lo)
                if b <= a or g(b) <= 0:
                    continue
                a = a if g(a) >= 0 else root(g, a, b)
            if b - a < .04:
                continue
            px, pz = -s * hw * .7071, hw * .7071
            A, B = (a, c + s * a), (b, c + s * b)
            mb.prism([(x0, A[0] + px, A[1] + pz), (x0, B[0] + px, B[1] + pz), (x0, B[0] - px, B[1] - pz), (x0, A[0] - px, A[1] - pz)],
                     (.008, 0, 0), mat)
    return mb.finish('garden.trellis.0')


def _trellis(ctx, L, z_foot):
    """Two 1.83 panels on the feature line, standing on the long planter's back rim against the neighbour's wall:
    crown 1.50 and shoulders 1.25 above the deck (phase3 3.1, RECONCILE3 garden-20)."""
    t = L.trellis
    (lx, ly0), (_, ly1) = t['line']
    w, crown = t['panelSize']
    zc = L.deck + crown
    first = _trellis_mesh(w, zc - .25 - z_foot, zc - z_foot)
    for i in range(t['panels']):
        ob = bpy.data.objects.new(f'garden.trellis.{i}', first.data) if i else first
        ob.location = (L.x0 + .002, min(ly0, ly1) + i * w, z_foot)
        _add(ctx, ob, 'fit', 'trellis')


# ---------------------------------------------------------------- planters and what grows in them
def _planters(ctx, L):
    rng = random.Random(11)
    leaves = {}                                                     # name -> (materials, leaf list)
    soil = P.mat('soil')
    east_wood, west_wood = _wood('#5A4A40'), _wood('#7A6650')

    def grow(name, mats, ls):
        leaves.setdefault(name, (mats, []))[1].extend(ls)

    # WEST: one long planter along the neighbour's wall under the trellis (phase3 3.1: x -0.74..-0.44 from y 17.65,
    # 0.42 high, mid brown), red geraniums spilling at the south end, low green foliage along it, dry stems at the north
    # end. It runs ~0.07 past the trellis's north end (v11 t188 / t189 and v13 t216, not the brief's 20.50), so both
    # panels stand on its rim
    ty1 = max(p[1] for p in L.trellis['line'])
    wy1 = ty1 + .07
    mb = mo.MB()
    x0, x1 = L.x0 + .008, -0.44
    zf = G.planter(mb, x0, x1, 17.65, wy1, L.deck, .42, wood=west_wood)
    dry = col('dry_stem', '#8E8270', .85)
    for _ in range(14):                                             # dead perennial stems at the north end (v11 t189)
        x, y = rng.uniform(x0 + .08, x1 - .06), rng.uniform(wy1 - .55, wy1 - .1)
        a, h, b = rng.uniform(0, 2 * pi), rng.uniform(.10, .22), rng.uniform(-.5, .5)
        mb.tube([(x, y, zf), (x + .2 * h * cos(a), y + .2 * h * sin(a), zf + .55 * h),
                 (x + .45 * h * cos(a + b), y + .45 * h * sin(a + b), zf + h)], .0022, dry, 3)
    _add(ctx, mb.finish('garden.planter.west'), 'furn', 'planter')
    rim = L.deck + .42 + .018
    wall = lambda p: p.x > L.x0 + .06 and not (x1 - .035 < p.x < x1 + .015 and p.z < rim + .005)   # not through the trellis / slats
    ger = leafmats('geranium', ('#6FAE4C', '#82BE5A', '#5E9C44'))
    red = leafmats('geranium_red', ('#D8402A', '#E2553A'), .6)
    herb = leafmats('herb', ('#5F9048', '#74A656', '#8EAE64'))
    cg = (x0 + .18, 18.05, zf + .17)
    lg = G.blob(rng, cg, (.30, .42, .24), 520, .065, .075, 3, droop=.25, shell=.35, lo=-.6, keep=wall)
    lr = [(p + V((0, 0, .03)), t + V((0, 0, .05)), .022, n, k % 2)
          for p, t, hw, n, k in G.blob(rng, cg, (.31, .43, .27), 60, .04, .04, 2, droop=-.6, shell=.9, lo=.05, keep=wall)]
    lh = G.blob(rng, (x0 + .16, 18.95, zf + .14), (.14, .26, .18), 120, .08, .06, 3, shell=.3, lo=-.3, keep=wall)
    lh += G.blob(rng, (x0 + .15, 19.75, zf + .05), (.12, .35, .09), 110, .05, .03, 3, shell=.2, lo=0, keep=wall)
    lh += G.blob(rng, (x0 + .16, 20.25, zf + .10), (.13, .2, .16), 90, .08, .06, 3, shell=.3, lo=-.2, keep=wall)
    _add(ctx, G.cards('garden.planter.west.geranium', lg, ger))
    _add(ctx, G.cards('garden.planter.west.flowers', lr, red))
    grow('herbs', herb, lh)

    # NW corner (v11 t188 / t189, v13 t216): a short dark box in the strip between the long planter's end and the deck
    # edge, set back level with it, soil and a timber corner post; the small standard pyracantha (red berries) grows
    # out of it, its head below the trellis shoulders. The cream stone-effect urn of variegated thyme on the deck beside it
    mb = mo.MB()
    nx0, nx1, ny0, ny1 = x0, x1 - .01, wy1 + .013, L.y1 - .008        # set back a little; rims clear of the long planter's
    zc = G.planter(mb, nx0, nx1, ny0, ny1, L.deck, .38, wood=_wood('#463A30'))
    mb.box((nx0 + .03, ny1 - .075, zc), (nx0 + .075, ny1 - .03, zc + .36), _wood('#8A7458'), bev=.004)     # corner post
    px, py = (nx0 + nx1) / 2, (ny0 + ny1) / 2
    bark = col('bark', '#5B4A3A', .85)
    mb.tube([(px, py, zc), (px + .008, py, zc + .14), (px - .004, py + .006, zc + .26)], .011, bark, 6)      # short clear stem
    for a in (0.3, 1.5, 2.6, 3.9, 5.1):
        mb.tube(G.chaikin([(px, py, zc + .2), (px + .05 * cos(a), py + .04 * sin(a), zc + .3),
                           (px + .12 * cos(a), py + .1 * sin(a), zc + .42)], 1), .005, bark, 4)
    for _ in range(5):                                              # soil lumps
        mb.at(T(rng.uniform(nx0 + .07, nx1 - .07), rng.uniform(ny0 + .07, ny1 - .07), zc, rng.uniform(0, 180)))
        mb.dome(rng.uniform(.03, .05), rng.uniform(.03, .04), .012, soil, 6, 1)
    mb.at()
    _add(ctx, mb.finish('garden.planter.corner'), 'furn', 'planter')
    pyr = leafmats('pyracantha', ('#4C7040', '#5A8046', '#426436'))
    keep_nw = lambda p: p.x > L.x0 + .03 and p.y < L.y1 + .25 and not (p.y < ty1 + .02 and p.x < L.x0 + .06)   # not into the trellis
    hc, hr = (px, py, zc + .38), (.2, .17, .24)
    lp = G.blob(rng, hc, hr, 520, .055, .03, 3, droop=.1, shell=.3, keep=keep_nw)
    berry = [(p, t, .014, n, 0) for p, t, hw, n, k in G.blob(rng, hc, (.19, .16, .22), 40, .022, .02, 1, shell=.5, keep=keep_nw)]
    grow('pyracantha', pyr, lp)
    _add(ctx, G.cards('garden.planter.corner.berries', berry, leafmats('berry', ('#C8321E',), .4)))
    mb = mo.MB()                                                    # urn: near-cylindrical bowl, slight belly, rolled lip
    ux, uy, ur = -0.05, 21.15, .20
    urn = col('urn', '#CDBF9F', .8)
    mb.at(T(ux, uy, L.deck))
    mb.lathe([(0, .03), (.15, .03), (.18, .10), (.195, .24), (.205, .30), (ur, .335), (ur - .02, .33), (ur - .03, .30)], urn, 20)
    mb.lathe([(ur - .03, .30), (0, .30)], soil, 20)
    for k in range(3):                                              # three small feet on the deck
        mb.at(T(ux, uy, L.deck, 120 * k + 30))
        mb.box((.105, -.02, 0), (.155, .02, .031), urn, bev=.006)
    mb.at()
    _add(ctx, mb.finish('garden.urn'), 'furn', 'plant')
    thyme = leafmats('thyme', ('#8E9F7A', '#C9C9A0', '#7C8E6C', '#D8D4B0'))
    in_urn = lambda p: math.hypot(p.x - ux, p.y - uy) < ur - .06 or p.z > L.deck + .35
    grow('thyme', thyme, G.blob(rng, (ux, uy, L.deck + .31), (.22, .22, .13), 260, .05, .022, 4, droop=.8, shell=.3, lo=-.35,
                                keep=in_urn))

    # pebble planter under the east rear window, filled to the brim with pale river cobbles (v11 t187-t191), the
    # wisteria on canes. Set clear of the balcony's east wall post (envelope: x 2.25..2.35 against the wall).
    mb = mo.MB()
    px0, px1, py0, py1 = _bb(L.items['pebble_planter']['polygon'])
    shift = max(0.0, _post_clear(2.30) - px0)
    px0, px1 = px0 + shift, min(px1 + shift, L.x1 - .03)
    dy = max(0.0, _sill_front(px0, px1, L.yr) + .012 - py0)       # the window's stone sill (Z 0.30..0.34) overhangs it
    py0, py1 = py0 + dy, py1 + dy
    zp = G.planter(mb, px0, px1, py0, py1, L.deck, L.items['pebble_planter']['height'], drop=.05, wood=east_wood)
    stones = [col(f'cobble_{i}', h, .5) for i, h in enumerate(('#E2DACB', '#D6CBB8', '#EAE4D8', '#C9BCA8', '#DCD2C4', '#B9AE9E'))]
    for _ in range(110):
        x, y = rng.uniform(px0 + .06, px1 - .06), rng.uniform(py0 + .06, py1 - .06)
        mb.at(T(x, y, zp - .012 + rng.uniform(0, .02), rng.uniform(0, 180)))
        mb.dome(rng.uniform(.03, .06), rng.uniform(.025, .045), rng.uniform(.022, .04), rng.choice(stones), 6, 2)
    mb.at()
    # wisteria: bamboo canes, twisting stems, wall-trained leader up the east margin of the rear wall to z 3.0
    cane, stem = col('bamboo', '#B9A56A', .6), col('wisteria_stem', '#6A5A46', .85)
    bx, by, YR = px1 - .30, py0 + .21, L.yr
    for dx, dy in ((-.3, .02), (-.12, .1), (.0, -.04), (.14, .08), (.24, -.02)):
        mb.tube([(bx + dx * .3, by + dy * .5, zp), (bx + dx, by + dy, zp + 1.3)], .006, cane, 5)
    for k, (dx, dy) in enumerate(((-.22, .06), (.05, .1), (.2, .0))):
        mb.tube(G.chaikin([(bx + .02 * k, by, zp), (bx + dx * .4, by + .05, zp + .35), (bx + dx * .5, by + dy, zp + .7), (bx + dx, by + dy * .5, zp + 1.1)]),
                .008, stem, 5)
    leader = G.chaikin([(bx + .12, by - .1, zp + .3), (bx + .12, YR + .04, 1.0), (bx + .2, YR + .03, 1.6), (bx + .14, YR + .03, 2.2),
                        (bx + .24, YR + .03, 2.75), (bx + .18, YR + .03, 3.0)])
    mb.tube(leader, .006, stem, 4)
    _add(ctx, mb.finish('garden.planter.pebble'), 'furn', 'planter')
    wis = leafmats('wisteria', ('#8FB45A', '#9EC064', '#7EA650', '#B4BE62'))
    pc = _post_clear(0) + .02
    clear = lambda p: p.y > YR + .03 and p.x > pc
    lw = G.blob(rng, (bx - .02, by + .07, zp + .78), (.45, .30, .52), 1300, .095, .042, 4, droop=.35, shell=.3, keep=clear)
    lw += G.blob(rng, (bx + .19, YR + .1, 1.95), (.2, .09, .32), 160, .095, .042, 4, droop=.4, shell=.3, keep=clear)
    lw += G.strand(rng, leader[4:], 90, .095, .042, 4, (0, 1, 0))
    _add(ctx, G.cards('garden.wisteria', lw, wis))

    # EAST: trough of vertical boards on four block feet with the black liner lapped over the rim, a few seedlings
    # (v11 t194); square planter of the same boards with a small olive tree (house.json planters, garden-21)
    tx0, tx1, ty0, ty1 = _bb(L.items['trough_planter']['polygon'])
    mb = mo.MB()
    zt = G.planter(mb, tx0, tx1, ty0, ty1, L.deck, L.items['trough_planter']['height'], feet=.07, drop=.15,
                   wood=east_wood, vertical=True, liner='fold')
    tc = (tx0 + tx1) / 2
    for y in (ty0 + .45, ty0 + 1.2, ty1 - .35):
        mb.at(T(tc, y, zt))
        mb.dome(.1, .14, .025, soil, 8, 2)
    mb.at()
    _add(ctx, mb.finish('garden.planter.trough'), 'furn', 'planter')
    for y in (ty0 + .45, ty0 + 1.2, ty1 - .35):
        grow('herbs', herb, G.blob(rng, (tc, y, zt + .03), (.07, .09, .07), 30, .05, .03, 3, shell=.2, lo=0))
    qx0, qx1, qy0, qy1 = _bb(L.items['square_planter']['polygon'])
    mb = mo.MB()
    zq = G.planter(mb, qx0, qx1, qy0, qy1, L.deck, L.items['square_planter']['height'], feet=.05, wood=east_wood, vertical=True)
    ox, oy = (qx0 + qx1) / 2, (qy0 + qy1) / 2
    trunk = [(ox, oy, zq), (ox + .015, oy - .01, zq + .25), (ox - .01, oy + .005, zq + .5)]
    mb.tube(trunk, .016, col('olive_bark', '#7B776A', .85), 6)
    olive_br = []
    for k in range(6):
        a = 2 * pi * k / 6 + .4
        e = (ox + .2 * cos(a), oy + .2 * sin(a), zq + rng.uniform(.75, 1.0))
        olive_br.append(e)
        mb.tube(G.chaikin([trunk[-1], (ox + .07 * cos(a), oy + .07 * sin(a), zq + .62), e], 1), .006, col('olive_bark', '#7B776A', .85), 4)
    _add(ctx, mb.finish('garden.planter.square'), 'furn', 'planter')
    olive = leafmats('olive', ('#7F8C6A', '#8E9A78', '#6E7C5E', '#A3AA8E'))
    lo_ = []
    for e in olive_br:
        lo_ += G.blob(rng, e, (.14, .14, .16), 110, .06, .016, 4, droop=.1, shell=.2)
    grow('olive', olive, lo_)

    for name, (mats, ls) in leaves.items():
        _add(ctx, G.cards('garden.planting.' + name, ls, mats))
    return rim


def _sill_front(x0, x1, y):
    """Front (max y) of the rear facade's projecting sills below Z 1 between x0 and x1 (envelope), else y."""
    o = bpy.data.objects.get('facade.rear_R.sills')
    if o is None:
        return y
    ys = [w.y for w in (o.matrix_world @ v.co for v in o.data.vertices) if x0 - .05 < w.x < x1 + .05 and w.z < 1.0]
    return max(ys + [y])


def _post_clear(x):
    """x just east of the balcony's east wall post if `x` would touch it (envelope builds posts against the rear
    wall); `x` itself when there is no balcony structure."""
    o = bpy.data.objects.get('balcony.structure')
    if o is None:
        return x
    low = [o.matrix_world @ v.co for v in o.data.vertices]
    low = [w.x for w in low if w.z < .5 and w.x > 1.3]
    return max(low) + .02 if low else x


def _pots(ctx, L):
    """Loose pots (phase3 3.1): black glazed rosemary on ochre pot feet, the dark blue-glazed pot of a small maple
    (bare twigs, a few yellow leaves left), terracotta pot with a bare sapling at the deck's NE corner, and a small
    black pot of thin stems in front of the long planter (v11 t188 / t189)."""
    rng = random.Random(23)
    bark = col('bark', '#5B4A3A', .85)
    black = col('pot_black', '#1E2024', .25)

    mb = mo.MB()                                                    # rosemary (2.75, 18.65), dia 0.30
    rx, ry = 2.75, 18.65
    z = G.pot(mb, rx, ry, L.deck + .025, .15, .26, black, belly=1.0)
    for k in range(3):                                              # terracotta-ochre pot feet
        a = 2 * pi * k / 3 + .5
        mb.at(T(rx + .1 * cos(a), ry + .1 * sin(a), L.deck, math.degrees(a)))
        mb.box((-.03, -.02, 0), (.03, .02, .026), col('pot_feet', '#B89A4E', .6), bev=.004)
    mb.at()
    _add(ctx, mb.finish('garden.pot.rosemary'), 'furn', 'plant')
    rosemary = leafmats('rosemary', ('#8CA080', '#9AAC8C', '#7C9272'))
    away = lambda p: not (p.x > 2.93 and p.y > ry + .17)            # clear of the trough's corner
    lr = G.blob(rng, (rx, ry, z + .02), (.2, .2, .3), 300, .09, .014, 3, droop=0, shell=.25, lo=-.1, up=.9, keep=away)
    _add(ctx, G.cards('garden.pot.rosemary.leaves', lr, rosemary))

    mb = mo.MB()                                                    # maple in the dark blue-glazed pot
    mx, my = 2.55, 20.40
    z = G.pot(mb, mx, my, L.deck, .14, .25, col('pot_blue', '#3E4F62', .15), feet=.02, belly=.7)
    mb.tube(G.chaikin([(mx, my, z), (mx + .01, my - .01, z + .3), (mx - .03, my + .02, z + .62)], 1), .006, bark, 4)
    tips = []
    for k in range(6):
        a, hgt = 2 * pi * k / 6 + .3, z + rng.uniform(.3, .55)
        tip = (mx + .17 * cos(a), my + .17 * sin(a), hgt + .15)
        tips.append(tip)
        mb.tube(G.chaikin([(mx, my, hgt), (mx + .08 * cos(a), my + .08 * sin(a), hgt + .1), tip], 1), .003, bark, 3)
    _add(ctx, mb.finish('garden.pot.maple'), 'furn', 'plant')
    maple = leafmats('maple', ('#B8B052', '#C8A84A', '#9CAA56'))
    lm = []
    for tp in tips:
        lm += G.blob(rng, tp, (.06, .06, .05), 7, .07, .07, 3, droop=.5, shell=.3)
    _add(ctx, G.cards('garden.pot.maple.leaves', lm, maple))

    mb = mo.MB()                                                    # terracotta (2.65, 21.10), dia 0.38
    tx, ty = 2.65, 21.10
    z = G.pot(mb, tx, ty, L.deck, .19, .30, P.mat('terracotta'), belly=.25)
    mb.tube([(tx, ty, z), (tx + .01, ty - .01, z + .55), (tx - .01, ty, z + .85)], .006, bark, 5)
    for k in range(4):
        a = 1.6 * k + .2
        mb.tube(G.chaikin([(tx, ty, z + .3 + .12 * k), (tx + .07 * cos(a), ty + .07 * sin(a), z + .42 + .12 * k),
                           (tx + .16 * cos(a), ty + .16 * sin(a), z + .5 + .14 * k)], 1), .003, bark, 3)
    _add(ctx, mb.finish('garden.pot.terracotta'), 'furn', 'plant')

    mb = mo.MB()                                                    # small black pot by the geraniums
    sx, sy = -0.31, 18.42
    z = G.pot(mb, sx, sy, L.deck, .08, .14, col('pot_grey', '#3C3F43', .4))
    for k in range(5):
        a = 2 * pi * k / 5
        mb.tube([(sx, sy, z), (sx + .07 * cos(a), sy + .07 * sin(a), z + rng.uniform(.18, .3))], .0025, col('stem_green', '#6B7A44', .7), 3)
    _add(ctx, mb.finish('garden.pot.small'), 'furn', 'plant')


# ---------------------------------------------------------------- recliner chairs
def _chair_mesh():
    """Reclining camping chair (garden.md 6), 0.60 x 0.65 x 1.05: grey tubular steel, mid-blue fabric.
    Local: faces +X, origin floor centre."""
    frame, cloth, pad = col('chair_frame', '#B4B8BC', .35, .8), col('chair_blue', '#5E7FA8', .9), col('chair_pad', '#2E3136', .6)
    mb = mo.MB()
    r, up = .011, (0, 1, 0)
    for y in (-.28, .28):
        for a, b in (((.31, 0), (-.10, .44)), ((-.27, 0), (.24, .44)), ((-.12, .43), (.26, .45)), ((-.08, .40), (-.32, 1.02)),
                     ((-.19, .68), (.22, .655)), ((.22, .655), (.255, .45))):
            mb.tube([(a[0], y, a[1]), (b[0], y, b[1])], r, frame, 6, up=up)
        mb.box((-.14, y - .024, .685), (.20, y + .024, .705), pad, bev=.004)                 # arm pad
        for x in (.31, -.27):                                                               # rubber feet
            mb.box((x - .03, y - .015, -.006), (x + .03, y + .015, .012), pad, bev=.003)
    for x, z in ((.31, .023), (-.27, .023), (-.32, 1.02), (.26, .45), (-.105, .425)):
        mb.tube([(x, -.28, z), (x, .28, z)], r, frame, 6)
    mb.box((-.10, -.268, .428), (.255, .268, .438), cloth, bev=.003)                          # seat
    mb.at(T(-.085, 0, .41) @ Matrix.Rotation(math.radians(-21.2), 4, 'Y'))
    mb.box((-.004, -.268, 0), (.006, .268, .66), cloth, bev=.003)                             # back
    mb.box((.004, -.19, .47), (.05, .19, .63), cloth, bev=.02)                                # head cushion
    for z in (.12, .5):                                                                     # webbing straps behind
        mb.box((-.012, -.27, z), (-.004, .27, z + .03), pad)
    return mb.at().finish('garden.chair.0')


def _chairs(ctx, L):
    """Two blue recliners, backs to the trellis (phase3 3.1: (0.25, 18.9) and (0.25, 19.7)), turned a little to the
    French doors as in v11 t189."""
    first = _chair_mesh()
    for i, (y, rz) in enumerate(((18.9, -8), (19.7, -14))):
        ob = bpy.data.objects.new(f'garden.chair.{i}', first.data) if i else first
        ob.location = (0.25, y, L.deck + .006)
        ob.rotation_euler.z = math.radians(rz)
        _add(ctx, ob, 'furn', 'chair')


# ---------------------------------------------------------------- lavender, climbers
def _lavender(ctx, L):
    """'Lots of lavender by the side': a continuous hedge of silvery grey-green mounds 0.45 high x 0.5 wide in the bed
    along the west fence, from the deck fascia to the shed pier (zone lavender_bed). No flowers (November)."""
    rng = random.Random(5)
    bx0, bx1, by0, by1 = L.bed
    body = col('lavender_body', '#A6A792', 1.0)                     # leaf tone: the leaves fuzz its surface
    mats = [P.two_sided(col(f'lavender_{i}', G._mute(h, .1), .8)) for i, h in enumerate(('#B2B29D', '#C0BFAA', '#A6A894', '#CAC8B5'))]
    n = max(2, round((by1 - by0 - .1) / .36))
    pitch = (by1 - by0 - .56) / (n - 1)
    sx0, _, _, sy1 = _bb(ctx.zone('deck_step_n')['polygon'])       # the step box beside the bed's south end
    keep = lambda p: bx0 + .07 < p.x < bx1 + .1 and by0 + .02 < p.y < by1 - .02 and not (p.x > sx0 - .04 and p.y < sy1 + .03)
    mb, ls = mo.MB(), []
    for i in range(n):
        rx, ry, h = rng.uniform(.23, .26), rng.uniform(.29, .33), rng.uniform(.40, .49)
        x, y = bx0 + .06 + rx + rng.uniform(0, .02), by0 + .28 + i * pitch        # off the west fence's rails (-0.694)
        if y - ry < sy1:                                            # narrower beside the step
            rx = min(rx, (sx0 - .015 - (bx0 + .06)) / 2)
            x = bx0 + .06 + rx
        mb.at(T(x, y, L.lawn - .02))
        mb.dome(rx * .88, ry * .88, h * .82, body, 10, 3)
        ls += G.blob(rng, (x, y, L.lawn + .02), (rx, ry, h * .95), 700, .06, .018, 4, droop=.05, shell=.8, lo=.0, up=.5, keep=keep)
    _add(ctx, mb.at().finish('garden.lavender'), 'decor', 'planter')        # a hedge: blocks the walker, drawn as a bed
    _add(ctx, G.cards('garden.lavender.leaves', ls, mats))


def climbers(ctx, room, name, ys, seed, top=1.70, rise=(), base=-0.45, posts=None):
    """Thin passion-flower / ivy strands on the garden face of the painted east fence (garden.md 7): one hanging down
    from the capping at each y in `ys`, one climbing from the ground at `base` and trailing along the top at each y in
    `rise` (v11 t59, t186). Stems lie on the boards, each within its bay (posts: y of the fence posts)."""
    _fence_line(ctx)
    r = .003
    posts = sorted(p[1] for p in _fence_posts()) if posts is None else sorted(posts)

    def need(y, z):                                                 # how far proud of the fence line the profile is at (y, z)
        if any(abs(y - q) < .052 for q in posts):
            return .05
        return FENCE_CAP if z > top - .10 else FENCE_GRAVEL if z < base + .25 else FENCE_FACE    # capping .03 deep, gravel board to base + .15

    def bay(y):                                                     # (lo, hi) of the bay holding y, clear of its posts
        lo = max([q for q in posts if q <= y], default=y - 9) + .12
        hi = min([q for q in posts if q > y], default=y + 9) - .12
        return lambda v: min(max(v, lo), hi)

    def at(y, z):
        return (fence_x(y) - need(y, z) - r - .002, y, z)
    rng = random.Random(seed)
    stem = col('climber_stem', '#5A6B3A', .8)
    mats = leafmats('ivy', ('#6C8F64', '#7CA06A', '#98B268'))
    mb, ls = mo.MB(), []
    paths = []
    for y in ys:
        n, cl = rng.randint(4, 6), bay(y)
        z, pts, y = top - .02, [], cl(y)
        for k in range(n + 1):
            pts.append(at(y, z))
            y, z = cl(y + rng.uniform(-.22, .22)), z - rng.uniform(.18, .3)
        paths.append((n, pts))
    for y in rise:
        n, z, pts, cl = 7, base - .004, [], bay(y)
        y = cl(y)
        for k in range(n + 1):
            pts.append(at(y, z))
            y, z = cl(y + rng.uniform(-.1, .1)), min(top - .04, z + (top - base) / n * rng.uniform(.9, 1.15))
        for k in range(3):                                          # then along under the capping
            y = cl(y + rng.uniform(.25, .4))
            z = top - .05 - rng.uniform(0, .1)
            pts.append(at(y, z))
        paths.append((n + 3, pts))
    clear = lambda p: fence_x(p.y) - p.x > need(p.y, p.z) + .002
    for n, pts in paths:
        pts = [V(at(p.y, p.z)) for p in G.chaikin(pts, 1)]        # smoothed points back onto the profile
        mb.tube(pts, r, stem, 3, up=(1, 0, 0))
        ls += [lf for lf in G.strand(rng, pts, 7 * n, .075, .055, 3, (-1, 0, 0), off=-.002)
               if min(lf[0].z, lf[1].z) > base + .03 and clear(lf[0]) and clear(lf[1])]
    ctx.add(mb.finish(name), room, 'decor', lm='dynamic')
    ctx.add(G.cards(name + '.leaves', ls, mats), room, 'decor', lm='dynamic')


# ---------------------------------------------------------------- lights, doorbell, the box on the fence post
def _floodlight(ctx, L):
    """Black LED flood with a PIR sensor on the door axis under the balcony (rear_elevation.md 3). Automatic in
    reality: here a click on the fitting lights it."""
    black, lens = M.mat('black_matt'), col('flood_lens', '#8A8E92', .2)
    tilt = T(0, -.045, 0) @ Matrix.Rotation(math.radians(25), 4, 'X')
    mb = mo.MB()
    mb.box((-.03, -.05, -.025), (.03, 0, .025), black, bev=.003)                               # wall bracket
    mb.at(tilt)
    mb.box((-.10, -.05, -.08), (.10, 0, .08), black, bev=.006)
    for k in range(5):                                                                        # cooling fins on the back
        mb.box((-.085 + k * .0425 - .003, -.004, -.07), (-.085 + k * .0425 + .003, .006, .07), black)
    mb.box((-.086, -.052, -.066), (.086, -.049, .066), lens)
    mb.at()
    mb.box((-.028, -.05, -.16), (.028, -.004, -.105), black, bev=.004)                         # PIR
    mb.at(T(0, -.05, -.135) @ Matrix.Rotation(pi / 2, 4, 'X'))
    mb.dome(.02, .02, .014, M.mat('plastic_white'), 8, 2)
    loc = (L.door_x, L.yr + .001, 2.58)
    body = P.place(mb.at().finish('garden.floodlight'), loc, facing=(0, 1))
    mb = mo.MB()
    mb.at(tilt)
    mb.face([(-.084, -.0535, -.064), (.084, -.0535, -.064), (.084, -.0535, .064), (-.084, -.0535, .064)], P.emissive('#FFD9A0', 10.0), (0, -1, 0))
    glow = P.place(mb.at().finish('garden.floodlight.glow'), loc, facing=(0, 1))
    G.click_glow(ctx, ROOM, body, glow, 'Floodlight')


def _octas(name, pts, r, mat):
    vs, fs = [], []
    for p in pts:
        o = len(vs)
        vs += [(p[0] + r, p[1], p[2]), (p[0], p[1] + r, p[2]), (p[0] - r, p[1], p[2]), (p[0], p[1] - r, p[2]),
               (p[0], p[1], p[2] + r * 1.4), (p[0], p[1], p[2] - r * 1.4)]
        fs += [(o + i, o + (i + 1) % 4, o + 4) for i in range(4)] + [(o + (i + 1) % 4, o + i, o + 5) for i in range(4)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(vs, [], fs)
    me.materials.append(mat)
    me.uv_layers.new(name='UVMap')
    me.update()
    return bpy.data.objects.new(name, me)


def _balcony_edge(ctx, L):
    """(x0, x1, y1, z) of the balcony tray's outer frame: west, east and front faces and its underside, from the
    envelope's `balcony.structure` (fallback: the room polygon)."""
    fz = ctx.floor_z('balcony')
    o = bpy.data.objects.get('balcony.structure')
    if o is not None:
        ws = [o.matrix_world @ v.co for v in o.data.vertices]
        tray = [w for w in ws if fz - .25 < w.z < fz + .01]
        if tray:
            x0, x1, y1 = min(w.x for w in tray), max(w.x for w in tray), max(w.y for w in tray)
            edge = [w.z for w in tray if abs(w.y - y1) < .01 or abs(w.x - x0) < .01 or abs(w.x - x1) < .01]
            return x0, x1, y1, min(edge)
    bal = ctx.room_poly('balcony')
    xs, ys = [p[0] for p in bal], [p[1] for p in bal]
    return min(xs) - .035, max(xs) + .035, max(ys) + .006, fz - .15


def _fairy_lights(ctx, L):
    """White icicle light strings clipped under the outer edge of the balcony tray along its front and both sides,
    drops 0.3 - 0.5 (rear_elevation.md 4, v11 t188). Off in daylight; a click lights the whole set."""
    x0, x1, y1, ze = _balcony_edge(ctx, L)
    o, z = .012, ze - .015
    run = [(x0 - o, L.yr + .06), (x0 - o, y1 + o), (x1 + o, y1 + o), (x1 + o, L.yr + .06)]
    white = M.mat('plastic_white')
    mb, bulbs, d, k = mo.MB(), [], .06, 0
    for (ax, ay), (bx, by) in zip(run, run[1:]):                    # 15 x 15 clip strip on the frame: a target you can click
        mb.box((min(ax, bx) - .0075, min(ay, by) - .0075, z), (max(ax, bx) + .0075, max(ay, by) + .0075, z + .015), white, bev=.002)
    for (ax, ay), (bx, by) in zip(run, run[1:]):
        Ln = math.hypot(bx - ax, by - ay)
        while d < Ln:
            x, y = ax + (bx - ax) * d / Ln, ay + (by - ay) * d / Ln
            drop = (.30, .50, .38, .44, .34)[k % 5]
            mb.tube([(x, y, z), (x, y, z - drop)], .0018, white, 3)
            bulbs += [(x, y, z - s * .05) for s in range(1, int(drop / .05) + 1)]
            d, k = d + .115, k + 1
        d -= Ln
    body = mb.finish('garden.fairy_lights')
    lit = _octas('garden.fairy_lights.glow', bulbs, .0075, P.emissive('#FFD9A0', 12.0))
    G.click_glow(ctx, ROOM, body, lit, 'Fairy lights', reach=2.4)
    bulbs = _octas('garden.fairy_lights.bulbs', bulbs, .0055, white)
    IX.tag(bulbs, 'trigger', g=body.name, label='Fairy lights', reach=2.4)
    _add(ctx, bulbs, 'fit')


def _doorbell(ctx, L):
    black = M.mat('black_gloss')
    mb = mo.MB()
    mb.box((-.03, -.024, -.065), (.03, 0, .065), black, bev=.006)
    mb.at(T(0, -.024, .03) @ Matrix.Rotation(pi / 2, 4, 'X'))
    mb.lathe([(.013, 0), (.013, .002), (0, .002)], col('flood_lens', '#8A8E92', .2), 12)       # camera
    mb.at(T(0, -.024, -.03) @ Matrix.Rotation(pi / 2, 4, 'X'))
    mb.lathe([(.016, 0), (.016, .003), (.012, .003), (.012, .001), (0, .001)], M.mat('silver_satin'), 12)   # button ring
    _add(ctx, P.place(mb.at().finish('garden.doorbell'), (2.07, L.yr + .001, 1.25), facing=(0, 1)), 'fit')


def _post_face(px, py):
    """Point on the garden face of an east fence post and the unit normal toward the garden."""
    (xa, ya), (xb, yb) = _fence_line()
    d = V((xb - xa, yb - ya, 0)).normalized()
    n = V((-d.y, d.x, 0)) if -d.y < 0 else V((d.y, -d.x, 0))       # points to -X (the garden)
    return V((px, py, 0)) + n * .052, n


def _fence_box(ctx, posts):
    """White weatherproof box 0.22 x 0.30 x 0.10 high on the passage fence post by the step, black conduit down the
    post into the ground (v11 f_0053-f_0060)."""
    px, py, top = min(posts, key=lambda p: abs(p[1] - 17.4))
    p, n = _post_face(px, py)
    gz = ctx.ground_z(p.x - .1, p.y)
    gz = -0.30 if gz is None else gz
    mb = mo.MB()
    white, black = M.mat('plastic_white'), M.mat('black_matt')
    z1 = min(top - .06, 1.64)
    mb.box((-.11, -.1, z1 - .30), (.11, 0, z1), white, bev=.008)                               # local -Y = away from the post
    mb.box((-.105, -.102, z1 - .295), (.105, -.1, z1 - .005), col('box_lid', '#E6E6E2', .5))  # lid seam
    for x in (-.08, .08):                                                                      # lid screws
        mb.at(T(x, -.101, z1 - .03) @ Matrix.Rotation(pi / 2, 4, 'X'))
        mb.lathe([(.006, 0), (.006, .004), (0, .004)], M.mat('silver_satin'), 8)
        mb.at()
    mb.tube([(.0, -.03, z1 - .30), (.0, -.03, z1 - .36), (.0, -.016, z1 - .42), (.0, -.016, gz - .02)], .011, black, 8)
    for z in (z1 - .6, z1 - 1.2, gz + .25):                                                   # saddle clips
        mb.box((-.02, -.03, z), (.02, 0, z + .02), black)
    ob = P.place(mb.finish('garden.fence_box'), (p.x, p.y, 0), facing=tuple(n.xy))
    _add(ctx, ob, 'fit')


# ---------------------------------------------------------------- bird table, feeding station, backdrop
def _birds(ctx, L, posts):
    """Small pitched-roof bird table on a post strapped to the east fence post by the lawn (v13 t216: on the post at
    y about 23.2, roof about 2.45 above the path), and the black shepherd's-crook feeding station at the lawn's SE
    corner (phase3 3.1: pole at (3.19, 21.76))."""
    wood, black = col('birdtable', '#6E5A44', .85), M.mat('black_matt')
    fx, fy, _ = min(posts, key=lambda p: abs(p[1] - 23.17))
    p, n = _post_face(fx, fy)
    x, y = p.x - .025, p.y
    mb = mo.MB()
    mb.box((x - .025, y - .025, 1.25), (x + .025, y + .025, 1.80), wood, bev=.003)             # post strapped to the fence post
    for z in (1.32, 1.62):
        mb.box((x - .03, y - .03, z), (x + .024, y + .03, z + .025), M.mat('silver_satin'))   # straps
    mb.prism([(x - .02, y - .006, 1.45), (x - .2, y - .006, 1.78), (x - .17, y - .006, 1.78), (x - .02, y - .006, 1.50)], (0, .012, 0), black)
    xc = x - .155                                                                               # roof eaves clear of the fence post
    mb.box((xc - .15, y - .12, 1.80), (xc + .15, y + .12, 1.815), wood, bev=.002)
    for sx in (-.13, .13):
        for sy in (-.10, .10):
            mb.box((xc + sx - .008, y + sy - .008, 1.815), (xc + sx + .008, y + sy + .008, 1.93), wood)
    for s in (-1, 1):                                                                           # two roof slabs, ridge along X
        mb.at(T(xc, y, 2.01) @ Matrix.Rotation(math.radians(38 * s), 4, 'X'))
        mb.box((-.17, 0 if s < 0 else -.17, -.008), (.17, .17 if s < 0 else 0, .004), wood, bev=.002)
    _add(ctx, mb.at().finish('garden.bird_table'))

    # feeding station (v11 t194, v2:f_0205): pole ~2.0 above the grass, four shepherd's-crook arms curling out at the top,
    # seed tubes and a peanut feeder hanging from them, a white dish and a mesh tray on brackets part-way up
    px, py, top = 3.19, 21.76, L.lawn + 2.02
    mb = mo.MB()
    mb.tube([(px, py, L.lawn - .1), (px, py, top)], .008, black, 6)
    mb.at(T(px, py, top))
    mb.lathe([(.008, 0), (.012, .02), (0, .045)], black, 6)                                     # finial
    mb.at()
    hang = []
    for k, (a, reach) in enumerate(((0.5, .25), (2.1, .22), (3.7, .25), (5.2, .2))):
        c, s = cos(a), sin(a)
        z0 = top - .30 - .05 * (k % 2)
        pts = G.chaikin([(px, py, z0 - .12), (px + .03 * c, py + .03 * s, z0 + .06), (px + reach * .55 * c, py + reach * .55 * s, z0 + .2),
                         (px + reach * .95 * c, py + reach * .95 * s, z0 + .12), (px + reach * c, py + reach * s, z0 - .02),
                         (px + reach * .9 * c, py + reach * .9 * s, z0 - .06)])
        mb.tube(pts, .0045, black, 4, up=(-s, c, 0))                                          # up = arm-plane normal
        hang.append((px + reach * .9 * c, py + reach * .9 * s, z0 - .06))
    green, wire = col('feeder_green', '#2F5E48', .4), col('feeder_wire', '#7A7E80', .4, .6)
    seed = col('feeder_seed', '#9A8862', .9)
    (ax, ay, az), (bx, by, bz), (cx_, cy_, cz), (dx_, dy_, dz) = hang
    mb.at(T(ax, ay, az - .40))                                                                  # mesh peanut feeder, green caps
    mb.lathe([(0, 0), (.05, 0), (.05, .03), (.044, .03), (.044, .28), (.05, .28), (.05, .31), (.02, .335), (0, .34)], wire, 12)
    for zc in (0, .28):
        mb.lathe([(0, zc - .002), (.052, zc - .002), (.052, zc + .032), (.02, zc + .05 if zc else zc + .04), (0, zc + .05)], green, 12)
    for hx, hy, hz in ((bx, by, bz), (dx_, dy_, dz)):                                          # two seed tubes
        mb.at(T(hx, hy, hz - .36))
        mb.lathe([(0, 0), (.034, 0), (.034, .30), (0, .30)], seed, 10)
        mb.lathe([(0, -.005), (.04, -.005), (.04, .02), (0, .02)], green, 10)
        mb.lathe([(0, .29), (.04, .29), (.04, .31), (0, .33)], green, 10)
        for zp in (.08, .2):                                                                    # perches
            mb.tube([(-.055, 0, zp), (.055, 0, zp)], .003, green, 4)
    mb.at(T(cx_, cy_, cz - .22))                                                                # small fat-ball cage
    mb.box((-.05, -.05, 0), (.05, .05, .13), wire)
    mb.at()
    for q, d in ((hang[0], .06), (hang[1], .06), (hang[2], .09), (hang[3], .06)):
        mb.tube([q, (q[0], q[1], q[2] - d)], .0015, black, 3)
    for a, kind in ((-.4, 'dish'), (1.2, 'tray')):                                              # brackets at ~1.3 above the grass
        c, s = cos(a), sin(a)
        zb = L.lawn + 1.28
        mb.tube([(px, py, zb), (px + .17 * c, py + .17 * s, zb)], .005, black, 4)
        mb.at(T(px + .17 * c, py + .17 * s, zb - .025))
        if kind == 'dish':
            mb.lathe([(0, 0), (.08, 0), (.11, .035), (.104, .035), (.074, .008), (0, .008)], M.mat('plastic_white'), 14)
        else:
            mb.box((-.12, -.12, 0), (.12, .12, .006), wire)
            mb.box((-.125, -.125, .006), (.125, .125, .025), black)
            mb.box((-.115, -.115, .006), (.115, .115, .026), wire)
        mb.at()
    _add(ctx, mb.finish('garden.bird_feeder'))


def _backdrop(ctx, L):
    """Backdrop only (garden.md 7, phase3 3.3): the big sycamore beyond the shed's NE corner and the east fence, its
    crown over the shed roof; a dark evergreen mass in the east neighbour's garden beside the lawn; tall bamboo and
    evergreen clumps west of the shed behind the west fence. Leaf cards on low-poly cores, nothing to walk to;
    everything clear of the shed (outline + coping) and of our side of the east fence."""
    rng = random.Random(41)
    sx0, sx1, sy0, sy1 = L.shed
    stop = L.shed_top + .25
    out_shed = lambda p: not (sx0 - .12 < p.x < sx1 + .12 and sy0 - .12 < p.y < sy1 + .12 and p.z < stop)
    beyond = lambda p: p.x > fence_x(p.y) + .08 or p.z > 2.3
    bark = col('tree_bark', '#5A5048', .9)
    mb, ls, ld = mo.MB(), [], []
    # the sycamore: trunk in the neighbour's garden east of the shed, crown spreading over the shed roof and the path,
    # lowest leaves ~3 m (v11 t59, t186; v13 t216)
    tx, ty = sx1 + 1.15, (sy0 + sy1) / 2 + .4
    fork = V((tx - .15, ty - .2, 3.7))
    mb.tube(G.chaikin([(tx, ty, -.5), (tx - .05, ty - .1, 1.9), fork], 1), .22, bark, 8)

    def crown(c, r, n, out, base, limbs=5, per=380, core=None, keep=None):
        """Limbs from `base`, n leafy clusters on twigs from the nearest limb (an evergreen gets a dense core)."""
        ends = []
        for i in range(limbs):
            a = 2 * pi * (i + rng.uniform(-.2, .2)) / limbs
            e = V((c[0] + .6 * r[0] * cos(a), c[1] + .6 * r[1] * sin(a), c[2] + rng.uniform(-.2, .4) * r[2]))
            if not out_shed(e):
                e.z = stop + .3
            mb.tube(G.chaikin([base, base.lerp(e, .45) + V((0, 0, .5)), e], 1), .09, bark, 6)
            ends.append(e)
        for _ in range(n):
            u = V((rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, .8))).normalized() * rng.uniform(.3, 1)
            p = V((c[0] + u.x * r[0], c[1] + u.y * r[1], c[2] + u.z * r[2]))
            k = rng.uniform(.65, 1.15)
            if not out_shed(p - V((0, 0, .75 * k))):                # cluster bottom would sink into the shed
                p.z = stop + .75 * k
            mb.tube([min(ends, key=lambda q: (q - p).length), p], .03, bark, 4)
            if core:
                mb.at(T(p.x, p.y, p.z - .45 * k, rng.uniform(0, 90)))
                mb.dome(.62 * k, .55 * k, .95 * k, core, 10, 3)
                mb.at()
            out += G.blob(rng, (p.x, p.y, p.z), (.9 * k, .8 * k, .7 * k), int(per * k), .2, .17, 4, droop=.35,
                          shell=.7 if core else .15, lo=-.7, keep=keep)
    keep_tree = lambda p: out_shed(p) and beyond(p)
    crown((tx - .6, ty, 6.2), (3.1, 2.8, 2.1), 24, ls, fork, keep=keep_tree)
    # low limbs over the shed's NE corner and the end of the path, down to just above the coping (v11 t186)
    crown((sx1 + .2, sy0 + 1.0, stop + .9), (.9, 1.1, .45), 7, ls, fork, limbs=2, per=320, keep=keep_tree)
    mb.tube([fork, fork + V((-.1, .1, 2.2))], .14, bark, 7)                                       # leader
    crown((tx - .2, ty + .6, 8.6), (2.0, 1.8, 1.0), 7, ls, fork + V((-.1, .1, 2.2)), limbs=3, keep=keep_tree)
    # shrubs in the east neighbour's garden beside the lawn, about a metre over the fence top (v13 t216, v11 t194)
    ey = (L.y1 + L.lawn_y1) / 2
    base2 = V((fence_x(ey) + 1.9, ey, .6))
    crown((base2.x, ey - .2, 2.2), (1.5, 2.3, .8), 18, ld, base2, limbs=4, per=300, keep=beyond)
    # bamboo clumps in the west neighbour's garden behind the shed's west wall (v13 t216: paving beside the shed front,
    # tall grass and bamboo further back); narrow leaves that never cross the boundary line
    hedge_core = col('hedge_core', '#3E5434', 1.0)
    cores = ((sx0 - 1.1, sy0 + 2.8, .8, 2.9), (sx0 - 1.0, sy0 + 4.2, .75, 2.8))
    for x, y, r, h in cores:
        mb.at(T(x, y, -.5))
        mb.dome(r, .75, h, hedge_core, 8, 3)
    # and the evergreen hedge beyond the west neighbour's patio (v2 f_0199 / f_0203, v11 t188 / t189; v13 t216 shows
    # ~1.5 m of their paving behind our fence, so it stands beyond that): one continuous, flat-topped, mid-green mass
    # seen about 0.3 m over our fence from the deck (v11 t189). Its core is a box, its leaves small cards over the
    # gently uneven top and the faces toward us
    wy0, wy1 = L.y1 + .1, L.bed[3]
    hx0, hx1, htop = L.x0 - 2.15, L.x0 - 1.55, 1.9                 # 0.3-0.4 m over the fence in v11 t189 (wall end = scale)
    bump = lambda y: .04 * sin(2.3 * y) + .025 * sin(5.1 * y + 1.0)
    mb.at()
    mb.box((hx0, wy0, -.5), (hx1, wy1, htop - .14), hedge_core)
    mb.at()
    _add(ctx, mb.finish('garden.backdrop'))
    tree = leafmats('sycamore', ('#8E9C48', '#A6A852', '#7A8C42', '#B4AC5A'), .7)
    _add(ctx, G.cards('garden.backdrop.tree', ls, tree))
    _add(ctx, G.cards('garden.backdrop.evergreen', ld, leafmats('evergreen', ('#4E6A44', '#5C7A4E', '#456040', '#6E8650'), .8)))
    hedge = leafmats('hedge', ('#56723F', '#62804A', '#4C6838', '#70884F', '#A9A57C'), .85)   # the last: pale grass
    west = lambda p: p.x < sx0 - .05 and p.y > L.y1 + .06            # clear of the neighbour's extension (to the deck edge)
    lh = []
    for x, y, r, h in cores:                                        # bamboo: long narrow leaves
        lh += G.blob(rng, (x, y, -.5), (r + .1, .85, h + .1), 320, .16, .035, 4, droop=.2, shell=.85, lo=.05, keep=west)
    zf = 1.1                                                        # below this the fence hides it
    top_a, face_a, end_a = (hx1 - hx0) * (wy1 - wy0), (htop - zf) * (wy1 - wy0), (hx1 - hx0) * (htop - zf)
    for _ in range(3200):
        u = rng.uniform(0, top_a + face_a + end_a)
        y = rng.uniform(wy0 + .05, wy1 - .05)
        if u < top_a:                                               # top
            nrm, p = V((0, 0, 1)), V((rng.uniform(hx0 + .03, hx1 + .03), y, htop - .08 + bump(y) + rng.uniform(-.03, .04)))
        elif u < top_a + face_a:                                    # face toward our fence
            nrm, p = V((1, 0, 0)), V((hx1 + rng.uniform(-.02, .05), y, rng.uniform(zf, htop - .06 + bump(y))))
        else:                                                       # north end, seen from the lawn
            y = wy1
            nrm, p = V((0, 1, 0)), V((rng.uniform(hx0, hx1), wy1 + rng.uniform(-.02, .05), rng.uniform(zf, htop - .06 + bump(y))))
        d = (nrm * .6 + V((rng.uniform(-.8, .8), rng.uniform(-.8, .8), rng.uniform(-.8, .4)))).normalized()
        lh.append((p, p + d * rng.uniform(.07, .12), rng.uniform(.045, .06), nrm + V((0, 0, .7)), rng.randrange(4)))
    # tall pale ornamental grass west of the shed, from just behind its front to the alley (v13 t216), its plumes over
    # the north end of our west fence (v2 f_0199, v11 t189)
    for cx, cy in ((sx0 - .45, sy0 + 2.0), (sx0 - .55, sy0 + 3.3), (sx0 - 1.2, sy0 + 1.4), (sx0 - 1.5, sy0 + 2.5)):
        for _ in range(110):
            b = V((cx + rng.uniform(-.15, .15), cy + rng.uniform(-.2, .2), -.45))
            a, h = rng.uniform(0, 2 * pi), rng.uniform(1.8, 2.7)
            t = b + V((cos(a) * rng.uniform(.2, .6), sin(a) * rng.uniform(.2, .6), h))
            if t.x < sx0 - .03:
                lh += [(b, t, .016, V((cos(a), sin(a), 0)), 4)]
    _add(ctx, G.cards('garden.backdrop.hedge', lh, hedge))


def build(ctx):
    L = _layout(ctx)
    _fence_line(ctx)
    posts = _fence_posts()
    _fire_pit(ctx)
    rim = _planters(ctx, L)
    _trellis(ctx, L, rim + .001)
    _pots(ctx, L)
    _chairs(ctx, L)
    _lavender(ctx, L)
    _, _, fy0, fy1 = _bb(ctx.zone('garden_path')['polygon'])
    span = fy1 - fy0                                                # strands spread along the garden's stretch of fence
    climbers(ctx, ROOM, 'garden.climbers', [fy0 + span * t for t in (.06, .25, .42, .6, .78, .93)], 9,
             rise=[fy0 + .25, fy0 + span * .52])
    _floodlight(ctx, L)
    _fairy_lights(ctx, L)
    _doorbell(ctx, L)
    _fence_box(ctx, posts)
    _birds(ctx, L, posts)
    _backdrop(ctx, L)

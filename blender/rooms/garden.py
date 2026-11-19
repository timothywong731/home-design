"""Rear garden (pseudo-room `garden`, level X): what stands on the deck, lawn and path that site / envelope did not
build - fire pit (lights on a click), trellis panels, slatted planters and their planting, pots, the two folding
chairs, lavender hedge, fence climbers, PIR floodlight and fairy lights (click to light), doorbell, bird table and
feeding station, and the trees behind the shed. Spec: spec/rooms/garden.md, spec/phase2/rear_elevation.md.

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --levels G,X --only shell,site,envelope,garden,side_passage \
        --preview garden --res 540x960 --samples 64 --tag garden          (--pose 1 --tag garden1: fire lit, lights on)

Sky-lit only: no lamps here. The floodlight and the fairy lights are off as modelled (daylight) and glow in state 1.
Everything is lm='dynamic' (see garden_parts). Refs are frames of reference/v2."""
import math
import random
from math import sin, cos, pi

import bpy
from mathutils import Matrix, Vector as V

from lib import interact as IX, materials as M, mouldings as mo, props as P
from rooms import garden_parts as G
from rooms.garden_parts import T, col, leafmats

ROOM = 'garden'
DECK, LAWN = -0.05, -0.45           # zone levels (house.json exterior.zones)
YR, XW = 17.36, -0.75               # rear wall face, west boundary (neighbour's brick wall / fence line)

CAMERAS = [
    dict(name='house', pos=(2.1, 23.75, 1.1), look=(1.35, 17.4, 2.5), fov_deg=100, ref='f_0251'),
    dict(name='deck_w', pos=(1.7, 17.8, 1.55), look=(-0.6, 19.5, 0.3), fov_deg=100, ref='f_0155'),
    dict(name='deck_e', pos=(1.5, 17.55, 1.5), look=(3.6, 18.4, 0.0), fov_deg=100, ref='f_0161'),
    dict(name='rear', pos=(1.9, 20.2, 1.5), look=(1.6, 17.4, 1.7), fov_deg=95, ref='f_0177'),
    dict(name='lawn', pos=(2.7, 20.3, 1.55), look=(0.4, 22.6, -0.2), fov_deg=100, ref='f_0203'),
    dict(name='firepit', pos=(2.35, 21.2, 0.95), look=(1.27, 22.26, -0.3), fov_deg=80, ref='f_0193'),
    dict(name='lavender', pos=(0.75, 20.1, 1.5), look=(-0.55, 22.4, 0.0), fov_deg=100, ref='f_0199'),
    dict(name='path', pos=(3.85, 23.1, 1.15), look=(3.7, 17.5, 0.6), fov_deg=95, ref='f_0311'),
    dict(name='east', pos=(0.6, 20.0, 1.55), look=(4.6, 21.6, 0.9), fov_deg=100, ref='f_0205'),
    dict(name='shed', pos=(1.2, 18.6, 1.55), look=(2.2, 24.0, 1.3), fov_deg=95, ref='f_0189'),
    dict(name='above', pos=(1.3, 18.9, 8.2), look=(1.6, 22.0, -0.4), fov_deg=80, ref='v4 f_0467'),
]


def fence_x(y):
    """East fence line (house.json east_fence): straight, converging on the house."""
    return 4.9 - 0.45 * (y - 9.88) / 13.52


def _add(ctx, ob, kind='decor', sym=None):
    return ctx.add(ob, ROOM, kind, plan_sym=sym, lm='dynamic')


# ---------------------------------------------------------------- fire pit
def _fire_pit(ctx):
    """Square brick fire pit (garden.md 3.4): two stretcher courses, a top course of headers laid flat, pinwheel
    corners; ash bed and charred logs inside (the click target); flames show in state 1."""
    f = next(x for x in ctx.spec['exterior']['features'] if x['id'] == 'fire_pit')
    (cx, cy), w, tw, z0 = f['center'], f['size'][0], f['wall'], f['baseZ']
    rng, h2 = random.Random(3), f['size'][0] / 2
    tones = [col(f'firebrick_{i}', h, .85) for i, h in enumerate(('#C9AC72', '#D3B77F', '#BFA068', '#CDB684', '#B59A64'))]
    moss, mortar = col('firebrick_moss', '#9A9A62', .9), col('fire_mortar', '#A89878', .95)
    mb = mo.MB()
    run = w - tw                                                    # each side runs from its corner to the next side
    for k in range(4):                                              # k = 0 south, 1 east, 2 north, 3 west
        mb.at(T(cx, cy, z0, 90 * k))
        mb.box((-h2 + .005, -h2 + .005, 0), (h2 - tw - .005, -h2 + tw - .005, .21), mortar)
        for c in (0, 1):                                            # stretcher courses, two wythes, half-bond
            for ya, yb in ((-h2, -h2 + .1025), (-h2 + tw - .1025, -h2 + tw)):
                x = -h2
                first = .1025 if c else .215
                while x < -h2 + run - .02:
                    L = min(first, -h2 + run - x)
                    mb.box((x, ya, c * .075), (x + L, yb, c * .075 + .065), moss if k == 3 and rng.random() < .3 else rng.choice(tones), bev=.004)
                    x, first = x + L + .01, .215
        p = (run + .01) / 7                                         # headers flat: 7 a side + the next side's flank
        for i in range(7):
            mb.box((-h2 + i * p, -h2, .15), (-h2 + (i + 1) * p - .01, -h2 + tw, .215),
                   moss if k == 3 and rng.random() < .45 else rng.choice(tones), bev=.004)
    ring = mb.at().finish('garden.fire_pit')
    _add(ctx, ring, 'fit', 'fire_pit')

    # bed of dark soil one course below the rim (v2:f_0193: visible, not a black hole), a few charred logs and the
    # pale dried stems lying across it / standing up (garden.md 3.4); the whole bed is the click target
    zb = z0 + .11
    soil, char, stem = col('fire_soil', '#4A4136', 1.0), col('fire_char', '#3A332D', .9), col('fire_stem', '#9C8C6A', .8)
    mb = mo.MB()
    hi = h2 - tw + .004
    mb.box((cx - hi, cy - hi, z0 + .02), (cx + hi, cy + hi, zb), soil)
    for a, r, L, dz in ((20, .035, .40, .025), (95, .03, .36, .03), (150, .04, .32, .035)):
        d = V((cos(math.radians(a)), sin(math.radians(a)), .06))
        c = V((cx + rng.uniform(-.04, .04), cy + rng.uniform(-.04, .04), zb + dz))
        mb.tube([c - d * L / 2, c + d * L / 2], r, char, 6)
    for k in range(14):
        x, y = cx + rng.uniform(-.2, .2), cy + rng.uniform(-.2, .2)
        if k < 4:                                                   # standing, splayed a little
            a, h = rng.uniform(0, 2 * pi), rng.uniform(.18, .32)
            mb.tube([(x, y, zb), (x + .2 * h * cos(a), y + .2 * h * sin(a), zb + h)], .003, stem, 4)
        else:                                                       # lying across the bed
            a, L = rng.uniform(0, pi), rng.uniform(.18, .34)
            dx, dy = L / 2 * cos(a), L / 2 * sin(a)
            mb.tube([(x - dx, y - dy, zb + .004), (x + dx, y + dy, zb + .012)], .003, stem, 4)
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
def _trellis_mesh(w=.90, hs=1.25, hc=1.50, fr=.035):
    """Arched lattice panel (garden.md 6). Local: back on x = 0, width along +Y from 0, foot at z = 0."""
    mat = col('trellis', '#6E5A44', .8)
    top = lambda u: hs + (hc - hs) * (1 - cos(pi * (1 - abs(2 * u / w - 1)))) / 2
    n = 16
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
    lo, hw, step = fr / 2, .015, .15                                 # laths 30 x 8 in two layers, cells ~0.11

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


def _trellis(ctx):
    first = _trellis_mesh()
    for i, y in enumerate((17.85, 18.75)):
        ob = bpy.data.objects.new(f'garden.trellis.{i}', first.data) if i else first
        ob.location = (XW + .002, y, DECK)
        _add(ctx, ob, 'fit', 'trellis')


# ---------------------------------------------------------------- planters and what grows in them
def _planters(ctx):
    rng = random.Random(11)
    leaves = {}                                                     # name -> (materials, leaf list)
    soil = P.mat('soil')

    def grow(name, mats, ls):
        leaves.setdefault(name, (mats, []))[1].extend(ls)

    # two west planters under the trellis: geraniums and green foliage in the first, low herbs in the second
    mb = mo.MB()
    x0, x1 = XW + .04, XW + .44
    zf = G.planter(mb, x0, x1, 17.65, 18.64, DECK, .42)
    G.planter(mb, x0, x1, 18.66, 19.65, DECK, .42)
    _add(ctx, mb.finish('garden.planter.west'), 'furn', 'planter')
    wall = lambda p: p.x > XW + .045
    ger = leafmats('geranium', ('#6FAE4C', '#82BE5A', '#5E9C44'))
    red = leafmats('geranium_red', ('#D8402A', '#E2553A'), .6)
    herb = leafmats('herb', ('#5F9048', '#74A656', '#8EAE64'))
    cg = (x0 + .22, 17.97, zf + .17)
    lg = G.blob(rng, cg, (.30, .34, .24), 420, .06, .07, 3, droop=.15, shell=.35, lo=-.45, keep=wall)
    lr = [(p + V((0, 0, .03)), t + V((0, 0, .05)), .022, n, k % 2)
          for p, t, hw, n, k in G.blob(rng, cg, (.31, .35, .27), 46, .04, .04, 2, droop=-.6, shell=.9, lo=.05, keep=wall)]
    lh = G.blob(rng, (x0 + .2, 18.42, zf + .16), (.16, .2, .2), 110, .08, .06, 3, shell=.3, lo=-.3, keep=wall)
    lh += G.blob(rng, (x0 + .18, 19.25, zf + .05), (.14, .25, .09), 90, .05, .03, 3, shell=.2, lo=0, keep=wall)
    _add(ctx, G.cards('garden.planter.west.geranium', lg, ger))
    _add(ctx, G.cards('garden.planter.west.flowers', lr, red))
    grow('herbs', herb, lh)

    # NW corner: square planter with a pyracantha (red berries), terracotta pot of trailing thyme on feet
    mb = mo.MB()
    zc = G.planter(mb, XW + .05, XW + .45, 19.75, 20.15, DECK, .40)
    px, py = XW + .25, 19.95
    bark = col('bark', '#5B4A3A', .85)
    for a in (0.3, 2.2, 4.1, 5.3):
        mb.tube(G.chaikin([(px, py, zc), (px + .05 * cos(a), py + .05 * sin(a), zc + .3), (px + .16 * cos(a), py + .16 * sin(a), zc + .62)], 1),
                .006, bark, 4)
    _add(ctx, mb.finish('garden.planter.corner'), 'furn', 'planter')
    pyr = leafmats('pyracantha', ('#4C7040', '#5A8046', '#426436'))
    lp = G.blob(rng, (px, py, zc + .40), (.20, .20, .32), 260, .04, .022, 3, droop=.0, shell=.15, keep=wall)
    berry = [(p, t, .014, n, 0) for p, t, hw, n, k in G.blob(rng, (px, py, zc + .40), (.19, .19, .28), 50, .022, .02, 1, shell=.5, keep=wall)]
    grow('pyracantha', pyr, lp)
    _add(ctx, G.cards('garden.planter.corner.berries', berry, leafmats('berry', ('#C8321E',), .4)))
    mb = mo.MB()
    zs = G.pot(mb, XW + .60, 20.25, DECK, .175, .30, P.mat('terracotta'), feet=.03, belly=.6)
    _add(ctx, mb.finish('garden.pot.thyme'), 'furn', 'plant')
    thyme = leafmats('thyme', ('#8E9F7A', '#9CAC88', '#7C8E6C'))
    grow('thyme', thyme, G.blob(rng, (XW + .60, 20.25, zs + .01), (.21, .21, .12), 220, .05, .02, 3, droop=.8, shell=.3, lo=-.35))

    # pebble planter under the east rear window (river cobbles to the brim) with the wisteria
    mb = mo.MB()
    px0, px1, py0, py1 = 2.30, 3.30, YR + .04, YR + .46
    zp = G.planter(mb, px0, px1, py0, py1, DECK, .36, drop=.05)
    stones = [col(f'cobble_{i}', h, .55) for i, h in enumerate(('#8E8E8A', '#A9A294', '#B79C8E', '#6F7072', '#C2B8A4', '#9A8478'))]
    for _ in range(95):
        x, y = rng.uniform(px0 + .06, px1 - .06), rng.uniform(py0 + .06, py1 - .06)
        mb.at(T(x, y, zp - .012 + rng.uniform(0, .02), rng.uniform(0, 180)))
        mb.dome(rng.uniform(.03, .06), rng.uniform(.025, .045), rng.uniform(.022, .04), rng.choice(stones), 6, 2)
    mb.at()
    # wisteria: bamboo canes, twisting stems, wall-trained leader up the east margin of the rear wall to z 3.0
    cane, stem = col('bamboo', '#B9A56A', .6), col('wisteria_stem', '#6A5A46', .85)
    bx, by = 3.0, YR + .25
    for dx, dy in ((-.3, .02), (-.12, .1), (.0, -.04), (.14, .08), (.24, -.02)):
        mb.tube([(bx + dx * .3, by + dy * .5, zp), (bx + dx, by + dy, zp + 1.3)], .006, cane, 5)
    for k, (dx, dy) in enumerate(((-.22, .06), (.05, .1), (.2, .0))):
        mb.tube(G.chaikin([(bx + .02 * k, by, zp), (bx + dx * .4, by + .05, zp + .35), (bx + dx * .5, by + dy, zp + .7), (bx + dx, by + dy * .5, zp + 1.1)]),
                .008, stem, 5)
    leader = G.chaikin([(bx + .12, by - .1, zp + .3), (3.12, YR + .04, 1.0), (3.2, YR + .03, 1.6), (3.14, YR + .03, 2.2), (3.24, YR + .03, 2.75),
                        (3.18, YR + .03, 3.0)])
    mb.tube(leader, .006, stem, 4)
    _add(ctx, mb.finish('garden.planter.pebble'), 'furn', 'planter')
    wis = leafmats('wisteria', ('#8FB45A', '#9EC064', '#7EA650', '#B4BE62'))
    clear = lambda p: p.y > YR + .03
    lw = G.blob(rng, (bx - .02, by + .07, zp + .78), (.45, .30, .52), 1300, .095, .042, 4, droop=.35, shell=.3, keep=clear)
    lw += G.blob(rng, (3.19, YR + .1, 1.95), (.2, .09, .32), 160, .095, .042, 4, droop=.4, shell=.3, keep=clear)
    lw += G.strand(rng, leader[4:], 90, .095, .042, 4, (0, 1, 0))
    _add(ctx, G.cards('garden.wisteria', lw, wis))

    # east edge of the deck: long trough on feet (black liner, a few small plants), square planter with a bare rose
    mb = mo.MB()
    zt = G.planter(mb, 2.95, 3.37, 18.20, 20.05, DECK, .45, feet=.06, drop=.13, fill=M.mat('black_matt'))
    for y in (18.6, 19.3, 19.8):
        mb.at(T(3.16, y, zt))
        mb.dome(.12, .16, .03, soil, 8, 2)
    mb.at()
    _add(ctx, mb.finish('garden.planter.trough'), 'furn', 'planter')
    for y in (18.6, 19.3, 19.8):
        grow('herbs', herb, G.blob(rng, (3.16, y, zt + .04), (.09, .12, .1), 45, .06, .035, 3, shell=.2, lo=0))
    mb = mo.MB()
    zq = G.planter(mb, 2.95, 3.37, 20.07, 20.48, DECK, .50)
    twig = col('rose_twig', '#5E5A40', .8)
    for k in range(7):
        a, r = 2 * pi * k / 7 + .3, rng.uniform(.08, .2)
        mb.tube(G.chaikin([(3.16, 20.275, zq), (3.16 + r * .4 * cos(a), 20.275 + r * .4 * sin(a), zq + .3),
                           (3.16 + r * cos(a), 20.275 + r * sin(a), zq + rng.uniform(.55, .85))], 1), .004, twig, 4)
    _add(ctx, mb.finish('garden.planter.square'), 'furn', 'planter')
    for name, (mats, ls) in leaves.items():
        _add(ctx, G.cards('garden.planting.' + name, ls, mats))


def _pots(ctx):
    """Loose pots on the deck (garden.md 6): blue glazed pot with a small maple, black pot of rosemary, large
    terracotta pot with a bare cane, small grey pot with a spider plant by the door."""
    rng = random.Random(23)
    bark = col('bark', '#5B4A3A', .85)
    mb = mo.MB()
    z = G.pot(mb, 2.65, 18.8, DECK, .14, .25, col('pot_blue', '#6F8FA8', .15), feet=.02, belly=.7)
    mb.tube(G.chaikin([(2.65, 18.8, z), (2.66, 18.79, z + .25), (2.62, 18.82, z + .5)], 1), .005, bark, 4)
    _add(ctx, mb.finish('garden.pot.maple'), 'furn', 'plant')
    maple = leafmats('maple', ('#9CB858', '#C0BC5A', '#8AAA52'))
    lm = G.blob(rng, (2.63, 18.81, z + .36), (.22, .22, .2), 70, .08, .085, 3, droop=.3, shell=.3)
    _add(ctx, G.cards('garden.pot.maple.leaves', lm, maple))

    mb = mo.MB()
    z = G.pot(mb, 2.70, 19.5, DECK, .13, .22, col('pot_black', '#1E2024', .25), feet=.02, belly=1.0)
    _add(ctx, mb.finish('garden.pot.rosemary'), 'furn', 'plant')
    rosemary = leafmats('rosemary', ('#8CA080', '#9AAC8C', '#7C9272'))
    lr = G.blob(rng, (2.70, 19.5, z + .02), (.2, .2, .3), 260, .09, .014, 3, droop=0, shell=.25, lo=-.1, up=.9)
    _add(ctx, G.cards('garden.pot.rosemary.leaves', lr, rosemary))

    mb = mo.MB()
    z = G.pot(mb, 2.70, 20.2, DECK, .21, .35, P.mat('terracotta'), feet=.03)
    mb.tube([(2.70, 20.2, z), (2.71, 20.19, z + 1.25)], .006, col('pot_black', '#1E2024', .25), 5)       # cane
    for k in range(5):
        a = 1.3 * k
        mb.tube(G.chaikin([(2.70, 20.2, z), (2.70 + .06 * cos(a), 20.2 + .06 * sin(a), z + .3),
                           (2.70 + .2 * cos(a), 20.2 + .2 * sin(a), z + .45 + .08 * k)], 1), .0035, col('rose_twig', '#5E5A40', .8), 4)
    _add(ctx, mb.finish('garden.pot.terracotta'), 'furn', 'plant')

    mb = mo.MB()
    z = G.pot(mb, 0.20, YR + .38, DECK, .09, .15, col('pot_grey', '#5F6468', .5))
    _add(ctx, mb.finish('garden.pot.spider'), 'furn', 'plant')
    spider = leafmats('spider', ('#6F9A52', '#8DB068'))
    ls = []
    for k in range(26):
        a, r = rng.uniform(0, 2 * pi), rng.uniform(.12, .22)
        ls.append((V((0.20, YR + .38, z)), V((0.20 + r * cos(a), max(YR + .38 + r * sin(a), YR + .08), z + rng.uniform(-.05, .16))), .011, V((0, 0, 1)), k % 2))
    _add(ctx, G.cards('garden.pot.spider.leaves', ls, spider))


# ---------------------------------------------------------------- folding chairs
def _chair_mesh():
    """Reclining camping chair (garden.md 6), 0.60 x 0.65 x 1.05: grey tubular steel, mid-blue fabric.
    Local: faces +X, origin floor centre."""
    frame, cloth, pad = col('chair_frame', '#B4B8BC', .35, .8), col('chair_blue', '#6283B4', .9), col('chair_pad', '#3A3D42', .6)
    mb = mo.MB()
    r, up = .011, (0, 1, 0)
    for y in (-.28, .28):
        for a, b in (((.31, 0), (-.10, .44)), ((-.27, 0), (.24, .44)), ((-.12, .43), (.26, .45)), ((-.08, .40), (-.32, 1.02)),
                     ((-.19, .68), (.22, .655)), ((.22, .655), (.255, .45))):
            mb.tube([(a[0], y, a[1]), (b[0], y, b[1])], r, frame, 6, up=up)
        mb.box((-.14, y - .024, .685), (.20, y + .024, .705), pad, bev=.004)                 # arm pad
    for x, z in ((.31, .011), (-.27, .011), (-.32, 1.02), (.26, .45), (-.105, .425)):
        mb.tube([(x, -.28, z), (x, .28, z)], r, frame, 6)
    mb.box((-.10, -.268, .428), (.255, .268, .438), cloth, bev=.003)                          # seat
    mb.at(T(-.085, 0, .41) @ Matrix.Rotation(math.radians(-21.2), 4, 'Y'))
    mb.box((-.004, -.268, 0), (.006, .268, .66), cloth, bev=.003)                             # back
    mb.box((.004, -.19, .47), (.05, .19, .63), cloth, bev=.02)                                # head cushion
    return mb.at().finish('garden.chair.0')


def _chairs(ctx):
    first = _chair_mesh()
    for i, y in enumerate((18.37, 19.02)):
        ob = bpy.data.objects.new(f'garden.chair.{i}', first.data) if i else first
        ob.location = (0.20, y, DECK)
        _add(ctx, ob, 'furn', 'chair')


# ---------------------------------------------------------------- lavender, climbers
def _lavender(ctx):
    """'Lots of lavender by the side': a continuous hedge of grey-green mounds 0.45 high x 0.5 wide in the bed
    along the west fence, deck to shed pier. No flowers (November)."""
    rng = random.Random(5)
    body = col('lavender_body', '#9DA68C', 1.0)                     # same tone as the leaves: reads as one soft mass
    mats = [P.two_sided(col(f'lavender_{i}', G._mute(h, .1), .8)) for i, h in enumerate(('#A9B394', '#B5BC9E', '#9AA587'))]
    mb, ls = mo.MB(), []
    for i in range(8):                                              # seven overlapping mounds to the shed pier, a small one by the step
        x, y = (XW + .27 + rng.uniform(-.02, .02), 21.05 + i * .34) if i < 7 else (XW + .115, 20.68)
        rx, ry, h = (rng.uniform(.25, .27), rng.uniform(.28, .31), rng.uniform(.44, .50)) if i < 7 else (.085, .12, .30)
        mb.at(T(x, y, LAWN))
        mb.dome(rx, ry, h * .85, body, 10, 3)
        ls += G.blob(rng, (x, y, LAWN + .02), (rx + .03, ry + .03, h), 700 if i < 7 else 120, .06, .03, 3, droop=.1, shell=.4,
                     lo=.0, up=.3, keep=lambda p: p.x > XW + .07 and p.y < 23.38)
    _add(ctx, mb.at().finish('garden.lavender'), 'decor', 'planter')        # a hedge: blocks the walker, drawn as a bed
    _add(ctx, G.cards('garden.lavender.leaves', ls, mats))


def climbers(ctx, room, name, ys, seed, top=1.70):
    """Thin passion-flower / ivy strands hanging down the painted east fence at the given y (garden.md 7)."""
    rng = random.Random(seed)
    stem = col('climber_stem', '#5A6B3A', .8)
    mats = leafmats('ivy', ('#6C8F64', '#7CA06A', '#98B268'))
    mb, ls = mo.MB(), []
    for y in ys:
        x, n = fence_x(y) - .022, rng.randint(4, 6)
        z, pts = top - .02, []
        for k in range(n + 1):
            pts.append((fence_x(y) - .022, y, z))
            y, z = y + rng.uniform(-.22, .22), z - rng.uniform(.18, .3)
        pts = G.chaikin(pts, 1)
        mb.tube(pts, .003, stem, 3, up=(1, 0, 0))
        ls += G.strand(rng, pts, 7 * n, .075, .055, 3, (-1, 0, 0))
    ctx.add(mb.finish(name), room, 'decor', lm='dynamic')
    ctx.add(G.cards(name + '.leaves', ls, mats), room, 'decor', lm='dynamic')


# ---------------------------------------------------------------- lights, doorbell
def _floodlight(ctx):
    """Black LED flood with a PIR sensor on the door axis under the balcony (rear_elevation.md 3). Automatic in
    reality: here a click on the fitting lights it."""
    black, lens = M.mat('black_matt'), col('flood_lens', '#8A8E92', .2)
    tilt = T(0, -.045, 0) @ Matrix.Rotation(math.radians(25), 4, 'X')
    mb = mo.MB()
    mb.box((-.03, -.05, -.025), (.03, 0, .025), black, bev=.003)                               # wall bracket
    mb.at(tilt)
    mb.box((-.10, -.05, -.08), (.10, 0, .08), black, bev=.006)
    mb.box((-.086, -.052, -.066), (.086, -.049, .066), lens)
    mb.at()
    mb.box((-.028, -.05, -.16), (.028, -.004, -.105), black, bev=.004)                         # PIR
    mb.at(T(0, -.05, -.135) @ Matrix.Rotation(pi / 2, 4, 'X'))
    mb.dome(.02, .02, .014, M.mat('plastic_white'), 8, 2)
    body = P.place(mb.at().finish('garden.floodlight'), (1.225, YR, 2.58), facing=(0, 1))
    mb = mo.MB()
    mb.at(tilt)
    mb.face([(-.084, -.0535, -.064), (.084, -.0535, -.064), (.084, -.0535, .064), (-.084, -.0535, .064)], P.emissive('#FFD9A0', 10.0), (0, -1, 0))
    glow = P.place(mb.at().finish('garden.floodlight.glow'), (1.225, YR, 2.58), facing=(0, 1))
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


def _fairy_lights(ctx):
    """White icicle light strings clipped along the balcony tray's front and side edges, drops 0.3 - 0.5
    (rear_elevation.md 4). Off in daylight; a click lights the whole set."""
    bal = ctx.room_poly('balcony')
    xs, ys = [p[0] for p in bal], [p[1] for p in bal]
    x0, x1, y1, z, o = min(xs), max(xs), max(ys), ctx.floor_z('balcony') - .165, .0085   # tray frame bottom 2.85
    run = [(x0 - o, YR + .05), (x0 - o, y1 + o), (x1 + o, y1 + o), (x1 + o, YR + .05)]
    white = M.mat('plastic_white')
    mb, bulbs, d, k = mo.MB(), [], .06, 0
    for (ax, ay), (bx, by) in zip(run, run[1:]):                    # 15 x 15 clip strip on the frame: a target you can click
        mb.box((min(ax, bx) - .0075, min(ay, by) - .0075, z), (max(ax, bx) + .0075, max(ay, by) + .0075, z + .015), white, bev=.002)
    for (ax, ay), (bx, by) in zip(run, run[1:]):
        L = math.hypot(bx - ax, by - ay)
        while d < L:
            x, y = ax + (bx - ax) * d / L, ay + (by - ay) * d / L
            drop = (.30, .50, .38, .44, .34)[k % 5]
            mb.tube([(x, y, z), (x, y, z - drop)], .0018, white, 3)
            bulbs += [(x, y, z - s * .05) for s in range(1, int(drop / .05) + 1)]
            d, k = d + .115, k + 1
        d -= L
    body = mb.finish('garden.fairy_lights')
    lit = _octas('garden.fairy_lights.glow', bulbs, .0075, P.emissive('#FFD9A0', 12.0))
    G.click_glow(ctx, ROOM, body, lit, 'Fairy lights', reach=2.4)
    bulbs = _octas('garden.fairy_lights.bulbs', bulbs, .0055, white)
    IX.tag(bulbs, 'trigger', g=body.name, label='Fairy lights', reach=2.4)
    _add(ctx, bulbs, 'fit')


def _doorbell(ctx):
    black = M.mat('black_gloss')
    mb = mo.MB()
    mb.box((-.03, -.024, -.065), (.03, 0, .065), black, bev=.006)
    mb.at(T(0, -.024, .03) @ Matrix.Rotation(pi / 2, 4, 'X'))
    mb.lathe([(.013, 0), (.013, .002), (0, .002)], col('flood_lens', '#8A8E92', .2), 12)       # camera
    mb.at(T(0, -.024, -.03) @ Matrix.Rotation(pi / 2, 4, 'X'))
    mb.lathe([(.016, 0), (.016, .003), (.012, .003), (.012, .001), (0, .001)], M.mat('silver_satin'), 12)   # button ring
    _add(ctx, P.place(mb.at().finish('garden.doorbell'), (2.07, YR, 1.25), facing=(0, 1)), 'fit')


# ---------------------------------------------------------------- bird table, feeding station, backdrop
def _birds(ctx):
    """Small pitched-roof bird table on a bracket at the top of an east fence post (y 22.5), and the black
    shepherd's-crook feeding station at the deck's NE corner (garden.md 5)."""
    wood, black = col('birdtable', '#6E5A44', .85), M.mat('black_matt')
    y = 22.5
    x = fence_x(y) - .07
    mb = mo.MB()
    mb.box((x - .025, y - .025, 1.25), (x + .025, y + .025, 1.80), wood, bev=.003)             # post strapped to the fence post
    mb.prism([(x - .02, y - .006, 1.45), (x - .2, y - .006, 1.78), (x - .17, y - .006, 1.78), (x - .02, y - .006, 1.50)], (0, .012, 0), black)
    xc = x - .09
    mb.box((xc - .15, y - .12, 1.80), (xc + .15, y + .12, 1.815), wood, bev=.002)
    for sx in (-.13, .13):
        for sy in (-.10, .10):
            mb.box((xc + sx - .008, y + sy - .008, 1.815), (xc + sx + .008, y + sy + .008, 1.93), wood)
    for s in (-1, 1):                                                                           # two roof slabs, ridge along X
        mb.at(T(xc, y, 2.01) @ Matrix.Rotation(math.radians(38 * s), 4, 'X'))
        mb.box((-.17, 0 if s < 0 else -.17, -.008), (.17, .17 if s < 0 else 0, .004), wood, bev=.002)
    _add(ctx, mb.at().finish('garden.bird_table'))

    # feeding station (v2:f_0205, f_0311): pole ~2.0 above the grass, four shepherd's-crook arms curling out at the top,
    # a white dish and a mesh tray on brackets part-way up
    px, py, top = 3.22, 20.95, LAWN + 2.02
    mb = mo.MB()
    mb.tube([(px, py, LAWN - .1), (px, py, top)], .008, black, 6)
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
    (ax, ay, az), (bx, by, bz), (cx_, cy_, cz), _ = hang
    mb.at(T(ax, ay, az - .40))                                                                  # mesh peanut feeder, green caps
    mb.lathe([(0, 0), (.05, 0), (.05, .03), (.044, .03), (.044, .28), (.05, .28), (.05, .31), (.02, .335), (0, .34)], wire, 12)
    for zc in (0, .28):
        mb.lathe([(0, zc - .002), (.052, zc - .002), (.052, zc + .032), (.02, zc + .05 if zc else zc + .04), (0, zc + .05)], green, 12)
    mb.at(T(bx, by, bz - .36))                                                                  # seed tube
    mb.lathe([(0, 0), (.034, 0), (.034, .30), (0, .30)], seed, 10)
    mb.lathe([(0, -.005), (.04, -.005), (.04, .02), (0, .02)], green, 10)
    mb.lathe([(0, .29), (.04, .29), (.04, .31), (0, .33)], green, 10)
    mb.at(T(cx_, cy_, cz - .22))                                                                # small fat-ball cage
    mb.box((-.05, -.05, 0), (.05, .05, .13), wire)
    mb.at()
    for p, d in ((hang[0], .06), (hang[1], .03), (hang[2], .09)):
        mb.tube([p, (p[0], p[1], p[2] - d)], .0015, black, 3)
    for a, kind in ((-.4, 'dish'), (1.2, 'tray')):                                              # brackets at ~1.3 above the grass
        c, s = cos(a), sin(a)
        zb = LAWN + 1.28
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


def _backdrop(ctx):
    """Backdrop only (garden.md 7): the big sycamore overhanging from beyond the shed's NE corner and the conifer
    hedge behind its west half. Leaf cards on low-poly cores, nothing to walk to."""
    rng = random.Random(41)
    bark = col('tree_bark', '#5A5048', .9)
    shed = lambda p: not (-.95 < p.x < 4.55 and 23.3 < p.y < 29.0 and p.z < 2.5)               # nothing inside the shed
    mb, ls, ld = mo.MB(), [], []
    # the sycamore: trunk in the neighbour's garden just east of the shed (behind the wing wall), crown spreading over
    # the shed roof and the path, lowest leaves ~3 m (v2:f_0189, f_0203, f_0205); airy clusters on dark cores
    core_d = col('crown_core_dark', '#2E4029', 1.0)
    fork = V((5.3, 26.9, 3.6))
    mb.tube(G.chaikin([(5.45, 27.1, -.5), (5.4, 27.0, 1.8), fork], 1), .22, bark, 8)

    def crown(c, r, n, out, base, limbs=5, per=380, core=None):
        """Limbs from `base`, n leafy clusters on twigs from the nearest limb (an evergreen gets a dense core)."""
        ends = []
        for i in range(limbs):
            a = 2 * pi * (i + rng.uniform(-.2, .2)) / limbs
            e = V((c[0] + .6 * r[0] * cos(a), c[1] + .6 * r[1] * sin(a), c[2] + rng.uniform(-.2, .4) * r[2]))
            mb.tube(G.chaikin([base, base.lerp(e, .45) + V((0, 0, .5)), e], 1), .09, bark, 6)
            ends.append(e)
        for _ in range(n):
            u = V((rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, .8))).normalized() * rng.uniform(.3, 1)
            p = V((c[0] + u.x * r[0], c[1] + u.y * r[1], c[2] + u.z * r[2]))
            k = rng.uniform(.65, 1.15)
            mb.tube([min(ends, key=lambda q: (q - p).length), p], .03, bark, 4)
            if core:
                mb.at(T(p.x, p.y, p.z - .45 * k, rng.uniform(0, 90)))
                mb.dome(.62 * k, .55 * k, .95 * k, core, 10, 3)
                mb.at()
            out += G.blob(rng, (p.x, p.y, p.z), (.9 * k, .8 * k, .7 * k), int(per * k), .2, .17, 4, droop=.35,
                          shell=.7 if core else .15, lo=-.7, keep=shed)
    crown((4.4, 26.4, 5.8), (3.3, 2.6, 2.0), 24, ls, fork)
    # low limbs hanging over the shed's NE corner and the path, down to the roof line (v2:f_0189)
    crown((4.6, 24.4, 3.4), (.9, 1.1, .45), 7, ls, fork, limbs=2, per=320)
    mb.tube([fork, fork + V((-.1, .1, 2.2))], .14, bark, 7)                                       # leader
    crown((5.2, 27.6, 8.4), (2.0, 1.8, 1.0), 7, ls, fork + V((-.1, .1, 2.2)), limbs=3)
    # a dark evergreen mass behind the east fence opposite the lawn, foliage from the fence top (v2:f_0161, f_0205)
    base2 = V((6.9, 21.8, 1.4))
    crown((6.9, 21.6, 3.5), (1.8, 2.6, 1.9), 18, ld, base2, limbs=4, per=300, core=core_d)   # clear of the neighbour (y < 17.0)
    hedge_core = col('hedge_core', '#2C3F2C', 1.0)
    cores = ((-.2, 30.1, 1.5, 3.9), (.9, 30.0, 1.4, 4.3), (1.9, 30.2, 1.2, 3.7))
    for x, y, r, h in cores:
        mb.at(T(x, y, -.5))
        mb.dome(r, .75, h, hedge_core, 8, 3)
    _add(ctx, mb.at().finish('garden.backdrop'))
    tree = leafmats('sycamore', ('#8E9C48', '#A6A852', '#7A8C42', '#B4AC5A'), .7)
    _add(ctx, G.cards('garden.backdrop.tree', ls, tree))
    _add(ctx, G.cards('garden.backdrop.evergreen', ld, leafmats('evergreen', ('#3E5838', '#4A6440', '#36502F'), .8)))
    hedge = leafmats('conifer', ('#3F5A3A', '#4A6642', '#35502F'), .9)
    lh = []
    for x, y, r, h in cores:
        lh += G.blob(rng, (x, y, -.5), (r + .1, .85, h + .1), 260, .3, .2, 3, droop=-.4, shell=.9, lo=.05, keep=lambda p: p.y > 28.95)
    _add(ctx, G.cards('garden.backdrop.hedge', lh, hedge))


def build(ctx):
    _fire_pit(ctx)
    _trellis(ctx)
    _planters(ctx)
    _pots(ctx)
    _chairs(ctx)
    _lavender(ctx)
    climbers(ctx, ROOM, 'garden.climbers', (18.35, 19.25, 20.4, 21.5, 22.2), 9)
    _floodlight(ctx)
    _fairy_lights(ctx)
    _doorbell(ctx)
    _birds(ctx)
    _backdrop(ctx)

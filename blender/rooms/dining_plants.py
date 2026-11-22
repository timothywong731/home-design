"""Dining room plants: the two Swiss-cheese plants on the east window sills and the citrus tree in the
north-east corner. Imported by rooms/dining.py.

Origin = centre of the pot's footprint. Monstera: local -Y points into the room, +Y at the window glass."""
import math
import random
from math import sin, cos, pi

import bmesh
from mathutils import Matrix, Vector

from lib import materials as M, mouldings as mo, props as P
from rooms.dining_furniture import T, fin, spline, loft, bar, oval


def _pot(mb, prof, tones, segs=24, seed=1):
    """Hand-glazed pot: lathe of [(r, z)...] whose facets take one of a few close glaze tones (mottled)."""
    rng = random.Random(seed)
    mats = [M.solid(f'dining_glaze_{h[1:]}', h, .12) for h in tones]
    ring = lambda r, z: [(r * cos(2 * pi * i / segs), r * sin(2 * pi * i / segs), z) for i in range(segs)]
    for (r0, z0), (r1, z1) in zip(prof, prof[1:]):
        a, b = ring(r0, z0), ring(r1, z1)
        m = rng.choice(mats)
        for i in range(segs):
            if rng.random() < .45:
                m = rng.choice(mats)                                                # blotches run round the pot
            j = (i + 1) % segs
            mb.face([a[i], a[j], b[j], b[i]], m, (a[i][0] + a[j][0], a[i][1] + a[j][1], (r0 - r1) * 4))


def _monstera_leaf(mb, F, L, mat, slits=0):
    """Heart-shaped leaf: attachment (sinus) at the origin of frame F, midrib along +Y to a drooping tip. The
    outline is a spline (33 - 45 points per half), the blade three spans from the creased midrib to an edge that
    curls down; the largest leaves carry `slits` cuts in each half."""
    W = .86 * L
    cut1 = [(.5, .26), (.24, .29), (.24, .31), (.49, .33)] if slits else [(.5, .3)]
    cut2 = [(.44, .49), (.2, .52), (.2, .54), (.42, .56)] if slits > 1 else [(.44, .5)]
    half = spline([(0, 0), (.08, -.11), (.2, -.19), (.33, -.19), (.44, -.1), (.495, .08)] + cut1 + cut2 +
                  [(.35, .68), (.23, .82), (.1, .94), (0, 1)], 3)
    Fw = mb.M.copy()
    mb.at(Fw @ F)
    for sx in (-1, 1):
        rows = []
        for x, y in half:
            ym = min(max(y, 0.0), 1.0)                                              # foot of this rib on the midrib
            rib = []
            for k in (0, .14, .6, 1):
                px, py = k * x * W, (ym + k * (y - ym)) * L
                z = -.26 * L * (py / L) ** 2 if py > 0 else 0.0                    # the blade droops toward the tip,
                z += .30 * px - .55 * W * (k * abs(x)) ** 2.4                       # folds up from the midrib, curls down at the edge
                z += .03 * L * sin(9 * py / L) * k * abs(x)                         # and undulates between the veins
                rib.append((sx * px, py, z))
            rows.append(rib if sx > 0 else rib[::-1])                               # both halves face +Z
        loft(mb, rows, mat, closed=False)
    mb.at(Fw)


def monstera(name, seed=0, lean=0.0, keep=None):
    """Swiss-cheese plant for a window sill, about 0.50 wide x 0.58 high (v1 f_0675, v2 f_0061): twelve deep-green
    heart-shaped leaves 0.11 - 0.15 across (the larger ones split) on long slender stalks rising out of the pot, the
    upper ones held up inside the window reveal, the lower ones arching out toward the room; mottled jade pot
    0.15 x 0.15 on a cork mat. `lean` shifts the head sideways (+X).
    keep(x, y, z) (local coords): a leaf whose blade or stalk fails it is tried again smaller and pulled in toward
    the stem, then left out, so the plant stays inside its window reveal and clear of its neighbours."""
    keep = keep or (lambda x, y, z: True)
    rng = random.Random(11 + seed)
    mb = mo.MB()
    mb.lathe([(0, 0), (.062, 0), (.062, .006), (0, .006)], 'cork', 20)
    _pot(mb, [(.05, .006), (.057, .02), (.066, .075), (.072, .125), (.077, .14), (.078, .15), (.072, .156), (.066, .15), (.063, .138)],
         ('#4E6B58', '#476352', '#54715D', '#4A6A5C'), seed=3 + seed)
    mb.lathe([(.064, .14), (0, .14)], P.mat('soil'), 16)
    # olive deep greens matched to f_0636 under the downlight above the sill (#3F6B2E rendered mint next to the window);
    # glossy: at roughness .45 the broad sheen of that downlight washed the dark blades out to sage
    leafs = [P.two_sided(M.solid(f'dining_leaf_{k}', h, .3)) for k, h in (('a', '#3A5A1E'), ('b', '#456A28'))]
    stem = M.solid('dining_leaf_stem', '#557A36', .45)
    # (base x, y, z, length, slits): top tier held up inside the reveal (y > -0.07), lower tiers arching out over the
    # sill nosing; overall spread about 0.50 along the wall, as the plants keep within their window surrounds
    plan = [(-.08, -.01, .55, .15, 1), (.07, .02, .57, .14, 0), (.15, -.03, .49, .15, 1), (-.17, .00, .47, .14, 0),
            (-.03, -.10, .45, .17, 2), (.11, -.12, .40, .15, 1), (-.19, -.10, .37, .15, 0), (.20, -.05, .36, .13, 0),
            (.01, .03, .38, .13, 0), (-.11, -.19, .30, .15, 1), (.12, -.20, .28, .14, 0), (.00, -.16, .32, .16, 2)]
    bm = mb.bm
    for i, (bx0, by0, bz0, L0, slits) in enumerate(plan):
        jx, jz, jd, dz = (rng.uniform(-.012, .012), rng.uniform(-.012, .012), rng.uniform(-.2, .2), rng.uniform(-.6, -.05))
        for s in (1.0, .82, .66, .5):                                               # shrink + pull in until it fits
            bx, by = (bx0 + jx) * s + lean * (bz0 - .15), by0 * s
            bz, L = bz0 + jz, L0 * (.8 + .2 * s)
            B = Vector((bx, by, bz))
            d = Vector(((bx - lean * .25) * 2.0 * s + jd * s, -.5 + 1.0 * by, dz)).normalized()   # midrib: outward, drooping
            n = Vector((bx * .8, -.6, .8))                                                  # blade faces up and toward the room
            n = (n - n.dot(d) * d).normalized()
            F = Matrix.Identity(4)
            for c, v in enumerate((d.cross(n), d, n)):
                for r in range(3):
                    F[r][c] = v[r]
            F.translation = B
            n0 = len(bm.verts)
            _monstera_leaf(mb, F, L, leafs[i % 2], slits)
            h = Vector((bx, by, 0))
            up = h.cross(Vector((0, 0, 1)))
            root = Vector((bx * .1, by * .1, .135))
            rise = B.z - root.z                                                     # stalk: up out of the pot, then arching over
            path = spline([tuple(root), tuple(root.lerp(B, .3) + Vector((0, 0, .42 * rise))),
                           tuple(root.lerp(B, .72) + Vector((0, 0, .26 * rise))), tuple(B)], 5)
            bar(mb, path, oval(.0055, .0055, 5), stem, up=tuple(up) if up.length > 1e-4 else (1, 0, 0), caps=False)
            bm.verts.ensure_lookup_table()
            new = bm.verts[n0:]
            if all(keep(*v.co) for v in new):
                break
            bmesh.ops.delete(bm, geom=list(new), context='VERTS')
    return fin(mb, name)


def citrus(name='dining.citrus', crown=.68, top=1.75, keep=None, elong=1.05, n_leaves=800, leaf=1.0):
    """Citrus tree: olive glazed pot 0.33 x 0.30 with three embossed bands on a low dark stand, stout pale stem
    bare for 0.75, irregular head (dia `crown`, `elong` times as tall) of `n_leaves` glossy ovate leaves on twigs,
    `leaf` = leaf size factor (1: 78 x 42 mm).
    keep(x, y, z) (local coords): leaves and twigs failing it are left out, so the head can push into a window
    recess without crossing its architraves or the curtain beside it."""
    keep = keep or (lambda x, y, z: True)
    rng = random.Random(7)
    mb = mo.MB()
    mb.lathe([(0, 0), (.15, 0), (.16, .01), (.16, .07), (.15, .08), (0, .08)], 'dark_oak_antique', 24)        # stand
    _pot(mb, [(.115, .08), (.125, .10), (.14, .16), (.146, .165), (.146, .18), (.15, .22), (.156, .225), (.156, .24), (.158, .29),
              (.164, .295), (.164, .31), (.16, .34), (.166, .36), (.168, .375), (.16, .382), (.15, .375), (.146, .355)],
         ('#5A6238', '#545C34', '#5E663A'), seed=5)
    mb.lathe([(.148, .36), (0, .36)], P.mat('soil'), 20)
    bark = M.solid('dining_citrus_bark', '#9A8B6C', .7)                             # pale grey-tan stem (f_0589)
    rc = crown / 2
    zc = top - rc * elong
    trunk = spline([(0, 0, .36), (.012, .004, .62), (-.008, -.006, .88), (.004, .003, zc - rc * .5)], 4)
    bar(mb, trunk, oval(.03, .03, 8), bark, up=(1, 0, 0), scale=[1.1 - .35 * i / (len(trunk) - 1) for i in range(len(trunk))])
    fork = Vector(trunk[-1])
    leaves = [P.two_sided(M.solid(f'dining_citrus_{k}', h, .35)) for k, h in (('a', '#44582F'), ('b', '#4F6638'), ('c', '#6A6434'))]

    def shell(f):                                                                   # point of the (lumpy) head
        th, cz = rng.uniform(0, 2 * pi), rng.uniform(-.85, 1)
        s = math.sqrt(1 - cz * cz)
        r = rc * f * (1 + .1 * sin(3 * th + 1) * s + .08 * cos(2 * th) * cz)
        return Vector((r * s * cos(th), r * s * sin(th), zc + r * cz * elong))
    tips = [shell(.75) for _ in range(20)]
    for t in tips:                                                                  # twigs
        if not keep(*t):
            continue
        mid = fork.lerp(t, .5) + Vector((0, 0, .03))
        bar(mb, [tuple(fork), tuple(mid), tuple(t)], oval(.007, .007, 4), bark, up=(.3, .9, 0), caps=False)
    L, W = .078 * leaf, .042 * leaf                                                 # ovate leaf, folded along the midrib
    quad = [((0, 0, 0), (-W / 2, .26 * L, .007), (-W / 2, .62 * L, .007), (0, L, 0)),
            ((0, 0, 0), (0, L, 0), (W / 2, .62 * L, .007), (W / 2, .26 * L, .007))]
    for i in range(n_leaves):
        base = shell(rng.uniform(.45, .97) ** .6) if i % 5 else tips[i // 5 % 20].lerp(fork, rng.uniform(0, .5))
        out = (base - Vector((0, 0, zc - .1))).normalized()
        d = (out + Vector((rng.uniform(-.7, .7), rng.uniform(-.7, .7), rng.uniform(-.5, .5)))).normalized()   # leaf axis
        k = rng.uniform(.75, 1.15)
        if not (keep(*base) and keep(*(base + d * L * k))):                         # same draws either way: the rest stay put
            m = rng.random()
            continue
        n = out + Vector((0, 0, .6))
        n = n - n.dot(d) * d
        n = n.normalized() if n.length > 1e-3 else d.orthogonal().normalized()
        F = Matrix.Identity(4)
        for c, v in enumerate((d.cross(n), d, n)):
            for r in range(3):
                F[r][c] = v[r]
        F.translation = base
        mb.at(F @ Matrix.Scale(k, 4))
        m = leaves[2] if rng.random() < .04 else leaves[i % 2]
        for q in quad:
            mb.face(q, m, (0, 0, 1))
    mb.at()
    return fin(mb, name)

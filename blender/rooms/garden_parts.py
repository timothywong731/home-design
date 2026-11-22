"""Shared parts of rooms/garden.py and rooms/side_passage.py: low-poly foliage (alpha-free leaf cards), slatted
timber planters, pots, bib taps that run, fittings that glow on a click, the outdoor a/c unit.

World coordinates (metres, Z up) unless a docstring says local. Everything here is probe-lit (lm='dynamic'):
thousands of leaf cards, slats and bricks would waste the half-density exterior lightmap on padding."""
import math
import random
from math import sin, cos, pi

import bpy
from mathutils import Matrix, Vector as V

from lib import interact as IX, materials as M, mouldings as mo, props as P

TIMBER = 'oak_table'                # dark walnut stain #5E4631 (garden.md: planters #5A4638)


def col(name, hx, rough=.7, metal=0.0):
    return M.solid('garden_' + name, hx, rough, metal)


def _mute(hx, k=.3):
    """Pull a colour toward its own grey: the AgX high-contrast view under the blue sky light oversaturates foliage."""
    r, g, b = (int(hx[i:i + 2], 16) for i in (1, 3, 5))
    y = .3 * r + .59 * g + .11 * b
    return '#%02X%02X%02X' % tuple(round(c + (y - c) * k) for c in (r, g, b))


def leafmats(prefix, hexes, rough=.55):
    """Two-sided plain materials for cards(); colours are the spec's leaf colours, muted (see _mute)."""
    return [P.two_sided(col(f'{prefix}_{i}', _mute(h), rough)) for i, h in enumerate(hexes)]


def T(x=0.0, y=0.0, z=0.0, rz=0.0):
    return Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(rz), 4, 'Z')


def chaikin(pts, it=2):
    """Corner-cutting smoothing of a polyline (end points kept)."""
    pts = [V(p) for p in pts]
    for _ in range(it):
        q = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            q += [a.lerp(b, .25), a.lerp(b, .75)]
        pts = q + [pts[-1]]
    return pts


# ---------------------------------------------------------------- foliage
def cards(name, leaves, mats, fold=.3):
    """leaves [(base, tip, half width, up hint, material index)] -> one object of diamond quads creased along the
    midrib: 2 triangles a leaf, no alpha. `mats` must be two-sided (leafmats)."""
    vs, fs, mi = [], [], []
    for b, t, hw, n, k in leaves:
        d = t - b
        s = d.cross(n)
        if s.length < 1e-7:
            s = d.cross(V((1, 0, .3)))
        s.normalize()
        m = b.lerp(t, .45) + s.cross(d).normalized() * (hw * fold)
        o = len(vs)
        vs += [b, m + s * hw, t, m - s * hw]
        fs.append((o, o + 1, o + 2, o + 3))
        mi.append(k)
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in vs], [], fs)
    for m in mats:
        me.materials.append(m)
    me.polygons.foreach_set('material_index', mi)
    me.uv_layers.new(name='UVMap')
    me.update()
    return bpy.data.objects.new(name, me)


def blob(rng, c, r, n, L, W, nm, droop=.3, shell=.5, lo=-1.0, keep=None, up=0.0):
    """n leaves in the outer shell of an ellipsoid (centre c, radii r), pointing outward and drooping.
    lo = lowest unit z kept (0 = a dome); keep(point) rejects leaves (walls, glass); up > 0 = upright spikes."""
    out, tries = [], 0
    while len(out) < n and tries < n * 30:
        tries += 1
        u = V((rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1))).normalized()
        if u.z < lo:
            continue
        f = rng.uniform(shell, 1)
        p = V((c[0] + u.x * r[0] * f, c[1] + u.y * r[1] * f, c[2] + u.z * r[2] * f))
        d = (u + V((rng.uniform(-.7, .7), rng.uniform(-.7, .7), rng.uniform(-.7, .7) - droop + up))).normalized()
        t = p + d * L * rng.uniform(.7, 1.3)
        if keep and not (keep(p) and keep(t)):
            continue
        out.append((p, t, W * rng.uniform(.75, 1.2) / 2, u + V((0, 0, .7)), rng.randrange(nm)))
    return out


def strand(rng, path, n, L, W, nm, normal, off=.012):
    """n leaves along a polyline lying on a wall / fence whose outward normal is `normal`: alternate sides,
    tipped a little outward and down."""
    pts, nv, out = [V(p) for p in path], V(normal).normalized(), []
    for i in range(n):
        k = (i + rng.random()) / n * (len(pts) - 1)
        a, b = pts[int(k)], pts[min(int(k) + 1, len(pts) - 1)]
        p = a.lerp(b, k % 1) + nv * off
        side = (b - a).cross(nv)
        side = side.normalized() if side.length > 1e-7 else V((0, 0, 1))
        d = (side * (1 if i % 2 else -1) + nv * rng.uniform(.1, .6) + V((0, 0, rng.uniform(-.7, .1)))).normalized()
        out.append((p, p + d * L * rng.uniform(.7, 1.3), W * rng.uniform(.75, 1.2) / 2, nv, rng.randrange(nm)))
    return out


# ---------------------------------------------------------------- containers
def planter(mb, x0, x1, y0, y1, z0, h, feet=0.0, fill=None, drop=.04, slat=.085, post=.045, t=.018, liner=True,
            wood=TIMBER, vertical=False):
    """Slatted timber planter (garden.md 6), filled to `drop` below the rim with `fill` (default soil), black liner
    (liner='fold': its edge turned over the rim). Horizontal style: corner posts down to the deck, slats with shadow
    gaps between them, `feet` = slat-free height at the bottom. vertical=True (the east trough, v11 t194): sides of
    vertical boards 0.095 with 3 mm gaps, square block feet `feet` high set 40 mm in from the corners.
    `wood` = material key or Material (e.g. site_tex 'oak_table@#5A4A40'). -> z of the fill surface."""
    zb, zt = z0 + feet, z0 + h
    if vertical:
        for x, y in ((x0 + .04, y0 + .04), (x1 - .11, y0 + .04), (x0 + .04, y1 - .11), (x1 - .11, y1 - .11)):
            if feet:
                mb.box((x, y, z0), (x + .07, y + .07, zb + .002), wood, bev=.004, grain=2)
        for ya, yb in ((y0, y0 + t), (y1 - t, y1)):                        # long sides run the full length
            n = max(1, round((x1 - x0) / .098))
            s = (x1 - x0) / n
            for i in range(n):
                mb.box((x0 + i * s + .0015, ya, zb), (x0 + (i + 1) * s - .0015, yb, zt - .001), wood, bev=.002, grain=2)
        for xa, xb in ((x0, x0 + t), (x1 - t, x1)):                        # ends between them
            n = max(1, round((y1 - y0 - 2 * t) / .098))
            s = (y1 - y0 - 2 * t) / n
            for i in range(n):
                mb.box((xa, y0 + t + i * s + .0015, zb), (xb, y0 + t + (i + 1) * s - .0015, zt - .001), wood, bev=.002, grain=2)
        i0 = t
    else:
        for x, y in ((x0, y0), (x1 - post, y0), (x0, y1 - post), (x1 - post, y1 - post)):
            mb.box((x, y, z0), (x + post, y + post, zt - .001), wood, bev=.003, grain=2)
        n = max(1, round((zt - zb) / slat))
        s = (zt - zb) / n
        for i in range(n):
            a, b = zb + i * s + .002, zb + (i + 1) * s - .002
            mb.box((x0 + post - .005, y0 + .004, a), (x1 - post + .005, y0 + .004 + t, b), wood, bev=.002, grain=0)
            mb.box((x0 + post - .005, y1 - .004 - t, a), (x1 - post + .005, y1 - .004, b), wood, bev=.002, grain=0)
            mb.box((x0 + .004, y0 + post - .005, a), (x0 + .004 + t, y1 - post + .005, b), wood, bev=.002, grain=1)
            mb.box((x1 - .004 - t, y0 + post - .005, a), (x1 - .004, y1 - post + .005, b), wood, bev=.002, grain=1)
        i0 = .005 + t
    r = .05
    mb.box((x0 - .006, y0 - .006, zt - .001), (x1 + .006, y0 + r, zt + .018), wood, bev=.003, grain=0)
    mb.box((x0 - .006, y1 - r, zt - .001), (x1 + .006, y1 + .006, zt + .018), wood, bev=.003, grain=0)
    mb.box((x0 - .006, y0 + r, zt - .001), (x0 + r, y1 - r, zt + .018), wood, bev=.003, grain=1)
    mb.box((x1 - r, y0 + r, zt - .001), (x1 + .006, y1 - r, zt + .018), wood, bev=.003, grain=1)
    zf = zt - drop
    black = M.mat('black_matt')
    mb.box((x0 + i0, y0 + i0, zb + .01), (x1 - i0, y1 - i0, zf), fill or P.mat('soil'))
    if liner:
        for a, b, hint in (((x0 + i0, y0 + i0), (x1 - i0, y0 + i0), (0, 1, 0)), ((x0 + i0, y1 - i0), (x1 - i0, y1 - i0), (0, -1, 0)),
                           ((x0 + i0, y0 + i0), (x0 + i0, y1 - i0), (1, 0, 0)), ((x1 - i0, y0 + i0), (x1 - i0, y1 - i0), (-1, 0, 0))):
            mb.face([(*a, zf), (*b, zf), (*b, zt + .017), (*a, zt + .017)], black, hint)
    if liner == 'fold':                                                    # the liner's edge lapped over the rim
        f, k = .028, zt + .0195
        for a, b in (((x0 + i0 - .002, y0 + i0 - f), (x1 - i0 + .002, y0 + i0)), ((x0 + i0 - .002, y1 - i0), (x1 - i0 + .002, y1 - i0 + f)),
                     ((x0 + i0 - f, y0 + i0), (x0 + i0, y1 - i0)), ((x1 - i0, y0 + i0), (x1 - i0 + f, y1 - i0))):
            mb.box((*a, zt + .0175), (*b, k), black)
    return zf


def pot(mb, x, y, z, r, h, mat, feet=0.0, belly=0.0, soil=None, segs=16):
    """Flower pot standing at (x, y, z): rim radius r, height h; belly > 0 = rounded jar; feet = height of three
    pot feet. -> z of the soil."""
    mb.at(T(x, y, z + feet))
    if belly:
        prof = [(0, 0), (r * .62, 0), (r * (.92 + .2 * belly), h * .3), (r * (.98 + .2 * belly), h * .58), (r * .9, h * .9),
                (r, h * .96), (r, h), (r - .012, h), (r - .02, h * .9)]
    else:
        prof = [(0, 0), (r * .66, 0), (r * .96, h * .84), (r, h * .86), (r, h), (r - .014, h), (r - .02, h * .88)]
    mb.lathe(prof, mat, segs)
    mb.lathe([(r - .018, h - .03), (0, h - .03)], soil or P.mat('soil'), segs)
    if feet:
        for k in range(3):
            a = 2 * pi * k / 3 + .4
            mb.box((r * .5 * cos(a) - .02, r * .5 * sin(a) - .02, -feet), (r * .5 * cos(a) + .02, r * .5 * sin(a) + .02, 0), mat)
    mb.at()
    return z + feet + h - .03


# ---------------------------------------------------------------- operable fittings
def bib_tap(ctx, room, name, x, y, z, normal, label, fall, splash=.07, outlet=None):
    """Brass bib tap on a wall at (x, y, z) = centre of its wall plate; `normal` = wall normal (unit xy).
    The cross head turns a quarter and one stream falls `fall` m from the nose (or from the world point
    `outlet`, e.g. under a distributor). -> world outlet point."""
    brass = M.mat('brass_antique')
    mb = mo.MB()
    mb.box((-.025, -.006, -.025), (.025, 0, .025), brass, bev=.002)                    # wall plate
    mb.tube([(0, -.004, 0), (0, -.075, 0)], .011, brass, 8)                             # body out of the wall
    mb.tube([(0, -.045, 0), (0, -.045, .036)], .009, brass, 8)                          # valve bonnet
    mb.tube([(0, -.066, .004), (0, -.078, -.02), (0, -.078, -.05)], .0095, brass, 8)    # spout turning down
    mb.tube([(0, -.078, -.05), (0, -.078, -.066)], .0125, brass, 8)                     # hose-union nose
    body = P.place(mb.finish(name), (x, y, z), facing=normal)
    mb = mo.MB()
    mb.box((-.028, -.0055, .036), (.028, .0055, .045), brass, bev=.002)
    mb.box((-.0055, -.028, .036), (.0055, .028, .045), brass, bev=.002)
    head = mb.finish(name + '.head')
    Mb = body.matrix_basis
    axis = Mb @ V((0, -.045, 0))
    head.matrix_basis = Mb @ Matrix.Translation((0, -.045, 0))
    out = V(outlet) if outlet else Mb @ V((0, -.078, -.066))
    water = P.place(P.water_stream(fall, dia=.011, splash=splash, name=name + '.water'), tuple(out))
    IX.tag(body, 'trigger', g=name, label=label)
    IX.tag(head, 'hinge', g=name, label=label, p=tuple(axis), a=(0, 0, 1), deg=90, dur=.4)
    IX.tag(water, 'show', g=name, label=label, when=1, fx='water')
    for o in (body, head, water):
        ctx.add(o, room, 'fit', lm='dynamic')
    return out


def click_glow(ctx, room, body, glow, label, **kw):
    """A fitting that is off as modelled and lights when clicked: `body` is the trigger, `glow` (emissive
    geometry 1 mm proud of the lens) appears in state 1. kw: e.g. reach for fittings overhead."""
    IX.tag(body, 'trigger', g=body.name, label=label, **kw)
    IX.tag(glow, 'show', g=body.name, label=label, when=1, fx='glow', **kw)
    ctx.add(body, room, 'fit', lm='dynamic')
    ctx.add(glow, room, 'fit', lm='dynamic')


# ---------------------------------------------------------------- plant
def condenser(name):
    """Outdoor a/c unit 0.80 x 0.30 x 0.65 on two galvanised wall brackets. Local frame: wall plane y = 0, the fan
    grille faces -Y, origin = centre of the unit's underside on the wall plane (use P.place(..., facing=))."""
    case, dark, galv = col('condenser', '#D8D8D4', .45), col('condenser_grille', '#3A3C40', .5), M.mat('silver_satin')
    mb = mo.MB()
    mb.box((-.40, -.42, 0), (.40, -.12, .65), case, bev=.008)
    mb.at(Matrix.Translation((-.12, -.421, .325)) @ Matrix.Rotation(pi / 2, 4, 'X'))
    mb.lathe([(.25, 0), (.25, .006), (0, .006)], dark, 20)                                     # fan grille
    mb.lathe([(.25, 0), (.27, 0), (.27, .014), (.25, .014), (.25, .006)], case, 20)             # its ring
    mb.lathe([(.07, .006), (.07, .014), (0, .014)], case, 12)                                  # hub
    mb.at()
    mb.box((.25, -.424, .08), (.37, -.42, .57), col('condenser_side', '#C4C4C0', .5))        # service panel
    for x in (-.3, .3):
        mb.box((x - .02, -.44, -.03), (x + .02, 0, 0), galv)                                   # bracket arm
        mb.box((x - .02, -.03, -.33), (x + .02, 0, -.03), galv)                                # bracket upright
        mb.prism([(x - .012, -.03, -.3), (x - .012, -.38, -.03), (x - .012, -.34, -.03), (x - .012, -.03, -.26)], (.024, 0, 0), galv)
    return mb.finish(name)

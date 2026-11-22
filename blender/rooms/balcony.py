"""balcony - bolt-on steel balcony off the rear blue bedroom (level 1, kind exterior). Spec: spec/rooms/balcony.md
and round 3 (RECONCILE3 garden-22): platform x 0.195..2.315, y 17.36..18.48 (2.12 x 1.12, centred on the door axis
1.255), deck Z 3.00, round 48 mm grey rail tubes (top 1.10 above the deck), lantern (2.33, 17.36, 5.10).

The envelope built the deck, frame, railing, wall posts, struts and rain pipe (balcony.floor / .structure /
.rainpipe). Here: the coach lantern with its lamp (`lamp` tag; the switch is rooms/blue_bedroom.py 'Balcony light'),
four rail planters (three on the front rail, one on the east rail; the west rail is bare) with ivy curtains and a
low fringe over the top rail, petunias at the north-east corner. Ivy, planters and flowers are kept clear of the railing
tubes, bars, deck edge and struts by `_clear` (v13 t215 from above: ivy over and outside the front rail, round the
north-west corner and down the outside of the east rail). No furniture (the folding chair is decluttered, spec 6).
The "small grey square unit on a bracket east of the doors" of the v13 survey is this lantern seen from above (its
cap reflects the sky): same place, same height, same S-bracket; no second fitting is modelled.
"""
import random
from math import cos, sin, pi

import bpy
from mathutils import Vector

from lib import interact as IX, lighting, materials as M, mouldings as mo, props as P

ROOM = 'balcony'
X0, X1, Y0, Y1, DZ = 0.195, 2.315, 17.36, 18.48, 3.00   # platform, deck top (build() checks them against the spec)
PS = 0.048                                               # rail / post tube diameter
RAIL = DZ + 1.10                                         # top of the top rail
ZR = RAIL - PS / 2                                       # top-rail axis (envelope: posts clamped PS/2 inside)
XA, XB, YR = X0 + PS / 2, X1 - PS / 2, Y1 - PS / 2       # rail axes: west, east, front

CAMERAS = [   # [round 4] 'rear' first: the first camera is the room's hero still (export.heroes); 'deck' was a dark close-up
    dict(name='rear', pos=(1.20, 23.00, 1.20), look=(1.20, 17.36, 3.60), fov_deg=80, ref='v2 f_0251'),
    dict(name='deck', pos=(1.20, 17.60, 4.55), look=(1.20, 18.60, 3.60), fov_deg=100, ref='v3 f_0285'),
    dict(name='lantern', pos=(1.40, 17.90, 4.50), look=(2.40, 17.36, 4.90), fov_deg=90, ref='v3 f_0295'),
    dict(name='west', pos=(1.80, 17.80, 4.55), look=(-0.50, 17.90, 4.00), fov_deg=100, ref='v3 f_0299'),
    dict(name='below', pos=(1.20, 19.80, 1.50), look=(1.20, 17.40, 4.40), fov_deg=100, ref='v2 f_0173'),
    dict(name='above', pos=(1.20, 17.55, 7.00), look=(1.30, 18.30, 3.00), fov_deg=80, ref='v13 t215 (study window)'),
    dict(name='east', pos=(0.50, 17.55, 4.50), look=(2.60, 18.10, 3.80), fov_deg=100, ref='v3 f_0277'),
]

# trough planters hung outside the top rail: (centre (x, y), along unit, out unit). The rail-side face of a trough is
# 12 mm off the rail's outer face (y 18.48 / x 2.315), so the hooks clear the 48 mm tube and the 60 mm tee collars.
# Three on the front (0.60 long over the 2.07 rail, the middle one in front of the middle post), one on the EAST side
# rail only: the west side rail is bare (v3 f_0269, f_0287, f_0299; v13 t215 shows only ivy trailing round the corner)
T_L, T_W, T_H, T_TOP = 0.60, 0.18, 0.16, RAIL - 0.05
_OFF = 0.012 + T_W / 2
TROUGHS = [((0.53, Y1 + _OFF), (1, 0), (0, 1)), ((1.255, Y1 + _OFF), (1, 0), (0, 1)), ((1.98, Y1 + _OFF), (1, 0), (0, 1)),
           ((X1 + _OFF, 18.06), (0, 1), (1, 0))]


# ----------------------------------------------------------------------------- clearance
def _segd(p, a, b):
    """Vector from the nearest point of segment a-b to p."""
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
    return p - (a + ab * t)


_TUBES = [(Vector((XA, YR, ZR)), Vector((XB, YR, ZR))), (Vector((XA, Y0, ZR)), Vector((XA, YR, ZR))),
          (Vector((XB, Y0, ZR)), Vector((XB, YR, ZR)))] +          [(Vector((x, YR, DZ)), Vector((x, YR, ZR + .03))) for x in (XA, 1.255, XB)]   # top rails, posts
_TUBE_R = PS / 2 + .006                                  # tube radius + clearance (the 60 mm collars: 0.030)


def _clear(p, out=None, outside=False):
    """Push a point out of the railing: the top-rail and post tubes (radially), the bar / bottom-rail slabs of the three
    sides, and - for hanging ivy (outside=True) - the whole platform volume from the strut feet (Z 1.85) to the rail
    top, along `out` (the trough's outward unit). Returns the moved point."""
    p = Vector(p)
    for a, b in _TUBES:
        d = _segd(p, a, b)
        if d.length < _TUBE_R:
            n = d.normalized() if d.length > 1e-6 else Vector((0, 0, 1))
            p += n * (_TUBE_R - d.length)
    m = .012
    if DZ - .01 < p.z < ZR:                              # bar slabs (16 mm bars on the rail axes)
        if XA - m < p.x < XB + m and abs(p.y - YR) < m:
            p.y = YR + (m if p.y >= YR else -m)
        for x in (XA, XB):
            if Y0 < p.y < YR + m and abs(p.x - x) < m:
                p.x = x + (m if p.x >= x else -m)
    if outside and out is not None and 1.85 < p.z < RAIL + .01:
        g = .03                                          # gap kept to the deck edge, frame and struts
        if X0 - g < p.x < X1 + g and Y0 < p.y < Y1 + g:
            o = Vector((out[0], out[1], 0))
            ts = [((Y1 + g) - p.y) / o.y] if o.y > 1e-6 else []
            ts += [((X1 + g) - p.x) / o.x] if o.x > 1e-6 else [((X0 - g) - p.x) / o.x] if o.x < -1e-6 else []
            p += o * min(ts)
    return p


def _clear_pts(pts, out=None, outside=False):
    """Move a whole leaf / flower (points) rigidly until none of its points needs a push (3 passes)."""
    pts = [Vector(q) for q in pts]
    for _ in range(3):
        best = Vector((0, 0, 0))
        for q in pts:
            d = _clear(q, out, outside) - q
            if d.length > best.length:
                best = d
        if best.length < 1e-5:
            break
        pts = [q + best * 1.05 for q in pts]
    return pts


def build(ctx):
    global STEEL
    f = ctx.feature('balcony_structure')
    xs, ys = zip(*f['polygon'])
    got = (min(xs), max(xs), min(ys), max(ys), f['deckTopZ'], f['railing']['height'], f['railing']['post'])
    want = (X0, X1, Y0, Y1, DZ, RAIL - DZ, PS)
    assert all(abs(a - b) < .002 for a, b in zip(got, want)), f'{ROOM}: balcony_structure {got} moved: re-fit'
    STEEL = M.solid('balcony_steel', '#33373A', 0.5)     # lantern and trough hooks: black-grey steel
    _lantern(ctx, f['lantern'])
    for i, t in enumerate(TROUGHS):
        _trough(ctx, i, *t)
    _ivy(ctx)
    _petunias(ctx, TROUGHS[2])


# ----------------------------------------------------------------------------- lantern
def _lantern(ctx, at):
    """Black four-sided coach lantern standing on an S-scroll bracket with an oval backplate (v3 f_0295), body centre
    at `at` (the feature's lantern: x 2.33 on the rear wall, Z 5.10 = 2.10 above the deck), projecting 0.22. The
    backplate stands 15 mm east of the platform edge 2.315 and 0.80 above the east rail's wall bracket: no clash."""
    x, w, ly, zb = at[0], at[1] + .001, at[1] + 0.22, at[2] - 0.115   # axis x, wall face (+1 mm), lantern axis y, bracket top
    mb = mo.MB()
    mb.at(P.Tr(x, w, zb - .02) @ P.Rot('X', -90))
    mb.lathe([(.032, 0), (.032, .008), (.022, .016), (0, .018)], STEEL, segs=16, ell=(1, 1.7))   # oval backplate
    mb.at(None)
    mb.tube([(x, w + .01, zb - .007), (x, ly, zb - .007)], .007, STEEL, n=8)                       # arm
    scroll = P._bez((x, w + .012, zb - .07), (x, w + .10, zb - .10), (x, w + .17, zb - .06), (x, ly - .02, zb - .012), 10)
    curl = [(x, w + .05 + .022 * sin(a), zb - .075 + .022 * cos(a)) for a in [pi * k / 5 for k in range(11)]]
    mb.tube(scroll, .005, STEEL, n=6)
    mb.tube(curl, .004, STEEL, n=6, up=(1, 0, 0))
    z0, z1 = zb, zb + .02                                  # bottom tray, finial below
    mb.box((x - .055, ly - .055, z0), (x + .055, ly + .055, z1), STEEL, bev=.003)
    mb.at(P.Tr(x, ly, z0))
    mb.lathe([(0, -.035), (.008, -.03), (.014, -.015), (.02, -.004), (.02, 0)], STEEL, segs=12)
    mb.at(None)
    zt = zb + .195                                         # top of the glazed body (tapered, wider at the top)
    lo, hi = .050, .075
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.tube([(x + sx * lo, ly + sy * lo, z1), (x + sx * hi, ly + sy * hi, zt)], .0045, STEEL, n=6)
    mb.box((x - .083, ly - .083, zt), (x + .083, ly + .083, zt + .014), STEEL, bev=.002)
    rings = [(.097, zt + .014), (.064, zt + .045), (.028, zt + .078), (.018, zt + .082)]       # pagoda cap
    sq = lambda h, z: [(x - h, ly - h, z), (x + h, ly - h, z), (x + h, ly + h, z), (x - h, ly + h, z)]
    mb.face(sq(*rings[0]), STEEL, hint=(0, 0, -1))
    for (h0, z0_), (h1, z1_) in zip(rings, rings[1:]):
        a, b = sq(h0, z0_), sq(h1, z1_)
        for i in range(4):
            c = Vector(a[i]) + Vector(a[(i + 1) % 4]) - 2 * Vector((x, ly, 0))
            mb.face([a[i], a[(i + 1) % 4], b[(i + 1) % 4], b[i]], STEEL, hint=(c.x, c.y, .5))
    mb.face(sq(*rings[-1]), STEEL, hint=(0, 0, 1))
    mb.at(P.Tr(x, ly, rings[-1][1]))
    mb.lathe([(.008, 0), (.012, .012), (.008, .022), (0, .03)], STEEL, segs=10)
    mb.at(None)
    for k in range(4):                                     # clear panes with an amber leaded diamond (f_0295)
        d = Vector(((1, 0, 0), (0, 1, 0), (-1, 0, 0), (0, -1, 0))[k])
        s = Vector((-d.y, d.x, 0))
        c = lambda u, hh, z: Vector((x, ly, z)) + d * (hh - .003) + s * u
        mb.face([c(-lo + .004, lo, z1), c(lo - .004, lo, z1), c(hi - .004, hi, zt), c(-hi + .004, hi, zt)], 'glass_clear',
                hint=tuple(d))
        zm, hm = (z1 + zt) / 2, (lo + hi) / 2 - .002
        mb.face([c(0, hm, zm - .045), c(.028, hm, zm), c(0, hm, zm + .045), c(-.028, hm, zm)], 'whisky', hint=tuple(d))
    body = mb.finish(f'{ROOM}.lantern')
    lamp = P.place(P.candle_bulb(.045, .018, lit=True, name=f'{ROOM}.lantern.lamp'), (x, ly, z1))
    for o in (body, lamp):
        IX.tag(o, 'lamp', g=f'{ROOM}.lantern', label='Lantern', rooms=[ROOM])
        ctx.add(o, ROOM, 'light', lm='dynamic')
    for p in P.bulb_points(lamp):
        lighting.bulb(ctx, ROOM, p, watts=12, kelvin=2700, name=f'{ROOM}.lantern.bulb')


# ----------------------------------------------------------------------------- planters
def _frame(c, al, out, u, v, z):
    """World point of trough-local (u along, v outward from the rail face) at height z."""
    return (c[0] + al[0] * u + out[0] * v, c[1] + al[1] * u + out[1] * v, z)


def _trough(ctx, i, c, al, out):
    """Dark-grey plastic trough 0.60 x 0.18 x 0.16, tapered, soil at the rim, two hooks over the top rail."""
    pm = M.solid('planter_grey', '#3C3F42', 0.6)
    mb = mo.MB()
    zb, zt = T_TOP - T_H, T_TOP
    corners = lambda hl, hw, z: [_frame(c, al, out, su * hl, sv * hw, z) for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    bot, top = corners(T_L / 2 - .03, T_W / 2 - .025, zb), corners(T_L / 2, T_W / 2, zt)
    cen = Vector((c[0], c[1], (zb + zt) / 2))
    mb.face(bot, pm, hint=(0, 0, -1))
    for k in range(4):
        q = [bot[k], bot[(k + 1) % 4], top[(k + 1) % 4], top[k]]
        h = (Vector(q[0]) + Vector(q[2])) / 2 - cen
        mb.face(q, pm, hint=(h.x, h.y, 0))
    mb.face(corners(T_L / 2 - .006, T_W / 2 - .006, zt - .012), P.mat('soil'), hint=(0, 0, 1))
    inner = corners(T_L / 2 - .006, T_W / 2 - .006, zt)
    for k in range(4):                                       # rim
        mb.face([top[k], top[(k + 1) % 4], inner[(k + 1) % 4], inner[k]], pm, hint=(0, 0, 1))
    for k in range(4):                                       # inner wall down to the soil
        a, b = inner[k], inner[(k + 1) % 4]
        a2, b2 = (a[0], a[1], zt - .012), (b[0], b[1], zt - .012)
        h = cen - (Vector(a) + Vector(b)) / 2
        mb.face([a, b, b2, a2], pm, hint=(h.x, h.y, 0))
    for su in (-.2, .2):                                     # hooks: up the trough's rail side, over the rail, down inside
        p = lambda v, z: _frame(c, al, out, su, v, z)
        v0 = -T_W / 2
        # strap 8 mm off the rail's outer face, over the tube top (1 mm air), inner leg 8 mm inside it
        for a, b in ((p(v0 - .004, zt - .06), p(v0, RAIL + .005)), (p(v0 - .072, RAIL + .001), p(v0, RAIL + .005)),
                     (p(v0 - .072, RAIL - .045), p(v0 - .068, RAIL + .005))):
            lo = [min(a[j], b[j]) for j in range(3)]
            hi = [max(a[j], b[j]) for j in range(3)]
            wv = (abs(al[0]) * .0125, abs(al[1]) * .0125)
            mb.box((lo[0] - wv[0], lo[1] - wv[1], lo[2]), (hi[0] + wv[0], hi[1] + wv[1], hi[2]), STEEL)
    ctx.add(mb.finish(f'{ROOM}.planter.{i}'), ROOM, 'decor', plan_sym='planter')


# ----------------------------------------------------------------------------- ivy
LEAF = [(0, 0), (-.42, .22), (-.36, .58), (0, 1.0), (.36, .58), (.42, .22)]   # ivy outline, base at the petiole


def _ivy_mats():
    return [(0.35, P.two_sided(M.solid('ivy_dark', '#557043', 0.6))), (0.40, P.two_sided(M.solid('ivy_mid', '#7C9760', 0.55))),
            (0.25, P.two_sided(M.solid('ivy_cream', '#C4C79C', 0.55)))]           # grey-green variegated (v2 f_0173)


def _leaf(mb, rnd, mats, base, axis, out, size, clear=None):
    axis = Vector(axis).normalized()
    out = Vector(out)
    across = out.cross(axis).normalized()
    nrm = axis.cross(across)
    r, m = rnd.random(), mats[-1][1]
    for f, mt in mats:
        if r < f:
            m = mt
            break
        r -= f
    pts = [Vector(base) + axis * (y * size) + across * (x * size) + nrm * (.12 * size * abs(x)) for x, y in LEAF]
    if clear:
        pts = _clear_pts(pts, *clear)
    mb.face(pts, m, hint=tuple(nrm))


def _strand(mb, rnd, mats, start, al, out, length, step=.03, droop=True, outside=False, cout=None, zmax=None):
    """One trailing stem: over the trough lip, then hanging with a slow outward bulge and sideways sway; leaves
    alternate along it, largest near the top. Every stem point and leaf is kept clear of the railing (`_clear`; a
    hanging strand, outside=True, also of the platform volume, pushed along `cout`, default `out`). zmax caps the stem
    height (the hedge fringe)."""
    clear = (cout or out, outside)
    al, out = Vector((*al, 0)), Vector((*out, 0))
    p = Vector(start)
    sway, n = 0.0, max(2, int(length / step))
    for k in range(n):
        t = k / n
        if droop:
            dv = Vector((0, 0, -1)) * (1 - max(0, .5 - t * 6)) + out * max(0, .9 - t * 8) + out * .08 * cos(t * 5)
        else:                                                # hedge sprig: rises and flops over
            dv = Vector((0, 0, 1)) * (1 - t * 1.6) + out * (t * 1.2 - .2)
        sway = max(-.9, min(.9, sway + rnd.uniform(-.35, .35)))
        p = _clear(p + (dv.normalized() + al * sway * .35) * step, *clear)
        if zmax is not None:
            p.z = min(p.z, zmax)
        side = 1 if k % 2 else -1
        size = rnd.uniform(.042, .072) * (1 - .3 * t)
        axis = al * side * rnd.uniform(.5, 1.0) + Vector((0, 0, rnd.uniform(-.9, .4))) + out * rnd.uniform(-.2, .4)
        face_out = out * .7 + Vector((0, 0, rnd.uniform(.1, 1.1))) + al * rnd.uniform(-.4, .4)   # leaves turn up to the light
        _leaf(mb, rnd, mats, p + al * side * .012 + out * rnd.uniform(0, .02), axis, face_out, size, clear)


def _ivy(ctx):
    """Variegated ivy: a curtain from each trough down past the deck (1.0-1.5 m below it, longest at the east
    corner and the front centre: about 0.6-1.0 m below the deck top, between the frontal v2 f_0251 (~0.5) and the
    spec's 1.0-1.5 m read from below in f_0173), stems down the face of the railing (about one in two: the lawn shows
    between the bars, f_0261) and a low fringe over the top rail: the rail stays visible end to end and the garden and
    shed show over it from the deck (v3 t284, f_0277, f_0261)."""
    rnd, mats = random.Random(11), _ivy_mats()
    for i, (c, al, out) in enumerate(TROUGHS):
        front = i < 3
        mb = mo.MB()
        n = 30
        for k in range(n):                                   # hanging strands from the outer lip
            u = -T_L / 2 + T_L * (k + rnd.random()) / n
            start = _frame(c, al, out, u * 1.15, T_W / 2 - .01, T_TOP + .01)
            wx = start[0]
            if front:
                L = 1.45 + .5 * max(0, 1 - abs(wx - 1.255) / .6) + .5 * max(0, (wx - 1.70) / .6) + rnd.uniform(-.45, .3)
            else:
                L = 1.8 * (0.55 + .45 * (start[1] - 17.76) / .6) + rnd.uniform(-.3, .2)
            _strand(mb, rnd, mats, start, al, out, max(.4, L), outside=True)
            if rnd.random() < .8:                            # short filler strand on the same spot
                _strand(mb, rnd, mats, start, al, out, rnd.uniform(.3, .8), outside=True)
            if rnd.random() < .5:                            # and a mid-length one: the curtain thins out lower down
                _strand(mb, rnd, mats, start, al, out, max(.4, L * rnd.uniform(.55, .85)), outside=True)
            # stems that drop from the rail-side lip straight down the face of the railing (v3 f_0285: a wall of
            # ivy right behind the bars, not a curtain 0.3 m away)
            if k % 2:
                rs = _frame(c, al, out, u * 1.1, -T_W / 2 + .006 + rnd.uniform(0, .015), T_TOP - T_H - .005)
                _strand(mb, rnd, mats, rs, al, (out[0] * .15, out[1] * .15), rnd.uniform(.5, 1.15), outside=True, cout=out)
        if i == 0:                                           # a heavy curtain round the north-west corner; the west
            for k in range(18):                              # rail has no trough (v2 f_0173, v3 f_0299)
                start = _frame(c, al, out, -T_L / 2 - .15 * rnd.random(), rnd.uniform(-.02, T_W / 2 - .01), T_TOP + .01)
                _strand(mb, rnd, mats, start, al, (-.5, .86), rnd.uniform(.8, 1.6), outside=True)
            for k in range(14):                              # stems trained back along the outside of the west rail
                y = YR - .53 * (k + rnd.random()) / 14       # from the corner to about half way (v13 t215)
                start = (X0 - .012 - rnd.uniform(0, .03), y, RAIL + .01)
                lw = .35 + .9 * (y - (YR - .53)) / .53 + rnd.uniform(-.15, .15)
                _strand(mb, rnd, mats, start, (0, 1), (-1, 0), max(.3, lw), outside=True)
                if k % 2:                                    # and a sprig over the rail top
                    _strand(mb, rnd, mats, (XA, y, RAIL + .03), (0, 1), (-1, 0), rnd.uniform(.12, .22), droop=False,
                            zmax=RAIL + .08)
        nh = 25                                              # fringe: short sprigs from the trough soil, at most
        for k in range(nh):                                  # 0.08 over the rail top, ~45 % flopping inward (t284)
            u = -T_L / 2 + T_L * (k + rnd.random()) / nh
            if i == 2 and -.06 < u < .28 and rnd.random() < .7:
                continue                                     # keep the petunia clump in view
            o = out if rnd.random() < .55 else (-out[0], -out[1])
            start = _frame(c, al, out, u, rnd.uniform(-T_W / 2 + .01, T_W / 2 - .01), T_TOP - .01)
            _strand(mb, rnd, mats, start, al, o, rnd.uniform(.08, .18), step=.03, droop=False, zmax=RAIL + .08)
        for k in range(5 if i < 3 else 0):                   # a few sprigs draped over the rail down its deck side
            u = -T_L / 2 + T_L * (k + rnd.random()) / 5
            start = _frame(c, al, out, u, -_OFF - PS / 2 - rnd.uniform(.01, .04), RAIL + .02)
            _strand(mb, rnd, mats, start, al, (-out[0], -out[1]), rnd.uniform(.12, .35))
        ctx.add(mb.finish(f'{ROOM}.ivy.{i}'), ROOM, 'decor')


def _petunias(ctx, trough):
    """Purple-blue petunias in the north-east trough (v3 f_0277 / t284)."""
    rnd = random.Random(5)
    c, al, out = trough
    mb = mo.MB()
    pet = P.two_sided(M.solid('petunia', '#5B3F98', 0.6))
    eye = M.solid('petunia_eye', '#2E1F4A', 0.6)
    for k in range(20):                                     # on stems above the rail, faces turned to the deck and up
        p = Vector(_frame(c, al, out, rnd.uniform(-.06, .28), rnd.uniform(-.07, .08), T_TOP + rnd.uniform(.12, .22)))
        n = Vector((rnd.uniform(-.4, .4), rnd.uniform(-.9, -.3), 1)).normalized()
        a = n.cross(Vector((1, 0, 0))).normalized()
        b = n.cross(a)
        r = rnd.uniform(.03, .04)
        ring = [p + (a * cos(2 * pi * j / 10) + b * sin(2 * pi * j / 10)) * (r if j % 2 == 0 else r * .62) + n * .006
                for j in range(10)]
        eye_ = [p + n * .0065 + (a * cos(2 * pi * j / 5) + b * sin(2 * pi * j / 5)) * .006 for j in range(5)]
        both = _clear_pts(ring + eye_)                    # keep the flowers off the rail
        p = p + (both[0] - ring[0])
        mb.face(both[:10], pet, hint=tuple(n))
        mb.face(both[10:], eye, hint=tuple(n))
        mb.tube([Vector((p.x, c[1] + rnd.uniform(-.05, .05), T_TOP - .012)), p], .002, _ivy_mats()[1][1], n=4)   # from the soil
    ctx.add(mb.finish(f'{ROOM}.petunias'), ROOM, 'decor')

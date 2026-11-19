"""balcony - bolt-on steel balcony off the rear blue bedroom (level 1, kind exterior). Spec: spec/rooms/balcony.md
(reconciled block wins: platform x 0.00..2.30, y 17.36..18.41, deck Z 3.00, lantern (2.33, 17.36, 5.10)).

The envelope built the deck, frame, railing, wall posts, struts and rain pipe (balcony.floor / .structure /
.rainpipe) and a lamp-less placeholder lantern, which this module replaces by a coach lantern with a lamp
(`lamp` tag; the switch is rooms/blue_bedroom.py 'Balcony light'). Here: lantern, four rail planters (three front,
one east) with ivy curtains and a hedge over the top rail, petunias. No furniture (the folding chair is decluttered, spec 6).
"""
import random
from math import cos, sin, pi

import bpy
from mathutils import Vector

from lib import interact as IX, lighting, materials as M, mouldings as mo, props as P

ROOM = 'balcony'
X0, X1, Y0, Y1, DZ = 0.0, 2.30, 17.36, 18.41, 3.00      # platform, deck top
RAIL = DZ + 1.10                                         # top of the top rail

CAMERAS = [
    dict(name='deck', pos=(1.20, 17.60, 4.55), look=(1.20, 18.60, 3.60), fov_deg=100, ref='v3 f_0285'),
    dict(name='lantern', pos=(1.40, 17.90, 4.50), look=(2.40, 17.36, 4.90), fov_deg=90, ref='v3 f_0295'),
    dict(name='west', pos=(1.80, 17.80, 4.55), look=(-0.50, 17.90, 4.00), fov_deg=100, ref='v3 f_0299'),
    dict(name='below', pos=(1.20, 19.80, 1.50), look=(1.20, 17.40, 4.40), fov_deg=100, ref='v2 f_0173'),
    dict(name='rear', pos=(1.20, 23.00, 1.20), look=(1.20, 17.36, 3.60), fov_deg=80, ref='v2 f_0251'),
]

# trough planters hung outside the top rail: (centre x, centre y, along unit, out unit); rail outer faces y 18.415,
# x -0.005 / 2.305 (envelope: rails 60 wide on the post line, posts clamped 25 mm inside the platform).
# Three on the front, one on the EAST side rail only: the west side rail is bare (v3 f_0269, f_0287, f_0299)
TROUGHS = [((0.42, 18.51), (1, 0), (0, 1)), ((1.15, 18.51), (1, 0), (0, 1)), ((1.88, 18.51), (1, 0), (0, 1)),
           ((2.40, 17.93), (0, 1), (1, 0))]
T_L, T_W, T_H, T_TOP = 0.60, 0.18, 0.16, RAIL - 0.05


def build(ctx):
    global STEEL
    STEEL = M.solid('balcony_steel', '#33373A', 0.5)     # = the envelope's balcony steel
    _lantern(ctx)
    for i, t in enumerate(TROUGHS):
        _trough(ctx, i, *t)
    _ivy(ctx)
    _petunias(ctx, TROUGHS[2])


# ----------------------------------------------------------------------------- lantern
def _lantern(ctx):
    """Black four-sided coach lantern standing on an S-scroll bracket with an oval backplate (v3 f_0295)."""
    old = bpy.data.objects.get(f'{ROOM}.lantern')           # envelope placeholder: no lamp, solid amber body
    if old is not None:
        bpy.data.objects.remove(old, do_unlink=True)
    x, w, ly, zb = 2.33, Y0, Y0 + 0.22, 4.985               # axis x, wall face, lantern axis y, top of the bracket
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
        for a, b in ((p(v0 - .004, zt - .06), p(v0, RAIL + .004)), (p(v0 - .072, RAIL), p(v0, RAIL + .004)),
                     (p(v0 - .072, RAIL - .045), p(v0 - .068, RAIL + .004))):
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


def _leaf(mb, rnd, mats, base, axis, out, size):
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
    mb.face(pts, m, hint=tuple(nrm))


def _strand(mb, rnd, mats, start, al, out, length, step=.03, droop=True):
    """One trailing stem: over the trough lip, then hanging with a slow outward bulge and sideways sway; leaves
    alternate along it, largest near the top."""
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
        p = p + (dv.normalized() + al * sway * .35) * step
        side = 1 if k % 2 else -1
        size = rnd.uniform(.042, .072) * (1 - .3 * t)
        axis = al * side * rnd.uniform(.5, 1.0) + Vector((0, 0, rnd.uniform(-.9, .4))) + out * rnd.uniform(-.2, .4)
        face_out = out * .7 + Vector((0, 0, rnd.uniform(.1, 1.1))) + al * rnd.uniform(-.4, .4)   # leaves turn up to the light
        _leaf(mb, rnd, mats, p + al * side * .012 + out * rnd.uniform(0, .02), axis, face_out, size)


def _ivy(ctx):
    """Variegated ivy: a curtain from each trough down past the deck (1.0-1.5 m below it, longest at the east
    corner and the front centre: about 0.6-1.0 m below the deck top, between the frontal v2 f_0251 (~0.5) and the
    spec's 1.0-1.5 m read from below in f_0173), stems down the face of the railing, a hedge over the top rail (f_0285)."""
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
                L = 1.45 + .5 * max(0, 1 - abs(wx - 1.15) / .6) + .5 * max(0, (wx - 1.6) / .7) + rnd.uniform(-.45, .3)
            else:
                L = (1.8 if out[0] > 0 else 1.3) * (0.55 + .45 * (start[1] - 17.6) / .6) + rnd.uniform(-.3, .2)
            _strand(mb, rnd, mats, start, al, out, max(.4, L))
            if rnd.random() < .8:                            # short filler strand on the same spot
                _strand(mb, rnd, mats, start, al, out, rnd.uniform(.3, .8))
            if rnd.random() < .5:                            # and a mid-length one: the curtain thins out lower down
                _strand(mb, rnd, mats, start, al, out, max(.4, L * rnd.uniform(.55, .85)))
            # stems that drop from the rail-side lip straight down the face of the railing (v3 f_0285: a wall of
            # ivy right behind the bars, not a curtain 0.3 m away)
            rs = _frame(c, al, out, u * 1.1, -T_W / 2 + .006 + rnd.uniform(0, .015), T_TOP - T_H - .005)
            _strand(mb, rnd, mats, rs, al, (out[0] * .15, out[1] * .15), rnd.uniform(.5, 1.15))
        if i == 0:                                           # a heavy curtain round the north-west corner, the west
            for k in range(18):                              # side rail itself stays bare (v2 f_0173, v3 f_0299)
                start = _frame(c, al, out, -T_L / 2 - .15 * rnd.random(), rnd.uniform(-.02, T_W / 2 - .01), T_TOP + .01)
                _strand(mb, rnd, mats, start, al, (-.5, .86), rnd.uniform(.8, 1.6))
        nh = 70                                              # hedge: a 0.2-0.3 mound burying the top rail and the
        for k in range(nh):                                  # trough lips, ~45 % flopping inward (f_0277, f_0285)
            u = -T_L / 2 + T_L * (k + rnd.random()) / nh
            if i == 2 and -.06 < u < .28 and rnd.random() < .7:
                continue                                     # keep the petunia clump in view
            o = out if rnd.random() < .55 else (-out[0], -out[1])
            v = rnd.uniform(-.12, .08)
            start = _frame(c, al, out, u, v, RAIL + .005 if v < -T_W / 2 else T_TOP - .01)
            _strand(mb, rnd, mats, start, al, o, rnd.uniform(.20, .45), step=.03, droop=False)
        for k in range(14 if i < 3 else 0):                  # sprigs draped over the rail down its deck side (f_0285)
            u = -T_L / 2 + T_L * (k + rnd.random()) / 14
            start = _frame(c, al, out, u, -T_W / 2 - rnd.uniform(.0, .05), RAIL + .01)
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
        mb.face(ring, pet, hint=tuple(n))
        mb.face([p + n * .0065 + (a * cos(2 * pi * j / 5) + b * sin(2 * pi * j / 5)) * .006 for j in range(5)], eye,
                hint=tuple(n))
        mb.tube([Vector((p.x, c[1] + rnd.uniform(-.05, .05), T_TOP - .012)), p], .002, _ivy_mats()[1][1], n=4)   # from the soil
    ctx.add(mb.finish(f'{ROOM}.petunias'), ROOM, 'decor')

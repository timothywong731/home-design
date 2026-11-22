"""Meshes of the green bathroom that no lib prop covers: slipper bath, ceramic basin, relief panels, wall clock,
plants, small brassware. Every builder returns ONE unlinked object (scale 1, UVs, materials); placement and
tags are done in rooms/green_bathroom.py. Local frames are stated per builder."""
import math
from math import cos, sin, pi, copysign

import bpy
from mathutils import Matrix, Vector

from lib import materials as M, mouldings as mo, props as P

L, W = 0.775, 0.36           # bath half length / half width
WASTE_X = -0.10              # bath-local x of the centre waste and the overflow


# ----------------------------------------------------------------------------- helpers
def loft(name, rings, mat, cap_first=True, cap_last=True, sharp=50):
    """Smooth skin over rings of equal point count (each counter-clockwise seen from +Z)."""
    n = len(rings[0])
    faces = [(i * n + j, i * n + (j + 1) % n, (i + 1) * n + (j + 1) % n, (i + 1) * n + j)
             for i in range(len(rings) - 1) for j in range(n)]
    if cap_first:
        faces.append(tuple(range(n))[::-1])
    if cap_last:
        faces.append(tuple(range((len(rings) - 1) * n, len(rings) * n)))
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for r in rings for v in r], [], faces)
    me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    me.set_sharp_from_angle(angle=math.radians(sharp))
    me.uv_layers.new(name='UVMap')
    me.materials.append(P.mat(mat) if isinstance(mat, str) else mat)
    return bpy.data.objects.new(name, me)


def share(ob, name):
    """Second object on the same mesh (linked duplicate)."""
    return bpy.data.objects.new(name, ob.data)


def _sring(z, axn, axp, ay, e=2.6, n=48):
    """Superellipse ring: half length axn toward -X, axp toward +X, half width ay; z = const or f(x)."""
    out = []
    for i in range(n):
        t = 2 * pi * i / n
        c, s = cos(t), sin(t)
        x = (axp if c > 0 else axn) * copysign(abs(c) ** (2 / e), c)
        y = ay * copysign(abs(s) ** (2 / e), s)
        out.append((x, y, z(x) if callable(z) else z))
    return out


def _rrect(xa, xb, ya, yb, z, r, n=4):
    """Rounded rectangle, counter-clockwise from above, 4 * (n + 1) points."""
    pts = []
    for cx, cy, a0 in ((xb - r, ya + r, -pi / 2), (xb - r, yb - r, 0), (xa + r, yb - r, pi / 2), (xa + r, ya + r, pi)):
        for i in range(n + 1):
            a = a0 + pi / 2 * i / n
            pts.append((cx + r * cos(a), cy + r * sin(a), z))
    return pts


# ----------------------------------------------------------------------------- slipper bath
def rim(x):
    """Rim height of the single-slipper bath: 0.60 at the tap end (-X), rising to 0.78 at the raised end (+X)."""
    return 0.60 + 0.18 * max(0.0, (x / L + 0.15) / 1.15) ** 2.4


def slipper_bath(name):
    """Free-standing single-slipper roll-top bath 1.55 x 0.72 (green_bathroom.md 5.1). Local frame: centre of
    the footprint at z = 0 (floor), length along X, tap end -X, raised end +X; underside 0.15 up (claw feet are
    separate). Interior floor at z 0.21."""
    r = lambda dz: (lambda x: rim(x) + dz)
    rings = [_sring(z, a, b, c) for z, a, b, c in (
        (.15, .60, .60, .25), (.16, .64, .64, .275), (.21, .70, .70, .31), (.31, .74, .745, .337),
        (.45, .762, .768, .352), (r(-.06), .772, .775, .360), (r(-.028), .788, .790, .374),
        (r(-.006), .782, .784, .368), (r(0), .768, .770, .355),                      # rolled rim
        (r(-.008), .752, .754, .340), (r(-.035), .742, .744, .330), (r(-.08), .728, .715, .318),
        (.42, .705, .60, .300), (.28, .68, .44, .250), (.21, .64, .33, .200))]
    ob = loft(name, rings, 'ceramic_white', sharp=60)
    # brass centre waste, overflow on the east (local -Y) inner wall above it and the bead chain between them
    # (v4 f_0106: overflow about mid-length on the far inner wall; v4 f_0118: brass rose with its chain)
    mb = mo.MB()
    br = 'gold_champagne'
    mb.at(Matrix.Translation((WASTE_X, 0, .2105)))
    mb.lathe([(0, 0), (.034, 0), (.034, .0015), (.032, .004), (0, .004)], br, 20)
    mb.at(Matrix.Translation((WASTE_X, -.304, .462)) @ Matrix.Rotation(math.radians(-80), 4, 'X'))
    mb.lathe([(0, -.004), (.024, -.004), (.024, .001), (.020, .005), (0, .006)], br, 20)
    mb.at()
    mb.tube([(WASTE_X, -.300, .440), (WASTE_X, -.297, .42), (WASTE_X, -.246, .282), (WASTE_X, -.186, .2155),
             (WASTE_X, -.035, .2135)], .0016, br, n=6)
    waste = mb.finish(name + '.waste')
    waste.parent = ob
    return ob


# ----------------------------------------------------------------------------- basin
BASIN_TAP = (0.0, -0.065, 0.14)       # local tap centre on the deck
BASIN_FLOOR = 0.03                    # bowl floor above the underside


def basin(name):
    """White rectangular ceramic counter basin 0.60 x 0.48 x 0.14 sitting on its cabinet (green_bathroom.md 5.3).
    Wall-prop frame: back on y = 0, front toward -Y, x across, z = 0 the underside. Tap ledge behind the bowl,
    brushed-brass click waste."""
    n = 5
    hw, d = .30, .48
    outer = lambda z, i, r: _rrect(-hw + i, hw - i, -d + i, -i, z, r, n)
    bowl = lambda z, i, r: _rrect(-.255 + i, .255 - i, -.455 + i, -.118 - i, z, r, n)
    rings = [outer(0, .004, .016), outer(.004, 0, .02), outer(.134, 0, .02), outer(.14, .003, .018),
             bowl(.14, 0, .03), bowl(.133, .004, .032), bowl(.07, .018, .05), bowl(.042, .04, .06),
             bowl(BASIN_FLOOR, .055, .055)]
    ob = loft(name, rings, 'ceramic_white')
    mb = mo.MB()
    mb.at(Matrix.Translation((0, -.29, BASIN_FLOOR + .0005)))
    mb.lathe([(.020, 0), (.020, .003), (.016, .005), (0, .005)], 'gold_champagne', 16)
    mb.at()
    w = mb.finish(name + '.waste')
    w.parent = ob
    return ob


# ----------------------------------------------------------------------------- carved relief panels B2 / B3
def relief_panel(name, flip=False, size=(.50, 1.00)):
    """Bronzed low-relief plaque in a dull-gold-over-black frame, `size` w x h (designed at 0.50 x 1.00, B2 / B3):
    arched niche with an urn on a plinth and a spray of acanthus leaves (generic, no figure). Wall prop: origin
    centre of the back, front -Y. flip mirrors the leaf spray (the pair)."""
    hw, hh, fw, fd = .25, .50, .045, .034
    gold, black = P.mat('gold_bronze'), P.mat('black_matt')
    bronze = M.solid('gbath_relief_bronze', '#3B2B1F', .5, .25)
    mb = mo.MB()
    for x0, x1, z0, z1 in ((-hw, -hw + fw, -hh, hh), (hw - fw, hw, -hh, hh), (-hw + fw, hw - fw, -hh, -hh + fw),
                           (-hw + fw, hw - fw, hh - fw, hh)):
        mb.box((x0, -fd, z0), (x1, 0, z1), gold, bev=.006)
    i = hw - fw
    for x0, x1, z0, z1 in ((-i, -i + .008, -hh + fw, hh - fw), (i - .008, i, -hh + fw, hh - fw),
                           (-i, i, -hh + fw, -hh + fw + .008), (-i, i, hh - fw - .008, hh - fw)):
        mb.box((x0, -fd + .006, z0), (x1, -.012, z1), black)
    mb.box((-i, -.014, -hh + fw), (i, -.004, hh - fw), bronze)                       # board
    rs, za, zb = .15, -.40, .20                                                       # arched niche bead
    arch = [(-rs, -.0155, za)] + [(-rs * cos(pi * k / 12), -.0155, zb + rs * sin(pi * k / 12)) for k in range(13)] + [(rs, -.0155, za)]
    mb.tube(arch, .009, bronze, n=8, closed=True, up=(0, 1, 0))
    mb.box((-.12, -.040, -.42), (.12, -.014, -.37), bronze, bev=.004)               # plinth
    mb.at(Matrix.Translation((0, -.014, -.37)))
    mb.lathe([(0, 0), (.040, 0), (.036, .018), (.022, .028), (.028, .040), (.068, .095), (.080, .150),
              (.070, .200), (.040, .222), (.046, .236), (.062, .246), (0, .248)], bronze, 16, ell=(1, .45), a0=pi, a1=2 * pi)
    s = -1 if flip else 1
    for k, (ang, ln, wd) in enumerate(((-62, .20, .07), (-40, .27, .08), (-18, .33, .085), (4, .38, .09),
                                        (24, .31, .085), (46, .25, .08), (68, .18, .065))):
        mb.at(Matrix.Translation((0, -.014, -.13)) @ Matrix.Rotation(math.radians(s * ang), 4, 'Y')
              @ Matrix.Rotation(math.radians(90), 4, 'X'))
        mb.leaf(ln, wd, .016, bronze, segs=8, serrate=.25, curl=.6 if k % 2 else -.3, round_=.8)
    for x, z in ((-.09, .14), (.10, .22), (.0, .30)):                                 # three rosettes in the spray
        mb.at(Matrix.Translation((s * x, -.014, z)) @ Matrix.Rotation(math.radians(90), 4, 'X'))
        mb.dome(.022, .022, .014, bronze, segs=10, rings=3)
    mb.at()
    ob = mb.finish(name, sharp_deg=40)
    ob.data.transform(Matrix.Diagonal((size[0] / .50, 1, size[1] / 1.00, 1)))   # solid colours: UV stretch is harmless
    return ob


# ----------------------------------------------------------------------------- wall clock B4
CLOCK_R, CLOCK_FACE = .15, .020


def wall_clock(name):
    """Round quartz wall clock dia 0.30: thin gold rim, white dial with black hour batons (the hands are live,
    P.clock_hands). Wall prop: origin centre of the back, dial facing -Y at y = -CLOCK_FACE."""
    mb = mo.MB()
    mb.at(Matrix.Rotation(math.radians(90), 4, 'X'))                 # lathe axis +Z -> -Y
    mb.lathe([(0, 0), (.150, 0), (.150, .024), (.146, .033), (.139, .032), (.137, .022)], 'gilt_bright', 40)
    mb.lathe([(.137, CLOCK_FACE), (0, CLOCK_FACE)], M.solid('gbath_dial', '#F4F3EF', .35), 40)
    mb.at()
    for k in range(12):
        a = 2 * pi * k / 12
        ln = .022 if k % 3 == 0 else .013
        r0, r1 = .128 - ln, .128
        wd = .006 if k % 3 == 0 else .0035
        mb.at(Matrix.Rotation(-a, 4, 'Y'))
        mb.box((-wd / 2, -CLOCK_FACE - .0008, r0), (wd / 2, -CLOCK_FACE + .0005, r1), 'black_matt')
    mb.at()
    return mb.finish(name, sharp_deg=40)


# ----------------------------------------------------------------------------- plants
def _pot(mb, dia, h, mat, ribs=0):
    r = dia / 2
    mb.lathe([(0, 0), (r * .78, 0), (r * .80, .01), (r * .98, h * .9), (r, h), (r * .93, h), (r * .9, h * .9)], mat,
             max(16, ribs))
    mb.lathe([(r * .9, h * .88), (0, h * .88)], P.mat('soil'), 14)


def fern(name, seed=0):
    """Bird's-nest fern (Asplenium) in a brown clay pot dia 0.14 (B5, v4 f_0150 / f_0152): eleven broad undivided
    fronds with crinkled margins and a dark midrib, a few upright in the middle, the rest arching out and drooping at
    the tips. Origin: base centre."""
    import random
    rnd = random.Random(seed)
    mb = mo.MB()
    _pot(mb, .14, .13, M.solid('gbath_clay', '#7A4E36', .85))
    green = P.two_sided(M.solid('gbath_fern', '#5A7E37', .55))
    rib = P.two_sided(M.solid('gbath_fern_rib', '#3B5524', .6))
    for k in range(12):
        az = 360 * k / 12 * 5 + rnd.uniform(-12, 12)
        inner = k < 4 or -sin(math.radians(az)) < -.45            # fronds toward the wall (local -X) stand up
        mb.at(Matrix.Translation((0, 0, .115)) @ Matrix.Rotation(math.radians(az), 4, 'Z'))
        if inner:
            _frond(mb, green, rib, rnd.uniform(.23, .29), rnd.uniform(.08, .095), rnd.uniform(66, 78), rnd.uniform(15, 35))
        else:
            _frond(mb, green, rib, rnd.uniform(.28, .35), rnd.uniform(.09, .11), rnd.uniform(38, 52), rnd.uniform(-45, -20))
    mb.at()
    return mb.finish(name, sharp_deg=70)


def _frond(mb, mat, rib, ln, wd, a0, a1, n=12):
    """Strap frond from the origin along local +Y: elevation a0 deg at the base bending to a1 at the tip; short stalk,
    widest past the middle, blunt tip; cupped section with a crinkled (wavy) margin and a narrow darker midrib."""
    c, rows = Vector((0, 0, 0)), []
    xs = ((-1, .32), (-.5, .08), (-.07, -.02), (.07, -.02), (.5, .08), (1, .32))
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + (a1 - a0) * t ** 1.3)
        d, nrm = Vector((0, cos(a), sin(a))), Vector((0, -sin(a), cos(a)))
        w = .5 * wd * max(.08, sin(pi * min(1.0, t ** 1.25 * 1.02)) ** .55)
        wave = .015 * sin(t * ln / .022 * 2 * pi) * min(1.0, 3 * t)
        rows.append(mb._vs([c + Vector((x * w, 0, 0)) + nrm * (h * w + wave * abs(x) ** 2) for x, h in xs]))
        c = c + d * (ln / n)
    mg, mr = mb.mi(mat), mb.mi(rib)
    for i in range(n):
        for j in range(5):
            mb._f([rows[i][j], rows[i][j + 1], rows[i + 1][j + 1], rows[i + 1][j]], mr if j == 2 else mg,
                  [(j / 5, i / n), ((j + 1) / 5, i / n), ((j + 1) / 5, (i + 1) / n), (j / 5, (i + 1) / n)])


def peace_lily(name, seed=3):
    """Peace lily in a ribbed dark-green pot dia 0.14 (B5): dark glossy lanceolate leaves and two white spathes."""
    import random
    rnd = random.Random(seed)
    mb = mo.MB()
    _pot(mb, .14, .13, M.solid('gbath_pot_green', '#2E3A33', .5), ribs=24)
    leaf, stalk = P.two_sided(P.mat('leaf_green')), P.mat('leaf_mid')
    white = P.two_sided(M.solid('gbath_spathe', '#F1F1EA', .5))
    for k in range(10):                                  # room half only (az 95..265, local -Y): it stands at the glass
        az, tilt, ln = 95 + 170 * k / 9 + rnd.uniform(-4, 4), rnd.uniform(35, 70), rnd.uniform(.08, .16)
        R = Matrix.Rotation(math.radians(az), 4, 'Z')
        top = R @ Vector((0, ln * cos(math.radians(tilt)), .12 + ln * sin(math.radians(tilt))))
        mb.tube([(0, 0, .11), tuple(top)], .003, stalk, n=5)
        mb.at(Matrix.Translation(top) @ R @ Matrix.Rotation(math.radians(tilt - 25), 4, 'X'))
        mb.leaf(rnd.uniform(.13, .18), rnd.uniform(.05, .065), .008, leaf, segs=6, curl=-.8, round_=1.0)
        mb.at()
    for az in (140, 220):
        R = Matrix.Rotation(math.radians(az), 4, 'Z')
        top = R @ Vector((0, .04, .40))
        mb.tube([(0, 0, .11), tuple(top)], .0025, stalk, n=5)
        mb.at(Matrix.Translation(top) @ R @ Matrix.Rotation(math.radians(70), 4, 'X'))
        mb.leaf(.08, .045, .012, white, segs=5, round_=1.0, curl=1.2)
        mb.at()
    return mb.finish(name, sharp_deg=60)


# ----------------------------------------------------------------------------- small hardware
def roll_holder(name):
    """Brushed-brass toilet-roll holder with a small flat shelf over the roll. Wall prop (origin back centre)."""
    br = 'gold_champagne'
    mb = mo.MB()
    mb.box((-.075, -.008, -.03), (.075, 0, .03), br, bev=.002)                     # back plate
    mb.box((-.08, -.11, .045), (.08, -.004, .051), br, bev=.0015)                  # shelf
    mb.box((-.075, -.012, .030), (-.065, -.008, .048), br)
    mb.box((.065, -.012, .030), (.075, -.008, .048), br)
    mb.tube([(-.055, -.008, 0), (-.055, -.06, 0), (.06, -.06, 0)], .006, br, n=10)  # arm
    mb.at(Matrix.Translation((.0, -.06, 0)) @ Matrix.Rotation(math.radians(90), 4, 'Y'))
    mb.lathe([(.022, -.05), (.056, -.05), (.058, -.046), (.058, .046), (.056, .05), (.022, .05)], P.mat('plastic_white'), 20)
    mb.at()
    return mb.finish(name, sharp_deg=40)


def brush_holder(name):
    """Wall-mounted toilet brush (v4 f_0108 / f_0162): brushed-brass rosette and ring at z 0.20 holding a dark bronze
    cup z 0.06..0.20, brass handle with a knob to z 0.44, standing in the cup. Wall prop: origin on the wall at FLOOR
    level (the cup is 0.06 clear of the floor)."""
    br = 'gold_champagne'
    mb = mo.MB()
    mb.at(Matrix.Translation((0, 0, .20)) @ Matrix.Rotation(math.radians(90), 4, 'X'))      # rosette on the wall
    mb.lathe([(0, 0), (.022, 0), (.022, .004), (.018, .008), (0, .009)], br, 20)
    mb.at()
    mb.box((-.004, -.022, .196), (.004, -.007, .204), br)                                     # arm to the ring
    mb.tube([(.042 * cos(2 * pi * k / 20), -.064 + .042 * sin(2 * pi * k / 20), .20) for k in range(20)],
            .0035, br, n=6, closed=True, up=(0, 0, 1))
    mb.at(Matrix.Translation((0, -.064, .06)))
    mb.lathe([(0, 0), (.030, 0), (.036, .010), (.0385, .03), (.0385, .142), (.0355, .142), (.0355, .012), (0, .012)],
             'bronze_dark', 20)                                                                # cup
    mb.lathe([(0, .03), (.006, .03), (.006, .36), (.010, .365), (.011, .376), (.007, .384), (0, .385)], br, 12)  # handle
    mb.at()
    return mb.finish(name, sharp_deg=40)


def wall_dish(name, kind='dish'):
    """Brushed-brass wall holder by a basin (v4 f_0150): round rosette, short arm and a ring 0.09 across carrying a
    shallow brass soap dish (kind 'dish') or a clear glass tumbler ('tumbler'). Wall prop: origin on the wall at the
    ring height."""
    br = 'gold_champagne'
    mb = mo.MB()
    mb.at(Matrix.Rotation(math.radians(90), 4, 'X'))
    mb.lathe([(0, 0), (.020, 0), (.020, .004), (.016, .008), (0, .009)], br, 20)
    mb.at()
    mb.box((-.004, -.040, -.004), (.004, -.007, .004), br)
    cy = -.085
    mb.tube([(.045 * cos(2 * pi * k / 24), cy + .045 * sin(2 * pi * k / 24), 0) for k in range(24)],
            .004, br, n=6, closed=True, up=(0, 0, 1))
    mb.at(Matrix.Translation((0, cy, 0)))
    if kind == 'dish':
        mb.lathe([(0, -.014), (.030, -.014), (.044, -.002), (.047, .003), (.043, .003), (.028, -.010), (0, -.010)], br, 24)
    else:
        mb.lathe([(0, -.030), (.032, -.030), (.037, .072), (.0345, .072), (.0295, -.026), (0, -.026)], 'glass_clear', 20)
    mb.at()
    return mb.finish(name, sharp_deg=40)


def claw_foot(name, mat):
    """Ball-and-claw foot of the slipper bath (v4 f_0106 / f_0112): ball dia 0.052 gripped by three claws, a swelling
    S-leg rising 0.21 and leaning back into the tub's belly, an acanthus leaf on its knee. Local frame: origin on the
    floor under the leg, the claw points +X (outward)."""
    mb = mo.MB()
    bx, br_ = .016, .026
    mb.at(Matrix.Translation((bx, 0, 0)))
    mb.lathe([(0, 0)] + [(br_ * sin(pi * k / 10), br_ * (1 - cos(pi * k / 10))) for k in range(1, 10)] + [(0, 2 * br_)],
             mat, 16)
    mb.at()
    for a in (0, 75, -75):                                                     # claws over the ball, knuckled
        c, s_ = cos(math.radians(a)), sin(math.radians(a))
        pts = []
        for el in (78, 55, 30, 5, -22):
            e = math.radians(el)
            r = br_ + .006 + (.004 if el == 30 else 0)
            pts.append((bx + r * cos(e) * c, r * cos(e) * s_, br_ + r * sin(e)))
        mb.tube(pts, .0075, mat, n=7)
    mi = mb.mi(mat)                                                            # swelling S-leg: horizontal rings
    spine = [(.012, .050, .018), (.022, .075, .021), (.030, .105, .025), (.028, .135, .027), (.012, .165, .030),
             (-.008, .190, .034), (-.022, .212, .038)]
    n = 12
    rings = [mb._vs([(x + r * cos(2 * pi * k / n), r * .85 * sin(2 * pi * k / n), z) for k in range(n)])
             for x, z, r in spine]
    for i in range(len(rings) - 1):
        for k in range(n):
            mb._f([rings[i][k], rings[i][(k + 1) % n], rings[i + 1][(k + 1) % n], rings[i + 1][k]], mi,
                  [(k / n, i * .03), ((k + 1) / n, i * .03), ((k + 1) / n, (i + 1) * .03), (k / n, (i + 1) * .03)])
    mb._f(rings[-1], mi)
    mb._f(rings[0][::-1], mi)
    al = math.radians(18)                                                      # leaf on the knee, tip down and out
    R = Matrix(((0, sin(al), cos(al), 0), (-1, 0, 0, 0), (0, -cos(al), sin(al), 0), (0, 0, 0, 1)))
    mb.at(Matrix.Translation((.030, 0, .185)) @ R)
    mb.leaf(.095, .062, .012, mat, segs=6, serrate=.3, curl=-.6, round_=.8)
    mb.at()
    return mb.finish(name, sharp_deg=50)


def dough_bowl(name, length=.44, width=.094, h=.066):
    """Long pale wooden 'dough bowl' trough for the duct niches (v4 f_0162): oval with raised ends, flaring sides, a
    hollow 12 mm in from the rim. Local frame: origin at the centre of the base, length along Y."""
    a, b = length / 2, width / 2
    rim = lambda x: h + .024 * (abs(x) / a) ** 4
    rings = [_sring(0, a * .86, a * .86, b * .74, e=2.4, n=32), _sring(h * .45, a * .96, a * .96, b * .94, e=2.4, n=32),
             _sring(rim, a, a, b, e=2.4, n=32),
             _sring(lambda x: rim(x * a / (a - .012)) - .002, a - .012, a - .012, b - .010, e=2.4, n=32),
             _sring(h * .40, a * .88, a * .88, b * .66, e=2.4, n=32), _sring(.014, a * .78, a * .78, b * .5, e=2.4, n=32)]
    ob = loft(name, rings, M.solid('gbath_bowl_wood', '#9E8A6E', .75), sharp=70)    # weathered, greyed
    ob.data.transform(Matrix.Rotation(math.radians(90), 4, 'Z'))
    return ob


def moss_mounds(name, centres, seed=5):
    """Clumps of preserved bun moss / boxwood (v4 f_0162 top niche): bumpy spheroids, flattened underneath, matt
    dark green. centres = [(x, y, z, r)] in the object frame (z = bottom of the clump)."""
    import bmesh
    import random
    rnd = random.Random(seed)
    bm = bmesh.new()
    for cx, cy, cz, r in centres:
        g = bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
        waves = [(Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1))).normalized(), rnd.uniform(4, 7),
                  rnd.uniform(0, 2 * pi)) for _ in range(4)]                   # low-frequency lumps, then fine fuzz
        for v in g['verts']:
            d = v.co.normalized()
            k = r * (1 + sum(.05 * cos(f * d.dot(u) + ph) for u, f, ph in waves) + rnd.uniform(-.025, .025))
            z = d.z * k * (1.0 if d.z > 0 else .55)
            v.co = Vector((cx + d.x * k * .78, cy + d.y * k, cz + r * .55 + z))     # x = niche depth: narrower
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    me.uv_layers.new(name='UVMap')
    me.materials.append(M.solid('gbath_moss', '#3A4E2C', .95))
    return bpy.data.objects.new(name, me)


def succulents(name, spots, seed=7):
    """Small echeveria / sedum rosettes for the middle niche (v4 f_0162): three rings of fleshy pointed leaves round
    a tight centre, grey-green, green and red-tinged. spots = [(x, y, z, dia)] (z = soil level). One object."""
    import random
    rnd = random.Random(seed)
    mb = mo.MB()
    cols = (M.solid('gbath_succ_grey', '#93A68C', .55), M.solid('gbath_succ_green', '#6C8C4C', .55),
            M.solid('gbath_succ_red', '#8E6258', .55), M.solid('gbath_succ_blue', '#7F9C98', .55))
    for k, (x, y, z, dia) in enumerate(spots):
        mat = cols[(k * 3) % 4]
        for ring, (nl, ln, el) in enumerate(((9, dia * .55, 46), (7, dia * .44, 63), (5, dia * .30, 79))):
            off = rnd.uniform(0, 360)
            for i in range(nl):
                az = off + 360 * i / nl
                mb.at(Matrix.Translation((x, y, z + .004 * ring)) @ Matrix.Rotation(math.radians(az), 4, 'Z')
                      @ Matrix.Rotation(math.radians(el), 4, 'X'))
                mb.leaf(ln, ln * .50, ln * .30, mat, segs=4, round_=1.0, curl=.8)
        mb.at(Matrix.Translation((x, y, z)))
        mb.dome(dia * .12, dia * .12, dia * .16, mat, segs=6, rings=2)
    mb.at()
    return mb.finish(name, sharp_deg=60)


def fan(name):
    """White square extractor fan 0.16 x 0.16 with a round louvred grille. Wall prop."""
    mb = mo.MB()
    w = P.mat('plastic_white')
    mb.box((-.08, -.03, -.08), (.08, 0, .08), w, bev=.006)
    mb.at(Matrix.Translation((0, -.030, 0)) @ Matrix.Rotation(math.radians(90), 4, 'X'))
    for k in range(4):
        r = .062 - k * .014
        mb.lathe([(r, 0), (r, .004), (r - .006, .004)], P.mat('plastic_dark') if k == 3 else w, 24)
    mb.at()
    return mb.finish(name, sharp_deg=40)

"""Hallway furnishing (spec/rooms/hallway.md): console table, gilt mirror, banjo barometer, the six paintings,
mosaic wall clock, switches / sockets / thermostat / PIR / smoke alarm / Wi-Fi access point, overhead cupboard
door, door stops + cabin hooks and the eight recessed downlights. Coordinates are world (hall local y + offset,
see the "Reconciled dimensions" table of the spec).

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --only shell,vestibule,hallway --preview vestibule,hallway --res 540x960 --samples 64 --tag hall
"""
import os
from math import atan2, cos, sin, pi, tau, hypot, radians

import bpy
from mathutils import Matrix

from lib import lighting, materials as M, mouldings as mo, props as P

ROOM = 'hallway'
ART = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'textures', 'art', ROOM)

CAMERAS = [
    dict(name='front', pos=(-0.05, 2.95, 1.6), look=(0.05, 6.5, 0.7), fov_deg=100, ref='f_0064'),
    dict(name='console', pos=(0.55, 3.55, 1.35), look=(-0.65, 3.7, 1.25), fov_deg=100, ref='f_0068'),
    dict(name='e1', pos=(-0.3, 3.85, 1.6), look=(0.65, 3.2, 1.6), fov_deg=100, ref='f_0076'),
    dict(name='back', pos=(0.1, 4.75, 1.6), look=(0.0, 1.83, 1.4), fov_deg=100, ref='f_0781'),
    dict(name='passage', pos=(-0.2, 6.2, 1.6), look=(-0.3, 12.0, 1.5), fov_deg=100, ref='f_0273'),
    dict(name='w3', pos=(0.9, 8.2, 1.6), look=(-0.65, 8.1, 1.35), fov_deg=100, ref='f_0770'),
    dict(name='arch', pos=(0.0, 8.13, 1.6), look=(0.0, 10.0, 2.7), fov_deg=100, ref='f_0283'),
    dict(name='rear', pos=(-0.1, 12.6, 1.6), look=(-0.1, 6.0, 1.4), fov_deg=100, ref='f_0745'),
]

RX = Matrix.Rotation(pi / 2, 4, 'X')            # local +Z -> -Y: lathes / leaves that face out of a wall
WEST, EAST, NORTH = (1, 0), (-1, 0), (0, -1)    # wall normals into the hall


def T(x=0.0, y=0.0, z=0.0):
    return Matrix.Translation((x, y, z))


def RY(deg):
    return Matrix.Rotation(radians(deg), 4, 'Y')


def loop(mb, pts, r, mat, up, n=5, closed=True):
    """Round bar along pts lying in the plane whose normal is `up` (mb.tube degenerates on vertical loops)."""
    prof = [(r * cos(tau * i / n), r * sin(tau * i / n)) for i in range(n)]
    mb.sweep(prof + prof[:1], pts, mat, closed=closed, up=up)


def curve(keys, n=5):
    """Smooth-stepped polyline through (s, v) keys."""
    out = []
    for (s0, v0), (s1, v1) in zip(keys, keys[1:]):
        for i in range(n):
            t = i / n
            out.append((s0 + (s1 - s0) * t, v0 + (v1 - v0) * t * t * (3 - 2 * t)))
    return out + [keys[-1]]


# ----------------------------------------------------------------------------- console table
# Leg centres (half plan, x >= 0; mirrored): back legs at the wall ends 0.88 apart, front legs 0.48 apart and
# 0.26 further out - measured on F_0236 (socket 146 mm = scale) and the near-frontal F_0795; the top runs from
# 0.09 inside the mirror's south edge (F_0067) to 0.13 inside its north edge (F_0236).
CON_BACK, CON_FRONT = (.44, -.045), (.24, -.305)

APRON_FRONT = [(0, .13), (.05, .126), (.2, .086), (.32, .09), (.39, .116), (.5, .12), (.61, .116), (.68, .09),
               (.8, .086), (.95, .126), (1, .13)]
APRON_SIDE = [(0, .13), (.14, .122), (.5, .088), (.86, .122), (1, .13)]


def _outline(d, back=0.0, bow=.012, n=4):
    """Half-octagon parallel to the leg frame, d outside the leg centres; both ends return square to y = back.
    The cants and the front swell out by `bow` (the real top reads as a flattened D, F_0236 / F_0070).
    Listed counter-clockwise seen from above (reverse it for mb.sweep: left of travel = outside)."""
    (bx, by), (fx, fy) = CON_BACK, CON_FRONT
    L = hypot(bx - fx, by - fy)
    nx, ny = (by - fy) / L, -(bx - fx) / L                      # outward normal of the right-hand cant
    c = nx * fx + ny * fy + d                                   # cant line: n . p = c
    xf = (c - ny * (fy - d)) / nx                               # front corner, on y = fy - d
    ye = (c - nx * (bx + d)) / ny                               # where the cant meets the square end x = bx + d
    half = [(bx + d, back)]
    for i in range(n + 1):                                      # cant, wall end -> front corner
        t = i / n
        o = bow * 4 * t * (1 - t)
        half.append((bx + d + (xf - bx - d) * t + nx * o, ye + (fy - d - ye) * t + ny * o))
    front = [(-xf + 2 * xf * i / n, fy - d - bow * 4 * (i / n) * (1 - i / n)) for i in range(1, n)]
    return [(-x, y) for x, y in half] + front + half[::-1]


def _apron(mb, p0, p1, keys, mat, t=.018, z1=.738, grain=None):
    (x0, y0), (x1, y1) = p0, p1
    L = hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy, ux
    if nx * (0 - x0) + ny * (-.17 - y0) < 0:        # thickness goes toward the middle of the table
        nx, ny = -nx, -ny
    pts = [(x0, y0, z1)] + [(x0 + ux * L * s, y0 + uy * L * s, z1 - d) for s, d in curve(keys)] + [(x1, y1, z1)]
    mb.prism(pts, (nx * t, ny * t, 0), mat, grain=grain)


def _board(a, b, w, bow=0.0, cusp=(0.0, 0.0), n=16):
    """Flat stretcher board from a to b (2D outline), half-width w / 2. bow = sag of the centre line to the
    LEFT of a -> b (a circular-ish arc); cusp = (left, right) extra width that swells in two concave sweeps
    to a point at mid-length (the bracket-shaped side stretchers)."""
    L = hypot(b[0] - a[0], b[1] - a[1])
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    lt, rt = [], []
    for i in range(n + 1):
        t = i / n
        o = bow * 4 * t * (1 - t)
        k = (1 - abs(2 * t - 1)) ** 2
        x, y = a[0] + ux * L * t - uy * o, a[1] + uy * L * t + ux * o
        s = bow * 4 * (1 - 2 * t) / L                           # slope of the bowed centre line
        d = hypot(1, s)
        nx, ny = (-uy - ux * s) / d, (ux - uy * s) / d          # its left normal
        lt.append((x + nx * (w / 2 + cusp[0] * k), y + ny * (w / 2 + cusp[0] * k)))
        rt.append((x - nx * (w / 2 + cusp[1] * k), y - ny * (w / 2 + cusp[1] * k)))
    return lt + rt[::-1]


def console(name):
    """William-and-Mary credence table 0.95 x 0.36 x 0.76 in polished figured walnut: half-octagon top with a
    thumb-moulded edge (back 0.95 on the wall, long canted sides, front 0.52), scalloped apron on the three
    outer sides, back legs at the two wall ends and front legs at the cant corners, each with a faceted bell
    ("inverted cup") over a tapering octagonal shaft, ball turning, block and bun foot; flat stretchers:
    straight back rail, bracket-shaped boards along the cants, one board bowed back between the front legs
    (F_0236, F_0068, F_0795). Local frame: back on y = 0, front -Y, width along X. Origin floor. [H]"""
    # ponytail: generated figure (reference/work/hall/r2/gen_tex.py), no normal map; the library dark woods are
    # near-uniform (std 2-5 / 255) and rendered as a black silhouette. Swap the JPG for a real burr veneer scan.
    wood = M.image_mat('console_walnut', os.path.join(ART, 'console_walnut.jpg'), size_m=(.6, .6), roughness=0.2)
    (bx, by), (fx, fy) = CON_BACK, CON_FRONT
    mb = mo.MB()
    # top 22 mm: flat board + thumb-moulded edge swept round the three outer sides (step, quarter round, fillet)
    zt = .738
    mb.prism([(x, y, zt) for x, y in _outline(.022)], (0, 0, .022), wood, grain=0)
    thumb = [(0, 0), (.004, 0), (.008, .005), (.008, .009), (.013, .010), (.014, .014), (.012, .019), (.008, .022),
             (0, .022)]
    mb.sweep(thumb, [(x, y, zt) for x, y in _outline(.022, back=.0005)[::-1]], wood)     # top overhangs 36 mm
    # apron: outer faces 3 mm behind the leg blocks, ends buried in the blocks
    L = hypot(bx - fx, by - fy)
    ux, uy = (bx - fx) / L, (by - fy) / L                       # along the right cant, front -> back
    nx, ny = uy, -ux                                            # its outward normal
    o = .0195
    _apron(mb, (-fx + .015, fy - o), (fx - .015, fy - o), APRON_FRONT, wood, grain=0)
    for sx in (1, -1):
        _apron(mb, (sx * (fx + ux * .008 + nx * o), fy + uy * .008 + ny * o),
               (sx * (bx - ux * .008 + nx * o), by - uy * .008 + ny * o), APRON_SIDE, wood, grain=1)
    mb.box((-bx, by + .0015, .628), (bx, by + .0195, .738), wood, grain=0)                    # back rail
    z0 = .112                                                                                 # stretcher boards
    fl, fr, bl, br = (-fx, fy), (fx, fy), (-bx, by), (bx, by)
    for a, b, bow, cusp in ((fl, fr, .095, (0, 0)),          # front board, bowed back toward the wall
                            (bl, fl, 0, (.012, .024)),       # boards along the cants: cusp on the outer edge
                            (fr, br, 0, (.012, .024))):
        mb.prism([(x, y, z0) for x, y in _board(a, b, .046, bow, cusp)], (0, 0, .018), wood, grain=0)
    mb.box((-bx, by - .017, z0), (bx, by + .017, z0 + .018), wood, bev=.002, grain=0)         # back rail
    root = mb.finish(name)

    A8 = pi / 8                                              # 8-sided bell and shaft (facets in F_0068), flats
    lg = mo.MB()                                             # parallel to the blocks. One leg, instanced
    lg.lathe([(0, 0), (.022, 0), (.030, .012), (.031, .034), (.027, .058), (.018, .072), (.018, .086), (0, .086)],
             wood, 24)                                       # bun foot
    lg.box((-.0225, -.0225, .084), (.0225, .0225, .152), wood, bev=.003)                      # stretcher block
    lg.lathe([(0, .15), (.017, .15), (.021, .155), (.021, .162), (.016, .167), (.022, .175), (.027, .188),
              (.027, .198), (.022, .211), (.015, .218), (.020, .224), (.020, .231), (.013, .236), (0, .236)],
             wood, 24)                                       # ring, ball, ring
    lg.lathe([(0, .234), (.0135, .234), (.023, .474), (0, .474)], wood, 8, a0=A8, a1=A8 + tau)   # octagonal shaft
    lg.lathe([(0, .470), (.0375, .470), (.0385, .478), (.0375, .500), (.033, .530), (.026, .556), (.019, .574),
              (.017, .580), (0, .580)], wood, 8, a0=A8, a1=A8 + tau)                          # bell, sharp lower edge
    lg.lathe([(0, .578), (.017, .578), (.024, .586), (.024, .596), (.016, .603), (0, .603)], wood, 24)
    lg.box((-.0225, -.0225, .60), (.0225, .0225, .738), wood, bev=.003)
    first = lg.finish(f'{name}.leg')
    for i, (x, y) in enumerate((fl, fr, bl, br)):
        leg = first if i == 0 else bpy.data.objects.new(f'{name}.leg', first.data)
        leg.parent = root
        leg.location = (x, y, 0)
    return root


# ----------------------------------------------------------------------------- banjo barometer
def barometer(name):
    """Carved oak banjo barometer 0.14 x 0.52: leaf crest, thermometer neck, silvered dial in a brass bezel,
    leaf pendant. Wall prop: back on y = 0, front -Y, origin = centre of the back."""
    wood = M.solid('baro_oak', '#5A4434', 0.45)              # warm red-brown oak; spec #6A4528 rendered terracotta,
    #                                                          this base renders the #6B4E3C of F_0071. No grain at this size
    dial = M.solid('baro_dial', '#BDBDB8', 0.35, 0.7)
    ink = M.solid('baro_ink', '#2A2622', 0.4)
    tick = M.solid('baro_tick', '#5E5C58', 0.4)              # printed scale: faint next to the hands
    plate = M.solid('baro_scale_brass', '#C8A24E', 0.4, 1.0)  # satin: polished brass mirrors the dark hall here
    ivory = M.solid('baro_tube', '#EEE8D8', 0.3)
    mb = mo.MB()
    zc, R = -.095, .07                                       # dial centre, body radius
    half = [(-.26, .004), (-.25, .014), (-.235, .023), (-.218, .02), (-.203, .027), (-.19, .037)]
    half += [(zc + R * sin(radians(a)), R * cos(radians(a))) for a in range(-62, 63, 12)]
    half += [(-.012, .029), (.005, .023), (.14, .023), (.152, .035), (.166, .03), (.18, .037), (.205, .036),
             (.23, .026), (.248, .02), (.26, .004)]
    out = [(hw, 0, z) for z, hw in half] + [(-hw, 0, z) for z, hw in reversed(half)]
    mb.prism(out, (0, -.018, 0), wood)
    mb.at(T(0, -.018, zc) @ RX)                              # raised turned ring round the dial
    mb.lathe([(.058, 0), (.07, 0), (.068, .006), (.063, .009), (.058, .006)], wood, 28)
    mb.lathe([(0, 0), (.0575, 0), (.0575, .003), (0, .003)], dial, 28)              # silvered dial
    mb.lathe([(.0605, .003), (.0605, .007), (.058, .01), (.055, .01), (.053, .007), (.053, .003)], 'brass', 28)
    mb.lathe([(0, .003), (.0175, .003), (.0175, .0042), (0, .0042)], ink, 20)       # small dark boss, 35 mm
    mb.lathe([(.0412, .003), (.0412, .0036), (.040, .0036), (.040, .003)], tick, 28)  # scale circles
    mb.lathe([(.0505, .003), (.0505, .0036), (.0495, .0036), (.0495, .003)], tick, 28)
    mb.lathe([(0, .0042), (.005, .0042), (.004, .009), (0, .0095)], 'brass', 10)
    mb.at()
    for k in range(40):                                      # scale ticks over the upper 300 degrees
        mb.at(T(0, -.018, zc) @ RY(-150 + 300 * k / 39))
        mb.box((-.0004, -.0216, .0412), (.0004, -.0212, .0495 if k % 5 else .0525), tick)
    for deg, ln in ((40, .046), (-115, .034)):               # hands
        mb.at(T(0, -.018, zc) @ RY(deg))
        mb.box((-.0007, -.0062, -.008), (.0007, -.0054, ln), ink)
    mb.at()
    mb.box((-.012, -.0205, .0), (.012, -.018, .15), plate, bev=.0008)                         # thermometer scale
    mb.box((-.003, -.0235, .012), (.003, -.0205, .138), ivory, bev=.001)                      # 24 x 150, ivory tube
    for k in range(11):                                      # graduations either side of the tube
        z = .022 + .0105 * k
        for sx in (-1, 1):
            mb.box((sx * .0045, -.0209, z - .0004), (sx * (.0085 if k % 5 == 0 else .0070), -.0205, z + .0004), ink)
    for z, deg, ln, wd in ((.172, 0, .082, .040), (.170, 32, .062, .028), (.170, -32, .062, .028),   # crest leaves
                           (.168, 180, .05, .03),                                             # bud under them
                           (-.178, 180, .075, .040), (-.176, 150, .05, .026), (-.176, -150, .05, .026)):   # pendant
        mb.at(T(0, -.018, z) @ RY(deg) @ RX)
        mb.leaf(ln, wd, .014, wood, segs=6, serrate=.3, curl=.5)
    mb.at()
    # C-scrolls: a carved roll curling round a boss - two crowning the crest, two at the foot of the neck,
    # two flanking the pendant leaf (centre x, z, radius, start / end angle of the right-hand one; mirrored)
    for cx, cz, r, a0, a1 in ((.017, .236, .013, -30, 200), (.030, .150, .011, 250, 20), (.026, -.200, .014, 120, -110)):
        for sx in (1, -1):
            arc = [(sx * (cx + r * cos(radians(a0 + (a1 - a0) * i / 7))), -.022,
                    cz + r * sin(radians(a0 + (a1 - a0) * i / 7))) for i in range(8)]
            loop(mb, arc, .0048, wood, (0, 1, 0), 5, closed=False)
            mb.at(T(sx * cx, -.018, cz) @ RX)
            mb.dome(r * .6, r * .6, .009, wood, 8, 2)
            mb.at()
    return mb.finish(name)


# ----------------------------------------------------------------------------- round mosaic clock
def clock(name):
    """Inlaid mosaic wall clock, dia 0.21 over the scallops (F_0561: 137 px against the 1.008 m architrave),
    28 mm deep and dished like a plate (rim 18 mm proud of the centre), dark overall: finely scalloped
    near-black walnut rim with pearl dots, twelve small gold-pearl hour marks on the sloping ring, a small
    red-brown and cream 12-point star on the flat centre, small gold hands. Wall prop, origin = centre of the back."""
    wal = M.solid('clock_walnut', '#2A1E18', 0.25)           # satin: at 0.10 the flat ground mirrored the wall grey
    pearl = M.solid('clock_pearl', '#D9CFB4', 0.25)
    gold = M.solid('clock_goldpearl', '#C2AE7A', 0.3, 0.5)
    red = M.solid('clock_red', '#6E3527', 0.35)
    K = RX @ Matrix.Scale(0.105 / 0.1485, 4)                # the profile below is drawn at 0.297 over the scallops
    R0, R1, Z0, Z1 = .066, .113, .014, .034                 # sloping ring: foot radius / lip radius, their heights
    slope = (Z1 - Z0) / (R1 - R0)

    def f(r):                                               # height of the dish at radius r
        return Z0 + slope * (max(r, R0) - R0)

    def RZ(a):
        return Matrix.Rotation(a, 4, 'Z')

    def star(ro, ri, z, a0=0.0):
        return [((ro if i % 2 == 0 else ri) * cos(a0 + tau * i / 24), (ro if i % 2 == 0 else ri) * sin(a0 + tau * i / 24), z)
                for i in range(24)]
    mb = mo.MB()
    mb.at(K)
    mb.lathe([(0, 0), (.128, 0), (.14, .012), (.14, .030), (.132, .040), (.120, .040), (R1, Z1), (R0, Z0), (0, Z0)],
             wal, 48)
    mb.lathe([(.1095, f(.1095) - .0005), (.1095, f(.1095) + .0025), (.104, f(.104) + .0025), (.104, f(.104) - .0005)],
             pearl, 48)
    mb.lathe([(.0665, Z0 - .0005), (.0665, Z0 + .0018), (.0615, Z0 + .0018), (.0615, Z0 - .0005)], gold, 36)
    mb.prism(star(.056, .034, Z0), (0, 0, .0012), red)
    mb.prism(star(.032, .019, Z0 + .0012, tau / 24), (0, 0, .0008), pearl)
    mb.lathe([(0, Z0 + .002), (.013, Z0 + .002), (.013, Z0 + .0032), (0, Z0 + .0032)], wal, 16)
    mb.lathe([(0, Z0 + .0032), (.006, Z0 + .0032), (.005, Z0 + .008), (0, Z0 + .0085)], 'brass', 10)
    for k in range(36):                                                   # scalloped rim
        a = tau * k / 36
        mb.at(K @ T(.139 * cos(a), .139 * sin(a), .020))
        mb.dome(.0085, .0085, .012, wal, 6, 2)
    for k in range(24):                                                   # pearl dots on the rim
        a = tau * (k + .5) / 24
        mb.at(K @ T(.126 * cos(a), .126 * sin(a), .040))
        mb.dome(.005, .005, .003, pearl, 6, 2)
    tilt = Matrix.Rotation(atan2(slope, 1), 4, 'X')
    for k in range(12):                                                   # hour marks lying on the slope
        mb.at(K @ RZ(tau * k / 12) @ T(0, .09, f(.09)) @ tilt)
        mb.box((-.0035, -.009, -.0012), (.0035, .009, .0018), gold)
    for a, ln in ((radians(55), .04), (radians(-62), .056)):               # ten past ten
        mb.at(K @ RZ(a))
        mb.box((-.0016, 0, Z0 + .0055), (.0016, ln, Z0 + .0065), 'brass')
    mb.at()
    return mb.finish(name)


# ----------------------------------------------------------------------------- small fittings
def thermostat(name):
    mb = mo.MB()
    mb.box((-.05, -.025, -.05), (.05, 0, .05), 'plastic_white', bev=.007)
    mb.box((.012, -.0258, .018), (.04, -.0248, .036), M.solid('lcd_grey', '#4A5052', 0.25))
    return mb.finish(name)


def pir(name):
    mb = mo.MB()
    mb.box((-.03, -.045, -.0475), (.03, 0, .0475), 'plastic_white', bev=.009)
    mb.box((-.022, -.0465, -.04), (.022, -.0445, -.002), M.solid('pir_lens', '#E4E4DE', 0.3), bev=.0008)
    return mb.finish(name)


def ceiling_disc(name, dia, h, gap=0.0):
    """White ceiling-mounted disc (Wi-Fi access point / smoke alarm). Origin ceiling, hangs -Z."""
    r = dia / 2
    mb = mo.MB()
    if gap:                                                 # access point: shadow-gap base ring
        mb.lathe([(0, -h), (r * .86, -h), (r * .97, -h * .8), (r, -h * .45), (r, -gap), (r - .008, -gap), (0, -gap)],
                 'plastic_white', 28)
        mb.lathe([(r - .009, -gap), (r - .009, 0)], M.solid('ap_base', '#55585A', 0.5), 28)
    else:                                                   # smoke alarm: grille groove round the side
        mb.lathe([(0, -h), (r * .62, -h), (r * .9, -h * .86), (r, -h * .6), (r, -h * .38), (r * .93, -h * .34),
                  (r * .93, -h * .22), (r, -h * .18), (r, 0), (0, 0)], 'plastic_white', 24)
        mb.at(T(r * .35, 0, -h))
        mb.lathe([(0, -.0015), (.007, -.0015), (.007, 0), (0, 0)], M.solid('pir_lens', '#E4E4DE', 0.3), 10)
        mb.at()
    return mb.finish(name)


def door_stop(name):
    """Brass door stop peg with rubber tip + cabin hook hanging from an eye. Wall prop (on the skirting),
    origin = centre of the back of the peg."""
    mb = mo.MB()
    mb.at(RX)
    mb.lathe([(0, 0), (.011, 0), (.011, .003), (.0065, .006), (.0065, .042), (0, .042)], 'brass', 12)
    mb.lathe([(0, .042), (.008, .042), (.008, .052), (.0055, .055), (0, .055)], 'black_matt', 12)
    mb.at(T(.035, 0, .095) @ RX)
    mb.lathe([(0, 0), (.007, 0), (.006, .002), (0, .0025)], 'brass', 10)
    mb.at()
    loop(mb, [(.035, -.008 + .005 * cos(tau * i / 8), .095 + .005 * sin(tau * i / 8)) for i in range(8)], .0014,
         'brass', (1, 0, 0), 4)
    mb.tube([(.035, -.008, .09), (.035, -.007, .05), (.035, -.007, .012), (.035, -.011, .004), (.035, -.018, .004),
             (.035, -.021, .012)], .0022, 'brass', 5)
    return mb.finish(name)


# ----------------------------------------------------------------------------- gilt mirror, picture frames
# Frame golds are true metals (metallic 1). Their base colours are calibrated on the previews: a metal picks up
# the warm floor and lamps, so the video's olive golds need a base that is greener than the frame looks.
GILT = '#8F8A5C'        # antique olive gold of the mirror and the E / W3 frames (video #796d46 .. #837e4f)
CHAMPAGNE = '#8E8C68'   # satin champagne gold of W1 / W2 / W4 (video #6f644a)
MIRROR_GILT = '#9A8C56'  # the mirror is a little warmer than the picture frames (F_0070 #8C7B4A .. #A08C52)


def mirror(name, w=1.20, h=.85, fw=.095, tilt=0.5):
    """Gilt mirror, outer w x h, frame 95 x 40: plain outer rim, a 60 mm band of diagonal overlapping acanthus
    leaves and ribbon straps in real low relief over a darker ground (they run from the middle of each side
    to the corners, so the pattern is mirrored about every mitre), plain inner bead (F_0070, F_0068).
    It hangs almost flat (F_0071: slim edge, 47 mm overall projection): the outer side shows only a 16 mm rim,
    the back is rebated 18 mm behind it. Wall prop: back on y = 0, front -Y, origin = centre; the top tips
    `tilt` degrees off the wall."""
    gold = M.solid('hall_gilt', MIRROR_GILT, 0.38, 1.0)
    dark = M.solid('hall_gilt_ground', '#4E472C', 0.5, 1.0)
    TILT = T(0, 0, -h / 2) @ Matrix.Rotation(radians(tilt), 4, 'X') @ T(0, 0, h / 2)
    mb = mo.MB()
    mb.at(TILT)
    path = [(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)]
    # (inset from the outer edge, height off the wall), listed from the sight edge outward
    bead = [(fw, 0), (fw, .018), (fw - .002, .025), (fw - .006, .028), (fw - .011, .026), (fw - .013, .021)]
    ground = [(fw - .013, .021), (.017, .021)]
    rim = [(.017, .021), (.016, .033), (.012, .040), (.004, .040), (0, .036), (0, .020), (.018, .020), (.018, 0)]
    for prof, m in ((bead, gold), (ground, dark), (rim, gold)):
        mb.sweep(prof, path, m, closed=True, up=(0, -1, 0))
    d0 = fw - .020                                           # leaf stems stand just outside the inner bead

    def leaf(x, z, dx, dz, ribbon=False):
        mb.at(TILT @ T(x, -.0205, z) @ Matrix.Rotation(atan2(dx, dz), 4, 'Y') @ RX)
        if ribbon:                                           # smooth strap lying over the leaves
            mb.leaf(.066, .015, .016, gold, segs=4, round_=1.0, rib=1.0, base=.6)
        else:
            mb.leaf(.076, .032, .012, gold, segs=6, serrate=.35, curl=.5)
    for k in range(4):                                       # sides: bottom, right, top, left
        tx, tz = ((1, 0), (0, 1), (-1, 0), (0, -1))[k]       # travel along the side
        nx, nz = -tz, tx                                     # toward the glass
        half = (w if k % 2 == 0 else h) / 2
        ex, ez = -nx * (h if k % 2 == 0 else w) / 2, -nz * (h if k % 2 == 0 else w) / 2   # middle of the outer edge
        for sg in (1, -1):                                   # from the middle toward both corners
            s = .012
            while s < half - d0 - .022:                      # leaves sweep outward, the ribbon crosses them inward
                leaf(ex + tx * sg * s + nx * d0, ez + tz * sg * s + nz * d0, sg * tx - nx, sg * tz - nz)
                leaf(ex + tx * sg * (s + .012) + nx * .024, ez + tz * sg * (s + .012) + nz * .024,
                     sg * tx + nx, sg * tz + nz, True)
                s += .024
        cx, cz = ex + tx * (half - d0) + nx * d0, ez + tz * (half - d0) + nz * d0   # corner leaf on the mitre
        leaf(cx, cz, tx - nx, tz - nz)
    hw, hh = w / 2 - fw + .003, h / 2 - fw + .003
    mb.at(TILT)
    mb.face([(-hw, -.016, -hh), (hw, -.016, -hh), (hw, -.016, hh), (-hw, -.016, hh)], 'mirror', hint=(0, -1, 0))
    mb.at()
    return mb.finish(name)


def reframe(ob, w, h, rim=.0005, tilt=1.5):
    """Finish one framed picture built UNTILTED: true metallic olive golds instead of the library frame golds
    (those render orange under the hall downlights), the outer side faces - and the outer `rim` of the face -
    in near-black like the real frames seen obliquely (F_0781), then tip the top off the wall.
    Every picture has its own mesh (unique image), so this stays local."""
    me = ob.data
    for old, name, hx in (('champagne', 'hall_frame_champagne', CHAMPAGNE), ('gold_bronze', 'hall_frame_antique', GILT)):
        om = P.mat(old)
        for i, m in enumerate(me.materials):
            if m == om:
                me.materials[i] = M.solid(name, hx, 0.45, 1.0)
    me.materials.append(P.mat('frame_dark'))
    di = len(me.materials) - 1
    for p in me.polygons:
        c = p.center
        if abs(c.x) > w / 2 - rim or abs(c.z) > h / 2 - rim:
            p.material_index = di
    me.transform(T(0, 0, -h / 2) @ Matrix.Rotation(radians(tilt), 4, 'X') @ T(0, 0, h / 2))


# ----------------------------------------------------------------------------- build
def build(ctx):
    cz = ctx.ceil_z(ROOM)
    xw, xp = -0.65, -0.59                                    # west wall, west pilaster faces

    def put(ob, loc, facing, kind='fit', **kw):
        return ctx.add(P.place(ob, loc, facing=facing), ROOM, kind, **kw)

    # --- console table under the mirror, barometer to its south (front hall, west wall)
    con = console('hallway.console')
    put(con, (xw + 0.02, 4.045, 0), WEST, 'furn', plan_sym='console')         # top y 3.57..4.52, x to -0.27
    put(mirror('hallway.mirror'), (xw, 4.06, 1.585), WEST, 'decor', plan_sym='mirror')
    put(barometer('hallway.barometer'), (xw, 3.12, 1.62), WEST, 'decor')      # 0.27 clear of the mirror (F_0795)

    # --- paintings: (file, outer w, h, style, kwargs, dark outer rim, x, y, z of the frame centre, wall normal)
    #     W3 and E1: wide olive-gold band, thin dark outer rim, dark line at the sight edge (F_0770, F_0076)
    pics = [
        ('w1', 0.78, 0.58, 'champagne', dict(frame_w=.06), 0, xw, 5.38, 1.81, WEST),
        ('w2', 0.86, 0.62, 'champagne', dict(frame_w=.065), 0, xw, 6.73, 1.79, WEST),
        ('w3', 0.565, 0.70, 'bronze_gold', dict(frame_w=.055, slip=('frame_dark', .006)), .004, xw, 8.03, 1.74, WEST),
        ('w4', 0.74, 0.61, 'champagne', dict(frame_w=.04, slip=('frame_dark', .02)), 0, xw, 10.70, 1.805, WEST),
        ('e1', 0.62, 0.82, 'bronze_gold', dict(frame_w=.07, slip=('frame_dark', .006)), .004, 0.65, 3.02, 1.75, EAST),
        ('e2', 0.70, 0.55, 'bronze_gold', dict(frame_w=.065), 0, 0.45, 11.70, 1.825, EAST),
    ]
    for key, w, h, style, kw, rim, x, y, z, nrm in pics:
        pic = P.framed_picture(os.path.join(ART, f'hallway_{key}.jpg'), w, h, style, name=f'hallway.painting.{key}', **kw)
        reframe(pic, w, h, rim or .0005)
        put(pic, (x, y, z), nrm, 'decor')

    # --- round clock over the dining door
    put(clock('hallway.clock'), (-0.056, 12.23, 2.42), NORTH, 'decor')

    # --- electrics and sensors
    put(P.switch_plate(3, name='hallway.switch.front'), (0.65, 3.29, 1.27), EAST)
    put(P.switch_plate(1, name='hallway.switch.rear'), (0.45, 11.30, 1.25), EAST)
    put(P.socket(2, name='hallway.socket.front'), (xw, 3.715, 0.36), WEST)    # behind the console, between its two south legs (F_0236, F_0795)
    put(P.socket(2, name='hallway.socket.lobby'), (xw, 8.36, 0.34), WEST)
    put(P.socket(2, name='hallway.socket.rear'), (xp, 9.53, 0.34), WEST)
    put(thermostat('hallway.thermostat'), (xw, 8.42, 1.42), WEST, lm='dynamic')
    put(pir('hallway.pir'), (xw, 2.03, 2.45), WEST, lm='dynamic')
    ap = ceiling_disc('hallway.wifi_ap', 0.20, 0.035, gap=.004)
    ap.location = (-0.26, 9.36, cz)                          # 30 mm clear of the cornice break round the pilaster (x -0.39)
    ctx.add(ap, ROOM, 'fit', lm='dynamic')
    sm = ceiling_disc('hallway.smoke_alarm', 0.11, 0.04)
    sm.location = (-0.20, 7.88, cz)
    ctx.add(sm, ROOM, 'fit', lm='dynamic')

    # --- brass door stops + cabin hooks on both skirtings, 0.60 north of the inner screen
    for i, (x, nrm) in enumerate(((xw + 0.02, WEST), (0.65 - 0.02, EAST))):
        put(door_stop(f'hallway.door_stop.{i}'), (x, 2.43, 0.06), nrm, lm='dynamic')

    # --- overhead cupboard door over the under-stairs door (carcass is shell), brass D handle
    mb = mo.MB()
    mb.box((0.206, 8.13, 2.327), (0.944, 8.148, 2.594), 'white_gloss', bev=.004)
    # 25 mm bullnose under the door: flush with the door face, rounding back under the carcass (F_0753)
    nose = [(-.007 + .025 * cos(radians(a)), -.025 * sin(radians(a))) for a in (73.7, 60, 45, 30, 15, 0)] + [(0, 0)]
    mb.sweep(nose, [(0.206, 8.13, 2.325), (0.944, 8.13, 2.325)], 'white_gloss')
    ctx.add(mb.finish('hallway.cupboard_door'), ROOM, 'fit')
    put(P.handle_d(.13, finish='brass', name='hallway.cupboard_handle'), (0.575, 8.148, 2.36), (0, 1))

    # --- recessed downlights, one row down the middle of each zone
    spots = [(0.0, 2.95), (0.0, 4.10), (-0.25, 5.38), (-0.25, 6.33), (-0.25, 7.28), (-0.10, 8.32),
             (-0.10, 10.15), (-0.10, 11.40)]
    for i, (x, y) in enumerate(spots):
        lighting.downlight(ctx, ROOM, x, y, watts=70, kelvin=3000, spot_deg=130, name=f'hallway.downlight.{i}')
        ctx.add(P.place(P.downlight(name=f'hallway.downlight_trim.{i}'), (x, y, cz)), ROOM, 'light')

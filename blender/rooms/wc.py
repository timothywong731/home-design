"""Cloakroom WC fittings. Spec: spec/rooms/wc.md.

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --only shell,utility,wc --preview utility,wc \
         --res 540x960 --samples 64 --tag service --save build/service.blend

World coords, metres. Room x 0.60..3.10, y 9.36..10.14, ceiling 2.40. W-basin = x 0.60, W-rad = y 9.36,
W-door = y 10.14 (pocket door to the utility), W-pan = x 3.10 behind the tiled cistern duct (front x 2.90,
ledge z 1.20). Walls, tile dado + steel trim, cornice, window, bulkhead and the pocket door are shell.
"""
import math
import os
import random

import bpy
from mathutils import Matrix, Vector

from lib import interact as IX, lighting, materials as M, mouldings as mo, props as P, shell

ROOM = 'wc'
ART = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'textures', 'art', ROOM)

X0, X1, Y0, Y1 = 0.60, 3.10, 9.36, 10.14
YC = 9.75                   # room centre line
XD, LEDGE = 2.90, 1.20      # duct front, ledge top
DOWN_W = 43                 # per downlight (3 of them): the video shows the WC as bright as the utility (f_0507 / f_0476)
WALL = '#7C7D81'            # dark cool grey: wall / tile code ratio 0.60-0.70 in f_0507, f_0509, f_0522 (shell: #A5A5A8)
UP_W = 4.5                  # ceiling up-fill: the spots put nothing on the ceiling, the video's is near white

CAMERAS = [
    dict(name='pan', pos=(1.6, 9.75, 1.5), look=(3.1, 9.75, 1.15), fov_deg=100, ref='f_0507'),
    dict(name='prints', pos=(1.5, 9.56, 1.5), look=(2.9, 10.0, 1.5), fov_deg=100, ref='f_0509'),
    dict(name='basin', pos=(1.6, 9.75, 1.5), look=(0.6, 9.75, 1.6), fov_deg=100, ref='f_0522'),
    dict(name='basin_low', pos=(1.55, 9.80, 1.5), look=(0.75, 9.72, 0.6), fov_deg=100, ref='f_0518'),
    dict(name='door', pos=(2.2, 9.66, 1.5), look=(1.35, 10.5, 1.2), fov_deg=100, ref='f_0528'),
    dict(name='rad', pos=(1.80, 11.1, 1.5), look=(1.80, 9.36, 1.0), fov_deg=100, ref='f_0499'),
    dict(name='ceiling', pos=(0.95, 9.75, 1.35), look=(2.9, 9.75, 2.25), fov_deg=100, ref='v2:f_0611'),   # 3 downlights
    # interaction checks (--pose 1): into the bowl with seat and lid up, the basin tap running
    dict(name='ix_pan', pos=(2.05, 9.60, 1.25), look=(2.75, 9.76, 0.45), fov_deg=100, ref='f_0507'),
    dict(name='ix_tap', pos=(1.25, 9.95, 1.25), look=(0.72, 9.74, 0.85), fov_deg=100, ref='f_0518'),
]

Z = Vector((0, 0, 1))


# ----------------------------------------------------------------------------- small mesh helpers
def _lathe(mb, origin, axis, profile, mat, segs=16):
    """mb.lathe with its axis moved to `origin` and turned from +Z to `axis`."""
    mb.at(Matrix.Translation(origin) @ Z.rotation_difference(Vector(axis).normalized()).to_matrix().to_4x4())
    mb.lathe(profile, mat, segs)
    mb.at()


def _pipe(mb, path, r, mat, up, n=10, closed=False):
    """Round bar along a path lying in the plane whose normal is `up` (mitred bends)."""
    prof = [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n)) for i in range(n)]
    mb.sweep(prof + prof[:1], path, mat, closed=closed, up=up)


def _ring(mb, c, t, r, wire, mat, n=16, m=6):
    """Torus-like ring of radius r round centre c in the plane normal to t."""
    c, t = Vector(c), Vector(t).normalized()
    a = t.orthogonal().normalized()
    b = t.cross(a)
    _pipe(mb, [c + r * (math.cos(2 * math.pi * i / n) * a + math.sin(2 * math.pi * i / n) * b) for i in range(n)],
          wire, mat, t, n=m, closed=True)


def _loft(name, rings, mat, cap_first=True, cap_last=True):
    """Smooth skin over rings of equal point count (each counter-clockwise seen from +Z, listed bottom -> top)."""
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
    me.set_sharp_from_angle(angle=math.radians(50))
    me.uv_layers.new(name='UVMap')
    me.materials.append(M.mat(mat))
    return bpy.data.objects.new(name, me)


def _d_ring(z, w, length, xw=XD, yc=YC, n=20):
    """D-shaped outline of a wall-hung pan at height z: flat on the plane x = xw, parallel sides for 65 % of the
    projection, broad blunt nose toward -x (superellipse, exponent 2.5). Counter-clockwise seen from above."""
    b, ls, e = w / 2, length * 0.65, 2 / 2.5
    pts = [(xw, yc - b, z), (xw, yc + b, z)]
    for i in range(n + 1):
        th = math.pi / 2 + math.pi * i / n
        c, s = math.cos(th), math.sin(th)
        pts.append((xw - ls - (length - ls) * abs(c) ** e, yc + b * math.copysign(abs(s) ** e, s), z))
    return pts


def _pan():
    """White wall-hung pan 0.36 x 0.53, seat top 0.42: D-shaped bowl, soft-close seat + lid (closed) standing on a
    4 mm shadow gap and overhanging the bowl by 5 mm, two hinge caps on the deck against the wall (f_0507 / f_0508).
    -> (body, seat, lid, bowl): the seat ring and the lid are separate objects that lift about the hinge line PAN_HINGE;
    under them the rim, the bowl and its water are 'wc.pan.bowl'. All are parented to the body."""
    body = _loft('wc.pan', [_d_ring(z, w, l) for z, w, l in (
        (0.085, 0.15, 0.22), (0.095, 0.21, 0.31), (0.130, 0.275, 0.41), (0.190, 0.320, 0.480),
        (0.270, 0.348, 0.515), (0.350, 0.360, 0.530), (0.379, 0.360, 0.530), (0.383, 0.352, 0.522))], 'ceramic_white',
        cap_last=False)
    xb = XD - 0.10                                          # back of the bowl opening: the deck behind it carries the hinges
    bowl = _loft('wc.pan.bowl', [_d_ring(0.383, 0.352, 0.522)] + [_d_ring(z, w, l, xw=xb) for z, w, l in (
        (0.383, 0.272, 0.382), (0.376, 0.256, 0.368), (0.320, 0.228, 0.335), (0.250, 0.170, 0.255),
        (0.200, 0.120, 0.170))], 'ceramic_white', cap_first=False)
    bowl.data.materials.append(M.solid('wc_pan_water', '#C3CDCE', 0.03))
    bowl.data.polygons[-1].material_index = 1               # the cap of the last ring = the water surface
    xs = XD - 0.042                                         # the seat stops short of the wall, behind it the hinges
    outer = lambda z, w, l: _d_ring(z, w, l - 0.042, xw=xs)
    hole = lambda z: _d_ring(z, 0.232, 0.365, xw=xs - 0.070)
    seat = _loft('wc.pan.seat', [hole(0.3875), outer(0.387, 0.350, 0.520), outer(0.3875, 0.370, 0.535),
                                 outer(0.4005, 0.370, 0.535), outer(0.4015, 0.360, 0.530), hole(0.4015), hole(0.3875)],
                 'ceramic_white', cap_first=False, cap_last=False)
    lid = _loft('wc.pan.lid', [outer(z, w, l) for z, w, l in (
        (0.4040, 0.360, 0.530), (0.4050, 0.370, 0.535), (0.417, 0.370, 0.535), (0.421, 0.362, 0.531),
        (0.423, 0.336, 0.512))], 'ceramic_white')
    mb = mo.MB()
    for sy in (-1, 1):
        mb.box((xs - 0.004, YC + sy * 0.085 - 0.022, 0.383), (XD - 0.004, YC + sy * 0.085 + 0.022, 0.409),
               'ceramic_white', bev=0.006)
    caps = mb.finish('wc.pan.hinges', sharp_deg=50)
    bowl.parent = seat.parent = lid.parent = caps.parent = body
    return body, seat, lid, bowl


PAN_HINGE = (XD - 0.032, YC, 0.400)     # seat / lid axis (along y) through the hinge caps; 90 deg stands them 9 mm off the duct


def _basin_outline(xa, xb, ya, yb, z, inset=0.0, r=0.012, n=4):
    """Plan outline of the basin, counter-clockwise: square against the wall x = xa, the two front corners rounded
    with radius r; `inset` moves all four sides inward first."""
    xa, xb, ya, yb = xa + inset, xb - inset, ya + inset, yb - inset
    pts = [(xa, yb, z), (xa, ya, z)]
    for cy, a0 in ((ya + r, -math.pi / 2), (yb - r, 0.0)):
        for i in range(n + 1):
            a = a0 + math.pi / 2 * i / n
            pts.append((xb - r + r * math.cos(a), cy + r * math.sin(a), z))
    return pts


def _basin():
    """Wall-hung rectangular basin 0.60 x 0.45 x 0.16, rim 0.86 (f_0518 / f_0520): a crisp box - vertical sides,
    R 12 corners, flat underside with a 5 mm arris, thin rim, bowl with rounded corners - and its fittings: tap
    ledge, round monobloc mixer with a curved spout and a thin loop lever, click-clack waste, overflow ring,
    bottle trap. -> (body, tap, lever): the fittings, the mixer (body + spout) and its lever are separate objects
    parented to the ceramic body; the lever lifts about the y axis through TAP_PIVOT, the spout ends at TAP_OUTLET."""
    xa, xb, ya, yb, z0, zt = X0, X0 + 0.45, YC - 0.30, YC + 0.30, 0.70, 0.86
    body = _loft('wc.basin', [_basin_outline(xa, xb, ya, yb, z, i, r) for i, z, r in (
        (0.005, z0, 0.008), (0.0, z0 + 0.005, 0.012), (0.0, zt - 0.004, 0.012), (0.0012, zt - 0.0012, 0.011),
        (0.004, zt, 0.009), (0.015, zt, 0.012), (0.018, zt - 0.002, 0.014), (0.020, zt - 0.008, 0.018),
        (0.030, z0 + 0.075, 0.030), (0.040, z0 + 0.058, 0.035), (0.055, z0 + 0.054, 0.030))], 'ceramic_white')
    mb = mo.MB()
    c, ch = 'ceramic_white', 'chrome'
    xl = xa + 0.105
    mb.box((xa + 0.004, ya + 0.008, z0 + 0.02), (xl, yb - 0.008, zt - 0.002), c, bev=0.002)       # tap ledge
    _lathe(mb, (xa + 0.275, YC, z0 + 0.054), Z, [(0.024, 0), (0.024, 0.003), (0.018, 0.003), (0.012, 0.001), (0, 0.001)], ch, 20)
    _lathe(mb, (xl, YC, zt - 0.045), (1, 0, 0), [(0.011, 0), (0.011, 0.002), (0.007, 0.002), (0.007, 0)], ch, 16)
    # bottle trap under the bowl centre and the waste pipe back to the wall
    px = xa + 0.275
    _lathe(mb, (px, YC, 0.60), Z, [(0.016, 0), (0.016, 0.101)], ch, 16)
    _lathe(mb, (px, YC, 0.50), Z, [(0, 0), (0.024, 0), (0.028, 0.006), (0.028, 0.094), (0.022, 0.10), (0.016, 0.10)], ch, 16)
    _lathe(mb, (xa, YC, 0.565), (1, 0, 0), [(0.030, 0), (0.030, 0.004), (0.016, 0.005), (0.016, 0.25)], ch, 16)
    fittings = mb.finish('wc.basin.fittings', sharp_deg=50)
    # mixer: round body dia 45 with a domed cap, spout curving out and down, thin loop lever rising toward the room
    tx, tz = xa + 0.055, zt - 0.002
    mb = mo.MB()
    _lathe(mb, (tx, YC, tz), Z, [(0, 0), (0.027, 0), (0.027, 0.004), (0.0225, 0.008), (0.0225, 0.104), (0.0205, 0.116),
                                 (0.013, 0.125), (0, 0.128)], ch, 24)
    _pipe(mb, [(tx + 0.010, YC, tz + 0.062), (tx + 0.060, YC, tz + 0.076), (tx + 0.098, YC, tz + 0.070),
               (tx + 0.118, YC, tz + 0.050)], 0.012, ch, (0, 1, 0), n=12)
    tap = mb.finish('wc.basin.tap', sharp_deg=50)
    mb = mo.MB()
    mb.at(Matrix.Translation(TAP_PIVOT) @ Matrix.Rotation(math.radians(-16), 4, 'Y'))
    _pipe(mb, [(-0.012, -0.013, 0), (0.105, -0.011, 0), (0.122, -0.005, 0), (0.122, 0.005, 0), (0.105, 0.011, 0),
               (-0.012, 0.013, 0)], 0.0035, ch, (0, 0, 1), n=8, closed=True)
    mb.at()
    lever = mb.finish('wc.basin.lever', sharp_deg=50)
    fittings.parent = tap.parent = lever.parent = body
    return body, tap, lever


TAP_PIVOT = (X0 + 0.055, YC, 0.858 + 0.122)         # top of the mixer body, where the loop lever is hinged
TAP_OUTLET = (X0 + 0.055 + 0.121, YC, 0.858 + 0.046)   # end of the spout; the bowl floor is at 0.754


def _soap_dish(x, y, z):
    """Shallow frosted-glass dish dia 110 sitting in a chrome band ring on a short arm, on the wall x = const, room
    toward +x (v2 f_0625); z = top of the ring."""
    mb = mo.MB()
    r, xc = 0.055, x + 0.008 + 0.055
    _lathe(mb, (x, y, z - 0.012), (1, 0, 0), [(0.016, 0), (0.016, 0.004), (0.006, 0.005), (0.006, 0.012)], 'chrome', 16)
    _lathe(mb, (xc, y, z - 0.018), Z, [(r + 0.0015, 0), (r + 0.0015, 0.018), (r - 0.0005, 0.018), (r - 0.0005, 0.002),
                                       (r + 0.0015, 0)], 'chrome', 32)                               # band ring
    dish = P.two_sided(M.solid('wc_soap_glass', '#DCE3E0', 0.45))                                     # frosted: opaque enough to read
    _lathe(mb, (xc, y, z - 0.026), Z, [(0, 0), (0.030, 0), (0.046, 0.010), (r - 0.001, 0.026), (r - 0.004, 0.026),
                                       (0.044, 0.013), (0.028, 0.004), (0, 0.004)], dish, 32)
    return mb.finish('wc.soap_dish', sharp_deg=50)


def _flush_plate():
    """Polished-chrome dual-flush plate 220 x 160 on the duct front, 10 mm proud with rounded corners: two push
    panels either side of a dark 4 mm gap (f_0507)."""
    mb = mo.MB()
    ch = 'chrome'                                           # mirror-polished (f_0507): library chrome, roughness 0.05

    def slab(ya, yb, za, zb, xa, xb, r):                    # rounded rectangle in the wall plane, x from xa to xb
        pts = [(xa, cy + r * math.cos(a0 + math.pi / 2 * i / 3), cz + r * math.sin(a0 + math.pi / 2 * i / 3))
               for cy, cz, a0 in ((yb - r, zb - r, 0), (ya + r, zb - r, math.pi / 2), (ya + r, za + r, math.pi),
                                  (yb - r, za + r, 1.5 * math.pi)) for i in range(4)]
        mb.prism(pts, (xb - xa, 0, 0), ch)

    slab(YC - 0.11, YC + 0.11, 0.92, 1.08, XD, XD - 0.010, 0.010)
    for ya, yb in ((YC - 0.101, YC - 0.002), (YC + 0.002, YC + 0.101)):
        slab(ya, yb, 0.929, 1.071, XD - 0.010, XD - 0.013, 0.006)
    mb.box((XD - 0.0105, YC - 0.002, 0.932), (XD - 0.010, YC + 0.002, 1.068), 'black_matt')          # the gap
    return mb.finish('wc.flush_plate', sharp_deg=50)


def _roll_holder(xc=2.55, z=0.73):
    """Black cast-iron Victorian roll holder on W-rad (f_0507 / f_0508): open frame - back bar on the wall, two
    flat arms on scroll brackets, rod across the arm ends - carrying one white roll."""
    mb = mo.MB()
    k = 'cast_iron'
    mb.box((xc - 0.10, Y0, z - 0.016), (xc + 0.10, Y0 + 0.006, z + 0.012), k, bev=0.0015)           # back bar
    yr = Y0 + 0.108                                                                                 # rod axis
    for sx in (-1, 1):
        x = xc + sx * 0.094
        mb.box((x - 0.006, Y0, z - 0.004), (x + 0.006, Y0 + 0.118, z + 0.004), k, bev=0.0015)       # arm
        arc = [(x, Y0 + 0.004 + 0.075 * math.cos(a), z + 0.075 * math.sin(a))
               for a in (math.radians(-90 + 90 * i / 8) for i in range(9))]
        _pipe(mb, arc, 0.004, k, (1, 0, 0), n=6)                                                    # quadrant bracket
        mb.box((x - 0.005, Y0, z - 0.080), (x + 0.005, Y0 + 0.005, z), k)                           # wall strap
        _ring(mb, (x, Y0 + 0.022, z - 0.024), (1, 0, 0), 0.016, 0.003, k, n=14, m=5)                # scroll eyes
        _ring(mb, (x, Y0 + 0.046, z - 0.014), (1, 0, 0), 0.009, 0.0025, k, n=12, m=5)
    _lathe(mb, (xc - 0.098, yr, z), (1, 0, 0), [(0, 0), (0.005, 0), (0.005, 0.196), (0, 0.196)], k, 10)
    _lathe(mb, (xc - 0.05, yr, z - 0.014), (1, 0, 0),                                               # roll hanging on the rod
           [(0.019, 0), (0.053, 0), (0.053, 0.10), (0.019, 0.10), (0.019, 0)], M.paint('#F4F3EF', 0.9), 24)
    return mb.finish('wc.roll_holder', sharp_deg=50)


def _brush(x, y):
    """Brushed-steel toilet brush holder dia 90 x 250 with a steel handle."""
    mb = mo.MB()
    _lathe(mb, (x, y, 0), Z, [(0, 0), (0.043, 0), (0.045, 0.003), (0.045, 0.247), (0.043, 0.25), (0.012, 0.25),
                              (0.008, 0.256), (0.008, 0.395), (0.0, 0.40)], 'steel_brushed', 20)
    return mb.finish('wc.brush', sharp_deg=50)


def _fan(yc=9.945, zc=1.90):
    """White square extractor fan 170 x 170 with a circular concentric-louvre grille, on the wall x = X1."""
    mb = mo.MB()
    w = 'plastic_white'
    mb.box((X1 - 0.034, yc - 0.085, zc - 0.085), (X1, yc + 0.085, zc + 0.085), w, bev=0.006)
    for r in (0.022, 0.039, 0.056, 0.072):
        _ring(mb, (X1 - 0.035, yc, zc), (1, 0, 0), r, 0.0045, w, n=28, m=6)
    _lathe(mb, (X1 - 0.034, yc, zc), (-1, 0, 0), [(0.011, 0), (0.011, 0.005), (0, 0.006)], w, 16)
    return mb.finish('wc.fan', sharp_deg=50)


def _roll_pole(x, y, z):
    """Turned antique-brass spare-roll pole: round base dia 140, pole 330."""
    mb = mo.MB()
    _lathe(mb, (x, y, z), Z, [(0, 0), (0.068, 0), (0.070, 0.004), (0.070, 0.012), (0.062, 0.020), (0.022, 0.025),
                              (0.013, 0.034), (0.012, 0.322), (0.009, 0.330), (0, 0.330)], 'bronze_antique', 24)
    return mb.finish('wc.roll_pole', sharp_deg=50)


def _wall_frame(p, dvec):
    """Matrix putting local Z on the W-basin wall normal (+X), local Y on dvec (a unit vector in the wall plane)."""
    zc, yc_ = Vector((1, 0, 0)), Vector(dvec).normalized()
    xc = yc_.cross(zc)
    m = Matrix((xc, yc_, zc)).transposed().to_4x4()
    m.translation = p
    return m


def _mirror(yc=YC, zc=1.66, w=0.56, h=0.84, fw=0.06):
    """Gilt mirror on W-basin: swept ogee frame in bright gold, beaded sight edge, acanthus cartouches at the
    four corners, a small leaf ornament at each side's centre, bevelled plate. Outer size w x h."""
    mb = mo.MB()
    g, x = M.solid('wc_mirror_gilt', '#D9CB86', 0.28, 1.0), X0
    g2 = P.two_sided(g)                                     # the leaves are open surfaces: no back-face culling
    ya, yb, za, zb = yc - w / 2, yc + w / 2, zc - h / 2, zc + h / 2
    prof = [(fw, 0.004), (fw, 0.014), (fw - 0.004, 0.019), (fw - 0.009, 0.015), (fw - 0.012, 0.016), (0.044, 0.026),
            (0.034, 0.032), (0.024, 0.034), (0.015, 0.032), (0.010, 0.027), (0.007, 0.029), (0.003, 0.027),
            (0.0, 0.021), (0.0, 0.0)]
    mb.sweep(prof, [(x, ya, za), (x, yb, za), (x, yb, zb), (x, ya, zb)], g, closed=True, up=(1, 0, 0))
    # plate: flat centre + 12 mm bevel border falling to the sight edge
    s, bv = fw - 0.001, 0.012
    o = [(ya + s, za + s), (yb - s, za + s), (yb - s, zb - s), (ya + s, zb - s)]
    i = [(ya + s + bv, za + s + bv), (yb - s - bv, za + s + bv), (yb - s - bv, zb - s - bv), (ya + s + bv, zb - s - bv)]
    mb.face([(x + 0.009, y, z) for y, z in i], 'mirror', hint=(1, 0, 0))
    for k in range(4):
        (y0, z0), (y1, z1), (y2, z2), (y3, z3) = o[k], o[(k + 1) % 4], i[(k + 1) % 4], i[k]
        mb.face([(x + 0.005, y0, z0), (x + 0.005, y1, z1), (x + 0.009, y2, z2), (x + 0.009, y3, z3)], 'mirror', hint=(1, 0, 0))
    # beads along the sight edge
    e, pitch = fw - 0.004, 0.011
    for (p0, p1) in (((ya + e, za + e), (yb - e, za + e)), ((yb - e, za + e), (yb - e, zb - e)),
                     ((yb - e, zb - e), (ya + e, zb - e)), ((ya + e, zb - e), (ya + e, za + e))):
        n = int(round(math.hypot(p1[0] - p0[0], p1[1] - p0[1]) / pitch))
        for k in range(n):
            t = (k + 0.5) / n
            mb.at(_wall_frame((x + 0.0175, p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t), (0, 0, 1)))
            mb.dome(0.0046, 0.0046, 0.0036, g, segs=6, rings=2)
    # corner cartouches and side-centre ornaments
    hl = 0.030

    def leaf(y, z, d, length, width):
        mb.at(_wall_frame((x + hl, y, z), d))
        mb.leaf(length, width, 0.011, g2, segs=6, serrate=0.28, curl=0.6)

    def boss(y, z, r):
        mb.at(_wall_frame((x + hl, y, z), (0, 0, 1)))
        mb.dome(r, r, r * 0.8, g, segs=10, rings=3)

    for sy in (-1, 1):
        for sz in (-1, 1):
            cy, cz_ = yc + sy * (w / 2 - 0.030), zc + sz * (h / 2 - 0.030)
            leaf(cy, cz_, (0, sy, sz), 0.055, 0.050)
            leaf(cy, cz_, (0, -sy, 0.12 * sz), 0.095, 0.046)
            leaf(cy, cz_, (0, 0.12 * sy, -sz), 0.095, 0.046)
            boss(cy, cz_, 0.012)
    for cy, cz_, d in ((yc, za + 0.028, (0, 1, 0)), (yc, zb - 0.028, (0, 1, 0)),
                       (ya + 0.028, zc, (0, 0, 1)), (yb - 0.028, zc, (0, 0, 1))):
        leaf(cy, cz_, d, 0.050, 0.036)
        leaf(cy, cz_, tuple(-c for c in d), 0.050, 0.036)
        boss(cy, cz_, 0.009)
    mb.at()
    return mb.finish('wc.mirror', sharp_deg=50)


def _plant(x, y, z, seed=7):
    """Ledge plant (hr_0507): ribbed pale-gold planter dia 160 x 150 holding sparse dried eucalyptus-type stems -
    thin stalks carrying small dull grey-green leaves, cupped and twisted. Most stems arch over the rim and hang
    down the pot, three stand up and nod over about 0.2 m above the rim."""
    mb = mo.MB()
    pot = M.solid('wc_planter_gold', '#A39B6E', 0.42, 0.7)
    leafm = P.two_sided(M.solid('wc_leaf_dry', '#6E735E', 0.8))
    stalk = M.solid('wc_stalk_dry', '#6B6A52', 0.8)
    rb, rt, hp = 0.066, 0.080, 0.15
    _lathe(mb, (x, y, z), Z, [(0, 0), (rb, 0), (rt, hp), (rt - 0.006, hp), (rt - 0.011, hp - 0.02)], pot, 28)
    _lathe(mb, (x, y, z), Z, [(rt - 0.011, hp - 0.02), (0, hp - 0.02)], P.mat('soil'), 28)
    for k in range(28):
        a = 2 * math.pi * k / 28
        c, sn = math.cos(a), math.sin(a)
        _pipe(mb, [(x + rb * c, y + rb * sn, z + 0.004), (x + rt * c, y + rt * sn, z + hp - 0.004)], 0.0048, pot,
              (-sn, c, 0), n=5)
    rnd = random.Random(seed)
    clamp = lambda q: Vector((min(q.x, X1 - 0.012), q.y, q.z))            # stay off the wall / window behind
    n = 9
    for k in range(n):
        az = 2 * math.pi * (k + rnd.uniform(-0.3, 0.3)) / n
        d = Vector((math.cos(az), math.sin(az), 0))
        side = Vector((-d.y, d.x, 0))
        if k % 3 == 1:                                                    # upright, tip nodding over
            reach, top, droop = rnd.uniform(0.05, 0.09), rnd.uniform(0.19, 0.25), rnd.uniform(0.02, 0.05)
        else:                                                             # up over the rim, then hanging down the pot
            reach, top = rnd.uniform(0.10, 0.14), rnd.uniform(0.045, 0.085)
            droop = top + rnd.uniform(0.03, 0.10)
        b0 = Vector((x, y, z + hp - 0.02)) + d * 0.025
        b1 = b0 + d * (reach * 0.15) + Z * (top * 0.8)
        b2 = b0 + d * (reach * 0.75) + Z * (top + 0.02)
        b3 = b0 + d * reach + Z * (top - droop)
        bez = lambda t: (1 - t) ** 3 * b0 + 3 * (1 - t) ** 2 * t * b1 + 3 * (1 - t) * t ** 2 * b2 + t ** 3 * b3
        _pipe(mb, [clamp(bez(j / 7)) for j in range(8)], 0.0013, stalk, side, n=5)
        nl = rnd.randint(6, 9)
        for i in range(nl):                                               # leaves alternate left / right up the stalk
            t = 0.28 + 0.72 * (i + rnd.uniform(0, 0.5)) / nl
            base, tg = bez(t), (bez(min(1.0, t + 0.02)) - bez(t - 0.02)).normalized()
            out = (side * (1 if i % 2 else -1) * rnd.uniform(0.5, 1.0) + d * rnd.uniform(-0.2, 0.5)).normalized()
            dirn = (tg * 0.6 + out * 0.8 - Z * rnd.uniform(0.3, 1.1)).normalized()      # dried: they hang
            length, width = rnd.uniform(0.045, 0.072), rnd.uniform(0.014, 0.022)
            wv = dirn.cross(Z)
            wv = (wv if wv.length > 0.05 else side).normalized()
            nv = wv.cross(dirn)
            twist, cup = rnd.uniform(-1.2, 1.2), rnd.uniform(0.25, 0.5)
            rows = []
            for j in range(5):
                u = j / 4
                c = base + dirn * (length * u) - Z * (0.25 * length * u * u)
                hw = 0.5 * width * max(0.12, math.sin(math.pi * (0.08 + 0.84 * u)) ** 0.8)
                w2 = wv * math.cos(twist * u) + nv * math.sin(twist * u)
                n2 = w2.cross(dirn)
                rows.append([clamp(q) for q in (c - w2 * hw + n2 * (cup * hw), c, c + w2 * hw + n2 * (cup * hw))])
            for (l0, c0, r0), (l1, c1, r1) in zip(rows, rows[1:]):
                mb.face([l0, c0, c1, l1], leafm)
                mb.face([c0, r0, r1, c1], leafm)
    return mb.finish('wc.plant', sharp_deg=50)


# ----------------------------------------------------------------------------- build
def build(ctx):
    cz = ctx.ceil_z(ROOM)
    art = lambda f: os.path.join(ART, f)

    # ---- sanitaryware. Interaction (blender/INTERACT.md): lid and seat ring lift 90 deg (the duct front stops
    #      them at vertical), the basin lever lifts and runs a stream from the spout to the bowl floor.
    #      The room's light switch is on the utility side of the pocket door (rooms/utility.py).
    #      Lid, then seat (spec W2): the seat `needs` the lid - opening the seat opens the lid first, closing the
    #      lid closes the seat first.
    pan, seat, lid, bowl = _pan()
    hinge = dict(p=PAN_HINGE, a=(0, 1, 0), deg=90)
    IX.tag(lid, 'hinge', label='Toilet lid', **hinge)
    IX.tag(seat, 'hinge', label='Toilet seat', needs='wc.pan.lid', **hinge)
    ctx.add(pan, ROOM, 'fit', plan_sym='wc')
    ctx.add(_flush_plate(), ROOM, 'fit')
    basin, tap, lever = _basin()
    water = P.place(P.water_stream(TAP_OUTLET[2] - 0.754, splash=0.05, name='wc.basin.water'), TAP_OUTLET)
    IX.tag(tap, 'trigger', g='wc.basin.tap', label='Tap')
    IX.tag(lever, 'hinge', g='wc.basin.tap', label='Tap', p=TAP_PIVOT, a=(0, 1, 0), deg=-20)
    IX.tag(water, 'show', g='wc.basin.tap', label='Tap', when=1, fx='water')
    ctx.add(basin, ROOM, 'fit', plan_sym='basin')
    ctx.add(water, ROOM, 'fit', lm='dynamic')
    for o in (seat, lid, bowl, lever):           # after the roots' ctx.add, which resets its children
        o['lm'] = 'dynamic'
    ctx.add(_soap_dish(X0, YC - 0.18, 0.86 + 0.16), ROOM, 'fit', lm='dynamic')    # W3: 0.18 left of the tap, 0.16 over the rim
    ctx.add(_roll_holder(z=0.66), ROOM, 'fit', lm='dynamic')                      # W4: beside the pan, z 0.65 (v2 f_0605)
    ctx.add(_brush(2.82, 9.48), ROOM, 'fit', lm='dynamic')
    ctx.add(_fan(), ROOM, 'fit')

    # ---- anthracite towel rail, 0.40 x 1.20, bars 8 / 7 / 5 from the bottom up
    rail = P.radiator_towel_rail(0.4, 1.2, groups=(8, 7, 5), mat='anthracite', name='wc.towel_rail')
    ctx.add(P.place(rail, (1.80, Y0, 0.18), facing=(0, 1)), ROOM, 'fit', plan_sym='towel_rail')

    # ---- gilt mirror over the basin
    ctx.add(_mirror(), ROOM, 'decor', plan_sym='mirror', lm='dynamic')

    # ---- pictures (rectified crops incl. their mounts; print 4 is a generated generic sketch)
    for name, pic, loc, n in (
            ('wc.print.1', P.framed_picture(art('print1_arched_door.jpg'), 0.36, 0.54, 'walnut_gold', frame_w=0.028),
             (1.80, Y0, 1.79), (0, 1)),
            ('wc.print.2', P.framed_picture(art('print2_coast.jpg'), 0.50, 0.42, 'silver_green', frame_w=0.045),
             (2.55, Y1, 1.65), (0, -1)),
            ('wc.print.3', P.framed_picture(art('print3_red_door.jpg'), 0.31, 0.34, 'dark_gold_slip', frame_w=0.025),
             (X1, 9.915, 1.60), (-1, 0)),
            ('wc.print.4', P.framed_picture(art('print4_sketch.jpg'), 0.30, 0.42, 'gilt_thin', frame_w=0.020,
                                            depth=0.020, mount=0.06), (1.10, Y1, 1.63), (0, -1))):
        pic.name = name
        ctx.add(P.place(pic, loc, facing=n), ROOM, 'decor')
    # print 4 (generic street wash sketch, generated - the original is illegible in the footage) hangs in a thin
    # flat pale green-gold frame (f_0528 / t_531): the metallic golds of the frame styles render orange under the
    # lamps, so its (own, unshared) mesh gets a satin paint-like gold instead
    pic.data = pic.data.copy()
    gold, pale = P.mat('gold_bright'), M.solid('wc_frame_pale_gold', '#989367', 0.45)
    for i, m in enumerate(pic.data.materials):
        if m == gold:
            pic.data.materials[i] = pale

    # ---- ledge ornaments: plant in a pale-gold planter in front of the window, spare-roll pole
    ctx.add(_plant(3.00, 9.63, LEDGE), ROOM, 'decor', plan_sym='plant')
    ctx.add(_roll_pole(3.00, 10.04, LEDGE), ROOM, 'decor')

    # ---- walls: the owner's "dark grey colour wall" (the shell paints #A5A5A8, which reads mid-light grey)
    shell.repaint(ROOM, '#A5A5A8', WALL)

    # ---- lighting: 3 downlights on the centre line (ground_corrections W1, v2 f_0608-f_0611) + an invisible up-fill
    #      for the ceiling (the spots only shine down; in the video the ceiling is near white from spill and bounce).
    #      They are switched from the utility side of the pocket door (utility.switch.light).
    for i, x in enumerate((1.05, 1.85, 2.65)):
        lighting.downlight(ctx, ROOM, x, YC, watts=DOWN_W, kelvin=3000, spot_deg=135, name=f'wc.downlight.{i}')
        ctx.add(P.place(P.downlight(name=f'wc.downlight_trim.{i}'), (x, YC, cz)), ROOM, 'light')
    up = lighting.strip(ctx, ROOM, (0.8, YC, cz - 0.25), (2.85, YC, cz - 0.25), watts_per_m=UP_W / 2.05, kelvin=3000,
                        width=0.40, direction=(0, 0, 1), name='wc.upfill')
    up.visible_camera = up.visible_glossy = False

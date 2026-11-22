"""Green bedroom (first-floor front): spec/rooms/green_bedroom.md, reconciled to spec/house.json.

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --levels 1 --only shell,green_bedroom --preview green_bedroom --res 540x960 --samples 64 --tag green_bedroom
    (--pose 1 --tag green_bedroom1 for the open state)

Room x -0.65..4.30, y 0.99..4.83, bay x 1.11..3.85 / y 0.14..0.99, floor Z 3.42, ceiling 2.77 above it (round 3;
`_measure` re-reads the frame from house.json at build time, so the fittings follow the shell).
W wall (x -0.65) dark green TV wall, E wall (x 4.30) bed wall, rear wall (y 4.83) two doors + big wardrobe.
Heights below are above the room floor (FZ is added on placement).
Helpers: green_bedroom_furn (furniture), green_bedroom_tex (generated fabric / inlay maps, plain Python).
"""
import os
import sys
import math
import random
from math import sin, cos, pi, radians, degrees
import bpy
from mathutils import Matrix, Vector
from lib import interact as IX, lighting, materials as M, mouldings as mo, props as P, shell

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:                       # build.py loads this file by path: make the helper importable
    sys.path.insert(0, _HERE)
import green_bedroom_furn as F
from green_bedroom_furn import Piece, Tr, Rx, Rz, tex, solid

ROOM = 'green_bedroom'
FZ = F.FZ
X0, X1, Y0, Y1 = -0.65, 4.30, 0.99, 4.83         # main room inside faces
BX0, BX1, BY0 = 1.11, 3.85, 0.14                 # bay inside faces
BC = 2.48                                        # bay and w_green_bay axis
CEIL = 2.77                                      # ceiling above the floor (cornice underside 2.67)
PIER, BUREAU = 0.67, 0.645                       # centres of the front-wall pier (sconce) and of the bureau
DARK_WALL = '#5A716B'                           # TV wall: #3F6B5C (spec) and #3D5F56 rendered emerald (23,64,48) under AgX
E = FZ + 1.5

CAMERAS = [
    dict(name='bed', pos=(0.6, 2.6, E), look=(4.3, 2.3, FZ + 0.9), fov_deg=100, ref='v3:f_0520'),
    dict(name='ne', pos=(0.8, 2.0, E), look=(4.0, 4.4, FZ + 1.1), fov_deg=100, ref='v3:f_0522'),
    dict(name='rear', pos=(1.3, 2.3, E), look=(1.3, 4.83, FZ + 1.2), fov_deg=100, ref='v3:f_0524'),
    dict(name='front', pos=(1.6, 3.7, E), look=(1.0, 0.5, FZ + 1.3), fov_deg=100, ref='v4:f_0015'),
    dict(name='tvwall', pos=(2.2, 2.5, E), look=(-0.65, 2.5, FZ + 1.1), fov_deg=100, ref='v3:f_0612'),
    dict(name='bay', pos=(1.5, 2.4, E), look=(3.0, 0.3, FZ + 1.2), fov_deg=100, ref='v3:f_0636'),
    dict(name='nib', pos=(2.3, 2.2, E), look=(4.1, 0.75, FZ + 1.15), fov_deg=100, ref='v4:f_0001'),
    dict(name='pier', pos=(1.3, 2.9, E), look=(0.6, 0.99, FZ + 1.2), fov_deg=100, ref='v4:f_0011'),
    dict(name='mirror', pos=(1.5, 3.4, E), look=(-0.65, 4.2, FZ + 1.2), fov_deg=100, ref='v3:f_0532'),
    # interaction checks: render with --pose 0 and --pose 1
    dict(name='ix_bureau', pos=(1.25, 2.35, FZ + 1.45), look=(0.7, 1.1, FZ + 0.75), fov_deg=85, ref='v3:f_0606'),
    dict(name='ix_small', pos=(2.5, 3.1, FZ + 1.5), look=(4.1, 4.2, FZ + 1.0), fov_deg=95, ref='v3:f_0556'),
    dict(name='ix_night', pos=(3.0, 3.5, FZ + 1.35), look=(4.15, 3.34, FZ + 0.6), fov_deg=80, ref='v3:f_0576'),
    dict(name='ix_dresser', pos=(1.2, 1.9, FZ + 1.5), look=(-0.5, 2.6, FZ + 0.6), fov_deg=95, ref='v3:f_0618'),
    dict(name='ix_chest', pos=(0.9, 3.5, FZ + 1.5), look=(2.0, 2.3, FZ + 0.4), fov_deg=85, ref='v3:f_0598'),
    dict(name='ix_bay', pos=(2.15, 1.4, FZ + 1.3), look=(3.3, 0.85, FZ + 0.3), fov_deg=95, ref='v3:f_0670'),
    dict(name='door1', pos=(1.5, 3.0, E), look=(-0.3, 4.83, FZ + 1.15), fov_deg=90, ref='v4:f_0206'),
    dict(name='pine',pos=(3.55, 1.75, FZ + 1.35), look=(4.3, 1.24, FZ + 1.15), fov_deg=60, ref='v3:f_0648'),
]

_ONLY = os.environ.get('GB_CAMS')                 # ponytail: scratch filter for iterating (GB_CAMS=pine,ix_bay)
if _ONLY:
    CAMERAS = [c for c in CAMERAS if c['name'] in _ONLY.split(',')]

ROSE_D = 0.040                                   # rose relief round its centre boss (0.032 at the boss, 0.035-0.046 at r 0.04-0.06)
W_DOWN, W_CHAND, W_SCONCE, W_PINE = 50, 90, 10, 14      # radiometric watts per emitter (see lighting README)


def _measure(ctx):
    """Room frame from house.json (round 3 moved the bay 0.05 west and dropped the ceiling 0.08)."""
    global X0, X1, Y0, Y1, BX0, BX1, BY0, BC, CEIL, PIER, BUREAU
    xs, ys = zip(*ctx.room_poly(ROOM))
    bx, by = zip(*ctx.feature('green_bay')['polygon'])
    X0, X1, Y1 = min(xs), max(xs), max(ys)
    BX0, BX1, BY0, Y0 = min(bx), max(bx), min(by), max(by)
    BC = (BX0 + BX1) / 2
    CEIL = ctx.ceil_z(ROOM) - FZ
    c, _, _, hw, _, _ = _reveal(ctx, 'w_green_west')
    PIER = (c.x + hw + BX0) / 2                  # pier between the west window reveal (0.23) and the bay (1.11)
    BUREAU = BX0 - 0.085 - 0.38                  # bureau's east end at the foot of the bay chamfer (v4 f_0011)
    assert abs(ctx.floor_z(ROOM) - FZ) < 1e-6, 'green_bedroom floor moved: update green_bedroom_furn.FZ'


def _reveal(ctx, oid):
    """Window hole in plan: centre, along, outward (unit Vectors), half width, the inner face of the frame and the
    room face of the wall as distances along `outward` from the wall centreline (frame set to the outside face)."""
    f = ctx.opening_frame(oid)
    o, a = Vector(f['outward']), Vector(f['along'])
    t_out = abs(f['face_out'])
    return f['center'].xy, a, o, f['width'] / 2, t_out - f['ext_reveal'] - 0.06, -(f['wall_thickness'] - t_out)


def _spline(pts, n=6):
    """Catmull-Rom resample of a polyline, n points per span (same as dining_furniture.spline)."""
    P_ = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P_) - 2):
        p0, p1, p2, p3 = P_[i - 1], P_[i], P_[i + 1], P_[i + 2]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * (2 * b + (c - a) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (3 * b - a - 3 * c + d) * t ** 3)
                             for a, b, c, d in zip(p0, p1, p2, p3)))
    return out + [tuple(pts[-1])]


def _add(ctx, ob, kind, sym=None, lm=None):
    return ctx.add(ob, ROOM, kind, plan_sym=sym, lm=lm)


def _wall(ctx, ob, x, y, z, facing, kind='fit', sym=None, lm=None):
    return _add(ctx, P.place(ob, (x, y, FZ + z), facing=facing), kind, sym, lm)


def _circ(name):
    """Tag kwargs of lighting circuit name (INTERACT.md, Circuits)."""
    return {'circuit': name}


def _gangs(ctx, names, x, y, z, facing, dimmer, pitch, width=0.02):
    """One object per gang of a blank plate (rotary knob or rocker, as P.switch_plate draws them), in plate-local
    +x order (facing (0, -1): west to east, facing (-1, 0): north to south), so each gang can carry its own tag."""
    out = []
    for i, nm in enumerate(names):
        mb = mo.MB().at(Tr(((i - (len(names) - 1) / 2) * pitch, -0.009, 0)) @ Rx(90 if dimmer else 6))
        if dimmer:
            mb.lathe([(0, 0), (0.0135, 0), (0.0125, 0.012), (0.011, 0.014), (0, 0.014)], 'plastic_white', 12)
        else:
            mb.box((-width / 2, -0.0045, -0.017), (width / 2, 0.001, 0.017), 'plastic_white', bev=0.0008)
        out.append(_wall(ctx, mb.finish(nm), x, y, z, facing, lm='dynamic'))
    return out


# ------------------------------------------------------------------------------------ sills, pelmets, rose
def sills(ctx):
    """Stained hardwood sill boards: a 5 mm slab on each reveal bottom (frame inside face to the plaster) and a
    25 mm board with a rounded nosing, 28 mm proud of the plaster, returned round both bay cheeks."""
    mb, S = mo.MB(), 'mahogany_mid'
    nose = [(0, -0.020), (0.021, -0.020), (0.026, -0.017), (0.028, -0.0075), (0.026, 0.002), (0.021, 0.005), (0, 0.005)]
    for oid in ('w_green_bay', 'w_green_cheek_w', 'w_green_cheek_e', 'w_green_west'):
        c, a, o, hw, t_in, t_room = _reveal(ctx, oid)
        z = FZ + ctx.openings[oid]['sill']
        p0, p1 = c - a * hw + o * t_in, c + a * hw + o * t_room
        mb.box((min(p0.x, p1.x), min(p0.y, p1.y), z), (max(p0.x, p1.x), max(p0.y, p1.y), z + 0.005), S,
               grain=0 if abs(a.x) > 0.5 else 1)
    z = FZ + ctx.openings['w_green_bay']['sill']
    mb.sweep(nose, [(BX0, 0.72, z), (BX0, BY0, z), (BX1, BY0, z), (BX1, 0.72, z)], S)
    c, a, o, hw, _, _ = _reveal(ctx, 'w_green_west')
    z = FZ + ctx.openings['w_green_west']['sill']
    mb.sweep(nose, [(c.x - hw - 0.03, Y0, z), (c.x + hw + 0.03, Y0, z)], S)
    _add(ctx, mb.finish('green_bedroom.sills'), 'trim')


def pelmets(ctx):
    """Boxed pelmets under the ceiling: round the three bay walls (breaking forward round both bay corners as a
    square block) and across the west window. They swallow the wall cornice behind them."""
    def prof(dep, drop):
        return [(0, -drop), (dep - 0.045, -drop), (dep - 0.045, -drop + 0.022), (dep - 0.04, -drop + 0.03),
                (dep - 0.03, -drop + 0.05), (dep - 0.012, -drop + 0.085), (dep - 0.01, -0.07), (dep, -0.07), (dep, 0)]
    zc = FZ + CEIL
    mb = mo.MB()
    mb.sweep(prof(0.15, 0.17), [(BX0 - 0.004, Y0 - 0.005, zc), (BX0, Y0 - 0.005, zc), (BX0, BY0, zc), (BX1, BY0, zc),
                                (BX1, Y0 - 0.005, zc), (BX1 + 0.004, Y0 - 0.005, zc)], 'joinery_white')
    # west: as deep as the bay box (0.15) so it swallows the 0.12 wall cornice (no coplanar fascia / slit at the ceiling)
    mb.sweep(prof(0.15, 0.17), [(-0.535, Y0 - 0.01, zc), (-0.535, Y0, zc), (0.20, Y0, zc), (0.20, Y0 - 0.01, zc)], 'joinery_white')
    _add(ctx, mb.finish('green_bedroom.pelmets'), 'trim')


def rose(ctx, x, y):
    ob = mo.ceiling_rose('acanthus_whorl', 'green_bedroom.rose')
    ob.data.transform(Matrix.Diagonal((0.8, 0.8, 0.8, 1.0)))        # dia 0.75 -> 0.60
    ob.location = (x, y, FZ + CEIL)
    _add(ctx, ob, 'trim')


# ------------------------------------------------------------------------------------ fixed fittings
def radiator(ctx):
    """White column radiator under the bay window: 28 tubes with domed tops, 1.43 x 0.48 x 0.10, z 0.12..0.60."""
    pc = Piece(ctx, 'radiator', BC + 0.005, BY0 + 0.03, (0, 1), z=0.12)
    mb, Wm = mo.MB(), 'white_gloss'
    n, L = 28, 1.43
    tube = [(0, 0.01), (0.02, 0.01), (0.02, 0.44), (0.017, 0.462), (0.009, 0.476), (0, 0.48)]
    for k in range(n):
        mb.at(Tr((-L / 2 + L * (k + 0.5) / n, -0.05, 0)))
        mb.lathe(tube, Wm, 8, ell=(1.0, 2.2))
    mb.at()
    mb.box((-L / 2, -0.085, 0.0), (L / 2, -0.015, 0.03), Wm, bev=0.006, grain=0)
    for sx in (-1, 1):                               # wall brackets, tails, valves
        mb.box((sx * 0.5 - 0.015, -0.03, 0.34), (sx * 0.5 + 0.015, 0.03, 0.40), Wm)
        vx = sx * (L / 2 + 0.035)
        mb.tube([(sx * L / 2, -0.05, 0.015), (vx, -0.05, 0.015)], 0.009, 'chrome', n=6)
        mb.tube([(vx, -0.05, 0.02), (vx, -0.05, -0.12)], 0.008, 'chrome', n=6)
        mb.at(Tr((vx, -0.05, 0.02)))
        mb.lathe([(0, 0), (0.016, 0), (0.019, 0.02), (0.019, 0.055), (0.012, 0.065), (0, 0.065)] if sx < 0 else
                 [(0, 0), (0.012, 0), (0.012, 0.03), (0, 0.032)], Wm, 10)       # TRV head at the east end (local -X)
        mb.at()
    pc.add(mb, kind='fit', sym='radiator')


def aircon(ctx):
    """White split indoor unit 0.80 x 0.29 x 0.22 on the east wall above the small wardrobe."""
    pc = Piece(ctx, 'aircon', X1, 4.30, (-1, 0), z=2.36)
    mb, Wm = mo.MB(), 'plastic_white'
    prof = [(0, 0), (-0.16, 0), (-0.205, 0.03), (-0.22, 0.10), (-0.22, 0.25), (-0.20, 0.29), (0, 0.29)]
    mb.prism([(-0.40, a, b) for a, b in prof], (0.80, 0, 0), Wm)
    mb.box((-0.37, -0.19, -0.002), (0.37, -0.06, 0.004), solid('ac_louvre', '#D9D9D6', 0.5))          # louvre flap
    mb.box((-0.38, -0.208, 0.035), (0.38, -0.205, 0.04), P.mat('plastic_dark'))                             # shadow gap
    mb.box((-0.37, -0.2125, 0.105), (0.30, -0.2105, 0.108), P.mat('plastic_dark'))                     # panel joint (v3 f_0562)
    mb.at(Tr((0.345, -0.2195, 0.13)) @ Rx(90))                                                       # round sensor + lamp dot
    mb.lathe([(0, 0), (0.012, 0), (0.011, 0.002), (0, 0.0025)], solid('ac_lens', '#9EA3A8', 0.25), 12)
    mb.at(Tr((0.345, -0.2185, 0.107)) @ Rx(90))
    mb.lathe([(0, 0), (0.003, 0), (0, 0.001)], solid('ac_led', '#7C8288', 0.3), 6)
    mb.at()
    pc.add(mb, kind='fit')


def coat_rail(ctx):
    """Oak board 0.50 x 0.09 with six brass double hooks on the rear wall over the door pocket."""
    pc = Piece(ctx, 'coat_rail', 3.55, Y1, (0, -1), z=1.75)
    mb = mo.MB()
    mb.box((-0.25, -0.018, -0.045), (0.25, 0, 0.045), 'oak_door', bev=0.004, grain=0)
    for k in range(6):
        x = -0.205 + k * 0.082
        mb.at(Tr((x, -0.018, 0)) @ Rx(90))
        mb.lathe([(0, 0), (0.014, 0), (0.012, 0.004), (0, 0.005)], 'brass', 10)
        mb.at()
        mb.tube([(x, -0.02, 0.0), (x, -0.045, -0.005), (x, -0.07, 0.015), (x, -0.075, 0.05)], 0.004, 'brass', n=5, up=(1, 0, 0))
        mb.tube([(x, -0.02, -0.01), (x, -0.035, -0.035), (x, -0.05, -0.03), (x, -0.055, -0.012)], 0.004, 'brass', n=5, up=(1, 0, 0))
    pc.add(mb, kind='fit')


def electrics(ctx):
    for i, (x, y, z, f) in enumerate(((X1, 1.24, 0.30, (-1, 0)), (X1, 3.34, 0.30, (-1, 0)),
                                      (0.15, Y0, 0.30, (0, 1)), (BC - 1.03, BY0, 0.45, (0, 1)), (X0, 2.45, 0.30, (1, 0)))):
        _wall(ctx, P.socket(2, name=f'green_bedroom.socket.{i}'), x, y, z, f)
    _wall(ctx, P.switch_plate(1, 'blank', name='green_bedroom.spur'), 3.95, Y1, 2.25, (0, -1))
    mb = mo.MB()                                     # a/c remote in its wall cradle, left of S4
    mb.box((3.165, Y1 - 0.02, FZ + 1.22), (3.215, Y1, FZ + 1.33), 'plastic_white', bev=0.003)
    mb.box((3.168, Y1 - 0.016, FZ + 1.25), (3.212, Y1 - 0.004, FZ + 1.40), solid('ac_remote', '#E9E9E6', 0.4), bev=0.004)
    _add(ctx, mb.finish('green_bedroom.remote'), 'fit')
    # S1: three rotary dimmers beside door 1, one knob per circuit (spec 8, INTERACT.md Circuits). Facing it: left
    # (west) = chandelier, middle = downlights (with the plate), right = wall sconce
    s1 = _wall(ctx, P.switch_plate(1, 'blank', wide=True, name='green_bedroom.switch.s1'), -0.50, Y1, 1.20, (0, -1),
               lm='dynamic')
    k_ch, k_dn, k_sc = _gangs(ctx, [f'green_bedroom.switch.s1.{w}' for w in ('chandelier', 'downlights', 'sconce')],
                              -0.50, Y1, 1.20, (0, -1), True, 0.036)
    IX.tag_many([s1, k_dn], 'light', g='green_bedroom.switch.s1', rooms=[ROOM], label='Spotlights', **_circ('main'))
    IX.tag(k_ch, 'lamp', g='green_bedroom.chandelier', label='Chandelier')
    IX.tag(k_sc, 'lamp', g='green_bedroom.sconce', label='Wall light')
    # S4: bathroom lights, right of the sliding door
    s4 = _wall(ctx, P.switch_plate(1, 'rocker', name='green_bedroom.switch.s4'), 3.29, Y1, 1.25, (0, -1))
    IX.tag(s4, 'light', rooms=['green_bathroom'], label='Bathroom lights')


# ------------------------------------------------------------------------------------ lights
def _bead(mb, c, r, mi):
    x, y, z = c
    v = mb._vs([(x + r, y, z), (x - r, y, z), (x, y + r, z), (x, y - r, z), (x, y, z + r * 1.25), (x, y, z - r * 1.25)])
    for a, b, t in ((0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4), (2, 0, 5), (1, 2, 5), (3, 1, 5), (0, 3, 5)):
        f = mb._f([v[a], v[b], v[t]], mi)
        if f:
            f.smooth = False


def chandelier(ctx, x, y):
    """Empire crystal basket chandelier: gilt crown and ring dia 0.70, bead strings sweeping from the crown to
    the ring and tiers of beads closing to a point below it; 0.68 from the ceiling to the bottom."""
    G = 'gilt_bright'
    ring = lambda R, z, n=32: [(R * cos(2 * pi * i / n), R * sin(2 * pi * i / n), z) for i in range(n)]
    mb = mo.MB()
    mb.lathe([(0, -0.035), (0.05, -0.03), (0.06, -0.005), (0.045, 0)], G, 16)                    # ceiling cup
    mb.tube([(0, 0, -0.03), (0, 0, -0.14)], 0.006, G, n=6)
    mb.lathe([(0, -0.16), (0.03, -0.15), (0.07, -0.135), (0.075, -0.12), (0.06, -0.11), (0.0, -0.105)], G, 16)   # crown
    band = [(-0.006, -0.016), (0.006, -0.016), (0.006, 0.016), (-0.006, 0.016)]
    mb.sweep(band + band[:1], ring(0.35, -0.30), G, closed=True)
    tiers = ((0.35, -0.30), (0.29, -0.40), (0.21, -0.49), (0.12, -0.56))
    for R, z in tiers[1:]:
        mb.tube(ring(R, z, 24), 0.004, G, n=4, closed=True, up=(0, 0, 1))
    for k in range(4):                                                                           # stays to the ring
        a = pi / 4 + k * pi / 2
        mb.tube([(0.07 * cos(a), 0.07 * sin(a), -0.125), (0.35 * cos(a), 0.35 * sin(a), -0.29)], 0.003, G, n=4)
    mb.lathe([(0, -0.66), (0.022, -0.64), (0.03, -0.61), (0.02, -0.585), (0, -0.575)], P.two_sided('glass_clear'), 8)
    mb.lathe([(0, -0.60), (0.12, -0.56), (0.21, -0.49), (0.29, -0.40), (0.35, -0.315)], P.two_sided('glass_clear'), 32)
    body = mb.finish('green_bedroom.chandelier')
    body.location = (x, y, FZ + CEIL - ROSE_D)       # the cup sits on the rose's centre boss, not inside it
    _add(ctx, body, 'light')

    cm = mo.MB()                                     # the lit crystal: warm, softly emissive beads
    mi = cm.mi(P.emissive('#F2C283', 1.0))
    for k in range(20):                              # strings from the crown down to the ring
        a = 2 * pi * k / 20
        for j in range(1, 10):
            t = j / 10
            R = 0.075 + (0.35 - 0.075) * t
            z = -0.125 + (-0.30 + 0.125) * t - 0.045 * sin(pi * t)
            _bead(cm, (R * cos(a), R * sin(a), z), 0.011, mi)
    for (R0, z0), (R1, z1), n in zip(tiers, tiers[1:] + ((0.02, -0.60),), (40, 30, 22, 12)):
        for k in range(n):
            a = 2 * pi * (k + 0.5) / n
            for j in range(4):
                t = (j + 0.5) / 4
                R, z = R0 + (R1 - R0) * t, z0 + (z1 - z0) * t
                _bead(cm, (R * cos(a), R * sin(a), z), 0.012, mi)
    lm = P.emissive('#FFD9A0', 6.0)
    for k in range(6):                               # candle lamps inside the basket
        a = 2 * pi * k / 6
        cm.at(Tr((0.17 * cos(a), 0.17 * sin(a), -0.40)))
        cm.lathe([(0, 0), (0.011, 0.004), (0.014, 0.03), (0.009, 0.05), (0, 0.062)], lm, 8)
    cm.at()
    cry = cm.finish('green_bedroom.chandelier.crystal')
    cry.location = body.location
    cry.visible_shadow = False                       # the lamp inside lights the room through the beads
    _add(ctx, cry, 'light')
    IX.tag_many([body, cry], 'lamp', g='green_bedroom.chandelier', label='Chandelier', reach=0.7)   # S1 left knob
    lighting.bulb(ctx, ROOM, (x, y, FZ + CEIL - ROSE_D - 0.36), watts=W_CHAND, kelvin=3000, radius=0.05, name='green_bedroom.chandelier.lamp')


def _crystal_lit():
    """Lit cut glass (v3 f_0648): near-white, polished and mostly metallic so every facet picks up a different
    reflection, part see-through so the bulb core and the lit back facets sparkle inside, faint warm emission."""
    m = M.solid('gb_crystal_cut', '#F5EADB', 0.03, 0.85)
    p = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    p.inputs['Emission Color'].default_value = M.hex_lin('#FFE6C0')
    p.inputs['Emission Strength'].default_value = 0.8         # lower: the cut facets keep their contrast
    p.inputs['Alpha'].default_value = 0.6           # blended glass, as lib glass_* (alpha < 1)
    m.surface_render_method = 'BLENDED'
    m.use_backface_culling = False
    return m


def _diamond_lathe(mb, prof, mat, n=12):
    """Lathe whose every other ring is turned half a facet: flat triangles read as diamond-cut glass."""
    mi = mb.mi(mat)
    rings = [mb._vs([(0, 0, z)]) if r <= 0 else
             mb._vs([(r * cos(2 * pi * (i + 0.5 * (j % 2)) / n), r * sin(2 * pi * (i + 0.5 * (j % 2)) / n), z) for i in range(n)])
             for j, (r, z) in enumerate(prof)]
    for j in range(len(rings) - 1):
        A, B = rings[j], rings[j + 1]
        for i in range(n):
            i1 = (i + 1) % n
            if len(A) == 1:
                mb._f([A[0], B[i1], B[i]], mi)
            elif len(B) == 1:
                mb._f([A[i], A[i1], B[0]], mi)
            elif j % 2 == 0:                         # B[i] lies above, between A[i] and A[i1]
                mb._f([A[i], A[i1], B[i]], mi)
                mb._f([B[i], A[i1], B[i1]], mi)
            else:                                    # B[i1] lies above, between A[i] and A[i1]
                mb._f([A[i], A[i1], B[i1]], mi)
                mb._f([B[i], A[i], B[i1]], mi)


def pineapple(ctx, tag, y):
    """Cast-brass rococo wall light with a cut-glass 'pineapple' shade (L3 / L4), its rocker plate below it."""
    pc = Piece(ctx, 'pineapple.' + tag, X1, y, (-1, 0), z=1.31)
    B = 'brass'
    Ry = lambda d: Matrix.Rotation(radians(d), 4, 'Y')
    mb = mo.MB()
    half = [(0.008, -0.10), (0.026, -0.085), (0.02, -0.06), (0.03, -0.03), (0.034, 0.0), (0.024, 0.035), (0.03, 0.06),
            (0.02, 0.085), (0.007, 0.10)]                                               # tall cast cartouche, waisted
    mb.prism([(w, 0, z) for w, z in half] + [(-w, 0, z) for w, z in reversed(half)], (0, -0.008, 0), B)
    mb.at(Tr((0, -0.008, -0.02)) @ Rx(90))
    mb.dome(0.022, 0.03, 0.014, B, segs=12, rings=3)                                    # boss at the arm root
    for a, L, z0 in ((0, 0.06, 0.055), (32, 0.05, 0.05), (-32, 0.05, 0.05), (64, 0.035, 0.045), (-64, 0.035, 0.045),
                     (180, 0.05, -0.065), (155, 0.035, -0.06), (-155, 0.035, -0.06)):   # shell fan on top, leaf drop below
        mb.at(Tr((0, -0.006, z0)) @ Rx(90) @ Rz(a))
        mb.leaf(L, L * 0.42, 0.01, B, 5, serrate=0.25, curl=0.3)
    mb.at()
    arm = [(0, -0.012, -0.02), (0, -0.04, -0.005), (0, -0.07, 0.03), (0, -0.11, 0.06), (0, -0.15, 0.07), (0, -0.185, 0.055),
           (0, -0.205, 0.02), (0, -0.21, -0.02), (0, -0.21, -0.075)]
    mb.tube(_spline(arm, 3), 0.012, B, n=10, up=(1, 0, 0))                              # heavy cast swan-neck arm, smooth (v3 f_0644)
    mb.tube([(0, -0.07, 0.03), (0, -0.058, 0.058), (0, -0.075, 0.078), (0, -0.096, 0.07), (0, -0.094, 0.05)], 0.007, B,
            n=6, up=(1, 0, 0))                                                          # inner scroll
    for s in (-1, 1):                                                                   # rosette in the curl, both faces
        mb.at(Tr((s * 0.007, -0.082, 0.058)) @ Ry(s * 90))
        mb.dome(0.012, 0.012, 0.006, B, segs=10, rings=2)
    mb.at(Tr((0, -0.21, -0.075)))
    G0 = Tr((0, -0.21, -0.075))
    mb.at(G0)
    mb.lathe([(0.012, 0.012), (0.012, 0.0), (0.024, -0.006), (0.042, -0.016), (0.054, -0.026), (0.058, -0.034), (0.058, -0.042),
              (0.052, -0.044)], P.two_sided('brass_antique'), 16)                      # domed gallery with a rim (antique, as v3 f_0648)
    slope = lambda r: (-0.006 - (r - 0.024) * 0.556 if r < 0.042 else -0.016 - (r - 0.042) * 0.833) + 0.0015
    glow = mb.mi(P.emissive('#FFE2B8', 2.0))
    for k in range(8):                              # leaf-shaped piercings in the dome, lit from the shade below
        a = 2 * pi * k / 8
        kite = [(0.028, 0), (0.037, -0.16), (0.051, 0), (0.037, 0.16)]
        mb._f(mb._vs([(r * cos(a + t), r * sin(a + t), slope(r)) for r, t in kite]), glow)
    for k in range(3):                              # thumbscrews holding the shade in the rim
        a = 2 * pi * k / 3 + pi / 2
        mb.at(G0 @ Tr((0.058 * cos(a), 0.058 * sin(a), -0.038)) @ Rz(degrees(a)) @ Ry(90))
        mb.dome(0.005, 0.005, 0.005, 'bronze_dark', segs=8, rings=2)
    mb.at()
    body = pc.add(mb, kind='light')
    sm = mo.MB()                                     # diamond-cut acorn shade hanging under the gallery, bottom at 1.05
    sm.at(Tr((0, -0.21, -0.26)))
    prof = [(0, 0), (0.012, 0.005), (0.024, 0.016), (0.035, 0.032), (0.044, 0.052), (0.049, 0.074), (0.05, 0.095),
            (0.047, 0.114), (0.041, 0.13), (0.035, 0.14)]
    zs = [i * 0.14 / 18 for i in range(19)]           # 18 rings, every other one sunk: rows of pointed diamonds (v3 f_0648)
    rad = lambda z: next(r0 + (r1 - r0) * (z - z0) / (z1 - z0) for (r0, z0), (r1, z1) in zip(prof, prof[1:]) if z <= z1 + 1e-9)
    _diamond_lathe(sm, [(rad(z) * (0.9 if 0 < j < 18 and j % 2 else 1.0), z) for j, z in enumerate(zs)], _crystal_lit(), 12)
    sm.at(Tr((0, -0.21, -0.20)))                     # bright bulb core seen through the cut glass
    sm.lathe([(0, 0), (0.012, 0.004), (0.017, 0.016), (0.015, 0.03), (0.008, 0.04), (0.006, 0.055), (0, 0.055)],
             P.emissive('#FFF2DC', 12.0), 10)
    shade = pc.add(sm, 'shade', kind='light')
    shade.visible_shadow = False
    for f in shade.data.polygons:
        f.use_smooth = f.material_index > 0          # facets flat, bulb smooth
    if tag == 'n':                                   # S2: its own 1-gang plate
        sw = [_wall(ctx, P.switch_plate(1, 'rocker', name=f'{pc.name}.switch'), X1, y, 0.98, (-1, 0))]
    else:                                            # S3: 2 rockers on one 86 mm plate (v3 f_0646): facing it, left
        plate = _wall(ctx, P.switch_plate(1, 'blank', name='green_bedroom.switch.s3'), X1, y, 0.98, (-1, 0),
                      lm='dynamic')
        sw, two_way = _gangs(ctx, ['green_bedroom.switch.s3.pineapple', 'green_bedroom.switch.s3.downlights'],
                             X1, y, 0.98, (-1, 0), False, 0.028)                            # (north) = this light,
        sw = [sw]                                    # right = the downlights, two-way with S1 (spec 8 assumption)
        IX.tag_many([plate, two_way], 'light', g='green_bedroom.switch.s3', rooms=[ROOM], label='Spotlights',
                    **_circ('main'))
    IX.tag_many([body, shade] + sw, 'lamp', g=pc.name, label='Bedside light')
    lighting.bulb(ctx, ROOM, pc.pt((0, -0.21, -0.19)), watts=W_PINE, kelvin=2800, radius=0.03, name=pc.name + '.lamp')


def sconce(ctx):
    sc = P.sconce(3, 0.36, 0.33, 0.16, mat='brass_antique', shade=(0.05, 0.115, 0.10, 'scalloped', '#F4CB94'),
                  name='green_bedroom.sconce')
    _wall(ctx, sc, PIER, Y0, 1.90, (0, 1), kind='light')      # centred on the pier between the west window and the bay
    IX.tag_many(P.family(sc), 'lamp', g='green_bedroom.sconce', label='Wall light')   # own circuit: S1 right knob
    bpy.context.view_layer.update()
    for j, p in enumerate(P.bulb_points(sc)):
        lighting.bulb(ctx, ROOM, p, watts=W_SCONCE, kelvin=2800, name=f'green_bedroom.sconce.lamp.{j}')


def downlights(ctx):
    pts = [(-0.10, 1.60), (1.90, 1.60), (3.60, 1.60), (-0.10, 4.10), (1.90, 4.10), (3.60, 4.10), (BC - 0.68, 0.55), (BC + 0.67, 0.55)]
    for k, (x, y) in enumerate(pts):
        lighting.downlight(ctx, ROOM, x, y, watts=W_DOWN, kelvin=3000, name=f'green_bedroom.downlight.{k}')
        _add(ctx, P.place(P.downlight(name=f'green_bedroom.downlight_trim.{k}'), (x, y, FZ + CEIL)), 'light')


# ------------------------------------------------------------------------------------ curtains
def curtains(ctx):
    """Same jacquard everywhere, hung under the pelmets (heading z 2.60, hem 0.62). State 0 = open: bay drapes
    gathered into the two front corners and tied back at z 1.15, west drape drawn to the west; state 1 = closed."""
    cloth = tex('curtain', (1.5, 1.5), 0.95)          # leaves 0.40-0.55 m long, 3-4 over the drop (v3 f_0636)
    top = CEIL - 0.17                                # under the pelmets (underside 2.60)
    H = top - 0.62                                   # hem just below the sill boards, clear of the radiator
    kw = dict(height=H, mat=cloth, tie_from_top=top - 1.15, tie_mat='#2F5A48', tassel_mat='#2F5A48', depth=0.05)
    n = [0]

    def hang(group, when, x, y, facing, width, tieback=None, hardware=True, **k):
        name = f'green_bedroom.curtain.{group}.{"open" if when == 0 else "closed"}.{n[0]}'
        n[0] += 1
        ob = P.curtain_panel(width, tieback=tieback, hardware=hardware, name=name, **dict(kw, **k))
        off = 0.03                                   # drapes hang clear of the 28 mm sill nosings
        _wall(ctx, ob, x + off * facing[0], y + off * facing[1], top, facing, kind='decor', lm='dynamic')
        IX.tag(ob, 'show', g=f'green_bedroom.curtains.{group}', when=when, fx='none', label='Curtains')

    # bay, open: cheek drape + front drape bunched into each front corner (rope and tassel on the front drape)
    hang('bay', 0, BX0, 0.57, (1, 0), 0.80, 'left', hardware=False, gather=0.35, seed=2)
    hang('bay', 0, BX0 + 0.29, BY0, (0, 1), 0.50, 'right', gather=0.6, seed=3)
    hang('bay', 0, BX1 - 0.29, BY0, (0, 1), 0.50, 'left', gather=0.6, seed=4)
    hang('bay', 0, BX1, 0.57, (-1, 0), 0.80, 'right', hardware=False, gather=0.35, seed=5)
    # bay, closed: a continuous wall of fabric round the three walls
    hang('bay', 1, BX0, 0.585, (1, 0), 0.78, fold_res=4, seed=6)
    hang('bay', 1, BX0 + 0.71, BY0, (0, 1), 1.34, fold_res=4, seed=7)
    hang('bay', 1, BX1 - 0.71, BY0, (0, 1), 1.34, fold_res=4, seed=8)
    hang('bay', 1, BX1, 0.585, (-1, 0), 0.78, fold_res=4, seed=9)
    # west window: drawn to the west / across x -0.50..0.32
    hang('west', 0, -0.29, Y0, (0, 1), 0.44, 'right', gather=0.6, seed=10)
    hang('west', 1, -0.12, Y0, (0, 1), 0.76, fold_res=4, seed=11)    # stops at the bureau (x 0.265)
    mb = mo.MB()                                     # draw cords with acorn pulls at the east end of each track
    for x, y in ((BX1 - 0.03, 0.94), (0.31, Y0 + 0.03)):
        mb.tube([(x, y, FZ + top), (x, y, FZ + 1.45)], 0.0015, 'linen_cream', n=4)
        mb.at(Tr((x, y, FZ + 1.41)))
        mb.lathe([(0, 0), (0.008, 0.01), (0.009, 0.025), (0.004, 0.04), (0, 0.042)], 'linen_cream', 8)
        mb.at()
    _add(ctx, mb.finish('green_bedroom.curtain.cords'), 'decor')


# ------------------------------------------------------------------------------------ art and ornaments
def ficus(ctx, x, y, rx=0.19, ry=0.12):
    """Bushy weeping fig, 1.15 high, in a ribbed celadon pot dia 0.30. The canopy (rx along the wall, ry across)
    keeps clear of the west curtain (south) and the chest of drawers (north)."""
    rnd = random.Random(4)
    mb = mo.MB()
    mb.lathe([(0, 0), (0.10, 0), (0.125, 0.08), (0.15, 0.25), (0.14, 0.265), (0.128, 0.262), (0.125, 0.24), (0, 0.24)], 'pot_jade', 20)
    for z in (0.07, 0.13, 0.19):
        r = 0.125 + (z - 0.08) * 0.147 + 0.002
        mb.tube([(r * cos(2 * pi * i / 20), r * sin(2 * pi * i / 20), z) for i in range(20)], 0.006, 'pot_jade', n=4, closed=True, up=(0, 0, 1))
    mb.lathe([(0, 0.241), (0.124, 0.241)], P.mat('soil'), 12)
    bark = P.mat('bark')
    for k in range(5):
        a = 2 * pi * k / 5 + 0.3
        mb.tube([(0.02 * cos(a), 0.02 * sin(a), 0.24), (0.06 * cos(a), 0.06 * sin(a), 0.55), (rx * 0.6 * cos(a + 0.4), ry * 0.6 * sin(a + 0.4), 0.95)],
                0.007, bark, n=5, up=(cos(a + 1.57), sin(a + 1.57), 0))
    L1, L2 = P.two_sided('leaf_green'), P.two_sided('leaf_mid')
    for i in range(460):
        d = Vector((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0, 1))).normalized()
        p = Vector((0, 0, 0.74)) + Vector((d.x * rx, d.y * ry, d.z * 0.40)) * rnd.uniform(0.25, 1) ** 0.5
        t = Vector((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(-0.6, 0.6))).normalized()        # leaves droop
        s = t.cross(Vector((0, 0, 1)))
        s = s.normalized() if s.length > 1e-3 else Vector((1, 0, 0))
        L = rnd.uniform(0.04, 0.07)
        w = L * 0.24
        n = t.cross(s) * (0.2 * w)
        vs = mb._vs([p, p + t * (L / 2) + s * w + n, p + t * L, p + t * (L / 2) - s * w + n])
        mb._f(vs, mb.mi(L1 if i % 3 else L2), [(0, 0), (1, 0.5), (0, 1), (-1, 0.5)])
    ob = mb.finish('green_bedroom.plant')
    ob.location = (x, y, FZ)
    _add(ctx, ob, 'decor', 'plant')


def ornaments(ctx):
    grey = ('#8E8E88', '#B5B4AE', '#D8D7D2')         # neutral wash: the real picture is a photograph of people
    a1 = P.framed_picture(None, 0.92, 0.86, 'gilt_plain', frame_w=0.07, mount=0.06, fill=grey, name='green_bedroom.picture')
    _wall(ctx, a1, X1, 2.29, 1.95, (-1, 0), kind='decor')
    mir = P.mirror_framed(0.78, 1.80, 'dark_wood', frame_w=0.09, depth=0.035, name='green_bedroom.mirror')
    _wall(ctx, mir, X0, 4.11, 1.32, (1, 0), kind='decor', sym='mirror')   # z 0.42..2.22: top level with the doorcase consoles (v4 f_0206 / f_0207)
    # three photo frames on the bureau top (blank inserts), leaning back
    for i, (x, w, h, style, fill) in enumerate(((BUREAU + 0.23, 0.20, 0.16, 'white', ('#B9B6AE', '#CFCCC4', '#E2E0DA')),
                                                (BUREAU, 0.26, 0.22, 'champagne', ('#A9ADA6', '#C6C8C0', '#DEDFD8')),
                                                (BUREAU - 0.25, 0.24, 0.20, 'dark_wood', ('#9D9A92', '#BDB9AE', '#D9D6CC')))):
        fr = P.framed_picture(None, w, h, style, frame_w=0.028, depth=0.016, fill=fill, name=f'green_bedroom.photo_frame.{i}')
        loc, rot, _ = (Tr((x, 1.09 + 0.02 * i, FZ + 1.02 + h / 2 * cos(radians(12)) + 0.002)) @ Rz(180 + (8, 0, -9)[i]) @ Rx(-12)).decompose()
        fr.location, fr.rotation_euler = loc, rot.to_euler()
        _add(ctx, fr, 'decor')
    # on the chest of drawers (top z 0.86): whisky glasses on a tray, tantalus, two jewellery chests
    zt = FZ + 0.86
    tray = P.glassware_set(6, False, tray=(0.34, 0.24), tray_mat='silver', glass_h=0.085, name='green_bedroom.glasses')
    _add(ctx, P.place(tray, (-0.38, 1.76, zt), rot_z=90), 'decor')
    pc = Piece(ctx, 'tantalus', -0.38, 2.10, (1, 0), z=0.86)
    mb = mo.MB()
    mb.box((-0.16, -0.075, 0), (0.16, 0.075, 0.03), 'dark_oak_antique', bev=0.003, grain=0)
    mb.box((-0.15, -0.07, 0.03), (0.15, -0.058, 0.10), 'dark_oak_antique', bev=0.002, grain=0)
    for sx in (-1, 1):
        mb.box((sx * 0.16, -0.07, 0.03), (sx * 0.146, 0.07, 0.27), 'dark_oak_antique', bev=0.003, grain=2)
        mb.box((sx * 0.162, -0.072, 0.045), (sx * 0.144, -0.05, 0.06), 'brass')
    mb.box((-0.165, -0.014, 0.27), (0.165, 0.014, 0.285), 'brass', bev=0.003)                    # locking bar
    mb.tube([(-0.07, 0, 0.285), (-0.07, 0, 0.32), (0, 0, 0.335), (0.07, 0, 0.32), (0.07, 0, 0.285)], 0.005, 'brass', n=6, up=(0, 1, 0))
    mb.box((-0.012, -0.0715, 0.055), (0.012, -0.0698, 0.085), 'brass')
    pc.add(mb, kind='decor')
    for i, sx in enumerate((-1, 1)):
        dec = P.decanter(0.225, 'square', level=0.5 if i == 0 else 0.3, name=f'green_bedroom.tantalus.decanter.{i}')
        pc.add(dec, kind='decor', T=Tr((sx * 0.07, 0.005, 0.03)))
    mb = mo.MB()                                     # cherry chest of eight small drawers, carved oak casket
    CH = 'oak_rustic'
    mb.at(Tr((-0.44, 2.47, zt)) @ Rz(90))            # local -Y = east (front)
    mb.box((-0.15, -0.10, 0), (0.15, 0.10, 0.25), CH, bev=0.004, grain=0)
    for k in range(8):
        z = 0.012 + k * 0.0285
        mb.box((-0.14, -0.104, z), (0.14, -0.10, z + 0.025), CH, bev=0.002, grain=0)
        F.knob(mb, 0, -0.104, z + 0.0125, 0.005, CH, 0.008)
    mb.at(Tr((-0.44, 2.83, zt)) @ Rz(90))
    mb.box((-0.15, -0.10, 0.015), (0.15, 0.10, 0.17), 'dark_oak_antique', bev=0.004, grain=0)
    mb.box((-0.16, -0.11, 0), (0.16, 0.11, 0.02), 'dark_oak_antique', bev=0.004, grain=0)
    mb.box((-0.16, -0.11, 0.17), (0.16, 0.11, 0.215), 'dark_oak_antique', bev=0.012, grain=0)    # domed lid
    for sx in (-1, 0, 1):
        mb.box((sx * 0.095 - 0.04, -0.104, 0.04), (sx * 0.095 + 0.04, -0.10, 0.15), 'dark_oak_antique', bev=0.004)
    mb.box((-0.012, -0.112, 0.15), (0.012, -0.108, 0.185), 'brass_antique')
    mb.at()
    _add(ctx, mb.finish('green_bedroom.jewellery'), 'decor')
    ficus(ctx, -0.38, 1.35)


# ------------------------------------------------------------------------------------ build
def build(ctx):
    _measure(ctx)
    shell.repaint(ROOM, '#3F6B5C', DARK_WALL)
    sills(ctx)
    pelmets(ctx)
    cx, cy = 1.85, 2.85                              # chandelier on its rose
    rose(ctx, cx, cy)
    radiator(ctx)
    aircon(ctx)
    coat_rail(ctx)
    electrics(ctx)

    # furniture
    F.wardrobe(ctx, 'wardrobe_big', 1.45, Y1 - 0.025, (0, -1), 1.30, 0.52, 1.72, degs=(-98, 98), n_clothes=18)
    F.wardrobe(ctx, 'wardrobe_small', X1 - 0.025, 4.21, (-1, 0), 1.02, 0.50, 1.80, degs=(-105, 90), shelf=1.45, n_clothes=14)
    F.bed(ctx)
    F.nightstand(ctx, 'nightstand_n', 3.34)
    F.nightstand(ctx, 'nightstand_s', 1.24)
    F.blanket_chest(ctx)
    F.bureau(ctx, BUREAU)
    F.dresser(ctx)
    F.armchair(ctx, BC + 0.74, 0.83, (-0.45, 0.89))     # clear of the drum table and the closed east cheek drape (BVH-checked)
    F.drum_table(ctx, BC + 0.03, 0.68)
    F.corner_chair(ctx, BC - 0.54, 0.80)

    # TV on the dark wall: blank until switched on
    tv = P.tv_panel(1.90, 1.08, name='green_bedroom.tv')
    _wall(ctx, tv, X0, 2.45, 1.64, (1, 0), sym='tv', lm='static')
    pic = P.tv_screen(1.89, 1.07, name='green_bedroom.tv.picture')
    pic.location, pic.rotation_euler = tv.matrix_basis @ Vector((0, -0.0716, 0)), tv.rotation_euler
    _add(ctx, pic, 'fit', lm='dynamic')
    IX.tag(tv, 'trigger', g='green_bedroom.tv', label='TV')
    IX.tag(pic, 'show', g='green_bedroom.tv', when=1, fx='tv', label='TV')

    ornaments(ctx)
    curtains(ctx)

    chandelier(ctx, cx, cy)
    pineapple(ctx, 'n', 3.34)
    pineapple(ctx, 's', 1.24)
    sconce(ctx)
    downlights(ctx)

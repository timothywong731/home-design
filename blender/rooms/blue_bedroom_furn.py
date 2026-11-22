"""Blue bedroom furniture (spec/rooms/blue_bedroom.md 6): wardrobe, bed, two nightstands, bureau, stool, TV cabinet.

Every piece is built in its own frame - x to the viewer's right, front at -y, back (wall side) on y = 0, z up from
the floor - as a handful of objects that all carry the piece's matrix: the carcass (with the plan symbol), the
moving parts (tagged, lm dynamic) and what they reveal (lm dynamic).
"""
import math
import os

import bpy
from mathutils import Matrix, Vector

from lib import interact as IX, materials as M, mouldings as mo, props as P

ROOM = 'blue_bedroom'
Z0 = 3.04                                                    # floor (world Z)
ART = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'textures', 'art')
BRASS = 'brass'
_MESH = {}                                                   # key -> mesh: repeats (nightstands, lamps) share data


def T(x=0.0, y=0.0, z=0.0):
    return Matrix.Translation((x, y, z))


def R(axis, deg):
    return Matrix.Rotation(math.radians(deg), 4, axis)


def art(name, size_m=None, rough=0.9):
    return M.image_mat(f'blue_bedroom_{name}', os.path.join(ART, f'blue_bedroom_{name}.jpg'), size_m=size_m, roughness=rough)


class Piece:
    def __init__(s, ctx, name, x, y, facing, z=Z0, kind='furn'):
        s.ctx, s.name, s.kind = ctx, name, kind
        s.M = T(x, y, z) @ R('Z', math.degrees(math.atan2(facing[0], -facing[1])))

    def add(s, sub, src, kind=None, plan_sym=None, lm=None, L=None, key=None):
        """src = function(mb) that fills a mouldings.MB in piece coordinates, or a ready object (a prop)."""
        name = f'{s.name}.{sub}' if sub else s.name
        if not callable(src):
            ob = src
            ob.name = name
        elif key and key in _MESH:
            ob = bpy.data.objects.new(name, _MESH[key])
        else:
            mb = mo.MB()
            src(mb)
            ob = mb.finish(name)
            if key:
                _MESH[key] = ob.data
        ob.matrix_basis = s.M @ L if L is not None else s.M
        return s.ctx.add(ob, ROOM, kind or s.kind, plan_sym=plan_sym, lm=lm)

    def pt(s, p):
        return s.M @ Vector(p)

    def vec(s, v):
        return s.M.to_3x3() @ Vector(v)

    def hinge(s, objs, sub, label, p, deg, a=None):
        kw = dict(a=s.vec(a)) if a else {}
        IX.tag_many(objs, 'hinge', g=f'{s.name}.{sub}', label=label, p=s.pt(p), deg=deg, **kw)

    def slide(s, objs, sub, label, d):
        IX.tag_many(objs, 'slide', g=f'{s.name}.{sub}', label=label, d=s.vec(d))


# ------------------------------------------------------------------------------------------ shared parts
def bail(mb, x, y, z, w=0.075, mat=BRASS):
    """Plate handle with a hanging bail on a front whose face is the plane y (facing -y)."""
    mb.box((x - w / 2, y - 0.003, z - 0.016), (x + w / 2, y, z + 0.016), mat, bev=0.0015)
    path = [(x + 0.34 * w * math.cos(a), y - 0.011, z + 0.004 + 0.026 * math.sin(a))
            for a in (math.pi * (1 + i / 8) for i in range(9))]
    mb.tube(path, 0.003, mat, n=5, up=(0, 1, 0))
    for sx in (-1, 1):
        mb.box((x + sx * 0.34 * w - 0.004, y - 0.012, z), (x + sx * 0.34 * w + 0.004, y, z + 0.008), mat, bev=0.001)


def drawer(mb, x0, x1, z0, z1, yf, depth, wood, pulls, inner='oak_light', pull_w=0.075, cut=0.0):
    """Drawer: moulded front (face on the plane yf) and an open tray behind it. cut > 0: geometric front."""
    t = 0.02
    mb.box((x0, yf, z0), (x1, yf + t, z1), wood, bev=0.002, grain=0)
    a, b, c, d = x0 + 0.022, x1 - 0.022, z0 + 0.022, z1 - 0.022
    if cut:                                                  # raised panel with the corners cut (Jacobean)
        mb.prism([(a + cut, yf, c), (b - cut, yf, c), (b, yf, c + cut), (b, yf, d - cut), (b - cut, yf, d),
                  (a + cut, yf, d), (a, yf, d - cut), (a, yf, c + cut)], (0, -0.006, 0), wood, grain=0)
    else:
        mb.box((a, yf - 0.004, c), (b, yf, d), wood, bev=0.004, grain=0)
    mb.box((x0 + 0.008, yf + t, z0 + 0.008), (x1 - 0.008, yf + depth, z0 + 0.016), inner)
    for xa, xb in ((x0 + 0.008, x0 + 0.018), (x1 - 0.018, x1 - 0.008)):
        mb.box((xa, yf + t, z0 + 0.016), (xb, yf + depth, z1 - 0.015), inner, grain=1)
    mb.box((x0 + 0.018, yf + depth - 0.01, z0 + 0.016), (x1 - 0.018, yf + depth, z1 - 0.015), inner, grain=0)
    for hx in pulls:
        bail(mb, hx, yf - (0.006 if cut else 0.004), (z0 + z1) / 2, pull_w)


def reeded(mb, x0, x1, y, z0, z1, mat, n=3):
    """Reeded pilaster strip standing 5 mm proud of the plane y."""
    mb.box((x0, y - 0.002, z0), (x1, y + 0.01, z1), mat, grain=2)
    w = (x1 - x0) / n
    for i in range(n):
        mb.box((x0 + w * (i + 0.12), y - 0.006, z0 + 0.01), (x0 + w * (i + 0.88), y, z1 - 0.01), mat, bev=0.003, grain=2)


def oct_ring(x0, x1, z0, z1, i, y, cut=0.0):
    """Rectangle x0..x1 x z0..z1 on the plane y, inset by i; cut = length of 45 degree corner cuts (0 = none)."""
    a, b, c, d = x0 + i, x1 - i, z0 + i, z1 - i
    if not cut:
        return [(a, y, c), (b, y, c), (b, y, d), (a, y, d)]
    k = max(0.0, cut - i * 0.586)
    return [(a + k, y, c), (b - k, y, c), (b, y, c + k), (b, y, d - k), (b - k, y, d), (a + k, y, d), (a, y, d - k),
            (a, y, c + k)]


def mirror_plate(mb, x0, x1, z0, z1, y, bevel=0.016, cut=0.0):
    """Bevelled mirror on the plane y (facing -y); cut = length of the 45 degree corner cuts."""
    o, i = oct_ring(x0, x1, z0, z1, 0.0, y + 0.004, cut), oct_ring(x0, x1, z0, z1, bevel, y, cut)
    mb.face(i, 'mirror', (0, -1, 0))
    for j in range(len(o)):
        k = (j + 1) % len(o)
        mb.face([o[j], o[k], i[k], i[j]], 'mirror', (0, -1, 0))


def relief(mb, cx, y, cz, leaves, mat, urn=None):
    """Low-relief foliage on the plane y (facing -y): leaves = [(dx, dz, angle from vertical, length, width)]."""
    for dx, dz, ang, ln, wd in leaves:
        mb.at(T(cx + dx, y, cz + dz) @ R('X', 90) @ R('Z', ang))
        mb.leaf(ln, wd, 0.007, mat, segs=5, serrate=0.25, curl=0.4)
    if urn:
        mb.at(T(cx, y, cz + urn[0]))
        mb.lathe(urn[1], mat, segs=8, ell=(1.0, 0.3), a0=math.pi, a1=2 * math.pi)
    mb.at()


def inward(mb, x0, x1, y0, y1, z0, z1, mat, front=True, top=True, skip=()):
    """Lining of a cupboard interior: faces looking into the box x0..x1, y0 (front) .. y1 (back), z0..z1."""
    mb.face([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], mat, (0, -1, 0), grain=2)
    for x, n in ((x0, 1), (x1, -1)):
        mb.face([(x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)], mat, (n, 0, 0), grain=2)
    if 'floor' not in skip:
        mb.face([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], mat, (0, 0, 1))
    if top:
        mb.face([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], mat, (0, 0, -1))


# ------------------------------------------------------------------------------------------ F1 wardrobe
def wardrobe(ctx):
    """Edwardian dark walnut wardrobe 1.20 x 0.52 x 2.05: reeded pilasters, carved urn panels over fielded panels
    in the fixed side bays, bevelled mirror door (opens, hinged right), two short drawers over a long one."""
    W, X, Yf = 'dark_oak_antique', 0.588, -0.508
    pc = Piece(ctx, 'blue_bedroom.wardrobe', 3.078, 13.61, (-1, 0))
    URN = [(0, 0), (0.022, 0), (0.016, 0.012), (0.03, 0.03), (0.046, 0.05), (0.05, 0.068), (0.05, 0.078), (0, 0.078)]

    def carcass(mb):
        b = mb.box
        b((-0.60, -0.52, 0), (0.60, 0, 0.08), W, bev=0.004, grain=0)                       # plinth
        b((-X, -0.012, 0.08), (X, 0, 1.95), W, grain=2)                                    # back
        for sx in (-1, 1):
            b((sx * X, Yf, 0.08), (sx * (X - 0.02), -0.012, 1.95), W, grain=2)             # sides
            reeded(mb, sx * X, sx * (X - 0.027), Yf, 0.462, 1.86, W)
            reeded(mb, sx * 0.21, sx * 0.237, Yf, 0.462, 1.86, W)
            x0, x1 = sx * 0.237, sx * (X - 0.027)                                          # fixed side bay
            b((x0, Yf + 0.006, 0.462), (x1, Yf + 0.02, 1.86), W, grain=2)
            for xa in (x0, x1 - sx * 0.04):                                                # stiles
                b((xa, Yf, 0.462), (xa + sx * 0.04, Yf + 0.006, 1.86), W, grain=2)
            for za, zb in ((0.462, 0.54), (1.40, 1.47), (1.80, 1.86)):                     # rails
                b((x0 + sx * 0.04, Yf, za), (x1 - sx * 0.04, Yf + 0.006, zb), W, grain=0)
            b((x0 + sx * 0.062, Yf + 0.001, 0.565), (x1 - sx * 0.062, Yf + 0.006, 1.375), W, bev=0.005, grain=2)
            cx = (x0 + x1) / 2                                                             # carved urn + foliage
            relief(mb, cx, Yf + 0.006, 1.49,
                   [(0, 0.125, 0, 0.165, 0.05), (-0.01, 0.12, 38, 0.13, 0.045), (0.01, 0.12, -38, 0.13, 0.045),
                    (-0.02, 0.115, 78, 0.09, 0.04), (0.02, 0.115, -78, 0.09, 0.04),
                    (-0.085, 0.05, -150, 0.05, 0.03), (0.085, 0.05, 150, 0.05, 0.03)], W, urn=(0.045, URN))
        b((-X, Yf, 0.08), (X, -0.012, 0.10), W)                                            # bottom board
        b((-X, Yf, 0.255), (X, Yf + 0.03, 0.27), W, grain=0)                               # drawer rail
        b((-0.011, Yf, 0.27), (0.011, Yf + 0.03, 0.425), W, grain=2)                       # drawer divider
        b((-X, Yf, 0.425), (X, -0.012, 0.44), W, grain=0)
        b((-0.60, -0.52, 0.43), (0.60, 0, 0.462), W, bev=0.006, grain=0)                   # waist moulding
        b((-X, Yf - 0.004, 1.86), (X, Yf + 0.016, 1.93), W, grain=0)                       # frieze
        for z in (1.875, 1.905):
            b((-X, Yf - 0.008, z), (X, Yf - 0.004, z + 0.012), W, bev=0.003, grain=0)
        b((-X, Yf, 1.93), (X, -0.012, 2.05), W, grain=0)                                   # top
        mb.sweep([(0.004, 0), (0.016, 0), (0.016, 0.02), (0.022, 0.032), (0.034, 0.052), (0.042, 0.075), (0.044, 0.09),
                  (0.044, 0.12), (0, 0.12)], [(X, 0, 1.93), (X, Yf, 1.93), (-X, Yf, 1.93), (-X, 0, 1.93)], W)

    def inner(mb):
        L, x, y0 = 'oak_rustic', X - 0.021, Yf + 0.021
        inward(mb, -x, x, y0, -0.013, 0.441, 1.929, L)
        for sx in (-1, 1):                                                                 # back of the fixed bays
            mb.face([(sx * 0.21, y0, 0.441), (sx * x, y0, 0.441), (sx * x, y0, 1.929), (sx * 0.21, y0, 1.929)], L, (0, 1, 0))
        mb.tube([(-x, -0.26, 1.77), (x, -0.26, 1.77)], 0.012, BRASS, n=8)                  # hanging rail
        for i, (gx, col, zb) in enumerate(((-0.33, '#8A8F99', 0.80), (-0.17, '#5B6470', 0.95), (-0.09, '#B8B2A7', 0.70),
                                           (0.0, '#2E3440', 0.62), (0.08, '#6E5A4E', 0.85), (0.16, '#9AA3B0', 0.95),
                                           (0.34, '#44495A', 0.75))):                      # plain garments on hangers
            cloth = M.solid(f'blue_bedroom_garment_{i}', col, 0.9)
            mb.prism([(gx, -0.47, 1.62), (gx, -0.285, 1.735), (gx, -0.235, 1.735), (gx, -0.05, 1.62), (gx, -0.07, zb),
                      (gx, -0.45, zb)], (0.036, 0, 0), cloth)
            mb.tube([(gx + 0.018, -0.26, 1.735), (gx + 0.018, -0.26, 1.775)], 0.003, 'chrome', n=5)

    def door(mb):
        x, z0, z1, yb = 0.208, 0.464, 1.858, Yf + 0.022
        for xa, xb in ((-x, -x + 0.05), (x - 0.05, x)):
            mb.box((xa, Yf, z0), (xb, yb, z1), W, bev=0.002, grain=2)
        mb.box((-x + 0.05, Yf, z0), (x - 0.05, yb, 0.56), W, grain=0)
        mb.box((-x + 0.05, Yf, 1.81), (x - 0.05, yb, z1), W, grain=0)
        mb.box((-x + 0.05, Yf + 0.014, 0.56), (x - 0.05, yb, 1.81), W, grain=2)            # backing board
        mirror_plate(mb, -x + 0.05, x - 0.05, 0.56, 1.81, Yf + 0.008, bevel=0.018)
        hx = -x + 0.025                                                                    # escutcheon + tassel drop
        mb.box((hx - 0.011, Yf - 0.003, 1.02), (hx + 0.011, Yf, 1.085), BRASS, bev=0.002)
        mb.at(T(hx, Yf - 0.012, 1.05))
        mb.lathe([(0, -0.08), (0.007, -0.075), (0.012, -0.05), (0.005, -0.018), (0.003, 0), (0, 0)], BRASS, segs=8)
        mb.at()

    pc.add('', carcass, plan_sym='wardrobe', lm='static')
    pc.add('inner', inner, lm='dynamic')
    d = pc.add('door', door, lm='dynamic')
    pc.hinge([d], 'door', 'Wardrobe', (0.208, Yf, 0), 100)
    for sub, x0, x1, z0, z1, pulls in (('long', -0.566, 0.566, 0.103, 0.252, (-0.30, 0.30)),
                                       ('left', -0.566, -0.013, 0.273, 0.422, (-0.29,)),
                                       ('right', 0.013, 0.566, 0.273, 0.422, (0.29,))):
        ob = pc.add(f'drawer.{sub}', lambda mb: drawer(mb, x0, x1, z0, z1, Yf, 0.44, W, pulls), lm='dynamic')
        pc.slide([ob], f'drawer.{sub}', 'Drawer', (0, -0.30, 0))
    return pc


# ------------------------------------------------------------------------------------------ F2 bed
def _arch(x, half, rise):
    return rise * max(0.0, math.cos(math.pi * x / (2 * half))) ** 0.75


def _board(mb, y, zr, zs, zp, rise, wood, burr):
    """Head / foot board on the plane y (thickness toward -y): posts to zp, top rail at zr, slats down to zs,
    pierced scroll cresting rising `rise` above the rail."""
    b, yb = mb.box, y - 0.07
    for sx in (-1, 1):
        b((sx * 0.73, yb, 0), (sx * 0.66, y, zp), wood, bev=0.004, grain=2)                # post
        b((sx * 0.74, yb - 0.01, zp), (sx * 0.65, y + 0.01, zp + 0.03), wood, bev=0.006)   # block cap
        b((sx * 0.725, yb + 0.005, zp + 0.03), (sx * 0.665, y - 0.005, zp + 0.045), wood, bev=0.012)
        ear = [(sx * 0.66, y - 0.02, zr + 0.06), (sx * 0.66, y - 0.02, zp - 0.04), (sx * 0.62, y - 0.02, zr + 0.105),
               (sx * 0.56, y - 0.02, zr + 0.07), (sx * 0.47, y - 0.02, zr + 0.06)]         # upturned ear at the post
        mb.prism(ear, (0, -0.03, 0), wood)
        for k in range(3):                                                                 # slats
            xa = sx * (0.60 - 0.115 * k)
            b((xa - 0.03, y - 0.045, zs), (xa + 0.03, y - 0.025, zr), wood, bev=0.002, grain=2)
    b((-0.66, y - 0.055, zr), (0.66, y - 0.015, zr + 0.07), wood, bev=0.004, grain=0)      # top rail
    b((-0.66, y - 0.055, zs - 0.07), (0.66, y - 0.015, zs), wood, bev=0.004, grain=0)      # bottom rail
    b((-0.19, y - 0.05, zs), (0.19, y - 0.02, zr), wood, grain=2)                          # centre panel
    b((-0.14, y - 0.053, zs + 0.05), (0.14, y - 0.05, zr - 0.05), burr, grain=2)
    half, n, zc = 0.42, 16, zr + 0.07
    xs = [-half + 2 * half * i / n for i in range(n + 1)]
    mb.tube([(x, y - 0.035, zc + _arch(x, half, rise)) for x in xs], 0.019, wood, n=6, up=(0, 1, 0))     # arched crest moulding
    mb.prism([(-half, y - 0.027, zc)] + [(x, y - 0.027, zc + 0.42 * _arch(x, half, rise)) for x in xs] + [(half, y - 0.027, zc)],
             (0, -0.016, 0), wood)                                                         # solid foot of the cresting

    def scroll(cx, cz, r, a0, a1, grow=0.0, rr=0.013):
        pts = []
        for i in range(13):
            a = math.radians(a0 + (a1 - a0) * i / 12)
            k = r * (1 + grow * i / 12)
            pts.append((cx + k * math.cos(a), y - 0.035, cz + k * math.sin(a)))
        mb.tube(pts, rr, wood, n=5, up=(0, 1, 0))
    s = rise / 0.24                                                                        # pierced C-scrolls above it
    scroll(0, zc + 0.155 * s, 0.05 * s, 0, 360)                                            # centre oval
    for sx in (-1, 1):
        scroll(sx * 0.115, zc + 0.14 * s, 0.045 * s, 90 - sx * 100, 90 + sx * 190, 0.25)
        scroll(sx * 0.215, zc + 0.115 * s, 0.035 * s, 90 + sx * 60, 90 - sx * 210, 0.2)
        scroll(sx * 0.295, zc + 0.085 * s, 0.022 * s, 0, 360, rr=0.009)


def _drape(mb, mat, x_half, y0, y1, top, hang, lift=0.0, nu=22, nv=20, r=0.07, head_roll=True, seed=0.0, uv0=(0.0, 0.0)):
    """Cloth lying on the mattress from y0 (head end) to y1 (foot), falling `hang` over both sides at x_half.
    UVs are arc lengths in metres, so the print keeps its size over the edge."""
    mi = mb.mi(mat)

    def across(u):                                           # arc length from the centre line -> (x, dz)
        s, a = (1 if u >= 0 else -1), abs(u)
        flat = x_half - r
        if a <= flat:
            return u, 0.0
        if a <= flat + r * math.pi / 2:
            t = (a - flat) / r
            return s * (flat + r * math.sin(t)), -r * (1 - math.cos(t))
        return s * (x_half + 0.012 * math.sin((a - flat) * 9)), -r - (a - flat - r * math.pi / 2)

    half = x_half - r + r * math.pi / 2 + hang - r
    rows = []
    for j in range(nv + 1):
        v = j / nv
        y = y0 + (y1 - y0) * v
        row = []
        for i in range(nu + 1):
            u = -half + 2 * half * i / nu
            x, dz = across(u)
            puff = 0.016 * math.sin(7.3 * x + 1.7 * y + seed) * math.sin(5.1 * y + 0.6 + seed) + 0.008 * math.sin(13 * x - 9 * y)
            edge = min(1.0, v / 0.06, (1 - v) / 0.04) if head_roll else 1.0
            z = top + lift + dz + puff * (1 if dz == 0 else 0.4) - 0.035 * (1 - edge) ** 2
            row.append((x, y, z, u, y))
        rows.append(row)
    V = [mb._vs([p[:3] for p in row]) for row in rows]
    for j in range(nv):
        for i in range(nu):
            q = [(j, i), (j, i + 1), (j + 1, i + 1), (j + 1, i)]
            mb._f([V[a][b] for a, b in q][::-1], mi, [(rows[a][b][3] + uv0[0], rows[a][b][4] + uv0[1]) for a, b in q][::-1])


def bed(ctx):
    """Edwardian dark mahogany double bedstead 2.05 x 1.46, head on the east wall: slatted head and foot boards with
    pierced scroll crestings, deep side rails; navy bamboo-leaf duvet and pillows, chrysanthemum band over the foot."""
    WOOD, BURR = 'mahogany_dark', 'mahogany_mid'
    pc = Piece(ctx, 'blue_bedroom.bed', 3.07, 15.36, (-1, 0))
    duv = P.two_sided(art('duvet', (0.9, 0.9)))
    bnd = P.two_sided(art('band', (1.0, 0.5)))
    sheet = M.solid('blue_bedroom_sheet', '#2B2A3E', 0.9)

    def frame(mb):
        _board(mb, 0.0, 1.11, 0.47, 1.29, 0.25, WOOD, BURR)                                # head (crest to 1.45)
        _board(mb, -1.98, 0.74, 0.37, 0.90, 0.16, WOOD, BURR)                              # foot (crest to 0.98)
        for sx in (-1, 1):
            mb.box((sx * 0.715, -1.985, 0.30), (sx * 0.685, -0.065, 0.48), WOOD, bev=0.003, grain=1)
        mb.box((-0.685, -1.98, 0.36), (0.685, -0.07, 0.40), 'oak_light')                    # slat base

    def bedding(mb):
        mb.box((-0.683, -1.975, 0.40), (0.683, -0.075, 0.62), sheet, bev=0.03)             # mattress in a fitted sheet
        _drape(mb, duv, 0.74, -0.52, -1.972, 0.645, 0.24)
        _drape(mb, bnd, 0.745, -1.28, -1.78, 0.645, 0.245, lift=0.004, nv=8, head_roll=False, uv0=(0.0, 1.28))

    pc.add('', frame, plan_sym='bed', lm='static')
    pc.add('bedding', bedding, kind='decor', lm='static')
    for i, sx in enumerate((-1, 1)):                                                       # two pillows against the head
        pil = P.cushion(0.62, 0.42, 0.15, duv, name=f'blue_bedroom.bed.pillow.{i}')
        pc.add(f'pillow.{i}', pil, kind='decor', L=T(sx * 0.345, -0.27, 0.62) @ R('Z', sx * 4) @ R('X', 63) @ T(0, 0.21, 0))
    return pc


# ------------------------------------------------------------------------------------------ F3 / F4 nightstands
def nightstand(ctx, i, yc):
    """French provincial light-oak bedside cabinet 0.39 x 0.34 x 0.60: moulded top, carved door (opens, hinged
    right), shaped apron, short cabriole legs. 0.39 along the wall (spec 0.42): the pair stands in the 0.41 gap
    between the wardrobe and the bed's side rail with the duvet hanging over the bed edge."""
    O, H, Yf = 'oak_rustic', 0.195, -0.325                                                 # H: half the top
    X = H - 0.025
    pc = Piece(ctx, f'blue_bedroom.nightstand.{i}', 3.078, yc, (-1, 0))

    def carcass(mb):
        b = mb.box
        b((-H, -0.34, 0.575), (H, 0, 0.60), O, bev=0.007, grain=0)                         # top
        b((-H + 0.01, -0.332, 0.562), (H - 0.01, -0.004, 0.577), O, bev=0.004, grain=0)
        b((-X, -0.012, 0.16), (X, -0.002, 0.565), O, grain=2)                              # back
        b((-X, Yf, 0.16), (X, -0.012, 0.18), O)
        for sx in (-1, 1):
            b((sx * X, Yf, 0.16), (sx * (X - 0.02), -0.012, 0.565), O, grain=2)
        b((-(X - 0.02), Yf, 0.555), (X - 0.02, Yf + 0.018, 0.565), O, grain=0)
        apron = [(-X, Yf, 0.16), (-X, Yf, 0.115), (-0.11, Yf, 0.135), (-0.045, Yf, 0.118), (0, Yf, 0.10), (0.045, Yf, 0.118),
                 (0.11, Yf, 0.135), (X, Yf, 0.115), (X, Yf, 0.16)]
        mb.prism(apron, (0, 0.018, 0), O)
        leg = [(0, 0.165), (0.05, 0.165), (0.056, 0.13), (0.04, 0.07), (0.036, 0.03), (0.05, 0.0), (0.022, 0.0),
               (0.012, 0.035), (0.006, 0.09)]
        for sx in (-1, 1):                                                                 # short cabriole legs
            for y in (Yf, -0.045):
                mb.prism([(sx * (X + 0.012 - d), y, z) for d, z in leg], (0, 0.034, 0), O)

    def inner(mb):
        inward(mb, -X + 0.021, X - 0.021, Yf + 0.019, -0.013, 0.181, 0.561, 'oak_light')
        mb.box((-X + 0.021, Yf + 0.03, 0.36), (X - 0.021, -0.013, 0.372), 'oak_light')

    def door(mb):
        x, z0, z1 = X - 0.022, 0.182, 0.553
        mb.box((-x, Yf, z0), (x, Yf + 0.018, z1), O, bev=0.002, grain=2)
        mb.prism([(-x + 0.03, Yf, z0 + 0.03), (x - 0.03, Yf, z0 + 0.03), (x - 0.03, Yf, z1 - 0.06), (x - 0.07, Yf, z1 - 0.03),
                  (-x + 0.07, Yf, z1 - 0.03), (-x + 0.03, Yf, z1 - 0.06)], (0, -0.005, 0), O)
        zc = (z0 + z1) / 2
        mb.at(T(0, Yf - 0.005, zc - 0.01) @ R('X', 90))                                    # cartouche: boss + horns
        mb.dome(0.035, 0.045, 0.009, O, segs=10)
        mb.at()
        relief(mb, 0, Yf - 0.005, zc,
               [(-0.03, 0.02, 70, 0.085, 0.03), (0.03, 0.02, -70, 0.085, 0.03), (-0.02, -0.03, 140, 0.07, 0.03),
                (0.02, -0.03, -140, 0.07, 0.03), (0, -0.05, 180, 0.06, 0.03)], O)
        mb.box((-x + 0.012, Yf - 0.012, zc + 0.03), (-x + 0.022, Yf, zc + 0.05), BRASS, bev=0.003)   # key escutcheon

    pc.add('', carcass, plan_sym='bedside', key='ns.carcass')
    pc.add('inner', inner, lm='dynamic', key='ns.inner')
    d = pc.add('door', door, lm='dynamic', key='ns.door')
    pc.hinge([d], 'door', 'Nightstand', (X - 0.022, Yf, 0), 95 if i == 0 else 88)    # south: clear of the wardrobe, north: the duvet
    return pc


# ------------------------------------------------------------------------------------------ F5 bureau
def bureau(ctx):
    """1920s Jacobean-revival dark oak bureau 0.76 x 0.42 x 1.00: sloping fall front with applied geometric
    mouldings (opens onto pull-out lopers, pigeonholes inside), two geometric drawers, barley-twist legs on bun feet
    with bobbin-turned stretchers."""
    O, X, Yf = 'dark_oak_antique', 0.38, -0.42                # dark oak with golden highlights (f_0463, spec #4A3A28)
    pc = Piece(ctx, 'blue_bedroom.bureau', -0.628, 15.94, (1, 0))
    H0, H1, YT = 0.645, 0.99, -0.145                         # hinge line / top edge of the fall, depth of the top board
    sl = math.hypot(YT - Yf, H1 - H0)
    sy, sz = (YT - Yf) / sl, (H1 - H0) / sl
    FALL = Matrix(((1, 0, 0, 0), (0, sy, -sz, Yf), (0, sz, sy, H0), (0, 0, 0, 1)))        # (x, along the slope, outward)

    def carcass(mb):
        b = mb.box
        for sx in (-1, 1):
            b((sx * X, Yf, 0.30), (sx * (X - 0.02), -0.012, 0.645), O, grain=2)            # lower sides
            mb.prism([(sx * X, Yf, 0.645), (sx * X, 0, 0.645), (sx * X, 0, 1.0), (sx * X, YT, 1.0)], (-sx * 0.02, 0, 0), O)
            for y in (Yf + 0.03, -0.04):                                                   # bun feet
                mb.at(T(sx * (X - 0.03), y, 0))
                mb.lathe([(0, 0), (0.018, 0), (0.03, 0.012), (0.03, 0.026), (0.016, 0.04), (0, 0.04)], O, segs=10)
            mb.at(T(sx * (X - 0.03), Yf + 0.03, 0.075) @ R('X', -90))                      # side stretchers
            mb.lathe(P.turned_profile('bobbin', 0.35, 0.03), O, segs=8)
            mb.at()                                                                        # next side in piece coords
        mb.at(T(-X + 0.03, Yf + 0.03, 0.075) @ R('Y', 90))                                 # front stretcher
        mb.lathe(P.turned_profile('bobbin', 2 * X - 0.06, 0.03), O, segs=8)
        mb.at()
        b((-X, -0.012, 0.30), (X, 0, 1.0), O, grain=2)                                     # back
        b((-X, Yf, 0.30), (X, -0.012, 0.318), O, grain=0)
        b((-X, Yf, 0.455), (X, Yf + 0.03, 0.47), O, grain=0)                               # drawer rail
        b((-0.335, Yf, 0.60), (0.335, -0.012, 0.645), O, grain=0)                          # writing bed
        b((-X - 0.006, Yf - 0.006, 0.296), (X + 0.006, 0, 0.312), O, bev=0.004, grain=0)   # base moulding
        b((-X - 0.008, YT - 0.008, 0.985), (X + 0.008, 0, 1.005), O, bev=0.004, grain=0)   # top board

    def inner(mb):
        L, x = 'oak_rustic', X - 0.0205
        mb.face([(-x, Yf, 0.6455), (x, Yf, 0.6455), (x, -0.013, 0.6455), (-x, -0.013, 0.6455)], O, (0, 0, 1), grain=0)
        mb.face([(-x, -0.013, 0.645), (x, -0.013, 0.645), (x, -0.013, 0.985), (-x, -0.013, 0.985)], L, (0, -1, 0))
        for sx in (-1, 1):
            mb.face([(sx * x, Yf, 0.645), (sx * x, -0.013, 0.645), (sx * x, -0.013, 0.985), (sx * x, YT, 0.985)], L, (-sx, 0, 0))
        mb.box((-x, -0.19, 0.66), (x, -0.013, 0.668), L)                                   # pigeonholes
        mb.box((-x, -0.19, 0.83), (x, -0.013, 0.838), L)
        for k in range(1, 7):
            xa = -x + 2 * x * k / 7
            mb.box((xa - 0.004, -0.19, 0.668), (xa + 0.004, -0.013, 0.978 if k in (2, 5) else 0.83), L, grain=2)
        mb.box((-x + 2 * x * 2 / 7, -0.19, 0.90), (-x + 2 * x * 5 / 7, -0.013, 0.908), L)

    def fall(mb):
        mb.at(FALL)
        w = X - 0.022
        mb.box((-w, 0, -0.018), (w, sl, 0), O, bev=0.002, grain=0)
        mb.box((-0.13, 0.07, 0), (0.13, sl - 0.07, 0.007), O, bev=0.006, grain=0)          # centre panel
        mb.box((-0.105, 0.095, 0.007), (0.105, sl - 0.095, 0.011), O, bev=0.004, grain=0)
        for sx in (-1, 1):                                                                 # cushion crosses
            cx, a, c, m = sx * 0.245, 0.085, 0.035, sl / 2
            cross = [(cx - c, m - a * 1.6), (cx + c, m - a * 1.6), (cx + c, m - c), (cx + a, m - c), (cx + a, m + c),
                     (cx + c, m + c), (cx + c, m + a * 1.6), (cx - c, m + a * 1.6), (cx - c, m + c), (cx - a, m + c),
                     (cx - a, m - c), (cx - c, m - c)]
            mb.prism([(px, py, 0) for px, py in cross], (0, 0, 0.008), O)
        mb.box((-0.008, sl - 0.06, 0), (0.008, sl - 0.03, 0.004), BRASS, bev=0.001)       # escutcheon, key and tassel
        mb.at(FALL @ T(0, sl - 0.05, 0.016) @ R('X', 90))
        mb.lathe([(0, 0), (0.004, 0), (0.004, 0.03), (0.011, 0.045), (0.014, 0.10), (0, 0.10)], 'linen_cream', segs=8)
        mb.at()

    def loper(mb):
        for sx in (-1, 1):
            mb.box((sx * 0.3575, Yf, 0.605), (sx * 0.3375, -0.10, 0.643), O, grain=1)
            mb.box((sx * 0.3515, Yf - 0.012, 0.619), (sx * 0.3435, Yf, 0.629), BRASS, bev=0.003)

    pc.add('', carcass, plan_sym='bureau', lm='static')
    pc.add('inner', inner, lm='dynamic')
    f, lp = pc.add('fall', fall, lm='dynamic'), pc.add('lopers', loper, lm='dynamic')
    pc.hinge([f], 'fall', 'Bureau', (0, Yf, H0), 180 - math.degrees(math.atan2(sz, sy)), a=(1, 0, 0))
    pc.slide([lp], 'fall', 'Bureau', (0, -0.28, 0))
    for k, (z0, z1) in enumerate(((0.32, 0.453), (0.472, 0.598))):
        ob = pc.add(f'drawer.{k}', lambda mb: drawer(mb, -0.357, 0.357, z0, z1, Yf, 0.36, O, (-0.2, 0.2), pull_w=0.04,
                                                     cut=0.03), lm='dynamic')
        pc.slide([ob], f'drawer.{k}', 'Drawer', (0, -0.25, 0))
    leg = None
    for k, (sx, y) in enumerate(((-1, Yf + 0.03), (1, Yf + 0.03), (-1, -0.04), (1, -0.04))):
        leg = P.turned_leg(0.26, 0.05, 'barley_twist', top_block=0.03, bottom_block=0.07, mat=O, pitch=0.09,
                           name=f'blue_bedroom.bureau.leg.{k}')
        pc.add(f'leg.{k}', leg, L=T(sx * (X - 0.03), y, 0.04))
    return pc


# ------------------------------------------------------------------------------------------ F6 stool
def stool(ctx):
    """Mahogany stool 0.50 x 0.34 x 0.50 on slim square tapered legs, drop-in navy seat with a cream piped edge."""
    Wd = 'mahogany_mid'
    pc = Piece(ctx, 'blue_bedroom.stool', -0.47, 15.27, (1, 0))

    def body(mb):
        for sx in (-1, 1):
            for y in (-0.315, -0.025):
                mb.at(T(sx * 0.225, y, 0) @ R('Z', 45))
                mb.lathe([(0, 0), (0.014, 0), (0.024, 0.40), (0, 0.40)], Wd, segs=4)
        mb.at()
        mb.box((-0.25, -0.34, 0.40), (0.25, 0, 0.455), Wd, bev=0.004, grain=0)
        mb.box((-0.225, -0.315, 0.455), (0.225, -0.025, 0.50), M.solid('blue_bedroom_seat', '#262B3C', 0.95), bev=0.014)
        mb.tube([(-0.222, -0.312, 0.458), (0.222, -0.312, 0.458), (0.222, -0.028, 0.458), (-0.222, -0.028, 0.458)], 0.004,
                'linen_cream', n=5, closed=True)

    pc.add('', body, plan_sym='stool')
    return pc


# ------------------------------------------------------------------------------------------ F7 TV cabinet
def tv_cabinet(ctx, x):
    """Georgian-style flame-mahogany cabinet 0.59 x 0.45 x 1.02 against the block face: two doors (open, burgundy
    lining, one shelf) over two long drawers, reeded quarter columns, bracket feet; a blank remote on top."""
    C, INL, X, Yf = 'mahogany', 'oak_light', 0.285, -0.44
    LN = M.solid('blue_bedroom_cab_lining', '#5B1F33', 0.7)
    FLAME = art('flame', None, 0.2)                          # flame-figured veneer, fills 0..1 UV once
    pc = Piece(ctx, 'blue_bedroom.tv_cabinet', x, 12.972, (0, 1))

    def stringing(mb, x0, x1, z0, z1, y):
        for a, b in (((x0, z0), (x1, z0 + 0.003)), ((x0, z1 - 0.003), (x1, z1)), ((x0, z0), (x0 + 0.003, z1)),
                     ((x1 - 0.003, z0), (x1, z1))):
            mb.box((a[0], y - 0.0008, a[1]), (b[0], y, b[1]), INL)

    def veneer(mb, x0, x1, z0, z1, y, uv=(0, 0, 1, 1)):
        """Flame panel inside the stringing, on the plane y (facing -y), showing the texture window uv."""
        u0, v0, u1, v1 = uv                                  # MB UVs = local coords: scale the frame, not the UVs
        mb.at(T(x0, y, z0) @ Matrix.Diagonal(((x1 - x0) / (u1 - u0), 1, (z1 - z0) / (v1 - v0), 1)) @ T(-u0, 0, -v0))
        mb.face([(u0, 0, v0), (u1, 0, v0), (u1, 0, v1), (u0, 0, v1)], FLAME, (0, -1, 0))
        mb.at()

    def carcass(mb):
        b = mb.box
        for sx in (-1, 1):
            for y in (Yf - 0.008, -0.07):                                                  # bracket feet
                b((sx * (X + 0.008), y, 0), (sx * (X - 0.07), y + 0.07, 0.07), C, bev=0.006)
            b((sx * X, Yf, 0.10), (sx * (X - 0.018), -0.01, 1.0), C, grain=2)
            reeded(mb, sx * X, sx * (X - 0.022), Yf, 0.10, 1.0, C, n=2)
        b((-X - 0.008, Yf - 0.008, 0.062), (X + 0.008, 0, 0.10), C, bev=0.005, grain=0)    # base moulding
        b((-X, -0.01, 0.10), (X, 0, 1.0), C, grain=2)
        b((-X, Yf, 0.10), (X, -0.01, 0.118), C)
        b((-X, Yf, 0.27), (X, Yf + 0.03, 0.285), C, grain=0)
        b((-X, Yf, 0.455), (X, -0.01, 0.475), C, grain=0)                                  # cupboard floor
        b((-X - 0.005, Yf - 0.005, 0.458), (X + 0.005, 0, 0.472), C, bev=0.003, grain=0)   # waist bead
        b((-X - 0.012, Yf - 0.012, 1.0), (X + 0.012, 0, 1.02), C, bev=0.004, grain=0)      # top
        mb.at(T(0.06, -0.21, 1.02) @ R('Z', 22))                                           # TV remote (blank)
        b((-0.022, -0.09, 0), (0.022, 0.09, 0.016), 'black_matt', bev=0.004)
        mb.at()

    def inner(mb):
        x = X - 0.019
        inward(mb, -x, x, Yf + 0.021, -0.011, 0.476, 0.999, LN, skip=('floor',))
        mb.face([(-x, Yf + 0.021, 0.476), (x, Yf + 0.021, 0.476), (x, -0.011, 0.476), (-x, -0.011, 0.476)], C, (0, 0, 1))
        mb.box((-x, Yf + 0.04, 0.72), (x, -0.011, 0.736), M.solid('blue_bedroom_cab_shelf', '#8A3A36', 0.5))

    pc.add('', carcass, plan_sym='cabinet', lm='static')
    pc.add('inner', inner, lm='dynamic')
    w = X - 0.023
    for k, sx in enumerate((-1, 1)):
        def door(mb, sx=sx):
            x0, x1 = (sx * w, sx * 0.001) if sx < 0 else (sx * 0.001, sx * w)
            mb.box((x0, Yf, 0.48), (x1, Yf + 0.02, 0.995), C, bev=0.002, grain=2)
            stringing(mb, x0 + 0.035, x1 - 0.035, 0.515, 0.96, Yf)
            veneer(mb, x0 + 0.038, x1 - 0.038, 0.518, 0.957, Yf - 0.0004)
            hx = sx * 0.028
            mb.box((hx - 0.007, Yf - 0.003, 0.725), (hx + 0.007, Yf, 0.775), BRASS, bev=0.002)
            mb.tube([(hx + 0.012 * math.cos(a), Yf - 0.008, 0.728 + 0.016 * math.sin(a))
                     for a in (math.pi * (1 + i / 6) for i in range(7))], 0.0025, BRASS, n=5, up=(0, 1, 0))
        d = pc.add(f'door.{k}', door, lm='dynamic')
        pc.hinge([d], f'door.{k}', 'Cabinet', (sx * w, Yf, 0), sx * 100)
    for k, (z0, z1) in enumerate(((0.12, 0.268), (0.287, 0.453))):
        def drw(mb, z0=z0, z1=z1):
            drawer(mb, -w, w, z0, z1, Yf, 0.40, C, (-0.15, 0.15), pull_w=0.06)
            stringing(mb, -w + 0.03, w - 0.03, z0 + 0.03, z1 - 0.03, Yf - 0.004)
            veneer(mb, -w + 0.033, w - 0.033, z0 + 0.033, z1 - 0.033, Yf - 0.0044, (0, 0.22, 1, 0.42))   # wide crop
        ob = pc.add(f'drawer.{k}', drw, lm='dynamic')
        pc.slide([ob], f'drawer.{k}', 'Drawer', (0, -0.30, 0))
    return pc

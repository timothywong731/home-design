"""Green bedroom furniture (spec/rooms/green_bedroom.md section 6): wardrobes, bed, nightstands, blanket chest,
bureau, chest of drawers, armchair + footstool, drum table, corner chair. Called by rooms/green_bedroom.py.

Every piece is built in its own local frame (props convention: back on y = 0, front faces -Y, +X to the
viewer's right, z = 0 on the room floor) and placed by `Piece`; moving parts are separate objects in the same
frame, tagged per blender/INTERACT.md with world points taken from the piece matrix.
"""
import math
import os
import random
from math import sin, cos, pi, radians, atan2
from mathutils import Matrix, Vector
from lib import interact as IX, materials as M, mouldings as mo, props as P

ROOM = 'green_bedroom'
FZ = 3.42                                           # floor level (house.json)
ART = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'textures', 'art'))
OAK, MH, MD = 'dark_oak_antique', 'oak_table', 'mahogany_dark'   # MH: dresser (mahogany_mid rendered too red)
Tr = Matrix.Translation


def Rx(deg):
    return Matrix.Rotation(radians(deg), 4, 'X')


def Rz(deg):
    return Matrix.Rotation(radians(deg), 4, 'Z')


def tex(name, size, rough=0.9):
    return M.image_mat('gb_' + name, os.path.join(ART, f'green_bedroom_{name}.jpg'), size_m=size, roughness=rough)


def solid(name, hx, rough=0.8, metallic=0.0):
    return M.solid('gb_' + name, hx, rough, metallic)


class Piece:
    """Local frame of one piece of furniture: origin (x, y) on the floor, front (-Y) turned toward `facing`."""

    def __init__(s, ctx, name, x, y, facing=(0, -1), z=0.0):
        s.ctx, s.name = ctx, f'{ROOM}.{name}'
        s.M = Tr((x, y, FZ + z)) @ Matrix.Rotation(atan2(facing[0], -facing[1]), 4, 'Z')

    def add(s, ob, sub=None, kind='furn', sym=None, lm=None, T=None):
        """ob: an MB (finished here) or an unlinked object given in the local frame (T = its local matrix)."""
        if isinstance(ob, mo.MB):
            ob = ob.finish(s.name + ('.' + sub if sub else ''))
        elif sub:
            ob.name = s.name + '.' + sub
        loc, rot, _ = (s.M @ T if T is not None else s.M).decompose()
        ob.location, ob.rotation_euler = loc, rot.to_euler()
        return s.ctx.add(ob, ROOM, kind, plan_sym=sym, lm=lm)

    def pt(s, p):
        return tuple(s.M @ Vector(p))

    def vec(s, v):
        return tuple(s.M.to_3x3() @ Vector(v))


def grid(mb, fn, nu, nv, mat, uv=None):
    """Smooth surface fn(u, v) -> (x, y, z), u, v in 0..1; uv(u, v) -> metres. Normal = d/du x d/dv."""
    V = [mb._vs([fn(i / nu, j / nv) for i in range(nu + 1)]) for j in range(nv + 1)]
    uv = uv or (lambda u, v: (u, v))
    mi = mb.mi(mat)
    for j in range(nv):
        for i in range(nu):
            mb._f([V[j][i], V[j][i + 1], V[j + 1][i + 1], V[j + 1][i]], mi,
                  [uv(i / nu, j / nv), uv((i + 1) / nu, j / nv), uv((i + 1) / nu, (j + 1) / nv), uv(i / nu, (j + 1) / nv)])


def knob(mb, x, y, z, r=0.014, mat=OAK, proj=0.022):
    """Turned knob on a front at local (x, y, z), pointing -Y."""
    M0 = mb.M.copy()
    mb.at(M0 @ Tr((x, y, z)) @ Rx(90))
    mb.lathe([(0, 0), (r * 0.45, 0), (r * 0.45, proj * 0.35), (r, proj * 0.6), (r * 0.8, proj * 0.92), (0, proj)], mat, 10)
    mb.at(M0)


def drawer_box(mb, x0, x1, y0, y1, z0, z1, mat='oak_light'):
    """Open-topped drawer box behind a front: x0..x1 wide, y0 (front) .. y1 (back)."""
    t = 0.008
    mb.box((x0, y0, z0), (x1, y1, z0 + t), mat)
    for a, b in ((x0, x0 + t), (x1 - t, x1)):
        mb.box((a, y0, z0), (b, y1, z1), mat)
    mb.box((x0, y1 - t, z0), (x1, y1, z1), mat)


# ------------------------------------------------------------------------------------------ wardrobes
CLOTHES = ['#3B4658', '#8C8478', '#D9D2C2', '#6E7F6A', '#5A3A3E', '#A9A39A', '#2F3136']


def _wardrobe_door(mb, x0, x1, zb, zt, yb, hinge_left, tassel):
    """Lay-on door, back face at y = yb, 22 mm thick: linenfold upper panel, carved rail at ~1.05, two fielded
    panels below; iron butterfly hinges on the hinge edge, drop ring on the meeting edge."""
    yp = yb - 0.016                                  # recessed panel plane
    yf = yb - 0.022                                  # frame face
    st, rl = 0.055, 0.065
    mb.box((x0, yp, zb), (x1, yb, zt), OAK, grain=2)
    for a in (x0, x1 - st):
        mb.box((a, yf, zb), (a + st, yp, zt), OAK, bev=0.002, grain=2)
    zc0, zc1 = 1.015, 1.09                           # carved rail
    zm = (zb + rl + zc0) / 2                         # rail between the two lower panels
    for a, b in ((zb, zb + rl), (zm - 0.03, zm + 0.03), (zc0, zc1), (zt - rl, zt)):
        mb.box((x0 + st, yf, a), (x1 - st, yp, b), OAK, bev=0.002, grain=0)
    for a, b in ((zb + rl, zm - 0.03), (zm + 0.03, zc0)):                      # fielded panels
        mb.box((x0 + st + 0.018, yp - 0.005, a + 0.018), (x1 - st - 0.018, yp, b - 0.018), OAK, bev=0.004, grain=2)
    a, b = x0 + st + 0.012, x1 - st - 0.012                                    # linenfold: four folds
    pw = (b - a) / 4
    za, zz = zc1 + 0.03, zt - rl - 0.03
    for k in range(4):
        xa = a + k * pw
        mb.box((xa + 0.004, yp - 0.004, za), (xa + pw - 0.004, yp, zz), OAK, bev=0.003, grain=2)
        for f in (0.28, 0.72):                       # two rolled ridges per fold, diving into the panel at the ends
            x = xa + pw * f
            mb.tube([(x, yp + 0.012, za), (x, yp - 0.003, za + 0.03), (x, yp - 0.003, zz - 0.03), (x, yp + 0.012, zz)],
                    0.009, OAK, n=8, up=(0, 1, 0))
    n = max(4, int((x1 - x0 - 2 * st) / 0.06))                                 # rosettes on the carved rail
    M0 = mb.M.copy()
    for k in range(n):
        cx = x0 + st + (k + 0.5) * (x1 - x0 - 2 * st) / n
        mb.at(M0 @ Tr((cx, yf, (zc0 + zc1) / 2)) @ Rx(90))
        mb.dome(0.024, 0.024, 0.008, OAK, segs=10, rings=2)
        mb.at(M0 @ Tr((cx, yf - 0.008, (zc0 + zc1) / 2)) @ Rx(90))
        mb.dome(0.009, 0.009, 0.005, OAK, segs=8, rings=2)
    mb.at(M0)
    xh, sg = (x0, 1) if hinge_left else (x1, -1)                               # butterfly hinges
    for z in (zb + 0.20, zt - 0.20):
        mb.box((xh, yf - 0.002, z - 0.02), (xh + sg * 0.035, yf, z + 0.02), 'cast_iron', bev=0.001)
    xm = x1 - 0.028 if hinge_left else x0 + 0.028                              # drop ring on the meeting stile
    mb.at(M0 @ Tr((xm, yf, 1.0)) @ Rx(90))
    mb.lathe([(0, 0), (0.013, 0), (0.011, 0.004), (0, 0.006)], 'cast_iron', 10)
    mb.at(M0)
    mb.tube([(xm + 0.016 * cos(t), yf - 0.006, 0.985 + 0.016 * sin(t)) for t in [i * pi / 5 for i in range(10)]],
            0.0025, 'cast_iron', n=5, closed=True, up=(0, 1, 0))
    if tassel:                                                                  # cream tassel on the key
        mb.at(M0 @ Tr((xm, yf - 0.008, 0.86)))
        mb.lathe([(0, 0), (0.008, 0.004), (0.011, 0.05), (0.006, 0.056), (0.004, 0.07), (0.002, 0.10), (0, 0.10)], 'linen_cream', 8)
        mb.at(M0)


def wardrobe(ctx, name, x, y, facing, w, d, h, degs=(-100, 100), shelf=None, n_clothes=12, label='Wardrobe'):
    pc = Piece(ctx, name, x, y, facing)
    hw, bw, t = w / 2, w / 2 - 0.02, 0.02
    yf = -(d - 0.045)                                # carcass front (the doors stand 22 mm proud of it)
    z0, z1 = 0.09, h - 0.06
    mb = mo.MB()
    for sx in (-1, 1):                               # bracket feet + recessed apron
        mb.box((sx * hw, yf - 0.02, 0), (sx * (hw - 0.15), 0, z0), OAK, bev=0.004)
    mb.box((-hw + 0.15, yf, 0.045), (hw - 0.15, 0, z0), OAK)
    mb.box((-hw, yf - 0.022, z0 - 0.012), (hw, 0, z0 + 0.012), OAK, bev=0.004, grain=0)       # base moulding
    mb.box((-bw + t, yf + 0.022, z0), (bw - t, -0.012, z0 + t), OAK)                          # bottom
    mb.box((-bw + t, yf + 0.022, z1 - t), (bw - t, -0.012, z1), OAK)                          # top
    mb.box((-bw + t, -0.012, z0), (bw - t, 0, z1), OAK)                                       # back
    for sx in (-1, 1):
        mb.box((sx * bw, yf + 0.022, z0), (sx * (bw - t), 0, z1), OAK, grain=2)               # sides
        mb.box((sx * bw, yf, z0), (sx * (bw - 0.045), yf + 0.022, z1), OAK, bev=0.002, grain=2)   # face stiles
    mb.box((-bw + 0.045, yf, z1 - 0.07), (bw - 0.045, yf + 0.022, z1), OAK, grain=0)          # top rail
    mb.box((-bw + 0.045, yf, z0), (bw - 0.045, yf + 0.022, z0 + 0.06), OAK, grain=0)          # bottom rail
    mb.box((-hw, yf - 0.03, z1), (hw, 0, h), OAK, bev=0.008, grain=0)                         # cornice
    mb.box((-hw + 0.008, yf - 0.022, z1 - 0.018), (hw - 0.008, 0, z1), OAK, bev=0.003, grain=0)
    zr = (shelf - 0.09) if shelf else z1 - 0.13
    if shelf:
        mb.box((-bw + t, yf + 0.03, shelf - 0.018), (bw - t, -0.012, shelf), OAK)
    mb.tube([(-bw + t, yf / 2, zr), (bw - t, yf / 2, zr)], 0.012, 'brass_antique', n=8)
    pc.add(mb, sym='wardrobe')

    cl = mo.MB()                                     # plain hanging garments, packed on the rail
    rnd = random.Random(len(name) * 7 + n_clothes)
    span = 2 * (bw - t) - 0.10
    yc, hw_g = yf / 2, min(0.20, -yf / 2 - 0.035)
    for k in range(n_clothes):
        cx = -span / 2 + span * (k + 0.5) / n_clothes + rnd.uniform(-0.012, 0.012)
        L = min(rnd.choice((0.68, 0.75, 0.82, 0.92, 1.02, 1.08)), zr - z0 - 0.12)
        th, flare = rnd.uniform(0.03, 0.085), rnd.uniform(-0.12, 0.05)          # thickness, hem flare / taper
        zs = zr - 0.045                                                           # shoulder line under the hanger

        def body(u, v, s, L=L, th=th, flare=flare, zs=zs):
            """u across the garment (0..1), v up from the hem (0..1); s = +1 front face, -1 back face."""
            z = zr - 0.02 - (L - 0.02) * (1 - v)
            w = hw_g * (1 + flare * (1 - v) - 0.07 * sin(pi * v) ** 2)            # waist, flare or taper to the hem
            if z > zs:                                                            # sloping shoulders up to the hook
                w *= max(0.12, 1 - (z - zs) / 0.03 * 0.88)
            y = w * (2 * u - 1) * s
            puff = th / 2 * sin(pi * u) ** 0.6 * min(1.0, v / 0.03, (1 - v) / 0.05)
            return (s * puff, y, z)
        cl.at(Tr((cx, yc, 0)) @ Rz(rnd.uniform(-10, 10)))
        mt = solid(f'cloth_{k % 7}', CLOTHES[(k * 3 + len(name)) % 7], 0.95)
        grid(cl, lambda u, v: body(u, v, 1), 6, 10, mt)
        grid(cl, lambda u, v: body(u, v, -1), 6, 10, mt)
        cl.at()
        cl.tube([(cx, yc, zr - 0.03), (cx, yc, zr + 0.016)], 0.002, 'chrome', n=4)
    pc.add(cl, 'clothes', kind='decor', lm='dynamic')

    xo = bw - 0.045 + 0.006                          # doors lap the stiles by 6 mm
    zb, zt = z0 + 0.054, z1 - 0.064
    for i, (a, b, left) in enumerate(((-xo, -0.0015, True), (0.0015, xo, False))):
        dm = mo.MB()
        _wardrobe_door(dm, a, b, zb, zt, yf, left, tassel=(i == 1))
        ob = pc.add(dm, f'door.{i}', lm='dynamic')
        IX.tag(ob, 'hinge', g=f'{pc.name}.door.{i}', label=label, p=pc.pt((a if left else b, yf, 0)), deg=degs[i])
    return pc


# ------------------------------------------------------------------------------------------ bed
def bed(ctx):
    """King divan against the east wall: local origin = centre of the headboard back on the floor."""
    pc = Piece(ctx, 'bed', 4.30, 2.29, (-1, 0))
    velvet = solid('velvet_bottle', '#1B3027', 0.75)
    mb = mo.MB()
    mb.box((-0.75, -2.10, 0.035), (0.75, -0.10, 0.38), velvet, bev=0.012)                     # divan base
    for sx in (-0.65, 0.65):
        for sy in (-0.25, -1.95):
            mb.box((sx - 0.02, sy - 0.02, 0), (sx + 0.02, sy + 0.02, 0.035), 'black_matt')    # castors
    mb.box((-0.82, -0.10, 0), (0.82, 0, 1.29), velvet, bev=0.012)                             # headboard panel
    # deep diamond buttoning on the face above the mattress
    x0, x1, zb, zt, y0 = -0.77, 0.77, 0.50, 1.24, -0.10
    px, pz = 0.20, 0.28                                                                       # button pitch / 2 rows

    def puff(x, z):
        a, b = x / px + (z - zb) / pz, x / px - (z - zb) / pz
        e = min(1.0, (x - x0) / 0.03, (x1 - x) / 0.03, (z - zb) / 0.03, (zt - z) / 0.03)
        return max(0.0, e) * (0.008 + 0.030 * abs(sin(pi * a) * sin(pi * b)) ** 0.45)

    grid(mb, lambda u, v: (x0 + (x1 - x0) * u, y0 - puff(x0 + (x1 - x0) * u, zb + (zt - zb) * v), zb + (zt - zb) * v),
         70, 34, velvet, lambda u, v: ((x1 - x0) * u, (zt - zb) * v))
    M0 = mb.M.copy()
    for ia in range(-12, 13):                                                                 # covered buttons
        for ib in range(-12, 13):
            bx, bz = (ia + ib) / 2 * px, zb + (ia - ib) / 2 * pz
            if x0 + 0.05 < bx < x1 - 0.05 and zb + 0.05 < bz < zt - 0.05:
                mb.at(M0 @ Tr((bx, y0 - 0.004, bz)) @ Rx(90))
                mb.dome(0.011, 0.011, 0.006, velvet, segs=6, rings=2)
    mb.at(M0)
    pc.add(mb, sym='bed')

    sheet = tex('sheet', (0.4, 0.4))
    mat = P.upholstered_seat(1.5, 2.0, 0.27, mat=sheet, crown=0.008, edge=0.05, name=pc.name + '.mattress')
    pc.add(mat, T=Tr((0, -1.10, 0.38)))

    duvet = P.two_sided(tex('duvet', (1.0, 1.0)))
    dv = mo.MB()                                     # neat duvet: flat on top, hanging down both sides, tucked at the foot
    a, hang, r, top, ya, yb = 0.775, 0.20, 0.05, 0.735, -0.70, -2.12

    def across(s):                                   # s = arc length from the centre line -> (x, drop)
        m = abs(s)
        if m <= a - r:
            return s, 0.0
        if m <= a - r + r * pi / 2:
            th = (m - (a - r)) / r
            return math.copysign(a - r + r * sin(th), s), r * (1 - cos(th))
        return math.copysign(a, s), r + m - (a - r + r * pi / 2)

    smax = a - r + r * pi / 2 + hang

    def fn(u, v):
        x, dx = across((1 - 2 * u) * smax)
        yy = ya + (yb - ya) * v
        dy = 0.0
        if v > 0.92:                                 # rolled over the foot end
            th = (v - 0.92) / 0.08 * pi / 2
            yy, dy = ya + (yb - ya) * 0.92 + 0.07 * sin(th), 0.07 * (1 - cos(th)) + 0.0
        if v < 0.04:                                 # turned-back hem at the pillow end
            dy = 0.03 * (1 - v / 0.04) ** 2
        quilt = 0.010 * sin(u * 9 * pi) * sin(v * 7 * pi) if dx == 0 else 0.0
        return x, yy, top - max(dx, dy) + quilt

    grid(dv, fn, 36, 30, duvet, lambda u, v: ((2 * u - 1) * smax, (yb - ya) * v))
    pc.add(dv, 'duvet')
    for i, (px_, flat) in enumerate(((-0.37, False), (0.37, False), (-0.37, True), (0.37, True))):
        c = P.cushion(0.70, 0.46, 0.15, mat=tex('duvet', (1.0, 1.0)), name=f'{pc.name}.pillow.{i}')
        pc.add(c, T=Tr((px_, -0.37, 0.655)) if flat else Tr((px_, -0.42, 0.79)) @ Rx(10))      # two neat stacks
    return pc


# ------------------------------------------------------------------------------------------ nightstands
def nightstand(ctx, name, yc):
    """French bombe bedside chest 0.36 x 0.30 x 0.70 against the east wall: three serpentine inlaid drawers
    on cabriole legs, gilt mounts, shaped breccia marble top."""
    pc = Piece(ctx, name, 4.28, yc, (-1, 0))
    w, d = 0.36, 0.29
    hw = w / 2
    KW, G = solid('kingwood', '#6A4A30', 0.35), 'gilt_bright'
    bulge = lambda x, amp=0.016: -d - amp * cos(pi * x / w)                 # serpentine front line
    xs = [-hw + w * i / 10 for i in range(11)]
    mb = mo.MB()
    z0, z1 = 0.33, 0.67
    for sx in (-1, 1):
        mb.box((sx * hw, -d + 0.01, z0), (sx * (hw - 0.014), 0, z1), KW, grain=2)             # sides
        mb.box((sx * hw, -d - 0.006, z0), (sx * (hw - 0.028), -d + 0.022, z1), KW, bev=0.004, grain=2)   # corner posts
        mb.box((sx * (hw + 0.002), -d - 0.009, 0.46), (sx * (hw - 0.02), -d + 0.012, 0.63), G, bev=0.004)   # leaf mounts
    mb.box((-hw, -0.01, z0), (hw, 0, z1), KW)                                                 # back
    for z in (z0, 0.447, 0.557, z1 - 0.012):
        mb.box((-hw + 0.014, -d + 0.01, z), (hw - 0.014, -0.01, z + 0.008 if z < z1 - 0.02 else z1), KW)   # dust boards
    apron = [(x, bulge(x, 0.012), z0) for x in xs] + [(x, -d + 0.03, z0) for x in reversed(xs)]
    mb.prism(apron, (0, 0, -0.035), KW)                                                       # shaped apron
    top = [(x * (1 + 0.03 / w), bulge(x) - 0.015, z1) for x in xs] + [(hw + 0.015, 0, z1), (-hw - 0.015, 0, z1)]
    mb.prism(top, (0, 0, 0.03), tex('marble', (0.30, 0.30), 0.2))                             # breccia marble top
    ob = pc.add(mb, sym='bedside')
    M.uv_box(ob)
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):                       # cabriole legs
        leg = P.turned_leg(0.345, 0.03, 'cabriole', top_block=0.02, mat=KW, out=(sx, sy), foot='pad')
        pc.add(leg, f'leg.{i}', T=Tr((sx * (hw - 0.016), -d / 2 + sy * (d / 2 - 0.016), 0)))
    fw, fh = w - 0.06, 0.098
    inl = tex('inlay', (fw, fh), 0.3)
    for k, z in enumerate((0.345, 0.455, 0.565)):
        dm = mo.MB()
        x0, x1 = -fw / 2, fw / 2
        fx = [x0 + fw * i / 8 for i in range(9)]
        dm.prism([(x, bulge(x) - 0.002, z) for x in fx] + [(x1, -d + 0.02, z), (x0, -d + 0.02, z)], (0, 0, fh), inl)
        drawer_box(dm, x0 + 0.004, x1 - 0.004, -d + 0.02, -0.03, z + 0.004, z + fh - 0.01)
        yb = bulge(0) - 0.002                                                                  # gilt swing handle
        dm.tube([(0.03 * cos(t), yb - 0.006, z + fh / 2 - 0.004 + 0.022 * sin(t)) for t in [pi + i * pi / 8 for i in range(9)]],
                0.0025, G, n=5, up=(0, 1, 0))
        for sx in (-1, 1):
            knob(dm, sx * 0.03, yb, z + fh / 2 - 0.004, 0.007, G, 0.008)
        ob = pc.add(dm, f'drawer.{k}', lm='dynamic')
        M.uv_box(ob, origin=pc.pt((x0, 0, z)))
        IX.tag(ob, 'slide', g=f'{pc.name}.drawer.{k}', label='Drawer', d=pc.vec((0, -0.18, 0)))
    return pc


# ------------------------------------------------------------------------------------------ blanket chest
def blanket_chest(ctx):
    """Panelled oak coffer 1.20 x 0.46 x 0.52 at the foot of the bed; the lid lifts on its back (east) edge."""
    pc = Piece(ctx, 'blanket_chest', 2.16, 2.29, (-1, 0))
    w, d, h = 1.20, 0.46, 0.52
    hw, zt = w / 2, h - 0.03
    mb = mo.MB()
    for sx in (-1, 1):
        for y in (-d, -0.05):
            mb.box((sx * hw, y, 0), (sx * (hw - 0.05), y + 0.05, zt), OAK, bev=0.003, grain=2)      # stile feet
    mb.box((-hw + 0.05, -d + 0.008, 0.07), (hw - 0.05, -d + 0.022, zt), OAK)                        # front
    mb.box((-hw + 0.05, -0.02, 0.07), (hw - 0.05, -0.006, zt), OAK)                                 # back
    for sx in (-1, 1):
        mb.box((sx * (hw - 0.008), -d + 0.05, 0.07), (sx * (hw - 0.022), -0.05, zt), OAK)           # ends
        for a, b in ((0.07, 0.13), (zt - 0.06, zt)):
            mb.box((sx * hw, -d + 0.05, a), (sx * (hw - 0.008), -0.05, b), OAK, bev=0.002, grain=1)
        mb.box((sx * (hw - 0.003), -d + 0.07, 0.15), (sx * (hw - 0.008), -0.07, zt - 0.08), OAK, bev=0.003)
    for a, b in ((0.07, 0.13), (zt - 0.06, zt)):
        mb.box((-hw + 0.05, -d, a), (hw - 0.05, -d + 0.008, b), OAK, bev=0.002, grain=0)            # front rails
    pw = (w - 0.10 - 3 * 0.05) / 4
    for k in range(4):
        xa = -hw + 0.05 + k * (pw + 0.05)
        if k:
            mb.box((xa - 0.05, -d, 0.13), (xa, -d + 0.008, zt - 0.06), OAK, bev=0.002, grain=2)     # muntins
        mb.box((xa + 0.018, -d + 0.003, 0.148), (xa + pw - 0.018, -d + 0.008, zt - 0.078), OAK, bev=0.004, grain=2)
    mb.box((-hw + 0.02, -d + 0.02, 0.09), (hw - 0.02, -0.02, 0.105), OAK)                           # floor
    pc.add(mb, sym='chest')
    li = mo.MB()                                     # folded linen
    for k, (cx, n, col) in enumerate(((-0.36, 4, '#E9E4D8'), (0.0, 3, '#B9C4B0'), (0.36, 5, '#D8D2C4'))):
        for j in range(n):
            li.box((cx - 0.15, -d + 0.07, 0.106 + j * 0.05), (cx + 0.15, -0.07, 0.152 + j * 0.05),
                   solid(f'linen_{k}', col, 0.95), bev=0.012)
    pc.add(li, 'linen', kind='decor', lm='dynamic')
    lid = mo.MB()
    lid.box((-hw - 0.02, -d - 0.02, zt), (hw + 0.02, 0, h), OAK, bev=0.007, grain=0)
    for k in range(4):                               # four sunk panels: raised framing round them
        xa = -hw + 0.05 + k * (pw + 0.05)
        lid.box((xa + 0.012, -d + 0.05, h), (xa + pw - 0.012, -0.06, h + 0.004), OAK, bev=0.004, grain=0)
    ob = pc.add(lid, 'lid', lm='dynamic')
    IX.tag(ob, 'hinge', g=pc.name + '.lid', label='Blanket chest', p=pc.pt((0, -0.004, zt)), a=pc.vec((1, 0, 0)), deg=-75)
    return pc


# ------------------------------------------------------------------------------------------ bureau
def bureau(ctx):
    """Jacobean-revival oak bureau on a stand, 0.76 x 0.45 x 1.02, back to the front wall (faces +Y)."""
    pc = Piece(ctx, 'bureau', 0.70, 1.012, (0, 1))
    w, d, h = 0.76, 0.45, 1.02
    hw, bw = w / 2, w / 2 - 0.012
    zs, zd = 0.36, 0.78                               # top of the stand, desk level
    run = 0.20                                        # plan depth of the fall
    mb = mo.MB()
    leg = [(0, 0), (0.030, 0), (0.036, 0.018), (0.030, 0.042), (0.020, 0.048)]                # bun foot
    bulb = [(0.020, 0.105), (0.024, 0.115), (0.016, 0.125), (0.034, 0.165), (0.037, 0.20), (0.030, 0.245),
            (0.016, 0.27), (0.024, 0.285), (0.020, 0.30)]
    for sx in (-1, 1):
        for y in (-0.04, -d + 0.04):
            M0 = Tr((sx * (hw - 0.04), y, 0))
            mb.at(M0)
            mb.lathe(leg + [(0.020, 0.05)], OAK, 12)
            mb.lathe(bulb, OAK, 12)
            mb.box((-0.028, -0.028, 0.048), (0.028, 0.028, 0.107), OAK, bev=0.003, grain=2)   # stretcher block
            mb.box((-0.028, -0.028, 0.298), (0.028, 0.028, zs - 0.012), OAK, bev=0.003, grain=2)
    mb.at()
    for y in (-0.04, -d + 0.04):
        mb.box((-hw + 0.06, y - 0.022, 0.06), (hw - 0.06, y + 0.022, 0.09), OAK, bev=0.003, grain=0)   # stretchers
    for sx in (-1, 1):
        mb.box((sx * (hw - 0.04) - 0.022, -d + 0.06, 0.06), (sx * (hw - 0.04) + 0.022, -0.06, 0.09), OAK, bev=0.003, grain=1)
    mb.box((-hw, -d, zs - 0.014), (hw, 0, zs + 0.012), OAK, bev=0.005, grain=0)               # waist moulding
    # drawer case
    for sx in (-1, 1):
        mb.box((sx * bw, -d + 0.012, zs), (sx * (bw - 0.018), 0, zd), OAK, grain=2)
    mb.box((-bw, -0.01, zs), (bw, 0, h), OAK)                                                 # back
    for z in (zs, 0.502, 0.642, zd - 0.006):
        mb.box((-bw + 0.018, -d + 0.012, z), (bw - 0.018, -0.01, z + 0.008), OAK)             # rails / desk floor
    # desk section: sloped cheeks, top, pigeonholes
    side = [(0, zd), (-d + 0.012, zd), (-d + 0.012, zd + 0.012), (-d + run + 0.012, h - 0.02), (0, h - 0.02)]
    for sx in (-1, 1):
        mb.prism([(sx * bw, a, b) for a, b in side], (-sx * 0.018, 0, 0), OAK)
    mb.box((-hw, -d + run, h - 0.022), (hw, 0, h), OAK, bev=0.004, grain=0)                   # top
    mb.box((-bw + 0.018, -0.15, 0.862), (bw - 0.018, -0.01, 0.87), OAK)                       # pigeonhole shelf
    for k in range(7):
        xk = -bw + 0.018 + (2 * bw - 0.036) * k / 6
        mb.box((xk - 0.004, -0.15, 0.87), (xk + 0.004, -0.01, h - 0.022), OAK)
    for k in range(3):                                                                        # small inner drawers
        xa = -bw + 0.022 + (2 * bw - 0.044) * k / 3
        xb = xa + (2 * bw - 0.044) / 3 - 0.006
        mb.box((xa, -0.155, zd + 0.006), (xb, -0.14, 0.858), OAK, bev=0.002, grain=0)
        knob(mb, (xa + xb) / 2, -0.155, zd + 0.045, 0.007, 'brass_antique', 0.01)
    mb.box((-bw + 0.018, -d + 0.02, zd + 0.002), (bw - 0.018, -0.16, zd + 0.0035), solid('leather', '#4E4234', 0.5))
    pc.add(mb, sym='bureau')

    # three long drawers with geometric moulded fronts and two turned knobs; the top one sits between the lopers
    for k, (za, zb) in enumerate(((0.371, 0.499), (0.513, 0.639), (0.653, 0.771))):
        x0 = -bw + 0.02 + (0.03 if k == 2 else 0.0)
        x1 = -x0
        dm = mo.MB()
        dm.box((x0, -d, za), (x1, -d + 0.02, zb), OAK, bev=0.002, grain=0)
        zc = (za + zb) / 2
        for sx in (-1, 1):                           # mitred geometric mouldings: two long hexagons + centre lozenge
            cx = sx * (x1 - x0) * 0.27
            hexa = [(cx - 0.11, zc), (cx - 0.085, zc + 0.04), (cx + 0.085, zc + 0.04), (cx + 0.11, zc),
                    (cx + 0.085, zc - 0.04), (cx - 0.085, zc - 0.04)]
            for i in range(6):
                (ax, az), (bx, bz) = hexa[i], hexa[(i + 1) % 6]
                dm.tube([(ax, -d - 0.004, az), (bx, -d - 0.004, bz)], 0.006, OAK, n=4, up=(0, 1, 0))
            knob(dm, cx, -d, zc, 0.015, OAK, 0.024)
        dm.prism([(0, -d, zc + 0.035), (0.03, -d, zc), (0, -d, zc - 0.035), (-0.03, -d, zc)], (0, -0.006, 0), OAK)
        drawer_box(dm, x0 + 0.006, x1 - 0.006, -d + 0.02, -0.03, za + 0.004, zb - 0.012)
        ob = pc.add(dm, f'drawer.{k}', lm='dynamic')
        IX.tag(ob, 'slide', g=f'{pc.name}.drawer.{k}', label='Drawer', d=pc.vec((0, -0.25, 0)))

    # fall front, hinged on its bottom edge; two lopers slide out under it
    slope = math.hypot(run, h - 0.02 - zd - 0.012)
    ang = math.degrees(atan2(h - 0.02 - zd - 0.012, run))
    fm = mo.MB()
    fm.at(Tr((0, -d + 0.012, zd + 0.012)) @ Rx(ang))                 # local Y' up the slope, Z' out of the face
    fm.box((-bw, 0, -0.016), (bw, slope, 0.002), OAK, bev=0.002, grain=0)
    hx, hy = bw - 0.07, slope / 2
    oct_ = [(-hx, hy), (-hx + 0.05, hy + 0.085), (hx - 0.05, hy + 0.085), (hx, hy), (hx - 0.05, hy - 0.085), (-hx + 0.05, hy - 0.085)]
    for i in range(6):                               # mitred geometric panel moulding
        (ax, ay), (bx, by) = oct_[i], oct_[(i + 1) % 6]
        fm.tube([(ax, ay, 0.006), (bx, by, 0.006)], 0.007, OAK, n=4, up=(0, 0, 1))
    fm.box((-bw + 0.05, 0.03, -0.0175), (bw - 0.05, slope - 0.03, -0.016), solid('leather', '#4E4234', 0.5))   # writing leather
    M0 = fm.M.copy()
    fm.at(M0 @ Tr((0, slope - 0.035, 0.002)))
    fm.lathe([(0, 0), (0.012, 0), (0.010, 0.003), (0, 0.004)], 'brass_antique', 10)           # escutcheon
    fm.at(M0 @ Tr((0, slope - 0.045, 0.008)) @ Rx(90))                                        # key tassel lying on the slope
    fm.lathe([(0, 0), (0.007, 0.004), (0.010, 0.05), (0.005, 0.056), (0.003, 0.075), (0, 0.075)], 'linen_cream', 8)
    fall = pc.add(fm, 'fall', lm='dynamic')
    g = pc.name + '.fall'
    IX.tag(fall, 'hinge', g=g, label='Bureau', p=pc.pt((0, -d + 0.012, zd + 0.012)), a=pc.vec((1, 0, 0)), deg=180 - ang)
    for i, sx in enumerate((-1, 1)):
        lm_ = mo.MB()
        xa = sx * (bw - 0.02) - (0.026 if sx > 0 else 0)
        lm_.box((xa, -d, 0.655), (xa + 0.026, -d + 0.34, 0.769), OAK, bev=0.002, grain=1)
        knob(lm_, xa + 0.013, -d, 0.712, 0.006, 'brass_antique', 0.01)
        ob = pc.add(lm_, f'loper.{i}', lm='dynamic')
        IX.tag(ob, 'slide', g=g, label='Bureau', d=pc.vec((0, -0.25, 0)))
    return pc


# ------------------------------------------------------------------------------------------ chest of drawers
def _batwing(mb, x, y, z, s=1.0):
    """Polished-brass bat-wing back-plate with a bail handle on a front at y, facing -Y."""
    wing = [(-0.038, 0.0), (-0.03, 0.016), (-0.014, 0.012), (0, 0.022), (0.014, 0.012), (0.03, 0.016), (0.038, 0.0),
            (0.028, -0.012), (0.012, -0.010), (0, -0.02), (-0.012, -0.010), (-0.028, -0.012)]
    mb.prism([(x + a * s, y, z + b * s) for a, b in wing], (0, -0.002, 0), 'brass')
    mb.tube([(x + 0.026 * s * cos(t), y - 0.010, z + 0.004 + 0.020 * s * sin(t)) for t in [pi + i * pi / 8 for i in range(9)]],
            0.003, 'brass', n=5, up=(0, 1, 0))
    for sx in (-1, 1):
        knob(mb, x + sx * 0.026 * s, y - 0.002, z + 0.004, 0.005, 'brass', 0.009)


def dresser(ctx):
    """American-colonial block-front chest of drawers 1.80 x 0.50 x 0.86 under the TV (west wall, faces +X)."""
    pc = Piece(ctx, 'dresser', -0.625, 2.45, (1, 0))
    w, d, h = 1.80, 0.495, 0.86
    hw = w / 2
    xb = 0.30                                         # half width of the recessed centre bay
    mb = mo.MB()
    for sx in (-1, 1):                               # ogee bracket feet
        for y0, y1 in ((-d, -d + 0.13), (-0.10, 0)):
            mb.box((sx * hw, y0, 0), (sx * (hw - 0.14), y1, 0.10), MH, bev=0.012)
    mb.box((-hw, -d, 0.095), (hw, 0, 0.125), MH, bev=0.006, grain=0)                          # base moulding
    mb.box((-hw - 0.012, -d - 0.018, h - 0.03), (hw + 0.012, 0, h), MH, bev=0.007, grain=0)   # top
    mb.box((-hw + 0.01, -0.012, 0.125), (hw - 0.01, 0, h - 0.03), MH)                         # back
    for x in (-hw + 0.01, -xb - 0.01, xb - 0.01, hw - 0.03):
        mb.box((x, -d + 0.022, 0.125), (x + 0.02, -0.012, h - 0.03), MH, grain=2)             # sides and bay divisions
    rows = ((0.137, 0.367), (0.379, 0.609), (0.621, 0.818))
    for z in (0.125, 0.367, 0.609, 0.818):
        mb.box((-hw + 0.01, -d + 0.022, z), (hw - 0.01, -0.012, z + 0.012), MH)               # rails / dust boards
    pc.add(mb, sym='chest')
    bays = ((-hw + 0.032, -xb - 0.012, 0.0), (-xb + 0.012, xb - 0.012, 0.022), (xb + 0.012, hw - 0.032, 0.0))
    n = 0
    for bi, (x0, x1, back) in enumerate(bays):
        yf = -d + back                               # outer bays stand 22 mm proud of the centre one (block front)
        for ri, (za, zb) in enumerate(rows):
            dm = mo.MB()
            dm.box((x0, yf, za), (x1, yf + 0.022, zb), MH, bev=0.004, grain=0)
            dm.box((x0 + 0.03, yf - 0.006, za + 0.025), (x1 - 0.03, yf, zb - 0.025), MH, bev=0.006, grain=0)   # blocked field
            cx, cz = (x0 + x1) / 2, (za + zb) / 2
            M0 = dm.M.copy()
            if ri == 2 and bi != 1:                  # carved fan on the outer top drawers
                dm.at(M0 @ Tr((cx, yf - 0.006, za + 0.04)) @ Rx(90))
                dm.lathe([(0, 0), (0.105, 0), (0.095, 0.010), (0, 0.016)], MH, 14, ell=(1.0, 1.0), a0=0, a1=pi)
                dm.at(M0)
                for i in range(1, 14, 2):
                    t = pi * i / 14
                    dm.tube([(cx + 0.012 * cos(t), yf - 0.021, za + 0.04 + 0.012 * sin(t)),
                             (cx + 0.098 * cos(t), yf - 0.016, za + 0.04 + 0.098 * sin(t))], 0.004, MH, n=4, up=(0, 1, 0))
                for sx in (-1, 1):
                    _batwing(dm, cx + sx * (x1 - x0) * 0.36, yf - 0.006, cz, 0.8)
            elif ri == 2:                            # arched panel on the centre top drawer
                arch = [(cx - 0.11, za + 0.03), (cx + 0.11, za + 0.03)] + \
                       [(cx + 0.11 * cos(t), za + 0.09 + 0.07 * sin(t)) for t in [i * pi / 8 for i in range(9)]]
                dm.prism([(a, yf - 0.006, b) for a, b in arch], (0, -0.005, 0), MH)
                _batwing(dm, cx, yf - 0.011, cz - 0.01)
            else:
                for sx in (-1, 1):
                    _batwing(dm, cx + sx * (x1 - x0) * 0.27, yf - 0.006, cz)
            drawer_box(dm, x0 + 0.008, x1 - 0.008, yf + 0.022, -0.03, za + 0.004, zb - 0.02)
            ob = pc.add(dm, f'drawer.{n}', lm='dynamic')
            IX.tag(ob, 'slide', g=f'{pc.name}.drawer.{n}', label='Drawer', d=pc.vec((0, -0.30, 0)))
            n += 1
    return pc


# ------------------------------------------------------------------------------------------ bay seating
def armchair(ctx, x, y, facing):
    """c. 1920 mahogany show-wood armchair 0.68 x 0.75, seat 0.42, back 0.95; local origin = footprint centre."""
    pc = Piece(ctx, 'armchair', x, y, facing)
    TP = tex('tapestry', (0.45, 0.45), 0.95)
    mb = mo.MB()
    for sx in (-1, 1):
        back = [(0.375, 0), (0.33, 0), (0.30, 0.30), (0.335, 0.93), (0.375, 0.93), (0.345, 0.30)]   # raked back leg / post
        mb.prism([(sx * 0.34, a, b) for a, b in back], (-sx * 0.05, 0, 0), MD)
        mb.box((sx * 0.34, -0.345, 0.235), (sx * 0.29, 0.34, 0.315), MD, bev=0.004, grain=1)        # side seat rails
        mb.prism([(sx * x, -0.33, z) for x, z in ((0.265, 0.315), (0.335, 0.315), (0.372, 0.585), (0.292, 0.585))],
                 (0, 0.64, 0), TP)                                                                  # arm panel splayed outward
        arm = [(-0.375, 0.30), (-0.375, 0.50), (-0.34, 0.60), (0.32, 0.64), (0.32, 0.60), (-0.31, 0.565), (-0.33, 0.50), (-0.335, 0.30)]
        mb.prism([(sx * 0.385, a, b) for a, b in arm], (-sx * 0.085, 0, 0), MD)                     # show-wood arm sweeping down
    mb.box((-0.29, -0.345, 0.235), (0.29, -0.30, 0.315), MD, bev=0.004, grain=0)                    # front rail
    mb.prism([(-0.20, -0.347, 0.235), (0.20, -0.347, 0.235), (0.12, -0.347, 0.20), (0, -0.347, 0.215), (-0.12, -0.347, 0.20)],
             (0, 0.03, 0), MD)                                                                      # carved apron
    mb.box((-0.29, 0.30, 0.235), (0.29, 0.345, 0.315), MD, bev=0.004, grain=0)
    Tb = Tr((0, 0.318, 0.675)) @ Rx(82)                                                             # back plane
    mb.at(Tb)
    mb.box((-0.29, -0.25, -0.03), (0.29, 0.25, 0.0), TP, bev=0.006)                                 # outside back
    xs = [-0.31 + 0.62 * i / 16 for i in range(17)]                                                  # shaped top rail:
    ytop = [0.30 + 0.045 * (abs(x) / 0.31) ** 4 + 0.03 * max(0.0, 1 - abs(x) / 0.09) for x in xs]     # raised ears, centre crest
    mb.prism([(x, 0.25, -0.04) for x in xs] + [(x, y, -0.04) for x, y in zip(reversed(xs), reversed(ytop))], (0, 0, 0.052), MD)
    mb.at()
    pc.add(mb, sym='armchair')
    seat = P.upholstered_seat(0.53, 0.62, 0.115, mat=TP, gimp='linen_cream', name=pc.name + '.seat')
    pc.add(seat, T=Tr((0, -0.02, 0.31)))
    pad = P.upholstered_seat(0.52, 0.47, 0.06, mat=TP, gimp='linen_cream', name=pc.name + '.back')
    pc.add(pad, T=Tb)
    for i, sx in enumerate((-1, 1)):                                                                # ball-and-claw front legs
        leg = P.turned_leg(0.30, 0.06, 'cabriole', top_block=0.07, mat=MD, out=(sx, -1), foot='claw')
        pc.add(leg, f'leg.{i}', T=Tr((sx * 0.305, -0.315, 0)))

    # footstool stored under the seat (top 0.19, clear of the apron): slides out toward the room
    R, zb, zt = 0.21, 0.12, 0.19
    rad = lambda a: R * (0.91 + 0.09 * cos(6 * a))                  # shaped (serpentine) hexagon
    ring = lambda s, z: [(rad(2 * pi * i / 36) * s * cos(2 * pi * i / 36), rad(2 * pi * i / 36) * s * sin(2 * pi * i / 36), z)
                         for i in range(36)]
    st = mo.MB()
    st.prism(ring(0.99, 0.07), (0, 0, zb - 0.07), MD)                # shaped apron rail
    st.tube(ring(1.0, zb), 0.005, 'linen_cream', n=5, closed=True, up=(0, 0, 1))      # gimp at the pad edge
    sv = lambda v: 1 - 0.99 * v                                      # radial factor: rim (v 0) to centre (v 1)
    grid(st, lambda u, v: (rad(2 * pi * u) * sv(v) * cos(2 * pi * u), rad(2 * pi * u) * sv(v) * sin(2 * pi * u),
                           zb + (zt - zb) * (1 - sv(v) ** 6) ** 0.5),
         36, 8, tex('needlepoint', None, 0.95),
         lambda u, v: (0.5 + 0.5 * sv(v) * rad(2 * pi * u) / R * cos(2 * pi * u), 0.5 + 0.5 * sv(v) * rad(2 * pi * u) / R * sin(2 * pi * u)))
    objs = [pc.add(st, 'footstool', sym='stool', lm='dynamic', T=Tr((0, -0.03, 0)))]
    for k in range(6):                                               # short carved cabriole feet at the corners
        a = 2 * pi * k / 6
        leg = P.turned_leg(0.075, 0.028, 'cabriole', top_block=0.015, mat=MD, out=(round(cos(a), 3), round(sin(a), 3)), foot='pad')
        objs.append(pc.add(leg, f'footstool.foot.{k}', lm='dynamic', T=Tr((0.84 * R * cos(a), -0.03 + 0.84 * R * sin(a), 0))))
    IX.tag_many(objs, 'slide', g=pc.name + '.footstool', label='Footstool', d=pc.vec((0, -0.50, 0)))
    return pc


def drum_table(ctx, x, y):
    """Mahogany octagonal drum table, dia 0.55 x 0.55 high: green gilt-tooled leather top, baluster pedestal,
    three sabre legs with brass caps."""
    pc = Piece(ctx, 'drum_table', x, y)
    mb = mo.MB()
    octa = lambda r, z: [(r * cos(pi / 8 + i * pi / 4), r * sin(pi / 8 + i * pi / 4), z) for i in range(8)]
    R = 0.275 / cos(pi / 8)
    mb.prism(octa(R, 0.525), (0, 0, 0.025), MD)                                # top board
    mb.prism(octa(R - 0.02, 0.455), (0, 0, 0.07), MD)                          # frieze
    mb.prism(octa(R - 0.045, 0.5502), (0, 0, 0.0015), solid('leather_top', '#2C4034', 0.6))
    for i in range(8):                                                         # gilt tooling line
        a, b = octa(R - 0.065, 0.5522)[i], octa(R - 0.065, 0.5522)[(i + 1) % 8]
        mb.tube([a, b], 0.0012, 'gilt_bright', n=3)
    mb.lathe([(0, 0.17), (0.045, 0.17), (0.05, 0.19), (0.03, 0.215), (0.024, 0.25), (0.04, 0.30), (0.047, 0.34), (0.03, 0.40),
              (0.026, 0.43), (0.06, 0.455), (0, 0.455)], MD, 14)               # baluster pedestal
    leg = [(0.03, 0.20), (0.03, 0.14), (0.13, 0.05), (0.25, 0.012), (0.27, 0.012), (0.27, 0.035), (0.15, 0.085), (0.07, 0.17), (0.05, 0.20)]
    cap = [(0.235, 0.0), (0.275, 0.0), (0.275, 0.036), (0.235, 0.045)]
    for k in range(3):
        mb.at(Rz(90 + k * 120))
        mb.prism([(r, -0.017, z) for r, z in leg], (0, 0.034, 0), MD)
        mb.prism([(r, -0.019, z) for r, z in cap], (0, 0.038, 0), 'brass')
    mb.at()
    pc.add(mb, sym='table_round')
    return pc


def corner_chair(ctx, x, y):
    """Edwardian mahogany corner chair: seat square to the room, curved top rail over the south and west sides
    (local +Y / +X), spindle panels, drop-in tapestry seat, X stretcher."""
    pc = Piece(ctx, 'corner_chair', x, y, (0, 1))
    mb = mo.MB()
    a = 0.20
    turn = [(0.016, 0.0), (0.02, 0.03), (0.014, 0.06), (0.019, 0.20), (0.014, 0.33), (0.02, 0.36)]
    up = [(0.02, 0.45), (0.014, 0.47), (0.019, 0.58), (0.012, 0.70), (0.016, 0.735)]
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        mb.at(Tr((sx * a, sy * a, 0)))
        mb.lathe([(0, 0)] + turn, MD, 10)
        mb.box((-0.022, -0.022, 0.36), (0.022, 0.022, 0.45), MD, bev=0.003, grain=2)
        if (sx, sy) != (-1, -1):
            mb.lathe(up, MD, 10)
    mb.at()
    for s in (-1, 1):                                # seat rails and X stretcher
        mb.box((-a, s * a - 0.018, 0.385), (a, s * a + 0.018, 0.445), MD, bev=0.003, grain=0)
        mb.box((s * a - 0.018, -a, 0.385), (s * a + 0.018, a, 0.445), MD, bev=0.003, grain=1)
        mb.tube([(-a, -s * a, 0.16), (a, s * a, 0.16)], 0.011, MD, n=6)
    r = a * math.sqrt(2)
    arc = [(r * cos(radians(t)), r * sin(radians(t)), 0.735) for t in range(135, -46, -15)]
    rail = [(-0.022, 0), (0.022, 0), (0.022, 0.04), (0.012, 0.05), (-0.012, 0.05), (-0.022, 0.04)]
    mb.sweep(rail + rail[:1], arc, MD)
    mb.at(Tr((a, a, 0.775)) @ Rz(-45))
    mb.box((-0.11, -0.014, 0), (0.11, 0.014, 0.045), MD, bev=0.012, grain=0)                  # raised cresting
    mb.at()
    for t in list(range(120, 59, -15)) + list(range(30, -31, -15)):                           # slim spindles
        px_, py_ = r * cos(radians(t)), r * sin(radians(t))
        fx, fy = (px_ * a / py_, a) if t > 45 else (a, py_ * a / px_)
        mb.tube([(fx, fy, 0.445), (px_, py_, 0.737)], 0.006, MD, n=5)
    pc.add(mb, sym='chair')
    seat = P.upholstered_seat(0.37, 0.37, 0.05, mat=tex('tapestry', (0.45, 0.45), 0.95), name=pc.name + '.seat')
    pc.add(seat, T=Tr((0, 0, 0.42)))
    return pc

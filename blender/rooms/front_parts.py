"""Forecourt parts (spec/rooms/front.md 5-8, spec/phase2/front_elevation.md 5): timber troughs with bellflowers on
the west wall, the flag, bins, doorbell, outdoor socket, access covers, the lamp column and the street tree.
Every function returns unlinked objects in WORLD coordinates unless it says otherwise."""
import math
import os
import random

import bpy
import numpy as np
from mathutils import Matrix, Vector

from lib import materials as M, mouldings as mo, props as P

ART = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'textures', 'art')
TAU = 2 * math.pi


# ------------------------------------------------------------------------------------------------ helpers
def rrect(w, d, r, n=3, cx=0.0, cy=0.0):
    """Rounded rectangle w (x) by d (y), counter-clockwise, 4 * (n + 1) points."""
    pts = []
    for qx, qy, a0 in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cx + qx * (w / 2 - r) + r * math.cos(a), cy + qy * (d / 2 - r) + r * math.sin(a)))
    return pts


def loft(mb, rings, mat, caps=(True, True)):
    """rings = [(z, [(x, y), ...]), ...] bottom to top, same point count each, counter-clockwise seen from +Z."""
    V = [mb._vs([(x, y, z) for x, y in pts]) for z, pts in rings]
    mi, n = mb.mi(mat), len(V[0])
    for a, b in zip(V, V[1:]):
        for k in range(n):
            mb._f([a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]], mi)
    if caps[0]:
        mb._f(V[0][::-1], mi)
    if caps[1]:
        mb._f(V[-1], mi)


def _frame(n):
    """Two unit vectors spanning the plane normal to n."""
    n = Vector(n).normalized()
    a = n.cross(Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((1, 0, 0))).normalized()
    return a, n.cross(a)


def _plastic(name, hx, rough=0.45):
    return M.solid(name, hx, rough)


# ------------------------------------------------------------------------------------------------ wall planters
def planter(ctx):
    """-> (troughs, foliage): rough-sawn timber troughs along the top of the west wall, filled end to end with
    trailing bellflower (leaves and flowers are real low-poly geometry: the path runs 0.5 m from it)."""
    b = next(b for b in ctx.spec['exterior']['boundaries'] if b['id'] == 'front_wall_w')
    (xc, ya), (_, yb) = b['line']
    top = b['baseZ'] + b['height']
    # pier end: 10 mm clear of the pier cap's 35 mm overhang; house end: stops just short of the downpipe
    # (facade.downpipe.2, y -0.233 .. -0.168) that stands in the corner against the brick face
    y0, y1 = min(ya, yb) + 0.045, max(ya, yb) - 0.135
    hw, th = b['thickness'] / 2 + 0.025, 0.018                     # boards stand 25 mm proud of the brick
    z0, z1 = top - 0.07, top + 0.18                                # the side boards lap 70 mm over the soldier course
    rnd = random.Random(5)
    mb = mo.MB()
    n = round((y1 - y0) / 0.095)
    for k in range(n):
        ya_, yb_ = y0 + (y1 - y0) * k / n, y0 + (y1 - y0) * (k + 1) / n
        for sx in (1, -1):
            p = rnd.uniform(0, 0.004)
            xa_, xb_ = sorted((xc + sx * (hw + p), xc + sx * (hw + p - th)))
            mb.box((xa_, ya_ + 0.0015, z0 - rnd.uniform(0, 0.012)), (xb_, yb_ - 0.0015, z1 + rnd.uniform(-0.014, 0.006)),
                   'timber_box_dark', grain=2)
    for k in range(5):                                             # ends of the four boxes
        y = y0 + (y1 - y0) * k / 4
        ya_, yb_ = (y, y + th) if k == 0 else (y - th, y) if k == 4 else (y - th, y + th)
        mb.box((xc - hw + th, ya_, z0), (xc + hw - th, yb_, z1 - 0.004), 'timber_box_dark', grain=2)
    mb.box((xc - hw + th, y0 + th, z1 - 0.06), (xc + hw - th, y1 - th, z1 - 0.045), P.mat('soil'))
    troughs = mb.finish('front.planter')

    # --- cushion: section = an arc from the low edge on our side (-35 deg) over the top to the low edge on the far side
    zr = z1 - 0.01
    A0, A1 = math.radians(-8), math.radians(188)

    def surf(y, a, grow=1.0):
        e = math.sqrt(max(0.0, min(1.0, (y1 - y + 0.01) / 0.14)))
        p = math.sqrt(max(0.0, min(1.0, (y - y0 + 0.01) / 0.5)))    # pier end: low and narrow over the last 0.5 m
        n = grow * (1 + 0.09 * math.sin(9 * y + 4 * a) + 0.06 * math.sin(17 * y - 3 * a + 1))
        fx, fz = (0.55 + 0.45 * e) * (0.75 + 0.25 * p) * n, (0.55 + 0.45 * e) * (0.22 + 0.78 * p) * n
        rx = (hw + 0.045 + 0.03 * math.sin(2.1 * y) + 0.02 * math.sin(5.3 * y + 1)) * fx
        rz = (0.16 + 0.03 * math.sin(3.3 * y + 2) + 0.02 * math.sin(7.7 * y)) * fz
        x = xc + rx * math.cos(a)
        if y > y1 - 0.75:                                          # trimmed back beside the street door: the open
            x = min(x, xc + hw + 0.005)                            # west leaf stands just off the board face
        return Vector((x, y, zr + rz * math.sin(a))), Vector((math.cos(a) * rz, 0, math.sin(a) * rx)).normalized()

    fb = mo.MB()
    fb._soft = 1
    dark = M.solid('front_foliage_shade', '#3E5A2F', 0.95)
    ny, na = round((y1 - y0) / 0.07), 12
    rows = [fb._vs([surf(y0 + (y1 - y0) * i / ny, A0 + (A1 - A0) * j / na, 0.9)[0] for j in range(na + 1)]) for i in range(ny + 1)]
    mi = fb.mi(dark)
    for r0, r1 in zip(rows, rows[1:]):
        for j in range(na):
            fb._f([r0[j], r1[j], r1[j + 1], r0[j + 1]], mi)
    fb._f(rows[0], mi)
    fb._f(rows[-1][::-1], mi)
    fb._soft = 0

    leaf = [fb.mi(P.two_sided(M.solid('front_leaf_%d' % k, hx, 0.55))) for k, hx in enumerate(('#6E9450', '#87A963', '#567B3F'))]
    petal = [fb.mi(P.two_sided(M.solid('front_bellflower_%d' % k, hx, 0.6))) for k, hx in enumerate(('#6B5BB5', '#8274CC'))]
    rim = [(math.cos(TAU * k / 5), math.sin(TAU * k / 5) * 0.85) for k in range(5)]
    for _ in range(5200):                                          # leaves: small round-ish pentagons on the cushion
        p, nrm = surf(rnd.uniform(y0, y1), rnd.uniform(A0, A1), rnd.uniform(0.93, 1.07))
        nrm = (nrm + Vector((rnd.uniform(-.6, .6), rnd.uniform(-.6, .6), rnd.uniform(-.3, .6)))).normalized()
        u, v = _frame(nrm)
        s, r = rnd.uniform(0.010, 0.016), rnd.uniform(0, TAU)
        u, v = u * math.cos(r) + v * math.sin(r), v * math.cos(r) - u * math.sin(r)
        fb._f(fb._vs([p + (u * a + v * b) * s for a, b in rim]), leaf[rnd.choices((0, 1, 2), (55, 25, 20))[0]])
    for _ in range(900):                                           # flowers: five-pointed stars, densest on top
        a = rnd.gauss(math.pi / 2, 0.6) if rnd.random() < 0.55 else rnd.uniform(A0, A1)
        p, nrm = surf(rnd.uniform(y0 + 0.02, y1 - 0.02), min(A1, max(A0, a)), rnd.uniform(1.08, 1.16))
        nrm = (nrm + Vector((rnd.uniform(-.35, .35), rnd.uniform(-.35, .35), rnd.uniform(-.1, .4)))).normalized()
        u, v = _frame(nrm)
        ro, r0 = rnd.uniform(0.011, 0.015), rnd.uniform(0, TAU)
        ring = fb._vs([p + (u * math.cos(r0 + TAU * k / 10) + v * math.sin(r0 + TAU * k / 10)) * (ro if k % 2 == 0 else ro * 0.42)
                       + nrm * (0.004 if k % 2 == 0 else 0) for k in range(10)])
        c = fb._vs([p - nrm * 0.003])[0]
        mi = petal[rnd.random() < 0.3]
        for k in range(0, 10, 2):
            fb._f([c, ring[k - 1], ring[k], ring[(k + 1) % 10]], mi)
    return troughs, fb.finish('front.planter.bellflower', sharp_deg=60)


# ------------------------------------------------------------------------------------------------ flag
def flag_texture(path, w=768, h=460):
    """Union Flag, 3:5, in the slightly sun-faded colours of front.md 7.1 (drawn, no reference pixels)."""
    ss = 3
    v, u = np.mgrid[0:h * ss, 0:w * ss]
    u, v = (u + 0.5) / (w * ss) * 50 - 25, (v + 0.5) / (h * ss) * 30 - 15       # flag units, v up, hoist at u = -25
    red, blue, white = (np.array([int(c[i:i + 2], 16) / 255 for i in (1, 3, 5)]) for c in ('#C23B3A', '#2B3A78', '#F0EFEC'))
    img = np.empty(u.shape + (3,))
    img[:] = blue
    ln = math.hypot(25, 15)
    for dx in (25, -25):                                           # the two diagonals: white 6 wide, red 2 wide, counterchanged
        s = (dx * v - 15 * u) / ln                                 # signed distance, + = counter-clockwise of (dx, 15)
        along = dx * u + 15 * v
        img[np.abs(s) <= 3] = white
        img[((along > 0) & (s >= 0) & (s <= 2)) | ((along < 0) & (s <= 0) & (s >= -2))] = red
    img[(np.abs(u) <= 5) | (np.abs(v) <= 5)] = white
    img[(np.abs(u) <= 3) | (np.abs(v) <= 3)] = red
    img = img.reshape(h, ss, w, ss, 3).mean((1, 3))
    im = bpy.data.images.new('front_flag_src', w, h, alpha=False)
    im.pixels.foreach_set(np.dstack([img, np.ones((h, w))]).astype(np.float32).ravel())
    im.filepath_raw, im.file_format = path, 'JPEG'
    im.save()
    bpy.data.images.remove(im)


def flag(base, pole=1.80, size=(0.91, 1.52)):
    """-> (bracket, pole, cloth). base = bracket base on the wall (x, y, z); the pole leaves the wall square to it
    (-Y) at 45 degrees. The cloth hangs limp from the top half of the pole in soft folds."""
    base = Vector(base)
    d = Vector((0, -1, 1)).normalized()
    tip = base + d * pole
    white, silver = M.solid('front_pole_white', '#F3F3F0', 0.35), M.mat('silver_satin')
    mb = mo.MB()
    mb.box((base.x - 0.035, base.y - 0.008, base.z - 0.065), (base.x + 0.035, base.y, base.z + 0.045), white, bev=0.003)
    mb.tube([base + Vector((0, 0.004, -0.004)), base + d * 0.11], 0.0185, white, n=10)             # socket
    mb.tube([base + d * 0.07 + Vector((0.018, 0, 0)), base + d * 0.07 + Vector((0.04, 0, 0))], 0.005, silver, n=6)   # thumbscrew
    bracket = mb.finish('front.flag.bracket')
    mb = mo.MB()
    mb.tube([base + d * 0.02, tip], 0.0125, white, n=10)
    mb.at(Matrix.Translation(tip + d * 0.012))
    mb._soft = 1
    mb.lathe([(0, -0.0225)] + [(0.0225 * math.sin(math.pi * k / 8), -0.0225 * math.cos(math.pi * k / 8)) for k in range(1, 8)]
             + [(0, 0.0225)], silver, segs=12)
    mb._soft = 0
    mb.at()
    hoist, fly = size
    for u in (0.03, 0.97):                                         # two clips
        mb.tube([tip - d * (0.035 + hoist * u) + Vector((-0.016, 0, 0)), tip - d * (0.035 + hoist * u) + Vector((0.02, 0, 0))],
                0.004, silver, n=5)
    pole_ob = mb.finish('front.flag.pole')

    path = os.path.join(ART, 'front_flag.jpg')
    if not os.path.exists(path):
        flag_texture(path)
    cloth_mat = P.two_sided(M.image_mat('front_flag', path, None, roughness=0.75))
    cb = mo.MB()
    cb._soft = 1
    nu, na = 10, 40

    def pt(u, a):
        h0 = tip - d * (0.035 + hoist * u)
        end = Vector((base.x + 0.20 + 0.07 * u, base.y - 0.87 + 0.30 * u, base.z + 0.64 - 0.46 * u))
        p = h0.lerp(end, a ** 0.85) + Vector((0.012, 0, -0.012)) * min(1, a * 20)
        amp = 0.075 * a ** 0.6
        p.x += amp * math.sin(TAU * 3.2 * a + 2.2 * u + 0.5)
        p.y += 0.03 * a * math.sin(TAU * 2.1 * a + 4 * u)
        p.z -= 0.10 * math.sin(math.pi * a) * (1 - u) + 0.02 * a * math.sin(TAU * 2.6 * a + 3 * u)
        return p

    rows = [cb._vs([pt(i / nu, j / na) for j in range(na + 1)]) for i in range(nu + 1)]
    mi = cb.mi(cloth_mat)
    for i in range(nu):
        for j in range(na):
            cb._f([rows[i][j], rows[i + 1][j], rows[i + 1][j + 1], rows[i][j + 1]], mi,
                  [(j / na, 1 - i / nu), (j / na, 1 - (i + 1) / nu), ((j + 1) / na, 1 - (i + 1) / nu), ((j + 1) / na, 1 - i / nu)])
    return bracket, pole_ob, cb.finish('front.flag', sharp_deg=80)


# ------------------------------------------------------------------------------------------------ bins
def _bin_wheel(mb, x, y, r=0.10, w=0.045):
    mb.at(Matrix.Translation((x, y, r)) @ Matrix.Rotation(math.pi / 2, 4, 'Y'))
    h = w / 2
    mb.lathe([(0, -h), (r * 0.55, -h), (r, -h * 0.6), (r, h * 0.6), (r * 0.55, h), (0, h)], _plastic('front_bin_tyre', '#161617', 0.8), segs=14)
    mb.at()


def wheelie_bin(name, colour):
    """240 l wheelie bin, 0.58 wide x 0.73 deep x 1.07 high. Origin: centre of the footprint; front -Y, wheels and
    handle +Y. Plain: no lettering."""
    body = _plastic('front_bin_' + colour.lstrip('#'), colour)
    mb = mo.MB()
    loft(mb, [(0.045, rrect(0.46, 0.50, 0.05, cy=-0.05)), (0.93, rrect(0.555, 0.635, 0.05, cy=-0.04)),
              (0.945, rrect(0.58, 0.70, 0.04, cy=-0.012)), (0.985, rrect(0.58, 0.70, 0.04, cy=-0.012)),
              (0.985, rrect(0.55, 0.67, 0.04, cy=-0.012))], body, caps=(True, False))
    loft(mb, [(0.985, rrect(0.55, 0.67, 0.04, cy=-0.012)), (0.992, rrect(0.55, 0.67, 0.04, cy=-0.012)),
              (0.992, rrect(0.58, 0.72, 0.04, cy=-0.003)), (1.022, rrect(0.58, 0.72, 0.04, cy=-0.003)),
              (1.048, rrect(0.54, 0.67, 0.07, cy=-0.003)), (1.07, rrect(0.40, 0.52, 0.09, cy=-0.003))], body, caps=(False, True))
    mb.box((-0.13, -0.372, 0.996), (0.13, -0.355, 1.018), body, bev=0.004)                          # lid lip
    for sx in (1, -1):                                                                              # hinge lugs + handle
        mb.box((sx * 0.20 - 0.02, 0.325, 0.93), (sx * 0.20 + 0.02, 0.362, 1.03), body, bev=0.006)
    mb.tube([(-0.22, 0.352, 1.012), (0.22, 0.352, 1.012)], 0.014, body, n=8)
    mb.tube([(-0.27, 0.285, 0.10), (0.27, 0.285, 0.10)], 0.012, M.mat('silver_satin'), n=6)         # axle
    for sx in (1, -1):
        _bin_wheel(mb, sx * 0.262, 0.285)
        mb.box((sx * 0.20 - 0.02, 0.20, 0.06), (sx * 0.20 + 0.02, 0.30, 0.30), body, bev=0.006)     # axle brackets
    return mb.finish(name)


def caddy(name):
    """Kerbside food caddy 0.32 x 0.40 x 0.40 with a paler lid and a carrying handle. Origin: footprint centre."""
    body, lid = _plastic('front_caddy', '#6F7A7C'), _plastic('front_caddy_lid', '#96A0A5')
    mb = mo.MB()
    loft(mb, [(0.0, rrect(0.26, 0.32, 0.04)), (0.33, rrect(0.31, 0.385, 0.045)), (0.345, rrect(0.32, 0.40, 0.045))], body)
    loft(mb, [(0.345, rrect(0.325, 0.405, 0.045)), (0.37, rrect(0.325, 0.405, 0.045)), (0.395, rrect(0.27, 0.34, 0.06))], lid)
    mb.tube([(-0.165, 0.02, 0.30), (-0.172, -0.10, 0.345), (-0.10, -0.205, 0.352), (0.10, -0.205, 0.352), (0.172, -0.10, 0.345),
             (0.165, 0.02, 0.30)], 0.007, lid, n=6)
    return mb.finish(name)


# ------------------------------------------------------------------------------------------------ fittings on the wall
def doorbell(name):
    """Video doorbell 45 x 125 x 25 on a black backplate. Origin: wall, centre; front -Y."""
    black, lens = M.mat('black_matt'), M.solid('front_lens', '#0A0C10', 0.03)
    mb = mo.MB()
    mb.box((-0.027, -0.006, -0.068), (0.027, 0, 0.068), black, bev=0.002)
    mb.box((-0.0225, -0.027, -0.0625), (0.0225, -0.006, 0.0625), M.mat('black_gloss'), bev=0.005)
    for z, r, m in ((0.036, 0.011, lens), (-0.038, 0.012, M.mat('silver_satin')), (-0.038, 0.009, black)):
        mb.at(Matrix.Translation((0, -0.027, z)) @ Matrix.Rotation(math.pi / 2, 4, 'X'))
        mb.lathe([(r, 0), (r, 0.0015 if m is not black else 0.002), (0, 0.0015 if m is not black else 0.002)], m, segs=14)
    return mb.at().finish(name)


def outdoor_socket(name):
    """Grey weatherproof socket box 160 x 100 x 80 with a hinged lid. Origin: wall, centre; front -Y."""
    grey = _plastic('front_socket_grey', '#B9BBB8', 0.5)
    mb = mo.MB()
    mb.box((-0.08, -0.05, -0.05), (0.08, 0, 0.05), grey, bev=0.006)
    mb.box((-0.076, -0.08, -0.046), (0.076, -0.052, 0.046), grey, bev=0.008)                        # lid
    mb.box((-0.06, -0.066, 0.046), (0.06, -0.05, 0.054), grey, bev=0.002)                           # hinge
    mb.box((-0.012, -0.084, -0.046), (0.012, -0.078, -0.03), _plastic('front_socket_catch', '#8C8E8B'), bev=0.002)
    mb.tube([(0.05, -0.025, -0.05), (0.05, -0.025, -0.075)], 0.011, _plastic('front_socket_catch', '#8C8E8B'), n=8)   # gland
    return mb.finish(name)


def security_cam(name):
    """Small black bullet camera on a short wall arm, cable looping down to the wall; unlit. Origin: wall, centre of
    the mounting plate; front -Y."""
    black, glass = M.solid('front_cam_black', '#16171A', 0.4), M.solid('front_lens', '#0A0C10', 0.03)
    mb = mo.MB()
    mb.box((-0.035, -0.012, -0.035), (0.035, 0, 0.035), black, bev=0.004)
    mb.tube([(0, -0.01, 0), (0, -0.07, -0.02)], 0.012, black, n=8)
    mb.at(Matrix.Translation((0, -0.11, -0.045)) @ Matrix.Rotation(math.radians(-70), 4, 'X'))
    mb._soft = 1
    mb.lathe([(0, -0.07), (0.03, -0.07), (0.034, -0.05), (0.034, 0.05), (0.028, 0.07), (0, 0.07)], black, segs=12)
    mb.lathe([(0.02, 0.0705), (0, 0.0705)], glass, segs=12)
    mb._soft = 0
    mb.at()
    mb.tube([(0.03, -0.005, -0.03), (0.04, -0.012, -0.09), (0.03, -0.006, -0.16)], 0.003, black, n=5)
    return mb.finish(name)


def cover(name, w, d):
    """Recessed inspection cover: steel frame with a concrete infill. Origin: centre, top face at z = 0.004."""
    mb = mo.MB()
    mb.box((-w / 2, -d / 2, -0.03), (w / 2, d / 2, 0.003), M.solid('front_cover_frame', '#5A5B5C', 0.5, 0.6))
    mb.box((-w / 2 + 0.02, -d / 2 + 0.02, 0.0), (w / 2 - 0.02, d / 2 - 0.02, 0.004), M.solid('front_cover_infill', '#949490', 0.9))
    for sx in (1, -1):
        mb.box((sx * (w / 2 - 0.07) - 0.02, -0.008, 0.004), (sx * (w / 2 - 0.07) + 0.02, 0.008, 0.0045), M.mat('cast_iron'))
    return mb.finish(name)


# ------------------------------------------------------------------------------------------------ street furniture
def lamp_column(name, h=6.0):
    """-> (shaft, arm): slim black steel lamp column with a small blank sign plate. Origin: foot; the lantern
    reaches toward -Y."""
    black = M.solid('front_column_black', '#1B1C1E', 0.45, 0.3)
    mb = mo.MB()
    mb._soft = 1
    mb.lathe([(0, 0), (0.075, 0), (0.075, 1.25), (0.05, 1.33), (0.042, h - 0.05), (0, h - 0.05)], black, segs=12)
    mb._soft = 0
    shaft = mb.finish(name)
    mb = mo.MB()
    mb.tube([(0, 0, h - 0.12), (0, -0.25, h + 0.02), (0, -0.55, h + 0.04)], 0.03, black, n=8)
    mb.box((-0.11, -0.95, h - 0.02), (0.11, -0.45, h + 0.075), black, bev=0.02)
    mb.box((-0.085, -0.92, h - 0.026), (0.085, -0.52, h - 0.02), M.solid('front_lantern_lens', '#D8D6CC', 0.3))
    mb.box((-0.006, -0.17, 2.0), (0.006, 0.17, 2.42), M.solid('front_sign_blank', '#D9DADB', 0.5), bev=0.002)       # blank plate
    for z in (2.08, 2.34):
        mb.box((-0.05, -0.02, z - 0.012), (0.05, 0.02, z + 0.012), black)
    return shaft, mb.finish(name + '.arm')


def street_tree(name, h=7.0, seed=3):
    """-> (trunk, branches, crown): young street tree, crown from 3 m, sparse yellow-green autumn leaves."""
    rnd = random.Random(seed)
    bark = M.solid('front_tree_bark', '#5B4E40', 0.9)
    mb = mo.MB()
    mb._soft = 1
    mb.lathe([(0, 0), (0.085, 0), (0.075, 0.4), (0.07, 2.9), (0.045, 4.6), (0, 4.7)], bark, segs=8)
    trunk = mb.finish(name)
    mb = mo.MB()
    tips = []
    for k in range(9):
        a, z0 = TAU * k / 9 + rnd.uniform(-.3, .3), rnd.uniform(2.7, 4.4)
        r1, z1 = rnd.uniform(0.9, 1.6), z0 + rnd.uniform(1.0, 2.3)
        mid = (0.45 * r1 * math.cos(a), 0.45 * r1 * math.sin(a), z0 + 0.65 * (z1 - z0))
        end = (r1 * math.cos(a), r1 * math.sin(a), min(z1, h - 0.3))
        mb.tube([(0, 0, z0), mid, end], 0.022, bark, n=5)
        tips += [Vector(mid), Vector(end), (Vector(mid) + Vector(end)) / 2]
    tips.append(Vector((0, 0, h - 0.6)))
    branches = mb.finish(name + '.branches')
    cb = mo.MB()
    cols = [cb.mi(P.two_sided(M.solid('front_tree_leaf_%d' % k, hx, 0.6))) for k, hx in enumerate(('#B9B548', '#9FA83C', '#CBBF58'))]
    for c in tips:
        for _ in range(70):
            p = c + Vector((rnd.gauss(0, 0.36), rnd.gauss(0, 0.36), rnd.gauss(0, 0.32)))
            u, v = _frame((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-.2, 1)))
            s = rnd.uniform(0.03, 0.05)
            cb._f(cb._vs([p + u * s, p + v * s * 0.7, p - u * s, p - v * s * 0.7]), cols[rnd.randrange(3)])
    return trunk, branches, cb.finish(name + '.crown')

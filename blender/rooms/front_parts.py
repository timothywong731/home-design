"""Forecourt parts (spec/rooms/front.md 5-8 and its round-3 notes, spec/phase2/front_elevation.md 5, spec/phase3/front.md):
timber troughs with bellflowers on the west wall, the flag, bins and caddy, doorbell, outdoor socket, meter and cable
boxes, the twin-flood security light, inspection covers, gullies, the pier plaque, the lamp column, the street tree and
the east neighbour's raised bed. planter / flag / street furniture return objects in WORLD coordinates; the small
fittings are built about their own origin (stated per function) for P.place / front._settle."""
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
    trailing bellflower (leaves and flowers are real low-poly geometry: the path runs 0.5 m from it).
    Spec `front_wall_w.planter` (RECONCILE3 front-03): the trough stands on the brick top (+0.54); its side boards
    run from bottomZ +0.47 (lapping 70 mm down over both brick faces, 7 mm clear of them) to the rim +0.76."""
    from lib import site_tex as ST
    b = next(b for b in ctx.spec['exterior']['boundaries'] if b['id'] == 'front_wall_w')
    (xc, ya), (_, yb) = b['line']
    top = b['baseZ'] + b['height']                                 # brick top: the trough's floor and end boards
    pl = b.get('planter', {})
    z0, z1 = pl.get('bottomZ', top - 0.07), pl.get('rimZ', top + 0.22)
    # pier end: under the pier cap's 60 mm overhang (cap underside 0.915 > rim); house end: 8 mm short of the wall end
    # (y -0.21), the canopy downpipe stands just beyond it at y -0.17
    y0, y1 = min(ya, yb) + 0.045, max(ya, yb) - 0.008
    hw, th = b['thickness'] / 2 + 0.025, 0.018                     # boards stand 25 mm proud of the brick
    rnd = random.Random(5)
    boards = [ST.mat('timber_box_dark@' + hx) for hx in ('#5B4A3A', '#6A5947', '#7E6C58', '#8F7C65')]   # weathered silver
    mb = mo.MB()
    n = round((y1 - y0) / 0.095)
    for k in range(n):
        ya_, yb_ = y0 + (y1 - y0) * k / n, y0 + (y1 - y0) * (k + 1) / n
        for sx in (1, -1):
            p = rnd.uniform(0, 0.004)
            xa_, xb_ = sorted((xc + sx * (hw + p), xc + sx * (hw + p - th)))
            mb.box((xa_, ya_ + 0.0015, z0 - rnd.uniform(0, 0.010)), (xb_, yb_ - 0.0015, z1 + rnd.uniform(-0.014, 0.006)),
                   boards[rnd.choices((0, 1, 2, 3), (30, 35, 22, 13))[0]], grain=2)
    for k in range(5):                                             # ends of the four boxes, standing on the brick
        y = y0 + (y1 - y0) * k / 4
        ya_, yb_ = (y, y + th) if k == 0 else (y - th, y) if k == 4 else (y - th, y + th)
        mb.box((xc - hw + th, ya_, top), (xc + hw - th, yb_, z1 - 0.004), boards[1], grain=2)
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
        rx = (hw + 0.065 + 0.03 * math.sin(2.1 * y) + 0.02 * math.sin(5.3 * y + 1)) * fx
        rz = (0.185 + 0.03 * math.sin(3.3 * y + 2) + 0.02 * math.sin(7.7 * y)) * fz          # top about Z 1.0
        x = xc + rx * math.cos(a)
        if y > y1 - 0.75:                                          # trimmed back beside the street door: the open
            x = min(x, xc + hw + 0.005)                            # west leaf stands just off the board face
        return Vector((x, y, zr + rz * math.sin(a))), Vector((math.cos(a) * rz, 0, math.sin(a) * rx)).normalized()

    fb = mo.MB()
    fb._soft = 1
    dark = M.solid('front_foliage_shade', '#4F6E36', 0.95)
    ny, na = round((y1 - y0) / 0.07), 12
    rows = [fb._vs([surf(y0 + (y1 - y0) * i / ny, A0 + (A1 - A0) * j / na, 0.9)[0] for j in range(na + 1)]) for i in range(ny + 1)]
    mi = fb.mi(dark)
    for r0, r1 in zip(rows, rows[1:]):
        for j in range(na):
            fb._f([r0[j], r1[j], r1[j + 1], r0[j + 1]], mi)
    fb._f(rows[0], mi)
    fb._f(rows[-1][::-1], mi)
    fb._soft = 0

    leaf = [fb.mi(P.two_sided(M.solid('front_leaf_%d' % k, hx, 0.55))) for k, hx in enumerate(('#84A65E', '#9CB873', '#6A8E4B'))]     # v8 t100-102: light yellow-green
    petal = [fb.mi(P.two_sided(M.solid('front_bellflower_%d' % k, hx, 0.6))) for k, hx in enumerate(('#6A4CC2', '#8468D4'))]                   # violet
    rim = [(math.cos(TAU * k / 5), math.sin(TAU * k / 5) * 0.85) for k in range(5)]
    for _ in range(5200):                                          # leaves: small round-ish pentagons on the cushion
        p, nrm = surf(rnd.uniform(y0 + 0.015, y1 - 0.015), rnd.uniform(A0, A1), rnd.uniform(0.93, 1.07))
        nrm = (nrm + Vector((rnd.uniform(-.6, .6), rnd.uniform(-.6, .6), rnd.uniform(-.3, .6)))).normalized()
        u, v = _frame(nrm)
        s, r = rnd.uniform(0.010, 0.016), rnd.uniform(0, TAU)
        u, v = u * math.cos(r) + v * math.sin(r), v * math.cos(r) - u * math.sin(r)
        fb._f(fb._vs([p + (u * a + v * b) * s for a, b in rim]), leaf[rnd.choices((0, 1, 2), (45, 40, 15))[0]])
    for _ in range(1700):                                          # flowers: five-pointed stars, densest on top (v8 f100-102)
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


def wheelie_bin(name, colour, lid=None):
    """240 l wheelie bin, 0.58 wide x 0.73 deep x 1.07 high, lid in its own colour (navy bin: paler lid). Origin:
    centre of the footprint; front -Y, wheels and handle +Y. Contacts: the wheels (+-0.262, 0.285) and two front
    feet (+-0.17, -0.25), all at z 0. Plain: no lettering."""
    body = _plastic('front_bin_' + colour.lstrip('#'), colour)
    top = _plastic('front_bin_' + (lid or colour).lstrip('#'), lid or colour)
    mb = mo.MB()
    loft(mb, [(0.045, rrect(0.46, 0.50, 0.05, cy=-0.05)), (0.93, rrect(0.555, 0.635, 0.05, cy=-0.04)),
              (0.945, rrect(0.58, 0.70, 0.04, cy=-0.012)), (0.985, rrect(0.58, 0.70, 0.04, cy=-0.012)),
              (0.985, rrect(0.55, 0.67, 0.04, cy=-0.012))], body, caps=(True, False))
    loft(mb, [(0.985, rrect(0.55, 0.67, 0.04, cy=-0.012)), (0.992, rrect(0.55, 0.67, 0.04, cy=-0.012)),
              (0.992, rrect(0.58, 0.72, 0.04, cy=-0.003)), (1.022, rrect(0.58, 0.72, 0.04, cy=-0.003)),
              (1.048, rrect(0.54, 0.67, 0.07, cy=-0.003)), (1.07, rrect(0.40, 0.52, 0.09, cy=-0.003))], top, caps=(False, True))
    mb.box((-0.13, -0.372, 0.996), (0.13, -0.355, 1.018), top, bev=0.004)                           # lid lip
    for sx in (1, -1):                                                                              # hinge lugs + handle
        mb.box((sx * 0.20 - 0.02, 0.325, 0.93), (sx * 0.20 + 0.02, 0.362, 1.03), body, bev=0.006)
        mb.box((sx * 0.17 - 0.03, -0.29, 0.0), (sx * 0.17 + 0.03, -0.21, 0.06), body, bev=0.008)    # front foot
    mb.tube([(-0.22, 0.352, 1.012), (0.22, 0.352, 1.012)], 0.014, body, n=8)
    for z in (0.32, 0.62):                                                                          # moulded ribs on the front
        y = -0.355 + 0.055 * z
        mb.box((-0.19, y - 0.012, z - 0.012), (0.19, y + 0.03, z + 0.012), body, bev=0.006)
    mb.tube([(-0.27, 0.285, 0.10), (0.27, 0.285, 0.10)], 0.012, M.mat('silver_satin'), n=6)         # axle
    for sx in (1, -1):
        _bin_wheel(mb, sx * 0.262, 0.285)
        mb.box((sx * 0.20 - 0.02, 0.20, 0.06), (sx * 0.20 + 0.02, 0.30, 0.30), body, bev=0.006)     # axle brackets
    return mb.finish(name)


def caddy(name):
    """Kerbside food caddy 0.32 x 0.40 x 0.40, pale sage green (front survey 2.5: T #8FA79A, nudged to yellow-green
    so it does not render teal) with a pale grey lid (v8 t30 / t60: #B6BEBD / #A4ADAF) and a carrying handle. Origin: footprint centre; contacts at the four bottom corners (+-0.12, +-0.15)."""
    body, lid = _plastic('front_caddy', '#93A597'), _plastic('front_caddy_lid', '#C4CBC8')
    mb = mo.MB()
    loft(mb, [(0.0, rrect(0.26, 0.32, 0.04)), (0.33, rrect(0.31, 0.385, 0.045)), (0.345, rrect(0.32, 0.40, 0.045))], body)
    loft(mb, [(0.345, rrect(0.325, 0.405, 0.045)), (0.37, rrect(0.325, 0.405, 0.045)), (0.395, rrect(0.27, 0.34, 0.06))], lid)
    mb.box((-0.06, -0.207, 0.355), (0.06, -0.195, 0.372), lid, bev=0.003)                           # latch
    mb.tube([(-0.165, 0.02, 0.30), (-0.172, -0.10, 0.345), (-0.10, -0.205, 0.352), (0.10, -0.205, 0.352), (0.172, -0.10, 0.345),
             (0.165, 0.02, 0.30)], 0.007, _plastic('front_caddy_handle', '#3A3D3C'), n=6)
    return mb.finish(name)


# ------------------------------------------------------------------------------------------------ fittings on the wall
def doorbell(name):
    """Slim video doorbell 46 x 122 x 25 (v9 f44-48: black, satin face, lens window at the top, ring button below)
    on a black backplate. Origin: wall, centre; front -Y."""
    black, lens = M.mat('black_matt'), M.solid('front_lens', '#0A0C10', 0.03)
    mb = mo.MB()
    mb.box((-0.027, -0.006, -0.066), (0.027, 0, 0.066), black, bev=0.002)
    mb.box((-0.023, -0.025, -0.061), (0.023, -0.006, 0.061), M.solid('front_bell_face', '#2A2C30', 0.35), bev=0.005)
    mb.box((-0.016, -0.0262, 0.022), (0.016, -0.0245, 0.052), lens, bev=0.001)                      # lens window
    for z, r, m in ((-0.036, 0.0115, M.mat('silver_satin')), (-0.036, 0.0085, black)):
        mb.at(Matrix.Translation((0, -0.025, z)) @ Matrix.Rotation(math.pi / 2, 4, 'X'))
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


SECLIGHT_R = 0.055          # wall-plate radius: the plate's top stands this far above the light's origin


def security_light(name):
    """White floodlight camera (v8 t69 / t70, cropped): round wall plate with a short hub; two round flood heads with
    frosted lenses on ball arms, splayed left and right and tipped down; a camera body below them with a black lens
    window; the cable hanging from the hub. About 0.24 wide x 0.20 high (v8 t69: 140 px against the 245 px cheek
    window, scaled for its distance). Unlit. Origin: wall, centre of the plate; front -Y."""
    R = SECLIGHT_R
    white, glass = _plastic('front_seclight_white', '#ECECE8', 0.4), M.solid('front_lens', '#0A0C10', 0.03)
    frost = M.solid('front_seclight_lens', '#DADAD4', 0.25)
    mb = mo.MB()
    mb._soft = 1
    mb.at(Matrix.Rotation(math.pi / 2, 4, 'X'))                                                     # plate + hub, out of the wall
    mb.lathe([(0, 0), (R, 0), (R + 0.002, 0.006), (R - 0.004, 0.018), (0.033, 0.019), (0.032, 0.058), (0, 0.06)], white, segs=18)
    mb.at()
    mb.box((-0.022, -0.072, -0.075), (0.022, -0.03, 0.0), white, bev=0.01)                         # neck down to the camera
    mb.box((-0.033, -0.118, -0.14), (0.033, -0.048, -0.055), white, bev=0.014)                     # camera body
    mb.box((-0.019, -0.1195, -0.118), (0.019, -0.1165, -0.072), glass, bev=0.003)                  # lens window
    for sx in (1, -1):                                                                              # two flood heads
        mb.tube([(0, -0.05, -0.006), (sx * 0.045, -0.08, -0.002)], 0.01, white, n=6)               # ball arm
        mb.at(Matrix.Translation((sx * 0.068, -0.095, 0.0)) @ Matrix.Rotation(sx * math.radians(30), 4, 'Z')
              @ Matrix.Rotation(math.radians(105), 4, 'X'))
        mb.lathe([(0, -0.032), (0.034, -0.032), (0.043, -0.014), (0.046, 0.026), (0.042, 0.03), (0, 0.03)], white, segs=18)
        mb.lathe([(0.038, 0.0305), (0, 0.0305)], frost, segs=18)
        mb.at()
    mb._soft = 0
    mb.tube([(0.012, -0.03, -0.035), (0.016, -0.034, -0.11), (0.022, -0.026, -0.17)], 0.0035, M.mat('black_matt'), n=5)  # cable
    return mb.finish(name)


def meter_box(name, h=0.53):
    """White surface gas-meter box 0.41 wide x h high x 0.21 deep (v8 f68-79, t69): door with a reveal, two key
    holes, hinge gap. Origin: wall, centre of the bottom edge; front -Y."""
    white = _plastic('front_meterbox_white', '#EAE9E2', 0.5)
    mb = mo.MB()
    mb.box((-0.205, -0.21, 0.0), (0.205, 0.0, h), white, bev=0.008)
    mb.box((-0.195, -0.214, 0.012), (0.195, -0.209, h - 0.012), white, bev=0.002)                   # door face
    for x in (-0.15, 0.15):
        mb.box((x - 0.004, -0.2155, 0.46 * h - 0.006), (x + 0.004, -0.2135, 0.46 * h + 0.006), M.mat('black_matt'))
    mb.box((0.196, -0.2145, 0.08), (0.2, -0.209, h - 0.08), M.solid('front_shutline', '#6E6D68', 0.6))   # hinge gap
    return mb.finish(name)


def cable_box(name):
    """Small white junction box 0.09 x 0.13 x 0.055 with rounded edges and a cable gland below. Origin: wall,
    centre; front -Y."""
    white = _plastic('front_meterbox_white', '#EAE9E2', 0.5)
    mb = mo.MB()
    mb.box((-0.045, -0.055, -0.065), (0.045, 0.0, 0.065), white, bev=0.014)
    mb.tube([(0, -0.025, -0.065), (0, -0.025, -0.085)], 0.007, white, n=6)
    return mb.finish(name)


def gully(name, s=0.15):
    """Square yard gully s x s: galvanised frame with a slotted cast grating, set flush. Origin: centre, top at z 0."""
    mb = mo.MB()
    frame, iron = M.solid('front_cover_frame', '#A9ABAA', 0.4, 0.7), M.mat('cast_iron')
    h = s / 2
    for a, b in (((-h, -h), (h, -h + 0.012)), ((-h, h - 0.012), (h, h)), ((-h, -h), (-h + 0.012, h)), ((h - 0.012, -h), (h, h))):
        mb.box((a[0], a[1], -0.04), (b[0], b[1], 0.002), frame)
    mb.box((-h + 0.012, -h + 0.012, -0.06), (h - 0.012, h - 0.012, -0.055), M.solid('front_gully_void', '#0B0B0B', 0.9))
    for k in range(6):                                                                              # grating bars
        x = -h + 0.012 + (s - 0.024) * (k + 0.5) / 6
        mb.box((x - 0.0055, -h + 0.012, -0.02), (x + 0.0055, h - 0.012, 0.0015), iron)
    return mb.finish(name)


def pier_plaque(name):
    """Small black cast plaque 0.22 x 0.065 with two lines of raised white capitals (front survey 2.2), drawn as short
    white bars, deliberately illegible, and two screws. Origin: wall, centre; front -Y."""
    black, white = M.solid('front_plaque_black', '#151515', 0.5, 0.3), M.solid('front_plaque_white', '#E8E6E0', 0.5)
    rnd = random.Random(11)
    mb = mo.MB()
    mb.box((-0.11, -0.006, -0.0325), (0.11, 0.0, 0.0325), black, bev=0.002)
    for zc, w in ((0.012, 0.15), (-0.012, 0.10)):
        x = -w / 2
        while x < w / 2 - 0.004:
            lw = rnd.choice((0.007, 0.008, 0.009, 0.006))
            mb.box((x, -0.0072, zc - 0.0055), (x + lw, -0.0058, zc + 0.0055), white)
            x += lw + (0.012 if rnd.random() < 0.18 else 0.0028)
    for x in (-0.098, 0.098):
        mb.at(Matrix.Translation((x, -0.006, 0)) @ Matrix.Rotation(math.pi / 2, 4, 'X'))
        mb.lathe([(0.0035, 0), (0.0035, 0.0012), (0, 0.0018)], M.mat('silver_satin'), segs=8)
    return mb.at().finish(name)


def cover(name, w, d, haunch=0.0):
    """Recessed inspection cover w x d: bright galvanised steel frame, tray of cool grey concrete (T #8C8A86; v8 t30 /
    t60 sample #8F9090 / #75777A, a little lighter than the tarmac), two key holes; with haunch > 0 a cast-concrete margin that wide all round, 3 mm proud of the tarmac (front survey 2.1).
    Origin: centre, z 0 = the surrounding surface; contacts at the corners (+-w/2, +-d/2)."""
    mb = mo.MB()
    if haunch:
        mb.box((-w / 2 - haunch, -d / 2 - haunch, -0.05), (w / 2 + haunch, d / 2 + haunch, 0.003),
               M.solid('front_cover_haunch', '#8F8D87', 0.92))
    mb.box((-w / 2, -d / 2, -0.03), (w / 2, d / 2, 0.005), M.solid('front_cover_frame', '#A9ABAA', 0.4, 0.7))
    mb.box((-w / 2 + 0.018, -d / 2 + 0.018, 0.0), (w / 2 - 0.018, d / 2 - 0.018, 0.0055), M.solid('front_cover_infill', '#8A8C8C', 0.85))
    for sy in (1, -1):                                                                              # key holes
        mb.box((-0.022, sy * (d / 2 - 0.08) - 0.007, 0.0035), (0.022, sy * (d / 2 - 0.08) + 0.007, 0.006), M.mat('cast_iron'))
    return mb.finish(name)


def steel_planter(name, w=0.9, d=2.0, h=0.5, seed=7):
    """-> (box, shrub): the east neighbour's raised bed (massing, front survey 2.3): dark corrugated steel 0.9 x 2.0 x
    0.5 with a galvanised rim, filled with a leafy shrub. Origin: footprint centre at the ground; long side along Y."""
    steel, rim = M.solid('front_corrugated_dark', '#262427', 0.55, 0.5), M.solid('front_planter_rim', '#7C7F80', 0.45, 0.7)
    mb = mo.MB()
    pitch, amp = 0.076, 0.009                                                                       # vertical corrugations
    mi = mb.mi(steel)
    for (ax, ay), (bx, by), (nx, ny) in (((-w / 2, -d / 2), (w / 2, -d / 2), (0, -1)), ((w / 2, -d / 2), (w / 2, d / 2), (1, 0)),
                                         ((w / 2, d / 2), (-w / 2, d / 2), (0, 1)), ((-w / 2, d / 2), (-w / 2, -d / 2), (-1, 0))):
        n = max(2, 2 * round(math.hypot(bx - ax, by - ay) / pitch))
        pts = [(ax + (bx - ax) * k / n + nx * amp * (k % 2), ay + (by - ay) * k / n + ny * amp * (k % 2)) for k in range(n + 1)]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            mb._f(mb._vs([(x0, y0, 0), (x1, y1, 0), (x1, y1, h), (x0, y0, h)]), mi)
    e = 0.02
    for a, b in (((-w / 2 - e, -d / 2 - e), (w / 2 + e, -d / 2 + 0.03)), ((-w / 2 - e, d / 2 - 0.03), (w / 2 + e, d / 2 + e)),
                 ((-w / 2 - e, -d / 2), (-w / 2 + 0.03, d / 2)), ((w / 2 - 0.03, -d / 2), (w / 2 + e, d / 2))):
        mb.box((a[0], a[1], h - 0.03), (b[0], b[1], h + 0.008), rim)
    mb.box((-w / 2 + 0.03, -d / 2 + 0.03, h - 0.07), (w / 2 - 0.03, d / 2 - 0.03, h - 0.06), P.mat('soil'))
    box = mb.finish(name)
    # shrub (v8 t60, f37, f61): a dense yellow-green mound 0.5-0.6 above the rim, spilling about 0.08 over it -
    # a low-poly cushion in the shade colour with leaf cards on its surface (the planter bellflower's method)
    rnd = random.Random(seed)
    cb = mo.MB()
    hy, top = d / 2 + 0.05, 0.55

    def surf(y, a, grow=1.0):
        e = max(0.0, 1 - (abs(y) / hy) ** 4) ** 0.5
        n = grow * (1 + 0.10 * math.sin(7 * y + 3 * a) + 0.06 * math.sin(13 * y - 5 * a + 1))
        rx, rz = (w / 2 + 0.06) * (0.55 + 0.45 * e) * n, top * (0.35 + 0.65 * e) * n
        return (Vector((rx * math.cos(a), y, h - 0.02 + rz * math.sin(a))),
                Vector((math.cos(a) * rz, 0, math.sin(a) * rx)).normalized())
    A0, A1, ny, na = math.radians(-10), math.radians(190), 16, 10
    cb._soft = 1
    rows = [cb._vs([surf(-hy + 2 * hy * i / ny, A0 + (A1 - A0) * j / na, 0.92)[0] for j in range(na + 1)]) for i in range(ny + 1)]
    mi = cb.mi(M.solid('front_shrub_shade', '#5A6330', 0.95))
    for r0, r1 in zip(rows, rows[1:]):
        for j in range(na):
            cb._f([r0[j], r1[j], r1[j + 1], r0[j + 1]], mi)
    cb._f(rows[0], mi)
    cb._f(rows[-1][::-1], mi)
    cb._soft = 0
    cols = [cb.mi(P.two_sided(M.solid('front_shrub_%d' % k, hx, 0.6))) for k, hx in enumerate(('#B4AD50', '#9C9F45', '#7E8A3B'))]
    for _ in range(1800):
        p, nrm = surf(rnd.uniform(-hy + 0.02, hy - 0.02), rnd.uniform(A0, A1), rnd.uniform(0.96, 1.06))
        u, v = _frame((nrm + Vector((rnd.uniform(-.7, .7), rnd.uniform(-.7, .7), rnd.uniform(-.2, .7)))).normalized())
        sz = rnd.uniform(0.028, 0.045)
        cb._f(cb._vs([p + u * sz, p + v * sz * 0.65, p - u * sz, p - v * sz * 0.65]),
              cols[rnd.choices((0, 1, 2), (45, 35, 20))[0]])
    return box, cb.finish(name + '.shrub', sharp_deg=60)


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
    """-> (trunk, branches, crown): street tree (v8 f7, f49, f55): trunk 0.2 forking at about 2.5 m into five limbs,
    four branches on each and four twigs on each branch; small yellow-green autumn leaves clustered on the twigs
    (within 0.12 of them; none more than 0.2 from wood). Crown about 4 m across."""
    rnd = random.Random(seed)
    bark = M.solid('front_tree_bark', '#5B4E40', 0.9)
    mb = mo.MB()
    mb._soft = 1
    mb.lathe([(0, 0), (0.11, 0), (0.10, 0.4), (0.09, 2.4), (0.065, 2.9), (0, 2.95)], bark, segs=8)
    trunk = mb.finish(name)
    wb = mo.MB()
    twigs = []
    for k in range(5):
        a, tilt = TAU * k / 5 + rnd.uniform(-.25, .25), rnd.uniform(0.3, 0.55)
        base = Vector((0, 0, rnd.uniform(2.4, 2.8)))
        dv = Vector((math.sin(tilt) * math.cos(a), math.sin(tilt) * math.sin(a), math.cos(tilt)))
        ln = min(rnd.uniform(2.8, 3.8), (h - 0.3 - base.z) / dv.z)
        mid, end = base + dv * ln * 0.5, base + dv * ln
        wb.tube([base, mid], 0.05, bark, n=6)
        wb.tube([mid, end], 0.028, bark, n=6)
        twigs.append((mid, end))
        for _ in range(4):
            t = rnd.uniform(0.3, 0.92)
            p, ba = base + dv * ln * t, a + rnd.uniform(-1.2, 1.2)
            bd = Vector((0.8 * math.cos(ba), 0.8 * math.sin(ba), rnd.uniform(0.25, 0.9))).normalized()
            bl = rnd.uniform(0.6, 1.1) * (1.15 - 0.4 * t)
            wb.tube([p, p + bd * bl], 0.015, bark, n=5)
            for _ in range(4):
                r0 = p + bd * bl * rnd.uniform(0.4, 1.0)
                td = (bd + Vector((rnd.uniform(-.8, .8), rnd.uniform(-.8, .8), rnd.uniform(-.3, .6)))).normalized()
                r1 = r0 + td * rnd.uniform(0.3, 0.5)
                r1.z = min(r1.z, h - 0.1)
                wb.tube([r0, r1], 0.007, bark, n=4)
                twigs.append((r0, r1))
    branches = wb.finish(name + '.branches')
    cb = mo.MB()
    cols = [cb.mi(P.two_sided(M.solid('front_tree_leaf_%d' % k, hx, 0.6))) for k, hx in enumerate(('#B9B548', '#9FA83C', '#CBBF58'))]
    for r0, r1 in twigs:
        for _ in range(38):
            j = Vector((rnd.gauss(0, 0.05), rnd.gauss(0, 0.05), rnd.gauss(0, 0.045)))
            if j.length > 0.12:
                j *= 0.12 / j.length
            p = r0.lerp(r1, rnd.uniform(0.15, 1.05)) + j
            u, v = _frame((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-.2, 1)))
            s = rnd.uniform(0.028, 0.045)
            cb._f(cb._vs([p + u * s, p + v * s * 0.7, p - u * s, p - v * s * 0.7]), cols[rnd.randrange(3)])
    return trunk, branches, cb.finish(name + '.crown')

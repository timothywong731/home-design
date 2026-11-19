"""Utility / laundry room fittings. Spec: spec/rooms/utility.md (+ its "Reconciled dimensions").

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --only shell,utility,wc --preview utility,wc \
         --res 540x960 --samples 64 --tag service --save build/service.blend

World coords, metres. Room x 0.60..3.10, y 10.26..12.23, ceiling 2.40. W-rear = y 12.23 (washer, dryer,
sink, wall cabinets), W-ext = x 3.10 (window, base doors A/B, tall cupboard), W-wc = y 10.26, W-hall = x 0.60.
Built-in pieces are mo.MB meshes in world coordinates (object at identity) with the lib props parented to
them, so each plan footprint covers the whole piece.

Interaction (blender/INTERACT.md): every cabinet front + its pull is a hinge group about the front corner on its
hinge side (OPEN = the angles; several are held under 90 deg by what stands in the swing), the carcasses are
open-fronted and lined, the machine portholes hinge on their left over a drum, the tap lever lifts and runs a
stream into the sink, the switch plates carry the lights. State 0 is the room as it was reviewed.
"""
import math
import os
import random

import bpy
import numpy as np
from mathutils import Matrix, Vector

from lib import interact as IX, lighting, materials as M, mouldings as mo, props as P, shell

ROOM = 'utility'
ART = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'textures', 'art', ROOM)

X0, X1, Y0, Y1 = 0.60, 3.10, 10.26, 12.23
TOP = 0.91                  # worktop surface; 40 mm thick
YF = 11.63                  # carcass fronts of the W-rear run (door faces 11.61 = worktop front edge)
XF = 2.53                   # carcass fronts of the W-ext run (door faces 2.51 = -x face of the corner post)
WALL_Z0, WALL_Z1 = 1.395, 2.295
STILE = 0.075               # cabinet door stiles / rails
REC = 0.010                 # door panel recess behind the frame face
SINK_Z0 = 0.649             # underside of the Belfast sink: its rim (0.869) sits 1 mm under the worktop
# Base door A (W-ext, next to the inside corner): hinge edge and width. Its free edge swings out to
# A_Y0 + hypot(A_W, 0.02) = 11.587, in front of the end of the sink apron (face y 11.59, 2.5 mm off the door plane).
A_Y0, A_W = 11.2465, 0.340

CAMERAS = [
    dict(name='rear', pos=(0.78, 10.72, 1.5), look=(1.75, 12.23, 1.05), fov_deg=100, ref='f_0476'),
    dict(name='far', pos=(0.9, 10.8, 1.5), look=(3.1, 11.3, 1.3), fov_deg=100, ref='f_0450'),
    dict(name='sink', pos=(1.6, 10.86, 1.5), look=(2.6, 11.9, 0.7), fov_deg=100, ref='f_0461'),
    dict(name='corner', pos=(1.9, 11.06, 1.5), look=(2.9, 12.0, 1.2), fov_deg=100, ref='f_0489'),
    dict(name='tall', pos=(1.9, 10.96, 1.5), look=(2.9, 10.4, 1.7), fov_deg=100, ref='f_0495'),
    dict(name='wcdoor', pos=(1.8, 11.26, 1.5), look=(1.6, 10.2, 0.9), fov_deg=100, ref='f_0499'),
    dict(name='fromhall', pos=(-0.2, 10.8, 1.5), look=(3.1, 11.0, 1.3), fov_deg=100, ref='f_0567'),
    dict(name='out', pos=(1.8, 10.86, 1.5), look=(0.6, 10.8, 1.4), fov_deg=100, ref='f_0546'),
    # interaction checks (--pose 1): portholes + drums, the base cupboards round the corner, the wall units from below
    dict(name='ix_machines', pos=(1.75, 10.75, 1.25), look=(1.2, 11.7, 0.4), fov_deg=100, ref='f_0476'),
    dict(name='ix_base', pos=(1.45, 10.75, 1.45), look=(2.45, 11.55, 0.45), fov_deg=100, ref='f_0461'),
    dict(name='ix_wall', pos=(1.6, 10.6, 1.2), look=(1.6, 12.0, 1.9), fov_deg=100, ref='f_0476'),
]

# State-1 angle of every cabinet front (degrees, right-hand rule about +Z: hinge on the viewer's left = negative).
# The contract asks for 95-110; a front opens less where something stands in its swing, so that nothing touches
# with every front open at once (checked: build/ix_service/check.py, also part-way through each swing):
#   base.sink    the inside corner: any further and it crosses base door A standing open
#   ext.B, ext.A, D4   90: past that they lean into the arc of the next front's free edge
#   tall.lower   its pull meets the WC wall behind it at 88;  tall.upper  its face meets the horse plaque at 68
#   D1           its pull meets the hall wall at 90;  D2 / D3 hang on one partition and open face to face
#   washer       the hall wall is 0.14 m beyond its hinge
# Left as the room is built: base door A cannot swing while the sink door stands open in front of it (an inside
# corner: one of the two at a time).
# Keys are the group ids without the 'utility.' prefix.
OPEN = {'base.sink': 42, 'base.ext.B': 90, 'base.ext.A': 90, 'tall.lower': 85, 'tall.upper': 65,
        'wall.D1': -85, 'wall.D2': 80, 'wall.D3': -84, 'wall.D4': 90, 'wall.D5': 100, 'washer': -90, 'dryer': -100}
LINING = '#ECEAE4'          # carcass interiors: pale melamine
STOCK = ('#D9D5CB', '#C9C2B4', '#B7A58E', '#8E9AA3', '#A9B2A6', '#8497A6', '#CDBE85', '#9AA590', '#E6E2D8')   # muted

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


def _ring(mb, c, t, r, wire, mat, n=10, m=4):
    """Torus-like ring of radius r round centre c in the plane normal to t."""
    c, t = Vector(c), Vector(t).normalized()
    a = t.orthogonal().normalized()
    b = t.cross(a)
    _pipe(mb, [c + r * (math.cos(2 * math.pi * i / n) * a + math.sin(2 * math.pi * i / n) * b) for i in range(n)],
          wire, mat, t, n=m, closed=True)


def _retone(key, name, target, contrast=1.0, nrm=None):
    """Module-local copy of library material `key` whose base-colour texture is shifted so that its mean is
    `target` (sRGB hex), grain contrast scaled by `contrast`; nrm = normal-map strength. The texture is a JPG
    under blender/textures/art/utility/ (written once per target / contrast, then loaded like any other texture),
    so the copy is one Principled BSDF with constants + image files. Re-targeting the mean (not multiplying)
    keeps the result the same if the library colour is corrected later. The file name carries target and
    contrast: after changing either, delete the superseded JPG."""
    m = bpy.data.materials.get(name)
    if m is not None:
        return m
    m = M.mat(key).copy()
    m.name = name
    nodes = m.node_tree.nodes
    tex = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED').inputs['Base Color'].links[0].from_node
    path = os.path.normpath(os.path.join(ART, f'{key}_{target[1:]}_c{round(contrast * 100)}.jpg'))
    if not os.path.exists(path):
        w, h = tex.image.size
        px = np.empty(w * h * 4, np.float32)
        tex.image.pixels.foreach_get(px)                   # 8-bit image: values stay sRGB-encoded
        px = px.reshape(-1, 4)
        tgt = np.array([int(target[i:i + 2], 16) / 255 for i in (1, 3, 5)], np.float32)
        px[:, :3] = np.clip((px[:, :3] - px[:, :3].mean(0)) * contrast + tgt, 0, 1)
        img = bpy.data.images.new(name + '_tmp', w, h)
        img.pixels.foreach_set(px.ravel())
        tmp = path[:-4] + f'.{os.getpid()}.jpg'            # parallel builds: write aside, then move into place
        img.filepath_raw, img.file_format = tmp, 'JPEG'
        img.save(quality=90)
        bpy.data.images.remove(img)
        os.replace(tmp, path)
    tex.image = bpy.data.images.load(path, check_existing=True)
    if nrm is not None:
        next(n for n in nodes if n.type == 'NORMAL_MAP').inputs['Strength'].default_value = nrm
    return m


_DOORS = {}


def _door_mesh(w, h, mat, t=0.02, e=0.002):
    """Shaker cabinet front w x h: 75 mm stiles (grain vertical) and rails (grain horizontal) round a flat panel
    recessed REC behind a 16 mm quirk-and-ovolo bead. Origin: bottom centre of the back face, front = local -Y.
    Cached per size, so equal doors share one mesh."""
    key = (round(w, 4), round(h, 4))
    if key in _DOORS:
        return _DOORS[key]
    mb = mo.MB()
    x, s, yf, F = w / 2, STILE, -t, (0, -1, 0)
    for sx in (-1, 1):                                                                     # stiles, full height
        mb.face([(sx * (x - e), yf, e), (sx * (x - s), yf, e), (sx * (x - s), yf, h - e), (sx * (x - e), yf, h - e)],
                mat, F, 2)
    for za, zb in ((e, s), (h - s, h - e)):                                                # rails between them
        mb.face([(-x + s, yf, za), (x - s, yf, za), (x - s, yf, zb), (-x + s, yf, zb)], mat, F, 0)
    fr = [(-x + e, yf, e), (x - e, yf, e), (x - e, yf, h - e), (-x + e, yf, h - e)]        # front, arris, back rects
    ar = [(-x, yf + e, 0), (x, yf + e, 0), (x, yf + e, h), (-x, yf + e, h)]
    bk = [(-x, 0, 0), (x, 0, 0), (x, 0, h), (-x, 0, h)]
    for i, hint in enumerate(((0, 0, -1), (1, 0, 0), (0, 0, 1), (-1, 0, 0))):
        j = (i + 1) % 4
        mb.face([fr[i], fr[j], ar[j], ar[i]], mat, (hint[0], -1, hint[2]), 2)
        mb.face([ar[i], ar[j], bk[j], bk[i]], mat, hint, 2)
    mb.face(bk, mat, (0, 1, 0), 2)
    bead = [(0.016, -REC), (0.0135, -0.0085), (0.011, -0.0045), (0.008, -0.001), (0.0055, 0.0), (0.0035, -0.001),
            (0.0025, -0.003), (0.0, -0.003), (0.0, 0.0)]
    mb.sweep(bead, [(-x + s, yf, s), (x - s, yf, s), (x - s, yf, h - s), (-x + s, yf, h - s)], mat, closed=True, up=F)
    i = s + 0.016
    mb.face([(-x + i, yf + REC, i), (x - i, yf + REC, i), (x - i, yf + REC, h - i), (-x + i, yf + REC, h - i)], mat, F, 2)
    _DOORS[key] = mb.finish('utility.door', sharp_deg=30).data
    return _DOORS[key]


def _kids(root, *objs):
    """Parent objs to root (root sits at identity, so world placement is kept)."""
    for o in objs:
        o.parent = root
    return root


def _handle_mesh():
    """T-bar pull, antique bronze bar with brighter square clasps (f_0489): 220 long, 160 centres, 35 proud.
    Origin: door face, centre; bar along Z; front = local -Y. (The bar's fine knurl is not modelled.)"""
    mb = mo.MB()
    bar, col = M.solid('utility_handle_bar', '#4C463A', 0.42, 0.8), M.solid('utility_handle_collar', '#6C624B', 0.38, 0.8)
    yb = -0.029
    _lathe(mb, (0, yb, -0.11), Z, [(0, 0), (0.0050, 0), (0.006, 0.001), (0.006, 0.219), (0.0050, 0.22), (0, 0.22)], bar, 12)
    for s in (-1, 1):
        mb.box((-0.0085, yb - 0.0085, s * 0.08 - 0.013), (0.0085, yb + 0.0085, s * 0.08 + 0.013), col, bev=0.0015)   # clasp
        mb.box((-0.0065, yb, s * 0.08 - 0.009), (0.0065, 0, s * 0.08 + 0.009), col, bev=0.001)                       # its foot
    return mb.finish('utility.handle', sharp_deg=50).data


def _machine(name, dryer):
    """Graphite front-loader 598 x 850 x 550 (+ door). Origin floor centre, front = local -Y. No lettering.
    -> (body, door, drum): the porthole door (dished glass back) and the seal + drum behind it are separate objects
    parented to the body on the same origin; the body front has a dia 360 opening under the door."""
    mb = mo.MB()
    body = M.solid('utility_appliance_graphite', '#6A6A6C', 0.42)      # dark inox grey; dielectric, so it keeps its diffuse
    fascia = M.solid('utility_appliance_fascia', '#828286', 0.40)       # the raked control panel reads lighter
    trim = M.solid('appliance_graphite_dark', '#2E2E30', 0.35, 0.3)
    w, yf, yb, h = 0.299, -0.275, 0.275, 0.85
    for sx in (-1, 1):
        for y in (-0.22, 0.22):
            _lathe(mb, (sx * 0.25, y, 0), Z, [(0, 0), (0.02, 0), (0.02, 0.012), (0, 0.012)], 'black_matt', 10)
    old = set(mb.bm.faces)
    mb.box((-w, yf, 0.012), (w, yb, h), body, bev=0.006)
    for f in [f for f in mb.bm.faces if f not in old and all(abs(v.co.y - yf) < 1e-6 for v in f.verts)]:
        for v in list(f.verts):                            # the box's front face: rebuilt round the drum opening
            mb.bm.verts.remove(v)
    N, RO, cz = 40, 0.18, 0.42                             # the lathes below use the same N, so the rims coincide
    ring = [(RO * math.cos(2 * math.pi * i / N), yf, cz + RO * math.sin(2 * math.pi * i / N)) for i in range(N + 1)]
    corner = [(sx * (w - 0.006), yf, z) for sx, z in ((1, h - 0.006), (-1, h - 0.006), (-1, 0.018), (1, 0.018))]
    ang = [math.atan2(c[2] - cz, c[0]) for c in corner]
    near = lambda a: min(range(4), key=lambda k: abs((a - ang[k] + math.pi) % (2 * math.pi) - math.pi))
    for i in range(N):                                     # fan from each rim segment to the nearest corner
        k, k0 = near(2 * math.pi * (i + 0.5) / N), near(2 * math.pi * (i - 0.5) / N)
        mb.face([ring[i], ring[i + 1], corner[k]], body, (0, -1, 0))
        if k != k0:
            mb.face([ring[i], corner[k0], corner[k]], body, (0, -1, 0))
    mb.box((-w + 0.004, yf - 0.002, 0.722), (w - 0.004, yf, 0.846), fascia, bev=0.001)  # control panel
    mb.box((-w + 0.004, yf - 0.0015, 0.716), (w - 0.004, yf, 0.719), trim)             # fascia seam
    mb.box((-w + 0.004, yf - 0.0015, 0.098), (w - 0.004, yf, 0.101), trim)             # kick seam
    dx = 0.05 if dryer else -0.02                                                    # dial
    _lathe(mb, (dx, yf, 0.785), (0, -1, 0),
           [(0.040, 0), (0.040, 0.004), (0.035, 0.006), (0.035, 0.022), (0.032, 0.026), (0, 0.026)], 'chrome', 24)
    if dryer:
        mb.box((0.105, yf - 0.0035, 0.755), (0.275, yf, 0.815), 'black_gloss', bev=0.0008)   # display
        mb.box((0.105, yf - 0.002, 0.045), (0.265, yf, 0.170), 'black_matt')                 # vent grille
        for i in range(6):
            z = 0.056 + i * 0.019
            mb.box((0.108, yf - 0.006, z), (0.262, yf - 0.001, z + 0.010), body, bev=0.002)
    else:
        mb.box((-0.287, yf - 0.0045, 0.738), (-0.097, yf, 0.836), fascia, bev=0.002)         # detergent drawer
        mb.box((-0.250, yf - 0.008, 0.745), (-0.134, yf - 0.0045, 0.752), trim, bev=0.001)   # its finger pull
        mb.box((0.070, yf - 0.0035, 0.755), (0.262, yf, 0.815), 'black_gloss', bev=0.0008)   # display
    ob = mb.finish(name, sharp_deg=50)
    # door: graphite rim, wide chrome ring, dark glass dish. Centre 0.42 above the floor, dia 490. Lathe z = out of
    # the front; the back is a dark trim ring 1 mm off the body and the glass bowl that reaches into the drum.
    c, out = (0, yf, cz), (0, -1, 0)
    mb = mo.MB()
    _lathe(mb, c, out, [(0.245, 0), (0.245, 0.016), (0.240, 0.022), (0.232, 0.024)], body, N)
    _lathe(mb, c, out, [(0.232, 0.024), (0.226, 0.034), (0.212, 0.038), (0.196, 0.034), (0.192, 0.026)], 'chrome', N)
    _lathe(mb, c, out, [(0.192, 0.026), (0.165, 0.016), (0.10, 0.006), (0, 0.004)], 'black_gloss', N)
    mb.box((0.218, yf - 0.040, 0.39), (0.243, yf - 0.020, 0.45), trim, bev=0.004)            # door catch / grip
    _lathe(mb, c, out, [(0, -0.070), (0.07, -0.064), (0.125, -0.045), (0.155, -0.018), (0.163, 0.001)], 'black_gloss', N)
    _lathe(mb, c, out, [(0.163, 0.001), (0.245, 0.001)], trim, N)
    door = mb.finish(name + '.door', sharp_deg=50)
    # behind it: grey rubber seal, brushed steel drum dia 450 with a hub and three lifters
    mb = mo.MB()
    _lathe(mb, c, out, [(RO, 0), (RO, -0.03), (0.165, -0.055)], M.solid('utility_door_seal', '#56595D', 0.6), N)
    _lathe(mb, c, out, [(0.225, -0.055), (0.225, -0.40), (0.05, -0.40), (0.05, -0.385), (0, -0.385)], 'steel_brushed', N)
    lifter = M.solid('utility_drum_lifter', '#C6C9CC', 0.45)
    for k in range(3):
        mb.at(Matrix.Translation(c) @ Z.rotation_difference(Vector(out)).to_matrix().to_4x4()
              @ Matrix.Rotation(math.radians(90 + 120 * k), 4, 'Z'))
        mb.box((0.193, -0.024, -0.37), (0.227, 0.024, -0.09), lifter, bev=0.008)
    mb.at()
    drum = mb.finish(name + '.drum', sharp_deg=50)
    door.parent = drum.parent = ob
    return ob, door, drum


def _tap(name, x, y, z):
    """Chrome spring-neck pull-down mixer on the worktop at (x, y, z); arches toward -Y over the sink.
    0.40 m tall (hr_0477: 180 px against 215 px from worktop to wall cabinets), so the arch clears the cabinets.
    -> (tap, lever): the side lever is its own object; it lifts about the y axis through (x + 0.020, y, z + 0.082)."""
    ch = 'chrome'
    mb = mo.MB()
    _pipe(mb, [(x + 0.020, y, z + 0.082), (x + 0.088, y, z + 0.100)], 0.006, ch, (0, 1, 0))          # side lever
    _lathe(mb, (x + 0.088, y, z + 0.100), (1, 0, 0.26), [(0, -0.002), (0.0085, 0), (0.0085, 0.010), (0, 0.012)], ch, 10)
    lever = mb.finish(name + '.lever', sharp_deg=50)
    mb = mo.MB()
    _lathe(mb, (x, y, z), Z, [(0, 0), (0.031, 0), (0.031, 0.004), (0.025, 0.008), (0.025, 0.112),
                              (0.021, 0.120), (0.011, 0.124), (0, 0.124)], ch, 20)
    R, zs, za = 0.09, 0.22, 0.29                           # arch radius, coil start / spring line above the deck
    _pipe(mb, [(x, y, z + 0.12), (x, y, z + zs)], 0.010, ch, (1, 0, 0))                                # riser
    cl = [(Vector((x, y, z + zs)), Z), (Vector((x, y, z + za)), Z)]                                    # centre line + tangent
    for i in range(1, 16):
        a = math.pi * i / 16
        cl.append((Vector((x, y - R + R * math.cos(a), z + za + R * math.sin(a))), Vector((0, -math.sin(a), math.cos(a)))))
    cl += [(Vector((x, y - 2 * R, z + za)), -Z), (Vector((x, y - 2 * R, z + zs)), -Z)]
    _pipe(mb, [p for p, _ in cl], 0.008, 'steel_brushed', (1, 0, 0), n=6)                           # hose in the coil
    pitch, acc = 0.011, 0.0
    for (p0, t0), (p1, t1) in zip(cl, cl[1:]):                                                         # spring = stacked rings
        seg = (p1 - p0).length
        while acc < seg:
            f = acc / seg
            _ring(mb, p0.lerp(p1, f), t0.lerp(t1, f), 0.0145, 0.0030, ch, n=10, m=4)
            acc += pitch
        acc -= seg
    xs, ys = x, y - 2 * R                                                                              # hand spray
    _lathe(mb, (xs, ys, z + zs - 0.115), Z, [(0, 0), (0.016, 0), (0.019, 0.006), (0.019, 0.030), (0.0135, 0.040),
                                             (0.0135, 0.118), (0, 0.120)], ch, 14)
    zarm = z + zs - 0.055                                                                              # support arm
    _pipe(mb, [(x, y, zarm), (xs, ys + 0.018, zarm)], 0.005, ch, (1, 0, 0), n=8)
    _ring(mb, (xs, ys, zarm), Z, 0.0165, 0.0035, ch, n=14)
    _ring(mb, (x, y, zarm), Z, 0.0125, 0.004, ch, n=14)
    return mb.finish(name, sharp_deg=50), lever


def _stock(name, rows, seed=4):
    """What the cupboards hold, one mesh in world coordinates: plain cartons, folded cloths and bottles (no labels).
    rows: (axis, a, b, d0, d1, z, clear) = a row along world axis 0 | 1 from a to b on a shelf at height z with
    `clear` headroom; things stand between d0 (the front) and d1 (the back) on the other horizontal axis."""
    rnd, mb = random.Random(seed), mo.MB()

    def tint(rough):
        hx = rnd.choice(STOCK)
        return M.solid(f'utility_stock_{hx[1:]}_{round(rough * 100)}', hx, rough)

    for axis, a, b, d0, d1, z, clear in rows:
        p = a + rnd.uniform(0.01, 0.05)
        while True:
            lo, hi = [0.0, 0.0, z], [0.0, 0.0, z]
            if rnd.random() < 0.45:                                                         # bottle
                r, h = rnd.uniform(0.035, 0.05), rnd.uniform(0.55, 0.85) * min(clear, 0.36)
                if p + 2 * r > b:
                    break
                lo[axis], lo[1 - axis] = p + r, d0 + r + (d1 - d0 - 2 * r) * rnd.uniform(0.2, 0.6)
                _lathe(mb, lo, Z, [(0, 0), (r, 0), (r, 0.68 * h), (0.42 * r, 0.84 * h), (0.42 * r, 0.93 * h)], tint(0.35), 12)
                _lathe(mb, (lo[0], lo[1], z + 0.93 * h), Z, [(0.48 * r, 0), (0.48 * r, 0.07 * h), (0, 0.07 * h)],
                       M.solid('utility_stock_cap', '#E8E6E0', 0.4), 12)
                p += 2 * r + rnd.uniform(0.02, 0.07)
            else:                                                                           # carton / folded cloths
                w, h = rnd.uniform(0.14, 0.30), rnd.uniform(0.4, 0.8) * min(clear, 0.30)
                if p + w > b:
                    break
                lo[axis], hi[axis], hi[2] = p, p + w, z + h
                lo[1 - axis] = d0 + (d1 - d0) * rnd.uniform(0.0, 0.25)
                hi[1 - axis] = min(d1, lo[1 - axis] + rnd.uniform(0.16, 0.26))
                mb.box(lo, hi, tint(0.7), bev=0.004)
                p += w + rnd.uniform(0.02, 0.07)
    return mb.finish(name, sharp_deg=50)


def _trap(name, x, y, z_top, z_out, y_wall):
    """White plastic sink waste: tail pipe down from (x, y, z_top), bottle trap, outlet back to the wall."""
    mb = mo.MB()
    w = 'plastic_white'
    _lathe(mb, (x, y, z_out - 0.085), Z, [(0, 0), (0.030, 0), (0.034, 0.008), (0.034, 0.090), (0.029, 0.100),
                                          (0.020, 0.100), (0.020, z_top - z_out + 0.085)], w, 16)
    _lathe(mb, (x, y, z_out + 0.045), Z, [(0.027, 0), (0.027, 0.022), (0.020, 0.022)], w, 16)         # compression nut
    _lathe(mb, (x, y + 0.030, z_out - 0.035), (0, 1, 0), [(0.020, 0), (0.020, y_wall - y - 0.030)], w, 16)
    _lathe(mb, (x, y_wall, z_out - 0.035), (0, -1, 0), [(0.032, 0), (0.032, 0.004), (0.020, 0.005)], w, 16)   # wall collar
    return mb.finish(name, sharp_deg=50)


def _sink(name):
    """Belfast sink, white fireclay 595 x 460 x 220, 25 mm walls with a rounded rim; apron 20 mm proud of the doors.
    Undermounted: the worktop cut-out overhangs the side and back walls, only bowl and front apron show (f_0489)."""
    mb = mo.MB()
    c = 'ceramic_white'
    x0, x1, y0, y1, z0 = 1.9125, 2.5075, 11.59, 12.05, SINK_Z0
    wall = [(0.025, 0.020), (0.025, 0.208), (0.022, 0.216), (0.0125, 0.220), (0.003, 0.216), (0.0, 0.208), (0.0, 0.006),
            (0.006, 0.0)]
    mb.sweep(wall, [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], c, closed=True)
    mb.box((x0 + 0.01, y0 + 0.01, z0 + 0.001), (x1 - 0.01, y1 - 0.01, z0 + 0.026), c)
    mb.box((x1 - 0.037, 11.77, z0 + 0.026), (x1 - 0.024, 11.87, z0 + 0.185), c, bev=0.004)          # weir overflow
    mb.box((x1 - 0.0375, 11.785, z0 + 0.150), (x1 - 0.0365, 11.855, z0 + 0.172), 'black_matt')
    wc = (2.25, 11.85, z0 + 0.026)                                                                  # basket waste
    _lathe(mb, wc, Z, [(0.045, 0), (0.045, 0.003), (0.040, 0.0035), (0.024, 0.0012)], 'chrome', 20)
    _lathe(mb, wc, Z, [(0.024, 0.0012), (0.009, 0.0008)], 'black_matt', 20)                         # dark strainer well
    _lathe(mb, wc, Z, [(0.009, 0.0008), (0.009, 0.004), (0.006, 0.006), (0, 0.006)], 'chrome', 12)  # centre post
    for i in range(8):                                                                              # slots in the flange
        mb.at(Matrix.Translation(wc) @ Matrix.Rotation(math.pi * i / 4, 4, 'Z'))
        mb.box((0.0275, -0.0015, 0.0018), (0.0375, 0.0015, 0.0042), 'black_matt')
    mb.at()
    return mb.finish(name, sharp_deg=50)


def _worktops(o):
    """Oak stave L-shaped worktop (material o), 40 mm -> (piece 1, piece 2). Piece 1 along W-rear (staves along x)
    with the sink cut-out open to the front and 7 drainer grooves on the corner square; piece 2 along W-ext
    (staves along y). The cut-out edges stand 2.5 / 5 mm inside the sink walls and cover its rim.
    Two objects: one L-shaped object would get a plan footprint covering the aisle."""
    mb = mo.MB()
    z0 = TOP - 0.04
    yb = 12.02                                                    # back edge of the cut-out (sink inner face 12.025)
    mb.box((X0, yb, z0), (X1, Y1, TOP), o, bev=0.003, grain=0)                       # strip behind the sink, full length
    mb.box((X0, YF - 0.02, z0), (1.94, yb, TOP), o, bev=0.003, grain=0)              # over washer + dryer
    gx0, gx1, gy0, n, pitch, gw = 2.48, 2.93, 11.739, 7, 0.045, 0.012                # drainer: grooves along x
    gy1 = gy0 + (n - 1) * pitch + gw
    mb.box((gx0, YF - 0.02, z0), (X1, gy0, TOP), o, bev=0.003, grain=0)
    mb.box((gx0, gy1, z0), (X1, yb, TOP), o, grain=0)
    mb.box((gx1, gy0, z0), (X1, gy1, TOP), o, grain=0)
    mb.box((gx0, gy0, z0), (gx1, gy1, TOP - 0.005), o, grain=0)                      # groove floor
    for i in range(n - 1):
        y = gy0 + gw + i * pitch
        mb.box((gx0, y, TOP - 0.005), (gx1, y + pitch - gw, TOP), o, bev=0.0015, grain=0)
    rear = mb.finish('utility.worktop.rear', sharp_deg=50)
    mb = mo.MB()
    mb.box((XF - 0.04, 10.88, z0), (X1, YF - 0.02, TOP), o, bev=0.003, grain=1)      # piece 2
    return rear, mb.finish('utility.worktop.ext', sharp_deg=50)


def _airer(name, y=11.38, z=2.10, cz=2.40):
    """Ceiling clothes rail: chrome tube dia 25 along x on three drop rods with ceiling flanges. Empty."""
    mb = mo.MB()
    ch = 'chrome'
    _lathe(mb, (0.90, y, z), (1, 0, 0), [(0, 0), (0.010, 0), (0.0125, 0.003), (0.0125, 1.897), (0.010, 1.90), (0, 1.90)], ch, 16)
    for x in (1.05, 1.85, 2.65):
        _lathe(mb, (x, y, z), Z, [(0.008, 0), (0.008, cz - z - 0.008)], ch, 12)                       # drop rod
        _lathe(mb, (x, y, cz), (0, 0, -1), [(0, 0), (0.030, 0), (0.030, 0.004), (0.014, 0.010), (0.011, 0.030),
                                            (0.008, 0.030)], ch, 20)                                # ceiling flange
        _lathe(mb, (x - 0.02, y, z), (1, 0, 0), [(0, 0), (0.0165, 0), (0.0165, 0.04), (0, 0.04)], ch, 16)    # T clamp
    return mb.finish(name, sharp_deg=50)


# ----------------------------------------------------------------------------- build
def build(ctx):
    cz = ctx.ceil_z(ROOM)
    hmesh = _handle_mesh()
    count = [0]

    def handle(x, y, zc, facing):
        count[0] += 1
        return P.place(bpy.data.objects.new(f'utility.handle.{count[0]:02d}', hmesh), (x, y, zc), facing=facing)

    # Local re-toned copies of two library materials (requests are in the fix report): the video shows a warm dove
    # grey with a faint ash grain (wall cabinets clearly darker than the tiles, f_0476; the tall cupboard under its
    # downlight nearly as light as the wall, f_0455 / f_0495) and a muted honey-olive oiled butcher block with fine
    # grain (f_0489).
    GREY = _retone('grey_cabinet', 'utility_grey_cabinet', GREY_HEX, contrast=0.6, nrm=0.45)
    OAK = _retone('oak_worktop', 'utility_oak_worktop', OAK_HEX, contrast=OAK_CONTRAST)

    def door(w, h, x, y, z, facing, name):
        return P.place(bpy.data.objects.new(name, _door_mesh(w, h, GREY)), (x, y, z), facing=facing)

    S, W = (0, -1), (-1, 0)                 # room-side normals of W-rear (faces -Y) and W-ext (faces -X)
    dyn = []                                # what moves and what it reveals: lm='dynamic' (set at the end of build)

    def front(key, pivot, *objs, label='Cupboard'):
        """objs (a front and its pull) = hinge group 'utility.<key>' about the vertical through `pivot` - the
        front's outer corner on its hinge side, so the opened front never enters the carcass or its neighbour."""
        dyn.extend(IX.tag_many(objs, 'hinge', g='utility.' + key, label=label, p=pivot, deg=OPEN[key]))
        return objs

    def carcass(w, d, h, loc, facing, name, **kw):
        """Open-fronted, lined cabinet box behind fronts that open (outside as the plain box it replaces)."""
        dyn.append(P.place(P.cabinet_carcass(w, d, h, mat=GREY, open_front=True, inner=LINING, name=name, **kw),
                           loc, facing=facing))
        return dyn[-1]

    # ---- W-rear base run: filler | washer | dryer | Belfast sink unit | corner post
    mb = mo.MB()
    mb.box((X0, YF - 0.02, 0), (0.69, YF, TOP - 0.04), GREY, bev=0.001)                    # end filler, floor to worktop
    filler = mb.finish('utility.base.filler')
    ctx.add(filler, ROOM, 'fit')

    for sym, x, label in (('washer', 0.99, 'Washing machine'), ('dryer', 1.605, 'Tumble dryer')):
        ob, porthole, drum = _machine('utility.' + sym, dryer=sym == 'dryer')
        ob.location = (x, 11.925, 0)
        front(sym, (x - 0.245, 11.925 - 0.275 - 0.016, 0.42), porthole, label=label)       # left edge of the door rim
        dyn.append(drum)
        ctx.add(ob, ROOM, 'fit', plan_sym=sym)

    mb = mo.MB()
    zr = SINK_Z0 - 0.002                                                                   # top of the rail / carcass
    mb.box((1.91, YF - 0.02, zr - 0.04), (2.51, YF, zr), GREY, bev=0.001)                  # rail under the apron
    mb.box((XF - 0.02, A_Y0 + A_W + 0.003, 0.15), (XF, YF, TOP - 0.04), GREY, bev=0.001)   # corner post + filler up to door A
    mb.box((XF - 0.02, YF + 0.03, 0), (XF, YF + 0.05, 0.15), GREY)                         # its plinth return
    base = mb.finish('utility.base.sink_unit')
    trap = _trap('utility.base.sink_trap', 2.25, 11.85, zr - 0.018, 0.47, Y1 - 0.006)
    dyn.append(trap)
    _kids(base,
          carcass(0.60, Y1 - YF, zr, (2.21, Y1, 0), S, 'utility.base.sink_carcass'), trap,
          *front('base.sink', (2.508, YF - 0.02, 0.155),
                 door(0.596, zr - 0.044 - 0.155, 2.21, YF, 0.155, S, 'utility.base.sink_door'),
                 handle(1.955, YF - 0.02, zr - 0.044 - 0.06 - 0.11, S)))
    ctx.add(base, ROOM, 'fit', plan_sym='base_unit')

    # the tap: lever lifts 20 deg, one stream from the hand spray (outlet z 1.015) to the floor of the bowl
    sink = _sink('utility.sink')
    tap, lever = _tap('utility.tap', 2.15, 12.17, TOP)
    water = P.place(P.water_stream(1.015 - (SINK_Z0 + 0.026), name='utility.tap.water'), (2.15, 11.99, 1.015))
    IX.tag(tap, 'trigger', g='utility.tap', label='Tap')
    IX.tag(lever, 'hinge', g='utility.tap', label='Tap', p=(2.17, 12.17, TOP + 0.082), a=(0, 1, 0), deg=-20)
    IX.tag(water, 'show', g='utility.tap', label='Tap', when=1, fx='water')
    dyn.append(lever)
    _kids(sink, tap, lever)
    ctx.add(sink, ROOM, 'fit', plan_sym='sink_belfast')
    ctx.add(water, ROOM, 'fit', lm='dynamic')

    # ---- W-ext base run: two 365 units. Doors B (y 10.88..11.245) and A (11.245..11.587) both hang on their -y
    #      edge, handles at the top +y corner. A stops A_W from its hinge, short of the sink apron (see A_W); the
    #      corner post of the sink unit runs on as a filler over the rest of A's carcass.
    ext = carcass(0.365, X1 - XF, TOP - 0.04, (X1, 11.0625, 0), W, 'utility.base.ext', shelves=1)
    kids = [carcass(0.365, X1 - XF, TOP - 0.04, (X1, 11.4275, 0), W, 'utility.base.ext.A', shelves=1)]
    for k, y0, w in (('B', 10.8815, 0.362), ('A', A_Y0, A_W)):                             # hinge edge, width
        kids += front('base.ext.' + k, (XF - 0.02, y0, 0.152),
                      door(w, 0.716, XF, y0 + w / 2, 0.152, W, f'utility.base.ext_door.{k}'),
                      handle(XF - 0.02, y0 + w - 0.045, 0.868 - 0.06 - 0.11, W))
    for o in kids:                                         # ext is a rotated prop: keep the children's world placement
        o.parent = ext
        o.matrix_parent_inverse = ext.matrix_basis.inverted()
    ctx.add(ext, ROOM, 'fit', plan_sym='base_unit')

    for wt in _worktops(OAK):
        ctx.add(wt, ROOM, 'fit', plan_sym='worktop')

    # ---- tall cupboard x 2.53..3.10, y 10.28..10.88; lower door 0.15..1.395, upper 1.40..2.295, top board 2.31
    mb = mo.MB()
    mb.box((XF - 0.02, Y0, 0), (X1, 10.28, 2.31), GREY, bev=0.001)                         # scribe filler against W-wc
    mb.box((XF - 0.03, 10.28, WALL_Z1), (X1, 10.88, 2.31), GREY, bev=0.002)                # top board, 10 mm overhang
    tall = mb.finish('utility.tall')
    _kids(tall,
          carcass(0.60, X1 - XF, WALL_Z1, (X1, 10.58, 0), W, 'utility.tall.carcass', shelves=4),
          *front('tall.lower', (XF - 0.02, 10.282, 0.152), door(0.596, 1.243, XF, 10.58, 0.152, W, 'utility.tall.door_lower'),
                 handle(XF - 0.02, 10.88 - 0.047, 1.21, W), label='Tall cupboard'),
          *front('tall.upper', (XF - 0.02, 10.282, 1.400), door(0.596, 0.893, XF, 10.58, 1.400, W, 'utility.tall.door_upper'),
                 handle(XF - 0.02, 10.88 - 0.047, 1.56, W), label='Tall cupboard'))
    ctx.add(tall, ROOM, 'fit', plan_sym='tall_unit')

    # ---- wall cabinets on W-rear: D1 D2 (300) | D3 D4 (500) | D5 (300, vent slots); fronts at y 11.90
    yw = Y1 - 0.31                                                                         # carcass front 11.92
    mb = mo.MB()
    mb.box((X0, yw - 0.02, WALL_Z0), (0.64, Y1, WALL_Z1), GREY, bev=0.001)                 # scribe filler
    mb.box((0.64, yw - 0.02, WALL_Z0 - 0.016), (2.56, yw - 0.002, WALL_Z0), GREY, bev=0.001)    # light pelmet
    mb.box((0.66, 12.150, WALL_Z0 - 0.006), (2.54, 12.166, WALL_Z0), P.emissive('#FFC489', 6.0))   # LED strip body: ~3400 K, reads neutral under the 3000 K view white balance
    wall = mb.finish('utility.wall_units')
    mb = mo.MB()
    yp = yw - 0.02 + REC                                                                   # panel face of the doors
    for z in (2.130, 2.153):                                                               # D5 vent slots, on its panel
        mb.box((2.338, yp - 0.0012, z), (2.442, yp + 0.0005, z + 0.008), 'black_matt')
    vents = mb.finish('utility.wall.door.D5.vents')
    kids = [carcass(xb - xa, 0.31, WALL_Z1 - WALL_Z0, ((xa + xb) / 2, Y1, WALL_Z0), S, f'utility.wall.carcass.{i}',
                    plinth=0, shelves=2)
            for i, (xa, xb) in enumerate(((0.64, 1.24), (1.24, 2.24), (2.24, 2.56)))]      # 600 | 1000 | 300 + end panel
    zh = WALL_Z0 + 0.06 + 0.11
    for i, (xa, xb, hx) in enumerate(((0.64, 0.94, 0.895), (0.94, 1.24, 0.985), (1.24, 1.74, 1.695),
                                      (1.74, 2.24, 1.785), (2.24, 2.54, 2.285))):
        k = f'wall.D{i + 1}'                                                               # hinge on the side away from the pull
        kids += front(k, (xa + 0.0015 if OPEN[k] < 0 else xb - 0.0015, yw - 0.02, WALL_Z0 + 0.0015),
                      door(xb - xa - 0.003, WALL_Z1 - WALL_Z0 - 0.003, (xa + xb) / 2, yw, WALL_Z0 + 0.0015, S,
                           f'utility.wall.door.D{i + 1}'),
                      handle(hx, yw - 0.02, zh, S), *([vents] if i == 4 else []))
    _kids(wall, *kids)
    ctx.add(wall, ROOM, 'fit', plan_sym='wall_unit')

    # ---- what the cupboards hold (rows: axis, from, to, front, back, shelf z, headroom)
    rows = [(0, 1.95, 2.20, 11.78, 12.19, 0.168, 0.26), (0, 2.31, 2.47, 11.78, 12.19, 0.168, 0.26)]          # under the sink
    rows += [(1, y, y + 0.31, 2.60, 3.06, z, 0.32) for y in (10.905, 11.27) for z in (0.168, 0.519)]         # base B, A
    rows += [(1, 10.31, 10.85, 2.60, 3.06, z, 0.40) for z in (0.168, 0.599, 1.021, 1.443, 1.865)]            # tall cupboard
    rows += [(0, xa + 0.03, xb - 0.03, 11.96, 12.20, z, 0.27)
             for xa, xb in ((0.64, 1.24), (1.24, 2.24), (2.24, 2.56)) for z in (1.413, 1.710, 1.998)]        # wall units
    dyn.append(ctx.add(_stock('utility.stock', rows), ROOM, 'fit'))

    # ---- marble metro splashbacks, 2 mm proud: W-rear full length, W-ext cut round the window reveal
    ob = shell.box('utility.splash.rear', X0, X1, Y1 - 0.002, Y1, TOP, WALL_Z0, 'marble_metro')
    M.uv_box(ob, origin=(0.729, 0, TOP))                   # first joint of the top course 0.28 m from the hall corner
    ctx.add(ob, ROOM, 'fit')
    for i, (ya, yb, zt) in enumerate(((10.88, 11.33, 1.39), (11.33, 11.89, 1.05), (11.89, Y1 - 0.002, 1.39))):
        ob = shell.box(f'utility.splash.ext.{i}', X1 - 0.002, X1, ya, yb, TOP, zt, 'marble_metro')
        M.uv_box(ob, origin=(0, Y1, TOP))
        ctx.add(ob, ROOM, 'fit')

    # ---- electrical. The grid by the hall door switches this room; the plate under the plaque is the WC light
    #      (the WC has no switch inside); the high plate is the WC fan isolator - nothing to show, not tagged.
    for name, prop, loc, n, lit in (
            ('utility.socket.rear', P.socket(2), (0.815, Y1 - 0.002, 1.10), S, None),
            ('utility.socket.corner', P.socket(1), (2.90, Y1 - 0.002, 1.10), S, None),
            ('utility.switch.grid', P.switch_plate(3, 'rocker', wide=False), (X0, 11.29, 1.27), (1, 0), 'utility'),
            ('utility.switch.fan', P.switch_plate(1, 'rocker'), (2.34, Y0, 2.02), (0, 1), None),
            ('utility.switch.light', P.switch_plate(1, 'rocker'), (2.32, Y0, 1.22), (0, 1), 'wc')):
        prop.name = name
        ctx.add(P.place(prop, loc, facing=n), ROOM, 'fit')
        if lit:
            IX.tag(prop, 'light', rooms=[lit], label='Lights' if lit == ROOM else 'WC light')

    # ---- bronze horse relief plaque on W-wc (rectified crop, no people): metallic face in a pale champagne frame.
    #      The library's metallic golds render orange under the lamps (f_0495 frame: #A39665), so the frame of this
    #      (own, unshared) mesh gets a satin paint-like gold, as print 4 in the WC.
    img = os.path.join(ART, 'plaque_horses.jpg')
    bsdf = next(n for n in P.image_mat(img).node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Metallic'].default_value, bsdf.inputs['Roughness'].default_value = 0.6, 0.4
    plaque = P.framed_picture(img, 0.265, 0.33, 'champagne', frame_w=0.035, depth=0.030, name='utility.plaque')
    plaque.data = plaque.data.copy()
    gold, pale = P.mat('champagne'), M.solid('utility_frame_champagne', '#A89A60', 0.45)
    for i, m in enumerate(plaque.data.materials):
        if m == gold:
            plaque.data.materials[i] = pale
    ctx.add(P.place(plaque, (2.35, Y0, 1.62), facing=(0, 1)), ROOM, 'decor')

    # ---- ceiling clothes rail (empty)
    ctx.add(_airer('utility.airer', cz=cz), ROOM, 'fit', plan_sym='airer', lm='dynamic')

    # ---- lighting: 2 downlights on the room centre line + the under-cabinet strip (neutral-warm white in the video)
    #      + an invisible up-fill for the ceiling (the spots only shine down; the video's ceiling is near white).
    #      The second downlight stands 0.4 m in front of the tall cupboard (f_0455), so its doors are lit face-on.
    for i, x in enumerate((1.30, 2.15)):
        lighting.downlight(ctx, ROOM, x, 11.245, watts=DOWN_W, kelvin=3000, spot_deg=160, name=f'utility.downlight.{i}')
        ctx.add(P.place(P.downlight(name=f'utility.downlight_trim.{i}'), (x, 11.245, cz)), ROOM, 'light')
    lighting.strip(ctx, ROOM, (0.68, 12.158, WALL_Z0 - 0.03), (2.52, 12.158, WALL_Z0 - 0.03), watts_per_m=STRIP_W,
                   kelvin=3200, name='utility.strip')
    for i, (ya, yb) in enumerate(((10.45, 11.33), (11.43, 11.85))):        # two upward panels, clear of the airer rods
        up = lighting.strip(ctx, ROOM, (0.9, (ya + yb) / 2, cz - 0.30), (2.4, (ya + yb) / 2, cz - 0.30),
                            watts_per_m=UP_W_M2 * (yb - ya), kelvin=3000, width=yb - ya, direction=(0, 0, 1),
                            name=f'utility.upfill.{i}')
        up.visible_camera = up.visible_glossy = False

    for o in dyn:                                          # after every ctx.add: a root's add resets its children
        o['lm'] = 'dynamic'


DOWN_W = 80         # per downlight; tuned so the previews match the video (median luminance 0.56, f_0476 / hr_0477)
STRIP_W = 5.5       # W per metre of under-cabinet strip
UP_W_M2 = 4.0       # ceiling up-fill, W per m2 of panel
GREY_HEX = '#AAA8A5'        # cabinet paint (texture mean)
OAK_HEX, OAK_CONTRAST = '#90804A', 1.0

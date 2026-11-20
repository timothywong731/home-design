"""Front forecourt (spec/rooms/front.md, spec/phase2/front_elevation.md 5 and 8): the two cars, wall planters with
bellflowers, the flag, bins, doorbell, outdoor socket, the security camera on the bay corner, access covers, and
the lamp column / street tree backdrop. Paving, wall, pier, facade and porch come from site / envelope; the three canopy
downlights ("outside lights") and their switches come from rooms/vestibule.py.

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --levels G,X --only shell,site,envelope,front \
        --preview front --res 540x960 --samples 64 --tag front
"""
import math

import bpy
from mathutils import Matrix, Vector

from lib import props as P, shell
from rooms import front_car as CAR, front_parts as FP

ROOM = 'front'

# refs: reference/work/p2_front_ext/<ref>.jpg (v2_tNNN = v2 frame f_(NNN+1), v4_tNN = v4 frame f_(NN+1))
CAMERAS = [
    dict(name='street', pos=(2.0, -11.0, 1.6), look=(2.0, 0.0, 2.6), fov_deg=75, ref=None),
    dict(name='doorway', pos=(0.1, -0.25, 1.5), look=(1.3, -3.0, 0.5), fov_deg=100, ref='v2_t944'),
    dict(name='path', pos=(-0.2, -0.9, 1.4), look=(-0.55, -4.6, 0.5), fov_deg=100, ref='v2_t948'),
    dict(name='facade', pos=(-0.1, -0.75, 1.5), look=(3.2, -0.25, 1.2), fov_deg=100, ref='v2_t952'),
    dict(name='flag', pos=(-0.1, -1.0, 1.5), look=(1.4, 0.4, 3.3), fov_deg=100, ref='v2_t954'),
    dict(name='canopy', pos=(0.2, -0.75, 1.5), look=(0.0, -0.2, 2.9), fov_deg=100, ref='v2_t958'),
    dict(name='above', pos=(2.0, -0.3, 4.8), look=(2.0, -3.6, 0.0), fov_deg=100, ref='v4_t48'),
    dict(name='bins', pos=(3.2, -0.3, 4.8), look=(4.5, -2.2, 0.0), fov_deg=100, ref='v4_t51'),
    dict(name='west', pos=(3.3, -0.3, 4.8), look=(-1.2, -2.7, 1.6), fov_deg=100, ref='v4_t63'),
    dict(name='noses', pos=(1.9, -7.4, 1.5), look=(1.9, -3.5, 0.7), fov_deg=80, ref=None),
    dict(name='white', pos=(-0.35, -0.45, 1.45), look=(4.0, -1.5, 0.45), fov_deg=100, ref='v2_t970'),
    dict(name='door', pos=(0.45, -1.75, 1.5), look=(0.25, 0.0, 1.75), fov_deg=100, ref='v2_t963'),
    dict(name='grey', pos=(-0.45, -5.6, 1.2), look=(0.9, -3.0, 0.7), fov_deg=80, ref=None),
    dict(name='wallend', pos=(0.1, -0.15, 1.5), look=(-0.4, -3.0, 0.45), fov_deg=100, ref='v2_t946'),
]


def _feature(ctx, fid):
    return next(f for f in ctx.spec['exterior']['features'] if f['id'] == fid)


def _hit(origin, direction, default, dist=1.5):
    """First surface of what is already built along a ray -> hit point, else `default`."""
    bpy.context.view_layer.update()
    ok, loc, *_ = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph, Vector(origin), Vector(direction), distance=dist)
    return loc if ok else Vector(default)


def _on_ground(ctx, ob, x, y, lift=0.0, half=0.3):
    """Stand an object on the paving at (x, y), tipped to its fall along Y."""
    z0, z1 = ctx.ground_z(x, y - half), ctx.ground_z(x, y + half)
    ob.matrix_world = Matrix.Translation((x, y, (z0 + z1) / 2 + lift)) @ Matrix.Rotation(math.atan2(z1 - z0, 2 * half), 4, 'X') \
        @ ob.matrix_basis                                           # matrix_basis: current even before the object is linked
    return ob


def _car(ctx, fid, S):
    """One car from exterior.features: nose out (-Y), square to the street, wheels on the falling paving."""
    f = _feature(ctx, fid)
    cx, cy = f['center']
    yaw = Matrix.Rotation(math.radians(f.get('yawDeg', 0)), 4, 'Z')
    ax = [Vector((cx, cy, 0)) + yaw @ Vector((0, t - S['L'] / 2, 0)) for t in S['axles']]
    zf, zr = (ctx.ground_z(p.x, p.y) for p in ax)
    wb = S['axles'][1] - S['axles'][0]
    Mc = (Matrix.Translation((cx, cy, zf + (zr - zf) * (S['L'] / 2 - S['axles'][0]) / wb)) @ yaw
          @ Matrix.Rotation(math.atan2(zr - zf, wb), 4, 'X'))
    body, wheels, mirrors = CAR.car(S, 'front.' + fid)
    body.matrix_world = Mc
    ctx.add(body, ROOM, 'furn', plan_sym='car')
    mirrors.matrix_world = Mc                                       # own object: the plan footprint is the body alone
    ctx.add(mirrors, ROOM, 'furn')
    for ob, Mw in wheels:
        ob.matrix_world = Mc @ Mw
        ctx.add(ob, ROOM, 'furn')


def build(ctx):
    # --- the two cars: grey to the west, white to the east (owner correction: yaw 0, long axis along Y)
    _car(ctx, 'car_grey', CAR.GREY)
    _car(ctx, 'car_white', CAR.WHITE)

    # --- timber troughs and bellflowers on the west wall
    troughs, foliage = FP.planter(ctx)
    ctx.add(troughs, ROOM, 'fit', plan_sym='planter')
    ctx.add(foliage, ROOM, 'decor')                                 # no plan symbol: it overhangs the path, it does not block it

    # --- flag on its 45-degree pole, bracket on the pilaster between the door and the bay (plan symbol: the bracket)
    bx, by, bz = _feature(ctx, 'flag')['bracket']
    wall = _hit((bx, by - 0.5, bz), (0, 1, 0), (bx, by, bz))
    bracket, pole, cloth = FP.flag((bx, wall.y, bz), _feature(ctx, 'flag')['pole'], _feature(ctx, 'flag')['flagSize'])
    ctx.add(bracket, ROOM, 'fit', plan_sym='flagpole', lm='dynamic')
    ctx.add(pole, ROOM, 'fit', lm='dynamic')
    ctx.add(cloth, ROOM, 'decor')

    # --- bins against the house beyond the bay, fronts facing west; food caddy
    items = _feature(ctx, 'bins')['items']
    for k, ((x, y), colour) in enumerate(zip(items, ('#3A3B3F', '#2F3550'))):
        ob = P.place(FP.wheelie_bin('front.bin.%d' % k, colour), (0, 0, 0), facing=(-1, 0))
        # ponytail: both bins 50 mm toward the street so the grey one's lid clears the corner pilaster (face y -0.20)
        ctx.add(_on_ground(ctx, ob, x, y - 0.05), ROOM, 'furn', plan_sym='bin')
    x, y = items[2]
    ctx.add(_on_ground(ctx, P.place(FP.caddy('front.caddy'), (0, 0, 0), facing=(-1, 0)), x, y, half=0.2), ROOM, 'furn', plan_sym='bin')

    # --- on the house face: video doorbell on the pilaster, weatherproof socket under the bay sill
    w = _hit((0.86, -0.7, 1.28), (0, 1, 0), (0.86, -0.18, 1.28))
    ctx.add(P.place(FP.doorbell('front.doorbell'), (0.86, w.y, 1.28), facing=(0, -1)), ROOM, 'fit', lm='dynamic')
    w = _hit((1.45, -0.7, 0.42), (0, 1, 0), (1.45, -0.12, 0.42))
    sock = P.place(FP.outdoor_socket('front.socket'), (1.45, w.y, 0.42), facing=(0, -1))
    sock.rotation_euler.y = math.radians(-3)
    ctx.add(sock, ROOM, 'fit', lm='dynamic')

    # --- the three "outside lights" in the canopy soffit and their switches are built by rooms/vestibule.py
    #     (vestibule.outside.*, switched with the lantern by vestibule.switch and the hall 3-gang porch rocker).
    #     Here only the small black security camera on the bay corner under the cornice, unlit
    w = _hit((1.0, -1.0, 2.80), (0, 1, 0), (1.0, -0.12, 2.80))
    ctx.add(P.place(FP.security_cam('front.camera'), (1.0, w.y, 2.80), facing=(0, -1)), ROOM, 'fit', lm='dynamic')

    # --- flush access covers: two by the bins, one small one in the footway
    # ponytail: moved 0.16 m west of front.md (x 4.45) so they lie wholly on the forecourt slab, not across the
    # 11 mm level step to the alley-mouth zone in house.json
    for k, (x, y, sx, sy) in enumerate(((4.29, -2.3, 0.45, 0.60), (4.29, -3.0, 0.45, 0.60), (1.9, -5.7, 0.30, 0.30))):
        ctx.add(_on_ground(ctx, FP.cover('front.cover.%d' % k, sx, sy), x, y, half=sy / 2 - 0.01), ROOM, 'fit')

    # --- street backdrop: lamp column and young tree at the kerb, plain white line on the carriageway
    for k, ob in enumerate(FP.lamp_column('front.lamp_column')):          # shaft (walk obstacle), then arm + lantern
        ob.location = (3.3, -7.0, ctx.ground_z(3.3, -7.0))
        ctx.add(ob, ROOM, 'fit', plan_sym='pipe' if k == 0 else None, lm='dynamic')
    for k, ob in enumerate(FP.street_tree('front.tree')):               # trunk (walk obstacle), branches, crown
        ob.location = (-0.6, -6.9, ctx.ground_z(-0.6, -6.9))
        ctx.add(ob, ROOM, 'decor', plan_sym='pipe' if k == 0 else None)
    zr = ctx.ground_z(1.0, -7.65)
    ctx.add(shell.box('front.road_line', -2.6, 7.6, -7.70, -7.60, zr, zr + 0.004, '#E6E6E2'), ROOM, 'fit')
    opposite_row(ctx)


OPPOSITE = (-15.0, 20.0, -21.5, 9.0)      # x from, x to, front face y, depth: the row across the street (front.md 37 / 142)
HOUSE_W, EAVES, RIDGE = 5.0, 6.2, 9.0


def opposite_row(ctx):
    """[round 4] The far side of the street (Q11: past the street tree there was asphalt to the horizon): a continuous row
    of gabled two-storey-plus-attic houses about 22 m away, red brick with every other upper storey in white render,
    dark windows, low front walls and the opposite footway; the carriageway and our footway carried on beyond the
    zones of house.json. Massing as backdrop, room 'neighbours' (the dollhouse hides it; quarter-density bake).
    ponytail: one object, no window frames or chimneys - it is seen from 20 m and more (v2 f_0944 / f_0950)."""
    from lib.site import _Mesh
    m = _Mesh()
    x_from, x_to, yf, depth = OPPOSITE
    yb, z0 = yf - depth, -0.5
    for lo, hi, key, top in (((-15, -15.2, z0), (-3, -7.2, -0.28), 'asphalt', 'asphalt'),       # road beyond the zone
                             ((8, -15.2, z0), (20, -7.2, -0.28), 'asphalt', 'asphalt'),
                             ((-15, -7.2, z0), (-3, -5.2, -0.16), 'concrete_flags', None),     # our footway, both ends
                             ((8, -7.2, z0), (20, -5.2, -0.16), 'concrete_flags', None),
                             ((-15, -17.2, z0), (20, -15.2, -0.16), 'concrete_flags', None),   # the opposite footway + kerb
                             ((-15, yf, z0), (20, -17.45, -0.12), '#5F6B4C', None)):           # front gardens
        m.box(lo, hi, key, only=('+z', '+y', '-y'))
    m.box((-15, -17.45, -0.16), (20, -17.2, 0.45), 'red_brick', only=('+z', '+y', '-y'))      # low front walls
    doors = ('#1F3A5F', '#5A1E1E', '#2F4F3A', '#202020', '#6B5A3A')
    n = int(round((x_to - x_from) / HOUSE_W))
    for i in range(n):
        x0, x1 = x_from + i * HOUSE_W, x_from + (i + 1) * HOUSE_W
        xc, ov = (x0 + x1) / 2, 0.2
        m.face([(x1, yf, z0), (x0, yf, z0), (x0, yf, EAVES), (xc, yf, RIDGE), (x1, yf, EAVES)], 'red_brick')   # gable
        m.face([(x0, yb, z0), (x1, yb, z0), (x1, yb, EAVES), (xc, yb, RIDGE), (x0, yb, EAVES)], 'stock_brick_grey')
        m.face([(x0, yf, z0), (x0, yb, z0), (x0, yb, EAVES), (x0, yf, EAVES)], 'stock_brick_grey')
        m.face([(x1, yb, z0), (x1, yf, z0), (x1, yf, EAVES), (x1, yb, EAVES)], 'stock_brick_grey')
        ze, zr = EAVES - ov * (RIDGE - EAVES) / (xc - x0), RIDGE + 0.12
        m.face([(x0 - ov, yf + ov, ze), (x0 - ov, yb - ov, ze), (xc, yb - ov, zr), (xc, yf + ov, zr)], 'slate')
        m.face([(xc, yf + ov, zr), (xc, yb - ov, zr), (x1 + ov, yb - ov, ze), (x1 + ov, yf + ov, ze)], 'slate')
        y1 = yf + 0.01
        if i % 2:                                                       # white render above the ground floor
            m.face([(x1, y1, 3.1), (x0, y1, 3.1), (x0, y1, EAVES), (xc, y1, RIDGE - 0.02), (x1, y1, EAVES)], '#EEEBE2')

        def rect(a, b, za, zb, key, y):                                # a window / door face on the front (+Y)
            m.face([(b, y, za), (a, y, za), (a, y, zb), (b, y, zb)], key)
        y2, y3 = yf + 0.02, yf + 0.03
        rect(x0 + 0.5, x0 + 2.5, 0.55, 2.35, '#F2F1EC', y2)             # ground-floor bay: white frame, dark glass
        rect(x0 + 0.6, x0 + 2.4, 0.65, 2.25, '#2B3135', y3)
        rect(x1 - 1.6, x1 - 0.6, -0.12, 2.15, '#F2F1EC', y2)            # front door in a white frame
        rect(x1 - 1.5, x1 - 0.7, -0.12, 2.05, doors[i % len(doors)], y3)
        for a in (x0 + 0.7, x1 - 1.7):                                  # two first-floor sashes
            rect(a, a + 1.0, 3.55, 5.05, '#F2F1EC', y2)
            rect(a + 0.08, a + 0.92, 3.63, 4.97, '#2B3135', y3)
        rect(xc - 0.45, xc + 0.45, 6.55, 7.65, '#F2F1EC', y2)           # attic window in the gable
        rect(xc - 0.37, xc + 0.37, 6.63, 7.57, '#2B3135', y3)
    m.obj(ctx, 'neighbours.opposite', 'neighbours', kind='decor')

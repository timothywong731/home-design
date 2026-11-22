"""Front forecourt (spec/rooms/front.md, spec/phase2/front_elevation.md 5 and 8, round 3: spec/phase3/front.md and
briefs/front.md): the two cars, wall planters with bellflowers, the flag, bins, doorbell, outdoor socket, the meter box and
security light on the bay's east cheek / return with the sett patch under them, the patched tarmac strip's tone,
inspection covers in their haunch and gullies, the pier plaque, and the lamp column /
street tree / neighbour's planter backdrop. Paving, wall, pier, facade and porch come from site / envelope; the three canopy
downlights ("outside lights") and their switches come from rooms/vestibule.py.

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --levels G,X --only shell,site,envelope,front \
        --preview front --res 540x960 --samples 64 --tag front
"""
import math

import bpy
import numpy as np
from mathutils import Matrix, Vector

from lib import materials as M, props as P, shell, site_tex as ST
from lib.site import _Mesh
from rooms import front_car as CAR, front_parts as FP

ROOM = 'front'

# refs: reference/work/p2_front_ext/<ref>.jpg (v2_tNNN = v2 frame f_(NNN+1), v4_tNN = v4 frame f_(NN+1));
# round 3: reference/work/r3_front/v8_tNN.jpg / v9_tNN.jpg (21 Nov, frame NN+1)
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
    dict(name='covers', pos=(4.75, -4.3, 1.55), look=(4.7, -0.6, 0.3), fov_deg=100, ref='v8_t30'),
    dict(name='cheek', pos=(5.45, -0.95, 1.3), look=(4.25, 0.45, 1.35), fov_deg=100, ref='v8_t69'),
    dict(name='pier', pos=(-0.35, -6.4, 1.5), look=(-0.7, -3.2, 0.55), fov_deg=100, ref='v8_t11'),
    dict(name='gate', pos=(4.9, -5.6, 1.6), look=(4.8, 1.0, 1.2), fov_deg=100, ref='v8_t60'),
    dict(name='gully', pos=(0.35, -0.95, 1.25), look=(-0.62, -0.28, 0.0), fov_deg=100, ref='v9_t54'),
    dict(name='meter', pos=(4.95, -0.25, 1.75), look=(4.3, 0.6, 1.2), fov_deg=90, ref='v8_t70'),
]


def _feature(ctx, fid):
    return next(f for f in ctx.spec['exterior']['features'] if f['id'] == fid)


def _hit(origin, direction, default, dist=1.5):
    """First surface of what is already built along a ray -> hit point, else `default` (None allowed)."""
    bpy.context.view_layer.update()
    ok, loc, *_ = bpy.context.scene.ray_cast(bpy.context.view_layer.depsgraph, Vector(origin), Vector(direction), distance=dist)
    return loc if ok else (Vector(default) if default is not None else None)


def _settle(ctx, ob, x, y, contacts, lift=0.0):
    """Stand `ob` (placed at the origin and turned, not yet linked) at (x, y): its local contact points (px, py, z 0)
    go onto the plane fitted through the ground under them, none below the ground (the setts and the tarmac strip
    meet with a 2 cm step at x 4.40, and both fall toward the street)."""
    R0 = ob.matrix_basis.copy()
    pts = [R0 @ Vector((px, py, 0)) for px, py in contacts]
    g = np.array([ctx.ground_z(x + p.x, y + p.y) for p in pts])
    a, b, c = np.linalg.lstsq(np.array([[1, p.x, p.y] for p in pts]), g, rcond=None)[0]
    tilt = Vector((0, 0, 1)).rotation_difference(Vector((-b, -c, 1)).normalized()).to_matrix().to_4x4()
    z = a + max(gi - (a + b * p.x + c * p.y) for gi, p in zip(g, pts)) + lift
    ob.matrix_world = Matrix.Translation((x, y, z)) @ tilt @ R0      # matrix_basis: current even before linking
    return ob


def _face(origin, direction, offsets, default):
    """Most proud surface along a ray, over the rays shifted by `offsets` (a reeded or moulded face): -> point."""
    hits = [_hit(Vector(origin) + Vector(o), direction, None) for o in offsets]
    hits = [h for h in hits if h is not None]
    if not hits:
        return Vector(default)
    d = Vector(direction)
    return min(hits, key=lambda h: h.dot(d))


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
    # --- the patched tarmac strip east of the setts (brief (a): #6B6A64, a worn light patch): the site lays the road's
    #     dark asphalt (#55565A, half the setts' value) on these two front zones; recoloured here so that the strip reads
    #     about 0.7 of the setts as in v8 t30 / t60 (0.72 in shade, 0.89 sunlit), a shade lighter than the brief's tone
    strip = ST.mat('asphalt@#77756C')
    for zid in ('forecourt_alley_mouth', 'forecourt_alley_apron'):
        ob = bpy.data.objects.get('%s.%s' % (ROOM, zid))
        for slot in ob.material_slots if ob else ():
            if slot.material == M.mat('asphalt'):
                slot.material = strip

    # --- the two cars: grey to the west, white to the east (owner correction: yaw 0, long axis along Y)
    _car(ctx, 'car_grey', CAR.GREY)
    _car(ctx, 'car_white', CAR.WHITE)

    # --- timber troughs and bellflowers on the west wall
    troughs, foliage = FP.planter(ctx)
    ctx.add(troughs, ROOM, 'fit', plan_sym='planter')
    ctx.add(foliage, ROOM, 'decor')                                 # no plan symbol: it overhangs the path, it does not block it

    # --- flag on its 45-degree pole, bracket on the pilaster between the door and the bay (plan symbol: the bracket)
    bx, by, bz = _feature(ctx, 'flag')['bracket']
    wall = _face((bx, by - 0.5, bz), (0, 1, 0), [(dx, 0, dz) for dx in (-0.035, 0, 0.035) for dz in (-0.065, 0, 0.045)], (bx, by, bz))
    bracket, pole, cloth = FP.flag((bx, wall.y, bz), _feature(ctx, 'flag')['pole'], _feature(ctx, 'flag')['flagSize'])
    ctx.add(bracket, ROOM, 'fit', plan_sym='flagpole', lm='dynamic')
    ctx.add(pole, ROOM, 'fit', lm='dynamic')
    ctx.add(cloth, ROOM, 'decor')

    # --- bins (front survey 2.5, v8 f31-36 / f61-66): grey against the bay's corner pilaster, navy south of it, both
    #     fronts west, half on the setts and half on the tarmac strip (x 4.40), just clear of the white car's flank
    #     (x <= 4.00 at its tail, 21 Nov position); the grey bin 0.01 off the pilaster's base block (face y -0.20).
    #     Pale-green food caddy south-west of the navy bin, beside the car's rear wheel.
    for k, (y, colour, lid) in enumerate(((-0.475, '#4A4C4B', None), (-1.075, '#3F4868', '#68759A'))):
        ob = P.place(FP.wheelie_bin('front.bin.%d' % k, colour, lid), (0, 0, 0), facing=(-1, 0))
        ctx.add(_settle(ctx, ob, 4.42, y, ((0.262, 0.285), (-0.262, 0.285), (0.17, -0.25), (-0.17, -0.25))), ROOM, 'furn',
                plan_sym='bin')
    ob = P.place(FP.caddy('front.caddy'), (0, 0, 0), facing=(0, -1))      # wholly on the setts (x < 4.40), off the haunch
    ctx.add(_settle(ctx, ob, 4.215, -1.64, ((0.12, 0.15), (-0.12, 0.15), (0.12, -0.15), (-0.12, -0.15))), ROOM, 'furn',
            plan_sym='bin')

    # --- on the house face: video doorbell on the flat strip between the door frame and the west pilaster's reeds
    #     (v9 f45-48; reeds from x 0.83), weatherproof socket under the west end of the bay sill, clear of the
    #     pilaster's base block (to x 1.17; survey x 1.22)
    w = _face((0.785, -0.7, 1.30), (0, 1, 0), [(dx, 0, dz) for dx in (-0.025, 0, 0.025) for dz in (-0.06, 0.06)], (0.785, -0.12, 1.30))
    ctx.add(P.place(FP.doorbell('front.doorbell'), (0.785, w.y, 1.30), facing=(0, -1)), ROOM, 'fit', lm='dynamic')
    w = _face((1.27, -0.7, 0.42), (0, 1, 0), [(dx, 0, dz) for dx in (-0.08, 0, 0.08) for dz in (-0.05, 0.05)], (1.27, -0.12, 0.42))
    sock = P.place(FP.outdoor_socket('front.socket'), (1.27, w.y, 0.42), facing=(0, -1))
    ctx.add(sock, ROOM, 'fit', lm='dynamic')

    # --- the bay's east cheek (face x 4.25) and return (y 0.74), v8 f64-79 / t69: white gas-meter box under the cheek
    #     window, its south edge in line with the window frame (y 0.19), top under the sill; small cable box north of
    #     it; a white pipe from the box into the ground. Twin-flood security light on the return just under the
    #     cornice (cornice from Z 2.70), near the cheek corner. (The black camera of round 2 on the west pilaster is
    #     not in the 21 Nov footage: this is the one unit.) The east downpipe at (4.295, -0.02) stays clear.
    cheek = _face((4.6, 0.395, 0.3), (-1, 0, 0), [(0, dy, dz) for dy in (-0.2, 0, 0.2) for dz in (-0.25, 0, 0.2)], (4.25, 0.395, 0.3))
    sill = _hit((4.36, 0.395, 0.3), (0, 0, 1), (4.36, 0.395, 0.552))
    z0 = 0.015
    ob = P.place(FP.meter_box('front.meter_box', h=sill.z - 0.004 - z0), (cheek.x, 0.395, z0), facing=(1, 0))
    ctx.add(ob, ROOM, 'fit', plan_sym='cabinet')
    ctx.add(P.place(FP.cable_box('front.cable_box'), (cheek.x, 0.655, 0.145), facing=(1, 0)), ROOM, 'fit')
    zg = ctx.ground_z(cheek.x + 0.09, 0.32)
    pipe = shell.box('front.meter_box.pipe', cheek.x + 0.078, cheek.x + 0.102, 0.308, 0.332, zg - 0.02, z0 + 0.002, '#EAE9E2')
    ctx.add(pipe, ROOM, 'fit')
    # the floodlight camera hangs with its plate just under the return's trim soffit (v8 t69 / t70: plate against the
    # cornice's lowest moulding), 3 cm clear of the cheek corner with its heads splayed (brief: x 4.40)
    ret = _hit((4.40, 0.2, 2.55), (0, 1, 0), (4.40, 0.74, 2.55))
    soffit = _hit((4.40, ret.y - 0.015, 2.3), (0, 0, 1), (4.40, ret.y - 0.015, 2.70))
    ctx.add(P.place(FP.security_light('front.camera'), (4.40, ret.y, soffit.z - 0.005 - FP.SECLIGHT_R), facing=(0, -1)),
            ROOM, 'fit', lm='dynamic')

    # --- the small patch of setts kept under the meter box (brief (a); v8 t69 / t70 / f77: from just north of the
    #     downpipe, y 0.03, to the return, 0.40 out from the cheek), courses along the cheek, 4 mm proud of the tarmac
    _setts_patch(ctx, 4.25, 4.65, 0.03, 0.74)

    # --- inspection covers on the tarmac strip, side by side east-west, in one cast-concrete haunch (survey 2.1);
    #     the small square cover in the footway; square yard gullies at the canopy downpipe's shoe and at the bay foot
    for k, x in enumerate((4.67, 5.21)):
        ctx.add(_settle(ctx, FP.cover('front.cover.%d' % k, 0.48, 0.58), x, -2.0, ((0.24, 0.29), (-0.24, 0.29), (0.24, -0.29), (-0.24, -0.29))),
                ROOM, 'fit')
    _haunch(ctx)
    ctx.add(_settle(ctx, FP.cover('front.cover.2', 0.30, 0.30), 1.9, -5.7, ((0.15, 0.15), (-0.15, 0.15), (0.15, -0.15), (-0.15, -0.15))),
            ROOM, 'fit')
    for k, (x, y) in enumerate(((-0.62, -0.30), (2.40, -0.20))):
        ctx.add(_settle(ctx, FP.gully('front.gully.%d' % k), x, y, ((0.075, 0.075), (-0.075, 0.075), (0.075, -0.075), (-0.075, -0.075))),
                ROOM, 'fit')

    # --- pier plaque on the street face, second course below the cap (survey 2.2; cap underside Z 0.915)
    pier = next(b for b in ctx.spec['exterior']['boundaries'] if b['id'] == 'front_pier_w')
    px = sum(p[0] for p in pier['polygon']) / 4
    py = min(p[1] for p in pier['polygon'])
    zc = pier['baseZ'] + pier['height'] - pier.get('cap', {}).get('edge', 0.085) - 0.04 - 1.5 * 0.075
    w = _hit((px, py - 0.5, zc), (0, 1, 0), (px, py, zc))
    ctx.add(P.place(FP.pier_plaque('front.pier_plaque'), (px, w.y, zc), facing=(0, -1)), ROOM, 'fit', lm='dynamic')

    # --- street backdrop (survey 2.6): lamp column at the kerb in front of the east neighbour, street tree straight out
    #     from the pier, plain white line on the carriageway, two black tarmac patches in the footway flags
    for k, ob in enumerate(FP.lamp_column('front.lamp_column')):          # shaft (walk obstacle), then arm + lantern
        ob.location = (7.5, -7.0, ctx.ground_z(7.5, -7.0))
        ctx.add(ob, ROOM, 'fit', plan_sym='pipe' if k == 0 else None, lm='dynamic')
    for k, ob in enumerate(FP.street_tree('front.tree')):               # trunk (walk obstacle), branches, crown
        ob.location = (-1.2, -7.0, ctx.ground_z(-1.2, -7.0))
        ctx.add(ob, ROOM, 'decor', plan_sym='pipe' if k == 0 else None)
    zr = ctx.ground_z(1.0, -7.65)
    ctx.add(shell.box('front.road_line', -2.6, 7.6, -7.70, -7.60, zr, zr + 0.004, '#E6E6E2'), ROOM, 'fit')
    zf = ctx.ground_z(1.0, -6.0)
    for k, (x0, x1, y0, y1) in enumerate(((-1.3, -0.2, -6.5, -5.2), (-0.2, 4.4, -5.40, -5.2))):
        ctx.add(shell.box('front.footway.patch.%d' % k, x0, x1, y0, y1, zf - 0.01, zf + 0.003, '#2E2F31'), ROOM, 'fit')

    # --- the east neighbour's corrugated-steel raised bed (massing; survey 2.3, x 6.0..6.9, y -5.0..-3.0)
    zn = _hit((6.45, -4.0, 1.0), (0, 0, -1), (6.45, -4.0, -0.36), dist=3).z     # the neighbour's yard (site: Z -0.36)
    for ob in FP.steel_planter('neighbours.east_planter'):
        ob.location = (6.45, -4.0, zn)
        ctx.add(ob, 'neighbours', 'decor')
    opposite_row(ctx)


def _setts_patch(ctx, x0, x1, y0, y1, proud=0.004):
    """Setts over the rectangle on the tarmac fall: top `proud` above the ground, exposed edges to the east and south
    (west and north stand against the cheek and the return). Courses run along Y, joints from the corner (x0, y0)."""
    m = _Mesh()

    def g(x, y, dz):
        return (x, y, ctx.ground_z(x, y) + dz)
    m.face([g(x0, y0, proud), g(x1, y0, proud), g(x1, y1, proud), g(x0, y1, proud)], 'site_setts')
    m.face([g(x0, y0, -0.02), g(x1, y0, -0.02), g(x1, y0, proud), g(x0, y0, proud)], 'site_setts')
    m.face([g(x1, y0, -0.02), g(x1, y1, -0.02), g(x1, y1, proud), g(x1, y0, proud)], 'site_setts')
    m.obj(ctx, 'front.setts_patch', ROOM, kind='fit', rot=True, origin=(x0, y0, 0.0))


def _haunch(ctx, proud=0.003):
    """Pale cast-concrete haunch round the two covers (v8 t30 / t60 / f64): a narrow margin on the north and east and
    between the covers, the sett edge on the west, a wider broken edge to the south. Top on the tarmac fall."""
    poly = [(4.402, -2.37), (4.56, -2.42), (4.74, -2.38), (4.93, -2.44), (5.12, -2.37), (5.30, -2.35), (5.49, -2.33),
            (5.49, -1.67), (4.402, -1.67)]                                  # counter-clockwise; covers y -2.29..-1.71
    m = _Mesh()
    m.face([(x, y, ctx.ground_z(x, y) + proud) for x, y in poly], 'site_concrete')
    for (ax, ay), (bx, by) in zip(poly, poly[1:] + poly[:1]):
        za, zb = ctx.ground_z(ax, ay), ctx.ground_z(bx, by)
        m.face([(ax, ay, za - 0.05), (bx, by, zb - 0.05), (bx, by, zb + proud), (ax, ay, za + proud)], 'site_concrete')
    m.obj(ctx, 'front.cover.haunch', ROOM, kind='fit', origin=(4.402, -2.44, 0.0))


OPPOSITE = (-15.0, 20.0, -21.5, 9.0)      # x from, x to, front face y, depth: the row across the street (front.md 37 / 142)
HOUSE_W, EAVES, RIDGE = 5.0, 6.2, 9.0


def opposite_row(ctx):
    """[round 4] The far side of the street (Q11: past the street tree there was asphalt to the horizon): a continuous row
    of gabled two-storey-plus-attic houses about 22 m away, red brick with every other upper storey in white render,
    dark windows, low front walls and the opposite footway; the carriageway and our footway carried on beyond the
    zones of house.json. Massing as backdrop, room 'neighbours' (the dollhouse hides it; quarter-density bake).
    ponytail: one object, no window frames or chimneys - it is seen from 20 m and more (v2 f_0944 / f_0950)."""
    m = _Mesh()
    x_from, x_to, yf, depth = OPPOSITE
    zones = {z['id']: z for z in ctx.spec['exterior']['zones']}
    zr, zw = zones['road']['z'], zones['footway']['z']               # round 3: road -0.50, footway -0.38 (front-02)
    yb, z0 = yf - depth, zr - 0.3
    for lo, hi, key, top in (((-15, -15.2, z0), (-3, -7.2, zr + 0.002), 'asphalt', 'asphalt'),  # road beyond the zone,
                             ((8, -15.2, z0), (20, -7.2, zr + 0.002), 'asphalt', 'asphalt'),   # 2 mm over the backdrop
                             ((-15, -7.2, z0), (-3, -5.2, zw), 'concrete_flags', None),        # our footway, both ends
                             ((8, -7.2, z0), (20, -5.2, zw), 'concrete_flags', None),
                             ((-15, -17.2, z0), (20, -15.2, zw), 'concrete_flags', None),      # the opposite footway + kerb
                             ((-15, yf, z0), (20, -17.45, zw + 0.04), '#5F6B4C', None)):       # front gardens
        m.box(lo, hi, key, only=('+z', '+y', '-y'))
    m.box((-15, -17.45, zw), (20, -17.2, zw + 0.61), 'red_brick', only=('+z', '+y', '-y'))    # low front walls
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

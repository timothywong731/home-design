"""Yellow room: first-floor middle room, unoccupied (spec/rooms/yellow_room.md, footage v3 f_0077-f_0140).

Adds: four downlights + switch, sockets, air-con unit + wall remote, column radiator, timber sill board, Roman
blind (raised = state 0), mahogany cupboard on a stand (doors open), Chippendale side chair, deep-buttoned white
ottoman, brass door stop. Everything is placed from the room polygon, the piers / boxings and the openings of
spec/house.json, so the sill ears, the blind head and the air-con trunking follow a corrected east-wall niche.
"""
import math
import os

import bmesh
import bpy
import numpy as np
from mathutils import Matrix

from lib import interact as IX, lighting, materials as M, mouldings as mo, props as P, site_tex as ST
from rooms.dining_chairs import chair as dining_chair      # same family of chair, same seat tapestry
from rooms.dining_furniture import dark_wood

ROOM = 'yellow_room'
ART = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'textures', 'art')
TEX = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'build', 'tex', ROOM)

# world coords; eye 1.5 m above the floor (Z 3.04); refs are v3 frames
CAMERAS = [
    dict(name='in', pos=(0.75, 10.50, 4.54), look=(3.0, 9.6, 4.25), fov_deg=100, ref='v3:f_0085'),
    dict(name='window', pos=(1.65, 10.30, 4.54), look=(3.1, 10.45, 4.55), fov_deg=100, ref='v3:f_0090'),
    dict(name='north', pos=(1.95, 9.55, 4.54), look=(2.45, 11.05, 4.2), fov_deg=100, ref='v3:f_0091'),
    dict(name='rad', pos=(2.2, 9.9, 4.54), look=(3.05, 10.5, 3.6), fov_deg=100, ref='v3:f_0096'),
    dict(name='west', pos=(2.3, 10.2, 4.54), look=(0.35, 10.1, 4.15), fov_deg=100, ref='v3:f_0130'),
    dict(name='door', pos=(1.75, 9.75, 4.54), look=(0.7, 11.0, 4.1), fov_deg=100, ref='v3:f_0132'),
    dict(name='ott', pos=(2.1, 10.15, 4.0), look=(2.6, 10.9, 3.35), fov_deg=80, ref='v3:f_0093'),
    dict(name='cab', pos=(1.9, 9.9, 4.4), look=(0.5, 9.45, 3.65), fov_deg=80, ref='v3:f_0129'),
    dict(name='stop', pos=(1.32, 10.3, 4.35), look=(1.24, 11.0, 3.16), fov_deg=80, ref='v3:f_0138'),
]

T = Matrix.Translation
WHITE = 'plastic_white'


def _cloth(name, profile, width, mat, repeat):
    """Ribbon of cloth: polyline [(y, z)...] (top first) extruded over x = +-width/2. UV: u across, v down the cloth,
    one image repeat per `repeat` metres."""
    verts, uvs, s = [], [], 0.0
    for i, (y, z) in enumerate(profile):
        if i:
            s += math.dist(profile[i - 1], (y, z))
        verts += [(-width / 2, y, z), (width / 2, y, z)]
        uvs += [(0, 1 - s / repeat), (1, 1 - s / repeat)]
    faces = [(2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2) for i in range(len(profile) - 1)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    uv = me.uv_layers.new(name='UVMap')
    for l in me.loops:
        uv.data[l.index].uv = uvs[l.vertex_index]
    me.polygons.foreach_set('use_smooth', [True] * len(faces))
    me.materials.append(mat)
    return bpy.data.objects.new(name, me)


def _tufted_top(name, w, d, mat, n=(4, 2), r=.02, res=(32, 16), puff=.008, dimple=.007):
    """Top skin of a deep-buttoned lid, w x d: quarter-round edge of radius r (z 0 at the rim, r on the flat), stitched
    creases through the n button grid (5 x 3 pillowed pads for 4 x 2 buttons: five equal pads along the length, rows
    at a quarter and three quarters of the depth as in v3 f_0092; each pad rises `puff` from its creases, the creases
    are narrow grooves on extra vertex rows) and a `dimple` at every button.
    Returns (object, z(x, y), button points)."""
    bx = [w * ((i + 1) / (n[0] + 1) - .5) for i in range(n[0])]
    by = [d * ((j + .5) / n[1] - .5) for j in range(n[1])]
    px, py = w / (n[0] + 1), d / n[1]

    def z(x, y):
        e = min(w / 2 - abs(x), d / 2 - abs(y), r)
        dx, dy = min(abs(x - c) for c in bx), min(abs(y - c) for c in by)
        fx = math.sin(math.pi / 2 * min(1, dx / (px / 2))) ** .45     # 0 on a crease, 1 mid-pad (edge pads: at the rim)
        fy = math.sin(math.pi / 2 * min(1, dy / (py / 2))) ** .45
        g = math.exp(-(dx * dx + dy * dy) / (2 * .011 ** 2))
        return math.sqrt(r * r - (r - e) ** 2) + (puff * fx * fy - dimple * g) * e / r

    def axis(size, cs, k):                      # uniform rows + rows hugging each crease (a crisp stitched groove)
        q = {round(size * (i / k - .5), 5) for i in range(k + 1)}
        q |= {round(c + o, 5) for c in cs for o in (0, -.003, .003, -.009, .009)}
        return sorted(q)
    X, Y = axis(w, bx, res[0]), axis(d, by, res[1])
    nx, ny = len(X), len(Y)
    verts = [(x, y, z(x, y)) for y in Y for x in X]
    faces = [(j * nx + i, j * nx + i + 1, (j + 1) * nx + i + 1, (j + 1) * nx + i) for j in range(ny - 1) for i in range(nx - 1)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.uv_layers.new(name='UVMap')
    me.polygons.foreach_set('use_smooth', [True] * len(faces))
    me.materials.append(mat)
    return bpy.data.objects.new(name, me), z, [(x, y) for x in bx for y in by]


def _fielded_door(name, w, h, wood, t=.02, stile=.045, rails=(.06, .045), recess=.007, field=.016, rise=.004):
    """Framed cabinet door with a fielded panel (raised field with a chamfered margin), as P.panel_door's frame:
    origin bottom centre of the back face, front at y = -t, w along x, h up."""
    mb = mo.MB()
    x0, x1, (rb, rt) = -w / 2, w / 2, rails
    for xa, xb in ((x0, x0 + stile), (x1 - stile, x1)):
        mb.box((xa, -t, 0), (xb, 0, h), wood, bev=.002, grain=2)
    for za, zb in ((0, rb), (h - rt, h)):
        mb.box((x0 + stile, -t, za), (x1 - stile, 0, zb), wood, bev=.002, grain=0)
    qx0, qx1, qz0, qz1, yp = x0 + stile, x1 - stile, rb, h - rt, -t + recess
    mb.box((qx0, yp, qz0), (qx1, -.004, qz1), wood, grain=2)                      # sunk panel board
    a = [(qx0 + .003, yp, qz0 + .003), (qx1 - .003, yp, qz0 + .003), (qx1 - .003, yp, qz1 - .003), (qx0 + .003, yp, qz1 - .003)]
    f = [(qx0 + field, yp - rise, qz0 + field), (qx1 - field, yp - rise, qz0 + field),
         (qx1 - field, yp - rise, qz1 - field), (qx0 + field, yp - rise, qz1 - field)]
    mb.face(f, wood, hint=(0, -1, 0), grain=2)                                     # the field
    for i, (ox, oz) in enumerate(((0, -1), (1, 0), (0, 1), (-1, 0))):            # its chamfered margin
        mb.face([a[i], a[(i + 1) % 4], f[(i + 1) % 4], f[i]], wood, hint=(ox, -1, oz), grain=2)
    return mb.finish(name)


def _escutcheon(name):
    """Brass oval escutcheon with a pear drop on a pin (v3 f_0129). Origin on the door face, front -Y."""
    mb = mo.MB()
    mb.at(Matrix.Rotation(math.pi / 2, 4, 'X'))                                    # local Z -> -Y
    mb.lathe([(0, 0), (.011, 0), (.011, .0012), (.008, .0025), (0, .0025)], 'brass_antique', 16, ell=(1, 1.7))
    mb.at()
    mb.tube([(0, -.002, .004), (0, -.008, .004)], .0015, 'brass_antique', n=6)
    mb.at(T((0, -.009, -.021)))
    mb.lathe([(0, 0), (.0035, .0015), (.006, .007), (.0052, .014), (.0025, .021), (.0018, .024), (0, .025)],
             'brass_antique', 12)
    return mb.finish(name)


def _pine_tex(version=3):
    """Path of the sill board's colour map, made once with numpy (no reference pixels) and cached under build/tex:
    flat-sawn softwood under a walnut stain, 0.25 m across x 1.0 m along the grain (image rows), 1 mm a pixel:
    growth rings 7 mm apart cut as cathedral arches (rings round a pith that wanders below the face), fibre streaks,
    three knots with the rings swirling round them, mean #5A4030 (sill board of v3 f_0085, f_0109-f_0114; the spec's
    #5A3A22 rendered orange in daylight)."""
    path = os.path.join(TEX, f'sill_pine_v{version}.jpg')
    if os.path.exists(path):
        return path
    os.makedirs(TEX, exist_ok=True)
    H, W = 1024, 256                                                 # rows along the grain, columns across
    v, u = np.mgrid[0:H, 0:W].astype(np.float32)
    rng = np.random.default_rng(7)

    def wander(n, amp):                                              # smooth periodic 1-D curve along the grain
        k = np.arange(1, n + 1)
        c = rng.standard_normal(n) / k, rng.uniform(0, 2 * np.pi, n)
        return amp * sum(ci * np.sin(2 * np.pi * ki * v / H + pi) for ci, ki, pi in zip(c[0], k, c[1]))

    def stretched(lo, hi, k, seed):                                  # noise k times longer along the grain
        n = ST._noise(H // k, W, lo, hi, seed)
        y = v / k
        i0, fr, ui = np.floor(y).astype(int) % (H // k), y - np.floor(y), u.astype(int)
        return n[i0, ui] * (1 - fr) + n[(i0 + 1) % (H // k), ui] * fr
    up, depth = 140 + wander(4, 45), 60 + wander(4, 25)              # pith across the board and below the face (mm)
    phase = np.sqrt((u - up) ** 2 + depth ** 2) / 7.0 + .5 * stretched(20, 200, 6, 12)
    knot = np.zeros_like(u)
    for ky, kx, r in ((180, 70, 9), (610, 190, 6), (880, 40, 7)):
        d = np.hypot(v - ky, (u - kx) * 1.4)
        phase += 4 * np.exp(-(d / (3 * r)) ** 2)                     # rings swirl round the knot
        knot = np.maximum(knot, np.clip(1.4 - d / r, 0, 1))
    f = phase - np.floor(phase)
    late = np.clip((f - .55) / .15, 0, 1) * np.clip((1 - f) / .2, 0, 1)    # dark latewood, a third of each ring
    fibre = ST._noise(H // 16, W, 1, 3, 13).repeat(16, 0)
    shade = late * .5 + knot * .85 + .05 * fibre + .06 * ST._noise(H, W, 40, 400, 14)
    early, dark = np.array([.52, .37, .25]), np.array([.22, .13, .08])     # sRGB
    img = early + (dark - early) * np.clip(shade, 0, 1)[..., None]
    ST._write(path, ST._recolor(img, '#5A4030'))
    return path


def _leaf_line(fz):
    """Open d_yellow leaf from joinery: (x of its free end, y of its north face as a function of x), measured on the
    mesh below knee height, or None when the leaf is not there (--only without shell)."""
    leaf = bpy.data.objects.get('yellow_room.d_yellow.leaf')
    if leaf is None or leaf.type != 'MESH':
        return None
    bpy.context.view_layer.update()
    mw = leaf.matrix_world
    pts = [mw @ v.co for v in leaf.data.vertices]
    pts = [p for p in pts if p.z < fz + .4]
    x_end = max(p.x for p in pts)
    ya = max(p.y for p in pts if p.x > x_end - .012)                 # face line through the free end and 0.3 m back
    yb = max([p.y for p in pts if abs(p.x - x_end + .3) < .02] or [ya])
    return x_end, lambda x: ya + (ya - yb) / .3 * (x - x_end)


def _door_stop(name, length):
    """Brass skirting door stop with a black rubber buffer, `length` from the skirting face. Origin on the skirting
    face, axis +Z (the caller turns it to point into the room)."""
    shaft = max(length - .016, .006)
    mb = mo.MB()
    mb.lathe([(0, 0), (.015, 0), (.015, .004), (.012, .006), (.0075, .009), (.0075, shaft), (0, shaft)], 'brass', 16)
    mb.lathe([(0, shaft), (.0105, shaft), (.0115, shaft + .003), (.0115, length - .003), (.009, length), (0, length)],
             M.solid('yellow_rubber', '#1C1B1A', .8), 16)
    return mb.finish(name)


def _masses(ctx):
    """Piers and boxings of this room as (x0, x1, y0, y1, z0, z1): the parts of the east wall that stand proud."""
    out = []
    for f in ctx.features:
        if f.get('room') == ROOM and f.get('type') in ('pier', 'boxing') and f.get('polygon'):
            xs, ys = zip(*f['polygon'])
            z = f.get('z') or (ctx.floor_z(ROOM), ctx.ceil_z(ROOM))
            out.append((min(xs), max(xs), min(ys), max(ys), z[0], z[1]))
    return out


def _chair():
    """The dining side chair with its straight front legs swapped for cabriole ball-and-claw legs (v3 f_0130, f_0132)."""
    ob = dining_chair('yellow_room.chair')
    ob.data = ob.data.copy()                    # the dining chairs keep their own mesh
    ob.data.name = 'yellow_room.chair'
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    seen, doomed = set(), []
    for v0 in bm.verts:                         # ponytail: drop the loose parts that are the straight front legs and
        if v0 in seen:                          # their reeds (below the seat rail, wholly in front of the centre);
            continue                            # relies on dining_chairs building them as separate islands
        isl, todo = [], [v0]
        seen.add(v0)
        while todo:
            v = todo.pop()
            isl.append(v)
            for e in v.link_edges:
                o = e.other_vert(v)
                if o not in seen:
                    seen.add(o)
                    todo.append(o)
        if max(v.co.z for v in isl) < 0.41 and max(v.co.y for v in isl) < 0:
            doomed += isl
    if not doomed:
        print('[yellow_room] WARNING: dining chair front legs not found, the chair keeps them beside the cabriole legs')
    bmesh.ops.delete(bm, geom=doomed, context='VERTS')
    bm.to_mesh(ob.data)
    bm.free()
    for i, s in enumerate((-1, 1)):
        leg = P.turned_leg(.40, .055, 'cabriole', .06, 0, dark_wood(), out=(s, -1), foot='claw',
                           name=f'yellow_room.chair.leg.{i}')
        leg.parent = ob
        leg.location = (s * (.265 - .028), -.25 + .028, 0)
    return ob


def build(ctx):
    xs, ys = zip(*ctx.room_poly(ROOM))
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)          # x1 = face of the east wall beside the window
    fz, cz = ctx.floor_z(ROOM), ctx.ceil_z(ROOM)
    xp = min(x for x, _ in ctx.feature('yellow_pier_e')['polygon'])     # pier face (south end of the east wall)
    w = ctx.opening_frame('w_yellow')
    wy, hw, sill, head = w['center'].y, w['width'] / 2, fz + w['sill'], fz + w['head']
    xf = w['center'].x + abs(w['face_out']) - w['ext_reveal'] - 0.06      # room face of the uPVC frame
    mass = [m for m in _masses(ctx) if m[1] >= x1 - .01]                  # proud parts of the east wall

    def east_face(y, z):                                                   # room face of the east wall at (y, z)
        return min([m[0] for m in mass if m[2] - 1e-4 <= y <= m[3] + 1e-4 and m[4] <= z <= m[5]], default=x1)

    def jamb_pier(yj, z):                                                  # a pier flush with a window jamb (niche side)
        return any(abs(m[3] - yj) < .02 or abs(m[2] - yj) < .02 for m in mass if m[4] <= z <= m[5])

    def add(ob, kind, sym=None, lm=None):
        return ctx.add(ob, ROOM, kind, plan_sym=sym, lm=lm)

    # ---- lighting: 2 x 2 downlights on the one-gang switch by the door (spec 8). Rows at the spec's fractions of the
    #      clear length (0.75 and 2.00 of 2.65 between the old west wall and the east face x 3.00): 0.68 from the new
    #      west wall, as v3 f_0130 puts the west row (about 1.22-1.29 from two lights' bearings)
    xe = east_face(y0 + .01, fz + 1.0)
    for i, (x, y) in enumerate((x, y) for x in (x0 + .283 * (xe - x0), x0 + .755 * (xe - x0))
                               for y in (y0 + .52, y0 + 1.50)):
        lighting.downlight(ctx, ROOM, x, y, watts=60, kelvin=3000, name=f'yellow_room.downlight.{i}')
        add(P.place(P.downlight(name=f'yellow_room.downlight_trim.{i}'), (x, y, cz)), 'light')
    sw = P.place(P.switch_plate(1, 'dimmer', name='yellow_room.switch'), (x0, y0 + .86, fz + 1.22),   # rotary
                 facing=(1, 0))                                           # dimmer knob: v3 f_0129, f_0130
    IX.tag(sw, 'light', rooms=[ROOM], label='Lights')
    add(sw, 'fit', lm='dynamic')

    # ---- sockets (spec 5.3; the south-wall socket is not in v3 f_0085 / f_0129, left out). North pair from the
    #      north-east corner: v3 f_0092 (square-on, 146 mm plate = 59 px) spur 0.12 short of it, 17 mm gap to the socket
    xn = east_face(y1 - .03, fz + .50)
    for nm, ob, loc, n in (
            ('socket.n', P.socket(2), (xn - .296, y1, fz + .50), (0, -1)),
            ('spur.n', P.switch_plate(1), (xn - .163, y1, fz + .50), (0, -1)),       # air-con fused spur
            ('socket.pier', P.socket(2), (xp, y0 + .37, fz + .30), (-1, 0)),
            ('socket.w', P.socket(1), (x0, y0 + .76, fz + .40), (1, 0))):
        ob.name = f'yellow_room.{nm}'
        add(P.place(ob, loc, facing=n), 'fit')

    # ---- air-con remote in its wall cradle between the switch and the architrave; blank LCD
    mb = mo.MB()
    mb.box((-.026, -.012, -.085), (.026, 0, .02), WHITE, bev=.003)                   # cradle
    mb.box((-.022, -.022, -.075), (.022, -.004, .085), WHITE, bev=.004)              # handset
    mb.box((-.015, -.0228, .03), (.015, -.021, .07), M.solid('yellow_lcd', '#A7B0A2', .3))
    add(P.place(mb.finish('yellow_room.ac_remote'), (x0, y0 + .97, fz + 1.27), facing=(1, 0)), 'fit')

    # ---- air-con indoor unit high on the north wall, trunking to the north-east corner (spec 5.1; no logo):
    #      flat front over a recessed outlet flap, round sensor disc at the right end, near-flat underside (v3 f_0092)
    az = fz + 2.06
    xne = east_face(y1 - .03, az + .04)                                    # the north-east corner at trunking height
    ax1 = min(x1 - .10, xne - .09)                                         # spec x 2.20..3.00; 9 cm of trunking at least
    ax0 = ax1 - .80
    mb = mo.MB()
    mb.sweep([(0, 0), (.19, 0), (.21, .007), (.219, .016), (.22, .022), (.22, .27), (.205, .288), (.18, .29), (0, .29)],
             [(ax1, y1, az), (ax0, y1, az)], WHITE)
    gap = M.solid('yellow_ac_gap', '#6E6E6B', .6)
    fy0, fy1 = y1 - .2212, y1 - .2199                                      # 1.3 mm proud of the front face
    fl, fr, fb, ft = ax0 + .04, ax1 - .13, az + .028, az + .09             # flap: the lower quarter of the front
    for a_, b_ in (((fl, fy0, fb), (fr, fy1, fb + .0025)), ((fl, fy0, ft - .0025), (fr, fy1, ft)),
                   ((fl, fy0, fb), (fl + .0025, fy1, ft)), ((fr - .0025, fy0, fb), (fr, fy1, ft))):
        mb.box(a_, b_, gap)                                                # outline of the outlet flap
    mb.box((ax0 + .012, fy0, ft + .008), (ax1 - .012, fy1, ft + .0095), gap)  # shadow line under the front panel
    grey = M.solid('yellow_ac_sensor', '#9A9B98', .35)
    for zc, rr in ((az + .062, .015), (az + .036, .004)):                 # sensor disc and indicator dot
        mb.at(T((ax1 - .068, y1 - .2199, zc)) @ Matrix.Rotation(math.pi / 2, 4, 'X'))
        mb.lathe([(0, 0), (rr, 0), (rr, .0016), (0, .0016)], grey, 20)
    mb.at()
    mb.box((ax1 - .002, y1 - .06, az + .02), (xne, y1, az + .06), WHITE, bev=.003)
    add(mb.finish('yellow_room.aircon'), 'fit')

    # ---- column radiator under the window: 8 oval tubes (v3 f_0096; 0.53 wide, not the spec's 0.36)
    n, pitch, a, b, h = 8, .066, .030, .038, .62
    yc = -(.03 + b)
    q = [math.radians(t) for t in (22.5, 45, 67.5, 90)]
    tube = ([(0, 0)] + [(a * math.sin(t), a - a * math.cos(t)) for t in q]
            + [(a * math.cos(t), h - a + a * math.sin(t)) for t in [0] + q[:3]] + [(0, h)])
    mb = mo.MB()
    xe = (n - 1) / 2 * pitch
    for i in range(n):
        mb.at(T((i * pitch - xe, yc, 0)))
        mb.lathe(tube, 'white_gloss', 14, ell=(1, b / a))
    mb.at()
    for z in (.055, h - .055):                                                        # headers through the tubes
        mb.tube([(-xe, yc, z), (xe, yc, z)], .017, 'white_gloss')
    mb.tube([(xe, yc, h - .055), (xe + a + .012, yc, h - .055)], .008, 'chrome')      # bleed plug
    for s, head_mat in ((-1, WHITE), (1, 'chrome')):                                  # TRV north, lockshield south
        xv = s * (xe + a + .03)
        mb.tube([(s * xe, yc, .055), (xv, yc, .055)], .011, 'chrome')
        mb.tube([(xv, yc, .055), (xv, 0, .055)], .0075, 'chrome')                     # tail into the wall
        if s < 0:                                                                     # TRV: chrome collar, upright
            mb.tube([(xv, yc, .05), (xv, yc, .075)], .012, 'chrome')                  # white head (v3 f_0090, f_0096)
            mb.tube([(xv, yc, .075), (xv, yc, .14)], .017, head_mat, n=12)
        else:
            mb.tube([(xv, yc, .055), (xv, yc - .035, .055)], .012, head_mat)
    # v3 f_0090 (square-on): the tube bank is nearer the north cheek (gaps 55 / 115 px between the cheeks at 60 / 470
    # px); with the perspective of the board's ends (face 30 / 42 px) its centre is 0.03-0.08 north of the window's
    add(P.place(mb.finish('yellow_room.radiator'), (x1, wy + .05, fz + .13), facing=(-1, 0)), 'fit', 'radiator')

    # ---- dark walnut-stained board in the reveal, nosing 50 mm proud of the wall below the window (the front edge
    #      sits about a quarter of the way out of the niche in the t = 108 s still); ears only where no niche side stops it
    es, en = (0 if jamb_pier(yj, sill) else .03 for yj in (wy - hw, wy + hw))
    mb = mo.MB()
    pine = M.image_mat('yellow_sill_pine', _pine_tex(), size_m=(.25, 1.0), roughness=.35)     # knotty, satin
    # 45 mm board, 15 mm round on the front arris, 25 mm apron under the nosing: the front reads about 70 mm and the
    # gap down to the radiator about 0.13, as in f_0090 (face 35 px against 245 px for the radiator) and f_0096
    D, t_, r_ = xf + .002 - (x1 - .05), .045, .015
    nose = [(D - r_ + r_ * math.sin(math.radians(g)), t_ - r_ + r_ * math.cos(math.radians(g))) for g in range(90, -1, -15)]
    mb.sweep([(0, 0), (D, 0)] + nose + [(0, t_)],                  # travel +y: d runs from the frame into the room
             [(xf + .002, wy - hw - es, sill - .015), (xf + .002, wy + hw + en, sill - .015)], pine)
    mb.box((x1 - .045, wy - hw - es, sill - .04), (x1 - .025, wy + hw + en, sill - .015), pine, bev=.002, grain=1)
    add(mb.finish('yellow_room.sill'), 'fit')

    # ---- Roman blind face-fixed above the window hole (under the niche head where there is one): head rail + bead
    #      chain (trigger), raised stack (state 0) clear of the fanlight's bottom rail as in f_0109, full drop (state 1)
    cloth = P.two_sided(M.image_mat('yellow_blind', os.path.join(ART, 'yellow_room_blind.jpg'), None, roughness=.9))
    top = min([m[4] for m in mass if m[2] < wy < m[3] and m[4] > head - .01], default=head + .06)
    bw, drop = 2 * hw - .02, top - sill - .035
    mb = mo.MB()
    mb.box((-bw / 2, -.012, -.035), (bw / 2, .012, 0), WHITE)
    mb.tube([(bw / 2 - .004, -.02, -.02), (bw / 2 - .004, -.02, -.95)], .002, 'chrome', n=5)
    rail = mb.finish('yellow_room.blind.rail')
    up = _cloth('yellow_room.blind.up', [
        (-.014, 0), (-.03, -.05), (-.06, -.12), (-.072, -.18), (-.066, -.205), (-.05, -.21), (-.038, -.195),
        (-.055, -.215), (-.058, -.232), (-.045, -.24), (-.034, -.225),
        (-.047, -.245), (-.05, -.262), (-.038, -.27), (-.028, -.255),
        (-.04, -.275), (-.042, -.292), (-.03, -.30), (-.018, -.285)], bw, cloth, 1.016)
    down = _cloth('yellow_room.blind.down', [(-.014, 0), (-.014, -drop), (-.002, -drop)], bw, cloth, 1.016)
    for ob in (rail, up, down):
        add(P.place(ob, (x1 - .013, wy, top), facing=(-1, 0)), 'decor', lm='dynamic')
    IX.tag(rail, 'trigger', g='yellow_room.blind', label='Blind')
    IX.tag(up, 'show', g='yellow_room.blind', when=0, fx='none', label='Blind')
    IX.tag(down, 'show', g='yellow_room.blind', when=1, fx='none', label='Blind')

    # ---- mahogany cupboard on cabriole legs against the west wall (spec 6); both doors open on empty shelves
    cw, cd, ch, leg, wood = .55, .38, 1.02, .24, 'mahogany_dark'          # 1.02 high: v3 f_0130, horizon at eye 1.63
    cy, bh = y0 + .15 + cw / 2, ch - leg - .028
    L = lambda dx, dy, dz: (x0 + .022 - dy, cy + dx, fz + dz)       # cupboard frame (x along the front, -y out) -> world
    add(P.place(P.cabinet_carcass(cw, cd - .02, bh, wood, plinth=0, open_front=True, shelves=1,
                                  name='yellow_room.cabinet'), L(0, 0, leg), facing=(1, 0)), 'furn', 'console')
    mb = mo.MB()
    tt, ov, tp = .024, .02, .012                       # top: 24 mm board overhanging 20 mm, thumb-moulded on 3 sides
    mb.box((-cw / 2 - ov + tp, -cd - ov + tp, ch - tt), (cw / 2 + ov - tp, 0, ch), wood, grain=0)
    thumb = [(0, 0), (.003, 0), (.006, .004), (.006, .008), (.0095, .009), (.012, .013), (.011, .018), (.007, .0225),
             (0, tt)]
    mb.sweep(thumb, [(cw / 2 + ov - tp, -.0005, ch - tt), (cw / 2 + ov - tp, -cd - ov + tp, ch - tt),
                     (-cw / 2 - ov + tp, -cd - ov + tp, ch - tt), (-cw / 2 - ov + tp, -.0005, ch - tt)], wood)
    mb.box((-cw / 2 - .006, -cd - .006, leg - .012), (cw / 2 + .006, -.002, leg), wood, bev=.003, grain=0)  # stand top
    hs, za = cw / 2 - .03, leg - .012                                     # front rail: flush with the leg fronts,
    us = [i / 16 for i in range(17)]                                      # cusped lower edge (v3 f_0129, f_0130)

    def depth(u):
        e = max(0.0, min(1.0, (u - .5) / .36))
        return .028 + .03 * e * e * (3 - 2 * e) + .02 * max(0.0, 1 - u / .2) ** 2
    edge = [(-hs * u, za - depth(u)) for u in us[::-1]] + [(hs * u, za - depth(u)) for u in us[1:]]
    mb.prism([(-hs, -cd, za)] + [(x, -cd, z) for x, z in edge] + [(hs, -cd, za)], (0, .018, 0), wood, grain=0)
    for s in (-1, 1):                                                      # side rails, flush with the leg sides
        mb.box((s * (cw / 2 - .018), -cd + .045, leg - .06), (s * cw / 2, -.045, za), wood, bev=.002)
    add(P.place(mb.finish('yellow_room.cabinet.top'), L(0, 0, 0), facing=(1, 0)), 'furn')
    for i, (s, fb) in enumerate((s, fb) for s in (-1, 1) for fb in (0, 1)):
        lg = (P.turned_leg(leg, .045, 'cabriole', .05, 0, wood, out=(s, -1), foot='pad') if fb == 0 else
              P.turned_leg(leg, .045, 'taper', .05, 0, wood))
        lg.name = f'yellow_room.cabinet.leg.{i}'
        add(P.place(lg, L(s * (cw / 2 - .0225), -.0225 if fb else -cd + .0225, 0), facing=(1, 0)), 'furn')
    for i, s in enumerate((-1, 1)):                # framed, fielded doors; one escutcheon + drop on the north (right) door
        d = P.place(_fielded_door(f'yellow_room.cabinet.door.{i}', cw / 2 - .002, bh - .004, wood),
                    L(s * cw / 4, -(cd - .02), leg + .002), facing=(1, 0))
        parts = [d]
        if s > 0:
            parts.append(P.place(_escutcheon('yellow_room.cabinet.pull'), L(.024, -cd, leg + bh * .55), facing=(1, 0)))
        IX.tag_many(parts, 'hinge', g=f'yellow_room.cabinet.door.{i}', label='Cupboard',
                    p=L(s * cw / 2, -(cd - .02), 0), deg=s * 95)
        for ob in parts:
            add(ob, 'furn', lm='dynamic')

    # ---- along the north wall, tight together as in v3 f_0092, f_0130, f_0134, f_0138: the open door leaf, the brass
    #      stop near its free end, the chair just beyond it, the ottoman to a few cm short of the east wall.
    #      Ottoman lid 1.09 long: f_0092, its back top edge on the wall plane spans 7.5 widths of the 146 mm double
    #      socket (443 / 59 px) = 1.09 +/- 0.05, its back corner 25 mm past the spur, about 0.08 short of the east face.
    #      The chair (the dining side chair, 0.53 at the seat front, 0.445 at the back) stands against its west end with
    #      the seat side meeting the lid's front corner; its west cresting ear tucks behind the open leaf's free end
    #      (f_0131: the ear lines up with the leaf edge), clear of the leaf's arc
    leaf = _leaf_line(fz)
    leaf_end = leaf[0] if leaf else x0 + .78
    ow, od = 1.09, .39                                             # lid; the box below is 15 mm smaller all round
    ox = min(east_face(y1 - .03, fz + .2), east_face(y1 - od, fz + .2)) - .08 - ow / 2
    cx = ox - ow / 2 - .25                                         # seat half-width 0.25 at the ottoman's front line
    if cx - .30 < leaf_end - .07:
        print(f'[yellow_room] WARNING: chair ear {cx - .30:.3f} runs deep behind the open leaf (end {leaf_end:.3f})')
    add(P.place(_chair(), (cx, y1 - .33, fz)), 'furn', 'chair')
    leather = M.solid('yellow_ottoman_white', '#DAD9D3', .4)      # darker than the spec white: keeps the tufts readable
    ott = P.place(P.bevel_box(ow - .03, od - .03, .30, leather, bevel=.008, segments=2, name='yellow_room.ottoman'),
                  (ox, y1 - .015 - od / 2, fz))
    lid = P.bevel_box(ow, od, .045, leather, bevel=.004, name='yellow_room.ottoman.lid')
    lid.parent, lid.location = ott, (0, 0, .30)
    top, zt, buttons = _tufted_top('yellow_room.ottoman.top', ow, od, leather, res=(44, 16), puff=.018, dimple=.012)
    top.parent, top.location = ott, (0, 0, .341)                   # rim at the foot of the lid box's 4 mm bevel
    button = M.solid('yellow_ottoman_button', '#B9B7AF', .3)      # covered buttons read a shade greyer (f_0092)
    for k, (bx_, by_) in enumerate(buttons):                       # one shared mesh
        b = P.lathe([(0, 0), (.0095, 0), (.009, .003), (.006, .0055), (0, .0065)], 12, button,     # 19 mm (f_0092)
                    name=f'yellow_room.ottoman.button.{k}')
        b.parent, b.location = ott, (bx_, by_, .341 + zt(bx_, by_) - .003)
    add(ott, 'furn', 'stool')

    # ---- brass door stop on the north skirting 6 cm short of the leaf's free end, just west of the chair's back leg
    #      (v3 f_0134, f_0138); its buffer reaches the open leaf (at openAngle 95 the gap is under 70 mm, so it is short)
    sx = leaf_end - .06
    sk = bpy.data.objects.get('yellow_room.skirting')
    ys = y1 - .018
    if sk is not None:                                             # face of the north skirting at the stop's height
        pts = [sk.matrix_world @ v.co for v in sk.data.vertices]
        ys = min([p.y for p in pts if y1 - .05 < p.y < y1 and p.z < fz + .12 and x0 + .1 < p.x < x1 - .2] or [ys])
    length = max(.02, min(.07, ys - (leaf[1](sx) if leaf else ys - .07) - .001))
    stop = _door_stop('yellow_room.door_stop', length)
    stop.location, stop.rotation_euler = (sx, ys, fz + .10), (math.pi / 2, 0, 0)
    add(stop, 'fit')

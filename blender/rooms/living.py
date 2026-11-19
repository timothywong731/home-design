"""Living room furnishing: spec/rooms/living.md (reconciled to spec/house.json).

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --only shell,living --preview living --res 540x960 --samples 64 --tag living

Room: x 0.80..4.30, y 0.99..5.19, 45-degree chamfer (0.80, 4.78) -> (1.21, 5.19) behind the door, bay x 1.10..4.00 /
y 0..0.99, ceiling 2.95. W wall (x 0.80) = terracotta TV wall, N wall (y 5.19) = bookcase wall, E wall (x 4.30) = sofa /
gallery wall, bay to the south. Phase-2 corrections (spec/phase2/ground_corrections.md 1, 4, 9): TV, TV unit,
amplifier, coffee table, rug, sofa and the big floral painting on one east-west axis y 2.33; N-wall items moved
north with the wall; the shell builds the bay-nib splays and the NW chamfer (their skirting is mouldings').
Helpers: living_parts (seating, tables), living_case (bookcase, chairs, TV unit, A/C), living_decor (lights,
ornaments). Textures in blender/textures/art/living: picture / tapestry / rug crops (reference/work/living/art.py,
rug.py, fix1/tex_fix.py) and generated maps (not reference-derived): toile*.jpg (fix1/gen_tex.py), tartan.jpg, velvet*.jpg,
oak_dark.jpg (fix2/gen_tex2.py).
"""
import os
import sys
import math
from math import sin, cos, pi, radians, sqrt, tau
import bpy
import bmesh
from mathutils import Vector
from lib import interact as IX, lighting, materials as M, mouldings as mo, props as P, shell

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:                       # build.py loads this file by path: make the helpers importable
    sys.path.insert(0, _HERE)
import living_parts as LP
import living_case as LC
import living_decor as LD

ROOM = 'living'
ART = os.path.normpath(os.path.join(_HERE, '..', 'textures', 'art', 'living'))
X0, X1, Y0, Y1 = 0.80, 4.30, 0.99, 5.19          # main room inside faces (W, E, nib line, N)
AXIS = 2.33                                     # furniture axis (ground_corrections L6): TV, unit, table, sofa, B5
RAIL_Z, RAIL_OFF = 2.70, 0.045                  # brass picture rail (shell): axis height, distance off the wall

CAMERAS = [   # ref: v1 frame (reference/frames) or v2:<frame> (reference/v2/frames)
    dict(name='bay', pos=(2.40, 3.90, 1.5), look=(2.5, 0.0, 1.4), fov_deg=100, ref='f_0791'),
    dict(name='door', pos=(1.10, 4.19, 1.55), look=(3.9, 2.2, 1.0), fov_deg=100, ref='f_0087'),
    dict(name='tvwall', pos=(3.70, 2.90, 1.5), look=(0.8, 2.90, 1.45), fov_deg=100, ref='f_0099'),
    dict(name='north', pos=(1.70, 3.30, 1.5), look=(3.4, 5.19, 1.55), fov_deg=100, ref='v2:f_0861'),
    dict(name='east', pos=(1.75, 2.45, 1.45), look=(4.3, 2.15, 1.6), fov_deg=100, ref='v2:f_0845'),
    dict(name='eastn', pos=(2.20, 3.40, 1.5), look=(4.3, 4.10, 1.75), fov_deg=100, ref='v2:f_0731'),
    dict(name='chamfer', pos=(2.30, 3.75, 1.35), look=(1.0, 4.95, 0.55), fov_deg=100, ref='v2:f_0791'),
    dict(name='baycorner', pos=(2.35, 1.15, 1.5), look=(1.15, 0.45, 1.9), fov_deg=90, ref='f_0127'),
    dict(name='nib_e', pos=(3.05, 1.75, 1.3), look=(4.05, 0.92, 2.0), fov_deg=90, ref='v2:f_0749'),
    dict(name='bayside', pos=(2.05, 2.5, 1.5), look=(2.7, 0.3, 1.0), fov_deg=100, ref='f_0115'),
    dict(name='table', pos=(2.00, 1.40, 1.5), look=(3.4, 3.4, 0.3), fov_deg=100, ref='f_0139'),
    # interaction checks (blender/INTERACT.md): render with --pose 0 and --pose 1
    dict(name='ix_dimmer', pos=(1.75, 3.15, 1.35), look=(0.8, 3.45, 1.22), fov_deg=45, ref='v2:f_0801'),
    dict(name='ix_tvunit', pos=(2.45, 2.70, 1.05), look=(0.9, 2.33, 0.45), fov_deg=80, ref='v2:f_0833'),
    dict(name='ix_bookcase', pos=(2.55, 3.40, 1.45), look=(2.95, 4.96, 0.75), fov_deg=80, ref='f_0185'),
    dict(name='ix_clock', pos=(3.02, 4.41, 1.42), look=(3.085, 4.96, 1.35), fov_deg=35, ref='f_0785'),
    dict(name='ix_lamp', pos=(2.25, 1.35, 1.25), look=(2.6, 0.1, 0.95), fov_deg=80, ref='f_0115'),
]

# Gallery, hung from the brass rail. (id, position along the wall, top z, outer w, outer h, frame style, frame w, glazed)
PICS_N = [                                       # N wall, position = x
    ('A1', 2.06, 2.66, 0.70, 0.55, 'gilt_bead', 0.06, False),          # A1 / A2 20 mm up: A2 clears the glasses tray;
    ('A2', 2.06, 2.09, 0.63, 0.82, 'baroque', 0.095, False),            # x 2.06: 15 mm off the tapestry. A2 = rippled frame
    ('A3', 3.82, 2.63, 0.62, 0.52, 'gilt_swept', 0.08, False),
    ('A4', 3.82, 2.09, 0.54, 0.70, 'gilt_bead', 0.06, False),
]
# E wall: B5 centred on the axis, the watercolour pair north of it, the botanical pair south, the oils at the north end
# (L6). Sizes from the daylight frames: rod-to-floor 2.70 m scales B5 to ~0.85 x 1.15 in v2:f_0845, the others 5-15 %
# over living.md; gaps B1|B3 ~0.3, B3|B5 and B5|B6 < 0.1 (v2:f_0731, f_0733, f_0845).
PICS_E = [                                       # E wall, position = y
    ('B1', 4.36, 2.66, 0.70, 0.58, 'gilt_bead', 0.055, False),
    ('B2', 4.36, 2.02, 0.72, 0.62, 'champagne', 0.055, False),
    ('B3', 3.25, 2.66, 0.84, 0.66, 'bronze_gold', 0.06, True),
    ('B4', 3.25, 1.96, 0.84, 0.66, 'bronze_gold', 0.06, True),
    ('B5', AXIS, 2.62, 0.80, 1.10, 'bronze_gold', 0.06, True),
    ('B6', 1.66, 2.60, 0.44, 0.54, 'gilt_thin', 0.015, True),
    ('B7', 1.66, 1.98, 0.44, 0.54, 'gilt_thin', 0.015, True),
]


def _add(ctx, ob, kind, sym=None, lm=None):
    return ctx.add(ob, ROOM, kind, plan_sym=sym, lm=lm)


# ----------------------------------------------------------------------------------------- NW chamfer, controls
def chamfer_edge(ctx):
    """The 45-degree NW chamfer behind the door (ground_corrections L1): (west corner, unit along it from the west
    corner, unit room-side normal), read from the room polygon (counter-clockwise: the room is on the left)."""
    poly = ctx.room_poly(ROOM)
    for a, b in zip(poly, poly[1:] + poly[:1]):
        if abs(a[0] - b[0]) > 1e-3 and abs(a[1] - b[1]) > 1e-3:
            a, b = Vector(a), Vector(b)
            t = (b - a).normalized()
            return b, -t, Vector((-t.y, t.x))
    raise ValueError('living: no diagonal edge in the room polygon')


def door_stop(ctx, w, u, n, along=0.47, z=0.30):
    """Wall-mounted brass door stop on the chamfer (L2): square rose 40 x 40, 70 mm overall with its black rubber tip,
    `along` metres from the chamfer's west corner. A leaf hinged at the living face of the wall and open 135 degrees
    stands ~0.21 off the chamfer (0.30 of wall between hinge and chamfer, times sin 45), so it cannot rest on a 70 mm
    stop: the gap is measured and printed for the report (the real leaf opens ~147 degrees onto it)."""
    bpy.context.view_layer.update()
    leaf = bpy.data.objects.get('living.d_living.leaf')
    gap = 0.074
    if leaf is not None:
        ds = [(leaf.matrix_world @ v.co) for v in leaf.data.vertices]
        ds = [(Vector((p.x, p.y)) - w).dot(n) for p in ds if abs(p.z - z) < 0.25 and abs((Vector((p.x, p.y)) - w).dot(u) - along) < 0.25]
        if ds:
            gap = min(ds)
    L = 0.074
    mb = mo.MB()
    B = M.mat('brass')
    mb.box((-0.02, -0.006, -0.02), (0.02, 0.0, 0.02), B, bev=0.002)
    mb.at(LP.Rx(90))                                  # lathe axis +Z -> -Y: out of the wall
    mb.lathe([(0, 0.006), (0.009, 0.006), (0.0065, 0.012), (0.0065, L - 0.022), (0.0085, L - 0.02), (0, L - 0.02)], B, 14)
    mb.lathe([(0, L - 0.02), (0.012, L - 0.02), (0.012, L - 0.003), (0.009, L), (0, L)], M.mat('black_matt'), 14)
    mb.at()
    p = w + u * along
    ob = P.place(mb.finish('living.door_stop'), (p.x, p.y, z), facing=tuple(n))
    _add(ctx, ob, 'fit')
    print(f'[living] door stop: leaf face {gap:.3f} off the chamfer, stop {L:.3f} long')
    return gap


def dimmer(ctx, loc=None):
    """3-gang rotary dimmer 146 x 86 on the TV wall (ground_corrections 1): one object per knob so that every knob
    drives its own circuit. As you face it: right (north) = ceiling spotlights, middle = the two wall lights, left
    (south) = chandelier. The viewer bakes the room as one circuit, so the plate body + spotlight knob is the room
    switch `living.dimmer` (bake, and every lamp of the room with it); the other two knobs share a `lamp` group with
    their fittings (living.sconces, living.chandelier), which switch the fittings' glow. Returns (sconce knob,
    chandelier knob)."""
    loc = loc or (X0, 3.40, 1.21)
    plate = P.place(P.switch_plate(3, 'blank', wide=True, name='living.dimmer'), loc, facing=(1, 0))
    _add(ctx, plate, 'fit', lm='dynamic')
    mb = mo.MB().at(LP.Tr(0, -0.009, 0) @ LP.Rx(90))
    mb.lathe([(0, 0), (0.0135, 0), (0.0125, 0.012), (0.011, 0.014), (0, 0.014)], 'plastic_white', 16)
    first = None
    knobs = []
    for x, what in ((0.036, 'spots'), (0.0, 'wall_lights'), (-0.036, 'chandelier')):
        name = 'living.dimmer.knob.' + what
        k = first = mb.finish(name) if first is None else bpy.data.objects.new(name, first.data)
        k.matrix_basis = plate.matrix_basis @ LP.Tr(x, 0, 0)
        _add(ctx, k, 'fit', lm='dynamic')
        knobs.append(k)
    IX.tag_many([plate, knobs[0]], 'light', g='living.dimmer', rooms=[ROOM], label='Lights')
    return knobs[1], knobs[2]


# ----------------------------------------------------------------------------------------- gallery
def _hang(mb, p, n, z_to, hook=True):
    """Brass chain from the top of a frame at p (wall point, z = frame top) up to z_to; n = wall normal."""
    B = M.mat('brass')
    q = Vector((p[0], p[1], 0)) + Vector((n[0], n[1], 0)) * RAIL_OFF
    mb.tube([(q.x, q.y, p[2] - 0.01), (q.x, q.y, z_to)], 0.0016, B, 4)
    if hook:                                     # S-hook over the rail
        t = Vector((-n[1], n[0], 0))
        ring = [tuple(Vector((q.x, q.y, RAIL_Z)) + 0.0135 * (cos(a) * Vector((n[0], n[1], 0)) + sin(a) * Vector((0, 0, 1))))
                for a in (radians(-110 + 290 * k / 9) for k in range(10))]
        LP.rtube(mb, ring, 0.002, B, 4)


GOLDS = {'gilt_bright': 'bright', 'gold_antique': 'antique', 'gold_champagne': 'champagne', 'gold_bronze': 'bronze'}


def _regild(pic):
    """Swap the library gilt of a framed_picture for the module golds (LP.gold): the library ones render
    orange-copper against this room's pink walls. The mesh is unique to the picture (its image is an argument)."""
    if pic.data.users > 1:
        pic.data = pic.data.copy()
    for i, m in enumerate(pic.data.materials):
        if m is not None and m.name in GOLDS:
            pic.data.materials[i] = LP.gold(GOLDS[m.name])


def _rail_stops():
    """Where an S-hook cannot sit on the lib picture rail, read from the rail as built (mouldings.brass_rail: ball
    finials r 0.016 at both ends, brackets every <= 0.9 m and 0.06 in from each end of a run). -> {wall: (position of
    the ball at the free end, [ball and bracket positions])}, positions = x on the N run, y on the E run."""
    rail = bpy.data.objects.get('living.picture_rail')
    if rail is None:
        return {}
    vs = [rail.matrix_world @ v.co for v in rail.data.vertices]
    xc, yc = X1 - RAIL_OFF, Y1 - RAIL_OFF                       # the corner of the two runs
    out = {}
    for wall, end, corner, sgn in (('N', min(v.x for v in vs) + 0.016, xc, 1), ('E', min(v.y for v in vs) + 0.016, yc, -1)):
        L = abs(corner - end)
        k = max(1, math.ceil(L / 0.9))
        a = end if sgn > 0 else corner                          # run start (the N run starts at its ball, the E run at the corner)
        out[wall] = (end, [end] + [a + sgn * min(max(L * i / k, 0.06), L - 0.06) for i in range(k + 1)])
    return out


def _free(s, stops, end, K=0.034):
    """Move a hook position s off the ball / brackets (K = their radius + the hook's) and onto the tube past the end ball."""
    merged = []
    for a, b in sorted([(-1e9, end + K)] + [(o - K, o + K) for o in stops]):
        if merged and a <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    for a, b in merged:
        if a < s < b:
            return b if a < -1e8 or b - s < s - a else a
    return s


def gallery(ctx):
    stops = _rail_stops()
    hang = mo.MB()
    for wall, pics in (('N', PICS_N), ('E', PICS_E)):
        n = (0, -1) if wall == 'N' else (-1, 0)
        end, obst = stops.get(wall, (-1e9, []))
        below = {}
        for pid, pos, top, w, h, style, fw, glass in pics:
            if style == 'baroque':
                pic = LD.baroque_frame(os.path.join(ART, pid + '.jpg'), w, h, fw, mat=LP.gold('antique'), name=f'living.art.{pid}')
            else:
                pic = P.framed_picture(image=os.path.join(ART, pid + '.jpg'), w=w, h=h, frame_style=style, frame_w=fw,
                                       glass=glass, tilt_deg=3.0, name=f'living.art.{pid}')
                _regild(pic)
            loc = (pos, Y1 - 0.022, top - h / 2) if wall == 'N' else (X1 - 0.022, pos, top - h / 2)
            P.place(pic, loc, facing=n)
            _add(ctx, pic, 'decor')
            upper = below.get(round(pos, 2))     # the lower picture of a column hangs from the upper one, on its chains
            ss = upper[1] if upper else [_free(pos + s * (w / 2 - 0.05), obst, end) for s in (-1, 1)]
            for sv in ss:
                p = (sv, Y1, top) if wall == 'N' else (X1, sv, top)
                _hang(hang, p, n, RAIL_Z - 0.012 if upper is None else upper[0], hook=upper is None)
            below[round(pos, 2)] = (top - h, ss)
    # tapestry: unframed textile on six brass hooks
    w, h, top, xc = 0.95, 1.40, 2.66, 2.90
    tm = M.image_mat('living_tapestry', os.path.join(ART, 'TAP.jpg'), size_m=(w, h), roughness=0.95)
    tb = mo.MB()
    tb.face([(0, -0.008, 0), (w, -0.008, 0), (w, -0.008, h), (0, -0.008, h)], tm, (0, -1, 0))
    tb.box((0.0, -0.0065, 0.0), (w, 0.0, h), M.paint('#1B2145'))
    tap = tb.finish('living.tapestry')
    tap.location = (xc - w / 2, Y1 - 0.02, top - h)
    _add(ctx, tap, 'decor', lm='static')
    end, obst = stops.get('N', (-1e9, []))
    for k in range(6):
        _hang(hang, (_free(xc - w / 2 + 0.04 + (w - 0.08) * k / 5, obst, end), Y1, top + 0.012), (0, -1), RAIL_Z - 0.012)
    _add(ctx, hang.finish('living.art.hangers'), 'decor')


# ----------------------------------------------------------------------------------------- build
def build(ctx):
    cz = ctx.ceil_z(ROOM)
    k_wall, k_chand = dimmer(ctx)

    # ---- W wall: TV, unit, A/V, controller, sconces (all on the axis y 2.33, L6)
    tv = P.tv_panel(1.89, 1.08, name='living.tv')
    P.place(tv, (X0, AXIS, 1.26), facing=(1, 0))
    _add(ctx, tv, 'fit', 'tv', lm='static')
    pic = P.tv_screen(1.88, 1.07, name='living.tv.picture')        # the lit picture, 1 mm proud of the black glass
    pic.location, pic.rotation_euler = tv.matrix_basis @ Vector((0, -0.0716, 0)), tv.rotation_euler
    _add(ctx, pic, 'fit', lm='dynamic')
    IX.tag(tv, 'trigger', g='living.tv', label='TV')
    IX.tag(pic, 'show', g='living.tv', when=1, fx='tv', label='TV')
    unit, ux = LC.tv_unit()
    P.place(unit, (X0 + 0.235, AXIS, 0), facing=(1, 0))              # local +x = north
    for i, sx in enumerate((-1, 1)):                      # speakers with their plain black cloth grilles on (f_0205)
        LP.kid(unit, LD.speaker(f'living.speaker.{i}'), (sx * 0.78, 0.02, 0.56), (0, 0, -sx * 8))
    LP.kid(unit, LD.amplifier(), (0.0, -0.07, 0.56))                # centred on the unit (v2:f_0825-0833)
    LP.kid(unit, LD.xiangqi(), (0.425, -0.01, 0.56), (0, 0, 4))     # between the amplifier and the north speaker, ~6 mm off both
    LP.kid(unit, LD.games_console(), (0.0, 0.01, 0.282))            # games console, centred on the open shelf
    _add(ctx, unit, 'furn', 'tv_unit', lm='static')
    U = unit.matrix_basis                                 # cupboards hinge on the outer posts, the drawer slides out
    for i, (objs, p, deg) in enumerate(ux['doors']):
        IX.tag_many(objs, 'hinge', g=f'living.tv_unit.door.{i}', label='Cupboard', p=U @ Vector(p), deg=deg)
    drawer, d = ux['drawer']
    IX.tag_many(drawer, 'slide', g='living.tv_unit.drawer', label='Drawer', d=U.to_3x3() @ Vector(d))
    for o in [o for objs, _, _ in ux['doors'] for o in objs] + drawer + ux['inner']:
        o['lm'] = 'dynamic'                               # moving parts and what they reveal are not baked
    mb = mo.MB()
    Wp = M.mat('plastic_white')
    mb.box((X0, AXIS - 0.02, 0.56), (X0 + 0.016, AXIS + 0.02, 0.73), Wp, bev=0.002)      # cable trunking, TV to unit
    mb.box((X0, 3.50, 1.225), (X0 + 0.022, 3.56, 1.375), Wp, bev=0.003)                  # A/C controller in cradle
    mb.box((X0 + 0.021, 3.51, 1.32), (X0 + 0.0233, 3.55, 1.36), M.solid('living_lcd', '#9AA39A', 0.3))
    mb.box((0.905, Y0, 1.458), (0.99, Y0 + 0.025, 1.542), Wp, bev=0.004)                 # thermostat on the west nib's room face
    _add(ctx, mb.finish('living.wall_controls'), 'fit')
    sc0 = LD.sconce('living.sconce.0')
    P.place(sc0, (X0, 1.60, 2.38), facing=(1, 0))
    sc1 = LP.instance(sc0, 'living.sconce.1')
    P.place(sc1, (X0, 4.09, 2.38), facing=(1, 0))
    for sc in (sc0, sc1):
        _add(ctx, sc, 'light')
    # one circuit (L7): both fittings and the middle dimmer knob switch together
    IX.tag_many(P.family(sc0) + P.family(sc1) + [k_wall], 'lamp', g='living.sconces', label='Wall lights')
    bpy.context.view_layer.update()
    for i, sc in enumerate((sc0, sc1)):
        for j, p in enumerate(P.bulb_points(sc)):
            lighting.bulb(ctx, ROOM, p, watts=W_SCONCE, kelvin=3000, name=f'living.sconce.{i}.lamp.{j}')

    # ---- NW chamfer: double socket 0.30 along it, brass door stop for the leaf open at 135 degrees (L1, L2, 9)
    w, u, n = chamfer_edge(ctx)
    s = w + u * 0.30
    _add(ctx, P.place(P.socket(2, name='living.socket.chamfer'), (s.x, s.y, 0.31), facing=tuple(n)), 'fit')
    door_stop(ctx, w, u, n)

    # ---- E wall, south to north: sofa on the axis, side table + tantalus, A/C console, pedestal + bird in the corner
    sofa = LP.sofa()
    P.place(sofa, (3.93, AXIS, 0), facing=(-1, 0))                   # 1.43 .. 3.23
    _add(ctx, sofa, 'furn', 'sofa')
    st = LP.side_table()
    P.place(st, (4.085, 3.52, 0), facing=(-1, 0))                    # 3.29 .. 3.75
    LP.kid(st, LD.tantalus(), (0, 0.02, 0.72))
    _add(ctx, st, 'furn', 'table')
    ac = LC.aircon()
    P.place(ac, (X1, 4.18, 0), facing=(-1, 0))                       # 3.805 .. 4.555, under B1 / B2
    _add(ctx, ac, 'fit', 'radiator', lm='static')
    ped = LC.torchere()
    P.place(ped, (4.02, 4.95, 0))
    LP.kid(ped, LD.bird(), (0, 0, 0.938), (0, 0, -40))            # bill toward the E wall, as in f_0154
    _add(ctx, ped, 'furn', 'table_round')
    _add(ctx, P.place(P.socket(2, name='living.socket'), (X1, 5.03, 0.33), facing=(-1, 0)), 'fit')   # behind the pedestal

    # ---- N wall: bookcase with its ornaments, bench, plant
    bc, doors = LC.bookcase()
    P.place(bc, (2.875, Y1 - 0.20, 0), facing=(0, -1))              # back on the skirting face
    for i, (objs, p, deg) in enumerate(doors):
        IX.tag_many(objs, 'hinge', g=f'living.bookcase.door.{i}', label='Bookcase', p=bc.matrix_basis @ Vector(p), deg=deg)
    top = 1.2206
    ck = LD.clock()
    XT = LD.CUT()                                         # cut crystal: decanter, footed vases
    for ob, x, y, rz in (
            (LD.glass_tray(), -0.60, -0.04, 0),                # front edge flush with the top: glasses clear of A2
            (LD.cat(), -0.19, -0.085, 200),
            (LD.mercury(), -0.29, 0.07, 12),
            (P.vase(0.07, 0.15, 'bowl', M.solid('living_celadon', '#B4CCAE', 0.25), name='living.bowl'), -0.125, 0.07, 0),
            (P.decanter(0.30, 'round', mat=XT, name='living.decanter'), 0.008, 0.03, 0),
            (ck, 0.21, 0.02, 0),
            (P.vase(0.20, 0.10, 'urn', XT, name='living.crystal_vase.0'), 0.31, -0.11, 0),
            (P.vase(0.12, 0.08, 'urn', XT, name='living.crystal_vase.1'), 0.43, -0.125, 0),
            (LD.flowers(), 0.405, -0.015, 0),                  # blooms clear of the tapestry and the wall
            (LD.potpourri_jar(), 0.485, -0.04, 0),
            (LD.tea_tray(), 0.712, 0.03, 0)):
        LP.kid(bc, ob, (x, y, top), (0, 0, rz))
    _add(ctx, bc, 'furn', 'bookcase')
    Wc = P._world(ck)                                     # live hands on the bracket clock, modelled at 12
    centre, out = Wc @ Vector(LD.CLOCK_DIAL), Wc.to_3x3() @ Vector((0, -1, 0))
    for hand, wh in zip(P.clock_hands(LD.CLOCK_R, 'baton', mat='black_matt', name='living.clock'), 'hm'):
        hand.location, hand.rotation_euler = centre, Wc.to_euler()
        IX.tag(hand, 'clock', hand=wh, p=centre, a=out)
        _add(ctx, hand, 'decor', lm='dynamic')
    bn = LP.bench()
    P.place(bn, (2.90, 3.75, 0))                          # just north of the coffee table (L6), ~1 m off the bookcase
    _add(ctx, bn, 'furn', 'stool')
    plant = P.plant_potted('dracaena', height=0.95, spread=0.62, pot_dia=0.28, pot_h=0.26, pot_mat='black_matt',
                           stand=0.05, leaves=80, name='living.plant')       # dense strap-leaf head (v2:f_0717, f_0861)
    # beside the chamfer corner (v2:f_0791): leaves clear of the N wall, the bookcase end and the door open at 135; the
    # leaf brushes the outer leaves over its first 30 degrees of closing (any 0.6 m plant in this corner does)
    P.place(plant, (1.62, 4.86, 0))
    _add(ctx, plant, 'decor', 'plant')

    # ---- centre: rug, coffee table on the axis, footstool
    rug = P.rug(os.path.join(ART, 'rug.jpg'), 1.40, 2.00, corner_r=0.01, name='living.rug')
    P.place(rug, (2.80, AXIS, 0))
    _add(ctx, rug, 'decor', 'rug', lm='static')
    ct = LP.coffee_table()
    P.place(ct, (2.80, AXIS, 0), rot_z=90)
    _add(ctx, ct, 'furn', 'coffee_table')
    fs = LP.footstool()
    P.place(fs, (3.12, 1.22, 0), rot_z=8)                 # in front of the east armchair (v2:f_0805, f_0873)
    _add(ctx, fs, 'furn', 'stool')

    # ---- bay: armchairs, lamp table + lamp, curtains
    ch0 = LC.armchair('living.armchair.0')
    P.place(ch0, (1.76, 0.61, 0), facing=(0.33, 0.94))
    ch1 = bpy.data.objects.new('living.armchair.1', ch0.data)
    P.place(ch1, (3.34, 0.61, 0), facing=(-0.33, 0.94))
    # loose velvet cushion propped on the east chair's back (v2:f_0755, f_0805, f_0873; the throw on it is clutter)
    LP.kid(ch1, P.cushion(0.48, 0.48, 0.15, mat=LP.velvet(), name='living.armchair.1.cushion'), (0.0, 0.235, 0.63), (80, 0, 4))
    for ch in (ch0, ch1):
        _add(ctx, ch, 'furn', 'armchair')
    lt = LC.lamp_table()
    P.place(lt, (2.55, 0.37, 0))
    lamp = LD.table_lamp()
    LP.kid(lt, lamp, (0.0, -0.13, 0.64))
    LP.kid(lt, LD.solitaire(), (-0.15, 0.06, 0.64))
    LP.kid(lt, LD.inlay_box(), (0.14, 0.09, 0.64), (0, 0, -25))
    _add(ctx, lt, 'furn', 'table_round')
    IX.tag_many(P.family(lamp), 'lamp', g='living.table_lamp', label='Lamp')      # plugged in: its own switch
    lighting.bulb(ctx, ROOM, (2.55, 0.24, 0.64 + 0.60), watts=W_LAMP, kelvin=2900, radius=0.03, name='living.table_lamp.bulb')
    curtains(ctx)
    gallery(ctx)

    # ---- chandelier on the rose (clickable, and on the dimmer's left knob), downlights
    rx, ry = mo.ROSE_AT[ROOM]
    ch = P.chandelier(0.76, 0.78, arms=8, upper_arms=4, upper_dia=0.40, mat=LP.brass(), body='bowl', crystals=False,
                      shade=None, name='living.chandelier')       # polished yellow brass; 0.89 over shades and crystals
    P.place(ch, (rx, ry, cz - 0.038))
    org = Vector(ch.location)
    bulbs = [p - org for p in P.bulb_points(ch)]
    hub = Vector((0, 0, -0.78 + 0.13))
    for part in LD.chandelier_dressing(bulbs, hub):
        part.parent = ch
    for i, c in enumerate(P.family(ch)):                 # lib children carry generic names
        if not c.name.startswith('living.'):
            c.name = f'living.chandelier.arm.{i:02d}'
    _add(ctx, ch, 'light')
    # The group box runs from the fitting to the knob on the wall (x 0.81-3.00, z 1.20-2.91). reach 0.7 limits Space / E
    # to 0.7 m round that box (the default 1.6 covers most of the room); inside the box it cannot help, since the viewer
    # measures reach and angle on the union box (viewer request). A mouse click on the fitting works from 4 m.
    IX.tag_many(P.family(ch) + [k_chand], 'lamp', g='living.chandelier', label='Chandelier', reach=0.7)
    for j, p in enumerate(bulbs):
        lighting.bulb(ctx, ROOM, tuple(p + org), watts=W_CHAND, kelvin=3000, radius=0.04, name=f'living.chandelier.lamp.{j}')
    k = 0
    for x in (1.40, 2.55, 3.70):                          # ring of eight round the rose, none in the bay
        for y in (ry - 1.35, ry, ry + 1.45):
            if x == rx and y == ry:
                continue
            lighting.downlight(ctx, ROOM, x, y, watts=W_DOWN, kelvin=3000, name=f'living.downlight.{k}')
            _add(ctx, P.place(P.downlight(name=f'living.downlight_trim.{k}'), (x, y, cz)), 'light')
            k += 1


# Radiometric watts per emitter. The downlights carry the floor and walls; the 12 candle bulbs and the 10 sconce
# lamps give the up-light that makes the ceiling read near-white as in f_0791 / f_0133 (bulb radius 0.04 for the
# chandelier so the extra energy spreads instead of burning a hot spot above it).
W_DOWN, W_CHAND, W_SCONCE, W_LAMP = 52, 18, 26, 25


def _strip_slots(ob, mats):
    """Remove every face of `ob` that uses one of `mats` (on a private copy of the mesh) and drop the slots."""
    me = ob.data.copy()
    kill = {i for i, m in enumerate(me.materials) if m in mats}
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index in kill], context='FACES')
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    used = {f.material_index for f in bm.faces}
    bm.to_mesh(me)
    bm.free()
    for i in sorted(kill, reverse=True):
        if i > max(used):                        # trailing slots only: the cloth keeps its index
            me.materials.pop(index=i)
    ob.data = me
    return ob


def _true_sett(me, sett=0.16, z0=-0.25, z1=-0.60):
    """props.curtain_panel writes U for a fullness of 2 whatever the folds are; with a few broad folds the cloth
    is only ~1.2 x its hanging width, which would squeeze the checks to 60 %. Rescale the UVs of this (private)
    mesh so that one repeat is `sett` metres square on the cloth surface, measured on the rows between z0 and z1.
    sett 0.16: f_0127 shows ~10.5 repeats down the 1.65 m from heading to tie-back and 3 across a drop (the
    spec's 0.20 was a rough estimate)."""
    uv = me.uv_layers[0].data
    size = me.materials[0].get('size_m', (1.0, 1.0))
    L3 = Lu = 0.0
    for p in me.polygons:
        li = list(p.loop_indices)
        for a, b in zip(li, li[1:] + li[:1]):
            va, vb = me.vertices[me.loops[a].vertex_index].co, me.vertices[me.loops[b].vertex_index].co
            if abs(uv[a].uv.y - uv[b].uv.y) < 1e-6 and z1 < min(va.z, vb.z) and max(va.z, vb.z) < z0:
                L3 += (va - vb).length
                Lu += abs(uv[a].uv.x - uv[b].uv.x)
    f = (L3 / sett) / Lu
    for d in uv:
        d.uv.x *= f
        d.uv.y *= size[1] / sett
    return f


def tieback(side, width, gather, depth=0.06, wall=0.075, name='living.tieback'):
    """Tie-back of one drop, in the curtain's own frame (origin = the tie height on the track line under the
    heading centre, room toward -Y, the wall `wall` metres behind it at y = +wall): a two-strand twisted cream rope
    swagged diagonally from a brass hook on the wall behind the cloth's edge down round the gathered bunch, and a
    slim 0.30 m champagne-gold tassel hanging at the front (v2:f_0747). side = +1 / -1: bunch (and hook) toward
    +X / -X. The bunch geometry mirrors props.curtain_panel."""
    f = gather * 0.8                                           # width fraction of the cloth at the tie
    hw, cx = width * f / 2, side * (width / 2) * (1 - f)
    a = depth * min(1.7, f ** -0.5) * 1.22                     # depth of the bunch
    hook = Vector((side * (width / 2 - 0.006), 0.012, 0.10))  # behind the cloth, so the rope wraps the bunch
    far = cx - side * (hw + 0.014)
    xm, ax = (hook.x + far) / 2, abs(hook.x - far) / 2
    ym, ay = -0.012 - a / 2, a / 2 + 0.02

    def centre(t):                                             # loop: t = 0 at the hook, pi at the far side of the bunch
        w = cos(t / 2) ** 6                                    # 1 at the hook, ~0 round the bunch
        return Vector((xm + side * ax * cos(t), ym * (1 - w) + hook.y * w + ay * (1 - w) * sin(t),
                       0.035 + 0.065 * cos(t) - 0.02 * sin(t) ** 2))
    mb = mo.MB()
    rope = M.mat('linen_cream')
    mb._soft = 1
    turns, per = 19, 6
    n = turns * per
    for k in (0, 1):                                           # two strands wound round each other
        pts = []
        for i in range(n + 1):
            t = tau * i / n
            c = centre(t)
            tan = (centre(t + 0.01) - centre(t - 0.01)).normalized()
            n1 = tan.cross(Vector((0, 0, 1))).normalized()
            n2 = tan.cross(n1)
            ph = tau * turns * i / n + pi * k
            pts.append(tuple(c + 0.0036 * (cos(ph) * n1 + sin(ph) * n2)))
        LP.rtube(mb, pts, 0.0046, rope, 4)
    mb._soft = 0
    B = M.mat('brass')                                         # hook: stem out of the timber / wall face, upturned tip
    yw = wall - 0.012                                          # the dark timber cladding stands 12 mm proud of the wall
    LP.rtube(mb, [(hook.x, yw, hook.z - 0.012), (hook.x, hook.y + 0.012, hook.z - 0.012), (hook.x, hook.y, hook.z - 0.004),
                  (hook.x, hook.y - 0.002, hook.z + 0.012)], 0.004, B, 6)
    mb.at(LP.Tr(hook.x, yw, hook.z - 0.012) @ LP.Rx(90))
    mb.lathe([(0, 0), (0.014, 0), (0.012, 0.004), (0, 0.005)], B, 10)
    p = centre(3 * pi / 2)                                     # the tassel hangs at the front of the bunch
    mb.at(LP.Tr(p.x, p.y - 0.004, p.z - 0.004))
    gold = M.solid('living_tassel', '#B5A174', 0.8)            # champagne gold (lib tassel_gold renders yellow)
    mb._soft = 1
    mb.lathe([(0, -0.122), (0.017, -0.122), (0.02, -0.114), (0.015, -0.106), (0.022, -0.094), (0.026, -0.078), (0.022, -0.062),
              (0.011, -0.05), (0.0045, -0.046), (0.0045, 0.004), (0, 0.004)], gold, 12)             # cord, bulb head, binding
    mb._soft = 0
    rings = []                                                 # long straight skirt of threads: fluted
    for r, z in ((0.0175, -0.118), (0.019, -0.20), (0.021, -0.30)):
        rings.append([((r + (0.0022 if j % 2 else -0.0022)) * cos(tau * j / 28), (r + (0.0022 if j % 2 else -0.0022)) * sin(tau * j / 28),
                       z) for j in range(28)])
    LP.loft(mb, rings, gold, caps=(False, True))
    mb.at()
    return mb.finish(name)


def drawn_curtains(cloth, top, hem, off, ye=0.875, sett=0.16, name='living.curtain.closed'):
    """The four drops untied and drawn right round the bay (interaction state 1), in world coordinates: one
    pleated sheet along each cheek and one across the front, 3 mm in front of the track line `off` from the wall,
    folds 40 mm deep. The lamp table stands against the sill with the lamp shade 7 mm off the window timber, so
    behind them the cloth is pressed back: every column runs straight from the track to where the shade rim
    pushes it (z 1.15), on to the table edge (z 0.645) and plumb below; the 0.17 m of cloth pinched behind the
    table ends on the sill board instead of reaching the floor. ye: north end of the cheek sheets (clear of the nib
    splays). Returns the cloth object (the track is static, curtains())."""
    LAMP, R_SHADE, TABLE, R_TABLE = (2.55, 0.24), 0.181, (2.55, 0.37), 0.317     # obstacle radii + 8 mm clearance
    Z_SHADE, Z_TABLE, Z_SILL, Y_NOSE = 1.15, 0.645, 0.626, 0.064                 # sill board: top 0.62, nose y 0.06
    zt = top - 0.003                                                             # heading just under the track
    zs = [zt, 2.25, 1.70, Z_SHADE, 0.90, Z_TABLE, Z_SILL, 0.37, hem]
    xw, xe, yf = 1.10 + off + 0.003, 4.00 - off - 0.003, off + 0.003
    runs = [((xw, ye), (0, -1), ye - yf, (1, 0)),                    # west cheek
            ((xw, yf), (1, 0), xe - xw, (0, 1)),                     # front: the folds die out at both ends, so the
            ((xe, yf), (0, 1), ye - yf, (-1, 0))]                    # east cheek      three sheets meet in the corners
    verts, uvs, faces = [], [], []
    for (sx, sy), t, length, n in runs:
        folds = round(length / 0.16)                                 # broad soft folds, as the tied drops
        cols = folds * 10
        base, u, prev, landed = len(verts), 0.0, None, []
        for c in range(cols + 1):
            s = length * c / cols
            o = 0.04 * (0.5 - 0.5 * cos(tau * folds * c / cols))
            p = Vector((sx + t[0] * s + n[0] * o, sy + t[1] * s + n[1] * o))
            u += (p - prev).length if prev is not None else 0.0
            prev = p
            y1 = y2 = p.y
            if n[1]:                                                 # front run: pressed back behind the lamp and the table
                dx = p.x - LAMP[0]
                if abs(dx) < R_SHADE:
                    y1 = min(p.y, LAMP[1] - sqrt(R_SHADE ** 2 - dx ** 2))
                y2 = min(y1, TABLE[1] - sqrt(R_TABLE ** 2 - dx ** 2)) if abs(dx) < R_TABLE else y1
            landed.append(y2 < Y_NOSE)                               # no way past the sill nose: the cloth lies on the sill
            for z in zs:
                if z >= Z_SHADE:
                    y = p.y + (y1 - p.y) * (zt - z) / (zt - Z_SHADE)
                else:
                    y = y1 + (y2 - y1) * min(1.0, (Z_SHADE - z) / (Z_SHADE - Z_TABLE))
                verts.append((p.x, y, z))
                uvs.append((u / sett, z / sett))
        nz = len(zs)
        for c in range(cols):
            for r in range(nz - 1):
                if zs[r + 1] < Z_SILL and (landed[c] or landed[c + 1]):
                    continue
                a, b = base + c * nz + r, base + (c + 1) * nz + r
                faces.append((a, b, b + 1, a + 1))                   # rows run downward: this winding faces the room
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    uvl = me.uv_layers.new(name='UVMap')
    for poly in me.polygons:
        poly.use_smooth = True
        for li, vi in zip(poly.loop_indices, poly.vertices):
            uvl.data[li].uv = uvs[vi]
    me.materials.append(cloth)
    return bpy.data.objects.new(name, me)


def curtains(ctx):
    """Four tartan drops on a concealed white track under the bay cornice, each gathered and tied back at
    z 1.15 with a swagged twisted rope and tassel (module-built: the prop's rigid hoop is stripped).
    Interaction group living.curtains: the tied drops and their tie-backs show in state 0, the cloth drawn
    round the bay (drawn_curtains) in state 1."""
    top, hem, tie = 2.79, 0.12, 1.15
    W, GATHER, FOLDS, DEPTH = 0.48, 0.50, 3, 0.05     # three broad soft folds per drop: the 0.2 m checks stay whole (f_0211)
    off = 0.075                                  # clear of the dark timber and the sill board
    ys = min(min(c['p'][1], c['q'][1]) for c in ctx.chamfers(ROOM) if c['reflex'])   # 0.884: where the nib splays start
    yr = ys - W / 2 - 0.012                      # the return drops end at the splay, as in v2:f_0745 / f_0749
    spec = [                                     # (location, wall normal, bunch side seen from the room)
        ((1.10 + off, yr, top), (1, 0), 'right'),        # west return, tied toward the nib
        ((1.10 + off + W / 2, off, top), (0, 1), 'right'),   # front, west corner, tied to the corner: clear of the
        ((4.00 - off - W / 2, off, top), (0, 1), 'left'),    # return sill board's nose; front, east corner
        ((4.00 - off, yr, top), (-1, 0), 'left'),        # east return
    ]
    cloth = LP.tartan()
    # the shutters (joinery) swing into the drawn curtains: the viewer shuts them before the curtains are drawn
    excl = sorted(o.name for o in bpy.data.objects if '.shutter.' in o.name and o.get('room') == ROOM and 'ix' in o.keys())
    dead = M.solid('living_tie_strip', '#000000', 1.0)   # the prop's hoop: stripped below
    meshes, ties = {}, {}
    for i, (loc, n, side) in enumerate(spec):
        c = P.curtain_panel(W, top - hem, cloth, folds=FOLDS, depth=DEPTH, tieback=side, tie_from_top=top - tie,
                            gather=GATHER, tassel=0, tie_mat=dead, name=f'living.curtain.{i}')
        if side not in meshes:
            meshes[side] = _strip_slots(c, {dead, M.mat('brass')}).data
            meshes[side].name = f'living.curtain.{side}'
            _true_sett(meshes[side])
            ties[side] = tieback(1 if side == 'right' else -1, W, GATHER, DEPTH, off, name=f'living.curtain.{i}.tieback')
            tb = ties[side]
        else:
            tb = bpy.data.objects.new(f'living.curtain.{i}.tieback', ties[side].data)
        c.data = meshes[side]
        LP.kid(c, tb, (0, 0, tie - top))
        _add(ctx, P.place(c, loc, facing=n), 'decor')
        IX.tag_many([c, tb], 'show', g='living.curtains', when=0, fx='none', label='Curtains', excl=excl)
    # one continuous white track round the bay under the cornice (v2:f_0741, f_0749): both cheeks to the ends of the
    # return drops, the front between them; 40 mm deep from 10 mm behind the heading line, butt-jointed in the corners
    tr = mo.MB()
    Wp, z0, z1, ye = M.mat('plastic_white'), top - 0.002, top + 0.012, yr + W / 2
    xw, xe = 1.10 + off, 4.00 - off
    tr.box((xw - 0.01, off - 0.01, z0), (xw + 0.03, ye, z1), Wp)
    tr.box((xw + 0.03, off - 0.01, z0), (xe - 0.03, off + 0.03, z1), Wp)
    tr.box((xe - 0.03, off - 0.01, z0), (xe + 0.01, ye, z1), Wp)
    _add(ctx, tr.finish('living.curtain_track'), 'fit')
    ob = drawn_curtains(cloth, top, hem, off, ye=ys - 0.008)
    _add(ctx, ob, 'decor', lm='dynamic')
    IX.tag(ob, 'show', g='living.curtains', when=1, fx='none', label='Curtains', excl=excl)

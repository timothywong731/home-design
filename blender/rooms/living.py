"""Living room furnishing: spec/rooms/living.md (reconciled to spec/house.json).

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --only shell,living --preview living --res 540x960 --samples 64 --tag living

Room: x 0.80..4.30, y 0.99..4.73, bay x 1.10..4.00 / y 0..0.99, ceiling 2.95. W wall (x 0.80) = terracotta TV
wall, N wall (y 4.73) = bookcase wall, E wall (x 4.30) = sofa / gallery wall, bay to the south.
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
X0, X1, Y0, Y1 = 0.80, 4.30, 0.99, 4.73          # main room inside faces
RAIL_Z, RAIL_OFF = 2.70, 0.045                  # brass picture rail (shell): axis height, distance off the wall

CAMERAS = [
    dict(name='bay', pos=(2.40, 3.59, 1.5), look=(2.5, 0.0, 1.4), fov_deg=100, ref='f_0791'),
    dict(name='door', pos=(1.10, 4.19, 1.55), look=(3.9, 2.2, 1.0), fov_deg=100, ref='f_0087'),
    dict(name='tvwall', pos=(3.40, 3.19, 1.5), look=(0.8, 2.8, 1.4), fov_deg=100, ref='f_0099'),
    dict(name='north', pos=(1.40, 3.59, 1.5), look=(4.0, 4.73, 1.5), fov_deg=100, ref='f_0785'),
    dict(name='east', pos=(2.70, 1.99, 1.4), look=(4.3, 3.2, 2.0), fov_deg=100, ref='f_0133'),
    dict(name='baycorner', pos=(2.35, 1.15, 1.5), look=(1.15, 0.45, 1.9), fov_deg=90, ref='f_0127'),
    dict(name='bayside', pos=(2.05, 2.5, 1.5), look=(2.7, 0.3, 1.0), fov_deg=100, ref='f_0115'),
    dict(name='table', pos=(2.10, 1.89, 1.5), look=(3.6, 3.6, 0.3), fov_deg=100, ref='f_0139'),
    # interaction checks (blender/INTERACT.md): render with --pose 0 and --pose 1
    dict(name='ix_tvunit', pos=(2.45, 2.75, 1.05), look=(0.9, 2.2, 0.45), fov_deg=80, ref='f_0205'),
    dict(name='ix_bookcase', pos=(2.55, 2.95, 1.45), look=(2.95, 4.5, 0.75), fov_deg=80, ref='f_0185'),
    dict(name='ix_clock', pos=(3.02, 3.95, 1.42), look=(3.085, 4.5, 1.35), fov_deg=35, ref='f_0785'),
    dict(name='ix_lamp', pos=(2.25, 1.35, 1.25), look=(2.6, 0.1, 0.95), fov_deg=80, ref='f_0115'),
]

# Gallery, hung from the brass rail. (id, position along the wall, top z, outer w, outer h, frame style, frame w, glazed)
PICS_N = [                                       # N wall, position = x
    ('A1', 2.03, 2.66, 0.70, 0.55, 'gilt_bead', 0.06, False),          # A1 / A2 20 mm up: A2 clears the glasses tray
    ('A2', 2.03, 2.09, 0.63, 0.82, 'baroque', 0.095, False),            # module-built rippled-leaf frame
    ('A3', 3.82, 2.63, 0.62, 0.52, 'gilt_swept', 0.08, False),
    ('A4', 3.82, 2.09, 0.54, 0.70, 'gilt_bead', 0.06, False),
]
PICS_E = [                                       # E wall, position = y
    ('B1', 4.267, 2.63, 0.62, 0.52, 'gilt_bead', 0.055, False),
    ('B2', 4.267, 2.09, 0.66, 0.58, 'champagne', 0.055, False),
    ('B3', 3.45, 2.63, 0.76, 0.62, 'bronze_gold', 0.06, True),
    ('B4', 3.45, 1.99, 0.76, 0.62, 'bronze_gold', 0.06, True),
    ('B5', 2.62, 2.60, 0.66, 0.92, 'bronze_gold', 0.06, True),
    ('B6', 1.99, 2.62, 0.42, 0.52, 'gilt_thin', 0.015, True),
    ('B7', 1.99, 2.08, 0.42, 0.52, 'gilt_thin', 0.015, True),
]


def _add(ctx, ob, kind, sym=None, lm=None):
    return ctx.add(ob, ROOM, kind, plan_sym=sym, lm=lm)


# ----------------------------------------------------------------------------------------- nib chamfers
def nib_chamfers(ctx):
    """70 mm chamfer on the two bay-nib arrises up to z 2.25, ending in a pointed lamb's-tongue stop.
    The shell is box CSG and cannot cut it: the two strips of living.walls next to each arris are removed
    (this room's own shell mesh) and replaced by one infill mesh in the same paint. The chamfer runs down to
    the floor so that the skirting can follow it as a 3-facet return (_nib_skirting)."""
    walls = shell.surface(ROOM, 'walls')
    if walls is None:
        return
    floor = shell.surface(ROOM, 'floor')
    L, z0, z1, hs, ya = 0.07 / sqrt(2), 0.0, 2.25, 0.11, Y0
    zs = z1 + hs
    bm = bmesh.new()
    bm.from_mesh(walls.data)
    mat = None

    def cut(faces, co, no):
        geom = list({e for f in faces for e in f.edges} | {v for f in faces for v in f.verts} | set(faces))
        bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-6, plane_co=co, plane_no=no)

    for xa, sx in ((1.10, -1), (4.00, 1)):       # sx: side of the arris the front-wall face lies on
        def on_a(f):
            return all(abs(v.co.y - ya) < 1e-4 and (v.co.x - xa) * sx > -1e-4 and (v.co.x - xa) * sx < 0.31 for v in f.verts)

        def on_b(f):
            return all(abs(v.co.x - xa) < 1e-4 and v.co.y < ya + 1e-4 and v.co.y > 0.05 for v in f.verts)
        for test, co, no in ((on_a, (xa + sx * L, 0, 0), (1, 0, 0)), (on_b, (0, ya - L, 0), (0, 1, 0))):
            cut([f for f in bm.faces if test(f)], co, no)
            cut([f for f in bm.faces if test(f)], (0, 0, z0), (0, 0, 1))
            cut([f for f in bm.faces if test(f)], (0, 0, zs), (0, 0, 1))
        dead = []
        for f in bm.faces:
            c = f.calc_center_median()
            if not (z0 < c.z < zs) or not (on_a(f) or on_b(f)):
                continue
            if (on_a(f) and abs(c.x - xa) < L) or (on_b(f) and ya - c.y < L):
                dead.append(f)
                mat = walls.data.materials[f.material_index]
        bmesh.ops.delete(bm, geom=dead, context='FACES')
    bm.to_mesh(walls.data)
    bm.free()
    if mat is None:
        return
    R = (hs * hs + L * L) / (2 * L)              # lancet stop: half-width L at the springing, a point hs above
    rows = [(z0, L), (z1, L)] + [(z1 + hs * k / 8, max(0.0, sqrt(R * R - (hs * k / 8) ** 2) - (R - L))) for k in range(1, 9)]
    mb = mo.MB()
    for xa, sx in ((1.10, -1), (4.00, 1)):
        n_ch = (-sx, 1, 0.4)
        for (za, ca), (zb, cb) in zip(rows, rows[1:]):
            a0, a1 = (xa + sx * ca, ya, za), (xa + sx * cb, ya, zb)
            b0, b1 = (xa, ya - ca, za), (xa, ya - cb, zb)
            mb.face([a0, b0, b1, a1] if cb > 1e-6 else [a0, b0, a1], mat, n_ch)
            if ca < L - 1e-6 or cb < L - 1e-6:
                mb.face([(xa + sx * L, ya, za), a0, a1, (xa + sx * L, ya, zb)], mat, (0, 1, 0))
                mb.face([(xa, ya - L, za), b0, b1, (xa, ya - L, zb)], mat, (-sx, 0, 0))
        if floor is not None:                    # floor under the cut-away arris (its tip shows past the skirting)
            mb.face([(xa, ya, 0.0), (xa + sx * L, ya, 0.0), (xa, ya - L, 0.0)], floor.data.materials[0], (0, 0, 1))
    _add(ctx, mb.finish('living.nib_chamfers'), 'trim', lm='static')
    _nib_skirting(ctx, L)


def _nib_skirting(ctx, L, d=0.10):
    """Skirting round the chamfered nib arrises: the square outside corner of living.skirting (this room's own
    trim mesh) is cut back `d` along both faces and replaced by a mitred 3-facet return in the same profile."""
    sk = bpy.data.objects.get('living.skirting')
    if sk is None:
        return
    ya = Y0
    bm = bmesh.new()
    bm.from_mesh(sk.data)
    for xa, sx in ((1.10, -1), (4.00, 1)):
        corner = [f for f in bm.faces if any(abs(v.co.x - xa) < 0.03 and abs(v.co.y - ya) < 0.03 for v in f.verts)]
        run_a = [f for f in corner if all(v.co.y > ya - 1e-4 for v in f.verts)]                 # on the face y = ya
        run_b = [f for f in corner if all(-sx * (v.co.x - xa) > -1e-4 for v in f.verts)]        # on the face x = xa
        for faces, co, no in ((run_a, (xa + sx * d, 0, 0), (1, 0, 0)), (run_b, (0, ya - d, 0), (0, 1, 0))):
            geom = list({e for f in faces for e in f.edges} | {v for f in faces for v in f.verts} | set(faces))
            bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-6, plane_co=co, plane_no=no)
        dead = []
        for f in bm.faces:
            c = f.calc_center_median()
            u, v = (c.x - xa) * sx, c.y - ya
            if c.z < 0.3 and ((-1e-3 < v < 0.03 and -0.03 < u < d) or (-1e-3 < -u < 0.03 and -d < v < 0.03)):
                dead.append(f)
        bmesh.ops.delete(bm, geom=dead, context='FACES')
        path = [(xa + sx * d, ya), (xa + sx * L, ya), (xa, ya - L), (xa, ya - d)]
        if sx > 0:                               # the room stays on the LEFT of travel
            path.reverse()
        ret = mo.sweep('sk_living', [(x, y, 0.0) for x, y in path], name='living.skirting.nib.' + ('w' if sx < 0 else 'e'),
                       material=sk.data.materials[0])
        _add(ctx, ret, 'trim', lm='static')
    bm.to_mesh(sk.data)
    bm.free()


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


def gallery(ctx):
    hang = mo.MB()
    for wall, pics in (('N', PICS_N), ('E', PICS_E)):
        n = (0, -1) if wall == 'N' else (-1, 0)
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
            upper = below.get(round(pos, 2))     # the lower picture of a column hangs from the upper one
            for s in (-1, 1):
                d = s * (w / 2 - 0.05)
                p = (pos + d, Y1, top) if wall == 'N' else (X1, pos + d, top)
                _hang(hang, p, n, RAIL_Z - 0.012 if upper is None else upper, hook=upper is None)
            below[round(pos, 2)] = top - h
    # tapestry: unframed textile on six brass hooks
    w, h, top, xc = 0.95, 1.40, 2.66, 2.90
    tm = M.image_mat('living_tapestry', os.path.join(ART, 'TAP.jpg'), size_m=(w, h), roughness=0.95)
    tb = mo.MB()
    tb.face([(0, -0.008, 0), (w, -0.008, 0), (w, -0.008, h), (0, -0.008, h)], tm, (0, -1, 0))
    tb.box((0.0, -0.0065, 0.0), (w, 0.0, h), M.paint('#1B2145'))
    tap = tb.finish('living.tapestry')
    tap.location = (xc - w / 2, Y1 - 0.02, top - h)
    _add(ctx, tap, 'decor', lm='static')
    for k in range(6):
        _hang(hang, (xc - w / 2 + 0.04 + (w - 0.08) * k / 5, Y1, top + 0.012), (0, -1), RAIL_Z - 0.012)
    _add(ctx, hang.finish('living.art.hangers'), 'decor')


# ----------------------------------------------------------------------------------------- build
def build(ctx):
    cz = ctx.ceil_z(ROOM)
    nib_chamfers(ctx)

    # ---- W wall: TV, unit, A/V, switch, controller, sconces
    tv = P.tv_panel(1.89, 1.08, name='living.tv')
    P.place(tv, (X0, 2.325, 1.26), facing=(1, 0))
    _add(ctx, tv, 'fit', 'tv', lm='static')
    pic = P.tv_screen(1.88, 1.07, name='living.tv.picture')        # the lit picture, 1 mm proud of the black glass
    pic.location, pic.rotation_euler = tv.matrix_basis @ Vector((0, -0.0716, 0)), tv.rotation_euler
    _add(ctx, pic, 'fit', lm='dynamic')
    IX.tag(tv, 'trigger', g='living.tv', label='TV')
    IX.tag(pic, 'show', g='living.tv', when=1, fx='tv', label='TV')
    unit, ux = LC.tv_unit()
    P.place(unit, (X0 + 0.235, 2.23, 0), facing=(1, 0))
    for i, sx in enumerate((-1, 1)):                      # speakers with their plain black cloth grilles on (f_0205)
        LP.kid(unit, LD.speaker(f'living.speaker.{i}'), (sx * 0.78, 0.02, 0.56), (0, 0, -sx * 8))
    LP.kid(unit, LD.amplifier(), (-0.34, -0.07, 0.56))
    LP.kid(unit, LD.xiangqi(), (0.28, -0.01, 0.56), (0, 0, 4))
    LP.kid(unit, LD.disc_player(), (0.0, 0.03, 0.282))
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
    mb.box((X0, 2.36, 0.56), (X0 + 0.016, 2.40, 0.73), Wp, bev=0.002)                    # cable trunking
    mb.box((X0, 3.50, 1.225), (X0 + 0.022, 3.56, 1.375), Wp, bev=0.003)                  # A/C controller in cradle
    mb.box((X0 + 0.021, 3.51, 1.32), (X0 + 0.0233, 3.55, 1.36), M.solid('living_lcd', '#9AA39A', 0.3))
    mb.box((0.905, Y0, 1.458), (0.99, Y0 + 0.025, 1.542), Wp, bev=0.004)                 # thermostat on the west nib's room face
    _add(ctx, mb.finish('living.wall_controls'), 'fit')
    sw = P.switch_plate(3, 'dimmer', name='living.dimmer')
    _add(ctx, P.place(sw, (X0, 3.40, 1.21), facing=(1, 0)), 'fit')
    IX.tag(sw, 'light', rooms=[ROOM], label='Lights')
    sock = P.socket(2, name='living.socket')
    _add(ctx, P.place(sock, (X1, 4.45, 0.33), facing=(-1, 0)), 'fit')
    sc0 = LD.sconce('living.sconce.0')
    P.place(sc0, (X0, 1.60, 2.38), facing=(1, 0))
    sc1 = LP.instance(sc0, 'living.sconce.1')
    P.place(sc1, (X0, 4.09, 2.38), facing=(1, 0))
    for i, sc in enumerate((sc0, sc1)):                   # wired to the dimmer plate: clicking one switches the room
        _add(ctx, sc, 'light')
        IX.tag_many(P.family(sc), 'lamp', g=f'living.sconce.{i}', label='Wall light', rooms=[ROOM])
    bpy.context.view_layer.update()
    for i, sc in enumerate((sc0, sc1)):
        for j, p in enumerate(P.bulb_points(sc)):
            lighting.bulb(ctx, ROOM, p, watts=W_SCONCE, kelvin=3000, name=f'living.sconce.{i}.lamp.{j}')

    # ---- E wall: sofa, side table + tantalus, A/C console, pedestal + bird
    sofa = LP.sofa()
    P.place(sofa, (3.93, 2.05, 0), facing=(-1, 0))
    _add(ctx, sofa, 'furn', 'sofa')
    st = LP.side_table()
    P.place(st, (4.08, 3.205, 0), facing=(-1, 0))
    LP.kid(st, LD.tantalus(), (0, 0.02, 0.72))
    _add(ctx, st, 'furn', 'table')
    ac = LC.aircon()
    P.place(ac, (X1, 3.825, 0), facing=(-1, 0))
    _add(ctx, ac, 'fit', 'radiator', lm='static')
    ped = LC.torchere()
    P.place(ped, (4.07, 4.50, 0))
    LP.kid(ped, LD.bird(), (0, 0, 0.938), (0, 0, -40))            # bill toward the E wall, as in f_0154
    _add(ctx, ped, 'furn', 'table_round')

    # ---- N wall: bookcase with its ornaments, bench, plant
    bc, doors = LC.bookcase()
    P.place(bc, (2.875, 4.55, 0), facing=(0, -1))
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
    for hand, w in zip(P.clock_hands(LD.CLOCK_R, 'baton', mat='black_matt', name='living.clock'), 'hm'):
        hand.location, hand.rotation_euler = centre, Wc.to_euler()
        IX.tag(hand, 'clock', hand=w, p=centre, a=out)
        _add(ctx, hand, 'decor', lm='dynamic')
    bn = LP.bench()
    P.place(bn, (2.85, 3.95, 0))
    _add(ctx, bn, 'furn', 'stool')
    plant = P.plant_potted('dracaena', height=1.10, spread=0.44, pot_dia=0.28, pot_h=0.26, pot_mat='black_matt',
                           stand=0.05, name='living.plant')
    P.place(plant, (1.75, 4.24, 0))                       # canopy clear of the open door leaf and the bookcase end
    _add(ctx, plant, 'decor', 'plant')

    # ---- centre: rug, coffee table, footstool
    rug = P.rug(os.path.join(ART, 'rug.jpg'), 1.40, 2.00, corner_r=0.01, name='living.rug')
    P.place(rug, (2.60, 2.76, 0))
    _add(ctx, rug, 'decor', 'rug', lm='static')
    ct = LP.coffee_table()
    P.place(ct, (2.80, 2.81, 0), rot_z=90)
    _add(ctx, ct, 'furn', 'coffee_table')
    fs = LP.footstool()
    P.place(fs, (3.20, 1.30, 0), rot_z=8)
    _add(ctx, fs, 'furn', 'stool')

    # ---- bay: armchairs, lamp table + lamp, curtains
    ch0 = LC.armchair('living.armchair.0')
    P.place(ch0, (1.76, 0.61, 0), facing=(0.33, 0.94))
    ch1 = bpy.data.objects.new('living.armchair.1', ch0.data)
    P.place(ch1, (3.34, 0.61, 0), facing=(-0.33, 0.94))
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

    # ---- chandelier on the rose, downlights
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
    for j, p in enumerate(bulbs):
        lighting.bulb(ctx, ROOM, tuple(p + org), watts=W_CHAND, kelvin=3000, radius=0.04, name=f'living.chandelier.lamp.{j}')
    k = 0
    for x in (1.40, 2.55, 3.70):
        for y in (1.53, 2.86, 4.19):
            if (x, y) == (2.55, 2.86):
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


def tieback(side, width, gather, depth=0.06, name='living.tieback'):
    """Tie-back of one drop, in the curtain's own frame (origin = the tie height on the wall plane under the
    heading centre, wall at y = 0, room toward -Y): a two-strand twisted cream rope swagged diagonally from a
    brass wall hook down round the gathered bunch, and a slim 0.30 m champagne-gold tassel hanging at the front.
    side = +1 / -1: bunch (and hook) toward +X / -X. The bunch geometry mirrors props.curtain_panel."""
    f = gather * 0.8                                           # width fraction of the cloth at the tie
    hw, cx = width * f / 2, side * (width / 2) * (1 - f)
    a = depth * min(1.7, f ** -0.5) * 1.22                     # depth of the bunch
    hook = Vector((side * (width / 2 + 0.025), -0.03, 0.10))
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
    B = M.mat('brass')                                         # hook: stem out of the wall, upturned tip
    LP.rtube(mb, [(hook.x, 0, hook.z - 0.012), (hook.x, -0.022, hook.z - 0.012), (hook.x, -0.034, hook.z - 0.004),
                  (hook.x, -0.036, hook.z + 0.012)], 0.004, B, 6)
    mb.at(LP.Tr(hook.x, 0, hook.z - 0.012) @ LP.Rx(90))
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


def drawn_curtains(cloth, top, hem, off, sett=0.16, name='living.curtain.closed'):
    """The four drops untied and drawn right round the bay (interaction state 1), in world coordinates: one
    pleated sheet along each cheek and one across the front, 3 mm in front of the track line `off` from the wall,
    folds 40 mm deep. The lamp table stands against the sill with the lamp shade 7 mm off the window timber, so
    behind them the cloth is pressed back: every column runs straight from the track to where the shade rim
    pushes it (z 1.15), on to the table edge (z 0.645) and plumb below; the 0.17 m of cloth pinched behind the
    table ends on the sill board instead of reaching the floor. Returns (cloth object, track infill object): the
    white track pieces that join the four short tracks of the tied-back drops."""
    LAMP, R_SHADE, TABLE, R_TABLE = (2.55, 0.24), 0.181, (2.55, 0.37), 0.317     # obstacle radii + 8 mm clearance
    Z_SHADE, Z_TABLE, Z_SILL, Y_NOSE = 1.15, 0.645, 0.626, 0.064                 # sill board: top 0.62, nose y 0.06
    zt = top - 0.003                                                             # heading just under the track
    zs = [zt, 2.25, 1.70, Z_SHADE, 0.90, Z_TABLE, Z_SILL, 0.37, hem]
    xw, xe, yf, ye = 1.10 + off + 0.003, 4.00 - off - 0.003, off + 0.003, 0.975
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
    tr = mo.MB()
    Wp = M.mat('plastic_white')
    tr.box((1.61, off - 0.01, top - 0.002), (3.49, off + 0.03, top + 0.012), Wp)
    for x0, x1 in ((1.10 + off - 0.01, 1.10 + off + 0.03), (4.00 - off - 0.03, 4.00 - off + 0.01)):
        tr.box((x0, off + 0.03, top - 0.002), (x1, 0.495, top + 0.012), Wp)
    return bpy.data.objects.new(name, me), tr.finish(name + '.track')


def curtains(ctx):
    """Four tartan drops on a concealed white track under the bay cornice, each gathered and tied back at
    z 1.15 with a swagged twisted rope and tassel (module-built: the prop's rigid hoop is stripped).
    Interaction group living.curtains: the tied drops and their tie-backs show in state 0, the cloth drawn
    round the bay (drawn_curtains) in state 1."""
    top, hem, tie = 2.79, 0.12, 1.15
    W, GATHER, FOLDS, DEPTH = 0.48, 0.50, 3, 0.05     # three broad soft folds per drop: the 0.2 m checks stay whole (f_0211)
    off = 0.075                                  # clear of the dark timber and the sill board
    spec = [                                     # (location, wall normal, bunch side seen from the room)
        ((1.10 + off, 0.735, top), (1, 0), 'right'),     # west return, tied to the nib
        ((1.37, off, top), (0, 1), 'right'),             # front, west corner, tied to the corner
        ((3.73, off, top), (0, 1), 'left'),              # front, east corner
        ((4.00 - off, 0.735, top), (-1, 0), 'left'),     # east return
    ]
    cloth = LP.tartan()
    dead = M.solid('living_tie_strip', '#000000', 1.0)   # the prop's hoop: stripped below
    meshes, ties = {}, {}
    tr = mo.MB()
    for i, (loc, n, side) in enumerate(spec):
        c = P.curtain_panel(W, top - hem, cloth, folds=FOLDS, depth=DEPTH, tieback=side, tie_from_top=top - tie,
                            gather=GATHER, tassel=0, tie_mat=dead, name=f'living.curtain.{i}')
        if side not in meshes:
            meshes[side] = _strip_slots(c, {dead, M.mat('brass')}).data
            meshes[side].name = f'living.curtain.{side}'
            _true_sett(meshes[side])
            ties[side] = tieback(1 if side == 'right' else -1, W, GATHER, DEPTH, name=f'living.curtain.{i}.tieback')
            tb = ties[side]
        else:
            tb = bpy.data.objects.new(f'living.curtain.{i}.tieback', ties[side].data)
        c.data = meshes[side]
        LP.kid(c, tb, (0, 0, tie - top))
        _add(ctx, P.place(c, loc, facing=n), 'decor')
        IX.tag_many([c, tb], 'show', g='living.curtains', when=0, fx='none', label='Curtains')
        t = (-n[1], n[0])
        a = (loc[0] - t[0] * (W / 2) - n[0] * 0.01, loc[1] - t[1] * (W / 2) - n[1] * 0.01)
        b = (loc[0] + t[0] * (W / 2) + n[0] * 0.03, loc[1] + t[1] * (W / 2) + n[1] * 0.03)
        tr.box((min(a[0], b[0]), min(a[1], b[1]), top - 0.002), (max(a[0], b[0]), max(a[1], b[1]), top + 0.012),
               M.mat('plastic_white'))
    _add(ctx, tr.finish('living.curtain_track'), 'fit')
    for ob in drawn_curtains(cloth, top, hem, off):
        _add(ctx, ob, 'decor', lm='dynamic')
        IX.tag(ob, 'show', g='living.curtains', when=1, fx='none', label='Curtains')

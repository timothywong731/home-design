"""Staircase: the whole flight from the hall floor to the half-landing (spec/rooms/stairs.md).

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --only shell,stairs --preview stairs --res 540x960 --samples 64 --tag stairs

Everything is derived from the stairs block of spec/house.json (15 risers of 0.19, going 0.23, R4 at
y 5.60, newel at (0.20, 5.33), landing 2.85).  World metres, +Y up the flight, balustrade on -X.
Print artwork and the carpet texture are drawn by blender/rooms/stairs_art.py (nothing is cropped from the footage).

Knee of the dado as filmed (full-res stills t=778.0 / 779.0 from the passage, t=241.5 / 245.5 from the hall):
the hall rail keeps its 0.965 from the living-room doorcase to the nib's outer corner (shell), turns the
corner and climbs across the nib return to the foot of the rake; a short level lead-in on the staircase
wall, then the rake - no plumb piece anywhere.  The shell's level rail on the nib return is removed here
(_drop_faces) until mouldings.TRIM skips it.
"""
import math
from pathlib import Path

import bmesh
import bpy

from lib import lighting, materials as M, mouldings as mo, props as P, shell

ROOM = 'stairs'
ART = Path(__file__).resolve().parents[1] / 'textures' / 'art' / ROOM

# Eye-height views matched to the reference frames of spec/rooms/stairs.md section 9 (hall-local
# camera positions moved with the reconciled newel: local y + 2.33 at the foot).
CAMERAS = [
    dict(name='foot', pos=(0.08, 4.03, 0.9), look=(0.45, 7.0, 0.7), fov_deg=100, ref='f_0243'),
    dict(name='nib', pos=(0.35, 5.2, 1.5), look=(0.85, 4.83, 1.0), fov_deg=100, ref='f_0779'),
    dict(name='prints', pos=(0.3, 4.63, 1.5), look=(0.8, 6.5, 2.7), fov_deg=100, ref='f_0247'),
    dict(name='bullnose', pos=(0.0, 4.63, 1.6), look=(0.45, 6.0, 0.7), fov_deg=100, ref='f_0249'),
    dict(name='hall', pos=(-0.1, 3.2, 1.6), look=(0.2, 6.5, 1.0), fov_deg=100, ref='f_0064'),
    dict(name='spandrel', pos=(-0.5, 7.0, 1.45), look=(0.25, 6.75, 2.2), fov_deg=100, ref='f_0774'),
    dict(name='balustrade', pos=(-0.15, 6.5, 1.5), look=(-0.15, 3.0, 1.4), fov_deg=100, ref='f_0777'),
    dict(name='lobby', pos=(-0.2, 8.6, 1.5), look=(0.3, 6.5, 2.2), fov_deg=100, ref='f_0753'),
]

WHITE = 'joinery_white'
NOSE = 0.025                   # carpet nosing overhang
X_WALL, X_OPEN = 0.99, 0.15     # staircase wall face / spandrel plane (west edge of the recess)
XE = X_WALL - 0.015             # carpet runs into the 30 mm wall string
XS = X_OPEN - 0.006             # face of the cut string, 6 mm proud of the spandrel panelling
XC = 0.205                      # west edge of the carpet = inside of the white tread ends
X_RAIL = 0.18                   # handrail / spindle centre line
RAIL_H, DADO_H, STRING_H, PRINT_H = 0.90, 0.965, 0.10, 1.45     # vertical heights above the nosing line
NEWEL_S = 0.115                 # newel stock (see build(): scaled from the frames, not the spec's 95 mm)


def _arc(p0, p1, bow, n):
    """Quadratic curve p0 -> p1 in plan whose middle is pushed `bow` towards -Y."""
    c = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 - 2 * bow)
    return [((1 - t) ** 2 * p0[0] + 2 * t * (1 - t) * c[0] + t * t * p1[0],
             (1 - t) ** 2 * p0[1] + 2 * t * (1 - t) * c[1] + t * t * p1[1]) for t in (i / n for i in range(n + 1))]


def _carpet_profile(h):
    """Riser face + carpet wrapped over a rounded nosing: (d out from the riser line, height)."""
    return [(0, 0), (0, h - 0.050), (0.008, h - 0.044), (0.018, h - 0.034), (0.024, h - 0.022), (0.025, h - 0.012),
            (0.021, h - 0.004), (0.012, h), (0, h)]


def _step(mb, front, back, z0, h, mat):
    """One carpeted step: riser + nosing swept along `front` (plan polyline, east -> west) and the tread
    back to `back` (west -> east, the next riser line)."""
    mb.sweep(_carpet_profile(h), [(x, y, z0) for x, y in front], mat)
    mb.face([(x, y, z0 + h) for x, y in front + back], mat, hint=(0, 0, 1))


def _carpet_mat():
    """Pale silver plush pile (stills t=241.5 / 244.0 / 249.0): module-local because the library's
    carpet_mink renders ~25 % too dark and too yellow.  Colour (brushed light / dark patches) and a fine
    pile normal come from stairs_art.py; same node layout as lib.materials (glTF-safe)."""
    m = M.image_mat('carpet_silver', str(ART / 'carpet_silver_col.jpg'), size_m=(1.2, 1.2), roughness=1.0)
    bsdf = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    if not bsdf.inputs['Normal'].is_linked:
        tex = m.node_tree.nodes.new('ShaderNodeTexImage')
        tex.image = bpy.data.images.load(str(ART / 'carpet_silver_nrm.jpg'), check_existing=True)
        tex.image.colorspace_settings.name = 'Non-Color'
        nm = m.node_tree.nodes.new('ShaderNodeNormalMap')
        m.node_tree.links.new(tex.outputs['Color'], nm.inputs['Color'])
        m.node_tree.links.new(nm.outputs['Normal'], bsdf.inputs['Normal'])
        bsdf.inputs['Sheen Weight'].default_value = 0.3             # pile -> KHR_materials_sheen
        bsdf.inputs['Sheen Roughness'].default_value = 0.45
    return m


def _wood():
    """Near-black gloss mahogany of the newel and handrail: the shaft samples (56, 46, 38) against a white
    wall at (191, 188, 181) in still t=241.5, where the library's mahogany_dark renders much redder."""
    return M.solid('stairs_mahogany', '#2E211C', 0.14)


def _square(ob, half, ease=0.02):
    """Clamp a lathed mesh to square stock of half-width `half`: wherever the profile radius exceeds the
    square it becomes the square block, and where it dips back inside, the flats end in the curved /
    pointed stops of a real turning - blocks, stops and turning are one closed mesh.  ease pulls the
    four arrises in a little (no razor edges).  Needs lathe vertices on the diagonals (segs % 8 == 0)."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    for v in bm.verts:
        x, y = v.co.x, v.co.y
        m = max(abs(x), abs(y))
        if m > half:
            k = half / m * ((1 - ease) if abs(abs(x) - abs(y)) < 1e-6 else 1)
            v.co.x, v.co.y = x * k, y * k
    bm.normal_update()
    for e in bm.edges:                                               # MB.finish marked them on the round lathe
        if len(e.link_faces) == 2:
            e.smooth = e.calc_face_angle() < math.radians(30)
    bm.to_mesh(ob.data)
    bm.free()
    return ob


def _drop_faces(name, box):
    """Delete the faces of a shell trim object lying wholly inside the plan box (x0, x1, y0, y1)."""
    ob = bpy.data.objects.get(name)
    if ob is None:                                                   # built without the shell stage
        return
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    dead = [f for f in bm.faces if all(box[0] <= v.co.x <= box[1] and box[2] <= v.co.y <= box[3] for v in f.verts)]
    bmesh.ops.delete(bm, geom=dead, context='FACES')
    bm.to_mesh(ob.data)
    bm.free()


# timber tread end: 30 mm rounded nosing over a 20 mm scotia, (d out from the string face, h from the tread top)
TREAD_END = [(0, -0.052), (0.006, -0.052), (0.006, -0.048), (0.008, -0.040), (0.012, -0.034), (0.018, -0.031),
             (0.020, -0.030), (0.026, -0.027), (0.030, -0.015), (0.027, -0.004), (0.021, 0), (0, 0)]
# planted panel moulding, 30 wide x 12 proud, swept in the spandrel plane
PANEL_MOULD = [(0.015, 0), (0.015, 0.004), (0.011, 0.009), (0.005, 0.012), (-0.003, 0.012), (-0.008, 0.008),
               (-0.012, 0.006), (-0.015, 0.003), (-0.015, 0)]
# wall string: 30 mm board, beaded top edge, (d from the wall, h from its top line); reaches just under the
# riser feet (nosing line - 0.21) and no lower, or it would show beneath the overhead cupboard in the lobby
WALL_STRING = ([(0.030, -0.315), (0.030, -0.030), (0.027, -0.026), (0.027, -0.021)]
               + mo._half((0.027, -0.021), (0.027, -0.006), 4) + [(0.024, -0.003), (0.024, 0), (0, 0)])
# hall dado rail turned into the wall plane: (d down from the rail top, h off the wall) for up = wall normal
DADO = [(0.070 - h, p) for p, h in mo.PROFILES['dado_hall']]


def _handrail(k):
    """65 x 55 toad's-back rail; heights stretched by k because the sweep cuts it plumb on the rake."""
    half = [(0.027, 0), (0.027, 0.006), (0.0325, 0.010), (0.0325, 0.020), (0.029, 0.024), (0.030, 0.034),
            (0.026, 0.044), (0.016, 0.052), (0, 0.055)]
    pts = [(-0.027, 0)] + half + [(-d, h) for d, h in half[-2::-1]] + [(-0.027, 0)]
    return [(d, h * k) for d, h in pts]


def _stop(h, z_tip, H, segs):
    """Lathe profile [(r, z)] of a stop on square stock of half-width h, from the tip of the flat's tongue
    (r = h, z_tip) to the arris (r = h * sqrt 2, z_tip + H); H < 0 = tongue pointing up.  One point per
    lathe column of a face, so after _square the rounded end of each flat runs along mesh edges."""
    return [(h / math.cos(a), z_tip + H * (1 - math.sqrt(max(0.0, 1 - math.tan(a) ** 2))))
            for a in (2 * math.pi * i / segs for i in range(segs // 8 + 1))]


def _bead(z, r, s, neck=11.5):
    """Crisp 14 mm bead of radius r (mm on 32 mm stock, scale s) starting at height z."""
    return [(neck * s, z + .001), ((r - 1.5) * s, z + .004), (r * s, z + .0075), ((r - 1.5) * s, z + .011),
            (neck * s, z + .014)]


def _spindle(name, height, base, top=0.15, w=0.045):
    """Square white baluster (stills t=776.5 / 777.0): base block, four-sided chamfer stop, collar bead,
    long vase, cluster of three beads at mid height, slender taper, collar bead, chamfer stop, top block.
    One lathe clamped to the square stock (_square); radii in mm on 32 mm stock."""
    s, t0, t1 = w / 32, base, height - top
    L, R = t1 - t0, 26 * w / 32
    zc = t0 + 0.5 * L
    # four-sided chamfer stop: a cone with points on the radii of the 16-segment columns (pointed flats)
    cone = lambda z, sg: [(22.627 * s, z), (17.318 * s, z + sg * .0132), (16 * s, z + sg * .0165), (13 * s, z + sg * .024)]
    p = [(0, 0), (R, 0), (R, t0 - .001)] + cone(t0, 1) + [(11 * s, t0 + .030)]
    p += _bead(t0 + .031, 16, s)
    p += [(11 * s, t0 + .047), (12.5 * s, t0 + .056), (14.5 * s, t0 + .10), (15.5 * s, t0 + .22 * L),
          (15.5 * s, t0 + .30 * L), (14 * s, t0 + .40 * L), (12 * s, zc - .040), (11 * s, zc - .030)]
    p += _bead(zc - .0225, 15, s) + _bead(zc - .0075, 16, s) + _bead(zc + .0075, 15, s)
    p += [(11 * s, zc + .024), (12 * s, zc + .034), (13.5 * s, t0 + .68 * L), (12.5 * s, t0 + .82 * L),
          (11 * s, t1 - .050)]
    p += _bead(t1 - .047, 16, s)
    p += [(11 * s, t1 - .030)] + cone(t1, -1)[::-1] + [(R, t1 + .001), (R, height), (0, height)]
    mb = mo.MB()
    mb.lathe(p, WHITE, segs=16)
    return _square(mb.finish(name), w / 2)


def _newel():
    """Mahogany newel, 1.75 m on 115 mm stock (stills t=241.5 / 249.0 / 777.0).  Bottom to top: square
    shaft with rounded stops, base ring, cup, fat vase tapering up to a slim neck, bold double ring at
    three-quarters height, short upper bulb, two rings, square block with rounded (lamb's-tongue) stops,
    collar, flattened ball with an incised groove.  One closed lathe clamped to the stock.  Origin floor."""
    h = NEWEL_S / 2
    R = 0.09                                                         # > arris radius h * sqrt 2 = full square
    p = [(0, 0), (R, 0), (R, .848)] + _stop(h, .885, -.035, 32)[::-1] + [
         (.056, .887), (.057, .891), (.056, .896), (.050, .900), (.037, .903), (.035, .908),          # base ring
         (.037, .916), (.043, .930), (.049, .948), (.052, .962), (.052, .972), (.049, .979),          # cup
         (.036, .983), (.034, .990),
         (.038, 1.000), (.047, 1.020), (.053, 1.045), (.055, 1.065), (.053, 1.090), (.047, 1.125),    # vase
         (.040, 1.160), (.034, 1.188), (.032, 1.198),
         (.036, 1.202), (.047, 1.206), (.050, 1.212), (.047, 1.218), (.043, 1.220), (.046, 1.223),    # double ring
         (.048, 1.228), (.045, 1.233), (.036, 1.236),
         (.034, 1.242), (.040, 1.252), (.047, 1.266), (.050, 1.280), (.049, 1.295), (.044, 1.310),    # upper bulb
         (.036, 1.320), (.033, 1.326),
         (.036, 1.331), (.046, 1.335), (.049, 1.342), (.046, 1.349), (.040, 1.352), (.044, 1.356),    # two rings
         (.047, 1.362), (.044, 1.368), (.038, 1.371), (.037, 1.378), (.042, 1.386)]
    p += _stop(h, 1.395, .040, 32) + [(R, 1.437), (R, 1.534)] + _stop(h, 1.561, -.025, 32)[::-1]     # block
    p += [(.052, 1.566), (.053, 1.574), (.050, 1.582), (.040, 1.588), (.033, 1.594), (.031, 1.604), (.035, 1.614),    # collar
         (.036, 1.628)]
    ball = lambda a: (0.0575 * math.cos(math.radians(a)), 1.685 + 0.067 * math.sin(math.radians(a)))
    p += [ball(a) for a in (-50, -37.5, -25, -12.5, 0, 12.5, 25)]
    p += [ball(28), (ball(30)[0] - .003, ball(30)[1]), ball(32)]     # incised groove round the upper third
    p += [ball(a) for a in (37.5, 50, 62.5, 75, 84)] + [(0, 1.752)]
    mb = mo.MB()
    mb.lathe(p, _wood(), segs=32)
    return _square(mb.finish('stairs.newel'), h)


def build(ctx):
    S = ctx.stairs
    rise, going, r4 = S['rise'], S['going'], S['firstStraightRiserY']
    nx, ny = S['newel']
    lz = S['landing']['z']
    yl1 = max(p[1] for p in S['landing']['polygon'])                 # 8.73 wall facing the top of the flight
    ys = [p[1] for p in ctx.room_poly(ROOM)]
    y_nib, y_post = min(ys), max(ys) + 0.005                         # nib return face 4.83 / corner post 7.585
    x_bulk = X_OPEN + 0.06                                           # bulkhead face beside steps 13-15 (shell)
    slope = rise / going
    k = math.hypot(1, slope)                                         # plumb height of 1 m measured square to the rake
    R = lambda n: r4 + going * (n - 4)                               # riser line of step n (straight flight)
    NL = lambda y: rise * (4 + (y + NOSE - r4) / going)              # nosing line
    inv = lambda z: r4 - NOSE + going * (z / rise - 4)               # y where the nosing line is at z
    y_newel = ny + NEWEL_S / 2                                       # north face of the newel
    last = max(n for n in range(3, S['risers']) if R(n) < y_post - 0.05)     # last tread with an open end (12)

    # ---- carpet: treads, risers, bullnose, landing ------------------------------------------------
    lower, upper, carpet = mo.MB(), mo.MB(), _carpet_mat()
    # Bullnose: quarter ellipse from the nib return, bulging ~55 mm west of the newel base (still t=776.5),
    # then a tight return onto the newel's west face.
    xn = nx - NEWEL_S / 2                                            # west face of the newel
    ax, ay, rr = 0.65 - (xn - 0.0325), ny - y_nib - 0.03, 0.0325
    r1 = [(0.65 + ax * math.cos(t), ny + ay * math.sin(t)) for t in (math.radians(-90 - 7.5 * i) for i in range(13))]
    r1 += [(xn - rr * math.cos(a), ny + rr * math.sin(a)) for a in (math.radians(d) for d in (30, 60, 90))]
    r1.append((xn + 0.012, ny + rr))
    r2 = _arc((XE, ny - 0.22), (nx + 0.05, ny - 0.03), 0.10, 8)
    _step(lower, r1, r2[::-1] + [(XE, y_nib + 0.015), (0.65, y_nib + 0.015)], 0, rise, carpet)
    _step(lower, r2, [(nx + 0.05, R(3)), (XE, R(3))], rise, rise, carpet)
    for n in range(3, last + 1):
        _step(lower, [(XE, R(n)), (XC, R(n))], [(XC, R(n + 1)), (XE, R(n + 1))], (n - 1) * rise, rise, carpet)
    # risers 14 and 15 stand on the planes of the cupboard carcass step and the landing slab: 4 mm proud
    xw, y14, y15 = x_bulk + 0.015, R(14) - 0.004, R(15) - 0.004
    _step(upper, [(XE, R(13)), (xw, R(13))], [(xw, y14), (XE, y14)], 12 * rise, rise, carpet)
    _step(upper, [(XE, y14), (xw, y14)], [(xw, y15), (XE, y15)], 13 * rise, rise, carpet)
    _step(upper, [(XE, y15), (xw, y15)], [(xw, yl1 - 0.015), (XE, yl1 - 0.015)], 14 * rise, lz - 14 * rise + 0.006,
          carpet)
    # Solid packing between the stepped top of the lobby cupboard carcass (shell: 2.40 / 2.59) and treads
    # 13 / 14: closes the 10 mm slit under the landing soffit seen from the lobby (north face 1 mm proud of
    # the carcass front) and the underside of these steps.
    cb = ctx.feature('lobby_overhead_cupboard')
    cy0, cy1 = min(p[1] for p in cb['polygon']), max(p[1] for p in cb['polygon'])        # 7.68 / 8.13
    pack = shell.material(shell.finish('hallway')['features']['lobby_overhead_cupboard'])
    upper.box((x_bulk + 0.001, cy0 - 0.005, 12 * rise + 0.11), (X_WALL - 0.001, y14, 13 * rise - 0.004), pack)
    upper.box((x_bulk + 0.001, y14 + 0.002, 13 * rise + 0.11), (X_WALL - 0.001, cy1 + 0.001, 14 * rise - 0.004), pack)
    flight, flight_up = lower.finish('stairs.flight'), upper.finish('stairs.flight_upper')

    # ---- open side: cut string, tread ends, spandrel panelling ------------------------------------
    sp = mo.MB()
    for n in range(3, last + 1):
        z, ya, yb = n * rise, R(n), min(R(n + 1), y_post)
        if n == 3:                                                   # starts behind the newel: side return only
            ya = y_newel - 0.005
            sp.sweep(TREAD_END, [(XS, ya, z), (XS, yb, z)], WHITE)
        else:                                                        # nosing mitred round the corner
            sp.sweep(TREAD_END, [(XC, ya, z), (XS, ya, z), (XS, yb, z)], WHITE)
            sp.face([(X_OPEN, ya, z - rise), (XC, ya, z - rise), (XC, ya, z - 0.052), (X_OPEN, ya, z - 0.052)],
                    WHITE, hint=(0, -1, 0))                          # riser end between string and carpet
        sp.face([(XC, ya, z), (XS, ya, z), (XS, yb, z), (XC, yb, z)], WHITE, hint=(0, 0, 1))
    saw = [(y_newel, 3 * rise - 0.02)]
    for n in range(4, last + 1):
        saw += [(R(n), (n - 1) * rise - 0.02), (R(n), n * rise - 0.02)]
    saw += [(y_post, last * rise - 0.02), (y_post, NL(y_post) - 0.28), (y_newel, NL(y_newel) - 0.28)]
    sp.prism([(XS, y, z) for y, z in saw], (X_OPEN - XS, 0, 0), WHITE, grain=1)       # the cut string board
    sp.face([(X_OPEN, y_newel, 0), (X_OPEN, y_post, 0), (X_OPEN, y_post, NL(y_post) - 0.26),
             (X_OPEN, y_newel, NL(y_newel) - 0.26)], WHITE, hint=(-1, 0, 0))          # flush panelling
    # planted raking bead under the string: the strong double shadow line of every spandrel still (plumb-cut ends)
    sp.sweep(PANEL_MOULD, [(X_OPEN - 0.0002, y, NL(y) - 0.28 - 0.016 * k) for y in (y_newel, y_post)], WHITE,
             up=(-1, 0, 0), ends=((0, 0, -k), (0, 0, -k)))
    # Panels as filmed (still t=776.0: three small raking-topped panels under treads 4-7, narrow stiles, bottom
    # mouldings 2 cm above the skirting): seven equal bays with 65 mm stiles; the first starts where its short
    # side is 45 mm between moulding centres (40 mm clear of the newel), the last ends 50 mm from the corner post.
    top = lambda y: NL(y) - 0.38                                     # raking top of the panels, 0.10 below the string
    nb, st, zp, m = 7, 0.065, 0.19, 0.015                            # bays, stile, underside of the panels, half moulding
    y0, y1 = inv(zp + m + 0.045 + 0.02 + 0.38) - m, y_post - 0.055
    pw = (y1 - y0 - st * (nb - 1)) / nb
    for b in range(nb):
        ya = y0 + (pw + st) * b + m
        yb = ya + pw - 2 * m
        sp.sweep(PANEL_MOULD, [(X_OPEN - 0.0002, y, z) for y, z in
                               ((ya, zp + m), (yb, zp + m), (yb, top(yb) - 0.02), (ya, top(ya) - 0.02))],
                 WHITE, closed=True, up=(-1, 0, 0))
    spandrel = sp.finish('stairs.spandrel')

    # ---- wall side: string easing down to the nib return, raking dado with its knee, landing trim --
    ws = mo.MB()
    z0, rad, th = 0.62, 0.6, math.atan(slope)                        # string top on the nib return; easing radius
    yc = inv(z0 - STRING_H) - rad * math.tan(th / 2)                 # the easing arc is level from here south
    a0 = math.asin(max(0.0, y_nib - yc) / rad)
    arc = [(yc + rad * math.sin(a), z0 + rad * (1 - math.cos(a))) for a in (a0 + (th - a0) * i / 7 for i in range(8))]
    arc[0] = (y_nib, arc[0][1])
    zs, y_top = lz + 0.17, inv(lz + 0.17 - STRING_H)                 # landing skirting height / where the rake reaches it
    ws.sweep(WALL_STRING, [(0.65, y_nib, arc[0][1])] + [(X_WALL, y, z) for y, z in arc]
             + [(X_WALL, y_top, zs), (X_WALL, yl1, zs), (x_bulk, yl1, zs), (x_bulk, y_top, zs),
                (x_bulk, y_post + 0.02, NL(y_post + 0.02) + STRING_H)], WHITE)
    # the board carries on down to the floor round the fanned bottom steps (1 mm behind the string face)
    ws.box((0.651, y_nib, 0), (X_WALL, y_nib + 0.029, 0.45), WHITE, grain=0)
    ws.box((X_WALL - 0.029, y_nib, 0), (X_WALL, R(4) - 0.10, 0.45), WHITE, grain=1)
    D = lambda y: NL(y) + DADO_H
    # Knee as filmed (see the module docstring): the shell's hall rail (0.965) stays up to the nib's outer corner;
    # from its mitre there a raking piece climbs across the nib return (0.27 in 0.34 m, ~38 deg) to the short
    # level lead-in on the staircase wall, then the rake.  The lead-in's top measures 1.15-1.24 in the stills,
    # hence 0.15 long (1.23) rather than 0.20 (1.28).
    yk, y_l, zd = y_nib + 0.15, inv(lz), lz + DADO_H                 # end of the level lead-in; top of the rake
    zk, zh = D(yk), shell.finish('hallway')['dado']                  # rail tops: lead-in / hall
    ph = mo.profile_size('dado_hall')[1]
    _drop_faces('hallway.dado', (0.61, 1.00, y_nib - 0.001, y_nib + 0.07))       # the shell's level leg on the nib return
    ws.sweep(mo.PROFILES['dado_hall'], [(0.65, y_nib, zh - ph), (X_WALL, y_nib, zk - ph)], WHITE,
             ends=((-1, 1, 0), (-1, 1, 0)))                          # plumb-cut raking rail, plan mitres at both corners
    ws.sweep(DADO, [(X_WALL, y_nib, zk), (X_WALL, yk, zk), (X_WALL, y_l, zd), (X_WALL, yl1, zd)], WHITE, up=(-1, 0, 0))
    ws.sweep(DADO, [(X_WALL, yl1, zd), (x_bulk, yl1, zd)], WHITE, up=(0, -1, 0))
    px = X_OPEN - 0.05                                               # moulded block on the corner post (3 open sides)
    ws.sweep(mo.PROFILES['ped_cap'], [(X_OPEN, y_post - 0.005, 2.28), (px, y_post - 0.005, 2.28),
                                      (px, y_post + 0.095, 2.28), (X_OPEN + 0.05, y_post + 0.095, 2.28)], WHITE)
    wall_string = ws.finish('stairs.wall_string')

    gb, grey, e = mo.MB(), M.paint(M.PAINT['hall_dado_grey']), 0.0015        # grey band, 1.5 mm proud of the plaster
    band = arc + [(y_top, zs), (yl1, zs), (yl1, zd), (y_l, zd), (yk, zk), (y_nib, zk)]
    gb.face([(X_WALL - e, y, z - 0.03) for y, z in band], grey, hint=(-1, 0, 0))
    gb.face([(x, y_nib + e, z) for x, z in ((0.65, z0 - 0.03), (X_WALL, z0 - 0.03), (X_WALL, zk - 0.03),
                                            (0.65, zh - 0.03))], grey, hint=(0, 1, 0))      # trapezoid under the climbing rail
    gb.face([(x, yl1 - e, z) for x, z in ((X_WALL, zs - 0.03), (x_bulk, zs - 0.03), (x_bulk, zd - 0.03),
                                          (X_WALL, zd - 0.03))], grey, hint=(0, -1, 0))
    band_ob = gb.finish('stairs.dado_band')

    # ---- balustrade ---------------------------------------------------------------------------------
    # Newel 1.75 m on 115 mm stock, not the spec's 1.45 / 95: in f_0064, f_0241 and f_0777 its ball lines
    # up with nosings 10-12 and it is ~8.5 risers tall in hr_243; the rail (0.90 above the nosing line)
    # then lands on the square block as filmed.
    newel = _newel()
    newel.location = (nx, ny, 0)
    U = lambda y: NL(y) + RAIL_H - 0.055 * k                         # underside of the handrail
    hz = ctx.ceil_z('hallway')
    ya, yb = y_newel - 0.005, inv(hz - RAIL_H + 0.055 * k) + 0.01    # dies into the soffit of the well edge
    yc, prof = inv(hz - RAIL_H + 0.018 * k), _handrail(k)            # from here its side beads are above the ceiling
    hb = mo.MB()
    hb.sweep(prof, [(X_RAIL, ya, U(ya)), (X_RAIL, yc, U(yc))], _wood())
    # the last 7 cm are buried in the well wall (face x = 0.21): east side trimmed so no fin shows inside the well
    hb.sweep([(max(d, -0.029), h) for d, h in prof], [(X_RAIL, yc, U(yc)), (X_RAIL, yb, U(yb))], _wood())
    rail = hb.finish('stairs.handrail')
    spindles = []
    SP = (0.045, 0.16)                                               # two per tread at 0.115 centres (f_0777)
    heights = [U(R(4) + dy) - 4 * rise + 0.02 for dy in SP]         # tops let into the rail
    protos = [_spindle(f'stairs.spindle.{i}', h, base) for i, (h, base) in enumerate(zip(heights, (0.20, 0.295)))]
    for n in range(3, last + 1):
        for dy, proto in zip(SP, protos):
            if R(n) + dy < y_post - 0.03:
                ob = bpy.data.objects.new(f'stairs.spindle.{len(spindles):02d}', proto.data)     # shared mesh
                ob.location = (X_RAIL, R(n) + dy, n * rise)
                spindles.append(ob)

    # ---- tagging: the flight in the recess is the plan symbol; steps 13-15 hang over the lobby --------
    for ob in protos:
        bpy.data.objects.remove(ob)
    for ob in (spandrel, newel, rail, *spindles):
        ob.parent = flight
    ctx.add(flight, ROOM, 'fit', plan_sym='stair')
    ctx.add(spandrel, ROOM, 'joinery')
    for ob in (newel, rail, *spindles):
        ctx.add(ob, ROOM, 'joinery', lm='dynamic')
    ctx.add(flight_up, ROOM, 'fit')
    ctx.add(wall_string, ROOM, 'trim')
    ctx.add(band_ob, ROOM, 'trim')

    # ---- hall ceiling carried over the stair foot (stills t=244.0-246.0, f_0247) ---------------------------
    # The well's south edge crosses the flight on the riser-4 line, not at the nib as house.json has it: slab
    # 1 mm under the shell's ceiling plane, a plain upstand closing the shaft above its edge, and the hall
    # cornice continued from the nib return along the staircase wall up to that edge.
    hc, y_edge, f = ctx.ceil_z('hallway') - 0.001, r4 - 0.02, shell.finish(ROOM)
    slab = shell.box('stairs.foot_ceiling', X_OPEN, X_WALL, y_nib, y_edge, hc, hc + 0.12, f['ceiling'])
    slab['part'] = 'ceiling'                                         # hidden with the other ceilings in plan views
    up = shell.box('stairs.well_upstand', x_bulk, X_WALL, y_edge - 0.06, y_edge, hc + 0.12, ctx.ceil_z(ROOM), f['upper'])
    for ob in (slab, up):
        ctx.add(ob, ROOM, 'shell')
    cm, B = mo.MB(), mo.HALL_BAND
    y_clear = y_nib + B['d'] + B['proj'] + 0.01                      # modillions start clear of the nib-return cornice
    cm.sweep(mo.PROFILES['cornice_hall'], [(X_WALL, y_nib, hc), (X_WALL, y_clear, hc)], 'plaster_white', caps=False)
    mo.cornice(cm, 'cornice_hall', [(X_WALL, y_clear, hc), (X_WALL, y_edge - 0.01, hc)])
    ctx.add(cm.finish('stairs.foot_cornice'), ROOM, 'trim')

    # ---- four prints stepping up the staircase wall (stills t=245.5 / 778.0) ------------------------------
    # S1: landscape wash in a wide cream mount and an ornate olive frame.  Filmed on a splayed face at the stair
    # foot that house.json does not have (its nib return is 0.34 m, narrower than the print), so it hangs on
    # the staircase wall hard against the nib corner.  S2-S4: flat olive frames, pale paper filling the sight.
    for i in range(4):
        img, name = str(ART / f'print_{i + 1}.jpg'), f'stairs.print.{i + 1}'
        if i == 0:
            y = y_nib + 0.03 + 0.23
            pic = P.framed_picture(image=img, w=0.46, h=0.40, frame_style='gilt_swept', frame_w=0.045, mount=0.06,
                                   glass=True, name=name)
            for sl in pic.material_slots:                            # dull olive-bronze, not gilt (props has no
                if sl.material == P.mat('gold_antique'):             # frame colour argument)
                    sl.material = P.mat('olive_bronze')
        else:
            y = ny - 0.20 + 0.70 * i
            pic = P.framed_picture(image=img, w=0.34, h=0.46, frame_style='olive_bronze', glass=True, name=name)
        P.place(pic, (X_WALL, y, NL(y) + PRINT_H), facing=(-1, 0))
        ctx.add(pic, ROOM, 'decor')

    # ---- light: one recessed downlight in the stairwell cap above the landing nosing (spec section 7) ---
    for i, (ly, watts) in enumerate(((R(15) - 0.03, 60), (R(7), 350))):
        lighting.downlight(ctx, ROOM, 0.57, ly, watts=watts, spot_deg=150, name=f'stairs.downlight.{i}')
        ctx.add(P.place(P.downlight(name=f'stairs.downlight_trim.{i}'), (0.57, ly, ctx.ceil_z(ROOM))), ROOM, 'light')

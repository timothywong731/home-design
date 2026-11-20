"""First-floor landings: landing1_front, landing1_ql, landing1_rear (spec/rooms/landing1.md).

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --levels 1 --only shell,landing1_front,landing1_ql,landing1_rear \
        --preview landing1_front,landing1_ql,landing1_rear --res 540x960 --samples 64 --tag landing1

Adds to the shell: the six "hallway" downlights and their four switch plates, sockets, thermostat, ceiling
plate and smoke alarm, the column radiator, paintings W1-W5 and P4 (crops: landing1_art.py), the raking dado /
skirting and carpet nosings of the split-level steps, and the top newel of the main flight (0.20, 8.13).
The strip balustrade on v_strip_well (rail, capping, fascia, spindles) belongs to rooms/stairs2.py (MULTILEVEL.md 1):
its level rail (top Z 4.32) enters this newel's block.  The main-flight rail (rooms/stairs.py) dies into the strip
fascia short of the newel (v6 f_0038), so the shaft takes no rail.

Deviation from the spec text (v3 f_0075, f_0496-0500): the dado and skirting rake over the two steps at the
stair pitch (0.19 / 0.25, 37 degrees) through the nosings, so the rake runs from riser B (y 7.88) to y 8.38,
0.25 north of riser A, not between the two riser lines (that would be 56 degrees).
"""
import math
from pathlib import Path

from mathutils import Matrix

from lib import interact as IX, lighting, materials as M, mouldings as mo, props as P, shell

ART = Path(__file__).resolve().parents[1] / 'textures' / 'art'
F, Q, R = 'landing1_front', 'landing1_ql', 'landing1_rear'
XW, XPIER = -0.65, -0.55            # west (party) wall face; face of the pier y 8.53..9.95
WEST, EAST, NORTH = (1, 0), (-1, 0), (0, 1)      # room-side normals of the west / east / south walls
WHITE = 'joinery_white'
Y_B, Y_A, PITCH = 7.88, 8.13, 0.19 / 0.25    # riser B (upper), riser A (lower) of the two steps; their pitch
LANDING = [F, Q, R, 'stairs']      # L1-L6 also light the main staircase, and its downlight is on this circuit
#                                    (landing1.md 8.2 S-stair; the hall plate's left gang, rooms/hallway.py, same list)
UPSTAIRS = ['landing2_head', 'landing2_platform', 'stairs2']     # what rooms/landing2.py's own switches light

# world coords; fov spans the longer side
CAMERAS = [
    dict(name='corridor', pos=(-0.15, 9.05, 4.5), look=(-0.2, 11.8, 4.2), fov_deg=100, ref='v3 f_0054'),
    dict(name='steps', pos=(-0.2, 9.0, 4.5), look=(-0.25, 6.0, 4.0), fov_deg=100, ref='v3 f_0075'),
    dict(name='front', pos=(-0.2, 6.5, 4.95), look=(0.3, 4.95, 4.5), fov_deg=100, ref='v3 f_0507'),
    dict(name='north', pos=(-0.3, 7.3, 4.95), look=(-0.2, 11.0, 4.2), fov_deg=100, ref='v6 f_0026'),
    dict(name='fromarch', pos=(-0.2, 11.0, 4.5), look=(-0.2, 8.0, 4.2), fov_deg=100, ref='v3 f_0490'),
    dict(name='ql', pos=(0.6, 7.75, 4.1), look=(0.45, 8.6, 2.9), fov_deg=100, ref='v3 f_0037'),
    dict(name='p4', pos=(-0.35, 8.9, 4.55), look=(0.99, 8.4, 4.5), fov_deg=100, ref='v3 f_0039'),
    dict(name='bay', pos=(-0.15, 10.3, 4.5), look=(-0.1, 12.4, 4.5), fov_deg=100, ref='v3 f_0148'),
    dict(name='balustrade', pos=(-0.5, 6.9, 4.95), look=(0.15, 7.7, 4.0), fov_deg=100, ref='v4 f_0183'),
    dict(name='westwall', pos=(0.15, 9.5, 4.55), look=(-0.65, 10.3, 4.45), fov_deg=100, ref='v3 f_0051'),
    dict(name='switches', pos=(-0.35, 6.3, 4.95), look=(0.8, 4.95, 4.6), fov_deg=100, ref='v4 f_0306'),
    dict(name='frontwest', pos=(0.75, 5.6, 4.9), look=(-0.65, 6.2, 4.7), fov_deg=100, ref='v4 f_0168'),
    dict(name='rake', pos=(0.05, 8.75, 4.35), look=(-0.65, 7.95, 3.85), fov_deg=100, ref='v3 f_0075'),
    dict(name='plates', pos=(0.70, 5.40, 4.74), look=(0.77, 4.95, 4.55), fov_deg=70, ref='v4 f_0310'),
    dict(name='spindles', pos=(-0.40, 7.50, 4.35), look=(0.18, 7.80, 3.95), fov_deg=80, ref='v4 f_0187'),
    dict(name='baysw', pos=(-0.45, 11.75, 4.5), look=(0.40, 12.0, 4.3), fov_deg=100, ref='v3 f_0150'),
    dict(name='nosing', pos=(0.0, 8.95, 4.45), look=(-0.45, 7.95, 3.30), fov_deg=75, ref='v3 f_0497'),
]


def _wood():
    """Dark gloss mahogany of newels and handrails: the same named solid as the main flight (rooms/stairs.py);
    the library's `mahogany` renders far redder than the chocolate brown of v3 f_0075 / v4 f_0183."""
    return M.solid('stairs_mahogany', '#2E211C', 0.14)


def _plate(name, rockers, body=True):
    """White 86 x 86 switch plate (wall prop frame: back on y = 0, front -Y) with rockers [(local x, width)].
    body=False gives the rockers alone: a 2-gang plate is the body + one rocker, and the other rocker as its own
    object, so each gang switches its own circuit."""
    mb = mo.MB()
    if body:
        mb.box((-0.043, -0.009, -0.043), (0.043, 0, 0.043), 'plastic_white', bev=0.0015)
    for xc, w in rockers:
        mb.box((xc - w / 2, -0.0125, -0.017), (xc + w / 2, -0.008, 0.017), 'plastic_white', bev=0.001)
    return mb.finish(name)


def _thermostat(name):
    mb = mo.MB()
    mb.box((-0.045, -0.025, -0.06), (0.045, 0, 0.06), 'plastic_white', bev=0.005)
    mb.box((-0.028, -0.0256, 0.012), (0.028, -0.024, 0.040), M.solid('lcd_blank', '#B4BAAE', 0.3))      # blank display
    return mb.finish(name)


def _radiator(name, n=16, pitch=0.045, h=0.57):
    """White column radiator: n oval tubes with domed ends on two header bars, TRV at the +X end (north on the
    west wall: v3 f_0141), lockshield at the -X end, chrome tails to the floor 0.13 below.  Tube fronts 0.115 off
    the wall, just proud of the pier (v3 f_0054).  Wall prop frame, origin = bottom centre on the wall."""
    mb, yc = mo.MB(), -0.081
    prof = [(0, 0), (0.010, 0.004), (0.017, 0.014), (0.019, 0.032), (0.019, h - 0.032), (0.017, h - 0.014),
            (0.010, h - 0.004), (0, h)]
    for i in range(n):
        mb.at(Matrix.Translation(((i - (n - 1) / 2) * pitch, yc, 0)))
        mb.lathe(prof, 'white_gloss', segs=10, ell=(1.0, 1.8))
    mb.at()
    half = n * pitch / 2
    for z in (0.045, h - 0.045):
        mb.tube([(-half + 0.02, yc, z), (half - 0.02, yc, z)], 0.013, 'white_gloss', n=6)
    for sx, head in ((1, True), (-1, False)):
        x = sx * (half + 0.035)
        mb.tube([(sx * (half - 0.02), yc, 0.045), (x, yc, 0.045)], 0.009, 'chrome', n=6)
        mb.tube([(x, yc, -0.13), (x, yc, 0.06)], 0.0075, 'chrome', n=6)
        mb.at(Matrix.Translation((x, yc, 0.06)))
        if head:
            mb.lathe([(0, 0), (0.016, 0), (0.021, 0.008), (0.021, 0.050), (0.017, 0.058), (0, 0.058)], 'white_gloss', segs=10)
        else:
            mb.lathe([(0, 0), (0.011, 0), (0.011, 0.022), (0, 0.024)], 'chrome', segs=8)
        mb.at()
    return mb.finish(name)


def _newel(name, z_top_block=4.34):
    """Top newel of the main flight, square mahogany (v4 f_0181-0186): foot on the main-flight string below the
    quarter landing, chamfered shaft, block for the level strip rail of rooms/stairs2.py (top Z 4.32), collar and
    flattened ball, top Z 4.475.  Local z = world Z."""
    mb, m = mo.MB(), _wood()
    mb.box((-0.0475, -0.0475, 2.66), (0.0475, 0.0475, 3.44), m, bev=0.004)
    mb.box((-0.040, -0.040, 3.43), (0.040, 0.040, z_top_block - 0.19), m, bev=0.010)
    mb.box((-0.0475, -0.0475, z_top_block - 0.20), (0.0475, 0.0475, z_top_block), m, bev=0.006)
    z = z_top_block
    ball = [(0.047 * math.cos(a), z + 0.092 + 0.043 * math.sin(a)) for a in (math.radians(d) for d in range(-60, 91, 15))]
    mb.lathe([(0, z - 0.01), (0.040, z - 0.01), (0.040, z + 0.004), (0.030, z + 0.012), (0.024, z + 0.024),
              (0.033, z + 0.030), (0.033, z + 0.038), (0.022, z + 0.046)] + ball, m, segs=20)
    return mb.finish(name)


def _steps(ctx):
    """Split-level steps on the west wall: dado and skirting rake at the pitch of the two steps through their
    nosings (riser B y 7.88 -> y 8.38), the skirting board filled down to the treads, the paint split moved onto
    the rake, rounded carpet nosings on the risers.  1 mm proud of the wall so it wins over the shell's level trim where
    that still overlaps (requested: front trim to stop at y 7.88, rear trim to start at y 8.38)."""
    zf, zr = ctx.floor_z(F), ctx.floor_z(R)
    y_l = Y_B + (zf - zr) / PITCH                             # 8.38: where the rake lands on the corridor level
    zn = lambda y: zf - PITCH * (y - Y_B)                     # nosing line
    top, dh = shell.finish(F)['dado'], mo.profile_size('dado_landing')[1]
    x, mb = XW + 0.001, mo.MB()
    mb.sweep(mo.PROFILES['dado_landing'], [(x, y_l, zr + top - dh), (x, Y_B, zf + top - dh)], WHITE)
    mb.sweep(mo.PROFILES['sk_hall'], [(x, y_l, zr), (x, Y_B, zf)], WHITE)
    za = zn(Y_A)
    for tri in ([(x, Y_B, zf), (x, Y_B, za), (x, Y_A, za)], [(x, Y_A, za), (x, Y_A, zr), (x, y_l, zr)]):
        mb.prism(tri, (0.018, 0, 0), WHITE)                   # board down to the tread and to the corridor floor
    ctx.add(mb.finish(F + '.rake_trim'), F, 'trim')
    # paint split on the rake: white over the shell's grey above it (front walls), grey over its white below it
    split, e = shell.split_z(F), XW + 0.0015
    fin = shell.finish(F)
    for room, pts, spec in ((F, [(Y_B, zf + split), (Y_A, zf + split), (Y_A, za + split)], fin['upper']),
                            (R, [(Y_A, zr + split), (Y_A, za + split), (y_l, zr + split)], fin['lower'])):
        ob = shell.faces_object(f'{room}.rake_paint', [([(e, y, z) for y, z in pts], (0, 8.1, 4.2), spec)])
        ctx.add(ob, room, 'trim')

    # carpet bullnose on each riser line (plush pile rolls over: v3 f_0075, f_0496-0501): 25 mm overhang, 45 mm
    # down the riser, top flush with the upper tread.  Profile (d out from the riser, h from the tread), CCW.
    arc = lambda cx, cz, r, a0, a1: [(cx + r * math.cos(math.radians(a)), cz + r * math.sin(math.radians(a)))
                                     for a in range(a0, a1 + 1, 30)]
    nose = [(0, -0.045)] + arc(0.017, -0.037, 0.008, -90, 0) + arc(0.013, -0.012, 0.012, 0, 90) + [(0, 0)]
    for name, room, z, path in (                              # sweep d is LEFT of travel = over the lower floor
            ('nosing.b', F, zf, [(XW, Y_B), (0.15, Y_B)]),
            ('nosing.a', F, za, [(XW, Y_A), (0.15, Y_A)]),
            ('nosing.ql', R, zr, [(0.35, 8.73), (0.15, 8.73), (0.15, 8.13 + 0.0475)])):   # L round the QL corner
        mb = mo.MB()
        mb.sweep(nose, [(x, y, z) for x, y in path], 'carpet_silver_beige')
        ctx.add(mb.finish(f'{room}.{name}'), room, 'fit')


def build(ctx):
    zf, zq, zr = ctx.floor_z(F), ctx.floor_z(Q), ctx.floor_z(R)

    def put(ob, loc, facing, room, kind='fit', **kw):
        return ctx.add(P.place(ob, loc, facing=facing), room, kind, **kw)

    # ---- lights: six recessed downlights, one circuit ("the hallway") --------------------------------------
    for i, (room, x, y) in enumerate(((F, 0.17, 5.50), (F, -0.25, 6.60), (F, -0.25, 7.50),
                                      (R, -0.20, 8.70), (R, -0.20, 9.75), (R, -0.20, 10.75)), 1):
        lighting.downlight(ctx, room, x, y, watts=55, name=f'{room}.downlight.{i}')
        trim = P.place(P.downlight(name=f'{room}.downlight_trim.{i}'), (x, y, ctx.ceil_z(room, x, y)))
        ctx.add(trim, room, 'light')

    # ---- switch plates (spec 8.2): three of them work the landing downlights -----------------------------
    for name, room, loc, nrm in ((R + '.switch.bay', R, (0.40, 11.95, zr + 1.25), EAST),
                                 # 0.10 north of the chamfer (v6 f_0035, v4 f_0300), not y 9.40: the spec kept
                                 # its world y when the reconcile moved the chamfer 0.24 south
                                 (R + '.switch.stair', R, (0.25, 8.93, zr + 1.25), EAST)):
        sw = put(P.switch_plate(1, name=name), loc, nrm, room, lm='dynamic')
        IX.tag(sw, 'light', rooms=LANDING, label='Landing lights')
    # south wall of the front landing, between the green door and the bathroom door (v4 f_0265-0271, f_0306):
    # 1-gang wide rocker (bathroom) east, 2-gang next to the green door.  Facing north, local +X is west, i.e. the
    # viewer's right: right rocker (with the plate body) = landing lights, left rocker = second-floor landing.
    za = zf + 1.27
    for name, x, rockers, body, rooms, label in (
            ('switch.bathroom', 0.802, ((0.0, 0.050),), True, ['green_bathroom'], 'Bathroom lights'),
            ('switch.landing', 0.71, ((0.0185, 0.020),), True, LANDING, 'Landing lights'),
            ('switch.second', 0.71, ((-0.0185, 0.020),), False, UPSTAIRS, 'Second-floor lights')):
        sw = put(_plate(f'{F}.{name}', rockers, body), (x, 4.95, za), NORTH, F, lm='dynamic')
        IX.tag(sw, 'light', rooms=rooms, label=label)

    # ---- sockets, thermostat, ceiling plate, smoke alarm ------------------------------------------------------
    put(P.socket(2, name=R + '.socket.pier'), (XPIER, 9.60, zr + 0.28), WEST, R)
    put(P.socket(2, name=F + '.socket'), (0.75, 4.95, zf + 0.28), NORTH, F)
    put(_thermostat(R + '.thermostat'), (0.25, 9.72, zr + 1.45), EAST, R)
    blank = P.switch_plate(1, 'blank', name=R + '.ceiling_plate')            # "got an empty socket here"
    blank.location, blank.rotation_euler = (-0.20, 9.30, ctx.ceil_z(R)), (math.pi / 2, 0, 0)
    ctx.add(blank, R, 'fit')
    alarm = P.lathe([(0, -0.036), (0.040, -0.036), (0.054, -0.030), (0.060, -0.014), (0.060, 0), (0, 0)], 20,
                    'plastic_white', name=F + '.smoke_alarm')
    alarm.location = (-0.25, 6.30, ctx.ceil_z(F))
    ctx.add(alarm, F, 'fit')

    # ---- radiator in the recess of the west wall, opposite the yellow-room door -----------------------------
    put(_radiator(R + '.radiator'), (XW, 10.48, zr + 0.13), WEST, R, plan_sym='radiator')

    # ---- paintings (west wall; P4 over the quarter landing).  Outer sizes follow the rectified crops ---------
    for key, room, loc, nrm, w, h, style, kw in (
            ('w1', F, (XW, 5.50, zf + 1.60), WEST, 0.50, 0.60, 'dark_gold_slip', dict(frame_w=0.046)),
            ('w2', F, (XW, 6.95, zf + 1.60), WEST, 0.55, 0.70, 'gilt_bead', dict(frame_w=0.055)),
            ('w3', R, (XPIER, 9.25, zr + 1.70), WEST, 0.93, 0.72, 'black', dict(frame_w=0.045, depth=0.03, slip=('gold_antique', 0.040))),
            ('w4', R, (XW, 10.48, zr + 1.62), WEST, 0.72, 0.56, 'gilt_bead', dict(frame_w=0.055)),
            ('w5', R, (XW, 11.95, zr + 1.55), WEST, 0.72, 0.56, 'bronze_gold', dict(frame_w=0.063)),
            ('p4', Q, (0.99, 8.43, zq + 1.75), EAST, 0.50, 0.41, 'gilt_swept',       # ornate antique gold
             dict(frame_w=0.06, mount=0.0485, mount_mat='#F2F0EA', glass=True))):
        pic = P.framed_picture(str(ART / f'landing1_{key}.jpg'), w, h, style, name=f'{room}.painting.{key}', **kw)
        put(pic, loc, nrm, room, 'decor')

    _steps(ctx)
    newel = _newel(F + '.newel')
    newel.location = (0.20, 8.13, 0)
    ctx.add(newel, F, 'joinery', lm='dynamic')

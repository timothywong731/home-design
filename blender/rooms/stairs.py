"""Main staircase, hall floor to the quarter landing (spec/rooms/stairs.md, spec/phase2/ground_corrections.md HA1-HA3,
spec/rooms/landing1.md 11).

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --levels G,1 --only shell,stairs --preview stairs \\
        --res 540x960 --samples 64 --tag stairs

Dresses the shell carcass of house.json `stair_main` (15 risers of 0.19, going 0.23, R4 at y 5.60, newel (0.20, 5.42),
R15 = quarter-landing nosing at y 8.13, Z 2.85).  The carcass keeps its raked soffit (the ceiling of the basement stair
below); only its plain tread / riser faces are deleted and replaced by the carpet here.  Built here: carpet with
wrapped nosings (bullnose R1, R2 / R3 radiating from the newel), cut string, returned tread nosings, panelled spandrel
and its skirting (closing the basement shaft from the hall), foot newel, handrail and spindles, the white drop of the
landing1 top newel under the string, the wall string and raking dado over the 45-degree face and the staircase wall
with the greige band under it, the three watercolours P1-P3 (crops: stairs_art.py), one downlight, and the hall
cornice returned along the staircase wall to the square edge of the hall ceiling (house.json zone stair_foot, 2.95).
The handrail dies into the underside of the white fascia under the first-floor strip capping (rooms/stairs2.py) about
0.5 m short of the top newel, as in v6 f_0038; the spindles beyond stop under that fascia (the strip's own spindles
stand on the capping above them, v4 f_0183).
Nothing on the stairs is operable: the stair downlight is on the landing circuit (hall plate's left gang, the landing
switches; ground_corrections 1, landing1.md 8.2).

Raking dado as filmed: level 0.965 on the hall wall, rakes up the diagonal at the pitch to 1.36 at the internal corner
(HA1, re-measured on v3 f_0009 against the hall rail and P1), a 0.12 level piece, then straight to the landing rail
at Z 4.015 at the quarter-landing edge (landing1 11.7, v6 f_0037: one plain knee there).  That rake is 45.7 degrees,
steeper than the 39.6-degree pitch: the two measured ends do not allow a parallel rail.
"""
import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix

from lib import lighting, materials as M, mouldings as mo, props as P, shell
from rooms import stairs2_parts as SP2

ROOM = 'stairs'
ART = Path(__file__).resolve().parents[1] / 'textures' / 'art'

# Eye-height views matched to the daylight footage (v3 = walk up, v6 = walk down, v2 = re-walk; v1 = night video).
CAMERAS = [
    dict(name='foot', pos=(0.42, 4.30, 1.65), look=(0.52, 6.6, 0.95), fov_deg=100, ref='v3 f_0017'),
    dict(name='diag', pos=(0.45, 5.75, 2.05), look=(0.82, 5.22, 1.45), fov_deg=100, ref='v3 f_0009'),
    dict(name='winders', pos=(0.30, 4.95, 1.65), look=(0.85, 5.3, 0.15), fov_deg=100, ref='v3 f_0011'),
    dict(name='flight', pos=(0.55, 5.6, 2.2), look=(0.55, 8.4, 3.5), fov_deg=100, ref='v3 f_0021'),
    dict(name='upper', pos=(0.6, 6.5, 2.9), look=(0.55, 8.4, 2.9), fov_deg=100, ref='v3 f_0029'),
    dict(name='down', pos=(0.6, 7.75, 4.1), look=(0.55, 5.0, 1.5), fov_deg=100, ref='v6 f_0041'),
    dict(name='ql', pos=(0.55, 8.5, 4.3), look=(1.0, 7.0, 2.6), fov_deg=100, ref='v6 f_0037'),
    dict(name='spandrel', pos=(-0.5, 7.2, 1.45), look=(0.15, 6.2, 1.5), fov_deg=100, ref='v1 f_0774'),
    dict(name='balustrade', pos=(-0.2, 7.3, 1.5), look=(0.05, 4.5, 1.3), fov_deg=100, ref='v1 f_0777'),
    dict(name='lobby', pos=(-0.25, 8.6, 1.55), look=(0.3, 7.85, 2.25), fov_deg=100, ref='v2 f_0520'),
]

WHITE = 'joinery_white'
NOSE = 0.025                   # carpet nosing overhang
X_WALL, X_OPEN = 0.99, 0.15    # staircase wall face / open (balustrade) side of the flight
XE = X_WALL - 0.015            # carpet runs into the 30 mm wall string
XS = X_OPEN - 0.006            # face of the cut string, 6 mm proud of the spandrel panelling
XP = X_OPEN - 0.001            # hall face of the spandrel panelling (1 mm proud of the carcass side faces)
XB = 0.155                     # its back face in the basement shaft (basement.md 3.2: upper wall face x 0.155)
XC = 0.205                     # west edge of the carpet = inside of the white tread ends
X_RAIL = 0.183                 # handrail / spindle line: the rail's west edge clears the well's slab edge (x 0.15)
RAIL_H, STRING_H = 0.90, 0.10  # handrail top / wall-string top above the nosing line
NEWEL_S = 0.115                # foot newel stock (scaled from the frames, not the spec's 95 mm)
Y_CORNER = 7.68                # lobby face of the basement-door wall: north end of the spandrel
TOP_NEWEL = (0.20, 8.13, 0.0475, 0.040)   # landing1's newel (rooms/landing1.py): centre, half width of foot / shaft
POST = (0.10, 0.20, 8.08, 8.18, 2.27)   # drop of that newel under the string (HA3): x0 x1 y0 y1, bottom Z
DADO_KNEE, DADO_LEVEL = 1.36, 0.12      # rail top at the internal corner (HA1), length of the level piece there
CARPET = 'carpet_silver_beige'                # the landings' carpet (landing1.md 4, 11.8)


def _carpet_profile(h):
    """Riser face + carpet wrapped over a rounded nosing: (d out from the riser line, height)."""
    return [(0, 0), (0, h - 0.050), (0.008, h - 0.044), (0.018, h - 0.034), (0.024, h - 0.022), (0.025, h - 0.012),
            (0.021, h - 0.004), (0.012, h), (0, h)]


def _step(mb, front, back, z0, h, mat):
    """One carpeted step: riser + nosing swept along `front` (plan polyline, wall end -> open end) and the tread top
    back to `back` (open end -> wall end, the next riser line); back=None: riser and nosing only."""
    mb.sweep(_carpet_profile(h), [(x, y, z0) for x, y in front], mat)
    if back:
        mb.face([(x, y, z0 + h) for x, y in front + back], mat, hint=(0, 0, 1))


def _wood():
    """Near-black gloss mahogany of the newels and handrails (also used by rooms/landing1.py)."""
    return M.solid('stairs_mahogany', '#2E211C', 0.14)


def _square(ob, half, ease=0.02):
    """Clamp a lathed mesh to square stock of half-width `half`: where the profile radius exceeds the square it
    becomes the square block, where it dips inside, the flats end in the stops of a real turning.  ease pulls the four
    arrises in a little.  Needs lathe vertices on the diagonals (segs % 8 == 0)."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    for v in bm.verts:
        x, y = v.co.x, v.co.y
        m = max(abs(x), abs(y))
        if m > half:
            k = half / m * ((1 - ease) if abs(abs(x) - abs(y)) < 1e-6 else 1)
            v.co.x, v.co.y = x * k, y * k
    bm.normal_update()
    for e in bm.edges:
        if len(e.link_faces) == 2:
            e.smooth = e.calc_face_angle() < math.radians(30)
    bm.to_mesh(ob.data)
    bm.free()
    return ob


def _strip_carcass(mat_name):
    """Delete the tread / riser faces of the shell carcass (material `mat_name`); its soffit and sides stay."""
    ob = bpy.data.objects.get(f'{ROOM}.flight')
    if ob is None:                                                   # built without the shell stage
        return
    slots = {i for i, s in enumerate(ob.material_slots) if s.material and s.material.name == mat_name}
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index in slots], context='FACES')
    bm.to_mesh(ob.data)
    bm.free()


def _fat(prof, e=0.0008):
    """Profile grown by e all round (a piece laid over a shell moulding it continues, without z-fighting)."""
    hm = max(h for _, h in prof)
    return [(d + e if d > 1e-6 else d, h + e * (2 * h / hm - 1)) for d, h in prof]


# timber tread end: 30 mm rounded nosing over a 20 mm scotia, (d out from the string face, h from the tread top)
TREAD_END = [(0, -0.052), (0.006, -0.052), (0.006, -0.048), (0.008, -0.040), (0.012, -0.034), (0.018, -0.031),
             (0.020, -0.030), (0.026, -0.027), (0.030, -0.015), (0.027, -0.004), (0.021, 0), (0, 0)]
# planted panel moulding, 30 wide x 12 proud, swept in the spandrel plane
PANEL_MOULD = [(0.015, 0), (0.015, 0.004), (0.011, 0.009), (0.005, 0.012), (-0.003, 0.012), (-0.008, 0.008),
               (-0.012, 0.006), (-0.015, 0.003), (-0.015, 0)]
# wall string: 30 mm board, beaded top edge, (d from the wall, h from its top line), 0.315 deep
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
    """Lathe profile of a stop on square stock of half-width h, from the tip of the flat's tongue (r = h, z_tip) to the
    arris (r = h * sqrt 2, z_tip + H); H < 0 = tongue pointing up."""
    return [(h / math.cos(a), z_tip + H * (1 - math.sqrt(max(0.0, 1 - math.tan(a) ** 2))))
            for a in (2 * math.pi * i / segs for i in range(segs // 8 + 1))]


def _bead(z, r, s, neck=11.5):
    """Crisp 14 mm bead of radius r (mm on 32 mm stock, scale s) starting at height z."""
    return [(neck * s, z + .001), ((r - 1.5) * s, z + .004), (r * s, z + .0075), ((r - 1.5) * s, z + .011),
            (neck * s, z + .014)]


def _spindle(name, height, base, top=0.15, w=0.045):
    """Square white baluster (stills t=776.5 / 777.0): base block, chamfer stop, collar bead, long vase, three beads at
    mid height, slender taper, collar bead, chamfer stop, top block.  One lathe clamped to the square stock."""
    s, t0, t1 = w / 32, base, height - top
    L, R = t1 - t0, 26 * w / 32
    zc = t0 + 0.5 * L
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
    """Mahogany foot newel, 1.75 m on 115 mm stock (stills t=241.5 / 249.0 / 777.0, v3 f_0017): square shaft with
    rounded stops, base ring, cup, fat vase, double ring, upper bulb, two rings, square block, collar, flattened ball
    with an incised groove.  One closed lathe clamped to the stock.  Origin floor."""
    h = NEWEL_S / 2
    R = 0.09
    p = [(0, 0), (R, 0), (R, .848)] + _stop(h, .885, -.035, 32)[::-1] + [
         (.056, .887), (.057, .891), (.056, .896), (.050, .900), (.037, .903), (.035, .908),
         (.037, .916), (.043, .930), (.049, .948), (.052, .962), (.052, .972), (.049, .979),
         (.036, .983), (.034, .990),
         (.038, 1.000), (.047, 1.020), (.053, 1.045), (.055, 1.065), (.053, 1.090), (.047, 1.125),
         (.040, 1.160), (.034, 1.188), (.032, 1.198),
         (.036, 1.202), (.047, 1.206), (.050, 1.212), (.047, 1.218), (.043, 1.220), (.046, 1.223),
         (.048, 1.228), (.045, 1.233), (.036, 1.236),
         (.034, 1.242), (.040, 1.252), (.047, 1.266), (.050, 1.280), (.049, 1.295), (.044, 1.310),
         (.036, 1.320), (.033, 1.326),
         (.036, 1.331), (.046, 1.335), (.049, 1.342), (.046, 1.349), (.040, 1.352), (.044, 1.356),
         (.047, 1.362), (.044, 1.368), (.038, 1.371), (.037, 1.378), (.042, 1.386)]
    p += _stop(h, 1.395, .040, 32) + [(R, 1.437), (R, 1.534)] + _stop(h, 1.561, -.025, 32)[::-1]
    p += [(.052, 1.566), (.053, 1.574), (.050, 1.582), (.040, 1.588), (.033, 1.594), (.031, 1.604), (.035, 1.614),
          (.036, 1.628)]
    ball = lambda a: (0.0575 * math.cos(math.radians(a)), 1.685 + 0.067 * math.sin(math.radians(a)))
    p += [ball(a) for a in (-50, -37.5, -25, -12.5, 0, 12.5, 25)]
    p += [ball(28), (ball(30)[0] - .003, ball(30)[1]), ball(32)]
    p += [ball(a) for a in (37.5, 50, 62.5, 75, 84)] + [(0, 1.752)]
    mb = mo.MB()
    mb.lathe(p, _wood(), segs=32)
    return _square(mb.finish(f'{ROOM}.newel'), h)


def _clip_shaft(ob, origin, x0, y0, z0, slope):
    """Delete the part of `ob` (local frame at `origin`) that hangs into the basement stair shaft: east of x0 and under
    the raked soffit z = z0 + slope * (y - y0).  The cut faces lie on the shaft's wall and soffit linings, which hide
    them (the foot newel stands at the edge of the shaft since the winders fan from (0.20, 5.42))."""
    ox, oy, oz = origin
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    n = (0.0, slope, -1.0)
    for co, no in (((x0 - ox, 0, 0), (1, 0, 0)), ((0, y0 - oy, z0 - oz), n)):
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=co, plane_no=no)
    below = lambda c: slope * (c.y + oy - y0) - (c.z + oz - z0) > 1e-6
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.calc_center_median().x + ox > x0 + 1e-6
                               and below(f.calc_center_median())], context='FACES')
    bm.to_mesh(ob.data)
    bm.free()


def _bezier(p0, p1, p2, p3, n):
    return [tuple((1 - t) ** 3 * a + 3 * t * (1 - t) ** 2 * b + 3 * t * t * (1 - t) * c + t ** 3 * d
                  for a, b, c, d in zip(p0, p1, p2, p3)) for t in (i / n for i in range(n + 1))]


def _cut(line, a, b, c):
    """Point where the plan line through line[0] -> line[1] meets a*x + b*y = c."""
    (x0, y0), (x1, y1) = line
    t = (c - a * x0 - b * y0) / (a * (x1 - x0) + b * (y1 - y0))
    return x0 + t * (x1 - x0), y0 + t * (y1 - y0)


def build(ctx):
    S = ctx.stair('stair_main')
    rise, going, r4, N = S['rise'], S['going'], S['firstStraightRiserY'], S['risers']
    nx, ny = S['newel']
    y_top, lz = S['lastStraightRiserY'], S['toZ']                    # 8.13, 2.85
    w1, w2, w3 = S['winders']['risers']
    ch = ctx.chamfers(ROOM)[0]                                       # the 45-degree face p -> q
    (px, py), (qx, qy) = ch['p'], ch['q']
    L = math.hypot(qx - px, qy - py)
    ux, uy = (qx - px) / L, (qy - py) / L                            # along the face, external -> internal corner
    dn = (-uy, ux)                                                   # its normal into the stairs
    on_diag = lambda s: (px + ux * s, py + uy * s)
    slope = rise / going
    k = math.hypot(1, slope)
    R = lambda n: r4 + going * (n - 4)                               # riser line of step n (straight flight)
    NL = lambda y: rise * (4 + (y + NOSE - r4) / going)              # nosing line
    inv = lambda z: r4 - NOSE + going * (z / rise - 4)               # y where the nosing line is at z
    y_newel = ny + NEWEL_S / 2                                       # north face of the foot newel
    xn, xne = nx - NEWEL_S / 2, nx + NEWEL_S / 2                     # its west / east faces
    tnx, tny, tnh, tns = TOP_NEWEL
    y_end = POST[2]                                                  # open-side joinery dies into the drop post
    last = N - 1                                                     # 14 treads with an open end
    carpet = M.mat(CARPET)

    _strip_carcass(M.mat((ctx.rooms[ROOM].get('covering') or ctx.rooms[ROOM]['floor'])['material']).name)

    # ---- carpet ---------------------------------------------------------------------------------------------
    # Carpet edges: 15 mm inside the 30 mm wall string on the stair wall and on the 45-degree face.
    dc = dn[0] * px + dn[1] * py + 0.015                             # diagonal edge line: dn . (x, y) = dc
    mb = mo.MB()
    # R1: quarter ellipse (house.json) from the external corner, round the newel's west side, then a tight return
    # into it; starts 22 mm west of the hall wall so the nosing clears the hall skirting
    (ecx, ecy), (ax, ay) = w1['ellipse']['centre'], w1['ellipse']['semi']
    rr = xn - (ecx - ax)
    t0 = math.degrees(math.acos((px - 0.022 - ecx) / ax))
    r1 = [(ecx + ax * math.cos(t), ecy - ay * math.sin(t)) for t in
          (math.radians(t0 + (180 - t0) * i / 12) for i in range(13))]
    r1 += [(xn - rr * math.cos(a), ny + rr * math.sin(a)) for a in (math.radians(d) for d in (30, 60, 90))]
    r1.append((xn + 0.012, ny + rr))
    # R2, R3: straight from the newel to the face / the internal corner, cut at the carpet edges and inside the newel
    r2 = [_cut(w2['line'], *dn, dc), _cut(w2['line'], 1, 0, xne - 0.012)]
    r3 = [_cut(w3['line'], *dn, dc), _cut(w3['line'], 1, 0, xne - 0.012)]
    _step(mb, r1, r2[::-1], -0.03, rise + 0.03, carpet)              # R1 down to the basement shelf level
    _step(mb, r2, r3[::-1], rise, rise, carpet)
    _step(mb, r3, [(XC, y_newel + 0.012), (XC, R(4)), (XE, R(4))], 2 * rise, rise, carpet)
    y15 = y_top - 0.004                                              # 4 mm proud of the landing slab edge
    for n in range(4, N):
        yb = y15 if n == N - 1 else R(n + 1)
        _step(mb, [(XE, R(n)), (XC, R(n))], [(XC, yb), (XE, yb)], (n - 1) * rise, rise, carpet)
    _step(mb, [(XE, y15), (tnx + tnh, y15)], None, (N - 1) * rise, rise, carpet)     # R15: the landing nosing
    # ... whose top laps 20 mm onto the quarter-landing carpet, 1 mm proud: no see-through slot at the slab edge
    # (clear of the landing1 newel and of the landing skirting; the wall end is under the wall string)
    xl0, xl1, yl0, yl1 = tnx + tnh + 0.002, XE - 0.012, y15 - 0.010, y_top + 0.02
    mb.face([(xl1, yl0, lz + 0.001), (xl0, yl0, lz + 0.001), (xl0, yl1, lz + 0.001), (xl1, yl1, lz + 0.001)], carpet,
            hint=(0, 0, 1))
    flight = mb.finish(f'{ROOM}.carpet')

    # ---- open side: cut string, returned tread nosings, spandrel panelling and its skirting ----------------------
    sp = mo.MB()
    for n in range(3, last + 1):
        z, ya, yb = n * rise, R(n), min(R(n + 1), y_end)
        if n == 3:                                                   # starts behind the newel: side return only
            ya = y_newel - 0.005
            sp.sweep(TREAD_END, [(XS, ya, z), (XS, yb, z)], WHITE)
        else:                                                        # nosing mitred round the corner
            sp.sweep(TREAD_END, [(XC, ya, z), (XS, ya, z), (XS, yb, z)], WHITE)
            sp.face([(X_OPEN, ya, z - rise), (XC, ya, z - rise), (XC, ya, z - 0.052), (X_OPEN, ya, z - 0.052)],
                    WHITE, hint=(0, -1, 0))                          # riser end between string and carpet
        sp.face([(XC, ya, z), (XS, ya, z), (XS, yb, z), (XC, yb, z)], WHITE, hint=(0, 0, 1))
    # cut string: saw-tooth top, raking bottom 0.28 under the nosing line; over the lobby cupboard (y > 7.68) it
    # stops at the cupboard's underside (Z 2.30) instead of hanging below it
    zb = 2.30
    yc = inv(zb + 0.28)
    saw = [(y_newel, 3 * rise - 0.02)]
    for n in range(4, last + 1):
        saw += [(R(n), (n - 1) * rise - 0.02), (R(n), n * rise - 0.02)]
    saw += [(y_end, last * rise - 0.02), (y_end, max(NL(y_end) - 0.28, zb))]
    if yc > Y_CORNER:
        saw += [(yc, zb), (Y_CORNER, zb), (Y_CORNER, NL(Y_CORNER) - 0.28)]
    saw += [(y_newel, NL(y_newel) - 0.28)]
    sp.prism([(XS, y, z) for y, z in saw], (X_OPEN - XS, 0, 0), WHITE, grain=1)
    # flush panelling from the basement shelf (Z -0.03) to the string, both faces (the back is the shaft wall)
    top = lambda y: NL(y) - 0.26
    outline = [(y_newel, -0.03), (Y_CORNER, -0.03), (Y_CORNER, top(Y_CORNER)), (y_newel, top(y_newel))]
    sp.face([(XP, y, z) for y, z in outline], WHITE, hint=(-1, 0, 0))
    sp.face([(XB, y, z) for y, z in outline], shell.material(shell.finish('basement_stair')['upper']), hint=(1, 0, 0))
    sp.face([(XP, Y_CORNER, -0.03), (XB, Y_CORNER, -0.03), (XB, Y_CORNER, top(Y_CORNER)), (XP, Y_CORNER, top(Y_CORNER))],
            WHITE, hint=(0, 1, 0))                                   # the arris at the basement-door wall
    # planted raking bead under the string (the strong double shadow line of every spandrel still)
    sp.sweep(PANEL_MOULD, [(XP - 0.0002, y, NL(y) - 0.28 - 0.016 * k) for y in (y_newel, Y_CORNER)], WHITE,
             up=(-1, 0, 0), ends=((0, 0, -k), (0, 0, -k)))
    # seven raised-moulding panels with raking tops, 65 mm stiles (still t=776.0, v2 f_0522)
    ptop = lambda y: NL(y) - 0.38
    nb, st, zp, m = 7, 0.065, 0.19, 0.015
    y0, y1 = inv(zp + m + 0.045 + 0.02 + 0.38) - m, Y_CORNER - 0.055
    pw = (y1 - y0 - st * (nb - 1)) / nb
    for b in range(nb):
        ya = y0 + (pw + st) * b + m
        yb = ya + pw - 2 * m
        sp.sweep(PANEL_MOULD, [(XP - 0.0002, y, z) for y, z in
                               ((ya, zp + m), (yb, zp + m), (yb, ptop(yb) - 0.02), (ya, ptop(ya) - 0.02))],
                 WHITE, closed=True, up=(-1, 0, 0))
    # hall skirting along the spandrel foot, round the arris onto the door wall up to the architrave (x 0.195);
    # the last leg lies 1 mm over the shell's piece there
    sp.sweep(mo.PROFILES['sk_hall'], [(XP, y_newel, 0), (XP, Y_CORNER + 0.001, 0), (0.194, Y_CORNER + 0.001, 0)], WHITE)
    spandrel = sp.finish(f'{ROOM}.spandrel')

    # ---- drop of the landing1 top newel under the string (HA3, basement.md 3.6): square white post from the hall
    # ceiling down to Z 2.27 with a moulded cap; above the tread it only covers the passage side (the mahogany newel
    # of rooms/landing1.py takes over inside the well)
    x0, x1, py0, py1, pz = POST
    zt = last * rise - 0.052                                         # under tread 14's returned nosing
    pb = mo.MB()
    pb.box((x0, py0, pz), (x1, py1, zt), WHITE, bev=0.006)
    pb.box((x0, py0, zt - 0.01), (tnx - tnh - 0.0005, py1, ctx.ceil_z('hallway', 0.0, 8.0)), WHITE, bev=0.004)
    cap = [(d * 0.7, h * 0.7) for d, h in mo.PROFILES['ped_cap']]
    pb.sweep(cap, [(x0, py0, pz + 0.012), (x0, py1, pz + 0.012), (x1, py1, pz + 0.012), (x1, py0, pz + 0.012)], WHITE,
             closed=True)
    post = pb.finish(f'{ROOM}.newel_drop')

    # ---- wall side: skirting return, wall string, raking dado, greige band ------------------------------------
    # Developed coordinate s: along the 45-degree face from its external corner (0 .. L), then up the staircase wall.
    def wall_pt(s, z):
        if s <= L:
            x, y = on_diag(s)
            return (x, y, z)
        return (X_WALL, qy + (s - L), z)
    rake = lambda s: NL(qy + (s - L)) + STRING_H                     # string top line, also extended back onto the face
    # skirting return 30 mm (HA1 "about 60": tread 1, 0.19, would bury a longer 0.17 return), then the string
    # springs up steeply and runs into the rake (h45a: v2 f_0690-0694)
    s0, sj = 0.03, 0.30
    curve = _bezier((s0, 0.17), (s0 + 0.012, 0.24), (sj - 0.08, rake(sj) - slope * 0.08), (sj, rake(sj)), 12)
    # it must clear the carpet where the treads run into the face / wall (tread top + 30 mm, at the samples)
    clear = [(0.0, 0.19), (math.hypot(r2[0][0] - px, r2[0][1] - py), 2 * rise), (L, 3 * rise)]
    for s, z in curve:
        need = max(zz for ss, zz in clear if ss <= s + 1e-9) + 0.03 if s > 0.05 else 0.17
        assert z >= need - 1e-6, f'wall string at s={s:.3f} is {z:.3f}, below {need:.3f}'
    ws = mo.MB()
    ws.sweep(_fat(mo.PROFILES['sk_hall']), [(px, py - 0.03, 0), (px, py, 0), wall_pt(s0, 0)], WHITE)
    ya_top = y_top - 0.08
    ws.sweep(WALL_STRING, [wall_pt(s, z) for s, z in curve] + [wall_pt(L, rake(L))]
             + [(X_WALL, ya_top, NL(ya_top) + STRING_H), (X_WALL, y_top, lz + 0.17)], WHITE)
    # dado: plumb section over the hall-wall lead-in (laid over the shell rail's end) and up the face ...
    dh = mo.profile_size('dado_hall')[1]
    zh = shell.finish('hallway')['dado']                             # 0.965
    m_ic = (dn[0] - 1, dn[1])                                        # mitre to the staircase wall at the internal corner
    m_ic = (m_ic[0] / (m_ic[0] * dn[0] + m_ic[1] * dn[1]), m_ic[1] / (m_ic[0] * dn[0] + m_ic[1] * dn[1]), 0)
    ws.sweep(_fat(mo.PROFILES['dado_hall']), [(px, py - 0.03, zh - dh), (px, py, zh - dh), (qx, qy, DADO_KNEE - dh)],
             WHITE, ends=(None, m_ic))
    # ... then the true section on the staircase wall: level piece, rake, knee, level stub to the landing rail
    zq = ctx.floor_z('landing1_ql') + shell.finish('landing1_ql')['dado']        # 4.015
    yk, yq = qy + DADO_LEVEL, y_top - 0.03
    dado_rail = lambda y: DADO_KNEE + (zq - DADO_KNEE) * (y - yk) / (yq - yk) if y > yk else DADO_KNEE
    ws.sweep(DADO, [(X_WALL, qy, DADO_KNEE), (X_WALL, yk, DADO_KNEE), (X_WALL, yq, zq), (X_WALL, y_top, zq)], WHITE,
             up=(-1, 0, 0))
    wall_string = ws.finish(f'{ROOM}.wall_string')

    # ---- the hall ceiling runs flat over the stair foot to the R4 line and ends in a plain square edge (shell zone
    # stair_foot, Z 2.95; v1 f_0245, v6 f_0041 / f_0043): the hall cornice on the 45-degree face returns along the
    # staircase wall to that edge.
    zc = ctx.ceil_z(ROOM, 0.5, 5.3)                                  # 2.95
    cc = mo.MB()
    cc.sweep(mo.PROFILES['cornice_hall'], [(X_WALL, qy, zc), (X_WALL, r4, zc)], 'plaster_white', ends=(m_ic, None))
    B = mo.HALL_BAND
    yb = r4 - B['pitch'] / 2                                         # one modillion, half a pitch from the edge
    cc.at(Matrix(((0, -1, 0, X_WALL - B['d']), (1, 0, 0, yb), (0, 0, 1, zc + B['top']), (0, 0, 0, 1))))
    mo.modillion(cc, 'plaster_white', B['w'], B['h'], B['proj'])
    cornice = cc.finish(f'{ROOM}.cornice')

    grey, e = M.paint(M.PAINT['hall_dado_grey']), 0.0015             # greige below the rail, 1.5 mm proud
    gb = mo.MB()
    face_band = [(0.0, 0.14), (s0, 0.14)] + [(s, z - 0.03) for s, z in curve if s <= L] + [(L, rake(L) - 0.03),
                 (L, DADO_KNEE - 0.035), (0.0, zh - 0.035)]
    gb.face([(x + dn[0] * e, y + dn[1] * e, z) for x, y, z in (wall_pt(min(s, L), z) for s, z in face_band)], grey,
            hint=(dn[0], dn[1], 0))
    wall_band = ([(qy, rake(L) - 0.03)] + [(qy + (s - L), z - 0.03) for s, z in curve if s > L]
                 + [(ya_top, NL(ya_top) + STRING_H - 0.03), (y_top, lz + 0.14), (y_top, zq - 0.035), (yq, zq - 0.035),
                    (yk, DADO_KNEE - 0.035), (qy, DADO_KNEE - 0.035)])
    gb.face([(X_WALL - e, y, z) for y, z in wall_band], grey, hint=(-1, 0, 0))
    band = gb.finish(f'{ROOM}.dado_band')

    # ---- balustrade: foot newel, handrail up to the strip fascia (v6 f_0038), two spindles per tread ------------------
    newel = _newel()
    newel.location = (nx, ny, 0)
    # its north-east corner overhangs the basement stair shaft: cut it back to the linings of rooms/basement.py
    # (wall face x 0.156, raked soffit -0.004 at y 5.42 rising 2.5 per m) + 6 mm, so no mahogany shows down there
    _clip_shaft(newel, (nx, ny, 0), 0.156, 5.42, 0.002, 2.5)
    U = lambda y: NL(y) + RAIL_H - 0.055 * k                         # underside of the handrail
    # underside of the white fascia under the strip capping (rooms/stairs2.py): 3.32 by the strip, 3.13 by the step
    fascia = lambda y: ctx.floor_z('landing1_front', X_RAIL - 0.2, y) - SP2.STRIP_FASCIA
    ya, yb = y_newel - 0.005, y_newel
    while U(yb) + 0.055 * k < fascia(yb) + 0.025:                    # rail top 25 mm into the fascia, then stop
        yb += 0.005
    rail = mo.sweep(_handrail(k), [(X_RAIL, ya, U(ya)), (X_RAIL, yb, U(yb))], name=f'{ROOM}.handrail', material=_wood())
    SP = (0.045, 0.16)                                               # two per tread at 0.115 centres (f_0777)
    heights = [U(R(4) + dy) - 4 * rise + 0.02 for dy in SP]          # tops let into the rail
    protos = [_spindle(f'{ROOM}.spindle.p{i}', h, base) for i, (h, base) in enumerate(zip(heights, (0.20, 0.295)))]
    spindles, short = [], {}
    y_last = tny - tnh - 0.0225 - 0.03                               # a base block 30 mm clear of the top newel's foot
    for n in range(3, last + 1):
        for dy, proto in zip(SP, protos):
            y = min(R(n) + dy, y_last)
            me = proto.data                                          # shared mesh; the top stays housed in the rail
            if y + 0.0225 > yb - 0.03:                               # past the rail: up to the fascia, let in 5 mm
                h = round(fascia(y) + 0.005 - n * rise, 3)
                if h not in short:
                    sp = _spindle(f'{ROOM}.spindle.s', h, 0.20) if h - 0.35 >= 0.46 else SP2.stub(f'{ROOM}.spindle.s', h)
                    short[h] = sp.data
                    bpy.data.objects.remove(sp)
                me = short[h]
            ob = bpy.data.objects.new(f'{ROOM}.spindle.{len(spindles):02d}', me)
            ob.location = (X_RAIL, y, n * rise)
            spindles.append(ob)
    for ob in protos:
        bpy.data.objects.remove(ob)

    # ---- tagging --------------------------------------------------------------------------------------------
    ctx.add(flight, ROOM, 'fit', plan_sym='stair')
    for ob in (spandrel, post):
        ctx.add(ob, ROOM, 'joinery')
    for ob in (newel, rail, *spindles):
        ctx.add(ob, ROOM, 'joinery', lm='dynamic')
    ctx.add(wall_string, ROOM, 'trim')
    ctx.add(cornice, ROOM, 'trim')
    ctx.add(band, ROOM, 'trim')

    # ---- three watercolours of one set (landing1.md 11.4; P4 over the quarter landing is landing1's): ornate
    # antique-gold frames with a beaded sight edge, wide white mount, glazed; hung plumb.  P1 fills the 45-degree
    # face (0.44 wide: house.json makes the face 0.48, the footage about 0.55).
    pics = [('p1', on_diag(L / 2), 1.80, dn, 0.44, 0.35, 0.052, 0.042),
            ('p2', (X_WALL, 6.25), None, (-1, 0), 0.50, 0.40, 0.06, 0.048),
            ('p3', (X_WALL, 7.30), None, (-1, 0), 0.50, 0.40, 0.06, 0.048)]
    for key, (x, y), z, nrm, w, h, fw, mt in pics:
        if z is None:                                                # uphill bottom corner 0.12 over the rail (v6 f_0037)
            z = dado_rail(y + w / 2) + 0.12 + h / 2
        pic = P.framed_picture(str(ART / f'stairs_{key}.jpg'), w, h, 'gilt_bead', frame_w=fw, mount=mt,
                               mount_mat='#F2F0EA', glass=True, name=f'{ROOM}.painting.{key}')
        for sl in pic.material_slots:                                # dull olive-bronze gold (stairs.md 6), not bright gilt
            if sl.material == P.mat('gold_bright'):
                sl.material = P.mat('olive_bronze')
        ctx.add(P.place(pic, (x, y, z), facing=nrm), ROOM, 'decor')

    # ---- light: one recessed downlight in the flat soffit over the lower flight (spec section 7) ---------------
    lx, ly = 0.57, 5.80
    lighting.downlight(ctx, ROOM, lx, ly, watts=60, kelvin=3000, spot_deg=130, name=f'{ROOM}.downlight')
    ctx.add(P.place(P.downlight(name=f'{ROOM}.downlight_trim'), (lx, ly, ctx.ceil_z(ROOM, lx, ly))), ROOM, 'light')

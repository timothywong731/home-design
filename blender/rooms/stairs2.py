"""Second flight, first floor to second floor (spec/rooms/stairs2.md), and every balustrade round its well.

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --levels 1,2 --only shell,stairs2,landing2_platform,landing2_head \
        --preview stairs2 --res 540x960 --samples 64 --tag stairs2

The shell's carcass (`stairs2.flight`: treads, risers, raked soffit) stays; this module dresses it: the carpet shared
with the main flight and the first-floor landings (carpet_silver_beige) with rolled nosings and the bullnose, cut
string with timber tread ends, wall string with its sweep over the winders, raking dado and the greige band under it,
both newels, handrail, spindles, the five cat studies.  Per blender/MULTILEVEL.md section 1 it also owns the guards
on the well's virtual walls: the platform balustrade with its apron (tagged landing2_platform) and the level
balustrade on the first-floor strip (v_strip_well) with the fascia the main flight's handrail dies into.
Spindle, handrail section, tread-end and wall-string profiles are those of the flight below (copied into
rooms/stairs2_parts.py).  No light fitting, switch or socket on the stair itself (stairs2.md 5, 8).
"""
import math
from pathlib import Path

import bpy

from lib import materials as M, mouldings as mo, props as P, shell
from rooms import stairs2_parts as SP

ROOM = 'stairs2'
ART = Path(__file__).resolve().parents[1] / 'textures' / 'art'

CAMERAS = [
    dict(name='foot', pos=(0.3, 5.6, 4.9), look=(0.5, 8.0, 6.3), fov_deg=100, ref='v4 f_0171'),
    dict(name='count', pos=(0.55, 5.8, 4.9), look=(0.6, 8.7, 7.0), fov_deg=100, ref='v4 f_0192'),
    dict(name='newel', pos=(-0.35, 6.75, 4.95), look=(0.25, 6.25, 4.2), fov_deg=100, ref='v4 f_0178'),
    dict(name='bull', pos=(-0.25, 5.35, 4.7), look=(0.35, 6.05, 3.5), fov_deg=100, ref='v6 f_0024'),
    dict(name='guard', pos=(-0.35, 6.85, 4.95), look=(0.2, 7.7, 4.0), fov_deg=100, ref='v4 f_0183'),
    dict(name='archi', pos=(-0.05, 5.5, 4.95), look=(0.99, 6.15, 4.75), fov_deg=100, ref='v4 f_0196'),
    dict(name='winders', pos=(0.7, 7.45, 6.25), look=(0.62, 8.6, 5.55), fov_deg=100, ref='v4 f_0320'),
    dict(name='corner', pos=(-0.25, 8.25, 7.55), look=(0.5, 8.75, 6.9), fov_deg=100, ref='v13 t4 / v4 f_0349'),
    dict(name='cats', pos=(-0.15, 8.35, 7.6), look=(0.75, 8.5, 6.75), fov_deg=100, ref='v13 t4 (N1, N2, dado)'),
    dict(name='top', pos=(0.55, 8.55, 7.5), look=(0.5, 7.2, 5.3), fov_deg=100, ref='v4 f_0355'),
    dict(name='down', pos=(0.6, 6.75, 5.75), look=(0.45, 5.0, 4.7), fov_deg=100, ref='v6 f_0014'),
]

WHITE = 'joinery_white'
NOSE = 0.025                    # carpet nosing overhang
X_WALL, X_OPEN = 0.99, 0.15     # staircase wall face / open side (strip and platform edge)
XE = X_WALL - 0.015             # carpet runs into the 30 mm wall string
XS = X_OPEN - 0.006             # face of the cut string
XC = 0.205                      # west edge of the carpet = inside of the white tread ends
X_RAIL = 0.19                   # handrail centre line of all three balustrades: inside the newels (x 0.195 / 0.20)
X_SP = 0.185                    # spindle centre line: on the tread ends, clear of the carpet edge XC
X_CAP = 0.22                    # well face of the strip capping and fascia
X_APRON = 0.215                 # well face of the platform apron: boxed out to the balustrade plane
RAIL_H, DADO_H, STRING_H, PRINT_H = 0.90, 0.975, 0.10, 1.40     # plumb heights above the nosing line
NEWEL_S = 0.095                 # newel stock
SPINDLE_W = 0.038               # spindle stock: 0.4 x the newel as in v4 f_0178 (spec 32 mm, flight below 45 on a 115 newel)


def roll(h):
    """Carpet wrapped over a rounded nosing, to plant on a plain riser: (d out from the riser, height); the back
    is open and 3 mm inside the riser, the top 1 mm proud of the tread."""
    return [(-0.003, h - 0.052), (0, h - 0.050), (0.008, h - 0.044), (0.018, h - 0.034), (0.024, h - 0.022),
            (0.025, h - 0.012), (0.021, h - 0.004), (0.012, h + 0.001), (-0.003, h + 0.001)]


def nosing(mb, pts, z0, h, mat):
    """Nosing roll along a riser line; pts = plan polyline walked with the LOWER tread on the left."""
    mb.sweep(roll(h), [(x, y, z0) for x, y in pts], mat)


CARPET = 'carpet_silver_beige'  # one carpet for both flights and the first-floor landings (#A9A397, stairs.md round 3)


def wood():
    """Gloss mahogany of every newel and handrail round both flights: one named solid with rooms/stairs.py and
    rooms/landing1.py, whose newel takes the strip rail (v4 f_0183, v6 f_0026: newel and rails one colour)."""
    return M.solid('stairs_mahogany', '#2E211C', 0.14)


BALL_R = 0.042                  # finial ball: 0.85-0.9 x the block face (v4 f_0177, f_0179; v13 t4; c_v5_139_bal)


def newel(name, base, block, foot=None):
    """Mahogany newel on 95 mm stock (v4 f_0178 / f_0190, v5 f_0140).  Local z: square base to `base` with chamfered
    shoulders, ring, long plain shaft swelling slightly upward, two rings, square block from `block` (0.21 high,
    the handrails enter it) with a pyramidal top, collar, ball finial; top of the ball = block + 0.349.
    foot = (lo, hi) local corners of a box carrying part of the square base further down."""
    h, R, b = NEWEL_S / 2, 0.075, block                              # R > arris radius = full square after _square
    s0, s1 = base + 0.03, block - 0.03
    p = [(0, 0), (R, 0), (R, base),
         (0.033, s0), (0.040, s0 + 0.006), (0.042, s0 + 0.012), (0.040, s0 + 0.018), (0.031, s0 + 0.022),      # ring
         (0.029, s0 + 0.035), (0.031, s0 + 0.3 * (s1 - s0)), (0.036, s1 - 0.075),                               # shaft
         (0.033, s1 - 0.062), (0.041, s1 - 0.057), (0.043, s1 - 0.050), (0.041, s1 - 0.043), (0.035, s1 - 0.040),
         (0.041, s1 - 0.036), (0.044, s1 - 0.028), (0.041, s1 - 0.020), (0.036, s1 - 0.016), (0.034, s1 - 0.008),
         (0.036, s1),
         (R, b), (R, b + 0.21), (0.030, b + 0.240),                                                             # block
         (0.027, b + 0.245), (0.036, b + 0.250), (0.038, b + 0.257), (0.035, b + 0.263), (0.026, b + 0.266)]   # collar
    zb = b + 0.270 + BALL_R * math.sin(math.radians(60))           # ball centre: its -60 deg point on the collar
    p += [(BALL_R * math.cos(math.radians(a)), zb + BALL_R * math.sin(math.radians(a)))
          for a in (-60, -45, -30, -15, 0, 15, 30, 45, 60, 75)] + [(0, zb + BALL_R)]
    mb = mo.MB()
    mb.lathe(p, wood(), segs=32)
    if foot:
        mb.box(*foot, wood())
    return SP.square(mb.finish(name), h)


def cut_back(name, sel, to):
    """Slide the vertices of a shell trim run (`name`) for which sel(world co) holds to y = `to`: its end ring and
    end cap move, the run gets shorter.  ponytail: edits the shell trim mesh of this unit's own rooms; skipped
    quietly if the trim is missing (--bare)."""
    ob = bpy.data.objects.get(name)
    if ob is None:
        return
    mw, inv = ob.matrix_world, ob.matrix_world.inverted()
    for v in ob.data.vertices:
        w = mw @ v.co
        if sel(w):
            w.y = to
            v.co = inv @ w
    ob.data.update()


class _Balusters:
    """Balusters by height, sharing one mesh per height."""

    def __init__(self):
        self.protos, self.out = {}, []

    def add(self, name, loc, h, base=0.18, top=0.12):
        h = round(h, 3)
        key = (h, base, top)
        if key not in self.protos:
            full = h - base - top >= 0.47                            # the full turning needs 0.46 m
            self.protos[key] = (SP.spindle(f'{name}.proto', h, base, top, SPINDLE_W) if full
                                else SP.stub(f'{name}.proto', h, SPINDLE_W))
        ob = bpy.data.objects.new(name, self.protos[key].data)
        ob.location = loc
        self.out.append(ob)

    def done(self):
        for ob in self.protos.values():
            bpy.data.objects.remove(ob)
        return self.out


def build(ctx):
    S = ctx.stair('stair_second')
    z0, z2, rise, going, r1 = S['fromZ'], S['toZ'], S['rise'], S['going'], S['firstStraightRiserY']
    ns = S['straightRisers']                                         # 10: R10 leads to the first winder
    fx, fy = S['newel'][0] - 0.005, S['newel'][1]                    # 5 mm west: the base covers the carcass corner
    tx, ty = S['turningNewel']
    yw = max(p[1] for p in S['winders']['polygon'])                  # 8.73 north wall of the well
    zp = ctx.floor_z('landing2_platform')                            # 6.22
    y_well = min(p[1] for p in ctx.room_poly('landing2_platform'))   # 6.23 south face of the well
    zb_ap = ctx.ceil_z('landing1_front') - 0.02                      # underside of the platform apron (5.75)
    slope = rise / going
    k = math.hypot(1, slope)                                         # plumb height of 1 m measured square to the rake
    R = lambda n: r1 + going * (n - 1)                               # riser line of step n (straight part)
    NL = lambda y: z0 + rise * ((y + NOSE - r1) / going + 1)         # nosing line
    inv = lambda z: r1 - NOSE + going * ((z - z0) / rise - 1)        # y where the nosing line is at z
    yn0, yn1 = fy + NEWEL_S / 2, ty - NEWEL_S / 2                    # north face of the foot newel / south face of the turning newel
    last = ns - 1                                                    # last tread with an open end (9)
    o = ctx.openings.get('d_gbath')
    y_arch = o['center'][1] + o['width'] / 2 + 0.08 if o else r1 - 0.09      # north edge of the bathroom architrave (5.97)

    # ---- carpet: the carcass recoloured, nosing rolls, bullnose ------------------------------------------
    # The flight, its bullnose and the first-floor landings share one carpet; only the top nosing R13 wraps the
    # second-floor landing carpet (house.json landing2_head floor).
    grey, pale = M.mat(CARPET), M.mat('carpet_grey_twist')
    fl = bpy.data.objects.get('stairs2.flight')
    for sl in fl.material_slots if fl else ():
        if sl.material == pale:
            sl.material = grey
    cb = mo.MB()
    for n in range(2, ns + 1):
        nosing(cb, [(XE, R(n)), (XC if n < ns else tx + NEWEL_S / 2, R(n))], z0 + rise * (n - 1), rise, grey)
    for n, w in enumerate(S['winders']['risers'][:2], ns + 1):      # R11, R12: from the wall into the turning newel
        (ax, ay), (bx, by) = w['line'][1], w['line'][0]
        ln = math.hypot(bx - ax, by - ay)
        ux, uy = (bx - ax) / ln, (by - ay) / ln
        nosing(cb, [(ax + ux * 0.02, ay + uy * 0.02), (bx - ux * 0.05, by - uy * 0.05)], z0 + rise * (n - 1), rise, grey)
    # top nosing R13 and its 7 cm return against the old rear wall: the landing carpet wraps over it
    xj = max(x for x, y in ctx.room_poly('landing2_head') if abs(y - yw) < 1e-6 and x < 0.5)        # 0.32
    nosing(cb, [(xj - 0.02, yw), (X_OPEN, yw), (X_OPEN, ty + NEWEL_S / 2)], z2 - rise, rise, pale)
    # Bullnose (v6 f_0022-f_0024, v4 f_0190): the first step is carpeted in the landing carpet, stands 70 mm in
    # front of the newel's south face and ends in a quarter round on the line of the newel's west face; the newel
    # stands in it, the white tread end of T1 is north of the newel.  1 mm above the carcass tread so the two tops
    # do not fight.
    x0, yn_s, rb = fx - NEWEL_S / 2, fy - NEWEL_S / 2, 0.07
    yf = yn_s - rb
    arc = [(x0 + rb - rb * math.sin(a), yf + rb - rb * math.cos(a)) for a in (math.radians(15 * i) for i in range(7))]
    SP.step(cb, [(XE, yf)] + arc[:-1] + [(x0, yn_s)], [(XC, yn_s), (XC, R(2)), (XE, R(2))], z0 + 0.001, rise, grey)
    ctx.add(cb.finish('stairs2.carpet'), ROOM, 'fit')

    # ---- open side: timber tread ends and the cut string ----------------------------------------------
    sp, e = mo.MB(), 0.002                                           # tread ends 2 mm proud of the carcass
    for n in range(1, last + 1):
        z, ya, yb = z0 + rise * n + e, R(n), R(n + 1) if n < last else yn1
        if n == 1:                                                   # starts behind the newel: side return only
            ya = yn0 - 0.005
            sp.sweep(SP.TREAD_END, [(XS, ya, z), (XS, yb, z)], WHITE)
        else:                                                        # nosing mitred round the corner
            sp.sweep(SP.TREAD_END, [(XC, ya, z), (XS, ya, z), (XS, yb, z)], WHITE)
            sp.face([(X_OPEN, ya - e, z - rise), (XC, ya - e, z - rise), (XC, ya - e, z - 0.052),
                     (X_OPEN, ya - e, z - 0.052)], WHITE, hint=(0, -1, 0))      # riser end between string and carpet
        sp.face([(XC, ya, z), (XS, ya, z), (XS, yb, z), (XC, yb, z)], WHITE, hint=(0, 0, 1))
    Zs = lambda y: NL(y) - 0.36                                      # lower edge of the string: 2 cm under the soffit
    y_fl = inv(z0 + 0.36)                                            # where it reaches the landing floor (6.22)
    saw = [(yn0, z0 + rise - 0.02)]
    for n in range(2, last + 1):
        saw += [(R(n), z0 + rise * (n - 1) - 0.02), (R(n), z0 + rise * n - 0.02)]
    saw += [(yn1, z0 + rise * last - 0.02), (yn1, Zs(yn1)), (y_fl, z0), (yn0, z0)]
    sp.prism([(XS, y, z) for y, z in saw], (X_OPEN - XS, 0, 0), WHITE, grain=1)
    ctx.add(sp.finish('stairs2.string'), ROOM, 'joinery')

    # ---- wall side: string with its sweep over the winders, dado, greige band -------------------------------
    ws = mo.MB()
    Sz = lambda y: NL(y) + STRING_H                                  # top of the wall string on the rake
    yq = R(ns)                                                       # 8.13: the winders start
    ws.sweep(SP.WALL_STRING, [(X_WALL, y_arch, Sz(y_arch)), (X_WALL, yq, Sz(yq))], WHITE)
    # Over the winders (v4 f_0320, f_0333-f_0344): the top edge carries on up the rake, eases over at the internal
    # corner and runs on in a shallow S along the old rear wall to a level bull-nosed capping block at the landing.
    ya, za = yq + 0.27, Sz(yq + 0.27)
    L = yw - ya
    east = [(yq, Sz(yq))] + [(ya + L * t, za + slope * L * t - (slope - 0.2) * L * t * t / 2) for t in (0, .25, .5, .75, 1)]
    zc_s, zt_s, x_cap = east[-1][1], z2 + 0.17, 0.46                 # string top at the corner / at the landing skirting
    north = [(X_WALL - (X_WALL - x_cap) * t, zc_s + (zt_s - zc_s) * (1 - math.cos(math.pi * t)) / 2)
             for t in (0, 1 / 6, 2 / 6, 3 / 6, 4 / 6, 5 / 6, 1)]
    x_end = xj - 0.02                                                # covers the end of the landing skirting
    top = [(0.030, -0.045)] + SP.WALL_STRING[1:]                     # the beaded top edge alone
    ws.sweep(top, [(X_WALL, y, z) for y, z in east] + [(x, yw, z) for x, z in north[1:]] + [(x_end, yw, zt_s)], WHITE)
    zw1, zw2, zw3 = (z0 + rise * n - 0.02 for n in (ns, ns + 1, ns + 2))     # just under winders 1-3
    y11, x12 = S['winders']['risers'][0]['line'][1][1], S['winders']['risers'][1]['line'][1][0]    # 8.59 / 0.55
    ws.prism([(X_WALL, y, z - 0.04) for y, z in east] + [(X_WALL, yw, zw2), (X_WALL, y11, zw2), (X_WALL, y11, zw1),
                                                         (X_WALL, yq, zw1)], (-0.0295, 0, 0), WHITE, grain=1)
    ws.prism([(x, yw, z - 0.04) for x, z in north] + [(x_end, yw, zt_s - 0.04), (x_end, yw, zw3), (x12, yw, zw3),
                                                      (x12, yw, zw2), (X_WALL, yw, zw2)], (0, -0.0295, 0), WHITE, grain=0)
    ws.box((x_end, yw - 0.045, zt_s), (x_cap, yw, zt_s + 0.04), WHITE, bev=0.012)       # capping block
    # Dado (v4 f_0192, f_0345-f_0353): one straight rake from the bathroom architrave, a knee to level over the
    # winders, the valley at the corner, then raking up the old rear wall to the level rail of the landing.
    ph = mo.profile_size('dado_landing')[1]
    dado = [(ph - h, p) for p, h in mo.PROFILES['dado_landing']]     # in the wall plane: (down from the top, off the wall)
    D = lambda y: NL(y) + DADO_H
    # Round 3: level run at 6.60 (v13 t4 rectified on N1: the north rail falls 0.57 per metre from the landing rail,
    # so 0.38 over the 0.67 wall; the east-wall run from the corner is level by its vanishing point, knee about 0.33
    # south of the corner).  Not "level on the north wall" as the survey note has it: v13 t4 and v4 f_0348-f_0352
    # both show the north rail raking and the east run level.
    # Fixer round 3: the hall rail turns the external corner (xj, yw) in a mitre, runs 0.08 level on the north wall
    # and knees down there (v13 t4 full-res, rectified on N1: corner and knee at the same height, 0.08-0.09 apart;
    # 0.60-0.65 per metre after the knee), so the level run is 6.63 (0.38 fall, as measured in round 3).
    zc, zt = z2 + 0.61, z2 + mo.TRIM['landing2_head']['dado']['top']         # level over the winders 6.63 / landing 7.01
    yk = inv(zc - DADO_H)                                            # knee (8.26)
    x_k, x_m = xj + 0.08, xj + 0.04                                  # knee / butt of the corner piece and the rake
    sn = (zt - zc) / (X_WALL - x_k)
    kn = math.hypot(1, sn)
    ws.sweep(dado, [(X_WALL, y_arch, D(y_arch)), (X_WALL, yk, zc), (X_WALL, yw, zc)], WHITE, up=(-1, 0, 0),
             ends=((0, 0, -k), None))
    ws.sweep(dado, [(X_WALL, yw, zc), (x_k, yw, zt), (x_m, yw, zt)], WHITE, up=(0, -1, 0), ends=((0, 0, -kn), None))
    # corner piece in the shell's own section and set-out (plumb, up +Z, room on the left): its end rings match the
    # rake's level stub at x_m and the hall rail, whose end is slid from yw to yw + 0.04 to make room for the mitre
    ws.sweep(mo.PROFILES['dado_landing'], [(x_m, yw, zt - ph), (xj, yw, zt - ph), (xj, yw + 0.04, zt - ph)], WHITE)
    cut_back('landing2_head.dado', lambda w: w.x > xj - 0.05 and abs(w.y - yw) < 0.003, yw + 0.04)
    ctx.add(ws.finish('stairs2.wall_string'), ROOM, 'trim')

    # greige band, 1.5 mm proud of the plaster, in the landing's lower paint (a core repaint of the hall dado zone,
    # survey #C0B9AD, follows here)
    gb, paint, e = mo.MB(), shell.material(shell.finish('landing2_head')['lower']), 0.0015
    gb.face([(X_WALL - e, y, z - 0.03) for y, z in [(y_arch, Sz(y_arch))] + east + [(yw, zc), (yk, zc), (y_arch, D(y_arch))]],
            paint, hint=(-1, 0, 0))
    gb.face([(x, yw - e, z - 0.03) for x, z in north + [(xj, zt_s), (xj, zt), (x_k, zt), (X_WALL, zc)]],
            paint, hint=(0, -1, 0))
    band = gb.finish('stairs2.dado_band')
    M.uv_box(band)
    ctx.add(band, ROOM, 'trim')

    # ---- ceiling of the well: the landing cove turns the external corner (0.32, 8.73) and runs along the old rear
    # wall into the staircase wall, which has only a thin shadow bead (landing2.md 3; v5 f_0153, v4 f_0369).  The
    # short return north overlaps the end of landing2_head.cornice by 2 mm so the mitre closes on it.
    cz = ctx.ceil_z('landing2_head')
    cove = mo.PROFILES[mo.TRIM['landing2_head']['cornice']['profile']]
    tb = mo.MB()
    tb.sweep(cove, [(X_WALL + 0.005, yw, cz), (xj, yw, cz), (xj, yw + 0.002, cz)], 'plaster_white')
    tb.sweep([(d * 0.18, h * 0.18) for d, h in cove], [(X_WALL, y_well - 0.005, cz), (X_WALL, yw - 0.01, cz)],
             'plaster_white')
    ctx.add(tb.finish('stairs2.cornice'), ROOM, 'trim')

    # ---- balustrade of the flight -------------------------------------------------------------------------
    # Newel 1.38 high, not the spec's 1.20: the rail (0.90 above the nosing line) is 1.19 above the landing
    # where it enters the block, and the ball stands at camera height in v4 f_0192.
    post = newel('stairs2.newel', 0.27, 1.03)
    post.location = (fx, fy, z0)
    U = lambda y: NL(y) + RAIL_H - 0.055 * k                         # underside of the handrail
    # With the reconciled levels the platform apron (underside 5.75) crosses the rail line 0.6 m before the turning
    # newel: the rail dies into it there, as it does at the newel in v4 f_0171.
    y_die = inv(zb_ap - RAIL_H + 0.055 * k) + 0.03
    hb = mo.MB()
    hb.sweep(SP.handrail(k), [(X_RAIL, yn0 - 0.005, U(yn0 - 0.005)), (X_RAIL, y_die, U(y_die))], wood())
    rail = hb.finish('stairs2.handrail')
    bal = _Balusters()
    for n in range(1, last + 1):                                     # two per tread (v4 f_0178)
        for dy, base in ((0.045, 0.20), (0.16, 0.30)):
            y = R(n) + dy
            if yn0 + 0.03 < y < yn1 - 0.03:
                h = min(U(y) + 0.02, zb_ap + 0.005) - (z0 + rise * n)
                bal.add(f'stairs2.spindle.{len(bal.out):02d}', (X_SP, y, z0 + rise * n), h, base, 0.15)
    for ob in (post, rail, *bal.done()):
        ctx.add(ob, ROOM, 'joinery', lm='dynamic')

    # ---- platform balustrade over the well (v_platform_well; v5 f_0140, v4 f_0361) ----------------------------
    PL = 'landing2_platform'
    # No drop below the string: the newel straddles the quarter-landing edge (R10, y 8.13), and a drop would hang
    # 0.37 out of the QL ceiling (5.35) beside its vault (none in v6 f_0033, v3 f_0029).  It starts just above that
    # ceiling; only its south half (over T9) carries on down into the T9 carcass, 2 mm behind the R10 riser plane.
    zt0, h = max(Zs(yn1) - 0.06, ctx.ceil_z('landing1_ql') + 0.002), NEWEL_S / 2
    zt9 = z0 + rise * (ns - 1)                                       # T9 top (5.22)
    # Block top 0.96 above the platform, level with the rail top (c_v5_139_bal, v13 t47.5); ball top 1.10 (survey
    # 1.05, v13 t47.5 measured 1.06 on the 0.20 riser).
    turn = newel('landing2_platform.newel', z2 + 0.28 - zt0, zp + 0.75 - zt0,
                 foot=((-h, -h, min(0.0, zt9 - 0.03 - zt0)), (h, R(ns) - 0.002 - ty, 0.001)))
    turn.location = (tx, ty, zt0)
    pb = mo.MB()
    pb.box((X_OPEN, y_well, zb_ap), (X_APRON, yn1, zp - 0.001), WHITE, bev=0.003)               # apron
    pb.box((X_APRON, y_well, zb_ap), (X_WALL, y_well + 0.015, zp - 0.001), WHITE, bev=0.003)    # the same band on the trimmer
    pb.box((X_OPEN - 0.012, y_well, zp), (X_APRON + 0.012, yn1, zp + 0.035), WHITE, bev=0.006)  # capping under the spindles
    pb.box((X_APRON + 0.012, y_well, zp), (X_WALL, y_well + 0.027, zp + 0.035), WHITE, bev=0.006)
    zr = zp + 0.95 - 0.055                                           # underside of the rail, top 0.95 above the platform
    hb = mo.MB()
    hb.sweep(SP.handrail(1), [(X_RAIL, yn1 + 0.005, zr), (X_RAIL, y_well - 0.01, zr)], wood())
    prail = hb.finish('landing2_platform.handrail')
    bal = _Balusters()
    cnt = int((yn1 - y_well - 0.13) / 0.09) + 1
    for i in range(cnt):                                             # ~90 mm centres
        y = yn1 - 0.07 - i * (yn1 - y_well - 0.13) / (cnt - 1)
        bal.add(f'landing2_platform.spindle.{i:02d}', (X_SP, y, zp + 0.035), zr + 0.02 - zp - 0.035)
    ctx.add(pb.finish('landing2_platform.apron'), PL, 'joinery')
    for ob in (turn, prail, *bal.done()):
        ctx.add(ob, PL, 'joinery', lm='dynamic')

    # ---- level balustrade on the first-floor strip (v_strip_well; landing1.md 5.1, v4 f_0181-f_0190) -------------
    # From the top newel of the main flight (0.20, 8.13; built by rooms/stairs.py) the rail runs level 0.90 over the
    # strip, then knees DOWN and falls more gently than the stair until it dies into the underside of the outer
    # string (landing1.md says "ramps up"; v4 f_0183 shows the bend steeper below the knee, which only a falling
    # ramp gives from that camera).  South of that the string is the guard, the spindles under it get shorter; the
    # capping and the spindle feet step down with the two steps to the rear level (y 7.88..8.13).
    zu, y_kn, fall = z0 + 0.90 - 0.055, 7.32, 0.70                   # rail underside on the level; knee; ramp fall
    under = lambda y: zu - fall * max(0.0, y_kn - y)
    y_end = y_kn
    while under(y_end) + 0.055 < Zs(y_end) + 0.01:                   # the rail top runs 10 mm into the string
        y_end -= 0.005
    hb = mo.MB()
    hb.sweep(SP.handrail(1), [(X_RAIL, yn1 - 0.005, zu), (X_RAIL, y_kn, zu), (X_RAIL, y_end, under(y_end))], wood())
    grail = hb.finish('stairs2.strip_handrail')
    fz = lambda y: ctx.floor_z('landing1_front', X_RAIL - 0.2, y)    # strip floor: 3.42, the steps 3.23 / 3.04
    # capping on the floor edge, and under it a white fascia on the well side that steps down with it: the main
    # flight's handrail dies into its underside short of the top newel (v6 f_0038; rooms/stairs.py), so the main rail
    # and spindles stay under the strip guard instead of running through it.
    gp, ya = mo.MB(), y_fl
    for yb in sorted({y_fl, yn1} | {y for _, y in ctx.stair('steps_rear_front')['riserLines'][1][:1]}):
        if yb > ya:
            z = fz((ya + yb) / 2)
            gp.box((X_OPEN - 0.015, ya, z), (X_CAP, yb, z + 0.03), WHITE, bev=0.006)
            gp.box((X_OPEN, ya, z - SP.STRIP_FASCIA), (X_CAP, yb, z - 0.0005), WHITE, bev=0.003)
            ya = yb
    bal, y = _Balusters(), yn1 - 0.075
    while True:
        base = fz(y) + 0.03
        h = min(under(y) + 0.02, Zs(y) + 0.004) - base
        if h < 0.05:
            break
        bal.add(f'stairs2.strip_spindle.{len(bal.out):02d}', (X_SP, y, base), h)
        y -= 0.11
    ctx.add(gp.finish('stairs2.strip_capping'), ROOM, 'joinery')
    for ob in (grail, *bal.done()):
        ctx.add(ob, ROOM, 'joinery', lm='dynamic')

    # ---- the cat studies (stairs2.md 7; landing2.md 7 N1 / N2 are C5 / C4) ----------------------------------------
    # C1-C3 step up the staircase wall 1.40 above the nosing line, C4 (N2, lying tabby) on the same wall just south of
    # the corner, C5 (N1, sitting cat) centred on the old rear wall.  Brushed pale-gold frame, white mount, burgundy
    # band.  Round 3: 0.45 x 0.35 (survey; C1 aspect 1.29 in v4 f_0196), band 0.31 x 0.21 (C1: 0.68 / 0.60 of the
    # frame); N1 centred on the wall, 1.45 above the landing (v13 t4 rectified: 0.15 / 0.45 / 0.16 along the wall);
    # N2 at y 8.35 (its north edge 0.15 from the corner), 1.12 above the landing (survey: 0.35 under N1; v13 t4: 0.38
    # above the level dado).  C1 2 cm off the bathroom architrave, top kept 5 cm over the architrave head (v4 f_0196).
    W, Hc = 0.45, 0.35
    cats = [(1, (X_WALL, y_arch + 0.02 + W / 2, NL(6.35) + PRINT_H + 0.235 - Hc / 2), (-1, 0)),
            (2, (X_WALL, 7.05, NL(7.05) + PRINT_H), (-1, 0)),
            (3, (X_WALL, 7.75, NL(7.75) + PRINT_H), (-1, 0)), (4, (X_WALL, 8.35, z2 + 1.12), (-1, 0)),
            (5, ((xj + X_WALL) / 2, yw, z2 + 1.45), (0, -1))]
    for i, loc, facing in cats:
        pic = P.framed_picture(image=str(ART / f'stairs2_cat{i}.jpg'), w=W, h=Hc, frame_style='champagne',
                               frame_w=0.02, depth=0.018, mount=0.052, slip=('#5B2A30', 0.012), mount_mat='#F1F0EC',
                               glass=True, name=f'stairs2.cat.{i}')
        ctx.add(P.place(pic, loc, facing=facing), ROOM, 'decor')

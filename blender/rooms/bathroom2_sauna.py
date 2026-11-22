"""bathroom2 sauna: free-standing one-person spruce cabin, called by rooms/bathroom2.py.

Round 3 (spec/phase3/floor2_a.md, bathroom layout; brief spec/phase3/briefs/bathroom2.md): the maker's cabin, 1.366 x
0.753 x 2.02 (Oceanic one-person "1020"), in the room's local frame x 1.254..2.62, y 1.23..1.983: front 1.23 from the
south wall (level with the north window jamb), 0.055 clear of the north wall, 0.06 of the window wall, 0.07 strip to the
shower. Front: west corner post + five-board panel (0.62), grey glass door 0.60 (two chrome hinges on its east edge,
opens out), post 0.15. Inside 1.28 x 0.66 (v13 t87): bench along the whole east wall (0.50, seven slats N-S, top 0.45),
three-slat backrest, one batten on the north wall; heater with its control unit on the west wall at mid depth in a
two-rail guard; sliding vent on the north wall 0.40 from the NE corner; white sensor on the east wall; round thermometer
on the front wall east of the door; coved fillets; dark grey mat; bucket and ladle on the bench (v13 f82-f105).
Walk: the cabin is a pen (docs/js/geom.js PENS): the door leaf `bathroom2.sauna.door` (one object: glass, hinges, both
handles) lies within 0.07 of the carcass outline, so the viewer opens the outline there; nothing inside blocks.
"""
import random

from lib import interact as IX, lighting, materials as M, mouldings as mo, props as P
from rooms import bathroom2_tex as TX

ROOM = 'bathroom2'
FZ = 6.02
L, D, H = 1.366, .753, 2.02                # maker's size
T = .045                                   # wall: (1.366 - 1.28) / 2 and (0.753 - 0.66) / 2
IH = 1.93                                  # clear inside height
BT = .018                                  # board thickness (outer boards and inner lining)
# set by build() from the room's SW corner
SX0 = SX1 = SY0 = SY1 = DX0 = DX1 = 0.0
# untreated flat-sawn spruce, cathedral grain and pin knots (rooms/bathroom2_tex.py, v13 t76 / t86 / t87): the generated
# images keep the mean tones tuned in round 3 (the library's oak_light renders orange-brown here). Inside, the near-closed
# timber box multiplies the albedo's saturation through inter-reflection, so the lining is greyer to render the pale ash
# of v13 t87 / t97. TW = outer boards, posts and capping; TL = inner lining; TI = benches, guard, vent, bucket, ladle.
TI_HEX = '#D9CEB2'                         # the door's inside bar (solid, too small for grain)
TW = TL = TI = None                        # set at build time (materials need bpy)


def z(h):
    return FZ + h


def boards(mb, lo, hi, n, axis, grain=2, bev=.0025, mat=None):
    """n tongue-and-groove boards side by side along `axis` (chamfered edges read as the V joints); every box gets its
    own UV offset from mouldings.MB, so each board shows another part of the grain image."""
    a, b = lo[axis], hi[axis]
    for i in range(n):
        p, q = list(lo), list(hi)
        p[axis], q[axis] = a + (b - a) * i / n, a + (b - a) * (i + 1) / n
        mb.box(tuple(p), tuple(q), mat or TW, bev=bev, grain=grain)


def build(ctx, x0, y0, y1, fz):
    """x0, y0: the room's SW inside corner (the survey's local origin); y1: north wall face; fz: floor Z."""
    global TW, TL, TI, FZ, SX0, SX1, SY0, SY1, DX0, DX1
    FZ = fz
    SX1 = x0 + 2.62
    SX0, SY0 = SX1 - L, y0 + 1.23
    SY1 = SY0 + D
    DX0, DX1 = SX0 + .616, SX0 + 1.216          # glass door span (corner post + five boards, 0.60 glass, 0.15 post)
    TW, TL, TI = TX.spruce('out'), TX.spruce('in'), TX.spruce('ti')
    add = lambda ob, kind='fit', **kw: ctx.add(ob, ROOM, kind, **kw)
    xi0, xi1, yi0, yi1 = SX0 + T, SX1 - T, SY0 + T, SY1 - T     # clear inside faces (1.276 x 0.663)
    zt = z(H - .09)                                              # under the capping (90 high)
    ja, jb = DX0 + .025, DX1 - .025                              # clear door opening 0.55: the glass laps the jambs

    # ---------------------------------------------------------------- carcass (one mesh: the pen outline)
    mb = mo.MB()
    for px, py in ((SX0, SY0), (SX1 - .06, SY0), (SX0, SY1 - .06), (SX1 - .06, SY1 - .06)):   # corner posts
        mb.box((px, py, z(.045)), (px + .06, py + .06, zt), TW, bev=.004, grain=2)
    o = .004                                                     # outer boards 4 mm behind the post faces
    boards(mb, (SX0 + .06, SY0 + o, z(.045)), (DX0 - .02, SY0 + o + BT, zt), 5, 0)         # front panel, five boards
    boards(mb, (DX1 + .02, SY0 + o, z(.045)), (SX1 - .06, SY0 + o + BT, zt), 1, 0)         # board beside the door
    boards(mb, (SX0 + o, SY0 + .06, z(.045)), (SX0 + o + BT, SY1 - .06, zt), 6, 1)         # west side
    boards(mb, (SX1 - o - BT, SY0 + .06, z(.045)), (SX1 - o, SY1 - .06, zt), 6, 1)         # east side
    boards(mb, (SX0 + .06, SY1 - o - BT, z(.045)), (SX1 - .06, SY1 - o, zt), 12, 0)        # back
    for a, b in (((SX0, SY0 - .006, FZ), (SX1, SY0 + .03, z(.045))),                       # base batten 45 high
                 ((SX0, SY1 - .03, FZ), (SX1, SY1 + .006, z(.045))),                       # (front one = door sill)
                 ((SX0 - .006, SY0 + .03, FZ), (SX0 + .03, SY1 - .03, z(.045))),
                 ((SX1 - .03, SY0 + .03, FZ), (SX1 + .006, SY1 - .03, z(.045)))):
        mb.box(a, b, TW, bev=.004, grain=None)
    mb.box((SX0 + .02, SY0 + .02, zt), (SX1 - .02, SY1 - .02, z(H - .012)), TW, grain=1)   # roof board
    for a, b in (((DX0 - .02, SY0, z(.045)), (ja, yi0, z(1.90))),                          # door frame: jambs, head
                 ((jb, SY0, z(.045)), (DX1 + .02, yi0, z(1.90))),
                 ((DX0 - .02, SY0, z(1.90)), (DX1 + .02, yi0, z(1.98)))):
        mb.box(a, b, TW, bev=.004, grain=2)
    # inside lining, boards to the floor (the room's tiles are the cabin floor), ceiling boards along y
    boards(mb, (xi0 - BT, yi0, FZ), (xi0, yi1, z(IH)), 7, 1, mat=TL)
    boards(mb, (xi1, yi0, FZ), (xi1 + BT, yi1, z(IH)), 7, 1, mat=TL)
    boards(mb, (xi0, yi1, FZ), (xi1, yi1 + BT, z(IH)), 13, 0, mat=TL)
    boards(mb, (xi0, yi0 - BT, FZ), (ja, yi0, z(IH)), 6, 0, mat=TL)
    boards(mb, (jb, yi0 - BT, FZ), (xi1, yi0, z(IH)), 1, 0, mat=TL)
    boards(mb, (ja, yi0 - BT, z(1.98)), (jb, yi0, z(IH)), 1, 0, mat=TL)                 # over the door
    boards(mb, (xi0 - BT, yi0 - BT, z(IH)), (xi1 + BT, yi1 + BT, z(IH + BT)), 13, 0, grain=1, mat=TL)
    r = .022                                                     # coved (quarter-round) fillets at the ceiling
    for a, b in (((xi0, yi0, z(IH - r)), (xi0 + r, yi1, z(IH))), ((xi1 - r, yi0, z(IH - r)), (xi1, yi1, z(IH))),
                 ((xi0, yi1 - r, z(IH - r)), (xi1, yi1, z(IH))), ((xi0, yi0, z(IH - r)), (xi1, yi0 + r, z(IH)))):
        mb.box(a, b, TI, bev=.009, grain=None)
    add(mb.finish(f'{ROOM}.sauna'), plan_sym='sauna')
    # rounded capping 90 high oversailing 20 (v13 t77): front / back full length, sides between
    cap = P.place(_b2_capping(SX1 - SX0, SY1 - SY0, name=f'{ROOM}.sauna.capping'), (SX0, SY0, zt))
    M.uv_box(cap, rotate=True)                                   # grain along the capping (horizontal)
    add(cap)

    # ---------------------------------------------------------------- grey glass door, hinged on its east edge
    gy = SY0 - .012                                              # glass centre plane, outside the frame
    door = P.place(_b2_sauna_door(DX1 - DX0, TI_HEX, name=f'{ROOM}.sauna.door'), (DX1, gy, FZ))
    IX.tag(door, 'hinge', g=f'{ROOM}.sauna.door', label='Sauna door', p=(DX1, gy, FZ), deg=95)   # 100 hits the boxing
    add(door, lm='dynamic')

    # ---------------------------------------------------------------- heater (W wall, mid depth): body, rocks, control
    yc, hw, dp = (yi0 + yi1) / 2, .20, .25
    mb = mo.MB()                                                 # black body z 0.32..0.72, open rock tray on top
    mb.box((xi0 + .004, yc - hw, z(.32)), (xi0 + dp, yc + hw, z(.72)), 'black_matt', bev=.02)
    for a, b in (((xi0 + .004, yc - hw, z(.72)), (xi0 + dp, yc - hw + .012, z(.75))),
                 ((xi0 + .004, yc + hw - .012, z(.72)), (xi0 + dp, yc + hw, z(.75))),
                 ((xi0 + .004, yc - hw, z(.72)), (xi0 + .016, yc + hw, z(.75))),
                 ((xi0 + dp - .012, yc - hw, z(.72)), (xi0 + dp, yc + hw, z(.75)))):
        mb.box(a, b, 'steel_brushed', bev=.003)
    gx = xi0 + dp + .05                                          # timber guard: two rails on two corner posts
    for s in (-1, 1):
        y = yc + s * (hw + .045)
        mb.box((gx, y - .02, FZ), (gx + .04, y + .02, z(.70)), TI, bev=.004, grain=2)
    for zr in (.40, .60):
        mb.box((gx, yc - hw - .065, z(zr)), (gx + .02, yc + hw + .065, z(zr + .055)), TI, bev=.003, grain=1)
        for s in (-1, 1):
            y = yc + s * (hw + .045)
            mb.box((xi0, y - .01, z(zr)), (gx, y + .01, z(zr + .055)), TI, bev=.003, grain=0)
    add(mb.finish(f'{ROOM}.sauna.heater'), plan_sym='heater')     # blocks inside the walk-in cabin (pen)
    add(P.place(_b2_rocks(seed=3, name=f'{ROOM}.sauna.rocks'), (xi0 + .127, yc, z(.70))), 'decor')
    # control unit z 0.20..0.32: brushed stainless housing, white fascia with display, buttons, rocker, blank label
    mb = mo.MB()
    fx = xi0 + dp - .008
    mb.box((xi0 + .004, yc - hw, z(.20)), (fx, yc + hw, z(.32)), 'steel_brushed', bev=.004)
    mb.box((fx, yc - .10, z(.215)), (fx + .002, yc + .02, z(.305)), 'plastic_white')
    for k in range(4):
        y = yc - .085 + k * .03
        mb.tube([(fx + .002, y, z(.235)), (fx + .006, y, z(.235))], .0055,
                P.mat('plastic_dark') if k else M.solid('bathroom2_btn', '#3A6FC4', .4), n=10)
    mb.box((fx + .002, yc - .057, z(.272)), (fx + .003, yc - .023, z(.296)), 'black_gloss')
    mb.box((fx, yc - .185, z(.24)), (fx + .012, yc - .165, z(.285)), 'black_matt', bev=.002)      # rocker
    mb.box((fx, yc + .065, z(.225)), (fx + .0015, yc + .175, z(.305)), M.solid('bathroom2_label', '#E6E4DC', .6))
    ctrl = add(mb.finish(f'{ROOM}.sauna.control'), lm='dynamic')
    mb = mo.MB()
    mb.box((fx + .0031, yc - .054, z(.275)), (fx + .0036, yc - .026, z(.293)), P.emissive('#FF3A1E', 3.0))
    disp = add(mb.finish(f'{ROOM}.sauna.display'), 'light', lm='dynamic')

    # ---------------------------------------------------------------- the one light, near the NW corner
    lx, ly = xi0 + .22, yi1 - .20
    lighting.downlight(ctx, ROOM, lx, ly, z=z(IH) - .02, watts=22, kelvin=3000, spot_deg=140, name=f'{ROOM}.sauna.lamp')
    lamp = add(P.place(P.downlight(.07, .04, trim='chrome', name=f'{ROOM}.sauna.light'), (lx, ly, z(IH))), 'light',
               lm='dynamic')
    IX.tag_many([ctrl, disp, lamp], 'lamp', g=f'{ROOM}.sauna', label='Sauna')

    # ---------------------------------------------------------------- bench along the whole east wall, backrest, batten
    mb = mo.MB()
    bx0, n, sw = xi1 - .50, 7, .058
    gap = (.50 - n * sw) / (n - 1)
    for k in range(n):                                           # seven slats running north-south, top z 0.45
        x = bx0 + k * (sw + gap)
        mb.box((x, yi0 + .004, z(.428)), (x + sw, yi1 - .004, z(.45)), TI, bev=.004, grain=1)
    for y in (yi0 + .03, yi1 - .07):                             # bearers under the slats, on the east wall
        mb.box((bx0 + .02, y, z(.37)), (xi1, y + .04, z(.428)), TI, bev=.003, grain=0)
    mb.box((bx0, yi0 + .006, z(.33)), (bx0 + .022, yi1 - .006, z(.428)), TI, bev=.003, grain=1)   # front apron
    for y in (yi0 + .03, yi1 - .07):                             # two legs at the front edge
        mb.box((bx0 + .022, y, FZ), (bx0 + .062, y + .04, z(.37)), TI, bev=.003, grain=2)
    for y in (yi0 + .10, yi1 - .12):                             # backrest: spacers, three slats z 0.80..1.10
        mb.box((xi1 - .025, y, z(.78)), (xi1, y + .045, z(1.12)), TI, bev=.003, grain=2)
    for zz in (.80, .91, 1.02):
        mb.box((xi1 - .047, yi0 + .06, z(zz)), (xi1 - .025, yi1 - .06, z(zz + .08)), TI, bev=.004, grain=1)
    mb.box((bx0, yi1 - .022, z(.77)), (xi1, yi1, z(.83)), TI, bev=.003, grain=0)      # batten on the north wall
    add(mb.finish(f'{ROOM}.sauna.seat'), plan_sym='bench')        # blocks inside the walk-in cabin (pen)

    # bucket (staved spruce pail, wooden inside down to its bottom disc, no liner: v13 t86 / t87) and long-handled ladle
    # on the bench, front (door) end
    bx, by = bx0 + .14, yi0 + .15
    add(P.place(P.lathe([(0, 0), (.088, 0), (.11, .19), (.10, .19), (.081, .014), (0, .014)], 16, TI,
                        name=f'{ROOM}.sauna.bucket'), (bx, by, z(.45))), 'decor')
    add(P.place(P.lathe([(.1, 0), (.106, 0), (.108, .02), (.102, .02)], 16, TI, name=f'{ROOM}.sauna.bucket.hoop'),
                (bx, by, z(.59))), 'decor')
    add(P.place(_b2_ladle(name=f'{ROOM}.sauna.ladle'), (bx - .02, by - .01, z(.56)), rot_z=30), 'decor')

    # sand timer on the inside of the front panel (flips), thermometer east of the door, sensor, vent
    tx = (xi0 + ja) / 2
    st = P.place(_b2_timer(name=f'{ROOM}.sauna.timer'), (tx, yi0, z(1.45)), facing=(0, 1))
    IX.tag(st, 'hinge', label='Sand timer', p=(tx, yi0 + .02, z(1.45)), a=(0, 1, 0), deg=180)
    add(st, 'decor', lm='dynamic')
    add(P.place(_b2_gauge(name=f'{ROOM}.sauna.gauge'), ((jb + xi1) / 2, yi0, z(1.75)), facing=(0, 1)), 'decor')
    add(P.place(_b2_sensor(name=f'{ROOM}.sauna.sensor'), (xi1, yi1 - .15, z(1.80)), facing=(-1, 0)), 'fit')
    mb = mo.MB()                                                 # vent slot + guides on the north wall
    vx = xi1 - .40
    mb.box((vx - .10, yi1 - .001, z(1.715)), (vx + .10, yi1, z(1.785)), 'black_matt')
    for zz in (1.685, 1.80):
        mb.box((vx - .14, yi1 - .016, z(zz)), (vx + .24, yi1, z(zz + .015)), TI, bev=.002, grain=0)
    add(mb.finish(f'{ROOM}.sauna.vent'))
    mb = mo.MB()
    mb.box((vx - .125, yi1 - .014, z(1.70)), (vx + .125, yi1 - .002, z(1.80)), TI, bev=.002, grain=0)
    mb.tube([(vx - .09, yi1 - .014, z(1.75)), (vx - .09, yi1 - .03, z(1.75))], .007, TI, n=8)
    hatch = mb.finish(f'{ROOM}.sauna.vent.hatch')
    IX.tag(hatch, 'slide', label='Sauna vent', d=(.10, 0, 0))
    add(hatch, lm='dynamic')

    # dark grey mat on the tiles inside (v13 t87, #6E6F6E); white isolator on the wall above the cabin (v5 f_0104)
    add(P.place(P.rug(None, xi1 - xi0 - .02, yi1 - yi0 - .02, thickness=.006, color='#6E6F6E', name=f'{ROOM}.sauna.mat'),
                ((xi0 + xi1) / 2, (yi0 + yi1) / 2, FZ)), 'decor')
    ix_ = SX0 + .92
    add(P.place(P.switch_plate(1, 'rocker', name=f'{ROOM}.sauna.isolator'), (ix_, y1 - .035, z(2.18)),
                facing=(0, -1)), 'fit')
    add(P.place(P.box(.086, .035, .086, 'plastic_white', name=f'{ROOM}.sauna.isolator.box'),
                (ix_, y1 - .0175, z(2.137)), facing=(0, -1)), 'fit')


# ----------------------------------------------------------------------------- parts
@P._prop
def _b2_capping(b, w, d):
    """Capping round the cabin top, 90 high, oversailing 20 mm, rounded edges (origin: SW corner of the cabin at the
    capping underside)."""
    c, h, r = .02, .09, .025
    m = TW
    b.add(P._box_round((-c, -c, 0), (w + c, .075, h), r, 3), m, True, closed=True)
    b.add(P._box_round((-c, d - .075, 0), (w + c, d + c, h), r, 3), m, True, closed=True)
    for x0, x1 in ((-c, .075), (w - .075, w + c)):
        b.add(P._box_round((x0, .06, 0), (x1, d - .06, h - .004), r, 3), m, True, closed=True)


@P._prop
def _b2_sauna_door(b, w, timber_hex):
    """Frameless light smoky-grey glass door 8 mm (about half the light passes: window, plant and bench read through it
    in v13 f_0076, t76, t77), origin on the hinge (east) edge at floor level, pane toward -X, outside -Y:
    glass z 0.08..1.92, two chrome clamp hinges on the hinge edge (z 0.30, 1.70), a vertical chrome cylinder handle
    dia 30 x 0.25 outside on two stand-offs and a turned timber bar inside, both 75 mm from the free edge, z 1.0."""
    x0, z0, z1 = -w, .08, 1.92
    b.add(P.G([(x0, 0, z0), (0, 0, z0), (0, 0, z1), (x0, 0, z1)], [(0, 1, 2, 3)]),
          M.solid('bathroom2_sauna_glass', '#5F5C57', .03, alpha=.45))
    vs = [(x, s * .004, zz) for x, zz in ((x0, z0), (0, z0), (0, z1), (x0, z1)) for s in (-1, 1)]
    b.add(P.G(vs, [(2 * i, 2 * i + 1, (2 * i + 3) % 8, (2 * i + 2) % 8) for i in range(4)]), P.two_sided('glass_green'))
    for zh in (.30, 1.70):
        b.add(P._box_round((-.055, -.012, zh - .035), (.03, .012, zh + .035), .004, 1), 'chrome', True, closed=True)
    xh = x0 + .075
    for s, rr, mat in ((-1, .015, 'chrome'), (1, .015, M.solid('bathroom2_spruce_' + timber_hex[1:], timber_hex, .7))):
        yb = s * (.004 + .035)
        for zz in (.90, 1.10):                                   # stand-offs through the glass
            b.add(P._tube([(xh, 0, zz), (xh, yb, zz)], .006, 8), 'chrome', True, closed=True)
        b.add(P._tube([(xh, yb, .875 if s < 0 else .85), (xh, yb, 1.125 if s < 0 else 1.15)], rr, 12), mat, True,
              closed=True)


@P._prop
def _b2_sensor(b):
    """White slotted temperature sensor 0.05 x 0.08 (wall prop, front -Y): body with two rows of slots (v13 t97)."""
    b.add(P._box_round((-.025, -.022, -.04), (.025, 0, .04), .004, 1), 'plastic_white', True, closed=True)
    for zz in (.018, .03):
        for k in range(3):
            x = -.016 + k * .016
            b.add(P._box((x - .005, -.0225, zz - .003), (x + .005, -.0215, zz + .003)), 'plastic_dark', closed=True)


@P._prop
def _b2_rocks(b, seed=3):
    """Heap of 27 large angular heater stones, 0.07-0.11 across, pale grey with white speckle, crowning a little
    above the tray rim (v13 t86, t87, t105). Origin: tray centre, 20 mm under the body top (tray floor at z 0.02, rim
    z 0.05). Each stone is a 6 x 4 sphere, stretched, its vertices jittered and cut by two or three flat planes;
    flat-shaded, so the facets read as broken stone (36 tris each)."""
    rnd = random.Random(seed)
    mats = (TX.stone(0), TX.stone(1))
    ax, ay = .111, .188                                          # tray half-size inside the steel walls
    spots = []
    for i in range(12):                                          # bottom layer: 3 x 4 on the tray floor
        spots.append((-.074 + .074 * (i % 3), -.141 + .094 * (i // 3), .0, rnd.uniform(.040, .052)))
    for i in range(10):                                          # second layer: 2 x 5 in the hollows
        spots.append((-.037 + .074 * (i % 2), -.15 + .075 * (i // 2), .025, rnd.uniform(.036, .048)))
    for i in range(5):                                           # crown, a few stones above the rim (v13 t105)
        spots.append((rnd.uniform(-.045, .045), -.11 + .055 * i, .045, rnd.uniform(.035, .045)))
    for k, (x, y, zl, r) in enumerate(spots):
        x += rnd.uniform(-.012, .012)
        y += rnd.uniform(-.012, .012)
        sx, sy, sz = rnd.uniform(1.0, 1.3), rnd.uniform(.8, 1.05), rnd.uniform(.6, .8)
        g = P._sphere(1.0, 6, 4)
        cuts = []
        for _ in range(rnd.choice((2, 3))):
            n = P.Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-.6, 1))).normalized()
            cuts.append((n, rnd.uniform(.55, .8)))
        vs = []
        for v in g.v:
            p = P.Vector((v[0] * sx, v[1] * sy, v[2] * sz)) * rnd.uniform(.85, 1.15)
            for n, dd in cuts:
                over = p.dot(n) - dd
                if over > 0:
                    p -= n * over
            vs.append(tuple(p * r))
        hx, hy = r * sx * .7, r * sy * .7
        x, y = max(-ax + hx, min(ax - hx, x)), max(-ay + hy, min(ay - hy, y))
        zc = .02 + zl + r * sz * .7
        b.add(P.G(vs, g.f, fuv=g.fuv), mats[k % 2], False, closed=True,
              T=P.Tr(x, y, zc) @ P.Rot('Z', rnd.uniform(0, 360)) @ P.Rot('X', rnd.uniform(-20, 20)))


@P._prop
def _b2_ladle(b):
    """Long-handled wooden sauna ladle: cup at the origin opening up, handle rising along +X."""
    b.add(P._lathe([(0, -.03), (.03, -.028), (.042, -.012), (.045, 0), (.04, 0), (.036, -.01), (.026, -.022),
                    (0, -.024)], 16), TI, True)
    b.add(P._tube([(.04, 0, -.005), (.20, 0, .05), (.40, 0, .11)], [.009, .008, .009], 8), TI, True, closed=True)


@P._prop
def _b2_timer(b):
    """15-minute sand timer: backboard, two posts, glass hourglass with blue sand (wall prop, front -Y, origin centre)."""
    b.add(P._box((-.032, -.012, -.135), (.032, 0, .135), .003), TI, closed=True)
    for sx in (-1, 1):
        b.add(P._box((sx * .024 - .006, -.032, -.12), (sx * .024 + .006, -.012, .12), .002), TI, closed=True)
    for zc in (-.115, .115):
        b.add(P._box((-.03, -.034, zc - .006), (.03, -.012, zc + .006), .002), TI, closed=True)
    prof = [(0, -.109), (.011, -.106), (.013, -.07), (.010, -.03), (.0025, -.004), (.0025, .004), (.010, .03),
            (.013, .07), (.011, .106), (0, .109)]
    b.add(P._lathe(prof, 12), 'glass_clear', True, T=P.Tr(0, -.022, 0))
    sand = M.solid('bathroom2_sand', '#2F64B5', .9)
    b.add(P._lathe([(0, -.106), (.0105, -.104), (.0122, -.07), (.0095, -.045), (0, -.045)], 12), sand, True,
          T=P.Tr(0, -.022, 0))


@P._prop
def _b2_gauge(b):
    """Round sauna thermometer, dial 0.12: chrome bezel, white face, black needle (wall prop, front -Y)."""
    b.add(P._lathe([(0, 0), (.06, 0), (.06, .016), (.054, .02), (.05, .016), (0, .016)], 28), 'chrome', True,
          T=P.Rot('X', 90))
    b.add(P._lathe([(0, 0), (.05, 0), (.05, .0005), (0, .0005)], 28), M.solid('bathroom2_dial', '#F2F0EA', .5), True,
          T=P.Tr(0, -.0162, 0) @ P.Rot('X', 90))
    b.add(P._box((-.002, -.019, -.008), (.002, -.0175, .04)), 'black_matt', closed=True)

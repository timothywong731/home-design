"""Basement plant / store room (room id 'basement'): boiler wall, hot-water cylinder, electrics, network cabinet,
gas meter, racking, stools, lights. Called from rooms/basement.py. spec/rooms/basement.md 5-8 (south wall y 5.19).
"""
import math

import bpy
from mathutils import Matrix

from lib import interact as IX, materials as M, mouldings as mo, props as P

RM = 'basement'
ZF = -2.31
X0, X1, Y0, Y1 = 1.25, 4.25, 5.19, 8.73          # inside faces W E S N
XB = 4.23                                        # face of the plywood backboard
# ponytail: no softwood-ply texture in the library; the yellow door oak renders nearest the filmed ply (#A79A6E)
PLY, WHITE, BLK, BRASS = 'oak_door', 'plastic_white', 'black_matt', 'brass'


def Z(h):
    return ZF + h


def C(name, hx, rough=0.5, metal=0.0):
    return M.solid('bs_' + name, hx, rough, metal)


def T(x, y, h):
    return Matrix.Translation((x, y, Z(h)))


def RX(deg):
    return Matrix.Rotation(math.radians(deg), 4, 'X')


def RY(deg):
    return Matrix.Rotation(math.radians(deg), 4, 'Y')


def pipe(mb, pts, r, mat, n=8):
    """Pipe run with square elbows: one capped bar per leg, legs lapped at the corners. pts are (x, y, h)."""
    pts = [(x, y, Z(h)) for x, y, h in pts]
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        d = [q - p for p, q in zip(a, b)]
        ln = math.sqrt(sum(c * c for c in d)) or 1.0
        u = [c / ln * r * 0.9 for c in d]
        a2 = a if i == 0 else tuple(p - c for p, c in zip(a, u))
        b2 = b if i == len(pts) - 2 else tuple(p + c for p, c in zip(b, u))
        mb.tube([a2, b2], r, mat, n)


def _add(ctx, mb, name, kind='fit', sym=None, lm=None):
    return ctx.add(mb.finish(name), RM, kind, plan_sym=sym, lm=lm)


def _wall_prop(ctx, ob, x, y, h, facing, kind='fit'):
    return ctx.add(P.place(ob, (x, y, Z(h)), facing=facing), RM, kind)


# ------------------------------------------------------------------------------------------- wall E-north
def _board(ctx):
    cu = C('copper', '#A86F45', 0.32, 1.0)
    mb = mo.MB()
    mb.box((XB, 7.05, Z(0.12)), (X1, 8.70, Z(2.0)), PLY, grain=2)
    # ponytail: the ragged ceiling slot and the boiler notch are a black panel under the shell ceiling, the sealed
    # recess a stained panel on the wall (both need a shell feature to be real openings)
    mb.box((4.08, 6.60, Z(2.0) - 0.003), (X1, Y1, Z(2.0) - 0.0005), BLK)
    mb.box((3.93, 8.28, Z(2.0) - 0.003), (4.08, Y1, Z(2.0) - 0.0005), BLK)
    mb.box((X1 - 0.003, 6.60, Z(1.25)), (X1, 7.05, Z(1.85)), C('recess', '#6E6654', 0.95))
    _add(ctx, mb, 'basement.backboard')

    xd, xh = 4.218, 4.200                                    # drops against the board, headers in front of them
    drops = (7.42, 7.55, 7.68, 7.80, 7.92, 8.02)
    mb = mo.MB()
    for y in drops:
        pipe(mb, [(xd, y, 1.999), (xd, y, 0.45)], 0.011, cu)
    pipe(mb, [(xd, 7.42, 0.45), (xd, 8.10, 0.45), (xd, 8.10, 0.22)], 0.011, cu)
    pipe(mb, [(xh, 7.36, 1.72), (xh, 8.25, 1.72), (xh, 8.25, 1.63)], 0.011, cu)                # header into the boiler
    pipe(mb, [(xh, 7.36, 1.84), (xh, 8.10, 1.84), (xh, 8.30, 1.995)], 0.011, cu)               # header into the notch
    for h, y1 in ((1.90, 8.12), (1.95, 8.05)):                                                # across the recess head
        pipe(mb, [(xd, 6.63, h), (xd, y1, h), (xd - 0.03, y1 + 0.2, 1.995)], 0.0075, cu)
    for y in (8.23, 8.31, 8.47, 8.55):                                                        # tails under the boiler
        pipe(mb, [(4.10, y, 0.91), (4.10, y, 0.78), (xd, y, 0.78), (xd, y, 0.22)], 0.011, cu)
    pipe(mb, [(4.10, 8.39, 0.91), (4.10, 8.39, 0.74), (xd, 8.39, 0.74), (xd, 8.39, 0.20)], 0.0105, WHITE)   # condensate
    pipe(mb, [(4.205, 7.07, 0.18), (4.205, 8.69, 0.18)], 0.02, BLK, 10)                       # 40 mm waste at the foot
    for y, col in ((7.55, '#C2261C'), (7.68, '#2748B0'), (7.80, '#C2261C')):                  # lever ball valves
        mb.box((xd - 0.02, y - 0.016, Z(1.33)), (xd + 0.008, y + 0.016, Z(1.375)), BRASS, bev=0.004)
        mb.box((xd - 0.034, y - 0.006, Z(1.30)), (xd - 0.02, y + 0.006, Z(1.39)), C('valve_' + col[1:], col, 0.4))
    grey = C('plant_grey', '#8B8E90', 0.5)
    mb.box((xd - 0.07, 7.89, Z(1.50)), (xd - 0.01, 7.95, Z(1.59)), grey, bev=0.006)           # motorised valve head
    mb.box((4.15, 7.39, Z(1.775)), (4.188, 7.51, Z(1.865)), C('ctl_blue', '#2F5FB8', 0.4), bev=0.004)   # control box
    led = P.emissive('#FF1030', 4.0)
    for y in (7.43, 7.47):
        mb.box((4.1485, y - 0.004, Z(1.80)), (4.15, y + 0.004, Z(1.808)), led)
    red = C('pump_red', '#B02A22', 0.35)
    mb.box((xd - 0.085, 7.79, Z(0.29)), (xd - 0.005, 7.91, Z(0.41)), red, bev=0.012)          # circulating pump
    mb.at(T(xd - 0.085, 7.85, 0.35) @ RY(-90))
    mb.lathe([(0, 0), (0.045, 0), (0.045, 0.05), (0.035, 0.06), (0, 0.06)], BLK, 12)
    mb.at()
    mb.box((4.18, 7.50, Z(0.25)), (XB, 7.60, Z(0.35)), C('galv', '#8C8C88', 0.5, 0.7), bev=0.003)   # adaptable box
    # "boiler controls" sub-board screwed over the pipes
    mb.box((4.185, 7.52, Z(0.80)), (4.203, 8.02, Z(0.99)), PLY, grain=1)
    mb.box((4.158, 7.925, Z(0.83)), (4.185, 7.995, Z(0.96)), WHITE, bev=0.004)                # wireless receiver
    mb.box((4.150, 7.755, Z(0.845)), (4.185, 7.905, Z(0.945)), WHITE, bev=0.004)              # wiring centre
    mb.box((4.157, 7.955, Z(0.935)), (4.158, 7.965, Z(0.945)), P.emissive('#30FF50', 3.0))
    for y in (7.69, 7.59):                                                                    # neon indicators
        mb.box((4.1745, y + 0.022, Z(0.90)), (4.176, y + 0.034, Z(0.91)), led)
    for i, y in enumerate((7.66, 7.80, 7.90)):                                                # white flex loops
        mb.tube([(4.18, y, Z(0.80)), (4.175, y + 0.02, Z(0.70)), (4.18, y + 0.06, Z(0.66)), (4.19, y + 0.10, Z(0.74))],
                0.004, WHITE, 5, up=(1, 0, 0))
    mb.box((4.19, 7.585, Z(1.035)), (4.225, 7.645, Z(1.09)), BLK, bev=0.004)                  # plug-in adaptor
    _add(ctx, mb, 'basement.pipework')

    for i, y in enumerate((7.86, 7.74)):                                                      # fused spurs, socket
        _wall_prop(ctx, P.switch_plate(1, name=f'basement.fcu.{i}'), XB, y, 1.10, (-1, 0))
    _wall_prop(ctx, P.socket(1, name='basement.board_socket'), XB, 7.615, 1.10, (-1, 0))
    for i, y in enumerate((7.69, 7.59)):
        _wall_prop(ctx, P.switch_plate(1, name=f'basement.boiler_switch.{i}'), 4.185, y, 0.895, (-1, 0))


def _boiler(ctx):
    mb = mo.MB()
    white = C('boiler_white', '#F2F2EF', 0.3)
    mb.box((3.89, 8.17, Z(0.90)), (XB, 8.61, Z(1.62)), white, bev=0.018)
    mb.box((3.886, 8.172, Z(1.16)), (3.90, 8.608, Z(1.23)), 'silver_satin')                   # fascia band, no badge
    mb.at(T(4.06, 8.39, 1.62))                                # flue: flange + short turret, 87 deg elbow at h 1.80
    mb.lathe([(0.075, 0), (0.075, 0.012), (0.05, 0.012), (0.05, 0.08)], WHITE, 14)
    mb.at()                                                   # ... then a short run back into the board (f_0217)
    mb.tube([(4.06, 8.39, Z(1.70)), (4.068, 8.39, Z(1.755)), (4.095, 8.39, Z(1.79)), (4.14, 8.39, Z(1.80)),
             (4.228, 8.39, Z(1.80))], 0.05, WHITE, 14, up=(0, 1, 0))
    _add(ctx, mb, 'basement.boiler', sym='boiler')

    mb = mo.MB()                                             # heating expansion vessel upright on its pipe, wall N
    red, yc = C('vessel_red', '#803623', 0.35), Y1 - 0.165
    mb.at(T(3.82, yc, 0.32))
    mb.lathe([(0, 0), (0.12, 0), (0.152, 0.03), (0.16, 0.08), (0.16, 0.20), (0.15, 0.255), (0.11, 0.29), (0.03, 0.30)],
             red, 20)
    mb.lathe([(0.03, 0.30), (0.03, 0.318), (0, 0.318)], BLK, 10)
    mb.lathe([(0.161, 0.135), (0.163, 0.14), (0.163, 0.16), (0.161, 0.165)], C('galv', '#8C8C88', 0.5, 0.7), 20)
    mb.at()
    pipe(mb, [(3.82, yc, 0.33), (3.82, yc, 0.24), (4.00, yc, 0.24), (4.00, yc, 0.06), (4.248, yc, 0.06)], 0.011, BLK)
    _add(ctx, mb, 'basement.vessel_heating', sym='cylinder')

    mb = mo.MB()                                             # potable expansion vessel lying on its side on the floor
    wv = C('vessel_white', '#F0EFEA', 0.3)
    mb.at(T(3.76, 7.66, 0.137) @ RY(90))
    mb.lathe([(0, 0), (0.03, 0), (0.03, 0.012), (0.10, 0.02), (0.13, 0.05), (0.135, 0.10), (0.135, 0.28),
              (0.125, 0.335), (0.09, 0.37), (0, 0.38)], wv, 20)
    mb.lathe([(0.1362, 0.17), (0.1362, 0.215)], 'chrome', 20)
    _add(ctx, mb, 'basement.vessel_potable', sym='cylinder')


def _cylinder(ctx):
    cx, cy, R = 3.93, 7.20, 0.2775
    white, blue, cu = C('cyl_white', '#F3F2EC', 0.25), C('cyl_blue', '#2D4FA3', 0.4), C('copper', '#A86F45', 0.32, 1.0)
    mb = mo.MB()
    mb.box((cx - 0.31, cy - 0.31, Z(0)), (cx + 0.31, cy + 0.31, Z(0.02)), PLY)
    mb.box((cx - 0.30, cy - 0.30, Z(0.02)), (cx + 0.30, cy + 0.30, Z(0.07)), C('slab', '#CFC8B4', 0.9), bev=0.005)
    mb.at(T(cx, cy, 0.07))
    mb.lathe([(0, 0), (R - 0.012, 0), (R, 0.012), (R, 1.555)], white, 32)
    mb.lathe([(R, 1.555), (R + 0.004, 1.56), (R + 0.004, 1.62), (R - 0.03, 1.675), (R * 0.55, 1.71), (0, 1.72)], blue, 32)
    mb.lathe([(R + 0.001, 1.21), (R + 0.001, 1.35)], C('label_cream', '#E9E3CF', 0.6), 6,
             a0=math.radians(168), a1=math.radians(196))                                      # blank sticker
    at = lambda deg, h: (cx + R * math.cos(math.radians(deg)), cy + R * math.sin(math.radians(deg)), h)
    for deg, h in ((150, 0.75), (150, 0.38)):                                                 # immersion-heater caps
        x, y, _ = at(deg, h)
        mb.at(T(x, y, h) @ Matrix.Rotation(math.radians(deg), 4, 'Z') @ RY(90))
        mb.lathe([(0, 0), (0.045, 0), (0.045, 0.025), (0.035, 0.035), (0, 0.035)], WHITE, 12)
    mb.at()
    x, y, _ = at(115, 0)                                                                      # T&P relief valve, red cap
    mb.box((x - 0.03, y - 0.005, Z(1.53)), (x + 0.02, y + 0.04, Z(1.575)), BRASS, bev=0.005)
    mb.box((x - 0.022, y + 0.04, Z(1.535)), (x + 0.012, y + 0.058, Z(1.57)), C('valve_C2261C', '#C2261C', 0.4), bev=0.004)
    pipe(mb, [(x - 0.005, y + 0.02, 1.53), (x - 0.005, y + 0.02, 0.30)], 0.0075, cu)          # discharge to the tundish
    x, y, _ = at(68, 0)
    pipe(mb, [(x, y - 0.01, 1.60), (x, 7.55, 1.60), (4.218, 7.55, 1.60)], 0.011, cu)          # 22 mm flow to the board
    x, y, _ = at(98, 0)
    mb.box((x - 0.02, y - 0.005, Z(0.10)), (x + 0.02, y + 0.03, Z(0.14)), BRASS, bev=0.004)   # drain cock + feed
    pipe(mb, [(x + 0.04, y + 0.012, 0.071), (x + 0.04, y + 0.012, 1.0), (4.218, y + 0.012, 1.0)], 0.011, cu)
    _add(ctx, mb, 'basement.cylinder', sym='cylinder')


# ------------------------------------------------------------------------------------------- wall W
def _electrics(ctx):
    cw = C('cu_white', '#EEEDE8', 0.35)
    mb = mo.MB()
    for i, h0 in enumerate((1.12, 1.50)):                                                     # two consumer units
        mb.box((X0, 7.20, Z(h0)), (X0 + 0.10, 7.80, Z(h0 + 0.36)), cw, bev=0.012)
        mb.box((X0 + 0.10, 7.215, Z(h0 + 0.015)), (X0 + 0.106, 7.785, Z(h0 + 0.165)), cw, bev=0.003)   # lower lid half
        mb.box((X0 + 0.10, 7.215, Z(h0 + 0.175)), (X0 + 0.112, 7.785, Z(h0 + 0.345)), cw, bev=0.005)   # flip-up lid
    mb.box((X0 + 0.112, 7.47, Z(1.375)), (X0 + 0.1128, 7.55, Z(1.41)), C('warn_yellow', '#E6C82A', 0.5))  # blank label
    # trunking: 100 x 50 along the top of wall W with a drop into the upper unit, 50 x 25 on the ceiling beside
    # it, 40 x 25 along wall N to the boiler notch
    mb.box((X0, 6.00, Z(1.88)), (X0 + 0.05, Y1, Z(1.98)), WHITE, bev=0.002)
    mb.box((X0, 7.45, Z(1.855)), (X0 + 0.05, 7.50, Z(1.885)), WHITE)
    mb.box((X0 + 0.052, 7.00, Z(1.975)), (X0 + 0.102, Y1, Z(1.9995)), WHITE, bev=0.002)
    mb.box((X0 + 0.05, Y1 - 0.025, Z(1.94)), (3.93, Y1, Z(1.98)), WHITE, bev=0.002)
    _add(ctx, mb, 'basement.electrics')

    _wall_prop(ctx, P.socket(2, name='basement.socket_w'), X0, 6.21, 0.30, (1, 0))
    _wall_prop(ctx, P.socket(2, name='basement.socket_cab'), X0, 7.995, 1.83, (1, 0))
    _wall_prop(ctx, P.switch_plate(1, kind='blank', name='basement.brush_plate'), X0, 7.865, 1.83, (1, 0))
    mb = mo.MB()
    mb.box((X0 + 0.009, 7.84, Z(1.82)), (X0 + 0.0105, 7.89, Z(1.84)), BLK)
    _add(ctx, mb, 'basement.brush_plate.brush')
    _wall_prop(ctx, P.socket(1, name='basement.socket_breast'), 3.90, 5.69, 0.42, (-1, 0))


def _netcab(ctx):
    """19-inch wall cabinet 0.60 w x 0.50 h x 0.45 d on wall W, glazed door facing east, hinged on the north side."""
    ya, yb, xa, xb, ha, hb = 7.98, 8.58, X0, 1.70, 1.22, 1.72
    blk, t = C('cab_black', '#1B1B1D', 0.6), 0.012
    mb = mo.MB()
    mb.box((xa, ya, Z(ha)), (xa + t, yb, Z(hb)), blk)                                         # back
    mb.box((xa, ya, Z(ha)), (xb, yb, Z(ha + t)), blk)
    mb.box((xa, ya, Z(hb - t)), (xb, yb, Z(hb)), blk)
    mb.box((xa, ya, Z(ha)), (xb, ya + t, Z(hb)), blk)
    mb.box((xa, yb - t, Z(ha)), (xb, yb, Z(hb)), blk)
    mb.box((xa + 0.10, ya - 0.001, Z(ha + 0.05)), (xb - 0.10, ya, Z(ha + 0.09)), C('louvre', '#38383B', 0.6))   # vent slot
    mb.at(T(xa + 0.225, ya, hb - 0.06) @ RX(90))
    mb.lathe([(0, 0), (0.011, 0), (0.011, 0.004), (0, 0.004)], 'chrome', 10)                  # side-panel key lock
    mb.at()
    grey = C('rack_gear', '#2C2C30', 0.5)                                                     # generic gear inside
    for y in (ya + 0.045, yb - 0.045):
        mb.box((xb - 0.07, y - 0.012, Z(ha + t)), (xb - 0.055, y + 0.012, Z(hb - t)), grey)   # 19-inch rails
    mb.box((xb - 0.14, ya + 0.045, Z(hb - 0.085)), (xb - 0.055, yb - 0.045, Z(hb - 0.04)), grey)      # patch panel
    mb.box((xb - 0.26, ya + 0.045, Z(hb - 0.16)), (xb - 0.055, yb - 0.045, Z(hb - 0.115)), grey)      # switch
    blue, green = C('patch_blue', '#3D62C8', 0.5), P.emissive('#30FF50', 3.0)
    for i in range(10):
        y = ya + 0.08 + i * 0.048
        mb.tube([(xb - 0.055, y, Z(hb - 0.062)), (xb - 0.03, y, Z(hb - 0.075)), (xb - 0.03, y, Z(hb - 0.125)),
                 (xb - 0.055, y, Z(hb - 0.138))], 0.003, blue, 5, up=(0, 1, 0))
        mb.box((xb - 0.0552, y + 0.012, Z(hb - 0.15)), (xb - 0.054, y + 0.018, Z(hb - 0.145)), green)
    mb.box((xb - 0.30, ya + 0.06, Z(ha + t)), (xb - 0.08, yb - 0.10, Z(ha + t + 0.045)), grey)        # box on the floor
    _add(ctx, mb, 'basement.netcab', sym='cabinet')

    fw, dt = 0.05, 0.015                                                                      # door frame, thickness
    d = mo.MB()
    for y0, y1, h0, h1 in ((ya, ya + fw, ha, hb), (yb - fw, yb, ha, hb), (ya, yb, ha, ha + fw), (ya, yb, hb - fw, hb)):
        d.box((xb + 0.001, y0, Z(h0)), (xb + 0.001 + dt, y1, Z(h1)), blk)
    d.at(T(xb + 0.001 + dt, ya + fw / 2, (ha + hb) / 2) @ RY(90))
    d.lathe([(0, 0), (0.011, 0), (0.011, 0.006), (0, 0.006)], 'chrome', 10)                   # cam lock, south stile
    door = d.finish('basement.netcab.door')
    g = mo.MB()
    g.box((xb + 0.007, ya + fw, Z(ha + fw)), (xb + 0.010, yb - fw, Z(hb - fw)), P.two_sided(M.mat('glass_clear')))
    glass = g.finish('basement.netcab.door.glass')
    # viewer faces west: the hinge (north) is on the right -> positive; 95 deg keeps the leaf 0.09 clear of wall N
    IX.tag_many([door, glass], 'hinge', g='basement.netcab.door', label='Network cabinet',
                p=(xb + 0.001 + dt / 2, yb, Z(ha)), deg=95)
    for o in (door, glass):
        ctx.add(o, RM, 'fit', lm='dynamic')

    n = mo.MB()                                                                               # 6-bay NAS, no logo
    n.box((1.42, 8.15, Z(hb)), (1.65, 8.38, Z(hb + 0.17)), blk, bev=0.004)
    for i in range(6):
        y = 8.165 + i * 0.0345
        n.box((1.65, y, Z(hb + 0.03)), (1.6515, y + 0.030, Z(hb + 0.155)), grey)
    n.box((1.65, 8.17, Z(hb + 0.012)), (1.651, 8.176, Z(hb + 0.018)), green)
    _add(ctx, n, 'basement.nas', 'decor')


def _plaque(ctx):
    """D1: an old oak arch-panel cabinet door hung landscape as a key board, y 6.21..6.96, h 1.10..1.70."""
    # ponytail: plain golden-oak colour; the library oaks render pale pink here next to L-A (oak_rustic #E0C8B2,
    # oak_table #A3806A against the filmed #846E4D), and no darker golden oak texture exists
    oak, ya, yb, ha, hb, fr = C('plaque_oak', '#554827', 0.45), 6.21, 6.96, 1.10, 1.70, 0.07
    mb = mo.MB()
    mb.box((X0, ya, Z(ha)), (X0 + 0.012, yb, Z(hb)), oak, grain=1)                            # back / sunk field
    for y0, y1, h0, h1, gr in ((ya, ya + fr, ha, hb, 2), (yb - fr, yb, ha, hb, 2), (ya + fr, yb - fr, ha, ha + fr, 1)):
        mb.box((X0, y0, Z(h0)), (X0 + 0.02, y1, Z(h1)), oak, bev=0.004, grain=gr)
    # cathedral top rail: lower edge 0.13 down at the stiles, a shoulder, then an arch rising 0.09 to the centre
    ym, wa = (ya + yb) / 2, (yb - ya) / 2 - fr - 0.07      # shoulders 0.05 in from the stiles (> field inset)

    def edge(drop, inset):                                   # lower edge of the rail lowered by `drop`, west to east
        pts = [(ya + fr + inset, hb - 0.13 - drop), (ym - wa - 0.02, hb - 0.13 - drop), (ym - wa - 0.02, hb - 0.115 - drop)]
        pts += [(ym - wa * math.cos(a), hb - 0.115 - drop + 0.075 * math.sin(a)) for a in
                (math.pi * i / 14 for i in range(15))]
        return pts + [(ym + wa + 0.02, hb - 0.115 - drop), (ym + wa + 0.02, hb - 0.13 - drop),
                      (yb - fr - inset, hb - 0.13 - drop)]
    rail = [(ya + fr, hb)] + edge(0, 0) + [(yb - fr, hb)]
    mb.prism([(X0, y, Z(h)) for y, h in rail], (0.02, 0, 0), oak, grain=1)
    for x0, dx, gap in ((X0 + 0.012, 0.006, 0.03), (X0 + 0.018, 0.008, 0.045)):               # raised field, 2 steps
        top = edge(gap, gap)
        field = [(top[0][0], ha + fr + gap)] + top + [(top[-1][0], ha + fr + gap)]
        mb.prism([(x0, y, Z(h)) for y, h in field], (dx, 0, 0), oak, grain=1)
    xf = X0 + 0.026                                                                           # face of the field
    for row, h in enumerate((1.48, 1.34)):                                                    # 6 + 6 brass hooks
        for i in range(6):
            y = ym - 0.20 + i * 0.08 + row * 0.02
            mb.box((xf, y - 0.003, Z(h)), (xf + 0.012, y + 0.003, Z(h + 0.006)), BRASS)
            mb.box((xf + 0.009, y - 0.003, Z(h)), (xf + 0.012, y + 0.003, Z(h + 0.014)), BRASS)
    for y, h in ((ym - 0.20, 1.48), (ym + 0.04, 1.48), (ym - 0.10, 1.34), (ym + 0.14, 1.34)):   # a few plain key rings
        mb.tube([(xf + 0.007, y + 0.012 * math.cos(a), Z(h - 0.012) + 0.012 * math.sin(a)) for a in
                 (math.pi * i / 4 for i in range(8))], 0.0012, 'silver_satin', 4, closed=True, up=(1, 0, 0))
        mb.box((xf + 0.004, y - 0.005, Z(h - 0.075)), (xf + 0.006, y + 0.005, Z(h - 0.024)), 'silver_satin')
    for y in (ya + 0.12, yb - 0.12):                                                          # fixing screws
        mb.box((X0 + 0.001, y - 0.004, Z(hb)), (X0 + 0.004, y + 0.004, Z(hb + 0.012)), BRASS)
    _add(ctx, mb, 'basement.keyboard', 'decor')
    hd = P.handle_drop(0.07, finish='brass', name='basement.keyboard.handle')
    ctx.add(P.place(hd, (X0 + 0.02, ym, Z(ha + fr / 2 + 0.01)), facing=(1, 0)), RM, 'decor')


def _shoe_racks(ctx):
    mb = mo.MB()                                             # rack 1: steel tube, 4 tiers, 1.00 x 0.30 x 0.65
    ya, yb, xa, xb = 6.45, 7.45, X0 + 0.01, X0 + 0.30
    for x in (xa, xb - 0.02):
        for y in (ya, yb - 0.02):
            mb.box((x, y, Z(0)), (x + 0.02, y + 0.02, Z(0.65)), BLK)
    for h in (0.06, 0.25, 0.44, 0.63):
        for x in (xa + 0.003, xa + 0.095, xa + 0.19, xb - 0.017):
            mb.box((x, ya + 0.01, Z(h)), (x + 0.014, yb - 0.01, Z(h + 0.014)), BLK)
    _add(ctx, mb, 'basement.shoe_rack.1', 'furn', 'rack')
    mb = mo.MB()                                             # rack 2: fabric shelves, 5 tiers, 0.90 x 0.30 x 0.85
    ya, yb, cloth = 7.50, 8.40, C('rack_fabric', '#242427', 0.95)
    for x in (xa, xb - 0.018):
        for y in (ya, yb - 0.018):
            mb.box((x, y, Z(0)), (x + 0.018, y + 0.018, Z(0.85)), BLK)
    for h in (0.05, 0.245, 0.44, 0.635, 0.83):
        mb.box((xa + 0.004, ya + 0.004, Z(h)), (xb - 0.004, yb - 0.004, Z(h + 0.012)), cloth)
    _add(ctx, mb, 'basement.shoe_rack.2', 'furn', 'rack')


# ------------------------------------------------------------------------------------------- wall S and breast
def _racks(ctx):
    """Two bays of blue boltless racking, 0.90 x 0.40 x 1.80, five white-faced chipboard decks (one shared mesh)."""
    blue, deck = C('rack_blue', '#171B3E', 0.5), C('rack_deck', '#EDEBE2', 0.6)        # spec #22306B rendered royal blue
    W, D, H, a, t = 0.90, 0.40, 1.80, 0.038, 0.004
    levels = (0.08, 0.50, 0.92, 1.34, 1.76)
    mb = mo.MB()
    for sx, x in ((1, 0.0), (-1, W)):
        for sy, y in ((1, 0.0), (-1, D)):                                                     # angle uprights
            mb.box((x, y, 0), (x + sx * a, y + sy * t, H), blue)
            mb.box((x, y, 0), (x + sx * t, y + sy * a, H), blue)
    for h in levels:
        for y in (t, D - t - 0.012):
            mb.box((t, y, h - 0.05), (W - t, y + 0.012, h - 0.002), blue)                     # front / back beams
        for x in (t, W - t - 0.012):
            mb.box((x, t, h - 0.05), (x + 0.012, D - t, h - 0.002), blue)
        mb.box((0.012, 0.012, h - 0.014), (W - 0.012, D - 0.012, h), deck)
    first = mb.finish('basement.rack.w')
    first.location = (2.07, Y0 + 0.005, ZF)
    ctx.add(first, RM, 'furn', plan_sym='rack')
    second = bpy.data.objects.new('basement.rack.e', first.data)
    second.location = (2.97, Y0 + 0.005, ZF)
    ctx.add(second, RM, 'furn', plan_sym='rack')

    # a few generic things: paint tins on the lowest deck of bay E, three plain boxes, two white tubs
    mb = mo.MB()
    tin = (C('tin_white', '#E8E6E0', 0.35), C('tin_grey', '#8A8D90', 0.35, 0.6), C('tin_dark', '#2B2D33', 0.4))
    lid = (C('tin_cream', '#E3D9BF', 0.4), C('tin_dark', '#2B2D33', 0.4), C('tin_white', '#E8E6E0', 0.35))
    for i in range(9):
        x, y = 3.07 + (i % 5) * 0.18 + (i // 5) * 0.09, Y0 + 0.11 + (i // 5) * 0.18
        mb.at(T(x, y, 0.08))
        mb.lathe([(0, 0), (0.083, 0), (0.085, 0.004), (0.085, 0.186)], tin[i % 3], 12)
        mb.lathe([(0.085, 0.186), (0.087, 0.19), (0.07, 0.19), (0.068, 0.184), (0, 0.184)], lid[(i * 2) % 3], 12)
    card = C('cardboard', '#B08F62', 0.9)
    mb.at()
    for (x, y, h), (w, d, hh) in (((2.18, Y0 + 0.06, 1.34), (0.36, 0.28, 0.24)), ((2.55, Y0 + 0.07, 0.92), (0.30, 0.26, 0.20)),
                                  ((3.12, Y0 + 0.05, 1.34), (0.40, 0.30, 0.22))):
        mb.box((x, y, Z(h)), (x + w, y + d, Z(h + hh)), card, bev=0.003)
    for x in (2.25, 2.62):
        mb.at(T(x, Y0 + 0.20, 0.08))
        mb.lathe([(0, 0), (0.11, 0), (0.13, 0.22), (0.135, 0.225), (0.135, 0.24), (0, 0.24)], WHITE, 14)
    _add(ctx, mb, 'basement.rack.stock', 'decor')


def _gas(ctx):
    galv, cu = C('galv', '#8C8C88', 0.5, 0.7), C('copper', '#A86F45', 0.32, 1.0)
    y = Y0
    mb = mo.MB()
    # ponytail: the 80 mm niche is a galvanised back plate on the wall face (a real recess needs a shell feature)
    mb.box((1.55, y, Z(1.45)), (1.85, y + 0.002, Z(1.88)), galv)
    # landscape smart meter nearly filling the niche width (f_0247); facing south, west (low x) is on the right
    mb.box((1.565, y + 0.002, Z(1.47)), (1.835, y + 0.072, Z(1.635)), C('meter', '#DAD9D6', 0.4), bev=0.012)
    mb.box((1.651, y + 0.072, Z(1.578)), (1.724, y + 0.0728, Z(1.605)), C('lcd', '#7E9A6A', 0.3))         # blank LCD
    mb.box((1.585, y + 0.072, Z(1.50)), (1.630, y + 0.0728, Z(1.565)), C('warn_yellow', '#E6C82A', 0.5))  # plain label
    for x in (1.603, 1.625):
        mb.at(T(x, y + 0.072, 1.592) @ RX(-90))
        mb.lathe([(0, 0), (0.008, 0), (0.008, 0.003), (0, 0.003)], galv, 8)
    mb.at()
    mb.box((1.60, y + 0.012, Z(1.66)), (1.80, y + 0.05, Z(1.68)), BRASS, bev=0.003)           # meter bar on two unions
    for x in (1.63, 1.77):
        pipe(mb, [(x, y + 0.031, 1.634), (x, y + 0.031, 1.665)], 0.016, BRASS)
    pipe(mb, [(1.63, y + 0.031, 1.675), (1.63, y + 0.031, 1.878)], 0.011, cu)                 # copper tail, west side
    pipe(mb, [(1.77, y + 0.031, 1.675), (1.77, y + 0.031, 1.76)], 0.012, BRASS)
    mb.at(T(1.77, y + 0.031, 1.755))                                                          # regulator, east side
    mb.lathe([(0, 0), (0.03, 0), (0.034, 0.012), (0.034, 0.03), (0.02, 0.045)], C('reg_grey', '#8E9494', 0.5), 12)
    mb.lathe([(0.02, 0.045), (0.02, 0.07), (0, 0.072)], C('reg_green', '#4F8F5A', 0.5), 10)
    mb.at()
    flex = [(1.745, 1.775), (1.70, 1.765), (1.64, 1.762), (1.58, 1.785), (1.53, 1.825), (1.49, 1.84)]
    mb.tube([(x, y + 0.045, Z(h)) for x, h in flex], 0.0125, 'silver_satin', 8, up=(0, 1, 0))  # flexible connector
    mb.tube([(x, y + 0.045, Z(h)) for x, h in ((1.545, 1.812), (1.52, 1.83))], 0.0135,
            C('warn_yellow', '#E6C82A', 0.5), 8, up=(0, 1, 0))                                # yellow tape band
    mb.box((1.43, y + 0.025, Z(1.82)), (1.49, y + 0.065, Z(1.86)), BRASS, bev=0.005)          # lever ball valve
    mb.box((1.40, y + 0.066, Z(1.80)), (1.51, y + 0.072, Z(1.814)), C('valve_C2261C', '#C2261C', 0.4))
    # boxed bulkhead carrying the gas pipe west, with its open square end; boxing in the opening's south reveal
    wall = M.paint('#F3F2EE')
    mb.box((X0, y, Z(1.85)), (1.45, y + 0.12, Z(2.0) - 0.0005), wall)
    mb.box((1.4495, y + 0.02, Z(1.87)), (1.451, y + 0.10, Z(1.985)), BLK)
    mb.box((1.10, y, ZF + 0.211), (1.20, y + 0.05, Z(1.8495)), wall)
    _add(ctx, mb, 'basement.gas_meter')


def _breast(ctx):
    x = 3.90
    mb = mo.MB()
    mb.box((x - 0.003, 5.70, Z(1.42)), (x, 6.00, Z(1.87)), WHITE)                             # access hatch + frame
    mb.box((x - 0.0045, 5.712, Z(1.432)), (x - 0.003, 5.988, Z(1.858)), WHITE)
    blue = C('cross_blue', '#2B3FA8', 0.5)
    mb.box((x - 0.006, 5.845, Z(1.12)), (x - 0.0005, 5.855, Z(1.25)), blue)                   # D2 cross on a thread
    mb.box((x - 0.006, 5.805, Z(1.20)), (x - 0.0005, 5.895, Z(1.21)), blue)
    mb.box((x - 0.002, 5.8495, Z(1.25)), (x - 0.001, 5.8505, Z(1.42)), blue)
    _add(ctx, mb, 'basement.hatch')


# ------------------------------------------------------------------------------------------- loose pieces
def _stools(ctx):
    white = C('stool_white', '#EFEEEA', 0.35)
    mb = mo.MB()
    mb.lathe([(0, 0.425), (0.15, 0.425), (0.16, 0.432), (0.16, 0.45), (0, 0.45)], white, 20)
    hole = C('stool_hole', '#A9A7A0', 0.8)
    for i in range(8):                                                                        # ring of finger holes
        a = math.pi * 2 * i / 8
        mb.at(Matrix.Translation((0.10 * math.cos(a), 0.10 * math.sin(a), 0.4502)))
        mb.lathe([(0.016, 0), (0, 0)], hole, 8)
    mb.at()
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.tube([(sx * 0.10, sy * 0.10, 0.43), (sx * 0.15, sy * 0.15, 0.0)], 0.0095, white, 6)
    first = mb.finish('basement.stool.0')
    first.location = (1.88, 5.40, ZF)                                           # clear of the stair foot
    ctx.add(first, RM, 'furn', plan_sym='stool')
    for i in range(4):                                                                        # the stack of four
        o = bpy.data.objects.new(f'basement.stool.{i + 1}', first.data)
        o.location = (3.55, 6.25, ZF + 0.05 * i)
        ctx.add(o, RM, 'furn', plan_sym='stool' if i == 0 else None)


def _cooler(ctx):
    mb = mo.MB()
    mb.at(T(3.75, 7.95, 0))
    mb.lathe([(0, 0), (0.10, 0), (0.10, 0.012), (0.07, 0.03), (0.03, 0.05), (0.018, 0.09), (0.022, 0.20), (0.014, 0.26),
              (0.02, 0.40), (0.03, 0.47), (0.07, 0.51), (0.10, 0.53), (0.115, 0.56), (0.12, 0.74), (0.126, 0.75),
              (0.112, 0.75), (0.108, 0.57), (0, 0.56)], BRASS, 20)
    for s in (-1, 1):                                                                         # ring handles
        mb.tube([(0, s * (0.122 + 0.02 * (1 - math.cos(a))), 0.66 + 0.035 * math.sin(a)) for a in
                 (math.pi * 2 * i / 10 for i in range(10))], 0.004, BRASS, 5, closed=True, up=(1, 0, 0))
    _add(ctx, mb, 'basement.wine_cooler', 'decor', 'table_round')


def build(ctx, ceiling_light):
    _board(ctx)
    _boiler(ctx)
    _cylinder(ctx)
    _electrics(ctx)
    _netcab(ctx)
    _plaque(ctx)
    _shoe_racks(ctx)
    _racks(ctx)
    _gas(ctx)
    _breast(ctx)
    _stools(ctx)
    _cooler(ctx)
    for name, (x, y) in (('a', (1.85, 6.00)), ('b', (2.20, 7.70))):                           # L-A, L-B
        ceiling_light(ctx, RM, f'basement.light.{name}', (x, y, ctx.ceil_z(RM)), 0.35, 0.07, 100)

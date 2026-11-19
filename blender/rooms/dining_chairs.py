"""Dining room chairs: eight Chippendale chairs (6 side chairs + 2 carvers) in near-black oak with padded
drop-in tapestry seats. Imported by rooms/dining.py.

Local frame: origin = footprint centre on the floor; the chair faces local -Y (the sitter looks along -Y)."""
import math
import os
from math import cos, pi

from lib import materials as M, mouldings as mo, props as P
from rooms.dining_furniture import T, R, WALL, ART, fin, spline, loft, bar, rrect, oval, dark_wood, shared

_CHAIR = {}


def _seat_mat():
    # rectified crop of the real tapestry (reference still t = 582.4 s, pattern only), shown once over each pad
    return M.image_mat('dining_seat_tapestry', os.path.join(ART, 'seat_tapestry.jpg'), None, roughness=.9)


def _strap(mb, pts, w, wood, dy=0.0, t=.011):
    """Ribbon of a pierced splat: chamfered section w x t following pts [(x, z)...] in the splat plane."""
    bar(mb, [(x, dy, z) for x, z in pts], rrect(w, t, .003, 1), wood, up=(0, -1, 0))


def _chair_mesh(arm):
    """One Chippendale chair mesh. Side chair 0.53 x 0.50 x 0.97, carver 0.64 over the arms (seat rail 0.60)
    x 0.56 x 0.99; seat 0.47 at the front edge, crowned pad."""
    wood = dark_wood()
    wf, wb, d, top = (.30, .25, .28, .96) if arm else (.265, .2225, .25, .94)       # half front / back width, half depth
    k = .06                                                                         # outward flare of the back uprights
    mb = mo.MB()
    # ---- moulded seat frame (trapezoid)
    mb.box((-wf, -d, .385), (wf, -d + .032, .445), wood, bev=.004)
    mb.box((-wb, d - .032, .385), (wb, d, .445), wood, bev=.004)
    for s in (-1, 1):
        mb.prism([(s * wf, -d + .004, .385), (s * wb, d - .004, .385), (s * (wb - .032), d - .004, .385),
                  (s * (wf - .032), -d + .004, .385)], (0, 0, .06), wood)
    lip = [(0, 0), (.005, 0), (.005, .004), (.002, .009), (0, .009)]                 # thumb mould round the top edge
    mb.sweep(lip, [(-wf, -d, .4365), (-wb, d, .4365), (wb, d, .4365), (wf, -d, .4365)], wood, closed=True)
    # ---- padded drop-in seat: soft rounded edge standing 32 mm proud of the frame, crowned a further 18 mm
    q = [(-wf + .026, -d + .026), (wf - .026, -d + .026), (wb - .026, d - .036), (-wb + .026, d - .036)]
    us = [0, .012, .035, .07, .12, .22, .36, .5, .64, .78, .88, .93, .965, .988, 1]
    edge = lambda u: math.sqrt(max(0.0, 1 - (1 - min(min(u, 1 - u) / .12, 1.0)) ** 2))
    crown = lambda u: 1 - abs(2 * u - 1) ** 2.5

    def pad(u, v):
        x = (q[0][0] * (1 - u) + q[1][0] * u) * (1 - v) + (q[3][0] * (1 - u) + q[2][0] * u) * v
        return (x, q[0][1] * (1 - v) + q[3][1] * v, .449 + .032 * edge(u) * edge(v) + .018 * crown(u) * crown(v))
    loft(mb, [[pad(u, v) for u in us] for v in us], _seat_mat(), closed=False, uv=lambda i, j: (us[j], us[i]))
    for a, b in ((0, 1), (1, 2), (2, 3), (3, 0)):  # low skirt closing the gap under the pad's edge
        mb.face([(*q[a], .448), (*q[b], .448), (*q[b], .44), (*q[a], .44)], wood,
                (q[a][0] + q[b][0], q[a][1] + q[b][1], 0))
    # ---- back legs + raked uprights: one rounded 45 x 32 bar each, flaring outward above the seat
    zs = [0, .15, .30, .445, .60, .75, top - .012]
    yc = [d + .045, d + .012, d - .008, d - .016, d - .006, d + .016, d + .052]
    sc = [(.9, .8), (1, .9), (1.1, 1), (1.15, 1), (1, .95), (.9, .9), (.85, .85)]
    cl = spline([(wb - .0225 + k * max(0.0, z - .445), y, z, a, b) for z, y, (a, b) in zip(zs, yc, sc)], 4)
    for s in (-1, 1):
        bar(mb, [(s * x, y, z) for x, y, z, _, _ in cl], rrect(.032, .045, .009, 2), wood, up=(1, 0, 0),
            scale=[(a, b) for *_, a, b in cl])
    # ---- serpentine cupid's-bow crest rail; ears turning up and out past the uprights into carved volutes
    xt = wb - .0225 + k * (top - .445)
    hw, yb = xt + .05, d + .052
    cu = [-1 + 2 * i / 36 for i in range(37)]
    mid = lambda u: top - .028 + .016 * cos(1.5 * pi * u) + .045 * abs(u) ** 6
    th = lambda u: .056 - .024 * abs(u) ** 1.5
    bar(mb, [(u * hw, yb, mid(u)) for u in cu], rrect(.056, .03, .011, 2), wood, up=(0, -1, 0),
        scale=[(th(u) / .056, 1 - .15 * abs(u) ** 4) for u in cu])
    yf = yb - .0145                                                                 # carved front face
    for a in (-66, -44, -22, 0, 22, 44, 66):                                        # raised shell at the centre
        mb.at(T((0, yf, top - .036)) @ WALL @ R('Z', -a))
        mb.leaf(.048, .017, .007, wood, 4, base=.4, round_=.5, rib=1.0, skew=1.4)
    for s in (-1, 1):
        mb.at(T((s * hw, yb, mid(1))) @ R('X', 90))
        mb.lathe([(0, -.017), (.015, -.017), (.021, -.011), (.021, .011), (.015, .017), (0, .017)], wood, 12)   # ear volute
        for uu, ang, L in ((.2, 78, .075), (.52, 96, .08), (.8, 60, .06)):          # leaf sprays running to the ears
            mb.at(T((s * uu * hw, yf, mid(uu) - .004)) @ WALL @ R('Z', -s * ang))
            mb.leaf(L, .024, .006, wood, 5, serrate=.3, curl=.3)
    # ---- pierced vase splat, raked between a moulded shoe and the crest: outline straps, an interlaced
    #      figure-eight (lower loop + pointed upper loop), a pair of lancet straps, mullion and collar
    mb.at()
    mb.box((-.082, d - .04, .445), (.082, d, .470), wood, bev=.005)                     # shoe
    mb.box((-.07, d - .034, .470), (.07, d - .004, .482), wood, bev=.004)
    y_bot, z_bot, y_top, z_top = d - .016, .478, yb + .002, top - .03
    h = math.hypot(y_top - y_bot, z_top - z_bot) / .44
    S = T((0, y_bot, z_bot)) @ R('X', -math.degrees(math.atan2(y_top - y_bot, z_top - z_bot)))
    mb.at(S)
    Z = lambda pts: [(x, z * h) for x, z in pts]
    outl = spline(Z([(.054, 0), (.041, .07), (.037, .12), (.050, .19), (.080, .27), (.098, .35), (.093, .44)]), 4)
    fig8 = spline(Z([(.014, 0), (.031, .055), (.033, .115), (0, .195), (-.047, .27), (-.063, .33), (-.042, .395), (0, .44)]), 4)
    vee = spline(Z([(.052, .44), (.043, .385), (.024, .325), (0, .285)]), 4)
    for s in (-1, 1):
        _strap(mb, [(s * x, z) for x, z in outl], .022, wood, t=.014)
        _strap(mb, [(s * x, z) for x, z in fig8], .019, wood, dy=.0018 * s)
        _strap(mb, [(s * x, z) for x, z in vee], .016, wood, dy=-.0018 * s)
    _strap(mb, Z([(0, .2), (0, .25), (0, .30)]), .016, wood)
    _strap(mb, Z([(-.056, .195), (0, .195), (.056, .195)]), .026, wood, dy=-.002, t=.014)
    mb.at(S @ T((0, -.008, .195 * h)) @ WALL)
    mb.dome(.022, .017, .007, wood, 8, 2)                                           # boss where the loops cross
    mb.at()
    if not arm:
        # ---- straight square front legs with reeded outer faces, H-stretcher
        for s in (-1, 1):
            mb.box((s * wf, -d, 0), (s * (wf - .045), -d + .045, .40), wood, bev=.005)
            for off in (.014, .031):
                mb.box((s * (wf - off) - .004, -d - .0015, .012), (s * (wf - off) + .004, -d + .002, .383), wood, bev=.0015)
                mb.box((s * (wf + .0015), -d + off - .004, .012), (s * (wf - .002), -d + off + .004, .383), wood, bev=.0015)
            mb.prism([(s * (wf - .012), -d + .04, .145), (s * (wf - .034), -d + .04, .145),
                      (s * (wb - .034), d, .145), (s * (wb - .012), d, .145)], (0, 0, .03), wood)
        xm = (wf + wb) / 2 - .023
        mb.box((-xm, -.011, .148), (xm, .011, .172), wood, bev=.003)
    else:
        # ---- open arms: thick oval bar sweeping down, out and forward in an S from the upright to a hand-rest
        #      that scrolls over into a volute; curved (cyma) support set back 0.11 from the front leg
        za = .695
        xu = wb - .0225 + k * (za - .445)
        for s in (-1, 1):
            pth = spline([(xu - .004, d + .002, za, .85, .8), (wf - .022, d - .15, za + .008, .9, .9),
                          (wf - .002, -.03, za - .008, 1, 1), (wf, -d + .15, za - .03, 1.1, 1.15),
                          (wf - .006, -d + .075, za - .04, 1.15, 1.25), (wf - .008, -d + .042, za - .058, 1.05, 1.2),
                          (wf - .008, -d + .04, za - .082, .9, 1.15), (wf - .008, -d + .06, za - .094, .7, 1.1)], 5)
            bar(mb, [(s * x, y, z) for x, y, z, _, _ in pth], oval(.03, .04, 10), wood, up=(s, 0, 0),
                scale=[(a, b) for *_, a, b in pth])
            mb.at(T((s * (wf - .008), -d + .062, za - .074)) @ R('Y', 90))
            mb.lathe([(0, -.026), (.014, -.026), (.019, -.016), (.019, .016), (.014, .026), (0, .026)], wood, 12)   # volute eye
            mb.at(T((s * (wf - .003), -d + .21, za - .012)) @ R('Z', 180) @ R('X', -12))
            mb.leaf(.15, .04, .008, wood, 6, serrate=.3, curl=.2)                   # carved leaf on the hand-rest
            mb.at()
            sup = spline([(wf - .02, -d + .15, .43, 1.2), (wf + .002, -d + .16, .50, 1.05), (wf + .008, -d + .135, .575, .95),
                          (wf, -d + .125, za - .04, 1.0)], 5)
            bar(mb, [(s * x, y, z) for x, y, z, _ in sup], rrect(.034, .03, .009, 2), wood, up=(s, 0, 0),
                scale=[a for *_, a in sup])
    for v in mb.bm.verts:                       # the raked back legs end square to their axis (-4 .. +4 mm): cut the feet level
        if v.co.z < .0045:
            v.co.z = 0.0
    return fin(mb, 'dining.chair.arm' if arm else 'dining.chair.side')


def chair(name, arm=False):
    """New chair object sharing the mesh of its type. Carvers get cabriole ball-and-claw front legs."""
    ob = shared(_CHAIR, arm, lambda: _chair_mesh(arm), name)
    if arm:
        for i, s in enumerate((-1, 1)):
            leg = P.turned_leg(.447, .062, 'cabriole', .065, 0, dark_wood(), out=(s, -1), foot='claw',
                               name=f'{name}.leg.{i}')
            leg.parent = ob
            leg.location = (s * (.30 - .031), -.28 + .031, 0)
    return ob

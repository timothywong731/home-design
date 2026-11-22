"""shed - brick garden building: veranda, store cupboard, workshop (spec/rooms/shed.md, spec/phase3/briefs/shed.md).

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --levels X --only shell,site,envelope,shed --preview shed --res 540x960 --samples 64 --tag shed
    (add --pose 1 --tag shed1 for the open state)

The site stage built walls, roof, soffit, fascia, paving, the front pier and the two rooms; joinery built the store
doors, the French doors and both windows with their interaction tags. This module adds the furniture, the fittings, the
lights and their switch. Every y is taken from the spec (RECONCILE3 garden-12..-18: the building moved 1.62..1.85 north):
the veranda zone VX0..VX1 x VY0 (front edge) .. VY1 (wall face), the store room, the openings. x is as measured
(round-3 survey, spec/phase3/garden.md 3.3: the building did not move sideways). Workshop interior: rooms/shed_workshop.py.
"""
import math
import random

import bpy
from mathutils import Matrix, Vector

from lib import interact as IX, lighting, mouldings as mo, props as P
from rooms import shed_workshop as W
from rooms.shed_workshop import C, cyl

ROOM = 'shed'            # building rooms shed_workshop / shed_store are geometry ids only: every object is tagged 'shed'

VX0, VX1, VY0, VY1 = 0.06, 4.22, 25.02, 26.70          # veranda zone (frame() re-reads it)
SX0, SX1, SY0, SY1 = -0.77, -0.37, 25.35, 26.68        # store room
BIRD = (-0.85, -0.65, 1.43, 1.78)                         # nest box x0, x1, z0, roof top (veranda() sets it)

CAMERAS = [
    dict(name='front', pos=(1.3, 22.3, 1.2), look=(2.0, 26.7, 0.6), fov_deg=95, ref='v2_t188'),
    dict(name='top', pos=(1.66, 17.53, 7.0), look=(1.9, 25.9, -0.42), fov_deg=34, ref='v13:f_0216 (r3_garden/g216_ver)'),
    dict(name='veranda_w', pos=(3.4, 25.6, 1.1), look=(-0.4, 26.2, 0.6), fov_deg=100, ref='v2:f_0257'),
    dict(name='veranda_e', pos=(0.9, 25.7, 1.1), look=(4.2, 26.3, 0.6), fov_deg=100, ref='v2:f_0275'),
    dict(name='rack', pos=(2.6, 25.5, 1.05), look=(4.2, 25.9, 0.35), fov_deg=95, ref='v2:f_0305'),
    dict(name='store', pos=(0.75, 25.95, 1.0), look=(-0.6, 26.02, 0.45), fov_deg=95, ref='v2:f_0265'),
    dict(name='store_in', pos=(-0.40, 26.60, 0.95), look=(-0.75, 25.5, 0.55), fov_deg=100, ref='v2:f_0265 (v2_t264)'),
    dict(name='pier', pos=(2.3, 22.0, 1.5), look=(0.0, 25.2, 0.8), fov_deg=90, ref='v2_t194'),
    dict(name='ws_glass', pos=(3.0, 26.45, 1.2), look=(2.0, 30.4, 0.55), fov_deg=95, ref='v2:f_0287'),
    dict(name='ws_back', pos=(3.3, 27.25, 1.15), look=(1.2, 30.4, 0.5), fov_deg=100, ref='v2:f_0282'),
    dict(name='ws_east', pos=(2.4, 27.25, 1.15), look=(4.2, 30.2, 0.3), fov_deg=100, ref='v2:f_0281'),
    dict(name='ws_door', pos=(-0.3, 29.6, 1.2), look=(3.6, 27.0, 0.5), fov_deg=100, ref=None),
    dict(name='ws_west', pos=(3.4, 29.6, 1.2), look=(-0.6, 29.3, 0.6), fov_deg=100, ref='v2:f_0291'),
    dict(name='switch', pos=(2.9, 28.1, 1.1), look=(4.18, 27.15, 0.8), fov_deg=80, ref=None),
]

TEAK = 'oak_rustic'                                          # weathered honey-brown teak #A9824F
BOWL = [(0, 0), (.06, 0), (.12, .06), (.125, .07), (.115, .07), (.055, .012), (0, .012)]     # shallow bowl, r 0.125


def frame(ctx):
    global VX0, VX1, VY0, VY1, SX0, SX1, SY0, SY1
    xs, ys = zip(*ctx.zone('shed_veranda')['polygon'])
    VX0, VX1, VY0, VY1 = min(xs), max(xs), min(ys), max(ys)
    xs, ys = zip(*ctx.room_poly('shed_store'))
    SX0, SX1, SY0, SY1 = min(xs), max(xs), min(ys), max(ys)


def _downpipe_x(default):
    """x extent of the site's SW downpipe: the only part of shed.fascia below Z 1.0."""
    o = bpy.data.objects.get('shed.fascia')
    xs = [w.x for w in (o.matrix_world @ v.co for v in o.data.vertices) if w.z < 1.0] if o else []
    return (min(xs), max(xs)) if xs else default


def bowl(mb, p, mat, s=1.0):
    mb.at(Matrix.Translation(p) @ Matrix.Scale(s, 4))
    mb.lathe(BOWL, mat, 20)
    mb.at()


# ------------------------------------------------------------------ veranda
def garden_furniture(ctx):
    """Two folded teak chairs against the wall under the window, x 0.5..1.4, and the oval slatted table top on its end to
    their right, behind the pine box (v2_t188, v2_t194; v13 f_0216: chairs x 0.5..1.4)."""
    mb, ZP = mo.MB(), W.ZP

    def chair():                                             # folded: 0.50 x 0.09 x 0.95; back on y = 0, front -Y
        for sx in (-1, 1):
            mb.box((sx * .25, -.03, 0), (sx * .205, 0, .95), TEAK, bev=.003)
            mb.box((sx * .20, -.06, .03), (sx * .16, -.03, .80), TEAK, bev=.003)
            mb.box((sx * .155, -.09, 0), (sx * .12, -.06, .72), TEAK, bev=.003)
            cyl(mb, (.25 if sx > 0 else -.27, -.015, .50), .008, .02, 'brass', 'x', 6)     # pivot bolts
        mb.box((-.205, -.03, .87), (.205, 0, .93), TEAK, bev=.003)
        mb.box((-.205, -.03, .50), (.205, 0, .55), TEAK, bev=.003)
        for i in range(6):                                   # back slats
            x = -.16 + .064 * i
            mb.box((x - .0175, -.022, .55), (x + .0175, -.006, .87), TEAK)
        for i in range(7):                                   # seat slats, folded flat
            z = .12 + .07 * i
            mb.box((-.16, -.055, z), (.16, -.035, z + .045), TEAK)
        mb.box((-.12, -.085, .20), (.12, -.065, .245), TEAK)

    def lean(x, deg, dy=0.0, top=.95):                       # back foot on the paving, top `top` up the back touching the wall
        a = math.radians(deg)
        mb.at(Matrix.Translation((x, VY1 - .003 - top * math.sin(a) - dy, ZP)) @ Matrix.Rotation(-a, 4, 'X'))

    lean(1.80, 6, top=.90)                                   # oval top 0.6 wide x 0.9 tall on its end, slats along its length
    for i in range(6):                                       # ponytail: square slat ends, the oval is in the slat lengths
        x = -.25 + .10 * i
        hh = .45 * math.sqrt(max(.05, 1 - (x / .31) ** 2))
        mb.box((x - .043, -.045, .45 - hh), (x + .043, -.018, .45 + hh), TEAK, bev=.002)
    for z in (.22, .68):                                     # cross battens behind
        mb.box((-.22, -.018, z - .02), (.22, 0, z + .02), TEAK)
    for x in (0.70, 1.22):                                   # chairs x 0.45..1.47; the window cill (Z 0.67) is above them
        lean(x, 14, .028)
        chair()
    mb.at()
    ctx.add(mb.finish('shed.garden_furniture'), ROOM, 'furn', plan_sym='console', lm='static')


def pine_box(ctx):
    """Pale new-pine box with a slatted lid and a small square opening at the east end of its front, x 1.6..2.3,
    y 26.1..26.5 (v13 f_0216; v2_t194). It clears the west door leaf at 100 degrees by 0.12."""
    mb, ZP = mo.MB(), W.ZP
    pine, edge, dark = C('#DCC79C', 0.7), C('#CDB585', 0.75), C('#1E1A16', 0.95)
    # 0.84 x 0.50 x 0.45 (crit shed-03: g216_ver 173 px/m, front edge 145 px, top depth 63 px; v2_t188 h/w 0.54); the east
    # edge stays at 2.33 so the west door leaf at 100 degrees still clears it
    x0, x1, y0, y1, h = 1.49, 2.33, VY1 - 0.70, VY1 - 0.20, 0.45
    mb.box((x0 + .01, y0 + .01, ZP + .02), (x1 - .01, y1 - .01, ZP + h - .025), pine, bev=.003)
    for x in (x0, x1 - .04):                                 # corner posts
        for y in (y0, y1 - .04):
            mb.box((x, y, ZP), (x + .04, y + .04, ZP + h - .025), edge, bev=.004)
    for i in range(4):                                       # front cladding: four boards with 4 mm shadow gaps
        z = .02 + .1015 * i
        mb.box((x0 + .04, y0 + .006, ZP + z), (x1 - .04, y0 + .01, ZP + z + .0975), pine)
    d0, d1 = x1 - .33, x1 - .18                              # square doorway 0.15 x 0.18, 0.18..0.33 from the east end
    mb.box((d0, y0 + .005, ZP + .05), (d1, y0 + .0062, ZP + .23), dark)                     # dark inside
    for a, b in (((d0 - .015, ZP + .035), (d0, ZP + .245)), ((d1, ZP + .035), (d1 + .015, ZP + .245)),
                 ((d0 - .015, ZP + .23), (d1 + .015, ZP + .245))):                       # its trim
        mb.box((a[0], y0 - .004, a[1]), (b[0], y0 + .006, b[1]), edge, bev=.002)
    for i in range(5):                                       # lid: five slats along the box
        y = y0 - .01 + .104 * i
        mb.box((x0 - .01, y, ZP + h - .025), (x1 + .01, y + .098, ZP + h - .003), pine, bev=.002)
    for x in (x0 + .06, x1 - .10):                           # lid battens under the overhang
        mb.box((x, y0 + .01, ZP + h - .045), (x + .04, y1 - .01, ZP + h - .025), edge)
    ctx.add(mb.finish('shed.chest'), ROOM, 'furn', plan_sym='chest', lm='static')


def veranda(ctx):
    ZP, ZS = W.ZP, W.ZS
    garden_furniture(ctx)
    pine_box(ctx)

    mb = mo.MB()                                             # black glazed pot with its lid in front of the chairs (1.25, 25.8)
    glaze = C('#1E1E20', 0.25)                               # 0.42 wide x 0.38 high (g216_ver 72 px at 173 px/m; v2_t188 h/w 0.9)
    mb.at(Matrix.Translation((1.25, VY0 + .78, ZP)) @ Matrix.Diagonal((1.35, 1.35, 1.2, 1)))
    mb.lathe([(0, 0), (.10, 0), (.125, .03), (.155, .10), (.15, .17), (.125, .22), (.118, .235), (.13, .24), (.125, .25),
              (.11, .25), (.10, .235)], glaze, 18)
    mb.lathe([(0, .228), (.115, .228), (.112, .245), (.08, .275), (.03, .29), (.022, .305), (.03, .315), (0, .318)], glaze, 18)
    mb.at()
    ctx.add(mb.finish('shed.pot'), ROOM, 'decor', plan_sym='plant', lm='static')

    # storage rack against the wing wall: pale new-pine posts at the two ends only, grey plank shelves at 0.48 / 0.75 /
    # 1.00 and nothing under the lowest (v2_t304: front post 312 : 170 : 170 px from the paving; compost bags omitted)
    mb = mo.MB()
    tan, plank = C('#CDB884', 0.85), C('#8C7B66', 0.9)
    x0, x1, y0, y1 = VX1 - .37, VX1 - .02, VY0 + .23, VY1 - .10        # x 3.85..4.20, y 25.25..26.60 (v13 f_0216)
    for x in (x0, x1 - .045):
        for y in (y0, y1 - .045):
            mb.box((x, y, ZP), (x + .045, y + .045, ZP + 1.05), tan, grain=2, bev=.003)
    for z in (0.48, 0.75, 1.00):
        for y in (y0 + .045, (y0 + y1) / 2 - .011, y1 - .067):        # end bearers and one mid-length bearer
            mb.box((x0, y, ZP + z - .045), (x1, y + .022, ZP + z), tan)
        for x in (x0 - .01, x1 - .035):                      # side rails along the rack
            mb.box((x, y0 - .01, ZP + z - .045), (x + .045, y1 + .01, ZP + z), tan)
        for i in range(3):
            x = x0 + .004 + .122 * i
            mb.box((x, y0 - .01, ZP + z), (x + .116, y1 + .01, ZP + z + .022), plank, bev=.002)
    ctx.add(mb.finish('shed.veranda_rack'), ROOM, 'fit', plan_sym='rack')
    mb, terra = mo.MB(), P.mat('terracotta')                 # v2_t304: terracotta bowl on its saucer at the north end of
    bowl(mb, (VX1 - .20, y1 - .27, ZP + .772), terra, 1.2)   # the middle shelf, the black bowl on the lowest
    bowl(mb, (VX1 - .20, y1 - .27, ZP + .787), terra, 1.0)
    bowl(mb, (VX1 - .21, y1 - .45, ZP + .502), C('#232426', 0.6), 1.2)
    ctx.add(mb.finish('shed.veranda_rack.bowls'), ROOM, 'decor', lm='static')

    # coat-hook rail on the wing wall: seven cream double hooks at 0.18. Board 1.76..1.95 above the paving (crit shed-07:
    # 2.4 brick courses tall in v2_t304, its top 2.0 +/- 0.1 by ratio against the 2.33 door in v2_t188); the hooks sit
    # on its upper half and reach its top edge
    mb, cream = mo.MB(), C('#EDE6D0', 0.35)
    z0, z1, yc = ZP + 1.76, ZP + 1.95, VY0 + .825
    zh = z0 + .07                                            # hook base: top hook tips at z1
    mb.box((VX1 - .02, yc - .625, z0), (VX1, yc + .625, z1), C('#3B2A22', 0.6), bev=.003)
    for i in range(7):
        y = yc + .18 * (i - 3)
        mb.box((VX1 - .028, y - .011, zh - .005), (VX1 - .02, y + .011, zh + .075), cream)
        mb.tube([(VX1 - .024, y, zh + .06), (VX1 - .055, y, zh + .062), (VX1 - .074, y, zh + .085), (VX1 - .07, y, zh + .12)],
                .005, cream, n=6)
        mb.tube([(VX1 - .024, y, zh + .03), (VX1 - .055, y, zh + .007), (VX1 - .083, y, zh + .013), (VX1 - .092, y, zh + .042)],
                .005, cream, n=6)
    ctx.add(mb.finish('shed.hook_rail'), ROOM, 'fit')

    # video doorbell on the 0.485 of brick between the window and the doors, 1.25 above the paving: no logo
    mb, blk, x = mo.MB(), C('#17181A', 0.35), 2.30
    mb.box((x - .031, VY1 - .028, ZP + 1.186), (x + .031, VY1, ZP + 1.314), blk, bev=.005)
    cyl(mb, (x, VY1 - .0315, ZP + 1.217), .015, .004, C('#C9D4DC', 0.3), 'y', 14)
    cyl(mb, (x, VY1 - .0325, ZP + 1.217), .010, .002, blk, 'y', 10)
    cyl(mb, (x, VY1 - .0315, ZP + 1.286), .009, .004, C('#0B0B0C', 0.1), 'y', 10)
    ctx.add(mb.finish('shed.doorbell'), ROOM, 'fit')

    # nest box on the south face of the front pier, 0.20 wide, body 1.85..2.12 above the paving with a gable roof to 2.20
    # (v2_t194: pier 2.40 to the fascia = 615 px, box rows 320..405, px 360..415 at the pier's west edge, the downpipe
    # east of it). It goes west of the site's downpipe where there is room, else east of it (while lib/site.py puts the
    # pipe at x -0.76: the 40 mm store wall is taken as the west parapet)
    global BIRD
    p0, p1 = _downpipe_x((-0.564, -0.496))
    xa = -0.85 if p0 - .02 >= -0.85 + .20 else p1 + .02
    mb, wood, xb = mo.MB(), C('#9A8466', 0.9), xa + .20
    za, zb, zr, yb = ZP + 1.85, ZP + 2.12, ZP + 2.20, VY0
    BIRD = (xa, xb, za, zr)
    xm = (xa + xb) / 2
    mb.prism([(xa, yb - .14, za), (xb, yb - .14, za), (xb, yb - .14, zb), (xm, yb - .14, zr), (xa, yb - .14, zb)],
             (0, .14, 0), wood)
    for s in (-1, 1):                                        # roof boards, 15 mm overhang
        e = xa - .012 if s < 0 else xb + .012
        mb.prism([(xm, yb - .16, zr + .018), (xm, yb - .16, zr), (e, yb - .16, zb - .012), (e, yb - .16, zb + .006)],
                 (0, .16, 0), C('#7E6A50', 0.9))
    cyl(mb, (xm, yb - .141, za + .18), .016, .0015, C('#0B0B0C', 0.9), 'y', 12)           # entrance hole
    cyl(mb, (xm, yb - .18, za + .12), .004, .04, wood, 'y', 6)                          # perch peg
    ctx.add(mb.finish('shed.bird_box'), ROOM, 'decor', lm='static')

    mb, stone = mo.MB(), C('#8F8F8A', 0.9)                   # two cast-stone sitting cats, (1.75, 25.75)
    for x, y, deg in ((1.68, VY0 + .72, 200), (1.84, VY0 + .75, 165)):
        T = Matrix.Translation((x, y, ZP)) @ Matrix.Rotation(math.radians(deg), 4, 'Z')
        mb.at(T)
        mb.lathe([(0, 0), (.05, 0), (.058, .03), (.05, .08), (.032, .12), (0, .128)], stone, 10, ell=(1.0, 1.25))
        mb.tube([(.045, .04, .012), (.062, -.02, .012), (.035, -.065, .012)], .008, stone, n=5)
        mb.at(T @ Matrix.Translation((0, -.012, .146)))
        mb.lathe([(.034 * math.sin(math.pi * k / 6), -.034 * math.cos(math.pi * k / 6)) for k in range(7)], stone, 10)
        for sx in (-1, 1):
            mb.at(T @ Matrix.Translation((sx * .02, -.012, .164)))
            mb.lathe([(0, 0), (.014, 0), (0, .032)], stone, 5)
    mb.at()
    ctx.add(mb.finish('shed.stone_cats'), ROOM, 'decor', lm='static')

    # grey door mat 1.0 x 0.6 in front of the west leaf (v13 f_0216: x 2.55..3.55, y 0.05..0.6 off the wall)
    for name, w, d, th, col in (('shed.mat.edge', 1.00, .60, .008, '#2E2E30'), ('shed.mat', .95, .55, .011, '#8E8E8C')):
        mat = P.place(P.rug(w=w, d=d, thickness=th, corner_r=.05, color=col, name=name), (3.05, VY1 - .34, ZP))
        ctx.add(mat, ROOM, 'decor', plan_sym='rug' if name == 'shed.mat' else None, lm='static')

    mb, joint = mo.MB(), C('#2A1712', 0.8)                   # V-joints at 95 mm on site's E-W soffit boards
    k = 1
    while VY0 + .095 * k < VY1 - .03:
        y = VY0 + .095 * k
        k += 1
        if VY0 + .09 < y < VY0 + .18:                        # the soffit vent strip (site: y0 + 0.10 .. 0.17)
            continue
        xa = VX0 if y < SY0 else SX1 + .02                   # behind the pier the soffit runs on to the store doors
        mb.box((xa, y - .002, ZS - .001), (VX1, y + .002, ZS + .0005), joint)
    ctx.add(mb.finish('shed.soffit_boards.joints'), ROOM, 'fit')
    # soffit downlights: three on the centre line, a fourth by the front edge at the west end (shed.md 8)
    for i, (x, y) in enumerate(((0.33, VY0 + .85), (2.03, VY0 + .85), (3.43, VY0 + .85), (0.25, VY0 + .38))):
        lighting.downlight(ctx, ROOM, x, y, z=ZS - .015, watts=22, name=f'shed.veranda_light.{i}')
        ctx.add(P.place(P.downlight(dia=.09, name=f'shed.veranda_light_trim.{i}'), (x, y, ZS)), ROOM, 'light')


def wisteria(ctx):
    """Climber up the front pier, over its top and along the western 2 m of the fascia (v2_t194, v11 f_0194, v13 f_0216).
    It grows in the lavender bed and hangs over the lawn, so it is tagged 'garden' (lit by the garden probe)."""
    rnd, mb, ZP = random.Random(7), mo.MB(), W.ZP
    leaf = [P.two_sided(C(h, 0.5)) for h in ('#7FA050', '#93AE58', '#6C8F48')]
    bark = P.mat('bark')
    yf = VY0 - .03                                           # in front of the pier face, under the gutter (rim 2.29)
    # trunk east of the downpipe (x -0.53, r 0.034) on the pier's south face, as in v2_t194; the bird box stays clear
    stem = [Vector(p) for p in ((-.40, yf, ZP - .05), (-.39, yf, .30), (-.40, yf, .95), (-.385, yf, 1.55),
                                (-.39, yf - .04, 1.92), (-.1, yf - .06, 2.03), (.55, yf - .06, 2.00), (1.15, yf - .06, 2.03))]
    xa, xb, za, zr = BIRD
    box_lo, box_hi = Vector((xa - .1, VY0 - .26, za - .1)), Vector((xb + .1, VY0 + .05, zr + .1))   # bird box + 0.1
    mb.tube(stem[:5], .014, bark, n=5)
    mb.tube(stem[4:], .009, bark, n=5)
    for k in range(130):
        t = rnd.uniform(1.4, len(stem) - 1.001)              # start on the upper pier or along the fascia
        i = int(t)
        p = stem[i].lerp(stem[i + 1], t - i)
        out = Vector((rnd.uniform(-.5, .5), rnd.uniform(-1, -.1), rnd.uniform(-.2, .5))).normalized()
        if p.x < -0.1:                                       # over the pier: grow east, the box and downpipe stay in view
            out.x = abs(out.x)
        n, step, pts = rnd.randint(6, 9), rnd.uniform(.045, .065), [p.copy()]
        for j in range(n):                                   # a twig that arches out, then droops
            out = (out + Vector((0, 0, -.22))).normalized()
            pts.append(pts[-1] + out * step)
        if any(all(lo <= c <= hi for lo, c, hi in zip(box_lo, q, box_hi)) for q in pts):
            continue                                         # would grow into the bird box
        mb.tube(pts, .003, bark, n=3)
        side = Vector((out.y, -out.x, 0)).normalized() if abs(out.z) < .99 else Vector((1, 0, 0))
        for j in range(1, n + 1):                            # leaflets in pairs
            for s in (-1, 1):
                d = (side * s + Vector((0, 0, -.55)) + out * .4).normalized()
                L, w = rnd.uniform(.06, .09), rnd.uniform(.014, .02)
                b = d.cross(Vector((rnd.uniform(-.3, .3), 1, rnd.uniform(-.3, .3)))).normalized() * w
                q = pts[j]
                mb.face([q, q + d * L * .45 + b, q + d * L, q + d * L * .45 - b], leaf[(k + j) % 3])
    ctx.add(mb.finish('garden.shed_wisteria', sharp_deg=180), 'garden', 'decor')


# ------------------------------------------------------------------ store cupboard behind the oxblood doors
def store(ctx):
    ZP = W.ZP
    x0, x1, y0, y1 = SX0, SX0 + .34, SY0, SY1               # shelves on the west wall: the doors' inside stays clear
    mb, soft, blk = mo.MB(), C('#C9B48A', 0.85), C('#1B1B1C', 0.7)
    tops = (ZP + 0.75, ZP + 1.25, ZP + 1.70)
    for i, z in enumerate(tops):
        mb.box((x0, y0, z - .03), (x1, y1, z), soft, bev=.002)
        for y in (y0, y1 - .022):
            mb.box((x0, y, z - .075), (x1, y + .022, z - .03), soft)                          # bearers on the side walls
        mb.box((x0, y0 + .022, z - .075), (x0 + .022, y1 - .022, z - .03), soft)              # and on the back wall
        if i < 2:
            mb.box((x0, y0, z), (x1 - .004, y1, z + .004), blk)                               # black board lining
    mb.box((SX1 - .034, y0 + .002, ZP + .10), (SX1 - .018, y0 + .020, ZP + 1.95), 'plastic_white')   # LED batten, south jamb
    mb.box((SX1 - .0335, y0 + .020, ZP + .12), (SX1 - .0185, y0 + .0215, ZP + 1.93), P.emissive('#F4CB94', 3.0))
    ctx.add(mb.finish('shed.store.shelves'), ROOM, 'fit', plan_sym='shelf')
    lighting.strip(ctx, ROOM, (SX1 - .026, y0 + .045, ZP + .12), (SX1 - .026, y0 + .045, ZP + 1.93), watts_per_m=12,
                   direction=(-.45, 1, 0), name='shed.store.light')

    mb = mo.MB()                                             # generic contents, blank labels (v2_t264)
    lid = C('#A9ADB0', 0.35, 0.8)
    xc = (x0 + x1) / 2
    z = tops[1] + .004
    for dy, r, h, body, band in ((.15, .095, .20, '#E9E7E0', '#B9C2C8'), (.37, .09, .21, '#C2C5C8', '#E6E3DA'),
                                 (.57, .085, .19, '#E9E7E0', '#8D9AA3'), (.79, .10, .20, '#54667A', '#D9D5C8')):
        cyl(mb, (xc, y0 + dy, z), r, h, C(body, 0.45), segs=20)
        cyl(mb, (xc, y0 + dy, z + h * .25), r + .0015, h * .45, C(band, 0.6), segs=20)
        cyl(mb, (xc, y0 + dy, z + h), r * .97, .008, lid, segs=20)
    bowl(mb, (xc, y0 + 1.08, z), P.mat('terracotta'), 1.0)
    z = tops[0] + .004
    cyl(mb, (xc + .01, y0 + .17, z), .09, .19, C('#C2C5C8', 0.45), segs=20)                  # fifth tin
    cyl(mb, (xc + .01, y0 + .17, z + .19), .087, .008, lid, segs=20)
    bowl(mb, (xc, y0 + .47, z), C('#8E9296', 0.4, 0.6), 1.2)
    hose = C('#3F6B45', 0.6)                                                                   # coiled hose
    for k in range(3):
        mb.tube([(xc + .135 * math.cos(a), y0 + .92 + .135 * math.sin(a), z + .013 + .024 * k)
                 for a in (2 * math.pi * i / 20 for i in range(20))], .012, hose, n=6, closed=True, up=(0, 0, 1))
    z = tops[2]
    for dy, col in ((.20, '#E9E7E0'), (.40, '#D9B93A')):                                       # two plain cans
        mb.box((xc - .10, y0 + dy, z), (xc + .10, y0 + dy + .13, z + .26), C(col, 0.5), bev=.012)
        cyl(mb, (xc, y0 + dy + .065, z + .26), .02, .02, C('#2A2A2C', 0.5), segs=8)
    mb.at(Matrix.Translation((SX0 + .185, y0 + .32, ZP)))                                      # black tub on the floor
    mb.lathe([(0, 0), (.125, 0), (.16, .24), (.172, .24), (.172, .25), (.155, .25), (.118, .015), (0, .015)], blk, 16)
    mb.at()
    ctx.add(mb.finish('shed.store.contents'), ROOM, 'decor', lm='static')


# ------------------------------------------------------------------ workshop lights and the one switch
def workshop_lights(ctx):
    X0, X1, Y0, Y1, ZF, ZC = W.X0, W.X1, W.Y0, W.Y1, W.ZF, W.ZC
    ya, yb = Y0 + 1.02, Y0 + 2.47                            # 2 x 3 recessed downlights (shed.md 8), x as phase 2
    for i, (x, y) in enumerate((x, y) for y in (ya, yb) for x in (X0 + 0.93, X0 + 2.38, X0 + 3.83)):
        lighting.downlight(ctx, ROOM, x, y, z=ZC - .015, watts=80, kelvin=3000, name=f'shed.downlight.{i}')
        ctx.add(P.place(P.downlight(name=f'shed.downlight_trim.{i}'), (x, y, ZC)), ROOM, 'light')
    f = ctx.opening_frame('shed_d1')                         # round surface fitting just inside the French doors (v2 f_0281)
    mb, x, y = mo.MB(), f['center'][0], Y0 + 0.52
    cyl(mb, (x, y, ZC - .022), .12, .022, 'plastic_white', segs=20)
    cyl(mb, (x, y, ZC - .05), .10, .028, P.emissive('#F4CB94', 5.0), segs=20)
    ctx.add(mb.finish('shed.ceiling_light'), ROOM, 'light')
    lighting.bulb(ctx, ROOM, (x, y, ZC - .09), watts=25, kelvin=2850, radius=.03, name='shed.ceiling_light.bulb')

    # [round 4] daylight (IX-04 / Q7): with the lamps off the bake left the workshop black (lights-off probe mean 0.005)
    # where v2 f_0279-0291 shows a daylit room; soft panels inside the glazed front and the misted rear window
    lighting.daylight_fill(ctx, ROOM, 'shed.daylight.front', ((X0 + X1) / 2, Y0 + .05, 0.85), (4.4, 1.6), (0, 1, 0), 45)
    w2 = ctx.opening_frame('shed_w2')
    lighting.daylight_fill(ctx, ROOM, 'shed.daylight.rear', (w2['center'][0], Y1 - .04, w2['center'][2] + w2['height'] / 2),
                           (1.7, 0.9), (0, -1, 0), 14)

    sw = P.place(P.switch_plate(1, name='shed.switch'), (X1, Y0 + 0.24, ZF + 1.2), facing=(-1, 0))   # inside, wing-wall side
    IX.tag(sw, 'light', rooms=[ROOM], label='Shed lights')   # one plate drives workshop, store and veranda lights
    ctx.add(sw, ROOM, 'fit', lm='dynamic')


def build(ctx):
    W.setup(ctx)
    frame(ctx)
    veranda(ctx)
    wisteria(ctx)
    store(ctx)
    W.build(ctx, ROOM)
    workshop_lights(ctx)

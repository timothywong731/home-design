"""shed - brick garden building: veranda, store cupboard, workshop (spec/rooms/shed.md).

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --only shell,site,envelope,shed --preview shed --res 540x960 --samples 64 --tag shed
    (no --levels: the shed's doors and windows are only built with the whole shell; add --pose 1 --tag shed1 for the open state)

The site stage built walls, roof, soffit, fascia, paving and the two rooms; joinery built the store doors, the French
doors and both windows with their interaction tags. This module adds the furniture, the fittings, the lights and their
switch. World = shed-local + (-0.87, 23.40), z_world = z_local - 0.42. Workshop interior: rooms/shed_workshop.py.
"""
import math
import random

from mathutils import Matrix, Vector

from lib import interact as IX, lighting, materials as M, mouldings as mo, props as P, shell
from rooms import shed_workshop as W
from rooms.shed_workshop import C, cyl, PINE, ZP, ZF, ZC, ZS

ROOM = 'shed'            # building rooms shed_workshop / shed_store are geometry ids only: every object is tagged 'shed'

CAMERAS = [
    dict(name='front', pos=(1.3, 20.6, 1.25), look=(2.0, 25.0, 0.6), fov_deg=95, ref='v2_t188'),
    dict(name='veranda_w', pos=(3.4, 24.0, 1.1), look=(-0.4, 24.5, 0.6), fov_deg=100, ref='v2:f_0257'),
    dict(name='veranda_e', pos=(0.9, 24.1, 1.1), look=(4.2, 24.6, 0.6), fov_deg=100, ref='v2:f_0275'),
    dict(name='rack', pos=(2.6, 23.9, 1.05), look=(4.2, 24.1, 0.35), fov_deg=95, ref='v2:f_0305'),
    dict(name='store', pos=(0.75, 24.35, 1.0), look=(-0.6, 24.37, 0.45), fov_deg=95, ref='v2:f_0265'),
    dict(name='ws_back', pos=(3.35, 25.5, 1.15), look=(1.2, 28.6, 0.5), fov_deg=100, ref='v2:f_0291'),
    dict(name='ws_east', pos=(2.4, 25.5, 1.15), look=(4.2, 28.4, 0.3), fov_deg=100, ref='v2:f_0281'),
    dict(name='ws_door', pos=(-0.3, 27.75, 1.2), look=(3.6, 25.3, 0.5), fov_deg=100, ref=None),
    dict(name='switch', pos=(2.9, 26.4, 1.1), look=(4.18, 25.45, 0.8), fov_deg=80, ref=None),
    dict(name='ws_west', pos=(3.4, 27.76, 1.2), look=(-0.6, 27.6, 0.6), fov_deg=100, ref='v2:f_0291'),
    dict(name='pier', pos=(2.3, 20.3, 1.5), look=(0.0, 23.6, 0.6), fov_deg=90, ref='v2_t194'),
    dict(name='store_shut', pos=(-0.405, 24.95, 1.25), look=(-0.72, 23.95, 0.35), fov_deg=110, ref='v2:f_0267'),
]

TEAK = 'oak_rustic'                                          # weathered honey-brown teak #A9824F
BOWL = [(0, 0), (.06, 0), (.12, .06), (.125, .07), (.115, .07), (.055, .012), (0, .012)]     # shallow bowl, r 0.125


def bowl(mb, p, mat, s=1.0):
    mb.at(Matrix.Translation(p) @ Matrix.Scale(s, 4))
    mb.lathe(BOWL, mat, 14)
    mb.at()


# ------------------------------------------------------------------ veranda
def garden_furniture(ctx):
    """Two folded teak chairs under the left of window W1, the oval table top on its end to their right, behind the chest
    (v2_t188, v2_t194)."""
    mb = mo.MB()

    def chair():                                             # folded: 0.50 x 0.09 x 0.95; back on y = 0, front -Y
        for sx in (-1, 1):
            mb.box((sx * .25, -.03, 0), (sx * .205, 0, .95), TEAK)
            mb.box((sx * .20, -.06, .03), (sx * .16, -.03, .80), TEAK)
            mb.box((sx * .155, -.09, 0), (sx * .12, -.06, .72), TEAK)
        mb.box((-.205, -.03, .87), (.205, 0, .93), TEAK)
        mb.box((-.205, -.03, .50), (.205, 0, .55), TEAK)
        for i in range(6):                                   # back slats
            x = -.16 + .064 * i
            mb.box((x - .0175, -.022, .55), (x + .0175, -.006, .87), TEAK)
        for i in range(7):                                   # seat slats, folded flat
            z = .12 + .07 * i
            mb.box((-.16, -.055, z), (.16, -.035, z + .045), TEAK)
        mb.box((-.12, -.085, .20), (.12, -.065, .245), TEAK)

    def lean(x, deg, dy=0.0, top=.95):                       # back foot on the paving, top `top` up the back touching the wall
        a = math.radians(deg)
        mb.at(Matrix.Translation((x, 25.0 - .003 - top * math.sin(a) - dy, ZP)) @ Matrix.Rotation(-a, 4, 'X'))

    lean(2.28, 6, top=.90)                                   # oval top 0.6 wide x 0.9 tall on its end, slats along its length
    for i in range(6):                                       # ponytail: square slat ends, the oval is in the slat lengths
        x = -.25 + .10 * i
        hh = .45 * math.sqrt(max(.05, 1 - (x / .31) ** 2))
        mb.box((x - .043, -.045, .45 - hh), (x + .043, -.018, .45 + hh), TEAK)
    for z in (.22, .68):                                     # cross battens behind
        mb.box((-.22, -.018, z - .02), (.22, 0, z + .02), TEAK)
    for x in (1.27, 1.77):                                   # chairs x 1.02-2.02: chest (lid from 2.04) stays clear
        lean(x, 14, .028)
        chair()
    mb.at()
    ctx.add(mb.finish('shed.garden_furniture'), ROOM, 'furn', plan_sym='console', lm='static')


def veranda(ctx):
    garden_furniture(ctx)

    mb, pine = mo.MB(), C('#DCC79C', 0.7)                    # plain pine chest with a slatted lid
    x0, x1, y0, y1 = 2.05, 2.60, 24.48, 24.83                # 0.13 west of the spec: clear of the west door leaf at 100 degrees;
                                                             # 0.17 off the wall: the oval top leans behind it
    mb.box((x0 + .01, y0 + .01, ZP + .02), (x1 - .01, y1 - .01, ZP + .31), pine, bev=.003)
    for x in (x0, x1 - .04):
        for y in (y0, y1 - .04):
            mb.box((x, y, ZP), (x + .04, y + .04, ZP + .31), pine)
    for i in range(5):
        y = y0 - .01 + .075 * i
        mb.box((x0 - .01, y, ZP + .31), (x1 + .01, y + .068, ZP + .332), pine, bev=.002)
    ctx.add(mb.finish('shed.chest'), ROOM, 'furn', plan_sym='chest', lm='static')

    mb = mo.MB()                                             # storage rack against the wing wall: tanalised posts, plank shelves
    tan, plank = C('#A9A070', 0.85), C('#8C7B66', 0.9)
    x0, x1, y0, y1 = 3.80, 4.20, 23.43, 24.36                # moved 0.25 south and 0.12 shorter: clear of the east door leaf
    for x in (x0, x1 - .045):
        for y in (y0, y1 - .045):
            mb.box((x, y, ZP), (x + .045, y + .045, ZP + 1.0), tan, grain=2)
    for z in (0.10, 0.50, 0.95):
        for y in (y0 + .045, y1 - .067):
            mb.box((x0, y, ZP + z - .045), (x1, y + .022, ZP + z), tan)
        for i in range(3):
            x = x0 + .004 + .132 * i
            mb.box((x, y0 - .01, ZP + z), (x + .128, y1 + .01, ZP + z + .022), plank)
    ctx.add(mb.finish('shed.veranda_rack'), ROOM, 'fit', plan_sym='rack')
    mb, terra = mo.MB(), P.mat('terracotta')
    bowl(mb, (4.00, 23.72, ZP + .522), terra, 1.1)
    bowl(mb, (4.01, 24.08, ZP + .522), terra, 0.8)
    bowl(mb, (3.99, 23.9, ZP + .122), C('#232426', 0.6), 1.2)
    ctx.add(mb.finish('shed.veranda_rack.bowls'), ROOM, 'decor', lm='static')

    mb = mo.MB()                                             # coat-hook rail on the wing wall: seven cream double hooks
    cream = C('#EDE6D0', 0.35)
    mb.box((4.20, 23.60, 1.13), (4.22, 24.85, 1.22), C('#3B2A22', 0.6))
    for i in range(7):
        y = 24.225 + .18 * (i - 3)
        mb.box((4.192, y - .011, 1.142), (4.20, y + .011, 1.208), cream)
        mb.tube([(4.196, y, 1.19), (4.165, y, 1.192), (4.146, y, 1.215), (4.15, y, 1.25)], .005, cream, n=6)
        mb.tube([(4.196, y, 1.16), (4.165, y, 1.137), (4.137, y, 1.143), (4.128, y, 1.172)], .005, cream, n=6)
    ctx.add(mb.finish('shed.hook_rail'), ROOM, 'fit')

    mb, blk = mo.MB(), C('#17181A', 0.35)                    # video doorbell between the window and the doors: no logo
    mb.box((2.569, 24.972, .766), (2.631, 25.0, .894), blk, bev=.005)
    cyl(mb, (2.60, 24.9685, .797), .015, .004, C('#C9D4DC', 0.3), 'y', 14)
    cyl(mb, (2.60, 24.9675, .797), .010, .002, blk, 'y', 10)
    cyl(mb, (2.60, 24.9685, .866), .009, .004, C('#0B0B0C', 0.1), 'y', 10)
    ctx.add(mb.finish('shed.doorbell'), ROOM, 'fit')

    mb, wood = mo.MB(), C('#9A8466', 0.9)                    # nest box on the south face of the SW pier
    mb.box((-.735, 23.28, 1.38), (-.585, 23.40, 1.58), wood)
    mb.prism([(-.75, 23.255, 1.555), (-.75, 23.40, 1.63), (-.75, 23.40, 1.652), (-.75, 23.255, 1.577)], (.18, 0, 0), wood)
    cyl(mb, (-.66, 23.2775, 1.50), .016, .003, C('#0B0B0C', 0.9), 'y', 10)
    ctx.add(mb.finish('shed.bird_box'), ROOM, 'decor', lm='static')

    mb, stone = mo.MB(), C('#8F8F8A', 0.9)                   # two cast-stone sitting cats
    for x, y, deg in ((2.10, 24.30, 200), (2.31, 24.34, 165)):
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

    for name, w, d, th, col in (('shed.mat.edge', .77, .52, .008, '#2E2E30'), ('shed.mat', .72, .47, .011, '#8E8E8C')):
        mat = P.place(P.rug(w=w, d=d, thickness=th, corner_r=.05, color=col, name=name), (3.35, 24.62, ZP))
        ctx.add(mat, ROOM, 'decor', plan_sym='rug' if name == 'shed.mat' else None, lm='static')

    # ponytail: 2 mm cover over site's soffit ('mahogany_dark' renders black under the canopy; spec #5A3229, red-brown
    # T&G boards E-W in v2:f_0273). Drop it, and the 2 mm on the trims, once site.SOFFIT is a lighter board.
    ob = shell.box('shed.soffit_boards', -0.36, 4.23, 23.39, 25.01, ZS - .002, ZS, 'mahogany_mid')    # edges into the walls
    M.uv_box(ob, rotate=True)                                # grain E-W
    ctx.add(ob, ROOM, 'fit')
    mb, joint = mo.MB(), C('#2A1712', 0.8)                   # V-joints at 95 mm
    for k in range(1, 17):
        y = 23.40 + .095 * k
        mb.box((-0.36, y - .002, ZS - .0025), (4.23, y + .002, ZS - .002), joint)
    ctx.add(mb.finish('shed.soffit_boards.joints'), ROOM, 'fit')
    for i, (x, y) in enumerate(((0.33, 24.25), (2.03, 24.25), (3.43, 24.25), (0.13, 23.75))):      # soffit downlights
        lighting.downlight(ctx, ROOM, x, y, z=ZS - .015, watts=22, name=f'shed.veranda_light.{i}')
        ctx.add(P.place(P.downlight(dia=.09, name=f'shed.veranda_light_trim.{i}'), (x, y, ZS - .0026)), ROOM, 'light')


def wisteria(ctx):
    """Climber up the SW pier and along the western 2 m of the fascia. It grows in the garden bed and hangs over the lawn,
    so it is tagged 'garden' (lit by the garden probe, not by the one inside the workshop)."""
    rnd, mb = random.Random(7), mo.MB()
    leaf = [P.two_sided(C(h, 0.5)) for h in ('#7FA050', '#93AE58', '#6C8F48')]
    bark = P.mat('bark')
    # trunk east of the downpipe (x -0.45, r 0.034) on the pier's SE corner, as in v2_t194; the bird box stays clear
    stem = [Vector(p) for p in ((-.385, 23.36, ZP - .05), (-.375, 23.37, .30), (-.385, 23.37, .95), (-.372, 23.37, 1.55),
                                (-.38, 23.31, 1.93), (-.1, 23.27, 1.99), (.55, 23.27, 1.96), (1.15, 23.27, 1.99))]
    box_lo, box_hi = Vector((-.85, 23.15, 1.28)), Vector((-.47, 23.45, 1.75))     # bird box grown by ~0.1 (leaf length)
    mb.tube(stem[:5], .014, bark, n=5)
    mb.tube(stem[4:], .009, bark, n=5)
    for k in range(95):
        t = rnd.uniform(1.6, len(stem) - 1.001)              # start on the upper pier or along the fascia
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
    x0, x1, y0, y1 = -0.77, -0.45, 23.75, 24.98              # shelves 0.32 deep: the strip light on the jamb reaches every bay
    mb, soft, blk = mo.MB(), C('#C9B48A', 0.85), C('#1B1B1C', 0.7)
    tops = (ZP + 0.75, ZP + 1.25, ZP + 1.70)
    for i, z in enumerate(tops):
        mb.box((x0, y0, z - .03), (x1, y1, z), soft)
        for y in (y0, y1 - .022):
            mb.box((x0, y, z - .075), (x1, y + .022, z - .03), soft)
        if i < 2:
            mb.box((x0, y0, z), (x1 - .004, y1, z + .004), blk)                               # black board lining
    mb.box((-.404, y0 + .002, ZP + .10), (-.388, y0 + .020, ZP + 1.95), 'plastic_white')      # LED batten on the south jamb
    mb.box((-.4035, y0 + .020, ZP + .12), (-.3885, y0 + .0215, ZP + 1.93), P.emissive('#F4CB94', 3.0))
    ctx.add(mb.finish('shed.store.shelves'), ROOM, 'fit')
    lighting.strip(ctx, ROOM, (-.396, y0 + .045, ZP + .12), (-.396, y0 + .045, ZP + 1.93), watts_per_m=12,
                   direction=(-.45, 1, 0), name='shed.store.light')

    mb = mo.MB()                                             # generic contents, blank labels
    lid = C('#A9ADB0', 0.35, 0.8)
    z = tops[1] + .004
    for y, r, h, body, band in ((23.89, .095, .20, '#E9E7E0', '#B9C2C8'), (24.10, .09, .21, '#C2C5C8', '#E6E3DA'),
                                (24.29, .085, .19, '#E9E7E0', '#8D9AA3'), (24.49, .10, .20, '#54667A', '#D9D5C8')):
        cyl(mb, (-.61, y, z), r, h, C(body, 0.45), segs=14)
        cyl(mb, (-.61, y, z + h * .25), r + .0015, h * .45, C(band, 0.6), segs=14)
        cyl(mb, (-.61, y, z + h), r * .97, .008, lid, segs=14)
    bowl(mb, (-.61, 24.76, z), P.mat('terracotta'), 1.0)
    z = tops[0] + .004
    cyl(mb, (-.60, 23.92, z), .09, .19, C('#C2C5C8', 0.45), segs=14)                          # fifth tin
    cyl(mb, (-.60, 23.92, z + .19), .087, .008, lid, segs=14)
    bowl(mb, (-.61, 24.20, z), C('#8E9296', 0.4, 0.6), 1.2)
    hose = C('#3F6B45', 0.6)                                                                   # coiled hose
    for k in range(3):
        mb.tube([(-.61 + .135 * math.cos(a), 24.62 + .135 * math.sin(a), z + .013 + .024 * k)
                 for a in (2 * math.pi * i / 14 for i in range(14))], .012, hose, n=6, closed=True, up=(0, 0, 1))
    z = tops[2]
    for y, col in ((23.95, '#E9E7E0'), (24.14, '#D9B93A')):                                    # two plain cans
        mb.box((-.71, y, z), (-.51, y + .13, z + .26), C(col, 0.5), bev=.012)
        cyl(mb, (-.61, y + .065, z + .26), .02, .02, C('#2A2A2C', 0.5), segs=8)
    mb.at(Matrix.Translation((-.585, 24.05, ZP)))                                              # black tub on the floor
    mb.lathe([(0, 0), (.125, 0), (.16, .24), (.172, .24), (.172, .25), (.155, .25), (.118, .015), (0, .015)], blk, 16)
    mb.at()
    ctx.add(mb.finish('shed.store.contents'), ROOM, 'decor', lm='static')


# ------------------------------------------------------------------ workshop lights and the one switch
def workshop_lights(ctx):
    for i, (x, y) in enumerate((x, y) for y in (26.20, 27.70) for x in (0.33, 1.78, 3.23)):       # 2 x 3 recessed downlights
        lighting.downlight(ctx, ROOM, x, y, z=ZC - .015, watts=80, kelvin=3000, name=f'shed.downlight.{i}')
        ctx.add(P.place(P.downlight(name=f'shed.downlight_trim.{i}'), (x, y, ZC)), ROOM, 'light')
    mb, x, y = mo.MB(), 3.35, 25.80                                                                # round surface fitting by the doors
    cyl(mb, (x, y, ZC - .022), .12, .022, 'plastic_white', segs=20)
    cyl(mb, (x, y, ZC - .05), .10, .028, P.emissive('#F4CB94', 5.0), segs=20)
    ctx.add(mb.finish('shed.ceiling_light'), ROOM, 'light')
    lighting.bulb(ctx, ROOM, (x, y, ZC - .09), watts=25, kelvin=2850, radius=.03, name='shed.ceiling_light.bulb')

    sw = P.place(P.switch_plate(1, name='shed.switch'), (W.X1, 25.52, ZF + 1.2), facing=(-1, 0))   # inside, wing-wall side
    IX.tag(sw, 'light', rooms=[ROOM], label='Shed lights')   # one plate drives workshop, store and veranda lights
    ctx.add(sw, ROOM, 'fit', lm='dynamic')


def build(ctx):
    veranda(ctx)
    wisteria(ctx)
    store(ctx)
    W.build(ctx, ROOM)
    workshop_lights(ctx)

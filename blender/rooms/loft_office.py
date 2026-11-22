"""Slate Room: second-floor front room in the converted loft (id loft_office; spec/rooms/loft_office.md,
spec/phase3/briefs/loft_office.md; footage v5 f_0170-f_0262, v12 f1-14 / f37-80 / f118-122).

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --levels 2,X --only shell,envelope,loft_office \
        --preview loft_office --res 540x960 --samples 64 --tag loft_office          (--pose 1: everything open)

The foundation built the shell, the door, the three eaves hatches (joinery._hatch), the skirting and the roof window
(its sash is tagged by lib/envelope). Here: built-in cabinet with four drawers, radiator, flags, desk and computers,
chairs, bookcase, tables, TV, air-con, pictures, sockets, the dimmer and its seven downlights, the roof-window blinds.
Detailed pieces (mesh chair, curved monitor, architect lamp, bookcase, piano stool, PC tower): loft_office_furn.py.
Textures: blender/rooms/loft_office_art.py -> blender/textures/art/loft_office_*.jpg.
Heights below are above the room floor (FZ); mb(...) puts geometry at world (x, y, FZ).

Round 3 ceiling (house.json): front knee wall 1.08 at y 2.54 with the stopgap front slope z = 6.30 + 0.50 y, flat
strip 2.12 for y 4.62..5.31 (east of x 1.25; to 5.38 west of it), rear slope 35 deg z = 12.33 - 0.70 y down to the
1.23 rear knee wall at y 6.59. Everything on the TV wall, the rear knee wall and the gable under the rear slope is kept
at least 3 cm under that plane (ceil_local below).
"""
import math
import os

import bpy
from mathutils import Matrix, Vector

from lib import interact as IX, lighting, materials as M, mouldings as mo, props as P, shell
from rooms import loft_office_furn as F

ROOM = 'loft_office'
FZ = 6.49
ART = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'textures', 'art', 'loft_office_')
W, E, S, N = (1, 0), (-1, 0), (0, 1), (0, -1)          # wall normals into the room: west, east, front, rear walls

CAMERAS = [
    dict(name='west', pos=(2.3, 4.5, FZ + 1.45), look=(-0.65, 4.0, FZ + 0.85), fov_deg=100, ref='v5:f_0346'),
    dict(name='east', pos=(1.5, 4.7, FZ + 1.45), look=(4.3, 4.7, FZ + 1.05), fov_deg=100, ref='v5:f_0183'),
    dict(name='rear', pos=(1.0, 4.2, FZ + 1.45), look=(2.6, 6.59, FZ + 0.9), fov_deg=100, ref='v5:f_0313'),
    dict(name='tv', pos=(3.2, 5.1, FZ + 1.45), look=(1.25, 5.9, FZ + 0.9), fov_deg=100, ref='v5:f_0344'),
    dict(name='cabinet', pos=(0.85, 3.6, FZ + 1.4), look=(0.78, 5.38, FZ + 1.0), fov_deg=100, ref='v5:f_0229'),
    dict(name='front', pos=(1.9, 5.0, FZ + 1.5), look=(1.7, 2.54, FZ + 0.4), fov_deg=100, ref='v5:f_0246'),
    dict(name='chairs', pos=(1.4, 4.7, FZ + 1.45), look=(0.5, 2.6, FZ + 0.5), fov_deg=100, ref='v5:f_0252'),
    dict(name='lobby', pos=(-0.25, 5.2, FZ + 1.45), look=(0.25, 6.13, FZ + 1.3), fov_deg=100, ref='v5:f_0212'),
    dict(name='dimmer', pos=(-0.45, 5.75, FZ + 1.35), look=(0.31, 5.72, FZ + 1.5), fov_deg=100, ref='v5:f_0172'),
    dict(name='desk', pos=(2.2, 4.3, FZ + 1.5), look=(4.3, 4.75, FZ + 0.85), fov_deg=100, ref='v5:f_0235'),
    dict(name='kit', pos=(3.2, 4.75, FZ + 1.25), look=(4.2, 4.7, FZ + 0.9), fov_deg=90, ref='v5:f_0237'),
    dict(name='velux', pos=(3.1, 4.8, FZ + 1.2), look=(3.15, 6.0, FZ + 1.9), fov_deg=100, ref='v5:f_0190'),
    dict(name='hatch', pos=(2.5, 4.3, FZ + 1.35), look=(2.48, 2.54, FZ + 0.45), fov_deg=100, ref='v12:f_0001'),
]

T = Matrix.Translation


def R(axis, deg):
    return Matrix.Rotation(math.radians(deg), 4, axis)


def mb(x=0.0, y=0.0, rot=0.0):
    return mo.MB().at(T((x, y, FZ)) @ R('Z', rot))


def col(name, hx, rough=0.6, metal=0):
    return M.solid('loft_' + name, hx, rough, metal)


def image(name, rough=0.85, size=None):
    return M.image_mat('loft_office_' + name, ART + name + '.jpg', size, roughness=rough)


def ceil_local(x, y):
    """Ceiling height above the room floor at (x, y) (the planes of house.json, round 3)."""
    if y <= 4.62:
        return 6.30 + 0.50 * y - FZ
    if x >= 1.25 and y >= 5.31:
        return 12.33 - 0.70 * y - FZ
    return (8.57 if y >= 5.38 else 8.61) - FZ


def quad(b, mat, x0, x1, z0, z1, y):
    """Picture quad facing -Y showing the whole image once."""
    b._f(b._vs([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)]), b.mi(mat), [(0, 0), (1, 0), (1, 1), (0, 1)])


# ------------------------------------------------------------------ built-in cabinet (spec 5.1)
def cabinet(ctx):
    """White joinery on the south face of the block: pilasters, frieze, cornice, open shelves over four deep
    drawers, 30 mm proud of the block, in front of its 0.70 deep hollow (house.json loft_cabinet_recess: x 0.44..1.12,
    y 5.38..6.08, h 0.09..1.89, the opening between the pilasters). The top fascia stops at the TV-wall line x 1.25:
    east of it the rear slope (round 3, 35 deg) comes down to 2.07 at y 5.38, and the cornice return dies under it."""
    proud, D = 0.03, .70                                 # D: clear depth behind the front
    yf, wh = 5.38 - proud, 'white_gloss'
    here = T((0.78, yf, FZ))                             # local: x across the front, +y into the cabinet
    b = mo.MB().at(here)
    for s in (-1, 1):
        b.box((s * .34, -.012, .15), (s * .45, proud, 1.89), wh)                    # pilaster shaft
        for k in range(4):                                                         # fillets between three flutes
            x0 = .352 + k * .0253
            b.box((s * x0, -.018, .19), (s * (x0 + .012), -.012, 1.85), wh, bev=.002)
        b.box((s * .335, -.022, 0), (s * .455, proud, .15), wh, bev=.003)           # plinth block
        b.box((s * .335, -.024, 1.865), (s * .457, proud, 1.89), wh, bev=.003)      # cap
        b.box((s * .332, -.027, 1.855), (s * .46, proud, 1.866), wh, bev=.002)      # cap astragal
    b.box((-.45, -.012, 1.89), (.45, proud, 2.06), wh)                              # frieze and the cornice core
    cyma = [(0, 0), (.02, 0), (.02, .03), (.035, .036), (.05, .06), (.07, .066), (.07, .10), (0, .10)]
    b.sweep(cyma, [(.45, proud, 1.96), (.45, -.012, 1.96), (-.45, -.012, 1.96), (-.45, proud, 1.96)], wh)
    b.box((-.52, -.082, 2.06), (.47, proud, 2.118), wh)                             # top fascia up to the flat ceiling
    b.box((-.34, .004, 0), (.34, proud, .09), wh)                                   # plinth under the drawers
    b.box((-.34, -.02, .856), (.34, D, .88), wh, bev=.002)                          # ledge
    for z in (1.24, 1.49):
        b.box((-.34, .01, z), (.34, D, z + .02), wh)                                # fixed shelves
    ctx.add(b.finish('loft_office.cabinet'), ROOM, 'fit', plan_sym='cabinet')

    for i, card in enumerate(('#A9C3DB', '#2F5A3C', '#C8A22C', '#7B2026')):         # bottom -> top
        z0 = .09 + i * .191
        b = mo.MB().at(here)
        b.box((-.34, -.02, z0), (.34, 0, z0 + .185), wh, bev=.002)                  # slab front
        zb = max(z0 + .02, .155)        # the bottom box rides over the room skirting that runs across the hollow
        for sx in (-1, 1):
            b.box((sx * .298, 0, zb), (sx * .31, .70, z0 + .165), wh)               # box sides, back, bottom
        b.box((-.298, .688, zb), (.298, .70, z0 + .165), wh)
        b.box((-.298, 0, zb), (.298, .688, zb + .012), wh)
        # brass card frame (four bars, a shaped top) round a plain coloured card, no writing
        for lo, hi in (((-.036, -.025, z0 + .115), (.036, -.02, z0 + .121)), ((-.036, -.025, z0 + .151), (.036, -.02, z0 + .158)),
                       ((-.036, -.025, z0 + .121), (-.03, -.02, z0 + .151)), ((.03, -.025, z0 + .121), (.036, -.02, z0 + .151))):
            b.box(lo, hi, 'brass', bev=.001)
        b.box((-.012, -.025, z0 + .158), (.012, -.02, z0 + .163), 'brass', bev=.001)
        b.box((-.03, -.0215, z0 + .121), (.03, -.02, z0 + .151), col('card%d' % i, card, .8))
        dr = b.finish(f'loft_office.cabinet.drawer.{i}')
        pull = P.place(P.handle_drop(.10, .03, 'brass', name=f'loft_office.cabinet.pull.{i}'),
                       (0.78, yf - .02, FZ + z0 + .085), facing=N)
        IX.tag_many([dr, pull], 'slide', g=f'loft_office.cabinet.drawer.{i}', label='Drawer', d=(0, -.55, 0))
        for o in (dr, pull):
            ctx.add(o, ROOM, 'fit', lm='dynamic')

    d = lambda want: min(want, D - .03)                  # contents never deeper than the compartment
    b = mo.MB().at(here)
    b.box((-.08, .02, .88), (.31, .02 + d(.36), 1.17), 'plastic_white', bev=.008)   # laser printer
    b.box((-.05, .015, .93), (.28, .02, .96), col('slot', '#3A3C40'))               # its paper slot
    b.box((.14, .012, 1.10), (.27, .02, 1.15), col('panel', '#2A2C30', .3))         # control panel (blank)
    b.box((-.31, .03, .88), (-.13, .03 + d(.22), 1.16), 'black_matt', bev=.004)     # black box
    b.box((-.14, .02, 1.26), (.30, .02 + d(.30), 1.41), 'black_matt', bev=.006)     # inkjet on the middle shelf
    b.box((-.30, .03, 1.26), (-.17, .03 + d(.25), 1.36), 'plastic_white', bev=.004)  # white carton beside it
    x = -.325
    lever = col('lever_label', '#ECEAE4', .8)
    for wd, h, c in ((.075, .32, '#1C1C1E'), (.075, .32, '#1C1C1E'), (.075, .32, '#1C1C1E'), (.05, .31, '#6A2A22'),
                     (.03, .30, '#2C4A8C'), (.03, .31, '#2C4A8C'), (.04, .31, '#D9B62B'), (.09, .26, '#E6E0CC'),
                     (.09, .26, '#E6E0CC')):                                        # files and folders, blank spines
        b.box((x, .02, 1.51), (x + wd - .004, .02 + d(.28), 1.51 + h), col('file' + c[1:], c, .7), bev=.002)
        if wd == .075:                                                              # lever-arch: blank label, ring pull
            b.box((x + .014, .0185, 1.66), (x + .057, .02, 1.79), lever)
            b.box((x + .022, .0185, 1.565), (x + .049, .02, 1.595), 'black_gloss')
        x += wd
    ctx.add(b.finish('loft_office.cabinet.contents'), ROOM, 'decor')


# ------------------------------------------------------------------ west wall: radiator and flags
def radiator(ctx):
    """White column radiator, 20 round-topped sections at 63.5 mm, 1.27 x 0.57 (eaves_loft 5: 1.27 x 0.57 against the
    spec's 1.25 x 0.52), 40 mm off the wall on two brackets, valves at both ends."""
    b, pitch = mb(-0.65, 0), .0635
    y0 = 3.25
    for i in range(20):
        y = y0 + pitch * (i + .5)
        b.tube([(.059, y, .17), (.059, y, .65), (.072, y, .68), (.108, y, .68), (.121, y, .65), (.121, y, .17),
                (.108, y, .148), (.072, y, .148)], .019, 'white_gloss', n=8, closed=True, up=(0, 1, 0))
    y1 = y0 + 20 * pitch
    for y in (y0 + .30, y1 - .30):                                                  # wall brackets
        b.box((0, y - .015, .55), (.045, y + .015, .58), 'white_gloss', bev=.003)
    for y in (y0 - .035, y1 + .035):                                                # valves and tails into the floor
        b.tube([(.09, y, 0), (.09, y, .16)], .008, 'chrome', n=6)
        b.box((.075, y - .02, .14), (.105, y + .02, .185), 'chrome', bev=.004)
        b.tube([(.09, y, .185), (.09, y, .20)], .012, 'chrome', n=8)
    ctx.add(b.finish('loft_office.radiator'), ROOM, 'fit', plan_sym='radiator')


def flag(ctx, name, img, w, h, y, z0, turn):
    """Cloth pinned flat to the west wall by its top corners, slightly rippled."""
    b, nx, nz, m = mo.MB(), 10, 12, P.two_sided(image(img, .95))
    pt = lambda i, j: (-w / 2 + w * i / nx, -.004 - .004 * (1 + math.sin(7.0 * i / nx * 3 + j * .9)) * j / nz, h - h * j / nz)
    for i in range(nx):
        for j in range(nz):
            u0, u1, v0, v1 = i / nx, (i + 1) / nx, 1 - j / nz, 1 - (j + 1) / nz
            uv = [(1 - v, u) for u, v in ((u0, v1), (u1, v1), (u1, v0), (u0, v0))] if turn else \
                [(u0, v1), (u1, v1), (u1, v0), (u0, v0)]
            b._f(b._vs([pt(i, j + 1), pt(i + 1, j + 1), pt(i + 1, j), pt(i, j)]), b.mi(m), uv)
    for sx in (-1, 1):
        b.box((sx * (w / 2 - .012) - .005, -.009, h - .017), (sx * (w / 2 - .012) + .005, -.003, h - .007), 'brass')
    ctx.add(P.place(b.finish('loft_office.' + name), (-0.65, y, FZ + z0), facing=W), ROOM, 'decor')


# ------------------------------------------------------------------ pictures
def framed(ctx, name, loc, facing, *a, **kw):
    return ctx.add(P.place(P.framed_picture(*a, name='loft_office.' + name, **kw), loc, facing=facing), ROOM, 'decor')


_SEAL = {}


def cert(ctx, name, loc, facing, w, h, style, mount, seal=False):
    """Certificate: frame, dark mount, blank cream sheet (no writing); optional plain red wafer seal."""
    ob = framed(ctx, name, loc, facing, None, w, h, style, mount=.04, mount_mat=mount, fill=('#EEE9DA',) * 3)
    if seal:
        if 'me' not in _SEAL:
            b = mo.MB()
            b.lathe([(0, 0), (.016, 0), (.016, .0015), (0, .0015)], col('seal', '#A3231F', .5), 12)
            _SEAL['me'] = b.finish('loft_office.seal').data
        s = bpy.data.objects.new('loft_office.' + name + '.seal', _SEAL['me'])
        s.matrix_basis = ob.matrix_basis @ T((-.05, -.012, -h * .22)) @ R('X', 90)
        ctx.add(s, ROOM, 'decor')


def leaning(ctx, name, img, w, h, y):
    """Oak-framed picture standing on the floor, leaning back against the TV wall (x = 1.25)."""
    b, fw, lean = mo.MB(), .045, 10.0
    for lo, hi in (((-w / 2, -.02, 0), (w / 2, 0, fw)), ((-w / 2, -.02, h - fw), (w / 2, 0, h)),
                   ((-w / 2, -.02, fw), (-w / 2 + fw, 0, h - fw)), ((w / 2 - fw, -.02, fw), (w / 2, 0, h - fw))):
        b.box(lo, hi, 'oak_rustic', bev=.003)
    b.box((-w / 2 + fw, -.011, fw), (w / 2 - fw, -.002, h - fw), col('mount', '#EDE8DA', .9))
    k = fw + .02
    if img:
        quad(b, image(img), -w / 2 + k, w / 2 - k, k, h - k, -.0115)
    else:                                                # the small photograph: neutral bands
        for z0, z1, c in ((k, h * .45, '#7C8466'), (h * .45, h - k, '#B9C3C8')):
            b.box((-w / 2 + k, -.0115, z0), (w / 2 - k, -.011, z1), col('band' + c[1:], c, .9))
    ob = b.finish('loft_office.' + name)
    ob.matrix_basis = T((1.25 + .003 + h * math.sin(math.radians(lean)), y, FZ)) @ R('Z', 90) @ R('X', -lean)
    ctx.add(ob, ROOM, 'decor')


# ------------------------------------------------------------------ furniture
def desk(ctx):
    """Sit-stand desk x 3.50..4.30, y 3.60..5.40, top 0.74: oak-effect top on black two-stage T-legs, felt mat,
    49-inch curved ultrawide and 27-inch monitor on an arm (both blank), laptop on a low stand under the ultrawide,
    keyboard, mouse; architect lamp clamped to the north-west corner (hr_235).
    Screens stand 8 cm clear of the desk with their tops at 1.19, 9 cm over the poster's bottom edge (1.10): in hr_183
    the 27-inch's top is 15-20 px above the poster's bottom (poster 165-170 px = 0.62 m) from about 3.6 m, which puts
    it at 1.17 once the 0.13 m stand-off is allowed for; in hr_235 and hr_183 the laptop's lid ends at the ultrawide's
    bottom edge."""
    b, blk = mb(), 'black_matt'
    b.box((3.50, 3.60, .70), (4.30, 5.40, .74), 'oak_light', bev=.003)
    for y in (3.90, 5.10):
        b.box((3.855, y - .04, .03), (3.945, y + .04, .40), blk, bev=.004)          # lower column
        b.box((3.862, y - .033, .40), (3.938, y + .033, .67), blk, bev=.004)        # upper stage
        b.box((3.55, y - .035, 0), (4.25, y + .035, .03), blk, bev=.004)            # foot
        for x in (3.57, 4.23):
            b.box((x - .015, y - .015, -.0), (x + .015, y + .015, .004), 'black_gloss')
        b.box((3.56, y - .03, .67), (4.24, y + .03, .70), blk, bev=.003)            # top bracket
    b.box((3.88, 3.90, .63), (3.92, 5.10, .69), blk)                                # crossbar
    b.box((3.505, 5.12, .672), (3.545, 5.27, .698), blk, bev=.004)                  # height control panel
    b.box((3.503, 5.15, .678), (3.505, 5.24, .692), col('keys', '#2D2F33', .4))
    b.box((3.56, 3.98, .74), (3.96, 4.88, .743), col('felt', '#1D1D20', 1.0))
    # [round 4] baked (furniture is probe-lit by default): the desk lamp's pool falls on this top, and a probe-lit top
    # showed nothing when the lamp was switched (IX-07)
    ctx.add(b.finish('loft_office.desk'), ROOM, 'furn', plan_sym='desk', lm='static')

    b, grey = mb(), col('alu', '#8D9096', .45, 1)
    F.curved_monitor(b, 4.15, 4.17, .82, .743)                                      # apex 0.15 off the wall
    arm = T((4.235, 5.10, FZ + 1.005)) @ R('Z', -14)                                # 27-inch, turned to the chair
    F.flat_monitor(b, arm @ T((-.065, 0, 0)))
    b.at(T((0, 0, FZ)))
    b.box((4.21, 5.08, .74), (4.27, 5.14, .752), blk, bev=.004)                     # arm clamp and pole
    b.tube([(4.24, 5.11, .752), (4.24, 5.11, 1.005)], .014, blk, n=10)
    b.tube([(4.24, 5.11, 1.005), (4.20, 5.105, 1.005)], .012, blk, n=8)
    lap = T((3.92, 4.47, FZ + .768)) @ R('Y', -8)                                   # laptop on a low stand, lid open
    b.at(lap)                                                                       # 112 degrees (leaning back)
    b.box((-.11, -.16, 0), (.11, .16, .015), grey, bev=.002)
    b.at(lap @ T((.11, 0, .015)) @ R('Y', 112))
    b.box((-.205, -.16, 0), (0, .16, .008), grey, bev=.002)
    b.box((-.195, -.15, -.0006), (-.01, .15, 0), 'screen_black')
    b.at(T((0, 0, FZ)))
    for y in (4.36, 4.58):                                                          # stand: two wedge rails
        b.prism([(3.82, y - .01, .740), (4.03, y - .01, .740), (4.03, y - .01, .785), (3.82, y - .01, .755)],
                (0, .02, 0), blk)
    b.box((3.62, 4.28, .743), (3.75, 4.66, .753), grey, bev=.002)                   # keyboard
    b.box((3.635, 4.29, .753), (3.735, 4.65, .755), col('keycaps', '#3A3C40', .5))
    b.box((3.65, 4.72, .743), (3.75, 4.78, .765), blk, bev=.008)                    # mouse
    ctx.add(b.finish('loft_office.desk.computers'), ROOM, 'furn')

    tower = F.pc_tower('loft_office.pc_tower')                                      # on the floor north of the desk
    tower.location = (4.05, 5.67, FZ)
    ctx.add(tower, ROOM, 'furn', plan_sym='cabinet')

    # architect lamp: clamp on the front edge at the north end, elbow up, domed shade over the 27-inch's left half
    b = mb()
    disc, ax = F.desk_lamp(b, (3.50, 5.355, .74), (3.585, 5.31, 1.20), (3.80, 5.16, 1.13), M0=T((0, 0, FZ)))
    b.at(T(disc + Vector((0, 0, FZ))) @ Vector((0, 0, 1)).rotation_difference(ax).to_matrix().to_4x4())
    b.lathe([(0, -.002), (.026, -.002), (.026, .0), (0, .0)], P.emissive('#F4CB94', 6.0), 12)   # lit lamp face
    lamp = b.finish('loft_office.desk_lamp')
    IX.tag(lamp, 'lamp', label='Desk lamp')
    ctx.add(lamp, ROOM, 'light')
    # [round 4] its Cycles lamp, inside the shade under the lamp face (IX-07: without one the export made no circuit
    # and the switch changed nothing); the name extends the fitting's, so it bakes as circuit 'desk_lamp' (INTERACT.md)
    bulb = disc - ax * .04
    lighting.bulb(ctx, ROOM, (bulb.x, bulb.y, FZ + bulb.z), watts=5, kelvin=3000, radius=.02,
                  name='loft_office.desk_lamp.bulb')


def office_chair(ctx):
    """Ergonomic mesh chair (loft_office_furn.office_chair), facing the desk (+X)."""
    ob = F.office_chair('loft_office.office_chair')
    ob.matrix_basis = T((3.05, 4.35, FZ)) @ R('Z', 90)
    IX.tag(ob, 'hinge', p=(3.05, 4.35, FZ), deg=-70, label='Chair', dur=1.0)
    ctx.add(ob, ROOM, 'furn', plan_sym='office_chair')


def stool(ctx):
    """Piano stool in its cream / mauve striped cover between the desk and the TV wall (hr_183, hr_235)."""
    root = F.stool('loft_office.stool', image('stripe', .9, (.12, .12)))
    root.location = (3.15, 5.35, FZ)
    ctx.add(root, ROOM, 'furn', plan_sym='stool')


def bookcase(ctx):
    """Rustic oak open bookcase 0.90 x 0.30 x 1.06 against the front knee wall, x 0.82..1.72, its top at the arris
    where the slope starts (eaves_loft 2.3, v12 f4-6, f64); 0.07 east of the round-2 spot so the west hatch's east leaf
    (x <= 0.77 over the bookcase depth at 100 degrees) swings past it."""
    x, y = 1.27, 2.565
    bc = F.bookcase('loft_office.bookcase')
    bc.location = (x, y, FZ)
    ctx.add(bc, ROOM, 'furn', plan_sym='bookcase')
    b = mb(x, y)
    for x0, x1, c2 in ((-.40, -.24, '#7FA6A8'), (-.22, -.06, '#6B2A35'), (.10, .34, '#E9E6DC')):   # plain boxes
        b.box((x0, .05, .742), (x1, .25, .872), col('box' + c2[1:], c2, .8), bev=.003)
    b.at(T((x - .30, y + .23, FZ + 1.06)))                                          # incense burner, front of the top
    b.lathe([(0, 0), (.03, 0), (.045, .02), (.04, .045), (.015, .055), (.012, .07), (0, .075)], 'brass_antique', 12)
    ctx.add(b.finish('loft_office.bookcase.top'), ROOM, 'decor')
    for i, (z, ln, seed) in enumerate(((.095, .62, 3), (.427, .52, 8))):
        bk = P.book_row(ln, .21, .16, seed=seed, name=f'loft_office.books.{i}')
        ctx.add(P.place(bk, (x + (.08 if i else -.08), y + .02, FZ + z), facing=S), ROOM, 'decor')


def tables(ctx):
    b, oak = mb(), 'oak_rustic'                            # coffee table 1.00 x 0.50 x 0.45, low shelf
    x0, x1, y0, y1 = .92, 1.92, 3.15, 3.65                 # 35 mm west of the east hatch's floor strip (x >= 1.955)
    b.box((x0, y0, .415), (x1, y1, .45), oak, bev=.004)
    for xa, xb, ya, yb in ((x0 + .06, x1 - .06, y0 + .036, y0 + .056), (x0 + .06, x1 - .06, y1 - .056, y1 - .036),
                           (x0 + .036, x0 + .056, y0 + .06, y1 - .06), (x1 - .056, x1 - .036, y0 + .06, y1 - .06)):
        b.box((xa, ya, .345), (xb, yb, .413), oak, bev=.002)                        # apron rails, set in 6 mm
    b.box((x0 + .05, y0 + .05, .10), (x1 - .05, y1 - .05, .12), oak)
    for x in (x0 + .03, x1 - .09):
        for y in (y0 + .03, y1 - .09):
            b.box((x, y, 0), (x + .06, y + .06, .415), oak, bev=.003)
    ctx.add(b.finish('loft_office.coffee_table'), ROOM, 'furn', plan_sym='coffee_table')

    b, wire = mb(), 'plastic_white'                        # drawer trolley 0.55 x 0.45 x 0.85, four mesh baskets
    x0, x1, y0, y1 = 3.72, 4.26, 2.75, 3.20                # clear of the east wall's skirting
    for x in (x0, x1 - .03):
        for y in (y0, y1 - .03):
            b.box((x, y, 0), (x + .03, y + .03, .83), 'oak_light', bev=.002)
    b.box((x0, y0, .83), (x1, y1, .85), 'oak_light', bev=.003)
    for k in range(4):
        z = .06 + k * .19
        b.box((x0 + .035, y0 + .01, z), (x1 - .035, y1 - .01, z + .012), wire)
        for lo, hi in (((x0 + .035, y0 + .01), (x1 - .035, y0 + .018)), ((x0 + .035, y1 - .018), (x1 - .035, y1 - .01)),
                       ((x0 + .035, y0 + .018), (x0 + .043, y1 - .018)), ((x1 - .043, y0 + .018), (x1 - .035, y1 - .018))):
            b.box((*lo, z + .012), (*hi, z + .15), wire)
        for j in range(1, 6):                                                       # wire mesh lines on the front
            yy = y0 + .018 + (y1 - y0 - .036) * j / 6
            b.box((x0 + .031, yy - .002, z + .012), (x0 + .035, yy + .002, z + .15), wire)
        b.box((x0 + .02, y0 + .15, z + .12), (x0 + .035, y1 - .15, z + .135), wire)  # basket grip rim
    for x in (x0, x1 - .03):                                                        # runners
        b.box((x + .005, y0 + .03, .05), (x + .025, y1 - .03, .062), 'oak_light')
    ctx.add(b.finish('loft_office.trolley'), ROOM, 'furn', plan_sym='chest')


# ------------------------------------------------------------------ fixed fittings
def aircon(ctx):
    """Split-system indoor unit on the east wall, centred under the flat strip (y 4.62..5.31, centre 4.965), its top
    8 mm under the flat ceiling and clear of both slopes (hr_183, hr_235); the louvre opens from the remote."""
    b, g = mb(), 'loft_office.aircon'
    y0, y1, z0, z1 = 4.565, 5.365, 1.77, 2.06
    b.box((4.09, y0, z0), (4.298, y1, z1), 'plastic_white', bev=.025)
    b.box((4.088, y0 + .03, z0 + .08), (4.091, y1 - .03, z0 + .083), col('slot', '#3A3C40'))
    b.box((4.0875, y1 - .09, z0 + .02), (4.09, y1 - .06, z0 + .05), col('display', '#C9CCD0', .3))   # sensor window
    ctx.add(b.finish(g), ROOM, 'fit')
    b = mb()
    b.box((4.105, y0 + .03, z0 - .008), (4.205, y1 - .03, z0 - .001), 'plastic_white')
    flap = b.finish(g + '.louvre')
    IX.tag(flap, 'hinge', g=g, label='Air conditioning', p=(4.205, (y0 + y1) / 2, FZ + z0 - .001), a=(0, 1, 0),
           deg=-55, reach=3.0)
    ctx.add(flap, ROOM, 'fit', lm='dynamic')
    b = mb(0.31, 5.70)                                    # remote in its wall cradle beside the dimmer: back plate,
    b.box((-.004, -.03, 1.14), (0, .03, 1.24), 'plastic_white', bev=.0015)          # cheeks, bottom and front lip
    for sy in (-1, 1):
        b.box((-.022, sy * .0245, 1.14), (-.0042, sy * .03, 1.215), 'plastic_white', bev=.0015)
    b.box((-.0215, -.024, 1.14), (-.0042, .024, 1.1485), 'plastic_white')
    b.box((-.022, -.024, 1.1405), (-.018, .024, 1.19), 'plastic_white', bev=.0012)
    ctx.add(b.finish(g + '.cradle'), ROOM, 'fit')
    b = mb(0.31, 5.70)
    b.box((-.0168, -.022, 1.149), (-.0052, .022, 1.29), col('remote', '#E9E9E6', .5), bev=.003)
    remote = b.finish(g + '.remote')
    IX.tag(remote, 'trigger', g=g, label='Air conditioning')
    ctx.add(remote, ROOM, 'fit', lm='dynamic')


def tv(ctx):
    """43-inch TV (0.97 x 0.56; eaves_loft V1.4: with the 1.23 rear knee the TV wall reads 2.23 TV heights) on the
    block's east face, y 5.58..6.55, z 0.62..1.18: its north top corner 7.5 cm under the 35-deg rear slope, as filmed
    (hr_344). Medal rail under it, two small frames over its south half, cat pictures leaning on the floor.
    Everything here stays within 42 mm of the wall (the rear hatch's west leaf swings to x 1.43, 95 degrees)."""
    set_ = P.place(P.tv_panel(.97, .56, standoff=.012, name='loft_office.tv'), (1.25, 6.065, FZ + .90), facing=W)
    pic = P.tv_screen(.96, .55, name='loft_office.tv.picture')
    pic.location, pic.rotation_euler = set_.matrix_basis @ Vector((0, -.0436, 0)), set_.rotation_euler
    IX.tag(set_, 'trigger', g='loft_office.tv', label='TV')
    IX.tag(pic, 'show', g='loft_office.tv', when=1, fx='tv')
    ctx.add(set_, ROOM, 'fit', plan_sym='tv')
    ctx.add(pic, ROOM, 'fit', lm='dynamic')
    # limed-oak frame with a cream mount (hr_344, spec 7): the flat 'dark_wood' moulding re-coloured pale limed oak
    # (sampled #9D8C73 / #C2BDAC in hr_344 against the wall's #B9B6AE = #F2F2EF)
    ob = framed(ctx, 'tv_frame.0', (1.25, 5.66, FZ + 1.385), W, None, .32, .27, 'dark_wood', frame_w=.04, mount=.04)
    ob.data = ob.data.copy()
    for i, m in enumerate(ob.data.materials):
        if m and m.name.startswith('frame_dark'):
            ob.data.materials[i] = col('limed_oak', '#D2C3A6', .65)
    framed(ctx, 'tv_frame.1', (1.25, 6.02, FZ + 1.385), W, None, .24, .23, 'dark_wood')

    rail = mo.brass_rail([(1.28, 5.62, FZ + .57), (1.28, 6.48, FZ + .57)], 'loft_office.medal_rail', r=.008, off=.03)
    ctx.add(rail, ROOM, 'decor')
    b = mb()                                              # eight plain ribbons with plain discs, no lettering
    for k, c in enumerate(('#6E9A3A', '#D0872B', '#1F1F22', '#3D7FB5', '#69A7C9', '#2B56A0', '#8BB7D6', '#A32A2A')):
        y, zd = 6.07 + k * .05, .27 + .012 * (k % 3)
        b.box((1.289, y - .015, zd + .025), (1.291, y + .015, .575), col('ribbon' + c[1:], c, .9))
        b.at(T((1.287, y, FZ + zd)) @ R('Y', 90))
        b.lathe([(0, 0), (.03, 0), (.03, .004), (0, .004)], 'silver_satin' if k % 2 else 'gilt_bright', 12)
        b.at(T((0, 0, FZ)))
    ctx.add(b.finish('loft_office.medals'), ROOM, 'decor')
    leaning(ctx, 'cat.0', 'cat1', .30, .38, 5.57)
    leaning(ctx, 'cat.1', 'cat2', .28, .36, 5.89)
    leaning(ctx, 'cat.2', None, .17, .22, 6.15)


def velux_blind(ctx):
    """Dark grey blackout roller in the roof window, parked across the top as filmed; state 1 draws it down. Below it
    the white pleated blind. ponytail: both are carried by the fixed frame, not by the sash."""
    f = next(q for q in ctx.features if q['id'] == 'velux')
    p = next(q for q in ctx.spec['roof']['planes'] if q['id'] == f['roofPlane'])['z']
    xs, ys = [q[0] for q in f['polygon']], [q[1] for q in f['polygon']]
    x0, y0, cy = min(xs), min(ys), p['cy']                 # y0 = the high (hinge) edge of the rear slope
    ey = Vector((0, 1, cy)).normalized()
    ex, en = Vector((1, 0, 0)), Vector((1, 0, 0)).cross(ey)
    o = Vector((x0, y0, p['c0'] + p['cx'] * x0 + cy * y0))
    frame = Matrix((ex, ey, en)).transposed().to_4x4()
    frame.translation = o                                  # local: x across, y down the slope, z out of the roof
    Wd, H = max(xs) - x0, (max(ys) - y0) * math.hypot(1, cy)
    cloth, g = P.two_sided(col('blind', '#565A60', .9)), 'loft_office.velux_blind'

    def part(name, y1, bar):
        b = mo.MB().at(frame)
        if y1:
            b.box((.092, .10, -.016), (Wd - .092, y1, -.014), cloth)
        if bar:
            b.box((.092, y1, -.026), (Wd - .092, y1 + .03, -.012), col('blind_bar', '#C9CBCD', .4, 1), bev=.003)
        else:
            b.box((.092, .092, -.045), (Wd - .092, .135, -.008), col('blind_bar', '#C9CBCD', .4, 1), bev=.004)
        return b.finish(name)

    cas = part(g + '.cassette', 0, False)
    IX.tag(cas, 'trigger', g=g, label='Blind', reach=2.4, excl=['roof.velux.sash'])
    ctx.add(cas, ROOM, 'decor', lm='dynamic')
    # parked bar 0.50 down the sash: the head reveal hides about 0.35 from eye height, and hr_313 / hr_183 show the
    # grey band as the top quarter of what is visible
    for name, y1, when in (('.parked', .50, 0), ('.drawn', H - .125, 1)):
        ob = part(g + name, y1, True)
        IX.tag(ob, 'show', g=g, when=when, fx='none', label='Blind', reach=2.4, excl=['roof.velux.sash'])
        ctx.add(ob, ROOM, 'decor', lm='dynamic')

    # White pleated blind between the blackout and the glass, drawn below the parked blackout in every still (hr_183,
    # hr_313). Its bottom bar slides up the slope (a 'slide' item, so the viewer offers "Open"); the cloth fades to a
    # stack under the blackout bar. The drawn blackout covers it in either state. No excl: parking it frees the sash,
    # and the viewer only shuts excl groups that are open (parked), which never conflicts.
    gp, top, bot = 'loft_office.velux_pleat', .53, H - .125
    pleat, kw = col('pleat', '#EEEDE8', .95), dict(g=gp, label='Pleated blind', reach=2.4)
    b = mo.MB().at(frame)
    b.box((.092, top, -.009), (Wd - .092, bot, -.008), pleat)
    for k in range(int((bot - top) / .025)):                                        # pleat ridges
        b.box((.092, top + .012 + .025 * k, -.011), (Wd - .092, top + .016 + .025 * k, -.009), pleat)
    cloth_p = b.finish(gp + '.drawn')
    IX.tag(cloth_p, 'show', when=0, fx='none', **kw)
    b = mo.MB().at(frame)
    b.box((.092, top, -.011), (Wd - .092, top + .03, -.006), pleat)
    stack = b.finish(gp + '.stack')
    IX.tag(stack, 'show', when=1, fx='none', **kw)
    b = mo.MB().at(frame)
    b.box((.092, bot, -.011), (Wd - .092, bot + .02, -.004), col('blind_bar', '#C9CBCD', .4, 1), bev=.003)
    bar = b.finish(gp + '.bar')
    IX.tag(bar, 'slide', d=tuple(-ey * (bot - top - .03)), **kw)
    for ob in (cloth_p, stack, bar):
        ctx.add(ob, ROOM, 'decor', lm='dynamic')


def lights(ctx):
    """Six downlights along the flat ceiling strip and one in the lobby, all on the lobby's rotary dimmer."""
    spots = [(x, y) for x in (0.1, 2.3, 3.7) for y in (4.75, 5.22)] + [(-0.17, 5.75)]
    for i, (x, y) in enumerate(spots):
        lighting.downlight(ctx, ROOM, x, y, watts=110, name=f'loft_office.downlight.{i}')
        trim = P.place(P.downlight(name=f'loft_office.downlight_trim.{i}'), (x, y, ctx.ceil_z(ROOM, x, y)))
        ctx.add(trim, ROOM, 'light')
    sw = P.place(P.switch_plate(1, 'dimmer', name='loft_office.dimmer'), (0.31, 5.83, FZ + 1.22), facing=E)
    IX.tag(sw, 'light', rooms=[ROOM], label='Lights')
    ctx.add(sw, ROOM, 'fit', lm='dynamic')
    for i, (loc, facing) in enumerate((((4.30, 4.2, FZ + .30), E), ((4.30, 5.2, FZ + .30), E), ((3.95, 6.59, FZ + .30), N))):
        ctx.add(P.place(P.socket(2, name=f'loft_office.socket.{i}'), loc, facing=facing), ROOM, 'fit')


def finishes(ctx):
    """Colours of the 21 Nov daylight survey (eaves_loft 2.7, brief b): the carpet is a neutral silver grey (#B6B3AC,
    the library's carpet_grey_twist #B9B4AB; house.json still names the creamier carpet_grey) and the white walls are
    neutral (#F2F2EF), not warm. The slopes (#EDEDEA) already read a shade greyer; the east gable stays #3B4046."""
    shell.repaint(ROOM, 'carpet_grey', 'carpet_grey_twist', part='floor')
    shell.repaint(ROOM, '#EFEDE7', '#F2F2EF')
    # Cover the shell's two gable holes (reported): in the grid cell y 3.90..4.33 both gable faces (x -0.65, x 4.30)
    # stop at Z 8.25 instead of following the front slope up to 8.465 at y 4.33, leaving a triangle open onto the roof
    # slab. Added only while the shell still has that corner, 1 mm proud of the wall, its sloped edge on the ceiling.
    walls = shell.surface(ROOM, 'walls')
    mw = walls.matrix_world if walls else None
    if walls and any(abs(q.y - 4.33) < .003 and abs(q.z - 8.25) < .003 for q in (mw @ v.co for v in walls.data.vertices)):
        tri = lambda x: [(x, 3.89, 8.245), (x, 4.335, 8.245), (x, 4.335, 8.4675)]
        patch = shell.faces_object('loft_office.gable_patch', [(tri(-0.649), (0.0, 4.2, 8.3), '#F2F2EF'),
                                                               (tri(4.299), (3.0, 4.2, 8.3), '#3B4046')])
        ctx.add(patch, ROOM, 'fit')
    # The envelope's main_rear slab underside dips to Z 8.58 at y 5.371..5.38 (the dormer edge), in front of the 4 cm
    # step between the flat (8.61) and the lobby ceiling (8.57), and shows there as a strip of black felt and rafters
    # (reported). A ceiling-white strip 12 mm deep covers it west of the cabinet's top fascia (x 0.26).
    strip = shell.box('loft_office.step_cover', -0.65, 0.26, 5.368, 5.38, 8.570, 8.6098, '#EDEDEA')
    ctx.add(strip, ROOM, 'fit')


def build(ctx):
    finishes(ctx)
    cabinet(ctx)
    radiator(ctx)
    flag(ctx, 'flag.union', 'union', .98, 1.49, 5.09, .16, True)           # hoist up, as it hangs
    # 3 x 2 ft ensign pinned at the SW corner (eaves_loft 2.3: 0.61 x 0.91, y 2.60..3.21, z 0.10..1.02); bottom on the
    # skirting top (0.15: at 0.12 its foot ran 3 cm behind the skirting face), top 4.5 cm under the stopgap slope (1.11)
    flag(ctx, 'flag.ensign', 'ensign', .61, .91, 2.905, .155, False)
    desk(ctx)
    office_chair(ctx)
    stool(ctx)
    bookcase(ctx)
    tables(ctx)
    aircon(ctx)
    tv(ctx)
    velux_blind(ctx)
    lights(ctx)

    # Chippendale chair (same set as the dining room), facing into the room with its back to the west hatch as filmed
    # (hr_252, v12 f44), but pulled 0.78 north so the floor in front of the hatch stays clear for 0.9 m (owner, round 3:
    # visitors open the hatch and duck into the eaves); a 0.54 m lane stays between it and the radiator.
    # cabriole front legs on ball-and-claw feet as filmed (hr_252), no stretchers (loft_office_furn.chippendale)
    ch = P.place(F.chippendale('loft_office.chair'), (0.33, 3.78, FZ), rot_z=180)
    ctx.add(ch, ROOM, 'furn', plan_sym='chair')
    # artificial pothos-like plant in a woven seagrass basket in the NE corner (hr_183)
    plant = P.plant_potted('monstera', height=.62, spread=.42, pot_dia=.30, pot_h=.22,
                           pot_mat=image('weave', .9, (.06, .06)), name='loft_office.plant')
    ctx.add(P.place(plant, (4.03, 6.30, FZ)), ROOM, 'decor', plan_sym='plant')

    # lobby: carved hardwood panel in a deep gilt frame (rectified crop of the carving)
    framed(ctx, 'carving', (0.31, 5.72, FZ + 1.72), E, ART + 'carving.jpg', .40, .60, 'gilt_plain', frame_w=.09, depth=.07)
    # east wall (hr_183, hr_235): periodic table centred under the a/c with its top just under it; two small frames
    # north of it, the gilt one level with the poster top and 4 cm under the rear slope at its north edge. The dark
    # wall below them is bare (the spec's "W-east certificate with a red seal" is the rear knee wall's cert.3).
    framed(ctx, 'periodic', (4.30, 4.965, FZ + 1.41), E, ART + 'periodic.jpg', .90, .62, 'black')
    framed(ctx, 'east_frame.0', (4.30, 5.64, FZ + 1.585), E, None, .37, .27, 'gilt_plain', frame_w=.035,
           mount=.03, fill=('#C2493D', '#E3C45A', '#3F6FA8'))
    framed(ctx, 'east_frame.1', (4.30, 5.64, FZ + 1.265), E, None, .37, .27, 'black', mount=.045, mount_mat='#6B2A35',
           fill=('#4E8A6A', '#E3C45A', '#C2493D'))
    # rear knee wall (1.23 high): seven certificates, blank sheets; the upper row's tops 5 cm under the arris (hr_313)
    styles = (('gilt_plain', '#1E2A44'), ('dark_wood', '#1E2A44'), ('walnut_gold', '#5C2630'), ('black', '#22242A'))
    for i, x in enumerate((2.79, 3.197, 3.603, 4.01)):
        cert(ctx, f'cert.{i}', (x, 6.59, FZ + .94), N, .34, .48, *styles[i], seal=i in (2, 3))
    for i, x in enumerate((2.79, 3.21, 3.63)):
        cert(ctx, f'cert.{i + 4}', (x, 6.59, FZ + .425), N, .34, .45, *styles[(i + 2) % 4])

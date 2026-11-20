"""Second-floor front office in the converted loft (spec/rooms/loft_office.md, footage v5 f_0170-f_0260).

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --levels 2,X --only shell,envelope,loft_office \
        --preview loft_office --res 540x960 --samples 64 --tag loft_office          (--pose 1: everything open)

The foundation built the shell, the door, the three eaves hatches, the skirting and the roof window (its sash is
tagged by lib/envelope). Here: built-in cabinet with four drawers, radiator, flags, desk and computers, chairs,
bookcase, tables, TV, air-con, pictures, sockets, the dimmer and its seven downlights, the roof-window blinds.
Textures: blender/rooms/loft_office_art.py -> blender/textures/art/loft_office_*.jpg.
Heights below are above the room floor (FZ); mb(...) puts geometry at world (x, y, FZ).
"""
import math
import os

import bpy
from mathutils import Matrix, Vector

from lib import interact as IX, lighting, materials as M, mouldings as mo, props as P
from rooms.dining_chairs import chair as chippendale_chair

ROOM = 'loft_office'
FZ = 6.49
ART = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'textures', 'art', 'loft_office_')
W, E, S, N = (1, 0), (-1, 0), (0, 1), (0, -1)          # wall normals into the room: west, east, front, rear walls

CAMERAS = [
    dict(name='west', pos=(2.3, 4.5, FZ + 1.45), look=(-0.65, 4.0, FZ + 0.85), fov_deg=100, ref='v5:f_0346'),
    dict(name='east', pos=(1.5, 4.7, FZ + 1.45), look=(4.3, 4.7, FZ + 1.05), fov_deg=100, ref='v5:f_0183'),
    dict(name='rear', pos=(1.9, 4.1, FZ + 1.45), look=(2.9, 6.59, FZ + 1.0), fov_deg=100, ref='v5:f_0313'),
    dict(name='tv', pos=(3.2, 5.1, FZ + 1.45), look=(1.25, 5.9, FZ + 0.9), fov_deg=100, ref='v5:f_0344'),
    dict(name='cabinet', pos=(0.85, 3.6, FZ + 1.4), look=(0.78, 5.38, FZ + 1.0), fov_deg=100, ref='v5:f_0229'),
    dict(name='front', pos=(1.9, 5.0, FZ + 1.5), look=(1.7, 2.54, FZ + 0.4), fov_deg=100, ref='v5:f_0246'),
    dict(name='chairs', pos=(1.4, 4.7, FZ + 1.45), look=(0.5, 2.6, FZ + 0.5), fov_deg=100, ref='v5:f_0252'),
    dict(name='lobby', pos=(-0.25, 5.2, FZ + 1.45), look=(0.25, 6.13, FZ + 1.3), fov_deg=100, ref='v5:f_0212'),
    dict(name='dimmer', pos=(-0.45, 5.75, FZ + 1.35), look=(0.31, 5.72, FZ + 1.5), fov_deg=100, ref='v5:f_0172'),
    dict(name='desk', pos=(2.4, 3.5, FZ + 1.45), look=(4.3, 4.7, FZ + 0.8), fov_deg=100, ref='v5:f_0235'),
    dict(name='kit', pos=(3.2, 4.75, FZ + 1.25), look=(4.2, 4.7, FZ + 0.9), fov_deg=90, ref='v5:f_0237'),
    dict(name='velux', pos=(3.1, 4.8, FZ + 1.2), look=(3.15, 6.0, FZ + 1.9), fov_deg=100, ref='v5:f_0190'),
]

T = Matrix.Translation


def R(axis, deg):
    return Matrix.Rotation(math.radians(deg), 4, axis)


def mb(x=0.0, y=0.0, rot=0.0):
    return mo.MB().at(T((x, y, FZ)) @ R('Z', rot))


def col(name, hx, rough=0.6, metal=0):
    return M.solid('loft_' + name, hx, rough, metal)


def image(name, rough=0.85):
    return M.image_mat('loft_office_' + name, ART + name + '.jpg', None, roughness=rough)


def quad(b, mat, x0, x1, z0, z1, y):
    """Picture quad facing -Y showing the whole image once."""
    b._f(b._vs([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)]), b.mi(mat), [(0, 0), (1, 0), (1, 1), (0, 1)])


# ------------------------------------------------------------------ built-in cabinet (spec 5.1)
def cabinet(ctx):
    """White joinery on the south face of the block: pilasters, frieze, cornice, open shelves over four deep
    drawers, 30 mm proud of the block, in front of its 0.70 deep hollow (house.json loft_cabinet_recess: x 0.44..1.12,
    y 5.38..6.08, h 0.09..1.89, the opening between the pilasters)."""
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
    b.box((-.45, -.012, 1.89), (.45, proud, 2.06), wh)                              # frieze and the cornice core
    cyma = [(0, 0), (.02, 0), (.02, .03), (.035, .036), (.05, .06), (.07, .066), (.07, .10), (0, .10)]
    b.sweep(cyma, [(.45, proud, 1.96), (.45, -.012, 1.96), (-.45, -.012, 1.96), (-.45, proud, 1.96)], wh)
    b.box((-.52, -.082, 2.06), (.52, proud, 2.118), wh)                             # top fascia up to the ceiling
    b.box((-.34, .004, 0), (.34, proud, .09), wh)                                   # plinth under the drawers
    b.box((-.34, -.02, .856), (.34, D, .88), wh, bev=.002)                          # ledge
    for z in (1.24, 1.49):
        b.box((-.34, .01, z), (.34, D, z + .02), wh)                                # fixed shelves
    ctx.add(b.finish('loft_office.cabinet'), ROOM, 'fit', plan_sym='cabinet')

    for i, card in enumerate(('#A9C3DB', '#2F5A3C', '#C8A22C', '#7B2026')):         # bottom -> top
        z0 = .09 + i * .191
        b = mo.MB().at(here)
        b.box((-.34, -.02, z0), (.34, 0, z0 + .185), wh, bev=.002)                  # slab front
        for sx in (-1, 1):
            b.box((sx * .298, 0, z0 + .02), (sx * .31, .70, z0 + .165), wh)         # box sides, back, bottom
        b.box((-.298, .688, z0 + .02), (.298, .70, z0 + .165), wh)
        b.box((-.298, 0, z0 + .02), (.298, .688, z0 + .032), wh)
        b.box((-.035, -.0235, z0 + .115), (.035, -.02, z0 + .155), 'brass', bev=.001)        # card holder
        b.box((-.028, -.025, z0 + .121), (.028, -.0235, z0 + .149), col('card%d' % i, card, .8))
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
    b.box((-.31, .03, .88), (-.13, .03 + d(.22), 1.16), 'black_matt', bev=.004)     # black box
    b.box((-.14, .02, 1.26), (.30, .02 + d(.30), 1.41), 'black_matt', bev=.006)     # inkjet on the middle shelf
    x = -.325
    for wd, h, c in ((.075, .32, '#1C1C1E'), (.075, .32, '#1C1C1E'), (.075, .32, '#1C1C1E'), (.05, .31, '#6A2A22'),
                     (.03, .30, '#2C4A8C'), (.03, .31, '#2C4A8C'), (.04, .31, '#D9B62B'), (.09, .26, '#E6E0CC'),
                     (.09, .26, '#E6E0CC')):                                        # files and folders, blank spines
        b.box((x, .02, 1.51), (x + wd - .004, .02 + d(.28), 1.51 + h), col('file' + c[1:], c, .7), bev=.002)
        x += wd
    ctx.add(b.finish('loft_office.cabinet.contents'), ROOM, 'decor')


# ------------------------------------------------------------------ west wall: radiator and flags
def radiator(ctx):
    """White column radiator, 20 round-topped sections, 1.25 x 0.52, 40 mm off the wall (spec 5.2)."""
    b = mb(-0.65, 0)
    for i in range(20):
        y = 3.25 + 0.0625 * (i + .5)
        b.tube([(.059, y, .17), (.059, y, .60), (.072, y, .632), (.108, y, .632), (.121, y, .60), (.121, y, .17),
                (.108, y, .148), (.072, y, .148)], .019, 'white_gloss', n=8, closed=True, up=(0, 1, 0))
    for y in (3.215, 4.535):                                                        # valves and tails into the floor
        b.tube([(.09, y, 0), (.09, y, .16)], .008, 'chrome', n=6)
        b.box((.075, y - .02, .14), (.105, y + .02, .185), 'chrome', bev=.004)
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
    """Sit-stand desk x 3.50..4.30, y 3.60..5.40, top 0.74: oak-effect top on black T-legs, felt mat."""
    b = mb()
    b.box((3.50, 3.60, .70), (4.30, 5.40, .74), 'oak_light', bev=.003)
    for y in (3.90, 5.10):
        b.box((3.86, y - .04, .03), (3.94, y + .04, .70), 'black_matt', bev=.003)
        b.box((3.55, y - .035, 0), (4.25, y + .035, .03), 'black_matt', bev=.003)
    b.box((3.88, 3.90, .63), (3.92, 5.10, .69), 'black_matt')
    b.box((3.56, 3.98, .74), (3.96, 4.88, .743), col('felt', '#1D1D20', 1.0))
    # [round 4] baked (furniture is probe-lit by default): the desk lamp's pool falls on this top, and a probe-lit top
    # showed nothing when the lamp was switched (IX-07)
    ctx.add(b.finish('loft_office.desk'), ROOM, 'furn', plan_sym='desk', lm='static')

    b, blk, scr, grey = mb(), 'black_matt', 'screen_black', col('alu', '#8D9096', .45, 1)
    # 49-inch curved ultrawide: 8 facets on a 1.8 m radius, centre y 4.17, 0.15 off the wall; both screens top out
    # at 1.13, the bottom of the periodic table (hr_235), with a clear gap between them
    Rr, n, a1 = 1.8, 8, math.asin(.6 / 1.8)
    arc = lambda r, k: (4.15 - Rr + r * math.cos(-a1 + 2 * a1 * k / n), 4.17 + r * math.sin(-a1 + 2 * a1 * k / n))
    for k in range(n):
        (ax, ay), (bx, by), (cx, cy), (dx, dy) = arc(Rr, k), arc(Rr, k + 1), arc(Rr + .025, k + 1), arc(Rr + .025, k)
        b.prism([(ax, ay, .76), (bx, by, .76), (cx, cy, .76), (dx, dy, .76)], (0, 0, .37), scr)
    b.box((4.177, 4.13, .752), (4.21, 4.21, .93), blk)
    b.box((4.02, 4.02, .74), (4.24, 4.32, .752), blk, bev=.003)
    # 27-inch on an arm, turned a little toward the chair; webcam on top
    b.at(T((4.12, 5.10, FZ)) @ R('Z', -14))
    b.box((0, -.305, .77), (.02, .305, 1.13), scr, bev=.002)
    b.box((-.01, -.04, 1.13), (.03, .04, 1.16), blk, bev=.003)
    b.box((.02, -.03, .88), (.10, .03, .94), blk)
    b.at(T((0, 0, FZ)))
    b.tube([(4.24, 5.11, .74), (4.24, 5.11, .91), (4.20, 5.10, .91)], .014, blk, n=8)
    # laptop on a stand (lid open, blank), keyboard, mouse
    lap = T((3.95, 4.47, FZ + .80)) @ R('Y', -14)
    b.at(lap)
    b.box((-.11, -.16, 0), (.11, .16, .015), grey, bev=.002)
    b.at(lap @ T((.11, 0, .015)) @ R('Y', 100))
    b.box((-.21, -.16, 0), (0, .16, .008), grey, bev=.002)
    b.box((-.20, -.15, -.0006), (-.01, .15, 0), scr)
    b.at(T((0, 0, FZ)))
    for y in (4.36, 4.58):
        b.box((3.87, y - .01, .74), (4.04, y + .01, .79), blk)
    b.box((3.62, 4.28, .743), (3.75, 4.66, .753), grey, bev=.002)
    b.box((3.65, 4.72, .743), (3.75, 4.78, .765), blk, bev=.008)
    ctx.add(b.finish('loft_office.desk.computers'), ROOM, 'furn')

    b = mb()                                              # PC tower on the floor north of the desk
    b.box((3.935, 5.42, .01), (4.165, 5.92, .51), 'black_gloss', bev=.006)
    ctx.add(b.finish('loft_office.pc_tower'), ROOM, 'furn', plan_sym='cabinet')

    # architect lamp clamped to the north-west corner of the desk; the bulb is its own emissive slot
    b = mb()
    b.box((3.50, 5.30, .69), (3.56, 5.36, .76), 'black_matt', bev=.004)
    arm = [(3.53, 5.33, .76), (3.60, 5.36, 1.14), (3.70, 5.10, 1.26)]
    b.tube(arm, .007, 'black_matt', n=6)
    b.at(T((3.70, 5.10, FZ + 1.26)) @ R('X', 150))        # shade: cone opening down toward the desk
    b.lathe([(.022, 0), (.085, .12), (.08, .12), (.02, .006)], P.two_sided('black_matt'), 16)
    b.lathe([(0, .05), (.03, .05), (.03, .052), (0, .052)], P.emissive('#F4CB94', 6.0), 12)
    lamp = b.finish('loft_office.desk_lamp')
    IX.tag(lamp, 'lamp', label='Desk lamp')
    ctx.add(lamp, ROOM, 'light')
    # [round 4] its Cycles lamp, just under the bulb disc inside the shade (IX-07: without one the export made no circuit
    # and the switch changed nothing); the name extends the fitting's, so it bakes as circuit 'desk_lamp' (INTERACT.md)
    lighting.bulb(ctx, ROOM, (3.70, 5.065, FZ + 1.20), watts=5, kelvin=3000, radius=.02, name='loft_office.desk_lamp.bulb')


def office_chair(ctx):
    """Ergonomic mesh chair, white shell, grey mesh, polished five-star base. Local: sitter faces -Y."""
    b, wh, mesh, cr = mo.MB(), 'plastic_white', col('mesh', '#8B8E94', .95), 'chrome'
    for k in range(5):
        b.at(R('Z', 72 * k + 18))
        b.box((-.022, 0, .07), (.022, .32, .10), cr, bev=.006)
        b.at(R('Z', 72 * k + 18) @ T((0, .31, .03)) @ R('Y', 90))
        b.lathe([(0, -.02), (.028, -.02), (.028, .02), (0, .02)], 'black_matt', 10)
    b.at()
    b.lathe([(0, .07), (.045, .07), (.03, .12), (.025, .40), (0, .40)], cr, 12)
    b.box((-.25, -.25, .43), (.25, .23, .455), wh, bev=.01)
    b.box((-.24, -.25, .455), (.24, .22, .50), mesh, bev=.015)
    for s in (-1, 1):                                      # flip-up arms
        b.box((s * .27, .02, .44), (s * .30, .08, .67), wh, bev=.004)
        b.box((s * .245, -.14, .67), (s * .325, .12, .70), mesh, bev=.008)
    b.at(T((0, .22, .50)) @ R('X', -10))                   # back, leaning 10 degrees
    b.box((-.035, .02, -.05), (.035, .05, .60), wh, bev=.006)
    for s in (-1, 1):
        b.box((s * .23, -.01, .06), (s * .205, .02, .60), wh, bev=.006)
    for z in (.06, .585):
        b.box((-.23, -.01, z), (.23, .02, z + .028), wh, bev=.006)
    b.box((-.207, .0, .085), (.207, .008, .588), mesh)
    b.box((-.14, -.03, .66), (.14, .01, .78), mesh, bev=.012)   # headrest
    b.box((-.02, .0, .58), (.02, .03, .70), wh, bev=.004)
    ob = b.finish('loft_office.office_chair')
    ob.matrix_basis = T((3.05, 4.35, FZ)) @ R('Z', 90)     # facing the desk (+X)
    IX.tag(ob, 'hinge', p=(3.05, 4.35, FZ), deg=-70, label='Chair', dur=1.0)
    ctx.add(ob, ROOM, 'furn', plan_sym='office_chair')


def stool(ctx):
    """Piano stool 0.35 x 0.55 x 0.48: dark box seat with a padded check lid on splayed tapered legs."""
    b = mo.MB()
    b.box((-.165, -.265, .29), (.165, .265, .42), 'mahogany_dark', bev=.004)
    root = b.finish('loft_office.stool')
    pad = P.upholstered_seat(.35, .55, .06, mat='check_grey', name='loft_office.stool.pad')
    pad.parent, pad.location = root, (0, 0, .42)
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        leg = P.turned_leg(.30, .034, 'taper', mat='mahogany_dark', name=f'loft_office.stool.leg.{i}')
        leg.parent, leg.location = root, (sx * .15, sy * .25, 0)
        leg.rotation_euler = (math.radians(5 * sy), math.radians(-5 * sx), 0)
    root.location = (3.15, 5.35, FZ)
    ctx.add(root, ROOM, 'furn', plan_sym='stool')


def bookcase(ctx):
    """Rustic oak open bookcase 0.90 x 0.30 x 0.90 tight against the front knee wall, its top level with the arris
    where the slope starts (hr_172, hr_252); 0.07 east of the filmed spot so the west hatch's east leaf (x <= 0.77
    over the bookcase depth at 110 degrees) swings past it."""
    x, y = 1.27, 2.575
    c = P.cabinet_carcass(.90, .30, .86, 'oak_rustic', plinth=.06, open_front=True, shelves=2,
                          name='loft_office.bookcase')
    ctx.add(P.place(c, (x, y, FZ), facing=S), ROOM, 'furn', plan_sym='bookcase')
    b = mb(x, y)
    b.box((-.47, -.02, .86), (.47, .32, .90), 'oak_rustic', bev=.008)               # chunky top
    for x0, x1, c2 in ((-.38, -.22, '#7FA6A8'), (-.20, -.04, '#6B2A35'), (.10, .32, '#E9E6DC')):   # plain boxes
        b.box((x0, .05, .605), (x1, .25, .735), col('box' + c2[1:], c2, .8), bev=.003)
    b.at(T((x + .25, y + .15, FZ + .90)))                                           # incense burner
    b.lathe([(0, 0), (.03, 0), (.045, .02), (.04, .045), (.015, .055), (.012, .07), (0, .075)], 'brass_antique', 12)
    ctx.add(b.finish('loft_office.bookcase.top'), ROOM, 'decor')
    for i, (z, ln, seed) in enumerate(((.078, .62, 3), (.351, .5, 8))):
        bk = P.book_row(ln, .21, .16, seed=seed, name=f'loft_office.books.{i}')
        ctx.add(P.place(bk, (x + (.08 if i else -.08), y + .02, FZ + z), facing=S), ROOM, 'decor')


def tables(ctx):
    b, oak = mb(), 'oak_rustic'                            # coffee table 1.00 x 0.50 x 0.45, low shelf
    x0, x1, y0, y1 = .95, 1.95, 3.15, 3.65
    b.box((x0, y0, .415), (x1, y1, .45), oak, bev=.004)
    b.box((x0 + .05, y0 + .05, .10), (x1 - .05, y1 - .05, .12), oak)
    for x in (x0 + .03, x1 - .09):
        for y in (y0 + .03, y1 - .09):
            b.box((x, y, 0), (x + .06, y + .06, .415), oak, bev=.003)
    ctx.add(b.finish('loft_office.coffee_table'), ROOM, 'furn', plan_sym='coffee_table')

    b, wire = mb(), 'plastic_white'                        # drawer trolley 0.55 x 0.45 x 0.85, four mesh baskets
    x0, x1, y0, y1 = 3.72, 4.26, 2.75, 3.20                # clear of the east wall's skirting
    for x in (x0, x1 - .03):
        for y in (y0, y1 - .03):
            b.box((x, y, 0), (x + .03, y + .03, .83), 'oak_light')
    b.box((x0, y0, .83), (x1, y1, .85), 'oak_light', bev=.003)
    for k in range(4):
        z = .06 + k * .19
        b.box((x0 + .035, y0 + .01, z), (x1 - .035, y1 - .01, z + .012), wire)
        for lo, hi in (((x0 + .035, y0 + .01), (x1 - .035, y0 + .018)), ((x0 + .035, y1 - .018), (x1 - .035, y1 - .01)),
                       ((x0 + .035, y0 + .018), (x0 + .043, y1 - .018)), ((x1 - .043, y0 + .018), (x1 - .035, y1 - .018))):
            b.box((*lo, z + .012), (*hi, z + .15), wire)
    ctx.add(b.finish('loft_office.trolley'), ROOM, 'furn', plan_sym='chest')


# ------------------------------------------------------------------ fixed fittings
def aircon(ctx):
    """Split-system indoor unit under the flat ceiling on the east wall; the louvre opens from the remote."""
    b, g = mb(), 'loft_office.aircon'
    b.box((4.09, 4.60, 1.78), (4.298, 5.40, 2.07), 'plastic_white', bev=.025)
    b.box((4.088, 4.63, 1.86), (4.091, 5.37, 1.863), col('slot', '#3A3C40'))
    ctx.add(b.finish(g), ROOM, 'fit')
    b = mb()
    b.box((4.105, 4.63, 1.772), (4.205, 5.37, 1.779), 'plastic_white')
    flap = b.finish(g + '.louvre')
    IX.tag(flap, 'hinge', g=g, label='Air conditioning', p=(4.205, 5.0, FZ + 1.779), a=(0, 1, 0), deg=-55, reach=3.0)
    ctx.add(flap, ROOM, 'fit', lm='dynamic')
    b = mb(0.31, 5.70)                                    # remote in its wall cradle beside the dimmer
    b.box((-.022, -.03, 1.14), (0, .03, 1.24), 'plastic_white', bev=.003)
    b.box((-.022, -.03, 1.14), (-.014, .03, 1.19), 'plastic_white', bev=.002)
    ctx.add(b.finish(g + '.cradle'), ROOM, 'fit')
    b = mb(0.31, 5.70)
    b.box((-.014, -.022, 1.15), (-.004, .022, 1.29), col('remote', '#E9E9E6', .5), bev=.003)
    remote = b.finish(g + '.remote')
    IX.tag(remote, 'trigger', g=g, label='Air conditioning')
    ctx.add(remote, ROOM, 'fit', lm='dynamic')


def tv(ctx):
    """50-inch TV on the block's east face, medal rail under it, two small frames over it (spec 5.4, 7).
    Everything here stays within 42 mm of the wall (the rear hatch's west leaf swings to x 1.43, 95 degrees)."""
    set_ = P.place(P.tv_panel(1.11, .64, standoff=.012, name='loft_office.tv'), (1.25, 6.015, FZ + 1.07), facing=W)
    pic = P.tv_screen(1.10, .63, name='loft_office.tv.picture')
    pic.location, pic.rotation_euler = set_.matrix_basis @ Vector((0, -.0436, 0)), set_.rotation_euler
    IX.tag(set_, 'trigger', g='loft_office.tv', label='TV')
    IX.tag(pic, 'show', g='loft_office.tv', when=1, fx='tv')
    ctx.add(set_, ROOM, 'fit', plan_sym='tv')
    ctx.add(pic, ROOM, 'fit', lm='dynamic')
    framed(ctx, 'tv_frame.0', (1.25, 5.63, FZ + 1.635), W, None, .32, .27, 'champagne', mount=.04)
    framed(ctx, 'tv_frame.1', (1.25, 5.98, FZ + 1.535), W, None, .24, .23, 'dark_wood')

    rail = mo.brass_rail([(1.28, 5.55, FZ + .72), (1.28, 6.30, FZ + .72)], 'loft_office.medal_rail', r=.008, off=.03)
    ctx.add(rail, ROOM, 'decor')
    b = mb()                                              # eight plain ribbons with plain discs, no lettering
    for k, c in enumerate(('#6E9A3A', '#D0872B', '#1F1F22', '#3D7FB5', '#69A7C9', '#2B56A0', '#8BB7D6', '#A32A2A')):
        y = 5.93 + k * .047
        b.box((1.289, y - .015, .34 + .01 * (k % 3)), (1.291, y + .015, .725), col('ribbon' + c[1:], c, .9))
        b.at(T((1.287, y, FZ + .31 + .01 * (k % 3))) @ R('Y', 90))
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
    spots = [(x, y) for x in (0.1, 2.3, 3.7) for y in (4.75, 5.25)] + [(-0.17, 5.75)]
    for i, (x, y) in enumerate(spots):
        lighting.downlight(ctx, ROOM, x, y, watts=110, name=f'loft_office.downlight.{i}')
        trim = P.place(P.downlight(name=f'loft_office.downlight_trim.{i}'), (x, y, ctx.ceil_z(ROOM, x, y)))
        ctx.add(trim, ROOM, 'light')
    sw = P.place(P.switch_plate(1, 'dimmer', name='loft_office.dimmer'), (0.31, 5.83, FZ + 1.22), facing=E)
    IX.tag(sw, 'light', rooms=[ROOM], label='Lights')
    ctx.add(sw, ROOM, 'fit', lm='dynamic')
    for i, (loc, facing) in enumerate((((4.30, 4.2, FZ + .30), E), ((4.30, 5.2, FZ + .30), E), ((3.95, 6.59, FZ + .30), N))):
        ctx.add(P.place(P.socket(2, name=f'loft_office.socket.{i}'), loc, facing=facing), ROOM, 'fit')


def build(ctx):
    cabinet(ctx)
    radiator(ctx)
    flag(ctx, 'flag.union', 'union', .98, 1.49, 5.09, .16, True)           # hoist up, as it hangs
    flag(ctx, 'flag.ensign', 'ensign', .50, .79, 2.90, .16, False)
    desk(ctx)
    office_chair(ctx)
    stool(ctx)
    bookcase(ctx)
    tables(ctx)
    aircon(ctx)
    tv(ctx)
    velux_blind(ctx)
    lights(ctx)

    # Chippendale chair (same set as the dining room), 0.3 m north of where it was filmed so the hatch behind it opens
    ch = P.place(chippendale_chair('loft_office.chair'), (0.05, 3.34, FZ), rot_z=180)
    ctx.add(ch, ROOM, 'furn', plan_sym='chair')
    plant = P.plant_potted('monstera', height=.62, spread=.45, pot_dia=.30, pot_h=.22, pot_mat='#B39C78',
                           name='loft_office.plant')
    ctx.add(P.place(plant, (4.06, 6.30, FZ)), ROOM, 'decor', plan_sym='plant')

    # lobby: carved hardwood panel in a deep gilt frame (rectified crop of the carving)
    framed(ctx, 'carving', (0.31, 5.72, FZ + 1.72), E, ART + 'carving.jpg', .40, .60, 'gilt_plain', frame_w=.09, depth=.07)
    # east wall: periodic table, two small frames; the dark wall below them is bare (hr_183, f_0240). The spec's
    # "W-east certificate with a red seal" is the rear knee wall's cert.3 seen across the corner.
    framed(ctx, 'periodic', (4.30, 5.02, FZ + 1.44), E, ART + 'periodic.jpg', .90, .62, 'black')
    framed(ctx, 'east_frame.0', (4.30, 5.71, FZ + 1.63), E, None, .38, .26, 'gilt_plain', frame_w=.035,
           mount=.03, fill=('#C2493D', '#E3C45A', '#3F6FA8'))
    framed(ctx, 'east_frame.1', (4.30, 5.71, FZ + 1.30), E, None, .38, .30, 'black', mount=.045, mount_mat='#6B2A35',
           fill=('#4E8A6A', '#E3C45A', '#C2493D'))
    # rear knee wall: seven certificates, blank sheets
    styles = (('gilt_plain', '#1E2A44'), ('dark_wood', '#1E2A44'), ('walnut_gold', '#5C2630'), ('black', '#22242A'))
    for i, x in enumerate((2.79, 3.197, 3.603, 4.01)):
        cert(ctx, f'cert.{i}', (x, 6.59, FZ + 1.05), N, .34, .48, *styles[i], seal=i in (2, 3))
    for i, x in enumerate((2.79, 3.21, 3.63)):
        cert(ctx, f'cert.{i + 4}', (x, 6.59, FZ + .475), N, .34, .45, *styles[(i + 2) % 4])

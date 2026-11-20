"""Second-floor rear study / office. Spec: spec/rooms/study.md (reconciled dimensions at its end win).

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --levels 2 --only shell,study --preview study \
         --res 540x960 --samples 64 --tag study          (open state: --pose 1 --tag study1)

World coords, metres; heights below are above the room floor (Z 6.02). L-shaped: neck x -0.65..0.30, y 13.04..14.15,
then the room x -0.65..3.10, y 14.15..16.86. W = x -0.65 (rose feature wall), N = y 16.86 (window), S = y 14.15.
Walls, door, window with its opening casements, skirting and cove are shell. Builders: rooms/study_parts.py.

Deviations from the spec (all inside its +-0.2 m furniture tolerance), so that doors, drawers and the walker clear:
desks 0.15 further east (desk B x 0.30..1.50, desk A x 1.50..2.30) - the bookcase doors open into the lane beside
desk B; radiator and a/c 0.06 / 0.04 further west. The window is 1.00 wide (x 0.76..1.76, round 3); the curtain pole
runs x 0.40..2.12, 0.26 clear of the a/c.
Corrected from the footage: the drawer pedestal stands in front of the radiator (x -0.45..-0.09, y 16.08..16.66) with
its drawer face to the south and four drawers (three shallow, one deep: hr_v4_449), not five facing east; the only
plate on the E wall is a single-gang outlet at z 1.03 (v4:f_0486), not a double socket at 0.40; the flat monitor's
screen faces the office chair.
"""
import math
import os

from mathutils import Matrix, Vector

from lib import interact as IX, lighting, materials as M, mouldings as mo, props as P, shell
from rooms import study_parts as S
from rooms.study_parts import T, RZ, facing, m

ROOM = 'study'
ART = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'textures', 'art'))
XW, XE, YS, YN = -0.65, 3.10, 14.15, 16.86          # wall faces of the main room
XNECK = 0.30                                         # east wall of the neck
DOWN_W = 85                                          # per downlight: the footage is a bright daylit room
ROSE = '#BCA3A5'                                     # W wall as it reads in v4:f_0510 / f_0518 (shell: #BC9D99), mauve
CURTAIN = '#BBB8B4'                                  # silver-grey damask (plain: no such texture in the library)
POLE = '#A08A70'                                     # mid-brown oak pole (hr_v4_559 samples #66533F..#866E5C)

_Z = 6.02 + 1.5
CAMERAS = [
    dict(name='door', pos=(-0.17, 13.12, _Z), look=(0.25, 16.5, 7.05), fov_deg=100, ref='v4:f_0444'),
    dict(name='overall', pos=(0.10, 14.30, _Z + .05), look=(2.2, 16.6, 7.2), fov_deg=100, ref='v4:f_0564'),
    dict(name='wwall', pos=(2.70, 16.50, 7.60), look=(-0.65, 15.1, 7.25), fov_deg=100, ref='v4:f_0510'),
    dict(name='desk', pos=(2.80, 16.35, _Z + .05), look=(1.8, 14.6, 6.9), fov_deg=100, ref='v4:f_0488'),
    dict(name='corner', pos=(2.20, 16.60, _Z), look=(2.85, 14.3, 6.95), fov_deg=100, ref='v4:f_0486'),
    dict(name='settee', pos=(1.0, 15.45, 7.4), look=(0.92, 14.15, 6.6), fov_deg=100, ref='v4:f_0544'),
    dict(name='window', pos=(0.55, 14.85, _Z), look=(1.5, 16.86, 7.3), fov_deg=100, ref='v4:f_0560'),
    dict(name='nw', pos=(1.0, 15.3, _Z), look=(-0.4, 16.7, 7.0), fov_deg=100, ref='v4:f_0514'),
    dict(name='bookcase', pos=(0.95, 15.25, 7.25), look=(-0.65, 15.45, 6.65), fov_deg=100, ref='v4:f_0518'),
    dict(name='cabinet', pos=(2.42, 15.25, 7.45), look=(2.92, 14.33, 6.85), fov_deg=100, ref='v4:f_0502'),
    dict(name='dimmer', pos=(-0.45, 13.55, 7.42), look=(0.30, 13.9, 7.27), fov_deg=90, ref='v4:f_0562'),
    dict(name='drawers', pos=(0.30, 14.90, 7.20), look=(-0.40, 16.2, 6.55), fov_deg=85, ref='v4:f_0450'),
]


def art(name):
    return os.path.join(ART, 'study_%s.jpg' % name)


def build(ctx):
    fz, cz = ctx.floor_z(ROOM), ctx.ceil_z(ROOM)

    def add(ob, kind, sym=None, lm=None):
        return ctx.add(ob, ROOM, kind, plan_sym=sym, lm=lm)

    def on(ob, x, y, z, face=None, rot=None):                     # z above the floor
        return P.place(ob, (x, y, fz + z), facing=face, rot_z=rot)

    W, N, Sw, E = (1, 0), (0, -1), (0, 1), (-1, 0)                 # wall normals into the room
    shell.repaint(ROOM, '#BC9D99', ROSE)

    fittings(ctx, add, on, fz, cz, W, N, E)
    curtains(add, on, fz, N)
    bookcase(add, on, fz, W)
    drawer_unit(add, on, fz)
    desks(ctx, add, on, fz, N)
    corner(add, on, fz)
    wall_art(add, on, W, N, Sw)

    add(on(S.settee('study.settee'), 0.905, YS, 0), 'furn', 'sofa')
    add(on(S.office_chair('study.office_chair'), 2.64, 15.50, 0, face=E), 'furn', 'office_chair')
    add(on(S.kneeling_chair('study.kneeling_chair'), 0.85, 15.10, 0, rot=-20), 'furn', 'stool')
    add(on(S.plant('study.plant'), 1.15, 16.48, 0), 'decor', 'plant')


# ----------------------------------------------------------------------------- fixed fittings, lights
def fittings(ctx, add, on, fz, cz, W, N, E):
    add(on(S.radiator('study.radiator'), -0.08, YN, 0.15, face=N), 'fit', 'radiator')
    add(on(S.aircon('study.aircon'), -0.205, YN, 2.17, face=N), 'fit')
    add(on(S.remote_cradle('study.ac_remote'), XNECK, 13.95, 1.24, face=E), 'fit')
    add(on(S.outlet_plate('study.outlet'), XE, 15.80, 1.03, face=E), 'fit')   # single-gang plate, centre outlet (v4:f_0486)
    add(on(S.detector('study.detector'), 2.30, 16.30, cz - fz), 'fit')

    fr = ctx.opening_frame('w_study')
    x0, x1 = fr['center'].x - fr['width'] / 2, fr['center'].x + fr['width'] / 2
    mb = mo.MB()                                                   # oak window board in the reveal, nosing to the room
    mb.box((x0 + .002, YN, fz + .681), (x1 - .002, YN + .198, fz + .706), 'oak_door', bev=.003, grain=0)
    mb.box((x0 - .03, YN - .035, fz + .681), (x1 + .03, YN, fz + .706), 'oak_door', bev=.006, grain=0)
    add(mb.finish('study.window_board'), 'fit')

    tv = on(P.tv_panel(1.45, .83, depth=.03, standoff=.02, name='study.tv'), XW, 15.35, 1.555, face=W)
    pic = P.tv_screen(1.44, .82, name='study.tv.picture')
    pic.location, pic.rotation_euler = tv.matrix_basis @ Vector((0, -.0516, 0)), tv.rotation_euler
    IX.tag(tv, 'trigger', g='study.tv', label='TV')
    IX.tag(pic, 'show', g='study.tv', when=1, fx='tv')
    add(tv, 'fit', 'tv')
    add(pic, 'fit', lm='dynamic')

    sw = on(P.switch_plate(1, 'dimmer', name='study.dimmer'), XNECK, 13.82, 1.25, face=E)
    IX.tag(sw, 'light', rooms=[ROOM], label='Lights')             # one rotary dimmer for all six downlights
    add(sw, 'fit')
    for i, (x, y) in enumerate(((-0.18, 13.65), (-0.05, 15.05), (1.25, 15.05), (2.50, 15.05), (0.60, 16.15), (1.90, 16.15))):
        lighting.downlight(ctx, ROOM, x, y, watts=DOWN_W, name='study.downlight.%d' % i)
        add(P.place(P.downlight(name='study.downlight_trim.%d' % i), (x, y, cz)), 'light')


def curtains(add, on, fz, N):
    """Pair with an eyelet heading on a mid-oak pole with ball finials (hr_v4_559), tied back (state 0) or drawn
    (state 1). The heading rises 50 mm above the pole axis and the pole runs through it on brushed-steel eyelet
    rings; the rings are part of each state (bunched over the stacks / spread across). Pole x 0.40..2.12 over the
    1.00 window, so the west finial stays clear of the a/c (x <= 0.235)."""
    xc, zp, sd, span, stack = 1.26, 2.26, .062, 1.68, .34           # pole centre x, axis z, axis off the wall; the
    # drops' inner edges on the window jambs (x 0.76 / 1.76), as in v4 f_0560
    kw = dict(width=span, height=2.28, mat=CURTAIN, stack=stack, tie_from_top=1.36, tassel=.15)   # top 2.31, hem 0.03, tie 0.95
    pole = P.curtain_pole(span + .04, .03, 'ball', rings=0, mat=M.solid('study_pole', POLE, .45), standoff=sd,
                          name='study.curtain.pole')
    add(on(pole, xc, YN, zp, face=N), 'decor')
    IX.tag(pole, 'trigger', g='study.curtain', label='Curtains')
    brackets = (xc - (span + .04) / 2 + .1, xc + (span + .04) / 2 - .1)   # as P.curtain_pole places them

    def spread(lo, hi, n):                                           # ring x, kept 18 mm off the brackets
        out = []
        for i in range(n):
            x = lo + (hi - lo) * (i + .5) / n
            b = min(brackets, key=lambda b: abs(x - b))
            out.append(x + max(0.0, .018 - abs(x - b)) * (1 if x >= b else -1))
        return out

    lo, hi, half = xc - span / 2, xc + span / 2, span / 2 + .01
    for state, closed in ((0, False), (1, True)):
        nm = 'study.curtain.' + ('closed' if closed else 'open')
        cloth = add(on(P.curtain_pair(hardware=False, closed=closed, name=nm, **kw), xc, YN, 2.31, face=N), 'decor',
                    lm='dynamic')
        xs = (spread(lo, lo + half, 7) + spread(hi - half, hi, 7)) if closed else \
            (spread(lo, lo + stack, 5) + spread(hi - stack, hi, 5))
        mb = mo.MB()
        for x in xs:                                                 # eyelets hang on the pole: centre 5 mm below its axis
            mb.tube([(x, YN - sd + .022 * math.cos(t), fz + zp - .005 + .022 * math.sin(t))
                     for t in (math.tau * k / 10 for k in range(10))], .0045, 'silver_satin', n=6, closed=True, up=(1, 0, 0))
        rings = add(mb.finish(nm + '.rings'), 'decor', lm='dynamic')
        IX.tag_many([cloth, rings], 'show', g='study.curtain', when=state, fx='none')


# ----------------------------------------------------------------------------- glazed bookcase under the TV
def bookcase(add, on, fz, W):
    """Dark mahogany, 1.02 x 0.33 x 0.83: lined carcass with two shelves of books, moulded top, two glazed doors
    hinged on their outer stiles."""
    mh, y0, y1, xf = 'mahogany_dark', 14.84, 15.86, XW + .33
    add(on(P.cabinet_carcass(1.02, .31, .80, mh, plinth=.07, plinth_recess=.0, open_front=True, shelves=2,
                             name='study.bookcase'), XW, 15.35, 0, face=W), 'furn', 'bookcase')
    mb = mo.MB()
    mb.box((XW, y0 - .02, fz + .80), (xf + .02, y1 + .02, fz + .83), mh, bev=.006, grain=1)
    mb.box((XW, y0 - .008, fz + .785), (xf + .008, y1 + .008, fz + .80), mh, bev=.004, grain=1)
    add(mb.finish('study.bookcase.top'), 'furn')
    for k, z in enumerate((.088, .328, .560)):
        add(on(P.book_row(.94, .19 - .02 * (k == 1), .16, seed=11 + k, fill=.97 - .12 * k, name='study.books.%d' % k),
               XW + .012, 15.35, z, face=W), 'decor')

    z0, z1, st = fz + .073, fz + .797, .045
    for tag, ya, yb, hinge, deg in (('s', y0 + .002, 15.349, y0 + .002, -95), ('n', 15.351, y1 - .002, y1 - .002, 90)):   # n: clear of the drawers
        mb = mo.MB()
        for a, b in ((ya, ya + st), (yb - st, yb)):
            mb.box((xf - .02, a, z0), (xf, b, z1), mh, bev=.002, grain=2)
        for a, b in ((z0, z0 + st), (z1 - st, z1)):
            mb.box((xf - .02, ya + st, a), (xf, yb - st, b), mh, bev=.002, grain=1)
        ym = (yb - .022) if tag == 's' else (ya + .022)                              # meeting stile
        mb.at(T(xf, ym, fz + .45) @ S.aim((1, 0, 0)))
        mb.lathe([(0, 0), (.006, 0), (.005, .008), (.011, .012), (.011, .018), (.006, .022), (0, .022)], 'brass', 10)
        mb.at()
        if tag == 'n':
            mb.box((xf, ym - .006, fz + .385), (xf + .0015, ym + .006, fz + .415), 'brass')   # key escutcheon
        door = mb.finish('study.bookcase.door.' + tag)
        gb = mo.MB()
        gb.face([(xf - .01, ya + st - .004, z0 + st - .004), (xf - .01, yb - st + .004, z0 + st - .004),
                 (xf - .01, yb - st + .004, z1 - st + .004), (xf - .01, ya + st - .004, z1 - st + .004)], 'glass_clear',
                hint=(1, 0, 0))
        glass = gb.finish('study.bookcase.door.%s.glass' % tag)
        IX.tag_many([door, glass], 'hinge', g='study.bookcase.' + tag, label='Bookcase', p=(xf, hinge, fz), deg=deg)
        add(door, 'furn', lm='dynamic')
        add(glass, 'furn', lm='dynamic')

    add(on(S.flower_frame('study.flower_frame'), XW + .13, 15.68, .83, face=W), 'decor')


# ----------------------------------------------------------------------------- white drawer pedestal
def drawer_unit(add, on, fz):
    """White pedestal on castors, 0.36 wide x 0.58 deep x 0.70, standing in front of the radiator with its narrow
    drawer face to the SOUTH, toward the bookcase (v4:f_0450, hr_v4_443 / _449; plain east face in f_0510): three
    shallow drawers over a deep one, inset between the carcass sides, a finger slot above each front."""
    x0, x1, y0, y1 = -0.45, -0.09, 16.08, 16.66                      # front y0; radiator front at y 16.70
    zb, zt = .06, .70                                                # carcass on 60 mm castors
    add(on(P.cabinet_carcass(x1 - x0, y1 - y0, zt - zb, 'white_gloss', plinth=0, open_front=True, name='study.drawers'),
           (x0 + x1) / 2, y1, zb, face=(0, -1)), 'furn', 'chest')
    mb = mo.MB()
    for x in (x0 + .05, x1 - .05):
        for y in (y0 + .06, y1 - .05):
            mb.at(T(x, y, fz))
            mb.lathe([(0, 0), (.02, 0), (.02, .045), (.008, .05), (.008, .06), (0, .06)], 'black_matt', 10)
    mb.at()
    add(mb.finish('study.drawers.castors'), 'furn')
    wh, gap, xa, xb = m('desk'), .015, x0 + .02, x1 - .02            # fronts inside the 18 mm sides, 2 mm reveal
    z = fz + zt - .018                                               # under the top panel
    for i, h in enumerate((.106, .106, .106, .222)):
        z -= gap + h
        mb = mo.MB()
        mb.box((xa, y0, z), (xb, y0 + .018, z + h), wh, bev=.002)                                  # front
        mb.box((xa + .006, y0 + .014, z + h - .004), (xb - .006, y0 + .02, z + h + gap - .002), 'black_matt')   # finger slot
        mb.box((xa + .008, y0 + .018, z + .008), (xb - .008, y1 - .03, z + .014), wh)               # tray
        for x in (xa + .008, xb - .014):
            mb.box((x, y0 + .018, z + .014), (x + .006, y1 - .03, z + h * .75), wh)
        mb.box((xa + .008, y1 - .036, z + .014), (xb - .008, y1 - .03, z + h * .75), wh)
        dr = mb.finish('study.drawers.drawer.%d' % i)
        IX.tag(dr, 'slide', label='Drawer', d=(0, -.20, 0))           # stops at y 15.88, clear of the bookcase (15.86)
        add(dr, 'furn', lm='dynamic')


# ----------------------------------------------------------------------------- desks, computers, desk lamp
def desks(ctx, add, on, fz, N):
    add(on(S.desk('study.desk_a', 1.60, .80), 1.90, 15.55, 0, rot=90), 'furn', 'desk')
    add(on(S.desk('study.desk_b', 1.20, .70), 0.90, 15.85, 0), 'furn', 'desk')
    mb, zt = mo.MB(), fz + .74
    B = T(1.85, 15.06, zt) @ facing(.7, .7)                        # curved ultrawide at the south end, facing NE
    S.riser(mb, B)
    S.monitor_curved(mb, B @ T(0, .02, .10))
    B = T(1.80, 15.98, zt) @ facing(.95, -.3)                      # flat 32-inch at the north end, screen toward the
    S.riser(mb, B)                                                 # chair (back seen from the window, hr_v4_485, and
    S.monitor_flat(mb, B @ T(0, 0, .10))                           # from the neck, hr_v4_565; screen from the E, hr_v4_487)
    S.keyboard_mouse(mb, T(2.10, 15.42, zt) @ RZ(90))
    add(S.weld(mb.finish('study.computers')), 'furn')

    lamp, under = S.desk_lamp('study.desk_lamp')                   # NE corner of desk A (hr_v4_563), head reaching south
    on(lamp, 2.20, 16.24, .74, face=(.1, -1))                      # beside the flat monitor's line of sight to the chair
    IX.tag(lamp, 'lamp', label='Desk lamp')
    add(lamp, 'light')
    lighting.bulb(ctx, ROOM, tuple(lamp.matrix_basis @ under), watts=5, kelvin=3000, radius=.03, name='study.desk_lamp.bulb')


# ----------------------------------------------------------------------------- corner cabinet (SE corner)
def corner(add, on, fz):
    Mw = Matrix(((-1, 0, 0, XE), (0, 1, 0, YS), (0, 0, 1, fz), (0, 0, 0, 1)))       # u along the S wall, v along the E wall
    cab, g = S.corner_cabinet('study.corner_cabinet', Mw)
    add(cab, 'furn', 'cabinet')
    add(S.ornaments('study.corner_cabinet.ornaments', Mw), 'decor')

    w = lambda p: Vector((XE - p[0], YS + p[1]))                   # local plan point -> world
    c0, c1 = w(g['c0']), w(g['c1'])
    e = (c1 - c0).normalized()
    out = Vector((-e.y, e.x)) if Vector((-e.y, e.x)).dot(Vector((-1, 1))) > 0 else Vector((e.y, -e.x))   # into the room
    a, b = c0 + e * .0625, c1 - e * .0625                          # door between the front stiles
    mid = (a + b) / 2 - out * .02
    door = P.place(P.panel_door((b - a).length, .522, t=.02, stile=.07, mat='oak_door', name='study.corner_cabinet.door'),
                   (mid.x, mid.y, fz + .115), facing=tuple(out))
    kp = b - e * .04
    knob = P.place(P.handle_knob(.025, .025, name='study.corner_cabinet.knob'), (kp.x, kp.y, fz + .40), facing=tuple(out))
    IX.tag_many([door, knob], 'hinge', g='study.corner_cabinet', label='Corner cabinet', p=(a.x, a.y, fz), deg=95)
    add(door, 'furn', lm='dynamic')
    add(knob, 'furn', lm='dynamic')


# ----------------------------------------------------------------------------- art and trophies
def wall_art(add, on, W, N, Sw):
    def pic(name, x, y, z, face, **kw):
        add(on(P.framed_picture(name='study.art.' + name, **kw), x, y, z, face=face), 'decor')

    neutral = ('#B9AE98', '#C9BFAA', '#D8D0BE')
    # W wall (feature wall)
    pic('cottage', XW, 14.15, 1.63, W, image=art('cottage'), w=.69, h=.62, frame_style='gilt_plain', frame_w=.03)
    pic('small', XW, 15.02, 1.06, W, w=.14, h=.16, frame_style='dark_gold_slip', frame_w=.03, mount=.015, fill=neutral)
    pic('cat', XW, 15.60, 1.04, W, image=art('cat'), w=.19, h=.21, frame_style='bronze_gold', frame_w=.058, depth=.03)
    pic('rooster', XW, 16.42, 1.47, W, image=art('rooster'), w=.42, h=.58, frame_style='champagne', frame_w=.05,
        depth=.05, glass=True)
    add(on(S.cats_frame('study.art.cats', art('cats')), XW, 15.30, 1.005, face=W), 'decor')
    add(on(S.goose_trophy('study.goose_trophy'), XW, 14.62, 2.25, face=W), 'decor')
    add(on(S.antler_trophy('study.antler_trophy'), XW, 15.40, 2.16, face=W), 'decor')
    # S wall
    pic('foliage', 2.05, YS, 1.80, Sw, image=art('foliage'), w=.52, h=.78, frame_style='walnut_gold', frame_w=.05, depth=.028)
    pic('green_small', 2.00, YS, 1.22, Sw, image=art('green_small'), w=.20, h=.25, frame_style='dark_gold_slip', frame_w=.045)
    add(on(S.octagon_frame('study.art.octagon', art('octagon')), 1.62, YS, 1.42, face=Sw), 'decor')
    # N wall, east of the window: both BLANK (privacy)
    add(on(S.certificate('study.certificate'), 2.55, YN, 1.85, face=N), 'decor')
    add(on(S.whiteboard('study.whiteboard'), 2.52, YN, 1.30, face=N), 'decor')

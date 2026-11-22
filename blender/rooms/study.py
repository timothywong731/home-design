"""Second-floor rear room `study`, named the Rose Room (2F rear, garden side). Spec: spec/rooms/study.md; round 3:
spec/phase3/briefs/study.md, spec/phase3/floor2_b.md section 1, spec/RECONCILE3.md floor2b-01..05.

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --levels 2 --only shell,study --preview study \
         --res 540x960 --samples 64 --tag r3study          (open state: --pose 1 --tag r3study1)

World coords, metres; heights below are above the room floor (Z 6.02). L-shaped: neck x -0.65..0.32, y 13.04..13.84
(0.97 x 0.80), then the main room x -0.65..3.10, y 13.84..16.86 (3.75 x 3.02). W = x -0.65 (rose feature wall),
N = y 16.86 (window w_study 1.55 x 1.56 from 0.58, centre x 1.255), S = y 13.84 (bathroom2 behind), E = x 3.10.
Walls, door, window with its top-hung lights, skirting and cornice are shell. Builders: rooms/study_parts.py; the
curtain jacquard is drawn by rooms/study_tex.py.

Positions (round 3, v13 of 21 Nov): items on the W wall keep their measured distance from the N wall; items keyed to
the S wall moved 0.31 south with it (settee, corner cabinet, pictures S1-S3, desk A 0.16 off the wall); desk B butts
desk A's W edge at y 14.95..15.65 (t127 / t129, see desks()), the kneeling chair between it and the settee; items on
the neck wall keep their distance from the door wall.
Deviations from the survey: the middle frame under the TV is 0.30 x 0.31 (survey 0.34 high) so that it clears both
the 0.90 bookcase top and the TV at 1.23; the drawer pedestal stands at x -0.31..0.05 (just clear of the bookcase
front) so its drawers run out; the E-wall plates are placed against the corner cabinet (0.24 / 0.54 N of it) as filmed
in t160, not at the survey's absolute y.
"""
import math
import os

from mathutils import Matrix, Vector

from lib import interact as IX, lighting, materials as M, mouldings as mo, props as P, shell
from rooms import study_parts as S
from rooms.study_parts import T, RZ, facing, m

ROOM = 'study'
ART = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'textures', 'art'))
XW, XE, YS, YN = -0.65, 3.10, 13.84, 16.86          # wall faces of the main room
XNECK, YDOOR = 0.32, 13.04                           # east wall of the neck, door wall
DOWN_W = 85                                          # per downlight: the footage is a bright daylit room
ROSE = '#C5ACA8'                                     # W wall: survey #C6ABA3 (v13), v4 #BC9D99: dusty rose-mauve
POLE = '#7E6048'                                     # mid-brown wooden pole (v13 t193.4 samples #5D493D in shade)

_Z = 6.02 + 1.5
CAMERAS = [
    dict(name='door', pos=(-0.17, 13.12, _Z + .05), look=(0.25, 16.5, 7.05), fov_deg=100, ref='v13:t127 / v4:f_0444'),
    dict(name='neck', pos=(0.18, 14.02, _Z), look=(2.9, 14.25, 7.0), fov_deg=100, ref='v13:t133'),
    dict(name='overall', pos=(0.15, 13.95, _Z + .05), look=(2.3, 16.6, 7.2), fov_deg=100, ref='v4:f_0564'),
    dict(name='wwall', pos=(1.75, 16.45, 7.55), look=(-0.65, 15.25, 7.30), fov_deg=100, ref='v13:t193.4 / v4:f_0510'),
    dict(name='desk', pos=(2.85, 15.95, 7.65), look=(1.75, 14.2, 6.85), fov_deg=100, ref='v13:t176'),
    dict(name='corner', pos=(2.55, 15.75, _Z), look=(3.0, 13.9, 6.9), fov_deg=100, ref='v13:t160'),
    dict(name='settee', pos=(1.0, 15.0, 7.4), look=(0.92, 13.84, 6.6), fov_deg=100, ref='v4:f_0544'),
    dict(name='window', pos=(1.05, 15.10, _Z), look=(1.25, 16.86, 6.95), fov_deg=100, ref='v13:t206 / v4:f_0560'),
    dict(name='nw', pos=(1.05, 15.35, _Z), look=(-0.3, 16.7, 7.2), fov_deg=100, ref='v13:t148'),
    dict(name='bookcase', pos=(0.95, 15.35, 7.25), look=(-0.65, 15.55, 6.75), fov_deg=100, ref='v13:t142'),
    dict(name='cabinet', pos=(2.40, 14.62, 7.40), look=(2.95, 14.0, 6.9), fov_deg=100, ref='v4:f_0502'),
    dict(name='dimmer', pos=(-0.30, 13.18, 7.45), look=(0.32, 13.45, 7.30), fov_deg=90, ref='v13:t127 / v4:f_0562'),
    dict(name='drawers', pos=(0.45, 15.15, 7.20), look=(-0.25, 16.3, 6.75), fov_deg=90, ref='v13:t193.4'),
    dict(name='beanbag', pos=(2.05, 15.75, 7.30), look=(2.95, 16.5, 6.3), fov_deg=100, ref='v13:t152 / t166'),
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

    fittings(ctx, add, on, fz, cz, W, N, E, Sw)
    window_board(ctx, add, fz)
    curtains(add, on, fz, N)
    bookcase(add, on, fz, W)
    drawer_unit(add, on, fz)
    desks(ctx, add, on, fz)
    corner(add, on, fz)
    wall_art(add, on, W, N, Sw)

    add(on(S.settee('study.settee'), 0.905, YS + .012, 0), 'furn', 'sofa')            # W arm 0.06 off the neck corner
    add(on(S.office_chair('study.office_chair'), 2.66, 14.86, 0, face=E), 'furn', 'office_chair')
    add(on(S.kneeling_chair('study.kneeling_chair'), 1.00, 14.68, 0, rot=85), 'furn', 'stool')   # faces W (t128 / t129)
    add(on(S.plant('study.plant'), 1.00, 16.45, 0), 'decor', 'plant')
    add(on(S.bean_bag('study.bean_bag'), 2.69, 16.43, 0, face=E), 'furn', 'armchair')   # NE corner, back on the E wall


# ----------------------------------------------------------------------------- fixed fittings, lights
def fittings(ctx, add, on, fz, cz, W, N, E, Sw):
    # radiator: 7 tubes 0.49 x 1.78, x -0.30..0.19, bottom 0.21, 0.09 off the wall (v13 t148, v4 f_0444 / f_0446)
    add(on(S.radiator('study.radiator'), -0.055, YN, 0.21, face=N), 'fit', 'radiator')
    # a/c 0.80 x 0.30 x 0.22, x -0.62..0.18, z 2.10..2.40 (v13 t147 / t148 / t193.4)
    add(on(S.aircon('study.aircon'), -0.22, YN, 2.10, face=N), 'fit')
    # neck E wall: dimmer 0.34 N of the door wall, the remote cradle 0.12 further N (v13 t127): satin nickel plate
    satin = M.solid('study_satin_nickel', '#B2B2AE', .4, .85)
    sw = on(P.switch_plate(1, 'dimmer', finish=satin, name='study.dimmer'), XNECK, YDOOR + .34, 1.32, face=E)
    IX.tag(sw, 'light', rooms=[ROOM], circuit='main', label='Lights')   # the six downlights, not the plug-in desk lamp
    add(sw, 'fit')
    add(on(S.remote_cradle('study.ac_remote'), XNECK, YDOOR + .46, 1.25, face=E), 'fit')
    # E wall: single outlet plate z 1.05 and a double socket z 0.35 below-north of it (t160); S wall: double socket
    # z 0.25 at x 2.35, just W of the corner cabinet (f_0178)
    add(on(S.outlet_plate('study.outlet'), XE, 14.68, 1.05, face=E), 'fit')
    add(on(P.socket(2, name='study.socket.e'), XE, 14.98, 0.35, face=E), 'fit')
    add(on(P.socket(2, name='study.socket.s'), 2.35, YS, 0.25, face=Sw), 'fit')
    add(on(S.detector('study.detector'), 2.30, 16.30, cz - fz), 'fit')

    # wall TV: 55-inch 1.23 x 0.71, y 14.83..16.06, z 1.23..1.94 (v4 f_0510, v13 t193.4), flat bracket
    tw, th, tz, ty = 1.23, .71, 1.585, 15.445
    tv = on(P.tv_panel(tw, th, depth=.03, standoff=.02, name='study.tv'), XW, ty, tz, face=W)
    pic = P.tv_screen(tw - .01, th - .01, name='study.tv.picture')
    pic.location, pic.rotation_euler = tv.matrix_basis @ Vector((0, -.0516, 0)), tv.rotation_euler
    IX.tag(tv, 'trigger', g='study.tv', label='TV')
    IX.tag(pic, 'show', g='study.tv', when=1, fx='tv')
    add(tv, 'fit', 'tv')
    add(pic, 'fit', lm='dynamic')
    mb = mo.MB()                                                   # two small bracket hooks under the bottom edge
    for dy in (-.30, .30):
        mb.box((XW, ty + dy - .012, fz + tz - th / 2 - .03), (XW + .045, ty + dy + .012, fz + tz - th / 2 + .02),
               'black_matt', bev=.003)
    add(mb.finish('study.tv.hooks'), 'fit')

    # six downlights in a 3 x 2 grid over the main room, none in the neck (v4 f_0563 / f_0565, v13 t193.4)
    for i, (x, y) in enumerate((x, y) for y in (14.75, 16.10) for x in (0.05, 1.25, 2.50)):
        lighting.downlight(ctx, ROOM, x, y, watts=DOWN_W, name='study.downlight.%d' % i)
        add(P.place(P.downlight(name='study.downlight_trim.%d' % i), (x, y, cz)), 'light')


def window_board(ctx, add, fz):
    """Oak window board 0.24 deep in the square reveal, on its bottom (the sill, 0.58) and up to the frame, with a
    25 mm bull-nose in front of the wall face; full opening width, the ends housed 5 mm into the reveals (v13 t206,
    t194.4)."""
    fr = ctx.opening_frame('w_study')
    x0, x1 = fr['center'].x - fr['width'] / 2 - .005, fr['center'].x + fr['width'] / 2 + .005
    z0 = fz + fr['sill']                                           # bottom of the hole = top of the reveal floor
    yb = YN + .238                                                 # back edge on the frame (joinery: inner face 17.102)
    t, r1, r2 = .022, .011, .005
    prof = [(yb, z0), (yb, z0 + t)]
    prof += [(YN - .025 + r1 - r1 * math.sin(math.pi / 2 * k / 4), z0 + t - r1 + r1 * math.cos(math.pi / 2 * k / 4))
             for k in range(5)]                                    # top front round
    prof += [(YN - .025 + r2 - r2 * math.cos(math.pi / 2 * k / 3), z0 + r2 - r2 * math.sin(math.pi / 2 * k / 3))
             for k in range(1, 4)]                                 # bottom front round
    mb = mo.MB()
    mb.prism([(x0, y, z) for y, z in prof], (x1 - x0, 0, 0), 'oak_door', grain=0)
    add(mb.finish('study.window_board'), 'fit')


def curtains(add, on, fz, N):
    """Pair of pale silver-grey jacquard curtains (generated tone-on-tone damask, rooms/study_tex.py) with an eyelet
    heading on a mid-brown wooden pole with ball finials: pole 1.88 long centred on the window axis, axis z 2.30;
    stacks 0.30 wide covering the jambs, full length to 0.03, tied at 0.95 with pale-gold ropes and 0.20 tassels
    (v13 t152 / t193.4, v4 hr_v4_563). State 0 tied back, state 1 drawn; the eyelet rings belong to each state."""
    xc, zp, sd = 1.255, 2.30, .062                                  # pole centre x, axis z, axis off the wall
    span, stack, ztop = 1.84, .30, 2.335                            # outer edges 0.335..2.175; heading top
    cloth_m = M.image_mat('study_curtain', art('curtain'), (0.64, 0.64), roughness=0.85)
    kw = dict(width=span, height=ztop - .03, mat=cloth_m, stack=stack, tie_from_top=ztop - .95, tassel=.20,
              tie_mat='rope_cream', tassel_mat='tassel_gold')
    pole = add(curtain_pole(xc, YN - sd, fz + zp), 'decor')
    IX.tag(pole, 'trigger', g='study.curtain', label='Curtains')
    brackets = (xc - .81, xc + .81)                                  # as curtain_pole() places them

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
        cloth = add(on(P.curtain_pair(hardware=False, closed=closed, name=nm, **kw), xc, YN, ztop, face=N), 'decor',
                    lm='dynamic')
        xs = (spread(lo, lo + half, 8) + spread(hi - half, hi, 8)) if closed else \
            (spread(lo, lo + stack, 5) + spread(hi - stack, hi, 5))
        mb = mo.MB()
        for x in xs:                                                 # eyelets hang on the pole: centre 5 mm below its axis
            mb.tube([(x, YN - sd + .022 * math.cos(t), fz + zp - .005 + .022 * math.sin(t))
                     for t in (math.tau * k / 12 for k in range(12))], .0045, 'silver_satin', n=6, closed=True,
                    up=(1, 0, 0))
        rings = add(mb.finish(nm + '.rings'), 'decor', lm='dynamic')
        IX.tag_many([cloth, rings], 'show', g='study.curtain', when=state, fx='none')


def curtain_pole(xc, y, z):
    """Mid-brown wooden pole 1.88 long overall: 30 mm bar 1.80 long, two ball finials 40 mm long (32 mm ball), two
    wall brackets with rosettes 0.81 either side of the centre, outside the reveals (x 0.48 / 2.03). Axis at (y, z),
    centred on x xc."""
    mb, wood, r = mo.MB(), M.solid('study_pole', POLE, .45), .015
    mb.tube([(xc - .90, y, z), (xc + .90, y, z)], r, wood, n=12)
    for sx in (-1, 1):
        mb.at(T(xc + sx * .90, y, z) @ S.aim((sx, 0, 0)))            # collar, neck and ball: 0.040 long
        mb.lathe([(0, 0), (.0175, 0), (.0175, .004), (.009, .007)] +
                 [(.016 * math.sin(math.pi * k / 7), .024 - .016 * math.cos(math.pi * k / 7)) for k in range(1, 8)],
                 wood, 12)
        x = xc + sx * .81
        mb.at(T(x, YN, z - .02) @ S.aim((0, -1, 0)))                 # rosette on the wall
        mb.lathe([(0, 0), (.022, 0), (.021, .004), (.012, .007), (0, .008)], wood, 12)
        mb.at()
        mb.tube([(x, YN - .007, z - .02), (x, y, z - .02)], .006, wood, n=8)                    # arm
        mb.box((x - .008, y - r, z - r - .012), (x + .008, y + r, z - r), wood, bev=.002)      # cradle
    return mb.finish('study.curtain.pole')


# ----------------------------------------------------------------------------- glazed bookcase under the TV
def bookcase(add, on, fz, W):
    """Dark mahogany glazed bookcase 1.02 x 0.33 x 0.90, y 15.00..16.02 (v13 t142 / t193.4): plinth with a small
    moulding, lined carcass with two shelves of books, an overhanging top with a rounded front edge and a bead under
    it, two glazed doors (one pane each) hinged on their outer stiles with brass butts, a brass catch and keyhole at
    the meeting stiles."""
    xb = XW + .02                                                  # back clear of the 20 mm skirting
    mh, y0, y1, xf = 'mahogany_dark', 15.00, 16.02, xb + .30
    yc, H = (y0 + y1) / 2, .90
    add(on(P.cabinet_carcass(1.02, .30, H - .03, mh, plinth=.07, plinth_recess=.0, open_front=True, shelves=2,
                             name='study.bookcase'), xb, yc, 0, face=W), 'furn', 'bookcase')
    mb = mo.MB()
    mb.box((xb, y0 - .022, fz + H - .024), (xf + .024, y1 + .022, fz + H), mh, bev=.009, grain=1)       # top
    mb.box((xb, y0 - .009, fz + H - .036), (xf + .009, y1 + .009, fz + H - .024), mh, bev=.004, grain=1)  # bead
    mb.box((xb, y0 - .006, fz), (xf + .006, y1 + .006, fz + .012), mh, bev=.003, grain=1)          # plinth foot
    mb.box((xb, y0 - .004, fz + .058), (xf + .004, y1 + .004, fz + .07), mh, bev=.003, grain=1)   # plinth moulding
    for y in (y0 + .002, y1 - .002):                                # brass butts on the outer stiles
        for z in (.16, .70):
            mb.box((xf - .004, y - .004, fz + z), (xf + .003, y + .004, fz + z + .05), 'brass')
    add(mb.finish('study.bookcase.top'), 'furn')
    for k, z in enumerate((.089, .353, .607)):                      # on the bottom panel and the shelf tops
        add(on(P.book_row(.94, .20 - .02 * (k == 1), .16, seed=11 + k, fill=.97 - .12 * k, name='study.books.%d' % k),
               xb + .012, yc, z, face=W), 'decor')

    z0, z1, st = fz + .073, fz + H - .043, .045
    doors = []
    for tag, ya, yb, hinge, deg in (('s', y0 + .002, yc - .001, y0 + .002, -95), ('n', yc + .001, y1 - .002, y1 - .002, 90)):
        mb = mo.MB()
        for a, b in ((ya, ya + st), (yb - st, yb)):
            mb.box((xf - .02, a, z0), (xf, b, z1), mh, bev=.002, grain=2)
        for a, b in ((z0, z0 + st), (z1 - st, z1)):
            mb.box((xf - .02, ya + st, a), (xf, yb - st, b), mh, bev=.002, grain=1)
        for a, b in ((ya + st, ya + st + .008), (yb - st - .008, yb - st)):        # glazing bead
            mb.box((xf - .006, a, z0 + st), (xf + .002, b, z1 - st), mh, bev=.002)
        for a, b in ((z0 + st, z0 + st + .008), (z1 - st - .008, z1 - st)):
            mb.box((xf - .006, ya + st, a), (xf + .002, yb - st, b), mh, bev=.002)
        ym = (yb - .022) if tag == 's' else (ya + .022)                              # meeting stile
        mb.at(T(xf, ym, fz + .48) @ S.aim((1, 0, 0)))
        mb.lathe([(0, 0), (.006, 0), (.005, .008), (.011, .012), (.011, .018), (.006, .022), (0, .022)], 'brass', 10)
        mb.at()
        if tag == 'n':
            mb.box((xf, ym - .007, fz + .40), (xf + .0015, ym + .007, fz + .43), 'brass')    # key escutcheon
            mb.box((xf, ym - .016, fz + .52), (xf + .006, ym - .004, fz + .55), 'brass', bev=.001)   # catch
        door = mb.finish('study.bookcase.door.' + tag)
        gb = mo.MB()
        gb.face([(xf - .01, ya + st - .004, z0 + st - .004), (xf - .01, yb - st + .004, z0 + st - .004),
                 (xf - .01, yb - st + .004, z1 - st + .004), (xf - .01, ya + st - .004, z1 - st + .004)], 'glass_clear',
                hint=(1, 0, 0))
        glass = gb.finish('study.bookcase.door.%s.glass' % tag)
        kw = dict(g='study.bookcase.' + tag, label='Bookcase', p=(xf, hinge, fz), deg=deg)
        if tag == 'n':                                               # its open leaf lies across the drawers' run
            kw['excl'] = ['study.drawers.drawer.%d' % i for i in range(4)]
        IX.tag_many([door, glass], 'hinge', **kw)
        add(door, 'furn', lm='dynamic')
        add(glass, 'furn', lm='dynamic')

    add(on(S.flower_frame('study.flower_frame'), xb + .12, 15.80, H, face=W), 'decor')


# ----------------------------------------------------------------------------- white drawer pedestal
def drawer_unit(add, on, fz):
    """White pedestal on castors, 0.36 wide x 0.58 deep x 0.72, in front of the radiator with its narrow drawer face
    to the SOUTH, toward the bookcase (v13 t127 / t142 / t193.4): three shallow drawers over a deep one, inset
    between the carcass sides, a finger slot above each front. Its W side lines up with the bookcase front (t127),
    so the drawers run out clear of the bookcase."""
    x0, x1, y0, y1 = -0.31, 0.05, 16.08, 16.66                       # front y0; radiator tubes reach y 16.69
    zb, zt = .06, .72                                                # carcass on 60 mm castors
    add(on(P.cabinet_carcass(x1 - x0, y1 - y0, zt - zb, 'white_gloss', plinth=0, open_front=True, name='study.drawers'),
           (x0 + x1) / 2, y1, zb, face=(0, -1)), 'furn', 'chest')
    mb = mo.MB()
    for x in (x0 + .05, x1 - .05):
        for y in (y0 + .06, y1 - .05):
            mb.at(T(x, y, fz + .03) @ Matrix.Rotation(math.pi / 2, 4, 'Y'))
            mb.lathe([(0, -.008), (.026, -.008), (.028, 0), (.026, .008), (0, .008)], 'black_matt', 10)   # wheel
            mb.at()
            mb.box((x - .014, y - .02, fz + .04), (x + .014, y + .014, fz + .06), 'black_matt', bev=.003)  # fork
    add(mb.finish('study.drawers.castors'), 'furn')
    wh, gap, xa, xb = m('desk'), .015, x0 + .02, x1 - .02            # fronts inside the 18 mm sides, 2 mm reveal
    z = fz + zt - .018                                               # under the top panel
    for i, h in enumerate((.11, .11, .11, .232)):
        z -= gap + h
        mb = mo.MB()
        mb.box((xa, y0, z), (xb, y0 + .018, z + h), wh, bev=.002)                                  # front
        mb.box((xa + .006, y0 + .014, z + h - .004), (xb - .006, y0 + .02, z + h + gap - .002), 'black_matt')   # finger slot
        mb.box((xa + .008, y0 + .018, z + .008), (xb - .008, y1 - .03, z + .014), wh)               # tray
        for x in (xa + .008, xb - .014):
            mb.box((x, y0 + .018, z + .014), (x + .006, y1 - .03, z + h * .75), wh)
        mb.box((xa + .008, y1 - .036, z + .014), (xb - .008, y1 - .03, z + h * .75), wh)
        dr = mb.finish('study.drawers.drawer.%d' % i)
        IX.tag(dr, 'slide', label='Drawer', d=(0, -.20, 0), excl=['study.bookcase.n'])   # stops at y 15.88
        add(dr, 'furn', lm='dynamic')


# ----------------------------------------------------------------------------- desks, computers, desk lamp
def desks(ctx, add, on, fz):
    """Desk A 1.60 x 0.80, long axis N-S, 0.16 off the S wall (x 1.55..2.35, y 14.00..15.60, v13 t170 / t176); desk B
    1.20 x 0.70 on castors, long axis E-W, butting desk A's W edge in its N half (x 0.35..1.55, y 14.95..15.65). A PnP
    fit of t127 puts its W foot centre at 15.21..15.31; t129 shows the ring lamp on desk A's NW corner near desk B's NE
    corner; the survey's N-tied 15.08..15.78 and t128 lean further N, but a N edge past 15.65 closes the 0.50 lane
    between desk B and the drawer pedestal (0.52 here). The kneeling chair fits between it and the settee."""
    xa, ya = 1.95, 14.80
    add(on(S.desk('study.desk_a', 1.60, .80), xa, ya, 0, rot=90), 'furn', 'desk')
    add(on(S.desk('study.desk_b', 1.20, .70, H=.72, castors=True), 0.948, 15.30, 0), 'furn', 'desk')   # 2 mm off desk A
    mb, zt = mo.MB(), fz + .74
    S.hand_control(mb, T(xa + .388, ya + .52, zt - .025) @ RZ(90))  # under the NE front edge (t164)
    S.hand_control(mb, T(0.68, 14.962, fz + .72 - .025))           # desk B: under its S edge just E of the W leg (t128 / t129)
    B = T(1.93, 14.24, zt) @ facing(.35, .94)                       # curved ultrawide at the S end, facing N-NE (t171)
    S.riser(mb, B)
    S.monitor_curved(mb, B @ T(0, .02, .10))
    B = T(1.86, 15.24, zt) @ facing(.92, -.38)                      # flat 32-inch at the N end, screen to the chair (t176)
    S.riser(mb, B)
    S.monitor_flat(mb, B @ T(0, 0, .10))
    S.keyboard_mouse(mb, T(2.13, 14.70, zt) @ RZ(90))
    add(S.weld(mb.finish('study.computers')), 'furn')

    lamp, front = S.desk_lamp('study.desk_lamp')                    # gooseneck ring lamp at desk A's NW corner (t129)
    on(lamp, 1.66, 15.48, .74, face=(.8, -.6))                      # the ring turned to the chair
    IX.tag(lamp, 'lamp', label='Desk lamp')
    add(lamp, 'light')
    lighting.bulb(ctx, ROOM, tuple(lamp.matrix_basis @ front), watts=5, kelvin=3000, radius=.03, name='study.desk_lamp.bulb')


# ----------------------------------------------------------------------------- corner cabinet (SE corner)
def corner(add, on, fz):
    xo, yo = XE - .02, YS + .02                                    # back corner clear of the skirting on both walls
    Mw = Matrix(((-1, 0, 0, xo), (0, 1, 0, yo), (0, 0, 1, fz), (0, 0, 0, 1)))       # u along the S wall, v along the E wall
    cab, g = S.corner_cabinet('study.corner_cabinet', Mw, back=.02)
    add(cab, 'furn', 'cabinet')
    add(S.ornaments('study.corner_cabinet.ornaments', Mw), 'decor')

    w = lambda p: Vector((xo - p[0], yo + p[1]))                   # local plan point -> world
    c0, c1 = w(g['c0']), w(g['c1'])
    e = (c1 - c0).normalized()
    out = Vector((-e.y, e.x)) if Vector((-e.y, e.x)).dot(Vector((-1, 1))) > 0 else Vector((e.y, -e.x))   # into the room
    a, b = c0 + e * .0625, c1 - e * .0625                          # door between the front stiles
    mid = (a + b) / 2 - out * .02
    door = P.place(P.panel_door((b - a).length, .522, t=.02, stile=.07, mat='oak_door', name='study.corner_cabinet.door'),
                   (mid.x, mid.y, fz + .115), facing=tuple(out))
    kp = b - e * .04                                               # small pewter knob at the left of the door (t160)
    knob = P.place(P.handle_knob(.025, .025, finish=m('pewter'), name='study.corner_cabinet.knob'), (kp.x, kp.y, fz + .40),
                   facing=tuple(out))
    IX.tag_many([door, knob], 'hinge', g='study.corner_cabinet', label='Corner cabinet', p=(a.x, a.y, fz), deg=95)
    add(door, 'furn', lm='dynamic')
    add(knob, 'furn', lm='dynamic')


# ----------------------------------------------------------------------------- art and trophies
def wall_art(add, on, W, N, Sw):
    def pic(name, x, y, z, face, **kw):
        add(on(P.framed_picture(name='study.art.' + name, **kw), x, y, z, face=face), 'decor')

    # W wall (feature wall), y tied to the N wall (v4 f_0510, v13 t142 / t193.4)
    pic('cottage', XW, 14.33, 1.61, W, image=art('cottage'), w=.70, h=.58, frame_style='gilt_plain', frame_w=.03)
    add(on(S.black_frame('study.art.small', art('cat_grey')), XW, 15.165, 1.065, face=W), 'decor')
    add(on(S.cats_frame('study.art.cats', art('cats'), .30, .31), XW, 15.48, 1.063, face=W), 'decor')   # .908..1.218
    pic('cat', XW, 15.80, 1.06, W, image=art('cat'), w=.18, h=.18, frame_style='bronze_gold', frame_w=.058, depth=.03)
    pic('rooster', XW, 16.42, 1.54, W, image=art('rooster'), w=.34, h=.58, frame_style='champagne', frame_w=.045,
        depth=.06, glass=True)
    add(on(S.goose_trophy('study.goose_trophy'), XW, 14.49, 2.23, face=W), 'decor')
    add(on(S.antler_trophy('study.antler_trophy'), XW, 15.42, 2.156, face=W), 'decor')   # plaque 2.05.., tips 2.38
    # S wall (moved with it to y 13.84)
    pic('foliage', 2.05, YS, 1.80, Sw, image=art('foliage'), w=.52, h=.78, frame_style='walnut_gold', frame_w=.05, depth=.028)
    pic('green_small', 2.00, YS, 1.22, Sw, image=art('green_small'), w=.20, h=.25, frame_style='dark_gold_slip', frame_w=.045)
    add(on(S.octagon_frame('study.art.octagon', art('octagon')), 1.60, YS, 1.42, face=Sw), 'decor')   # 1 cm clear of the foliage
    # N wall, east of the window: certificate over a whiteboard, both BLANK (privacy)
    add(on(S.certificate('study.certificate'), 2.55, YN, 1.85, face=N), 'decor')
    add(on(S.whiteboard('study.whiteboard'), 2.52, YN, 1.30, face=N), 'decor')

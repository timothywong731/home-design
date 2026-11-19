"""Furniture and ornaments of the study, as plain builders. Spec: spec/rooms/study.md (sections 5-7).

Everything returns unlinked objects at scale 1. Free-standing pieces: origin floor centre. Wall pieces follow the
props convention (wall plane y = 0, front = local -Y, +X to the viewer's right) and go on with P.place(..., facing=).
Builders taking (mb, B) draw into an existing mo.MB under the base matrix B."""
import math
import random

import bmesh
from mathutils import Matrix, Vector

from lib import materials as M, mouldings as mo, props as P

SOLID = {                                   # name: (hex, roughness) -> M.solid('study_<name>', ...)
    'desk': ('#F0EFEB', 0.45), 'burgundy': ('#4F2428', 0.92), 'gimp': ('#C8B463', 0.8), 'boxwood': ('#D9C08C', 0.45),
    'fabric': ('#1D1C1F', 0.95), 'ply': ('#DBC69B', 0.5), 'pad': ('#48484B', 0.95), 'ac_line': ('#A9A9A6', 0.5),
    'owl': ('#F2F0EA', 0.5), 'kestrel': ('#9A6B45', 0.7), 'slate_blue': ('#8E96A0', 0.7), 'bowl': ('#D6BE86', 0.55),
    'goose': ('#8F8873', 0.9), 'beak': ('#D49B7C', 0.6), 'bone': ('#E4DCC8', 0.6), 'antler': ('#B39C78', 0.7),
    'petal': ('#E2C34B', 0.8), 'petal_pale': ('#EBDDA6', 0.8), 'card': ('#EFE8D6', 0.9), 'panel': ('#B9B1A3', 0.9),
    'stake': ('#C9B37A', 0.7), 'remote_screen': ('#8D9794', 0.3),
}


def m(key):
    """Material: a SOLID name, a props extra (walnut, leaf_green, terracotta ...) or a library key."""
    if key in SOLID:
        return M.solid('study_' + key, *SOLID[key])
    try:
        return M.mat(key)
    except KeyError:
        return P.mat(key)


def T(x=0.0, y=0.0, z=0.0):
    return Matrix.Translation((x, y, z))


def RX(deg):
    return Matrix.Rotation(math.radians(deg), 4, 'X')


def RZ(deg):
    return Matrix.Rotation(math.radians(deg), 4, 'Z')


def aim(d):
    """Rotation taking local +Z to the direction d."""
    return Vector((0, 0, 1)).rotation_difference(Vector(d).normalized()).to_matrix().to_4x4()


def facing(nx, ny):
    """Rotation about Z turning local -Y (the front) to the plan direction (nx, ny), as P.place does."""
    return Matrix.Rotation(math.atan2(nx, -ny), 4, 'Z')


def rrect(w, d, r, n=4):
    """Rounded rectangle w x d centred on the origin, counter-clockwise [(x, y)]."""
    out = []
    for cx, cy, a0 in ((w / 2 - r, d / 2 - r, 0), (-w / 2 + r, d / 2 - r, 90), (-w / 2 + r, -d / 2 + r, 180),
                       (w / 2 - r, -d / 2 + r, 270)):
        out += [(cx + r * math.cos(math.radians(a0 + 90 * i / n)), cy + r * math.sin(math.radians(a0 + 90 * i / n)))
                for i in range(n + 1)]
    return out


def ball(mb, B, r, mat, segs=8, squash=1.0):
    """Sphere (or ellipsoid, z scaled by squash) centred on the origin of B."""
    mb.at(B)
    mb.lathe([(r * math.sin(math.pi * k / 6), -r * squash * math.cos(math.pi * k / 6)) for k in range(7)], mat, segs)
    mb.at()


def weld(ob, deg=35.0):
    """Merge the coincident vertices of faces added one by one (curved screens), then re-mark the sharp edges."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.set_sharp_from_angle(angle=math.radians(deg))
    return ob


def strip(mb, path, t, w, mat, up):
    """Flat bar t thick (in the plane of the path) x w wide (along `up`, the normal of that plane)."""
    prof = [(-t / 2, -w / 2), (t / 2, -w / 2), (t / 2, w / 2), (-t / 2, w / 2)]
    mb.sweep(prof + prof[:1], path, mat, up=up)


# ----------------------------------------------------------------------------- frames (wall convention)
def frame_ring(mb, pts, fw, fd, mat):
    """Moulded frame along the outline pts [(x, z)] (counter-clockwise seen from the room), fw wide, fd deep."""
    prof = [(0, 0), (fw, 0), (fw, fd * .55), (fw * .55, fd), (0, fd * .8)]
    mb.sweep(prof + prof[:1], [(x, 0, z) for x, z in pts], mat, closed=True, up=(0, -1, 0))


def rect(w, h, cx=0.0, cz=0.0):
    return [(cx - w / 2, cz - h / 2), (cx + w / 2, cz - h / 2), (cx + w / 2, cz + h / 2), (cx - w / 2, cz + h / 2)]


def flat(mb, pts, y, mat):
    mb.face([(x, y, z) for x, z in pts], mat, hint=(0, -1, 0))


def picture(mb, pts, y, name, path):
    """Image filling the bounding box of pts [(x, z)] once, upright, on the plane y."""
    xs, zs = [p[0] for p in pts], [p[1] for p in pts]
    mat = M.image_mat('study_art_' + name, path, size_m=(max(xs) - min(xs), max(zs) - min(zs)), roughness=0.6)
    mb.face([(x, y, z) for x, z in pts], mat, hint=(0, -1, 0), off=(-min(xs), -min(zs)))


def certificate(name):
    """N1, BLANK: gold frame, burgundy mount, one cream card, one neutral panel, small brass plate. No text."""
    mb = mo.MB()
    frame_ring(mb, rect(.55, .45), .04, .025, 'gilt')
    flat(mb, rect(.48, .38), -.008, m('burgundy'))
    flat(mb, rect(.17, .25, -.115, .025), -.009, m('card'))
    flat(mb, rect(.17, .22, .105, .03), -.009, m('panel'))
    flat(mb, rect(.11, .022, 0, -.145), -.009, 'brass')
    return mb.finish(name)


def whiteboard(name):
    """N2, BLANK: frameless white board with a small clip at the top."""
    mb = mo.MB()
    mb.box((-.30, -.012, -.225), (.30, 0, .225), 'white_gloss', bev=.004)
    mb.box((-.035, -.024, .20), (.035, -.012, .235), 'black_matt', bev=.003)
    return mb.finish(name)


def octagon_frame(name, path):
    """S3: dark walnut octagonal frame 0.36 x 0.47 round a cream ground with a pressed leaf spray."""
    def oct_(w, h, c):
        return [(-w / 2 + c, -h / 2), (w / 2 - c, -h / 2), (w / 2, -h / 2 + c), (w / 2, h / 2 - c), (w / 2 - c, h / 2),
                (-w / 2 + c, h / 2), (-w / 2, h / 2 - c), (-w / 2, -h / 2 + c)]
    mb = mo.MB()
    frame_ring(mb, oct_(.36, .47, .10), .05, .03, m('walnut'))
    frame_ring(mb, oct_(.27, .38, .075), .006, .012, 'gilt')
    picture(mb, oct_(.262, .372, .073), -.006, 'octagon', path)
    return mb.finish(name)


def cats_frame(name, path):
    """W5: gold frame with a rope inner bead, burgundy mount, the two-cats picture (cats only)."""
    mb = mo.MB()
    frame_ring(mb, rect(.28, .34), .042, .026, 'gilt')
    frame_ring(mb, rect(.20, .26), .009, .016, 'gilt_bright')
    flat(mb, rect(.19, .25), -.006, m('burgundy'))
    flat(mb, rect(.172, .124, 0, .012), -.007, m('card'))
    picture(mb, rect(.16, .112, 0, .012), -.008, 'cats', path)
    return mb.finish(name)


def flower_frame(name):
    """Brass-edged glass floating frame with pressed yellow flowers, standing (leans back 8 degrees). Origin: foot."""
    mb = mo.MB()
    mb.at(RX(-8))
    frame_ring(mb, rect(.15, .20, 0, .10), .006, .006, 'brass')
    flat(mb, rect(.14, .19, 0, .10), -.002, 'glass_clear')
    rnd = random.Random(4)
    for i, (x, z, r) in enumerate(((-.02, .09, .028), (.03, .12, .024), (0, .15, .02), (.035, .07, .018), (-.035, .13, .016))):
        a0 = rnd.uniform(0, 1)
        flat(mb, [(x + r * math.cos(a0 + math.tau * k / 9), z + r * math.sin(a0 + math.tau * k / 9)) for k in range(9)],
             -.003 - .0003 * i, m('petal' if i % 2 == 0 else 'petal_pale'))
    mb.at()
    mb.box((-.02, .0, 0), (.02, .05, .004), 'brass')
    return mb.finish(name)


# ----------------------------------------------------------------------------- trophies (wall convention)
def goose_trophy(name):
    """W2: two greylag heads, necks and breasts side by side on a dark shaped shield, 0.36 x 0.30, 0.25 off the wall;
    the heads turned to each other, a folded wing behind the larger bird."""
    mb = mo.MB()
    g = m('goose')
    mb.prism([(.18 * math.cos(math.tau * k / 16), 0, -.05 + .10 * math.sin(math.tau * k / 16)) for k in range(16)],
             (0, -.02, 0), 'dark_oak_antique')
    for sx, s in ((-1, .85), (1, 1.0)):
        c = Vector((sx * .085, -.10, -.035))
        head = Vector((sx * .055, -.17, .125 * s))
        ball(mb, T(*c), .082 * s, g, squash=1.15)                               # breast
        mb.tube([c + Vector((0, -.03, .05 * s)), Vector((sx * .085, -.16, .075 * s)), head], .034 * s, g, n=8)
        ball(mb, T(*head), .04 * s, g)
        mb.at(T(*head) @ aim((-sx, -.25, -.3)))                                 # beaks turned to each other
        mb.lathe([(0, .02), (.017, .03), (.012, .06), (0, .085)], m('beak'), 8)
        mb.at()
    mb.box((.10, -.07, -.03), (.185, -.02, .11), g, bev=.02)                    # folded wing
    return mb.finish(name)


def antler_trophy(name):
    """W3: roe skull cap with a pair of three-point antlers on a dark leaf-shaped plaque. Origin: plaque centre."""
    mb = mo.MB()
    leaf = [(0, -.14), (.045, -.09), (.06, -.02), (.05, .06), (.02, .11), (0, .12), (-.02, .11), (-.05, .06), (-.06, -.02),
            (-.045, -.09)]
    mb.prism([(x, 0, z) for x, z in leaf], (0, -.018, 0), 'dark_oak_antique')
    mb.at(T(0, -.018, .02) @ RX(90))
    mb.dome(.034, .055, .04, m('bone'))
    mb.at()
    mb.box((-.012, -.045, -.09), (.012, -.018, -.03), m('bone'), bev=.006)      # nasal bones
    a = m('antler')
    for sx in (-1, 1):
        beam = [(sx * .02, -.04, .06), (sx * .04, -.055, .14), (sx * .06, -.045, .22), (sx * .055, -.03, .30)]
        mb.tube(beam, .006, a, n=6)
        mb.tube([beam[1], (sx * .045, -.10, .19)], .0045, a, n=6)
        mb.tube([beam[2], (sx * .10, -.03, .27)], .0045, a, n=6)
    return mb.finish(name)


# ----------------------------------------------------------------------------- fixed fittings (wall convention)
def radiator(name, tubes=8, w=.44, h=1.80, gap=.09):
    """White vertical column radiator: one row of round-ended oval tubes, chrome valves at both bottom corners.
    Origin: wall, bottom centre of the tubes."""
    mb = mo.MB()
    pitch = w / tubes
    r, yc = pitch * .41, -gap - .035
    for i in range(tubes):
        mb.at(T((i - (tubes - 1) / 2) * pitch, yc, 0))
        mb.lathe([(0, 0), (r * .6, .006), (r, .03), (r, h - .03), (r * .6, h - .006), (0, h)], 'white_gloss', 10,
                 ell=(1, 1.55))
    mb.at()
    for z in (.25, h - .25):
        mb.box((-w / 2 + .03, yc + .01, z), (w / 2 - .03, yc + .03, z + .03), 'white_gloss')
        for x in (-.12, .12):
            mb.box((x - .012, yc + .03, z), (x + .012, 0, z + .03), 'white_gloss')
    for sx in (-1, 1):
        x = sx * (w / 2 - pitch / 2)
        mb.tube([(x, yc, .0), (x, yc, -.05), (x, 0, -.05)], .008, 'chrome', n=8, up=(1, 0, 0))
        mb.at(T(x, yc, -.05) @ aim((sx, 0, 0)))
        mb.lathe([(0, 0), (.013, 0), (.013, .03), (.02, .032), (.02, .075), (0, .075)],
                 'white_gloss' if sx > 0 else 'chrome', 10)                      # TRV head at the east, lockshield west
        mb.at()
    return mb.finish(name)


def aircon(name, w=.88, h=.30, d=.22):
    """White split indoor unit: rounded front, louvre line along the bottom, indicator at the lower right.
    Origin: wall, bottom centre."""
    mb = mo.MB()
    side = [(0, .02), (.68 * d, 0), (.93 * d, .13 * h), (d, .40 * h), (.98 * d, .80 * h), (.82 * d, .985 * h), (0, h)]
    mb.prism([(-w / 2, -y, z) for y, z in side], (w, 0, 0), 'plastic_white')
    mb.box((-w / 2 + .012, -.945 * d, .15 * h), (w / 2 - .012, -.90 * d, .15 * h + .004), m('ac_line'))
    mb.box((w / 2 - .11, -d - .0015, .24 * h), (w / 2 - .07, -d + .01, .24 * h + .014), m('ac_line'))
    return mb.finish(name)


def remote_cradle(name):
    """White wall cradle holding the a/c remote. Origin: wall, bottom centre of the cradle."""
    mb = mo.MB()
    mb.box((-.03, -.022, 0), (.03, 0, .10), 'plastic_white', bev=.003)
    mb.box((-.023, -.034, .03), (.023, -.014, .19), 'plastic_white', bev=.004)
    mb.box((-.016, -.0345, .13), (.016, -.034, .175), m('remote_screen'))
    return mb.finish(name)


def outlet_plate(name):
    """White single-gang 86 x 86 plate with a small round outlet in the centre (coax / cable outlet). Origin: wall,
    plate centre."""
    mb = mo.MB()
    mb.box((-.043, -.009, -.043), (.043, 0, .043), 'plastic_white', bev=.003)
    mb.at(T(0, -.009, 0) @ RX(90))
    mb.lathe([(0, 0), (.0085, 0), (.0075, .006), (.0045, .0065), (.0045, .004), (0, .004)], 'plastic_white', 12)
    mb.at()
    mb.face([(-.0018, -.0137, -.0018), (.0018, -.0137, -.0018), (.0018, -.0137, .0018), (-.0018, -.0137, .0018)],
            m('plastic_dark'), hint=(0, -1, 0))
    return mb.finish(name)


def detector(name):
    """Round white ceiling detector, dia 0.12. Origin: ceiling."""
    mb = mo.MB()
    mb.lathe([(0, -.035), (.04, -.035), (.06, -.015), (.06, 0)], 'plastic_white', 16)
    return mb.finish(name)


# ----------------------------------------------------------------------------- desks and what stands on them
def desk(name, L, W, H=.74):
    """White sit-stand table: 25 mm top with rounded corners, two columns on T-feet 0.70 long. Long axis = X."""
    mb = mo.MB()
    w = m('desk')
    mb.prism([(x, y, H - .025) for x, y in rrect(L, W, .06)], (0, 0, .025), w)
    for sx in (-1, 1):
        x = sx * (L / 2 - .16)
        mb.box((x - .035, -.35, 0), (x + .035, .35, .028), w, bev=.008)
        mb.box((x - .04, -.03, .028), (x + .04, .03, .40), w, bev=.003)
        mb.box((x - .032, -.023, .40), (x + .032, .023, H - .045), w, bev=.003)
        mb.box((x - .05, -W / 2 + .08, H - .045), (x + .05, W / 2 - .08, H - .025), w)
    mb.box((-L / 2 + .16, -.04, H - .065), (L / 2 - .16, .04, H - .025), w)
    mb.box((L / 2 - .44, -W / 2 + .01, H - .045), (L / 2 - .30, -W / 2 + .07, H - .025), 'black_matt')   # hand control
    return mb.finish(name)


def riser(mb, B, w=.55, d=.22, h=.10):
    """Pale bentwood monitor riser. Origin: desk top, centre."""
    p = m('ply')
    mb.at(B)
    mb.box((-w / 2, -d / 2, h - .012), (w / 2, d / 2, h), p, bev=.003)
    for sx in (-1, 1):
        mb.box((sx * w / 2, -d / 2, 0), (sx * (w / 2 - .012), d / 2, h - .004), p, bev=.003)
    mb.at()


def monitor_curved(mb, B, w=.82, h=.37, R=1.5, z0=.105):
    """34-inch curved ultrawide, blank. Origin: centre of its foot; screen faces -Y, its lower edge at z0."""
    n, half, t = 8, w / 2 / R, .022
    k = 'black_matt'
    mb.at(B)
    col = [(R * math.sin(a), -R * (1 - math.cos(a))) for a in (-half + 2 * half * i / n for i in range(n + 1))]
    for (xa, ya), (xb, yb) in zip(col, col[1:]):
        f = [(xa, ya, z0), (xb, yb, z0), (xb, yb, z0 + h), (xa, ya, z0 + h)]
        bk = [(x, y + t, z) for x, y, z in f]
        mb.face([(x, y - .0008, z) for x, y, z in f], 'screen_black', hint=(0, -1, 0))
        mb.face(bk, k, hint=(0, 1, 0))
        mb.face([f[0], f[1], bk[1], bk[0]], k, hint=(0, 0, -1))
        mb.face([f[3], f[2], bk[2], bk[3]], k, hint=(0, 0, 1))
    for sx, (x, y) in ((-1, col[0]), (1, col[-1])):
        mb.face([(x, y - .0008, z0), (x, y + t, z0), (x, y + t, z0 + h), (x, y - .0008, z0 + h)], k, hint=(sx, 0, 0))
    mb.box((-.03, t, .008), (.03, t + .03, z0 + .20), k, bev=.004)                 # neck
    mb.box((-.13, -.08, 0), (.13, .09, .008), k, bev=.003)                         # foot plate
    mb.at()


def monitor_flat(mb, B, w=.72, h=.42, z0=.09):
    """32-inch flat monitor with a silver edge on a T-foot, blank. Origin: centre of its foot; screen faces -Y."""
    mb.at(B)
    mb.box((-w / 2, 0, z0), (w / 2, .018, z0 + h), 'silver_satin', bev=.002)
    mb.face([(-w / 2 + .007, -.0008, z0 + .007), (w / 2 - .007, -.0008, z0 + .007), (w / 2 - .007, -.0008, z0 + h - .007),
             (-w / 2 + .007, -.0008, z0 + h - .007)], 'screen_black', hint=(0, -1, 0))
    mb.box((-w / 2 + .02, .018, z0 + .02), (w / 2 - .02, .04, z0 + h - .02), 'black_matt', bev=.008)
    mb.box((-.03, .04, .01), (.03, .058, z0 + .22), 'black_matt', bev=.004)
    mb.box((-.26, -.03, 0), (.26, .0, .012), 'silver_satin', bev=.003)
    mb.box((-.03, 0, 0), (.03, .16, .012), 'silver_satin', bev=.003)
    mb.at()


def keyboard_mouse(mb, B):
    """Black keyboard (long axis X, origin its centre) and a mouse 0.30 to its +X end."""
    mb.at(B)
    mb.box((-.22, -.065, 0), (.22, .065, .016), 'black_matt', bev=.004)
    mb.at(B @ T(.34, .0, 0))
    mb.dome(.032, .052, .034, 'black_matt', segs=10)
    mb.at()


def desk_lamp(name):
    """Small black LED desk lamp; the head reaches toward local -Y. -> (object, local point under the head)."""
    mb = mo.MB()
    k = 'black_matt'
    mb.lathe([(0, 0), (.07, 0), (.07, .012), (.02, .016), (0, .016)], k, 16)
    mb.tube([(0, 0, .016), (0, 0, .26), (0, -.04, .36), (0, -.13, .40)], .006, k, n=8, up=(1, 0, 0))
    mb.box((-.03, -.27, .39), (.03, -.11, .405), k, bev=.004)
    mb.face([(-.024, -.26, .3895), (.024, -.26, .3895), (.024, -.12, .3895), (-.024, -.12, .3895)],
            P.emissive('#F4CB94', 6.0), hint=(0, 0, -1))
    return mb.finish(name), Vector((0, -.19, .35))


# ----------------------------------------------------------------------------- seating
def office_chair(name):
    """Black fabric gaming chair, 0.66 x 0.66 x 1.27: winged back with integral headrest, bucket seat, armrests,
    five-star base on castors. Faces local -Y."""
    mb = mo.MB()
    f, k = m('fabric'), 'black_matt'
    for i in range(5):
        B = RZ(72 * i + 18)
        mb.at(B)
        mb.box((.02, -.022, .055), (.32, .022, .09), k, bev=.006)
        mb.at(B @ T(.30, 0, 0))
        mb.box((-.028, -.02, 0), (.028, .02, .055), k, bev=.012)
    mb.at()
    mb.lathe([(0, .05), (.045, .05), (.045, .10), (.028, .12), (.028, .37), (0, .37)], k, 12)
    mb.box((-.13, -.13, .37), (.13, .13, .41), k, bev=.006)
    mb.box((-.25, -.27, .41), (.25, .23, .51), f, bev=.035)                        # seat
    for sx in (-1, 1):
        mb.box((sx * .19, -.27, .45), (sx * .27, .20, .545), f, bev=.03)           # side bolsters
        mb.box((sx * .285, -.03, .43), (sx * .325, .03, .66), k, bev=.006)         # arm post
        mb.box((sx * .26, -.17, .66), (sx * .35, .10, .69), k, bev=.012)           # arm pad
    mb.box((-.32, -.025, .42), (.32, .025, .445), k)
    mb.at(T(0, .20, .47) @ RX(-10))                                               # back, leaning 10 degrees
    half = [(x, .95 * z) for x, z in ((.20, 0), (.25, .07), (.26, .22), (.215, .32), (.235, .42), (.28, .53), (.27, .61),
            (.19, .665), (.155, .70), (.165, .78), (.145, .83), (.08, .85))]    # racing-seat outline (v4:f_0486)
    # ponytail: overall height kept under 1.30 so the walk layer treats the chair as soft (geom.js SMALL)
    sil = half + [(-x, z) for x, z in half[::-1]]
    mb.prism([(x, 0, z) for x, z in sil], (0, .085, 0), f)                         # shell
    mb.prism([(x * .82, -.035, .03 + z * .94) for x, z in sil], (0, .035, 0), f)   # padded front
    for sx in (-1, 1):
        mb.box((sx * .20, -.065, .34), (sx * .275, 0, .60), f, bev=.025)          # shoulder wings
        mb.box((sx * .19, -.055, .04), (sx * .255, 0, .26), f, bev=.022)          # lumbar wings
        mb.box((sx * .045 - .018, -.0362, .70), (sx * .045 + .018, -.0345, .75), k)   # harness slots
    mb.at()
    return mb.finish(name)


def kneeling_chair(name):
    """Bentwood rocker kneeling chair 0.46 x 0.72 x 0.55: two plywood runners, grey seat and knee pads.
    The sitter faces local +Y."""
    mb = mo.MB()
    ply, pad = m('ply'), m('pad')
    side = [(-.16, .47), (-.33, .36), (-.36, .18), (-.28, .035), (0, .012), (.26, .035), (.36, .12), (.33, .24), (.20, .30)]
    for sx in (-1, 1):
        strip(mb, [(sx * .19, y, z) for y, z in side], .022, .06, ply, (1, 0, 0))
    mb.box((-.19, -.20, .445), (.19, -.13, .47), ply)
    mb.box((-.19, .20, .275), (.19, .27, .30), ply)
    mb.at(T(0, -.18, .47) @ RX(-10))
    mb.box((-.20, -.15, 0), (.20, .15, .07), pad, bev=.025)
    mb.at(T(0, .25, .29) @ RX(25))
    mb.box((-.20, -.10, 0), (.20, .10, .06), pad, bev=.022)
    mb.at()
    return mb.finish(name)


def settee(name):
    """Edwardian inlaid mahogany two-seat salon settee 1.05 x 0.52 x 0.93, seat 0.43, burgundy with gold gimp.
    Origin: floor, centre of the back; the wall is y = 0, the front faces local +Y. The stuffed seat is a child."""
    mb = mo.MB()
    mh, bg, gp, bx = 'mahogany_dark', m('burgundy'), m('gimp'), m('boxwood')
    D, xl = .52, .485                                               # depth, leg centres
    yb0, yb1 = .015, .045                                           # back frame
    yf = D - .034                                                   # front leg centre

    def top(x):                                                     # serpentine top rail: ears, dips, central crest
        t = min(1.0, abs(x) / (xl + .04))
        return .895 - .035 * math.sin(math.pi * t) - .015 * t

    for sx in (-1, 1):
        x = sx * xl
        mb.box((x - .016, yb0, 0), (x + .016, yb1 + .005, top(x) - .02), mh, bev=.004)   # back leg + stile
        mb.box((x - .016, yf - .016, 0), (x + .016, yf + .016, .37), mh, bev=.004)       # front leg
        mb.box((x - .019, yf - .014, 0), (x + .019, yf + .022, .03), mh, bev=.006)       # toe
        mb.box((x - .014, yb1, .31), (x + .014, yf - .016, .37), mh)                     # side seat rail
        mb.tube([(x, yb1, .13), (x, yf - .016, .13)], .009, mh, n=8)                     # side stretcher
        mb.box((x - .0015, yf + .0162, .05), (x + .0015, yf + .0168, .30), bx)           # stringing on the leg
        strip(mb, [(x, yb1, .635), (x, .28, .625), (x, .44, .60), (x, D, .565)], .018, .05, mh, (1, 0, 0))   # arm
        strip(mb, [(x, yf, .37), (x, yf - .07, .44), (x, yf - .085, .52), (x, yf - .03, .595)], .02, .028, mh, (1, 0, 0))
    mb.tube([(-xl, D / 2, .13), (xl, D / 2, .13)], .009, mh, n=8)                        # cross stretcher
    mb.box((-xl, yf - .016, .31), (xl, yf + .016, .37), mh, bev=.003)                    # front seat rail
    mb.box((-xl, yb0, .31), (xl, yb1, .37), mh)
    mb.box((-xl, yb0 + .003, .47), (xl, yb1 - .003, .50), mh, bev=.003)                  # lower back rail
    mb.box((-xl, yf + .0162, .335), (xl, yf + .0168, .338), bx)

    n = 20                                                                                # shaped top board
    xs = [-xl - .04 + (2 * xl + .08) * i / n for i in range(n + 1)]
    for xa, xb in zip(xs, xs[1:]):
        mb.prism([(xa, yb0, top(xa) - .10), (xb, yb0, top(xb) - .10), (xb, yb0, top(xb)), (xa, yb0, top(xa))],
                 (0, yb1 - yb0, 0), mh)
        mb.face([(xa, yb1 + .0006, top(xa) - .012), (xb, yb1 + .0006, top(xb) - .012), (xb, yb1 + .0006, top(xb) - .009),
                 (xa, yb1 + .0006, top(xa) - .009)], bx, hint=(0, 1, 0))                  # stringing under the top edge
    fan = [(.05 * math.cos(math.pi * k / 8), .05 * math.sin(math.pi * k / 8)) for k in range(9)]
    mb.prism([(x, yb0 - .002, top(0) - .012 + z) for x, z in fan], (0, yb1 - yb0 + .006, 0), mh)      # crest
    for k in range(1, 8, 2):
        a = math.pi * k / 8
        mb.face([(0, yb1 + .0046, top(0) - .01), (.045 * math.cos(a - .09), yb1 + .0046, top(0) - .012 + .045 * math.sin(a - .09)),
                 (.045 * math.cos(a + .09), yb1 + .0046, top(0) - .012 + .045 * math.sin(a + .09))], bx, hint=(0, 1, 0))

    yp = yb1 + .012                                                                       # front of the pads
    for sx in (-1, 1):                                    # hr_v4_543: tall pads with a shaped top, slim pads in the rail
        ts = [sx * (.085 + .37 * i / 8) for i in range(9)]                                # main pad, top follows the rail
        low, high = [(sx * .035, .515), (sx * .455, .515)], [(t, top(t) - .112) for t in ts]
        loop = low + high[::-1] if sx > 0 else low[::-1] + high
        mb.prism([(x, yb0 + .004, z) for x, z in loop], (0, yp - yb0 - .004, 0), bg)
        mb.tube([(x, yp, z) for x, z in loop], .005, gp, n=6, closed=True, up=(0, 1, 0))
        ts = [sx * (.05 + .385 * i / 8) for i in range(9)]                                # slim pad in the top rail
        low = [(t, top(t) - .088) for t in ts]
        high = [(t, top(t) - .024) for t in ts]
        loop = low + high[::-1] if sx > 0 else low[::-1] + high
        mb.prism([(x, yb1, z) for x, z in loop], (0, .007, 0), bg)
        mb.tube([(x, yb1 + .007, z) for x, z in loop], .0045, gp, n=6, closed=True, up=(0, 1, 0))
    zs = top(0) - .10
    splat = [(-.07, zs), (-.022, .50), (.022, .50), (.07, zs)]
    mb.prism([(x, yb0 + .006, z) for x, z in splat], (0, .02, 0), mh)                     # waisted centre splat
    ys = yb0 + .0266                                                                      # inlay, 0.6 mm proud
    for pts in ([(-.024, .775), (.024, .775), (.013, .742), (0, .71), (-.013, .742)],     # urn
                [(-.003, .53), (.003, .53), (.003, .705), (-.003, .705)],                  # stem
                [(-.055, .787), (.055, .787), (.055, .790), (-.055, .790)]):
        mb.face([(x, ys, z) for x, z in pts], bx, hint=(0, 1, 0))
    for cx, cz, r in ((-.042, .77, .012), (.042, .77, .012), (0, .665, .009), (0, .625, .008), (0, .59, .007),
                      (0, .56, .006)):                                                    # scrolls, husks
        mb.face([(cx + r * math.cos(math.tau * k / 8), ys, cz + r * 1.3 * math.sin(math.tau * k / 8)) for k in range(8)], bx,
                hint=(0, 1, 0))
    ob = mb.finish(name)
    seat = P.upholstered_seat(2 * xl - .012, D - .05, .075, mat=bg, gimp=gp, name=name + '.seat')
    seat.parent = ob
    seat.location = (0, (yb1 + yf + .016) / 2, .362)
    return ob


# ----------------------------------------------------------------------------- plant
def plant(name, height=1.05):
    """Upright ficus-like shrub on a staked stem (hr_v4_559, f_0510): twigs spreading to about 0.45 m low down and
    0.2 m at the top, glossy rounded mid-green leaves, in a pale weathered terracotta pot (dia 0.30 x 0.27) on a saucer."""
    mb = mo.MB()
    tc, rnd, bark = M.solid('study_pot', '#B98C68', .85), random.Random(7), m('bark')
    mb.lathe([(0, 0), (.17, 0), (.18, .025), (.168, .025), (.162, .012), (0, .012)], tc, 20)
    mb.at(T(0, 0, .012))
    mb.lathe([(0, 0), (.115, 0), (.15, .25), (.158, .25), (.158, .27), (.14, .27), (.136, .243), (0, .243)], tc, 20)
    mb.at()
    mb.face([(.136 * math.cos(math.tau * k / 12), .136 * math.sin(math.tau * k / 12), .256) for k in range(12)], m('soil'),
            hint=(0, 0, 1))
    mb.tube([(0, 0, .25), (.012, 0, .60), (0, .01, height - .04)], .008, bark, n=6)
    mb.tube([(.02, .01, .25), (.02, .01, height - .02)], .004, m('stake'), n=5)
    lg, lm = P.two_sided(m('leaf_green')), P.two_sided(m('leaf_mid'))
    count = [0]

    def leaf(p, az, tilt):                                          # leaf along the plan direction az (deg), tilted up
        s, count[0] = rnd.uniform(.9, 1.3), count[0] + 1
        mb.at(T(*p) @ RZ(az - 90 + rnd.uniform(-50, 50)) @ RX(tilt))
        for sx in (-1, 1):
            mb.face([(0, 0, 0), (0, .075 * s, 0), (sx * .025 * s, .052 * s, .006), (sx * .025 * s, .02 * s, .006)],
                    lg if count[0] % 3 == 0 else lm, hint=(0, 0, 1))
        mb.at()

    nb = 10
    for j in range(nb):                                             # side twigs, longest low down
        f = j / (nb - 1)
        z, L = .40 + (height - .55) * f, .21 - .13 * f
        az = j * 137.5 + rnd.uniform(-15, 15)
        d = Vector((math.cos(math.radians(az)), math.sin(math.radians(az)), 0))
        pts = [Vector((0, 0, z)), Vector((0, 0, z)) + d * L * .55 + Vector((0, 0, L * .3)), Vector((0, 0, z)) + d * L + Vector((0, 0, L * .5))]
        mb.tube(pts, .0035, bark, n=5)
        for t in (.3, .55, .75, .9, 1.0, 1.0):
            q = pts[0].lerp(pts[1], t / .5) if t <= .5 else pts[1].lerp(pts[2], (t - .5) / .5)
            leaf(q, az, rnd.uniform(10, 50))
    for i in range(24):                                             # leaves on the leader, crowded at the top
        z = .50 + (height - .52) * (i / 23) ** .6
        leaf((.01 * math.sin(i), .01 * math.cos(i), z), i * 137.5, rnd.uniform(30, 70))
    return mb.finish(name)


# ----------------------------------------------------------------------------- corner cabinet
def corner_cabinet(name, Mw, leg=.60):
    """Rustic light-oak two-part corner cabinet 1.82 high, its back corner at the origin of Mw: local u along one
    wall, v along the other (Mw may mirror). Lower cupboard 0.68 with a real interior, waist shelf, open upper part
    with two shelves, flat cornice. The door is NOT here (study.py hangs and tags it).
    -> (carcass object, dict of local plan points: c0, c1 = ends of the front, e = unit vector c0 -> c1)."""
    oak = 'oak_door'
    c0, c1 = (leg - .04, .12), (.12, leg - .04)
    ex, ey = -math.sqrt(.5), math.sqrt(.5)
    nx, ny = -math.sqrt(.5), -math.sqrt(.5)                          # from the front back into the corner
    plan = [(0, 0), (leg, 0), c0, c1, (0, leg)]

    def grow(d):
        return [(0, 0), (leg + d * .3, 0), (c0[0] + d, c0[1] + d * .6), (c1[0] + d * .6, c1[1] + d), (0, leg + d * .3)]

    def slab(pts, z0, z1, mat=oak):
        mb.prism([(u, v, z0) for u, v in pts], (0, 0, z1 - z0), mat)

    def stile(a, b, t, z0, z1):                                      # board from a to b (plan), t thick, set inward
        ux, uy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(ux, uy)
        px, py = -uy / L * t, ux / L * t                             # left of a -> b
        if px * (0.2 - a[0]) + py * (0.2 - a[1]) < 0:                # make it point to the inside of the cabinet
            px, py = -px, -py
        slab([a, b, (b[0] + px, b[1] + py), (a[0] + px, a[1] + py)], z0, z1)

    mb = mo.MB()
    mb.at(Mw)
    inner = [(.012, .012), (leg - .03, .012), (c0[0] - .02, c0[1] - .004), (c1[0] - .004, c1[1] - .02), (.012, leg - .03)]
    slab([(.02, .02), (leg - .06, .02), (c0[0] - .04, c0[1] - .03), (c1[0] - .03, c1[1] - .04), (.02, leg - .06)], 0, .08)   # plinth
    slab(plan, .08, .10)                                             # cupboard floor
    slab(inner, .37, .388)                                           # its shelf
    slab(grow(.03), .68, .71)                                        # waist shelf
    for z in (1.07, 1.42):                                           # two shelves = three compartments (hr_v4_501)
        slab(inner, z - .02, z)
    slab(plan, 1.77, 1.79)
    slab(grow(.035), 1.79, 1.82)                                     # cornice
    for z0, z1 in ((.10, .68), (.71, 1.77)):
        mb.box((0, 0, z0), (leg, .012, z1), oak, grain=2)            # back boards on the two walls
        mb.box((0, .012, z0), (.012, leg, z1), oak, grain=2)
        stile((leg, 0), c0, .018, z0, z1)                            # canted side stiles
        stile((0, leg), c1, .018, z0, z1)
        fw = .06 if z0 < .5 else .05                                 # front stiles
        stile(c0, (c0[0] + ex * fw, c0[1] + ey * fw), .02, z0, z1)
        stile(c1, (c1[0] - ex * fw, c1[1] - ey * fw), .02, z0, z1)
    a, b = (c0[0] + ex * .05, c0[1] + ey * .05), (c1[0] - ex * .05, c1[1] - ey * .05)
    stile(a, b, .02, 1.70, 1.77)                                     # top rail of the open part
    a, b = (c0[0] + ex * .06, c0[1] + ey * .06), (c1[0] - ex * .06, c1[1] - ey * .06)
    stile(a, b, .02, .10, .112)                                      # rails over and under the door
    stile(a, b, .02, .64, .68)
    return mb.finish(name), dict(c0=c0, c1=c1, e=(ex, ey), n=(nx, ny))


def ornaments(name, Mw):
    """Kept ornaments of the corner cabinet (local frame of Mw): turned wooden bowl on the top, white owl with
    spread wings on the upper shelf, kestrel on a round dark base on the lower one."""
    mb = mo.MB()
    dark = 'dark_oak_antique'
    mb.at(Mw @ T(.23, .23, 1.82))
    mb.lathe([(0, 0), (.065, 0), (.15, .13), (.142, .13), (.06, .012), (0, .012)], m('bowl'), 20)
    B = Mw @ T(.21, .21, 1.42) @ Matrix.Scale(1.35, 4)               # owl
    mb.at(B)
    mb.lathe([(0, 0), (.06, 0), (.06, .014), (0, .014)], dark, 14)
    ow = m('owl')
    ball(mb, B @ T(0, 0, .085), .04, ow, squash=1.6)
    ball(mb, B @ T(.012, .012, .16), .03, ow)
    wing = P.two_sided(ow)
    for sx in (-1, 1):
        mb.at(B @ T(0, 0, .10) @ RZ(-45) @ Vector((0, 1, 0)).rotation_difference(Vector((sx * .75, -.1, .65))).to_matrix().to_4x4())
        mb.leaf(.15, .075, .008, wing, segs=5, serrate=.25)
    B = Mw @ T(.22, .22, 1.07) @ Matrix.Scale(1.25, 4)               # kestrel
    mb.at(B)
    mb.lathe([(0, 0), (.055, 0), (.055, .018), (0, .018)], dark, 14)
    ke = m('kestrel')
    ball(mb, B @ T(0, 0, .11) @ RX(12), .03, ke, squash=2.2)
    ball(mb, B @ T(0, -.012, .19), .023, m('slate_blue'))
    mb.at(B @ T(0, .02, .03) @ RX(15))
    mb.box((-.014, 0, 0), (.014, .012, .09), m('slate_blue'), bev=.003)                   # tail
    mb.at()
    return mb.finish(name)

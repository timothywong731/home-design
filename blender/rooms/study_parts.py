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
    'stitch': ('#66201F', 0.85), 'beanbag': ('#93566B', 0.62), 'leather': ('#6B4A33', 0.55), 'key': ('#3A3B3E', 0.6),
    'pewter': ('#8E8F8A', 0.4), 'ac_dark': ('#2E3032', 0.4), 'glide': ('#2A2A2C', 0.6), 'button': ('#9A9CA0', 0.5),
}


def m(key):
    """Material: a SOLID name, a props extra (walnut, leaf_green, terracotta ...) or a library key."""
    if key == 'pewter':
        return M.solid('study_pewter', SOLID['pewter'][0], SOLID['pewter'][1], 0.9)
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


def loft(mb, secs, mat, caps=(True, True)):
    """Skin closed loops of equal length (lists of local 3D points) with quads, plus planar end caps. Faces are
    oriented away from the axis through the loop centroids; weld() the finished object for smooth shading."""
    cents = [sum((Vector(p) for p in sc), Vector()) / len(sc) for sc in secs]
    n = len(secs[0])
    for i in range(len(secs) - 1):
        a, b = secs[i], secs[i + 1]
        c = (cents[i] + cents[i + 1]) / 2
        for j in range(n):
            q = [a[j], a[(j + 1) % n], b[(j + 1) % n], b[j]]
            qc = sum((Vector(p) for p in q), Vector()) / 4
            mb.face(q, mat, hint=qc - c)
    if caps[0]:
        mb.face(secs[0], mat, hint=cents[0] - cents[1])
    if caps[1]:
        mb.face(secs[-1], mat, hint=cents[-1] - cents[-2])


def fan_cap(mb, ring, apex, mat):
    """Close a loop with triangles to one apex point (a crowned cushion top)."""
    n, apex = len(ring), Vector(apex)
    c = sum((Vector(p) for p in ring), Vector()) / n
    for j in range(n):
        tri = [Vector(ring[j]), Vector(ring[(j + 1) % n]), apex]
        mb.face(tri, mat, hint=apex - c + (sum(tri, Vector()) / 3 - c) * 0.01)


def beam(mb, p0, p1, w0, h0, w1, h1, mat, up=(0, 0, 1)):
    """Tapered rectangular bar from p0 (w0 x h0) to p1 (w1 x h1); w across, h along `up` (top/bottom faces)."""
    p0, p1, up = Vector(p0), Vector(p1), Vector(up)
    d = (p1 - p0).normalized()
    s = d.cross(up).normalized()
    u = s.cross(d).normalized()
    ring = lambda p, w, h: [p - s * w / 2 - u * h / 2, p + s * w / 2 - u * h / 2, p + s * w / 2 + u * h / 2,
                            p - s * w / 2 + u * h / 2]
    loft(mb, [ring(p0, w0, h0), ring(p1, w1, h1)], mat)


def lerp_table(tab, v):
    """Piecewise-linear lookup in [(v, value), ...] (v ascending)."""
    if v <= tab[0][0]:
        return tab[0][1]
    for (a, x), (b, y) in zip(tab, tab[1:]):
        if v <= b:
            return x + (y - x) * (v - a) / (b - a)
    return tab[-1][1]


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


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


def cats_frame(name, path, w=.30, h=.32):
    """W5: gold frame with a rope inner bead (pierced scroll moulding read as a bead of knots), burgundy mount, the
    two-cats picture (cats only). v13 t142 / t193.4."""
    mb = mo.MB()
    fw = .045
    frame_ring(mb, rect(w, h), fw, .026, 'gilt')
    iw, ih = w - 2 * fw + .012, h - 2 * fw + .012
    frame_ring(mb, rect(iw, ih), .009, .016, 'gilt_bright')
    for k in range(36):                                                 # rope knots round the sight edge
        t = k / 36
        per = 2 * (iw + ih)
        dpos = t * per
        if dpos < iw:
            x, z = -iw / 2 + dpos, -ih / 2
        elif dpos < iw + ih:
            x, z = iw / 2, -ih / 2 + dpos - iw
        elif dpos < 2 * iw + ih:
            x, z = iw / 2 - (dpos - iw - ih), ih / 2
        else:
            x, z = -iw / 2, ih / 2 - (dpos - 2 * iw - ih)
        mb.box((x - .004, -.022, z - .004), (x + .004, -.016, z + .004), 'gilt_bright', bev=.002)
    flat(mb, rect(iw - .012, ih - .012), -.006, m('burgundy'))
    flat(mb, rect(.172, .124, 0, .012), -.007, m('card'))
    picture(mb, rect(.16, .112, 0, .012), -.008, 'cats', path)
    return mb.finish(name)


def black_frame(name, path, w=.17):
    """W4: wide flat black frame with a stepped (reeded) gold slip, cream card and a small drawing of a grey cat
    (v13 t142; crop study_cat_grey.jpg). w = outer size, square."""
    mb = mo.MB()
    fw = .045
    frame_ring(mb, rect(w, w), fw, .020, 'black_matt')
    s = w - 2 * fw + .004
    for k, (dw, dd) in enumerate(((.0, .014), (.006, .011), (.012, .008))):    # three gold steps falling inward
        frame_ring(mb, rect(s - 2 * dw, s - 2 * dw), .005, dd, 'gilt_bright' if k % 2 == 0 else 'gilt')
    flat(mb, rect(s - .036, s - .036), -.005, m('card'))
    picture(mb, rect(s - .046, s - .046), -.006, 'cat_grey', path)
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
    """W2: two taxidermy greylag geese, breast, neck and head, side by side on a dark kidney-shaped plaque, turned
    toward each other, the larger (south) one with a raised fanned wing behind it (hr_v4_527, v13 t146). 0.36 x 0.30,
    0.20 off the wall. Origin: wall, centre."""
    mb = mo.MB()
    g, dk = m('goose'), 'dark_oak_antique'
    kid = []
    for k in range(20):                                             # kidney outline, dipped at the top centre
        t = math.tau * k / 20
        x, z = .175 * math.cos(t), .085 * math.sin(t)
        if z > 0:
            z -= .03 * math.exp(-(x / .05) ** 2)
        kid.append((x, 0, z - .07))
    mb.prism(kid, (0, -.022, 0), dk)
    mb.prism([(x * .9, -.022, (z + .07) * .8 - .07) for x, _, z in kid], (0, -.008, 0), dk)       # raised field
    for sx, s in ((-1, .86), (1, 1.0)):                             # left (north) smaller, right (south) larger
        c = Vector((sx * .075, -.085 * s - .02, -.045))
        mb.at(T(*c))                                                # body / breast: upright ellipsoid
        mb.lathe([(.058 * s * math.sin(math.pi * k / 8), -.075 * s * math.cos(math.pi * k / 8)) for k in range(9)], g,
                 12, ell=(1, 1.15))
        mb.at()
        top = c + Vector((0, -.012, .06 * s))
        head = Vector((sx * .045, c.y - .03, .145 * s - .03))
        mid = top.lerp(head, .5) + Vector((sx * .012, -.012, 0))
        mb.tube([top, mid, head], .021 * s, g, n=8)                 # neck
        ball(mb, T(*head), .029 * s, g, segs=10, squash=1.05)
        mb.at(T(*head) @ aim((-sx, -.45, -.25)))                    # beak toward the other bird
        mb.lathe([(0, .018), (.013, .024), (.010, .045), (.004, .06), (0, .062)], m('beak'), 8)
        mb.at()
    for k in range(6):                                              # fanned wing behind the larger bird
        a = math.radians(12 + 12 * k)
        base = Vector((.11, -.035, -.01))
        mb.at(T(*base) @ Matrix.Rotation(a, 4, 'Y') @ RX(90))
        mb.leaf(.13 - .008 * k, .035, .006, P.two_sided(m('goose' if k < 3 else 'bone')), segs=4)
    mb.at()
    return mb.finish(name)


def antler_trophy(name, s=.76):
    """W3: roe skull cap with a pair of three-point antlers on a dark carved leaf-shaped plaque, scaled by s so that
    the plaque spans 0.20 and the tips stand 0.23 above its centre (v13 t193.4: plaque bottom 2.05, tips 2.38).
    Origin: plaque centre."""
    mb = mo.MB()
    S0 = Matrix.Scale(s, 4)
    mb.at(S0)
    leaf = [(0, -.14), (.03, -.12), (.045, -.09), (.065, -.06), (.06, -.02), (.07, .02), (.05, .06), (.04, .09),
            (.02, .11), (0, .12), (-.02, .11), (-.04, .09), (-.05, .06), (-.07, .02), (-.06, -.02), (-.065, -.06),
            (-.045, -.09), (-.03, -.12)]                                       # lobed (carved oak-leaf) outline
    mb.prism([(x, 0, z) for x, z in leaf], (0, -.014, 0), 'dark_oak_antique')
    mb.prism([(x * .82, -.014, z * .85) for x, z in leaf], (0, -.006, 0), 'dark_oak_antique')   # raised centre
    mb.at(S0 @ T(0, -.02, .02) @ RX(90))
    mb.dome(.034, .055, .04, m('bone'))
    mb.at(S0)
    mb.box((-.012, -.047, -.09), (.012, -.02, -.03), m('bone'), bev=.006)      # nasal bones
    a = m('antler')
    for sx in (-1, 1):
        mb.at(S0 @ T(sx * .022, -.045, .055))
        mb.lathe([(0, 0), (.012, 0), (.013, .008), (.009, .016), (0, .018)], a, 8)   # burr / pedicle
        mb.at(S0)
        bm_ = [(sx * .02, -.045, .06), (sx * .04, -.055, .14), (sx * .06, -.045, .22), (sx * .055, -.03, .30)]
        mb.tube(bm_, .006, a, n=6)
        mb.tube([bm_[1], (sx * .045, -.10, .19)], .0045, a, n=6)
        mb.tube([bm_[2], (sx * .10, -.03, .27)], .0045, a, n=6)
    mb.at()
    return mb.finish(name)


# ----------------------------------------------------------------------------- fixed fittings (wall convention)
def radiator(name, tubes=7, w=.49, h=1.78, gap=.09):
    """White vertical column radiator (v13 t148, v4 f_0444): one row of 7 round-topped oval tubes 0.49 wide x 1.78,
    joined by headers behind top and bottom, two small wall brackets at the top ends and two lower stays, chrome
    valves at both bottom corners. Origin: wall, bottom centre of the tubes."""
    mb = mo.MB()
    pitch = w / tubes
    r, yc = pitch * .42, -gap - .035
    for i in range(tubes):
        mb.at(T((i - (tubes - 1) / 2) * pitch, yc, 0))
        mb.lathe([(0, 0), (r * .55, .004), (r * .9, .016), (r, .036), (r, h - .036), (r * .9, h - .016), (r * .55, h - .004),
                  (0, h)], 'white_gloss', 12, ell=(1, 1.55))
    mb.at()
    for z in (.035, h - .065):                                                     # headers, hidden behind the tubes
        mb.box((-w / 2 + pitch * .3, yc + .02, z), (w / 2 - pitch * .3, yc + .042, z + .03), 'white_gloss', bev=.004)
    for x in (-w / 2 + pitch * .5, w / 2 - pitch * .5):                             # top wall brackets
        mb.box((x - .01, yc + .042, h - .06), (x + .01, 0, h - .035), 'white_gloss', bev=.002)
        mb.box((x - .016, -.004, h - .07), (x + .016, 0, h - .025), 'white_gloss', bev=.0015)
    for x in (-.12, .12):                                                          # lower stays
        mb.box((x - .01, yc + .042, .25), (x + .01, 0, .27), 'white_gloss', bev=.002)
    for sx in (-1, 1):
        x = sx * (w / 2 - pitch / 2)
        mb.tube([(x, yc, .0), (x, yc, -.05), (x, 0, -.05)], .008, 'chrome', n=8, up=(1, 0, 0))
        mb.at(T(x, yc, -.05) @ aim((sx, 0, 0)))
        mb.lathe([(0, 0), (.013, 0), (.013, .03), (.02, .032), (.02, .075), (0, .075)],
                 'white_gloss' if sx > 0 else 'chrome', 10)                      # TRV head at the east, lockshield west
        mb.at()
    return mb.finish(name)


def aircon(name, w=.80, h=.30, d=.22):
    """White split indoor unit 0.80 x 0.30 x 0.22 (v13 t147 / t148 / t193.4): rounded casing with the top intake
    grille, a shadow gap under the front panel, the louvre flap along the curved lower front (dark slot above it),
    a round sensor eye and two indicator dots at the lower right. Origin: wall, bottom centre."""
    mb = mo.MB()
    side = [(0, .02), (.62 * d, 0), (.90 * d, .10 * h), (d, .36 * h), (.985 * d, .80 * h), (.84 * d, .985 * h), (0, h)]
    mb.prism([(-w / 2, -y, z) for y, z in side], (w, 0, 0), 'plastic_white')
    for sx in (-1, 1):                                                             # rounded end caps (slightly proud)
        mb.prism([(sx * (w / 2 + .0015), -y * .995, z) for y, z in side[1:-1]], (-sx * .006, 0, 0), 'plastic_white')
    # shadow gap under the front panel, louvre flap on the curved lower front over a dark outlet slot
    zf0 = .40 * h
    mb.box((-w / 2 + .016, -d - .0012, zf0 - .003), (w / 2 - .016, -d + .004, zf0), m('ac_line'))
    (y1, z1), (y2, z2) = (.90 * d, .10 * h), (d, .36 * h)
    yon = lambda z: y1 + (y2 - y1) * (z - z1) / (z2 - z1)
    za, zb, zc = .13 * h, .17 * h, .345 * h
    mb.prism([(-w / 2 + .03, -(yon(z) + o), z) for z, o in ((za, .001), (zb, .001), (zb, -.004), (za, -.004))],
             (w - .06, 0, 0), m('ac_dark'))
    mb.prism([(-w / 2 + .028, -(yon(z) + o), z) for z, o in ((zb, .0045), (zc, .0045), (zc, -.001), (zb, -.001))],
             (w - .056, 0, 0), 'plastic_white')
    # top intake grille: slots across the top
    for k in range(18):
        x = -w / 2 + .05 + k * (w - .10) / 17
        mb.box((x - .003, -.80 * d, .983 * h), (x + .003, -.25 * d, .9965 * h), m('ac_line'))
    # sensor eye and indicators, lower right of the front panel
    mb.at(T(w / 2 - .075, -d + .0005, zf0 + .035) @ RX(90))
    mb.lathe([(0, 0), (.014, 0), (.014, .002), (.011, .005), (0, .006)], m('remote_screen'), 14)
    mb.at()
    for dx in (.0, .014):
        mb.box((w / 2 - .045 + dx - .002, -d - .0015, zf0 + .012), (w / 2 - .045 + dx + .002, -d + .002, zf0 + .016),
               m('button'))
    return mb.finish(name)


def remote_cradle(name):
    """White wall cradle holding the a/c remote (v13 t127): cradle cup, long remote with a dark display near the top
    and a few round buttons. Origin: wall, bottom centre of the cradle."""
    mb = mo.MB()
    mb.box((-.032, -.024, 0), (.032, 0, .095), 'plastic_white', bev=.004)
    mb.box((-.026, -.03, .012), (.026, -.022, .08), 'plastic_white', bev=.003)          # cup lip
    mb.box((-.023, -.036, .03), (.023, -.016, .20), 'plastic_white', bev=.006)          # remote
    mb.box((-.016, -.0365, .145), (.016, -.0355, .188), m('ac_dark'))                   # display
    for k, (x, z) in enumerate(((-.01, .125), (.01, .125), (0, .108), (-.01, .092), (.01, .092))):
        mb.at(T(x, -.036, z) @ RX(90))
        mb.lathe([(0, 0), (.0042, 0), (.0038, .0018), (0, .002)], m('button') if k == 2 else 'plastic_white', 8)
    mb.at()
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
def desk(name, L, W, H=.74, castors=False):
    """White electric sit-stand table (v13 t129 / t164 / t176): 25 mm top with generously rounded corners
    (r 0.08) and a softened edge, steel frame with two telescopic rectangular columns (wide lower stage, slimmer
    upper stage) on flat T-feet 0.70 long with rounded ends, glides (or twin castors), a cross beam and side brackets
    under the top. Long axis = X; the front is local -Y. Origin: floor centre."""
    mb = mo.MB()
    w = m('desk')
    top = rrect(L, W, .08, n=5)
    mb.prism([(x, y, H - .022) for x, y in top], (0, 0, .022), w)
    mb.prism([(x * (L - .006) / L, y * (W - .006) / W, H - .025) for x, y in top], (0, 0, .003), w)   # eased edge
    for sx in (-1, 1):
        x = sx * (L / 2 - .17)
        foot = rrect(.07, .70, .03, n=3)
        mb.prism([(x + a, b, .012) for a, b in foot], (0, 0, .022), w)                     # flat T-foot
        mb.box((x - .028, -.33, .034), (x + .028, .33, .040), w, bev=.003)                 # foot crown
        for y in (-.31, .31):
            if castors:
                for dx in (-.012, .012):
                    mb.at(T(x + dx, y - .004, .022) @ Matrix.Rotation(math.pi / 2, 4, 'Y'))
                    mb.lathe([(0, -.006), (.02, -.006), (.022, -.002), (.022, .002), (.02, .006), (0, .006)],
                             'black_matt', 10)
                mb.at()
                mb.box((x - .018, y - .02, .03), (x + .018, y + .012, .042), 'black_matt', bev=.004)
            else:
                mb.at(T(x, y, 0))
                mb.lathe([(0, 0), (.018, 0), (.018, .008), (.012, .012), (0, .012)], m('glide'), 10)
                mb.at()
        mb.box((x - .042, -.032, .04), (x + .042, .032, .40), w, bev=.004)                 # lower stage
        mb.box((x - .036, -.026, .40), (x + .036, .026, H - .052), w, bev=.003)            # upper stage
        mb.box((x - .044, -.034, .395), (x + .044, .034, .405), w, bev=.002)               # stage collar
        mb.box((x - .03, -W / 2 + .07, H - .052), (x + .03, W / 2 - .07, H - .025), w, bev=.003)   # side bracket
    mb.box((-L / 2 + .17, -.035, H - .07), (L / 2 - .17, .035, H - .03), w, bev=.003)          # cross beam
    return mb.finish(name)


def hand_control(mb, B):
    """Black hand control strip under the front edge (v13 t164): up / down arrows, four presets and M (no
    lettering). Origin: underside of the top at the front edge, strip along local X, its face toward -Y."""
    mb.at(B)
    mb.box((-.10, -.012, -.042), (.10, .06, -.002), 'black_matt', bev=.004)
    mb.box((-.095, -.0135, -.038), (.095, -.012, -.006), m('ac_dark'))
    for k in range(7):
        x = -.075 + k * .025
        mb.box((x - .006, -.0145, -.028), (x + .006, -.013, -.016), m('button'), bev=.0005)
    mb.at()


def riser(mb, B, w=.55, d=.22, h=.10, t=.012, r=.03):
    """Pale bentwood plywood monitor riser (v13 t171): one board bent down at both ends with rounded bends.
    Origin: desk top, centre."""
    p = m('ply')
    mb.at(B)
    path = [(-w / 2 + t / 2, 0, 0)]
    for k in range(7):                                                  # west bend
        a = math.pi * (1 - k / 12)
        path.append((-w / 2 + r + (r - t / 2) * math.cos(a), 0, h - r + (r - t / 2) * math.sin(a)))
    for k in range(6, -1, -1):                                          # east bend
        a = math.pi * k / 12
        path.append((w / 2 - r + (r - t / 2) * math.cos(a), 0, h - r + (r - t / 2) * math.sin(a)))
    path.append((w / 2 - t / 2, 0, 0))
    prof = [(-t / 2, -d / 2), (t / 2, -d / 2), (t / 2, d / 2), (-t / 2, d / 2)]
    mb.sweep(prof + prof[:1], path, p, up=(0, 1, 0))
    mb.at()


def monitor_curved(mb, B, w=.82, h=.37, R=1.5, z0=.105):
    """34-inch curved ultrawide, blank, on a black stem and a hexagonal ring foot (v13 t171). Origin: centre of its
    foot; screen faces -Y, its lower edge at z0."""
    n, half, t = 10, w / 2 / R, .022
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
    mb.box((-.12, t, z0 + .05), (.12, t + .03, z0 + .25), k, bev=.006)               # back housing
    mb.box((-.028, t + .02, .008), (.028, t + .045, z0 + .20), k, bev=.006)           # stem
    hexo = [(.15 * math.cos(math.tau * i / 6), .09 * math.sin(math.tau * i / 6)) for i in range(6)]
    hexi = [(.105 * math.cos(math.tau * i / 6), .055 * math.sin(math.tau * i / 6)) for i in range(6)]
    for i in range(6):                                                  # hexagonal ring foot
        a, b, c, d_ = hexo[i], hexo[(i + 1) % 6], hexi[(i + 1) % 6], hexi[i]
        mb.prism([(a[0], a[1] + .04, 0), (b[0], b[1] + .04, 0), (c[0], c[1] + .04, 0), (d_[0], d_[1] + .04, 0)],
                 (0, 0, .008), k)
    mb.at()


def monitor_flat(mb, B, w=.72, h=.42, z0=.09):
    """32-inch flat monitor with a silver edge on a T-foot, blank. Origin: centre of its foot; screen faces -Y."""
    mb.at(B)
    mb.box((-w / 2, 0, z0), (w / 2, .018, z0 + h), 'silver_satin', bev=.002)
    mb.face([(-w / 2 + .007, -.0008, z0 + .007), (w / 2 - .007, -.0008, z0 + .007), (w / 2 - .007, -.0008, z0 + h - .007),
             (-w / 2 + .007, -.0008, z0 + h - .007)], 'screen_black', hint=(0, -1, 0))
    mb.box((-w / 2 + .02, .018, z0 + .02), (w / 2 - .02, .04, z0 + h - .02), 'black_matt', bev=.008)
    mb.box((-.03, .04, .01), (.03, .058, z0 + .22), 'silver_satin', bev=.004)
    mb.box((-.26, -.03, 0), (.26, .0, .012), 'silver_satin', bev=.003)
    mb.box((-.03, 0, 0), (.03, .16, .012), 'silver_satin', bev=.003)
    mb.at()


def keyboard_mouse(mb, B):
    """Dark grey full-size keyboard 0.43 x 0.13 with its key caps (long axis X, origin its centre), a brown leather
    mouse mat with an organic outline and a mouse 0.32 to its +X end (v13 t171 / t176)."""
    k = m('key')
    mb.at(B)
    mb.box((-.215, -.065, 0), (.215, .065, .012), 'black_matt', bev=.004)
    for y, nk in ((-.024, 13), (-.002, 13), (.02, 12), (.042, 12)):     # main block, 18.5 mm pitch
        for i in range(nk):
            x = -.205 + i * .0185
            mb.box((x, y - .008, .012), (x + .0155, y + .008, .0185), k, bev=.0012)
    mb.box((-.205, -.054, .012), (-.15, -.038, .0185), k, bev=.0012)               # bottom row: modifiers,
    mb.box((-.14, -.054, .012), (.02, -.038, .0185), k, bev=.0012)                 # space bar,
    mb.box((.03, -.054, .012), (.07, -.038, .0185), k, bev=.0012)                  # arrows
    for i in range(4):                                                  # numeric block
        for j in range(5):
            x, y = .135 + i * .0185, -.046 + j * .022
            mb.box((x, y - .008, .012), (x + .0155, y + .008, .0185), k, bev=.0012)
    mb.at(B @ T(.32, .0, 0))
    mat_ = [(.11 * math.cos(a) * (1 + .12 * math.sin(3 * a)), .085 * math.sin(a) * (1 + .1 * math.cos(2 * a)))
            for a in (math.tau * i / 16 for i in range(16))]
    mb.prism([(x, y, 0) for x, y in mat_], (0, 0, .003), m('leather'))
    mb.at(B @ T(.32, .0, .003))
    mb.dome(.032, .052, .034, 'black_matt', segs=10)
    mb.at()


def desk_lamp(name):
    """Black gooseneck ring lamp (v13 t129): weighted round base, gooseneck, LED ring 0.20 across facing local -Y.
    -> (object, local point in front of the ring)."""
    mb = mo.MB()
    k = 'black_matt'
    mb.lathe([(0, 0), (.065, 0), (.065, .014), (.03, .02), (.012, .03), (0, .03)], k, 16)
    neck = [(0, 0, .03), (0, 0, .20), (0, -.01, .30), (0, -.04, .38), (0, -.07, .42)]
    mb.tube(neck, .0065, k, n=8, up=(1, 0, 0))
    rc = Vector((0, -.075, .52))
    mb.tube([(0, -.07, .42), (0, -.075, .432)], .006, k, n=8, up=(1, 0, 0))
    mb.at(T(*rc) @ RX(90))                                              # ring in the x-z plane, facing -Y
    mb.lathe([(.088, -.008), (.10, -.008), (.10, .008), (.088, .008), (.088, -.008)], k, 24)
    mb.lathe([(.099, .0082), (.089, .0082)], P.emissive('#F4CB94', 5.0), 24)       # LED face
    mb.at()
    return mb.finish(name), Vector((0, -.16, .52))


# ----------------------------------------------------------------------------- seating
def office_chair(name):
    """Black fabric gaming chair (v13 t160 / t176 / t129): five-star nylon base on twin castors, black gas lift, a
    bucket seat with raised side bolsters and a rolled front, a tall winged back with integral headrest - padded
    vertical channels fanning up over the shoulders, horizontal channels over the lumbar - red contrast stitching,
    oval arm pads on flip-up posts. 0.67 x 0.66 x 1.24: under 1.30, so the walk layer treats it as soft furniture
    (geom.js SMALL). Faces local -Y; origin floor centre."""
    mb = mo.MB()
    f, k, st = m('fabric'), 'black_matt', m('stitch')
    # --- five-star base on twin castors, hub, gas lift, mechanism
    for i in range(5):
        a = math.radians(72 * i + 18)
        d = Vector((math.cos(a), math.sin(a), 0))
        s = Vector((-d.y, d.x, 0))
        beam(mb, d * .03 + Vector((0, 0, .098)), d * .29 + Vector((0, 0, .074)), .052, .042, .036, .026, k)
        tip = d * .30
        mb.at(T(tip.x, tip.y, .058))
        mb.lathe([(0, -.006), (.017, -.006), (.017, .016), (0, .016)], k, 8)       # castor socket
        mb.at()
        for sw in (-1, 1):                                                          # twin wheels
            c = tip + d * .012 + s * sw * .013
            mb.at(T(c.x, c.y, .028) @ aim(s))
            mb.lathe([(0, -.0065), (.025, -.0065), (.028, -.003), (.028, .003), (.025, .0065), (0, .0065)], k, 10)
        mb.at()
        hood = tip + d * .012
        mb.box((hood.x - .013, hood.y - .013, .04), (hood.x + .013, hood.y + .013, .062), k, bev=.004)   # fork
    mb.lathe([(0, .06), (.05, .06), (.06, .075), (.056, .11), (.034, .125), (0, .125)], k, 14)   # hub
    mb.lathe([(0, .12), (.034, .12), (.031, .30), (.025, .31), (.022, .41), (0, .41)], k, 14)    # gas lift
    mb.box((-.13, -.12, .385), (.13, .12, .43), k, bev=.01)                         # tilt mechanism
    mb.tube([(.12, -.06, .40), (.20, -.10, .395), (.23, -.11, .39)], .006, k, n=6)  # lever
    mb.at(T(.23, -.11, .39))
    mb.lathe([(0, -.012), (.011, -.012), (.012, .0), (.011, .012), (0, .012)], k, 8)
    mb.at()

    # --- bucket seat (t160): dished centre panel, tall rolled side bolsters rising about 0.07 above it from a crease,
    # waterfall front. Lofted cross-sections from the back (y +0.23) to the front roll (y -0.27)
    ST = [(.23, .505, .056, .255), (.17, .497, .060, .266), (.08, .489, .062, .272), (0, .486, .062, .272),
          (-.08, .489, .060, .272), (-.15, .495, .052, .268), (-.21, .498, .038, .262), (-.25, .487, .02, .254),
          (-.27, .463, .005, .244)]                                                 # (y, centre top z, bolster, half w)
    zb, U = .425, (-1, -.96, -.90, -.83, -.75, -.67, -.58, -.48, -.32, -.16, 0, .16, .32, .48, .58, .67, .75, .83,
                   .90, .96, 1)

    def ztop(u, zc, bh):
        a = abs(u)
        z = zc - .014 * max(0.0, 1 - (a / .48) ** 2)                                # dished centre panel
        z += bh * smooth((a - .48) / .25)                                           # bolster, up from the crease
        if a > .84:
            z -= (bh + .03) * smooth((a - .84) / .16) ** 1.4                         # rounded outer edge
        return z

    def seat_sec(y, zc, bh, hw):
        top = [(u * hw, y, ztop(u, zc, bh)) for u in U]
        bot = [(hw - .012, y, zb + .012), (hw - .04, y, zb), (-(hw - .04), y, zb), (-(hw - .012), y, zb + .012)]
        return top + bot
    loft(mb, [seat_sec(*row) for row in ST], f)

    def seat_pt(x, y, lift=.0022):                                                  # point on the seat top
        for (ya, za, ba, ha), (yb_, zb_, bb, hb) in zip(ST, ST[1:]):
            if ya >= y >= yb_:
                t = (ya - y) / (ya - yb_)
                zc, bh, hw = za + (zb_ - za) * t, ba + (bb - ba) * t, ha + (hb - ha) * t
                return (x, y, ztop(x / hw, zc, bh) + lift)
        return (x, y, ST[-1][1] + lift)
    for yc in (.13, .04, -.05, -.14):                                               # chevron channels, V to the front
        mb.tube([seat_pt(u * .115, yc - .04 * (1 - abs(u))) for u in (-1, -.5, 0, .5, 1)], .0011, st, n=4)
    for sx in (-1, 1):                                                              # seams along the bolster creases
        mb.tube([seat_pt(sx * .128, y) for y in (.21, .12, .03, -.06, -.15, -.22)], .0011, st, n=4)

    # --- back (t160): sections up its own axis v, leaning back 12 degrees. U-shaped: shoulder wings 0.11 forward,
    # easing to 0.04 at the lumbar (which bulges 0.016), their tops rounded off into ears beside a narrower head section (0.72 of the
    # shoulder width). A centre panel of padded channels with real grooves - five vertical channels over the
    # shoulders, five horizontal ones over the lumbar - and red stitching along both edges of every groove.
    HW = [(0, .238), (.12, .242), (.25, .252), (.40, .272), (.52, .286), (.58, .288), (.615, .278), (.64, .25),
          (.66, .222), (.68, .21), (.74, .207), (.77, .20), (.79, .184), (.80, .16), (.81, .11)]
    WING = [(0, .04), (.15, .042), (.30, .065), (.42, .10), (.55, .112), (.60, .105), (.635, .065), (.67, .025),
            (.81, .012)]
    PAN = [(0, .62), (.58, .62), (.67, .74), (.81, .74)]                            # panel half-width, share of HW
    VS = [k * .015 for k in range(25)] + [.39, .42, .45, .48, .51, .54, .57, .60, .62, .64, .66, .68, .71, .74, .765,
                                          .785, .80, .81]
    SS = [k / 10 - 1 for k in range(21)]                                            # panel samples, share of PAN
    WS = (.15, .35, .55, .75, .88, .96, 1.0)                                        # wing samples, seam 0 .. rim 1
    LUMB, UPPER = (.03, .33), (.36, .78)

    def pillow(s, v):                                                               # channel bulge toward -y
        if LUMB[0] <= v <= LUMB[1]:                                                 # horizontal channels 0.06 apart
            return .006 * math.sin(math.pi * (((v - LUMB[0]) / .06) % 1.0)) * smooth((1 - abs(s)) / .12)
        if UPPER[0] <= v <= UPPER[1]:                                               # vertical channels 0.4 of s apart
            return .007 * math.sin(math.pi * (((s + 1) / .4) % 1.0)) * smooth((v - UPPER[0]) / .03) * \
                smooth((UPPER[1] - v) / .03)
        return 0.0

    def lumbar(v):
        return .016 * math.sin(math.pi * min(1.0, max(0.0, (v - .02) / .34)))

    def ypan(s, v):
        return -.048 - lumbar(v) - pillow(s, v) + (.003 if abs(s) > .999 else 0.0)  # seam groove on the panel edge

    def ywing(w, v):                                                                # bolster bulge, rolled rim
        fw = lerp_table(WING, v)
        return -.048 - lumbar(v) - fw * math.sin(math.pi / 2 * min(1.0, w / .75)) + fw * .25 * smooth((w - .85) / .15)

    def uw(w, v):
        p = lerp_table(PAN, v)
        return p + (1 - p) * w

    def back_sec(v):
        hw, fw, p = lerp_table(HW, v), lerp_table(WING, v), lerp_table(PAN, v)
        sec = [(-uw(w, v) * hw, ywing(w, v), v) for w in WS[::-1]]
        sec += [(s * p * hw, ypan(s, v), v) for s in SS]
        sec += [(uw(w, v) * hw, ywing(w, v), v) for w in WS]
        yb = lambda u: .045 + .012 * (1 - u * u) - .8 * fw * smooth((abs(u) - .55) / .45)
        sec.append((hw + .008, (ywing(1, v) + yb(1)) / 2, v))
        sec += [(u * hw * .97, yb(u), v) for u in (.85, .55, .2, -.2, -.55, -.85)]
        sec.append((-(hw + .008), (ywing(1, v) + yb(1)) / 2, v))
        return sec
    B = T(0, .19, .45) @ RX(-12)
    mb.at(B)
    loft(mb, [back_sec(v) for v in VS], f)

    def bpt(s, v, lift=.0024):                                                      # stitch point on the panel
        return (s * lerp_table(PAN, v) * lerp_table(HW, v), ypan(s, v) - lift, v)
    vu, R = [v for v in VS if UPPER[0] + .02 <= v <= UPPER[1] - .02], .0008       # R: stitch thread
    for g in (-.6, -.2, .2, .6):                                                    # vertical grooves, both edges
        for e in (-.022, .022):
            mb.tube([bpt(g + e, v) for v in vu], R, st, n=4)
    for g in (.09, .15, .21, .27):                                                  # lumbar grooves, both edges
        for e in (-.0035, .0035):
            mb.tube([bpt(s, g + e) for s in (-.95, -.85, 0, .85, .95)], R, st, n=4)
    for v in (.035, .325):                                                          # lumbar panel top and bottom
        mb.tube([bpt(s, v) for s in (-.95, -.85, 0, .85, .95)], R, st, n=4)
    for v in (.365, .775):                                                          # upper panel bottom and top
        mb.tube([bpt(s, v) for s in SS if abs(s) < .99], R, st, n=4)
    for sx in (-1, 1):
        mb.tube([bpt(sx * .95, v) for v in VS if .03 <= v <= .78], R, st, n=4)      # panel outline
        mb.tube([(sx * uw(.55, v) * lerp_table(HW, v), ywing(.55, v) - .0024, v) for v in VS if .40 <= v <= .62],
                R, st, n=4)                                                         # wing seams
    mb.at()

    # --- arms: bracket under the seat, post, oval pad
    for sx in (-1, 1):
        beam(mb, (sx * .11, -.03, .405), (sx * .29, -.03, .405), .05, .02, .045, .02, k)
        mb.box((sx * .275 - .015, -.065, .40), (sx * .275 + .015, .005, .615), k, bev=.008)
        mb.box((sx * .277 - .011, -.075, .60), (sx * .277 + .011, .015, .628), k, bev=.006)   # flip hinge block
        mb.at(T(sx * .285, -.04, .628))
        mb.lathe([(0, 0), (.04, 0), (.045, .01), (.044, .024), (.034, .033), (0, .035)], k, 14, ell=(1, 2.9))
        mb.at()
    return weld(mb.finish(name))


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


def pillow(mb, B, w, d, h, r, mat, crown=.015, bulge=.012, n=4, seam=None):
    """Soft cushion w (x) x d (y) x h (z): rounded-rectangle sections with round top and bottom edges, gently
    bulging sides and a crowned top; seam = material of a piping cord round the top edge. Origin B: bottom centre."""
    mb.at(B)
    secs = []
    for t in (0, .1, .3, .5, .7, .9, 1.0):
        e = r * (1 - math.sqrt(max(0.0, 1 - (2 * t - 1) ** 2)))
        bl = bulge * math.sin(math.pi * t)
        ww, dd = w - 2 * e + 2 * bl, d - 2 * e + 2 * bl
        rr = max(.012, min(r, ww / 2 - .002, dd / 2 - .002))
        secs.append([(x, y, t * h) for x, y in rrect(ww, dd, rr, n)])
    loft(mb, secs, mat, caps=(True, False))
    fan_cap(mb, secs[-1], (0, 0, h + crown), mat)
    if seam is not None:
        t = .9
        e = r * (1 - math.sqrt(max(0.0, 1 - (2 * t - 1) ** 2))) - .004
        ww, dd = w - 2 * e + 2 * bulge * math.sin(math.pi * t), d - 2 * e + 2 * bulge * math.sin(math.pi * t)
        rr = max(.012, min(r, ww / 2 - .002, dd / 2 - .002))
        mb.tube([(x, y, t * h) for x, y in rrect(ww, dd, rr, n)], .005, seam, n=5, closed=True, up=(0, 0, 1))
    mb.at()


def bean_bag(name):
    """Lounger bean bag (v13 t152 / t166, f_0151-f_0158): dusty raspberry woven nylon, a seat cushion and a back
    cushion leaning on the wall behind (0.55 high), piped seams, a carry loop on top. 0.72 wide x 0.85 deep. Faces
    local -Y (the back stands against the wall at local y +0.425). Origin floor centre."""
    mb = mo.MB()
    c = m('beanbag')
    pillow(mb, T(0, -.10, 0), .72, .64, .24, .09, c, crown=.02, bulge=.018, seam=c)
    lean = 15
    Bb = T(0, .175, .03) @ RX(-lean)
    pillow(mb, Bb @ T(0, 0, 0), .70, .19, .53, .075, c, crown=.012, bulge=.012, seam=c)
    mb.at(Bb @ T(0, .0, .53 + .01))                                                # carry loop
    mb.tube([(-.05, .0, -.004), (-.04, .0, .03), (0, .0, .045), (.04, .0, .03), (.05, .0, -.004)], .009, c, n=6,
            up=(0, 1, 0))
    mb.at()
    return weld(mb.finish(name), 40.0)


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
        strip(mb, [(x, yf, .37), (x, yf + .007, .31), (x, yf + .005, .23), (x, yf - .006, .13), (x, yf - .004, .06),
                   (x, yf + .008, .018)], .032, .03, mh, (1, 0, 0))                     # front leg, slight cabriole
        mb.box((x - .018, yf - .012, 0), (x + .018, yf + .026, .02), mh, bev=.006)       # pad foot
        mb.box((x - .014, yb1, .31), (x + .014, yf - .016, .37), mh)                     # side seat rail
        mb.tube([(x, yb1, .13), (x, yf - .016, .13)], .009, mh, n=8)                     # side stretcher
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
    """Narrow upright staked shrub packed with glossy oval leaves (v13 t152 / t166 / t194.4, hr_v4_559): one leader
    on a cane, short rising side shoots from 0.40 up, about 0.30 across low down and 0.15 at the top; about 180 cupped
    leaves 0.055-0.08 long, held upward (one leaf shape, smooth shaded); terracotta pot (dia 0.30 x 0.27) with a darker
    drip-glaze band under the rim, on a saucer."""
    mb = mo.MB()
    tc, rnd, bark = M.solid('study_pot', '#B98C68', .85), random.Random(7), m('bark')
    glaze = M.solid('study_pot_glaze', '#7A5844', .5)
    mb.lathe([(0, 0), (.17, 0), (.18, .025), (.168, .025), (.162, .012), (0, .012)], tc, 20)
    mb.at(T(0, 0, .012))
    mb.lathe([(0, 0), (.115, 0), (.134, .12)], tc, 20)
    mb.lathe([(.134, .12), (.146, .21)], glaze, 20)                  # dark drip band under the rim (t166)
    mb.lathe([(.146, .21), (.15, .25), (.158, .25), (.158, .27), (.14, .27), (.136, .243), (0, .243)], tc, 20)
    mb.at()
    mb.face([(.136 * math.cos(math.tau * k / 12), .136 * math.sin(math.tau * k / 12), .256) for k in range(12)], m('soil'),
            hint=(0, 0, 1))
    mb.tube([(0, 0, .25), (.012, 0, .60), (0, .01, height - .04)], .008, bark, n=6)
    mb.tube([(.02, .01, .25), (.02, .01, height - .02)], .004, m('stake'), n=5)
    greens = [P.two_sided(M.solid('study_leaf_%d' % i, c, .3)) for i, c in enumerate(('#46683A', '#537647', '#628554'))]
    rim = [(.5 * math.sin(t) * (1.15 - .35 * (.5 - .5 * math.cos(t))), .5 - .5 * math.cos(t))
           for t in (math.tau * k / 8 for k in range(8))]           # unit leaf: widest below the middle, blunt tip
    count = [0]

    def leaf(p, az, tilt):                                          # cupped oval leaf pointing to plan direction az
        s, count[0] = rnd.uniform(.8, 1.2), count[0] + 1
        L, W = .068 * s, .037 * s
        mb.at(T(*p) @ RZ(az - 90 + rnd.uniform(-35, 35)) @ RX(tilt) @ Matrix.Rotation(rnd.uniform(-.4, .4), 4, 'Y'))
        ring = [(W * x, L * y, .005 * s) for x, y in rim]           # edges up, centre down: a shallow cup
        c, g = (0, L * .5, 0), greens[count[0] % 3]
        for k in range(8):
            mb.face([c, ring[k], ring[(k + 1) % 8]], g, hint=(0, 0, 1))
        mb.at()

    nb = 18
    for j in range(nb):                                             # rising side shoots, longest low down
        f = j / (nb - 1)
        z, L = .40 + (height - .50) * f, .11 - .06 * f
        az = j * 137.5 + rnd.uniform(-15, 15)
        d = Vector((math.cos(math.radians(az)), math.sin(math.radians(az)), 0))
        pts = [Vector((0, 0, z)), Vector((0, 0, z)) + d * L * .5 + Vector((0, 0, L * .5)), Vector((0, 0, z)) + d * L + Vector((0, 0, L * 1.1))]
        mb.tube(pts, .0028, bark, n=4)
        for i, t in enumerate((.25, .38, .5, .6, .7, .8, .9, 1.0)):
            q = pts[0].lerp(pts[1], t / .5) if t <= .5 else pts[1].lerp(pts[2], (t - .5) / .5)
            side = 65 if i % 2 else -65                             # alternate leaves either side of the shoot
            leaf(q, az + side * (1 - t * .7) + rnd.uniform(-20, 20), rnd.uniform(30, 65))
    for i in range(40):                                             # leaves on the leader, crowded at the top
        z = .40 + (height - .40) * (i / 39) ** .7
        leaf((.01 * math.sin(i), .01 * math.cos(i), z), i * 137.5, rnd.uniform(40, 75))
    ob = mb.finish(name)
    return weld(ob, 40.0)                                           # leaves smooth across their fan triangles


# ----------------------------------------------------------------------------- corner cabinet
def corner_cabinet(name, Mw, leg=.60, back=0.0):
    """Rustic light-oak two-part corner cabinet 1.82 high, its back corner at the origin of Mw: local u along one
    wall, v along the other (Mw may mirror). Lower cupboard 0.68 with a real interior, waist shelf, open upper part
    with two shelves, flat cornice; `back` = gap from the local origin to the walls (the waist shelf and the cornice
    run back to them over the skirting). The door is NOT here (study.py hangs and tags it).
    -> (carcass object, dict of local plan points: c0, c1 = ends of the front, e = unit vector c0 -> c1)."""
    oak = 'oak_door'
    c0, c1 = (leg - .04, .12), (.12, leg - .04)
    ex, ey = -math.sqrt(.5), math.sqrt(.5)
    nx, ny = -math.sqrt(.5), -math.sqrt(.5)                          # from the front back into the corner
    plan = [(0, 0), (leg, 0), c0, c1, (0, leg)]

    def grow(d):                                                     # overhanging slab, run back to the walls
        return [(-back, -back), (leg + d * .3, -back), (c0[0] + d, c0[1] + d * .6), (c1[0] + d * .6, c1[1] + d),
                (-back, leg + d * .3)]

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
        stile((leg - .002, .007), c0, .018, z0, z1)                  # canted side stiles, kept off the walls
        stile((.007, leg - .002), c1, .018, z0, z1)
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

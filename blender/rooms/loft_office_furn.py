"""Detailed pieces of the Slate Room (loft_office): mesh office chair, 49-inch curved monitor, 27-inch monitor on an arm,
architect desk lamp with a domed shade, rustic oak bookcase with framed-panel ends, piano stool, PC tower.

Also the Chippendale side chair of the dining set re-legged with the carver's cabriole ball-and-claw front legs, as
filmed in this room (hr_252).

Every builder returns one unlinked object (or adds into an MB the caller passes); the caller places and tags it.
Sizes from v5 f_0233-f_0246 (hr_183, hr_235), v12 f4-6 / f64 (bookcase) and spec/rooms/loft_office.md 6.
"""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

from lib import materials as M, mouldings as mo, props as P

T = Matrix.Translation


def R(axis, deg):
    return Matrix.Rotation(math.radians(deg), 4, axis)


def col(name, hx, rough=0.6, metal=0):
    return M.solid('loft_' + name, hx, rough, metal)


# ------------------------------------------------------------------ small mesh helpers
def solid8(b, c, mat):
    """Closed six-sided solid from 8 corners c[(i, j, k)], i, j, k in (0, 1); faces wound outward."""
    cen = sum((Vector(p) for p in c.values()), Vector()) / 8
    for f in (((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)), ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)),
              ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)), ((0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)),
              ((0, 0, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1)), ((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1))):
        pts = [Vector(c[k]) for k in f]
        b.face(pts, mat, hint=sum(pts, Vector()) / 4 - cen)


def grid(b, fn, nu, nv, mat):
    """Single-sided surface of nu x nv quads from fn(u, v) -> (x, y, z), u, v in [0, 1] (two-sided material)."""
    V = [b._vs([fn(i / nu, j / nv) for j in range(nv + 1)]) for i in range(nu + 1)]
    mi = b.mi(mat)
    for i in range(nu):
        for j in range(nv):
            b._f([V[i][j], V[i + 1][j], V[i + 1][j + 1], V[i][j + 1]], mi,
                 [(i / nu, j / nv), ((i + 1) / nu, j / nv), ((i + 1) / nu, (j + 1) / nv), (i / nu, (j + 1) / nv)])


def rounded(s, t):
    """Square (s, t) in [-1, 1]^2 -> superellipse of order 4 (soft rounded corners)."""
    m = max(abs(s), abs(t))
    if m < 1e-9:
        return 0.0, 0.0
    k = m / (abs(s) ** 4 + abs(t) ** 4) ** 0.25
    return s * k, t * k


def ring(n):
    """n points counter-clockwise round the superellipse |x|^4 + |y|^4 = 1 (the outline of rounded()), spaced evenly
    by angle so every rounded corner gets several points (even spacing along the square left one or two per corner)."""
    pts = []
    for k in range(n):
        a = 2 * math.pi * (k + .5) / n - math.pi
        c, s = math.cos(a), math.sin(a)
        r = (c ** 4 + s ** 4) ** -.25
        pts.append((c * r, s * r))
    return pts


# ------------------------------------------------------------------ mesh office chair (v5 f_0233-f_0244, hr_235)
def office_chair(name):
    """Ergonomic mesh chair: white frame, grey mesh seat / back / headrest, flip-up arms with grey pads, black gas-lift
    shroud on a chrome column, polished five-star base on twin-wheel castors. Local: origin floor centre, the sitter
    faces -Y. 0.66 x 0.66 x 1.25."""
    b = mo.MB()
    wh, al, blk = 'plastic_white', 'chrome', 'black_matt'
    mesh = P.two_sided(col('mesh', '#7F8287', .95))
    pad = col('armpad', '#5A5D63', .7)
    # five-star base: tapered polished spokes, one forward, dipping toward the castors
    for k in range(5):
        th = math.radians(-90 + 72 * k)
        d, p = Vector((math.cos(th), math.sin(th), 0)), Vector((-math.sin(th), math.cos(th), 0))
        st = [(0.04, .028, .100, .140), (0.22, .022, .088, .118), (0.305, .018, .072, .094)]   # r, half width, z0, z1
        for (r0, w0, a0, c0), (r1, w1, a1, c1) in zip(st, st[1:]):
            c = {}
            for i, (r, w, za, zc) in enumerate(((r0, w0, a0, c0), (r1, w1, a1, c1))):
                for j, s in enumerate((-1, 1)):
                    for kk, z in enumerate((za, zc)):
                        q = d * r + p * (s * w * (0.8 if kk else 1.0))
                        c[(i, j, kk)] = (q.x, q.y, z)
            solid8(b, c, al)
        tip = d * 0.30
        b.at(T((tip.x, tip.y, 0)) @ R('Z', math.degrees(th)))
        b.lathe([(0, .068), (.009, .068), (.009, .078), (0, .078)], al, 8)                       # swivel stem
        b.box((-.028, -.024, .032), (.022, .024, .07), blk, bev=.012)                          # hood
        for s in (-1, 1):                                                                      # twin wheels
            b.at(T((tip.x, tip.y, .029)) @ R('Z', math.degrees(th)) @ T((-.008, s * .015, 0)) @ R('X', 90))
            b.lathe([(0, -.0075), (.025, -.0075), (.029, -.003), (.029, .003), (.025, .0075), (0, .0075)], blk, 12)
        b.at()
    b.lathe([(0, .10), (.05, .10), (.05, .145), (.03, .15), (0, .15)], al, 16)                   # hub
    b.lathe([(0, .15), (.034, .15), (.034, .17), (.031, .18), (.031, .30), (.026, .305), (0, .305)], blk, 16)
    b.lathe([(0, .30), (.021, .30), (.021, .405), (0, .405)], al, 14)                           # gas lift
    b.box((-.10, -.11, .40), (.10, .13, .44), blk, bev=.01)                                     # tilt mechanism
    b.tube([(.10, -.02, .42), (.165, -.06, .425)], .006, blk, n=6)                               # height paddle
    b.box((.16, -.075, .418), (.185, -.045, .432), blk, bev=.004)

    # seat: white shell, white rim, grey mesh slung in it, waterfall front
    W, D = .245, .235
    def seat_z(x, y):
        dip = .014 * (1 - (x / W) ** 2) * (1 - (y / D) ** 2)
        fall = .02 * max(0.0, (-y - .13) / .105) ** 2
        return .478 - dip - fall
    b.box((-.225, -.215, .432), (.225, .205, .456), wh, bev=.012)
    rim = [(x * W, y * D, seat_z(x * W * .999, y * D * .999) + .004) for x, y in ring(36)]
    b.tube(rim, .013, wh, n=12, closed=True, up=(0, 0, 1))
    def seat(u, v):
        x, y = rounded(-.96 + 1.92 * u, -.96 + 1.92 * v)
        return (x * W, y * D, seat_z(x * W, y * D))
    grid(b, seat, 8, 8, mesh)
    for s in (-1, 1):                                                                          # skirt under the rim
        b.box((s * .235, -.20, .445), (s * .245, .20, .47), wh, bev=.003)

    # back: S-curved white frame (lumbar forward), grey mesh, reclined about 10 degrees, wrapped round the sitter
    def back(s, t):
        z = .575 + .50 * t
        w = .232 - .022 * t
        y = .232 + .16 * t - .032 * math.exp(-((t - .26) / .17) ** 2) - .065 * s * s
        return (s * w, y, z)
    nb = Vector((0, 1, -.32)).normalized()
    fr = [back(x, (y + 1) / 2) for x, y in ring(44)]
    b.tube(fr, .014, wh, n=12, closed=True, up=tuple(nb))
    grid(b, lambda u, v: back(*((lambda x, y: (x * .97, (y * .97 + 1) / 2))(*rounded(2 * u - 1, 2 * v - 1)))), 8, 10, mesh)
    # spine from the mechanism, behind the mesh, up to the headrest
    sp = [(0, .10, .425), (0, .22, .43), (0, .275, .47), (0, .272, .55)]
    sp += [(lambda q: (0, q[1] + .03, q[2]))(back(0, t)) for t in (0.0, .25, .5, .75, 1.0)]
    sp += [(0, .44, 1.13)]
    b.tube(sp, .02, wh, n=12, up=(1, 0, 0))
    b.box((-.035, .395, 1.05), (.035, .425, 1.10), wh, bev=.008)                                # headrest slider
    # headrest: curved white frame with mesh
    def head(s, t):
        return (s * .15, .43 + .035 * t - .055 * s * s, 1.125 + .125 * t)
    hf = [head(x, (y + 1) / 2) for x, y in ring(32)]
    b.tube(hf, .012, wh, n=12, closed=True, up=(0, 1, -.25))
    grid(b, lambda u, v: head(*((lambda x, y: (x * .95, (y * .9 + 1) / 2))(*rounded(2 * u - 1, 2 * v - 1)))), 6, 4, mesh)

    # flip-up arms: white bracket under the seat, upright, grey pad
    for s in (-1, 1):
        b.box((s * .17, -.01, .408), (s * .275, .06, .428), wh, bev=.006)
        b.box((s * .258, -.005, .405), (s * .288, .055, .655), wh, bev=.008)
        b.box((s * .225, -.17, .652), (s * .318, .10, .682), pad, bev=.012)
        b.box((s * .245, -.03, .638), (s * .30, .07, .654), blk, bev=.004)                    # flip hinge block
    return b.finish(name)


# ------------------------------------------------------------------ monitors (hr_235)
def curved_monitor(b, cx, cy, z0, desk_z, R_=1.8, w=1.20, h=.37, n=18):
    """49-inch 32:9 curved ultrawide (1800R) into MB b (world frame): apex of the screen at (cx, cy), concave toward
    -X, panel z0..z0+h; thin black bezel, glossy black screen, matt shell with the stand mount, V-neck and foot plate.
    Screen blank."""
    a1 = (w / 2) / R_
    ox = cx - R_
    def P_(r, a, z):
        return (ox + r * math.cos(a), cy + r * math.sin(a), z)
    scr, bz, blk = 'screen_black', 'black_matt', 'black_matt'
    zb, zt = z0 + .018, z0 + h - .007                       # screen inside the bezel; chin at the bottom
    for k in range(n):
        a, c = -a1 + 2 * a1 * k / n, -a1 + 2 * a1 * (k + 1) / n
        b.face([P_(R_, a, z0), P_(R_, c, z0), P_(R_, c, zb), P_(R_, a, zb)], bz, hint=(-1, 0, 0))
        b.face([P_(R_, a, zt), P_(R_, c, zt), P_(R_, c, z0 + h), P_(R_, a, z0 + h)], bz, hint=(-1, 0, 0))
        b.face([P_(R_ - .001, a, zb), P_(R_ - .001, c, zb), P_(R_ - .001, c, zt), P_(R_ - .001, a, zt)], scr,
               hint=(-1, 0, 0))
        b.face([P_(R_ + .022, a, z0 + .004), P_(R_ + .022, c, z0 + .004), P_(R_ + .022, c, z0 + h - .004),
                P_(R_ + .022, a, z0 + h - .004)], blk, hint=(1, 0, 0))                          # back shell
        for za, zc, r0, r1, hz in ((z0, z0 + .004, R_, R_ + .022, -1), (z0 + h - .004, z0 + h, R_ + .022, R_, 1)):
            b.face([P_(r0, a, za if hz < 0 else zc), P_(r0, c, za if hz < 0 else zc), P_(r1, c, zc if hz < 0 else za),
                    P_(r1, a, zc if hz < 0 else za)], blk, hint=(0, 0, hz))
    for s in (-1, 1):                                       # end caps
        a = s * a1
        b.face([P_(R_, a, z0), P_(R_ + .022, a, z0 + .004), P_(R_ + .022, a, z0 + h - .004), P_(R_, a, z0 + h)], blk,
               hint=(0, s, 0))
    # rear hump with the VESA mount (thicker middle of the shell)
    r = R_ + .022
    b.box((ox + r - .002, cy - .24, z0 + .05), (ox + r + .035, cy + .24, z0 + h - .05), blk, bev=.018)
    b.box((ox + r + .033, cy - .05, z0 + .10), (ox + r + .06, cy + .05, z0 + .22), blk, bev=.006)
    # stand: neck down to a flat V foot on the desk
    nx = ox + r + .045
    b.box((nx - .012, cy - .035, desk_z + .012), (nx + .022, cy + .035, z0 + .21), 'silver_satin', bev=.008)
    for s in (-1, 1):
        b.prism([(nx + .01, cy, desk_z), (nx - .13, cy + s * .155, desk_z), (nx - .15, cy + s * .13, desk_z),
                 (nx - .01, cy - s * .012, desk_z)], (0, 0, .012), 'silver_satin')


def flat_monitor(b, frame, w=.615, h=.365):
    """27-inch monitor in MB b, local frame: screen faces -X, centre of the back at the origin. Thin bezel, chin,
    tapered back with the VESA plate; screen blank."""
    b.at(frame)
    b.box((-.012, -w / 2, -h / 2), (0, w / 2, h / 2), 'black_matt', bev=.003)
    b.box((-.0125, -w / 2 + .007, -h / 2 + .02), (-.012, w / 2 - .007, h / 2 - .007), 'screen_black')
    b.box((0, -w / 2 + .03, -h / 2 + .03), (.03, w / 2 - .03, h / 2 - .04), 'black_matt', bev=.012)
    b.box((.03, -.055, -.055), (.045, .055, .055), 'black_matt', bev=.004)
    b.box((-.008, -.04, h / 2), (.022, .04, h / 2 + .028), 'black_matt', bev=.008)              # webcam
    b.box((-.0085, -.006, h / 2 + .01), (-.008, .006, h / 2 + .022), col('lens', '#202226', .2, 0))


# ------------------------------------------------------------------ architect desk lamp (hr_235)
def desk_lamp(b, base, elbow, head, tilt=35.0, M0=None):
    """Black spring-balanced architect lamp into MB b, points in the frame M0 (the MB's matrix, e.g. the room floor):
    C-clamp on the desk's front edge at base (x, y, z of the desk top), twin-rod lower and upper arms with springs,
    domed metal shade (black outside, white inside) hanging from head and tilted `tilt` degrees toward -X.
    Returns (centre of the lamp face inside the shade, shade axis) in the M0 frame."""
    blk, wh = 'black_matt', 'plastic_white'
    M0 = M0 if M0 is not None else Matrix.Identity(4)
    b.at(M0)
    x, y, z = base
    b.box((x - .012, y - .03, z - .085), (x, y + .03, z + .018), blk, bev=.003)                 # clamp back
    b.box((x - .012, y - .03, z), (x + .05, y + .03, z + .018), blk, bev=.003)                  # upper jaw
    b.box((x - .012, y - .03, z - .085), (x + .05, y + .03, z - .07), blk, bev=.003)            # lower jaw
    b.tube([(x + .03, y, z - .14), (x + .03, y, z - .07)], .005, blk, n=6)                     # screw
    b.box((x + .015, y - .015, z - .145), (x + .045, y + .015, z - .138), blk)
    p0 = Vector((x + .025, y, z + .018))
    b.tube([tuple(p0), tuple(p0 + Vector((0, 0, .05)))], .013, blk, n=12)                      # swivel post
    p0 = p0 + Vector((0, 0, .06))
    def arm(a, c):
        a, c = Vector(a), Vector(c)
        u = (c - a).normalized()
        s = u.cross(Vector((0, 0, 1)))
        s = (s if s.length > 1e-6 else Vector((1, 0, 0))).normalized()
        for k in (-1, 1):
            b.tube([tuple(a + s * k * .011), tuple(c + s * k * .011)], .0042, blk, n=6)
        b.tube([tuple(a + s * .026 + u * .06), tuple(a + s * .026 + u * .22)], .0065, blk, n=8)   # spring
        b.at(M0 @ Matrix.Translation(a) @ Vector((0, 0, 1)).rotation_difference(s).to_matrix().to_4x4())
        b.lathe([(0, -.016), (.017, -.016), (.017, .016), (0, .016)], blk, 12)                  # joint knuckle
        b.at(M0)
    arm(p0, elbow)
    arm(elbow, head)
    hv = Vector(head)
    ax = Vector((math.sin(math.radians(tilt)), 0, math.cos(math.radians(tilt))))                # shade 'up'
    rim = hv - ax * .125
    fr = M0 @ Matrix.Translation(rim) @ R('Y', tilt)
    b.at(M0 @ Matrix.Translation(hv) @ R('Y', tilt))
    b.lathe([(0, -.012), (.012, -.012), (.012, .012), (0, .012)], blk, 10)                      # head knuckle
    b.at(fr)
    out = [(.081, 0), (.08, .03), (.074, .06), (.062, .088), (.045, .108), (.025, .12), (.012, .125)]
    b.lathe(out, P.two_sided('black_matt'), 20)
    inn = [(.0105, .121), (.023, .116), (.043, .104), (.059, .085), (.071, .058), (.0765, .03), (.0775, .002)]
    b.lathe(inn, wh, 20)
    b.lathe([(.0775, .0), (.081, .0), (.081, .002), (.0775, .002)], blk, 20)                    # rolled rim
    b.lathe([(0, .088), (.026, .088), (.03, .098), (.02, .11), (0, .112)], col('lampholder', '#D9D6CE', .5), 12)
    b.at(M0)
    return rim + ax * .088, ax


# ------------------------------------------------------------------ rustic oak bookcase (v12 f4-6, f64; hr_252)
def bookcase(name, W=.90, D=.30, H=1.06):
    """Open bookcase with framed-panel ends, recessed plinth, bottom board and two shelves, tongue-and-groove back and
    a thick top with rounded front corners. Local: x across (centre 0), back at y 0, front +Y, floor z 0."""
    b, oak = mo.MB(), 'oak_rustic'
    groove = col('groove', '#3B2C1E', .8)
    hw, t, top = W / 2, .025, .045
    zt = H - top
    for s in (-1, 1):
        xo, xi = s * hw, s * (hw - t)
        lo, hi = min(xo, xi), max(xo, xi)
        b.box((lo, 0, 0), (hi, .05, zt), oak, bev=.003)                                         # back stile
        b.box((lo, D - .055, 0), (hi, D, zt), oak, bev=.003)                                    # front stile
        b.box((lo, .05, zt - .065), (hi, D - .055, zt), oak, bev=.002)                          # top rail
        b.box((lo, .05, 0), (hi, D - .055, .16), oak, bev=.002)                                 # bottom rail
        pin = (lo, hi - .007) if s > 0 else (lo + .007, hi)                     # panel set back 7 mm from the outside
        b.box((pin[0], .05, .16), (pin[1], D - .055, zt - .065), oak)
        bl, bh = (s * (hw - .007), s * (hw - .002)) if s > 0 else (s * (hw - .002), s * (hw - .007))
        bl, bh = min(bl, bh), max(bl, bh)
        for ya, yb, za, zb in ((.05, .059, .16, zt - .065), (D - .064, D - .055, .16, zt - .065),
                               (.059, D - .064, .16, .169), (.059, D - .064, zt - .074, zt - .065)):
            b.box((bl, ya, za), (bh, yb, zb), oak)                                              # panel bead
    b.box((-hw + t, D - .045, 0), (hw - t, D - .025, .075), oak, bev=.002)                     # recessed plinth
    b.box((-hw + t, .012, .075), (hw - t, D - .02, .095), oak, bev=.002)                      # bottom board
    for z in (.405, .72):
        b.box((-hw + t, .012, z), (hw - t, D - .028, z + .022), oak, bev=.002)                 # shelves
        b.box((-hw + t, D - .028, z - .012), (hw - t, D - .008, z + .024), oak, bev=.003)      # front lips
    b.box((-hw + t, 0, .075), (hw - t, .012, zt), oak)                                         # T&G back
    nb = 7
    for k in range(1, nb):
        x = -hw + t + (W - 2 * t) * k / nb
        b.box((x - .0015, .012, .095), (x + .0015, .013, zt), groove)
    r, pts = .035, [(-hw - .02, -.005), (hw + .02, -.005)]                                   # top: rounded front corners
    for cx, a0 in ((hw + .02 - r, 0), (-hw - .02 + r, 90)):
        for k in range(7):
            a = math.radians(a0 + 90 * k / 6)
            pts.append((cx + r * math.cos(a), D + .02 - r + r * math.sin(a)))
    b.prism([(px, py, zt) for px, py in pts], (0, 0, top), oak, grain=0)
    return b.finish(name)


# ------------------------------------------------------------------ piano stool (hr_183, hr_235)
def stool(name, stripe_mat):
    """Piano stool 0.36 x 0.56 x 0.49: dark mahogany box with a hinged padded lid in the cream / mauve striped cover,
    two brass hinge plates on the lid edge, square tapered legs splayed a little. Local: long axis along Y, origin
    floor centre."""
    b, wood = mo.MB(), 'mahogany_dark'
    L, Wd = .28, .18
    b.box((-Wd, -L, .30), (Wd, L, .415), wood, bev=.004)                                      # box with apron
    b.box((-Wd - .006, -L - .006, .412), (Wd + .006, L + .006, .43), wood, bev=.004)          # lid board
    for k in (-1, 1):                                                                         # lid hinges (seen front)
        b.box((-Wd - .003, k * .18 - .022, .394), (-Wd, k * .18 + .022, .411), 'brass')
    for sx in (-1, 1):
        for sy in (-1, 1):
            top = Vector((sx * (Wd - .022), sy * (L - .022), .30))
            foot = Vector((sx * (Wd + .002), sy * (L + .01), 0))
            c = {}
            for kk, (p, h) in enumerate(((foot, .013), (top, .021))):
                for i, ox in enumerate((-1, 1)):
                    for j, oy in enumerate((-1, 1)):
                        c[(i, j, kk)] = (p.x + ox * h, p.y + oy * h, p.z)
            solid8(b, c, wood)
    ob = b.finish(name)
    pad = P.upholstered_seat(.372, .572, .058, mat=stripe_mat, crown=.01, name=name + '.pad')
    pad.parent, pad.location = ob, (0, 0, .43)
    return ob


# ------------------------------------------------------------------ PC tower (hr_183)
def pc_tower(name):
    """Black gloss mid tower 0.23 x 0.50 x 0.50 with a smoked glass side toward the room, top vent, front I/O and a
    small green status light. Local: origin floor centre, front -Y, glass side -X."""
    b = mo.MB()
    b.box((-.115, -.25, .012), (.115, .25, .51), 'black_gloss', bev=.006)
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.box((sx * .09 - .012, sy * .21 - .012, 0), (sx * .09 + .012, sy * .21 + .012, .014), 'black_matt')
    b.box((-.1165, -.235, .03), (-.115, .235, .49), 'glass_dark')                             # smoked side panel
    b.box((-.06, -.2, .51), (.06, .18, .513), col('vent', '#151517', .8))                     # top mesh
    b.box((-.03, -.2515, .44), (.03, -.25, .47), col('io', '#202024', .6))
    b.box((-.004, -.2525, .475), (.004, -.25, .483), P.emissive('#7CF08C', 4.0))              # status light
    return b.finish(name)


# ------------------------------------------------------------------ Chippendale side chair on claw feet (hr_252)
def chippendale(name):
    """The dining set's side chair (rooms.dining_chairs) as it stands in this room: cabriole front legs on ball-and-claw
    feet (hr_252, spec 6) in place of the side chair's straight reeded legs and H-stretcher, which hr_252 does not show.
    A copy of the shared side-chair mesh with the parts below the seat frame that stand forward of the back legs
    removed; the legs are the carvers' (dining_chairs.chair(arm=True)), parented. Local: faces -Y, origin floor centre."""
    from rooms import dining_chairs as C
    from rooms.dining_furniture import dark_wood
    src = C.chair(name + '.src')
    me = src.data.copy()
    bpy.data.objects.remove(src)
    bm = bmesh.new()
    bm.from_mesh(me)
    seen, drop = set(), []
    for v0 in bm.verts:                                  # mesh islands: drop those wholly under the seat frame
        if v0 in seen:
            continue
        isl, stack = [], [v0]
        seen.add(v0)
        while stack:
            v = stack.pop()
            isl.append(v)
            for e in v.link_edges:
                w = e.other_vert(v)
                if w not in seen:
                    seen.add(w)
                    stack.append(w)
        if max(v.co.z for v in isl) <= .401 and min(v.co.y for v in isl) < .20:
            drop += isl
    bmesh.ops.delete(bm, geom=drop, context='VERTS')
    bm.to_mesh(me)
    bm.free()
    me.name = 'loft_office.chippendale'
    ob = bpy.data.objects.new(name, me)
    wf, d = .265, .25                                    # side chair: half front width, half depth
    for i, s in enumerate((-1, 1)):
        leg = P.turned_leg(.447, .062, 'cabriole', .065, 0, dark_wood(), out=(s, -1), foot='claw',
                           name=f'{name}.leg.{i}')
        leg.parent = ob
        leg.location = (s * (wf - .031), -d + .031, 0)
    return ob

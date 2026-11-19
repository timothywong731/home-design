"""Living room: light fittings and ornaments (imported by rooms/living.py). Conventions as living_parts."""
import math
import os
import random
from math import sin, cos, pi, radians, tau
import bpy
from mathutils import Matrix, Vector
from lib import materials as M, mouldings as mo, props as P
from living_parts import (Tr, Rz, Rx, Ry, MIRX, kid, loft, rrect, circ, slab, _face, tube_var, rtube, crystal, brass,
                          _bsdf, ART)


def sphere(mb, c, r, mat, n=10, sy=1.0, sz=1.0):
    k = max(5, n // 2)                           # latitude bands follow the segment count: no faceted rings
    prof = [(r * sin(pi * i / k), -r * cos(pi * i / k)) for i in range(k + 1)]
    prof[0], prof[-1] = (0, -r), (0, r)
    old = mb.M.copy()
    mb.at(old @ Tr(*c) @ Matrix.Diagonal((1, sy, sz, 1)))
    mb.lathe(prof, mat, n)
    mb.at(old)


def frame(p, ydir, zhint):
    """4x4 with origin p, local +Y along ydir, local +Z as close to zhint as possible."""
    y = Vector(ydir).normalized()
    x = y.cross(Vector(zhint))
    if x.length < 1e-5:
        x = y.cross(Vector((1, 0, 0)))
    x.normalize()
    z = x.cross(y)
    m = Matrix((x, y, z)).transposed().to_4x4()
    m.translation = Vector(p)
    return m


def bez(p0, p1, p2, p3, n=10):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3
        out.append(tuple(a * Vector(p0) + b * Vector(p1) + c * Vector(p2) + d * Vector(p3)))
    return out


# ------------------------------------------------------------------------------------------ sconce
SCONCE_CUPS = [(-0.25, -0.10, 0.03), (-0.135, -0.19, 0.10), (0.0, -0.14, 0.17), (0.135, -0.19, 0.10), (0.25, -0.10, 0.03)]


def sconce(name='living.sconce'):
    """Five-light gilt tole 'flowering branch' bracket, 0.55 x 0.50 x 0.22: leafy stems gathered by a ribbon
    bow, frosted tulip cups, flame-tip candle lamps. Antique gold with a dark patina: stems and leaves dark
    bronze, brighter gilt only on the flowers, bow and cup holders. Origin: wall, centre of the fitting;
    front -Y. Returns the root; the glass cups and the candle lamps are children."""
    mb = mo.MB()
    G = M.mat('bronze_antique')                                     # stems, leaves: dark recesses
    F = M.mat('gilt')                                               # flowers, bow, cup holders: brighter gilt
    K = Vector((0, -0.035, -0.20))
    for sx in (-1, 1):                                              # ribbon bow + tails, short wall stem
        loop = [(K.x + sx * 0.05 * (1 - cos(a)) * 0.9, K.y - 0.006, K.z + 0.028 * sin(a)) for a in
                (tau * k / 12 for k in range(13))]
        rtube(mb, loop, 0.0045, F, 5)
        rtube(mb, bez(K, K + Vector((sx * 0.02, -0.01, -0.03)), K + Vector((sx * 0.045, -0.01, -0.05)),
                       K + Vector((sx * 0.04, 0.0, -0.085)), 6), 0.004, F, 5)
    sphere(mb, K, 0.014, F, 8)
    mb.tube([K, (0, 0, -0.20)], 0.006, G, 6)
    mb.at(Tr(0, 0, -0.20) @ Rx(90))
    mb.lathe([(0, 0), (0.028, 0), (0.028, 0.003), (0.012, 0.008), (0, 0.008)], G, 10)
    mb.at()
    for sx, hgt in ((-1, 0.20), (1, 0.20), (-0.35, 0.27), (0.35, 0.27)):       # leafy sprigs between the arms
        tip = K + Vector((sx * 0.13, -0.05, hgt))
        sprig = bez(K, K + Vector((sx * 0.02, -0.03, 0.08)), tip - Vector((sx * 0.03, 0, 0.07)), tip, 8)
        rtube(mb, sprig, 0.0035, G, 5)
        for j, t in enumerate((2, 4, 6, 8)):
            p = Vector(sprig[t])
            tan = (Vector(sprig[t]) - Vector(sprig[t - 1])).normalized()
            side = Vector((1 if j % 2 else -1, -0.3, 0))
            mb.at(frame(p, (tan * 0.8 + side * 0.6).normalized(), (0, -1, 0.3)))
            mb.leaf(0.08 - 0.006 * j, 0.024, 0.005, G, 4, round_=1.0, curl=1.5)
        mb.at()
    cups = mo.MB()
    for i, c in enumerate(SCONCE_CUPS):
        c = Vector(c)
        mb.at()
        stem = bez(K, K + Vector((c.x * 0.15, c.y * 0.5, 0.10)), Vector((c.x * 1.12, c.y * 1.05, c.z - 0.15)),
                   c + Vector((0, 0, -0.03)), 12)
        rtube(mb, stem, 0.0042, G, 5)
        sgn = 1 if c.x >= 0 else -1
        for j, t in enumerate((2, 3, 4, 5, 6, 7, 8, 9, 10)):             # lanceolate leaves alternate along the stem
            p = Vector(stem[t])
            tan = (Vector(stem[t + 1]) - Vector(stem[t - 1])).normalized()
            side = Vector((sgn, 0, 0)) if j % 2 == 0 else Vector((-sgn * 0.6, -0.5, 0.2))
            d = (tan * 0.75 + side.normalized() * 0.65).normalized()
            mb.at(frame(p, d, (0, -1, 0.3)))
            mb.leaf(0.095 - 0.004 * j, 0.026, 0.005, G, 4, round_=1.0, curl=1.5)
        for t, off in ((4, (0.03 * sgn, -0.02, 0.0)), (8, (-0.025 * sgn, -0.015, 0.01))):   # five-petal flowers
            p = Vector(stem[t]) + Vector(off)
            mb.at()
            rtube(mb, [stem[t], tuple(p)], 0.0025, G, 4)
            for q in range(5):
                mb.at(frame(p, (cos(tau * q / 5), 0.25, sin(tau * q / 5)), (0, -1, 0)))
                mb.leaf(0.016, 0.012, 0.002, F, 3, round_=0.6)
            mb.at()
            sphere(mb, p + Vector((0, -0.003, 0)), 0.004, F, 6)
        mb.at(Tr(c.x, c.y, c.z - 0.03))
        mb.lathe([(0, 0), (0.008, 0), (0.014, 0.008), (0.02, 0.011), (0.02, 0.013), (0.006, 0.014), (0, 0.014)], F, 10)
        cups.at(Tr(c.x, c.y, c.z - 0.017))
        cups.lathe([(0.009, 0), (0.024, 0.007), (0.033, 0.024), (0.033, 0.044), (0.038, 0.06), (0.045, 0.068)],
                   P.two_sided(M.mat('glass_frosted')), 10)
    mb.at()
    root = mb.finish(name)
    glass = cups.finish(name + '.cups')
    glass.parent = root
    for i, c in enumerate(SCONCE_CUPS):
        kid(root, P.candle_bulb(0.075, 0.02, name=f'{name}.candle.{i}'), (c[0], c[1], c[2] - 0.016))
    return root


# -------------------------------------------------------------------------------------- table lamp
def toile():
    """Lamp-shade cloth: coral floral toile on cream. Both maps are generated (reference/work/living/fix1/
    gen_tex.py), not reference crops: toile.jpg = the print, toile_glow.jpg = the same print pre-warmed, used
    as the emission map of the lit shade (emissive colours are seen through the 3000 K view white balance).
    One repeat = a quarter of the shade's bottom rim."""
    m = M.image_mat('living_toile', os.path.join(ART, 'toile.jpg'), size_m=(0.2663, 0.2663), roughness=0.9)
    b = _bsdf(m)
    if not b.inputs['Emission Color'].links:
        t = m.node_tree.nodes.new('ShaderNodeTexImage')
        t.image = bpy.data.images.load(os.path.join(ART, 'toile_glow.jpg'), check_existing=True)
        m.node_tree.links.new(t.outputs['Color'], b.inputs['Emission Color'])
        b.inputs['Emission Strength'].default_value = 0.75
    return P.two_sided(m)


def table_lamp(name='living.table_lamp'):
    """Salmon alabaster urn lamp with ormolu mounts, 0.78 high with its bell shade (top 0.24, bottom 0.34,
    height 0.27) in cream cloth printed with a coral floral toile."""
    mb = mo.MB()
    G = brass()
    A = M.solid('living_alabaster_pink', '#C99A7A', 0.3)
    mb.lathe([(0, 0), (0.085, 0), (0.085, 0.012), (0.08, 0.016), (0, 0.016)], A, 20)
    mb.lathe([(0, 0.016), (0.078, 0.016), (0.08, 0.026), (0.062, 0.034), (0.04, 0.05), (0.03, 0.066), (0.034, 0.074), (0, 0.074)], G, 16)
    mb.lathe([(0, 0.072), (0.03, 0.072), (0.046, 0.10), (0.06, 0.15), (0.066, 0.205), (0.06, 0.25), (0.04, 0.285),
              (0.03, 0.30), (0, 0.30)], A, 20)
    mb.lathe([(0, 0.296), (0.036, 0.296), (0.04, 0.306), (0.03, 0.318), (0.016, 0.33), (0.012, 0.36), (0.012, 0.455),
              (0.02, 0.462), (0.02, 0.50), (0, 0.50)], G, 12)
    for k in range(6):                                              # rose garland round the belly
        a0, a1 = tau * k / 6, tau * (k + 1) / 6
        pts = []
        for i in range(7):
            t = i / 6
            a = a0 + (a1 - a0) * t
            pts.append((0.068 * cos(a), 0.068 * sin(a), 0.225 - 0.03 * sin(pi * t)))
        mb.tube(pts, 0.005, G, 5)
        sphere(mb, (0.07 * cos(a0), 0.07 * sin(a0), 0.228), 0.009, G, 6)
    for sx in (-1, 1):                                              # figure handles reduced to scrolled mounts
        pts = [(sx * (0.045 + 0.03 * sin(pi * t) + 0.012 * sin(tau * t)), 0, 0.285 - 0.12 * t) for t in (i / 8 for i in range(9))]
        tube_var(mb, pts, [0.006, 0.009, 0.011, 0.01, 0.008, 0.008, 0.009, 0.007, 0.004], G, 6)
        sphere(mb, (sx * 0.058, 0, 0.295), 0.012, G, 8)
    root = mb.finish(name)
    sh = mo.MB()                                                    # round bell shade; the trim follows the rims
    n = 24
    rings = [[(r * cos(tau * k / n), r * sin(tau * k / n), z) for k in range(n)]
             for r, z in ((0.17, 0.0), (0.159, 0.06), (0.146, 0.13), (0.132, 0.20), (0.12, 0.27))]
    sh._soft = 1
    loft(sh, rings, toile(), caps=(False, False))
    sh._soft = 0
    for ring in (rings[0], rings[-1]):
        sh.tube(ring, 0.0028, G, 4, closed=True)
    for k in range(3):                                              # spider to the lamp holder, inside the top rim
        a = tau * k / 3
        sh.tube([(0, 0, 0.245), (0.119 * cos(a), 0.119 * sin(a), 0.268)], 0.0015, G, 3)
    shade = sh.finish(name + '.shade')
    kid(root, shade, (0, 0, 0.51))
    return root


# ------------------------------------------------------------------------------------- A/V on the unit
def amplifier(name='living.amplifier'):
    """Valve amplifier 0.43 x 0.33 x 0.19: champagne-silver fascia with two VU meters and knobs, perforated
    black valve cage (bar lattice over a gloss-black inset) and three transformer cans. Front -Y, origin
    bottom centre."""
    mb = mo.MB()
    S, Bk = M.solid('living_amp_champagne', '#CDC7B6', 0.3, 1), M.mat('black_matt')
    mb.box((-0.215, -0.15, 0.008), (0.215, 0.165, 0.075), M.mat('silver_satin'), bev=0.002)
    mb.box((-0.215, -0.165, 0.004), (0.215, -0.15, 0.085), S, bev=0.003)
    for sx in (-1, 1):
        mb.box((sx * 0.085 - 0.04, -0.1665, 0.03), (sx * 0.085 + 0.04, -0.1648, 0.072), Bk)
        mb.box((sx * 0.085 - 0.034, -0.1675, 0.035), (sx * 0.085 + 0.034, -0.166, 0.067), M.solid('living_vu_dial', '#E9D9A6', 0.4))
        mb.at(Tr(sx * 0.175, -0.165, 0.045) @ Rx(90))
        mb.lathe([(0, 0), (0.016, 0), (0.016, 0.014), (0.013, 0.018), (0, 0.018)], S, 12)
        mb.at()
        for sy in (-1, 1):
            mb.at(Tr(sx * 0.19, sy * 0.13 + 0.0075, 0))
            mb.lathe([(0, 0), (0.012, 0), (0.012, 0.008), (0, 0.008)], Bk, 8)
            mb.at()
    x0, x1, y0, y1, z0, z1 = -0.19, 0.19, -0.13, 0.03, 0.075, 0.17
    mb.box((x0 + 0.003, y0 + 0.003, z0), (x1 - 0.003, y1 - 0.003, z1 - 0.003), M.mat('black_gloss'))   # dark behind the mesh
    for x in (x0, x1 - 0.006):                                                          # cage corner posts, top frame
        for y in (y0, y1 - 0.006):
            mb.box((x, y, z0), (x + 0.006, y + 0.006, z1), Bk)
    for k in range(20):                                                                 # perforated cage: bar lattice
        x = x0 + 0.006 + (x1 - x0 - 0.012) * (k + 0.5) / 20
        mb.box((x - 0.0035, y0, z0), (x + 0.0035, y0 + 0.002, z1), Bk)                  # front
        mb.box((x - 0.0035, y0, z1 - 0.002), (x + 0.0035, y1, z1), Bk)                  # top
    for k in range(5):
        z = z0 + (z1 - z0) * (k + 0.5) / 5
        mb.box((x0, y0, z - 0.0035), (x1, y0 + 0.0022, z + 0.0035), Bk)
    for k in range(8):
        y = y0 + (y1 - y0) * (k + 0.5) / 8
        mb.box((x0, y - 0.0035, z1 - 0.0022), (x1, y + 0.0035, z1 + 0.0002), Bk)
        for x in (x0, x1 - 0.002):                                                      # sides: vertical slots
            mb.box((x, y - 0.0035, z0), (x + 0.002, y + 0.0035, z1), Bk)
    for k in range(3):
        mb.at(Tr(-0.13 + 0.13 * k, 0.10, 0.075))
        mb.lathe([(0, 0), (0.05, 0), (0.05, 0.105), (0.044, 0.113), (0, 0.113)], Bk, 14)
    mb.at()
    return mb.finish(name)


def speaker(name='living.speaker'):
    """Black bookshelf speaker 0.21 x 0.33 x 0.27 with its cloth grille on: the library box (which always shows
    a bare woofer) behind a flat grille frame standing 12 mm proud of the baffle. Origin bottom centre, front -Y."""
    root = P.speaker_box(drivers=0, name=name)
    mb = mo.MB()
    mb.box((-0.101, -0.012, 0.004), (0.101, 0.0, 0.326), M.solid('living_grille_cloth', '#141414', 1.0), bev=0.004)
    kid(root, mb.finish(name + '.grille'), (0, -0.27, 0))
    return root


def disc_player(name='living.disc_player'):
    mb = mo.MB()
    mb.box((-0.215, -0.14, 0.006), (0.215, 0.14, 0.066), M.mat('black_matt'), bev=0.002)
    mb.box((-0.20, -0.1412, 0.03), (0.06, -0.1398, 0.042), M.mat('black_gloss'))
    mb.box((0.12, -0.1412, 0.03), (0.19, -0.1398, 0.036), M.mat('silver_satin'))
    return mb.finish(name)


def xiangqi(name='living.xiangqi'):
    """Chinese chess board 0.38 x 0.42 in pale wood with the 32 dark-red round pieces set out."""
    mb = mo.MB()
    red = M.solid('living_xiangqi_red', '#6B211B', 0.35)
    mb.box((-0.19, -0.21, 0), (0.19, 0.21, 0.018), 'oak_light', bev=0.002, grain=1)
    dx, dy = 0.04, 0.04
    spots = [(c, 0) for c in range(9)] + [(1, 2), (7, 2)] + [(c, 3) for c in (0, 2, 4, 6, 8)]
    spots += [(c, 9 - r) for c, r in spots]
    for c, r in spots:
        mb.at(Tr((c - 4) * dx, (r - 4.5) * dy, 0.018))
        mb.lathe([(0, 0), (0.015, 0), (0.016, 0.003), (0.016, 0.007), (0.014, 0.0095), (0, 0.0095)], red, 10)
    mb.at()
    return mb.finish(name)


# ------------------------------------------------------------------------------- ornaments
def diamond_cut(mb, pt, nu, nv, h, mat, wrap=False):
    """Diamond-cut (hobnail) crystal relief on a (nu x nv)-step lattice. pt(i, j, lift) -> 3D point of node
    (i, j) pushed `lift` out of the surface; nodes with i + j even are pyramid apexes (lift h), the others and
    the border stay on the surface, and every cell is split along its low diagonal, so the pyramids stand on
    diamond bases. u x v must point out of the surface. wrap = the lattice closes on itself in i (nu even).
    Every facet has its own vertices, so it is flat-shaded whatever the angle: the sparkle is geometry."""
    mi = mb.mi(mat)
    cols = nu if wrap else nu + 1

    def lift(i, j):
        return 0.0 if (i + j) % 2 or j in (0, nv) or (not wrap and i in (0, nu)) else h
    V = [[pt(i, j, lift(i, j)) for j in range(nv + 1)] for i in range(cols)]
    for i in range(nu):
        i2 = (i + 1) % cols
        for j in range(nv):
            a, b, c, d = V[i][j], V[i2][j], V[i2][j + 1], V[i][j + 1]
            for tri in (((a, b, d), (b, c, d)) if (i + j) % 2 == 0 else ((a, b, c), (a, c, d))):
                _face(mb, mb._vs(tri), mi)                           # own vertices: every facet flat


def CUT():
    """Cut table crystal (decanters, tumblers, stem glasses): denser than plain glass with a faint lift, so the
    facets read white and sparkling as in f_0148 / f_0194 instead of as grey ghosts."""
    return crystal(0.36, 'living_crystal_cut', glow=0.07)


def cut_decanter(name='living.cut_decanter', liquid=False):
    """Square hobnail-cut crystal decanter 74 x 74 x 213 mm: diamond-cut relief on the four faces, plain
    chamfered arrises, sloping shoulders, round neck with a lip and a faceted ball stopper. liquid = whisky
    filling 55 % of the body as a prism 4 mm inside the glass. Origin base centre."""
    mb = mo.MB()
    G = CUT()
    a, c, z0, z1 = 0.037, 0.004, 0.010, 0.100

    def ring(z, s=1.0, n=16):                                        # chamfered square sampled on n rays
        out = []
        for k in range(n):
            t = tau * (k + 0.5) / n
            r = min(a / max(abs(cos(t)), abs(sin(t))), (2 * a - c) / (abs(cos(t)) + abs(sin(t))))
            out.append((s * r * cos(t), s * r * sin(t), z))
        return out

    def rnd(r, z, n=16):
        return [(r * cos(tau * (k + 0.5) / n), r * sin(tau * (k + 0.5) / n), z) for k in range(n)]
    for k in range(4):
        mb.at(Rz(90 * k))
        diamond_cut(mb, lambda i, j, l: (-(a - c) + 2 * (a - c) * i / 10, -a - l, z0 + (z1 - z0) * j / 14), 10, 14, 0.0035, G)
        mb.face([(a - c, -a, z0), (a, -(a - c), z0), (a, -(a - c), z1), (a - c, -a, z1)], G, (1, -1, 0))   # plain arris
    mb.at()
    loft(mb, [ring(0.0, 0.93), ring(0.004), ring(z0)], G, caps=(True, False))
    loft(mb, [ring(z1), ring(0.105), ring(0.113, 0.84), rnd(0.02, 0.123), rnd(0.0135, 0.130), rnd(0.0125, 0.146),
              rnd(0.0195, 0.150), rnd(0.0195, 0.154), rnd(0.011, 0.156)], G, caps=(False, True))
    mb.lathe([(0, 0.154), (0.009, 0.154), (0.009, 0.164), (0, 0.164)], G, 8)                           # stopper peg
    sphere(mb, (0, 0, 0.187), 0.0265, G, 10)                         # faceted ball (36 deg facets stay sharp)
    if liquid:
        b = a - 0.004
        mb.box((-b, -b, 0.006), (b, b, 0.006 + 0.55 * (z1 - 0.006)), M.solid('living_whisky', '#3A1C0C', 0.05))   # dark malt
    return mb.finish(name)


def tantalus(name='living.tantalus'):
    """Oak three-bottle tantalus 0.36 x 0.15 x 0.30 (f_0148): base board, low front board with brass corner
    straps and lock plate, two end boards with a serpentine front edge, a top locking bar with two small brass
    knobs; three square hobnail-cut decanters, the first half full of whisky; key tassel."""
    mb = mo.MB()
    W, B = 'dark_oak_antique', M.mat('bronze_antique')
    mb.box((-0.18, -0.075, 0), (0.18, 0.075, 0.03), W, bev=0.003, grain=0)                          # base board
    mb.box((-0.164, -0.07, 0.03), (0.164, -0.058, 0.108), W, bev=0.002, grain=0)                    # front board
    mb.box((-0.164, 0.058, 0.03), (0.164, 0.066, 0.075), W, bev=0.002, grain=0)                     # low back rail
    side = [(-0.07, 0.03), (-0.07, 0.108), (-0.058, 0.118), (-0.044, 0.136), (-0.037, 0.158), (-0.04, 0.18), (-0.047, 0.198),
            (-0.047, 0.214), (-0.038, 0.232), (-0.03, 0.254), (-0.03, 0.288), (-0.022, 0.296), (0.035, 0.296), (0.046, 0.288),
            (0.07, 0.24), (0.07, 0.03)]                                                             # (y, z): serpentine front
    for sx in (-1, 1):
        x0 = 0.164 if sx > 0 else -0.18
        loft(mb, [[(x0 + dx, y, z) for y, z in side] for dx in (0.0, 0.016)], W)
        for z, hgt in ((0.04, 0.015), (0.084, 0.015)):                                              # dark brass corner straps
            mb.box((sx * 0.1815, -0.0715, z), (sx * 0.154, -0.0705, z + hgt), B)
            mb.box((sx * 0.1815, -0.0715, z), (sx * 0.1805, -0.048, z + hgt), B)
    mb.box((-0.166, -0.022, 0.262), (0.166, 0.022, 0.288), W, bev=0.003, grain=0)                   # locking bar
    for sx in (-1, 1):                                                                              # brass knobs on the bar
        mb.at(Tr(sx * 0.04, 0, 0.288))
        mb.lathe([(0, 0), (0.008, 0), (0.008, 0.002), (0.0035, 0.004), (0.0035, 0.008), (0.0075, 0.012), (0.0065, 0.017), (0, 0.019)],
                 B, 10)
    mb.at()
    mb.box((-0.011, -0.0712, 0.066), (0.011, -0.0698, 0.094), B)                                    # lock plate
    root = mb.finish(name)
    full = cut_decanter(name + '.decanter.0', liquid=True)
    empty = cut_decanter(name + '.decanter.1')
    kid(root, full, (-0.108, 0, 0.03))
    kid(root, empty, (0.0, 0, 0.03), (0, 0, 90))
    kid(root, bpy.data.objects.new(name + '.decanter.2', empty.data), (0.108, 0, 0.03))
    kid(root, P.tassel(0.07, 0.012, mat=M.solid('living_key_tassel', '#A08A4A', 0.8), name=name + '.tassel'), (0.004, -0.079, 0.07))
    return root


def bird(name='living.bird'):
    """Long-billed brown wader perched on a gnarled driftwood branch, stepped wooden base 0.22 x 0.14; 0.42 high.
    Smooth-shaded: slim body, long neck, slightly down-curved 65 mm bill, folded wings, tail, thin legs."""
    mb = mo.MB()
    wood = M.solid('living_driftwood', '#B9AC98', 0.9)               # pale grey driftwood
    feath = M.solid('living_bird_breast', '#9A8566', 0.8)            # paler breast and flanks
    wing = M.solid('living_bird_back', '#4E3C2A', 0.8)               # dark back, wings, crown
    horn = M.solid('living_bird_bill', '#8C7850', 0.5)
    spot = M.solid('living_bird_speckle', '#33281C', 0.85)
    mb.box((-0.11, -0.07, 0), (0.11, 0.07, 0.022), 'oak_table', bev=0.003, grain=0)
    mb.box((-0.095, -0.058, 0.022), (0.095, 0.058, 0.04), 'oak_table', bev=0.004, grain=0)
    mb._soft = 1
    tube_var(mb, [(-0.055, 0.0, 0.036), (-0.05, 0.008, 0.07), (-0.03, 0.0, 0.105), (-0.022, -0.008, 0.14), (0.0, 0.0, 0.175),
                  (0.012, 0.006, 0.205), (0.03, 0.0, 0.232), (0.05, -0.004, 0.25)],
             [0.03, 0.023, 0.026, 0.019, 0.021, 0.015, 0.014, 0.009], wood, 12)                    # gnarled trunk
    tube_var(mb, [(-0.027, 0.0, 0.118), (-0.06, 0.012, 0.15), (-0.085, 0.005, 0.19), (-0.09, 0.0, 0.215)],
             [0.015, 0.012, 0.009, 0.005], wood, 10)
    tube_var(mb, [(0.0, 0.0, 0.17), (0.045, -0.015, 0.18), (0.085, -0.012, 0.172), (0.105, -0.01, 0.18)],
             [0.013, 0.011, 0.008, 0.004], wood, 10)
    tube_var(mb, [(-0.04, 0.004, 0.085), (-0.012, 0.03, 0.095), (0.01, 0.045, 0.085)], [0.013, 0.009, 0.004], wood, 8)
    tube_var(mb, [(-0.068, 0, 0.27), (-0.045, 0, 0.287), (-0.01, 0, 0.31), (0.025, 0, 0.332), (0.05, 0, 0.352), (0.064, 0, 0.371),
                  (0.074, 0, 0.386)], [0.006, 0.024, 0.036, 0.034, 0.024, 0.017, 0.016], feath, 14)   # body and neck
    sphere(mb, (0.083, 0, 0.395), 0.0225, feath, 14)
    tube_var(mb, [(0.10, 0, 0.397), (0.13, 0, 0.397), (0.158, 0, 0.392), (0.18, 0, 0.383)], [0.0052, 0.0036, 0.0026, 0.0014],
             horn, 8)                                                                               # long bill
    tube_var(mb, [(-0.05, 0, 0.283), (-0.095, 0, 0.258), (-0.135, 0, 0.24)], [0.018, 0.012, 0.003], wing, 10)   # tail
    for sy in (-1, 1):
        mb.at(Tr(-0.012, sy * 0.031, 0.311) @ Ry(-31))
        sphere(mb, (0, 0, 0), 0.062, wing, 14, sy=0.2, sz=0.4)                                      # folded wing
        mb.at()
        sphere(mb, (0.092, sy * 0.018, 0.4), 0.0035, M.mat('black_gloss'), 8)                       # eye
        rtube(mb, [(0.0, sy * 0.014, 0.29), (0.012, sy * 0.012, 0.268), (0.028, sy * 0.009, 0.247)], 0.0036, horn, 6)   # leg
        for q in (-1, 0, 1):                                                                        # toes gripping the branch
            rtube(mb, [(0.028, sy * 0.009, 0.247), (0.04 + 0.004 * abs(q), sy * 0.009 + q * 0.012, 0.243)], 0.0022, horn, 4)
    mb.at(Tr(-0.012, 0, 0.318) @ Ry(-31))                                                           # dark mantle over the back
    sphere(mb, (0, 0, 0), 0.058, wing, 14, sy=0.52, sz=0.42)
    mb.at()
    sphere(mb, (0.08, 0, 0.408), 0.016, wing, 12, sy=0.85, sz=0.62)                                 # dark crown
    rs = random.Random(2)
    axis = [(0.0, 0.316, 0.0355), (0.025, 0.332, 0.034), (0.05, 0.352, 0.024), (0.064, 0.371, 0.017), (0.074, 0.386, 0.016)]
    for _ in range(60):                                         # dark speckles on the breast and neck, ahead of the wings
        k = rs.randrange(len(axis) - 1)
        t = rs.random()
        (x0, z0, r0), (x1, z1, r1) = axis[k], axis[k + 1]
        cx, cz, rr = x0 + (x1 - x0) * t, z0 + (z1 - z0) * t, r0 + (r1 - r0) * t
        a = rs.uniform(0.7, 3.14) * rs.choice((-1, 1))                                              # 0 = top of the body
        sphere(mb, (cx - 0.64 * rr * cos(a), rr * sin(a), cz + 0.77 * rr * cos(a)), rs.uniform(0.0022, 0.0036), spot, 6, sz=0.6)
    for sy in (-1, 1):                                          # pale flecks on the folded wings
        for _ in range(26):
            u, w = rs.uniform(-0.8, 0.75), rs.uniform(-0.75, 0.75)
            if u * u + w * w > 0.8:
                continue
            mb.at(Tr(-0.012, sy * 0.031, 0.311) @ Ry(-31))
            sphere(mb, (0.062 * u, sy * 0.0124 * (1 - u * u - w * w) ** 0.5, 0.0248 * w), rs.uniform(0.002, 0.0032), feath, 6, sy=0.5)
    mb.at()
    mb._soft = 0
    return mb.finish(name)


def mercury(name='living.mercury'):
    """Bronze 'Flying Mercury' statuette (after Giambologna), 0.56 high on a black socle: a slender figure
    balanced on one toe, trailing leg bent back, one arm raised, winged cap, caduceus in the other hand.
    A stylised ornament built from smooth tapered limbs, not a likeness."""
    mb = mo.MB()
    Bz = M.solid('living_bronze_dark', '#3A3028', 0.34, 1)           # near-black patinated bronze (lib bronze_dark reads mid-brown)
    mb.lathe([(0, 0), (0.05, 0), (0.05, 0.006), (0.044, 0.012), (0.044, 0.075), (0.048, 0.082), (0, 0.082)], M.mat('black_gloss'), 24)
    mb._soft = 1
    n = 12
    sphere(mb, (0, 0, 0.097), 0.017, Bz, n)
    tube_var(mb, [(0.004, 0, 0.11), (-0.003, 0, 0.133), (0.0, 0, 0.185), (0.005, 0, 0.225), (0.0, 0, 0.28), (-0.002, 0.009, 0.325)],
             [0.0045, 0.0068, 0.012, 0.0105, 0.0165, 0.019], Bz, n)                                 # standing leg
    tube_var(mb, [(-0.002, -0.01, 0.322), (-0.045, -0.02, 0.276), (-0.09, -0.022, 0.286), (-0.125, -0.022, 0.271),
                  (-0.142, -0.022, 0.258)], [0.019, 0.012, 0.0095, 0.006, 0.0035], Bz, n)           # trailing leg
    tube_var(mb, [(-0.002, 0, 0.30), (0.0, 0, 0.325), (0.006, 0, 0.368), (0.016, 0, 0.415), (0.02, 0, 0.441), (0.024, 0, 0.458),
                  (0.027, 0, 0.47)], [0.02, 0.0245, 0.019, 0.027, 0.024, 0.0098, 0.009], Bz, n)     # torso, neck
    for sy in (-1, 1):
        sphere(mb, (0.02, sy * 0.022, 0.441), 0.0125, Bz, n)                                        # shoulders
    sphere(mb, (0.031, 0, 0.487), 0.02, Bz, n, sy=0.9)
    mb.at(Tr(0.031, 0, 0.495))
    mb.lathe([(0.0, 0.0), (0.027, 0.0), (0.02, 0.008), (0.012, 0.017), (0, 0.02)], Bz, n)            # petasos (cap)
    mb.at()
    tube_var(mb, [(0.02, -0.024, 0.441), (0.04, -0.032, 0.49), (0.047, -0.032, 0.535), (0.05, -0.032, 0.562)],
             [0.0105, 0.008, 0.0058, 0.003], Bz, n)                                                 # raised arm
    tube_var(mb, [(0.02, 0.024, 0.441), (-0.005, 0.036, 0.40), (0.025, 0.045, 0.375), (0.034, 0.047, 0.368)],
             [0.0105, 0.008, 0.006, 0.005], Bz, n)                                                  # arm with caduceus
    mb.tube([(0.045, 0.049, 0.325), (-0.012, 0.042, 0.475)], 0.0024, Bz, 6)
    sphere(mb, (-0.013, 0.042, 0.479), 0.005, Bz, 8)
    for sx in (-1, 1):
        mb.at(frame((-0.01, 0.042, 0.468), (sx * 0.8, 0, 0.5), (0, 1, 0)))
        mb.leaf(0.03, 0.012, 0.002, P.two_sided(Bz), 3)
        mb.at(frame((0.031, sx * 0.016, 0.50), (-0.5, sx * 0.6, 0.7), (1, 0, 0)))                   # wings on the cap
        mb.leaf(0.03, 0.013, 0.002, P.two_sided(Bz), 3)
        mb.at(frame((-0.125, -0.022 + sx * 0.005, 0.273), (-0.6, sx * 0.5, 0.7), (1, 0, 0)))        # winged heel
        mb.leaf(0.02, 0.009, 0.002, P.two_sided(Bz), 3)
    mb.at()
    mb._soft = 0
    return mb.finish(name)


def cat(name='living.cat'):
    """White porcelain reclining long-haired cat, 0.25 long: one smooth body, ruff, raised round head with
    small ears, paws stretched forward, fluffy tail curled along the flank."""
    mb = mo.MB()
    C = M.mat('ceramic_white')
    mb._soft = 1
    n = 16
    tube_var(mb, [(-0.108, 0, 0.034), (-0.09, 0, 0.042), (-0.06, 0, 0.047), (-0.02, 0, 0.049), (0.02, 0, 0.049), (0.05, 0, 0.052),
                  (0.07, 0, 0.06), (0.082, 0, 0.07)], [0.012, 0.036, 0.046, 0.048, 0.046, 0.045, 0.04, 0.03], C, n)   # body, ruff
    sphere(mb, (0.086, 0, 0.094), 0.035, C, n, sy=1.08, sz=0.94)                                    # head
    sphere(mb, (0.112, 0, 0.086), 0.015, C, 12, sy=1.3, sz=0.8)                                     # muzzle
    for sy in (-1, 1):
        mb.at(Tr(0.08, sy * 0.022, 0.118) @ Rx(-sy * 18))
        mb.lathe([(0, -0.006), (0.011, -0.006), (0.007, 0.006), (0, 0.016)], C, 10)                 # ear
        mb.at()
        tube_var(mb, [(0.05, sy * 0.024, 0.017), (0.10, sy * 0.022, 0.013), (0.126, sy * 0.021, 0.011)], [0.016, 0.0125, 0.0105],
                 C, 12, caps=(False, False))
        sphere(mb, (0.128, sy * 0.021, 0.011), 0.0108, C, 12)                                       # paw
    tube_var(mb, [(-0.10, 0, 0.03), (-0.128, -0.03, 0.027), (-0.108, -0.066, 0.024), (-0.05, -0.074, 0.022), (-0.015, -0.068, 0.02)],
             [0.018, 0.021, 0.021, 0.018, 0.012], C, 12, caps=(False, False))                       # tail
    sphere(mb, (-0.013, -0.068, 0.02), 0.0122, C, 12)
    mb._soft = 0
    return mb.finish(name)


def flowers(name='living.flowers', seed=5):
    """Glass vase 0.26 high with a bunch of small multi-petal orange / red / pink flowers and leaves, 0.45 high."""
    rnd = random.Random(seed)
    mb = mo.MB()
    green = P.mat('leaf_green')
    leaf = P.two_sided(P.mat('leaf_mid'))
    cols = [P.two_sided(M.solid(f'living_petal_{i}', hx, 0.6)) for i, hx in enumerate(('#D4502C', '#E08A2E', '#D96A84', '#B8322E'))]
    eye = M.solid('living_flower_eye', '#6B4A1E', 0.7)
    for i in range(16):
        a = tau * i * 0.618 + rnd.uniform(-0.25, 0.25)
        tilt = radians(rnd.uniform(5, 34)) if i else 0.05
        h = rnd.uniform(0.33, 0.445)
        tip = Vector((sin(tilt) * cos(a) * (h - 0.1), sin(tilt) * sin(a) * (h - 0.1), h))
        if tip.y > 0:                                              # the vase stands against a wall: the back stems are upright
            tip.y *= 0.55
        foot = Vector((0.012 * cos(a + pi), 0.012 * sin(a + pi), 0.02))
        stem = bez(foot, foot + Vector((0, 0, 0.15)), tip - Vector((tip.x * 0.5, tip.y * 0.5, 0.1)), tip, 6)
        rtube(mb, stem, 0.002, green, 5)
        d = (Vector(stem[-1]) - Vector(stem[-2])).normalized()
        u = d.orthogonal().normalized()
        v = d.cross(u)
        col = cols[i % len(cols)]
        for ring, (npet, ln, lift) in enumerate(((8, 0.032, 0.25), (5, 0.021, 0.9))):               # two whorls of petals
            for q in range(npet):
                t = tau * (q + 0.5 * ring) / npet
                e = cos(t) * u + sin(t) * v
                mb.at(frame(tip, e + d * lift, d))
                mb.leaf(ln, ln * 0.62, 0.003, col, 3, round_=0.6)
        mb.at()
        sphere(mb, tip + d * 0.003, 0.0055, eye, 8)
        for t in (2, 3):                                                                            # leaves on the stem
            p = Vector(stem[t])
            e = (cos(a + t * 2.2) * Vector((1, 0, 0)) + sin(a + t * 2.2) * Vector((0, 1, 0)))
            mb.at(frame(p, e + Vector((0, 0, 0.7)), (0, 0, 1)))
            mb.leaf(0.065, 0.02, 0.004, leaf, 4, round_=1.0)
        mb.at()
    root = mb.finish(name)
    kid(root, P.vase(0.26, 0.12, 'cylinder', crystal(), name=name + '.vase'), (0, 0, 0))
    return root


CLOCK_DIAL, CLOCK_R = (0.0, -0.062, 0.133), 0.072      # clock(): dial centre on the dial plate (local), chapter-ring radius


def clock(name='living.clock'):
    """Antique bracket clock 0.26 x 0.15 x 0.30: brown walnut case on a moulded plinth, stepped top with a
    brass carrying handle, glazed door frame, square brass dial plate with a silvered chapter ring carrying
    thin black hour batons, matted centre and four gilt corner spandrels. No hands: rooms/living.py adds live
    ones (P.clock_hands at CLOCK_DIAL, radius CLOCK_R) under the brass centre boss. Origin bottom centre,
    front -Y."""
    mb = mo.MB()
    W, B, S, K, Gd = 'mahogany_dark', M.mat('brass'), M.mat('silver_satin'), M.mat('black_matt'), M.mat('brass')
    mb.box((-0.13, -0.075, 0), (0.13, 0.075, 0.022), W, bev=0.004, grain=0)                         # plinth
    mb.box((-0.12, -0.068, 0.022), (0.12, 0.068, 0.034), W, bev=0.004, grain=0)
    mb.box((-0.108, -0.06, 0.034), (0.108, 0.06, 0.232), W, bev=0.002, grain=2)                     # case
    mb.box((-0.122, -0.07, 0.232), (0.122, 0.07, 0.246), W, bev=0.004, grain=0)                     # cornice
    mb.box((-0.10, -0.056, 0.246), (0.10, 0.056, 0.262), W, bev=0.005, grain=0)                     # stepped top
    mb.box((-0.078, -0.044, 0.262), (0.078, 0.044, 0.276), W, bev=0.006, grain=0)
    rtube(mb, [(-0.04, 0, 0.276), (-0.04, 0, 0.288), (-0.028, 0, 0.2985), (0.028, 0, 0.2985), (0.04, 0, 0.288), (0.04, 0, 0.276)],
          0.0035, B, 6)
    yf, zc, hw = -0.06, 0.133, 0.08
    for x0, x1, z0, z1 in ((-0.098, -hw, 0.04, 0.226), (hw, 0.098, 0.04, 0.226), (-hw, hw, 0.04, zc - hw), (-hw, hw, zc + hw, 0.226)):
        mb.box((x0, yf - 0.009, z0), (x1, yf, z1), W, bev=0.002, grain=2 if x1 - x0 < 0.05 else 0)   # door frame
    mb.box((-hw, yf - 0.002, zc - hw), (hw, yf, zc + hw), B)                                        # dial plate
    D = Tr(0, yf - 0.002, zc) @ Rx(90)                                                              # dial plane: x right, y up, z out
    mb.at(D)
    mb.lathe([(0.046, 0), (0.072, 0), (0.072, 0.0012), (0.046, 0.0012)], S, 40)                     # silvered chapter ring
    mb.lathe([(0, 0), (0.046, 0), (0.046, 0.0008), (0, 0.0008)], M.mat('brass_antique'), 32)        # matted centre
    for h in range(12):
        mb.at(D @ Rz(30 * h))
        w = 0.0042 if h % 3 == 0 else 0.0026                                                        # bold hour marks, no text
        mb.box((-w, 0.050, 0.0012), (w, 0.069, 0.002), K)
    mb.at(D)
    mb.lathe([(0, 0.002), (0.005, 0.002), (0.005, 0.0045), (0, 0.0045)], B, 10)
    for sx in (-1, 1):
        for sz in (-1, 1):                                                                          # corner spandrels
            for da in (-48, 0, 48):
                mb.at(D @ Tr(sx * 0.047, sz * 0.047, 0.0002) @ Rz(math.degrees(math.atan2(-sx, sz)) + da))
                mb.leaf(0.034 if da == 0 else 0.028, 0.016, 0.0045, Gd, 3, round_=0.8)
            mb.at(D @ Tr(sx * 0.066, sz * 0.066, 0.0))
            mb.dome(0.006, 0.006, 0.004, Gd, 8, 2)                                                   # raised corner boss
    mb.at()
    root = mb.finish(name)
    g = mo.MB()
    g.face([(-hw, yf - 0.007, zc - hw), (hw, yf - 0.007, zc - hw), (hw, yf - 0.007, zc + hw), (-hw, yf - 0.007, zc + hw)],
           M.mat('glass_clear'), (0, -1, 0))
    kid(root, g.finish(name + '.glass'), (0, 0, 0))
    return root


def tea_tray(name='living.tea_tray'):
    """Low bamboo tea tray 0.34 x 0.25 with a small grey-green teapot and four cups."""
    mb = mo.MB()
    W = 'oak_light'
    pot = M.solid('living_teapot', '#8A9684', 0.35)
    mb.box((-0.17, -0.125, 0.02), (0.17, 0.125, 0.032), W, bev=0.002, grain=0)
    for sy in (-1, 1):
        mb.box((-0.17, sy * 0.125, 0.0), (0.17, sy * 0.113, 0.05), W, bev=0.002, grain=0)
    for sx in (-1, 1):
        mb.box((sx * 0.17, -0.113, 0.0), (sx * 0.158, 0.113, 0.05), W, bev=0.002, grain=1)
    mb.at(Tr(-0.085, 0.02, 0.032))
    mb.lathe([(0, 0), (0.028, 0), (0.04, 0.02), (0.04, 0.04), (0.026, 0.055), (0.012, 0.058), (0.008, 0.068), (0, 0.07)], pot, 16)
    rtube(mb, [(0.036, 0, 0.025), (0.055, 0, 0.035), (0.066, 0, 0.055)], 0.005, pot, 6)
    rtube(mb, [(-0.036, 0, 0.045), (-0.058, 0, 0.042), (-0.06, 0, 0.022), (-0.038, 0, 0.015)], 0.004, pot, 6)
    for i, (x, y) in enumerate(((0.02, -0.05), (0.08, -0.05), (0.05, 0.05), (0.11, 0.05))):
        mb.at(Tr(x, y, 0.032))
        mb.lathe([(0, 0), (0.014, 0), (0.021, 0.022), (0.019, 0.022), (0.012, 0.004), (0, 0.004)], pot, 12)
    mb.at()
    return mb.finish(name)


def solitaire(name='living.solitaire'):
    """Turned wooden solitaire board dia 0.23 with cream stone marbles."""
    mb = mo.MB()
    mb.lathe([(0, 0), (0.10, 0), (0.115, 0.006), (0.115, 0.014), (0.108, 0.02), (0.10, 0.016), (0, 0.016)], 'oak_table', 28)
    iv = P.mat('ivory')
    for i in range(-3, 4):
        for j in range(-3, 4):
            if (abs(i) > 1 and abs(j) > 1) or (i == 0 and j == 0):
                continue
            mb.at(Tr(i * 0.025, j * 0.025, 0.014))
            mb.dome(0.0085, 0.0085, 0.0085, iv, 6, 2)
    mb.at()
    return mb.finish(name)


def inlay_box(name='living.inlay_box'):
    """Bone-inlaid marquetry box 0.20 x 0.13 x 0.07: pale inlay all over, dark banding and a geometric star."""
    mb = mo.MB()
    iv = P.mat('ivory')
    dk = 'dark_oak_antique'
    mb.box((-0.10, -0.065, 0), (0.10, 0.065, 0.07), iv, bev=0.003)
    for z0, z1 in ((0.0, 0.008), (0.046, 0.052), (0.064, 0.0705)):          # base, lid joint and lid edge bands
        mb.box((-0.1012, -0.0662, z0), (0.1012, 0.0662, z1), dk, grain=0)
    for k in range(8):                                               # geometric star on the lid
        a = tau * k / 8
        r0, r1 = 0.012, 0.048
        mb.face([(r0 * cos(a - 0.3) * 1.4, r0 * sin(a - 0.3), 0.0717), (r1 * cos(a) * 1.5, r1 * sin(a), 0.0717),
                 (r0 * cos(a + 0.3) * 1.4, r0 * sin(a + 0.3), 0.0717)], dk, (0, 0, 1))
    for sx in (-1, 1):                                               # diamond lozenges on the front
        for k in range(3):
            x = sx * (0.02 + 0.028 * k)
            mb.face([(x - 0.01, -0.0663, 0.027), (x, -0.0663, 0.04), (x + 0.01, -0.0663, 0.027), (x, -0.0663, 0.014)], dk, (0, -1, 0))
    return mb.finish(name)


def potpourri_jar(name='living.potpourri'):
    mb = mo.MB()
    mb.lathe([(0, 0.004), (0.042, 0.004), (0.046, 0.03), (0.046, 0.11), (0, 0.11)], M.solid('living_potpourri', '#8C5A46', 0.9), 12)
    mb.lathe([(0.03, 0.142), (0.052, 0.142), (0.052, 0.156), (0, 0.158)], M.mat('cork'), 12)
    mb.tube([(0.05 * cos(a), 0.05 * sin(a), 0.135) for a in (tau * k / 12 for k in range(12))], 0.004, 'linen_cream', 5, closed=True)
    root = mb.finish(name)
    g = P.vase(0.15, 0.105, 'cylinder', 'glass_clear', name=name + '.glass')
    kid(root, g, (0, 0, 0))
    return root


# ------------------------------------------------------------------------------------- chandelier dressing
WARM_WHITE = '#FFD49C'        # emissive colours are seen through the 3000 K view white balance: this reads cream
ROSE_GLOW = '#E8875A'         # ... and this reads as back-lit salmon-pink cloth


_TURN = random.Random(3)


def bead(mb, p, r, mat, long=1.0):
    """Faceted crystal bead: a girdled hexagonal bipyramid, turned and tipped at random so that a string of them
    sparkles unevenly instead of reading as a row of identical flat tiles."""
    mb.at(Tr(*p) @ Rz(_TURN.uniform(0, 60)) @ Rx(_TURN.uniform(-40, 40)) @ Ry(_TURN.uniform(-40, 40)))
    mb.lathe([(0, -r * long), (r, -0.28 * r), (r, 0.28 * r), (0, r * long)], mat, 6)


def bead_string(mb, pts, r, mat, pitch=None):
    """Faceted beads along a polyline, one every `pitch` metres."""
    pitch = pitch or 2.3 * r
    P_ = [Vector(p) for p in pts]
    acc, nxt = 0.0, 0.0
    for a, b in zip(P_, P_[1:]):
        L = (b - a).length
        while nxt <= acc + L:
            bead(mb, tuple(a + (b - a) * ((nxt - acc) / max(L, 1e-9))), r, mat)
            nxt += pitch
        acc += L
    mb.at()


def swag(a, b, sag, n=12):
    a, b = Vector(a), Vector(b)
    return [tuple(a + (b - a) * (i / n) - Vector((0, 0, sag * 4 * (i / n) * (1 - i / n)))) for i in range(n + 1)]


def spear(mb, p, L, mat, n=4, fat=0.15, turn=0.0):
    """Cut-glass spear / pear drop hanging from p (n = 4: square-cut spear; fat 0.22 + n = 6: pear)."""
    mb.at(Tr(*p) @ Rz(turn))
    mb.lathe([(0, -L), (L * fat, -L * 0.7), (L * fat * 0.5, -L * 0.2), (L * fat * 0.5, -L * 0.1), (0, 0)], mat, n)


def chandelier_dressing(bulbs, hub, name='living.chandelier'):
    """Crystals, shades and arm scrolls for the brass chandelier (still t=110 / f_0791). bulbs = lamp centres,
    hub = centre of the brass bowl, all in the chandelier's local frame. Returns (crystals, shades, scrolls):
    cut-glass bobeche dishes under every candle, each hung with a ring of 14 bead-headed spear drops, an inner
    ring of 7 and a pear pendant on a bead chain under the arm tip; two tiers of faceted bead swags from arm to
    arm; bead strings from every arm up to the top of the stem; pleated dusky-rose clip-on shades that glow
    (translucent cloth, cream lining); a scroll curl in polished brass on each of the eight long arms.
    Everything stays within 0.445 m of the axis (0.89 overall)."""
    _TURN.seed(3)
    cr = mo.MB()
    G = crystal(0.6, 'living_crystal_drops', glow=0.2)        # dense and faintly lit: the facets read white against the ceiling
    hub = Vector(hub)
    Z = lambda dz: Vector((0, 0, dz))
    lower = [Vector(b) for b in bulbs if (Vector(b) - hub).xy.length > 0.3]
    upper = [Vector(b) for b in bulbs if (Vector(b) - hub).xy.length <= 0.3]
    for b in lower + upper:
        pan = b - Z(0.125)                                    # drip pan under the candle
        cr.at(Tr(*pan))
        cr.lathe([(0.012, -0.008), (0.038, -0.004), (0.055, 0.007)], G, 12)            # cut-glass bobeche
        for k in range(14):                                   # skirt of bead-headed spear drops round the dish
            a = tau * k / 14
            top = pan + Vector((cos(a), sin(a), 0)) * 0.053 + Z(0.003)
            bead(cr, tuple(top), 0.0085, G)
            bead(cr, tuple(top - Z(0.016)), 0.007, G)
            spear(cr, tuple(top - Z(0.024)), 0.075 if k % 2 == 0 else 0.055, G, fat=0.17, turn=45)
        for k in range(7):                                    # inner ring of short drops
            a = tau * (k + 0.5) / 7
            top = pan + Vector((cos(a), sin(a), 0)) * 0.03 - Z(0.006)
            bead(cr, tuple(top), 0.007, G)
            spear(cr, tuple(top - Z(0.008)), 0.04, G, fat=0.2, turn=45)
        for k, dz in enumerate((0.022, 0.038, 0.053)):        # pear pendant on a three-bead chain under the arm tip
            bead(cr, tuple(pan - Z(dz)), 0.0075 - 0.0005 * k, G)
        spear(cr, tuple(pan - Z(0.062)), 0.058, G, n=6, fat=0.24)
    lower.sort(key=lambda v: math.atan2(v.y - hub.y, v.x - hub.x))
    lp = [b - Z(0.125) for b in lower]
    top = hub + Z(0.42)                                       # the strings gather high on the stem
    for i, p in enumerate(lp):
        q = lp[(i + 1) % len(lp)]
        d0, d1 = (p - hub), (q - hub)
        d0.z = d1.z = 0
        d0.normalize()
        d1.normalize()
        a_, b_ = p - d0 * 0.03, q - d1 * 0.03
        bead_string(cr, swag(a_ - Z(0.012), b_ - Z(0.012), 0.07, 16), 0.0068, G)
        bead_string(cr, swag(a_ - Z(0.035), b_ - Z(0.035), 0.125, 16), 0.006, G)
        mid = Vector(swag(a_ - Z(0.035), b_ - Z(0.035), 0.125, 16)[8])
        spear(cr, tuple(mid - Z(0.008)), 0.05, G, n=6, fat=0.22)                        # pear at the low point
        bead_string(cr, swag(p - d0 * 0.05 + Z(0.004), top + d0 * 0.02, 0.07, 16), 0.006, G, pitch=0.0145)
    for p in [b - Z(0.125) for b in upper]:
        d0 = p - hub
        d0.z = 0
        d0.normalize()
        bead_string(cr, swag(p - d0 * 0.045 + Z(0.004), top + Z(0.08) + d0 * 0.015, 0.035, 10), 0.0056, G, pitch=0.0135)
    for k in range(8):                                        # bead collar where the strings gather, drops under the bowl
        a = tau * k / 8
        bead(cr, tuple(top + Vector((cos(a), sin(a), 0)) * 0.018 + Z(0.01)), 0.007, G)
        e = hub + Vector((cos(a + 0.39), sin(a + 0.39), 0)) * 0.125 - Z(0.012)
        bead(cr, tuple(e), 0.0065, G)
        spear(cr, tuple(e - Z(0.007)), 0.045, G, turn=45)
    cr.at()
    crystals = cr.finish(name + '.crystals')

    sc = mo.MB()                                              # scroll curl springing from the middle of each long arm
    Br = brass()
    for b in lower:
        d = b - hub
        d.z = 0
        d.normalize()
        pts, rad = [], []
        for j in range(17):
            t = j / 16
            a = radians(-90 + 430 * t)
            rr = 0.042 - 0.03 * t
            pts.append(tuple(hub + d * (0.236 + rr * cos(a)) + Z(-0.03 + rr * sin(a))))
            rad.append(0.0058 - 0.003 * t)
        tube_var(sc, pts, rad, Br, 6)
        sphere(sc, pts[-1], 0.0055, Br, 8)
    scrolls = sc.finish(name + '.scrolls')

    sh = mo.MB()
    rose = M.solid('living_shade_rose', '#B86F66', 0.9)       # dusky rose cloth, lit from inside: it glows salmon
    e = _bsdf(rose)
    e.inputs['Emission Color'].default_value = M.hex_lin(ROSE_GLOW)
    e.inputs['Emission Strength'].default_value = 0.26
    glow = P.emissive(WARM_WHITE, 1.6)
    npl = 22
    for b in lower + upper:
        rings_o, rings_i = [], []
        for r, dz in ((0.064, -0.05), (0.036, 0.06)):
            ro, ri = [], []
            for k in range(2 * npl):
                a = tau * k / (2 * npl)
                rr = r + (0.0028 if k % 2 else -0.0028) * (r / 0.064)
                ro.append((b.x + rr * cos(a), b.y + rr * sin(a), b.z + dz))
                ri.append((b.x + (rr - 0.0022) * cos(a), b.y + (rr - 0.0022) * sin(a), b.z + dz))
            rings_o.append(ro)
            rings_i.append(ri)
        loft(sh, rings_o, rose, caps=(False, False), flip=False)
        loft(sh, rings_i, glow, caps=(False, False), flip=True)
        sh.tube([(b.x - 0.034, b.y, b.z + 0.052), (b.x + 0.034, b.y, b.z + 0.052)], 0.0012, M.mat('brass'), 3)   # clip wire
    shades = sh.finish(name + '.shades')
    return crystals, shades, scrolls


def cut_tumbler(name='living.tumbler', R=0.0375, H=0.09):
    """Cut-crystal whisky tumbler dia 75 x 90: diamond-cut band round the lower two thirds, plain polished rim,
    inner wall and thick base. Origin base centre."""
    mb = mo.MB()
    G = CUT()
    z0, z1, nu, nv = 0.010, 0.066, 32, 8

    def rad(z):
        return R * (0.86 + 0.14 * z / H)

    def pt(i, j, l):
        z = z0 + (z1 - z0) * j / nv
        return ((rad(z) + l) * cos(tau * i / nu), (rad(z) + l) * sin(tau * i / nu), z)
    diamond_cut(mb, pt, nu, nv, 0.003, G, wrap=True)
    loft(mb, [circ(rad(0) * 0.96, 0.0, nu), circ(rad(z0), z0, nu)], G, caps=(True, False))
    loft(mb, [circ(rad(z1), z1, nu), circ(R, H, nu), circ(R * 0.93, H, nu), circ(R * 0.80, 0.016, nu)], G, caps=(False, True))
    return mb.finish(name)


def glass_tray(name='living.glass_tray'):
    """Oval silver-plated tray 0.50 x 0.30 with a low pierced gallery rim, packed with nine cut-crystal tumblers
    and three stem glasses (f_0194). Everything stays within y <= +0.11 of the tray centre, clear of the
    picture hanging above the bookcase."""
    mb = mo.MB()
    S = M.mat('silver_satin')
    ax, ay = 0.25, 0.15
    mb.lathe([(0, 0), (ax, 0), (ax, 0.004), (0, 0.004)], S, 32, ell=(1.0, ay / ax))
    m = 64
    lo = [((ax - 0.0025) * cos(tau * k / m), (ay - 0.0025) * sin(tau * k / m), 0.006) for k in range(m)]
    hi = [((ax - 0.0025) * cos(tau * k / m), (ay - 0.0025) * sin(tau * k / m), 0.022) for k in range(m)]
    mb.tube(lo, 0.0022, S, 4, closed=True)
    mb.tube(hi, 0.0028, S, 5, closed=True)
    for k in range(m):                                               # pierced gallery: a zig-zag lattice between the rails
        mb.tube([lo[k], hi[(k + 1) % m] if k % 2 == 0 else hi[k - 1]], 0.0016, S, 3)
    root = mb.finish(name)
    first = None
    spots = [(x, -0.068) for x in (-0.158, -0.079, 0.0, 0.079, 0.158)] + [(x, 0.008) for x in (-0.118, -0.039, 0.04, 0.119)]
    for i, (x, y) in enumerate(spots):
        if first is None:
            g = first = cut_tumbler(f'{name}.tumbler.{i}')
        else:
            g = bpy.data.objects.new(f'{name}.tumbler.{i}', first.data)
        kid(root, g, (x, y, 0.004), (0, 0, 37 * i))
    for i, x in enumerate((-0.08, 0.0, 0.08)):
        kid(root, P.wine_glass(0.15, 0.065, mat=CUT(), name=f'{name}.stem.{i}'), (x, 0.062, 0.004))
    return root

# ------------------------------------------------------------------------------------- gallery
def baroque_frame(image, w, h, fw=0.095, depth=0.05, tilt_deg=3.0, mat=None, name='living.art', lam=0.027, amp=0.0085,
                  step=0.0045):
    """Framed picture in a heavy swept 'rippled leaf' Baroque frame (A2, f_0176): a 95 mm scoop moulding whose
    whole face is worked into deep irregular rippled leaves - two crossing wave trains of wavelength ~lam whose
    interference makes slanting blobs, drifting in phase and depth along the side; real relief of +-amp sampled
    every `step` - mitred at the corners. w, h = outer size;
    image fills the sight opening once. Same conventions as props.framed_picture: origin wall, centre of the
    frame, front -Y, tilt_deg tips the top off the wall about the bottom back edge."""
    mb = mo.MB()
    prof = [(0.0, 0.0), (0.0, 0.50), (0.07, 0.82), (0.20, 1.0), (0.36, 0.90), (0.52, 0.62), (0.68, 0.44), (0.80, 0.40),
            (0.88, 0.50), (0.95, 0.46), (1.0, 0.30), (1.0, 0.0)]          # (inset / fw, height / depth), outer back -> sight edge
    T = Tr(0, 0, -h / 2) @ Rx(tilt_deg) @ Tr(0, 0, h / 2)

    def relief(s, t, ph):
        if not 0.03 < t < 0.97:
            return 0.0
        s += 0.006 * sin(tau * s / 0.19 + ph) + 0.004 * sin(tau * s / 0.083 + 5 * t)       # drift: no two leaves alike
        a = sin(tau * (s / lam + 1.5 * t) + ph)
        b = sin(tau * (s / (0.83 * lam) - 1.9 * t) + 1.0 + 2 * ph)
        c = 0.72 + 0.28 * sin(tau * s / 0.117 + 3.1 * t + ph)
        return amp * c * (0.5 * a + 0.5 * b + 0.35 * a * b) * min(1.0, (t - 0.03) / 0.08, (0.97 - t) / 0.08)
    mb._soft = 1
    for k, (L, H) in enumerate(((w, h), (h, w), (w, h), (h, w))):       # bottom, left, top, right (turned about Y)
        mb.at(T @ Ry(90 * k))
        n = max(8, round(L / step))
        rings = []
        for i in range(n + 1):
            q = -1 + 2 * i / n
            rings.append([(q * (L / 2 - t * fw), -(y * depth + relief(q * (L / 2 - t * fw), t, 1.7 * k)), -H / 2 + t * fw)
                          for t, y in prof])
        loft(mb, rings, mat, closed=False, caps=(False, False))
    mb._soft = 0
    cw, ch, yb = w - 2 * fw + 0.006, h - 2 * fw + 0.006, -0.30 * depth + 0.003
    img = M.image_mat('living_art_' + os.path.splitext(os.path.basename(image))[0], image, size_m=(cw, ch), roughness=0.6)
    mb.at(T)
    mb.face([(-cw / 2, yb, -ch / 2), (cw / 2, yb, -ch / 2), (cw / 2, yb, ch / 2), (-cw / 2, yb, ch / 2)], img, (0, -1, 0),
            off=(cw / 2, ch / 2))
    mb.at()
    return mb.finish(name)

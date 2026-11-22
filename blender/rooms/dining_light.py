"""Dining room light fittings: the 12-light brass and crystal chandelier ("remember the design") and the two
twin-arm wall lights, both with six-panel bell shades. Imported by rooms/dining.py.

Chandelier: origin = ceiling contact, hangs -Z. Wall light: origin = wall, backplate centre, front -Y."""
import math
from math import sin, cos, pi

import bpy

from lib import materials as M, mouldings as mo, props as P
from rooms.dining_furniture import T, R, WALL, fin, spline, grid, bar, rrect, oval, turn, brass, crystal, shared

# Lit cloth. Emission is not white-balanced: under the 3000 K view white point the spec ivory (#FFF3D6) reads
# blue and AgX tops out near #E2, so the hues are amber, picked from rendered test patches. Footage (F_705):
# cloth #FFFEF2 above the waist braid, skirt #FEFEFD, ceiling #E5E0CA. Rendered: cloth -> #DED9CB (cream-white),
# skirt and lining -> #DFE1DB, ceiling #B2A998.
SHADE_UP, SHADE_LOW, SHADE_IN = ('#F2BC62', 2.6), ('#F3C473', 3.6), ('#F5CC78', 4.0)
_CACHE = {}


# ------------------------------------------------------------------------------ crystal parts (faceted)
def _bead(mb, c, r, mat, n=6):
    """Faceted bead: n-sided bipyramid centred on c."""
    ring = [(c[0] + r * cos(2 * pi * i / n), c[1] + r * sin(2 * pi * i / n), c[2]) for i in range(n)]
    for i in range(n):
        a, b = ring[i], ring[(i + 1) % n]
        for sz in (1, -1):
            f = mb.face([a, b, (c[0], c[1], c[2] + sz * r)], mat, ((a[0] + b[0]) / 2 - c[0], (a[1] + b[1]) / 2 - c[1], sz * r))
            if f:
                f.smooth = False


def _swag(mb, a, b, sag, mat, r=.0055):
    """String of touching beads sagging from a to b."""
    chord = math.dist(a, b)
    n = max(3, int(chord * (1 + 8 / 3 * (sag / chord) ** 2) / (2.1 * r)))
    for i in range(n):
        t = (i + .5) / n
        _bead(mb, (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t - 4 * sag * t * (1 - t)), r, mat)


def _pendalogue(mb, L, mat, F):
    """Flat kite-cut drop under a small bead; hangs from the frame F's origin down -Z, flat in its XZ plane."""
    M0 = mb.M.copy()
    mb.at(M0 @ F)
    b, w, t = .009, .3 * L, .13 * L
    _bead(mb, (0, 0, -b / 2), b / 2, mat)
    top, bot, zs = (0, 0, -b), (0, 0, -L), -b - .3 * (L - b)
    for sy in (-1, 1):
        ridge = (0, sy * t / 2, zs)
        for p, q in (((-w / 2, 0, zs), top), (bot, (-w / 2, 0, zs)), ((w / 2, 0, zs), bot), (top, (w / 2, 0, zs))):
            f = mb.face([p, q, ridge], mat, ((p[0] + q[0]) / 2, sy, 0))
            if f:
                f.smooth = False
    mb.at(M0)


def _tear(mb, L, mat, F, n=8):
    """Long raindrop pendant on a thin neck, hanging from the frame F's origin."""
    M0 = mb.M.copy()
    mb.at(M0 @ F)
    turn(mb, [(.0012, 0), (.002, -.3 * L), (.0045, -.52 * L), (.15 * L, -.78 * L), (.17 * L, -.87 * L), (.11 * L, -.96 * L),
              (.002, -L)], mat, n)
    mb.at(M0)


# ------------------------------------------------------------------------------ shade and one complete light
def _shade(mb, top_d, bot_d, h, z0):
    """Six-panel bell shade as filmed (F_710): ivory cloth glowing warm above a braid at two fifths of the height,
    a brighter skirt below it (the lamp sits at that level) flaring to the lower rim, which hangs in a point at
    every rib and arches up between; gold braid at the top, the waist, the rim and down the six ribs."""
    rt, rb = top_d / 2, bot_d / 2
    WAIST = .40

    def surf(k, v0=0.0, v1=1.0, u0=0.0, u1=1.0):
        def fn(u, v):
            th, v = 2 * pi * (u0 + (u1 - u0) * u), v0 + (v1 - v0) * v
            w = 1 - v
            r = (rt + (rb - rt) * (.7 * w ** 2.3 + .3 * w)) * (1 + .022 * cos(6 * th)) + k
            return (r * cos(th), r * sin(th), z0 + v * h + .019 * abs(sin(3 * th)) * w ** 2)
        return fn
    lit = lambda spec: P.two_sided(P.emissive(*spec))
    grid(mb, surf(0, 0, WAIST), 24, 3, lit(SHADE_LOW), wrap=True)
    grid(mb, surf(0, WAIST, 1), 24, 4, lit(SHADE_UP), wrap=True)
    grid(mb, surf(-.0012), 24, 6, lit(SHADE_IN), wrap=True)
    braid = P.two_sided(M.solid('dining_braid', '#8F7A46', .8))
    for v0, v1 in ((0, .05), (WAIST - .035, WAIST + .035), (.92, 1)):
        grid(mb, surf(.0012, v0, v1), 24, 1, braid, wrap=True)
    for k in range(6):                                                              # braid down the ribs, above the waist
        grid(mb, surf(.0012, WAIST, .92, k / 6 - .006, k / 6 + .006), 1, 3, braid)


def _light_unit(shade, bobeche, tube):
    """Drip pan, optional cut-glass bobeche bowl with six drops, cream candle tube, lamp and bell shade.
    Origin = top of the arm (underside of the pan). -> (object, z of the lamp centre)."""
    br, cr = brass(), crystal()
    mb = mo.MB()
    mb.lathe([(0, -.012), (.006, -.012), (.008, -.002), (.021, 0), (.0275, .006), (.0265, .008), (.012, .008), (.012, .016),
              (0, .016)], br, 16)
    z0 = .016 + tube                                                                # lower rim of the shade (rib points)
    if bobeche:                                                                     # star-cut bowl 0.115 x 0.04: thick glass
        turn(mb, [(.013, .004), (.032, .007), (.047, .019), (.055, .035), (.0585, .041), (.053, .041), (.043, .025), (.029, .013),
                  (.013, .010)], cr, 16, flat=True, stagger=True, caps=False,       # (outer wall, rolled rim, inner wall)
             rmod=lambda th, j: 1 + (.07 * cos(8 * th) if j in (3, 4, 5) else 0))
        for k in range(6):                                                          # six kite-cut spear drops, 68 x 20 mm
            a = pi * k / 3 + pi / 6
            _pendalogue(mb, .068, cr, T((.057 * cos(a), .057 * sin(a), .038)) @ R('Z', math.degrees(a) + 90))
    mb.lathe([(0, .016), (.012, .016), (.012, z0 + .035), (.006, z0 + .04), (0, z0 + .04)], P.mat('ivory'), 12)
    zl = z0 + .068
    mb.lathe([(0, z0 + .04), (.007, z0 + .045), (.011, z0 + .06), (.01, z0 + .076), (.004, z0 + .09), (0, z0 + .094)],
             P.emissive('#FFD9A0', 6.0), 8)     # slim lamp: the 25 mm light sphere at its centre must enclose it
    _shade(mb, shade[0], shade[1], shade[2], z0)
    return fin(mb, 'dining.light_unit'), zl


def _unit(name, shade, bobeche, tube):
    key = ('unit', shade, bobeche, tube)
    if key not in _CACHE:
        _CACHE[key] = _light_unit(shade, bobeche, tube)
    ob, zl = _CACHE[key]
    return bpy.data.objects.new(name, ob.data), zl


def _ribbon(mb, pts, br, w=.014, t=.005):
    """Flat brass strip bent in the local XZ plane (width across the plane)."""
    bar(mb, pts, rrect(t, w, .0015, 1), br, up=(0, 1, 0))


# ------------------------------------------------------------------------------ chandelier
def chandelier(shade=(.07, .15, .13), zh=-.48):
    """12-light brass and crystal chandelier, dia 0.80 over the shades, 0.71 from the ceiling to the lowest
    crystal (f_0705: drop / width 0.75 seen 23 deg from below; `zh` = hub below the ceiling contact): pierced
    ceiling cup, wire fountain with drops, cut-crystal column on the stem, hub with 8 flat S-scroll arms (C-scroll
    fillers between) + 4 short arms 0.09 higher; every light a star-cut bobeche bowl with 6 drops and a bell shade;
    bead swags arm to arm (two tiers) and hub to arm, a teardrop under every long arm, faceted ball + teardrop finial.
    Returns the root; P.bulb_points(root) gives the 12 lamps."""
    br, cr = brass(), crystal()
    RL, RU = .325, .17                                                              # radius of the lower / upper lights
    mb = mo.MB()
    mb.lathe([(0, -.055), (.02, -.055), (.048, -.036), (.06, -.01), (.06, 0)], br, 20)                # ceiling cup
    for k in range(14):                                                             # its ring of pierced dots
        a = 2 * pi * k / 14
        mb.at(T((.047 * cos(a), .047 * sin(a), -.032)) @ R('Z', math.degrees(a)) @ R('Y', 125))
        mb.dome(.004, .004, .002, 'black_matt', 6, 1)
    mb.at()
    mb.lathe([(0, zh - .04), (.014, zh - .04), (.02, zh - .03), (.04, zh - .022), (.045, zh), (.04, zh + .022), (.02, zh + .032),
              (.012, zh + .04), (.012, zh + .075), (.03, zh + .082), (.033, zh + .095), (.03, zh + .108), (.012, zh + .115),
              (.008, zh + .125), (.008, -.172), (.017, -.16), (.008, -.146), (.007, -.055), (0, -.055)], br, 16)   # hubs + stem
    kc = (min(zh + .34, -.19) - zh - .125) / .215                                   # the column stops under the fountain collar
    turn(mb, [(r, zh + .125 + kc * (z - .125)) for r, z in ((.013, .125), (.026, .14), (.031, .18), (.022, .225), (.029, .275),
              (.024, .32), (.012, .34))], cr, 8, flat=True, stagger=True)         # cut-crystal column round the stem
    turn(mb, [(.004, zh - .094), (.02, zh - .086), (.028, zh - .067), (.02, zh - .048), (.004, zh - .04)], cr, 8, flat=True,
         stagger=True)                                                              # faceted ball finial
    _tear(mb, .10, cr, T((0, 0, zh - .094)))
    for k in range(12):                                                             # fountain of wires with drops
        a = 2 * pi * k / 12
        r1, z1 = (.10, -.185) if k % 2 == 0 else (.07, -.165)
        mb.at(R('Z', math.degrees(a)))
        mb.tube(spline([(.008, 0, -.16), (r1 * .45, 0, -.118), (r1 * .85, 0, -.135), (r1, 0, z1)], 4), .0015, br, 4)
        _pendalogue(mb, .05, cr, T((r1, 0, z1)) @ R('Z', 90))
    mb.at()
    root = fin(mb, 'dining.chandelier')

    def kid(ob, Mx):
        ob.parent = root
        ob.matrix_basis = Mx
        return ob

    # one sector of the lower tier: arm, C-scroll filler, teardrop, three bead swags
    zd = .072                                                                       # arm tip above the hub
    sec = mo.MB()
    arm = spline([(.036, 0, 0), (.07, 0, .022), (.115, 0, -.02), (.17, 0, -.056), (.23, 0, -.05), (.29, 0, -.014),
                  (.321, 0, .034), (RL, 0, zd - .012)], 5)
    _ribbon(sec, arm, br)
    _tear(sec, .085, cr, T((.175, 0, -.06)))                                # 55 mm raindrop on its neck
    sec.at(R('Z', 22.5))
    _ribbon(sec, spline([(.036, 0, -.008), (.066, 0, .03), (.10, 0, .026), (.112, 0, -.004), (.098, 0, -.026), (.08, 0, -.014)], 5),
            br, .011, .004)
    sec.at()
    c8, s8 = cos(pi / 4), sin(pi / 4)
    _swag(sec, (RL, 0, zd - .016), (RL * c8, RL * s8, zd - .016), .075, cr)                # tip to tip
    _swag(sec, (.20, 0, -.056), (.20 * c8, .20 * s8, -.056), .05, cr)                      # lower ring, at the dip
    _swag(sec, (.034, 0, .034), (RL - .012, 0, zd - .02), .05, cr)                         # hub to arm tip
    sec = fin(sec, 'dining.chandelier.arm')
    up = mo.MB()
    _ribbon(up, spline([(.03, 0, 0), (.058, 0, .02), (.095, 0, -.014), (.135, 0, -.018), (.163, 0, .016), (RU, 0, .048)], 5), br,
            .012, .0045)
    up = fin(up, 'dining.chandelier.arm_upper')
    bulbs = []
    for i in range(12):
        lower = i < 8
        deg = 45 * i if lower else 22.5 + 90 * (i - 8)
        rr, z = (RL, zh + zd) if lower else (RU, zh + .095 + .06)
        a = sec if i == 0 else up if i == 8 else bpy.data.objects.new('x', (sec if lower else up).data)
        a.name = f'dining.chandelier.arm.{i}'
        kid(a, T((0, 0, zh if lower else zh + .095)) @ R('Z', deg))
        u, zl = _unit(f'dining.chandelier.light.{i}', shade, True, .039)
        kid(u, R('Z', deg) @ T((rr, 0, z)))
        ang = math.radians(deg)
        bulbs += [rr * cos(ang), rr * sin(ang), z + zl]
    root.data['bulbs'] = bulbs
    return root


# ------------------------------------------------------------------------------ wall light
def _sconce_body():
    br = brass()
    mb = mo.MB()
    mb.at(T((0, -.001, 0)) @ WALL)
    mb.dome(.04, .066, .006, br, 24, 2)                                             # smooth oval backplate, raised centre
    mb.at(T((0, -.005, 0)) @ WALL)
    mb.dome(.03, .054, .012, br, 24, 4)
    mb.at(T((0, -.012, 0)))
    mb.lathe([(0, .056), (.007, .058), (.015, .074), (.012, .086), (.005, .092), (.008, .10), (.003, .109), (0, .113)], br, 16)  # urn
    mb.lathe([(0, -.082), (.006, -.076), (.009, -.066), (.004, -.058), (0, -.056)], br, 12)                                  # drop
    for s in (-1, 1):
        bar(mb, spline([(0, -.006, -.01), (s * .03, -.045, -.03), (s * .075, -.085, -.022), (s * .106, -.10, .012),
                        (s * .115, -.10, .074)], 6), oval(.01, .01, 8), br, up=(0, 1, .3))
        bar(mb, spline([(s * .034, -.048, -.03), (s * .05, -.05, -.008), (s * .04, -.04, .01), (s * .026, -.038, 0)], 4),
            oval(.007, .007, 6), br, up=(0, 1, .3))                                 # small inner scroll
    mb.at()
    return fin(mb, 'dining.sconce')


def sconce(name, shade=(.065, .13, .12)):
    """Twin-arm polished-brass wall light, 0.36 wide x 0.33 high, projecting 0.165: oval backplate with urn
    finial, two S-arms with drip pans, 80 mm cream candle tubes and bell shades (tops 0.30 above the centre)."""
    root = shared(_CACHE, 'sconce', _sconce_body, name)
    bulbs = []
    for i, s in enumerate((-1, 1)):
        u, zl = _unit(f'{name}.light.{i}', shade, False, .08)
        u.parent = root
        u.location = (s * .115, -.10, .085)
        bulbs += [s * .115, -.10, .085 + zl]
    root.data['bulbs'] = bulbs
    return root

"""Dining room fireplace (carved dark-oak surround, barley-twist columns, bronze cast-iron insert with
sunflower tile strips, canopy hood, grate) and the mantel ornaments. Imported by rooms/dining.py.

Everything is built as a wall prop: back on local y = 0, front toward local -Y, +X to the viewer's
right, z = 0 on the floor (ornaments: z = 0 on the shelf)."""
import math
from math import sin, cos, pi

from lib import mouldings as mo, props as P
from rooms.dining_furniture import T, R, WALL, fin, spline, loft, bar, oval, turn, shared

OAK, BRONZE, IRON = 'dark_oak_antique', 'bronze_antique', 'cast_iron'
_CACHE = {}


def _cyma(d0, h0, d1, h1):
    return [(d0, h0)] + mo._s((d0, h0), (d1, h1), 6, 'h')


def _twist(mb, z0, z1, radius, groove, pitch, mat, segs=24, starts=2, fade=.03):
    """Barley-twist (rope) shaft round local Z: `starts` fat rounded ropes with deep V grooves between, one
    full turn per `pitch`. The mesh turns with the ropes, so the grooves are clean helical creases."""
    rows = max(4, round((z1 - z0) / (pitch / 12)))
    rings = []
    for j in range(rows + 1):
        z = z0 + (z1 - z0) * j / rows
        g = groove * min(1.0, (z - z0) / fade + .15, (z1 - z) / fade + .15)        # grooves run out at both ends
        ph = 2 * pi * z / pitch
        rings.append([((radius - g * (1 - abs(sin(starts * pi * i / segs)) ** .55)) * cos(2 * pi * i / segs + ph),
                       (radius - g * (1 - abs(sin(starts * pi * i / segs)) ** .55)) * sin(2 * pi * i / segs + ph), z)
                      for i in range(segs)])
    loft(mb, rings, mat, True, True)


def _column():
    """Free-standing barley-twist column, 0.60 high: gadrooned cup base (0.10 high, 0.14 across), fat rope
    shaft 0.116 dia with 22 mm grooves, two-ring capital."""
    mb = mo.MB()
    cup = [(.058, 0), (.062, .006), (.062, .014), (.05, .02), (.058, .03), (.069, .047), (.07, .06), (.062, .078), (.05, .09),
           (.054, .095), (.054, .102)]
    turn(mb, cup, OAK, 24, rmod=lambda th, j: 1 + (.075 * abs(cos(6 * th)) if 4 <= j <= 7 else 0))
    _twist(mb, .10, .548, .058, .022, .16, OAK)
    turn(mb, [(.05, .545), (.058, .55), (.062, .558), (.058, .566), (.052, .57), (.058, .576), (.066, .586), (.066, .596),
              (.06, .60)], OAK, 24)
    return fin(mb, 'dining.fireplace.column')


def _console(mb, w, flutes, mat):
    """Scrolled console (S-profile bracket) with vertical fluting on its face. Local frame: origin = wall,
    bottom centre; X along the wall, -Y out, Z up; 0.19 high, projecting 0.03 at the foot and 0.10 at the top."""
    side = spline([(.030, 0), (.033, .03), (.045, .07), (.068, .108), (.09, .14), (.10, .166), (.097, .182), (.088, .19)], 3)
    n = 4 * flutes
    rings = []
    for y, z in side:
        ring = [(-w / 2, 0, z), (w / 2, 0, z), (w / 2, -y + .006, z)]
        ring += [(w / 2 - .008 - (w - .016) * i / n, -y + .012 * (.5 - .5 * cos(2 * pi * flutes * i / n)), z) for i in range(n + 1)]
        rings.append(ring + [(-w / 2, -y + .006, z)])
    loft(mb, rings, mat, True, True)
    M0 = mb.M.copy()
    mb.at(M0 @ T((0, -.03, .012)) @ R('Y', 90))                                      # rolled foot of the scroll
    mb.lathe([(0, -w / 2 - .004), (.012, -w / 2 - .004), (.016, -w / 2), (.016, w / 2), (.012, w / 2 + .004), (0, w / 2 + .004)], mat, 12)
    mb.at(M0)


def _acanthus_panel(mb, F, s, mat):
    """Relief filling a 0.42 x 0.15 frieze panel: a scrolling stem (rinceau) running from the end console to
    the centre, clothed both sides in overlapping, curling acanthus leaves; relief up to 15 mm."""
    wave = lambda x: .022 * sin(2 * pi * (x + .19) / .38)
    slope = lambda x: math.degrees(math.atan(.022 * 2 * pi / .38 * cos(2 * pi * (x + .19) / .38)))
    mb.at(F)
    mb.tube([(s * (-.19 + .38 * i / 20), wave(-.19 + .38 * i / 20), .007) for i in range(21)], .007, mat, 6)
    for i in range(17):
        x = -.185 + .0225 * i
        big = i % 2 == 0
        side = 1 if (i // 2) % 2 == 0 else -1
        phi = slope(x) + side * (44 if big else -58)                                # tip direction, from +X
        L = .068 if big else .042
        mb.at(F @ T((s * x, wave(x), .003 if big else .001)) @ R('Z', (phi if s > 0 else 180 - phi) - 90))
        mb.leaf(L, L * .82, .015 if big else .01, mat, 6, serrate=.4, curl=.8, base=.2)
    for x in (-.196, .196):                                                         # volute eye at each end of the stem
        mb.at(F @ T((s * x, wave(x), 0)))
        mb.dome(.014, .014, .012, mat, 10, 3)
    mb.at()


def fireplace():
    """Surround body 1.39 wide, shelf 1.51 x 0.24 at 1.19; opening 0.91 x 0.90 filled by the insert."""
    mb = mo.MB()
    cap = [(0, 0), (.004, 0), (.004, .006)] + _cyma(.004, .008, .018, .026) + [(.018, .032), (0, .032)]
    for s in (-1, 1):
        mb.box((s * .455, 0, 0), (s * .695, -.07, .90), OAK, bev=.003)                  # jamb board behind the column
        for x in (.462, .688):
            mb.box((s * (x - .007), -.07, .30), (s * (x + .007), -.085, .90), OAK, bev=.003)   # edge beads
        mb.box((s * .455, 0, 0), (s * .695, -.18, .272), OAK, bev=.004)                 # plinth block
        mb.sweep(cap, [(s * x, y, .268) for x, y in (((.695, 0), (.695, -.18), (.455, -.18), (.455, 0)) if s > 0 else
                                                      ((.455, 0), (.455, -.18), (.695, -.18), (.695, 0)))], OAK)   # moulded cap
        mb.box((s * .46, 0, .268), (s * .69, -.175, .30), OAK)
        cx = s * .575                                                               # diamond point on the front
        q = [(cx - .08, -.18, .05), (cx + .08, -.18, .05), (cx + .08, -.18, .22), (cx - .08, -.18, .22)]
        ap = (cx, -.208, .135)
        for a, b in zip(q, q[1:] + q[:1]):
            mb.face([a, b, ap], OAK, ((a[0] + b[0]) / 2 - cx, -1, (a[2] + b[2]) / 2 - .135))
        mb.box((s * .48, 0, .90), (s * .67, -.20, .96), OAK)                            # cap block over the column
        mb.at(T((cx, -.09, .96)))
        _console(mb, .15, 3, OAK)                                                   # fluted end console under the shelf
        mb.at()
        # carved frieze panel: bead frame + scrolling acanthus
        px = s * .27
        for a, b in (((-.21, .068), (.21, .075)), ((-.21, -.075), (.21, -.068)), ((-.21, -.075), (-.203, .075)),
                     ((.203, -.075), (.21, .075))):
            mb.box((px + a[0], -.09, 1.055 + a[1]), (px + b[0], -.098, 1.055 + b[1]), OAK, bev=.002)
        _acanthus_panel(mb, T((px, -.09, 1.055)) @ WALL, s, OAK)
    mb.box((-.695, 0, .90), (.695, -.09, .96), OAK)                                     # lintel core
    mb.box((-.695, 0, .96), (.695, -.09, 1.15), OAK)                                    # frieze board
    mb.at(T((0, -.09, .96)))
    _console(mb, .075, 2, OAK)                                                      # narrow centre console
    mb.at()
    # lower cornice, breaking 0.11 forward round the cap block over each column; mantel shelf with ogee edge
    prof = [(0, 0), (.005, 0), (.005, .012)] + _cyma(.01, .016, .03, .048) + [(.03, .06), (0, .06)]
    mb.sweep(prof, [(x, y, .90) for x, y in ((.695, 0), (.695, -.09), (.67, -.09), (.67, -.20), (.48, -.20), (.48, -.09),
                                             (-.48, -.09), (-.48, -.20), (-.67, -.20), (-.67, -.09), (-.695, -.09),
                                             (-.695, 0))], OAK)
    mb.box((-.71, 0, 1.128), (.71, -.20, 1.15), OAK, bev=.006)                          # bed mould
    mb.box((-.725, 0, 1.15), (.725, -.21, 1.19), OAK)
    edge = [(0, 0), (.006, 0)] + mo._s((.006, 0), (.03, .03), 6, 'v') + [(.03, .04), (0, .04)]
    mb.sweep(edge, [(.725, 0, 1.15), (.725, -.21, 1.15), (-.725, -.21, 1.15), (-.725, 0, 1.15)], OAK)

    # ---- cast-iron insert, antique bronze finish
    for s in (-1, 1):
        mb.box((s * .20, -.012, 0), (s * .455, -.06, .80), BRONZE)
        mb.box((s * .425, -.06, 0), (s * .455, -.074, .90), BRONZE, bev=.005)           # moulded outer frame
        mb.box((s * .352, -.06, .02), (s * .366, -.068, .80), BRONZE, bev=.003)
        mb.box((s * .186, -.06, .02), (s * .20, -.068, .80), BRONZE, bev=.003)
        x0, x1 = (.20, .352) if s > 0 else (-.352, -.20)                            # 5 sunflower tiles, 152 mm
        mb.face([(x0, -.0612, .04), (x1, -.0612, .04), (x1, -.0612, .80), (x0, -.0612, .80)], 'sunflower_tile',
                (0, -1, 0), off=(-x0, -.04))
        mb.box((s * .19, -.06, 0), (s * .20, -.135, .20), IRON, bev=.003)               # grate cheeks
    mb.box((-.455, -.012, .80), (.455, -.064, .90), BRONZE)
    mb.box((-.455, -.064, .885), (.455, -.074, .90), BRONZE, bev=.004)
    mb.box((-.425, -.064, .80), (.425, -.07, .812), BRONZE, bev=.003)
    for i in range(9):                                                              # running lozenge relief
        mb.at(T((-.36 + .09 * i, -.064, .849)) @ WALL @ R('Z', 45))
        mb.box((-.019, -.019, 0), (.019, .019, .005), BRONZE, bev=.004)
        mb.at(T((-.315 + .09 * i, -.064, .849)) @ WALL)
        if i < 8:
            mb.dome(.008, .008, .005, BRONZE, 6, 2)
    mb.at()
    # matt black fireback, 5 mm in front of the room skirting that runs across the breast behind the surround
    mb.face([(-.20, -.027, 0), (.20, -.027, 0), (.20, -.027, .80), (-.20, -.027, .80)], 'black_matt', (0, -1, 0))

    # canopy hood: cast shell, narrow and shallow under the top bar, swelling forward and outward to a flared lip
    # whose lower edge droops in the middle. Rings: (z, half width, projection)
    def hood_pt(z, w, d, a, dip=0.0):
        sa = sin(a)
        return (-w * cos(a), -.064 - d * sa ** .35, z - dip * sa * sa)
    arc = [pi * i / 20 for i in range(21)]
    rings = [[hood_pt(z, w, d, a, dip) for a in arc]
             for z, w, d, dip in ((.80, .13, .012, 0), (.775, .15, .04, 0), (.72, .166, .062, 0), (.66, .18, .082, 0),
                                  (.60, .192, .098, .008), (.566, .20, .108, .022), (.55, .198, .102, .03))]
    loft(mb, rings, BRONZE, True, True)
    HF = T((0, -.141, .68)) @ R('X', 73)                                            # frame on the swelling hood front
    mb.at(HF)
    mb.dome(.026, .034, .012, BRONZE, 10, 2)                                        # cast relief: boss, scrolls, leaves
    for s in (-1, 1):
        mb.tube([(s * (.07 + (.045 - .003 * i) * cos(.6 * i)), -.005 + (.045 - .003 * i) * sin(.6 * i), .001) for i in range(14)],
                .004, BRONZE, 5)
        for a in (30, 80, 130):
            mb.at(HF @ T((s * .03, 0, 0)) @ R('Z', -s * a))
            mb.leaf(.06, .032, .009, BRONZE, 5, serrate=.3, curl=.4)
        mb.at(HF)
    for i in range(11):                                                             # beaded rim above the lip
        a = pi * (.14 + .072 * i)
        mb.at(T(hood_pt(.60, .192, .098, a, .008)) @ R('Z', math.degrees(a) - 90) @ WALL)
        mb.dome(.008, .008, .006, BRONZE, 6, 2)
    mb.at()
    mb.box((-.19, -.02, 0), (.19, -.13, .05), IRON, bev=.004)                           # ash-pan front, back to the fireback
    mb.box((-.12, -.13, .008), (.12, -.138, .042), IRON, bev=.003)
    mb.at(T((0, -.138, .025)) @ WALL)
    mb.dome(.012, .012, .012, BRONZE, 8, 2)
    mb.at()
    for z in (.085, .125, .165):
        mb.tube([(-.19, -.125, z), (0, -.133, z), (.19, -.125, z)], .008, IRON, 6)         # grate bars
    root = fin(mb, 'dining.fireplace')
    for i, s in enumerate((-1, 1)):
        col = shared(_CACHE, 'column', _column, f'dining.fireplace.column.{i}')
        col.parent = root
        col.location = (s * .575, -.125, .30)
    return root


# ------------------------------------------------------------------------------ mantel ornaments
def _candelabrum():
    br, gilt = 'brass_antique', 'gilt_bright'
    mb = mo.MB()
    # dark pedestal: base block, barley twist, taller top block carrying a gilt leaf mount
    mb.box((-.035, -.035, 0), (.035, .035, .028), OAK, bev=.003)
    _twist(mb, .026, .142, .024, .009, .09, OAK, 16)
    mb.box((-.034, -.034, .14), (.034, .034, .20), OAK, bev=.003)
    for a, L in ((0, .05), (38, .04), (-38, .04)):
        mb.at(T((0, -.034, .15)) @ WALL @ R('Z', a))
        mb.leaf(L, L * .42, .007, gilt, 5, serrate=.3, curl=.5)
    mb.at(T((0, -.034, .152)) @ WALL)
    mb.dome(.008, .008, .006, gilt, 10, 3)
    mb.at()
    # stout cast-brass stem in tiers: spreading foot, knop, vase baluster, knop, arm boss, shaft, centre candle cup
    # with an urn finial rising out of it (the fifth light)
    mb.lathe([(0, .20), (.034, .20), (.036, .206), (.031, .213), (.018, .222), (.013, .232), (.019, .243), (.021, .252),
              (.014, .262), (.017, .272), (.027, .288), (.029, .303), (.022, .322), (.013, .340), (.018, .350), (.021, .358),
              (.015, .366), (.023, .374), (.023, .384), (.014, .392), (.011, .41), (.010, .44), (.013, .455), (.012, .47),
              (.0165, .49), (.0175, .502), (.0135, .503), (.008, .506), (.006, .52), (.010, .528), (.015, .533), (.008, .54),
              (.011, .552), (.013, .562), (.009, .576), (.004, .588), (0, .60)], br, 24)
    cup = [(0, -.006), (.008, -.006), (.011, .004), (.012, .012), (.013, .02), (.0165, .04), (.0175, .05), (.0135, .05),
           (.012, .022), (0, .022)]                                                 # heavy candle cup, 35 x 50 mm

    def drip_pan():                                                                 # wide dark pan with a scalloped edge, 51 mm
        turn(mb, [(.009, .002), (.021, .004), (.0255, .008), (.024, .0105), (.011, .008)], 'bronze_dark', 16,
             rmod=lambda th, j: 1 + (.06 * cos(8 * th) if j in (2, 3) else 0))
    M0 = mb.M.copy()
    mb.at(M0 @ T((0, 0, .452)))
    drip_pan()
    for a in (18, 162, 198, 342):                                                   # four full S-scroll arms, spread flat
        mb.at(M0 @ R('Z', a))
        bar(mb, spline([(.012, 0, .378), (.035, 0, .346), (.066, 0, .336), (.096, 0, .356), (.112, 0, .39), (.118, 0, .428)], 5),
            oval(.0095, .0095, 8), br, up=(0, 1, 0))
        bar(mb, spline([(.046, 0, .342), (.062, 0, .37), (.05, 0, .394), (.034, 0, .384), (.04, 0, .366)], 4), oval(.007, .007, 6),
            br, up=(0, 1, 0))                                                       # scroll curling back off the arm
        mb.at(M0 @ R('Z', a) @ T((.118, 0, .432)))
        mb.lathe(cup, br, 20)
        drip_pan()
    mb.at(M0)
    return fin(mb, 'dining.candelabrum')


def candelabrum(name):
    """Cast-brass 5-light candelabrum (0.26 wide x 0.40) on a dark barley-twist pedestal; total 0.60."""
    return shared(_CACHE, 'candelabrum', _candelabrum, name)


def _candlestick():
    mb = mo.MB()
    mb.lathe([(0, 0), (.03, 0), (.032, .006), (.026, .012), (.012, .02), (.009, .034), (.012, .046), (.016, .058), (.017, .066),
              (.013, .08), (0, .08)], 'brass', 24)
    mb.lathe([(0, .078), (.011, .078), (.011, .43), (.004, .44), (0, .44)], P.mat('ivory'), 16)
    return fin(mb, 'dining.candlestick')


def candlestick(name):
    """Small brass candlestick with a tall white taper candle (total 0.44)."""
    return shared(_CACHE, 'candlestick', _candlestick, name)


def clock_face(r=.0544):
    """Round brass bezel, cream dial, thin Roman-style hour strokes and hands, laid over the library clock's
    octagonal dial. Wall prop: dial in the local XZ plane, facing -Y, origin = dial centre."""
    blk = 'black_matt'
    mb = mo.MB()
    mb.at(WALL)
    mb.lathe([(r, .001), (r, .0025), (0, .0025)], P.mat('dial_cream'), 32)
    mb.lathe([(r * 1.17, .001), (r * 1.17, .006), (r * 1.13, .012), (r * 1.04, .011), (r * .99, .004), (r * .99, .001)], 'brass', 32)

    def stroke(x0, x1):                                                             # thin bar from (x0, foot) to (x1, head)
        mb.prism([(x0 - .0007, r * .68, .0026), (x0 + .0007, r * .68, .0026), (x1 + .0007, r * .9, .0026),
                  (x1 - .0007, r * .9, .0026)], (0, 0, .0006), blk)
    for k, num in enumerate(('I', 'II', 'III', 'IIII', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII')):
        mb.at(WALL @ R('Z', -30 * (k + 1)))
        x = -sum(.0034 if c == 'I' else .0075 for c in num) / 2
        for c in num:
            if c == 'I':
                stroke(x + .0017, x + .0017)
            elif c == 'V':
                stroke(x + .0037, x + .001)
                stroke(x + .0037, x + .0065)
            else:
                stroke(x + .001, x + .0065)
                stroke(x + .0065, x + .001)
            x += .0034 if c == 'I' else .0075
    for ang, L, wd in ((60, .5, .05), (-60, .78, .032)):                            # hands at ten past ten
        mb.at(WALL @ R('Z', ang))
        mb.prism([(-r * wd, -r * .1, .0036), (r * wd, -r * .1, .0036), (r * wd * .3, r * L, .0036), (-r * wd * .3, r * L, .0036)],
                 (0, 0, .0008), blk)
    mb.at(WALL)
    mb.dome(.004, .004, .0052, 'brass', 10, 2)
    mb.at()
    return fin(mb, 'dining.mantel_clock.face')

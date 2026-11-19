"""Dining room wall pieces and soft furnishings modelled as geometry: the two carved grapevine panels, the
triptych mirror, the mounted sword board, the 36 crest plaques and the two tied-back check curtains.
Imported by rooms/dining.py.

Wall props: back on local y = 0, front toward local -Y, +X to the viewer's right, origin = centre of
the back face (curtain: top centre of the heading)."""
import math
from math import sin, cos, pi

from lib import materials as M, mouldings as mo, props as P
from rooms.dining_furniture import T, R, WALL, fin, spline, loft, grid, bar, rrect, oval, turn, dark_wood, shared, check_mat

DARK = 'dark_joinery'
_CACHE = {}


def _ring(mb, w, h, band, y0, y1, mat, bev=.002):
    """Rectangular ring of four boards, outer size w x h, members `band` wide, between depths y0 and y1."""
    mb.box((-w / 2, y0, h / 2 - band), (w / 2, y1, h / 2), mat, bev=bev)
    mb.box((-w / 2, y0, -h / 2), (w / 2, y1, -h / 2 + band), mat, bev=bev)
    for s in (-1, 1):
        mb.box((s * w / 2, y0, -h / 2 + band), (s * (w / 2 - band), y1, h / 2 - band), mat, bev=bev)


def _vine_leaf(mb, F, x, y, ang, size, mat):
    """Five-lobed vine leaf in relief on the panel frame F (X along, Y up, Z out), stalk at (x, y)."""
    for a, k in ((0, 1.0), (48, .82), (-48, .82), (100, .55), (-100, .55)):
        mb.at(F @ T((x, y, .002)) @ R('Z', ang + a))
        mb.leaf(size * k, size * .55 * k, .012, mat, 5, serrate=.3, curl=.5, base=.3)


def carved_panel():
    """Carved near-black oak panel 0.44 x 0.88: frame with a gilt slip, fielded panel with a hanging grapevine
    in high relief (vine leaves, a long tapering bunch of grapes, lower leaves and tendrils)."""
    wd = dark_wood()
    mb = mo.MB()
    _ring(mb, .44, .88, .045, 0, -.045, wd, .004)                                   # flat outer band
    _ring(mb, .35, .79, .006, 0, -.041, 'gilt', .001)                               # gilt inner slip
    _ring(mb, .338, .778, .014, 0, -.036, wd, .004)                                 # moulded border, stepping in
    _ring(mb, .31, .75, .012, 0, -.028, wd, .004)
    mb.box((-.143, 0, -.363), (.143, -.016, .363), wd)                               # field
    F = T((0, -.016, 0)) @ WALL
    for x, y, a, sz in ((-.055, .255, 35, .095), (.05, .27, -40, .09), (0, .30, 0, .075), (-.085, .19, 110, .06),
                        (.085, .18, -115, .065)):
        _vine_leaf(mb, F, x, y, a, sz, wd)
    row = 0
    for n in (3, 4, 5, 4, 4, 3, 3, 3, 2, 2, 1, 1):                                  # the bunch, tapering down
        yy = .215 - .039 * row
        for i in range(n):
            xx = (i - (n - 1) / 2) * .036 + .006 * sin(row * 2.3 + i)
            mb.at(F @ T((xx, yy + .008 * cos(i * 1.7 + row), .002 + .006 * ((row + i) % 2))))
            mb.dome(.0185, .0185, .016, wd, 8, 3)
        row += 1
    for x, y, a, sz in ((-.06, -.265, 150, .075), (.055, -.25, -140, .07), (0, -.30, 180, .06)):
        _vine_leaf(mb, F, x, y, a, sz, wd)
    mb.at(F)
    mb.tube([(0, .34, .006), (.01, .30, .01), (0, .24, .01)], .006, wd, 5)                # main stalk
    for s in (-1, 1):                                                               # curling tendrils
        mb.tube([(s * (.03 + .0035 * i) * cos(.7 * i) + s * .09, -.02 + .012 * i + (.03 - .002 * i) * sin(.7 * i), .004)
                 for i in range(12)], .003, wd, 4)
    mb.at()
    mb.box((-.09, -.016, -.363), (.09, -.03, -.345), wd, bev=.004)                      # small moulded base
    return fin(mb, 'dining.carved_panel')


def triptych_mirror():
    """Near-black oak triptych mirror 1.47 x 0.85: bolection-moulded 75 mm frame, two 90 mm moulded mullions,
    three plates (0.30 / 0.52 / 0.30 wide x 0.70 high) with a 20 mm bevel."""
    oak = dark_wood()
    mb = mo.MB()
    W, H = 1.47, .85
    mb.box((-W / 2 + .004, 0, -H / 2 + .004), (W / 2 - .004, -.012, H / 2 - .004), oak)   # back board
    bol = [(.075, .012), (.075, .017), (.07, .026), (.062, .031), (.05, .031), (.04, .037), (.024, .041), (.009, .037),
           (0, .028), (0, 0)]                                                       # bolection: raised roll, cove to the glass
    mb.sweep(bol, [(-W / 2, 0, -H / 2), (W / 2, 0, -H / 2), (W / 2, 0, H / 2), (-W / 2, 0, H / 2)], oak, closed=True, up=(0, -1, 0))
    mul = [(.045, .012), (.045, .017), (.04, .026), (.03, .031), (.012, .038), (0, .04), (-.012, .038), (-.03, .031),
           (-.04, .026), (-.045, .017), (-.045, .012)]
    for x in (-.305, .305):
        mb.sweep(mul, [(x, 0, -.352), (x, 0, .352)], oak, up=(0, -1, 0), caps=False)
    for cx, w in ((-.505, .31), (0, .52), (.505, .31)):                             # plates, each with a 20 mm bevel
        w2, h2, bv = w / 2, .35, .02
        o = [(cx - w2, -.0125, -h2), (cx + w2, -.0125, -h2), (cx + w2, -.0125, h2), (cx - w2, -.0125, h2)]
        i_ = [(cx - w2 + bv, -.0165, -h2 + bv), (cx + w2 - bv, -.0165, -h2 + bv), (cx + w2 - bv, -.0165, h2 - bv),
              (cx - w2 + bv, -.0165, h2 - bv)]
        # flat-shaded: the 11 deg bevel is under the smoothing angle, and averaged normals bent the plate into a lens
        for f in [mb.face(i_, 'mirror', (0, -1, 0))] + [mb.face([o[k], o[(k + 1) % 4], i_[(k + 1) % 4], i_[k]], 'mirror', (0, -1, 0))
                                                         for k in range(4)]:
            f.smooth = False
    for s in (-1, 1):                                                               # brass hanging hooks
        mb.at(T((s * .45, -.004, H / 2 + .008)) @ WALL)
        mb.dome(.009, .009, .008, 'brass', 8, 2)
    mb.at()
    return fin(mb, 'dining.mirror')


def sword_board():
    """Dark board 1.24 x 0.22 with ogee-pointed ends carrying an officer's sword (pierced half-basket hilt at
    the viewer's left, fullered blade) above its steel scabbard, on two pairs of black iron hooks."""
    # polished steel: the library's silver_satin (#9C9C98, roughness .35) read as dull pewter against the dark board
    steel, blk = M.solid('dining_steel', '#D8D8D4', .14, metallic=1), 'cast_iron'
    mb = mo.MB()
    end = [(.56, -.11), (.575, -.085), (.585, -.045), (.62, 0), (.585, .045), (.575, .085), (.56, .11)]
    out = end + [(-x, z) for x, z in reversed(end)]
    mb.prism([(x, 0, z) for x, z in out], (0, -.02, 0), DARK)
    mb.prism([(x * .97, -.02, z * .9) for x, z in out], (0, -.004, 0), DARK)            # raised field
    zs, zc, yb = .047, -.047, -.039
    rings = []
    for x, k in ((-.37, 1), (.30, .92), (.47, .8), (.535, .5), (.562, .08)):         # blade: lens section, shallow fuller
        w, t = .015 * k, .004 * k                                                   # 30 mm blade, full lens section
        rings.append([(x, yb, zs + w), (x, yb - t, zs + w * .45), (x, yb - t * (.55 if x < .4 else 1), zs), (x, yb - t, zs - w * .45),
                      (x, yb, zs - w), (x, yb + t, zs - w * .45), (x, yb + t, zs + w * .45)])
    loft(mb, rings, steel, True, True)
    mb.at(T((0, yb, zs)) @ R('Y', -90))                                             # hilt axis: local +Z runs toward the pommel
    grip = [(.0085 + .0012 * (i % 2), .378 + .0075 * i) for i in range(15)]         # wire-bound grip
    turn(mb, [(.006, .376)] + grip + [(.006, .485)], 'black_matt', 10)
    mb.lathe([(0, .484), (.008, .484), (.0125, .492), (.0135, .502), (.01, .513), (.004, .518), (0, .519)], steel, 12)   # pommel
    mb.lathe([(0, .366), (.024, .366), (.026, .371), (.024, .376), (0, .376)], steel, 16)                               # guard plate
    for a in (-190, -158, -126, -94, -62):                                          # bars of the half-basket (front and below)
        ca, sa = cos(math.radians(a)), sin(math.radians(a))
        pts = [(rr * ca, rr * sa, z) for rr, z in ((.022, .371), (.04, .385), (.05, .42), (.046, .46), (.03, .495), (.012, .51))]
        bar(mb, spline(pts, 4), oval(.0045, .0045, 6), steel, up=(-sa, ca, 0))
    for z in (.40, .44, .478):                                                      # cross-links of the basket
        r = {.40: .047, .44: .05, .478: .04}[z]
        bar(mb, [(r * cos(math.radians(a)), r * sin(math.radians(a)), z) for a in range(-190, -61, 16)], oval(.0035, .0035, 6),
            steel, up=(0, 0, 1))
    mb.at(T((0, -.04, zc)) @ R('Y', -90))
    mb.lathe([(0, -.44), (.008, -.44), (.013, -.425), (.014, 0), (.016, .38), (.019, .385), (.019, .40), (.016, .405),
              (.016, .42), (0, .42)], steel, 12)                                    # scabbard, mouth toward the hilt
    for z in (.18, .34):
        mb.lathe([(.0155, z), (.019, z), (.019, z + .012), (.0155, z + .012)], steel, 12)   # ring mounts
    mb.at()
    for x in (-.27, .30):
        for z0 in (zs - .016, zc - .018):
            mb.box((x - .006, -.02, z0 - .006), (x + .006, -.062, z0), blk, bev=.002)       # hook arm
            mb.box((x - .006, -.056, z0), (x + .006, -.062, z0 + .022), blk, bev=.002)      # upturned tip
    return fin(mb, 'dining.sword')


# ============================================================================== crest plaques
def _heater(w, h, n=7):
    """Shield outline [(x, z)...], counter-clockwise seen from the front: flat top with cut shoulders,
    straight sides, curving to a pointed base."""
    zs = h / 2 - .46 * h
    right = [(w / 2 - .011, h / 2), (w / 2, h / 2 - .011), (w / 2, zs)]
    right += [(w / 2 * (1 - (i / n) ** 1.7), zs - (zs + h / 2) * i / n) for i in range(1, n)]      # arcs meeting in a point
    right.append((0, -h / 2))
    return [(-x, z) for x, z in right[:-1]] + right[::-1]


def _scaled(poly, k, c=(0, 0)):
    return [(c[0] + (x - c[0]) * k, c[1] + (z - c[1]) * k) for x, z in poly]


def _clip(poly, nx, nz, c):
    """Part of a polygon with nx * x + nz * z <= c (Sutherland-Hodgman)."""
    out = []
    for (x0, z0), (x1, z1) in zip(poly, poly[1:] + poly[:1]):
        d0, d1 = nx * x0 + nz * z0 - c, nx * x1 + nz * z1 - c
        if d0 <= 0:
            out.append((x0, z0))
        if d0 * d1 < 0:
            t = d0 / (d0 - d1)
            out.append((x0 + (x1 - x0) * t, z0 + (z1 - z0) * t))
    return out


def _slab(mb, poly, y0, y1, mat, bev=0.0):
    """Board cut to `poly`, between depths y0 (back) and y1 (front), front edge chamfered by bev."""
    rings = [[(x, y0, z) for x, z in poly], [(x, y1 + bev, z) for x, z in poly]]
    if bev:
        cx, cz = sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly)
        ext = max(max(abs(p[0] - cx), abs(p[1] - cz)) for p in poly)
        rings.append([(x, y1, z) for x, z in _scaled(poly, 1 - bev / ext, (cx, cz))])
    loft(mb, rings, mat, True, True)


def _crown(mb, x, z, y, s, mat):
    """Small relief crown: band, three bosses and an arch, about 2.4 s wide. Frame: wall (x, z), relief -y."""
    mb.box((x - 1.1 * s, y, z), (x + 1.1 * s, y - .003, z + .5 * s), mat, bev=.0008)
    for dx in (-.8, 0, .8):
        mb.at(T((x + dx * s, y, z + (.95 if dx == 0 else .75) * s)) @ WALL)
        mb.dome(.33 * s, .33 * s, .004, mat, 6, 2)
    mb.at()
    mb.tube([(x + 1.0 * s * cos(pi * i / 6), y - .002, z + .5 * s + .75 * s * sin(pi * i / 6)) for i in range(7)], .0015, mat, 4)


def _scroll(mb, z, y, half, mat, sag=.008):
    """Gilt motto scroll (no lettering): bent strip with upturned ends."""
    pts = [(-half - .006, z + .009), (-half, z + .002)] + [(half * (i / 4 - 1), z - sag * (1 - (i / 4 - 1) ** 2)) for i in range(1, 8)] + \
          [(half, z + .002), (half + .006, z + .009)]
    bar(mb, [(x, y, zz) for x, zz in pts], rrect(.012, .003, .001, 1), mat, up=(0, -1, 0))


def _plaque_mesh(kind, w, h):
    """Slots: 0 board, 1 enamel field, 2 second enamel colour, 3 gilt. The first three are overridden per plaque."""
    board, f1, f2 = (M.solid(f'dining_plaque_{k}', c, r) for k, c, r in
                     (('board', '#6E4F31', .15), ('field', '#1B2540', .2), ('field2', '#4A1A22', .2)))
    gilt = P.mat('gilt_bright')
    mb = mo.MB()
    for m in (board, f1, f2, gilt):
        mb.mi(m)                                                                    # fix the slot order
    t, k = .02, w / .15
    if kind == 'round':                                                             # ship's badge: rope ring, crown, disc
        circ = lambda r, n=28: [(r * cos(2 * pi * i / n), r * sin(2 * pi * i / n)) for i in range(n)]
        _slab(mb, circ(w / 2), 0, -t, board, .004)
        _slab(mb, circ(w * .33), -t, -t - .003, f1)
        mb.tube([(x, -t - .004, z) for x, z in circ(w * .37, 24)], .0055, gilt, 6, closed=True)
        for i in range(24):                                                         # lay of the rope
            a = 2 * pi * (i + .5) / 24
            mb.at(T((w * .37 * cos(a), -t - .0085, w * .37 * sin(a))) @ WALL @ R('Z', math.degrees(a) + 35))
            mb.box((-.004, -.0012, 0), (.004, .0012, .0012), gilt)
        mb.at()
        _crown(mb, 0, w * .40, -t - .008, .014, gilt)
        mb.at(T((0, -t - .003, 0)) @ WALL)
        mb.dome(w * .11, w * .13, .006, gilt, 16, 3)
        mb.at()
        mb.box((-w * .2, -t - .003, -w * .25), (w * .2, -t - .0055, -w * .2), gilt, bev=.0008)
    elif kind == 'lozenge':                                                         # diamond naval badge
        dia = [(w / 2, 0), (0, h / 2), (-w / 2, 0), (0, -h / 2)]
        _slab(mb, dia, 0, -t, board, .004)
        _slab(mb, _scaled(dia, .78), -t, -t - .003, gilt)
        _slab(mb, _scaled(dia, .7), -t - .003, -t - .0045, f1)
        _slab(mb, _clip(_scaled(dia, .7), 0, 1, -.012), -t - .0045, -t - .0052, f2)
        mb.box((-.003, -t - .0045, -.035), (.003, -t - .0075, .04), gilt, bev=.001)        # anchor: shank, stock, arms, ring
        mb.box((-.02, -t - .0045, .022), (.02, -t - .007, .027), gilt, bev=.001)
        mb.tube([(.028 * cos(pi + pi * i / 8), -t - .006, -.014 + .022 * sin(pi + pi * i / 8)) for i in range(9)], .0025, gilt, 5)
        mb.tube([(.007 * cos(2 * pi * i / 8), -t - .006, .047 + .007 * sin(2 * pi * i / 8)) for i in range(8)], .002, gilt, 4, closed=True)
    else:
        out = _heater(w, h)
        _slab(mb, out, 0, -t, board, .004)
        if kind == 'badge':                                                         # big gilt cap badge straight on the board
            zc = .012 * k
            mb.tube([(.036 * k * cos(2 * pi * i / 20), -t - .003, zc + .04 * k * sin(2 * pi * i / 20)) for i in range(20)], .0045 * k,
                    gilt, 6, closed=True)
            for i in range(14):                                                     # wreath leaves round the ring
                a = 2 * pi * (i + .5) / 14
                mb.at(T((.036 * k * cos(a), -t - .004, zc + .04 * k * sin(a))) @ WALL @ R('Z', math.degrees(a) + (20 if i < 7 else 160)))
                mb.leaf(.02 * k, .009 * k, .003, gilt, 3)
            mb.at(T((0, -t, zc)) @ WALL)
            mb.dome(.024 * k, .027 * k, .007, gilt, 12, 3)
            mb.at()
            _crown(mb, 0, zc + .043 * k, -t - .001, .013 * k, gilt)
            _scroll(mb, zc - .052 * k, -t - .003, .036 * k, gilt)
        else:                                                                       # inset enamel crest shield with gilt edge
            c = (0, (.012 if kind == 'chief' else .006) * k)
            crest = [(x + c[0], z + c[1]) for x, z in _heater(.09 * k, .11 * k)]
            _slab(mb, _scaled(crest, 1.075, c), -t, -t - .003, gilt)
            _slab(mb, crest, -t - .003, -t - .0045, f1)
            if kind == 'bend':                                                      # diagonal band of the second colour
                part = _clip(_clip(_scaled(crest, .999, c), .7, -.7, c[1] * -.7 + .011 * k), -.7, .7, c[1] * .7 + .011 * k)
            elif kind == 'party':                                                   # parted per bend: lower half second colour
                part = _clip(_scaled(crest, .999, c), -.7, .7, c[1] * .7)
            else:                                                                   # chief: band across the top
                part = _clip(_scaled(crest, .999, c), 0, -1, -(c[1] + .026 * k))
            _slab(mb, part, -t - .0045, -t - .0052, f2)
            zc = c[1] - .004 * k
            mb.tube([(.016 * k * cos(2 * pi * i / 14), -t - .0055, zc + .016 * k * sin(2 * pi * i / 14)) for i in range(14)], .003 * k,
                    gilt, 5, closed=True)                                           # gilt relief badge: wreath ring, device, crown
            mb.at(T((0, -t - .005, zc)) @ WALL)
            mb.dome(.009 * k, .011 * k, .004, gilt, 8, 2)
            mb.at()
            _crown(mb, 0, zc + .018 * k, -t - .005, .008 * k, gilt)
            _scroll(mb, c[1] - .066 * k, -t - .002, .034 * k, gilt)
            if kind == 'chief':
                _scroll(mb, c[1] + .064 * k, -t - .002, .03 * k, gilt, sag=-.005)
    return fin(mb, f'dining.plaque.{kind}')


def plaque(name, kind='bend', board='#6E4F31', field='#1B2540', field2='#4A1A22', w=.15, h=.18):
    """Regimental / naval wall plaque: glossy wooden board with bevelled edge, inset enamel crest with gilt rim,
    gilt relief badge (wreath, crown, device) and gilt scroll - generic, no lettering. kind: 'bend' | 'party' |
    'chief' (heater shields with an enamel crest), 'badge' (large gilt badge on the bare board), 'round'
    (ship's badge), 'lozenge'. Plaques of one kind and size share a mesh; colours are per-object materials."""
    ob = shared(_CACHE, (kind, w, h), lambda: _plaque_mesh(kind, w, h), name)
    for i, (key, hx, rough) in enumerate((('wood', board, .15), ('enamel', field, .2), ('enamel', field2, .2))):
        ob.material_slots[i].link = 'OBJECT'
        ob.material_slots[i].material = M.solid(f'dining_{key}_{hx[1:]}', hx, rough)
    return ob


# ============================================================================== curtains
def curtain(name, seed=0):
    """New curtain object; the two drops share one mesh (linked duplicates)."""
    return shared(_CACHE, ('curtain', seed), lambda: _curtain_mesh(seed), name)


def _curtain_mesh(seed=0, name='dining.curtain'):
    """Full-length check curtain on the pelmet track, tied round its middle into a symmetric hourglass: 0.60
    wide at the gathered pencil-pleat heading (75 mm tape, 46 small pleats), 0.25 at the tie-back 1.50 below,
    0.50 at the hem, 10 mm clear of the floor. Soft, shallow folds of uneven width (8 columns per fold), deep
    only where the tie bunches the cloth. Doubled cream cord with a 40 mm bead and a long gold fringed tassel.
    Origin: wall plane, top centre."""
    Ht, zt, n, zh = 2.49, -1.50, 11, -.075                                          # zh = foot of the heading tape
    cloth = P.two_sided(check_mat())
    mb = mo.MB()

    def width(z):
        if z > zt:
            t = z / zt
            return .60 - .35 * (t * t * (3 - 2 * t)) ** 1.3
        return .25 + .25 * (1 - math.exp((z - zt) / .22))

    def depth(z):                                                                   # 8 mm under the tape, 25 mm folds, bunch at the tie
        return .008 + .017 * min(1.0, (zh - z) / .35) + .030 * math.exp(-((z - zt) / .20) ** 2)

    def fn(u, v):
        z = zh - (Ht + zh) * v
        uw = u + .018 * sin(14.5 * u + 1.1 + seed) + .011 * sin(35.8 * u + .4 + 2 * seed)     # folds of uneven width ...
        ph = 2 * pi * n * uw + .5 * sin(2.2 * pi * v + 4 * u + seed)                           # ... wandering a little on the way down
        amp = 1 + .35 * sin(19.5 * u + 2 + seed) + .2 * sin(45.9 * u + seed)                   # ... and of uneven depth
        x = width(z) * (u - .5) + .008 * sin(ph * .5 + 3 * v + seed) * min(1.0, -z)
        y = -.022 - depth(z) * amp * (.5 + .5 * cos(ph))
        return (x, y, z + .006 * (1 + sin(5 * u + seed)) * v)                       # hem 10 - 22 mm above the floor
    grid(mb, fn, n * 8, 36, cloth, uv=lambda u, v: (1.3 * u, zh - (Ht + zh) * v))

    def head(u, v):                                                                 # gathered heading: pencil pleats on the tape,
        k = 1 - v * v                                                               # tucked into the folds at its foot
        return (.60 * (u - .5), -.030 - (.006 + .009 * (.5 + .5 * cos(2 * pi * 46 * u))) * k, (zh - .012) * v)
    grid(mb, head, 46 * 4, 2, cloth, uv=lambda u, v: (1.3 * u, (zh - .012) * v))
    # tie-back: doubled twisted cord round the bunch, sagging to the front, from a brass hook on the post
    cord, gold = P.mat('rope_cream'), P.mat('tassel_gold')
    rx, ry, yc = .14, .058, -.062
    for dz in (0, .011):
        loop = [(rx * sin(a), yc - ry * cos(a), zt + dz + .05 * (1 - cos(a)) / 2) for a in (2 * pi * i / 20 for i in range(21))]
        bar(mb, loop, oval(.009, .009, 6), cord, up=(0, 0, 1))
    mb.at(T((0, -.008, zt + .055)) @ WALL)
    mb.dome(.012, .012, .02, 'brass', 8, 2)                                         # hook
    mb.at()
    # tassel hanging from the front of the loop: cord, cream bead, gold collar, skirt of fringe strands
    x0, y0, z0 = 0, yc - ry - .006, zt
    bar(mb, [(x0, y0 + .004, z0 + .01), (x0, y0, z0 - .03)], oval(.007, .007, 6), cord, up=(1, 0, 0))
    mb.at(T((x0, y0, z0)))
    mb.lathe([(0, -.068), (.008, -.066), (.017, -.058), (.02, -.048), (.017, -.038), (.008, -.03), (0, -.028)], cord, 14)   # bead
    mb.lathe([(0, -.095), (.013, -.095), (.015, -.085), (.012, -.07), (.006, -.066), (0, -.066)], gold, 12)                # collar
    strands = P.two_sided(gold)
    for i in range(26):
        a = 2 * pi * i / 26
        da = .085
        L = .30 - .012 * ((i * 7) % 5) / 4
        pts = [(.012, -.09), (.022, -.16), (.03, -.23), (.033, -L)]
        for (r0, za), (r1, zb) in zip(pts, pts[1:]):
            mb.face([(r0 * cos(a - da), r0 * sin(a - da), za), (r0 * cos(a + da), r0 * sin(a + da), za),
                     (r1 * cos(a + da), r1 * sin(a + da), zb), (r1 * cos(a - da), r1 * sin(a - da), zb)], strands, (cos(a), sin(a), 0))
    mb.lathe([(0, -.24), (.022, -.24), (.026, -.20), (.016, -.10), (0, -.10)], gold, 10)                                      # core of the skirt
    mb.at()
    return fin(mb, name)


def frame_beads(w, h, inset, y, pitch=.011, r=.0045, mat='gold_antique'):
    """Running bead course for a picture frame w x h (outer): beads on a rectangle `inset` inside the outer edge,
    standing on depth y (wall prop: front -Y)."""
    mb = mo.MB()
    hw, hh = w / 2 - inset, h / 2 - inset
    for half, other, horiz in ((hw, hh, True), (hh, hw, False)):
        n = round(2 * half / pitch)
        for i in range(n):
            t = -half + 2 * half * (i + .5) / n
            for sg in (-1, 1):
                mb.at(T((t, y, sg * other) if horiz else (sg * other, y, t)) @ WALL)
                mb.dome(r, r, r * .9, P.mat(mat), 6, 1)
    mb.at()
    return fin(mb, 'dining.mantel_picture.beads')

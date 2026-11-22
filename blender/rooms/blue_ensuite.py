"""blue_ensuite - en-suite bathroom of the rear blue bedroom (first floor). Spec: spec/rooms/blue_ensuite.md
(reconciled blocks at the end win: room x 0.57..2.90 (round 3, dims_1-04), y 11.15..12.85, floor Z 3.04, ceiling
Z 5.54). Round 3: the 0.07 narrower room takes a 1700 x 700 nominal bath (was 750); the south-wall run is bath 0.69 /
gap 0.04 / vanity 0.60 / gap 0.05 / towel rail 0.50 / roll-holder zone 0.46.

The shell built walls, floor (porcelain_pale), ceiling, the cove cornice, the marble_metro wainscot to 1.20 on all
walls, the door (oak 4-panel, opens into the bedroom) and the deep window with its top-hung casement (joinery tags it).
The light switch and the fan isolator are on the bedroom side (rooms/blue_bedroom.py, 'En-suite light').
Here: Calacatta cladding (east wall, shower back wall, window recess) with steel trims, the tile-dado trim, bath with
panel and deck mixer, vanity + basin + mirror with light bands, towel rail, WC, shower tray + sliding screen + the
shared shower control, shelf, fan, accessories, aloe, mat, downlights.  Shared bathroom kit: lib/bath.py.
"""
from math import cos, sin, pi

import bpy
from mathutils import Vector

from lib import bath, interact as IX, lighting, materials as M, mouldings as mo, props as P, shell
from lib.bath import _loft

import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:                           # build.py loads this file by path: make the helper importable
    sys.path.insert(0, _HERE)
import blue_ensuite_slab as SL

ROOM = 'blue_ensuite'
X0, X1, Y0, Y1 = 0.57, 2.90, 11.15, 12.85          # inside wall faces (build() checks them against the spec)
FZ, CZ = 3.04, 5.54                                 # floor, ceiling (world Z)
SH_X, SH_Y = 2.10, 11.75                            # shower tray front edge / return plane
GL_X = 2.13                                         # glass front: on the tray 30 mm in from its edge, so the
                                                    # sliding pane clears the door architrave (outer edge x 2.101)
BATH_W = 0.688                                      # 1700 x 700 nominal bath (rim lip 0.693): stops 2 mm short
                                                    # of the door architrave (x 1.265) at the north end
VA_X0, VA_X1 = 1.29, 1.89                           # vanity: 37 mm off the bath panel
RAIL_X = 2.19                                       # towel rail centre (50 mm east of the vanity)
WIN_Y0, WIN_Y1, WIN_Z0, WIN_Z1 = 11.28, 11.68, FZ + 1.30, FZ + 2.10   # window hole in the false-wall face

CAMERAS = [
    dict(name='door', pos=(1.80, 12.80, 4.65), look=(2.05, 11.15, 3.75), fov_deg=105, ref='v3 f_0359'),
    dict(name='bath', pos=(1.80, 12.30, 4.60), look=(0.70, 11.50, 3.50), fov_deg=100, ref='v3 f_0364'),
    dict(name='basin', pos=(1.60, 12.20, 4.60), look=(1.60, 11.15, 4.20), fov_deg=90, ref='v3 f_0371'),
    dict(name='wc', pos=(1.95, 11.75, 4.45), look=(2.90, 11.48, 3.90), fov_deg=100, ref='v3 f_0387'),
    dict(name='shower', pos=(1.75, 11.60, 4.50), look=(2.60, 12.60, 4.40), fov_deg=100, ref='v3 f_0391'),
    dict(name='north', pos=(1.40, 11.40, 4.60), look=(1.20, 12.85, 4.30), fov_deg=100, ref='v3 f_0409'),
    dict(name='window', pos=(2.30, 11.48, 4.40), look=(3.30, 11.48, 4.80), fov_deg=90, ref='v3 f_0417'),
]

CHARCOAL = '#2B2D30'                                # vanity, bath panel (satin)


def _charcoal():
    return M.paint(CHARCOAL, 0.45)


def _add(ctx, ob, kind='fit', **kw):
    return ctx.add(ob, ROOM, kind, **kw)


def _ring(x0, x1, y0, y1, radii, z, k=6):
    """Rounded rectangle, counter-clockwise from above, corners SW SE NE NW with radii (sw, se, ne, nw), k+1 points
    per corner (equal counts for any radii, so rings loft)."""
    out = []
    for (cx, cy, a0), r in zip(((x0, y0, pi), (x1, y0, 1.5 * pi), (x1, y1, 0.0), (x0, y1, 0.5 * pi)), radii):
        r = max(r, 1e-4)
        ox, oy = cx + (r if cx == x0 else -r), cy + (r if cy == y0 else -r)
        out += [(ox + r * cos(a0 + pi / 2 * i / k), oy + r * sin(a0 + pi / 2 * i / k), z) for i in range(k + 1)]
    return out


def _inset(x0, x1, y0, y1, dx, dy):
    return x0 + dx, x1 - dx, y0 + dy, y1 - dy


# ----------------------------------------------------------------------------- sanitaryware (own meshes)
@P._prop
def _tub(b, w, l, h):
    """Double-ended acrylic bath, origin = floor at the wall-side back corner (x 0 = wall, +x = room side, y along
    the length). Rim h, 0.09 tap deck on the wall side, 40 mm rims elsewhere, sloped ends, floor 0.40 below the rim."""
    c = 'ceramic_white'
    outer = lambda z: _ring(0, w + .005, 0, l, (.001, .012, .012, .001), z)
    inner = (.09, w - .035, .04, l - .04)
    rings = [_ring(*inner, (.07,) * 4, h)]
    for dz, sx, ex, r in ((.006, .004, .004, .066), (.10, .012, .07, .07), (.25, .022, .17, .08), (.36, .03, .23, .09),
                          (.40, .034, .25, .09)):
        rings.append(_ring(*_inset(*inner, sx, ex), (r,) * 4, h - dz))
    b.add(_loft(rings, cap_first=False), c, 60)                       # inner shell + floor
    b.add(_loft([outer(h), rings[0]], False, False), c)               # rim top
    b.add(_loft([outer(h - .03), outer(h)], False, False), c, 60)     # rim lip
    fx, fy = (inner[0] + inner[1]) / 2, l / 2
    b.add(P._lathe([(0, 0), (.032, 0), (.032, .003), (.026, .006), (0, .007)], 20), 'chrome', True,
          T=P.Tr(fx, fy, h - .40 + .0005))                            # click-clack waste
    xo = inner[1] - .030                                              # overflow knob on the room-side inner wall
    b.add(P._lathe([(0, 0), (.030, 0), (.030, .004), (.024, .008), (.022, .016), (0, .018)], 20), 'black_gloss', True,
          T=P.Tr(xo, fy, h - .16) @ P.Rot('Y', -90))
    b.add(P._lathe([(.030, 0), (.034, 0), (.034, .003), (.030, .004)], 20), 'chrome', True,
          T=P.Tr(xo, fy, h - .16) @ P.Rot('Y', -90))


@P._prop
def _basin(b, w, d, h):
    """Semi-recessed rectangular basin, origin = back centre at its underside; front toward +y. One tap hole on the
    0.09 back deck, bowl floor 0.105 below the rim, rounded front corners."""
    c = 'ceramic_white'
    o = (-w / 2, w / 2, 0, d)
    rad = (.012, .012, .07, .07)                                      # back corners (sw, se) sharp-ish, front round
    outer = [_ring(*_inset(*o, .005, .0), rad, 0), _ring(*o, rad, .006), _ring(*o, rad, h - .008),
             _ring(*_inset(*o, .005, .0), rad, h - .001)]
    b.add(_loft(outer, cap_first=True, cap_last=False), c, 60)
    inner = (-w / 2 + .03, w / 2 - .03, .09, d - .03)
    rim = _ring(*inner, (.03, .03, .055, .055), h)
    b.add(_loft([_ring(*_inset(*o, .005, .0), rad, h - .001), rim], False, False), c, 60)
    bowl = [rim] + [_ring(*_inset(*inner, s, s), (r,) * 4, h - dz) for s, dz, r in
                    ((.004, .006, .05), (.02, .055, .05), (.045, .095, .05), (.055, .105, .04))]
    b.add(_loft(bowl, cap_first=False), c, 60)
    b.add(P._lathe([(0, 0), (.020, 0), (.020, .002), (.016, .005), (0, .006)], 16), 'chrome', True,
          T=P.Tr(0, (inner[2] + inner[3]) / 2, h - .105 + .0005))
    b.add(P._box((-.025, d - .0335, h - .028), (.025, d - .0325, h - .020)), 'black_matt')   # overflow slot


# ----------------------------------------------------------------------------- build
def build(ctx):
    xs, ys = zip(*ctx.room_poly(ROOM))
    got = (min(xs), max(xs), min(ys), max(ys))
    assert all(abs(a - b) < .002 for a, b in zip(got, (X0, X1, Y0, Y1))), f'{ROOM}: spec room box {got} moved: re-fit'
    _walls(ctx)
    _bath(ctx)
    _vanity(ctx)
    _wall_south(ctx)
    _wc(ctx)
    _shower(ctx)
    _extras(ctx)
    _lights(ctx)


def _walls(ctx):
    """Calacatta slab cladding (east wall, shower back wall, window recess) + steel trims; the dado tile trim. The
    slab is the en-suite's own grey-veined texture (blue_ensuite_slab: the library slab reads orange-tan here)."""
    S, slab = 'porcelain_calacatta_slab', SL.mat()
    door = ctx.opening_frame('d_ensuite')
    xe = door['center'].x + door['width'] / 2 + .075                   # outer edge of the east architrave: the
    pieces = [('e.n', 2.898, X1, WIN_Y1, Y1, FZ, CZ), ('e.s', 2.898, X1, Y0, WIN_Y0, FZ, CZ),
              ('e.lo', 2.898, X1, WIN_Y0, WIN_Y1, FZ, WIN_Z0), ('e.hi', 2.898, X1, WIN_Y0, WIN_Y1, WIN_Z1, CZ),
              ('n', xe, X1, Y1 - .002, Y1, FZ, CZ)]                     # shower back wall slab starts at it (t408)
    xf = _window_frame_x(ctx)
    pieces += [('r.s', X1, xf, WIN_Y0, WIN_Y0 + .002, WIN_Z0, WIN_Z1), ('r.n', X1, xf, WIN_Y1 - .002, WIN_Y1, WIN_Z0, WIN_Z1),
               ('r.lo', X1, xf, WIN_Y0, WIN_Y1, WIN_Z0, WIN_Z0 + .002), ('r.hi', X1, xf, WIN_Y0, WIN_Y1, WIN_Z1 - .002, WIN_Z1)]
    for n, *bx in pieces:
        ob = shell.box(f'{ROOM}.cladding.{n}', *bx, S)
        ob.data.materials[0] = slab
        M.uv_box(ob, origin=(SH_X, Y0, FZ + 1.20))                    # slab joint at 1.20 (f_0385)
        _add(ctx, ob)
    mb = mo.MB()                                                       # square-edge steel trim round the recess arrises
    t, x = .009, 2.898
    for a, b_ in (((x - .002, WIN_Y0 - t, WIN_Z0 - t), (x + .006, WIN_Y0 + .001, WIN_Z1 + t)),
                  ((x - .002, WIN_Y1 - .001, WIN_Z0 - t), (x + .006, WIN_Y1 + t, WIN_Z1 + t)),
                  ((x - .002, WIN_Y0, WIN_Z0 - t), (x + .006, WIN_Y1, WIN_Z0 + .001)),
                  ((x - .002, WIN_Y0, WIN_Z1 - .001), (x + .006, WIN_Y1, WIN_Z1 + t))):
        mb.box(a, b_, 'silver_satin', bev=.001)
    # 3 mm light slab joints, 1 mm proud: course joint at 1.20, verticals on the east wall at y 11.325 (30 mm south of
    # the flush plate's south edge 11.355, t384.5: floor to the recess, then recess head to ceiling) and 12.20 (south
    # of the fan, f_0391 / f_0405); the 0.80 back wall is one slab
    gj, zj, xj = M.paint('#E6E3DC', 0.3), FZ + 1.20, 2.897
    mb.box((xj, Y0, zj - .0015), (2.898, Y1 - .002, zj + .0015), gj)
    mb.box((xe, Y1 - .003, zj - .0015), (2.897, Y1 - .002, zj + .0015), gj)
    for y, spans in ((11.325, ((FZ, WIN_Z0 - .01), (WIN_Z1 + .01, CZ))), (12.20, ((FZ, CZ),))):
        for z0, z1 in spans:
            mb.box((xj, y - .0015, z0), (2.898, y + .0015, z1), gj)
    prof = [(0, 0), (.004, 0), (.004, .010), (0, .010)]               # dado trim: 10 mm face, 4 mm proud (as the WC)
    z = FZ + 1.19
    xw = door['center'].x - door['width'] / 2 - .075                   # outer edge of the west architrave
    mb.sweep(prof, [(xw, Y1, z), (X0, Y1, z), (X0, Y0, z), (2.894, Y0, z)], 'steel_brushed')
    _add(ctx, mb.finish(f'{ROOM}.tile_trim'), 'trim')


def _window_frame_x(ctx):
    """Room-side face of the window frame in the deep recess (joinery), else the spec's 0.45 reveal."""
    xs = [v[0] for o in bpy.data.objects if 'w_ensuite' in o.name and o.type == 'MESH'
          for v in (o.matrix_world @ Vector(c) for c in o.bound_box) if WIN_Y0 - .01 < v[1] < WIN_Y1 + .01]
    xs = [x for x in xs if x > X1 + .1]
    return round(min(xs), 3) if xs else X1 + .45


def _bath(ctx):
    ch = _charcoal()
    tub = P.place(_tub(BATH_W, Y1 - Y0 - .002, .56, name=f'{ROOM}.bath'), (X0 + .001, Y0 + .001, FZ))   # 1 mm off the tiles
    _add(ctx, tub, plan_sym='bath')
    xp = X0 + BATH_W - .025                                              # back of the panel, front 5 mm behind the rim lip
    pan = P.place(P.panel_door(Y1 - Y0, .47, t=.02, stile=.075, panels=(3, 1), mat=ch, name=f'{ROOM}.bath.panel'),
                  (xp, (Y0 + Y1) / 2, FZ + .06), facing=(1, 0))
    _add(ctx, pan)
    pl = shell.box(f'{ROOM}.bath.plinth', xp - .02, xp, Y0, Y1, FZ, FZ + .06, CHARCOAL)
    pl.data.materials[0] = ch
    _add(ctx, pl)
    # deck bath-shower mixer on the wall-side deck, spout into the bath; handset parked on the south wall
    mx = bath.bath_mixer(f'{ROOM}.bath_tap', (X0 + .055, 12.05, FZ + .56), FZ + .16, facing=(1, 0))
    bath.add(ctx, ROOM, mx)
    # handset bracket on the west wall just north of the south-west corner (f_0364; the spec's 'W-south' reads the
    # corner the other way)
    hs = P.place(bath.handset(name=f'{ROOM}.bath_tap.handset'), (X0, Y0 + .20, FZ + 1.10), facing=(1, 0))
    _add(ctx, hs)
    foot = hs.matrix_basis @ Vector((0, -.036, -.045))
    union = mx[0].matrix_basis @ Vector((0, .030, .010))
    mb = mo.MB()
    # the hose swings down from the bracket out over the tub, crosses the rim and runs back along the deck behind
    # the south pillar (wall gap 28 mm) to the union under the bridge (v3 t364); it never dips into the 0.09 deck
    m1, m2 = Vector((X0 + .12, 11.78, FZ + .588)), Vector((X0 + .018, 11.90, FZ + .573))
    pts = (P._bez(foot, foot + Vector((.12, .08, -.30)), m1 + Vector((.045, -.09, 0)), m1, 14)[:-1]
           + P._bez(m1, m1 + Vector((-.045, .05, 0)), m2 - Vector((0, .04, 0)), m2, 5)[:-1]
           + P._bez(m2, m2 + Vector((0, .05, 0)), union - Vector((.003, .05, 0)), union, 4))
    assert all(p.z - .007 > FZ + .56 or p.x > X0 + .10 for p in pts), f'{ROOM}: bath hose cuts the tap deck'
    mb.tube(pts, .007, 'chrome', n=8)
    _add(ctx, mb.finish(f'{ROOM}.bath_tap.hose'))


def _vanity(ctx):
    """Free-standing charcoal shaker vanity on legs (x 1.30..1.90, 0.38 deep), two doors hinged at the outer edges,
    basin on top, mono mixer."""
    ch = _charcoal()
    xa, xb, d, zc0, zc1 = VA_X0, VA_X1, .38, FZ + .10, FZ + .70
    xc, yf = (xa + xb) / 2, Y0 + d
    car = P.place(P.cabinet_carcass(xb - xa, d, zc1 - zc0, mat=ch, plinth=0, open_front=True, shelves=1, inner=ch,
                                    name=f'{ROOM}.vanity'), (xc, Y0, zc0), facing=(0, 1))
    _add(ctx, car, plan_sym='vanity')
    for i, (x, y) in enumerate(((xa + .02, Y0 + .02), (xb - .02, Y0 + .02), (xa + .02, yf - .02), (xb - .02, yf - .02))):
        _add(ctx, P.place(P.box(.035, .035, .10, mat=ch, name=f'{ROOM}.vanity.leg.{i}'), (x, y, FZ)))
    rail = shell.box(f'{ROOM}.vanity.rail', xa, xb, yf, yf + .02, zc1 - .09, zc1, CHARCOAL)
    rail.data.materials[0] = ch
    _add(ctx, rail)
    dw, dz0, dh = (xb - xa) / 2 - .003, zc0 + .015, .48
    # west door hinges on its west edge, east on its east; the west one stops at 80 deg so its pull clears the bath rim
    for side, sgn, deg in (('w', -1, 80), ('e', 1, -100)):
        x = xc + sgn * (dw / 2 + .0015)
        door = P.place(P.panel_door(dw, dh, t=.02, stile=.06, mat=ch, name=f'{ROOM}.vanity.door.{side}'),
                       (x, yf, dz0), facing=(0, 1))
        pull = P.place(P.handle_d(.10, vertical=True, finish='chrome', name=f'{ROOM}.vanity.door.{side}.pull'),
                       (xc + sgn * .035, yf + .02, dz0 + dh - .09), facing=(0, 1))
        IX.tag_many([door, pull], 'hinge', g=f'{ROOM}.vanity.{side}', label='Cupboard',
                    p=(x + sgn * dw / 2, yf, dz0), deg=deg)
        _add(ctx, door, lm='dynamic'); _add(ctx, pull, lm='dynamic')
    bs = P.place(_basin(xb - xa, .46, .16, name=f'{ROOM}.basin'), (xc, Y0, zc1))
    _add(ctx, bs)                                                      # the vanity symbol draws the bowl
    bath.add(ctx, ROOM, bath.basin_mixer(f'{ROOM}.tap', (xc, Y0 + .045, zc1 + .16), zc1 + .055, facing=(0, 1)))


def _wall_south(ctx):
    """Mirror with light bands, accessories above the basin, towel rail + hooks, roll holder."""
    xc, zm = (VA_X0 + VA_X1) / 2, FZ + 1.24
    mb = mo.MB()
    mb.box((-.25, -.006, 0), (.25, 0, .72), 'mirror', bev=.0015)
    mir = P.place(mb.finish(f'{ROOM}.mirror'), (xc, Y0, zm), facing=(0, 1))
    _add(ctx, mir, 'decor', plan_sym='mirror')
    mb = mo.MB()                                                       # frosted LED bands, 40 mm, 50 mm in from the sides
    for sx in (-1, 1):
        x0 = sx * (.25 - .05)
        mb.face([(x0, -.0066, .05), (x0 - sx * .04, -.0066, .05), (x0 - sx * .04, -.0066, .67), (x0, -.0066, .67)],
                P.emissive('#F6DCB4', 1.0), hint=(0, -1, 0))
    _add(ctx, P.place(mb.finish(f'{ROOM}.mirror.light'), (xc, Y0, zm), facing=(0, 1)), 'light')
    # z 1.03 (f_0359, f_0371 - the spec's x are mirrored): soap dish in a chrome ring EAST of the tap, chrome double
    # tumbler holder with two frosted tumblers WEST of it
    za, xs, xt = FZ + 1.03, xc + .22, xc - .22
    ring = lambda cx, cy: [(cx + .038 * cos(a * pi / 8), cy + .038 * sin(a * pi / 8), za) for a in range(16)]
    mb = mo.MB()
    for x in (xs, xt):
        mb.box((x - .018, Y0, za - .018), (x + .018, Y0 + .012, za + .018), 'chrome', bev=.002)
    mb.tube([(xs, Y0 + .01, za), (xs, Y0 + .03, za)], .005, 'chrome', n=8)
    mb.tube(ring(xs, Y0 + .067), .003, 'chrome', n=6, closed=True, up=(0, 0, 1))
    mb.tube([(xt - .06, Y0 + .012, za), (xt + .06, Y0 + .012, za)], .005, 'chrome', n=8)
    for dx in (-.06, .06):
        mb.tube(ring(xt + dx, Y0 + .055), .003, 'chrome', n=6, closed=True, up=(0, 0, 1))
    _add(ctx, mb.finish(f'{ROOM}.accessories'), 'decor')
    dish = mo.MB()
    dish.lathe([(0, 0), (.03, 0), (.045, .012), (.047, .016), (.043, .016), (.03, .006), (0, .006)], 'glass_frosted', segs=20)
    _add(ctx, P.place(dish.finish(f'{ROOM}.soap_dish'), (xs, Y0 + .067, za - .006)), 'decor')
    for i, dx in enumerate((-.06, .06)):
        _add(ctx, P.place(P.tumbler(.095, .066, mat='glass_frosted', name=f'{ROOM}.tumbler.{i}'),
                          (xt + dx, Y0 + .055, za - .03)), 'decor')
    # towel rail 0.50 x 1.50, bottom 0.33 (f_0359), three black robe hooks on the top group
    rail = P.place(bath.towel_rail(.5, 1.5, mat='anthracite', name=f'{ROOM}.towel_rail'), (RAIL_X, Y0, FZ + .33),
                   facing=(0, 1))
    _add(ctx, rail, plan_sym='towel_rail')
    hk = mo.MB()
    for x in (RAIL_X - .12, RAIL_X, RAIL_X + .12):
        hk.tube([(x, Y0 + .068, FZ + 1.77), (x, Y0 + .068, FZ + 1.74), (x, Y0 + .105, FZ + 1.72), (x, Y0 + .115, FZ + 1.75)],
                .004, 'black_matt', n=6)
    _add(ctx, hk.finish(f'{ROOM}.robe_hooks'), 'decor')
    # antique-brass open-arm roll holder (f_0387)
    rh = mo.MB()
    rh.box((-.045, -.010, -.028), (.045, 0, .028), 'brass_antique', bev=.002)
    rh.tube([(.03, -.008, 0), (.03, -.062, 0), (-.115, -.062, 0)], .0055, 'brass_antique', n=8)
    rh.tube([(-.02, -.010, -.02), (.0, -.03, -.03), (.03, -.05, -.012), (.03, -.06, 0)], .003, 'brass_antique', n=6)
    _add(ctx, P.place(rh.finish(f'{ROOM}.roll_holder'), (2.62, Y0, FZ + .72), facing=(0, 1)), 'decor')


def _wc(ctx):
    bath.add(ctx, ROOM, bath.wc(f'{ROOM}.wc', (2.898, 11.48, FZ), facing=(-1, 0), top=.44, clear=.06, flush_z=1.0),
             plan_sym='wc')
    br = mo.MB()                                                       # brushed-steel toilet brush holder
    br.lathe([(0, 0), (.043, 0), (.045, .004), (.045, .115), (.040, .12), (.012, .124), (0, .124)], 'steel_brushed', segs=20)
    br.tube([(0, 0, .12), (0, 0, .36)], .006, 'steel_brushed', n=8)
    br.lathe([(0, .35), (.012, .352), (.013, .37), (0, .38)], 'steel_brushed', segs=12)
    _add(ctx, P.place(br.finish(f'{ROOM}.brush'), (2.80, 11.215, FZ)), 'decor')


def _shower(ctx):
    """Stone-resin tray 0.80 x 1.10, sliding front (door on the north end slides south), fixed return, control."""
    tz = FZ + .04
    tray = shell.box(f'{ROOM}.shower.tray', SH_X, 2.898, SH_Y, Y1 - .002, FZ, tz, '#F1F0EC')
    tray.data.materials[0] = M.solid('stone_resin_white', '#F1F0EC', 0.4)
    _add(ctx, tray, plan_sym='shower')
    mb = mo.MB()                                                       # slot drain 0.30, 0.10 off the east wall
    yc = (SH_Y + Y1) / 2
    mb.box((2.785, yc - .155, tz - .001), (2.815, yc + .155, tz + .0015), 'steel_brushed', bev=.001)
    mb.box((2.795, yc - .145, tz + .0015), (2.805, yc + .145, tz + .0018), 'black_matt')
    _add(ctx, mb.finish(f'{ROOM}.shower.drain'))
    w = Y1 - .002 - SH_Y
    bath.add(ctx, ROOM, bath.shower_slider(f'{ROOM}.screen', (GL_X, SH_Y + w / 2, tz), w, facing=(-1, 0), height=2.0,
                                           door='left', finish='silver_satin'))
    xr0, xr1 = GL_X + .018, 2.898 - .008                               # the wall channel's 8 mm stays proud of the slab
    ret = P.place(bath.glass_pane(xr1 - xr0, 2.0, channel='right', name=f'{ROOM}.screen.return'),
                  ((xr0 + xr1) / 2, SH_Y, tz), facing=(0, -1))
    _add(ctx, ret)
    bath.add(ctx, ROOM, bath.shower_set(f'{ROOM}.shower', (2.55, Y1 - .002, FZ), facing=(0, -1), to_z=tz, basket_z=1.35))


def _extras(ctx):
    """Shelf over the bath end, extractor fan, aloe on the window ledge, bath mat."""
    top = FZ + 1.33
    mb = mo.MB()
    mb.box((X0 + .05, Y1 - .12, top - .02), (X0 + .60, Y1, top), 'joinery_white', bev=.003)
    cove = [(0, 0), (.012, .006), (.035, .022), (.06, .040), (.08, .052), (.095, .060), (.10, .07), (0, .07)]
    mb.sweep(cove, [(X0 + .59, Y1, top - .09), (X0 + .06, Y1, top - .09)], 'joinery_white')
    _add(ctx, mb.finish(f'{ROOM}.shelf'), plan_sym='shelf')
    fan = mo.MB()                                                      # white wall fan with a round louvre
    x, y, z = 2.898, 12.45, FZ + 2.25
    fan.box((x - .022, y - .075, z - .075), (x, y + .075, z + .075), 'plastic_white', bev=.004)
    fan.at(P.Tr(x - .022, y, z) @ P.Rot('Y', -90))
    fan.lathe([(.052, 0), (.05, .002), (.03, .002), (.03, .004), (0, .004)], 'plastic_white', segs=24)
    fan.lathe([(.008, .0045), (.008, .006), (0, .006)], 'plastic_white', segs=12)
    fan.at(None)
    _add(ctx, fan.finish(f'{ROOM}.fan'))
    _aloe(ctx, (3.00, (WIN_Y0 + WIN_Y1) / 2, WIN_Z0 + .002))
    mat_o = P.place(P.rug(None, .50, .85, thickness=.008, color='#9E9E9B', name=f'{ROOM}.mat'), (1.82, 12.22, FZ))
    mat_i = P.place(P.rug(None, .36, .70, thickness=.011, color='#B9B9B5', name=f'{ROOM}.mat.field'), (1.82, 12.22, FZ))
    _add(ctx, mat_o, 'decor', plan_sym='rug'); _add(ctx, mat_i, 'decor')


def _aloe(ctx, at):
    """Aloe in a black pot at the front of the ledge: long arching strap leaves fanning out into the room (f_0385,
    f_0417). A leaf may only spread sideways once it has left the 0.40 recess: one that would cut a jamb is turned
    toward -x and shortened until it clears."""
    import random
    rnd = random.Random(7)
    pot = mo.MB()
    pot.lathe([(0, 0), (.055, 0), (.065, .11), (.068, .12), (.062, .12), (.055, .02), (0, .02)], 'black_gloss', segs=20)
    pot.lathe([(.061, .105), (0, .105)], P.mat('soil'), segs=16)
    _add(ctx, P.place(pot.finish(f'{ROOM}.plant.pot'), at), 'decor')    # on the ledge: no plan symbol
    lv = mo.MB()
    leaf = P.two_sided(M.solid('aloe_leaf', '#6F8A63', 0.5))      # fleshy grey-green (t384.5, f_0421)
    half = (WIN_Y1 - WIN_Y0) / 2 - .015                                # clear half-width of the recess
    # out of the recess a leaf may spread sideways, but stays south of the shower return pane (y 11.75)
    clear = lambda p: (at[0] + p.x < X1 and at[1] + p.y < SH_Y - .015) or (abs(p.y) < half and at[0] + p.x < 3.30)

    def rows_of(a, L, rise):
        d, s = Vector((cos(a), sin(a), 0)), Vector((-sin(a), cos(a), 0))
        p0 = Vector((0, 0, .10)) + d * .015
        pts = P._bez(p0, p0 + Vector((0, 0, rise)) + d * .03, p0 + d * L * .75 + Vector((0, 0, rise * 1.1)),
                     p0 + d * L + Vector((0, 0, rise * .1 - .07)), 8)
        out = []
        for k, c in enumerate(pts):
            hw = .022 * (1 - k / len(pts)) ** .8 + .001
            out.append([c - s * hw, c + Vector((0, 0, .012 * (1 - k / 8))), c + s * hw])   # V-section
        return out

    for i in range(11):
        a = pi + 1.05 * (2 * i / 10 - 1) + rnd.uniform(-.1, .1)      # fan of +-60 deg about -x (into the room)
        L, rise = rnd.uniform(.26, .42), rnd.uniform(.06, .16)
        rows = rows_of(a, L, rise)
        while not all(clear(p) for r in rows for p in r):
            a, L = pi + (a - pi) * .85, L * .97
            rows = rows_of(a, L, rise)
        for r0, r1 in zip(rows, rows[1:]):
            for j in range(2):
                lv.face([r0[j], r0[j + 1], r1[j + 1], r1[j]], leaf, hint=(0, 0, 1))
    _add(ctx, P.place(lv.finish(f'{ROOM}.plant.leaves'), at), 'decor')


def _lights(ctx):
    for i, (x, y) in enumerate(((1.48, 11.62), (1.48, 12.40), (2.50, 12.30))):
        lighting.downlight(ctx, ROOM, x, y, watts=60, name=f'{ROOM}.downlight.{i}')
        _add(ctx, P.place(P.downlight(name=f'{ROOM}.downlight_trim.{i}'), (x, y, CZ)), 'light')

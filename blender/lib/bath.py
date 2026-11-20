"""bath.py - shared bathroom fittings, so the three upstairs bathrooms match (green_bathroom, blue_ensuite, bathroom2).

Signatures and examples: blender/lib/README.md, section "bath".  Test: blender/test_bath.py (BATH OK).

Two kinds of function:
  * builders  wc / basin_mixer / bath_filler / bath_mixer / shower_set / shower_slider / glass_door
        take name (= object name prefix AND interaction group prefix), at (world x, y, z) and facing=(nx, ny)
        (or rot_z=deg), and return a LIST of unlinked objects that are already placed and already tagged with
        lib.interact.  parts[0] is the fixed body.  Link them with bath.add(ctx, room, parts, plan_sym=...).
  * props     glass_pane / handset / flush_plate / flush_button / towel_rail
        plain lib.props-style props: one unlinked object, P.place(obj, loc, facing=...), ctx.add(...).
Local frame of everything (lib.props wall convention): the wall / back plane is local y = 0, the front faces local
-Y (P.place aims -Y along `facing`, the wall normal pointing into the room), +X is to the viewer's right, +Z up.
Meshes are cached by argument like props (same arguments -> same mesh datablock).
"""
from math import sin, cos, pi, tau, copysign

from mathutils import Vector

from . import interact as IX, materials as _ML, props as P
from .props import G, Tr, Rot, _prop, _lathe, _tube, _box, _box_round, _bez, _prism, _rrect


# ----------------------------------------------------------------------------- placement / tagging helpers
def _put(objs, at, facing=None, rot_z=None):
    for o in objs:
        P.place(o, at, facing=facing, rot_z=rot_z)
    return objs


def _wp(o, p):
    """Local point of a placed (still unlinked) object -> world."""
    return o.matrix_basis @ Vector(p)


def _wv(o, v):
    return o.matrix_basis.to_3x3() @ Vector(v)


def add(ctx, room, parts, plan_sym=None, kind='fit'):
    """ctx.add every part of a builder's list: parts[0] gets plan_sym, tagged parts are lm='dynamic'."""
    for i, o in enumerate(parts):
        ctx.add(o, room, kind, plan_sym=plan_sym if i == 0 else None, lm='dynamic' if 'ix' in o.keys() else None)
    return parts


def _loft(rings, cap_first=True, cap_last=True):
    """Skin over rings of equal point count (each counter-clockwise seen from +Z, listed bottom -> top)."""
    n = len(rings[0])
    fs = [(i * n + j, i * n + (j + 1) % n, (i + 1) * n + (j + 1) % n, (i + 1) * n + j)
          for i in range(len(rings) - 1) for j in range(n)]
    if cap_first:
        fs.append(tuple(range(n))[::-1])
    if cap_last:
        fs.append(tuple(range((len(rings) - 1) * n, len(rings) * n)))
    g = G([tuple(v) for r in rings for v in r], fs)
    g.soft = 50
    return g


def _cyl(b, p0, p1, r, mat, seg=12):
    b.add(_tube([p0, p1], r, seg), mat, True, closed=True)


def _disc_y(b, x, y, z, r, length, mat, seg=16):
    """Cylinder with its axis along -Y: from the plane y to y - length."""
    b.add(_lathe([(0, 0), (r, 0), (r, length), (0, length)], seg), mat, True, T=Tr(x, y, z) @ Rot('X', 90))


# ----------------------------------------------------------------------------- WC
def _d_ring(z, w, length, yw=0.0, n=16):
    """D-shaped pan outline at height z: flat on the plane y = yw, parallel sides for 65 % of the projection, blunt
    nose toward -Y (superellipse, exponent 2.5). Counter-clockwise seen from above. (rooms/wc.py, turned 90 deg.)"""
    b, ls, e = w / 2, length * .65, .8
    pts = [(b, yw, z), (-b, yw, z)]
    for i in range(n + 1):
        th = pi / 2 + pi * i / n
        c, s = cos(th), sin(th)
        pts.append((-b * copysign(abs(s) ** e, s), yw - ls - (length - ls) * abs(c) ** e, z))
    return pts


_PAN = {   # (height fraction clear -> rim, width, projection) of the 0.36 x 0.53 pan
    'wall_hung': ((0, .15, .22), (.034, .21, .31), (.151, .275, .41), (.352, .32, .48), (.621, .348, .515),
                  (.889, .36, .53), (.987, .36, .53), (1, .352, .522)),
    # pedestal to the floor, bowl oversailing it at the front and sides (v5 f_0112)
    'back_to_wall': ((0, .215, .36), (.02, .225, .37), (.50, .235, .38), (.66, .29, .44), (.80, .345, .51),
                     (.90, .36, .53), (.987, .36, .53), (1, .352, .522)),
}


@_prop
def _pan(b, kind, w, proj, top, clear):
    rim, sw, sl = top - .040, w / .36, proj / .53
    z0 = clear if kind == 'wall_hung' else 0.0
    c = 'ceramic_white'
    b.add(_loft([_d_ring(z0 + t * (rim - z0), ww * sw, ll * sl) for t, ww, ll in _PAN[kind]], cap_last=False), c, 50)
    yb = -.10 * sl                                          # back of the bowl opening: the deck behind it carries the hinges
    bowl = _loft([_d_ring(rim, .352 * sw, .522 * sl)] + [_d_ring(rim - dz, ww * sw, ll * sl, yb) for dz, ww, ll in (
        (0, .272, .382), (.007, .256, .368), (.063, .228, .335), (.133, .170, .255), (.183, .120, .170))], cap_first=False)
    water = _ML.solid('wc_pan_water', '#C3CDCE', 0.03)      # the cap of the last ring = the water surface
    b.add(bowl, [c] * (len(bowl.f) - 1) + [water], 50)
    for sx in (-1, 1):                                      # hinge caps
        b.add(_box((sx * .085 - .022, -.046, rim), (sx * .085 + .022, -.004, rim + .026), .006), c, closed=True)


def _seat_ring(w, proj, z, ww, ll):
    return _d_ring(z, ww * w / .36, ll * proj / .53 - .042, -.042)


@_prop
def _seat(b, w, proj, top):
    rim = top - .040
    hole = lambda z: _d_ring(z, .232 * w / .36, .365 * proj / .53, -.112)
    o = lambda dz, ww, ll: _seat_ring(w, proj, rim + dz, ww, ll)
    b.add(_loft([hole(rim + .0045), o(.004, .350, .520), o(.0045, .370, .535), o(.0175, .370, .535),
                 o(.0185, .360, .530), hole(rim + .0185), hole(rim + .0045)], False, False), 'ceramic_white', 50)


@_prop
def _lid(b, w, proj, top):
    rim = top - .040
    b.add(_loft([_seat_ring(w, proj, rim + dz, ww, ll) for dz, ww, ll in (
        (.021, .360, .530), (.022, .370, .535), (.034, .370, .535), (.038, .362, .531), (.040, .336, .512))]),
        'ceramic_white', 50)


@_prop
def flush_plate(b, w=.25, h=.16, finish='chrome'):
    """Dual-flush plate, 10 mm proud, two push panels either side of a dark gap. Wall prop: origin centre of the back."""
    b.add(_prism(_rrect(w, h, .010), -.010, 0), finish, closed=True)
    for sx in (-1, 1):
        b.add(_prism(_rrect(w / 2 - .011, h - .018, .006, cx=sx * (w / 4 - .0035)), -.013, -.010), finish, closed=True)
    b.add(_box((-.002, -.0105, -h / 2 + .012), (.002, -.010, h / 2 - .012)), 'black_matt', closed=True)


@_prop
def flush_button(b, dia=.05, finish='chrome'):
    """Round dual-flush push button in a ring (furniture WC unit). Wall prop: origin centre of the back."""
    r = dia / 2
    b.add(_lathe([(0, 0), (r + .008, 0), (r + .008, .004), (r + .002, .007), (r, .007), (r, .012), (r - .004, .014),
                  (0, .014)], 20), finish, True, T=Rot('X', 90))


def wc(name, at, facing=None, rot_z=None, kind='wall_hung', w=.36, proj=.53, top=.42, clear=.085, lift=90,
       flush='plate', flush_z=1.0, label='Toilet'):
    """White D-shaped pan with a wrap-over soft-close seat and lid -> [pan, seat, lid(, flush)].
    kind 'wall_hung' (underside `clear` above the floor) | 'back_to_wall' (pedestal to the floor).
    at = point on the wall / furniture front the pan backs onto, at FLOOR level, on the pan's centre line;
    top = top of the shut lid (bowl rim = top - 0.04). flush: 'plate' | 'button' | None, centred flush_z above `at`
    on the same plane (not tagged: the ground-floor WC has no flush interaction).
    Groups: '<name>.lid' and '<name>.seat' (needs the lid) - each lifts `lift` deg about the hinge line 32 mm off
    the wall (90 = vertical, 9 mm clear of the wall; as rooms/wc.py)."""
    pan = _pan(kind, w, proj, top, clear, name=name)
    seat, lid = _seat(w, proj, top, name=name + '.seat'), _lid(w, proj, top, name=name + '.lid')
    parts = _put([pan, seat, lid], at, facing, rot_z)
    hinge = dict(p=_wp(pan, (0, -.032, top - .023)), a=_wv(pan, (-1, 0, 0)), deg=lift)
    IX.tag(lid, 'hinge', label=label + ' lid', **hinge)
    IX.tag(seat, 'hinge', label=label + ' seat', needs=lid.name, **hinge)
    if flush:
        fl = flush_plate(name=name + '.flush') if flush == 'plate' else flush_button(name=name + '.flush')
        fl.location, fl.rotation_euler = _wp(pan, (0, 0, flush_z)), pan.rotation_euler
        parts.append(fl)
    return parts


# ----------------------------------------------------------------------------- taps
TAP = {   # style: (spout outlet y, outlet z, lever pivot z) above the deck, local
    'mono': (-.104, .066, .108),     # chrome monobloc, flat top lever (en-suite v3 f_0375, bathroom2)
    'pin': (-.108, .096, .150),      # slim brushed-brass cylinder, straight spout, pin lever (green bathroom v4 f_0152)
}


@_prop
def _mixer(b, style, finish):
    if style == 'mono':
        b.add(_lathe([(0, 0), (.027, 0), (.027, .004), (.0225, .008), (.0225, .097), (.019, .106), (0, .107)], 20),
              finish, True)
        b.add(_tube([(0, -.010, .046), (0, -.070, .074), (0, -.108, .082)], [.015, .013, .0115], 10), finish, True, closed=True)
        b.add(_lathe([(0, 0), (.009, 0), (.009, .010), (0, .010)], 10), finish, True, T=Tr(0, -.104, .066))   # aerator
    else:
        b.add(_lathe([(0, 0), (.022, 0), (.022, .004), (.017, .007), (.017, .140), (.008, .141), (.008, .150), (0, .150)], 16),
              finish, True)
        b.add(_tube([(0, -.008, .112), (0, -.112, .104)], .0095, 10), finish, True, closed=True)
        b.add(_lathe([(0, 0), (.007, 0), (.007, .008), (0, .008)], 10), finish, True, T=Tr(0, -.108, .096))


@_prop
def _mixer_lever(b, style, finish):
    """Origin = the pivot (top of the body); the lever points -Y and lifts about +X by a negative angle."""
    if style == 'mono':
        b.add(_box_round((-.012, -.088, 0), (.012, .016, .008), .003), finish, True, T=Rot('X', -8))
    else:
        b.add(_lathe([(0, 0), (.017, 0), (.0165, .006), (.014, .011), (.009, .015), (0, .017)], 16), finish, True)   # ball cap
        b.add(_tube([(0, 0, .008), (0, -.052, .026)], .004, 8), finish, True, closed=True)


def _tap_tags(name, label, trigger, lever, hinge, water_at, to_z, splash):
    """Shared tap wiring: body = trigger, lever = hinge, stream from the outlet down to world z `to_z` = show."""
    water = P.place(P.water_stream(round(water_at.z - to_z, 3), splash=splash, name=name + '.water'), water_at)
    IX.tag(trigger, 'trigger', g=name, label=label)
    if lever is not None:
        IX.tag(lever, 'hinge', g=name, label=label, **hinge)
    IX.tag(water, 'show', g=name, label=label, when=1, fx='water')
    return water


def basin_mixer(name, at, to_z, facing=None, rot_z=None, style='mono', finish='chrome', label='Tap'):
    """Basin monobloc mixer -> [body, lever, water]. at = centre of the tap base on the basin deck; the spout points
    along `facing` (the normal of the wall behind the basin). to_z = WORLD z of the bowl floor under the spout (the
    outlet is TAP[style] = (y, z, pivot z) from `at`). style 'mono' | 'pin'; finish e.g. 'chrome' / 'brass_antique'.
    Group '<name>': body trigger, lever hinge 20 deg up, water show."""
    body, lever = _mixer(style, finish, name=name), _mixer_lever(style, finish, name=name + '.lever')
    oy, oz, pz = TAP[style]
    P.place(body, at, facing=facing, rot_z=rot_z)
    lever.location, lever.rotation_euler = _wp(body, (0, 0, pz)), body.rotation_euler
    water = _tap_tags(name, label, body, lever, dict(p=lever.location, a=_wv(body, (1, 0, 0)), deg=-20),
                      _wp(body, (0, oy, oz)), to_z, .05)
    return [body, lever, water]


@_prop
def _filler(b, finish, h, reach):
    """Floor-standing bath filler: base, column, mixer block, swan neck arching `reach` toward -Y, pencil hand shower
    in a cradle with its hose."""
    R, f = reach / 2, finish
    b.add(_lathe([(0, 0), (.07, 0), (.07, .010), (.062, .016), (.022, .020), (.019, .74), (.026, .745), (.026, .815),
                  (.019, .82), (0, .82)], 20), f, True)
    neck = [(0, 0, .80), (0, 0, h - R)] + [(0, -R + R * cos(pi * i / 16), h - R + R * sin(pi * i / 16)) for i in range(1, 17)]
    neck.append((0, -reach, h - R - .05))
    b.add(_tube(neck, .012, 10), f, True, closed=True)
    _cyl(b, (-.026, 0, .78), (-.040, 0, .78), .017, f)                       # lever boss (the lever is its own object)
    _cyl(b, (.026, 0, .80), (.060, 0, .80), .007, f, 8)                      # cradle arm
    _cyl(b, (.060, 0, .775), (.060, 0, .81), .013, f, 10)                    # cradle
    b.add(_tube([(.060, 0, .80), (.066, -.012, .94), (.070, -.020, 1.02)], [.010, .011, .011], 10), f, True, closed=True)
    b.add(_tube(_bez((.060, 0, .775), (.075, .02, .50), (.03, .03, .48), (.012, .018, .70), 12), .006, 6), f, True, closed=True)


@_prop
def _filler_lever(b, finish):
    """Origin = pivot on the lever boss; the lever points -X and lifts about +Y by a positive angle."""
    _cyl(b, (0, 0, 0), (-.012, 0, 0), .015, finish)
    b.add(_tube([(-.008, 0, 0), (-.070, 0, .004)], [.005, .004], 8), finish, True, closed=True)


def bath_filler(name, at, to_z, facing=None, rot_z=None, finish='brass_antique', h=1.10, reach=.22, label='Bath tap'):
    """Floor-standing bath filler (green bathroom) -> [body, lever, water]. at = centre of the base on the floor; the
    swan neck rises to `h` and arches `reach` along `facing` (toward the bath). to_z = WORLD z of the bath floor.
    Group '<name>': body trigger, side lever hinge 25 deg, water show."""
    body, lever = _filler(finish, h, reach, name=name), _filler_lever(finish, name=name + '.lever')
    P.place(body, at, facing=facing, rot_z=rot_z)
    lever.location, lever.rotation_euler = _wp(body, (-.040, 0, .78)), body.rotation_euler
    water = _tap_tags(name, label, body, lever, dict(p=lever.location, a=_wv(body, (0, 1, 0)), deg=25),
                      _wp(body, (0, -reach, h - reach / 2 - .05)), to_z, .09)
    return [body, lever, water]


@_prop
def _deck_mixer(b, finish):
    """Deck bath-shower mixer: two pillar valves with lever heads 0.18 apart, bridge, central spout toward -Y."""
    f = finish
    for sx in (-1, 1):
        b.add(_lathe([(0, 0), (.027, 0), (.027, .004), (.017, .010), (.015, .040), (.021, .046), (.021, .070),
                      (.012, .080), (0, .081)], 16), f, True, T=Tr(sx * .09, 0, 0))
        b.add(_tube([(sx * .09, 0, .066), (sx * .145, 0, .074)], [.006, .0045], 8), f, True, closed=True)   # lever
    _cyl(b, (-.09, 0, .034), (.09, 0, .034), .014, f)
    b.add(_tube([(0, 0, .034), (0, -.070, .050), (0, -.105, .040)], [.015, .012, .011], 10), f, True, closed=True)
    b.add(_lathe([(0, 0), (.011, 0), (.011, .020), (0, .022)], 12), f, True, T=Tr(0, 0, .046))               # diverter
    _cyl(b, (0, .0, .022), (0, .030, .010), .008, f, 8)                                                     # hose union


def bath_mixer(name, at, to_z, facing=None, rot_z=None, finish='chrome', label='Bath tap'):
    """Deck-mounted bath-shower mixer (en-suite) -> [body, water]. at = centre between the two pillars on the bath
    rim; the spout points along `facing` (into the bath). to_z = WORLD z of the bath floor.
    Group '<name>': body (with both heads) trigger, water show. The handset on the wall is bath.handset()."""
    body = P.place(_deck_mixer(finish, name=name), at, facing=facing, rot_z=rot_z)
    return [body, _tap_tags(name, label, body, None, None, _wp(body, (0, -.105, .030)), to_z, .09)]


@_prop
def handset(b, finish='chrome'):
    """Pencil hand shower parked in a wall bracket (en-suite bath). Wall prop: origin = bracket centre on the wall.
    The hose is the room's (a P._tube / mo.MB tube from the handset foot at local (0, -.036, -.045))."""
    _disc_y(b, 0, 0, 0, .017, .014, finish)
    _cyl(b, (0, -.014, 0), (0, -.036, 0), .008, finish, 8)
    b.add(_tube([(0, -.036, -.045), (0, -.040, .06), (0, -.046, .13)], [.009, .011, .012], 10), finish, True, closed=True)


# ----------------------------------------------------------------------------- shower control (the same in every bathroom)
@_prop
def _shower(b, valve_z, head_z, reach, head_dia, basket_z, finish):
    """Exposed thermostatic bar valve, rigid riser to a swan-neck arm and round rain head, hand shower on a sliding
    bracket with its hose, optional wire basket (v3 f_0399, v4_f140, v5 f_0026)."""
    f, yb, vz = finish, -.065, valve_z                       # yb: axis of the bar and the riser off the wall
    grey = 'silver_satin'
    _cyl(b, (-.105, yb, vz), (.105, yb, vz), .021, f, 14)                    # bar
    for sx in (-1, 1):
        _cyl(b, (sx * .108, yb, vz), (sx * .150, yb, vz), .024, f, 14)       # flow / temperature knobs
        _cyl(b, (sx * .075, 0, vz), (sx * .075, yb, vz), .014, f, 10)        # wall unions
        _disc_y(b, sx * .075, 0, vz, .031, .010, f)
    zt, R = head_z + .050, .09                                               # arm height, bend radius
    riser = [(0, yb, vz + .015), (0, yb, zt - R)] + [(0, yb - R + R * cos(pi / 2 * i / 6), zt - R + R * sin(pi / 2 * i / 6))
                                                    for i in range(1, 7)] + [(0, -reach, zt)]
    b.add(_tube(riser, .011, 10), f, True, closed=True)
    zs = zt - R - .06                                                        # wall stay under the bend
    _cyl(b, (0, 0, zs), (0, yb, zs), .008, f, 8)
    _disc_y(b, 0, 0, zs, .022, .008, f)
    _cyl(b, (0, yb, zs - .015), (0, yb, zs + .015), .015, f, 10)
    r = head_dia / 2                                                         # rain head, underside at head_z
    b.add(_lathe([(r - .006, 0), (r, .003), (r, .008), (r - .025, .014), (.035, .020), (.016, .034), (.016, .050),
                  (0, .062)], 28), f, True, T=Tr(0, -reach, head_z))
    b.add(_lathe([(0, 0), (r - .006, 0)], 28), grey, T=Tr(0, -reach, head_z))
    zh = vz + .45                                                            # sliding bracket + hand shower
    _cyl(b, (-.060, yb, zh), (.030, yb, zh), .014, f, 10)
    foot, tip = Vector((-.048, yb - .018, zh - .035)), Vector((-.048, yb - .062, zh + .125))
    b.add(_tube([foot, foot.lerp(tip, .6), tip], [.009, .011, .012], 10), f, True, closed=True)
    T = Tr(*tip) @ Rot('X', 112) @ Tr(0, 0, -.012)                           # head faces the room and 22 deg down
    b.add(_lathe([(0, 0), (.02, 0), (.048, .010), (.05, .016), (.05, .022)], 20), f, True, T=T)
    b.add(_lathe([(.05, .022), (0, .022)], 20), 'plastic_dark', T=T)
    hose = _bez(foot, (-.115, yb - .06, vz - .50), (-.075, yb - .005, vz - .42), (-.050, yb, vz - .020), 16)
    b.add(_tube(hose, .007, 6), grey, True, closed=True)
    if basket_z is not None:                                                 # wire basket clipped to the riser
        x0, x1, y0, y1, z0, z1 = -.13, .13, yb - .075, yb + .045, basket_z, basket_z + .06
        for z in (z0, z1):
            b.add(_tube([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], .002, 4, loop=True), f, True)
        for x in (x0, x0 / 3, x1 / 3, x1):
            for y in (y0, y1):
                b.add(_tube([(x, y, z0), (x, y, z1)], .0015, 4, cap=False), f, True)
        for i in range(7):
            y = y0 + (y1 - y0) * i / 6
            b.add(_tube([(x0, y, z0), (x1, y, z0)], .0015, 4, cap=False), f, True)


@_prop
def _spray(b, fall, dia):
    """Rain-head spray for `show when=1 fx='water'`: 36 thin streams from the origin plane (the head's underside)
    flaring 25 % on the way down to z = -fall, and a splash disc at the foot. Material 'water'. UVs as
    props.water_stream: V runs along the fall, 0 at the foot, +1 per 0.1 m up."""
    vs, fs, uv = [], [], []
    for q, n in ((.25, 6), (.55, 12), (.85, 18)):
        for i in range(n):
            a = tau * (i + .5 * (n == 12)) / n
            x, y = q * dia / 2 * cos(a), q * dia / 2 * sin(a)
            o = len(vs)
            for k in range(3):
                c, s = .0025 * cos(tau * k / 3), .0025 * sin(tau * k / 3)
                vs += [(x + c, y + s, 0), (1.25 * x + c, 1.25 * y + s, -fall)]
                uv += [(k / 3, fall / .1), (k / 3, 0)]
            fs += [(o + 2 * k, o + 2 * k + 1, o + (2 * k + 3) % 6, o + (2 * k + 2) % 6) for k in range(3)]
    b.add(G(vs, fs, vuv=uv), 'water')
    R, z, m = dia * .7, -fall + .0005, 16
    vs = [(0, 0, z)] + [(R * cos(tau * i / m), R * sin(tau * i / m), z) for i in range(m)]
    b.add(G(vs, [(0, 1 + i, 1 + (i + 1) % m) for i in range(m)],
            fuv=[[((i + .5) / m, 0), (i / m, -R / .1), ((i + 1) / m, -R / .1)] for i in range(m)]), 'water')


def shower_set(name, at, facing=None, rot_z=None, to_z=None, valve_z=1.10, head_z=2.12, reach=.35, head_dia=.25,
               basket_z=None, finish='chrome', label='Shower'):
    """The shower control every bathroom has -> [set, spray]: exposed thermostatic bar valve 0.30 long at valve_z,
    rigid riser, swan-neck arm reaching `reach` off the wall to a round rain head (underside at head_z), hand shower
    on a sliding bracket at valve_z + 0.45 with a hose, wire basket at basket_z (None = none).
    at = point on the shower wall on the riser's centre line at the ROOM FLOOR level (heights are above it);
    to_z = WORLD z the spray lands on (default: at.z + 0.04, a low-profile tray).
    Group '<name>': the whole set is the trigger, the spray under the rain head is show / fx water."""
    body = P.place(_shower(valve_z, head_z, reach, head_dia, basket_z, finish, name=name), at, facing=facing, rot_z=rot_z)
    top = _wp(body, (0, -reach, head_z))
    spray = P.place(_spray(round(top.z - (at[2] + .04 if to_z is None else to_z), 3), head_dia, name=name + '.spray'), top)
    IX.tag(body, 'trigger', g=name, label=label)
    IX.tag(spray, 'show', g=name, label=label, when=1, fx='water')
    return [body, spray]


# ----------------------------------------------------------------------------- glass
def _glass(b, x0, x1, z0, z1, y, t, mat):
    """Single-surface pane in the plane y (lib.materials: glass is one alpha-blended surface) with a pale green
    polished rim `t` deep, which is what makes frameless glass read."""
    b.add(G([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], [(0, 1, 2, 3)]), mat)
    h = t / 2
    c = [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]
    vs = [(x, y + s, z) for x, z in c for s in (-h, h)]
    b.add(G(vs, [(2 * i, 2 * i + 1, (2 * i + 3) % 8, (2 * i + 2) % 8) for i in range(4)]), P.two_sided('glass_green'))


@_prop
def glass_pane(b, w, h, t=.008, mat='glass_clear', channel=None, finish='chrome'):
    """Fixed frameless glass panel (shower return / end panel). Origin: bottom centre, pane in the local XZ plane.
    channel 'left' | 'right' | None: a slim wall profile down that edge (left = local -X) plus a floor clamp at the
    other end."""
    _glass(b, -w / 2, w / 2, 0, h, 0, t, mat)
    if channel:
        s = -1 if channel == 'left' else 1
        b.add(_box((s * w / 2 - .008, -.010, 0), (s * w / 2 + .008, .010, h), .002), finish, closed=True)
        b.add(_box((-s * w / 2 - .012, -.012, 0), (-s * w / 2 + .030, .012, .028), .003), finish, closed=True)


_RAIL = {'flat': (.020, .006), 'round': (.0125, .0125)}      # top rail: half height, half thickness
_GY = .018                                                   # fixed pane at +_GY, sliding pane at -_GY, rail between


@_prop
def _slider_fixed(b, width, height, door_w, side, rail, rail_z, finish):
    hz, hy = _RAIL[rail]
    fw = width - door_w + .03                                # 30 mm overlap with the door
    xa, xb = sorted((-side * width / 2, -side * (width / 2 - fw)))
    _glass(b, xa, xb, 0, height, _GY, .008, 'glass_clear')
    if rail == 'flat':
        b.add(_box((-width / 2, -hy, rail_z - hz), (width / 2, hy, rail_z + hz), .002), finish, closed=True)
    else:
        _cyl(b, (-width / 2, 0, rail_z), (width / 2, 0, rail_z), hz, finish)
    for k in (.2, .8):                                       # stand-offs through the fixed pane
        _disc_y(b, xa + (xb - xa) * k, _GY + .012, rail_z, .016, _GY + .012 - hy, finish)
    for x in (-width / 2, width / 2):                        # rail end sockets
        b.add(_box((x - .012 * (x > 0), -.014, rail_z - hz - .006), (x + .012 * (x < 0), .014, rail_z + hz + .006), .002),
              finish, closed=True)
    xe = -side * width / 2                                   # wall profile at the fixed pane's wall edge
    b.add(_box((xe - .008, _GY - .010, 0), (xe + .008, _GY + .010, height), .002), finish, closed=True)
    xg = -side * (width / 2 - fw)                            # floor guide where the panes pass
    b.add(_box((xg - .020, -_GY - .012, 0), (xg + .020, _GY + .012, .022), .003), finish, closed=True)


@_prop
def _slider_door(b, width, height, door_w, side, rail, rail_z, handle_z, finish):
    hz, hy = _RAIL[rail]
    xa, xb = sorted((side * width / 2, side * (width / 2 - door_w)))
    _glass(b, xa, xb, 0, height, -_GY, .008, 'glass_clear')
    zr = rail_z + hz + .016                                  # rollers ride on the rail, their caps show outside
    for k in (.22, .78):
        x = xa + (xb - xa) * k
        _disc_y(b, x, hy, zr, .016, 2 * hy, finish)
        _disc_y(b, x, -hy, zr, .006, _GY, finish, 8)
        _disc_y(b, x, -_GY - .004, zr, .021, .010, finish)
    xh, yh = side * (width / 2 - door_w + .07), -_GY - .004  # bar handle by the edge that meets the fixed pane
    b.add(_tube([(xh, yh, handle_z - .11), (xh, yh - .040, handle_z - .11), (xh, yh - .040, handle_z + .11),
                 (xh, yh, handle_z + .11)], .008, 8), finish, True, closed=True)
    _disc_y(b, xh, -_GY + .012, handle_z, .016, .008, finish)  # flush pull on the inner face


def shower_slider(name, at, width, facing=None, rot_z=None, height=1.95, door_w=None, door='right', travel=None,
                  rail='flat', rail_z=None, handle_z=1.05, finish='steel_brushed', label='Shower door'):
    """Frameless sliding shower front -> [fixed, door]: top rail across the whole `width`, a fixed pane on one side
    and a door pane hung on two rollers that slides in front of it.
    at = centre of the front at the level the glass stands on (tray top); `facing` points OUT of the shower (the
    side the visitor stands on); door 'right' | 'left' = which end the door closes, seen from outside.
    door_w default width / 2 + 15 mm; travel default door_w - 0.06; rail 'flat' (40 x 12 bar) | 'round' (dia 25) at
    rail_z (default height - 0.075); bar handle outside at handle_z by the door edge that meets the fixed pane.
    Local y: fixed pane +18 mm (shower side), rail 0, door -18 mm. Group '<name>': the door slides `travel`."""
    side = 1 if door == 'right' else -1
    door_w = round(width / 2 + .015, 4) if door_w is None else door_w
    rail_z = round(height - .075, 4) if rail_z is None else rail_z
    fixed = _slider_fixed(width, height, door_w, side, rail, rail_z, finish, name=name)
    leaf = _slider_door(width, height, door_w, side, rail, rail_z, handle_z, finish, name=name + '.door')
    _put([fixed, leaf], at, facing, rot_z)
    IX.tag(leaf, 'slide', g=name, label=label, d=_wv(fixed, (-side * (door_w - .06 if travel is None else travel), 0, 0)))
    return [fixed, leaf]


@_prop
def _hinged_door(b, w, h, side, mat, handle_z, finish):
    _glass(b, -w / 2, w / 2, 0, h, 0, .008, mat)
    for z in (.16 * h, .84 * h):                             # glass hinges on the hinge edge
        b.add(_box((side * w / 2 - .045 * (side > 0), -.012, z - .035), (side * w / 2 + .045 * (side < 0), .012, z + .035), .003),
              finish, closed=True)
    xh = -side * (w / 2 - .06)
    b.add(_tube([(xh, -.004, handle_z - .11), (xh, -.045, handle_z - .11), (xh, -.045, handle_z + .11),
                 (xh, -.004, handle_z + .11)], .008, 8), finish, True, closed=True)


def glass_door(name, at, w, h, facing=None, rot_z=None, hinge='left', deg=100, mat='glass_clear', handle_z=1.05,
               finish='chrome', label='Door'):
    """Frameless hinged glass door (sauna door with mat='glass_dark', a hinged shower door) -> [door]: pane, two
    glass hinges on the hinge edge, bar handle on the outside by the other edge.
    at = bottom centre of the pane; `facing` = the side it opens to; hinge 'left' | 'right' seen from that side.
    Group '<name>': hinge about the vertical hinge edge, `deg` outward (toward `facing`)."""
    side = -1 if hinge == 'left' else 1
    door = P.place(_hinged_door(w, h, side, mat, handle_z, finish, name=name), at, facing=facing, rot_z=rot_z)
    IX.tag(door, 'hinge', g=name, label=label, p=_wp(door, (side * w / 2, 0, 0)), deg=side * deg)
    return [door]


# ----------------------------------------------------------------------------- towel rail
def towel_rail(w=.5, h=1.5, mat='black_matt', name=None):
    """The straight ladder rail all three bathrooms have: props.radiator_towel_rail with the bars in four groups
    (bottom -> top q, q+1, q, q-1; 28 bars at 1.5 m, 32 at 1.6 m). Wall prop, origin: wall plane, bottom centre of the
    uprights. mat 'black_matt' (green bathroom, bathroom2) | 'anthracite' (en-suite)."""
    q = round((h - .38) / .16)
    return P.radiator_towel_rail(w, h, groups=(q, q + 1, q, q - 1), mat=mat, name=name)

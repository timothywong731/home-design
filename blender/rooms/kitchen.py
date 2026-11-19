"""Kitchen: navy shaker cabinet runs, quartz worktops + upstands, metro splashbacks, hob + angled hood,
oven tower, American fridge-freezer, sink with two taps, bar nook, plaque, bins, sockets and all lights.

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --only shell,kitchen --preview kitchen --res 540x960 --samples 64 --tag kitchen

Everything is set out in spec/rooms/kitchen.md coordinates (local mm / 1000, origin K0 = door-wall /
sink-wall corner) through four wall frames: u runs along the wall to the viewer's right, d = distance
off the wall into the room, z up. Each cabinet run is one static mesh (carcasses, plinth, cornice,
pelmet) with its shaker fronts and handles parented to it, so the plan footprint is one rectangle.
"""
import math
import os

import bpy
from mathutils import Matrix, Vector

from lib import lighting, materials as M, mouldings as mo, props as P, shell
from rooms.kitchen_outline import OUTLINE

ROOM = 'kitchen'
X0, Y0, SX, SY = 1.25, 5.31, 3.05, 3.42          # world position of K0 and the room size
NAVY, QUARTZ = 'navy_cabinet', 'marble_quartz'   # NAVY is replaced by the local navy() material in build()
ART = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'textures', 'art', 'kitchen')

BASE_TOP, WT_TOP = 0.88, 0.91                     # carcass top / worktop top
WALL_Z0, WALL_Z1, PELMET_Z = 1.455, 2.355, 1.42   # wall-unit carcass; pelmet underside
TALL_Z1 = 2.435
UPSTAND = 0.10                                    # quartz upstand height (seen at t=417 s and 761 s)
TILE_Z0 = WT_TOP + UPSTAND
# LED tape under the wall units, distance off the wall. At the back, not behind the pelmet: the frames show a
# clipped band on the top tile course that falls off fast down the wall (t=347, 413, 759 s) and a bright line on
# top of the 20 mm upstand (t=761 s), i.e. a source right against the tiles. At 50 mm the spill on the lower
# courses was twice as strong for the same top band.
LED_D = 0.025
# small ogee + top fillet, 45 high, projecting 25 (wall units and tall units)
CORNICE = [(0, 0), (.006, 0), (.008, .010), (.016, .020), (.022, .028), (.025, .031), (.025, .045), (0, .045)]
# nook cornice 100 high x 70: fascia 30, bead 8, cove 40, fillet 12, cap 10
NOOK_CORNICE = [(0, 0), (.012, 0), (.012, .030), (.016, .032), (.017, .034), (.016, .037), (.013, .038),
                (.014, .048), (.019, .058), (.028, .067), (.040, .074), (.055, .078), (.060, .078), (.060, .090),
                (.070, .090), (.070, .100), (0, .100)]

CAMERAS = [
    dict(name='entry', pos=(0.65, 8.26, 1.5), look=(4.3, 8.0, 1.4), fov_deg=100, ref='f_0755'),
    dict(name='nook', pos=(2.75, 7.01, 1.5), look=(2.6, 9.0, 1.4), fov_deg=100, ref='f_0766'),
    dict(name='hobwall', pos=(2.15, 7.91, 1.5), look=(4.3, 6.9, 1.45), fov_deg=100, ref='f_0758'),
    dict(name='hob', pos=(2.2, 7.46, 1.45), look=(4.3, 7.3, 1.35), fov_deg=100, ref='f_0348'),
    dict(name='corner', pos=(2.75, 7.61, 1.55), look=(4.3, 5.6, 1.35), fov_deg=100, ref='f_0760'),
    dict(name='sink', pos=(2.75, 7.45, 1.5), look=(2.6, 5.31, 1.45), fov_deg=100, ref='f_0378'),
    dict(name='fridge', pos=(3.55, 7.01, 1.5), look=(1.25, 7.01, 1.2), fov_deg=100, ref='f_0385'),
    dict(name='halldoor', pos=(3.05, 8.11, 1.5), look=(1.25, 8.2, 1.3), fov_deg=100, ref='f_0388'),
]


def variant(key, name, **inputs):
    """Copy of a library material with some Principled inputs replaced by constants (still glTF-safe:
    constants + the remaining image textures)."""
    m = bpy.data.materials.get(name)
    if m is None:
        m = M.mat(key).copy()
        m.name = name
        nt = m.node_tree
        bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
        for k, v in inputs.items():
            for l in list(bsdf.inputs[k].links):
                nt.links.remove(l)
            bsdf.inputs[k].default_value = v
        for n in list(nt.nodes):                              # drop the texture nodes that fed the replaced inputs
            if n.type == 'TEX_IMAGE' and not any(o.links for o in n.outputs):
                nt.nodes.remove(n)
    return m


def navy():
    """ponytail: local cabinet colour. Library navy_cabinet (#23252D) renders olive near-black under the
    3000 K view white balance (specular of the warm floor beats a 2 % albedo); the owner calls the units
    'dark blue navy blue' and the video reads them bluer than the wall. Same ash-grain normal map, bluer
    and lighter constant base. Drop this (NAVY = 'navy_cabinet') once the library colour is corrected."""
    return variant('navy_cabinet', 'kitchen_navy', **{'Base Color': M.hex_lin(NAVY_HEX)})


def satin():
    """Satin stainless for the small parts (hob tray, oven handles and trim, bins). Plain constant: the library
    streak maps (1 mm streaks) alias into a woven moire; only the hood and chimney carry them, see hood()."""
    return M.solid('kitchen_steel', '#B9B9B6', .33, 1)


def brass():
    """Pale satin brass of the T-bars and knobs (library brass_antique rendered dark bronze)."""
    return M.solid('kitchen_brass_satin', BRASS_HEX, .32, 1)


NAVY_HEX, BRASS_HEX, GLASS_ALPHA = '#2E323E', '#DDD2A6', .28


# ----------------------------------------------------------------------------- wall frames + run builder
class Wall:
    """Frame of one wall: local x = u along the wall (viewer's right), local -y = into the room."""

    def __init__(s, ox, oy, deg):
        s.rz = math.radians(deg)
        s.M = Matrix.Translation((ox, oy, 0)) @ Matrix.Rotation(s.rz, 4, 'Z')

    def p(s, u, d, z):
        return s.M @ Vector((u, -d, z))

    def put(s, ob, u, d, z, rz=0.0):
        ob.location, ob.rotation_euler = s.p(u, d, z), (0, 0, s.rz + rz)
        return ob


WN = Wall(X0, Y0 + SY, 0)            # nook wall:  u = spec x          (the nook itself is d < 0)
WS = Wall(X0 + SX, Y0, 180)          # sink wall:  u = 3.05 - spec x
WW = Wall(X0, Y0, 90)                # door wall:  u = spec y
WE = Wall(X0 + SX, Y0 + SY, -90)     # hob wall:   u = 3.42 - spec y


def T(x=0.0, y=0.0, z=0.0):
    return Matrix.Translation((x, y, z))


def RX(deg):
    return Matrix.Rotation(math.radians(deg), 4, 'X')


def circle(r, n=8):
    c = [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n)) for i in range(n)]
    return c + c[:1]


def rr(x0, x1, y0, y1, r, n=4):
    """Rounded rectangle outline, counter-clockwise, n chords per corner (closed sweep path)."""
    return [(cx + r * math.cos(a), cy + r * math.sin(a))
            for q, (cx, cy) in enumerate(((x1 - r, y1 - r), (x0 + r, y1 - r), (x0 + r, y0 + r), (x1 - r, y0 + r)))
            for a in ((q + k / n) * math.pi / 2 for k in range(n + 1))]


class Run:
    """One fitted piece: an MB mesh set out in a wall frame + prop children (fronts, handles)."""

    def __init__(s, ctx, wall, name):
        s.ctx, s.w, s.name, s.kids, s.n = ctx, wall, name, [], 0
        s.mb = mo.MB().at(wall.M)

    def box(s, u0, u1, d0, d1, z0, z1, mat=None, bev=0.001, grain=None):
        s.mb.box((u0, -d1, z0), (u1, -d0, z1), mat or NAVY, bev, grain)

    def at(s, u=0.0, d=0.0, z=0.0, rot=None):
        """Local frame for lathes / tubes: origin at (u, d, z), optional extra rotation. at() = wall frame."""
        m = s.w.M @ T(u, -d, z)
        s.mb.at(m @ rot if rot is not None else m)
        return s.mb

    def prop(s, ob, u, d, z, rz=0.0):
        s.kids.append(s.w.put(ob, u, d, z, rz))
        return ob

    def front(s, u0, u1, z0, z1, d, handle=None, at='top', slab=False, gap=0.003):
        """Shaker front whose back is d off the wall. handle: 'L' / 'R' vertical T-bar 55 mm from that
        edge, 'H' horizontal T-bar, 'KL' / 'KR' knob 50 mm from that edge; at = 'top' (base units:
        handle near the top) or 'bot' (wall units: near the bottom)."""
        w, h = u1 - u0 - gap, z1 - z0 - gap
        s.n += 1
        door = P.panel_door(w, h, stile=.085 if w >= .26 else .055, slab=slab, mat=NAVY, name=f'{s.name}.front.{s.n:02d}')
        s.prop(door, (u0 + u1) / 2, d, z0 + gap / 2)
        za, zb, f, br = z0 + gap / 2, z1 - gap / 2, d + 0.02, brass()
        if handle in ('L', 'R'):
            u = u0 + .055 if handle == 'L' else u1 - .055
            s.prop(P.handle_bar(finish=br, vertical=True, name=f'{s.name}.pull.{s.n:02d}'), u, f,
                   zb - .17 if at == 'top' else za + .17)
        elif handle == 'H':
            s.prop(P.handle_bar(finish=br, name=f'{s.name}.pull.{s.n:02d}'), (u0 + u1) / 2, f,
                   zb - .045 if at == 'top' else za + .06)
        elif handle in ('KL', 'KR'):                          # wall corner knobs: level with the top of the T-bars
            u = u0 + .05 if handle == 'KL' else u1 - .05
            s.prop(P.handle_knob(finish=br, name=f'{s.name}.knob.{s.n:02d}'), u, f, zb - .08 if at == 'top' else za + .255)
        return door

    def cornice(s, ur, ul, depth, z, ret_r=False, ret_l=False, mitre_r=False, mitre_l=False, profile=CORNICE):
        """Cornice along the front (right -> left so the profile projects into the room), with returns to
        the wall at exposed ends or a 45 deg cut where the next run carries on round an internal corner."""
        pts = ([(ur, 0, z)] if ret_r else []) + [(ur, -depth, z), (ul, -depth, z)] + ([(ul, 0, z)] if ret_l else [])
        s.mb.sweep(profile, pts, NAVY, ends=((-1, -1, 0) if mitre_r else None, (1, -1, 0) if mitre_l else None))

    def done(s, kind='fit', plan_sym=None, lm=None, uv=False):
        root = s.mb.finish(s.name)
        if uv:
            M.uv_box(root, rotate=(uv == 'rot'))
        for k in s.kids:
            k.parent = root                                   # root sits at the world origin: no parent inverse
        return s.ctx.add(root, ROOM, kind, plan_sym=plan_sym, lm=lm)


def wall_unit(r, u0, u1, depth=0.30, pelmet=True, side_l=False, side_r=False):
    """Closed wall-unit carcass 1455..2355 with the filler behind the cornice and the light pelmet."""
    r.box(u0, u1, 0, depth, WALL_Z0, WALL_Z1)
    r.box(u0, u1, 0, depth + .02, WALL_Z1, WALL_Z1 + .044, bev=0)
    if pelmet:
        pelmet_lip(r, u0, u1, depth)
        for on, a, b in ((side_l, u0, u0 + .018), (side_r, u1 - .018, u1)):
            if on:
                r.box(a, b, 0, depth, PELMET_Z, WALL_Z0 + .001, bev=.0005)


def pelmet_lip(r, u0, u1, depth=0.30):
    """Light pelmet under the door line. It runs 10 mm back under the carcass and 1 mm up into it, so no
    seam is left between the two for the LED strip to shine through (door bottoms are at WALL_Z0 + 1.5 mm)."""
    r.box(u0, u1, depth - .01, depth + .018, PELMET_Z, WALL_Z0 + .001, bev=.0005)


def led(r, u0, u1, depth=LED_D):
    """Visible LED tape under a wall unit (the Cycles emitter is lighting.strip, see lights()). Warm white:
    against the 3000 K view white balance a D65 white reads blue."""
    r.box(u0 + .02, u1 - .02, depth - .006, depth + .006, WALL_Z0 - .003, WALL_Z0 - .0005, P.emissive('#FFCF9A', 10.0), bev=0)


def metro():
    """ponytail: local tile colour. Library metro_grey (#C4C2BD) renders as light as the painted wall and the
    quartz upstand; the frames put the tile faces at 0.62-0.82 of the upstand (t=417, 761 s) with clearly
    lighter grout. Same maps, base colour swapped for art/kitchen/metro_grey_dark.jpg = the library image
    with the tile faces x 0.87 (#ABA9A4) and the grout untouched. Drop this once the library key is darkened."""
    m = bpy.data.materials.get('kitchen_metro_grey')
    if m is None:
        m = variant('metro_grey', 'kitchen_metro_grey')
        bsdf = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        bsdf.inputs['Base Color'].links[0].from_node.image = bpy.data.images.load(os.path.join(ART, 'metro_grey_dark.jpg'))
    return m


def tiles(ctx, name, x0, x1, y0, y1, z0, z1, origin):
    ob = shell.box(name, x0, x1, y0, y1, z0, z1, 'metro_grey')
    ob.data.materials[0] = metro()
    M.uv_box(ob, origin=origin)
    return ctx.add(ob, ROOM, 'fit')


# ----------------------------------------------------------------------------- hob wall (x = 3050)
def hob_wall(ctx):
    r = Run(ctx, WE, 'kitchen.base.hob')                      # H1..H5 + the corner, spec y 2508 -> 0
    r.box(.930, SY, 0, .54, 0, .15)                           # plinth, recessed 40
    r.box(.930, SY, 0, .58, .15, BASE_TOP)
    r.box(.912, .930, 0, .60, 0, BASE_TOP)                    # H1 end panel to the floor
    r.box(2.80, 2.84, .58, .60, .15, BASE_TOP, bev=0)         # corner filler between the two door planes
    z0, z1 = .15, .868
    r.front(.930, 1.530, z0, z1, .58, 'R')                    # H2 600 door
    r.front(1.530, 1.730, z0, z1, .58, 'R')                   # H3 200 pull-out
    r.front(1.730, 2.530, .690, z1, .58, 'H', slab=True)      # H4 pan drawers: 175 slab + 2 x 270 framed
    r.front(1.730, 2.530, .420, .690, .58, 'H')
    r.front(1.730, 2.530, z0, .420, .58, 'H')
    r.front(2.530, 2.800, z0, z1, .58, 'KL')                  # H5 corner door, knob
    r.done(plan_sym='base_unit')

    w = Run(ctx, WE, 'kitchen.worktop.hob')                   # hob-wall leg of the L, joint at the corner
    w.box(.882, SY, 0, .62, BASE_TOP, WT_TOP, QUARTZ, bev=.002)
    w.box(.882, SY, 0, .02, WT_TOP, TILE_Z0, QUARTZ, bev=.002)
    w.done(plan_sym='worktop', uv=True)

    r = Run(ctx, WE, 'kitchen.wall.w1')                       # W1 600, both sides exposed
    wall_unit(r, .912, 1.512, side_l=True, side_r=True)
    r.front(.912, 1.512, WALL_Z0, WALL_Z1, .30, 'R', 'bot')
    r.cornice(1.512, .912, .32, WALL_Z1, ret_r=True, ret_l=True)
    led(r, .912, 1.512)
    r.done(plan_sym='wall_unit')

    r = Run(ctx, WE, 'kitchen.wall.w2')                       # W2 500 pair of doors + the corner
    wall_unit(r, 2.59, SY, side_l=True)
    r.front(2.59, 2.84, WALL_Z0, WALL_Z1, .30, 'R', 'bot')
    r.front(2.84, 3.09, WALL_Z0, WALL_Z1, .30, 'R', 'bot')
    r.cornice(3.10, 2.59, .32, WALL_Z1, ret_l=True, mitre_r=True)
    led(r, 2.59, 3.10)
    r.done(plan_sym='wall_unit')

    y = lambda u: Y0 + SY - u                                 # splashback above the upstand, 3 mm proud
    org = (X0 + SX, Y0, TILE_Z0)
    tiles(ctx, 'kitchen.splash.hob.a', X0 + SX - .003, X0 + SX, y(1.512), y(.912), TILE_Z0, WALL_Z0, org)
    tiles(ctx, 'kitchen.splash.hob.b', X0 + SX - .003, X0 + SX, y(2.59), y(1.512), TILE_Z0, TILE_Z0 + 5 * .103, org)   # 5 courses, to just under the hood
    tiles(ctx, 'kitchen.splash.hob.c', X0 + SX - .003, X0 + SX, Y0, y(2.59), TILE_Z0, WALL_Z0, org)

    for u, z in ((2.86, 1.13),):                              # double socket under W2
        ctx.add(WE.put(P.socket(2, name='kitchen.socket.hob'), u, .003, z), ROOM, 'fit')


def hob(ctx):
    """5-burner gas hob 750 x 520 centred on spec y 1290, front edge 55 back from the worktop edge."""
    r = Run(ctx, WE, 'kitchen.hob')
    SATIN = satin()
    uc, d0, d1, z = 2.13, .045, .565, WT_TOP
    r.box(uc - .375, uc + .375, d0, d1, z, z + .004, SATIN, bev=.0015, grain=0)
    for a, b, c, e in ((uc - .375, uc + .375, d0, d0 + .008), (uc - .375, uc + .375, d1 - .008, d1),
                       (uc - .375, uc - .367, d0, d1), (uc + .367, uc + .375, d0, d1)):       # 5 mm raised rim
        r.box(a, b, c, e, z + .003, z + .008, SATIN, bev=.001, grain=0)
    burners = [(uc - .25, .27, .062), (uc, .17, .042), (uc, .37, .030), (uc + .25, .17, .042), (uc + .25, .38, .036)]
    for bu, bd, br in burners:                                # (wok burner on the +Y third)
        mb = r.at(bu, bd, z + .004)
        mb.lathe([(0, 0), (br * 1.25, 0), (br * 1.25, .006), (br * 1.05, .012), (0, .012)], 'nickel_brushed', 20)
        mb.lathe([(0, .012), (br, .012), (br, .019), (br * .9, .022), (0, .022)], 'cast_iron', 20)
        if br > .05:                                          # triple ring
            mb.lathe([(0, .022), (br * .45, .022), (br * .45, .028), (0, .028)], 'cast_iron', 16)
    r.at()
    zt, zb = z + .046, z + .034                               # pan supports: three cast-iron grids
    for i, ga in enumerate((uc - .365, uc - .118, uc + .129)):
        gb, f0, f1 = ga + .236, d0 + .02, d1 - .075
        for a, b, c, e in ((ga, gb, f0, f0 + .01), (ga, gb, f1 - .01, f1), (ga, ga + .01, f0, f1), (gb - .01, gb, f0, f1)):
            r.box(a, b, c, e, zb, zt, 'cast_iron', bev=.002)
        for a, e in ((ga + .004, f0 + .004), (gb - .012, f0 + .004), (ga + .004, f1 - .012), (gb - .012, f1 - .012)):
            r.box(a, a + .008, e, e + .008, z + .004, zb, 'cast_iron', bev=0)                 # feet
        for bu, bd, br in burners:
            if ga < bu < gb:                                  # four fingers toward each burner
                k = br * .55
                for a, b, c, e in ((ga, bu - k, bd - .004, bd + .004), (bu + k, gb, bd - .004, bd + .004),
                                   (bu - .004, bu + .004, max(f0, bd - .11), bd - k),
                                   (bu - .004, bu + .004, bd + k, min(f1, bd + .11))):
                    r.box(a, b, c, e, zb + .002, zt + .001, 'cast_iron', bev=.0015)
    for i in range(5):                                        # control knobs along the front edge
        mb = r.at(uc - .14 + i * .045, d1 - .04, z + .004)
        mb.lathe([(0, 0), (.019, 0), (.019, .018), (.016, .024), (0, .024)], 'nickel_brushed', 16)
    r.at()
    r.done(plan_sym='hob', lm='dynamic')


def hood(ctx):
    """900 angled chimney hood: face leans out ~25 deg, black base with two spots, telescopic chimney."""
    r = Run(ctx, WE, 'kitchen.hood')
    SATIN = 'steel_brushed'                                   # see the uv_box at the end
    u0, u1, zb, zt, db, dt = 1.68, 2.58, 1.572, 2.13, .155, .42
    r.mb.prism([(u0, 0, zb), (u0, -db, zb), (u0, -dt, zt), (u0, 0, zt)], (u1 - u0, 0, 0), SATIN, grain=2)
    r.box(u0 + .008, u1 - .008, .01, db - .008, 1.54, zb + .001, 'black_matt', bev=.002)
    ang = math.degrees(math.atan2(dt - db, zt - zb))
    L = math.hypot(dt - db, zt - zb)
    mb = r.at((u0 + u1) / 2, db, zb, RX(ang))                 # frame on the sloping face: x across, z up the slope
    mb.box((-.36, -.0015, .72 * L), (.36, .001, .72 * L + .022), 'black_gloss', bev=.0005)       # extraction slot
    mb.box((-.449, -.0008, .72 * L + .027), (.449, .001, .72 * L + .030), 'chrome')              # seam
    mb.box((-.095, -.0012, .86 * L), (.095, .001, .86 * L + .022), 'black_gloss', bev=.0005)     # touch strip
    r.at()
    lens = P.emissive('#FFE9C4', 8.0)
    for u in (u0 + .15, u1 - .15):                            # two spot lenses under the base
        r.mb.face([(u + .0275 * math.cos(a), -.08 + .0275 * math.sin(a), 1.539)
                   for a in (2 * math.pi * k / 16 for k in range(16))], lens, hint=(0, 0, -1))
    uc = (u0 + u1) / 2
    # chimney 340 wide x 270 deep (f_0348: 0.55 of the 600 wall unit), two telescopic sections
    r.box(uc - .17, uc + .17, 0, .27, zt - .001, 2.50, SATIN, bev=.001, grain=2)
    r.box(uc - .165, uc + .165, 0, .265, 2.50, ctx.ceil_z(ROOM) - .001, SATIN, bev=.001, grain=2)
    for sg in (-1, 1):                                        # vent grille slots near the top, both sides
        for k in range(3):
            r.box(uc + sg * .165 - .001, uc + sg * .165 + .001, .06, .21, 2.80 + k * .014, 2.807 + k * .014, 'black_matt', bev=0)
    # Library streak maps turned vertical and stretched x16: the roughness streaks become soft 10-20 mm bands,
    # which is how the real hood and chimney read (broad vertical light / dark bands, f_0366-f_0367). At the
    # native 1 mm they alias into a woven moire, at x4 they look like scratches.
    M.uv_box(r.done(lm='dynamic'), scale=16, rotate=True)


# ----------------------------------------------------------------------------- sink wall (y = 0)
SINK = (1.23, 1.97, .11, .51)                                 # cut-out u0 u1 d0 d1 (spec x 1820 -> 1080)


def sink_wall(ctx):
    r = Run(ctx, WS, 'kitchen.base.sink')                     # S1..S4, spec x 2470 -> 0
    r.box(.54, SX, 0, .54, 0, .15)                            # plinth, closing the internal corner
    r.box(.58, 1.20, 0, .58, .15, BASE_TOP)
    r.box(1.20, 2.00, 0, .58, .15, .66)                       # sink base: open under the bowls
    r.box(1.20, 2.00, 0, .10, .66, BASE_TOP, bev=0)
    r.box(1.20, 2.00, .52, .58, .66, BASE_TOP, bev=0)
    r.box(2.00, SX, 0, .58, .15, BASE_TOP)
    z0, z1 = .15, .868
    r.front(.60, 1.20, z0, z1, .58, 'H')                      # S1 integrated dishwasher
    r.front(1.20, 1.60, z0, z1, .58, 'R')                     # S2 sink base pair
    r.front(1.60, 2.00, z0, z1, .58, 'L')
    r.front(2.00, 2.45, z0, z1, .58, 'L')                     # S3 450
    r.done(plan_sym='base_unit')

    w = Run(ctx, WS, 'kitchen.worktop.sink')                  # sink-wall leg, butt joint at spec x 2430
    a, b, c, e = SINK
    for u0, u1, d0, d1 in ((.62, a, 0, .62), (b, SX, 0, .62), (a, b, 0, c), (a, b, e, .62)):
        w.box(u0, u1, d0, d1, BASE_TOP, WT_TOP, QUARTZ, bev=0)   # flush seams round the cut-out
    w.box(.02, SX, 0, .02, WT_TOP, TILE_Z0, QUARTZ, bev=.002)    # upstands: sink wall + door-wall return
    w.box(SX - .02, SX, .02, .60, WT_TOP, TILE_Z0, QUARTZ, bev=.002)
    w.done(plan_sym='worktop', uv=True)

    r = Run(ctx, WS, 'kitchen.wall.sink')                     # T1..T5, spec x 2730 -> 0
    wall_unit(r, .32, 1.225)                                  # T1 + T2
    wall_unit(r, 2.425, SX)                                   # T5 + blind corner
    pelmet_lip(r, 1.225, 2.425)
    r.box(1.225, 2.425, 0, .32, WALL_Z1, WALL_Z1 + .044, bev=0)
    r.front(.32, .625, WALL_Z0, WALL_Z1, .30, 'KL', 'bot')    # T1 corner knob door
    r.front(.625, 1.225, WALL_Z0, WALL_Z1, .30, 'R', 'bot')   # T2 600
    r.front(2.425, 2.725, WALL_Z0, WALL_Z1, .30, 'R', 'bot')  # T5 300 (handle on the corner side, f_0378 / f_0396)
    # T3 plate rack 900: flap door over an open rack
    u0, u1, zr = 1.225, 2.125, 1.975
    r.box(u0, u1, 0, .30, zr, WALL_Z1)
    r.front(u0, u1, zr, WALL_Z1, .30, 'H', 'bot')
    r.box(u0, u0 + .018, 0, .30, WALL_Z0, zr)
    r.box(u1 - .018, u1, 0, .30, WALL_Z0, zr)
    r.box(u0, u1, 0, .006, WALL_Z0, zr, bev=0)
    r.box(u0, u1, .26, .30, WALL_Z0, WALL_Z0 + .04)           # front rail 40
    r.box(u0, u1, 0, .04, WALL_Z0, WALL_Z0 + .04)
    for d in (.10, .22):                                      # two rails the plates stand on
        r.mb.tube([(u0, -d, 1.48), (u1, -d, 1.48)], .006, NAVY, 6)
    uc = (u0 + u1) / 2
    for i in range(13):                                       # 13 dowels, front and rear rows
        for d in (.275, .05):
            u = uc + (i - 6) * .065
            r.mb.tube([(u, -d, WALL_Z0 + .03), (u, -d, zr + .002)], .005, NAVY, 6)
    # T4 wine rack 300: 2 x 7 cells (c_377_wine); 126 pitch keeps the 900 unit height
    u0, u1 = 2.125, 2.425
    r.box(u0, u0 + .018, 0, .30, WALL_Z0, WALL_Z1)
    r.box(u1 - .018, u1, 0, .30, WALL_Z0, WALL_Z1)
    r.box(u0, u1, 0, .006, WALL_Z0, WALL_Z1, bev=0)
    r.box((u0 + u1) / 2 - .009, (u0 + u1) / 2 + .009, .006, .30, WALL_Z0, WALL_Z1)
    rows = 7
    pitch = (WALL_Z1 - WALL_Z0 - .018) / rows
    for k in range(rows + 1):
        r.box(u0 + .018, u1 - .018, .006, .30, WALL_Z0 + k * pitch, WALL_Z0 + k * pitch + .018)
    r.cornice(2.73, .32, .32, WALL_Z1, mitre_r=True, mitre_l=True)
    led(r, .32, 2.73)
    r.done(plan_sym='wall_unit')

    # contents: plates on edge, bottles neck-out (movable -> separate dynamic objects)
    lean = Matrix.Rotation(math.radians(-9), 4, 'Y') @ Matrix.Rotation(math.radians(-90), 4, 'Z') @ RX(90)
    for i in list(range(10)) + [11]:
        dia = .30 if i == 11 else .27
        pl = P.plate(dia, name=f'kitchen.plate.{i:02d}')
        u = uc + (i - 5.5) * .065
        pl.location = WS.p(u - .012, .16, 1.486 + math.sqrt((dia / 2) ** 2 - .06 ** 2))
        pl.rotation_euler = lean.to_euler()
        ctx.add(pl, ROOM, 'decor')
    foils = [M.solid('kitchen_foil_green', '#2F5A3A', .35, 1), M.solid('kitchen_foil_silver', '#B9BBBE', .3, 1), 'cork']
    first = []
    # 10 bottles as filmed: col 0 = the plate-rack side, row 0 = bottom
    for n, (col, row) in enumerate(((0, 6), (0, 5), (1, 5), (0, 4), (1, 4), (0, 3), (1, 3), (0, 2), (1, 2), (1, 1))):
        if n < 3:                                             # three cap colours = three meshes, then instances
            mb = mo.MB()
            mb.lathe([(0, 0), (.037, 0), (.037, .17), (.030, .20), (.015, .225), (.014, .24)], 'glass_dark', 14)
            mb.lathe([(.0145, .22), (.0155, .225), (.0155, .28), (0, .28)], foils[n], 14)
            b = mb.finish(f'kitchen.bottle.{n}')
            first.append(b)
        else:
            b = bpy.data.objects.new(f'kitchen.bottle.{n}', first[n % 3].data)
        u = u0 + .018 + (col + .5) * (u1 - u0 - .036) / 2 + (.006 if col else -.006)
        b.location = WS.p(u, .012, WALL_Z0 + row * pitch + .018 + .037)
        b.rotation_euler = (WS.M.to_3x3() @ RX(90).to_3x3()).to_euler()      # axis -> into the room
        ctx.add(b, ROOM, 'decor')

    org = (X0 + SX, Y0, TILE_Z0)
    tiles(ctx, 'kitchen.splash.sink', X0, X0 + SX, Y0, Y0 + .003, TILE_Z0, WALL_Z0, org)
    tiles(ctx, 'kitchen.splash.return', X0, X0 + .003, Y0, Y0 + .60, TILE_Z0, WALL_Z0, org)
    ctx.add(WS.put(P.socket(2, name='kitchen.socket.sink'), .80, .003, 1.13), ROOM, 'fit')
    ctx.add(WS.put(P.switch_plate(1, name='kitchen.spur'), .15, .003, 1.13), ROOM, 'fit')


def sink(ctx):
    """Undermounted double bowl + spring-neck mixer + filter tap ("two taps")."""
    r = Run(ctx, WS, 'kitchen.sink')
    a, b, c, e = SINK
    zr, zf, nk = BASE_TOP, .68, 'nickel_brushed'
    # plain satin (the streak map crossed itself on the bowl faces); rough + mid grey so the bowls do not mirror
    # the white ceiling and merge with the quartz when seen from above
    sm = M.solid('kitchen_sink_steel', '#8C8D8A', .45, 1)
    m = a + .45 * (b - a)                                     # the +X (disposer) bowl is the narrower one (t=413 s)
    # Each bowl is one sweep round its rounded rim (R18, 3 mm inside the cut-out = the undermount reveal):
    # bottom strip, R12 cove, wall, then a flat flange running 12.5 out under the quartz / to the divider centre.
    R, rc, zl = .018, .012, zr - .001
    H = zl - zf
    prof = [(rc + .004, -H)] + [(rc - rc * math.sin(t), rc - rc * math.cos(t) - H)
                                for t in (0, math.pi / 6, math.pi / 3, math.pi / 2)] + [(0, 0), (-.0125, 0)]
    y0, y1, k, zb = -(e - .003), -(c + .003), rc + .001, zf - .0005
    for u0, u1, waste in ((a + .003, m - .0125, 'black_matt'), (m + .0125, b - .003, 'chrome')):
        r.mb.sweep(prof, [(x, y, zl) for x, y in rr(u0, u1, y0, y1, R)], sm, closed=True)
        r.mb.face([(u0 + k, y0 + k, zb), (u1 - k, y0 + k, zb), (u1 - k, y1 - k, zb), (u0 + k, y1 - k, zb)], sm, hint=(0, 0, 1))
        r.at((u0 + u1) / 2, (c + e) / 2, zf).lathe([(0, .001), (.028, .001), (.045, .003), (.045, 0)][::-1], waste, 16)
        r.at()

    # (a) chrome spring-neck pull-down mixer at spec x 1450, lever on the -X side (full-res still t=413 s):
    # body 200, coil-wrapped riser to 320, semicircular spring arch R 115 (top 435 above the worktop, 75 under
    # the pelmet), spray head hanging on the far side to 150, flat cradle arm from the body top to the head.
    ch, up = 'chrome', (1, 0, 0)
    BODY, RISE, R, HEAD = .20, .32, .115, .15
    mb = r.at(1.60, .06, WT_TOP)
    mb.lathe([(0, 0), (.027, 0), (.027, .004), (.022, .007), (.022, BODY), (.017, BODY + .006), (0, BODY + .006)], ch, 16)
    mb.tube([(.018, 0, .075), (.05, 0, .075)], .013, ch, 10)
    mb.sweep(circle(.004, 6), [(.046, 0, .08), (.052, -.006, .11), (.062, -.012, .145)], ch, up=(0, 1, 0))
    mb = r.at(1.60, .06, WT_TOP, Matrix.Rotation(math.radians(-40), 4, 'Z'))   # arch plane: into the room, swung 40 deg to +X
    line = [(0, 0, BODY), (0, 0, RISE)] + [(0, -R + R * math.cos(t), RISE + R * math.sin(t))
                                          for t in (math.pi * k / 14 for k in range(1, 15))] + [(0, -2 * R, HEAD + .12)]
    mb.sweep(circle(.008, 8), line, ch, up=up)                # hose / riser
    mb.at(mb.M @ T(0, -2 * R, HEAD)).lathe([(0, 0), (.019, 0), (.019, .02), (.014, .03), (.014, .12), (0, .12)], ch, 12)
    mb = r.at(1.60, .06, WT_TOP, Matrix.Rotation(math.radians(-40), 4, 'Z'))
    mb.box((-.011, -2 * R - .016, BODY - .002), (.011, 0, BODY + .003), ch, bev=.001)          # flat cradle arm
    cl = []                                                   # coil: one ring every 9 mm, ending 30 mm down the far side
    for (p, q) in zip(line, line[1:]):
        p, q = Vector(p), Vector(q)
        n = max(1, round((q - p).length / .009))
        cl += [(p.lerp(q, k / n), (q - p).normalized()) for k in range(n)]
    for p, t in cl[1:len(cl) - round((RISE - HEAD - .12 - .03) / .009)]:
        e2 = t.cross(Vector(up))
        ring = [p + .0135 * (math.cos(a) * Vector(up) + math.sin(a) * e2) for a in (2 * math.pi * k / 8 for k in range(8))]
        mb.sweep(circle(.0022, 4), ring, ch, closed=True, up=t)
    # (b) brushed-nickel filter tap at spec x 1180
    mb = r.at(1.87, .06, WT_TOP)
    mb.lathe([(0, 0), (.021, 0), (.021, .05), (.017, .056), (0, .056)], nk, 14)
    mb.sweep(circle(.0095, 8), [(0, 0, .05), (0, 0, .225), (0, -.022, .25), (0, -.105, .25), (0, -.122, .232), (0, -.122, .19)],
             nk, up=up)
    r.at()
    r.done(plan_sym='sink', lm='dynamic')


# ----------------------------------------------------------------------------- door wall (x = 0)
def door_wall(ctx):
    r = Run(ctx, WW, 'kitchen.wall.corner')                   # knob-door cupboard spec y 320 -> 600, faces +X
    wall_unit(r, .32, .60)
    r.front(.32, .60, WALL_Z0, WALL_Z1, .30, 'KL', 'bot')
    r.cornice(.60, .32, .32, WALL_Z1, mitre_l=True)
    led(r, .32, .60)
    r.done(plan_sym='wall_unit')

    r = Run(ctx, WW, 'kitchen.tower')                         # oven tower spec y 600 -> 1200
    SATIN = satin()
    a, b, gl = .60, 1.20, 'black_gloss'
    ua, ub, uc = a + .0025, b - .0025, (a + b) / 2
    r.box(a, b, 0, .56, 0, .15)
    r.box(a, b, 0, .60, .15, TALL_Z1)
    r.box(a, b, 0, .62, TALL_Z1, TALL_Z1 + .044, bev=0)

    def bar(z):                                               # flat steel bar handle on two posts
        r.box(ua + .03, ub - .03, .650, .664, z, z + .028, SATIN, bev=.003, grain=0)
        for u in (ua + .075, ub - .075):
            r.box(u - .012, u + .012, .62, .652, z + .006, z + .022, SATIN, bev=.002)

    r.box(ua + .001, ub - .001, .60, .618, .153, .547, gl, bev=.001)   # lower drop-front appliance, 1 mm inside its steel surround
    for u0, u1, z0, z1 in ((ua, ub, .152, .164), (ua, ub, .536, .548), (ua, ua + .012, .152, .548), (ub - .012, ub, .152, .548)):
        r.box(u0, u1, .60, .621, z0, z1, SATIN, bev=.001)
    bar(.49)
    r.box(ua, ub, .60, .622, .553, 1.050, gl, bev=.002)       # single oven: door, handle, control band
    bar(1.005)
    r.box(ua, ub, .60, .618, 1.053, 1.143, gl, bev=.001)
    r.mb.face([(uc + .02 * math.cos(t), -.6195, 1.098 + .02 * math.sin(t)) for t in (2 * math.pi * k / 16 for k in range(16))],
              P.emissive('#E0506A', 1.5), hint=(0, -1, 0))    # round colour display (no glyphs)
    r.box(ua, ub, .60, .622, 1.148, 1.500, gl, bev=.002)      # compact oven, control band at the top
    bar(1.455)
    r.box(ua, ub, .60, .618, 1.503, 1.597, gl, bev=.001)
    r.mb.face([(uc - .15, -.6195, 1.542), (uc - .03, -.6195, 1.542), (uc - .03, -.6195, 1.556), (uc - .15, -.6195, 1.556)],
              P.emissive('#CFE4FF', 1.5), hint=(0, -1, 0))    # display glow bar (digits deliberately not drawn)
    r.box(ua, ub, .60, .612, 1.60, 1.64, 'oak_light', bev=0, grain=0)      # the bare-oak filler strip
    r.front(a, b, 1.64, TALL_Z1, .60, 'R', 'bot')
    r.cornice(b, a, .62, TALL_Z1, ret_l=True)
    r.done(plan_sym='oven_tower')

    r = Run(ctx, WW, 'kitchen.fridge_housing')                # spec y 1200 -> 2230
    a, b = 1.20, 2.23
    r.box(a, a + .018, 0, .60, 0, TALL_Z1)
    r.box(b - .018, b, 0, .60, 0, TALL_Z1)
    r.box(a + .018, b - .018, 0, .58, 2.04, TALL_Z1)
    r.box(a, b, 0, .62, TALL_Z1, TALL_Z1 + .044, bev=0)
    r.box(a + .018, b - .018, 0, .006, 0, 2.04, bev=0)        # dark back behind the fridge and in the niche
    r.front(a + .018, b - .018, 2.04, TALL_Z1, .58, 'H', 'bot')
    r.cornice(b, a, .62, TALL_Z1, ret_r=True)
    r.done(plan_sym='tall_unit')

    r = Run(ctx, WW, 'kitchen.fridge')                        # American side-by-side 912 x 1780 x 716, no magnets
    g = M.solid('kitchen_graphite', '#2B2C2E', .55, .3)
    u0, u1 = 1.715 - .456, 1.715 + .456
    sp = u0 + .42 * .912                                      # door split: ice / water door is 0.42 of the width
    r.box(u0, u1, .02, .64, .04, 1.78, g, bev=.002)
    r.box(u0 + .02, u1 - .02, .06, .62, 0, .04, 'black_matt', bev=0)
    r.box(sp - .005, sp + .005, .64, .70, .04, 1.78, 'black_matt', bev=0)          # recessed grips at the meeting edges
    r.box(sp + .005, u1, .645, .716, .04, 1.78, g, bev=.004, grain=2)
    n0, n1, m0, m1 = u0 + .046, u0 + .336, .815, 1.205        # dispenser niche 290 x 390, centre z 1010
    for a, b, z0, z1 in ((u0, n0, .04, 1.78), (n1, sp - .005, .04, 1.78), (n0, n1, .04, m0), (n0, n1, m1, 1.78)):
        r.box(a, b, .645, .716, z0, z1, g, bev=0, grain=2)
    r.box(n0, n1, .645, .656, m0, m1, 'black_gloss', bev=0)
    r.box(n0 + .02, n1 - .02, .656, .705, m0, m0 + .012, 'black_matt', bev=.002)   # drip tray
    r.box(n0 + .10, n1 - .10, .656, .69, m1 - .05, m1, 'black_matt', bev=.004)     # spout block
    r.box(n0, n1, .716, .7172, m1 + .012, m1 + .062, 'black_gloss', bev=0)         # control strip
    r.done(plan_sym='fridge')

    ctx.add(WW.put(P.switch_plate(1, name='kitchen.switch'), 2.34, 0, 1.25), ROOM, 'fit')

    r = Run(ctx, WW, 'kitchen.bin.steel')                     # pedal bin between the housing and the hall door
    r.box(2.255, 2.485, .035, .405, 0, .03, 'black_matt', bev=0)
    r.box(2.25, 2.49, .03, .41, .03, .60, satin(), bev=.012, grain=2)
    r.box(2.248, 2.492, .028, .412, .597, .606, 'black_matt', bev=.001)
    r.box(2.245, 2.495, .025, .415, .606, .65, satin(), bev=.012, grain=1)
    r.box(2.30, 2.44, .40, .46, .012, .028, 'black_matt', bev=.004)
    r.done(kind='furn')['toggle'] = 'bins'


# ----------------------------------------------------------------------------- bar nook (recess d < 0)
def nook(ctx):
    a, b, back = .12, 1.37, -.52
    r = Run(ctx, WN, 'kitchen.nook.base')                     # 350 + 350 + 550 (t=765 s), faces 10 behind the wall face
    r.box(a, b, back, -.07, 0, .15)
    r.box(a, b, back, -.03, .15, BASE_TOP)
    r.front(a, .47, .15, .868, -.03, 'R')
    r.front(.47, .82, .15, .868, -.03, 'R')
    r.front(.82, b, .15, .868, -.03, 'L')
    r.done(plan_sym='base_unit')

    w = Run(ctx, WN, 'kitchen.worktop.nook')
    w.box(a, b, back, -.015, BASE_TOP, WT_TOP, QUARTZ, bev=.002)
    w.box(a, b, back, back + .02, WT_TOP, TILE_Z0, QUARTZ, bev=.002)
    w.box(a, a + .02, back + .02, -.015, WT_TOP, TILE_Z0, QUARTZ, bev=.002)
    w.box(b - .02, b, back + .02, -.015, WT_TOP, TILE_Z0, QUARTZ, bev=.002)
    w.done(plan_sym='worktop', uv=True)

    xa, xb, ya, yb = X0 + a, X0 + b, Y0 + SY, Y0 + SY - back  # tiles above the upstand to the lower shelf
    org = (xa, yb, TILE_Z0)
    tiles(ctx, 'kitchen.splash.nook', xa, xb, yb - .003, yb, TILE_Z0, 1.464, org)
    tiles(ctx, 'kitchen.splash.nook.l', xa, xa + .003, ya + .002, yb, TILE_Z0, 1.464, org)
    tiles(ctx, 'kitchen.splash.nook.r', xb - .003, xb, ya + .002, yb, TILE_Z0, 1.464, org)
    sof = shell.box('kitchen.nook.soffit', xa, xb, ya, yb, 2.018, 2.029, 'navy_cabinet')      # black soffit lining
    sof.data.materials[0] = NAVY
    ctx.add(sof, ROOM, 'fit')

    r = Run(ctx, WN, 'kitchen.nook.shelves')                  # two glass shelves, clamp brackets, back mirror
    for zt in (1.474, 1.652):
        r.box(a + .002, b - .002, back + .002, -.22, zt - .01, zt, 'glass_clear', bev=.001)
        r.box(a + .002, b - .002, -.221, -.219, zt - .01, zt, M.solid('kitchen_glass_edge', '#3F6B55', .05),
              bev=0)                                          # dark green polished front edge, 1 mm proud (t=765 s)
        for u in (a + .18, (a + b) / 2, b - .18):
            r.box(u - .012, u + .012, back + .002, back + .026, zt - .016, zt + .006, 'chrome', bev=.002)
        for d in (-.47, -.27):
            r.box(a, a + .022, d - .012, d + .012, zt - .016, zt + .006, 'chrome', bev=.002)
            r.box(b - .022, b, d - .012, d + .012, zt - .016, zt + .006, 'chrome', bev=.002)
    r.box(a, b, back, back + .004, 1.474, 2.018, 'mirror', bev=0)
    r.done(plan_sym='shelf')

    r = Run(ctx, WN, 'kitchen.nook.cornice')                  # black cornice over the opening, returned to the wall
    r.mb.sweep(NOOK_CORNICE, [(b + .018, .05, 2.03), (b + .018, 0, 2.03), (a - .018, 0, 2.03), (a - .018, .05, 2.03)], NAVY)
    r.done()

    r = Run(ctx, WN, 'kitchen.nook.rack')                     # brass stemware rack: 9 slots, two rows deep
    zs = 2.018
    zw = zs - .055
    slots = [.395 + i * .105 for i in range(9)]
    for uc in slots:
        for sg in (-1, 1):                                    # pair of wires per slot, flared at the front
            r.mb.tube([(uc + sg * .042, .035, zw), (uc + sg * .016, .08, zw), (uc + sg * .016, .37, zw)], .0025, 'brass', 6)
    for y in (.085, .225, .365):
        r.mb.tube([(.33, y, zw + .005), (1.30, y, zw + .005)], .0025, 'brass', 6)
    for y in (.085, .365):
        for u in (.345, .66, .975, 1.285):
            r.mb.tube([(u, y, zw + .005), (u, y, zs)], .0025, 'brass', 6)
    r.done(lm='dynamic')
    # glassware: library glass_clear (alpha 0.10) left the glasses as dark ghosts; the bar's sparkle needs more body
    gl = variant('glass_clear', 'kitchen_glassware', Alpha=GLASS_ALPHA, Roughness=.02)
    hang = [(i, .15) for i in range(9)] + [(i, .29) for i in (0, 1, 3, 4, 6, 7, 8)]
    for n, (i, y) in enumerate(hang):                         # 14 wine + 2 wider "martini" glasses, bowl down
        g = P.wine_glass(.18, .105, mat=gl, name=f'kitchen.nook.glass.{n:02d}') if n in (9, 15) else \
            P.wine_glass(.2, .085, mat=gl, name=f'kitchen.nook.glass.{n:02d}')
        g.location, g.rotation_euler = WN.p(slots[i], -y, zw + .0055), (math.pi, 0, 0)
        ctx.add(g, ROOM, 'decor')

    def stand(ob, u, y, z, rz=0.0):
        ob.location, ob.rotation_euler = WN.p(u, -y, z), (0, 0, rz)
        return ctx.add(ob, ROOM, 'decor')

    def mug(name, mat):
        mb = mo.MB()
        mb.lathe([(0, 0), (.036, 0), (.040, .004), (.041, .095), (.038, .095), (.037, .008), (0, .008)], mat, 16)
        mb.sweep(circle(.0055, 6), [(.039, 0, .078), (.062, 0, .074), (.070, 0, .05), (.062, 0, .026), (.039, 0, .02)],
                 mat, up=(0, 1, 0))
        return mb.finish(name)

    lime = M.solid('kitchen_mug_lime', '#C8D23C', .25)
    kinds = {}
    for n, (k, rz) in enumerate((('w', .5), ('w', 2.2), ('y', 1.2), ('y', -.6), ('w', 3.0), ('w', .9))):     # lower shelf
        if k not in kinds:
            kinds[k] = mug(f'kitchen.nook.mug.{n}', lime if k == 'y' else 'ceramic_white')
            ob = kinds[k]
        else:
            ob = bpy.data.objects.new(f'kitchen.nook.mug.{n}', kinds[k].data)
        stand(ob, .19 + n * .10, .36, 1.474, rz)
    for n in range(8):
        stand(P.tumbler(.12, .08, mat=gl, name=f'kitchen.nook.tankard.{n}'), .80 + (n % 4) * .088, .31 + (n // 4) * .11, 1.474)
    blue = M.solid('kitchen_canister_blue', '#2E4A8C', .2)
    can = None
    for n, u in enumerate((1.16, 1.24, 1.315)):               # tea canisters (plain blue, white lid)
        if can is None:
            mb = mo.MB()
            mb.lathe([(0, 0), (.033, 0), (.035, .004), (.035, .075), (.03, .08), (0, .08)], blue, 14)
            mb.lathe([(0, .08), (.031, .08), (.031, .09), (.012, .096), (.01, .106), (0, .108)], 'ceramic_white', 14)
            can = ob = mb.finish('kitchen.nook.canister.0')
        else:
            ob = bpy.data.objects.new(f'kitchen.nook.canister.{n}', can.data)
        stand(ob, u, .37, 1.474)
    for n in range(7):                                        # upper shelf: tumblers, shaker, teapot
        stand(P.tumbler(mat=gl, name=f'kitchen.nook.tumbler.{n}'), .50 + n * .095, .43, 1.652)
    stand(P.lathe([(0, 0), (.036, 0), (.044, .13), (.042, .14), (.030, .17), (.022, .20), (.020, .22), (0, .22)], 16, 'chrome',
                  name='kitchen.nook.shaker'), .19, .42, 1.652)
    mb = mo.MB()
    mb.lathe([(0, 0), (.04, 0), (.058, .03), (.06, .06), (.045, .10), (.03, .115), (.03, .12), (.012, .13), (.012, .14), (0, .145)],
             'silver_satin', 16)
    mb.sweep(circle(.007, 6), [(.05, 0, .04), (.085, 0, .07), (.10, 0, .11)], 'silver_satin', up=(0, 1, 0))
    mb.sweep(circle(.005, 6), [(-.05, 0, .10), (-.085, 0, .095), (-.095, 0, .065), (-.085, 0, .035), (-.055, 0, .03)],
             'silver_satin', up=(0, 1, 0))
    stand(mb.finish('kitchen.nook.teapot'), .30, .44, 1.652, .4)


# ----------------------------------------------------------------------------- decor
def plaque(name, w=.44, h=.59, relief=.03, base=.004):
    """Cast peacock plaque: scalloped outline (kitchen_outline.OUTLINE) triangulated with an interior grid
    and pushed out by the height map; the rectified photo is the albedo. Origin: centre of the back."""
    import bmesh
    import numpy as np
    from mathutils.geometry import delaunay_2d_cdt
    img = bpy.data.images.load(os.path.join(ART, 'peacock_height.png'))
    img.colorspace_settings.name = 'Non-Color'
    gw, gh = img.size
    hm = np.array(img.pixels[:], dtype=np.float32).reshape(gh, gw, -1)[:, :, 0]      # row 0 = bottom
    bpy.data.images.remove(img)

    def hgt(u, v):
        x, y = min(max(u * gw - .5, 0), gw - 1.001), min(max(v * gh - .5, 0), gh - 1.001)
        i, j = int(x), int(y)
        fx, fy = x - i, y - j
        return float((hm[j, i] * (1 - fx) + hm[j, i + 1] * fx) * (1 - fy) + (hm[j + 1, i] * (1 - fx) + hm[j + 1, i + 1] * fx) * fy)

    out = [Vector(p) for p in OUTLINE]
    if sum(a.x * b.y - b.x * a.y for a, b in zip(out, out[1:] + out[:1])) < 0:
        out.reverse()
    nb, nx, ny = len(out), 84, 112                            # ponytail: 5 mm relief grid (~19 k tris), plenty at 0.5 m
    grid = [Vector(((i + .5) / nx, (j + .5) / ny)) for j in range(ny) for i in range(nx)]
    pts = out + [p for p in grid if hgt(p.x, p.y) > .2]
    vs, _, fs, *_ = delaunay_2d_cdt(pts, [(i, (i + 1) % nb) for i in range(nb)], [list(range(nb))], 1, 1e-5)
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new('UVMap')
    bv = [bm.verts.new(((v.x - .5) * w, -(base + relief * hgt(v.x, v.y)), (v.y - .5) * h)) for v in vs]

    def setuv(f):
        for l in f.loops:
            l[uvl].uv = (l.vert.co.x / w + .5, l.vert.co.z / h + .5)

    for f in fs:
        if len(set(f)) < 3:
            continue
        face = bm.faces.new([bv[i] for i in f])
        face.normal_update()
        if face.normal.y > 0:
            face.normal_flip()
        face.smooth = True
        setuv(face)
    for e in [e for e in bm.edges if len(e.link_faces) == 1]:                         # rim down to the wall
        p, q = e.verts
        inward = e.link_faces[0].calc_center_median() - (p.co + q.co) / 2
        side = bm.faces.new([bm.verts.new(c) for c in (p.co, q.co, (q.co.x, 0, q.co.z), (p.co.x, 0, p.co.z))])
        side.normal_update()
        if side.normal.dot(inward) > 0:
            side.normal_flip()
        setuv(side)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(M.image_mat('kitchen_peacock', os.path.join(ART, 'peacock_plaque.jpg'), None, .5))
    return bpy.data.objects.new(name, me)


def decor(ctx):
    ctx.add(WN.put(plaque('kitchen.plaque'), 1.64, 0, 1.92), ROOM, 'decor')         # nook-wall pier

    # wireless thermostat: landscape rounded 120 x 100 x 24 with a small blank display window (k_765: 0.27 of the
    # plaque width, wider than tall). Body = sweep round the R16 outline in the wall plane, chamfered front edge.
    r = Run(ctx, WN, 'kitchen.thermostat')
    r.mb.sweep([(.010, .024), (.003, .024), (0, .021), (0, 0)], [(u, 0, z) for u, z in rr(1.64, 1.76, 1.385, 1.485, .016)],
               'plastic_white', closed=True, up=(0, -1, 0))
    r.mb.face([(1.646, -.0235, 1.391), (1.754, -.0235, 1.391), (1.754, -.0235, 1.479), (1.646, -.0235, 1.479)],
              'plastic_white', hint=(0, -1, 0))
    r.box(1.712, 1.746, .020, .025, 1.452, 1.467, M.solid('kitchen_lcd', '#5E6462', .2), bev=0)
    r.done()

    # Aluminium 5-bar tread plate 540 x 265 (k_765 crop): clusters of five raised bars at 45 deg, one hand on a
    # 63.5 mm square grid, the other hand on the same grid shifted half a pitch both ways. Dull sheet + polished
    # ridge-shaped bars so the pattern reads from across the room; bars that would cross the cut edge are left out.
    r = Run(ctx, WN, 'kitchen.chequer')
    alu = M.solid('kitchen_chequer', '#B8B8B4', .6, 1)        # mill finish: lighter + rougher than the spec's #9C9C98 /
    bar = M.solid('kitchen_chequer_bar', '#D8D8D4', .2, 1)    # 0.35, which mirrored the navy units and read near-black
    U0, U1, Z0, Z1, PIT, d0, d1 = 1.41, 1.95, .52, .785, .0635, .003, .006
    r.box(U0, U1, 0, d0, Z0, Z1, alu, bev=.001)
    s = math.sqrt(.5)
    for hand in (0, 1):
        e1, e2 = Vector((s, 0, -s if hand else s)), Vector((s if hand else -s, 0, s))    # bar axis, stacking axis
        for i in range(-1, 10):
            for j in range(-1, 6):
                c = Vector((U0 + .026 + (i + .5 * hand) * PIT, 0, Z0 + .025 + (j + .5 * hand) * PIT))
                for k in range(-2, 3):
                    o = c + e2 * (k * .0066)
                    if any(not (U0 + .004 < p.x < U1 - .004 and Z0 + .004 < p.z < Z1 - .004) for p in (o - e1 * .017, o + e1 * .017)):
                        continue
                    lo = [o + e1 * a + e2 * b + Vector((0, -d0, 0)) for a, b in ((-.017, -.0028), (.017, -.0028), (.017, .0028), (-.017, .0028))]
                    hi = [o + e1 * a + e2 * b + Vector((0, -d1, 0)) for a, b in ((-.013, -.0008), (.013, -.0008), (.013, .0008), (-.013, .0008))]
                    r.mb.face(hi, bar, hint=(0, -1, 0))
                    for q in range(4):
                        q2 = (q + 1) % 4
                        r.mb.face([lo[q], lo[q2], hi[q2], hi[q]], bar, hint=(lo[q] + lo[q2]) / 2 - o + Vector((0, -d0 - .01, 0)))
    r.done(lm='dynamic')

    r = Run(ctx, WE, 'kitchen.memo_board')                    # frameless glass board, blank (privacy)
    r.box(.07, .87, .015, .020, .95, 1.95, 'glass_green', bev=.001)
    for u in (.10, .84):
        for z in (.98, 1.92):
            r.at(u, 0, z, RX(90)).lathe([(0, 0), (.006, 0), (.006, .021), (.010, .021), (.010, .026), (0, .026)], 'chrome', 12)
    r.at()
    r.box(.775, .835, .020, .034, 1.895, 1.925, 'black_matt', bev=.003)             # magnetic eraser
    r.done(kind='decor', lm='dynamic')

    r = Run(ctx, WN, 'kitchen.bin.black')                     # black pedal bin, wide side (420) along the pier (t=765 s)
    blk = M.solid('kitchen_bin_black', '#1C1C1D', .45)
    uc = 1.63
    r.box(uc - .21, uc + .21, .03, .36, 0, .52, blk, bev=.015)
    r.box(uc - .22, uc + .22, .022, .368, .50, .60, blk, bev=.02)                   # lid
    r.box(uc - .195, uc + .195, .04, .35, .60, .618, blk, bev=.008)
    r.box(uc - .045, uc + .045, .366, .371, .555, .59, 'silver_satin', bev=.001)    # silver latch plate on the lid front
    r.box(uc - .09, uc + .09, .35, .42, .012, .03, satin(), bev=.004, grain=0)        # wide steel pedal
    r.done(kind='furn')['toggle'] = 'bins'


# ----------------------------------------------------------------------------- lights
# Tuned against the frames (t=377, 759, 761 s): the strips put a bright band on the top tile course only, the
# courses below stay grey (at 14 W/m the whole splashback washed out to off-white); the bounce lights stand in
# for the glow off the white worktops and floor and keep the wall above the units as bright as the tiles.
DOWN_W, STRIP_W, NOOK_STRIP_W, BOUNCE_W, LOW_FILL_W = 72, 5, 12, 45, 35


def lights(ctx):
    cz = ctx.ceil_z(ROOM)
    for i, (x, y) in enumerate(((1.05, .95), (2.15, .95), (1.05, 2.45), (2.15, 2.45))):       # 2 x 2 downlights
        lighting.downlight(ctx, ROOM, X0 + x, Y0 + y, watts=DOWN_W, spot_deg=165, name=f'kitchen.downlight.{i}')
        ctx.add(P.place(P.downlight(name=f'kitchen.downlight_trim.{i}'), (X0 + x, Y0 + y, cz)), ROOM, 'light')
    z = WALL_Z0 - .025                                        # under-cabinet strips (4000 K in the spec; 3100 here:
    # against the 3000 K preview white point anything cooler reads blue, the phone shows the band neutral white)
    for i, (wl, u0, u1) in enumerate(((WE, .912, 1.512), (WE, 2.59, 3.10), (WS, .32, 2.73), (WW, .32, .60))):
        lighting.strip(ctx, ROOM, wl.p(u0 + .03, LED_D, z), wl.p(u1 - .03, LED_D, z), watts_per_m=STRIP_W, kelvin=3100,
                       name=f'kitchen.strip.{i}')
    for i, u in enumerate((1.83, 2.43)):                      # hood spots
        p = WE.p(u, .08, 1.515)
        lighting.downlight(ctx, ROOM, p.x, p.y, z=p.z, watts=3, kelvin=3000, spot_deg=100, radius=.02,
                           name=f'kitchen.hood_spot.{i}')
    lighting.strip(ctx, ROOM, WN.p(.45, -.49, 1.62), WN.p(1.05, -.49, 1.62), watts_per_m=NOOK_STRIP_W, kelvin=2900,
                   name='kitchen.strip.nook')                 # bar under the upper glass shelf
    # ponytail: two soft point lights stand in for the multi-bounce glow off the white worktops and the floor
    # (same trick as lighting.fill). One at mid height so the ceiling stays even (a light 450 under the ceiling
    # left a 1 m blob), one low so the navy base fronts read navy, not black. Invisible to camera and reflections.
    for nm, z, w in (('ceiling_bounce', 1.7, BOUNCE_W), ('low_fill', .95, LOW_FILL_W)):
        b = lighting.bulb(ctx, ROOM, (X0 + 1.6, Y0 + 1.7, z), watts=w, kelvin=3000, radius=.3, name=f'kitchen.{nm}')
        b.visible_camera = b.visible_glossy = False
    mb = mo.MB().at(T(X0 + 1.5, Y0 + 2.2, cz))                # smoke alarm
    mb.lathe([(0, -.045), (.036, -.045), (.050, -.036), (.055, -.012), (.055, 0)], 'plastic_white', 20)
    ctx.add(mb.finish('kitchen.smoke_alarm'), ROOM, 'fit', lm='dynamic')


def build(ctx):
    global NAVY
    NAVY = navy()
    hob_wall(ctx)
    hob(ctx)
    hood(ctx)
    sink_wall(ctx)
    sink(ctx)
    door_wall(ctx)
    nook(ctx)
    decor(ctx)
    lights(ctx)

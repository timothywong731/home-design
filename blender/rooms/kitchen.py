"""Kitchen: navy shaker cabinet runs, quartz worktops + upstands, metro splashbacks, hob + angled hood,
oven tower, American fridge-freezer, sink with two taps, bar nook, plaque, bins, sockets and all lights.

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --only shell,kitchen --preview kitchen --res 540x960 --samples 64 --tag kitchen

Everything is set out in spec/rooms/kitchen.md coordinates (local mm / 1000, origin K0 = door-wall /
sink-wall corner) through four wall frames: u runs along the wall to the viewer's right, d = distance
off the wall into the room, z up. Each cabinet run is one static mesh (carcasses, plinth, cornice,
pelmet) with its shaker fronts and handles parented to it, so the plan footprint is one rectangle.

Everything that opens is tagged for the viewer (blender/INTERACT.md): fronts, drawers, oven / dishwasher /
fridge doors, bin lids, taps, hob burners, the light switch. A moving part or an interior is a Run.sub() - its
own lm='dynamic' object parented to its run; Run.cab() turns a solid carcass into a lined one with contents
(rooms/kitchen_ix.py draws what is inside). The modelled pose is state 0; check state 1 with --pose 1.
Some pairs cannot be open together, as in the real room (the swings cross): EXCL lists them and interlock()
writes each group's partners into its tag as `excl`, for the viewer to shut before it opens the group.
"""
import json
import math
import os
import random

import bpy
from mathutils import Matrix, Vector

from lib import interact as IX, lighting, materials as M, mouldings as mo, props as P, shell
from rooms import kitchen_ix as K
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
    # close views of what opens (compare --pose 0 and --pose 1; refs are frames of the daylight video v2)
    dict(name='ix_tower', pos=(3.45, 6.75, 1.5), look=(1.25, 6.55, 1.05), fov_deg=100, ref='v2 f_0403'),
    dict(name='ix_corner', pos=(2.7, 7.1, 1.65), look=(3.95, 5.75, .55), fov_deg=100, ref='v2 f_0446'),
    dict(name='ix_sink', pos=(2.7, 6.35, 1.7), look=(2.62, 5.5, .8), fov_deg=100, ref='v2 f_0394'),
    dict(name='ix_hob', pos=(3.35, 6.6, 1.5), look=(4.05, 6.6, .9), fov_deg=100, ref='v2 f_0452'),
    dict(name='ix_bins', pos=(3.6, 7.75, 1.55), look=(1.77, 8.56, .4), fov_deg=100, ref='v2 f_0431'),
    dict(name='ix_nook', pos=(2.35, 7.78, 1.5), look=(1.95, 8.9, .5), fov_deg=100, ref='v2 f_0438'),
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


def hinge(w, u, d, z, deg, axis='z'):
    """IX hinge parameters for an axis through (u, d, z) of wall frame w. axis 'z' (upright): deg < 0 = hinged on
    the viewer's left, > 0 on the right. axis 'x' (along the wall): deg > 0 drops a bottom-hung door towards
    the viewer, deg < 0 lifts a top-hung flap or a bin lid."""
    return dict(p=w.p(u, d, z), a=(0, 0, 1) if axis == 'z' else w.M.to_3x3() @ Vector((1, 0, 0)), deg=deg)


def fill(c, items):
    """Contents of an interior c: (K function, u, d, z or shelf level index into c.lv[, kwargs]) each."""
    for fn, u, d, z, *kw in items:
        fn(c.at(u, d, c.lv[z] if isinstance(z, int) else z), **(kw[0] if kw else {}))
    c.at()


def stock(c, u0, u1, d, seed, room=.25):
    """A row of generic groceries (K.row) on the floor and on every shelf of interior c, from u0 to u1 at depth d."""
    rng = random.Random(seed)
    for z in c.lv:
        K.row(c.at((u0 + u1) / 2, d, z), u1 - u0, room, rng)
    c.at()


def carcass():
    """Inside of the cupboards: pale oak melamine (v2 t=388..470 s) - the grain relief of the library oak_light
    under a paler constant colour (the library oak itself rendered a saturated orange in there)."""
    return variant('oak_light', 'kitchen_carcass', **{'Base Color': M.hex_lin('#D3C1A0')})


class Run:
    """One fitted piece: an MB mesh set out in a wall frame + prop children (fronts, handles) + subs: moving
    parts and interiors, each its own lm='dynamic' object parented to the run (so the plan footprint holds)."""

    def __init__(s, ctx, wall, name, ix=None):
        s.ctx, s.w, s.name, s.kids, s.n, s.subs, s.ix = ctx, wall, name, [], 0, [], ix
        s.mb = mo.MB().at(wall.M)

    def sub(s, name, t=None, like=None, **kw):
        """Own object of this run, drawn like a Run: a moving part tagged IX type t with **kw, or sharing the
        tag of the object `like` (a front returned by front()), or an untagged interior."""
        s.subs.append(Run(s.ctx, s.w, name, (t, kw) if t else like))
        return s.subs[-1]

    def cab(s, name, u0, u1, d0, d1, z0, z1, shelves=0, top=True, grain=0, lining=None, shell=True):
        """Carcass that a front opens on, in place of the solid block box(u0, u1, d0, d1, z0, z1): the same
        outside in this run's static mesh (16 mm panels, open at the front d1) and, returned, its interior
        `name`: lining 2 mm inside the panels + shelves. Draw the contents with fill(c, ...); c.lv = heights
        of the floor and of each shelf top. shell=False: the lining only, inside panels the caller has built."""
        t, m = .016, lining or carcass()
        if shell:
            for a, b in ((u0, u0 + t), (u1 - t, u1)):
                s.box(a, b, d0, d1, z0, z1, bev=0, grain=grain)
            s.box(u0 + t, u1 - t, d0, d0 + .006, z0, z1, bev=0, grain=grain)
            for za, zb in ((z0, z0 + t), (z1 - t, z1))[:2 if top else 1]:
                s.box(u0 + t, u1 - t, d0 + .006, d1, za, zb, bev=0, grain=grain)
        c = s.sub(name)
        a, b, za, zb = u0 + t + .002, u1 - t - .002, z0 + t + .002, z1 - (t + .002 if top else .001)
        K.lining(c.mb, a, b, -(d0 + .008), -d1, za, zb, m, 'front' if top else 'front top')
        c.lv = [za]
        for i in range(shelves):
            c.lv.append(za + (zb - za) * (i + 1) / (shelves + 1))
            c.box(a, b, d0 + .008, d1 - .02, c.lv[-1] - .018, c.lv[-1], m, bev=0)
        return c

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

    def front(s, u0, u1, z0, z1, d, handle=None, at='top', slab=False, gap=0.003, g=None, op=None, deg=95,
              label='Cupboard'):
        """Shaker front whose back is d off the wall. handle: 'L' / 'R' vertical T-bar 55 mm from that
        edge, 'H' horizontal T-bar, 'KL' / 'KR' knob 50 mm from that edge; at = 'top' (base units:
        handle near the top) or 'bot' (wall units: near the bottom).
        g = interaction group of the front and its handle. op: 'L' / 'R' = hinged on that edge (default: the
        edge opposite the handle), opening deg; 'flap' = top-hung, lifts deg; 'drop' = bottom-hung, drops deg;
        'slide' = drawer, deg = metres it pulls out. Hinge axes run through the front arris of the door, so an
        open door never crosses its own edge line into the neighbour. -> [front, handle]"""
        w, h = u1 - u0 - gap, z1 - z0 - gap
        s.n += 1
        door = P.panel_door(w, h, stile=.085 if w >= .26 else .055, slab=slab, mat=NAVY, name=f'{s.name}.front.{s.n:02d}')
        parts = [s.prop(door, (u0 + u1) / 2, d, z0 + gap / 2)]
        za, zb, f, br = z0 + gap / 2, z1 - gap / 2, d + 0.02, brass()
        if handle in ('L', 'R'):
            u = u0 + .055 if handle == 'L' else u1 - .055
            parts.append(s.prop(P.handle_bar(finish=br, vertical=True, name=f'{s.name}.pull.{s.n:02d}'), u, f,
                                zb - .17 if at == 'top' else za + .17))
        elif handle == 'H':
            parts.append(s.prop(P.handle_bar(finish=br, name=f'{s.name}.pull.{s.n:02d}'), (u0 + u1) / 2, f,
                                zb - .045 if at == 'top' else za + .06))
        elif handle in ('KL', 'KR'):                          # wall corner knobs: level with the top of the T-bars
            u = u0 + .05 if handle == 'KL' else u1 - .05
            parts.append(s.prop(P.handle_knob(finish=br, name=f'{s.name}.knob.{s.n:02d}'), u, f,
                                zb - .08 if at == 'top' else za + .255))
        op = op or {'R': 'L', 'KR': 'L', 'L': 'R', 'KL': 'R'}.get(handle)
        if g and op == 'slide':
            IX.tag_many(parts, 'slide', g=g, label=label, d=s.w.M.to_3x3() @ Vector((0, -deg, 0)))
        elif g:
            uc = (u0 + u1) / 2
            kw = (hinge(s.w, u0 + gap / 2, f, za, -deg) if op == 'L' else hinge(s.w, u1 - gap / 2, f, za, deg) if op == 'R'
                  else hinge(s.w, uc, f, zb, -deg, 'x') if op == 'flap' else hinge(s.w, uc, f, za, deg, 'x'))
            IX.tag_many(parts, 'hinge', g=g, label=label, **kw)
        return parts

    def cornice(s, ur, ul, depth, z, ret_r=False, ret_l=False, mitre_r=False, mitre_l=False, profile=CORNICE):
        """Cornice along the front (right -> left so the profile projects into the room), with returns to
        the wall at exposed ends or a 45 deg cut where the next run carries on round an internal corner."""
        pts = ([(ur, 0, z)] if ret_r else []) + [(ur, -depth, z), (ul, -depth, z)] + ([(ul, 0, z)] if ret_l else [])
        s.mb.sweep(profile, pts, NAVY, ends=((-1, -1, 0) if mitre_r else None, (1, -1, 0) if mitre_l else None))

    def done(s, kind='fit', plan_sym=None, lm=None, uv=False):
        root = s.mb.finish(s.name)
        if uv:
            M.uv_box(root, rotate=(uv == 'rot'))
        dyn = []
        for c in s.subs:                                      # moving parts and interiors
            dyn.append(c.mb.finish(c.name))
            if isinstance(c.ix, tuple):
                IX.tag(dyn[-1], c.ix[0], **c.ix[1])
            elif c.ix is not None:
                IX.tag(dyn[-1], **json.loads(c.ix['ix']))
            s.kids += [dyn[-1]] + c.kids
        for k in s.kids:
            k.parent = root                                   # root sits at the world origin: no parent inverse
        out = s.ctx.add(root, ROOM, kind, plan_sym=plan_sym, lm=lm)
        for k in dyn + [k for k in s.kids if 'ix' in k.keys()]:
            k['lm'] = 'dynamic'                               # what moves, and what is behind it, is probe-lit
        return out


def wall_unit(r, u0, u1, depth=0.30, pelmet=True, side_l=False, side_r=False, bays=()):
    """Wall-unit carcass 1455..2355 with the filler behind the cornice and the light pelmet. bays = (name, ua,
    ub, shelves) per cupboard behind a door: lined carcasses (Run.cab), returned in order; what is left of
    u0..u1 stays a solid block (blind corners)."""
    grain, u, out = (0 if u1 - u0 > WALL_Z1 - WALL_Z0 else 2), u0, []
    for name, ua, ub, n in bays:
        if ua > u:
            r.box(u, ua, 0, depth, WALL_Z0, WALL_Z1, bev=0, grain=grain)
        out.append(r.cab(name, ua, ub, 0, depth, WALL_Z0, WALL_Z1, n, grain=grain))
        u = ub
    if u < u1:
        r.box(u, u1, 0, depth, WALL_Z0, WALL_Z1, bev=0 if bays else .001, grain=grain)
    r.box(u0, u1, 0, depth + .02, WALL_Z1, WALL_Z1 + .044, bev=0)
    if pelmet:
        pelmet_lip(r, u0, u1, depth)
        for on, a, b in ((side_l, u0, u0 + .018), (side_r, u1 - .018, u1)):
            if on:
                r.box(a, b, 0, depth, PELMET_Z, WALL_Z0 + .001, bev=.0005)
    return out


def bin_body(r, u0, u1, d0, d1, z0, z1, mat, bev, wall=.012):
    """Open-topped bin body: the sides of r.box(u0, u1, d0, d1, z0, z1, mat, bev) with the same chamfered
    edges, and a flat rim `wall` wide where the top face was (the inside is the liner, an interior of its own)."""
    c = Vector(((u0 + u1) / 2, -(d0 + d1) / 2, 0))

    def ring(i, k, z):                                        # chamfered rectangle: sides inset i, corners cut k
        a, b, y0, y1 = u0 + i, u1 - i, -d1 + i, -d0 - i
        return [Vector((x, y, z)) for x, y in ((a + k, y0), (b - k, y0), (b, y0 + k), (b, y1 - k), (b - k, y1), (a + k, y1),
                                               (a, y1 - k), (a, y0 + k))]
    lv = [ring(bev, 0, z0), ring(0, bev, z0 + bev), ring(0, bev, z1 - bev), ring(bev, 0, z1), ring(bev + wall, 0, z1)]
    for lo, hi in zip(lv, lv[1:]):
        for j in range(8):
            q = [lo[j], lo[(j + 1) % 8], hi[(j + 1) % 8], hi[j]]
            if (q[1] - q[0]).cross(q[3] - q[0]).length + (q[2] - q[1]).cross(q[3] - q[1]).length < 1e-9:
                continue                                      # corner sliver of a ring without corner cuts
            flat = abs(lo[0].z - hi[0].z) < 1e-9
            r.mb.face(q, mat, hint=(0, 0, 1) if flat else (sum(q, Vector()) / 4 - c).to_2d().to_3d())


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
    G = 'kitchen.base.hob.'
    r.box(.930, SY, 0, .54, 0, .15)                           # plinth, recessed 40
    r.box(2.84, SY, 0, .58, .15, BASE_TOP)                    # blind corner behind the dishwasher
    r.box(.912, .930, 0, .60, 0, BASE_TOP)                    # H1 end panel to the floor
    r.box(2.80, 2.84, .58, .60, .15, BASE_TOP, bev=0)         # corner filler between the two door planes
    z0, z1 = .15, .868
    c = r.cab(G + 'h2.in', .930, 1.530, 0, .58, .15, BASE_TOP, 1)
    r.front(.930, 1.530, z0, z1, .58, 'R', g=G + 'h2', deg=100)                 # H2 600 door (opened at v2 t=457 s)
    fill(c, [(K.tub, 1.14, .30, 0, dict(w=.34, d=.28, h=.22)), (K.carton, 1.41, .25, 0, dict(w=.16, d=.24, h=.26)),
             (K.jar, 1.05, .30, 1, dict(h=.16, dia=.09)), (K.jar, 1.17, .34, 1, dict(h=.13)),
             (K.carton, 1.30, .28, 1, dict(w=.10, d=.18, h=.20, mat=K.hue(2))), (K.carton, 1.42, .30, 1, dict(mat=K.hue(0)))])
    # H3 200: a door on tray storage, not a pull-out (v2 t=460 s). There it hangs on the drawer side; here it
    # follows the modelled handle (hinge opposite), which also keeps it clear of the drawers.
    c = r.cab(G + 'h3.in', 1.530, 1.730, 0, .58, .15, BASE_TOP)
    r.front(1.530, 1.730, z0, z1, .58, 'R', g=G + 'h3')
    fill(c, [(K.board, 1.585, .30, 0, dict(w=.44, h=.50)), (K.board, 1.625, .30, 0, dict(w=.40, h=.42, mat=K.col('tray', '#8E949A', .4, 1))),
             (K.board, 1.665, .32, 0, dict(w=.36, h=.34))])
    r.cab(G + 'h4.in', 1.730, 2.530, 0, .58, .15, BASE_TOP)   # H4 pan drawers: 175 slab + 2 x 270 framed
    for n, (za, zb, zf, h, out) in enumerate(((.690, z1, .705, .10, .30), (.420, .690, .440, .19, .35), (z0, .420, .172, .19, .40))):
        f = r.front(1.730, 2.530, za, zb, .58, 'H', slab=not n, g=f'{G}drawer.{n}', op='slide', deg=out, label='Drawer')
        dr = r.sub(f'{G}drawer.{n}.box', like=f[0])
        K.drawer(dr.at(2.13, .58, zf), .74, .50, h)
        dr.lv = [zf + .012]
        if n == 0:
            K.cutlery(dr.at(2.13, .58, zf + .012), .70, .47)
        elif n == 1:                                          # crockery (v2 t=448 s)
            fill(dr, [(K.plates, 1.92, .44, 0, dict(n=8)), (K.plates, 1.92, .20, 0, dict(n=5, dia=.21)),
                      (K.bowls, 2.20, .42, 0, dict(n=5)), (K.bowls, 2.20, .20, 0, dict(n=3, dia=.19)),
                      (K.plates, 2.39, .28, 0, dict(n=4, dia=.18, mat=K.col('china_blue', '#31456E', .1)))])
        else:                                                 # pans and food boxes (v2 t=446 s)
            fill(dr, [(K.pot, 1.92, .44, 0, dict(dia=.24, h=.10, handle=0)), (K.pot, 1.90, .19, 0, dict(dia=.18, h=.09, handle=.12)),
                      (K.tub, 2.22, .40, 0, dict(w=.20, d=.15, h=.09)), (K.tub, 2.22, .19, 0, dict(w=.18, d=.14, h=.07, lid=K.hue(7))),
                      (K.tub, 2.40, .30, 0, dict(w=.14, d=.20, h=.11, lid=K.hue(2)))])
        dr.at()
    # H5 corner door, knob. Hung on the corner side (opposite the knob), its knob meets the shut dishwasher front
    # at 82 deg: a limit of the room, not of the pair (EXCL keeps it out of the dropped dishwasher door).
    c = r.cab(G + 'h5.in', 2.530, 2.84, 0, .58, .15, BASE_TOP, 1)
    r.front(2.530, 2.800, z0, z1, .58, 'KL', g=G + 'h5', deg=80)
    fill(c, [(K.pot, 2.68, .30, 0, dict(dia=.20, h=.14, handle=0)), (K.pot, 2.68, .30, 1, dict(dia=.16, h=.08, handle=0))])
    r.done(plan_sym='base_unit')

    w = Run(ctx, WE, 'kitchen.worktop.hob')                   # hob-wall leg of the L, joint at the corner
    w.box(.882, SY, 0, .62, BASE_TOP, WT_TOP, QUARTZ, bev=.002)
    w.box(.882, SY, 0, .02, WT_TOP, TILE_Z0, QUARTZ, bev=.002)
    w.done(plan_sym='worktop', uv=True)

    r = Run(ctx, WE, 'kitchen.wall.w1')                       # W1 600, both sides exposed
    c, = wall_unit(r, .912, 1.512, side_l=True, side_r=True, bays=[('kitchen.wall.w1.in', .912, 1.512, 2)])
    r.front(.912, 1.512, WALL_Z0, WALL_Z1, .30, 'R', 'bot', g='kitchen.wall.w1')      # snacks (v2 t=469 s)
    stock(c, .96, 1.47, .16, 11)
    r.cornice(1.512, .912, .32, WALL_Z1, ret_r=True, ret_l=True)
    led(r, .912, 1.512)
    r.done(plan_sym='wall_unit')

    r = Run(ctx, WE, 'kitchen.wall.w2')                       # W2 500 pair of doors + the corner
    ca, cb = wall_unit(r, 2.59, SY, side_l=True, bays=[('kitchen.wall.w2a.in', 2.59, 2.84, 2), ('kitchen.wall.w2b.in', 2.84, 3.09, 2)])
    r.front(2.59, 2.84, WALL_Z0, WALL_Z1, .30, 'R', 'bot', g='kitchen.wall.w2a')
    r.front(2.84, 3.09, WALL_Z0, WALL_Z1, .30, 'R', 'bot', g='kitchen.wall.w2b')
    stock(ca, 2.63, 2.80, .16, 12)
    stock(cb, 2.88, 3.05, .16, 13)
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
    r.at()
    for i, (bu, bd, br) in enumerate(burners):                # control knobs along the front edge: knob i lights
        g, dia = f'kitchen.hob.{i}', 2 * br + .010            # burner i, a crown of flames round the cap
        k = r.sub(f'kitchen.hob.knob.{i}', 'trigger', g=g, label='Hob')
        k.at(uc - .14 + i * .045, d1 - .04, z + .004).lathe([(0, 0), (.019, 0), (.019, .018), (.016, .024), (0, .024)],
                                                            'nickel_brushed', 16)
        fl = r.prop(P.flame_ring(dia, round(math.pi * dia / .0125), .016, name=f'kitchen.hob.flame.{i}'), bu, bd, z + .0165)
        IX.tag(fl, 'show', g=g, when=1, fx='flame')
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
    G = 'kitchen.base.sink.'
    r.box(.54, SX, 0, .54, 0, .15)                            # plinth, closing the internal corner
    r.box(.58, .60, 0, .58, .15, BASE_TOP)
    r.box(2.38, SX, 0, .58, .15, BASE_TOP)                    # the blind end behind the oven tower
    z0, z1 = .15, .868
    # S1 integrated dishwasher: the front drops on its bottom edge, the appliance door on its back (v2 t=381 s)
    st = K.col('dw_steel', '#A9ACAD', .35, 1)
    c = r.cab('kitchen.dishwasher.in', .60, 1.20, 0, .58, .15, BASE_TOP, lining=st)
    K.dishwasher(c.at(.90, .525, .19), .54, .64, .50)
    c.at()
    f = r.front(.60, 1.20, z0, z1, .58, 'H', g='kitchen.dishwasher', op='drop', deg=85, label='Dishwasher')
    dw = r.sub('kitchen.dishwasher.door', like=f[0])
    dw.box(.625, 1.175, .535, .58, .19, .84, st, bev=.004)
    dw.box(.80, 1.00, .525, .535, .40, .50, 'plastic_white', bev=.003)             # detergent drawer
    # S2 sink base pair: the bowls, the waste disposer and the trap under them (v2 t=394 s)
    c = r.cab(G + 's2.in', 1.20, 2.00, 0, .58, .15, BASE_TOP, top=False)
    r.front(1.20, 1.60, z0, z1, .58, 'R', g=G + 's2a', deg=85)                     # 85: clear of the dishwasher door
    r.front(1.60, 2.00, z0, z1, .58, 'L', g=G + 's2b', deg=85)                     # ... and of the oven door's handle
    a, b, e0, e1 = SINK
    K.lining(c.mb, a - .001, b + .001, -(e0 - .001), -(e1 + .001), .672, .875, M.solid('kitchen_sink_steel', '#8C8D8A', .45, 1),
             'top', out=True)                                 # underside of the two bowls
    c.box(1.59, 1.61, .52, .578, c.lv[0], .672, carcass(), bev=0)                     # post between the doors
    c.box(1.47, 1.77, .29, .33, .53, .57, 'plastic_white', bev=.004)               # waste pipe
    c.at(1.392, .31, .40).lathe([(0, 0), (.08, 0), (.085, .02), (.085, .22), (.05, .272), (0, .272)], 'black_matt', 14)
    c.at(1.771, .31, .50).lathe([(0, 0), (.035, 0), (.035, .08), (.02, .09), (.02, .172), (0, .172)], 'plastic_white', 12)
    fill(c, [(K.pot, 1.82, .40, 0, dict(dia=.24, h=.17, mat='plastic_white', handle=0)),
             (K.bottle, 1.27, .40, 0, dict(h=.27, body=K.hue(3, .2))), (K.bottle, 1.30, .22, 0, dict(h=.24, body=K.hue(1, .2))),
             (K.bottle, 1.68, .42, 0, dict(h=.26, body=K.hue(4, .2))), (K.carton, 1.92, .18, 0, dict(w=.09, d=.12, h=.22))])
    # S3: a 380 door hung on the oven-tower side (opposite its handle) + a 70 corner filler against the tower, the
    # clearance the real corner must have: the oven fronts stand 22 mm proud of the tower in the plane of that edge
    # and the lower oven's bar handle 64, so a full 450 door could not swing. 90 deg: 7 mm short of that bar.
    c = r.cab(G + 's3.in', 2.00, 2.38, 0, .58, .15, BASE_TOP, 1)
    r.front(2.00, 2.38, z0, z1, .58, 'L', g=G + 's3', deg=90)
    r.box(2.3815, 2.45, .58, .60, z0 + .0015, z1 - .0015)
    fill(c, [(K.pot, 2.14, .34, 0, dict(dia=.24, h=.13, handle=0)), (K.pot, 2.24, .16, 0, dict(dia=.16, h=.09, handle=0)),
             (K.tub, 2.15, .32, 1, dict(w=.22, d=.16, h=.10, lid=K.hue(5))), (K.bowls, 2.27, .17, 1, dict(n=3, dia=.15))])
    r.done(plan_sym='base_unit')

    w = Run(ctx, WS, 'kitchen.worktop.sink')                  # sink-wall leg, butt joint at spec x 2430
    a, b, c, e = SINK
    for u0, u1, d0, d1 in ((.62, a, 0, .62), (b, SX, 0, .62), (a, b, 0, c), (a, b, e, .62)):
        w.box(u0, u1, d0, d1, BASE_TOP, WT_TOP, QUARTZ, bev=0)   # flush seams round the cut-out
    w.box(.02, SX, 0, .02, WT_TOP, TILE_Z0, QUARTZ, bev=.002)    # upstands: sink wall + door-wall return
    w.box(SX - .02, SX, .02, .60, WT_TOP, TILE_Z0, QUARTZ, bev=.002)
    w.done(plan_sym='worktop', uv=True)

    r = Run(ctx, WS, 'kitchen.wall.sink')                     # T1..T5, spec x 2730 -> 0
    t1, t2 = wall_unit(r, .32, 1.225, bays=[('kitchen.wall.t1.in', .32, .625, 2), ('kitchen.wall.t2.in', .625, 1.225, 2)])
    t5, = wall_unit(r, 2.425, SX, bays=[('kitchen.wall.t5.in', 2.425, 2.725, 2)])   # T5 + blind corner
    pelmet_lip(r, 1.225, 2.425)
    r.box(1.225, 2.425, 0, .32, WALL_Z1, WALL_Z1 + .044, bev=0)
    # T1 corner knob door and T2 600 hang on the same stile: 85 deg keeps T1's knob off T2
    r.front(.32, .625, WALL_Z0, WALL_Z1, .30, 'KL', 'bot', g='kitchen.wall.t1', deg=85)
    r.front(.625, 1.225, WALL_Z0, WALL_Z1, .30, 'R', 'bot', g='kitchen.wall.t2', deg=85)
    # T5 300 (handle on the corner side, f_0378 / f_0396): opens until it reaches the side of the oven tower
    r.front(2.425, 2.725, WALL_Z0, WALL_Z1, .30, 'R', 'bot', g='kitchen.wall.t5', deg=66)
    stock(t1, .36, .59, .15, 16)
    fill(t2, [(K.plates, .80, .155, 0, dict(n=8)), (K.bowls, 1.06, .15, 0, dict(n=5)), (K.plates, .78, .15, 1, dict(n=6, dia=.21)),
              (K.bowls, 1.0, .15, 1, dict(n=4, dia=.14)), (K.jar, 1.14, .14, 1, dict(h=.15, dia=.09)), (K.dish, .92, .16, 2)])
    stock(t5, 2.47, 2.68, .15, 17)
    # T3 plate rack 900: lift-up flap door over an open rack
    u0, u1, zr = 1.225, 2.125, 1.975
    c = r.cab('kitchen.wall.t3.in', u0, u1, 0, .30, zr, WALL_Z1)
    r.front(u0, u1, zr, WALL_Z1, .30, 'H', 'bot', g='kitchen.wall.t3', op='flap', deg=85)
    stock(c, 1.30, 2.05, .15, 15)
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
    # Interaction: the tap is the trigger, its side lever tips 22 deg towards you, the water falls from the spray
    # head into the +X bowl.
    ch, up = 'chrome', (1, 0, 0)
    BODY, RISE, R, HEAD = .20, .32, .115, .15
    g, swing = 'kitchen.tap.mixer', Matrix.Rotation(math.radians(-40), 4, 'Z')
    tap = r.sub('kitchen.sink.mixer', 'trigger', g=g, label='Tap')
    mb = tap.at(1.60, .06, WT_TOP)
    mb.lathe([(0, 0), (.027, 0), (.027, .004), (.022, .007), (.022, BODY), (.017, BODY + .006), (0, BODY + .006)], ch, 16)
    lever = r.sub('kitchen.sink.mixer.lever', 'hinge', g=g, label='Tap', **hinge(WS, 1.63, .06, WT_TOP + .075, 22, 'x'))
    mb = lever.at(1.60, .06, WT_TOP)
    mb.tube([(.018, 0, .075), (.05, 0, .075)], .013, ch, 10)
    mb.sweep(circle(.004, 6), [(.046, 0, .08), (.052, -.006, .11), (.062, -.012, .145)], ch, up=(0, 1, 0))
    head = swing @ Vector((0, -2 * R, 0))                     # spray head outlet, off the tap axis in the wall frame
    ws = r.prop(P.water_stream(WT_TOP + HEAD - zf - .0005, name='kitchen.sink.mixer.water'), 1.60 + head.x, .06 - head.y,
                WT_TOP + HEAD)                                # ends 1 mm above the bowl floor
    IX.tag(ws, 'show', g=g, when=1, fx='water')
    mb = tap.at(1.60, .06, WT_TOP, swing)                     # arch plane: into the room, swung 40 deg to +X
    line = [(0, 0, BODY), (0, 0, RISE)] + [(0, -R + R * math.cos(t), RISE + R * math.sin(t))
                                          for t in (math.pi * k / 14 for k in range(1, 15))] + [(0, -2 * R, HEAD + .12)]
    mb.sweep(circle(.008, 8), line, ch, up=up)                # hose / riser
    mb.at(mb.M @ T(0, -2 * R, HEAD)).lathe([(0, 0), (.019, 0), (.019, .02), (.014, .03), (.014, .12), (0, .12)], ch, 12)
    mb = tap.at(1.60, .06, WT_TOP, swing)
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
    # (b) brushed-nickel filter tap at spec x 1180: no lever of its own, the tap is the trigger
    g = 'kitchen.tap.filter'
    mb = r.sub('kitchen.sink.filter_tap', 'trigger', g=g, label='Filter tap').at(1.87, .06, WT_TOP)
    mb.lathe([(0, 0), (.021, 0), (.021, .05), (.017, .056), (0, .056)], nk, 14)
    mb.sweep(circle(.0095, 8), [(0, 0, .05), (0, 0, .225), (0, -.022, .25), (0, -.105, .25), (0, -.122, .232), (0, -.122, .19)],
             nk, up=up)
    ws = r.prop(P.water_stream(WT_TOP + .19 - zf - .0005, .008, .05, name='kitchen.sink.filter_tap.water'), 1.87, .182, WT_TOP + .19)
    IX.tag(ws, 'show', g=g, when=1, fx='water')
    r.at()
    r.done(plan_sym='sink', lm='dynamic')


# ----------------------------------------------------------------------------- door wall (x = 0)
def door_wall(ctx):
    r = Run(ctx, WW, 'kitchen.wall.corner')                   # knob-door cupboard spec y 320 -> 600, faces +X
    c, = wall_unit(r, .32, .60, bays=[('kitchen.wall.corner.in', .32, .60, 2)])
    # hung beside the oven tower (opposite the knob), swinging across the corner: at 80 deg the knob meets the
    # tower side. T5 swings through the same corner (EXCL).
    r.front(.32, .60, WALL_Z0, WALL_Z1, .30, 'KL', 'bot', g='kitchen.wall.corner', deg=78)
    stock(c, .36, .56, .15, 18)
    r.cornice(.60, .32, .32, WALL_Z1, mitre_l=True)
    led(r, .32, .60)
    r.done(plan_sym='wall_unit')

    r = Run(ctx, WW, 'kitchen.tower')                         # oven tower spec y 600 -> 1200
    SATIN = satin()
    a, b, gl = .60, 1.20, 'black_gloss'
    # The appliance fronts sit between the 18 mm side panels (v2 t=402 s: a navy strip either side of the ovens),
    # which also puts their edge 2 mm outside the nose of the sink-run worktop: the doors can drop past it.
    ua, ub, uc = a + .022, b - .022, (a + b) / 2
    r.box(a, b, 0, .56, 0, .15)
    for u0, u1 in ((a, a + .018), (b - .018, b)):             # carcass: sides, back, decks between the appliances
        r.box(u0, u1, 0, .60, .15, TALL_Z1)
    r.box(a + .018, b - .018, 0, .02, .15, TALL_Z1, bev=0)
    for z0, z1 in ((.15, .156), (.545, .556), (1.048, 1.150), (1.498, 1.640), (TALL_Z1 - .016, TALL_Z1)):
        r.box(a + .018, b - .018, .02, .60, z0, z1, bev=0)
    r.box(a, b, 0, .62, TALL_Z1, TALL_Z1 + .044, bev=0)

    def oven(n, z0, z1, f, label, deg=85):
        """Drop-down door `n` over z0..z1, hung on the bottom edge of its front face (f off the wall), bar
        handle underneath when down. Behind it the oven itself (K.oven) and its lamp. -> the door, to draw into."""
        g = f'kitchen.oven.{n}'
        K.oven(r.sub(g + '.in').at(uc, .60, z0 + .004), b - a - .036, z1 - z0 - .008)      # frame to the side panels
        r.sub(g + '.light', 'show', g=g, when=1, fx='glow').box(uc - .05, uc + .05, .24, .30, z1 - .052, z1 - .046,
                                                                P.emissive('#FFE2B0', 12.0), bev=0)     # cavity lamp
        return r.sub(g + '.door', 'hinge', g=g, label=label, **hinge(WW, uc, f, z0, deg, 'x'))

    def bar(t, z):                                            # flat steel bar handle on two posts
        t.box(ua + .03, ub - .03, .650, .664, z, z + .028, SATIN, bev=.003, grain=0)
        for u in (ua + .075, ub - .075):
            t.box(u - .012, u + .012, .62, .652, z + .006, z + .022, SATIN, bev=.002)

    t = oven('low', .152, .548, .621, 'Lower oven')
    t.box(ua + .001, ub - .001, .60, .618, .153, .547, gl, bev=.001)   # lower drop-front appliance, 1 mm inside its steel surround
    for u0, u1, z0, z1 in ((ua, ub, .152, .164), (ua, ub, .536, .548), (ua, ua + .012, .152, .548), (ub - .012, ub, .152, .548)):
        t.box(u0, u1, .60, .621, z0, z1, SATIN, bev=.001)
    bar(t, .49)
    # flat (90, not 85): the door edge passes 16 mm inside the reach of the S3 handle and lies 11 mm under its foot
    t = oven('mid', .553, 1.050, .622, 'Oven', 90)
    t.box(ua, ub, .60, .622, .553, 1.050, gl, bev=.002)       # single oven: door, handle, control band
    bar(t, 1.005)
    r.box(ua, ub, .60, .618, 1.053, 1.143, gl, bev=.001)
    r.mb.face([(uc + .02 * math.cos(t), -.6195, 1.098 + .02 * math.sin(t)) for t in (2 * math.pi * k / 16 for k in range(16))],
              P.emissive('#E0506A', 1.5), hint=(0, -1, 0))    # round colour display (no glyphs)
    t = oven('top', 1.148, 1.500, .622, 'Top oven')
    t.box(ua, ub, .60, .622, 1.148, 1.500, gl, bev=.002)      # compact oven, control band at the top
    bar(t, 1.455)
    r.box(ua, ub, .60, .618, 1.503, 1.597, gl, bev=.001)
    r.mb.face([(uc - .15, -.6195, 1.542), (uc - .03, -.6195, 1.542), (uc - .03, -.6195, 1.556), (uc - .15, -.6195, 1.556)],
              P.emissive('#CFE4FF', 1.5), hint=(0, -1, 0))    # display glow bar (digits deliberately not drawn)
    r.box(ua, ub, .60, .612, 1.60, 1.64, 'oak_light', bev=0, grain=0)      # the bare-oak filler strip
    c = r.cab('kitchen.tower.top.in', a + .002, b - .002, .014, .60, 1.624, TALL_Z1, 1, shell=False)
    # oven dishes (v2 t=407 s); the open door crosses the raised T3 flap and the T5 door round the corner (EXCL)
    r.front(a, b, 1.64, TALL_Z1, .60, 'R', 'bot', g='kitchen.tower.top', deg=95)
    fill(c, [(K.dish, .79, .30, 0), (K.dish, .79, .30, 1.705, dict(w=.26, d=.17)), (K.bowls, 1.05, .30, 0, dict(n=4, dia=.20)),
             (K.dish, .82, .30, 1, dict(w=.34, d=.24)), (K.pot, 1.06, .30, 1, dict(dia=.20, h=.12, handle=0))])
    r.cornice(b, a, .62, TALL_Z1, ret_l=True)
    r.done(plan_sym='oven_tower')

    r = Run(ctx, WW, 'kitchen.fridge_housing')                # spec y 1200 -> 2230
    a, b = 1.20, 2.23
    r.box(a, a + .018, 0, .60, 0, TALL_Z1)
    r.box(b - .018, b, 0, .60, 0, TALL_Z1)
    c = r.cab('kitchen.fridge_housing.in', a + .018, b - .018, 0, .58, 2.04, TALL_Z1)
    r.box(a, b, 0, .62, TALL_Z1, TALL_Z1 + .044, bev=0)
    r.box(a + .018, b - .018, 0, .006, 0, 2.04, bev=0)        # dark back behind the fridge and in the niche
    r.front(a + .018, b - .018, 2.04, TALL_Z1, .58, 'H', 'bot', g='kitchen.fridge_housing', op='flap', deg=85)
    fill(c, [(K.tub, 1.50, .30, 0, dict(w=.42, d=.30, h=.22, lid=K.hue(4))), (K.carton, 1.92, .30, 0, dict(w=.30, d=.24, h=.18)),
             (K.pot, 1.72, .28, 0, dict(dia=.22, h=.16, handle=0))])
    r.cornice(b, a, .62, TALL_Z1, ret_r=True)
    r.done(plan_sym='tall_unit')

    r = Run(ctx, WW, 'kitchen.fridge')                        # American side-by-side 912 x 1780 x 716, no magnets
    g = M.solid('kitchen_graphite', '#2B2C2E', .55, .3)
    u0, u1 = 1.715 - .456, 1.715 + .456
    sp = u0 + .42 * .912                                      # door split: ice / water door is 0.42 of the width
    # cabinet: sides, mullion, back, top and bottom round the freezer (ice / water door) and fridge compartments
    for a, b in ((u0, u0 + .03), (u1 - .03, u1)):
        r.box(a, b, .02, .64, .04, 1.78, g, bev=0)
    r.box(u0 + .03, u1 - .03, .02, .05, .04, 1.78, g, bev=0)
    for z0, z1 in ((.04, .08), (1.74, 1.78)):
        r.box(u0 + .03, u1 - .03, .05, .64, z0, z1, g, bev=0)
    r.box(sp - .015, sp + .015, .05, .64, .08, 1.74, g, bev=0)
    r.box(u0 + .02, u1 - .02, .06, .62, 0, .04, 'black_matt', bev=0)
    # Each door swings 100 deg on its outer front edge and carries half of the recessed grip strip between
    # them, its inner panel and bins; behind it shelves, drawers and a light that comes on (v2 t=414..423 s).
    G, glow = 'kitchen.fridge.', P.emissive('#EAF3FF', 5.0)
    for nm, lab, ca, cb, hu, deg, sg in (('freezer', 'Freezer', u0 + .03, sp - .015, u0, -98, -1),
                                          ('fridge', 'Fridge', sp + .015, u1 - .03, u1, 100, 1)):
        um, w = (ca + cb) / 2, cb - ca
        K.fridge(r.sub(G + nm + '.in').at(um, .64, .082), w - .004, 1.656, .588, freezer=nm == 'freezer')
        r.sub(G + nm + '.light', 'show', g=G + nm, when=1, fx='glow').box(um - w * .3, um + w * .3, .25, .50, 1.725, 1.737,
                                                                          glow, bev=0)
        t = r.sub(G + nm + '.door', 'hinge', g=G + nm, label=lab, **hinge(WW, hu, .716, .04, deg))
        K.fridge_door(t.at(um + sg * .01, .645, .10), w - .08, 1.60, 2 if nm == 'freezer' else 4, ice=nm == 'freezer')
        t.at()
        t.box(sp, sp + sg * .005, .64, .70, .04, 1.78, 'black_matt', bev=0)       # its half of the grip strip
        if nm == 'fridge':
            t.box(sp + .005, u1, .645, .716, .04, 1.78, g, bev=.004, grain=2)
            continue
        n0, n1, m0, m1 = u0 + .046, u0 + .336, .815, 1.205    # dispenser niche 290 x 390, centre z 1010
        for a, b, z0, z1 in ((u0, n0, .04, 1.78), (n1, sp - .005, .04, 1.78), (n0, n1, .04, m0), (n0, n1, m1, 1.78)):
            t.box(a, b, .645, .716, z0, z1, g, bev=0, grain=2)
        t.box(n0, n1, .645, .656, m0, m1, 'black_gloss', bev=0)
        t.box(n0 + .02, n1 - .02, .656, .705, m0, m0 + .012, 'black_matt', bev=.002)   # drip tray
        t.box(n0 + .10, n1 - .10, .656, .69, m1 - .05, m1, 'black_matt', bev=.004)     # spout block
        t.box(n0, n1, .716, .7172, m1 + .012, m1 + .062, 'black_gloss', bev=0)         # control strip
    r.done(plan_sym='fridge')

    sw = ctx.add(WW.put(P.switch_plate(1, name='kitchen.switch'), 2.34, 0, 1.25), ROOM, 'fit', lm='dynamic')
    IX.tag(sw, 'light', rooms=[ROOM], label='Lights')         # downlights and under-cabinet strips together

    r = Run(ctx, WW, 'kitchen.bin.steel')                     # pedal bin between the housing and the hall door
    g, st = 'kitchen.bin.steel', satin()                      # lid lifts 70 deg on its back edge, the pedal works it
    r.box(2.255, 2.485, .035, .405, 0, .03, 'black_matt', bev=0)
    bin_body(r, 2.25, 2.49, .03, .41, .03, .60, st, .012)
    for u0, u1, d0, d1 in ((2.248, 2.492, .028, .042), (2.248, 2.492, .398, .412), (2.248, 2.262, .042, .398),
                           (2.478, 2.492, .042, .398)):       # the black rim band, now a ring round the opening
        r.box(u0, u1, d0, d1, .597, .606, 'black_matt', bev=.001)
    K.lining(r.sub(g + '.in').mb, 2.274, 2.466, -.054, -.386, .28, .60, 'black_matt', open='top')      # inner bucket
    r.sub(g + '.lid', 'hinge', g=g, label='Bin', **hinge(WW, 2.37, .025, .65, -70, 'x')).box(
        2.245, 2.495, .025, .415, .606, .65, st, bev=.012, grain=1)
    r.sub(g + '.pedal', 'trigger', g=g, label='Bin').box(2.30, 2.44, .40, .46, .012, .028, 'black_matt', bev=.004)
    r.done(kind='furn')['toggle'] = 'bins'


# ----------------------------------------------------------------------------- bar nook (recess d < 0)
def nook(ctx):
    a, b, back = .12, 1.37, -.52
    r = Run(ctx, WN, 'kitchen.nook.base')                     # 350 + 350 + 550 (t=765 s), faces 10 behind the wall face
    r.box(a, b, back, -.07, 0, .15)
    for n, (u0, u1, hd) in enumerate(((a, .47, 'R'), (.47, .82, 'R'), (.82, b, 'L'))):       # drinks and bags (v2 t=438 s)
        c = r.cab(f'kitchen.nook.base.{n}.in', u0, u1, back, -.03, .15, BASE_TOP, 1)
        # the end doors stop square to the reveals (skirting on one side, the black bin on the other)
        r.front(u0, u1, .15, .868, -.03, hd, g=f'kitchen.nook.base.{n}', deg=95 if n == 1 else 90)
        stock(c, u0 + .05, u1 - .05, -.28, 20 + n, room=.3)
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
    g = 'kitchen.bin.black'                                   # lid lifts 65 deg on its back edge, the pedal works it
    bin_body(r, uc - .21, uc + .21, .03, .36, 0, .52, blk, .015)
    K.lining(r.sub(g + '.in').mb, uc - .183, uc + .183, -.057, -.333, .20, .52, K.col('bin_bag', '#0E0E0F', .35), open='top')
    t = r.sub(g + '.lid', 'hinge', g=g, label='Bin', **hinge(WN, uc, .022, .60, -65, 'x'))
    t.box(uc - .22, uc + .22, .022, .368, .50, .60, blk, bev=.02)                   # lid
    t.box(uc - .195, uc + .195, .04, .35, .60, .618, blk, bev=.008)
    t.box(uc - .045, uc + .045, .366, .371, .555, .59, 'silver_satin', bev=.001)    # silver latch plate on the lid front
    r.sub(g + '.pedal', 'trigger', g=g, label='Bin').box(uc - .09, uc + .09, .35, .42, .012, .03, satin(), bev=.004,
                                                         grain=0)                    # wide steel pedal
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


# ----------------------------------------------------------------------------- interlocks
# Pairs of groups whose open poses cross (build/ixfix/kitchen/check.py, [both open]); each needs the other shut.
EXCL = (
    ('kitchen.dishwasher', 'kitchen.base.hob.drawer.2'), ('kitchen.dishwasher', 'kitchen.base.hob.h5'),
    ('kitchen.oven.mid', 'kitchen.base.sink.s3'), ('kitchen.oven.low', 'kitchen.base.sink.s3'),
    ('kitchen.oven.mid', 'kitchen.base.sink.s2b'),
    ('kitchen.tower.top', 'kitchen.wall.t3'), ('kitchen.wall.corner', 'kitchen.wall.t5'),
)


def interlock():
    """Write `excl` = the groups that must be shut before this one opens into every tag of a group in EXCL.
    ponytail: patched into the json after the build, because lib.interact.tag rejects keys it does not list;
    pass excl= to IX.tag instead once lib/interact.py OPTIONAL has it."""
    both, seen = EXCL + tuple((b, a) for a, b in EXCL), set()
    for o in bpy.data.objects:
        if 'ix' in o.keys():
            d = json.loads(o['ix'])
            seen.add(d['g'])
            ex = sorted(b for a, b in both if a == d['g'])
            if ex:
                o['ix'] = json.dumps(dict(d, excl=ex), separators=(',', ':'))
    missing = {a for a, b in both} - seen
    assert not missing, f'EXCL names groups that do not exist: {sorted(missing)}'


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
    interlock()

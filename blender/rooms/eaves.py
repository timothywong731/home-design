"""Eaves storage behind the Slate Room knee walls (loft_office): eaves_front (low void along the street side with the
A-shaped tunnel under the bay gable) and eaves_rear (behind the rear knee wall, east of the stair dormer, with a step
in its floor). Visitors open a hatch, duck through and move about inside (owner, round 3).
Spec: spec/rooms/eaves.md + spec/phase3/eaves_loft.md + spec/phase3/briefs/eaves.md. Footage v12 (21 Nov, silent):
front tunnel f19-36, low voids f23-59, rear void f76-118; v5 f_0260-0346 (narrated).

    "$B" -b --factory-startup --python blender/build.py -- --levels 2,X --only shell,envelope,eaves_front,eaves_rear \
         --preview eaves_front,eaves_rear --res 540x960 --samples 64 --tag r3eaves [--pose 1 --tag r3eaves1]

The shell gives walls and floors only (under_roof rooms get no ceiling: the envelope's black roof underside shows), so
the white plasterboard linings are built here as '<room>.ceiling' (the dollhouse lifts '.ceiling' off), exactly at
ctx.ceil_z = min(ceilingZ, roof + ceiling.offset, ceiling.planes): the walk headroom, the plan and the model agree
(asserted on a grid below); lib.envelope keeps the slab underside 1 cm above (front 1.00 at the knee-wall back).
Front lining: main slope + the tunnel (strip 0.40 at 1.70, linings 50 deg), the valley cuts closed by a fascia band
whose top meets the crease corner (0.20 on the spec lining, v12 f25), and above the knee wall's vertical part (1.20) a
ramp rising north to a dark slot under the strip (eaves_loft 2.5, -06). Rear lining: 35 deg from 1.16 at the knee-wall
back, landing on a 0.13 upstand board on the platform and on the lower floor beyond the step.
"""
import os
import sys
from math import radians, tan

import bmesh
from mathutils import Vector

from lib import lighting, materials as M, props as P, shell
from lib.ctx import poly_contains

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:                       # build.py loads this file by path: make the helpers importable
    sys.path.insert(0, _HERE)
import eaves_parts as EP

FRONT, REAR = 'eaves_front', 'eaves_rear'
WHITE = '#EFEEEA'                 # eaves.md 4: plasterboard, matt white emulsion (v12 linings #D6D4C8 lit)
EDGE = '#E2E0D9'                  # cut plasterboard edge round the hatch holes (a shade darker: filler, shadow)
SLOT = '#1D1C1A'                  # the dark slot where the ramp meets the strip
CREASE = 1.20                     # knee-wall back vertical to here above the east hatch (eaves_loft-06); the valley
                                  # fascia band's top meets it at the knee wall (f25: the crease runs into the band's top
                                  # corner, the band end stands over the switch at x ~1.84)
RAMP_DEG = 35.0                   # ramp above it (verifier: slot at 1.65-1.70 for a 30-40 deg ramp; the roof is 35)
SLOT_H, SLOT_D = 0.03, 0.07       # slot about 0.4 x 0.03 (eaves_loft 2.5)
STRIP_HALF = 0.20                 # flat strip 0.40 wide (eaves_loft-06)
UPSTAND = 0.13                    # white board under the rear lining at the platform's north edge (eaves_loft 2.6)
ROUGH = 0.055                     # plasterboard cut back round the hatch holes: 1.16 for a 1.05 hole (eaves_loft 2.1)
SPILL_W = 4.0                     # W per metre of the hidden panels in the hatches (room light, see _front)
LANE = 0.55                       # owner: lane kept free along the front knee wall (y > yk - LANE) and from each hatch

F_Z = 6.49                        # loft floor, for the camera list only (the code reads ctx.floor_z)
CAMERAS = [   # world coords; refs are v12 frames (v5 for the room side). The voids have their own light: lit in both poses.
    dict(name='tunnel', pos=(2.48, 2.25, F_Z + 1.40), look=(2.48, 0.14, F_Z + 0.85), fov_deg=100, ref='v12_f_0021'),
    dict(name='tunnel_back', pos=(2.56, 1.20, F_Z + 1.42), look=(2.48, 2.44, F_Z + 1.05), fov_deg=100, ref='v12_f_0025'),
    dict(name='crouch', pos=(2.30, 1.70, F_Z + 0.75), look=(2.48, 2.44, F_Z + 1.25), fov_deg=100, ref='v12_f_0029'),
    dict(name='switch', pos=(2.45, 2.20, F_Z + 0.80), look=(0.40, 2.05, F_Z + 0.45), fov_deg=100, ref='v12_f_0035'),
    dict(name='east', pos=(2.55, 1.85, F_Z + 0.95), look=(4.30, 2.05, F_Z + 0.40), fov_deg=100, ref='v12_f_0023'),
    dict(name='west', pos=(0.20, 2.32, F_Z + 0.70), look=(2.40, 1.75, F_Z + 0.55), fov_deg=100, ref='v12_f_0057'),
    dict(name='party', pos=(0.45, 2.32, F_Z + 0.72), look=(-0.65, 1.55, F_Z + 0.35), fov_deg=100, ref='v12_f_0053'),
    dict(name='office_e', pos=(2.62, 3.45, F_Z + 1.25), look=(2.48, 1.20, F_Z + 0.65), fov_deg=100, ref='v12_f_0013'),
    dict(name='office_w', pos=(0.30, 3.45, F_Z + 1.25), look=(0.20, 1.40, F_Z + 0.50), fov_deg=100, ref='v12_f_0049'),
    dict(name='r_in', pos=(1.85, 6.85, F_Z + 0.85), look=(3.10, 7.95, F_Z + 0.05), fov_deg=100, ref='v12_f_0085'),
    dict(name='r_light', pos=(2.62, 7.20, F_Z + 0.55), look=(2.72, 6.69, F_Z + 0.95), fov_deg=100, ref='v12_f_0089'),
    dict(name='r_step', pos=(1.85, 7.10, F_Z + 0.80), look=(2.40, 8.20, F_Z - 0.05), fov_deg=100, ref='v12_f_0097'),
    dict(name='r_east', pos=(2.20, 6.95, F_Z + 0.75), look=(4.30, 7.65, F_Z + 0.20), fov_deg=100, ref='v12_f_0101'),
    dict(name='r_west', pos=(2.65, 6.92, F_Z + 0.75), look=(1.35, 7.85, F_Z + 0.15), fov_deg=100, ref='v12_f_0103'),
    dict(name='r_office', pos=(1.95, 5.60, F_Z + 1.30), look=(2.10, 7.60, F_Z + 0.45), fov_deg=100, ref='v12_f_0079'),
]


def _plane(ctx, pid):
    z = next(p for p in ctx.spec['roof']['planes'] if p['id'] == pid)['z']
    assert not z['cx'], pid                         # both main planes slope along y only
    return lambda y: z['c0'] + z['cy'] * y


def _slab_under(ctx, room, x, y):
    """Underside of the roof slab lib.envelope builds over (x, y): roof_under, lifted 1 cm over the lining in the room."""
    ru = ctx.roof_under(x, y)
    if ru is not None and poly_contains(x, y, ctx.room_poly(room), 1e-4):
        ru = max(ru, ctx.ceil_z(room, x, y) + 0.01)
    return ru


def _agree(ctx, room, lining, step=0.05):
    """The lining built here (lining(x, y) = world z, None where it is not the ceiling) against ctx.ceil_z on a grid
    inside the room, 2 cm clear of its edges and of the valley lines (where the band stands): within 3 mm."""
    poly = ctx.room_poly(room)
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    n, worst = 0, (0.0, ())
    for i in range(int((max(xs) - min(xs)) / step)):
        for j in range(int((max(ys) - min(ys)) / step)):
            x, y = min(xs) + step * (i + 0.5), min(ys) + step * (j + 0.5)
            near = [lining(x + dx, y + dy) for dx in (-0.02, 0, 0.02) for dy in (-0.02, 0, 0.02)]
            if not ctx.room_at(x, y, '2') == room or None in near or max(near) - min(near) > 0.06:
                continue
            d = abs(lining(x, y) - ctx.ceil_z(room, x, y))
            n, worst = n + 1, max(worst, (d, (round(x, 3), round(y, 3))))
    assert n > 50 and worst[0] < 0.003, (f'{room} lining is not ctx.ceil_z', n, worst)
    print(f'[eaves] {room} lining = ctx.ceil_z at {n} points (worst {worst[0] * 1000:.1f} mm)')


def _patch_wall_tops(ctx, room, name, lining, skip):
    """Where the shell clips a wall below the lining (it takes the bay-gable plane over the tunnel feet, and caps the
    end walls at the knee-wall corner), close the slot between the wall's top edge and the lining with a white
    patch 1 mm proud of the wall. lining(x, y) = world z of the lining over that point, None = not a lining here;
    skip(face centre, normal) -> True for faces to leave alone."""
    ob = shell.surface(room, 'walls')
    if ob is None:
        return
    mw = ob.matrix_world
    faces = []
    for p in ob.data.polygons:
        n = (mw.to_3x3() @ p.normal).normalized()
        if abs(n.z) > 0.1:
            continue
        c = mw @ p.center
        if skip(c, n):
            continue
        vs = [mw @ ob.data.vertices[i].co for i in p.vertices]
        u = Vector((-n.y, n.x, 0))                                   # horizontal axis in the face
        for a, b in zip(vs, vs[1:] + vs[:1]):
            ua, ub, uc = a.dot(u), b.dot(u), c.dot(u)
            if abs(ua - ub) < 1e-4:
                continue                                             # vertical edge
            k = (uc - ua) / (ub - ua)
            if a.z + (b.z - a.z) * k <= c.z:
                continue                                             # bottom edge
            za, zb = lining(a.x, a.y), lining(b.x, b.y)
            if za is None and zb is None:
                continue
            if za is None or zb is None:                             # keep the part over the lining's area
                good, bad = (a, b) if za is not None else (b, a)
                for _ in range(24):
                    m = good.lerp(bad, 0.5)
                    good, bad = (m, bad) if lining(m.x, m.y) is not None else (good, m)
                a, b = (good, b) if za is None else (a, good)
                za, zb = lining(a.x, a.y), lining(b.x, b.y)
            da, db = za - a.z, zb - b.z                              # gap above the edge at both ends
            if da < 0.002 and db < 0.002:
                continue
            if da < 0 or db < 0:                                     # the edge crosses the lining: keep the gap part
                t = da / (da - db)
                m = a.lerp(b, t)
                m.z = lining(m.x, m.y)
                a, b, za, zb = (m, b, m.z, zb) if da < 0 else (a, m, za, m.z)
            off = n * 0.001
            faces.append(([a + off, b + off, Vector((b.x, b.y, zb)) + off, Vector((a.x, a.y, za)) + off],
                          tuple(c + n), WHITE))
    if faces:
        ctx.add(shell.faces_object(name, faces), room, 'trim')


def _open_above(ctx, room, y, x0, x1, zc):
    """Delete the part of the shell's wall face at y (normal -Y: the knee-wall back seen from the void) above world
    z zc for x0 < x < x1: the shell carries the knee-wall back up to the tunnel lining, the footage shows it stopping
    at the crease with the ramp rising behind it (eaves_loft 2.5; README shell: 'not modelled')."""
    ob = shell.surface(room, 'walls')
    if ob is None:
        return 0
    mwi = ob.matrix_world.inverted()

    def picked(f):
        c = ob.matrix_world @ f.calc_center_median()
        n = ob.matrix_world.to_3x3() @ f.normal
        return n.y < -0.999 and abs(c.y - y) < 2e-3 and x0 < c.x < x1

    bm = bmesh.new()
    bm.from_mesh(ob.data)
    sel = [f for f in bm.faces if picked(f)]
    geom = sel + list({e for f in sel for e in f.edges}) + list({v for f in sel for v in f.verts})
    co = mwi @ Vector((0, 0, zc))
    bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-6, plane_co=co, plane_no=(0, 0, 1))
    dead = [f for f in bm.faces if picked(f) and (ob.matrix_world @ f.calc_center_median()).z > zc + 1e-5]
    bmesh.ops.delete(bm, geom=dead, context='FACES')
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()
    return len(dead)


def _hatch_edge(ctx, room, oid, ceiling, name, rough=ROUGH):
    """Rough-cut plasterboard round a hatch hole on the void side (eaves_loft 2.1: board cut 1.16 wide round a frame
    of about 1.0): a slightly jagged white margin 2 mm proud of the knee-wall back, on the sides and the head."""
    fr = ctx.opening_frame(oid)
    n = Vector((fr['normal'][0], fr['normal'][1], 0.0)) * (1 if fr['room_pos'] == room else -1)   # into the void
    face = fr['face_pos'] if fr['room_pos'] == room else fr['face_neg']
    a = Vector((fr['along'][0], fr['along'][1]))
    c = Vector((fr['center'][0], fr['center'][1])) + n.xy * (abs(face) + 0.002)
    z0, z1, hw = fr['z0'] + fr['sill'], fr['z0'] + fr['top'], fr['width'] / 2
    zt = min(z1 + rough, ceiling - 0.004)
    jag = [0.0, 0.006, -0.004, 0.005, -0.003, 0.004, -0.005, 0.003]          # deterministic ragged cut

    def P3(u, z):
        q = c + a.xy * u
        return Vector((q.x, q.y, z))

    faces, j = [], 0
    zj = z1 if zt > z1 + 0.01 else zt                     # jambs stop under the head: overlapping coplanar faces bake black
    for s in (-1, 1):                                                          # jambs: hole edge out to ~rough
        zs = [z0 + (zj - z0) * i / 6 for i in range(7)]
        for za, zb in zip(zs, zs[1:]):
            ua, ub = s * (hw + rough + jag[j % 8]), s * (hw + rough + jag[(j + 1) % 8])
            j += 1
            faces.append(([P3(s * hw, za), P3(s * hw, zb), P3(ub, zb), P3(ua, za)], tuple(P3(0, z0) + n * 1.0), EDGE))
    if zt > z1 + 0.01:                                                         # head
        us = [-(hw + rough) + 2 * (hw + rough) * i / 8 for i in range(9)]
        for i, (ua, ub) in enumerate(zip(us, us[1:])):
            ta, tb = zt + 0.6 * jag[i % 8], zt + 0.6 * jag[(i + 1) % 8]
            faces.append(([P3(ua, z1), P3(ub, z1), P3(ub, min(tb, ceiling - 0.003)), P3(ua, min(ta, ceiling - 0.003))],
                          tuple(P3(0, z1) + n * 1.0), EDGE))
    ctx.add(shell.faces_object(name, faces), room, 'trim')


# ------------------------------------------------------------------------------------------------------------ front
def _front(ctx):
    F = ctx.floor_z(FRONT)
    (xw, yf), (bw, _), (_, yg), (be, _), _, (xe, _), (_, yk), _ = ctx.room_poly(FRONT)   # house.json order
    gable = ctx.spec['roof']['gable']
    ax, k = gable['ridge'][0][0], tan(radians(gable['pitchDeg']))             # tunnel axis 2.48, lining 50 deg
    sz = ctx.feature('eaves_bay_tunnel')['z'][1] - F                           # strip 1.70 above the floor
    hh = STRIP_HALF + sz / k                                                   # lining foot half width (1.63)
    T = lambda x: min(sz, k * (hh - abs(x - ax)))                              # tunnel lining height
    surf = _plane(ctx, 'main_front')
    spec_off = ctx.rooms[FRONT]['ceiling']['offset']
    band = CREASE - (surf(yk) + spec_off - F)                                 # valley band height on the spec lining
    off = spec_off                                                             # the lining is ctx.ceil_z (see _agree)
    Mz = lambda y: surf(y) + off - F                                           # main lining height (spec: 1.00 at yk)
    Dz = lambda y: surf(y) + spec_off - F + band                               # top of the valley band (CREASE at yk)
    hv = lambda y: hh - Dz(y) / k                                              # band half distance from the axis
    print(f'[eaves] front lining offset {off:+.3f} (spec {spec_off:+.3f}): {Mz(yk):.3f} at the knee-wall back, '
          f'band to {Dz(yk):.3f}, valley at x {ax - hv(yk):.3f} / {ax + hv(yk):.3f}')
    V = lambda x, y, z: (x, y, F + z)
    below = lambda y: (ax, y, F + 0.05)

    # --- ramp above the knee wall's vertical part, rising north to the slot under the strip
    tr = tan(radians(RAMP_DEG))
    ys = yk + (sz - SLOT_H - CREASE) / tr
    ys2 = ys + SLOT_D
    hr = lambda z: hh - z / k                                                  # lining half width at height z

    faces = [([V(xw, yf, Mz(yf)), V(ax - hv(yf), yf, Mz(yf)), V(ax - hv(yk), yk, Mz(yk)), V(xw, yk, Mz(yk))],
              below((yf + yk) / 2), WHITE),                                    # main slope, west stretch
             ([V(ax + hv(yf), yf, Mz(yf)), V(xe, yf, Mz(yf)), V(xe, yk, Mz(yk)), V(ax + hv(yk), yk, Mz(yk))],
              below((yf + yk) / 2), WHITE),                                    # main slope, east stretch
             ([V(ax - STRIP_HALF, yg - .003, sz), V(ax + STRIP_HALF, yg - .003, sz), V(ax + STRIP_HALF, ys2, sz),
               V(ax - STRIP_HALF, ys2, sz)], below(1.0), WHITE)]               # flat strip, gable end to the slot
    for s, foot in ((-1, bw), (1, be)):                                        # west / east halves of the tunnel
        e, v0, v1 = ax + s * STRIP_HALF, ax + s * hv(yf), ax + s * hv(yk)
        faces += [
            ([V(foot, yg - .003, T(foot)), V(foot, yf, T(foot)), V(e, yf, sz), V(e, yg - .003, sz)], below(0.5), WHITE),
            ([V(v0, yf, Dz(yf)), V(v1, yk, Dz(yk)), V(e, yk, sz), V(e, yf, sz)], below(1.7), WHITE),
            ([V(v0, yf, Mz(yf)), V(v1, yk, Mz(yk)), V(v1, yk, Dz(yk)), V(v0, yf, Dz(yf))], (ax, 1.7, F + .5), WHITE),
            ([V(foot, yf, Mz(yf)), V(v0, yf, Mz(yf)), V(v0, yf, Dz(yf)), V(foot, yf, T(foot))], (ax, yf - .4, F), WHITE),
            ([V(ax + s * hr(CREASE), yk, CREASE), V(ax + s * hr(sz - SLOT_H), ys, sz - SLOT_H),
              V(ax + s * hr(sz - SLOT_H), ys2, sz - SLOT_H), V(e, ys2, sz), V(e, yk, sz)], (ax, (yk + ys) / 2, F + CREASE), WHITE)]
    faces += [([V(ax - hr(CREASE), yk, CREASE), V(ax + hr(CREASE), yk, CREASE), V(ax + hr(sz - SLOT_H), ys, sz - SLOT_H),
                V(ax - hr(sz - SLOT_H), ys, sz - SLOT_H)], (ax, yk - 1.0, F + 1.9), WHITE),          # the ramp
              ([V(ax - hr(sz - SLOT_H), ys, sz - SLOT_H), V(ax + hr(sz - SLOT_H), ys, sz - SLOT_H),
                V(ax + hr(sz - SLOT_H), ys2, sz - SLOT_H), V(ax - hr(sz - SLOT_H), ys2, sz - SLOT_H)], (ax, ys, F + 2.5), SLOT),
              ([V(ax - hr(sz - SLOT_H), ys2, sz - SLOT_H), V(ax + hr(sz - SLOT_H), ys2, sz - SLOT_H), V(ax + STRIP_HALF, ys2, sz),
                V(ax - STRIP_HALF, ys2, sz)], (ax, yk, F + sz), SLOT)]
    for f, _, _ in faces:                                                      # the check: nothing pokes into the slab
        for x, y, z in f:
            ru = _slab_under(ctx, FRONT, x, y)
            assert ru is None or z <= ru + 0.002, ('eaves_front lining above the roof slab', x, y, z, ru)

    def model(x, y):                                                           # the lining just built, world z
        if y > yk:
            return None
        d = abs(x - ax)
        if y < yf or d < hv(y):                                                # tunnel: strip, then the 50-deg linings
            return F + T(x)
        return F + Mz(y)
    _agree(ctx, FRONT, model)
    ctx.add(shell.faces_object(f'{FRONT}.ceiling', faces), FRONT, 'trim')
    batten = EP.slab(f'{FRONT}.slot_batten', 2 * STRIP_HALF - .03, .028, .024, M.solid('batten_sw', '#5C4B37', 0.8))
    batten.location = (ax, ys + .035, F + sz - SLOT_H)
    ctx.add(batten, FRONT, 'trim')

    # the shell carries the knee-wall back up to the tunnel lining: open it above the crease, where the ramp is
    cut = _open_above(ctx, FRONT, yk, ax - 0.80, ax + 0.80, F + CREASE)
    print(f'[eaves] knee-wall back above the crease: {cut} shell faces removed')

    def lining(x, y):                                                          # the main slope over the low voids
        return F + Mz(y) if (x < ax - hv(yk) - 1e-3 or x > ax + hv(yk) + 1e-3) else None

    holes = []
    for oid in ('h_eaves_front_w', 'h_eaves_front_e'):
        fr = ctx.opening_frame(oid)
        holes.append((fr['center'][0] - fr['width'] / 2, fr['center'][0] + fr['width'] / 2, fr['z0'] + fr['top']))

    def keep(c, n):                                                            # knee-wall back and the two end walls
        knee = n.y < -0.99 and abs(c.y - yk) < 2e-3
        end = abs(n.x) > 0.99 and (abs(c.x - xw) < 2e-3 or abs(c.x - xe) < 2e-3)
        under_hole = knee and any(a - 1e-3 < c.x < b + 1e-3 and c.z < top for a, b, top in holes)
        return (knee or end) and not under_hole

    _patch_wall_tops(ctx, FRONT, f'{FRONT}.kneecap', lining, lambda c, n: not keep(c, n))
    for oid in ('h_eaves_front_w', 'h_eaves_front_e'):
        hx = ctx.openings[oid]['center'][0]
        hw = ctx.openings[oid]['width'] / 2
        if abs(hx - ax) <= hv(yk):                                             # east hatch: between the valley bands
            _hatch_edge(ctx, FRONT, oid, F + CREASE, f'{FRONT}.{oid}.edge', rough=min(ROUGH, hv(yk) - hw - 0.008))
            continue
        _hatch_edge(ctx, FRONT, oid, F + Mz(yk), f'{FRONT}.{oid}.edge')         # west hatch: under the main lining
        fr = ctx.opening_frame(oid)
        assert F + Mz(yk) > fr['z0'] + fr['top'] + 0.05, ('hatch head above the lining', oid)   # 0.93 under 1.00

    # --- switch and double socket on the knee-wall back just west of the east hatch (v12 f25 / f26 / f36: 0.17-0.21
    # west of the hole, switch centre 0.79, socket 0.37; x measured on the 86 mm plates, see spec/rooms/eaves_front.md)
    hole_w = ctx.openings['h_eaves_front_e']['center'][0] - ctx.openings['h_eaves_front_e']['width'] / 2
    xp = hole_w - 0.115
    EP.switch(ctx, FRONT, xp, yk, F + 0.79, (0, -1))
    EP.socket(ctx, FRONT, xp + 0.02, yk, F + 0.37, (0, -1))
    strip = EP.slab(f'{FRONT}.cover_strip', .032, .009, .36, M.paint('#F1F0EC', 0.6))   # white cover strip (f26, f36)
    strip.location = (xp - 0.125, yk - .0045, F + .06)
    ctx.add(strip, FRONT, 'trim')

    # --- "one light": round opal bulkhead with a deep rim on the strip (f20), switched from the rocker
    EP.bulkhead(ctx, FRONT, f'{FRONT}.bulkhead', (ax, 1.05, F + sz), (0, 0, -1), 0.28, 30,   # f20: over the middle
                reach=2.0)                         # 1.9 m in from the Slate Room: answers through the open east hatch

    # ponytail: the west stretch gets only spill ("it's a bit dark") and bakes near black with its hatch shut, yet in
    # the footage the open hatch lets the room light in. A dim unseen panel in the hatch plane, facing into the void,
    # stands in for that light (a bulb left a hot spot on the lining); a second, hatch-open bake would be the real answer.
    west = lighting.strip(ctx, FRONT, (-0.30, yk - 0.04, F + 0.48), (0.55, yk - 0.04, F + 0.48), watts_per_m=SPILL_W,
                          kelvin=3000, width=0.55, direction=(0, -1, 0), name=f'{FRONT}.spill')
    west.visible_camera = west.visible_glossy = False
    # the same for the east stretch, which the valley band shades from the tunnel bulkhead (it baked near black at
    # its end once the lane along the knee wall was cleared): light from the east hatch thrown east under the band
    hx_e = ctx.openings['h_eaves_front_e']['center'][0] + ctx.openings['h_eaves_front_e']['width'] / 2
    east = lighting.strip(ctx, FRONT, (hx_e - 0.03, yk - 0.10, F + 0.15), (hx_e - 0.03, yk - 0.10, F + 0.70),
                          watts_per_m=SPILL_W, kelvin=3000, width=0.30, direction=(1.0, -0.4, -0.1),
                          name=f'{FRONT}.spill_e')
    east.visible_camera = east.visible_glossy = False

    # --- stored things, only where v12 shows them and clear of the lanes: east hatch -> tunnel -> gable end down the
    # middle (x 2.17..2.80 free at the gable end, wider elsewhere), both hatches -> along the knee wall to the party
    # wall and to the east wall (y 1.89..2.44 free)
    def put(ob, x, y, z=0.0, rot=0.0, sym='box'):
        ob.location, ob.rotation_euler = (x, y, F + z), (0.0, 0.0, radians(rot))
        ctx.add(ob, FRONT, 'decor', plan_sym=sym, lm='static')   # void rooms get no probe: probe-lit, they would take the room below's
        return ob

    # gable end, east side (left, looking south in f19-21): two lidded plastic boxes stacked; west of the middle the
    # pale carton of f21 (the soft vacuum bags on the west side are left out)
    sb = EP.storage_box(f'{FRONT}.plastic_box.0', 0.46, 0.36, 0.24)
    put(sb, 3.18, yg + 0.22)
    sb2 = EP.storage_box(f'{FRONT}.plastic_box.1', 0.46, 0.36, 0.24)
    sb2.location, sb2.rotation_euler = (3.17, yg + 0.215, F + 0.24), (0, 0, radians(3))
    ctx.add(sb2, FRONT, 'decor', lm='static')
    put(EP.carton(f'{FRONT}.carton.0', 0.38, 0.34, 0.36), 1.98, yg + 0.21, rot=-4)
    # the silver cabin case standing on its wheels in the tunnel's east side (f25 foreground, f29), and two black cases
    # lying on their backs under the slope in the east stretch, as f23 / f31 show black cases there. f25 / f29 also
    # show black cases standing at the knee wall east of the hatch: that is the only walkable strip of the east stretch
    # (headroom), so the owner's lane wins and they lie south of it. Wheels to the east, the east wall first.
    put(EP.suitcase(f'{FRONT}.suitcase.0', 0.40, 0.24, 0.58, '#B7B1A2', metallic=0.6), 2.92, 1.50, z=0.045, rot=90)
    x_e = xe - 0.01
    for i, (w, d, h) in ((2, (0.44, 0.26, 0.60)), (1, (0.42, 0.25, 0.55))):
        wheel = 0.045
        yc = yk - LANE - w / 2 - 0.005                                         # north side (zip line) off the lane
        top = d + 0.0075                                                       # shell + ribs, lying on its back
        assert Mz(yc - w / 2) > top + 0.01, ('lying case under the lining', i, Mz(yc - w / 2), top)
        case = EP.suitcase(f'{FRONT}.suitcase.{i}', w, d, h, '#26272A')
        case.location = (x_e - wheel, yc, F + d / 2 + 0.004)                    # local +z (handle end) turns to -x
        case.rotation_euler = (radians(-90), 0.0, radians(90))
        ctx.add(case, FRONT, 'decor', plan_sym='box', lm='static')
        x_e -= h + 0.028 + 0.02                                                 # handle end + a gap
    # west end by the party wall: one closed carton under the slope, clear of the lane along the knee wall (f51-53
    # shows the end piled with soft bags, left out)
    put(EP.carton(f'{FRONT}.carton.1', 0.42, 0.34, 0.28), -0.36, 1.66, rot=-6)


# ------------------------------------------------------------------------------------------------------------- rear
def _rear(ctx):
    F = ctx.floor_z(REAR)
    (x0, y0), (x1, _), (_, y1), _ = ctx.room_poly(REAR)
    step = ctx.feature('eaves_rear_step')
    xs, lo = step['line'][0][0], step['zLow']
    surf = _plane(ctx, 'main_rear')
    off = ctx.rooms[REAR]['ceiling']['offset']                                 # -0.31: 0.01 under the 0.30 slab
    Lz = lambda y: surf(y) + off                                               # world z of the lining
    cy = surf(1.0) - surf(0.0)
    at = lambda z: (z - surf(0.0) - off) / cy                                  # y where the lining is at world z
    y_up, y_lo = at(F + UPSTAND), at(lo)
    print(f'[eaves] rear lining offset {off:+.3f}: {Lz(y0) - F:.3f} at the knee-wall back, upstand at y {y_up:.3f}, '
          f'lands on the lower floor at y {y_lo:.3f}')
    assert y_lo < y1, 'the rear lining must land inside the polygon'
    quad = [(x0, y0, Lz(y0)), (x1, y0, Lz(y0)), (x1, y_lo, lo), (xs, y_lo, lo), (xs, y_up, F + UPSTAND),
            (x0, y_up, F + UPSTAND)]
    for x, y, z in quad:
        ru = _slab_under(ctx, REAR, x, y)
        assert ru is None or z <= ru + 0.002, ('eaves_rear lining above the roof slab', x, y, z, ru)
    _agree(ctx, REAR, lambda x, y: Lz(y) if Lz(y) > ctx.floor_z(REAR, x, y) + UPSTAND else None)
    ctx.add(shell.faces_object(f'{REAR}.ceiling', [(quad, ((x0 + x1) / 2, (y0 + y1) / 2, F), WHITE)]), REAR, 'trim')

    # --- the platform's north edge: a white upstand board 0.13 high that the lining lands on (v12 f83-85, f107-110).
    # At the step end a narrow white return board stands on the LOWER floor against the riser end, from the
    # upstand's top corner down past the riser; its north edge rakes down steeper than the lining, leaving a dark
    # triangular gap between it and the lining (f95, f97)
    ctx.add(shell.box(f'{REAR}.upstand', x0, xs, y_up, y_up + 0.018, F, F + UPSTAND, '#F1F0EC'), REAR, 'trim')
    yt, yb = y_up + 0.02, y_up + 0.20                                          # board top 20 mm, foot 0.20 (f97)
    prof = [(y_up, lo), (yb, lo), (yt, Lz(yt) - 0.003), (y_up, F + UPSTAND - 0.002)]
    xa, xb = xs + 0.001, xs + 0.019
    pa, pb = [(xa, y, z) for y, z in prof], [(xb, y, z) for y, z in prof]
    qy, qz = sum(y for y, _ in prof) / 4, sum(z for _, z in prof) / 4
    faces = [(pb, (xs + 1, qy, qz), '#F1F0EC'), (pa, (xs - 1, qy, qz), '#F1F0EC')]
    for k in (1, 2, 3):                                                        # raking edge, top, south end
        my, mz = (prof[k][0] + prof[(k + 1) % 4][0]) / 2, (prof[k][1] + prof[(k + 1) % 4][1]) / 2
        faces.append(([pa[k], pa[(k + 1) % 4], pb[(k + 1) % 4], pb[k]], (xs, 11 * my - 10 * qy, 11 * mz - 10 * qz), '#F1F0EC'))
    faces.append(([(xs + 0.004, yt, Lz(yt) - 0.004), (xs + 0.004, y_lo - 0.004, lo + 0.001), (xs + 0.004, yb, lo + 0.001)],
                  (xs + 1, (yt + y_lo) / 2, lo), SLOT))                         # the gap: into the dark over the platform
    ctx.add(shell.faces_object(f'{REAR}.upstand_return', faces), REAR, 'trim')

    # --- "there's a step here": two aluminium angle nosings side by side on the platform edge, a dark grey anti-slip
    # insert in each (30 mm; 78 mm in all), aluminium leg down the riser (f85-98). Up to the upstand.
    alu, ins = M.solid('nosing_alu', '#C4C6C8', 0.42, 0.35), M.solid('nosing_insert', '#3A3C3F', 0.8)  # mill finish (f85)
    L, yc = y_up - y0, (y0 + y_up) / 2
    parts = ((xs - .078, xs + .003, F, F + .003, alu),                         # top plates
             (xs, xs + .003, F - .036, F, alu),                                # leg on the riser
             (xs - .073, xs - .043, F + .003, F + .0045, ins),
             (xs - .035, xs - .005, F + .003, F + .0045, ins),
             (xs - .0405, xs - .0375, F + .003, F + .0035, M.solid('nosing_gap', '#2A2A2A', 0.6)))
    for i, (xa, xb, za, zb, mat) in enumerate(parts):
        bar = P.box(xb - xa, L, zb - za, mat, name=f'{REAR}.nosing.{i}')
        bar.location = ((xa + xb) / 2, yc, za)
        ctx.add(bar, REAR, 'trim')

    _hatch_edge(ctx, REAR, 'h_eaves_rear', Lz(y0), f'{REAR}.h_eaves_rear.edge')

    # --- "lights on, switch": rocker 0.13 east of the hatch jamb, small bulkhead beside it (f89, f111-116)
    hole_e = ctx.openings['h_eaves_rear']['center'][0] + ctx.openings['h_eaves_rear']['width'] / 2
    EP.switch(ctx, REAR, hole_e + 0.13, y0, F + 1.00, (0, 1))
    EP.bulkhead(ctx, REAR, f'{REAR}.bulkhead', (hole_e + 0.38, y0, F + 1.01), (0, 1, 0), 0.17, 22)
    # ponytail: room light through the open hatch, as at the front (_front, SPILL_W): the open carton by the step
    # stands between the bulkhead and the step-end corner, which baked near black with the bulkhead alone; the
    # footage (f95-98, hatch open, room lit) shows that corner evenly lit. Unseen panel in the hatch, facing in.
    hole_w = hole_e - ctx.openings['h_eaves_rear']['width']
    spill = lighting.strip(ctx, REAR, (hole_w + 0.15, y0 + 0.04, F + 0.55), (hole_e - 0.15, y0 + 0.04, F + 0.55),
                           watts_per_m=SPILL_W, kelvin=3000, width=0.55, direction=(0, 1, 0), name=f'{REAR}.spill')
    spill.visible_camera = spill.visible_glossy = False

    # --- stored things (f86-101, f103-110): the open carton by the step, flattened cartons leaning on the east wall,
    # two small boxes and a long one at the platform's north end. The lane along the knee wall (y < 7.25) stays free.
    def put(ob, x, y, z, rot=0.0, sym='box'):
        ob.location, ob.rotation_euler = (x, y, z), (0, 0, radians(rot))
        ctx.add(ob, REAR, 'decor', plan_sym=sym, lm='static')
        return ob

    # the open carton stands just east of the step (f86, f90, f93: a hand's width off the nosing); 0.34 off here so
    # its west flap clears the line from the bulkhead (x 2.83 on the knee wall) to the step-end corner, which baked
    # near black in its shadow (f95-98 show that corner evenly lit)
    put(EP.open_carton(f'{REAR}.carton_open', 0.42, 0.38, 0.36, (25, 30, 65, 20)), xs + 0.55, 7.52, lo, rot=2)
    sheets = [(0.62, 0.42, -0.02), (0.55, 0.41, 0.03), (0.58, 0.40, -0.05), (0.52, 0.39, 0.04), (0.50, 0.37, 0.06),
              (0.56, 0.36, -0.01), (0.46, 0.33, 0.12), (0.40, 0.28, 0.20)]   # (width along the wall, height, dy)
    fc = EP.flat_cartons(f'{REAR}.cartons_flat', sheets, lean=9.0, gap=0.011)  # a bundle about 0.1 thick (f101)
    put(fc, x1 - 0.002, 7.59, lo)
    for i, (xx, yy, zz, w, d, h, r) in enumerate(((1.50, 7.98, F, .20, .15, .10, 4), (1.51, 7.975, F + .10, .19, .14, .09, -6),
                                                  (1.86, 8.02, F, .55, .13, .12, 2))):
        b = EP.carton(f'{REAR}.box.{i}', w, d, h)
        if i == 1:
            b.location, b.rotation_euler = (xx, yy, zz), (0, 0, radians(r))
            ctx.add(b, REAR, 'decor', lm='static')
        else:
            put(b, xx, yy, zz, rot=r)


def build(ctx):
    _front(ctx)
    _rear(ctx)

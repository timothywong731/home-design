"""Architecture shell of every level, built from house.json (schema "house/2"). Contract: blender/MULTILEVEL.md section 4.

Box CSG on one non-uniform grid for the whole house (class Grid): the envelope blocks are filled as solid mass, rooms,
reveals, wells and openings are carved out of it, and the boundary faces between solid and a room void are emitted as
merged quads. Walls, floor zones, poche and unseen zones are simply what is never carved. Every face knows the room it
faces and gets that room's finish from FINISHES; faces whose other side is outside are not emitted (the envelope owns
the outside). Everything that is not axis-aligned is a small separate object: chamfer prisms, ceiling haunches, sloped
ceilings, arch infill; the flights come from lib.stairs.
"""
import math

import bmesh
import bpy
import numpy as np
from mathutils import Vector

from . import materials as M
from .ctx import plane_z, point_in_poly, poly_area, poly_contains

SLAB = 0.15          # mass carried below the lowest floor of every storey
WHITE = '#F4F2EC'    # painted joinery / reveal liners
GREY = '#8C8C8C'     # fallback for a missing material key
ARCH_PAD = 0.06      # arch holes are cut this much above the crown; the infill mesh owns that band
HEADROOM = 1.95      # flight sweeps clear this much above every tread
RISER_MAX = 0.45     # a mass face under a floor at most this far above the floor it faces is a riser (two steps)
UNDER_TREAD = 0.11   # band under a tread that is always inside the flight carcass (lib.stairs.WAIST - 0.01)
SOLID_FLIGHTS = {'stair_basement'}      # carcass = mass down to the shaft floor (walls both sides): treads + risers only
SOLID_FEATS = ('pier', 'pilaster', 'nib', 'chimney_breast', 'boxing', 'hearth')
MISSING = []         # material keys that fell back to grey (build.py counts them as errors unless --bare)

# world point that lands on UV (0, 0) of a room's floor texture (registers the tile motif to the spec)
FLOOR_ORIGIN = {'vestibule': (-0.045 - 0.165, 0.025 - 0.165, 0.0)}      # blue square centred on (-0.045, 0.025)


def _plain(wall, ceiling, joinery='#F4F3EF', **kw):
    return dict(upper=wall, lower=wall, dado=None, dado_h=0, ceiling=ceiling, joinery=joinery, **kw)


_L1 = dict(upper='#F1EEE6', lower='#C8C5BB', dado=0.975, dado_h=0.065, ceiling='#F6F5F2', joinery='#F4F3EF')
_L2 = dict(upper='#F2F0EA', lower='#C8C5BB', dado=0.99, dado_h=0.06, ceiling='#F4F3EE', joinery=WHITE)

# Per-room finishes (colours = neutral-light estimates from the surfaces section of spec/rooms/<id>.md).
#   upper/lower : wall paint above/below the dado split (same when no dado)
#   dado        : TOP of the dado rail ABOVE THE ROOM FLOOR or None; dado_h = rail height; paint splits at dado - dado_h/2
#   (skirting / dado rail / cornice PROFILES live in lib.mouldings.TRIM; its dado 'top' must equal `dado` here)
#   faces       : per-face overrides [dict(axis=0|1, at=coord, mat=spec, range=(lo,hi)?, z=(z0,z1)?)], z above the floor
#   wainscot    : (z_top above the floor, material) applied to every wall face of the room below z_top
#   features    : feature id -> material for all faces of that feature seen from this room
# A material spec is '#RRGGBB' (paint) or a lib.materials key. Rooms without an entry get DEFAULT_FINISH.
FINISHES = {
    'basement': _plain('#F3F2EE', '#F4F3F0'),
    'basement_stair': _plain('#EDE7DA', '#EDE7DA'),
    'vestibule': dict(upper='#F2F0EA', lower='#C8C5BB', dado=0.965, dado_h=0.07, ceiling='#F4F3EE', joinery=WHITE),
    # lower: hallway.md gives #B9B5A8; it rendered a khaki band ~0.6 of the upper wall where f_0770 / f_0548 show a
    # pale greige at ~0.78 (the oak floor's bounce warms it), so it is lightened and neutralised.
    'hallway': dict(upper='#F2F0EA', lower='#C8C5BB', dado=0.965, dado_h=0.07, ceiling='#F4F3EE', joinery=WHITE,
                    features={'lobby_overhead_cupboard': WHITE}),
    'stairs': dict(upper='#F2F0EA', lower='#F2F0EA', dado=None, dado_h=0.07, ceiling='#F4F3EE', joinery=WHITE),
    # living.md gives #E8D6CF / #A4685A; both rendered more saturated than every sampled frame value
    # (#DBD2CC.. / #9F6F5F..#A87C69), so they are eased toward the samples.
    'living': dict(upper='#EADFD9', lower='#EADFD9', dado=None, dado_h=0, ceiling='#F6F4EF', joinery=WHITE,
                   faces=[dict(axis=0, at=0.80, mat='#A27365')]),            # terracotta TV wall
    'kitchen': dict(upper='#F1EFE9', lower='#F1EFE9', dado=None, dado_h=0, ceiling='#F5F4F0', joinery='#F4F3EF'),
    'utility': dict(upper='#F1F0EB', lower='#F1F0EB', dado=None, dado_h=0, ceiling='#F6F5F2', joinery='#F4F3EF',
                    faces=[dict(axis=0, at=0.60, range=(11.17, 12.23), z=(0.0, 1.39), mat='marble_metro')]),
    'wc': dict(upper='#A5A5A8', lower='#A5A5A8', dado=None, dado_h=0,
               ceiling='#F6F5F2', joinery='#F4F3EF',
               wainscot=(1.20, 'marble_metro'), features={'wc_cistern_duct': 'marble_metro'}),
    'dining': dict(upper='#DFD8CB', lower='wallcovering_aubergine', dado=1.05, dado_h=0.055, ceiling='#F3F1EB', joinery='#3B2E26',
                   features={'dining_hearth': 'hearth_marble'}),
    # first floor
    'green_bedroom': _plain('#D4E0D2', '#F5F4F0', faces=[dict(axis=0, at=-0.65, mat='#3F6B5C')]),     # deep teal TV wall
    'green_bathroom': _plain('#9AA59E', '#F5F4F0', wainscot=(1.20, 'metro_carrara_100x400'),
                             features={'gbath_duct': 'metro_carrara_100x400'}),              # WC duct tiled all over
    # the quarter landing lies 0.19 below the corridor and carries the corridor's rail level on (world 4.015)
    'landing1_front': _L1, 'landing1_ql': dict(_L1, dado=1.165), 'landing1_rear': _L1,
    'stairs2': _plain('#F1EEE6', '#F6F5F2', WHITE),          # raking dado and its paint line: room module
    'yellow_room': _plain('#EEE7C6', '#F6F5F2'),
    'blue_ensuite': _plain('#B3BEC8', '#F5F4F0', wainscot=(1.20, 'marble_metro')),
    'blue_bedroom': _plain('#C9CAD4', '#F4F2EC', '#F4F3EE', faces=[dict(axis=0, at=-0.65, mat='#2B3B4C')],
                           features={'blue_breast_w': '#2B3B4C'}),                                  # navy west wall
    # second floor
    'landing2_head': _L2, 'landing2_platform': _L2,
    'loft_office': _plain('#EFEDE7', '#F2F1EC', faces=[dict(axis=0, at=4.3, mat='#3B4046')]),         # anthracite gable
    'eaves_front': _plain('#EFEEEA', '#EFEEEA'), 'eaves_rear': _plain('#EFEEEA', '#EFEEEA'),
    'purple_room': _plain('#B4AFC6', '#F4F3EE', WHITE),
    'bathroom2': _plain('#B9B7B1', '#F4F3EF', wainscot=(1.20, 'marble_metro'), features={'bath2_pipe_boxing': 'marble_metro'}),
    'study': _plain('#EEE6DC', '#F4F3EE', WHITE, faces=[dict(axis=0, at=-0.65, mat='#BC9D99')]),      # dusty rose wall
}
DEFAULT_FINISH = _plain('#F2F0EA', '#F4F3EE', WHITE)
for _f in list(FINISHES.values()) + [DEFAULT_FINISH]:
    _f.setdefault('faces', []), _f.setdefault('features', {}), _f.setdefault('wainscot', None)

_mats = {}


def finish(room):
    return FINISHES.get(room, DEFAULT_FINISH)


def split_z(room):
    """Height ABOVE THE ROOM FLOOR where lower paint changes to upper (hidden behind the dado rail), or None."""
    f = finish(room)
    return None if f['dado'] is None else round(f['dado'] - f['dado_h'] / 2, 4)


def material(spec):
    """'#RRGGBB' -> matt paint, anything else -> lib.materials key. A missing key logs a WARNING, is recorded in
    MISSING and falls back to grey paint."""
    if spec not in _mats:
        try:
            _mats[spec] = M.paint(spec) if spec.startswith('#') else M.mat(spec)
        except KeyError:
            print(f'[shell] WARNING material key {spec!r} is missing - grey paint')
            MISSING.append(spec)
            _mats[spec] = M.paint(GREY)
    return _mats[spec]


def _r(v):
    return round(float(v), 4)


class Grid:
    """Non-uniform voxel grid. solid/void hold tag indices (0 = empty / outside)."""

    def __init__(self, ops, extra=((), (), ())):
        cs = [set(extra[0]), set(extra[1]), set(extra[2])]
        for _, b, _ in ops:
            for a in range(3):
                cs[a].update((_r(b[2 * a]), _r(b[2 * a + 1])))
        self.c = [np.array(sorted({_r(v) for v in s})) for s in cs]
        n = tuple(len(c) - 1 for c in self.c)
        self.solid = np.zeros(n, np.int16)
        self.void = np.zeros(n, np.int16)
        self.tags, self._ti = [None], {None: 0}
        for kind, b, tag in ops:
            sl = self.sl(b)
            if kind == 'fill':
                self.solid[sl] = self.t(tag)
            elif kind == 'carve':
                self.solid[sl] = 0
                self.void[sl] = self.t(tag)
            else:                                   # cut: only what is solid (keeps room/reveal voids)
                sv, vv = self.solid[sl], self.void[sl]
                m = sv > 0
                vv[m], sv[m] = self.t(tag), 0

    def t(self, tag):
        if tag not in self._ti:
            self._ti[tag] = len(self.tags)
            self.tags.append(tag)
        return self._ti[tag]

    def sl(self, b):
        return tuple(slice(int(np.searchsorted(self.c[a], _r(b[2 * a]))),
                           int(np.searchsorted(self.c[a], _r(b[2 * a + 1])))) for a in range(3))

    def k_at(self, z):
        return int(np.searchsorted(self.c[2], _r(z), side='right')) - 1

    def cell(self, x, y, z):
        """Index of the cell containing a point, or None outside the grid."""
        i = tuple(int(np.searchsorted(self.c[a], v, side='right')) - 1 for a, v in enumerate((x, y, z)))
        return i if all(0 <= i[a] < self.solid.shape[a] for a in range(3)) else None


def is_solid(ctx, x, y, z):
    """True when the built grid is solid at a world point (False outside the grid or before shell.build)."""
    i = ctx.grid.cell(x, y, z) if ctx.grid is not None else None
    return bool(i is not None and ctx.grid.solid[i])


# ------------------------------------------------------------------ plan -> box ops
def _end_ext(ctx, w, end):
    """Half-thickness of the thickest perpendicular wall of the same level through this end (fills corners)."""
    horiz = abs(w['a'][1] - w['b'][1]) < 1e-6
    px, py = w[end]
    e = 0.0
    for o in ctx.walls.values():
        if o is w or o.get('virtual') or o.get('level') != w.get('level') or 'building' in o:
            continue
        (ax, ay), (bx, by) = o['a'], o['b']
        if (abs(ay - by) < 1e-6) == horiz:
            continue
        if horiz and abs(px - ax) < 0.01 and min(ay, by) - 0.01 <= py <= max(ay, by) + 0.01:
            e = max(e, o['thickness'] / 2)
        if not horiz and abs(py - ay) < 0.01 and min(ax, bx) - 0.01 <= px <= max(ax, bx) + 0.01:
            e = max(e, o['thickness'] / 2)
    return e


def wall_rect(ctx, w):
    """(x0, x1, y0, y1) plan rectangle of an axis-aligned wall including corner extensions."""
    (ax, ay), (bx, by) = w['a'], w['b']
    h = w['thickness'] / 2
    ea, eb = _end_ext(ctx, w, 'a'), _end_ext(ctx, w, 'b')
    if abs(ay - by) < 1e-6:
        return (ax - ea, bx + eb, ay - h, ay + h) if bx > ax else (bx - eb, ax + ea, ay - h, ay + h)
    return (ax - h, ax + h, ay - ea, by + eb) if by > ay else (ax - h, ax + h, by - eb, ay + ea)


def poly_rects(poly, extra=()):
    """Decompose a rectilinear polygon into grid rectangles (x0, x1, y0, y1), also split at the `extra` points.
    A polygon with a diagonal edge is rasterised by cell centres."""
    pts = [(float(p[0]), float(p[1])) for p in poly]
    xs, ys = {_r(p[0]) for p in pts}, {_r(p[1]) for p in pts}
    xs |= {_r(p[0]) for p in extra if min(xs) < p[0] < max(xs)}
    ys |= {_r(p[1]) for p in extra if min(ys) < p[1] < max(ys)}
    xs, ys = sorted(xs), sorted(ys)
    return [(x0, x1, y0, y1) for x0, x1 in zip(xs, xs[1:]) for y0, y1 in zip(ys, ys[1:])
            if point_in_poly((x0 + x1) / 2, (y0 + y1) / 2, pts)]


def _bounds(poly):
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    return min(xs), max(xs), min(ys), max(ys)


def _inter(a, b):
    """Intersection of two (x0, x1, y0, y1) rectangles, or None when it has no area."""
    r = (max(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), min(a[3], b[3]))
    return r if r[1] - r[0] > 1e-6 and r[3] - r[2] > 1e-6 else None


def _overlap_area(ra, rb):
    return sum((i[1] - i[0]) * (i[3] - i[2]) for a in ra for b in rb for i in [_inter(a, b)] if i)


def _carve_top(ctx, rid):
    """ceilingZ; a stairwell stops at the floor of the first `through` room of the flight above its own."""
    r = ctx.rooms[rid]
    top = float(r['ceilingZ'])
    if r.get('kind') == 'stairwell':
        own = next((s for s in ctx.stairs if s['kind'] == 'flight' and s['through'][0] == rid), None)
        if own and own.get('above'):
            above = next(s for s in ctx.stairs if s['id'] == own['above'])
            top = min(top, float(ctx.rooms[above['through'][0]]['floorZ']))
    return top


def _interior(ctx, rid):
    return rid in ctx.rooms and ctx.rooms[rid].get('kind') != 'exterior'


def _ops(ctx, levels):
    """Box operations in the order of MULTILEVEL.md section 4 (mass, rooms, inner walls, features, steps, flight
    sweeps, openings). Void tags: a room id, 'op|<opening>|<room>' (white liner), 'fl|<room>' (cleared by a flight)."""
    ops = []
    fill = lambda r, z0, z1, tag: ops.append(('fill', (*r, z0, z1), tag))
    carve = lambda r, z0, z1, tag: ops.append(('carve', (*r, z0, z1), tag))
    cut = lambda r, z0, z1, tag: ops.append(('cut', (*r, z0, z1), tag))
    on = lambda d: d.get('level', 'G') in levels
    rooms = {rid: r for rid, r in ctx.rooms.items() if on(r) and r.get('kind') != 'exterior'}
    rects = {rid: poly_rects(ctx.room_poly(rid, rect=True)) for rid in ctx.rooms}

    for blk in ctx.spec['exterior']['envelope']['blocks']:             # 1. mass: every storey carries its own slab
        for lv in blk['levels']:
            if lv['level'] not in levels:
                continue
            rcs = poly_rects(lv['polygon'])
            z0 = min([lv['z'][0]] + [r['floorZ'] for rid, r in rooms.items()
                                     if r['level'] == lv['level'] and _overlap_area(rcs, rects[rid]) > 1e-6])
            for rc in rcs:
                fill(rc, z0 - SLAB, lv['z'][1], 'mass')

    for rid, r in rooms.items():                                       # 2. rooms
        top, zones = _carve_top(ctx, rid), r.get('ceilingZones', [])
        for rc in poly_rects(ctx.room_poly(rid, rect=True), [p for z in zones for p in z['polygon']]):
            c = ((rc[0] + rc[1]) / 2, (rc[2] + rc[3]) / 2)
            carve(rc, r['floorZ'], min([top] + [z['z'] for z in zones if point_in_poly(*c, z['polygon'])]), rid)

    for w in ctx.walls.values():                                       # 3. inner walls (arch walls)
        if 'building' not in w and not w.get('virtual') and on(w) and w['rooms'][0] == w['rooms'][1] \
                and w['rooms'][0] in rooms:
            fill(wall_rect(ctx, w), w['baseZ'], w['baseZ'] + w['height'], 'wall:' + w['id'])

    piers = {}
    for f in ctx.features:                                             # 4. features (world Z)
        if not on(f):
            continue
        t, fid, room = f['type'], f['id'], f.get('room')
        if t == 'floor_step':                                          # carve the low side
            (x0, y0), low = f['line'][0], f['lowSide']
            for rc in poly_rects(ctx.room_poly(room, rect=True), f['line']):
                cx, cy = (rc[0] + rc[1]) / 2, (rc[2] + rc[3]) / 2
                if {'east': cx > x0, 'west': cx < x0, 'north': cy > y0, 'south': cy < y0}[low]:
                    carve(rc, f['zLow'], f['zHigh'], room)
        elif t == 'bay':                                               # arris splays: open the square k..c
            for ch in ctx.chamfers(room):
                if ch['reflex'] and ch['id'].startswith(fid + '.'):
                    carve(_bounds([ch['v'], ch['c']]), ch['z'][0], (ch['stop'] or ch['z'])[1], room)
        if 'polygon' not in f:
            continue
        rc = _bounds(f['polygon'])
        if t in SOLID_FEATS:
            fill(rc, f['z'][0], f['z'][1], 'feat:' + fid)
            if t == 'pier':
                piers.setdefault(room, []).append(f)
        elif t in ('recess', 'reveal'):
            carve(rc, f['z'][0], f['z'][1], room)
        elif t == 'arch_vault':                                        # mass above the vault + over the piers
            fz, cz, r = ctx.floor_z(room), ctx.ceil_z(room), f['crown'] - f['springing']
            fill((rc[0] + r, rc[1] - r, rc[2], rc[3]), fz + f['crown'], cz, 'feat:' + fid)      # haunches: _curved
            for p in piers.get(room, []):
                fill(_bounds(p['polygon']), p['z'][1], cz, 'feat:' + fid)
        elif t == 'floor_void':
            for rc in poly_rects(f['polygon']):
                cut(rc, f.get('bottom', f['z'] - 0.5), f.get('top', f['z'] + 0.02), room)
        elif t == 'roof_opening':                                      # shaft from the ceiling to the roof surface
            cut(rc, ctx.ceil_z(room), _roof_at(ctx, (rc[0] + rc[1]) / 2, (rc[2] + rc[3]) / 2), room)

    stairs = [s for s in ctx.stairs if on(s)]
    for s in stairs:                                                   # 5. steps: the cut is their only geometry
        if s['kind'] == 'steps':
            for t in ctx.stair(s['id'])['treads']:
                (cut if t['z'] < s['toZ'] else fill)(_bounds(t['poly']), *sorted((t['z'], s['toZ'])),
                                                     s['toRoom'] if t['z'] < s['toZ'] else 'mass')
    for s in stairs:                                                   # 6. flight sweeps: headroom over every tread
        if s['kind'] != 'flight':
            continue
        if s['id'] in SOLID_FLIGHTS:                                   # the stairwell carve took the mass a solid flight
            base = min(s['fromZ'], s['toZ']) - SLAB                    # stands on: put it back under the square treads
            for t in ctx.stair(s['id'])['treads']:                     # ponytail: winder treads stay hollow (two kites
                b = _bounds(t['poly'])                                 # one riser high, closed by their risers)
                if len(t['poly']) == 4 and abs(abs(poly_area(t['poly'])) - (b[1] - b[0]) * (b[3] - b[2])) < 1e-6:
                    fill(b, base, t['z'], 'mass')
        thr = s['through']
        W = [rc for rid in thr for rc in rects[rid]]
        W += [rc for f in ctx.features if f['type'] == 'floor_void' and f.get('room') in thr for rc in poly_rects(f['polygon'])]
        fzs = sorted((float(ctx.rooms[rid]['floorZ']), rid) for rid in thr)
        for t in ctx.stair(s['id'])['treads']:
            zs = [t['z']] + [fz for fz, _ in fzs[1:] if t['z'] < fz < t['z'] + HEADROOM] + [t['z'] + HEADROOM]
            for rc in filter(None, (_inter(_bounds(t['poly']), w) for w in W)):
                for z0, z1 in zip(zs, zs[1:]):
                    cut(rc, z0, z1, 'fl|' + [rid for fz, rid in fzs if fz <= z0 + 1e-6 or rid == fzs[0][1]][-1])

    for oid, o in ctx.openings.items():                                # 7. openings, through the whole wall
        if 'building' in o or not on(o):
            continue
        fr = ctx.opening_frame(oid)
        if fr['virtual']:
            continue
        c, al, nm, hw, t2 = fr['center'], fr['along'], fr['normal'], fr['width'] / 2, fr['wall_thickness'] / 2
        if min(abs(al[0]), abs(al[1])) > 1e-6:
            print(f'[shell] WARNING opening {oid} is in a diagonal wall - not cut')
            continue
        z0, z1 = c[2], fr['z0'] + fr['top'] + (ARCH_PAD if o['type'] == 'arch' else 0)
        passage = o['type'] in ('arch', 'opening')
        sides = [fr['room_pos'], fr['room_neg']]
        inside = next((r for r in sides + list(o['connects']) if _interior(ctx, r)), None)
        for sgn, room in zip((1, -1), sides):
            p = (c[0] - al[0] * hw, c[1] - al[1] * hw)
            q = (c[0] + al[0] * hw + nm[0] * sgn * t2, c[1] + al[1] * hw + nm[1] * sgn * t2)
            room = room if _interior(ctx, room) else inside
            cut((min(p[0], q[0]), max(p[0], q[0]), min(p[1], q[1]), max(p[1], q[1])), z0, z1,
                room if passage else f'op|{oid}|{room}')
    return ops


def _roof_at(ctx, x, y):
    """Roof surface over (x, y): the main roof, else the porch lean-to, else None."""
    z = ctx.roof_z(x, y)
    return ctx.roof_z(x, y, ground=True) if z is None else z


def _roof_plane(ctx, x, y):
    """(c0, cx, cy) of the roof surface plane over (x, y), or None."""
    for ground in (False, True):
        pid = ctx.roof_plane(x, y, ground)
        if pid:
            z = next(p for p in ctx.spec['roof']['planes'] if p['id'] == pid)['z']
            return z['c0'], z['cx'], z['cy']
    return None


def _trim_roof(g, ctx):
    """Remove the mass cells that lie wholly above the roof surface (the level-2 block is a box up to the ridge), so
    a roof opening cut up to the roof is open to the sky. Under the slopes the result is stepped; no face shows it."""
    nx, ny, _ = g.solid.shape
    mx, my = ((c[:-1] + c[1:]) / 2 for c in g.c[:2])
    rz = np.full((nx, ny), np.inf)
    for i in range(nx):
        for j in range(ny):
            z = _roof_at(ctx, mx[i], my[j])
            if z is not None:
                rz[i, j] = z
    m = (g.solid > 0) & (g.c[2][None, None, :-1] >= rz[:, :, None] - 1e-6)
    g.solid[m], g.void[m] = 0, 0


# ------------------------------------------------------------------ faces -> labelled quads
def _ceil_plane(ctx, room, x, y):
    """(c0, cx, cy) of the sloped ceiling of a 'planes' / 'under_roof' room over (x, y)."""
    r = ctx.rooms[room]
    c = r['ceiling']
    if c['type'] == 'under_roof':                  # underside of the roof slab of the highest plane there
        pid = ctx.roof_plane(x, y)
        if pid:
            z = next(p for p in ctx.spec['roof']['planes'] if p['id'] == pid)['z']
            return z['c0'] - ctx.roof_slab_t(pid), z['cx'], z['cy']
    else:
        ps = [p for p in c['planes'] if poly_contains(x, y, p['polygon'])]
        if ps:
            z = min(ps, key=lambda p: plane_z(p, x, y))['z']
            return z['c0'], z['cx'], z['cy']
    return float(r['ceilingZ']), 0.0, 0.0


def _clip_z(cs, pl):
    """Polygon (3D points) clipped to z <= c0 + cx*x + cy*y; None when nothing is left."""
    c0, cx, cy = pl
    d = [p[2] - (c0 + cx * p[0] + cy * p[1]) for p in cs]
    out = []
    for i, p in enumerate(cs):
        q, dp, dq = cs[(i + 1) % len(cs)], d[i], d[(i + 1) % len(cs)]
        if dp <= 1e-9:
            out.append(p)
        if (dp > 1e-9) != (dq > 1e-9):
            k = dp / (dp - dq)
            out.append(tuple(round(p[a] + (q[a] - p[a]) * k, 6) for a in range(3)))
    out = [p for i, p in enumerate(out) if p != out[i - 1]]
    return out if len(out) >= 3 else None


def _greedy(L):
    out, done = [], np.zeros(L.shape, bool)
    nu, nv = L.shape
    for u in range(nu):
        v = 0
        while v < nv:
            l = L[u, v]
            if l < 0 or done[u, v]:
                v += 1
                continue
            v1 = v + 1
            while v1 < nv and L[u, v1] == l and not done[u, v1]:
                v1 += 1
            u1 = u + 1
            while u1 < nu and (L[u1, v:v1] == l).all() and not done[u1, v:v1].any():
                u1 += 1
            done[u:u1, v:v1] = True
            out.append((u, u1, v, v1, l))
            v = v1
    return out


def _quads(g, ctx):
    """-> {object name: [(corner coords, material spec), ...]} for every face between solid and a room void."""
    S = g.solid > 0
    nz = S.shape[2]
    T, K = np.zeros(S.shape, np.int16), np.zeros(S.shape, np.int32)    # first void above a solid cell: tag, k index
    for k in range(nz - 2, -1, -1):
        up = S[:, :, k + 1]
        T[:, :, k] = np.where(up, T[:, :, k + 1], g.void[:, :, k + 1])
        K[:, :, k] = np.where(up, K[:, :, k + 1], k + 1)
    Z = g.c[2]
    mids = [(c[:-1] + c[1:]) / 2 for c in g.c]

    def parse(t):                                  # void tag -> (kind, room)
        if t is None or t == 'mass' or t[:5] in ('feat:', 'wall:'):
            return None
        return ('op', t.split('|')[2]) if t.startswith('op|') else ('fl', t[3:]) if t.startswith('fl|') else ('', t)
    tagv = [parse(t) for t in g.tags]
    info, fzc, czc, cpl = {}, {}, {}, {}

    def R(room):
        if room not in info:
            r = ctx.rooms[room]
            info[room] = (finish(room), float(r['floorZ']), r.get('kind', 'room'), (r.get('ceiling') or {}).get('type'),
                          float(r['ceilingZ']), r['floor']['material'], split_z(room))
        return info[room]

    def fz_at(room, i):
        key = (room, i[0], i[1])
        if key not in fzc:
            fzc[key] = ctx.floor_z(room, mids[0][i[0]], mids[1][i[1]])
        return fzc[key]

    def cz_at(room, i):
        key = (room, i[0], i[1])
        if key not in czc:
            czc[key] = ctx.ceil_z(room, mids[0][i[0]], mids[1][i[1]])
        return czc[key]
    solid_fl = [(s['walk']['polygon'], min(s['fromZ'], s['toZ']) - 1e-3, max(s['fromZ'], s['toZ']) - 1e-3)
                for s in ctx.stairs if s['kind'] == 'flight' and s['id'] in SOLID_FLIGHTS]

    def label(i, j, a, s):
        """(object name, material spec, clip key) of the unit face of solid cell i against void cell j, or None."""
        st = g.tags[g.solid[i]]
        kind, room = tagv[g.void[j]]
        F, fz, rk, sl, top, fmat, sz = R(room)
        name = room + '.walls'
        if kind == 'op':
            return name, WHITE, None                              # reveal liners (jambs, head, sill)
        tt = tagv[T[i]]
        if tt and tt[0] == 'fl' and (kind == 'fl' or (rk == 'stairwell' and Z[i[2]] >= Z[K[i]] - UNDER_TREAD - 1e-6)):
            return None                                           # under a tread: the flight carcass owns it
        clip = (room, j[0], j[1]) if sl and a != 2 else None
        if st[:5] == 'feat:' and st[5:] in F['features']:
            return name, F['features'][st[5:]], clip
        if a == 2:
            plane = Z[i[2] + (1 if s > 0 else 0)]
            if s > 0 and any(lo < plane < hi and poly_contains(mids[0][i[0]], mids[1][i[1]], p) for p, lo, hi in solid_fl):
                return None                                       # under a solid flight
            if s < 0 and sl and plane >= top - 2e-3:
                return None                                       # box top above a sloped ceiling
            if st == 'mass':
                if s > 0 and abs(plane - fz_at(room, j)) < 2e-3:
                    return room + '.floor', fmat, None
                if s < 0 and not sl and abs(plane - cz_at(room, j)) < 2e-3:
                    return room + '.ceiling', F['ceiling'], None
            return name, (F['ceiling'] if s < 0 else F['upper']), None
        z = mids[2][i[2]]
        if z > top:
            return name, F['ceiling'], clip                       # roof-opening shaft
        if st == 'mass' and kind == '' and rk != 'stairwell' and tt and tt[0] == '':
            zt = Z[K[i]]                                          # riser between split floors: the upper floor's covering
            if zt - fz_at(room, j) <= RISER_MAX + 1e-6 and abs(zt - fz_at(tt[1], i)) < 2e-3:
                return name, R(tt[1])[5], clip
        plane, zr = g.c[a][i[a] + (1 if s > 0 else 0)], z - fz
        for o in F['faces']:
            if o['axis'] == a and abs(o['at'] - plane) < 2e-3:
                h = mids[1 - a][i[1 - a]]
                if ('range' not in o or o['range'][0] < h < o['range'][1]) and \
                        ('z' not in o or o['z'][0] < zr < o['z'][1]):
                    return name, o['mat'], clip
        if F['wainscot'] and zr < F['wainscot'][0]:
            return name, F['wainscot'][1], clip
        return name, (F['lower'] if sz is not None and zr < sz else F['upper']), clip

    labels, lab_i, out = [], {}, {}
    for a in range(3):
        ua, va = (a + 1) % 3, (a + 2) % 3
        for s in (1, -1):
            nbS, nbV = np.ones_like(S), np.zeros_like(g.void)     # neighbour in direction s: solid?, void tag
            src, dst = [slice(None)] * 3, [slice(None)] * 3
            src[a], dst[a] = (slice(1, None), slice(None, -1)) if s > 0 else (slice(None, -1), slice(1, None))
            nbS[tuple(dst)], nbV[tuple(dst)] = S[tuple(src)], g.void[tuple(src)]
            planes = {}
            for i in np.argwhere(S & ~nbS & (nbV > 0)).tolist():
                i = tuple(i)
                j = i[:a] + (i[a] + s,) + i[a + 1:]
                lab = label(i, j, a, s)
                if lab is None:
                    continue
                li = lab_i.setdefault(lab, len(labels))
                if li == len(labels):
                    labels.append(lab)
                p = i[a] + (1 if s > 0 else 0)
                L = planes.get(p)
                if L is None:
                    L = planes[p] = np.full((S.shape[ua], S.shape[va]), -1, np.int32)
                L[i[ua], i[va]] = li
            for p, L in planes.items():
                for u0, u1, v0, v1, li in _greedy(L):
                    name, spec, clip = labels[li]
                    cs = []
                    for uu, vv in ((u0, v0), (u1, v0), (u1, v1), (u0, v1)):
                        pt = [0.0, 0.0, 0.0]
                        pt[a], pt[ua], pt[va] = g.c[a][p], g.c[ua][uu], g.c[va][vv]
                        cs.append(tuple(float(x) for x in pt))
                    cs = cs if s > 0 else cs[::-1]
                    if clip:                                      # wall under a sloped ceiling: one half-plane per cell
                        if clip not in cpl:
                            cpl[clip] = _ceil_plane(ctx, clip[0], mids[0][clip[1]], mids[1][clip[2]])
                        cs = _clip_z(cs, cpl[clip])
                        if cs is None:
                            continue
                    out.setdefault(name, []).append((cs, spec))
    return out


def _mesh_object(name, quads):
    """quads: [(corners, material spec)] -> object with welded verts and material slots."""
    vi, faces, mi, specs = {}, [], [], []
    for cs, spec in quads:
        faces.append([vi.setdefault(c, len(vi)) for c in cs])
        if spec not in specs:
            specs.append(spec)
        mi.append(specs.index(spec))
    me = bpy.data.meshes.new(name)
    me.from_pydata(sorted(vi, key=vi.get), [], faces)
    for spec in specs:
        me.materials.append(material(spec))
    me.polygons.foreach_set('material_index', mi)
    me.update()
    return bpy.data.objects.new(name, me)


def faces_object(name, faces):
    """faces: [(points, point the normal faces towards, material spec)] -> object (welded, uv_box UVs). Degenerate
    faces are skipped. For the non-axis pieces: chamfer prisms, haunches, sloped ceilings, flight carcasses."""
    bm = bmesh.new()
    specs = []
    for pts, toward, spec in faces:
        pts = [Vector(p) for p in pts]
        n = sum((pts[i].cross(pts[(i + 1) % len(pts)]) for i in range(len(pts))), Vector())
        if n.length < 1e-8:
            continue
        f = bm.faces.new([bm.verts.new(p) for p in pts])
        if n.dot(Vector(toward) - f.calc_center_median()) < 0:
            f.normal_flip()
        if spec not in specs:
            specs.append(spec)
        f.material_index = specs.index(spec)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for spec in specs:
        me.materials.append(material(spec))
    ob = bpy.data.objects.new(name, me)
    M.uv_box(ob)
    return ob


# ------------------------------------------------------------------ non-axis pieces
def _chamfer(ctx, room, ch):
    """Prism of one chamfer (ctx.chamfers): the diagonal face, plus caps where it stops short of floor / ceiling
    (polygon-edge chamfer) or the 45-to-90 stop above it (bay arris splay). Like the grid wall quads, the faces are
    split at the dado line: lower paint below floor + split_z, upper above."""
    p, q, c, k = ch['p'], ch['q'], ch['c'], ch['v']
    (z0, z1), F, sz = ch['z'], finish(room), split_z(room)
    zs = None if sz is None else ctx.floor_z(room) + sz
    spec = lambda z: F['lower'] if zs is not None and z < zs else F['upper']
    at = lambda pt, z: (pt[0], pt[1], z)
    front = (p[0] + q[0] - c[0], p[1] + q[1] - c[1])                   # room side of the diagonal
    cuts = [z0] + ([zs] if zs is not None and z0 + 1e-4 < zs < z1 - 1e-4 else []) + [z1]
    faces = [([at(p, a), at(q, a), at(q, b), at(p, b)], at(front, (a + b) / 2), spec((a + b) / 2)) for a, b in zip(cuts, cuts[1:])]
    if not ch['reflex']:
        mid = ((p[0] + q[0] + front[0]) / 3, (p[1] + q[1] + front[1]) / 3)
        if z0 > ctx.floor_z(room) + 1e-3:
            faces.append(([at(p, z0), at(c, z0), at(q, z0)], at(mid, z0 - 1), spec(z0)))
        if z1 < ctx.ceil_z(room, *mid) - 1e-3:
            faces.append(([at(p, z1), at(c, z1), at(q, z1)], at(mid, z1 + 1), spec(z1)))
    elif ch['stop']:
        z2, sp = ch['stop'][1], spec((z1 + ch['stop'][1]) / 2)         # wedge: p, q at z1 rising to the square arris k at z2
        faces += [([at(p, z1), at(q, z1), at(k, z2)], at(front, z1), sp),
                  ([at(p, z1), at(p, z2), at(k, z2)], at((p[0] + k[0] - q[0], p[1] + k[1] - q[1]), z2), sp),
                  ([at(q, z1), at(q, z2), at(k, z2)], at((q[0] + k[0] - p[0], q[1] + k[1] - p[1]), z2), sp)]
    return faces_object(f'{room}.chamfer.{ch["id"]}', faces)


def _haunch(ctx, f):
    """45-degree splay in the wall / ceiling corner at wallAt: the diagonal face only (both ends die into solids)."""
    x0, x1, y0, y1 = _bounds(f['polygon'])
    (z0, z1), w, spec = f['z'], f['wallAt'], finish(f['room'])['ceiling']
    if min(abs(w - x0), abs(w - x1)) < 1e-6:                           # runs along Y
        o = x1 if abs(w - x0) < 1e-6 else x0
        pts, toward = [(w, y0, z0), (w, y1, z0), (o, y1, z1), (o, y0, z1)], (o, (y0 + y1) / 2, z0)
    else:
        o = y1 if abs(w - y0) < 1e-6 else y0
        pts, toward = [(x0, w, z0), (x1, w, z0), (x1, o, z1), (x0, o, z1)], ((x0 + x1) / 2, o, z0)
    return faces_object(f'{f["room"]}.haunch.{f["id"]}', [(pts, toward, spec)])


def _cove(ctx, f):
    """ceiling_cove: quarter-elliptical vault between walls and ceiling. On every side listed in f['sides'] of the
    polygon's bounding box it springs from the wall at z[0] and meets the ceiling z[1] `sides[side]` metres out.
    Neighbouring sides mitre in a groin; an end with no neighbour is closed by a cap."""
    x0, x1, y0, y1 = _bounds(f['polygon'])
    (z0, z1), sides, spec, N = f['z'], f['sides'], finish(f['room'])['ceiling'], 12
    th = [math.pi / 2 * i / N for i in range(N + 1)]
    zt = lambda t: z0 + (z1 - z0) * math.sin(t)
    off = lambda side, t: sides.get(side, 0.0) * (1 - math.cos(t))
    rect = lambda t: (x0 + off('west', t), x1 - off('east', t), y0 + off('south', t), y1 - off('north', t))
    line = {'east': lambda r: ((r[1], r[2]), (r[1], r[3])), 'west': lambda r: ((r[0], r[2]), (r[0], r[3])),
            'north': lambda r: ((r[0], r[3]), (r[1], r[3])), 'south': lambda r: ((r[0], r[2]), (r[1], r[2]))}
    ends = {'east': ('south', 'north'), 'west': ('south', 'north'), 'north': ('west', 'east'), 'south': ('west', 'east')}
    below, faces = ((x0 + x1) / 2, (y0 + y1) / 2, z0 - 1.0), []
    for side in sides:
        for ta, tb in zip(th, th[1:]):
            (a0, a1), (b0, b1) = line[side](rect(ta)), line[side](rect(tb))
            faces.append(([(*a0, zt(ta)), (*a1, zt(ta)), (*b1, zt(tb)), (*b0, zt(tb))], below, spec))
        for k, nb in enumerate(ends[side]):                            # free end: the section of the cove as a cap
            if nb in sides:
                continue
            arc = [(*line[side](rect(t))[k], zt(t)) for t in th]
            corner = (*arc[0][:2], z1)
            out = [2 * arc[0][0] - below[0], 2 * arc[0][1] - below[1], z1]      # away from the middle of the room, along the wall
            out[0 if side in ('east', 'west') else 1] = arc[0][0 if side in ('east', 'west') else 1]
            faces += [([corner, a, b], out, spec) for a, b in zip(arc, arc[1:])]
    ob = faces_object(f'{f["room"]}.cove.{f["id"]}', faces)
    ob.data.polygons.foreach_set('use_smooth', [True] * len(ob.data.polygons))
    ob.data.set_sharp_from_angle(angle=math.radians(40))
    return ob


def _plane_ceiling(ctx, rid):
    """Sloped ceiling of a `planes` room: one face per plane polygon, with a hole and four liners up to the roof
    surface at every roof window of the room."""
    F, faces = finish(rid), []
    wins = [_bounds(f['polygon']) for f in ctx.features if f['type'] == 'roof_window' and f.get('room') == rid]
    for p in ctx.rooms[rid]['ceiling']['planes']:
        z = lambda x, y: plane_z(p, x, y)
        rcs = [_bounds(p['polygon'])]
        for h in wins:
            if not point_in_poly((h[0] + h[1]) / 2, (h[2] + h[3]) / 2, p['polygon']):
                continue
            new = []
            for a in rcs:                                              # frame of four strips round the hole
                if not _inter(a, h):
                    new.append(a)
                    continue
                new += [r for r in ((a[0], a[1], a[2], h[2]), (a[0], a[1], h[3], a[3]),
                                    (a[0], h[0], max(a[2], h[2]), min(a[3], h[3])),
                                    (h[1], a[1], max(a[2], h[2]), min(a[3], h[3]))) if r[1] - r[0] > 1e-6 and r[3] - r[2] > 1e-6]
            rcs = new
            cn = [(h[0], h[2]), (h[1], h[2]), (h[1], h[3]), (h[0], h[3])]
            mid = ((h[0] + h[1]) / 2, (h[2] + h[3]) / 2)
            for a, b in zip(cn, cn[1:] + cn[:1]):
                faces.append(([(*a, z(*a)), (*b, z(*b)), (*b, _roof_at(ctx, *b) - 0.01), (*a, _roof_at(ctx, *a) - 0.01)],
                              (*mid, z(*mid) + 0.1), F['joinery']))
        for x0, x1, y0, y1 in rcs:
            faces.append(([(x0, y0, z(x0, y0)), (x1, y0, z(x1, y0)), (x1, y1, z(x1, y1)), (x0, y1, z(x0, y1))],
                          ((x0 + x1) / 2, (y0 + y1) / 2, z((x0 + x1) / 2, (y0 + y1) / 2) - 1), F['ceiling']))
    planes, room = ctx.rooms[rid]['ceiling']['planes'], ctx.room_poly(rid)
    cuts = sorted({v for pt in room for v in pt})
    for i, p in enumerate(planes):                                     # downstand where two planes meet at different heights
        for q in planes[i + 1:]:
            for a, b in _shared_edges(p['polygon'], q['polygon']):
                ax = 0 if abs(a[1] - b[1]) < 1e-9 else 1               # the edge runs along this axis
                ts = [a[ax]] + [v for v in cuts if a[ax] + 1e-6 < v < b[ax] - 1e-6] + [b[ax]]
                for t0, t1 in zip(ts, ts[1:]):                         # only where the room is on both sides of the edge
                    u, v = list(a), list(a)
                    u[ax], v[ax] = t0, t1
                    m, n = [(u[0] + v[0]) / 2, (u[1] + v[1]) / 2], [0.0, 0.0]
                    n[1 - ax] = 0.01
                    side = [(m[0] + sg * n[0], m[1] + sg * n[1]) for sg in (1, -1)]
                    if not all(point_in_poly(*pt, room) for pt in side):
                        continue
                    zp, zq = [plane_z(p, *e) for e in (u, v)], [plane_z(q, *e) for e in (u, v)]
                    if max(abs(zp[0] - zq[0]), abs(zp[1] - zq[1])) < 0.003:
                        continue
                    hi = p if zp[0] + zp[1] > zq[0] + zq[1] else q     # seen from under the higher plane
                    toward = next((pt for pt in side if point_in_poly(*pt, hi['polygon'])), side[0])
                    faces.append(([(*u, min(zp[0], zq[0])), (*v, min(zp[1], zq[1])), (*v, max(zp[1], zq[1])), (*u, max(zp[0], zq[0]))],
                                  (m[0] + (toward[0] - m[0]) * 50, m[1] + (toward[1] - m[1]) * 50, (zp[0] + zq[0]) / 2), F['ceiling']))
    return faces_object(rid + '.ceiling', faces)


def _shared_edges(pa, pb):
    """Axis-aligned segments (a, b), a < b along the edge, that an edge of polygon pa shares with an edge of pb."""
    out = []
    for a0, a1 in zip(pa, pa[1:] + pa[:1]):
        for b0, b1 in zip(pb, pb[1:] + pb[:1]):
            for ax in (0, 1):                                          # both edges lie on the same line c[1 - ax] = const
                k = 1 - ax
                if max(abs(a0[k] - a1[k]), abs(b0[k] - b1[k]), abs(a0[k] - b0[k])) > 1e-6:
                    continue
                lo, hi = max(min(a0[ax], a1[ax]), min(b0[ax], b1[ax])), min(max(a0[ax], a1[ax]), max(b0[ax], b1[ax]))
                if hi - lo > 1e-6:
                    u, v = [0.0, 0.0], [0.0, 0.0]
                    u[ax], v[ax], u[k], v[k] = lo, hi, a0[k], a0[k]
                    out.append((tuple(u), tuple(v)))
    return out


def _fan_prism(name, pieces, d0, d1, spec, axis=0):
    """pieces: [((cu, cz), [(u, z), ...arc], (vu, vz), [extra (u, z)...])] in the plane of a wall along `axis`
    (u = that coordinate). Each piece is the fan corner->arc(+extra) extruded d0..d1 across the wall; emits both end
    faces and the curved intrados along arc, whose normals face the void point v (the faces against the wall are
    left out)."""
    P = (lambda u, d, z: Vector((u, d, z))) if axis == 0 else (lambda u, d, z: Vector((d, u, z)))
    bm = bmesh.new()

    def face(pts, want, smooth=False):
        f = bm.faces.new([bm.verts.new(p) for p in pts])
        f.normal_update()
        if f.normal.dot(want) < 0:
            f.normal_flip()
        f.smooth = smooth
    for (cu, cz), arc, (vu, vz), extra in pieces:
        ring = arc + extra
        for (ua, za), (ub, zb) in zip(ring, ring[1:]):
            face([P(cu, d0, cz), P(ua, d0, za), P(ub, d0, zb)], P(0, -1, 0))
            face([P(cu, d1, cz), P(ua, d1, za), P(ub, d1, zb)], P(0, 1, 0))
        for (ua, za), (ub, zb) in zip(arc, arc[1:]):
            mu, mz = (ua + ub) / 2, (za + zb) / 2
            face([P(ua, d0, za), P(ub, d0, zb), P(ub, d1, zb), P(ua, d1, za)], P(vu - mu, 0, vz - mz), True)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(material(spec))
    ob = bpy.data.objects.new(name, me)
    M.uv_box(ob)
    return ob


def _unique(name):
    return name if name not in bpy.data.objects else next(f'{name}.{n}' for n in range(2, 99) if f'{name}.{n}' not in bpy.data.objects)


def _curved(ctx, levels):
    """Arch infill (walls along X or Y; springing / crown above the opening's floorZ) and the vestibule vault."""
    N = 24                                                        # segments per haunch / half arch
    for f in ctx.features:
        if f.get('level', 'G') not in levels:
            continue
        room = f.get('room')
        if f['type'] == 'arch':                                   # segmental / semicircular arch
            o = ctx.openings[f['opening']]
            w = ctx.walls[o['wall']]
            ax = 0 if abs(w['a'][1] - w['b'][1]) < 1e-6 else 1
            fz = ctx.opening_frame(f['opening'])['z0']
            ua, ub = o['center'][ax] - o['width'] / 2, o['center'][ax] + o['width'] / 2
            zs, zc = fz + f['springing'], fz + f['crown']
            zt, hs, um = zc + ARCH_PAD, (ub - ua) / 2, (ua + ub) / 2
            rise = min(zc - zs, hs)                               # a taller arch is stilted on straight jambs
            R = (hs * hs + rise * rise) / (2 * rise)
            th0 = math.asin(min(1.0, hs / R))
            arc = lambda sg: [(um + sg * R * math.sin(th0 * (1 - i / N)), zc - R + R * math.cos(th0 * (1 - i / N)))
                              for i in range(N + 1)]
            rc = wall_rect(ctx, w)
            d0, d1 = (rc[2], rc[3]) if ax == 0 else (rc[0], rc[1])
            ob = _fan_prism(_unique(room + '.arch_fill'), [((ua, zt), arc(-1), (um, zs), [(um, zt)]),
                                                           ((ub, zt), arc(1), (um, zs), [(um, zt)])], d0, d1, finish(room)['upper'], ax)
            ctx.add(ob, room, 'shell')
        elif f['type'] == 'arch_vault':                           # basket vault: quarter-round haunches
            x0, x1, y0, y1 = _bounds(f['polygon'])
            fz = ctx.floor_z(room)
            zs, zc, cz = fz + f['springing'], fz + f['crown'], ctx.ceil_z(room)
            r = zc - zs
            hp = lambda xp, sg: [(xp - sg * r * (1 - math.cos(math.pi / 2 * i / N)), zs + r * math.sin(math.pi / 2 * i / N))
                                 for i in range(N + 1)]
            ob = _fan_prism(_unique(room + '.vault_fill'), [((x0, cz), hp(x0, -1), (x0 + r, zs), [(x0 + r, cz)]),
                                                            ((x1, cz), hp(x1, 1), (x1 - r, zs), [(x1 - r, cz)])], y0, y1,
                            finish(room)['upper'])
            ctx.add(ob, room, 'shell')


def _pieces(ctx, levels):
    for rid, r in ctx.rooms.items():
        if r.get('level', 'G') not in levels or r.get('kind') == 'exterior':
            continue
        for ch in ctx.chamfers(rid):
            ctx.add(_chamfer(ctx, rid, ch), rid, 'shell')['part'] = 'chamfer'
        if (r.get('ceiling') or {}).get('type') == 'planes':
            ctx.add(_plane_ceiling(ctx, rid), rid, 'shell')['part'] = 'ceiling'
    for f in ctx.features:
        if f['type'] == 'ceiling_haunch' and f.get('level', 'G') in levels:
            ctx.add(_haunch(ctx, f), f['room'], 'shell')['part'] = 'haunch'
        if f['type'] == 'ceiling_cove' and f.get('level', 'G') in levels:
            ctx.add(_cove(ctx, f), f['room'], 'shell')['part'] = 'cove'
    _curved(ctx, levels)


def box(name, x0, x1, y0, y1, z0, z1, spec):
    """World-axis-aligned slab (metres, world coords, origin at the world origin) with one material
    spec ('#RRGGBB' paint or lib.materials key) and true-scale uv_box UVs. Not linked: ctx.add it.
    For splashbacks, soffits, fillers: keep it >= 1 mm proud of the shell face it covers; call
    materials.uv_box(ob, origin=...) again to register tile joints."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = ((x0 + x1) / 2 + v.co.x * (x1 - x0), (y0 + y1) / 2 + v.co.y * (y1 - y0), (z0 + z1) / 2 + v.co.z * (z1 - z0))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(material(spec))
    ob = bpy.data.objects.new(name, me)
    M.uv_box(ob)
    return ob


# opening id -> (width, thickness, material): basement.md 2.1, a ribbed aluminium stair nosing caps the hall floor edge
# ponytail: one plain bar, the two black anti-slip inserts are not modelled
THRESHOLD = {'d_basement': (0.055, 0.006, 'silver_satin')}
CARPET_STRIP = (0.030, 0.004, 'brass')      # landing1.md 2 / landing2.md 2: brass carpet strip at EVERY doorway upstairs


def _thresholds(ctx, levels):
    """Bar under the door line, <first room>.threshold.<oid>: THRESHOLD[oid]; a brass carpet strip at every doorway of
    levels 1 and 2; elsewhere a hardwood bar (mahogany sill at the mahogany screen) where two floor finishes meet."""
    for oid, o in ctx.openings.items():
        a, b = o['connects']
        if o.get('level', 'G') not in levels or a not in ctx.rooms or b not in ctx.rooms or 'door' not in o['type']                 or 'exterior' in (ctx.kind(a), ctx.kind(b)):       # the balcony door stands on its own uPVC sill
            continue
        upper = o.get('level') in ('1', '2')
        if not (upper or oid in THRESHOLD or ctx.rooms[a]['floor']['material'] != ctx.rooms[b]['floor']['material']):
            continue
        f = ctx.opening_frame(oid)
        # inner (mahogany) screen: flush 100 mm mahogany sill (vestibule.md, f_0026); elsewhere a 75 x 8 hardwood bar
        wd, th, key = THRESHOLD.get(oid) or (CARPET_STRIP if upper else (0.100, 0.002, 'mahogany')
                                             if str(o.get('style', '')).startswith('mahogany') else (0.075, 0.008, 'hardwood_threshold'))
        c, al, hw, d = f['center'], f['along'], f['width'] / 2, min(wd, f['wall_thickness']) / 2
        ex, ey = abs(al[0]) * hw + abs(al[1]) * d, abs(al[1]) * hw + abs(al[0]) * d
        z = max(c[2], ctx.floor_z(a), ctx.floor_z(b)) if upper else c[2]      # on the higher floor where a door has a step
        ob = box(f'{a}.threshold.{oid}', c[0] - ex, c[0] + ex, c[1] - ey, c[1] + ey, z, z + th, key)
        M.uv_box(ob, rotate=abs(al[0]) > 0.5)                     # grain along the bar
        ctx.add(ob, a, 'shell')


# ------------------------------------------------------------------ helpers for other modules
def _near(a, b, tol=1e-4):                                        # grid coordinates are rounded to 0.1 mm
    return abs(a[0] - b[0]) < tol and abs(a[1] - b[1]) < tol


def _merge(loop):
    """Join consecutive collinear runs of the same kind / opening (also across the loop's start)."""
    def joins(r0, r1):
        (a, b), c = r0[:2], r1[1]
        return r0[2:] == r1[2:] and abs((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])) < 1e-9
    out = []
    for r in loop:
        if out and joins(out[-1], r):
            out[-1] = (out[-1][0], r[1], *r[2:])
        else:
            out.append(r)
    if len(out) > 1 and joins(out[-1], out[0]):
        out[0] = (out[-1][0], out[0][1], *out[0][2:])
        out.pop()
    return out


def _substitute(loop, p, q, path):
    """Algorithm C on one loop: replace whatever the grid outline does between p and q (at most four runs, through
    the squared-off corner) by the runs along `path` (p ... q). Returns the loop unchanged when p -> q is not on it."""
    runs = []
    for a, b, kind, oid in loop:                                  # split the runs that pass through p or q
        dx, dy = b[0] - a[0], b[1] - a[1]
        on = [pt for pt in (p, q) if abs((pt[0] - a[0]) * dy - (pt[1] - a[1]) * dx) < 1e-4 * math.hypot(dx, dy)]
        ts = sorted(t for t in (((pt[0] - a[0]) * dx + (pt[1] - a[1]) * dy) / (dx * dx + dy * dy) for pt in on)
                    if 1e-4 < t * math.hypot(dx, dy) < math.hypot(dx, dy) - 1e-4)
        pts = [a] + [(a[0] + dx * t, a[1] + dy * t) for t in ts] + [b]
        runs += [(u, v, kind, oid) for u, v in zip(pts, pts[1:])]
    n = len(runs)
    for i in range(n):
        if not _near(runs[i][0], p):
            continue
        for m in range(1, 5):
            if _near(runs[(i + m - 1) % n][1], q):
                path = [runs[i][0]] + list(path[1:-1]) + [runs[(i + m - 1) % n][1]]       # keep the loop closed exactly
                new = [(u, v, 'wall', None) for u, v in zip(path, path[1:])]
                rest = [runs[(i + m + t) % n] for t in range(n - m)]
                return _merge(new + rest)
    return loop


def wall_runs(ctx, room, z=0.05):
    """Outline of the room's clear space at WORLD height z (piers, pilasters, breast, boxing included), as
    closed loops of straight runs walked with the ROOM ON THE LEFT (outer boundary = counter-clockwise).
    -> [[((ax, ay), (bx, by), kind, opening_id), ...], ...]; kind 'wall' = solid behind the run,
    'open' = door/window hole or open boundary (opening_id is None for the latter). Chamfers are followed
    (Algorithm C): a diagonal run p -> q inside a chamfer's z, the square arris between a bay splay's z[1] and its stop."""
    g = ctx.grid
    k = g.k_at(z)
    ids = [g._ti[t] for t in (room, 'fl|' + room) if t in g._ti]
    R = np.isin(g.void[:, :, k], ids) & (g.solid[:, :, k] == 0)
    nx, ny = R.shape
    X, Y = g.c[0], g.c[1]
    edges = {}
    for i, j in np.argwhere(R):
        i, j = int(i), int(j)
        for ii, jj, a, b in ((i + 1, j, (i + 1, j), (i + 1, j + 1)), (i, j + 1, (i + 1, j + 1), (i, j + 1)),
                             (i - 1, j, (i, j + 1), (i, j)), (i, j - 1, (i, j), (i + 1, j))):
            ok = 0 <= ii < nx and 0 <= jj < ny
            if ok and R[ii, jj]:
                continue
            tag = g.tags[g.void[ii, jj, k]] if ok else None
            kind = 'wall' if ok and g.solid[ii, jj, k] else 'open'
            edges[a] = (b, kind, tag.split('|')[1] if kind == 'open' and tag and tag.startswith('op|') else None)
    loops = []
    while edges:
        a, loop = next(iter(edges)), []
        while a in edges:
            b, kind, oid = edges.pop(a)
            loop.append(((float(X[a[0]]), float(Y[a[1]])), (float(X[b[0]]), float(Y[b[1]])), kind, oid))
            a = b
        loops.append(_merge(loop))
    for ch in ctx.chamfers(room):
        (z0, z1), zs = ch['z'], (ch['stop'] or ch['z'])[1]
        if not z0 - 1e-6 <= z <= zs + 1e-6:
            continue
        path = [ch['p'], ch['q']] if z <= z1 + 1e-6 or not ch['reflex'] else [ch['p'], ch['v'], ch['q']]
        loops = [_substitute(_substitute(loop, ch['p'], ch['q'], path), ch['q'], ch['p'], path[::-1]) for loop in loops]
    return loops


def surface(room, part='walls'):
    """Shell object of a room: part in walls | floor | ceiling | flight (plus arch_fill / vault_fill, chamfer.<id>,
    haunch.<id>, cove.<id> where present)."""
    return bpy.data.objects.get(f'{room}.{part}')


def remove(room, part):
    """Delete a shell object of a room, e.g. shell.remove('stairs', 'flight') before a room module builds its own."""
    ob = surface(room, part)
    if ob:
        bpy.data.objects.remove(ob, do_unlink=True)
    return ob is not None


def repaint(room, old, new, part='walls'):
    """Swap one finish of a room's shell surface: old/new are material specs ('#RRGGBB' or key) or Materials.
    e.g. shell.repaint('kitchen', '#F1EFE9', '#EEEEEE'). Returns the number of slots changed."""
    ob = surface(room, part)
    old, new = (material(m) if isinstance(m, str) else m for m in (old, new))
    n = 0
    for slot in ob.material_slots if ob else ():
        if slot.material == old:
            slot.material, n = new, n + 1
    return n


def section_cap(ctx, axis, at, roof=True):
    """Black poche of everything solid in the grid on the plane <axis> = at (previews only: an unlinked object with
    no tags). Vertical caps are clipped to the roof surface, because the level-2 mass is a box up to the ridge."""
    g = ctx.grid
    i = int(np.searchsorted(g.c[axis], at, side='right')) - 1
    if not 0 <= i < g.solid.shape[axis]:
        return None
    S = np.take(g.solid, i, axis=axis) > 0
    ua, va = (axis + 1) % 3, (axis + 2) % 3
    if axis == 1:
        S = S.T                                                   # -> indexed [ua, va] = [z, x]
    mids = [(c[:-1] + c[1:]) / 2 for c in g.c]
    hz = None if axis == 2 else (0 if va == 2 else 1)             # vertical caps merge along z only (one roof plane each)
    L = np.where(S, 0 if hz is None else np.arange(S.shape[hz]).reshape((-1, 1) if hz == 0 else (1, -1)), -1).astype(np.int32)
    quads = []
    for u0, u1, v0, v1, _ in _greedy(L):
        cs = []
        for uu, vv in ((u0, v0), (u1, v0), (u1, v1), (u0, v1)):
            pt = [0.0, 0.0, 0.0]
            pt[axis], pt[ua], pt[va] = at, g.c[ua][uu], g.c[va][vv]
            cs.append(tuple(float(x) for x in pt))
        if hz is not None and roof:
            h = 1 - axis                                          # the horizontal axis inside the cap
            m = [at, at]
            m[h] = mids[h][u0 if ua == h else v0]
            pl = _roof_plane(ctx, *m)
            cs = _clip_z(cs, pl) if pl else cs
            if cs is None:
                continue
        quads.append((cs, '#000000'))
    return _mesh_object('preview.cap', quads) if quads else None


# ------------------------------------------------------------------ entry point
def build(ctx, levels=None, bare=False):
    """Build the shell of the given levels (default: all): grid surfaces, non-axis pieces, flight carcasses,
    thresholds, then joinery and trim unless bare. Needs a schema-2 house (build.py --house <path>)."""
    assert ctx.schema == 2, 'lib.shell builds the multi-level spec (schema "house/2"): spec/house.json is schema 2 since the phase-2 adoption'
    levels = [l for l in ctx.levels if levels is None or l in levels]
    lv = set(levels)
    ops = _ops(ctx, lv)
    xs, ys, zs = set(), set(), set()
    for rid, r in ctx.rooms.items():
        if r.get('level', 'G') not in lv:
            continue
        F, fz = finish(rid), float(r['floorZ'])
        zs.update(fz + z for z in (split_z(rid), F['wainscot'] and F['wainscot'][0]) if z)
        for o in F['faces']:
            (ys if o['axis'] == 0 else xs).update(o.get('range', ()))
            zs.update(fz + z for z in o.get('z', ()))
        for p in (r.get('ceiling') or {}).get('planes', []):          # one ceiling plane per cell
            xs.update(q[0] for q in p['polygon'])
            ys.update(q[1] for q in p['polygon'])
    for p in ctx.spec['roof']['planes']:                              # one roof plane per cell, flat roofs exact
        xs.update(q[0] for q in p['polygon'])
        ys.update(q[1] for q in p['polygon'])
        if not p['z']['cx'] and not p['z']['cy']:
            zs.add(p['z']['c0'])
    lim = [(min(b[2 * a] for _, b, _ in ops), max(b[2 * a + 1] for _, b, _ in ops)) for a in range(3)]
    g = ctx.grid = Grid(ops, tuple({v for v in s if lim[a][0] < v < lim[a][1]} for a, s in enumerate((xs, ys, zs))))
    _trim_roof(g, ctx)
    n, tris = 0, 0
    for name, qs in sorted(_quads(g, ctx).items()):
        room, part = name.split('.')
        rot = part == 'floor' and ctx.rooms[room]['floor'].get('direction') == 'x'
        ob = ctx.add(_mesh_object(name, qs), room, 'shell')
        ob['part'] = part
        M.uv_box(ob, rotate=rot, origin=FLOOR_ORIGIN.get(room, (0, 0, 0)) if part == 'floor' else (0, 0, 0))
        n += len(qs)
        if part == 'floor' and ctx.kind(room) != 'stairwell':     # self-check: the floor covers the room polygon
            area = sum(abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(c, c[1:] + c[:1]))) / 2 for c, _ in qs)
            rcs = poly_rects(ctx.room_poly(room, rect=True))
            want = _overlap_area(rcs, rcs) - sum(
                _overlap_area(rcs, poly_rects(f['polygon'])) for f in ctx.features
                if f['type'] == 'floor_void' and f.get('level') == ctx.level(room))
            assert area > 0.85 * want, f'{name}: floor area {area:.2f} < polygon {want:.2f}'
    missing = [rid for rid in ctx.rooms if ctx.level(rid) in lv and ctx.kind(rid) not in ('stairwell', 'exterior')
               and surface(rid, 'floor') is None]
    assert not missing, f'rooms without a floor: {missing}'
    _pieces(ctx, lv)
    from . import stairs
    for s in ctx.stairs:
        if s['kind'] == 'flight' and s.get('level') in lv:
            stairs.carcass(ctx, s['id'])
    _thresholds(ctx, lv)
    for o in ctx.col('shell').objects:
        tris += sum(len(p.vertices) - 2 for p in o.data.polygons)
    print(f'[shell] levels {",".join(levels)}: grid {g.solid.shape}, {n} grid faces, {len(ctx.col("shell").objects)} objects, '
          f'{tris} triangles (budget 60000)')
    if tris > 60000:
        ctx.errors = getattr(ctx, 'errors', []) + [f'shell: {tris} triangles > 60000']
    if not bare:
        _install(ctx, lv)


def _install(ctx, levels):
    """Joinery and trim are owned by other modules; call them if they exist, log loudly if not."""
    import traceback
    ctx.errors = getattr(ctx, 'errors', [])

    def call(what, fn, *a):
        try:
            fn(*a)
        except Exception:
            traceback.print_exc()
            ctx.errors.append(what)
            print(f'[shell] ERROR in {what} - continuing without it')
    whole = levels >= set(ctx.levels)
    try:                                         # ImportError/AttributeError = module not written (yet)
        from . import joinery
        fn = joinery.install_openings if whole else joinery.build_opening
    except (ImportError, AttributeError) as e:
        print(f'[shell] joinery.install_openings missing ({e}) - openings left bare')
    else:
        if whole:
            call('joinery.install_openings', fn, ctx)
        else:                                    # a subset of levels: only their openings
            for oid, o in ctx.openings.items():
                if o.get('level', 'G') in levels:
                    call(f'joinery:{oid}', fn, ctx, oid)
    try:
        from . import mouldings
        fn = mouldings.install_room_trim
    except (ImportError, AttributeError) as e:
        print(f'[shell] mouldings.install_room_trim missing ({e}) - no skirting/dado/cornice')
    else:
        for rid in ctx.rooms:
            if ctx.level(rid) in levels:
                call(f'mouldings.install_room_trim({rid})', fn, ctx, rid)

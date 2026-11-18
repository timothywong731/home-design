"""Architecture shell built from spec/house.json: solid walls with openings, floors, ceilings, features.

Everything in house.json is axis-aligned, so the shell is box CSG on a non-uniform grid (class Grid):
solid/void boxes are rasterised onto the grid of all their coordinates, then the boundary faces are
emitted as merged quads. No booleans, no coplanar duplicates, and every face knows which room it
faces, so it gets that room's finish from FINISHES. Curved bits (hall arch, vestibule vault) are
small extruded infill meshes added on top.
"""
import math

import bmesh
import bpy
import numpy as np

from . import materials as M
from .ctx import point_in_poly

SLAB = 0.15          # floor slab thickness below Z=0
CEIL_T = 0.12        # ceiling slab thickness
WHITE = '#F4F2EC'    # painted joinery / reveal liners
EXT = '#9A6B55'      # exterior placeholder (brick-ish)
TOPS = '#3C3C3C'     # wall tops (reads as plan poche in the top-down view)
ARCH_PAD = 0.06      # arch holes are cut this much above the crown; the infill mesh owns that band

# world point that lands on UV (0, 0) of a room's floor texture (registers the tile motif to the spec)
FLOOR_ORIGIN = {'vestibule': (-0.045 - 0.165, 0.025 - 0.165, 0.0)}      # blue square centred on (-0.045, 0.025)

# Per-room finishes (colours = neutral-light estimates from spec/rooms/<id>.md section 3).
#   upper/lower : wall paint above/below the dado split (same when no dado)
#   dado        : TOP of the dado rail (m) or None; dado_h = rail height; paint splits at dado - dado_h/2
#   (skirting / dado rail / cornice PROFILES live in lib.mouldings.TRIM; its dado 'top' must equal `dado` here)
#   faces       : per-face overrides [dict(axis=0|1, at=coord, mat=spec, range=(lo,hi)?, z=(z0,z1)?)]
#   wainscot    : (z_top, material) applied to every wall face of the room below z_top
#   features    : feature id -> material for all faces of that feature seen from this room
# A material spec is '#RRGGBB' (paint) or a lib.materials key.
FINISHES = {
    'vestibule': dict(upper='#F2F0EA', lower='#C8C5BB', dado=0.965, dado_h=0.07, ceiling='#F4F3EE', joinery=WHITE),
    # lower: hallway.md gives #B9B5A8; it rendered a khaki band ~0.6 of the upper wall where f_0770 / f_0548 show a
    # pale greige at ~0.78 (the oak floor's bounce warms it), so it is lightened and neutralised.
    'hallway': dict(upper='#F2F0EA', lower='#C8C5BB', dado=0.965, dado_h=0.07, ceiling='#F4F3EE', joinery=WHITE,
                    features={'lobby_overhead_cupboard': WHITE, 'stair_boarding': WHITE,
                              'stair_corner_post': WHITE}),
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
}
for _f in FINISHES.values():
    _f.setdefault('faces', []), _f.setdefault('features', {}), _f.setdefault('wainscot', None)

_mats = {}


def finish(room):
    return FINISHES[room]


def split_z(room):
    """Height where lower paint changes to upper (hidden behind the dado rail), or None."""
    f = FINISHES[room]
    return None if f['dado'] is None else round(f['dado'] - f['dado_h'] / 2, 4)


def material(spec):
    """'#RRGGBB' -> matt paint, anything else -> lib.materials key (KeyError when unknown)."""
    if spec not in _mats:
        _mats[spec] = M.paint(spec) if spec.startswith('#') else M.mat(spec)
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
        self.c = [np.array(sorted(_r(v) for v in s)) for s in cs]
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


# ------------------------------------------------------------------ plan -> box ops
def _end_ext(ctx, w, end):
    """Half-thickness of the thickest perpendicular wall through this end (fills corners); as validate_house.py."""
    horiz = abs(w['a'][1] - w['b'][1]) < 1e-6
    px, py = w[end]
    e = 0.0
    for o in ctx.walls.values():
        if o is w or o.get('virtual'):
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
    """(x0, x1, y0, y1) plan rectangle of a wall including corner extensions."""
    (ax, ay), (bx, by) = w['a'], w['b']
    h = w['thickness'] / 2
    ea, eb = _end_ext(ctx, w, 'a'), _end_ext(ctx, w, 'b')
    if abs(ay - by) < 1e-6:
        return (ax - ea, bx + eb, ay - h, ay + h) if bx > ax else (bx - eb, ax + ea, ay - h, ay + h)
    return (ax - h, ax + h, ay - ea, by + eb) if by > ay else (ax - h, ax + h, by - eb, ay + ea)


def poly_rects(poly):
    """Decompose a rectilinear polygon into grid rectangles (x0, x1, y0, y1)."""
    xs, ys = sorted({_r(p[0]) for p in poly}), sorted({_r(p[1]) for p in poly})
    return [(x0, x1, y0, y1) for x0, x1 in zip(xs, xs[1:]) for y0, y1 in zip(ys, ys[1:])
            if point_in_poly((x0 + x1) / 2, (y0 + y1) / 2, [tuple(p) for p in poly])]


def _bounds(poly):
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    return min(xs), max(xs), min(ys), max(ys)


def _ops(ctx):
    ops = []
    fill = lambda r, z0, z1, tag: ops.append(('fill', (*r, z0, z1), tag))
    carve = lambda r, z0, z1, tag: ops.append(('carve', (*r, z0, z1), tag))
    real = [w for w in ctx.walls.values() if not w.get('virtual')]
    inner = [w for w in real if w['rooms'][0] == w['rooms'][1]]        # partition inside one room (arch wall)
    for w in real:                                                     # slab under walls, walls
        fill(wall_rect(ctx, w), -SLAB, 0, 'slab')
        if w not in inner:
            fill(wall_rect(ctx, w), 0, w['height'], 'wall:' + w['id'])
    for rid, r in ctx.rooms.items():
        for rc in poly_rects(r['polygon']):
            fill(rc, r['floorZ'] - SLAB, r['floorZ'], 'slab')
            carve(rc, r['floorZ'], r['ceilingZ'], rid)
    for w in inner:
        fill(wall_rect(ctx, w), 0, w['height'], 'wall:' + w['id'])

    piers = {}
    for f in ctx.features:
        t, fid, room = f['type'], f['id'], f.get('room')
        if 'polygon' not in f:
            continue
        rc = _bounds(f['polygon'])
        if fid == 'lobby_overhead_cupboard' or t in ('soffit', 'bay', 'outside_yard', 'panelled_spandrel'):
            continue                                                   # stairwell special / no geometry
        if t in ('pier', 'pilaster', 'nib', 'chimney_breast', 'boxing', 'hearth'):
            fill(rc, f['z'][0], f['z'][1], 'feat:' + fid)
            if t == 'pier':
                piers.setdefault(room, []).append(f)
        elif t == 'poche':
            fill(rc, 0, ctx.spec['ceilingDefault'], 'feat:' + fid)
        elif t == 'recess':                                            # room polygon includes it: close the top
            fill(rc, f['z'][1], ctx.ceil_z(room), 'feat:' + fid)
        elif t == 'reveal':
            carve(rc, f['z'][0], f['z'][1], room)
        elif t == 'arch_vault':                                        # mass above the vault + over the piers
            cz, r = ctx.ceil_z(room), f['crown'] - f['springing']
            fill((rc[0] + r, rc[1] - r, rc[2], rc[3]), f['crown'], cz, 'feat:' + fid)   # haunches: _curved
            for p in piers.get(room, []):
                fill(_bounds(p['polygon']), p['z'][1], cz, 'feat:' + fid)

    for oid, o in ctx.openings.items():
        fr = ctx.opening_frame(oid)
        if fr['virtual']:
            continue
        c, al, nm, hw, t2 = fr['center'], fr['along'], fr['normal'], fr['width'] / 2, fr['wall_thickness'] / 2
        z0, z1 = c.z, fr['z0'] + fr['top'] + (ARCH_PAD if o['type'] == 'arch' else 0)
        passage = o['type'] in ('arch', 'opening')
        inside = next(r for r in o['connects'] if r != 'outside')
        for sgn, room in ((1, fr['room_pos']), (-1, fr['room_neg'])):
            p = (c.x - al.x * hw, c.y - al.y * hw)
            q = (c.x + al.x * hw + nm.x * sgn * t2, c.y + al.y * hw + nm.y * sgn * t2)
            rc = (min(p[0], q[0]), max(p[0], q[0]), min(p[1], q[1]), max(p[1], q[1]))
            room = inside if room == 'outside' else room
            ops.append(('cut', (*rc, z0, z1), room if passage else f'op|{oid}|{room}'))
    _stairwell(ctx, fill, carve)
    return ops


def _stairwell(ctx, fill, carve):
    """Stair void above the lobby, half-landing slab / soffit, enclosing walls up to the stairwell cap.
    The flight, strings, balustrade and spandrel panelling belong to rooms/stairs.py."""
    S = ctx.stairs
    x0, x1, ys0, ys1 = _bounds(ctx.room_poly('stairs'))                # 0.15 0.99 4.83 7.58
    _, _, yl0, yl1 = _bounds(S['landing']['polygon'])                  # 8.13 8.73
    sof, lz = S['landing']['soffitZ'], S['landing']['z']
    top, hc = ctx.ceil_z('stairs'), ctx.ceil_z('hallway')
    cb = ctx.feature('lobby_overhead_cupboard')
    cz0, cz1 = cb['z']
    yw = _bounds(cb['polygon'])[2]                                     # 7.68 lobby face of the under-stairs wall
    y14 = S['lastRiserY'] - S['going']                                 # riser 14
    tread = lambda n: n * S['rise']                                    # top of tread n
    carve((x0, x1, ys1, yw), tread(12) - 0.08, top, 'stairs')          # under-stairs wall stops under tread 12
    carve((x0, x1, yw, yl0), cz0, top, 'stairs')
    carve((x0, x1, yl0, yl1), sof, top, 'stairs')
    wt = 0.06                                                          # thin upper walls inside the well
    fill((x1, x1 + 0.26, ys1 - 0.1, yl1 + 0.1), hc, top, 'wall:stairwell')       # east, on the lobby/kitchen wall
    fill((x0, x1 + 0.26, yl1, yl1 + 0.1), hc, top, 'wall:stairwell')             # north, on the arch wall
    fill((x0, x0 + wt, ys0, ys1), hc, top, 'wall:stairwell')                     # west, above the hall ceiling
    fill((x0, x0 + wt, ys1, yl0), cz0, top, 'wall:stairwell')                    # west bulkhead over the lobby
    fill((x0, x0 + wt, yl0, yl1), sof, top, 'wall:stairwell')
    fill((x0, 0.65, ys0, ys0 + wt), hc, top, 'wall:stairwell')                   # south, above the stair foot
    fill((x0, x1, yl0, yl1), sof, lz, 'feat:stair_landing')                      # half-landing slab (soffit 2.60)
    fill((x0 - 0.05, x0 + 0.05, ys1, yw), 0, hc, 'feat:stair_corner_post')
    fill((x0, x1, yw, yw + 0.02), 2.07, cz0, 'feat:stair_boarding')              # T&G boarding above the door
    fill((x0 + wt, x1, yw, y14), cz0, tread(13) - 0.07, 'feat:lobby_overhead_cupboard')   # stays under the treads
    fill((x0 + wt, x1, y14, yl0), cz0, min(cz1, tread(14) - 0.07), 'feat:lobby_overhead_cupboard')


def _add_ceilings(g, ctx):
    """Ceiling slab cells above every room-void column that is open to the sky."""
    for rid in ctx.rooms:
        if rid not in g._ti:
            continue
        ti = g._ti[rid]
        tops = sorted({_r(v) for v in g.c[2][1:][((g.void == ti) & (g.solid == 0)).any(axis=(0, 1))]})
        for zc in tops:
            k = int(np.searchsorted(g.c[2], zc))                 # first cell above zc
            if k >= g.solid.shape[2]:
                continue
            below = (g.void[:, :, k - 1] == ti) & (g.solid[:, :, k - 1] == 0)
            open_above = (g.solid[:, :, k] == 0) & (g.void[:, :, k] == 0)
            k1 = int(np.searchsorted(g.c[2], _r(zc + CEIL_T)))
            for kk in range(k, k1):
                col = below & open_above & (g.solid[:, :, kk] == 0)
                g.solid[:, :, kk][col] = g.t('ceil:' + rid)


# ------------------------------------------------------------------ faces -> labelled quads
def _label(ctx, st, vt, a, s, plane, mid):
    """(object name, material spec) for a unit face. st = solid tag, vt = tag of the void it faces
    (None = outside), a = axis, s = sign of the normal, plane = coordinate, mid = face centre."""
    if st.startswith('ceil:'):
        room = st[5:]
        return room + '.ceiling', (FINISHES[room]['ceiling'] if a == 2 and s < 0 and vt else EXT)
    if vt is None:
        return ('shell.wall_tops', TOPS) if a == 2 and s > 0 else ('shell.exterior', EXT)
    op = vt.startswith('op|')
    room = vt.split('|')[2] if op else vt
    F = FINISHES[room]
    if a == 2 and s > 0 and st == 'slab':
        return room + '.floor', ctx.rooms[room]['floor']['material']
    name = room + '.walls'
    if op:
        return name, WHITE                                        # reveal liners (jambs, head, sill)
    if st.startswith('feat:') and st[5:] in F['features']:
        return name, F['features'][st[5:]]
    if a == 2:
        return name, (F['ceiling'] if s < 0 else F['upper'])
    for o in F['faces']:
        if o['axis'] == a and abs(o['at'] - plane) < 2e-3:
            h = mid[1 - a]
            if ('range' not in o or o['range'][0] < h < o['range'][1]) and \
                    ('z' not in o or o['z'][0] < mid[2] < o['z'][1]):
                return name, o['mat']
    if F['wainscot'] and mid[2] < F['wainscot'][0]:
        return name, F['wainscot'][1]
    sz = split_z(room)
    return name, (F['lower'] if sz is not None and mid[2] < sz else F['upper'])


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
    """-> {object name: [(4 corner coords, axis, material spec), ...]}"""
    labels, lab_i, out = [], {}, {}
    mids = [(c[:-1] + c[1:]) / 2 for c in g.c]
    is_ceil = np.array([bool(t) and t.startswith('ceil:') for t in g.tags])
    for group in (False, True):                                   # structure, then ceilings
        S = (g.solid > 0) & (is_ceil[g.solid] == group)
        for a in range(3):
            ua, va = (a + 1) % 3, (a + 2) % 3
            for s in (1, -1):
                nb = np.zeros_like(S)                             # neighbour in direction s is also in S
                src = [slice(None)] * 3
                dst = [slice(None)] * 3
                src[a], dst[a] = (slice(1, None), slice(None, -1)) if s > 0 else (slice(None, -1), slice(1, None))
                nb[tuple(dst)] = S[tuple(src)]
                planes = {}
                for idx in np.argwhere(S & ~nb):
                    i = tuple(int(v) for v in idx)
                    j = list(i)
                    j[a] += s
                    inside = 0 <= j[a] < S.shape[a]
                    if group and inside and g.solid[tuple(j)]:
                        continue                                  # ceiling edge buried in a wall
                    vt =g.tags[g.void[tuple(j)]] if inside and g.solid[tuple(j)] == 0 else None
                    p = i[a] + (1 if s > 0 else 0)
                    mid = [mids[0][i[0]], mids[1][i[1]], mids[2][i[2]]]
                    lab = _label(ctx, g.tags[g.solid[i]], vt, a, s, g.c[a][p], mid)
                    li = lab_i.setdefault(lab, len(labels))
                    if li == len(labels):
                        labels.append(lab)
                    L = planes.get(p)
                    if L is None:
                        L = planes[p] = np.full((S.shape[ua], S.shape[va]), -1, np.int32)
                    L[i[ua], i[va]] = li
                for p, L in planes.items():
                    for u0, u1, v0, v1, li in _greedy(L):
                        name, spec = labels[li]
                        cs = []
                        for uu, vv in ((u0, v0), (u1, v0), (u1, v1), (u0, v1)):
                            pt = [0.0, 0.0, 0.0]
                            pt[a], pt[ua], pt[va] = g.c[a][p], g.c[ua][uu], g.c[va][vv]
                            cs.append(tuple(float(x) for x in pt))
                        out.setdefault(name, []).append((cs if s > 0 else cs[::-1], a, spec))
    return out


def _uv(p, a, rot=False):
    if a == 0:
        return p[1], p[2]
    if a == 1:
        return p[0], p[2]
    return (p[1], p[0]) if rot else (p[0], p[1])


def _mesh_object(name, quads, rot=False):
    """quads: [(corners, uv axis, material spec)] -> object with welded verts, UVMap, material slots."""
    vi, verts, faces, mi, uvs, specs = {}, [], [], [], [], []
    for cs, a, spec in quads:
        faces.append([vi.setdefault(c, len(vi)) for c in cs])
        if spec not in specs:
            specs.append(spec)
        mi.append(specs.index(spec))
        for c in cs:
            uvs.extend(_uv(c, a, rot))
    verts = sorted(vi, key=vi.get)
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    for spec in specs:
        me.materials.append(material(spec))
    me.polygons.foreach_set('material_index', mi)
    me.uv_layers.new(name='UVMap').data.foreach_set('uv', uvs)
    me.update()
    return bpy.data.objects.new(name, me)


# ------------------------------------------------------------------ curved infill, thresholds, ground
def _fan_prism(name, pieces, y0, y1, spec):
    """pieces: [((cx, cz), [(x, z), ...arc], (vx, vz), [extra (x, z)...])]. Each piece is the fan
    corner->arc(+extra) extruded y0..y1; emits both end faces and the curved intrados along arc, whose
    normals face the void point v (the faces against the wall are left out)."""
    bm = bmesh.new()
    uv = bm.loops.layers.uv.new('UVMap')

    def face(pts, want):
        f = bm.faces.new([bm.verts.new(p) for p in pts])
        f.normal_update()
        if f.normal.dot(want) < 0:
            f.normal_flip()
        horiz = abs(f.normal.y) < 0.5
        for l in f.loops:
            l[uv].uv = (l.vert.co.x, l.vert.co.y) if horiz else (l.vert.co.x, l.vert.co.z)
        f.smooth = horiz
    for (cx, cz), arc, (vx, vz), extra in pieces:
        ring = arc + extra
        for (xa, za), (xb, zb) in zip(ring, ring[1:]):
            face([(cx, y0, cz), (xa, y0, za), (xb, y0, zb)], (0, -1, 0))
            face([(cx, y1, cz), (xa, y1, za), (xb, y1, zb)], (0, 1, 0))
        for (xa, za), (xb, zb) in zip(arc, arc[1:]):
            mx, mz = (xa + xb) / 2, (za + zb) / 2
            face([(xa, y0, za), (xb, y0, zb), (xb, y1, zb), (xa, y1, za)], (vx - mx, 0, vz - mz))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(material(spec))
    return bpy.data.objects.new(name, me)


def _curved(ctx):
    N = 12
    for f in ctx.features:
        if f['type'] == 'arch':                                   # segmental arch in a wall along X
            o = ctx.openings[f['opening']]
            w = ctx.walls[o['wall']]
            assert abs(w['a'][1] - w['b'][1]) < 1e-6, 'arch infill only implemented for walls along X'
            xa, xb = o['center'][0] - o['width'] / 2, o['center'][0] + o['width'] / 2
            zs, zc = f['springing'], f['crown']
            zt = zc + ARCH_PAD
            hs, rise, xm = (xb - xa) / 2, zc - zs, (xa + xb) / 2
            R = (hs * hs + rise * rise) / (2 * rise)
            th0 = math.asin(min(1.0, hs / R))
            arc = lambda sg: [(xm + sg * R * math.sin(th0 * (1 - i / N)), zc - R + R * math.cos(th0 * (1 - i / N)))
                              for i in range(N + 1)]
            _, _, y0, y1 = wall_rect(ctx, w)
            room = f['room']
            ob = _fan_prism(room + '.arch_fill', [((xa, zt), arc(-1), (xm, zs), [(xm, zt)]), ((xb, zt), arc(1), (xm, zs), [(xm, zt)])], y0, y1,
                            FINISHES[room]['upper'])
            ctx.add(ob, room, 'shell')
        elif f['type'] == 'arch_vault':                           # basket vault: quarter-round haunches
            x0, x1, y0, y1 = _bounds(f['polygon'])
            zs, zc, cz = f['springing'], f['crown'], ctx.ceil_z(f['room'])
            r = zc - zs
            hp = lambda xp, sg: [(xp - sg * r * (1 - math.cos(math.pi / 2 * i / N)), zs + r * math.sin(math.pi / 2 * i / N))
                                 for i in range(N + 1)]
            room = f['room']
            ob = _fan_prism(room + '.vault_fill', [((x0, cz), hp(x0, -1), (x0 + r, zs), [(x0 + r, cz)]), ((x1, cz), hp(x1, 1), (x1 - r, zs), [(x1 - r, cz)])], y0, y1,
                            FINISHES[room]['upper'])
            ctx.add(ob, room, 'shell')


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


def _thresholds(ctx):
    """Hardwood bar under the door line wherever two different floor finishes meet."""
    for oid, o in ctx.openings.items():
        a, b = o['connects']
        if a not in ctx.rooms or b not in ctx.rooms or 'door' not in o['type']:
            continue
        if ctx.rooms[a]['floor']['material'] == ctx.rooms[b]['floor']['material']:
            continue
        f = ctx.opening_frame(oid)
        # inner (mahogany) screen: flush 100 mm mahogany sill (vestibule.md, f_0026); elsewhere a 75 x 8 hardwood bar
        wd, th, key = (0.100, 0.002, 'mahogany') if str(o.get('style', '')).startswith('mahogany') else (0.075, 0.008, 'hardwood_threshold')
        c, al, hw, d = f['center'], f['along'], f['width'] / 2, min(wd, f['wall_thickness']) / 2
        ex, ey = abs(al.x) * hw + abs(al.y) * d, abs(al.y) * hw + abs(al.x) * d
        ob = box(f'shell.threshold.{oid}', c.x - ex, c.x + ex, c.y - ey, c.y + ey, c.z, c.z + th, key)
        M.uv_box(ob, rotate=abs(al.x) > 0.5)                      # grain along the bar
        ctx.add(ob, 'shell', 'shell')


def _ground(ctx):
    """Big outdoor ground plane (daylight bounce, something to see through the windows). Not for export."""
    B = ctx.spec['bounds']
    z = next((f['z'] for f in ctx.features if f['type'] == 'outside_yard'), -SLAB)
    ob = box('shell.ground', B['minX'] - 15, B['maxX'] + 15, B['minY'] - 15, B['maxY'] + 15, z - 0.05, z - 0.001, '#77746C')
    ctx.add(ob, 'shell', 'shell', lm='dynamic')
    ob['no_export'] = True


# ------------------------------------------------------------------ helpers for other modules
def wall_runs(ctx, room, z=0.05):
    """Outline of the room's clear space at height z (piers, pilasters, breast, boxing included), as
    closed loops of straight runs walked with the ROOM ON THE LEFT (outer boundary = counter-clockwise).
    -> [[((ax, ay), (bx, by), kind, opening_id), ...], ...]; kind 'wall' = solid behind the run,
    'open' = door/window hole or open boundary (opening_id is None for the latter)."""
    g = ctx.grid
    k = g.k_at(z)
    R = (g.void[:, :, k] == g._ti[room]) & (g.solid[:, :, k] == 0)
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
            pa, pb = (float(X[a[0]]), float(Y[a[1]])), (float(X[b[0]]), float(Y[b[1]]))
            if loop and loop[-1][2:] == (kind, oid) and (loop[-1][0][0] == pb[0] or loop[-1][0][1] == pb[1]):
                loop[-1] = (loop[-1][0], pb, kind, oid)
            else:
                loop.append((pa, pb, kind, oid))
            a = b
        if len(loop) > 1 and loop[0][2:] == loop[-1][2:] and (loop[-1][0][0] == loop[0][1][0] or loop[-1][0][1] == loop[0][1][1]):
            loop[0] = (loop[-1][0], loop[0][1], *loop[0][2:])
            loop.pop()
        loops.append(loop)
    return loops


def surface(room, part='walls'):
    """Shell object of a room: part in walls | floor | ceiling (plus arch_fill / vault_fill where present)."""
    return bpy.data.objects.get(f'{room}.{part}')


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


# ------------------------------------------------------------------ entry point
def build(ctx):
    ops = _ops(ctx)
    xs, ys, zs = set(), set(), {r['ceilingZ'] + CEIL_T for r in ctx.rooms.values()}
    for rid, F in FINISHES.items():
        zs.update(z for z in (split_z(rid), F['wainscot'] and F['wainscot'][0]) if z)
        for o in F['faces']:
            (ys if o['axis'] == 0 else xs).update(o.get('range', ()))
            zs.update(o.get('z', ()))
    g = ctx.grid = Grid(ops, (xs, ys, zs))
    _add_ceilings(g, ctx)
    n = 0
    for name, qs in sorted(_quads(g, ctx).items()):
        room, part = name.split('.')
        rot = part == 'floor' and ctx.rooms[room]['floor'].get('direction') == 'x'
        ob = ctx.add(_mesh_object(name, qs, rot), room, 'shell')
        ob['part'] = part
        M.uv_box(ob, rotate=rot, origin=FLOOR_ORIGIN.get(room, (0, 0, 0)) if part == 'floor' else (0, 0, 0))
        n += len(qs)
        if part == 'floor':                                       # self-check: floor covers the room polygon
            area = sum(abs((c[2][0] - c[0][0]) * (c[2][1] - c[0][1])) for c, _, _ in qs)
            want = sum((x1 - x0) * (y1 - y0) for x0, x1, y0, y1 in poly_rects(ctx.room_poly(room)))
            assert area > 0.85 * want, f'{name}: floor area {area:.2f} < polygon {want:.2f}'
    _curved(ctx)
    _thresholds(ctx)
    _ground(ctx)
    print(f'[shell] grid {g.solid.shape}, {n} quads, {len(ctx.col("shell").objects)} objects')
    _install(ctx)


def _install(ctx):
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
    try:                                         # ImportError/AttributeError = module not written (yet)
        from . import joinery
        fn = joinery.install_openings
    except (ImportError, AttributeError) as e:
        print(f'[shell] joinery.install_openings missing ({e}) - openings left bare')
    else:
        call('joinery.install_openings', fn, ctx)
    try:
        from . import mouldings
        fn = mouldings.install_room_trim
    except (ImportError, AttributeError) as e:
        print(f'[shell] mouldings.install_room_trim missing ({e}) - no skirting/dado/cornice')
    else:
        for rid in ctx.rooms:
            call(f'mouldings.install_room_trim({rid})', fn, ctx, rid)

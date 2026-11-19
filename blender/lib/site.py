"""Site (owner: site; blender/MULTILEVEL.md section 6): everything outside the house that is not its envelope.

    from lib import site
    site.build(ctx)             # ground zones, steps, boundaries, side gate, shed shell, neighbours, backdrop
    site.surface('deck')        # the ground object of a zone

Everything is read from ctx.spec['exterior']; the tables below only add what the json does not carry (how a fence or
a wall of a given material is put together, shed finishes). Notes: blender/lib/README.md.
"""
import math
from bisect import bisect_left
from collections import Counter

import bmesh
import bpy
import numpy as np
from mathutils.geometry import delaunay_2d_cdt

from . import ctx as C
from . import interact as IX
from . import materials as M

THICK = 0.10                    # a zone slab reaches this far below the lowest ground it stands proud of
ZONE_MAT = {s: s for s in (     # zone `surface` -> lib.materials key (d owns the textures)
    'asphalt', 'clay_block_paving_red_herringbone', 'composite_deck_dark_brown', 'concrete_flags',
    'concrete_or_flags', 'concrete_setts_grey_buff', 'grass', 'sandstone_flags_grey', 'soil_lavender',
    'timber_box_dark')}
EDGE_MAT = {'composite_deck_dark_brown': 'timber_box_dark'}     # exposed sides: the deck's fascia boards
ROT = {'composite_deck_dark_brown', 'timber_box_dark'}          # textures have boards along V; these run E-W / level
KERB = {'concrete_flags': '#8A8A88'}                            # 150 mm kerb stones where the footway stands proud
DRAINS = {'passage_step': 0.13}                                 # channel drain at the foot of a `line` step: width
NOSE = 0.015                                                    # tread flags oversail their risers
# brick, mortar: soldier bricks are modelled, so they need the plain colours of the textured brick they sit in
BRICK = {'buff_brick': ('#C9B58C', '#CFC6B0'), 'red_brick': ('#A8624A', '#C9BA8E'),
         'stock_brick_yellow': ('#C2AE85', '#D8CFBD'), 'stock_brick_grey': ('#A99873', '#8E866F')}
CONC, STONE, LEAD, BLACK, GALV = '#A8A49C', '#9A958A', '#3F4245', '#1C1C1E', 'silver_satin'
# fences by material: rails on our side (+1) or the far side (-1); trellis topper (m) on the bays beside that zone
FENCE = {'closeboard_grey_painted': dict(rails=-1, trellis=('deck', 0.30)), 'closeboard_brown': dict(rails=1)}
BAY, POST = 1.83, 0.10
GATE_DEG, GATE_POST = 50, 0.095                                 # state-1 angle (contract), goal-post section
EXT_DEPTH = 5.5                                                 # a neighbour_wall with no massing behind it gets this
SOFFIT = 'mahogany_dark'                                        # shed veranda: stained T&G boards
SHED_FIN = {'shed_workshop': dict(walls='#EFEEEA', ceiling='#EFEEEA', floor='vinyl_grey_sheet')}
ROOF_FALL = 0.07                                                # shed felt roof falls to the front gutter
EXPORT_BACKDROP = False                                         # True: the backdrop ground is exported too
MISSING = set()
_SURF = {}
AX = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))


def _mat(key):
    """'#RRGGBB' -> matt paint, else a lib.materials key; an unknown key logs once and renders grey."""
    if key.startswith('#'):
        return M.paint(key)
    try:
        return M.mat(key)
    except KeyError:
        if key not in MISSING:
            print(f'[site] WARNING: unknown material {key!r}, grey fallback')
            MISSING.add(key)
        return M.paint('#8A8A88')


def _shade(hx, f):
    return '#' + ''.join(f'{min(255, max(0, round(int(hx[i:i + 2], 16) * f))):02X}' for i in (1, 3, 5))


def _tone(key):
    """Plain colour of a textured material (for rails and cappings, where its board lines would run the wrong way)."""
    return M.MANIFEST.get(key, {}).get('target', '#9A9A96')


# ---- 2D helpers
def _ccw(poly):
    poly = [tuple(p) for p in poly]
    return poly if C.poly_area(poly) > 0 else poly[::-1]


def _edges(poly):
    return zip(poly, poly[1:] + poly[:1])


def _bbox(poly):
    xs, ys = zip(*poly)
    return min(xs), min(ys), max(xs), max(ys)


def _dir(a, b):
    ln = math.hypot(b[0] - a[0], b[1] - a[1])
    return ((b[0] - a[0]) / ln, (b[1] - a[1]) / ln), ln


def _yaw(u):
    """Local frame of a run: x along u, y to its left, z up."""
    return ((u[0], u[1], 0.0), (-u[1], u[0], 0.0), (0.0, 0.0, 1.0))


def edge_dist(x, y, poly):
    """Distance from a point to the boundary of a polygon."""
    d = 9e9
    for (x0, y0), (x1, y1) in _edges([tuple(p) for p in poly]):
        dx, dy = x1 - x0, y1 - y0
        t = min(1.0, max(0.0, ((x - x0) * dx + (y - y0) * dy) / ((dx * dx + dy * dy) or 1.0)))
        d = min(d, math.hypot(x - x0 - t * dx, y - y0 - t * dy))
    return d


def _house_polys(ctx):
    """Plan areas the site must stay out of: the ground-floor envelope and the garden buildings."""
    ext = ctx.spec['exterior']
    return [lv['polygon'] for b in ext['envelope']['blocks'] for lv in b['levels'] if lv['level'] == 'G'] + \
           [b['outline'] for b in ext.get('buildings', [])]


def _low(ctx, pts, default):
    zs = [z for z in (ctx.ground_z(x, y) for x, y in pts) if z is not None]
    return min(zs) if zs else default


# ---- mesh accumulator
class _Mesh:
    """Faces with outward normals and one material key each -> one object."""

    def __init__(self, weld=False):
        self.v, self.f, self.k, self.ix = [], [], [], {} if weld else None

    def vert(self, p):
        p = (float(p[0]), float(p[1]), float(p[2]))
        if self.ix is None:
            self.v.append(p)
            return len(self.v) - 1
        k = (round(p[0], 4), round(p[1], 4), round(p[2], 4))
        if k not in self.ix:
            self.ix[k] = len(self.v)
            self.v.append(p)
        return self.ix[k]

    def face(self, pts, key):
        self.f.append([self.vert(p) for p in pts])
        self.k.append(key)

    def box(self, lo, hi, key, org=(0.0, 0.0, 0.0), ax=AX, only=None, keys=None):
        """Box lo..hi in the right-handed frame ax at org. only = faces to emit ('+x', '-z', ...); keys = per-face
        material overrides, e.g. {'+z': 'flat_felt'}."""
        def p(i, j, k):
            c = ((lo, hi)[i][0], (lo, hi)[j][1], (lo, hi)[k][2])
            return tuple(org[d] + sum(c[a] * ax[a][d] for a in range(3)) for d in range(3))
        c = [p(i, j, k) for i in (0, 1) for j in (0, 1) for k in (0, 1)] if self.ix is None else None
        ids = None if c is None else [self.vert(q) for q in c]
        quads = {'-z': ((0, 1, 0), (1, 1, 0), (1, 0, 0), (0, 0, 0)), '+z': ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)),
                 '-y': ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)), '+y': ((1, 1, 0), (0, 1, 0), (0, 1, 1), (1, 1, 1)),
                 '-x': ((0, 1, 0), (0, 0, 0), (0, 0, 1), (0, 1, 1)), '+x': ((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1))}
        for d, q in quads.items():
            if only and d not in only:
                continue
            self.f.append([ids[i * 4 + j * 2 + k] for i, j, k in q] if ids else [self.vert(p(*t)) for t in q])
            self.k.append((keys or {}).get(d, key))

    def prism(self, poly, z0, z1, key, top=None, ends=True):
        """Vertical prism over a polygon (any winding); top = material of the upper face."""
        poly = _ccw(poly)
        for a, b in _edges(poly):
            self.face([(*a, z0), (*b, z0), (*b, z1), (*a, z1)], key)
        if ends:
            self.face([(*q, z1) for q in poly], top or key)

    def tube(self, a, b, r, key, n=8, arc=(0.0, 2 * math.pi), up=(0.0, 0.0, 1.0)):
        """Round bar from a to b (n sides); arc < 2 pi gives a solid segment (half-round gutter) closed by a chord."""
        ax = np.subtract(b, a)
        ax = ax / np.linalg.norm(ax)
        e1 = np.cross(up, ax)
        e1 = e1 / np.linalg.norm(e1)
        e2 = np.cross(ax, e1)
        ring = [(math.cos(t) * e1 + math.sin(t) * e2) * r
                for t in (arc[0] + (arc[1] - arc[0]) * i / n for i in range(n + (arc[1] - arc[0] < 6.2)))]
        for i in range(len(ring)):
            p, q = ring[i], ring[(i + 1) % len(ring)]
            self.face([a + p, a + q, b + q, b + p], key)
        self.face([b + p for p in ring], key)
        self.face([a + p for p in reversed(ring)], key)

    def obj(self, ctx, name, room, kind='shell', rot=False, bevel=0.0, dissolve=False, origin=(0.0, 0.0, 0.0)):
        """origin = world point where the texture starts (course and board joints register to it)."""
        me = bpy.data.meshes.new(name)
        me.from_pydata(self.v, [], self.f)
        keys = list(dict.fromkeys(self.k))
        for k in keys:
            me.materials.append(_mat(k))
        me.polygons.foreach_set('material_index', [keys.index(k) for k in self.k])
        me.update()
        if bevel or dissolve:
            bm = bmesh.new()
            bm.from_mesh(me)
            if dissolve:        # grid cells -> one polygon per flat surface
                bmesh.ops.dissolve_limit(bm, angle_limit=0.002, verts=bm.verts, edges=bm.edges, delimit={'MATERIAL'})
            if bevel:
                bmesh.ops.bevel(bm, geom=bm.edges[:], offset=bevel, segments=1, profile=0.5, affect='EDGES')
            bm.to_mesh(me)
            bm.free()
        assert name not in bpy.data.objects, f'site: duplicate object name {name}'
        ob = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(ob)
        M.uv_box(ob, rotate=rot, origin=origin)
        return ctx.add(ob, room, kind)


# ---- ground
def _fall_pieces(z):
    """A zone polygon cut at both ends of its `fall`, so that every piece is one plane."""
    poly, fall = _ccw(z['polygon']), z.get('fall')
    if not fall:
        return [poly]
    (fx, fy), (tx, ty) = fall['from'], fall['to']
    px, py = fy - ty, tx - fx                           # left of the fall direction
    out, rest = [], poly
    for x, y in ((fx, fy), (tx, ty)):
        out.append(C.clip_poly(rest, (x, y), (x + px, y + py), left=True))
        rest = C.clip_poly(rest, (x, y), (x + px, y + py), left=False)
    return [p for p in out + [rest] if len(p) >= 3 and abs(C.poly_area(p)) > 1e-6]


def _proud(ctx, house, a, b, zf):
    """Edge a -> b of a CCW polygon whose top is zf(x, y): the lowest ground 5 mm outside it wherever the edge stands
    proud (open ground with no zone counts as the edge's own level); None when nothing outside is lower."""
    (ux, uy), ln = _dir(a, b)
    n = max(2, int(ln / 0.25) + 1)
    lows = []
    for i in range(n):
        x, y = a[0] + ux * ln * (i + 0.5) / n, a[1] + uy * ln * (i + 0.5) / n
        ox, oy = x + uy * 0.005, y - ux * 0.005
        if any(C.point_in_poly(ox, oy, h) for h in house):
            continue
        g, top = ctx.ground_z(ox, oy), zf(x, y)
        if g is None or g < top - 1e-3:
            lows.append(top if g is None else g)
    return min(lows) if lows else None


def _gaps(ctx, house):
    """Plot area that no zone, house or building covers (the spec leaves corners: beside the bay, the deck's NW
    notch), as triangles per zone: each connected patch goes to the lowest zone it shares an edge with, since ground
    runs under what stands higher."""
    polys = [_ccw(p) for p in [ctx.spec['exterior']['plot']['polygon']] +
             [z['polygon'] for z in ctx.zones.values()] + house]
    verts, faces = [], []
    for p in polys:
        faces.append(list(range(len(verts), len(verts) + len(p))))
        verts += p
    vo, _, fo, _, _, orig = delaunay_2d_cdt(verts, [], faces, 0, 1e-4)      # orig = input faces containing each triangle
    tris = [tri for tri, src in zip(fo, orig) if src == [0]]
    patch = {}                                                              # vertex index -> patch id (union by shared vertices)
    for tri in tris:
        ids = {patch[i] for i in tri if i in patch}
        for i in list(patch) if ids else ():
            if patch[i] in ids:
                patch[i] = min(ids)
        for i in tri:
            patch[i] = min(ids) if ids else tri[0]
    out, edge_zones = {}, {}
    for tri in tris:
        for i, j in _edges(list(tri)):
            mx, my = (vo[i] + vo[j]) / 2
            edge_zones.setdefault(patch[tri[0]], set()).update(
                zid for zid, z in ctx.zones.items() if edge_dist(mx, my, z['polygon']) < 2e-3)
    for tri in tris:
        zs, t = edge_zones[patch[tri[0]]], _ccw([tuple(vo[i]) for i in tri])
        if zs:
            out.setdefault(min(zs, key=lambda k: ctx.zone_z(k, *t[0])), []).append(t)
    for zid, ts in out.items():
        print(f'[site] spec gap: {sum(abs(C.poly_area(t)) for t in ts):.2f} m2 beside {zid} filled at its level')
    return out


def _zones(ctx, house):
    fills = _gaps(ctx, house)
    for zid, z in ctx.zones.items():
        key = ZONE_MAT.get(z['surface'], z['surface'])
        edge = EDGE_MAT.get(key, key)

        def zf(x, y, zid=zid):
            return ctx.zone_z(zid, x, y)
        pieces = _fall_pieces(z)
        used = Counter(frozenset((a, b)) for p in pieces for a, b in _edges(p))
        m, kerb, sides = _Mesh(), _Mesh(), []
        for p in pieces + fills.get(zid, []):
            m.face([(x, y, zf(x, y)) for x, y in p], key)
        for p in pieces:
            for a, b in _edges(p):
                low = None if used[frozenset((a, b))] > 1 else _proud(ctx, house, a, b, zf)
                if low is not None:
                    sides.append((a, b, low))
        bot = min([zf(*q) for p in pieces for q in p] + [s[2] for s in sides]) - THICK
        for a, b, low in sides:
            m.face([(*a, bot), (*b, bot), (*b, zf(*b)), (*a, zf(*a))], edge)
            if key in KERB and low < zf(*a) - 1e-3:         # kerb stones stand in the lower zone, level with this one
                u, ln = _dir(a, b)
                kerb.box((0, -0.15, low - THICK), (ln, 0, zf(*a)), KERB[key], org=(*a, 0), ax=_yaw(u))
        x0, y0, _, _ = _bbox(z['polygon'])                  # boards start at the zone's corner and top edge; paving
        org = (x0, y0, z['z']) if key in ROT else (0.0, 0.0, 0.0)   # keeps the world origin, so it runs on across zones
        _SURF[zid] = m.obj(ctx, f"{z['room']}.{zid}", z['room'], rot=key in ROT, origin=org).name
        if kerb.f:
            kerb.obj(ctx, f"{z['room']}.{zid}.kerb", z['room'])


def surface(zone_id):
    """The ground object of a zone (after build)."""
    return bpy.data.objects[_SURF[zone_id]]


def _steps(ctx, house):
    for s in ctx.spec['exterior'].get('steps', []):
        zone = ctx.zones[s['fromZone']]
        key = ZONE_MAT.get(zone['surface'], zone['surface'])
        if s.get('treads'):                                 # stone flags on riser blocks, lowest first
            m = _Mesh()
            for t in sorted(s['treads'], key=lambda t: t['z']):
                x0, y0, x1, y1 = _bbox(t['polygon'])
                rect = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
                show = [_proud(ctx, house, a, b, lambda x, y: t['z']) is not None for a, b in _edges(rect)]
                dirs = [d for d, on in zip(('-y', '+x', '+y', '-x'), show) if on]
                n = [NOSE * on for on in show]
                if dirs:
                    m.box((x0, y0, zone['z'] - 0.05), (x1, y1, t['z'] - 0.04), key, only=dirs)
                m.box((x0 - n[3], y0 - n[0], t['z'] - 0.04), (x1 + n[1], y1 + n[2], t['z']), key, only=dirs + ['+z', '-z'])
            m.obj(ctx, f"{zone['room']}.{s['id']}", zone['room'])
        if s['id'] in DRAINS and s.get('line'):             # slotted channel in the lower zone along the riser
            a, b = s['line']
            u, _ = _dir(a, b)
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            sg = 1 if C.poly_contains(mx - u[1] * 0.05, my + u[0] * 0.05, zone['polygon']) else -1
            ox, oy = -u[1] * DRAINS[s['id']] * sg, u[0] * DRAINS[s['id']] * sg
            strip = C.clip_poly(_ccw(zone['polygon']), (a[0] + ox, a[1] + oy), (b[0] + ox, b[1] + oy), left=sg < 0)
            m = _Mesh()
            m.prism(strip, zone['z'] - 0.02, zone['z'] + 0.003, BLACK)      # ponytail: plain strip, slots are a texture job
            m.obj(ctx, f"{zone['room']}.{s['id']}.drain", zone['room'])


# ---- boundaries
def _soldiers(m, org, ax, s0, s1, n0, n1, z0, z1, brick, mortar=None, seed=0):
    """A course of bricks on end (65 mm faces at 75 mm centres) with real joints; mortar = hex of a recessed core."""
    if mortar:
        m.box((s0, n0 + 0.004, z0), (s1, n1 - 0.004, z1 - 0.004), mortar, org=org, ax=ax)
    n = max(1, round((s1 - s0) / 0.075))
    p = (s1 - s0) / n
    for i in range(n):
        tone = _shade(brick, (0.94, 1.0, 1.05, 0.98, 1.02)[(i * 7 + seed) % 5])
        m.box((s0 + i * p + 0.005, n0, z0), (s0 + (i + 1) * p - 0.005, n1, z1), tone, org=org, ax=ax)


def _wall(ctx, b):
    """Garden wall: stretcher courses by texture under a soldier course."""
    a, e = b['line']
    (u, ln), t, top = _dir(a, e), b['thickness'], b['baseZ'] + b['height']
    bot = _low(ctx, [(a[0] + u[0] * s - u[1] * d, a[1] + u[1] * s + u[0] * d)
                     for s in (0.05, ln / 2, ln - 0.05) for d in (-t / 2 - 0.02, t / 2 + 0.02)], b['baseZ']) - 0.05
    brick, mortar = BRICK[b['material']]
    m = _Mesh()
    m.box((0, -t / 2, bot), (ln, t / 2, top - 0.225), b['material'], org=(*a, 0), ax=_yaw(u), only=('-x', '+x', '-y', '+y'))
    _soldiers(m, (*a, 0), _yaw(u), 0, ln, -t / 2, t / 2, top - 0.225, top, brick, mortar)
    m.obj(ctx, f"{b['room']}.{b['id']}", b['room'], origin=(a[0], a[1], top - 0.225))


def _pier(ctx, b):
    x0, y0, x1, y1 = _bbox(b['polygon'])
    top = b['baseZ'] + b['height']
    bot = _low(ctx, [(x, y) for x in (x0 - 0.02, x1 + 0.02) for y in (y0 - 0.02, y1 + 0.02)], b['baseZ']) - 0.05
    m = _Mesh()
    m.box((x0, y0, bot), (x1, y1, top - 0.075), b['material'], only=('-x', '+x', '-y', '+y'))
    m.obj(ctx, f"{b['room']}.{b['id']}", b['room'], origin=(x0, y0, top - 0.075))
    cap = _Mesh()
    cap.box((x0 - 0.035, y0 - 0.035, top - 0.075), (x1 + 0.035, y1 + 0.035, top), STONE)
    cap.obj(ctx, f"{b['room']}.{b['id']}.cap", b['room'], bevel=0.006)


def _snap(ctx, p):
    """A fence end within 0.3 m of a garden building is carried on to it."""
    best = (0.3, tuple(p))
    for bd in ctx.spec['exterior'].get('buildings', []):
        for a, b in _edges(_ccw(bd['outline'])):
            (u, ln) = _dir(a, b)
            s = min(ln, max(0.0, (p[0] - a[0]) * u[0] + (p[1] - a[1]) * u[1]))
            q = (a[0] + u[0] * s, a[1] + u[1] * s)
            best = min(best, (math.hypot(q[0] - p[0], q[1] - p[1]), q))
    return best[1]


def _fence(ctx, b, gate_ends):
    """Closeboard fence: concrete posts and gravel boards, boarded panels (boards by texture), arris rails, capping,
    and a lattice topper on the bays its style names."""
    st, key = FENCE[b['material']], b['material']
    a, e = tuple(b['line'][0]), _snap(ctx, b['line'][1])
    (u, ln), top = _dir(a, e), b['baseZ'] + b['height']
    ax, org, tone = _yaw(u), (*a, 0), _tone(key)
    mx, my = (a[0] + e[0]) / 2, (a[1] + e[1]) / 2
    ours = 1 if C.point_in_poly(mx - u[1] * 0.3, my + u[0] * 0.3, ctx.spec['exterior']['plot']['polygon']) else -1
    nb = max(1, round(ln / BAY))
    bay, h = ln / nb, POST / 2
    start = any(math.hypot(a[0] - g[0], a[1] - g[1]) < 0.05 for g in gate_ends)     # the gate's latch post stands here

    def at(s, d):
        return a[0] + u[0] * s - u[1] * d, a[1] + u[1] * s + u[0] * d
    panels, posts, trel, tops = _Mesh(), _Mesh(), _Mesh(), [top] * (nb + 1)
    for i in range(nb):
        s0, s1 = i * bay + (POST if start and i == 0 else h), (i + 1) * bay - h
        g = _low(ctx, [at(s, ours * 0.1) for s in (s0, (s0 + s1) / 2, s1)], b['baseZ'])
        posts.box((s0, -0.025, g - 0.05), (s1, 0.025, g + 0.15), CONC, org=org, ax=ax)          # gravel board
        panels.box((s0, -0.011, g + 0.15), (s1, 0.011, top - 0.03), key, org=org, ax=ax)
        panels.box((s0, -0.03, top - 0.03), (s1, 0.03, top), tone, org=org, ax=ax)              # capping
        r0, r1 = sorted((st['rails'] * ours * 0.011, st['rails'] * ours * 0.056))
        for zr in (g + 0.35, (g + top) / 2, top - 0.25):
            panels.box((s0, r0, zr - 0.035), (s1, r1, zr + 0.035), tone, org=org, ax=ax)
        zone, th = st.get('trellis', (None, 0.0))
        if zone and any(C.poly_contains(*at((s0 + s1) / 2, ours * d), ctx.zones[zone]['polygon']) for d in (0.4, 0.8, 1.2, 1.6)):
            tops[i] = tops[i + 1] = top + th
            for z0 in (top, top + th - 0.035):                                                  # frame rails
                trel.box((s0, -0.0175, z0), (s1, 0.0175, z0 + 0.035), tone, org=org, ax=ax)
            zc, half = top + th / 2, (th - 0.07) / 2
            for k in range(int((s1 - s0 - 2 * half) / 0.155) + 1):                              # diamond lattice, 30 x 8 laths
                o = (*at(s0 + half + 0.01 + k * 0.155, 0), zc)                                  # ponytail: no half laths at the bay ends
                for sg in (1, -1):
                    ex = np.array((u[0], u[1], sg)) * 0.7071
                    ey = np.array(ax[1])
                    trel.box((-half * 1.4142, min(0, -0.008 * sg), -0.015), (half * 1.4142, max(0, -0.008 * sg), 0.015),
                             tone, org=o, ax=(ex, ey, np.cross(ex, ey)))
    for i in range(nb + 1):
        if start and i == 0:
            continue
        s = min(max(i * bay, h), ln - h)
        g = _low(ctx, [at(s, ours * 0.1)], b['baseZ'])
        posts.box((s - h, -h, g - 0.05), (s + h, h, tops[i] + 0.02), CONC, org=org, ax=ax)
    name = f"{b['room']}.{b['id']}"
    panels.obj(ctx, name, b['room'])
    posts.obj(ctx, name + '.posts', b['room'], bevel=0.008)
    if trel.f:
        trel.obj(ctx, name + '.trellis', b['room'])


def _gate(ctx, b):
    """Ledged-and-braced gate in a goal-post frame. Frame coordinates: s along the line from the hinge end, n > 0 on
    the side it opens to. The hinge post stands 50 mm off the wall behind the leaf plane (clear of the house and of
    the step beside it), so the pivot is 0.155 m along the line from `hingeAt`."""
    a, e = (tuple(p) for p in b['line'])
    if math.dist(a, b['hingeAt']) > math.dist(e, b['hingeAt']):
        a, e = e, a
    u, ln = _dir(a, e)
    into = ctx.zones[b['swingInto']]['polygon']
    sg = 1 if C.poly_contains((a[0] + e[0]) / 2 - u[1] * 0.2, (a[1] + e[1]) / 2 + u[0] * 0.2, into) else -1
    g, pw, tone = b['baseZ'], GATE_POST, _tone(b['material'])
    s_piv, s_end, head = 0.05 + pw + 0.01, ln - 0.004, g + 1.95
    piv = (a[0] + u[0] * s_piv, a[1] + u[1] * s_piv)

    def box(m, lo, hi, key):
        n0, n1 = sorted((lo[1] * sg, hi[1] * sg))               # n is measured to the left of the line in _yaw
        m.box((lo[0], n0, lo[2]), (hi[0], n1, hi[2]), key, org=(*a, 0), ax=_yaw(u))
    fr = _Mesh()
    box(fr, (0.05, -pw, g - 0.05), (0.05 + pw, 0.0, head), tone)                    # hinge post
    box(fr, (ln + 0.006, -0.07, g - 0.05), (ln + 0.006 + pw, 0.025, head), tone)    # latch post, beyond the leaf's reach
    box(fr, (0.05 + pw, -0.07, head - 0.07), (ln + 0.006, 0.0, head), tone)         # head rail
    fr.obj(ctx, f"{b['room']}.{b['id']}.frame", b['room'], bevel=0.004)
    # the leaf clears by 20 mm whatever ground and treads it sweeps over on the way to GATE_DEG
    base = math.atan2(u[1], u[0])
    sweep = [(piv[0] + r * math.cos(base + sg * math.radians(d)), piv[1] + r * math.sin(base + sg * math.radians(d)))
             for d in range(0, GATE_DEG + 1, 2) for r in np.arange(0.03, s_end - s_piv + 0.03, 0.03)]
    z0 = max(z for z in (ctx.ground_z(x, y) for x, y in sweep) if z is not None) + 0.02
    z1 = min(z0 + b['height'], head - 0.09)
    m = _Mesh()
    l0, l1 = s_piv + 0.005, s_end
    box(m, (l0, -0.022, z0), (l1, 0.0, z1), b['material'])                          # boards (joints by texture)
    ledges = (z0 + 0.15, (z0 + z1) / 2 - 0.05, z1 - 0.25)
    for zl in ledges:
        box(m, (l0 + 0.01, 0.0, zl), (l1 - 0.01, 0.03, zl + 0.10), tone)
        box(m, (l0 - 0.004, 0.03, zl + 0.03), (l0 + 0.32, 0.034, zl + 0.07), GALV)  # T-hinge strap
    u3, n3 = np.array((u[0], u[1], 0.0)), np.array((-u[1], u[0], 0.0)) * sg
    for za, zb in zip(ledges, ledges[1:]):                                          # braces rise from the hinge side
        ds, dz = l1 - l0 - 0.12, zb - za - 0.10
        ex = (u3 * ds + np.array((0, 0, dz))) / math.hypot(ds, dz)
        o = np.array((*a, 0.0)) + u3 * (l0 + l1) / 2 + np.array((0, 0, (za + zb) / 2 + 0.05))
        m.box((-math.hypot(ds, dz) / 2 + 0.03, 0.0, -0.045), (math.hypot(ds, dz) / 2 - 0.03, 0.028, 0.045), tone,
              org=o, ax=(ex, n3, np.cross(ex, n3)))
    box(m, (l1 - 0.14, 0.0, g + 1.04), (l1 - 0.02, 0.03, g + 1.16), '#8E9093')      # long-throw lock
    box(m, (l1 - 0.10, 0.0, g + 0.72), (l1 - 0.04, 0.02, g + 0.78), BLACK)          # ring latch
    leaf = m.obj(ctx, f"{b['room']}.{b['id']}", b['room'], kind='joinery')
    IX.tag(leaf, 'hinge', label='Side gate', p=(piv[0], piv[1], z0), a=(0, 0, 1), deg=sg * GATE_DEG, blocks=b['id'])


def _neighbour_wall(ctx, b):
    """A neighbour's wall on our boundary: the massing box behind it if there is one, else a block of its own."""
    a, e = b['line']
    mid = ((a[0] + e[0]) / 2, (a[1] + e[1]) / 2)
    ext = ctx.spec['exterior']
    for nb in ext.get('neighbours', []):
        if C.poly_contains(*mid, nb['polygon'], 1e-3):
            return
    (u, ln), top = _dir(a, e), b['baseZ'] + b['height']
    away = -1 if C.point_in_poly(mid[0] - u[1] * 0.3, mid[1] + u[0] * 0.3, ext['plot']['polygon']) else 1
    lo, hi = sorted((0.0, away * EXT_DEPTH))
    m = _Mesh()
    m.box((0, lo, -0.6), (ln, hi, top), b['material'], org=(*a, 0), ax=_yaw(u), keys={'+z': 'flat_felt'}, only=('-x', '+x', '-y', '+y', '+z'))
    c0, c1 = sorted((-away * 0.03, away * 0.30))
    m.box((0, c0, top), (ln, c1, top + 0.05), STONE, org=(*a, 0), ax=_yaw(u))       # parapet coping
    m.obj(ctx, f"{b['room']}.{b['id']}", b['room'])


def _neighbours(ctx):
    """Plain massing, a yard between each neighbour and the street (else our open east side ends in a drop), and the
    backdrop ground with a hole under the house (it would cut through the basement)."""
    ext = ctx.spec['exterior']
    street = [z for z in ctx.zones.values() if z.get('group') == 'street']
    for nb in ext.get('neighbours', []):
        # one prism per part up to its `top` (a flat Z or a roof plane c0 / cx / cy); parts may overlap, the higher one
        # shows. Faces to the street (-Y) take `front.material` (and `front.upper.colour` above `front.upper.z`), a
        # part with `walls` takes that all round, everything else is stock brick. No parts: the plain box of old.
        m, front = _Mesh(), nb.get('front', {})
        for pt in nb.get('parts') or [dict(polygon=nb['polygon'], top=nb['z'][1])]:
            t = pt['top']
            zt = (lambda x, y, t=t: t['c0'] + t['cx'] * x + t['cy'] * y) if isinstance(t, dict) else (lambda x, y, t=t: float(t))
            poly = _ccw(pt['polygon'])
            for a, b in _edges(poly):
                street_face = (b[0] - a[0]) > 1e-6 and abs(b[1] - a[1]) < 1e-6          # ccw: this edge faces -Y
                key = pt.get('walls') or (front.get('material') if street_face else None) or 'stock_brick_grey'
                za, zb, up = zt(*a), zt(*b), front.get('upper') if street_face and 'walls' not in pt else None
                zm = min(up['z'], za, zb) if up else None
                if up:
                    m.face([(*a, -0.6), (*b, -0.6), (*b, zm), (*a, zm)], key)
                    m.face([(*a, zm), (*b, zm), (*b, zb), (*a, za)], up['colour'])
                else:
                    m.face([(*a, -0.6), (*b, -0.6), (*b, zb), (*a, za)], key)
            m.face([(*q, zt(*q)) for q in poly], pt.get('covering', 'flat_felt'))
        m.obj(ctx, f"neighbours.{nb['id']}", 'neighbours')
        x0, y0, x1, _ = _bbox(nb['polygon'])
        ys = max((_bbox(z['polygon'])[3] for z in street), default=y0)             # the street lies at -Y (BRIEF)
        if ys < y0:                                                                # 2 m under the block: parts may stand back
            yard = _Mesh()
            yard.box((x0, ys, -0.6), (x1, y0 + 2.0, max(z['z'] for z in street) + 0.02), 'asphalt', only=('-x', '+x', '-y', '+z'))
            yard.obj(ctx, f"neighbours.{nb['id']}.yard", 'neighbours')
    env = [p for bl in ext['envelope']['blocks'] for lv in bl['levels'] for p in lv['polygon']]
    hx0, hy0, hx1, hy1 = _bbox(env)
    px0, py0, px1, py1 = _bbox(ext['plot']['polygon'])
    cx, cy = (px0 + px1) / 2, (py0 + py1) / 2
    bx0, bx1, by0, by1 = cx - 30, cx + 30, cy - 40, cy + 40
    m = _Mesh()
    for x0, y0, x1, y1 in ((bx0, by0, hx0, by1), (hx1, by0, bx1, by1), (hx0, by0, hx1, hy0), (hx0, hy1, hx1, by1)):
        m.face([(x0, y0, -0.5), (x1, y0, -0.5), (x1, y1, -0.5), (x0, y1, -0.5)], '#6B6F63')
    ob = m.obj(ctx, 'neighbours.backdrop', 'neighbours')
    if not EXPORT_BACKDROP:
        ob['no_export'] = 1


# ---- garden building
def _shed(ctx, b):
    """Shell of a garden building: its outline as solid mass minus the rooms, the roofed veranda and the openings, on
    a grid of all their coordinates (so every face knows which void it looks into), then roof trim."""
    room, brick = b.get('room', b['id']), b['material']
    x0, y0, x1, y1 = _bbox(b['outline'])
    top, soffit, bot = b['roof']['topZ'], b['roof']['verandaSoffitZ'], b['datumZ'] - 0.18
    veranda = [z for z in ctx.zones.values() if z.get('room') == room]
    paving = ZONE_MAT.get(veranda[0]['surface'], veranda[0]['surface']) if veranda else brick
    voids = [('veranda', *_bbox(z['polygon']), bot - 1, soffit) for z in veranda]
    voids += [(r['id'], *_bbox(r['polygon']), r['floorZ'], r['ceilingZ']) for r in b['rooms']]
    heads = _Mesh()
    for o in b['openings']:
        fr = ctx.opening_frame(o['id'])
        (cx, cy, cz), al, out, t = fr['center'], fr['along'], fr['outward'], fr['wall_thickness']
        assert abs(al[0]) < 1e-6 or abs(al[1]) < 1e-6, f"site: shed opening {o['id']} is not axis-aligned"
        ztop, half = fr['z0'] + fr['top'], fr['width'] / 2
        for tag, d0, d1 in (('out:', t / 2, t / 2 - fr['ext_reveal']), ('in:', t / 2 - fr['ext_reveal'], -t / 2)):
            xs = sorted((cx - al[0] * half + out[0] * d0, cx + al[0] * half + out[0] * d1))
            ys = sorted((cy - al[1] * half + out[1] * d0, cy + al[1] * half + out[1] * d1))
            voids.append((tag + o['id'], xs[0], ys[0], xs[1], ys[1], cz, ztop))
        # soldier course over the head, 3 mm proud of the stretcher texture; under the veranda it stops at the soffit
        fx, fy = cx + out[0] * t / 2, cy + out[1] * t / 2
        under = any(C.poly_contains(fx + out[0] * 0.05, fy + out[1] * 0.05, z['polygon']) for z in veranda)
        zs = min(ztop + 0.225, soffit if under else top - 0.05)
        _soldiers(heads, (fx - out[1] * half, fy + out[0] * half, 0), _yaw((out[1], -out[0])), 0, 2 * half, -0.01, 0.003,
                  ztop, zs, BRICK[brick][0], seed=len(heads.f))
    # grid
    X, Y, Z = (sorted({round(min(hi, max(lo, v)), 4) for v in vs} | {lo, hi}) for lo, hi, vs in (
        (x0, x1, [c for v in voids for c in (v[1], v[3])]), (y0, y1, [c for v in voids for c in (v[2], v[4])]),
        (bot, top, [c for v in voids for c in (v[5], v[6])])))
    tags = ['solid', 'outside'] + [v[0] for v in voids]
    T = np.ones((len(X) + 1, len(Y) + 1, len(Z) + 1), int)             # one layer of 'outside' all round
    T[1:-1, 1:-1, 1:-1] = 0

    def span(A, lo, hi):
        return slice(bisect_left(A, round(max(A[0], lo), 4)) + 1, bisect_left(A, round(min(A[-1], hi), 4)) + 1)
    for i, v in enumerate(voids):
        T[span(X, v[1], v[3]), span(Y, v[2], v[4]), span(Z, v[5], v[6])] = i + 2
    doors = {o['id'] for o in b['openings'] if 'door' in o['type']}
    inner = {o['id']: next((r for r in o['connects'] if r != 'outside'), None) for o in b['openings']}

    def finish(tag, d):
        """(object suffix, material) of a face looking into void `tag` along d, or None."""
        if tag == 'outside':
            return None if d == '-z' else ('roof', 'flat_felt') if d == '+z' else ('walls', brick)
        if tag == 'veranda':
            return ('soffit', SOFFIT) if d == '-z' else ('walls', brick)
        kind, _, oid = tag.partition(':')
        rid = inner[oid] if oid else tag
        fin = SHED_FIN.get(rid, dict(walls=brick, ceiling=SOFFIT, floor=paving))
        short = rid.removeprefix(b['id'] + '_')
        if kind == 'out':
            return ('walls', paving if d == '+z' and oid in doors else brick)
        if oid:
            return (short + '.walls', paving if d == '+z' and oid in doors else fin['walls'])
        return (short + '.' + {'+z': 'floor', '-z': 'ceiling'}.get(d, 'walls'), fin[{'+z': 'floor', '-z': 'ceiling'}.get(d, 'walls')])
    meshes, org = {}, (x0, y0, b['datumZ'])                 # brick courses count up from the veranda paving
    for i, j, k in zip(*np.nonzero(T == 0)):
        lo, hi = (X[i - 1], Y[j - 1], Z[k - 1]), (X[i], Y[j], Z[k])
        for d, (di, dj, dk) in (('-x', (-1, 0, 0)), ('+x', (1, 0, 0)), ('-y', (0, -1, 0)), ('+y', (0, 1, 0)),
                                ('-z', (0, 0, -1)), ('+z', (0, 0, 1))):
            f = finish(tags[T[i + di, j + dj, k + dk]], d) if T[i + di, j + dj, k + dk] else None
            if f:
                meshes.setdefault(f[0], _Mesh(weld=True)).box(lo, hi, f[1], only=(d,))

    def roof_z(y):
        return top - ROOF_FALL * (y1 - y) / (y1 - y0)
    for sfx, m in meshes.items():
        m.v = [(x, y, roof_z(y) if abs(z - top) < 1e-6 else z) for x, y, z in m.v]
        m.obj(ctx, f'{room}.{sfx}', room, dissolve=True, origin=org)
    if heads.f:
        heads.obj(ctx, f'{room}.heads', room)
    # roof trim: kerbs with coping on the west and back, a capped pier at each front corner
    m = _Mesh()
    # their outer faces stand PROUD (5 mm) of the wall faces they continue: coplanar they rendered black in Cycles
    pr = 0.005
    for kx0, ky0, kx1, ky1 in ((x0 - pr, y0 + 0.45, x0 + 0.10, y1 - 0.10), (x0 - pr, y1 - 0.10, x1 + pr, y1 + pr)):
        m.box((kx0, ky0, roof_z(ky0) - 0.05), (kx1, ky1, top + 0.12), brick, only=('-x', '+x', '-y', '+y'))
    for kx0, ky0, kx1, ky1 in ((x0, y0 + 0.45, x0 + 0.10, y1 - 0.10 - 0.03), (x0, y1 - 0.10, x1, y1)):   # copings butt, no overlap
        m.box((kx0 - 0.015, ky0 - 0.015, top + 0.12), (kx1 + 0.015, ky1 + 0.015, top + 0.15), '#8E9093')
    for px, pa, pb in ((x0, pr, 0.0), (x1 - 0.33, 0.0, pr)):
        m.box((px - pa, y0 - pr, roof_z(y0) - 0.05), (px + 0.33 + pb, y0 + 0.45, roof_z(y0) + 0.35), brick, only=('-x', '+x', '-y', '+y'))
        m.box((px - 0.02, y0 - 0.02, roof_z(y0) + 0.35), (px + 0.35, y0 + 0.47, roof_z(y0) + 0.39), LEAD)
    m.obj(ctx, f'{room}.roof.kerb', room, origin=org)
    # white uPVC: fascia over the roof edge, half-round gutter, downpipe at the west end, soffit vent strip
    m, zg = _Mesh(), roof_z(y0)
    m.box((x0, y0 - 0.02, soffit - 0.02), (x1, y0, zg + 0.01), 'upvc_white')
    m.tube(np.array((x0, y0 - 0.075, zg - 0.01)), np.array((x1, y0 - 0.075, zg - 0.01)), 0.055, 'upvc_white', arc=(math.pi, 2 * math.pi))
    foot = _low(ctx, [(x0 + 0.42, y0 - 0.06)], b['datumZ'])
    m.tube(np.array((x0 + 0.42, y0 - 0.055, foot)), np.array((x0 + 0.42, y0 - 0.055, zg - 0.06)), 0.034, 'upvc_white', up=(1.0, 0.0, 0.0))
    if veranda:
        vx0, _, vx1, _ = _bbox(veranda[0]['polygon'])
        m.box((vx0, y0 + 0.10, soffit - 0.004), (vx1, y0 + 0.17, soffit + 0.01), 'upvc_white')
    m.obj(ctx, f'{room}.fascia', room, kind='trim')


BOUNDARY = {'wall': _wall, 'pier': _pier, 'neighbour_wall': _neighbour_wall, 'gate': _gate}


def build(ctx):
    """Build the whole site from ctx.spec['exterior']; returns the objects."""
    ext = ctx.spec.get('exterior')
    if not ext:
        print('[site] this spec has no exterior')
        return []
    before = set(bpy.data.objects)
    _SURF.clear()
    house = _house_polys(ctx)
    _zones(ctx, house)
    _steps(ctx, house)
    gate_ends = [tuple(p) for b in ext['boundaries'] if b['type'] == 'gate' for p in b['line']]
    for b in ext['boundaries']:
        if b['type'] == 'fence':
            _fence(ctx, b, gate_ends)
        else:
            BOUNDARY[b['type']](ctx, b)
    for b in ext.get('buildings', []):
        _shed(ctx, b)
    _neighbours(ctx)
    objs = [o for o in bpy.data.objects if o not in before]
    tris = sum(len(p.vertices) - 2 for o in objs for p in o.data.polygons)
    print(f'[site] {len(objs)} objects, {tris} triangles')
    return objs

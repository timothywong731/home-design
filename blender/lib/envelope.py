"""Envelope (blender/MULTILEVEL.md section 7): the outside of the house. Outer skin with holes, reveals and sills,
roof slabs (upper envelope of roof.planes), roof steps, fascias, gutters, ridges, roof windows, chimney stack, the
street-front trim, pipes and the steel balcony. Reads exterior.envelope / facades, roof, features and
ctx.opening_frame only; needs no shell and no site. API: build(ctx), roof_surface(x, y). Notes: blender/lib/README.md.

Literal positions that are not in house.json (pilasters, cornice, pipes) come from spec/phase2/front_elevation.md
and rear_elevation.md and are kept in the tables below."""
import math

import bmesh
import bpy
from mathutils import Vector

from . import ctx as C
from . import interact as IX
from . import materials as M

EPS = 0.002
STEP = 0.01             # sampling step along a wall when looking for changes (features narrower than this are lost)
PLINTH_TOP = -0.08      # black plinth band on the rendered faces (rear_elevation.md 5: Z -0.30 .. -0.08)
BRICK_X = -0.50         # rear_R: exposed stock brick west of this x (MULTILEVEL 7)
PORCH_SOFFIT_Z = 2.62   # flat canopy soffit (front_elevation.md 3.4)
SILL = dict(t=0.07, out=0.06, side=0.06)
GUTTER = dict(w=0.114, h=0.07, t=0.008)
TRANSOM = 0.13          # masonry transom of the ground-floor bay lights (front_elevation.md 2.2: Z 1.80 .. 1.93)
EDGE_TRIM = (0.035, 0.03)   # flat-roof edge trim on a fascia board: height above it, projection (rear_elevation.md 3)
# sunk panels of the first-floor bay corner piers (front_elevation.md 3.5, +0.19 for the 3.42 floor):
# (x centre on front_A, width, z0, z1, depth)
PIER_PANELS = [(1.20, 0.27, 4.34, 5.59, 0.015), (3.855, 0.27, 4.34, 5.59, 0.015)]

# key -> (hex, roughness) used when materials.mat(key) does not know the key (the spec colours win over the hex)
FALLBACK = {
    'white_masonry_paint': ('#F2F2EE', 0.9), 'render_sandstone': ('#D2C596', 0.9), 'plinth_black': ('#2A2A2C', 0.8),
    'slate': ('#474A52', 0.7), 'fibre_cement_slate': ('#4B4E57', 0.75), 'flat_felt': ('#3A3C40', 0.9),
    'roof_underside': ('#6B5A45', 0.9), 'stock_brick_grey': ('#A99873', 0.9), 'red_brick': ('#A4553A', 0.9),
    'steel_chequer_plate': ('#2E3033', 0.45),
    'sill_stone': ('#EDEDE8', 0.8), 'pipe_black': ('#18181A', 0.35), 'pipe_old': ('#3A3B3E', 0.6),
    'steel_black': ('#33373A', 0.5), 'dormer_panel': ('#3F4146', 0.6), 'sill_board': ('#4A3F38', 0.7),
    'lead': ('#7C8087', 0.6), 'velux_grey': ('#5A5D62', 0.5), 'lamp_amber': ('#E8B45A', 0.3),
    'edge_trim': ('#1F2A24', 0.5),
}

# rear_elevation.md 5.3 / 6 and front_elevation.md 5: (material, diameter, square, [(x, y, z), ...]);
# z None = on the paving, 'porch' = on the lean-to roof
PIPES = [
    ('pipe_black', 0.068, False, [(4.38, 9.08, -0.25), (4.38, 9.08, 6.56)]),               # main-roof downpipe, face K
    ('pipe_black', 0.068, False, [(3.45, 9.08, 3.35), (3.45, 9.08, 8.58)]),                # flank gutter, F / K corner
    ('pipe_black', 0.110, False, [(4.25, 9.10, 3.30), (3.47, 9.10, 3.30), (3.47, 12.35, 3.10)]),   # first-floor waste
    ('pipe_black', 0.050, False, [(3.44, 13.40, 4.05), (3.44, 12.42, 3.45)]),              # second branch
    ('pipe_old', 0.110, False, [(3.47, 9.70, -0.20), (3.47, 12.30, -0.20)]),               # old drain along the foot
    ('pipe_black', 0.070, False, [(3.44, 17.40, 6.0), (0.15, 17.40, 6.0), (0.15, 17.40, 8.6)]),    # a/c trunking, R
    ('pipe_black', 0.070, False, [(3.44, 17.36, 6.2), (3.44, 11.0, 6.2)]),                 # the same along F
    ('upvc_white', 0.065, True, [(-0.68, -0.20, None), (-0.68, -0.20, 2.75)]),             # canopy downpipe (clear of the front wall, x <= -0.7225)
    ('upvc_white', 0.065, True, [(0.83, 0.08, 'porch'), (0.83, 0.08, 6.22), (0.56, 0.08, 6.40)]),   # main eaves, bay west cheek, offset bend to the gutter
]

_CTX = None


def roof_surface(x, y):
    """Outer roof surface Z at (x, y) (the same value as ctx.roof_z), or None."""
    return (_CTX or C.House.load()).roof_z(x, y)


# ---------------------------------------------------------------- helpers
def _mat(ctx, key):
    try:
        return M.mat(key)
    except (KeyError, FileNotFoundError):
        hx, rough = FALLBACK.get(key, ('#808080', 0.8))
        return M.solid('env_' + key, ctx.spec['exterior'].get('colours', {}).get(key, hx), rough)


def _normal(pts):
    n = Vector((0, 0, 0))
    for p, q in zip(pts, pts[1:] + pts[:1]):
        n += Vector(((p.y - q.y) * (p.z + q.z), (p.z - q.z) * (p.x + q.x), (p.x - q.x) * (p.y + q.y)))
    return n


class _Mesh:
    """Faces with material keys -> one object."""

    def __init__(self):
        self.v, self.f = [], []

    def face(self, pts, mat, n=None):
        """Polygon. n = the direction its normal must face (the winding is flipped when it does not)."""
        pts = [Vector(p) for p in pts]
        if n is not None and _normal(pts).dot(Vector(n)) < 0:
            pts.reverse()
        self.f.append((list(range(len(self.v), len(self.v) + len(pts))), mat))
        self.v += pts

    def prism(self, prof, a, b, mat, up=(0, 0, 1)):
        """Closed profile [(u, v)] swept a -> b: u = right of travel (d x up), v = up. Solid meshes only."""
        a, b, up = Vector(a), Vector(b), Vector(up)
        d = (b - a).normalized()
        if abs(d.dot(up)) > 0.999:
            up = Vector((1, 0, 0))
        s = d.cross(up).normalized()
        u = s.cross(d)
        ra, rb = ([o + s * x + u * y for x, y in prof] for o in (a, b))
        for i in range(len(prof)):
            j = (i + 1) % len(prof)
            self.face([ra[i], ra[j], rb[j], rb[i]], mat)
        self.face(ra, mat)
        self.face(rb, mat)

    def rings(self, rings, mat):
        """Closed profile rings (lists of points, same length) joined ring to ring, capped at both ends: a sweep with
        mitred corners. Solid meshes only."""
        n = len(rings[0])
        for ra, rb in zip(rings, rings[1:]):
            for i in range(n):
                j = (i + 1) % n
                self.face([ra[i], ra[j], rb[j], rb[i]], mat)
        self.face(rings[0], mat)
        self.face(rings[-1], mat)

    def box(self, lo, hi, mat, frame=None):
        """Axis box lo..hi; frame = (origin, ex, ey, ez) maps the box from local to world."""
        o, ex, ey, ez = frame or (Vector(), Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)))
        c = [Vector(o) + Vector(ex) * x + Vector(ey) * y + Vector(ez) * z
             for z in (lo[2], hi[2]) for y in (lo[1], hi[1]) for x in (lo[0], hi[0])]
        for q in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
            self.face([c[i] for i in q], mat)

    def pipe(self, path, d, mat, square=False, n=10):
        r = d / 2
        prof = [(-r, -r), (r, -r), (r, r), (-r, r)] if square else \
            [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n)) for i in range(n)]
        for a, b in zip(path, path[1:]):
            a, b = Vector(a), Vector(b)
            e = (b - a).normalized() * (0 if square else r * 0.5)       # run into the elbow
            self.prism(prof, a - e, b + e, mat)

    def obj(self, ctx, name, room, kind, solid=False, smooth=False, lm=None):
        """Create the object (None when empty). solid=True: closed pieces, normals recalculated outward."""
        if not self.f:
            return None
        keys = list(dict.fromkeys(k for _, k in self.f))
        bm = bmesh.new()
        vs = [bm.verts.new(p) for p in self.v]
        for idx, k in self.f:
            bm.faces.new([vs[i] for i in idx]).material_index = keys.index(k)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        if solid:
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        for k in keys:
            me.materials.append(_mat(ctx, k))
        if smooth:
            me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
            me.set_sharp_from_angle(angle=math.radians(40))
        ob = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(ob)
        M.uv_box(ob)
        return ctx.add(ob, room, kind, lm=lm)


def _vols(ctx):
    """Envelope prisms above ground: dict(id, level, poly (ccw), z0, z1, lowest)."""
    out = []
    for b in ctx.spec['exterior']['envelope']['blocks']:
        lv = [l for l in b['levels'] if not l.get('below_ground')]
        for i, l in enumerate(lv):
            poly = [tuple(p) for p in l['polygon']]
            if C.poly_area(poly) < 0:
                poly.reverse()
            out.append(dict(id=f"{b['id']}.{l['level']}", level=l['level'], poly=poly, z0=l['z'][0], z1=l['z'][1],
                            lowest=i == 0))
    return out


def _top(ctx, x, y, ground=False, tol=1e-6):
    """(z, plane) of the highest roof plane over (x, y) or None; ground=True: the porch lean-to only."""
    best = None
    for p in ctx.spec['roof']['planes']:
        if (p.get('level') == 'G') == ground and C.poly_contains(x, y, p['polygon'], tol):
            z = C.plane_z(p, x, y)
            if best is None or z > best[0]:
                best = (z, p)
    return best


def _floor_under(vols, x, y, z):
    """Floor Z of the highest envelope prism at (x, y) that reaches up to z (a roof underside), or None when the
    point hangs outside the walls (an overhang: the prisms below stop short of it)."""
    return max((v['z0'] for v in vols if v['z1'] >= z - 0.01 and C.point_in_poly(x, y, v['poly'])), default=None)


def _seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = min(1.0, max(0.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / ((dx * dx + dy * dy) or 1.0)))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def _on_edge(p, poly, tol=1e-4):
    return any(_seg_dist(p, a, b) < tol for a, b in zip(poly, poly[1:] + poly[:1]))


def _facade_line(f):
    e0, e1 = f['extent']
    return ((f['at'], e0), (f['at'], e1)) if f['axis'] == 'x' else ((e0, f['at']), (e1, f['at']))


def _facade_n(f):
    return {'+x': (1, 0), '-x': (-1, 0), '+y': (0, 1), '-y': (0, -1)}[f['faces']]


def _finish(ctx, p, n):
    """(facade id | None, finish) of a wall point with outward normal n: the facade it lies on, else the finish of
    the nearest facade, one facing the same way counting as 1 m nearer (the nib beside the bay is street-white)."""
    best = None
    for f in ctx.spec['exterior']['facades']:
        same = _facade_n(f) == (round(n[0]), round(n[1]))
        d = _seg_dist(p, *_facade_line(f))
        if d < 1e-3 and same:
            return f['id'], f['finish']
        if best is None or d - same < best[0]:
            best = (d - same, f['finish'])
    return None, best[1]


def _ext_openings(ctx):
    """Exterior openings of the house: dict(id, fr, p0 (xy on the outer face), z0, z1)."""
    out = []
    for oid in ctx.exterior_openings():
        if 'building' in ctx.openings[oid]:
            continue
        fr = ctx.opening_frame(oid)
        c, o = fr['center'], fr['outward']
        d = abs(fr['face_out'])
        out.append(dict(id=oid, fr=fr, p0=(c[0] + o[0] * d, c[1] + o[1] * d), z0=c[2], z1=fr['z0'] + fr['top']))
    return out


def _breaks(L, sig):
    """Positions along 0..L where sig(s) changes (sampled every STEP, refined by bisection, rounded to 0.1 mm)."""
    n = max(1, math.ceil(L / STEP))
    ss = [L * (i + 0.5) / n for i in range(n)]
    out, prev = [0.0], sig(ss[0])
    for a, b in zip(ss, ss[1:]):
        cur = sig(b)
        if cur != prev:
            lo, hi = a, b
            for _ in range(18):
                mid = (lo + hi) / 2
                lo, hi = (mid, hi) if sig(mid) == prev else (lo, mid)
            out.append(round(hi, 4))
            prev = cur
    return out + [L]


def _cut(polys, s0, s1, lo, hi=None):
    """2D (s, z) polygons minus the band between the lines lo and hi, each (z at s0, z at s1); hi=None: everything
    above lo goes."""
    out = []
    for P in polys:
        parts = [C.clip_poly(P, (s0, lo[0]), (s1, lo[1]), left=False)]
        if hi:
            parts.append(C.clip_poly(P, (s0, hi[0]), (s1, hi[1]), left=True))
        out += [Q for Q in parts if len(Q) >= 3 and abs(C.poly_area(Q)) > 1e-7]
    return out


# ---------------------------------------------------------------- skin
def _skin(ctx, vols, ops, meshes):
    """Outer faces of every envelope prism: clipped to the roof, minus what another prism or a neighbour covers,
    with holes at the openings. meshes: facade id | 'returns' -> _Mesh."""
    ext = ctx.spec['exterior']
    nbs = ext.get('neighbours', [])

    def zone_base(x, y):
        zid = ctx.zone_at(x, y)
        if zid is None:
            return None
        z = ctx.zone(zid)
        return min([z['z']] + list((z.get('fall') or {}).get('z', []))) - 0.05

    for vol in vols:
        poly = vol['poly']
        for a, b in zip(poly, poly[1:] + poly[:1]):
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
            nx, ny = uy, -ux                                    # outward (the polygon is ccw)
            mine = [o for o in ops if _seg_dist(o['p0'], a, b) < 0.02
                    and o['fr']['outward'][0] * nx + o['fr']['outward'][1] * ny > 0.9]
            above = [w for w in vols if w is not vol and abs(w['z0'] - vol['z1']) < 1e-6]

            def state(s):
                x, y = a[0] + ux * s, a[1] + uy * s
                ox, oy = x + nx * EPS, y + ny * EPS
                top = _top(ctx, x, y)
                # a ground-floor wall stops under the porch roof unless the storey above continues it
                cont = any(_on_edge((x, y), w['poly']) and C.point_in_poly(x - nx * EPS, y - ny * EPS, w['poly'])
                           for w in above)
                gtop = _top(ctx, x, y, True, 0.03) if vol['level'] == 'G' and not cont else None
                inside = tuple(i for i, w in enumerate(vols) if w is not vol and C.point_in_poly(ox, oy, w['poly']))
                nb = next(((i, ctx.neighbour_top(q, ox, oy)[1]) for i, q in enumerate(nbs)
                           if C.point_in_poly(ox, oy, q['polygon'])), None)
                fid, fin = _finish(ctx, (x, y), (nx, ny))
                if fid == 'rear_R' and x < BRICK_X:
                    fin = 'stock_brick_grey'
                op = tuple(i for i, o in enumerate(mine)
                           if abs((x - o['p0'][0]) * ux + (y - o['p0'][1]) * uy) < o['fr']['width'] / 2)
                base = zone_base(x + nx * 0.05, y + ny * 0.05) if vol['lowest'] else None
                return (top and top[1]['id'], gtop and gtop[1]['id'], inside, nb, fid, fin, op, base)

            bk = _breaks(L, state)
            for s0, s1 in zip(bk, bk[1:]):
                if s1 - s0 < 1e-4:
                    continue
                tid, gid, inside, nb, fid, fin, op, base = state((s0 + s1) / 2)
                pt = lambda s, d=0.0: (a[0] + ux * s + nx * d, a[1] + uy * s + ny * d)
                zb = vol['z0'] if not vol['lowest'] else (vol['z0'] - 0.05 if base is None else base)
                zt = 99.0 if gid else vol['z1']                 # under the porch: up to its roof, whatever z1 says
                polys = [[(s0, zb), (s1, zb), (s1, zt), (s0, zt)]]
                for pid in (tid, gid):                          # under the roof surface
                    if pid:
                        pl = next(p for p in ctx.spec['roof']['planes'] if p['id'] == pid)
                        polys = _cut(polys, s0, s1, (C.plane_z(pl, *pt(s0)), C.plane_z(pl, *pt(s1))))
                for i in inside:                                # hidden inside another prism (up to its own roof)
                    w = vols[i]
                    hi = [w['z1'], w['z1']]
                    wt = _top(ctx, *pt((s0 + s1) / 2, EPS))
                    if wt:
                        hi = [min(w['z1'], C.plane_z(wt[1], *pt(s, EPS))) for s in (s0, s1)]
                    polys = _cut(polys, s0, s1, [-99.0 if w['lowest'] else w['z0']] * 2, hi)
                if nb is not None:                              # party wall below the neighbour's roof
                    d = min(1e-4, (s1 - s0) / 4)
                    polys = _cut(polys, s0, s1, (-99.0, -99.0), [ctx.neighbour_top(nbs[nb[0]], *pt(s, EPS))[0] for s in (s0 + d, s1 - d)])
                for i in op:
                    polys = _cut(polys, s0, s1, [mine[i]['z0']] * 2, [mine[i]['z1']] * 2)
                m = meshes.setdefault(fid or 'returns', _Mesh())
                for P in polys:
                    parts = [(P, fin)]
                    if fin == 'render_sandstone' and vol['lowest']:
                        parts = [(C.clip_poly(P, (s0, PLINTH_TOP), (s1, PLINTH_TOP), left=False), 'plinth_black'),
                                 (C.clip_poly(P, (s0, PLINTH_TOP), (s1, PLINTH_TOP), left=True), fin)]
                    for Q, k in parts:
                        if len(Q) >= 3 and abs(C.poly_area(Q)) > 1e-7:
                            m.face([pt(s) + (z,) for s, z in Q], k, (nx, ny, 0))


def _reveals(ctx, ops, meshes, banded):
    """Returns of every hole (2 mm inside it, ext_reveal deep, facade finish) and the projecting window sills.
    banded: opening ids whose sill is a string course (no sill box of their own). Windows with `transom` / `mullion`
    (the ground-floor bay) get those in masonry from the wall face back to the frame; joinery glazes behind them."""
    for o in ops:
        fr = o['fr']
        al, out = Vector((fr['along'][0], fr['along'][1], 0)), Vector((fr['outward'][0], fr['outward'][1], 0))
        fid, fin = _finish(ctx, o['p0'], (out.x, out.y))
        if fid == 'rear_R' and o['p0'][0] < BRICK_X:
            fin = 'stock_brick_grey'
        m = meshes.setdefault(fid or 'returns', _Mesh())
        o3 = Vector((o['p0'][0], o['p0'][1], 0))
        w, d, z0, z1 = fr['width'] / 2 - EPS, fr['ext_reveal'], o['z0'] + EPS, o['z1'] - EPS
        P = lambda s, z, dep: o3 + al * s - out * dep + Vector((0, 0, z))
        for sg in (-1, 1):
            m.face([P(sg * w, z0, 0), P(sg * w, z0, d), P(sg * w, z1, d), P(sg * w, z1, 0)], fin, -sg * al)
        m.face([P(-w, z1, 0), P(w, z1, 0), P(w, z1, d), P(-w, z1, d)], fin, (0, 0, -1))
        m.face([P(-w, z0, 0), P(w, z0, 0), P(w, z0, d), P(-w, z0, d)], 'sill_stone', (0, 0, 1))
        if fr['type'] not in C.WINDOWS:
            continue
        sm = meshes.setdefault((fid or 'returns') + '.sills', _Mesh())
        F, wf = (o3, al, out, Vector((0, 0, 1))), fr['width'] / 2
        if o['id'] not in banded:
            sm.box((-wf - SILL['side'], 0, z0 - SILL['t']), (wf + SILL['side'], SILL['out'], z0), 'sill_stone', F)
        lights = [(-wf, wf)]                                 # masonry mullions and transom, flush with the wall face;
        if fr.get('mullion'):                                # the transom runs light by light: no box overlaps another
            n, lw, mu = fr['lights'], fr['lightWidth'], fr['mullion']
            x0 = -(n * lw + (n - 1) * mu) / 2
            edges = [-wf] + [x0 + i * (lw + mu) + k for i in range(n) for k in (0, lw)] + [wf]
            lights = list(zip(edges[1::2], edges[2::2]))
            for a, b in zip(edges[0::2], edges[1::2]):
                if b - a > 1e-3:
                    sm.box((a, -d, z0), (b, 0, z1), fin, F)
        if fr.get('transom'):
            zt = fr['z0'] + fr['transom']['height']
            for a, b in lights:
                sm.box((a, -d, zt), (b, 0, zt + TRANSOM), fin, F)


# ---------------------------------------------------------------- roof
def _line(nx, ny, c):
    k = math.hypot(nx, ny)
    if k < 1e-9:
        return None
    nx, ny, c = nx / k, ny / k, c / k
    if nx < -1e-9 or (abs(nx) <= 1e-9 and ny < 0):
        nx, ny, c = -nx, -ny, -c
    return (round(nx, 6), round(ny, 6), round(c, 6))


def _edge_lines(poly):
    return [_line(q[1] - p[1], p[0] - q[0], (q[1] - p[1]) * p[0] + (p[0] - q[0]) * p[1])
            for p, q in zip(poly, poly[1:] + poly[:1])]


def _roof(ctx, vols, steps):
    """Roof slabs: the upper envelope of the planes (cut along valleys and at every higher plane), fascias on free
    edges, soffits, undersides in the roof voids, gutters on pitched eaves. steps: _Mesh for the roof-step skin."""
    roof = ctx.spec['roof']
    wins = [f for f in ctx.features if f['type'] in ('roof_window', 'roof_opening')]
    floors = sorted({v['z0'] for v in vols if v['level'] == ctx.levels[-1]})
    objs, gutters, runs = [], {}, []

    def eave(x, y):                                         # nearest roof.eaves entry within 0.3 m
        best = None
        for e in roof.get('eaves', []):
            d = _seg_dist((x, y), *e['line'])
            if d < 0.3 and (best is None or d < best[0]):
                best = (d, e)
        return best and best[1]

    for ground in (False, True):
        planes = [p for p in roof['planes'] if (p.get('level') == 'G') == ground]
        lines = set()
        for p in planes:
            lines.update(_edge_lines(p['polygon']))
            pz = p['z']
            for q in planes:
                lines.add(_line(pz['cx'] - q['z']['cx'], pz['cy'] - q['z']['cy'], q['z']['c0'] - pz['c0']))
            for zf in floors:                               # where the underside meets the top floor
                lines.add(_line(pz['cx'], pz['cy'], zf + ctx.roof_slab_t(p['id']) - pz['c0']))
        for v in vols:
            lines.update(_edge_lines(v['poly']))
        for f in wins:
            lines.update(_edge_lines([tuple(q) for q in f['polygon']]))
        bm = bmesh.new()
        lay = bm.faces.layers.int.new('plane')
        for i, p in enumerate(planes):
            poly = [tuple(q) for q in p['polygon']]
            if C.poly_area(poly) < 0:
                poly.reverse()
            bm.faces.new([bm.verts.new((x, y, C.plane_z(p, x, y))) for x, y in poly])[lay] = i
        for ln in lines - {None}:
            bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6,
                                   plane_co=(ln[0] * ln[2], ln[1] * ln[2], 0), plane_no=(ln[0], ln[1], 0))
        dead = []
        for f in bm.faces:
            c = f.calc_center_median()
            top = _top(ctx, c.x, c.y, ground)
            if top is None or top[1] is not planes[f[lay]] or any(
                    C.point_in_poly(c.x, c.y, w['polygon']) and w['roofPlane'] == top[1]['id'] for w in wins):
                dead.append(f)
        bmesh.ops.delete(bm, geom=dead, context='FACES')

        for i, p in enumerate(planes):
            m, t = _Mesh(), ctx.roof_slab_t(p['id'])
            pitched = bool(p['z']['cx'] or p['z']['cy'])
            down = Vector((0, 0, -t))
            for f in (f for f in bm.faces if f[lay] == i):
                pts = [v.co.copy() for v in f.verts]
                m.face(pts, p['covering'], (0, 0, 1))
                c = f.calc_center_median()
                zf = _floor_under(vols, c.x, c.y, c.z - t)
                if ground:
                    if zf is None:                          # the canopy's flat soffit
                        m.face([(q.x, q.y, PORCH_SOFFIT_Z) for q in pts], 'upvc_white', (0, 0, -1))
                elif zf is None:                            # overhang: soffit
                    m.face([q + down for q in pts], 'upvc_white', (0, 0, -1))
                elif c.z - t >= zf - 1e-4:                  # inside the roof void, above the top floor
                    m.face([q + down for q in pts], 'roof_underside', (0, 0, -1))
                for l in f.loops:
                    if len(l.edge.link_faces) != 1:
                        continue
                    a, b = l.vert.co, l.link_loop_next.vert.co
                    e = (b - a).to_2d()
                    if e.length < 1e-5:
                        continue
                    n = Vector((e.y, -e.x)).normalized()    # outward in plan (the face is ccw seen from above)
                    mid = (a + b) / 2
                    oth = _top(ctx, mid.x + n.x * EPS, mid.y + n.y * EPS, ground)
                    wall = any(_on_edge((mid.x, mid.y), v['poly']) and v['z0'] < mid.z and v['z1'] >= mid.z - t - 0.01
                               for v in vols)
                    if oth:                                 # another plane beyond: a step when it is lower
                        za, zb = C.plane_z(oth[1], a.x, a.y), C.plane_z(oth[1], b.x, b.y)
                        if oth[1] is p or wall or (za >= a.z - 0.005 and zb >= b.z - 0.005):
                            continue
                        fin = 'dormer_panel' if p['id'] == 'stair_dormer' else _finish(ctx, (mid.x, mid.y), n)[1]
                        steps.face([a, b, (b.x, b.y, min(zb, b.z)), (a.x, a.y, min(za, a.z))], fin, (n.x, n.y, 0))
                    elif not wall:                          # free edge: fascia / bargeboard
                        ev = eave(mid.x, mid.y)
                        black = bool(ev) and ev.get('colour') == 'black'
                        m.face([a, b, b + down, a + down], 'pipe_black' if black else 'upvc_white', (n.x, n.y, 0))
                        slope = Vector((p['z']['cx'], p['z']['cy']))
                        if pitched and abs(a.z - b.z) < 1e-4 and slope.dot(n) < 0 and e.length > 0.05:   # no stubs
                            off = Vector((n.x, n.y, 0)) * (GUTTER['w'] / 2 + 0.004) - Vector((0, 0, 0.03))
                            runs.append([(ev['id'] if ev else p['id'], black), a + off, b + off])
            ob = m.obj(ctx, f"roof.{p['id']}", 'roof', 'shell')
            if ob:
                if abs(p['z']['cx']) > abs(p['z']['cy']):   # slate courses run along the eaves
                    M.uv_box(ob, rotate=True)
                objs.append(ob)
        bm.free()

    for r in runs:                                          # two eaves meeting in a valley: one gutter round the corner.
        for k in (1, 2):                                    # Each end that passes another run's line stops half a width
            for q in runs:                                  # beyond it, so the two troughs close on each other
                d, e = (r[3 - k] - r[k]).to_2d(), (q[2] - q[1]).to_2d()
                if q is r or abs(d.normalized().dot(e.normalized())) > 0.1 or abs(r[k].z - q[1].z) > 0.05:
                    continue
                t = (q[1].to_2d() - r[k].to_2d()).dot(d) / d.length_squared      # where r crosses q's line
                u = (r[k].to_2d() + d * t - q[1].to_2d()).dot(e) / e.length_squared
                if 0 < t * d.length < 0.3 and -0.3 / e.length < u < 1 + 0.3 / e.length:
                    r[k] = r[k] + (r[3 - k] - r[k]).normalized() * (t * d.length - GUTTER['w'] / 2)
    for key, a, b in runs:
        _gutter(gutters.setdefault(key, _Mesh()), a, b, key[1])
    for e in roof.get('eaves', []):                         # eaves the roof edges did not give (flat-roof gutters)
        a, b = (Vector(q) for q in e['line'])
        black = e.get('colour') == 'black'
        if 'gutterZ' in e and not any(k[0] == e['id'] for k in gutters):
            g = gutters.setdefault((e['id'], black), _Mesh())
            _gutter(g, Vector((a.x, a.y, e['gutterZ'])), Vector((b.x, b.y, e['gutterZ'])), black)
        elif 'z' in e:                                      # a fascia board on the line, against the roof edge
            m, hb = _Mesh(), e['z'][1] - e['z'][0]
            d = (b - a).normalized()
            r = Vector((d.y, -d.x))                          # right of travel = the prism's +u
            sg = 1 if ctx.roof_z(*((a + b) / 2 + r * 0.2)) is None else -1      # +u or -u is the outside
            col = 'pipe_black' if black else 'upvc_white'
            u0, u1 = sorted((0.0, sg * 0.022))
            m.prism([(u0, 0), (u1, 0), (u1, hb), (u0, hb)], (a.x, a.y, e['z'][0]), (b.x, b.y, e['z'][0]), col)
            h, pj = EDGE_TRIM                                # dark flat-roof edge trim capping the board
            u0, u1 = sorted((-sg * 0.02, sg * pj))
            m.prism([(u0, 0), (u1, 0), (u1, h), (u0, h)], (a.x, a.y, e['z'][1]), (b.x, b.y, e['z'][1]), 'edge_trim')
            objs.append(m.obj(ctx, f"roof.{e['id']}", 'roof', 'trim', solid=True))
    for (gid, _), g in gutters.items():
        objs.append(g.obj(ctx, f'roof.{gid}.gutter', 'roof', 'fit', solid=True))

    m = _Mesh()                                             # ridge cappings
    cap = [(-0.13, -0.06), (0.13, -0.06), (0.0, 0.03)]
    ridges = [(roof['ridge']['line'], roof['ridge']['z'])]
    if roof.get('gable'):
        ridges.append((roof['gable']['ridge'], roof['gable']['ridgeZ']))
    for (a, b), z in ridges:
        m.prism(cap, (a[0], a[1], z), (b[0], b[1], z), 'lead')
    objs.append(m.obj(ctx, 'roof.ridge', 'roof', 'trim', solid=True))
    return objs


def _gutter(m, a, b, black):
    """Open gutter with its top edge on the line a -> b."""
    w, h, t = GUTTER['w'] / 2, GUTTER['h'], GUTTER['t']
    prof = [(-w, -h), (w, -h), (w, 0), (w - t, 0), (w - t, t - h), (t - w, t - h), (t - w, 0), (-w, 0)]
    m.prism(prof, a, b, 'pipe_black' if black else 'upvc_white')


def _roof_windows(ctx):
    """Frame and glass in every roof_window / roof_opening hole: an upstand kerb with fixed glass on a flat roof,
    a frame with a top-hung sash (its own object, IX hinge) on a slope."""
    objs = []
    for f in ctx.features:
        if f['type'] not in ('roof_window', 'roof_opening'):
            continue
        p = next(q for q in ctx.spec['roof']['planes'] if q['id'] == f['roofPlane'])
        assert not p['z']['cx'], f"{f['id']}: roof windows are built on planes sloping along Y only"
        xs, ys = [q[0] for q in f['polygon']], [q[1] for q in f['polygon']]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        cy = p['z']['cy']
        ey = Vector((0, 1, cy)).normalized()
        ex, en = Vector((1, 0, 0)), Vector((1, 0, 0)).cross(ey)
        W, H = x1 - x0, (y1 - y0) * math.hypot(1, cy)
        fr = (Vector((x0, y0, C.plane_z(p, x0, y0))), ex, ey, en)
        m, name = _Mesh(), f"roof.{f['id']}"
        if f['type'] == 'roof_opening' or not f.get('operable'):
            k, h = 0.06, 0.15                               # kerb round the hole, fixed glass on top
            for lo, hi in (((-k, -k, -0.02), (W + k, 0, h)), ((-k, H, -0.02), (W + k, H + k, h)),
                           ((-k, 0, -0.02), (0, H, h)), ((W, 0, -0.02), (W + k, H, h))):
                m.box(lo, hi, 'velux_grey', fr)
            objs.append(m.obj(ctx, name + '.kerb', 'roof', 'fit', solid=True))
            g = _Mesh()
            g.box((-k - 0.01, -k - 0.01, h), (W + k + 0.01, H + k + 0.01, h + 0.012), 'glass_clear', fr)
            objs.append(g.obj(ctx, name + '.glass', 'roof', 'fit', solid=True))
            continue
        k = 0.04                                            # fixed frame inside the hole, 25 mm above the slates
        for lo, hi in (((0, 0, -0.10), (W, k, 0.025)), ((0, H - k, -0.10), (W, H, 0.025)),
                       ((0, k, -0.10), (k, H - k, 0.025)), ((W - k, k, -0.10), (W, H - k, 0.025))):
            m.box(lo, hi, 'velux_grey', fr)
        objs.append(m.obj(ctx, name + '.frame', 'roof', 'fit', solid=True))
        s, b = _Mesh(), 0.05                                # sash: four rails and the pane
        for lo, hi in (((k, k, 0.0), (W - k, k + b, 0.045)), ((k, H - k - b, 0.0), (W - k, H - k, 0.045)),
                       ((k, k + b, 0.0), (k + b, H - k - b, 0.045)), ((W - k - b, k + b, 0.0), (W - k, H - k - b, 0.045))):
            s.box(lo, hi, 'velux_grey', fr)
        s.box((k + b, k + b, 0.018), (W - k - b, H - k - b, 0.030), 'glass_clear', fr)
        sash = s.obj(ctx, name + '.sash', 'roof', 'joinery', solid=True, lm='dynamic')
        top_low = cy < 0                                    # the hinge is on the high edge
        hinge = fr[0] + ex * (W / 2) + ey * (k if top_low else H - k) + en * 0.025
        IX.tag(sash, 'hinge', p=hinge, a=(1, 0, 0), deg=f.get('angle', 30) * (1 if top_low else -1),
               label='Roof window', reach=2.2)
        objs.append(sash)
    return objs


def _chimney(ctx):
    """Stacks of roof.chimneys above the roof only (below it the pier is the brick strip of the skin)."""
    objs = []
    for cid in ctx.spec['roof'].get('chimneys', []):
        f = next(q for q in ctx.spec['exterior']['features'] if q['id'] == cid)
        xs, ys = [q[0] for q in f['polygon']], [q[1] for q in f['polygon']]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        zr = max(z for z in (ctx.roof_z(x, y) for x in (x0, x1) for y in (y0, y1)) if z is not None)
        m = _Mesh()
        m.box((x0, y0, zr - 0.02), (x1, y1, f['z'][1] - 0.06), 'stock_brick_grey')
        m.box((x0 - 0.03, y0 - 0.03, f['z'][1] - 0.06), (x1 + 0.03, y1 + 0.03, f['z'][1]), 'sill_stone')
        objs.append(m.obj(ctx, f'roof.{cid}', 'roof', 'shell', solid=True))
    return objs


# ---------------------------------------------------------------- street front trim (front_elevation.md 3)
def _front_trim(ctx):
    fac = {f['id']: f for f in ctx.spec['exterior']['facades']}
    if not {'front_A', 'bay_cheek_w', 'bay_cheek_e'} <= fac.keys():
        return [], set()
    y0, xw, xe = fac['front_A']['at'], fac['bay_cheek_w']['at'], fac['bay_cheek_e']['at']
    yb = fac['bay_cheek_e']['extent'][1]
    base = ctx.zone_z('forecourt') - 0.11 if 'forecourt' in ctx.zones else -0.1
    m, W = _Mesh(), 'white_masonry_paint'
    for x0, x1, reeds in ((0.68, 1.07, 3), (3.955, xe, 0)):         # pilasters: base block, shaft, capital
        m.box((x0, y0 - 0.06, base), (x1, y0, 2.90), W)
        m.box((x0 - 0.015, y0 - 0.08, base), (x1 + 0.015, y0, 0.62), W)
        m.box((x0 - 0.04, y0 - 0.10, 2.52), (x1 + 0.04, y0, 2.65), W)
        reed = [(0.0275 * math.cos(math.pi * i / 6), 0.015 * math.sin(math.pi * i / 6)) for i in range(7)]
        for i in range(reeds):
            cx = (x0 + x1) / 2 + (i - 1) * 0.09
            m.prism(reed, (cx, y0 - 0.06, 0.72), (cx, y0 - 0.06, 2.42), W, up=(0, -1, 0))
    m.box((1.07, y0 - 0.02, base), (3.955, y0, 0.30), W)            # plinth, 20 mm proud
    m.box((xe, y0, base), (xe + 0.02, yb, 0.30), W)
    corn = [(0, 0), (0.03, 0), (0.03, 0.03), (0.08, 0.08), (0.10, 0.08), (0.10, 0.12), (0.16, 0.18), (0.18, 0.18),
            (0.18, 0.20), (0, 0.20)]                                # bay cornice Z 2.90 .. 3.10, returned on the cheek
    m.rings([[(x + u * kx, y - u * ky if ky else y, 2.90 + v) for u, v in corn]         # one sweep, mitred at the corner
             for x, y, kx, ky in ((0.93, y0, 0, 1), (xe, y0, 1, 1), (xe, yb, 1, 0))], W)
    banded = {o for fid in ('front_A', 'bay_cheek_w', 'bay_cheek_e') for o in fac[fid]['openings']
              if ctx.openings[o].get('level') == '1'}
    front = next((ctx.opening_frame(o) for o in fac['front_A']['openings'] if o in banded), None)
    if front:
        zs, zh = front['center'][2], front['z0'] + front['head']
        led = [(0, -0.07), (0.12, -0.07), (0.12, 0), (0, 0)]        # first-floor sill ledge round the bay
        m.rings([[(x + u * kx, y - u * ky if ky else y, zs + v) for u, v in led]       # round both corners, mitred
                 for x, y, kx, ky in ((xw, fac['bay_cheek_w']['extent'][1], -1, 0), (xw, y0, -1, 1), (xe, y0, 1, 1), (xe, yb, 1, 0))], W)
        g = ctx.spec['roof'].get('gable')
        gp = [p for p in ctx.spec['roof']['planes'] if p['id'].startswith(g['id'])] if g else []
        if len(gp) == 2:                                            # gable field: head rail and raking struts
            t, xr, zt = ctx.roof_slab_t(gp[0]['id']), g['ridge'][0][0], zh + 0.09
            m.box((xw, y0 - 0.03, zh), (xe, y0, zt), W)
            # ponytail: struts are straight boards cut by the verge line; the two curved braces are left out
            for sg, pl in ((-1, max(gp, key=lambda p: p['z']['cx'])), (1, min(gp, key=lambda p: p['z']['cx']))):
                z1, z2 = (C.plane_z(pl, q, y0) - t - 0.02 for q in (0, 1))
                for i in range(3):
                    # foot on the rail, 0.35 apart; 60 degrees to the horizontal, leaning away from the centre until
                    # the bargeboard stops it (crop_gable_t955 / t956: the tops lie on the verge, the feet fan out from
                    # the middle of the window head)
                    xa = xr + sg * (0.25 + 0.35 * i)
                    dx, dz = sg * 3 * math.cos(math.radians(60)), 3 * math.sin(math.radians(60))
                    P = [(xa - 0.052, zt), (xa + 0.052, zt), (xa + 0.052 + dx, zt + dz), (xa - 0.052 + dx, zt + dz)]
                    P = C.clip_poly(P, (0, z1), (1, z2), left=False)        # under the verge
                    P = C.clip_poly(P, (xr, 0), (xr, 1), left=sg < 0)       # on its own half
                    if len(P) >= 3:
                        m.prism([(-x, z) for x, z in P], (0, y0, 0), (0, y0 - 0.025, 0), W)
    eav = next((e for e in ctx.spec['roof'].get('eaves', []) if e['id'] == 'front'), None)
    kn = _Mesh()
    if eav:                                                         # party-wall kneeler, west (3.8)
        xk, yk = fac['front_B']['extent'][0], fac['front_B']['at']
        zk = ctx.roof_under(xk + 0.1, yk - 0.29) - 0.50                # its cap sits under the eaves soffit
        for i in range(6):
            kn.box((xk, yk - 0.05 * (i + 1), zk + 0.075 * i), (xk + 0.22, yk, zk + 0.075 * (i + 1)), 'red_brick')
        kn.box((xk, yk - 0.32, zk + 0.45), (xk + 0.22, yk, zk + 0.49), 'lead')
    return [m.obj(ctx, 'facade.front_A.trim', 'facade', 'trim', solid=True),
            kn.obj(ctx, 'facade.front_B.kneeler', 'facade', 'trim', solid=True)], banded


def _pier_panels(ctx, meshes):
    """Sunk panels PIER_PANELS in the street face: the recessed back and four returns go into the facade's mesh;
    returns the pseudo-openings that make _skin leave the holes."""
    f = next((q for q in ctx.spec['exterior']['facades'] if q['id'] == 'front_A'), None)
    if f is None:
        return []
    y0, m, holes = f['at'], meshes.setdefault('front_A', _Mesh()), []
    for xc, w, z0, z1, dep in PIER_PANELS:
        xa, xb, yb = xc - w / 2, xc + w / 2, y0 + dep
        m.face([(xa, yb, z0), (xb, yb, z0), (xb, yb, z1), (xa, yb, z1)], f['finish'], (0, -1, 0))
        for pts, n in (([(xa, y0, z0), (xa, yb, z0), (xa, yb, z1), (xa, y0, z1)], (1, 0, 0)),
                       ([(xb, y0, z0), (xb, yb, z0), (xb, yb, z1), (xb, y0, z1)], (-1, 0, 0)),
                       ([(xa, y0, z0), (xb, y0, z0), (xb, yb, z0), (xa, yb, z0)], (0, 0, 1)),
                       ([(xa, y0, z1), (xb, y0, z1), (xb, yb, z1), (xa, yb, z1)], (0, 0, -1))):
            m.face(pts, f['finish'], n)
        holes.append(dict(id='panel', fr=dict(outward=(0.0, -1.0), width=w), p0=(xc, y0), z0=z0, z1=z1))
    return holes


def _pipes(ctx):
    """Soil stack (exterior.features type pipe) and the PIPES table. A pipe that stands on the ground is its own
    object with plan_sym 'pipe': its footprint keeps the walker's body out of it."""
    objs = []
    for f in ctx.spec['exterior'].get('features', []):
        if f['type'] != 'pipe':
            continue
        fc = min(ctx.spec['exterior']['facades'], key=lambda q: _seg_dist(f['at'], *_facade_line(q)))
        n, r = _facade_n(fc), f['diameter'] / 2
        x, y = f['at'][0] + n[0] * (r + 0.03), f['at'][1] + n[1] * (r + 0.03)
        m = _Mesh()
        m.pipe([(x, y, f['z'][0]), (x, y, f['z'][1])], f['diameter'], 'pipe_black', n=12)
        z = f['z'][0] + 1.0
        while z < f['z'][1] - 0.3:                                  # ring-seal sockets about every 2 m
            m.pipe([(x, y, z), (x, y, z + 0.12)], f['diameter'] + 0.024, 'pipe_black', n=12)
            z += 2.0
        ob = m.obj(ctx, f"facade.{f['id']}", 'facade', 'fit', solid=True, smooth=True)
        if ctx.ground_z(x, y) is not None and f['z'][0] < ctx.ground_z(x, y) + 0.5:
            ob['plan_sym'] = 'pipe'
        objs.append(ob)
    by, n = {}, 0
    for mat, d, sq, path in PIPES:
        pts = []
        for x, y, z in path:
            if z == 'porch':
                z = _top(ctx, x, y, True)[0]
            elif z is None:
                z = ctx.ground_z(x, y) if ctx.ground_z(x, y) is not None else 0.0
            pts.append((x, y, z))
        (x, y, z), g = pts[0], ctx.ground_z(*pts[0][:2])
        if g is not None and z < g + 0.5 and pts[1][:2] == (x, y) and pts[1][2] - z > 1.0:      # a downpipe to the ground
            m, n = _Mesh(), n + 1
            m.pipe(pts, d, mat, square=sq)
            ob = m.obj(ctx, f'facade.downpipe.{n}', 'facade', 'fit', solid=True, smooth=True)
            ob['plan_sym'] = 'pipe'
            objs.append(ob)
            continue
        by.setdefault(mat, _Mesh()).pipe(pts, d, mat, square=sq)
    for mat, m in by.items():
        objs.append(m.obj(ctx, f'facade.pipes.{mat}', 'facade', 'fit', solid=True, smooth=True))
    return objs


# ---------------------------------------------------------------- balcony
def _balcony(ctx):
    objs = []
    for f in ctx.features:
        if f['type'] != 'balcony':
            continue
        room = f['room']
        xs, ys = [q[0] for q in f['polygon']], [q[1] for q in f['polygon']]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        zt, th, S = f['deckTopZ'], f['deckThickness'], 'steel_black'
        d = _Mesh()                                                 # chequer plate = the room's floor
        d.box((x0, y0, zt - 0.006), (x1, y1, zt), 'steel_chequer_plate')
        objs.append(d.obj(ctx, f'{room}.floor', room, 'shell', solid=True))
        m = _Mesh()
        for lo, hi in (((x0, y0, zt - th), (x1, y0 + 0.06, zt - 0.006)), ((x0, y1 - 0.06, zt - th), (x1, y1, zt - 0.006)),
                       ((x0, y0 + 0.06, zt - th), (x0 + 0.06, y1 - 0.06, zt - 0.006)),
                       ((x1 - 0.06, y0 + 0.06, zt - th), (x1, y1 - 0.06, zt - 0.006)),
                       ((x0 + 0.06, y0 + 0.06, zt - th + 0.01), (x1 - 0.06, y1 - 0.06, zt - th + 0.016))):   # frame, soffit
            m.box(lo, hi, S)
        r = f['railing']
        H, ps, bar = r['height'], r['post'], r['bar']
        cl = lambda x, y: (min(max(x, x0 + ps / 2), x1 - ps / 2), min(max(y, y0 + ps / 2), y1 - ps / 2))
        posts = [cl(*q) for q in r['posts']]
        for x, y in posts:
            m.box((x - ps / 2, y - ps / 2, zt), (x + ps / 2, y + ps / 2, zt + H - 0.04), S)
        yr, xa, xb = y1 - ps / 2, x0 + ps / 2, x1 - ps / 2
        runs = {'north': [(posts[i], posts[i + 1], r['barsPerFrontBay']) for i in range(len(posts) - 1)],
                'west': [((xa, y0), (xa, yr), r['barsPerSide'])], 'east': [((xb, y0), (xb, yr), r['barsPerSide'])]}
        for side in r['sides']:
            for a, b, n in runs[side]:
                a, b = Vector((a[0], a[1], zt)), Vector((b[0], b[1], zt))
                m.prism([(-0.03, H - 0.04), (0.03, H - 0.04), (0.03, H), (-0.03, H)], a, b, S)          # top rail
                m.prism([(-0.005, 0.10), (0.005, 0.10), (0.005, 0.14), (-0.005, 0.14)], a, b, S)        # bottom rail
                for i in range(n):
                    q = a + (b - a) * ((i + 1) / (n + 1))
                    m.box((q.x - bar / 2, q.y - bar / 2, zt + 0.14), (q.x + bar / 2, q.y + bar / 2, zt + H - 0.04), S)
            if side != 'north':                                     # wall brackets of the side rails
                x = xa if side == 'west' else xb
                for z in (zt + 0.12, zt + H - 0.02):
                    m.box((x - 0.04, y0, z - 0.04), (x + 0.04, y0 + 0.006, z + 0.04), S)
        sup = f['supports']
        st = sup['struts']
        for px, py in sup['wallPosts']:                             # wall channels and 45-degree struts
            m.box((px - 0.05, py, sup['postZ'][0]), (px + 0.05, py + 0.04, sup['postZ'][1]), S)
            m.prism([(-0.03, -0.03), (0.03, -0.03), (0.03, 0.03), (-0.03, 0.03)],
                    (px, py + 0.03, st['fromZ']), (px, py + st['reach'], st['toZ'] - 0.03), S)
        objs.append(m.obj(ctx, f'{room}.structure', room, 'fit', solid=True))
        if f.get('rainPipe'):
            px, py = f['rainPipe']
            p = _Mesh()
            p.pipe([(px, py + 0.30, zt - th), (px, py + 0.30, zt - th - 0.12), (px, py + 0.06, zt - th - 0.40),
                    (px, py + 0.06, 0.10)], 0.068, 'pipe_black')
            objs.append(p.obj(ctx, f'{room}.rainpipe', room, 'fit', solid=True, smooth=True))
        if f.get('lantern'):                                        # coach lantern on a scroll bracket (balcony.md 5)
            lx, ly, lz = f['lantern']
            l = _Mesh()
            l.box((lx - 0.05, ly, lz + 0.10), (lx + 0.05, ly + 0.015, lz + 0.20), S)
            l.pipe([(lx, ly, lz + 0.15), (lx, ly + 0.13, lz + 0.19), (lx, ly + 0.13, lz + 0.125)], 0.015, S, n=6)
            for (h0, w0), (h1, w1), k in (((-0.125, 0.05), (0.075, 0.08), 'lamp_amber'), ((0.075, 0.10), (0.125, 0.02), S),
                                          ((-0.14, 0.06), (-0.125, 0.06), S)):
                q = [Vector((lx + sx * w, ly + 0.13 + sy * w, lz + h)) for h, w in ((h0, w0), (h1, w1))
                     for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
                for i in range(4):
                    l.face([q[i], q[(i + 1) % 4], q[4 + (i + 1) % 4], q[4 + i]], k)
                l.face(q[:4], k)
                l.face(q[4:], k)
            objs.append(l.obj(ctx, f'{room}.lantern', room, 'fit', solid=True))
    return objs


# ---------------------------------------------------------------- entry point
def build(ctx):
    """Build the whole envelope into the scene; returns the objects. Rooms: facade, roof, balcony."""
    global _CTX
    _CTX = ctx
    vols, ops, meshes = _vols(ctx), _ext_openings(ctx), {}
    objs, banded = _front_trim(ctx)
    _skin(ctx, vols, ops + _pier_panels(ctx, meshes), meshes)
    _reveals(ctx, ops, meshes, banded)
    steps = meshes.setdefault('returns', _Mesh())
    objs += _roof(ctx, vols, steps)
    for o in ops:                                                   # the board under the French doors (rear 2)
        if o['fr']['type'] == 'french_door' and o['fr']['level'] == 'G':
            fr = o['fr']
            fid = _finish(ctx, o['p0'], tuple(fr['outward']))[0] or 'returns'
            out, al = Vector((fr['outward'][0], fr['outward'][1], 0)), Vector((fr['along'][0], fr['along'][1], 0))
            meshes.setdefault(fid + '.sills', _Mesh()).box(
                (-fr['width'] / 2 - 0.18, -fr['ext_reveal'], o['z0'] - 0.10), (fr['width'] / 2 + 0.18, 0.05, o['z0']),
                'sill_board', (Vector((o['p0'][0], o['p0'][1], 0)), al, out, Vector((0, 0, 1))))
    for key, m in meshes.items():
        sills = key.endswith('.sills')
        objs.append(m.obj(ctx, f'facade.{key}', 'facade', 'trim' if sills else 'shell', solid=sills))
    objs += _roof_windows(ctx) + _chimney(ctx) + _pipes(ctx) + _balcony(ctx)
    objs = [o for o in objs if o]
    tris = sum(len(p.vertices) - 2 for o in objs for p in o.data.polygons)
    print(f'[envelope] {len(objs)} objects, {tris} triangles')
    return objs

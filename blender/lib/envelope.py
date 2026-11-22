"""Envelope (blender/MULTILEVEL.md section 7): the outside of the house. Outer skin with holes, reveals and sills,
roof slabs (upper envelope of roof.planes), roof steps, fascias, gutters, ridges, valleys, roof windows, chimney stack,
the external-insulation foot, pipes and the steel balcony; the street-front trim is lib/envelope_front.py. Reads
exterior.envelope / facades, roof, features and ctx.opening_frame only; needs no shell and no site. API: build(ctx),
roof_surface(x, y). Notes: blender/lib/README.md.

Literal positions that are not in house.json (pipes, sills, the porch soffit) come from spec/phase3/briefs/envelope.md
and spec/phase2/*_elevation.md and are kept in the tables below."""
import math

import bmesh
import bpy
from mathutils import Vector

from . import ctx as C
from . import interact as IX
from . import materials as M

EPS = 0.002
STEP = 0.01             # sampling step along a wall when looking for changes (features narrower than this are lost)
CHIMNEY_SHAFT, CHIMNEY_HAUNCH = 0.26, 0.29   # brick shaft width, haunch reach east of it at roof level
PLINTH_TOP = -0.08      # black plinth band on the rendered faces (rear_elevation.md 5: Z -0.30 .. -0.08)
BRICK_X = -0.77         # rear_R: the neighbour's stock brick west of this x (junction 4.22 from the flank corner, envelope-04)
PORCH_SOFFIT = (-0.12, 2.63, -0.55, 2.40)   # raked boarded canopy soffit: (y, z) at the door head and at the fascia
PORCH_VERGE = 0.25      # depth of the boxed verge board of the lean-to behind the front plane
SILL = dict(t=0.07, out=0.06, side=0.06, mat='sill_stone')
SILLS = {               # per opening (brief (b), v11 / v13 / v2): thickness, projection, beyond each jamb, material
    'w_wc': dict(t=0.10, out=0.07, side=0.08),
    'w_utility': dict(t=0.03, out=0.035, side=0.05, mat='upvc_white'),
    'w_dining_e_s': dict(t=0.10, side=0.06), 'w_dining_e_n': dict(t=0.10, side=0.06),
    'w_study': dict(t=0.14, out=0.06, side=0.10),
}
GUTTER = dict(w=0.114, h=0.075, t=0.008, drop=0.03, drop_porch=0.05)
GUTTER_BRACKET = 0.6     # fascia bracket spacing (v8 f126)
TRANSOM = 0.13          # masonry transom of the ground-floor bay lights (front_elevation.md 2.2: Z 1.80 .. 1.93)
EDGE_TRIM = (0.035, 0.03)   # flat-roof edge trim on a fascia board: height above it, projection (rear_elevation.md 3)
RIDGE = dict(w=0.15, h=0.03, t=0.018, joint=0.45)  # ridge tiles: half width, rise above the apex, thickness, length
VALLEY_W = 0.10         # lead valley lining, each side of the valley line

# key -> (hex, roughness) used when materials.mat(key) does not know the key (the spec colours win over the hex)
FALLBACK = {
    'white_masonry_paint': ('#F2F2EE', 0.9), 'render_sandstone': ('#D2C596', 0.9), 'plinth_black': ('#2A2A2C', 0.8),
    'slate': ('#474A52', 0.7), 'fibre_cement_slate': ('#4B4E57', 0.75), 'flat_felt': ('#3A3C40', 0.9),
    'roof_underside': ('#6B5A45', 0.9), 'stock_brick_grey': ('#A99873', 0.9), 'red_brick': ('#A4553A', 0.9),
    'red_brick_dark': ('#7A4A3C', 0.9), 'steel_chequer_plate': ('#3A3C40', 0.45),
    'sill_stone': ('#EDEDE8', 0.8), 'pipe_black': ('#18181A', 0.35), 'pipe_old': ('#3A3B3E', 0.6),
    'steel_black': ('#33373A', 0.5), 'rail_grey': ('#6B7076', 0.45), 'dormer_panel': ('#3F4146', 0.6),
    'sill_board': ('#4A3F38', 0.7), 'lead': ('#7C8087', 0.6), 'lead_dark': ('#45484E', 0.6), 'velux_grey': ('#5A5D62', 0.5),
    'lamp_amber': ('#E8B45A', 0.3), 'ridge_tile': ('#3D3F45', 0.7), 'chimney_render': ('#8E8C86', 0.9),
    'velux_white': ('#F4F3EF', 0.35),           # roof-window frame / sash faces below the roof plane (v5 hr_313, hr_194)
    'edge_trim': ('#5F6066', 0.5),              # dark flat-roof edge trim over the white fascia (v2 t248.5)
    'fascia_white': ('#DBD9DB', 0.5), 'pipe_grey': ('#B9BBB8', 0.5),
}

# brief (b) and rear_elevation.md 5.3 / 6: (material, diameter, square, [(x, y, z), ...]);
# z None = on the paving, 'porch' = on the lean-to roof. Flank face x 3.45, face K y 9.03, rear y 17.36.
PIPES = [
    # main rear slope over K: between the treads' east end (4.38) and the corner, its shoe over the gully (4.45, 9.12)
    ('pipe_black', 0.068, False, [(4.45, 9.15, -0.21), (4.45, 9.08, -0.13), (4.45, 9.08, 6.08)]),
    ('pipe_black', 0.068, False, [(3.50, 9.08, 3.35), (3.50, 9.08, 8.58)]),                # flank gutter, F / K corner
    ('pipe_black', 0.110, False, [(4.25, 9.10, 3.30), (3.52, 9.10, 3.30), (3.52, 12.07, 3.10)]),   # first-floor soil branch
    ('pipe_black', 0.050, False, [(3.49, 13.40, 4.05), (3.49, 12.20, 3.45)]),              # second branch
    ('pipe_old', 0.110, False, [(3.52, 9.70, -0.20), (3.52, 12.07, -0.20)]),               # old drain along the foot
    # twin black ribbed a/c conduits: rear wall 0.35 under the study sill, then up the party side to the roof edge;
    # flank from the K corner at second-floor sill level, dropping north of the yellow-room window to Z 3.9
    ('pipe_black', 0.045, False, [(3.45, 17.39, 6.27), (0.28, 17.39, 6.27), (0.28, 17.39, 8.60)]),
    ('pipe_black', 0.045, False, [(3.45, 17.39, 6.22), (0.22, 17.39, 6.22), (0.22, 17.39, 8.60)]),
    ('pipe_black', 0.045, False, [(3.475, 9.03, 6.74), (3.475, 11.05, 6.74), (3.475, 11.05, 3.90), (3.475, 14.95, 3.90)]),
    ('pipe_black', 0.045, False, [(3.475, 9.03, 6.69), (3.475, 11.00, 6.69), (3.475, 11.00, 3.85), (3.475, 14.95, 3.85)]),
    ('upvc_white', 0.065, True, [(-0.78, -0.17, 0.06), (-0.78, -0.17, 2.02), (-0.78, -0.58, 2.36), (-0.78, -0.675, 2.44)]),  # canopy: running outlet, offset back to the wall
    ('upvc_white', 0.065, True, [(0.62, -0.08, 'porch'), (0.68, -0.02, 3.30), (0.68, -0.02, 6.25), (0.55, -0.02, 6.42)]),  # gable west eaves down the bay west cheek corner (v8 f126): shoe on the lean-to
    ('upvc_white', 0.065, True, [(4.295, -0.02, None), (4.295, -0.02, 6.25), (4.41, -0.02, 6.42)]),  # gable east eaves down the east cheek, 0.10 behind the corner
]
# small boxes on the walls (brief (b)): (material, centre (x, y, z), size (x, y, z))
FITTINGS = [
    ('upvc_white', (3.49, 12.57, 8.32), (0.08, 0.16, 0.16)),        # square extractor outlet over the bathroom2 window
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
    rail = {f['id']: f['insulation']['baseRailZ'][0] for f in ext['facades'] if 'insulation' in f}

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
                op = tuple(i for i, o in enumerate(mine)        # EPS narrower: the skin meets the reveal (_reveals)
                           if abs((x - o['p0'][0]) * ux + (y - o['p0'][1]) * uy) < o['fr']['width'] / 2 - EPS)
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
                for i in op:                                    # no slot onto the room's own jamb at the arris
                    polys = _cut(polys, s0, s1, [mine[i]['z0'] + EPS] * 2, [mine[i]['z1'] - EPS] * 2)
                if fid in rail:                                 # insulated: the old face below the rail (_insulation)
                    polys = _cut(polys, s0, s1, (-99.0, -99.0), [rail[fid]] * 2)
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
            k = dict(SILL, **SILLS.get(o['id'], {}))
            sm.box((-wf - k['side'], 0, z0 - k['t']), (wf + k['side'], k['out'], z0), k['mat'], F)
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


def _ceilings(ctx):
    """[(room id, room polygon, [ceiling plane dicts])] of the top level's rooms that have a ceiling of their own: the
    slab underside stays 1 cm above ctx.ceil_z there where the roof is steeper than the ceiling (front loft), and
    over an under_roof room with a lining `offset` (eaves: the slab thins to 0.16 over eaves_front, whose lining is
    0.17 under the roof; its planes / ceilingZ only add cut lines, roof + offset runs parallel to the roof)."""
    out = []
    for rid, r in ctx.rooms.items():
        c = r.get('ceiling') or {}
        if r.get('level') != ctx.levels[-1] or ctx.kind(rid) == 'exterior' or \
                (c.get('type') == 'under_roof' and 'offset' not in c):
            continue
        pl = list(c.get('planes', []))
        if r.get('ceilingZ') is not None:
            pl.append(dict(polygon=ctx.room_poly(rid), z=dict(c0=float(r['ceilingZ']), cx=0, cy=0)))
        if pl:
            out.append((rid, [tuple(q) for q in ctx.room_poly(rid)], pl))
    return out


def porch_soffit_z(y):
    """Z of the raked canopy soffit (PORCH_SOFFIT) at y: the canopy downlights (rooms/vestibule.py) sit on it."""
    y0, z0, y1, z1 = PORCH_SOFFIT
    return z0 + (y - y0) * (z1 - z0) / (y1 - y0)


def _roof(ctx, vols, steps):
    """Roof slabs: the upper envelope of the planes (cut along valleys and at every higher plane), fascias on free
    edges, soffits, undersides in the roof voids, gutters on pitched eaves. steps: _Mesh for the roof-step skin."""
    roof = ctx.spec['roof']
    wins = [f for f in ctx.features if f['type'] in ('roof_window', 'roof_opening')]
    floors = sorted({v['z0'] for v in vols if v['level'] == ctx.levels[-1]})
    ceils = _ceilings(ctx)
    gid = (roof.get('gable') or {}).get('id', '-')
    objs, gutters, runs, verge = [], {}, [], _Mesh()

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
            if not ground:                                  # where the underside would meet a ceiling of the top level
                for _, poly, cps in ceils:
                    lines.update(_edge_lines(poly))
                    for cp in cps:
                        lines.update(_edge_lines([tuple(q) for q in cp['polygon']]))
                        cz = cp['z']
                        lines.add(_line(pz['cx'] - cz['cx'], pz['cy'] - cz['cy'],
                                        cz['c0'] + 0.01 + ctx.roof_slab_t(p['id']) - pz['c0']))
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
                    if zf is None:                          # the canopy's raked boarded soffit
                        m.face([(q.x, q.y, porch_soffit_z(q.y)) for q in pts], 'upvc_white', (0, 0, -1))
                elif zf is None:                            # overhang: soffit
                    m.face([q + down for q in pts], 'upvc_white', (0, 0, -1))
                elif c.z - t >= zf - 1e-4:                  # inside the roof void, above the top floor
                    rid = next((r for r, poly, _ in ceils if C.point_in_poly(c.x, c.y, poly)), None)

                    def lift(q):                            # the ceiling of THIS face's side: a vertex on a ceiling
                        if not rid:                         # step line (flat 8.61 / lobby 8.57 at y 5.38) is read
                            return q.z - t                  # 10 um in toward the face centre, else it takes the
                        d = (c - q).to_2d()                 # lower side and the slab dips through the higher one
                        d = d / d.length * 1e-5 if d.length > 1e-9 else d
                        return max(q.z - t, ctx.ceil_z(rid, q.x + d.x, q.y + d.y) + 0.01)
                    m.face([(q.x, q.y, lift(q)) for q in pts], 'roof_underside', (0, 0, -1))
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
                        if ground:                          # down to the soffit in front, a boxed verge behind
                            front = mid.y < PORCH_SOFFIT[0]
                            lo = lambda q: Vector((q.x, q.y, porch_soffit_z(q.y) if front else q.z - PORCH_VERGE))
                            m.face([a, b, lo(b), lo(a)], 'upvc_white', (n.x, n.y, 0))
                        else:
                            m.face([a, b, b + down, a + down], 'pipe_black' if black else 'upvc_white', (n.x, n.y, 0))
                        slope = Vector((p['z']['cx'], p['z']['cy']))
                        if pitched and abs(a.z - b.z) < 1e-4 and slope.dot(n) < 0:
                            off = Vector((n.x, n.y, 0)) * (GUTTER['w'] / 2 + 0.004) - \
                                Vector((0, 0, GUTTER['drop_porch' if ground else 'drop']))
                            runs.append([(ev['id'] if ev else p['id'], black), a + off, b + off])
                    if not ground and pitched and abs(a.z - b.z) > 1e-3 and n.x > 0.5 and not p['id'].startswith(gid) \
                            and not oth:                    # black dry verge on the blank east gable end
                        verge.prism([(-0.012, -0.06), (0.035, -0.06), (0.035, 0.025), (-0.012, 0.025)], a, b, 'pipe_black')
            ob = m.obj(ctx, f"roof.{p['id']}", 'roof', 'shell')
            if ob:
                if abs(p['z']['cx']) > abs(p['z']['cy']):   # slate courses run along the eaves
                    M.uv_box(ob, rotate=True)
                objs.append(ob)
        bm.free()

    merged = True                                           # one run per straight eave (the slab is cut into pieces)
    while merged:
        merged = False
        for r in runs:
            q = next((q for q in runs if q is not r and q[0] == r[0] and (q[1] - r[2]).length < 1e-4
                      and abs((r[2] - r[1]).normalized().dot((q[2] - q[1]).normalized())) > 0.9999), None)
            if q:
                r[2] = q[2]
                runs.remove(q)
                merged = True
                break
    runs = [r for r in runs if (r[2] - r[1]).length > 0.05]    # no stubs
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

    objs.append(verge.obj(ctx, 'roof.verge', 'roof', 'trim', solid=True))
    m = _Mesh()                                             # angled ridge tiles bedded on the two slopes, joint every 0.45
    ridges = [(roof['ridge']['line'], roof['ridge']['z'])]
    if roof.get('gable'):
        ridges.append((roof['gable']['ridge'], roof['gable']['ridgeZ']))
    w, h, t, jl = RIDGE['w'], RIDGE['h'], RIDGE['t'], RIDGE['joint']
    for (a, b), z in ridges:
        a, b = Vector((a[0], a[1], z)), Vector((b[0], b[1], z))
        d = (b - a).normalized()
        s = d.cross(Vector((0, 0, 1)))                      # the prism's +u
        mid = (a + b) / 2
        dr = [z - (ctx.roof_z(*(mid + s * sg * w).xy) or z - 0.6 * w) for sg in (1, -1)]
        prof = [(-w, -dr[1]), (0, h), (w, -dr[0]), (w, -dr[0] - t), (0, h - 1.4 * t), (-w, -dr[1] - t)]
        L, k = (b - a).length, 0
        while k * jl < L - 1e-3:
            m.prism(prof, a + d * (k * jl), a + d * min(L, (k + 1) * jl - 0.006), 'ridge_tile')
            k += 1
    objs.append(m.obj(ctx, 'roof.ridge', 'roof', 'trim', solid=True))
    objs.append(_valleys(ctx, gid))
    return objs


def _valleys(ctx, gid):
    """Lead lining along the valleys of the bay gable (its plane edges that run neither along x nor along y)."""
    m = _Mesh()
    for p in ctx.spec['roof']['planes']:
        if not p['id'].startswith(gid):
            continue
        poly = [tuple(q) for q in p['polygon']]
        for a, b in zip(poly, poly[1:] + poly[:1]):
            if abs(a[0] - b[0]) < 1e-6 or abs(a[1] - b[1]) < 1e-6:
                continue
            a, b = Vector(a), Vector(b)
            n = Vector(((b - a).y, -(b - a).x)).normalized() * VALLEY_W
            for sg in (1, -1):
                q = [a, b, b + n * sg, a + n * sg]
                z = [ctx.roof_z(*v) for v in q]
                if None not in z:
                    m.face([(v.x, v.y, zz + 0.004) for v, zz in zip(q, z)], 'lead', (0, 0, 1))
    return m.obj(ctx, 'roof.valleys', 'roof', 'trim')


def _gutter(m, a, b, black):
    """Open gutter with its top edge on the line a -> b, a fascia bracket (a U strap under it) every GUTTER_BRACKET."""
    w, h, t = GUTTER['w'] / 2, GUTTER['h'], GUTTER['t']
    prof = [(-w, -h), (w, -h), (w, 0), (w - t, 0), (w - t, t - h), (t - w, t - h), (t - w, 0), (-w, 0)]
    mat = 'pipe_black' if black else 'upvc_white'
    m.prism(prof, a, b, mat)
    k = 0.004
    strap = [(-w - k, 0), (-w - k, -h - k), (w + k, -h - k), (w + k, 0), (w, 0), (w, -h), (-w, -h), (-w, 0)]
    L, d = (b - a).length, (b - a).normalized()
    for i in range(1, int(L / GUTTER_BRACKET) + 1):
        c = a + d * min(i * GUTTER_BRACKET - GUTTER_BRACKET / 2, L - 0.05)
        m.prism(strap, c - d * 0.0125, c + d * 0.0125, mat)


def _clips(m, pts, d, mat, sq):
    """Pipe clips along each straight run longer than 0.6: every 0.9 on conduits (saddle clips), 1.7 on downpipes."""
    gap = 0.9 if d < 0.05 else 1.7
    for a, b in zip(pts, pts[1:]):
        a, b = Vector(a), Vector(b)
        L = (b - a).length
        if L < 0.6:
            continue
        u = (b - a) / L
        s = 0.3
        while s < L - 0.2:
            c = a + u * s
            m.pipe([c - u * 0.015, c + u * 0.015], d + 0.012, mat, square=sq)
            s += gap


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
            m.box(lo, (hi[0], hi[1], 0.0), 'velux_white', fr)      # white painted inside, grey cladding above the slates
            m.box((lo[0], lo[1], 0.0), hi, 'velux_grey', fr)
        objs.append(m.obj(ctx, name + '.frame', 'roof', 'fit', solid=True))
        s, b = _Mesh(), 0.05                                # sash: four rails and the pane
        for lo, hi in (((k, k, 0.0), (W - k, k + b, 0.045)), ((k, H - k - b, 0.0), (W - k, H - k, 0.045)),
                       ((k, k + b, 0.0), (k + b, H - k - b, 0.045)), ((W - k - b, k + b, 0.0), (W - k, H - k - b, 0.045))):
            s.box(lo, (hi[0], hi[1], 0.018), 'velux_white', fr)
            s.box((lo[0], lo[1], 0.018), hi, 'velux_grey', fr)
        s.box((k + b, k + b, 0.018), (W - k - b, H - k - b, 0.030), 'glass_clear', fr)
        yh = H - k - b / 2 if cy < 0 else k + b / 2        # operating bar on the rail opposite the hinge (v5 hr_194)
        s.box((W / 2 - 0.175, yh - 0.011, -0.028), (W / 2 + 0.175, yh + 0.011, 0.0), 'silver_satin', fr)
        sash = s.obj(ctx, name + '.sash', 'roof', 'joinery', solid=True, lm='dynamic')
        top_low = cy < 0                                    # the hinge is on the high edge
        hinge = fr[0] + ex * (W / 2) + ey * (k if top_low else H - k) + en * 0.025
        IX.tag(sash, 'hinge', p=hinge, a=(1, 0, 0), deg=f.get('angle', 30) * (1 if top_low else -1),
               label='Roof window', reach=2.2, excl=[f"{f['room']}.velux_blind"] if f.get('room') else [])
        objs.append(sash)
    return objs


def _chimney(ctx):
    """Stacks of roof.chimneys above the roof only (below it the pier is the neighbour's brick). The brick shaft is
    CHIMNEY_SHAFT wide from the polygon's west side, under a stone cap; the rest of the polygon is a rendered haunch
    sloping from under the cap down to the roof, reaching CHIMNEY_HAUNCH east of the shaft (v2 t248.5, envelope-04)."""
    objs = []
    for cid in ctx.spec['roof'].get('chimneys', []):
        f = next(q for q in ctx.spec['exterior']['features'] if q['id'] == cid)
        xs, ys = [q[0] for q in f['polygon']], [q[1] for q in f['polygon']]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        zr = max(z for z in (ctx.roof_z(x, y) for x in (x0, x1) for y in (y0, y1)) if z is not None)
        zt, xb = f['z'][1], min(x1, x0 + CHIMNEY_SHAFT)
        m = _Mesh()
        m.box((x0, y0, zr - 0.02), (xb, y1, zt - 0.07), 'stock_brick_grey')
        m.box((x0 - 0.03, y0 - 0.03, zt - 0.07), (xb + 0.03, y1 + 0.03, zt), 'sill_stone')
        P = [(xb, zr - 0.02), (xb + CHIMNEY_HAUNCH, zr - 0.02), (xb + CHIMNEY_HAUNCH, zr + 0.01), (xb, zt - 0.09)]
        m.prism([(-x, z) for x, z in P], (0, y1, 0), (0, y0, 0), 'chimney_render')
        objs.append(m.obj(ctx, f'roof.{cid}', 'roof', 'shell', solid=True))
    return objs


def _insulation(ctx, meshes):
    """External wall insulation (facades[].insulation): the render stops at the base rail; below it the old face,
    `proud` further in, painted `below`; a white bell-cast bead along the foot and a white stop board at the south end
    (brief (b), v8 f77-79)."""
    for f in ctx.spec['exterior']['facades']:
        ins = f.get('insulation')
        if not ins or f['axis'] != 'x':
            continue
        (xa, ya), (_, yb) = _facade_line(f)
        n = _facade_n(f)[0]
        x0, (zr0, zr1) = ins['oldFace'], ins['baseRailZ']
        gz = [ctx.ground_z(xa + n * 0.1, ya + (yb - ya) * k / 20) for k in range(21)]
        base = min([g for g in gz if g is not None] or [zr0 - 0.25]) - 0.05
        meshes.setdefault(f['id'], _Mesh()).face([(x0, ya, base), (x0, yb, base), (x0, yb, zr0), (x0, ya, zr0)],
                                                 ins.get('below', 'plinth_black'), (n, 0, 0))
        tm = meshes.setdefault(f['id'] + '.sills', _Mesh())
        h = zr1 - zr0
        bead = [(-ins['proud'], 0), (0.035, 0), (0.035, 0.008), (0.012, h * 0.5), (0.004, h), (-ins['proud'], h)]
        a, b = sorted((ya, yb), key=lambda v: n * v)        # travel so that the prism's +u is outward
        tm.prism(bead, (xa, a, zr0), (xa, b, zr0), 'upvc_white')
        ys = min(ya, yb)                                            # stop under the rail at the south end
        tm.box((min(x0, xa + n * 0.025), ys, base), (max(x0, xa + n * 0.025), ys + 0.04, zr0), 'upvc_white')


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
        m, (z0, z1), dd = _Mesh(), f['z'], f['diameter']
        zg = z1 - (z1 - z0) / 3                                     # top third weathered pale grey (v11 f_0170)
        m.pipe([(x, y, z0), (x, y, zg)], dd, 'pipe_black', n=12)
        m.pipe([(x, y, zg), (x, y, z1)], dd, 'pipe_grey', n=12)
        z = z0 + 1.0
        while z < z1 - 0.3:                                         # ring-seal sockets every 1.75
            m.pipe([(x, y, z), (x, y, z + 0.12)], dd + 0.024, 'pipe_black' if z < zg else 'pipe_grey', n=12)
            z += 1.75
        m.pipe([(x, y, z1), (x, y, z1 + 0.14)], dd + 0.02, 'pipe_grey', n=8)        # cage cowl
        zb = (ctx.ground_z(x, y) if ctx.ground_z(x, y) is not None else z0) + 0.35
        m.pipe([(x, y, zb), (x, y - 0.11, zb)], 0.07, 'pipe_black', n=10)            # capped access boss, south side
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
        if g is not None and z < g + 0.5 and math.dist(pts[1][:2], (x, y)) < 0.15 and \
                max(p[2] for p in pts[:3]) - z > 1.0:                   # a downpipe to the ground (maybe with a shoe)
            m, n = _Mesh(), n + 1
            m.pipe(pts, d, mat, square=sq)
            _clips(m, pts, d, mat, sq)
            ob = m.obj(ctx, f'facade.downpipe.{n}', 'facade', 'fit', solid=True, smooth=True)
            ob['plan_sym'] = 'pipe'
            objs.append(ob)
            continue
        by.setdefault(mat, _Mesh()).pipe(pts, d, mat, square=sq)
        _clips(by[mat], pts, d, mat, sq)
    for mat, m in by.items():
        objs.append(m.obj(ctx, f'facade.pipes.{mat}', 'facade', 'fit', solid=True, smooth=True))
    m = _Mesh()
    for mat, (x, y, z), (sx, sy, sz) in FITTINGS:
        m.box((x - sx / 2, y - sy / 2, z - sz / 2), (x + sx / 2, y + sy / 2, z + sz / 2), mat)
    objs.append(m.obj(ctx, 'facade.fittings', 'facade', 'fit', solid=True))
    return objs


# ---------------------------------------------------------------- balcony
def _balcony(ctx):
    """Chequer-plate deck (the room's floor), channel frame and soffit, railing, wall posts and struts, rain pipe. A
    railing with section 'round_tube' has round posts and top rail in mid grey with collars at the joints and thin black
    bars on a flat bottom rail (v13 t214)."""
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
        for x in [x0 + 0.03 + k * 0.25 for k in range(int((x1 - x0 - 0.06) / 0.25) + 1)]:     # screw heads on the edges
            for y in (y0 + 0.03, y1 - 0.03):
                m.box((x - 0.006, y - 0.006, zt), (x + 0.006, y + 0.006, zt + 0.003), S)
        r = f['railing']
        H, ps, bar = r['height'], r['post'], r['bar']
        tube = r.get('section') == 'round_tube'
        RL, BR = ('rail_grey', 'pipe_black') if tube else (S, S)
        cl = lambda x, y: (min(max(x, x0 + ps / 2), x1 - ps / 2), min(max(y, y0 + ps / 2), y1 - ps / 2))
        posts = [cl(*q) for q in r['posts']]
        zr = zt + H - ps / 2                                        # top rail axis
        for x, y in posts:
            if tube:
                m.pipe([(x, y, zt), (x, y, zr)], ps, RL, n=12)
                m.pipe([(x, y, zr - 0.05), (x, y, zr + 0.03)], ps + 0.012, RL, n=12)      # tee / elbow fitting
            else:
                m.box((x - ps / 2, y - ps / 2, zt), (x + ps / 2, y + ps / 2, zt + H - 0.04), S)
        yr, xa, xb = y1 - ps / 2, x0 + ps / 2, x1 - ps / 2
        runs = {'north': [(posts[i], posts[i + 1], r['barsPerFrontBay']) for i in range(len(posts) - 1)],
                'west': [((xa, y0), (xa, yr), r['barsPerSide'])], 'east': [((xb, y0), (xb, yr), r['barsPerSide'])]}
        for side in r['sides']:
            for a, b, n in runs[side]:
                a, b = Vector((a[0], a[1], zt)), Vector((b[0], b[1], zt))
                if tube:
                    m.pipe([a + Vector((0, 0, zr - zt)), b + Vector((0, 0, zr - zt))], ps, RL, n=12)
                else:
                    m.prism([(-0.03, H - 0.04), (0.03, H - 0.04), (0.03, H), (-0.03, H)], a, b, S)      # top rail
                m.prism([(-0.004, 0.10), (0.004, 0.10), (0.004, 0.14), (-0.004, 0.14)], a, b, BR)     # bottom rail
                for i in range(n):
                    q = a + (b - a) * ((i + 1) / (n + 1))
                    if tube:
                        m.pipe([(q.x, q.y, zt + 0.10), (q.x, q.y, zr - ps / 2)], bar, BR, n=6)
                    else:
                        m.box((q.x - bar / 2, q.y - bar / 2, zt + 0.14), (q.x + bar / 2, q.y + bar / 2, zt + H - 0.04), S)
            if side != 'north':                                     # wall brackets of the side rails
                x = xa if side == 'west' else xb
                for z in (zt + 0.12, zr):
                    m.box((x - 0.04, y0, z - 0.04), (x + 0.04, y0 + 0.006, z + 0.04), S)
        sup = f['supports']
        st = sup['struts']
        for px, py in sup['wallPosts']:                             # wall channels and 45-degree struts
            m.box((px - 0.05, py, sup['postZ'][0]), (px + 0.05, py + 0.04, sup['postZ'][1]), S)
            m.prism([(-0.03, -0.03), (0.03, -0.03), (0.03, 0.03), (-0.03, 0.03)],
                    (px, py + 0.03, st['fromZ']), (px, py + st['reach'], st['toZ'] - 0.03), S)
        objs.append(m.obj(ctx, f'{room}.structure', room, 'fit', solid=True, smooth=tube))
        if f.get('rainPipe'):
            px, py = f['rainPipe']
            p = _Mesh()
            p.pipe([(px, py + 0.30, zt - th), (px, py + 0.30, zt - th - 0.12), (px, py + 0.06, zt - th - 0.40),
                    (px, py + 0.06, 0.10)], 0.068, 'pipe_black')
            objs.append(p.obj(ctx, f'{room}.rainpipe', room, 'fit', solid=True, smooth=True))
        # the coach lantern (f['lantern']) is rooms/balcony.py's: a lamp with its switch, not envelope massing
    return objs


# ---------------------------------------------------------------- entry point
def build(ctx):
    """Build the whole envelope into the scene; returns the objects. Rooms: facade, roof, balcony."""
    global _CTX
    _CTX = ctx
    from . import envelope_front as EF                             # it imports this module: not at the top
    vols, ops, meshes = _vols(ctx), _ext_openings(ctx), {}
    objs, banded = EF.build(ctx)
    _skin(ctx, vols, ops + EF.pier_panels(ctx, meshes), meshes)
    _reveals(ctx, ops, meshes, banded)
    _insulation(ctx, meshes)
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

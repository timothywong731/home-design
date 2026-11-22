"""Cross-sections cut from the built model -> sections.json, next to footprints.json (tools/plan/draft.py drafts them).

    blender -b --factory-startup build/home.blend --python blender/export_sections.py -- --out docs/assets [--house spec/house.json]

export.py calls write() on every export, so the sections follow the model with no extra step. The planes are data:
tools/plan/section_planes.py (what each plane passes through; its position is derived from spec/house.json).

Per plane, in section coordinates (s = metres along the plane from the left end of the drawing, z = world Z):
- cut      what the plane cuts of the structure (kind 'shell': walls, floors, ceilings, flights, facade, roof, ground
           surfaces, fences, the shed) as closed outlines with holes, class 'fabric' or 'earth';
- rooms    the cut rooms: their clear outline, floor and ceiling as the model has them;
- fixtures joinery, trim and fittings cut by the plane (door leaves, frames, cabinets, sanitaryware): polylines per
           piece (`root` = its top parent, so the drafter can reduce a cut cabinet to its outline);
- beyond   what stands beyond the plane and is seen from it, hidden lines removed: outlines and creases of the
           structure, joinery, trim and fittings (kind 'fit' of FIT_MIN or more, and the parts of FIXED plan symbols);
           loose furniture, decor, light fittings and stored goods are neither drawn nor hide anything. The lines run
           over the plane's whole length (plot + margin), also where the frame of the cut was trimmed to the model:
           a chimney on the party line is drawn whole;
- hidden   rooms the plane misses (section_planes `hidden`), cut on a plane of their own: drawn dashed by the drafter.
           All the air inside the room's own box counts (claim()): a stair shaft shares its plan with the flight
           above it.

How the cut becomes closed outlines. The shell is open surfaces whose normals face the air (rooms, outside), so a cut
is loose segments, each knowing its air side. The s axis is split into slabs at every segment end and crossing; in a
slab the segments are ordered by height, and air is exactly what lies above an upward-facing segment and below the
next, downward-facing one (and above the topmost upward one: the sky). Everything else is solid. That needs no closed
loops, so a 1 mm gap in the model costs a 1 mm sliver, not a leak. Solid is 'fabric' inside the mass the shell was
carved from (the envelope blocks of house.json, each storey from shell.SLAB below its lowest floor) and above the
ground line; below the ground line and outside that mass it is 'earth'. Air inside a room of house.json carries the
room's id. The outlines of each class are then traced along the slab edges.
"""
import argparse
import bisect
import importlib.util
import json
import math
import sys
import time
from pathlib import Path

import bpy
import numpy as np
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
T0 = time.time()

SKIP_ROOMS = {'neighbours'}                      # context massing: not part of the drawing, hides nothing
# plan symbols of the fixed pieces that explain a room in section (their children: doors, handles, taps come along)
FIXED = {'base_unit', 'wall_unit', 'tall_unit', 'worktop', 'hob', 'sink', 'sink_belfast', 'fridge', 'oven_tower',
         'washer', 'dryer', 'wc', 'basin', 'vanity', 'bath', 'shower', 'sauna', 'boiler', 'cylinder', 'fireplace',
         'radiator', 'towel_rail'}
NOT_DRAWN = {'tv', 'mirror', 'airer'}            # wall- and ceiling-hung things that are no part of the building
STORED = {'stock'}                               # <room>.<this>: goods kept in a room, tagged 'fit' by their module
FIT_MIN = 0.30          # m: a fitting smaller than this is electrical / hardware clutter at drawing scale ...
FIT_PART = 0.08         # ... unless it is part of a FIXED piece (doors, handles, pans, cisterns of a fitting)
CLASSES = ('shell', 'joinery', 'trim', 'fit')
CREASE = {'shell': 30.0, 'joinery': 50.0, 'trim': None, 'fit': 50.0}   # deg between faces drawn as a line; None: outline only
MIN_CREASE = 0.04       # m: shorter creases are detail below drawing scale (turned work, beads); outlines always stay
FACING = 0.02           # |normal . view| below this: the face is seen edge-on
STEP = 0.02             # m between visibility samples along an edge
EPS = 1e-3              # m a visibility ray starts off the surface its edge lies on
DEPTH = 1.0             # m of earth kept below the lowest floor (the drafter trims the hatch to a band)
SKY = 1.0               # m of air kept above the highest point
SIMPLIFY = 0.0015       # m: polylines of the lines beyond are simplified to this


def log(msg):
    print(f'[sections {time.time() - T0:6.1f}s] {msg}', flush=True)


def planes_module():
    spec = importlib.util.spec_from_file_location('section_planes', ROOT / 'tools' / 'plan' / 'section_planes.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ------------------------------------------------------------------ the model as arrays
class Model:
    """World-space triangles (the cut, the occluders) and polygon edges (the lines beyond) of everything drawn."""

    def __init__(self):
        import export_bake as EB
        fixed = set()
        for o in bpy.context.scene.objects:
            if o.get('plan_sym') in FIXED:
                fixed.update([o.name] + [c.name for c in o.children_recursive])
        V, T, TP, PN, EV, EA, EB_, names, roots, pcls, pobj = [], [], [], [], [], [], [], [], [], [], []
        nv = npoly = 0
        for o in bpy.context.scene.objects:
            if o.type != 'MESH' or o.get('no_export') or EB.state1(o) or o.get('room') in SKIP_ROOMS:
                continue
            kind, me = o.get('kind'), o.data
            if kind not in CLASSES or not len(me.polygons) or o.get('plan_sym') in NOT_DRAWN or o.name.split('.')[-1] in STORED:
                continue
            if kind == 'fit' and max(o.dimensions) < (FIT_PART if o.name in fixed else FIT_MIN):
                continue                                           # sockets, switches, taps, knobs
            n, P, L = len(me.vertices), len(me.polygons), len(me.loops)
            co = np.empty(n * 3, np.float32)
            me.vertices.foreach_get('co', co)
            M = np.array(o.matrix_world, np.float64)
            V.append(co.reshape(-1, 3).astype(np.float64) @ M[:3, :3].T + M[:3, 3])
            pn = np.empty(P * 3, np.float32)
            me.polygons.foreach_get('normal', pn)
            pn = pn.reshape(-1, 3).astype(np.float64) @ np.linalg.inv(M[:3, :3])      # inverse transpose, row vectors
            PN.append(pn / np.maximum(np.linalg.norm(pn, axis=1, keepdims=True), 1e-12))
            me.calc_loop_triangles()
            nt = len(me.loop_triangles)
            t, tp = np.empty(nt * 3, np.int32), np.empty(nt, np.int32)
            me.loop_triangles.foreach_get('vertices', t)
            me.loop_triangles.foreach_get('polygon_index', tp)
            T.append(t.reshape(-1, 3) + nv)
            TP.append(tp + npoly)
            # polygon edges with the one or two polygons on them
            le, ls, lt = np.empty(L, np.int32), np.empty(P, np.int32), np.empty(P, np.int32)
            me.loops.foreach_get('edge_index', le)
            me.polygons.foreach_get('loop_start', ls)
            me.polygons.foreach_get('loop_total', lt)
            lp = np.repeat(np.arange(P, dtype=np.int32), lt)                    # loops are stored polygon by polygon ...
            if ls[0] != 0 or (np.diff(ls) != lt[:-1]).any():                    # ... and if ever they are not: the slow way
                for i in range(P):
                    lp[ls[i]:ls[i] + lt[i]] = i
            ev = np.empty(len(me.edges) * 2, np.int32)
            me.edges.foreach_get('vertices', ev)
            ev = ev.reshape(-1, 2)
            so = np.argsort(le, kind='stable')
            es, ps = le[so], lp[so]
            uniq, first, cnt = np.unique(es, return_index=True, return_counts=True)
            EV.append(ev[uniq] + nv)
            EA.append(ps[first] + npoly)
            EB_.append(np.where(cnt >= 2, ps[np.minimum(first + 1, L - 1)] + npoly, -1))
            names.append(o.name)
            top = o
            while top.parent:
                top = top.parent
            roots.append(top.name)
            pcls.append(np.full(P, CLASSES.index(kind), np.int8))
            pobj.append(np.full(P, len(names) - 1, np.int32))
            nv += n
            npoly += P
        self.V, self.T, self.TP = np.concatenate(V), np.concatenate(T), np.concatenate(TP)
        self.PN, self.EV = np.concatenate(PN), np.concatenate(EV)
        self.EA, self.EB = np.concatenate(EA), np.concatenate(EB_)
        self.pcls, self.pobj, self.names, self.roots = np.concatenate(pcls), np.concatenate(pobj), names, roots
        zs = self.V[self.T[self.pcls[self.TP] == 0]][:, :, 2]
        self.zrange = (round(float(zs.min()) - DEPTH, 2), round(float(zs.max()) + SKY, 2))     # of the structure, + margins
        self.bvh = BVHTree.FromPolygons(self.V.tolist(), self.T.tolist(), all_triangles=True)
        log(f'model: {len(names)} objects, {len(self.T)} triangles, {len(self.EV)} edges '
            f'({", ".join(f"{c} {int((self.pcls == i).sum())}" for i, c in enumerate(CLASSES))} polygons)')

    def cut(self, n3, c, origin, right):
        """Plane n3 . p = c through every triangle -> (segments (k, 4): s0 z0 s1 z1; air-side normals (k, 2); polygon
        index (k,)). Triangles lying in the plane give nothing."""
        d = self.V @ n3 - c
        d[np.abs(d) < 1e-9] = 1e-9
        dt = d[self.T]
        idx = np.nonzero((dt.min(1) < 0) & (dt.max(1) > 0))[0]
        a, da = self.T[idx], dt[idx]
        P = self.V[a]
        seg, k = np.zeros((len(idx), 2, 3)), np.zeros(len(idx), np.int64)
        with np.errstate(divide='ignore', invalid='ignore'):
            for i, j in ((0, 1), (1, 2), (2, 0)):
                rows = np.nonzero(da[:, i] * da[:, j] < 0)[0]
                t = da[rows, i] / (da[rows, i] - da[rows, j])
                seg[rows, k[rows]] = P[rows, i] + (P[rows, j] - P[rows, i]) * t[:, None]
                k[rows] += 1
        pol = self.TP[idx]
        s = (seg[:, :, :2] - np.asarray(origin)) @ np.asarray(right, float)
        out = np.round(np.stack([s[:, 0], seg[:, 0, 2], s[:, 1], seg[:, 1, 2]], 1), 4)
        nrm = np.stack([self.PN[pol, :2] @ np.asarray(right, float), self.PN[pol, 2]], 1)
        keep = (np.abs(out[:, 0] - out[:, 2]) + np.abs(out[:, 1] - out[:, 3])) > 1e-5
        return out[keep], nrm[keep], pol[keep]


# ------------------------------------------------------------------ slabs: solid, air, classes
class Slabs:
    """The cut of the structure as z-intervals per slab of s (module docstring): build() finds the air, classify()
    labels air and solid, rings() traces the closed outlines of a class."""

    def __init__(self, segs, nrm, frame, breaks=()):
        s0, z0, s1, z1 = self.frame = frame
        sw = segs[:, 0] > segs[:, 2]
        segs = np.where(sw[:, None], segs[:, [2, 3, 0, 1]], segs)
        flat = np.abs(segs[:, 2] - segs[:, 0]) > 1e-5              # not vertical: crosses columns
        H, up = segs[flat], nrm[flat][:, 1] > 0
        cuts = [segs[:, 0], segs[:, 2], np.asarray(list(breaks) + [s0, s1], float)]
        slope = (H[:, 3] - H[:, 1]) / (H[:, 2] - H[:, 0])
        icpt = H[:, 1] - slope * H[:, 0]
        for i in np.nonzero(np.abs(H[:, 3] - H[:, 1]) > 1e-6)[0]:  # where a sloped segment crosses another one
            with np.errstate(divide='ignore', invalid='ignore'):
                x = (icpt - icpt[i]) / (slope[i] - slope)
            ok = np.isfinite(x) & (x > max(H[i, 0], s0) + 1e-6) & (x < min(H[i, 2], s1) - 1e-6) & (x > H[:, 0] + 1e-6) & (x < H[:, 2] - 1e-6)
            cuts.append(x[ok])
        self.H, self.up, self.slope, self.icpt = H, up, slope, icpt
        self._cuts = cuts

    def add_zlines(self, zs):
        """Slab breaks where a sloped segment crosses one of the given levels (class boundaries inside solid)."""
        H, slope, icpt = self.H, self.slope, self.icpt
        sl = np.nonzero(np.abs(H[:, 3] - H[:, 1]) > 1e-6)[0]
        for z in zs:
            x = (z - icpt[sl]) / slope[sl]
            self._cuts.append(x[(x > H[sl, 0] + 1e-6) & (x < H[sl, 2] - 1e-6)])

    def build(self):
        s0, z0, s1, z1 = self.frame
        b = np.unique(np.round(np.concatenate(self._cuts), 4))
        b = b[(b >= s0 - 1e-9) & (b <= s1 + 1e-9)]
        self.b = b = b[np.concatenate([[True], np.diff(b) > 1e-5])]
        H, up = self.H, self.up
        self.air, self.cross = [], []
        for k in range(len(b) - 1):
            a, c = b[k], b[k + 1]
            act = np.nonzero((H[:, 0] <= a + 1e-9) & (H[:, 2] >= c - 1e-9))[0]
            zl, zr = self.icpt[act] + self.slope[act] * a, self.icpt[act] + self.slope[act] * c
            zl, zr = np.round(zl, 4), np.round(zr, 4)
            o = np.lexsort((up[act], np.round((zl + zr) / 2, 5)))   # by height; at one height the downward one first
            cr = [(float(zl[i]), float(zr[i]), bool(up[act][i])) for i in o]
            air = []
            for i, (l, r, u) in enumerate(cr):
                if u and i + 1 < len(cr) and not cr[i + 1][2]:
                    air.append((l, r, cr[i + 1][0], cr[i + 1][1]))
                elif u and i + 1 == len(cr):
                    air.append((l, r, z1, z1))
            self.air.append([q for q in air if q[2] - q[0] > 1e-6 or q[3] - q[1] > 1e-6])
            self.cross.append(cr)
        return self

    def is_air(self, s, z):
        """Past the ends of the frame: as in its end columns (what stands there is seen over the last thing cut)."""
        k = min(max(bisect.bisect_right(self.bl, s) - 1, 0), len(self.air) - 1)
        a, c = self.bl[k], self.bl[k + 1]
        t = min(max((s - a) / (c - a), 0.0), 1.0)
        for l0, r0, l1, r1 in self.air[k]:
            if l0 + (r0 - l0) * t - 1e-6 <= z <= l1 + (r1 - l1) * t + 1e-6:
                return True
        return False

    def classify(self, solid, air):
        """solid(k, smid) -> (mass intervals [(m0, m1)], ground (gl, gr) | None | inf); air(smid, zmid) -> (label,
        top, floor): air open to the sky carries a room's label only when it stands on that room's floor (a
        rooflight shaft; not the sky over a roof), and then only up to `top`: plain 'air' above.
        Fills self.iv[k] = [(lo_l, lo_r, hi_l, hi_r, label)] bottom to top, covering the frame."""
        s0, z0, s1, z1 = self.frame
        self.bl = [float(v) for v in self.b]
        self.iv = []
        for k in range(len(self.b) - 1):
            a, c = self.bl[k], self.bl[k + 1]
            sm = (a + c) / 2
            mass, g = solid(k, sm)
            out, lo = [], (z0, z0)

            def fill(lo, hi):                                      # a solid interval -> fabric / earth pieces
                if hi[0] - lo[0] < 1e-6 and hi[1] - lo[1] < 1e-6:
                    return
                marks = [((m, m)) for mm in mass for m in mm]
                if g is not None and g != math.inf:
                    marks.append(g)
                mid = lambda q: (q[0] + q[1]) / 2
                marks = sorted({q for q in marks if mid(lo) + 1e-6 < mid(q) < mid(hi) - 1e-6}, key=mid)
                edges = [lo] + marks + [hi]
                for p, q in zip(edges, edges[1:]):
                    zm = (mid(p) + mid(q)) / 2
                    inmass = any(m0 - 1e-9 <= zm <= m1 + 1e-9 for m0, m1 in mass)
                    under = g == math.inf and (not mass or zm < min(m0 for m0, _ in mass))       # below the house
                    earth = not inmass and (under or (g is not None and g != math.inf and zm < mid(g)))
                    q = (min(max(q[0], p[0]), hi[0]), min(max(q[1], p[1]), hi[1]))
                    out.append((p[0], p[1], q[0], q[1], 'earth' if earth else 'fabric'))
            for l0, r0, l1, r1 in self.air[k]:
                fill(lo, (l0, r0))
                if l1 >= z1 - 1e-9 and r1 >= z1 - 1e-9:             # open to the sky
                    lab, top, floor = air(sm, (l0 + r0) / 2 + 0.5)
                    if lab != 'air' and top is not None and max(l0, r0) < top < z1 and abs(min(l0, r0) - floor) < 0.3:
                        out += [(l0, r0, top, top, lab), (top, top, l1, r1, 'air')]
                    else:
                        out.append((l0, r0, l1, r1, 'air'))
                else:
                    out.append((l0, r0, l1, r1, air(sm, (l0 + r0 + l1 + r1) / 4)[0]))
                lo = (l1, r1)
            fill(lo, (z1, z1))
            merged = []
            for q in out:
                if merged and merged[-1][4] == q[4]:
                    merged[-1] = (*merged[-1][:2], q[2], q[3], q[4])
                else:
                    merged.append(q)
            self.iv.append(merged)

    # ---- outlines of one class
    def rings(self, want):
        """Closed outlines of the union of every interval whose label satisfies want(label) -> [(outer, [holes])]."""
        E = []                                                     # directed edges with the region on their left
        K = len(self.iv)
        r5 = lambda v: round(v, 5)
        for k in range(K):
            a, c = self.bl[k], self.bl[k + 1]
            for l0, r0, l1, r1, lab in self._merged(k, want):
                E.append(((a, l0), (c, r0)))
                E.append(((c, r1), (a, l1)))
        for k in range(K + 1):                                     # vertical edges on the slab boundaries
            x = self.bl[k]
            A = [(q[1], q[3]) for q in self._merged(k - 1, want)] if k > 0 else []
            B = [(q[0], q[2]) for q in self._merged(k, want)] if k < K else []
            for lo, hi in _minus(A, B):
                E.append(((x, lo), (x, hi)))                       # region on the -s side: upward
            for lo, hi in _minus(B, A):
                E.append(((x, hi), (x, lo)))
        E = [((r5(p[0]), r5(p[1])), (r5(q[0]), r5(q[1]))) for p, q in E]
        E = [e for e in E if e[0] != e[1]]
        start = {}
        for i, (p, q) in enumerate(E):
            start.setdefault(p, []).append(i)
        used, loops = [False] * len(E), []
        for i0 in range(len(E)):
            if used[i0]:
                continue
            loop, i = [], i0
            while not used[i]:
                used[i] = True
                p, q = E[i]
                loop.append(p)
                nxt = [j for j in start.get(q, ()) if not used[j]]
                if not nxt:
                    break
                din = math.atan2(q[1] - p[1], q[0] - p[0])

                def turn(j):                                       # left turns first: keeps to one region at a pinch
                    t = math.atan2(E[j][1][1] - q[1], E[j][1][0] - q[0]) - din
                    return (t + math.pi) % (2 * math.pi) - math.pi
                i = max(nxt, key=turn)
            if len(loop) >= 3 and E[i0][0] == q:
                loops.append(_tidy(loop))
        loops = [l for l in loops if len(l) >= 3 and abs(_area(l)) > 1e-7]
        outers = sorted([l for l in loops if _area(l) > 0], key=lambda l: abs(_area(l)))
        polys = [(o, []) for o in outers]
        for h in (l for l in loops if _area(l) < 0):
            (px, py), (qx, qy) = h[0], h[1]
            L = math.hypot(qx - px, qy - py)
            pt = ((px + qx) / 2 - (qy - py) / L * 1e-5, (py + qy) / 2 + (qx - px) / L * 1e-5)   # just inside the region
            for o, holes in polys:                                 # smallest outline that holds it
                if _inside(pt, o):
                    holes.append(h)
                    break
        return polys

    def _merged(self, k, want):
        out = []
        for q in self.iv[k]:
            if not want(q[4]):
                continue
            if out and abs(out[-1][2] - q[0]) < 1e-6 and abs(out[-1][3] - q[1]) < 1e-6:
                out[-1] = (*out[-1][:2], q[2], q[3], q[4])
            else:
                out.append(q)
        return out


def _minus(A, B):
    """1-D intervals of A not covered by B (both sorted lists of (lo, hi))."""
    out = []
    for lo, hi in A:
        cur = lo
        for b0, b1 in B:
            if b1 <= cur + 1e-7 or b0 >= hi - 1e-7:
                continue
            if b0 > cur + 1e-7:
                out.append((cur, b0))
            cur = max(cur, b1)
        if hi > cur + 1e-7:
            out.append((cur, hi))
    return out


def _area(l):
    return sum(p[0] * q[1] - q[0] * p[1] for p, q in zip(l, l[1:] + l[:1])) / 2


def _inside(pt, poly):
    x, y, c = pt[0], pt[1], False
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            c = not c
    return c


def _tidy(loop):
    """Drop repeated and collinear points of a closed loop."""
    out = []
    n = len(loop)
    for i, p in enumerate(loop):
        a, b = loop[i - 1], loop[(i + 1) % n]
        cr = (p[0] - a[0]) * (b[1] - p[1]) - (p[1] - a[1]) * (b[0] - p[0])
        dot = (p[0] - a[0]) * (b[0] - p[0]) + (p[1] - a[1]) * (b[1] - p[1])
        if abs(cr) > 1e-7 or dot < 0:
            out.append(p)
    return out


# ------------------------------------------------------------------ polylines
def chain(segs, tol=4):
    """Loose segments [(s0, z0, s1, z1)] -> polylines, joined where exactly two ends meet (rounded to `tol`
    decimals), simplified. A closed one repeats its first point."""
    key = lambda p: (round(p[0], tol), round(p[1], tol))
    S = [((a, b), (c, d)) for a, b, c, d in segs]
    ends, used, out = {}, [False] * len(S), []
    for i, (p, q) in enumerate(S):
        ends.setdefault(key(p), []).append(i)
        ends.setdefault(key(q), []).append(i)

    def extend(pts):                                               # grow the tail while one segment continues it
        while True:
            k = key(pts[-1])
            nxt = [j for j in ends[k] if not used[j]]
            if len(ends[k]) != 2 or not nxt:
                return
            used[nxt[0]] = True
            p, q = S[nxt[0]]
            pts.append(q if key(p) == k else p)

    for i, (p, q) in enumerate(S):
        if used[i]:
            continue
        used[i] = True
        pts = [p, q]
        extend(pts)
        if key(pts[-1]) != key(pts[0]):                            # open: grow the other end too
            pts.reverse()
            extend(pts)
        out.append(simplify(pts, SIMPLIFY))
    return [p for p in out if len(p) >= 2]


def simplify(pts, eps):
    """Ramer-Douglas-Peucker, iterative; keeps both ends (a closed polyline stays closed)."""
    if len(pts) < 3:
        return pts
    keep, stack = [False] * len(pts), [(0, len(pts) - 1)]
    keep[0] = keep[-1] = True
    while stack:
        i, j = stack.pop()
        (x0, y0), (x1, y1) = pts[i], pts[j]
        L = math.hypot(x1 - x0, y1 - y0)
        best, bd = None, eps
        for m in range(i + 1, j):
            x, y = pts[m]
            d = abs((x - x0) * (y1 - y0) - (y - y0) * (x1 - x0)) / L if L > 1e-9 else math.hypot(x - x0, y - y0)
            if d > bd:
                best, bd = m, d
        if best is not None:
            keep[best] = True
            stack += [(i, best), (best, j)]
    return [p for p, k in zip(pts, keep) if k]


# ------------------------------------------------------------------ one section
def mass_table(h):
    """[(polygon, z0, z1, level)] of the mass the shell is carved from: lib.shell._ops step 1."""
    from lib import shell
    rects = {rid: shell.poly_rects(h.room_poly(rid, rect=True)) for rid, r in h.rooms.items() if r.get('kind') != 'exterior'}
    out = []
    for blk in h.spec['exterior']['envelope']['blocks']:
        for lv in blk['levels']:
            rcs = shell.poly_rects(lv['polygon'])
            z0 = min([lv['z'][0]] + [h.rooms[rid]['floorZ'] for rid in rects
                                     if h.rooms[rid].get('level', 'G') == lv['level'] and shell._overlap_area(rcs, rects[rid]) > 1e-6])
            out.append(([tuple(p) for p in lv['polygon']], z0 - shell.SLAB, lv['z'][1], lv['level']))
    return out


def line_breaks(poly, plane, PL):
    """Section coordinates where the plane's line crosses the edges of a plan polygon."""
    axis = 0 if plane['axis'] == 'x' else 1
    at, out = plane['at'], []
    for p, q in zip(poly, poly[1:] + poly[:1]):
        if (p[axis] - at) * (q[axis] - at) < 0:
            t = (at - p[axis]) / (q[axis] - p[axis])
            out.append(PL.to_s(plane, p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return out


def slabs_for(model, h, plane, PL, mass, frame=None):
    """Cut the model on the plane -> (Slabs classified, all cut segments, their normals, their polygons)."""
    from lib import ctx as C
    n3 = np.array([*plane['normal'], 0.0])
    c = plane['at'] * (plane['normal'][0] + plane['normal'][1])    # axis-aligned: n . p = at * sign
    segs, nrm, pol = model.cut(n3, c, plane['origin'], plane['right'])
    shell = model.pcls[pol] == CLASSES.index('shell')
    brk = [s for poly, *_ in mass for s in line_breaks(poly, plane, PL)]
    zlines = sorted({z for _, z0, z1, _ in mass for z in (z0, z1)})

    def build(frame):
        keep = shell & (np.minimum(segs[:, 0], segs[:, 2]) < frame[2]) & (np.maximum(segs[:, 0], segs[:, 2]) > frame[0])
        S = Slabs(segs[keep], nrm[keep], frame, brk)
        S.add_zlines(zlines)
        return S.build(), keep
    if frame is None:                                              # the plot's extent, less the ends the model leaves bare
        frame = (0.0, model.zrange[0], plane['length'], model.zrange[1])
        S, keep = build(frame)
        has = [k for k, cr in enumerate(S.cross) if cr]
        frame = (float(S.b[has[0]]), frame[1], float(S.b[has[-1] + 1]), frame[3])
    S, keep = build(frame)
    # ground line: the highest upward-facing cut of a ground surface (the site zones' objects) per slab; where there
    # is none (under walls, fences, the shed) it runs straight between its neighbours; under the house it is not
    # needed (everything solid outside the mass is earth)
    zone_obj = {f"{z['room']}.{z['id']}" for z in h.spec['exterior']['zones']}
    gpol = np.array([model.names[i] in zone_obj for i in model.pobj[pol[keep]]])
    Hs = segs[keep][gpol]
    sw = Hs[:, 0] > Hs[:, 2]
    Hs = np.where(sw[:, None], Hs[:, [2, 3, 0, 1]], Hs)
    Hs = Hs[np.abs(Hs[:, 2] - Hs[:, 0]) > 1e-5]
    K = len(S.b) - 1
    ground = [None] * K
    for k in range(K):
        a, c2 = S.b[k], S.b[k + 1]
        act = Hs[(Hs[:, 0] <= a + 1e-9) & (Hs[:, 2] >= c2 - 1e-9)]
        if len(act):
            sl = (act[:, 3] - act[:, 1]) / (act[:, 2] - act[:, 0])
            zl, zr = act[:, 1] + sl * (a - act[:, 0]), act[:, 1] + sl * (c2 - act[:, 0])
            i = int(np.argmax(zl + zr))
            ground[k] = (round(float(zl[i]), 4), round(float(zr[i]), 4))
    known = [k for k in range(K) if ground[k]]
    for k in range(K):
        if ground[k] is None and known:
            lo = max((j for j in known if j < k), default=None)
            hi = min((j for j in known if j > k), default=None)
            if lo is None or hi is None:
                v = ground[hi][0] if lo is None else ground[lo][1]
                ground[k] = (v, v)
            else:
                x0, v0, x1, v1 = S.b[lo + 1], ground[lo][1], S.b[hi], ground[hi][0]
                f = lambda x: v0 if x1 - x0 < 1e-9 else v0 + (v1 - v0) * (x - x0) / (x1 - x0)
                ground[k] = (round(float(f(S.b[k])), 4), round(float(f(S.b[k + 1])), 4))
    foot = [poly for poly, _, _, lv in mass if lv in ('B', 'G')]
    rooms = [(rid, [tuple(p) for p in r['polygon']], float(r['floorZ']), r.get('ceilingZ'))
             for rid, r in list(h.rooms.items()) + list(h.building_rooms.items()) if r.get('kind') != 'exterior']

    def solid(k, sm):
        x, y = PL.to_xy(plane, sm)
        ms = sorted((z0, z1) for poly, z0, z1, _ in mass if C.point_in_poly(x, y, poly))
        return ms, (math.inf if any(C.point_in_poly(x, y, p) for p in foot) else ground[k])

    def air(sm, zm):
        x, y = PL.to_xy(plane, sm)
        best = None
        for rid, poly, fz, cz in rooms:
            if fz - 0.05 <= zm <= (fz + 3.5 if cz is None else float(cz)) + 0.05 and C.point_in_poly(x, y, poly):
                if best is None or fz > best[1]:
                    best = (rid, fz, None if cz is None else float(cz))
        return ('room:' + best[0], best[2], best[1]) if best else ('air', None, None)

    S.classify(solid, air)
    S.ground = ground
    return S, segs, nrm, pol


def claim(S, h, rid, plane, PL):
    """Air of any label inside a room's own box (its plan extent along the plane, floor to ceiling) takes that
    room's label. air() gives air that two rooms share to the higher floor - right for a split level, but a stair
    shaft under a flight would be left with its two ends only."""
    r = h.rooms[rid]
    ss = line_breaks([tuple(p) for p in r['polygon']], plane, PL)
    if len(ss) < 2:
        return
    z0 = float(r['floorZ']) - 0.05
    z1 = z0 + 3.55 if r.get('ceilingZ') is None else float(r['ceilingZ']) + 0.05
    for k, iv in enumerate(S.iv):
        if min(ss) < (S.bl[k] + S.bl[k + 1]) / 2 < max(ss):
            S.iv[k] = [q if q[4] in ('fabric', 'earth') or not z0 <= (q[0] + q[1] + q[2] + q[3]) / 4 <= z1
                       else (*q[:4], 'room:' + rid) for q in iv]


def room_records(S):
    """[{id, outer, s: [lo, hi], floor, top}] of the cut rooms: outline of the largest piece of each; floor = the
    height most of its width stands on, top = its highest point."""
    ids = sorted({q[4][5:] for iv in S.iv for q in iv if q[4].startswith('room:')})
    out = []
    for rid in ids:
        polys = S.rings(lambda lab, r='room:' + rid: lab == r)
        if not polys:
            continue
        outer, _ = max(polys, key=lambda p: abs(_area(p[0])))
        w = {}
        for k, iv in enumerate(S.iv):
            for l0, r0, l1, r1, lab in iv:
                if lab == 'room:' + rid and abs(l0 - r0) < 1e-6:
                    w[l0] = w.get(l0, 0.0) + S.bl[k + 1] - S.bl[k]
        ss = [p[0] for p in outer]
        out.append(dict(id=rid, outer=[list(p) for p in outer], s=[min(ss), max(ss)],
                        floor=max(w, key=w.get) if w else min(p[1] for p in outer), top=max(p[1] for p in outer),
                        pieces=len(polys)))
    return out


def beyond(model, plane, S):
    """Visible edges beyond the plane, hidden lines removed -> {class: [polyline]}."""
    d3 = np.array([*plane['normal'], 0.0])
    right = np.asarray(plane['right'], float)
    origin = np.asarray(plane['origin'], float)
    c = plane['at'] * (plane['normal'][0] + plane['normal'][1])
    fa = model.PN[model.EA] @ d3
    has_b = model.EB >= 0
    fb = np.where(has_b, model.PN[np.maximum(model.EB, 0)] @ d3, np.nan)
    front_a, front_b = fa < -FACING, has_b & (fb < -FACING)
    cls = model.pcls[model.EA]
    thr = np.array([math.cos(math.radians(CREASE[k])) if CREASE[k] else -2.0 for k in CLASSES])
    dots = np.einsum('ij,ij->i', model.PN[model.EA], model.PN[np.maximum(model.EB, 0)])
    crease = front_a & front_b & (dots < thr[cls])
    cand = (front_a ^ front_b) | (~has_b & (np.abs(fa) <= FACING)) | crease
    p0, p1 = model.V[model.EV[:, 0]], model.V[model.EV[:, 1]]
    t0, t1 = p0 @ d3 - c, p1 @ d3 - c
    cand &= np.maximum(t0, t1) > 2 * EPS
    cand &= ~(crease & (np.linalg.norm(p1 - p0, axis=1) < MIN_CREASE))
    s0, s1 = (p0[:, :2] - origin) @ right, (p1[:, :2] - origin) @ right
    cand &= (np.hypot(s1 - s0, p1[:, 2] - p0[:, 2]) > 1e-3)
    f0, f1 = 0.0, plane['length']                                   # the plane's whole length, not the trimmed frame
    cand &= (np.maximum(s0, s1) > f0) & (np.minimum(s0, s1) < f1)
    idx = np.nonzero(cand)[0]
    # ray start: off the edge's own faces (their normals, the front-facing ones as they are) and towards the viewer
    off = model.PN[model.EA[idx]] + np.where(has_b[idx][:, None], model.PN[np.maximum(model.EB[idx], 0)], 0.0)
    ln = np.linalg.norm(off, axis=1, keepdims=True)
    off = np.where(ln > 1e-6, off / np.maximum(ln, 1e-12), 0.0) * EPS - d3 * EPS
    back = tuple(-d3)
    ray, is_air = model.bvh.ray_cast, S.is_air
    out = {k: [] for k in CLASSES}
    nray = 0
    for n, i in enumerate(idx):
        a, b = p0[i], p1[i]
        ta, tb = t0[i], t1[i]
        u0, u1 = 0.0, 1.0                                          # the part beyond the plane
        if ta < EPS:
            u0 = (EPS - ta) / (tb - ta)
        if tb < EPS:
            u1 = (EPS - ta) / (tb - ta)
        L2 = math.hypot((s1[i] - s0[i]), (b[2] - a[2])) * (u1 - u0)
        m = max(1, min(4000, int(math.ceil(L2 / STEP))))
        o = off[n]
        run, segs = None, out[CLASSES[cls[i]]]
        for j in range(m):
            u = u0 + (u1 - u0) * (j + 0.5) / m
            px, py, pz = a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u
            s = (px - origin[0]) * right[0] + (py - origin[1]) * right[1]
            vis = f0 <= s <= f1 and is_air(s, pz)
            if vis:
                t = ta + (tb - ta) * u
                nray += 1
                vis = ray((px + o[0], py + o[1], pz + o[2]), back, t - 2 * EPS)[0] is None
            if vis and run is None:
                run = j
            if run is not None and (not vis or j == m - 1):
                e = j + 1 if vis else j
                ua, ub = u0 + (u1 - u0) * run / m, u0 + (u1 - u0) * e / m
                segs.append((round(float(s0[i] + (s1[i] - s0[i]) * ua), 4), round(float(a[2] + (b[2] - a[2]) * ua), 4),
                             round(float(s0[i] + (s1[i] - s0[i]) * ub), 4), round(float(a[2] + (b[2] - a[2]) * ub), 4)))
                run = None
    lines = {k: chain(_dedupe(v)) for k, v in out.items()}
    log(f"  beyond: {len(idx)} candidate edges, {nray} rays -> " + ', '.join(f'{k} {len(v)}' for k, v in lines.items()) + ' polylines')
    return lines


def _dedupe(segs):
    """Drop repeated segments (the same edge from two objects, or drawn in both directions)."""
    seen, out = set(), []
    for a, b, c, d in segs:
        k = (a, b, c, d) if (a, b) <= (c, d) else (c, d, a, b)
        if k not in seen and (a, b) != (c, d):
            seen.add(k)
            out.append((a, b, c, d))
    return out


def section(model, h, sec, PL, mass):
    plane = PL.resolve(h.spec, sec)
    log(f"section {plane['id']}: {plane['axis']} = {plane['at']:+.3f} looking {plane['normal']}, {plane['length']} m")
    S, segs, nrm, pol = slabs_for(model, h, plane, PL, mass)
    polys = lambda want: [dict(outer=[list(p) for p in o], holes=[[list(p) for p in hh] for hh in hs]) for o, hs in S.rings(want)]
    cut = [dict(p, **{'class': c}) for c in ('fabric', 'earth') for p in polys(lambda lab, c=c: lab == c)]
    rooms = room_records(S)
    fixtures, groups = [], {}
    inside = (np.maximum(segs[:, 0], segs[:, 2]) >= S.frame[0]) & (np.minimum(segs[:, 0], segs[:, 2]) <= S.frame[2])
    for i in np.nonzero((model.pcls[pol] != CLASSES.index('shell')) & inside)[0]:
        groups.setdefault((int(model.pcls[pol[i]]), model.roots[model.pobj[pol[i]]]), []).append(tuple(float(v) for v in segs[i]))
    for (k, root), sg in sorted(groups.items()):
        fixtures.append({'class': CLASSES[k], 'root': root, 'lines': [[list(p) for p in pl] for pl in chain(_dedupe(sg))]})
    lines = beyond(model, plane, S)
    hidden = []
    for hd in plane['hidden']:                                     # rooms the plane misses, on a plane of their own
        hp = dict(plane, at=hd['at'], hidden=[])
        hp['origin'] = [hd['at'], plane['origin'][1]] if plane['axis'] == 'x' else [plane['origin'][0], hd['at']]
        HS = slabs_for(model, h, hp, PL, mass, S.frame)[0]
        claim(HS, h, hd['room'], hp, PL)
        for r in room_records(HS):
            if r['id'] == hd['room']:
                hidden.append(dict(r, at=hd['at']))
    empty = sum(1 for cr in S.cross if not cr)
    log(f"  cut: {sum(c['class'] == 'fabric' for c in cut)} fabric + {sum(c['class'] == 'earth' for c in cut)} earth outlines, "
        f"{len(rooms)} rooms {[r['id'] for r in rooms]}, {len(S.b) - 1} slabs ({empty} without any surface), "
        f"{len(fixtures)} pieces cut, hidden {[r['id'] for r in hidden]}")
    return dict(plane, frame=list(S.frame), cut=cut, rooms=rooms, fixtures=fixtures,
                beyond={k: [[list(p) for p in pl] for pl in v] for k, v in lines.items()}, hidden=hidden,
                ground=[[S.bl[k], g[0], S.bl[k + 1], g[1]] for k, g in enumerate(S.ground) if g])


def write(h, out_dir, only=None):
    """Cut every plane of tools/plan/section_planes.py from the scene and write <out_dir>/sections.json. -> the dict."""
    PL = planes_module()
    model = Model()
    mass = mass_table(h)
    secs = []
    for sec in PL.SECTIONS:
        if only and sec['id'] not in only:
            continue
        try:
            secs.append(section(model, h, sec, PL, mass))
        except Exception:                                          # one plane that no longer fits the house: the others still go out
            import traceback
            traceback.print_exc()
            log(f"WARNING: section {sec['id']} failed (traceback above) and is left out")
    if not secs:
        raise RuntimeError('no section could be cut')
    data = dict(schema=1, units='m',
                note='section coordinates: s = metres along the plane from the left end of the drawing '
                     '(s = (p - origin) . right in plan), z = world Z; cut = closed outlines with holes; beyond = visible '
                     'lines of what stands beyond the plane; fixtures = joinery / trim / fittings cut by it; hidden = '
                     'rooms cut on a plane of their own (dashed); ground = the ground line per slab [s0, z0, s1, z1]',
                classes=list(CLASSES), sections=secs)
    path = Path(out_dir) / 'sections.json'
    path.write_text(json.dumps(data, separators=(',', ':')), encoding='utf-8', newline='\n')
    log(f'wrote {path} ({path.stat().st_size / 1e6:.2f} MB, {len(secs)} sections)')
    return data


def main():
    from lib import ctx as C
    ap = argparse.ArgumentParser(prog='export_sections.py')
    ap.add_argument('--out', default='docs/assets', help='directory for sections.json (default docs/assets)')
    ap.add_argument('--house', default='spec/house.json')
    ap.add_argument('--only', default='', help='section ids, e.g. AA,BB (default: all)')
    a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    out = (ROOT / a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    write(C.House.load((ROOT / a.house).resolve()), out, [s for s in a.only.split(',') if s])
    print('SECTIONS OK')


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except BaseException:
        import traceback
        traceback.print_exc()
        sys.exit(1)

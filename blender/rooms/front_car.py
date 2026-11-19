"""Generic parked cars for the forecourt (spec/rooms/front.md 6.1).

One lofted body per car (stations along the length x one half ring per station, materials by grid cell), lamps,
grilles and intakes as patches projected onto that body (ray cast along a view direction), four wheels sharing one
mesh and a pair of door mirrors. No number plates, no badges, no lettering: the plate areas are plain body colour.
Car frame: origin = centre of the footprint on the ground, nose toward -Y, +X = the car's left seen from the front
(world east when parked nose-out), Z up; t = metres from the nose.

    body, wheels, mirrors = car(GREY, 'front.car_grey')      # unlinked objects in the car frame; wheels = [(obj, Matrix)]
"""
import math

import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

from lib import materials as M, mouldings as mo

NT, NR, NG, NS, NU = 8, 4, 5, 12, 5         # ring segments: top, roof rail / shoulder, side glass, body side, underside
J_RAIL, J_GLASS, J_SIDE, J_UNDER, NJ = NT, NT + NR, NT + NR + NG, NT + NR + NG + NS, NT + NR + NG + NS + NU
ARCH_GAP = 0.045                            # wheel arch radius - tyre radius
WELL = 0.27                                 # depth of the wheel wells from the body side


def _chaikin(p, n):
    for _ in range(n):
        q, r = 0.75 * p[:-1] + 0.25 * p[1:], 0.25 * p[:-1] + 0.75 * p[1:]
        p = np.vstack([p[:1], np.column_stack([q, r]).reshape(-1, 2), p[-1:]])
    return p


def prof(pts, r=0.05):
    """Key points (t, value[, corner radius]) -> smooth function of t: every inner corner is rounded within its
    radius (straight runs stay straight), by corner cutting."""
    P = [np.array(p[:2], float) for p in pts]
    out = [P[0]]
    for a, b, c, p in zip(P, P[1:], P[2:], pts[1:]):
        rr = p[2] if len(p) > 2 else r
        la, lc = np.linalg.norm(b - a), np.linalg.norm(c - b)
        out += [b + (a - b) * min(rr, 0.45 * la) / la, b, b + (c - b) * min(rr, 0.45 * lc) / lc]
    q = _chaikin(np.array(out + [P[-1]]), 3)
    t = np.maximum.accumulate(q[:, 0])
    return lambda x: np.interp(x, t, q[:, 1])


def _stations(S):
    L = S['L']
    ts = list(L * (0.5 - 0.5 * np.cos(np.pi * np.linspace(0, 1, 76))))
    for ta in S['axles']:
        ra = S['tyre_r'] + ARCH_GAP
        ts += [ta - ra * math.cos(math.pi * k / 24) for k in range(25)]
    ends = (0.003, 0.006, 0.009, 0.012, 0.018, 0.025, 0.035, 0.05, 0.065, 0.08, 0.10, 0.12, 0.15)
    ts += list(ends) + [L - t for t in ends] + list(S['stations'])
    out = [0.0]
    for t in sorted(ts)[1:]:
        if t - out[-1] > min(0.010, 0.0015 + 0.2 * min(t, L - t)) and t < L - 1e-4:
            out.append(t)
    return np.array(out + [L])


def _grid(S, ts):
    """-> P[i, j] = (x, y, z) of the +X half ring at every station (j: 0 = top centre ... NJ = bottom centre)."""
    L = S['L']
    top, belt, bot, plan = (prof(S[k]) for k in ('top', 'belt', 'bottom', 'plan'))
    zt = top(ts)
    zb = np.minimum(belt(ts), zt)
    zl0 = np.minimum(bot(ts), zb)
    e = np.clip(np.minimum(ts, L - ts) / 0.15, 0, 1)
    crown = np.minimum(S.get('crown', 0.045), 0.4 * (zt - zb))
    zg = np.maximum(zb, zt - crown - 0.055)                         # top of the side glass (= belt where there is none)
    zl = zl0.copy()
    for ta in S['axles']:                                           # wheel arches
        ra = S['tyre_r'] + ARCH_GAP
        d2 = ra * ra - (ts - ta) ** 2
        zl = np.where(d2 > 0, np.maximum(zl, S['tyre_r'] + np.sqrt(np.maximum(d2, 0))), zl)
    zl = np.minimum(zl, zb)
    zf = zl0 - 0.025 * e
    w = plan(ts)
    b = np.minimum(0.045, 0.15 * (zb - zl))
    wb, wbot = w - b, w - 0.6 * b
    wr = wb - S.get('tumble', 0.42) * (zg - zb)
    r1x = np.minimum(np.minimum(0.09, 0.5 * wr), 2.0 * (zt - crown - zg) + 0.01)
    inset = np.minimum(WELL, 0.5 * wbot)
    X, Z = np.zeros((len(ts), NJ + 1)), np.zeros((len(ts), NJ + 1))
    for j in range(NT + 1):
        s = j / NT
        X[:, j], Z[:, j] = (wr - r1x) * s, zt - crown * s * s
    for k in range(1, NR + 1):
        th = math.pi / 2 * k / NR
        X[:, J_RAIL + k], Z[:, J_RAIL + k] = wr - r1x + r1x * math.sin(th), zg + (zt - crown - zg) * math.cos(th)
    for k in range(1, NG + 1):
        s = k / NG
        X[:, J_GLASS + k] = wr + (wb - wr) * s + 0.012 * math.sin(math.pi * s) * np.minimum(1, (zg - zb) / 0.2)
        Z[:, J_GLASS + k] = zg + (zb - zg) * s
    for k in range(1, NS + 1):
        s = k / NS
        X[:, J_SIDE + k] = (1 - s) ** 2 * wb + 2 * s * (1 - s) * (w + 0.5 * b) + s * s * wbot
        Z[:, J_SIDE + k] = zb + (zl - zb) * s
    xi = wbot - inset                                               # sill / well roof, well wall, floor
    for k, (x, z) in enumerate(((wbot - 0.5 * inset, zl), (xi, zl), (xi, zf), (0.5 * xi, zf), (0 * xi, zf))):
        X[:, J_UNDER + 1 + k], Z[:, J_UNDER + 1 + k] = x, z
    Y = np.repeat((ts - L / 2)[:, None], NJ + 1, 1)
    return np.stack([X, Y, Z], 2), dict(top=top, belt=belt, plan=plan, zb=zb, w=w)


def _kind(j):
    for name, j0 in (('U', J_UNDER), ('S', J_SIDE), ('G', J_GLASS), ('R', J_RAIL)):
        if j >= j0:
            return name, j - j0
    return 'T', j


def _cell_mat(S, tm, j):
    kind, k = _kind(j)
    for t0, t1, kd, k0, k1, m in S['patches']:
        if kd == kind and t0 < tm < t1 and k0 <= k < k1:
            return m
    if kind == 'U':
        return 'paint' if tm < 0.07 or tm > S['L'] - 0.07 else 'under'
    if kind == 'T':
        if S['ws'][0] < tm < S['ws'][1] or S['rear_glass'][0] < tm < S['rear_glass'][1]:
            return 'glass'
        if S['ws'][0] - 0.045 < tm <= S['ws'][0]:
            return 'trim'                                           # cowl panel
    if kind == 'G' and S['side_glass'][0] < tm < S['side_glass'][1]:
        return 'trim' if any(a < tm < b for a, b in S['pillars']) else 'glass'
    return 'paint'


def _mats(S):
    return dict(paint=M.solid(*S['paint']), glass=M.solid('car_glass', '#14161A', 0.04),
                trim=M.solid('car_trim_black', '#101012', 0.32), under=M.solid('car_underbody', '#0E0E0F', 0.9),
                lamp=M.solid('car_lamp_clear', '#BFC3C8', 0.14, 0.65), lens=M.solid('car_lamp_dark', '#2A2D31', 0.05, 0.7),
                red=M.solid('car_lamp_red', '#B01E1A', 0.08), red_dark=M.solid('car_lamp_red_dark', '#7E1612', 0.05),
                reflector=M.solid('car_lamp_reflector', '#C4C7CB', 0.25, 0.9), amber=M.solid('car_lamp_amber', '#D9822B', 0.1),
                tyre=M.solid('car_tyre', '#1A1A1B', 0.82), alloy=M.solid('car_alloy', '#B6B9BD', 0.28, 0.9),
                alloy_dark=M.solid(*S['alloy_dark']), disc=M.solid('car_brake_disc', '#55565A', 0.45, 0.8),
                chrome=M.mat('chrome'), cap=M.solid(*S['mirror_cap']), groove=M.solid('car_shutline', '#0A0A0B', 0.6),
                mesh=M.solid('car_grille', '#1B1C1F', 0.5))


def _normals(P):
    """Outward grid normals; where the ring is pinched to a point (no side glass) the neighbour's is used."""
    N = np.cross(np.gradient(P, axis=1), np.gradient(P, axis=0))
    ln = np.linalg.norm(N, axis=2, keepdims=True)
    N = N / np.maximum(ln, 1e-12)
    bad = ln[..., 0] < 1e-7
    for j in range(1, NJ + 1):                                      # fill forward, then backward
        fix = bad[:, j] & ~bad[:, j - 1]
        N[fix, j], bad[fix, j] = N[fix, j - 1], False
    for j in range(NJ - 1, -1, -1):
        fix = bad[:, j] & ~bad[:, j + 1]
        N[fix, j], bad[fix, j] = N[fix, j + 1], False
    return N


VIEWS = {'rear': ((0, -1, 0), (1, 0, 0)), 'front': ((0, 1, 0), (1, 0, 0)), 'side': ((-1, 0, 0), (0, 1, 0)),
         'top': ((0, 0, -1), (1, 0, 0))}


def _pdecal(mb, bvh, L, lamp, mats):
    """A patch lying on the body, on both sides of the car. lamp = dict(m, pts=[(u, v), ...], view, turn=0, at=None,
    off=0.003, rim=True, sub=4, rings=3, mirror=True): the outline is drawn in the plane through `at` square to the
    view direction of `view` (VIEWS: rear / front look along -Y / +Y with u = x, v = z, plane at the tail / nose;
    side looks at the +X flank with u = y, v = z; top looks down with u = x, v = y), and every vertex is projected
    onto the body along the view direction turned by `turn` degrees about Z (wrap-round lamps: the outline is seen
    obliquely). Lamps follow the curved surface whatever the grid does there; `rim` closes the edge down into the
    body with a dark shut line."""
    D0, U = (Vector(v) for v in VIEWS[lamp['view']])
    D = Matrix.Rotation(math.radians(lamp.get('turn', 0)), 3, 'Z') @ D0
    V = Vector((0, 1, 0)) if lamp['view'] == 'top' else Vector((0, 0, 1))
    A = Vector(lamp.get('at', dict(front=(0, -L / 2, 0), rear=(0, L / 2, 0), side=(0.9, 0, 0), top=(0, 0, 2))[lamp['view']]))
    off, sub, rings = lamp.get('off', 0.003), lamp.get('sub', 6), lamp.get('rings', 4)
    poly = lamp['pts']
    outline = [(u0 + (u1 - u0) * k / sub, v0 + (v1 - v0) * k / sub)
               for (u0, v0), (u1, v1) in zip(poly, poly[1:] + poly[:1]) for k in range(sub)]
    cu, cv = sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly)
    mi, gi, n = mb.mi(mats[lamp['m']]), mb.mi(mats['groove']), len(outline)
    for s in ((1, -1) if lamp.get('mirror', True) else (1,)):
        d = Vector((D.x * s, D.y, D.z))

        def hit(u, v, o=off):
            p = A + U * u + V * v
            loc, nrm, _, _ = bvh.ray_cast(Vector((p.x * s, p.y, p.z)) - d * 6, d, 12.0)
            if loc is None:
                raise ValueError('car lamp %s: (%.3f, %.3f) misses the body' % (lamp['m'], u, v))
            if nrm.dot(d) > 0:
                nrm = -nrm
            return loc + nrm * o, nrm

        c, nc = hit(cu, cv)
        cv0 = mb._vs([c])[0]
        loops = [mb._vs([hit(cu + (u - cu) * r / rings, cv + (v - cv) * r / rings)[0] for u, v in outline])
                 for r in range(1, rings + 1)]
        a, b = loops[0][0].co - cv0.co, loops[0][1].co - cv0.co
        flip = a.cross(b).dot(nc) < 0
        faces = [[cv0, loops[0][k], loops[0][(k + 1) % n]] for k in range(n)]
        faces += [[la[k], lb[k], lb[(k + 1) % n], la[(k + 1) % n]] for la, lb in zip(loops, loops[1:]) for k in range(n)]
        for f in faces:
            mb._f(f[::-1] if flip else f, mi)
        if lamp.get('rim', True):
            base = mb._vs([hit(u, v, -0.004)[0] for u, v in outline])
            for k in range(n):
                f = [loops[-1][k], base[k], base[(k + 1) % n], loops[-1][(k + 1) % n]]
                mb._f(f[::-1] if flip else f, gi)


def _strip(mb, pts, nrm, mat, hw=0.0035, off=0.0015):
    """Thin dark band lying on the body along a polyline (door shut lines)."""
    P, Nn = [Vector(p) for p in pts], [Vector(n).normalized() for n in nrm]
    rows = []
    for k, (p, n) in enumerate(zip(P, Nn)):
        tan = (P[min(k + 1, len(P) - 1)] - P[max(k - 1, 0)])
        if tan.length < 1e-6:
            continue
        s = n.cross(tan.normalized()).normalized()
        rows.append(mb._vs([p + n * off + s * hw, p + n * off - s * hw]))
    mi = mb.mi(mat)
    for (a0, b0), (a1, b1) in zip(rows, rows[1:]):
        mb._f([a0, b0, b1, a1], mi)


def _on_body(bvh, x, y, d=(0, 0, -1), lift=0.0):
    """First body point below / along d from (x, y, 3) -> (point + normal * lift, normal) or (None, None)."""
    d = Vector(d).normalized()
    o = Vector((x, y, 0.8)) - d * 3
    loc, nrm, _, _ = bvh.ray_cast(o, d, 8.0)
    if loc is None:
        return None, None
    nrm = -nrm if nrm.dot(d) > 0 else nrm
    return loc + nrm * lift, nrm


def _body(S, name, mats):
    ts = _stations(S)
    P, F = _grid(S, ts)
    ni = len(ts)
    mb = mo.MB()
    mb._soft = 1
    cache = {}

    def vert(i, j, sx):
        x, y, z = P[i, j]
        key = (round(sx * x * 5e3), round(y * 5e3), round(z * 5e3))          # weld within 0.2 mm
        if key not in cache:
            cache[key] = mb._vs([(sx * x, y, z)])[0]
        return cache[key]

    for i in range(ni - 1):
        tm = 0.5 * (ts[i] + ts[i + 1])
        for j in range(NJ):
            mi = mb.mi(mats[_cell_mat(S, tm, j)])
            for sx in (1, -1):
                q = [vert(i, j, sx), vert(i, j + 1, sx), vert(i + 1, j + 1, sx), vert(i + 1, j, sx)]
                vs = [v for k, v in enumerate(q) if v is not q[k - 1]]
                if len(set(vs)) >= 3:
                    mb._f(vs if sx > 0 else vs[::-1], mi)

    mb.bm.verts.index_update()                                      # the bare shell: what lamps and trim lie on
    bvh = BVHTree.FromPolygons([v.co.copy() for v in mb.bm.verts], [[v.index for v in f.verts] for f in mb.bm.faces])
    N = _normals(P)
    near = lambda t: int(np.argmin(np.abs(ts - t)))
    mir = np.array([-1, 1, 1])
    mb._soft = 0
    for t, j0, j1 in S['shut_i']:                                    # along a station: door edges
        i = near(t)
        for s in (1, mir):
            _strip(mb, P[i, j0:j1 + 1] * s, N[i, j0:j1 + 1] * s, mats['groove'])
    for j, t0, t1 in S['shut_j']:                                    # along a ring line: bonnet and tailgate sides
        i0, i1 = near(t0), near(t1)
        for s in (1, mir):
            _strip(mb, P[i0:i1 + 1, j] * s, N[i0:i1 + 1, j] * s, mats['groove'])
    i0, i1 = near(S['side_glass'][0] + 0.10), near(S['side_glass'][1])
    for s in (1, mir):                                               # waistline seal under the side glass
        _strip(mb, P[i0:i1 + 1, J_SIDE] * s, N[i0:i1 + 1, J_SIDE] * s, mats['trim'], hw=0.008, off=0.002)
    mb._soft = 1
    for lamp in S['lamps']:
        _pdecal(mb, bvh, S['L'], lamp, mats)
    mb._soft = 0

    # door handles (body colour) on the side, a little under the waistline
    for t in S['handles']:
        i = near(t)
        x, y, z = P[i, J_SIDE + 2]
        for sx in (1, -1):
            mb.at(Matrix.Translation((sx * (x + 0.004), y, z - 0.01)))
            mb.box((-0.016, -0.085, -0.016), (0.016, 0.085, 0.016), mats['paint'], bev=0.008)
            mb.box((-0.004, -0.10, -0.03), (0.002, 0.10, 0.012), mats['groove'])
    mb.at()
    # front wipers parked along the foot of the windscreen
    yw = S['ws'][0] - S['L'] / 2 + 0.07
    for x0, x1 in ((-0.62, 0.02), (0.04, 0.58)):
        pts = []
        for k in range(7):
            x = x0 + (x1 - x0) * k / 6
            p, _ = _on_body(bvh, x, yw + 0.06 * (k / 6) * (1 if x1 > 0.3 else -1) + 0.03, lift=0.012)
            if p is not None:
                pts.append(p)
        if len(pts) > 2:
            mb.tube(pts, 0.006, mats['trim'], n=5)
    for fn in S.get('extras', ()):
        fn(mb, S, mats, dict(F, ts=ts, P=P, N=N, near=near, bvh=bvh))
    ob = mb.finish(name, sharp_deg=40)
    return ob, dict(F, ts=ts, P=P, near=near)


def _wheel(S, name, mats):
    """One wheel, axis along X, outer face toward +X, origin at the hub centre."""
    R, w, rr = S['tyre_r'], S['tyre_w'], S['rim_r']
    mb = mo.MB().at(Matrix.Rotation(math.pi / 2, 4, 'Y'))
    h = w / 2
    mb._soft = 1
    mb.lathe([(rr, -h * 0.92), (rr + 0.035, -h), (R - 0.03, -h * 0.98), (R - 0.012, -h * 0.86), (R - 0.003, -h * 0.62),
              (R, -h * 0.3), (R, h * 0.3), (R - 0.003, h * 0.62), (R - 0.012, h * 0.86), (R - 0.03, h * 0.98),
              (rr + 0.035, h), (rr, h * 0.92)], mats['tyre'], segs=40)
    mb._soft = 0
    z0 = h * 0.25                                                     # dished back of the rim
    mb.lathe([(rr + 0.002, h * 0.93), (rr - 0.006, h * 0.97), (rr - 0.016, h * 0.86), (rr - 0.024, h * 0.6),
              (rr - 0.028, z0)], mats['alloy'], segs=40)
    mb.lathe([(rr - 0.028, z0), (0, z0)], mats['alloy_dark'], segs=36)
    mb.lathe([(0.0, -h * 0.1), (rr - 0.045, -h * 0.1), (rr - 0.045, z0 - 0.004), (0.0, z0 - 0.004)], mats['disc'], segs=20)
    mb.lathe([(0, -h * 0.5), (rr - 0.03, -h * 0.5), (rr, -h * 0.92)], mats['under'], segs=16)       # inner side, never seen close
    mb.lathe([(0.052, z0), (0.052, h * 0.74), (0.04, h * 0.86), (0.024, h * 0.9), (0, h * 0.9)], mats['alloy'], segs=24)
    mb.lathe([(0.022, h * 0.9), (0.022, h * 0.92), (0, h * 0.92)], mats['alloy_dark'], segs=12)   # centre cap, plain
    base = mb.M.copy()
    for k in range(5):
        for da in (-0.12, 0.12):
            mb.at(base @ Matrix.Rotation(2 * math.pi * k / 5 + da + 0.3, 4, 'Z'))
            mb.box((0.042, -0.012, z0 + 0.004), (rr - 0.018, 0.012, h * 0.80), mats['alloy'], bev=0.005)
    for k in range(5):                                                # wheel nuts
        mb.at(base @ Matrix.Rotation(2 * math.pi * (k + 0.5) / 5 + 0.3, 4, 'Z') @ Matrix.Translation((0.036, 0, h * 0.86)))
        mb.lathe([(0.008, 0), (0.008, 0.01), (0, 0.012)], mats['chrome'], segs=6)
    return mb.at().finish(name, sharp_deg=40)


def _mirrors(S, name, mats, info):
    """Door mirrors, both sides, in the car frame."""
    mb = mo.MB()
    t = S['ws'][0] + 0.20
    i = info['near'](t)
    x, y, z = info['P'][i, J_SIDE]
    for sx in (1, -1):
        mb.at(Matrix.Translation((sx * x, y, z + 0.035)) @ Matrix.Scale(sx, 4, (1, 0, 0)))
        mb.box((-0.02, -0.03, -0.035), (0.07, 0.03, 0.0), mats['trim'], bev=0.006)                 # foot
        mb._soft = 1
        ring = lambda yy, hw, hh, zc: [(0.045 + hw + hw * math.cos(a), yy, zc + hh * math.sin(a))
                                       for a in (2 * math.pi * k / 16 for k in range(16))]
        rings = [ring(0.045, 0.085, 0.052, 0.045), ring(0.03, 0.09, 0.056, 0.045), ring(0.0, 0.092, 0.058, 0.045),
                 ring(-0.03, 0.082, 0.052, 0.045), ring(-0.05, 0.06, 0.038, 0.045), ring(-0.062, 0.03, 0.02, 0.045)]
        V = [mb._vs(r) for r in rings]
        cap, gl = mb.mi(mats['cap']), mb.mi(mats['lamp'])
        for a, b in zip(V, V[1:]):
            for k in range(16):
                mb._f([a[k], a[(k + 1) % 16], b[(k + 1) % 16], b[k]], cap)
        inner = mb._vs([(0.045 + 0.085 + 0.075 * math.cos(a), 0.04, 0.045 + 0.042 * math.sin(a))
                        for a in (2 * math.pi * k / 16 for k in range(16))])
        for k in range(16):                                           # housing lip round the glass
            mb._f([V[0][(k + 1) % 16], V[0][k], inner[k], inner[(k + 1) % 16]], cap)
        mb._f(inner[::-1], gl)                                        # the glass faces the tail
        mb._f(V[-1], cap)
        mb._soft = 0
    return mb.at().finish(name, sharp_deg=50)


def car(S, name):
    """-> body, [(wheel object, car-frame matrix) x 4], mirrors."""
    mats = _mats(S)
    body, info = _body(S, name, mats)
    wheel = _wheel(S, name + '.wheel', mats)
    wheels = []
    for k, (ta, sx) in enumerate((ta, sx) for ta in S['axles'] for sx in (1, -1)):
        ob = wheel if k == 0 else bpy.data.objects.new('%s.wheel.%d' % (name, k), wheel.data)
        ob.name = '%s.wheel.%d' % (name, k)
        wheels.append((ob, Matrix.Translation((sx * S['track'] / 2, ta - S['L'] / 2, S['tyre_r']))
                       @ Matrix.Rotation(0 if sx > 0 else math.pi, 4, 'Z')))
    return body, wheels, _mirrors(S, name + '.mirrors', mats, info)


# ------------------------------------------------------------------------------------------------ extras
def _rear(F, S, z):
    """-> Matrix of a frame lying on the tail at height z on the centre line: origin on the surface, +Y out of it."""
    ts = np.linspace(S['L'] * 0.8, S['L'], 800)
    zz = F['top'](ts)
    t = lambda h: float(ts[np.argmin(np.abs(zz - h))])
    lean = math.atan2(t(z - 0.02) - t(z + 0.02), 0.04)             # the panel's top leans toward the nose
    return Matrix.Translation((0, t(z) - S['L'] / 2, z)) @ Matrix.Rotation(lean, 4, 'X')


def _aerial(mb, S, mats, F):
    t = S['rear_glass'][0] - 0.16
    y, z = t - S['L'] / 2, float(F['top'](t))
    mb.at(Matrix.Translation((0, y, z - 0.004)))
    mb.box((-0.02, -0.03, 0), (0.02, 0.03, 0.014), mats['trim'], bev=0.006)
    mb.tube([(0, 0, 0.01), (0, 0.10, 0.15)], 0.003, mats['trim'], n=5)
    mb.at()


def _spoiler(mb, S, mats, F):
    t = S['rear_glass'][0] - 0.01
    y, z = t - S['L'] / 2, float(F['top'](t))
    hw = float(F['plan'](t)) * 0.80
    mb.at(Matrix.Translation((0, y, z)) @ Matrix.Rotation(math.radians(-9), 4, 'X'))
    mb.box((-hw, -0.09, -0.012), (hw, 0.06, 0.016), mats['paint'], bev=0.008)
    for sx in (1, -1):                                                                            # end plates
        mb.box((sx * hw - 0.02, -0.06, -0.05), (sx * hw + 0.002 * sx, 0.06, 0.012), mats['paint'], bev=0.006)
    mb.box((-0.16, 0.045, -0.014), (0.16, 0.062, 0.004), mats['red_dark'])                         # high-level brake light
    mb.at()


def _wiper(mb, S, mats, F, z):
    mb.at(_rear(F, S, z))
    mb.box((-0.02, -0.004, -0.012), (0.02, 0.02, 0.012), mats['trim'], bev=0.004)
    mb.tube([(-0.0, 0.016, 0.0), (0.30, 0.016, 0.05)], 0.006, mats['trim'], n=5)
    mb.at()


def _tail_trim(mb, S, mats, F):
    """Plain chrome strip across the tailgate (no badge), rear wiper."""
    mb.at(_rear(F, S, 0.93))
    mb._soft = 1
    mb.box((-0.36, -0.004, -0.013), (0.36, 0.006, 0.013), mats['chrome'], bev=0.005)
    mb._soft = 0
    _wiper(mb, S, mats, F, 1.12)


def _white_tail(mb, S, mats, F):
    _wiper(mb, S, mats, F, 1.06)


# ------------------------------------------------------------------------------------------------ the two cars
def _front(head, grille, intake, fog=None, turn=38):
    """Headlamps (clear housing + dark projector), upper grille, lower intake, optional fog-lamp recesses."""
    out = [dict(m='lamp', view='front', turn=turn, pts=head[0], off=0.004),
           dict(m='lens', view='front', turn=turn, pts=head[1], off=0.0055, rim=False),
           dict(m='mesh', view='front', pts=grille, off=0.002, mirror=False, sub=4, rings=2),
           dict(m='mesh', view='front', pts=intake, off=0.002, mirror=False, sub=4, rings=2)]
    if fog:
        out.append(dict(m='trim', view='front', pts=fog, off=0.0025))
    return out


# Dark metallic grey 5-door supermini, 3.89 x 1.70 x 1.51 (front.md 6.1)
GREY = dict(
    L=3.89, track=1.47, axles=(0.74, 3.25), tyre_r=0.30, tyre_w=0.185, rim_r=0.195,
    paint=('car_paint_grey', '#5A5C61', 0.3, 0.5), alloy_dark=('car_alloy_dark', '#3C3D40', 0.35, 0.8),
    mirror_cap=('car_paint_grey', '#5A5C61', 0.3, 0.5),
    top=[(0, .50), (.006, .60, .004), (.035, .69, .012), (.12, .755, .03), (.55, .875, .15), (.98, .955, .05),
         (1.74, 1.455, .12), (2.25, 1.51, .3), (3.05, 1.475, .2), (3.39, 1.41, .03), (3.63, 1.06, .04), (3.78, .68, .03),
         (3.80, .645, .015), (3.87, .60, .03), (3.888, .52, .01), (3.89, .50)],
    belt=[(0, .50), (.006, .575, .004), (.04, .64, .012), (.15, .70, .04), (.55, .79, .2), (1.0, .895, .2), (2.0, .955, .4),
          (3.0, 1.04, .3), (3.45, 1.05, .1), (3.70, .93, .05), (3.84, .70, .03), (3.884, .60, .006), (3.89, .50)],
    bottom=[(0, .50), (.006, .37, .004), (.03, .26, .012), (.10, .205, .03), (.5, .20), (3.3, .21), (3.80, .24, .03),
            (3.865, .30, .015), (3.884, .40, .006), (3.89, .50)],
    plan=[(0, .50), (.03, .62, .02), (.14, .74, .06), (.5, .83, .2), (.95, .85, .2), (3.0, .85, .3), (3.55, .825, .15),
          (3.80, .74, .06), (3.87, .64, .02), (3.89, .52)],
    ws=(1.03, 1.69), side_glass=(1.03, 3.13), rear_glass=(3.41, 3.62), pillars=[(2.06, 2.14)],
    stations=(1.03, 1.69, 3.13, 3.41, 3.62, 2.06, 2.14, 1.12, 2.10, 3.02, 0.30, 0.47, 3.50, 3.64, 3.80, 3.845),
    patches=[],
    lamps=_front(([(0.36, 0.635), (0.60, 0.625), (0.84, 0.66), (1.10, 0.75), (1.14, 0.79), (0.90, 0.78), (0.62, 0.72),
                   (0.40, 0.675)],
                  [(0.56, 0.645), (0.70, 0.645), (0.74, 0.70), (0.60, 0.695)]),
                 [(-0.30, 0.60), (0.30, 0.60), (0.33, 0.645), (-0.33, 0.645)],
                 [(-0.42, 0.27), (0.42, 0.27), (0.46, 0.33), (0.38, 0.46), (-0.38, 0.46), (-0.46, 0.33)],
                 fog=[(0.56, 0.33), (0.66, 0.33), (0.68, 0.39), (0.58, 0.40)])
    # tail-lamps (v2_t944 / t946): smoked housing, clear upper-inner part over chrome reflectors, dark red band
    # along the lower and outer edge
    + [dict(m='lens', view='rear', turn=-42, off=0.004,
            pts=[(0.60, 1.05), (0.85, 1.06), (1.10, 1.03), (1.17, 0.98), (1.05, 0.90), (0.92, 0.84), (0.75, 0.85), (0.64, 0.95)]),
       dict(m='red_dark', view='rear', turn=-42, off=0.0065, rim=False,
            pts=[(0.65, 0.935), (0.75, 0.86), (0.92, 0.85), (1.05, 0.91), (1.16, 0.98), (1.10, 1.02), (1.02, 0.95),
                 (0.91, 0.895), (0.77, 0.90), (0.68, 0.96)]),
       dict(m='reflector', view='rear', turn=-42, off=0.0065, rim=False,
            pts=[(0.63, 1.035), (0.85, 1.045), (1.00, 1.025), (0.98, 0.975), (0.88, 0.94), (0.76, 0.94), (0.67, 0.98)]),
       dict(m='red_dark', view='rear', off=0.003, pts=[(0.50, 0.40), (0.66, 0.405), (0.66, 0.43), (0.50, 0.425)])],
    shut_i=[(1.12, J_SIDE, J_UNDER), (2.10, J_SIDE, J_UNDER), (3.02, J_SIDE, J_UNDER - 4), (0.065, 0, J_RAIL + 1),
            (3.845, 0, J_RAIL + 2)],
    shut_j=[(J_RAIL, 0.47, 0.97), (NT - 1, 3.74, 3.845)],                      # tailgate edge: stops under the lamps
    handles=(1.92, 2.84), extras=(_aerial, _spoiler, _tail_trim))

# Solid white city car, 3.46 x 1.62 x 1.46: upright tail, all-glass black tailgate, black C-pillar, orange-red mirror caps
WHITE = dict(
    L=3.46, track=1.42, axles=(0.66, 3.00), tyre_r=0.285, tyre_w=0.175, rim_r=0.195,
    paint=('car_paint_white', '#F0F1F1', 0.14, 0.0), alloy_dark=('car_alloy_black', '#17181A', 0.35, 0.6),
    mirror_cap=('car_mirror_red', '#D2452F', 0.2, 0.0),
    top=[(0, .50), (.006, .61, .004), (.035, .70, .012), (.12, .77, .03), (.50, .885, .15), (.87, .96, .05),
         (1.52, 1.405, .12), (2.0, 1.46, .3), (2.85, 1.44, .2), (3.11, 1.395, .03), (3.33, 1.02, .04), (3.42, .74, .04),
         (3.455, .62, .006), (3.46, .50)],
    belt=[(0, .50), (.006, .58, .004), (.04, .65, .012), (.15, .71, .04), (.5, .80, .2), (.9, .895, .2), (1.8, .95, .4),
          (2.7, 1.04, .3), (3.15, 1.08, .08), (3.34, .98, .04), (3.43, .72, .02), (3.455, .60, .006), (3.46, .50)],
    bottom=[(0, .50), (.006, .37, .004), (.03, .27, .012), (.10, .215, .03), (.5, .21), (2.95, .22), (3.38, .25, .03),
            (3.44, .31, .012), (3.455, .40, .005), (3.46, .50)],
    plan=[(0, .48), (.03, .60, .02), (.14, .71, .06), (.5, .79, .2), (.9, .81, .2), (2.7, .81, .3), (3.15, .79, .15),
          (3.38, .71, .05), (3.445, .62, .02), (3.46, .50)],
    ws=(0.92, 1.47), side_glass=(0.92, 3.12), rear_glass=(3.12, 3.40), pillars=[(1.88, 1.96), (2.62, 3.12)],
    stations=(0.92, 1.47, 3.12, 3.40, 1.88, 1.96, 2.62, 1.00, 1.92, 2.72, 0.28, 0.44, 3.16, 3.425, 1.02, 2.64),
    patches=[(1.47, 3.40, 'R', 0, NR, 'trim'), (3.12, 3.40, 'G', 0, NG, 'trim'), (1.02, 2.64, 'S', NS - 2, NS, 'trim')],
    lamps=_front(([(0.32, 0.64), (0.56, 0.63), (0.80, 0.665), (1.04, 0.75), (1.08, 0.79), (0.84, 0.78), (0.58, 0.725),
                   (0.36, 0.68)],
                  [(0.52, 0.65), (0.66, 0.65), (0.70, 0.705), (0.56, 0.70)]),
                 [(-0.24, 0.62), (0.24, 0.62), (0.28, 0.665), (-0.28, 0.665)],
                 [(-0.46, 0.26), (0.46, 0.26), (0.44, 0.31), (0.30, 0.52), (-0.30, 0.52), (-0.44, 0.31)], turn=40)
    + [dict(m='red', view='rear', turn=-50, off=0.004,
            pts=[(0.70, 0.78), (0.80, 0.78), (0.86, 1.05), (0.96, 1.36), (0.88, 1.38), (0.76, 1.08)]),
       dict(m='trim', view='rear', off=0.002, pts=[(-0.46, 0.30), (0.46, 0.30), (0.49, 0.41), (-0.49, 0.41)], mirror=False),
       dict(m='red', view='rear', off=0.003, pts=[(-0.42, 0.365), (0.42, 0.365), (0.42, 0.38), (-0.42, 0.38)], mirror=False)],
    shut_i=[(1.00, J_SIDE, J_UNDER), (1.92, J_SIDE, J_UNDER), (2.72, J_SIDE, J_UNDER - 4), (0.065, 0, J_RAIL + 1)],
    shut_j=[(J_RAIL, 0.44, 0.87)],
    handles=(1.76, 2.56), extras=(_aerial, _white_tail))

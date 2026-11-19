"""Mouldings: mesh builder, profile library, mitred sweeps, enriched cornices, ceiling roses,
corbels, arch helpers and per-room trim (skirting / dado / cornice) fitted from spec/house.json.
Owner: joinery agent. Public API is documented in blender/lib/README.md (section "mouldings")."""
import math

import bpy
import bmesh
from mathutils import Matrix, Vector

from . import materials as _mats

# --------------------------------------------------------------------------- materials
# logical joinery key -> lib.materials key, or (hex, roughness) for a plain colour the library lacks
MATS = {
    'joinery_white': 'white_gloss', 'plaster_white': 'plaster_white', 'upvc_white': 'upvc_white',
    'oak': 'oak_door', 'mahogany': 'mahogany', 'dark_stain': 'dark_joinery', 'threshold': 'hardwood_threshold',
    'shutter_white': 'white_satin', 'brass': 'brass', 'chrome': 'chrome', 'black': 'black_matt',
    'red_plastic': ('#B02020', 0.4), 'flap_smoked': ('#6F7678', 0.15),      # cat-flap door: translucent smoked plastic
    'glass': 'glass_clear', 'glass_frosted': 'glass_frosted', 'glass_obscure': 'glass_obscure',
    'glass_smoked': 'glass_dark',
}


def mat(key):
    """Material for a logical joinery key (MATS) or any lib.materials key."""
    k = MATS.get(key, key)
    return _mats.solid('jn_' + key, *k) if isinstance(k, tuple) else _mats.mat(k)


# --------------------------------------------------------------------------- mesh builder
class MB:
    """Accumulates primitives into one mesh with material slots (keys from MATS, or Material objects).
    Geometry is written through the current transform `M` (set with at()); a mirrored M is
    handled (winding flipped). UVs: 1 unit = 1 m, V along the grain / along the sweep path."""

    def __init__(self):
        self.bm = bmesh.new()
        self.uvl = self.bm.loops.layers.uv.new('UVMap')
        self.softl = self.bm.faces.layers.int.new('soft')    # carved relief: shaded smooth across creases
        self._soft = 0
        self.keys = []
        self.M = Matrix.Identity(4)
        self._flip = False
        self._n = 0

    def at(self, M=None):
        self.M = M.copy() if M is not None else Matrix.Identity(4)
        self._flip = self.M.determinant() < 0
        return self

    def mi(self, key):
        if key not in self.keys:
            self.keys.append(key)
        return self.keys.index(key)

    def _vs(self, cos):
        return [self.bm.verts.new(self.M @ Vector(c)) for c in cos]

    def _f(self, vs, mi, uvs=None):
        if len(set(vs)) < 3:
            return None
        if self._flip:
            vs = vs[::-1]
            uvs = uvs[::-1] if uvs else None
        try:
            f = self.bm.faces.new(vs)
        except ValueError:
            return None
        f.material_index = mi
        f.smooth = True
        f[self.softl] = self._soft
        if uvs:
            for l, uv in zip(f.loops, uvs):
                l[self.uvl].uv = uv
        return f

    def _off(self):
        self._n += 1
        return (self._n * 0.371) % 1.0, (self._n * 0.613) % 1.0

    def face(self, cos, mat, hint=None, grain=None, off=(0.0, 0.0)):
        """Planar polygon from local coords; winding is fixed so the normal agrees with `hint`."""
        cos = [Vector(c) for c in cos]
        n = Vector((0, 0, 0))
        for a, b in zip(cos, cos[1:] + cos[:1]):
            n += a.cross(b)
        if hint is not None and n.dot(Vector(hint)) < 0:
            cos = cos[::-1]
            n = -n
        ax = max(range(3), key=lambda i: abs(n[i]))
        oth = [i for i in range(3) if i != ax]
        if grain in oth:
            u, v = [i for i in oth if i != grain][0], grain
        else:
            u, v = oth
        return self._f(self._vs(cos), self.mi(mat), [(c[u] + off[0], c[v] + off[1]) for c in cos])

    def box(self, a, b, mat, bev=0.0, grain=None):
        """Axis-aligned (in local coords) cuboid between corners a and b; bev = chamfer width on all
        12 edges; grain = axis index the wood grain runs along (default: longest side)."""
        lo = [min(a[i], b[i]) for i in range(3)]
        hi = [max(a[i], b[i]) for i in range(3)]
        if grain is None:
            grain = max(range(3), key=lambda i: hi[i] - lo[i])
        off = self._off()
        bev = min(bev, 0.45 * min(hi[i] - lo[i] for i in range(3)))

        def P(ax, s):                   # vertex on face `ax` nearest the box corner with signs s
            return tuple((hi[i] if s[i] > 0 else lo[i]) if i == ax else
                         ((hi[i] - bev) if s[i] > 0 else (lo[i] + bev)) for i in range(3))

        def S(**kw):
            s = [0, 0, 0]
            for k, v in kw.items():
                s[int(k[1])] = v
            return s

        for ax in range(3):
            p, q = [i for i in range(3) if i != ax]
            for sg in (-1, 1):
                ring = [S(**{f'a{ax}': sg, f'a{p}': a, f'a{q}': b}) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
                self.face([P(ax, s) for s in ring], mat, S(**{f'a{ax}': sg}), grain, off)
        if bev <= 0:
            return
        for r in range(3):              # edge chamfers: edges running along axis r
            p, q = [i for i in range(3) if i != r]
            for sp in (-1, 1):
                for sq in (-1, 1):
                    lo_s = S(**{f'a{p}': sp, f'a{q}': sq, f'a{r}': -1})
                    hi_s = S(**{f'a{p}': sp, f'a{q}': sq, f'a{r}': 1})
                    self.face([P(p, lo_s), P(p, hi_s), P(q, hi_s), P(q, lo_s)],
                              mat, S(**{f'a{p}': sp, f'a{q}': sq}), grain, off)
        for sx in (-1, 1):              # corner triangles
            for sy in (-1, 1):
                for sz in (-1, 1):
                    s = (sx, sy, sz)
                    self.face([P(0, s), P(1, s), P(2, s)], mat, s, grain, off)

    def prism(self, base, vec, mat, grain=None):
        """Extrude a planar polygon (list of 3D points) along vec; closed solid."""
        base = [Vector(p) for p in base]
        vec = Vector(vec)
        n = Vector((0, 0, 0))
        for a, b in zip(base, base[1:] + base[:1]):
            n += a.cross(b)
        if n.dot(vec) > 0:
            base = base[::-1]
        top = [p + vec for p in base]
        off = self._off()
        self.face(base, mat, -vec, grain, off)
        self.face(top, mat, vec, grain, off)
        k = len(base)
        for j in range(k):
            e = base[(j + 1) % k] - base[j]
            self.face([base[j], top[j], top[(j + 1) % k], base[(j + 1) % k]], mat, vec.cross(e), grain, off)

    def sweep(self, profile, path, mat, closed=False, up=(0, 0, 1), caps=True, ends=(None, None)):
        """Sweep a 2D profile [(d, h)...] along a polyline with mitred corners.
        Ring point = P + d*side + h*up, side = up x travel (for up=+Z: LEFT of travel, so a CCW
        room path puts d into the room). `up` is constant: use +Z for skirting/dado/cornice (also
        raking rails: plumb mitres) and the wall normal for architraves / archivolts / raking
        pediment cornices drawn in the wall plane. The profile must be listed counter-clockwise
        round the solid when seen with the travel direction pointing at the viewer (e.g. skirting:
        from (thickness, 0) up to (0, height)); only the listed edges are faced. Open paths are
        capped with the profile polygon. ends = (m0, m1): optional vectors replacing `side` at the
        first / last ring of an open path, for skew cuts (ring point = P + d*m + h*up)."""
        up = Vector(up).normalized()
        P = [Vector(p) for p in path]
        n, k = len(P), len(profile)
        if n < 2:
            return

        def side(a, b):
            s = up.cross(b - a)
            return s.normalized()

        rings, sides = [], []
        for i in range(n):
            a = P[i - 1] if (i > 0 or closed) else None
            b = P[(i + 1) % n] if (i < n - 1 or closed) else None
            if a is not None and b is not None:
                s1, s2 = side(a, P[i]), side(P[i], b)
                m = (s1 + s2) / max(1e-6, 1 + s1.dot(s2))
            elif b is not None:
                m = Vector(ends[0]) if ends[0] is not None else side(P[i], b)
            else:
                m = Vector(ends[1]) if ends[1] is not None else side(a, P[i])
            sides.append(m)
            rings.append([P[i] + m * d + up * h for d, h in profile])
        us = [0.0]
        for (d0, h0), (d1, h1) in zip(profile, profile[1:]):
            us.append(us[-1] + math.hypot(d1 - d0, h1 - h0))
        vsum = [0.0]
        for a, b in zip(P, P[1:] + (P[:1] if closed else [])):
            vsum.append(vsum[-1] + (b - a).length)
        ou, ov = self._off()
        mi = self.mi(mat)
        V = [self._vs(r) for r in rings]
        for i in range(n if closed else n - 1):
            i2 = (i + 1) % n
            for j in range(k - 1):
                self._f([V[i][j], V[i][j + 1], V[i2][j + 1], V[i2][j]], mi,
                        [(us[j] + ou, vsum[i] + ov), (us[j + 1] + ou, vsum[i] + ov),
                         (us[j + 1] + ou, vsum[i + 1] + ov), (us[j] + ou, vsum[i + 1] + ov)])
        if caps and not closed and k >= 3:
            # End polygons. A profile that starts on the wall and ends on the ceiling / floor (cornice,
            # skirting) is closed through that corner: closed by the bare chord it is a sliver of ~zero
            # area whose normal can point either way (the dark cornice end at the lobby post).
            (d0, h0), (d1, h1) = profile[0], profile[-1]
            prof = list(profile)
            if abs(d0 - d1) > 1e-6 and abs(h0 - h1) > 1e-6:
                prof += [q for q in ((d0, h1), (d1, h0)) if (d0 - d1) * (q[1] - h1) - (h0 - h1) * (q[0] - d1) < 0][:1]
            uv = [(d + ou, h + ov) for d, h in prof]
            for i, rev in ((0, True), (n - 1, False)):
                vs = self._vs([P[i] + sides[i] * d + up * h for d, h in prof])
                self._f(vs[::-1] if rev else vs, mi, uv[::-1] if rev else uv)

    def lathe(self, profile, mat, segs=24, ell=(1.0, 1.0), a0=0.0, a1=2 * math.pi):
        """Revolve [(r, z)...] round local Z (profile CCW in the r-z half plane: e.g. from the axis
        at the bottom outwards and up). ell scales x / y for elliptical domes."""
        full = abs((a1 - a0) - 2 * math.pi) < 1e-6
        na = segs if full else segs + 1
        mi = self.mi(mat)
        V = []
        axis = {}
        for i in range(na):
            th = a0 + (a1 - a0) * i / segs
            ring = []
            for j, (r, z) in enumerate(profile):
                if r < 1e-7:
                    if j not in axis:
                        axis[j] = self._vs([(0, 0, z)])[0]
                    ring.append(axis[j])
                else:
                    ring.append(self._vs([(ell[0] * r * math.cos(th), ell[1] * r * math.sin(th), z)])[0])
            V.append(ring)
        us = [0.0]
        for (r0, z0), (r1, z1) in zip(profile, profile[1:]):
            us.append(us[-1] + math.hypot(r1 - r0, z1 - z0))
        for i in range(segs):
            i2 = (i + 1) % na
            for j in range(len(profile) - 1):
                vs = []
                for v in (V[i][j], V[i2][j], V[i2][j + 1], V[i][j + 1]):
                    if v not in vs:
                        vs.append(v)
                t0, t1 = i / segs, (i + 1) / segs
                self._f(vs, mi, [(t0, us[j]), (t1, us[j]), (t1, us[j + 1]), (t0, us[j + 1])][:len(vs)])

    def dome(self, rx, ry, h, mat, segs=8, rings=3):
        """Half-ellipsoid sitting on the local XY plane, bulging to +Z."""
        prof = [(math.cos(math.pi / 2 * k / rings), h * math.sin(math.pi / 2 * k / rings))
                for k in range(rings + 1)]
        self._soft = 1
        self.lathe(prof, mat, segs, ell=(rx, ry))
        self._soft = 0

    def leaf(self, length, width, relief, mat, segs=6, serrate=0.0, curl=0.0, base=0.25, rib=0.55,
             round_=0.6, skew=1.0):
        """Low-relief acanthus-style leaf lying on the local XY plane: stem at the origin, tip at
        +Y, relief to +Z. Two swelling halves with a midrib valley; serrate = lobed edge amount;
        round_ < 1 = blunt broad leaf, 1 = pointed; skew > 1 moves the widest point to the tip."""
        mi = self.mi(mat)
        rows = []
        self._soft = 1
        for i in range(segs + 1):
            t = 1 - (1 - i / segs) ** (1.7 if round_ < 0.8 else 1.0)       # blunt leaves: rows crowd the tip
            w = 0.5 * width * (base * (1 - t) + (1 - base) * max(0.0, math.sin(math.pi * t ** skew)) ** round_)
            if serrate and 0 < i < segs and i % 2 == 0:
                w *= 1 - serrate
            z = relief * (math.sin(math.pi * min(1.0, t * 1.1 + 0.08)) ** 0.5) + curl * relief * t ** 3
            if i == segs:
                w, z = 0.0, curl * relief + relief * 0.15
            y = t * length
            rows.append(self._vs([(-w, y, 0), (-0.55 * w, y, z * 0.9), (0, y, z * rib),
                                  (0.55 * w, y, z * 0.9), (w, y, 0)]))
        for i in range(segs):
            for j in range(4):
                a, b, c, d = rows[i][j], rows[i][j + 1], rows[i + 1][j + 1], rows[i + 1][j]
                self._f([a, b, c, d], mi, [(j / 4, i / segs), ((j + 1) / 4, i / segs),
                                           ((j + 1) / 4, (i + 1) / segs), (j / 4, (i + 1) / segs)])
        self._soft = 0

    def tube(self, path, r, mat, n=8, closed=False, up=None):
        """Round bar along a polyline. The section frame is built on one constant `up` (default: Z, or X
        for a steep chord), so the bar pinches where the path runs parallel to it: for a loop lying in a
        plane pass up=<plane normal> (e.g. the wall normal for a ring on a wall)."""
        P = [Vector(p) for p in path]
        d = (P[-1] - P[0]).normalized()
        up = Vector(up) if up is not None else Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))
        prof = [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n)) for i in range(n)]
        self.sweep(prof + prof[:1], P, mat, closed=closed, up=up)

    def finish(self, name, matrix=None, sharp_deg=35.0):
        """-> new Object (not linked to a collection; ctx.add links it). Smooth-shaded with edges
        sharper than sharp_deg marked sharp."""
        bm = self.bm
        bm.normal_update()
        cs, cs_soft = math.cos(math.radians(sharp_deg)), math.cos(math.radians(80.0))
        for e in bm.edges:
            lf = e.link_faces
            if len(lf) == 2:
                soft = lf[0][self.softl] and lf[1][self.softl]
                if lf[0].normal.dot(lf[1].normal) < (cs_soft if soft else cs):
                    e.smooth = False
        ms = [k if isinstance(k, bpy.types.Material) else mat(k) for k in self.keys]
        for i, m in enumerate(ms):                      # metres -> texture repeats
            sz = m.get('size_m') if m is not None else None
            if sz and (sz[0] != 1.0 or sz[1] != 1.0):
                for f in bm.faces:
                    if f.material_index == i:
                        for l in f.loops:
                            uv = l[self.uvl].uv
                            l[self.uvl].uv = (uv[0] / sz[0], uv[1] / sz[1])
        bm.faces.layers.int.remove(self.softl)
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        for m in ms:
            me.materials.append(m)
        ob = bpy.data.objects.new(name, me)
        if matrix is not None:
            ob.matrix_world = matrix
        return ob


def tri_count(obs):
    return sum(len(p.vertices) - 2 for o in obs if o.type == 'MESH' for p in o.data.polygons)


def sweep(profile, path, closed=False, name='sweep', material='joinery_white', up=(0, 0, 1)):
    """One-call sweep -> Object. profile: key in PROFILES or [(d, h)...]; path: [(x, y, z)...]."""
    mb = MB()
    mb.sweep(PROFILES[profile] if isinstance(profile, str) else profile, path, material, closed, up)
    return mb.finish(name)


# --------------------------------------------------------------------------- profile helpers
def _q(p0, p1, mode='hv', n=4):
    """Quarter ellipse p0 -> p1 (p0 excluded). 'hv' leaves p0 horizontally (along d) and arrives
    vertically; 'vh' the reverse."""
    (d0, h0), (d1, h1) = p0, p1
    c = (d0, h1) if mode == 'hv' else (d1, h0)
    return [(c[0] + (d0 - c[0]) * math.cos(a) + (d1 - c[0]) * math.sin(a),
             c[1] + (h0 - c[1]) * math.cos(a) + (h1 - c[1]) * math.sin(a))
            for a in (math.pi / 2 * i / n for i in range(1, n + 1))]


def _s(p0, p1, n=6, mode='h'):
    """S-curve p0 -> p1 (p0 excluded). 'h': tangents along d at both ends (cyma recta when rising
    outward); 'v': tangents along h at both ends (cyma reversa / ogee)."""
    (d0, h0), (d1, h1) = p0, p1
    out = []
    for i in range(1, n + 1):
        t = i / n
        e = (1 - math.cos(math.pi * t)) / 2
        out.append((d0 + (d1 - d0) * t, h0 + (h1 - h0) * e) if mode == 'h'
                   else (d0 + (d1 - d0) * e, h0 + (h1 - h0) * t))
    return out


def _half(p0, p1, n=4):
    """Half-round p0 -> p1 (p0 excluded) bulging to the right of travel (outward on a CCW outline)."""
    c = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
    r = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) / 2
    a0 = math.atan2(p0[1] - c[1], p0[0] - c[0])
    return [(c[0] + r * math.cos(a0 + math.pi * i / n), c[1] + r * math.sin(a0 + math.pi * i / n))
            for i in range(1, n + 1)]


def _scale(p, sd=1.0, sh=1.0):
    return [(d * sd, h * sh) for d, h in p]


def _build_profiles():
    P = {}
    # ---- skirtings: (d = thickness from wall, h = height from floor), base z = floor
    p = [(0.020, 0), (0.020, 0.120), (0.016, 0.126)] + _s((0.016, 0.126), (0.008, 0.156), 5, 'v')
    P['sk_hall'] = p + [(0.006, 0.160)] + _half((0.006, 0.160), (0.006, 0.170), 4) + [(0, 0.170)]
    P['sk_kitchen'] = P['sk_hall']
    p = [(0.022, 0), (0.022, 0.140), (0.018, 0.146)] + _s((0.018, 0.146), (0.009, 0.186), 5, 'v')
    P['sk_vest'] = p + [(0.007, 0.190)] + _half((0.007, 0.190), (0.007, 0.200), 4) + [(0, 0.200)]
    P['sk_living'] = ([(0.020, 0), (0.020, 0.115), (0.016, 0.120)] + _s((0.016, 0.120), (0.006, 0.162), 6, 'v')
                      + [(0.006, 0.170), (0, 0.170)])
    P['sk_utility'] = ([(0.018, 0), (0.018, 0.125), (0.012, 0.128)] + _half((0.012, 0.128), (0.012, 0.140), 4)
                       + _s((0.012, 0.140), (0.004, 0.166), 4, 'v') + [(0.004, 0.170), (0, 0.170)])
    P['sk_dining'] = ([(0.020, 0), (0.020, 0.105), (0.014, 0.107)] + _half((0.014, 0.107), (0.014, 0.122), 4)
                      + [(0.012, 0.125)] + _s((0.012, 0.125), (0.004, 0.147), 4, 'v') + [(0.004, 0.150), (0, 0.150)])
    # ---- dado rails: base z = top of rail - height
    P['dado_hall'] = ([(0, 0), (0.008, 0), (0.008, 0.004)] + _q((0.008, 0.004), (0.016, 0.024), 'vh')
                      + [(0.016, 0.030)] + _half((0.016, 0.030), (0.016, 0.058), 6)
                      + [(0.022, 0.058), (0.022, 0.070), (0, 0.070)])                     # 70 x 30
    p = [(0, 0), (0.004, 0)] + _q((0.004, 0), (0.018, 0.009), 'vh')
    for i in range(5):
        p += _half((0.018, 0.009 + 0.008 * i), (0.018, 0.017 + 0.008 * i), 3)
    P['dado_dining'] = p + [(0.016, 0.049)] + _half((0.016, 0.049), (0.016, 0.055), 3) + [(0, 0.055)]  # 55 x 22
    # ---- cornices: (d = projection along the ceiling, h = below ceiling, negative), base z = ceiling
    P['cornice_hall'] = ([(0, -0.220), (0.010, -0.220), (0.010, -0.205)]
                         + _s((0.010, -0.205), (0.040, -0.170), 5, 'v')
                         + [(0.040, -0.095), (0.130, -0.095), (0.130, -0.055), (0.136, -0.055)]
                         + _s((0.136, -0.055), (0.192, -0.010), 6, 'h') + [(0.200, -0.010), (0.200, 0)])
    P['cornice_living'] = ([(0, -0.150), (0.012, -0.150)] + _half((0.012, -0.150), (0.012, -0.144), 3)
                           + [(0.012, -0.095), (0.022, -0.095), (0.022, -0.085)]
                           + _s((0.022, -0.085), (0.090, -0.030), 6, 'h') + [(0.095, -0.030), (0.095, -0.020)]
                           + _q((0.095, -0.020), (0.118, -0.006), 'hv') + [(0.130, -0.006), (0.130, 0)])
    P['cornice_kitchen'] = ([(0, -0.110), (0.008, -0.110), (0.008, -0.098)]
                            + _q((0.008, -0.098), (0.086, -0.022), 'vh', 7)
                            + [(0.086, -0.010), (0.110, -0.010), (0.110, 0)])
    P['cornice_utility'] = ([(0, -0.080), (0.008, -0.080), (0.008, -0.072)]
                            + _s((0.008, -0.072), (0.052, -0.013), 6, 'h')
                            + [(0.056, -0.013), (0.056, -0.005), (0.086, -0.005), (0.086, 0)])
    P['cornice_wc'] = P['cornice_utility']
    P['cornice_dining'] = ([(0, -0.150), (0.008, -0.150), (0.008, -0.140)]
                           + _q((0.008, -0.140), (0.026, -0.115), 'vh') + [(0.030, -0.115)]
                           + _half((0.030, -0.115), (0.030, -0.105), 3)
                           + [(0.032, -0.105), (0.087, -0.050), (0.092, -0.050), (0.092, -0.042)]
                           + _s((0.092, -0.042), (0.115, -0.012), 5, 'h')
                           + [(0.115, -0.006), (0.130, -0.006), (0.130, 0)])
    # ---- architraves: (d = across the face from the opening edge outward, h = projection off the
    #      wall); listed outer edge first. Sweep with up = wall normal, path right leg up -> head -> left leg down.
    P['arch_hall'] = ([(0.070, 0), (0.070, 0.020), (0.064, 0.020)] + _s((0.064, 0.020), (0.042, 0.012), 5, 'h')
                      + [(0, 0.012), (0, 0)])
    P['arch_living'] = ([(0.100, 0), (0.100, 0.025), (0.092, 0.025)] + _s((0.092, 0.025), (0.068, 0.016), 5, 'h')
                        + [(0.041, 0.016), (0.038, 0.010), (0.008, 0.010)]
                        + _half((0.008, 0.010), (0.0, 0.010), 3) + [(0, 0)])
    P['arch_kitchen'] = ([(0.080, 0), (0.080, 0.022), (0.067, 0.022)] + _s((0.067, 0.022), (0.043, 0.014), 5, 'h')
                         + [(0.040, 0.012), (0, 0.012), (0, 0)])
    P['arch_utility'] = ([(0.072, 0), (0.072, 0.015)] + _half((0.072, 0.015), (0.062, 0.015), 3)
                         + _s((0.062, 0.015), (0.014, 0.008), 6, 'h') + [(0.012, 0.011), (0, 0.011), (0, 0)])
    P['arch_hall_dining'] = _scale(P['arch_living'], 0.85, 0.9)
    P['arch_vest_window'] = _scale(P['arch_living'], 0.75, 0.8)
    p = [(0.110, 0), (0.110, 0.016), (0.102, 0.016)]
    for i in range(3):
        p += _half((0.102 - 0.012 * i, 0.016), (0.090 - 0.012 * i, 0.016), 3)
    P['arch_dark'] = p + [(0.060, 0.016), (0.058, 0.018), (0, 0.018), (0, 0)]            # reeded, 110
    P['arch_dark_window'] = _scale(P['arch_dark'], 0.10 / 0.11, 1.0)
    # ---- returned cap / shelf mouldings: (d = projection, h = height above the member's base)
    P['dark_cap'] = ([(0, 0), (0.004, 0)] + _q((0.004, 0), (0.014, 0.018), 'vh') + [(0.018, 0.018), (0.018, 0.030)]
                     + _s((0.018, 0.030), (0.052, 0.075), 5, 'h') + [(0.060, 0.075), (0.060, 0.090), (0, 0.090)])
    P['ped_bed'] = ([(0, 0), (0.004, 0)] + _s((0.004, 0), (0.030, 0.043), 5, 'h')
                    + [(0.035, 0.043), (0.035, 0.055), (0, 0.055)])
    P['ped_shelf'] = ([(0, 0), (0.010, 0)] + _q((0.010, 0), (0.060, 0.030), 'vh', 5)
                      + [(0.075, 0.030), (0.075, 0.056), (0.072, 0.060), (0, 0.060)])
    P['ped_cornice'] = ([(0, 0), (0.012, 0), (0.012, 0.022), (0.018, 0.022)]
                        + _s((0.018, 0.022), (0.060, 0.058), 6, 'h') + [(0.070, 0.058), (0.070, 0.070), (0, 0.070)])
    P['ped_rake'] = P['ped_cornice']
    P['ped_cap'] = ([(0, 0), (0.006, 0), (0.006, 0.010)] + _q((0.006, 0.010), (0.024, 0.028), 'vh')
                    + [(0.032, 0.028), (0.032, 0.040), (0, 0.040)])
    P['impost_vest'] = ([(0, 0), (0.002, 0)] + _half((0.002, 0), (0.002, 0.012), 3)
                        + [(0.002, 0.107), (0.010, 0.107), (0.010, 0.122)]
                        + _q((0.010, 0.122), (0.045, 0.182), 'hv', 5) + [(0.050, 0.182), (0.050, 0.230), (0, 0.230)])
    P['archivolt'] = ([(0.120, 0), (0.120, 0.012)] + _half((0.120, 0.012), (0.108, 0.012), 4)
                      + [(0.106, 0.015), (0, 0.015), (0, 0)])
    P['bay_sill'] = ([(0, 0), (0.020, 0)] + _q((0.020, 0), (0.040, 0.040), 'vh') + [(0.045, 0.040), (0.045, 0.050)]
                     + _q((0.045, 0.050), (0.060, 0.068), 'hv') + [(0.060, 0.090), (0, 0.090)])
    P['bead_bolection'] = [(0.016, -0.008), (0.012, -0.002), (0.007, 0.003), (0.002, 0.003), (-0.003, 0.0)]
    P['bead_ovolo'] = [(0.012, -0.008), (0.009, -0.003), (0.004, 0.0), (0.0, 0.0)]
    for a, b in (('skirting_vestibule', 'sk_vest'), ('skirting_hall', 'sk_hall'), ('skirting_living', 'sk_living'),
                 ('skirting_kitchen', 'sk_kitchen'), ('skirting_utility', 'sk_utility'), ('skirting_dining', 'sk_dining'),
                 ('coving_kitchen', 'cornice_kitchen'), ('coving_utility', 'cornice_utility')):
        P[a] = P[b]                      # names used by shell.FINISHES
    return P


PROFILES = _build_profiles()
# cornice enrichment data: where the modillion band / acanthus face sits in the profile
HALL_BAND = dict(d=0.040, top=-0.095, w=0.055, h=0.070, proj=0.060, pitch=0.13)
DINING_FACE = dict(p0=(0.032, -0.105), p1=(0.087, -0.050), repeat=0.075)


def profile_size(key):
    """(projection, height) bounding size of a named profile."""
    p = PROFILES[key]
    return (max(d for d, h in p) - min(d for d, h in p), max(h for d, h in p) - min(h for d, h in p))


# --------------------------------------------------------------------------- arches
def arch_points(kind, x0, x1, springing, crown, n=24, haunch=None):
    """Intrados polyline [(x, z)...] from (x0, springing) over the crown to (x1, springing).
    kind 'segmental' (one circular arc) or 'basket' (quarter-round haunches of radius `haunch`
    = crown - springing by default, flat crown between)."""
    rise = crown - springing
    if kind == 'segmental':
        half = (x1 - x0) / 2
        r = (half * half + rise * rise) / (2 * rise)
        a = math.asin(half / r)
        cx, cz = (x0 + x1) / 2, crown - r
        return [(cx + r * math.sin(-a + 2 * a * i / n), cz + r * math.cos(-a + 2 * a * i / n)) for i in range(n + 1)]
    r = haunch or rise
    m = max(3, n // 3)
    left = [(x0 + r - r * math.cos(math.pi / 2 * i / m), springing + rise * math.sin(math.pi / 2 * i / m))
            for i in range(m + 1)]
    return left + [(x1 - (x - x0), z) for x, z in reversed(left)]


# --------------------------------------------------------------------------- enrichment
def stations(path, closed, pitch, dm=0.0):
    """Evenly spaced stations along every straight leg of a mitred run, set out on the line offset
    dm to the left of the path (legs shorten at inside corners, lengthen at outside corners).
    -> [(point on the path, unit travel dir, actual step)]."""
    P = [Vector(p) for p in path]
    n = len(P)

    def turn(j):
        if not closed and (j <= 0 or j >= n - 1):
            return 0
        p, q, r = P[(j - 1) % n], P[j % n], P[(j + 1) % n]
        c = (q.x - p.x) * (r.y - q.y) - (q.y - p.y) * (r.x - q.x)
        return 1 if c > 1e-9 else (-1 if c < -1e-9 else 0)

    out = []
    for i in range(n if closed else n - 1):
        a, b = P[i], P[(i + 1) % n]
        t = b - a
        L = t.length
        t = t / L
        ta, tb = dm * turn(i), dm * turn(i + 1)
        span = L - ta - tb
        k = int(round(span / pitch))
        if k <= 0:
            continue
        step = span / k
        out += [(a + t * (ta + (m + 0.5) * step), t, step) for m in range(k)]
    return out


def fluted_body(mb, path, x0, x1, back, mat, n=3, depth=0.004):
    """Solid whose front follows `path` [(y, z)...] (listed top to bottom in the local YZ plane) and
    is carved with n flutes running along the path between x0 and x1; `back` = [(y, z)...] closing
    the side outline from the path end round to the path start. Used for modillions and corbels."""
    W = x1 - x0
    f = W * 0.07
    fw = (W - (n + 1) * f) / n
    prof = [(0.0, x0)]
    for i in range(n):
        s = x0 + f + i * (fw + f)
        prof += [(0.0, s), (-0.8 * depth, s + 0.2 * fw), (-depth, s + 0.5 * fw), (-0.8 * depth, s + 0.8 * fw),
                 (0.0, s + fw)]
    T = depth + 0.003
    prof += [(0.0, x1), (-T, x1), (-T, x0), (0.0, x0)]
    P3 = [Vector((0, y, z)) for y, z in path]
    mb.sweep(prof, P3, mat, up=(1, 0, 0))
    # inner fill: side outline with the front pulled back by depth + 1 mm
    k = len(path)
    inner = []
    for i, (y, z) in enumerate(path):
        a = Vector(path[max(i - 1, 0)])
        b = Vector(path[min(i + 1, k - 1)])
        t = (b - a).normalized()
        nrm = Vector((-t.y, t.x))            # X x t  in (y, z): outward
        inner.append((y - nrm.x * (depth + 0.001), z - nrm.y * (depth + 0.001)))
    poly = [Vector((x0 + 0.0003, y, z)) for y, z in inner + list(back)]
    mb.prism(poly, (W - 0.0006, 0, 0), mat)


def modillion(mb, mat='plaster_white', w=0.055, h=0.070, proj=0.060):
    """Fluted block of the hall cornice. Local frame: origin on the band face under the corona,
    X along the wall, Y out of the wall, block hangs to -Z."""
    cap = 0.012
    mb.box((-w / 2, 0, -cap), (w / 2, proj, 0), mat)
    bw = w * 0.86
    yf = proj - 0.005
    path = [(yf, -cap), (yf, -h * 0.55)] + _q((yf, -h * 0.55), (0.012, -h), 'vh', 4)
    fluted_body(mb, path, -bw / 2, bw / 2, [(0, -h), (0, -cap)], mat, 3, 0.004)


def _fluted_grid(mb, rows, n, mat, depth=0.42, fillet=0.09):
    """Vertical face carved with n flutes that narrow to points. rows (top -> bottom):
    (P0, P1, out, wz): the face spans P0 -> P1 at that level (walking counter-clockwise round the
    solid seen from above), `out` = outward unit normal (flutes are cut against it), wz = 1 full-width flutes
    .. 0 none (pointed ends). Flute depth = depth x its width."""
    fw = (1.0 - (n + 1) * fillet) / n                         # flute width as a fraction of the face
    cols = [(0.0, 0.0, 0.0)]                                  # (s at wz = 1, s of the flute centre, depth factor)
    for i in range(n):
        c = fillet + i * (fw + fillet) + fw / 2
        cols += [(c + k * fw / 2, c, 1 - k * k) for k in (-1, -0.6, 0, 0.6, 1)]
    cols.append((1.0, 1.0, 0.0))
    V, uv = [], []
    for P0, P1, out, wz in rows:
        P0, P1, out = Vector(P0), Vector(P1), Vector(out)
        L = (P1 - P0).length
        pts = [P0 + (P1 - P0) * (c + (s_ - c) * wz) - out * (depth * fw * L * wz * dk) for s_, c, dk in cols]
        V.append(mb._vs(pts))
        uv.append([((c + (s_ - c) * wz) * L, P0.z) for s_, c, dk in cols])
    mi = mb.mi(mat)
    mb._soft = 1
    for i in range(len(V) - 1):
        for j in range(len(cols) - 1):
            mb._f([V[i][j], V[i + 1][j], V[i + 1][j + 1], V[i][j + 1]], mi,
                  [uv[i][j], uv[i + 1][j], uv[i + 1][j + 1], uv[i][j + 1]])
    mb._soft = 0


def arch_corbel(mb, length=0.26, proj=0.11, height=0.38, mat='plaster_white'):
    """Hall arch corbel (f_0282..f_0285). Local frame: origin on the jamb face at the TOP centre
    (springing level), X along the jamb (through the wall thickness), Y out of the jamb into the
    opening, -Z down. From the top: stepped three-fillet cap (90), plain neck block, a cavetto that
    sweeps back on the front and both ends to a slender shaft, three flutes on each of the three
    faces running down the sweep and dying out as points on the shaft (the scalloped edge), and a
    small moulded drop block attached under the shaft."""
    for i, st in enumerate((0.045, 0.030, 0.015)):          # top fillet steps out most
        L, pr = length - 2 * (0.045 - st), proj - (0.045 - st) * 0.67
        mb.box((-L / 2, 0, -0.030 * (i + 1)), (L / 2, pr, -0.030 * i), mat, bev=0.0015)
    k = (height - 0.09) / 0.29                                # the spec body is 0.29 high
    a0, p0 = (length - 0.09) / 2, proj - 0.030                # neck: half length, projection
    a1, p1 = a0 * 0.62, p0 * 0.48                             # shaft
    zt, zn = -0.09, -0.09 - 0.045 * k
    zc, ztip, zf, zb = zn - 0.115 * k, zn - 0.185 * k, zn - 0.185 * k, -height
    mb.box((-a0, 0, zn), (a0, p0, zt + 0.001), mat, bev=0.001)
    lv = []                                                   # (z, half length, projection, flute width factor)
    for i in range(7):                                        # cavetto: leaves the neck horizontally, lands plumb
        th = math.pi / 2 * i / 6
        f = 1 - math.sin(th)
        lv.append((zn - (zn - zc) * (1 - math.cos(th)), a1 + (a0 - a1) * f, p1 + (p0 - p1) * f, 1.0))
    lv += [(zc + (ztip - zc) * t, a1, p1, max(0.0, 1 - t / 0.8)) for t in (0.2, 0.4, 0.6, 0.8, 1.0)]
    for face in range(3):                                     # +X end, front, -X end (counter-clockwise from above)
        rows = []
        for z, a, p, wz in lv:
            P0, P1, inw = (((a, 0, z), (a, p, z), (1, 0, 0)), ((a, p, z), (-a, p, z), (0, 1, 0)),
                           ((-a, p, z), (-a, 0, z), (-1, 0, 0)))[face]
            rows.append((P0, P1, inw, wz))
        _fluted_grid(mb, rows, 3, mat)
    e = 0.012 * k                                             # drop: fillet block with a splayed underside
    mb.box((-a1 - e / 2, 0, zf - 0.016 * k), (a1 + e / 2, p1 + e / 2, zf + 0.002), mat, bev=0.001)
    side = [(0, zb), (p1 * 0.45, zb), (p1 + e, zb + 0.018 * k), (p1 + e, zf - 0.014 * k), (0, zf - 0.014 * k)]
    mb.prism([Vector((-a1 - e, y, z)) for y, z in side], (2 * (a1 + e), 0, 0), mat)


def scroll_corbel(mb, w=0.10, h=0.16, proj=0.075, foot=0.045, mat='joinery_white'):
    """Acanthus console of the pedimented doorcase. Local frame: origin at the wall, bottom centre;
    X along the wall, Y out, Z up. Rect cap, tapering body, oval cabochon framed by two leaves,
    pendant husk and a three-lobed gadrooned foot."""
    mb.box((-w / 2, 0, h - 0.022), (w / 2, proj, h), mat, bev=0.002)
    bw = w * 0.88
    side = [(0, 0.012), (foot * 0.8, 0.012)] + _s((foot * 0.8, 0.012), (proj - 0.012, h - 0.022), 6, 'v') + [(0, h - 0.022)]
    mb.prism([Vector((-bw / 2, y, z)) for y, z in side], (bw, 0, 0), mat)
    # decoration on the (tilted) front: frame with X along the wall, Y up the front, Z out
    a, b = Vector((0, foot * 0.8 + 0.004, 0.02)), Vector((0, proj - 0.012, h - 0.03))
    yl = (b - a).normalized()
    zl = yl.cross(Vector((1, 0, 0)))
    F = mb.M @ Matrix(((-1, yl.x, zl.x, a.x), (0, yl.y, zl.y, a.y), (0, yl.z, zl.z, a.z), (0, 0, 0, 1)))
    M0 = mb.M.copy()
    L = (b - a).length
    mb.at(F @ Matrix.Translation((0, L * 0.56, 0.004)))
    mb.dome(0.015, 0.024, 0.014, mat, 10, 3)                          # cabochon
    for sgn in (-1, 1):                                               # framing leaves
        mb.at(F @ Matrix.Translation((sgn * 0.030, L * 0.30, 0.002)) @ Matrix.Rotation(sgn * 0.20, 4, 'Z'))
        mb.leaf(L * 0.62, 0.030, 0.012, mat, 6, serrate=0.25, curl=0.8)
    mb.at(F @ Matrix.Translation((0, L * 0.36, 0.002)) @ Matrix.Rotation(math.pi, 4, 'Z'))
    mb.leaf(L * 0.22, 0.018, 0.008, mat, 4)                           # pendant husk
    mb.at(M0)
    for i in (-1, 0, 1):                                              # gadrooned foot
        mb.at(M0 @ Matrix.Translation((i * bw * 0.31, foot * 0.45, 0.022)) @ Matrix.Rotation(-math.pi / 2, 4, 'X'))
        mb.dome(bw * 0.17, foot * 0.5, 0.022, mat, 8, 3)
    mb.at(M0)


def shell_scroll_ornament(mb, width=0.35, height=0.075, relief=0.010, mat='joinery_white'):
    """Applied frieze ornament (f_0082): a bold nine-rib scallop shell on a raised boss, flanked by
    a round volute and a trail of foliage each side. Local frame: centred at the origin on the
    frieze face, X along, Y up, Z out of the face. Overall ~width x height."""
    M0 = mb.M.copy()
    k, by = width / 0.35, -height * 0.42
    T = Matrix.Translation
    mb.at(M0 @ T((0, by + 0.020 * k, 0)))
    mb.dome(0.036 * k, 0.034 * k, relief * 0.55, mat, 14, 2)             # shell body
    for i in range(9):                                                # ribs fanning out from the hinge
        ang = math.radians(-80 + 20 * i)
        mb.at(M0 @ T((0, by, relief * 0.25)) @ Matrix.Rotation(-ang, 4, 'Z'))
        mb.leaf(height * 0.86, 0.019 * k, relief, mat, 4, base=0.45, round_=0.5, rib=1.0, skew=1.4)
    mb.at(M0 @ T((0, by, 0)))
    mb.dome(0.013 * k, 0.011 * k, relief * 1.3, mat, 8, 2)               # hinge boss
    for sgn in (-1, 1):
        cx, cy, r = sgn * 0.066 * k, by + 0.026 * k, 0.017 * k        # volute: ring + eye
        mb.at(M0 @ T((cx, cy, relief * 0.45)))
        mb.tube([(r * math.cos(2 * math.pi * j / 12), r * math.sin(2 * math.pi * j / 12), 0) for j in range(12)],
                relief * 0.55, mat, 6, closed=True)
        mb.dome(0.008 * k, 0.008 * k, relief * 0.6, mat, 8, 2)
        x = 0.088 * k
        for j, (ln, ang, dy) in enumerate(((0.046, 76, -0.008), (0.038, 104, 0.012), (0.032, 80, -0.004))):
            mb.at(M0 @ T((sgn * x, dy * k, 0)) @ Matrix.Rotation(-sgn * math.radians(ang), 4, 'Z'))
            mb.leaf(ln * k, (0.032 - 0.004 * j) * k, relief, mat, 6, serrate=0.3, curl=0.6, base=0.4, round_=0.6)
            x += ln * k * 0.76
    mb.at(M0)


def cornice(mb, key, path, closed=False, mat='plaster_white'):
    """Sweep a named cornice along a run (path z = ceiling) and add its enrichment: fluted
    modillion blocks for 'cornice_hall', the upright acanthus-leaf band for 'cornice_dining'."""
    mb.sweep(PROFILES[key], path, mat, closed)
    M0 = mb.M.copy()
    Z = Vector((0, 0, 1))
    if PROFILES[key] is PROFILES['cornice_hall']:
        B = HALL_BAND
        for p, t, _ in stations(path, closed, B['pitch'], B['d'] + B['proj'] + 0.01):
            s = Z.cross(t)
            o = p + s * B['d'] + Z * B['top']
            mb.at(M0 @ Matrix(((t.x, s.x, 0, o.x), (t.y, s.y, 0, o.y), (0, 0, 1, o.z), (0, 0, 0, 1))))
            modillion(mb, mat, B['w'], B['h'], B['proj'])
    elif PROFILES[key] is PROFILES['cornice_dining']:
        (d0, h0), (d1, h1) = DINING_FACE['p0'], DINING_FACE['p1']
        fl = math.hypot(d1 - d0, h1 - h0)
        for p, t, step in stations(path, closed, DINING_FACE['repeat'], (d0 + d1) / 2):
            s = Z.cross(t)
            yl = (s * (d1 - d0) + Z * (h1 - h0)).normalized()
            zl = yl.cross(t)
            o = p + s * d0 + Z * h0 + zl * 0.0004
            F = M0 @ Matrix(((-t.x, yl.x, zl.x, o.x), (-t.y, yl.y, zl.y, o.y), (-t.z, yl.z, zl.z, o.z), (0, 0, 0, 1)))
            mb.at(F @ Matrix.Translation((0, 0.003, 0)))
            mb.leaf(fl * 0.94, step * 0.74, 0.008, mat, 5, serrate=0.2, curl=0.5, base=0.45, round_=0.45, skew=1.3)
            mb.at(F @ Matrix.Translation((step / 2, 0.003, 0)))
            mb.leaf(fl * 0.80, step * 0.22, 0.004, mat, 3, base=0.7, round_=1.0)
    mb.at(M0)


# --------------------------------------------------------------------------- ceiling roses
def _radial(theta, r, z=0.0):
    """Frame at radius r, angle theta: local +Y radially outward, +Z DOWN (relief hangs below)."""
    c, s = math.cos(theta), math.sin(theta)
    return Matrix(((-s, c, 0, r * c), (c, s, 0, r * s), (0, 0, -1, z), (0, 0, 0, 1)))


ROSES = {'living': dict(style='acanthus_whorl', d=0.75), 'dining': dict(style='floral_dish', d=0.90)}


def ceiling_rose(style='acanthus_whorl', name='rose', mat='plaster_white'):
    """-> Object, origin at the ceiling centre point, relief hanging down (-Z).
    'acanthus_whorl' (living, dia 0.75): boss + 8 broad inner leaves + 16 outer leaves, scalloped rim.
    'floral_dish' (dining, dia 0.80): 36 pointed leaves + bosses, bead ring, dish with 3 blooms."""
    mb = MB()
    tau = 2 * math.pi
    def acanthus(length, width, relief, curl, skew=1.3):
        """Lobed leaf with a midrib groove and a raised spine, tip curling down off the plate."""
        M = mb.M.copy()
        mb.leaf(length, width, relief, mat, 12, serrate=0.34, curl=curl, base=0.35, rib=0.45, round_=0.45, skew=skew)
        mb.at(M @ Matrix.Translation((0, length * 0.04, relief * 0.40)))
        mb.leaf(length * 0.86, width * 0.13, relief * 0.75, mat, 5, curl=curl * 0.9, base=0.8, rib=1.0, round_=1.0)
        mb.at(M)

    if style == 'acanthus_whorl':                             # relief 40 mm at the boss -> ~10 mm at the rim
        mb.lathe([(0, -0.040), (0.022, -0.038), (0.040, -0.030), (0.047, -0.018), (0.047, -0.008)], mat, 16)
        mb.lathe([(0.047, -0.008), (0.335, -0.008), (0.345, -0.004), (0.345, 0)], mat, 40)
        for i in range(16):                                   # outer whorl: scalloped outline
            mb.at(_radial(tau * (i + 0.5) / 16, 0.165, -0.0075))
            acanthus(0.210, 0.150, 0.028, 0.55)
        for i in range(8):                                    # inner whorl: broad leaves over the joints
            mb.at(_radial(tau * i / 8, 0.040, -0.008))
            acanthus(0.215, 0.185, 0.046, 0.30)       # integration: leaf relief x1.7 (read as a flat disc from below)
        for i in range(8):                                    # small leaves round the boss
            mb.at(_radial(tau * (i + 0.5) / 8, 0.030, -0.012))
            mb.leaf(0.080, 0.046, 0.034, mat, 5, serrate=0.2, curl=0.2, base=0.5, round_=0.6)
    else:                                                     # floral dish: total relief ~45 mm
        mb.lathe([(0, -0.010), (0.325, -0.010), (0.332, -0.017), (0.340, -0.025), (0.350, -0.027), (0.358, -0.021),
                  (0.362, -0.012), (0.400, -0.008), (0.405, 0)], mat, 48)
        for i in range(36):                                   # dense band of broad pointed leaves, touching side by side
            mb.at(_radial(tau * i / 36, 0.364, -0.009))
            mb.leaf(0.082, 0.096, 0.027, mat, 7, curl=0.6, base=0.6, rib=0.5, round_=0.35, skew=0.8)
            mb.at(_radial(tau * i / 36, 0.368, -0.016))
            mb.leaf(0.070, 0.012, 0.018, mat, 4, curl=0.6, base=0.8, rib=1.0, round_=1.0)     # raised midrib
            mb.at(_radial(tau * (i + 0.5) / 36, 0.376, -0.012))
            mb.dome(0.0125, 0.0125, 0.020, mat, 8, 2)         # 25 mm boss between the leaf bases
        blooms = ((0.4, 0.07, 1.5), (2.3, 0.20, 1.3), (4.4, 0.19, 1.2))        # angle, radius, size
        rings = ((7, 0.074, 0.072, 0.024, 0.5, 0.000, 0.0), (6, 0.052, 0.058, 0.024, 0.8, 0.008, 0.5),
                 (5, 0.032, 0.042, 0.020, 1.0, 0.016, 0.25))  # n, length, width, relief, curl (cupping), lift, turn
        for a, r, k in blooms:                                # naturalistic blooms: three tiers of cupped petals
            C = _radial(a, r, -0.010)
            mb.at(C)
            mb.dome(0.016 * k, 0.016 * k, 0.020 * k, mat, 10, 3)
            for n, ln, wd, rl, curl, lift, off in rings:
                for j in range(n):
                    mb.at(C @ Matrix.Rotation(tau * (j + off) / n, 4, 'Z') @ Matrix.Translation((0, 0.008 * k, lift * k)))
                    mb.leaf(ln * k, wd * k, rl * k, mat, 6, curl=curl, base=0.5, rib=0.85, round_=0.4, skew=1.5)
        leaves = ((1.3, 0.16, 0.6, 0.15), (1.6, 0.27, -0.9, 0.12), (3.3, 0.12, 1.4, 0.15), (3.4, 0.27, -0.4, 0.12),
                  (5.4, 0.10, 0.3, 0.15), (5.6, 0.26, 1.0, 0.12), (0.2, 0.25, -1.2, 0.12), (2.9, 0.29, 0.8, 0.09),
                  (5.0, 0.29, -0.8, 0.09), (1.0, 0.29, 0.2, 0.09))
        for a, r, tw, ln in leaves:                                              # curling leaves between the blooms
            mb.at(_radial(a, r, -0.010) @ Matrix.Rotation(tw, 4, 'Z'))
            mb.leaf(ln, ln * 0.45, 0.024, mat, 8, serrate=0.28, curl=0.7, rib=0.45)
        for a, r in ((0.75, 0.27), (3.05, 0.21), (6.0, 0.22)):                    # fruit clusters
            for da, dr in ((0, 0), (0.09, 0.02), (-0.06, 0.03)):
                mb.at(_radial(a + da, r + dr, -0.010))
                mb.dome(0.017, 0.017, 0.016, mat, 8, 2)
    mb.at()
    ob = mb.finish(name)
    if style != 'acanthus_whorl':                             # integration: 0.89 -> 0.80 over the leaf tips (the footage
        ob.data.transform(Matrix.Diagonal((0.9, 0.9, 1.0, 1.0)))   # has the chandelier as wide as the rose: f_0705, f_0574)
    return ob


def brass_rail(points, name='rail', r=0.0095, off=0.045, spacing=0.9):
    """Gallery hanging rod: brass tube along `points` [(x, y, z)...] (the rod centre line), cup
    brackets back to the wall on the LEFT of travel at <= spacing, ball finials at both ends."""
    mb = MB()
    P = [Vector(p) for p in points]
    mb.tube(P, r, 'brass', 10)
    for a, b in zip(P, P[1:]):
        t = (b - a)
        L = t.length
        t /= L
        s = Vector((0, 0, 1)).cross(t)
        k = max(1, int(math.ceil(L / spacing)))
        for i in range(k + 1):
            q = a + t * min(max(L * i / k, 0.06), L - 0.06)
            mb.at(Matrix(((t.x, -t.z, s.x, q.x), (t.y, 0, s.y, q.y), (0, 1, 0, q.z), (0, 0, 0, 1))))
            mb.lathe([(0.0, -0.004), (0.006, -0.004), (0.006, off - 0.008), (0.016, off - 0.003), (0.016, off), (0, off)],
                     'brass', 10)
    for q in (P[0], P[-1]):
        mb.at(Matrix.Translation(q))
        mb.lathe([(0, -0.016), (0.011, -0.011), (0.016, 0), (0.011, 0.011), (0, 0.016)], 'brass', 10)
    mb.at()
    return mb.finish(name)


# --------------------------------------------------------------------------- room outline
SOLID_TYPES = {'pier', 'pilaster', 'chimney_breast', 'boxing', 'nib'}
ARCH_BY_ROOM = {'hallway': 'arch_hall', 'stairs': 'arch_hall', 'living': 'arch_living', 'kitchen': 'arch_kitchen',
                'utility': 'arch_utility', 'wc': 'arch_utility', 'vestibule': 'arch_vest_window', 'dining': 'arch_dark'}
ARCH_OVERRIDE = {('d_dining', 'hallway'): 'arch_hall_dining'}


def architrave_key(oid, room):
    """Profile key of the plain architrave round opening `oid` on the `room` side."""
    return ARCH_OVERRIDE.get((oid, room)) or ARCH_BY_ROOM.get(room, 'arch_hall')


def surround_reach(oid, sur, room):
    """(how far the surround covers the wall beyond the hole edge, True if it runs to the floor
    even under a window). Skirting / dado stop there."""
    if sur == 'plain_architrave':
        return profile_size(architrave_key(oid, room))[0], False
    return {'pediment': (0.109, False), 'dark_architrave': (0.11, True), 'dark_aedicule': (0.10, True),
            'mahogany_frame': (9.0, True), 'white_upvc_frame': (9.0, True),
            'white_architrave_two_lights': (0.10, False)}.get(sur, (0.0, False))


def _pip(x, y, poly):
    inside = False
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            inside = not inside
    return inside


def _bounds(poly):
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    return (min(xs), min(ys), max(xs), max(ys))


def _sub(ivs, a, b):
    """Subtract [a, b] from a list of intervals."""
    out = []
    for s, e in ivs:
        if b <= s or a >= e:
            out.append((s, e))
        else:
            if a > s:
                out.append((s, a))
            if b < e:
                out.append((b, e))
    return out


def room_loops(ctx, rooms, z, solids=()):
    """Outline(s) of the clear space of `rooms` (ids, unioned) at height z: room polygons minus
    walls, piers, pilasters, breasts, boxings, low soffits, plus `solids` [(x0, y0, x1, y1)...].
    -> list of loops [(x, y)...], interior on the LEFT (outer boundary counter-clockwise)."""
    rooms = tuple(rooms)
    polys = [[tuple(p) for p in ctx.rooms[r]['polygon']] for r in rooms]
    sol, voids = list(solids), []
    for f in ctx.features:
        if f.get('room') not in rooms or 'polygon' not in f:
            continue
        zz, t, rc = f.get('z'), f['type'], _bounds(f['polygon'])
        if t in SOLID_TYPES and isinstance(zz, list) and zz[0] - 1e-6 <= z <= zz[1] + 1e-6:
            sol.append(rc)
        elif t == 'recess' and isinstance(zz, list):
            (voids if zz[0] <= z <= zz[1] else sol).append(rc)
        elif t == 'soffit' and isinstance(zz, (int, float)) and z > zz:
            sol.append(rc)
    for w in ctx.walls.values():
        if w.get('virtual') or w['thickness'] <= 0:
            continue
        (ax, ay), (bx, by), h = w['a'], w['b'], w['thickness'] / 2
        hor = abs(ay - by) < 1e-6
        ivs = [tuple(sorted((ax, bx)) if hor else sorted((ay, by)))]
        for o in ctx.openings.values():
            if o['wall'] == w['id'] and o['type'] in ('arch', 'opening') and z < o.get('springing', o['sill'] + o['height']):
                c = o['center'][0 if hor else 1]
                ivs = _sub(ivs, c - o['width'] / 2, c + o['width'] / 2)
        sol += [(s, ay - h, e, ay + h) if hor else (ax - h, s, ax + h, e) for s, e in ivs]
    R = lambda v: round(v, 4)
    xs = sorted({R(p[0]) for pl in polys for p in pl} | {R(v) for r in sol + voids for v in (r[0], r[2])})
    ys = sorted({R(p[1]) for pl in polys for p in pl} | {R(v) for r in sol + voids for v in (r[1], r[3])})
    inr = lambda x, y, r: r[0] - 1e-6 < x < r[2] + 1e-6 and r[1] - 1e-6 < y < r[3] + 1e-6

    def inside(i, j):
        if not (0 <= i < len(xs) - 1 and 0 <= j < len(ys) - 1):
            return False
        x, y = (xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2
        if not any(_pip(x, y, pl) for pl in polys):
            return False
        return any(inr(x, y, r) for r in voids) or not any(inr(x, y, r) for r in sol)

    cells = {(i, j) for i in range(len(xs) - 1) for j in range(len(ys) - 1) if inside(i, j)}
    edges = {}
    for i, j in cells:
        for (ni, nj), a, b in (((i, j - 1), (i, j), (i + 1, j)), ((i + 1, j), (i + 1, j), (i + 1, j + 1)),
                               ((i, j + 1), (i + 1, j + 1), (i, j + 1)), ((i - 1, j), (i, j + 1), (i, j))):
            if (ni, nj) not in cells:
                edges.setdefault(a, []).append(b)
    loops = []
    while edges:
        a = next(iter(edges))
        loop = []
        while a in edges:
            b = edges[a].pop()
            if not edges[a]:
                del edges[a]
            loop.append((xs[a[0]], ys[a[1]]))
            a = b
        out = []                                            # drop collinear points
        n = len(loop)
        for k in range(n):
            p, q, r = loop[k - 1], loop[k], loop[(k + 1) % n]
            if abs((q[0] - p[0]) * (r[1] - q[1]) - (q[1] - p[1]) * (r[0] - q[0])) > 1e-9:
                out.append(q)
        if len(out) >= 4:
            loops.append(out)
    return loops


def _edge_keeps(ctx, rooms, A, B, z, cfg):
    """Parts [(t0, t1)...] (metres from A) of outline edge A->B that carry trim at height z."""
    hor = abs(A[1] - B[1]) < 1e-6
    ax = 0 if hor else 1                                    # axis the edge runs along
    perp = A[1 - ax]
    lo, hi = sorted((A[ax], B[ax]))
    keep = [(lo, hi)]
    for o in ctx.openings.values():                         # doors / windows + their surrounds
        w = ctx.walls[o['wall']]
        if w.get('virtual') or o['type'] in ('arch', 'opening'):
            continue
        whor = abs(w['a'][1] - w['b'][1]) < 1e-6
        if whor != hor or abs(perp - w['a'][1 - ax]) > w['thickness'] / 2 + 0.03:
            continue
        sur = next((o['surround'][r] for r in rooms if r in (o.get('surround') or {})), None)
        room = next((r for r in rooms if r in (o.get('surround') or {})), rooms[0])
        reach, to_floor = surround_reach(o['id'], sur, room)
        top = max(o['sill'] + o['height'], (o.get('transom') or {}).get('height', 0.0))
        if not ((o['sill'] - 0.02 < z < top + 0.02) or (to_floor and z < top)):
            continue
        c = o['center'][ax]
        keep = _sub(keep, c - o['width'] / 2 - reach, c + o['width'] / 2 + reach)
    for f in ctx.features:                                  # set-back frames (reveals)
        zz = f.get('z')
        if f['type'] != 'reveal' or f.get('room') not in rooms or not (zz[0] <= z <= zz[1]):
            continue
        r = _bounds(f['polygon'])
        if r[1 - ax] - 0.02 <= perp <= r[3 - ax] + 0.02:
            keep = _sub(keep, r[ax], r[2 + ax])
    for bx in cfg.get('skip', ()):
        if bx[1 - ax] <= perp <= bx[3 - ax] and min(hi, bx[2 + ax]) - max(lo, bx[ax]) > 0.02:
            keep = _sub(keep, bx[ax], bx[2 + ax])
    if cfg.get('only'):
        only = []
        for bx in cfg['only']:
            if bx[1 - ax] <= perp <= bx[3 - ax]:
                only += [(max(s, bx[ax]), min(e, bx[2 + ax])) for s, e in keep if min(e, bx[2 + ax]) - max(s, bx[ax]) > 0.012]
        keep = sorted(only)
    L = hi - lo
    fwd = B[ax] > A[ax]
    out = [((s - lo) if fwd else (hi - e), (e - lo) if fwd else (hi - s)) for s, e in keep if e - s > 0.012]
    return sorted(out), L


def trim_runs(ctx, rooms, z, cfg=None):
    """Mitre-ready runs of trim at height z round `rooms`: the room outline minus door / window
    surrounds, reveals and the cfg 'skip' / 'only' boxes. -> [([(x, y)...], closed)...]"""
    cfg = cfg or {}
    runs = []
    for loop in room_loops(ctx, rooms, z, cfg.get('solids', ())):
        n = len(loop)
        cur, first_from_vertex, loop_runs, at_vertex = None, False, [], False
        for i in range(n):
            A, B = Vector(loop[i]), Vector(loop[(i + 1) % n])
            keeps, L = _edge_keeps(ctx, rooms, loop[i], loop[(i + 1) % n], z, cfg)
            d = (B - A) / L
            if not keeps:
                at_vertex = False
            for t0, t1 in keeps:
                if cur is not None and at_vertex and t0 < 1e-6:
                    cur.append(A + d * t1)                  # carry on round the corner (mitre)
                else:
                    if cur is not None:
                        loop_runs.append(cur)
                    elif i == 0 and t0 < 1e-6:
                        first_from_vertex = True
                    cur = [A + d * t0, A + d * t1]
                at_vertex = t1 > L - 1e-6
        if cur:
            loop_runs.append(cur)
        if loop_runs and at_vertex and first_from_vertex:           # wraps through vertex 0
            if len(loop_runs) == 1:
                runs.append(([tuple(p) for p in loop_runs[0][:-1]], True))
                continue
            loop_runs[0] = loop_runs.pop()[:-1] + loop_runs[0]
        runs += [([tuple(p) for p in r], False) for r in loop_runs]
    return runs


# --------------------------------------------------------------------------- per-room trim
# kind -> dict(profile, [top] (dado: top of rail above floor), [mat], [solids], [skip], [only]).
# solids / skip / only are world-plan boxes (x0, y0, x1, y1): `solids` are extra masses for that
# kind's outline; trim is dropped where an edge runs through a `skip` box and, when `only` is
# given, kept only inside those boxes.
TRIM = {
    'vestibule': dict(skirting=dict(profile='sk_vest'), dado=dict(profile='dado_hall', top=0.965)),
    'hallway': dict(
        rooms=('hallway', 'stairs'),
        skirting=dict(profile='sk_hall', solids=[(0.15, 5.33, 0.99, 7.58), (0.10, 7.58, 0.20, 7.68)],
                      skip=[(0.98, 4.84, 1.00, 5.34), (0.14, 5.32, 1.00, 5.34)]),
        dado=dict(profile='dado_hall', top=0.965, solids=[(0.15, 5.33, 0.99, 7.58), (0.10, 7.58, 0.20, 7.68)],
                  skip=[(0.98, 4.84, 1.00, 5.34), (0.14, 5.32, 1.00, 5.34), (0.09, 5.32, 0.16, 7.69),
                        (0.09, 7.67, 1.00, 7.69)]),
        cornice=dict(profile='cornice_hall', solids=[(0.15, 7.58, 0.99, 8.73), (0.10, 7.58, 0.20, 7.68)],
                     skip=[(0.98, 4.84, 1.00, 7.59), (0.09, 7.57, 1.00, 7.59), (-0.70, 8.72, 1.00, 8.74),
                           (-0.70, 9.02, 1.00, 9.04), (-0.70, 1.82, 0.70, 1.84)])),
    'living': dict(skirting=dict(profile='sk_living'), cornice=dict(profile='cornice_living')),
    'kitchen': dict(skirting=dict(profile='sk_kitchen', only=[(4.29, 7.82, 4.31, 8.74), (1.24, 8.72, 3.25, 8.74),
                                                               (1.24, 7.54, 1.26, 7.76)]),
                    cornice=dict(profile='cornice_kitchen')),
    'utility': dict(skirting=dict(profile='sk_utility', only=[(0.59, 10.25, 2.53, 10.27)]),
                    cornice=dict(profile='cornice_utility')),
    'wc': dict(cornice=dict(profile='cornice_wc')),
    'dining': dict(skirting=dict(profile='sk_dining', mat='dark_stain'), dado=dict(profile='dado_dining', top=1.05),
                   cornice=dict(profile='cornice_dining', solids=[(-0.65, 16.74, 3.10, 16.86)])),
}
ROSE_AT = {'living': (2.55, 2.86), 'dining': (1.225, 14.61)}       # world xy of the rose centres


def _extras_vestibule(ctx):
    obs = []
    mb = MB()
    for f in ctx.features:                                  # impost bands round the piers
        if f['type'] == 'pier' and f.get('room') == 'vestibule':
            x0, y0, x1, y1 = _bounds(f['polygon'])
            cfg = dict(only=[(x0 - 0.006, y0 - 0.006, x1 + 0.006, y1 + 0.006)])
            zb = f['z'][1] - 0.230
            for run, closed in trim_runs(ctx, ('vestibule',), zb + 0.05, cfg):
                mb.sweep(PROFILES['impost_vest'], [(x, y, zb) for x, y in run], 'plaster_white', closed)
    v = next((f for f in ctx.features if f['type'] == 'arch_vault' and f.get('room') == 'vestibule'), None)
    if v:                                                   # archivolt band on both faces of the vault
        x0, y0, x1, y1 = _bounds(v['polygon'])
        arc = arch_points('basket', x0, x1, v['springing'], v['crown'], 24)
        mb.sweep(PROFILES['archivolt'], [(x, y0, z) for x, z in arc], 'plaster_white', up=(0, -1, 0))
        mb.sweep(PROFILES['archivolt'], [(x, y1, z) for x, z in reversed(arc)], 'plaster_white', up=(0, 1, 0))
    if mb.bm.faces:
        obs.append(ctx.add(mb.finish('vestibule.arch_mouldings'), 'vestibule', 'trim'))
    return obs


def _extras_hallway(ctx):
    mb = MB()
    for f in ctx.features:
        if f['type'] == 'arch' and f.get('room') == 'hallway':
            sz = f['corbelSize']
            for c in f['corbels']:
                y = Vector((c['projects'][0], c['projects'][1], 0))
                x = y.cross(Vector((0, 0, 1)))
                o = Vector((c['at'][0], c['at'][1], sz['z'][1]))
                mb.at(Matrix(((x.x, y.x, 0, o.x), (x.y, y.y, 0, o.y), (0, 0, 1, o.z), (0, 0, 0, 1))))
                arch_corbel(mb, sz['length'], sz['projection'], sz['height'])
    mb.at()
    return [ctx.add(mb.finish('hallway.arch_corbels'), 'hallway', 'trim')] if mb.bm.faces else []


def _extras_living(ctx):
    cz = ctx.ceil_z('living')
    x0, y0, x1, y1 = _bounds(ctx.room_poly('living'))
    rose = ceiling_rose(ROSES['living']['style'], 'living.rose')
    rose.location = (*ROSE_AT['living'], cz)
    zr = cz - 0.25                                          # 2.70: hangs 100 mm below the cornice (f_0133, f_0785)
    rail = brass_rail([(x0 + 0.95, y1 - 0.045, zr), (x1 - 0.045, y1 - 0.045, zr),
                       (x1 - 0.045, 1.44, zr)], 'living.picture_rail')
    return [ctx.add(rose, 'living', 'trim'), ctx.add(rail, 'living', 'trim')]


def _extras_dining(ctx):
    cz = ctx.ceil_z('dining')
    rose = ceiling_rose(ROSES['dining']['style'], 'dining.rose')
    rose.location = (*ROSE_AT['dining'], cz)
    x0, y0, x1, y1 = _bounds(ctx.room_poly('dining'))
    mb = MB()                                               # white boxed pelmet over the N screen
    mb.box((x0, y1 - 0.12, 2.50), (x1, y1 + 0.001, cz), 'plaster_white')
    return [ctx.add(rose, 'dining', 'trim'), ctx.add(mb.finish('dining.pelmet'), 'dining', 'trim')]


# brushed-steel straight-edge trim along the top of the tile dado: z = tile top, optional `only` boxes
TILE_TRIM = {'wc': dict(z=1.20), 'utility': dict(z=1.39, only=[(0.59, 11.17, 0.61, 12.23)])}


def _extras_tile_trim(ctx, room):
    c = TILE_TRIM[room]
    mb = MB()
    prof = [(0, 0), (0.004, 0), (0.004, 0.010), (0, 0.010)]            # 10 mm face, 4 mm proud of the plaster
    for run, closed in trim_runs(ctx, (room,), c['z'] - 0.005, c):
        mb.sweep(prof, [(x, y, c['z'] - 0.010) for x, y in run], 'steel_brushed', closed)
    return [ctx.add(mb.finish(f'{room}.tile_trim'), room, 'trim')] if mb.bm.faces else []


EXTRAS = {'vestibule': _extras_vestibule, 'hallway': _extras_hallway, 'living': _extras_living,
          'dining': _extras_dining, 'wc': lambda ctx: _extras_tile_trim(ctx, 'wc'),
          'utility': lambda ctx: _extras_tile_trim(ctx, 'utility')}


def install_room_trim(ctx, room_id):
    """Fit skirting, dado rail and cornice round a room (TRIM table) plus the room's fixed plaster
    ornaments (EXTRAS: vestibule imposts + archivolt, hall arch corbels, living rose + brass
    picture rail, dining rose + pelmet). Objects are tagged kind='trim'. -> [objects]"""
    cfg = TRIM.get(room_id)
    obs = []
    if cfg:
        rooms = cfg.get('rooms', (room_id,))
        fz, cz = ctx.floor_z(room_id), ctx.ceil_z(room_id)
        for kind in ('skirting', 'dado', 'cornice'):
            c = cfg.get(kind)
            if not c:
                continue
            if kind == 'skirting':
                zb, zq, m = fz, fz + 0.05, 'joinery_white'
            elif kind == 'dado':
                zb = fz + c['top'] - profile_size(c['profile'])[1]
                zq, m = zb + 0.02, 'joinery_white'
            else:
                zb, zq, m = cz, cz - 0.03, 'plaster_white'
            m = c.get('mat', m)
            mb = MB()
            for run, closed in trim_runs(ctx, rooms, zq, c):
                path = [(x, y, zb) for x, y in run]
                if kind == 'cornice':
                    cornice(mb, c['profile'], path, closed, m)
                else:
                    mb.sweep(PROFILES[c['profile']], path, m, closed)
            if mb.bm.faces:
                obs.append(ctx.add(mb.finish(f'{room_id}.{kind}'), room_id, 'trim'))
    if room_id in EXTRAS:
        obs += EXTRAS[room_id](ctx)
    return obs

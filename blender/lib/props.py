"""props.py - shared parametric small parts for every room module (owner: props).

Full signature table: blender/lib/README.md, section "props".  Conventions:
  * every public prop returns ONE unlinked bpy Object (scale 1) - pass it to ctx.add().  Props marked
    [H] in the README also carry parented children (lights / linked sub-parts): link them with
    `for o in props.family(root): ctx.add(o, room, kind)`.
  * identical arguments -> the SAME mesh datablock (linked duplicates for free).  Keep `seed`s equal
    when you want instancing, vary them when you want variety.
  * origins: floor props = centre of the footprint on the floor; wall props = centre of the back face,
    back on local y=0, front faces local -Y, +X to the viewer's right; ceiling props = contact point,
    hanging -Z.  `place(obj, loc, facing=(nx, ny))` aims local -Y along a wall normal.
  * materials: any `mat`/colour argument accepts a lib.materials key, a '#rrggbb' paint, a props
    extra key (see _PAL) or a bpy Material.  Unknown keys raise KeyError.
Run the contact sheet:  blender -b --factory-startup --python blender/lib/props.py -- --out build/props
"""
import bpy, bmesh, math, random, functools, inspect, os, sys, contextlib
from math import sin, cos, pi, tau, radians, sqrt, atan2, hypot
from mathutils import Vector, Matrix

if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from . import materials as _ML
except ImportError:                      # run directly as the contact-sheet script
    import materials as _ML

# ----------------------------------------------------------------------------- materials
# Props-only constant colours: key -> (hex, roughness, metallic). Everything else is a lib.materials key.
_PAL = {
    # golds: olive bases - the first orange-leaning ones (#9C8440 / #8C7446) rendered copper next to coloured walls
    'gold_antique': ('#928A52', .42, 1), 'gold_bronze': ('#8E8458', .45, 1),
    'olive_bronze': ('#7C7048', .45, .8), 'silver_green': ('#B9B59F', .45, .6),
    'frame_dark': ('#2E261C', .45, 0), 'walnut': ('#4A3524', .45, 0),
    'plastic_dark': ('#151515', .5, 0), 'ivory': ('#EFE6CF', .7, 0),
    'cream_mount': ('#ECE7DA', .9, 0), 'tassel_gold': ('#B5A174', .7, 0),
    'soil': ('#2B2019', .95, 0), 'bark': ('#5A4632', .85, 0),
    'leaf_green': ('#2F5A2A', .35, 0), 'leaf_mid': ('#3F6B2E', .4, 0), 'leaf_lime': ('#A9C24A', .4, 0),
    'leaf_grey': ('#8A9A86', .7, 0), 'fruit_orange': ('#E08A1E', .45, 0), 'terracotta': ('#B0603C', .8, 0),
    'marble_green': ('#3E5A46', .15, 0), 'dial_cream': ('#EFE8D2', .4, 0),
    'skin_ref': ('#9AA3AD', .8, 0), 'cone_grey': ('#3A3A3C', .6, 0),
}

# props shorthand -> lib.materials key
_ALIAS = {'antique_brass': 'brass_antique', 'gold_bright': 'gilt_bright', 'champagne': 'gold_champagne',
          'silver': 'silver_satin', 'rope_cream': 'linen_cream'}


def _lin(h):
    return _ML.hex_lin(h)[:3]


def _principled(m):
    return next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')


def mat(x):
    """Resolve a material spec: bpy Material | '#rrggbb' paint | lib.materials key | props extra key (_PAL).
    Unknown keys raise KeyError."""
    if isinstance(x, bpy.types.Material):
        return x
    if x.startswith('#'):
        return _ML.paint(x)
    x = _ALIAS.get(x, x)
    if x in _PAL:
        return _ML.solid(x, *_PAL[x])
    return _ML.mat(x)


def two_sided(m):
    """Double-sided variant (lib.materials culls back faces of opaque materials in the GLB): returns m itself
    when it is already double-sided, else a cached copy '<name>_2s' with use_backface_culling off.
    Used for single-surface cloth, leaves, shades."""
    m = mat(m)
    if not m.use_backface_culling:
        return m
    c = bpy.data.materials.get(m.name + '_2s')
    if c is None:
        c = m.copy(); c.name = m.name + '_2s'; c.use_backface_culling = False
    return c


def _emit(name, base, emit, strength, rough=.5):
    m = _ML.solid(name, base, rough)
    p = _principled(m)
    p.inputs['Emission Color'].default_value = (*_lin(emit), 1); p.inputs['Emission Strength'].default_value = strength
    return m


def emissive(hx='#FFE2B0', strength=8.0):
    """Principled material with constant emission (glTF-safe), cached by colour + strength."""
    return _emit('emit_%s_%g' % (hx.lstrip('#').lower(), strength), hx, hx, strength)


def image_mat(path, rough=.6):
    """Image-textured material filling a 0..1 UV square once (lib.materials.image_mat)."""
    return _ML.image_mat('img_' + os.path.splitext(os.path.basename(path))[0], path, None, roughness=rough)


FINISH = {'brass': 'brass', 'antique_brass': 'antique_brass', 'black': 'black_matt', 'steel': 'steel_brushed',
          'chrome': 'chrome', 'white': 'plastic_white', 'gilt': 'gilt', 'bronze': 'bronze_dark'}


def _fin(f):
    return mat(FINISH.get(f, f) if isinstance(f, str) else f)


# ----------------------------------------------------------------------------- geometry core
class G:
    """Raw geometry: verts, faces (index tuples), optional per-vertex uv or per-face-corner uv."""
    __slots__ = ('v', 'f', 'vuv', 'fuv', 'soft')

    def __init__(s, v, f, vuv=None, fuv=None, soft=None):
        s.v, s.f, s.vuv, s.fuv, s.soft = v, f, vuv, fuv, soft   # soft = own sharp-edge angle (deg) when smooth


def Tr(x=0, y=0, z=0):
    return Matrix.Translation((x, y, z))


def Rot(axis, deg):
    return Matrix.Rotation(radians(deg), 4, axis)


def Sc(x, y=None, z=None):
    return Matrix.Diagonal((x, x if y is None else y, x if z is None else z, 1))


class _B:
    """bmesh accumulator: primitives are appended with a material slot, smooth flag and UVs.
    Faces without explicit UVs get a 1 m box projection in mesh()."""

    def __init__(s):
        s.bm = bmesh.new(); s.uvl = s.bm.loops.layers.uv.new('UVMap')
        s.mats = []; s.auto = set(); s.kids = []; s.T = Matrix.Identity(4); s.sharp = {}; s.bulbs = []

    @contextlib.contextmanager
    def at(s, T):
        old = s.T; s.T = old @ T
        try:
            yield s
        finally:
            s.T = old

    def slot(s, m):
        m = mat(m)
        if m not in s.mats:
            s.mats.append(m)
        return s.mats.index(m)

    def add(s, g, m, smooth=False, closed=False, T=None):
        """m: one material spec, or a list aligned with g.f.  smooth: False | True (edges sharper than 50 deg
        - or g.soft - stay crisp) | number (own threshold in deg).  closed=True -> recalc normals outward."""
        M = s.T @ T if T is not None else s.T
        flip = M.determinant() < 0
        bv = [s.bm.verts.new(M @ Vector(v)) for v in g.v]
        mi = [s.slot(x) for x in m] if isinstance(m, list) else [s.slot(m)] * len(g.f)
        out = []
        for k, f in enumerate(g.f):
            try:
                face = s.bm.faces.new([bv[i] for i in (reversed(f) if flip else f)])
            except ValueError:
                continue
            face.material_index = mi[k]; face.smooth = bool(smooth)
            if smooth:
                s.sharp[face] = radians(g.soft or (50 if smooth is True else smooth))
            if g.fuv:
                for l, uv in zip(face.loops, reversed(g.fuv[k]) if flip else g.fuv[k]):
                    l[s.uvl].uv = uv
            elif g.vuv:
                for l, i in zip(face.loops, reversed(f) if flip else f):
                    l[s.uvl].uv = g.vuv[i]
            else:
                s.auto.add(face)
            out.append(face)
        if closed:
            bmesh.ops.recalc_face_normals(s.bm, faces=out)
        return out

    def kid(s, factory, T=None):
        """Register a child object factory (called once per instance) at local matrix T."""
        s.kids.append((factory, s.T @ T if T is not None else s.T.copy()))

    def mesh(s, name):
        bm = s.bm; bm.normal_update()
        for f in s.auto:
            if not f.is_valid:
                continue
            n = f.normal; a = max(range(3), key=lambda i: abs(n[i]))
            for l in f.loops:
                c = l.vert.co
                l[s.uvl].uv = (c.y, c.z) if a == 0 else (c.x, c.z) if a == 1 else (c.x, c.y)
        for f in bm.faces:                       # metres -> texture repeats (lib.materials 'size_m'; 'fit' = 0..1 image)
            m = s.mats[f.material_index] if s.mats else None
            sz = None if (m is None or m.get('fit')) else m.get('size_m')
            if sz and (sz[0] != 1 or sz[1] != 1):
                for l in f.loops:
                    uv = l[s.uvl].uv; l[s.uvl].uv = (uv.x / sz[0], uv.y / sz[1])
        for e in bm.edges:
            lf = e.link_faces
            if len(lf) == 2 and lf[0].smooth and lf[1].smooth and e.calc_face_angle(0) > s.sharp.get(lf[0], .87):
                e.smooth = False
        me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
        for m in s.mats:
            me.materials.append(m)
        if s.bulbs:
            me['bulbs'] = [c for q in s.bulbs for c in q]
        return me


_MESH = {}


def _prop(fn):
    """Public prop = cached mesh builder.  fn(b, *args, **kw) fills the _B; wrapper returns a new
    Object sharing the cached mesh (plus fresh children registered via b.kid)."""
    sig = inspect.signature(fn)

    @functools.wraps(fn)
    def wrap(*a, name=None, **k):
        ba = sig.bind(None, *a, **k); ba.apply_defaults()           # same call, however spelled -> same key
        key = (fn.__name__, repr(list(ba.arguments.items())[1:]))
        hit = _MESH.get(key)
        try:
            hit and hit[0].name
        except ReferenceError:
            hit = None
        if hit is None:
            b = _B(); fn(b, *a, **k)
            hit = _MESH[key] = (b.mesh(fn.__name__), b.kids)
        ob = bpy.data.objects.new(name or fn.__name__, hit[0])
        for factory, T in hit[1]:
            c = factory(); c.parent = ob; c.matrix_basis = T
        return ob
    return wrap


def family(obj):
    """obj plus all parented descendants (works on unlinked objects)."""
    return [obj] + list(obj.children_recursive)


def tris(obj, unique=False):
    """Triangle count of obj + children.  unique=True counts each shared mesh once."""
    seen, n = set(), 0
    for o in family(obj):
        if o.type != 'MESH' or (unique and o.data.name in seen):
            continue
        seen.add(o.data.name); n += sum(len(p.vertices) - 2 for p in o.data.polygons)
    return n


def _world(o):
    return o.matrix_basis.copy() if o.parent is None else _world(o.parent) @ o.matrix_parent_inverse @ o.matrix_basis


def bulb_points(obj):
    """World-space centres of every candle lamp in obj + children (chandelier, sconce, candle_bulb,
    chandelier_arm) - feed them to lighting.bulb().  Valid as soon as location/rotation are set."""
    out = []
    for o in family(obj):
        if o.type == 'MESH' and 'bulbs' in o.data:
            b = list(o.data['bulbs']); M = _world(o)
            out += [M @ Vector(b[i:i + 3]) for i in range(0, len(b), 3)]
    return out


def place(obj, loc, facing=None, rot_z=None):
    """Set location; facing=(nx, ny) aims the prop's front (local -Y) along that wall normal."""
    obj.location = loc
    if facing is not None:
        obj.rotation_euler = (0, 0, atan2(facing[0], -facing[1]))
    elif rot_z is not None:
        obj.rotation_euler = (0, 0, radians(rot_z))
    return obj


def _light(kind, watts, kelvin=2700, radius=.03, spot_deg=110):
    nm = 'L_%s_%g_%d_%g' % (kind, watts, kelvin, radius)
    l = bpy.data.lights.get(nm)
    if l is None:
        l = bpy.data.lights.new(nm, kind); l.energy = watts; l.shadow_soft_size = radius
        try:
            l.use_temperature = True; l.temperature = kelvin
        except AttributeError:
            pass
        if kind == 'SPOT':
            l.spot_size = radians(spot_deg); l.spot_blend = .6
    return bpy.data.objects.new(nm, l)

# ----------------------------------------------------------------------------- primitives (-> G)
_CORN = [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]


def _box(lo, hi, bev=0.0):
    """Cuboid lo..hi; bev > 0 = single flat chamfer on all 12 edges (44 tris)."""
    c = [(a + b) / 2 for a, b in zip(lo, hi)]; h = [abs(b - a) / 2 for a, b in zip(lo, hi)]
    if bev <= 0:
        return G([tuple(c[i] + s[i] * h[i] for i in range(3)) for s in _CORN],
                 [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
    b = min(bev, .49 * min(h))
    vs = [tuple(c[i] + s[i] * (h[i] - (0 if i == a else b)) for i in range(3)) for s in _CORN for a in range(3)]
    fs = []
    for a in range(3):
        p, q = [i for i in range(3) if i != a]
        for sg in (-1, 1):
            ks = sorted((k for k in range(8) if _CORN[k][a] == sg), key=lambda k: atan2(_CORN[k][q], _CORN[k][p]))
            fs.append(tuple(k * 3 + a for k in ks))
    for k in range(8):
        for l in range(k + 1, 8):
            d = [i for i in range(3) if _CORN[k][i] != _CORN[l][i]]
            if len(d) == 1:
                p, q = [i for i in range(3) if i != d[0]]
                fs.append((k * 3 + p, l * 3 + p, l * 3 + q, k * 3 + q))
        fs.append((k * 3, k * 3 + 1, k * 3 + 2))
    return G(vs, fs)


def _box_round(lo, hi, r, seg=2):
    """Cuboid with a rounded multi-segment bevel (via bmesh.ops.bevel)."""
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = [(lo[i] + hi[i]) / 2 + v.co[i] * (hi[i] - lo[i]) for i in range(3)]
    r = min(r, .49 * min(abs(hi[i] - lo[i]) for i in range(3)))
    bmesh.ops.bevel(bm, geom=bm.edges[:], offset=r, offset_type='OFFSET', segments=seg, profile=.5, affect='EDGES')
    bm.verts.index_update()
    g = G([v.co.copy() for v in bm.verts], [[v.index for v in f.verts] for f in bm.faces]); bm.free()
    return g


def _lathe(prof, seg=12, rmod=None, arc=None):
    """Revolve [(r, z)] about Z.  Profile runs CCW in the r-z plane (bottom -> out -> up -> top) for
    outward normals.  r = 0 points collapse to a pole.  rmod(theta, j) scales radius of profile point j."""
    a0, a1 = arc or (0, tau)
    vs, rings = [], []
    for j, (r, z) in enumerate(prof):
        if r < 1e-6:
            vs.append((0, 0, z)); rings.append([len(vs) - 1] * (seg + 1)); continue
        ring = []
        for i in range(seg if arc is None else seg + 1):
            t = a0 + (a1 - a0) * i / seg; rr = r * (rmod(t, j) if rmod else 1)
            vs.append((rr * cos(t), rr * sin(t), z)); ring.append(len(vs) - 1)
        if arc is None:
            ring.append(ring[0])
        rings.append(ring)
    L = [0.0]
    for j in range(1, len(prof)):
        L.append(L[-1] + hypot(prof[j][0] - prof[j - 1][0], prof[j][1] - prof[j - 1][1]))
    U = (a1 - a0) * max(r for r, _ in prof)
    fs, fuv = [], []
    for j in range(len(prof) - 1):
        A, Bq = rings[j], rings[j + 1]
        for i in range(seg):
            q = [A[i], A[i + 1], Bq[i + 1], Bq[i]]
            uv = [(U * i / seg, L[j]), (U * (i + 1) / seg, L[j]), (U * (i + 1) / seg, L[j + 1]), (U * i / seg, L[j + 1])]
            if q[0] == q[1]:
                q, uv = q[1:], uv[1:]
            elif q[2] == q[3]:
                q, uv = q[:3], uv[:3]
            if len(set(q)) == len(q):
                fs.append(q); fuv.append(uv)
    return G(vs, fs, fuv=fuv)


def _sphere(r, seg=8, rings=5, squash=1.0):
    g = _lathe([(r * sin(pi * k / rings), -r * squash * cos(pi * k / rings)) for k in range(rings + 1)], seg)
    g.soft = 100
    return g


def _frames(pts, up=(0, 0, 1), loop=False):
    """Parallel-transport frames along a polyline -> [(centre, N, B)] with N x B = tangent."""
    P = [Vector(p) for p in pts]; n = len(P); out = []; N = None; Tp = None
    for k in range(n):
        a = P[k - 1] if (k > 0 or loop) else P[k]
        b = P[(k + 1) % n] if (k < n - 1 or loop) else P[k]
        T = (b - a).normalized()
        if N is None:
            N = Vector(up) - T * T.dot(Vector(up))
            if N.length < 1e-4:
                N = Vector((1, 0, 0)) - T * T.x
        else:
            N = Tp.rotation_difference(T) @ N; N = N - T * T.dot(N)
        N.normalize(); out.append((P[k], N.copy(), T.cross(N))); Tp = T
    return out


def _sweep(sec, frames, scale=None, cap=True, loop=False):
    """Sweep a 2D section [(a, b)] (CCW) along frames; scale = per-frame float or (sa, sb)."""
    m = len(sec); K = len(frames); vs = []
    for k, (c, N, Bv) in enumerate(frames):
        s = scale[k] if scale else 1.0
        sa, sb = s if isinstance(s, tuple) else (s, s)
        vs += [c + N * (a * sa) + Bv * (b_ * sb) for a, b_ in sec]
    fs = []
    for k in range(K if loop else K - 1):
        k2 = (k + 1) % K
        for i in range(m):
            i2 = (i + 1) % m
            fs.append((k * m + i, k * m + i2, k2 * m + i2, k2 * m + i))
    if cap and not loop:
        fs.append(tuple(range(m - 1, -1, -1))); fs.append(tuple((K - 1) * m + i for i in range(m)))
    return G(vs, fs)


def _circle(n, r=1.0, a0=0.0):
    return [(r * cos(a0 + tau * i / n), r * sin(a0 + tau * i / n)) for i in range(n)]


def _tube(pts, r, seg=6, cap=True, loop=False, up=(0, 0, 1)):
    """Round tube along a polyline; r = radius or per-point list."""
    g = _sweep(_circle(seg), _frames(pts, up, loop), list(r) if isinstance(r, (list, tuple)) else [r] * len(pts), cap, loop)
    g.soft = 75 if seg >= 6 else 100          # round even when low-poly; caps of 6+ sided tubes stay crisp
    return g


def _grid(fn, nu, nv, uvfn=None, flip=False):
    """Surface fn(u, v) -> xyz over [0,1]^2; normal = du x dv (flip reverses)."""
    vs = [fn(i / nu, j / nv) for j in range(nv + 1) for i in range(nu + 1)]
    uv = [uvfn(i / nu, j / nv) for j in range(nv + 1) for i in range(nu + 1)] if uvfn else None
    w = nu + 1
    fs = [(j * w + i, j * w + i + 1, (j + 1) * w + i + 1, (j + 1) * w + i) for j in range(nv) for i in range(nu)]
    if flip:
        fs = [f[::-1] for f in fs]
    return G(vs, fs, vuv=uv)


def _inset(poly, d):
    """Offset a CCW 2D polygon inward by d (mitred)."""
    out = []; n = len(poly)
    for i in range(n):
        p, v, q = Vector(poly[i - 1]), Vector(poly[i]), Vector(poly[(i + 1) % n])
        e1, e2 = (v - p).normalized(), (q - v).normalized()
        n1, n2 = Vector((-e1.y, e1.x)), Vector((-e2.y, e2.x))
        out.append(tuple(v + (n1 + n2) * (d / max(.3, 1 + n1.dot(n2)))))
    return out


def _prism(poly, y0, y1, ch=0.0):
    """Extrude an x-z outline (CCW seen from the front, i.e. looking along +Y) from front y0 to back y1.
    ch = chamfer of the front edge.  Use with closed=True."""
    n = len(poly)
    rings = [(_inset(poly, ch), y0), (poly, y0 + ch), (poly, y1)] if ch else [(poly, y0), (poly, y1)]
    vs = [(x, y, z) for pl, y in rings for x, z in pl]
    fs = [tuple(range(n))]
    for k in range(len(rings) - 1):
        fs += [(k * n + (i + 1) % n, k * n + i, (k + 1) * n + i, (k + 1) * n + (i + 1) % n) for i in range(n)]
    fs.append(tuple((len(rings) - 1) * n + i for i in range(n - 1, -1, -1)))
    return G(vs, fs)


def _rrect(w, h, r, k=3, cx=0.0, cz=0.0):
    """Rounded rectangle outline (CCW), k segments per corner."""
    if r <= 0:
        return [(cx - w / 2, cz - h / 2), (cx + w / 2, cz - h / 2), (cx + w / 2, cz + h / 2), (cx - w / 2, cz + h / 2)]
    out = []
    for q, (sx, sz) in enumerate(((1, -1), (1, 1), (-1, 1), (-1, -1))):
        for i in range(k + 1):
            a = -pi / 2 + q * pi / 2 + (pi / 2) * i / k
            out.append((cx + sx * (w / 2 - r) + r * cos(a), cz + sz * (h / 2 - r) + r * sin(a)))
    return out


def _lerp_tab(tab, t):
    """Piecewise cosine interpolation of [(t, v1, v2, ...)]."""
    for (t0, *a), (t1, *b) in zip(tab, tab[1:]):
        if t <= t1:
            k = (1 - cos(pi * max(0, min(1, (t - t0) / (t1 - t0))))) / 2
            return [x + (y - x) * k for x, y in zip(a, b)]
    return list(tab[-1][1:])


def _bez(p0, p1, p2, p3, n):
    P = [Vector(p) for p in (p0, p1, p2, p3)]
    return [P[0] * (1 - t) ** 3 + P[1] * 3 * t * (1 - t) ** 2 + P[2] * 3 * t * t * (1 - t) + P[3] * t ** 3
            for t in (i / n for i in range(n + 1))]


# ----------------------------------------------------------------------------- generic parts
@_prop
def lathe(b, profile, segments=16, mat='brass', smooth=True):
    """Revolve [(r, z), ...] (metres, bottom -> top) about Z.  Origin = axis at z=0."""
    b.add(_lathe(list(profile), segments), mat, smooth)


@_prop
def box(b, w, d, h, mat='white_gloss'):
    """Plain cuboid, origin bottom centre."""
    b.add(_box((-w / 2, -d / 2, 0), (w / 2, d / 2, h)), mat)


@_prop
def bevel_box(b, w, d, h, mat='white_gloss', bevel=.003, segments=1):
    """Cuboid with bevelled edges (1 segment = flat chamfer, 44 tris), origin bottom centre."""
    lo, hi = (-w / 2, -d / 2, 0), (w / 2, d / 2, h)
    b.add(_box(lo, hi, bevel) if segments <= 1 else _box_round(lo, hi, bevel, segments), mat, closed=True)


# (t, r): t = 0..1 bottom -> top of the turned part, r relative to half the stock width
TURNINGS = {
    'baluster': [(0, .62), (.03, .92), (.06, .92), (.08, .6), (.11, .55), (.16, .78), (.24, .98), (.32, .95), (.45, .7),
                 (.62, .48), (.76, .4), (.8, .4), (.82, .66), (.85, .66), (.87, .42), (.91, .5), (.94, .8), (.97, .8), (1, .6)],
    'spindle': [(0, .9), (.04, .9), (.06, .6), (.12, .72), (.25, .94), (.36, .8), (.5, .6), (.52, .82), (.54, .6),
                (.57, .6), (.59, .82), (.61, .6), (.8, .56), (.94, .56), (.96, .9), (1, .9)],
    'bobbin': [(0, .7), (.04, .95), (.14, 1), (.3, .95), (.34, .7), (.38, .95), (.5, 1), (.62, .95), (.66, .7), (.7, .95),
               (.82, 1), (.96, .95), (1, .75)],
    'bun': [(0, .55), (.15, .9), (.4, 1), (.7, .92), (.9, .65), (1, .5)],
    'cup_cover': [(0, .8), (.03, .8), (.05, .55), (.09, .55), (.11, .8), (.13, .8), (.16, .7), (.22, 1.05), (.32, 1.42),
                  (.42, 1.58), (.47, 1.6), (.49, 1.72), (.53, 1.72), (.55, 1.6), (.6, 1.6), (.7, 1.5), (.8, 1.22),
                  (.87, .85), (.9, .62), (.93, .62), (.95, .82), (.98, .82), (1, .6)],
    'vase': [(0, .85), (.04, 1), (.07, 1), (.1, .7), (.16, .8), (.3, 1), (.42, .92), (.6, .68), (.75, .58), (.78, .85),
             (.84, .85), (.87, .62), (.9, .75), (.96, .75), (1, .6)],
    'column': [(0, 1), (.04, 1), (.06, .8), (.09, .86), (.5, .8), (.91, .72), (.94, .86), (.97, .86), (1, .75)],
}


def turned_profile(style, height, width, z0=0.0):
    """[(r, z)] lathe profile for a TURNINGS style scaled to height x width (dia of the square stock)."""
    return [(r * width / 2, z0 + t * height) for t, r in TURNINGS[style]]


def _cabriole(b, m, w, z0, z1, out, foot):
    o = Vector((out[0], out[1], 0)).normalized(); rb = .42 * w; claw = foot == 'claw'
    #        s    offset  half-size  (units of w); s = 0 foot .. 1 top of the leg
    tab = [(0, .2, .22), (.1, .06, .21), (.3, -.1, .24), (.5, -.08, .3), (.7, .1, .39), (.84, .3, .48), (.94, .26, .5), (1, 0, .5)]
    za = z0 + (rb if claw else .12 * w); n = 14
    sec = [(1, .45), (.45, 1), (-.45, 1), (-1, .45), (-1, -.45), (-.45, -1), (.45, -1), (1, -.45)]
    fr, sc = [], []
    for i in range(n + 1):
        off, half = _lerp_tab(tab, i / n)
        fr.append((o * (off * w) + Vector((0, 0, za + (z1 - za) * i / n)), Vector((1, 0, 0)), Vector((0, 1, 0))))
        sc.append(half * w)
    b.add(_sweep(sec, fr, sc), m, True, closed=True)
    C = o * (.2 * w) + Vector((0, 0, z0 + rb))
    if not claw:                                      # pad foot: flattened disc under the ankle
        b.add(_sphere(.4 * w, 10, 4, .35), m, True, closed=True, T=Tr(C.x + o.x * .1 * w, C.y + o.y * .1 * w, z0 + .14 * w))
        return
    b.add(_sphere(rb, 8, 5), m, True, closed=True, T=Tr(*C))
    a0 = atan2(o.y, o.x)
    for da in (0, 65, -65, 180):
        a = a0 + radians(da); pts, rr = [], []
        for k in range(6):
            ph = radians(12 + 22 * k)
            pts.append(C + Vector((cos(a) * sin(ph), sin(a) * sin(ph), cos(ph))) * (rb * 1.06))
            rr.append(w * (.17 - .02 * k))
        b.add(_tube(pts, rr, 5), m, True, closed=True)


@_prop
def turned_leg(b, height, width=.06, style='baluster', top_block=0.0, bottom_block=0.0, mat='dark_oak_antique',
               segments=12, pitch=.16, starts=2, out=(1, -1), foot='claw', taper=.6):
    """Furniture leg / column, origin floor centre, axis +Z.  width = square stock side (block size);
    top_block / bottom_block = heights of square joint blocks.  style: any TURNINGS key, or
    'barley_twist' (pitch = one full turn, starts = number of ropes), 'cabriole' (S-leg whose knee
    points along `out`; foot = 'claw' ball-and-claw | 'pad'), 'taper' (square, foot = taper * width)."""
    m = mat; w = width; z0, z1 = bottom_block, height - top_block
    if bottom_block:
        b.add(_box((-w / 2, -w / 2, 0), (w / 2, w / 2, z0), w * .05), m, closed=True)
    if top_block:
        b.add(_box((-w / 2, -w / 2, z1), (w / 2, w / 2, height), w * .05), m, closed=True)
    if style == 'cabriole':
        _cabriole(b, m, w, z0, z1, out, foot)
    elif style == 'taper':
        f = _frames([(0, 0, z0), (0, 0, z0 + (z1 - z0) * .5), (0, 0, z1)], up=(1, 0, 0))
        b.add(_sweep([(1, 1), (-1, 1), (-1, -1), (1, -1)], f, [w * taper / 2, w * (1 + taper) / 4, w / 2]), m, closed=True)
    elif style == 'barley_twist':
        R = w / 2; c = min(.035, (z1 - z0) * .08); n = max(4, int((z1 - z0 - 2 * c) / (pitch / 12)))
        prof = [(0, z0), (R * .96, z0), (R, z0 + c * .35), (R, z0 + c * .7), (R * .8, z0 + c)]
        tw = {}
        for i in range(n + 1):
            z = z0 + c + (z1 - z0 - 2 * c) * i / n
            tw[len(prof)] = (z, min(1, i / 3, (n - i) / 3)); prof.append((R * .9, z))
        prof += [(R * .8, z1 - c), (R, z1 - c * .7), (R, z1 - c * .35), (R * .96, z1), (0, z1)]

        def rmod(t, j):
            if j not in tw:
                return 1
            z, k = tw[j]
            return 1 - .2 * k * (.5 - .5 * cos(starts * (t - tau * z / pitch)))
        b.add(_lathe(prof, max(segments, 6 * starts), rmod), m, True, closed=True)
    else:
        prof = [(0, z0)] + turned_profile(style, z1 - z0, w, z0) + [(0, z1)]
        rmod, seg = None, segments
        if style == 'cup_cover':            # gadrooned cover (upper half of the bulb)
            seg = max(segments, 36)
            gad = {j + 1 for j, (t, _) in enumerate(TURNINGS[style]) if .55 <= t <= .87}
            rmod = lambda t, j: 1 + (.07 * cos(12 * t) if j in gad else 0)
        b.add(_lathe(prof, seg, rmod), m, True, closed=True)


def baluster(height=.9, width=.032, base_block=.18, top_block=.12, mat='white_gloss', style='spindle', name=None):
    """Stair spindle: square stock with a turned middle.  Origin floor centre."""
    return turned_leg(height, width, style, top_block, base_block, mat, 10, name=name or 'baluster')

# ----------------------------------------------------------------------------- cabinetry + hardware
@_prop
def panel_door(b, w, h, t=.02, stile=.085, rail=None, recess=.006, bead=.012, mat='navy_cabinet', panels=(1, 1),
               slab=False, edge=.002):
    """Shaker cabinet door / drawer front: frame + recessed flat panel(s) with a sloped bead moulding.
    stile = vertical member width (also muntins), rail = horizontal member width (default = stile),
    panels = (columns, rows), slab=True = plain flat front.  Origin: bottom centre of the back face."""
    rail = stile if rail is None else rail
    yf, e, x0, x1 = -t, edge, -w / 2, w / 2
    vs, fs = [], []

    def R(xa, za, xb, zb, y):
        return [(xa, y, za), (xb, y, za), (xb, y, zb), (xa, y, zb)]

    def quad(p):
        n = len(vs); vs.extend(p); fs.append((n, n + 1, n + 2, n + 3))

    def ring(A, Bq):
        for i in range(4):
            quad([A[i], A[(i + 1) % 4], Bq[(i + 1) % 4], Bq[i]])
    back, full, front = R(x0, 0, x1, h, 0), R(x0, 0, x1, h, yf + e), R(x0 + e, e, x1 - e, h - e, yf)
    quad(back[::-1]); ring(back, full); ring(full, front)
    cols, rows = panels
    if slab or w < 2 * stile + .03 or h < 2 * rail + .03:
        quad(front)
    else:
        pw = (w - (cols + 1) * stile) / cols; ph = (h - (rows + 1) * rail) / rows
        xs = [x0 + e] + [x0 + stile + c * (pw + stile) + k * pw for c in range(cols) for k in (0, 1)] + [x1 - e]
        zs = [e] + [rail + r * (ph + rail) + k * ph for r in range(rows) for k in (0, 1)] + [h - e]
        for i in range(len(xs) - 1):
            for j in range(len(zs) - 1):
                O = R(xs[i], zs[j], xs[i + 1], zs[j + 1], yf)
                if i % 2 and j % 2:
                    I = R(xs[i] + bead, zs[j] + bead, xs[i + 1] - bead, zs[j + 1] - bead, yf + recess)
                    ring(O, I); quad(I)
                else:
                    quad(O)
    b.add(G(vs, fs), mat)


@_prop
def cabinet_carcass(b, w, d, h, mat='navy_cabinet', plinth=.15, plinth_recess=.04, open_front=False, shelves=0,
                    panel=.018, inner=None):
    """Cabinet box.  Origin: floor centre on the wall plane; body spans y 0..-d, z plinth..h (plinth=0 for
    wall units).  open_front=True builds real 18 mm panels, a back and `shelves` evenly spaced shelves; every face
    seen through the open front (sides, top, bottom, back, shelves) takes `inner` (default = mat), the outside
    and the front edges stay `mat` - the carcass behind a door that opens."""
    m, x = mat, w / 2
    if plinth:
        b.add(_box((-x, -d + plinth_recess, 0), (x, -.002, plinth)), m)
    if not open_front:
        b.add(_box((-x, -d, plinth), (x, 0, h), .0015), m, closed=True)
        return
    p, im = panel, inner or mat

    def lined(face):                             # bevelled _box faces come -x +x -y +y -z +z, then 20 chamfers
        return [im if k == face else m for k in range(26)]
    for sx in (-1, 1):
        b.add(_box((sx * x, -d, plinth), (sx * (x - p), 0, h), .001), lined(0 if sx > 0 else 1), closed=True)
    b.add(_box((-x + p, -d, plinth), (x - p, 0, plinth + p), .001), lined(5), closed=True)
    b.add(_box((-x + p, -d, h - p), (x - p, 0, h), .001), lined(4), closed=True)
    b.add(_box((-x + p, -.006, plinth + p), (x - p, 0, h - p)), im)
    for i in range(shelves):
        z = plinth + p + (h - plinth - 2 * p) * (i + 1) / (shelves + 1)
        b.add(_box((-x + p, -d + .01, z - p / 2), (x - p, -.006, z + p / 2), .001), im, closed=True)


@_prop
def handle_bar(b, length=.22, centres=.16, dia=.012, standoff=.032, finish='antique_brass', vertical=False):
    """T-bar pull: bar on two posts.  Origin: door face, centre.  Bar along X (vertical=True -> along Z)."""
    m = _fin(finish)
    with b.at(Rot('Y', 90) if vertical else Matrix.Identity(4)):
        b.add(_tube([(-length / 2, -standoff, 0), (length / 2, -standoff, 0)], dia / 2, 8), m, True, closed=True)
        for sx in (-1, 1):
            b.add(_tube([(sx * centres / 2, 0, 0), (sx * centres / 2, -standoff, 0)], dia * .42, 8), m, True, closed=True)


@_prop
def handle_knob(b, dia=.03, projection=.03, finish='antique_brass'):
    """Mushroom knob.  Origin: door face."""
    r, p = dia / 2, projection
    b.add(_lathe([(0, 0), (r * .5, 0), (r * .4, p * .5), (r * .95, p * .62), (r, p * .8), (r * .7, p), (0, p)], 14),
          _fin(finish), True, closed=True, T=Rot('X', 90))


@_prop
def handle_cup(b, width=.096, height=.04, projection=.026, finish='antique_brass'):
    """Cup (bin) pull, open underneath.  Origin: drawer face, centre of the bottom edge of the cup."""
    m, a = _fin(finish), width / 2
    b.add(_grid(lambda u, v: (a * cos(pi * u) * cos(pi / 2 * v), -projection * sin(pi / 2 * v),
                              height * sin(pi * u) * cos(pi / 2 * v)), 10, 4), two_sided(m), True)
    b.add(_box((-a - .005, -.002, -.003), (a + .005, 0, height + .006), .0008), m, closed=True)


@_prop
def handle_lever(b, length=.12, finish='brass', rose=.052, hand=1):
    """Door lever on a round rose.  Origin: door face, rose centre; lever points +X (hand=-1 -> -X)."""
    m = _fin(finish)
    b.add(_lathe([(0, 0), (rose / 2, 0), (rose / 2, .004), (rose * .42, .007), (.011, .009), (.009, .04), (0, .04)], 16),
          m, True, closed=True, T=Rot('X', 90))
    L = hand * length
    b.add(_tube([(0, -.04, 0), (L * .1, -.047, 0), (L * .5, -.049, .002), (L * .9, -.046, 0), (L, -.04, -.004)],
                [.009, .009, .0075, .007, .0065], 8), m, True, closed=True)


@_prop
def handle_d(b, length=.13, dia=.01, projection=.03, finish='brass', vertical=False):
    """D / bow handle.  Origin: door face, centre."""
    L, p = length / 2, projection; r = min(p * .5, .012)
    pts = [(-L, 0, 0), (-L, -p + r, 0), (-L + r * .3, -p + r * .3, 0), (-L + r, -p, 0), (L - r, -p, 0),
           (L - r * .3, -p + r * .3, 0), (L, -p + r, 0), (L, 0, 0)]
    b.add(_tube(pts, dia / 2, 6), _fin(finish), True, closed=True, T=Rot('Y', 90) if vertical else None)


@_prop
def handle_drop(b, width=.07, drop=.035, finish='black'):
    """Bail / swan-neck drop handle on two rosettes.  Origin: face, centre between the rosettes."""
    m = _fin(finish)
    for sx in (-1, 1):
        b.add(_lathe([(0, 0), (.009, 0), (.008, .003), (.004, .006), (0, .008)], 8), m, True, closed=True,
              T=Tr(sx * width / 2, 0, 0) @ Rot('X', 90))
    b.add(_tube([(-cos(pi * i / 8) * width / 2, -.008, -sin(pi * i / 8) * drop) for i in range(9)], .003, 5),
          m, True, closed=True)


# ----------------------------------------------------------------------------- electrical
@_prop
def downlight(b, dia=.085, lamp_dia=.05, watts=0.0, kelvin=3000, spot_deg=110, strength=12.0, trim='plastic_white'):
    """Recessed LED downlight: trim ring + emissive lens.  watts > 0 adds a real child SPOT light [H];
    the default 0 leaves the emitter to lighting.downlight(ctx, room, x, y) so it is not doubled.
    Origin: ceiling plane, centre; everything hangs below z=0 (max 5 mm)."""
    ro, ri = dia / 2, lamp_dia / 2
    b.add(_lathe([(ri, -.0015), (ri + .004, -.005), (ro - .002, -.004), (ro, 0)], 20), trim, True)
    b.add(_lathe([(0, -.0012), (ri + .001, -.0012)], 20), emissive('#FFE9C4', strength))
    if watts:
        b.kid(lambda: _light('SPOT', watts, kelvin, ri, spot_deg), Tr(0, 0, -.02))


def _plate(b, w, h, t, m):
    b.add(_box((-w / 2, -t, -h / 2), (w / 2, 0, h / 2), min(.003, t * .6)), m, closed=True)


@_prop
def switch_plate(b, gangs=1, kind='rocker', finish='white', wide=None, h=.086):
    """UK light switch.  kind: 'rocker' | 'dimmer' (round knobs) | 'push' (small round buttons) | 'toggle'
    (dolly) | 'blank'.  finish 'white' (moulded plastic) or 'brass'/'antique_brass'/'chrome'/'black' (flat
    metal plate).  Plate 86x86, or 146x86 when wide (default: 3+ gangs of dimmer/push/toggle).
    Origin: wall, plate centre."""
    white = finish == 'white'
    w = .146 if (wide or (wide is None and gangs >= 3 and kind != 'rocker')) else .086
    t = .009 if white else .004
    pm = _fin(finish); km = pm if white or kind in ('dimmer', 'toggle') else mat('plastic_dark')
    _plate(b, w, h, t, pm)
    pitch = min(.036, (w - .03) / gangs); rw = min(.022, pitch * .72)
    for i in range(gangs):
        x = (i - (gangs - 1) / 2) * pitch
        if kind == 'rocker':
            b.add(_box((-rw / 2, -.0045, -.017), (rw / 2, .001, .017), .0008), km, closed=True,
                  T=Tr(x, -t, 0) @ Rot('X', 6))
        elif kind == 'dimmer':
            b.add(_lathe([(0, 0), (.0135, 0), (.0125, .012), (.011, .014), (0, .014)], 12), km, True, closed=True,
                  T=Tr(x, -t, 0) @ Rot('X', 90))
        elif kind == 'push':
            b.add(_lathe([(0, 0), (.007, 0), (.0065, .004), (0, .0045)], 10), km, True, closed=True,
                  T=Tr(x, -t, 0) @ Rot('X', 90))
        elif kind == 'toggle':
            b.add(_lathe([(0, 0), (.006, 0), (.005, .003), (0, .003)], 8), km, True, closed=True,
                  T=Tr(x, -t, 0) @ Rot('X', 90))
            b.add(_tube([(x, -t, 0), (x, -t - .012, .008)], [.003, .0022], 6), km, True, closed=True)


@_prop
def socket(b, gangs=2, switched=True, finish='white', h=.086):
    """UK 13 A socket outlet (1 or 2 gang, 86 / 146 x 86), white plastic or flat metal plate.
    Origin: wall, plate centre."""
    white = finish == 'white'
    w = .146 if gangs == 2 else .086; t = .009 if white else .004
    pm = _fin(finish); dark = mat('plastic_dark'); km = pm if white else dark
    _plate(b, w, h, t, pm)
    for i in range(gangs):
        x = (i - (gangs - 1) / 2) * .072
        if not white:   # black plastic insert on metal plates
            b.add(_box((x - .024, -t - .0006, -.03), (x + .024, -t + .001, .012)), dark)
        yy = -t - (.0005 if white else .0011)
        for dx, dz, sw, sh in ((0, .002, .004, .008), (-.011, -.019, .0065, .004), (.011, -.019, .0065, .004)):
            b.add(_box((x + dx - sw / 2, yy, dz - sh / 2), (x + dx + sw / 2, -t + .001, dz + sh / 2)),
                  mat('#3a3a3a') if white else mat('#6a6a6a'))
        if switched:
            b.add(_box((-.006, -.004, -.009), (.006, .001, .009), .0006), km, closed=True,
                  T=Tr(x, -t, .027) @ Rot('X', 6))

# ----------------------------------------------------------------------------- frames, pictures, mirrors
# style: (default frame width, default depth, profile kind, outer material, inner-slip material, corner ornaments)
FRAME_STYLES = {
    'gilt_ornate': (.095, .045, 'swept', 'gold_antique', None, True),    # rippled baroque + cartouches
    'gilt_swept': (.08, .04, 'swept', 'gold_antique', None, False),      # rippled leaf moulding
    'gilt_plain': (.06, .03, 'scoop', 'gold_bright', None, False),
    'gilt_bead': (.06, .03, 'reeded', 'gold_bright', None, False),       # reeded with inner bead course
    'gilt_thin': (.015, .02, 'flat', 'gold_bright', None, False),
    'champagne': (.06, .03, 'scoop', 'champagne', None, False),
    'bronze_gold': (.06, .03, 'scoop', 'gold_bronze', None, False),
    'silver_green': (.045, .025, 'scoop', 'silver_green', None, False),
    'dark_wood': (.045, .025, 'flat', 'frame_dark', None, False),
    'dark_gold_slip': (.055, .028, 'slip', 'frame_dark', 'gold_antique', False),
    'walnut_gold': (.028, .02, 'slip', 'walnut', 'gold_antique', False),
    'olive_bronze': (.042, .02, 'flat', 'olive_bronze', None, False),
    'white': (.03, .02, 'flat', 'white_gloss', None, False),
    'black': (.02, .02, 'flat', 'black_matt', None, False),
}
_FRAME_PROF = {   # (d, y) in units of (frame width, depth): back-outer -> front -> back-inner
    'scoop': [(0, 0), (0, .65), (.1, .95), (.24, 1), (.34, .9), (.5, .55), (.7, .38), (.84, .36), (.88, .48), (.96, .48),
              (1, .38), (1, 0)],
    'swept': [(0, 0), (0, .45), (.08, .8), (.2, 1), (.34, .95), (.46, .66), (.62, .5), (.74, .52), (.8, .62), (.88, .6),
              (.93, .42), (1, .36), (1, 0)],
    'reeded': [(0, 0), (0, .8), (.06, 1), (.16, .86), (.26, 1), (.36, .86), (.46, 1), (.56, .84), (.66, .7), (.76, .56),
               (.82, .7), (.9, .7), (.94, .5), (1, .45), (1, 0)],
    'slip': [(0, 0), (0, .9), (.08, 1), (.7, 1), (.76, .9), (.78, .72), (.86, .76), (.94, .62), (1, .55), (1, 0)],
    'flat': [(0, 0), (0, .85), (.12, 1), (.88, 1), (1, .88), (1, 0)],
}


def _frame(b, w, h, prof, mats, fw, ripple=0.0, pitch=.04):
    """Mitred moulding round a w x h rectangle (outer size).  prof = closed loop [(d, y)], d = inset from the
    outer edge, y = depth (negative = toward the viewer).  ripple > 0 carves a running leaf/bead pattern
    into the crest (and, in antiphase, the inner bead) between the mitres."""
    m = len(prof); rings = []
    corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]; inward = [(0, 1), (-1, 0), (0, -1), (1, 0)]
    for k in range(4):
        (sx, sz), (tx, tz), (ix, iz) = corners[k], corners[(k + 1) % 4], inward[k]
        rings.append([(sx * (w / 2 - d), y, sz * (h / 2 - d)) for d, y in prof])
        if not ripple:
            continue
        L = (w if k % 2 == 0 else h) - 2 * fw; n = 2 * max(1, round(L / pitch))
        ax, az = (tx - sx) / 2, (tz - sz) / 2          # unit travel direction along the side
        for i in range(n + 1):
            s = -L / 2 + L * i / n; mm = i % 2
            px, pz = sx * w / 2 * abs(ix) + ax * s, sz * h / 2 * abs(iz) + az * s
            rings.append([(px + ix * d, y * (1 - ripple * (.36 * mm if .04 * fw < d < .5 * fw else
                                                           .3 * (1 - mm) if .7 * fw < d < .92 * fw else 0)), pz + iz * d)
                          for d, y in prof])
    K = len(rings)
    vs = [p for r in rings for p in r]
    fs = [(j * m + i, ((j + 1) % K) * m + i, ((j + 1) % K) * m + (i + 1) % m, j * m + (i + 1) % m)
          for j in range(K) for i in range(m)]
    b.add(G(vs, fs), [mats[i] for j in range(K) for i in range(m)], smooth=70 if ripple else False, closed=True)


def _framed(b, w, h, style, frame_w, depth, content, image=None, mount=0.0, mount_mat='cream_mount', slip=None,
            glass=False, fill=None, bevel=0.0, tilt=0.0):
    fw0, fd0, kind, om, sm, orn = FRAME_STYLES[style]
    fw, fd = frame_w or fw0, depth or fd0
    prof = [(d * fw, -y * fd) for d, y in _FRAME_PROF[kind]]; m = len(prof)
    mats = [sm if (sm and prof[i][0] >= .77 * fw and i < m - 1) else om for i in range(m)]

    def rect(ww, hh, y):
        return [(-ww / 2, y, -hh / 2), (ww / 2, y, -hh / 2), (ww / 2, y, hh / 2), (-ww / 2, y, hh / 2)]

    def ring(A, Bq, mm):
        b.add(G(A + Bq, [(i, (i + 1) % 4, 4 + (i + 1) % 4, 4 + i) for i in range(4)]), mm)
    with b.at(Tr(0, 0, -h / 2) @ Rot('X', tilt) @ Tr(0, 0, h / 2)):
        _frame(b, w, h, prof, mats, fw, 1.0 if kind == 'swept' else 0.0)
        if orn:
            for sx, sz in ((-1, -1), (1, -1), (1, 1), (-1, 1), (0, -1), (1, 0), (0, 1), (-1, 0)):
                T = Tr(sx * (w / 2 - fw * .5), -fd * .6, sz * (h / 2 - fw * .5)) @ \
                    Rot('Y', -45 * sx * sz if sx and sz else 90 * abs(sx)) @ Sc(fw * (.85 if sx and sz else .7), fd * .42, fw * .4)
                b.add(_sphere(1, 10, 5), om, True, closed=True, T=T)
        yb = prof[-2][1] + .003                       # content plane, just behind the inner lip
        cw, ch = w - 2 * fw + .006, h - 2 * fw + .006  # sight size + rabbet overlap
        if glass:
            b.add(G(rect(cw, ch, yb - .002), [(0, 1, 2, 3)]), 'glass_clear')
        if content == 'mirror':
            if bevel:
                ring(rect(cw, ch, yb), rect(cw - 2 * bevel, ch - 2 * bevel, yb - .002), 'mirror')
                cw, ch, yb = cw - 2 * bevel, ch - 2 * bevel, yb - .002
            b.add(G(rect(cw, ch, yb), [(0, 1, 2, 3)]), 'mirror')
            return
        if mount:
            mw = .18 * min(cw, ch) if mount is True else mount
            ring(rect(cw, ch, yb), rect(cw - 2 * mw, ch - 2 * mw, yb), mount_mat)
            ring(rect(cw - 2 * mw, ch - 2 * mw, yb), rect(cw - 2 * mw - .004, ch - 2 * mw - .004, yb + .0015), '#FAFAF6')
            cw, ch, yb = cw - 2 * mw - .004, ch - 2 * mw - .004, yb + .0015
        if slip:
            ring(rect(cw, ch, yb), rect(cw - 2 * slip[1], ch - 2 * slip[1], yb), slip[0])
            cw, ch = cw - 2 * slip[1], ch - 2 * slip[1]
        if image:
            b.add(G(rect(cw, ch, yb), [(0, 1, 2, 3)], vuv=[(0, 0), (1, 0), (1, 1), (0, 1)]), image_mat(image))
        else:                                          # neutral three-band "landscape" placeholder
            z = -ch / 2
            for frac, col in zip((.3, .22, .48), fill or ('#6F7A55', '#93A07E', '#BCC7CE')):
                b.add(G([(-cw / 2, yb, z), (cw / 2, yb, z), (cw / 2, yb, z + ch * frac), (-cw / 2, yb, z + ch * frac)],
                        [(0, 1, 2, 3)]), col)
                z += ch * frac


@_prop
def framed_picture(b, image=None, w=.6, h=.5, frame_style='gilt_plain', frame_w=None, depth=None, mount=0.0,
                   glass=False, slip=None, mount_mat='cream_mount', tilt_deg=0.0, fill=None):
    """Framed picture, outer size w x h.  image = file path (UV 0..1 over the picture window) or None
    (neutral 3-band placeholder; fill=(ground, mid, sky) hex).  frame_style: FRAME_STYLES key.
    mount = mount width in m (True = auto), slip = (material, width) inner fillet, glass = glazing quad.
    tilt_deg tips the top off the wall (pivot = bottom back edge).  Origin: wall, centre of the frame."""
    _framed(b, w, h, frame_style, frame_w, depth, 'picture', image, mount, mount_mat, slip, glass, fill, 0, tilt_deg)


@_prop
def mirror_framed(b, w=1.2, h=.85, frame_style='gilt_ornate', frame_w=None, depth=None, bevel=0.0, tilt_deg=0.0):
    """Framed mirror (real mirror material); bevel = width of the bevelled glass edge.  Origin: wall, centre."""
    _framed(b, w, h, frame_style, frame_w, depth, 'mirror', bevel=bevel, tilt=tilt_deg)


# ----------------------------------------------------------------------------- rug
@_prop
def rug(b, image=None, w=1.4, d=2.0, thickness=.008, fringe=0.0, corner_r=0.0, color='#E4DDC8', fringe_mat='ivory',
        seed=0):
    """Rug w (X) x d (Y) with a soft edge; image mapped u->X, v->Y over the whole rug.  fringe = strand
    length (m) on the two short ends (0 = none).  Origin: floor centre (underside 1.2 mm above z=0)."""
    m = image_mat(image, .9) if image else mat(color)
    out = _rrect(w, d, corner_r, 4); top = _inset(out, thickness * .8); n = len(out)
    vs = [(x, y, thickness) for x, y in top] + [(x, y, .0012) for x, y in out]
    b.add(G(vs, [tuple(range(n))] + [(i, n + i, n + (i + 1) % n, (i + 1) % n) for i in range(n)],
            vuv=[(x / w + .5, y / d + .5) for x, y, _ in vs]), m)
    if fringe:
        rnd = random.Random(seed); span, half = (w, d / 2) if d >= w else (d, w / 2)
        span -= 2 * corner_r; k = int(span / .008); vs, fs = [], []
        for sg in (-1, 1):
            for i in range(k):
                x = -span / 2 + span * (i + .5) / k; L = fringe * rnd.uniform(.8, 1.1); sk = rnd.uniform(-.004, .004)
                q = [(x - .002, sg * half, .002), (x + .002, sg * half, .002), (x + sk + .001, sg * (half + L), .0008),
                     (x + sk - .001, sg * (half + L), .0008)]
                fs.append(tuple(range(len(vs), len(vs) + 4))[::sg]); vs += q
        b.add(G(vs, fs), fringe_mat, T=None if d >= w else Rot('Z', 90))


# ----------------------------------------------------------------------------- wall plaque, TV, speaker
def _clip(poly, axis, val, keep_hi):
    """Sutherland-Hodgman clip of a 2D polygon against x (axis 0) or z (axis 1) = val."""
    out = []
    for i in range(len(poly)):
        p, q = poly[i - 1], poly[i]
        ip, iq = (p[axis] >= val) == keep_hi, (q[axis] >= val) == keep_hi
        if ip != iq:
            t = (val - p[axis]) / (q[axis] - p[axis]); out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
        if iq:
            out.append(q)
    return out


def _shield(w, h, shape):
    if shape == 'round':
        return _circle(20, w / 2)
    if shape == 'lozenge':
        return [(0, -h / 2), (w / 2, 0), (0, h / 2), (-w / 2, 0)]
    zc = -h / 2 + .62 * h
    R = [((w / 2) * sin(radians(a)), zc - (zc + h / 2) * cos(radians(a))) for a in (18, 36, 54, 72, 90)]
    return [(0, -h / 2)] + R + [(w / 2, h / 2), (-w / 2, h / 2)] + [(-x, z) for x, z in reversed(R)]


_HERALD = ['#1F2A44', '#8E1B1B', '#141414', '#C8A64B', '#7FA6C9', '#E8E4D8', '#2E5A3A']


@_prop
def wall_plaque_shield(b, w=.15, h=.18, shape='heater', variant=0, board=None, colors=None, image=None,
                       thickness=.02, scroll=True):
    """Regimental crest plaque: bevelled wooden board (shape 'heater' | 'round' | 'lozenge') carrying a raised
    crest with coloured emblem zones.  variant (int) picks board tone, partition (plain / chief / per-pale /
    per-fess), colours and emblem deterministically; colors=(field, second, emblem) overrides; image = a
    rectified crop mapped over the whole board front instead.  Origin: wall, centre."""
    rnd = random.Random(variant * 7919 + 13)
    board = board or ('#7A5230', '#3A2A20')[variant % 2]
    out = _shield(w, h, shape); t = thickness
    if image:
        ins = _inset(out, .003); n = len(out)
        b.add(_prism(out, -t + .003, 0), board, closed=True)
        b.add(G([(x, -t, z) for x, z in ins] + [(x, -t + .003, z) for x, z in out],
                [tuple(range(n))] + [(n + i, n + (i + 1) % n, (i + 1) % n, i) for i in range(n)],
                vuv=[(x / w + .5, z / h + .5) for x, z in ins + out]), image_mat(image))
        return
    b.add(_prism(out, -t, 0, .003), board, closed=True)
    ca, cb, ce = colors or (rnd.choice(_HERALD[:3] + _HERALD[4:5]), rnd.choice(_HERALD[3:6]), rnd.choice(('gilt', 'silver', '#E8E4D8')))
    field = _inset(out, .11 * w) if shape != 'round' else _circle(20, w * .36)
    part = rnd.choice(('plain', 'chief', 'pale', 'fess')) if shape != 'round' else 'plain'
    zones = [(field, ca)]
    if part == 'chief':
        zones = [(_clip(field, 1, h * .2, False), ca), (_clip(field, 1, h * .2, True), cb)]
    elif part == 'pale':
        zones = [(_clip(field, 0, 0, False), ca), (_clip(field, 0, 0, True), cb)]
    elif part == 'fess':
        zones = [(_clip(field, 1, h * .05, False), cb), (_clip(field, 1, h * .05, True), ca)]
    for poly, col in zones:
        b.add(_prism(poly, -t - .004, -t + .001, .001), col, closed=True)
    if shape == 'round':                               # rope ring + crown
        b.add(_tube([(x, -t - .003, z) for x, z in _circle(16, w * .41)], .006, 5, loop=True), 'gilt', True)
        b.add(_box((-.02, -t - .008, w * .4), (.02, -t, w * .4 + .022), .003), 'gilt', closed=True)
    em = rnd.choice(('disc', 'cross', 'lozenge', 'star')); y = -t - .004; s = w * .16; cz = h * (.02 if shape == 'heater' else 0)
    if em == 'disc':
        b.add(_lathe([(0, 0), (s, 0), (s * .8, .004), (0, .007)], 10), ce, True, closed=True, T=Tr(0, y, cz) @ Rot('X', 90))
    elif em == 'cross':
        b.add(_box((-s, y - .004, cz - s * .28), (s, y, cz + s * .28), .001), ce, closed=True)
        b.add(_box((-s * .28, y - .0045, cz - s * 1.2), (s * .28, y, cz + s * 1.2), .001), ce, closed=True)
    else:
        k = 4 if em == 'lozenge' else 10
        poly = [((s if i % 2 == 0 or k == 4 else s * .45) * 1.1 * sin(tau * i / k), cz + (s if i % 2 == 0 or k == 4 else s * .45) * 1.3 * cos(tau * i / k))
                for i in range(k)][::-1]
        b.add(_prism(poly, y - .004, y, .001), ce, closed=True)
    if scroll and shape == 'heater':
        b.add(_box((-w * .3, -t - .005, -h * .36), (w * .3, -t, -h * .36 + .016), .002), '#E0D6B8', closed=True)


@_prop
def tv_panel(b, w=1.89, h=1.08, depth=.03, standoff=.04, bezel=.005):
    """Wall-mounted flat TV: glossy black screen, thin bezel, slim mount.  Origin: wall, screen centre."""
    y0 = -standoff - depth
    b.add(_box((-w / 2, y0, -h / 2), (w / 2, -standoff, h / 2), .002), 'plastic_dark', closed=True)
    b.add(G([(-w / 2 + bezel, y0 - .0006, -h / 2 + bezel), (w / 2 - bezel, y0 - .0006, -h / 2 + bezel),
             (w / 2 - bezel, y0 - .0006, h / 2 - bezel), (-w / 2 + bezel, y0 - .0006, h / 2 - bezel)], [(0, 1, 2, 3)]),
          'screen_black')
    if standoff:
        b.add(_box((-min(.2, w * .3), -standoff, -min(.15, h * .3)), (min(.2, w * .3), 0, min(.15, h * .3))), 'plastic_dark')


@_prop
def tv_screen(b, w=1.88, h=1.07):
    """The lit picture of a TV, for the viewer's `show when=1 fx='tv'`: one quad with 0..1 UVs (U to the viewer's
    right, V up), black base + pale emission (glTF emissive, so the viewer can swap in its animated picture).
    Origin: centre; lies in the plane y = 0, faces -Y.  Put it 1 mm in front of the black glass."""
    b.add(G([(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)], [(0, 1, 2, 3)],
            vuv=[(0, 0), (1, 0), (1, 1), (0, 1)]), _emit('tv_screen', '#050506', '#AFC6F2', 1.5, .2))


@_prop
def speaker_box(b, w=.21, h=.33, d=.27, mat='black_matt', drivers=2):
    """Bookshelf loudspeaker: cabinet + woofer (+ tweeter when drivers=2).  Origin: bottom centre, front -Y."""
    b.add(_box((-w / 2, -d, 0), (w / 2, 0, h), .004), mat, closed=True)
    r = min(w * .38, h * .25)
    spec = [(r, h * (.36 if drivers > 1 else .5))] + ([(w * .13, h * .8)] if drivers > 1 else [])
    for rr, z in spec:
        prof = [(rr, 0), (rr, .003), (rr * .94, .004), (rr * .86, .008), (rr * .78, .004), (rr * .34, .0015), (rr * .3, .004), (0, .006)]
        b.add(_lathe(prof, 16), 'cone_grey', True, T=Tr(0, -d, z) @ Rot('X', 90))

# ----------------------------------------------------------------------------- curtains, poles, shutters
def _tassel(b, L, head, m, T=None):
    r = head / 2
    prof = [(0, -L), (r * 1.15, -L), (r * .95, -L * .45), (r * .6, -L * .3), (r, -L * .22), (r, -L * .16),
            (r * .55, -L * .08), (.004, -L * .06), (.004, 0), (0, 0)]
    b.add(_lathe(prof, 8), m, True, closed=True, T=T)


@_prop
def tassel(b, length=.30, head_dia=.06, mat='tassel_gold'):
    """Tassel: cord, bulb head, skirt.  Origin: hanging point (top)."""
    _tassel(b, length, head_dia, mat)


def _sm(k):
    k = max(0.0, min(1.0, k)); return k * k * (3 - 2 * k)


def _curtain(b, W, H, m, folds, depth, side, tie, gather, seed, res, tie_mat, tassel_mat, tassel_len, hardware=True):
    """Pleated cloth W wide hanging from z=0 to -H in front of y=0.  side = -1/0/+1: tied back toward -X / not / +X."""
    rnd = random.Random(seed); p0, p1, p2 = (rnd.uniform(0, tau) for _ in range(3))
    n = folds or max(2, round(W / .11)); vt = tie / H if side else 2.0; g0 = gather * .8

    def wf(v):                                   # width fraction at height v (0 top .. 1 hem)
        if not side:
            return 1.0
        if v <= vt:
            return 1 + (g0 - 1) * _sm(v / vt) ** 1.5
        return g0 + (gather - g0) * _sm((v - vt) * H / .5)

    def amp(v):                                  # fold depth: tight pencil pleats at the heading, deeper where gathered
        return .012 + (depth * min(1.7, wf(v) ** -.5) - .012) * _sm(v * H / .22)

    def fn(u, v):
        f = wf(v); x = side * (W / 2) * (1 - f) + (u - .5) * W * f
        s = sin(tau * (n * u + .1 * sin(3 * v + p2)) + p0); s = math.copysign(abs(s) ** .6, s)   # fuller, steeper pleats
        y = -.012 - amp(v) * (.5 + .5 * s) * (1 + .22 * sin(tau * n * .5 * u + p1))
        z = -v * H
        if side and v > vt:                      # the pulled (leading) edge of the hem rides up a little
            z += .07 * ((1 - u) if side > 0 else u) * ((v - vt) / (1 - vt)) ** 2
        return (x, y, z)
    b.add(_grid(fn, n * res, max(10, round(H / .09)), lambda u, v: (u * W * 2, -v * H), flip=True), two_sided(m), True)
    if side and hardware:
        f = wf(vt); a = amp(vt) * 1.22; cx = side * (W / 2) * (1 - f); hw = W * f / 2; zt = -tie
        loop = [(cx + (hw + .012) * cos(t), -.012 - a / 2 + (a / 2 + .014) * sin(t), zt + .03 * side * cos(t))
                for t in (tau * i / 16 for i in range(16))]
        b.add(_tube(loop, .007, 5, loop=True), tie_mat, True)
        hx = side * (W / 2 + .012)
        b.add(_tube([(hx, 0, zt + .03), (hx, -.035, zt + .03)], .005, 6), 'brass', True, closed=True)
        if tassel_len:
            tx, ty = cx - side * hw * .2, -.012 - a - .03
            b.add(_sphere(.02, 8, 5), tie_mat, True, closed=True, T=Tr(tx, ty, zt - .012))
            _tassel(b, tassel_len, .06, tassel_mat, Tr(tx, ty, zt - .03))


@_prop
def curtain_panel(b, width=.5, height=2.4, mat='tartan_red', folds=None, depth=.06, tieback=None, tie_from_top=1.4,
                  gather=.6, tassel=.30, seed=1, fold_res=6, tie_mat='rope_cream', tassel_mat='tassel_gold',
                  hardware=True):
    """One pleated curtain drop (single-sided cloth - the material must be double-sided).  width = hanging
    (stack) width, folds = number of pleats (default width / 0.11), depth = fold depth.
    tieback: None | 'left' | 'right' (side the bunch is pulled to, seen from the room); tie_from_top = distance
    of the tie below the heading; gather = bunch width / width; tassel = tassel length (0 = none).
    hardware=False = cloth only: no tie rope, wall hook or tassel (a tieback=None drop never has any - that is the
    closed curtain to hang on an existing pole).
    UVs: 1 unit = 1 m of cloth (fullness 2).  Origin: wall plane, top centre of the heading."""
    _curtain(b, width, height, mat, folds, depth, {'left': -1, 'right': 1}.get(tieback, 0), tie_from_top, gather, seed,
             fold_res, tie_mat, tassel_mat, tassel, hardware)


_FINIALS = {
    'ball': lambda r: [(0, 0), (r * 1.15, 0), (r * 1.15, .008), (r * .6, .012)] +
                      [(2 * r * sin(radians(a)), .012 + 2 * r * (1 - cos(radians(a)))) for a in (20, 50, 80, 110, 140, 165, 180)],
    'urn': lambda r: [(0, 0), (r * 1.15, 0), (r * 1.15, .008), (r * .6, .014), (r * 1.6, .03), (r * 1.9, .05), (r * 1.2, .075),
                      (r * .5, .085), (r * .7, .095), (0, .105)],
}


def _pole(b, length, dia, finial, ring_xs, m, y, z):
    r = dia / 2
    b.add(_tube([(-length / 2, y, z), (length / 2, y, z)], r, 10), m, True, closed=True)
    for sx in (-1, 1):
        b.add(_lathe(_FINIALS[finial](r), 10), m, True, closed=True, T=Tr(sx * length / 2, y, z) @ Rot('Y', 90 * sx))
    bx = [-(length / 2 - .1), length / 2 - .1] + ([0] if length > 2.4 else [])
    for x in bx:
        b.add(_tube([(x, 0, z - .02), (x, y, z - .02)], .006, 6), m, True, closed=True)
        b.add(_lathe([(0, 0), (.022, 0), (.02, .004), (0, .005)], 10), m, True, closed=True, T=Tr(x, 0, z - .02) @ Rot('X', 90))
        b.add(_box((x - .008, y - r, z - r - .012), (x + .008, y + r, z - r), .002), m, closed=True)
    R = r + .011
    for x in ring_xs:
        b.add(_tube([(x, y + R * cos(t), z - .008 + R * sin(t)) for t in (tau * i / 10 for i in range(10))], .003, 4,
                    loop=True, up=(1, 0, 0)), m, True)


@_prop
def curtain_pole(b, length=2.0, dia=.028, finial='ball', rings=12, mat='brass', standoff=.075):
    """Curtain pole with finials ('ball' | 'urn'), brackets and `rings` evenly spread rings.
    Origin: wall plane at pole-axis height, centre."""
    _pole(b, length, dia, finial, [(-.5 + (i + .5) / rings) * (length - .3) for i in range(rings)], mat, -standoff, 0)


def _pelmet(b, length, height, depth, m, z=0.0):
    t = .018
    b.add(_box((-length / 2, -depth, z - height), (length / 2, -depth + t, z), .002), m, closed=True)
    for sx in (-1, 1):
        b.add(_box((sx * length / 2, -depth + t, z - height), (sx * (length / 2 - t), 0, z), .002), m, closed=True)
    b.add(_box((-length / 2 + t, -depth + t, z - t), (length / 2 - t, 0, z)), m)


@_prop
def pelmet_box(b, length=2.0, height=.2, depth=.14, mat='white_gloss'):
    """Boxed pelmet (front board, returns, top board).  Origin: wall plane, top centre."""
    _pelmet(b, length, height, depth, mat)


@_prop
def curtain_pair(b, width=1.8, height=2.4, mat='tartan_red', stack=.5, tieback=True, tie_from_top=1.4, gather=.6,
                 hang='pole', depth=.06, tassel=.30, seed=1, fold_res=6, hang_mat=None, finial='ball',
                 tie_mat='rope_cream', tassel_mat='tassel_gold', hardware=True, cloth=True, closed=False):
    """Two drops (each `stack` wide) at the ends of a `width` span, tied back outward when tieback=True.
    hang: 'pole' (pole + rings + finials, overhanging 0.15 each end) | 'pelmet' (boxed pelmet 0.2 high) |
    'track' (slim white track) | None.  Origin: wall plane, top centre of the curtain heading.
    Openable curtains = the same call three times: cloth=False (pole / pelmet / track only, always there),
    hardware=False (the tied-back drops with their ties, nothing to hang from: show when=0) and hardware=False,
    closed=True (the two drops drawn straight across the span, no ties: show when=1)."""
    off = .035 if hang else 0.0
    cw, tb = (width / 2 + .01, False) if closed else (stack, tieback)    # closed: the halves lap 20 mm in the middle
    for sg in (-1, 1) if cloth else ():
        with b.at(Tr(sg * (width - cw) / 2, -off, 0)):
            _curtain(b, cw, height, mat, None, depth, sg if tb else 0, tie_from_top, gather, seed + (sg > 0),
                     fold_res, tie_mat, tassel_mat, tassel)
    yc = -off - .012 - depth * .6
    if not hardware:
        return
    if hang == 'pole':
        k = max(3, round(stack / .1))                                    # ponytail: rings stay bunched over the open stacks
        xs = [sg * (width / 2 - stack * (i + .5) / k) for sg in (-1, 1) for i in range(k)]
        _pole(b, width + .3, .028, finial, xs, hang_mat or 'brass', yc, .04)
    elif hang == 'pelmet':
        _pelmet(b, width + .12, .2, -yc + depth + .05, hang_mat or 'white_gloss', .06)
    elif hang == 'track':
        b.add(_box((-width / 2, yc - .008, .002), (width / 2, yc + .008, .016), .002), hang_mat or 'plastic_white', closed=True)


@_prop
def plantation_shutter_panel(b, w=.4, h=1.5, stile=.05, rail=.09, louvre=.063, thickness=.028, tilt_deg=40,
                             mid_rail=None, mat='white_gloss', tilt_rod=True):
    """Louvred shutter leaf: stiles, top/bottom rails, optional mid rail (z of its centre) and tilted
    elliptical louvres.  Origin: bottom centre, leaf mid-plane on y=0."""
    t, x = thickness / 2, w / 2
    for sx in (-1, 1):
        b.add(_box((sx * x, -t, 0), (sx * (x - stile), t, h), .0015), mat, closed=True)
    bays, z0 = [], rail
    for za, zb in [(0, rail)] + ([(mid_rail - .035, mid_rail + .035)] if mid_rail else []) + [(h - rail, h)]:
        b.add(_box((-x + stile, -t, za), (x - stile, t, zb), .0015), mat, closed=True)
        if za > z0:
            bays.append((z0, za))
        z0 = zb
    L, e, c, s = louvre / 2, .005, cos(radians(tilt_deg)), sin(radians(tilt_deg))
    sec = [(-(py * s + pz * c), -(py * c - pz * s)) for py, pz in ((-L, 0), (-L / 2, -e), (L / 2, -e), (L, 0), (L / 2, e), (-L / 2, e))]
    for za, zb in bays:
        n = max(1, int((zb - za) / (louvre * .78))); p = (zb - za) / n
        for i in range(n):
            f = _frames([(-x + stile, 0, za + p * (i + .5)), (x - stile, 0, za + p * (i + .5))])
            b.add(_sweep(sec, f), mat, True, closed=True)
        if tilt_rod:
            b.add(_box((-.005, -t - .014, za + p * .5), (.005, -t - .006, zb - p * .5), .001), mat, closed=True)


# ----------------------------------------------------------------------------- radiators
@_prop
def radiator_towel_rail(b, w=.4, h=1.2, groups=(8, 7, 5), pitch=.04, bar_dia=.022, standoff=.08, mat='anthracite',
                        valves=True):
    """Ladder towel radiator: two uprights, round bars in `groups` (bars per group, bottom -> top), four wall
    brackets, chrome valves + tails below.  Origin: wall plane, bottom centre of the uprights."""
    y, ux = -standoff, w / 2 - .015
    for sx in (-1, 1):
        b.add(_box((sx * ux - .015, y - .011, 0), (sx * ux + .015, y + .011, h), .006), mat, closed=True)
        for zb in (.12 * h, .88 * h):
            b.add(_tube([(sx * ux, 0, zb), (sx * ux, y, zb)], .008, 6), mat, True, closed=True)
        if valves:
            b.add(_tube([(sx * ux, y, 0), (sx * ux, y, -.03), (sx * ux, y, -.055)], [.009, .013, .013], 8), 'chrome', True, closed=True)
            b.add(_tube([(sx * ux, y, -.045), (sx * ux, 0, -.045)], .0075, 6), 'chrome', True, closed=True)
    nb, ng = sum(groups), len(groups)
    gap = (h - .08 - pitch * (nb - ng)) / max(1, ng - 1); z = .04
    for g in groups:
        for i in range(g):
            b.add(_tube([(-ux, y, z + pitch * i), (ux, y, z + pitch * i)], bar_dia / 2, 6, cap=False), mat, True)
        z += pitch * (g - 1) + gap


@_prop
def radiator_panel(b, w=1.0, h=.6, depth=.1, standoff=.03, mat='white_gloss', valves=True, floor_gap=.15):
    """Fluted double-panel convector radiator with top grille, valves and pipes dropping `floor_gap` to the
    floor.  Origin: wall plane, bottom centre of the radiator body."""
    yf, x = -standoff - depth, w / 2
    b.add(_box((-x, yf + .008, 0), (x, -standoff, h), .003), mat, closed=True)
    n = max(3, round((w - .02) / .0333)); p = (w - .02) / n; pts = [(-x + .01, yf + .007)]
    for i in range(n):
        x0 = -x + .01 + p * i
        pts += [(x0 + p * .1, yf), (x0 + p * .75, yf), (x0 + p * .85, yf + .007), (x0 + p, yf + .007)]
    vs = [(px, py, z) for z in (.012, h - .012) for px, py in pts]; k = len(pts)
    b.add(G(vs, [(i, i + 1, k + i + 1, k + i) for i in range(k - 1)]), mat)
    b.add(_box((-x + .012, yf + .014, h - .001), (x - .012, -standoff - .012, h + .0012)), 'cone_grey')
    if valves:
        yp = (yf - standoff) / 2
        for sx in (-1, 1):
            px = sx * (x + .035)
            b.add(_tube([(sx * x, yp, .04), (px, yp, .04), (px, yp, -floor_gap)], .0075, 6), 'chrome', True, closed=True)
        b.add(_lathe([(0, 0), (.02, 0), (.022, .03), (.018, .05), (0, .05)], 10), 'plastic_white', True, closed=True,
              T=Tr(x + .035, yp, .045))

# ----------------------------------------------------------------------------- plants (alpha-free leaves)
def _pot(b, dia, h, m):
    rt, rb = dia / 2, dia * .39
    b.add(_lathe([(0, 0), (rb, 0), (rt, h * .9), (rt * 1.04, h * .9), (rt * 1.04, h), (rt * .93, h), (rt * .9, h * .9)], 20), m, True)
    b.add(_lathe([(rt * .9, h * .9), (0, h * .9)], 20), 'soil')


def _leaf_monstera(s):
    """Split heart leaf of length ~s: base notch at the origin, tip toward +Y, face +Z, folded on the midrib."""
    c = Vector((0, .2 * s)); half = []
    for a, r in ((0, .2), (22, .44), (44, .5), (56, .5), (60, .2), (64, .5), (80, .52), (91, .52), (95, .22), (99, .54),
                 (115, .56), (126, .56), (130, .24), (134, .6), (156, .66), (180, .8)):
        half.append((r * s * sin(radians(a)), c.y - r * s * cos(radians(a))))
    z = lambda x, y: .2 * abs(x) - .15 * (y - c.y) ** 2 / s
    vs = [(0, c.y, 0)] + [(x, y, z(x, y)) for x, y in half] + [(-x, y, z(x, y)) for x, y in half]
    n = len(half)
    return G(vs, [(0, i, i + 1) for i in range(1, n)] + [(0, n + i + 1, n + i) for i in range(1, n)])


def _leaf_strap(L, W, bend):
    """Arching strap leaf from the origin along +Y bending toward -Z; 3 strips across (margin, centre, margin)."""
    vs, y, z = [], 0.0, 0.0
    for i, wk in enumerate((.45, 1, 1, .85, .5, .06)):
        a = bend * (i / 5) ** 1.4; w = W / 2 * wk
        vs += [(-w, y, z), (-w * .45, y, z - .12 * w), (w * .45, y, z - .12 * w), (w, y, z)]
        y += cos(a) * L / 5; z -= sin(a) * L / 5
    return G(vs, [(i * 4 + k, i * 4 + k + 1, i * 4 + k + 5, i * 4 + k + 4) for i in range(5) for k in range(3)])


@_prop
def plant_potted(b, kind='monstera', height=None, spread=None, pot_dia=.2, pot_h=.18, pot_mat='terracotta', seed=1,
                 leaves=None, stand=0.0, stand_mat='dark_oak_antique'):
    """Pot plant with solid low-poly leaves (single-sided - leaf materials must be double-sided).
    kind: 'monstera' (split leaves on arching stems) | 'dracaena' (two canes, striped strap rosettes) |
    'citrus' (bare stem, round leafy head, fruit) | 'eucalyptus' (sparse drooping stems, round leaves).
    height / spread = overall size incl. pot (defaults per kind); stand = height of a low wooden stand.
    Origin: floor centre."""
    H, S, N = {'monstera': (.6, .55, 9), 'dracaena': (1.1, .75, 44), 'citrus': (1.75, .7, 520), 'eucalyptus': (.5, .35, 7)}[kind]
    H, S, N = (height or H) - stand, spread or S, leaves or N
    rnd = random.Random(seed); zs = pot_h * .9
    LG, LM, LL, LY = (two_sided(k) for k in ('leaf_green', 'leaf_mid', 'leaf_lime', 'leaf_grey'))
    if stand:
        b.add(_lathe([(0, 0), (pot_dia * .55, 0), (pot_dia * .55, stand), (0, stand)], 14), stand_mat, True, closed=True)
    with b.at(Tr(0, 0, stand)):
        _pot(b, pot_dia, pot_h, pot_mat)
        if kind == 'monstera':
            for i in range(N):
                az = tau * (i + rnd.uniform(-.3, .3)) / N; s = rnd.uniform(.3, .42) * S
                R = max(.02, (S / 2 - s * .7) * rnd.uniform(.5, 1)); top = zs + (H - zs) * rnd.uniform(.5, 1)
                d = Vector((cos(az), sin(az), 0)); end = d * R + Vector((0, 0, top))
                pts = _bez((0, 0, zs), d * (R * .1) + Vector((0, 0, zs + (top - zs) * .7)), d * (R * .6) + Vector((0, 0, top + .03)), end, 6)
                b.add(_tube(pts, .004, 4), 'leaf_mid', True, closed=True)
                b.add(_leaf_monstera(s), LG, True, T=Tr(*end) @ Rot('Z', math.degrees(az) - 90) @ Rot('X', -rnd.uniform(0, 30)))
        elif kind == 'dracaena':
            for ci, (cx, cy, fr) in enumerate(((-.035, 0, .6), (.04, .015, .85))):
                C = Vector((cx * 1.6, cy, zs + (H - zs) * fr - S * .12))
                b.add(_tube([(cx, cy, zs), (cx * 1.3, cy, (zs + C.z) / 2), C], .014, 6), 'bark', True, closed=True)
                n = N // 2
                for j in range(n):
                    t = j / (n - 1); L = S * rnd.uniform(.42, .55)
                    T = Tr(*C) @ Rot('Z', j * 137.5 + ci * 40) @ Rot('X', 82 - 80 * t ** .8)
                    b.add(_leaf_strap(L, .05, radians(75)), [LL, LG, LL] * 5, True, T=T)
        elif kind == 'citrus':
            R = S / 2; C = Vector((0, 0, H - R)); zt = C.z - R * .55
            b.add(_tube([(0, 0, zs), (.012, 0, zs + (zt - zs) * .5), (0, .008, zt)], [.014, .012, .01], 6), 'bark', True, closed=True)
            for _ in range(7):
                d = Vector((rnd.gauss(0, 1), rnd.gauss(0, 1), abs(rnd.gauss(0, 1)) + .3)).normalized()
                b.add(_tube([(0, .008, zt), Vector((0, 0, zt)) + d * R * .35, C + d * R * .7], [.007, .005, .003], 4), 'bark', True, closed=True)
            for i in range(N):
                d = Vector((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(.15, 1))).normalized()
                p = C + d * (R * rnd.uniform(.12, 1) ** .5); L = rnd.uniform(.065, .1); w = L * .3
                T = Tr(*p) @ d.to_track_quat('Y', 'Z').to_matrix().to_4x4() @ Rot('Y', rnd.uniform(0, 360)) @ Rot('X', rnd.uniform(-60, 25))
                b.add(G([(0, 0, 0), (w, L / 2, .2 * w), (0, L, 0), (-w, L / 2, .2 * w)], [(0, 1, 2), (0, 2, 3)]),
                      LM if i % 5 else LG, True, T=T)
            for i in range(8):
                d = Vector((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.uniform(-1, .3))).normalized()
                b.add(_sphere(.019, 6, 4), 'fruit_orange', True, closed=True, T=Tr(*(C + d * R * .85)))
        else:
            hexa = G([(0, 0, 0)] + [(.017 * cos(tau * k / 6), .017 * sin(tau * k / 6), 0) for k in range(6)],
                     [(0, k + 1, (k + 1) % 6 + 1) for k in range(6)])
            for i in range(N):
                az = tau * (i + rnd.uniform(-.3, .3)) / N; d = Vector((cos(az), sin(az), 0)); R = S / 2 * rnd.uniform(.5, 1)
                top = zs + (H - zs) * rnd.uniform(.6, 1)
                pts = _bez((0, 0, zs), d * (R * .15) + Vector((0, 0, top * .8)), d * (R * .7) + Vector((0, 0, top + .04)),
                           d * R + Vector((0, 0, top - .06)), 8)
                b.add(_tube(pts, .002, 3), 'leaf_grey', True, closed=True)
                for k in range(2, 9):
                    for sg in (-1, 1):
                        T = Tr(*pts[k]) @ Rot('Z', math.degrees(az) + 90) @ Rot('Y', rnd.uniform(-50, 50)) @ Tr(sg * .02, 0, 0)
                        b.add(hexa, LY, True, T=T)


# ----------------------------------------------------------------------------- light fittings
def _candle(b, h, dia, sleeve, lit, T=None, watts=0.0, kelvin=2700):
    r = dia / 2; z0 = h + .003; R = r * .95
    with b.at(T if T is not None else Matrix.Identity(4)):
        b.add(_lathe([(0, 0), (r, 0), (r, h), (r * .5, z0), (0, z0)], 8), sleeve, True, closed=True)
        prof = [(0, z0), (R * .55, z0 + .004), (R, z0 + .018), (R * .9, z0 + .03), (R * .45, z0 + .045), (R * .12, z0 + .058), (0, z0 + .062)]
        b.add(_lathe(prof, 8), emissive('#FFD9A0', 6.0) if lit else 'glass_frosted', True, closed=True)
        b.bulbs.append(b.T @ Vector((0, 0, h + .035)))
        if watts:                                    # emitter sits 2.5 cm above the lamp tip, clear of the mesh
            b.kid(lambda: _light('POINT', watts, kelvin, .012), Tr(0, 0, h + .09))


@_prop
def candle_bulb(b, height=.09, dia=.025, sleeve='ivory', lit=True, watts=0.0, kelvin=2700):
    """Candle sleeve + flame-tip lamp (emissive when lit).  watts > 0 adds a child POINT light [H].
    Origin: base centre of the sleeve; total height = height + 0.065."""
    _candle(b, height, dia, sleeve, lit, None, watts, kelvin)


def _shade(b, top, bottom, height, style, color, lit, trim, panels=6, T=None):
    seg = {'pleated': 32, 'scalloped': 4 * panels, 'panel': panels}.get(style, 16)

    def fn(u, v):
        t = tau * u; r = (bottom + (top - bottom) * v) / 2
        if style == 'pleated':
            r *= 1 + .035 * (1 if round(u * seg) % 2 else -1)
        z = v * height
        if style == 'scalloped':
            z -= .014 * (1 - v) ** 3 * (.5 - .5 * cos(panels * t))
        return (r * cos(t), r * sin(t), z)
    m = emissive(color, 1.6) if lit else two_sided(color)
    with b.at(T if T is not None else Matrix.Identity(4)):
        b.add(_grid(fn, seg, 3 if style == 'scalloped' else 1), m, style != 'panel')
        if trim:
            for z, r in ((0 if style != 'scalloped' else .003, bottom / 2), (height - .006, top / 2)):
                b.add(_lathe([(r + .0015, z), (r + .0015, z + .006)], 16), trim, True)


@_prop
def lampshade(b, top_dia=.07, bottom_dia=.15, height=.13, style='scalloped', color='#F0E6CF', lit=True,
              trim='tassel_gold', panels=6):
    """Fabric shade (open cone).  style: 'empire'/'drum' (smooth) | 'panel' (flat panels) | 'pleated' |
    'scalloped' (wavy lower edge).  lit=True -> softly emissive.  trim = braid material or None.
    Origin: centre of the bottom rim."""
    _shade(b, top_dia, bottom_dia, height, style, color, lit, trim, panels)


def _drop(b, L, kind='spear', m='glass_clear', T=None):
    if kind == 'ball':
        b.add(_sphere(L / 2, 6, 4), m, closed=True, T=(T if T is not None else Matrix.Identity(4)) @ Tr(0, 0, -L / 2)); return
    prof = {'spear': [(0, -L), (L * .14, -L * .7), (L * .07, -L * .2), (L * .07, -L * .12), (0, 0)],
            'tear': [(0, -L), (L * .2, -L * .82), (L * .24, -L * .65), (L * .12, -L * .3), (L * .03, -L * .08), (0, 0)]}[kind]
    b.add(_lathe(prof, 4 if kind == 'spear' else 6), m, closed=True, T=T)


@_prop
def crystal_drop(b, length=.06, kind='spear', mat='glass_clear'):
    """Faceted crystal pendant: 'spear' | 'tear' | 'ball'.  Origin: hanging point (top)."""
    _drop(b, length, kind, mat)


@_prop
def bead_swag(b, span=.3, sag=.06, bead=.01, mat='glass_clear'):
    """String of faceted beads sagging from the origin to (span, 0, 0)."""
    n = max(3, int(hypot(span, 2 * sag) / (bead * 1.05)))
    for i in range(n + 1):
        t = i / n
        b.add(_lathe([(0, -bead / 2), (bead / 2, 0), (0, bead / 2)], 4), mat, closed=True, T=Tr(span * t, 0, -4 * sag * t * (1 - t)))


def _arm(b, reach, rise, dip, m, pan=.055, candle=.09, bobeche=0.0, drops=6, drop_len=.06, shade=None, pendant=0.0,
         lit=True, scroll=True, r=.006, watts=0.0, kelvin=2700):
    """S-scroll arm in the local XZ plane from the origin to a candle at (reach, 0, rise)."""
    pts = _bez((0, 0, 0), (reach * .35, 0, -dip * 2.2), (reach * 1.02, 0, -dip * 1.6), (reach, 0, rise - .012), 18)
    b.add(_tube(pts, [r * (1.25 - .45 * i / 18) for i in range(19)], 6, up=(0, 1, 0)), m, True, closed=True)
    if scroll:
        sp = [(reach * .1 + (.03 - .0022 * i) * cos(-pi / 2 - i * .55), 0, -dip * .5 + .03 + (.03 - .0022 * i) * sin(-pi / 2 - i * .55))
              for i in range(11)]
        b.add(_tube(sp, [r * (.9 - .05 * i) for i in range(11)], 4, up=(0, 1, 0)), m, True, closed=True)
    pr = pan / 2
    with b.at(Tr(reach, 0, rise)):
        b.add(_lathe([(0, -.014), (.007, -.014), (.007, -.004), (pr * .6, -.002), (pr, .004), (pr * .96, .006), (pr * .55, .002),
                      (.014, .002), (.014, .012), (0, .012)], 10), m, True, closed=True)
        if bobeche:
            br = bobeche / 2
            b.add(_lathe([(br * .2, -.007), (br * .8, -.003), (br, .005)], 12), 'glass_clear')
            for k in range(drops):
                _drop(b, drop_len, 'spear', 'glass_clear', Tr(br * .96 * cos(tau * k / drops), br * .96 * sin(tau * k / drops), .003))
        if pendant:
            _drop(b, pendant, 'tear', 'glass_clear', Tr(0, 0, -.014))
        _candle(b, candle, .024, 'ivory', lit, Tr(0, 0, .012), watts, kelvin)
        if shade:
            top, bottom, height, style, color = shade
            _shade(b, top, bottom, height, style, color, lit, 'tassel_gold', 6, Tr(0, 0, .012 + candle - .03))


@_prop
def chandelier_arm(b, reach=.4, rise=.1, dip=.06, mat='brass', pan_dia=.055, candle_h=.09, bobeche_dia=0.0, drops=6,
                   drop_len=.06, shade=None, pendant=0.0, lit=True, scroll=True, watts=0.0, kelvin=2700):
    """One complete chandelier light: S-scroll arm + drip pan + candle sleeve + flame lamp, optional glass
    bobeche dish with `drops` spear crystals, tear pendant, and clip-on shade = (top_dia, bottom_dia, height,
    style, colour).  Instance it N times round the hub (identical args share one mesh).
    watts > 0 adds a child POINT light above the lamp [H].
    Origin: hub attachment; the arm extends along +X and ends at (reach, 0, rise)."""
    _arm(b, reach, rise, dip, mat, pan_dia, candle_h, bobeche_dia, drops, drop_len, shade, pendant, lit, scroll,
         watts=watts, kelvin=kelvin)


@_prop
def chandelier(b, dia=.8, drop=.55, arms=8, upper_arms=4, upper_dia=.44, upper_rise=.12, mat='brass', body='column',
               shade=None, crystals=True, rise=.1, watts=0.0, kelvin=2700, lit=True):
    """[H] Two-tier candle chandelier: ceiling cup, turned stem, hub, bottom finial (root mesh) + linked
    chandelier_arm children (lower tier on `dia`, upper tier on `upper_dia`) and bead swags between the lower
    arm tips.  watts = radiometric watts PER LAMP (child POINT lights; 0 = none, then add emitters with
    lighting.bulb() at props.bulb_points(root)).  body: 'column' (crystal column + crystal ball
    finial) | 'bowl' (dished brass bowl + acorn finial).  shade as chandelier_arm.  drop = ceiling to the
    lowest point.  Origin: ceiling contact, hangs -Z."""
    zh = -drop + .13; m = mat
    b.add(_lathe([(0, -.04), (.02, -.04), (.05, -.022), (.06, -.006), (.06, 0), (0, 0)], 16), m, True, closed=True)
    stem = [(0, zh), (.012, zh)] + [(r, zh + (-.04 - zh) * t) for t, r in
                                    ((.1, .012), (.18, .02), (.3, .026), (.45, .016), (.6, .011), (.72, .02), (.8, .011), (1, .009))] + [(0, -.04)]
    b.add(_lathe(stem, 10), m, True, closed=True)
    b.add(_sphere(.04, 10, 6, .8), m, True, closed=True, T=Tr(0, 0, zh))
    if upper_arms:
        b.add(_sphere(.03, 10, 6, .8), m, True, closed=True, T=Tr(0, 0, zh + upper_rise))
    if body == 'bowl':
        b.add(_lathe([(0, zh - .05), (.03, zh - .05), (.1, zh - .03), (.14, zh), (.132, zh + .006), (.09, zh - .018), (0, zh - .03)], 16), m, True, closed=True)
        b.add(_lathe([(0, zh - .13), (.012, zh - .115), (.022, zh - .09), (.012, zh - .07), (.016, zh - .055), (0, zh - .05)], 10), m, True, closed=True)
    else:
        b.add(_lathe([(0, zh + .04), (.03, zh + .04), (.034, zh + .1), (.026, zh + .2), (0, zh + .2)], 8), 'glass_clear', closed=True)
        b.add(_lathe([(0, zh - .045), (.012, zh - .045), (.012, zh - .03), (0, zh - .03)], 8), m, True, closed=True)
        _drop(b, .05, 'ball', 'glass_clear', Tr(0, 0, zh - .04)); _drop(b, .04, 'tear', 'glass_clear', Tr(0, 0, zh - .09))
    cr = dict(bobeche_dia=.11, drops=6) if crystals else {}
    lo = dict(reach=dia / 2, rise=rise, mat=m, shade=shade, lit=lit, pendant=.05 if crystals else 0, watts=watts, kelvin=kelvin, **cr)
    up = dict(reach=upper_dia / 2, rise=rise, dip=.04, mat=m, shade=shade, lit=lit, watts=watts, kelvin=kelvin, **cr)
    for k in range(arms):
        b.kid(lambda a=lo: chandelier_arm(**a), Tr(0, 0, zh) @ Rot('Z', 360 * k / arms))
    for k in range(upper_arms):
        b.kid(lambda a=up: chandelier_arm(**a), Tr(0, 0, zh + upper_rise) @ Rot('Z', 360 * (k + .5) / upper_arms + 180 / arms))
    if crystals and arms > 2:
        R = dia / 2; chord = 2 * R * sin(pi / arms)
        for k in range(arms):
            a = tau * k / arms
            b.kid(lambda c=chord: bead_swag(c, c * .22), Tr(R * cos(a), R * sin(a), zh + rise - .012) @ Rot('Z', math.degrees(a) + 90 + 180 / arms))


@_prop
def sconce(b, arms=2, width=.36, height=.33, projection=.16, mat='brass', shade=None, lit=True, watts=0.0, kelvin=2700):
    """Candle wall bracket: oval backplate with urn finial + `arms` S-arms each carrying drip pan, candle,
    flame lamp and optional shade (as chandelier_arm).  watts > 0 adds a child POINT light per lamp [H].
    Origin: wall, backplate centre.  Overall ~width x height x projection."""
    b.add(_sphere(1, 10, 5), mat, True, closed=True, T=Tr(0, -.012, 0) @ Sc(.035, .012, .06))
    b.add(_lathe([(0, .05), (.008, .055), (.016, .075), (.008, .09), (.004, .1), (0, .105)], 8), mat, True, closed=True, T=Tr(0, -.018, 0))
    cand = max(.05, height - .25) if shade else max(.05, height - .2)
    for k in range(arms):
        tx = (k / (arms - 1) - .5) * (width - .06) if arms > 1 else 0.0
        ty = -(projection - .042) * (1 if arms < 3 else .6 + .4 * (1 - abs(tx) / (width / 2)))
        with b.at(Tr(0, -.012, 0) @ Rot('Z', math.degrees(atan2(ty, tx)))):
            _arm(b, hypot(tx, ty), .04, .035, mat, .05, cand, shade=shade, lit=lit, scroll=False, r=.005, watts=watts, kelvin=kelvin)

# ----------------------------------------------------------------------------- books, soft furnishings
_BOOKS = ['#5A1E1E', '#1F3A2E', '#2A2F4A', '#6B4A2A', '#8A7A5A', '#3A2A20', '#7A2E2A', '#4A4A3A', '#C9B88A', '#22303A']


@_prop
def book_row(b, length=.8, height=.22, depth=.15, seed=0, fill=1.0, palette=None):
    """Row of upright books with varied thickness / height / depth / colour and gilt spine bands; the last
    book leans when there is room.  Same (length, height, depth, seed) -> shared mesh.
    Origin: shelf surface, centre of the row; spines face -Y at y = -depth, backs toward y = 0."""
    rnd = random.Random(seed); pal = palette or _BOOKS; x = -length / 2; end = x + length * fill
    while True:
        t = rnd.uniform(.016, .045)
        if x + t > end:
            break
        h, d, col = height * rnd.uniform(.72, 1), depth * rnd.uniform(.78, 1), rnd.choice(pal)
        yf = -depth + rnd.uniform(0, .008)
        lean = end - (x + t) < .016 and end - (x + t) > .006
        with b.at(Tr(x + t, 0, 0) @ Rot('Y', 9) @ Tr(-t, 0, 0) if lean else Tr(x, 0, 0)):
            b.add(_box((0, yf, 0), (t - .0008, yf + d, h)), col)
            if rnd.random() < .6:
                for zb in (.8, .86) if rnd.random() < .5 else (.82,):
                    b.add(G([(.001, yf - .0004, h * zb), (t - .002, yf - .0004, h * zb), (t - .002, yf - .0004, h * zb + .006),
                             (.001, yf - .0004, h * zb + .006)], [(0, 1, 2, 3)]), 'gilt')
        x += t


@_prop
def cushion(b, w=.45, h=.45, thickness=.14, mat='velvet_orange', piping=None, res=8):
    """Scatter cushion (pillow shape: plump middle, pinched seam, pointed corners).  piping = cord material.
    Origin: centre of the underside, lying flat on z=0 (w along X, h along Y)."""
    def side(sg):
        def f(u, v):
            a, c = 2 * u - 1, 2 * v - 1
            z = thickness / 2 * ((1 - abs(a) ** 2.5) * (1 - abs(c) ** 2.5)) ** .45
            return (a * w / 2 * (1 - .06 * (1 - c * c)), c * h / 2 * (1 - .06 * (1 - a * a)), thickness / 2 + sg * z)
        return f
    uv = lambda u, v: (u * w, v * h)
    b.add(_grid(side(1), res, res, uv), mat, True); b.add(_grid(side(-1), res, res, uv, flip=True), mat, True)
    if piping:
        f = side(1); n = res
        pts = [f(i / n, 0) for i in range(n)] + [f(1, i / n) for i in range(n)] + [f(1 - i / n, 1) for i in range(n)] + [f(0, 1 - i / n) for i in range(n)]
        b.add(_tube(pts, .004, 4, loop=True), piping, True)


@_prop
def bolster(b, dia=.17, length=.4, mat='velvet_orange', button='rope_cream'):
    """Cylindrical bolster with gathered ends and covered buttons.  Origin: centre of the underside, axis X."""
    r, L = dia / 2, length / 2
    prof = [(0, -L + .012), (r * .3, -L + .006), (r * .8, -L), (r, -L + .03), (r, L - .03), (r * .8, L), (r * .3, L - .006), (0, L - .012)]
    with b.at(Tr(0, 0, r) @ Rot('Y', 90)):
        b.add(_lathe(prof, 14), mat, True, closed=True)
        for sg in (-1, 1):
            b.add(_sphere(.013, 6, 4, .6), button, True, closed=True, T=Tr(0, 0, sg * (L - .012)))


@_prop
def upholstered_seat(b, w=.5, d=.45, thickness=.08, style='plain', mat='velvet_orange', buttons=(4, 2), crown=.012,
                     edge=None, piping=None, gimp=None):
    """Upholstered pad with soft rounded top edges and a crowned top.  style 'plain' | 'buttoned' (deep-buttoned
    top: buttons=(across, deep) dimples + covered buttons).  piping = welt-cord material round the top edge,
    gimp = braid material round the bottom edge.  Origin: bottom centre."""
    T_, e = thickness, edge or min(.03, thickness * .45)
    prof = [(0, 0), (0, T_ - e), (.13 * e, T_ - .5 * e), (.5 * e, T_ - .13 * e), (e, T_)]
    but = style == 'buttoned'

    def axis(n, half):
        return [(-half + o, z) for o, z in prof] + [(-half + e + (2 * half - 2 * e) * i / n, T_) for i in range(1, n)] + \
               [(half - o, z) for o, z in reversed(prof)]
    X, Y = axis(buttons[0] * 4 if but else 6, w / 2), axis(buttons[1] * 4 if but else 6, d / 2)
    bp = [(-w / 2 + w * (i + .5) / buttons[0], -d / 2 + d * (j + .5) / buttons[1]) for i in range(buttons[0]) for j in range(buttons[1])] if but else []

    def top(x, y):
        z = T_ + crown * (1 - (2 * x / w) ** 2) * (1 - (2 * y / d) ** 2)
        return z - sum(.022 * math.exp(-((x - px) ** 2 + (y - py) ** 2) / .0007) for px, py in bp)
    nx, ny = len(X), len(Y)
    vs = [(x, y, top(x, y) if min(zx, zy) >= T_ else min(zx, zy)) for (y, zy) in Y for (x, zx) in X]
    fs = [(j * nx + i, j * nx + i + 1, (j + 1) * nx + i + 1, (j + 1) * nx + i) for j in range(ny - 1) for i in range(nx - 1)
          if not (i in (0, nx - 2) and j in (0, ny - 2))]
    b.add(G(vs, fs), mat, True)
    for px, py in bp:
        b.add(_sphere(.009, 6, 3, .5), mat, True, closed=True, T=Tr(px, py, top(px, py) + .002))
    if piping:
        b.add(_tube([(x, y, T_ - e * .6) for x, y in _rrect(w + .004, d + .004, .006, 2)], .0045, 4, loop=True), piping, True)
    if gimp:
        for sx, sy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            hx, hy = (w / 2 + .0015, d / 2 + .0015)
            lo = (sx * hx - .0015 if sx else -hx, sy * hy - .0015 if sy else -hy, .001)
            hi = (sx * hx + .0015 if sx else hx, sy * hy + .0015 if sy else hy, .013)
            b.add(_box(tuple(min(a, c) for a, c in zip(lo, hi)), tuple(max(a, c) for a, c in zip(lo, hi))), gimp)


# ----------------------------------------------------------------------------- glassware, ornaments
@_prop
def tumbler(b, height=.09, dia=.075, sides=10, mat='glass_clear'):
    """Cut-glass tumbler (faceted, thick base).  Origin: base centre."""
    r = dia / 2
    b.add(_lathe([(0, 0), (r * .86, 0), (r, height), (r * .93, height), (r * .8, .012), (0, .012)], sides), mat, closed=True)


@_prop
def wine_glass(b, height=.2, bowl_dia=.085, mat='glass_clear'):
    """Stem glass.  Origin: centre of the foot (standing upright; rotate 180 deg about X to hang it)."""
    r, h = bowl_dia / 2, height
    b.add(_lathe([(0, 0), (r * .85, 0), (r * .8, .003), (.006, .008), (.004, h * .42), (r * .55, h * .5), (r, h * .72), (r * .84, h)], 12),
          mat, True)


@_prop
def decanter(b, height=.3, kind='square', mat='glass_clear', liquid='whisky', level=.55):
    """Cut-crystal decanter with faceted ball stopper.  kind 'square' | 'round'; liquid = material or None.
    Origin: base centre."""
    H = height; bh = H * .58; seg = 4 if kind == 'square' else 10; R = H * (.165 if kind == 'square' else .2)
    body = [(0, 0), (R * .95, 0), (R, bh * .06), (R, bh * .82), (R * .7, bh * .97), (R * .3, bh)] if kind == 'square' else \
           [(0, 0), (R * .6, 0), (R * .95, bh * .25), (R, bh * .45), (R * .8, bh * .8), (R * .3, bh)]
    T = Rot('Z', 45) if kind == 'square' else None
    b.add(_lathe(body, seg), mat, kind != 'square', T=T)
    if liquid:
        b.add(_lathe([(r * .9, z + .004) for r, z in body if z <= bh * level] + [(0, bh * level)], seg), liquid, T=T)
    b.add(_lathe([(R * .3, bh), (.016, bh + H * .04), (.014, H * .8), (.022, H * .82), (.012, H * .82)], 8), mat, True)
    b.add(_lathe([(0, H * .8), (.011, H * .8), (.011, H * .85), (0, H * .85)], 6), mat, closed=True)
    _drop(b, H * .15, 'ball', mat, Tr(0, 0, H))


@_prop
def glassware_set(b, tumblers=6, with_decanter=True, tray=(.5, .35), tray_mat='silver', glass_h=.09):
    """[H] Oval gallery tray with `tumblers` linked tumblers and a decanter.  Origin: centre of the tray base."""
    a, c = tray[0] / 2, tray[1] / 2
    b.add(_lathe([(0, 0), (.96, 0), (1, .004), (1, .022), (.985, .022), (.975, .006), (0, .006)], 28), tray_mat, True, closed=True, T=Sc(a, c, 1))
    if with_decanter:
        b.kid(lambda: decanter(), Tr(-a * .55, 0, .006))
    x0 = -a * .1 if with_decanter else -a * .6
    cols = max(1, (tumblers + 1) // 2)
    for i in range(tumblers):
        b.kid(lambda: tumbler(glass_h), Tr(x0 + (a * .85 - x0) * ((i // 2) + .5) / cols * (1 if cols > 1 else .5), (-.5 + (i % 2)) * c * .8, .006))


def _dial(b, r, face, hands='plastic_dark', bezel='brass', T=None, show_hands=True):
    """Clock dial in the local XY plane facing +Z."""
    with b.at(T if T is not None else Matrix.Identity(4)):
        b.add(_lathe([(r, 0), (0, 0)], 16), face)
        if bezel:
            b.add(_lathe([(r * .98, 0), (r * 1.1, 0), (r * 1.12, .004), (r * 1.02, .008), (r * .98, .003), (r * .98, 0)], 16), bezel, True, closed=True)
        for k in range(12):
            b.add(_box((-.006 * r / .05, r * .72, .0003), (.006 * r / .05, r * .9, .001)), hands, T=Rot('Z', 30 * k))
        for ang, L, wd in ((60, .5, .05), (-60, .78, .035)) if show_hands else ():
            b.add(_box((-r * wd, -r * .1, .0012), (r * wd, r * L, .002)), hands, T=Rot('Z', ang))


@_prop
def mantel_clock(b, w=.32, d=.16, h=.37, style='slate', mat=None, dial_dia=None, hands=True):
    """Mantel clock.  style 'slate' (black architectural case: stepped plinth, green colonnettes, stepped
    top with low dome, cream dial in a brass bezel) | 'bracket' (wooden bracket clock: stepped top, brass
    carrying handle, square brass dial with silvered chapter ring).  Origin: bottom centre, front -Y.
    hands=False leaves the dial bare for live `clock_hands` (centre + radius: `mantel_clock_dial`)."""
    def bx(ww, dd, z0, z1, m, bev=.003):
        b.add(_box((-ww / 2, -dd / 2, z0 * h), (ww / 2, dd / 2, z1 * h), bev), m, closed=True)
    if style == 'slate':
        m = mat or 'slate_black'; r = (dial_dia or .34 * w) / 2
        bx(w, d, 0, .07, m); bx(w * .93, d * .93, .07, .12, m); bx(w * .7, d * .74, .12, .72, m)
        for sx in (-1, 1):
            for sy in (-1, 1):
                b.add(_lathe(turned_profile('column', .6 * h, .1 * w, .12 * h), 8), 'marble_green', True, T=Tr(sx * w * .405, sy * d * .37, 0))
        bx(w * .92, d * .92, .72, .79, m); bx(w * .74, d * .74, .79, .86, m); bx(w * .5, d * .52, .86, .91, m)
        b.add(_sphere(1, 12, 4, 1), m, True, closed=True, T=Tr(0, 0, .91 * h) @ Sc(w * .2, d * .2, .09 * h))
        _dial(b, r, 'dial_cream', T=Tr(0, -d * .37 - .0005, .44 * h) @ Rot('X', 90), show_hands=hands)
    else:
        m = mat or 'mahogany'; s = min(w * .62, h * .5)
        bx(w, d, 0, .08, m); bx(w * .88, d * .86, .08, .76, m); bx(w * .96, d * .94, .76, .81, m)
        bx(w * .72, d * .7, .81, .88, m); bx(w * .46, d * .46, .88, .93, m)
        b.add(_tube([(-w * .14 * cos(pi * i / 8), 0, h * .93 + .06 * h * sin(pi * i / 8)) for i in range(9)], .004, 5), 'brass', True, closed=True)
        with b.at(Tr(0, -d * .43 - .0005, .43 * h) @ Rot('X', 90)):
            b.add(_box((-s / 2, -s / 2, 0), (s / 2, s / 2, .002)), 'brass')
            _dial(b, s * .43, 'silver', bezel=None, T=Tr(0, 0, .0022), show_hands=hands)


def mantel_clock_dial(w=.32, d=.16, h=.37, style='slate', dial_dia=None):
    """-> (centre, radius) of the dial of `mantel_clock(w, d, h, style, dial_dia=dial_dia)`: centre = Vector on
    the dial face in the clock's local frame (the dial looks along local -Y)."""
    if style == 'slate':
        return Vector((0, -d * .37 - .0005, .44 * h)), (dial_dia or .34 * w) / 2
    return Vector((0, -d * .43 - .0027, .43 * h)), min(w * .62, h * .5) * .43


_VASES = {   # (r / (dia/2), z / height) outer profile, bottom -> mouth
    'baluster': [(0, 0), (.5, 0), (.55, .03), (.42, .08), (1, .4), (.95, .55), (.5, .8), (.42, .9), (.62, 1)],
    'urn': [(0, 0), (.45, 0), (.45, .04), (.2, .1), (.25, .16), (.9, .45), (1, .62), (.8, .78), (.55, .84), (.7, 1)],
    'bottle': [(0, 0), (.9, 0), (1, .05), (1, .5), (.35, .72), (.3, .95), (.4, 1)],
    'bowl': [(0, 0), (.4, 0), (.45, .08), (.9, .6), (1, 1)],
    'cylinder': [(0, 0), (.95, 0), (1, .03), (1, 1)],
    'planter': [(0, 0), (.8, 0), (.85, .04), (1, .9), (1.05, .92), (1.05, 1)],
}


@_prop
def vase(b, height=.3, dia=.16, kind='baluster', mat='ceramic_white', flowers=0,
         flower_colors=('#D9482B', '#E88A2E', '#E06A8A'), seed=0):
    """Vase / urn / bowl / planter (kind: see _VASES) with an optional bunch of `flowers` simple blooms.
    Origin: base centre."""
    P = [(r * dia / 2, z * height) for r, z in _VASES[kind]]; rt = P[-1][0]
    b.add(_lathe(P + [(rt * .88, height), (rt * .8, height * .88), (0, height * .88)], 14), mat, True)
    rnd = random.Random(seed)
    for i in range(flowers):
        az = tau * i / flowers + rnd.uniform(-.3, .3); R = rnd.uniform(.3, 1) * dia * .7; top = height * rnd.uniform(1.25, 1.6)
        end = Vector((cos(az) * R, sin(az) * R, top))
        b.add(_tube(_bez((0, 0, height * .7), (0, 0, height), end * .7 + Vector((0, 0, top * .3)), end, 4), .002, 3), 'leaf_mid', True, closed=True)
        b.add(_sphere(rnd.uniform(.022, .034), 6, 4, .7), flower_colors[i % len(flower_colors)], True, closed=True, T=Tr(*end))


@_prop
def plate(b, dia=.27, mat='ceramic_white', height=.022):
    """Rimmed dinner plate.  Origin: centre of the base, lying flat (rotate to stand it in a rack)."""
    r = dia / 2
    b.add(_lathe([(0, 0), (r * .55, 0), (r * .6, .003), (r, height), (r * .99, height + .003), (r * .62, .008), (r * .55, .005),
                  (0, .005)], 24), mat, True, closed=True)


@_prop
def human_ref(b, height=1.7, mat='skin_ref'):
    """Scale mannequin for previews (do not ship).  Origin: floor centre, facing -Y."""
    with b.at(Sc(height / 1.7)):
        b.add(_lathe([(0, .82), (.15, .84), (.17, 1.0), (.14, 1.15), (.19, 1.38), (.2, 1.44), (.07, 1.5), (.055, 1.54), (0, 1.54)], 10),
              mat, True, closed=True, T=Sc(1, .6, 1))
        b.add(_sphere(.095, 10, 6, 1.1), mat, True, closed=True, T=Tr(0, 0, 1.6))
        for sx in (-1, 1):
            b.add(_tube([(sx * .09, 0, .9), (sx * .1, 0, .5), (sx * .1, 0, .06)], [.085, .06, .045], 8), mat, True, closed=True)
            b.add(_box((sx * .1 - .05, -.17, 0), (sx * .1 + .05, .08, .07), .02), mat, closed=True)
            b.add(_tube([(sx * .22, 0, 1.41), (sx * .25, 0, 1.12), (sx * .26, -.03, .84)], [.048, .04, .034], 8), mat, True, closed=True)

# ----------------------------------------------------------------------------- interaction parts (blender/INTERACT.md)
@_prop
def water_stream(b, height, dia=.012, splash=.06):
    """Running water for `show when=1 fx='water'`: a thin round stream from the origin (the spout outlet) straight
    down to z = -height, necking to 60 % of `dia` over the first 0.15 m, plus a flat splash disc `splash` across
    0.5 mm above the foot (0 = none).  Material 'water' (alpha-blended, double-sided).
    UVs: U once round the stream; V runs along the fall, 0 at the foot and +1 per 0.1 m up to the outlet (the
    viewer scrolls V downward); the disc carries on from V = 0 at its centre to negative V at its rim."""
    r0, n, k = dia / 2, 8, max(3, min(12, round(height / .04)))

    def fn(u, v):
        r = r0 * (1 - .4 * _sm(v * height / .15)); a = tau * u
        return (r * cos(a), r * sin(a), -v * height)
    b.add(_grid(fn, n, k, lambda u, v: (u, (1 - v) * height / .1), flip=True), 'water', 100)
    if splash:
        R, z, m = splash / 2, -height + .0005, 12
        vs = [(0, 0, z)] + [(R * cos(tau * i / m), R * sin(tau * i / m), z) for i in range(m)]
        fs = [(0, 1 + i, 1 + (i + 1) % m) for i in range(m)]
        b.add(G(vs, fs, fuv=[[((i + .5) / m, 0), (i / m, -R / .1), ((i + 1) / m, -R / .1)] for i in range(m)]), 'water')


@_prop
def flame_ring(b, dia=.07, n=24, h=.014):
    """Gas-burner flames for `show when=1 fx='flame'`: a crown of `n` small pointed flames on a circle `dia`
    across, `h` high, leaning outward.  Origin: centre of the burner at the foot of the flames (set it just
    above the burner cap), +Z up.  Material 'flame_blue': emissive blue, double-sided.
    UVs per flame: V = 0 at the foot, 1 at the tip.  4 triangles per flame."""
    m = _emit('flame_blue', '#0A1433', '#3D6BFF', 6.0); m.use_backface_culling = False
    R, w = dia / 2, min(.8 * pi * dia / n, h) / 2
    vs, fs, fuv = [], [], []
    for i in range(n):
        a = tau * i / n; c, s_ = cos(a), sin(a); o = len(vs)
        vs += [((R - .6 * w) * c, (R - .6 * w) * s_, 0), (R * c - w * s_, R * s_ + w * c, 0),
               ((R + .6 * w) * c, (R + .6 * w) * s_, 0), (R * c + w * s_, R * s_ - w * c, 0),
               ((R + .35 * h) * c, (R + .35 * h) * s_, h)]
        for j in range(4):
            fs.append((o + j, o + (j + 1) % 4, o + 4)); fuv.append([(0, 0), (1, 0), (.5, 1)])
    b.add(G(vs, fs, fuv=fuv), m)


_HANDS = {   # outline (x, z) in units of the dial radius, counter-clockwise seen from the front, pointing at 12
    ('baton', 'h'): [(-.05, -.10), (.05, -.10), (.035, .50), (-.035, .50)],
    ('baton', 'm'): [(-.035, -.12), (.035, -.12), (.022, .80), (-.022, .80)],
    ('spade', 'h'): [(-.035, -.10), (.035, -.10), (.028, .26), (.085, .36), (.05, .44), (0, .52), (-.05, .44), (-.085, .36),
                     (-.028, .26)],
    ('spade', 'm'): [(-.028, -.12), (.028, -.12), (.022, .52), (.05, .60), (0, .80), (-.05, .60), (-.022, .52)],
    's': [(-.012, -.22), (.012, -.22), (.006, .85), (-.006, .85)],
}
_HAND_Y = {'h': (-.0025, -.0015, .075), 'm': (-.004, -.003, .06), 's': (-.005, -.0045, .045)}   # front y, back y, hub radius


@_prop
def _clock_hand(b, radius, style, which, mat):
    y0, y1, hub = _HAND_Y[which]
    b.add(_prism([(x * radius, z * radius) for x, z in _HANDS.get((style, which)) or _HANDS[which]], y0, y1), mat, closed=True)
    b.add(_lathe([(0, 0), (hub * radius, 0), (hub * radius, y1 - y0), (0, y1 - y0)], 10), mat, T=Tr(0, y1, 0) @ Rot('X', 90))


def clock_hands(radius=.1, style='baton', mat='plastic_dark', second=None, name=None):
    """Live clock hands -> (hour, minute) or (hour, minute, second): separate objects for the viewer's `clock`
    tag.  Each is modelled pointing at 12 (+Z) for a dial that faces -Y, with its origin at the dial centre ON
    the dial face (hour 1.5-2.5 mm, minute 3-4 mm, second 4.5-5 mm in front of it): give all of them the
    location of the dial centre and the rotation of the clock, e.g. P.place(hand, centre, facing=(nx, ny)).
    radius = dial radius (hour hand 0.50, minute 0.80, second 0.85 of it).  style: 'baton' plain tapered bars |
    'spade' antique spade hour hand + lance minute hand | 'sweep' batons + a red second hand.
    second=True / False overrides whether a second hand is made (default: only 'sweep')."""
    kind = 'baton' if style == 'sweep' else style
    if (kind, 'h') not in _HANDS:
        raise KeyError('clock_hands style %r: expected baton, spade or sweep' % style)
    nm = name or 'clock'
    out = [_clock_hand(radius, kind, w, mat, name='%s.hand_%s' % (nm, w)) for w in 'hm']
    if style == 'sweep' if second is None else second:
        out.append(_clock_hand(radius, kind, 's', _ML.solid('hand_red', '#B3261E', .5) if style == 'sweep' else mat,
                               name=nm + '.hand_s'))
    return tuple(out)


# ----------------------------------------------------------------------------- contact sheet (self-test)
def _test_image(path):
    """Orientation test card: red block top-left, green top-right, dark border, checker field."""
    import numpy as np
    W, H = 400, 300; yy, xx = np.mgrid[0:H, 0:W]            # row 0 = bottom of the image in Blender
    px = np.zeros((H, W, 4), np.float32); px[..., 3] = 1
    chk = ((xx // 25 + yy // 25) % 2).astype(np.float32)
    px[..., 0] = .75 - .25 * chk; px[..., 1] = .68 - .3 * chk; px[..., 2] = .5 - .3 * chk + .3 * yy / H
    bd = (xx < 20) | (xx >= W - 20) | (yy < 20) | (yy >= H - 20); px[bd, :3] = (.07, .1, .22)
    px[H - 90:H - 30, 30:90, :3] = (.8, .05, .05); px[H - 90:H - 30, W - 90:W - 30, :3] = (.05, .6, .1)
    im = bpy.data.images.new('props_testcard', W, H); im.pixels.foreach_set(px.ravel())
    im.filepath_raw = path; im.file_format = 'PNG'; im.save()
    return path


def contact_sheet(out_dir, res=(1600, 900), samples=64, only=None):
    """Lay out every prop in four bays (each with a back wall and a 1.7 m mannequin), render Cycles stills
    per bay camera into out_dir, print per-prop triangle counts, run cheap sanity asserts."""
    out_dir = os.path.abspath(out_dir); os.makedirs(out_dir, exist_ok=True)   # Blender resolves relative paths against the drive root
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene; col = sc.collection; table = []; card = _test_image(os.path.join(out_dir, 'testcard.png'))

    def put(o, x, y, z=0.0, rz=0.0, label=None, rx=0.0):
        o.location = (x, y, z); o.rotation_euler = (radians(rx), 0, radians(rz))
        for q in family(o):
            col.objects.link(q)
        if label:
            table.append((label, o))
        return o
    put(box(40, 14, .1, '#B9B2A6'), 9, -3, -.1)
    BX = dict(A=0, B=6, C=12, D=18, E=24)
    for bx in BX.values():
        put(box(5.2, .1, 2.8, '#D9D4CA'), bx, .05, 0)
        put(human_ref(), bx + 2.35, -.5, 0, label='human_ref' if bx == 0 else None)

    # ---- bay A: turnings, cabinetry, hardware, electrical
    x = BX['A']; legs = [
        ('turned_leg baluster', turned_leg(.72, .07, 'baluster', .1, .08)),
        ('turned_leg barley_twist', turned_leg(.72, .06, 'barley_twist', .1, .1)),
        ('turned_leg barley column .11', turned_leg(.6, .11, 'barley_twist', pitch=.16)),
        ('turned_leg cup_cover', turned_leg(.73, .13, 'cup_cover', .12, .14)),
        ('turned_leg cabriole claw', turned_leg(.47, .065, 'cabriole', .1, mat='mahogany')),
        ('turned_leg cabriole pad', turned_leg(.3, .06, 'cabriole', .06, foot='pad', mat='mahogany')),
        ('turned_leg bobbin', turned_leg(.2, .09, 'bobbin', mat='mahogany')),
        ('turned_leg taper', turned_leg(.64, .04, 'taper', .08)),
        ('turned_leg vase (newel)', turned_leg(1.1, .095, 'vase', .18, .5, mat='mahogany')),
        ('baluster (stair spindle)', baluster()),
        ('lathe (custom profile)', lathe([(0, 0), (.06, 0), (.07, .02), (.02, .05), (.03, .2), (.05, .22), (0, .24)], 16)),
        ('bevel_box', bevel_box(.2, .2, .2, 'oak_worktop', .01, 2)), ('box', box(.15, .15, .15, '#8899AA'))]
    for i, (lab, o) in enumerate(legs):
        put(o, x - 2.2 + i * .3, -1.5, 0, label=lab)

    def unit(x0, w, z0, h, d, fronts, m, plinth):
        put(cabinet_carcass(w, d, h, m, plinth), x0, 0, z0, label='cabinet_carcass %gx%g' % (w, h))
        for (fx, fz, fw, fh, slab, hdl) in fronts:
            put(panel_door(fw - .003, fh - .003, mat=m, slab=slab), x0 + fx, -d, z0 + fz, label='panel_door %gx%g%s' % (fw, fh, ' slab' if slab else ''))
            if hdl == 'v':
                put(handle_bar(vertical=True), x0 + fx + fw / 2 - .055, -d - .02, z0 + fz + fh - .17)
            elif hdl == 'h':
                put(handle_bar(), x0 + fx, -d - .02, z0 + fz + fh - .045)
            elif hdl == 'k':
                put(handle_knob(), x0 + fx + fw / 2 - .05, -d - .02, z0 + fz + .08, label='handle_knob')
            elif hdl == 'c':
                put(handle_cup(finish='black'), x0 + fx, -d - .02, z0 + fz + fh / 2 - .02, label='handle_cup')
    unit(x - 1.9, .6, 0, .87, .58, [(0, .15, .6, .715, False, 'v')], 'navy_cabinet', .15)
    unit(x - 1.2, .8, 0, .87, .58, [(0, .15, .8, .27, False, 'h'), (0, .42, .8, .27, False, 'h'), (0, .69, .8, .175, True, 'h')], 'navy_cabinet', .15)
    unit(x - .45, .6, 0, .87, .58, [(0, .15, .6, .43, False, 'k'), (0, .58, .6, .28, True, 'c')], 'grey_cabinet', .15)
    put(box(2.1, .62, .03, 'marble_quartz'), x - 1.2, -.3, .88)
    unit(x - 1.7, 1.0, 1.455, .9, .3, [(-.25, 0, .5, .9, False, 'v'), (.25, 0, .5, .9, False, 'v')], 'navy_cabinet', 0)
    put(cabinet_carcass(.9, .33, 1.2, 'mahogany', .06, open_front=True, shelves=2), x + .75, 0, 0, label='cabinet_carcass open + shelves')
    for k, zz in enumerate((.078, .44, .8)):
        put(book_row(.84, .24, .2, seed=k, fill=1 if k else .8), x + .75, -.06, zz, label='book_row seed %d' % k)
    for k in range(5):
        put(plate(), x + .45 + k * .04, -.2, 1.2 + .135, rx=90, rz=90, label='plate' if k == 0 else None)
    hw = [('handle_bar antique_brass', handle_bar()), ('handle_bar black', handle_bar(finish='black')), ('handle_bar steel', handle_bar(.3, .224, finish='steel')),
          ('handle_knob', handle_knob()), ('handle_cup', handle_cup()), ('handle_lever brass', handle_lever()), ('handle_lever black', handle_lever(finish='black', hand=-1)),
          ('handle_d', handle_d()), ('handle_drop', handle_drop()), ('switch_plate 1 rocker', switch_plate()), ('switch_plate 3 rocker', switch_plate(3)),
          ('switch_plate 3 dimmer', switch_plate(3, 'dimmer')), ('switch_plate 3 push', switch_plate(3, 'push')), ('switch_plate brass toggle', switch_plate(2, 'toggle', 'brass')),
          ('socket double', socket()), ('socket single', socket(1)), ('socket brass', socket(2, finish='brass'))]
    hx = x + .95
    for i, (lab, o) in enumerate(hw):
        put(o, hx + (i % 4) * .37, 0, 1.9 - (i // 4) * .17, label=lab)
    assert handle_bar().data is handle_bar(.22, finish='antique_brass').data, 'mesh sharing broken'

    # ---- bay B: wall-hung
    x = BX['B']
    pics = [('framed_picture gilt_ornate + mount + slip', framed_picture(None, .61, .85, 'gilt_ornate', .06, mount=.11, slip=('#7A2A2A', .005)), -2.1, 1.75),
            ('framed_picture gilt_swept (image)', framed_picture(card, .66, .52, 'gilt_swept'), -1.35, 2.0),
            ('framed_picture gilt_plain', framed_picture(None, .62, .5, 'gilt_plain'), -1.35, 1.4),
            ('framed_picture gilt_bead (image, tilt 3)', framed_picture(card, .54, .7, 'gilt_bead', tilt_deg=3), -.65, 1.9),
            ('framed_picture champagne', framed_picture(None, .5, .4, 'champagne'), -.65, 1.25),
            ('framed_picture bronze_gold + mount + glass', framed_picture(None, .5, .62, 'bronze_gold', mount=.095, glass=True), -.05, 1.95),
            ('framed_picture dark_gold_slip', framed_picture(None, .4, .5, 'dark_gold_slip'), -.05, 1.3),
            ('framed_picture olive_bronze', framed_picture(None, .34, .46, 'olive_bronze'), .42, 2.0),
            ('framed_picture walnut_gold + mount', framed_picture(None, .36, .54, 'walnut_gold', mount=True), .42, 1.4),
            ('framed_picture gilt_thin + mount + glass', framed_picture(None, .42, .52, 'gilt_thin', mount=True, glass=True), .9, 2.0),
            ('framed_picture dark_wood', framed_picture(None, .3, .4, 'dark_wood'), .9, 1.45),
            ('mirror_framed gilt_ornate 1.2x.85', mirror_framed(), 1.75, 1.6),
            ('mirror_framed gilt_swept bevel', mirror_framed(.56, .84, 'gilt_swept', .06, bevel=.02), 1.75, .6)]
    for lab, o, dx, z in pics:
        put(o, x + dx, 0, z, label=lab)
    for i in range(12):
        sh = 'round' if i < 2 else 'lozenge' if i == 2 else 'heater'
        put(wall_plaque_shield(.17 if sh == 'round' else .15, .17 if sh == 'round' else .18, sh, variant=i), x - 2.2 + i * .265, 0, 2.52,
            label='wall_plaque_shield %s v%d' % (sh, i) if i in (0, 2, 3) else None)
    put(tv_panel(1.1, .63), x + .55, 0, .75, label='tv_panel 1.1x.63')
    put(sconce(shade=(.07, .13, .12, 'scalloped', '#F0E6CF')), x - .65, 0, .8, label='sconce 2 arm + shades')
    put(sconce(3, .4, shade=None, mat='antique_brass'), x - .1, 0, .7, label='sconce 3 arm')
    put(radiator_towel_rail(), x - 2.1, 0, .18, label='radiator_towel_rail')
    put(radiator_panel(.8, .6), x - 1.35, 0, .15, label='radiator_panel')

    # ---- bay C: soft furnishings
    x = BX['C']
    put(curtain_pair(1.9, 2.45, 'tartan_red', tie_from_top=1.35), x - 1.25, 0, 2.5, label='curtain_pair pole + tiebacks')
    put(curtain_pair(1.3, 2.45, 'check_grey', stack=.45, hang='pelmet', tieback=False), x + .8, 0, 2.5, label='curtain_pair pelmet')
    put(curtain_panel(.5, 2.45, 'check_grey', tieback='left', tie_from_top=1.5), x + 2.0, 0, 2.5, label='curtain_panel tieback')
    put(curtain_pole(1.2, finial='urn', rings=8, mat='black_matt'), x + .8, 0, 2.72, label='curtain_pole urn')
    put(pelmet_box(1.0), x - 1.25, 0, 2.78, label='pelmet_box')
    for k in range(2):
        put(plantation_shutter_panel(.42, 1.5, mid_rail=.8), x - 1.46 + k * .425, -.03, .7, label='plantation_shutter_panel' if k == 0 else None)
    put(rug(card, 1.4, 2.0, fringe=.04), x - .9, -2.2, 0, label='rug 1.4x2 image + fringe')
    put(rug(None, .62, .98, corner_r=.05, color='#B89A45'), x + .9, -3.2, 0, label='rug plain rounded')
    put(bevel_box(1.6, .5, .42, 'dark_oak_antique', .01), x + .9, -1.6, 0)
    put(upholstered_seat(.5, .45, .08, 'plain', gimp='rope_cream'), x + .35, -1.6, .42, label='upholstered_seat plain + gimp')
    put(upholstered_seat(.5, .45, .1, 'buttoned', buttons=(4, 3)), x + .9, -1.6, .42, label='upholstered_seat buttoned')
    put(upholstered_seat(.5, .45, .06, 'plain', mat='#D3C6A6', piping='rope_cream'), x + 1.45, -1.6, .42, label='upholstered_seat piped')
    put(cushion(.55, .55, .16), x + .1, -2.4, .0, label='cushion 55')
    put(cushion(.42, .42, .13, '#C98958', piping='rope_cream'), x + .75, -2.4, 0, label='cushion 42 piped')
    put(cushion(.45, .45), x + 1.3, -1.36, .78, rx=75, label=None)
    put(bolster(), x + 1.4, -2.4, 0, label='bolster')
    put(tassel(), x + 1.9, -2.4, .32, label='tassel')

    # ---- bay D: lighting + ornaments + plants
    x = BX['D']
    put(box(4.6, 2.6, .05, '#EEEEEA'), x, -1.3, 2.6)
    put(chandelier(shade=(.07, .15, .13, 'scalloped', '#F0E6CF'), watts=4), x - 1.2, -1.3, 2.6, label='chandelier 8+4 column, shades, crystals')
    ch2 = put(chandelier(.85, .8, body='bowl', crystals=False, shade=(.07, .13, .11, 'pleated', '#B4605A'), watts=4), x + 1.1, -1.3, 2.6, label='chandelier 8+4 bowl, pleated shades')
    for k in range(3):
        put(downlight(watts=20), x - .9 + k * .9, -.5, 2.6, label='downlight' if k == 0 else None)
    put(bevel_box(2.6, .6, .75, 'dark_oak_antique', .01), x, -1.0, 0)
    tabletop = [('mantel_clock slate', mantel_clock(), -1.1), ('mantel_clock bracket', mantel_clock(.26, .15, .3, 'bracket'), -.7),
                ('vase baluster + flowers', vase(.3, .18, flowers=7), -.35), ('vase urn', vase(.22, .14, 'urn', 'marble_green'), -.1),
                ('vase bowl', vase(.08, .16, 'bowl', '#9DB8A6'), .1), ('decanter round', decanter(kind='round'), .3),
                ('wine_glass', wine_glass(), .45), ('lampshade empire', lampshade(.24, .34, .27, 'empire', '#F1E6DA'), .72),
                ('candle_bulb', candle_bulb(), .98), ('crystal_drop tear', crystal_drop(.05, 'tear'), 1.08)]
    for lab, o, dx in tabletop:
        put(o, x + dx, -1.0, .75 + (.1 if 'crystal' in lab else 0), label=lab)
    put(glassware_set(), x - .6, -1.2, .75, label='glassware_set tray+6+decanter')
    put(plate(), x + .35, -1.2, .75, label=None)
    put(speaker_box(), x + 1.15, -1.05, .75, rz=-15, label='speaker_box')
    put(chandelier_arm(), x + 1.7, -.2, 1.5, label='chandelier_arm (plain)')
    put(bead_swag(), x + 1.7, -.05, 2.0, label='bead_swag')
    put(plant_potted('monstera'), x - 2.0, -1.9, 0, label='plant_potted monstera')
    put(plant_potted('dracaena', pot_dia=.3, pot_h=.28, pot_mat='black_matt', stand=.06), x - 1.3, -2.2, 0, label='plant_potted dracaena')
    put(plant_potted('citrus', pot_dia=.33, pot_h=.3, pot_mat='#6F7A45', stand=.08), x + 1.9, -2.2, 0, label='plant_potted citrus')
    put(plant_potted('eucalyptus', pot_dia=.16, pot_h=.15, pot_mat='brass'), x + .4, -2.1, 0, label='plant_potted eucalyptus')

    # ---- bay E: interaction parts (INTERACT.md): left of each pair = state 0, right = state 1
    x = BX['E']
    ck = dict(width=1.2, height=2.0, mat='tartan_red', stack=.4, tie_from_top=1.2)
    for dx, closed in ((-1.8, False), (-.3, True)):
        put(curtain_pair(cloth=False, **ck), x + dx, 0, 2.3, label=None if closed else 'curtain_pair cloth=False (pole only)')
        put(curtain_pair(hardware=False, closed=closed, **ck), x + dx, 0, 2.3,
            label='curtain_pair hardware=False' + (', closed=True' if closed else ''))
    for i, st in enumerate(('baton', 'spade', 'sweep')):
        cx, cz, r = x + .85 + i * .35, 2.35, .13
        put(lathe([(0, 0), (r * 1.08, 0), (r * 1.08, .01), (0, .01)], 24, 'dial_cream'), cx, 0, cz, rx=90)
        hs = clock_hands(r, st, name='sheet.clock%d' % i)
        assert len(hs) == (3 if st == 'sweep' else 2) and clock_hands(r, st)[0].data is hs[0].data
        for o, deg in zip(hs, (305, 60, 210)):                # 10:10:35 - turn clockwise about the dial axis
            put(o, cx, -.01, cz, label='clock_hands %s' % st if o is hs[0] else None).rotation_euler = (0, radians(deg), 0)
    put(tv_panel(1.1, .63), x + 1.5, 0, 1.6)
    put(tv_screen(1.09, .62), x + 1.5, -.0716, 1.6, label='tv_screen (on)')
    put(bevel_box(1.7, .6, .86, 'grey_cabinet', .004), x + 1.2, -1.2, 0)
    put(box(.6, .5, .02, 'black_gloss'), x + 1.6, -1.2, .86)
    for k, (bx_, by, dia) in enumerate(((-.15, -.12, .07), (.15, -.12, .10), (-.15, .12, .10), (.15, .12, .07))):
        put(lathe([(0, 0), (dia * .42, 0), (dia * .42, .012), (0, .014)], 16, 'cast_iron'), x + 1.6 + bx_, -1.2 + by, .88)
        fl = put(flame_ring(dia), x + 1.6 + bx_, -1.2 + by, .894, label='flame_ring %g' % dia if k < 2 else None)
        assert len(fl.data.polygons) == 96
    put(vase(.09, .34, 'bowl', 'ceramic_white'), x + .75, -1.2, .86)
    put(lathe([(0, 0), (.018, 0), (.014, .26), (0, .26)], 12, 'chrome'), x + .75, -1.0, .86)
    put(lathe([(0, 0), (.011, 0), (.011, .2), (0, .2)], 10, 'chrome'), x + .75, -1.0, 1.1, rx=90)
    ws = put(water_stream(.16), x + .75, -1.19, 1.1, label='water_stream .16')
    assert abs(max(l.uv.y for l in ws.data.uv_layers[0].data) - 1.6) < 1e-5, 'water V = fall in 0.1 m'
    for dx, inner in ((-1.6, '#F4F2EC'), (-.8, None)):
        cc = put(cabinet_carcass(.6, .56, .87, 'navy_cabinet', open_front=True, shelves=1, inner=inner), x + dx, -2.2, 0,
                 label='cabinet_carcass open, inner=%s' % inner)
        assert len(cc.data.materials) == (2 if inner else 1)
        put(panel_door(.597, .717), x + dx - .3 + .2985 * cos(radians(-100)), -2.76 + .2985 * sin(radians(-100)), .15, rz=-100)

    # ---- sanity + triangle table
    bp = bulb_points(ch2)
    assert len(bp) == 12 and all(2.0 < q.z < 2.6 and abs(q.x - BX['D'] - 1.1) < .5 for q in bp), bp
    for lab, o in table:
        for q in family(o):
            assert tuple(round(s, 6) for s in q.scale) == (1, 1, 1), lab
            if q.type == 'MESH' and q is o:
                assert len(q.data.polygons) > 0 and q.data.uv_layers, lab
                assert all(math.isfinite(c) for v in q.data.vertices for c in v.co), lab
    lines = ['%-46s %7s %7s' % ('prop', 'tris', 'unique')] + ['%-46s %7d %7d' % (lab, tris(o), tris(o, True)) for lab, o in table]
    total = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in sc.objects if o.type == 'MESH')
    lines.append('%-46s %7d' % ('WHOLE SHEET (all instances)', total))
    open(os.path.join(out_dir, 'tris.txt'), 'w').write('\n'.join(lines)); print('\n'.join(lines))

    # ---- light + cameras + render
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs['Color'].default_value = (.9, .94, 1, 1); bg.inputs['Strength'].default_value = .9
    sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); sun.data.energy = 2.2; sun.data.angle = radians(6)
    sun.rotation_euler = (radians(58), 0, radians(-28)); col.objects.link(sun)
    cams = {'A': [((0, -4.6, 1.5), (0, 0, 1.15), 24), ((-1.2, -2.6, 1.3), (-1.2, 0, .95), 28), ((.3, -3.0, .7), (-.6, -1.5, .32), 40), ((1.5, -1.9, 1.55), (1.5, 0, 1.55), 45)],
            'B': [((0, -4.6, 1.5), (0, 0, 1.35), 24), ((-.9, -2.3, 1.7), (-1.2, 0, 1.7), 35), ((1.2, -2.5, 1.5), (.9, 0, 1.5), 35), ((-1.2, -2.2, .8), (-1.2, 0, .6), 35)],
            'C': [((0, -5.2, 1.6), (0, 0, 1.2), 24), ((-1.25, -3.0, 1.5), (-1.25, 0, 1.45), 30), ((.9, -3.6, 1.5), (.9, -1.8, .4), 35), ((1.2, -2.6, 1.6), (1.4, 0, 1.6), 30)],
            'D': [((0, -5.0, 1.5), (0, -.5, 1.35), 24), ((-1.2, -3.0, 1.9), (-1.2, -1.3, 2.25), 40), ((1.1, -3.1, 1.7), (1.1, -1.3, 2.1), 40), ((0, -2.7, 1.3), (0, -1.0, .9), 35),
                  ((-1.5, -3.6, 1.0), (-1.6, -2.0, .45), 35), ((1.6, -4.2, 1.3), (1.9, -2.2, .9), 35)],
            'E': [((0, -5.0, 1.6), (0, -.5, 1.2), 24), ((1.2, -2.3, 1.45), (1.2, -1.2, .92), 40), ((1.25, -2.6, 1.9), (1.25, 0, 1.95), 35),
                  ((-1.2, -3.9, 1.1), (-1.2, -2.3, .45), 40), ((-1.05, -4.3, 1.4), (-1.05, 0, 1.3), 28)]}
    sc.render.engine = 'CYCLES'; sc.cycles.samples = samples; sc.cycles.use_denoising = True
    sc.cycles.sample_clamp_indirect = 10; sc.cycles.max_bounces = 8
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.image_settings.file_format = 'JPEG'
    sc.view_settings.view_transform = 'AgX'
    try:
        p = bpy.context.preferences.addons['cycles'].preferences
        for t in ('OPTIX', 'CUDA'):
            try:
                p.compute_device_type = t; p.get_devices(); break
            except Exception:
                continue
        for dv in p.devices:
            dv.use = dv.type != 'CPU'
        if any(dv.use for dv in p.devices):
            sc.cycles.device = 'GPU'
    except Exception as ex:
        print('GPU setup failed, CPU render:', ex)
    for bay, lst in cams.items():
        for i, (pos, look, lens) in enumerate(lst):
            if only and bay + str(i) not in only and bay not in only:
                continue
            cd = bpy.data.cameras.new('cam'); cd.lens = lens; cd.clip_start = .05
            co = bpy.data.objects.new('cam', cd); col.objects.link(co)
            pos = Vector(pos) + Vector((BX[bay], 0, 0)); look = Vector(look) + Vector((BX[bay], 0, 0))
            co.location = pos; co.rotation_euler = (look - pos).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
            sc.render.filepath = os.path.join(out_dir, 'props_%s%d.jpg' % (bay, i)); bpy.ops.render.render(write_still=True)
    print('PROPS SHEET OK')


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='build/props'); ap.add_argument('--res', default='1600x900')
    ap.add_argument('--samples', type=int, default=64); ap.add_argument('--only', default='')
    a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    try:
        contact_sheet(a.out, tuple(int(v) for v in a.res.split('x')), a.samples, [s for s in a.only.split(',') if s])
    except Exception:
        import traceback
        traceback.print_exc(); sys.exit(1)

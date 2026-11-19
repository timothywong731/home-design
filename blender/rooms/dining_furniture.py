"""Dining room: shared modelling helpers, the room's own materials and the draw-leaf refectory table.
Imported by rooms/dining.py and the other rooms/dining_*.py modules.

All builders work in a local frame (origin = footprint centre on the floor, metres) and return
unlinked objects."""
import math
import os
from math import sin, cos, pi

import bmesh
import bpy
from mathutils import Matrix, Vector

from lib import materials as M, mouldings as mo, props as P

T = Matrix.Translation
CRYSTAL_GLOW = 0.6       # emission strength of the chandelier's cut glass (x 0.6 alpha); 0 = mirror facets only
ART =os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'textures', 'art', 'dining')


def R(axis, deg):
    return Matrix.Rotation(math.radians(deg), 4, axis)


WALL = R('X', 90)        # relief frame: local +Z (relief) -> -Y (toward the viewer of a wall prop), local +Y -> up
RECT = lambda a, b: [(-a, 0), (a, 0), (a, b), (-a, b), (-a, 0)]      # sweep section, 2a wide x b high


# ============================================================================== materials of this room
def _bsdf(m):
    return next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')


def dark_wood():
    """Near-black oak of the chairs, carved panels and mirror frame (#2E221A; library grain, darkened)."""
    return M.image_mat('dining_dark_wood', os.path.join(ART, 'dark_wood.jpg'), (1.2, 1.2), roughness=.3)


def brass():
    """Yellow polished brass of the light fittings (the library brass reads copper next to the dark walls)."""
    return M.solid('dining_brass', '#CDC47E', .15, metallic=1)


def crystal():
    """Cut crystal: the library's mirror-glass, 60 % opaque (at the library's 10 % a 10 mm bead vanishes), with a
    faint warm emission standing in for the lamp light the real glass refracts - mirror facets alone only
    show the dark walls and the dressing reads grey. Constant emission, so it survives glTF."""
    m = bpy.data.materials.get('dining_crystal')
    if m is None:
        m = M.mat('glass_clear').copy()
        m.name = 'dining_crystal'
        b = _bsdf(m)
        b.inputs['Alpha'].default_value = .6
        b.inputs['Emission Color'].default_value = M.hex_lin('#F2C070')     # amber = white under the 3000 K view white point
        b.inputs['Emission Strength'].default_value = CRYSTAL_GLOW
    return m


def check_mat():
    """Curtain cloth: the library's check_grey (weave normal map, 0.2 m sett) with this room's colour map, whose
    bands are paler and greyer - the library taupe rendered brown in the folds next to F_680."""
    m = bpy.data.materials.get('dining_check')
    if m is None:
        m = M.mat('check_grey').copy()
        m.name = 'dining_check'
        tex = _bsdf(m).inputs['Base Color'].links[0].from_node
        tex.image = bpy.data.images.load(os.path.join(ART, 'check_curtain.jpg'), check_existing=True)
        tex.image.name = 'dining_check_col'
    return m


def top_mat():
    """French-polished table top: darkened oak with rubbed patches, roughness map (0.08 - 0.4) for the wear."""
    m = M.image_mat('dining_table_top', os.path.join(ART, 'table_top.jpg'), (1.2, 1.2), roughness=.15)
    if not m.get('orm'):
        nt = m.node_tree
        tex = nt.nodes.new('ShaderNodeTexImage')
        tex.image = bpy.data.images.load(os.path.join(ART, 'table_top_orm.jpg'), check_existing=True)
        tex.image.colorspace_settings.name = 'Non-Color'
        sep = nt.nodes.new('ShaderNodeSeparateColor')            # glTF packing, as the library: G roughness, B metallic
        nt.links.new(tex.outputs['Color'], sep.inputs['Color'])
        nt.links.new(sep.outputs['Green'], _bsdf(m).inputs['Roughness'])
        nt.links.new(sep.outputs['Blue'], _bsdf(m).inputs['Metallic'])
        m['orm'] = True
    return m


# ============================================================================== mesh helpers (on mo.MB)
def fin(mb, name):
    """MB.finish after welding coincident vertices, so curved bands / grids shade smooth."""
    bmesh.ops.remove_doubles(mb.bm, verts=mb.bm.verts[:], dist=1e-5)
    return mb.finish(name)


def spline(pts, n=6):
    """Catmull-Rom resample of a polyline (tuples of any dimension), n points per span."""
    P_ = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P_) - 2):
        p0, p1, p2, p3 = P_[i - 1], P_[i], P_[i + 1], P_[i + 2]
        for k in range(n):
            t = k / n
            out.append(tuple(0.5 * (2 * b + (c - a) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (3 * b - a - 3 * c + d) * t ** 3)
                             for a, b, c, d in zip(p0, p1, p2, p3)))
    return out + [tuple(pts[-1])]


def loft(mb, rings, mat, closed=True, caps=False, flat=False, solid=None, uv=None):
    """Quad skin through consecutive rings (lists of points, equal length). closed: every ring is a loop;
    caps: n-gons on the first and last ring; flat: faceted shading (cut crystal); solid (default = closed and
    capped): normals recalculated outward. uv(i, j) -> (u, v) in metres; default: girth x length along."""
    mi = mb.mi(mat)
    V = [mb._vs(r) for r in rings]
    n, m = len(rings[0]), len(rings)
    if uv is None:
        gu, gv = [0.0], [0.0]
        r0 = [Vector(p) for p in rings[0]]
        for a, b in zip(r0, r0[1:] + r0[:1]):
            gu.append(gu[-1] + (b - a).length)
        for a, b in zip(rings, rings[1:]):
            gv.append(gv[-1] + (Vector(b[0]) - Vector(a[0])).length)
        ou, ov = mb._off()
        uv = lambda i, j: (gu[j] + ou, gv[i] + ov)
    faces = []
    for i in range(m - 1):
        for j in range(n if closed else n - 1):
            j2 = (j + 1) % n
            faces.append(mb._f([V[i][j], V[i][j2], V[i + 1][j2], V[i + 1][j]], mi,
                               [uv(i, j), uv(i, j + 1), uv(i + 1, j + 1), uv(i + 1, j)]))
    if caps:
        for i, rev in ((0, True), (m - 1, False)):
            vs = V[i][::-1] if rev else V[i]
            faces.append(mb._f(vs, mi, [(Vector(v.co).x, Vector(v.co).z) for v in vs]))
    faces = [f for f in faces if f is not None]
    if flat:
        for f in faces:
            f.smooth = False
    if solid if solid is not None else (closed and caps):
        bmesh.ops.recalc_face_normals(mb.bm, faces=faces)
    return faces


def grid(mb, fn, nu, nv, mat, wrap=False, flat=False, uv=None, solid=False):
    """Parametric surface fn(u, v) -> point, u, v in 0..1 (u wraps when wrap). uv(u, v) -> texture coords."""
    cols = nu if wrap else nu + 1
    rings = [[fn(j / nu, i / nv) for j in range(cols)] for i in range(nv + 1)]
    return loft(mb, rings, mat, wrap, False, flat, solid, (lambda i, j: uv(j / nu, i / nv)) if uv else None)


def bar(mb, path, sec, mat, up=(0, 0, 1), scale=None, caps=True, flat=False):
    """Bar of section sec [(a, b)...] along a curved path. a runs along up x tangent, b along the remaining
    axis (= up for a planar path with up = plane normal). scale = per-point (sa, sb) or number."""
    pts = [Vector(p[:3]) for p in path]
    up = Vector(up).normalized()
    n = len(pts)
    rings = []
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        s = up.cross(t)
        s = s.normalized() if s.length > 1e-6 else Vector((1, 0, 0))
        u2 = t.cross(s)
        k = scale[i] if scale is not None else 1.0
        sa, sb = k if isinstance(k, (tuple, list)) else (k, k)
        rings.append([p + s * (a * sa) + u2 * (b * sb) for a, b in sec])
    return loft(mb, rings, mat, True, caps, flat, solid=True)


def rrect(w, h, r=None, k=2):
    """Rounded rectangle w (a) x h (b) centred on the origin; k segments per corner."""
    r = min(r if r is not None else .25 * min(w, h), w / 2, h / 2)
    out = []
    for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180),
                       (w / 2 - r, -h / 2 + r, 270)):
        out += [(cx + r * cos(math.radians(a0 + 90 * i / k)), cy + r * sin(math.radians(a0 + 90 * i / k))) for i in range(k + 1)]
    return out


def oval(w, h, n=10):
    return [(w / 2 * cos(2 * pi * i / n), h / 2 * sin(2 * pi * i / n)) for i in range(n)]


def turn(mb, prof, mat, segs=16, flat=False, rmod=None, stagger=False, caps=True):
    """Lathe round local Z of [(r, z)...] with no points on the axis (ends capped unless caps=False). rmod(theta, j) scales
    the radius of profile point j (gadroons, scallops, twists); stagger turns alternate rings half a
    segment (diamond-cut crystal)."""
    rings = []
    for j, (r, z) in enumerate(prof):
        ring = []
        for i in range(segs):
            th = 2 * pi * (i + (.5 if stagger and j % 2 else 0)) / segs
            rr = r * (rmod(th, j) if rmod else 1.0)
            ring.append((rr * cos(th), rr * sin(th), z))
        rings.append(ring)
    return loft(mb, rings, mat, True, caps, flat)


def band(mb, A, B, y0, y1, mat):
    """Flat member cut from a board standing in the local XZ plane: strip between the polylines A and B
    [(x, z)...] (same length), y0 = front (faces -Y), y1 = back."""
    n = len(A)
    for i in range(n - 1):
        a, a2, b, b2 = A[i], A[i + 1], B[i], B[i + 1]
        mb.face([(a[0], y0, a[1]), (a2[0], y0, a2[1]), (b2[0], y0, b2[1]), (b[0], y0, b[1])], mat, (0, -1, 0))
        mb.face([(a[0], y1, a[1]), (a2[0], y1, a2[1]), (b2[0], y1, b2[1]), (b[0], y1, b[1])], mat, (0, 1, 0))
        for p, p2, q in ((a, a2, b), (b, b2, a)):
            mb.face([(p[0], y0, p[1]), (p2[0], y0, p2[1]), (p2[0], y1, p2[1]), (p[0], y1, p[1])], mat,
                    (p[0] - q[0], 0, p[1] - q[1]))
    for i, j in ((0, 1), (n - 1, n - 2)):
        a, b = A[i], B[i]
        mb.face([(a[0], y0, a[1]), (b[0], y0, b[1]), (b[0], y1, b[1]), (a[0], y1, a[1])], mat,
                (A[i][0] - A[j][0], 0, A[i][1] - A[j][1]))


def shared(cache, key, build, name):
    """New object on the mesh that build() made the first time (linked duplicates)."""
    me = cache.get(key)
    try:
        me and me.name
    except ReferenceError:
        me = None
    if me is None:
        me = cache[key] = build().data
    return bpy.data.objects.new(name, me)


# ============================================================================== table
def _board(mb, x0, x1, y0, y1, z0, z1, mat, round_x, r=.012, seed=0.0):
    """One board of the top, running along Y. round_x = (left, right): thumb-moulded outer long edge with a
    slightly wavy, hand-worked line (else a 1 mm V-joint to its neighbour); both ends rounded."""
    re = .010
    ys = [y0 + re * (1 - cos(pi / 2 * k / 3)) for k in range(3)]
    nmid = max(2, round((y1 - y0) / .13))
    ys += [y0 + re + (y1 - y0 - 2 * re) * k / nmid for k in range(nmid + 1)]
    ys += [y1 - re * (1 - cos(pi / 2 * k / 3)) for k in (2, 1, 0)]
    dz = .0006 * sin(seed * 5.1)                                   # boards a hair out of level: the joints catch the light
    rings = []
    for y in ys:
        e = min(y - y0, y1 - y, re)
        zt = z1 + dz - re * (1 - math.sqrt(max(0.0, 1 - (1 - e / re) ** 2)))    # rounded ends
        wv = .0016 * sin(7.3 * y + seed) + .0009 * sin(19 * y + 2.1 * seed)     # waviness of a moulded edge
        ring = [(x0 + (.003 if round_x[0] else 0), z0)]
        for side, rnd, sg in ((x0, round_x[0], 1), (x1, round_x[1], -1)):
            rr = r if rnd else .001
            arc = [(side + sg * (rr - rr * cos(pi / 2 * k / 3)) + (wv * sg if rnd else 0), z1 + dz - rr + rr * sin(pi / 2 * k / 3))
                   for k in range(4)]
            ring += arc if sg > 0 else arc[::-1]
        ring.append((x1 - (.003 if round_x[1] else 0), z0))
        rings.append([(x, y, min(z, zt) if z > z0 else z) for x, z in ring])
    loft(mb, rings, mat, True, True)


def table():
    """Antique dark-oak draw-leaf refectory table, both leaves out: 2.74 x 0.90 x 0.77, long axis Y.
    Top and leaves of four boards each (V-joints, thumb-moulded wavy edge, French polish with rubbed
    patches); cup-and-cover legs on bun feet, box stretcher, lunette-carved frieze with a scalloped edge."""
    top, dark = top_mat(), 'dark_oak_antique'
    mb = mo.MB()
    xs = [-.45, -.225, 0, .225, .45]
    for part, (y0, y1, z0, z1) in enumerate(((-.75, .75, .735, .77), (.752, 1.37, .727, .762), (-1.37, -.752, .727, .762))):
        for b in range(4):
            _board(mb, xs[b] + .0001, xs[b + 1] - .0001, y0, y1, z0, z1, top, (b == 0, b == 3), seed=1.7 * b + 4.1 * part)
    for s in (-1, 1):
        for x in (-.27, .27):                                                       # tapered leaf bearers
            mb.prism([(x - .022, s * .69, .727), (x - .022, s * 1.30, .727), (x - .022, s * 1.30, .707),
                      (x - .022, s * .69, .665)], (.044, 0, 0), dark)
    # frieze: four boards, 0.11 deep, lobed lower edge; a lunette (arch + boss) carved over every lobe
    for F, L in ((T((.38, 0, 0)) @ R('Z', 90), 1.36), (T((-.38, 0, 0)) @ R('Z', -90), 1.36),
                 (T((0, -.68, 0)), .76), (T((0, .68, 0)) @ R('Z', 180), .76)):
        k = round(L / .124)
        n = k * 8
        fx = [-L / 2 + L * i / n for i in range(n + 1)]
        mb.at(F)
        band(mb, [(x, .625 + .02 * (1 - sin(pi * ((i / 8) % 1.0)) ** .6)) for i, x in enumerate(fx)],
             [(x, .735) for x in fx], 0, .03, dark)
        mb.box((-L / 2, -.004, .712), (L / 2, 0, .726), dark, bev=.002)                 # bead under the top
        for j in range(k):
            cx = -L / 2 + (j + .5) * L / k
            mb.tube([(cx + .043 * cos(pi * a / 8), -.001, .652 + .043 * sin(pi * a / 8)) for a in range(9)], .005, dark, 5)
            mb.at(F @ T((cx, 0, .668)) @ WALL)
            mb.dome(.017, .013, .007, dark, 8, 2)
            mb.at(F)
    mb.at()
    for sx in (-1, 1):
        mb.box((sx * .32 - .035, -.535, .08), (sx * .32 + .035, .535, .13), dark, bev=.005)     # box stretcher
        for sy in (-1, 1):
            mb.at(T((sx * .32, sy * .60, 0)))
            mb.lathe([(0, 0), (.05, 0), (.07, .012), (.064, .026), (.05, .03), (0, .03)], dark, 16)   # bun foot
            mb.at()
    for sy in (-1, 1):
        mb.box((-.255, sy * .60 - .035, .08), (.255, sy * .60 + .035, .13), dark, bev=.005)
    root = fin(mb, 'dining.table')
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        leg = P.turned_leg(.705, .13, 'cup_cover', .12, .14, dark, name=f'dining.table.leg.{i}')
        leg.parent = root
        leg.location = (sx * .32, sy * .60, .03)
    return root

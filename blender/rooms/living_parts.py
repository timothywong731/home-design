"""Living-room furniture builders (imported by rooms/living.py).

Every builder returns ONE unlinked root object at scale 1: origin = footprint centre on the floor,
front = local -Y, parts that are lib props are parented children (ctx.add links the family).
"""
import bpy
import math
import os
from math import sin, cos, pi, radians, tau
from mathutils import Matrix, Vector
from lib import materials as M, mouldings as mo, props as P

GIMP = 'linen_cream'                                     # cream gimp braid
ART = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'textures', 'art', 'living'))


# ------------------------------------------------------------------------------------ module-local materials
# Each is one Principled BSDF with constants (+ the library's own image maps), so it exports to glTF as is.
def _bsdf(m):
    return next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')


def _retex(key, name, image, size_m=None):
    """Copy of the library material `key` (its normal map, sheen ...) with a module colour map from ART."""
    m = bpy.data.materials.get(name)
    if m is None:
        m = M.mat(key).copy()
        m.name = name
        m['key'] = name
        tex = _bsdf(m).inputs['Base Color'].links[0].from_node
        tex.image = bpy.data.images.load(os.path.join(ART, image), check_existing=True)
        if size_m:
            m['size_m'] = [float(size_m[0]), float(size_m[1])]
    return m


def velvet(name='living_velvet', image='velvet_rose.jpg', tint='#F0A898'):
    """Crushed terracotta-rose velvet: the library 'velvet_orange' (nap normal map, sheen) with a generated colour
    map of nap patches (0.6 m repeat; velvet_rose.jpg = the round-2 burnt-orange map, median #8B5631, turned toward
    the v10 daylight samples, median #9B5044: living_games_tex.py velvet), a full rose-tinted sheen and a slightly
    lower roughness so the pile catches the lamps. ponytail: drop it once lib velvet_orange has nap."""
    m = bpy.data.materials.get(name)
    if m is None:
        m = _retex('velvet_orange', name, image, (0.6, 0.6))
        b = _bsdf(m)
        b.inputs['Roughness'].default_value = 0.7
        b.inputs['Sheen Weight'].default_value = 1.0
        b.inputs['Sheen Roughness'].default_value = 0.35
        b.inputs['Sheen Tint'].default_value = M.hex_lin(tint)
    return m


def velvet_light():
    """Scatter cushions: the same cloth one tone lighter."""
    return velvet('living_velvet_light', 'velvet_rose_light.jpg', '#F4B4A4')


def oak_dark():
    """Dark stained open-grain oak of the coffee and side tables: library 'oak_table' (normal map) with a generated
    colour map of long, irregular plain-sawn grain with broad cathedral arches over four boards, lower contrast than
    round 2 (oak_top.jpg, living_games_tex.py oak; 0.64 m across x 1.28 m along), satin-gloss (v10 t03, t40)."""
    m = _retex('oak_table', 'living_oak_dark', 'oak_top.jpg', (0.64, 1.28))
    _bsdf(m).inputs['Roughness'].default_value = 0.26
    return m


def gold(kind='bright'):
    """Gilt of the gallery frames, paler and greener than lib gilt / gilt_bright, which render orange-copper in
    this pink room. Metallic bases tuned so that the frames render like f_0176 (olive gold #7C6938 body with
    yellow highlights): the spec's #C8A64B / #9C8440 / #8C7446 are what should be SEEN, not the base colour."""
    hx, rough = {'bright': ('#A89C54', 0.28), 'antique': ('#928A52', 0.32), 'bronze': ('#8E8458', 0.40),
                 'champagne': ('#B8AE7C', 0.35)}[kind]
    return M.solid('living_gold_' + kind, hx, rough, 1)


def brass():
    """Polished yellow brass of the chandelier and lamp mounts. Library 'brass' (#E3CC8E) reflects this room's
    pink walls and rose shades as rose-gold; a greener base lands on the yellow brass of the video."""
    return M.solid('living_brass', '#C4BE70', 0.2, 1)


def crystal(alpha=0.22, name='living_crystal', glow=0.0):
    """Cut crystal (tumblers, decanters, vases; chandelier drops with a higher alpha under their own name): a
    clear polished mirror like the library's glass_clear, a little denser so flat-shaded facets flash
    (alpha-blended, glTF-safe). The cut is geometry (facets), never roughness: rough = frosted."""
    m = M.solid(name, '#F6FAFA', 0.0, 1)
    if glow:                                              # cut crystal next to lamps scatters light: a faint warm lift
        b = _bsdf(m)
        b.inputs['Emission Color'].default_value = M.hex_lin('#FFBC78')     # neutral white under the 3000 K view balance
        b.inputs['Emission Strength'].default_value = glow
    _bsdf(m).inputs['Alpha'].default_value = alpha
    m.surface_render_method = 'BLENDED'
    m.use_backface_culling = False
    return m


def wood():
    """Dark show-wood (brown-black, not red) of the bookcase, sofa frame, chairs, stools and small tables: library
    'dark_oak_antique' at roughness 0.5 instead of 0.30, which mirrored the bay glass and the sky steel-blue on
    the open bookcase doors. ponytail: drop it if the library key gets a satin roughness."""
    m = bpy.data.materials.get('living_dark_oak')
    if m is None:
        m = M.mat('dark_oak_antique').copy()
        m.name = 'living_dark_oak'
        m['key'] = m.name
        _bsdf(m).inputs['Roughness'].default_value = 0.5
    return m


def tartan():
    """Curtain cloth: the library 'tartan_red' weave (normal map, 0.2 m sett) with a module-local colour map
    generated to the spec yarns - taupe-grey ground over ~70 % of the threads, narrow raspberry-wine bands (v10
    daylight #9A4A55: tartan_wine.jpg, living_games_tex.py tartan), cream and charcoal lines (not a reference crop).
    ponytail: drop it once lib tartan_red is retuned."""
    m = bpy.data.materials.get('living_tartan')
    if m is None:
        m = M.mat('tartan_red').copy()
        m.name = 'living_tartan'
        m['key'] = m.name
        tex = _bsdf(m).inputs['Base Color'].links[0].from_node
        tex.image = bpy.data.images.load(os.path.join(ART, 'tartan_wine.jpg'), check_existing=True)
    return m


def Tr(x, y, z):
    return Matrix.Translation((x, y, z))


def Rz(deg):
    return Matrix.Rotation(radians(deg), 4, 'Z')


def Rx(deg):
    return Matrix.Rotation(radians(deg), 4, 'X')


def Ry(deg):
    return Matrix.Rotation(radians(deg), 4, 'Y')


MIRX = Matrix.Scale(-1, 4, (1, 0, 0))


def kid(root, ob, loc=(0, 0, 0), rot=(0, 0, 0)):
    """Parent a prop to a furniture root at a root-local position (rot in degrees, XYZ euler)."""
    ob.parent = root
    ob.location = loc
    ob.rotation_euler = tuple(radians(a) for a in rot)
    return ob


def instance(ob, name):
    """Linked duplicate of a root and its children (shared mesh data); children are renamed under the new root
    ('living.sconce.0.candle.3' -> 'living.sconce.1.candle.3')."""
    new = bpy.data.objects.new(name, ob.data)
    for c in ob.children:
        k = bpy.data.objects.new(c.name.replace(ob.name, name, 1), c.data)
        k.parent = new
        k.location, k.rotation_euler = c.location.copy(), c.rotation_euler.copy()
    return new


def _face(mb, vs, mi, uvs=None):
    try:
        f = mb.bm.faces.new(vs)
    except ValueError:
        return None
    f.material_index = mi
    f.smooth = True
    f[mb.softl] = mb._soft                            # mb._soft = 1: organic shapes stay smooth up to 80 deg
    if uvs:
        for l, uv in zip(f.loops, uvs):
            l[mb.uvl].uv = uv
    return f


def loft(mb, rings, mat, closed=True, caps=(True, True), flip=None, planar=None):
    """Skin consecutive rings (lists of 3D points, equal length) with shared vertices, so the surface
    shades smooth where it bends less than MB.finish's sharp angle. Faces are wound outward (signed
    volume about the centroid) unless flip is given. caps = n-gons on the first / last ring.
    planar = ring index from which the UVs are the rings' own local (x, y) instead of (girth, length):
    the crowned top of a pad, so the cloth pattern does not pinch toward the centre."""
    mi = mb.mi(mat)
    V = [mb._vs(r) for r in rings]
    n = len(rings[0])
    us = [0.0]
    for a, b in zip(rings[0], rings[0][1:] + (rings[0][:1] if closed else [])):
        us.append(us[-1] + (Vector(b) - Vector(a)).length)
    vv = [0.0]
    for r0, r1 in zip(rings, rings[1:]):
        vv.append(vv[-1] + max(1e-6, (Vector(r1[0]) - Vector(r0[0])).length))
    quads = []
    for i in range(len(rings) - 1):
        for j in range(n if closed else n - 1):
            j2 = (j + 1) % n
            if planar is not None and i >= planar:
                uv = [rings[i][j][:2], rings[i][j2][:2], rings[i + 1][j2][:2], rings[i + 1][j][:2]]
            else:
                uv = [(us[j], vv[i]), (us[j + 1], vv[i]), (us[j + 1], vv[i + 1]), (us[j], vv[i + 1])]
            quads.append(([V[i][j], V[i][j2], V[i + 1][j2], V[i + 1][j]], uv))
    cen = sum((v.co for r in V for v in r), Vector()) / (len(V) * n)
    if flip is None:
        vol = 0.0
        for q, _ in quads:
            a, b, c, d = (v.co for v in q)
            vol += (c - a).cross(d - b).dot((a + b + c + d) / 4 - cen)
        flip = vol < 0
    for q, uv in quads:
        if len(set(q)) < 3:
            continue
        _face(mb, q[::-1] if flip else q, mi, uv[::-1] if flip else uv)
    for k, on in ((0, caps[0]), (-1, caps[1])):
        if not on or not closed:
            continue
        vs = V[k]
        c0 = sum((v.co for v in vs), Vector()) / n
        nrm = Vector()
        for a, b in zip(vs, vs[1:] + vs[:1]):
            nrm += (a.co - c0).cross(b.co - c0)
        out = c0 - cen
        ax = max(range(3), key=lambda i: abs(nrm[i]))
        u, w = [i for i in range(3) if i != ax]
        uv = [tuple(q[:2]) for q in rings[k]] if planar is not None and k == -1 else [(v.co[u], v.co[w]) for v in vs]
        if nrm.dot(out) <= 0:
            vs, uv = vs[::-1], uv[::-1]
        _face(mb, vs, mi, uv)


def tube_var(mb, pts, radii, mat, n=6, caps=(True, True)):
    """Round limb along a polyline with a radius per point (rings square to the local tangent, frame carried
    along the path without twisting). Use it instead of MB.tube for curves that turn through the vertical."""
    P_ = [Vector(p) for p in pts]
    rings = []
    ref = None
    for i, p in enumerate(P_):
        t = (P_[min(i + 1, len(P_) - 1)] - P_[max(i - 1, 0)]).normalized()
        if ref is None:
            ref = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        u = ref - t * ref.dot(t)                      # previous side vector projected square to the new tangent
        if u.length < 1e-6:
            u = t.orthogonal()
        u.normalize()
        v = t.cross(u)
        ref = u
        rings.append([tuple(p + radii[i] * (cos(tau * k / n) * u + sin(tau * k / n) * v)) for k in range(n)])
    loft(mb, rings, mat, caps=caps)


def rtube(mb, pts, r, mat, n=6):
    tube_var(mb, pts, [r] * len(pts), mat, n)


def rrect(hw, hd, r, z, n=3, x=0.0, y=0.0):
    """Rounded rectangle ring in the XY plane at height z (counter-clockwise)."""
    r = min(r, hw, hd)
    pts = []
    for cx, cy, a0 in ((hw - r, hd - r, 0), (-hw + r, hd - r, 90), (-hw + r, -hd + r, 180), (hw - r, -hd + r, 270)):
        for k in range(n + 1):
            a = radians(a0 + 90 * k / n)
            pts.append((x + cx + r * cos(a), y + cy + r * sin(a), z))
    return pts


def circ(r, z, n=16, x=0.0, y=0.0, ph=0.0):
    return [(x + r * cos(tau * k / n + ph), y + r * sin(tau * k / n + ph), z) for k in range(n)]


def slab(mb, hw, hd, r, z0, z1, mat, edge=((0.0, 0.0), (0.0, 1.0)), n=3, grain=0):
    """Rounded-rectangle slab whose edge follows `edge` = [(inset, t)...] (t 0..1 from z0 to z1); the top and
    bottom faces carry the grain along axis `grain`."""
    rings = [rrect(hw - i, hd - i, max(0.001, r - i), z0 + t * (z1 - z0), n) for i, t in edge]
    loft(mb, rings, mat, caps=(False, False))
    mb.face(rings[0], mat, (0, 0, -1), grain=grain)
    mb.face(rings[-1], mat, (0, 0, 1), grain=grain)


OGEE = ((0.014, 0.0), (0.004, 0.18), (0.0, 0.45), (0.0, 0.62), (0.004, 0.75), (0.010, 1.0))   # thumb-moulded edge
PAD = ((0.012, 0.0), (0.002, 0.12), (0.0, 0.35), (0.004, 0.70), (0.016, 0.90), (0.04, 1.0))   # stuffed-over pad


def _taper(ring, hd, k):
    """Narrow a ring toward +Y: x scaled by 1 at y = -hd down to k at y = +hd (trapezoid seats)."""
    return ring if k == 1.0 else [(x * (1 + (k - 1) * (y + hd) / (2 * hd)), y, z) for x, y, z in ring]


DOME = (0.86, 0.68, 0.47, 0.24)                          # rings of the crowned top, as fractions of the top ring


def pad(mb, hw, hd, r, z0, z1, mat=None, crown=0.012, n=4, taper=1.0):
    """Stuffed upholstery pad: rounded plan, soft top edge and a domed top (rings shrinking to the centre and
    rising by `crown`, one smooth surface with the sides). crown 0.01 = flat squab, 0.04-0.05 = overstuffed /
    sprung seat. taper = back width / front width (front = -Y). Total height = z1 + crown."""
    mat = mat or velvet()
    rings = [_taper(rrect(hw - i, hd - i, max(0.004, r - i * 0.5), z0 + t * (z1 - z0), n), hd, taper) for i, t in PAD]
    top = rings[-1]
    rings += [[(x * f, y * f, z1 + crown * (1 - f * f)) for x, y, _ in top] for f in DOME]
    soft, mb._soft = mb._soft, 1
    loft(mb, rings, mat, caps=(True, True), planar=3)        # UV seam on the shoulder, not across the top
    mb._soft = soft


def gimp_band(mb, hw, hd, r, z, h=0.012, mat=GIMP, n=3, proud=0.002, taper=1.0):
    loft(mb, [_taper(rrect(hw + proud, hd + proud, r + proud, zz, n), hd, taper) for zz in (z, z + h)],
         mat, caps=(False, False))


def cushion(mb, w, h, t, mat, sag=0.22, n=14):
    """Plump loose cushion written through the current mb transform: lies in the local XY plane (w along X,
    h along +Y from the origin = centre of its bottom edge, mid thickness), 8 mm seam all round, pulled-in
    sides (pointed corners); sag > 0 slumps the filling toward the bottom edge (a cushion stood on edge)."""
    def half(a, c):
        s = (max(0.0, 1 - abs(a) ** 3.0) * max(0.0, 1 - abs(c) ** 3.0)) ** 0.42      # full to the seam: feather-filled
        dent = 1 - 0.10 * math.exp(-((a - 0.15) ** 2 + (c - 0.1) ** 2) / 0.12)       # a soft sat-in hollow
        return 0.004 + (t / 2 - 0.004) * s * (1 - sag * c) * dent
    cs = [-1 + 2 * j / n for j in range(n + 1)]
    rings = []
    for a in cs:
        top = [(a * w / 2 * (1 - 0.05 * (1 - c * c)), h / 2 + c * h / 2 * (1 - 0.05 * (1 - a * a)), half(a, c)) for c in cs]
        rings.append(top + [(x, y, -z) for x, y, z in reversed(top)])
    mb._soft = 1
    loft(mb, rings, mat)
    mb._soft = 0


# --------------------------------------------------------------------------------------------- sofa
def _scroll_outline():
    """Right-hand scroll arm seen from the front (x, z): upholstered inner face, roll, tucked-in outer line."""
    cx, cz, r = 0.795, 0.742, 0.105
    pts = [(0.66, 0.315), (0.662, 0.43), (0.668, 0.55), (0.68, 0.66)]
    for k in range(33):                                   # 8.75 deg steps: the roll reads round, not faceted
        a = radians(180 - 280 * k / 32)
        pts.append((cx + r * cos(a), cz + r * sin(a)))
    pts += [(0.765, 0.56), (0.772, 0.46), (0.81, 0.37), (0.84, 0.315)]
    return pts, (cx, cz, r)


def sofa(name='living.sofa'):
    """William IV double-ended settee, 1.80 x 0.70 x 0.86 (seat 0.42): dark show-frame with volute scroll
    facings, stout three-ring bobbin legs, low upholstered back under a dark top rail, fixed squab, bolsters
    and plump loose cushions."""
    mb = mo.MB()
    VELVET, WOOD = velvet(), wood()
    leg = [(0, 0), (0.03, 0), (0.042, 0.006), (0.048, 0.02), (0.042, 0.036), (0.028, 0.044), (0.031, 0.052),
           (0.05, 0.064), (0.056, 0.085), (0.05, 0.106), (0.031, 0.118), (0.028, 0.126), (0.042, 0.136), (0.048, 0.152),
           (0.042, 0.168), (0.031, 0.178), (0.036, 0.186), (0.036, 0.20), (0, 0.20)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.at(Tr(sx * 0.74, sy * 0.27, 0))
            mb.lathe(leg, wood(), 20)
    mb.at()
    mb.box((-0.84, -0.35, 0.20), (0.84, 0.35, 0.315), WOOD, bev=0.006, grain=0)
    mb.tube([(-0.835, -0.352, 0.214), (0.835, -0.352, 0.214)], 0.008, WOOD, 6)          # bead on the lower edge
    mb.box((-0.66, -0.3525, 0.304), (0.66, -0.3465, 0.315), GIMP)                        # 11 mm gimp over the tacks
    out, (cx, cz, r) = _scroll_outline()
    gx = sum(p[0] for p in out) / len(out)
    gz = sum(p[1] for p in out) / len(out)
    big = [(gx + (x - gx) * 1.035, gz + (z - gz) * 1.035) for x, z in out]              # facing stands proud
    for mir in (None, MIRX):
        mb.at(mir)
        mb._soft = 1                                                                       # one smooth roll
        loft(mb, [[(x, y, z) for x, z in out] for y in (-0.326, 0.326)], VELVET, caps=(False, False))
        for y0, y1 in ((-0.35, -0.324), (0.324, 0.35)):
            loft(mb, [[(x, y, z) for x, z in big] for y in (y0, y1)], WOOD)
        rtube(mb, [(x, -0.3225, z) for x, z in big[1:-1]], 0.005, GIMP, 6)                   # thin gimp braid follows the scroll
        mb._soft = 0
        spiral = []
        for k in range(57):
            t = k / 56
            a = radians(200 - 630 * t)
            rr = 0.094 - 0.072 * t
            spiral.append((cx + rr * cos(a), -0.352, cz + rr * sin(a)))
        rtube(mb, spiral, 0.0055, WOOD, 5)                                                 # carved volute
        mb.at((mir or Matrix.Identity(4)) @ Tr(cx, -0.35, cz) @ Rx(90))
        mb.dome(0.022, 0.022, 0.014, WOOD, 10, 3)
    mb.at()
    back = [(0.33, 0.315), (0.33, 0.735), (0.215, 0.735), (0.205, 0.70), (0.195, 0.315)]     # low upholstered back
    loft(mb, [[(x, y, z) for y, z in back] for x in (-0.70, 0.70)], VELVET)
    mb.box((-0.72, 0.20, 0.733), (0.72, 0.345, 0.762), WOOD, bev=0.008, grain=0)         # dark top rail at 0.75
    mb.tube([(-0.72, 0.20, 0.7475), (0.72, 0.20, 0.7475)], 0.012, WOOD, 8)                # its rounded front nose
    mb.box((-0.84, 0.335, 0.315), (0.84, 0.35, 0.735), WOOD, bev=0.004, grain=0)         # back show-panel
    for sx in (-1, 1):
        # two plump 0.54 back cushions slumped against the back (tops ~0.95: in f_0135 they stand well clear of
        # the 0.75 back rail), a lighter scatter cushion propped on each bolster; all set down a little askew
        mb.at(Tr(sx * 0.235, 0.035, 0.435) @ Rz(-sx * 5) @ Rx(74 if sx < 0 else 70) @ Rz(6 if sx < 0 else -9))
        cushion(mb, 0.54, 0.52, 0.21, VELVET, sag=0.30)
        mb.at(Tr(sx * 0.38, -0.15, 0.447) @ Rz(-sx * 72) @ Rx(62 if sx < 0 else 57) @ Rz(sx * 11))
        cushion(mb, 0.42, 0.42, 0.18, velvet_light(), sag=0.22)
    mb.at()
    root = mb.finish(name)
    seat = P.upholstered_seat(1.335, 0.545, 0.10, mat=VELVET, crown=0.03, name=name + '.squab')
    kid(root, seat, (0, -0.075, 0.315))
    for i, sx in enumerate((-1, 1)):
        kid(root, P.bolster(0.17, 0.40, mat=VELVET, name=f'{name}.bolster.{i}'), (sx * 0.575, -0.10, 0.425), (0, 0, 90))
    return root


# ------------------------------------------------------------------------------------- coffee table
TABLE_EDGE = ((0.030, 0.0), (0.027, 0.07), (0.019, 0.20), (0.013, 0.33), (0.011, 0.44), (0.011, 0.50),   # cove
              (0.0, 0.53), (0.0, 0.80), (0.003, 0.92), (0.011, 1.0))                         # quirk, band, thumb round-over


def coffee_table(name='living.coffee_table', mat=None):
    """Dark stained open-grain oak trestle coffee table 1.60 (X) x 0.62 x 0.46: 55 mm top with a two-step ogee
    edge (thumb round-over, quirk, cove) and 45 mm corner radii, boards and cathedral grain along the length;
    two 60 mm slab ends with scrolled toes, low stretcher."""
    mb = mo.MB()
    mat = mat or oak_dark()
    slab(mb, 0.80, 0.31, 0.045, 0.405, 0.46, mat, TABLE_EDGE, n=8)
    end = [(-0.24, 0), (-0.25, 0.03), (-0.20, 0.07), (-0.135, 0.17), (-0.13, 0.27), (-0.17, 0.36), (-0.225, 0.395),
           (-0.225, 0.406), (0.225, 0.406), (0.225, 0.395), (0.17, 0.36), (0.13, 0.27), (0.135, 0.17), (0.20, 0.07),
           (0.25, 0.03), (0.24, 0)]
    for sx in (-1, 1):
        x0 = sx * 0.52
        rings = []
        for dx, s in ((-0.03, 0.975), (-0.024, 1.0), (0.024, 1.0), (0.03, 0.975)):
            rings.append([(x0 + dx, y * s, z if z in (0, 0.406) else 0.21 + (z - 0.21) * s) for y, z in end])
        loft(mb, rings, mat)
        for sy in (-1, 1):                                               # scrolled toes: a roll across each foot end
            mb.at(Tr(x0, sy * 0.247, 0.034) @ Ry(90))
            mb.lathe([(0, -0.034), (0.022, -0.034), (0.034, -0.028), (0.034, 0.028), (0.022, 0.034), (0, 0.034)], mat, 14)
        mb.at()
    mb.box((-0.50, -0.03, 0.10), (0.50, 0.03, 0.17), mat, bev=0.006, grain=0)
    return mb.finish(name)


# ------------------------------------------------------------------- bench, footstool, side table
def bench(name='living.bench'):
    """Window stool 1.15 x 0.42 x 0.46: velvet pad with gimp on a dark oak frame, turned legs, H-stretcher."""
    mb = mo.MB()
    W = wood()
    mb.box((-0.56, -0.195, 0.31), (0.56, 0.195, 0.375), W, bev=0.004, grain=0)
    pad(mb, 0.575, 0.21, 0.03, 0.372, 0.455)
    gimp_band(mb, 0.575, 0.21, 0.03, 0.372, 0.014)
    for sx in (-1, 1):
        mb.box((sx * 0.50 - 0.016, -0.14, 0.10), (sx * 0.50 + 0.016, 0.14, 0.132), W, bev=0.003, grain=1)
    mb.box((-0.50, -0.016, 0.10), (0.50, 0.016, 0.132), W, bev=0.003, grain=0)
    root = mb.finish(name)
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        leg = P.turned_leg(0.31, 0.05, 'baluster', top_block=0.0, bottom_block=0.0, mat=W, name=f'{name}.leg.{i}')
        kid(root, leg, (sx * 0.50, sy * 0.155, 0))
    return root


def footstool(name='living.footstool'):
    """Overstuffed velvet footstool 0.55 x 0.45 x 0.40 on four short cabriole legs."""
    mb = mo.MB()
    WOOD = wood()
    mb.box((-0.255, -0.205, 0.20), (0.255, 0.205, 0.255), WOOD, bev=0.004, grain=0)
    pad(mb, 0.275, 0.225, 0.075, 0.25, 0.355, crown=0.05, n=6)             # domed, overstuffed: 0.405 at the crown
    gimp_band(mb, 0.275, 0.225, 0.075, 0.25, 0.012, n=6)
    root = mb.finish(name)
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        leg = P.turned_leg(0.22, 0.045, 'cabriole', top_block=0.05, out=(sx, sy), foot='pad', mat=WOOD,
                           name=f'{name}.leg.{i}')
        kid(root, leg, (sx * 0.225, sy * 0.175, 0))
    return root


def barley_twist(mb, z0, z1, R, mat, pitch=0.07, starts=2, n=12, per_turn=8):
    """Deep rope turning from z0 to z1 round the local Z axis: a `starts`-lobed section (waist 0.52 R) turning
    once per `pitch`, fading to round at both ends. The library turned_leg twist is only 20 % deep, which reads
    as a faintly wavy stick at furniture scale."""
    steps = max(4, round((z1 - z0) / pitch * per_turn))
    rings = []
    for i in range(steps + 1):
        z = z0 + (z1 - z0) * i / steps
        k = min(1.0, i / 3, (steps - i) / 3)
        ring = []
        for j in range(n):
            a = tau * j / n
            r = R * (1 - 0.48 * k * (0.5 - 0.5 * cos(starts * a - tau * z / pitch)))
            ring.append((r * cos(a), r * sin(a), z))
        rings.append(ring)
    soft, mb._soft = mb._soft, 1
    loft(mb, rings, mat, caps=(False, False))
    mb._soft = soft


def _piecrust(hw, hd, z, amp=0.013, lobes=(3, 2), m=10, k=1.0):
    """Scalloped (pie-crust) outline of a rectangular top, counter-clockwise: `lobes` round scallops per long and
    short side bulging `amp` beyond the hw x hd rectangle and meeting in cusps (also at the corners); k scales it."""
    pts = []
    for (ax, ay), (bx, by), nl in (((-hw, -hd), (hw, -hd), lobes[0]), ((hw, -hd), (hw, hd), lobes[1]),
                                   ((hw, hd), (-hw, hd), lobes[0]), ((-hw, hd), (-hw, -hd), lobes[1])):
        L = math.hypot(bx - ax, by - ay)
        tx, ty = (bx - ax) / L, (by - ay) / L
        for i in range(nl * m):
            t = i / (nl * m)
            o = amp * abs(sin(pi * nl * t)) ** 0.7
            pts.append((k * (ax + (bx - ax) * t + ty * o), k * (ay + (by - ay) * t - tx * o), z))
    return pts


def side_table(name='living.side_table'):
    """Barley-twist occasional table 0.47 x 0.37 x 0.72 in dark open-grain oak: scalloped pie-crust top (3 lobes
    per long side, 2 per short side, 22 mm, rounded edge), four deep rope-twist legs between square blocks, box
    stretchers."""
    mb = mo.MB()
    W = oak_dark()
    hw, hd = 0.222, 0.172
    loft(mb, [_piecrust(hw, hd, 0.698, k=0.975), _piecrust(hw, hd, 0.703), _piecrust(hw, hd, 0.714),
              _piecrust(hw, hd, 0.72, k=0.985)], W, caps=(True, False))
    mb.face(_piecrust(hw, hd, 0.72, k=0.985), W, (0, 0, 1), grain=0)
    mb.box((-0.20, -0.15, 0.63), (0.20, 0.15, 0.699), W, bev=0.003, grain=0)
    for sx in (-1, 1):
        mb.box((sx * 0.18 - 0.012, -0.13, 0.11), (sx * 0.18 + 0.012, 0.13, 0.14), W, bev=0.003, grain=1)
    for sy in (-1, 1):
        mb.box((-0.18, sy * 0.13 - 0.012, 0.11), (0.18, sy * 0.13 + 0.012, 0.14), W, bev=0.003, grain=0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.at(Tr(sx * 0.18, sy * 0.13, 0))
            mb.box((-0.02, -0.02, 0.0), (0.02, 0.02, 0.17), W, bev=0.002, grain=2)          # foot block
            mb.box((-0.02, -0.02, 0.56), (0.02, 0.02, 0.63), W, bev=0.002, grain=2)         # top block
            barley_twist(mb, 0.17, 0.56, 0.02, W)
    mb.at()
    return mb.finish(name)

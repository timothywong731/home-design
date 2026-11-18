"""Small, tested (Blender 5.1) architectural helpers. Import via sys.path or exec.
Units metres, Z up. All builders return a bpy Object linked to the active collection."""
import bpy, bmesh, math
from mathutils import Vector

def _obj(name, bm):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    return ob

def box(name, x0, y0, z0, x1, y1, z1):
    """Axis-aligned cuboid from min/max corners."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = ((x0 + x1) / 2 + v.co.x * (x1 - x0), (y0 + y1) / 2 + v.co.y * (y1 - y0),
                (z0 + z1) / 2 + v.co.z * (z1 - z0))
    return _obj(name, bm)

def cut(target, cutters, delete_cutters=True):
    """Boolean-subtract cutters (EXACT solver; 'FAST' was renamed 'FLOAT' in 5.0) and apply."""
    for c in cutters:
        m = target.modifiers.new("cut", 'BOOLEAN'); m.operation = 'DIFFERENCE'
        m.solver = 'EXACT'; m.object = c
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(target.evaluated_get(dg))
    old = target.data; target.modifiers.clear(); target.data = me; bpy.data.meshes.remove(old)
    if delete_cutters:
        for c in cutters: bpy.data.objects.remove(c, do_unlink=True)
    return target

def wall(name, p0, p1, height, thick, openings=(), z0=0.0):
    """Wall whose centre line runs p0->p1 (x,y). openings: (u_from_p0, width, sill, head) in metres.
    Wall is built along +X then rotated/placed, cutters are 1 cm oversize through the thickness."""
    (x0, y0), (x1, y1) = p0, p1
    L = math.hypot(x1 - x0, y1 - y0)
    w = box(name, 0, -thick / 2, z0, L, thick / 2, z0 + height)
    cs = [box("c", u, -thick, z0 + sill, u + wd, thick, z0 + head) for (u, wd, sill, head) in openings]
    if cs: cut(w, cs)
    w.rotation_euler = (0, 0, math.atan2(y1 - y0, x1 - x0)); w.location = (x0, y0, 0)
    return w

def sweep_profile(name, profile, path, closed=True):
    """Sweep a 2D profile along a horizontal polyline with mitred corners.
    profile: [(d, h)...] d = offset to the LEFT of travel (CCW path => into the room), h = height (m).
    path: [(x, y, z)...] (z = base height of the moulding). Faces are closed with a cap when open.
    Use for cornice, dado/picture rail, skirting, architrave (open path), window boards."""
    n, k = len(path), len(profile)
    P = [Vector(p) for p in path]
    def seg_n(a, b):
        d = (b - a); d.z = 0; d.normalize(); return Vector((-d.y, d.x, 0))
    rings = []
    for i in range(n):
        a = P[i - 1] if (i > 0 or closed) else None
        b = P[(i + 1) % n] if (i < n - 1 or closed) else None
        if a is not None and b is not None:
            n1, n2 = seg_n(a, P[i]), seg_n(P[i], b); m = (n1 + n2) / (1 + n1.dot(n2))
        elif b is not None: m = seg_n(P[i], b)
        else: m = seg_n(a, P[i])
        rings.append([P[i] + m * d + Vector((0, 0, h)) for d, h in profile])
    bm = bmesh.new()
    V = [[bm.verts.new(c) for c in r] for r in rings]
    segs = n if closed else n - 1
    for i in range(segs):
        for j in range(k):
            bm.faces.new((V[i][j], V[(i + 1) % n][j], V[(i + 1) % n][(j + 1) % k], V[i][(j + 1) % k]))
    if not closed:
        bm.faces.new(V[0]); bm.faces.new(V[-1][::-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _obj(name, bm)

# Handy profiles: (d, h). Skirting 18x120 mm with bullnose-ish top; cornice cove 100x100.
SKIRTING = [(0, 0), (0.018, 0), (0.018, 0.10), (0.012, 0.115), (0, 0.12)]
DADO_RAIL = [(0, 0), (0.025, 0), (0.025, 0.03), (0.015, 0.045), (0, 0.045)]
def cove(depth=0.10, drop=0.10, steps=8):
    """Concave cornice cove. Path CCW (left = into the room), base z = ceiling height."""
    return [(0, 0)] + [(depth * (1 - math.cos(a)), -drop + drop * math.sin(a))
                       for a in (math.pi / 2 * i / steps for i in range(steps + 1))]

def panel_door(name, w=0.762, h=1.981, t=0.044, stile=0.11, rail=0.14,
               mid_rail=0.16, depth=0.012):
    """Four-panel door leaf: slab with 2x2 recessed/raised panels (raised = +depth on both faces).
    Origin at hinge bottom corner, leaf in XZ plane, thickness along Y centred on 0."""
    leaf = box(name, 0, -t / 2, 0, w, t / 2, h)
    iw = (w - 2 * stile - stile) / 2          # two columns, middle stile = stile
    ih_top = (h - 2 * rail - mid_rail) * 0.45; ih_bot = (h - 2 * rail - mid_rail) - ih_top
    parts = [leaf]
    zs = [(rail, rail + ih_bot), (h - rail - ih_top, h - rail)]
    for (za, zb) in zs:
        for xa in (stile, stile + iw + stile):
            for s in (-1, 1):
                y0, y1 = (t / 2, t / 2 + depth) if s > 0 else (-t / 2 - depth, -t / 2)
                parts.append(box("pnl", xa, y0, za, xa + iw, y1, zb))
    return join(parts, name)

def join(objs, name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join(); o = bpy.context.view_layer.objects.active; o.name = name
    return o

def bevel(ob, width=0.002, segments=2, angle=30):
    """Catch-light bevel; limit by angle so flat faces stay clean."""
    m = ob.modifiers.new("bevel", 'BEVEL'); m.width = width; m.segments = segments
    m.limit_method = 'ANGLE'; m.angle_limit = math.radians(angle); m.harden_normals = True
    return m

def smooth_by_angle(ob, deg=30):
    """mesh.use_auto_smooth is gone (4.1+). Operator appends the 'Smooth by Angle' modifier."""
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.shade_auto_smooth(use_auto_smooth=True, angle=math.radians(deg))

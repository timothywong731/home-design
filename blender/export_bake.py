"""Lightmap UVs, Cycles lightmap bake, room probes and image encoding for blender/export.py.
Documented in blender/lib/README.md. Everything is driven by the custom props
obj['lm'] / obj['room'] / obj['no_export'] / obj['ix'] (blender/INTERACT.md), never by object names."""
import json
import math
from contextlib import contextmanager
from pathlib import Path

import bmesh
import bpy
import numpy as np
from mathutils import Vector
from mathutils.geometry import box_fit_2d, convex_hull_2d

UV = 'Lightmap'        # second UV layer -> TEXCOORD_1 in the GLB
DENSITY = 160.0        # target lightmap texels per metre inside house rooms (--density); export.atlas_rule scales it
MIN_AREA = 0.05        # m2 of surface: smaller lm='static' objects are demoted to 'dynamic' (probe-lit)
MARGIN = 1 / 512       # gap between lightmap islands as a fraction of the atlas (4 px at 2048); a constant
                       # fraction keeps the layout independent of the bake resolution
SOLID = 0.4            # islands filling less of their best-fit rectangle than this are cut up (rings, frames)
PERCENTILE = 99.5      # of the lit texels: the value that maps to 255 (brighter texels clip) ...
HEADROOM = 6.0         # ... but never more than this many times the median: 8 bits must not be spent on hot spots
FLOOR = 0.02           # ... the median of the texels brighter than this fraction of the PERCENTILE value (see encode)
EYE = 1.5              # probe height above the floor
MOVING = {'hinge', 'slide', 'clock'}   # ix types that move in the viewer: probe-lit, except door leaves
# Lights-off set (lights_off, bake_off): the dusk sky alone leaves windowless rooms black (median 0.0003, lit: 0.9)
# and the far end of the living room at 1 % of its lit level. So that a dark room stays readable, a cool
# ambient-occlusion term is added: AMBIENT_OFF of radiance on an open wall, falling off into corners and under
# furniture within AMBIENT_DIST metres. (Cycles' own "fast GI, add" does this in renders but not in bakes: measured.)
AMBIENT_OFF = 0.15
AMBIENT_TINT = (0.62, 0.8, 1.0)   # its colour as displayed, i.e. after the white balance (the sky itself shows deep blue)
AMBIENT_DIST = 1.0
PEAK_OFF = 12 * AMBIENT_OFF   # most that 255 stands for in the off set: sunlit patches (0.9) fit and the ambient level
                              # sits at pixel value 77 or higher (one 8-bit step = 2.5 %). The median is no guide
                              # there: half of a kitchen atlas is cabinet backs at zero.


def select(objs):
    bpy.context.view_layer.update()                          # drop objects removed since the last call
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]


def mesh_objects():
    return [o for o in bpy.context.scene.objects if o.type == 'MESH' and not o.get('no_export') and o.data.polygons]


# ------------------------------------------------------------------ interaction tags (blender/INTERACT.md)
def ix(o):
    """The interaction tag of an object as a dict, {} when it has none. obj['ix'] itself is never rewritten."""
    return json.loads(o['ix']) if 'ix' in o.keys() else {}


def state1(o):
    """Only there in the toggled state (water, flames, closed curtains, TV picture, fridge glow)."""
    d = ix(o)
    return d.get('t') == 'show' and d.get('when') == 1


def prepare_tagged():
    """Undo what IX.pose may have left in the saved file: every tagged object selectable (or the GLB export would
    drop it) and rendered, except the state-1 objects, which stay out of every bake, probe and still.
    -> (tagged objects, state-1 objects)."""
    tagged = [o for o in bpy.context.scene.objects if ix(o)]
    for o in tagged:
        o.hide_viewport = False
        o.hide_set(False)
        o.hide_render = state1(o)
    return tagged, [o for o in tagged if state1(o)]


@contextmanager
def lights_off():
    """The scene with every lamp switched off, for the lights-off lightmaps and probes: all light objects except
    suns and portals hidden, every emission strength 0 (AO distance set for bake_off). Restored on exit.
    Yields (lights hidden, emission sockets zeroed)."""
    sc = bpy.context.scene
    lamps = [o for o in sc.objects if o.type == 'LIGHT' and o.data.type != 'SUN' and not o.data.cycles.is_portal
             and not o.hide_render]
    glow = [(s, s.default_value) for m in bpy.data.materials if m.node_tree for n in m.node_tree.nodes
            for s in [n.inputs.get('Emission Strength' if n.type == 'BSDF_PRINCIPLED' else 'Strength')]
            if n.type in {'BSDF_PRINCIPLED', 'EMISSION'} and not s.is_linked and s.default_value]
    ws = sc.world.light_settings
    keep = ws.distance
    try:
        for o in lamps:
            o.hide_render = True
        for s, _ in glow:
            s.default_value = 0
        ws.distance = AMBIENT_DIST
        yield len(lamps), len(glow)
    finally:
        for o in lamps:
            o.hide_render = False
        for s, v in glow:
            s.default_value = v
        ws.distance = keep


def _signature(m):
    """What makes two modifiers do the same thing: type, plain settings, referenced datablocks, node inputs."""
    sig = [m.type]
    for p in m.bl_rna.properties:
        v = getattr(m, p.identifier, None)
        if p.type in {'BOOLEAN', 'INT', 'FLOAT', 'STRING', 'ENUM'} and not p.identifier.startswith(('show_', 'is_', 'name')):
            sig.append((p.identifier, v[:] if hasattr(v, '__len__') and not isinstance(v, (str, set, frozenset)) else v))
        elif p.type == 'POINTER' and hasattr(v, 'name_full'):
            sig.append((p.identifier, v.name_full))
    try:
        sig += [(k, repr(v)) for k, v in m.items()]          # geometry-nodes inputs
    except TypeError:                                         # other modifier types have no ID properties (5.x)
        pass
    return sig


def apply_modifiers(objs):
    """Bake every modifier stack into mesh data, so that lightmap UVs are made on the final faces and the GLB
    keeps linked duplicates linked: objects sharing a mesh AND an identical stack share the applied mesh."""
    dg = bpy.context.evaluated_depsgraph_get()
    cache, todo = {}, []
    for o in objs:
        if not o.modifiers:
            continue
        key = (o.data.name, repr([_signature(m) for m in o.modifiers]))
        if key not in cache:
            cache[key] = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
            cache[key].name = o.data.name
        todo.append((o, cache[key]))
    for o, me in todo:                      # assign after all evaluations: changing data invalidates the depsgraph
        o.modifiers.clear()
        o.data = me
    return len(todo), len(cache)


def area(o):
    a = np.empty(len(o.data.polygons), np.float32)
    o.data.polygons.foreach_get('area', a)
    return float(a.sum())


def _no_diffuse(mat):
    """Metal or glass: nothing for a lightmap to light (three.js lightMap only feeds the diffuse lobe)."""
    p = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None) if mat and mat.node_tree else None
    if p is None:
        return False
    metal, alpha = p.inputs['Metallic'], p.inputs['Alpha']
    return (not metal.is_linked and metal.default_value > 0.5) or (not alpha.is_linked and alpha.default_value < 0.99)


def classify(objs):
    """-> {room: [objects that get a baked lightmap]}; every object carries obj['room'] (export.retag). Decisions:
    - tagged objects that move (MOVING) or exist only in state 1 become lm='dynamic'; door leaves (obj['door'], or
      a tag with 'blocks') may keep the lightmap of the pose they are modelled in;
    - lm='static' objects under MIN_AREA, or made only of metal/glass, become lm='dynamic' (keeps their instancing);
    - remaining static objects that share mesh data are made single-user: lightmap UVs live in the mesh, so every
      instance needs its own copy to get its own texels."""
    rooms, demoted, unlinked = {}, 0, 0
    for o in objs:
        if o.get('lm') != 'static':
            continue
        d = ix(o)
        mats = [s.material for s in o.material_slots if s.material]
        if (state1(o) or (d.get('t') in MOVING and (d.get('on') or not (o.get('door') or 'blocks' in d))) or area(o) < MIN_AREA
                or (mats and all(_no_diffuse(m) for m in mats))):
            o['lm'] = 'dynamic'
            demoted += 1
            continue
        if o.data.users > 1:
            o.data = o.data.copy()
            unlinked += 1
        rooms.setdefault(o['room'], []).append(o)
    return rooms, demoted, unlinked


def atlas_size(m2, fill, density, cap):
    """Power-of-two atlas side nearest to `density` px/m for m2 of surface packed at `fill`, at most `cap`."""
    return int(min(cap, max(256, 2 ** round(math.log2(density * math.sqrt(m2 / fill))))))


def _uv_area(o):
    me = o.data
    me.calc_loop_triangles()
    tri = np.empty(len(me.loop_triangles) * 3, np.int32)
    me.loop_triangles.foreach_get('loops', tri)
    uv = np.empty(len(me.loops) * 2, np.float32)
    me.uv_layers[UV].uv.foreach_get('vector', uv)
    a, b, c = uv.reshape(-1, 2)[tri.reshape(-1, 3)].transpose(1, 0, 2)
    return float(np.abs((b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (b[:, 1] - a[:, 1]) * (c[:, 0] - a[:, 0])).sum() / 2)


def fit_box(pts):
    """Minimum-area rectangle of 2D points -> (R, lo, hi): the rows of pts @ R.T fill the box lo..hi."""
    p = np.asarray(pts, np.float64).reshape(-1, 2)
    hull = p[convex_hull_2d(p.tolist())]
    best = None
    for a in (0.0, box_fit_2d(hull.tolist()), -box_fit_2d(hull.tolist())):      # sign convention: try both
        R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
        q = hull @ R.T
        size = float(np.prod(q.max(0) - q.min(0)))
        if best is None or size < best[0] * 0.999:          # keep the axis-aligned box unless a turned one is smaller
            best = (size, R, q.min(0), q.max(0))
    return best[1:]


def _split_hollow(me):
    """Smart-project turns a skirting loop, an architrave or a window frame into one ring-shaped island whose
    bounding box is mostly empty. Cut such islands (fill of their best-fit rectangle < SOLID) in halves along
    their long axis until the pieces are solid strips, so the atlas is not wasted on holes."""
    bm = bmesh.new()
    bm.from_mesh(me)
    uvl = bm.loops.layers.uv[UV]
    shift = [0]

    def same(l, r):                                           # do faces l.face / r.face share this edge in UV space?
        a, b = l[uvl].uv, l.link_loop_next[uvl].uv
        c, d = (r[uvl].uv, r.link_loop_next[uvl].uv) if r.vert == l.vert else (r.link_loop_next[uvl].uv, r[uvl].uv)
        return (a - c).length_squared + (b - d).length_squared < 1e-10

    def cut(faces, depth):
        uv = [np.array([l[uvl].uv for l in f.loops]) for f in faces]
        R, lo, hi = fit_box(np.concatenate(uv))
        used = sum(abs(np.cross(p, np.roll(p, -1, 0)).sum()) / 2 for p in uv)
        if len(faces) > 1 and depth < 12 and used < SOLID * float(np.prod(hi - lo)):
            for axis in np.argsort(lo - hi):                  # long axis first; the short one separates an L
                side = [(p @ R.T).mean(0)[axis] < (lo[axis] + hi[axis]) / 2 - 1e-9 for p in uv]
                if 0 < sum(side) < len(faces):
                    cut([f for f, s in zip(faces, side) if s], depth + 1)
                    cut([f for f, s in zip(faces, side) if not s], depth + 1)
                    return
        if depth:                                             # a cut-off piece: move it away so it is its own island
            shift[0] += 1
            for f in faces:
                for l in f.loops:
                    l[uvl].uv.x += 4.0 * shift[0]

    seen = set()
    for f0 in bm.faces:
        if f0 in seen:
            continue
        island = [f0]
        seen.add(f0)
        for f in island:                                      # flood fill over UV-connected faces
            for l in f.loops:
                for r in l.link_loops:
                    if r.face not in seen and same(l, r):
                        seen.add(r.face)
                        island.append(r.face)
        cut(island, 0)
    if shift[0]:
        bm.to_mesh(me)
    bm.free()
    return shift[0]


def unwrap(objs):
    """Second UV layer 'Lightmap' for all objects of one atlas: smart-project each, cut hollow islands, equalise
    the texel density (world area, objects are at scale 1) and pack everything into one 0-1 square.
    The UV operators run on welded temporary copies: the library meshes split their vertices at every hard edge,
    which would make each moulding facet an island of its own (half the atlas lost to padding). Loop order
    survives welding, so the UVs are copied back loop for loop. Returns (fill of the atlas, islands cut)."""
    tmp = []
    for o in objs:
        me = o.data
        if not me.uv_layers:
            me.uv_layers.new(name='UVMap')                   # TEXCOORD_0 must exist or Lightmap would become it
        while len(me.uv_layers) > 1:                         # ... and nothing may sit between them
            me.uv_layers.remove(me.uv_layers[len(me.uv_layers) - 1])
        me.uv_layers.new(name=UV)
        t = o.copy()
        t.data = me.copy()
        bpy.context.scene.collection.objects.link(t)
        t.data.uv_layers.active = t.data.uv_layers[UV]       # active = the layer the UV operators edit
        bm = bmesh.new()
        bm.from_mesh(t.data)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        if len(bm.faces) == len(me.polygons) and sum(len(f.loops) for f in bm.faces) == len(me.loops):
            bm.to_mesh(t.data)                               # else a face collapsed: keep this copy unwelded
        bm.free()
        tmp.append(t)
    select(tmp)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0)
    bpy.ops.object.mode_set(mode='OBJECT')
    cuts = sum(_split_hollow(t.data) for t in tmp)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.select_all(action='SELECT')
    bpy.ops.uv.average_islands_scale()
    # ponytail: AABB packing, fast and predictable for thousands of islands (they are solid by now); 'CONCAVE'
    # measured no tighter on the shell and 10x slower
    bpy.ops.uv.pack_islands(rotate=True, margin_method='FRACTION', margin=MARGIN, shape_method='AABB')
    bpy.ops.object.mode_set(mode='OBJECT')
    for o, t in zip(objs, tmp):
        uv = np.empty(len(o.data.loops) * 2, np.float32)
        t.data.uv_layers[UV].uv.foreach_get('vector', uv)
        o.data.uv_layers[UV].uv.foreach_set('vector', uv)
        me = t.data
        bpy.data.objects.remove(t)
        bpy.data.meshes.remove(me)
    return sum(_uv_area(o) for o in objs), cuts


def bake(name, objs, res, kind='DIFFUSE'):
    """Cycles DIFFUSE direct+indirect (no albedo) of one atlas -> float RGBA array (res*res, 4), scene linear,
    still noisy (see denoise). kind='AO': ambient occlusion instead (grey, 1 = open).
    The objects are baked as ONE joined temporary copy (a bake per object would re-sync the whole scene each time);
    the originals are hidden from the render meanwhile so the copy does not shadow itself."""
    sc = bpy.context.scene
    img = bpy.data.images.new('lm_' + name, res, res, alpha=False, float_buffer=True)
    # leaves modelled standing open are probe-lit and stay out of the bake: no shadow is left behind when they close
    ghosts = [o for o in sc.objects if not o.hide_render and ix(o).get('t') in MOVING and ix(o).get('on')]
    for o in ghosts:
        o.hide_render = True
    dup = []
    for o in objs:
        d = o.copy()
        d.data = o.data.copy()
        sc.collection.objects.link(d)
        dup.append(d)
        o.hide_render = True
    if len(dup) > 1:
        with bpy.context.temp_override(active_object=dup[0], selected_editable_objects=dup):
            bpy.ops.object.join()
    j = dup[0]
    j.data.uv_layers.active = j.data.uv_layers[UV]
    nodes = []
    for m in {s.material for s in j.material_slots if s.material}:
        n = m.node_tree.nodes.new('ShaderNodeTexImage')      # unconnected + active = bake target
        n.image, n.select = img, True
        m.node_tree.nodes.active = n
        nodes.append((m.node_tree, n))
    select([j])
    try:
        bpy.ops.object.bake(type=kind, pass_filter={'DIRECT', 'INDIRECT'}, margin=max(4, res // 128),
                            margin_type='EXTEND', use_clear=True, target='IMAGE_TEXTURES')
    finally:
        for nt, n in nodes:
            nt.nodes.remove(n)
        me = j.data
        bpy.data.objects.remove(j)
        bpy.data.meshes.remove(me)
        for o in objs + ghosts:
            o.hide_render = False
    px = np.empty(res * res * 4, np.float32)
    img.pixels.foreach_get(px)
    bpy.data.images.remove(img)
    return px.reshape(-1, 4)


def bake_off(name, objs, res, ambient):
    """Lights-off lightmap of one atlas; call inside lights_off(). Daylight bake + ambient (rgb) x occlusion."""
    px = bake(name, objs, res)
    px[:, :3] += bake(name, objs, res, 'AO')[:, :1] * np.asarray(ambient, np.float32)
    return px


# ------------------------------------------------------------------ encoding
def wb_matrix():
    """3x3 scene-linear matrix of the scene's view white balance (lighting.WHITE_BALANCE / WHITE_TINT), measured by
    pushing three colours through Blender's own display pipeline. Bakes ignore view settings, so the lightmaps and
    probes get the white balance of the previews multiplied in here."""
    sc = bpy.context.scene
    vs, fmt = sc.view_settings, sc.render.image_settings
    if not getattr(vs, 'use_white_balance', False):
        return np.eye(3)
    P = np.array([[.2, .1, .1], [.1, .2, .1], [.1, .1, .2]])
    src = bpy.data.images.new('wb_probe', 3, 1, alpha=False, float_buffer=True)
    src.pixels.foreach_set(np.hstack([P, np.ones((3, 1))]).astype(np.float32).ravel())
    keep = (vs.view_transform, vs.look, vs.exposure, vs.gamma, fmt.file_format, fmt.color_mode, fmt.color_depth)
    path = str(Path(bpy.app.tempdir) / 'wb_probe.png')
    try:
        vs.view_transform, vs.look, vs.exposure, vs.gamma = 'Standard', 'None', 0.0, 1.0
        fmt.file_format, fmt.color_mode, fmt.color_depth = 'PNG', 'RGB', '16'
        src.save_render(path, scene=sc)
    finally:
        vs.view_transform, vs.look, vs.exposure, vs.gamma, fmt.file_format, fmt.color_mode, fmt.color_depth = keep
    back = bpy.data.images.load(path)
    out = np.empty(12, np.float32)
    back.pixels.foreach_get(out)                              # 16-bit sRGB file -> linear floats
    bpy.data.images.remove(src)
    bpy.data.images.remove(back)
    return out.reshape(3, 4)[:, :3].T.astype(np.float64) @ np.linalg.inv(P.T)


def encode(px, w, h, path, M, quality=93, cap=None):
    """Scene-linear float pixels (n, 3+) -> 8-bit sRGB JPEG with the white balance M applied.
    Returns the intensity k of the encoding:  linear = srgb_decode(pixel / 255) * k.
    k is the PERCENTILE of the lit texels, at most cap (default: HEADROOM x the median of the really lit ones), so hot spots next to lamps clip
    instead of costing everything else its precision (one 8-bit step is ~2 % at the median); +-1 LSB triangular
    dither before quantising hides the banding on smooth ceilings."""
    rgb = np.maximum(px[:, :3].astype(np.float64) @ M.T, 0)
    peak = rgb.max(axis=1)
    lit = peak[peak > 0]
    if lit.size:
        top = float(np.percentile(lit, PERCENTILE))
        # the median is taken over the texels that are really lit (above FLOOR x top): cabinet backs and the wall behind
        # furniture that stands a few cm off it are faintly lit, fill half a kitchen atlas and would otherwise drag the
        # median down until every visible surface clips (integration: kitchen k 0.10 instead of ~2.5)
        body = lit[lit > FLOOR * top]
        k = max(min(top, cap or HEADROOM * float(np.median(body if body.size else lit))), 1e-3)
    else:
        k = 1.0
    v = np.clip(rgb / k, 0, 1)
    v = np.where(v <= 0.0031308, v * 12.92, 1.055 * v ** (1 / 2.4) - 0.055)
    rng = np.random.default_rng(0)
    v += (rng.random(v.shape) - rng.random(v.shape)) / 255
    buf = np.ones((w * h, 4), np.float32)
    buf[:, :3] = np.clip(v, 0, 1)
    out = bpy.data.images.new('encode', w, h, alpha=False)   # byte image: pixels are stored as given (display space)
    out.pixels.foreach_set(buf.ravel())
    out.filepath_raw, out.file_format = str(path), 'JPEG'
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    out.save(quality=quality)
    bpy.data.images.remove(out)
    return round(k, 5)


# ------------------------------------------------------------------ probes
def probe_point(poly, z):
    """Most open spot of a room at height z: grid point inside the polygon with the largest mean free distance
    over 16 horizontal directions + up (each capped at 4 m), at least 0.2 m clear of everything. Keeps the probe
    out of furniture, chandeliers and the under-stairs cupboard. None when the room has no such point."""
    sc, dg = bpy.context.scene, bpy.context.evaluated_depsgraph_get()
    dirs = [Vector((math.cos(a), math.sin(a), 0)) for a in np.arange(16) * math.pi / 8] + [Vector((0, 0, 1)), Vector((0, 0, -1))]
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    mid = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)     # tie-break: open ground scores 4 m everywhere
    best = None
    for x in np.arange(min(xs) + 0.2, max(xs), 0.2):
        for y in np.arange(min(ys) + 0.2, max(ys), 0.2):
            if not _inside(x, y, poly):
                continue
            o, d = Vector((x, y, z)), []
            for v in dirs:
                hit, loc, *_ = sc.ray_cast(dg, o, v, distance=4.0)
                d.append((loc - o).length if hit else 4.0)
            score = sum(d[:-1]) - 0.01 * math.hypot(x - mid[0], y - mid[1])     # the floor below does not count as open
            if min(d) >= 0.2 and (best is None or score > best[0]):
                best = (score, (round(float(x), 3), round(float(y), 3), round(z, 3)))
    return best and best[1]


def _inside(x, y, poly):
    inside = False
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            inside = not inside
    return inside


def _render_exr(w, h, path):
    """bpy.ops.render.render into a w x h 32-bit EXR -> float pixels (w*h, 4); render settings are restored."""
    sc = bpy.context.scene
    r, fmt = sc.render, sc.render.image_settings
    keep = (r.resolution_x, r.resolution_y, r.resolution_percentage, r.filepath, fmt.file_format, fmt.color_mode, fmt.color_depth)
    try:
        r.resolution_x, r.resolution_y, r.resolution_percentage, r.filepath = w, h, 100, str(path)
        fmt.file_format, fmt.color_mode, fmt.color_depth = 'OPEN_EXR', 'RGB', '32'
        bpy.ops.render.render(write_still=True)
    finally:
        r.resolution_x, r.resolution_y, r.resolution_percentage, r.filepath = keep[:4]
        fmt.file_format, fmt.color_mode, fmt.color_depth = keep[4:]
    img = bpy.data.images.load(str(path))
    px = np.empty(w * h * 4, np.float32)
    img.pixels.foreach_get(px)
    bpy.data.images.remove(img)
    return px.reshape(-1, 4)


def denoise(px, res, tmp):
    """OpenImageDenoise over a baked atlas. Cycles ignores scene.cycles.use_denoising when baking (measured on
    5.1.1: identical noise with it on or off), so the atlas goes through a compositor Denoise node instead; with
    no Render Layers node the scene itself is not rendered (0.2 s for 1024 px). The bake margin has already
    extended every island into the gaps, which keeps the filter from pulling black into island borders."""
    sc = bpy.context.scene
    img = bpy.data.images.new('lm_noisy', res, res, alpha=False, float_buffer=True)
    img.pixels.foreach_set(px.ravel())
    tree = bpy.data.node_groups.new('lm_denoise', 'CompositorNodeTree')
    tree.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    src, dn, out = (tree.nodes.new(t) for t in ('CompositorNodeImage', 'CompositorNodeDenoise', 'NodeGroupOutput'))
    src.image = img
    tree.links.new(src.outputs['Image'], dn.inputs['Image'])
    tree.links.new(dn.outputs['Image'], out.inputs['Image'])
    keep = (sc.compositing_node_group, sc.render.use_compositing)
    try:
        sc.compositing_node_group, sc.render.use_compositing = tree, True
        return _render_exr(res, res, Path(tmp) / 'denoise.exr')
    finally:
        sc.compositing_node_group, sc.render.use_compositing = keep
        bpy.data.node_groups.remove(tree)
        bpy.data.images.remove(img)


@contextmanager
def _pano(pos, samples):
    """Equirectangular scene camera at pos facing +X with Z up: the image centre is +X and the image runs towards
    -Y to the right, the three.js equirect layout after the (x, z, -y) axis swap (no rotation in the viewer)."""
    sc = bpy.context.scene
    cam = bpy.data.cameras.new('probe')
    cam.type, cam.panorama_type, cam.clip_start = 'PANO', 'EQUIRECTANGULAR', 0.02
    ob = bpy.data.objects.new('probe', cam)
    ob.location, ob.rotation_euler = pos, (math.pi / 2, 0, -math.pi / 2)
    sc.collection.objects.link(ob)
    keep = (sc.camera, sc.cycles.samples)
    try:
        sc.camera, sc.cycles.samples = ob, samples
        yield
    finally:
        sc.camera, sc.cycles.samples = keep
        bpy.data.objects.remove(ob)
        bpy.data.cameras.remove(cam)


def render_probe(pos, res, samples, tmp):
    """Equirectangular Cycles panorama at pos -> float pixels (res * res/2, 4), scene linear."""
    with _pano(pos, samples):
        return _render_exr(res, res // 2, Path(tmp) / 'probe.exr')


def render_sky(path, w=2048, samples=16):
    """The world alone (every object hidden from the render) as an equirect panorama in the probes' orientation,
    saved as the DISPLAYED 8-bit image: the scene's view transform, look, exposure and white balance are in the
    pixels, because three.js does not tone-map an sRGB scene.background. -> '#rrggbb', the mean displayed colour of
    the upper half (the sky proper; below the horizon the viewer sees it only past the edge of the site)."""
    sc = bpy.context.scene
    r, fmt = sc.render, sc.render.image_settings
    hidden = [(o, o.hide_render) for o in sc.objects]
    keep = (r.resolution_x, r.resolution_y, r.resolution_percentage, r.filepath, r.film_transparent,
            fmt.file_format, fmt.color_mode, fmt.quality)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    try:
        for o, _ in hidden:
            o.hide_render = True
        r.resolution_x, r.resolution_y, r.resolution_percentage, r.filepath, r.film_transparent = w, w // 2, 100, str(path), False
        fmt.file_format, fmt.color_mode, fmt.quality = 'JPEG', 'RGB', 92
        with _pano((0, 0, 1.5), samples):
            bpy.ops.render.render(write_still=True)
    finally:
        for o, v in hidden:
            o.hide_render = v
        r.resolution_x, r.resolution_y, r.resolution_percentage, r.filepath, r.film_transparent = keep[:5]
        fmt.file_format, fmt.color_mode, fmt.quality = keep[5:]
    img = bpy.data.images.load(str(path))
    img.colorspace_settings.name = 'Non-Color'               # the stored display bytes as they are
    px = np.empty(w * (w // 2) * 4, np.float32)
    img.pixels.foreach_get(px)
    bpy.data.images.remove(img)
    top = px.reshape(w // 2, w, 4)[w // 4:, :, :3]           # rows run bottom-up
    return '#%02x%02x%02x' % tuple(int(round(v * 255)) for v in top.reshape(-1, 3).mean(0))

"""Export a saved build to the web viewer: one GLB per level, lightmaps (lights on and off), probes, sky, manifest
(schema 2), footprints, hero renders. Documented in blender/lib/README.md; contract: blender/MULTILEVEL.md
section 10; interaction tags: blender/INTERACT.md.

blender -b [--factory-startup] build/home.blend --python blender/export.py -- --out docs/assets [--house spec/house.json]
        [--levels G,1] [--rooms a,b] [--bake-res 4096] [--samples 256] [--density 160] [--probe-res 1024] [--skip-bake]
        [--skip-off] [--renders] [--stills-only] [--still-res 1920x1080] [--tmp build/export]
"""
import argparse
import importlib
import json
import shutil
import struct
import subprocess
import sys
import time
import traceback
from pathlib import Path

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
T0 = time.time()
GLTF_TRANSFORM = 'npx --yes @gltf-transform/cli@4.5.1'

# ---- knobs and budgets (MULTILEVEL.md sections 5 and 10)
ATLAS_CAP = {}                                   # room -> largest atlas side: the one knob when a budget fails
NONCOLOUR_MAX = 512                              # px: cap of the normal and ORM maps in the GLBs (colour maps: 2048)
FAR_ROOMS = ('facade', 'roof', 'neighbours')     # quarter density, no lights-off atlas, never named by a switch
SITE_NAMES = {'front': 'Front', 'side_passage': 'Side passage', 'garden': 'Garden', 'shed': 'Shed'}
LOAD_ORDER = ('G', 'X', '1', '2', 'B')
MB = 1e6
TRIANGLES = {'G': 850e3, '1': 1.3e6, '2': 850e3, 'B': 150e3, 'X': 850e3}     # the numbers of build.py report_tris
TRIANGLES_ALL = 4.0e6
GLB_MAX, GLB_G_MAX, FILE_MAX, FIRST_VIEW_MAX, SITE_MAX = 40 * MB, 21.5 * MB, 50 * MB, 35 * MB, 300 * MB
ATLAS_BYTES, PROBE_BYTES = 2.7 * MB, 0.1 * MB    # first-view estimate before the bake: a 4096 px atlas, a probe


def log(msg):
    print(f'[export {time.time() - T0:6.1f}s] {msg}', flush=True)


def parse():
    ap = argparse.ArgumentParser(prog='export.py')
    ap.add_argument('--out', default='docs/assets')
    ap.add_argument('--house', default='spec/house.json', help='house json, schema 1 or 2')
    ap.add_argument('--levels', default='', help='write only these level GLBs; without --rooms also bake only their rooms')
    ap.add_argument('--rooms', default='', help='bake / render only these rooms (others keep their old images)')
    ap.add_argument('--bake-res', type=int, default=4096, help='upper bound of the lightmap atlas side')
    ap.add_argument('--samples', type=int, default=256, help='Cycles samples for lightmaps and probes')
    ap.add_argument('--density', type=float, default=None, help='lightmap texels per metre in house rooms (default 160)')
    ap.add_argument('--probe-res', type=int, default=1024, help='probe panorama width')
    ap.add_argument('--skip-bake', action='store_true', help='no lightmaps or probes: GLBs, manifest, footprints only')
    ap.add_argument('--skip-off', action='store_true', help='no lights-off lightmaps / probes (rebaked rooms lose theirs)')
    ap.add_argument('--tmp', default='build/export', help='scratch directory (raw GLBs, EXRs): one per concurrent run')
    ap.add_argument('--renders', action='store_true', help='hero stills into <out>/../renders')
    ap.add_argument('--stills-only', action='store_true', help='only the hero stills: no bake, GLB or manifest')
    ap.add_argument('--still-res', default='1920x1080', help='hero still size (smaller for framing tests)')
    a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    a.out, a.tmp, a.house = (ROOT / a.out).resolve(), (ROOT / a.tmp).resolve(), (ROOT / a.house).resolve()
    a.rooms = [s for s in a.rooms.split(',') if s]
    a.levels = [s for s in a.levels.split(',') if s]
    a.still_res = tuple(int(v) for v in a.still_res.split('x'))
    return a


# ------------------------------------------------------------------ rooms, levels, tags
def room_table(h):
    """rooms[] of the manifest: every house room, then each pseudo-room that has walkable ground, with the largest
    walkable polygon tagged to it (a zone or a building room: forecourt, side_passage, deck, the shed workshop)."""
    from lib import ctx as C
    out = [dict(id=rid, level=h.level(rid), kind=h.kind(rid), name=r['name'], polygon=r['polygon'],
                floorZ=r['floorZ'], ceilZ=r.get('ceilingZ')) for rid, r in h.rooms.items()]
    for p in C.PSEUDO_ROOMS:
        cand = [(z['polygon'], z['z']) for z in h.zones.values() if z.get('room') == p and z.get('walk', True)]
        cand += [(r['polygon'], r['floorZ']) for rid, r in h.building_rooms.items()
                 if h.tag_room(rid) == p and r.get('walk', True)]
        if cand:
            poly, z = max(cand, key=lambda c: abs(C.poly_area(c[0])))
            out.append(dict(id=p, level='X', kind='site', name=SITE_NAMES.get(p, p), polygon=poly, floorZ=z, ceilZ=None))
    return out


def level_table(h, rooms):
    """levels[] of the manifest without the GLB fields. cutZ = lowest ceiling of the level's kind-'room' rooms - 0.07."""
    out = [dict(id=l, name=h.level_info[l]['name'], datumZ=h.level_info[l]['datumZ'],
                cutZ=round(min(r['ceilZ'] for r in rooms if r['level'] == l and r['kind'] == 'room') - 0.07, 3),
                rooms=h.rooms_on(l)) for l in h.levels]
    if h.schema == 2:
        site = [r['floorZ'] for r in rooms if r['level'] == 'X']
        out.append(dict(id='X', name='Outside', datumZ=min(site, default=0.0), cutZ=None, rooms=h.rooms_on('X')))
    return out


def retag(h):
    """obj['room'] and obj['level'] as the export needs them on everything that can reach a GLB: a room that is
    neither a house room nor a pseudo-room becomes 'neighbours' (WARNING: the phase-1 build has 'shell'), and the
    level is ALWAYS the level of the room (MULTILEVEL.md section 1), whatever the file says."""
    from lib import ctx as C
    known, odd, fixed = set(h.rooms) | set(C.PSEUDO_ROOMS), {}, []
    for o in bpy.context.scene.objects:
        if o.type in {'LIGHT', 'CAMERA'}:
            continue
        room = o.get('room')
        if room not in known:
            odd.setdefault(room, []).append(o.name)
            room = o['room'] = 'neighbours'
        if o.get('level') != h.level(room):
            if 'level' in o.keys():
                fixed.append(o.name)
            o['level'] = h.level(room)
    for room, names in odd.items():
        log(f'WARNING: {len(names)} objects of unknown room {room!r} exported as neighbours: {names[:6]}')
    if fixed:
        log(f'WARNING: obj["level"] was not the level of the room on {len(fixed)} objects, corrected: {fixed[:6]}')


def check_ix(h, tagged):
    """Interaction tags the viewer cannot serve: a group spread over two level GLBs (interactions start per level
    as each GLB arrives) and a switch naming a room that has no lights-off atlas."""
    import export_bake as EB
    from lib import ctx as C
    groups, known = {}, set(h.rooms) | set(C.PSEUDO_ROOMS)
    for o in tagged:
        d = EB.ix(o)
        groups.setdefault(d.get('g', o.name), set()).add(o['level'])
        rooms = set(d.get('rooms', []) if d.get('t') in {'light', 'lamp'} else [])
        assert not rooms & set(FAR_ROOMS), f'{o.name}: a switch cannot name {sorted(rooms & set(FAR_ROOMS))}'
        if rooms - known:
            log(f'WARNING: {o.name} switches unknown rooms {sorted(rooms - known)}')
    split = {g: sorted(v) for g, v in groups.items() if len(v) > 1}
    assert not split, f'interaction groups spread over several levels: {dict(list(split.items())[:5])}'


def atlas_rule(h, room, density, bake_res):
    """(texels per metre aimed for, largest side) of a room's atlas: house rooms full density up to 4096, exterior
    rooms (balcony, pseudo-rooms) half up to 2048, facade / roof / neighbours a quarter; ATLAS_CAP trims further."""
    ext = h.is_exterior(room)
    return (density * (0.25 if room in FAR_ROOMS else 0.5 if ext else 1.0),
            min(bake_res, 2048 if ext else 4096, ATLAS_CAP.get(room, bake_res)))


def budget(rows):
    """Log (label, value, limit, unit 'MB' | 'tris') rows; -> the labels that are over their limit."""
    over = []
    for label, value, limit, unit in rows:
        k = MB if unit == 'MB' else 1e3
        log(f'budget {label:24s} {value / k:9.2f} / {limit / k:.2f} {"MB" if unit == "MB" else "k triangles"}'
            f'{"" if value <= limit else "   OVER"}')
        if value > limit:
            over.append(label)
    return over


def sun_dir():
    """Unit vector TO the sun in the house frame, from the scene's sun lamp (light travels along its local -Z)."""
    from mathutils import Vector
    sun = next((o for o in bpy.context.scene.objects if o.type == 'LIGHT' and o.data.type == 'SUN'), None)
    if sun is None:
        from lib import lighting
        v = -Vector(lighting.SUN_DIR)
    else:
        v = sun.matrix_world.to_3x3() @ Vector((0, 0, 1))
    return [round(c, 4) for c in v.normalized()]


# ------------------------------------------------------------------ GLB
def flatten():
    """Clear every parent, keeping world transforms. A glTF node that has both a mesh and children gets its mesh
    moved into an unnamed child by the quantisation of glTF-Transform, and the viewer could then no longer tell a
    lightmapped cabinet from the probe-lit handles parented to it. Flat, every node is a named mesh with its own
    extras. Call after footprints() (which needs the children)."""
    bpy.context.view_layer.update()
    for o in [o for o in bpy.context.scene.objects if o.parent]:
        mw = o.matrix_world.copy()
        o.parent = None
        o.matrix_world = mw
    bpy.context.view_layer.update()


def level_objects(level):
    """What goes into glb/<level>.glb: everything of that level except lights, cameras and obj['no_export']."""
    return [o for o in bpy.context.scene.objects
            if o.type not in {'LIGHT', 'CAMERA'} and not o.get('no_export') and o.get('level') == level]


def export_glb(path, objs):
    """The given objects, +Y up, custom props as extras, both UV sets, textures embedded in their source format
    (JPEG). Modifiers were applied by export_bake.apply_modifiers."""
    import export_bake as EB
    EB.select(objs)
    bpy.ops.export_scene.gltf(
        filepath=str(path), export_format='GLB', use_selection=True, export_apply=True, export_yup=True,
        export_texcoords=True, export_normals=True, export_tangents=False, export_materials='EXPORT',
        export_image_format='AUTO', export_extras=True, export_cameras=False, export_lights=False,
        export_animations=False, export_skins=False, export_morph=False, export_gpu_instances=False)


def compress(raw, out):
    """glTF-Transform: textures capped at 2048 (normal / ORM maps at NONCOLOUR_MAX: all five level GLBs together decoded
    to 880 MB of RGBA8 + mips, 390 MB of it in those maps), colour textures to WebP (normal / ORM maps stay JPEG: recompressing
    them only adds artefacts), meshopt geometry. No dedup / join / instance / prune / simplify: those drop the
    unused-looking TEXCOORD_1, merge named nodes or lose the extras."""
    a, b = raw, raw.with_suffix('.tmp.glb')
    nc = ' --width {0} --height {0}'.format(NONCOLOUR_MAX)
    for step in ('resize {a} {b} --width 2048 --height 2048',
                 'resize {a} {b} --pattern "*_nrm"' + nc,     # normal / ORM maps of the material library (named
                 'resize {a} {b} --pattern "*_orm"' + nc,     # <key>_nrm / <key>_orm): 45 % of the decoded texture memory
                 'webp {a} {b} --slots "{{baseColorTexture,emissiveTexture}}" --quality 88',
                 'meshopt {a} {b} --level medium --quantize-texcoord 14'):
        cmd = f'{GLTF_TRANSFORM} ' + step.format(a=f'"{a}"', b=f'"{b}"')
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
        if r.returncode:
            raise RuntimeError(f'{cmd}\n{r.stdout}\n{r.stderr}')
        shutil.move(b, out)
        a = out


def glb_json(path):
    with open(path, 'rb') as f:
        f.seek(12)
        n, _ = struct.unpack('<I4s', f.read(8))
        return json.loads(f.read(n))


def world_verts(o):
    """Vertices of a mesh object in world space, (n, 3)."""
    co = np.empty(len(o.data.vertices) * 3, np.float32)
    o.data.vertices.foreach_get('co', co)
    return co.reshape(-1, 3) @ np.array(o.matrix_world.to_3x3()).T + np.array(o.matrix_world.translation)


def _corners(lo, hi):
    return np.array([[(lo, hi)[c >> k & 1][k] for k in range(3)] for c in range(8)], float)


def tagged_boxes(objs):
    """{name: (obj['ix'], world box (lo, hi) in glTF axes (x, z, -y) or None)} of the interaction-tagged objects:
    what check_glb compares the GLB nodes with. Take it before flatten(), so that flatten is checked too.
    The box is that of the 8 corners of the object's LOCAL bounding box, which is all a GLB accessor's min / max
    give: for a leaf modelled standing open at 85 degrees it is larger than the box of the vertices."""
    bpy.context.view_layer.update()
    out = {}
    for o in objs:
        box = None
        if o.type == 'MESH' and len(o.data.vertices):
            co = np.empty(len(o.data.vertices) * 3, np.float32)
            o.data.vertices.foreach_get('co', co)
            co = co.reshape(-1, 3)
            v = _corners(co.min(0), co.max(0)) @ np.array(o.matrix_world.to_3x3()).T + np.array(o.matrix_world.translation)
            v = v[:, [0, 2, 1]] * (1, 1, -1)
            box = (v.min(0), v.max(0))
        out[o.name] = (o['ix'], box)
    return out


def _node_matrix(n):
    if 'matrix' in n:
        return np.array(n['matrix'], float).reshape(4, 4).T
    x, y, z, w = n.get('rotation', (0, 0, 0, 1))
    m = np.eye(4)
    m[:3, :3] = np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                          [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                          [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]) * n.get('scale', (1, 1, 1))
    m[:3, 3] = n.get('translation', (0, 0, 0))
    return m


def _check_tagged(g, tagged, where):
    """Every interaction-tagged object is still its own childless root node with its name, its 'ix' string byte for
    byte, and its geometry where Blender had it (world box within 1 mm: flatten, the exporter and the quantisation
    of glTF-Transform all move transforms around)."""
    index = {n.get('name'): i for i, n in enumerate(g['nodes'])}
    roots = set(g['scenes'][g.get('scene', 0)]['nodes'])
    assert 'EXT_mesh_gpu_instancing' not in g.get('extensionsUsed', []), f'{where}: GPU instancing swallows nodes'
    for name, (tag, box) in tagged.items():
        i = index.get(name)
        assert i is not None, f'{where}: tagged object {name} is not a node of the GLB'
        n = g['nodes'][i]
        assert i in roots and not n.get('children'), f'{where}: tagged node {name} is not a childless root node'
        assert n.get('extras', {}).get('ix') == tag, f'{where}: ix of {name} changed: {n.get("extras", {}).get("ix")!r}'
        if box is None:
            continue
        assert 'mesh' in n, f'{where}: tagged node {name} lost its mesh'
        m, los, his = _node_matrix(n), [], []
        for prim in g['meshes'][n['mesh']]['primitives']:
            a = g['accessors'][prim['attributes']['POSITION']]
            q = {5120: 127, 5121: 255, 5122: 32767, 5123: 65535}[a['componentType']] if a.get('normalized') else 1
            los.append(np.array(a['min']) / q)
            his.append(np.array(a['max']) / q)
        pts = _corners(np.min(los, 0), np.max(his, 0)) @ m[:3, :3].T + m[:3, 3]      # local box, as tagged_boxes()
        err = max(np.abs(pts.min(0) - box[0]).max(), np.abs(pts.max(0) - box[1]).max())
        assert err < 1e-3, f'{where}: tagged node {name} moved by {err:.4f} m'


def check_glb(path, lightmapped, ix=()):
    """The check that fails when the export breaks: every lightmapped object is a named mesh node whose primitives
    all carry TEXCOORD_1, extras survived, no lights or cameras, interaction-tagged objects intact (ix = tagged_boxes()).
    Returns a summary dict."""
    g = glb_json(path)
    nodes = {n.get('name'): n for n in g['nodes']}
    acc = g['accessors']
    _check_tagged(g, dict(ix), path.name)
    bad = [name for name in lightmapped if 'mesh' not in nodes.get(name, {}) or
           any('TEXCOORD_1' not in p['attributes'] for p in g['meshes'][nodes[name]['mesh']]['primitives'])]
    assert not bad, f'lightmapped objects without TEXCOORD_1 in {path.name}: {bad[:10]}'
    assert not g.get('cameras') and 'KHR_lights_punctual' not in g.get('extensionsUsed', []), 'lights/cameras in the GLB'
    meshed = [n['mesh'] for n in g['nodes'] if 'mesh' in n]
    tagged = sum('kind' in n.get('extras', {}) for n in g['nodes'])
    assert tagged, 'custom props (extras) missing from the GLB nodes'
    tris = sum(acc[p['indices']]['count'] // 3 for m in meshed for p in g['meshes'][m]['primitives'])
    return dict(nodes=len(g['nodes']), meshes=len(g['meshes']), instanced_nodes=len(meshed) - len(set(meshed)),
                triangles=tris, materials=len(g.get('materials', [])), images=len(g.get('images', [])),
                nodes_with_extras=tagged, interactive=len(dict(ix)), extensions=g.get('extensionsUsed', []), bytes=path.stat().st_size)


# ------------------------------------------------------------------ plan footprints
def footprints():
    """Every object tagged plan_sym: tight oriented rectangle of its (and its children's) vertices in world XY,
    with the room and level it is tagged with (after retag: balcony furniture is '1', a car is 'X').
    The kitchen pedal bins carry obj['toggle'] = 'bins' instead of a plan symbol; they stand on the floor, so they
    are written as plan_sym 'bin' (drawn on the plan, solid for the walker).
    Objects that exist only in state 1 (closed curtains, water: show when=1) are no obstacles: never a footprint
    of their own, never part of their parent's. Cabinet / fridge interiors need nothing: only plan_sym roots get
    a footprint, and an interior parented to one lies inside its box."""
    import export_bake as EB
    out = []
    for o in bpy.context.scene.objects:
        sym = o.get('plan_sym') or ('bin' if o.get('toggle') == 'bins' else None)
        if not sym or o.get('no_export') or EB.state1(o):
            continue
        pts = [world_verts(m) for m in [o] + list(o.children_recursive)
               if m.type == 'MESH' and len(m.data.vertices) and not EB.state1(m)]
        if not pts:
            continue
        p = np.concatenate(pts)
        R, lo, hi = EB.fit_box(p[:, :2])
        obb = np.array([[lo[0], lo[1]], [hi[0], lo[1]], [hi[0], hi[1]], [lo[0], hi[1]]]) @ R      # back to world
        zmin, zmax = float(p[:, 2].min()), float(p[:, 2].max())
        out.append(dict(name=o.name, room=o['room'], level=o['level'], plan_sym=sym, obb=np.round(obb, 4).tolist(),
                        zmin=round(zmin, 4), zmax=round(zmax, 4), height=round(zmax - zmin, 4)))
    return sorted(out, key=lambda r: r['name'])


def strip_notes(v):
    if isinstance(v, dict):
        return {k: strip_notes(x) for k, x in v.items() if k != 'notes'}
    return [strip_notes(x) for x in v] if isinstance(v, list) else v


# ------------------------------------------------------------------ hero renders
# Landscape stills for the gallery: (file stem, room, title, camera position, look-at point, horizontal fov in
# degrees), world metres. Framed by hand on the furnished phase-1 ground floor (the room modules' CAMERAS are
# portrait matches of the phone frames); every one was rendered and looked at. Keep cameras >= 0.25 m clear of
# furniture. A room module that defines its own HEROES replaces its rows here (see heroes()).
HEROES = [
    ('vestibule_inner', 'vestibule', 'Vestibule - inner doors', (0.0, 0.15, 1.55), (0.0, 1.78, 0.95), 90),
    ('hallway_front', 'hallway', 'Hallway - from the inner doors', (0.2, 2.2, 1.55), (-0.1, 8.0, 1.2), 80),
    ('hallway_rear', 'hallway', 'Hallway - looking to the front', (-0.1, 12.0, 1.55), (-0.1, 5.0, 1.3), 75),
    ('stairs_foot', 'stairs', 'Staircase', (-0.2, 3.7, 1.5), (0.6, 6.6, 1.35), 75),
    ('living_door', 'living', 'Living room - from the door', (1.05, 4.3, 1.5), (3.6, 1.6, 1.0), 85),
    ('living_gallery', 'living', 'Living room - bookcase and paintings', (1.3, 1.6, 1.45), (4.0, 4.2, 1.5), 85),
    ('living_tv', 'living', 'Living room - TV wall', (3.3, 3.4, 1.4), (0.8, 2.2, 1.3), 80),
    ('living_bay', 'living', 'Living room - bay window', (2.5, 3.9, 1.5), (2.55, 0.0, 1.3), 80),
    ('kitchen_corner', 'kitchen', 'Kitchen - from the garden door', (4.0, 8.4, 1.55), (1.9, 5.6, 1.1), 85),
    ('kitchen_sink', 'kitchen', 'Kitchen - sink, plate rack and wine rack', (2.9, 7.7, 1.5), (2.55, 5.31, 1.3), 80),
    ('kitchen_nook', 'kitchen', 'Kitchen - bar nook and garden door', (3.55, 7.0, 1.5), (1.9, 9.1, 1.3), 85),
    ('kitchen_hob', 'kitchen', 'Kitchen - hob and extractor', (1.75, 8.3, 1.5), (4.3, 6.4, 1.2), 85),
    ('utility_door', 'utility', 'Utility room', (0.75, 10.6, 1.5), (2.6, 12.0, 1.1), 90),
    ('utility_tall', 'utility', 'Utility room - tall unit', (1.0, 11.3, 1.5), (3.1, 10.9, 1.3), 85),
    ('wc_pan', 'wc', 'Cloakroom', (1.2, 9.75, 1.5), (3.1, 9.75, 1.0), 90),
    ('dining_entry', 'dining', 'Dining room - from the door', (-0.35, 12.7, 1.5), (2.4, 15.6, 1.1), 85),
    ('dining_fire', 'dining', 'Dining room - fireplace', (-0.4, 14.0, 1.5), (3.0, 14.9, 1.2), 80),
    ('dining_north', 'dining', 'Dining room - table and French doors', (1.9, 12.62, 1.55), (0.9, 16.9, 1.2), 80),
    ('dining_west', 'dining', 'Dining room - mirror and crest plaques', (2.6, 15.9, 1.5), (-0.65, 14.0, 1.5), 85),
]


def heroes(h, rooms):
    """[(stem, room, title, pos, look, fov)] in rooms[] order. Per room the first of: HEROES of its room module
    (blender/rooms/<module>.py: [dict(name, pos, look, title=..., fov_deg=80, room=...)], landscape), its rows in
    the table above, the module's CAMERAS (reference matches; fov capped at 90). A camera of a module that
    furnishes several rooms belongs to c['room'], else to the room it stands in."""
    from lib import ctx as C
    legacy, mods, siblings, out = {}, {}, {}, []
    for row in HEROES:
        legacy.setdefault(row[1], []).append(row)
    for r in rooms:
        siblings.setdefault(h.module_of(r['id']), []).append(r)

    def cams(r, attr):
        name = h.module_of(r['id'])
        if name not in mods:
            try:
                mods[name] = importlib.import_module('rooms.' + name)
            except ModuleNotFoundError as e:
                mods[name] = None
                if e.name != 'rooms.' + name:
                    log(f'WARNING: rooms/{name}.py does not import ({e}): no stills from it')
        sib = siblings[name]
        for c in getattr(mods[name], attr, None) or []:
            x, y, z = c['pos']
            room = c.get('room') or next((s['id'] for s in sib if C.poly_contains(x, y, s['polygon'])
                                          and s['floorZ'] <= z <= s['floorZ'] + 3), sib[0]['id'])
            if room == r['id']:
                yield (f'{room}_{c["name"]}', room, c.get('title') or f'{r["name"]} - {c["name"]}',
                       tuple(c['pos']), tuple(c['look']), min(90, c.get('fov_deg', 80)))

    for r in rooms:
        out += list(cams(r, 'HEROES')) or legacy.get(r['id']) or list(cams(r, 'CAMERAS'))
    return out


def renders(h, table, rooms, out, samples, res):
    """Cycles stills of heroes() for the rooms asked for (AgX and white balance of the scene, denoised, JPEG quality
    88) -> <out>/<stem>.jpg and index.json [{file, room, level, title}]; other rooms keep their old entries."""
    from lib import preview
    out.mkdir(parents=True, exist_ok=True)
    idx = out / 'index.json'
    old = {e['file']: e for e in (json.loads(idx.read_text(encoding='utf-8')) if idx.exists() else [])}
    sc, index = bpy.context.scene, []
    for stem, room, title, pos, look, fov in table:
        entry = dict(file=f'{stem}.jpg', room=room, level=h.level(room), title=title)
        if room in rooms:
            cam = preview.camera('hero.' + stem, pos, look, fov)
            sc.camera, sc.cycles.samples = cam, samples
            sc.render.resolution_x, sc.render.resolution_y = res
            sc.render.image_settings.file_format, sc.render.image_settings.quality = 'JPEG', 88
            sc.render.filepath = str(out / entry['file'])
            bpy.ops.render.render(write_still=True)
            bpy.data.objects.remove(cam)
            log(f'render {entry["file"]}')
        elif entry['file'] not in old:
            continue
        index.append(entry)
    idx.write_text(json.dumps(index, indent=1), encoding='utf-8')


# ------------------------------------------------------------------ main
def main():
    args = parse()
    import export_bake as EB
    from lib import ctx as C, lighting
    h = C.House.load(args.house)
    rooms = room_table(h)                        # manifest rooms[]: house rooms + pseudo-rooms with ground
    levels = level_table(h, rooms)
    level_ids = [l['id'] for l in levels]
    known = set(h.rooms) | set(C.PSEUDO_ROOMS)
    bad = [x for x in args.levels if x not in level_ids] + [x for x in args.rooms if x not in known]
    if bad:
        raise SystemExit(f'unknown level(s) / room(s) {bad}; levels {level_ids}, rooms {sorted(known)}')
    out, tmp = args.out, args.tmp
    for d in (out, tmp):
        d.mkdir(parents=True, exist_ok=True)
    sc = bpy.context.scene
    lighting.setup_cycles(args.samples)          # GPUs + denoiser (preferences are per run), AgX, white balance
    sc.cycles.adaptive_threshold = 0.01
    tagged, fx = EB.prepare_tagged()             # fx: state-1 objects, hidden from every bake, probe and still

    def picked(room):                            # --rooms wins; else the rooms of --levels; else everything
        return room in args.rooms if args.rooms else h.level(room) in args.levels if args.levels else True

    def todo(room):
        return not args.skip_bake and picked(room)

    table = heroes(h, rooms)
    still_rooms = [r for r in {row[1] for row in table} if picked(r)]
    if args.stills_only:
        renders(h, table, still_rooms, out.parent / 'renders', args.samples, args.still_res)
        print('EXPORT OK')
        return

    retag(h)
    check_ix(h, tagged)
    objs = EB.mesh_objects()
    applied, unique = EB.apply_modifiers(objs)
    atlases, demoted, unlinked = EB.classify(objs)
    log(f'{len(objs)} mesh objects; modifiers applied on {applied} ({unique} meshes); lightmapped '
        f'{sum(map(len, atlases.values()))} in {len(atlases)} atlases; {demoted} small/metal/glass static objects '
        f'demoted to dynamic; {unlinked} shared static meshes made single-user; {len(tagged)} interaction-tagged '
        f'({len(fx)} state-1 objects hidden while baking)')
    write = args.levels or level_ids             # level GLBs written by this run
    probed = [r for r in rooms if r['kind'] != 'void']      # eaves are looked into, never stood in

    # previous manifest: what is not redone keeps its entry (only valid while that geometry is unchanged)
    old = json.loads((out / 'manifest.json').read_text(encoding='utf-8')) if (out / 'manifest.json').exists() else {}
    old = old if old.get('schema') == 2 and not old.get('standin') else {}

    def kept(key, valid):
        return {e['room']: e for e in old.get(key, []) if e['room'] in valid and (out / e['image']).exists()}

    lightmaps, lightmaps_off = kept('lightmaps', atlases), kept('lightmapsOff', atlases)
    probes, probes_off = (kept(k, {r['id'] for r in probed}) for k in ('probes', 'probesOff'))
    info = {e['id']: e for e in old.get('levels', []) if e.get('glb') and (out / e['glb']).exists()}
    M = EB.wb_matrix()
    log('white balance matrix ' + np.array2string(M, precision=3, suppress_small=True).replace('\n', ''))

    # 1. lightmap UVs and atlas sizes of everything that is written or baked (the UVs go into the GLB)
    size = {}
    for room, obs in sorted(atlases.items()):
        if h.level(room) not in write and not todo(room):
            continue
        t = time.time()
        fill, cuts = EB.unwrap(obs)
        m2 = sum(EB.area(o) for o in obs)
        aim, cap = atlas_rule(h, room, args.density or EB.DENSITY, args.bake_res)
        res = EB.atlas_size(m2, fill, aim, cap)
        size[room] = (res, res * (fill / m2) ** 0.5)
        log(f'uv   {room:16s} {len(obs):4d} objects {m2:6.1f} m2 -> {res} px, {size[room][1]:.0f} px/m (aim {aim:.0f}, '
            f'cap {cap}), fill {fill:.2f}, {cuts} islands cut ({time.time() - t:.1f}s)')
        if room in lightmaps:
            lightmaps[room]['objects'] = [o.name for o in obs]

    # 2. one GLB per level (plan footprints first: they need the parent-child links that flatten() removes)
    fp = footprints()
    boxes = tagged_boxes(tagged)
    flatten()
    for o in fx:
        o.hide_render = False                    # exported like everything else; the viewer shows them in state 1
    for L in write:
        t = time.time()
        obs = level_objects(L)
        if not obs:
            info.pop(L, None)
            continue
        raw, glb = tmp / f'{L}_raw.glb', out / 'glb' / f'{L}.glb'
        glb.parent.mkdir(exist_ok=True)
        export_glb(raw, obs)
        compress(raw, glb)
        names = {o.name for o in obs}
        static = [o.name for room in atlases for o in atlases[room] if o.name in names]
        ix = {k: v for k, v in boxes.items() if k in names}
        check_glb(raw, static, ix)
        i = info[L] = check_glb(glb, static, ix)
        log(f'glb  {L}.glb {i["bytes"] / MB:.2f} MB (raw {raw.stat().st_size / MB:.2f}), {i["triangles"]} triangles, '
            f'{i["nodes"]} nodes, {i["meshes"]} meshes ({i["instanced_nodes"]} nodes reuse a mesh), {i["images"]} images, '
            f'TEXCOORD_1 + extras verified, {i["interactive"]} tagged nodes intact ({time.time() - t:.1f}s)')
    for o in fx:
        o.hide_render = True                     # ... and out of the bakes and stills again
    if (out / 'home.glb').exists():              # schema 1 leftover
        (out / 'home.glb').unlink()
    levels = [dict(l, glb=f'glb/{l["id"]}.glb' if l['id'] in info else None,
                   **{k: info.get(l['id'], {}).get(k, 0) for k in ('bytes', 'triangles', 'nodes', 'interactive')})
              for l in levels]

    # 3. budgets known before any bake: triangles, GLB sizes and the first-view estimate
    first_rooms = h.rooms_on('G')
    jsons = [n for n in ('manifest.json', 'house.json', 'plan.json', 'footprints.json') if (out / n).exists()]

    def first_view(estimate):
        """Bytes of what the viewer loads before the ground floor shows. estimate: an atlas / probe that will be
        (re)baked counts as the old file when it has the same size, else ATLAS_BYTES x (size / 4096)^2 / PROBE_BYTES."""
        n = info.get('G', {}).get('bytes', 0) + sum((out / j).stat().st_size for j in jsons)
        for room in first_rooms:
            lm, new = lightmaps.get(room), size.get(room, (0,))[0]
            if lm and not (estimate and todo(room) and lm['size'] != new):
                n += lm['bytes']
            elif estimate and room in atlases:
                n += ATLAS_BYTES * (new / 4096) ** 2
            if room in probes:
                n += probes[room]['bytes']
            elif estimate and any(r['id'] == room for r in probed):
                n += PROBE_BYTES
        return n

    rows = [(f'triangles {l["id"]}', l['triangles'], TRIANGLES.get(l['id'], TRIANGLES_ALL), 'tris') for l in levels]
    rows += [('triangles total', sum(l['triangles'] for l in levels), TRIANGLES_ALL, 'tris')]
    rows += [(l['glb'], l['bytes'], GLB_G_MAX if l['id'] == 'G' else GLB_MAX, 'MB') for l in levels if l['glb']]
    rows += [('first view (estimate)', first_view(True), FIRST_VIEW_MAX, 'MB')]
    over = budget(rows)
    if over:
        raise SystemExit(f'BUDGET FAILED before the bake: {over} (trim with ATLAS_CAP in export.py or cut triangles)')

    # 4. lightmaps
    for room, obs in sorted(atlases.items()):
        if not todo(room):
            continue
        t = time.time()
        res, density = size[room]
        img = out / 'lightmaps' / f'{room}.jpg'
        # exterior atlases hold sunlit and shaded faces (10x apart): only the percentile clips there, not 6 x median
        k = EB.encode(EB.denoise(EB.bake(room, obs, res), res, tmp), res, res, img, M,
                      cap=float('inf') if h.is_exterior(room) else None)
        lightmaps[room] = dict(room=room, level=h.level(room), image=f'lightmaps/{room}.jpg', size=res,
                               pxPerM=round(density), intensity=k, bytes=img.stat().st_size, objects=[o.name for o in obs])
        lightmaps_off.pop(room, None)            # stale now; step 6 bakes it again unless --skip-off
        log(f'bake {room:16s} {res} px, {args.samples} spp, intensity {k} ({time.time() - t:.1f}s)')

    # 5. probes
    for r in probed:
        rid = r['id']
        if not todo(rid):
            continue
        t = time.time()
        pos = EB.probe_point([tuple(p) for p in r['polygon']], r['floorZ'] + EB.EYE)
        probes_off.pop(rid, None)                # stale now, like the lightmap
        if pos is None:
            probes.pop(rid, None)
            log(f'probe {rid}: no free spot, skipped')
            continue
        img = out / 'probes' / f'{rid}.jpg'
        k = EB.encode(EB.render_probe(pos, args.probe_res, args.samples, tmp), args.probe_res, args.probe_res // 2, img, M,
                      quality=90)
        probes[rid] = dict(room=rid, level=r['level'], image=f'probes/{rid}.jpg', pos=list(pos), intensity=k,
                           bytes=img.stat().st_size)
        log(f'probe {rid:16s} at {pos}, intensity {k} ({time.time() - t:.1f}s)')

    # 6. lights-off set: every lamp and emissive off, same UVs at half the size, same probe positions. Indoors a
    # cool ambient term keeps dark rooms readable; outdoors the sun and the sky are still there, so none is added.
    if not args.skip_bake and not args.skip_off:
        amb = EB.AMBIENT_OFF * np.linalg.solve(M, EB.AMBIENT_TINT)       # scene linear: encode() applies M again
        with EB.lights_off() as (n_lights, n_glow):
            log(f'lights off: {n_lights} lights hidden, {n_glow} emission strengths zeroed, ambient {amb.round(4).tolist()}')
            for room, obs in sorted(atlases.items()):
                if not todo(room) or room in FAR_ROOMS:
                    continue
                t = time.time()
                res, inside = lightmaps[room]['size'] // 2, not h.is_exterior(room)
                img = out / 'lightmaps_off' / f'{room}.jpg'
                px = EB.bake_off(room, obs, res, amb) if inside else EB.bake(room, obs, res)
                k = EB.encode(EB.denoise(px, res, tmp), res, res, img, M, cap=EB.PEAK_OFF if inside else float('inf'))
                lightmaps_off[room] = dict(room=room, level=h.level(room), image=f'lightmaps_off/{room}.jpg', size=res,
                                           pxPerM=round(lightmaps[room]['pxPerM'] / 2), intensity=k, bytes=img.stat().st_size)
                log(f'off  {room:16s} {res} px, intensity {k} ({time.time() - t:.1f}s)')
            for r in probed:
                rid, inside = r['id'], not h.is_exterior(r['id'])
                if not todo(rid) or rid not in probes:
                    continue
                t = time.time()
                img = out / 'probes_off' / f'{rid}.jpg'
                px = EB.render_probe(probes[rid]['pos'], args.probe_res, args.samples, tmp)
                if inside:
                    px[:, :3] += amb             # uniform: lights a probe-lit object like bake_off lights an open wall
                k = EB.encode(px, args.probe_res, args.probe_res // 2, img, M, quality=90, cap=EB.PEAK_OFF if inside else None)
                probes_off[rid] = dict(probes[rid], image=f'probes_off/{rid}.jpg', intensity=k, bytes=img.stat().st_size)
                log(f'off  probe {rid:16s} intensity {k} ({time.time() - t:.1f}s)')

    # 7. sky: kept from the old manifest in partial runs
    sky = old.get('sky')
    if not sky or not (out / sky['image']).exists() or not (args.skip_bake or args.rooms or args.levels):
        t = time.time()
        sky = dict(image='sky.jpg', color=EB.render_sky(out / 'sky.jpg'), sunDir=sun_dir())
        log(f'sky  {sky} ({time.time() - t:.1f}s)')

    # 8. manifest, house.json, footprints
    vs = sc.view_settings
    order = [l for l in LOAD_ORDER if l in info] + [l for l in level_ids if l in info and l not in LOAD_ORDER]
    first = ([levels[level_ids.index('G')]['glb']] if 'G' in info else []) + \
        [e[r]['image'] for e in (lightmaps, probes) for r in first_rooms if r in e]
    viewpoints = {}                              # room-jump views: the first hero still of each room
    for _, room, _, pos, look, _ in table:
        viewpoints.setdefault(room, dict(pos=list(pos[:2]), look=list(look[:2])))
    manifest = dict(
        schema=2,
        levels=levels,                           # glb null: nothing is built on that level (yet)
        loadOrder=order,                         # only levels that have a GLB
        rooms=rooms,
        lightmaps=[lightmaps[k] for k in sorted(lightmaps)],
        # the same atlases / probes with every lamp off; a room may be missing (--skip-off, facade / roof / neighbours)
        lightmapsOff=[dict(lightmaps_off[k], objects=lightmaps[k]['objects']) for k in sorted(lightmaps_off) if k in lightmaps],
        probes=[probes[r['id']] for r in probed if r['id'] in probes],
        probesOff=[probes_off[r['id']] for r in probed if r['id'] in probes_off and r['id'] in probes],
        viewpoints=viewpoints,                   # the viewer snaps pos to walkable floor on the room's level
        spawn=dict(pos=list(h.spec.get('spawn', [0, 3]))[:2], yaw=0, level='G'),
        toneMapping='agx' if vs.view_transform == 'AgX' else 'none', exposure=round(2 ** vs.exposure, 4),
        whiteBalance=np.round(M, 5).tolist(),    # 3x3, rows: the viewer applies it to emissive colours
        sky=sky,
        firstView=dict(bytes=0, files=first + ['manifest.json', 'house.json', 'plan.json', 'footprints.json']),
        encoding='8-bit sRGB JPEG; linear = srgbDecode(px) * intensity; lightmaps = Cycles diffuse direct+indirect '
                 'without albedo (radiance of a white surface: multiply by PI for three.js lightMap), on TEXCOORD_1, '
                 'flipY false; probes = equirect radiance, image centre +X, pos in plan metres (x, y, z up); '
                 'white balance of the previews already applied; whiteBalance = that matrix (scene linear, rows) for '
                 'emissive colours, which the GLBs carry unbalanced; sky.image = the world alone as DISPLAYED (view '
                 'transform, exposure and white balance in the pixels: use as an sRGB equirect background, same '
                 'orientation as the probes), sky.color its mean above the horizon, sky.sunDir the unit vector to '
                 'the sun (x, y, z up); lightmapsOff / probesOff = the same encoding, UVs, object lists and probe '
                 'positions with every lamp and emissive off: sun + sky, plus indoors a cool ambient-occlusion term '
                 f'(radiance {EB.AMBIENT_OFF} x {EB.AMBIENT_TINT} on an open wall as encoded; lit rooms have about 0.9) '
                 'that keeps dark rooms readable (probes: the same radiance added uniformly, so a probe-lit object '
                 'matches the wall beside it); lightmaps half the size, own intensity per image '
                 f'(indoors at most {EB.PEAK_OFF:g}); bytes = file sizes; firstView = what loads before level G shows')
    # newline='\n': byte counts must not depend on the platform (json.dumps output is ASCII)
    (out / 'house.json').write_text(json.dumps(strip_notes(h.spec), indent=1), encoding='utf-8', newline='\n')
    (out / 'footprints.json').write_text(json.dumps(fp, indent=1), encoding='utf-8', newline='\n')
    jsons = [n for n in ('house.json', 'plan.json', 'footprints.json') if (out / n).exists()]
    for _ in range(2):                           # the count is part of the text it counts: settles on the second pass
        manifest['firstView']['bytes'] = first_view(False) + len(json.dumps(manifest, indent=1))
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=1), encoding='utf-8', newline='\n')
    log(f'manifest: {len(order)} level GLBs {order}, {len(manifest["lightmaps"])} lightmaps, {len(manifest["probes"])} '
        f'probes, off set {len(manifest["lightmapsOff"])} + {len(manifest["probesOff"])}; {len(fp)} footprints')
    used = {e['image'] for k in ('lightmaps', 'lightmapsOff', 'probes', 'probesOff') for e in manifest[k]} | \
        {l['glb'] for l in levels}
    for d in ('glb', 'lightmaps', 'lightmaps_off', 'probes', 'probes_off'):      # images no entry points to any more
        for f in sorted((out / d).glob('*')):
            if f.is_file() and f'{d}/{f.name}' not in used:
                f.unlink()
                log(f'removed stale {d}/{f.name}')

    # 9. hero stills, then the budgets of the finished output
    if args.renders:
        renders(h, table, still_rooms, out.parent / 'renders', max(256, args.samples), args.still_res)
    site = out.parent if (out.parent / 'index.html').exists() else out     # docs/ when exporting into the site
    files = [f for f in site.rglob('*') if f.is_file()]
    big = max(files, key=lambda f: f.stat().st_size)
    over = budget([(f'largest file {big.name}', big.stat().st_size, FILE_MAX, 'MB'),
                   ('first view', manifest['firstView']['bytes'], FIRST_VIEW_MAX, 'MB'),
                   (f'{site.name}/ ({len(files)} files)', sum(f.stat().st_size for f in files), SITE_MAX, 'MB')])
    if over:
        raise SystemExit(f'BUDGET FAILED: {over} (trim with ATLAS_CAP in export.py)')
    log('done')
    print('EXPORT OK')


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except BaseException:
        traceback.print_exc()
        sys.exit(1)

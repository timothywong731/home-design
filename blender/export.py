"""Export a saved build to the web viewer: lightmaps (lights on and off), probes, home.glb, manifest, footprints,
hero renders. Documented in blender/lib/README.md (section "export"); interaction tags in blender/INTERACT.md.

blender -b [--factory-startup] build/home.blend --python blender/export.py -- --out docs/assets
        [--bake-res 2048] [--samples 256] [--density 160] [--probe-res 1024] [--rooms a,b] [--skip-bake] [--skip-off]
        [--renders] [--stills-only] [--still-res 1920x1080] [--tmp build/export]
"""
import argparse
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


def log(msg):
    print(f'[export {time.time() - T0:6.1f}s] {msg}', flush=True)


def parse():
    ap = argparse.ArgumentParser(prog='export.py')
    ap.add_argument('--out', default='docs/assets')
    ap.add_argument('--bake-res', type=int, default=2048, help='largest lightmap atlas side')
    ap.add_argument('--samples', type=int, default=256, help='Cycles samples for lightmaps and probes')
    ap.add_argument('--density', type=float, default=None, help='lightmap texels per metre aimed for (default 160)')
    ap.add_argument('--probe-res', type=int, default=1024, help='probe panorama width')
    ap.add_argument('--rooms', default='', help='bake / render only these rooms (others keep their old images)')
    ap.add_argument('--skip-bake', action='store_true', help='no lightmaps or probes: GLB, manifest, footprints only')
    ap.add_argument('--skip-off', action='store_true', help='no lights-off lightmaps / probes (rebaked rooms lose theirs)')
    ap.add_argument('--tmp', default='build/export', help='scratch directory (raw GLB, EXRs): one per concurrent run')
    ap.add_argument('--renders', action='store_true', help='hero stills (HEROES) into <out>/../renders')
    ap.add_argument('--stills-only', action='store_true', help='only the hero stills: no bake, GLB or manifest')
    ap.add_argument('--still-res', default='1920x1080', help='hero still size (smaller for framing tests)')
    a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    a.out, a.tmp = (ROOT / a.out).resolve(), (ROOT / a.tmp).resolve()
    a.rooms = [s for s in a.rooms.split(',') if s]
    a.still_res = tuple(int(v) for v in a.still_res.split('x'))
    return a


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


def export_glb(path):
    """Everything except lights, cameras and obj['no_export'], +Y up, custom props as extras, both UV sets,
    textures embedded in their source format (JPEG). Modifiers were applied by export_bake.apply_modifiers."""
    import export_bake as EB
    EB.select([o for o in bpy.context.scene.objects if o.type not in {'LIGHT', 'CAMERA'} and not o.get('no_export')])
    bpy.ops.export_scene.gltf(
        filepath=str(path), export_format='GLB', use_selection=True, export_apply=True, export_yup=True,
        export_texcoords=True, export_normals=True, export_tangents=False, export_materials='EXPORT',
        export_image_format='AUTO', export_extras=True, export_cameras=False, export_lights=False,
        export_animations=False, export_skins=False, export_morph=False, export_gpu_instances=False)


def compress(raw, out):
    """glTF-Transform: textures capped at 2048, colour textures to WebP (normal / ORM maps stay JPEG: recompressing
    them only adds artefacts), meshopt geometry. No dedup / join / instance / prune / simplify: those drop the
    unused-looking TEXCOORD_1, merge named nodes or lose the extras."""
    a, b = raw, raw.with_suffix('.tmp.glb')
    for step in ('resize {a} {b} --width 2048 --height 2048',
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
    """Every object tagged plan_sym: tight oriented rectangle of its (and its children's) vertices in world XY.
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
        out.append(dict(name=o.name, room=o.get('room'), plan_sym=sym, obb=np.round(obb, 4).tolist(),
                        zmin=round(zmin, 4), zmax=round(zmax, 4), height=round(zmax - zmin, 4)))
    return sorted(out, key=lambda r: r['name'])


def strip_notes(v):
    if isinstance(v, dict):
        return {k: strip_notes(x) for k, x in v.items() if k != 'notes'}
    return [strip_notes(x) for x in v] if isinstance(v, list) else v


# ------------------------------------------------------------------ hero renders
# Landscape stills for the gallery: (file stem, room, title, camera position, look-at point, horizontal fov in
# degrees), world metres. Framed by hand on the furnished model (the room modules' CAMERAS are portrait matches of
# the phone frames); every one was rendered and looked at. Keep cameras >= 0.25 m clear of furniture.
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


def renders(rooms, out, samples, res):
    """Cycles stills of HEROES (AgX and white balance of the scene, denoised, JPEG quality 88) -> <out>/<stem>.jpg
    and index.json [{file, room, title}] in HEROES order; rooms not asked for keep their old entries."""
    from lib import preview
    out.mkdir(parents=True, exist_ok=True)
    idx = out / 'index.json'
    old = {e['file']: e for e in (json.loads(idx.read_text(encoding='utf-8')) if idx.exists() else [])}
    sc, index = bpy.context.scene, []
    for stem, room, title, pos, look, fov in HEROES:
        entry = dict(file=f'{stem}.jpg', room=room, title=title)
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
    from lib import lighting
    house = json.loads((ROOT / 'spec' / 'house.json').read_text(encoding='utf-8'))
    room_ids = [r['id'] for r in house['rooms']]
    out, tmp = args.out, args.tmp
    for d in (out, tmp):
        d.mkdir(parents=True, exist_ok=True)
    sc = bpy.context.scene
    lighting.setup_cycles(args.samples)          # GPUs + denoiser (preferences are per run), AgX, white balance
    sc.cycles.adaptive_threshold = 0.01
    tagged, fx = EB.prepare_tagged()             # fx: state-1 objects, hidden from every bake, probe and still
    if args.stills_only:
        renders(args.rooms or room_ids, out.parent / 'renders', max(256, args.samples), args.still_res)
        print('EXPORT OK')
        return

    objs = EB.mesh_objects()
    applied, unique = EB.apply_modifiers(objs)
    atlases, demoted, unlinked = EB.classify(objs)
    log(f'{len(objs)} mesh objects; modifiers applied on {applied} ({unique} meshes); lightmapped '
        f'{sum(map(len, atlases.values()))} in {len(atlases)} atlases; {demoted} small/metal/glass static objects '
        f'demoted to dynamic; {unlinked} shared static meshes made single-user; {len(tagged)} interaction-tagged '
        f'({len(fx)} state-1 objects hidden while baking)')
    bad = [r for r in args.rooms if r not in room_ids and r not in atlases]
    if bad:
        raise SystemExit(f'unknown room(s) {bad}; valid: {sorted(set(room_ids) | set(atlases))}')

    def todo(room):
        return not args.skip_bake and (not args.rooms or room in args.rooms)

    # previous manifest: rooms that are not rebaked keep their images (only valid while their geometry is unchanged)
    old = json.loads((out / 'manifest.json').read_text(encoding='utf-8')) if (out / 'manifest.json').exists() else {}
    old = {} if old.get('standin') else old
    lightmaps = {e['room']: e for e in old.get('lightmaps', []) if e.get('room') in atlases}
    probes = {e['room']: e for e in old.get('probes', []) if e.get('room') in room_ids}
    lightmaps_off = {e['room']: e for e in old.get('lightmapsOff', []) if e.get('room') in atlases}
    probes_off = {e['room']: e for e in old.get('probesOff', []) if e.get('room') in room_ids}
    M = EB.wb_matrix()
    log('white balance matrix ' + np.array2string(M, precision=3, suppress_small=True).replace('\n', ''))

    # 1. lightmap UVs for every atlas (they go into the GLB even with --skip-bake), bake where asked
    for room, obs in sorted(atlases.items()):
        entry = lightmaps.get(room)
        t = time.time()
        fill, cuts = EB.unwrap(obs)
        m2 = sum(EB.area(o) for o in obs)
        res = EB.atlas_size(m2, fill, (args.density or EB.DENSITY) * (1 if room in room_ids else EB.OUTSIDE_SCALE), args.bake_res)
        density = res * (fill / m2) ** 0.5
        log(f'uv   {room:10s} {len(obs):4d} objects {m2:6.1f} m2 -> {res} px, {density:.0f} px/m, fill {fill:.2f}, '
            f'{cuts} islands cut ({time.time() - t:.1f}s)')
        if todo(room):
            t = time.time()
            px = EB.denoise(EB.bake(room, obs, res), res, tmp)
            k = EB.encode(px, res, res, out / 'lightmaps' / f'{room}.jpg', M)
            entry = dict(room=room, image=f'lightmaps/{room}.jpg', intensity=k, size=res, pxPerM=round(density))
            lightmaps_off.pop(room, None)        # stale now; step 2b bakes it again unless --skip-off
            log(f'bake {room:10s} {res} px, {args.samples} spp, intensity {k} ({time.time() - t:.1f}s)')
        if entry:
            entry['objects'] = [o.name for o in obs]
            lightmaps[room] = entry

    # 2. probes
    for r in house['rooms']:
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
        px = EB.render_probe(pos, args.probe_res, args.samples, tmp)
        k = EB.encode(px, args.probe_res, args.probe_res // 2, out / 'probes' / f'{rid}.jpg', M, quality=90)
        probes[rid] = dict(room=rid, image=f'probes/{rid}.jpg', pos=list(pos), intensity=k)
        log(f'probe {rid:10s} at {pos}, intensity {k} ({time.time() - t:.1f}s)')

    # 2b. lights-off set: every lamp and emissive off, same UVs at half the size, same probe positions
    if not args.skip_bake and not args.skip_off:
        amb = EB.AMBIENT_OFF * np.linalg.solve(M, EB.AMBIENT_TINT)       # scene linear: encode() applies M again
        with EB.lights_off() as (n_lights, n_glow):
            log(f'lights off: {n_lights} lights hidden, {n_glow} emission strengths zeroed, ambient {amb.round(4).tolist()}')
            for room, obs in sorted(atlases.items()):
                if not todo(room):
                    continue
                t = time.time()
                res = lightmaps[room]['size'] // 2
                px = EB.denoise(EB.bake_off(room, obs, res, amb), res, tmp)
                k = EB.encode(px, res, res, out / 'lightmaps_off' / f'{room}.jpg', M, cap=EB.PEAK_OFF)
                lightmaps_off[room] = dict(room=room, image=f'lightmaps_off/{room}.jpg', intensity=k, size=res,
                                           pxPerM=round(lightmaps[room]['pxPerM'] / 2))
                log(f'off  {room:10s} {res} px, intensity {k} ({time.time() - t:.1f}s)')
            for rid in room_ids:
                if not todo(rid) or rid not in probes:
                    continue
                t = time.time()
                px = EB.render_probe(probes[rid]['pos'], args.probe_res, args.samples, tmp)
                px[:, :3] += amb                 # uniform: lights a probe-lit object like bake_off lights an open wall
                k = EB.encode(px, args.probe_res, args.probe_res // 2, out / 'probes_off' / f'{rid}.jpg', M, quality=90,
                              cap=EB.PEAK_OFF)
                probes_off[rid] = dict(probes[rid], image=f'probes_off/{rid}.jpg', intensity=k)
                log(f'off  probe {rid:10s} intensity {k} ({time.time() - t:.1f}s)')

    # 3. GLB (plan footprints first: they need the parent-child links that flatten() removes)
    fp = footprints()
    boxes = tagged_boxes(tagged)
    flatten()
    for o in fx:
        o.hide_render = False                    # exported like everything else; the viewer shows them in state 1
    t = time.time()
    raw = tmp / 'home_raw.glb'
    export_glb(raw)
    for o in fx:
        o.hide_render = True                     # ... and out of the hero stills again
    log(f'glb  raw {raw.stat().st_size / 1e6:.2f} MB ({time.time() - t:.1f}s)')
    t = time.time()
    compress(raw, out / 'home.glb')
    static = [o.name for obs in atlases.values() for o in obs]
    check_glb(raw, static, boxes)
    info = check_glb(out / 'home.glb', static, boxes)
    log(f'glb  home.glb {info["bytes"] / 1e6:.2f} MB, {info["triangles"]} triangles, {info["nodes"]} nodes, '
        f'{info["meshes"]} meshes ({info["instanced_nodes"]} nodes reuse a mesh), {info["images"]} images, '
        f'TEXCOORD_1 + extras verified, {info["interactive"]} tagged nodes intact ({time.time() - t:.1f}s)')

    # 4. manifest, house.json, 5. footprints
    vs = sc.view_settings
    manifest = dict(
        lightmaps=[lightmaps[k] for k in sorted(lightmaps)],
        probes=[probes[r] for r in room_ids if r in probes],
        # the same atlases / probes with every lamp off (export_bake.AMBIENT_OFF); a room may be missing (--skip-off)
        lightmapsOff=[dict(lightmaps_off[k], objects=lightmaps[k]['objects']) for k in sorted(lightmaps_off) if k in lightmaps],
        probesOff=[probes_off[r] for r in room_ids if r in probes_off and r in probes],
        rooms=[dict(id=r['id'], name=r['name'], polygon=r['polygon'], ceilZ=r['ceilingZ'], floorZ=r['floorZ'])
               for r in house['rooms']],
        spawn=dict(pos=list(house.get('spawn', [0, 3]))[:2], yaw=0),
        toneMapping='agx' if vs.view_transform == 'AgX' else 'none', exposure=round(2 ** vs.exposure, 4),
        whiteBalance=np.round(M, 5).tolist(),      # 3x3, rows: the viewer applies it to emissive colours
        sky=EB.display_hex([c * lighting.SKY_STRENGTH for c in lighting.SKY_COLOR]),     # world colour as displayed
        encoding='8-bit sRGB JPEG; linear = srgbDecode(px) * intensity; lightmaps = Cycles diffuse direct+indirect '
                 'without albedo (radiance of a white surface: multiply by PI for three.js lightMap), on TEXCOORD_1, '
                 'flipY false; probes = equirect radiance, image centre +X, pos in plan metres (x, y, z up); '
                 'white balance of the previews already applied; whiteBalance = that matrix (scene linear, rows) for '
                 'emissive colours, which the GLB carries unbalanced; sky = sRGB of the world behind the windows; '
                 'lightmapsOff / probesOff = the same encoding, UVs, object lists and probe positions with every lamp '
                 'and emissive off: sun + dusk sky through the windows plus a cool ambient-occlusion term '
                 f'(radiance {EB.AMBIENT_OFF} x {EB.AMBIENT_TINT} on an open wall as encoded; lit rooms have about 0.9) '
                 'that keeps dark rooms readable (probes: the same radiance added uniformly, so a probe-lit object '
                 'matches the wall beside it); lightmaps half the size, own intensity per image '
                 f'(at most {EB.PEAK_OFF:g})',
        # room-jump views of the viewer: the first hero still of each room (the viewer snaps pos to walkable floor)
        viewpoints={room: dict(pos=list(pos[:2]), look=list(look[:2])) for _, room, _, pos, look, _ in reversed(HEROES)},
        glb=info)
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=1), encoding='utf-8')
    (out / 'house.json').write_text(json.dumps(strip_notes(house), indent=1), encoding='utf-8')
    (out / 'footprints.json').write_text(json.dumps(fp, indent=1), encoding='utf-8')
    log(f'manifest: {len(manifest["lightmaps"])} lightmaps, {len(manifest["probes"])} probes, off set '
        f'{len(manifest["lightmapsOff"])} + {len(manifest["probesOff"])}; {len(fp)} footprints')

    # 6. hero stills
    if args.renders:
        renders(args.rooms or room_ids, out.parent / 'renders', max(256, args.samples), args.still_res)
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

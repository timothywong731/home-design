"""Visual proof that the exported lightmaps fit an exported level GLB: re-import the GLB into an empty scene, drive
every lightmapped material as emission = base colour x lightmap (sampled on the SECOND UV set) x intensity, with no
lights at all, and render cameras. If UV2, the manifest object lists or the encoding were wrong the walls come out
scrambled, black or mis-exposed. Read the JPEGs next to build/preview/<room>_<cam>.jpg.

blender -b --factory-startup --python blender/export_check.py -- [--assets docs/assets] [--level G] [--tmp build/export]
        [--glb <tmp>/<level>_raw.glb] [--out <tmp>/check] [--cams living:bay,hallway:front,...] [--off]

--level  which level to re-light (manifest entries with that level, <tmp>/<level>_raw.glb).
--cams   room:cam from preview.default_cameras (portrait 540x960). Default: one landscape view per lightmapped room
         of the level, from its probe position towards the far end of the room -> <room>_probe.jpg.
--off    re-light from the lights-off set (manifest lightmapsOff), files get the suffix _off: dim but readable.

--glb defaults to the uncompressed export: Blender's importer cannot read EXT_meshopt_compression, so the compressed
glb/<level>.glb is checked structurally by export.py (check_glb) and visually in the web viewer."""
import argparse
import json
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))


def lightmapped(mat, img, k, uv, cache):
    key = (mat.name, img.name)
    if key not in cache:
        m = cache[key] = mat.copy()
        nt = m.node_tree
        bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
        base = bsdf.inputs['Base Color']
        uvn, lm, mul, em = (nt.nodes.new(t) for t in ('ShaderNodeUVMap', 'ShaderNodeTexImage', 'ShaderNodeMix', 'ShaderNodeEmission'))
        uvn.uv_map, lm.image = uv, img
        mul.data_type, mul.blend_type, mul.inputs['Factor'].default_value = 'RGBA', 'MULTIPLY', 1.0
        nt.links.new(uvn.outputs['UV'], lm.inputs['Vector'])
        if base.is_linked:
            nt.links.new(base.links[0].from_socket, mul.inputs['A'])
        else:
            mul.inputs['A'].default_value = base.default_value
        nt.links.new(lm.outputs['Color'], mul.inputs['B'])
        nt.links.new(mul.outputs['Result'], em.inputs['Color'])
        em.inputs['Strength'].default_value = k               # linear = srgb_decode(pixel) * intensity
        nt.links.new(em.outputs['Emission'], next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL').inputs['Surface'])
    return cache[key]


def main():
    ap = argparse.ArgumentParser(prog='export_check.py')
    ap.add_argument('--assets', default='docs/assets')
    ap.add_argument('--level', default='G')
    ap.add_argument('--tmp', default='build/export', help='the --tmp of the export run: holds <level>_raw.glb')
    ap.add_argument('--glb', default=None)
    ap.add_argument('--out', default=None)
    ap.add_argument('--cams', default='')
    ap.add_argument('--off', action='store_true', help='check the lights-off lightmaps instead')
    a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    from lib import ctx as C, lighting, preview
    assets = (ROOT / a.assets).resolve()
    glb = (ROOT / (a.glb or f'{a.tmp}/{a.level}_raw.glb')).resolve()
    out = (ROOT / (a.out or f'{a.tmp}/check')).resolve()
    manifest = json.loads((assets / 'manifest.json').read_text(encoding='utf-8'))
    entries = [e for e in manifest['lightmapsOff' if a.off else 'lightmaps'] if e.get('level', 'G') == a.level]
    assert entries, f'the manifest has no {"lights-off " if a.off else ""}lightmaps on level {a.level}'

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(glb))
    objs = {o.name: o for o in bpy.data.objects}
    cache, done, missing = {}, 0, []
    for e in entries:
        img = bpy.data.images.load(str(assets / e['image']))
        for name in e['objects']:
            o = objs.get(name)
            if o is None or o.type != 'MESH' or len(o.data.uv_layers) < 2:
                missing.append(name)
                continue
            for slot in o.material_slots:
                slot.material = lightmapped(slot.material, img, e['intensity'], o.data.uv_layers[1].name, cache)
            done += 1
    assert not missing, f'manifest objects missing from {glb.name} or without a second UV set: {missing[:10]}'
    meshes = [o for o in objs.values() if o.type == 'MESH']
    assert all(o.get('kind') and o.get('room') for o in meshes), 'extras (custom props) did not survive'
    stray = [o.name for o in meshes if o.get('level', 'G') != a.level]
    assert not stray, f'objects of another level in {glb.name}: {stray[:10]}'
    ix = {o: json.loads(o['ix']) for o in objs.values() if 'ix' in o.keys()}      # still the JSON of INTERACT.md
    for o, d in ix.items():
        o.hide_render = d['t'] == 'show' and d['when'] == 1                       # state 0, as baked

    sc = bpy.context.scene
    lighting.setup_cycles(16)                                 # emission only: no light paths to converge
    sc.view_settings.use_white_balance = False                # already baked into the lightmaps
    sc.world = bpy.data.worlds.new('sky')
    sc.world.use_nodes = True
    next(n for n in sc.world.node_tree.nodes if n.type == 'BACKGROUND').inputs['Color'].default_value = (0.5, 0.6, 0.8, 1)
    suffix = '_off' if a.off else ''
    if a.cams:
        h = C.House.load(assets / 'house.json')
        for spec in a.cams.split(','):
            room, cam = spec.split(':')
            c = next(c for c in preview.default_cameras(h, room) if c['name'] == cam)
            preview.render(preview.camera(f'{room}.{cam}', c['pos'], c['look'], c['fov_deg']), out / f'{room}_{cam}{suffix}.jpg', (540, 960), 16)
    else:
        polys = {r['id']: r['polygon'] for r in manifest['rooms']}
        probes = {p['room']: p['pos'] for p in manifest['probes']}
        for e in entries:
            room = e['room']
            if room not in probes:
                print(f'[check] {room}: no probe, no view (pass --cams)')
                continue
            x, y, z = probes[room]
            fx, fy = max(polys[room], key=lambda p: (p[0] - x) ** 2 + (p[1] - y) ** 2)
            preview.render(preview.camera(f'{room}.probe', (x, y, z), (fx, fy, z - 0.4), 90), out / f'{room}_probe{suffix}.jpg', (960, 540), 16)
    print(f'CHECK OK: level {a.level}, {done} lightmapped objects re-lit from {len(entries)} atlases, '
          f'{len(ix)} interaction-tagged objects')


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except BaseException:
        import traceback
        traceback.print_exc()
        sys.exit(1)

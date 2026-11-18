"""Visual proof that the exported lightmaps fit the exported GLB: re-import the GLB into an empty scene, drive every
lightmapped material as emission = base colour x lightmap (sampled on the SECOND UV set) x intensity, with no lights
at all, and render the preview cameras. If UV2, the manifest object lists or the encoding were wrong the walls come
out scrambled, black or mis-exposed. Read the JPEGs next to build/preview/<room>_<cam>.jpg.

blender -b --factory-startup --python blender/export_check.py -- [--assets docs/assets] [--glb build/export/home_raw.glb]
        [--out build/export/check] [--cams living:bay,hallway:front,...]

--glb defaults to the uncompressed export: Blender's importer cannot read EXT_meshopt_compression, so the
compressed home.glb is checked structurally by export.py (check_glb) and visually in the web viewer."""
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
    ap.add_argument('--glb', default='build/export/home_raw.glb')
    ap.add_argument('--out', default='build/export/check')
    ap.add_argument('--cams', default='hallway:front,living:bay,living:tvwall,kitchen:entry,dining:entry,wc:pan')
    a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    from lib import lighting, preview
    assets = (ROOT / a.assets).resolve()
    manifest = json.loads((assets / 'manifest.json').read_text(encoding='utf-8'))

    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str((ROOT / a.glb).resolve()))
    objs = {o.name: o for o in bpy.data.objects}
    cache, done, missing = {}, 0, []
    for e in manifest['lightmaps']:
        img = bpy.data.images.load(str(assets / e['image']))
        for name in e['objects']:
            o = objs.get(name)
            if o is None or o.type != 'MESH' or len(o.data.uv_layers) < 2:
                missing.append(name)
                continue
            for slot in o.material_slots:
                slot.material = lightmapped(slot.material, img, e['intensity'], o.data.uv_layers[1].name, cache)
            done += 1
    assert not missing, f'manifest objects missing from the GLB or without a second UV set: {missing[:10]}'
    assert all(o.get('kind') for o in objs.values() if o.type == 'MESH'), 'extras (custom props) did not survive'

    sc = bpy.context.scene
    lighting.setup_cycles(16)                                 # emission only: no light paths to converge
    sc.view_settings.use_white_balance = False                # already baked into the lightmaps
    sc.world = bpy.data.worlds.new('sky')
    sc.world.use_nodes = True
    next(n for n in sc.world.node_tree.nodes if n.type == 'BACKGROUND').inputs['Color'].default_value = (0.5, 0.6, 0.8, 1)
    out = (ROOT / a.out).resolve()
    for spec in a.cams.split(','):
        room, cam = spec.split(':')
        c = next(c for c in preview.DEFAULT_CAMERAS[room] if c['name'] == cam)
        preview.render(preview.camera(f'{room}.{cam}', c['pos'], c['look'], c['fov_deg']), out / f'{room}_{cam}.jpg', (540, 960), 16)
    print(f'CHECK OK: {done} lightmapped objects re-lit from {len(manifest["lightmaps"])} atlases')


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except BaseException:
        import traceback
        traceback.print_exc()
        sys.exit(1)

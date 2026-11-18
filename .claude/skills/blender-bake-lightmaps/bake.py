"""Bake diffuse lighting (direct+indirect, colour excluded) to the 'Lightmap' UV layer. Blender 5.1.1.
bake_lightmap(objs, path, size) -> Image saved as EXR (linear) ready for three.js lightMap."""
import bpy

def setup_cycles(samples=256, denoise=True, gpu=True):
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.samples = samples
    sc.cycles.use_denoising = denoise  # bake denoise: scene.cycles.use_denoising applies to bakes
    if gpu:
        p = bpy.context.preferences.addons['cycles'].preferences
        for t in ('OPTIX', 'CUDA'):
            try: p.compute_device_type = t; p.get_devices(); break
            except Exception: continue
        for d in p.devices: d.use = d.type != 'CPU'
        if any(d.use for d in p.devices): sc.cycles.device = 'GPU'

def bake_lightmap(objs, path, size=2048, uv="Lightmap", margin=4):
    im = bpy.data.images.new("lm_" + objs[0].name, size, size, alpha=False, float_buffer=True)
    im.colorspace_settings.name = 'Non-Color'          # linear data
    nodes_added = []
    for ob in objs:
        ob.data.uv_layers.active = ob.data.uv_layers[uv]
        for slot in ob.material_slots:                   # every material needs a target image node
            nt = slot.material.node_tree
            n = nt.nodes.new('ShaderNodeTexImage'); n.image = im; n.select = True
            nt.nodes.active = n; nodes_added.append((nt, n))   # active + unconnected = bake target
    bpy.ops.object.select_all(action='DESELECT')
    for ob in objs: ob.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.bake(type='DIFFUSE', pass_filter={'DIRECT', 'INDIRECT'}, margin=margin,
                        margin_type='EXTEND', use_clear=True, target='IMAGE_TEXTURES')
    im.filepath_raw = path; im.file_format = 'OPEN_EXR'; im.save()
    for nt, n in nodes_added: nt.nodes.remove(n)         # keep the exported materials clean
    return im

"""PBR material + UV helpers that survive glTF export (tested on Blender 5.1.1).
Rules: image textures only (no procedural nodes), one Principled BSDF, ORM packed texture,
normal map via Normal Map node (tangent space, Non-Color image)."""
import bpy, numpy as np

def load_img(path, srgb=True):
    im = bpy.data.images.load(path, check_existing=True)
    im.colorspace_settings.name = 'sRGB' if srgb else 'Non-Color'
    return im

def pack_orm(ao, rough, metal, out_path, size=None):
    """Pack three greyscale images/floats into one RGB PNG: R=AO, G=roughness, B=metallic (glTF ORM).
    ao/rough/metal: bpy Image, or a float constant."""
    def px(x, n):
        if isinstance(x, (int, float)): return np.full(n, float(x), np.float32)
        a = np.empty(len(x.pixels), np.float32); x.pixels.foreach_get(a); return a[0::4]
    ref = next(i for i in (ao, rough, metal) if not isinstance(i, (int, float)))
    w, h = (ref.size if size is None else size); n = w * h
    rgba = np.ones((n, 4), np.float32)
    rgba[:, 0], rgba[:, 1], rgba[:, 2] = px(ao, n), px(rough, n), px(metal, n)
    im = bpy.data.images.new("orm", w, h, alpha=False, float_buffer=False)
    im.colorspace_settings.name = 'Non-Color'; im.pixels.foreach_set(rgba.ravel()); im.update()
    im.filepath_raw = out_path; im.file_format = 'PNG'; im.save()
    return im

def make_material(name, base, orm=None, normal=None, uv_name=None, rough=0.6, metal=0.0, tint=None):
    """base/orm/normal: bpy Images (or None). orm: R=AO(unused by Principled; exported as occlusion),
    G=roughness, B=metallic. Returns material."""
    m = bpy.data.materials.new(name); m.use_backface_culling = True; m.use_nodes = True   # use_nodes is deprecated-but-harmless in 5.x
    nt = m.node_tree; N = nt.nodes; L = nt.links
    bsdf = next(n for n in N if n.type == 'BSDF_PRINCIPLED')
    def tex(im, x, y):
        t = N.new('ShaderNodeTexImage'); t.image = im; t.location = (x, y)
        if uv_name:
            u = N.new('ShaderNodeUVMap'); u.uv_map = uv_name; u.location = (x - 220, y)
            L.new(u.outputs[0], t.inputs['Vector'])
        return t
    bsdf.inputs['Roughness'].default_value = rough; bsdf.inputs['Metallic'].default_value = metal
    if base:
        t = tex(base, -500, 300)
        if tint:  # multiply node exports as baseColorFactor only when value is a constant: keep tint in the texture instead
            pass
        L.new(t.outputs['Color'], bsdf.inputs['Base Color'])
    if orm:
        t = tex(orm, -500, 0); s = N.new('ShaderNodeSeparateColor'); s.location = (-250, 0)
        L.new(t.outputs['Color'], s.inputs['Color'])
        L.new(s.outputs['Green'], bsdf.inputs['Roughness']); L.new(s.outputs['Blue'], bsdf.inputs['Metallic'])
        # occlusion: exporter reads a node group named 'glTF Material Output' with an 'Occlusion' input
        g = bpy.data.node_groups.get('glTF Material Output')
        if g is None:
            g = bpy.data.node_groups.new('glTF Material Output', 'ShaderNodeTree')
            g.interface.new_socket('Occlusion', in_out='INPUT', socket_type='NodeSocketFloat')
        gn = N.new('ShaderNodeGroup'); gn.node_tree = g; gn.location = (0, -250)
        L.new(s.outputs['Red'], gn.inputs['Occlusion'])
    if normal:
        t = tex(normal, -500, -300); nm = N.new('ShaderNodeNormalMap'); nm.location = (-250, -300)
        L.new(t.outputs['Color'], nm.inputs['Color']); L.new(nm.outputs['Normal'], bsdf.inputs['Normal'])
    return m

def box_uv(ob, size=1.0, name="UVMap"):
    """World-scale box projection: texel density = constant (1 UV unit = `size` metres). Good for
    walls/floors/trim; use smart_project for organic furniture."""
    me = ob.data
    uv = me.uv_layers.get(name) or me.uv_layers.new(name=name)
    me.uv_layers.active = uv
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.cube_project(cube_size=size, correct_aspect=True, scale_to_bounds=False)
    bpy.ops.object.mode_set(mode='OBJECT')

def lightmap_uv(ob, name="Lightmap", margin=0.003, angle=66):
    """Second UV layer: non-overlapping, 0-1 packed. smart_project + pack_islands. (lightmap_pack is
    simpler but makes one island per face; smart_project gives better texel use.)"""
    me = ob.data
    uv = me.uv_layers.get(name) or me.uv_layers.new(name=name)
    me.uv_layers.active = uv
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=np.radians(angle), island_margin=margin)
    bpy.ops.uv.pack_islands(margin=margin)
    bpy.ops.object.mode_set(mode='OBJECT')
    return uv

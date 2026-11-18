"""Material library test: swatch wall render + GLB export check.

  blender -b --factory-startup --python blender/textures/test_swatches.py -- [--out build/materials] [--samples 48] [--only key,key]

Builds a 1 m plane + sphere per material (every mat() key, sample paint()/solid()/image_mat()),
box-mapped with uv_box so textures show at true scale, with the key printed under each swatch.
Renders sheets of 6 swatches (key light from the upper LEFT, so raised tiles must be bright on
their top/left edges) to <out>/swatch_NN.jpg, exports <out>/swatches.glb and checks from its JSON
that every material kept the textures the library gave it. Prints SWATCH OK / exits 1 on failure."""
import argparse, json, math, os, struct, sys, traceback
import bpy

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'blender'))

COLS, CW, CH = 3, 1.2, 1.3          # sheet = 3 x 2 swatches, cell size in metres


def args():
    p = argparse.ArgumentParser()
    p.add_argument('--out', default=os.path.join(ROOT, 'build', 'materials'))
    p.add_argument('--samples', type=int, default=48)
    p.add_argument('--only', default='')
    p.add_argument('--px', type=int, default=1500)
    p.add_argument('--close', default='', help='keys to also render as 0.4 m close-ups under grazing light')
    return p.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])


def mesh_obj(name, verts, faces, col):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    return ob


def sphere(name, r, col):
    import bmesh
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=r)
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    col.objects.link(ob)
    return ob


def label(text, x, z, col, mat):
    cu = bpy.data.curves.new('lbl', 'FONT')
    cu.body, cu.size, cu.align_x = text, 0.085, 'CENTER'
    ob = bpy.data.objects.new('lbl.' + text, cu)
    ob.location, ob.rotation_euler = (x, -0.01, z), (math.pi / 2, 0, 0)
    ob.data.materials.append(mat)
    col.objects.link(ob)


def build(M, items):
    sc = bpy.context.scene
    sw = bpy.data.collections.new('swatches')
    aux = bpy.data.collections.new('aux')
    sc.collection.children.link(sw)
    sc.collection.children.link(aux)
    ink = M.solid('label_ink', '#101010', 0.9)
    dark, light = M.solid('bg_dark', '#30343A', 0.9), M.solid('bg_light', '#C8C8C8', 0.9)
    rows = math.ceil(len(items) / COLS)
    for i, (name, m) in enumerate(items):
        x0, z0 = (i % COLS) * CW + 0.1, -(i // COLS) * CH - 0.08
        p = mesh_obj('sw.' + name, [(x0, 0, z0 - 1), (x0 + 1, 0, z0 - 1), (x0 + 1, 0, z0), (x0, 0, z0)], [(0, 1, 2, 3)], sw)
        s = sphere('sp.' + name, 0.2, sw)
        s.location = (x0 + 0.76, -0.24, z0 - 0.76)
        for o in (p, s):
            o.data.materials.append(m)
            M.uv_box(o)
        for k in range(16):                             # 4x4 checker 0.2 m behind the plane (shows through glass)
            cx, cz = x0 + (k % 4) * 0.25, z0 - (k // 4) * 0.25
            b = mesh_obj('bg', [(cx, 0.2, cz), (cx + 0.25, 0.2, cz), (cx + 0.25, 0.2, cz - 0.25), (cx, 0.2, cz - 0.25)], [(3, 2, 1, 0)], aux)
            b.data.materials.append(dark if (k % 4 + k // 4) % 2 else light)
        label(name, x0 + 0.5, z0 - 1.13, aux, ink)
    return sw, rows


def lights(rows):
    w = bpy.data.worlds.new('w')
    bpy.context.scene.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs['Color'].default_value, bg.inputs['Strength'].default_value = (1, 1, 1, 1), 0.35
    s = bpy.data.lights.new('key', 'SUN')                 # raking key light from the upper left
    s.energy, s.angle = 2.6, math.radians(3)
    o = bpy.data.objects.new('key', s)
    o.rotation_euler = (math.radians(62), 0, math.radians(-38))
    bpy.context.scene.collection.objects.link(o)


def render(rows, out, samples, px):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.samples, sc.cycles.use_denoising = samples, True
    pr = bpy.context.preferences.addons['cycles'].preferences
    for t in ('OPTIX', 'CUDA'):
        try:
            pr.compute_device_type = t
            pr.get_devices()
            break
        except Exception:
            continue
    for d in pr.devices:
        d.use = d.type != 'CPU'
    if any(d.use for d in pr.devices):
        sc.cycles.device = 'GPU'
    sc.view_settings.view_transform = 'Standard'          # so colours can be compared with the spec hexes
    sc.render.resolution_x, sc.render.resolution_y = px, int(px * 2 * CH / (COLS * CW))
    sc.render.image_settings.media_type = 'IMAGE'
    sc.render.image_settings.file_format = 'JPEG'
    sc.render.image_settings.quality = 90
    cam = bpy.data.cameras.new('cam')
    cam.type, cam.ortho_scale = 'ORTHO', COLS * CW
    co = bpy.data.objects.new('cam', cam)
    co.rotation_euler = (math.pi / 2, 0, 0)
    sc.collection.objects.link(co)
    sc.camera = co
    for n in range(math.ceil(rows / 2)):
        co.location = (COLS * CW / 2, -6, -(2 * n + 1) * CH)
        sc.render.filepath = os.path.join(out, f'swatch_{n:02d}.jpg')
        bpy.ops.render.render(write_still=True)
        print('RENDERED', sc.render.filepath)
    return co


def closeups(names, co, out):
    """0.4 m wide view of the swatch's top-left corner, light grazing from the upper left: raised
    parts must be bright on their top/left flanks and dark on their bottom/right flanks."""
    sc = bpy.context.scene
    bpy.data.objects['key'].rotation_euler = (math.radians(80), 0, math.radians(-45))
    bpy.data.lights['key'].energy = 3.5
    co.data.ortho_scale = 0.4
    sc.render.resolution_x = sc.render.resolution_y = 900
    for n in names:
        p = bpy.data.objects.get('sw.' + n)
        if p is None:
            continue
        x0, z0 = p.data.vertices[3].co.x, p.data.vertices[3].co.z
        co.location = (x0 + 0.2, -6, z0 - 0.2)
        sc.render.filepath = os.path.join(out, f"close_{n.replace(' ', '_')}.jpg")
        bpy.ops.render.render(write_still=True)
        print('RENDERED', sc.render.filepath)


def export_and_check(M, sw, items, out):
    for o in bpy.context.scene.objects:
        o.select_set(o.name in sw.objects)
    path = os.path.join(out, 'swatches.glb')
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', use_selection=True, export_apply=True,
                              export_yup=True, export_cameras=False, export_lights=False,
                              export_image_format='AUTO', export_texcoords=True, export_normals=True)
    raw = open(path, 'rb').read()
    j = json.loads(raw[20:20 + struct.unpack('<I', raw[12:16])[0]])
    gm = {m['name']: m for m in j['materials']}
    imgs = [i.get('name', '?') + ':' + i.get('mimeType', '?') for i in j.get('images', [])]
    bad = []
    for name, m in items:
        g = gm.get(m.name)
        if g is None:
            bad.append(f'{name}: not in glb')
            continue
        nodes = {n.type: n for n in m.node_tree.nodes}
        nimg = sum(1 for n in m.node_tree.nodes if n.type == 'TEX_IMAGE')
        pbr = g.get('pbrMetallicRoughness', {})
        has = dict(base='baseColorTexture' in pbr, orm='metallicRoughnessTexture' in pbr, nrm='normalTexture' in g)
        bsdf = nodes['BSDF_PRINCIPLED']
        want = dict(base=bsdf.inputs['Base Color'].is_linked, orm=bsdf.inputs['Roughness'].is_linked,
                    nrm=bsdf.inputs['Normal'].is_linked)
        if has != want or sum(has.values()) != nimg:
            bad.append(f'{name}: textures in glb {has} but material has {want} ({nimg} image nodes)')
        alpha = bsdf.inputs['Alpha'].default_value
        if (alpha < 1) != (g.get('alphaMode') == 'BLEND'):
            bad.append(f"{name}: alpha {alpha:.2f} but alphaMode {g.get('alphaMode')}")
        if alpha >= 1 and g.get('doubleSided'):
            bad.append(f'{name}: opaque but doubleSided')
        print(f"GLB {name:26s} tex {''.join(k[0] if v else '-' for k, v in has.items())} "
              f"factor {[round(x, 3) for x in pbr.get('baseColorFactor', [1, 1, 1, 1])]} "
              f"r {pbr.get('roughnessFactor', 1)} m {pbr.get('metallicFactor', 1)} {g.get('alphaMode', 'OPAQUE')} "
              f"ext {list(g.get('extensions', {}))}")
    print(f'GLB {len(j["materials"])} materials, {len(imgs)} images, {len(raw) / 1e6:.1f} MB; extensions {j.get("extensionsUsed")}')
    missing = [t for t in j.get('textures', []) if 'source' not in t]
    if missing:
        bad.append(f'{len(missing)} textures without an image')
    return bad


def check_uv(M):
    """uv_box self-check: true scale, direction, rotate, origin, per-slot size, moved object."""
    col = bpy.context.scene.collection
    fl = mesh_obj('t.floor', [(0, 0, 0), (2.2, 0, 0), (2.2, 4.4, 0), (0, 4.4, 0)], [(0, 1, 2, 3)], col)
    fl.data.materials.append(M.mat('oak_floor'))                     # size_m 2.2 x 4.4, boards along V

    def uvs(o):
        return [tuple(round(c, 4) for c in d.uv) for d in o.data.uv_layers[0].data]
    M.uv_box(fl)
    assert uvs(fl) == [(0, 0), (1, 0), (1, 1), (0, 1)], uvs(fl)       # U = +X, V = +Y, one repeat
    M.uv_box(fl, rotate=True)
    assert uvs(fl) == [(0, 0), (0, -0.5), (2, -0.5), (2, 0)], uvs(fl)  # boards now along X
    M.uv_box(fl, origin=(2.2, 4.4, 0))
    assert uvs(fl) == [(-1, -1), (0, -1), (0, 0), (-1, 0)], uvs(fl)
    fl.location = (2.2, 0, 0)                                         # no depsgraph update needed
    M.uv_box(fl)
    assert uvs(fl)[0] == (1, 0), uvs(fl)
    wl = mesh_obj('t.wall', [(0, 0, 0), (0.909, 0, 0), (0.909, 0, 0.618), (0, 0, 0.618),
                             (0, 0, 1), (0.33, 0, 1), (0.33, 0, 1.33), (0, 0, 1.33)], [(0, 1, 2, 3), (4, 5, 6, 7)], col)
    wl.data.materials.append(M.mat('metro_grey'))
    wl.data.materials.append(M.mat('victorian_tile'))
    wl.data.polygons[1].material_index = 1
    M.uv_box(wl)                                                      # wall facing -Y: U = +X, V = +Z
    u = uvs(wl)
    assert u[:4] == [(0, 0), (1, 0), (1, 1), (0, 1)] and u[5][0] == 1 and round(u[6][1] - u[5][1], 3) == 1, u
    for o in (fl, wl):
        bpy.data.objects.remove(o)
    print('UV OK')


def main():
    a = args()
    a.out = os.path.abspath(a.out)                       # Blender resolves a relative render path against the drive root
    os.makedirs(a.out, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    from lib import materials as M
    items = [(k, M.mat(k)) for k in M.keys()]
    items += [('paint ' + n, M.paint(M.PAINT[n])) for n in ('hall_white', 'hall_dado_grey', 'living_terracotta', 'living_pink', 'wc_grey', 'dining_cream')]
    items += [('paint gloss', M.paint('#F4F2EC', 0.15)), ('solid test', M.solid('solid_test', '#6F7C8C', 0.5)),
              ('image_mat', M.image_mat('image_test', 'sunflower_tile_col.jpg', (0.5, 0.5), 0.3))]
    for alias in M.ALIAS:
        assert M.mat(alias) is M.mat(M.ALIAS[alias])
    assert M.paint('#f2f0ea') is M.paint('#F2F0EA') and M.mat('brass') is M.mat('brass')
    if a.only:
        items = [it for it in items if it[0] in a.only.split(',')]
    print('KEYS', len(M.keys()), ' '.join(M.keys()))
    check_uv(M)
    sw, rows = build(M, items)
    bad = export_and_check(M, sw, items, a.out)
    lights(rows)
    cam = render(rows, a.out, a.samples, a.px)
    closeups([n for n in a.close.split(',') if n], cam, a.out)
    if bad:
        print('SWATCH FAILED:\n  ' + '\n  '.join(bad))
        sys.exit(1)
    print('SWATCH OK', len(items), 'materials')


try:
    main()
except SystemExit:
    raise
except Exception:
    traceback.print_exc()
    sys.exit(1)

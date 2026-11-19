"""Material library (owner: materials). See the "materials" section of blender/lib/README.md.

    from lib import materials as M
    floor.data.materials.append(M.mat('oak_floor')); M.uv_box(floor)
    wall.data.materials.append(M.paint(M.PAINT['living_pink']))

Every material is one Principled BSDF fed by constants and image textures only (base colour, packed
ORM, tangent normal), so it renders in Cycles and exports to glTF unchanged. Textured materials and
their real-world repeat size come from blender/textures/manifest.json (written by
blender/textures/gen/make_all.py); constant-colour ones are listed in CONST below.
Each material carries custom props: mat['size_m'] = (w, h) metres per texture repeat, mat['key']."""
import json, os
import bpy
import numpy as np

TEX_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'textures'))
with open(os.path.join(TEX_DIR, 'manifest.json'), encoding='utf8') as _f:
    MANIFEST = json.load(_f)

PAINT_STIPPLE = True     # matt paint() gets the shared faint roller-stipple normal map

# Constant-colour materials. hex = neutral-light sRGB from spec/rooms/*.md.
# Optional: metal, alpha (<1 = blended glass), tex = auxiliary map set in the manifest, nrm = strength.
CONST = {
    # metals
    # polished brass (door furniture, chandeliers, picture rail). The specs' #C9A44C is the colour it looks; as a metallic
    # base colour that rendered copper-orange, so the reflectance is paler (frames show pale polished brass).
    # Integration: all gold / brass bases moved from orange toward olive-yellow - hall, living, stairs, dining and WC
    # each measured the old ones (#E3CC8E, #B0903C, #C8A84B, #B9A56A) as orange / rose against the frames.
    'brass':            dict(hex='#D3C882', rough=0.18, metal=1),
    'brass_antique':    dict(hex='#B09A62', rough=0.35, metal=1),   # satin knurled kitchen handles
    'bronze_antique':   dict(hex='#6F5C3A', rough=0.40, metal=1),   # utility handles
    'bronze_dark':      dict(hex='#5C4B3A', rough=0.50, metal=1),   # relief plaques, fireplace insert
    'gilt':             dict(hex='#A2924A', rough=0.35, metal=1),   # antique gold frames
    'gilt_bright':      dict(hex='#B8A655', rough=0.25, metal=1),   # bright gold frames (WC mirror)
    'gold_champagne':   dict(hex='#B8AE7C', rough=0.40, metal=1),   # brushed champagne frames
    'chrome':           dict(hex='#D0D2D2', rough=0.05, metal=1),
    'steel_brushed':    dict(hex='#B9B9B6', rough=0.30, metal=1, tex='_brushed', nrm=1.0),   # hood, appliances
    'nickel_brushed':   dict(hex='#A9AAA8', rough=0.30, metal=1, tex='_brushed', nrm=1.0),   # sink, filter tap
    'silver_satin':     dict(hex='#9C9C98', rough=0.35, metal=1),
    # blacks
    'black_matt':       dict(hex='#1A1A1A', rough=0.85),
    'black_gloss':      dict(hex='#141516', rough=0.05),            # oven / appliance glass fronts
    'screen_black':     dict(hex='#0B0B0C', rough=0.08),            # TV screen
    'cast_iron':        dict(hex='#1E1E1E', rough=0.65),            # pan supports, grate, roll holder
    'anthracite':       dict(hex='#26272A', rough=0.50),            # towel radiator, fridge doors
    'slate_black':      dict(hex='#1D1B1A', rough=0.15),            # mantel clock
    # whites
    'white_gloss':      dict(hex='#F4F2EC', rough=0.15),            # gloss joinery paint
    'white_satin':      dict(hex='#F5F4F0', rough=0.35),            # shutters
    'plaster_white':    dict(hex='#F4F3EE', rough=0.90),            # cornices, roses, ceilings
    'upvc_white':       dict(hex='#F4F4F0', rough=0.25),
    'plastic_white':    dict(hex='#F3F3F1', rough=0.40),            # switches, sockets, A/C console
    'ceramic_white':    dict(hex='#F4F3EF', rough=0.04),            # Belfast sink, WC, basin
    # glass. Clear glass is a 10 % mirror (metallic, alpha 0.10): light passes in Cycles without
    # caustics and three.js gets plain alpha blending with reflections - no transmission pass.
    'glass_clear':      dict(hex='#F2F7F5', rough=0.0, metal=1, alpha=0.10),
    'glass_frosted':    dict(hex='#E4EAE8', rough=0.55, alpha=0.78),                        # etched transom, kitchen door lights
    'glass_obscure':    dict(hex='#DDE5E3', rough=0.12, alpha=0.60, tex='_stipple', nrm=1.0),  # stippled street-door / WC glazing
    'glass_green':      dict(hex='#DFE6E0', rough=0.06, alpha=0.90),                        # kitchen memo board
    'glass_dark':       dict(hex='#101214', rough=0.03, alpha=0.85),                        # washer / dryer door bowls
    'whisky':           dict(hex='#8A4A12', rough=0.05, alpha=0.85),                        # decanter contents
    'mirror':           dict(hex='#F2F2F2', rough=0.0, metal=1),
    # misc
    'pot_jade':         dict(hex='#5F8F7A', rough=0.12),
    'pot_olive':        dict(hex='#6F7A45', rough=0.20),
    'alabaster':        dict(hex='#C99A7A', rough=0.30),
    'cork':             dict(hex='#B58F62', rough=0.90),
}

# names used in spec/house.json -> library key
ALIAS = {'oak_plank': 'oak_floor', 'victorian_geometric_tile': 'victorian_tile',
         'wood_effect_porcelain_plank': 'wood_tile_floor', 'carpet_mink_grey': 'carpet_mink'}

# wall / ceiling paint colours by room (neutral-light estimates): paint(PAINT['living_pink'])
PAINT = {
    'hall_white': '#F2F0EA', 'hall_dado_grey': '#C8C5BB', 'joinery_white': '#F4F2EC', 'ceiling_white': '#F4F3EE',
    'living_terracotta': '#A27365', 'living_pink': '#EADFD9', 'living_ceiling': '#F6F4EF',
    'kitchen_white': '#F1EFE9', 'kitchen_ceiling': '#F5F4F0',
    'utility_white': '#F1F0EB', 'utility_ceiling': '#F6F5F2',
    'wc_grey': '#A5A5A8', 'wc_ceiling': '#F6F5F2',
    'dining_cream': '#DFD8CB', 'dining_ceiling': '#F3F1EB',
}

_cache = {}


def hex_lin(h):
    """'#RRGGBB' sRGB -> (r, g, b, 1) linear, as Blender colour sockets expect."""
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c) + (1.0,)


def _image(fn, colour):
    path = fn if os.path.isabs(fn) else os.path.join(TEX_DIR, fn)
    if not os.path.exists(path):
        raise FileNotFoundError(f'texture missing: {path}')
    im = bpy.data.images.load(path, check_existing=True)
    im.name = os.path.splitext(os.path.basename(path))[0]         # glTF image names
    im.colorspace_settings.name = 'sRGB' if colour else 'Non-Color'
    return im


def _build(name, hex=None, base=None, nrm=None, orm=None, rough=0.5, metal=0.0, nrm_strength=1.0,
           size_m=(1.0, 1.0), alpha=1.0, sheen=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    I = bsdf.inputs

    def tex(fn, colour, y):
        t = nt.nodes.new('ShaderNodeTexImage')
        t.image = _image(fn, colour)
        t.location = (-620, y)
        return t
    I['Roughness'].default_value = rough
    I['Metallic'].default_value = metal
    if hex:
        I['Base Color'].default_value = hex_lin(hex)
        m.diffuse_color = hex_lin(hex)                              # viewport only
    if base:
        nt.links.new(tex(base, True, 320).outputs['Color'], I['Base Color'])
    if orm:                                                         # glTF packing: G roughness, B metallic
        sep = nt.nodes.new('ShaderNodeSeparateColor')
        sep.location = (-300, 20)
        nt.links.new(tex(orm, False, 20).outputs['Color'], sep.inputs['Color'])
        nt.links.new(sep.outputs['Green'], I['Roughness'])
        nt.links.new(sep.outputs['Blue'], I['Metallic'])
    if nrm:
        nm = nt.nodes.new('ShaderNodeNormalMap')
        nm.location = (-300, -280)
        nm.inputs['Strength'].default_value = nrm_strength
        nt.links.new(tex(nrm, False, -280).outputs['Color'], nm.inputs['Color'])
        nt.links.new(nm.outputs['Normal'], I['Normal'])
    if sheen:                                                       # velvet / pile -> KHR_materials_sheen
        I['Sheen Weight'].default_value = sheen
        I['Sheen Roughness'].default_value = 0.45
    if alpha < 1.0:
        I['Alpha'].default_value = alpha
        m.surface_render_method = 'BLENDED'
        m.use_backface_culling = False
    else:
        m.use_backface_culling = True                               # glTF doubleSided: false
    m['size_m'] = [float(size_m[0]), float(size_m[1])]
    return m


def keys():
    """All library keys accepted by mat()."""
    return sorted([k for k in MANIFEST if not k.startswith('_')] + list(CONST))


def mat(key):
    """Library material by key (cached; shared across the whole scene)."""
    key = ALIAS.get(key, key)
    if key in _cache:
        return _cache[key]
    if key in MANIFEST and not key.startswith('_'):
        e = MANIFEST[key]
        m = _build(key, base=e['base'], nrm=e.get('nrm'), orm=e.get('orm'), rough=e['rough'], metal=e['metal'],
                   nrm_strength=e.get('nrm_strength', 1.0), size_m=e['size_m'], sheen=e.get('sheen', 0.0))
    elif key in CONST:
        c = dict(CONST[key])
        aux = MANIFEST[c.pop('tex')] if 'tex' in c else {}
        m = _build(key, hex=c['hex'], rough=c['rough'], metal=c.get('metal', 0.0), alpha=c.get('alpha', 1.0),
                   nrm=aux.get('nrm'), orm=aux.get('orm'), nrm_strength=c.get('nrm', 1.0),
                   size_m=aux.get('size_m', (1.0, 1.0)))
    else:
        raise KeyError(f'unknown material {key!r}; known: {", ".join(keys())}')
    m['key'] = key
    _cache[key] = m
    return m


def solid(name, hex, roughness, metallic=0):
    """Plain constant-colour material, cached by name."""
    k = ('solid', name)
    if k not in _cache:
        _cache[k] = _build(name, hex=hex, rough=roughness, metal=metallic)
    return _cache[k]


def paint(hex, roughness=0.9):
    """Wall/ceiling/joinery paint, cached per colour + roughness. Matt paint (roughness >= 0.6)
    carries a faint roller-stipple normal map (needs uv_box UVs; harmless without)."""
    hex = '#' + hex.lstrip('#').upper()
    k = ('paint', hex, round(roughness, 2))
    if k not in _cache:
        aux = MANIFEST['_paint'] if (PAINT_STIPPLE and roughness >= 0.6) else {}
        _cache[k] = _build(f'paint_{hex[1:]}_r{int(round(roughness * 100)):02d}', hex=hex, rough=roughness,
                           nrm=aux.get('nrm'), nrm_strength=0.6, size_m=aux.get('size_m', (1.0, 1.0)))
    return _cache[k]


def image_mat(name, path, size_m=None, roughness=0.8):
    """Material from one picture (art, rug, tile). path absolute or relative to blender/textures/.
    size_m=(w, h): the image repeats every w x h metres under uv_box(). size_m=None: the image is
    meant to fill a 0..1 UV square exactly once (give the mesh its own 0..1 UVs)."""
    k = ('image', name)
    if k not in _cache:
        m = _build(name, base=path, rough=roughness, size_m=size_m or (1.0, 1.0))
        m['fit'] = size_m is None
        _cache[k] = m
    return _cache[k]


def _world(obj):
    """World matrix from loc/rot/scale directly (matrix_world is stale until a depsgraph update)."""
    m = obj.matrix_basis.copy()
    return m if obj.parent is None else _world(obj.parent) @ obj.matrix_parent_inverse @ m


def uv_box(obj, scale=1.0, rotate=False, origin=(0.0, 0.0, 0.0)):
    """World-space box-projected UVs at true scale: each face is projected along its dominant
    world axis and UV = metres / (material's size_m * scale), so textures show at real size and
    line up across neighbouring objects. Faces use the size_m of their own material slot.
    Mapping (never mirrored): floors/ceilings U = +X, V = +Y; walls U = horizontal, V = +Z.
    rotate=True turns the texture 90 deg (plank / grain direction along X or horizontal).
    origin = world point that lands on UV (0, 0), e.g. to register a tile joint or motif.
    Works on the base mesh (object mode), writes the first UV layer ('UVMap', created if absent)."""
    me = obj.data
    uv = me.uv_layers[0] if me.uv_layers else me.uv_layers.new(name='UVMap')
    nv, nl, npoly = len(me.vertices), len(me.loops), len(me.polygons)
    if not npoly:
        return
    M = np.array(_world(obj), dtype=np.float64)
    co = np.empty(nv * 3, np.float64)
    me.vertices.foreach_get('co', co)
    co = co.reshape(-1, 3) @ M[:3, :3].T + M[:3, 3] - np.asarray(origin, np.float64)
    nrm = np.empty(npoly * 3, np.float64)
    me.polygons.foreach_get('normal', nrm)
    nrm = nrm.reshape(-1, 3) @ np.linalg.inv(M[:3, :3])               # normals: inverse transpose
    lv = np.empty(nl, np.int32)
    me.loops.foreach_get('vertex_index', lv)
    ls, lt, mi = (np.empty(npoly, np.int32) for _ in range(3))
    me.polygons.foreach_get('loop_start', ls)
    me.polygons.foreach_get('loop_total', lt)
    me.polygons.foreach_get('material_index', mi)
    pol = np.empty(nl, np.int32)
    order = np.argsort(ls)
    pol[:] = np.repeat(order, lt[order])                              # polygon of every loop
    sizes = np.array([tuple(m['size_m']) if (m is not None and 'size_m' in m) else (1.0, 1.0)
                      for m in me.materials] or [(1.0, 1.0)], np.float64) * scale
    S = sizes[np.clip(mi, 0, len(sizes) - 1)][pol]
    P, N = co[lv], nrm[pol]
    ax = np.abs(N).argmax(1)
    sg = np.sign(N[np.arange(nl), ax])
    sg[sg == 0] = 1
    u = np.where(ax == 0, P[:, 1] * sg, np.where(ax == 1, -P[:, 0] * sg, P[:, 0]))
    v = np.where(ax == 2, P[:, 1] * sg, P[:, 2])
    if rotate:
        u, v = v, -u
    out = np.empty(nl * 2, np.float32)
    out[0::2], out[1::2] = u / S[:, 0], v / S[:, 1]
    uv.data.foreach_set('uv', out)
    me.update()

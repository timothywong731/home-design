"""Render settings, daylight and interior emitter helpers. Contract: blender/MULTILEVEL.md section 9; API notes in
blender/lib/README.md."""
import math

import bpy
from mathutils import Matrix, Vector

from .shell import poly_rects

EXPOSURE = -0.6                      # EV, tuned on the empty shell with fills + daylight
# ONE white balance for everything, indoors and outdoors: the preview white point = the lamps (like the phone's auto
# white balance at night); export multiplies the same balance into every atlas and probe.
WHITE_BALANCE = 3000                 # K
WHITE_TINT = -10                     # slightly yellow whites (wall #F2F0EA renders ~#B9B4A8, video ~#BDB9AF)
SUN_ELEVATION = 24.0                 # degrees
SUN_AZIMUTH = 28.0                   # degrees east of the street normal: plan vector TO the sun (0.469, -0.883)
_e, _a = math.radians(SUN_ELEVATION), math.radians(SUN_AZIMUTH)
SUN_DIR = (-round(math.sin(_a) * math.cos(_e), 3), round(math.cos(_a) * math.cos(_e), 3), -round(math.sin(_e), 3))
#          = (-0.429, 0.807, -0.407): the direction the light TRAVELS (from the front right, low)
SUN_STRENGTH = 2.5                   # W/m2
SUN_KELVIN = 3600                    # low golden sun; keeps daylit rooms from going lilac under the lamp white balance
SUN_ANGLE = 1.0                      # degrees
# Physical sky (ShaderNodeTexSky, sun disc off: the lamp gives all direct light) x SKY_TINT x SKY_STRENGTH.
# A physical sky under a 3000 K balance renders saturated blue (phase 1: a (0.86, 0.92, 1.0) sky showed bright blue
# in every window); SKY_TINT is what keeps the one balance usable outdoors. Calibration targets (MULTILEVEL 9): a
# horizontal white card in open shade (sun lamp hidden) has, after the 3000 K balance, blue / red in 1.00 .. 1.25
# and a scene-linear luminance of 0.30 +- 0.03.
# Measured on the bare world (Blender 5.1.1, MULTIPLE_SCATTERING; re-run: blender/test_shell.py -- --sky):
#   balance matrix of 3000 K / tint -10 = [[0.728, -0.302, -0.124], [0.021, 1.169, -0.029], [0.037, 0.132, 2.547]]
#   untinted sky at strength 1: card (2.134, 3.548, 6.048) -> balanced blue / red < 0 (red goes negative);
#   phase-1 tint (1, 0.86, 0.74) x 0.20: card (0.427, 0.610, 0.895), balanced (0.015, 0.696, 2.376): saturated blue;
#   the values below: card (0.534, 0.249, 0.110), luminance 0.300; balanced (0.300, 0.299, 0.334), blue / red 1.11.
# So the sky has to carry a lamp-coloured tint for open shade to read neutral under the lamp balance. Displayed, it is
# a dusk sky: salmon at the horizon (the orthographic elevations show only that band), slate blue overhead.
SKY_TINT = (1.0, 0.281, 0.073)
SKY_STRENGTH = 0.6                   # integration: 0.25 (card 0.30) left the garden, passage and shed near black beside the
                                     # lamp-lit rooms; 0.6 -> card luminance 0.72 (target 0.72 +- 0.07), same tint
# [round 4] The footage outdoors is bright overcast daylight (the phone exposed for it, some 2 stops brighter than the
# lamp-lit rooms); at the one exposure the garden and the side passage (house shadow, sky only) read as night (view luminance 39-41 against
# 110-148 in v2 f_0195-0205 / f_0335-0345). So the exterior rooms (ctx.is_exterior: level X and the balcony) bake their
# lightmaps and probes, and render their stills, under a stronger sky and a softer sun (export_bake.exterior_daylight);
# interiors keep SKY_STRENGTH / SUN_STRENGTH. Measured (480 px Cycles views, mean display luminance): garden 62 -> 103,
# passage 27 -> 65, the sunlit front path 159 -> 193.
EXTERIOR_SKY_GAIN = 3.5
EXTERIOR_SUN_GAIN = 0.6
# What the camera sees (integration decision on MULTILEVEL open question 1): the lamp-coloured sky above stays the
# LIGHT, but camera rays get the same physical sky taken back through the inverse of the balance, so that previews,
# stills, probes and the viewer's sky.jpg show a daylight sky instead of the salmon one. Shown colour (scene linear,
# before exposure) = sky texture x SKY_SHOW_TINT x SKY_SHOW; below the horizon GROUND_SHOW (seen past the site edge).
WB_MATRIX = ((0.728, -0.302, -0.124), (0.021, 1.169, -0.029), (0.037, 0.132, 2.547))   # of 3000 K / tint -10, measured
SKY_SHOW_TINT = (1.0, 0.95, 0.85)
SKY_SHOW = 0.12
GROUND_SHOW = (0.10, 0.11, 0.10)
# sky.sun_rotation: the sky texture's sun stands at plan (sin r, cos r). 128 px panorama: at the sun's elevation the
# brightest sky is 2.8 degrees off the lamp's azimuth; with the disc off the brightest pixel overall is the horizon
# haze under the sun (same azimuth, elevation 1.4), so the contract's "within 15 degrees of -SUN_DIR" holds in
# azimuth only.
SKY_ROTATION = math.pi - _a
FILL_W_PER_M2 = 30.0                 # default per-room fill: wide downward spots on a ~1.3 m grid under the ceiling ...
FILL_UP_W_PER_M2 = 2.5               # ... plus one soft point light per rectangle for the ceiling and cornices
FILL_PITCH = 1.3


DEVICE = None        # build.py --device: None = every GPU, 'CPU', or one GPU by index ('0', '1') when the GPUs are busy


def setup_cycles(samples=64, res=(960, 540)):
    """Cycles on every non-CPU OptiX device (falls back to CUDA, then CPU), AgX, denoised. DEVICE narrows it to the
    CPU or to one GPU."""
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    c = sc.cycles
    c.samples, c.use_adaptive_sampling, c.adaptive_threshold = samples, True, 0.02
    c.max_bounces, c.diffuse_bounces, c.glossy_bounces, c.transmission_bounces = 8, 4, 4, 8
    c.sample_clamp_indirect, c.use_light_tree = 10.0, True
    c.use_denoising = True
    prefs = bpy.context.preferences.addons['cycles'].preferences
    gpu = False
    for t in ('OPTIX', 'CUDA') if str(DEVICE).upper() != 'CPU' else ():
        try:
            prefs.compute_device_type = t
            prefs.get_devices()
        except Exception:
            continue
        gpus = [d for d in prefs.devices if d.type != 'CPU']
        pick = gpus if DEVICE is None else gpus[int(DEVICE):int(DEVICE) + 1]
        for d in prefs.devices:
            d.use = d in pick
        gpu = bool(pick)
        if gpu:
            break
    c.device = 'GPU' if gpu else 'CPU'
    for dn in ('OPTIX', 'OPENIMAGEDENOISE'):
        try:
            c.denoiser = dn
            break
        except TypeError:
            continue
    print(f'[lighting] cycles device={c.device} type={prefs.compute_device_type} '
          f'gpus={[d.name for d in prefs.devices if d.use]} denoiser={c.denoiser}')
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    v = sc.view_settings
    v.view_transform, v.exposure = 'AgX', EXPOSURE
    for look in ('AgX - Medium High Contrast', 'Medium High Contrast', 'None'):     # name differs between builds
        try:
            v.look = look
            break
        except TypeError:
            continue
    try:                                 # preview only (bakes ignore view settings)
        v.use_white_balance, v.white_balance_temperature = True, WHITE_BALANCE
        v.white_balance_tint = WHITE_TINT
    except AttributeError:
        pass


def setup_sky(tint=None, strength=None, rotation=None, display=True):
    """World = physical sky texture (sun disc off). Light (every ray but camera and glossy rays): sky x SKY_TINT ->
    Background(SKY_STRENGTH), the calibrated lamp-coloured sky that reads neutral under the one white balance.
    display=True adds what the CAMERA and mirror reflections see instead (previews, stills, probes, sky.jpg): the same sky
    taken back through the inverse balance (x SKY_SHOW_TINT x SKY_SHOW), so it displays as a daylight sky, and
    GROUND_SHOW below the horizon. Returns the sky node."""
    sc = bpy.context.scene
    w = sc.world or bpy.data.worlds.new('World')
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    new, link = nt.nodes.new, nt.links.new
    sky = new('ShaderNodeTexSky')
    types = [e.identifier for e in sky.bl_rna.properties['sky_type'].enum_items]
    sky.sky_type = next(t for t in ('MULTIPLE_SCATTERING', 'SINGLE_SCATTERING', 'NISHITA') if t in types)
    sky.sun_elevation, sky.sun_rotation = math.radians(SUN_ELEVATION), SKY_ROTATION if rotation is None else rotation
    sky.sun_disc, sky.altitude, sky.air_density, sky.ozone_density = False, 0.0, 1.0, 1.0
    for name in ('aerosol_density', 'dust_density'):          # renamed between builds
        if hasattr(sky, name):
            setattr(sky, name, 1.0)
    mul = new('ShaderNodeVectorMath')
    mul.operation = 'MULTIPLY'
    mul.inputs[1].default_value = SKY_TINT if tint is None else tint
    bg = new('ShaderNodeBackground')
    bg.name = 'sky_light'                                     # export_bake.exterior_daylight scales this one
    bg.inputs['Strength'].default_value = SKY_STRENGTH if strength is None else strength
    out = new('ShaderNodeOutputWorld')
    link(sky.outputs[0], mul.inputs[0])
    link(mul.outputs[0], bg.inputs['Color'])
    if not display:
        link(bg.outputs[0], out.inputs['Surface'])
        return sky
    # camera branch: colour c with WB_MATRIX . c = shown, i.e. c = inverse(WB_MATRIX) . shown
    inv = Matrix(WB_MATRIX).inverted()
    up = new('ShaderNodeSeparateXYZ')                         # view direction: z > 0 = above the horizon
    link(new('ShaderNodeTexCoord').outputs['Generated'], up.inputs[0])
    above = new('ShaderNodeMath')
    above.operation = 'GREATER_THAN'
    above.inputs[1].default_value = 0.0
    link(up.outputs['Z'], above.inputs[0])
    show = new('ShaderNodeVectorMath')
    show.operation = 'MULTIPLY'
    show.inputs[1].default_value = SKY_SHOW_TINT
    link(sky.outputs[0], show.inputs[0])
    pick = new('ShaderNodeMix')
    pick.data_type = 'RGBA'
    link(above.outputs[0], pick.inputs['Factor'])
    pick.inputs['A'].default_value = (*(v / SKY_SHOW for v in GROUND_SHOW), 1.0)
    link(show.outputs[0], pick.inputs['B'])
    comb = new('ShaderNodeCombineXYZ')
    for i in range(3):
        dot = new('ShaderNodeVectorMath')
        dot.operation = 'DOT_PRODUCT'
        dot.inputs[1].default_value = tuple(inv[i])
        link(pick.outputs['Result'], dot.inputs[0])
        link(dot.outputs['Value'], comb.inputs[i])
    seen = new('ShaderNodeBackground')
    seen.name = 'sky_show'
    seen.inputs['Strength'].default_value = SKY_SHOW
    link(comb.outputs[0], seen.inputs['Color'])
    mix = new('ShaderNodeMixShader')
    lp, seen_by = new('ShaderNodeLightPath'), new('ShaderNodeMath')
    seen_by.operation = 'MAXIMUM'                             # camera rays OR glossy rays: glass and gloss paint mirror the
    link(lp.outputs['Is Camera Ray'], seen_by.inputs[0])      # display sky too (they showed a salmon band of the lamp sky);
    link(lp.outputs['Is Glossy Ray'], seen_by.inputs[1])      # the diffuse lightmap bakes never start a glossy ray
    link(seen_by.outputs[0], mix.inputs['Fac'])
    link(bg.outputs[0], mix.inputs[1])
    link(seen.outputs[0], mix.inputs[2])
    link(mix.outputs[0], out.inputs['Surface'])
    return sky


def _portal(col, name, w, h, loc, direction):
    l = bpy.data.lights.new(name, 'AREA')
    l.shape, l.size, l.size_y = 'RECTANGLE', w, h
    l.cycles.is_portal = True
    po = bpy.data.objects.new(name, l)
    po.location = loc
    po.rotation_euler = Vector(direction).to_track_quat('-Z', 'Z').to_euler()
    col.objects.link(po)


def setup_daylight(ctx):
    """Physical sky + low sun lamp, and a Cycles portal 30 mm inside every exterior opening and under every roof
    window. Glass casts no shadow, so interiors get sun and sky through the holes in the mass and in the skin."""
    setup_sky()
    col = ctx.col('lighting')
    sun = bpy.data.lights.new('sun', 'SUN')
    sun.energy, sun.angle = SUN_STRENGTH, math.radians(SUN_ANGLE)
    sun.use_temperature, sun.temperature = True, SUN_KELVIN
    so = bpy.data.objects.new('sun', sun)
    so.rotation_euler = Vector(SUN_DIR).to_track_quat('-Z', 'Y').to_euler()
    col.objects.link(so)
    for oid in ctx.exterior_openings():
        f = ctx.opening_frame(oid)
        c, o = f['center'], f['outward']
        d = f['wall_thickness'] / 2 + 0.03
        s = 1 if f['face_out'] > 0 else -1                    # the outer face is on the +normal side
        _portal(col, 'portal.' + oid, f['width'], f['top'] - f['sill'],
                (c[0] - f['normal'][0] * s * d, c[1] - f['normal'][1] * s * d, f['z0'] + (f['sill'] + f['top']) / 2),
                (-o[0], -o[1], 0))
    for ft in ctx.features:
        if ft['type'] in ('roof_window', 'roof_opening'):
            xs, ys = [p[0] for p in ft['polygon']], [p[1] for p in ft['polygon']]
            x, y = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
            _portal(col, 'portal.' + ft['id'], max(xs) - min(xs), max(ys) - min(ys),
                    (x, y, ctx.ceil_z(ft['room'], x, y) - 0.03), (0, 0, -1))


def setup(ctx, samples=64, res=(960, 540)):
    setup_cycles(samples, res)
    setup_daylight(ctx)


# ------------------------------------------------------------------ interior emitters (kind='light')
def _add(ctx, room, name, data, loc, direction=None):
    data.use_temperature = True
    ob = bpy.data.objects.new(name, data)
    ob.location = loc
    if direction is not None:
        ob.rotation_euler = Vector(direction).to_track_quat('-Z', 'Y').to_euler()
    return ctx.add(ob, room, 'light')


def downlight(ctx, room, x, y, z=None, watts=60, kelvin=2850, spot_deg=115, radius=0.035, name=None):
    """Recessed ceiling spot emitter pointing straight down. z defaults to 15 mm below the ceiling over (x, y)
    (ceiling zones and slopes included). Only the emitter: the visible bezel/trim is props.downlight."""
    l = bpy.data.lights.new(name or f'{room}.downlight', 'SPOT')
    l.energy, l.temperature, l.spot_size, l.spot_blend, l.shadow_soft_size = watts, kelvin, math.radians(spot_deg), 0.6, radius
    return _add(ctx, room, l.name, l, (x, y, ctx.ceil_z(room, x, y) - 0.015 if z is None else z), (0, 0, -1))


def bulb(ctx, room, loc, watts=12, kelvin=2700, radius=0.025, name=None):
    """Omnidirectional warm bulb (candle bulb, lamp under a shade, wall light). ~8-12 W per candle bulb
    of a chandelier, 25-40 W for a single table/pendant lamp."""
    l = bpy.data.lights.new(name or f'{room}.bulb', 'POINT')
    l.energy, l.temperature, l.shadow_soft_size = watts, kelvin, radius
    return _add(ctx, room, l.name, l, loc)


def strip(ctx, room, p0, p1, watts_per_m=10, kelvin=3000, width=0.012, direction=(0, 0, -1), name=None):
    """LED strip between two points (under-cabinet / shelf lighting): a thin rectangular area light
    shining along `direction` (default down)."""
    p0, p1 = Vector(p0), Vector(p1)
    l = bpy.data.lights.new(name or f'{room}.strip', 'AREA')
    l.shape, l.size, l.size_y = 'RECTANGLE', width, (p1 - p0).length
    l.energy, l.temperature = watts_per_m * (p1 - p0).length, kelvin
    ob = _add(ctx, room, l.name, l, (p0 + p1) / 2)
    z = -Vector(direction).normalized()                 # area lights emit along local -Z
    yv = (p1 - p0).normalized()
    xv = yv.cross(z).normalized()
    ob.rotation_euler = Matrix((xv, yv, xv.cross(yv))).transposed().to_euler()
    return ob


def fill(ctx, room):
    """Default fill for a kind 'room' / 'stairwell' room that has no light fittings yet (empty-shell previews stay
    legible); never outdoors. A grid of wide ceiling spots pointing down, i.e. lit like the real rooms (recessed
    downlights): floors and the lower walls get their share. (A point light under the ceiling left the wall below
    the dado ~15x darker than the wall beside the lamp and the floor a stop down.) The lamps hang 0.35 below
    zc = floor + min(room height, ceilingDefault), lowered to the ceiling over each lamp (zones, slopes).
    Objects are tagged obj['fill']=True; build.py only adds them to rooms without kind='light' objects."""
    out = []
    fz = ctx.floor_z(room)
    zc = fz + min(ctx.ceil_z(room) - fz, ctx.spec['ceilingDefault'])
    for x0, x1, y0, y1 in poly_rects(ctx.room_poly(room, rect=True)):
        area = (x1 - x0) * (y1 - y0)
        if area < 0.5:
            continue
        nx, ny = max(1, round((x1 - x0) / FILL_PITCH)), max(1, round((y1 - y0) / FILL_PITCH))
        for i in range(nx):
            for j in range(ny):
                x, y = x0 + (i + 0.5) * (x1 - x0) / nx, y0 + (j + 0.5) * (y1 - y0) / ny
                z = min(zc, ctx.ceil_z(room, x, y)) - 0.35    # 0.35 down: clear of vaults and bulkheads
                if z > fz + 0.6:
                    out.append(downlight(ctx, room, x, y, z=z, watts=FILL_W_PER_M2 * area / (nx * ny), kelvin=3000,
                                         radius=0.06, name=f'{room}.fill'))
        x, y = (x0 + x1) / 2, (y0 + y1) / 2
        out.append(bulb(ctx, room, (x, y, min(zc, ctx.ceil_z(room, x, y)) - 0.35), watts=FILL_UP_W_PER_M2 * area,
                        kelvin=3000, radius=0.12, name=f'{room}.fill'))
    for ob in out:
        ob['fill'] = True
        ob.visible_camera = ob.visible_glossy = False          # no white discs through glazing / in mirrors and glass
    return out


DAYLIGHT_RGB = (1.0, 0.466, 0.206)   # the open-shade card of SKY_TINT normalised: reads neutral under the one balance


def daylight_fill(ctx, room, name, centre, size, toward, watts):
    """[round 4] A soft rectangle of daylight for a room that the footage shows daylit but whose openings the bake
    starves (the shed workshop: shaded veranda, a hedge 0.8 m off). Tagged obj['daylight']: export_bake keeps it on in the
    lights-off bakes (it is not a lamp) and off in the circuit bakes; invisible to the camera and in reflections."""
    l = bpy.data.lights.new(name, 'AREA')
    l.shape, l.size, l.size_y, l.energy, l.color = 'RECTANGLE', size[0], size[1], watts, DAYLIGHT_RGB
    ob = bpy.data.objects.new(name, l)
    ob.location = centre
    ob.rotation_euler = Vector(toward).to_track_quat('-Z', 'Y').to_euler()
    ctx.add(ob, room, 'light')
    ob['daylight'] = True
    ob.visible_camera = ob.visible_glossy = False
    return ob


def void_fill(ctx, room):
    """Dim bulbs in a space that is only looked into through a hatch or doors (eaves voids, the shed store) and has no
    fitting yet: baked shut it came out pitch black, and what a door reveals must exist (INTERACT.md). One 3 W bulb per
    grid rectangle of the polygon, at its highest point, 0.12 under the ceiling. Tagged obj['fill'] like fill()."""
    out, fz = [], ctx.floor_z(room)
    for x0, x1, y0, y1 in poly_rects(ctx.room_poly(room, rect=True)):
        if (x1 - x0) * (y1 - y0) < 0.3:
            continue
        d = min(0.3, (x1 - x0) / 2, (y1 - y0) / 2)
        pts = [((x0 + x1) / 2, (y0 + y1) / 2)] + [(x, y) for x in (x0 + d, x1 - d) for y in (y0 + d, y1 - d)]
        x, y = max(pts, key=lambda q: ctx.ceil_z(room, *q) or fz)
        top = ctx.ceil_z(room, x, y) or fz
        if top - fz > 0.3:
            out.append(bulb(ctx, room, (x, y, max(fz + 0.15, min(top - 0.12, fz + 1.8))), watts=3, kelvin=3000, radius=0.03,
                            name=f'{room}.fill'))
    for ob in out:
        ob['fill'] = True
        ob.visible_camera = ob.visible_glossy = False
    return out

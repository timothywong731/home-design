"""Render settings, daylight and interior emitter helpers. Documented in blender/lib/README.md."""
import math

import bpy
from mathutils import Vector

from .shell import poly_rects

EXPOSURE = -0.6                      # EV, tuned on the empty shell with fills + daylight
WHITE_BALANCE = 3000                 # K: preview white point = the fill lamps, like the phone's auto white balance at night (daylight reads cool)
WHITE_TINT = -10                     # slightly yellow whites (wall #F2F0EA renders ~#B9B4A8, video ~#BDB9AF)
SUN_DIR = (-0.38, 0.72, -0.58)       # direction the light TRAVELS: from the front-right, 35 deg up
SUN_STRENGTH = 2.5
SUN_KELVIN = 3600                    # low golden sun; with SKY_COLOR keeps daylit rooms from going lilac under the lamp white balance
# Dusk sky. Integration: the first daylight sky (0.86, 0.92, 1.0) x 0.6 showed saturated bright blue in every window
# under the 3000 K view white balance, where the video (shot at night) has dark glass; interiors barely changed.
SKY_STRENGTH = 0.22
SKY_COLOR = (1.0, 0.86, 0.74)
FILL_W_PER_M2 = 30.0                 # default per-room fill: wide downward spots on a ~1.3 m grid under the ceiling ...
FILL_UP_W_PER_M2 = 2.5               # ... plus one soft point light per rectangle for the ceiling and cornices
FILL_PITCH = 1.3


def setup_cycles(samples=64, res=(960, 540)):
    """Cycles on every non-CPU OptiX device (falls back to CUDA, then CPU), AgX, denoised."""
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    c = sc.cycles
    c.samples, c.use_adaptive_sampling, c.adaptive_threshold = samples, True, 0.02
    c.max_bounces, c.diffuse_bounces, c.glossy_bounces, c.transmission_bounces = 8, 4, 4, 8
    c.sample_clamp_indirect, c.use_light_tree = 10.0, True
    c.use_denoising = True
    prefs = bpy.context.preferences.addons['cycles'].preferences
    gpu = False
    for t in ('OPTIX', 'CUDA'):
        try:
            prefs.compute_device_type = t
            prefs.get_devices()
        except Exception:
            continue
        for d in prefs.devices:
            d.use = d.type != 'CPU'
        gpu = any(d.use for d in prefs.devices)
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


def setup_daylight(ctx):
    """Late-afternoon sky + sun, and a Cycles portal just inside every external opening."""
    sc = bpy.context.scene
    w = sc.world or bpy.data.worlds.new('World')
    sc.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs['Color'].default_value = (*SKY_COLOR, 1)
    bg.inputs['Strength'].default_value = SKY_STRENGTH
    col = ctx.col('lighting')
    sun = bpy.data.lights.new('sun', 'SUN')
    sun.energy, sun.angle = SUN_STRENGTH, math.radians(1.5)
    sun.use_temperature, sun.temperature = True, SUN_KELVIN
    so = bpy.data.objects.new('sun', sun)
    so.rotation_euler = Vector(SUN_DIR).to_track_quat('-Z', 'Y').to_euler()
    col.objects.link(so)
    for oid, o in ctx.openings.items():
        if 'outside' not in o['connects']:
            continue
        f = ctx.opening_frame(oid)
        inward = f['normal'] * (-1 if f['room_pos'] == 'outside' else 1)
        l = bpy.data.lights.new('portal.' + oid, 'AREA')
        l.shape, l.size, l.size_y = 'RECTANGLE', f['width'], f['top'] - f['sill']
        l.cycles.is_portal = True
        po = bpy.data.objects.new('portal.' + oid, l)
        c = f['center']
        d = f['wall_thickness'] / 2 + 0.03
        po.location = (c.x + inward.x * d, c.y + inward.y * d, f['z0'] + (f['sill'] + f['top']) / 2)
        po.rotation_euler = Vector((inward.x, inward.y, 0)).to_track_quat('-Z', 'Z').to_euler()
        col.objects.link(po)


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
    """Recessed ceiling spot emitter pointing straight down. z defaults to 15 mm below the room ceiling.
    Only the emitter: the visible bezel/trim is props.downlight."""
    l = bpy.data.lights.new(name or f'{room}.downlight', 'SPOT')
    l.energy, l.temperature, l.spot_size, l.spot_blend, l.shadow_soft_size = watts, kelvin, math.radians(spot_deg), 0.6, radius
    return _add(ctx, room, l.name, l, (x, y, ctx.ceil_z(room) - 0.015 if z is None else z), (0, 0, -1))


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
    from mathutils import Matrix
    ob.rotation_euler = Matrix((xv, yv, xv.cross(yv))).transposed().to_euler()
    return ob


def fill(ctx, room):
    """Default fill for a room that has no light fittings yet (empty-shell previews stay legible).
    A grid of wide ceiling spots pointing down, i.e. lit like the real rooms (recessed downlights):
    floors and the lower walls get their share. (A point light under the ceiling left the wall below
    the dado ~15x darker than the wall beside the lamp and the floor a stop down, which made floor and
    dado colours read too dark and too brown against the reference frames.)
    Objects are tagged obj['fill']=True; build.py only adds them to rooms without kind='light' objects."""
    out = []
    zc = min(ctx.ceil_z(room), ctx.spec['ceilingDefault'])
    for x0, x1, y0, y1 in poly_rects(ctx.room_poly(room)):
        area = (x1 - x0) * (y1 - y0)
        if area < 0.5:
            continue
        nx, ny = max(1, round((x1 - x0) / FILL_PITCH)), max(1, round((y1 - y0) / FILL_PITCH))
        for i in range(nx):
            for j in range(ny):
                out.append(downlight(ctx, room, x0 + (i + 0.5) * (x1 - x0) / nx, y0 + (j + 0.5) * (y1 - y0) / ny,
                                     z=zc - 0.35, watts=FILL_W_PER_M2 * area / (nx * ny), kelvin=3000, radius=0.06,
                                     name=f'{room}.fill'))    # 0.35 down: clear of vaults and bulkheads
        out.append(bulb(ctx, room, ((x0 + x1) / 2, (y0 + y1) / 2, zc - 0.35), watts=FILL_UP_W_PER_M2 * area, kelvin=3000,
                        radius=0.12, name=f'{room}.fill'))
    for ob in out:
        ob['fill'] = True
        ob.visible_camera = ob.visible_glossy = False          # no white discs through glazing / in mirrors and glass
    return out

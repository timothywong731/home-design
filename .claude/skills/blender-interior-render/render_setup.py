"""Interior still setup helpers, tested on Blender 5.1.1 headless."""
import bpy, math
from mathutils import Vector

def colour_management(view='AgX', look='Medium High Contrast', exposure=0.0):
    """5.x: view_transform 'AgX' | 'Filmic' | 'Standard' | 'Khronos PBR Neutral' | 'Flim'(if present).
    Look names are bare ('Medium High Contrast'), NOT 'AgX - Medium High Contrast' as in 4.0/4.1."""
    v = bpy.context.scene.view_settings; v.view_transform = view; v.exposure = exposure
    try: v.look = look
    except TypeError: v.look = 'None'

def world_sky(strength=1.0, rgb=(0.55, 0.7, 1.0)):
    w = bpy.context.scene.world or bpy.data.worlds.new("World"); bpy.context.scene.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs['Color'].default_value = (*rgb, 1); bg.inputs['Strength'].default_value = strength

def sun(direction_deg=(50, 0, 30), strength=3.0, angle_deg=0.53, kelvin=5500):
    l = bpy.data.lights.new("sun", 'SUN'); l.energy = strength; l.angle = math.radians(angle_deg)
    l.use_temperature = True; l.temperature = kelvin   # 5.x: Light.use_temperature / temperature
    o = bpy.data.objects.new("sun", l); o.rotation_euler = [math.radians(a) for a in direction_deg]
    bpy.context.collection.objects.link(o); return o

def window_portal(centre, size, normal_rot=(math.pi / 2, 0, 0)):
    """Area light flagged as Cycles portal, placed just INSIDE a window opening, facing into the room.
    Needs a World with a non-black Background. Portal adds no light itself: it only guides sampling."""
    l = bpy.data.lights.new("portal", 'AREA'); l.shape = 'RECTANGLE'; l.size, l.size_y = size
    l.cycles.is_portal = True
    o = bpy.data.objects.new("portal", l); o.location = centre; o.rotation_euler = normal_rot
    bpy.context.collection.objects.link(o); return o

def lamp(loc, watts=40, kelvin=2700, radius=0.06, spot_deg=None):
    """Warm interior bulb. Point light W is radiometric: ~40-100 W for a lamp in Blender units."""
    l = bpy.data.lights.new("lamp", 'SPOT' if spot_deg else 'POINT'); l.energy = watts
    l.shadow_soft_size = radius; l.use_temperature = True; l.temperature = kelvin
    if spot_deg: l.spot_size = math.radians(spot_deg)
    o = bpy.data.objects.new("lamp", l); o.location = loc; bpy.context.collection.objects.link(o); return o

def camera(loc, target, lens=18, eye_h=None):
    """Eye-height camera (1.5-1.65 m) looking at target; 16-20 mm on full frame for rooms, keep verticals
    vertical (no pitch) or use shift_y instead of tilting."""
    c = bpy.data.cameras.new("cam"); c.lens = lens; c.clip_start = 0.05
    o = bpy.data.objects.new("cam", c); o.location = loc
    d = Vector(target) - Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.collection.objects.link(o); bpy.context.scene.camera = o; return o

def cycles_still(path, res=(1920, 1080), samples=256, gpu=True, denoise=True, clamp=10.0):
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'
    sc.cycles.samples = samples; sc.cycles.use_denoising = denoise; sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    sc.cycles.sample_clamp_indirect = clamp      # kills fireflies from small bright lamps
    sc.cycles.max_bounces = 8; sc.cycles.diffuse_bounces = 4; sc.cycles.use_light_tree = True
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'PNG'; sc.render.filepath = path
    if gpu:
        p = bpy.context.preferences.addons['cycles'].preferences
        for t in ('OPTIX', 'CUDA'):
            try: p.compute_device_type = t; p.get_devices(); break
            except Exception: continue
        for d in p.devices: d.use = d.type != 'CPU'
        if any(d.use for d in p.devices): sc.cycles.device = 'GPU'
    bpy.ops.render.render(write_still=True)

"""Preview cameras and Cycles renders (build/preview/<room>_<cam>[_<tag>].jpg)."""
import math
from pathlib import Path

import bpy
from mathutils import Vector

# Shell review cameras matched to the reference frames of spec/rooms/<id>.md section 9 (world coords,
# portrait ultrawide: render with --res 540x960). Used for rooms whose module defines no CAMERAS.
def _c(name, pos, look, ref, fov=100):
    return dict(name=name, pos=pos, look=look, fov_deg=fov, ref=ref)


DEFAULT_CAMERAS = {
    'vestibule': [_c('street', (0.2, 1.7, 1.6), (0.0, 0.0, 1.3), 'f_0012'),
                  _c('window', (-0.2, 0.9, 1.6), (0.9, 0.45, 2.0), 'f_0019'),
                  _c('vault', (0.0, 0.3, 1.5), (0.0, 1.3, 2.2), 'f_0021')],
    'hallway': [_c('inner', (0.0, 3.33, 1.75), (0.0, 1.83, 1.7), 'f_0057'),
                _c('front', (-0.1, 2.23, 1.6), (0.0, 8.0, 1.4), 'f_0064'),
                _c('doorcase', (-0.3, 3.33, 1.6), (0.65, 4.0, 2.3), 'f_0082'),
                _c('arch', (0.0, 8.13, 1.6), (0.0, 10.0, 2.7), 'f_0283'),
                _c('lobby', (0.0, 9.13, 1.6), (0.3, 5.0, 1.5), 'f_0751'),
                _c('rear', (-0.1, 12.73, 1.6), (-0.1, 6.0, 1.4), 'f_0745')],
    'stairs': [_c('foot', (0.1, 3.73, 1.3), (0.5, 6.6, 1.9), 'f_0243'),
               _c('passage', (-0.3, 7.13, 1.5), (0.6, 5.6, 2.3), 'f_0773')],
    'living': [_c('bay', (2.4, 3.59, 1.5), (2.5, 0.0, 1.4), 'f_0791'),
               _c('tvwall', (3.4, 3.19, 1.5), (0.8, 2.8, 1.4), 'f_0099'),
               _c('north', (1.4, 3.59, 1.5), (4.0, 4.73, 1.5), 'f_0785'),
               _c('baycorner', (2.4, 1.19, 1.5), (1.1, 0.3, 2.2), 'f_0127')],
    'kitchen': [_c('entry', (0.65, 8.26, 1.5), (4.3, 8.0, 1.4), 'f_0755'),
                _c('nook', (2.75, 7.01, 1.5), (2.6, 9.0, 1.4), 'f_0766'),
                _c('halldoor', (3.05, 8.11, 1.5), (1.25, 8.2, 1.3), 'f_0388'),
                _c('sink', (2.95, 7.61, 1.5), (2.9, 5.31, 1.4), 'f_0378')],
    'utility': [_c('far', (0.9, 10.8, 1.5), (3.1, 11.3, 1.3), 'f_0450'),
                _c('wcdoor', (1.8, 11.26, 1.5), (1.6, 10.2, 0.9), 'f_0499'),
                _c('fromhall', (-0.2, 10.8, 1.5), (3.1, 11.0, 1.3), 'f_0567'),
                _c('out', (1.8, 10.86, 1.5), (0.6, 10.8, 1.4), 'f_0546')],
    'wc': [_c('pan', (1.6, 9.75, 1.5), (3.1, 9.75, 1.3), 'f_0507'),
           _c('basin', (1.6, 9.75, 1.5), (0.6, 9.75, 1.5), 'f_0522'),
           _c('door', (2.2, 9.66, 1.5), (1.7, 10.14, 1.3), 'f_0528')],
    'dining': [_c('entry', (-0.05, 12.66, 1.45), (2.5, 16.0, 1.3), 'f_0574'),
               _c('east', (0.25, 14.86, 1.45), (3.1, 14.61, 1.4), 'f_0675'),
               _c('north', (1.55, 12.76, 1.45), (1.3, 16.86, 1.4), 'f_0705'),
               _c('south', (0.85, 14.56, 1.45), (0.2, 12.36, 1.5), 'f_0741'),
               _c('nw', (0.95, 15.66, 1.45), (0.0, 16.86, 2.0), 'f_0681')],
}


def default_cameras(ctx, room):
    """Reference-matched shell cameras of a room (DEFAULT_CAMERAS)."""
    return DEFAULT_CAMERAS[room]


def camera(name, pos, look, fov_deg=75, **_):
    """Perspective camera at pos looking at look. fov_deg spans the LONGER image side."""
    cam = bpy.data.cameras.new(name)
    cam.sensor_fit, cam.angle, cam.clip_start, cam.clip_end = 'AUTO', math.radians(fov_deg), 0.03, 200
    ob = bpy.data.objects.new(name, cam)
    ob.location = pos
    ob.rotation_euler = (Vector(look) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.collection.objects.link(ob)
    return ob


def render(cam, path, res=(960, 540), samples=64):
    sc = bpy.context.scene
    sc.camera = cam
    sc.cycles.samples = samples
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.image_settings.file_format = 'JPEG'
    sc.render.image_settings.quality = 90
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    sc.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    print(f'[preview] wrote {path}')


def render_room(ctx, room, cams, out_dir, res, samples, tag=None, only=None):
    """Render every camera dict (name, pos, look, fov_deg) of a room; returns the written paths."""
    out = []
    for c in cams:
        if only and c['name'] != only:
            continue
        ob = camera(f'cam.{room}.{c["name"]}', c['pos'], c['look'], c.get('fov_deg', 75))
        path = Path(out_dir) / f'{room}_{c["name"]}{"_" + tag if tag else ""}.jpg'
        render(ob, path, res, samples)
        out.append(path)
    return out


def render_plan(ctx, path, res=(960, 540), samples=64, cut_z=1.5):
    """Top-down orthographic view of the whole floor, +Y up, ceilings hidden, sectioned at cut_z
    (camera clipping), so door/window openings show as gaps and cut walls read as dark poche."""
    B = ctx.spec['bounds']
    w, h = B['maxX'] - B['minX'] + 0.6, B['maxY'] - B['minY'] + 0.6
    cam = bpy.data.cameras.new('cam.plan')
    cam.type, cam.ortho_scale, cam.clip_start, cam.clip_end = 'ORTHO', max(w, h), 30 - cut_z, 100
    ob = bpy.data.objects.new('cam.plan', cam)
    ob.location = ((B['minX'] + B['maxX']) / 2, (B['minY'] + B['maxY']) / 2, 30)
    bpy.context.scene.collection.objects.link(ob)
    hidden = [o for o in bpy.data.objects if o.get('part') == 'ceiling' and not o.hide_render]
    for o in hidden:
        o.hide_render = True
    long = max(1600, max(res))
    vs = bpy.context.scene.view_settings
    keep = vs.exposure, vs.white_balance_temperature, vs.white_balance_tint
    # floors are lit at grazing angles by the fills, and with the ceilings off daylight dominates
    vs.exposure, vs.white_balance_temperature, vs.white_balance_tint = keep[0] + 0.8, 4300, 0
    try:
        render(ob, path, (round(long * w / h), long) if h > w else (long, round(long * h / w)), samples)
    finally:
        vs.exposure, vs.white_balance_temperature, vs.white_balance_tint = keep
        for o in hidden:
            o.hide_render = False

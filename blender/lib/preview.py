"""Preview cameras and Cycles renders (build/preview/<what>_<cam>[_<tag>].jpg): eye-height room views, and the
orthographic plan / section / elevation views of blender/MULTILEVEL.md section 5."""
import math
from pathlib import Path

import bpy
from mathutils import Vector

from . import shell
from .ctx import point_in_poly

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
    # rooms where the automatic pair of views starts inside the mass or outside the roof
    'stairs2': [_c('foot', (0.57, 5.3, 4.9), (0.57, 8.2, 5.4), 'v4_f_0300', 90),
                _c('well', (0.57, 7.0, 5.9), (0.3, 7.2, 8.87), 'v4_f_0360', 100),
                _c('head', (-0.3, 8.9, 7.5), (0.6, 7.0, 4.6), 'v6_f_0010', 100)],
    'eaves_front': [_c('in', (0.2, 2.1, 7.0), (3.5, 1.7, 6.8), 'v5_f_0296', 100)],     # dark unless --pose 1 (hatches open)
    'eaves_rear': [_c('in', (1.7, 7.1, 7.1), (4.0, 8.0, 6.9), 'v5_f_0303', 100)],
    # pseudo-rooms: used until blender/rooms/<pseudo>.py brings its own CAMERAS (refs: reference/v2 stills)
    'front': [_c('street', (2.0, -11.0, 1.6), (2.0, 0.0, 3.6), 'v2_t963', 75),
              _c('forecourt', (3.9, -4.3, 1.6), (0.3, 0.0, 1.7), 'v2_t955', 90),
              _c('door', (0.3, -2.6, 1.6), (0.0, 0.0, 1.6), 'v2_t948', 80),
              _c('mouth', (4.98, -2.5, 1.6), (4.95, 6.0, 1.0), None, 80)],
    'side_passage': [_c('passage', (4.0, 16.8, 1.5), (4.05, 9.0, 1.0), 'v2_t342', 80),
                     _c('steps', (4.25, 11.2, 1.5), (3.6, 9.1, 0.4), 'v2_t318', 80),
                     _c('alley', (4.98, 1.6, 1.5), (5.0, 9.6, 0.9), None, 80),
                     _c('out', (3.8, 10.5, 1.5), (4.1, 17.5, 1.0), None, 80)],
    'garden': [_c('house', (1.6, 22.9, 1.15), (1.3, 17.4, 3.6), 'v2_t250', 95),
               _c('shed', (1.3, 18.3, 1.55), (1.9, 24.0, 0.7), 'v2_t188', 90),
               _c('deck', (3.1, 20.2, 1.55), (-0.5, 17.6, 0.8), 'v2_t174', 90),
               _c('path', (3.9, 23.0, 1.15), (4.0, 17.5, 1.0), 'v2_t232', 80)],
    'shed': [_c('veranda', (0.3, 24.3, 1.2), (3.6, 25.1, 0.8), 'v2_t256', 90),
             _c('workshop', (3.7, 28.2, 1.2), (0.2, 25.6, 0.7), None, 90),
             _c('workshop_door', (0.2, 28.2, 1.2), (3.3, 25.2, 0.7), None, 90)],
    'roof': [_c('aerial_front', (9.0, -13.0, 13.0), (2.0, 4.0, 4.5), None, 50),
             _c('aerial_rear', (9.5, 31.0, 14.0), (1.5, 12.0, 4.0), None, 50),
             _c('aerial_west', (-9.0, 27.0, 13.0), (1.5, 12.0, 5.0), None, 50)],
}
PLAN_CUT = 0.9          # plan views are cut this far above the highest floor of the level (doors and windows show as gaps)
SECTION_X = -0.25       # the long section cuts the hall and the landings
SIDES = ('front', 'rear', 'flank')


def default_cameras(ctx, room):
    """Cameras of a room whose module defines none: the reference-matched ground-floor set (DEFAULT_CAMERAS), else
    two eye-height views from the two polygon corners that are farthest apart, each looking at the other."""
    if room in DEFAULT_CAMERAS:
        return DEFAULT_CAMERAS[room]
    if room not in ctx.rooms and room not in ctx.building_rooms:
        return []                                             # pseudo-rooms: their module supplies CAMERAS
    poly, fz = ctx.room_poly(room), ctx.floor_z(room)
    a, b = max(((p, q) for p in poly for q in poly), key=lambda pq: math.dist(*pq))
    mid = (sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly))
    out = []
    for name, p, q in (('a', a, b), ('b', b, a)):
        d = math.dist(p, q)
        pos = (p[0] + (q[0] - p[0]) * 0.45 / d, p[1] + (q[1] - p[1]) * 0.45 / d)
        if not point_in_poly(*pos, poly):
            pos = ((p[0] + 2 * mid[0]) / 3, (p[1] + 2 * mid[1]) / 3)
        head = (ctx.ceil_z(room, *pos) or fz + 2.4) - fz
        out.append(_c(name, (*pos, fz + min(1.5, max(0.5, head - 0.2))), (*q, fz + 1.0), None))
    return out


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
    """Render every camera dict (name, pos, look, fov_deg) of a room (only: one name, or 'first'); returns the paths."""
    out = []
    if only == 'first':
        cams, only = cams[:1], None
    for c in cams:
        if only and c['name'] != only:
            continue
        ob = camera(f'cam.{room}.{c["name"]}', c['pos'], c['look'], c.get('fov_deg', 75))
        path = Path(out_dir) / f'{room}_{c["name"]}{"_" + tag if tag else ""}.jpg'
        render(ob, path, res, samples)
        out.append(path)
    return out


# ------------------------------------------------------------------ orthographic views
def plan_cut(ctx, level):
    """World Z of the plan cut of a level: PLAN_CUT above its highest kind-'room' floor (B -1.41, G 0.9, 1 4.32,
    2 7.39). Lower than the dollhouse cutZ of the manifest (just under the lowest ceiling), which runs above the
    door heads."""
    return max(ctx.floor_z(r) for r in ctx.rooms_on(level) if ctx.kind(r) == 'room') + PLAN_CUT


def _ortho(ctx, name, eye, forward, w, h, path, res, samples, cap=None, mirror=False):
    """Orthographic render of a w x h (metres) frame centred on `eye`, looking along `forward`, with everything in
    front of the plane through `eye` clipped away. cap = (axis, coordinate): the mass cut by that plane is drawn
    as black poche (shell.section_cap)."""
    cam = bpy.data.cameras.new(name)
    cam.type, cam.ortho_scale, cam.clip_start, cam.clip_end = 'ORTHO', max(w, h), 60 - 0.002, 400
    ob = bpy.data.objects.new(name, cam)
    f = Vector(forward).normalized()
    ob.location = Vector(eye) - f * 60
    ob.rotation_euler = f.to_track_quat('-Z', 'Y').to_euler()
    if mirror:
        ob.scale.x = -1
    bpy.context.scene.collection.objects.link(ob)
    cob = shell.section_cap(ctx, *cap) if cap and ctx.grid is not None else None
    if cob:
        bpy.context.scene.collection.objects.link(cob)
    long = max(res)
    try:
        render(ob, path, (round(long * w / h), long) if h > w else (long, round(long * h / w)), samples)
    finally:
        if cob:
            bpy.data.objects.remove(cob, do_unlink=True)


def render_plan(ctx, level, path, res=(960, 540), samples=64):
    """Top view of one level, +Y up, cut at plan_cut(level): doors and windows are gaps, cut mass is black.
    Level 'X' = the whole site from above, uncut."""
    if level == 'X':
        B = ctx.spec['siteBounds']
        x0, x1, y0, y1, z, cap = B['minX'], B['maxX'], B['minY'], B['maxY'], 30.0, None
    else:
        pts = [p for r in ctx.rooms_on(level) for p in ctx.room_poly(r)]
        B = ctx.spec['bounds']
        x0, x1 = min([B['minX']] + [p[0] for p in pts]) - 0.3, max([B['maxX']] + [p[0] for p in pts]) + 0.3
        y0, y1 = min([B['minY']] + [p[1] for p in pts]) - 0.3, max([B['maxY']] + [p[1] for p in pts]) + 0.3
        z = plan_cut(ctx, level)
        cap = (2, z)
    _ortho(ctx, 'cam.plan', ((x0 + x1) / 2, (y0 + y1) / 2, z), (0, 0, -1), x1 - x0, y1 - y0, path, res, samples, cap)


def render_section(ctx, path, res=(960, 540), samples=64, x=SECTION_X):
    """Long section cut at x (default -0.25: hall and landings), showing what lies EAST of the cut (the stairs).
    The image is mirrored so that +Y (the garden) is on the right, as in spec/plan_section.png and elev:flank."""
    B = ctx.spec['bounds']
    y0, y1, z0, z1 = B['minY'] - 1.2, B['maxY'] + 1.6, -2.8, 9.7
    _ortho(ctx, 'cam.section', (x, (y0 + y1) / 2, (z0 + z1) / 2), (1, 0, 0), y1 - y0, z1 - z0, path, res, samples,
           (0, x), mirror=True)


def render_elev(ctx, side, path, res=(960, 540), samples=64):
    """Orthographic elevation: front (from the street), rear (from the garden) or flank (from the east alley).
    The view starts 5 m (front), 5.5 m (rear: in front of the shed) or 0.85 m (flank) off the house, so neighbours do not hide it."""
    B = ctx.spec['bounds']
    xc, yc, zc, h = (B['minX'] + B['maxX']) / 2, (B['minY'] + B['maxY']) / 2, 4.4, 11.4
    eye, fwd, w = {'front': ((xc, B['minY'] - 5.0, zc), (0, 1, 0), B['maxX'] - B['minX'] + 5),
                   'rear': ((xc, B['maxY'] + 5.5, zc), (0, -1, 0), B['maxX'] - B['minX'] + 5),
                   'flank': ((B['maxX'] + 0.85, yc, zc), (-1, 0, 0), B['maxY'] - B['minY'] + 4)}[side]
    _ortho(ctx, 'cam.elev', eye, fwd, w, h, path, res, samples)

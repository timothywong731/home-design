"""Joinery / mouldings / materials test (owner d, blender/MULTILEVEL.md section 12).

  blender -b --factory-startup --python blender/test_joinery.py -- [--house spec/house.json]
      [--only id,id] [--pose 0|1] [--render] [--res 420x560] [--samples 32] [--out build/joinery] [--tag t]

Asserts: joinery.validate() is empty; every material key of section 8 and every material named by the spec resolves;
trim_runs on living / hallway / stairs / landing1_rear / green_bedroom give the expected runs. Then, for every opening
with joinery: a wall slab with the hole from ctx.opening_frame, joinery.build_opening, checks on names / rooms /
interaction tags, and (state 1) that no moving part ends inside the wall. --render writes one picture per side to
<out>/<id>_<in|out>[_<tag>].jpg: look at them. Prints JOINERY OK, exits 1 on failure."""
import argparse, json, math, os, sys, traceback

import bpy
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(ROOT, 'blender'))
from lib import ctx as C, interact as IX, joinery as J, materials as M, mouldings as mo   # noqa: E402


def args():
    p = argparse.ArgumentParser()
    p.add_argument('--house', default=os.path.join(ROOT, 'spec', 'house.json'))
    p.add_argument('--only', default='')
    p.add_argument('--pose', type=int, default=0)
    p.add_argument('--render', action='store_true')
    p.add_argument('--res', default='420x560')
    p.add_argument('--samples', type=int, default=32)
    p.add_argument('--out', default=os.path.join(ROOT, 'build', 'joinery'))
    p.add_argument('--tag', default='')
    return p.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])


# ------------------------------------------------------------------------------------------------ pure checks
def check_materials(h):
    keys = set(M.SPEC_KEYS)
    keys |= {r['floor']['material'] for r in h.rooms.values() if (r.get('floor') or {}).get('material')}
    ext = h.spec.get('exterior', {})
    keys |= {z['surface'] for z in ext.get('zones', [])} | {b['material'] for b in ext.get('boundaries', []) if b.get('material')}
    keys |= {f['finish'] for f in ext.get('facades', [])} | {b['material'] for b in ext.get('buildings', []) if b.get('material')}
    keys |= {p['covering'] for p in h.spec.get('roof', {}).get('planes', [])}
    for k in sorted(keys):
        m = M.mat(k)
        nodes = {n.type for n in m.node_tree.nodes}
        assert nodes <= {'BSDF_PRINCIPLED', 'OUTPUT_MATERIAL', 'TEX_IMAGE', 'NORMAL_MAP', 'SEPARATE_COLOR'}, (k, nodes)
    return len(keys)


def check_trim(h):
    diag = lambda a, b: abs(a[0] - b[0]) > 1e-6 and abs(a[1] - b[1]) > 1e-6
    def runs(rooms, z, cfg=None):
        out = mo.trim_runs(h, rooms, z, cfg)
        for r, closed in out:
            assert len(r) >= 2 and all(math.dist(a, b) > 0.01 for a, b in zip(r, r[1:])), (rooms, z, r)
        return out
    diags = lambda rs: sum(diag(a, b) for r, c in rs for a, b in zip(r, r[1:] + (r[:1] if c else [])))
    # living: the skirting follows the NW 45-degree wall and both bay splays (3 diagonals), cut once by the door
    sk = runs(('living',), 0.05)
    assert len(sk) == 1 and not sk[0][1] and diags(sk) == 3, (len(sk), diags(sk))
    co = runs(('living',), 2.92)                                # cornice: closed, bay corners square, NW wall diagonal
    assert len(co) == 1 and co[0][1] and diags(co) == 1, (len(co), diags(co))
    assert any(math.dist(p, (1.1, 0.99)) < 1e-6 for p in co[0][0]) and not any(math.dist(p, (1.1, 0.99)) < 1e-6 for p in sk[0][0])
    # hallway at Z 0.05: the first-floor wall w_green_rear (y 4.83..4.95) must not cut the hall in two
    lp = mo.room_loops(h, ('hallway',), 0.05)
    assert len(lp) == 1, len(lp)
    hk = runs(('hallway',), 0.05)
    ys = [p[1] for r, c in hk for p in r]
    assert min(ys) < 2.0 and max(ys) > 12.0 and not any(abs(p[1] - 4.83) < 0.02 or abs(p[1] - 4.95) < 0.02 for r, c in hk for p in r)
    assert not any(abs(a[0] - 0.15) < 1e-6 and abs(b[0] - 0.15) < 1e-6 and min(a[1], b[1]) < 7.5
                   for r, c in hk for a, b in zip(r, r[1:])), 'skirting on the open stair edge'
    # stairs (stairwell): the outline carries the diagonal; hallway + stairs is one loop
    assert diags([(l, True) for l in mo.room_loops(h, ('stairs',), 0.05)]) == 1
    assert len(mo.room_loops(h, ('hallway', 'stairs'), 2.92)) == 1
    # landing1_rear: the small chamfer at (0.35, 8.73)-(0.25, 8.83), open towards the quarter landing and the steps
    lr = runs(('landing1_rear',), 3.09)
    assert diags(lr) == 1 and len(lr) == 3, (diags(lr), len(lr))
    assert not any(abs(a[1] - 8.13) < 1e-6 and abs(b[1] - 8.13) < 1e-6 for r, c in lr for a, b in zip(r, r[1:]))
    # green bedroom at Z 3.47: two door gaps -> two runs, both bay splays followed (2 diagonals)
    gb = runs(('green_bedroom',), 3.47)
    assert len(gb) == 2 and diags(gb) == 2, (len(gb), diags(gb))
    gc = runs(('green_bedroom',), 6.24)
    assert len(gc) == 1 and gc[0][1] and diags(gc) == 0
    # every TRIM entry builds without error and names a known profile
    for room, cfg in mo.TRIM.items():
        for kind in ('skirting', 'dado', 'cornice'):
            e = cfg.get(kind) or []
            for c in ([e] if isinstance(e, dict) else e):
                assert c['profile'] in mo.PROFILES, (room, kind)


# ------------------------------------------------------------------------------------------------ slab + checks
def slab(h, oid, fr, col):
    """Wall slab round one opening: wall-local boxes (x along the wall, y the wall normal, z above z0)."""
    hw, z0s, top = fr['width'] / 2, fr['sill'], fr['top']
    t = fr['wall_thickness']
    W, zb, zt = hw + 0.75, -0.12, top + 0.75
    boxes = []

    def holed(y0, y1, x0, x1, za, zb_):
        boxes.extend([((-W, y0, zb), (x0, y1, zt)), ((x1, y0, zb), (W, y1, zt)), ((x0, y0, zb_), (x1, y1, zt)), ((x0, y0, zb), (x1, y1, za))])
    holed(fr['face_neg'], fr['face_pos'], -hw, hw, z0s, top)
    for sgn, face in ((1, fr['face_pos']), (-1, fr['face_neg'])):          # the wall in front of a reveal (recess)
        if abs(abs(face) - t / 2) > 1e-4:
            a, n, c = fr['along'], fr['normal'], fr['center']
            f = next((f for f in h.features if f['type'] == 'reveal' and f.get('level', 'G') == fr.get('level', 'G')
                      and min((p[0] - c.x) * a.x + (p[1] - c.y) * a.y for p in f['polygon']) < 0
                      < max((p[0] - c.x) * a.x + (p[1] - c.y) * a.y for p in f['polygon'])), None)
            xs = [(p[0] - c.x) * a.x + (p[1] - c.y) * a.y for p in f['polygon']] if f else [-hw, hw]
            fz = [v - fr['z0'] for v in f['z']] if f else [z0s, top]
            y0, y1 = sorted((face, sgn * t / 2))
            holed(y0, y1, min(xs), max(xs), fz[0], fz[1])
    Mw = J.base_frame(fr)
    mb = mo.MB().at(Mw)
    for a, b in boxes:
        if all(b[i] - a[i] > 1e-4 for i in range(3)):
            mb.box(a, b, M.paint('#D9D4C8'))
    mb.box((-W, -2.6, zb - 0.02), (W, 2.6, zb + 0.119), M.paint('#8C8478'))     # floor both sides (top at z0 - 1 mm)
    ob = mb.finish(f'slab.{oid}')
    col.objects.link(ob)
    return Mw, [bx for bx in boxes if all(bx[1][i] - bx[0][i] > 1e-4 for i in range(3))]


def world_verts(o):
    return [o.matrix_world @ v.co for v in o.data.vertices]


def check_opening(h, oid, fr, objs, Mw, boxes, pose):
    o = h.openings[oid]
    assert objs, f'{oid}: nothing built'
    rooms = {h.tag_room(r) for r in o['connects'] if r != 'outside' and h.kind(r) != 'exterior'} | \
            {h.tag_room(r) for r in (fr['room_pos'], fr['room_neg']) if r in h.rooms}
    for ob in objs:
        assert ob['kind'] == 'joinery' and ob['room'] in rooms, f"{ob.name}: room {ob['room']!r} not in {rooms}"
        assert ob.name.startswith(ob['room'] + '.'), ob.name
        assert ob['level'] == h.level(ob['room']), ob.name
    moving = [ob for ob in objs if 'ix' in ob.keys()]
    kinds = {json.loads(ob['ix'])['t'] for ob in moving}
    if o['type'] in ('door', 'double_door', 'french_door'):
        tags = [json.loads(ob['ix']) for ob in moving if '.leaf' in ob.name and not ob.name.endswith('.glass')]
        assert tags and all(d.get('blocks') == oid for d in tags), f'{oid}: door leaves must carry blocks'
        assert len(tags) == (1 if o['type'] == 'door' else 2), f'{oid}: {len(tags)} leaves'
    if o['type'] == 'hatch':
        assert len({json.loads(ob['ix'])['g'] for ob in moving}) == 2 and kinds == {'hinge'}
    n_open = sum(1 for s in (o.get('sashes') or J.SHED_WINDOWS.get(oid, {}).get('sashes') or [])
                 if s.get('type', 'fixed') != 'fixed' and s.get('operated', True))
    if o['type'] == 'window' and o.get('style') != 'dark_timber_white_upvc_shutters':
        groups = {json.loads(ob['ix'])['g'] for ob in moving}
        assert (len(groups) >= n_open) and (bool(groups) == bool(n_open)), f'{oid}: {len(groups)} sash groups for {n_open} opening sashes'
    if fr.get('exterior') and o.get('style') not in ('dark_timber_white_upvc_shutters',) and \
            (o.get('surround') or {}).get(J._inside(fr)[0]) != 'flat_white_surround':
        # the outside of the fixed frame sits ext_reveal behind the outer face
        inv, out_y = Mw.inverted(), fr['face_out']
        fo = [ob for ob in objs if ob.name.endswith('.frame')]
        ys = [(inv @ v).y for ob in fo for v in world_verts(ob)]
        got = (out_y - max(ys)) if out_y > 0 else (min(ys) - out_y)
        assert abs(got - fr['ext_reveal']) < 0.004, f"{oid}: frame {got:.3f} behind the outer face, ext_reveal {fr['ext_reveal']}"
    if pose:
        IX.pose(moving, 1)
        bpy.context.view_layer.update()
        inv = Mw.inverted()
        for ob in moving:
            d = json.loads(ob['ix'])
            if d['t'] not in ('hinge',):
                continue
            bad = 0
            for v in world_verts(ob):
                q = inv @ v
                bad += any(all(a[i] + 0.004 < q[i] < b[i] - 0.004 for i in range(3)) for a, b in boxes)
            assert bad == 0, f'{ob.name}: {bad} vertices inside the wall in state 1'
    return len(moving)


# ------------------------------------------------------------------------------------------------ render
def setup_render(res, samples):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    c = sc.cycles
    c.samples, c.use_denoising = samples, True
    prefs = bpy.context.preferences.addons['cycles'].preferences
    for t in ('OPTIX', 'CUDA'):
        try:
            prefs.compute_device_type = t
            prefs.get_devices()
            for d in prefs.devices:
                d.use = d.type != 'CPU'
            if any(d.use for d in prefs.devices):
                c.device = 'GPU'
                break
        except Exception:
            continue
    sc.render.resolution_x, sc.render.resolution_y = (int(v) for v in res.split('x'))
    sc.render.image_settings.file_format = 'JPEG'
    sc.render.image_settings.quality = 85
    sc.view_settings.view_transform = 'AgX'
    w = bpy.data.worlds.new('w')
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs['Color'].default_value, bg.inputs['Strength'].default_value = (0.75, 0.80, 0.9, 1), 0.9
    sc.world = w
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam'))
    cam.data.sensor_fit, cam.data.angle = 'VERTICAL', math.radians(58)
    sc.collection.objects.link(cam)
    sc.camera = cam
    sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN'))
    sun.data.energy, sun.data.angle = 2.5, math.radians(3)
    sc.collection.objects.link(sun)
    return cam, sun


def shoot(cam, sun, Mw, fr, side, path):
    top = fr['top'] + (0.7 if fr['type'] == 'door' else 0.0)       # room for a doorcase over the head
    zc = (max(fr['sill'], 0.0) + top) / 2
    span = max(fr['width'] + 0.9, (top - min(fr['sill'], 0.3)) * 0.82 + 0.5)
    dist = span / (2 * math.tan(math.radians(58) / 2) * 0.75) + 0.3
    pos = Mw @ Vector((0.55 * side, side * dist, min(zc + 0.25, 1.65 if top > 1.9 else zc + 0.4)))
    look = Mw @ Vector((0, 0, zc))
    cam.location = pos
    cam.rotation_euler = (look - pos).to_track_quat('-Z', 'Y').to_euler()
    sp = Mw @ Vector((-1.5 * side, side * 2.5, zc + 2.5))
    sun.rotation_euler = (look - sp).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


def main():
    a = args()
    for o in list(bpy.data.objects):                            # factory startup: cube, light, camera
        bpy.data.objects.remove(o)
    h = C.House.load(a.house)
    h.errors = []
    assert J.validate(h) == [], J.validate(h)
    n_mat = check_materials(h)
    if h.schema == 2:                                           # the run counts are those of the phase-2 geometry
        check_trim(h)
    for room in mo.TRIM:                                        # every room's trim builds (objects are dropped again)
        for ob in mo.install_room_trim(h, room):
            bpy.data.objects.remove(ob)
    print(f'[test] validate ok, {n_mat} material keys resolve, trim runs ok')
    only = [s for s in a.only.split(',') if s]
    ids = [oid for oid, o in h.openings.items() if o.get('style') and o['type'] not in J.NO_JOINERY and (not only or oid in only)]
    os.makedirs(a.out, exist_ok=True)
    cam = sun = None
    if a.render:
        cam, sun = setup_render(a.res, a.samples)
    report, cols = {}, {}
    for oid in ids:
        fr = h.opening_frame(oid)
        col = bpy.data.collections.new('t.' + oid)
        bpy.context.scene.collection.children.link(col)
        Mw, boxes = slab(h, oid, fr, col)
        before = set(bpy.data.objects)
        J.build_opening(h, oid)
        objs = [o for o in bpy.data.objects if o not in before]
        for o in objs:                                          # one collection per opening, so renders can isolate it
            for c in list(o.users_collection):
                c.objects.unlink(o)
            col.objects.link(o)
        bpy.context.view_layer.update()
        moving = check_opening(h, oid, fr, objs, Mw, boxes, a.pose)
        report[oid] = dict(objects=len(objs), tagged=moving, tris=mo.tri_count(objs))
        cols[oid] = (col, Mw, fr)
    print('[test] ' + ', '.join(f"{k}: {v['objects']} obj / {v['tagged']} ix / {v['tris']} tris" for k, v in report.items()))
    print(f"[test] joinery total {sum(v['tris'] for v in report.values())} triangles in {len(ids)} openings")
    if a.render:
        tag = ('_' + a.tag) if a.tag else ''
        for oid, (col, Mw, fr) in cols.items():
            for other, (c2, _, _) in cols.items():
                c2.hide_render = other != oid
            inside = J._inside(fr)[1]                           # +1 / -1: side of the inside room (pos room for internal walls)
            for name, side in (('in', inside), ('out', -inside)):
                shoot(cam, sun, Mw, fr, side, os.path.join(a.out, f'{oid}_{name}{tag}.jpg'))
    print('JOINERY OK')


try:
    main()
except Exception:
    traceback.print_exc()
    sys.exit(1)

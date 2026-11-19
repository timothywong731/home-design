"""Builds the site alone (blender/MULTILEVEL.md section 6) on the fixture, asserts its acceptance checks and renders
previews for comparison with spec/rooms/{garden,front,shed}.md.

    blender -b --factory-startup --python blender/test_site.py -- [--house spec/house.json]
            [--out build/site] [--res 540x960] [--samples 64] [--cams a,b|none] [--pose 0|1] [--save FILE.blend]
Prints SITE OK; exits 1 on any failure. The grey house is a stand-in drawn by this test, not part of the site.
"""
import argparse
import json
import math
import sys
import traceback
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lib import ctx as C                                    # noqa: E402
from lib import interact as IX                              # noqa: E402
from lib import site                                        # noqa: E402

SITE_ROOMS = ('front', 'side_passage', 'garden', 'shed', 'neighbours')
SUN_DIR = (-0.429, 0.807, -0.407)                           # contract section 9: the way the light travels
# name, position, look-at, field of view (longer side), matching reference still
CAMS = [
    ('garden_out', (1.2, 17.7, 1.55), (1.6, 23.5, 0.6), 100, 'v2:f_0189'),
    ('house_back', (1.9, 24.3, 1.5), (1.4, 17.4, 1.7), 100, 'v2:f_0251'),
    ('shed_front', (2.6, 21.6, 1.55), (2.6, 25.0, 1.0), 100, 'v2:f_0189'),
    ('veranda', (3.7, 24.3, 1.5), (-0.4, 24.2, 1.1), 100, 'v2:f_0257'),
    ('workshop', (3.3, 25.7, 1.2), (0.6, 28.2, 0.6), 100, 'v2:f_0283'),
    ('step', (4.0, 19.0, 0.45), (4.0, 16.8, -0.3), 90, 'v2:f_0233'),
    ('passage', (3.95, 16.4, 1.6), (4.3, 9.5, 0.7), 100, 'v2:f_0319'),
    ('gate', (3.75, 11.0, 1.5), (4.55, 9.3, 0.6), 100, 'v2:f_0343'),
    ('alley', (4.95, 3.0, 1.6), (4.8, 9.6, 0.8), 90, None),
    ('front_wall', (-0.2, -0.9, 1.4), (-0.75, -5.0, 0.2), 100, 'v2:f_0949'),
    ('street', (2.2, -11.5, 1.6), (2.0, 0.0, 1.8), 90, None),
    ('above', (2.0, 17.6, 8.0), (1.6, 22.6, -0.4), 100, 'v4:f_0467'),
]


def parse():
    ap = argparse.ArgumentParser(prog='test_site.py')
    ap.add_argument('--house', default=str(HERE.parent / 'spec' / 'house.json'))
    ap.add_argument('--out', default=str(HERE.parent / 'build' / 'site'))
    ap.add_argument('--res', default='540x960')
    ap.add_argument('--samples', type=int, default=64)
    ap.add_argument('--cams', default='')
    ap.add_argument('--pose', type=int, default=0, choices=(0, 1))
    ap.add_argument('--save', default='')
    a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    a.res = tuple(int(v) for v in a.res.lower().split('x'))
    return a


def bvh(objs, mat=None):
    """One BVH over the world-space polygons of objs (mat: per-object matrix override)."""
    vs, ps = [], []
    for o in objs:
        m, n = (mat or {}).get(o.name, o.matrix_world), len(vs)
        vs += [m @ v.co for v in o.data.vertices]
        ps += [[n + i for i in p.vertices] for p in o.data.polygons]
    return BVHTree.FromPolygons(vs, ps)


def edge_dist(x, y, polys):
    return min(site.edge_dist(x, y, p) for p in polys)


def grid(x0, y0, x1, y1, step):
    nx, ny = int((x1 - x0) / step), int((y1 - y0) / step)
    return ((x0 + (i + 0.37) * step, y0 + (j + 0.37) * step) for i in range(nx) for j in range(ny))


def check(ctx, objs):
    ext = ctx.spec['exterior']
    by = {o.name: o for o in objs}
    house = site._house_polys(ctx)
    env = house[:len(house) - len(ext.get('buildings', []))]         # the ground-floor envelope alone
    plot = ext['plot']['polygon']
    treads = [[tuple(p) for p in t['polygon']] for s in ext['steps'] for t in s.get('treads', [])]
    zpolys = [[tuple(p) for p in z['polygon']] for z in ctx.zones.values()]

    # tags and names
    assert len(by) == len(objs), 'duplicate names'
    for o in objs:
        assert o['room'] in SITE_ROOMS and o['level'] == 'X' and o.name.startswith(o['room'] + '.'), o.name
        assert o.data.uv_layers and len(o.data.polygons), o.name
    shed = [o.name for o in objs if o['room'] == 'shed']
    for n in ('shed.shed_veranda', 'shed.walls', 'shed.roof', 'shed.soffit', 'shed.workshop.walls', 'shed.workshop.floor',
              'shed.workshop.ceiling', 'shed.store.walls', 'shed.heads', 'shed.fascia'):
        assert n in shed, f'missing {n}'
    assert all(o['room'] == 'shed' for o in objs if o.name.startswith('shed.'))
    assert by['neighbours.backdrop'].get('no_export') == 1 and not site.MISSING, site.MISSING

    # every zone top within 1 mm of ctx.zone_z at its polygon vertices
    for zid, z in ctx.zones.items():
        ob = site.surface(zid)
        assert ob.name == f"{z['room']}.{zid}" and ob['kind'] == 'shell' and ob['lm'] == 'static'
        for x, y in z['polygon']:
            top = max(v.co.z for v in ob.data.vertices if abs(v.co.x - x) < 1e-4 and abs(v.co.y - y) < 1e-4)
            assert abs(top - ctx.zone_z(zid, x, y)) < 1e-3, (zid, x, y, top)

    # the ground seen from above is ctx.ground_z everywhere (falls, overlays, treads), 5 cm grid
    ground = bvh([site.surface(z) for z in ctx.zones] + [o for o in objs if o.name.endswith('_steps')])
    bx0, by0, bx1, by1 = site._bbox([p for poly in zpolys for p in poly])
    n = 0
    for x, y in grid(bx0, by0, bx1, by1, 0.05):
        want = ctx.ground_z(x, y)
        if want is None or edge_dist(x, y, zpolys + treads) < 0.02:
            continue
        hit = ground.ray_cast(Vector((x, y, 5)), Vector((0, 0, -1)))[0]
        assert hit is not None and abs(hit.z - want) < 1e-3, f'ground at ({x:.2f}, {y:.2f}): {hit} != {want}'
        n += 1
    print(f'[test] ground matches ctx.ground_z at {n} points')

    # no holes: every point of the plot outside the house looks down on something of the site, not on the backdrop
    solid = bvh([o for o in objs if o.name != 'neighbours.backdrop'])
    px0, py0, px1, py1 = site._bbox(plot)
    holes = [(round(x, 2), round(y, 2)) for x, y in grid(px0, py0, px1, py1, 0.04)
             if C.point_in_poly(x, y, plot) and not any(C.poly_contains(x, y, h, 1e-3) for h in house)
             and solid.ray_cast(Vector((x, y, 20)), Vector((0, 0, -1)))[0] is None]
    assert not holes, f'{len(holes)} holes in the ground, e.g. {holes[:5]}'
    # ... and the ground runs right up to the house: 5 mm outside every envelope edge there is a zone surface
    n = 0
    for h in ext['envelope']['blocks']:
        for lv in (lv for lv in h['levels'] if lv['level'] == 'G'):
            poly = site._ccw(lv['polygon'])
            for a, b in zip(poly, poly[1:] + poly[:1]):
                (u, ln) = site._dir(a, b)
                for i in range(int(ln / 0.1)):
                    x, y = a[0] + u[0] * (i + 0.5) * 0.1 + u[1] * 0.005, a[1] + u[1] * (i + 0.5) * 0.1 - u[0] * 0.005
                    if not C.point_in_poly(x, y, plot) or any(C.point_in_poly(x, y, q) for q in house):
                        continue
                    hit = ground.ray_cast(Vector((x, y, 5)), Vector((0, 0, -1)))[0]
                    assert hit is not None and hit.z > -0.5, f'no ground against the house at ({x:.2f}, {y:.2f})'
                    n += 1
    print(f'[test] no holes; ground touches the envelope at {n} points')

    # nothing of the site stands inside the house footprint
    for o in objs:
        if o.name == 'neighbours.backdrop':
            continue
        bad = [tuple(round(c, 3) for c in v.co) for v in o.data.vertices for lv in env
               if C.point_in_poly(v.co.x, v.co.y, lv) and edge_dist(v.co.x, v.co.y, [[tuple(p) for p in lv]]) > 0.002]
        assert not bad, f'{o.name} inside the envelope: {bad[:3]}'

    # shed openings are cut: a ray through each hole is free, a ray beside it hits the wall
    for oid in ctx.exterior_openings('X'):
        fr = ctx.opening_frame(oid)
        c, al, out, t = fr['center'], fr['along'], fr['outward'], fr['wall_thickness']
        zc = c.z + (fr['z0'] + fr['top'] - c.z) / 2
        def ray(off):
            o = Vector((c.x + al[0] * off + out[0] * (t / 2 + 0.25), c.y + al[1] * off + out[1] * (t / 2 + 0.25), zc))
            return solid.ray_cast(o, Vector((-out[0], -out[1], 0)), t + 0.3)[0]
        assert ray(0.0) is None, f'{oid}: the hole is blocked'
        assert any(ray(sg * (fr['width'] / 2 + 0.06)) for sg in (1, -1)), f'{oid}: no wall beside the hole'

    # side gate: tagged, leaf bottom 20 mm over the tread, both poses clear of everything
    g = next(b for b in ext['boundaries'] if b['type'] == 'gate')
    leaf = by[f"{g['room']}.{g['id']}"]
    ix = json.loads(leaf['ix'])
    assert ix['t'] == 'hinge' and ix['blocks'] == g['id'] and abs(ix['deg']) == 50 and ix['a'] == [0, 0, 1], ix
    assert abs(min(v.co.z for v in leaf.data.vertices) - (-0.14)) < 1e-6, 'leaf bottom is not at Z -0.14'
    others = bvh([o for o in objs if o is not leaf])
    assert not bvh([leaf]).overlap(others), 'closed gate leaf intersects something'
    keep = leaf.matrix_world.copy()
    IX.pose([leaf], 1)
    hits = bvh([leaf], {leaf.name: leaf.matrix_world}).overlap(others)
    tip = leaf.matrix_world @ Vector(max((v.co for v in leaf.data.vertices), key=lambda p: (p - Vector(ix['p'])).length))
    leaf.matrix_world = keep
    assert not hits, f'open gate leaf intersects something ({len(hits)} pairs)'
    assert C.poly_contains(tip.x, tip.y, ctx.zones[g['swingInto']]['polygon']), f'gate opens the wrong way: tip {tip}'

    # budget
    tris = {}
    for o in objs:
        k = (o['room'], o['kind'])
        tris[k] = tris.get(k, 0) + sum(len(p.vertices) - 2 for p in o.data.polygons)
    for k in sorted(tris):
        print(f'[test] triangles {k[0]:13s} {k[1]:8s} {tris[k]:6d}')
    total = sum(tris.values())
    assert total <= 100_000, f'{total} triangles > 100 k'
    print(f'[test] triangles total {total} / 100000')


def standin(ctx):
    """Plain boxes for the house so the previews have its bulk and its shadow."""
    col = bpy.data.collections.new('standin')
    bpy.context.scene.collection.children.link(col)
    for bl in ctx.spec['exterior']['envelope']['blocks']:
        for lv in bl['levels']:
            if lv.get('below_ground'):
                continue
            m = site._Mesh()
            m.prism(lv['polygon'], lv['z'][0] - (0.35 if lv['level'] == 'G' else 0), lv['z'][1], '#D2C596')
            me = bpy.data.meshes.new(f"standin.{bl['id']}.{lv['level']}")
            me.from_pydata(m.v, [], m.f)
            me.materials.append(site._mat('#D2C596'))
            col.objects.link(bpy.data.objects.new(me.name, me))


def light(samples, res):
    """Sun + plain sky stub (the real sky is core's lighting.py)."""
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.samples, sc.cycles.use_denoising, sc.cycles.max_bounces = samples, True, 6
    prefs = bpy.context.preferences.addons['cycles'].preferences
    for t in ('OPTIX', 'CUDA'):
        try:
            prefs.compute_device_type = t
            prefs.get_devices()
            for d in prefs.devices:
                d.use = d.type != 'CPU'
            if any(d.use for d in prefs.devices):
                sc.cycles.device = 'GPU'
                break
        except Exception:
            continue
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = *res, 100
    sc.render.image_settings.file_format, sc.render.image_settings.quality = 'JPEG', 88
    sc.view_settings.view_transform = 'AgX'
    w = bpy.data.worlds.new('sky')
    sc.world = w
    w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs['Color'].default_value, bg.inputs['Strength'].default_value = (0.75, 0.84, 1.0, 1), 1.6
    sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN'))
    sun.data.energy, sun.data.angle = 2.2, math.radians(3)
    sun.rotation_euler = Vector(SUN_DIR).to_track_quat('-Z', 'Y').to_euler()
    sc.collection.objects.link(sun)


def render(a, tag=''):
    sc = bpy.context.scene
    want = [c for c in a.cams.split(',') if c]
    for name, pos, look, fov, ref in CAMS:
        if want and name not in want:
            continue
        cam = bpy.data.cameras.new(name)
        cam.sensor_fit, cam.angle, cam.clip_start = 'AUTO', math.radians(fov), 0.03
        ob = bpy.data.objects.new('cam.' + name, cam)
        ob.location = pos
        ob.rotation_euler = (Vector(look) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
        sc.collection.objects.link(ob)
        sc.camera = ob
        sc.render.filepath = str(Path(a.out) / f'{name}{tag}.jpg')
        bpy.ops.render.render(write_still=True)
        print(f'[test] wrote {sc.render.filepath}  (ref {ref})')
    if not want or 'top' in want:                           # plan view, 1 px = 4 cm
        cam = bpy.data.cameras.new('top')
        cam.type, cam.ortho_scale = 'ORTHO', 38.4
        ob = bpy.data.objects.new('cam.top', cam)
        ob.location = (2.3, 11.0, 30)
        sc.collection.objects.link(ob)
        sc.camera = ob
        sc.render.resolution_x, sc.render.resolution_y = 400, 960
        for o in bpy.data.objects:                          # look into the shed and past the neighbours
            o.hide_render = o.name in ('shed.roof', 'shed.soffit', 'shed.workshop.ceiling', 'shed.store.ceiling',
                                       'shed.roof.kerb', 'shed.fascia') or o.name.startswith('standin')
        sc.render.filepath = str(Path(a.out) / f'top{tag}.jpg')
        bpy.ops.render.render(write_still=True)
        print(f'[test] wrote {sc.render.filepath}  (ref spec/plan_site.png)')


def main():
    a = parse()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ctx = C.House.load(a.house)
    objs = site.build(ctx)
    bpy.context.view_layer.update()
    check(ctx, objs)
    if a.cams != 'none':
        standin(ctx)
        light(a.samples, a.res)
        if a.pose:
            bpy.context.view_layer.update()
            IX.pose([o for o in objs if 'ix' in o.keys()], 1)
        render(a, '_open' if a.pose else '')
    if a.save:
        bpy.ops.wm.save_as_mainfile(filepath=str(Path(a.save).resolve()))
    print('SITE OK')


try:
    main()
except Exception:
    traceback.print_exc()
    sys.exit(1)

"""Envelope alone (MULTILEVEL.md section 12c): skin + roof + balcony from the fixture, asserts, then orthographic
front / rear / flank / roof-plan renders and a few eye-level views next to the reference stills.

blender -b --factory-startup --python blender/test_envelope.py -- [--house spec/house.json]
        [--out build/envelope] [--res 720] [--samples 48] [--no-render] [--only front,rear,...] [--with-site]
Prints ENVELOPE OK. Dark stand-in boxes fill the room volumes in the renders (no shell is built here)."""
import argparse
import json
import math
import sys
import time
from pathlib import Path

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lib import ctx as C                    # noqa: E402
from lib import envelope as E               # noqa: E402
from lib import materials as M              # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('--house', default=str(HERE.parent / 'spec' / 'house.json'))
ap.add_argument('--out', default=str(HERE.parent / 'build' / 'envelope'))
ap.add_argument('--res', type=int, default=720)
ap.add_argument('--samples', type=int, default=48)
ap.add_argument('--no-render', action='store_true')
ap.add_argument('--only', default='')
ap.add_argument('--with-site', action='store_true', help='renders only: also build lib/site.py (if it works)')
A = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
A.out = str(Path(A.out).resolve())          # Blender resolves a relative render path against the drive root

bpy.ops.wm.read_factory_settings(use_empty=True)
h = C.House.load(A.house)
t0 = time.time()
objs = E.build(h)
print(f'[test] build {time.time() - t0:.1f} s')
bpy.context.view_layer.update()
fails = []


def check(ok, msg):
    if not ok:
        fails.append(msg)
        print('[test] FAIL', msg)


def tree(sel):
    """BVH over the selected objects (their vertices are world coordinates) + the owner of every polygon."""
    vs, ps, own = [], [], []
    for o in sel:
        n = len(vs)
        vs += [v.co.copy() for v in o.data.vertices]
        ps += [[n + i for i in p.vertices] for p in o.data.polygons]
        own += [o] * len(o.data.polygons)
    return BVHTree.FromPolygons(vs, ps), own


# ---- tags, names, budget
names = [o.name for o in objs]
check(len(set(names)) == len(names), 'object names are not unique')
for o in objs:
    check(o['room'] in ('facade', 'roof', 'balcony') and o['level'] == h.level(o['room']) and
          o.name.split('.')[0] == o['room'], f'{o.name}: room / level / name prefix')
tris = sum(len(p.vertices) - 2 for o in objs if o['room'] in ('facade', 'roof') for p in o.data.polygons)
check(tris <= 150_000, f'facade + roof {tris} triangles > 150 k')
print(f'[test] {len(objs)} objects, facade + roof {tris} triangles')

vols = E._vols(h)
ops = {o['id']: o for o in E._ext_openings(h)}
skin = [o for o in objs if o['room'] == 'facade' and o['kind'] == 'shell']
slabs = [bpy.data.objects['roof.' + p['id']] for p in h.spec['roof']['planes']]
wins = [f for f in h.features if f['type'] in ('roof_window', 'roof_opening')]
in_win = lambda x, y: any(C.poly_contains(x, y, f['polygon'], 0.02) for f in wins)
footprint = lambda x, y: any(C.point_in_poly(x, y, v['poly']) for v in vols)

# ---- 1. holes line up with the opening list of each facade
bvh, _ = tree(skin)
n_holes = 0
for f in h.spec['exterior']['facades']:
    (ax, ay), (bx, by) = E._facade_line(f)
    for oid in f['openings']:
        o = ops[oid]
        fr = o['fr']
        al, out = Vector((fr['along'][0], fr['along'][1], 0)), Vector((fr['outward'][0], fr['outward'][1], 0))
        check(E._seg_dist(o['p0'], (ax, ay), (bx, by)) < 1e-3 and (out.x, out.y) == E._facade_n(f),
              f'{oid}: outer face is not on facade {f["id"]}')
        w, zc = fr['width'] / 2, (o['z0'] + o['z1']) / 2
        probes = [(0, zc, False)]
        for d, solid in ((-0.03, False), (0.03, True)):          # just inside / just outside each edge of the hole
            probes += [(-w - d, zc, solid), (w + d, zc, solid), (0, o['z0'] - d, solid), (0, o['z1'] + d, solid)]
        for s, z, solid in probes:
            p = Vector((o['p0'][0], o['p0'][1], z)) + al * s
            if E._seg_dist((p.x, p.y), (ax, ay), (bx, by)) > 1e-6:       # past the end of the wall
                continue
            hit = bvh.ray_cast(p + out, -out)
            at_face = hit[0] is not None and abs(hit[3] - 1.0) < 2e-3
            check(at_face == solid, f'{oid}: skin {"missing" if solid else "present"} at s {s:+.3f} z {z:.3f}')
        n_holes += 1
print(f'[test] holes checked: {n_holes}')

# ---- 2. from above: the first hit is the roof (or a pipe / kneeler standing above it), never anything under it,
#         and the slabs lie on the upper envelope of the planes (valleys)
allbvh, allown = tree(objs)
slabbvh, _ = tree(slabs)
xs = [q[0] for p in h.spec['roof']['planes'] for q in p['polygon']]
ys = [q[1] for p in h.spec['roof']['planes'] for q in p['polygon']]
n_top = 0
for i in range(int((max(xs) - min(xs)) / 0.1) + 1):
    for j in range(int((max(ys) - min(ys)) / 0.1) + 1):
        x, y = min(xs) + 0.033 + 0.1 * i, min(ys) + 0.033 + 0.1 * j
        rz = max((z for z in (h.roof_z(x, y), h.roof_z(x, y, True)) if z is not None), default=None)
        hit = allbvh.ray_cast(Vector((x, y, 15)), Vector((0, 0, -1)))
        if rz is None:
            continue
        n_top += 1
        if hit[0] is None or allown[hit[2]]['room'] not in ('roof', 'facade') or hit[0].z < rz - 2e-3:
            check(False, f'from above at ({x:.2f}, {y:.2f}): {allown[hit[2]].name if hit[0] else None} '
                         f'z {hit[0].z if hit[0] else None} (roof {rz:.3f})')
        if not in_win(x, y):
            s = slabbvh.ray_cast(Vector((x, y, 15)), Vector((0, 0, -1)))
            check(s[0] is not None and abs(s[0].z - rz) < 2e-3, f'roof surface at ({x:.2f}, {y:.2f}): '
                  f'{s[0].z if s[0] else None} != {rz:.3f}')
print(f'[test] roof points from above: {n_top}')

# ---- 3. slab undersides: pitched 0.30, flat 0.24
n_under = {}
for p in h.spec['roof']['planes']:
    if p.get('level') == 'G':
        continue
    t = h.roof_slab_t(p['id'])
    check(abs(t - (0.30 if p['z']['cx'] or p['z']['cy'] else 0.24)) < 1e-6, f'{p["id"]}: slab {t}')
    px, py = [q[0] for q in p['polygon']], [q[1] for q in p['polygon']]
    for i in range(int((max(px) - min(px)) / 0.2)):
        for j in range(int((max(py) - min(py)) / 0.2)):
            x, y = min(px) + 0.07 + 0.2 * i, min(py) + 0.07 + 0.2 * j
            if h.roof_plane(x, y) != p['id'] or in_win(x, y):
                continue
            under = h.roof_z(x, y) - t
            zf = E._floor_under(vols, x, y, under)
            if zf is not None and under < zf + 0.02:
                continue
            hit = slabbvh.ray_cast(Vector((x, y, under - 0.3)), Vector((0, 0, 1)))
            check(hit[0] is not None and abs(hit[0].z - under) < 2e-3,
                  f'{p["id"]} underside at ({x:.2f}, {y:.2f}): {hit[0].z if hit[0] else None} != {under:.3f}')
            n_under[p['id']] = n_under.get(p['id'], 0) + 1
print(f'[test] underside points: {n_under}')
check(len(n_under) == sum(1 for p in h.spec['roof']['planes'] if p.get('level') != 'G'), 'a plane has no underside')

# ---- 4. no skin above the roof surface
for o in skin:
    for v in o.data.vertices:
        top = E._top(h, v.co.x, v.co.y, False, 1e-4) or E._top(h, v.co.x, v.co.y, True, 0.03)
        if top is None or v.co.z > top[0] + 2e-3:
            check(False, f'{o.name}: vertex {tuple(round(c, 3) for c in v.co)} above the roof {top and round(top[0], 3)}')
            break

# ---- 5. nothing of the envelope inside a room (between its floor and its ceiling)
#         Exempt, with a WARNING: an under_roof room that reaches under two roof planes of different height has the
#         step between them (a spec matter: eaves_rear runs 0.10 m under the stair dormer).
rooms = [(rid, h.room_poly(rid)) for rid in h.rooms if h.kind(rid) != 'exterior']
step_line = lambda x, y: len({h.roof_plane(x + dx, y + dy) for dx in (-0.003, 0.003) for dy in (-0.003, 0.003)}) > 1
for o in objs:
    bad, known = 0, 0
    for v in o.data.vertices:
        x, y, z = v.co
        for rid, poly in rooms:
            if C.point_in_poly(x, y, poly) and not E._on_edge((x, y), poly, 0.003):
                cz = h.ceil_z(rid, x, y)
                if cz is not None and h.floor_z(rid) + 0.003 < z < cz - 0.003:
                    if (h.rooms[rid].get('ceiling') or {}).get('type') == 'under_roof' and step_line(x, y):
                        known += 1
                        continue
                    bad += 1
                    where = (rid, round(x, 3), round(y, 3), round(z, 3), round(cz, 3))
    check(not bad, f'{o.name}: {bad} vertices inside a room, e.g. {where if bad else None}')
    if known:
        print(f'[test] WARNING {o.name}: {known} vertices on a roof step inside an under_roof room')

# ---- 6. horizontal rays from the four sides, Z 0..9.2: whatever passes through the house hits skin or roof first
cache = {}


def column(x, y):
    """Z intervals certainly inside the house at (x, y): envelope prisms, 5 cm in from every face and the roof."""
    k = (round(x / 0.05), round(y / 0.05))
    if k not in cache:
        iv = []
        ru = h.roof_under(x, y)
        for v in vols:
            if C.point_in_poly(x, y, v['poly']) and not E._on_edge((x, y), v['poly'], 0.05):
                hi = v['z1'] if ru is None else min(v['z1'], ru)
                if v['level'] == 'G' and ru is None and h.roof_under(x, y, True) is not None:
                    hi = min(hi, h.roof_under(x, y, True))
                iv.append((v['z0'] + 0.05, hi - 0.05))
        cache[k] = iv
    return cache[k]


nbs = [([tuple(p) for p in q['polygon']], q['z'][1]) for q in h.spec['exterior']['neighbours']]
hbvh, hown = tree([o for o in objs if o['room'] in ('facade', 'roof')])        # the balcony stands in front
B = h.spec['bounds']
n_side, n_miss = 0, 0
for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
    lo, hi = (B['minY'], B['maxY']) if d[0] else (B['minX'], B['maxX'])
    span = (B['maxX'] - B['minX']) if d[0] else (B['maxY'] - B['minY'])
    for i in range(int((hi - lo) / 0.3)):
        c = lo + 0.13 + 0.3 * i
        for k in range(31):
            z = 0.1 + 0.3 * k
            start = Vector((B['minX'] - 2 if d[0] > 0 else B['maxX'] + 2, c, z)) if d[0] else \
                Vector((c, B['minY'] - 2 if d[1] > 0 else B['maxY'] + 2, z))
            entry = None
            for s in range(int((span + 4) / 0.05)):
                q = start + Vector((d[0], d[1], 0)) * (0.05 * s)
                if any(a <= z <= b for a, b in column(q.x, q.y)):
                    entry = 0.05 * s
                    break
            if entry is None:
                continue
            dv = Vector((d[0], d[1], 0))
            first = next(s for s in range(int((span + 4) / 0.05)) if footprint(*(start + dv * (0.05 * s)).xy))
            q = start + dv * (0.05 * first - 0.2)
            if any(C.point_in_poly(q.x, q.y, poly) and z < top for poly, top in nbs):
                continue                                         # party wall below the neighbour's roof: no skin
            q = start + dv * entry
            if any(abs((q.x - o['p0'][0]) * o['fr']['along'][0] + (q.y - o['p0'][1]) * o['fr']['along'][1]) < o['fr']['width'] / 2 + 0.02
                   and abs((q.x - o['p0'][0]) * o['fr']['outward'][0] + (q.y - o['p0'][1]) * o['fr']['outward'][1]) < 0.7
                   and (q.x - start.x) * o['fr']['outward'][0] + (q.y - start.y) * o['fr']['outward'][1] < 0
                   and o['z0'] - 0.02 < z < o['z1'] + 0.02 for o in ops.values()):
                continue                                         # through a window or door hole
            n_side += 1
            hit = hbvh.ray_cast(start, dv)
            if hit[0] is None or hit[3] > entry + 0.01:
                n_miss += 1
                if n_miss <= 12:
                    print(f'[test] side ray dir {d} at {c:.2f}, z {z:.2f}: enters at {entry:.2f}, hit '
                          f'{hown[hit[2]].name if hit[0] else None} at {hit[3] if hit[0] else None}')
check(n_miss == 0, f'{n_miss} of {n_side} horizontal rays reach the house without hitting skin or roof')
print(f'[test] side rays through the house: {n_side}')

# ---- 7. the roof window opens outward (state 1 clears the roof)
for o in objs:
    if 'ix' in o.keys():
        ix = json.loads(o['ix'])
        R = Matrix.Translation(Vector(ix['p'])) @ Matrix.Rotation(math.radians(ix['deg']), 4, Vector(ix['a'])) @ \
            Matrix.Translation(-Vector(ix['p']))
        low = min((R @ v.co).z - h.roof_z(*(R @ v.co).xy) for v in o.data.vertices if h.roof_z(*(R @ v.co).xy))
        check(low > -0.03, f'{o.name}: state 1 dips {low:.3f} under the roof')
        print(f'[test] {o.name}: ix {o["ix"]}, state 1 lowest point {low:+.3f} above the roof')
check(any('ix' in o.keys() for o in objs), 'no roof window sash is tagged')
check(abs(E.roof_surface(1.0, 3.0) - h.roof_z(1.0, 3.0)) < 1e-9, 'roof_surface != ctx.roof_z')

# ---- renders
VIEWS = {   # name: (ortho?, pos, look, scale or fov, portrait)
    'front': (True, (1.8, -30, 4.7), (1.8, 0, 4.7), 10.8, True),
    'rear': (True, (1.3, 50, 4.7), (1.3, 0, 4.7), 10.8, True),
    'flank': (True, (5.42, 8.6, 4.7), (0, 8.6, 4.7), 19.5, False),             # between the house and the east neighbour
    'roofplan': (True, (1.8, 8.6, 40), (1.8, 8.6, 0), 19.5, True),
    'garden': (False, (1.6, 24.6, 1.6), (1.3, 17.4, 4.6), 80, True),            # v2:f_0251
    'balcony': (False, (1.25, 19.6, 1.5), (1.25, 17.4, 4.3), 100, True),        # v2:f_0175
    'door': (False, (0.4, -1.9, 1.5), (0.5, -0.1, 3.1), 100, True),             # v2:f_0964
    'gable': (False, (-0.3, -1.4, 1.5), (2.2, -0.1, 6.2), 100, True),           # v2:f_0956
    'passage': (False, (4.35, 11.6, 1.5), (3.7, 9.0, 2.7), 100, True),          # v2:f_0343
    'aerial_rear': (False, (11.0, 27.0, 15.0), (1.8, 9.0, 5.5), 50, False),
    'aerial_front': (False, (9.0, -11.0, 13.0), (1.8, 5.0, 5.5), 50, False),
    'on_balcony': (False, (0.5, 17.6, 4.6), (2.2, 18.5, 3.6), 100, False),      # v3:f_0285
    'velux': (False, (3.6, 8.2, 9.9), (3.0, 6.0, 8.5), 60, False),
    'bay': (False, (0.0, -2.6, 1.5), (2.4, -0.1, 1.9), 95, True),               # v2:f_0954
    'gable_ortho': (True, (2.5, -30, 6.3), (2.5, 0, 6.3), 4.6, False),
    'eaves_k': (False, (5.2, 12.5, 4.0), (3.9, 9.0, 6.8), 70, True),            # v4:f_0422 (from below)
}
if not A.no_render:
    sc = bpy.context.scene
    stand = E._Mesh()                               # dark stand-ins for the rooms, so holes read as openings
    for rid, r in h.rooms.items():
        if h.kind(rid) == 'exterior' or r['level'] == 'B' or r.get('ceiling'):       # not under the slopes
            continue
        poly, z0, z1 = h.room_poly(rid), h.floor_z(rid), h.ceil_z(rid)
        stand.face([(x, y, z1) for x, y in poly], 'standin')
        for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
            stand.face([(x0, y0, z0), (x1, y1, z0), (x1, y1, z1), (x0, y0, z1)], 'standin')
    E.FALLBACK['standin'] = ('#15161A', 0.9)
    E.FALLBACK['ground'] = ('#6E6E68', 0.9)
    stand.box((-12, -16, -0.6), (16, 32, -0.5), 'ground')
    if A.with_site:
        try:
            from lib import site
            site.build(h)
        except Exception as e:                      # another owner's module: the envelope test does not depend on it
            print(f'[test] site not built: {e!r}')
    for q in h.spec['exterior']['neighbours']:      # neighbours as plain boxes
        px, py = [p[0] for p in q['polygon']], [p[1] for p in q['polygon']]
        stand.box((min(px), min(py), q['z'][0] - 0.5), (max(px), max(py), q['z'][1]), 'ground')
    stand.obj(h, 'neighbours.standin', 'neighbours', 'shell')
    sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN'))
    sun.data.energy, sun.data.angle = 3.0, math.radians(1.0)
    sun.rotation_euler = Vector((0.429, -0.807, 0.407)).to_track_quat('Z', 'Y').to_euler()     # MULTILEVEL 9 SUN_DIR
    sc.collection.objects.link(sun)
    sc.world = bpy.data.worlds.new('sky')
    sc.world.use_nodes = True
    bg = next(n for n in sc.world.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs['Color'].default_value, bg.inputs['Strength'].default_value = (0.62, 0.74, 0.95, 1), 1.0
    sc.render.engine = 'CYCLES'
    sc.cycles.samples, sc.cycles.use_denoising = min(A.samples, 96), True
    prefs = bpy.context.preferences.addons['cycles'].preferences
    for dev in ('OPTIX', 'CUDA'):
        try:
            prefs.compute_device_type = dev
            prefs.get_devices()
            for dv in prefs.devices:
                dv.use = dv.type == dev
            if any(dv.use for dv in prefs.devices):
                sc.cycles.device = 'GPU'
                break
        except TypeError:
            pass
    sc.view_settings.view_transform = 'AgX'
    sc.render.image_settings.file_format = 'JPEG'
    res = min(A.res, 960)
    for name, (ortho, pos, look, k, portrait) in VIEWS.items():
        if A.only and name not in A.only.split(','):
            continue
        cam = bpy.data.cameras.new(name)
        if ortho:
            cam.type, cam.ortho_scale = 'ORTHO', k
        else:
            cam.sensor_fit, cam.angle = 'AUTO', math.radians(k)
        cam.clip_start, cam.clip_end = 0.01, 300
        ob = bpy.data.objects.new('cam.' + name, cam)
        ob.location = pos
        ob.rotation_euler = (Vector(look) - Vector(pos)).to_track_quat('-Z', 'Y').to_euler()
        sc.collection.objects.link(ob)
        sc.camera = ob
        sc.render.resolution_x, sc.render.resolution_y = (round(res * 0.5625), res) if portrait else (res, round(res * 0.5625))
        sc.render.filepath = str(Path(A.out) / f'{name}.jpg')
        bpy.ops.render.render(write_still=True)
        print(f'[test] wrote {sc.render.filepath}')

if fails:
    print(f'[test] {len(fails)} FAILURES')
    sys.exit(1)
print('ENVELOPE OK')

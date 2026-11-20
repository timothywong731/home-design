"""Multi-level fixture for the export, and the check of what an export wrote (MULTILEVEL.md section 12 e).

1. Build the fixture (Blender): the phase-1 build with levels.
   blender -b --factory-startup build/home.blend --python blender/export_fixture.py --
           [--house spec/house.json] [--save build/fx_levels.blend]
   - every object gets level 'G' (a phase-1 build has no obj['level']);
   - the kitchen and wc objects, lights included, are copied up to the first floor as room 'green_bathroom'
     (level 1); their interaction tags follow (group ids prefixed, points lifted, switches name green_bathroom,
     no 'blocks': the copied leaves stand in no opening of the house);
   - a deck quad 'garden.deck' (level X) from the house json.
   Then: blender -b --factory-startup build/fx_levels.blend --python blender/export.py -- --house
         spec/house.json --out build/export_fx --tmp build/export_fx_tmp --samples 64

2. Check an export (plain Python with PIL, no Blender):
   python blender/export_fixture.py --check build/export_fx [--fixture]
   Asserts the manifest (schema 2) against the files it names: GLB nodes carry their level, names are unique across
   the GLBs, lightmap object lists resolve in their own level's GLB, the lights-off set is complete, interaction
   groups stay on one level, sky.jpg is an 8-bit 2:1 image, byte counts and budgets hold. --fixture also expects
   what step 1 builds (GLBs G, 1, X; atlases and off atlases of green_bathroom and garden). Prints EXPORT CHECK OK.
"""
import json
import struct
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FAR_ROOMS = {'facade', 'roof', 'neighbours'}     # as export.py: no rooms[] entry, no lights-off atlas


def glb_json(path):
    with open(path, 'rb') as f:
        f.seek(12)
        n, _ = struct.unpack('<I4s', f.read(8))
        return json.loads(f.read(n))


def check(out, fixture=False):
    from PIL import Image
    m = json.loads((out / 'manifest.json').read_text(encoding='utf-8'))
    assert m['schema'] == 2
    levels = {l['id']: l for l in m['levels']}
    rooms = {r['id']: r for r in m['rooms']}
    assert not FAR_ROOMS & set(rooms), 'facade / roof / neighbours must not be in rooms[]'
    assert all({'level', 'kind', 'name', 'polygon', 'floorZ', 'ceilZ'} <= set(r) for r in rooms.values())
    level_of = {rid: l['id'] for l in m['levels'] for rid in l['rooms']}
    assert all(r['level'] == level_of[rid] for rid, r in rooms.items()), 'rooms[].level disagrees with levels[].rooms'
    assert m['loadOrder'] == [l for l in m['loadOrder'] if levels[l]['glb']] and \
        set(m['loadOrder']) == {l for l in levels if levels[l]['glb']}, 'loadOrder = exactly the levels with a GLB'

    nodes, groups = {}, {}                       # node name -> level; ix group -> levels
    for lid in m['loadOrder']:
        l = levels[lid]
        assert (out / l['glb']).stat().st_size == l['bytes'], f'{l["glb"]}: bytes'
        g = glb_json(out / l['glb'])
        assert not any(n.get('children') for n in g['nodes']), f'{l["glb"]}: the node list is not flat'
        for n in g['nodes']:
            x = n.get('extras', {})
            assert x.get('level') == lid and level_of.get(x.get('room')) == lid, f'{l["glb"]}: {n.get("name")} extras {x}'
            assert n['name'] not in nodes, f'node name {n["name"]} in two GLBs'
            nodes[n['name']] = lid
            if 'ix' in x:
                groups.setdefault(json.loads(x['ix'])['g'], set()).add(lid)
    assert all(len(v) == 1 for v in groups.values()), 'an interaction group spans two level GLBs'

    def images(key, sized):
        seen = {}
        for e in m[key]:
            f = out / e['image']
            assert f.stat().st_size == e['bytes'], f'{e["image"]}: bytes'
            assert e['level'] == level_of[e['room']], f'{key} {e["room"]}: level'
            with Image.open(f) as im:
                assert im.mode == 'RGB' and (not sized or im.size == (e['size'], e['size'])), f'{e["image"]}: {im.mode} {im.size}'
            for name in e.get('objects', []):
                assert nodes.get(name) == e['level'], f'{key} {e["room"]}: object {name} is not in glb/{e["level"]}.glb'
            seen[e['room']] = e
        return seen

    on, off = images('lightmaps', True), images('lightmapsOff', True)
    pr, pr_off = images('probes', False), images('probesOff', False)
    assert set(on) - FAR_ROOMS == set(off) and not FAR_ROOMS & set(off), f'off atlases: {sorted(set(on) ^ set(off))}'
    assert all(off[r]['objects'] == on[r]['objects'] and off[r]['size'] * 2 == on[r]['size'] for r in off)
    assert set(pr) == set(pr_off) and set(pr) <= set(rooms), 'probes / probesOff'

    with Image.open(out / m['sky']['image']) as im:
        assert im.mode == 'RGB' and im.size[0] == 2 * im.size[1] and im.format == 'JPEG', f'sky: {im.mode} {im.size}'
    assert abs(sum(c * c for c in m['sky']['sunDir']) - 1) < 1e-3 and m['sky']['sunDir'][2] > 0, 'sky.sunDir'
    assert len(m['sky']['color']) == 7 and m['spawn']['level'] in levels

    first = sum((out / f).stat().st_size for f in m['firstView']['files'] if (out / f).exists())
    assert abs(first - m['firstView']['bytes']) < 64, f'firstView.bytes {m["firstView"]["bytes"]} != {first}'
    assert first < 35e6 and all(l['bytes'] <= (21.5e6 if l['id'] == 'G' else 40e6) for l in levels.values())
    assert max(f.stat().st_size for f in out.rglob('*') if f.is_file()) < 50e6

    for f in json.loads((out / 'footprints.json').read_text(encoding='utf-8')):
        assert f['level'] == level_of[f['room']] and nodes.get(f['name']) == f['level'], f'footprint {f["name"]}'

    if fixture:
        assert m['loadOrder'] == ['G', 'X', '1'], m['loadOrder']
        assert {'green_bathroom', 'garden'} <= set(on) & set(off) and {'green_bathroom', 'garden'} <= set(pr)
        assert on['green_bathroom']['level'] == '1' and on['garden']['level'] == 'X'
        assert any(g.startswith('green_bathroom.') for g in groups), 'copied interaction tags did not reach glb/1.glb'
    print(f'EXPORT CHECK OK: {len(m["loadOrder"])} GLBs {m["loadOrder"]}, {len(nodes)} nodes, {len(groups)} interaction '
          f'groups, {len(on)} + {len(off)} lightmaps, {len(pr)} + {len(pr_off)} probes, first view {first / 1e6:.1f} MB')


def build():
    import argparse
    import bpy
    from mathutils import Matrix
    sys.path.insert(0, str(HERE))
    from lib import ctx as C
    ap = argparse.ArgumentParser(prog='export_fixture.py')
    ap.add_argument('--house', default='spec/house.json')
    ap.add_argument('--save', default='build/fx_levels.blend')
    a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    h = C.House.load(ROOT / a.house)
    sc = bpy.context.scene
    for o in sc.objects:
        if 'room' in o.keys():
            o['level'] = 'G'

    room, prefix = 'green_bathroom', 'green_bathroom.'
    lift = Matrix.Translation((0, 0, h.floor_z(room) - h.floor_z('kitchen')))
    twin = {}
    for o in [o for o in sc.objects if o.get('room') in ('kitchen', 'wc')]:
        d = twin[o] = o.copy()                   # shares mesh / light data, like any linked duplicate
        for c in o.users_collection:
            c.objects.link(d)
        d.name = prefix + o.name
        d['room'], d['level'] = room, h.level(room)
    for o, d in twin.items():
        if o.parent in twin:
            d.parent = twin[o.parent]            # the local matrix and the parent inverse came with the copy
        else:
            d.parent = None
            d.matrix_world = lift @ o.matrix_world
        if 'ix' in d.keys():
            t = json.loads(d['ix'])
            t['g'] = prefix + t['g']
            if 'p' in t:
                t['p'][2] = round(t['p'][2] + lift.translation.z, 4)
            if 'excl' in t:
                t['excl'] = [prefix + g for g in t['excl']]
            if 'rooms' in t:
                t['rooms'] = [room]
            t.pop('blocks', None)
            d['ix'] = json.dumps(t, separators=(',', ':'))

    deck = h.zone('deck')
    me = bpy.data.meshes.new('garden.deck')
    me.from_pydata([(x, y, deck['z']) for x, y in deck['polygon']], [], [range(len(deck['polygon']))])
    mat = bpy.data.materials.new('fx_deck')
    mat.use_nodes = True
    next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value = (0.16, 0.1, 0.07, 1)
    me.materials.append(mat)
    h.add(bpy.data.objects.new('garden.deck', me), 'garden', 'shell')

    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / a.save))
    print(f'FIXTURE OK: {len(twin)} objects copied to {room}, garden.deck added -> {a.save}')


if __name__ == '__main__':
    try:
        if '--check' in sys.argv:
            check((ROOT / sys.argv[sys.argv.index('--check') + 1]).resolve(), '--fixture' in sys.argv)
        else:
            build()
    except SystemExit:
        raise
    except BaseException:
        import traceback
        traceback.print_exc()
        sys.exit(1)

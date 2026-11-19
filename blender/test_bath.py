"""Bathroom fittings library test (lib/bath.py).

  blender -b --factory-startup --python blender/test_bath.py -- [--res 400] [--samples 64] [--no-render]

Builds every item once on an empty scene (one wall at y = 0, room side -Y), asserts tags / normals / state-1 clearances,
renders six cameras in state 0 and posed (state 1) and tiles them into D:/.../build/rooms2/kit/kit.jpg (top row = state
0, bottom row = state 1; the single tiles stay beside it as tile_<cam>_<state>.jpg). Prints BATH OK, exits 1 on failure."""
import argparse, json, math, os, sys, traceback

import bpy, bmesh
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(ROOT, 'blender'))
from lib import bath, interact as IX, lighting, preview, props as P   # noqa: E402

OUT = os.path.join(ROOT, 'build', 'rooms2', 'kit')                   # absolute: a relative path lands on the drive root
N = (0, -1)                                                          # normal of the test wall


def build():
    """-> {label: parts}; everything linked into the scene."""
    col = bpy.context.scene.collection
    items = {}

    def put(o, loc, facing=N, rot_z=None):
        P.place(o, loc, facing=facing, rot_z=rot_z)
        col.objects.link(o)
        return o

    def keep(label, parts):
        for o in parts:
            if o.name not in col.objects:
                col.objects.link(o)
        items[label] = parts
        return parts

    put(P.box(12, 6, .1, '#C9C5BC'), (4, -2.5, -.1), None)                       # floor
    put(P.box(12, .1, 2.6, '#9AA59E'), (4, .05, 0), None)                         # wall, face at y = 0

    keep('wc wall_hung', bath.wc('t.wc', (0, 0, 0), N))
    put(P.box(.44, .22, .83, '#DAD8D0'), (.8, -.11, 0), None)                       # furniture WC unit, front at y = -0.22
    keep('wc back_to_wall', bath.wc('t.wc2', (.8, -.22, 0), N, kind='back_to_wall', flush='button', flush_z=.72))

    keep('wc rotated', bath.wc('t.wc3', (-1.5, -4, 0), (1, 0)))                  # tags must follow any wall direction
    for x, style, fin in ((1.8, 'mono', 'chrome'), (2.3, 'pin', 'brass_antique')):
        put(P.box(.48, .45, .16, 'ceramic_white'), (x, -.225, .70), None)             # stand-in basin, rim 0.86
        keep('basin_mixer ' + style, bath.basin_mixer('t.tap.' + style, (x, -.06, .86), .80, N, style=style, finish=fin))
    assert bath.basin_mixer('t.tap.x', (0, -9, 0), .0 - .06, N)[0].data is items['basin_mixer mono'][0].data, 'mesh sharing'

    put(P.box(.9, .3, .56, 'ceramic_white'), (3.1, -.15, 0), None)                  # stand-in bath rim
    keep('bath_mixer', bath.bath_mixer('t.bathmix', (3.1, -.10, .56), .10, N))
    keep('handset', [put(bath.handset(name='t.handset'), (3.45, 0, 1.10))])
    keep('bath_filler', bath.bath_filler('t.filler', (3.95, -.45, 0), .10, N))
    keep('towel_rail', [put(bath.towel_rail(.5, 1.5, name='t.rail'), (4.75, 0, .30))])
    keep('glass_door', bath.glass_door('t.sauna.door', (5.55, -.45, .08), .60, 1.84, N, hinge='right', mat='glass_dark'))

    # shower 1.40 x 0.90 in the corner of the test wall and a side wall at x = 6.3: tray, control set, slider, return pane
    put(P.box(.1, 1.2, 2.6, '#9AA59E'), (6.25, -.6, 0), None)
    put(P.box(1.4, .9, .04, 'ceramic_white'), (7.0, -.45, 0), None)
    keep('shower_set', bath.shower_set('t.shower', (6.3, -.45, 0), (1, 0), basket_z=1.30))
    keep('shower_slider', bath.shower_slider('t.screen', (7.0, -.90, .04), 1.40, N, door='right'))
    keep('glass_pane', [put(bath.glass_pane(.90, 1.95, channel='right', name='t.return'), (7.7, -.45, .04), None, 90)])
    return items


def ix(o):
    return json.loads(o['ix']) if 'ix' in o.keys() else None


def volume(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    v = bm.calc_volume(signed=True)
    bm.free()
    return v


def world(o):
    return [o.matrix_world @ v.co for v in o.data.vertices]


def check_state0(items):
    lines = []
    for label, parts in items.items():
        for o in parts:
            assert tuple(round(s, 6) for s in o.scale) == (1, 1, 1) and o.parent is None, label
            assert o.data.polygons and o.data.uv_layers and o.data.materials, (label, o.name)
            assert all(math.isfinite(c) for v in o.data.vertices for c in v.co), label
        lines.append('%-22s %6d tris  %s' % (label, sum(P.tris(o) for o in parts),
                                             ' '.join('%s:%s' % (o.name, (ix(o) or {}).get('t', '-')) for o in parts)))
    kinds = lambda label: [(ix(o) or {}).get('t') for o in items[label]]
    assert kinds('wc wall_hung') == kinds('wc back_to_wall') == kinds('wc rotated') == [None, 'hinge', 'hinge', None]
    assert kinds('basin_mixer mono') == kinds('bath_filler') == ['trigger', 'hinge', 'show']
    assert kinds('bath_mixer') == ['trigger', 'show'] and kinds('shower_set') == ['trigger', 'show']
    assert kinds('shower_slider') == [None, 'slide'] and kinds('glass_door') == ['hinge']
    for label, parts in items.items():                                           # one group per builder, fx water on streams
        gs = {ix(o)['g'] for o in parts if ix(o)}
        assert len(gs) <= 1 or label.startswith('wc'), (label, gs)
        assert all(ix(o)['fx'] == 'water' for o in parts if ix(o) and ix(o)['t'] == 'show'), label
    for label in ('wc wall_hung', 'wc back_to_wall'):                            # outward normals (the GLB culls back faces)
        for o in items[label][:3]:
            assert volume(o) > 1e-5, (o.name, volume(o))
    for label, to_z in (('basin_mixer mono', .80), ('basin_mixer pin', .80), ('bath_mixer', .10), ('bath_filler', .10),
                        ('shower_set', .04)):                                    # streams land where they were told to
        z = min(p.z for p in world(items[label][-1]))
        assert abs(z - to_z) < 2e-3, (label, z)
    assert items['towel_rail'][0].data is bath.towel_rail(.5, 1.5).data
    return lines


def check_state1(items):
    for label, wall_y in (('wc wall_hung', 0.0), ('wc back_to_wall', -.22)):     # raised seat + lid stand clear of the wall
        for o in items[label][1:3]:
            ys = [p.y for p in world(o)]
            assert max(ys) < wall_y - .004, (o.name, max(ys))
            assert max(p.z for p in world(o)) > .85, o.name
    for o in items['wc rotated'][1:3]:                                            # backs onto x = -1.5, room side +X
        assert min(p.x for p in world(o)) > -1.5 + .004 and max(p.z for p in world(o)) > .85, o.name
    xs = [p.x for p in world(items['shower_slider'][1])]                          # the door stays between wall and return
    assert 6.3 - 1e-3 <= min(xs) and max(xs) < 7.1, (min(xs), max(xs))
    assert min(p.y for p in world(items['glass_door'][0])) < -1.0                 # the hinged door swung outward (-Y)
    for label in ('basin_mixer mono', 'basin_mixer pin', 'bath_filler'):          # levers lift
        lever = items[label][1]
        assert max(p.z for p in world(lever)) > lever.get('_z0', 0) + .008, label


CAMS = [   # name, pos, look, fov over the tile
    ('wc', (.4, -1.55, 1.15), (.4, -.1, .50), 62),
    ('basin', (2.05, -.60, 1.10), (2.05, -.06, .92), 62),
    ('bath', (3.5, -1.75, 1.25), (3.5, -.2, .62), 62),
    ('rail_door', (5.1, -2.7, 1.3), (5.1, 0, 1.05), 55),
    ('shower', (7.9, -3.0, 1.55), (6.95, -.45, 1.10), 50),
    ('control', (7.25, -.72, 1.60), (6.3, -.45, 1.62), 80),
]


def render_tiles(state, res, samples):
    tiles = []
    for name, pos, look, fov in CAMS:
        cam = bpy.data.objects.get('cam_' + name) or preview.camera('cam_' + name, pos, look, fov)
        path = os.path.join(OUT, 'tile_%s_%d.jpg' % (name, state))
        preview.render(cam, path, (res, res), samples)
        im = bpy.data.images.load(path)
        tiles.append(np.array(im.pixels[:], np.float32).reshape(res, res, 4))
        bpy.data.images.remove(im)
    return np.concatenate(tiles, axis=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--res', type=int, default=400)
    ap.add_argument('--samples', type=int, default=64)
    ap.add_argument('--no-render', action='store_true')
    a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    os.makedirs(OUT, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    items = build()
    bpy.context.view_layer.update()
    tagged = [o for o in sc.objects if 'ix' in o.keys()]
    IX.pose(tagged, 0)                                                           # hide the running water
    print('\n'.join(check_state0(items)))
    for label in ('basin_mixer mono', 'basin_mixer pin', 'bath_filler'):
        items[label][1]['_z0'] = max(p.z for p in world(items[label][1]))

    if not a.no_render:
        lighting.setup_cycles(a.samples, (a.res, a.res))
        sc.view_settings.exposure = 0.0
        try:
            sc.view_settings.use_white_balance = False
        except AttributeError:
            pass
        w = bpy.data.worlds.new('W')
        sc.world = w
        w.use_nodes = True
        bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND')
        bg.inputs['Color'].default_value, bg.inputs['Strength'].default_value = (.92, .95, 1, 1), .9
        sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN'))
        sun.data.energy, sun.data.angle = 2.0, math.radians(8)
        sun.rotation_euler = (math.radians(55), 0, math.radians(25))
        sc.collection.objects.link(sun)
        row0 = render_tiles(0, a.res, a.samples)

    IX.pose(tagged, 1)
    bpy.context.view_layer.update()
    check_state1(items)

    if not a.no_render:
        row1 = render_tiles(1, a.res, a.samples)
        sheet = np.concatenate([row1, row0], axis=0)                             # image rows run bottom-up: state 0 on top
        im = bpy.data.images.new('kit', sheet.shape[1], sheet.shape[0])
        im.pixels.foreach_set(sheet.ravel())
        im.filepath_raw, im.file_format = os.path.join(OUT, 'kit.jpg'), 'JPEG'
        im.save()
        print('[test_bath] wrote', im.filepath_raw)
    print('BATH OK')


if __name__ == '__main__':
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)

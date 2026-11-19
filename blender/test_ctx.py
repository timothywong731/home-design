"""Asserts the ctx API of blender/MULTILEVEL.md section 3 on spec/house.json (schema 2) and, while it exists, on the schema-1 docs/assets/house.json.

    python blender/test_ctx.py [--house spec/house.json]                          # pure data
    blender -b --factory-startup --python blender/test_ctx.py [-- --house PATH]              # + ctx.add, Vectors
Prints CTX OK; exits 1 on any failure.
"""
import math
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lib import ctx as C                                    # noqa: E402

ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
HOUSE = ARGS[ARGS.index('--house') + 1] if '--house' in ARGS else HERE.parent / 'spec' / 'house.json'


def near(a, b, tol=1e-6):
    if isinstance(a, (int, float)):
        return abs(a - b) <= tol
    return len(a) == len(b) and all(near(x, y, tol) for x, y in zip(a, b))


def eq(a, b, tol=1e-6):
    assert near(a, b, tol), f'{a} != {b}'


def schema2():
    h = C.House.load(HOUSE)
    assert h.schema == 2 and h.spec['schema'] == 'house/2'
    # rooms, levels, pseudo-rooms
    assert len(h.rooms) == 28 and h.levels == ['B', 'G', '1', '2']
    eq(h.level_info['1']['datumZ'], 3.04)
    assert h.rooms_on('B') == ['basement', 'basement_stair'] and h.rooms_on('X') == list(C.PSEUDO_ROOMS)
    assert sum(len(h.rooms_on(l)) for l in h.levels) == 28
    assert set(h.building_rooms) == {'shed_workshop', 'shed_store'} and h.building_rooms['shed_store']['building'] == 'shed'
    assert [h.level(r) for r in ('basement', 'living', 'balcony', 'loft_office', 'garden', 'shed_workshop', 'roof')] == \
        ['B', 'G', '1', '2', 'X', 'X', 'X']
    assert [h.kind(r) for r in ('living', 'stairs', 'eaves_front', 'balcony', 'facade', 'shed_store')] == \
        ['room', 'stairwell', 'void', 'exterior', 'site', 'site']
    assert h.is_exterior('balcony') and h.is_exterior('garden') and not h.is_exterior('living')
    assert h.tag_room('shed_workshop') == 'shed' and h.tag_room('living') == 'living' and h.tag_room('garden') == 'garden'
    assert [h.module_of(r) for r in ('landing1_ql', 'landing2_head', 'eaves_rear', 'basement_stair', 'stairs2', 'shed_store',
                                     'front')] == ['landing1', 'landing2', 'eaves', 'basement', 'stairs2', 'shed', 'front']
    assert h.room_at(2.5, 3.0, 'G') == 'living' and h.room_at(2.5, 3.0, '1') == 'green_bedroom'

    # chamfers: polygon edges
    (nw, b0, b1) = h.chamfers('living')
    assert (nw['id'], nw['reflex'], nw['stop']) == ('living_nw_chamfer', False, None)
    eq(nw['p'], (1.21, 5.19)), eq(nw['q'], (0.8, 4.78)), eq(nw['c'], (0.8, 5.19)), eq(nw['v'], nw['c']), eq(nw['z'], (0, 2.95))
    (sd,) = h.chamfers('stairs')
    assert sd['id'] == 'hall_stair_diag'
    eq(sd['p'], (0.65, 5.05)), eq(sd['q'], (0.99, 5.39)), eq(sd['c'], (0.99, 5.05))
    (lc,) = h.chamfers('landing1_rear')
    eq(lc['p'], (0.35, 8.73)), eq(lc['q'], (0.25, 8.83)), eq(lc['c'], (0.35, 8.83)), eq(lc['z'], (3.04, 5.49))
    assert h.chamfers('hallway') == [] and h.chamfers('shed_workshop') == []
    # chamfers: bay arris splays ("45 at the bottom, 90 at the top")
    leg = 0.15 / math.sqrt(2)
    assert (b0['id'], b1['id'], b0['reflex']) == ('living_bay.0', 'living_bay.1', True)
    eq(b0['v'], (1.1, 0.99)), eq(b0['p'], (1.1 - leg, 0.99)), eq(b0['q'], (1.1, 0.99 - leg)), eq(b0['c'], (1.1 - leg, 0.99 - leg))
    eq(b1['v'], (4.0, 0.99)), eq(b1['p'], (4.0, 0.99 - leg)), eq(b1['q'], (4.0 + leg, 0.99)), eq(b1['c'], (4.0 + leg, 0.99 - leg))
    eq(b0['z'], (0, 2.2)), eq(b0['stop'], (2.2, 2.4))
    g0, g1 = h.chamfers('green_bedroom')
    eq(g0['v'], (1.16, 0.99)), eq(g1['v'], (3.9, 0.99)), eq(g0['z'], (3.42, 5.72)), eq(g0['stop'], (5.72, 5.82))
    eq(math.dist(g0['p'], g0['v']), 0.12 / math.sqrt(2)), eq(g0['c'], (1.16 - 0.0848528, 0.99 - 0.0848528))
    for ch in (b0, b1, g0, g1):                            # c lies in the wall, i.e. outside the room polygon
        room = 'living' if ch['id'].startswith('living') else 'green_bedroom'
        assert not C.point_in_poly(*ch['c'], h.room_poly(room))
    # room_poly
    eq(h.room_poly('stairs', rect=True), [(0.15, 5.05), (0.99, 5.05), (0.99, 7.58), (0.15, 7.58)])
    lr = h.room_poly('living', rect=True)
    assert (0.8, 5.19) in lr and (1.21, 5.19) not in lr and len(lr) == len(h.room_poly('living')) - 1
    assert (0.35, 8.83) in h.room_poly('landing1_rear', rect=True) and len(h.room_poly('landing1_rear', rect=True)) == 10
    assert h.room_poly('dining', rect=True) == h.room_poly('dining') and len(h.room_poly('shed_workshop')) == 4

    # floors and ceilings
    eq(h.floor_z('landing1_front'), 3.42), eq(h.floor_z('landing1_front', -0.3, 8.0), 3.23), eq(h.floor_z('landing1_front', -0.3, 7.0), 3.42)
    eq(h.floor_z('eaves_rear', 3.0, 7.5), 6.37), eq(h.floor_z('eaves_rear', 2.0, 7.5), 6.49), eq(h.floor_z('shed_workshop'), -0.32)
    eq(h.ceil_z('hallway'), 2.95), eq(h.ceil_z('hallway', 0.5, 7.9), 2.3), eq(h.ceil_z('hallway', 0.5, 8.4), 2.6)
    eq(h.ceil_z('hallway', 0.0, 3.0), 2.95), eq(h.ceil_z('kitchen', 2.0, 9.0), 2.03), eq(h.ceil_z('shed_store'), 1.83)
    eq(h.ceil_z('loft_office'), 8.61), eq(h.ceil_z('loft_office', 2.0, 3.0), 5.9435 + 0.57735 * 3.0), eq(h.ceil_z('loft_office', 0.0, 5.8), 8.57)
    eq(h.ceil_z('loft_office', 2.0, 2.54), 5.9435 + 0.57735 * 2.54)            # on the polygon edge (knee wall)
    assert h.ceil_z('balcony') is None and h.ceil_z('balcony', 1.0, 18.0) is None
    eq(h.ceil_z('eaves_front', -0.3, 2.0), 6.2528 + 0.57735 * 2.0 - 0.30)      # under_roof: slab underside

    # roof
    eq(h.roof_z(2.0, 5.0), 9.14, 0.02), eq(h.roof_z(0.0, 0.0, ground=True), 3.3111), eq(h.roof_z(1.0, 12.0), 8.87)
    assert h.roof_z(10, 10) is None and h.roof_z(0.0, 0.0) is None and h.roof_under(10, 10) is None
    assert h.roof_plane(1.0, 12.0) == 'rear_flat' and h.roof_plane(2.0, 1.0) == 'bay_gable_w' and h.roof_plane(0.0, 7.0) == 'stair_dormer'
    slab = {p['id']: h.roof_slab_t(p['id']) for p in h.spec['roof']['planes']}
    assert slab == dict(main_front=0.30, main_rear=0.30, stair_dormer=0.24, rear_flat=0.24, bay_gable_w=0.30, bay_gable_e=0.30,
                        porch_leanto=0.30), slab
    eq(h.roof_under(1.0, 12.0), 8.63), eq(h.roof_under(0.0, 7.0), 8.63), eq(h.roof_under(0.0, 0.0, ground=True), 3.0111)
    for rid in h.rooms_on('2'):                            # every flat slab clears the ceilings of the kind-'room' rooms
        if h.kind(rid) == 'room' and rid != 'loft_office':
            x, y = h.room_poly(rid)[0]
            assert h.roof_under(x + 0.05, y + 0.05) >= h.ceil_z(rid) + 0.01 - 1e-9, rid

    # stairs
    assert [s['id'] for s in h.stairs] == ['stair_main', 'stair_basement', 'steps_ql_rear', 'steps_rear_front', 'stair_second',
                                           'step_head_platform']
    for sid, n, z1, zn, whole in (('stair_main', 14, 0.19, 2.66, False), ('stair_basement', 10, -0.21, -2.1, True),
                                  ('stair_second', 12, 3.62, 5.82, True)):
        s = h.stair(sid)
        tr = s['treads']
        assert [t['n'] for t in tr] == list(range(1, n + 1)) and tr[0]['riser'] == s['walk']['risers'][0]
        eq(tr[0]['z'], z1), eq(tr[-1]['z'], zn)
        areas = [C.poly_area(t['poly']) for t in tr]
        assert min(areas) > 0.04, (sid, areas)             # counter-clockwise, none degenerate
        if whole:                                          # first and last riser lie on the footprint edge
            eq(sum(areas), C.poly_area(s['walk']['polygon']), 1e-4)
    eq(sorted(h.stair('stair_basement')['treads'][9]['poly']), [(0.265, 5.19), (1.25, 5.19), (1.25, 6.0)])     # last winder
    eq(sorted(h.stair('stair_main')['treads'][5]['poly']), [(0.15, 6.06), (0.15, 6.29), (0.99, 6.06), (0.99, 6.29)])
    (t,) = h.stair('steps_rear_front')['treads']
    eq(t['poly'], [(-0.65, 8.13), (0.15, 8.13), (0.15, 7.88), (-0.65, 7.88)]), eq(t['z'], 3.23)
    assert h.stair('steps_ql_rear')['treads'] == [] and h.step_treads('landing1_front')[0]['z'] == t['z']
    assert h.stairs['rise'] == 0.19 and h.stairs['landing']['z'] == 2.85 and h.stairs[1]['id'] == 'stair_basement'    # phase-1 key access

    # site
    assert h.zones_of('garden') == ['garden_path', 'deck', 'deck_step_n', 'deck_step_e', 'lawn', 'lavender_bed']
    assert h.zones_of('front') == ['forecourt', 'forecourt_alley_mouth', 'footway', 'road'] and h.zones_of('shed') == ['shed_veranda']
    assert h.zone('road')['walk'] is False and 'zFar' not in h.zone('forecourt')
    for zid, (z0, z1) in (('forecourt', (-0.06, -0.14)), ('side_alley', (-0.08, -0.30))):      # both ends of each fall
        f = h.zone(zid)['fall']
        eq(h.zone_z(zid, *f['from']), z0), eq(h.zone_z(zid, *f['to']), z1), eq(h.zone_z(zid), z0)
        eq(h.zone_z(zid, (f['from'][0] + f['to'][0]) / 2, (f['from'][1] + f['to'][1]) / 2), (z0 + z1) / 2)
    eq(h.zone_z('forecourt', -0.5, -9.0), -0.14), eq(h.zone_z('forecourt', 4.0, -2.66), -0.10), eq(h.zone_z('deck', 1.0, 18.0), -0.05)
    assert h.zone_at(1.0, 18.0) == 'deck' and h.zone_at(3.5, 18.0) == 'deck_step_e' and h.zone_at(3.5, 19.5) == 'garden_path'
    assert h.zone_at(4.8, 9.5) == 'side_alley' and h.zone_at(2.0, 5.0) is None            # the gate now leads somewhere
    eq(h.ground_z(3.5, 9.1), -0.02), eq(h.ground_z(3.5, 9.5), -0.16), eq(h.ground_z(3.5, 12.0), -0.30), eq(h.ground_z(1.9, -2.66), -0.10)
    assert h.ground_z(2.0, 5.0) is None

    # openings, walls
    assert len(h.spec['openings']) == 51 and len(h.openings) == 55 and len(h.walls) == 108 + 5
    assert h.openings['shed_d1']['building'] == 'shed' and h.openings['shed_d1']['level'] == 'X' and 'building' not in h.spec['exterior']['buildings'][0]['openings'][0]
    assert h.walls['shed_w_front']['rooms'] == ['shed_workshop', 'outside'] and h.walls['shed_w_front']['kind'] == 'external'
    assert h.exterior_openings('X') == ['shed_w1', 'shed_d1', 'shed_w2', 'shed_store_doors']
    assert h.exterior_openings('G') == ['d_street', 'd_back', 'd_french', 'w_dining_n_w', 'w_dining_n_e', 'w_dining_e_s', 'w_dining_e_n',
                                        'w_utility', 'w_wc', 'w_bay_front', 'w_bay_cheek_e'], h.exterior_openings('G')
    assert 'd_balcony' in h.exterior_openings('1') and 'd_blue' not in h.exterior_openings() and h.exterior_openings('B') == []
    listed = {o for f in h.spec['exterior']['facades'] for o in f['openings']}
    assert listed == set(h.exterior_openings()) - set(h.exterior_openings('X'))
    assert h.facade_of('d_balcony')['id'] == 'rear_R' and h.facade_of('w_ensuite')['id'] == 'flank_F' and h.facade_of('shed_d1') is None

    f = h.opening_frame('d_balcony')                       # connects end 'balcony' is not a room of the wall
    assert (f['level'], f['exterior'], f['outside_room'], f['room_pos'], f['room_neg'], f['swing_sign']) == \
        ('1', True, 'balcony', 'outside', 'blue_bedroom', 1)
    eq(tuple(f['outward']), (0, 1)), eq(tuple(f['normal']), (0, 1)), eq(f['face_out'], 0.25), eq(f['z0'], 3.04), eq(tuple(f['center']), (1.29, 17.11, 3.04))
    eq(f['ext_reveal'], 0.20), eq(f['head'], 1.9)          # explicit extReveal: 0.24 of reveal inside (blue_bedroom.md 2.3)
    eq(h.zone_z('forecourt_alley_mouth', 4.98, 0.74), h.zone_z('side_alley', 4.98, 0.74))      # no step at the alley mouth
    nb = {q['id']: q for q in h.spec['exterior']['neighbours']}
    eq(h.neighbour_top(nb['west'], -1.0, 3.0)[0], h.roof_z(-0.5, 3.0)), eq(h.neighbour_top(nb['west'], -1.0, 12.0)[0], 8.9)
    assert h.neighbour_top(nb['east'], 5.6, 0.0) == (-99.0, -1) and h.neighbour_top(dict(polygon=[], z=[0, 7.0]), 0, 0) == (7.0, -1)
    eq(h.roof_z(0.6, 0.0), 6.5), eq(h.roof_z(0.0, 0.44), 6.5, 0.01)       # gable eave edge = main eave: one gutter level
    f = h.opening_frame('w_dining_n_w')                    # 0.38 recess in the 0.50 wall: d = 0.12
    eq(f['face_neg'], 0.13), eq(f['face_out'], 0.25), eq(f['ext_reveal'], 0.06), eq(tuple(f['outward']), (0, 1))
    eq(h.opening_frame('w_ensuite')['ext_reveal'], 0.01)   # revealDepth 0.45 in the 0.50 wall
    eq(h.opening_frame('w_yellow')['ext_reveal'], 0.10), eq(h.opening_frame('d_back')['ext_reveal'], 0.08)
    eq(h.opening_frame('d_street')['ext_reveal'], 0.06), eq(h.opening_frame('w_bay_front')['ext_reveal'], 0.015)   # 0.12 walls; the bay has an explicit extReveal
    eq(h.opening_frame('w_wc')['ext_reveal'], 0.215)                # explicit extReveal beats the 0.10 default
    f = h.opening_frame('d_street')
    assert (f['level'], f['exterior'], f['outside_room'], f['swing_sign']) == ('G', True, 'outside', -1)
    eq(tuple(f['outward']), (0, -1)), eq(f['face_out'], -0.06)
    f = h.opening_frame('w_study')                         # upper floor: same shape, center.z = floorZ + sill
    eq(tuple(f['center']), (1.23, 17.11, 6.02 + 0.68)), eq(f['z0'], 6.02), eq(tuple(f['outward']), (0, 1))
    f = h.opening_frame('d_blue')
    assert (f['exterior'], f['outward'], f['face_out'], f['ext_reveal'], f['outside_room']) == (False, None, None, None, None)
    f = h.opening_frame('d_basement')                      # roomsBelow end: swing follows the wall's rooms
    assert f['swing_sign'] == 1 and f['room_pos'] == 'hallway' and not f['exterior']
    f = h.opening_frame('o_stairs2_head')
    assert f['virtual'] and f['swing_sign'] == 0 and near(tuple(f['center']), (0.15, 8.43, 6.02))
    f = h.opening_frame('shed_d1')
    assert (f['level'], f['exterior'], f['outside_room'], f['swing_sign'], f['building']) == ('X', True, 'outside', -1, 'shed')
    eq(tuple(f['outward']), (0, -1)), eq(f['z0'], -0.42), eq(f['ext_reveal'], 0.08), eq(f['wall_thickness'], 0.28)
    eq(tuple(h.opening_frame('shed_store_doors')['outward']), (1, 0))
    for oid in h.exterior_openings():                      # every exterior opening: frame fits in the wall, outward is a unit axis
        f = h.opening_frame(oid)
        assert 0.01 <= f['ext_reveal'] <= (0.10 if 'extReveal' not in h.openings[oid] else 0.3) and abs(abs(f['face_out']) - f['wall_thickness'] / 2) < 1e-9, oid
        o = f['outward']
        eq(abs(o[0]) + abs(o[1]), 1.0)
        fc = h.facade_of(oid)
        if fc:                                             # outward agrees with the facade it is listed in
            assert fc['faces'] == ('+' if o[0] + o[1] > 0 else '-') + ('x' if abs(o[0]) > 0.5 else 'y'), (oid, fc['id'])
    return h


def schema1():
    # the schema-1 loader is still used for the phase-1 assets published in docs/assets until the phase-2 export lands
    import json
    old = HERE.parent / 'docs' / 'assets' / 'house.json'
    if not old.exists() or json.loads(old.read_text(encoding='utf-8')).get('schema') == 'house/2':
        print('[test_ctx] no schema-1 house.json left: schema-1 loader not tested')
        return
    h = C.House.load(old)
    assert h.schema == 1 and h.levels == ['G'] and len(h.rooms) == 8 and h.rooms_on('G') == list(h.rooms)
    assert h.level('living') == 'G' and h.level('shell') == 'G' and h.kind('living') == 'room' and not h.is_exterior('living')
    assert h.building_rooms == {} and h.zones == {} and h.roof_z(0, 0) is None and h.step_treads('hallway') == []
    assert isinstance(h.stairs, dict) and h.tag_room('living') == 'living' and h.module_of('stairs') == 'stairs'
    assert h.ceil_z('living') == float(h.rooms['living']['ceilingZ']) and h.floor_z('living') == 0.0
    assert h.room_poly('living') == [tuple(p) for p in h.rooms['living']['polygon']] and h.room_at(2.5, 3.0) == 'living'
    f = h.opening_frame('d_street')
    assert f['z0'] == 0.0 and f['level'] == 'G' and f['exterior'] and f['room_pos'] == h.walls['w_front_vest']['rooms'][0]
    assert len(h.exterior_openings()) > 5 and h.facade_of('d_street') is None
    for oid in h.openings:
        h.opening_frame(oid)


def blender(h):
    import bpy

    def obj(name):
        return bpy.data.objects.new(name, bpy.data.meshes.new(name))

    a = h.add(obj('shed.bench'), 'shed_workshop', 'fit', plan_sym='workbench')
    assert (a['room'], a['level'], a['kind'], a['lm'], a['plan_sym']) == ('shed', 'X', 'fit', 'static', 'workbench')
    assert [c.name for c in a.users_collection] == ['room_shed']
    b = h.add(obj('balcony.chair'), 'balcony', 'furn')
    assert (b['room'], b['level'], b['lm']) == ('balcony', '1', 'dynamic') and b.users_collection[0].name == 'room_balcony'
    c = h.add(obj('green_bedroom.walls'), 'green_bedroom', 'shell')
    assert (c['room'], c['level']) == ('green_bedroom', '1') and c.users_collection[0].name == 'shell'
    d = h.add(obj('facade.front_A'), 'facade', 'shell')
    assert (d['room'], d['level']) == ('facade', 'X')
    f = h.opening_frame('d_balcony')
    assert abs(f['outward'].length - 1.0) < 1e-6 and abs(f['center'].z - f['z0']) < 1e-6 and len(f['along']) == 2


try:
    house = schema2()
    schema1()
    if C.bpy is not None:
        blender(house)
    print('CTX OK' + (' (with Blender)' if C.bpy is not None else ' (pure Python; ctx.add not run)'))
except Exception:
    traceback.print_exc()
    sys.exit(1)

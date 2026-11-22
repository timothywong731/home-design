"""Asserts the multi-level shell, the flight carcasses and the fills (blender/MULTILEVEL.md sections 4 and 9, core's
acceptance row of section 12) on the schema-2 fixture, bare (no joinery, trim, site or envelope).

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/test_shell.py [-- --house PATH] [--sky]
--sky also re-measures the sky calibration recorded in lib/lighting.py (two tiny GPU renders).
Prints SHELL OK; exits 1 on any failure. It judges geometry only: read the previews of build.py as well.
"""
import math
import sys
import traceback
from pathlib import Path

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lib import ctx as C, lighting, materials, mouldings, shell         # noqa: E402

ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
HOUSE = ARGS[ARGS.index('--house') + 1] if '--house' in ARGS else HERE.parent / 'spec' / 'house.json'


def fresh(levels=None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    shell._mats.clear()                                        # the reset removed every cached material
    materials._cache.clear()
    h = C.House.load(HOUSE)
    h.errors = []
    shell.build(h, levels, bare=True)
    return h


def faces(name):
    """[(centre, normal, material name, zmin, zmax)] of a shell object."""
    me = bpy.data.objects[name].data
    out = []
    for p in me.polygons:
        zs = [me.vertices[v].co.z for v in p.vertices]
        out.append((p.center, p.normal, me.materials[p.material_index].name, min(zs), max(zs)))
    return out


def has_run(loops, a, b):
    near = lambda p, q: math.dist(p, q) < 1e-4
    return any(near(r[0], a) and near(r[1], b) and r[2] == 'wall' for loop in loops for r in loop)


def whole():
    h = fresh()
    g, ob = h.grid, bpy.data.objects
    assert not h.errors and not shell.MISSING, (h.errors, shell.MISSING)
    names = {o.name for o in h.col('shell').objects}
    for o in h.col('shell').objects:                           # tags
        assert o['kind'] == 'shell' and o['room'] in h.rooms and o['level'] == h.level(o['room']) and o.name.startswith(o['room'] + '.'), o.name
    # every room has walls and a floor; ceilings where core owns them (not the under_roof eaves)
    for rid in h.rooms:
        if h.kind(rid) == 'exterior':
            assert not any(n.startswith(rid + '.') for n in names)
            continue
        assert rid + '.walls' in names, rid
        if h.kind(rid) != 'stairwell':
            assert rid + '.floor' in names, rid
        if h.kind(rid) == 'room':
            assert rid + '.ceiling' in names, rid
    assert 'eaves_front.ceiling' not in names and 'eaves_rear.ceiling' not in names

    # mass, slabs and voids
    assert shell.is_solid(h, 2.5, 3.0, 3.2) and shell.is_solid(h, 2.5, 3.0, -0.1) and not shell.is_solid(h, 2.5, 3.0, 1.0)
    assert shell.is_solid(h, 0.57, 8.4, 2.75) and shell.is_solid(h, -0.3, 10.0, 2.95)      # under the split floors 2.85 / 3.04
    assert not shell.is_solid(h, 0.57, 7.0, 3.3) and not shell.is_solid(h, 0.57, 7.0, 5.9)   # the wells are open
    assert not shell.is_solid(h, 0.57, 8.4, 5.6) and shell.is_solid(h, 0.57, 8.4, 5.38)       # well over the winders, slab over QL
    assert not shell.is_solid(h, 0.6, 6.5, -0.3)                                              # no ground slab over the shaft
    assert not shell.is_solid(h, 0.25, 6.83, 8.75) and shell.is_solid(h, -0.5, 6.83, 8.75)    # skylight shaft through the slab
    # o_basement_foot: the wall a flight crosses is opened only by its opening, head at -0.46
    assert not shell.is_solid(h, 1.09, 5.6, -0.47) and shell.is_solid(h, 1.09, 5.6, -0.45) and shell.is_solid(h, 1.09, 6.5, -1.5)
    assert any(abs(c.z + 0.46) < 1e-4 and n.z < -0.9 for o in ('basement.walls', 'basement_stair.walls') for c, n, *_ in faces(o))
    # the main flight opens the wall and the slab above treads 12-14, not the door wall below them
    assert not shell.is_solid(h, 0.57, 7.62, 2.6) and shell.is_solid(h, 0.57, 7.62, 2.2) and shell.is_solid(h, 0.57, 7.80, 2.4)
    # the overhead cupboard is hollow behind its flap (lobby_cupboard_interior), under tread 14
    assert not shell.is_solid(h, 0.57, 8.0, 2.45) and shell.is_solid(h, 0.57, 8.0, 2.62)
    # the loft cabinet's 0.70 m hollow in loft_block; the shower niche; the utility corner boxing
    assert not shell.is_solid(h, 0.78, 6.02, 7.5) and shell.is_solid(h, 0.78, 6.10, 7.5)
    assert not shell.is_solid(h, 1.2, 13.75, 7.33) and shell.is_solid(h, 3.02, 12.10, 8.2)
    assert shell.is_solid(h, 3.0, 12.0, 1.5) and not shell.is_solid(h, 3.0, 12.0, 0.5)
    # the hall ceiling carried over the stair foot (stair_foot zone, also over the cell on the diagonal)
    assert shell.is_solid(h, 0.4, 5.3, 3.0) and shell.is_solid(h, 0.82, 5.22, 3.0) and not shell.is_solid(h, 0.4, 5.7, 3.0)

    # finishes: floors, ceilings, feature tops, split paint, feature walls, risers
    mat = lambda spec: shell.material(spec).name
    assert any(abs(c.z - 0.02) < 1e-4 and n.z > 0.9 and m == mat('hearth_marble') for c, n, m, *_ in faces('dining.walls'))
    assert any(abs(c.z - 1.2) < 1e-4 and n.z > 0.9 and m == mat('marble_metro') for c, n, m, *_ in faces('wc.walls'))
    assert all(m == mat(h.rooms['living']['floor']['material']) and n.z > 0.9 and abs(c.z) < 1e-6 for c, n, m, *_ in faces('living.floor'))
    assert all(n.z < -0.9 and m == mat(shell.FINISHES['kitchen']['ceiling']) for c, n, m, *_ in faces('kitchen.ceiling'))
    assert {round(c.z, 2) for c, *_ in faces('kitchen.ceiling')} == {2.03, 2.95}               # nook soffit zone
    assert {round(c.z, 2) for c, *_ in faces('hallway.ceiling')} == {2.3, 2.6, 2.7, 2.84, 2.95}
    assert any(m == mat('#2B3B4C') and abs(c.x + 0.65) < 1e-4 for c, n, m, *_ in faces('blue_bedroom.walls'))
    assert any(m == mat('metro_carrara_100x400') and z1 <= 3.42 + 1.2 + 1e-4 for c, n, m, z0, z1 in faces('green_bathroom.walls'))
    lo, up = mat(shell.HALL_LOWER), mat('#F1EEE6')             # dado split 0.9425 above the landing floor 3.04
    assert any(m == lo and abs(z1 - 3.9825) < 1e-4 for c, n, m, z0, z1 in faces('landing1_rear.walls'))
    assert any(m == up and abs(z0 - 3.9825) < 1e-4 for c, n, m, z0, z1 in faces('landing1_rear.walls'))
    carpet = mat(h.rooms['landing1_front']['floor']['material'])
    assert any(m == carpet and abs(n.y) > 0.9 and abs(z0 - 3.04) < 1e-4 and abs(z1 - 3.23) < 1e-4
               for c, n, m, z0, z1 in faces('landing1_rear.walls')), 'riser of the two steps'
    assert {round(c.z, 2) for c, *_ in faces('landing1_front.floor')} == {3.23, 3.42}           # the tread is floor
    assert {round(c.z, 2) for c, *_ in faces('eaves_rear.floor')} == {6.37, 6.49}               # floor_step

    # non-axis pieces: chamfers of both kinds, the stops of the four bay splays, haunches, loft slopes
    for n in ('living.chamfer.living_nw_chamfer', 'stairs.chamfer.hall_stair_diag', 'landing1_rear.chamfer.landing1_chamfer',
              'vestibule.haunch.vest_ceiling_slope', 'hallway.arch_fill',
              'landing1_rear.arch_fill', 'landing2_head.arch_fill', 'vestibule.vault_fill'):
        assert n in names, n
    for n, z2 in (('living.chamfer.living_bay.0', 2.4), ('living.chamfer.living_bay.1', 2.4),
                  ('green_bedroom.chamfer.green_bay.0', 5.82), ('green_bedroom.chamfer.green_bay.1', 5.82)):
        zs = [v.co.z for v in ob[n].data.vertices]
        assert abs(max(zs) - z2) < 1e-5 and len(ob[n].data.polygons) == 4, n                    # diagonal + 3 stop faces
    zs = [v.co.z for v in ob['loft_office.ceiling'].data.vertices]
    assert abs(min(zs) - 7.57) < 0.01 and abs(max(zs) - 8.61) < 0.02 + 0.31, (min(zs), max(zs))  # liners reach the roof
    assert all(p.normal.z < 0 for p in ob['loft_office.ceiling'].data.polygons if abs(p.normal.z) > 0.5)
    for o in h.col('shell').objects:                           # nothing above the roof surface
        for v in o.data.vertices:
            rz = shell._roof_at(h, v.co.x, v.co.y)
            assert rz is None or v.co.z <= rz + 1e-3, (o.name, tuple(v.co), rz)

    # flights
    for room, sid, n in (('stairs', 'stair_main', 13), ('basement_stair', 'stair_basement', 10), ('stairs2', 'stair_second', 12)):
        fl = ob[room + '.flight']
        assert fl['part'] == 'flight' and fl['room'] == room
        tops = sorted({round(p.center.z, 3) for p in fl.data.polygons if p.normal.z > 0.99})
        assert tops == sorted(round(t['z'], 3) for t in h.stair(sid)['treads']) and len(tops) == n, (sid, tops)
    under = [p for p in ob['stairs.flight'].data.polygons if p.normal.z < -0.5]
    assert under and min(p.center.z for p in under) >= -1e-6                                    # raked soffit, never below the floor
    assert not any(p.normal.z < -0.5 for p in ob['basement_stair.flight'].data.polygons)         # solid: no soffit
    assert shell.remove('stairs', 'flight') and shell.surface('stairs', 'flight') is None

    # wall_runs: Algorithm C, world Z
    nw, b0, b1 = h.chamfers('living')
    lv = shell.wall_runs(h, 'living', 0.05)
    assert len(lv) == 1 and all(has_run(lv, c['p'], c['q']) for c in (nw, b0, b1)), lv
    sq = shell.wall_runs(h, 'living', 2.3)                    # inside the stop: square arris, diagonal NW wall
    assert has_run(sq, nw['p'], nw['q']) and not has_run(sq, b0['p'], b0['q']) and any(math.dist(r[1], b0['v']) < 1e-4 for r in sq[0])
    assert any(math.dist(r[1], b0['v']) < 1e-4 for r in shell.wall_runs(h, 'living', 2.6)[0])
    (sd,) = h.chamfers('stairs')
    assert has_run(shell.wall_runs(h, 'stairs', 0.05), sd['p'], sd['q'])
    g0, _ = h.chamfers('green_bedroom')
    assert has_run(shell.wall_runs(h, 'green_bedroom', 3.47), g0['p'], g0['q'])
    assert not shell.wall_runs(h, 'green_bedroom', 0.05)      # world Z: nothing of that room at the ground floor
    for rid in ('dining', 'kitchen', 'blue_bedroom', 'study'):
        for loop in shell.wall_runs(h, rid, h.floor_z(rid) + 0.05):
            assert all(math.dist(r[1], loop[(i + 1) % len(loop)][0]) < 1e-6 for i, r in enumerate(loop)), rid   # closed

    # budget
    tris = sum(len(p.vertices) - 2 for o in h.col('shell').objects for p in o.data.polygons)
    assert tris <= 60000, tris

    # fills light their own storey (phase 1 put every fill at Z 2.6)
    for rid in ('green_bedroom', 'loft_office', 'basement', 'stairs2', 'hallway'):
        for l in lighting.fill(h, rid):
            x, y, z = l.location
            assert h.floor_z(rid) + 0.6 < z <= h.ceil_z(rid) - 0.3 and l['level'] == h.level(rid), (rid, z)
    for rid in ('eaves_front', 'eaves_rear'):                  # voids looked into through a hatch: a dim glow inside
        ls = lighting.void_fill(h, rid)
        assert ls and all(h.floor_z(rid) < l.location.z < h.ceil_z(rid, l.location.x, l.location.y) for l in ls), rid

    # review fixes (foundation review, 2026-11-19)
    # the downstand between the loft ceiling planes flat 8.61 / lobby_flat 8.57 is closed, inside the room only
    f = [(c, n) for c, n, *_ in faces('loft_office.ceiling') if abs(n.y) > 0.9 and abs(c.y - 5.38) < 1e-4]
    assert len(f) == 1 and abs(f[0][0].z - 8.59) < 1e-3 and -0.65 < f[0][0].x < 0.31 and f[0][1].y < 0, f
    # the landing chamfer splits at the dado like the walls round it
    ch = faces('landing1_rear.chamfer.landing1_chamfer')
    assert any(m == lo and abs(z1 - 3.9825) < 1e-4 for *_, m, z0, z1 in ch) and any(m == up and abs(z0 - 3.9825) < 1e-4 for *_, m, z0, z1 in ch)
    # the solid basement flight keeps its mass under the square treads (tread 6 at -1.26 over y 6.4..6.6)
    assert shell.is_solid(h, 0.6, 6.5, -1.5) and shell.is_solid(h, 0.6, 7.3, -1.0) and not shell.is_solid(h, 0.6, 6.5, -1.0)
    # shelf and ledge beside the basement shaft (floor_void with `bottom`)
    assert not shell.is_solid(h, 0.2, 6.0, -0.01) and shell.is_solid(h, 0.2, 6.0, -0.05)
    assert not shell.is_solid(h, 0.96, 6.5, -0.4) and shell.is_solid(h, 0.96, 6.5, -0.55) and shell.is_solid(h, 0.96, 7.3, -0.2)
    # quarter vault over the quarter landing, WC duct, pipe boxing with its tiled top
    zs = [v.co.z for v in ob['landing1_ql.cove.ql_vault'].data.vertices]
    assert abs(min(zs) - 4.95) < 1e-5 and abs(max(zs) - 5.35) < 1e-5
    assert shell.is_solid(h, 4.2, 5.4, 5.0) and shell.is_solid(h, 3.04, 12.0, 6.5) and shell.is_solid(h, 3.04, 12.0, 7.5)
    assert any(m == mat('metro_carrara_100x400') and abs(c.x - 4.08) < 1e-4 and z1 > 6.0 for c, n, m, z0, z1 in faces('green_bathroom.walls'))
    # the full-height pipe-boxing column: tiled to the 1.20 dado line, painted above (v5 f_0095)
    box = [(c, m) for c, n, m, *_ in faces('bathroom2.walls') if abs(c.x - 2.98) < 1e-3 and n.x < -0.9 and 11.5 < c.y < 12.16]
    assert any(m == mat('marble_metro') and c.z < 7.22 for c, m in box) and any(m == mat('#B9B7B1') and c.z > 7.22 for c, m in box)
    # thresholds: aluminium nosing at the basement door, a brass strip at every doorway upstairs
    th = {o.name.split('.threshold.')[1]: o.data.materials[0].name for o in h.col('shell').objects if '.threshold.' in o.name}
    assert th['d_basement'] == mat('silver_satin') and th['d_green'] == th['d_loft'] == th['d_study'] == mat('brass') and 'd_balcony' not in th, th
    d = lighting.downlight(h, 'loft_office', 2.0, 3.0)
    assert abs(d.location.z - (6.30 + 0.50 * 3.0 - 0.015)) < 1e-6
    # round 3: the basement riser R9 stops at the pier (x 0.93); stair_second R10 has a back face over the QL; the
    # tile runs through d_wc; the three-centred hall arch rises vertically off the springing; landing1's steps cut
    r9 = [c for c, n, *_ in faces('basement_stair.flight') if abs(n.z) < 0.5 and abs(c.y - 6.0) < 0.01]
    assert r9 and all(c.x < 0.93 for c in r9), r9
    assert any(abs(c.y - 8.131) < 0.002 and n.y > 0.9 for c, n, *_ in faces('stairs2.flight'))
    assert any(abs(c.y - 10.2) < 0.07 and n.z > 0.9 and 1.47 < c.x < 2.08 for c, n, *_ in faces('wc.floor') + faces('utility.floor'))
    # round 3 follow-ups: nothing of the solid basement flight's mass on its riser planes (lib.stairs' risers own them,
    # coplanar pairs render black); each half of an inner door's hole carries its room's floor (d_kitchen: hall oak
    # x 0.99..1.12, kitchen planks beyond); the hall boards register a joint on x -0.52
    assert not [c for c, n, *_ in faces('basement_stair.walls') if abs(n.y) > 0.9 and 0.27 < c.x < 0.92
                and 6.0 - 1e-3 < c.y < 7.4 + 1e-3 and -2.3 < c.z < -0.01], 'riser-plane faces of the solid flight'
    def covers(name, x, y, z=0.0):                             # material of the up-facing face over (x, y, z), or None
        me = ob[name].data
        for p in me.polygons:
            vs = [me.vertices[v].co for v in p.vertices]
            if p.normal.z > 0.9 and abs(vs[0].z - z) < 1e-6 and min(v.x for v in vs) < x < max(v.x for v in vs)                     and min(v.y for v in vs) < y < max(v.y for v in vs):
                return me.materials[p.material_index].name
    assert covers('hallway.floor', 1.05, 8.24) == mat('oak_floor') and covers('kitchen.floor', 1.20, 8.24) == mat('wood_tile_floor')
    assert covers('hallway.walls', 1.05, 8.24) is None and covers('kitchen.walls', 1.20, 8.24) is None
    me = ob['hallway.floor'].data
    w = me.materials[0]['size_m'][0]
    assert all(abs(d.uv.x * w - (me.vertices[me.loops[i].vertex_index].co.x + 0.52)) < 1e-4 for i, d in enumerate(me.uv_layers[0].data))
    arc = shell._three_centred(-0.12, 0.47, 2.40, 2.75, 0.32, 24)(-1)
    assert arc[0] == (-0.59, 2.40) and abs(arc[-1][1] - 2.75) < 1e-9 and arc[1][1] - arc[0][1] > 15 * (arc[1][0] - arc[0][0])
    assert mouldings.steps_skip(h, 'landing1_front') == mouldings.steps_skip(h, 'landing1_rear') and \
        [round(v, 6) for v in mouldings.steps_skip(h, 'landing1_rear')[0]] == [-0.67, 7.88, 0.17, 8.38]
    # round 3 (shell foundation): w_utility's frame (0.70 x 0.98 from 0.92) runs wider and lower behind the plaster of a
    # 0.56 reveal with its board at 1.05 (shell.INNER); the eaves walls reach the lining `offset` under the roof
    # where it is higher than the slab underside (eaves_front -0.17), never lower than the slab underside (eaves_rear)
    assert shell.is_solid(h, 3.2, 11.61, 1.0) and not shell.is_solid(h, 3.2, 11.61, 1.1) and not shell.is_solid(h, 3.4, 11.61, 1.0)
    assert shell.is_solid(h, 3.2, 11.30, 1.5) and not shell.is_solid(h, 3.4, 11.30, 1.5)
    rz = h.roof_z(0.0, 2.0)
    c0, cx, cy = shell._ceil_plane(h, 'eaves_front', 0.0, 2.0)
    assert abs(c0 + cx * 0.0 + cy * 2.0 - (rz - 0.17)) < 1e-6
    c0, cx, cy = shell._ceil_plane(h, 'eaves_rear', 2.0, 7.5)
    assert abs(c0 + cx * 2.0 + cy * 7.5 - h.roof_under(2.0, 7.5)) < 1e-6
    return tris


def subset():
    """--levels 1: mass, rooms, openings and stairs of that level only; every floor is still there."""
    h = fresh(['1'])
    names = {o.name for o in h.col('shell').objects}
    assert all(o['level'] == '1' for o in h.col('shell').objects)
    for rid in h.rooms_on('1'):
        assert h.kind(rid) in ('stairwell', 'exterior') or rid + '.floor' in names, rid
    assert 'stairs2.flight' in names and 'stairs.flight' not in names and 'living.walls' not in names
    assert shell.is_solid(h, 0.57, 8.4, 2.75) and not shell.is_solid(h, 2.5, 3.0, 1.0) and not shell.is_solid(h, 2.5, 3.0, 2.0)


def sky():
    """Re-measure lighting.SKY_ROTATION / SKY_TINT / SKY_STRENGTH against the targets of MULTILEVEL.md section 9."""
    import export_bake as EB
    out = HERE.parent / 'build' / 'core'
    bpy.ops.wm.read_factory_settings(use_empty=True)
    lighting.setup_cycles(64, (128, 64))
    sc = bpy.context.scene
    sc.cycles.use_denoising = False
    Y = np.array([0.2126, 0.7152, 0.0722])

    def exr(cam, name, res, samples):
        sc.camera, sc.cycles.samples = cam, samples
        sc.render.resolution_x, sc.render.resolution_y = res
        sc.render.image_settings.file_format, sc.render.image_settings.color_depth = 'OPEN_EXR', '32'
        sc.render.filepath = str(out / name)
        bpy.ops.render.render(write_still=True)
        px = np.empty(res[0] * res[1] * 4, np.float32)
        bpy.data.images.load(str(out / name)).pixels.foreach_get(px)
        return px.reshape(res[1], res[0], 4)[:, :, :3].astype(np.float64)

    def emitter(name, loc, strength):
        me = bpy.data.meshes.new(name)
        me.from_pydata([(-4, -4, 0), (4, -4, 0), (4, 4, 0), (-4, 4, 0)], [], [(0, 1, 2, 3)])
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        m.node_tree.nodes.clear()
        e, o = m.node_tree.nodes.new('ShaderNodeEmission'), m.node_tree.nodes.new('ShaderNodeOutputMaterial')
        e.inputs['Strength'].default_value = strength
        m.node_tree.links.new(e.outputs[0], o.inputs[0])
        me.materials.append(m)
        ob = bpy.data.objects.new(name, me)
        ob.location = loc
        ob.rotation_euler = (-Vector(loc)).to_track_quat('Z', 'Y').to_euler()
        sc.collection.objects.link(ob)
        return ob
    from mathutils import Vector
    cam = bpy.data.cameras.new('pano')
    cam.type, cam.panorama_type = 'PANO', 'EQUIRECTANGULAR'
    po = bpy.data.objects.new('pano', cam)
    po.rotation_euler = (math.pi / 2, 0, 0)
    sc.collection.objects.link(po)
    lighting.setup_sky(display=False)                         # the LIGHT sky (camera rays see the display sky)
    lum = exr(po, 'sky_pano.exr', (128, 64), 64) @ Y
    bg = next(n for n in sc.world.node_tree.nodes if n.type == 'BACKGROUND')
    bg.inputs['Strength'].default_value = 0
    mk = emitter('marker', tuple(-50 * v for v in lighting.SUN_DIR), 1000)         # where the lamp's sun stands
    mark = exr(po, 'sky_marker.exr', (128, 64), 16) @ Y
    bpy.data.objects.remove(mk)
    my, mx = np.unravel_index(np.argmax(mark), mark.shape)
    by, bx = np.unravel_index(np.argmax(lum), lum.shape)
    off = lambda x: abs(((x - mx) / 128 * 360 + 180) % 360 - 180)
    row = off(int(np.argmax(lum[my])))
    print(f'[sky] brightest sky at the sun elevation: {row:.1f} deg off the lamp azimuth; brightest pixel overall: '
          f'{off(bx):.1f} deg off in azimuth, elevation {(by + 0.5) / 64 * 180 - 90:.1f} (sun {lighting.SUN_ELEVATION})')
    assert row <= 15 and off(bx) <= 15

    lighting.setup_sky()
    me = bpy.data.meshes.new('card')
    me.from_pydata([(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)], [], [(0, 1, 2, 3)])
    m = bpy.data.materials.new('white')
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value, b.inputs['Roughness'].default_value = (1, 1, 1, 1), 1.0
    b.inputs['Specular IOR Level'].default_value = 0.0
    me.materials.append(m)
    sc.collection.objects.link(bpy.data.objects.new('card', me))
    oc = bpy.data.cameras.new('down')
    oc.type, oc.ortho_scale = 'ORTHO', 1.0
    co = bpy.data.objects.new('down', oc)
    co.location = (0, 0, 5)
    sc.collection.objects.link(co)
    raw = exr(co, 'sky_card.exr', (16, 16), 256).reshape(-1, 3).mean(0)
    bal = EB.wb_matrix() @ raw
    print(f'[sky] white card in open shade: raw {raw.round(3)} luminance {raw @ Y:.3f}; after the {lighting.WHITE_BALANCE} K '
          f'balance {bal.round(3)}, blue / red {bal[2] / bal[0]:.2f}')
    assert abs(raw @ Y - 0.72) <= 0.07 and 1.0 <= bal[2] / bal[0] <= 1.25       # MULTILEVEL.md section 9 (integration values)
    assert np.abs(EB.wb_matrix() - np.array(lighting.WB_MATRIX)).max() < 0.01, 'lighting.WB_MATRIX is stale'


try:
    n = whole()
    subset()
    if '--sky' in ARGS:
        sky()
    print(f'SHELL OK ({n} triangles' + (', sky calibration re-measured)' if '--sky' in ARGS else ')'))
except Exception:
    traceback.print_exc()
    sys.exit(1)

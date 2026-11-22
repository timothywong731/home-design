"""Green bathroom (level 1): fittings, sanitaryware, furniture, decor and lights. Spec: spec/rooms/green_bathroom.md
(the "Reconciled dimensions" at its end win: floor Z 3.42, ceiling 2.75, south wall y 4.95, south-keyed items +0.08).

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --levels 1 --only shell,green_bathroom \
         --preview green_bathroom --res 540x960 --samples 64 --tag green_bathroom   [--pose 1 --tag green_bathroom1]

World coords, metres. Room x 1.25..4.30, y 4.95..8.73. W-west x 1.25 (landing door, clock, vanity, shower),
W-north y 8.73 (shower slab, towel rail, window), W-east x 4.30 (WC duct, fan, bath, mirror), W-south y 4.95
(sliding door with its pediment, relief panels, roll holder). Shell: walls, 1.20 tile dado, duct, cove cornice,
doors, window. The lights are switched from the bedroom (green_bedroom.py) and the landing (landing1.py).
"""
import math

import bmesh
from mathutils import Matrix, Vector

from lib import bath, interact as IX, lighting, materials as M, mouldings as mo, props as P, shell
from rooms import green_bathroom_parts as GP

ROOM = 'green_bathroom'
FZ, CZ = 3.42, 6.17
X0, X1, Y0, Y1 = 1.25, 4.30, 4.95, 8.73
E = FZ + 1.5
TILE = 'metro_carrara_100x400'
DX, DY0, DY1 = 4.08, 4.95, 5.87                      # WC duct face and its extent (house.json gbath_duct)
NY0, NY1, ND = 5.16, 5.74, 0.12                      # niches: y range and depth (r3: centred over the pan, v4 f_0108 / f_0162)
WC_Y = 5.45                                          # pan, flush plate and niches share this axis (r3, was 5.41)
SLAB = 'porcelain_calacatta_slab'                    # niche lining: gold-veined slab (v4 f_0108 / f_0162), as the shower
NICHES = ((1.20, 1.50), (1.60, 1.95), (2.02, 2.45))  # z above the floor
CHARCOAL = '#2A2D2E'
RELIEF = (.46, .92)   # B2 / B3 as measured in v4 f_0164 (spec 0.50 x 1.00): tops under the pediment cornice line
BRASS = 'gold_champagne'   # brushed brass: 'brass_antique' rendered copper beside the pale champagne of v4 f_0106 / f_0150

CAMERAS = [
    dict(name='door', pos=(2.7, 5.05, E), look=(2.7, 8.7, FZ + 1.3), fov_deg=100, ref='v4:f_0105'),
    dict(name='bath', pos=(3.05, 5.12, E), look=(3.65, 8.7, FZ + 0.45), fov_deg=110, ref='v4:f_0106'),   # r3: re-solved
    dict(name='duct', pos=(3.1, 5.75, E), look=(4.3, 5.42, FZ + 0.95), fov_deg=100, ref='v4:f_0108'),
    dict(name='window', pos=(3.3, 7.0, E), look=(3.6, 8.8, FZ + 1.0), fov_deg=100, ref='v4:f_0118'),
    dict(name='shower', pos=(3.2, 6.8, E), look=(1.6, 8.4, FZ + 1.3), fov_deg=100, ref='v4:f_0140'),
    dict(name='vanity', pos=(2.8, 6.4, E), look=(1.25, 6.85, FZ + 1.0), fov_deg=100, ref='v4:f_0150'),
    dict(name='cabinet', pos=(2.98, 5.87, E), look=(1.25, 7.0, FZ + 0.95), fov_deg=100, ref='v4:f_0152'),
    dict(name='niches', pos=(3.25, 5.45, FZ + 1.75), look=(4.2, 5.45, FZ + 1.7), fov_deg=75, ref='v4:f_0162'),
    dict(name='south', pos=(2.0, 6.6, E), look=(2.7, 4.95, FZ + 1.6), fov_deg=100, ref='v4:f_0164'),
    dict(name='landing', pos=(1.35, 5.5, E), look=(4.3, 6.6, FZ + 0.8), fov_deg=100, ref='v4:f_0246'),
    dict(name='clock', pos=(2.7, 6.1, E), look=(1.25, 5.45, FZ + 1.9), fov_deg=100, ref='v4:f_0166'),
    # interaction checks (--pose 1): vanity doors, drawer, mirror cabinet, taps; bath filler and WC seat
    dict(name='ix_vanity', pos=(2.7, 6.8, FZ + 1.3), look=(1.4, 6.8, FZ + 0.8), fov_deg=100, ref='v4:f_0150'),
    dict(name='ix_bath', pos=(3.0, 5.75, FZ + 1.45), look=(3.95, 6.3, FZ + 0.45), fov_deg=100, ref='v4:f_0112'),
]


def _add(ctx, ob, kind='fit', sym=None, lm=None):
    return ctx.add(ob, ROOM, kind, plan_sym=sym, lm=lm)


# ----------------------------------------------------------------------------- WC duct: niches cut into the tile
def _duct(ctx):
    """Replace the shell's duct face (x 4.08) by the same tile with three niche holes, line the niches with the
    wall tile and frame them in polished steel; style them (basket, two planted troughs)."""
    ob = shell.surface(ROOM, 'walls')
    mw = ob.matrix_world
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    on = lambda v: abs((mw @ v.co).x - DX) < 1e-4 and DY0 - 1e-4 <= (mw @ v.co).y <= DY1 + 1e-4
    dead = [f for f in bm.faces if all(on(v) for v in f.verts)]
    bmesh.ops.delete(bm, geom=dead, context='FACES')
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()
    print(f'[{ROOM}] duct face: {len(dead)} shell faces replaced by the niche wall')
    face = lambda y0, y1, z0, z1: ([(DX, y0, z0), (DX, y1, z0), (DX, y1, z1), (DX, y0, z1)], (DX - 1, (y0 + y1) / 2, z0), TILE)
    zs = [FZ] + [FZ + z for zz in NICHES for z in zz] + [CZ]
    faces = [face(DY0, NY0, FZ, CZ), face(NY1, DY1, FZ, CZ)]
    faces += [face(NY0, NY1, zs[i], zs[i + 1]) for i in range(0, len(zs), 2)]
    xb, yc = DX + ND, (NY0 + NY1) / 2
    for z0, z1 in NICHES:
        z0, z1 = FZ + z0, FZ + z1
        zc = (z0 + z1) / 2
        faces += [([(xb, NY0, z0), (xb, NY1, z0), (xb, NY1, z1), (xb, NY0, z1)], (DX, yc, zc), SLAB),
                  ([(DX, NY0, z0), (xb, NY0, z0), (xb, NY0, z1), (DX, NY0, z1)], (DX + .06, yc, zc), SLAB),
                  ([(DX, NY1, z0), (xb, NY1, z0), (xb, NY1, z1), (DX, NY1, z1)], (DX + .06, yc, zc), SLAB),
                  ([(DX, NY0, z0), (xb, NY0, z0), (xb, NY1, z0), (DX, NY1, z0)], (DX + .06, yc, zc), SLAB),
                  ([(DX, NY0, z1), (xb, NY0, z1), (xb, NY1, z1), (DX, NY1, z1)], (DX + .06, yc, zc), SLAB)]
    _add(ctx, shell.faces_object(f'{ROOM}.duct', faces))
    mb = mo.MB()                                                        # polished steel edge trim, 9 mm, 3 mm proud
    t, xa = .009, DX - .0035
    for z0, z1 in NICHES:
        z0, z1 = FZ + z0, FZ + z1
        for a, b in (((xa, NY0 - t, z0 - t), (DX + .012, NY0 + .001, z1 + t)),   # inner faces 1 mm off the lining
                     ((xa, NY1 - .001, z0 - t), (DX + .012, NY1 + t, z1 + t)),
                     ((xa, NY0, z0 - t), (DX + .012, NY1, z0 + .001)), ((xa, NY0, z1 - .001), (DX + .012, NY1, z1 + t))):
            mb.box(a, b, 'chrome')        # 'steel_brushed' texture + normal map speckles at 9 mm (v4 f_0108: bright edge)
    _add(ctx, mb.finish(f'{ROOM}.duct_trim'))
    # niche styling (v4 f_0108 / f_0162): a lidded rattan box at the north end of the lowest niche, a pale wooden
    # dough bowl of succulents in the middle one and one of three bun-moss clumps in the top one
    mb = mo.MB()
    rattan, dark = M.solid('gbath_rattan', '#B9975F', .85), M.solid('gbath_rattan_dk', '#8A6A43', .9)
    z, (xa, xb, ya, yb) = FZ + NICHES[0][0], (DX + .012, DX + .112, NY1 - .150, NY1 - .012)
    mb.box((xa, ya, z), (xb, yb, z + .098), rattan, bev=.004)
    for k in range(11):                                                             # woven weft rows
        mb.box((xa - .001, ya - .001, z + .006 + .0078 * k), (xb + .001, yb + .001, z + .0095 + .0078 * k), dark)
    mb.box((xa - .004, ya - .004, z + .098), (xb + .004, yb + .004, z + .114), rattan, bev=.004)   # lid
    mb.box((xa - .0045, (ya + yb) / 2 - .025, z + .080), (xa - .002, (ya + yb) / 2 + .025, z + .094), dark, bev=.002)  # grip
    _add(ctx, mb.finish(f'{ROOM}.niche_basket'), 'decor')
    yc, xc = (NY0 + NY1) / 2, DX + .064
    bowl = GP.dough_bowl(f'{ROOM}.niche_bowl.0')
    for k, zz in enumerate((NICHES[1][0], NICHES[2][0])):
        b = bowl if k == 0 else GP.share(bowl, f'{ROOM}.niche_bowl.{k}')
        b.location = (xc, yc, FZ + zz)
        _add(ctx, b, 'decor')
    z = FZ + NICHES[1][0]
    spots = [(xc + (.006 if k % 2 else -.012), yc - .165 + .0471 * k, z + .062 + .005 * (k % 2), .088 + .010 * (k % 3))
             for k in range(8)]
    sc = GP.succulents(f'{ROOM}.niche_succulents', spots)
    _add(ctx, sc, 'decor')
    mb = mo.MB()                                                                    # soil in the two bowls
    for zz in (NICHES[1][0], NICHES[2][0]):
        mb.at(Matrix.Translation((xc, yc, FZ + zz + .040)))
        mb.dome(.037, .202, .026, P.mat('soil'), segs=16, rings=2)
    mb.at()
    _add(ctx, mb.finish(f'{ROOM}.niche_soil'), 'decor')
    z = FZ + NICHES[2][0] + .040
    _add(ctx, GP.moss_mounds(f'{ROOM}.niche_moss', [(xc, yc - .14, z, .058), (xc - .004, yc, z + .004, .066),
                                                     (xc + .003, yc + .14, z, .056)]), 'decor')


# ----------------------------------------------------------------------------- double vanity + mirror cabinet
UNITS = ((6.10, 6.70, 'cab'), (6.70, 6.95, 'mid'), (6.95, 7.55, 'cab'))
VX, VD, VZ0, VZ1 = 1.25, 0.43, 0.10, 0.80          # wall, carcass depth, carcass bottom / top above the floor


def _door(ctx, name, yc, w, z0, h, hinge_y, deg, handle, label='Cupboard'):
    """Lay-on beaded panel door on the carcass front x = VX + VD, hinged on the vertical edge at hinge_y."""
    xf = VX + VD
    paint = M.paint(CHARCOAL, .45)
    d = P.place(P.panel_door(w, h, t=.02, stile=.052, recess=.004, bead=.008, mat=paint, name=name), (xf, yc, FZ + z0), facing=(1, 0))
    parts = [d]
    if handle:
        hy, hz, kind = handle
        hd = P.handle_d(length=.09, dia=.008, projection=.022, finish='bronze_dark', vertical=True, name=name + '.pull') \
            if kind == 'bow' else P.handle_knob(dia=.026, projection=.024, finish='bronze_dark', name=name + '.pull')
        parts.append(P.place(hd, (xf + .02, hy, FZ + hz), facing=(1, 0)))
    IX.tag_many(parts, 'hinge', g=name, label=label, p=(xf + .02, hinge_y, FZ + z0), deg=deg)
    for o in parts:
        _add(ctx, o, lm='dynamic')
    return parts


def _vanity(ctx):
    paint = M.paint(CHARCOAL, .45)
    inner = '#E4E2DC'
    yc0 = (UNITS[0][0] + UNITS[-1][1]) / 2
    mb = mo.MB()                                                        # legs: local props frame, x along the wall
    for ya, yb, _ in UNITS:
        xa, xb = ya - yc0, yb - yc0
        for x0 in (xa + .002, xb - .042):
            for y0 in (-.002, -VD + .040):
                mb.box((x0, y0 - .040, 0), (x0 + .040, y0, VZ0 + .002), paint, bev=.002)
        mb.box((xa + .002, -VD, VZ0 - .022), (xb - .002, -VD + .02, VZ0 + .002), paint, bev=.002)   # bottom rail
    legs = P.place(mb.finish(f'{ROOM}.vanity'), (VX, yc0, FZ), facing=(1, 0))
    _add(ctx, legs, sym='vanity')
    mb = mo.MB()                       # tongue-and-groove end panels: dark V-joints on both exposed sides (v4 f_0152)
    groove = M.paint('#17191A', .6)
    for y, s in ((UNITS[0][0] + .001, -1), (UNITS[-1][1] - .001, 1)):
        for x in (VX + .10, VX + .185, VX + .27, VX + .355):
            y0, y1 = sorted((y, y + s * .0012))
            mb.box((x - .003, y0, FZ + VZ0 + .05), (x + .003, y1, FZ + VZ1 - .05), groove)
    _add(ctx, mb.finish(f'{ROOM}.vanity.grooves'))
    xf, g = VX + VD, .004
    for k, (ya, yb, kind) in enumerate(UNITS):
        yc, w = (ya + yb) / 2, yb - ya
        car = P.cabinet_carcass(w - .002, VD, VZ1 - VZ0, paint, plinth=0, open_front=True,
                                shelves=1 if kind == 'cab' else 0, inner=inner, name=f'{ROOM}.vanity.{k}')
        _add(ctx, P.place(car, (VX, yc, FZ + VZ0), facing=(1, 0)))
        if kind == 'cab':
            dw = (w - 3 * g) / 2
            _door(ctx, f'{ROOM}.vanity.{k}.door.l', ya + g + dw / 2, dw, .125, .655, ya + g, -90, (ya + g + dw - .035, .66, 'bow'))
            _door(ctx, f'{ROOM}.vanity.{k}.door.r', yb - g - dw / 2, dw, .125, .655, yb - g, 90, (yb - g - dw + .035, .66, 'bow'))
        else:
            dw = w - 2 * g
            # hinged north, pull on the south stile (v4 f_0150); 80 deg: at 90 its pull meets the open vanity.2.door.l
            _door(ctx, f'{ROOM}.vanity.{k}.door', yc, dw, .125, .50, yb - g, 80, (ya + g + .035, .54, 'bow'))
            mb = mo.MB()                                                    # divider + drawer box (moves with the front)
            mb.box((VX + .02, ya + .018, FZ + .626), (xf, yb - .018, FZ + .644), paint)
            div = mb.finish(f'{ROOM}.vanity.{k}.divider')
            _add(ctx, div)
            name = f'{ROOM}.vanity.{k}.drawer'
            fr = P.place(P.panel_door(dw, .13, t=.02, slab=True, mat=paint, name=name), (xf, yc, FZ + .648), facing=(1, 0))
            kb = P.place(P.handle_cup(width=.07, height=.03, projection=.022, finish='bronze_dark', name=name + '.pull'),
                         (xf + .02, yc, FZ + .697), facing=(1, 0))
            mb = mo.MB()
            y0, y1, z0, z1, x0 = ya + .022, yb - .022, FZ + .655, FZ + .765, VX + .04
            pale = M.paint(inner, .6)
            mb.box((x0, y0, z0), (xf, y1, z0 + .012), pale)
            mb.box((x0, y0, z0), (x0 + .012, y1, z1), pale)
            mb.box((x0, y0, z0), (xf, y0 + .012, z1), pale)
            mb.box((x0, y1 - .012, z0), (xf, y1, z1), pale)
            box = mb.finish(name + '.box')
            IX.tag_many([fr, kb, box], 'slide', g=name, label='Drawer', d=(.30, 0, 0))
            for o in (fr, kb, box):
                _add(ctx, o, lm='dynamic')
            top = shell.box(f'{ROOM}.vanity.top', VX, xf + .03, ya, yb, FZ + VZ1, FZ + VZ1 + .02, 'black_gloss')
            _add(ctx, top)
    # basins (one mesh) and their brushed-brass pin mixers
    b0 = None
    for k, yc in enumerate((6.40, 7.25)):
        b = GP.basin(f'{ROOM}.basin.{k}') if b0 is None else GP.share(b0, f'{ROOM}.basin.{k}')
        if b0 is not None:
            w = GP.share(b0.children[0], f'{ROOM}.basin.{k}.waste')
            w.parent = b
        b0 = b0 or b
        _add(ctx, P.place(b, (1.28, yc, FZ + VZ1), facing=(1, 0)))
        tx = 1.28 - GP.BASIN_TAP[1]
        bath.add(ctx, ROOM, bath.basin_mixer(f'{ROOM}.tap.{"sn"[k]}', (tx, yc, FZ + VZ1 + GP.BASIN_TAP[2]),
                                             FZ + VZ1 + GP.BASIN_FLOOR + .002, facing=(1, 0), style='pin',
                                             finish=BRASS))
    # brushed-brass tumbler ring and soap dish on the tile, north of each tap (v4 f_0150)
    for k, (y, kind) in enumerate(((6.58, 'tumbler'), (7.43, 'dish'))):
        _add(ctx, P.place(GP.wall_dish(f'{ROOM}.wall_{kind}', kind), (X0, y, FZ + 1.06), facing=(1, 0)), 'decor')
    # mirror cabinet: mid-grey carcass, three mirrored doors, z 1.24..1.96; r3: 1.40 long, 0.15 deep (v4 f_0152 re-solved:
    # the north end stops 0.08 short of the shower slab, the south end over the vanity's). Carcass side and bottom edge
    # read 0.63-0.65 x the wall in f_0150 / f_0152 (side in shade): mid grey, inside stays pale
    grey = M.paint('#8E908C', .4)
    y0, y1, z0, h, d = 6.22, 7.62, 1.24, .72, .15
    car = P.cabinet_carcass(y1 - y0, d, h, grey, plinth=0, open_front=True, shelves=2, inner='#F1F1EE',
                            name=f'{ROOM}.mirror_cabinet')
    _add(ctx, P.place(car, (VX, (y0 + y1) / 2, FZ + z0), facing=(1, 0)), sym='wall_unit')
    dw, xf = (y1 - y0 - .006) / 3, VX + d
    mb = mo.MB()
    mb.box((-dw / 2, -.018, 0), (dw / 2, 0, h - .004), grey, bev=.0015)
    mb.face([(-dw / 2 + .002, -.0185, .002), (dw / 2 - .002, -.0185, .002), (dw / 2 - .002, -.0185, h - .006),
             (-dw / 2 + .002, -.0185, h - .006)], 'mirror', hint=(0, -1, 0))
    dm = mb.finish(f'{ROOM}.mirror_cabinet.door.0')
    for k, (hy, deg) in enumerate(((y0 + .001, -90), (y0 + .003 + dw, -90), (y1 - .001, 90))):
        dr = dm if k == 0 else GP.share(dm, f'{ROOM}.mirror_cabinet.door.{k}')
        P.place(dr, (xf, y0 + .002 + dw / 2 + k * (dw + .001), FZ + z0 + .002), facing=(1, 0))
        IX.tag(dr, 'hinge', g=dr.name, label='Mirror cabinet', p=(xf + .018, hy, FZ + z0), deg=deg)
        _add(ctx, dr, lm='dynamic')


# ----------------------------------------------------------------------------- shower
def _shower(ctx):
    tray_top = FZ + .04
    sx, ny = X0 + .008, Y1 - .008                                       # slab faces (8 mm porcelain slabs)
    for name, a in (('w', (X0, sx, 7.70, Y1)), ('n', (sx, 2.72, ny, Y1))):
        ob = shell.box(f'{ROOM}.slab.{name}', *a, FZ, FZ + 2.48, 'porcelain_calacatta_slab')
        M.uv_box(ob, origin=(X0, 7.70, tray_top))
        _add(ctx, ob)
    mb = mo.MB()
    mb.box((sx, 7.83, FZ), (2.65, ny, tray_top), M.solid('gbath_tray', '#F1F0EB', .45), bev=.004)
    mb.box((1.95, 8.615, tray_top - .003), (2.15, 8.64, tray_top + .0006), 'steel_brushed')
    mb.box((1.955, 8.621, tray_top - .002), (2.145, 8.634, tray_top + .0008), 'black_matt')
    _add(ctx, mb.finish(f'{ROOM}.shower_tray'), sym='shower')
    bath.add(ctx, ROOM, bath.shower_set(f'{ROOM}.shower', (sx, 8.30, FZ), facing=(1, 0)))
    w = 2.65 - sx
    bath.add(ctx, ROOM, bath.shower_slider(f'{ROOM}.screen', (sx + w / 2, 7.83, tray_top), w, facing=(0, -1), door='right',
                                           rail='round', rail_z=1.89, height=1.95))
    ret = P.place(bath.glass_pane(ny - 7.83, 1.95, channel='right', name=f'{ROOM}.screen.return'),
                  (2.65, (7.83 + ny) / 2, tray_top), rot_z=90)
    _add(ctx, ret)


# ----------------------------------------------------------------------------- bath + filler
def _bath(ctx):
    cx, cy = 3.78, 6.925
    tub = P.place(GP.slipper_bath(f'{ROOM}.bath'), (cx, cy, FZ), rot_z=90)
    _add(ctx, tub, sym='bath')
    # ball-and-claw feet pointing out on the diagonals, leg top buried in the tub's belly (v4 f_0106 / f_0112)
    leg = GP.claw_foot(f'{ROOM}.bath.foot.0', BRASS)
    for k, (dx, dy) in enumerate(((1, 1), (1, -1), (-1, 1), (-1, -1))):
        f = leg if k == 0 else GP.share(leg, f'{ROOM}.bath.foot.{k}')
        f.location = (cx + .21 * dx, cy + .56 * dy, FZ)
        f.rotation_euler = (0, 0, math.atan2(dy, dx))
        _add(ctx, f)
    bath.add(ctx, ROOM, bath.bath_filler(f'{ROOM}.filler', (3.88, 6.00, FZ), FZ + .225, facing=(0, 1), reach=.30,
                                         finish=BRASS), plan_sym='pipe')      # round post: drawn, solid for the walker
    mb = mo.MB()                                                        # small white wall shelf with a candle
    mb.box((X1 - .10, 7.20, FZ + .83), (X1 - .001, 7.50, FZ + .85), 'white_gloss', bev=.003)
    mb.at(Matrix.Translation((X1 - .05, 7.38, FZ + .85)))
    mb.lathe([(0, 0), (.034, 0), (.034, .075), (.030, .078), (0, .078)], M.solid('gbath_wax', '#EFEBE1', .6), 16)
    mb.at()
    _add(ctx, mb.finish(f'{ROOM}.bath_shelf'), 'decor')


# ----------------------------------------------------------------------------- window sill, reveal tiles
def _window(ctx):
    fr = ctx.opening_frame('w_gbath')
    xa, xb = fr['center'].x - fr['width'] / 2, fr['center'].x + fr['width'] / 2
    zs = fr['center'].z                                                # world z of the sill (hole bottom)
    yf = Y1 + .20                                                      # frame inner face (0.20 reveal)
    ob = shell.box(f'{ROOM}.window_sill', xa - .03, min(xb + .03, X1 - .001), Y1 - .03, yf - .002, zs - .025, zs + .002,
                   'white_gloss')                                      # east horn stops at the east wall (r3 window move)
    _add(ctx, ob)
    for x0, x1 in ((xa, xa + .002), (xb - .002, xb)):
        t = shell.box(f'{ROOM}.reveal_tile.{int(x0 * 100)}', x0, x1, Y1, yf - .002, zs + .002, FZ + 1.20, TILE)
        _add(ctx, t)
    return zs + .002


def build(ctx):
    _duct(ctx)
    _vanity(ctx)
    _shower(ctx)
    _bath(ctx)
    sill = _window(ctx)

    bath.add(ctx, ROOM, bath.wc(f'{ROOM}.wc', (DX, WC_Y, FZ), facing=(-1, 0), flush_z=1.02), plan_sym='wc')
    rail = P.place(bath.towel_rail(.6, 1.6, name=f'{ROOM}.towel_rail'), (3.07, Y1, FZ + .25), facing=(0, -1))  # r3: v4 f_0105
    _add(ctx, rail, sym='towel_rail')
    _add(ctx, P.place(GP.roll_holder(f'{ROOM}.roll_holder'), (3.85, Y0, FZ + .72), facing=(0, 1)))
    _add(ctx, P.place(GP.brush_holder(f'{ROOM}.brush_holder'), (DX, 5.19, FZ), facing=(-1, 0)))   # beside the pan
    _add(ctx, P.place(GP.fan(f'{ROOM}.fan'), (X1, 6.03, FZ + 2.45), facing=(-1, 0)))

    # art, mirror, clock, plants
    _add(ctx, P.place(P.mirror_framed(1.0, .42, 'gilt_swept', frame_w=.06, name=f'{ROOM}.mirror'), (X1, 6.95, FZ + 1.57),
                      facing=(-1, 0)), 'decor', sym='mirror')
    # B2 / B3 at z 1.32..2.24, about 0.22 clear of the pediment consoles as in v4 f_0164 (not the spec x 3.60 / 1.75)
    for k, (x, flip) in enumerate(((3.70, False), (1.67, True)), 1):
        _add(ctx, P.place(GP.relief_panel(f'{ROOM}.relief.{k}', flip=flip, size=RELIEF), (x, Y0, FZ + 1.78),
                          facing=(0, 1)), 'decor')
    ck = P.place(GP.wall_clock(f'{ROOM}.clock'), (X0, 5.51, FZ + 2.38), facing=(1, 0))
    centre = ck.matrix_basis @ Vector((0, -GP.CLOCK_FACE, 0))
    for hand, w in zip(P.clock_hands(.128, 'baton', name=f'{ROOM}.clock'), 'hm'):
        P.place(hand, centre, facing=(1, 0))
        IX.tag(hand, 'clock', hand=w, p=tuple(centre), a=(1, 0, 0))
        _add(ctx, hand, 'decor', lm='dynamic')
    _add(ctx, ck, 'decor')
    _add(ctx, P.place(GP.fern(f'{ROOM}.fern'), (1.52, 6.825, FZ + VZ1 + .02)), 'decor')
    # ponytail: fronds toward the wall are the upright kind (no wall test per frond)
    lily = P.place(GP.peace_lily(f'{ROOM}.lily'), (3.80, 8.82, sill))
    assert max((lily.matrix_basis @ v.co).y for v in lily.data.vertices) < Y1 + .19, 'lily reaches the window frame'
    _add(ctx, lily, 'decor')
    # two cotton bath mats: grey ground, a pale band 50 mm in, grey field (v4 f_0105 / f_0118)
    for k, (x, y, w, d) in enumerate(((2.20, 7.45, .80, .50), (3.05, 7.00, .50, .80))):
        mat = P.place(P.rug(w=w, d=d, thickness=.012, corner_r=.03, color='#A4A39F', name=f'{ROOM}.mat.{k}'), (x, y, FZ))
        _add(ctx, mat, 'decor', sym='rug')
        for i, (ins, t, col) in enumerate(((.05, .0135, '#D3D1CB'), (.08, .015, '#A8A7A3'))):
            pile = P.rug(w=w - 2 * ins, d=d - 2 * ins, thickness=t, corner_r=.02, color=col, name=f'{ROOM}.mat.{k}.{i}')
            _add(ctx, P.place(pile, (x, y, FZ)), 'decor')

    # six recessed downlights, neutral white (no switch in the room: bedroom + landing plates, other modules)
    for i, (x, y) in enumerate((x, y) for y in (5.68, 6.88, 8.08) for x in (2.05, 3.55)):
        lighting.downlight(ctx, ROOM, x, y, watts=70, kelvin=3300, spot_deg=140, name=f'{ROOM}.downlight.{i}')
        _add(ctx, P.place(P.downlight(name=f'{ROOM}.downlight_trim.{i}'), (x, y, CZ)), 'light')

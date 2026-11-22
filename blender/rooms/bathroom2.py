"""bathroom2 - second-floor bathroom: shower, free-standing sauna, vanity, WC unit, tall cabinet (spec/rooms/bathroom2.md).

Round 3 (spec/phase3/briefs/bathroom2.md): room x 0.42..3.10, y 11.66..13.70 (2.68 x 2.04), floor Z 6.02, ceiling 8.49.
Every fitting is placed in the survey's local frame (origin = the room's SW inside corner, read from ctx) off the v13
floor-tile lattice (spec/phase3/floor2_a.md, "Bathroom"): door clear y 0.05..0.74, towel radiator x 0.76..1.29, vanity
1.33..1.92 (plinth 0.30 deep, basin to 0.45), WC unit 1.92..2.35 (pan front y 0.69), tall cabinet from 2.35, window
reveal y 0.59..1.23, slab lining x 0..0.05, tray x 0.05..1.19, y 1.28..2.04, 0.07 strip, sauna x 1.254..2.62, y 1.23..1.98
(rooms/bathroom2_sauna.py), bath mat x 0.31..1.22, y 0.73..1.26. The light switch for the four spots is landing2's S3.
"""
import os
import random
from math import cos, sin, radians

from lib import bath, interact as IX, lighting, materials as M, mouldings as mo, props as P, shell
from rooms import bathroom2_sauna as SA, bathroom2_tex as TX

ROOM = 'bathroom2'
X0, X1, Y0, Y1 = 0.42, 3.10, 11.66, 13.70          # replaced from ctx in build()
FZ, CZ = 6.02, 8.49
WY0, WY1 = 12.25, 12.89                             # window reveal (w_bath2)
DOWN_W = 55                                         # per downlight (4 in 5.5 m2)
ART = os.path.join(os.path.dirname(__file__), '..', 'textures', 'art', 'bathroom2_watercolour.jpg')

CAMERAS = [
    dict(name='door', pos=(0.55, 12.05, 7.52), look=(3.10, 12.55, 7.02), fov_deg=100, ref='v13:f_0109'),
    dict(name='shower', pos=(1.25, 12.35, 7.50), look=(0.60, 13.70, 7.10), fov_deg=100, ref='v13:f_0057'),
    dict(name='showerin', pos=(1.10, 12.75, 7.62), look=(0.48, 13.35, 6.70), fov_deg=100, ref='v13:f_0113'),
    dict(name='sauna', pos=(2.15, 12.20, 7.45), look=(2.50, 13.70, 7.05), fov_deg=100, ref='v13:f_0077'),
    dict(name='saunain', pos=(2.10, 13.10, 7.45), look=(2.95, 13.35, 6.55), fov_deg=100, ref='v13:f_0087'),
    dict(name='heater', pos=(2.55, 13.05, 7.35), look=(1.80, 13.30, 6.45), fov_deg=100, ref='v13:f_0089'),
    dict(name='saunafront', pos=(2.30, 13.45, 7.30), look=(2.70, 12.90, 7.55), fov_deg=100, ref='v13:f_0097'),
    dict(name='window', pos=(1.90, 12.55, 7.45), look=(3.10, 12.45, 7.05), fov_deg=100, ref='v13:f_0071'),
    dict(name='tallcab', pos=(2.20, 12.70, 7.45), look=(2.95, 11.85, 6.90), fov_deg=100, ref='v13:f_0073'),
    dict(name='south', pos=(1.95, 12.80, 7.55), look=(2.05, 11.66, 6.95), fov_deg=100, ref='v13:f_0105'),
    dict(name='doorwall', pos=(2.30, 12.60, 7.45), look=(0.42, 12.10, 7.05), fov_deg=100, ref='v13:f_0117'),
]


def z(h):
    return FZ + h


def _mb_add(ctx, mb, name, kind='fit', plan_sym=None, lm=None):
    return ctx.add(mb.finish(name), ROOM, kind, plan_sym=plan_sym, lm=lm)


def grooved(mb, lo, hi, n, axis, mat, bev=.0025):
    """Board split along `axis` (0 = x, 1 = y, 2 = z) into n planks with chamfered edges = V-grooves."""
    a, b = lo[axis], hi[axis]
    for i in range(n):
        p, q = list(lo), list(hi)
        p[axis], q[axis] = a + (b - a) * i / n, a + (b - a) * (i + 1) / n
        mb.box(tuple(p), tuple(q), mat, bev=bev, grain=2)


def _bounds(poly):
    xs, ys = zip(*poly)
    return min(xs), max(xs), min(ys), max(ys)


def build(ctx):
    global X0, X1, Y0, Y1, FZ, CZ, WY0, WY1, PLANT_X, PLANT_Y
    X0, X1, Y0, Y1 = _bounds(ctx.room_poly(ROOM))
    FZ, CZ = ctx.floor_z(ROOM), ctx.ceil_z(ROOM)
    wf = ctx.opening_frame('w_bath2')
    WY0, WY1 = wf['center'].y - wf['width'] / 2, wf['center'].y + wf['width'] / 2
    lx0, XL, YL, _ = _bounds(ctx.feature('bath2_shower_lining')['polygon'])     # slab lining x 0.42..0.47 from 12.48
    XB, _, YB0, YB1 = _bounds(ctx.feature('bath2_pipe_boxing')['polygon'])      # column x 2.98..3.10, y 11.66..12.25
    nx0, nx1, _, _ = _bounds(ctx.feature('bath2_niche')['polygon'])
    nz0, nz1 = ctx.feature('bath2_niche')['z']
    furn = M.paint('#DAD8D0', 0.45)          # satin painted shaker furniture (vanity, WC unit, tall cabinet)
    inner = M.paint('#F2F1EC', 0.5)
    top = CZ - .08                           # cornice underside

    # ---------------------------------------------------------------- shell coverings
    # wall paint cooler than phase 2: #BBC0C0 against the white ceiling in daylight (v13 t77) -> #B5B8B8
    shell.repaint(ROOM, '#B9B7B1', '#B5B8B8')

    def slab(name, x0, x1, y0, y1, z0, z1):
        ob = shell.box(name, x0, x1, y0, y1, z0, z1, 'porcelain_calacatta_slab')
        M.uv_box(ob, origin=(X0, Y1, FZ))
        return ctx.add(ob, ROOM, 'fit')

    # shower walls: Calacatta slabs to the cornice, 10 mm on the slab lining (its face x 0.47, mitred end by the door
    # architrave, v13 t108.5) and on the north wall as far as the glass return
    xs = XL + .01                                                        # slab face on the lining
    xr = X0 + 1.19                                                       # tray / glass return (local 1.19)
    slab(f'{ROOM}.slab.w', XL, xs, YL, Y1 - .01, FZ, top)
    slab(f'{ROOM}.slab.end', lx0, xs, YL - .01, YL, FZ, top)             # the lining's south end, beside the architrave
    yn = Y1 - .01
    slab(f'{ROOM}.slab.n0', XL, xr + .02, yn, Y1, FZ, nz0)
    slab(f'{ROOM}.slab.n1', XL, xr + .02, yn, Y1, nz1, top)
    slab(f'{ROOM}.slab.n2', XL, nx0, yn, Y1, nz0, nz1)
    slab(f'{ROOM}.slab.n3', nx1, xr + .02, yn, Y1, nz0, nz1)
    back, bt = Y1 + .10, .01                                             # the recess: house.json bath2_niche
    yb = back - bt
    slab(f'{ROOM}.niche.back', nx0, nx1, yb, back, nz0, nz1)
    slab(f'{ROOM}.niche.bottom', nx0, nx1, yn, yb, nz0, nz0 + .01)
    slab(f'{ROOM}.niche.top', nx0, nx1, yn, yb, nz1 - .01, nz1)
    slab(f'{ROOM}.niche.l', nx0, nx0 + .01, yn, yb, nz0 + .01, nz1 - .01)
    slab(f'{ROOM}.niche.r', nx1 - .01, nx1, yn, yb, nz0 + .01, nz1 - .01)
    mb = mo.MB()                                                         # polished steel frame round it (v13 t111)
    for a, b in (((nx0 - .012, yn - .004, nz0 - .012), (nx1 + .012, yn, nz0)),
                 ((nx0 - .012, yn - .004, nz1), (nx1 + .012, yn, nz1 + .012)),
                 ((nx0 - .012, yn - .004, nz0), (nx0, yn, nz1)), ((nx1, yn - .004, nz0), (nx1 + .012, yn, nz1))):
        mb.box(a, b, 'chrome', bev=.001)
    _mb_add(ctx, mb, f'{ROOM}.niche.trim')

    # window: white quartz sill 30 mm with a rounded nose 30 mm proud, horn past the north jamb only (the south jamb is
    # flush with the boxing's north face); marble metro returns on both jambs from the sill to the 1.20 dado (v13 t73)
    fx = wf['center'].x + wf['wall_thickness'] / 2 - wf['ext_reveal'] - .06   # inside face of the frame (3.33)
    mb = mo.MB()
    sill = M.solid('bathroom2_sill', '#F1F0EC', 0.3)
    mb.box((X1 - .002, WY0, z(.80)), (fx, WY1, z(.83)), sill)
    mb.box((X1 - .03, WY0 + .001, z(.80)), (X1, WY1 + .02, z(.83)), sill, bev=.008)
    _mb_add(ctx, mb, f'{ROOM}.sill')
    for k, (y0, y1) in enumerate(((WY0, WY0 + .003), (WY1 - .003, WY1))):
        ob = shell.box(f'{ROOM}.jamb_tile.{k}', X1, fx, y0, y1, z(.83), z(1.20), 'marble_metro')
        M.uv_box(ob, origin=(X1, 0, z(1.20)))
        ctx.add(ob, ROOM, 'fit')

    # chrome-look trim on top of the metro dado (1.20) and down the external corners
    mb = mo.MB()
    t0, t1, e = z(1.195), z(1.207), .006
    xc0 = X0 + 2.35                                                      # tall cabinet's west side
    for a, b in (((X0 + .025, Y0, t0), (xc0, Y0 + e, t1)),               # south wall (door architrave -> tall cabinet)
                 ((XB - e, Y0 + .30, t0), (XB, YB1 + e, t1)),            # boxing W face (N of the cabinet)
                 ((XB - e, YB1, t0), (X1, YB1 + e, t1)),                 # boxing N face
                 ((X1, WY0, t0), (fx, WY0 + .006, t1)),                  # south jamb
                 ((X1, WY1 - .006, t0), (fx, WY1, t1)),                  # north jamb
                 ((X1 - e, WY1, t0), (X1, Y1, t1)),                      # E wall N of the window (behind the sauna)
                 ((xr + .02, Y1 - e, t0), (X1, Y1, t1)),                 # N wall behind the sauna
                 ((XB - .008, YB1, FZ), (XB, YB1 + .008, t1)),           # boxing corner (v5 f_0099)
                 ((X1 - .008, WY1, z(.83)), (X1, WY1 + .008, t1))):      # north jamb corner
        mb.box(a, b, 'silver_satin', bev=.0015)
    _mb_add(ctx, mb, f'{ROOM}.tile_trim', kind='trim')

    # ---------------------------------------------------------------- shower (NW corner): tray 1.14 x 0.76
    ty0 = Y0 + 1.28
    tray_m = M.solid('bathroom2_tray', '#F2F1EE', 0.35)
    mb = mo.MB()
    mb.box((xs, ty0, FZ), (xr, Y1 - .01, z(.04)), tray_m, bev=.005)
    _mb_add(ctx, mb, f'{ROOM}.shower.tray', plan_sym='shower')
    yc = (ty0 + Y1) / 2
    ctx.add(P.place(P.lathe([(0, 0), (.045, 0), (.045, .002), (.03, .003), (0, .003)], 20, 'chrome',
                            name=f'{ROOM}.shower.waste'), (xs + .22, yc, z(.04))), ROOM, 'fit')
    bath.add(ctx, ROOM, bath.shower_set(f'{ROOM}.shower', (xs, yc, FZ), (1, 0), to_z=z(.04), valve_z=1.10, head_z=2.10,
                                        reach=.38, head_dia=.28, basket_z=1.25))
    ff = ty0 + .02                                                       # front: door pane over the tray edge
    bath.add(ctx, ROOM, bath.shower_slider(f'{ROOM}.screen', ((xs + xr - .01) / 2, ff, z(.04)), xr - .01 - xs, (0, -1),
                                           height=1.95, door='left', rail='round', rail_z=1.93, handle_z=1.06,
                                           finish='chrome'))
    ret = P.place(bath.glass_pane(Y1 - .01 - ff, 1.95, channel='right', name=f'{ROOM}.screen.return'),
                  (xr - .01, (ff + Y1 - .01) / 2, z(.04)), rot_z=90)
    ctx.add(ret, ROOM, 'fit')

    # ---------------------------------------------------------------- south wall, west -> east
    xt = X0 + 1.025                                                      # towel radiator x 0.76..1.29, z 0.20..1.80
    rad = P.place(bath.towel_rail(.5, 1.6, mat=M.solid('bathroom2_rail_black', '#191A1B', .45),
                                  name=f'{ROOM}.towel_rail'), (xt, Y0, z(.20)), facing=(0, 1))
    ctx.add(rad, ROOM, 'fit', plan_sym='towel_rail')
    mb = mo.MB()                                                         # bolt-on hook rail across the top
    mb.box((xt - .23, Y0 + .068, z(1.79)), (xt + .23, Y0 + .08, z(1.815)), 'black_matt', bev=.002)
    for dx in (-.17, -.055, .055, .17):
        x = xt + dx
        mb.tube([(x, Y0 + .08, z(1.81)), (x, Y0 + .115, z(1.80)), (x, Y0 + .12, z(1.83))], .005, 'black_matt', n=6)
    _mb_add(ctx, mb, f'{ROOM}.towel_rail.hooks')

    # vanity x 1.33..1.92: shaker face frame with the stiles down to the floor, two inset doors with flat recessed
    # panels, dark bronze bow handles 0.10 by the meeting stiles; carcass 0.30 deep; basin 0.60 x 0.45, rim 0.87
    xv, wv, dv, hv, st = X0 + 1.625, .58, .28, .745, .045         # carcass top under the basin's apron (0.745)
    yf = Y0 + dv                                                         # back of the doors / face frame
    car = P.place(P.cabinet_carcass(wv, dv, hv, furn, plinth=.03, plinth_recess=.015, open_front=True, shelves=1,
                                    inner=inner, name=f'{ROOM}.vanity'), (xv, Y0, FZ), facing=(0, 1))
    ctx.add(car, ROOM, 'fit', plan_sym='vanity')
    mb = mo.MB()
    for s in (-1, 1):
        mb.box((xv + s * wv / 2 - (st if s > 0 else 0), yf, FZ), (xv + s * wv / 2 + (st if s < 0 else 0), yf + .02, z(hv)),
               furn, bev=.002)
    mb.box((xv - wv / 2 + st, yf, z(.03)), (xv + wv / 2 - st, yf + .02, z(.10)), furn, bev=.002)
    mb.box((xv - wv / 2 + st, yf, z(hv - .06)), (xv + wv / 2 - st, yf + .02, z(hv)), furn, bev=.002)
    for s in (-1, 1):                                                    # side panels to the floor
        mb.box((xv + s * wv / 2 - (.018 if s > 0 else 0), Y0, FZ), (xv + s * wv / 2 + (.018 if s < 0 else 0), yf, z(.03)),
               furn)
    _mb_add(ctx, mb, f'{ROOM}.vanity.frame')
    wd, hd = (wv - 2 * st) / 2 - .003, hv - .06 - .10 - .004
    for k, s in enumerate((-1, 1)):                                      # west door hinges W (+), east door E (-)
        xd = xv + s * (wd / 2 + .0015)
        d = P.place(P.panel_door(wd, hd, stile=.05, mat=furn, name=f'{ROOM}.vanity.door.{k}'), (xd, yf, z(.102)),
                    facing=(0, 1))
        h = P.place(P.handle_d(.10, .008, .026, 'bronze_dark', vertical=True, name=f'{ROOM}.vanity.pull.{k}'),
                    (xv + s * .035, yf + .02, z(.60)), facing=(0, 1))
        IX.tag_many([d, h], 'hinge', g=f'{ROOM}.vanity.d{k}', label='Cupboard', p=(xv + s * (wv / 2 - st), yf + .02, FZ),
                    deg=-95 * s)
        for o in (d, h):
            ctx.add(o, ROOM, 'fit', lm='dynamic')
    basin = P.place(_b2_basin(.60, .45, .125, name=f'{ROOM}.basin'), (xv, Y0, z(.87)), facing=(0, 1))
    ctx.add(basin, ROOM, 'fit')                                          # the plan's 'vanity' symbol draws the bowl
    ctx.add(P.place(P.lathe([(0, 0), (.019, 0), (.019, .004), (.014, .006), (0, .006)], 16, 'chrome',
                            name=f'{ROOM}.basin.waste'), (xv, Y0 + .26, z(.75))), ROOM, 'fit')
    bath.add(ctx, ROOM, bath.basin_mixer(f'{ROOM}.tap', (xv, Y0 + .05, z(.87)), z(.75), (0, 1)))
    # glass soap dish in a chrome ring on a square plate E of the tap, white double toothbrush holder W (v13 t105, t106)
    mb = mo.MB()
    xsd = xv + .17
    mb.box((xsd - .03, Y0, z(.975)), (xsd + .03, Y0 + .008, z(1.035)), 'chrome', bev=.003)
    mb.tube([(xsd, Y0 + .008, z(1.005)), (xsd, Y0 + .04, z(1.005))], .006, 'chrome', n=8)
    mb.tube([(xsd + .052 * cos(radians(a)), Y0 + .095 + .052 * sin(radians(a)), z(1.0)) for a in range(0, 361, 30)],
            .0035, 'chrome', n=6)
    _mb_add(ctx, mb, f'{ROOM}.holders')
    dish = P.place(P.lathe([(0, 0), (.032, 0), (.05, .02), (.047, .022), (.029, .006), (0, .006)], 20, 'glass_frosted',
                           name=f'{ROOM}.soapdish'), (xsd, Y0 + .095, z(.985)))
    ctx.add(dish, ROOM, 'decor')
    mb = mo.MB()
    for dx in (-.025, .025):                                             # two clip cradles on one white backplate
        x = xv - .14 + dx
        mb.box((x - .014, Y0, z(1.02)), (x + .014, Y0 + .012, z(1.11)), 'plastic_white', bev=.004)
        mb.box((x - .016, Y0 + .012, z(1.02)), (x + .016, Y0 + .04, z(1.035)), 'plastic_white', bev=.005)
        mb.box((x - .012, Y0 + .012, z(1.085)), (x + .012, Y0 + .03, z(1.10)), 'plastic_white', bev=.004)
    _mb_add(ctx, mb, f'{ROOM}.toothbrush_holder', kind='decor')

    # illuminated mirror cabinet over the vanity, two mirror doors with a frosted light strip between them; 0.62 so it
    # clears the towel radiator (1.70) and the picture
    mb = mo.MB()
    x0m, x1m, z0m, z1m = xv - .31, xv + .31, z(1.30), z(2.00)
    mb.box((x0m, Y0, z0m), (x1m, Y0 + .124, z1m), M.solid('bathroom2_mcab', '#E9E8E4', 0.35), bev=.003)
    for a, b in (((x0m + .003, Y0 + .124, z0m + .003), (xv - .022, Y0 + .13, z1m - .003)),
                 ((xv + .022, Y0 + .124, z0m + .003), (x1m - .003, Y0 + .13, z1m - .003))):
        mb.box(a, b, 'mirror')
    _mb_add(ctx, mb, f'{ROOM}.mirror_cabinet', kind='fit', plan_sym='mirror')
    mb = mo.MB()
    mb.box((xv - .02, Y0 + .124, z0m + .04), (xv + .02, Y0 + .129, z1m - .04), P.emissive('#F4CB94', 2.5))
    strip = _mb_add(ctx, mb, f'{ROOM}.mirror_cabinet.light', kind='light', lm='dynamic')
    IX.tag(strip, 'lamp', label='Mirror light')

    # back-to-wall WC unit x 1.92..2.35 (0.20 carcass + V-grooved front, 0.83 high, white quartz top) + pan (front y
    # 0.69) + round chrome flush button W of the pan
    xw, ww = X0 + 2.135, .42
    wcu = P.place(P.cabinet_carcass(ww, .20, .81, furn, plinth=.06, plinth_recess=.012, name=f'{ROOM}.wc_unit'),
                  (xw, Y0, FZ), facing=(0, 1))
    ctx.add(wcu, ROOM, 'fit', plan_sym='cabinet')
    mb = mo.MB()
    grooved(mb, (xw - ww / 2 + .002, Y0 + .20, z(.062)), (xw + ww / 2 - .002, Y0 + .22, z(.808)), 5, 0, furn)
    _mb_add(ctx, mb, f'{ROOM}.wc_unit.front')
    mb = mo.MB()
    # plain light-grey quartz, no veining (v13 t71, t73, t106: an even slab a shade darker and warmer than the basin)
    mb.box((xw - ww / 2, Y0, z(.81)), (xw + ww / 2, Y0 + .225, z(.83)), M.solid('bathroom2_quartz', '#DDDBD5', .3),
           bev=.002)                                                     # clear of the raised lid
    _mb_add(ctx, mb, f'{ROOM}.wc_unit.top')
    bath.add(ctx, ROOM, bath.wc(f'{ROOM}.wc', (xw, Y0 + .22, FZ), (0, 1), kind='back_to_wall', w=.35, proj=.47, top=.44,
                                flush=None), plan_sym='wc')
    fb = P.place(bath.flush_button(name=f'{ROOM}.wc.flush'), (xw - .12, Y0 + .214, z(.72)), facing=(0, 1))
    ctx.add(fb, ROOM, 'fit')

    # watercolour over the WC: limed frame, silver slip, cream mount (in the crop), glazed; 0.38 x 0.28 between the
    # mirror cabinet and the tall-cabinet side (spec 0.44 x 0.32, which the 2.68 m room does not hold)
    pic = P.framed_picture(os.path.abspath(ART), .38, .28, 'white', frame_w=.042, depth=.025, slip=('silver_satin', .008),
                           glass=True, name=f'{ROOM}.picture')
    pic.data = pic.data.copy()
    limed = M.solid('bathroom2_frame_limed', '#D3C4A2', 0.6)
    for i, m in enumerate(pic.data.materials):
        if m and m.name.startswith('white_gloss'):
            pic.data.materials[i] = limed
    ctx.add(P.place(pic, (((x1m + xc0) / 2), Y0, z(1.61)), facing=(0, 1)), ROOM, 'decor')

    # tall cabinet in the SE corner (local x 2.35.., y 0..0.30, 2.04 high), doors face N: lower 0.10..0.85, open niche
    # 0.88..1.20, upper 1.22..2.00, bow handles on the window side, hinged W; plain flat side panel. It runs to the
    # east wall when the pipe boxing starts north of it (survey), else stops at the boxing (house.json: from the wall)
    xe = (X1 if YB0 >= Y0 + .30 - .005 else XB) - .002
    wc_, dc = xe - xc0, .30
    xc, yc_ = (xc0 + xe) / 2, Y0 + dc
    tc = P.place(P.cabinet_carcass(wc_, dc, 2.04, furn, plinth=.08, plinth_recess=.015, open_front=True, inner=inner,
                                   name=f'{ROOM}.tallcab'), (xc, Y0, FZ), facing=(0, 1))
    ctx.add(tc, ROOM, 'fit', plan_sym='cabinet')
    mb = mo.MB()
    xi0, xi1 = xc - wc_ / 2 + .018, xc + wc_ / 2 - .018
    for zs in (.855, 1.201, .45, 1.62):                                  # niche floor / top, one shelf per cupboard
        mb.box((xi0, Y0 + .006, z(zs)), (xi1, yc_ - (.02 if zs in (.45, 1.62) else 0), z(zs + .018)), inner)
    bw = xi1 - xi0
    for f0, f1, z0b, h, col in ((.08, .45, .873, .15, '#D8D2C4'), (.55, .92, .873, .11, '#C9CDD0'),
                                (.08, .85, 1.638, .16, '#E4E0D6'), (.10, .60, .468, .20, '#CFC8BA')):
        mb.box((xi0 + bw * f0, Y0 + .06, z(z0b)), (xi0 + bw * f1, Y0 + .24, z(z0b + h)),
               M.solid('bathroom2_box_' + col[1:], col, .8), bev=.002)
    _mb_add(ctx, mb, f'{ROOM}.tallcab.inside', lm='dynamic')
    for part, z0d, hd_, hz, deg in (('lower', .10, .75, .70, 90), ('upper', 1.22, .78, 1.38, 100)):
        d = P.place(P.panel_door(wc_ - .004, hd_, stile=min(.06, wc_ * .25), mat=furn, name=f'{ROOM}.tallcab.{part}'),
                    (xc, yc_, z(z0d)), facing=(0, 1))
        h = P.place(P.handle_d(.128, .009, .03, 'bronze_dark', vertical=True, name=f'{ROOM}.tallcab.{part}.pull'),
                    (xc + wc_ / 2 - .03, yc_ + .02, z(hz)), facing=(0, 1))
        IX.tag_many([d, h], 'hinge', g=f'{ROOM}.tallcab.{part}', label='Cupboard', p=(xc - wc_ / 2 + .002, yc_ + .02, FZ),
                    deg=deg)
        for o in (d, h):
            ctx.add(o, ROOM, 'fit', lm='dynamic')

    # ---------------------------------------------------------------- window wall
    wy = (WY0 + WY1) / 2
    roll = P.place(_b2_roll_holder(name=f"{ROOM}.roll_holder"), (X1, wy + .02, z(.62)), facing=(-1, 0))
    ctx.add(roll, ROOM, 'fit')
    brush = P.place(P.lathe([(0, 0), (.045, 0), (.046, .01), (.045, .33), (.04, .345), (.012, .35), (.008, .36),
                             (.008, .43), (.014, .44), (.012, .455), (0, .456)], 20, 'steel_brushed', name=f'{ROOM}.brush'),
                    (X1 - .07, WY1 - .11, FZ))
    ctx.add(brush, ROOM, 'decor')
    PLANT_X, PLANT_Y = X1 + .10, wy
    plant = P.place(_b2_spider(seed=5, name=f'{ROOM}.plant'), (PLANT_X, PLANT_Y, z(.831)))
    ctx.add(plant, ROOM, 'decor')
    # white square louvred extractor fan on the east wall above the window head (v13 t77, f78)
    ctx.add(P.place(_b2_fan(name=f'{ROOM}.extractor'), (X1, wy - .07, z(2.27)), facing=(-1, 0)), ROOM, 'fit')

    # ---------------------------------------------------------------- floor
    mat_ = P.place(_b2_bathmat(.90, .53, name=f'{ROOM}.bath_mat'), (X0 + .765, Y0 + .995, FZ))
    ctx.add(mat_, ROOM, 'decor', plan_sym='rug')

    # four recessed LED downlights (switched from the hall, landing2 S3)
    for i, (x, y) in enumerate(((1.10, Y0 + .50), (2.40, Y0 + .50), (1.10, Y0 + 1.50), (2.40, Y0 + 1.50))):
        lighting.downlight(ctx, ROOM, x, y, watts=DOWN_W, kelvin=3000, spot_deg=120, name=f'{ROOM}.downlight.{i}')
        ctx.add(P.place(P.downlight(name=f'{ROOM}.downlight_trim.{i}'), (x, y, CZ)), ROOM, 'light')

    SA.build(ctx, X0, Y0, Y1, FZ)


# ----------------------------------------------------------------------------- own parts
def _rr(x0, x1, y0, y1, r, zz, k=4):
    """Rounded rectangle ring at height zz, counter-clockwise seen from +Z, 4 * (k + 1) points."""
    out = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for i in range(k + 1):
            a = radians(a0 + 90 * i / k)
            out.append((cx + r * cos(a), cy + r * sin(a), zz))
    return out


@P._prop
def _b2_basin(b, w, d, h):
    """Semi-countertop basin: rim top at z 0, back on y = 0, front at y = -d; bowl with a tap deck at the back."""
    hw = w / 2
    rings = [_rr(-hw + .012, hw - .012, -d + .012, -.004, .05, -h),       # underside of the front apron
             _rr(-hw, hw, -d, 0, .055, -.012), _rr(-hw + .002, hw - .002, -d + .002, -.002, .053, -.002),
             _rr(-hw + .006, hw - .006, -d + .006, -.006, .05, 0),        # rounded rim
             _rr(-hw + .035, hw - .035, -d + .035, -.105, .045, 0),       # bowl edge (deck at the back)
             _rr(-hw + .039, hw - .039, -d + .039, -.109, .043, -.006),
             _rr(-hw + .052, hw - .052, -d + .05, -.12, .04, -.05),
             _rr(-hw + .085, hw - .085, -d + .08, -.15, .035, -.10),
             _rr(-hw + .11, hw - .11, -d + .105, -.175, .03, -.12)]
    b.add(bath._loft(rings), 'ceramic_white', 40)


@P._prop
def _b2_bathmat(b, w, d):
    """Grey tufted cotton bath mat (origin floor centre): sunk field 10 mm inside a raised, slightly lighter border band
    14 mm, 0.07 wide (v13 t106, t123); both carry a generated loop-pile image (rooms/bathroom2_tex.py, #A3A6A8 mean)."""
    m, mb_ = TX.pile('field'), TX.pile('border')
    e = .07
    b.add(P._box_round((-w / 2 + e - .002, -d / 2 + e - .002, 0), (w / 2 - e + .002, d / 2 - e + .002, .010), .004, 1), m,
          True, closed=True)
    for lo, hi in (((-w / 2, -d / 2, 0), (w / 2, -d / 2 + e, .014)), ((-w / 2, d / 2 - e, 0), (w / 2, d / 2, .014)),
                   ((-w / 2, -d / 2 + e, 0), (-w / 2 + e, d / 2 - e, .014)), ((w / 2 - e, -d / 2 + e, 0), (w / 2, d / 2 - e, .014))):
        b.add(P._box_round(lo, hi, .006, 2), mb_, True, closed=True)


@P._prop
def _b2_fan(b):
    """White square wall extractor 0.15 (wall prop, front -Y): housing with a louvred grille of six slats."""
    b.add(P._box_round((-.075, -.035, -.075), (.075, 0, .075), .006, 2), 'plastic_white', True, closed=True)
    for k in range(6):
        zz = -.05 + k * .02
        b.add(P._box((-.055, -.038, zz - .004), (.055, -.034, zz + .004)), 'plastic_white', closed=True)
        b.add(P._box((-.055, -.0352, zz + .004), (.055, -.0342, zz + .0095)), 'plastic_dark', closed=True)


PLANT_X, PLANT_Y = 3.20, 12.57          # spider-plant pot centre on the sill (set in build)


def _spider_ok(g, T, zmin=-.05):
    """Leaf keeps clear of the glass, the reveal jambs, the sill, the roll holder below and the open sauna door, whose
    glass and handle reach x 3.01 (local frame: origin = pot base on the sill top, world x = PLANT_X + x)."""
    for v in g.v:
        p = T @ P.Vector(v)
        if not -.165 < p.x < X1 + .225 - PLANT_X or p.z < zmin:
            return False
        if p.x > -.135 and (p.z < .003 or not WY0 + .01 - PLANT_Y < p.y < WY1 - .01 - PLANT_Y):  # sill / reveal
            return False
    return True


def _spider_leaf(b, mats, L, W, bend, T, zmin=-.05):
    """Add one strap leaf, shortened up to 12 times by 10 % until _spider_ok holds (dropped if it never does)."""
    for _ in range(12):
        g = P._leaf_strap(L, W, bend)
        if _spider_ok(g, T, zmin):
            b.add(g, mats, True, T=T)
            return
        L *= .9


@P._prop
def _b2_spider(b, seed=5):
    """Spider plant in a white embossed pot (origin: pot base centre): about 45 arching green leaves with a cream centre
    stripe from the soil, bending over the pot rim; two runners with plantlets drooping just over the sill nose (-X)."""
    rnd = random.Random(seed)
    P._pot(b, .17, .14, 'ceramic_white')
    zs = .14 * .9
    LG = P.two_sided('leaf_mid')
    mats = [LG, P.two_sided(M.solid('bathroom2_leaf_cream', '#DCE2C0', .45)), LG] * 5
    for i in range(46):
        az = rnd.uniform(-70, 250)                                     # 270 = +X (the glass): kept out
        L, W = rnd.uniform(.20, .34), rnd.uniform(.016, .024)
        r0 = rnd.uniform(0, .03)
        T0 = P.Tr(-sin(radians(az)) * r0, cos(radians(az)) * r0, zs)
        elev, bend = rnd.uniform(20, 65), radians(rnd.uniform(80, 130))
        _spider_leaf(b, mats, L, W, bend, T0 @ P.Rot('Z', az) @ P.Rot('X', elev))
    for az, dy in ((100, -.15), (80, .14)):                            # runners clear of the roll holder (|y| < .09)
        end = P.Vector((-.155, dy, -.06))
        pts = P._bez((0, 0, zs), (-.04, dy * .2, zs + .10), (-.14, dy * .8, .06), end, 8)
        b.add(P._tube(pts, .0016, 4), 'leaf_mid', True, closed=True)
        for k in range(5):
            _spider_leaf(b, mats, .07, .009, radians(90), P.Tr(*end) @ P.Rot('Z', az + k * 72) @ P.Rot('X', 35), -.12)


@P._prop
def _b2_roll_holder(b):
    """Antique-brass hooded toilet-roll holder (wall prop, front -Y, origin = centre of the back plate): oval back plate,
    a domed hood with an embossed rim over the roll, side arms and a bar with a white roll (v13 t73)."""
    br = 'brass_antique'
    b.add(P._box_round((-.09, -.006, -.04), (.09, 0, .065), .004, 2), br, True, closed=True)
    hood = P._lathe([(.085, 0), (.084, .03), (.078, .055), (.065, .075), (.04, .088), (0, .092)], 16, arc=(0, 3.14159))
    b.add(hood, P.two_sided(br), True, T=P.Tr(0, -.006, -.025) @ P.Rot('X', 90) @ P.Sc(1, .8, 1.1))  # shallow half dome
    for rr, yy in ((.087, -.009), (.07, -.08)):                        # embossed beads round the hood
        b.add(P._tube([(rr * cos(radians(a)), yy, -.025 + .8 * rr * sin(radians(a))) for a in range(0, 181, 15)], .003, 6,
                      up=(0, 1, 0)), br, True, closed=True)
    for s in (-1, 1):
        b.add(P._tube([(s * .075, -.006, -.02), (s * .075, -.07, -.025)], .005, 8), br, True, closed=True)
        b.add(P._sphere(.009, 8, 5), br, True, closed=True, T=P.Tr(s * .079, -.07, -.025))
    b.add(P._tube([(-.072, -.07, -.025), (.072, -.07, -.025)], .006, 8), br, True, closed=True)
    b.add(P._lathe([(.02, 0), (.055, 0), (.055, .105), (.02, .105)], 20), 'plastic_white', True,
          T=P.Tr(-.0525, -.07, -.025) @ P.Rot('Y', 90))

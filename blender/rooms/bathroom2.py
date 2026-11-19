"""bathroom2 - second-floor bathroom: shower, free-standing sauna, vanity, WC unit, tall cabinet (spec/rooms/bathroom2.md).

Room x 0.40..3.10, y 11.50..13.70, floor Z 6.02, ceiling 8.49 (house.json; the spec text's local frame is 0.10 longer, so
the south-wall run is re-fitted between the open door leaf (x <= 1.152) and the pipe boxing (x 2.98), see the report).
The sauna is rooms/bathroom2_sauna.py. The light switch for the four spots is landing2's S3 (hall side, v5 f_0016).
"""
import os
import random
from math import cos, sin, radians

from lib import bath, interact as IX, lighting, materials as M, mouldings as mo, props as P, shell
from rooms import bathroom2_sauna as SA

ROOM = 'bathroom2'
X0, X1, Y0, Y1 = 0.40, 3.10, 11.50, 13.70
FZ, CZ = 6.02, 8.49
WALL = '#B9B7B1'
DOWN_W = 55                       # per downlight (4 in 5.9 m2)
ART = os.path.join(os.path.dirname(__file__), '..', 'textures', 'art', 'bathroom2_watercolour.jpg')

CAMERAS = [
    dict(name='door', pos=(0.48, 11.93, 7.52), look=(3.10, 12.40, 7.02), fov_deg=100, ref='v5:f_0123'),
    dict(name='shower', pos=(1.05, 12.30, 7.52), look=(0.70, 13.70, 7.10), fov_deg=100, ref='v5:f_0013'),
    dict(name='showerin', pos=(1.05, 12.62, 7.62), look=(0.45, 13.35, 6.70), fov_deg=100, ref='v5:f_0027'),
    dict(name='sauna', pos=(2.20, 12.15, 7.45), look=(2.45, 13.70, 7.05), fov_deg=100, ref='v5:f_0045'),
    dict(name='saunain', pos=(2.58, 12.62, 7.55), look=(2.30, 13.55, 6.65), fov_deg=100, ref='v5:f_0047'),
    dict(name='heater', pos=(2.55, 12.80, 7.30), look=(1.85, 13.25, 6.45), fov_deg=90, ref='v5:f_0055'),
    dict(name='saunafront', pos=(2.40, 13.45, 7.25), look=(2.15, 12.87, 7.50), fov_deg=100, ref='v5:f_0061'),
    dict(name='window', pos=(1.95, 12.45, 7.45), look=(3.10, 12.30, 7.05), fov_deg=100, ref='v5:f_0089'),
    dict(name='tallcab', pos=(2.15, 12.55, 7.40), look=(2.95, 11.70, 6.95), fov_deg=100, ref='v5:f_0093'),
    dict(name='south', pos=(1.95, 12.70, 7.55), look=(2.10, 11.50, 7.00), fov_deg=100, ref='v5:f_0115'),
    dict(name='doorwall', pos=(2.30, 12.45, 7.45), look=(0.40, 12.00, 7.05), fov_deg=100, ref='v5:f_0128'),
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


def build(ctx):
    furn = M.paint('#DAD8D0', 0.45)          # satin painted shaker furniture (vanity, WC unit, tall cabinet)
    inner = M.paint('#F2F1EC', 0.5)

    # ---------------------------------------------------------------- shell coverings
    # shower walls: Calacatta slabs, two tiers (joint at 1.20), full height to the cornice, 10 mm on the wall
    def slab(name, x0, x1, y0, y1, z0, z1):
        ob = shell.box(name, x0, x1, y0, y1, z0, z1, 'porcelain_calacatta_slab')
        M.uv_box(ob, origin=(X0, Y1, FZ))
        return ctx.add(ob, ROOM, 'fit')

    top = CZ - .08                                                       # cornice underside
    slab(f'{ROOM}.slab.w', X0, X0 + .01, 12.402, Y1, FZ, top)            # from the door architrave to the N wall
    nx0, nx1, nz0, nz1 = 0.90, 1.50, z(1.15), z(1.47)                     # niche in the N wall (spec 5.1)
    yn = Y1 - .01
    slab(f'{ROOM}.slab.n0', X0 + .01, 1.66, yn, Y1, FZ, nz0)
    slab(f'{ROOM}.slab.n1', X0 + .01, 1.66, yn, Y1, nz1, top)
    slab(f'{ROOM}.slab.n2', X0 + .01, nx0, yn, Y1, nz0, nz1)
    slab(f'{ROOM}.slab.n3', nx1, 1.66, yn, Y1, nz0, nz1)
    carved = not shell.is_solid(ctx, (nx0 + nx1) / 2, Y1 + .05, (nz0 + nz1) / 2)
    # the wall stays solid until house.json cuts the recess: then only a 9 mm sinking in the slab lining is possible
    back, bt = (Y1 + .10, .01) if carved else (Y1 - .0005, .0005)
    yb = back - bt
    slab(f'{ROOM}.niche.back', nx0, nx1, yb, back, nz0, nz1)
    slab(f'{ROOM}.niche.bottom', nx0, nx1, yn, yb, nz0, nz0 + .01)
    slab(f'{ROOM}.niche.top', nx0, nx1, yn, yb, nz1 - .01, nz1)
    slab(f'{ROOM}.niche.l', nx0, nx0 + .01, yn, yb, nz0 + .01, nz1 - .01)
    slab(f'{ROOM}.niche.r', nx1 - .01, nx1, yn, yb, nz0 + .01, nz1 - .01)
    print(f'[bathroom2] shower niche: {"recess cut in the wall" if carved else "wall solid -> 9 mm sinking only"}')
    mb = mo.MB()                                                          # brushed stainless edge trim round it
    for a, b in (((nx0 - .012, yn - .004, nz0 - .012), (nx1 + .012, yn, nz0)),
                 ((nx0 - .012, yn - .004, nz1), (nx1 + .012, yn, nz1 + .012)),
                 ((nx0 - .012, yn - .004, nz0), (nx0, yn, nz1)), ((nx1, yn - .004, nz0), (nx1 + .012, yn, nz1))):
        mb.box(a, b, 'steel_brushed', bev=.001)
    _mb_add(ctx, mb, f'{ROOM}.niche.trim')

    # pipe boxing: the footage (v5 f_0095, f_0101) shows it running up to the ceiling as a plastered column, tiled only
    # below 1.20, and continuing behind the tall cabinet; house.json stops it at 1.20 -> paint the rest here
    for i, (ya, yb_, za) in enumerate(((Y0, 11.85, FZ), (11.85, 12.16, z(1.20)))):
        if shell.is_solid(ctx, 3.04, (ya + yb_) / 2, za + .3):           # house.json already carries the full boxing
            continue
        ob = shell.box(f'{ROOM}.boxing_col.{i}', 2.98, X1, ya, yb_, za, CZ, WALL)
        ctx.add(ob, ROOM, 'fit')

    # chrome-look trim on top of the metro dado (1.20) and down the boxing's external corner
    mb = mo.MB()
    t0, t1, e = z(1.195), z(1.207), .006
    for a, b in (((X0 + .02, Y0, t0), (2.67, Y0 + e, t1)),                # south wall (door architrave -> tall cabinet)
                 ((2.98 - e, 11.85, t0), (2.98, 12.16 + e, t1)),           # boxing W face
                 ((2.98 - e, 12.16, t0), (X1, 12.16 + e, t1)),             # boxing N face
                 ((X1 - e, 12.80, t0), (X1, Y1, t1)),                      # E wall N of the window (behind the sauna)
                 ((1.66, Y1 - e, t0), (X1, Y1, t1)),                       # N wall behind the sauna
                 ((2.98 - .008, 12.16, FZ), (2.98, 12.168, t1))):          # boxing corner (v5 f_0099)
        mb.box(a, b, 'silver_satin', bev=.0015)
    _mb_add(ctx, mb, f'{ROOM}.tile_trim', kind='trim')

    # window board: white quartz-effect sill, 30 mm with a rounded nose 30 mm proud (spec 2.2)
    mb = mo.MB()
    sill = M.solid('bathroom2_sill', '#F1F0EC', 0.3)
    mb.box((X1 - .002, 12.161, z(.801)), (3.33, 12.799, z(.83)), sill)
    mb.box((X1 - .03, 12.161, z(.801)), (X1, 12.82, z(.83)), sill, bev=.008)
    _mb_add(ctx, mb, f'{ROOM}.sill')

    # ---------------------------------------------------------------- shower (NW corner)
    tray_m = M.solid('bathroom2_tray', '#F2F1EE', 0.35)
    mb = mo.MB()
    mb.box((X0 + .01, 12.90, FZ), (1.62, Y1 - .01, z(.04)), tray_m, bev=.005)
    _mb_add(ctx, mb, f'{ROOM}.shower.tray', plan_sym='shower')
    w = P.place(P.lathe([(0, 0), (.045, 0), (.045, .002), (.03, .003), (0, .003)], 20, 'chrome',
                        name=f'{ROOM}.shower.waste'), (0.62, 13.30, z(.04)))
    ctx.add(w, ROOM, 'fit')
    bath.add(ctx, ROOM, bath.shower_set(f'{ROOM}.shower', (X0 + .01, 13.30, FZ), (1, 0), to_z=z(.04), valve_z=1.10,
                                        head_z=2.10, reach=.38, head_dia=.25, basket_z=1.25))
    bath.add(ctx, ROOM, bath.shower_slider(f'{ROOM}.screen', ((X0 + .01 + 1.62) / 2, 12.93, z(.04)), 1.62 - X0 - .01,
                                           (0, -1), height=1.95, door='left', rail='round', rail_z=1.93, handle_z=1.06,
                                           finish='chrome'))
    ret = P.place(bath.glass_pane(.735, 1.95, channel='right', name=f'{ROOM}.screen.return'), (1.62, 13.3225, z(.04)),
                  rot_z=90)
    ctx.add(ret, ROOM, 'fit')

    # ---------------------------------------------------------------- south wall, west -> east
    rad = P.place(bath.towel_rail(.5, 1.6, name=f'{ROOM}.towel_rail'), (1.42, Y0, z(.20)), facing=(0, 1))
    ctx.add(rad, ROOM, 'fit', plan_sym='towel_rail')
    mb = mo.MB()                                                          # bolt-on hook rail across the top
    mb.box((1.19, Y0 + .068, z(1.79)), (1.65, Y0 + .08, z(1.815)), 'black_matt', bev=.002)
    for x in (1.25, 1.37, 1.47, 1.59):
        mb.tube([(x, Y0 + .08, z(1.81)), (x, Y0 + .115, z(1.80)), (x, Y0 + .12, z(1.83))], .005, 'black_matt', n=6)
    _mb_add(ctx, mb, f'{ROOM}.towel_rail.hooks')

    # vanity 0.58 x 0.38 x 0.80 (x 1.68..2.26), semi-countertop basin, monobloc mixer
    xv, dv = 1.97, .38
    yf = Y0 + dv
    car = P.place(P.cabinet_carcass(.58, dv, .80, furn, plinth=.05, plinth_recess=.012, open_front=True, shelves=1,
                                    inner=inner, name=f'{ROOM}.vanity'), (xv, Y0, FZ), facing=(0, 1))
    ctx.add(car, ROOM, 'fit', plan_sym='vanity')
    mb = mo.MB()                                                          # V-grooved end panels
    grooved(mb, (xv - .29 - .005, Y0, z(.05)), (xv - .29, yf, z(.80)), 5, 1, furn)
    grooved(mb, (xv + .29, Y0, z(.05)), (xv + .29 + .005, yf, z(.80)), 5, 1, furn)
    _mb_add(ctx, mb, f'{ROOM}.vanity.ends')
    for k, (s, deg) in enumerate(((-1, 100), (1, -80))):                 # west door hinges W (+), east door E (-)
        xd = xv + s * .1445                                               # 80 deg: the pan stands beside the east door
        d = P.place(P.panel_door(.287, .64, stile=.06, mat=furn, name=f'{ROOM}.vanity.door.{k}'), (xd, yf, z(.07)),
                    facing=(0, 1))
        h = P.place(P.handle_d(.096, .008, .026, 'bronze_dark', vertical=True, name=f'{ROOM}.vanity.pull.{k}'),
                    (xv + s * .04, yf + .02, z(.52)), facing=(0, 1))
        IX.tag_many([d, h], 'hinge', g=f'{ROOM}.vanity.d{k}', label='Cupboard', p=(xv + s * .289, yf + .02, FZ), deg=deg)
        for o in (d, h):
            ctx.add(o, ROOM, 'fit', lm='dynamic')
    basin = P.place(_b2_basin(.58, .45, .15, name=f'{ROOM}.basin'), (xv, Y0, z(.87)), facing=(0, 1))
    ctx.add(basin, ROOM, 'fit')                                          # the plan's 'vanity' symbol draws the bowl
    ctx.add(P.place(P.lathe([(0, 0), (.019, 0), (.019, .004), (.014, .006), (0, .006)], 16, 'chrome',
                            name=f'{ROOM}.basin.waste'), (xv, Y0 + .26, z(.75))), ROOM, 'fit')
    bath.add(ctx, ROOM, bath.basin_mixer(f'{ROOM}.tap', (xv, Y0 + .05, z(.87)), z(.75), (0, 1)))
    # glass soap dish (E of the tap, toward the WC) and tumbler (W) in chrome rings on the tiles (hr_115)
    mb = mo.MB()
    for x, cup in ((xv + .19, False), (xv - .17, True)):
        mb.tube([(x, Y0, z(1.05)), (x, Y0 + .05, z(1.05))], .007, 'chrome', n=8)
        mb.tube([(x - .045 * (not cup) - .035 * cup, Y0 + .085, z(1.05)), (x, Y0 + .04, z(1.05)),
                 (x + .045 * (not cup) + .035 * cup, Y0 + .085, z(1.05))], .004, 'chrome', n=6)
    _mb_add(ctx, mb, f'{ROOM}.holders')
    dish = P.place(P.lathe([(0, 0), (.035, 0), (.055, .022), (.052, .024), (.032, .006), (0, .006)], 20, 'glass_frosted',
                           name=f'{ROOM}.soapdish'), (xv + .19, Y0 + .085, z(1.04)))
    ctx.add(dish, ROOM, 'decor')
    tum = P.place(P.tumbler(.10, .066, 12, name=f'{ROOM}.tumbler'), (xv - .17, Y0 + .085, z(.99)))
    ctx.add(tum, ROOM, 'decor')

    # illuminated mirror cabinet over the vanity, two mirror doors, frosted light strip: as wide as the vanity (0.58,
    # spec 0.65) so it clears the towel rail (1.67) and the picture in the 2.70 m room
    mb = mo.MB()
    x0m, x1m, z0m, z1m = xv - .29, xv + .29, z(1.33), z(2.03)
    mb.box((x0m, Y0, z0m), (x1m, Y0 + .124, z1m), M.solid('bathroom2_mcab', '#E9E8E4', 0.35), bev=.003)
    for a, b in (((x0m + .003, Y0 + .124, z0m + .003), (xv - .022, Y0 + .13, z1m - .003)),
                 ((xv + .022, Y0 + .124, z0m + .003), (x1m - .003, Y0 + .13, z1m - .003))):
        mb.box(a, b, 'mirror')
    _mb_add(ctx, mb, f'{ROOM}.mirror_cabinet', kind='fit', plan_sym='mirror')
    mb = mo.MB()
    mb.box((xv - .02, Y0 + .124, z0m + .04), (xv + .02, Y0 + .129, z1m - .04), P.emissive('#F4CB94', 2.5))
    strip = _mb_add(ctx, mb, f'{ROOM}.mirror_cabinet.light', kind='light', lm='dynamic')
    IX.tag(strip, 'lamp', label='Mirror light')

    # back-to-wall WC unit (x 2.26..2.67, 0.22 deep, 0.83 high, quartz top) + pan + round flush button
    xw = 2.465
    wcu = P.place(P.cabinet_carcass(.41, .22, .81, furn, plinth=.06, plinth_recess=.012, name=f'{ROOM}.wc_unit'),
                  (xw, Y0, FZ), facing=(0, 1))
    ctx.add(wcu, ROOM, 'fit', plan_sym='cabinet')
    front = P.place(P.panel_door(.405, .745, stile=.06, mat=furn, panels=(1, 2), name=f'{ROOM}.wc_unit.front'),
                    (xw, Y0 + .22, z(.062)), facing=(0, 1))
    ctx.add(front, ROOM, 'fit')
    mb = mo.MB()
    mb.box((2.262, Y0, z(.81)), (2.668, Y0 + .235, z(.83)), 'marble_quartz', bev=.002)
    _mb_add(ctx, mb, f'{ROOM}.wc_unit.top')
    bath.add(ctx, ROOM, bath.wc(f'{ROOM}.wc', (xw, Y0 + .22 + .02, FZ), (0, 1), kind='back_to_wall', w=.35, top=.44,
                                flush=None), plan_sym='wc')
    # W of the pan (v5 f_0093), sunk 6 mm into the 20 mm front so its face (y 11.748) stays in front of the raised lid
    fb = P.place(bath.flush_button(name=f'{ROOM}.wc.flush'), (xw - .11, Y0 + .234, z(.72)), facing=(0, 1))
    ctx.add(fb, ROOM, 'fit')

    # watercolour over the WC: limed frame, silver slip, cream mount (in the crop), glazed; 0.38 x 0.28 (spec 0.44 x
    # 0.32) so it sits between the mirror cabinet (2.26) and the tall-cabinet side (2.665)
    pic = P.framed_picture(os.path.abspath(ART), .38, .28, 'white', frame_w=.042, depth=.025, slip=('silver_satin', .008),
                           glass=True, name=f'{ROOM}.picture')
    pic.data = pic.data.copy()
    limed = M.solid('bathroom2_frame_limed', '#D3C4A2', 0.6)
    for i, m in enumerate(pic.data.materials):
        if m and m.name.startswith('white_gloss'):
            pic.data.materials[i] = limed
    ctx.add(P.place(pic, (xw, Y0, z(1.61)), facing=(0, 1)), ROOM, 'decor')

    # tall cabinet in the SE corner (x 2.67..2.98 against the boxing column, 0.35 deep, 2.04 high), doors face N
    xc, wc_, dc = 2.825, .31, .35
    yc = Y0 + dc
    tc = P.place(P.cabinet_carcass(wc_, dc, 2.04, furn, plinth=.08, plinth_recess=.015, open_front=True, inner=inner,
                                   name=f'{ROOM}.tallcab'), (xc, Y0, FZ), facing=(0, 1))
    ctx.add(tc, ROOM, 'fit', plan_sym='cabinet')
    mb = mo.MB()
    grooved(mb, (xc - wc_ / 2 - .005, Y0, z(.08)), (xc - wc_ / 2, yc, z(2.04)), 5, 1, furn)   # V-grooved W side
    xi0, xi1 = xc - wc_ / 2 + .018, xc + wc_ / 2 - .018
    for zs in (.855, 1.201, .45, 1.62):                                   # niche floor / top, one shelf per cupboard
        mb.box((xi0, Y0 + .006, z(zs)), (xi1, yc - (.02 if zs in (.45, 1.62) else 0), z(zs + .018)), inner)
    for x0b, x1b, z0b, h, col in ((xi0 + .02, xi0 + .13, .873, .17, '#D8D2C4'), (xi0 + .15, xi1 - .03, .873, .12, '#C9CDD0'),
                                  (xi0 + .02, xi1 - .06, 1.638, .16, '#E4E0D6'), (xi0 + .03, xi0 + .15, .468, .22, '#CFC8BA')):
        mb.box((x0b, Y0 + .08, z(z0b)), (x1b, Y0 + .28, z(z0b + h)), M.solid('bathroom2_box_' + col[1:], col, .8), bev=.002)
    _mb_add(ctx, mb, f'{ROOM}.tallcab.inside', lm='dynamic')
    for part, z0d, hd, hz, deg in (('lower', .10, .75, .70, 85), ('upper', 1.22, .78, 1.38, 100)):
        d = P.place(P.panel_door(wc_ - .004, hd, stile=.06, mat=furn, name=f'{ROOM}.tallcab.{part}'), (xc, yc, z(z0d)),
                    facing=(0, 1))
        h = P.place(P.handle_d(.128, .009, .03, 'bronze_dark', vertical=True, name=f'{ROOM}.tallcab.{part}.pull'),
                    (xc + wc_ / 2 - .035, yc + .02, z(hz)), facing=(0, 1))
        IX.tag_many([d, h], 'hinge', g=f'{ROOM}.tallcab.{part}', label='Cupboard', p=(xc - wc_ / 2 + .002, yc + .02, FZ),
                    deg=deg)
        for o in (d, h):
            ctx.add(o, ROOM, 'fit', lm='dynamic')

    # ---------------------------------------------------------------- window wall
    roll = P.place(_b2_roll_holder(name=f'{ROOM}.roll_holder'), (X1, 12.45, z(.68)), facing=(-1, 0))
    ctx.add(roll, ROOM, 'fit')
    brush = P.place(P.lathe([(0, 0), (.045, 0), (.046, .01), (.045, .33), (.04, .345), (.012, .35), (.008, .36),
                             (.008, .43), (.014, .44), (.012, .455), (0, .456)], 20, 'chrome', name=f'{ROOM}.brush'),
                    (3.02, 12.68, FZ))
    ctx.add(brush, ROOM, 'decor')
    plant = P.place(_b2_spider(seed=5, name=f'{ROOM}.plant'), (PLANT_X, 12.46, z(.831)))
    ctx.add(plant, ROOM, 'decor')

    # ---------------------------------------------------------------- floor, ceiling
    mat_ = P.place(P.rug(None, .80, .50, thickness=.012, corner_r=.03, color='#B5B8BD', name=f'{ROOM}.bath_mat'),
                   (1.15, 12.60, FZ))
    ctx.add(mat_, ROOM, 'decor', plan_sym='rug')
    ext = P.place(P.lathe([(0, -.012), (.03, -.012), (.032, -.014), (.06, -.014), (.088, -.012), (.10, -.006), (.10, 0),
                           (0, 0)], 28, 'plastic_white', name=f'{ROOM}.extractor'), (0.85, 13.05, CZ))
    ctx.add(ext, ROOM, 'fit')

    # four recessed LED downlights (switched from the hall, landing2 S3)
    for i, (x, y) in enumerate(((1.10, 12.10), (2.40, 12.10), (1.10, 13.10), (2.40, 13.10))):
        lighting.downlight(ctx, ROOM, x, y, watts=DOWN_W, kelvin=3000, spot_deg=120, name=f'{ROOM}.downlight.{i}')
        ctx.add(P.place(P.downlight(name=f'{ROOM}.downlight_trim.{i}'), (x, y, CZ)), ROOM, 'light')

    SA.build(ctx)


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


PLANT_X = 3.20                    # spider-plant pot centre on the sill (glass / frame from x ~3.33, reveal y 12.16..12.80)


def _spider_ok(g, T, zmin=-.05):
    """Leaf keeps clear of the glass, the reveal jambs, the sill, the roll holder below and the open sauna door, whose
    pane and bar handle reach x 3.026 (local frame: origin = pot base on the sill top, world x = PLANT_X + x)."""
    for v in g.v:
        p = T @ P.Vector(v)
        if not -.165 < p.x < 3.325 - PLANT_X or p.z < zmin:
            return False
        if p.x > -.135 and (p.z < .003 or not -.28 < p.y < .32):     # over the sill board / inside the reveal
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
    """Spider plant in a white pot (origin: pot base centre): about 45 arching green leaves with a cream centre stripe
    from the soil, bending over the pot rim; two runners with plantlets drooping just over the sill nose (-X)."""
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
    for az, dy in ((100, -.15), (80, .14)):                            # runners clear of the roll holder (|y| < .07)
        end = P.Vector((-.155, dy, -.06))
        pts = P._bez((0, 0, zs), (-.04, dy * .2, zs + .10), (-.14, dy * .8, .06), end, 8)
        b.add(P._tube(pts, .0016, 4), 'leaf_mid', True, closed=True)
        for k in range(5):
            _spider_leaf(b, mats, .07, .009, radians(90), P.Tr(*end) @ P.Rot('Z', az + k * 72) @ P.Rot('X', 35), -.12)


@P._prop
def _b2_roll_holder(b):
    """Chrome dome-backed roll holder (wall prop, front -Y): round back plate with a hood, arm, white roll."""
    b.add(P._lathe([(0, 0), (.062, 0), (.062, .004), (.055, .010), (0, .012)], 24), 'chrome', True,
          T=P.Tr(0, 0, .03) @ P.Rot('X', 90))
    b.add(P._tube([(-.07, -.004, -.02), (-.07, -.065, -.02), (.05, -.065, -.02)], .006, 8), 'chrome', True, closed=True)
    b.add(P._lathe([(.02, 0), (.055, 0), (.055, .10), (.02, .10)], 20), 'plastic_white', True,
          T=P.Tr(-.055, -.065, -.02) @ P.Rot('Y', 90))

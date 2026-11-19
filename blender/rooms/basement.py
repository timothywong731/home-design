"""basement + basement_stair (level B): spec/rooms/basement.md, footage v6 f_0095..f_0298.

This file: cameras, the stair shaft (shelf cap, spandrel back with its jog, south soffit lining, beads, nosing
trims, extinguisher, shelf ornaments, light, switch). The plant / store room is in basement_plant.py.
Heights `h` of the spec are above the basement floor: Z = h - 2.31. The reconciled south wall is y 5.19.
"""
import math

from mathutils import Matrix, Vector

from lib import interact as IX, lighting, materials as M, mouldings as mo, props as P, shell, stairs as LS

from rooms import basement_plant as plant

ST, RM = 'basement_stair', 'basement'

CAMERAS = [
    dict(name='top', pos=(0.60, 7.45, 1.45), look=(0.58, 5.9, -1.3), fov_deg=100, ref='v6:f_0121'),
    dict(name='up', pos=(0.60, 6.25, 0.0), look=(0.58, 7.6, 0.9), fov_deg=100, ref='v6:f_0143'),
    dict(name='shelf', pos=(0.80, 6.75, 0.55), look=(0.2, 5.75, 0.05), fov_deg=100, ref='v6:f_0133'),
    dict(name='foot', pos=(0.50, 5.70, -0.45), look=(3.0, 6.3, -1.3), fov_deg=100, ref='v6:f_0146'),
    dict(name='winders', pos=(1.65, 5.75, -0.85), look=(0.5, 5.75, -1.9), fov_deg=100, ref='v6:f_0259'),
    dict(name='boiler', pos=(2.55, 7.55, -0.81), look=(4.2, 8.0, -1.15), fov_deg=100, ref='v6:f_0165'),
    dict(name='tank', pos=(2.45, 6.30, -0.81), look=(4.1, 6.8, -1.1), fov_deg=100, ref='v6:f_0179'),
    dict(name='racks', pos=(2.70, 6.90, -0.81), look=(2.9, 5.2, -1.3), fov_deg=100, ref='v6:f_0184'),
    dict(name='west', pos=(3.30, 6.60, -0.81), look=(1.25, 6.7, -1.15), fov_deg=100, ref='v6:f_0193'),
    dict(name='cabinet', pos=(2.70, 7.40, -0.81), look=(1.4, 8.4, -0.95), fov_deg=100, ref='v6:f_0197'),
    dict(name='meter', pos=(2.35, 6.30, -0.81), look=(1.55, 5.19, -0.75), fov_deg=100, ref='v6:f_0246'),
]

BEIGE, SOFFIT, WHITE = '#EDE7DA', '#F4F3EE', 'white_gloss'
X_W, X_E, X_SP = 0.265, 0.93, 0.151          # lower shaft walls; back of the hall spandrel (its face is x 0.15)
X_UP, X_JOG, Y_JOG = 0.156, 0.225, 6.45      # upper west wall face south / north of the jog
Y_S, Y_DOOR = 5.19, 7.58
SHELF_Z, CAP_T = -0.03, 0.035


def _stair(ctx):
    s = ctx.stair('stair_basement')
    return s['rise'], s['going'], s['firstStraightRiserY'], s['straightRisers']


def soffit(ctx, y):
    """Underside of the main flight over the shaft (lib/stairs.py: WAIST below the pitch line), y >= 5.60."""
    m = ctx.stair('stair_main')
    return (3 + (y - m['firstStraightRiserY']) / m['going']) * m['rise'] - LS.WAIST


def _shaft(ctx):
    """Linings of the shaft above shelf level: the shell stops at the hall floor and the spandrel is one-sided."""
    beige, sof = M.paint(BEIGE), M.paint(SOFFIT)
    y4 = ctx.stair('stair_main')['firstStraightRiserY']                      # 5.60: the clean rake starts here
    yn = ctx.stair('stair_main')['newel'][1]                                 # 5.33: all winder soffits meet here
    mb = mo.MB()
    # back of the spandrel = upper west wall, with the 0.07 jog at y 6.45 (basement.md 3.2)
    top = lambda y: soffit(ctx, y) + 0.01
    mb.prism([(X_SP, Y_S, SHELF_Z), (X_SP, Y_JOG, SHELF_Z), (X_SP, Y_JOG, top(Y_JOG)), (X_SP, y4, top(y4)),
              (X_SP, yn, 0.0), (X_SP, Y_S, 0.0)], (X_UP - X_SP, 0, 0), beige)
    mb.prism([(X_SP, Y_JOG, SHELF_Z), (X_SP, Y_DOOR, SHELF_Z), (X_SP, Y_DOOR, top(Y_DOOR)), (X_SP, Y_JOG, top(Y_JOG))],
             (X_JOG - X_SP, 0, 0), beige)
    # South end: the carcass soffit under the main winders is faceted, meets at the newel at floor level and leaves
    # the triangle (0.265, 5.19) (0.425, 5.19) (0.265, 5.29) open to the hall. One lining below all of it.
    # ponytail: flat + steep rake instead of the filmed cove; a cove cannot pass under the bottom step of the model.
    z0, z1 = -0.004, soffit(ctx, y4) - 0.004
    mb.face([(X_SP, Y_S, z0), (0.99, Y_S, z0), (0.99, yn, z0), (X_SP, yn, z0)], sof, hint=(0, 0, -1))
    mb.face([(X_SP, yn, z0), (0.99, yn, z0), (0.99, y4, z1), (X_SP, y4, z1)], sof, hint=(0, 0, -1))
    # the 60 mm strip of hall floor left on top of the lintel beside the foot of the flight (x 0.93..0.99) is plaster
    mb.box((X_E, yn, 0.0), (0.99, 6.0, 0.002), M.paint('#F2F0EA'))
    ctx.add(mb.finish('basement_stair.lining'), ST, 'fit')

    # white bullnosed cap board on the west shelf, cavetto bed mould under the oversail
    nose = [(0.006 + 0.0175 * math.cos(math.radians(a)), 0.0175 + 0.0175 * math.sin(math.radians(a)))
            for a in range(-90, 91, 30)]
    bed = [(0.0, -0.016), (0.0015, -0.008), (0.0035, -0.003)]
    cap = mo.MB()
    y_lo = yn + 0.03                                                         # the lining comes down onto the shelf here
    for ya, yb, xb in ((Y_DOOR, Y_JOG, X_JOG), (Y_JOG, y_lo, X_UP)):
        cap.sweep(bed + nose + [(xb - X_W, CAP_T)], [(X_W, ya, SHELF_Z), (X_W, yb, SHELF_Z)], WHITE)
    ctx.add(cap.finish('basement_stair.shelf_cap'), ST, 'trim')


def _steps(ctx):
    """Bead against both walls, pale edge trim at every nosing, the two black inserts of the door nosing."""
    rise, going, y1, n_str = _stair(ctx)
    R = lambda n: y1 - going * (n - 1)
    zt = lambda k: -rise * k
    mb, trim = mo.MB(), M.solid('bs_nosing_trim', '#C6C2B8', 0.5)
    b = 0.012
    for xa, xb in ((X_W, X_W + b), (X_E - b, X_E)):
        for k in range(1, n_str):                                            # treads T1..T8
            mb.box((xa, R(k + 1), zt(k)), (xb, R(k), zt(k) + b), WHITE)
        for n in range(1, n_str + 1):                                        # risers R1..R9
            mb.box((xa, R(n) - b, zt(n)), (xb, R(n), zt(n - 1)), WHITE)
    yf, zw2, zw1 = R(n_str), zt(n_str), zt(n_str + 1)                        # 6.00, W2 -1.89, W1 -2.10
    mb.box((X_W, Y_S, zw2), (X_W + b, yf, zw2 + b), WHITE)                   # W2 against the west wall
    mb.box((X_E, yf - b, zw2), (1.25, yf, zw2 + b), WHITE)                   # W2 against the pier
    mb.box((X_W, Y_S, zw1), (1.25, Y_S + b, zw1 + b), WHITE)                 # W1 against the south wall
    # the shell carries the R9 riser tile across the pier face (x 0.93..1.25): wall paint over it, 1 mm proud
    mb.box((X_E + 0.001, yf - 0.002, zw2 + b), (1.2495, yf - 0.001, zt(n_str - 1)), M.paint('#F3F2EE'))
    s = TT + 0.0008                                                          # trims sit 0.8 mm proud of the tile skin
    for n in range(2, n_str + 1):
        mb.box((X_W + 0.001, R(n) - s, zt(n - 1) - 0.010), (X_E - 0.001, R(n) + 0.010, zt(n - 1) + s), trim)
    p0, p1 = (X_W, Y_S), (1.25, yf)                                          # R10, the diagonal winder riser
    ln = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    mb.at(Matrix.Translation((*p0, 0)) @ Matrix.Rotation(math.atan2(p1[1] - p0[1], p1[0] - p0[0]), 4, 'Z'))
    mb.box((0.02, -s, zw2 - 0.010), (ln - 0.02, 0.010, zw2 + s), trim)
    mb.at()
    mb.box((1.240, Y_S, zw1 - 0.010), (1.25 + s, yf, zw1 + s), trim)         # R11
    ctx.add(mb.finish('basement_stair.beads'), ST, 'trim')

    ins = mo.MB()                                                            # shell bar: y 7.602..7.658, top 0.006
    for y in (7.613, 7.635):
        ins.box((X_W + 0.004, y, 0.0055), (0.871, y + 0.012, 0.0072), 'black_matt')
    ctx.add(ins.finish('basement_stair.nosing_inserts'), ST, 'trim')


TT = 0.002                                   # tile skin thickness
_COLS = [round(1024 * i / 6) for i in range(7)]                 # wood_tile_floor_dark_col.jpg (1024 x 2048 px):
_STAGGER = (0.0, 0.34, 0.71, 0.12, 0.60, 0.88)                  # 6 columns x 3 planks, gen/woods.py wood_tile_floor()
_TEX_W, _TEX_H = 1.221, 3.6105                                  # metres per repeat (manifest size_m)


def _plank(i, length):
    """UV rect (u0, u1, v0, v1) inside one whole plank of the texture, `length` metres of it along V (clamped)."""
    c, m = (i * 5 + 1) % 6, 6                                   # column; margin px clear of the grout
    cuts = sorted((j * 682 + int(_STAGGER[c] * 682)) % 2048 for j in range(3))
    r0, r1 = cuts[i % 2], cuts[i % 2 + 1]                      # a plank that does not wrap the image edge
    need = min(length / _TEX_H * 2048, r1 - r0 - 2 * m)
    ra = r0 + m + (i * 0.618 % 1) * (r1 - r0 - 2 * m - need)
    return (_COLS[c] + m) / 1024, (_COLS[c + 1] - m) / 1024, 1 - ra / 2048, 1 - (ra + need) / 2048


def _tiles(ctx):
    """2 mm wood-effect tile skin over the carcass treads and risers with explicit UVs: each straight tread and riser
    is one uncut plank laid across the stair, the winders W1 / W2 are planked parallel to R10 (basement.md 3.1)."""
    rise, going, y1, n = _stair(ctx)
    R = lambda k: y1 - going * (k - 1)
    zt = lambda k: -rise * k
    e, tile = 0.001, M.mat('wood_tile_floor_dark')
    yf, zw2, zw1, zf = R(n), zt(n), zt(n + 1), zt(n + 2)
    mb = mo.MB()
    for k in range(1, n):                                                    # T1..T8
        mb.box((X_W + e, R(k + 1), zt(k)), (X_E - e, R(k), zt(k) + TT), tile)
    for k in range(1, n + 1):                                                # R1..R9 (R1 stops under the threshold)
        mb.box((X_W + e, R(k) - TT, zt(k) + TT), (X_E - e, R(k), zt(k - 1) + (TT if k > 1 else 0)), tile)
    mb.prism([(X_W + e, yf, zw2), (1.25, yf, zw2), (X_W + e, Y_S + e, zw2)], (0, 0, TT), tile)          # W2
    mb.prism([(1.25, yf - e, zw1), (1.25, Y_S + e, zw1), (X_W + e, Y_S + e, zw1)], (0, 0, TT), tile)    # W1
    d = Vector((1.25 - X_W, yf - Y_S))
    ln = d.length
    d.normalize()
    mb.at(Matrix.Translation((X_W, Y_S, 0)) @ Matrix.Rotation(math.atan2(d.y, d.x), 4, 'Z'))
    mb.box((0, -TT, zw1 + TT), (ln, 0, zw2 + TT), tile)                      # R10, 2 mm proud toward W1
    mb.at()
    mb.box((1.25, Y_S + e, zf), (1.25 + TT, yf - e, zw1 + TT), tile)         # R11, faces the room
    ob = mb.finish('basement_stair.tiles')

    nd = Vector((d.y, -d.x))                                                 # across R10, toward W1
    uv = ob.data.uv_layers[0].data
    vs = ob.data.vertices
    for p in ob.data.polygons:
        c, nn = p.center, p.normal
        ax = max(range(3), key=lambda i: abs(nn[i]))
        if abs(nn.x) > 0.3 and abs(nn.y) > 0.3:                              # R10
            rect, st = _plank(32, ln), lambda q: ((q.z - zw1) / rise, (q.x - X_W) * d.x + (q.y - Y_S) * d.y)
            sc = (1.0, ln)
        elif ax == 2 and round(-c.z / rise) >= n:                            # W2, W1: world planks along R10,
            rect = None                                                      # a column joint on the R10 line
        elif ax == 2:
            k = round(-c.z / rise)
            rect, st, sc = _plank(k, X_E - X_W), lambda q, k=k: ((q.y - R(k + 1)) / going, q.x - X_W), (1, X_E - X_W)
        elif ax == 1:
            k = int(-c.z / rise) + 1
            rect, st, sc = _plank(20 + k, X_E - X_W), lambda q, k=k: ((q.z - zt(k)) / rise, q.x - X_W), (1, X_E - X_W)
        else:                                                                # R11 (and the 2 mm side faces)
            rect, st, sc = _plank(31, yf - Y_S), lambda q: ((q.z - zf) / rise, q.y - Y_S), (1, yf - Y_S)
        for li in p.loop_indices:
            q = vs[ob.data.loops[li].vertex_index].co
            if rect is None:
                a, b = (q.x - X_W) * d.x + (q.y - Y_S) * d.y, (q.x - X_W) * nd.x + (q.y - Y_S) * nd.y
                uv[li].uv = (b / _TEX_W, a / _TEX_H)
                continue
            s_, t_ = st(q)
            s_, t_ = min(max(s_ / sc[0], 0), 1), min(max(t_ / sc[1], 0), 1)
            uv[li].uv = (rect[0] + s_ * (rect[1] - rect[0]), rect[2] + t_ * (rect[3] - rect[2]))
    ctx.add(ob, ST, 'fit')


def _extinguisher(ctx):
    x, y, z = X_JOG + 0.067, 7.38, 0.38
    red, blk = M.solid('bs_ext_red', '#C8281E', 0.3), 'black_matt'
    mb = mo.MB()
    mb.box((X_JOG, y - 0.02, z + 0.17), (x, y + 0.02, z + 0.20), blk)        # wall bracket + strap
    mb.at(Matrix.Translation((x, y, z)))
    mb.lathe([(0, 0), (0.056, 0), (0.057, 0.004), (0.057, 0.022)], blk, 16)
    mb.lathe([(0.055, 0.022), (0.055, 0.27), (0.046, 0.305), (0.022, 0.33), (0.02, 0.345)], red, 16)
    mb.lathe([(0.057, 0.17), (0.057, 0.20)], blk, 16)
    mb.box((-0.018, -0.018, 0.34), (0.018, 0.018, 0.362), blk, bev=0.003)
    mb.box((-0.012, -0.012, 0.362), (0.07, 0.012, 0.37), blk)                # squeeze lever
    mb.tube([(0.03, 0.03, 0.345), (0.062, 0.045, 0.27), (0.066, 0.04, 0.13), (0.062, 0.03, 0.06)], 0.008, blk, 6)
    ctx.add(mb.finish('basement_stair.extinguisher'), ST, 'fit')


def _ornaments(ctx):
    """D3..D8 on the wide part of the shelf. Moved ~0.4 north of the spec so they clear the model's soffit."""
    zc, x = SHELF_Z + CAP_T, 0.218
    oak, cream = 'dark_oak_antique', M.solid('bs_card', '#EFE8D2', 0.8)
    mb = mo.MB()
    mb.at(Matrix.Translation((x, 5.63, zc + 0.0125)) @ Matrix.Rotation(math.radians(90), 4, 'X'))
    mb.lathe([(0, -0.022), (0.0125, -0.022), (0.0125, 0.022), (0, 0.022)], 'cork', 8)             # D7 cork on its side
    mb.at(Matrix.Translation((x, 5.74, zc)))                                                       # D3 green bottle
    mb.lathe([(0, 0.004), (0.034, 0), (0.0375, 0.01), (0.0375, 0.15), (0.03, 0.185), (0.014, 0.215), (0.0125, 0.28),
              (0.016, 0.283), (0.016, 0.292), (0.0125, 0.295)], M.solid('bs_bottle_green', '#24402A', 0.06), 14)
    mb.lathe([(0, 0.27), (0.0115, 0.27), (0.0115, 0.305), (0, 0.305)], 'cork', 8)
    mb.at()
    mb.box((x - 0.05, 5.80, zc), (x + 0.05, 5.94, zc + 0.065), oak, bev=0.003)                     # D4 box, stepped lid
    mb.box((x - 0.054, 5.796, zc + 0.065), (x + 0.054, 5.944, zc + 0.078), oak, bev=0.003)
    mb.box((x - 0.04, 5.81, zc + 0.078), (x + 0.04, 5.93, zc + 0.09), oak, bev=0.004)
    # leaning on the wall: foot `off` out, top on the wall
    lean = lambda y, off, deg: Matrix.Translation((X_UP + off, y, zc)) @ Matrix.Rotation(math.radians(-deg), 4, 'Y')
    mb.at(lean(6.03, 0.028, 14))
    mb.box((0, -0.07, 0), (0.002, 0.07, 0.10), cream)                                              # D5 card: blank
    mb.at(lean(6.15, 0.022, 16))
    mb.box((0, -0.035, 0), (0.015, 0.035, 0.07), M.solid('bs_tile', '#E9E2CF', 0.15), bev=0.002)   # D6 tile
    mb.at()
    mb.box((x - 0.04, 6.22, zc), (x + 0.04, 6.30, zc + 0.03), oak, bev=0.003)                      # D6 block
    ctx.add(mb.finish('basement_stair.shelf_ornaments'), ST, 'decor')

    # D8 narrow gilt frame with a two-pronged fork, slightly askew on the upper wall
    fr = mo.MB()
    w, h, d, fw = 0.09, 0.36, 0.03, 0.018
    fr.at(Matrix.Translation((X_UP, 6.06, 0.46)) @ Matrix.Rotation(math.radians(-3), 4, 'X'))
    for ya, yb, za, zb in ((-w / 2, -w / 2 + fw, -h / 2, h / 2), (w / 2 - fw, w / 2, -h / 2, h / 2),
                           (-w / 2, w / 2, -h / 2, -h / 2 + fw), (-w / 2, w / 2, h / 2 - fw, h / 2)):
        fr.box((0, ya, za), (d, yb, zb), 'gilt_bright', bev=0.004)
    fr.box((0, -w / 2 + 0.01, -h / 2 + 0.01), (0.012, w / 2 - 0.01, h / 2 - 0.01), M.solid('bs_frame_back', '#2E3A30', 0.9))
    fr.box((0.012, -0.006, -0.15), (0.02, 0.006, -0.03), oak, bev=0.002)                           # handle
    fr.box((0.013, -0.003, -0.03), (0.018, 0.003, 0.04), 'silver_satin')                           # shank
    for s in (-1, 1):
        fr.box((0.013, s * 0.009 - 0.002, 0.04), (0.018, s * 0.009 + 0.002, 0.15), 'silver_satin')  # prongs
    fr.box((0.013, -0.011, 0.035), (0.018, 0.011, 0.043), 'silver_satin')
    ctx.add(fr.finish('basement_stair.fork_frame'), ST, 'decor')


def ceiling_light(ctx, room, name, loc, dia, depth, watts, matrix=None):
    """Round flush LED fitting: white pan + opal diffuser with a glowing side band, and its emitter."""
    r = dia / 2
    mb = mo.MB()
    mb.at(matrix if matrix is not None else Matrix.Translation(loc))
    mb.lathe([(0, -depth), (r - 0.03, -depth + 0.003), (r - 0.004, -depth + 0.02), (r, -0.022)],
             P.emissive('#FFE9C4', 9.0), 24)
    mb.lathe([(r, -0.022), (r + 0.002, -0.02), (r + 0.002, 0)], 'plastic_white', 24)
    ctx.add(mb.finish(name), room, 'light')
    m = matrix if matrix is not None else Matrix.Translation(loc)
    # 3000 K = the house white balance: whites render neutral as filmed (3200 K left a blue / pink cast on wood)
    lighting.bulb(ctx, room, tuple(m @ Matrix.Translation((0, 0, -depth - 0.06)).to_translation()), watts=watts,
                  kelvin=3000, radius=0.07, name=name + '.lamp')


def _lights(ctx):
    y = 5.95                                                                 # L-S on the rake over the foot of the flight
    m = ctx.stair('stair_main')
    pitch = math.atan(m['rise'] / m['going'])
    ceiling_light(ctx, ST, 'basement_stair.light', None, 0.30, 0.06, 35,
                  Matrix.Translation((0.60, y, soffit(ctx, y))) @ Matrix.Rotation(pitch, 4, 'X'))
    # SW-B: one rocker on the east wall just inside the door, 1.20 above the hall floor; all three lights (spec 8)
    xf = next(X_E + 0.005 * i for i in range(40) if shell.is_solid(ctx, X_E + 0.005 * i + 0.003, 7.42, 1.20))
    sw = P.place(P.switch_plate(1, name='basement_stair.switch'), (xf, 7.42, 1.20), facing=(-1, 0))
    IX.tag(sw, 'light', rooms=[ST, RM], label='Basement lights')
    ctx.add(sw, ST, 'fit', lm='dynamic')


def build(ctx):
    _shaft(ctx)
    _tiles(ctx)
    _steps(ctx)
    _extinguisher(ctx)
    _ornaments(ctx)
    _lights(ctx)
    plant.build(ctx, ceiling_light)

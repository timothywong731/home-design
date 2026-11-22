"""Workshop interior of the shed (spec/rooms/shed.md 6.2): benches, generic machines, racking, clamps, trim.

The frame is read from spec/house.json by setup(ctx): workshop inside faces X0..X1 x Y0..Y1, floor ZF, ceiling ZC, plus
the veranda paving ZP and soffit ZS (RECONCILE3 garden-13 / -16 / -18: the building moved 1.70..1.85 north and the
ceiling rose to 2.13). Each group is modelled in its own local frame and placed with `mb.finish(name, T(x, y))` at an
anchor taken from that frame, so the layout follows the spec: the island keeps 1.08 to the front wall and 0.61 to the
back bench, the benches stand against their walls. x is as in phase 2 (only y moved), z stays world.
Machines are generic shapes, no brands.
"""
import math
import random

from mathutils import Matrix

from lib import materials as M, mouldings as mo, props as P

ZP, ZF, ZC, ZS = -0.42, -0.32, 2.13, 2.02        # veranda paving, workshop floor, workshop ceiling, veranda soffit
X0, X1, Y0, Y1 = -0.60, 4.18, 26.98, 30.47       # workshop inside faces (setup() re-reads them from the spec)
PINE = 'oak_light'                               # planed softwood (#D2BC94 in the spec, key mean #C9A877)


def setup(ctx):
    """Read the building frame from the spec (exterior.buildings[shed])."""
    global ZP, ZF, ZC, ZS, X0, X1, Y0, Y1
    b = next(b for b in ctx.spec['exterior']['buildings'] if b['id'] == 'shed')
    xs, ys = zip(*ctx.room_poly('shed_workshop'))
    X0, X1, Y0, Y1 = min(xs), max(xs), min(ys), max(ys)
    ZP, ZS = b['datumZ'], b['roof']['verandaSoffitZ']
    ZF, ZC = ctx.floor_z('shed_workshop'), ctx.ceil_z('shed_workshop')


def T(x, y):
    return Matrix.Translation((x, y, 0.0))


def C(hx, rough=0.8, metal=0.0):
    """Plain colour, cached by its values."""
    return M.solid('shed_%s_%d_%d' % (hx.lstrip('#'), rough * 100, metal * 100), hx, rough, metal)


def cyl(mb, p, r, h, mat, axis='z', segs=12, r1=None):
    """Capped cylinder / cone from p along +axis (keeps the builder's transform)."""
    rot = {'z': Matrix.Identity(4), 'x': Matrix.Rotation(math.pi / 2, 4, 'Y'), 'y': Matrix.Rotation(-math.pi / 2, 4, 'X')}[axis]
    M0 = mb.M.copy()
    mb.at(M0 @ Matrix.Translation(p) @ rot)
    mb.lathe([(0, 0), (r, 0), (r if r1 is None else r1, h), (0, h)], mat, segs)
    mb.at(M0)


def bench(mb, x0, x1, y0, y1, h, top=None, shelf=None, braces=False, castors=False, over=0.02, z0=None, tt=0.036):
    """Softwood bench frame: 70 mm legs, top rails, optional low shelf at `shelf` above the floor, knee braces, castors.
    `top` = material of a plain slab top (None: the caller lays its own on z0 + h - tt). -> z of the frame top."""
    z0 = ZF if z0 is None else z0
    L, zt, zl = 0.07, z0 + h - tt, z0 + (0.075 if castors else 0.0)
    lx = (x1 - x0) >= (y1 - y0)                              # long axis a, short axis b
    a0, a1, b0, b1 = (x0, x1, y0, y1) if lx else (y0, y1, x0, x1)

    def bx(al, ah, bl, bh, zl_, zh, m=PINE, **kw):
        mb.box((al, bl, zl_) if lx else (bl, al, zl_), (ah, bh, zh) if lx else (bh, ah, zh), m, **kw)

    def pt(a, b, z):
        return (a, b, z) if lx else (b, a, z)

    n = max(2, round((a1 - a0) / 1.2) + 1)
    for i in range(n):
        a = a0 + (a1 - a0 - L) * i / (n - 1)
        for b in (b0, b1 - L):
            bx(a, a + L, b, b + L, zl, zt, bev=0.003, grain=2)
            if castors:
                bx(a + 0.01, a + 0.06, b + 0.01, b + 0.06, z0 + 0.05, zl, C('#9A9DA0', 0.4, 0.8))
                cyl(mb, pt(a + 0.035, b + 0.02, z0 + 0.027), 0.027, 0.03, 'black_matt', 'y' if lx else 'x', 10)
        bx(a + 0.012, a + L - 0.012, b0 + L, b1 - L, zt - 0.095, zt)
        if shelf:
            bx(a + 0.012, a + L - 0.012, b0 + L, b1 - L, z0 + shelf - 0.07, z0 + shelf)
        if braces:                                            # 45-degree knee braces along the bench, front and back
            for s in ((1,) if i == 0 else (-1,) if i == n - 1 else (-1, 1)):
                e = a + L if s > 0 else a
                for b in (b0 + 0.014, b1 - 0.045):
                    mb.prism([pt(e, b, zt - 0.47), pt(e + s * 0.38, b, zt - 0.09), pt(e + s * 0.38, b, zt - 0.01),
                              pt(e, b, zt - 0.39)], pt(0, 0.031, 0), PINE)
    for b in (b0 + 0.012, b1 - 0.047):
        bx(a0 + L, a1 - L, b, b + 0.035, zt - 0.095, zt)
        if shelf:
            bx(a0 + L, a1 - L, b, b + 0.035, z0 + shelf - 0.07, z0 + shelf)
    if shelf:
        bx(a0 + 0.01, a1 - 0.01, b0 + 0.01, b1 - 0.01, z0 + shelf, z0 + shelf + 0.018, C('#C9B79A', 0.85))
    if top is not None:
        bx(a0 - over, a1 + over, b0 - over, b1 + over, zt, zt + tt, top, bev=0.003)
    return zt


# ------------------------------------------------------------------ island: bench, mitre saw, table saw, offcuts
ISLAND = (2.40, 1.20)                                        # spec 6.2: 2.40 x 1.20 x 0.90


def island_anchor():
    """SW corner of the island: x as phase 2 (local x 1.2), 1.08 off the front wall (v2 f_0283 / f_0287)."""
    return X0 + 0.93, Y0 + 1.08


def island(ctx, room):
    ox, oy = island_anchor()
    W, D = ISLAND
    mdf, mb = C('#C9B79A', 0.85), mo.MB()
    zt = bench(mb, 0, W, 0, D, 0.90, shelf=0.18)
    top = zt + 0.036
    for a, b in (((-.02, -.02), (0.57, D + .02)), ((1.17, -.02), (1.73, D + .02)),
                 ((0.57, -.02), (1.17, 0.72)), ((1.73, -.02), (W + .02, 0.58))):            # top panels round the two saws
        mb.box((*a, zt), (*b, top), mdf, bev=0.003)
    mb.box((0.57, 0.72, top - 0.126), (1.17, D + .02, top - 0.09), mdf)                    # sunk well under the mitre saw
    ctx.add(mb.finish('shed.island', T(ox, oy)), room, 'fit', plan_sym='workbench')

    mb = mo.MB()                                                                           # generic saws
    dark, alu, yel = C('#3A3D40', 0.5), C('#B8BBBD', 0.35, 0.7), C('#E0B32A', 0.45)
    zw = top - 0.09                                                                        # mitre saw in the well,
    zh = zw + 0.42                                                                         # head raised: top 0.42 above
    mb.box((0.62, 0.78, zw), (1.12, 1.14, zw + 0.07), C('#8E9296', 0.4, 0.6), bev=0.004)   # the island (v2:f_0291)
    cyl(mb, (0.87, 0.94, zw + 0.07), 0.13, 0.022, dark, segs=20)                           # turntable
    mb.box((0.62, 1.05, zw + 0.07), (1.12, 1.07, zw + 0.15), alu)                          # fence
    mb.box((0.82, 1.07, zw + 0.07), (0.92, 1.16, zh + 0.05), dark, bev=0.006)              # pivot post
    for x in (0.84, 0.90):                                                                 # slide rails
        cyl(mb, (x, 0.80, zh + 0.03), 0.011, 0.36, alu, 'y', 8)
    mb.box((0.825, 0.86, zh - 0.01), (0.915, 1.00, zh + 0.07), yel, bev=0.006)             # head housing on the rails
    cyl(mb, (0.863, 0.92, zh - 0.12), 0.125, 0.004, C('#A9ADB0', 0.3, 0.9), 'x', 20)       # blade
    M0 = mb.M.copy()
    mb.at(M0 @ Matrix.Translation((0.835, 0.92, zh - 0.12)) @ Matrix.Rotation(math.pi / 2, 4, 'Y'))
    mb.lathe([(0, 0), (.137, 0), (.137, .06), (0, .06)], yel, 12, a0=math.pi / 2, a1=3 * math.pi / 2)   # upper guard
    mb.at(M0)
    mb.box((0.835, 0.783, zh - 0.121), (0.895, 1.057, zh - 0.119), yel)
    cyl(mb, (0.895, 0.92, zh - 0.10), 0.055, 0.13, dark, 'x', 12)                          # motor, yellow end cap
    cyl(mb, (1.025, 0.92, zh - 0.10), 0.057, 0.025, yel, 'x', 12)
    mb.box((0.84, 0.74, zh + 0.03), (0.90, 0.86, zh + 0.09), dark, bev=0.006)              # handle
    mb.box((0.855, 0.82, zh - 0.02), (0.885, 0.86, zh + 0.05), dark)
    zs = ZF + 0.198                                                                        # table saw on the low shelf
    mb.box((1.81, 0.64, zs), (2.32, 1.11, top - 0.027), dark, bev=0.004)      # inside the end legs
    mb.box((1.77, 0.60, top - 0.027), (2.42, 1.15, top + 0.002), alu, bev=0.003)
    mb.box((1.92, 0.84, top + 0.002), (2.27, 0.90, top + 0.003), C('#A03028', 0.5))        # throat plate
    mb.box((1.77, 1.05, top + 0.002), (2.42, 1.11, top + 0.06), C('#E6E6E2', 0.4))         # rip fence
    cyl(mb, (2.09, 0.625, zs + 0.17), 0.05, 0.02, 'black_matt', 'y', 12)                   # height wheel
    mb.box((2.30, 0.56, zs + 0.24), (2.36, 0.64, zs + 0.30), C('#C0302A', 0.5), bev=0.004)  # paddle switch
    ctx.add(mb.finish('shed.island.saws', T(ox, oy)), room, 'furn')

    mb, rnd = mo.MB(), random.Random(5)                                                    # a few plain offcuts on the shelf
    z = ZF + 0.198
    for i, (x, y, l, w, deg) in enumerate(((0.22, 0.25, 0.9, 0.14, 4), (0.42, 0.50, 1.2, 0.09, -3), (0.27, 0.75, 0.7, 0.19, 8),
                                           (0.72, 0.95, 1.0, 0.07, -5), (0.57, 0.32, 0.6, 0.12, 14), (1.02, 0.65, 0.5, 0.2, -9))):
        mb.at(Matrix.Translation((x, y, z + 0.02 * (i // 4))) @ Matrix.Rotation(math.radians(deg), 4, 'Z'))
        mb.box((0, -w / 2, 0), (l, w / 2, 0.02), PINE if rnd.random() < 0.6 else mdf)
    mb.at()
    ctx.add(mb.finish('shed.island.offcuts', T(ox, oy)), room, 'decor')


# ------------------------------------------------------------------ back-wall bench: pillar drill, thicknesser, extractor
def back_bench(ctx, room):
    ox, oy = X0 + 1.33, Y1                                   # west end (local x 1.6), back wall face; local y < 0
    mb = mo.MB()
    top = bench(mb, 0, 2.77, -0.60, -0.02, 0.92, top=PINE, braces=True) + 0.036            # ends short of the east bench
    ctx.add(mb.finish('shed.bench_back', T(ox, oy)), room, 'fit', plan_sym='workbench')

    mb = mo.MB()
    blue, dark, steel = C('#56677A', 0.45), C('#2E3033', 0.5), C('#A9ADB0', 0.3, 0.9)
    x, y = 0.25, -0.32                                                                     # pillar drill, west end
    mb.box((x - 0.11, y - 0.14, top), (x + 0.11, y + 0.18, top + 0.03), blue, bev=0.004)
    cyl(mb, (x, y + 0.11, top + 0.03), 0.022, 0.50, steel)
    cyl(mb, (x, y - 0.02, top + 0.20), 0.085, 0.015, dark, segs=16)                        # table
    mb.box((x - 0.02, y - 0.02, top + 0.185), (x + 0.02, y + 0.13, top + 0.215), dark)
    mb.box((x - 0.07, y - 0.10, top + 0.47), (x + 0.07, y + 0.17, top + 0.62), blue, bev=0.006)   # head
    cyl(mb, (x, y + 0.17, top + 0.44), 0.055, 0.16, C('#8E9296', 0.4, 0.6))                # motor
    cyl(mb, (x, y - 0.03, top + 0.39), 0.018, 0.08, dark)                                  # chuck
    for a in (0.4, 2.5, 4.6):                                                              # feed handle spokes
        mb.tube([(x + 0.075, y + 0.02, top + 0.52), (x + 0.085, y + 0.02 + 0.1 * math.cos(a), top + 0.52 + 0.1 * math.sin(a))],
                0.005, steel, n=5)
    x, y = 2.39, -0.30                                                                     # pale-wood boxed thicknesser, east end
    mb.box((x - 0.17, y - 0.17, top), (x + 0.17, y + 0.17, top + 0.03), dark)
    mb.box((x - 0.15, y - 0.15, top + 0.03), (x + 0.15, y + 0.15, top + 0.33), C('#DCC79C', 0.7), bev=0.004)
    mb.box((x - 0.10, y - 0.153, top + 0.20), (x + 0.10, y - 0.15, top + 0.29), C('#B79F78', 0.8))
    cyl(mb, (x, y, top + 0.33), 0.012, 0.035, dark, segs=8)
    cyl(mb, (x, y, top + 0.365), 0.035, 0.012, dark, segs=10)
    x, y = 1.97, -0.31                                                                     # dust extractor drum under the bench
    cyl(mb, (x, y, ZF), 0.175, 0.50, C('#4F6078', 0.5), segs=20)
    cyl(mb, (x, y, ZF + 0.50), 0.18, 0.03, dark, segs=20)
    cyl(mb, (x, y - 0.06, ZF + 0.53), 0.03, 0.04, dark, segs=8)
    x, y = 1.45, -0.30                                                                     # grey workshop vacuum beside it (v2 f_0282)
    grey = C('#A9ADB0', 0.35, 0.6)
    cyl(mb, (x, y, ZF + 0.03), 0.165, 0.40, grey, segs=16)
    mb.at(Matrix.Translation((x, y, ZF + 0.43)))
    mb.lathe([(0, 0), (.17, 0), (.16, .07), (.10, .11), (0, .12)], dark, 16)
    mb.at()
    for a in (0.6, 2.7, 4.8):                                                              # castors
        cyl(mb, (x + 0.13 * math.cos(a), y + 0.13 * math.sin(a), ZF), 0.025, 0.03, 'black_matt', segs=8)
    ctx.add(mb.finish('shed.bench_back.machines', T(ox, oy)), room, 'furn')

    # pale flexible extraction hose from the drum, along the floor, up to the back of the table saw (v2 f_0282 / f_0287)
    ix, iy = island_anchor()
    sx, sy = ix + 2.09, iy + ISLAND[1] - 0.06
    dx, dy = ox + 1.97, oy - 0.37
    mb = mo.MB()
    mb.tube([(dx, dy, ZF + 0.53), (dx, dy - 0.12, ZF + 0.40), (dx - 0.10, dy - 0.25, ZF + 0.05),
             ((dx + sx) / 2, (dy + sy) / 2, ZF + 0.03), (sx + 0.05, sy + 0.12, ZF + 0.06), (sx, sy + 0.02, ZF + 0.30)],
            0.027, C('#D9CFA6', 0.55), n=10)
    ctx.add(mb.finish('shed.extractor_hose'), room, 'decor')


# ------------------------------------------------------------------ east-wall bench on castors: desktop CNC
def east_bench(ctx, room):
    ox, oy = X1, Y1 - 0.02                                   # north end at the back wall; local x, y < 0
    L = 2.40                                                 # spec 6.2: 2.4 x 0.60; starts 1.07 inside the front wall
    mb = mo.MB()
    top = bench(mb, -0.60, -0.02, -L, 0, 0.90, top=PINE, shelf=0.25, castors=True) + 0.036
    ctx.add(mb.finish('shed.bench_east', T(ox, oy)), room, 'fit', plan_sym='workbench')

    mb, blk, sil = mo.MB(), C('#1C1D1F', 0.45), C('#B4B8BB', 0.3, 0.9)
    mb.box((-0.55, -0.88, top), (-0.05, -0.28, top + 0.04), blk, bev=0.004)                # bed
    for x in (-0.54, -0.10):
        mb.box((x, -0.58, top + 0.04), (x + 0.04, -0.51, top + 0.34), blk)                 # gantry uprights
    mb.box((-0.54, -0.57, top + 0.27), (-0.06, -0.52, top + 0.35), blk)
    mb.box((-0.35, -0.63, top + 0.20), (-0.25, -0.57, top + 0.40), blk)                    # carriage
    cyl(mb, (-0.30, -0.66, top + 0.12), 0.032, 0.26, sil)                                  # spindle
    cyl(mb, (-0.30, -0.66, top + 0.07), 0.006, 0.05, sil, segs=6)
    mb.tube([(-0.30, -0.61, top + 0.40), (-0.32, -0.48, top + 0.46), (-0.38, -0.34, top + 0.36), (-0.40, -0.30, top + 0.06)],
            0.012, blk, n=6)                                                               # one cable chain
    mb.box((-0.50, -1.34, top), (-0.15, -1.04, top + 0.045), C('#B5524E', 0.5), bev=0.006)  # red tray
    mb.box((-0.48, -1.32, top + 0.045), (-0.17, -1.06, top + 0.046), C('#8E3F3C', 0.6))
    zs = ZF + 0.25 + 0.018                                                                 # white crate on the low shelf (v2 f_0282)
    mb.box((-0.52, -1.85, zs), (-0.10, -1.30, zs + 0.30), C('#ECECE8', 0.45), bev=0.008)
    mb.box((-0.51, -1.84, zs + 0.30), (-0.11, -1.31, zs + 0.31), C('#D9D9D4', 0.45))
    ctx.add(mb.finish('shed.cnc', T(ox, oy)), room, 'furn')

    # sheet goods leaning on the bench's west edge at its south end: a white-primed frame and a plywood board side by side
    # (v2 f_0279, f_0281); feet 0.27 / 0.20 off the bench, the lane to the island stays 0.54
    mb, white, ply, s = mo.MB(), C('#ECEAE3', 0.6), C('#D8C49C', 0.8), 0.045
    xe, ys = ox - 0.62, oy - L + 0.05
    for foot, y, w, h, t in ((0.27, 0.0, 0.80, 1.50, s), (0.20, 0.86, 0.60, 1.22, 0.018)):
        a = math.atan((foot - t) / 0.90)                     # its bench-side face meets the top's edge 0.90 up
        mb.at(Matrix.Translation((xe - foot, ys + y, ZF + t * math.sin(a))) @ Matrix.Rotation(a, 4, 'Y'))   # outer edge on the floor
        if t == s:                                           # open 45 mm frame, no brace (v2 f_0281)
            mb.box((0, 0, 0), (s, w, s), white)
            mb.box((0, 0, h - s), (s, w, h), white)
            mb.box((0, 0, s), (s, s, h - s), white)
            mb.box((0, w - s, s), (s, w, h - s), white)
        else:
            mb.box((0, 0, 0), (t, w, h), ply)
    mb.at()
    ctx.add(mb.finish('shed.sheet_goods'), room, 'decor', plan_sym='rack')        # blocks: not walked through


# ------------------------------------------------------------------ boltless steel racking, NW corner
def racking(ctx, room):
    ox, oy = X0, Y1                                          # NW inside corner; local x > 0, y < 0
    x0, x1, y0, y1, H = 0.08, 0.98, -0.47, -0.02, 1.80
    mb, blk, chip = mo.MB(), C('#1E1F21', 0.45, 0.6), C('#B79F78', 0.9)
    levels = [ZF + z for z in (0.08, 0.50, 0.92, 1.34, 1.76)]
    for x in (x0, x1 - 0.035):
        for y in (y0, y1 - 0.035):
            mb.box((x, y, ZF), (x + 0.035, y + 0.035, ZF + H), blk)
    for z in levels:
        for y in (y0, y1 - 0.012):
            mb.box((x0 + 0.035, y, z - 0.05), (x1 - 0.035, y + 0.012, z), blk)
        mb.box((x0 + 0.02, y0 + 0.012, z - 0.016), (x1 - 0.02, y1 - 0.012, z), chip)
    ctx.add(mb.finish('shed.racking', T(ox, oy)), room, 'fit', plan_sym='rack')

    mb, rnd = mo.MB(), random.Random(3)                       # generic contents: cases, boxes, bottles; toolbox + reel on top
    card = C('#B08D5F', 0.9)
    mb.box((0.14, -0.42, levels[0]), (0.54, -0.10, levels[0] + 0.12), C('#2B3A55', 0.5), bev=0.006)
    mb.box((0.58, -0.40, levels[0]), (0.92, -0.12, levels[0] + 0.15), C('#232426', 0.5), bev=0.006)
    mb.box((0.15, -0.40, levels[1]), (0.50, -0.10, levels[1] + 0.24), card)
    mb.box((0.56, -0.38, levels[1]), (0.90, -0.12, levels[1] + 0.18), card)
    mb.box((0.62, -0.38, levels[3]), (0.92, -0.10, levels[3] + 0.20), card)
    cols = ('#E8E6DF', '#C9CCD0', '#A8762E', '#3F5F8A', '#6C7A4A', '#D9D2B8')
    for z, xs in ((levels[2], [0.16 + 0.09 * i for i in range(9)]), (levels[3], [0.16 + 0.1 * i for i in range(4)])):
        for x in xs:
            r, h, col = rnd.uniform(0.028, 0.04), rnd.uniform(0.14, 0.25), C(rnd.choice(cols), 0.4)
            y = rnd.uniform(-0.36, -0.26)
            cyl(mb, (x, y, z), r, h, col, segs=8)
            cyl(mb, (x, y, z + h), r * 0.45, 0.03, C('#2A2A2C', 0.5), segs=6)
    red = C('#8E3F30', 0.5, 0.3)                                                           # rust-red steel toolbox
    mb.box((0.14, -0.38, levels[4]), (0.56, -0.16, levels[4] + 0.17), red, bev=0.006)
    mb.box((0.14, -0.32, levels[4] + 0.17), (0.56, -0.22, levels[4] + 0.20), red, bev=0.006)
    mb.tube([(0.27, -0.27, levels[4] + 0.20), (0.27, -0.27, levels[4] + 0.235), (0.43, -0.27, levels[4] + 0.235),
             (0.43, -0.27, levels[4] + 0.20)], 0.006, C('#2A2A2C', 0.5), n=5)
    yel = C('#E0B32A', 0.45)                                                               # yellow cable reel
    for y in (-0.33, -0.245):
        cyl(mb, (0.78, y, levels[4] + 0.14), 0.13, 0.015, yel, 'y', 16)
    cyl(mb, (0.78, -0.315, levels[4] + 0.14), 0.085, 0.07, C('#232426', 0.6), 'y', 12)
    mb.box((0.66, -0.34, levels[4]), (0.90, -0.22, levels[4] + 0.015), C('#232426', 0.6))
    ctx.add(mb.finish('shed.racking.items', T(ox, oy)), room, 'decor')


# ------------------------------------------------------------------ wall-hung: clamps, disc rack
def wall_things(ctx, room):
    mb = mo.MB()                                              # four red bar clamps on a board, back wall
    red, steel = C('#B0302A', 0.45), C('#A9ADB0', 0.3, 0.9)
    zb = ZF + 1.90
    mb.box((1.06, -0.03, zb - 0.06), (1.35, 0, zb), PINE)
    for i in range(4):
        x, drop = 1.10 + 0.07 * i, (0.62, 0.50, 0.62, 0.50)[i]
        mb.box((x - 0.003, -0.055, zb - drop), (x + 0.003, -0.035, zb + 0.05), steel)
        mb.box((x - 0.011, -0.12, zb), (x + 0.011, -0.005, zb + 0.05), red)               # fixed jaw hooked over the board
        zj = zb - drop + 0.12
        mb.box((x - 0.011, -0.12, zj), (x + 0.011, -0.03, zj + 0.05), red)
        cyl(mb, (x, -0.09, zj - 0.10), 0.013, 0.10, 'black_matt', segs=8)
    ctx.add(mb.finish('shed.clamps', T(X0, Y1)), room, 'decor')

    mb = mo.MB()                                              # timber rack of round brown discs, west wall (local y 3.6)
    brown = C('#6B4A35', 0.8)
    mb.box((0, -0.25, ZF + 1.50), (0.02, 0.35, ZF + 1.75), PINE)
    for z in (ZF + 1.565, ZF + 1.685):
        for i in range(5):
            cyl(mb, (0.02, -0.17 + 0.11 * i, z), 0.048, 0.05, brown, 'x', 12)
    ctx.add(mb.finish('shed.wall_rack', T(X0, (Y0 + Y1) / 2)), room, 'decor')


# ------------------------------------------------------------------ coving and skirting (site leaves them to this module)
def trim(ctx, room):
    white = M.paint('#EFEEEA')
    cove = mo.sweep('cove_70', [(X0, Y0, ZC), (X1, Y0, ZC), (X1, Y1, ZC), (X0, Y1, ZC)], closed=True, name='shed.cove',
                    material=white)
    ctx.add(cove, room, 'trim')
    f = ctx.opening_frame('shed_d1')                         # 70 mm square-edge skirting, stops at the French doors
    dx0 = f['center'][0] - f['width'] / 2
    sk = mo.sweep([(0.015, 0.0), (0.015, 0.07), (0.0, 0.07)],
                  [(X1, Y0, ZF), (X1, Y1, ZF), (X0, Y1, ZF), (X0, Y0, ZF), (dx0, Y0, ZF)], name='shed.skirting')
    ctx.add(sk, room, 'trim')


def build(ctx, room):
    setup(ctx)
    island(ctx, room)
    back_bench(ctx, room)
    east_bench(ctx, room)
    racking(ctx, room)
    wall_things(ctx, room)
    trim(ctx, room)

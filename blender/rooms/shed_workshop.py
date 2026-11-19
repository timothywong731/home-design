"""Workshop interior of the shed (spec/rooms/shed.md 6.2): benches, generic machines, racking, clamps, trim.

Everything is modelled in WORLD coordinates (objects sit at the origin), so the numbers below read straight off the
spec: world = shed-local + (-0.87, 23.40), z_world = z_local - 0.42. Machines are generic shapes, no brands.
"""
import math
import random

from mathutils import Matrix

from lib import materials as M, mouldings as mo, props as P

ZP, ZF, ZC, ZS = -0.42, -0.32, 1.98, 1.83        # veranda paving, workshop floor, workshop ceiling, veranda soffit
X0, X1, Y0, Y1 = -0.60, 4.18, 25.28, 28.62       # workshop inside faces
PINE = 'oak_light'                               # planed softwood (#D2BC94 in the spec, key mean #C9A877)


def C(hx, rough=0.8, metal=0.0):
    """Plain colour, cached by its values."""
    return M.solid('shed_%s_%d_%d' % (hx.lstrip('#'), rough * 100, metal * 100), hx, rough, metal)


def cyl(mb, p, r, h, mat, axis='z', segs=12, r1=None):
    """Capped cylinder / cone from p along +axis."""
    rot = {'z': Matrix.Identity(4), 'x': Matrix.Rotation(math.pi / 2, 4, 'Y'), 'y': Matrix.Rotation(-math.pi / 2, 4, 'X')}[axis]
    mb.at(Matrix.Translation(p) @ rot)
    mb.lathe([(0, 0), (r, 0), (r if r1 is None else r1, h), (0, h)], mat, segs)
    mb.at()


def bench(mb, x0, x1, y0, y1, h, top=None, shelf=None, braces=False, castors=False, over=0.02, z0=ZF, tt=0.036):
    """Softwood bench frame: 70 mm legs, top rails, optional low shelf at `shelf` above the floor, knee braces, castors.
    `top` = material of a plain slab top (None: the caller lays its own on z0 + h - tt). -> z of the frame top."""
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
def island(ctx, room):
    x0, x1, y0, y1 = 0.33, 2.73, 26.30, 27.50                # local 1.2-3.6 x 2.9-4.1, top 0.90 above the floor
    mdf, mb = C('#C9B79A', 0.85), mo.MB()
    zt = bench(mb, x0, x1, y0, y1, 0.90, shelf=0.18)
    top = zt + 0.036
    for a, b in (((x0 - .02, y0 - .02), (0.90, y1 + .02)), ((1.50, y0 - .02), (2.06, y1 + .02)),
                 ((0.90, y0 - .02), (1.50, 27.02)), ((2.06, y0 - .02), (x1 + .02, 26.88))):     # top panels round the two saws
        mb.box((*a, zt), (*b, top), mdf, bev=0.003)
    mb.box((0.90, 27.02, top - 0.126), (1.50, y1 + .02, top - 0.09), mdf)                     # sunk well under the mitre saw
    ctx.add(mb.finish('shed.island'), room, 'fit', plan_sym='workbench')

    mb = mo.MB()                                                                               # generic saws
    dark, alu, yel = C('#3A3D40', 0.5), C('#B8BBBD', 0.35, 0.7), C('#E0B32A', 0.45)
    zw = top - 0.09                                                                            # mitre saw in the well,
    zh = zw + 0.42                                                                             # head raised: top 0.42 above
    mb.box((0.95, 27.08, zw), (1.45, 27.44, zw + 0.07), C('#8E9296', 0.4, 0.6), bev=0.004)     # the island (v2:f_0291)
    cyl(mb, (1.20, 27.24, zw + 0.07), 0.13, 0.022, dark, segs=20)
    mb.box((0.95, 27.35, zw + 0.07), (1.45, 27.37, zw + 0.15), alu)                            # fence
    mb.box((1.15, 27.37, zw + 0.07), (1.25, 27.46, zh + 0.05), dark, bev=0.006)                # pivot post
    for x in (1.17, 1.23):                                                                     # slide rails
        cyl(mb, (x, 27.10, zh + 0.03), 0.011, 0.36, alu, 'y', 8)
    mb.box((1.155, 27.16, zh - 0.01), (1.245, 27.30, zh + 0.07), yel, bev=0.006)              # head housing on the rails
    cyl(mb, (1.193, 27.22, zh - 0.12), 0.125, 0.004, C('#A9ADB0', 0.3, 0.9), 'x', 20)          # blade
    mb.at(Matrix.Translation((1.165, 27.22, zh - 0.12)) @ Matrix.Rotation(math.pi / 2, 4, 'Y'))
    mb.lathe([(0, 0), (.137, 0), (.137, .06), (0, .06)], yel, 12, a0=math.pi / 2, a1=3 * math.pi / 2)   # upper guard
    mb.at()
    mb.box((1.165, 27.083, zh - 0.121), (1.225, 27.357, zh - 0.119), yel)
    cyl(mb, (1.225, 27.22, zh - 0.10), 0.055, 0.13, dark, 'x', 12)                             # motor, yellow end cap
    cyl(mb, (1.355, 27.22, zh - 0.10), 0.057, 0.025, yel, 'x', 12)
    mb.box((1.17, 27.04, zh + 0.03), (1.23, 27.16, zh + 0.09), dark, bev=0.006)                # handle
    mb.box((1.185, 27.12, zh - 0.02), (1.215, 27.16, zh + 0.05), dark)
    zs = ZF + 0.198                                                                            # table saw on the low shelf
    mb.box((2.14, 26.94, zs), (2.71, 27.41, top - 0.027), dark, bev=0.004)
    mb.box((2.10, 26.90, top - 0.027), (2.75, 27.45, top + 0.002), alu, bev=0.003)
    mb.box((2.25, 27.14, top + 0.002), (2.60, 27.20, top + 0.003), C('#A03028', 0.5))          # throat plate
    mb.box((2.10, 27.35, top + 0.002), (2.75, 27.41, top + 0.06), C('#E6E6E2', 0.4))           # rip fence
    cyl(mb, (2.42, 26.925, zs + 0.17), 0.05, 0.02, 'black_matt', 'y', 12)                      # height wheel
    ctx.add(mb.finish('shed.island.saws'), room, 'furn')

    mb, rnd = mo.MB(), random.Random(5)                                                        # a few plain offcuts on the shelf
    z = ZF + 0.198
    for i, (x, y, l, w, deg) in enumerate(((0.55, 26.55, 0.9, 0.14, 4), (0.75, 26.80, 1.2, 0.09, -3), (0.60, 27.05, 0.7, 0.19, 8),
                                           (1.05, 27.25, 1.0, 0.07, -5), (0.9, 26.62, 0.6, 0.12, 14), (1.35, 26.95, 0.5, 0.2, -9))):
        mb.at(Matrix.Translation((x, y, z + 0.02 * (i // 4))) @ Matrix.Rotation(math.radians(deg), 4, 'Z'))
        mb.box((0, -w / 2, 0), (l, w / 2, 0.02), PINE if rnd.random() < 0.6 else mdf)
    mb.at()
    ctx.add(mb.finish('shed.island.offcuts'), room, 'decor')


# ------------------------------------------------------------------ back-wall bench: pillar drill, boxed machine, extractor
def back_bench(ctx, room):
    x0, x1, y0, y1 = 0.73, 3.50, 28.02, 28.60                # ends short of the east bench (v2:f_0281)
    mb = mo.MB()
    top = bench(mb, x0, x1, y0, y1, 0.92, top=PINE, braces=True) + 0.036
    ctx.add(mb.finish('shed.bench_back'), room, 'fit', plan_sym='workbench')

    mb = mo.MB()
    blue, dark, steel = C('#56677A', 0.45), C('#2E3033', 0.5), C('#A9ADB0', 0.3, 0.9)
    x, y = 0.98, 28.30                                                                         # pillar drill, west end
    mb.box((x - 0.11, y - 0.14, top), (x + 0.11, y + 0.18, top + 0.03), blue, bev=0.004)
    cyl(mb, (x, y + 0.11, top + 0.03), 0.022, 0.50, steel)
    cyl(mb, (x, y - 0.02, top + 0.20), 0.085, 0.015, dark, segs=16)                            # table
    mb.box((x - 0.02, y - 0.02, top + 0.185), (x + 0.02, y + 0.13, top + 0.215), dark)
    mb.box((x - 0.07, y - 0.10, top + 0.47), (x + 0.07, y + 0.17, top + 0.62), blue, bev=0.006)   # head
    cyl(mb, (x, y + 0.17, top + 0.44), 0.055, 0.16, C('#8E9296', 0.4, 0.6))                    # motor
    cyl(mb, (x, y - 0.03, top + 0.39), 0.018, 0.08, dark)                                      # chuck
    for a in (0.4, 2.5, 4.6):                                                                  # feed handle spokes
        mb.tube([(x + 0.075, y + 0.02, top + 0.52), (x + 0.085, y + 0.02 + 0.1 * math.cos(a), top + 0.52 + 0.1 * math.sin(a))],
                0.005, steel, n=5)
    x, y = 3.12, 28.32                                                                         # pale-wood boxed machine, east end
    mb.box((x - 0.17, y - 0.17, top), (x + 0.17, y + 0.17, top + 0.03), dark)
    mb.box((x - 0.15, y - 0.15, top + 0.03), (x + 0.15, y + 0.15, top + 0.33), C('#DCC79C', 0.7), bev=0.004)
    mb.box((x - 0.10, y - 0.153, top + 0.20), (x + 0.10, y - 0.15, top + 0.29), C('#B79F78', 0.8))
    cyl(mb, (x, y, top + 0.33), 0.012, 0.035, dark, segs=8)
    cyl(mb, (x, y, top + 0.365), 0.035, 0.012, dark, segs=10)
    x, y = 2.70, 28.31                                                                         # dust extractor drum under the bench
    cyl(mb, (x, y, ZF), 0.175, 0.50, C('#4F6078', 0.5), segs=20)
    cyl(mb, (x, y, ZF + 0.50), 0.18, 0.03, dark, segs=20)
    cyl(mb, (x, y - 0.06, ZF + 0.53), 0.03, 0.04, dark, segs=8)
    ctx.add(mb.finish('shed.bench_back.machines'), room, 'furn')


# ------------------------------------------------------------------ east-wall bench on castors: desktop CNC
def east_bench(ctx, room):
    x0, x1, y0, y1 = 3.58, 4.16, 26.55, 28.60                # shortened at its south end: the doorway stays clear
    mb = mo.MB()
    top = bench(mb, x0, x1, y0, y1, 0.90, top=PINE, shelf=0.25, castors=True) + 0.036
    ctx.add(mb.finish('shed.bench_east'), room, 'fit', plan_sym='workbench')

    mb, blk, sil = mo.MB(), C('#1C1D1F', 0.45), C('#B4B8BB', 0.3, 0.9)
    mb.box((3.63, 27.72, top), (4.13, 28.32, top + 0.04), blk, bev=0.004)                      # bed
    for x in (3.64, 4.08):
        mb.box((x, 28.02, top + 0.04), (x + 0.04, 28.09, top + 0.34), blk)                     # gantry uprights
    mb.box((3.64, 28.03, top + 0.27), (4.12, 28.08, top + 0.35), blk)
    mb.box((3.83, 27.97, top + 0.20), (3.93, 28.03, top + 0.40), blk)                          # carriage
    cyl(mb, (3.88, 27.94, top + 0.12), 0.032, 0.26, sil)                                       # spindle
    cyl(mb, (3.88, 27.94, top + 0.07), 0.006, 0.05, sil, segs=6)
    mb.tube([(3.88, 27.99, top + 0.40), (3.86, 28.12, top + 0.46), (3.80, 28.26, top + 0.36), (3.78, 28.30, top + 0.06)],
            0.012, blk, n=6)                                                                   # one cable chain
    mb.box((3.68, 27.26, top), (4.03, 27.56, top + 0.045), C('#B5524E', 0.5), bev=0.006)       # red tray
    mb.box((3.70, 27.28, top + 0.045), (4.01, 27.54, top + 0.046), C('#8E3F3C', 0.6))
    ctx.add(mb.finish('shed.cnc'), room, 'furn')


# ------------------------------------------------------------------ boltless steel racking, NW corner
def racking(ctx, room):
    x0, x1, y0, y1, H = -0.52, 0.38, 28.15, 28.60, 1.80
    mb, blk, chip = mo.MB(), C('#1E1F21', 0.45, 0.6), C('#B79F78', 0.9)
    levels = [ZF + z for z in (0.08, 0.50, 0.92, 1.34, 1.76)]
    for x in (x0, x1 - 0.035):
        for y in (y0, y1 - 0.035):
            mb.box((x, y, ZF), (x + 0.035, y + 0.035, ZF + H), blk)
    for z in levels:
        for y in (y0, y1 - 0.012):
            mb.box((x0 + 0.035, y, z - 0.05), (x1 - 0.035, y + 0.012, z), blk)
        mb.box((x0 + 0.02, y0 + 0.012, z - 0.016), (x1 - 0.02, y1 - 0.012, z), chip)
    ctx.add(mb.finish('shed.racking'), room, 'fit', plan_sym='rack')

    mb, rnd = mo.MB(), random.Random(3)                       # generic contents: cases, boxes, bottles; toolbox + reel on top
    card = C('#B08D5F', 0.9)
    mb.box((-0.46, 28.20, levels[0]), (-0.06, 28.52, levels[0] + 0.12), C('#2B3A55', 0.5), bev=0.006)
    mb.box((-0.02, 28.22, levels[0]), (0.32, 28.50, levels[0] + 0.15), C('#232426', 0.5), bev=0.006)
    mb.box((-0.45, 28.22, levels[1]), (-0.10, 28.52, levels[1] + 0.24), card)
    mb.box((-0.04, 28.24, levels[1]), (0.30, 28.50, levels[1] + 0.18), card)
    mb.box((0.02, 28.24, levels[3]), (0.32, 28.52, levels[3] + 0.20), card)
    cols = ('#E8E6DF', '#C9CCD0', '#A8762E', '#3F5F8A', '#6C7A4A', '#D9D2B8')
    for z, xs in ((levels[2], [-0.44 + 0.09 * i for i in range(9)]), (levels[3], [-0.44 + 0.1 * i for i in range(4)])):
        for x in xs:
            r, h, col = rnd.uniform(0.028, 0.04), rnd.uniform(0.14, 0.25), C(rnd.choice(cols), 0.4)
            y = rnd.uniform(28.26, 28.36)
            cyl(mb, (x, y, z), r, h, col, segs=8)
            cyl(mb, (x, y, z + h), r * 0.45, 0.03, C('#2A2A2C', 0.5), segs=6)
    red = C('#8E3F30', 0.5, 0.3)                                                               # rust-red steel toolbox
    mb.box((-0.46, 28.24, levels[4]), (-0.04, 28.46, levels[4] + 0.17), red, bev=0.006)
    mb.box((-0.46, 28.30, levels[4] + 0.17), (-0.04, 28.40, levels[4] + 0.20), red, bev=0.006)
    mb.tube([(-0.33, 28.35, levels[4] + 0.20), (-0.33, 28.35, levels[4] + 0.235), (-0.17, 28.35, levels[4] + 0.235),
             (-0.17, 28.35, levels[4] + 0.20)], 0.006, C('#2A2A2C', 0.5), n=5)
    yel = C('#E0B32A', 0.45)                                                                   # yellow cable reel
    for y in (28.29, 28.375):
        cyl(mb, (0.18, y, levels[4] + 0.14), 0.13, 0.015, yel, 'y', 16)
    cyl(mb, (0.18, 28.305, levels[4] + 0.14), 0.085, 0.07, C('#232426', 0.6), 'y', 12)
    mb.box((0.06, 28.28, levels[4]), (0.30, 28.40, levels[4] + 0.015), C('#232426', 0.6))
    ctx.add(mb.finish('shed.racking.items'), room, 'decor')


# ------------------------------------------------------------------ wall-hung: clamps, disc rack
def wall_things(ctx, room):
    mb = mo.MB()                                              # four red bar clamps on a board, back wall
    red, steel = C('#B0302A', 0.45), C('#A9ADB0', 0.3, 0.9)
    zb = ZF + 1.90
    mb.box((0.46, Y1 - 0.03, zb - 0.06), (0.75, Y1, zb), PINE)
    for i in range(4):
        x, drop = 0.50 + 0.07 * i, (0.62, 0.50, 0.62, 0.50)[i]
        mb.box((x - 0.003, Y1 - 0.055, zb - drop), (x + 0.003, Y1 - 0.035, zb + 0.05), steel)
        mb.box((x - 0.011, Y1 - 0.12, zb), (x + 0.011, Y1 - 0.005, zb + 0.05), red)            # fixed jaw hooked over the board
        zj = zb - drop + 0.12
        mb.box((x - 0.011, Y1 - 0.12, zj), (x + 0.011, Y1 - 0.03, zj + 0.05), red)
        cyl(mb, (x, Y1 - 0.09, zj - 0.10), 0.013, 0.10, 'black_matt', segs=8)
    ctx.add(mb.finish('shed.clamps'), room, 'decor')

    mb = mo.MB()                                              # timber rack of round brown discs, west wall
    brown = C('#6B4A35', 0.8)
    mb.box((X0, 26.70, ZF + 1.50), (X0 + 0.02, 27.30, ZF + 1.75), PINE)
    for z in (ZF + 1.565, ZF + 1.685):
        for i in range(5):
            cyl(mb, (X0 + 0.02, 26.78 + 0.11 * i, z), 0.048, 0.05, brown, 'x', 12)
    ctx.add(mb.finish('shed.wall_rack'), room, 'decor')


# ------------------------------------------------------------------ coving and skirting (site leaves them to this module)
def trim(ctx, room):
    white = M.paint('#EFEEEA')
    cove = mo.sweep('cove_70', [(X0, Y0, ZC), (X1, Y0, ZC), (X1, Y1, ZC), (X0, Y1, ZC)], closed=True, name='shed.cove',
                    material=white)
    ctx.add(cove, room, 'trim')
    sk = mo.sweep([(0.015, 0.0), (0.015, 0.07), (0.0, 0.07)],                                  # 70 mm square-edge, stops at the doors
                  [(3.95, Y0, ZF), (X1, Y0, ZF), (X1, Y1, ZF), (X0, Y1, ZF), (X0, Y0, ZF), (2.75, Y0, ZF)], name='shed.skirting')
    ctx.add(sk, room, 'trim')


def build(ctx, room):
    island(ctx, room)
    back_bench(ctx, room)
    east_bench(ctx, room)
    racking(ctx, room)
    wall_things(ctx, room)
    trim(ctx, room)

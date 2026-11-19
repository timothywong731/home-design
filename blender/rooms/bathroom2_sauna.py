"""bathroom2 sauna: free-standing one-person spruce cabin (spec/rooms/bathroom2.md 5.2), called by rooms/bathroom2.py.

World box x 1.68..3.01, y 12.82..13.70, 2.02 high (window-wall chain of the reconciled spec: 0.09 clear of the window wall,
front level with the north window jamb, back on the north wall). Front: boarded panel, tinted glass door x 2.28..2.88
hinged on its east edge (opens out 100 deg), post. Inside: heater with rocks and control unit on the W wall, slatted
corner seat with backrest, bucket + ladle, sand timer, gauge, vent hatch, louvre, one recessed light.
"""
import json
import random

from lib import bath, interact as IX, lighting, materials as M, mouldings as mo, props as P

ROOM = 'bathroom2'
FZ = 6.02
SX0, SX1, SY0, SY1, H = 1.68, 3.01, 12.82, 13.70, 2.02
T = .05                                    # wall: posts / boards outside, boards inside
IX0, IX1, IY0, IY1, IH = SX0 + T, SX1 - T, SY0 + T, SY1 - T, 1.93     # clear inside 1.23 x 0.78 x 1.93
DX0, DX1 = 2.28, 2.88                      # door (glass) span
# untreated spruce: constant tones per board (the library's palest grained timber, oak_light, renders orange-brown here,
# far from the blond boards of v5 f_0047 / f_0075); outside #D8BE8C (spec 4). Inside, the near-closed timber box
# multiplies the albedo's saturation through inter-reflection, so the lining is much greyer to render the pale ash
# of v5 f_0055 / f_0061 (#C3B997); TI = interior furniture, a touch warmer than the lining.
OUT = ('#D9C49B', '#D3BC90', '#DDCAA4', '#D6BF94')
INS = ('#D8D0BC', '#D2C9B4', '#DCD5C2', '#D5CDB8')
TI_HEX = '#D9CEB2'


def tw(hx=OUT[0]):
    return M.solid('bathroom2_spruce_' + hx[1:], hx, .7)


TW = TI = None                             # replaced by tw() at build time (materials need bpy)


def z(h):
    return FZ + h


def boards(mb, lo, hi, n, axis, grain=2, bev=.0025, tones=OUT):
    """n tongue-and-groove boards side by side along `axis` (chamfered edges read as the V joints), board tones varied."""
    a, b = lo[axis], hi[axis]
    for i in range(n):
        p, q = list(lo), list(hi)
        p[axis], q[axis] = a + (b - a) * i / n, a + (b - a) * (i + 1) / n
        k = int(abs(p[0] * 31 + p[1] * 17 + p[2] * 7) * 100 + i * 3) % len(tones)
        mb.box(tuple(p), tuple(q), tw(tones[k]), bev=bev, grain=grain)


def build(ctx):
    global TW, TI
    TW, TI = tw(), tw(TI_HEX)
    add = lambda ob, kind='fit', **kw: ctx.add(ob, ROOM, kind, **kw)
    zt = z(H - .04)                                                      # under the capping

    # ---------------------------------------------------------------- cabin carcass (one mesh)
    mb = mo.MB()
    for x0, y0 in ((SX0, SY0), (SX1 - .06, SY0), (SX0, SY1 - .06), (SX1 - .06, SY1 - .06)):   # corner posts
        mb.box((x0, y0, FZ), (x0 + .06, y0 + .06, zt), TW, bev=.003, grain=2)
    o = .005                                                             # boards sit 5 mm behind the post faces
    boards(mb, (SX0 + .06, SY0 + o, FZ), (DX0, SY0 + o + .018, zt), 6, 0)                 # front panel
    boards(mb, (DX1, SY0 + o, FZ), (SX1 - .06, SY0 + o + .018, zt), 1, 0)                 # post beside the door
    boards(mb, (SX0 + o, SY0 + .06, FZ), (SX0 + o + .018, SY1 - .06, zt), 8, 1)           # west side
    boards(mb, (SX1 - o - .018, SY0 + .06, FZ), (SX1 - o, SY1 - .06, zt), 8, 1)           # east side (the 90 mm gap)
    for a, b in (((SX0 + .06, SY0 - .012, FZ), (DX0, SY0 + .01, z(.06))),                 # plinth batten
                 ((DX1, SY0 - .012, FZ), (SX1 - .06, SY0 + .01, z(.06))),
                 ((SX0 - .012, SY0 + .06, FZ), (SX0 + .01, SY1 - .06, z(.06))),
                 ((SX1 - .01, SY0 + .06, FZ), (SX1 + .012, SY1 - .06, z(.06)))):
        mb.box(a, b, TW, bev=.003, grain=0)
    cap = .02                                                            # square capping oversailing 20 mm
    for a, b, g in (((SX0 - cap, SY0 - cap, zt), (SX1 + cap, SY0 + .07, z(H)), 0),
                    ((SX0 - cap, SY1 - .07, zt), (SX1 + cap, SY1, z(H)), 0),
                    ((SX0 - cap, SY0 + .07, zt), (SX0 + .07, SY1 - .07, z(H)), 1),
                    ((SX1 - .07, SY0 + .07, zt), (SX1 + cap, SY1 - .07, z(H)), 1)):
        mb.box(a, b, TW, bev=.004, grain=g)
    mb.box((SX0 + .07, SY0 + .07, zt), (SX1 - .07, SY1 - .07, z(H - .01)), TW, grain=1)   # roof board
    for a, b in (((DX0, SY0, FZ), (DX0 + .04, IY0 + .018, z(1.98))),                      # door frame: jambs, head
                 ((DX1 - .04, SY0, FZ), (DX1, IY0 + .018, z(1.98))),
                 ((DX0 + .04, SY0, z(1.90)), (DX1 - .04, IY0 + .018, z(1.98)))):
        mb.box(a, b, TW, bev=.003, grain=2)
    # inside lining (boards to the floor; the room tiles are the floor) and the ceiling boards along y
    t = .018
    boards(mb, (IX0, IY0, FZ), (IX0 + t, IY1, z(IH)), 9, 1, tones=INS)
    boards(mb, (IX1 - t, IY0, FZ), (IX1, IY1, z(IH)), 9, 1, tones=INS)
    boards(mb, (IX0 + t, IY1 - t, FZ), (IX1 - t, IY1, z(IH)), 13, 0, tones=INS)
    boards(mb, (IX0 + t, IY0, FZ), (DX0, IY0 + t, z(IH)), 6, 0, tones=INS)
    boards(mb, (DX1, IY0, FZ), (IX1 - t, IY0 + t, z(IH)), 1, 0, tones=INS)
    boards(mb, (IX0, IY0, z(IH - t)), (IX1, IY1, z(IH)), 13, 0, grain=1, tones=INS)
    r = .022                                                             # quarter-round fillets at the ceiling
    for a, b in (((IX0 + t, IY0 + t, z(IH - t - r)), (IX0 + t + r, IY1 - t, z(IH - t))),
                 ((IX1 - t - r, IY0 + t, z(IH - t - r)), (IX1 - t, IY1 - t, z(IH - t))),
                 ((IX0 + t, IY1 - t - r, z(IH - t - r)), (IX1 - t, IY1 - t, z(IH - t))),
                 ((IX0 + t, IY0 + t, z(IH - t - r)), (IX1 - t, IY0 + t + r, z(IH - t)))):
        mb.box(a, b, TI, bev=.009, grain=0)
    add(mb.finish(f'{ROOM}.sauna'), plan_sym='sauna')
    xi0, xi1, yi0, yi1 = IX0 + t, IX1 - t, IY0 + t, IY1 - t             # clear inside faces

    # ---------------------------------------------------------------- tinted glass door, east hinges, opens out 100 deg
    door = bath.glass_door(f'{ROOM}.sauna.door', ((DX0 + DX1) / 2, SY0 - .012, z(.08)), DX1 - DX0, 1.84, (0, -1),
                           hinge='right', deg=100, mat='glass_dark', handle_z=.97, label='Sauna door')
    bath.add(ctx, ROOM, door)
    mb = mo.MB()                                                         # turned timber pull inside
    xh = DX0 + .08
    for zz in (.94, 1.16):
        mb.tube([(xh, SY0 - .008, z(zz)), (xh, SY0 + .028, z(zz))], .006, 'steel_brushed', n=8)
    mb.tube([(xh, SY0 + .028, z(.90)), (xh, SY0 + .028, z(1.20))], .012, TI, n=12)
    pull = mb.finish(f'{ROOM}.sauna.door.pull')
    d = json.loads(door[0]['ix'])
    IX.tag(pull, **d)
    add(pull, lm='dynamic')

    # ---------------------------------------------------------------- heater (W wall, centred y 13.26)
    yc, hw = 13.26, .20
    mb = mo.MB()                                                         # black body z 0.32..0.75, open rock tray on top
    mb.box((xi0 + .002, yc - hw, z(.32)), (xi0 + .262, yc + hw, z(.72)), 'black_matt', bev=.02)
    for a, b in (((xi0 + .002, yc - hw, z(.72)), (xi0 + .262, yc - hw + .014, z(.75))),
                 ((xi0 + .002, yc + hw - .014, z(.72)), (xi0 + .262, yc + hw, z(.75))),
                 ((xi0 + .002, yc - hw, z(.72)), (xi0 + .016, yc + hw, z(.75))),
                 ((xi0 + .248, yc - hw, z(.72)), (xi0 + .262, yc + hw, z(.75)))):
        mb.box(a, b, 'black_matt', bev=.003)
    gx = xi0 + .32                                                       # timber guard rails round front and sides
    for zr in (.42, .64):
        mb.box((gx, yc - hw - .06, z(zr)), (gx + .02, yc + hw + .06, z(zr + .06)), TI, bev=.003, grain=1)
        for s in (-1, 1):
            y0 = yc + s * (hw + .05)
            mb.box((xi0, min(y0, y0 + s * .02), z(zr)), (gx, max(y0, y0 + s * .02), z(zr + .06)), TI, bev=.003, grain=0)
    add(mb.finish(f'{ROOM}.sauna.heater'))
    add(P.place(_b2_rocks(seed=3, name=f'{ROOM}.sauna.rocks'), (xi0 + .132, yc, z(.70))), 'decor')
    # control unit z 0.20..0.32: brushed stainless housing, white fascia with display, buttons, rocker, blank label
    mb = mo.MB()
    fx = xi0 + .252
    mb.box((xi0 + .002, yc - hw, z(.20)), (fx, yc + hw, z(.32)), 'steel_brushed', bev=.004)
    mb.box((fx, yc - .10, z(.215)), (fx + .002, yc + .02, z(.305)), 'plastic_white')
    for k in range(4):
        y = yc - .085 + k * .03
        mb.tube([(fx + .002, y, z(.235)), (fx + .006, y, z(.235))], .0055, P.mat('plastic_dark') if k else M.solid('bathroom2_btn', '#3A6FC4', .4), n=10)
    mb.box((fx + .002, yc - .057, z(.272)), (fx + .003, yc - .023, z(.296)), 'black_gloss')
    mb.box((fx, yc - .185, z(.24)), (fx + .012, yc - .165, z(.285)), 'black_matt', bev=.002)       # rocker
    mb.box((fx, yc + .065, z(.225)), (fx + .0015, yc + .175, z(.305)), M.solid('bathroom2_label', '#E6E4DC', .6))
    ctrl = add(mb.finish(f'{ROOM}.sauna.control'), lm='dynamic')
    mb = mo.MB()
    mb.box((fx + .0031, yc - .054, z(.275)), (fx + .0036, yc - .026, z(.293)), P.emissive('#FF3A1E', 3.0))
    disp = add(mb.finish(f'{ROOM}.sauna.display'), 'light', lm='dynamic')

    # ---------------------------------------------------------------- the one light, near the NW corner
    lx, ly = xi0 + .22, yi1 - .25
    lighting.downlight(ctx, ROOM, lx, ly, z=z(IH - t) - .02, watts=22, kelvin=3000, spot_deg=140, name=f'{ROOM}.sauna.lamp')
    lamp = add(P.place(P.downlight(.07, .04, trim='chrome', name=f'{ROOM}.sauna.light'), (lx, ly, z(IH - t))), 'light',
               lm='dynamic')
    IX.tag_many([ctrl, disp, lamp], 'lamp', g=f'{ROOM}.sauna', label='Sauna')

    # ---------------------------------------------------------------- slatted corner seat, backrest, back rail
    mb = mo.MB()
    sx0, sy0 = 2.35, 13.15
    for k in range(6):                                                   # slats run front to back
        x = sx0 + .01 + k * (.07 + (xi1 - sx0 - .01 - .42) / 5)
        mb.box((x, sy0, z(.43)), (x + .07, yi1, z(.45)), TI, bev=.004, grain=1)
    for x in (sx0 + .01, xi1 - .02):                                     # aprons, front leg, front rail
        mb.box((x, sy0 + .01, z(.33)), (x + .02, yi1, z(.43)), TI, bev=.003, grain=1)
    mb.box((sx0 + .01, sy0 + .01, FZ), (sx0 + .03, sy0 + .09, z(.43)), TI, bev=.003, grain=2)
    mb.box((sx0 + .03, sy0 + .01, z(.37)), (xi1, sy0 + .03, z(.43)), TI, bev=.003, grain=0)
    for zz in (.85, .96, 1.07):                                          # backrest on the east wall
        mb.box((xi1 - .04, 13.22, z(zz)), (xi1 - .02, yi1 - .02, z(zz + .07)), TI, bev=.004, grain=1)
    for y in (13.28, 13.56):
        mb.box((xi1 - .02, y, z(.82)), (xi1, y + .04, z(1.17)), TI, bev=.003, grain=2)
    mb.box((xi0, yi1 - .02, z(.91)), (xi1, yi1, z(.99)), TI, bev=.003, grain=0)     # flat rail on the north wall
    add(mb.finish(f'{ROOM}.sauna.seat'))

    # bucket (staved pail, white liner) and long-handled ladle on the seat
    bx, by = 2.66, 13.42
    add(P.place(P.lathe([(0, 0), (.088, 0), (.11, .19), (.10, .19), (.081, .014), (0, .014)], 16, TI,
                        name=f'{ROOM}.sauna.bucket'), (bx, by, z(.45))), 'decor')
    add(P.place(P.lathe([(0, .015), (.08, .015), (.097, .175), (.093, .175), (.077, .018), (0, .018)], 20, 'plastic_white',
                        name=f'{ROOM}.sauna.bucket.liner'), (bx, by, z(.45))), 'decor')
    add(P.place(P.lathe([(.1, 0), (.106, 0), (.108, .02), (.102, .02)], 16, TI, name=f'{ROOM}.sauna.bucket.hoop'),
                (bx, by, z(.59))), 'decor')
    ladle = P.place(_b2_ladle(name=f'{ROOM}.sauna.ladle'), (bx - .02, by - .01, z(.56)), rot_z=150)
    add(ladle, 'decor')

    # sand timer on the inside of the front panel (flips), gauge high on the east wall, vents
    st = P.place(_b2_timer(name=f'{ROOM}.sauna.timer'), (2.05, yi0, z(1.45)), facing=(0, 1))
    IX.tag(st, 'hinge', label='Sand timer', p=(2.05, yi0 + .02, z(1.45)), a=(0, 1, 0), deg=180)
    add(st, 'decor', lm='dynamic')
    add(P.place(_b2_gauge(name=f'{ROOM}.sauna.gauge'), (xi1, 12.97, z(1.75)), facing=(-1, 0)), 'decor')
    add(P.place(P.box(.07, .012, .06, 'plastic_white', name=f'{ROOM}.sauna.louvre'), (xi1, 13.52, z(1.77)),
                facing=(-1, 0)), 'fit')
    mb = mo.MB()                                                         # vent slot + guides on the north wall
    vx = 2.15
    mb.box((vx - .10, yi1 - .001, z(1.715)), (vx + .10, yi1, z(1.785)), 'black_matt')
    for zz in (1.685, 1.80):
        mb.box((vx - .14, yi1 - .016, z(zz)), (vx + .26, yi1, z(zz + .015)), TI, bev=.002, grain=0)
    add(mb.finish(f'{ROOM}.sauna.vent'))
    mb = mo.MB()
    mb.box((vx - .125, yi1 - .014, z(1.70)), (vx + .125, yi1 - .002, z(1.80)), TI, bev=.002, grain=0)
    mb.tube([(vx + .09, yi1 - .014, z(1.75)), (vx + .09, yi1 - .03, z(1.75))], .007, TI, n=8)
    hatch = mb.finish(f'{ROOM}.sauna.vent.hatch')
    IX.tag(hatch, 'slide', label='Sauna vent', d=(.10, 0, 0))
    add(hatch, lm='dynamic')

    # grey mat on the tiles inside; white isolator on the wall above the cabin (v5 f_0104)
    add(P.place(P.rug(None, xi1 - xi0 - .02, yi1 - yi0 - .02, thickness=.006, color='#8E9092', name=f'{ROOM}.sauna.mat'),
                ((xi0 + xi1) / 2, (yi0 + yi1) / 2, FZ)), 'decor')
    iso = P.place(P.switch_plate(1, 'rocker', name=f'{ROOM}.sauna.isolator'), (2.60, SY1 - .035, z(2.18)), facing=(0, -1))
    add(iso, 'fit')
    add(P.place(P.box(.086, .035, .086, 'plastic_white', name=f'{ROOM}.sauna.isolator.box'), (2.60, SY1 - .0175, z(2.137)),
                facing=(0, -1)), 'fit')


# ----------------------------------------------------------------------------- parts
@P._prop
def _b2_rocks(b, seed=3):
    """Packed heap of dark grey olivine stones for the open heater tray (origin 20 mm under the body top, which is
    the tray floor): a full bottom layer and a smaller top layer crowning ~35 mm above the rim (v5 f_0053, f_0057)."""
    rnd = random.Random(seed)
    stone = M.solid('bathroom2_olivine', '#646761', .85)
    for i in range(100):                                                 # 40 on a jittered 5 x 8 grid (covers the
        top = i >= 70                                                    # tray floor), 30 loose, 30 on top
        if i < 40:
            x, y = -.09 + .045 * (i % 5) + rnd.uniform(-.012, .012), -.16 + .0457 * (i // 5) + rnd.uniform(-.012, .012)
        else:
            x, y = rnd.uniform(-.075, .075) if top else rnd.uniform(-.10, .10), rnd.uniform(-.15, .15) if top else rnd.uniform(-.172, .172)
        r = rnd.uniform(.020, .034)
        g = P._sphere(r, 6, 4, squash=rnd.uniform(.5, .8))
        zc = (.055 + rnd.uniform(0, .015)) if top else (.03 + r * .3 + rnd.uniform(0, .01))
        b.add(g, stone, False, closed=True,
              T=P.Tr(x, y, zc) @ P.Rot('Z', rnd.uniform(0, 360)) @ P.Rot('X', rnd.uniform(-40, 40))
              @ P.Rot('Y', rnd.uniform(-30, 30)) @ P.Sc(rnd.uniform(.75, 1.3), rnd.uniform(.7, 1.2), rnd.uniform(.8, 1.1)))


@P._prop
def _b2_ladle(b):
    """Long-handled wooden sauna ladle: cup at the origin opening up, handle rising along +X."""
    b.add(P._lathe([(0, -.03), (.03, -.028), (.042, -.012), (.045, 0), (.04, 0), (.036, -.01), (.026, -.022),
                    (0, -.024)], 16), TI, True)
    b.add(P._tube([(.04, 0, -.005), (.20, 0, .05), (.40, 0, .11)], [.009, .008, .009], 8), TI, True, closed=True)


@P._prop
def _b2_timer(b):
    """15-minute sand timer: backboard, two posts, glass hourglass with blue sand (wall prop, front -Y, origin centre)."""
    b.add(P._box((-.032, -.012, -.135), (.032, 0, .135), .003), TI, closed=True)
    for sx in (-1, 1):
        b.add(P._box((sx * .024 - .006, -.032, -.12), (sx * .024 + .006, -.012, .12), .002), TI, closed=True)
    for zc in (-.115, .115):
        b.add(P._box((-.03, -.034, zc - .006), (.03, -.012, zc + .006), .002), TI, closed=True)
    prof = [(0, -.109), (.011, -.106), (.013, -.07), (.010, -.03), (.0025, -.004), (.0025, .004), (.010, .03),
            (.013, .07), (.011, .106), (0, .109)]
    b.add(P._lathe(prof, 12), 'glass_clear', True, T=P.Tr(0, -.022, 0))
    sand = M.solid('bathroom2_sand', '#2F64B5', .9)
    b.add(P._lathe([(0, -.106), (.0105, -.104), (.0122, -.07), (.0095, -.045), (0, -.045)], 12), sand, True,
          T=P.Tr(0, -.022, 0))


@P._prop
def _b2_gauge(b):
    """Round sauna thermometer, dial 0.12: silver bezel, white face, black needle (wall prop, front -Y)."""
    b.add(P._lathe([(0, 0), (.06, 0), (.06, .016), (.054, .02), (.05, .016), (0, .016)], 28), 'silver_satin', True,
          T=P.Rot('X', 90))
    b.add(P._lathe([(0, 0), (.05, 0), (.05, .0005), (0, .0005)], 28), M.solid('bathroom2_dial', '#F2F0EA', .5), True,
          T=P.Tr(0, -.0162, 0) @ P.Rot('X', 90))
    b.add(P._box((-.002, -.019, -.008), (.002, -.0175, .04)), 'black_matt', closed=True)

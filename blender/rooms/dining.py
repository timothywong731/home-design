"""Dining room furnishing ("the most important part"): draw-leaf oak table, 8 Chippendale chairs, carved
fireplace + mantel ornaments, TV, mounted sword, 36 crest plaques, carved panels, triptych mirror,
check curtains, plants, chandelier, wall lights, downlights. Spec: spec/rooms/dining.md.

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --only shell,dining --preview dining --res 540x960 --samples 64 --tag dining

Room (world): x -0.65..3.10, y 12.36..16.86, ceiling 2.80. Chimney breast face x = 2.92, centred
y = 14.61. Helpers: rooms/dining_furniture.py (shared mesh helpers, materials, table), dining_chairs.py,
dining_fire.py, dining_decor.py (panels, mirror, sword, plaques, curtains), dining_light.py, dining_plants.py.
"""
import math
import os

from lib import lighting, mouldings as mo, props as P
from rooms import (dining_chairs as C, dining_decor as D, dining_fire as F, dining_furniture as U, dining_light as L,
                   dining_plants as G)

ROOM = 'dining'
X0, X1, Y0, Y1 = -0.65, 3.10, 12.36, 16.86      # inside wall faces: W, E, S (hall), N (screen face)
BX, FY = 2.92, 14.61                            # chimney-breast face, fireplace centre line
TX, TY = 1.1375, 14.61                          # table centre (0.09 west of the ceiling rose)
GLOW_W = 60                                     # stand-in for the light through the chandelier's cloth shades
BULB_W = 3                                      # per candle lamp: pools on the rose through the shade tops (10 W burnt it out)

# fov_deg spans the longer (vertical) image side; ref = reference frame to compare with
CAMERAS = [
    dict(name='entry', pos=(-0.05, 12.66, 1.45), look=(2.5, 16.0, 1.3), fov_deg=100, ref='f_0574'),
    dict(name='east', pos=(0.25, 14.86, 1.45), look=(3.1, 14.61, 1.4), fov_deg=100, ref='f_0675'),
    dict(name='north', pos=(1.55, 12.76, 1.45), look=(1.3, 16.86, 1.4), fov_deg=100, ref='f_0705'),
    dict(name='table', pos=(0.02, 15.80, 1.50), look=(2.3, 13.3, 0.75), fov_deg=100, ref='f_0608'),
    dict(name='west', pos=(1.40, 13.16, 1.45), look=(-0.65, 14.9, 1.75), fov_deg=100, ref='f_0720'),
    dict(name='tv', pos=(2.04, 14.56, 1.45), look=(1.2, 12.36, 1.9), fov_deg=100, ref='f_0613'),
    dict(name='chand', pos=(1.94, 14.36, 1.30), look=(1.05, 14.72, 2.75), fov_deg=100, ref='f_0714'),
    dict(name='fire', pos=(1.93, 13.56, 1.45), look=(2.95, 14.55, 0.65), fov_deg=100, ref='f_0643'),
]

# crest plaques: generic heraldry (the real ones carry lettering). Muted enamels; a few light-blue / red ones.
_KINDS = ('bend', 'chief', 'party', 'bend', 'badge', 'chief', 'party')
_BOARDS = ('#6E4F31', '#3A2A20', '#3A2A20', '#6E4F31', '#3A2A20', '#6E4F31', '#6E4F31', '#3A2A20')    # mid-brown / near-black
_F1 = ('#1B2540', '#4A1A22', '#151515', '#1B2540', '#1F3326', '#4A1A22', '#232B4A', '#151515')
_F2 = ('#4A1A22', '#1B2540', '#151515', '#1B2540', '#C9C4B4', '#4A1A22', '#1F3326')
_SPECIAL = {9: '#6F93B5', 22: '#6F93B5', 5: '#8E1B1B', 27: '#8E1B1B'}


def _crest(n):
    """Deterministic variety for plaque n -> dict(kind, board, field, field2)."""
    f1 = _SPECIAL.get(n, _F1[(n * 5 + n // 3) % len(_F1)])
    f2 = _F2[(n * 3 + 1) % len(_F2)]
    return dict(kind=_KINDS[n % len(_KINDS)], board=_BOARDS[n % len(_BOARDS)], field=f1,
                field2='#C9C4B4' if f2 == f1 else f2)


def build(ctx):
    cz = ctx.ceil_z(ROOM)
    add = lambda ob, kind, **kw: ctx.add(ob, ROOM, kind, **kw)

    # ------------------------------------------------------------------ table + 8 chairs
    add(P.place(U.table(), (TX, TY, 0)), 'furn', plan_sym='table')
    seats = [  # (x, y, facing, armchair) - three per long side with the middle one a carver, one per end
        (TX, 13.05, (0, 1), False), (TX, 16.17, (0, -1), False),
        (TX - .63, 13.54, (1, 0), False), (TX - .68, TY, (1, 0), True), (TX - .63, 15.68, (1, 0), False),
        (TX + .63, 13.54, (-1, 0), False), (TX + .68, TY, (-1, 0), True), (TX + .63, 15.68, (-1, 0), False)]
    for i, (x, y, f, arm) in enumerate(seats):
        ch = C.chair(f'dining.chair.{i}', arm)
        add(P.place(ch, (x, y, 0), facing=f), 'furn', plan_sym='armchair' if arm else 'chair')

    # ------------------------------------------------------------------ fireplace (E wall, on the breast)
    east = lambda xl, out, z: (BX - out, FY - xl, z)      # fireplace-local (x across, depth out, z) -> world
    add(P.place(F.fireplace(), (BX, FY, 0), facing=(-1, 0)), 'fit', plan_sym='fireplace', lm='dynamic')
    clock = P.mantel_clock(name='dining.mantel_clock')
    face = F.clock_face()                                         # round bezel + Roman strokes over the prop's dial
    face.parent = clock
    face.location = (0, -.0605, .1628)
    add(P.place(clock, east(0, .115, 1.19), facing=(-1, 0)), 'decor')
    for i, s in enumerate((-1, 1)):
        add(P.place(F.candelabrum(f'dining.candelabrum.{i}'), east(s * .48, .125, 1.19), facing=(-1, 0)), 'decor')
        add(P.place(F.candlestick(f'dining.candlestick.{i}'), east(s * .68, .12, 1.19)), 'decor')
    # the original over the mantel is a wedding portrait: frame kept, picture replaced by a neutral, fully
    # synthetic landscape (reference/work/dining/make_landscape.py - no reference pixels)
    pic = P.framed_picture(os.path.join(U.ART, 'mantel_landscape.jpg'), .61, .85, 'gilt_swept', frame_w=.06, depth=.035,
                           mount=.105, slip=('#7A2A2A', .005), name='dining.mantel_picture')
    beads = D.frame_beads(.61, .85, .0504, -.0214)                # bead course on the frame's inner member
    beads.parent = pic
    add(P.place(pic, (BX, FY, 1.96), facing=(-1, 0)), 'decor')

    # ------------------------------------------------------------------ S wall: TV, switch, sword, plaques
    add(P.place(P.tv_panel(1.89, 1.08, name='dining.tv'), (1.805, Y0, 1.69), facing=(0, 1)), 'fit', plan_sym='tv')
    add(P.place(P.switch_plate(3, 'toggle', name='dining.switch'), (0.67, Y0, 1.37), facing=(0, 1)), 'fit')
    add(P.place(D.sword_board(), (1.64, Y0, 2.43), facing=(0, 1)), 'decor')
    n = 0
    for x in (-0.43, -0.15, 0.13, 0.41, 0.69):                    # five over the door
        kw = dict(kind='badge', board='#1F2A44') if x == -0.15 else _crest(n)   # dark blue, gilt arms, centred over the door
        add(P.place(D.plaque(f'dining.plaque.s.{n}', **kw), (x, Y0, 2.50), facing=(0, 1)), 'decor')
        n += 1
    for x in (2.33, 2.61, 2.89):                                  # three small ones east of the sword
        kw = _crest(n)
        kw['kind'] = ('bend', 'chief', 'party')[n % 3]
        add(P.place(D.plaque(f'dining.plaque.s.{n}', w=.11, h=.14, **kw), (x, Y0, 2.50), facing=(0, 1)), 'decor')
        n += 1

    # ------------------------------------------------------------------ W wall: two plaque rows, carvings, mirror
    for k in range(16):                                           # top row: 3 round ship's badges, 1 lozenge, 12 shields
        if k < 3:
            pl = D.plaque(f'dining.plaque.w.{k}', 'round', '#1B1A1A', ('#1B2540', '#4A1A22', '#151515')[k], w=.17, h=.17)
        elif k == 3:
            pl = D.plaque(f'dining.plaque.w.{k}', 'lozenge', '#E8E4D8', '#E8E4D8', '#6F93B5', w=.17, h=.21)
        else:
            pl = D.plaque(f'dining.plaque.w.{k}', **_crest(n))
        add(P.place(pl, (X0, Y0 + .20 + .265 * k, 2.50), facing=(1, 0)), 'decor')
        n += 1
    for j in range(12):                                           # lower row, staggered half a pitch
        add(P.place(D.plaque(f'dining.plaque.w.{16 + j}', **_crest(n)), (X0, Y0 + .865 + .265 * j, 2.27), facing=(1, 0)),
            'decor')
        n += 1
    panel = D.carved_panel()
    for i, y in enumerate((13.51, 15.72)):                        # the pair of grapevine carvings
        ob = panel if i == 0 else panel.copy()                    # linked duplicate (shares the mesh)
        ob.name = f'dining.carved_panel.{i}'
        add(P.place(ob, (X0, y, 1.70), facing=(1, 0)), 'decor')
    add(P.place(D.triptych_mirror(), (X0, 14.635, 1.685), facing=(1, 0)), 'decor', plan_sym='mirror')
    stop = P.lathe([(0, 0), (.016, 0), (.016, .004), (.006, .008), (.006, .05), (.011, .052), (.011, .062), (0, .062)],
                   12, 'brass', name='dining.door_stop')            # projecting door stop on the W skirting
    stop.rotation_euler = (0, math.pi / 2, 0)
    stop.location = (X0 + .02, 13.08, .09)
    add(stop, 'fit')

    # ------------------------------------------------------------------ sockets
    for i, (loc, f, g) in enumerate((((X1, 13.61, .25), (-1, 0), 2), ((X1, 15.61, .25), (-1, 0), 2),
                                     ((X0, 16.36, .45), (1, 0), 1))):
        add(P.place(P.socket(g, name=f'dining.socket.{i}'), loc, facing=f), 'fit')

    # ------------------------------------------------------------------ N wall: check curtains, tied round the middle
    for i, x in enumerate((0.3675, 2.0875)):
        add(P.place(D.curtain(f'dining.curtain.{i}'), (x, Y1 - .05, 2.50), facing=(0, -1)), 'decor')

    # ------------------------------------------------------------------ plants
    for i, y in enumerate((13.02, 16.20)):                        # monstera in each E-window reveal, leaning into the room
        # the north one leans south (local +X), away from the citrus head
        add(P.place(G.monstera(f'dining.monstera.{i}', seed=i, lean=.45 * i), (3.12, y, 1.10), facing=(-1, 0)), 'decor')
    add(P.place(G.citrus(), (2.60, 16.42, 0)), 'decor', plan_sym='plant')    # head 0.68: 50 mm clear of the curtain

    # ------------------------------------------------------------------ lighting: every fitting of the room
    rx, ry = mo.ROSE_AT[ROOM]
    chand = L.chandelier()
    add(P.place(chand, (rx, ry, cz - .035)), 'light')             # ceiling cup under the centre of the rose
    for i, p in enumerate(P.bulb_points(chand)):
        lighting.bulb(ctx, ROOM, p, watts=BULB_W, name=f'dining.chandelier.bulb.{i}')     # 25 mm sphere round the 11 mm lamp
    # The cloth shades are opaque geometry: their lamps only shine out of the top and bottom openings. One large
    # soft bulb just under the arms stands in for the light the real, translucent shades give to the walls (hidden
    # from the camera and from reflections). It sits below the ring of shades, which therefore screen the ceiling
    # rose from it - higher up it burnt the rose's relief out.
    glow = lighting.bulb(ctx, ROOM, (rx, ry, 2.10), watts=GLOW_W, kelvin=2900, radius=.20, name='dining.chandelier.glow')
    glow.visible_camera = glow.visible_glossy = False
    for i, y in enumerate((13.59, 15.63)):                        # twin-arm brass wall lights in the alcoves
        sc = L.sconce(f'dining.sconce.{i}')
        add(P.place(sc, (X1, y, 1.80), facing=(-1, 0)), 'light')
        for j, p in enumerate(P.bulb_points(sc)):
            lighting.bulb(ctx, ROOM, p, watts=14, name=f'dining.sconce.{i}.bulb.{j}')
    i = 0
    for x in (-0.0125, 1.2275, 2.4575):                           # 3 x 3 downlight grid, centre left to the rose
        for y in (13.01, 14.61, 16.21):
            if (x, y) == (1.2275, 14.61):
                continue
            lighting.downlight(ctx, ROOM, x, y, watts=130, kelvin=3000, name=f'dining.downlight.{i}')
            add(P.place(P.downlight(name=f'dining.downlight_trim.{i}'), (x, y, cz)), 'light')
            i += 1

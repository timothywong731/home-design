"""Dining room furnishing ("the most important part"): draw-leaf oak table, 8 Chippendale chairs, carved
fireplace + mantel ornaments, TV, mounted sword, 36 crest plaques, carved panels, triptych mirror,
check curtains, plants, chandelier, wall lights, downlights. Spec: spec/rooms/dining.md, corrected by
spec/phase2/ground_corrections.md (sections 1, 8, 9).

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --levels G --only shell,dining --preview dining --res 540x960 --samples 64 --tag dining

Room (world): x -0.65..3.10, y 12.36..16.86, ceiling 2.80. Chimney breast face x = 2.92, centred
y = 14.61. N wall (shell): three dark-lined recesses 0.38 deep (window -0.34..0.18, French doors 0.64..1.83,
window 2.295..2.815) with plastered piers 0.28..0.54 and 1.93..2.195 between them; window seats, recess linings
and architraves are joinery. Helpers: rooms/dining_furniture.py (shared mesh helpers, materials, table),
dining_chairs.py, dining_fire.py, dining_decor.py (panels, mirror, sword, plaques, curtains, dado ribbons),
dining_light.py, dining_plants.py.
"""
import math
import os

import bpy
from mathutils import Vector

from lib import interact as IX, lighting, mouldings as mo, props as P
from rooms import (dining_chairs as C, dining_decor as D, dining_fire as F, dining_furniture as U, dining_light as L,
                   dining_plants as G)

ROOM = 'dining'
X0, X1, Y0, Y1 = -0.65, 3.10, 12.36, 16.86      # inside wall faces: W, E, S (hall), N (pier faces)
BX, FY = 2.92, 14.61                            # chimney-breast face, fireplace centre line
HEARTH = 0.02                                   # the surround stands on the 20 mm hearth slab (shell)
SHELF = 1.19 + HEARTH                           # mantel shelf top
PIERS = (0.41, 2.0625)                          # N-wall pier centres (behind the tied curtains, D1)
RECESS_E = (2.295, 2.815)                       # clear width of the NE window recess
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
    # interaction checks (render with --pose 0 and --pose 1): live clock hands; closed curtains past the citrus
    dict(name='clock', pos=(2.20, 14.45, 1.44), look=(2.80, 14.61, 1.375), fov_deg=35, ref='f_0643'),
    # daylight re-walk (v2): east pier curtain + citrus in front of the NE recess; west recess and pier; switch
    dict(name='curtain', pos=(1.35, 15.70, 1.45), look=(2.25, 16.86, 1.30), fov_deg=95, ref='v2 f_0067'),
    dict(name='nwest', pos=(0.55, 15.55, 1.45), look=(-0.05, 16.95, 1.10), fov_deg=95, ref='v2 f_0129'),
    dict(name='switch', pos=(1.05, 13.25, 1.45), look=(0.62, 12.36, 1.25), fov_deg=70, ref='v2 f_0009'),
    dict(name='dado', pos=(0.15, 15.75, 1.35), look=(-0.65, 16.45, 0.75), fov_deg=70, ref='v2 f_0143'),
]

# crest plaques: generic heraldry (the real ones carry lettering). Muted enamels; a few light-blue / red ones.
_KINDS = ('bend', 'chief', 'party', 'bend', 'badge', 'chief', 'party')
_BOARDS = ('#6E4F31', '#3A2A20', '#3A2A20', '#6E4F31', '#3A2A20', '#6E4F31', '#6E4F31', '#3A2A20')    # mid-brown / near-black
_F1 = ('#1B2540', '#4A1A22', '#151515', '#1B2540', '#1F3326', '#4A1A22', '#232B4A', '#151515')
_F2 = ('#4A1A22', '#1B2540', '#151515', '#1B2540', '#C9C4B4', '#4A1A22', '#1F3326')
_SPECIAL = {9: '#6F93B5', 22: '#6F93B5', 5: '#8E1B1B', 27: '#8E1B1B'}


def _circ(name):
    """Tag kwargs of lighting circuit name (INTERACT.md, Circuits)."""
    return {'circuit': name}


def _crest(n):
    """Deterministic variety for plaque n -> dict(kind, board, field, field2)."""
    f1 = _SPECIAL.get(n, _F1[(n * 5 + n // 3) % len(_F1)])
    f2 = _F2[(n * 3 + 1) % len(_F2)]
    return dict(kind=_KINDS[n % len(_KINDS)], board=_BOARDS[n % len(_BOARDS)], field=f1,
                field2='#C9C4B4' if f2 == f1 else f2)


SILL_X, SILL_Z = 3.145, 1.104                   # E-window plants: pot centre on the sill board, board top (joinery)


def _sill_keep(y0, avoid=None):
    """keep(x, y, z) in the local frame of a monstera on the E sill at world y0 (local +X = world -Y, +Y = world +X,
    z above the board). Joinery of w_dining_e_*: reveal linings at y0 +- 0.256, architrave fronts x 3.079, frame
    inner face x 3.24. Inside the reveal the plant stays between the linings and short of the frame; in front of
    the architraves it keeps within 0.29 of the pot and 0.29 into the room; avoid = (x, y, r): a plan circle."""
    def ok(x, y, z):
        wx, wy = SILL_X + y, y0 - x
        if z < .01 or wx < SILL_X - .29 or abs(wy - y0) > .29:
            return False
        if wx > 3.072 and (abs(wy - y0) > .245 or wx > 3.23):
            return False
        return not (avoid and math.hypot(wx - avoid[0], wy - avoid[1]) < avoid[2])
    return ok


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
    add(P.place(F.fireplace(), (BX, FY, HEARTH), facing=(-1, 0)), 'fit', plan_sym='fireplace', lm='dynamic')
    clock = P.mantel_clock(hands=False, name='dining.mantel_clock')
    face = F.clock_face()                                         # round bezel + Roman strokes over the prop's dial
    face.parent = clock
    face.location = (0, -.0605, .1628)
    add(P.place(clock, east(0, .115, SHELF), facing=(-1, 0)), 'decor')
    # live hands (modelled at 12, the viewer turns them): origin on the cream dial of F.clock_face, 2.5 mm proud of it
    centre, out = clock.matrix_basis @ Vector((0, -.063, .1628)), clock.matrix_basis.to_3x3() @ Vector((0, -1, 0))
    for hand, w in zip(P.clock_hands(.0544, 'baton', 'black_matt', name='dining.mantel_clock'), 'hm'):
        hand.location, hand.rotation_euler = centre, clock.rotation_euler
        IX.tag(hand, 'clock', hand=w, p=centre, a=out)
        add(hand, 'decor', lm='dynamic')
    for i, s in enumerate((-1, 1)):
        add(P.place(F.candelabrum(f'dining.candelabrum.{i}'), east(s * .48, .125, SHELF), facing=(-1, 0)), 'decor')
        add(P.place(F.candlestick(f'dining.candlestick.{i}'), east(s * .68, .12, SHELF)), 'decor')
    # the original over the mantel is a wedding portrait: frame kept, picture replaced by a neutral, fully
    # synthetic landscape (reference/work/dining/make_landscape.py - no reference pixels)
    pic = P.framed_picture(os.path.join(U.ART, 'mantel_landscape.jpg'), .61, .85, 'gilt_swept', frame_w=.06, depth=.035,
                           mount=.105, slip=('#7A2A2A', .005), name='dining.mantel_picture')
    beads = D.frame_beads(.61, .85, .0504, -.0214)                # bead course on the frame's inner member
    beads.parent = pic
    add(P.place(pic, (BX, FY, 1.96), facing=(-1, 0)), 'decor')

    # ------------------------------------------------------------------ S wall: TV, switch, sword, plaques
    tv = add(P.place(P.tv_panel(1.89, 1.08, name='dining.tv'), (1.805, Y0, 1.69), facing=(0, 1)), 'fit', plan_sym='tv')
    pic = P.tv_screen(1.88, 1.07, name='dining.tv.picture')       # state 1 only, 1 mm proud of the black glass
    pic.location, pic.rotation_euler = tv.matrix_basis @ Vector((0, -.0716, 0)), tv.rotation_euler
    IX.tag(tv, 'trigger', g='dining.tv', label='TV')
    add(IX.tag(pic, 'show', g='dining.tv', when=1, fx='tv'), 'fit', lm='dynamic')
    # 3-gang rotary dimmer midway between TV and door (ground_corrections section 1, D7). Facing it: left (east, by
    # the TV) = wall lights, middle = chandelier, right (west, by the door) = spotlights. One knob per circuit
    # (INTERACT.md, Circuits): each switches only its own lamps and their baked light.
    sw = add(P.place(P.switch_plate(3, 'blank', wide=True, name='dining.switch'), (0.67, Y0, 1.30), facing=(0, 1)), 'fit',
             lm='dynamic')
    kb = mo.MB()
    kb.at(U.WALL)
    kb.lathe([(0, 0), (.0095, 0), (.0095, .008), (.0087, .0115), (.006, .013), (0, .013)], 'plastic_white', 16)
    kb.at()
    knob = U.fin(kb, 'dining.switch.knob')
    for i, (g, label, c) in enumerate((('dining.switch.wall_lights', 'Wall lights', 'wall'),
                                        ('dining.switch.chandelier', 'Chandelier', 'chandelier'),
                                        ('dining.switch', 'Spotlights', 'main'))):
        k = knob if i == 0 else bpy.data.objects.new('x', knob.data)
        k.name = f'dining.switch.knob.{i}'
        k.matrix_basis = sw.matrix_basis @ U.T(((i - 1) * .036, -.009, 0))      # local +X = viewer's right = west
        add(IX.tag(k, 'light', g=g, label=label, rooms=[ROOM], **_circ(c)), 'fit', lm='dynamic')
    IX.tag(sw, 'light', g='dining.switch', label='Spotlights', rooms=[ROOM], **_circ('main'))
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
    # projecting brass door stop on the W skirting (face x -0.63) reaching the parked leaf (face x -0.465 near the floor)
    sb = mo.MB()
    sb.lathe([(0, 0), (.016, 0), (.016, .004), (.006, .008), (.006, .148), (0, .148)], 'brass', 12)
    sb.lathe([(0, .148), (.011, .148), (.011, .162), (0, .162)], 'black_matt', 12)              # rubber tip
    stop = U.fin(sb, 'dining.door_stop')
    stop.rotation_euler = (0, math.pi / 2, 0)
    stop.location = (X0 + .02, 13.02, .09)
    add(stop, 'fit')

    # ------------------------------------------------------------------ sockets (ground_corrections section 9, D9)
    for i, (loc, f) in enumerate((((X1, 13.59, .33), (-1, 0)), ((X1, 15.63, .33), (-1, 0)), ((X0, 16.35, .40), (1, 0)))):
        add(P.place(P.socket(2, name=f'dining.socket.{i}'), loc, facing=f), 'fit')

    # ------------------------------------------------------------------ dado rail: reed-and-ribbon crossings (D6)
    c = dict(mo.TRIM[ROOM]['dado'])
    zb = ctx.floor_z(ROOM) + c['top'] - mo.profile_size(c['profile'])[1]
    runs = mo.trim_runs(ctx, (ROOM,), zb + .02, c)
    add(D.ribbon_crossings(runs, lambda x, y: x > BX - .25 and FY - .74 < y < FY + .74, zb), 'trim')

    # ------------------------------------------------------------------ N wall: check curtains on the two piers (D1, D5)
    # A white corded track under the pelmet carries a pair of check curtains that are tied back onto the wall piers
    # beside the French doors (state 0, as filmed); state 1 draws them across the doors, meeting on the doors' centre
    # line x = 1.225. The window recesses keep their deep seats clear (nothing to draw over them in the footage).
    YC = Y1 - .025                                                # back of the headings, clear of the 22 mm architraves
    track = P.box(PIERS[1] - PIERS[0] + .66, .022, .014, 'plastic_white', name='dining.curtain.track')
    add(P.place(track, ((PIERS[0] + PIERS[1]) / 2, Y1 - .034, 2.486)), 'decor')       # behind the headings
    for i, x in enumerate(PIERS):
        tied = add(P.place(D.curtain(f'dining.curtain.{i}', back=Y1 - YC), (x, YC, 2.50), facing=(0, -1)), 'decor')
        w = (1.235 - 0.28) if i == 0 else (2.195 - 1.215)
        shut = P.curtain_panel(w, 2.489, U.check_mat(), depth=.03, hardware=False, fold_res=4, seed=i,
                               name=f'dining.curtain.{i}.closed')
        add(P.place(shut, ((0.28 + w / 2) if i == 0 else (2.195 - w / 2), Y1 - .047, 2.499), facing=(0, -1)), 'decor',
            lm='dynamic')
        IX.tag(tied, 'show', g='dining.curtain', when=0, fx='none', label='Curtains')
        IX.tag(shut, 'show', g='dining.curtain', when=1, fx='none', label='Curtains')
        # the track's pull cords hang at the window-side edge of each heading (v2 f_0067, f_0111)
        add(P.place(D.pull_cords(f'dining.curtain.cords.{i}'), (x + (.315 if i else -.315), Y1 - .05, 2.479)), 'decor')

    # ------------------------------------------------------------------ plants
    # citrus in front of the NE window recess (v2 f_0035, f_0061, f_0067): its head pushes into the recess between the
    # architraves and stops short of the east curtain and the glass
    cx, cy = 2.62, 16.62
    for i, y in enumerate((13.02, 16.20)):                        # monstera on each E-window sill board (top 1.104)
        # inside its window surround (v1 f_0675, v2 f_0061); the north one keeps out of the citrus head
        keep = _sill_keep(y, (cx, cy, .43) if i else None)
        add(P.place(G.monstera(f'dining.monstera.{i}', seed=i, keep=keep), (SILL_X, y, SILL_Z), facing=(-1, 0)), 'decor')
    ok = lambda x, y, z: not ((y + cy > Y1 - .04 and not RECESS_E[0] + .04 < x + cx < RECESS_E[1] - .04)
                              or y + cy > Y1 + .33 or (x + cx < PIERS[1] + .23 and y + cy > Y1 - .16))
    add(P.place(G.citrus(keep=ok), (cx, cy, 0)), 'decor', plan_sym='plant')

    # ------------------------------------------------------------------ lighting: every fitting of the room
    rx, ry = mo.ROSE_AT[ROOM]
    chand = L.chandelier()
    add(P.place(chand, (rx, ry, cz - .035)), 'light')             # ceiling cup under the centre of the rose
    # clickable like the switch. Reach is measured from the walker's body column (eye 1.6) to the fitting's box (lowest
    # crystal ~2.05, the table keeps the walker 0.1-0.6 m off it sideways): 0.5 was out of reach from the floor
    IX.tag_many([chand] + list(chand.children_recursive), 'lamp', g='dining.chandelier', label='Chandelier',
                rooms=[ROOM], reach=1.2, **_circ('chandelier'))
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
        # on the wall-light circuit with its knob (INTERACT.md, Circuits)
        IX.tag_many([sc] + list(sc.children_recursive), 'lamp', g=sc.name, label='Wall light', rooms=[ROOM],
                    **_circ('wall'))
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

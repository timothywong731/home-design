"""Rear "blue" bedroom, first floor (spec/rooms/blue_bedroom.md, footage v3 f_0150..f_0490).

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --levels 1 --only shell,blue_bedroom --preview blue_bedroom \
        --res 540x960 --samples 64 --tag me          (--pose 1 for the open state, --cam <name> for one camera)

The shell stage brings walls, carpet, both doors with their pediments, the French doors with the dark reveal,
skirting and cornice. Here: furniture (rooms/blue_bedroom_furn.py), radiator, TV, air-con, switches and sockets,
pelmet and curtains, art and mirror, ceiling rose, star chandelier, mermaid wall light, bedside lamps, downlights.
Fabric and painting textures: rooms/blue_bedroom_tex.py -> textures/art/blue_bedroom_*.jpg.
World coordinates; the floor is Z 3.04 (heights in the comments are above the floor).
"""
import math
import os

import bpy
from mathutils import Vector

from lib import interact as IX, lighting, materials as M, mouldings as mo, props as P, shell
from rooms import blue_bedroom_furn as F
from rooms.blue_bedroom_furn import Piece, T, R, Z0, ART, BRASS

ROOM = 'blue_bedroom'
X0, X1, Y0, Y1 = -0.65, 3.10, 12.95, 16.86                   # main room; the entrance recess is x -0.65..0.47, y 12.52..12.95
# keyed to the spec in build(): east face of the entrance recess, d_balcony axis, pelmet ends, d_ensuite clear west edge
XR, AXIS, PEL, ENS = 0.47, 1.255, (0.20, 2.40), 1.34
AC = (-0.63, 0.17)                                           # X3 air-con unit on the north wall (x)
PEL_LEN = 2.20                                               # spec 3: pelmet 2.20 long, west end 30 mm short of the air-con
CAB = XR + 0.025 + 0.297                                     # TV cabinet centre: 25 mm short of the recess corner (v3 f_0185)
BREAST = -0.55                                               # face of the chimney breast (y 13.20..15.30)
ROSE = (1.28, 14.90)
RAD_Z = 0.22                                                 # X1 radiator bottom above the floor
W_DOWN, W_CANDLE, W_SCONCE, W_LAMP = 90, 9, 16, 5
EYE = Z0 + 1.50

CAMERAS = [
    dict(name='door', pos=(-0.10, 12.72, EYE + 0.05), look=(1.45, 16.8, Z0 + 1.15), fov_deg=100, ref='v3:f_0159'),
    dict(name='west', pos=(2.25, 14.75, EYE), look=(-0.65, 14.35, Z0 + 1.25), fov_deg=100, ref='v3:f_0171'),
    dict(name='south', pos=(1.05, 15.7, EYE), look=(0.85, 12.9, Z0 + 1.3), fov_deg=100, ref='v3:f_0353'),
    dict(name='wardrobe', pos=(0.75, 14.25, EYE), look=(3.1, 13.6, Z0 + 1.1), fov_deg=100, ref='v3:f_0205'),
    dict(name='bed', pos=(0.35, 13.5, EYE + 0.05), look=(2.8, 16.1, Z0 + 0.95), fov_deg=100, ref='v3:f_0453'),
    dict(name='bedside', pos=(1.0, 16.45, EYE), look=(3.1, 14.9, Z0 + 0.95), fov_deg=100, ref='v3:f_0231'),
    dict(name='bureau', pos=(1.1, 16.45, EYE - 0.05), look=(-0.65, 15.0, Z0 + 1.15), fov_deg=100, ref='v3:f_0463'),
    dict(name='north', pos=(1.25, 14.1, EYE), look=(1.2, 16.86, Z0 + 1.75), fov_deg=100, ref='v3:f_0345'),
    dict(name='chandelier', pos=(-0.35, 15.1, EYE + 0.1), look=(3.0, 15.3, Z0 + 1.95), fov_deg=100, ref='v3:f_0471'),
    dict(name='recess', pos=(-0.35, 12.58, EYE), look=(0.47, 12.95, Z0 + 1.25), fov_deg=95, ref='v3:f_0163'),
    dict(name='back', pos=(2.35, 16.45, EYE + 0.05), look=(0.0, 12.9, Z0 + 1.2), fov_deg=100, ref='v3:f_0459'),
]


def _circ(name):
    """Tag kwargs of lighting circuit name (INTERACT.md, Circuits)."""
    return {'circuit': name}


def _add(ctx, ob, kind, plan_sym=None, lm=None):
    return ctx.add(ob, ROOM, kind, plan_sym=plan_sym, lm=lm)


def gilt():
    return M.solid('blue_bedroom_gilt', '#C9B768', 0.28, metallic=1)


def crystal():
    """Cut crystal as in the dining room: the library mirror-glass at 60 % with a faint warm lift (glTF-safe)."""
    m = bpy.data.materials.get('blue_bedroom_crystal')
    if m is None:
        m = M.mat('glass_clear').copy()
        m.name = 'blue_bedroom_crystal'
        b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        b.inputs['Alpha'].default_value = 0.85
        b.inputs['Base Color'].default_value = M.hex_lin('#FFF4E2')                     # the library pane is cool
        b.inputs['Emission Color'].default_value = M.hex_lin('#F2C070')
        b.inputs['Emission Strength'].default_value = 1.4
    return m


# ------------------------------------------------------------------------------------------ fixed fittings
def radiator(ctx):
    """X1: white horizontal column radiator 1.33 x 0.60 on the breast: 19 oval tubes at 70 mm, two rows (19 counted
    in the full-res still v3 t170: 615 px wide, 32.4 px per tube, ~10 mm gaps). Bottom 0.22 above the floor (was 0.15):
    in v3 f_0171 / t170 / f_0175 / f_0463 a strip of navy wall shows between its tubes and the skirting top (0.17)
    even from above, which a radiator 0.137 proud at 0.15 would hide; a camera pose on t170 (cornice, skirting, TV and
    radiator outlines) puts the bottom at 0.215-0.24."""
    pc = Piece(ctx, 'blue_bedroom.radiator', BREAST, 14.25, (1, 0), kind='fit')
    zb = RAD_Z

    def body(mb):
        Wm, r = 'white_gloss', 0.030
        for y in (-0.064, -0.118):
            for i in range(19):
                mb.at(T((i - 9) * 0.070, y, zb))
                mb.lathe([(0, 0), (r * 0.55, 0.004), (r, 0.03), (r, 0.57), (r * 0.55, 0.596), (0, 0.60)], Wm, segs=8, ell=(1, 0.62))
        mb.at()
        for z in (zb + 0.04, zb + 0.56):
            mb.box((-0.655, -0.105, z - 0.012), (0.655, -0.077, z + 0.012), Wm)            # headers between the rows
        for sx in (-1, 1):
            mb.box((sx * 0.45 - 0.012, -0.08, zb + 0.15), (sx * 0.45 + 0.012, 0, zb + 0.45), Wm)   # wall brackets
            mb.tube([(sx * 0.705, -0.09, 0.0), (sx * 0.705, -0.09, zb + 0.04), (sx * 0.66, -0.09, zb + 0.04)], 0.008, 'chrome', n=6)
            mb.box((sx * 0.705 - 0.014, -0.104, zb + 0.015), (sx * 0.705 + 0.014, -0.076, zb + 0.065), 'chrome', bev=0.004)
        mb.at(T(0.705, -0.09, zb + 0.065))                                                 # TRV head on the north valve
        mb.lathe([(0, 0), (0.019, 0), (0.021, 0.045), (0.015, 0.058), (0, 0.058)], 'plastic_white', segs=10)
        mb.at()

    pc.add('', body, plan_sym='radiator')


def television(ctx):
    """X2: 55 inch set centred on the breast, z 1.14..1.85 (was 1.20..1.91): camera pose on v3 t170 1.13-1.15, the
    critic's 1-D fits on f_0171 / t170 1.125-1.17 and f_0459 (top 0.725 under the cornice) agree within 0.03, one
    vanishing-point estimate on t170 gives 1.22. Blank glass, the picture shows in state 1."""
    tv = P.tv_panel(1.23, 0.71, depth=0.05, standoff=0.03, bezel=0.008, name='blue_bedroom.tv')
    _add(ctx, P.place(tv, (BREAST, 14.25, Z0 + 1.495), facing=(1, 0)), 'fit', 'tv', lm='static')
    pic = P.tv_screen(1.214, 0.694, name='blue_bedroom.tv.picture')
    pic.location, pic.rotation_euler = tv.matrix_basis @ Vector((0, -0.0816, 0)), tv.rotation_euler
    _add(ctx, pic, 'fit', lm='dynamic')
    IX.tag(tv, 'trigger', g='blue_bedroom.tv', label='TV')
    IX.tag(pic, 'show', g='blue_bedroom.tv', when=1, fx='tv', label='TV')


def wall_fittings(ctx):
    """Air-con unit, remote cradle, coat hooks, door stop: one static mesh in world coordinates."""
    mb, Wp = mo.MB(), 'plastic_white'
    # X3 air-con indoor unit on the north wall, x -0.63..0.17, 2.10..2.39, 0.22 deep (no branding)
    z0, z1, ya, a = Z0 + 2.10, Z0 + 2.39, Y1 - 0.22, AC[0]
    mb.prism([(a, Y1, z1), (a, ya + 0.02, z1), (a, ya, z1 - 0.025), (a, ya, z0 + 0.10), (a, ya + 0.045, z0),
              (a, Y1, z0)], (AC[1] - AC[0], 0, 0), Wp)
    mb.box((-0.60, ya - 0.0015, z0 + 0.105), (-0.07, ya, z0 + 0.109), M.solid('blue_bedroom_ac_gap', '#8E9092', 0.6))   # flap joint
    mb.box((-0.07, ya - 0.0015, z0 + 0.03), (-0.066, ya, z0 + 0.20), M.solid('blue_bedroom_ac_gap', '#8E9092', 0.6))
    mb.at(T(0.07, ya, z0 + 0.075) @ R('X', 90))
    mb.lathe([(0.016, 0), (0.016, 0.002), (0, 0.002)], M.solid('blue_bedroom_ac_eye', '#B9BEC4', 0.2), segs=12)       # sensor
    mb.at()
    # X4 remote in its cradle on the recess wall (x 0.47, faces west), y 12.84, 1.30..1.48; blank LCD
    mb.box((XR - 0.022, 12.805, Z0 + 1.30), (XR, 12.875, Z0 + 1.40), Wp, bev=0.004)
    mb.box((XR - 0.028, 12.815, Z0 + 1.32), (XR - 0.010, 12.865, Z0 + 1.48), Wp, bev=0.004)
    mb.box((XR - 0.0288, 12.822, Z0 + 1.42), (XR - 0.028, 12.858, Z0 + 1.465), M.solid('blue_bedroom_lcd', '#8E9A90', 0.3))
    # X5 coat-hook rail in the south alcove of the west wall (behind the open door), four brass double hooks
    mb.box((X0, 12.80, Z0 + 1.57), (X0 + 0.018, 13.18, Z0 + 1.67), 'dark_joinery', bev=0.004, grain=1)
    for k in range(4):
        y, x, z = 12.85 + 0.093 * k, X0 + 0.018, Z0 + 1.62
        mb.box((x, y - 0.012, z - 0.03), (x + 0.004, y + 0.012, z + 0.03), BRASS, bev=0.002)
        mb.tube([(x, y, z - 0.012), (x + 0.03, y, z - 0.03), (x + 0.045, y, z - 0.022), (x + 0.048, y, z + 0.002)], 0.0035, BRASS, n=5)
        mb.tube([(x, y, z + 0.012), (x + 0.025, y, z + 0.02), (x + 0.042, y, z + 0.04), (x + 0.045, y, z + 0.065)], 0.0035, BRASS, n=5)
    # X6 projecting door stop on the west skirting: reaches the open d_blue leaf (its back face stands 0.136 off the wall)
    mb.at(T(X0 + 0.02, 12.90, Z0 + 0.08) @ R('Y', 90))
    mb.lathe([(0.016, 0), (0.016, 0.004), (0.006, 0.008), (0.006, 0.096), (0.009, 0.098), (0, 0.098)], BRASS, segs=10)
    mb.lathe([(0.009, 0.098), (0.011, 0.10), (0.011, 0.11), (0, 0.11)], 'black_matt', segs=10)          # rubber tip
    mb.at()
    _add(ctx, mb.finish('blue_bedroom.wall_fittings'), 'fit')


def electrics(ctx):
    """Switch plates (each a `light` tag for what it really controls), sockets, fan isolator."""
    # S1 three-gang on the recess wall, one rocker per circuit (spec 8, INTERACT.md Circuits). Facing it (east):
    # left (north) = the wall light, middle = the downlights (with the plate), right (south) = the chandelier
    loc, f = (XR, 12.69, Z0 + 1.30), (-1, 0)
    sw = P.place(P.switch_plate(1, 'blank', wide=True, name='blue_bedroom.switch'), loc, facing=f)
    IX.tag(_add(ctx, sw, 'fit', lm='dynamic'), 'light', rooms=[ROOM], label='Spotlights', **_circ('main'))
    for i, (what, label) in enumerate((('wall_light', 'Wall light'), ('downlights', 'Spotlights'),
                                       ('chandelier', 'Chandelier'))):
        mb = mo.MB().at(T((i - 1) * 0.036, -0.009, 0) @ R('X', 6))           # local +x = south
        mb.box((-0.011, -0.0045, -0.017), (0.011, 0.001, 0.017), 'plastic_white', bev=0.0008)
        ro = _add(ctx, P.place(mb.finish(f'blue_bedroom.switch.{what}'), loc, facing=f), 'fit', lm='dynamic')
        if what == 'downlights':
            IX.tag(ro, 'light', g='blue_bedroom.switch', rooms=[ROOM], label=label, **_circ('main'))
        else:
            IX.tag(ro, 'lamp', g=f'blue_bedroom.{what}', label=label)              # the fitting's own circuit
    # S2 beside the en-suite door: the en-suite lights
    # v3 t352 puts S2 0.19 and the isolator 0.20 west of the clear opening; the block face is shorter in the spec than
    # in the footage, so they keep clear of the moved cabinet (east edge CAB + 0.297) and of the pediment shelf (ENS - 0.16)
    sx2, sxi = ENS - 0.19, ENS - 0.25
    sw = P.place(P.switch_plate(1, 'rocker', name='blue_bedroom.switch.ensuite'), (sx2, Y0, Z0 + 1.30), facing=(0, 1))
    IX.tag(_add(ctx, sw, 'fit'), 'light', rooms=['blue_ensuite'], label='En-suite light')
    # S3 right of the east curtain: the balcony lantern (assumed, not demonstrated)
    sw = P.place(P.switch_plate(1, 'rocker', name='blue_bedroom.switch.balcony'), (2.55, Y1, Z0 + 1.25), facing=(0, -1))
    IX.tag(_add(ctx, sw, 'fit'), 'light', rooms=['balcony'], label='Balcony light')
    for i, (loc, f, g) in enumerate((((max(CAB + 0.38, sx2), Y0, Z0 + 0.30), (0, 1), 2),     # X7 beside the cabinet
                                     ((X1, 14.50, Z0 + 0.85), (-1, 0), 1), ((X1, 16.17, Z0 + 0.75), (-1, 0), 1))):   # X8 bedside
        _add(ctx, P.place(P.socket(g, name=f'blue_bedroom.socket.{i}'), loc, facing=f), 'fit')
    iso = P.place(P.switch_plate(1, 'rocker', name='blue_bedroom.fan_isolator'), (sxi, Y0, Z0 + 2.11), facing=(0, 1))
    _add(ctx, iso, 'fit')                    # X9 over S2, ~45 mm clear of the en-suite pediment shelf (f_0353)


# ------------------------------------------------------------------------------------------ north wall: pelmet, curtains
def pelmet(ctx):
    """White boxed pelmet x 0.20..2.40 (spec 3: 2.20 long, its west end 30 mm short of the air-con; it stands 45 mm
    east of the d_balcony axis and its east return sits over the S3 switch, as in v3 t452), 0.16 proud: fascia
    2.30..2.47 with the room cornice mitred round it."""
    cz, yf, (xa, xb) = ctx.ceil_z(ROOM), Y1 - 0.16, PEL
    mb, Wj = mo.MB(), 'joinery_white'
    mb.box((xa, yf, Z0 + 2.30), (xb, yf + 0.018, cz), Wj, grain=0)
    for x in (xa, xb - 0.018):
        mb.box((x, yf + 0.018, Z0 + 2.30), (x + 0.018, Y1, cz), Wj, grain=1)
    mb.box((xa + 0.018, Y1 - 0.075, Z0 + 2.445), (xb - 0.018, Y1 - 0.055, Z0 + 2.46), 'plastic_white')          # curtain track
    mo.cornice(mb, 'cornice_blue', [(xb, Y1, cz), (xb, yf, cz), (xa, yf, cz), (xa, Y1, cz)])
    _add(ctx, mb.finish('blue_bedroom.pelmet'), 'trim')


def curtains(ctx):
    """D4: full-length navy Art-Nouveau print curtains on the pelmet track. State 0 tied back with navy rope
    tie-backs, state 1 drawn across the pelmet between its returns."""
    cloth = F.art('curtain', (0.21, 0.28))
    kw = dict(width=PEL[1] - PEL[0] - 0.04, height=2.43, mat=cloth, stack=0.40, tie_from_top=1.44, gather=0.75, hang=None, hardware=False,
              depth=0.05, tie_mat='#232838', tassel_mat='#232838')
    tied = P.curtain_pair(name='blue_bedroom.curtain.open', **kw)
    shut = P.curtain_pair(closed=True, fold_res=4, name='blue_bedroom.curtain.closed', **kw)
    for ob, when in ((tied, 0), (shut, 1)):
        _add(ctx, P.place(ob, ((PEL[0] + PEL[1]) / 2, Y1 - 0.012, Z0 + 2.44), facing=(0, -1)), 'decor', lm='dynamic')
        IX.tag(ob, 'show', g='blue_bedroom.curtains', when=when, fx='none', label='Curtains')


# ------------------------------------------------------------------------------------------ art, mirror, ornaments
def art(ctx):
    # A1 landscape oil over the bureau (rectified crop, rider painted out), moulded gold frame with a pale liner
    pic = P.framed_picture(os.path.join(ART, 'blue_bedroom_landscape.jpg'), 0.88, 0.75, 'gilt_swept', frame_w=0.095,
                           depth=0.04, slip=('#D9D3BC', 0.012), name='blue_bedroom.painting.landscape')
    _add(ctx, P.place(pic, (X0, 16.01, Z0 + 1.775), facing=(1, 0)), 'decor')
    # A2 near-black canvas in a narrow gold frame (subject unreadable in the footage: plain dark abstract)
    pic = P.framed_picture(None, 0.50, 0.70, 'gilt_plain', frame_w=0.03, depth=0.022, fill=('#17181A', '#1E1B19', '#141517'),
                           name='blue_bedroom.painting.dark')
    _add(ctx, P.place(pic, (-0.15, Y1, Z0 + 1.60), facing=(0, -1)), 'decor')


def octagon_mirror(ctx):
    """A3: 1920s oak wall mirror 0.95 x 0.66 with the corners cut at 45 degrees, beaded inner edge, bevelled plate,
    hung on a chain over the headboard (z 1.66..2.32), tilted 3 degrees. Size and height measured in v3 t452 (wide
    shot, mirror near the centre): headboard 145 px = 1.46 m -> mirror 94 px = 0.95 wide; crest top 1.45 to cornice
    underside 2.52 = 144 px -> mirror 88 px = 0.65 high, 30 px (0.22) over the crest, 26 px (0.19) under the
    cornice; +/- 0.04 (the phase-2 0.86 x 0.60 at 1.58 sat too low and too small against v3 f_0453 / t452)."""
    pc = Piece(ctx, 'blue_bedroom.mirror', X1, 15.36, (-1, 0), z=Z0 + 1.66, kind='decor')
    O, a, b, H, c, fw = 'dark_oak_antique', -0.475, 0.475, 0.66, 0.16, 0.06

    def body(mb):
        back, o1, o2 = F.oct_ring(a, b, 0, H, 0, 0.0, c), F.oct_ring(a, b, 0, H, 0, -0.024, c), F.oct_ring(a, b, 0, H, 0.012, -0.03, c)
        i1, i2 = F.oct_ring(a, b, 0, H, fw - 0.008, -0.034, c), F.oct_ring(a, b, 0, H, fw, -0.016, c)
        n = len(back)
        for j in range(n):
            k = (j + 1) % n
            mid = Vector(back[j]) + Vector(back[k])
            out = Vector((mid.x, 0, mid.z - H))                                            # points away from the centre
            mb.face([back[j], back[k], o1[k], o1[j]], O, out)
            mb.face([o1[j], o1[k], o2[k], o2[j]], O, (0, -1, 0))
            mb.face([o2[j], o2[k], i1[k], i1[j]], O, (0, -1, 0))
            mb.face([i1[j], i1[k], i2[k], i2[j]], O, -out)
            e = Vector(i1[k]) - Vector(i1[j])                                              # bead course on the inner edge
            m = max(1, int(e.length / 0.03))
            for q in range(m):
                p = Vector(i1[j]) + e * ((q + 0.5) / m)
                mb.at(T(p.x, p.y + 0.001, p.z) @ R('X', 90))
                mb.dome(0.008, 0.008, 0.006, O, segs=6, rings=2)
            mb.at()
        F.mirror_plate(mb, a + fw, b - fw, fw, H - fw, -0.02, bevel=0.022, cut=c - 0.586 * fw)
        for sx in (-1, 1):                                                                 # paterae on the upright sides
            mb.at(T(sx * (b - fw / 2), -0.031, H / 2) @ R('X', 90))
            mb.dome(0.012, 0.03, 0.007, O, segs=8)
        mb.at(T(0, -0.031, fw / 2) @ R('X', 90))                                           # tablet at the bottom centre
        mb.dome(0.06, 0.012, 0.007, O, segs=8)
        mb.at()
        mb.tube([(-0.17, -0.01, H), (0, -0.004, H + 0.09), (0.17, -0.01, H)], 0.002, BRASS, n=4)   # chain to one hook
        mb.box((-0.006, -0.012, H + 0.08), (0.006, 0, H + 0.105), BRASS, bev=0.002)            # (under the 2.47 cornice)

    pc.add('', body, plan_sym='mirror', L=R('X', 3))


def bureau_ornaments(ctx, pc):
    """D3 on the bureau top (north end): glass vase with dried cotton stems to 1.75, black oil burner, tea-light on cork."""
    def body(mb):
        z = 1.005
        vy = -0.10                                                                         # vase 0.10 off the back
        mb.at(T(0.30, vy, z))                                                              # vase
        mb.lathe([(0.032, 0), (0.034, 0.003), (0.03, 0.06), (0.026, 0.16), (0.034, 0.25)], 'glass_clear', segs=12)
        stem, boll = M.solid('blue_bedroom_stem', '#6B5440', 0.9), M.solid('blue_bedroom_cotton', '#EEEAE0', 1.0)
        for k, (dx, dy, h) in enumerate(((-0.10, -0.02, 0.62), (-0.04, -0.03, 0.72), (0.03, -0.03, 0.75), (0.07, -0.02, 0.66),
                                         (-0.01, -0.04, 0.55), (0.10, -0.03, 0.50))):     # dy < 0: leaning into the room,
            pts = [(dx * t * t, dy * t * t, 0.01 + h * t) for t in (0, 0.35, 0.7, 1.0)]      # clear of the painting (x -0.61)
            mb.tube(pts, 0.0022, stem, n=4)
            for j, t in enumerate((1.0, 0.78, 0.58)):                                      # cotton bolls up the stem
                bx, by, bz = dx * t * t + 0.022 * ((j + k) % 3 - 1), dy * t * t + 0.018 * ((j * 2 + k) % 3 - 1), 0.01 + h * t
                mb.at(T(0.30 + bx, vy + by, z + bz))
                mb.lathe([(0, -0.028), (0.022, -0.016), (0.03, 0.0), (0.022, 0.018), (0, 0.028)], boll, segs=6)
                mb.at(T(0.30, vy, z))
        mb.at(T(0.13, -0.07, z))                                                           # oil burner
        mb.lathe([(0.03, 0), (0.034, 0.02), (0.026, 0.055), (0.04, 0.085), (0.04, 0.09), (0.03, 0.088), (0, 0.075)],
                 'black_gloss', segs=12)
        mb.at(T(0.02, -0.07, z))                                                           # tea-light glass on a cork coaster
        mb.lathe([(0, 0), (0.045, 0), (0.045, 0.006), (0, 0.006)], 'cork', segs=12)
        mb.lathe([(0.026, 0.006), (0.03, 0.012), (0.032, 0.065)], 'glass_clear', segs=10)
        mb.lathe([(0, 0.008), (0.019, 0.008), (0.019, 0.022), (0, 0.022)], M.solid('blue_bedroom_wax', '#EFE9DC', 0.6), segs=8)
        mb.at()
    pc.add('ornaments', body, kind='decor')


def alarm_clock(ctx, pc):
    """D2: small black twin-bell alarm clock on the north nightstand, bed side; live hands."""
    cx, cy, zc, r = 0.125, -0.235, 0.60 + 0.058, 0.043
    Mc = T(cx, cy, 0)

    def body(mb):
        K = 'black_gloss'
        mb.at(Mc @ T(0, 0, zc) @ R('X', 90))                                               # case: drum with its axis on y
        mb.lathe([(0, -0.018), (r, -0.018), (r, 0.016), (r - 0.004, 0.018), (r - 0.004, 0.0165), (0, 0.0165)], K, segs=20)
        mb.lathe([(0, 0.0166), (r - 0.0045, 0.0166), (r - 0.0045, 0.0168), (0, 0.0168)], P.mat('dial_cream'), segs=20)
        mb.at(Mc)
        for sx in (-1, 1):
            mb.at(Mc @ T(sx * 0.027, 0, zc + r + 0.003) @ R('Y', sx * 28))                 # bells
            mb.dome(0.019, 0.019, 0.014, K, segs=10)
            mb.at(Mc)
            mb.tube([(sx * 0.025, 0, zc - r + 0.006), (sx * 0.036, 0, 0.6028)], 0.003, K, n=5)   # feet (stand on the top)
        mb.tube([(-0.02, 0, zc + r + 0.022), (0, 0, zc + r + 0.03), (0.02, 0, zc + r + 0.022)], 0.002, K, n=4)   # handle
        mb.at()

    pc.add('alarm_clock', body, kind='decor')
    centre, out = pc.pt((cx, cy - 0.0169, zc)), pc.vec((0, -1, 0))
    for hand, w in zip(P.clock_hands(r - 0.008, 'baton', mat='black_matt', name='blue_bedroom.alarm_clock'), 'hm'):
        hand.matrix_basis = pc.M @ T(cx, cy - 0.0169, zc)
        IX.tag(hand, 'clock', hand=w, p=centre, a=out)
        _add(ctx, hand, 'decor', lm='dynamic')


# ------------------------------------------------------------------------------------------ lights
def rose(ctx):
    """L1r: plaster ceiling rose, dia 0.55: plain centre boss, ring of radiating acanthus leaves, egg band."""
    cz, PW = ctx.ceil_z(ROOM), 'plaster_white'
    mb = mo.MB()
    M0 = T(ROSE[0], ROSE[1], cz) @ R('X', 180)
    mb.at(M0)
    mb.lathe([(0.275, 0), (0.275, 0.012), (0.262, 0.02), (0.252, 0.013), (0.234, 0.013), (0.224, 0.022), (0.212, 0.014),
              (0.085, 0.012), (0.075, 0.022), (0.055, 0.026), (0, 0.026)], PW, segs=40)
    for k in range(16):
        mb.at(M0 @ R('Z', 22.5 * k) @ T(0, 0.088, 0.012))
        mb.leaf(0.122, 0.052, 0.013, PW, segs=5, serrate=0.3, curl=0.3)
    for k in range(36):
        mb.at(M0 @ R('Z', 10 * k) @ T(0, 0.243, 0.013))
        mb.dome(0.009, 0.013, 0.008, PW, segs=6, rings=2)
    mb.at()
    _add(ctx, mb.finish('blue_bedroom.rose'), 'trim')


def _bead(mb, mi, p, r):
    x, y, z = p
    v = mb._vs([(x + r, y, z), (x - r, y, z), (x, y + r, z), (x, y - r, z), (x, y, z + r * 1.25), (x, y, z - r * 1.25)])
    for a, b, c in ((0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4), (2, 0, 5), (1, 2, 5), (3, 1, 5), (0, 3, 5)):
        mb._f([v[a], v[b], v[c]], mi)


def _string(mb, mi, p0, p1, sag=0.0, pitch=0.014, r=0.006, ends=True):
    p0, p1 = Vector(p0), Vector(p1)
    n = max(2, int((p1 - p0).length / pitch))
    for i in range(0 if ends else 1, n + 1 if ends else n):
        t = i / n
        p = p0.lerp(p1, t)
        p.z -= sag * 4 * t * (1 - t)
        _bead(mb, mi, p, r)


def _rope(mb, mi, p0, p1, sag=0.0, pitch=0.012, r=0.0075, tw=0.0035, ends=False):
    """Twisted crystal bead rope (v3 t466): beads on a slack line, each turned 125 degrees round it."""
    p0, p1 = Vector(p0), Vector(p1)
    d = (p1 - p0).normalized()
    n1 = d.cross(Vector((0, 0, 1)))
    n1 = n1.normalized() if n1.length > 1e-6 else Vector((1, 0, 0))
    n2 = n1.cross(d)
    n = max(2, int((p1 - p0).length / pitch))
    for i in range(0 if ends else 1, n + 1 if ends else n):
        t, a = i / n, 2.18 * i
        p = p0.lerp(p1, t) + (n1 * math.cos(a) + n2 * math.sin(a)) * tw
        p.z -= sag * 4 * t * (1 - t)
        _bead(mb, mi, p, r)


def chandelier(ctx):
    """L1: brass star chandelier, eight points, 0.80 across (1.59 x the 0.55 rose in v3 f_0471, less the 9 % it
    gains hanging 0.4 nearer the camera): a flat brass rim with upturned points, a fringe of crystal strands
    hanging off it (12 mm apart), twisted bead ropes in 16 nested star rings down to a bottom finial (a shallow star
    basket), six candle lamps inside; nothing above the rim but the rod (v3 t466 / t470).
    Rim 2.23 (points 2.27), bottom 1.98 above the floor, on a rod and chain from a brass cup on the rose."""
    cz = ctx.ceil_z(ROOM)
    BR, CR = M.solid('blue_bedroom_brass', '#CDC47E', 0.18, metallic=1), crystal()
    ZR, ZB, RT, RV, TIP = -0.37, -0.62, 0.40, 0.22, 0.045                                 # rim / bottom below the ceiling
    Mc = T(ROSE[0], ROSE[1], cz - 0.026)

    def node(k, s):                                                                        # k: 16 rim nodes, tips even
        rr = (RT if k % 2 == 0 else RV) * s
        a = math.pi * k / 8
        lift = TIP * s ** 6 if k % 2 == 0 else 0.0                                         # the points turn up (t470)
        return (rr * math.cos(a), rr * math.sin(a), ZB + (ZR - ZB) * s ** 2.2 + lift)

    cands = [(0.10 * math.cos(math.pi * (k + 0.5) / 3), 0.10 * math.sin(math.pi * (k + 0.5) / 3), ZB + 0.10) for k in range(6)]

    def frame(mb):
        mb.at(R('X', 180))
        mb.lathe([(0.055, 0), (0.055, 0.006), (0.04, 0.022), (0.02, 0.04), (0.008, 0.05), (0, 0.05)], BR, segs=16)   # ceiling cup
        mb.at()
        mb.tube([(0, 0, -0.045), (0, 0, -0.17)], 0.004, BR, n=6)                           # rod
        for i in range(4):                                                                 # chain
            mb.at(T(0, 0, -0.185 - 0.028 * i) @ R('Z', 90 * (i % 2)))
            mb.tube([(0.008 * math.cos(a), 0, 0.016 * math.sin(a)) for a in (math.pi * j / 4 for j in range(8))], 0.0018, BR,
                    n=4, closed=True, up=(0, 1, 0))
        mb.at(T(0, 0, -0.31))
        mb.lathe([(0, -0.02), (0.012, -0.018), (0.03, 0.0), (0.03, 0.006), (0.01, 0.02), (0, 0.022)], BR, segs=12)   # crown
        mb.at()
        mb.tube([(0, 0, -0.31), (0, 0, ZB - 0.01)], 0.004, BR, n=6)                        # stem
        for dz in (0.0, -0.009):                                                           # star rim: a flat brass band
            mb.tube([(x, y, z + dz) for x, y, z in (node(k, 1.0) for k in range(16))], 0.0035, BR, n=5, closed=True)
        for k in range(16):                                                                # ribs of the basket
            mb.tube([node(k, s) for s in (1.0, 0.8, 0.6, 0.4, 0.22, 0.08)], 0.0026, BR, n=4)
        mb.at(T(0, 0, ZB - 0.035))
        mb.lathe([(0, 0), (0.012, 0.004), (0.028, 0.02), (0.03, 0.03), (0.012, 0.05), (0, 0.055)], BR, segs=12)      # bottom boss
        mb.at()
        ivory, flame = P.mat('ivory'), P.emissive('#FFD9A0', 6.0)
        for x, y, z in cands:                                                              # candle lamps on scroll arms
            mb.tube([(0, 0, z - 0.05), (x * 0.5, y * 0.5, z - 0.07), (x, y, z - 0.03), (x, y, z)], 0.003, BR, n=5)
            mb.at(T(x, y, z))
            mb.lathe([(0, 0), (0.017, 0), (0.019, 0.008), (0.01, 0.012), (0, 0.012)], BR, segs=10)
            mb.lathe([(0.009, 0.012), (0.009, 0.075), (0, 0.075)], ivory, segs=8)
            mb.lathe([(0, 0.075), (0.007, 0.08), (0.009, 0.092), (0.004, 0.11), (0, 0.118)], flame, segs=8)
            mb.at()

    def crystals(mb):
        # dense like the real one (v3 t466 from below: ~16 nested twisted ropes per point; t452 / f_0459 from the side:
        # a solid sparkling basket with a close fringe off every rim edge)
        mi = mb.mi(CR)
        NR = 16
        for q in range(1, NR + 1):                                                         # nested star rings: ropes
            s = q / NR
            for k in range(16):
                _rope(mb, mi, node(k, s), node((k + 1) % 16, s), sag=0.004)
                _bead(mb, mi, node(k, s), 0.0085)
        for k in range(16):                                                              # fringe hanging off the rim
            p0, p1 = Vector(node(k, 1.0)), Vector(node((k + 1) % 16, 1.0))
            n = int((p1 - p0).length / 0.012)
            for i in range(n):
                p = p0.lerp(p1, (i + 0.5) / n) + Vector((0, 0, -0.012))
                q = p + Vector((-p.x, -p.y, 0)).normalized() * 0.02 + Vector((0, 0, -(0.12, 0.15, 0.135)[i % 3]))
                _string(mb, mi, p, q, pitch=0.0135, r=0.0055)
                _bead(mb, mi, q + Vector((0, 0, -0.008)), 0.0075)
        _bead(mb, mi, (0, 0, ZB - 0.06), 0.02)                                             # ball finial and drops
        for k in range(8):
            a = math.pi * k / 4
            _string(mb, mi, (0.028 * math.cos(a), 0.028 * math.sin(a), ZB - 0.015), (0.01 * math.cos(a), 0.01 * math.sin(a), ZB - 0.07),
                    pitch=0.012, r=0.005)

    objs = []
    for sub, fn in (('', frame), ('crystals', crystals)):
        mb = mo.MB()
        fn(mb)
        ob = mb.finish('blue_bedroom.chandelier' + ('.' + sub if sub else ''))
        ob.matrix_basis = Mc
        objs.append(_add(ctx, ob, 'light'))
    # its own circuit with the south rocker of S1 (INTERACT.md, Circuits); clickable, short reach
    IX.tag_many(objs, 'lamp', g='blue_bedroom.chandelier', label='Chandelier', reach=0.5)
    for i, c in enumerate(cands):
        lighting.bulb(ctx, ROOM, Mc @ Vector((c[0], c[1], c[2] + 0.095)), watts=W_CANDLE, name=f'blue_bedroom.chandelier.bulb.{i}')


def wall_light(ctx):
    """L3: gilt-brass mermaid wall light on the block face over the cabinet: round gadrooned backplate, curled tail
    for an arm, winged figure holding a torch up, cream scalloped shade (top 2.05)."""
    pc = Piece(ctx, 'blue_bedroom.wall_light', CAB + 0.11, Y0, (0, 1), z=Z0 + 1.66, kind='light')   # over the east door
    G = gilt()

    def body(mb):
        mb.at(R('X', 90))
        mb.lathe([(0.065, 0), (0.065, 0.007), (0.054, 0.016), (0.04, 0.017), (0.03, 0.028), (0.012, 0.032), (0, 0.032)], G, segs=20)
        for k in range(16):                                                                # gadroons
            mb.at(R('X', 90) @ R('Z', 22.5 * k) @ T(0, 0.047, 0.014))
            mb.dome(0.006, 0.011, 0.005, G, segs=6, rings=2)
        mb.at()
        mb.tube([(0, -0.03, 0), (0, -0.075, 0.0), (0, -0.10, -0.012)], 0.011, G, n=8)      # arm from the plate
        tail = []
        for i in range(17):                                                                # the tail: a scroll curling under
            a = math.radians(70 - 310 * i / 16)
            rr = 0.062 - 0.03 * i / 16
            tail.append((0, -0.15 + rr * math.cos(a), -0.035 + rr * math.sin(a)))
        mb.tube(tail, 0.017, G, n=8, up=(1, 0, 0))
        mb.at(T(0, -0.182, -0.115) @ R('X', 200))
        mb.leaf(0.08, 0.06, 0.01, G, segs=5, serrate=0.4)                                  # tail fin
        mb.at(T(0, -0.178, 0.035) @ R('X', -8))
        mb.lathe([(0, 0), (0.024, 0.01), (0.033, 0.045), (0.027, 0.085), (0.03, 0.115), (0.02, 0.135), (0.009, 0.142),
                  (0.009, 0.152), (0, 0.152)], G, segs=10, ell=(1, 0.8))                   # torso
        mb.at(T(0, -0.20, 0.205))
        mb.lathe([(0, -0.02), (0.014, -0.014), (0.019, 0.0), (0.014, 0.015), (0, 0.021)], G, segs=10)   # head
        for sx in (-1, 1):
            mb.at(T(sx * 0.02, -0.17, 0.15) @ R('Z', sx * -35) @ R('X', 75) @ R('Z', sx * -28))
            mb.leaf(0.15, 0.07, 0.008, G, segs=6, serrate=0.45, curl=0.5)                  # wings
            mb.at()
            mb.tube([(sx * 0.028, -0.185, 0.165), (sx * 0.035, -0.215, 0.20), (sx * 0.012, -0.235, 0.228)], 0.007, G, n=6)   # arms
        mb.at(T(0, -0.235, 0.18))
        mb.lathe([(0, 0), (0.008, 0.004), (0.011, 0.04), (0.02, 0.055), (0.022, 0.064), (0.012, 0.066), (0.012, 0.085), (0, 0.085)],
                 G, segs=10)                                                               # torch and candle socket
        mb.at()

    b = pc.add('', body)
    shade = P.lampshade(0.07, 0.17, 0.15, 'scalloped', '#F2C58E', lit=True, name='blue_bedroom.wall_light.shade')
    s = pc.add('shade', shade, L=T(0, -0.235, 0.24))
    IX.tag_many([b, s], 'lamp', g='blue_bedroom.wall_light', label='Wall light')      # own circuit: S1 north rocker
    lighting.bulb(ctx, ROOM, pc.pt((0, -0.235, 0.31)), watts=W_SCONCE, kelvin=2800, radius=0.03, name='blue_bedroom.wall_light.bulb')


def bedside_lamp(ctx, pc, i, x, y):
    """D1: gilt figural lamp 0.55 high on a nightstand: scrolled rococo base, winged cherub holding up a torch that
    ends in a frosted-glass flower shade. Each on its own in-line switch."""
    G, glass = gilt(), P.two_sided(P.emissive('#F2BC80', 2.0))

    def body(mb):
        mb.lathe([(0, 0), (0.08, 0), (0.08, 0.01), (0.062, 0.022), (0.05, 0.045), (0.028, 0.06), (0.02, 0.085), (0.026, 0.095),
                  (0.014, 0.105), (0, 0.105)], G, segs=16)
        for k in range(3):                                                                 # scroll feet
            mb.at(R('Z', 120 * k + 30) @ T(0, 0.07, 0.0) @ R('X', 55))
            mb.leaf(0.05, 0.035, 0.008, G, segs=4, curl=0.8)
        mb.at()
        for sx in (-1, 1):                                                                 # legs, wings
            mb.tube([(sx * 0.008, 0, 0.10), (sx * 0.014, -0.004, 0.17), (sx * 0.012, 0, 0.235)], 0.009, G, n=6)
            mb.at(T(sx * 0.012, 0.016, 0.30) @ R('Z', sx * -40) @ R('X', 100) @ R('Z', sx * -30))
            mb.leaf(0.11, 0.05, 0.006, G, segs=5, serrate=0.4, curl=0.4)
            mb.at()                                                                        # next leg in lamp coords
        mb.at(T(0, 0, 0.225))
        mb.lathe([(0, 0), (0.018, 0.008), (0.024, 0.04), (0.02, 0.075), (0.024, 0.10), (0.015, 0.118), (0.007, 0.124), (0, 0.124)],
                 G, segs=10, ell=(1, 0.8))                                                 # torso
        mb.at(T(0, -0.004, 0.368))
        mb.lathe([(0, -0.02), (0.014, -0.014), (0.018, 0.0), (0.014, 0.014), (0, 0.02)], G, segs=10)   # head
        mb.at()
        mb.tube([(0.02, 0, 0.325), (0.04, -0.01, 0.365), (0.045, -0.012, 0.41)], 0.006, G, n=6)        # raised arm
        mb.tube([(-0.02, 0, 0.325), (-0.035, -0.012, 0.29), (-0.03, -0.02, 0.26)], 0.006, G, n=6)
        mb.at(T(0.045, -0.012, 0.39))
        mb.lathe([(0, 0), (0.005, 0.002), (0.006, 0.05), (0.014, 0.062), (0.016, 0.07), (0, 0.07)], G, segs=8)   # torch
        mb.lathe([(0.012, 0.068), (0.03, 0.078), (0.044, 0.105), (0.05, 0.14), (0.046, 0.16)], glass, segs=10)   # flower shade
        for k in range(5):                                                                 # petal tips
            mb.at(T(0.045, -0.012, 0.39) @ R('Z', 72 * k) @ T(0, 0.046, 0.15) @ R('X', 72))
            mb.leaf(0.03, 0.04, 0.003, glass, segs=3)
        mb.at()

    ob = pc.add(f'lamp', body, kind='light', L=T(x, y, 0.60) @ R('Z', -25 if i else 25), key='lamp')
    IX.tag(ob, 'lamp', g=f'blue_bedroom.bedside_lamp.{i}', label='Bedside lamp')
    top = pc.M @ T(x, y, 0.60) @ R('Z', -25 if i else 25) @ Vector((0.045, -0.012, 0.585))
    glow = lighting.bulb(ctx, ROOM, top, watts=W_LAMP, kelvin=2700, radius=0.02, name=f'blue_bedroom.bedside_lamp.{i}.bulb')
    glow.visible_camera = glow.visible_glossy = False


def downlights(ctx):
    """L2: six white-bezel LED downlights, two rows of three (four are seen in the footage)."""
    cz, i = ctx.ceil_z(ROOM), 0
    for x in (0.10, 2.40):
        for y in (13.55, 14.90, 16.25):
            lighting.downlight(ctx, ROOM, x, y, watts=W_DOWN, kelvin=3000, name=f'blue_bedroom.downlight.{i}')
            _add(ctx, P.place(P.downlight(name=f'blue_bedroom.downlight_trim.{i}'), (x, y, cz)), 'light')
            i += 1


# ------------------------------------------------------------------------------------------ build
def _keys(ctx):
    """Re-key the fittings to the openings and walls they belong to, so a later spec move carries them along."""
    global XR, AXIS, PEL, ENS, CAB
    XR = max(x for x, y in ctx.room_poly(ROOM) if y < Y0 - 0.01)
    AXIS = ctx.openings['d_balcony']['center'][0]
    PEL = (AC[1] + 0.03, AC[1] + 0.03 + PEL_LEN)           # 0.20..2.40: the measured length, not centred on AXIS
    e = ctx.openings['d_ensuite']
    ENS = e['center'][0] - e['width'] / 2
    CAB = XR + 0.025 + 0.297


def build(ctx):
    _keys(ctx)
    shell.repaint(ROOM, '#2B3B4C', '#2A3552')                 # the navy wall rendered teal under the 3000 K view
    F.wardrobe(ctx)
    F.bed(ctx)
    ns = [F.nightstand(ctx, i, y) for i, y in enumerate((14.406, 16.32))]   # 14.211..14.601 against the wardrobe, 16.125..16.515
    bur = F.bureau(ctx)
    F.stool(ctx)
    F.tv_cabinet(ctx, CAB)

    radiator(ctx)
    television(ctx)
    wall_fittings(ctx)
    electrics(ctx)
    pelmet(ctx)
    curtains(ctx)
    art(ctx)
    octagon_mirror(ctx)
    bureau_ornaments(ctx, bur)
    alarm_clock(ctx, ns[1])

    rose(ctx)
    chandelier(ctx)
    wall_light(ctx)
    bedside_lamp(ctx, ns[0], 0, 0.0, -0.17)
    bedside_lamp(ctx, ns[1], 1, -0.075, -0.15)
    downlights(ctx)

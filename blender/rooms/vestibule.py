"""Vestibule / porch furnishing (spec/rooms/vestibule.md, spec/phase3/briefs/hall.md, spec/phase3/porch.md 2.3):
alarm keypad + switch, box stool, door mat, honey shoe rack, brass hall-lantern chandelier, the two downlights in the
sloping ceiling panel of the front recess and the three downlights in the raked canopy soffit (the canopy itself is
lib/envelope). The cheek-wall dado / skirting stop with returned ends against joinery's corner cover board in
lib/mouldings (TRIM['vestibule']).

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --levels G --only shell,vestibule,hallway --preview vestibule,hallway --res 540x960 --samples 64 --tag hall
    canopy lights (needs the envelope): --levels G,X --only shell,envelope,vestibule --preview vestibule --cam canopy
"""
import os
from math import atan, cos, sin, pi, tau, radians

from mathutils import Matrix, Vector

from lib import envelope, interact as IX, lighting, materials as M, mouldings as mo, props as P, shell

ROOM = 'vestibule'
ART = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'textures', 'art', ROOM)

CAMERAS = [
    dict(name='street', pos=(0.2, 1.80, 1.6), look=(0.0, 0.0, 1.3), fov_deg=100, ref='f_0012'),
    dict(name='window', pos=(-0.25, 1.05, 1.6), look=(0.75, 0.63, 1.9), fov_deg=100, ref='v9:f_0024'),
    dict(name='vault', pos=(0.0, 0.45, 1.5), look=(0.0, 1.6, 2.4), fov_deg=100, ref='v9:f_0030'),
    dict(name='floor', pos=(-0.3, 0.5, 1.6), look=(0.0, 1.15, 0.0), fov_deg=100, ref='f_0026'),
    dict(name='keypad', pos=(-0.1, 1.30, 1.45), look=(0.65, 1.64, 1.28), fov_deg=100, ref='f_0033'),
    dict(name='inner', pos=(0.0, 3.33, 1.75), look=(0.0, 1.96, 1.7), fov_deg=100, ref='f_0057'),
    dict(name='stool', pos=(-0.45, 1.05, 1.25), look=(0.2, 1.64, 0.3), fov_deg=75),     # drawers (--pose 1: out)
    dict(name='corner', pos=(0.0, 0.85, 1.35), look=(0.75, 0.0, 0.85), fov_deg=90, ref='photo, v9:f_0036'),
    dict(name='slope', pos=(0.1, 0.85, 1.2), look=(0.1, 0.0, 2.7), fov_deg=100, ref='v9:f_0027'),     # sloping ceiling
    dict(name='stop', pos=(0.40, 0.40, 1.05), look=(0.75, 0.02, 0.85), fov_deg=60, ref='v9:f_0036'),  # dado return
    dict(name='canopy', pos=(0.1, -1.6, 1.5), look=(0.0, -0.3, 2.45), fov_deg=90, ref='v8:f_0118'),   # outside
]

PORCH = ['vestibule', 'front']                  # porch circuit: the canopy lights light the forecourt (front atlas)
CANOPY_X = (-0.42, 0.0, 0.42)                   # porch-10: three downlights in a row in the raked soffit
CANOPY_OUT = 0.22                               # out from the outer face of the front wall (y -0.34)
SWITCH_YZ = (1.65, 1.22)                        # measured v2 k902.4 / k903.2 / v1 f_0033 (see build)
KEYPAD_YZ = (1.615, 1.375)                      # north edge flush with the plate's

RX = Matrix.Rotation(pi / 2, 4, 'X')            # local +Z -> -Y: lathes that face out of a wall


def T(x=0.0, y=0.0, z=0.0):
    return Matrix.Translation((x, y, z))


def loop(mb, pts, r, mat, up, n=5):
    """Closed round-bar loop lying in the plane whose normal is `up` (mb.tube picks a fixed up vector that
    degenerates where a vertical loop runs parallel to it)."""
    prof = [(r * cos(tau * i / n), r * sin(tau * i / n)) for i in range(n)]
    mb.sweep(prof + prof[:1], pts, mat, closed=True, up=up)


def keypad(name):
    """Alarm keypad 160 x 110 x 22 (porch survey: 1.85 x the 86 mm switch plate, v2 t903.2), blank: no logo or
    printing. 3 x 4 key grid on the left, round dial ring with a centre button on the right, three small mode
    buttons over the dial and a round status button at the top right. Wall prop: back on y = 0, front -Y."""
    mb = mo.MB()
    mb.box((-.08, -.022, -.055), (.08, 0, .055), 'plastic_white', bev=.006)
    grey = M.solid('keypad_key', '#DADAD6', 0.5)
    line = M.solid('keypad_line', '#C9C9C4', 0.6)
    for i in range(3):
        for j in range(4):
            mb.at(T(-.058 + .019 * i, -.022, .030 - .019 * j) @ RX)
            mb.lathe([(0, 0), (.0062, 0), (.0056, .002), (0, .0023)], grey, 10)
    mb.at()
    for i in range(1, 3):                                                                    # printed key grid
        mb.box((-.0675 + .019 * i - .0003, -.0222, -.043), (-.0675 + .019 * i + .0003, -.0219, .040), line)
    mb.box((-.0295, -.0222, -.043), (-.0289, -.0219, .040), line)
    mb.at(T(.038, -.022, -.006) @ RX)
    mb.lathe([(.014, 0), (.029, 0), (.028, .003), (.015, .003), (.014, 0)], grey, 20)       # dial ring
    mb.lathe([(0, 0), (.012, 0), (.011, .0025), (0, .003)], 'plastic_white', 16)             # centre button
    for k, x in enumerate((.022, .038, .054)):                                               # mode buttons
        mb.at(T(x, -.022, .033) @ RX)
        mb.lathe([(0, 0), (.003, 0), (.0028, .0012), (0, .0014)], M.solid('keypad_blue', '#4C78B4', 0.4) if k == 1
                 else grey, 8)
    mb.at(T(.068, -.022, .040) @ RX)
    mb.lathe([(0, 0), (.0042, 0), (.004, .0015), (0, .0018)], M.solid('keypad_status', '#9A9C9E', 0.4), 10)
    mb.at()
    return mb.finish(name)


def stool(name):
    """Mahogany box stool 0.42 (X) x 0.36 (Y) x 0.50, drawers on the -X face, velvet lid. Origin floor centre.
    The two drawers are their own children `<name>.drawer.<k>` (front + oak box) with their pulls
    `<name>.drawer.<k>.pull`; build() tags them. [H]"""
    wood = 'mahogany_dark'
    mb = mo.MB()
    # case 0.414 x 0.354 x 0.18, hollow behind the drawers. Outside it is the plain box it always was: every
    # joint between these boards is under a leg block or behind a drawer front
    for sy in (-1, 1):
        mb.box((-.207, sy * .140, .26), (.195, sy * .177, .44), wood, bev=.002, grain=0)      # sides
    mb.box((.195, -.177, .26), (.207, .177, .44), wood, bev=.002, grain=0)                    # back
    for z0, z1 in ((.26, .272), (.339, .359), (.426, .44)):                                   # bottom, dust board, top
        mb.box((-.207, -.140, z0), (.195, .140, z1), wood, bev=.002, grain=0)
    mb.box((-.214, -.184, .437), (.214, .184, .446), wood, bev=.002, grain=0)                # lid board
    root = mb.finish(name)
    for k, z0 in enumerate((.268, .355)):                                                     # two drawers
        d = mo.MB()
        d.box((-.214, -.150, z0), (-.205, .150, z0 + .075), wood, bev=.003, grain=1)          # front
        for sy in (-1, 1):
            d.box((-.205, sy * .127, z0 + .006), (.185, sy * .135, z0 + .066), 'oak_light', grain=0)
        d.box((.177, -.127, z0 + .006), (.185, .127, z0 + .066), 'oak_light', grain=1)        # back
        d.box((-.205, -.127, z0 + .006), (.177, .127, z0 + .012), 'oak_light', grain=0)       # bottom
        d.finish(f'{name}.drawer.{k}').parent = root
    for sx in (-1, 1):
        for sy in (-1, 1):
            leg = P.turned_leg(.44, .035, 'taper', top_block=.185, mat=wood, taper=.63, name=f'{name}.leg')
            leg.parent = root
            leg.location = (sx * .1925, sy * .1625, 0)
    # champagne crushed velvet (F_0028: mottled pile, strong sheen, puffy pad). ponytail: generated mottle
    # (reference/work/hall/r2/gen_tex.py) on the library velvet's sheen settings; swap for a library
    # 'velvet_champagne_crushed' if materials adds one
    velvet = M.image_mat('vestibule_velvet_crushed', os.path.join(ART, 'stool_velvet.jpg'), size_m=(.3, .3),
                         roughness=0.6)
    sheen = next(n for n in velvet.node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs
    sheen['Sheen Weight'].default_value, sheen['Sheen Roughness'].default_value = 1.0, 0.35
    seat = P.upholstered_seat(.43, .37, .030, mat=velvet, crown=.028, name=f'{name}.lid')   # top at z 0.504
    seat.parent = root
    seat.location = (0, 0, .446)
    for k, z in enumerate((.3055, .3925)):
        for y in (-.075, .075):
            h = P.handle_drop(.05, .022, 'bronze', name=f'{name}.drawer.{k}.pull')
            h.parent = root
            P.place(h, (-.214, y, z + .008), facing=(-1, 0))
    return root


def lantern(name):
    """Brass hall lantern: ceiling cup, chain, hexagonal glazed cage with urn finials, three candles inside,
    six S-scroll candle arms from the base, pendant finial. Origin ceiling contact; lowest point -0.69. [H]"""
    B = 'brass'
    mb = mo.MB()
    mb.lathe([(0, -.046), (.011, -.046), (.014, -.038), (.03, -.03), (.05, -.02), (.058, -.01), (.06, -.003),
              (.06, 0), (0, 0)], B, 20)
    mb.tube([(.055 * cos(tau * i / 20), .055 * sin(tau * i / 20), -.012) for i in range(20)], .0045, B, 6, closed=True)
    a, b = .028, .011                                    # chain: three oval links, alternate planes
    for k in range(3):
        zc = -.046 - a + .006 - k * (2 * a - .012)
        pts = [(b * cos(tau * i / 12), 0, zc + a * sin(tau * i / 12)) for i in range(12)]
        if k % 2:
            pts = [(0, x, z) for x, _, z in pts]
        loop(mb, pts, .003, B, (1, 0, 0) if k % 2 else (0, 1, 0))
    zr = -.046 - 3 * (2 * a - .012) - .014               # big ring the lantern hangs from
    loop(mb, [(.02 * cos(tau * i / 14), 0, zr + .02 * sin(tau * i / 14)) for i in range(14)], .0035, B, (0, 1, 0))
    zt, zb, R = -.275, -.630, .10                        # cage top / bottom, corner radius
    zk = zr - .028                                       # crown boss
    mb.at(T(0, 0, zk))
    mb.lathe([(0, -.014), (.008, -.012), (.014, -.004), (.010, .004), (.005, .010), (0, .012)], B, 10)
    mb.at()
    cor = [(R * cos(radians(30 + 60 * k)), R * sin(radians(30 + 60 * k))) for k in range(6)]
    for x, y in cor:
        mb.tube([(x, y, zt), (x, y, zb)], .0055, B, 6)                                         # glazing bars
        crown = [(x * t, y * t, zk - .006 + (zt - zk + .006) * t ** 2.2) for t in (.1, .3, .5, .7, .85, 1.0)]
        mb.tube(crown, .003, B, 5)                                                            # crown straps
        mb.at(T(x, y, zt))                                                                    # urn finials
        mb.lathe([(0, 0), (.006, 0), (.004, .006), (.009, .014), (.008, .022), (.003, .028), (.004, .033),
                  (0, .038)], B, 8)
        mb.at()
    for z in (zt, zb):
        mb.tube([(x, y, z) for x, y in cor], .007, B, 4, closed=True)
    brass2 = P.two_sided(P.mat(B))
    for k in range(6):                                   # six clear panes, each in a flat brass bevel border
        (x0, y0), (x1, y1) = cor[k], cor[(k + 1) % 6]
        out = (x0 + x1, y0 + y1, 0)
        mb.face([(x0, y0, zb), (x1, y1, zb), (x1, y1, zt), (x0, y0, zt)], 'glass_clear', hint=out)

        def pt(u, z, o=.0015 / (2 * R * cos(pi / 6))):   # on the pane, 1.5 mm outside the glass
            return (x0 + (x1 - x0) * u + out[0] * o, y0 + (y1 - y0) * u + out[1] * o, z)
        ro = [pt(0, zb), pt(1, zb), pt(1, zt), pt(0, zt)]
        ri = [pt(.13, zb + .013), pt(.87, zb + .013), pt(.87, zt - .013), pt(.13, zt - .013)]
        for j in range(4):
            mb.face([ro[j], ro[(j + 1) % 4], ri[(j + 1) % 4], ri[j]], brass2, hint=out)
    mb.at(T(0, 0, zb))                                   # base dish, candle plate, hub and pendant finial
    mb.lathe([(0, -.022), (.03, -.022), (.07, -.012), (.098, -.002), (.098, .004), (.07, -.004), (.03, -.012),
              (0, -.012)], B, 18)
    mb.lathe([(0, -.012), (.012, -.012), (.012, .012), (.05, .016), (.05, .02), (0, .02)], B, 14)
    mb.lathe([(0, -.062), (.004, -.058), (.010, -.048), (.006, -.040), (.016, -.030), (.02, -.022), (0, -.022)], B, 12)
    mb.at()
    root = mb.finish(name)
    lamps = []
    for k in range(3):
        c = P.candle_bulb(.10, name=f'{name}.candle')
        c.parent = root
        c.location = (.034 * cos(tau * k / 3), .034 * sin(tau * k / 3), zb + .02)
        lamps.append(c)
    for k in range(6):                                   # reach 0.205 + half a pan = 0.47 m across the arms
        arm = P.chandelier_arm(reach=.205, rise=.10, dip=.028, mat=B, pan_dia=.06, candle_h=.09, drops=0,
                               name=f'{name}.arm')
        arm.parent = root
        arm.location = (0, 0, zb - .014)
        arm.rotation_euler = (0, 0, tau * k / 6)
        lamps.append(arm)
    warm_flames(lamps)
    return root


def warm_flames(objs, hx='#FFB469', strength=6.0):
    """Give the flame tips of these props a 3000 K emission colour: the library flame (#FFD9A0) is cooler than
    the preview white point and renders blue-white. Works on one private copy per shared prop mesh."""
    warm, copies = P.emissive(hx, strength), {}
    for o in objs:
        if o.data.name not in copies:
            me = copies[o.data.name] = o.data.copy()
            for i, m in enumerate(me.materials):
                bsdf = m and m.node_tree and next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
                if bsdf and bsdf.inputs['Emission Strength'].default_value > 0:
                    me.materials[i] = warm
        o.data = copies[o.data.name]


def shoe_rack(name, L=.70, D=.27, H=.75, tiers=4):
    """Honey bamboo slatted shoe rack (porch survey 2.3.10, v9 f_0042, photo): two ladder ends of square posts
    joined by a side rail at each tier, three flat slats per tier running the length. Empty: shoes are clutter.
    Local frame: length along X, depth along Y (back on y = 0, front -Y), origin floor centre of the back."""
    wood = M.solid('vestibule_bamboo', '#CDAE6E', 0.45)  # honey: #C49A55 rendered orange under 3000 K
    mb = mo.MB()
    p, s = .024, .018                                       # post section, rail / slat thickness
    zs = [.07 + (H - .07 - s) * k / (tiers - 1) for k in range(tiers)]
    for x in (-L / 2, L / 2 - p):
        for y in (-D, -p):
            mb.box((x, y, 0), (x + p, y + p, H), wood, bev=.002, grain=2)              # posts
        for z in zs:
            mb.box((x + .002, -D + p, z - .004), (x + p - .002, -p, z + s - .004), wood, bev=.0015, grain=1)
    w = (D - 2 * p - .012) / 3                              # slat pitch across the depth
    for z in zs:
        for k in range(3):                                  # slats with 18 mm gaps, resting on the end rails
            y0 = -D + p + .006 + k * w
            mb.box((-L / 2 + p, y0, z + s - .004), (L / 2 - p, y0 + w - .018, z + s + .008), wood, bev=.0015, grain=0)
    return mb.finish(name)


def slope_downlight(ctx, name, x, y, z, slope, watts, trim_name, room=ROOM, **trim):
    """Recessed downlight flush in a ceiling that rises `slope` (dz/dy) toward +Y: the trim tilts with the plane,
    the emitter hangs 30 mm under it and shines straight down (gimbal lamp)."""
    lighting.downlight(ctx, room, x, y, z=z - 0.03, watts=watts, kelvin=3000, spot_deg=130, name=name)
    tr = P.place(P.downlight(name=trim_name, **trim), (x, y, z))
    tr.rotation_euler = (atan(slope), 0, 0)
    return ctx.add(tr, room, 'light')


def build(ctx):
    cz = ctx.ceil_z(ROOM)

    # --- east wall of the rear recess: alarm keypad over the light switch, mid-wall (v2 k902.4, k903.2, v1 f_0033).
    #     On the 86 mm plate scale, corrected for the oblique wall: switch centre 0.21-0.23 north of the pier's north
    #     face (1.44) and about 0.20 south of the inner frame face (1.86) -> y 1.65 (round-2 offset +0.13); keypad
    #     bottom 55 mm over the plate top (z 1.375, not the 1.48 of round 1), its north edge flush with the plate's
    (sy, sz), (ky, kz) = SWITCH_YZ, KEYPAD_YZ
    kp = P.place(keypad('vestibule.keypad'), (0.65, ky, kz), facing=(-1, 0))
    ctx.add(kp, ROOM, 'fit', lm='dynamic')
    sw = P.place(P.switch_plate(1, name='vestibule.switch'), (0.65, sy, sz), facing=(-1, 0))
    IX.tag(sw, 'light', rooms=PORCH, label='Porch light')                # 2-way with the hall plate (v2:f_0903-0906)
    ctx.add(sw, ROOM, 'fit', lm='dynamic')

    # --- box stool in the corner of the east wall and the inner screen (drawers face west): 0.22 south of the screen
    #     as before, clear of the east pier (y <= 1.44) by 15 mm
    fi = ctx.opening_frame('d_inner')
    y_screen = fi['center'].y - fi['wall_thickness'] / 2                 # vestibule face of the screen (1.86)
    st = stool('vestibule.stool')
    st.location = (0.41, y_screen - 0.22, 0)
    ctx.add(st, ROOM, 'furn', plan_sym='stool')
    out = st.matrix_basis.to_3x3() @ Vector((-.28, 0, 0))                # drawers pull out 0.28 of their 0.39
    for k in range(2):
        IX.tag_many([o for o in P.family(st) if o.name.startswith(f'vestibule.stool.drawer.{k}')], 'slide',
                    g=f'vestibule.stool.drawer.{k}', label='Drawer', d=out)

    # --- flat-woven door mat 0.60 x 1.10 (porch survey 2.3.9): x -0.44..0.16, from 0.04 behind the threshold to the
    #     third pattern row beside the pier. ponytail: pattern drawn (build/rooms3/hall/rug.py, after
    #     reference/work/hall/r2/rug.py) with the layout, band widths and colours measured on F_0028 and v9 f_0021
    rug = P.rug(os.path.join(ART, 'vestibule_rug.jpg'), w=0.60, d=1.10, thickness=.006, corner_r=.03,
                name='vestibule.rug')
    rug.location = (-0.14, 0.59, 0)
    ctx.add(rug, ROOM, 'decor', plan_sym='rug')

    # --- empty shoe rack against the cheek wall under the lower light (x 0.45..0.72, y 0.05..0.75)
    ctx.add(P.place(shoe_rack('vestibule.shoe_rack'), (0.72, 0.40, 0), facing=(-1, 0)), ROOM, 'furn', plan_sym='rack')

    # --- brass lantern chandelier in the middle of the flat ceiling of the rear recess (y 1.44..1.86), clear of the
    #     vault end face (9 lamps, 2700 K)
    y_pier = max(p[1] for p in ctx.feature('vest_pier_e')['polygon'])
    ch = lantern('vestibule.lantern')
    ch.location = (0.0, (y_pier + y_screen) / 2 - 0.01, cz)            # 10 mm south: arm pans clear the screen
    ctx.add(ch, ROOM, 'light')
    IX.tag_many(P.family(ch), 'lamp', g='vestibule.lantern', label='Lantern', rooms=PORCH)
    for i, p in enumerate(P.bulb_points(ch)):
        lighting.bulb(ctx, ROOM, p, watts=10.5, kelvin=2800, radius=.012, name=f'vestibule.lantern.bulb.{i}')

    # --- two downlights side by side in the sloping ceiling panel (porch survey 2.3.5, v9 t31.5): ctx.ceil_z does not
    #     know the ceiling_haunch, so the plane comes from the feature (2.62 at y 0 -> 2.85 at y 0.62)
    hf = ctx.feature('vest_ceiling_slope')
    y0, y1 = min(p[1] for p in hf['polygon']), max(p[1] for p in hf['polygon'])
    z0, k = hf['z'][0], (hf['z'][1] - hf['z'][0]) / (y1 - y0)
    for i, (x, y) in enumerate(((-0.30, 0.30), (0.32, 0.30))):
        slope_downlight(ctx, f'vestibule.downlight.{i}', x, y, z0 + k * (y - y0), k, 32,
                        f'vestibule.downlight_trim.{i}')

    # (the cheek-wall dado / skirting stop 2 mm clear of the corner cover board with returned ends: lib/mouldings TRIM)

    # --- the three outside lights: downlights in the raked canopy soffit (envelope.porch_soffit_z), same circuit as
    #     the lantern (seen as soft discs through the frosted transom)
    f = ctx.opening_frame('d_street')
    y = f['center'].y - f['wall_thickness'] / 2 - CANOPY_OUT
    rake = (envelope.porch_soffit_z(y + 0.1) - envelope.porch_soffit_z(y)) / 0.1
    for i, x in enumerate(CANOPY_X):
        slope_downlight(ctx, f'vestibule.outside.{i}', x, y, envelope.porch_soffit_z(y), rake, 40,
                        f'vestibule.outside_trim.{i}', dia=.09, lamp_dia=.055, strength=30.0)

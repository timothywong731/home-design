"""Vestibule / porch furnishing (spec/rooms/vestibule.md): alarm keypad + switch, box stool, door rug,
brass hall-lantern chandelier, recess-B downlight and the street canopy with the three outside lights.

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --only shell,vestibule,hallway --preview vestibule,hallway --res 540x960 --samples 64 --tag hall
"""
import os
from math import cos, sin, pi, tau, radians

import bpy
from mathutils import Matrix, Vector

from lib import interact as IX, lighting, materials as M, mouldings as mo, props as P

ROOM = 'vestibule'
ART = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'textures', 'art', ROOM)

CAMERAS = [
    dict(name='street', pos=(0.2, 1.7, 1.6), look=(0.0, 0.0, 1.3), fov_deg=100, ref='f_0012'),
    dict(name='window', pos=(-0.2, 0.9, 1.6), look=(0.9, 0.45, 2.0), fov_deg=100, ref='f_0019'),
    dict(name='vault', pos=(0.0, 0.3, 1.5), look=(0.0, 1.3, 2.2), fov_deg=100, ref='f_0022'),
    dict(name='floor', pos=(-0.3, 0.45, 1.6), look=(0.0, 1.0, 0.0), fov_deg=100, ref='f_0026'),
    dict(name='keypad', pos=(-0.1, 1.15, 1.5), look=(0.65, 1.5, 1.15), fov_deg=100, ref='f_0033'),
    dict(name='inner', pos=(0.0, 3.33, 1.75), look=(0.0, 1.83, 1.7), fov_deg=100, ref='f_0057'),
    dict(name='stool', pos=(-0.45, 0.95, 1.25), look=(0.15, 1.5, 0.3), fov_deg=75),     # drawers (--pose 1: out)
]

RX = Matrix.Rotation(pi / 2, 4, 'X')            # local +Z -> -Y: lathes that face out of a wall


def T(x=0.0, y=0.0, z=0.0):
    return Matrix.Translation((x, y, z))


def loop(mb, pts, r, mat, up, n=5):
    """Closed round-bar loop lying in the plane whose normal is `up` (mb.tube picks a fixed up vector that
    degenerates where a vertical loop runs parallel to it)."""
    prof = [(r * cos(tau * i / n), r * sin(tau * i / n)) for i in range(n)]
    mb.sweep(prof + prof[:1], pts, mat, closed=True, up=up)


def keypad(name):
    """Alarm keypad 150 x 100 x 22 (no branding). Wall prop: back on y = 0, front -Y."""
    mb = mo.MB()
    mb.box((-.075, -.022, -.05), (.075, 0, .05), 'plastic_white', bev=.004)
    grey = M.solid('keypad_key', '#DADAD6', 0.5)
    for i in range(3):
        for j in range(4):
            mb.at(T(-.056 + .018 * i, -.022, .027 - .018 * j) @ RX)
            mb.lathe([(0, 0), (.0058, 0), (.0052, .002), (0, .0022)], grey, 10)
    mb.at(T(.036, -.022, -.002) @ RX)
    mb.lathe([(.013, 0), (.027, 0), (.026, .003), (.014, .003), (.013, 0)], grey, 20)       # dial ring
    mb.lathe([(0, 0), (.011, 0), (.010, .0025), (0, .003)], 'plastic_white', 16)             # centre button
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


def build(ctx):
    cz = ctx.ceil_z(ROOM)

    # --- east wall of recess A: alarm keypad with the light switch below it (f_0033)
    kp = P.place(keypad('vestibule.keypad'), (0.65, 1.52, 1.48), facing=(-1, 0))
    ctx.add(kp, ROOM, 'fit', lm='dynamic')
    sw = P.place(P.switch_plate(1, name='vestibule.switch'), (0.65, 1.52, 1.22), facing=(-1, 0))
    IX.tag(sw, 'light', rooms=['vestibule'])
    ctx.add(sw, ROOM, 'fit', lm='dynamic')

    # --- box stool in the corner of the east wall and the inner screen (drawers face west)
    st = stool('vestibule.stool')
    st.location = (0.41, 1.51, 0)
    ctx.add(st, ROOM, 'furn', plan_sym='stool')
    out = st.matrix_basis.to_3x3() @ Vector((-.28, 0, 0))                # drawers pull out 0.28 of their 0.39
    for k in range(2):
        IX.tag_many([o for o in P.family(st) if o.name.startswith(f'vestibule.stool.drawer.{k}')], 'slide',
                    g=f'vestibule.stool.drawer.{k}', label='Drawer', d=out)

    # --- flat-woven door rug
    # ponytail: pattern drawn (reference/work/hall/r2/rug.py) with the layout, band widths and colours
    # measured on the rectified still F_0028, not a crop - half of the real rug is under bags, shoes and feet
    # in every view; swap the JPG if a clean photo turns up
    rug = P.rug(os.path.join(ART, 'vestibule_rug.jpg'), w=0.62, d=0.98, thickness=.006, corner_r=.03,
                name='vestibule.rug')
    rug.location = (-0.12, 0.57, 0)
    ctx.add(rug, ROOM, 'decor', plan_sym='rug')

    # --- brass lantern chandelier, recess A (9 lamps, 2700 K)
    ch = lantern('vestibule.lantern')
    ch.location = (0.0, 1.48, cz)
    ctx.add(ch, ROOM, 'light')
    IX.tag_many(P.family(ch), 'lamp', g='vestibule.lantern', label='Lantern', rooms=['vestibule'])
    for i, p in enumerate(P.bulb_points(ch)):
        lighting.bulb(ctx, ROOM, p, watts=10.5, kelvin=2800, radius=.012, name=f'vestibule.lantern.bulb.{i}')

    # --- recessed downlight, recess B
    lighting.downlight(ctx, ROOM, 0.20, 0.35, watts=60, kelvin=3000, spot_deg=130, name='vestibule.downlight')
    ctx.add(P.place(P.downlight(name='vestibule.downlight_trim'), (0.20, 0.35, cz)), ROOM, 'light')

    # --- street canopy with the three outside lights (seen as soft discs through the frosted transom)
    f = ctx.opening_frame('d_street')
    y_out = f['center'].y - f['wall_thickness'] / 2
    mb = mo.MB()
    mb.box((-0.80, y_out - 0.80, 2.65), (0.80, y_out, 2.69), 'upvc_white')                    # boarded soffit
    mb.box((-0.82, y_out - 0.82, 2.64), (0.82, y_out - 0.80, 2.82), 'upvc_white', bev=.004)   # fascia
    for sx in (-1, 1):
        mb.box((sx * 0.82, y_out - 0.82, 2.64), (sx * 0.80, y_out, 2.82), 'upvc_white', bev=.004)
    mb.box((-0.82, y_out - 0.82, 2.82), (0.82, y_out, 2.84), M.solid('canopy_lead', '#5A5D60', 0.6))
    for k in range(1, 8):                                                                     # board joints
        mb.box((-0.80, y_out - 0.1 * k - .002, 2.649), (0.80, y_out - 0.1 * k + .002, 2.651),
               M.solid('canopy_joint', '#C9C9C4', 0.6))
    can = mb.finish('vestibule.canopy')
    ctx.add(can, ROOM, 'fit')
    for i, x in enumerate((-0.38, 0.0, 0.38)):
        lighting.downlight(ctx, ROOM, x, y_out - 0.40, z=2.63, watts=40, kelvin=3000, name=f'vestibule.outside.{i}')
        ctx.add(P.place(P.downlight(dia=.105, lamp_dia=.065, strength=30.0, name=f'vestibule.outside_trim.{i}'),
                        (x, y_out - 0.40, 2.649)), ROOM, 'light')

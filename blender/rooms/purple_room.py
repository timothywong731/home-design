"""purple_room - the Lavender Room, the unused lilac room on the second floor (spec/rooms/purple_room.md; footage
v4 f_0388-f_0440, v13 f_0011-f_0049; round-3 brief spec/phase3/briefs/purple_room.md).

The owner calls it unfurnished: what is here is fixed - eight-section column radiator, split air-conditioning unit
with its remote, oak window board, trickle vent, the floral eyelet curtains on a mid-brown wooden pole, sockets, the
dimmer and its four downlights - plus the one real piece of furniture that stands in it, a Chippendale side chair.
Everything is laid out from the room polygon and the two openings of house.json (round 3: the room moved to
x 0.42..3.10, y 9.55..11.50); offsets below are the surveyed ones (floor2_a, v13 f19-f27, v4 t389).

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --levels 2 --only shell,purple_room --preview purple_room \
        --res 540x960 --samples 64 --tag purple_room            (open state: --pose 1 --tag purple_room1)
"""
import bmesh
import bpy
from math import atan2, cos, radians, sin, tau
from mathutils import Matrix, Vector

from lib import interact as IX, lighting, materials as M, mouldings as mo, props as P, shell

ROOM = 'purple_room'

CAMERAS = [
    dict(name='door', pos=(0.55, 11.10, 7.52), look=(3.10, 10.47, 7.25), fov_deg=100, ref='v4:f_0390 (hr_v4_389)'),
    dict(name='window', pos=(1.45, 10.55, 7.50), look=(3.10, 10.47, 7.70), fov_deg=100, ref='v13:f_0020 (hr_v13_019)'),
    dict(name='west', pos=(2.55, 10.05, 7.52), look=(0.42, 10.70, 7.30), fov_deg=100, ref='v13:f_0043, v4:f_0394'),
    dict(name='south', pos=(1.95, 11.35, 7.40), look=(2.05, 9.55, 7.40), fov_deg=100, ref='v4:f_0400 (hr_v4_399)'),
    dict(name='north', pos=(1.60, 9.80, 7.45), look=(1.90, 11.50, 6.90), fov_deg=100, ref='v4:f_0436'),
    dict(name='sill', pos=(2.55, 10.47, 7.62), look=(3.35, 10.47, 7.00), fov_deg=100, ref='v13:f_0025'),
    dict(name='head', pos=(2.70, 10.62, 7.45), look=(3.20, 10.30, 8.32), fov_deg=100, ref='v4:f_0408'),
    dict(name='ceiling', pos=(2.70, 11.30, 6.60), look=(1.40, 9.95, 8.62), fov_deg=100, ref='v4:f_0402 (hr_v4_401)'),
]

Tr = Matrix.Translation


def _sm(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


def _radiator(name, n=8, pitch=0.069, h=0.51, w=0.068, d=0.10, standoff=0.03):
    """White sectional column radiator: eight wide round-topped sections at 69 mm pitch, 0.55 wide x 0.10 (hr_v13_021
    shows all eight; floor2_a counted seven where the carpet cleaner hides the north one in v4 t389 / v13 t19; the
    body is 0.64-0.66 of the 0.85 board in v4 t389, v13 t19 and t20):
    each section a flat oval column with domed heads top and bottom that touch the next section (w = head width,
    waist 0.84 w: the dark slots between them stop short of the ends, hr_v4_389); a chrome angle valve with a tail to
    the floor at each end, the manual head at the south end (local +X). Origin: wall plane, bottom centre of the body;
    front -Y."""
    mb, m, yc = mo.MB(), 'white_gloss', -(standoff + d / 2)
    ends = [(0, 0), (.6, .006), (.88, .02), (1.0, .04), (.98, .06), (.84, .085)]
    prof = ends + [(r, h - z) for r, z in reversed(ends)]
    half = (n - 1) * pitch / 2
    for i in range(n):
        mb.at(Tr((-half + i * pitch, yc, 0)))
        mb.lathe(prof, m, 12, ell=(w / 2, d / 2))
    mb.at()
    xe = half + w / 2 + 0.024
    for s in (-1, 1):
        mb.tube([(s * (half + w / 2 - 0.006), yc, 0.04), (s * xe, yc, 0.04)], 0.0095, 'chrome', 8)    # tail
        mb.tube([(s * xe, yc, -0.02), (s * xe, yc, 0.055)], 0.0115, 'chrome', 10)                     # valve body
        mb.tube([(s * xe, yc, -0.172), (s * xe, yc, -0.02)], 0.0075, 'chrome', 8)                     # pipe to the floor
    mb.at(Tr((xe, yc, 0.055)))
    mb.lathe([(0, 0), (.014, 0), (.015, .006), (.013, .022), (.009, .026), (0, .027)], 'chrome', 12)   # manual head
    mb.at(Tr((-xe, yc, 0.055)))
    mb.lathe([(0, 0), (.0115, 0), (.0115, .012), (0, .013)], 'plastic_white', 10)                      # lockshield cap
    return mb.finish(name)


def _window_board(name, length, depth, t=0.03, r=0.015):
    """Oak window board with a bullnose: swept along +Y (local), back edge on x = 0, nose toward -X, top at z = 0."""
    nose = [(depth - r + r * cos(radians(a)), -r + r * sin(radians(a))) for a in range(-90, 91, 30)]
    mb = mo.MB()
    mb.sweep([(0, -t)] + nose + [(0, 0)], [(0, -length / 2, 0), (0, length / 2, 0)], 'oak_rustic')
    return mb.finish(name)


def _aircon(name):
    """Wall-mounted split indoor unit 0.80 x 0.29 x 0.21 and its bottom louvre (own object, hinged on its back
    edge). Origin: wall plane, bottom centre; front -Y. -> (body, louvre, hinge point, hinge axis) in the local frame."""
    w, grey = M.mat('plastic_white'), M.solid('purple_room_ac_grey', '#C4C6C8', 0.5)
    sec = [(0, 0), (-.15, 0), (-.185, .012), (-.205, .04), (-.21, .08), (-.21, .24), (-.20, .27), (-.18, .287),
           (-.15, .29), (0, .29)]
    mb = mo.MB()
    mb.prism([(-0.40, y, z) for y, z in sec], (0.80, 0, 0), w)
    mb.box((-0.398, -0.2106, 0.108), (0.398, -0.2094, 0.1105), grey)                # front panel joint
    mb.box((-0.37, -0.148, -0.0008), (0.37, -0.062, 0.001), 'anthracite')           # the outlet behind the louvre
    mb.box((0.30, -0.2108, 0.045), (0.345, -0.2094, 0.057), grey)                   # blank logo plate
    mb.at(Tr((0.25, -0.2104, 0.051)) @ Matrix.Rotation(1.5708, 4, 'X'))
    mb.lathe([(0, 0), (.004, 0), (.004, .0012), (0, .0012)], grey, 10)              # indicator
    body = mb.finish(name)
    lv = mo.MB()
    lv.box((-0.385, -0.152, -0.006), (0.385, -0.058, -0.0012), w, bev=0.0015)
    return body, lv.finish(name + '.louvre'), Vector((0, -0.058, -0.0012)), Vector((1, 0, 0))


def _remote(name):
    """White a/c remote with a blank screen in its wall cradle, 0.07 x 0.16. Origin: wall, centre; front -Y."""
    mb = mo.MB()
    mb.box((-0.035, -0.012, -0.08), (0.035, 0, 0.02), 'plastic_white', bev=0.003)                # cradle
    mb.box((-0.026, -0.024, -0.07), (0.026, -0.006, 0.08), 'plastic_white', bev=0.004)           # handset
    mb.box((-0.018, -0.0248, 0.03), (0.018, -0.0236, 0.068), 'screen_black')                     # screen, blank
    for i in range(3):
        mb.box((-0.018, -0.0246, -0.045 + 0.022 * i), (0.018, -0.0236, -0.033 + 0.022 * i), M.paint('#D9DADB', 0.5))
    return mb.finish(name)


def _twin_plate(name):
    """Single white plate with two small outlets (aerial / data). Origin: wall, centre; front -Y."""
    mb = mo.MB()
    mb.box((-0.043, -0.008, -0.043), (0.043, 0, 0.043), 'plastic_white', bev=0.003)
    for x in (-0.018, 0.018):
        mb.box((x - 0.012, -0.0095, -0.012), (x + 0.012, -0.0078, 0.012), M.paint('#E4E4E2', 0.5), bev=0.001)
        mb.at(Tr((x, -0.0096, 0)) @ Matrix.Rotation(1.5708, 4, 'X'))
        mb.lathe([(0, 0), (.0045, 0), (.0045, .0006), (0, .0006)], 'black', 8)
        mb.at()
    return mb.finish(name)


def _chair(name):
    """The Chippendale side chair that stands in the room: the dining side chair (same pierced splat and tapestry
    seat) with its straight front legs cut away for cabriole legs on claw feet. Faces local -Y."""
    from rooms import dining_chairs as DC, dining_furniture as DF
    src = DC.chair(name + '.src')
    me = src.data.copy()
    me.name = name
    bpy.data.objects.remove(src)
    bm = bmesh.new()
    bm.from_mesh(me)
    cut = [f for f in bm.faces if any(v.co.z < 0.38 for v in f.verts)
           and all(v.co.y < -0.20 and abs(v.co.x) > 0.21 and v.co.z < 0.401 for v in f.verts)]
    bmesh.ops.delete(bm, geom=cut, context='FACES')
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    for i, s in enumerate((-1, 1)):
        leg = P.turned_leg(.447, .062, 'cabriole', .065, 0, DF.dark_wood(), out=(s, -1), foot='claw', name=f'{name}.leg.{i}')
        leg.parent = ob
        leg.location = (s * (.265 - .031), -.25 + .031, 0)
    return ob


def _eyelet(ob, axis_y, n, drop=0.25, half=0.05, lean=-0.015, dip=0.022):
    """Eyelet heading on a curtain_panel cloth of n pleats: its top `drop` is drawn into waves +/- half round the pole
    axis (local y = axis_y), in the phase of the prop's own pleats and easing back into them below. `lean` shifts
    the cloth along the width so the front crests round over (radius about 2 cm) and the back folds close up behind
    the pole; the top edge dips `dip` where the cloth crosses the pole (the eyelets), so it rolls over the pole in
    soft humps (hr_v13_019). Works on a copy of the mesh."""
    me = ob.data = ob.data.copy()
    rows = {}
    for v in me.vertices:
        if v.co.z > -drop:
            rows.setdefault(round(v.co.z, 4), []).append(v)
    for vs in rows.values():
        vs.sort(key=lambda v: v.co.x)
    zt = max(rows)
    top = [(v.co.y, tau * n * i / (len(rows[zt]) - 1)) for i, v in enumerate(rows[zt])]
    ps = atan2(sum(y * sin(a) for y, a in top), sum(y * cos(a) for y, a in top))    # phase of the back folds
    for z, vs in rows.items():
        t = _sm(1 + z / drop)
        for i, v in enumerate(vs):
            th = tau * n * i / (len(vs) - 1) - ps                   # 0 = back fold (wall side), pi = front crest
            v.co.y += t * (axis_y + half * cos(th) - v.co.y)
            v.co.x += t * lean * sin(th)
            if z == zt:
                v.co.z -= dip * (1 - abs(cos(th))) ** 2             # flat crowns, notched at the eyelets
    me.update()
    return ob


def build(ctx):
    poly = ctx.room_poly(ROOM)
    X0, X1 = min(p[0] for p in poly), max(p[0] for p in poly)
    Y0, Y1 = min(p[1] for p in poly), max(p[1] for p in poly)
    FZ, cz = ctx.floor_z(ROOM), ctx.ceil_z(ROOM)
    E, W, N, S = (-1, 0), (1, 0), (0, -1), (0, 1)                   # wall normals into the room
    fw = ctx.opening_frame('w_purple')
    YW, WW, ZS, ZH = fw['center'].y, fw['width'], FZ + fw['sill'], FZ + fw['head']
    fd = ctx.opening_frame('d_purple')
    YD = fd['center'].y - fd['width'] / 2                           # south edge of the door's clear opening
    fr = bpy.data.objects.get(f'{ROOM}.w_purple.frame')             # ponytail: the window is in the east wall (+X out)
    XF = (min((fr.matrix_world @ Vector(c)).x for c in fr.bound_box) if fr else
          (fw['center'].xy + fw['normal'] * fw['face_out'] - fw['outward'] * (fw['ext_reveal'] + ctx.FRAME_D)).x)

    # ---- window wall: reveal in the wall colour, oak board, trickle vent, radiator
    shell.repaint(ROOM, shell.WHITE, '#B9B5C6')
    # board 0.27 deep from the frame (nose 0.05 proud of the wall), 0.85 long: 15 mm horns past the 0.82 reveal.
    # Top 2 mm above the reveal floor, the body let into the wall below it as a real board is.
    bd = _window_board('purple_room.window_board', WW + 0.03, XF - (X1 - 0.055))
    bd.location = (XF, YW, ZS + 0.002)
    ctx.add(bd, ROOM, 'fit')
    mb = mo.MB()                                                    # white slot vent on the head of the fixed light
    mb.box((XF - 0.013, YW - 0.27, ZH - 0.036), (XF + 0.001, YW + 0.27, ZH - 0.010), 'upvc_white', bev=0.003)  # v13 t19:
    mb.box((XF - 0.0136, YW - 0.25, ZH - 0.026), (XF - 0.0126, YW + 0.25, ZH - 0.020), 'anthracite')       # 0.69 of the head
    ctx.add(mb.finish('purple_room.trickle_vent'), ROOM, 'fit')
    # bottom level with the skirting top (0.17), 0.51 high (top 0.05 under the board, hr_v4_389), centred on the window
    ctx.add(P.place(_radiator('purple_room.radiator'), (X1, YW, FZ + 0.17), facing=E), ROOM, 'fit', plan_sym='radiator')

    # ---- air conditioning: unit high on the S wall at the SE corner, 0.05 from the E wall (hr_v4_399), or 0.25 from
    # it while the S pole finial (tip 0.79 from the window axis) would stand in front of it (floor2_a); remote in its
    # cradle beside the dimmer; either opens the louvre
    body, louvre, hp, ha = _aircon('purple_room.aircon')
    gap = 0.05 if YW - 0.79 - Y0 > 0.26 else 0.25
    for o in (body, louvre):
        P.place(o, (X1 - gap - 0.40, Y0, FZ + 2.18), facing=S)
    remote = P.place(_remote('purple_room.aircon.remote'), (X0, YD - 0.27, FZ + 1.30), facing=W)
    IX.tag(louvre, 'hinge', g='purple_room.aircon', label='Air conditioning', p=louvre.matrix_basis @ hp,
           a=louvre.matrix_basis.to_3x3() @ ha, deg=50, reach=3.0)
    IX.tag(remote, 'trigger', g='purple_room.aircon', label='Air conditioning')
    IX.tag(body, 'trigger', g='purple_room.aircon', label='Air conditioning', reach=3.0)
    ctx.add(body, ROOM, 'fit', lm='dynamic')
    ctx.add(louvre, ROOM, 'fit', lm='dynamic')
    ctx.add(remote, ROOM, 'fit', lm='dynamic')

    # ---- electrics: W wall double socket 0.74 from the S wall (floor2_a, hr_v4_393), N wall double socket 0.17 from
    # the E wall (hr_v4_389: 15 px left of the NE corner, 198 / 213 px from the vanishing point), twin outlet plate
    # high on the S wall, detector disc on the ceiling 0.30 off the S wall
    for i, (loc, n) in enumerate((((X0, Y0 + 0.74, FZ + 0.33), W), ((X1 - 0.17, Y1, FZ + 0.33), N))):
        ctx.add(P.place(P.socket(2, name=f'purple_room.socket.{i}'), loc, facing=n), ROOM, 'fit')
    ctx.add(P.place(_twin_plate('purple_room.outlet_plate'), (X1 - 1.53, Y0, FZ + 1.25), facing=S), ROOM, 'fit')
    disc = mo.MB()
    disc.lathe([(0, -.012), (.045, -.012), (.06, -.004), (.06, 0)], 'plastic_white', 20)
    ob = disc.finish('purple_room.ceiling_disc')
    ob.location = (X1 - 1.33, Y0 + 0.30, cz)
    ctx.add(ob, ROOM, 'fit')

    # ---- lights: four downlights in a 1.00 x 0.91 grid on the room centre, one dimmer beside the door
    xc, yc = (X0 + X1) / 2, (Y0 + Y1) / 2
    for i, (x, y) in enumerate((xc + dx, yc + dy) for dx in (-0.50, 0.50) for dy in (-0.455, 0.455)):
        lighting.downlight(ctx, ROOM, x, y, watts=45, name=f'purple_room.downlight.{i}')
        ctx.add(P.place(P.downlight(name=f'purple_room.downlight_trim.{i}'), (x, y, cz)), ROOM, 'light')
    sw = P.place(P.switch_plate(1, 'dimmer', name='purple_room.dimmer'), (X0, YD - 0.16, FZ + 1.25), facing=W)
    IX.tag(sw, 'light', rooms=[ROOM], label='Lights')
    ctx.add(sw, ROOM, 'fit', lm='dynamic')

    # ---- curtains: eyelet drops on a mid-brown pole 1.58 tip to tip at z 2.33, 0.09 off the wall, centred on the
    # window; tied back at z 0.88 beside the reveal (state 0) / drawn across (state 1). Hem 0.30 above the floor.
    cloth = M.image_mat('purple_room_curtain', 'art/purple_room_curtain.jpg', (1.075, 1.875), roughness=0.85)
    gold = P.mat('tassel_gold')
    dia, st, pz = 0.032, 0.09, FZ + 2.33
    half = 1.58 / 2 - (0.012 + 2 * dia)                             # pole tube half length (props 'ball' finial)
    top, hem, tie = pz + 0.045, FZ + 0.30, FZ + 0.88
    pole = P.curtain_pole(2 * half, dia, 'ball', rings=0, mat=M.solid('purple_room_pole', '#8B5E3C', 0.45),
                          standoff=st, name='purple_room.curtain.pole')
    ctx.add(P.place(pole, (X1, YW, pz), facing=E), ROOM, 'decor', lm='dynamic')
    IX.tag(pole, 'trigger', g='purple_room.curtain', label='Curtains')
    # open drops: from 0.33 off the window axis (the heading laps the reveal, hr_v4_389) to the finial base; the
    # cloth origin plane 0.05 off the wall keeps the back folds clear of the board nose (0.055)
    w_in, o, depth, gather = 0.33, 0.05, 0.055, 0.7
    ws, c = half - w_in, (half + w_in) / 2
    hw_mb = mo.MB()
    for i, sy in enumerate((1, -1)):                    # sy +1: the north drop (left seen from the room)
        side = sy                                       # local +x of a drop facing E is world -Y: both tie to the window
        drop = P.curtain_panel(ws, top - hem, cloth, folds=4, depth=depth, tieback='right' if side > 0 else 'left',
                               tie_from_top=top - tie, gather=gather, tassel=0, seed=3 + i, fold_res=16,
                               hardware=False, name=f'purple_room.curtain.open.{i}')
        _eyelet(drop, o - st, 4)
        P.place(drop, (X1 - o, YW + sy * c, top), facing=E)
        IX.tag(drop, 'show', g='purple_room.curtain', when=0, fx='none', label='Curtains')
        ctx.add(drop, ROOM, 'decor', lm='dynamic')
        # gold rope loop round the bunch, hook to the wall behind it, tassel in front.
        # ponytail: f, a, cx, hw repeat props._curtain's bunch (gather * .8) and fold depth at the tie
        f = gather * .8
        a = 1.22 * depth * min(1.7, f ** -.5)
        cx, hw, zt = side * ws / 2 * (1 - f), ws * f / 2, -(top - tie)
        Mb = drop.matrix_basis
        loop = [Mb @ Vector((cx + (hw + .012) * cos(t), -.012 - a / 2 + (a / 2 + .014) * sin(t), zt + .03 * side * cos(t)))
                for t in (tau * k / 16 for k in range(16))]
        hw_mb.tube(loop, .007, gold, 6, closed=True, up=Mb.to_3x3() @ Vector((0, 0, 1)))
        hw_mb.tube([Mb @ Vector((cx, o, zt + .03)), Mb @ Vector((cx, -.006, zt + .03))], .005, 'brass', 6)
        tas = P.tassel(.16, .03, gold, name=f'purple_room.curtain.tassel.{i}')
        P.place(tas, Mb @ Vector((cx - side * hw * .2, -.012 - a - .03, zt - .02)))
        IX.tag(tas, 'show', g='purple_room.curtain', when=0, fx='none', label='Curtains')
        ctx.add(tas, ROOM, 'decor', lm='dynamic')
    hk = hw_mb.finish('purple_room.curtain.hooks')
    IX.tag(hk, 'show', g='purple_room.curtain', when=0, fx='none', label='Curtains')
    ctx.add(hk, ROOM, 'decor', lm='dynamic')
    # closed: each half from the finial base to 10 mm past the middle; hung 0.125 off the wall below the heading
    # so the folds clear the radiator front (0.13), easing back to the pole over the top 1.2 m
    wc, oc = half + 0.01, 0.125
    for i, sy in enumerate((1, -1)):
        shut = P.curtain_panel(wc, top - hem, cloth, folds=6, depth=depth, seed=5 + i, fold_res=12, hardware=False,
                               name=f'purple_room.curtain.closed.{i}')
        _eyelet(shut, oc - st, 6, drop=1.2)
        P.place(shut, (X1 - oc, YW + sy * (half - wc / 2), top), facing=E)
        IX.tag(shut, 'show', g='purple_room.curtain', when=1, fx='none', label='Curtains')
        ctx.add(shut, ROOM, 'decor', lm='dynamic')

    # ---- the one piece of furniture: side chair against the S wall
    try:
        ch = _chair('purple_room.chair')
    except Exception as e:                                          # the chair mesh lives in the dining module
        print(f'[purple_room] WARNING: chair skipped ({e!r})')
    else:
        ctx.add(P.place(ch, (X1 - 1.23, Y0 + 0.34, FZ), rot_z=180), ROOM, 'furn', plan_sym='chair')

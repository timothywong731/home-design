"""purple_room - the unused lilac room on the second floor (spec/rooms/purple_room.md, footage v4 f_0388-f_0440).

The owner calls it unfurnished: what is here is fixed - column radiator, split air-conditioning unit with its remote,
oak window board, the floral eyelet curtains on a dark pole, sockets, the dimmer and its four downlights - plus the
one real piece of furniture that stands in it, a Chippendale side chair.

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --levels 2 --only shell,purple_room --preview purple_room \
        --res 540x960 --samples 64 --tag purple_room            (open state: --pose 1 --tag purple_room1)
"""
import bmesh
import bpy
from mathutils import Matrix, Vector

from lib import interact as IX, lighting, materials as M, mouldings as mo, props as P, shell

ROOM = 'purple_room'
X0, X1, Y0, Y1, FZ = 0.32, 3.10, 9.29, 11.20, 6.02          # inside wall faces, floor (house.json)
YW = 10.25                                                  # window centre

CAMERAS = [
    dict(name='door', pos=(0.50, 10.80, 7.52), look=(3.10, 10.20, 7.25), fov_deg=100, ref='v4:f_0390'),
    dict(name='window', pos=(1.32, 10.49, 7.50), look=(3.10, 10.25, 7.75), fov_deg=100, ref='v4:f_0392'),
    dict(name='west', pos=(2.32, 9.89, 7.52), look=(0.32, 10.45, 7.35), fov_deg=100, ref='v4:f_0394'),
    dict(name='south', pos=(1.92, 11.00, 7.40), look=(2.05, 9.29, 7.35), fov_deg=100, ref='v4:f_0400'),
    dict(name='north', pos=(1.50, 9.60, 7.45), look=(1.90, 11.20, 6.90), fov_deg=100, ref='v4:f_0436'),
    dict(name='sill', pos=(2.45, 10.25, 7.60), look=(3.30, 10.25, 7.05), fov_deg=100, ref='v4:f_0416'),
    dict(name='head', pos=(2.72, 10.40, 7.45), look=(3.30, 10.20, 8.25), fov_deg=100, ref='v4:f_0408'),
    dict(name='ceiling', pos=(2.70, 10.95, 6.60), look=(1.40, 9.90, 8.62), fov_deg=100, ref='v4:f_0396'),
]

Tr = Matrix.Translation


def _radiator(name, n=9, pitch=0.048, h=0.60):
    """Two-column steel column radiator: per section a round-topped header bulb top and bottom and two tubes.
    Origin: wall plane, bottom centre of the body; front -Y (0.03 .. 0.10 off the wall)."""
    mb, w, yc = mo.MB(), 'white_gloss', -0.065
    bulb = [(0, -.036), (.012, -.034), (.019, -.028), (.0225, -.014), (.0225, .012), (.018, .027), (.010, .034), (0, .036)]
    half = (n - 1) * pitch / 2
    for i in range(n):
        x = -half + i * pitch
        for z in (0.036, h - 0.036):
            mb.at(Tr((x, yc, z)))
            mb.lathe(bulb, w, 12, ell=(1, 1.55))
        mb.at()
        for dy in (-0.019, 0.019):
            mb.tube([(x, yc + dy, 0.05), (x, yc + dy, h - 0.05)], 0.0145, w, 8)
    for z in (0.036, h - 0.036):                                    # the nipples that join the sections
        mb.tube([(-half, yc, z), (half, yc, z)], 0.013, w, 8)
    xe = half + pitch / 2 + 0.022
    for s in (-1, 1):                                               # chrome valve + tail to the floor at each end
        mb.tube([(s * xe, yc, -0.11), (s * xe, yc, 0.036)], 0.0075, 'chrome', 8)
        mb.tube([(s * (xe + 0.012), yc, 0.036), (s * half, yc, 0.036)], 0.011, 'chrome', 8)
    mb.tube([(xe + 0.012, yc, 0.036), (xe + 0.06, yc, 0.036)], 0.019, 'plastic_white', 10)      # TRV head, south end
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


def build(ctx):
    cz = ctx.ceil_z(ROOM)
    E, W, N, S = (-1, 0), (1, 0), (0, -1), (0, 1)                   # wall normals into the room

    # ---- window wall: reveal in the wall colour, oak board, trickle vent, radiator
    shell.repaint(ROOM, shell.WHITE, '#B4AFC6')
    mb = mo.MB()
    mb.box((X1 - 0.03, YW - 0.40, FZ + 0.732), (X1 + 0.221, YW + 0.40, FZ + 0.762), 'oak_rustic', bev=0.006, grain=1)
    ctx.add(mb.finish('purple_room.window_board'), ROOM, 'fit')
    mb = mo.MB()
    mb.box((X1 + 0.206, YW - 0.20, FZ + 2.142), (X1 + 0.221, YW + 0.20, FZ + 2.168), 'upvc_white', bev=0.004)
    ctx.add(mb.finish('purple_room.trickle_vent'), ROOM, 'fit')
    ctx.add(P.place(_radiator('purple_room.radiator'), (X1, YW, FZ + 0.11), facing=E), ROOM, 'fit', plan_sym='radiator')

    # ---- air conditioning: unit high on the S wall, remote in its cradle by the door; either opens the louvre
    body, louvre, hp, ha = _aircon('purple_room.aircon')
    for o in (body, louvre):
        P.place(o, (X0 + 2.33, Y0, FZ + 2.18), facing=S)
    remote = P.place(_remote('purple_room.aircon.remote'), (X0, Y0 + 0.95, FZ + 1.30), facing=W)
    IX.tag(louvre, 'hinge', g='purple_room.aircon', label='Air conditioning', p=louvre.matrix_basis @ hp,
           a=louvre.matrix_basis.to_3x3() @ ha, deg=50, reach=3.0)
    IX.tag(remote, 'trigger', g='purple_room.aircon', label='Air conditioning')
    IX.tag(body, 'trigger', g='purple_room.aircon', label='Air conditioning', reach=3.0)
    ctx.add(body, ROOM, 'fit', lm='dynamic')
    ctx.add(louvre, ROOM, 'fit', lm='dynamic')
    ctx.add(remote, ROOM, 'fit', lm='dynamic')

    # ---- electrics
    for i, (loc, n) in enumerate((((X0, Y0 + 0.55, FZ + 0.33), W), ((X0 + 2.35, Y1, FZ + 0.33), N))):
        ctx.add(P.place(P.socket(2, name=f'purple_room.socket.{i}'), loc, facing=n), ROOM, 'fit')
    ctx.add(P.place(_twin_plate('purple_room.outlet_plate'), (X0 + 1.25, Y0, FZ + 1.25), facing=S), ROOM, 'fit')
    disc = mo.MB()
    disc.lathe([(0, -.012), (.045, -.012), (.06, -.004), (.06, 0)], 'plastic_white', 20)
    ob = disc.finish('purple_room.ceiling_disc')
    ob.location = (X0 + 1.45, Y0 + 0.30, cz)
    ctx.add(ob, ROOM, 'fit')

    # ---- lights: four downlights on one rotary dimmer beside the door
    for i, (x, y) in enumerate(((0.90, 0.50), (0.90, 1.41), (1.90, 0.50), (1.90, 1.41))):
        lighting.downlight(ctx, ROOM, X0 + x, Y0 + y, watts=45, name=f'purple_room.downlight.{i}')
        ctx.add(P.place(P.downlight(name=f'purple_room.downlight_trim.{i}'), (X0 + x, Y0 + y, cz)), ROOM, 'light')
    sw = P.place(P.switch_plate(1, 'dimmer', name='purple_room.dimmer'), (X0, Y0 + 1.04, FZ + 1.25), facing=W)
    IX.tag(sw, 'light', rooms=[ROOM], label='Lights')
    ctx.add(sw, ROOM, 'fit', lm='dynamic')

    # ---- curtains: dark pole, eyelet drops tied back toward the window (state 0) / drawn (state 1)
    cloth = M.image_mat('purple_room_curtain', 'art/purple_room_curtain.jpg', (0.5375, 0.9375), roughness=0.85)
    span, stack, top, tie, off = 1.36, 0.29, 2.38, 1.50, 0.105      # ponytail: no modelled eyelets - the cloth hangs just
    gold, depth = 'tassel_gold', .055                               # in front of the pole, clear of radiator and board
    # pole 1.30, not the spec's 1.50: that puts the south finial inside the a/c; the footage has it clear (f_0401)
    pole = P.curtain_pole(1.30, .030, 'ball', rings=0, mat=M.solid('purple_room_pole', '#4A3024', 0.45), standoff=0.09,
                          name='purple_room.curtain.pole')
    ctx.add(P.place(pole, (X1, YW, FZ + 2.33), facing=E), ROOM, 'decor', lm='dynamic')
    IX.tag(pole, 'trigger', g='purple_room.curtain', label='Curtains')
    hooks = mo.MB()
    for i, sg in enumerate((-1, 1)):                    # sg -1: the north drop (left seen from the room), tied to its right
        side = -sg                                      # local +x of a drop facing E is world -Y: both gather to the window
        drop = P.curtain_panel(stack, top - 0.32, cloth, folds=5, depth=depth, tieback='right' if side > 0 else 'left',
                               tie_from_top=tie, tassel=0, seed=3 + i, tie_mat=gold, name=f'purple_room.curtain.open.{i}')
        P.place(drop, (X1 - off, YW - sg * (span - stack) / 2, FZ + top), facing=E)
        IX.tag(drop, 'show', g='purple_room.curtain', when=0, fx='none', label='Curtains')
        ctx.add(drop, ROOM, 'decor', lm='dynamic')
        y = YW - sg * (span / 2 - stack - 0.012)        # the prop's tie hook (beside the reveal) starts at the cloth plane:
        hooks.tube([(X1, y, FZ + top - tie + 0.03), (X1 - off, y, FZ + top - tie + 0.03)], 0.005, 'brass', 6)   # carry it to the wall
        # slender tassel from the front of the tie loop (the prop's own has a fixed 60 mm head).
        # ponytail: f and a repeat props._curtain's bunch width (gather .6 * .8) and loop depth at the tie
        f = .6 * .8
        a = 1.22 * depth * min(1.7, f ** -.5)
        tas = P.tassel(.14, .028, gold, name=f'purple_room.curtain.tassel.{i}')
        P.place(tas, drop.matrix_basis @ Vector((side * stack / 2 * (1 - f), -.033 - a, -tie)))
        IX.tag(tas, 'show', g='purple_room.curtain', when=0, fx='none', label='Curtains')
        ctx.add(tas, ROOM, 'decor', lm='dynamic')
    hk = hooks.finish('purple_room.curtain.hooks')
    IX.tag(hk, 'show', g='purple_room.curtain', when=0, fx='none', label='Curtains')
    ctx.add(hk, ROOM, 'decor', lm='dynamic')
    shut = P.curtain_pair(span, top - 0.32, cloth, hang=None, hardware=False, closed=True, depth=depth, seed=5,
                          name='purple_room.curtain.closed')
    IX.tag(shut, 'show', g='purple_room.curtain', when=1, fx='none', label='Curtains')
    ctx.add(P.place(shut, (X1 - off, YW, FZ + top), facing=E), ROOM, 'decor', lm='dynamic')

    # ---- the one piece of furniture: side chair against the S wall
    try:
        ch = _chair('purple_room.chair')
    except Exception as e:                                          # the chair mesh lives in the dining module
        print(f'[purple_room] WARNING: chair skipped ({e!r})')
    else:
        ctx.add(P.place(ch, (X0 + 1.55, Y0 + 0.34, FZ), rot_z=180), ROOM, 'furn', plan_sym='chair')

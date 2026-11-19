"""Side passage and side alley (pseudo-room `side_passage`, level X): what hangs on the flank (x 3.40), the
kitchen-door wall (y 9.03) and the alley wall (x 4.53) and lies on the paving - hose reel, the two garden taps
(water runs), a/c condensers, security light (click to light), louvre vent, gully, inspection cover, fence
climbers. Spec: spec/phase2/rear_elevation.md 5 - 6, spec/rooms/garden.md 3.2, 5.

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --levels G,X --only shell,site,envelope,garden,side_passage \
        --preview side_passage --res 540x960 --samples 64 --tag garden      (--pose 1 --tag garden1: taps run, light on)

Sky-lit only: no lamps. Soil stack, downpipes, waste runs, the old drain along the wall foot, the gate and the
kitchen steps are built by envelope / site. Refs are frames of reference/v2."""
import math
from math import pi

import bpy
from mathutils import Matrix, Vector as V

from lib import materials as M, mouldings as mo, props as P
from rooms import garden_parts as G
from rooms.garden import climbers, fence_x
from rooms.garden_parts import T, col

ROOM = 'side_passage'
XF, YK, XE = 3.40, 9.03, 4.53       # flank face, kitchen-door wall face, east wall of the main house (alley)
PAVE = -0.30

CAMERAS = [
    dict(name='passage', pos=(4.05, 17.0, 1.25), look=(4.0, 9.0, 0.9), fov_deg=95, ref='f_0319'),
    dict(name='reel', pos=(4.35, 16.0, 1.0), look=(3.4, 16.85, 0.45), fov_deg=85, ref='f_0321'),
    dict(name='tap_rear', pos=(4.0, 16.45, 0.35), look=(3.4, 16.6, 0.0), fov_deg=75, ref='f_0325'),
    dict(name='flank', pos=(4.2, 16.7, 1.0), look=(3.4, 15.3, 3.6), fov_deg=95, ref='f_0329'),
    dict(name='steps', pos=(4.3, 11.5, 1.3), look=(3.8, 9.1, 1.1), fov_deg=100, ref='f_0343'),
    dict(name='gate', pos=(3.85, 11.3, 1.5), look=(4.9, 9.9, 1.4), fov_deg=80, ref='f_0343'),
    dict(name='tap_door', pos=(4.2, 10.45, 0.7), look=(3.4, 9.75, 0.25), fov_deg=80, ref='f_0353'),
    dict(name='gully', pos=(4.2, 10.0, 0.6), look=(4.4, 9.1, -0.25), fov_deg=80, ref='f_0349'),
    dict(name='out', pos=(3.9, 10.3, 1.3), look=(4.0, 17.5, 0.9), fov_deg=95, ref='f_0231'),
    dict(name='alley', pos=(5.0, 4.6, 1.5), look=(4.6, 8.4, 2.3), fov_deg=90, ref=None),
]


def _add(ctx, ob, kind='fit', sym=None):
    return ctx.add(ob, ROOM, kind, plan_sym=sym, lm='dynamic')


def _hose_reel(ctx):
    """Grey automatic wall reel with yellow trim on a pivot bracket near the rear corner (rear_elevation.md 5.1,
    v2:f_0321): a flat oval housing ~0.6 x 0.47, 0.23 off the wall, its dark drum cover facing out. Local frame: wall
    y = 0, front -Y, +X toward the garden. The trailing hose is decluttered: only the feed from the tap's distributor
    and the short tail with the spray gun hanging from the outlet."""
    grey, dark, yellow = col('reel_grey', '#8E9296', .45), col('reel_dark', '#55595E', .5), col('reel_yellow', '#E6C81E', .4)
    hose, orange = col('hose_grey', '#9C9E9A', .5), col('hose_gun', '#E0782A', .45)
    y, z = 16.93, 0.975
    out = Matrix.Rotation(pi / 2, 4, 'X')                                                      # lathe axis -> local -Y
    mb = mo.MB()
    mb.box((-.07, -.03, -.13), (.07, 0, .13), dark, bev=.004)                                  # wall bracket and pivot
    mb.box((-.04, -.045, -.08), (.04, -.03, .08), dark, bev=.004)
    mb.at(T(-.04) @ out)                                                                       # housing, stretched along the wall
    mb.lathe([(0, .044), (.215, .044), (.232, .06), (.236, .09), (.236, .19), (.226, .214), (.2, .228), (0, .228)], grey, 24,
             ell=(1.27, 1.0))
    mb.at(T(.03) @ out)                                                                        # drum cover, hub
    mb.lathe([(.172, .2275), (.172, .233), (.06, .233), (.06, .237), (0, .237)], dark, 24)
    mb.at()
    mb.box((-.13, -.20, .214), (.07, -.07, .244), yellow, bev=.01)                             # carry handle on top
    mb.box((.236, -.19, -.07), (.268, -.08, .10), yellow, bev=.008)                            # trim on the garden end
    mb.box((-.35, -.17, -.13), (-.29, -.06, .02), dark, bev=.01)                               # hose guide arm
    reel = P.place(mb.finish('side_passage.hose_reel'), (XF, y, z), facing=(1, 0))
    _add(ctx, reel, 'fit', 'pipe')                          # wall-hung at hip height: 'pipe' = blocking footprint, plain outline

    mb = mo.MB()                                                                               # local frame of the reel
    tail = G.chaikin([(.17, -.12, -.17), (.18, -.13, -.30), (.19, -.14, -.46), (.19, -.14, -.52)])
    mb.tube(tail, .0075, hose, 6)
    gx, gy, gz = tail[-1]
    mb.tube([(gx, gy, gz), (gx, gy, gz - .12)], .012, orange, 6)                               # spray gun hanging on the tail
    mb.tube([(gx, gy, gz - .12), (gx, gy - .03, gz - .17)], .016, M.mat('black_matt'), 6)
    mb.tube([(gx, gy - .03, gz - .17), (gx, gy - .045, gz - .195)], .022, M.mat('silver_satin'), 8)
    lx = lambda wy: wy - y                                                                     # world y -> local x
    feed = G.chaikin([(lx(16.57), -.078, -.01 - z), (lx(16.60), -.10, -.20 - z), (lx(16.68), -.16, -.275 - z), (lx(16.76), -.16, -.15 - z),
                      (lx(16.79), -.12, .40 - z), (-.16, -.10, -.19)])
    mb.tube(feed, .0075, hose, 6)
    _add(ctx, P.place(mb.finish('side_passage.hose'), (XF, y, z), facing=(1, 0)), 'decor')


def _taps(ctx):
    """T1 (rear, with a black four-way distributor) and T2 by the kitchen door ("there's a tap here")."""
    black = M.mat('black_matt')
    # T1: y 16.55, z 0.15; the distributor hangs on its nose, three hoses plugged in, water runs from the free outlet
    mb = mo.MB()
    xs, zs = XF + .078, .15 - .066
    mb.box((xs - .028, 16.55 - .085, zs - .06), (xs + .028, 16.55 + .085, zs), black, bev=.006)
    for i, hx in enumerate(('#3FA04E', '#E6C81E', '#3FA04E')):
        mb.at(T(xs, 16.55 - .06 + i * .04, zs - .095))
        mb.lathe([(0, 0), (.011, 0), (.013, .012), (.013, .035), (0, .035)], col('hose_fit_' + hx[1:], hx, .4), 8)
    mb.at()
    _add(ctx, mb.finish('side_passage.tap.rear.splitter'))
    out = (xs, 16.55 + .06, zs - .062)
    G.bib_tap(ctx, ROOM, 'side_passage.tap.rear', XF, 16.55, .15, (1, 0), 'Garden tap', out[2] - PAVE - .002, outlet=out)
    # T2: y 9.80, z 0.45, straight above the old drain pipe along the wall foot (envelope: centre x 3.47, z -0.20, d 0.11)
    G.bib_tap(ctx, ROOM, 'side_passage.tap.door', XF, 9.80, .45, (1, 0), 'Garden tap', .45 - .066 + .143, splash=.05)
    galv = M.mat('silver_satin')
    mb = mo.MB()
    mb.tube([(XF, 10.0, .76), (XF + .03, 10.0, .76), (XF + .03, 10.0, .74)], .004, galv, 5)   # hook
    for i in range(15):                                                                        # short chain
        zc = .736 - i * .02
        a, b = ((.0015, .007), (.007, .0015))[i % 2]
        mb.box((XF + .03 - a, 10.0 - b, zc - .013), (XF + .03 + a, 10.0 + b, zc + .013), galv)
    _add(ctx, mb.finish('side_passage.chain'), 'decor')


def _wall_bits(ctx):
    """Louvre vent and the small white box by the kitchen door (flank wall, rear_elevation.md 5.1)."""
    white = M.mat('plastic_white')
    mb = mo.MB()
    mb.box((-.075, -.012, -.075), (.075, 0, .075), white, bev=.003)
    for i in range(5):
        mb.at(T(0, -.012, -.05 + i * .025) @ Matrix.Rotation(math.radians(-35), 4, 'X'))
        mb.box((-.062, -.012, -.002), (.062, .004, .002), white)
    _add(ctx, P.place(mb.at().finish('side_passage.vent'), (XF, 9.25, 2.05), facing=(1, 0)))
    mb = mo.MB()
    mb.box((-.05, -.03, -.035), (.05, 0, .035), white, bev=.004)
    _add(ctx, P.place(mb.finish('side_passage.wall_box'), (XF, 9.20, 1.30), facing=(1, 0)))


def _condensers(ctx):
    """Outdoor a/c units: on the flank above the dining windows (isolator and a 25 mm pipe down the wall), and on
    the east wall of the main house in the alley, with the grey 120 mm flue beside it (rear_elevation.md 5.1, 6)."""
    feats = {f['id']: f for f in ctx.spec['exterior']['features']}
    black, grey = M.mat('black_matt'), col('flue_grey', '#8C8E90', .5)
    first = G.condenser('side_passage.condenser.flank')
    x, y, z = feats['condenser_flank']['at']
    _add(ctx, P.place(first, (x, y, z), facing=(1, 0)), 'fit', 'condenser')
    mb = mo.MB()
    mb.box((x, y + .61, z + .30), (x + .05, y + .69, z + .40), col('condenser', '#D8D8D4', .45), bev=.004)   # rotary isolator
    mb.box((x + .05, y + .635, z + .335), (x + .065, y + .665, z + .365), col('isolator_red', '#C0281E', .4))
    mb.tube([(x + .015, y + .47, z + .2), (x + .015, y + .47, PAVE)], .0125, black, 6)
    mb.tube([(x + .015, y + .42, z + .3), (x + .015, y + .65, z + .33)], .008, black, 5)
    _add(ctx, mb.finish('side_passage.condenser.flank.pipes'))

    x, y, z = feats['condenser_east']['at']
    ob = bpy.data.objects.new('side_passage.condenser.east', first.data)
    _add(ctx, P.place(ob, (x, y, z), facing=(1, 0)), 'fit', 'condenser')
    g = ctx.ground_z(x + .3, y - .6)
    mb = mo.MB()
    mb.tube([(x + .075, y - .62, g), (x + .075, y - .62, 2.95)], .06, grey, 10)
    mb.at(T(x + .075, y - .62, 2.95))
    mb.lathe([(.06, 0), (.085, .02), (.085, .05), (0, .09)], grey, 10)
    for zc in (.6, 1.8):
        mb.at(T(x, y - .62, zc))
        mb.box((0, -.07, -.012), (.02, .07, .012), black)
    _add(ctx, mb.at().finish('side_passage.flue'), 'fit', 'pipe')


def _security_light(ctx):
    """White twin-head security light with a camera between the heads, above the back door (rear_elevation.md 6).
    Mounted 0.2 higher than the spec so that it clears the first-floor waste pipe (envelope, z 3.30)."""
    white, lens = M.mat('plastic_white'), col('flood_lens', '#8A8E92', .2)
    aim = Matrix.Rotation(math.radians(115), 4, 'X')                                         # lamp axis: out and 25 deg down
    mb, gl = mo.MB(), mo.MB()
    mb.box((-.05, -.03, -.06), (.05, 0, .06), white, bev=.005)
    mb.box((-.022, -.07, -.05), (.022, -.03, -.005), white, bev=.005)                         # camera
    mb.at(T(0, -.07, -.027) @ Matrix.Rotation(pi / 2, 4, 'X'))
    mb.lathe([(.014, 0), (.014, .002), (0, .002)], M.mat('black_gloss'), 10)
    for s in (-1, 1):
        mb.at()
        mb.tube([(s * .04, -.02, .03), (s * .085, -.05, .04)], .009, white, 6)
        H = T(s * .085, -.05, .04) @ aim
        mb.at(H)
        mb.lathe([(0, -.02), (.03, -.02), (.047, .03), (.047, .05), (.04, .05), (.04, .046)], white, 14)
        mb.lathe([(.04, .046), (0, .046)], lens, 14)
        gl.at(H)
        gl.lathe([(.039, .0475), (0, .0475)], P.emissive('#FFD9A0', 10.0), 14)
    body = P.place(mb.at().finish('side_passage.security_light'), (3.95, YK, 3.55), facing=(0, 1))
    glow = P.place(gl.at().finish('side_passage.security_light.glow'), (3.95, YK, 3.55), facing=(0, 1))
    G.click_glow(ctx, ROOM, body, glow, 'Security light')


def _solar_light(ctx):
    """Small solar light on top of the gate's latch post (garden.md 5, v2:f_0343): black panel tilted to the sky on a
    short stem, a lamp under its front edge facing the passage. Automatic in reality; here a click lights it."""
    g = next(b for b in ctx.spec['exterior']['boundaries'] if b['id'] == 'side_gate')
    (ax, ay), (ex, ey) = g['line']
    u = V((ex - ax, ey - ay))
    ln = u.length
    u.normalize()
    n = V((-u.y, u.x))                                                                         # into the side passage
    c = V((ax, ay)) + u * (ln + .0535) - n * .0225                                             # latch post centre (lib/site._gate)
    tilt = T(0, .01, .13) @ Matrix.Rotation(math.radians(30), 4, 'X')
    black, lens = M.mat('black_matt'), col('flood_lens', '#8A8E92', .2)
    mb, gl = mo.MB(), mo.MB()
    mb.box((-.016, -.016, 0), (.016, .016, .12), black, bev=.003)                              # stem on the post top
    mb.box((-.03, -.075, .048), (.03, -.016, .078), black, bev=.004)                           # lamp head
    mb.face([(-.024, -.0755, .052), (.024, -.0755, .052), (.024, -.0755, .074), (-.024, -.0755, .074)], lens, (0, -1, 0))
    gl.face([(-.024, -.0765, .052), (.024, -.0765, .052), (.024, -.0765, .074), (-.024, -.0765, .074)], P.emissive('#FFE2B8', 8.0), (0, -1, 0))
    mb.at(tilt)
    mb.box((-.08, -.065, -.012), (.08, .065, .006), black, bev=.003)
    mb.box((-.07, -.055, .006), (.07, .055, .008), col('solar_cell', '#1C2232', .15))
    mb.at()
    loc = (c.x, c.y, g['baseZ'] + 1.95)
    body = P.place(mb.finish('side_passage.solar_light'), loc, facing=tuple(n))
    glow = P.place(gl.finish('side_passage.solar_light.glow'), loc, facing=tuple(n))
    G.click_glow(ctx, ROOM, body, glow, 'Solar light')


def _ground(ctx):
    """Gully under the main-roof downpipe (red-brown plastic grate) and the recessed inspection cover's steel frame."""
    gx, gy = 4.38, 9.15
    g = ctx.ground_z(gx, gy)
    red, dark = col('gully_red', '#8A3A2A', .5), col('gully_dark', '#1C1C1E', .6)
    mb = mo.MB()
    mb.box((gx - .075, gy - .055, g), (gx + .075, gy + .095, g + .006), red, bev=.002)
    for i in range(5):
        mb.box((gx - .055, gy - .035 + i * .026, g + .006), (gx + .055, gy - .023 + i * .026, g + .0065), dark)
    _add(ctx, mb.finish('side_passage.gully'))
    steel = M.mat('silver_satin')
    x0, x1, y0, y1, w, z = 4.15, 4.75, 10.10, 10.90, .012, PAVE
    mb = mo.MB()
    for a, b in (((x0, y0), (x1, y0 + w)), ((x0, y1 - w), (x1, y1)), ((x0, y0 + w), (x0 + w, y1 - w)), ((x1 - w, y0 + w), (x1, y1 - w))):
        mb.box((*a, z), (*b, z + .003), steel)
    _add(ctx, mb.finish('side_passage.inspection_cover'))


def build(ctx):
    _hose_reel(ctx)
    _taps(ctx)
    _wall_bits(ctx)
    _condensers(ctx)
    _security_light(ctx)
    _solar_light(ctx)
    _ground(ctx)
    climbers(ctx, ROOM, 'side_passage.climbers', (11.2, 13.1, 14.9, 16.4), 17)

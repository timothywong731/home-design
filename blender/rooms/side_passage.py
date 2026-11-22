"""Side passage and side alley (pseudo-room `side_passage`, levels G / X): what hangs on the flank F (x 3.45), the
kitchen-door wall K (y 9.03) and the insulated east wall E in the alley (x 4.65), and what lies on the paving and the
alley concrete - hose reel, the two garden taps (water runs), both a/c condensers with their conduits and isolators,
the white boiler flue, the two alley wall lights (click to light), the security and solar lights, louvre vent and
extract grille, gully, inspection and access covers, fence climbers. Spec: spec/phase3/briefs/side_passage.md,
spec/phase3/passage.md, spec/rooms/side_passage.md.

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --levels G,X --only shell,site,envelope,side_passage \
        --preview side_passage --res 540x960 --samples 64 --tag r3side_passage   (--pose 1: taps run, lights on)

Sky-lit only: no lamps. Soil stack, downpipes, the old drain along the flank foot, the flank conduits up to the
condenser, the east-wall base rail, both gates, the kitchen steps and the fence are built by envelope / site.
Camera refs are frames of reference/v11 (21 Nov) unless marked v2."""
import json
import math
import random
from math import pi

import bpy
from mathutils import Matrix, Vector as V

from lib import interact as IX, materials as M, mouldings as mo, props as P, site as S
from rooms import garden_parts as G
from rooms.garden_parts import T, col, leafmats

ROOM = 'side_passage'
XF, YK, XE = 3.45, 9.03, 4.65       # flank face, kitchen-door wall face, rendered face of the east wall (alley)
PAVE = -0.30                        # passage flags and alley concrete

CAMERAS = [
    dict(name='passage', pos=(4.05, 17.3, 1.25), look=(4.0, 9.0, 0.9), fov_deg=95, ref='v11 f_0175'),
    dict(name='reel', pos=(4.35, 16.0, 1.0), look=(3.45, 16.85, 0.45), fov_deg=85, ref='v11 f_0053'),
    dict(name='tap_rear', pos=(4.0, 16.35, 0.35), look=(3.45, 16.55, 0.0), fov_deg=75, ref='v11 f_0055'),
    dict(name='loop', pos=(4.6, 12.7, 1.3), look=(3.5, 15.1, 4.2), fov_deg=75, ref='v11 f_0044'),
    dict(name='steps', pos=(4.3, 11.5, 1.3), look=(3.8, 9.1, 1.1), fov_deg=100, ref='v11 f_0063'),
    dict(name='gate', pos=(3.85, 11.3, 1.5), look=(4.9, 9.9, 1.4), fov_deg=80, ref='v11 f_0151'),
    dict(name='tap_door', pos=(4.2, 10.75, 0.75), look=(3.45, 9.9, 0.2), fov_deg=85, ref='v11 f_0021'),
    dict(name='cover', pos=(4.1, 12.1, 1.2), look=(4.75, 10.3, -0.3), fov_deg=85, ref='v11 f_0033'),
    dict(name='out', pos=(3.9, 10.3, 1.3), look=(4.0, 17.5, 0.9), fov_deg=95, ref='v11 f_0045'),
    dict(name='alley_n', pos=(5.2, 2.65, 1.1), look=(5.0, 8.5, 1.4), fov_deg=95, ref='v11 f_0127'),     # clear of the street gate's swing
    dict(name='alley_s', pos=(5.2, 8.3, 1.1), look=(5.2, 1.9, 0.9), fov_deg=95, ref='v11 f_0083'),
    dict(name='east', pos=(5.6, 4.6, 0.9), look=(4.65, 5.6, 2.7), fov_deg=95, ref='v11 f_0101'),
    dict(name='flue', pos=(5.45, 7.0, 1.1), look=(4.75, 8.7, 0.6), fov_deg=95, ref='v11 f_0149'),
]


def _add(ctx, ob, kind='fit', sym=None):
    return ctx.add(ob, ROOM, kind, plan_sym=sym, lm='dynamic')


def _fence_face(ctx):
    """x of the east fence's board face on the passage side at y (site builds the boards 11 mm behind the line)."""
    f = next(b for b in ctx.spec['exterior']['boundaries'] if b['id'] == 'east_fence')
    (x0, y0), (x1, y1) = f['line']
    return lambda y: x0 + (x1 - x0) * (y - y0) / (y1 - y0) - .0115


def _offset(pts, d):
    """Polyline in the (y, z) plane of a wall offset by d to its left (mitred); -> list of (y, z)."""
    out = []
    for i, p in enumerate(pts):
        a, b = V(pts[max(i - 1, 0)]), V(pts[min(i + 1, len(pts) - 1)])
        n = V((0.0, 0.0))
        for s, e in ((a, V(p)), (V(p), b)):
            t = e - s
            if t.length > 1e-9:
                n += V((-t.y, t.x)).normalized()
        n.normalize()
        k = 1.0
        if 0 < i < len(pts) - 1:
            t = (V(p) - a).normalized()
            k = 1.0 / max(.3, abs(n.dot(V((-t.y, t.x)))))
        out.append((p[0] + n.x * d * k, p[1] + n.y * d * k))
    return out


def _fillet(pts, rads):
    """2D polyline with interior corner i+1 rounded to radius rads[i] (arc points every <= 15 degrees)."""
    out = [tuple(pts[0])]
    for i in range(1, len(pts) - 1):
        a, p, b = V(pts[i - 1]), V(pts[i]), V(pts[i + 1])
        u, w = (a - p).normalized(), (b - p).normalized()
        th, r = u.angle(w), rads[i - 1]
        s, e = p + u * (r / math.tan(th / 2)), p + w * (r / math.tan(th / 2))
        c = p + (u + w).normalized() * (r / math.sin(th / 2))
        a0, a1 = math.atan2(s.y - c.y, s.x - c.x), math.atan2(e.y - c.y, e.x - c.x)
        d = (a1 - a0 + pi) % (2 * pi) - pi
        n = max(2, math.ceil(abs(d) / (pi / 12)))
        out += [(c.x + r * math.cos(a0 + d * k / n), c.y + r * math.sin(a0 + d * k / n)) for k in range(n + 1)]
    return out + [tuple(pts[-1])]


def _twin(mb, x, yz, mat, r=.0225, gap=.047, straps=.5):
    """Twin black conduits strapped together, on a wall x = const; yz = centre line in the wall plane. A strap every
    `straps` m of run (the first half a pitch in), turned square to the run where it lies."""
    for s in (-.5, .5):
        mb.tube([(x, y, z) for y, z in _offset(yz, s * gap)], r, mat, 8, up=(1, 0, 0))
    strap = col('conduit_strap', '#1A1A1C', .5)
    hw, run, nxt = gap / 2 + r + .002, 0.0, straps / 2
    total = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(yz, yz[1:]))
    for (y0, z0), (y1, z1) in zip(yz, yz[1:]):
        L = math.hypot(y1 - y0, z1 - z0)
        while L > 1e-9 and nxt <= run + L and nxt < total - .06:
            t = (nxt - run) / L
            mb.at(T(x, y0 + (y1 - y0) * t, z0 + (z1 - z0) * t) @ Matrix.Rotation(math.atan2(z1 - z0, y1 - y0), 4, 'X'))
            mb.box((-r - .002, -.006, -hw), (r + .002, .006, hw), strap)
            nxt += straps
        run += L
    mb.at()


# ---------------------------------------------------------------- parts (local frames: wall y = 0, front -Y)
def _condenser(name, L, D, H, gap=.08):
    """Outdoor a/c unit L along the wall x D deep x H high on two galvanised wall brackets, its back `gap` off the wall
    (v11 f_0047, f_0096-f_0104). Origin = centre of the underside on the wall plane, +X = valve end (service cover with
    its label), -X = coil end (guard grid over the fins); fan behind a wire grille on the front."""
    case, side = col('condenser', '#D8D8D4', .45), col('condenser_side', '#C4C4C0', .5)
    disc, wire = col('condenser_fan', '#1E1F22', .6), col('condenser_grille', '#3A3C40', .5)
    fins, rubber = col('condenser_fins', '#5E6166', .6), M.mat('black_matt')
    galv, label = M.mat('silver_satin'), col('condenser_label', '#ECECE8', .6)
    yf, yb, hx = -(gap + D), -gap, L / 2
    mb = mo.MB()
    mb.box((-hx, yf, .012), (hx, yb, H - .014), case, bev=.008)
    mb.box((-hx - .006, yf - .006, H - .014), (hx + .006, yb + .003, H), case, bev=.004)          # lid, overhanging
    R = min(.42 * H, .31 * L)
    fx, fz = -hx + .05 + R, H * .5
    mb.at(Matrix.Translation((fx, yf, fz)) @ Matrix.Rotation(pi / 2, 4, 'X'))                      # lathe +Z -> -Y
    mb.lathe([(R + .025, 0), (R + .025, .006), (R + .012, .013), (R, .013), (R, .001)], case, 28)  # bezel
    mb.lathe([(R, .001), (0, .001)], disc, 28)
    for k in range(1, 5):
        rr = R * k / 4.6
        mb.tube([(rr * math.cos(2 * pi * i / 24), rr * math.sin(2 * pi * i / 24), .009) for i in range(24)],
                .0022, wire, 4, closed=True, up=(0, 0, 1))
    for i in range(8):
        a = 2 * pi * (i + .5) / 8
        mb.tube([(.045 * math.cos(a), .045 * math.sin(a), .009), (R * math.cos(a), R * math.sin(a), .009)], .0022, wire, 4)
    mb.lathe([(.045, .001), (.045, .014), (.04, .017), (0, .017)], wire, 14)                       # hub cap
    mb.at()
    px = fx + R + .045                                                                             # valve-side front panel
    mb.box((px, yf - .003, .05), (hx - .02, yf, H - .06), side, bev=.002)
    for i in range(6):
        mb.box((px + .02, yf - .0045, .09 + i * .03), (hx - .04, yf - .003, .098 + i * .03), disc)  # air slots
    mb.box((-hx - .003, yf + .02, .04), (-hx, yb - .015, H - .05), fins)                           # coil end
    for i in range(7):
        z = .04 + (H - .09) * i / 6
        mb.box((-hx - .008, yf + .02, z - .003), (-hx - .003, yb - .015, z + .003), case)
    for i in range(4):
        y = yf + .02 + (D - .035) * i / 3
        mb.box((-hx - .008, y - .003, .04), (-hx - .003, y + .003, H - .05), case)
    mb.box((hx, yf + .02, .06), (hx + .035, yf + min(.2, D - .05), .44), case, bev=.008)          # service cover
    mb.box((hx + .035, yf + .05, .30), (hx + .0365, yf + .13, .38), label)
    for x in (-hx + .1, hx - .1):
        mb.box((x - .02, yf - .04, -.03), (x + .02, 0, 0), galv)                                   # arm
        mb.box((x - .02, -.03, -.33), (x + .02, 0, -.03), galv)                                    # wall upright
        mb.prism([(x - .012, -.03, -.30), (x - .012, yf + .04, -.03), (x - .012, yf + .08, -.03), (x - .012, -.03, -.26)],
                 (.024, 0, 0), galv)                                                               # strut
        for y0 in (yf + .02, yb - .06):
            mb.box((x - .03, y0, 0), (x + .03, y0 + .04, .012), rubber)                            # anti-vibration feet
    return mb.finish(name)


def _louvre(name, a, n, mat, void='#141416'):
    """Square louvre grille a x a, 20 mm proud: frame, n louvres tilted down and out over a dark void. Centre = origin."""
    mb, h, w = mo.MB(), a / 2, .012
    mb.box((-h, -.006, -h), (h, 0, h), mat, bev=.002)
    for lo, hi in (((-h, -.02, h - w), (h, -.006, h)), ((-h, -.02, -h), (h, -.006, -h + w)),
                   ((-h, -.02, -h + w), (-h + w, -.006, h - w)), ((h - w, -.02, -h + w), (h, -.006, h - w))):
        mb.box(lo, hi, mat, bev=.002)
    mb.box((-h + w, -.0068, -h + w), (h - w, -.006, h - w), col('vent_void', void, .8))
    pitch = (a - 2 * w) / n
    for i in range(n):
        mb.at(T(0, -.014, -h + w + pitch * (i + .5)) @ Matrix.Rotation(math.radians(-35), 4, 'X'))
        mb.box((-h + w, -.0015, -pitch * .5), (h - w, .0015, pitch * .5), mat)
    return mb.at().finish(name)


def _wall_lamp(name, r=.03, h=.15, plate=.08, off=.075, lit=True):
    """Anthracite cylinder wall light (v11 f_0094, f_0102): square plate, short arm, a cylinder r x h standing `off`
    from the wall, frosted band low down. Origin = centre of the plate. -> body, glow (band + bottom lens, 1 mm proud)."""
    an, frost = M.mat('anthracite'), col('lamp_frost', '#D9D6CC', .3)
    z0, zb, zc = -.03, .02, h - .03                                         # bottom, top of the band, top
    mb = mo.MB()
    mb.box((-plate / 2, -.012, -plate / 2), (plate / 2, 0, plate / 2), an, bev=.003)
    mb.box((-.012, -off + r * .7, -.015), (.012, -.012, .012), an, bev=.002)
    mb.at(T(0, -off, 0))
    mb.lathe([(0, z0), (r, z0), (r, z0 + .012)], an, 16)
    mb.lathe([(r, z0 + .012), (r, zb)], frost if lit else an, 16)
    mb.lathe([(r, zb), (r, zc - .004), (r - .004, zc), (0, zc)], an, 16)
    mb.lathe([(0, z0 - .001), (r * .7, z0 - .001)], frost if lit else M.mat('black_gloss'), 12)
    body = mb.at().finish(name)
    if not lit:
        return body, None
    gl, em = mo.MB(), P.emissive('#F4CB94', 12.0)
    gl.at(T(0, -off, 0))
    gl.lathe([(r + .001, z0 + .013), (r + .001, zb - .001)], em, 16)
    gl.lathe([(0, z0 - .002), (r * .7, z0 - .002)], em, 12)
    return body, gl.at().finish(name + '.glow')


# ---------------------------------------------------------------- flank and K
def _hose_reel(ctx, tap_out):
    """Grey automatic wall reel with a yellow band on a dark pivot bracket (v11 f_0049-f_0055; y 16.7..17.2, z
    0.75..1.25): a flat oval housing ~0.6 x 0.47, 0.23 off the wall, its dark drum cover facing out. Local frame:
    wall y = 0, front -Y, +X toward the garden. The feed hose runs from the distributor under tap T1; the short tail
    with the spray gun hangs from the outlet."""
    grey, dark, yellow = col('reel_grey', '#8E9296', .45), col('reel_dark', '#55595E', .5), col('reel_yellow', '#E6C81E', .4)
    hose, orange = col('hose_grey', '#9C9E9A', .5), col('hose_gun', '#E0782A', .45)
    y, z = 16.95, 1.0
    out = Matrix.Rotation(pi / 2, 4, 'X')
    mb = mo.MB()
    mb.box((-.07, -.03, -.13), (.07, 0, .13), dark, bev=.004)                                  # wall bracket and pivot
    mb.box((-.04, -.045, -.08), (.04, -.03, .08), dark, bev=.004)
    for zz in (-.1, .1):
        mb.at(T(0, -.0, zz) @ out)
        mb.lathe([(.008, .0), (.008, .004), (0, .004)], M.mat('silver_satin'), 8)              # wall screws
    mb.at(T(-.04) @ out)                                                                       # housing, stretched along the wall
    mb.lathe([(0, .044), (.215, .044), (.232, .06), (.236, .09), (.236, .19), (.226, .214), (.2, .228), (0, .228)], grey, 24,
             ell=(1.27, 1.0))
    mb.at(T(.03) @ out)                                                                        # drum cover, hub
    mb.lathe([(.172, .2275), (.172, .233), (.06, .233), (.06, .237), (.03, .243), (0, .243)], dark, 24)
    mb.at()
    mb.box((-.13, -.20, .214), (.07, -.07, .244), yellow, bev=.01)                             # carry handle / band on top
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
    tx, ty, tz = tap_out                                                                       # world: hose connector foot
    feed = G.chaikin([(lx(ty), -(tx - XF), tz - z), (lx(ty) + .02, -.10, PAVE + .05 - z), (lx(ty) + .1, -.16, PAVE + .012 - z),
                      (lx(16.85), -.17, PAVE + .02 - z), (lx(16.86), -.12, .30 - z), (-.16, -.10, -.19)])
    mb.tube(feed, .0075, hose, 6)
    _add(ctx, P.place(mb.finish('side_passage.hose'), (XF, y, z), facing=(1, 0)), 'decor')


def _taps(ctx):
    """T1 (y 16.50, z 0.20) with its black four-way distributor, T2 (y 9.90, z 0.48) with a hose click connector;
    the chain hanging from its staple plate (y 10.02, z 0.75) to the strap of the old drain (v11 f_0021-f_0031)."""
    black, galv = M.mat('black_matt'), M.mat('silver_satin')
    green, yellow, grey = col('hose_fit_3FA04E', '#3FA04E', .4), col('hose_fit_E6C81E', '#E6C81E', .4), col('click_grey', '#8C9094', .45)
    teal, brass = col('hose_fit_2E9C9A', '#2E9C9A', .4), M.mat('brass_antique')
    # T1 (v11 f_0051): a black water-timer box 0.17 x 0.12 with rounded edges and a round dial on its face hangs on
    # the tap nose; three outlets underneath with yellow / teal / green connectors: a loose tail, the reel feed, water
    t1y, t1z = 16.50, .20
    xs, ztop = XF + .078, t1z - .066
    mb = mo.MB()
    mb.box((xs - .028, t1y - .085, ztop - .12), (xs + .028, t1y + .085, ztop), black, bev=.016)
    mb.at(T(xs + .028, t1y + .02, ztop - .058) @ Matrix.Rotation(pi / 2, 4, 'Y'))             # dial: lathe +Z -> +X
    mb.lathe([(.017, -.002), (.017, .003), (.014, .006), (0, .006)], col('timer_dial', '#2A2B2E', .35), 16)
    mb.lathe([(.009, .0062), (.0105, .0062)], grey, 12)
    mb.at(T(xs, t1y, ztop))
    mb.lathe([(.016, -.01), (.016, .0), (.012, .004), (0, .004)], black, 10)                   # union under the nose
    outs = []
    for i, mat in enumerate((yellow, teal, green)):
        oy = t1y - .05 + i * .05
        mb.at(T(xs, oy, ztop - .12))
        mb.lathe([(.009, .0), (.009, -.018), (.0075, -.022), (0, -.022)], black, 8)            # outlet spigot
        mb.at(T(xs, oy, ztop - .142))
        mb.lathe([(0, 0), (.0125, 0), (.0135, -.012), (.0135, -.034), (.008, -.042), (0, -.042)], mat, 10)
        outs.append((xs, oy, ztop - .184))
    mb.at()
    _add(ctx, mb.finish('side_passage.tap.rear.splitter'))
    x, oy, oz = outs[2]
    G.bib_tap(ctx, ROOM, 'side_passage.tap.rear', XF, t1y, t1z, (1, 0), 'Garden tap', oz - PAVE - .002, outlet=(x, oy, oz))
    lever = mo.MB()                                       # T1 has a flat lever, not a cross head (same hinge, same axis)
    lever.lathe([(.0095, .034), (.0095, .046), (.006, .049), (0, .049)], brass, 10)
    lever.at(T(0, 0, .044) @ Matrix.Rotation(math.radians(-8), 4, 'Y'))                       # along the wall, north
    lever.box((0, -.0045, -.003), (.075, .0045, .003), brass, bev=.0015)
    lever.box((.06, -.006, -.004), (.08, .006, .004), col('lever_grip', '#1E1E20', .5), bev=.002)
    head = bpy.data.objects['side_passage.tap.rear.head']
    old, tmp = head.data, lever.at().finish('side_passage.tap.rear.head')
    head.data = tmp.data
    bpy.data.objects.remove(tmp)
    bpy.data.meshes.remove(old)
    d = json.loads(head['ix'])                            # turn the other way so the lever swings out, not into the wall
    IX.tag(head, 'hinge', g=d['g'], label=d['label'], p=d['p'], a=d['a'], deg=-90, dur=d['dur'])
    sp = mo.MB()                                          # both taps are double: a plain spout turns down by the plate
    for ty, tz in ((t1y, t1z), (9.90, .48)):
        sp.tube([(XF + .004, ty, tz - .008), (XF + .026, ty - .014, tz - .012), (XF + .030, ty - .020, tz - .03),
                 (XF + .030, ty - .020, tz - .058)], .0085, brass, 6)
        sp.tube([(XF + .030, ty - .020, tz - .052), (XF + .030, ty - .020, tz - .066)], .0105, brass, 6)
    _add(ctx, sp.finish('side_passage.tap_spouts'))
    tails = mo.MB()                                                                            # the loose hose tail
    hose = col('hose_grey', '#9C9E9A', .5)
    x, oy, oz = outs[0]
    tails.tube(G.chaikin([(x, oy, oz + .002), (x + .01, oy, PAVE + .06), (x + .06, oy - .09, PAVE + .012),
                          (x + .09, oy - .22, PAVE + .012)]), .0075, hose, 6)
    _add(ctx, tails.finish('side_passage.tap.rear.hoses'), 'decor')
    feed = outs[1][0], outs[1][1], outs[1][2] + .002

    # T2: brass bib tap with a grey / green click connector on the nose, straight above the old drain (top -0.145)
    t2y, t2z = 9.90, .48
    nose = (XF + .078, t2y, t2z - .066)
    mb = mo.MB()
    mb.at(T(*nose))
    mb.lathe([(0, 0), (.0135, 0), (.0135, -.012), (.0125, -.016)], grey, 10)
    mb.lathe([(.0125, -.016), (.014, -.018), (.014, -.034), (.0125, -.036)], green, 10)
    mb.lathe([(.0125, -.036), (.009, -.048), (.009, -.056), (0, -.056)], grey, 10)
    _add(ctx, mb.at().finish('side_passage.tap.door.connector'))
    pipe_top = -.145
    G.bib_tap(ctx, ROOM, 'side_passage.tap.door', XF, t2y, t2z, (1, 0), 'Garden tap', nose[2] - .056 - pipe_top,
              splash=.05, outlet=(nose[0], nose[1], nose[2] - .056))

    # chain: staple plate at z 0.75, galvanised links hanging to the drain strap
    mb = mo.MB()
    cy, ztop = 10.02, .75
    mb.box((XF, cy - .022, ztop - .03), (XF + .004, cy + .022, ztop + .03), galv, bev=.001)
    mb.tube([(XF + .004, cy, ztop - .01), (XF + .022, cy, ztop - .01), (XF + .022, cy, ztop - .03)], .004, galv, 5)
    strap_top = -.20 + .061                                                                    # the drain strap (_drain_bits)
    n = round((ztop - .045 - (strap_top + .012)) / .021) + 1
    for i in range(n):
        zc = ztop - .045 - i * .021
        xc = XF + .022 + (.068 - .022) * i / max(n - 1, 1)                                 # leans out to the strap
        a, b = ((.0016, .008), (.008, .0016))[i % 2]
        mb.box((xc - a, cy - b, zc - .014), (xc + a, cy + b, zc + .014), galv)
    _add(ctx, mb.finish('side_passage.chain'), 'decor')
    return feed


def _drain_bits(ctx):
    """On the old 110 mm drain along the flank foot (envelope: centre x 3.52, z -0.20, y 9.70..12.30): a socketed
    end with a 45-degree branch rising toward the steps under a round screw cap (raised bar, two slots; v11 f_0022),
    the wall strap, and the second 40 mm black pipe lying beside it on the passage side (v11 f_0021-f_0031). The cap
    clears the lower tread's nosing (y 9.665, top -0.16)."""
    black, cap = col('drain_black', '#26262A', .55), col('drain_cap', '#1E1E21', .6)
    slot = col('drain_void', '#0E0E10', .9)
    x, z = 3.52, -.20
    mb = mo.MB()
    mb.at(T(x, 9.668, z) @ Matrix.Rotation(-pi / 2, 4, 'X'))                                   # socketed end: +Z -> +Y
    mb.lathe([(0, 0), (.058, 0), (.0625, .004), (.0625, .12), (.058, .124)], black, 20)
    up = T(x, 9.80, z) @ Matrix.Rotation(pi / 4, 4, 'X')                                       # branch axis (0, -.71, .71)
    mb.at(up)
    mb.lathe([(.055, .0), (.055, .095), (.0585, .098)], black, 20)
    mb.at(up @ T(0, 0, .098))
    mb.lathe([(.064, 0), (.064, .022), (.06, .026), (0, .026)], cap, 20)                       # screw cap
    mb.box((-.046, -.009, .026), (.046, .009, .036), cap, bev=.002)                            # raised bar
    for sx in (-.024, .024):
        mb.box((sx - .007, -.003, .0355), (sx + .007, .003, .0365), slot)                      # its two slots
    mb.at()
    mb.box((XF, 10.005, z + .045), (XF + .006, 10.035, z + .085), black)                        # strap tab on the wall
    mb.at(T(x, 10.02, z) @ Matrix.Rotation(pi / 2, 4, 'X'))
    mb.lathe([(.058, -.012), (.061, -.012), (.061, .012), (.058, .012)], black, 16)            # strap band (chain end)
    mb.at()
    x2 = 3.581 + .006 + .02
    mb.tube([(x2, 9.80, PAVE + .02), (x2, 12.18, PAVE + .02)], .02, black, 8)
    mb.at(T(x2, 9.80, PAVE + .02) @ Matrix.Rotation(pi / 2, 4, 'X'))
    mb.lathe([(.0165, .001), (0, .001)], col('drain_void', '#0E0E10', .9), 8)                   # open end
    mb.at()
    for y in (10.6, 11.6):
        mb.box((x2 - .024, y - .01, PAVE), (x2 + .024, y + .01, PAVE + .044), black)            # saddle clips
    _add(ctx, mb.finish('side_passage.drain_cap'))


def _flank_vent(ctx):
    """White gravity louvre vent, 0.155 square, 3 louvres, north of the WC window (v11 f_0026-f_0029)."""
    ob = _louvre('side_passage.vent', .155, 3, M.mat('plastic_white'))
    _add(ctx, P.place(ob, (XF, 10.00, 1.945), facing=(1, 0)))


def _flank_condenser(ctx):
    """Condenser on the flank above the dining windows (spec feature condenser_flank), its rotary isolator, the 25 mm
    drop pipe at y 15.86, and the inverted-U loop of the twin conduits into its top (the envelope runs them along the
    flank at z 3.90 / 3.85 to y 14.95; v11 f_0044-f_0048, passage.md 2.4)."""
    f = next(x for x in ctx.spec['exterior']['features'] if x['id'] == 'condenser_flank')
    x, y, z = f['at']
    D, L, H = f['size']
    black = col('conduit', '#202022', .5)
    unit = _condenser('side_passage.condenser.flank', L, D, H)
    _add(ctx, P.place(unit, (x, y, z), facing=(1, 0)), 'fit', 'condenser')
    mb = mo.MB()
    ye = y + L / 2
    mb.box((x, ye + .21, z + .30), (x + .05, ye + .29, z + .40), col('condenser', '#D8D8D4', .45), bev=.004)   # isolator
    mb.at(T(x + .05, ye + .25, z + .35) @ Matrix.Rotation(pi / 2, 4, 'Y'))
    mb.lathe([(.022, 0), (.022, .008), (0, .008)], col('isolator_red', '#C0281E', .4), 12)
    mb.at()
    mb.box((x + .05, ye + .243, z + .33), (x + .068, ye + .257, z + .37), col('isolator_red', '#C0281E', .4))
    dy = 15.86
    mb.tube([(x + .08 + D * .5, ye - .02, z + .22), (x + .02, dy, z + .22), (x + .014, dy, z + .16), (x + .014, dy, PAVE)],
            .0125, black, 6)
    for zc in (.6, 1.6, 2.6):
        mb.box((x, dy - .018, zc - .008), (x + .03, dy + .018, zc + .008), black)
    mb.tube([(x + .1, ye - .01, z + .36), (x + .035, ye + .1, z + .36), (x + .03, ye + .21, z + .35)], .006, black, 5)
    # the loop (v11 f_0045, f_0047): the pair turns up off the envelope run (z 3.90 / 3.85, ends y 14.95) at the unit's
    # back south corner, rises 0.9 above the lid, turns over and runs diagonally down north along the wall to the
    # valve end, then drops behind the lid and turns out into it; side by side all the way, a strap every 0.5 m
    xc, zt = 3.475, z + H
    c = _fillet([(14.92, 3.875), (15.0, 3.875), (15.0, zt + 1.055), (15.62, zt + .32), (15.62, zt + .10)], (.06, .09, .06))
    _twin(mb, xc, c, black, gap=.05)
    for s in (-.025, .025):
        ys, zs = _offset(c, s)[-1]
        mb.tube(G.chaikin([(xc, ys, zs + .01), (xc, ys, zt + .06), (xc + .025, ys, zt + .03), (xc + .07, ys, zt + .025),
                           (x + .14, ys, zt + .02), (x + .16, ys, zt - .03)], 2), .0225, black, 8, up=(0, 1, 0))
        mb.at(T(x + .16, ys, zt))
        mb.lathe([(.031, 0), (.031, .004), (.024, .007)], black, 10)                         # gland on the lid
        mb.at()
    _add(ctx, mb.finish('side_passage.condenser.flank.pipes'))


def _security_light(ctx):
    """White twin-head security light with a camera between the heads, above the back door (rear_elevation.md 6,
    passage.md 2.2). Mounted at z 3.55, clear of the first-floor soil branch (envelope, top 3.355)."""
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
    """Small solar light on top of the garden gate's latch post (passage.md 2.6): black panel tilted to the sky on a
    short stem, a lamp under its front edge facing the passage. Automatic in reality; here a click lights it."""
    g = next(b for b in ctx.spec['exterior']['boundaries'] if b['id'] == 'side_gate')
    (ax, ay), (ex, ey) = g['line']
    u = V((ex - ax, ey - ay))
    ln = u.length
    u.normalize()
    n = V((-u.y, u.x))                                                                         # into the side passage
    c = V((ax, ay)) + u * (ln + .006 + S.GATE_POST / 2) - n * .0225                            # latch post centre (lib/site._gate)
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
    loc = (c.x, c.y, g['baseZ'] + S.GATE_HEAD - .004)
    body = P.place(mb.finish('side_passage.solar_light'), loc, facing=tuple(n))
    glow = P.place(gl.finish('side_passage.solar_light.glow'), loc, facing=tuple(n))
    G.click_glow(ctx, ROOM, body, glow, 'Solar light')


# ---------------------------------------------------------------- east wall (alley)
def _east_condenser(ctx):
    """Multi-split condenser on galvanised brackets, y 5.30..6.15, z 2.35..3.15 (spec condenser_east: `at` = its
    south end and underside), rotary isolator on the wall at its north end with the cables into the service cover;
    the twin conduits rise from the base rail at y 3.5 leaning north, run north at z 3.3 and drop into the top of the
    unit at its back south corner (v11 f_0096-f_0104, f_0127)."""
    f = next(x for x in ctx.spec['exterior']['features'] if x['id'] == 'condenser_east')
    x, y0, z = f['at']
    D, L, H = f['size']
    yc = y0 + L / 2
    unit = _condenser('side_passage.condenser.east', L, D, H)
    _add(ctx, P.place(unit, (x, yc, z), facing=(1, 0)), 'fit', 'condenser')
    black = col('conduit', '#202022', .5)
    grey, red = col('isolator_grey', '#BDBDB8', .5), col('isolator_red', '#C0281E', .4)
    mb = mo.MB()
    yi, zi = y0 + L + .14, z + H - .12                                                         # isolator
    mb.box((x, yi - .05, zi - .075), (x + .07, yi + .05, zi + .075), grey, bev=.006)
    mb.at(T(x + .07, yi, zi + .01) @ Matrix.Rotation(pi / 2, 4, 'Y'))
    mb.lathe([(.026, 0), (.026, .008), (0, .008)], red, 14)
    mb.at()
    mb.box((x + .074, yi - .007, zi - .02), (x + .092, yi + .007, zi + .04), red, bev=.003)
    for dz, k in ((-.05, 0), (-.03, 1)):                                                       # cables into the service cover
        mb.tube(G.chaikin([(x + .03, yi - .01 + k * .02, zi - .075), (x + .05, yi - .02, zi - .2 + dz), (x + .2, y0 + L + .06, z + .35 + dz),
                           (x + .25, y0 + L + .03, z + .35 + dz)]), .006, black, 5)
    # twin conduits: from the base rail at y 3.5 up to z 3.3 leaning north, north along the wall, down into the lid
    xw, zr = XE + .024, 3.30
    _twin(mb, xw, [(3.50, -.03), (3.86, zr - .12), (3.98, zr), (y0 - .12, zr)], black)
    for k, dz in enumerate((-.0235, .0235)):
        mb.tube([(xw, y0 - .12, zr + dz), (xw + .02, y0 - .03, zr + dz - .01), (x + .09 + k * .05, y0 + .05, z + H + .04),
                 (x + .09 + k * .05, y0 + .07, z + H - .006)], .0225, black, 8)
    # one conduit carries on 0.4 above the bend and ends in an elbow with a thin cable (f_0102, f_0127)
    mb.tube([(xw, 3.95, zr), (xw, 3.97, zr + .40)], .0225, black, 8)
    mb.tube([(xw, 3.97, zr + .40), (xw + .03, 3.97, zr + .44), (xw + .03, 4.03, zr + .47)], .0225, black, 8)
    mb.tube([(xw + .03, 4.03, zr + .47), (XE + .012, 4.20, zr + .50), (XE + .012, 4.20, zr + .80)], .007, black, 5)
    _add(ctx, mb.finish('side_passage.condenser.east.pipes'))


def _flue(ctx):
    """White 100 mm boiler flue up the east wall (v11 f_0086-f_0090, f_0148): dressed lead slate 0.30 square on the
    alley floor at y 8.55, lead collar, socket joints, two white clips, a 90-degree elbow at z 2.6 and a 0.35 ribbed
    terminal pointing north along the wall. The pipe stands clear of the base rail (x 4.685)."""
    x, y = XE + .105, 8.55
    g = ctx.ground_z(x + .1, y) or PAVE
    white, lead = M.mat('upvc_white'), col('lead_slate', '#6E7275', .6)
    r, rb, zt = .05, .09, 2.6
    mb = mo.MB()                                                                               # flat on the floor: no plan symbol
    mb.box((x - .145, y - .15, g), (x + .155, y + .15, g + .004), lead, bev=.002)
    _add(ctx, mb.finish('side_passage.flue.slate'))
    mb = mo.MB()
    mb.at(T(x, y, g))
    mb.lathe([(r + .012, .004), (r + .012, .20), (r + .006, .21), (r + .001, .21)], lead, 16)
    mb.at()
    mb.tube([(x, y, g + .004), (x, y, zt - rb)], r, white, 12)
    for zc in (.55, 1.55):                                                                     # socket joints
        mb.at(T(x, y, zc))
        mb.lathe([(r + .005, -.04), (r + .005, .04), (r, .045)], white, 12)
    arc = [(x, y + rb - rb * math.cos(a), zt - rb + rb * math.sin(a)) for a in [pi / 2 * i / 6 for i in range(7)]]
    mb.at()
    mb.tube(arc, r, white, 12, up=(1, 0, 0))
    mb.at(T(x, y + rb, zt) @ Matrix.Rotation(-pi / 2, 4, 'X'))                                 # lathe +Z -> +Y
    prof = [(r + .006, 0)]
    for k in range(5):
        b = .025 + k * .052
        prof += [(r + .006, b), (r + .012, b + .006), (r + .012, b + .026), (r + .006, b + .032)]
    prof += [(r + .006, .30), (r + .014, .305), (r + .014, .33), (r * .6, .345), (0, .345)]
    mb.lathe(prof, white, 12)
    mb.at()
    for zc in (.35, 1.75):                                                                     # clips with their wall stems
        mb.at(T(x, y, zc))
        mb.lathe([(r + .009, -.012), (r + .009, .012), (r, .014)], white, 12)
        mb.at()
        mb.box((XE, y - .012, zc - .012), (x - r - .006, y + .012, zc + .012), white, bev=.002)
    _add(ctx, mb.finish('side_passage.flue'), 'fit', 'pipe')


def _alley_lights(ctx):
    """Two anthracite cylinder wall lights, lit in v11 (one switch: one group, click either), at y 3.4 and 7.0,
    z 2.65; the smaller unlit black fitting (y 5.0, z 1.75); the black louvred kitchen
    extract grille (y 6.7, z 1.85) and the black vent cowl high up behind the front corner (y 1.75, z 4.3)."""
    body, glow = _wall_lamp('side_passage.alley_light')
    grp = 'side_passage.alley_light'
    for i, yy in enumerate((3.4, 7.0)):
        b, gw = (body, glow) if i == 0 else (bpy.data.objects.new(f'{body.name}.{i}', body.data),
                                              bpy.data.objects.new(f'{glow.name}.{i}', glow.data))
        P.place(b, (XE, yy, 2.65), facing=(1, 0))
        P.place(gw, (XE, yy, 2.65), facing=(1, 0))
        IX.tag(b, 'trigger', g=grp, label='Wall lights')
        IX.tag(gw, 'show', g=grp, label='Wall lights', when=1, fx='glow')
        ctx.add(b, ROOM, 'fit', lm='dynamic')
        ctx.add(gw, ROOM, 'fit', lm='dynamic')
    small, _ = _wall_lamp('side_passage.alley_sensor', r=.021, h=.10, plate=.06, off=.05, lit=False)
    _add(ctx, P.place(small, (XE, 5.0, 1.75), facing=(1, 0)))
    grille = _louvre('side_passage.extract_grille', .15, 4, M.mat('black_matt'))
    _add(ctx, P.place(grille, (XE, 6.7, 1.85), facing=(1, 0)))
    black = M.mat('black_matt')
    mb = mo.MB()                                                                               # vent cowl, open below
    mb.box((-.125, -.012, -.15), (.125, 0, .15), black, bev=.003)
    mb.prism([(-.125, -.012, .15), (-.125, -.11, -.09), (-.125, -.11, -.15), (-.125, -.012, -.15)], (.25, 0, 0), black)
    mb.box((-.11, -.1, -.152), (.11, -.02, -.15), col('vent_void', '#141416', .8))
    _add(ctx, P.place(mb.finish('side_passage.vent_cowl'), (XE, 1.75, 4.3), facing=(1, 0)))


def _corner_cables(ctx):
    """Bundle of four black cables clipped up the NE corner of the east wall from the alley floor to under the eaves
    (v11 f_0090, f_0148): they come up off the floor over the base rail."""
    black = col('cable_black', '#151517', .5)
    top = ctx.roof_z(XE - .05, YK - .08) - .30 if ctx.roof_z(XE - .05, YK - .08) else 6.0
    mb = mo.MB()
    for i in range(4):
        yy = YK - .025 - i * .013
        mb.tube([(XE + .09 + i * .01, yy - .08, PAVE + .006), (XE + .05, yy - .02, PAVE + .02), (XE + .052, yy, -.09),
                 (XE + .046, yy, -.022), (XE + .007, yy, .06), (XE + .007, yy, top)], .0055, black, 6)
    for k in range(int((top - .3) / .45)):
        zc = .3 + k * .45
        mb.box((XE, YK - .08, zc - .008), (XE + .016, YK - .012, zc + .008), black)
    _add(ctx, mb.finish('side_passage.corner_cables'), 'decor')


# ---------------------------------------------------------------- ground
def _ground(ctx, fence):
    """Gully under the K downpipe (0.15 square, dark grey #2A2A2C, set in the flags), the recessed inspection cover
    0.56 x 0.72 against the fence (galvanised frame, centre bar, lifting slot north, two flag infills) and the alley's
    0.60 x 0.45 concrete access cover with a steel edge, 0.5 m south of the flue (passage.md 2.5, 2.8)."""
    grate, slot = col('gully_grey', '#2A2A2C', .55), col('gully_slot', '#0C0C0E', .9)
    steel, flag = M.mat('silver_satin'), M.mat('sandstone_flags_grey')
    gx, gy = 4.475, 9.12                                                                       # clear of the tread nosing (4.395)
    mb = mo.MB()
    mb.box((gx - .075, gy - .075, PAVE), (gx + .075, gy + .075, PAVE + .003), grate, bev=.0015)
    for i in range(5):
        mb.box((gx - .055, gy - .052 + i * .024, PAVE + .003), (gx + .055, gy - .040 + i * .024, PAVE + .0035), slot)
    _add(ctx, mb.finish('side_passage.gully'))

    x0, x1, y0, y1, w = 4.50, min(5.06, fence(10.97) - .008), 10.25, 10.97, .02
    ym = (y0 + y1) / 2
    mb = mo.MB()
    for a, b in (((x0, y0), (x1, y0 + w)), ((x0, y1 - w), (x1, y1)), ((x0, y0 + w), (x0 + w, y1 - w)),
                 ((x1 - w, y0 + w), (x1, y1 - w)), ((x0 + w, ym - w / 2), (x1 - w, ym + w / 2))):
        mb.box((*a, PAVE), (*b, PAVE + .003), steel)
    xm = (x0 + x1) / 2                                                                         # lifting plate with its slot
    mb.box((xm - .06, y1 - w - .012, PAVE), (xm + .06, y1 - .002, PAVE + .0035), steel)
    mb.box((xm - .03, y1 - w - .004, PAVE + .0035), (xm + .03, y1 - w + .004, PAVE + .004), slot)
    for a, b in (((x0 + w, y0 + w), (x1 - w, ym - w / 2)), ((x0 + w, ym + w / 2), (x1 - w, y1 - w))):
        mb.box((*a, PAVE), (*b, PAVE + .0015), flag)
    _add(ctx, mb.finish('side_passage.inspection_cover'))

    ax0, ax1, ay0, ay1 = XE + .05, XE + .50, 7.73, 8.33
    mb = mo.MB()
    for a, b in (((ax0, ay0), (ax1, ay0 + .012)), ((ax0, ay1 - .012), (ax1, ay1)), ((ax0, ay0 + .012), (ax0 + .012, ay1 - .012)),
                 ((ax1 - .012, ay0 + .012), (ax1, ay1 - .012))):
        mb.box((*a, PAVE), (*b, PAVE + .0025), steel)
    mb.box((ax0 + .012, ay0 + .012, PAVE), (ax1 - .012, ay1 - .012, PAVE + .0015), col('cover_concrete', '#9A9C95', .9))
    _add(ctx, mb.finish('side_passage.access_cover'))


def _climbers(ctx, fence):
    """Climber on the east fence toward the step (v11 f_0045, f_0047, f_0053, f_0055; passage.md 2.6): strands come
    over the capping (z 1.70) and hang down the boards, a few to the paving, thickest on the last two bays
    (y 15.7..17.9); large leaves bunch along the capping at y 16.0..17.3. Each strand stays inside its bay, clear of
    the concrete posts (site: BAY / POST along the fence line)."""
    rng = random.Random(17)
    f = next(b for b in ctx.spec['exterior']['boundaries'] if b['id'] == 'east_fence')
    (x0, y0), (x1, y1) = f['line']
    ln = math.hypot(x1 - x0, y1 - y0)
    bay = ln / max(1, round(ln / S.BAY))
    posts = [y0 + (y1 - y0) / ln * bay * i for i in range(1, 12)]
    nrm = V((-(y1 - y0), x1 - x0, 0)).normalized()                                             # board face normal, to the passage
    nrm = nrm if nrm.x < 0 else -nrm
    top = f['baseZ'] + f['height']
    stem = col('climber_stem', '#5A6B3A', .8)
    mats = leafmats('ivy', ('#5E8A4E', '#6E9A5A', '#8AAE62'))
    mb, ls = mo.MB(), []
    fx = lambda y, z: fence(y) - (.010 if z > -.1 else .025)           # clear of the gravel board low down
    tr = bpy.data.objects.get('garden.east_fence.trellis')                                     # lattice topper (site)
    ty = [(tr.matrix_world @ V(c)).y for c in tr.bound_box] if tr else [0.0]                   # ponytail: one run of bays
    for ys, zb in ((14.45, .75), (14.95, .35), (15.25, 1.0), (15.85, -.27), (16.15, .55), (16.35, .05), (16.55, -.27),
                   (16.9, .2), (17.15, -.27), (17.35, .9), (17.6, -.27), (17.8, .4)):
        lo = max(p for p in [y0] + posts if p < ys) + S.POST / 2 + .06
        hi = min(min(p for p in posts if p > ys) - S.POST / 2 - .06, 17.93)
        if tr and min(ty) < ys < max(ty):                       # down through the lattice, in front of the capping
            pts = [(fence(ys) - .03, ys, top + .22), (fence(ys) - .036, ys + .03, top + .08), (fence(ys) - .03, ys, top - .03)]
        else:                                                   # over the capping from the far side
            pts = [(fence(ys) + .03, ys, top - .03), (fence(ys) - .005, ys, top + .012), (fence(ys) - .028, ys, top - .01)]
        pts.append((fx(ys, 1) - .006, ys, top - .07))
        y, z = ys, top - .07
        while z > zb + .01:
            z = max(zb, z - rng.uniform(.12, .22))
            y = min(hi, max(lo, y + rng.uniform(-.09, .09)))
            pts.append((fx(y, z), y, z))
        if zb < -.2:                                                                           # trails a little on the paving
            pts.append((fx(y, z) - .05, y + rng.uniform(-.1, .1), PAVE + .006))
        mb.tube(G.chaikin(pts, 1), .0035, stem, 3, up=(1, 0, 0))
        hang = pts[3:]                                                                         # leaves below the capping,
        ls += G.strand(rng, hang[:3], 9, .10, .08, 3, tuple(nrm), off=.012)                    # densest at the top
        ls += G.strand(rng, hang[2:], 2 + int(1.5 * len(hang)), .085, .065, 3, tuple(nrm), off=.012)
    for ya, yb in ((16.0, 16.6), (16.75, 17.3)):                                               # big leaves along the capping
        ls += G.strand(rng, [(fence(y) - .021, y, top + .005) for y in (ya, (ya + yb) / 2, yb)], 12, .11, .09, 3,
                       tuple(nrm), off=.01)
    ls = [l for l in ls if min(l[0].z, l[1].z) > PAVE + .01                                    # none through the paving
          and all(abs(q.y - p) > S.POST / 2 + .02 for p in posts for q in l[:2])]                # or the posts
    _add(ctx, mb.finish('side_passage.climbers'), 'decor')
    _add(ctx, G.cards('side_passage.climbers.leaves', ls, mats), 'decor')


def build(ctx):
    fence = _fence_face(ctx)
    feed = _taps(ctx)
    _hose_reel(ctx, feed)
    _drain_bits(ctx)
    _flank_vent(ctx)
    _flank_condenser(ctx)
    _security_light(ctx)
    _solar_light(ctx)
    _east_condenser(ctx)
    _flue(ctx)
    _alley_lights(ctx)
    _corner_cables(ctx)
    _ground(ctx, fence)
    _climbers(ctx, fence)

"""Flight carcasses (blender/MULTILEVEL.md section 4.10): treads, risers and the raked soffit of a kind-'flight' stair,
from ctx.stair(id)['treads']. Called by shell.build for every flight. Strings, balustrades, newels, nosings and carpet
detail belong to the room modules; one that models its own flight calls shell.remove(<room>, 'flight') first."""
import math

from . import shell

WAIST = 0.12        # the soffit is this far (vertically) below the inner corner of each step; shell.UNDER_TREAD = WAIST - 0.01


def _dist(pt, line):
    (ax, ay), (bx, by) = line
    return abs((pt[0] - ax) * (by - ay) - (pt[1] - ay) * (bx - ax)) / math.hypot(bx - ax, by - ay)


def _edge(poly, line):
    """End points of the polygon's edge on a riser line, ordered along the line a -> b."""
    (ax, ay), (bx, by) = line
    pts = sorted((p for p in poly if _dist(p, line) < 1e-5), key=lambda p: (p[0] - ax) * (bx - ax) + (p[1] - ay) * (by - ay))
    return pts[0], pts[-1]


def _side(line, d):
    """Mid point of a riser line moved d to its left (the far side, towards toRoom); d < 0 = the near side."""
    (ax, ay), (bx, by) = line
    ln = math.hypot(bx - ax, by - ay)
    return (ax + bx) / 2 - (by - ay) / ln * d, (ay + by) / 2 + (bx - ax) / ln * d


def carcass(ctx, stair_id, solid=None):
    """Build the carcass object '<first through room>.flight' (kind 'shell', part 'flight') and return it.
    Treads and risers take the stairwell's covering (else its floor material), the underside its ceiling paint.
    solid (default: stair_id in shell.SOLID_FLIGHTS) = walls on both sides and mass below: treads and risers only.
    Otherwise every tread that has nothing solid under it gets the raked soffit (WAIST below the pitch line), side
    faces on its open edges and a back face where the soffit stops; steps that sit on mass are left to the grid."""
    s = ctx.stair(stair_id)
    assert s['kind'] == 'flight', stair_id
    solid = stair_id in shell.SOLID_FLIGHTS if solid is None else solid
    room, treads, rs = s['through'][0], s['treads'], s['walk']['risers']
    N, up, rise = len(rs), s['toZ'] > s['fromZ'], abs(s['rise'])
    lv = [s['fromZ']] + [t['z'] for t in treads] + [s['toZ']]          # level behind riser n = lv[n], n = 0 .. N
    low = -1 if up else 1                                              # side of a riser line the lower level is on
    r = ctx.rooms[room]
    step, under = (r.get('covering') or r['floor'])['material'], shell.finish(room)['ceiling']
    cen = lambda poly: (sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly))
    faces = [([(x, y, t['z']) for x, y in t['poly']], (*cen(t['poly']), t['z'] + 1), step) for t in treads]

    for n in range(1, N + 1):                                          # risers; riser n stands on line rs[n - 1]
        line = rs[n - 1]
        a, b = _edge(treads[min(n, N - 1) - 1]['poly'], line)
        lo, hi = sorted((lv[n - 1], lv[n]))
        m = _side(line, 0)
        # the riser against the upper landing (and the bottom riser of a solid flight, which stands on the passage
        # floor) coincides with a slab edge of the grid: 1 mm proud of it
        d = _side(line, low * 0.001) if n == (N if up else 1) or (solid and n == (1 if up else N)) else m
        ox, oy = d[0] - m[0], d[1] - m[1]
        faces.append(([(a[0] + ox, a[1] + oy, lo), (b[0] + ox, b[1] + oy, lo), (b[0] + ox, b[1] + oy, hi),
                       (a[0] + ox, a[1] + oy, hi)], (*_side(line, low), (lo + hi) / 2), step))
    if solid:
        return _finish(ctx, room, faces)

    zmin = min(s['fromZ'], s['toZ'])
    sof = [None] + [max(min(lv[n - 1], lv[n]) - WAIST, zmin) for n in range(1, N + 1)]     # soffit height on riser line n

    def zs(k, pt):                                                     # soffit of tread k under a plan point
        d0, d1 = _dist(pt, rs[k - 1]), _dist(pt, rs[k])
        w = 0.5 if d0 + d1 < 1e-9 else d0 / (d0 + d1)
        return sof[k] + w * (sof[k + 1] - sof[k])
    has = [False] * (N + 1)                                            # tread k hangs free (nothing solid under it)
    for k in range(1, N):
        c, z = cen(treads[k - 1]['poly']), treads[k - 1]['z']
        has[k] = not any(shell.is_solid(ctx, *c, z - 0.02 * i) for i in range(1, int((rise + WAIST) / 0.02) + 2))
    for k in range(1, N):
        if not has[k]:
            continue
        poly, z = treads[k - 1]['poly'], treads[k - 1]['z']
        c = cen(poly)
        p3 = [(x, y, zs(k, (x, y))) for x, y in poly]
        for i in range(1, len(p3) - 1):                                # the soffit may be warped at a winder: fan
            faces.append(([p3[0], p3[i], p3[i + 1]], (*c, z - 2), under))
        for (ax, ay, az), (bx, by, bz) in zip(p3, p3[1:] + p3[:1]):    # open side edges
            if any(_dist((ax, ay), l) < 1e-5 and _dist((bx, by), l) < 1e-5 for l in (rs[k - 1], rs[k])):
                continue
            ln = math.hypot(bx - ax, by - ay)
            if ln < 1e-6:
                continue
            ox, oy = (by - ay) / ln * 0.02, -(bx - ax) / ln * 0.02    # outward (treads are counter-clockwise)
            mx, my = (ax + bx) / 2, (ay + by) / 2
            if shell.is_solid(ctx, mx + ox, my + oy, z - 0.02) or shell.is_solid(ctx, mx - ox, my - oy, z - 0.02):
                continue                                               # a wall beside it or mass under it: grid face there
            faces.append(([(ax, ay, az), (bx, by, bz), (bx, by, z), (ax, ay, z)], (mx + ox * 50, my + oy * 50, z), under))
    for n in range(2, N + 1):
        if not has[n - 1]:
            continue
        line = rs[n - 1]
        a, b = _edge(treads[n - 2]['poly'], line)
        za, zb = zs(n - 1, a), zs(n - 1, b)
        if n < N and has[n]:                                           # step in the soffit at a winder newel
            ya, yb = zs(n, a), zs(n, b)
            if max(abs(ya - za), abs(yb - zb)) > 1e-6:
                far = (ya - za) + (yb - zb) > 0
                faces.append(([(*a, za), (*b, zb), (*b, yb), (*a, ya)], (*_side(line, 1 if far else -1), (za + zb) / 2), under))
        else:                                                          # the soffit stops here: close the back
            ox, oy = (v - w for v, w in zip(_side(line, 0.001), _side(line, 0)))
            top = max(lv[n - 1], lv[n])
            faces.append(([(a[0] + ox, a[1] + oy, za), (b[0] + ox, b[1] + oy, zb), (b[0] + ox, b[1] + oy, top),
                           (a[0] + ox, a[1] + oy, top)], (*_side(line, 1), top), under))
    return _finish(ctx, room, faces)


def _finish(ctx, room, faces):
    ob = ctx.add(shell.faces_object(f'{room}.flight', faces), room, 'shell')
    ob['part'] = 'flight'
    return ob

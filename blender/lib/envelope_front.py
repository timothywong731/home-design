"""Street-front trim for lib/envelope.py (MULTILEVEL.md 7). Numbers: spec/phase3/briefs/envelope.md (b) from v8 f26,
f29, f138 and t135 (gable), v9 t14. Everything is white masonry paint on the facade plane front_A (outward -y).

Ground-floor bay: reeded pilasters with base block and capital, the bay sill, a raised moulded architrave round each of
the eight lights, entablature (architrave band, plain frieze) and a four-fillet cornice returned along the east cheek and
the south-facing return. First floor: two hexagonal raised panels on the apron, window sill and hood mould, sunk panels in
the corner piers. Gable: head band, king post, curved braces and struts, bargeboards with scrolled feet. Porch: lead
upstand at the abutment. The party-wall kneeler comes from the exterior feature of type 'kneeler'."""
import math

from mathutils import Vector

from . import ctx as C
from . import envelope as E

W = 'white_masonry_paint'
# pilasters: (base block x0, x1, shaft x0, x1, wraps the cheek corner) - zones x 0.80..1.175 and 3.785..4.285
PILASTERS = [(0.80, 1.175, 0.83, 1.09, False), (3.785, 4.285, 3.83, 4.285, True)]
SHAFT_D, BASE_D, CAP = 0.05, 0.08, (2.58, 2.70, 0.075)   # projections; capital z0, z1, projection
REED = (0.04, 0.016, 0.085)            # convex reed: half width, projection, spacing (three per shaft)
BAY_SILL = (0.07, 0.08)                # thickness, projection (top = the bay window sill 0.62)
ARCH = [(0, 0), (0, 0.012), (0.012, 0.022), (0.03, 0.022), (0.04, 0.01), (0.04, 0)]   # (out from the light, proud)
ENT = (0.07, 0.035, 0.27, 0.02)        # band height, band projection, band + frieze height, frieze projection
CORNICE = [(0, 0), (0.04, 0), (0.04, 0.05), (0.07, 0.06), (0.10, 0.10), (0.12, 0.12), (0.12, 0.17), (0.15, 0.18),
           (0.18, 0.22), (0.20, 0.24), (0.20, 0.30), (0.18, 0.30), (0.18, 0.33), (0.14, 0.37), (0, 0.37)]  # 2.97..3.34
APRON = dict(dx=0.80, length=1.47, h=0.34, zc=3.64, tip=0.22, proud=0.015, bevel=0.012)
FF_SILL = [(0, 0), (0.05, 0), (0.07, 0.03), (0.07, 0.14), (0, 0.14)]          # (proud, up from its bottom)
HOOD = [(0, 0), (0.03, 0), (0.05, 0.02), (0.05, 0.10), (0.03, 0.14), (0, 0.14)]
PIER_PANEL = dict(inset=0.20, w=0.30, z=(4.08, 6.14), depth=0.015)
GABLE = dict(band=(6.35, 6.44), w=0.09, proud=0.025, brace_drop=0.45, board=0.22, board_t=0.03, toe=0.12)
# struts per half: (foot offset from the axis, foot z or None = band top, head offset, head z, bow); heads run on to
# the verge (v8 t135: the struts reach the bargeboards and bow toward the apex)
STRUTS = [(0.045, None, 0.75, 7.40, 0.06), (0.90, None, 1.20, 6.85, 0.04)]


def _strip(pts, w):
    """Outline (x, z) of a band of width w along a polyline."""
    left, right = [], []
    for i, p in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        d = (b - a).normalized()
        n = Vector((-d.y, d.x)) * (w / 2)
        left.append(p + n)
        right.append(p - n)
    return [tuple(q) for q in left + right[::-1]]


def _bezier(p0, p1, p2, n=8):
    return [p0 * (1 - t) ** 2 + p1 * 2 * t * (1 - t) + p2 * t * t for t in (i / n for i in range(n + 1))]


def _slab(m, P, y0, d, mat=W):
    """Polygon P in (x, z) on the plane y = y0, d proud toward -y."""
    if len(P) >= 3 and abs(C.poly_area(P)) > 1e-6:
        m.prism([(-x, z) for x, z in P], (0, y0, 0), (0, y0 - d, 0), mat)


def _architraves(m, P, lights, zs, ztr, zt):
    """Raised moulded architrave (ARCH, mitred) round each light of a two-tier window: three sides round the lower
    light (it stands on the sill), all four round the top light. P(s, z, proud) -> world point on the face."""
    for a, b in lights:
        m.rings([[P(s + os * u, z + oz * u, v) for u, v in ARCH]
                 for s, z, os, oz in ((a, zs, -1, 0), (a, ztr, -1, 1), (b, ztr, 1, 1), (b, zs, 1, 0))], W)
        z0 = ztr + E.TRANSOM
        rings = [[P(s + os * u, z + oz * u, v) for u, v in ARCH]
                 for s, z, os, oz in ((a, z0, -1, -1), (b, z0, 1, -1), (b, zt, 1, 1), (a, zt, -1, 1))]
        n = len(ARCH)
        for ra, rb in zip(rings, rings[1:] + rings[:1]):            # a closed ring: no caps
            for i in range(n):
                m.face([ra[i], ra[(i + 1) % n], rb[(i + 1) % n], rb[i]], W, None)


def _bay_lights(fr):
    n, lw, mu = fr['lights'], fr['lightWidth'], fr['mullion']
    x0 = fr['center'][0] - (n * lw + (n - 1) * mu) / 2
    return [(x0 + i * (lw + mu), x0 + i * (lw + mu) + lw) for i in range(n)]


def _ground_bay(ctx, m, fac, y0):
    """Pilasters, sill, light architraves, entablature and cornice of the ground-floor bay."""
    fr = ctx.opening_frame('w_bay_front')
    xe, yr, xr = fac['bay_cheek_e']['at'], fac['bay_cheek_e']['extent'][1], fac['east_E']['at']
    zs, zt, ztr = fr['z0'] + fr['sill'], fr['z0'] + fr['top'], fr['z0'] + fr['transom']['height']
    g = ctx.ground_z(fr['center'][0], y0 - 0.3)
    base = (g if g is not None else 0.0) - 0.04
    for x0, x1, s0, s1, wrap in PILASTERS:
        def block(xa, xb, d, za, zb, back):                        # on the front; a corner block wraps onto the cheek
            m.box((xa, y0 - d, za), (xb, y0, zb), W)
            if wrap:
                m.box((xe, y0, za), (xb, y0 + back, zb), W)
        block(x0, x1 + (0.015 if wrap else 0), BASE_D, base, zs, 0.06)   # backs on the cheek clear the downpipe
        block(s0, s1, SHAFT_D, zs, CAP[0], 0.05)                           # 0.10 behind the corner (y -0.02)
        block(x0 - 0.01, x1 + (0.02 if wrap else 0.01), CAP[2], CAP[0], CAP[1], 0.065)
        hw, pr, sp = REED
        reed = [(hw * math.cos(math.pi * i / 8), pr * math.sin(math.pi * i / 8)) for i in range(9)]
        for i in range(3):
            cx = (s0 + s1) / 2 + (i - 1) * sp
            m.prism(reed, (cx, y0 - SHAFT_D, zs + 0.10), (cx, y0 - SHAFT_D, CAP[0] - 0.10), W, up=(0, -1, 0))
    lights = _bay_lights(fr)
    t, out = BAY_SILL
    m.box((PILASTERS[0][1], y0 - out, zs - t), (PILASTERS[1][0], y0, zs), 'sill_stone')
    _architraves(m, lambda s, z, v: (s, y0 - v, z), lights, zs, ztr, zt)
    if 'w_bay_cheek_e' in ctx.openings:                             # the cheek window has the same surround
        fc = ctx.opening_frame('w_bay_cheek_e')
        yc, hw = fc['center'][1], fc['width'] / 2
        _architraves(m, lambda s, z, v: (xe + v, s, z), [(yc - hw, yc + hw)], fc['z0'] + fc['sill'],
                     fc['z0'] + fc['transom']['height'], fc['z0'] + fc['top'])
    # entablature: architrave band + plain frieze, then the cornice; along the front, the east cheek and the return
    path = [(PILASTERS[0][0] + 0.04, y0, 0, -1), (xe, y0, 1, -1), (xe, yr, 1, -1), (xr, yr, 0, -1)]
    hb, db, hf, df = ENT
    ent = [(0, 0), (db, 0), (db, hb), (df, hb), (df, hf), (0, hf)]
    m.rings([[(x + u * kx, y + u * ky, zt + v) for u, v in ent] for x, y, kx, ky in path], W)
    for x0, x1, *_ in PILASTERS:                                    # the pilasters run on through the frieze
        m.box((x0 - 0.01, y0 - 0.05, zt), (x1 + 0.01, y0, zt + hf), W)
    m.rings([[(x + u * kx, y + u * ky, zt + hf + v) for u, v in CORNICE] for x, y, kx, ky in path], W)


def _first_floor(ctx, m, fac, y0):
    """Apron panels, sill and hood of the first-floor bay window."""
    fr = ctx.opening_frame('w_green_bay')
    xc, hw = fr['center'][0], fr['width'] / 2
    zs, zt = fr['z0'] + fr['sill'], fr['z0'] + fr['top']
    a = APRON
    for sg in (-1, 1):
        cx, L, h, tip = xc + sg * a['dx'], a['length'] / 2, a['h'] / 2, a['tip']
        hexa = lambda k: [(cx - L + k * 1.6, a['zc']), (cx - L + tip + k, a['zc'] - h + k), (cx + L - tip - k, a['zc'] - h + k),
                          (cx + L - k * 1.6, a['zc']), (cx + L - tip - k, a['zc'] + h - k), (cx - L + tip + k, a['zc'] + h - k)]
        lo, hi = hexa(0), hexa(a['bevel'])
        yb, yf = y0, y0 - a['proud']
        m.face([(x, yf, z) for x, z in hi], W, (0, -1, 0))
        m.face([(x, yb, z) for x, z in lo], W, (0, 1, 0))
        for i in range(6):
            j = (i + 1) % 6
            m.face([(lo[i][0], yb, lo[i][1]), (lo[j][0], yb, lo[j][1]), (hi[j][0], yf, hi[j][1]), (hi[i][0], yf, hi[i][1])], W)
    m.prism(FF_SILL, (xc - hw - 0.07, y0, zs - FF_SILL[-1][1]), (xc + hw + 0.07, y0, zs - FF_SILL[-1][1]), 'sill_stone')
    m.prism(HOOD, (xc - hw - 0.05, y0, zt), (xc + hw + 0.05, y0, zt), W)


def _cheek_e(ctx, m, fac):
    """East cheek, first floor: hood over the window and a small raised panel on the apron below it (v8 f64-70)."""
    if 'w_green_cheek_e' not in ctx.openings:
        return
    fr = ctx.opening_frame('w_green_cheek_e')
    x, yc, hw = fac['bay_cheek_e']['at'], fr['center'][1], fr['width'] / 2
    zt = fr['z0'] + fr['top']
    m.prism(HOOD, (x, yc - hw - 0.05, zt), (x, yc + hw + 0.05, zt), W)       # travel +y: the profile's +u is +x
    L, h = 0.24, 0.12                                               # half length, half height
    P = [(yc - L, APRON['zc']), (yc - L + h, APRON['zc'] - h), (yc + L - h, APRON['zc'] - h), (yc + L, APRON['zc']),
         (yc + L - h, APRON['zc'] + h), (yc - L + h, APRON['zc'] + h)]
    ring = [(x + APRON['proud'], y, z) for y, z in P]
    m.face(ring, W, (1, 0, 0))
    base = [(x, y, z) for y, z in P]
    for i in range(6):
        j = (i + 1) % 6
        m.face([base[i], base[j], ring[j], ring[i]], W)
    m.face(base, W, (-1, 0, 0))


def pier_panels(ctx, meshes):
    """Sunk panels in the first-floor corner piers: the recessed back and four returns go into front_A's mesh; returns
    the pseudo-openings that make _skin leave the holes."""
    fac = {f['id']: f for f in ctx.spec['exterior']['facades']}
    if not {'front_A', 'bay_cheek_w', 'bay_cheek_e'} <= fac.keys():
        return []
    f, p = fac['front_A'], PIER_PANEL
    y0, m, holes = f['at'], meshes.setdefault('front_A', E._Mesh()), []
    z0, z1 = p['z']
    for xa in (fac['bay_cheek_w']['at'] + p['inset'], fac['bay_cheek_e']['at'] - p['inset'] - p['w']):
        xb, yb = xa + p['w'], y0 + p['depth']
        m.face([(xa, yb, z0), (xb, yb, z0), (xb, yb, z1), (xa, yb, z1)], f['finish'], (0, -1, 0))
        for pts, n in (([(xa, y0, z0), (xa, yb, z0), (xa, yb, z1), (xa, y0, z1)], (1, 0, 0)),
                       ([(xb, y0, z0), (xb, yb, z0), (xb, yb, z1), (xb, y0, z1)], (-1, 0, 0)),
                       ([(xa, y0, z0), (xb, y0, z0), (xb, yb, z0), (xa, yb, z0)], (0, 0, 1)),
                       ([(xa, y0, z1), (xb, y0, z1), (xb, yb, z1), (xa, yb, z1)], (0, 0, -1))):
            m.face(pts, f['finish'], n)
        holes.append(dict(id='panel', fr=dict(outward=(0.0, -1.0), width=p['w']), p0=(xa + p['w'] / 2, y0), z0=z0, z1=z1))
    return holes


def _gable(ctx, m, fac, y0):
    """Head band, timbering (king post, braces, struts) under the verge, and the two bargeboards."""
    g = ctx.spec['roof'].get('gable')
    gp = [p for p in ctx.spec['roof']['planes'] if g and p['id'].startswith(g['id'])]
    if len(gp) != 2:
        return
    G = GABLE
    west, east = max(gp, key=lambda p: p['z']['cx']), min(gp, key=lambda p: p['z']['cx'])
    t, xr = ctx.roof_slab_t(west['id']), g['ridge'][0][0]
    xw, xe = fac['bay_cheek_w']['at'], fac['bay_cheek_e']['at']
    zv = lambda pl, x: C.plane_z(pl, x, y0) - t                    # verge underside (soffit) on the wall
    under = lambda P: C.clip_poly(C.clip_poly(P, (0, zv(west, 0)), (1, zv(west, 1)), left=False),
                                  (0, zv(east, 0)), (1, zv(east, 1)), left=False)
    zb0, zb1 = G['band']
    _slab(m, under([(xw, zb0), (xe, zb0), (xe, zb1), (xw, zb1)]), y0, G['proud'])
    w = G['w']
    apex = zv(west, xr)
    _slab(m, under([(xr - w / 2, zb1), (xr + w / 2, zb1), (xr + w / 2, apex + 0.1), (xr - w / 2, apex + 0.1)]), y0, G['proud'])
    for sg, pl in ((-1, west), (1, east)):
        half = lambda P: C.clip_poly(P, (xr + sg * w / 2, 0), (xr + sg * w / 2, 1), left=sg < 0)
        z0 = apex - G['brace_drop']                                 # the two curved braces under the apex
        p0, p2 = Vector((xr, z0)), Vector((xr + sg * 0.25, zv(pl, xr + sg * 0.25) + 0.05))
        _slab(m, half(under(_strip(_bezier(p0, Vector((xr + sg * 0.05, apex - 0.25)), p2), w))), y0, G['proud'])
        for fo, fz, ho, hz, bow in STRUTS:
            p0 = Vector((xr + sg * fo, zb1 - 0.02 if fz is None else fz))
            d = (Vector((xr + sg * ho, hz)) - p0).normalized()
            s = 0.0                                                 # run on to the verge
            while p0.y + d.y * s < zv(pl, p0.x + d.x * s) + 0.05 and s < 4:
                s += 0.01
            p2 = p0 + d * s
            p1 = (p0 + p2) / 2 + Vector((-d.y, d.x)) * (bow * sg)  # bow toward the apex
            _slab(m, half(under(_strip(_bezier(p0, p1, p2), w))), y0, G['proud'])
        # bargeboard on the verge, in front of the slab edge, with a scrolled foot
        yv = min(q[1] for q in pl['polygon'])
        xf = (min if sg < 0 else max)(q[0] for q in pl['polygon'])
        D = G['board'] / math.cos(math.atan(abs(pl['z']['cx'])))
        top = lambda x: C.plane_z(pl, x, yv) + 0.03
        bot = lambda x: top(x) - D
        toe = [(xf - sg * 0.30 * (1 - k / 6), bot(xf - sg * 0.30 * (1 - k / 6)) - G['toe'] * math.sin(math.pi / 2 * k / 6))
               for k in range(7)]
        P = [(xf, top(xf)), (xr, top(xr)), (xr, bot(xr))] + toe
        _slab(m, P, yv, G['board_t'])


def _porch(ctx, m, fac):
    """Where the lean-to meets the first floor (v8 f126): lead upstand 0.15 high along front_B with an apron down the
    slates, a raking flashing up the bay west cheek, and the cheek face down to the slates below the first floor."""
    p = next((q for q in ctx.spec['roof']['planes'] if q.get('level') == 'G'), None)
    if p is None or 'front_B' not in fac:
        return
    fb, xc, y0 = fac['front_B'], fac['bay_cheek_w']['at'], fac['front_A']['at']
    ya = fb['at']
    xs = [q[0] for q in p['polygon']]
    x0, x1 = max(min(xs), fb['extent'][0]), min(max(xs), fb['extent'][1])
    z = C.plane_z(p, x0, ya)
    m.box((x0, ya - 0.012, z - 0.01), (x1, ya, z + 0.15), 'lead_dark')
    dz = p['z']['cy'] * 0.12                                        # apron lapping 0.12 down the slates
    m.face([(x0, ya - 0.012, z + 0.005), (x1, ya - 0.012, z + 0.005), (x1, ya - 0.13, z - dz + 0.005), (x0, ya - 0.13, z - dz + 0.005)],
           'lead_dark', (0, 0, 1))
    zl = lambda y: C.plane_z(p, xc, y)
    zf = next((v['z'][0] for b in ctx.spec['exterior']['envelope']['blocks'] for v in b['levels']
               if v['level'] == '1' and C.point_in_poly(xc + 0.05, (y0 + ya) / 2, v['polygon'])), None)
    if zf is None:
        return
    yt = min(ya, (zf - p['z']['c0']) / p['z']['cy'])                # where the slates pass the first-floor line
    if yt > y0:
        m.face([(xc, y0, zl(y0)), (xc, yt, zl(yt)), (xc, y0, zf)], W, (-1, 0, 0))
    m.prism([(-0.012, 0), (0.0, 0), (0.0, 0.14), (-0.012, 0.14)], (xc, y0, zl(y0) - 0.01), (xc, ya, zl(ya) - 0.01), 'lead_dark')


def kneelers(ctx):
    """Party-wall kneeler: brick stub on the party line at the eaves, corbelled out in five courses, sloping cap."""
    objs = []
    for f in ctx.spec['exterior'].get('features', []):
        if f['type'] != 'kneeler':
            continue
        xs, ys = [q[0] for q in f['polygon']], [q[1] for q in f['polygon']]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        z0, z1 = f['z']
        m, mat, c = E._Mesh(), f.get('material', 'red_brick_dark'), 0.075
        yb = y0 + 0.28                                              # face of the shaft below the corbel
        m.box((x0, yb, z0), (x1, y1, z0 + c), mat)
        for i in range(5):
            m.box((x0, yb - 0.056 * (i + 1), z0 + c * (i + 1)), (x1, y1, z0 + c * (i + 2)), mat)
        zc = z1 - 0.08
        m.box((x0, y0, z0 + c * 6), (x1, y1, zc), mat)
        m.prism([(-0.02, 0), (y1 - y0 + 0.02, 0), (y1 - y0 + 0.02, 0.10), (-0.02, 0.06)],
                (x0 - 0.02, y1, zc), (x1 + 0.02, y1, zc), 'slate')  # cap sloping toward the street
        ob = m.obj(ctx, f"facade.{f['id']}", 'facade', 'trim', solid=True)
        if ob:
            objs.append(ob)
    return objs


def build(ctx):
    """-> (objects, opening ids whose sill this module builds)."""
    fac = {f['id']: f for f in ctx.spec['exterior']['facades']}
    if not {'front_A', 'bay_cheek_w', 'bay_cheek_e', 'east_E'} <= fac.keys():
        return kneelers(ctx), set()
    y0, m = fac['front_A']['at'], E._Mesh()
    _ground_bay(ctx, m, fac, y0)
    _first_floor(ctx, m, fac, y0)
    _gable(ctx, m, fac, y0)
    _porch(ctx, m, fac)
    _cheek_e(ctx, m, fac)
    return [m.obj(ctx, 'facade.front_A.trim', 'facade', 'trim', solid=True)] + kneelers(ctx), {'w_bay_front', 'w_green_bay'}

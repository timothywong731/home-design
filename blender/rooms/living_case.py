"""Living room: case furniture, chairs and tables (imported by rooms/living.py). Conventions as living_parts."""
import math
import bpy
from math import sin, cos, pi, radians, tau, sqrt
from mathutils import Matrix, Vector
from lib import materials as M, mouldings as mo, props as P
from living_parts import (Tr, Rz, Rx, Ry, MIRX, kid, loft, rrect, circ, slab, pad, gimp_band, OGEE, wood, GIMP, velvet,
                          tube_var, rtube)


def gadroon(mb, pts, mat, r=0.009, h=0.03, lean=0.012):
    """Rope-twist edge: one slanted lobe at every point (x, y, z, (tx, ty)) leaning along the tangent."""
    for x, y, z, (tx, ty) in pts:
        mb.tube([(x - tx * lean / 2, y - ty * lean / 2, z), (x + tx * lean / 2, y + ty * lean / 2, z + h)], r, mat, 6)


# ----------------------------------------------------------------------------------------- bookcase
def _tracery(mb, x0, x1, z0, z1, y, mat, r=0.0045):
    """Gothic astragals of one glazed door: two bars making three lights, every bar and both jambs branching
    into arcs of radius 1.5 x light width that cross into interlaced pointed arches under the top rail."""
    lw = (x1 - x0) / 3
    R = 1.5 * lw
    rise = min(0.15, 0.9 * R)
    zs = z1 - rise
    for k in (1, 2):
        mb.tube([(x0 + k * lw, y, z0), (x0 + k * lw, y, zs)], r, mat, 4)
    amax = math.asin(rise / R)
    for k in range(4):
        xk = x0 + k * lw
        for sg in (-1, 1):                       # sg=1: branch leaning toward +x (centre on the +x side)
            pts = []
            for i in range(9):
                a = amax * i / 8
                x = xk + sg * (R - R * cos(a))
                if x < x0 - 1e-6 or x > x1 + 1e-6:
                    break
                pts.append((x, y, zs + R * sin(a)))
            if len(pts) > 1:
                rtube(mb, pts, r, mat, 4)


# spines as in f_0185 / f_0785: mostly pale paperbacks with reds, blues and greens (the lib default is dark leather)
BOOKS = ['#E9E2D0', '#F1EEE6', '#D9CDB0', '#B8433A', '#9A3A32', '#3C5E8C', '#4A7684', '#4D7355', '#C9A24E', '#E3D9C2',
         '#7A2E2A', '#2C3A46', '#C9B88A', '#F4F1EA', '#A8603C', '#6C86A4', '#EDE6D6', '#DDD3BC']


BOOKCASE_DEG = (-95, 88, -88, 95)      # door swing, state 0 -> 1: the inner pair hinges on the 30 mm centre stile, so
#                                        both stop just short of square (at 95 they would cross); the bench is ~1 m away


def bookcase(name='living.bookcase'):
    """Glazed dark brown-black bookcase 1.75 x 0.36 x 1.22 with a brown polished top: gadrooned edge, four astragal-glazed doors, cabriole
    ball-and-claw legs, two shelves of books. Returns (root, doors): every door is its own frame + glass object
    (children of root, modelled shut) for the interaction tags - doors = [(objects that swing together, hinge
    point on the floor in the root's frame, degrees about +Z that open it)]; hinges on the end stiles and the
    centre stile, escutcheons on the meeting stiles, the key tassel hangs from door 1."""
    mb = mo.MB()
    W = wood()
    hx, yf, yb = 0.875, -0.18, 0.18
    z_pl, z_c0, z_c1 = 0.20, 0.26, 1.15
    mb.box((-hx + 0.005, yf + 0.004, z_pl), (hx - 0.005, yb, z_c0 + 0.005), W, bev=0.005, grain=0)      # plinth rail
    for sx in (-1, 1):                                                                               # sides, back legs
        mb.box((sx * hx, yf + 0.02, z_c0), (sx * (hx - 0.02), yb, z_c1), W, bev=0.002, grain=2)
        mb.box((sx * 0.84 - 0.024, 0.13, 0), (sx * 0.84 + 0.024, 0.178, z_pl), W, bev=0.003, grain=2)
    mb.box((-hx + 0.02, yb - 0.008, z_c0), (hx - 0.02, yb, z_c1), W, grain=2)                          # back
    mb.face([(-hx + 0.021, yb - 0.009, z_c0 + 0.02), (hx - 0.021, yb - 0.009, z_c0 + 0.02), (hx - 0.021, yb - 0.009, z_c1 - 0.02),
             (-hx + 0.021, yb - 0.009, z_c1 - 0.02)], 'oak_table', (0, -1, 0), grain=2)                 # mid-brown lining
    mb.box((-hx + 0.02, yf + 0.02, z_c0), (hx - 0.02, yb - 0.008, z_c0 + 0.02), W, grain=0)            # bottom
    mb.box((-hx + 0.02, yf + 0.02, z_c1 - 0.02), (hx - 0.02, yb - 0.008, z_c1), W, grain=0)            # top board
    mb.box((-0.01, yf + 0.04, z_c0 + 0.02), (0.01, yb - 0.008, z_c1 - 0.02), W, grain=2)               # partition
    shelves = (0.545, 0.81)
    for zs in shelves:
        mb.box((-hx + 0.02, yf + 0.045, zs - 0.018), (hx - 0.02, yb - 0.008, zs), W, grain=0)
    # face frame: end stiles, centre stile, bottom rail, frieze
    z_d0, z_d1 = z_c0 + 0.015, 1.085
    for sx in (-1, 1):
        mb.box((sx * hx, yf, z_c0), (sx * (hx - 0.025), yf + 0.022, z_c1), W, bev=0.002, grain=2)
    mb.box((-0.015, yf, z_c0), (0.015, yf + 0.022, z_c1), W, bev=0.002, grain=2)
    mb.box((-hx + 0.025, yf, z_c0), (hx - 0.025, yf + 0.022, z_d0), W, grain=0)
    mb.box((-hx + 0.025, yf, z_d1), (hx - 0.025, yf + 0.022, z_c1), W, bev=0.002, grain=0)
    # cornice moulding + top slab with the gadrooned edge; polished mid-brown top surface
    mb.sweep([(0.0, 0.0), (0.006, 0.0), (0.012, 0.012), (0.012, 0.022), (0.02, 0.035), (0.0, 0.035)],
             [(hx, yb, z_c1), (hx, yf, z_c1), (-hx, yf, z_c1), (-hx, yb, z_c1)], W)
    zt0, zt1 = z_c1 + 0.035, 1.22
    mb.box((-hx - 0.012, yf - 0.012, zt0), (hx + 0.012, yb, zt1), W, bev=0.003, grain=0)
    mb.face([(-hx - 0.008, yf - 0.008, zt1 + 0.0012), (hx + 0.008, yf - 0.008, zt1 + 0.0012),
             (hx + 0.008, yb - 0.004, zt1 + 0.0012), (-hx - 0.008, yb - 0.004, zt1 + 0.0012)], 'oak_table', (0, 0, 1), grain=0)
    pts = []
    n = int((2 * hx + 0.02) / 0.021)
    for i in range(n + 1):
        pts.append((-hx - 0.01 + (2 * hx + 0.02) * i / n, yf - 0.014, zt0 + 0.002, (1, 0)))
    m = int((yb - yf) / 0.021)
    for i in range(1, m + 1):
        y = yf - 0.012 + (yb - yf) * i / m
        pts.append((-hx - 0.014, y, zt0 + 0.002, (0, -1)))
        pts.append((hx + 0.014, y, zt0 + 0.002, (0, 1)))
    gadroon(mb, pts, W, r=0.0085, h=zt1 - zt0 - 0.004, lean=0.014)
    # doors
    dw = (2 * hx - 0.05 - 0.03) / 4
    xs = [-hx + 0.025, -hx + 0.025 + dw, 0.015, 0.015 + dw]
    fr = 0.045
    root = mb.finish(name)
    doors = []
    for i, x0 in enumerate(xs):
        x1 = x0 + dw
        ya, yb2 = yf - 0.003, yf + 0.019
        db = mo.MB()
        db.box((x0 + 0.001, ya, z_d0), (x0 + fr, yb2, z_d1), W, bev=0.003, grain=2)
        db.box((x1 - fr, ya, z_d0), (x1 - 0.001, yb2, z_d1), W, bev=0.003, grain=2)
        db.box((x0 + fr, ya, z_d0), (x1 - fr, yb2, z_d0 + fr), W, bev=0.003, grain=0)
        db.box((x0 + fr, ya, z_d1 - fr), (x1 - fr, yb2, z_d1), W, bev=0.003, grain=0)
        _tracery(db, x0 + fr, x1 - fr, z_d0 + fr, z_d1 - fr, yf + 0.006, W)
        xe = x1 - 0.022 if i % 2 == 0 else x0 + 0.022                      # escutcheon on the meeting stile
        db.at(Tr(xe, ya, 0.70) @ Rx(90))
        db.lathe([(0, 0), (0.009, 0), (0.009, 0.002), (0.004, 0.004), (0, 0.004)], 'brass', 8)
        db.at()
        g = mo.MB()
        px0, px1, pz0, pz1 = x0 + fr - 0.004, x1 - fr + 0.004, z_d0 + fr - 0.004, z_d1 - fr + 0.004
        g.face([(px0, yf + 0.008, pz0), (px1, yf + 0.008, pz0), (px1, yf + 0.008, pz1), (px0, yf + 0.008, pz1)],
               M.mat('glass_clear'), (0, -1, 0))
        parts = [db.finish(f'{name}.door.{i}'), g.finish(f'{name}.door.{i}.glass')]
        for ob in parts:
            ob.parent = root
        hinge = x0 + 0.001 if i % 2 == 0 else x1 - 0.001                   # opposite the escutcheon, front arris
        doors.append((parts, (hinge, ya, 0.0), BOOKCASE_DEG[i]))
    for i, (x, out) in enumerate(((-0.84, (-1, -1)), (0.0, (0, -1)), (0.84, (1, -1)))):
        leg = P.turned_leg(z_pl, 0.05, 'cabriole', top_block=0.05, out=out, foot='claw', mat=W, name=f'{name}.leg.{i}')
        kid(root, leg, (x, yf + 0.03, 0))
    doors[1][0].append(kid(root, P.tassel(0.10, 0.018, name=name + '.key_tassel'), (xs[1] + 0.022, yf - 0.012, 0.69)))
    # books: three tiers in two bays
    tiers = (z_c0 + 0.02, shelves[0], shelves[1])
    k = 0
    for zt, hgt in zip(tiers, (0.235, 0.225, 0.20)):
        for sx in (-1, 1):
            row = P.book_row(0.80, hgt, 0.17, seed=20 + k, fill=0.93 if k % 3 else 1.0, palette=BOOKS,
                             name=f'{name}.books.{k}')
            kid(root, row, (sx * 0.435, yf + 0.215, zt))                    # spines 37 mm behind the glass
            k += 1
    return root, doors


# ------------------------------------------------------------------------- torchere and lamp table
def torchere(name='living.pedestal', mat='mahogany_dark'):
    """Very dark mahogany torchere 0.95 high: dished 0.32 top with moulded rim, round turned baluster column
    with ring collars, wide cabriole tripod (pad feet 0.19 from the axis)."""
    prof = [(0, 0.165), (0.014, 0.165), (0.032, 0.18), (0.05, 0.205), (0.055, 0.245), (0.05, 0.283), (0.03, 0.30),   # boss
            (0.036, 0.308), (0.036, 0.322), (0.025, 0.332),                                                           # collar
            (0.03, 0.37), (0.043, 0.43), (0.047, 0.48), (0.041, 0.53), (0.027, 0.58),                                 # vase
            (0.022, 0.598), (0.034, 0.608), (0.034, 0.624), (0.022, 0.634),                                           # collar
            (0.019, 0.70), (0.019, 0.775), (0.024, 0.795), (0.035, 0.805), (0.035, 0.821), (0.024, 0.831),            # shaft, collar
            (0.03, 0.86), (0.05, 0.885), (0.078, 0.902),
            (0.148, 0.915), (0.16, 0.925), (0.16, 0.944), (0.153, 0.95), (0.146, 0.938), (0, 0.934)]                  # dished top
    root = P.lathe(prof, 28, mat, name=name)
    mb = mo.MB()
    mb._soft = 1
    for i in range(3):
        a = tau * i / 3 + pi / 2
        c, s = cos(a), sin(a)
        leg = [(0.03, 0.262), (0.065, 0.262), (0.105, 0.215), (0.135, 0.13), (0.158, 0.055), (0.185, 0.02)]
        tube_var(mb, [(r * c, r * s, z) for r, z in leg], [0.021, 0.023, 0.02, 0.017, 0.015, 0.019], mat, 12)
        mb.at(Tr(0.188 * c, 0.188 * s, 0))
        mb.lathe([(0, 0), (0.02, 0), (0.026, 0.008), (0.022, 0.022), (0, 0.03)], mat, 12)
        mb.at()
    legs = mb.finish(name + '.legs')
    legs.parent = root
    return root


def lamp_table(name='living.lamp_table', top='mahogany_mid', mat=None):
    """Round brown lamp table dia 0.62 x 0.64: polished mid-brown top of plain straight-grained boards, darker
    carved (gadrooned) edge band, plain apron, four splayed square tapered legs with spade feet."""
    mb = mo.MB()
    mat = mat or wood()
    mb.lathe([(0, 0.60), (0.285, 0.60), (0.303, 0.606), (0.303, 0.634), (0.296, 0.6385), (0, 0.6385)], mat, 40)
    mb.face(circ(0.292, 0.64, 40), top, (0, 0, 1), grain=0)                    # planar UVs: grain straight across
    pts = []
    for i in range(110):
        a = tau * i / 110
        pts.append((0.3035 * cos(a), 0.3035 * sin(a), 0.609, (-sin(a), cos(a))))
    gadroon(mb, pts, mat, r=0.0055, h=0.022, lean=0.008)
    mb.lathe([(0.235, 0.545), (0.25, 0.545), (0.25, 0.60), (0.235, 0.60)], mat, 32)
    for i in range(4):
        a = tau * (i + 0.5) / 4
        c, s = cos(a), sin(a)
        rings = []
        for rad, half, z in ((0.262, 0.012, 0.0), (0.258, 0.018, 0.045), (0.254, 0.0115, 0.075), (0.21, 0.017, 0.60)):
            rings.append([(rad * c + half * (dx * c - dy * s), rad * s + half * (dx * s + dy * c), z)
                          for dx, dy in ((1, 1), (-1, 1), (-1, -1), (1, -1))])
        loft(mb, rings, mat)
    return mb.finish(name)


# ----------------------------------------------------------------------------------------- armchair
def armchair(name='living.armchair'):
    """Late-Victorian carved parlour armchair 0.65 x 0.67 x 1.03 (seat 0.39, arm pads 0.65), low and wide:
    seat wider at the front with a fixed stuffed-over seat and gimp inside the rails; back raked 10 deg with
    ring-turned finial posts, a shaped scrolled cresting rail with a carved shell and an upholstered panel edged
    in cream cord; open arms on turned supports ending in knobs, full velvet pads centred on the arm rails;
    stacked-ring front legs, raked back legs."""
    mb = mo.MB()
    W, V = wood(), velvet()
    HF, HB, YF, YB = 0.275, 0.225, -0.33, 0.22            # seat half-width front / back, front / back edge
    hd, yc, k = (YB - YF) / 2, (YB + YF) / 2, HB / HF
    mb.prism([(-HF, YF, 0.20), (HF, YF, 0.20), (HB, YB, 0.20), (-HB, YB, 0.20)], (0, 0, 0.085), W, grain=0)   # seat rails
    mb.at(Tr(0, yc, 0))
    pad(mb, HF - 0.012, hd - 0.012, 0.05, 0.27, 0.35, V, crown=0.045, n=5, taper=k)                 # sprung, domed seat
    gimp_band(mb, HF - 0.012, hd - 0.012, 0.05, 0.283, 0.012, n=5, taper=k)
    fl = [(0, 0), (0.02, 0), (0.028, 0.01), (0.028, 0.028), (0.019, 0.04), (0.033, 0.062), (0.036, 0.08), (0.033, 0.098),
          (0.021, 0.112), (0.03, 0.13), (0.035, 0.15), (0.035, 0.175), (0.026, 0.19), (0.026, 0.20), (0, 0.20)]
    post = [(0, -0.02), (0.022, -0.02), (0.022, 0.08), (0.016, 0.095), (0.026, 0.11), (0.026, 0.13), (0.016, 0.145),
            (0.019, 0.28), (0.026, 0.295), (0.017, 0.31), (0.019, 0.50), (0.027, 0.515), (0.027, 0.54), (0.017, 0.555),
            (0.024, 0.58), (0.024, 0.62), (0.013, 0.632), (0.021, 0.652), (0.027, 0.675), (0.021, 0.70), (0.008, 0.72),
            (0.012, 0.735), (0, 0.752)]
    sup = [(0, 0), (0.02, 0), (0.02, 0.02), (0.013, 0.035), (0.022, 0.06), (0.026, 0.10), (0.022, 0.14), (0.013, 0.17),
           (0.018, 0.19), (0.018, 0.21), (0.013, 0.225), (0.017, 0.28), (0, 0.28)]
    B = Tr(0, YB - 0.01, 0.285) @ Rx(-10)                             # raked back frame: local z runs up the back
    for sx in (-1, 1):
        mb.at(Tr(sx * (HF - 0.03), YF + 0.033, 0))
        mb.lathe(fl, W, 16)
        mb.at()
        x0 = sx * 0.205 - 0.022
        mb.prism([(x0, 0.172, 0.20), (x0, 0.22, 0.20), (x0, 0.312, 0.0), (x0, 0.27, 0.0)], (0.044, 0, 0), W, grain=2)   # back leg
        mb.at(B @ Tr(sx * 0.238, 0, 0))
        mb.lathe(post, W, 16)
        mb.at(B)
        mb.box((sx * 0.222, -0.014, 0.085), (sx * 0.178, 0.014, 0.62), W, bev=0.003, grain=2)       # back stiles
        # open arm: turned support with knob, rail back to the post, velvet pad centred on the rail
        fx, fy, bx, by = sx * 0.28, -0.29, sx * 0.24, 0.262
        mb.at(Tr(fx, fy + 0.012, 0.285))
        mb.lathe(sup, W, 14)
        mb.at()
        loft(mb, [[(bx + dx, by, 0.588 + dz) for dx, dz in ((-0.02, -0.014), (0.02, -0.014), (0.02, 0.014), (-0.02, 0.014))],
                  [(fx + dx, fy, 0.578 + dz) for dx, dz in ((-0.023, -0.016), (0.023, -0.016), (0.023, 0.016), (-0.023, 0.016))]], W)
        mb.at(Tr(fx, fy - 0.012, 0.582))
        mb.lathe([(0, -0.027), (0.016, -0.021), (0.027, 0), (0.016, 0.021), (0, 0.027)], W, 14)      # hand knob
        mb.at(Tr(fx + (bx - fx) * 0.3, fy + (by - fy) * 0.3, 0.592) @ Rz(sx * 4.1))
        pad(mb, 0.045, 0.125, 0.03, 0.0, 0.06, V, crown=0.006, n=3)
        gimp_band(mb, 0.045, 0.125, 0.03, 0.0, 0.012)
    mb.at(B)
    mb.box((-0.222, -0.014, 0.085), (0.222, 0.014, 0.132), W, bev=0.003, grain=0)                  # lower back rail
    crest = [(0.218, 0.61), (0.218, 0.668), (0.203, 0.684), (0.178, 0.686), (0.162, 0.674), (0.145, 0.69), (0.115, 0.712),
             (0.075, 0.724), (0.035, 0.731), (0.0, 0.733)]                                          # scrolled shoulders, low arch
    crest = [(-x, z) for x, z in crest] + crest[-2::-1]
    mb.prism([(x, -0.016, z) for x, z in crest], (0, 0.032, 0), W, grain=0)                         # shaped cresting rail
    mb.box((-0.18, 0.0, 0.13), (0.18, 0.016, 0.61), V)                                              # outside back
    mb.at(B @ Tr(0, -0.004, 0.37) @ Rx(90))
    pad(mb, 0.18, 0.24, 0.02, 0.0, 0.04, V, crown=0.02, n=3)                                        # back panel
    mb.tube(rrect(0.182, 0.242, 0.022, 0.008, 3), 0.0065, GIMP, 6, closed=True)                     # cream cord round it
    for a in (-78, -52, -26, 0, 26, 52, 78):                                                       # carved shell
        mb.at(B @ Tr(0, -0.0165, 0.636) @ Rx(90) @ Rz(a))
        mb.leaf(0.082 if a == 0 else 0.074 - abs(a) * 0.0002, 0.034, 0.012, W, 5, round_=0.7)
    for sx in (-1, 1):                                                                             # volute bosses
        mb.at(B @ Tr(sx * 0.19, -0.016, 0.662) @ Rx(90))
        mb.dome(0.02, 0.02, 0.01, W, 10, 3)
    for sx in (-1, 1):                                                                             # C-scrolls
        mb.at(B)
        pts = []
        for j in range(13):
            t = j / 12
            a = radians(200 - 300 * t)
            rr = 0.028 - 0.014 * t
            pts.append((sx * (0.165 + rr * cos(a)), -0.0185, 0.642 + rr * sin(a)))
        rtube(mb, pts, 0.005, W, 5)
        rtube(mb, [(sx * 0.13, -0.0185, 0.63), (sx * 0.065, -0.0185, 0.618)], 0.005, W, 5)
    mb.at()
    return mb.finish(name)


# ---------------------------------------------------------------------------------- TV unit, A/C
def tv_unit(name='living.tv_unit', mat='oak_rustic'):
    """Rustic oak TV unit 1.80 x 0.45 x 0.56: plank top, square posts, door | shelf over drawer | door,
    black thumb latches on the doors, a black cup pull on the drawer. Returns (root, ix) with everything parented to root; ix holds the parts for the
    interaction tags, points / vectors in the root's frame: doors = [(objects, hinge point, degrees about +Z)]
    (hinged on the outer posts, pulls toward the middle), drawer = (objects, slide vector) - front, pull and a
    real drawer box with a few things in it - and inner = what the doors reveal (a lined carcass with a shelf in
    each cupboard, books and boxes)."""
    mb = mo.MB()
    yf, yb = -0.225, 0.225
    mb.box((-0.915, yf - 0.015, 0.53), (0.915, yb, 0.56), mat, bev=0.006, grain=0)
    for x in (-0.865, -0.395, 0.395, 0.865):
        mb.box((x - 0.035, yf, 0), (x + 0.035, yf + 0.07, 0.53), mat, bev=0.004, grain=2)
        mb.box((x - 0.035, yb - 0.07, 0), (x + 0.035, yb, 0.53), mat, bev=0.004, grain=2)
        mb.box((x - 0.012, yf + 0.07, 0.08), (x + 0.012, yb - 0.07, 0.53), mat, grain=1)             # side / partition
    mb.box((-0.83, yb - 0.02, 0.08), (0.83, yb - 0.008, 0.53), mat, grain=0)                         # back
    mb.box((-0.83, yf + 0.01, 0.08), (0.83, yb - 0.02, 0.10), mat, grain=0)                          # bottom
    mb.box((-0.83, yf + 0.008, 0.495), (0.83, yf + 0.03, 0.53), mat, grain=0)                        # top rail
    mb.box((-0.83, yf + 0.008, 0.06), (0.83, yf + 0.03, 0.10), mat, grain=0)                         # bottom rail
    mb.box((-0.36, yf + 0.01, 0.262), (0.36, yb - 0.02, 0.282), mat, grain=0)                        # shelf
    root = mb.finish(name)
    doors, inner = [], []
    lb = mo.MB()                                      # black thumb latch on the closing stile of each door (v2:f_0833)
    Bk = M.mat('black_matt')
    lb.box((-0.008, -0.003, -0.018), (0.008, 0.0, 0.018), Bk, bev=0.001)
    lb.box((-0.0035, -0.013, -0.005), (0.0035, -0.003, 0.007), Bk, bev=0.0012)
    latch = lb.finish(f'{name}.pull.0')
    for i, sx in enumerate((-1, 1)):
        d = kid(root, P.panel_door(0.39, 0.392, t=0.02, stile=0.06, mat=mat, name=f'{name}.door.{i}'), (sx * 0.63, yf + 0.026, 0.101))
        h = kid(root, latch if i == 0 else bpy.data.objects.new(f'{name}.pull.{i}', latch.data), (sx * 0.465, yf + 0.0055, 0.34))
        doors.append(([d, h], (sx * 0.825, yf + 0.006, 0.0), sx * 100))    # front arris of the outer edge
        # behind the door: a lined box between the posts with one shelf (shelf top 0.304, floor 0.1125)
        inner.append(kid(root, P.cabinet_carcass(0.398, 0.399, 0.394, mat, plinth=0, open_front=True, shelves=1, panel=0.012,
                                                 name=f'{name}.inner.{i}'), (sx * 0.63, yb - 0.021, 0.1005)))
    for nm, x, z, ln, hgt, seed in (('books.0', -0.67, 0.1125, 0.26, 0.165, 41), ('books.1', 0.63, 0.304, 0.34, 0.16, 42)):
        inner.append(kid(root, P.book_row(ln, hgt, 0.15, seed=seed, name=f'{name}.{nm}'), (x, 0.0, z)))
    sb = mo.MB()                                                          # board games, a storage box
    for x, y0, z, w, dp, hgt, col in ((-0.63, -0.15, 0.304, 0.30, 0.27, 0.042, '#7A2E2A'), (-0.625, -0.14, 0.346, 0.27, 0.25, 0.038, '#2C3A46'),
                                      (-0.64, -0.13, 0.384, 0.24, 0.24, 0.035, '#C9B88A'), (0.63, -0.16, 0.1125, 0.33, 0.30, 0.14, '#8A7A5A')):
        sb.box((x - w / 2, y0, z), (x + w / 2, y0 + dp, z + hgt), M.solid('living_box_' + col[1:], col, 0.6), bev=0.002)
    sb.box((0.63 - 0.168, -0.163, 0.2225), (0.63 + 0.168, 0.143, 0.2545), M.solid('living_box_lid', '#6B5E44', 0.6), bev=0.002)
    inner.append(kid(root, sb.finish(name + '.stored'), (0, 0, 0)))
    front = kid(root, P.panel_door(0.716, 0.158, t=0.02, slab=True, mat=mat, name=name + '.drawer'), (0, yf + 0.026, 0.102))
    pull = kid(root, P.handle_cup(0.096, 0.04, 0.026, finish='black', name=name + '.pull.2'), (0, yf + 0.005, 0.181))   # cup pull
    bx = mo.MB()                                                          # drawer box 0.70 x 0.38 behind the front
    y0, y1, z0, z1 = yf + 0.026, yf + 0.406, 0.112, 0.245
    for sx in (-1, 1):
        bx.box((sx * 0.35, y0, z0), (sx * 0.338, y1, z1), mat, grain=1)
    bx.box((-0.338, y1 - 0.012, z0), (0.338, y1, z1), mat, grain=0)
    bx.box((-0.338, y0, z0), (0.338, y1 - 0.012, z0 + 0.01), mat, grain=0)
    Bk = M.mat('black_matt')
    for x, rz in ((-0.24, 8), (-0.17, -5)):                               # two remote controls, a stack of disc cases
        bx.at(Tr(x, y0 + 0.12, z0 + 0.01) @ Rz(rz))
        bx.box((-0.022, -0.085, 0), (0.022, 0.085, 0.018), Bk, bev=0.003)
    bx.at()
    for k, col in enumerate(('#E9E2D0', '#3C5E8C', '#B8433A', '#2C3A46')):
        bx.box((0.08 + 0.004 * k, y0 + 0.05, z0 + 0.01 + 0.014 * k), (0.22 + 0.004 * k, y0 + 0.24, z0 + 0.023 + 0.014 * k),
               M.solid('living_box_' + col[1:], col, 0.6))
    box = kid(root, bx.finish(name + '.drawer.box'), (0, 0, 0))
    return root, dict(doors=doors, drawer=([front, pull, box], (0.0, -0.32, 0.0)), inner=inner)


def aircon(name='living.aircon'):
    """Daikin-style floor console 0.75 x 0.60 x 0.235, wall hung 0.10 above the floor. Origin: wall plane at
    floor level, front -Y."""
    mb = mo.MB()
    Wt = M.mat('white_gloss')
    grey = M.solid('living_ac_grey', '#C9CACB', 0.5)
    mb.box((-0.375, -0.235, 0.10), (0.375, 0.0, 0.70), Wt, bev=0.012)
    for k in range(5):
        z = 0.20 + 0.085 * k
        mb.box((-0.362, -0.2363, z), (0.362, -0.2345, z + 0.0025), grey)
    mb.box((-0.345, -0.19, 0.6995), (0.345, -0.05, 0.7012), grey)                                   # outlet flap joint
    mb.box((-0.335, -0.182, 0.7006), (0.335, -0.058, 0.7024), Wt)
    mb.box((-0.03, -0.2364, 0.615), (0.03, -0.2348, 0.627), grey)                                   # logo plate, no text
    mb.at(Tr(0.33, -0.21, 0.70))
    mb.lathe([(0, 0), (0.011, 0), (0.011, 0.002), (0, 0.002)], grey, 12)
    mb.at()
    return mb.finish(name)

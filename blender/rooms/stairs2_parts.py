"""Joinery sections shared by both flights, copied from rooms/stairs.py (spec/rooms/stairs2.md 5.4: "identical to the
flight below").

ponytail: a copy, not an import, so a parallel edit of rooms/stairs.py cannot break or restyle this flight; if the
flight below changes its spindle, tread end, wall string or handrail, copy the change here by hand.
"""
import math

import bmesh

from lib import mouldings as mo

WHITE = 'joinery_white'

# timber tread end: 30 mm rounded nosing over a 20 mm scotia, (d out from the string face, h from the tread top)
TREAD_END = [(0, -0.052), (0.006, -0.052), (0.006, -0.048), (0.008, -0.040), (0.012, -0.034), (0.018, -0.031),
             (0.020, -0.030), (0.026, -0.027), (0.030, -0.015), (0.027, -0.004), (0.021, 0), (0, 0)]
# wall string: 30 mm board, beaded top edge, (d from the wall, h from its top line)
WALL_STRING = ([(0.030, -0.315), (0.030, -0.030), (0.027, -0.026), (0.027, -0.021)]
               + mo._half((0.027, -0.021), (0.027, -0.006), 4) + [(0.024, -0.003), (0.024, 0), (0, 0)])


def carpet_profile(h):
    """Riser face + carpet wrapped over a rounded nosing: (d out from the riser line, height)."""
    return [(0, 0), (0, h - 0.050), (0.008, h - 0.044), (0.018, h - 0.034), (0.024, h - 0.022), (0.025, h - 0.012),
            (0.021, h - 0.004), (0.012, h), (0, h)]


def step(mb, front, back, z0, h, mat):
    """One carpeted step: riser + nosing swept along `front` (plan polyline, east -> west) and the tread back to
    `back` (west -> east)."""
    mb.sweep(carpet_profile(h), [(x, y, z0) for x, y in front], mat)
    mb.face([(x, y, z0 + h) for x, y in front + back], mat, hint=(0, 0, 1))


def square(ob, half, ease=0.02):
    """Clamp a lathed mesh to square stock of half-width `half` (blocks and stops of a real turning in one closed
    mesh); ease pulls the four arrises in a little.  Needs lathe vertices on the diagonals (segs % 8 == 0)."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    for v in bm.verts:
        x, y = v.co.x, v.co.y
        m = max(abs(x), abs(y))
        if m > half:
            k = half / m * ((1 - ease) if abs(abs(x) - abs(y)) < 1e-6 else 1)
            v.co.x, v.co.y = x * k, y * k
    bm.normal_update()
    for e in bm.edges:
        if len(e.link_faces) == 2:
            e.smooth = e.calc_face_angle() < math.radians(30)
    bm.to_mesh(ob.data)
    bm.free()
    return ob


def handrail(k):
    """65 x 55 toad's-back rail; heights stretched by k because the sweep cuts it plumb on the rake."""
    half = [(0.027, 0), (0.027, 0.006), (0.0325, 0.010), (0.0325, 0.020), (0.029, 0.024), (0.030, 0.034),
            (0.026, 0.044), (0.016, 0.052), (0, 0.055)]
    pts = [(-0.027, 0)] + half + [(-d, h) for d, h in half[-2::-1]] + [(-0.027, 0)]
    return [(d, h * k) for d, h in pts]


def _bead(z, r, s, neck=11.5):
    return [(neck * s, z + .001), ((r - 1.5) * s, z + .004), (r * s, z + .0075), ((r - 1.5) * s, z + .011),
            (neck * s, z + .014)]


def _cone(s, z, sg):
    """Four-sided chamfer stop between the square block and the turning."""
    return [(22.627 * s, z), (17.318 * s, z + sg * .0132), (16 * s, z + sg * .0165), (13 * s, z + sg * .024)]


def spindle(name, height, base, top=0.15, w=0.045):
    """Square white baluster: base block, chamfer stop, collar bead, long vase, three beads at mid height, slender
    taper, collar bead, chamfer stop, top block.  Radii in mm on 32 mm stock scaled to w."""
    s, t0, t1 = w / 32, base, height - top
    L, R = t1 - t0, 26 * w / 32
    zc = t0 + 0.5 * L
    p = [(0, 0), (R, 0), (R, t0 - .001)] + _cone(s, t0, 1) + [(11 * s, t0 + .030)]
    p += _bead(t0 + .031, 16, s)
    p += [(11 * s, t0 + .047), (12.5 * s, t0 + .056), (14.5 * s, t0 + .10), (15.5 * s, t0 + .22 * L),
          (15.5 * s, t0 + .30 * L), (14 * s, t0 + .40 * L), (12 * s, zc - .040), (11 * s, zc - .030)]
    p += _bead(zc - .0225, 15, s) + _bead(zc - .0075, 16, s) + _bead(zc + .0075, 15, s)
    p += [(11 * s, zc + .024), (12 * s, zc + .034), (13.5 * s, t0 + .68 * L), (12.5 * s, t0 + .82 * L),
          (11 * s, t1 - .050)]
    p += _bead(t1 - .047, 16, s)
    p += [(11 * s, t1 - .030)] + _cone(s, t1, -1)[::-1] + [(R, t1 + .001), (R, height), (0, height)]
    mb = mo.MB()
    mb.lathe(p, WHITE, segs=16)
    return square(mb.finish(name), w / 2)


def stub(name, h, w=0.045):
    """Short white baluster where the standard turning does not fit: two blocks and one plain vase, or a block."""
    s, R = w / 32, 26 * w / 32
    b = max(0.03, min(0.14, (h - 0.14) / 2))
    t0, t1 = b, h - b
    mb = mo.MB()
    if t1 - t0 < 0.14:
        mb.box((-w / 2, -w / 2, 0), (w / 2, w / 2, h), WHITE, bev=0.002)
        return mb.finish(name)
    p = ([(0, 0), (R, 0), (R, t0 - .001)] + _cone(s, t0, 1)
         + [(11 * s, t0 + .030), (14.5 * s, t0 + .3 * (t1 - t0)), (15 * s, (t0 + t1) / 2), (12 * s, t1 - .030)]
         + _cone(s, t1, -1)[::-1] + [(R, t1 + .001), (R, h), (0, h)])
    mb.lathe(p, WHITE, segs=16)
    return square(mb.finish(name), w / 2)

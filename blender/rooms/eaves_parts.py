"""Small parts of the eaves storage voids (rooms/eaves.py): bulkhead fittings, switch and socket plates, stored
cartons, cases and boxes. Every builder returns unlinked objects; eaves.py places them and calls ctx.add.
Footage v12 (21 Nov), v5 f_0260-0346; spec/rooms/eaves.md, spec/phase3/eaves_loft.md."""
from math import cos, pi, radians, sin

import bmesh
import bpy
from mathutils import Vector

from lib import interact as IX, lighting, materials as M, props as P

EMIT = '#FFF0E0'      # opal diffuser, cool white LED. r >= g >= b: the viewer only switches "warm" emissives
CARD = '#B39566'      # kraft board (f86-101 in daylight: #C8B98F lit, kraft brown under neutral light)
TAPE = '#C9B183'


def card():
    return P.two_sided(M.solid('cardboard', CARD, 0.9))


def mesh_object(name, verts, faces, mat, smooth=False):
    """Plain object from vertex / face lists with one material and box UVs (my own meshes, not props)."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    me.validate(clean_customdata=False)
    me.materials.append(mat)
    if smooth:
        me.shade_smooth()
    ob = bpy.data.objects.new(name, me)
    M.uv_box(ob)
    return ob


def slab(name, w, d, h, mat):
    """Cuboid centred on the origin in x / y, from z 0 to h (my own mesh: one per call, no sharing)."""
    vs = [(sx * w / 2, sy * d / 2, z) for z in (0, h) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    fs = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return mesh_object(name, vs, fs, mat)


# ---------------------------------------------------------------------------------------------------- light fittings
def bulkhead(ctx, room, name, loc, normal, dia, watts, label='Eaves light', reach=None):
    """Round opal LED bulkhead (v12 f20 front, f89 / f115 rear): white polycarbonate base with a deep rim and a
    shallow opal dome. Modelled on +Z, turned so +Z = `normal` (out of the surface it is screwed to) at `loc`.
    The dome is the click target ('lamp' for the whole void, like the rocker); the Cycles bulb hangs in front of it
    (invisible to the camera)."""
    r = dia / 2
    rim = 0.30 * dia                                  # depth of the base + rim (deep rim, f20)
    base = P.lathe([(r * .93, 0), (r, .004), (r, rim * .80), (r * .985, rim * .93), (r * .95, rim),
                    (r * .86, rim), (r * .85, rim * .92)], 40, 'plastic_white', name=f'{name}.base')
    dome = P.lathe([(r * .855, rim * .90), (r * .84, rim * 1.02), (r * .70, rim * 1.12), (r * .40, rim * 1.19),
                    (0, rim * 1.21)], 40, P.emissive(EMIT, 10.0), name=name)
    n = Vector(normal).normalized()
    rot = n.to_track_quat('Z', 'Y').to_euler()
    for o in (base, dome):
        o.location, o.rotation_euler = loc, rot
        ctx.add(o, room, 'light')
    IX.tag(dome, 'lamp', rooms=[room], label=label, **({'reach': reach} if reach else {}))
    lamp = lighting.bulb(ctx, room, Vector(loc) + n * (rim * 1.21 + 0.05), watts=watts, kelvin=3100, radius=0.04,
                         name=f'{name}.bulb')
    lamp.visible_camera = False                       # the dome is what is seen, not a white ball in front of it
    return dome


def switch(ctx, room, x, y, z, facing, label='Eaves light'):
    """1-gang white rocker (86 x 86) on the knee-wall back; switches the void's light."""
    sw = P.place(P.switch_plate(1, name=f'{room}.switch'), (x, y, z), facing=facing)
    IX.tag(sw, 'light', rooms=[room], label=label)
    ctx.add(sw, room, 'fit', lm='dynamic')
    return sw


def socket(ctx, room, x, y, z, facing):
    """Double switched socket (146 x 86), white."""
    return ctx.add(P.place(P.socket(2, name=f'{room}.socket'), (x, y, z), facing=facing), room, 'fit')


# ---------------------------------------------------------------------------------------------------- stored things
def carton(name, w, d, h):
    """Closed kraft carton with bevelled edges, a centre seam on top and a tape strip over it (and down the ends).
    Origin bottom centre."""
    box = P.bevel_box(w, d, h, M.solid('cardboard', CARD, 0.9), bevel=.005, name=name)
    tape = M.solid('parcel_tape', TAPE, 0.35)
    te = min(.10, h - .01)                                                         # tape down the ends
    parts = [P.box(.050, d + .002, .0008, tape),                                    # over the seam
             P.box(.050, .0008, te, tape), P.box(.050, .0008, te, tape)]
    seam = P.box(.002, d - .02, .0004, M.solid('carton_seam', '#6E5A3C', 0.9))
    at = [(0, 0, h), (0, -d / 2 - .0004, h - te), (0, d / 2 + .0004, h - te)]
    for i, (k, p) in enumerate(zip(parts, at)):
        k.name, k.parent, k.location = f'{name}.tape.{i}', box, p
    seam.name, seam.parent, seam.location = f'{name}.seam', box, (0, 0, h + .0008)
    return box


def open_carton(name, w, d, h, flaps):
    """Open kraft carton, flaps up (v12 f86-93): four 3 mm walls and a bottom, four flaps hinged at the rim and
    leaning outwards by the angles `flaps` = (south, east, north, west) degrees from vertical. Origin bottom centre."""
    t = .003
    bm = bmesh.new()

    def quad(pts):
        bm.faces.new([bm.verts.new(p) for p in pts])

    # walls (outer and inner skins) and the bottom
    for sx, sy, L, ax in ((0, -1, w, 'x'), (1, 0, d, 'y'), (0, 1, w, 'x'), (-1, 0, d, 'y')):
        for off in (0, -t):
            if ax == 'x':
                yy = sy * (d / 2 + off)
                quad([(-L / 2, yy, 0), (L / 2, yy, 0), (L / 2, yy, h), (-L / 2, yy, h)])
            else:
                xx = sx * (w / 2 + off)
                quad([(xx, -L / 2, 0), (xx, L / 2, 0), (xx, L / 2, h), (xx, -L / 2, h)])
    quad([(-w / 2, -d / 2, .002), (w / 2, -d / 2, .002), (w / 2, d / 2, .002), (-w / 2, d / 2, .002)])
    # flaps: the long sides' flaps are half the width deep, the short sides' meet in the middle when shut
    fl = {0: d / 2 * .95, 2: d / 2 * .95, 1: d / 2 * .9, 3: d / 2 * .9}
    for k, deg in enumerate(flaps):
        a = radians(deg)
        if k in (0, 2):                     # south / north: hinge along x at y = -+d/2
            s = -1 if k == 0 else 1
            y0, L = s * d / 2, w
            dy, dz = s * fl[k] * sin(a), fl[k] * cos(a)
            quad([(-L / 2, y0, h), (L / 2, y0, h), (L / 2 * .98, y0 + dy, h + dz), (-L / 2 * .98, y0 + dy, h + dz)])
        else:                               # east / west: hinge along y
            s = 1 if k == 1 else -1
            x0, L = s * w / 2, d
            dx, dz = s * fl[k] * sin(a), fl[k] * cos(a)
            quad([(x0, -L / 2, h), (x0, L / 2, h), (x0 + dx, L / 2 * .97, h + dz), (x0 + dx, -L / 2 * .97, h + dz)])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(card())
    ob = bpy.data.objects.new(name, me)
    M.uv_box(ob)
    return ob


def flat_cartons(name, sheets, lean=11.0, gap=0.007):
    """Bundle of flattened cartons leaning against a wall (v12 f87, f93, f100-101): sheets = [(w, h, dy)], each a
    4 mm kraft board w along the wall (local y) and h up it, all leaning `lean` degrees from vertical; the first sheet's
    top touches the wall (local x = 0), each next one stands `gap` further out (they lie on one another). Origin on
    the wall plane at floor level; the bundle lies on the -x side (turn it with rot_z to face the wall)."""
    t, a = .004, radians(lean)
    vs, fs = [], []
    for i, (w, h, dy) in enumerate(sheets):
        top = -.002 - i * gap                       # x of the board's wall-side face at its top edge
        foot = top - h * sin(a)
        zt = h * cos(a)
        b = len(vs)
        for ox in (0.0, -t):
            vs += [(foot + ox, dy - w / 2, 0), (foot + ox, dy + w / 2, 0), (top + ox, dy + w / 2, zt),
                   (top + ox, dy - w / 2, zt)]
        fs += [(b, b + 1, b + 2, b + 3), (b + 7, b + 6, b + 5, b + 4),          # wall side / room side
               (b + 3, b + 2, b + 6, b + 7), (b, b + 4, b + 5, b + 1),          # top edge / foot
               (b, b + 3, b + 7, b + 4), (b + 1, b + 5, b + 6, b + 2)]          # ends
    return mesh_object(name, vs, fs, card())


def suitcase(name, w, d, h, colour, metallic=0.0):
    """Plain hard-shell spinner case (no labels): ribbed shell with a zip line round the middle, top handle,
    telescopic-handle housing, four spinner wheels. w across, d front-to-back, h tall; origin bottom centre (the
    shell stands on its wheels, 45 mm). Lying cases: rotate it yourself."""
    wheel = .045
    shell = M.solid(f'luggage_{colour.lstrip("#")}', colour, 0.42, metallic)
    trim = M.solid('luggage_trim', '#202124', 0.55)
    body = P.bevel_box(w, d, h - wheel, shell, bevel=.03, segments=3, name=name)
    # two raised ribs down the front and the back shell
    kids = [(P.bevel_box(.034, .005, (h - wheel) * .78, shell, bevel=.002), (sx * w * .24, sy * (d / 2 + .001), (h - wheel) * .11))
            for sx in (-1, 1) for sy in (-1, 1)]
    kids.append((P.box(w + .004, d + .004, .012, trim), (0, 0, (h - wheel) * .52)))         # zip / seal line
    kids.append((P.bevel_box(.17, .032, .028, trim, bevel=.008, segments=2), (0, 0, h - wheel)))   # top handle
    kids.append((P.box(.20, .03, .015, trim), (0, d / 2 - .02, h - wheel)))                 # trolley housing
    rot = {}
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * (w / 2 - .045), sy * (d / 2 - .045)
            wh = P.lathe([(0, 0), (.022, 0), (.022, .02), (0, .02)], 10, trim)     # wheel, axle along y
            kids.append((wh, (x, y + .01, -wheel + .022)))
            rot[len(kids) - 1] = (pi / 2, 0, 0)
            kids.append((P.box(.034, .034, .02, trim), (x, y, -.02)))              # caster housing
    for i, (k, at) in enumerate(kids):
        k.name, k.parent, k.location = f'{name}.part.{i}', body, at
        if i in rot:
            k.rotation_euler = rot[i]
    body['wheel'] = wheel
    return body


def storage_box(name, w, d, h, body='#D7DBDC', lid='#B9C0C4'):
    """Lidded plastic storage box (f19-21 at the gable end): slightly tapered tub, lip, lid with a raised panel."""
    tub = M.solid(f'plasticbox_{body.lstrip("#")}', body, 0.30)
    top = M.solid(f'plasticbox_{lid.lstrip("#")}', lid, 0.35)
    hb = h - .035
    vs =[(sx * (w / 2 - .015), sy * (d / 2 - .015), 0) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    vs += [(sx * w / 2, sy * d / 2, hb) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    root = mesh_object(name, vs, [(0, 3, 2, 1), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7)], tub)
    kids = [(P.bevel_box(w + .012, d + .012, .022, top, bevel=.004), (0, 0, hb)),
            (P.bevel_box(w * .70, d * .62, .013, top, bevel=.004), (0, 0, hb + .022))]
    for i, (k, at) in enumerate(kids):
        k.name, k.parent, k.location = f'{name}.lid.{i}', root, at
    return root

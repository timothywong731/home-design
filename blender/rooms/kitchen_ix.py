"""Kitchen: what the things that open reveal (blender/INTERACT.md) - cupboard contents, drawer boxes, oven
cavities, the insides of the dishwasher and the fridge-freezer.

Every function draws into a lib.mouldings.MB at its current frame and leaves the frame as it found it:
x runs along the wall to the viewer's right, z is up and +y points AWAY from the viewer (towards the wall), so
an interior starts at its mouth y = 0 and runs back to y = depth. Small items stand on z = 0 round the origin.
Generic shapes only (BRIEF: no labels, no brands, nothing copied from the footage).

    blender -b --factory-startup --python blender/rooms/kitchen_ix.py        # self-check: every piece builds
"""
import math
import os
import random
import sys

from mathutils import Matrix

if __name__ == '__main__':
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from lib import materials as M

HUES = ('#B5462F', '#D9A441', '#3F7A4E', '#35618C', '#E6E0D0', '#6B4A8C', '#C96F2B', '#8FB7C9')


def T(x=0.0, y=0.0, z=0.0):
    return Matrix.Translation((x, y, z))


def col(name, hx, rough=.5, metal=0):
    return M.solid('kitchen_' + name, hx, rough, metal)


def hue(i, rough=.45):
    return col('hue%d_%d' % (i % len(HUES), round(rough * 100)), HUES[i % len(HUES)], rough)


def lining(mb, a, b, y0, y1, za, zb, mat, open='front', out=False):
    """Inside faces of the box x a..b, y y1..y0 (y0 = the back, y1 = the mouth side), z za..zb. `open` names
    the sides left out: 'front' (y1), 'top', or 'front top'. Faces look inwards, so nothing shows from outside;
    out=True turns them outwards: the casing of something open (the underside of the sink bowls)."""
    faces = [([(a, y0, za), (a, y1, za), (a, y1, zb), (a, y0, zb)], (1, 0, 0)),
             ([(b, y0, za), (b, y1, za), (b, y1, zb), (b, y0, zb)], (-1, 0, 0)),
             ([(a, y0, za), (b, y0, za), (b, y1, za), (a, y1, za)], (0, 0, 1)),
             ([(a, y0, za), (b, y0, za), (b, y0, zb), (a, y0, zb)], (0, -1, 0))]
    if 'top' not in open:
        faces.append(([(a, y0, zb), (b, y0, zb), (b, y1, zb), (a, y1, zb)], (0, 0, -1)))
    if 'front' not in open:
        faces.append(([(a, y1, za), (b, y1, za), (b, y1, zb), (a, y1, zb)], (0, 1, 0)))
    for cos, hint in faces:
        mb.face(cos, mat, hint=[-h for h in hint] if out else hint)


# ----------------------------------------------------------------------------- small things
def plates(mb, n=6, dia=.26, mat='ceramic_white'):
    """Stack of n plates."""
    r, p = dia / 2, .011
    prof = [(0, 0), (r * .55, 0)]
    for i in range(n):
        prof += [(r, i * p + .014), (r * .97, i * p + .017)]
    top = (n - 1) * p + .017
    mb.lathe(prof + [(r * .6, top - .009), (0, top - .009)], mat, 14)


def bowls(mb, n=4, dia=.16, mat='ceramic_white'):
    """Nest of n bowls."""
    r, h, s = dia / 2, dia * .42, (n - 1) * .014
    mb.lathe([(0, 0), (r * .4, 0), (r, h), (r, h + s), (r - .005, h + s), (r * .38, .01 + s), (0, .01 + s)], mat, 14)


def dish(mb, w=.30, d=.20, h=.06, mat='ceramic_white'):
    """Rectangular oven dish (open box)."""
    x, y, t = w / 2, d / 2, .008
    mb.box((-x, -y, 0), (x, y, t), mat)
    for a, b in (((-x, -y, t), (-x + t, y, h)), ((x - t, -y, t), (x, y, h)), ((-x + t, -y, t), (x - t, -y + t, h)),
                 ((-x + t, y - t, t), (x - t, y, h))):
        mb.box(a, b, mat)


def pot(mb, dia=.22, h=.11, mat=None, handle=.13):
    """Saucepan / stock pot; handle = length of the long handle along +x (0: none)."""
    r, m = dia / 2, mat or col('pan', '#2A2C30', .5)
    mb.lathe([(0, 0), (r * .96, 0), (r, .006), (r, h), (r - .004, h), (r - .004, .008), (0, .008)], m, 16)
    if handle:
        mb.box((r - .002, -.011, h - .03), (r + handle, .011, h - .014), 'black_matt', .003)


def jar(mb, h=.13, dia=.075, body=None, lid=None):
    r = dia / 2
    mb.lathe([(0, 0), (r, 0), (r, .78 * h), (.8 * r, .86 * h), (0, .86 * h)], body or col('jar', '#C9B58A', .15), 10)
    mb.lathe([(0, .86 * h), (.84 * r, .86 * h), (.84 * r, h), (0, h)], lid or col('jar_lid', '#D8D5CC', .4), 10)


def bottle(mb, h=.28, dia=.07, body=None, cap=None):
    r = dia / 2
    mb.lathe([(0, 0), (r, 0), (r, .6 * h), (.38 * r, .82 * h), (.36 * r, .93 * h), (0, .93 * h)],
             body or col('bottle', '#DCE9EC', .1), 10)
    mb.lathe([(0, .93 * h), (.42 * r, .93 * h), (.42 * r, h), (0, h)], cap or col('cap', '#2F5FA8', .4), 8)


def carton(mb, w=.07, d=.07, h=.20, mat=None):
    mb.box((-w / 2, -d / 2, 0), (w / 2, d / 2, h), mat or hue(4), .003)


def tub(mb, w=.20, d=.14, h=.08, body=None, lid=None):
    """Lidded food container."""
    mb.box((-w / 2, -d / 2, 0), (w / 2, d / 2, h - .012), body or col('tub', '#C7DCE2', .15), .006)
    mb.box((-w / 2 - .003, -d / 2 - .003, h - .012), (w / 2 + .003, d / 2 + .003, h), lid or hue(3), .003)


def board(mb, w=.30, h=.40, t=.016, mat='oak_light'):
    """Chopping board / tray standing on edge, face across x."""
    mb.box((-t / 2, -w / 2, 0), (t / 2, w / 2, h), mat, .003)


# ----------------------------------------------------------------------------- drawers
def drawer(mb, w, d, h):
    """Drawer box behind a front. Origin: centre of the bottom edge on the back of the front; runs back to y = d."""
    g, x, t = col('drawer_grey', '#6E7379', .45, .6), w / 2, .013
    mb.box((-x, 0, 0), (-x + t, d, h), g)
    mb.box((x - t, 0, 0), (x, d, h), g)
    mb.box((-x + t, d - t, 0), (x - t, d, h), g)
    mb.box((-x + t, 0, 0), (x - t, d - t, .012), col('drawer_base', '#8C9298', .7))


def cutlery(mb, w, d, n=6):
    """Cutlery tray filling a drawer w x d: dividers and a few pieces. Origin: front centre of the drawer floor."""
    g = col('tray_grey', '#9AA3AD', .6)
    for i in range(n + 1):
        x = -w / 2 + i * w / n
        mb.box((x - .003, .02, 0), (x + .003, d - .02, .045), g)
    for y in (.02, d - .026):
        mb.box((-w / 2, y, 0), (w / 2, y + .006, .045), g)
    for i in range(n):
        x = -w / 2 + (i + .5) * w / n
        for k in (-1, 0, 1):
            mb.box((x + k * .022 - .006, .05, .002 + (k + 1) * .003), (x + k * .022 + .006, d * (.62 + .08 * ((i + k) % 3)),
                   .005 + (k + 1) * .003), 'silver_satin' if (i + k) % 4 else 'black_matt')


# ----------------------------------------------------------------------------- appliances
def _wire(mb, a, b, y0, y1, z, mat, pitch=.05, along='y'):
    """Flat wire grid: a rim of 5 mm bars + bars every `pitch` running along y (or x); pitch=0: the rim alone."""
    for p, q in (((a, y0, z), (b, y0 + .005, z + .005)), ((a, y1 - .005, z), (b, y1, z + .005)),
                 ((a, y0, z), (a + .005, y1, z + .005)), ((b - .005, y0, z), (b, y1, z + .005))):
        mb.box(p, q, mat)
    lo, hi = (a, b) if along == 'y' else (y0, y1)
    n = max(1, round((hi - lo) / pitch)) if pitch else 1
    for i in range(1, n):
        v = lo + i * (hi - lo) / n
        if along == 'y':
            mb.box((v - .002, y0, z), (v + .002, y1, z + .004), mat)
        else:
            mb.box((a, v - .002, z), (b, v + .002, z + .004), mat)


def oven(mb, w, h, depth=.43, fans=1):
    """Built-in oven behind its drop-down door. Origin: bottom centre of the front (y = 0): black frame round the
    mouth, enamel cavity with side runners, one wire shelf and the fan cover(s) on the back: one central 170, or
    fans=2, a pair of 110 side by side (the compact combi oven, v2 f_0403-0404)."""
    B, en, ch, x, fr = mb.M.copy(), col('oven_enamel', '#26262A', .35), 'chrome', w / 2, .034
    a, b, za, zb = -x + fr, x - fr, fr * .8, h - fr * 1.2
    for p, q in (((-x, .001, 0), (a, .02, h)), ((b, .001, 0), (x, .02, h)), ((a, .001, 0), (b, .02, za)),
                 ((a, .001, zb), (b, .02, h))):
        mb.box(p, q, 'black_gloss')
    lining(mb, a, b, depth, .02, za, zb, en)
    step = (zb - za) / 5.5
    for k in range(1, 5):                                      # shelf runners
        z = za + k * step
        for sx in (-1, 1):
            mb.box((sx * (b - .008), .05, z), (sx * b, depth - .03, z + .006), ch)
    _wire(mb, a + .010, b - .010, .045, depth - .025, za + 2 * step + .006, ch, .045)
    r = .085 if fans == 1 else .055
    for k in range(fans):                                      # fan covers, facing -y
        mb.at(B @ T((k - (fans - 1) / 2) * (2 * r + .012), depth - .001, (za + zb) / 2) @ Matrix.Rotation(math.radians(90), 4, 'X'))
        mb.lathe([(0, 0), (r, 0), (r - .01, .006), (0, .006)], col('oven_fan', '#3A3A3E', .4), 16)
    mb.at(B)


def dishwasher(mb, w, h, depth=.50):
    """Inside of a dishwasher w wide, h high. Origin: bottom centre of the mouth (y = 0): lower and upper baskets
    with a few plates and bowls, cutlery tray at the top. The steel tub is the caller's carcass lining."""
    B, wire, x = mb.M.copy(), col('dw_wire', '#C9CCD0', .5), w / 2
    for z, hh in ((.06, .12), (.36, .09)):                     # baskets: floor grid + a rim rail on four posts
        _wire(mb, -x + .02, x - .02, .07, depth - .02, z, wire, .055)
        _wire(mb, -x + .02, x - .02, .07, depth - .02, z + hh, wire, 0)
        for sx in (-1, 1):
            for y in (.07, depth - .025):
                mb.box((sx * (x - .02), y, z), (sx * (x - .025), y + .005, z + hh), wire)
    _wire(mb, -x + .02, x - .02, .07, depth - .02, h - .09, wire, .04)        # cutlery tray
    disc = [(0, 0), (.125, 0), (.125, .006), (0, .006)]
    for i in range(6):                                         # plates on edge in the lower basket
        mb.at(B @ T(-x + .09 + i * .035, .30, .066 + .125) @ Matrix.Rotation(math.radians(90), 4, 'Y'))
        mb.lathe(disc, 'ceramic_white', 14)
    for i in range(3):
        mb.at(B @ T(x - .12, .14 + i * .12, .365))
        bowls(mb, 1, .13)
    mb.at(B)


def row(mb, w, room=.25, rng=None, freezer=False):
    """A row of generic groceries w wide, centred on the origin: bottles, jars, cartons and tubs (freezer: frosted
    packs), nothing taller than `room`."""
    B, rng = mb.M.copy(), rng or random.Random(1)
    n = max(1, int(w / .1))
    for i in range(n):
        mb.at(B @ T(-w / 2 + (i + .5) * w / n, 0, 0))
        k = rng.randrange(8)
        if freezer:
            mb.box((-.04, -.06, 0), (.04, .06, min(room, rng.choice((.04, .06, .09)))),
                   (hue(4), hue(7), hue(3), col('frost', '#E3EAEE', .35))[k % 4], .008)
        elif k < 2:
            bottle(mb, min(room, .19 + .01 * k), .06, hue(k + 1, .15), hue(k))
        elif k < 4:
            jar(mb, min(room, .10 + .02 * k), .07, hue(k, .15))
        elif k < 6:
            carton(mb, .07, .07, min(room, .17), hue(k))
        else:
            tub(mb, .09, .12, .06, lid=hue(k))
    mb.at(B)


def fridge(mb, w, h, depth, freezer=False, seed=3):
    """One compartment of the fridge-freezer. Origin: bottom centre of its mouth (y = 0): white liner, glass
    shelves on white trims, two drawers at the bottom, generic groceries. Shelves stop .13 behind the mouth
    so the door bins (fridge_door) fit in front of them."""
    B, x, rng = mb.M.copy(), w / 2, random.Random(seed)
    wh, gl, fr = 'plastic_white', col('fridge_shelf', '#C9DDE2', .1), col('frost', '#E3EAEE', .35)
    lining(mb, -x, x, depth, 0, 0, h, wh)
    for k in range(2):
        mb.box((-x + .01, .12, .02 + k * h * .14), (x - .01, depth - .03, h * .13 + k * h * .14), fr, .004)
    step = h * .14
    for i in range(5):
        z = h * .30 + i * step
        mb.box((-x + .004, .14, z - .006), (x - .004, depth - .01, z), gl)
        mb.box((-x + .004, .132, z - .012), (x - .004, .14, z + .003), wh)
        for y, inset in ((.24, .03), (.42, .05)):
            row(mb.at(B @ T(0, y, z)), w - 2 * inset, step - .03, rng, freezer)
            mb.at(B)


def fridge_door(mb, w, h, bins=4, ice=False, seed=5):
    """Inside of a fridge door. Origin: bottom centre of the inner panel on the back of the door (y = 0); the
    panel is 12 thick and the bins reach y = .112. ice=True: the ice-maker housing takes the top half."""
    B, x, rng = mb.M.copy(), w / 2, random.Random(seed)
    wh, cl = 'plastic_white', col('bin_clear', '#D5E0E6', .2)
    mb.box((-x, 0, 0), (x, .012, h), wh, .003)
    if ice:
        mb.box((-x + .015, .012, h * .52), (x - .015, .10, h * .95), wh, .01)
    top = h * (.45 if ice else .92)
    for k in range(bins):
        z = h * .05 + k * (top - h * .05) / bins
        mb.box((-x + .01, .012, z), (x - .01, .112, z + .005), cl)
        mb.box((-x + .01, .107, z + .005), (x - .01, .112, z + .07), cl)
        for sx in (-1, 1):
            mb.box((sx * (x - .01), .012, z + .005), (sx * (x - .015), .107, z + .07), cl)
        n = max(1, int((w - .06) / .085))
        for i in range(n):
            if rng.random() < .75:
                mb.at(B @ T(-x + .04 + (i + .5) * (w - .08) / n, .06, z + .005))
                j = rng.randrange(6)
                (bottle if j % 2 else jar)(mb, .12 + .02 * (j % 3), .06, hue(j, .15), hue(j + 2))
        mb.at(B)


def _demo():
    from lib import mouldings as mo
    mb = mo.MB()
    for fn, a in ((plates, ()), (bowls, ()), (dish, ()), (pot, ()), (jar, ()), (bottle, ()), (carton, ()), (tub, ()),
                  (board, ()), (drawer, (.74, .5, .18)), (cutlery, (.7, .46)), (oven, (.56, .49)), (oven, (.56, .34, .43, 2)),
                  (dishwasher, (.56, .68)), (row, (.5,)), (fridge, (.34, 1.66, .59)), (fridge_door, (.26, 1.6))):
        before = len(mb.bm.faces)
        fn(mb, *a)
        assert len(mb.bm.faces) > before, fn.__name__
        assert mb.M == Matrix.Identity(4), fn.__name__ + ' left the frame moved'
    ob = mb.finish('kitchen_ix_demo')
    print('KITCHEN_IX OK', len(ob.data.polygons), 'faces')


if __name__ == '__main__':
    _demo()

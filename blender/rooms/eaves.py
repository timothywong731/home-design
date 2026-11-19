"""Eaves storage voids either side of the loft office: eaves_front (with the bay-gable tunnel) and eaves_rear.
Spec: spec/rooms/eaves.md. Footage v5 f_0260-f_0346. The voids are looked into through the knee-wall hatches of
loft_office (joinery owns the six leaves), never walked.

    "$B" -b --factory-startup --python blender/build.py -- --levels 2,X --only shell,envelope,eaves_front,eaves_rear \
         --preview eaves_front,eaves_rear --res 540x960 --samples 64 --tag eaves [--pose 1 --tag eaves1]

The shell gives walls and floor only (under_roof rooms get no ceiling: the black roof underside shows), so the white
plasterboard linings of eaves.md 1 / 4 are built here, just under the roof slab, as '<room>.ceiling'.
"""
from math import pi

from lib import interact as IX, lighting, materials as M, props as P, shell

FRONT, REAR = 'eaves_front', 'eaves_rear'
WHITE = '#EFEEEA'                 # eaves.md 4: plasterboard, matt white emulsion
EMIT = '#FFF0E0'                  # opal diffuser, cool white. Kept r >= g >= b: the viewer only switches "warm" emissives

# Tunnel section (eaves.md 1.2): flat strip 0.30 wide at 0.90, linings fall to the floor 1.10 either side of the axis.
STRIP_Z, STRIP_HALF = 0.90, 0.15
MAIN_PITCH = 0.577                # main-roof lining, rise per metre of y (30 degrees)
SPILL_W = 4.0                     # W per metre of the hidden panel in the west hatch (stand-in for room light, see _front)

CAMERAS = [   # world coords; refs are v5 frames. The voids have their own light, so both poses are lit.
    dict(name='tunnel', pos=(2.95, 2.38, 6.99), look=(2.53, 0.30, 6.94), fov_deg=100, ref='v5_f_0284'),
    dict(name='switch', pos=(3.05, 2.20, 6.95), look=(1.00, 2.25, 6.85), fov_deg=100, ref='v5_f_0278'),
    dict(name='west', pos=(0.20, 2.10, 7.00), look=(3.50, 1.70, 6.80), fov_deg=100, ref='v5_f_0303'),
    dict(name='office_e', pos=(2.95, 3.50, 7.45), look=(2.70, 1.00, 6.80), fov_deg=100, ref='v5_f_0267'),
    dict(name='office_w', pos=(0.30, 3.50, 7.45), look=(0.40, 1.00, 6.70), fov_deg=100, ref='v5_f_0298'),
    dict(name='r_in', pos=(1.70, 7.10, 7.10), look=(4.00, 8.00, 6.90), fov_deg=100, ref='v5_f_0322'),
    dict(name='r_light', pos=(1.75, 7.10, 7.40), look=(3.20, 6.69, 7.50), fov_deg=100, ref='v5_f_0323'),
    dict(name='r_step', pos=(1.90, 7.00, 7.50), look=(2.55, 7.35, 6.40), fov_deg=100, ref='v5_f_0327'),
    dict(name='r_west', pos=(4.10, 7.25, 7.05), look=(1.40, 7.00, 6.95), fov_deg=100, ref='v5_f_0331'),
    dict(name='r_office', pos=(1.95, 5.50, 7.75), look=(2.30, 7.60, 6.80), fov_deg=100, ref='v5_f_0318'),
]


def _bulkhead(ctx, room, name, loc, rot, dia, bulb_at, watts):
    """Round opal LED bulkhead: white base + lit dome (modelled on +Z, `rot` turns it onto its surface) and the
    Cycles emitter. The dome is the click target ('lamp' for the whole void, like the rocker)."""
    s = dia / 0.30
    base = P.lathe([(.150 * s, 0), (.150 * s, .030), (.142 * s, .040), (.136 * s, .040)], 32, 'plastic_white',
                   name=f'{name}.base')
    dome = P.lathe([(.137 * s, .038), (.132 * s, .050), (.100 * s, .058), (.050 * s, .062), (0, .063)], 32,
                   P.emissive(EMIT, 10.0), name=name)
    for o in (base, dome):
        o.location, o.rotation_euler = loc, rot
        ctx.add(o, room, 'light')
    IX.tag(dome, 'lamp', rooms=[room], label='Eaves light')
    lamp = lighting.bulb(ctx, room, bulb_at, watts=watts, kelvin=3400, radius=0.05, name=f'{name}.bulb')
    lamp.visible_camera = False                              # the dome is what is seen, not a white ball in front of it
    return dome


def _switch(ctx, room, x, y, z, facing, socket_z=None):
    sw = P.place(P.switch_plate(1, name=f'{room}.switch'), (x, y, z), facing=facing)
    IX.tag(sw, 'light', rooms=[room], label='Eaves light')
    ctx.add(sw, room, 'fit', lm='dynamic')
    if socket_z is not None:
        ctx.add(P.place(P.socket(2, name=f'{room}.socket'), (x, y, socket_z), facing=facing), room, 'fit')


def _carton(ctx, room, n, x, y, z, w, d, h, rot=0.0):
    """Plain closed cardboard box with a tape strip along the top seam. (x, y) = centre, z = what it stands on."""
    box = P.place(P.bevel_box(w, d, h, M.solid('cardboard', '#B39566', 0.9), bevel=.004, name=f'{room}.carton.{n}'),
                  (x, y, z), rot_z=rot)
    tape = P.box(w + .002, .048, .0008, M.solid('parcel_tape', '#C9B183', 0.35), name=f'{room}.carton.{n}.tape')
    tape.parent, tape.location = box, (0, 0, h)
    ctx.add(box, room, 'decor', lm='static')    # void rooms get no probe: probe-lit, it would take the room below's


def _suitcase(ctx, room, n, x, y, z, colour, rot=0.0, flat=False):
    """Plain hard-shell suitcase 0.44 x 0.26 x 0.62 on four wheels, no labels. flat = lying on its back."""
    w, d, h, wheel = 0.44, 0.26, 0.62, 0.035
    dark = M.solid('luggage_trim', '#232427', 0.5)
    body = P.bevel_box(w, d, h, M.solid(f'luggage_{colour.lstrip("#")}', colour, 0.45), bevel=.035, segments=3,
                       name=f'{room}.suitcase.{n}')
    kids = [(P.bevel_box(.16, .03, .022, dark, bevel=.006), (0, 0, h))]
    kids += [(P.box(.035, .03, wheel, dark), (sx * (w / 2 - .05), sy * (d / 2 - .04), -wheel)) for sx in (-1, 1) for sy in (-1, 1)]
    for i, (k, at) in enumerate(kids):
        k.name, k.parent, k.location = f'{room}.suitcase.{n}.part.{i}', body, at
    body.location = (x, y, z + (d / 2 if flat else wheel))
    body.rotation_euler = (pi / 2 if flat else 0, 0, rot * pi / 180)
    ctx.add(body, room, 'decor', lm='static')   # baked, like the cartons


def _front(ctx):
    F = ctx.floor_z(FRONT)
    (xw, yf), (bw, _), (_, yg), (be, _), _, (xe, _), (_, yk), _ = ctx.room_poly(FRONT)   # house.json order
    cx = (bw + be) / 2
    k = STRIP_Z / ((be - bw) / 2 - STRIP_HALF)               # tunnel lining rise per metre of x (43 degrees)
    m = MAIN_PITCH * (yk - yf)                               # main lining height at the knee wall (0.86)
    v = m / k                                                # valley reaches the knee wall this far inside the tunnel foot

    # --- plasterboard linings: envelope of the main slope and the tunnel (eaves.md 1.1, 1.2), z above the floor
    faces = [[(xw, yf, 0), (bw, yf, 0), (bw, yk, m), (xw, yk, m)],                       # main slope, west stretch
             [(be, yf, 0), (xe, yf, 0), (xe, yk, m), (be, yk, m)],                       # main slope, east stretch
             [(cx - STRIP_HALF, yg, STRIP_Z), (cx + STRIP_HALF, yg, STRIP_Z),
              (cx + STRIP_HALF, yk, STRIP_Z), (cx - STRIP_HALF, yk, STRIP_Z)]]           # flat strip, up to the hatch
    for s, foot in ((1, bw), (-1, be)):                      # west and east halves of the tunnel
        edge = cx - s * STRIP_HALF
        faces += [[(foot, yf, 0), (foot + s * v, yk, m), (foot, yk, m)],                 # main slope up to the valley
                  [(foot, yg, 0), (edge, yg, STRIP_Z), (edge, yk, STRIP_Z), (foot + s * v, yk, m), (foot, yf, 0)]]
    for f in faces:                                          # the check: nothing pokes through the roof slab
        for x, y, z in f:
            assert F + z <= ctx.ceil_z(FRONT, min(max(x, xw + .01), xe - .01), min(max(y, yg + .01), yk - .01)) + .02, (x, y, z)
    inside = (cx, (yf + yk) / 2, F + 0.2)
    # named '.ceiling' so the level-2 dollhouse lifts it off like every other ceiling (main.js dollVis)
    lining = shell.faces_object(f'{FRONT}.ceiling', [([(x, y, F + z) for x, y, z in f], inside, WHITE) for f in faces])
    ctx.add(lining, FRONT, 'trim')
    # the shell clips the knee wall to the bay-gable planes at the tunnel feet, leaving its top below the lining edge
    # (F + m): close those two slots on the void side (x 1.40..1.84 and 3.50..3.63, wall top down to F + 0.45)
    ctx.add(shell.faces_object(f'{FRONT}.kneecap', [([(xa, yk - .001, F + .45), (xb, yk - .001, F + .45), (xb, yk - .001, F + m),
                                                     (xa, yk - .001, F + m)], (xa, yf, F), WHITE)
                                                   for xa, xb in ((1.40, 1.84), (3.50, 3.63))]), FRONT, 'trim')

    # --- "light switch here, sockets here": on the knee-wall back just west of the east hatch (v5 f_0274-0282)
    _switch(ctx, FRONT, 2.33, yk, F + 0.60, (0, -1), socket_z=F + 0.25)
    # --- "one light": bulkhead on the flat strip of the tunnel
    _bulkhead(ctx, FRONT, f'{FRONT}.bulkhead', (cx, 1.60, F + STRIP_Z), (pi, 0, 0), 0.30, (cx, 1.60, F + STRIP_Z - 0.12), 30)

    # ponytail: the west stretch gets only spill ("it's a bit dark") and bakes near black with its hatch shut, yet in
    # the footage the open hatch lets the room light in. A dim unseen panel in the hatch plane, facing into the void,
    # stands in for that light (a bulb left a hot spot on the lining); a second, hatch-open bake would be the real answer.
    west = lighting.strip(ctx, FRONT, (-0.30, yk - 0.04, F + 0.48), (0.55, yk - 0.04, F + 0.48), watts_per_m=SPILL_W,
                          kelvin=3000, width=0.55, direction=(0, -1, 0), name=f'{FRONT}.spill')
    west.visible_camera = west.visible_glossy = False

    # --- a few plain stored things (eaves.md 6), under the linings
    _carton(ctx, FRONT, 0, 2.25, yg + 0.24, F, 0.45, 0.35, 0.32)                         # against the gable end wall
    _carton(ctx, FRONT, 1, 2.82, yg + 0.26, F, 0.40, 0.40, 0.40, rot=6)
    _carton(ctx, FRONT, 2, 2.24, yg + 0.22, F + 0.32, 0.35, 0.28, 0.22, rot=-8)
    _carton(ctx, FRONT, 3, 0.86, yk - 0.21, F, 0.45, 0.35, 0.32)                         # west stretch, by the knee wall
    _suitcase(ctx, FRONT, 0, 1.36, yk - 0.16, F, '#3A3D42')                              # standing, west of the switch
    _suitcase(ctx, FRONT, 1, 2.00, 1.05, F, '#A8A294', rot=90, flat=True)                # lying under the tunnel slope


def _rear(ctx):
    F = ctx.floor_z(REAR)
    (x0, y0), (x1, _), (_, y1), _ = ctx.room_poly(REAR)
    step = ctx.feature('eaves_rear_step')
    xs, lo = step['line'][0][0], step['zLow']

    # --- lining 11 mm under the roof slab (the spec's 1.42 at the knee wall would stand above the roof underside)
    xm, ya, yb = (x0 + x1) / 2, y0 + .05, y1 - .05           # sampled inside: on the edges other roof planes answer
    za, zb = ctx.ceil_z(REAR, xm, ya), ctx.ceil_z(REAR, xm, yb)
    quad = [(x, y, za + (zb - za) * (y - ya) / (yb - ya) - 0.011) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    ctx.add(shell.faces_object(f'{REAR}.ceiling', [(quad, ((x0 + x1) / 2, (y0 + y1) / 2, F), WHITE)]), REAR, 'trim')

    # --- lower floor east of the step: darker sheet (v5 hr_322 / hr_327: charcoal beside the pale upper floor)
    ctx.add(shell.box(f'{REAR}.floor_low', xs + .004, x1, y0, y1, lo, lo + .002, '#63625F'), REAR, 'fit')

    # --- "there's a step here": double aluminium nosing with dark inserts, 60 mm wide in all
    alu, rubber = M.mat('silver_satin'), M.solid('nosing_insert', '#3A3C3F', 0.8)
    L, yc = y1 - y0, (y0 + y1) / 2
    for i, (xa, xb, za, zb, mat) in enumerate(((xs - .060, xs + .003, F, F + .0035, alu),          # top flange
                                               (xs, xs + .003, F - .035, F, alu),                   # down leg on the riser
                                               (xs - .050, xs - .034, F + .0035, F + .0045, rubber),
                                               (xs - .024, xs - .008, F + .0035, F + .0045, rubber))):
        bar = P.box(xb - xa, L, zb - za, mat, name=f'{REAR}.nosing.{i}')
        bar.location = ((xa + xb) / 2, yc, za)
        ctx.add(bar, REAR, 'trim')

    # --- "lights on, switch": rocker east of the hatch, bulkhead beside it, both on the knee-wall back
    _switch(ctx, REAR, 2.60, y0, F + 1.05, (0, 1))
    _bulkhead(ctx, REAR, f'{REAR}.bulkhead', (2.85, y0, F + 1.05), (-pi / 2, 0, 0), 0.26, (2.85, y0 + 0.12, F + 1.05), 30)

    # --- a few plain stored things on the lower floor
    _carton(ctx, REAR, 0, 2.78, 7.42, lo, 0.50, 0.40, 0.40, rot=4)                       # the box by the step (hr_322)
    _carton(ctx, REAR, 1, 3.50, y0 + 0.22, lo, 0.45, 0.35, 0.32)
    _suitcase(ctx, REAR, 0, 4.02, y0 + 0.17, lo, '#3A3D42')


def build(ctx):
    _front(ctx)
    _rear(ctx)

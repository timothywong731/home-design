"""Minimal room module. Copy to blender/rooms/<room id>.py, set ROOM, replace the body of build().

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --only shell,wc --preview wc --res 540x960 --samples 64 --tag me
    -> build/preview/wc_<camera>_me.jpg      (add --cam pan for one camera, --save build/me.blend to keep the scene)

The shell stage has already built walls, floor, ceiling, doors, windows, skirting, dado, cornice (and
roses, pelmet, arch corbels, picture rail - see blender/lib/README.md). A room module adds fittings,
furniture, decor and ALL of the room's light fittings. API reference: blender/lib/README.md.
Everything is metres, world coordinates (+Y into the house, +X right, Z up), object scale 1.
"""
from lib import lighting, materials as M, mouldings as mo, props as P, shell

ROOM = 'wc'            # must equal the file name; objects are named '<room>.<what>[.<n>]'

# Preview cameras: world coords; fov_deg spans the LONGER image side; ref = reference frame to match.
# Without CAMERAS the shell review cameras in lib/preview.py (DEFAULT_CAMERAS[ROOM]) are used.
CAMERAS = [
    dict(name='pan', pos=(1.6, 9.75, 1.5), look=(3.1, 9.75, 1.3), fov_deg=100, ref='f_0507'),
    dict(name='basin', pos=(1.6, 9.75, 1.5), look=(0.6, 9.75, 1.5), fov_deg=100, ref='f_0522'),
]


def build(ctx):
    xs, ys = zip(*ctx.room_poly(ROOM))
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)          # inside wall faces
    cz = ctx.ceil_z(ROOM)

    # 1. Wall-hung prop. Origin = centre of its back face, front = local -Y.
    #    facing = normal of the wall pointing INTO the room (south wall y = y0 -> (0, 1)).
    rail = P.radiator_towel_rail(0.4, 1.2, name='wc.towel_rail')
    P.place(rail, (x0 + 1.0, y0, 0.18), facing=(0, 1))
    ctx.add(rail, ROOM, 'fit', plan_sym='towel_rail')            # plan_sym = 2D plan symbol key (CONTRACT.md)

    mirror = P.mirror_framed(0.56, 0.84, 'gilt_swept', name='wc.mirror')
    P.place(mirror, (x0, (y0 + y1) / 2, 1.55), facing=(1, 0))    # west wall x = x0, room on its +X side
    ctx.add(mirror, ROOM, 'decor', plan_sym='mirror')

    # 2. Lights: emitter from lighting.*, visible trim from props.*. Add every fitting of the room:
    #    the default fill light disappears as soon as one kind='light' object exists.
    for i, x in enumerate((x0 + 0.6, x0 + 1.8)):
        lighting.downlight(ctx, ROOM, x, (y0 + y1) / 2, watts=40, name=f'wc.downlight.{i}')
        trim = P.place(P.downlight(name=f'wc.downlight_trim.{i}'), (x, (y0 + y1) / 2, cz))
        ctx.add(trim, ROOM, 'light')
    # Chandeliers / sconces: ctx.add(root, ...) links the children too, then
    #   for p in P.bulb_points(root): lighting.bulb(ctx, ROOM, p, watts=10)

    # 3. Restyle a shell surface of THIS room: swap one finish for another ...
    shell.repaint(ROOM, '#A5A5A8', '#9FA0A6')                    # wall paint; specs are '#RRGGBB' or material keys
    # ... or cover a zone with a slab standing >= 1 mm proud (splashbacks, soffits, fillers).
    panel = shell.box('wc.demo_panel', x0 + 1.5, x0 + 2.1, y1 - 0.002, y1 + 0.0, 1.20, 1.60, 'metro_grey')
    M.uv_box(panel, origin=(x0 + 1.5, 0, 1.20))                  # tile joints start at the panel's corner
    ctx.add(panel, ROOM, 'fit')

    # 4. Custom geometry: mo.MB collects boxes / sweeps / lathes into one mesh with material slots.
    mb = mo.MB()
    mb.box((0, 0, 0), (0.40, 0.12, 0.02), 'oak', bev=0.002)      # local coords; 'oak' = mo.MATS key or any library key
    mb.sweep(mo.PROFILES['bead_ovolo'], [(0, 0.12, 0), (0.40, 0.12, 0)], 'oak')
    shelf = mb.finish('wc.shelf')
    shelf.location = (x0 + 0.3, y0, 1.30)
    ctx.add(shelf, ROOM, 'fit', plan_sym='shelf')

    # 5. Small free-standing prop (origin = footprint centre on the floor / on the surface it stands on).
    plant = P.plant_potted('eucalyptus', pot_mat='pot_olive', name='wc.plant')
    plant.location = (x1 - 0.10, y0 + 0.25, 1.20)                # on the cistern ledge
    ctx.add(plant, ROOM, 'decor', plan_sym='plant')

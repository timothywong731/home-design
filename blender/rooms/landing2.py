"""Second-floor landing: landing2_platform and landing2_head (spec/rooms/landing2.md).

    B="C:/Program Files/Blender Foundation/Blender 5.1/blender.exe"
    "$B" -b --factory-startup --python blender/build.py -- --levels 1,2 --only shell,stairs2,landing2_platform,landing2_head \
        --preview landing2_head --res 540x960 --samples 64 --tag stairs2

The shell brings walls, the arch, the skylight shaft, doors, skirting, dado and cove; rooms/stairs2.py brings the
balustrade over the well, the turning newel and the cat studies on the well walls.  Here: downlights and their
switches, sockets, alarms, the five pictures, the nosing of the platform step, the dado ramp above it (with a white
patch over the shell's paint split) and the brass nosing of the "massive step" under the loft door.  No furniture (landing2.md 6).

Round 3 (spec/phase3/briefs/stairs2.md): everything on the hall east wall stands on its one straight face (x 0.32,
read from the polygon); the pier carries two single switched sockets (v5 t5-t6), all sockets sit just above the
skirting (v5 t133, v5 t5); the west-wall dado climbs the platform step on a ramp (v13 t47.5), not a plumb kink.
The arch nib with its dado and skirting returns is built by the shell (the arch clears x -0.65..0.25).
"""
from pathlib import Path

from lib import interact as IX, lighting, materials as M, mouldings as mo, props as P, shell
from rooms import stairs2 as S2

H, PL = 'landing2_head', 'landing2_platform'
ART = Path(__file__).resolve().parents[1] / 'textures' / 'art'

CAMERAS = [
    dict(name='loft', pos=(-0.3, 9.1, 7.6), look=(-0.1, 6.3, 8.0), fov_deg=100, ref='v4 f_0361'),
    dict(name='step', pos=(-0.3, 9.0, 7.6), look=(0.1, 7.6, 6.7), fov_deg=100, ref='v5 f_0140'),
    # [round 4] 'sky' before 'west': the platform's first camera is its hero still and 'west' was a close-up of a frame
    dict(name='sky', pos=(-0.15, 6.45, 7.55), look=(0.1, 8.6, 8.5), fov_deg=100, ref='v5 f_0153'),
    dict(name='west', pos=(0.05, 7.3, 7.75), look=(-0.65, 6.75, 7.7), fov_deg=100, ref='v5 f_0146'),
    dict(name='hall', pos=(-0.2, 7.0, 7.75), look=(-0.2, 11.0, 7.4), fov_deg=100, ref='v4 f_0369'),
    dict(name='arch', pos=(-0.25, 9.3, 7.53), look=(-0.2, 11.5, 7.5), fov_deg=100, ref='v4 f_0383'),
    dict(name='east', pos=(-0.62, 9.6, 7.45), look=(0.22, 9.64, 7.4), fov_deg=100, ref='v5 f_0135'),
    dict(name='north', pos=(-0.2, 11.95, 7.5), look=(-0.2, 13.3, 7.15), fov_deg=100, ref='v4 f_0442'),
    dict(name='pier', pos=(-0.45, 12.3, 7.4), look=(0.3, 12.65, 6.9), fov_deg=100, ref='v5 f_0005'),
    dict(name='south', pos=(-0.2, 12.8, 7.5), look=(-0.2, 10.0, 6.4), fov_deg=100, ref='v5 f_0001'),
    dict(name='nib', pos=(-0.2, 11.3, 7.35), look=(0.28, 11.6, 6.75), fov_deg=100, ref='v13 f_0014'),
    dict(name='ramp', pos=(-0.1, 10.4, 7.55), look=(-0.3, 7.6, 6.9), fov_deg=100, ref='v13 t47.5'),
]

LIT = [H, PL, 'stairs2']        # what the landing downlights light: the hallway, the platform and the well


def build(ctx):
    z2, zp, cz = ctx.floor_z(H), ctx.floor_z(PL), ctx.ceil_z(H)
    xw = min(x for x, _ in ctx.room_poly(H))                         # west party wall -0.65
    y_well = min(y for _, y in ctx.room_poly(PL))                    # loft-door wall face 6.23
    y_step = max(y for _, y in ctx.room_poly(PL))                    # platform riser 8.13
    xe = max(x for x, _ in ctx.room_poly(H))                         # hall east wall, one straight face (0.32)

    # ---- downlights L1-L5 (landing2.md 8) and the fitting north of the arch, read as a sixth spot (doubt 8).  The
    # platform has no fitting (lit by the skylight and L1's spill); build.py NO_FILL keeps the default fill out of it.
    for i, (room, x, y) in enumerate([(H, -0.25, 8.40), ('stairs2', 0.57, 8.45), (H, -0.22, 9.30), (H, -0.22, 10.20),
                                      (H, -0.22, 10.90), (H, -0.18, 12.25)], 1):
        lighting.downlight(ctx, room, x, y, z=cz - 0.015, watts=45, name=f'{room}.downlight.{i}')
        ctx.add(P.place(P.downlight(name=f'{room}.downlight_trim.{i}'), (x, y, cz)), room, 'light')

    # ---- switches: S1 / S2 two-way for the landing spots, S3 outside the bathroom for its lights ------------------
    for name, room, loc, facing, rooms, label in (
            ('landing2_head.switch.s1', H, (xe, 9.10, z2 + 1.20), (-1, 0), LIT, 'Landing lights'),
            ('landing2_platform.switch.s2', PL, (xw, y_well + 0.14, zp + 1.22), (1, 0), LIT, 'Landing lights'),
            ('landing2_head.switch.s3', H, (xe, 12.68, z2 + 1.22), (-1, 0), ['bathroom2'], 'Bathroom lights')):
        sw = P.place(P.switch_plate(1, name=name), loc, facing=facing)
        IX.tag(sw, 'light', rooms=rooms, label=label)
        ctx.add(sw, room, 'fit', lm='dynamic')

    # ---- sockets, alarms ---------------------------------------------------------------------------------------
    # Plates sit 0.02-0.04 over the 0.17 skirting (v5 t133: 20 px gap at 457 px/m; v5 t5: 10-15 px under a 45 px
    # plate), centre 0.25.  Pier: two SINGLE switched sockets, centres 0.14 / 0.275 from the end wall (floor2_a
    # verification note 4; v5 t5-t6 reads 0.15 / 0.29); the white plug-in in socket 0 is omitted.
    for i, (y, g) in enumerate(((10.28, 2), (12.795, 1), (12.66, 1))):
        ctx.add(P.place(P.socket(g, name=f'landing2_head.socket.{i}'), (xe, y, z2 + 0.25), facing=(-1, 0)), H, 'fit')
    for i, (x, y, r) in enumerate(((-0.22, 9.75, 0.065), (0.0, 10.55, 0.06))):
        al = P.lathe([(0, -0.04), (r - 0.012, -0.04), (r - 0.002, -0.032), (r, 0)], mat='plastic_white',
                     name=f'landing2_head.alarm.{i}')
        ctx.add(P.place(al, (x, y, cz)), H, 'fit')
    rim = P.lathe([(0.0445, -0.0401), (0.0445, -0.0407), (0.0485, -0.0407), (0.0485, -0.0401)],
                  mat='#9A9A96', name='landing2_head.alarm.1.rim')    # only a faint grey line on the second disc (v4 f_0383)
    ctx.add(P.place(rim, (0.0, 10.55, cz)), H, 'fit')

    # ---- pictures (landing2.md 7; W2 is a generic papyrus, not a crop) -------------------------------------------
    for name, room, img, loc, facing, kw in (
            ('tree', PL, 'landing2_tree', (xw, 6.90, zp + 1.60), (1, 0),     # 0.25 past S2 (v5 f_0146), not 7.62
             dict(w=0.56, h=0.76, frame_style='gilt_bead', frame_w=0.045, mount=0.105, glass=True)),
            ('papyrus', H, 'landing2_papyrus', (xw, 8.95, z2 + 1.58), (1, 0),
             dict(w=0.62, h=0.98, frame_style='black', frame_w=0.025, mount=0.03, glass=True)),
            ('cottage', H, 'landing2_cottage', (xw, 10.62, z2 + 1.62), (1, 0),
             dict(w=0.65, h=0.52, frame_style='gilt_bead', frame_w=0.055)),     # straight reeded gold (v4 f_0383)
            ('cats', H, 'landing2_cats', (xw, 12.25, z2 + 1.72), (1, 0),
             dict(w=0.28, h=0.78, frame_style='walnut_gold', frame_w=0.03, glass=True)),
            ('harbour', H, 'landing2_harbour', (xe, 9.75, z2 + 1.60), (-1, 0),
             dict(w=0.98, h=0.68, frame_style='gilt_bead', frame_w=0.045, mount=0.09, glass=True))):
        pic = P.framed_picture(image=str(ART / f'{img}.jpg'), name=f'{room}.picture.{name}', **kw)
        ctx.add(P.place(pic, loc, facing=facing), room, 'decor')

    # ---- platform step: carpet nosing from the skirting to the turning newel; dado ramp on the west wall ----------
    tx = ctx.stair('stair_second')['turningNewel'][0]
    mb = mo.MB()
    S2.nosing(mb, [(xw + 0.02, y_step), (tx - S2.NEWEL_S / 2, y_step)], z2, zp - z2, M.mat('carpet_grey_twist'))
    ctx.add(mb.finish('landing2_platform.step_nosing'), PL, 'fit')
    # The rail leaves the hall level above the riser and climbs the 0.20 on a straight ramp over the platform
    # (v13 t47.5: ramp / platform wall = 0.29 by the vanishing point of the hall rails -> 0.55 of 1.90; c_v5_0_far
    # agrees on a long ramp; 0.50 used), mitred at both knees.  The two level shell rails are cut back by STUB
    # and the ramp brings short level stubs of the same section, so both joints are square butts.
    top, ph = mo.TRIM[H]['dado']['top'], mo.profile_size('dado_landing')[1]
    y_r, STUB = y_step - 0.50, 0.04
    mb = mo.MB()
    mb.sweep([(ph - h, p) for p, h in mo.PROFILES['dado_landing']],
             [(xw, y_step + STUB, z2 + top), (xw, y_step, z2 + top), (xw, y_r, zp + top), (xw, y_r - STUB, zp + top)],
             S2.WHITE, up=(1, 0, 0))
    ctx.add(mb.finish('landing2_head.dado_ramp'), H, 'trim')
    for room, lo, hi, to in ((H, y_step - 0.01, y_step + STUB, y_step + STUB), (PL, y_r - STUB, y_step + 0.01, y_r - STUB)):
        S2.cut_back(f'{room}.dado', lambda w: w.x < xw + 0.06 and lo <= w.y <= hi, to)
    # The shell splits the platform paint level at zp + split_z, above the low end of the ramp: white over the
    # triangle there, its lower edge 10 mm behind the rail top, so the split follows the ramp (v13 t47.5, v4 f_0370).
    zs, z0 = zp + shell.split_z(PL) + 0.005, z2 + top - 0.01
    mb = mo.MB()
    mb.face([(xw + 0.0015, y_step, z0), (xw + 0.0015, y_step, zs), (xw + 0.0015, y_step - (zs - z0) * 0.50 / 0.20, zs)],
            shell.material(shell.finish(PL)['upper']), hint=(1, 0, 0))
    mb.face([(xw + 0.0015, y_step, z0), (xw + 0.0015, y_step, zs), (xw, y_step + 0.004, zs), (xw, y_step + 0.004, z0)],
            shell.material(shell.finish(PL)['upper']), hint=(1, 1, 0))     # closes the slot: no dark hairline at the riser line
    patch = mb.finish('landing2_platform.ramp_paint')
    M.uv_box(patch)
    ctx.add(patch, PL, 'trim')
    # No skirting kink: the platform skirting ends square on the riser line over the hall skirting (v13 t47.5).

    # ---- the "massive step": polished-brass nosing on the white riser under the loft door -------------------------
    o = ctx.openings['d_loft']
    x0, x1, zs = o['center'][0] - o['width'] / 2, o['center'][0] + o['width'] / 2, o['floorZ'] + o['sill']
    mb = mo.MB()
    mb.box((x0, y_well - 0.03, zs - 0.002), (x1, y_well + 0.008, zs + 0.005), 'brass', bev=0.002)
    mb.box((x0, y_well, zs - 0.022), (x1, y_well + 0.008, zs - 0.002), 'brass')
    ctx.add(mb.finish('landing2_platform.loft_step_nosing'), PL, 'fit')


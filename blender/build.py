"""Build the house. See blender/MULTILEVEL.md section 5, blender/CONTRACT.md and blender/lib/README.md.

blender -b --factory-startup --python blender/build.py -- [--house <path>] [--levels B,G,1,2,X] [--only <stage>,...]
        [--bare] [--save build/home.blend] [--preview <what>,...] [--res WxH] [--samples n] [--cam name]
        [--tag suffix] [--pose 0|1] [--device CPU|0|1]
Stages (build order): shell, site, envelope, then the room modules (house rooms in file order, then pseudo-rooms).
--only takes stage names and room / pseudo-room ids. --preview takes room ids, level:<id>, plan:<level>, section,
elev:front|rear|flank, all. --cam: one camera name, or 'first' (each room's first). --device: render on the CPU or on one GPU (default every GPU) when the GPUs are busy.
"""
import argparse
import importlib
import importlib.util
import sys
import traceback
from pathlib import Path

import bpy
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
STAGES = ('shell', 'site', 'envelope')


def parse():
    ap = argparse.ArgumentParser(prog='build.py')
    ap.add_argument('--house', default='')
    ap.add_argument('--levels', default='')
    ap.add_argument('--only', default='')
    ap.add_argument('--bare', action='store_true')
    ap.add_argument('--save', default='')
    ap.add_argument('--preview', default='')
    ap.add_argument('--res', default='960x540')
    ap.add_argument('--samples', type=int, default=64)
    ap.add_argument('--cam', default='')
    ap.add_argument('--tag', default='')
    ap.add_argument('--pose', type=int, default=0, choices=(0, 1))
    ap.add_argument('--device', default='', choices=('', 'CPU', 'cpu', '0', '1'))
    a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    a.res = tuple(int(v) for v in a.res.lower().split('x'))
    return a


def load_room(name):
    """blender/rooms/<module>.py as a module, or None when it does not exist yet."""
    path = HERE / 'rooms' / f'{name}.py'
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location(f'rooms.{name}', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def pose_scene(state):
    """Previews only (after --save): put every interaction-tagged object (blender/INTERACT.md) in `state`.
    State 0 = as modelled, only `show when=1` objects (water, flames, closed curtains, TV pictures) are hidden.
    State 1 = doors / lids swung, drawers slid, `show` objects swapped. Parents are cleared first, as the
    export does, so an untagged child stays behind exactly like in the viewer."""
    from lib import interact as IX
    bpy.context.view_layer.update()                 # matrix_world is stale until now
    if state:
        for o, W in [(o, o.matrix_world.copy()) for o in bpy.data.objects if o.parent]:
            o.parent = None
            o.matrix_world = W
    tagged = [o for o in bpy.data.objects if 'ix' in o.keys()]
    IX.pose(tagged, state)
    print(f'[build] pose {state}: {len(tagged)} tagged objects')


TOTAL = 4_000_000
LEVEL_BUDGET = {'G': 850_000, '1': 1_300_000, '2': 850_000, 'B': 150_000, 'X': 850_000}
# rooms the spec gives no fitting (lit by spill / daylight only): no default fill, else its 'on' bake gets a phantom lamp
NO_FILL = ('landing2_platform',)
BIG_ROOMS = ('living', 'dining', 'kitchen', 'green_bedroom', 'blue_bedroom', 'loft_office', 'garden', 'front')
SITE_SHELL = ('front', 'side_passage', 'garden', 'shed', 'neighbours')


def report_tris(ctx):
    """Triangles by obj['level'], obj['room'] and obj['kind'] (every object instance counted, as the GLBs will hold
    them), against the budgets of MULTILEVEL.md section 5."""
    rooms, levels, shell = {}, {}, {}
    for o in bpy.context.scene.objects:           # linked objects only: templates left in bpy.data are not exported
        if o.type != 'MESH' or o.get('no_export') or not len(o.data.polygons):
            continue
        lt = np.empty(len(o.data.polygons), np.int32)
        o.data.polygons.foreach_get('loop_total', lt)
        n, lv, room, kind = int((lt - 2).sum()), o.get('level', '?'), o.get('room', '?'), o.get('kind', '?')
        rooms.setdefault((lv, room), {})
        rooms[lv, room][kind] = rooms[lv, room].get(kind, 0) + n
        levels[lv] = levels.get(lv, 0) + n
        if kind == 'shell':
            g = 'house' if room in ctx.rooms else 'envelope' if room in ('facade', 'roof') else 'site'
            shell[g] = shell.get(g, 0) + n
    over = lambda n, cap: '' if n <= cap else f'   ** OVER BUDGET {cap} **'
    order = {l: i for i, l in enumerate(ctx.levels + ['X'])}
    for (lv, room), kinds in sorted(rooms.items(), key=lambda kv: (order.get(kv[0][0], 9), kv[0][1])):
        n = sum(kinds.values())
        print(f'[build] tris {lv:>2} {room:18s} {n:8d}  ' + ' '.join(f'{k}={v}' for k, v in sorted(kinds.items()))
              + over(n, 300_000 if room in BIG_ROOMS else 150_000))
    for lv, n in sorted(levels.items(), key=lambda kv: order.get(kv[0], 9)):
        print(f'[build] tris level {lv:>2} {n:8d}' + over(n, LEVEL_BUDGET.get(lv, TOTAL)))
    for g, cap in (('house', 60_000), ('envelope', 150_000), ('site', 100_000)):
        if g in shell:
            print(f'[build] tris kind shell, {g:8s} {shell[g]:8d}' + over(shell[g], cap))
    total = sum(levels.values())
    print(f'[build] tris TOTAL {total:8d}  (budget 4.0 M)' + over(total, TOTAL))


def main():
    args = parse()
    from lib import ctx as C, lighting, preview, shell
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ctx = C.House.load((ROOT / args.house) if args.house else None)
    ctx.errors = []
    house, pseudo = list(ctx.rooms), list(C.PSEUDO_ROOMS) if ctx.schema == 2 else []
    rooms = house + pseudo
    all_levels = ctx.levels + (['X'] if ctx.schema == 2 else [])
    levels = [s for s in args.levels.split(',') if s] or all_levels
    only = [s for s in args.only.split(',') if s] or list(STAGES) + rooms
    for s in levels:
        if s not in all_levels:
            raise SystemExit(f'unknown level {s!r}; valid: {", ".join(all_levels)}')
    for s in only:
        if s not in rooms and s not in STAGES:
            raise SystemExit(f'unknown stage/room {s!r}; valid: {", ".join(STAGES)}, {", ".join(rooms)}')

    views = []                                 # (kind, argument)
    for s in [s for s in args.preview.split(',') if s]:
        if s == 'all':
            views += [('room', r) for r in rooms if ctx.level(r) in levels]
            views += [('plan', l) for l in levels] + [('section', '')] + [('elev', e) for e in preview.SIDES]
        elif s == 'plan':
            views.append(('plan', 'G'))
        elif s == 'section':
            views.append(('section', ''))
        elif s.split(':')[0] == 'level' and s[6:] in all_levels:
            views += [('room', r) for r in ctx.rooms_on(s[6:])]
        elif s.split(':')[0] == 'plan' and s[5:] in all_levels:
            views.append(('plan', s[5:]))
        elif s.split(':')[0] == 'elev' and s[5:] in preview.SIDES:
            views.append(('elev', s[5:]))
        elif s in rooms:
            views.append(('room', s))
        else:
            raise SystemExit(f'unknown preview {s!r}; valid: room ids, level:<id>, plan:<level>, section, '
                             f'elev:{"|".join(preview.SIDES)}, all')

    if 'shell' in only:
        shell.build(ctx, [l for l in levels if l != 'X'], bare=args.bare)
    for name in STAGES[1:]:                    # site, envelope: owned by other agents, may not exist yet
        if name not in only or 'X' not in levels:
            continue
        try:
            mod = importlib.import_module('lib.' + name)
        except ImportError as e:
            print(f'[build] lib.{name} missing ({e}) - stage skipped')
            continue
        try:
            mod.build(ctx)
            print(f'[build] stage {name} done')
            if not args.bare:                  # a material key the stage could not resolve (grey fallback)
                ctx.errors += [f'material {k!r} missing ({name})' for k in sorted(getattr(mod, 'MISSING', ()))]
        except Exception:
            traceback.print_exc()
            ctx.errors.append(f'lib/{name}.py')
            print(f'[build] ERROR in {name}.build - continuing without it')

    mods, built = {}, set()
    for rid in rooms:                          # one module may serve several rooms (landing1): it runs once
        run = rid in only and ctx.level(rid) in levels
        if not run and ('room', rid) not in views:
            continue
        name = ctx.module_of(rid)
        try:                                   # one broken room must not hide the others; still exits 1
            if name not in mods:
                mods[name] = load_room(name)
            if mods[name] and run and name not in built:
                built.add(name)
                mods[name].build(ctx)
                print(f'[build] room module {name}: {len(ctx.col("room_" + rid).objects)} objects in room_{rid}')
        except Exception:
            traceback.print_exc()
            ctx.errors.append(f'rooms/{name}.py')

    if not args.bare:
        ctx.errors += [f'material {k!r} missing' for k in sorted(set(shell.MISSING))]
        try:                                   # the dado rail must sit on the paint split
            from lib import mouldings
            for rid, cfg in mouldings.TRIM.items():
                top = (cfg.get('dado') or {}).get('top')
                if top is not None and rid in shell.FINISHES and shell.FINISHES[rid]['dado'] != top:
                    ctx.errors.append(f'dado top of {rid}: mouldings.TRIM {top} != shell.FINISHES {shell.FINISHES[rid]["dado"]}')
        except ImportError:
            pass

    lighting.DEVICE = args.device.upper() if args.device.lower() == 'cpu' else (args.device or None)
    lighting.setup(ctx, args.samples, args.res)
    for rid in house:                          # default fill where no real light fittings exist yet; never outdoors
        if ctx.level(rid) in levels and ctx.kind(rid) in ('room', 'stairwell', 'void') and rid not in NO_FILL \
                and not any(o.get('kind') == 'light' for o in ctx.col('room_' + rid).objects):
            (lighting.void_fill if ctx.kind(rid) == 'void' else lighting.fill)(ctx, rid)       # eaves: a dim glow
    if 'X' in levels and 'site' in only and not any(o.get('kind') == 'light' for o in ctx.col('room_shed').objects):
        for rid, r in ctx.building_rooms.items():          # the shed has no fittings until rooms/shed.py exists
            (lighting.fill if r.get('walk') else lighting.void_fill)(ctx, rid)                 # store: a dim glow

    report_tris(ctx)
    if args.save:
        path = (ROOT / args.save).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
        print(f'[build] saved {path}')

    pose_scene(args.pose)
    out, tag, shown = ROOT / 'build' / 'preview', '_' + args.tag if args.tag else '', set()
    for kind, arg in views:
        if kind == 'room':
            name = ctx.module_of(arg)
            cams = getattr(mods.get(name), 'CAMERAS', None)
            if cams and name in shown:                     # a module shared by several rooms: its cameras once
                continue
            shown.add(name)
            preview.render_room(ctx, name if cams else arg, cams or preview.default_cameras(ctx, arg), out, args.res,
                                args.samples, args.tag, args.cam)
        elif kind == 'plan':
            preview.render_plan(ctx, arg, out / f'plan_{arg}{tag}.jpg', args.res, args.samples)
        elif kind == 'section':
            preview.render_section(ctx, out / f'section{tag}.jpg', args.res, args.samples)
        else:
            preview.render_elev(ctx, arg, out / f'elev_{arg}{tag}.jpg', args.res, args.samples)

    if ctx.errors:
        print('BUILD FAILED: ' + '; '.join(ctx.errors))
        sys.exit(1)
    print('BUILD OK')


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except BaseException:
        traceback.print_exc()
        sys.exit(1)

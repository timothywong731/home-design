"""Build the house. See blender/CONTRACT.md and blender/lib/README.md.

blender -b --factory-startup --python blender/build.py -- [--only shell,living,...] [--save build/home.blend]
        [--preview <room>[,<room>]|all|plan] [--res 960x540] [--samples 64] [--cam <name>] [--tag <suffix>] [--pose 0|1]
"""
import argparse
import importlib.util
import sys
import traceback
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))


def parse():
    ap = argparse.ArgumentParser(prog='build.py')
    ap.add_argument('--only', default='')
    ap.add_argument('--save', default='')
    ap.add_argument('--preview', default='')
    ap.add_argument('--res', default='960x540')
    ap.add_argument('--samples', type=int, default=64)
    ap.add_argument('--cam', default='')
    ap.add_argument('--tag', default='')
    ap.add_argument('--pose', type=int, default=0, choices=(0, 1))
    a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    a.res = tuple(int(v) for v in a.res.lower().split('x'))
    return a


def load_room(rid):
    """blender/rooms/<id>.py as a module, or None when the room has no module yet."""
    path = HERE / 'rooms' / f'{rid}.py'
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location(f'rooms.{rid}', path)
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


BUDGET = {'room_living': 300_000, 'room_dining': 300_000, 'room_kitchen': 300_000}     # CONTRACT: others 150 k


def report_tris():
    """Triangles per collection and kind (every object instance counted, as the GLB will hold them)."""
    total = 0
    for col in bpy.data.collections:
        kinds = {}
        for o in col.objects:
            if o.type == 'MESH' and not o.get('no_export'):
                n = sum(len(p.vertices) - 2 for p in o.data.polygons)
                kinds[o.get('kind', '?')] = kinds.get(o.get('kind', '?'), 0) + n
        n = sum(kinds.values())
        total += n
        if n:
            over = '' if col.name == 'shell' or n <= BUDGET.get(col.name, 150_000) else '   ** OVER BUDGET **'
            print(f'[build] tris {col.name:14s} {n:8d}  ' + ' '.join(f'{k}={v}' for k, v in sorted(kinds.items())) + over)
    print(f'[build] tris {"TOTAL":14s} {total:8d}  (budget 1.8 M)')


def main():
    args = parse()
    from lib import ctx as C, lighting, preview, shell
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ctx = C.House.load()
    ctx.errors = []
    rooms = list(ctx.rooms)
    only = [s for s in args.only.split(',') if s] or ['shell'] + rooms
    want = [s for s in args.preview.split(',') if s]
    if want == ['all']:
        want = rooms + ['plan']
    for s in only + want:
        if s not in rooms + ['shell', 'plan']:
            raise SystemExit(f'unknown stage/room {s!r}; valid: shell, plan, {", ".join(rooms)}')

    if 'shell' in only:
        shell.build(ctx)
    mods = {}
    for rid in rooms:
        if rid not in only and rid not in want:
            continue
        try:                                   # one broken room must not hide the others; still exits 1
            mods[rid] = load_room(rid)
            if mods[rid] and rid in only:
                mods[rid].build(ctx)
                print(f'[build] room {rid}: {len(ctx.col("room_" + rid).objects)} objects')
        except Exception:
            traceback.print_exc()
            ctx.errors.append(f'rooms/{rid}.py')

    lighting.setup(ctx, args.samples, args.res)
    for rid in rooms:                          # default fill where no real light fittings exist yet
        if not any(o.get('kind') == 'light' for o in ctx.col('room_' + rid).objects):
            lighting.fill(ctx, rid)

    report_tris()
    if args.save:
        path = (ROOT / args.save).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
        print(f'[build] saved {path}')

    pose_scene(args.pose)
    out = ROOT / 'build' / 'preview'
    for rid in want:
        if rid == 'plan':
            preview.render_plan(ctx, out / f'plan{"_" + args.tag if args.tag else ""}.jpg', args.res, args.samples)
            continue
        cams = getattr(mods.get(rid), 'CAMERAS', None) or preview.default_cameras(ctx, rid)
        preview.render_room(ctx, rid, cams, out, args.res, args.samples, args.tag, args.cam)

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

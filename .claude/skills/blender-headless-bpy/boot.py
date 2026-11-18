"""Template entry point. Run:
  "C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" -b --factory-startup --python boot.py -- --out build
Everything after `--` is yours; Blender ignores it."""
import bpy, sys, argparse, os
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser(); ap.add_argument("--out", default="build"); args = ap.parse_args(argv)
os.makedirs(args.out, exist_ok=True)

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)       # empty scene, no default cube/light/camera
    s = bpy.context.scene; s.unit_settings.system = 'METRIC'; s.unit_settings.scale_length = 1.0
    return s

def sanity(ob_names_expected=()):
    """Cheap assertions that fail the script (non-zero exit is NOT automatic: raise)."""
    missing = [n for n in ob_names_expected if n not in bpy.data.objects]
    assert not missing, f"missing objects {missing}"
    bad = [o.name for o in bpy.data.objects if o.type == 'MESH' and not o.data.polygons]
    assert not bad, f"empty meshes {bad}"

if __name__ == "__main__":
    s = reset()
    print("BLENDER", bpy.app.version_string, "engines", s.render.engine)
    # ... build scene here ...
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(args.out, "scene.blend"))

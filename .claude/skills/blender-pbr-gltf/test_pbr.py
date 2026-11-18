import sys, os, json, struct; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "blender-arch-modelling"))
import bpy, numpy as np, arch, pbr, export_gltf
bpy.ops.wm.read_factory_settings(use_empty=True)
out = os.environ.get("OUT", os.path.dirname(os.path.abspath(__file__)) + "/_t"); os.makedirs(out, exist_ok=True)
def img(n, col):
    i = bpy.data.images.new(n, 16, 16); i.pixels = list(col) * 256; i.filepath_raw = f"{out}/{n}.png"; i.file_format='PNG'; i.save(); return i
base = img("base", (0.6, 0.3, 0.2, 1)); nrm = img("nrm", (0.5, 0.5, 1, 1)); r = img("r", (0.7,0.7,0.7,1))
orm = pbr.pack_orm(1.0, r, 0.0, f"{out}/orm.png")
m = pbr.make_material("wall", base, orm, nrm, uv_name="UVMap")
w = arch.wall("w", (0,0), (4,0), 2.7, 0.2); w.data.materials.append(m)
pbr.box_uv(w, 1.0); pbr.lightmap_uv(w)
print("T uvs", [u.name for u in w.data.uv_layers])
export_gltf.export_glb(f"{out}/t.glb")
b = open(f"{out}/t.glb", "rb").read(); n = struct.unpack("<I", b[12:16])[0]; j = json.loads(b[20:20+n])
print("T mat", json.dumps(j["materials"][0])[:400]); print("T attrs", j["meshes"][0]["primitives"][0]["attributes"].keys())

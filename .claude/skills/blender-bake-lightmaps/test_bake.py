import sys, os; here=os.path.dirname(os.path.abspath(__file__)); sys.path[:0]=[here, here+"/../blender-arch-modelling", here+"/../blender-pbr-gltf"]
import bpy, numpy as np, arch, pbr, bake
bpy.ops.wm.read_factory_settings(use_empty=True)
out = os.environ.get("OUT", here + "/_t"); os.makedirs(out, exist_ok=True)
room = arch.box("room", 0,0,0, 4,3,2.6)
bpy.ops.object.select_all(action='DESELECT'); room.select_set(True); bpy.context.view_layer.objects.active = room
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.flip_normals(); bpy.ops.object.mode_set(mode='OBJECT')
room.data.materials.append(pbr.make_material("m", None))
pbr.box_uv(room); pbr.lightmap_uv(room)
l = bpy.data.lights.new("a", 'AREA'); l.energy = 300; l.size = 1; lo = bpy.data.objects.new("a", l); lo.location = (2,1.5,2.5); lo.rotation_euler=(3.14159,0,0)
bpy.context.collection.objects.link(lo)
bake.setup_cycles(samples=8, denoise=False, gpu=False)
im = bake.bake_lightmap([room], f"{out}/lm.exr", size=64)
a = np.empty(len(im.pixels), np.float32); im.pixels.foreach_get(a)
print("T lightmap mean/max", a.reshape(-1,4)[:,:3].mean(), a.max())

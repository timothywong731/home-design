import sys, os; here=os.path.dirname(os.path.abspath(__file__)); sys.path[:0]=[here, here+"/../blender-arch-modelling"]
import bpy, arch, render_setup as rs, numpy as np
bpy.ops.wm.read_factory_settings(use_empty=True)
out = os.environ.get("OUT", here + "/_t"); os.makedirs(out, exist_ok=True)
room = arch.box("room", 0,0,0, 4,3,2.6)
bpy.ops.object.select_all(action='DESELECT'); room.select_set(True); bpy.context.view_layer.objects.active = room
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.flip_normals(); bpy.ops.object.mode_set(mode='OBJECT')
arch.cut(room, [arch.box("win", 1,2.5,0.9, 2.2,3.5,2.2)])
rs.colour_management(); rs.world_sky(2.0); rs.window_portal((1.6,2.95,1.55),(1.2,1.3),(3.14159/2,0,3.14159))
rs.sun((60,0,200),4); rs.lamp((3,1,2.2),60)
rs.camera((0.4,0.3,1.55),(2.5,2.0,1.2),lens=16)
rs.cycles_still(out+"/r.png",(160,90),16,gpu=False)
im = bpy.data.images.load(out+"/r.png"); a=np.array(im.pixels[:]); print("T render mean", a.mean(), im.size[:])

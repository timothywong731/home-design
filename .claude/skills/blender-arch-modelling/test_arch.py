import sys, math, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, arch
bpy.ops.wm.read_factory_settings(use_empty=True)
w = arch.wall("w", (0,0), (4,0), 2.7, 0.22, openings=[(1.0, 0.9, 0.0, 2.1), (2.6, 1.2, 0.9, 2.1)])
print("T wall verts", len(w.data.vertices), "dims", tuple(round(x,3) for x in w.dimensions))
room = [(0,0,2.6),(4,0,2.6),(4,3,2.6),(0,3,2.6)]
c = arch.sweep_profile("cornice", arch.cove(), room)
sk = arch.sweep_profile("skirt", arch.SKIRTING, [(x,y,0) for x,y,_ in room])
print("T cornice", len(c.data.polygons), "bbox", [round(v,3) for v in c.dimensions])
d = arch.panel_door("door"); arch.bevel(d)
print("T door dims", tuple(round(x,3) for x in d.dimensions))
arch.smooth_by_angle(sk); print("T mods", [m.name for m in sk.modifiers])

# yellow_room - round-3 brief

Module `blender/rooms/yellow_room.py`. Decisions: `spec/RECONCILE3.md` (dims_1-02, -03; envelope-03).

## (a) What moved in the shell

- **West (door) wall 0.22 east**: room x 0.35..3.10 -> **0.57..3.10** (2.75 -> **2.53** wide x 2.02). The corridor
  partition `w_corr_yellow` is on centreline 0.52 (0.10 thick) and now 2.60 high on the corridor side. **Everything keyed
  to the west wall moves 0.22 east**; `d_yellow` centre (0.30, 10.53) -> **(0.52, 10.53)**, hinge y 10.911 unchanged (hard
  against the north wall, hinge jamb about 0.1 from the corner, v3 t130.5).
- Flank wall 0.30 -> 0.35 thick outwards (inner face 3.10); `w_yellow` keeps y 10.475, extReveal 0.15.
- Ceiling 2.45 unchanged (measured 2.50 +/- 0.06, small cove at the junction).

Exact spec changes (old -> new):

<!-- diff:begin (generated from spec/house.json) -->
- `rooms[yellow_room].polygon`: [[0.35, 9.03], [3.1, 9.03], [3.1, 11.05], [0.35, 11.05]] -> [[0.57, 9.03], [3.1, 9.03], [3.1, 11.05], [0.57, 11.05]]
- `rooms[yellow_room].size`: [2.75, 2.02] -> [2.53, 2.02]
- `walls[w_main_rear_1a].a`: [0.3, 8.88] -> [0.52, 8.88]
- `walls[w_main_rear_1b].b`: [3.25, 8.88] -> [3.275, 8.88]
- `walls[w_corr_yellow].a`: [0.3, 8.88] -> [0.52, 8.88]
- `walls[w_corr_yellow].b`: [0.3, 11.35] -> [0.52, 11.42]
- `walls[w_corr_yellow].height`: 2.45 -> 2.6
- `walls[w_yellow_n].a`: [0.3, 11.1] -> [0.52, 11.1]
- `walls[w_yellow_n].b`: [3.25, 11.1] -> [3.275, 11.1]
- `walls[w_flank_1_yellow].a`: [3.25, 8.88] -> [3.275, 8.88]
- `walls[w_flank_1_yellow].b`: [3.25, 11.1] -> [3.275, 11.1]
- `walls[w_flank_1_yellow].thickness`: 0.3 -> 0.35
- `openings[d_yellow].center`: [0.3, 10.53] -> [0.52, 10.53]
- `openings[d_yellow].hingeAt`: [0.3, 10.911] -> [0.52, 10.911]
- `openings[w_yellow].center`: [3.25, 10.475] -> [3.275, 10.475]
- `openings[w_yellow].extReveal` new: 0.15
<!-- diff:end -->

## (b) Surveyors' notes (dims_1, passage merged)

- Width 2.53 is a knock-on of the corridor wall, not measured inside; it matches the utility / WC below (x 0.60..3.10)
  and the room's own tolerance (2.75 +/- 0.25, never filmed along its length). Room length, window and furniture were not
  audited.
- Outside (v11 f_0035-f_0043): the twin black conduits on the flank drop in a rectangle just north of this window to z
  3.9 (envelope builds them).

## (c) New footage

- Outside only: v11 18-60 (the flank window from the passage).

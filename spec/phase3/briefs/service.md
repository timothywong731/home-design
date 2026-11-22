# service (utility + wc) - round-3 brief

Modules `blender/rooms/utility.py`, `wc.py`. Decisions: `spec/RECONCILE3.md` (passage-10, -11, envelope-03, dimsG-01).

## (a) What moved in the shell

- **Flank wall** (`w_flank_wc`, `w_flank_utility`): 0.30 -> **0.35** thick outwards; inner face x 3.10 unchanged, outer
  face 3.40 -> 3.45. Openings on it keep their y.
- **`w_wc` exterior frame**: 0.34 x 0.70 sill 1.22 -> **0.34 x 0.82 sill 1.10** (head 1.92 unchanged), set back about 0.20
  outside (extReveal 0.215 -> 0.265 with the thicker wall). The interior cistern ledge stays at 1.22: inside, the glass
  shows only about 0.19 x 0.58 above it; outside the frame runs lower behind it.
- **`w_utility` exterior frame**: 0.56 x 0.82 sill 1.05 -> **0.70 x 0.98 sill 0.92** (head 1.90), extReveal 0.06. The
  interior window board stays at 1.05; the frame runs lower behind it (low confidence).
- `w_dining_s_utility` is now 2.62 high (dining ceiling); the utility ceiling 2.40 is unchanged.
- Room sizes (utility 2.50 x 1.97, wc 2.50 x 0.78), ceilings, pocket door: unchanged.

Exact spec changes (old -> new):

<!-- diff:begin (generated from spec/house.json) -->
- `walls[w_kitchen_n].b`: [3.25, 9.045] -> [3.275, 9.045]
- `walls[w_wc_utility].b`: [3.25, 10.2] -> [3.275, 10.2]
- `walls[w_flank_wc].a`: [3.25, 8.88] -> [3.275, 8.88]
- `walls[w_flank_wc].b`: [3.25, 10.2] -> [3.275, 10.2]
- `walls[w_flank_wc].thickness`: 0.3 -> 0.35
- `walls[w_flank_utility].a`: [3.25, 10.2] -> [3.275, 10.2]
- `walls[w_flank_utility].b`: [3.25, 12.295] -> [3.275, 12.295]
- `walls[w_flank_utility].thickness`: 0.3 -> 0.35
- `walls[w_dining_s_utility].b`: [3.25, 12.295] -> [3.275, 12.295]
- `walls[w_dining_s_utility].height`: 2.8 -> 2.62
- `openings[w_utility].center`: [3.25, 11.61] -> [3.275, 11.61]
- `openings[w_utility].width`: 0.56 -> 0.7
- `openings[w_utility].height`: 0.82 -> 0.98
- `openings[w_utility].sill`: 1.05 -> 0.92
- `openings[w_utility].extReveal`: 0.01 -> 0.06
- `openings[w_wc].center`: [3.25, 9.58] -> [3.275, 9.58]
- `openings[w_wc].height`: 0.7 -> 0.82
- `openings[w_wc].sill`: 1.22 -> 1.1
- `openings[w_wc].extReveal`: 0.215 -> 0.265
<!-- diff:end -->

## (b) Surveyors' notes (passage, dims_G merged)

- Utility and WC interiors were not measured this round (dims_G); sizes, ceiling 2.40, window and pocket door keep their
  present evidence.
- Outside (v11 f_0021-f_0031, t63-64, t170): `w_wc` frame 0.33 x 0.82 from z 1.10 set 0.20 back, white-painted stone sill
  block 0.50 x 0.10 projecting 0.07, flaking (the "wall box" of the side-passage module was this sill block: delete
  `side_passage.wall_box`). `w_utility`: shallow 0.06 reveal, thin white uPVC stub cill 0.03 x 0.80 (not a stone block),
  slot trickle vent in the head, frame bottom about 0.92; rectified w/h 0.714 (v11 t170). Sills true #EDEDE8.

## (c) New footage

- v11 18-60 (side passage: both windows from outside, sills, vents); no interior footage.

# landing1 (landing1_front, landing1_ql, landing1_rear) - round-3 notes

The room spec is `spec/rooms/landing1.md`; the round-3 shell changes are in `spec/phase3/briefs/landing1.md` and
`spec/RECONCILE3.md` (dims_1-02, -05..-08, vert-01). These notes record what `blender/rooms/landing1.py` measured or
changed in round 3. World coordinates, heights above the local floor.

| item | was | now | evidence |
|---|---|---|---|
| S-stair (corridor east wall) | (0.25, 8.93, 1.25) | **(0.47, 8.92, 1.30)** | on the moved wall x 0.47; plate edge 75 mm north of the chamfer arris y 8.80 (v6 f_0034, plate 63 px = 86 mm, gap 55 px); centre 0.33 above the dado top by the 86 mm plate (v6 t29), level with the thermostat (v6 f_0029-0030, v4 f_0300) |
| thermostat | (0.25, 9.72, 1.45), 90 x 120 x 25 box, display in the middle | **(0.47, 9.55, 1.35)**, 86 x 120 x 24, rounded corners, narrow dark display slot at the top right | centre 0.35-0.38 above the dado top by its own height (v6 t29, v4 t299); h / w 1.25-1.5 in two oblique views; display slot top right (v4 t299, v6 t29). y: cross-ratio along the east wall from its vanishing point, S-stair (8.92) and the near edge of the yellow-door architrave (10.069): v6 t28 9.47 (architrave edge read at u 760) / 9.62 (u 790), v6 t29 9.46, v4 f_0183 9.63; mean 9.55 (v3 f_0054, which gave 9.72, cuts it at the frame edge) |
| S-bay (arch-bay east wall) | (0.40, 11.95, 1.25) | **(0.47, 12.00, 1.25)** | on x 0.47; centre 3.5-4 plate widths (0.35-0.40) from the blue-door wall corner (v4 f_0297, f_0298); height readings 1.18-1.42 (v3 f_0151-0152, lens-distorted), 1.25 kept |
| ceiling blank plate | (-0.20, 9.30) | **(-0.35, 9.20)**, screws along the wall | over the middle of W3, about 0.2 off the pier face (v3 t69, v4 t293); 1-gang (screws at about 0.65 of the plate length, v3 t69) |
| downlights L4-L6 | x -0.20 (old corridor axis) | L4 (-0.15, 8.72), L5 (-0.09, 9.75), L6 (-0.09, 10.75) | centred on the 1.12 corridor (axis x -0.09); L4 between the strip beside the QL and the corridor |
| radiator (west-wall recess) | 16 tubes x 45 mm = 0.72 long, centre y 10.48 | **16 x 70 mm = 1.12**, oval tubes 58 x 68, centre **y 10.60** (tubes 10.05..11.15) | v3 t140.5 (face-on from the yellow door, camera pose fitted to dado / floor / threshold / W4 bottom): 645 px over the 16 tubes = 1.05-1.15 m; v4 287: 14 tubes over 1060 px against W4 670 px = 70-75 mm pitch; ends: lockshield next to the pier corner (v3 t50, f_0051), TRV end about 2 pitches (0.15) short of the arch face (v4 t293, f_0051). Height 0.13..0.70 kept (v3 t140.5 gives 0.11..0.73) |
| W4 (over the radiator) | centre y 10.48 | **y 10.65** | v3 f_0051 about 10.62 (bottom edge vs the arch corner), v4 287 10.69 (its north edge 0.10 short of the radiator end), v3 t140.5 10.67 (0.07 north of the radiator centre), v4 t293 10.73 (vanishing-point map of the dado from the pier and arch corners) |
| QL riser nosing | return to x 0.35 | to **x 0.54** (foot of the chamfer) | `steps_ql_rear.riserLines` |

Checked and kept: radiator height (bottom 0.13, top 0.70 - v3 t50 ratio to the dado and skirting gives a top of
about 0.72; TRV at the north end, v3 t140.5); the pier socket is a double (square-looking only through
foreshortening, v3 t50); the low glow on the west wall near the steps in v4 f_0278-0280 is the plug-in night light in
the pier socket (clutter, omitted), not a step light.

Open for other owners (in the round-3 report): the blue doorcase on the landing side (architrave top 2.05, shelf top
2.23, apex 2.36-2.42 measured, built as 2.14 / 2.26) and the door's margins in the bay (0.225 W / 0.16 E measured, so
the centre near x -0.06 rather than -0.10).

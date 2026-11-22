# landing1 (first-floor front landing, quarter landing, rear corridor) - round-3 brief

Module `blender/rooms/landing1.py`. Decisions: `spec/RECONCILE3.md` (dims_1-02, -05..-08, -10; vert-01).

## (a) What moved in the shell

- **Rear corridor and arch bay 0.22 wider**: one east wall face at x **0.47** from the head of the quarter landing to the
  blue bedroom door wall (was 0.25 for the corridor and 0.40 in the arch bay); no jog at the arch. Partition 0.10 to x
  0.57 (centreline 0.52). Corridor 0.90 -> **1.12** wide. **Everything keyed to the corridor east wall moves 0.22 east**:
  `d_yellow` (x 0.30 -> 0.52) and its architrave, thermostat, switch, anything hung on that wall. West wall, pier and
  radiator stay.
- **45-degree face** `landing1_chamfer`: (0.35, 8.73)-(0.25, 8.83) -> **(0.54, 8.73)-(0.47, 8.80)** (face 0.09, legs
  0.07); the riser return of `steps_ql_rear` runs x 0.15..0.54 (stairwell edge stays at 0.15). The quarter-landing NE
  corner is square.
- **Arch**: `a_landing1` 0.80 -> **1.00** wide, centre x -0.18 -> **-0.09** (centred in the corridor, piers about 0.07
  proud each side), crown 2.05 -> **2.12**, springing 1.65 -> **1.62** (semicircle). Arch wall `w_arch1` 0.30 -> **0.12**
  thick, y 11.35 -> **11.42** (faces 11.36..11.48); arch bay stays about 0.91 deep.
- **Ceiling 2.45 -> 2.60** (Z 5.49 -> 5.64), the same plane as the blue bedroom; small plain cove. `landing1_pier_w` and
  the chamfer run to 5.64; `landing1_downstand` (over the two steps) is now 0.13 deep (z 5.64..5.77).
- Quarter landing `landing1_ql` unchanged (0.84 x 0.60); the main flight below now arrives with 14 risers of 0.2036 at the
  same nosing (y 8.13, Z 2.85). The three landing risers stay 0.19.
- Front landing (`landing1_front`) unchanged.

Exact spec changes (old -> new):

<!-- diff:begin (generated from spec/house.json) -->
- `rooms[landing1_rear].polygon`: [[-0.65, 8.13], [0.15, 8.13], [0.15, 8.73], [0.35, 8.73], [0.25, 8.83], [0.25, 11.5], [0.4, 11.5], [0.4, 12.39], [-0.65, 12.39]] -> [[-0.65, 8.13], [0.15, 8.13], [0.15, 8.73], [0.54, 8.73], [0.47, 8.8], [0.47, 12.39], [-0.65, 12.39]]
- `rooms[landing1_rear].ceilingZ`: 5.49 -> 5.64
- `rooms[landing1_rear].size`: [0.9, 4.26] -> [1.12, 4.26]
- `walls[w_green_rear].height`: 2.85 -> 2.77
- `walls[w_main_rear_1a].a`: [0.3, 8.88] -> [0.52, 8.88]
- `walls[w_corr_yellow].a`: [0.3, 8.88] -> [0.52, 8.88]
- `walls[w_corr_yellow].b`: [0.3, 11.35] -> [0.52, 11.42]
- `walls[w_corr_yellow].height`: 2.45 -> 2.6
- `walls[w_arch1].a`: [-0.765, 11.35] -> [-0.765, 11.42]
- `walls[w_arch1].b`: [0.45, 11.35] -> [0.52, 11.42]
- `walls[w_arch1].thickness`: 0.3 -> 0.12
- `walls[w_arch1].height`: 2.45 -> 2.6
- `walls[w_bay_ensuite].a`: [0.45, 11.1] -> [0.52, 11.1]
- `walls[w_bay_ensuite].b`: [0.45, 12.455] -> [0.52, 12.455]
- `walls[w_bay_ensuite].height`: 2.5 -> 2.6
- `walls[w_blue_s].b`: [0.45, 12.455] -> [0.52, 12.455]
- `walls[v_ql_n].b`: [0.35, 8.73] -> [0.54, 8.73]
- `openings[d_yellow].center`: [0.3, 10.53] -> [0.52, 10.53]
- `openings[d_yellow].hingeAt`: [0.3, 10.911] -> [0.52, 10.911]
- `openings[a_landing1].center`: [-0.18, 11.35] -> [-0.09, 11.42]
- `openings[a_landing1].width`: 0.8 -> 1.0
- `openings[a_landing1].height`: 2.05 -> 2.12
- `openings[a_landing1].springing`: 1.65 -> 1.62
- `openings[a_landing1].crown`: 2.05 -> 2.12
- `features[landing1_chamfer].face`: [[0.35, 8.73], [0.25, 8.83]] -> [[0.54, 8.73], [0.47, 8.8]]
- `features[landing1_chamfer].z`: [3.04, 5.49] -> [3.04, 5.64]
- `features[landing1_pier_w].z`: [3.04, 5.49] -> [3.04, 5.64]
- `features[landing1_arch].springing`: 1.65 -> 1.62
- `features[landing1_arch].crown`: 2.05 -> 2.12
- `features[landing1_arch].thickness`: 0.3 -> 0.12
- `features[landing1_downstand].z`: [5.49, 5.77] -> [5.64, 5.77]
- `stairs[stair_main].risers`: 15 -> 14
- `stairs[stair_main].rise`: 0.19 -> 0.20357142857142857
- `stairs[stair_main].going`: 0.23 -> 0.253
- `stairs[stair_main].straightRisers`: 12 -> 11
- `stairs[stair_main].walk.risers`: [[[0.2, 5.42], [0.65, 5.05]], [[0.2, 5.42], [0.79, 5.19]], [[0.2, 5.42], [0.99, 5.39]], [[0.15, 5.6], [0.99, 5.6]], [[0.15, 5.83], [0.99, 5.83]], [[0.15, 6.06], [0.99, 6.06]], [[0.15, 6.29], [0.99, 6.29]], [[0.15, 6.52], [0.99, 6.52]], [[0.15, 6.75], [0.99, 6.75]], [[0.15, 6.98], [0.99, 6.98]], [[0.15, 7.21], [0.99, 7.21]], [[0.15, 7.44], [0.99, 7.44]], [[0.15, 7.67], [0.99, 7.67]], [[0.15, 7.9],  ... -> [[[0.2, 5.42], [0.65, 5.05]], [[0.2, 5.42], [0.79, 5.19]], [[0.2, 5.42], [0.99, 5.39]], [[0.15, 5.6], [0.99, 5.6]], [[0.15, 5.853], [0.99, 5.853]], [[0.15, 6.106], [0.99, 6.106]], [[0.15, 6.359], [0.99, 6.359]], [[0.15, 6.612], [0.99, 6.612]], [[0.15, 6.865], [0.99, 6.865]], [[0.15, 7.118], [0.99, 7.118]], [[0.15, 7.371], [0.99, 7.371]], [[0.15, 7.624], [0.99, 7.624]], [[0.15, 7.877], [0.99, 7.877 ...
- `stairs[steps_ql_rear].riserLines`: [[[0.15, 8.13], [0.15, 8.73], [0.35, 8.73]]] -> [[[0.15, 8.13], [0.15, 8.73], [0.54, 8.73]]]
<!-- diff:end -->

## (b) Surveyors' notes (dims_1, dims_vert merged)

- Corridor width 1.12 +/- 0.03 wall to wall (v3 t54.5, t56, t488.5, t148.5); arch 0.97-1.00 between the pier reveals,
  axis within 0.01 of the corridor axis (v3 t56). Arch wall about 0.12 thick: pier reveal skirting 0.13, soffit depth
  0.10-0.11 (v3 t56, t61).
- Ceiling 2.58-2.61 on the arch wall (v3 t56); dims_vert read 2.44-2.55 at v3 t53 (camera looking up): 2.60 adopted.
- d_blue doorcase on the landing side: architrave top 2.05, shelf top about 2.23, apex 2.36-2.42 above the floor
  (landing1.md has 2.14 / 2.26; v3 t54.5, t148.5). d_blue margins in the bay: 0.225 to the west wall, 0.16 to the east
  wall. All hinged leaves 762 x 1981 (confirmed).
- Dado top on the rear landing 0.96-1.00 above the floor.
- Two steps rear-to-front at about 0.19 each (v3 t72.5, t488.5; v4 t175); one riser west off the quarter landing (v3
  t35). Front landing ceiling 2.31 against the green door (v6 t13; hood top 2.26), model 2.35: no change.
- Not settled: the plan of the riser return and the 45-degree face (v3 t36.5 and t488.5 disagree: 0.14 vs 0.28-0.32);
  the strip beside the stairwell measures 0.89-0.95 against 0.80 modelled (v3 t502, t487.5), so the stairwell edge may
  really be at x 0.27-0.30; the quarter landing may be 1.04 deep (v3 t36.5, v3 t46). In v3 t53 the arch is 295 px wide
  where the blue door wall is at 208 px/m, which would put an arch of at most 1.0 at least 1.3 in front of the door wall
  (model 0.89+0.12); the short wall between the yellow door and the arch argues the other way.

## (c) New footage

- None (v8-v13 do not show the first floor inside; the audit re-read v3, v4, v6).

## Fallout after the foundation round

Gate check of the full build of the current tree (`build/r3/gate/home.blend`, BUILD OK) against `spec/house.json`.
Bounds are world metres of the built objects (x a..b, y c..d, z e..f), measured by `build/r3/gate/audit.py` and
`collide.py` (results in `build/r3/gate/audit_new.json` and `coll_cmp.txt`). Objects that already moved with the spec
are not listed.

- The east wall of `landing1_rear` moved from x 0.25 to x 0.47 (y 8.80..12.39). The old step to x 0.40 at y 11.5 is
  gone, and the chamfer is now (0.54, 8.73)-(0.47, 8.80). The fittings on that wall now float in the air:
  - `landing1_rear.switch.stair` (x 0.235..0.25, y 8.887..8.973, z 4.25..4.33): 0.22 off the wall
  - `landing1_rear.thermostat` (x 0.224..0.25, y 9.675..9.765, z 4.43..4.55): 0.22 off
  - `landing1_rear.switch.bay` (x 0.385..0.40, y 11.907..11.993): 0.07 off

  Put them on x 0.47. Check their y against `d_yellow` (now x 0.52, y 10.149..10.911) and `a_landing1` (now y 11.42,
  x -0.59..0.41).
- The ceiling fittings followed the 5.64 ceiling. Nothing else is broken.

# Phase 3 — dims_1: dimension audit of the first-floor interior

Area: landings (three split levels), yellow room, blue bedroom, en-suite, balcony, green bedroom, green
bathroom. Footage: v3 (all), v4 f_0001–f_0355. Scratch: stills, grids and zoom crops in
`reference/work/r3_dims_1/` (private); the measuring scripts `tools.py` (stills, pixel grids, montages) and
`sv.py` (single-view metrology, with self-checks) in `build/r3/dims_1/`.

**Honest scope.** The budget went into getting a small number of measurements right rather than touching
every item on the list. Audited: ceiling heights (green bedroom, green bathroom, blue bedroom, yellow room,
rear corridor), the rear corridor / arch / arch bay in plan, the quarter landing, the two steps, the green
bay window heights, door-leaf size. **Not audited** (present values stand, nothing implied): green bedroom
length and rear-wall chain, green bathroom plan size and window, yellow room length and window, en-suite
plan size and window, blue bedroom length, balcony, front landing size and ceiling, west window, bed sizes,
radiators, sockets. No Blender previews were rendered: the comparison is against `spec/house.json`,
`spec/plan_1.png` and the room specs. No colours were sampled.

## 1. Method and calibration

- **Frame times.** The 1 fps frame `f_N` is at about t = N − 0.5 s, not N − 1 (the still at t = 530.0 is the
  view of `f_0530`, not `f_0531`). Stills below are named by time: `v3 t530.6` = `ffmpeg -ss 530.6`.
- **Lens.** The footage is rectilinear: a cornice line crossing the full width 470 px above the centre is
  straight to 3 px (`v3 t530.6`). So one focal length describes the whole frame.
- **Focal length f = 820 ± 30 px** (1080 x 1920 stills, principal point at the centre). Four estimates:
  vanishing points of a closed door `v3 t182.5` 775 ± 37; of an open leaf `v4 t158.5` 852 ± 24; reprojection
  minimum of the same two doors 795 / 830; the two floor vanishing points of the quarter landing seen
  steeply from above `v3 t36.5` 832 (16–84 %: 760–908). The first, second and fourth use no door size.
- **Door leaves are 762 x 1981.** With f fixed by the vanishing points, `d_blue` (v3 t182.5) and `d_gbath`
  (v4 t158.5) reproject to 2.1 / 1.3 px as 762 x 1981 and to 6–18 px as 826 x 2040, 726 x 2040, 838 x 1981
  or 686 x 1981.
- **In-plane measurement** (used for every height): a vertical scale from a door in the same wall, read
  along one vertical line; when the verticals are parallel in the image the scale is uniform (pitch below
  1 degree changes a 2.7 m height by about 10 mm); when they converge, the cross-ratio with the vertical
  vanishing point. On a closed door, a 4-point pose (`sv.View`).
- **What did not work, and is not used:** distances to planes behind or in front of the reference door from
  floor-line rays alone. They move 0.06 m per degree of pitch, and pitch from two door jambs is only good to
  2–3 degrees (the corridor width seen through the yellow-room door came out anywhere from 0.95 to 1.5 m).
  Off-plane results below are given only where a second, independent constraint (equal dado heights, a
  known width in the same depth plane, a metric floor rectification from two vanishing points) pins them.

## 2. Dimension table

`ok` = present value inside my tolerance, no change proposed.

| # | item | where in house.json | present | measured | method, frames | conf. |
|---|---|---|---|---|---|---|
| 1 | green bedroom ceiling | `rooms.green_bedroom.ceilingZ` (floor 3.42) | 2.85 (6.27) | cornice underside **2.69 ± 0.02** (2.709, 2.676, 2.697); ceiling **2.77 ± 0.04** | hinge edge of door 1 (1.981) as vertical scale, verticals parallel: `v3 t530.6`, `v3 t532.5` (roll 2.4 degrees, no pitch); closed sliding door `v4 t94.5`. Ceiling = underside + cornice drop 0.07–0.09, solved from the apparent band with drop = projection | high |
| 2 | green bathroom ceiling | `rooms.green_bathroom.ceilingZ` | 2.75 | 2.69–2.77 | `v4 t164.5`, scale from the sliding-door opening width (0.69–0.766) | ok |
| 3 | blue bedroom ceiling | `rooms.blue_bedroom.ceilingZ` | 2.60 | cornice underside 2.52, ceiling 2.60 ± 0.03 | `v3 t182.5`, pose on the closed `d_blue` leaf (rms 2 px) | ok, high |
| 4 | yellow room ceiling | `rooms.yellow_room.ceilingZ` | 2.45 | 2.50 ± 0.06 (cove lower edge 2.48) | `v3 t130.5`, cross-ratio up the door jamb, vertical VP about 6000 px | ok |
| 5 | rear corridor ceiling | `rooms.landing1_rear.ceilingZ` (floor 3.04) | 2.45 (5.49) | **2.62–2.67** over the arch; at least 2.54 on the `d_blue` wall | `v3 t54.5` with the arch plane fixed by items 7–8; `v3 t148.5` frontal, door-width scale, lower edge of the cove (the camera looks up, which makes this a lower bound) | medium |
| 6 | arch bay width at the `d_blue` wall | `rooms.landing1_rear` polygon x -0.65..0.40 | 1.05 | **1.15 ± 0.04**; door margins 0.225 (west) / 0.16 (east) | in plane with the door opening: `v3 t148.5` (0.225 + 0.766 + 0.16); `v3 t54.5` (1.10–1.18) | medium-high |
| 7 | rear corridor width | `rooms.landing1_rear` polygon x -0.65..0.25; `walls.w_corr_yellow` | 0.90 | **1.10–1.13** | (a) `v3 t54.5`, pose on the `d_blue` opening, pier bases on the floor, dado heights at the pier and at the door wall forced equal: 1.13 ± 0.05 between skirtings at the arch for pitch 7–12 degrees and f 790–850. (b) `v3 t488.5`, looking south, one depth plane at the head of the quarter landing: the first riser of the two steps (strip 0.80) is 206 px; nearer, the floor from the pier face to the east wall is 310 px at 311 px/m = 1.00, plus the 0.10 pier = 1.10; the riser return from x 0.15 to the east wall is 88 px = 0.28. (c) the ground-floor hall below is 1.10 (x -0.65..0.45) | medium-high |
| 8 | arch clear width | `openings.a_landing1.width` | 0.80 | **1.00 ± 0.05**; piers 0.06–0.075 proud each side | `v3 t54.5` as 7(a): 0.95–1.03 over the same range | medium |
| 9 | arch wall position | `walls.w_arch1` (y 11.20..11.50) | south face 1.19 from the `d_blue` wall, wall 0.30, bay 0.89 deep | south face **1.10 ± 0.06** from the door wall (y 11.29), wall 0.33 ± 0.05, bay **0.77 ± 0.06** | `v3 t54.5` floor points; `landing1.md` first read 0.78 / 0.35 and the second-floor analyst read this wall at y 11.30..11.57 | medium-low |
| 10 | arch springing / crown | `openings.a_landing1.springing`, `.crown` | 1.65 / 2.05 | 1.70–1.78 / 2.09–2.15 | `v3 t54.5` on the arch plane of item 9 | medium-low |
| 11 | quarter landing depth | `rooms.landing1_ql` polygon y 8.13..8.73 | 0.60 | **1.04 ± 0.06** for a width of 0.84 | `v3 t36.5`: metric rectification of the landing floor from its own two vanishing points (north wall base and top nosing; east wall base and riser base); depth / width 1.24; 1.01–1.06 for f 700–900; Monte Carlo with 4 px picks 1.025–1.055 | medium |
| 12 | two steps rear to front | `stairs.steps_rear_front` | 2 x 0.19 | 2 risers, 0.19–0.20 each | `v3 t72.5`, `v3 t488.5`: nosing to nosing 50–55 px at 275 px/m (strip 0.80) | ok |
| 13 | riser quarter landing to corridor | `stairs.steps_ql_rear` | 1 x 0.19 | 1 riser | `v3 f_0043`–`f_0049` | ok (count only) |
| 14 | `d_blue` position | `openings.d_blue.center` x -0.10 | jamb 0.169 from the west wall | 0.155–0.18 (bedroom side), 0.225 (landing side) | `v3 t182.5`, `v3 t148.5` | ok |
| 15 | green bay window sill | `openings.w_green_bay.sill` | 0.70 | 0.72 ± 0.04 | `v4 t12.5`, floor to cornice underside = 2.69 as the scale | ok |
| 16 | green bay window head / transom | `openings.w_green_bay.height`, `.transomBar` | head 2.55 (height 1.85), transom 2.00 | head **2.43 ± 0.05** (height 1.71), transom **1.95 ± 0.04** | same frame and scale | medium-low |
| 17 | door leaf size | all first-floor hinged doors | 762 x 1981 | 762 x 1981 | section 1 | ok, high |

Not in `house.json`, for the room builders: dado top on the rear landing 0.96–1.00 above the floor
(`v3 t54.5`); `d_blue` doorcase on the landing side: architrave top 2.05, shelf top about 2.23, apex
2.36–2.42 (`landing1.md` has 2.14 / 2.26); green-bedroom doorcases on the bedroom side: shelf top about
2.29, apex about 2.48 (`green_bedroom.md` has 2.60) — in the green bedroom everything above the door head
was scaled to a 2.95 ceiling and should come down with it.

## 3. What the numbers say together

1. **Front rooms share one ceiling, about 2.76 above the 3.42 floor** (bedroom 2.77, bathroom 2.75), so the
   zone under the loft floor (6.49) is 0.30, an ordinary joist depth. The 2.95 of `green_bedroom.md` came
   from frames in which the camera looks up.
2. **Rear rooms: blue bedroom 2.60 and the corridor outside its door about 2.60–2.65**, i.e. one ceiling
   plane at about Z 5.64 through the door wall, instead of a 0.15 step down into the corridor. The yellow
   room (2.50 ± 0.06) may be the same plane or 0.10 lower; not resolved.
3. **The rear corridor is as wide as the hall below it: about 1.10–1.12**, not 0.90. Its east wall face is
   at about x 0.45–0.50, on the ground-floor wall between the hall and the WC / utility (0.45..0.60), and
   the arch bay is the same width (1.15 ± 0.04), with no jog at the arch (east pier faces at u 0.908 /
   0.968 either side, bay wall 0.952). The arch is about 1.00 clear with piers about 0.07 proud.
   Consequence: the rooms east of the corridor start at about x 0.57 and are about 2.5 wide, like the WC and
   utility below them (0.60..3.10) — the walls stack.
4. **The quarter landing is deeper than wide (about 0.84 x 1.04)**. With the top nosing kept at y 8.13 its
   north wall would be at about 9.17, past the old rear wall (8.73..9.03) and into the yellow room's
   south-west corner; with the north wall kept at 8.73 the top nosing would be at about 7.69, which is the
   south edge of the ground-floor lobby (7.68..8.73, soffit 2.60) but leaves the main flight too short.
   See open question 1.

## 4. Per-unit notes

**shell**
- Green bedroom ceiling 2.77 (Z 6.19): cornice underside 2.69; walls, cornice, pelmets and door pediments
  come down with it (pediment apex about 2.48, shelf top about 2.29).
- Rear corridor and arch bay: east wall face on one line at x 0.47 (corridor 1.12 wide), partition 0.10 to
  x 0.57; ceiling 2.60 (Z 5.64); arch 1.00 clear, centred in the corridor (x -0.59..0.41), springing 1.74,
  crown 2.12, piers 0.07 proud each side, arch wall y 11.30..11.60.
- The 45-degree face at the head of the quarter landing moves with the east wall (about (0.61, 8.73) to
  (0.47, 8.87) if the north wall of the landing stays where it is); the riser return from x 0.15 to the
  east wall is 0.28–0.32 long, not 0.20.
- Green bay window: head 2.43, transom 1.95, sill 0.72 above the floor.

**landing1** — everything keyed to the corridor east wall moves 0.22 east (thermostat, switch, `d_yellow`
architrave, the two paintings on that wall if any are keyed to it); the west wall, pier and radiator do not
move. Dado top 0.96–1.00. Doorcase of `d_blue`: shelf top 2.23, apex about 2.38. Ceiling 2.60 with a small
plain cove (`v3 t148.5`, `v3 t54.5`).

**stairs2 / stairs** — the well above the quarter landing is as deep as the landing; if the landing becomes
1.04 deep the three winders of the second flight have 0.84 x 1.04 to turn in. Not re-measured from the
second-flight frames.

**yellow_room** — becomes about 2.53 wide (x 0.57..3.10) if the corridor widens; all furniture keyed to the
west (door) wall moves 0.22 east; the door is hard against the north wall (hinge jamb about 0.1 from the
corner, `v3 t130.5`). Ceiling 2.45 stands (measured 2.50 ± 0.06); the ceiling junction is a small cove.

**blue_ensuite** — west wall face about 0.57 (room about 2.33 wide between it and the false wall at 2.90).
Not measured from inside.

**blue_bedroom** — ceiling 2.60 and cornice underside 2.52 confirmed; entrance recess about 1.12–1.15 wide
(east face about 0.47–0.50). French doors: transom 1.90–2.05 and frame head 2.18–2.35 are both possible
from `v3 t344.5` (the camera looks up); not changed.

**green_bedroom** — ceiling and everything above the door head as under shell. "Double wooden door" is two
separate single oak doors either side of the big wardrobe (`v3 f_0523`–`f_0539`), as modelled.

**green_bathroom** — ceiling 2.75 stands (2.69–2.77).

**envelope** — front bay window head at world Z about 5.85 (3.42 + 2.43) instead of 5.97, transom 5.37;
check against the brick-course heights of the street survey before changing the facade.

## 5. Open questions

1. **Quarter landing depth and position** (0.60 modelled, 1.04 ± 0.06 measured, 0.84 ± 0.20 in
   `landing1.md`). One frame; the scale is the stair width 0.84. It cannot be placed without the main
   flight: either the top nosing or the north wall has to move. The second-floor analyst read the stair head
   above it as 0.40–0.61 deep, which disagrees with 1.04.
2. **Detail at the top newel**: in `v3 t36.5` the riser return scales to 0.14 with a 0.27 diagonal face east
   of it; in `v3 t488.5` the return from x 0.15 to the east wall is 0.28–0.32. I could not make one plan of
   the return, the 45-degree face and the east wall from the two views; the corridor width does not depend
   on it.
3. **Yellow room ceiling**: same plane as the corridor (2.60) or 0.10 lower (2.50)?
4. **Arch wall line** 11.20..11.50 (present) or 11.30..11.60 (this audit, single frame; agrees with the
   second-floor reading before it was averaged).
5. **French door heights** in the blue bedroom (transom 1.90 or about 2.0).
6. Everything listed as not audited in the scope paragraph, including bed sizes (double or king) and the
   balcony.

## Verification

Verifier pass on the ten proposed changes (`dims_1-01` .. `-10`). Every item was measured again on stills
the survey did not use (v3 t44, t46, t56, t61, t487.5, t502, t506, t546, t548; v4 t20, t22; 1080 x 1920,
`ffmpeg -ss`), before reading sections 1-5 above. Scratch: stills, grids and zooms in
`reference/work/r3_dims_1_v/` (private); scripts in `build/r3/dims_1_v/` (`sv.py` single-view metrology,
`vp.py` / `ls.py` vanishing points and line segments from LSD, `m56*.py`, `m46.py`, `m487*.py`).
Calibration: principal point at the centre, f from each frame's own orthogonal vanishing points (795-865;
results are quoted over f 780-860 where they depend on it). No Blender preview was rendered: every verdict
is against `spec/house.json`.

| id | verdict | value to use | my measurement (reference, frames, ratio, result) |
|---|---|---|---|
| dims_1-01 | **accept** | `green_bedroom.ceilingZ` 6.19 (2.77); cornice underside 2.69 | Reference: opening of the closed sliding door `d_green_slide`, carpet to head lining 1.99, read up its west jamb to the cornice, cross-ratio with the vertical vanishing point. v3 t546 (jamb base y 1372, head 768, cornice underside 518, Vz y 8148): underside **2.72**; v3 t548 (1400 / 755 / 489, Vz y 9783): **2.73**. Ceiling from the apparent top edge of the cornice (projection 0.08): 2.79-2.82. Vz +/- 15 % moves the result 0.02. Mine is 0.03 above the survey's 2.69, inside its +/- 0.04; the present 2.85 is outside both. |
| dims_1-02 | **adjust** | east wall face **x 0.47** for corridor and bay, partition 0.10 to 0.57 (centreline 0.52), as proposed. Chamfer legs 0.07, not 0.14: **(0.54, 8.73)-(0.47, 8.80)**; the riser return follows it. West wall, pier, radiator unchanged | (a) Bay width in the plane of the `d_blue` wall, scale = the door opening height 1.99 (floor to head lining), v3 t56: skirting corner to skirting corner **1.087** at the door wall, 1.07 at the pier (f 780-860 changes it by 0.002); plus two skirtings = **1.12 +/- 0.03** wall to wall. The same scale returns the opening as 0.745 wide (stop to stop of a 762 leaf), which checks it. (b) No jog at the arch: the wall / skirting-top line of the bay east wall (LSD segment 139 px long) extended 150 px south lands 2-3 px (0.01 m) from the same line on the corridor wall south of the pier; a 0.15 jog would be 50 px. West side: bay wall and corridor wall within 0.02. (c) Piers 0.065 (east) and 0.08 (west) proud. (d) The 45-degree face, v3 t46 looking straight down from the quarter landing (nadir from three vertical edges, scale = landing width): face 0.09 long, legs about 0.07 x 0.05. See note 1 for the riser return. |
| dims_1-03 | **accept** | `yellow_room` west face x 0.57 (2.53 wide) | Knock-on of -02; not measured inside. Consistent with the room's own tolerance (2.75 +/- 0.25, `yellow_room.md`) and with the utility / WC below (0.60..3.10). X chain at y 10: 1.12 + 0.10 + 2.53 = 3.75 = -0.65..3.10. |
| dims_1-04 | **accept** | `blue_ensuite` west face x 0.57 (2.33 wide); recess east face x 0.47 | The bay east wall is measured (-02); recess and en-suite share that partition. 2.33 is inside the en-suite's own range (2.25-2.40 by fixture arithmetic, `blue_ensuite.md` doubt 1: a 0.70 bath gives 2.35). Door margins seen from the bay, v3 t56: west wall to opening 0.23, opening 0.745, 0.15 to the east wall = 1.12. |
| dims_1-05 | **accept** | `a_landing1` width 1.00, centre x -0.09 | v3 t56, same scale as -02(a): between the pier reveals at the skirting bases 0.93, at the springing **0.97 +/- 0.03** (0.96-1.01 over f 780-860 and the two pier depths). Arch axis within 0.01 of the corridor axis. |
| dims_1-06 | **adjust** | crown **2.12**, springing **1.62** (semicircle, radius = half the width); `height` 2.12 | v3 t56, points on the arch wall's south face (depth from the pier bases): crown **2.09-2.13**, tangent points 1.62-1.68. The intrados traced by edge scans fits a semicircle of radius = half the opening to 5 px except near the springing, so springing = crown - 0.49. The proposed 1.74 with a 1.00 opening would put the crown at 2.24; the present 1.65 was nearer. |
| dims_1-07 | **accept** | `landing1_rear.ceilingZ` 5.64 (2.60) | v3 t56: wall / ceiling line on the arch wall (strongest edge in column scans at x 200 / 400 / 600, a straight line) on the south-face plane, door-height scale: **2.58-2.61** (f 801-830; 2.56-2.64 over f 780-860), level to 0.01 across the wall. |
| dims_1-08 | **adjust** | `w_arch1` **thickness 0.12**, centreline **y 11.42** (faces 11.36..11.48); `landing1_arch.thickness` 0.12; bay 0.91 deep | v3 t56, floor points, door-height scale: south face **1.03 +/- 0.04** from the `d_blue` wall face (1.02-1.07 over f 780-860; survey 1.10 +/- 0.06). Thickness, four cues in two frames: pier reveal skirting 0.13 (t56); the bay skirting reappears from behind the east pier where a 0.10-0.13 pier predicts, not where a 0.30 pier would (t56); soffit at the crown, far / near depth ratio 1.111 at about 1.0 m = 0.11 (v3 t61), 0.10 (t56); the dado returning round the west pier is about as long as the pier is proud (t61). So the bay is **0.91** deep (the present 0.89 stands) and it is the wall that is thin. The proposed 0.30 wall at 11.30..11.60 with a 0.79 bay is not what the frames show. |
| dims_1-09 | **reject** | keep sill 0.70, height 1.85, `transomBar` 2.00 (and the cheek windows) | v4 t20, bay front wall seen square on, floor line 1155 px, cornice underside 578 px taken as 2.69-2.71, cross-ratio with Vz (y 6047): opening head (arris of the reveal) **2.52-2.54**, transom centre 1.99-2.00 (1.94 without the pitch correction), frame bottom 0.71-0.77. The wall strip between cornice and window head is 41 px of 577 = 0.18-0.19 (same proportion in v4 t22), not 0.26. The survey's 2.43 is the top of the glass of the fanlights (645 px here = 2.43); the frame head member is above it. The street-side notes agree with the present head (`front.md` item 14: keep; `dims_envelope.md`: frame 3.98..6.00). |
| dims_1-10 | **reject** | keep 0.84 x 0.60 until it can be placed | The depth is real: v3 t46 (near-vertical view, f-independent) shows at least 1.23-1.40 landing widths of riser between the top newel and the north-west corner, against 0.71 modelled; v3 t487.5 gives 0.9-1.15 m depending on the scale. But neither placement fits what is measured around it: a north wall at 9.17 adds 0.14-0.44 to a rear chain that is already 0.30 over (`RECONCILE2` P1), a nosing at 7.69 leaves the flight eleven goings of 0.19. Not applicable as proposed; see note 3. |

### Notes for the reconciler

1. **Stairwell edge (open, outside the proposals).** The strip between the west wall and the stairwell edge is
   **0.89-0.95** wide, not 0.80: (a) v3 t502, looking south along the strip, floor edges carried to the
   `d_green` threshold through the vanishing point, scale = the door opening 0.75: west skirting face to the
   carpet edge at the balustrade capping 0.87, + skirting = 0.89 +/- 0.03, and the door's west stop is 0.50
   from the west wall (0.38 modelled); (b) v3 t487.5, looking south from the arch, camera height fixed by
   the dado (top 1.03 above the floor, from the door-scaled v3 t56): riser line to west skirting 0.92-0.94.
   From the same riser line the corridor east wall is 0.13 (v3 t46) to 0.21 (v3 t487.5) east, and the riser
   return to the 45-degree face 0.15-0.20 long (the survey's open question 2 is the same puzzle). With the
   west wall at -0.65 and the east wall at 0.47 that puts the stairwell edge / top newel / riser at about
   **x 0.27-0.30**, not 0.15: a stair about 0.70-0.75 wide where 0.84 is modelled, or a wall beyond it that is
   not where the model has it. I did not check the ground floor (passage 0.80 / stair 0.84 were not
   re-measured this round either). Until that is settled, -02 leaves the riser return in the model at 0.39
   (x 0.15..0.54) against 0.15-0.20 seen.
2. **Knock-ons of the accepted changes.** -02 / -03 / -04: `w_corr_yellow`, `w_bay_ensuite`,
   `w_recess_ensuite` centreline x 0.52; `w_arch1` b, `w_main_rear_1a` a, `w_yellow_n` a, `w_ensuite_n` a,
   `w_blue_s` b to x 0.52; `d_yellow` centre / hinge x 0.52; `v_ql_n` and the `steps_ql_rear` return to
   x 0.54. -07: `landing1_downstand` becomes z 5.64..5.77 (0.13, not 0.28); `landing1_pier_w` and
   `landing1_chamfer` tops 5.64; `w_corr_yellow` and `w_arch1` height 2.60; the yellow room keeps 5.49. The
   floor zone under the second floor (6.02) becomes 0.38. -01: zone under the loft floor 0.30. -08: the
   corridor's east wall runs on to y 11.36; `a_landing1` keeps its wall.
3. **Y chain (not settled).** Seen from v3 t56 the north architrave of `d_yellow` is 0.20 south of the arch
   wall's south face; with -08 the model shows 0.37. So either `d_yellow` and the yellow room sit about
   0.17 too far south, or the `d_blue` wall is 0.17 too far north (it would then stand on the dining room's
   south wall, 12.23..12.36). Together with -10 this says the first-floor Y chain between the top nosing and
   the `d_blue` wall needs one more pass with a reference that spans it; I could not get a trustworthy long
   distance along the corridor (v3 t487.5 puts the two steps 4.6 m from the arch against 3.07 modelled,
   which cannot be right, although its near field checks out: level radiator top and dado, pier end at 1.3).
4. Small things seen on the way: dado top 1.03 above the rear floor (bay east wall, v3 t56; the survey has
   0.96-1.00); skirting 0.17-0.19 high; the west pier is about 0.05 proud by its skirting (0.10 modelled);
   the corridor radiator has 12-13 sections; the tread between the two steps looks deeper than 0.25 from
   v3 t487.5 and v3 t500 (not measured).

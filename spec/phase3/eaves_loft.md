# Phase 3 survey - eaves storage and the knee walls of the Slate Room (`eaves_loft`)

Surveyor notes for round 3. Footage: **v12** (all 122 frames read; full-resolution stills of every second in
`reference/work/r3_eaves_loft/hr/h_NNNN.jpg`, frame N = t N-1 s) and, for cross-checks, **v5** t 243-253 and the
round-2 stills `reference/work/p2_second_front/hr_*.jpg`. v12 is silent. Model looked at: `spec/house.json`,
`spec/rooms/eaves.md`, `spec/rooms/loft_office.md`, `blender/rooms/eaves.py`, `blender/lib/joinery.py::_hatch`,
and the published stills `docs/renders/eaves_front_tunnel.jpg`, `eaves_rear_r_in.jpg`, `loft_office_west.jpg`,
`loft_office_desk.jpg`. **No preview build was run** (the published stills show the same geometry).

Frame: world X, Y of the brief; `z` = height above the loft floor (world Z 6.49) unless "world Z" is written.
"Leaf pair width W" is the unit of the rectified hatch drawings below.

## 0. What v12 shows, in order

| frames | content |
|---|---|
| 1-6 | Slate Room, front knee wall: east hatch closed, bookcase, shredder, SE corner (dark east wall, basket trolley), west wall beyond |
| 7-14 | east hatch: west leaf opened, then east leaf; architrave and outer bead close up; view in, dark |
| 15-36 | **inside the front void / bay-gable tunnel**, light on: store towards the gable end (19-22), back towards the hatch (24, 25, 29), west low void under the main lining (17, 18, 26-28, 34-36), east low void (23, 30-32), switch + double socket (36) |
| 37-45 | Slate Room: carpet, rear knee wall and roof window (40), west wall (41, 42), SW corner with the west hatch (43-45) |
| 46-69 | west hatch: west leaf opened; west low void to the party wall (49-55); along the void eastwards to the tunnel (56-60); hatch joinery (64-68); knee wall by the SW corner (69) |
| 70-75 | lobby, door, built-in cabinet, rear knee wall with the rear hatch |
| 76-118 | **rear void**: both leaves opened (76-80), platform, step with double nosing, upstand board, lower floor, lining landing on the floor (83-102), light and switch (88-89, 111-116), west end wall (103-110) |
| 119-122 | rear hatch closed: leaf edge, knobs, architrave, skirting |

## 1. How the scale was obtained (read this before trusting any number)

1. **Wall plates inside the front void** (v12 f25, sharp, camera square to the knee-wall back): a 1-gang switch
   (86 x 86) and a double socket (146 x 86) on the knee-wall back 0.17 m west of the east hatch. Their four sides
   measure 51 x 47.5 px and 78 x 39 px. A pinhole fit (f 860 px at 1080 x 1920, also run at 760 and 960 - the wall
   results move by < 5 mm) gives the camera 1.33 m from the wall, 1.47 m above the void floor, pitched 16 deg down, and
   on the wall plane: switch centre z 0.79, socket centre z 0.37, **hatch head (void side) 0.93**, sill top 0.11,
   **top of the vertical wall above the hatch ("crease") 1.28**, main lining meeting the knee wall at 1.00,
   **opening between the lining faces 1.16 wide**, about 0.99 between the hinge edges of the frame. All "above the void
   floor". Reading error of the plates +/- 1.5 px = +/- 3 %; I give +/- 0.05 m on the heights.
   Through the opening the room carpet is visible right up to the head edge: the room-side clear opening is therefore
   not lower than 0.89 above the void floor (a lower frame rail would show as a white band; it does not).
2. **Room side** (v5 t248 = v5 f249, sharp and nearly frontal on the east hatch; rectified with f 860, the four leaf
   corners give an 89 deg rectangle): leaf pair **W : H = 1.16 : 1** (1.13-1.19 for f 960-760). In units of W:
   leaf height 0.855, carpet 0.07 below the leaf bottom, architrave outer edge 0.035 outside the leaves, outer panel
   bead 0.08 outside (sides) / 0.075 above, **start of the ceiling slope 0.224 above the leaf top**, knobs 0.172 below
   the leaf top and 0.10 from the meeting edge.
   W itself: a toolbox organiser (440 x 332 x 119, standing on its long edge against the wall beside the hatch, wall
   contact at 0.34 W) gives W 0.91-0.97; a cutting mat leaning on the other side (top at 0.63 W; A2 = 0.60 high) gives
   0.94; the void-side frame opening (0.99 between hinge edges, lay-on leaves) gives 0.99-1.01.
   **Adopted W = 0.96 +/- 0.05.**
3. The two routes agree on the leaf top: 0.925 W = 0.89 above the carpet; 0.93 above the void floor, which is about
   0.04 below the carpet surface (sill top 0.11 above the vinyl, 0.07 above the carpet).
4. **A contradiction I could not fully remove.** The west wall seen in round 2 (`hr_346`, v5 f346) scaled by the
   large flag as a 5 x 3 ft flag (0.91 wide) and treated as frontal gives only 0.87 for the knee wall at the SW
   corner - this is where the present 0.92 comes from. It is reconciled if that wall is not frontal in the still
   (corner about 20 % farther than the large flag): the small ensign by the corner then measures 0.58 x 0.90, a
   standard 3 x 2 ft flag, the radiator 1.27 long (20 oval columns at 63 mm - the pitch already in the room spec) and
   the knee wall 1.05-1.10. I take that reading, because the plates are the only hard reference in the whole area,
   but the reader should know the front knee height rests on it. A second plate-based reading of the opening height
   from an oblique frame (f26) gave 0.67-0.72 instead of 0.82; I keep 0.82 from the square-on frame and widen the
   tolerance downwards.

## 2. Inventory - what the footage shows and the model lacks or has wrong

### 2.1 Eaves hatches (all three are **pairs**, hinged on the outer stiles, opening into the room)

Model now (`joinery._hatch`): a plain flat frame 75 / 50 mm, flush leaves 0.45 x 0.60 (front) and 0.47 x 0.95 (rear),
knob at mid height (front) / z 0.80 (rear) 60 mm from the edge, frame z 0.15-0.85 (front), 0.17-1.20 (rear).

Footage (f1, f7-14, f44-48, f64-68, f73-80, f104-109, f118-122; v5 t245-248):

- **Leaves**: flat white 18 mm boards (melamine / painted MDF, square edges), lay-on. Two **concealed nickel cup
  hinges** per leaf with cruciform mounting plates screwed to the inner face of the frame stile, about 0.10 from the
  leaf top and bottom (f8, f13, f14, f104, f107, f113-116). Leaves swing about 95-100 deg (f8-13, f48, f77-80).
- **Knob**: polished-brass mushroom knob, about 30 mm, **in the upper quarter** of each leaf: 0.165 below the leaf top
  and 0.095 from the meeting edge, both leaves, all three hatches (f1, f44-46, f65-68, f74-76, f119-120). Its fixing
  screw shows on the inside face (f8, f11-13).
- **Architrave**: white ogee / stepped moulding about 45 mm wide round the leaf pair on all four sides at the rear
  hatch and on head and sides at the front hatches, mitred corners, standing about 20 mm proud; seen from below it is
  a deep three-step section (f14, f80, f108-109).
- **Outer panel bead**: a second, thin applied moulding (about 20 mm) forming a rectangle about 80 mm outside the leaf
  edges at the sides and 75 mm above the leaf top (35-40 mm of flat wall between it and the architrave). Its two
  uprights run down to the skirting. Present at all three hatches (f1, f8, f10, f12-13, f43-46, f69, f73-75, f121-122).
  This is the "panel moulding" of the knee walls; there are **no other panels** on the visible parts of either knee
  wall, **no dado rail and no capping rail** - the horizontal moulding seen above the doors in the close-ups is the
  architrave head.
- **Bottom**: front hatches - one moulded member about 65 mm high between the carpet and the leaf bottom (the skirting
  profile carried across; f8, v5 t248). Rear hatch - bottom architrave on a skirting about 0.10 high, leaf bottom at
  0.21 (f77, f118-120).
- **Inside**: a white lining through the wall (wall 0.11-0.12 thick), a white sill ledge; on the void side the
  plasterboard is cut wider than the frame (1.16 against about 1.00) with a rough edge (f24-26, f36).

Sizes (W = 0.96):

| | leaf (each) | leaf z | architrave outer (w x z) | outer bead rectangle | knob z |
|---|---|---|---|---|---|
| front east, front west | **0.48 x 0.82** | 0.07 - 0.89 | 1.04 x 0.03 - 0.93 | 1.11 wide, top at 0.96 | 0.72 |
| rear | **0.48 x 0.88** | 0.21 - 1.09 | 1.04 x 0.17 - 1.13 | 1.11 wide, top at 1.16 | 0.93 |

Rear pair: rectified in f74 (W : H = 1.09 : 1, floor 0.215 W below the leaf bottom); its W was not measured
independently - a switch plate seen beside the jamb in f115 bounds the clear height to 0.77-0.87, which fits 0.88
leaves.

### 2.2 Position of the east front hatch

The tunnel under the bay gable is centred on the east hatch within 0.08 m (f25: wall above the hatch spans -0.69 ...
+0.53 about the hatch centre; ceiling slot centred +0.04; f24 and f29 agree). The bay, and so the tunnel, is centred
on x 2.525. In the room the hatch has a toolbox (0.44) plus leaning boards between it and the corner trolley (v5 t245),
and a shredder and a cutting mat between it and the bookcase (v5 t248, v12 f1, f4). Both put the east hatch centre at
**x 2.60 +/- 0.10**, not 2.975. The west hatch (bead frame about 0.25-0.30 from the SW corner, f43, f69) fits its
present centre 0.175.

### 2.3 Front knee wall and the start of the slope

- White, flat, plain arris where the slope starts; **height 1.08 +/- 0.06** (0.224 W above the leaf top; void side:
  main lining meets the knee-wall back at 1.00, plus the rise across a 0.11 wall). Present 0.92.
- The ensign at the SW corner hangs from two pins at the slope line; as a 3 x 2 ft flag it spans z 0.10-1.02 (model:
  0.50 x 0.82).
- The bookcase top is level with the slope start (f4-6, f64): **1.05-1.08 high**, not 0.90. It is a rustic oak piece
  with framed-panel ends and a thick top with rounded front corners (f64).
- Skirting in this room is low: about **0.09** (f43, f69, `hr_346`), small moulded top - the room spec says 0.15.

### 2.4 Front void - main-roof part

- Lining pitch on the west party wall, f53 (vertical corner + lining/knee junction give the camera attitude; f 860):
  **33.7 deg** (+/- 3; 33.5-34.0 for f 960-760). Round-2 value 30 +/- 3.
- Lining at the knee-wall back **1.00** (model 0.86).
- The **west party wall** end is a plain plastered triangle, unpainted cream (sampled #969082 in shade, true about
  **#D8D2BE**), not white (f51-53).
- West stretch runs from the party wall to the valley; a loose white board leans on the knee-wall back near the
  tunnel (f34-36, f57-60; omit). A white cover strip (about 20 x 300 mm) is fixed upright on the knee-wall back
  0.12 west of the plates (f26, f36; optional).
- **East stretch exists and is used** (suitcases under the lining, f23, f30-32) - round-2 doubt 3 is settled; how far
  it runs east was not filmed.
- **Valley edges**: where the tunnel cuts the main lining the cut is closed by a white **fascia band about 0.28 high**
  (the roof build-up: lining underside 1.00, top 1.28 at the knee wall), running from the knee wall at about 0.75
  either side of the hatch centre (x 1.85 / 3.35) down and outwards towards the bay cheeks (f25, f26, f34-36, f57-59).
  The model has a knife edge.
- Switch and double socket on the knee-wall back, centred **x 2.23** (0.17 west of the void-side opening), **switch
  centre z 0.79, socket centre z 0.37** (model x 2.33, z 0.60 / 0.25). 1-gang rocker; double socket with two rockers.
- Floor: one grey concrete-effect sheet (vinyl) throughout, sampled #77746F lit / #151517 unlit, true about
  **#807D77**, lightly mottled. Where the lining meets the front wall was not seen (stored bags).

### 2.5 Bay-gable tunnel (the big error in the present model)

Model: A-section 2.20 wide at the floor, linings 43 deg, flat strip 0.30 wide at **z 0.90**, strip running up to the
hatch. Footage (f19-22, f24, f25, f29):

- The person **stands** in it: the camera is at z 1.36-1.55 in f24, f25, f29 and looks down on the hatch head.
- Looking back at the knee wall (f24, f25, f29): the knee-wall back is a **vertical white wall up to z 1.28**
  (+/- 0.05; 1.27-1.33 in three frames), 1.22-1.35 wide at that height between the tunnel linings, with the hatch in
  it. Above z 1.28 a lined **ramp** (the upper side of the main roof slope, which continues over the Slate Room) rises
  northwards between the two tunnel linings to the flat strip, where it ends at a dark **slot about 0.4 long x 30 mm**
  with a batten in it.
- **Flat strip: z 1.80 +/- 0.15** (two- and three-view triangulation of the slot from f24, f25, f29: 1.80-1.83; if
  the ramp follows the 30 deg main roof it is 1.98 - the views have a short baseline, so the ramp pitch is open
  between 30 and 50 deg). Strip width **0.42 +/- 0.08** (slot 0.34-0.52; 1.3-1.6 light diameters in f20).
- **Tunnel linings 52 deg +/- 5** (0.62 half-width at z 1.28, 0.21 at z 1.80; gable end wall in f21 reads 49 and 61
  deg on its two sides). Extended to the floor they are 1.63 either side of the axis - the outer faces of the bay
  cheeks (x 0.90, 4.15).
- **Gable end wall**: plain white trapezoid under the strip, no window (f19-22). Its lower part and the feet of the
  linings are hidden by storage.
- **Light**: one round white opal LED bulkhead with a deep rim on the flat strip (f20), about 0.25-0.30 diameter.

### 2.6 Rear void

- West end wall (x 1.35): plain white triangle against the stair dormer cheek, directly beside the hatch's west jamb
  (f103-110).
- **Platform** by the hatch: from the west wall to the step, from the knee wall north to a **white upstand board
  about 0.13 high** on which the lining lands (f83-85, f94-98, f102, f107-110, f117-118). A short return of the same
  board closes the triangle at the step end; a dark triangular gap shows behind it (f95-97).
- **Step**: straight, square to the knee wall, meeting it at the hatch's east jamb (x 2.35-2.40; f79, f80, f102);
  **double nosing**: two aluminium angle nosings side by side, each with a dark grey anti-slip insert about 30 mm
  wide - 75-80 mm in all - and an aluminium riser face (f85, f86, f90-98). Drop **about 0.07** (0.05-0.08, judged
  against the nosing and the upstand; model 0.12).
- **Lower floor** east of the step: the lining comes **down onto the floor** (no kerb) along a straight line from
  the step to the east wall, 0.3-0.4 m beyond the upstand (f86, f91-92, f95-99). The model stops the void at y 8.73
  with a 0.18-0.30 high strip of wall there.
- East end (x 4.30): plain white triangle (f87, f93, f100-101).
- Floor: the same grey concrete-effect sheet on both levels (sampled #5D5A53-#79756B, true about **#807D77**); the
  round-2 "pale upper / charcoal lower" was the lighting.
- **Light and switch** on the knee-wall back east of the hatch: switch (1-gang rocker) 0.13 from the jamb, x 2.58;
  round opal bulkhead next to it, centre x 2.83, same height. The bulkhead is small: **0.17 diameter** (2.0 and 1.8
  switch-plate heights in f115 and f89; model 0.26). Height about 1.0 (not re-measured).
- Lining pitch here: 28.4 deg (f101, east wall) and 38.6 deg (f109, west wall, a poor view): no better than the
  present 30.

### 2.7 Colours sampled in daylight (v12)

| surface | sampled | estimate |
|---|---|---|
| knee walls, hatch leaves, architraves | #DFE1E0, #DADBDB | #F2F2EF (unchanged) |
| slopes | #C9CBCA | #EDEDEA - reads a shade greyer than the knee wall in every frame |
| carpet | #858681 (f1), #A3A29D lit | **#B6B3AC** - a neutral silver grey in daylight; the published stills are creamier |
| east wall | #3A3F42 | #3B4046 (unchanged) |
| void linings | #D6D4C8, #C8C8C7 | #EFEEEA (unchanged) |
| bookcase oak | #716250 | #9A7B52 |

## 3. Dimension table

| item | house.json | present | measured | method | confidence |
|---|---|---|---|---|---|
| front knee wall height | `walls.w_knee_front.height` | 0.92 | **1.08 +/- 0.06** | section 1: plates in f25 -> leaf top 0.89; rectified v5 t248 -> slope 0.224 W above it; lining 1.00 at the wall back | medium |
| front hatch frame height | `h_eaves_front_w/e.height` | 0.70 | **0.90** (leaves 0.82 +0.03/-0.10) | plates f25 (opening 0.11-0.93), rectified pair 0.855 W | medium |
| front hatch sill | `h_eaves_front_w/e.sill` | 0.15 | **0.03** (leaf bottom 0.07) | rectified v5 t248; f8 | medium |
| front hatch frame width | `h_eaves_front_w/e.width` | 1.05 | 1.04 (leaf pair 0.96 +/- 0.05) | section 1 | medium - no change |
| east front hatch centre x | `h_eaves_front_e.center[0]` | 2.975 | **2.60 +/- 0.10** | tunnel axis in f24/25/29; objects either side in v5 t245/t248 | medium |
| west front hatch centre x | `h_eaves_front_w.center[0]` | 0.175 | 0.15-0.20 | gap to the SW corner, f43/f69 | low - no change |
| rear hatch frame height | `h_eaves_rear.height` | 1.03 | **0.96** (leaves 0.88) | rectified f74 (W:H 1.09) with W 0.96; f115 switch | low-medium |
| rear hatch sill | `h_eaves_rear.sill` | 0.17 | 0.17 (leaf bottom 0.21) | f74, f118-120 | medium - no change |
| rear knee wall height | `walls.w_knee_rear.height` | 1.42 | about 1.43 | architrave top 1.13 + 0.3 leaf heights, f73 | low - no change |
| main lining pitch | `roof.planes.main_front/main_rear.pitchDeg` | 30 | 33.7 (front, f53); 28.4 / 38.6 (rear) | end-wall junction lines, f 860 | low - no change, see open questions |
| lining at the front knee-wall back | follows `main_front` (-0.31) | 0.86 | **1.00 +/- 0.05** | plates f25 | medium |
| bay tunnel strip height | `features.eaves_bay_tunnel.z[1]` | 7.39 (0.90) | **8.29 (1.80 +/- 0.15)** | camera height 1.47 from plates; triangulated slot | medium that it is >= 1.6; low on the exact value |
| bay tunnel lining pitch | `roof.planes.bay_gable_w/e.pitchDeg`, `roof.gable` | 43 | **52 +/- 5** | widths at z 1.28 and 1.80; end wall f21 | low-medium |
| bay gable ridge | `roof.gable.ridgeZ` | 8.295 | about **8.9 +/- 0.15** (derived: strip 8.29 + 0.21 x tan 52 + 0.33 build-up) | derived | low - for the front elevation |
| tunnel floor width | `rooms.eaves_front.polygon` (x 1.43..3.63) | 2.20 | >= 2.6; linings aim at x 0.90 / 4.15 | derived from the lining planes | low |
| rear void north limit, lower floor | `rooms.eaves_rear.polygon` (y 8.73) | 8.73 | lining lands on the floor **0.3-0.4 beyond the upstand**: y 8.85-9.25 | geometry: (1.36 + step) / tan pitch; f91-98 | low-medium |
| rear platform upstand | - | wall strip at 8.73 | board 0.13 high at y 8.5-8.8 | nosing-width ratio f98 | low |
| rear floor step | `features.eaves_rear_step.zLow` | 6.37 (0.12) | 0.07 +/- 0.03 | nosing / upstand ratios f95-98 | low |
| rear step line x | `features.eaves_rear_step.line` | 2.35 | 2.35-2.40 | meets the hatch east jamb, f79-80 | medium - no change |
| void floor level, front | `rooms.eaves_front.floorZ` | 6.49 | about 6.45 | sill 0.11 above vinyl, 0.07 above carpet | low - no change |

## 4. Proposed spec changes and what they push

1. `w_knee_front.height` 0.92 -> **1.08**. The ceiling plane of the Slate Room then no longer fits (0.92 at y 2.54 was
   an input of the 30 deg plane). Smallest consistent change: keep the knee wall where it is and the pitch at 30,
   raise the front plane by 0.16 - `rooms.loft_office.ceiling.front_slope` c0 5.9435 -> **6.1035**, its north edge and
   the flat's south edge y 4.62 -> **4.34** (flat strip 1.04 wide), `roof.planes.main_front` c0 6.2528 -> **6.4135**
   (front gutter 6.50 -> 6.66, ridge line 0.14 forward and 0.08 up). The front void lining then stands 1.02 at the
   knee-wall back (measured 1.00) and **0.16 above the floor at the front wall face** - a low upstand instead of the
   feather edge (round-2 doubt 1 suspected one). What gives way: the roof, i.e. the envelope and the front elevation's
   eaves height - to be confirmed against the street footage. The alternative (planes untouched, slope 26.6 deg from
   1.08 to the flat at y 4.62) contradicts every pitch reading.
2. `h_eaves_front_w`, `h_eaves_front_e`: height 0.70 -> **0.90**, sill 0.15 -> **0.03**; `h_eaves_front_e.center`
   x 2.975 -> **2.60**. Nothing else moves; the bookcase stays between the hatches (0.82..1.72) and the shredder zone
   narrows.
3. `h_eaves_rear`: height 1.03 -> **0.96** (top 1.13 instead of 1.20).
4. `features.eaves_bay_tunnel` z top 7.39 -> **8.29**; tunnel linings 52 deg aiming at the bay cheeks; flat strip 0.42;
   the knee-wall back carried up to z 1.28 inside the tunnel with the ramp above. `roof.gable` / `bay_gable_w/e` must
   rise to contain it (ridge about 8.9, pitch about 52) - envelope, front elevation to confirm.
5. `rooms.eaves_rear.polygon`: lower-floor part (x 2.35..4.30) north edge 8.73 -> **9.05**, platform part unchanged
   with the upstand board; gives way: `w_addition_s_2` (0.56 thick placeholder, y 8.73..9.29) thinned from the south
   for x 2.35..3.25, and the wall-head zone east of it.
6. Not proposed (evidence no better than the present value): rear knee 1.42, roof pitch 30, step line x, front hatch
   width, west hatch position, void floor levels.

## 5. Notes per unit

### loft_office (Slate Room)
- Hatch joinery as 2.1: leaves 0.48 x 0.82 (front, z 0.07-0.89) and 0.48 x 0.88 (rear, z 0.21-1.09), 18 mm, two
  concealed cup hinges per leaf on the outer stiles, brass knob 30 mm at 0.165 below the leaf top and 0.095 from the
  meeting edge; ogee architrave 45 mm, mitred, 20 mm proud; outer applied bead 20 mm, 80 mm outside the leaves at the
  sides and 75 mm above, uprights down to the skirting. Leaves open 95-100 deg.
- Front knee wall 1.08 high, plain arris, no rail. Skirting 0.09 with a small moulded top (rear knee wall: 0.10 under
  the hatch's bottom architrave).
- East front hatch centred x 2.60; everything between it and the east wall moves with it (trolley stays in the
  corner x 3.75..4.30; about 0.6 of plain wall between).
- Bookcase 1.06 high (top at the slope line), framed-panel ends, thick top with rounded front corners, three shelves.
- Ensign at the SW corner of the west wall: 0.61 x 0.91 hung vertically, pinned at the slope line (z 0.10-1.02), badge
  omitted as before.
- Carpet a neutral silver grey (#B6B3AC), slopes a shade greyer than the white knee walls.
- Radiator: 20 oval columns, about 1.27 x 0.57 (spec 1.25 x 0.52) - within tolerance, no change needed.

### eaves
- Front, tunnel: section as 2.5 - vertical knee-wall back to z 1.28 above the east hatch, ramp to the strip, strip
  0.42 wide at z 1.80, linings 52 deg, slot 0.4 x 0.03 where the ramp meets the strip, bulkhead 0.28 diameter on the
  strip. Valley cuts closed by a 0.28 high white fascia band.
- Front, low voids: lining 1.00 at the knee-wall back; west party wall end cream plaster (#D8D2BE); east stretch
  open. Switch z 0.79 and double socket z 0.37 at x 2.23 on the knee-wall back. Rough plasterboard edge round the
  hatch opening (1.16 wide on this side), white lining, sill ledge 0.11 above the floor.
- Rear: platform x 1.35..2.35 with a 0.13 white upstand board at its north edge under the lining (return piece and
  dark gap at the step end); double aluminium nosing 78 mm wide with two dark inserts and an aluminium riser, drop
  0.07; lower floor running on until the lining lands on it; bulkhead 0.17 diameter at x 2.83, switch at x 2.58, both
  on the knee-wall back.
- Floors: one grey concrete-effect sheet vinyl, #807D77, in both voids and on both rear levels.
- Storage (declutter): a few plain closed boxes and two plain suitcases as now; one open-topped plain carton by the
  rear step and a few flattened cartons leaning on the rear east wall are what is really there (f86-93, f100-101).

### shell
- `w_knee_front` 1.08; hatch holes as section 4; the knee-wall back inside the tunnel is a full-height wall to z 1.28.
- Skirting height in `loft_office` 0.09.

### envelope
- Front main roof plane +0.16 if change 1 is accepted; bay gable ridge about Z 8.9 at about 52 deg so that the tunnel
  (lining strip at world Z 8.29) fits under it. Both need the street footage to agree.

## 6. Open questions

1. **Front knee wall 1.08 or 0.92.** The plate chain says 1.08; a frontal reading of the round-2 west-wall still says
   0.87-0.92. A frame with a known-size object standing against the front knee wall would settle it.
2. **Pitch of the main roof**: 33.7 deg on the front party wall (one frame), 28-39 at the rear. If it is 33-34 the
   room section changes again (flat strip, ridge height).
3. **How the Slate Room ceiling meets the higher knee wall** - wider flat strip (proposed) or another plan; the flat
   strip was not filmed in v12.
4. **Tunnel**: exact strip height (1.65-2.0), ramp pitch (30-50), floor width and whether the linings reach the floor
   or a low upstand at the bay cheeks; length to the gable end (not re-measured, storage in the way).
5. **Gable outside**: ridge height and pitch implied above are derived from the inside only.
6. **Rear void depth**: where the lining lands (y 8.85-9.25), the upstand's y, the step height (0.05-0.12); and what
   stands north of it (the placeholder wall).
7. Whether the front lining ends on an upstand at the front wall; how far the east low void runs.
8. Rear hatch leaf width not measured independently of the front ones.
9. Heights of the rear light and switch (about 1.0) not re-measured.

## Verification

Measurements by the verifier, made before reading sections 1-6. Scratch: stills in `reference/work/r3_eaves_loft_v/`,
scripts in `build/r3/eaves_loft_v/` (`edge.py` sub-pixel edge fits, `bundle.py` pinhole fit of the knee-wall back,
`rect.py` wall rectification from a rectangle, `gable.py` gable-wall section). No preview build was run and nothing
in the model was changed.

### V1. How I measured (frames and references differ from the survey where the footage allows)

1. **Front void, plates again but other frames and a different fit.** v12 t 23.9 s and t 24.5 s (between the 1 fps
   frames; the survey used f24, f25, f29). Edges of the opening (head, void floor line, both lining arrises) and
   the eight plate sides fitted to sub-pixel; unknowns solved together: camera pose, opening width and head height,
   plate positions (f 860; 800-920 moves the wall results by under 1 %). The wall is **not square to the camera**:
   head and floor lines converge (yaw about 10 deg). The widths in section 1 ("1.16 between the lining faces", "0.99
   between hinge edges") are the plate ratio taken without that convergence and are about 20 % too large; the
   heights are less affected. The plate outline seen from above and from the side includes part of the 9 mm plate
   thickness, so I ran the fit with 86 / 146 mm (lower bound) and 91 / 152 x 94 mm (upper bound).
   Above the void floor: sill arris **0.10-0.11**, head arris **0.83-0.93 (0.88)**, clear opening **0.78 +/- 0.04**
   high and **0.84-0.95 (0.90)** wide between the lining arrises, main lining at the knee-wall back
   **0.92-1.01 (0.97)**, top of the vertical wall above the hatch **1.14-1.24 (1.19)**, camera 1.36-1.45 high and
   1.05-1.10 from the wall. Sill depth (wall thickness) from the same pose 0.11. The values in section 1 (0.93,
   1.00, 1.28, 1.47) sit at or just above my upper bound.
2. **Room side, vertical proportions without focal length or scale** (leaf pair mapped to a unit square; ratios
   along the vertical are then exact). Front east hatch, two frames of my own (v12 t 0.2 s, v5 t 249.0 s): slope
   start **0.260 / 0.260** leaf heights above the leaf top, carpet **0.089 / 0.084** below the leaf bottom, so
   **front knee = 1.346 x leaf height**; leaf pair W : H **1.18 / 1.14** (f 860). Rear hatch (v5 t 314): slope start
   **0.239** above, carpet **0.215** below, so **rear knee = 1.454 x leaf height**; W : H **1.10**.
3. **A hard scale standing against a wall of the room: the east gable.** v5 t 182 and t 182.5 (sharp, nearly
   frontal): the wall rectified by the framed periodic-table poster. Result in both frames: rear knee corner / apex
   = **0.58** (vertical ratio, no focal length), both slopes **35.3-35.6 deg** to the flat ceiling line, flat strip
   1.28 and rear slope run 1.99 poster heights. With the apex at 2.12 (door and cabinet, round 2) the poster frame
   comes out 0.94 x 0.62, i.e. a 36 x 24 inch poster in a narrow frame, which confirms the 2.12 independently. In
   metres: **rear knee 1.23**, rear run 1.24, flat 0.80.
4. **TV wall** (v5 t 342, rectified by the TV rectangle, aspect 1.72 at f 860): rear knee corner = 2.23 TV heights,
   slope about 31 deg (poor fit). A 43-inch set gives 1.23, a 50-inch set 1.43.
5. **Rear void plate** (v12 t 114, grazing view of the east jamb with the switch 0.13-0.18 beyond it): clear opening
   0.71-0.79 (section 3 has 0.77-0.87).

The chain closes on one leaf size: front leaf pair 0.92-0.93 wide (void-side opening 0.90 plus lay-on), front leaf
0.80 high, front knee 1.346 x 0.80 = **1.07**; the same leaf width at the rear gives a rear leaf 0.84 high and a
rear knee of 1.454 x 0.84 = **1.23**, which is what the poster gives without using any hatch.

### V2. Verdicts

| id | verdict | value to use | my measurement | reason |
|---|---|---|---|---|
| eaves_loft-01 | **accept** | `w_knee_front.height` **1.08** | 1.07 +/- 0.04 by the leaf proportion (V1.2 with a 0.80 leaf), 0.99-1.04 from the lining at the wall back; centre 1.05 | Present 0.92 needs a leaf pair only 0.80 wide and a 0.69 leaf; the void-side opening alone is 0.78 high. Within the stated tolerance. |
| eaves_loft-02 | **reject** | keep front_slope c0 5.9435 / edge y 4.62 and main_front c0 6.2528 | pitch 35.5 +/- 1.5 deg both sides, flat 0.80, apex 2.12 (V1.3) | Derived, not measured, and built on a 30 deg pitch that the gable wall does not show. A 1.04 flat strip contradicts 0.80 measured in two frames. Outside, `dims_envelope.md` has the front gutter at 6.4-6.6, not 6.66. See V3 for what to do instead. |
| eaves_loft-03 | **accept** | height **0.90**, sill **0.03**; width 1.05 unchanged | leaves 0.46 x 0.80 at z 0.07..0.87, architrave outer 0.03..0.90; void-side clear opening 0.78 | Leaf bottom is 0.085 leaf heights above the carpet in two frames, so a 0.15 sill is out. Leaf height 0.80 +/- 0.03 is inside the proposed 0.82 +0.03 / -0.10. |
| eaves_loft-04 | **adjust** | `h_eaves_front_e.center` x **2.525** (= `roof.gable.ridge` x; move with it) | wall above the hatch between the valley cheeks spans -0.55..+0.56 (t 23.9) and -0.58..+0.64 (t 24.5) about the hatch centre, ridge slot centre -0.02 | The hatch is on the tunnel axis within 0.03. The -0.69..+0.53 of section 3 is the uncorrected yaw. Room side agrees: the shredder fills the gap to the bookcase. `front.md` wants the bay centre at 2.40; if that is adopted the hatch follows the ridge. |
| eaves_loft-05 | **adjust** | height **0.91**, sill **0.15** (architrave 0.15..1.06, leaves 0.46 x 0.84 at 0.18..1.02) **only together with `w_knee_rear.height` 1.23**; if the rear knee wall stays 1.42, keep 1.03 / 0.17 | V1.2 rear proportions with a 0.84 leaf; rear knee 1.23 +/- 0.04 from V1.3, V1.4 (43-inch), V1.5 | As proposed (0.96 under an unchanged 1.42 wall) the wall above the leaf would be 0.33, i.e. 0.38 leaf heights against 0.24 measured. The present 1.03 under 1.42 has the right proportions at the wrong scale. |
| eaves_loft-06 | **adjust** | z top **8.19**: strip 0.40 wide at **1.70** above the floor, linings **50 deg**, knee-wall back vertical to **1.20** above the east hatch, then the ramp | slot 1.65-1.70 for a 30-40 deg ramp (t 24.5), +/- 0.10 with the plate bounds; slot 0.35-0.42 long; wall-top half width 0.56-0.61 at 1.19 | Direction certain: the camera is 1.4 above the floor and looks up at the strip. 1.70 fits under the gable measured from the street (apex 8.7-8.75) with 0.24 rise and 0.28 build-up; 1.80 leaves 0.19. |
| eaves_loft-07 | **adjust** | `roof.gable.ridgeZ` **8.72**, bay_gable_w / e `pitchDeg` **50** | inside needs at least 8.19 + 0.24 + 0.25 = 8.68 | Not measurable from inside. `dims_envelope.md` (49 +/- 3 deg, apex 8.7 +/- 0.2) and `front.md` (about 50 deg, 8.75) measured it from the street; use those, not the inside-derived 8.9 / 52. |
| eaves_loft-08 | **reject** | keep north edge y 8.73 and `w_addition_s_2` | lining 1.23 - 0.07 at the knee-wall back falling at 35.5 deg lands on the lower floor about 1.7 from the wall back, y about 8.4 | The 9.05 is (1.36 + step) / tan 30, and both inputs fail V1.3. The landing line is inside the present polygon, and 9.05 would cut into the old rear wall of the main body (inner face 8.73). The upstand board and the lower floor running 0.3 beyond it are right as description and belong in the room module. |
| eaves_loft-09 | **reject** | keep zLow 6.37 (drop 0.12) | upstand return below the platform = 0.67-0.8 of the upstand height (v12 t 95, t 96); upstand at least 2 nosing widths in the same frame | No hard scale in these frames (the nosing width is assumed). With the 0.13 upstand of section 3 the drop is 0.09-0.10, more if the upstand is taller. 0.07 is not better supported than 0.12. |

### V3. Knock-on consistency

- **01 and 03 only show if the ceiling plane at y 2.54 rises with the wall.** The shell carves the room by the
  ceiling planes, so a 1.08 wall under a plane that is 0.92 there changes nothing visible, and a 0.90 hatch head
  would stand above the void lining (0.86 at the wall back). Stopgap that leaves the roof, gutter, ridge and flat
  strip alone: `front_slope` through (2.54, 1.08) and (4.62, 2.12), i.e. c0 **6.30**, cy **0.50**, and the
  `eaves_front` lining offset **-0.17** instead of -0.31 (1.00 at the knee-wall back, as measured; roof build-up over
  the front slope 0.15-0.31). It is a stopgap: that slope is 26.6 deg and the measured one is 35.5. I did not build
  it.
- **The room section does not close along Y.** Measured: apex 2.12, flat 0.80, 35.5 deg both sides, knees 1.07
  (front) and 1.23 (rear). That is 1.47 + 0.80 + 1.24 = **3.5 between the knee walls; the model has 4.05**. The rear
  half fits the present plan as it stands once the rear knee is 1.23 (rear knee 6.59, flat edge 5.38: 36.3 deg). The
  whole 0.58 is in the front run. Either the front knee wall is about 0.5 further north than 2.54, or the front slope
  is not one plane. The front gutter at 6.4-6.6 with 35.5 deg and a lining 0.97 high puts the knee-wall back at
  y 2.2-2.4, which argues for the wall staying where it is. I could not decide this: no frame shows the front knee
  corner and the flat strip in one wall plane.
- **Not in the proposal list but required by the same evidence:** `w_knee_rear.height` 1.42 -> **1.23**, the rear
  ceiling plane through (6.59, 1.23) and (5.38, 2.12), and with it the rear hatch of 05, the TV as a 43-inch set
  (0.97 x 0.55), and the roof pitch question already raised in `floor2_b.md` 2.2 (35 +/- 2.5 deg there).
- Sums along X with 04: west hatch frame -0.35..0.70, bookcase 0.82..1.72, east hatch frame 2.00..3.05, 1.25 to the
  east wall for the trolley and the organiser. No wall or level moves; no riser count is touched.
- 06 and 07 must go together: a strip at 8.19 does not fit under the present 8.295 ridge.

### V4. Not settled

1. Y position of the front knee wall and of the flat strip (above).
2. Front knee 1.05 or 1.08: the lining route and the leaf route differ by 0.06.
3. Rear leaf width was not measured against a plate; 0.46 rests on the three routes to the rear knee agreeing.
4. The rear step height and the rear landing line have no hard scale.
5. I did not re-measure the tunnel length, the west hatch position, or the void floor levels.

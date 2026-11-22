# Phase 3 — dimension audit of the envelope and the plot (`dims_envelope`)

Surveyor's notes, round 3. Footage: v8 (all 138 frames), v9 1-20 and 45-60, v11 17-196, v13 22-45 and
202-225, v2 150-366 and 884-1012 (sampled) with the rear still t = 249.5 s, v4 2-94 (sampled). Stills,
grids and montages: `reference/work/r3_dims_envelope/` (private); tools and the model previews
(`elev_{front,rear,flank}_r3dimsenvelope.jpg`): `build/r3/dims_envelope/`, `build/preview/`.
Frame of reference as BRIEF (metres, +Y into the house, +X to the right, Z up, ground-floor FFL = 0).
`v8 t63` means the full-resolution still at 63 s (= frame f_0064).

## 0. Verdict

- **Vertical scale: right.** The rear face measured on a fronto-parallel still with a hard scale gives the
  roof edge at **8.84 ± 0.15** (model 8.87), the first-floor door head at 5.34 (model 5.36), the ground-floor
  door set at 1.97 / 2.35 (model 1.97 / 2.32). The front gutter comes out at 6.4-6.6 (model 6.50). No storey
  level needs to move on exterior evidence.
- **Horizontal scale: right within about 3 % overall, but the east side is locally wrong by 0.1-0.4 m.**
  Rear face, brick junction to flank corner: **4.22 ± 0.08** (model: 3.90 from the "pier" at x -0.50, or 4.165
  from the party-wall centre line). The walls carry **external wall insulation** (about 0.10 m, section 2),
  which the phase-2 reconciliation did not know: flank and east wall are about 0.35 thick, not 0.30 / 0.23.
- **Wrong in the model, with direct evidence:** the bay's east cheek is only **0.10** behind the east wall
  face (model 0.38); the side alley is **1.15** wide (model 0.90) and was walked end to end; the rear render
  runs to the party line (no exposed pier on our side); the three ground-floor rear openings are spaced
  **1.45** apart, not 1.32; the study window is **1.53 x 1.63** (model 1.00 x 1.40); the bay gable is steeper
  and higher (about 49 deg, apex about 8.7; model 43 deg, 8.295).
- **Not settled:** the absolute X layout of the front (door set and bay lights), the main ridge height and
  pitch, the garden length and the main-block length by an exterior method. See section 6.

## 1. Scales and rulers (read this before using any brick count)

| ruler | value | how established |
|---|---|---|
| old stock / red brickwork of the terrace (rear pier, neighbours, party stack) | **course 84 mm (4 courses = 13 1/4 in), stretcher + joint 238 mm, Flemish module 358 mm** | v2 t249.5 rear pier: course pitch 7.95 px (autocorrelation, uniform from Z 3.3 to 8.5), perpend peaks at 22.5 px and 34 px; the same picture gives 94.5 px/m from the door set. **The 75 mm course of the brief does not apply to the old walls** (using it makes every height 10 % too small) |
| modern brick (front boundary wall, neighbour's rear extension, shed, fire pit) | course 75 mm, 225 mm module | neighbour's extension: 36-38 courses to the coping from the deck (v11 t188), 2.7-2.9 m, consistent with 2.95 at 94.5 px/m |
| rear French-door set | frame **1.19 wide** (standard 1190 unit), leaf 1.96-1.98 high | 112.7 px x 185 px in v2 t249.5; width / height ratio matches a 1190 unit; it fixes 94.5 +/- 1.5 px/m together with the brick lengths |
| kitchen back door | door part 2.04-2.09 high | scale 216-225 px/m in v11 t64 |
| gas meter box on the bay cheek | 0.41 wide | only a sanity check (it stands 0.2 proud of the wall) |

The phone picture is not exactly rectilinear near the frame edges; vanishing-point self-calibration gave
no usable focal length, so every result below is a ratio inside one plane, or a count.

## 2. Inventory — what the footage shows that the model lacks or has wrong

| # | item | world position / size | colour (sampled -> estimate) | frames |
|---|---|---|---|---|
| I1 | **External wall insulation on every sandstone-coloured wall** (flank F, face K, east wall E, rear R): render about 0.10 proud of the old brick face, stopping 0.25-0.30 above the paving on a **white base rail** (drip bead 40 high) with a **black recessed plinth** behind; white PVC stop bead at free ends | all `render_sandstone` facades; base rail underside Z about -0.02 on the alley side (paving -0.3), 0.22 above the flags on flank F | render overcast #C1BDA6 / #CEC59E, in sun-shade #8A7C61 -> keep **#D2C596**; rail #B9B8C1 -> #F2F2EE; plinth #31343B -> #2A2A2C | v8 t68-t81, v11 f133-f149, f171-f179 |
| I2 | **East wall of the main house is a blank rendered gable end** with a black dry-verge trim; fittings south to north: black cable from the bay cornice, vertical twin black conduit about 3 m from the street gate, small black vent grille (0.15) at Z about 1.8, **two cylindrical wall lights** (lit) at Z about 2.3, condenser on brackets at Z about 3.0-3.6 near the north end, **white 110 mm downpipe** with a swan neck near the north end standing on a concrete pad | `east_E`, x = east face, y 0.95..9.03 | as I1 | v11 f83-f105, f127-f149, v8 f83-f87 |
| I3 | **White / yellow junction at the front corner**: the white paint (bay cheek) runs 1.05-1.15 back from the bay front, then the insulation starts with a white return | junction y **0.95 +/- 0.08** (model: `east_E` starts at 0.74) | - | v8 t70 (cheek seen square: corner post 0.57 W, window frame W, wall 0.53 W, W = 0.50-0.55) |
| I4 | **Side alley**: plain concrete, 1.15 wide, open to the sky, between our east wall and the neighbour's yellow-stock flank wall; one inspection cover and the downpipe pad at the north end | x east face .. +1.15, y 2.3..9.0 | concrete #6A6B6B, algae green at the foot of the wall | v11 f73-f83, f113-f127 |
| I5 | **Street-end alley gate**: full-height boarded screen across the alley, 1.0-1.3 behind the white return: ledged-and-braced leaf about 0.85 x 1.9 in a post frame, opens **towards the street**, fixed boarded panel above to about 2.7 with a felt-capped top; long-throw lock at 1.1; a white meter box on the neighbour's wall beside it | y **2.3 +/- 0.3**, width = alley | boards #A09FA4 / #C0BFC4 -> pale warm grey **#BDB9B3** (as the garden gate) | v8 t80-t83, v11 f107-f113 |
| I6 | **Bay east cheek**: white, with the ground-floor cheek window (lower light with shutter + top light), the first-floor cheek window above, a white surface gas-meter box (0.41 x 0.56 x 0.21) under the ground-floor sill, a white twin-head security light at Z about 2.6, the bay cornice returning along the cheek and stopping against the yellow wall | cheek face 0.10 behind the east wall face | white #CAC9C4 -> #F2F2EE | v8 t39, t68-t72 |
| I7 | **East corner pilaster of the bay is a full reeded pilaster** like the west one, not a narrow strip: 0.44 +/- 0.03 wide with a 0.04 jamb to light 4 | bay front, east end | white | v8 t25 (projective fit over the 8 light edges, rms 0.7 px) |
| I8 | **Party-wall stack at the front eaves (west)**: unpainted red-brick upstand on the party line, 0.37 wide x about 0.45 deep, corbelled out at Z about 6.1, top about **7.7** with a flat stone cap; our white gutter stops against it; a lower grey step of the party parapet behind it | x -0.88..-0.55, y 0.3..0.75 | #4B3C36 (back-lit) -> #A4553A | v8 f15-f24, f113-f115, v9 t15 |
| I9 | **Main roof, rear slope over face K**: large-format fibre-cement slates (600 x 300, broken bond, about 250 gauge), black gutter immediately above the first-floor window head, black verge trim on the east edge | `main_rear` east of x flank | #909094 wet-sky reflection -> #474A52 | v13 t28 |
| I10 | **Rear face**: render to the party line; the bare brick beyond belongs to the neighbour. Shared stack 0.55 wide straddling the junction, top Z 9.7 | junction x = flank - 4.22 | stock #999798 -> #A99873 | v2 t249.5 |
| I11 | **Forecourt east side**: the setts stop about x 3.9; east of that a patched tarmac / concrete apron runs to the alley, with **two cast inspection covers** (0.6 x 0.45 each, side by side, about y -2.5) and a dark slatted **raised planter** (about 1.6 x 0.6 x 0.5) on the east boundary at the pavement; bins stand at the bay's east corner | x 3.9..5.8, y -5.2..1.0 | - | v8 f27-f42, f60-f66, v4 t49 |
| I12 | **Neighbour's rear extension** ends level with the north edge of our deck (not 0.85 short of it); a pale lattice / slatted fence continues to the shed; its roof is flat with a glazed pyramid lantern | boundary x -0.75, y 17.36..about 20.4 | - | v13 t216, v11 t188 |
| I13 | **Shed roof from above**: felt deck inside pale stone copings (0.25 wide) on the west, north and east parapets, white gutter along the south (veranda) edge | `buildings.shed.roof` | - | v13 f212-f217 |

Declutter / privacy: bins, cars and the lettering on the transom are in most of these frames; nothing of
them is recorded here beyond what the brief already lists.

## 3. Dimension table

Confidence: H = two methods or a count with a hard scale; M = one good method; L = single frame or a long
extrapolation.

### 3.1 Rear face R (v2 t249.5 and t250, wall plane 94.5 +/- 1.5 px/m, picture fronto-parallel: roof line level to 1 px in 400)

| item | house.json | present | measured | method | conf |
|---|---|---|---|---|---|
| roof edge trim, top | `roof.planes.rear_flat.z` | 8.87 | **8.84 +/- 0.15** | rows 291.5 / 1126 (door bottom) | H |
| fascia | `roof.eaves.rear_fascia.z` | 8.67..8.87 | 8.56..8.73, trim to 8.84 | same | H |
| shared stack top | `exterior.features.rear_chimney.z[1]` | 9.87 | 9.7 +/- 0.2 | same | M |
| study window frame | `openings.w_study` sill 0.68, height 1.40, width 1.00 (floor 6.02) | Z 6.70..8.10, 1.00 wide | **Z 6.52..8.15 (+/- 0.12), 1.53 wide**; stone sill 6.35..6.49; 2 casements + 2 fanlights, transom 7.67 | rows 512 / 357, columns 553 / 698 | H (width), M (sill) |
| conduit across the wall | - | 6.0 | 6.06 | row 553 | M |
| balcony door frame | `openings.d_balcony` (floor 3.04, h 1.90, w 1.50) | head about 5.36 | **head 5.34, frame 1.62 wide**, on the French-door axis | row 621, columns 553 / 706 | H |
| French doors | `openings.d_french` w 1.19, h 1.97 | - | frame 1.19 wide, leaf head 1.97, fanlight head **2.35** | rows 940 / 904 | H |
| side windows, heads / transoms | `w_dining_n_w/e` sill 0.37 h 1.83 | head 2.20 | **head 2.38**, transom 1.32, frames 0.60-0.67 wide | rows 900-903, 998-1004 | M |
| **brick junction -> flank corner** | `facades.rear_R` notes (render -0.50..3.40) | 3.90 | **4.22 +/- 0.08** | columns 415.7 / 814.3 at Z 1.3; 405 / 805 at Z 8.5 | H |
| flank corner -> east window axis | `w_dining_n_e.center.x` 2.54 | 0.86 | 0.875 | column 498.4 | H |
| flank corner -> French-door axis | `d_french.center.x` 1.225 | 2.175 | **2.342** | column 637.0 | H |
| flank corner -> west window axis | `w_dining_n_w.center.x` -0.09 | 3.49 | **3.767** | column 771.7 | H |
| window axes from the door axis | - | +/- 1.315 | **+1.467 / -1.425** (symmetric within 0.04) | same | H |
| west window frame -> junction | - | 0.10 | 0.15 | - | M |
| study window / balcony door axis | `w_study` 1.26, `d_balcony` 1.29 | 0.035 / 0.065 east of the door axis | **on the door axis +/- 0.03** | columns, roll 0.9 deg removed | H |

### 3.2 Faces K, F and the east wall

| item | house.json | present | measured | method | conf |
|---|---|---|---|---|---|
| **width of face K** (flank face -> east face) | `facades.kitchen_K.extent` | 1.13 | **1.20 +/- 0.06** | v11 t64, frontal; door part 2.04-2.09 as ruler: 266 px at 216-225 px/m | M |
| back-door frame | `openings.d_back` w 0.84 | - | frame 0.77-0.80 wide, **0.07 from the flank corner, 0.35 from the east corner**; fanlight head 2.72 | same | M |
| first-floor window on K | `openings.w_gbath` sill 0.72 (Z 4.14) | 4.14 | sill about 4.30, frame 0.76 wide | same, one frame | L |
| eaves on K | `roof.eaves.rear_K.gutterZ` | 6.65 | gutter directly over the window head: **6.1-6.4** | v13 t28, v11 f77-f81 with the window head from the line above | L |
| east wall face proud of the bay cheek | `facades.bay_cheek_e.at` 4.15 vs `east_E.at` 4.53 | 0.38 | **0.10 +/- 0.03** | v8 t78 (end cap of the insulation against the 0.28 void), v8 t39, t70 | H |
| flank wall build-up | `walls.w_flank_*` thickness | 0.30 | 0.35-0.40 (225 brick + 100 insulation + finishes); exterior reveals 0.15-0.20 at the WC slot, 0.12-0.17 at the dining windows | v11 t26, t176-t182 | M |
| alley width | `zones.side_alley`, `boundaries.alley_neighbour_wall` x 5.43 | 0.90 | **1.15 +/- 0.08** | v8 t81: gate 550 px, 15.5 boards at 75 cover, 1.10-1.22 by the brick courses beside it; v11 f107-f109 leaf + posts | H |
| street gate position | not in the spec | - | y 2.3 +/- 0.3 | v8 t78 | M |

### 3.3 Front

| item | house.json | present | measured | method | conf |
|---|---|---|---|---|---|
| east pilaster zone (light 4 -> bay corner) | `front_elevation.md` 3.2 | 0.295 | **0.47 +/- 0.04** (0.86-0.89 light widths) | v8 t25 projective fit | H |
| bay corner -> east wall face | see 3.2 | 0.38 | 0.10 | - | H |
| door frame : light opening | frame 1.24, light 0.54 (2.30) | 2.30 | 2.3-2.7 depending on the perspective term | v8 t25, v9 t15 | L - **not settled** |
| first-floor bay window frame | `w_green_bay` sill 0.70 h 1.85 (Z 4.12..5.97) | 4.12..5.97 | 3.98..6.00 | v9 t15, verticals parallel, 137-141 px/m from the door head / transom and the bay top lights | L |
| porch window frame (wall B) | `w_green_west` sill 0.78 h 1.80 (Z 4.20..6.00) | 4.20..6.00 | 4.20..6.14 | same, depth ratio 0.88 | L |
| main front gutter | `roof.eaves.front.gutterZ` | 6.50 | **6.4-6.6** | same; and 0.40 above the porch-window head in v8 t15 | M |
| bay gable pitch | `roof.planes.bay_gable_*.pitchDeg` | 43 | **49 +/- 3** | v9 t15: verge slopes 46.7 and 51 deg either side of a near-frontal view; v8 t15 43 / 63 deg (oblique) | M |
| bay gable apex | `roof.gable.ridgeZ` | 8.295 | **8.7 +/- 0.2** | v9 t15 verge intersection (8.67); v8 t15 from the window head (8.7-9.0); 6.50 + 1.925 x tan 49 = 8.71 | M |
| party stack top (I8) | not in the spec | - | 7.7 +/- 0.2 | v9 t15 | L |
| forecourt depth | `zones.forecourt` | 5.08 | not re-measured: 32 sett courses of 160 and 21 stretchers of 225 (phase 2) stand | - | - |

## 4. What the measurements mean for the spec

**The east side, one consistent reading** (all walls old brick + 0.10 insulation):

| line | present | proposed | why |
|---|---|---|---|
| flank face F | 3.40 | **3.45** | rear face 4.22 = party centre line (-0.765) to the flank; wall 0.35. This is `rear_elevation.md`'s own figure |
| east face E | 4.53 | **4.65** | face K 1.20 wide; wall 0.35 on the inner face 4.30 |
| bay east cheek | 4.15 | **4.55** | 0.10 behind E = flush with the old brick face |
| render / brick junction on R | -0.50 | **-0.77** | no exposed pier on our side |
| alley, neighbour's wall | 5.43 | **5.80** | E + 1.15 |

Knock-on: `bounds.maxX` 4.53 -> 4.65; `envelope.blocks.main` polygons (the notch at the bay becomes
[4.55, -0.12], [4.55, 0.95], [4.65, 0.95]); `rear_addition` polygons x 3.40 -> 3.45; `zones.side_alley`,
`forecourt_alley_mouth`, `side_passage`, kitchen steps, `side_gate` hinge (4.5 -> 4.65, 9.03),
`east_fence` south end, `plot` east edge; `roof` plane polygons that use 4.53 / 3.40 and the neighbour
blocks at 5.43. **No interior face moves**: the walls get thicker (flank 0.35, east 0.35, bay cheek 0.55 at
the ground floor). The living bay's lights then sit 0.70 from the corner where the picture says 0.47: the
lights are probably 0.57-0.58 wide rather than 0.54, or stand further east - the living / front agents must
say which (section 6, Q1).

**Rear openings.** Measured from the flank corner the axes are 0.875 / 2.342 / 3.767. With the flank at
3.45: east window **2.575**, French doors **1.11**, west window **-0.32**; the study window and balcony
doors sit on the French-door axis (1.11) and the balcony platform is centred on it. The west window frame
then ends 0.03 inside the room's west face, so either the dining room's west face is a little further west
than -0.65 or the flank is nearer 3.50; the interior footage (v2 f_0140, v1 f_0694) does show both side
windows tucked hard into the corners, which the present 0.25 piers do not.

## 5. Notes per unit

- **envelope**: I1 (base rail, void, returns, 0.10 step at the bay), I2, I3, I6, I7, I8, I9, I10; bay gable
  49 deg with the apex at 8.7 and the ridge running back to about y 4.2; study window 1.53 x 1.63 with a
  stone sill 1.75 x 0.14; rear side-window heads at 2.38; the rear fascia 8.56..8.73 under a dark trim to
  8.84; the east verge trim; `east_E` is no longer "unknown openings": it has none.
- **site**: I4, I5 (new boundary: street-end gate), alley 1.15 wide and concrete, neighbour's flank wall at
  E + 1.15 in yellow stock with a red-brick return to the street; I11; I12; I13.
- **shell**: flank and east walls 0.35 thick; bay cheek wall thicker; exterior reveals 0.12-0.20.
- **front**: I11; the east pilaster; the door set may be a 1490 unit (leaf 0.34 as wide as high in v9 t19):
  check against the vestibule tiles before changing 1.24.
- **side_passage**: gate, steps and paving shift with the flank / east faces; K is 1.20 wide with the door
  frame 0.07 from the internal corner; black plinth band and base rail (I1); waste pipe on its low kerb.
- **garden**: I12; rear openings as section 4; the render junction.
- **shed**: I13.
- **dining**: side windows at +/- 1.45 from the French-door axis, tucked into the corners; heads 2.38,
  transom 1.32; fanlight head 2.35.
- **study** (Rose Room): window 1.53 wide, frame Z 6.52..8.15 (interior board about 0.55 above the floor if
  the floor is 6.02), on the door axis.
- **blue_ensuite / balcony**: balcony doors and platform centred on the French-door axis; door frame 1.62
  wide, head 5.34.
- **green_bathroom**: the K window sill may be 0.15 higher than modelled (L).
- **living / green_bedroom**: bay cheek outer face moves east; cheek windows keep their Y (frame y
  0.18..0.70 measured outside).
- **eaves / loft_office** (Slate Room): gable tunnel under a 49-degree gable; rear eaves on K possibly 0.3
  lower than the symmetric 30-degree roof gives.

## 6. Open questions

1. **Absolute X layout of the front.** Relations are firm (pilaster zone 0.47, cheek 0.10 behind the east
   face, east wall at least 0.33 thick) but they cannot all hold with lights of 0.54 at 1.245..3.855 and a
   room face at 4.30: 0.15-0.25 m is missing east of the bay lights. A hard horizontal reference on the
   front is needed (shutter panels or sill board inside the bay, the vestibule tile count against the door
   set, or a tape across the bay).
2. **Flank at 3.45 or 3.50, and where the dining room's west face is** (section 4).
3. **Main ridge height and pitch** (9.14, 30 deg): not visible from any exterior frame except steeply from
   the alley; the K eaves hint at a steeper or lower rear slope east of the back addition.
4. **Garden length, shed position, main-block and outrigger lengths**: no exterior measurement better than
   phase 2 was obtained. v13 f212-f217 are plan-like and would give them from a ground homography once
   the east-fence posts are picked (bays of 1.83 + post).
5. **Second-floor level from outside**: the Lavender Room window looks straight at the neighbour's brick
   wall (v13 f22-f34); a course count to the horizon would give the camera height above the passage, but
   that wall's course height is not calibrated.
6. **Height of the alley gate screen and of the neighbour's flank wall**; ownership of the alley.
7. The neighbour's extension wall top: 2.7-2.95 (base hidden behind the planters).

## Verification

Verifier's re-measurement of the fourteen proposed changes (envelope-01 .. 14). Own stills, grids and tools:
`reference/work/r3_dims_envelope_v/` (private), `build/r3/dims_envelope_v/` (`crop.py`, `edges.py` sub-pixel
edge finder, `period.py` brick-course period). Different frames from the survey wherever the footage allowed:
rear face **v2 t248.5** (survey: t249.5), face K **v11 t62** (t64), bay corner **v8 t62, t68, t74, t84** (t70,
t78), bay front **v8 t28** (t25), gable **v9 t12 and v8 t124** (v9 t15), alley **v11 t82, t116** (v8 t81),
garden from above **v13 f_0215** (f_0217); interior cross-checks v2 t68 / f_0139 / f_0141 (dining corners),
v4 t443 (Rose Room north wall), v11 f_0001 (back door from inside).

**Is the model scaled right?** Vertically yes: on v2 t248.5 (camera level, both wall edges vertical within
3 px over 500) the door set fixes 94-95 px/m (frame 111.8 px = 1.19; frame below the transom 199.5 px = 2.10,
i.e. a 1190 x 2090 unit, aspect 1.78), the roof edge comes out at 8.73-8.89 (model 8.87) and the Rose Room
window head at 8.02-8.17 against 8.16 measured indoors. Horizontally the east side is short: render
junction to flank corner 4.19-4.27 (model 4.165), face K 1.16-1.24 (model 1.13), and the whole width from the
dining room's west face to the east wall face 5.3-5.5 (model 5.18). The proposed 3.45 / 4.65 are the least
moves that satisfy the exterior chains without touching a room face; the footage hints at a further 0.10
(see "Not settled" below).

| id | verdict | value to use | own measurement |
|---|---|---|---|
| envelope-01 | **adjust** | `bay_cheek_e.at` = `east_E.at` - 0.40 = **4.25** (with 4.65). Notch stays [cheek, -0.12], [cheek, **0.74**], [east, 0.74]. Cheek walls thicken outwards only (G 4.00..4.25, first floor 3.90..4.25) | The step is **not 0.10**. v8 t62 (pavement, east of the bay): the twin-head security light hangs on a white wall that faces the street, between the foreshortened cheek and the yellow face; that return is 53-55 px against light 4's frame 80 px (0.54) at 1.15-1.17 x the depth = **0.42-0.45**; against the light fitting itself (0.30 wide, 43 px) 0.38. v8 t84: same return 200 px against the fitting 117 px = 0.5 (close-up, upper bound). v8 t68 / t74: the bay cornice turns a re-entrant mitre and runs along this return to the yellow face; the cheek's sill band stops at the re-entrant corner 0.03-0.05 beyond the window frame; the return's foot covers two sett rows. What the survey measured in t78 (end cap against the void) is the insulation thickness at the end of the return. Present 0.38 holds (0.38-0.45). The cheek does move east, but with the east wall: pilaster zone light 4 -> corner 108 px against the frame 107 px in v8 t28 = 0.50-0.54 (survey 0.47; model 0.295); with 4.25 it becomes 0.395 |
| envelope-02 | **accept** | **4.65** (wall 0.35, inner face 4.30) | v11 t62: east corner col 682, flank internal corner 908-912 = 228 px; back-door frame 748..903 = 155 px taken as 0.79-0.84 wide (a width ruler, the survey used the height) -> K **1.16-1.24**; frame 0.34-0.36 from the east corner, 0.04-0.05 from the flank. Chain: party centre -0.765 + 4.22 + 1.20 = 4.655. Upper check: indoors (v11 f_0001) the frame stands at most 0.10 from the kitchen's east wall, so the wall is 0.25-0.35: 4.65 is the top of that range (frame on the inner face). Front chain (light 4 edge 3.86-3.88 + 0.47 + 0.40) gives 4.73-4.79, so 4.65 is not too far east |
| envelope-03 | **accept** | **3.45** (wall 0.35). Not 3.50: K would be 1.15 or the back-door frame would pass the kitchen's east face | v2 t248.5: flank corner col 462.1 (Z 6-8) / 463.5 (Z 1-3), render-brick junction 859.4-860.9 / 864.3 = 398-401 px at 94-95 px/m = **4.19-4.27**; old brick course on the adjoining wall 7.85 px = 83 mm at this scale (survey 84). Flank >= -0.765 + 4.19 = 3.43 |
| envelope-04 | **adjust** | Render **x -0.77..3.45** (accept). No exposed pier east of the junction (accept). Stack: brick shaft **0.26 wide, wholly west of the junction: x -1.17..-0.91**, grey sloping haunch on its east side reaching 0.15 east of the junction at roof level; **top Z 9.55** | Width as above. v2 t248.5 x7 crop: shaft cols 873..898 (junction 860), cap rows 250-255 -> 9.45-9.62 (present 9.87, survey 9.7). The dark strip cols 860-872 below the roof is the neighbour's brick face in the shade of the 0.10 insulation step, not a pier. The survey's "768-820 straddling 805" does not match this frame: the brick is on the far side of the junction, only the haunch is on ours |
| envelope-05 | **accept** | width **1.50**, sill **0.52**, height **1.60**; centre on the door axis = **1.225** (see 06) | Outside (t248.5): frame cols 610.0..755.1 = 145 px = 1.53; rows 385.7..540 = 154 px = 1.62-1.65; exactly as wide as the balcony door frame under it (607..757); glass alone spans 1.33, so 1.00 is impossible. Inside (v4 t443, wall plane scaled by the column radiator 396 px = 1.80, which gives the ceiling at 2.64): oak board **0.545 +/- 0.04**, transom 1.64, frame head **2.14**. Outside levels 6.39..8.02 at 95 px/m, 6.50..8.17 at 93.3 (+/- 0.12) |
| envelope-06 | **adjust** | Spacing accepted, position anchored on the room: `d_french` stays **1.225**; `w_dining_n_e` **2.665**; `w_dining_n_w` **-0.215**; both **0.65 wide** (0.52 now); `d_balcony` **1.225**; `w_study` **1.225**; balcony platform centred on 1.225 (0.075..2.375), wall posts at the axis +/- 1.02..1.07 | Outside (t248.5): flank 463.5; east frame 514.0..577.4; door frame 627.2..739.0; west frame (788.5)..850.0 (left edge behind the balcony post, taken from its 7 px stile); junction 864.3 -> axes 0.865 / 2.312 / 3.745 from the flank at 95 px/m (survey 0.875 / 2.342 / 3.767), window axes **1.447 / 1.433** from the door, frames 0.65-0.67, piers 0.52 each. Inside: v2 t68 (north-east corner: the dado rail on the strip right of the recess slopes, so that strip is the east wall and the recess architrave stands in the corner) and v2 f_0139 / f_0141 (north-west corner: the same) -> the screen is symmetric in the room; v4 t443: Rose Room mullion 1.92 +/- 0.08 from the west wall = axis 1.27 (an axis at 1.11 would read 1.76). With the door at 1.11 the west frame is flush with the wall face (no room for the architrave of f_0141) and the east frame 0.20 from its corner. With 1.225 +/- 1.44 and 0.65 frames both margins are 0.11. Cost: outside, the group stands 0.09 east of its measured place between the corners |
| envelope-07 | **accept** | head **2.37** (height 2.00), transom **1.32** | t248.5 rows: side-window frame tops 922-924, door fanlight frame top 924-926, transoms 1021-1023, door bottom 1147.5 -> 2.36-2.41 and 1.32-1.35. `dining.md` has the reveal soffit at 2.38 |
| envelope-08 | **accept** | 1.15 wide, east face .. +1.15 = **4.65..5.80**, concrete, open to the sky; neighbour's wall yellow stock, red-brick return at the street | v11 t82 (inside): the gate fills the alley, 148 px; foot to the top of the braced leaf 247 px; a 1.83-2.00 leaf gives **1.10-1.20**. v8 t62 (street): gate 140 px at 100-115 px/m (return-plane scale carried 1.3 m back) = 1.2-1.4. Model 0.90 is out |
| envelope-09 | **adjust** | gate at **y 2.0 +/- 0.3**; the rest as proposed | The survey counted its 1.0-1.3 from a "white return" at y 0.95; the yellow wall starts at 0.74 (item 11). v11 t116 (standing in the gateway, looking down): yellow corner 1.2-1.4 m ahead of the gate line (sandal 0.27 as ruler) -> 0.74 + 1.3. v11 t82: braced leaf under a fixed boarded panel, whole screen 340 px against the 148 px width = 2.6-2.7 high |
| envelope-10 | **accept** | pitch **49**, ridgeZ **8.70** (8.77 if the half-span becomes 1.975 with the cheek at 4.25), ridge back to y 4.24 | v9 t12: verge slopes 50.2 (west) and 57.3 (east), mean 53.7; the first-floor window as an in-plane ruler puts the horizontal foreshortening at 0.96-1.05, so 52-55: steeper than 43 for certain, and `eaves_loft.md` reads the tunnel linings 52 +/- 5 from inside. The present 43 / 8.295 was inferred, not measured (`front_elevation.md` 3.6). Apex height: no frontal frame shows it; two extrapolations in v8 t124 (cross-ratio up the bay axis 8.25 +/- 0.25; window homography 9.5) bracket 8.70 and settle nothing. main_front reaches 8.70 at y 4.24, below the ridge 9.14 |
| envelope-11 | **reject** (extent) / accept (no openings) | keep extent **[0.74, 9.03]**; `openings: []`, note "blank gable end, black verge trim" | v8 t68 / t74: the cheek is corner post + window + 0.03-0.05, then the re-entrant corner: 0.29 + 0.52 + 0.05 = 0.86 = y -0.12..0.74, the present value. The survey's own t70 ratios say the same (post 0.57 W + window W = 0.82-0.86); its third segment "wall 0.53 W" is the street-facing return of item 01 seen obliquely. Blank wall: v11 t82 |
| envelope-12 | **reject** | keep 6.65 until the roof is reconciled | The observation is right: v11 t40, cross-ratio up face K (door head 2.06, fanlight head 2.64, sill 4.14, head 5.82) puts the gutter underside at 6.48 in the wall plane, **6.1-6.3** after the 0.2 eaves projection. But `gutterZ` is not read for pitched eaves (`envelope.py` hangs the gutter on the plane's free edge), so the change is really `roof.planes.main_rear` (ridge about 0.4 further forward, or a 33-34 degree rear slope), which the loft interior (RECONCILE2 E4) fixes |
| envelope-13 | **adjust** | wall end **y 20.4** (accept); `west_fence` starts there and **stays closeboard_brown** | v13 f_0215: balcony platform (Z 3.0, 1.05 deep) = 195 px gives 186 px/m at the height of the coping (2.95); coping end 525 px from the threshold = 2.8-3.05 m -> y 20.2-20.4; v2 t251: the wall runs on past both trellis panels. Fence: v2 f_0193-f_0203 from the garden show brown closeboard on concrete posts; the pale lattice of v13 is seen from above on the far side |
| envelope-14 | **accept**, with 03 | frame **x 3.50..4.30**: centre **3.90**, width **0.80** | v11 t62: frame 155 px of K's 228 px = 0.80-0.84; 7-10 px (0.04-0.05) from the flank corner, 66 px (0.35) from the east corner. Needed as soon as the flank is 3.45: left at 3.40..4.24 the frame's first 0.05 lies behind the flank face. Kitchen: the return to the east wall becomes about 0 (v11 f_0001 shows at most 0.10); check the hinge side and the unit run |

**Knock-on, checked.** X at face K: 3.45 + 0.05 + 0.80 + 0.35 = 4.65. X on the rear face: -0.77 (junction)
/ -0.65 (room) / west frame -0.54..0.11 / pier 0.52 / door frame 0.63..1.82 / pier 0.52 / east frame
2.34..2.99 / room 3.10 / flank 3.45; junction to flank 4.22. X at the front: bay 0.90..4.25, return 0.40, east
face 4.65, alley to 5.80. Stacked walls: every `w_flank_*` (G, 1, 2) becomes 0.35 on the same inner face
(`w_flank_1_ensuite` 2.90..3.45), the east walls of all levels 0.35 on 4.30, the east cheek walls end at 4.25.
Polygons and lines that carry 3.40 / 4.53 / 4.15 / 5.43: `envelope.blocks`, `bounds.maxX`, facades `front_A`,
`kitchen_K`, `flank_F`, `rear_R`, roof planes `main_front`, `main_rear`, `rear_flat`, eaves `rear_K` / `flank`
(3.48 -> 3.53), the bay gable (east eave 4.55, ridge x 2.575 = the bay-window axis within 0.03), zones
`side_alley`, `forecourt_alley_mouth`, `side_passage`, `side_gate` hinge, `alley_neighbour_*`, `plot`,
`neighbours.east`. No level and no Y line changes, so riser counts are untouched.

**Not settled (say so to the reconciliation).**
1. The exterior wants about 0.10 more than 3.45 / 4.65. Rear face: flank -> door axis 2.31-2.34 with the
   door on the room's axis gives a flank at 3.54-3.57; front: 3.87 + 0.47 + 0.40 gives an east face at
   4.73-4.79. Both fit only if the kitchen and living room are about 0.15 wider than modelled (east inner face
   about 4.45; `living.md` first measured 3.60 +/- 0.15, RECONCILE2 lists the kitchen's 3.05 as open). An
   interior measurement across the kitchen or the living room decides it; nothing outside can.
2. Side passage at the K end: in v11 t62 the garden gate (about 0.85) plus face K (1.20) span about 2.05
   from the fence line to the flank corner, and the gate looks square to the passage; the spec has 1.5 and a
   diagonal gate. For the passage survey.
3. Main rear eaves 0.3-0.5 lower than the symmetric 30-degree roof gives (item 12).
4. Bay gable apex height (item 10) and the party line on the rear face (the stack is not centred on the
   junction, item 04).

# Phase 2 reconciliation: whole house into `spec/house.next.json`

Inputs: the 18 new room specs (`spec/rooms/{basement, landing1, yellow_room, stairs2, blue_bedroom,
blue_ensuite, balcony, green_bedroom, green_bathroom, landing2, purple_room, study, bathroom2,
loft_office, eaves, garden, shed, front}.md`), `spec/phase2/{ground_corrections, front_elevation,
rear_elevation}.md`, `spec/house.json` and `spec/RECONCILE.md` (phase 1). Two stills were re-read to
settle the side alley (`reference/work/p2_rear_ext/c_v2_342_gap.jpg`,
`reference/work/p2_front_ext/v2_t955.jpg`).

Outputs: `spec/house.next.json` (all levels, exterior, roof), `spec/validate_house_next.py`,
`spec/plan_next_{B,G,1,2,site,section}.png`, `spec/layout2.md`, this file, and a "Reconciled
dimensions" section appended to each of the 18 new room specs. `spec/house.json` and the eight
ground-floor room specs were not touched; the ground-floor corrections live only in `house.next.json`.

`python spec/validate_house_next.py` passes: 28 rooms on 4 levels, 108 walls, 50 openings, 43 features,
6 flights, every room reachable from the vestibule. `house.next.json` was written by
`reference/work/p2_reconcile/gen_main.py` (private scratch, git-ignored) from `house.json` plus the
patches below, and then patched in place by `apply_verify.py` in the same folder for the verification
round (section 5): **the generator is now stale — edit the JSON directly**. The tables in section 1 show
the values after the verification round.

Where a room spec and `house.next.json` differ, **`house.next.json` and the room's "Reconciled
dimensions" section win**.

## 1. Result

### 1.1 Levels (world Z, ground-floor finished floor = 0)

| level | floor | Z | how |
|---|---|---|---|
| B | basement | **-2.31** | 11 risers x 0.21 down from the hall |
| G | all ground-floor rooms | 0.00 | - |
| 1 | quarter landing | **2.85** | 15 x 0.19 |
| 1 | rear: corridor, yellow room, blue bedroom, en-suite | **3.04** | +1 riser |
| 1 | balcony deck | 3.00 | 0.04 below the bedroom |
| 1 | front: landing, green bedroom, green bathroom | **3.42** | +2 risers ("two steps up") |
| 2 | stair head, hallway, purple room, bathroom, study | **6.02** | 13 x 0.20 from the front landing |
| 2 | platform | **6.22** | +1 riser |
| 2 | loft office, eaves storage | **6.49** | +0.27 at the loft door ("a massive step") |

### 1.2 Rooms (inside faces; rectangles unless a polygon is given)

| room | x | y | size | floor | ceiling (world) |
|---|---|---|---|---|---|
| basement | 1.25..4.25 | 5.19..8.73 | 3.00 x 3.54 | -2.31 | -0.31 |
| basement_stair (shaft) | 0.265..0.93 | 5.19..7.60 | 0.665 x 2.41 | steps | raked, 2.10 at the door |
| vestibule | -0.65..0.65 (front recess to 0.90) | 0..1.73 | 1.30 x 1.73 | 0 | 2.85, haunches in the front recess |
| hallway | polygon, see 2.1 | 1.83..12.23 | 1.30 / 0.80 / 1.10 wide | 0 | 2.95; 2.84 north of y 8.13; lobby soffit 2.60 |
| stairs (well) | 0.15..0.99, diagonal at the foot | 5.05..7.58 | 0.84 x 2.53 | 0 | soffit 3.17 then raking |
| living | 0.80..4.30, NW chamfer | 0.99..5.19 (+ bay 0..0.99) | 3.50 x 4.20 | 0 | 2.95 |
| kitchen | 1.25..4.30 | 5.31..8.73 (+ nook to 9.25) | 3.05 x 3.42 | 0 | 2.95 |
| wc | 0.60..3.10 | 9.36..10.14 | 2.50 x 0.78 | 0 | 2.40 |
| utility | 0.60..3.10 | 10.26..12.23 | 2.50 x 1.97 | 0 | 2.40 |
| dining | -0.65..3.10 | 12.36..16.86 | 3.75 x 4.50 | 0 | 2.80 |
| green_bedroom | -0.65..4.30 (+ bay 1.16..3.90) | 0.99..4.83 (bay 0.14..0.99) | 4.95 x 3.84 | 3.42 | 6.27 (2.85) |
| green_bathroom | 1.25..4.30 | 4.95..8.73 | 3.05 x 3.78 | 3.42 | 6.17 (2.75) |
| landing1_front | -0.65..0.99 / strip -0.65..0.15 | 4.95..6.06 / 6.06..8.13 | 1.64 x 1.11 + 0.80 x 2.07 | 3.42 | 5.77 (2.35) |
| stairs2 (well) | 0.15..0.99 | 6.06..8.13 (winders to 8.73) | 0.84 x 2.07 | 3.42 → 6.02 | 8.62 north of y 6.23; 5.77 for 6.06..6.23 |
| landing1_ql | 0.15..0.99 | 8.13..8.73 | 0.84 x 0.60 | 2.85 | vault, about 5.35 |
| landing1_rear | -0.65..0.15 / ..0.25 / bay ..0.40 | 8.13..8.73 / ..11.50 / 11.50..12.39 | corridor 0.90 wide | 3.04 | 5.49 (2.45) |
| yellow_room | 0.35..3.10 | 9.03..11.05 | 2.75 x 2.02 | 3.04 | 5.49 (2.45) |
| blue_ensuite | 0.50..2.90 | 11.15..12.85 | 2.40 x 1.70 | 3.04 | 5.54 (2.50) |
| blue_bedroom | -0.65..3.10 (recess -0.65..0.40) | 12.95..16.86 (recess from 12.52) | 3.75 x 3.91 | 3.04 | 5.64 (2.60) |
| balcony | 0.00..2.30 | 17.36..18.41 | 2.30 x 1.05 | 3.00 | open |
| landing2_platform | -0.65..0.15 | 6.23..8.13 | 0.80 x 1.90 | 6.22 | 8.62 |
| landing2_head | -0.65..0.15 / ..0.22 / ..0.30 | 8.13..8.73 / ..11.50 / ..12.94 | 0.87 / 0.95 wide | 6.02 | 8.62 |
| loft_office | -0.65..4.30; cabinet block 0.31..1.25, y 5.38..6.13 | 2.54..6.59 (door wall 6.13) | 4.95 x 4.05 | 6.49 | sloped, flat strip 8.61 |
| eaves_front | -0.65..4.30 (+ gable tunnel 1.43..3.63) | 0.95..2.44 (tunnel from 0.14) | 4.95 x 1.49 | 6.49 | under the roof |
| eaves_rear | 1.25..4.30 | 6.69..8.73 | 3.05 x 2.04 | 6.49 (6.37 east of x 2.35) | under the roof |
| purple_room | 0.32..3.10 | 9.29..11.20 | 2.78 x 1.91 | 6.02 | 8.62 |
| bathroom2 | 0.40..3.10 | 11.50..13.70 | 2.70 x 2.20 | 6.02 | 8.49 |
| study | neck -0.65..0.30, main -0.65..3.10 | 13.04..14.15, 14.15..16.86 | 3.75 x 2.71 | 6.02 | 8.62 |

### 1.3 Stairs

| flight | from → to | risers x rise | going | notes |
|---|---|---|---|---|
| stair_basement | hallway 0 → basement -2.31 | 11 x 0.21 | 0.20 | south from the basement door (R1 at y 7.60), R9 at 6.00, two winders east, R11 at x 1.25 |
| stair_main | stairs 0 → quarter landing 2.85 | 15 x 0.19 | 0.23 | three kite winders at the foot against the 45-degree wall; R4..R15 at y 5.60..8.13 |
| steps_ql_rear | 2.85 → 3.04 | 1 x 0.19 | - | west off the quarter landing |
| steps_rear_front | 3.04 → 3.42 | 2 x 0.19 | 0.25 | risers at y 8.13 and 7.88 |
| stair_second | front landing 3.42 → 6.02 | 13 x 0.20 | 0.23 | R1 at y 6.06, R10 at 8.13, three winders west over the quarter landing |
| step_head_platform | 6.02 → 6.22 | 1 x 0.20 | - | at the top newel, y 8.13 |
| loft door `d_loft` | 6.22 → 6.49 | step 0.27 | - | white riser board under the threshold |

Headroom (validator, 0.25 structure): basement stair under the main flight 2.2-2.6; main flight under
the second flight 2.2-2.3.

### 1.4 Envelope and roof

- Outer faces: west party wall x -0.88 (centre -0.765, 0.23); east wall of the main house x 4.53
  (inner 4.30) — **external, facing a side alley**; bay front / street doors y -0.12; main front wall
  y 0.74; bay cheeks x 0.90 (first floor only) and 4.15; rear wall of the main house y 9.03; back
  addition flank x **3.40** (inner 3.10, wall 0.30); rear wall y **17.36** (inner 16.86, wall 0.50).
  `bounds` = x -0.88..4.53, y -0.12..17.36.
- Main block z: G 0..3.42, first 3.42..6.49, loft 6.49..ridge. Back addition z: G 0..3.04, first
  3.04..6.02, second 6.02..8.87 (three full storeys, flat roof).
- Main roof: symmetric 30-degree duo-pitch, ridge parallel to the street at y 5.00, Z 9.14; outer surface
  Z 6.68 over the front wall face, front gutter about Z 6.50; rear slope survives east of x 1.35 and
  abuts the back addition's second-floor wall, with eaves over the kitchen-door wall for x 3.40..4.53.
- Stair dormer: flat roof Z 8.87 over x -0.88..1.35, y 5.47..8.73 with the fixed skylight (x -0.20..0.70,
  y 6.38..7.28, 0.15 north of the loft-door wall); it is continuous with the back addition's flat roof
  (Z 8.87, y 8.73..17.46).
- Bay gable: ridge along Y at x 2.525, Z 7.70, pitch about 43 degrees, dies into the main slope at y 2.51.
- Porch lean-to: x -0.86..0.93, eaves Z 2.85 at y -0.58, abutment Z 3.90 at y 0.74.
- Velux in the rear slope x 2.76..3.54, plan y 5.48..6.45. Chimney: one shared stack on the party line
  at the NW rear corner; none on the main roof.

## 2. Decisions

Principle as phase 1: a room keeps what its analyst measured from fixed modules or direct counts;
chains nobody measured directly give way; what cannot be reconciled goes into zones nobody sees.
Tags: **[=]** all sources agree, **[c]** compromise within the stated tolerances, **[!]** somebody's
tolerance is exceeded (also listed in section 4).

### 2.1 Ground floor (apply `ground_corrections.md`)

Applied as its patch list, ids kept: hallway / stairs polygons with the 45-degree wall
(`hall_stair_diag`, (0.65, 5.05)→(0.99, 5.39)); living NW chamfer (`living_nw_chamfer`) and north wall
at y 5.19; `w_cross` 0.12 thick; `w_nib`, `hall_nib`, `cross_wall_zone` removed, solid triangle kept as
`stair_foot_poche`; `d_living` opens 135 degrees; bay-nib chamfers 0.15 to 2.20 with stops to 2.40;
vestibule haunches; `d_street` swings outside; `d_understairs` renamed **`d_basement`**; dining north
wall = three recesses 0.38 deep (`dining_n_recess_*`), both side windows z 0.37..2.20; utility window
obscure, top-hung. Additional decisions:

- **G1 [c] Side-window transoms.** Both dining side windows get a transom at 1.40 (frontal exterior
  still, `rear_elevation.md`); the west upper light is the opener (`ground_corrections` D3 had 1.55 and
  "one tall pane" for the east one from oblique interior views).
- **G2 [c] Hall ceiling north of y 8.13 is 2.84, not 2.95** (`hallway.ceilingZones`). The first-floor rear
  corridor floor is 3.04 (16 risers), which cannot sit on a 2.95 ceiling. 2.84 leaves a 0.20 floor and
  0.09 of wall over the arch crown (2.75). The lobby bulkhead on x 0.15 becomes 0.24 deep.
- **G3 Winders.** Bottom three risers are kite winders from the newel (`landing1.md` 11): R1 ellipse
  0.53 x 0.28, R2 to the diagonal, R3 to the internal corner. The riser chain R4..R15 is unchanged.
- **G4 Basement stair.** Shaft x 0.265..0.93, y 5.19..7.60 under the main flight
  (`basement_stair_void`); see B1.
- **G5 [c] Flank wall and back door: see E2.** `d_back` moves 0.075 east and narrows to 0.76 clear.
- **G6 East wall is external** (`w_party_e_*` keep their ids, kind `external`): see E3.

### 2.2 Levels

- **L1 [=] Rear first floor 3.04.** Stair count (15 + 1 risers of 0.19), the blue-bedroom estimate (3.05
  from the dining ceiling and the balcony) and the rear still (platform 2.9-3.1) agree.
- **L2 [!] Front first floor 3.42**, not the 3.22 of `green_bedroom.md` / `front_elevation.md`. Those
  assumed the stair lands on the rear level; in fact it lands one riser below it, and the two-riser
  difference between rear and front is certain. This leaves a 0.47 floor zone over the 2.95 hall / living
  / kitchen ceilings (deep, but the front rooms have recessed downlights throughout). First-floor front
  window sills are therefore at Z 4.12 (bay) / 4.20 (west window), heads 5.97 / 6.00.
- **L3 [!] Second floor 6.02, loft 6.49; green bedroom ceiling 2.85 and green bathroom ceiling 2.75.**
  The front chain wants the second floor high (green ceiling 2.95 + floor ≥ 0.2 → loft ≥ 6.57) and the
  rear wants it low (rear still: second-floor sill 6.30, wall top 8.55; rear ceilings 5.49-5.64). 13 risers
  (first_landing's count; second_rear counted 14) with ceilings shaved by 0.10 is the one combination
  where every floor zone is at least 0.20: bedroom 6.27 → loft 6.49 (0.22); bathroom 6.17 → rear eaves
  floor 6.37 (0.20). The green-bathroom analyst had already found that the north-wall view implies 2.75.
- **L4 Loft 6.49** = platform 6.22 + 0.27 (`landing2.md`); `loft_office.md` had 6.45 from the green
  ceiling. All its world Z move +0.04.
- **L5 Ceilings elsewhere as the room specs**: landings 2.35 / 2.45, yellow 2.45, blue 2.60, en-suite
  2.50, second floor 2.60 (bathroom 2.47), basement 2.00.

### 2.3 Stairs and the Y chain along the hall

- **S1 [c] The stairwell north wall is y 8.73 on every floor** (the old rear wall of the main house,
  8.73..9.03): the quarter landing is 0.84 x 0.60, not 0.84 square (`landing1.md` had its north wall at
  8.97). Evidence: the ground-floor lobby wall below is at 8.73 (kitchen door parks on it); `landing2.md`
  measured the stair head above at 0.40-0.61 in three stills; `landing1.md`'s Y is +/-0.20. The winders
  of the second flight fit in 0.84 x 0.60. The corridor chamfer moves to (0.35, 8.73)-(0.25, 8.83).
  The main flight is **not** shifted north (the alternative reading in `landing1.md` doubt 1): the top
  riser at 8.13 is tied to the overhead cupboard and lobby soffit seen on the ground floor.
- **S2 [!] Second-floor platform is 1.90 long, loft door wall y 6.13..6.23** (`loft_office.md`), not
  1.25 long with the wall at 6.78..6.88 (`landing2.md`). Three things fit together only this way: the
  second flight's well starts at y 6.06 (`stairs2.md`, trimmer apron over the first riser); the loft's
  "cabinet block" stands over the first-floor front landing with its back on the door-wall line (x 0.31..1.25,
  y 5.38..6.13 — corrected in section 5, T1: it does not reach into the well); and the loft's 30-degree
  ceilings centre the ridge at y 5.00 between the front and rear walls of the main body. `landing2.md` gave
  0.9-1.4 from perspective and 13-14 spindles.
- **S3 Chimney breasts do not stack and are not forced to.** Dining: breast and fireplace on the east
  flank wall (phase 1, verified). Blue bedroom: 0.10 projection on the west party wall carrying the TV and
  radiator (`blue_breast_w`, first floor only). Outside, the only stack is on the party line at the NW rear
  corner (`rear_chimney`), and no flue shows on the flank. Both internal breasts are modelled as local
  features with no flue above them.
- **S4 Loft door is a 610 leaf** (aspect ratio 3.17 measured from the platform, frame fills the 0.80
  platform width); `loft_office.md` assumed 762. `d_bath2` is 762 (the bathroom analyst measured it).

### 2.4 Rear half of the first and second floors (the over-constrained chains)

- **P1 [c] First floor, x 0.35..3.10.** Measured: yellow room 2.08 + en-suite 1.75 + blue bedroom 4.10
  (+ two 0.10 partitions) = 8.13 against 7.83 available between the old rear wall (9.03) and the rear wall
  (16.86). The 0.30 excess is shared within each tolerance: yellow **2.02** (9.03..11.05), en-suite
  **1.70** (11.15..12.85, the 1.70 bath wall to wall), blue main room **3.91** (12.95..16.86). The en-suite
  window ends up at y 11.28..11.68, nearer the rear still's "about 11.8".
- **P2 [c] Blue bedroom door wall at y 12.39..12.52**, 0.16 north of the dining south wall below, so the
  entrance recess stays 0.43 deep (measured 0.33-0.46). The arch bay is 0.89 deep. Bay and recess share
  one east wall at x 0.40..0.50 (en-suite west face 0.50); the door is centred at x -0.10 (clear
  -0.481..0.281), between the two analysts' -0.164 and -0.06.
- **P3 [c] One arch wall line on both upper floors: y 11.20..11.50** (first floor read 11.10..11.45,
  second 11.30..11.57). On the second floor it is also the purple room's north wall and the bathroom's
  south wall.
- **P4 [!] Second floor, bathroom and study.** `bathroom2.md` measured 2.20 north-south, `study.md` a
  main room 2.56 deep; together they are 0.50 short of the 5.36 between the arch wall and the rear wall,
  and the bathroom door (seen by both analysts 0.07-0.13 north of the arch wall) pins the bathroom's south
  end. ~~The gap is split: bathroom 2.45 (11.50..13.95), study main room 2.81 (14.05..16.86), study
  neck 1.01.~~ **Revised in section 5 (INV-01):** the bathroom's fittings form a rigid chain along the window
  wall, so it keeps **2.20** (11.50..13.70); the study takes 0.15 (neck **1.11**, main room **2.71**,
  14.15..16.86, both inside its analyst's tolerances); the remaining 0.35 is an unseen zone in the wall between
  them (`w_bath2_study`, 13.70..14.15, solid).
- **P5 [c] Purple room y 9.29..11.20** (measured 1.91, moved 0.10 south with the arch wall). The 0.56
  between it and the stair well (y 8.73..9.29) is unseen and modelled solid (`w_addition_s_2`).
- **P6 Bathroom2 width 2.70** (0.40..3.10): the hall partition is at x 0.30..0.40 (`landing2.md`);
  `bathroom2.md` had 2.80 by assuming no partition thickness.
- **P7 [c] Front landing / green rooms partition y 4.83..4.95** (`landing1.md`; `green_bedroom.md` had
  4.73..4.87 by stacking on the old ground-floor line, which has since moved to 5.19). It is a stud
  partition with a pocket door and does not need to stack. Green bedroom 3.84 deep, green bathroom 3.78.
- **P8 First-floor bay cheek windows y 0.19..0.67** (`front_elevation.md`): the interior spec centred
  them on the inside cheek (0.32..0.80), which would put them behind the main wall face (y 0.74).

### 2.5 Basement

- **B1 [c] South wall at y 5.19** (under the living / kitchen cross wall) instead of 5.10, by taking the
  going as 0.20 instead of 0.21 (stated +/-0.015). R9 at y 6.00, opening y 5.19..6.00. This also keeps
  the shaft clear of the hall floor in front of the bullnose step.
- **B2** The room polygon is the full rectangle; the SE block is the feature `basement_breast_base`
  (x 3.90..4.25, y 5.19..6.60). Nothing in the kitchen stands over it.

### 2.6 Envelope and exterior

- **E1 [=] Rear wall outer face y 17.36** (0.50 wall): `ground_corrections` D2 and `rear_elevation` agree.
  `balcony.md` / `blue_bedroom.md` values on the old 17.16 face move +0.20.
- **E2 [!] Flank outer face x 3.40 (0.30 wall), `d_back` clear x 3.42..4.18.** Outside, the back-door
  frame's west edge sits on the flank corner and the kitchen-door wall is 1.17 wide; inside, the kitchen
  units put the frame at x 3.25..4.20 and the east wall face at 4.30. `rear_elevation.md` (flank 3.45,
  east face 4.62) and the kitchen cannot both be right: with the east outer face kept at **4.53** (0.23
  wall, the kitchen-door wall is then 1.13 wide) and the flank at 3.40, the door moves 0.075 east and its
  frame is 0.86 (the exterior still gives 0.80-0.85). Garden x values keyed to the flank move -0.05.
  The utility window reveal can then be at most about 0.20 (measured "about 0.25").
- **E3 The house is not mid-terrace: there is a side alley on the east.** `garden.md` D3 and
  `front.md` disagreed. The crop over the side gate shows open sky between our rendered east wall (with a
  condenser and a flue on it) and the neighbour's brick wall, and a gabled house across the street
  beyond; the owner calls the gate the "side entrance" that "goes to the front". So the east wall of the
  main house is external (`east_E` facade, no known openings) and `exterior.zones.side_alley`
  (x 4.53..5.43, y 0.74..9.03) runs to the forecourt, where the paving and bins were already seen
  running "about 0.5 m past" the bay. Its width, surface and street-end closure are not established.
- **E4 [c] Roof = the loft's interior geometry** (`loft_office.md`): 30 degrees, ridge y 5.00, eaves at
  loft-floor level. `front_elevation.md`'s inferred eaves at 5.95 / ridge 9.0 / 42 degrees are superseded;
  with the front floor at 3.42 the first-floor window heads (5.97) clear the gutter (6.50) by 0.5.
  `rear_elevation.md`'s eaves at 6.05 on the kitchen-door wall becomes about 6.65.
- **E5 Back addition roof Z 8.87** (second-floor ceiling 8.62 + 0.25), 0.3 above the rear still's 8.55
  (stated +/-0.25).
- **E6 Balcony**: `balcony.md` geometry on the new wall face; deck top 3.00 is 0.04 below the bedroom
  floor (the two blue specs had 0.05 and 0.12). It is a bolt-on platform beyond the flush three-storey
  rear wall: there is no ground-floor roof under it. Wall posts at x **0.27** / 2.20 stand on the rendered
  piers between the French-door reveal (0.50..1.95) and the side-window frames (outer edges 0.22 and
  2.25); `balcony.md` had the west post at 0.21, which would overlap the window frame.
- **E7 Study window 1.50 wide centred x 1.23** (rear still: 1.55 over the frame, centre 1.20; `study.md`
  had 1.00). Heights from the interior (sill 0.68, head 2.08).

## 3. Schema additions (superset of `house.json`)

- `levels`: `[{id: B|G|1|2, name, datumZ, floors}]`; every room, wall, opening, feature and flight has
  `level`.
- rooms: `kind` (`room | stairwell | void | exterior`), world `floorZ` / `ceilingZ`, optional
  `ceilingZones` and `ceiling: {type: planes | under_roof}` (plane z = c0 + cx·x + cy·y).
- walls: `baseZ` (+ `height`), pseudo-room `void`, `roomsBelow`, `aboveRoof`, kind `retaining`.
- openings: `floorZ`, `step`, `transomBar`, `sashes`, `outsideZone`, type `hatch`.
- features: `chamfer` (`face`, `z`, `rooms`), `ceiling_haunch`, `floor_void`, `floor_step`, `balcony`
  (deck, railing, supports), `roof_opening`, `roof_window`, `roof_void`; `living_bay.chamfers` and
  `green_bay.chamfers` (`corner`, `width` of the 45-degree face, `z`, `stop`; world Z); `offsetFromWall`
  (`wall`, `distance`) on a feature that must follow a wall.
- `stairs` is a **list** of flights (`kind: flight | steps`, `fromRoom`, `toRoom`, `fromZ`, `toZ`,
  `through`, `viaOpenings`, `above`, straight-riser arithmetic, `riserLines`).
- `exterior`: `plot`, `zones`, `steps`, `boundaries`, `features`, `buildings` (shed with its own rooms,
  walls, openings, roof), `envelope.blocks[].levels[]`, `facades[]`, `neighbours`.
- `roof`: `planes`, `ridge`, `eaves`, `gable`, `chimneys`, `structure`.

Consumers of `house.json` need two changes to read it: `stairs` is a list (the old block is
`stairs[0]`, id `stair_main`, with its old keys intact), and rooms / walls / openings must be filtered
by `level`.

## 4. Open questions for the owner (tape-measure list)

1. **Kitchen / east wall / flank wall (E2).** One of: kitchen width wall to wall (3.05?), living-room
   width (3.50?), flank wall thickness at the utility window, width of the wall the back door is in
   (outside, flank corner to the east corner). The likeliest truth is that the kitchen and the main
   house's east wall sit 0.1-0.2 further east than modelled.
2. **Side alley (E3).** Its width, what closes it at the street end (door, gate, nothing), its paving,
   and whether the house's east wall has any window. The front spec recorded none of this.
3. **Storey heights (L2, L3).** Riser height of the main stair (0.19?) and of the upper stair (0.20?),
   number of risers of the upper stair (13 or 14), and the ceiling heights of the green bedroom (2.85 or
   2.95?) and the ground-floor rear corridor (2.84?).
4. **Second-floor platform length (S2)**: loft door to the single step — 1.9 m or 1.25 m?
5. **Quarter landing depth (S1)**: 0.60 or 0.84?
6. **Rear first-floor chain (P1, P2)**: yellow room length, en-suite length, blue bedroom length, depth of
   the blue bedroom's entrance recess.
7. **Second-floor bathroom and study depths (P4)**: 2.2 + 2.56 measured, 2.20 + 2.71 modelled with a 0.45
   wall between them; is there really a thick wall or cupboard between the bathroom and the study?
8. **Basement level** (-2.31, +/-0.12) and whether its south wall is under the living / kitchen wall (B1).
9. **Dining fireplace on the flank wall vs the "breast" on the west wall of the blue bedroom (S3)**:
   which is a real flue? Is there a chimney anywhere on the main roof?
10. **Roof**: back addition flat or low mono-pitch; stair-dormer extent and cladding; bay-gable pitch and
    eaves level (6.2 modelled, lower than the main gutter at 6.5); whether the main eaves really sit at
    loft-floor level.
11. Carried from the analysts and unchanged: 45-degree face lengths (hall 0.48-0.55, living 0.58), vestibule
    haunch angle, switch gang orders, dining head member, upper flank window positions seen from outside,
    shed depth (+/-0.5), garden length north of the deck (+/-0.4), forecourt depth (+/-0.3), fence
    convergence, colour estimates (HLG footage: tone-map before sampling, see `blue_bedroom.md`).

## 5. Verification round

Three independent checkers (topology, dimensions, inventory) compared the reconciled spec with the frames
and raised 13 issues. Each was re-checked against the cited frames (stills in
`reference/work/p2_verify_*/` and `reference/work/p2_reconcile/`), then applied to `house.next.json` by
`reference/work/p2_reconcile/apply_verify.py` and to the room specs ("Reconciled dimensions" sections, plus
the body text where the body itself was wrong). `python spec/validate_house_next.py` passes afterwards
(28 rooms, 108 walls, 50 openings, 43 features, 6 flights) and the previews were redrawn.

| id | decision | what changed, and why |
|---|---|---|
| **T1** loft block in the stair well | **accept** | v4 t360 / t362 / t378: left of the loft door the far wall is one flat plane to the corner with the well's east wall, and the platform handrail dies into it; `landing2.md`'s own sketch has a "(bulkhead)" on that line. `loft_block` → x 0.31..1.25, **y 5.38..6.13**; new wall **`w_well_s_2`** (x 0.15..0.99, y 6.13..6.23, Z 5.77..8.62) = the well's south face, coplanar with `w_loft_door`; `stairwell_void_2` → **y 6.23..8.73**; `stairs2` gets a ceiling zone Z 5.77 for y 6.06..6.23 (R1 starts under the landing ceiling, headroom 2.15). `loft_office` polygon unchanged. Docs: `loft_office.md`, `stairs2.md`, `landing2.md`, `layout2.md`. |
| **T2** skylight too far north | **accept, own size** | Same stills; and `landing2.md` section 3 already said "south edge about 0.10 from the loft door wall" — the first reconcile moved the wall (S2) but not the skylight. `skylight` → **x -0.20..0.70, y 6.38..7.28** (0.90 square: the checker's width reading was 0.99, the analyst's 0.85), with `offsetFromWall: {w_loft_door, 0.15}` so it follows the wall if S2 is revised. |
| **V1** green bay corners square | **accept, own width** | v4 f_0079 / f_0083 / t92 and `p2_green/v4_f1.jpg` show the chamfer with its curved stop under the cornice on both nibs. New level-1 feature **`green_bay`** with `chamfers` at (1.16, 0.99) and (3.90, 0.99), world Z **3.42..5.72**, stop to **5.82**. Two values differ from the proposed fix: the face is **0.12** wide, not 0.06 (measured against the 86 mm bedside switch plate and the 0.17 skirting in t92 / t86: 0.10–0.15), and it starts **at the floor**, not above the skirting (t86: the skirting returns round the chamfer in three faces). `green_bedroom.md` 3.1 / 3.2 corrected. |
| **V2** balcony bar pitch | **accept** | v3 t288 / t298: 5 bars on the west return; t272: 6 between front posts. `railing.barCentres` **0.165**, `barsPerSide` 5, `barsPerFrontBay` 6. `balcony.md`, `rear_elevation.md` section 4. |
| **INV-01** bathroom2 sauna / window gap | **accept, own values** | v5 f_0081, f_0123, f_0125: the sauna front is level with the window's north jamb. The chain along the window wall is rigid, but the "0.09 gap" the checker added behind the sauna is the gap between the sauna and the **window (east) wall** (`bathroom2.md` 2.3, v5 f_0104–f_0106), so the chain is 0.35 + 0.31 + 0.64 + 0.02 + 0.88 = the measured **2.20**, not 2.29. `bathroom2` → **y 11.50..13.70**, no y transform at all (sauna 12.82..13.70). Neighbour: `study` south face → **14.15** (neck 1.11, main 2.71 — inside the study analyst's 1.1–1.4 and 2.56 ± 0.15, which the first reconcile's 1.01 / 2.81 were not); `w_bath2_study` becomes a 0.45 solid zone (13.70..14.15). P4 rewritten; `study.md` transform is now -0.15. |
| **INV-02** blue bedroom wardrobe overlaps nightstand | **accept** | v3 f_0203–f_0223: wardrobe, cherub-lamp nightstand, bed stand side by side. The whole east-wall run moves +0.19: wardrobe 13.01..14.21, south nightstand 14.21..14.63, bed 14.63..16.09, north nightstand 16.11..16.53; mirror centre 15.36; sockets X8 at 14.50 / 16.17. `blue_bedroom.md` only (furniture is not in the JSON). |
| **INV-03** landing plates swapped | **accept** | v4 f_0266: the flat wide-rocker plate is directly beside the bathroom-door architrave with the 2-gang to its west; f_0270 the 2-gang beside the green door. `green_bathroom.md` section 8 now agrees with `landing1.md` 8.2: 1-gang (0.84, 4.95, 1.27), 2-gang (0.70, 4.95, 1.27), right rocker = landing, left = second-floor hall. |
| **INV-04** basement switch on the wrong wall | **accept** | v6 f_0117 / f_0119: the switch is on the wall beyond the east (hinge) jamb, left of the descending treads. `ground_corrections.md` section 1 corrected to the east wall, **(0.93, 7.42)**, 1.20 above the hall floor (x 0.93 is the reconciled shaft face; `basement.md` 8 had 0.98 on the old face — note added). Switches L-S, L-A, L-B. |
| **INV-05** sauna heater control unit | **accept** | v5 f_0055: brushed-steel box under the black heater body with a white fascia, red display and buttons. `bathroom2.md` 5.2: body Z 0.32..0.75, control housing 0.20..0.32 (0.40 x 0.12 x 0.25), dark display window (emissive while the sauna light is on), 4–5 buttons, blank label panel, no text. |
| **INV-06** "teddy lamp" in the brief | **accept, not applied here** | v2 f_0655–f_0659: the owner's hand is on the dining TV; no such lamp exists (`ground_corrections.md` H13 / D8 already make the TV the on / off trigger). `spec/BRIEF.md` line 197 still says "the teddy lamp turns on and off": that file is outside this task's write set — **the orchestrator should change it to "the dining-room TV turns on and off"**. `blender/INTERACT.md` does not mention it. |
| **INV-07** crops with human figures | **accept** | `landing2` W2 (papyrus with figurative panels, v4 t368): **no crop**, generic papyrus texture with abstract pattern bands only. `landing1` P4 (v3 f_0039, small seated angler): crop allowed only with the **figure and rod painted out (mandatory)**. Both room specs changed in place. |

No two checkers conflicted. Side effects of this round:

- **Validator** (`validate_house_next.py`, section 12): a solid feature (boxing, pier, breast, poche) may not
  stand in a `floor_void` of its level, and a feature with `offsetFromWall` must be at that distance from the
  wall face. The first check fails on the pre-round file for `loft_block` (T1) and also found that the
  ground-level `basement_stair_void` ran 0.14 under the hall's 45-degree wall (`stair_foot_poche`); its SE
  corner is now clipped along the diagonal, (0.79, 5.19)-(0.93, 5.33).
- **S2 is still open** (platform 1.90 long, loft-door wall at y 6.13..6.23): T1 and T2 are both keyed to that
  wall, so if the owner's tape says 1.25, the wall, `w_well_s_2`, the skylight and the loft's Y anchor move
  together.

## 6. Questions only the owner can answer (never filmed, or not measurable from the videos)

1. **Side alley** on the east of the main house: how wide is it, what closes it at the street end, what is it
   paved with, and is there any window, vent or pipe on the house's east wall?
2. **Roof from above**: is the back addition's roof flat or a low mono-pitch; how far does the flat stair
   dormer extend and what is its cheek clad in; is there any chimney on the main roof?
3. **Hidden zones on the second floor**: what is between the bathroom and the study (we have a 0.45 m solid
   wall — is it a thick wall, a cupboard, or are the rooms simply bigger?), and what is behind the hallway's
   east wall between the stair well and the purple room (0.56 m)?
4. **Tape measurements** that would settle the stacking: riser height of each stair (0.19 / 0.20 assumed) and
   the riser count of the upper stair (13 or 14); ceiling height of the green bedroom (2.85 or 2.95); loft
   door to the single step on the second-floor platform (1.9 or 1.25 m); depth of the quarter landing
   (0.60 or 0.84).
5. **Kitchen / east wall**: kitchen width wall to wall, and the width of the wall the back door is in measured
   outside (flank corner to east corner).
6. **Switches never demonstrated**: the 1-gang by the blue bedroom's balcony door (balcony lantern?), the
   switch for the second-floor bathroom lights (assumed on the hall side by the door), and whether the
   basement has a second switch at the bottom of its stair.
7. **Dining room**: confirm that "the teddy can turn on and off" in the v2 narration is "the telly".
8. **Unfilmed faces** we have modelled plain: the inside face of the study's door wall, the west wall of the
   study neck, and the upper flank windows (yellow room, en-suite, purple room, bathroom) as seen from outside.

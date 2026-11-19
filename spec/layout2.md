# Whole-house layout, level by level (Phase 2)

Companion to `spec/house.next.json` (canonical numbers) and `spec/RECONCILE2.md` (why). `spec/layout.md`
remains the phase-1 ground-floor description; where it differs from this file, this file wins.
Previews: `spec/plan_next_B.png`, `plan_next_G.png`, `plan_next_1.png`, `plan_next_2.png`,
`plan_next_site.png`, `plan_next_section.png` (redrawn by `python spec/validate_house_next.py`).

Frame: metres, Z up. Origin = centre of the inside face of the street-door threshold. +Y from the front
door into the house (toward the garden), +X to the right walking in. World Z = 0 at the ground-floor
finished floor. Rectangles are inside wall faces.

## 0. The house in one paragraph

An Edwardian house attached to its neighbour on the **west** (party wall, inner face x -0.65) with a
narrow **side alley on the east**. It has two parts. The **main body** (y 0.74..9.03, 5.41 wide outside)
is two storeys plus a converted loft under a 30-degree slate roof whose ridge runs parallel to the
street; a square two-storey bay with its own front gable projects 0.86 to y -0.12, and beside it the old
open porch is enclosed by the street doors under a slated lean-to. The **back addition** (y 9.03..17.36,
4.28 wide outside, x -0.88..3.40) is three full storeys under a flat roof, so its floors do not line up
with the main body's: the first floor is 0.38 lower at the rear than at the front, and the second floor
is 0.47 lower than the loft. One staircase against the stair flank wall (x 0.99..1.25) serves all of it:
basement stair under the main flight, second flight above it, with short steps where the two halves of
the house meet. Behind the house: a deck, a small garden with a brick fire pit and a brick workshop
across the end of the plot. In front: a block-paved forecourt with two cars.

```
        section looking east (not to scale)                       Z
                    ridge 9.14
                  /\________________ flat roofs 8.87 ___________
        30 deg  / loft \ |platform| hall 6.02 | bath | study     |   second floor 6.02
 gutter 6.50  /__6.49___\|__6.22__|___________|______|___________|   (loft 6.49)
 [gable]     | green bed  | landing |  rear corridor | blue bed  |
 [ bay ]     |  3.42      |  3.42  =|=   3.04  (yellow, en-suite)|   first floor 3.42 / 3.04
             |____________|_________|=QL 2.85____________________|--balcony 3.00
 porch       | hall / living / kitchen 2.95     | wc utl | dining|
 lean-to     |   0.00                           |  2.40  | 2.80  |   ground 0.00
 ____forecourt_-0.06__|________[basement -2.31]_|________|_______|deck -0.05__lawn -0.45__[shed]
           y -0.12    0.74        5.19..8.73   9.03            17.36
```

## 1. Basement (level B, floor Z -2.31)

- **Door**: the oak four-panel door in the lobby wall under the stairs (`d_basement`, centre
  (0.57, 7.63), 0.61 clear, hinged east, opening north into the lobby). A metal nosing at the threshold
  and the first riser immediately inside; light switch on the east wall just inside.
- **Stair** (`stair_basement`): shaft x 0.265..0.93 between white walls, running **south** under the main
  flight; 11 risers of 0.21 (9 straight at y 7.60..6.00 with a 0.20 going, then 2 winders turning east);
  the bottom riser stands in the room face of a plain opening through the 0.32 spine wall
  (x 0.93..1.25, y 5.19..6.00, head 1.85). Raked plaster soffit of the main stair overhead.
- **Room** (`basement`): x 1.25..4.25, y 5.19..8.73 (3.00 x 3.54) directly under the kitchen, flat
  ceiling 2.00, no window. A block 0.35 x 1.41 projects in the SE corner. West wall: consumer units,
  key board, network cabinet; east wall: boiler on a plywood board, hot-water cylinder; south wall:
  racks, gas meter. Wood-effect tile floor, white walls.

## 2. Ground floor (level G, all floors Z 0)

Unchanged from phase 1 except the corrections of `spec/phase2/ground_corrections.md`. Front to back:

- **Vestibule** x -0.65..0.65, y 0..1.73 (front recess widens to x 0.90). Street doors (pair, 1.18,
  **opening outward**) in the plane y -0.12..0; mahogany glazed inner doors at y 1.78 opening into the
  hall. Piers and a basket vault between the two recesses; the front recess ceiling has 45-degree
  haunches along both side walls.
- **Hallway** along the party wall: front hall x -0.65..0.65, y 1.83..5.05; passage 0.80 wide beside the
  stairs to y 7.68; lobby 1.64 wide (y 7.68..8.73) with the kitchen door (east), the basement door
  (south) and the overhead cupboard; arch wall y 8.73..9.03; rear corridor 1.10 wide to the dining door
  at y 12.23. Ceiling 2.95, dropping to 2.84 from the lobby bulkhead line (y 8.13) to the rear.
- **The 45-degree walls.** North of the living-room door the hall's east wall turns through a diagonal
  face (0.65, 5.05)→(0.99, 5.39) to the stair flank wall; inside the living room the matching corner is a
  chamfer (0.80, 4.78)→(1.21, 5.19) behind the door, which opens 135 degrees onto it.
- **Stairs** recess x 0.15..0.99, y 5.05..7.58: three winders at the foot, 15 risers to the quarter
  landing at Z 2.85 (y 8.13..8.73, over the lobby's 2.60 soffit).
- **Living room** x 0.80..4.30, y 0.99..5.19 (3.50 x 4.20) plus the square bay (x 1.10..4.00, y 0..0.99).
- **Kitchen** x 1.25..4.30, y 5.31..8.73 with the bar nook (x 1.37..2.62 to y 9.25) and the back door
  (clear x 3.42..4.18, inward, hinged east) in the rear wall of the main house.
- **WC** x 0.60..3.10, y 9.36..10.14, reached through the pocket door from the **utility**
  (x 0.60..3.10, y 10.26..12.23); both 2.40 high.
- **Dining room** x -0.65..3.10, y 12.36..16.86, ceiling 2.80; fireplace on the east wall; the north wall
  is 0.50 thick with three dark-lined recesses 0.38 deep: window, French doors (opening outward onto the
  deck), window.

## 3. First floor (level 1, split: quarter landing 2.85, rear 3.04, front 3.42)

**Circulation.** The main flight arrives from the south on the quarter landing (`landing1_ql`,
x 0.15..0.99, y 8.13..8.73, Z 2.85; walls east and north, vaulted soffit under the winders of the next
flight). One riser up to the west is the rear level (3.04): a strip beside the landing, then the
corridor 0.90 wide along the party wall (x -0.65..0.25) with a 45-degree chamfer on the corner at
(0.25..0.35, 8.73..8.83), a pier on the west wall, a plain semicircular arch (wall y 11.20..11.50) and a
small bay (x -0.65..0.40, y 11.50..12.39) ending at the pedimented blue-bedroom door. From the strip,
**two steps up** to the south (risers at y 8.13 and 7.88) reach the front level (3.42): a strip
x -0.65..0.15 beside the open stairwell (balustrade), widening at y 6.06 into the front landing
(x -0.65..0.99, y 4.95..6.06). The second flight starts at y 6.06 on the east side of that landing.

| room | rectangle | floor Z | ceiling | doors and windows |
|---|---|---|---|---|
| green bedroom | x -0.65..4.30, y 0.99..4.83 + bay x 1.16..3.90, y 0.14..0.99 | 3.42 | 2.85 | door from the landing in the rear wall (clear x -0.28..0.48, hinged east, opens in); sliding pocket door to its bathroom (clear x 2.34..3.03, pocket to the east); bay front window x 1.50..3.56 (side lights open outward), fixed cheek windows y 0.19..0.67, west window over the porch (x -0.41..0.23, opens outward) |
| green bathroom | x 1.25..4.30, y 4.95..8.73 | 3.42 | 2.75 | hinged door from the landing in the stair wall (clear y 5.13..5.89, hinged south); the pocket door; window in the north wall x 3.42..4.22 above the kitchen back door |
| yellow room | x 0.35..3.10, y 9.03..11.05 | 3.04 | 2.45 | door from the corridor (clear y 10.15..10.91, hinged north); flank window y 10.00..10.95 |
| blue en-suite | x 0.50..2.90, y 11.15..12.85 | 3.04 | 2.50 | door in its north wall into the bedroom (clear x 1.34..2.03, hinged east); small window in a deep recess of the east false wall, y 11.28..11.68 |
| blue bedroom | x -0.65..3.10, y 12.95..16.86, entrance recess x -0.65..0.40 from y 12.52 | 3.04 | 2.60 | landing door (clear x -0.48..0.28, hinged west, opens in); French doors x 0.47..2.11 opening outward onto the balcony; no other window |
| balcony | x 0.00..2.30, y 17.36..18.41 | 3.00 | open | black steel platform on two wall posts with 45-degree struts, railing 1.10 with bars at 0.165 centres |

The two corners where the green bedroom's bay opens into the room, (1.16, 0.99) and (3.90, 0.99), are chamfered
at 45 degrees from the floor to 2.30 and square above (feature `green_bay`), like the living-room bay below.

Partitions: front rooms / landing y 4.83..4.95; yellow / en-suite 11.05..11.15; en-suite / bedroom
12.85..12.95; blue door wall 12.39..12.52; corridor / yellow x 0.25..0.35; bay / en-suite x 0.40..0.50.
The stair flank wall x 0.99..1.25 is the green bathroom's west wall.

## 4. Second floor and loft (level 2, split: rear and hall 6.02, platform 6.22, loft 6.49)

**Circulation.** The second flight (13 risers) climbs north over the main flight and turns west on three
winders above the quarter landing, arriving on the stair head (x -0.65..0.15, y 8.13..8.73, Z 6.02).
North: the hallway along the party wall, 0.87 wide to a plain arch (wall y 11.20..11.50), 0.95 wide
beyond, ending at the study door (wall y 12.94..13.04). South: one riser up to the platform
(x -0.65..0.15, y 6.23..8.13, Z 6.22) with a balustrade over the well; at its south end the narrow loft door
stands on a 0.27 white riser (the "massive step"). The south wall of the well is in the same plane as the
loft-door wall (north face y 6.23), flat from the first-floor landing ceiling to the second-floor ceiling, and
the fixed square skylight (x -0.20..0.70, y 6.38..7.28) starts 0.15 north of it, over platform and well.

| room | rectangle | floor Z | ceiling | doors and windows |
|---|---|---|---|---|
| loft office | x -0.65..4.30, y 2.54..6.59 east of the TV wall (x 1.25); west of it the lobby x -0.65..0.31 to the door wall at y 6.13, and the cabinet block x 0.31..1.25, y 5.38..6.13 | 6.49 | knee wall 0.92 at the front, 30-degree slope, flat strip 2.12 for y 4.62..5.38, 30 degrees down to a 1.42 knee wall at the rear | door (0.61, hinged west, opens south into the lobby); Velux in the rear slope x 2.76..3.54; three pairs of hatch doors to the eaves |
| front eaves | x -0.65..4.30, y 0.95..2.44 + tunnel under the bay gable x 1.43..3.63 to y 0.14 | 6.49 | roof | two hatches in the front knee wall (x -0.35..0.70 and 2.45..3.50) |
| rear eaves | x 1.25..4.30, y 6.69..8.73 | 6.49, 6.37 east of x 2.35 | roof | one hatch in the rear knee wall (x 1.40..2.45) |
| purple room | x 0.32..3.10, y 9.29..11.20 | 6.02 | 2.60 | door at its NW corner (clear y 10.49..11.10, 0.61, hinged north); flank window centred y 10.25 |
| bathroom (sauna) | x 0.40..3.10, y 11.50..13.70 | 6.02 | 2.47 | door from the hallway (clear y 11.57..12.33, hinged south); flank window y 12.16..12.80 |
| study | neck x -0.65..0.30, y 13.04..14.15; main x -0.65..3.10, y 14.15..16.86 | 6.02 | 2.60 | door in the hall end wall (clear x -0.52..0.17, hinged west); rear window x 0.48..1.98 |

The loft's "cabinet block" (x 0.31..1.25, y 5.38..6.13) stands over the first-floor front landing: four deep
drawers and an open compartment facing south, its north side the well's south wall. The stair well
(x 0.15..0.99, y 6.23..8.73) is open to the second-floor ceiling right up to that wall; the stair flank wall
carried up is the loft's TV wall (x 1.25). Between the bathroom (north face y 13.70) and the study (south
face y 14.15) the wall is 0.45 thick: an unseen zone that absorbs what the two rooms' measurements leave over.

## 5. Roof

- **Main roof**: 30 degrees both ways, ridge at y 5.00, Z 9.14, dark slate. Front slope unbroken down to
  a white gutter at about Z 6.50 over the entrance bay. Rear slope only east of x 1.35 (with the Velux);
  it runs into the back addition's second-floor wall, and reaches a black gutter over the kitchen-door
  wall for x 3.40..4.53.
- **Bay gable**: ridge at x 2.525 running back from the street face to the main slope, apex Z 7.70, about
  43 degrees, white bargeboards and applied struts.
- **Stair dormer**: flat roof Z 8.87 over the stair (x -0.88..1.35 from just behind the ridge to y 8.73),
  dark grey panel cheek on its east side, fixed rooflight 0.90 square at x -0.20..0.70, y 6.38..7.28.
- **Back addition**: flat roof Z 8.87, white fascia on the rear edge, black gutter along the flank;
  shared chimney stack on the party line at the NW corner.
- **Porch**: slated lean-to from Z 2.85 at y -0.58 up to 3.90 against the main wall, soffit 2.62 with
  three downlights.

## 6. Outside

**Elevations** (details in `spec/phase2/front_elevation.md` and `rear_elevation.md`; the planes and the
openings on each are listed in `exterior.facades`):

| facade | plane | finish | openings |
|---|---|---|---|
| front A | y -0.12 | white masonry paint | street doors; ground-floor bay (4 lights); first-floor bay window |
| front B | y 0.74 | white | first-floor west window over the porch |
| bay cheeks | x 0.90 / 4.15 | white | first-floor cheek windows; ground-floor east cheek |
| east | x 4.53 | sandstone render | none known |
| kitchen-door wall | y 9.03, x 3.40..4.53 | sandstone render | back door; green-bathroom window |
| flank | x 3.40 | sandstone render, black plinth | WC, utility, two dining windows; yellow room, en-suite; purple room, bathroom |
| rear | y 17.36 | sandstone render, stock-brick pier at the party line | French doors and two side windows; balcony doors; study window |

First-floor front windows: sills Z 4.12 (bay), 4.20 (west); heads 5.97 / 6.00.

**Front** (`front.md`): block-paved forecourt x -0.72..4.53, y -5.20..-0.12, Z -0.06 falling to -0.14,
open to the footway; buff brick wall and pier on the west; grey supermini and white city car parked
nose-out; flag on a bracket between door and bay; bins at the east side, where the paving runs on to the
side alley.

**Side alley**: x 4.53..5.43 along the east wall of the main house (unverified width), closed at its
rear end by the diagonal side gate (4.50, 9.03)→(4.90, 9.88).

**Rear** (`garden.md`), south to north, Z relative to the ground floor:

| zone | extent | Z |
|---|---|---|
| side passage | x 3.40 → fence (1.5 narrowing to 1.2), y 9.03..17.55 | -0.30; two steps up to the kitchen door |
| deck ("patio") | x -0.75..3.40, y 17.36..20.50 | -0.05; long step on its north edge at -0.25 |
| garden path | along the east fence, y 17.55..23.40 | -0.45; one 0.15 riser up to the side passage |
| lawn | x -0.27..3.28, y 20.80..23.40, fire pit 1.01 square at (1.27, 22.26) | -0.45 |
| lavender bed | x -0.75..-0.27, y 20.80..23.40 | -0.45 |
| shed veranda | x -0.35..4.22, y 23.40..25.00 | -0.42 |

Boundaries: west = the neighbour's extension wall (3.0 high) to y 19.65, then a brown closeboard fence;
east = grey-painted closeboard fence from (4.90, 9.88) to (4.47, 23.2), converging on the house.

**Shed** (`shed.md`): red-brick flat-roofed building across the plot, outline x -0.87..4.45,
y 23.40..28.90, roof top Z 2.25. Covered veranda in front (soffit Z 1.83) with a store cupboard at its
west end; front wall y 25.00..25.28 with a window (x 1.15..2.45) and French doors (x 2.75..3.95);
workshop inside x -0.60..4.18, y 25.28..28.62, floor Z -0.32, with a rear window.

## 7. What stacks on what

| line | basement | ground | first | second |
|---|---|---|---|---|
| west party wall, inner face x -0.65 | - | all | all | all |
| stair flank wall x 0.99..1.25 | spine wall 0.93..1.25 | stairs / kitchen | stairwell / green bathroom | well and loft TV wall |
| east wall, inner face x 4.30 | lined to 4.25 | living, kitchen | green bedroom, bathroom | loft gable |
| old rear wall of the main house y 8.73..9.03 | basement north wall | arch wall, kitchen north wall | quarter-landing north wall, yellow south wall | stair-well north wall (thick to 9.29) |
| flank wall x 3.10..3.40 | - | wc, utility, dining | yellow, (en-suite false wall), blue | purple, bathroom, study |
| rear wall y 16.86..17.36 | - | dining | blue bedroom | study |
| living / kitchen cross wall y 5.19..5.31 | basement south wall | yes | no (partition at 4.83..4.95 instead) | - |
| upper arch wall y 11.20..11.50 | - | - | corridor arch | hallway arch, purple / bathroom wall |

Not stacking (documented in `RECONCILE2.md`): the dining south wall (12.23..12.36) against the
blue-bedroom door wall (12.39..12.52) and the study door wall (12.94..13.04); the chimney breasts
(dining east, blue bedroom west).

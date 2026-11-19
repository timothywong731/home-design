# garden — rear garden, deck ("patio"), side passage and boundaries

Source: v2:f_0146–f_0366 (daylight walk: French doors → deck → lawn → shed → side passage → kitchen
door), top-down views v4:f_0421–f_0426 (side passage from the second-floor flank window) and
v4:f_0457–f_0467 (whole garden from the second-floor rear window), v3:f_0257–f_0284 (from the balcony).
Full-res stills, pixel-grid crops and montages are in `reference/work/p2_rear_ext/` (`v2_tNNN.jpg` is
v2 at t = NNN s = frame f_(NNN+1); `c_v4_466_grid.jpg` is the near-plan view everything was scaled from).

Owner narration (v2 transcript 02:25–06:05, authoritative): "this door is openable, open both doors, it
goes to the patio, this is the garden patio … two garden planters in here … a metallic balcony … there's a
light here in the middle, I've got a lot of plants … outside there is a shed … a fire pit, square shaped,
in the middle … lots of lavender by the side and a garden panel … the house is in sandstone colour … this
is how the side looks like — stone pavement — now there's a step here, make sure you get this right … this
is your straight-in side entrance as well … the soil stack, the gutter, lots of windows … that goes to the
front … cat door is at the centre, there's a tap here, this is a kitchen door".

Related files: `spec/rooms/shed.md` (shed + workshop), `spec/phase2/rear_elevation.md` (house faces,
balcony structure, pipes).

**Dimension confidence.** X (across the plot): ±0.10 m on the deck, ±0.15 m elsewhere. Y (down the
garden): ±0.15 m to the deck edge, ±0.4 m beyond it (everything north of the deck comes from one oblique
top-down frame whose focal length is not known independently). Levels ±0.04 m. Scale references used: the
back-addition width, the fire pit (9 header bricks per side = 1.01 m), UK brick coursing, the 2.04 m
kitchen-door leaf, the French-door frame, fence-post/horizon geometry in v2:f_0319.

## 1. Shape, frame, levels

World axes as BRIEF (+Y = away from the street, +X = right walking in; so standing in the garden looking
back at the house, **west (−X) is on your right**). No room-local frame: all coordinates below are world.

Reference lines used (see doubts D1–D3 — two of these differ from `house.json`):

| line | value | note |
|---|---|---|
| rear wall outer (render) face `Y_R` | **y = 17.36** | dining room face 16.86 + **0.50 wall** (house.json has 0.30 → 17.16). `spec/phase2/ground_corrections.md` D2 measures the reveals 0.38 deep inside and leaves the outer face to the rear-elevation spec; 0.38 + 0.07 frame + 0.05 outer reveal = 0.50. Every garden y below hangs off this line — if it moves, move them all with it. |
| flank (back-addition east) wall outer face `X_F` | **x = 3.45** | house.json has 3.30 (a 0.20 m wall). Exterior evidence needs 3.45–3.55; see D1. Every x ≥ 3.0 below assumes 3.45. |
| kitchen rear wall outer face | y = 9.03 | house.json w_kitchen_n_ext centre 8.88 + 0.15 |
| main-house NE corner | (4.62, 9.03) | hidden behind the gate; ±0.08 |
| west boundary | x = −0.75 | party-wall line carried straight down the garden (verified parallel to the house in v4:f_0467) |
| east boundary (fence line) | from (4.90, 9.88) to (4.47, 23.2) | **not parallel to the house**: converges ~0.035 m per m (2°) toward the rear. See D2. |
| French-door axis | x = 1.225 | house.json |

Plot behind the rear wall: 5.4 m wide at the rear wall (−0.75 … 4.67) narrowing to 5.2 m at the shed
(−0.75 … 4.47); from the rear wall to the shed's veranda edge 6.04 m (deck 3.14 + step 0.30 + lawn 2.60).

**Zones (polygons, world x/y; Z = top surface relative to ground-floor finished floor = 0):**

| id | polygon | Z | surface |
|---|---|---|---|
| `side_passage` | (3.45, 9.03) (4.50, 9.03) [gate] (4.90, 9.88) → fence → (4.66, 17.55) (3.45, 17.55) | **−0.30** (falls ~20 mm to the drain) | grey sandstone flags |
| `kitchen_steps` | upper tread x 3.45–4.40, y 9.03–9.33; lower tread x 3.45–4.55, y 9.03–9.65 | −0.02 / −0.16 | grey sandstone, 2 risers ≈ 0.14 |
| `passage_step` | riser line y = 17.55, x 3.45 → fence (4.66); channel drain y 17.55–17.68 at the foot | drop −0.30 → −0.45 | "there's a step here" |
| `deck` ("patio") | x −0.75–3.45, y 17.36–20.50 (4.20 × 3.14) | **−0.05** | dark brown composite boards |
| `deck_step` (north) | x −0.55–2.45, y 20.50–20.80 | −0.25 | one long box tread, same boards |
| `deck_step_e` (side) | x 3.45–3.80, y 17.75–18.65 | −0.25 | loose timber box step on the lower path |
| `path` | x 3.45 (3.28 north of the deck) → fence, y 17.68–23.40 | **−0.45** | grey sandstone flags |
| `lawn` | x −0.27–3.28, y 20.80–23.40 (3.55 × 2.60) | −0.45 | grass |
| `lavender_bed` | x −0.75–−0.27, y 20.55–23.40 | −0.45 soil | lavender hedge |
| `shed_veranda` | x −0.35–4.22, y 23.40–25.00 | −0.42 | red clay block paving (see shed.md) |

So from the dining room you step out level onto the deck (door sill 50 mm), down two risers of 0.20 to
the lawn (deck → long tread → grass), and the paved side passage is one 0.15 riser above the garden path
and 0.25 below the deck. The kitchen door is two steps above the side passage.

```
 y                                                    (not to scale; +X to the right)
28.9 +===============================================+   shed back wall (window)
     |                 WORKSHOP                      |
25.0 +--[store]--[ window ]--[bell][French drs]--+---+
     |cpd|      covered veranda (block paving)   |rack|  wing wall with hooks
23.4 +pier----------------------------------------+--+
     |lav|                                  |  path  \
     |end|        LAWN   [fire pit]         | (flags) \   grey fence
     |er |        3.55 x 2.60               |  1.2     \  (converging)
20.8 |---+====== long step ========+--------+           |
20.5 | W fence  +------------------------------+        |
     |..........| trellis|                 [sq]|        |
19.65+--------- | + long |     DECK        [  ]| path   |
     | neighbour| planter|   4.20 x 3.14   [tr]| 1.1    |
     | extension|        |                 [ou]|        |
     | wall     |        |                 [gh]| [step] |
17.55|          |        |         [pebble pl] |=drain==|  <- step up to the passage
17.36+----------+==[w]==[French doors]==[w]====+        |
     :  (house: dining room)                   | side   |
     :                                    flank| passage|
     :                                    wall | 1.2-1.45
 9.9 :                                         |      /gate (diagonal)
 9.03:                 kitchen =====[door]=====+-----+   alley to the front ->
     -0.75            1.225                  3.45   4.62
```

## 2. Openings onto the garden (doors and gates)

Full exterior description of the house openings is in `rear_elevation.md`; summary of how each works:

| id | where | leaf / size | hinge and swing (observed) |
|---|---|---|---|
| French doors (`d_french`) | rear wall, axis x 1.225 | white uPVC pair, frame ≈ 1.33 × 2.32 incl. fanlight | hinged at the outer jambs, **both leaves swing OUT over the deck** (owner pushes the east leaf out, v2:f_0149–f_0153; confirms the house.json guess). Round cat flap in the lower pane of the **west** leaf. |
| kitchen back door (`d_back`) | kitchen rear wall, west edge of frame at the flank corner | white uPVC, obscure glass upper panel, solid lower panel with a white cat flap in its centre, fanlight over | hinge on the **east** jamb, **swings into the kitchen** (v2:f_0357–f_0359); lever handle on the west side, gold. |
| side gate | diagonal, hinge post on the kitchen rear wall at (4.50, 9.03), latch post = fence end post (4.90, 9.88) | ledged-and-braced timber, 0.90 × 1.75, in a goal-post frame (posts 95 × 95, head rail top 1.95 above paving) | two galvanised T-hinges on the garden face at the house end → swings **into the side passage** about the house-end post. Grey long-throw gate lock at 1.10 and a ring latch at 0.75, both on the latch stile. Shown closed. Leads to a ~0.9 m alley along the east wall of the main house "that goes to the front" (D3). |
| shed doors / window / store | see shed.md | | |

## 3. Architecture and built elements

### 3.1 Deck
- Composite deck boards, 0.145 wide with 5 mm gaps, wood-grain embossed, running **E–W (parallel to the
  house)**; ≈ 21 boards from the door to the north edge. Colour dark coffee brown, lighter where dry.
- Edges: closed fascia of the same boards laid horizontally — 3 boards (0.42) on the north face down to the
  lawn, 2 boards (0.25) visible on the east face above the passage flags, 3 where it meets the lower path.
- North step: a box tread 3.0 long × 0.30 deep, top 0.20 below the deck, 0.20 above the grass, stopping
  1.0 m short of the deck's NE corner and 0.2 m short of the NW corner (v2:f_0247, f_0251).
- Side step: separate dark-stained timber box 0.90 × 0.35 × 0.20 high standing on the lower path against the
  deck's east fascia immediately north of the drain (v2:f_0231, f_0235, f_0323).
- At the rear wall the boards run up to a dark brown sill board under the French doors.

### 3.2 Paving ("stone pavement")
- Riven grey Indian-sandstone flags, mixed sizes in a random coursed pattern (modules ≈ 0.29 / 0.60 / 0.90),
  10 mm mortar joints, surface gently cleft; wet and leaf-strewn in the video.
- Side passage: two to three flags across. A recessed (flag-infilled) inspection cover 0.60 × 0.80 with a
  thin steel frame at x 4.15–4.75, y 10.1–10.9 (v2:f_0345, v4:f_0426).
- The step (v2:f_0231–f_0235): the passage ends in a flag nosing with a rough-dressed 0.15 riser, and a
  black plastic slotted channel drain 0.13 wide lies across the full width at its foot, butting the deck
  step box on the west and the fence on the east.
- Garden path: same flags, 1.1–1.25 wide between the deck/lawn and the east fence, running to the shed
  veranda where it meets the red block paving at a slight diagonal (v2:f_0239, f_0241). A narrow gravel
  margin (0.05–0.10) separates flags and lawn.
- Kitchen steps: two sandstone-flag treads on rendered/stone risers (see zones). A square gully with a red
  plastic grate sits under the rainwater downpipe at (4.38, 9.15), east of the steps.

### 3.3 Boundaries
| side | from → to | construction | height |
|---|---|---|---|
| west, y 17.36–19.65 | flank wall of the neighbour's single-storey rear extension | yellow London-stock brick, stretcher bond, cream mortar; flat roof behind a brick parapet with a mortar/stone coping | ≈ 3.0 above the deck |
| west, y 19.65–23.4 | timber closeboard (feather-edge) fence, 2 bays of ≈ 1.83 on concrete posts with concrete gravel boards, 3 arris rails visible on our side | weathered brown, unpainted | 1.8 |
| east, whole length | closeboard fence on slotted concrete posts (bays ≈ 1.83), smooth face to us, **painted pale warm grey**; a diamond-lattice trellis topper (0.3) on the bays opposite the deck; capping rail | grey paint | ≈ 2.0 above the passage flags (2.15 above the garden path) |
| south-east | the diagonal side gate, then the kitchen rear wall | — | — |
| north | the shed across the full width | red brick | — |

Beyond the east fence is the neighbour's side yard and their three-storey stock-brick back addition (sash
windows facing us); beyond the west fence the neighbour's paved patio. Model both as plain massing only.

### 3.4 Fire pit ("square shaped, in the middle")
Centre (1.27, 22.26), i.e. on the French-door axis and 0.95 from the deck step, 0.63 from the shed paving.
Outer **1.01 × 1.01**, wall 0.215 thick, inner opening 0.58 × 0.58, **3 courses = 0.225 high** above the
grass: two courses of stretchers with a top course of **headers laid flat (9 per side)**, yellow London
stock brick with weathered buff mortar and a little moss. Inside: soil/ash with dried stems (model dark
soil or charred logs).

## 4. Surfaces and colours

Daylight, overcast, phone HDR (shadows lifted, slightly warm). "Sampled" = median of a patch in the still.

| surface | sampled sRGB | estimated true colour | finish |
|---|---|---|---|
| deck boards (dry) | #614E40 – #7A6652 (wet sheen #9E8E6C) | **#6B5645** coffee brown | matt, grain embossed, darker in the grooves; a wet-look roughness of 0.35 matches the video |
| deck fascia / steps / side step box | #494541 | **#4A3F38** | matt, dark stain |
| sandstone flags | #ACACAE, #9E9DA2, #CECFD1 (glare) | **#9A9CA0** mid grey, slight blue cast; individual flags vary ±8 % with darker cleft patches | matt, riven |
| mortar joints | — | #8C8A84 | |
| channel drain grate, gully | — | #1C1C1E black plastic | satin |
| east fence + gate (painted) | #C1BDBA, #C9C9C9, #B2B2B2, gate #BEBAB7 | **#BDB9B3** pale warm grey | flat exterior paint, board edges visible, green algae streaks at post feet |
| concrete posts / gravel boards | — | #A8A49C | rough |
| west fence (closeboard) | #B3AAA2, #A69A8F | **#8A735C** weathered brown with pale grey water streaks | rough sawn |
| neighbour's extension wall (stock brick) | #9A886C, #D4C8B3 | brick **#C2AE85** (range #B39A6E–#D3C39E), mortar #D8CFBD | |
| trellis panels | #80725A | **#6E5A44** brown stain | |
| timber planters | #614E40 | **#5A4638** dark walnut stain | slatted |
| fire-pit brick | top #BAA179, shaded side #73604C | **#B79A6A** yellow stock, mortar #A89878, moss #6F7A45 on the west side | |
| lawn | #869D70, #768F5C | **#6E8B4F**, with worn dark soil patches #3F3A30 near the shed paving and deck step | long rough grass |
| lavender | — | foliage #8E9A8C grey-green, no flowers (November) | |
| ivy / wisteria foliage | — | ivy #5F7F5A with cream variegation; wisteria #7FA050 yellow-green | |

## 5. Fixed fittings in the garden

| item | position | description |
|---|---|---|
| Channel drain | y 17.55–17.68, x 3.45 → fence | see 3.2 |
| Gully | (4.38, 9.15) | 0.15 square, red-brown plastic grate, under the black downpipe |
| Inspection cover | x 4.15–4.75, y 10.1–10.9 | recessed tray filled with the same flags |
| Hose reel, garden tap with 4-way timer splitter, second tap, AC unit, soil stack, low pipe along the flank base | on the flank wall | located in `rear_elevation.md` §5 |
| Bird table on the fence | fence post at ≈ (4.50, 22.5), top 2.45 above the path | small pitched-roof timber bird table on a black angle bracket fixed to a post that rises above the fence (v2:f_0187, f_0205, f_0308). Optional. |
| Bird-feeding station | (3.30, 20.95) on the lawn at the deck's NE corner | black shepherd's-crook pole 2.0 high with three arms: wire peanut feeder, green seed feeder, shallow white dish and a mesh tray. Optional (declutter candidate; it is prominent in every view of the deck). |
| Solar light | on the fence end post by the gate, 2.1 high | small black panel + lamp; optional |

## 6. Furniture and planters (all loose)

Sizes L × W × H; positions are centres unless ranges are given. Heights are above the deck.

| item | position | size | description |
|---|---|---|---|
| West planters ×2 | x −0.73–−0.33, y 17.65–18.65 and 18.65–19.65 | 1.00 × 0.40 × 0.42 each | slatted horizontal boards, dark walnut stain, black liner, dark compost; geraniums (red) and green foliage in the first, low herbs in the second (v2:f_0155, f_0167, f_0169) |
| **Trellis panels ×2** ("garden panel") | against the brick wall behind those planters, y 17.85–18.75 and 18.75–19.65 | 0.90 wide, 1.25 at the sides rising to **1.50 at the centre (convex arched top)** | framed diagonal (diamond) lattice, ≈ 0.11 m cells, laths 30 × 8, frame 35 × 35, brown stain (v2:f_0155, f_0167, f_0237) |
| NW corner planter + pot | (−0.50, 19.95) and (−0.15, 20.25) | planter 0.40 cube; terracotta pot Ø 0.35 × 0.30 on feet | pyracantha with red berries in the planter; trailing thyme in the pot (v2:f_0165, f_0197) |
| Folding chairs ×2 | (0.20, 18.35) and (0.20, 19.00), facing east | 0.60 × 0.65 × 1.05 | reclining camping chairs: mid-blue fabric (#5E7FA8) on a grey tubular steel frame. Real furniture — keep, standing upright and neat. |
| **Pebble planter** | x 2.30–3.30, y 17.40–17.82 (under the east rear window) | 1.00 × 0.42 × 0.36 | same slatted timber; filled to the brim with rounded river cobbles 60–120 mm (grey, buff, pink); a **wisteria** on bamboo canes, bushy to 1.6 with stems on wall wires up the east edge of the rear wall to 3.0 (v2:f_0215, f_0219, f_0221) |
| **Trough planter** | x 3.00–3.42, y 18.20–20.05 (along the deck's east edge) | 1.85 × 0.42 × 0.45 on four short feet | slatted, dark stain, black pond-liner lining, a few small plants (v2:f_0207, f_0217, f_0227, f_0237) |
| Square planter | x 3.00–3.42, y 20.05–20.48 | 0.42 × 0.42 × 0.50 | same family, a bare rose bush |
| Pots on the deck | blue glazed pot Ø 0.28 with a small maple at (2.65, 18.8); black pot Ø 0.26 with rosemary at (2.70, 19.5); large terracotta pot Ø 0.42 × 0.35 on feet at (2.70, 20.2) | | (v2:f_0183, f_0185, f_0207) |
| Small pot by the door | (0.35, 17.75) | Ø 0.18 | grey plastic pot with a spider plant — optional |

Owner: "I got two garden planters in here" (spoken at the doors, v2:f_0160) — the pebble planter on the
left and the long planters on the right as he steps out; "I've got a lot of plants".

## 7. Planting and decor

- **Lavender** ("lots of lavender by the side"): continuous low hedge of grey-green mounds, 0.45 high ×
  0.50 wide, in the bed along the west fence from the deck to the shed pier (v2:f_0193–f_0203).
- **Ivy** cascading from the balcony planters to 0.9 below the balcony tray (see rear_elevation.md).
- **Wisteria/jasmine** trained up the shed's west pier and along its fascia (see shed.md).
- **Passion-flower / ivy strands** climbing the east fence at four or five places (thin, sparse).
- A large sycamore overhangs from beyond the shed's NE corner; bamboo and a conifer hedge behind the
  west half of the shed (backdrop only).
- No garden ornaments other than the two small grey stone cat figures on the shed veranda (shed.md).

## 8. Lighting and switches

| light | position | notes |
|---|---|---|
| LED floodlight with PIR ("there's a light here in the middle") | rear wall, on the door axis x 1.225, z 2.55, under the balcony | black, 0.20 × 0.16 body tilted down, sensor below. Automatic; no switch shown. |
| Icicle fairy lights | hanging from the balcony tray's front and side edges, 0.3–0.5 strands | white cable, off in daylight; treat as one switchable decorative set |
| Lantern | rear wall first floor, east of the balcony doors (see rear_elevation.md) | switch presumably inside the blue bedroom — not shown |
| Twin-head security floodlight/camera | kitchen rear wall above the back door, z 3.25 | white; automatic |
| Shed veranda downlights | see shed.md | |

No exterior switch is demonstrated anywhere in v2; do not invent switch plates outdoors. For the viewer,
bind the floodlight and the fairy lights to a click on the fitting itself.

## 9. Reference frames

| subject | frames |
|---|---|
| French doors opening outward, threshold, cat flap, view out | v2:f_0146–f_0153 |
| Deck west side: trellis, planters, chairs, brick wall | v2:f_0153–f_0157, f_0163–f_0169, f_0237 |
| Deck east side: fence, trough, pots, pebble planter | v2:f_0159–f_0161, f_0183–f_0187, f_0207, f_0215–f_0221 |
| Rear elevation from the deck | v2:f_0171–f_0181, f_0209–f_0213 |
| Lawn, fire pit, lavender, west fence | v2:f_0189–f_0203, f_0245–f_0247 (fire-pit bricks: still `c_firepit_202.jpg`) |
| East fence, bird table, feeder pole, garden path | v2:f_0205, f_0217, f_0227–f_0229, f_0239–f_0241, f_0308–f_0311 |
| The step + channel drain, deck side step | v2:f_0223–f_0225, f_0231–f_0235, f_0323 |
| Whole house from the shed | v2:f_0249–f_0255 (still `v2_t250.jpg`) |
| Side passage looking south, fence, gate, neighbour | v2:f_0313–f_0319 (still `v2_t318.jpg`) |
| Gate, kitchen door, steps, gully, inspection cover | v2:f_0343–f_0351 (stills `v2_t342.jpg`, `v2_t344.jpg`) |
| Plan view of the side passage and gate from above | v4:f_0422, f_0426 (stills `v4_t421.jpg`, `v4_t425.jpg`, crops `c_v4_421_gate.jpg`, `c_v4_425_gate.jpg`) |
| **Plan view of the whole garden from above** | v4:f_0467 (still `v4_t466.jpg`, gridded crop `c_v4_466_grid.jpg`), v4:f_0458–f_0464 |
| Garden from the balcony | v3:f_0260–f_0284 |

## 10. Interactions

| object | action | evidence |
|---|---|---|
| French doors | both leaves open outward 0 → 100°, hinges on the outer jambs; east leaf is the active leaf (handle used) | v2:f_0146–f_0153, "open both doors" |
| Cat flap in the French door (west leaf) and in the kitchen door | flap swings ±60° | "cat door" v2:f_0118, f_0358 |
| Kitchen back door | opens inward 0 → 95°, hinge east | v2:f_0357–f_0359 |
| Side gate | opens into the side passage 0 → 100° about the house-end post | hinges visible, not operated |
| Garden tap(s) | water can run (tap on the flank wall by the kitchen door: "there's a tap here") | v2:f_0353 |
| Floodlight, fairy lights | on/off by clicking the fitting | — |
| Shed doors, shed window top lights, store cupboard doors | see shed.md | v2:f_0257–f_0277 |

## Declutter (excluded)
Fallen leaves and twigs, the green garden hose trailing along the path and deck edge, watering lance,
loose bricks and plant saucer on the deck, empty plastic pots, the aluminium combination ladder leaning
on the fence by the shed, the black-and-white cat, neighbours' bins and ladders, compost bags.

## Doubts

- **D1 — flank wall plane.** house.json puts the back-addition flank outer face at x = 3.30 (0.20 m wall).
  From the garden (v2:f_0251, frontal, scale from the 2.32 m door height) the rear façade's east corner is
  0.60 m east of the east side-window frame and 2.35–2.5 m east of the French-door axis, i.e. x ≈ 3.45–3.7,
  and the owner stresses that the dining windows "go quite deep"; ground_corrections.md gives the utility
  window a 0.25 m inside reveal, which with frame and outer reveal already needs a ≥ 0.40 m wall (3.50).
  At the kitchen end the back-door frame's west edge is flush with the same wall. I used **3.45**
  (wall 0.35). If the reconciler keeps 3.30, subtract 0.15 from every x ≥ 3.0 here (widths measured from
  the wall stay valid); if it goes to 3.55, add 0.10. The kitchen door frame must then be about 0.80–0.85
  wide (house.json: 0.95) or sit 0.15–0.25 further east to keep its west edge on the wall corner.
- **D2 — east fence skew.** Three independent reads disagree unless the fence converges on the house:
  passage width 1.45–1.75 at the gate (gate geometry, v4:f_0422/f_0426; horizon method in v2:f_0319),
  1.35–1.4 mid-way, 1.0–1.1 beside the deck and 1.2 beside the lawn (v4:f_0467). Modelled as one
  straight line (4.90, 9.88) → (4.47, 23.2). A parallel fence at x ≈ 4.6 would be within ±0.25 m of it
  everywhere and is an acceptable simplification.
- **D3 — the alley to the front.** The gate closes a passage that runs between the east wall of our main
  house and the neighbour's brick flank (an air-conditioning condenser hangs on our wall in it;
  v2:f_0343, v4:f_0422). The owner calls it "your straight-in side entrance" and says it "goes to the
  front". So the main house is **not attached on its east side**; `house.json` calls that wall a party
  wall. Width ≈ 0.9 m, with a second (black iron) gate for the neighbour at the same point — it looks
  shared, boundary down the middle. Above the gate there is open sky and, low down, a clear sight line
  to a gabled house across the street (crop `c_v2_342_gap.jpg`), so the gap is open right through.
  **`spec/rooms/front.md` says the opposite** ("mid-terrace frontage, attached houses both sides, no side
  gate at the front") — one of the two is wrong and the reconciler must look at the front footage for a
  door or gate between the two houses. Until then: model the gate, 1.5 m of alley paving behind it
  (same flags, Z −0.30) and the two side walls, and close the far end with a plain dark plane.
- **D4 — garden length.** Deck depth 3.14 is firm to ±0.15; lawn 2.60 and veranda 1.60 are ±0.3 each.
- Deck height above lawn (0.40) and passage (0.25), kitchen step risers: ±0.04.
- Planter lengths and exact y positions ±0.15; pot positions are indicative.
- Fence heights ±0.1; whether the trellis topper runs the whole length of the east fence (seen only
  opposite the deck).
- West boundary beside the deck: the neighbour's wall face is taken as x = −0.75; the yellow render of
  our rear wall actually stops ≈ 0.25 m east of that against an exposed brick pier (rear_elevation.md §3).

## Reconciled dimensions (house.next.json)

Added by the phase-2 reconcile step. `spec/house.next.json` is canonical; where the text above differs, the values below win. Reasons and evidence: `spec/RECONCILE2.md` (decision ids in brackets).

- **Rear wall face y 17.36**: adopted [E1]; all y values stand.
- **Flank face x 3.40** (this spec used 3.45) [E2]: move every x keyed to the flank by **-0.05** — deck x -0.75..3.40
  (4.15 wide), side passage and kitchen steps from x 3.40, side step box x 3.40..3.75, trough planter x 2.95..3.37, rear
  render x -0.50..3.40. Fence, gate, path, lawn, fire pit: unchanged.
- **Main-house NE corner (4.53, 9.03)** (was 4.62): the east wall is 0.23 thick; the kitchen-door wall is 1.13 wide.
- **Kitchen back door**: clear x 3.42..4.18 (frame 0.86), so its frame's west edge is on the flank corner as seen.
- **D3 resolved** [E3]: the alley is real (`exterior.zones.side_alley`, x 4.53..5.43, y 0.74..9.03, unverified width);
  the east wall of the main house is external. Model the alley through to the forecourt, not a dark plane, once the
  owner confirms its street end.
- Zones and levels are in `exterior.zones` / `exterior.steps`: side passage -0.30, deck -0.05, path and lawn -0.45,
  veranda -0.42; kitchen door 2 x 0.15, passage step 0.15, deck to lawn 2 x 0.20.

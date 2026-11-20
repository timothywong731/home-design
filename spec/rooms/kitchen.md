# Kitchen (`kitchen`) — visual / dimensional specification

Source frames: f_0287–f_0435 (main tour) and f_0755–f_0767 (second, cleaner sweep). Cross-checked
against `reference/transcript.txt` in the verification round: all owner-named items are present (the two
rubbish bins and the shelf mugs/glasses were added then). All dimensions in mm unless stated; "≈" = estimated from reference objects (worktop
900–910, UK door leaf 1981x762, door handle 1000, 100 mm tile courses, American fridge 912x1780).
Tolerance on room-scale numbers ±100 mm, on joinery modules ±30 mm.

## 0. Where the room sits (global context)

- The kitchen is on the **+X (right-hand) side of the hallway**, immediately to the rear of the
  staircase. Its door is in the hall's +X wall, in the stretch between the foot-of-stairs cross wall
  (which holds the solid-oak under-stairs cupboard door, facing +Y) and the hallway arch.
  Evidence: f289–291 (looking down the hall toward the dining-room door, kitchen door leaf on the
  right), f753–754 (kitchen doorway and under-stairs door form an inside corner), f301–304 (from
  inside the kitchen the under-stairs door is seen on the left = toward the house front).
- You enter walking in **+X**. On entering: **left = +Y (house rear)**, **right = −Y (house front)**,
  **straight ahead = +X**.
- The fridge/oven wall is the same wall as the hall door and backs onto the under-stairs
  cupboard/stair. The hob wall is the +X wall. The white uPVC back door is in the rear (+Y) wall at
  its +X end and leads outdoors (dark at night) — presumably a side-return yard alongside the
  utility room. The bar nook is recessed into the rear (+Y) wall and backs toward the utility.

## 1. Shape & dimensions

**Room-local frame** (axes parallel to the BRIEF world axes):

- Origin `K0` = floor-level inside corner where the **hall-door wall (−X wall)** meets the
  **sink wall (−Y wall, house-front side)**.
- `x` = 0 at the hall-door wall → 3050 at the hob wall (= world +X).
- `y` = 0 at the sink wall → 3420 at the nook / back-door wall (= world +Y, toward house rear).
- `z` = 0 at kitchen finished floor (flush with hallway oak, world Z = 0).

| Wall | Name used below | Local position | Length | Faces (normal into room) |
|---|---|---|---|---|
| W | **door wall** (hall door, fridge, ovens) | x = 0 | 3420 | +X |
| E | **hob wall** (hob, hood, whiteboard) | x = 3050 | 3420 | −X |
| S | **sink wall** (sink, plate rack, wine rack) | y = 0 | 3050 | +Y |
| N | **nook wall** (bar nook, plaque, back door) | y = 3420 | 3050 | −Y |

- Plain rectangle **3050 (x) × 3420 (y)**, ≈10.4 m². No chimney breast, no bay.
- **Ceiling height ≈ 2950** (flat). Derivation: projective fit on the nook wall in f766 using floor,
  back-door handle (1000) and uPVC leaf top (2050) reproduces the worktop at 896 and gives reveal
  head 2650, cove underside ≈2840, ceiling ≈2950. Use the house-wide ground-floor ceiling height
  from `spec/house.json` if it differs by <150.
- **Bar nook alcove** in the nook wall: opening x = 120 → 1370 (1250 wide), recess depth ≈ 520
  (so its back face is at y ≈ 3940), floor to soffit; black soffit at z = 2030. Wall above the nook
  is flush plain wall up to the cove.
- **Back-door reveal**: the door set sits ≈120 back from the room face of the nook wall, in a
  square plastered reveal x = 1990 → 2960, head at z = 2650. Plain wall 2650 → cove above it.
- Sizing logic: door wall = 600 (sink-run return) + 600 (oven tower) + ≈1030 (fridge housing) +
  ≈210 (wall strip with switch) + ≈980 (door set incl. architraves) = 3420. Hob wall = ≈910 clear
  + 18 + 600 + 200 + 800 + 270 + 620 = 3418 ✓. Sink wall wall-units = 630 + 600 + 900 + 300 + 300 +
  320 = 3050; nook wall = 120 + 1250 + 620 + 970 + 90 = 3050 ✓.
- **Floor level**: flush with the hallway (no step). A dark hardwood threshold bar sits in the
  doorway (see §3).

## 2. Openings

### 2.1 Hall door (door wall, x = 0)

- Structural opening: y = 2518 → 3340 (30 mm linings each side, clear 2548 → 3310 = 762 leaf),
  head z ≈ 2030. Architrave legs y = 2438 → 2518 and 3340 → 3420: the +Y leg sits tight in the
  room corner against the nook wall.
- Leaf: **1981 × 762 × 35 oak-veneer "2-light over 2-panel" Victorian door** — two tall upper
  lights of **frosted/obscure (satin) glass**, two short raised-and-fielded oak panels below.
  Stiles ≈ 95, top rail ≈ 95, centre muntin ≈ 95, lock rail ≈ 190 spanning z ≈ 760 → 950,
  bottom rail ≈ 230. Upper lights ≈ 240 w × 935 h each with a small ovolo glazing bead; lower
  panels ≈ 240 w × 530 h, raised-and-fielded with a plain ovolo sticking (no bolection).
  Straight vertical oak grain, satin lacquer. Sampled sRGB #8c784f / #998049 / #675436 (warm
  light) → neutral estimate **#b08a55** (golden oak).
- **Hinges on the +Y jamb** (the jamb in the room corner); **opens outward into the hallway**,
  swinging toward the house rear. Three polished-brass butt hinges. In the video it stands open
  ≈ 90–100°. Model it open 90°.
- Furniture: **polished brass lever on a long rectangular backplate** (≈ 150 × 40, scroll lever
  ≈ 110), both sides, lever axis z ≈ 1000, 60 from the −Y (latch) edge.
- Lining + architrave: **white gloss**. Kitchen-side architrave ≈ 80 wide, stepped/ogee profile
  (flat 40 mm inner band, quirk, 27 mm ogee, 13 mm outer fillet), mitred corners, standing on
  small plinth blocks no taller than the skirting. No overdoor/pediment on the kitchen side.
  (The hall side of this doorway belongs to the `hallway` spec.)
- Colour: sampled #dad6c8 → neutral **#f4f3ef** (brilliant white gloss).

### 2.2 Back door (nook wall, y = 3420, at the +X end)

- White **uPVC external door set with fixed toplight**, set in the reveal described in §1.
  Outer frame x = 2000 → 2950 (950 wide), z = 0 → 2640. Frame members ≈ 70 wide, chamfered uPVC.
- Transom at z ≈ 2080 → 2150. **Toplight** above: single fixed pane ≈ 780 × 430, clear glass
  (reads near-black at night, sampled #2a2a28).
- **Leaf ≈ 850 × 2040**: half-glazed. Upper glazed panel ≈ 560 w × 940 h, clear double glazing
  (dark, reflects the under-cabinet lights), its sill at z ≈ 1010; a ≈ 25 mm projecting drip/weather
  bar moulding across the leaf just above the glass and a rebated mid-rail below it. Lower solid
  flat uPVC panel ≈ 560 w × 720 h with a mitred bead moulding around it.
- **Cat flap** in the lower panel: white square frame 220 × 240 with smoked-grey arched flap and a
  small red rotary lock at bottom right; centred ≈ 80 right of panel centre, bottom of frame
  at z ≈ 190.
- **Hinges on the +X jamb** (3 white flag hinges visible inside ⇒ **opens inward**, swinging
  against the hob-wall/whiteboard gap). Model closed.
- Handle: **polished brass lever on a long narrow backplate** (≈ 240 × 30, with euro-cylinder
  below the lever) on the −X stile, lever at z ≈ 1000.
- Colour: sampled #dfdccd / #ddd9cf → neutral **#f3f3f0** white uPVC, satin-gloss.
- Connects to: outdoors (side-return yard). Nothing beyond is modelled; put a dark backdrop
  behind the glass.

No windows. No other openings.

## 3. Surfaces

### 3.1 Walls
- All four walls: one colour, **flat warm white emulsion**, no dado rail, no picture rail, no
  panelling. Sampled #dfdbcf (f766), #d6d1c5 (f332), #d8d5c6 (f402), #cbc8b7 (f758, dimmer) →
  neutral estimate **#f1efe9**. Matt.
- Inside the nook, the two side reveals are the same white.

### 3.2 Skirting
- White gloss, **≈ 170 high × 20 thick**, profile from floor up: 120 flat, small 8 mm quirk,
  30 mm ogee/torus, 10 mm top fillet. Present on all exposed wall lengths: hob wall from the
  NE corner to the cabinet end (x = 3050, y = 2510 → 3420), nook wall pier between nook and back
  door reveal and returning into the reveal, the short pier left of the nook, and the door wall
  strip between fridge housing and hall-door architrave. Neutral **#f4f3ef**.

### 3.3 Cornice / ceiling
- **Plain run plaster cornice, no dentils**: ≈ 110 down the wall × 110 across the ceiling.
  Profile from wall upward: 12 mm bead/fillet at the bottom, 75 mm quarter-round **cove**, 12 mm
  step, 10 mm fillet onto the ceiling. Runs unbroken round all four walls (it passes above the
  cabinets and above the back-door reveal; the hood chimney butts up to the ceiling in front of it
  — notch the cornice round the chimney). White, matt.
- Ceiling: flat, smooth, white matt. Sampled #c7c2af / #bebaaa (in shade) → neutral **#f5f4f0**.
  No ceiling rose.

### 3.4 Splashback tiles
- **Light warm-grey gloss ceramic metro tiles, 100 × 300, flat (non-bevelled) with slightly
  cushioned edges, laid in horizontal half-bond (brick bond)**, 3 mm **white** grout.
  Sampled #beb9ac (f367), #b9b6a8 (f766) → neutral **#c4c2bd**; gloss, slight colour variation
  tile to tile (±4 %).
- Extents:
  - Hob wall: from the worktop (z = 910) up to the wall-cabinet pelmet underside (z ≈ 1420) from
    y = 0 to the left end of the worktop (y ≈ 2510); behind the hood the same tiling continues up
    to z ≈ 1420 only (5 courses); plain painted wall above, behind the hood and chimney.
  - Sink wall: full length x = 0 → 3050, z = 910 → 1420.
  - Door wall return behind the corner worktop (y = 0 → 600): z = 910 → 1420.
  - Nook back wall: z = 910 → 1464 (underside of lower glass shelf), 5½ courses; the two nook
    side reveals are tiled to the same height.
- A 100 mm-high worktop **upstand in the same quartz** is NOT present — tiles sit directly on the
  worktop with a white silicone bead.

### 3.5 Floor
- **Wood-effect porcelain plank tiles, ≈ 200 × 1200**, weathered grey-brown oak print with
  knots and dark streaks, matt/satin. **Long axis parallel to the door wall (planks run along
  local y / world Y)**, i.e. you see the plank ends side-on as you walk in. Laid in an irregular
  1/3-offset stagger. **3–4 mm light-grey/off-white grout**, clearly visible (#cfcabb).
- Colour: sampled #867854 (f766), #857857 (f758), #9d9161 (f346), #a69874 (f372) → neutral
  base **#8e8676**, dark grain/knots **#5c564b**, light streaks **#aba392**. Roughness ≈ 0.45.
- Tiles run under the cabinet plinths and into both door reveals.
- **Threshold at the hall door**: dark walnut-stained hardwood bar ≈ 60 wide × 8 proud with
  eased edges, under the closed-door line, colour **#4a2f1f**; hallway oak on the other side.
- Back door: tiles run to the uPVC frame; white uPVC low threshold 40 high.

## 4. Fixed fittings

### 4.1 Cabinet system (applies to every unit)

- **Colour**: very dark navy / blue-black painted **ash-grain** timber (open grain visible in
  raking light). Sampled #272526, #2d2d2f, #383739, #3e3e40, #424143 (all under warm light) →
  neutral estimate **#23252d**; satin (roughness ≈ 0.4). Carcass edges, end panels, plinths,
  cornice and pelmet all the same colour.
- **Door style**: 5-piece framed "shaker with moulding" door, 20 thick. Stiles and rails
  **≈ 85 wide**; a **12 mm ogee/bead moulding** runs round the inside of the frame; flat centre
  panel recessed 6 mm. Drawer fronts ≥ 250 high are framed the same way; shallow top drawers are
  a flat slab with a 4 mm edge radius. 3 mm gaps between fronts.
- **Handles**: satin/antique-brass **knurled T-bar** pulls, Ø 12 bar on two Ø 10 posts standing
  32 off the door, bar length ≈ 220 (hole centres 160). Vertical on doors, centred 55 in from the
  opening edge; on base doors the top of the bar is ≈ 60 below the door top, on wall doors the
  bottom of the bar is ≈ 60 above the door bottom, on tall doors the bar is centred at z ≈ 1750
  and ≈ 300 long. Horizontal and centred on drawers/flap doors. Corner doors have a **Ø 30 knurled
  brass knob** instead. Neutral colour **#b09a62**, metallic, roughness 0.35.
- **Base units**: plinth 150 high, recessed 40, same navy. Carcass 150 → 870. Door 715 high.
  Depth 580 + 20 door.
- **Worktop**: white quartz with soft grey marble veining (Calacatta style: sparse long diagonal
  veins, some forked), polished, **30 thick, top at z = 910**, square edge with 2 mm arris,
  20 overhang at the front. Sampled #dad5c7 / #dedace / #d3cebb → neutral **#f2f1ee**, veins
  **#b5b3ae**. One L-shaped piece on hob wall + sink wall (joint at the internal corner), a
  separate piece in the nook.
- **Wall units**: 900 high × 320 deep (300 + door). Light pelmet 35 high under them
  (underside z = 1420), carcass 1455 → 2355, **cornice** on top 45 high projecting 25 (small ogee
  with top fillet) → top z = 2400. Continuous **LED strip** behind the pelmet (see §7).
- **Tall units** (oven tower + fridge housing): 600 deep, top of carcass 2435, same 45 cornice
  → z = 2480 (≈ 80 higher than the wall units; the wall-unit cornice dies into the tower side).

### 4.2 Hob wall (x = 3050) — in run order from the back-door corner (y = 3420) toward the sink wall

Viewpoint: standing in the room facing the hob wall (+X); left = house rear (+Y).

| # | y from → to | Base level | Wall level |
|---|---|---|---|
| H0 | 3420 → 2508 | **clear wall** 912 (back door swings into it). Glass memo board on wall, §6 | — |
| H1 | 2508 → 2490 | 18 end panel to floor; worktop overhangs it 30 | — |
| H2 | 2490 → 1890 | 600 base, one door, hinged on the +Y side, handle on the −Y edge | **W1** 600 single-door wall unit y 2508 → 1908, hinged +Y, handle on −Y edge at the bottom. Both sides exposed (finished end panels). |
| H3 | 1890 → 1690 | 200 narrow pull-out, framed front, vertical T-bar on its −Y edge | (bare tiled wall 168 wide between W1 and hood) |
| H4 | 1690 → 890 | **800 three-drawer pan unit**: top drawer 175 high (slab), two 270-high framed drawers; horizontal T-bars centred, each ≈ 45 below the top edge of its front | **Hob + hood**, below |
| H5 | 890 → 620 | 270 corner door with brass knob (knob 50 from its +Y edge, 80 below top), hinged −Y | **W2** 500 wall unit y 830 → 330: pair of narrow doors (≈ 245 each), each with a T-bar on its −Y edge; exposed finished side facing the hood at y = 830 |
| H6 | 620 → 0 | return of the sink-wall run (internal corner of the L worktop at y = 620) | return of sink-wall wall units (front plane at y = 320) |

- **Hob**: Samsung 75 cm stainless-steel **5-burner gas hob**, 750 × 520, centred at y = 1290,
  front edge 55 back from the worktop edge. Brushed stainless tray with a 5 mm raised rim;
  three matt-black cast-iron pan-support grids (left / centre / right); large triple-ring wok
  burner on the +Y (left) third, two burners centre (front smaller), two right; **five round
  stainless control knobs in a row along the front edge**, from the left-centre toward the
  centre (Ø 38, 45 pitch); small "SAMSUNG" wordmark at the front right.
- **Hood**: brushed-stainless **angled (inclined) chimney hood, 900 wide**, centred y = 1290
  (y 1740 → 840). Lower edge z = 1540 where it stands 150 off the wall; the face leans **outward
  toward the top** at ≈ 25° from vertical so the top edge (z ≈ 2130) stands ≈ 400 off the wall.
  Face from the bottom: plain flap 0 → 72 % of the slope, then a **black perimeter-extraction
  slot** 22 mm high running the middle 80 % of the width with radiused ends, a 3 mm polished
  seam line right above it across the full width, then a 26 % upper band carrying a centred
  black touch-control strip (≈ 190 × 22). Sides closed in stainless (trapezoidal). Underside:
  recessed matt-black strip 60 deep with **two Ø 55 LED spotlights** 150 in from each end.
  Steel colour sampled #a9a58d (lit) → neutral **#b9b9b6**, metallic 1.0, anisotropic brushed
  (vertical brushing), roughness 0.3.
- **Chimney**: square brushed-stainless duct cover **250 wide × 220 deep**, centred on the hood,
  from the hood top to the ceiling (two telescopic sections, joint at z ≈ 2500); a small
  rectangular vent grille near the top on the sides.

### 4.3 Sink wall (y = 0) — in run order from the hob-wall corner (x = 3050) toward the door wall

Viewpoint: facing the sink wall (−Y); left = hob wall (+X), right = oven tower.

Base level (front plane y = 600):

| # | x from → to | Unit |
|---|---|---|
| S0 | 3050 → 2450 | corner (occupied by hob-wall run; worktop only) |
| S1 | 2450 → 1850 | **integrated dishwasher**: one full-height framed door 600 × 715 with a **horizontal** T-bar centred 55 below its top edge |
| S2 | 1850 → 1050 | **800 sink base**, pair of 400 doors, T-bars at the meeting stiles |
| S3 | 1050 → 600 | 450 single door, hinged −X (tower side), T-bar on its +X edge |
| S4 | 600 → 0 | blind corner behind the oven tower — worktop continues to the door wall, no visible front |

- **Sink**: stainless-steel **undermounted double bowl**, cut-out x = 1820 → 1080 (740) ×
  y = 110 → 510 (400), square bowls with R15 corners, 200 deep, a 25 mm-wide steel divider between
  them at x ≈ 1450. +X bowl has a black waste-disposer flange, −X bowl a basket strainer.
  Brushed steel **#a9aaa8**.
- **Taps** (on the worktop behind the sink, y ≈ 60): (a) chrome **professional spring-neck
  pull-down mixer** at x = 1450 — vertical Ø 28 riser 520 high wrapped in an open coil spring
  that arcs over forward 220, side lever on the −X side, plus a horizontal spray-arm cradle
  halfway up; (b) small **brushed-nickel angular filter/boiling-water tap** at x = 1180, 250 high
  with a square-ish 120 mm reach spout.
- Worktop drainer grooves: none.

Wall level (front plane y = 320; pelmet underside 1420, cornice top 2400):

| # | x from → to | Unit |
|---|---|---|
| T0 | 3050 → 2730 | corner (hob-wall W2 return) |
| T1 | 2730 → 2425 | 305 corner door with **brass knob** (knob on its +X edge, 80 above the bottom) |
| T2 | 2425 → 1825 | 600 single door, hinged +X, T-bar on −X edge |
| T3 | 1825 → 925 | **900 plate-rack unit**: upper 380 is a top-hung **lift-up flap door** (framed, horizontal T-bar centred near its bottom edge); lower 520 is an **open plate rack** — black frame, a front rail 40 high at the bottom, **13 vertical Ø 10 black dowels** at ≈ 65 centres in a front row (and a matching rear row), holding ≈ 10 white dinner plates on edge |
| T4 | 925 → 625 | **300 wine rack**: open lattice 2 columns × 6 rows of ≈ 123 w × 132 h cells, 18 mm dividers, a few bottles neck-out |
| T5 | 625 → 325 | 300 single door, hinged −X, T-bar on +X edge |
| T6 | 325 → 0 | corner; on the **door wall** a 280 knob door faces +X at y = 320 → 600 (front plane x = 320), meeting the tower side at y = 600 |

### 4.4 Door wall (x = 0) — from the sink-wall corner (y = 0) toward the hall door

Viewpoint: facing the door wall (−X); left = sink wall, right = hall door.

- y 0 → 600: end of the sink-wall worktop + the T6 corner wall cupboard above it.
- **Oven tower**, y = 600 → 1200, front plane x = 620, side panel at y = 600 exposed above the
  worktop. From the floor: plinth 0 → 150; **lower appliance** 150 → 550 (black glass
  drop-front / warming-drawer type with a brushed-stainless surround trim and a steel bar handle
  along its top); **single built-in oven** 550 → 1145 (black glass door, full-width brushed-steel
  bar handle at the top of the door, 90 mm black control band above it with a small round
  colour display at centre); **compact oven / combi-microwave** 1145 → 1600 (black glass, bar
  handle, its touch-control band at the very top with white/blue digits); a **40 mm light-oak
  filler strip** 1600 → 1640 (bare carcass colour **#c9a877** — a characteristic detail);
  framed cupboard door 1640 → 2435 (595 w × 795 h, hinged −Y, long T-bar on its +Y edge);
  cornice to 2480. Appliances are 595 wide, black glass **#141516**, gloss.
- **Fridge housing**, y = 1200 → 2230: 18 panel | 994 clear | 18 end panel (full height,
  x 0 → 600). **American side-by-side fridge-freezer**, 912 W × 1780 H × 716 D, centred in the
  housing, doors standing ≈ 110 proud of the housing front. Finish matt black / graphite steel,
  sampled #2e2c22 → neutral **#26272a**, roughness 0.5. Left (−Y) door 0.42 of the width with a
  recessed **ice/water dispenser** (≈ 290 w × 390 h niche, centre z ≈ 1010, gloss-black control
  strip above it); right door plain. Handleless (recessed vertical grips at the meeting edges).
  Above the fridge: open black niche z 1790 → 2040, then a **bridging cupboard** with a single
  wide top-hung flap door 994 × 395 (z 2040 → 2435), framed, horizontal T-bar centred near its
  bottom edge; cornice to 2480 continuous with the tower.
- y 2230 → 2438: plain wall strip with skirting; **single white rocker light switch** (86 × 86)
  centred y = 2340, z = 1250.
- y 2438 → 3420: hall door set (§2.1).

### 4.5 Nook wall (y = 3420) — from the door-wall corner (x = 0) toward the back door

Viewpoint: facing the nook wall (+Y); left = hall door, right = back door.

- x 0 → 120: plain pier (the hall-door architrave is on the adjacent wall).
- **Bar nook**, x = 120 → 1370, recess 520 deep, white plastered side reveals.
  - Base: three framed doors filling the width, faces 10 behind the wall face: 300 (x 120 → 420,
    hinged −X, T-bar on +X edge), 350 (420 → 770, hinged −X, T-bar on +X edge), 600
    (770 → 1370, hinged +X, T-bar on −X edge). Plinth 150.
  - Worktop: same white veined quartz, 30 thick, top z = 910, 520 deep, front edge 15 behind the
    wall face, scribed to both reveals.
  - Back wall and both reveals tiled (§3.4) from 910 to 1464.
  - **Two clear toughened-glass shelves**, 10 thick with polished green-tinted edges, full width
    1250 × 300 deep, top faces at **z = 1474 and z = 1652**, carried on small satin-chrome
    clamp brackets: two on each side reveal and three along the back wall per shelf.
  - Back wall above the lower shelf (z 1474 → 2030): full-width plain silver **mirror**.
  - Top: black (cabinet navy) **soffit board** at z = 2030 spanning the recess, with a black
    **cornice** on its front edge, z 2030 → 2130, x = 90 → 1400 (30 past each reveal, mitred
    returns back to the wall), projecting 70 from the wall face. Profile bottom to top: 30 flat
    fascia, 8 bead, 40 cove/ogee sweeping out, 12 fillet, 10 top cap.
  - **Stemware rack**: polished-brass wire rack screwed under the soffit, x 330 → 1300,
    two rows deep (≈ 300), 9 slots across at ≈ 105 centres; each slot is a pair of 5 mm wires
    hanging 55 below the soffit with flared ends. ≈ 14 wine glasses hang bowl-down.
- Pier x = 1370 → 1990: peacock relief plaque and thermostat (§6); **aluminium chequer-plate
  (5-bar tread plate) panel** 540 w × 265 h fixed flat to the wall, x 1410 → 1950,
  z 520 → 785, sampled #847f6c → neutral **#9c9c98** metallic, roughness 0.35; skirting below.
- x 1990 → 2960: back-door reveal and door set (§2.2). x 2960 → 3050: 90 mm return to the corner.

### 4.6 Switches, sockets, services

All white moulded plastic, 86 high.

| Item | Wall | Position |
|---|---|---|
| Light switch, 1-gang rocker | door wall | y 2340, z 1250 |
| Double socket (switched) | hob wall, on tiles | centre y 560, z 1130 |
| Double socket (switched) | sink wall, on tiles | centre x 2700, z 1130 |
| Small 1-gang fused switch | sink wall, on tiles | x 2900, z 1130 |
| Room thermostat, white 86 × 86 × 25, rounded | nook wall pier | x 1700, z 1430 |
| Smoke/heat alarm, white Ø 110 × 45 | ceiling | x 1500, y 2200 |

No radiator in this room.

## 5. Furniture

There is **no loose furniture** to model in the kitchen — it is entirely fitted, apart from the
two owner-named pedal bins in §6. (A black two-step folding stool and a black folding step-ladder
are present in the video and are on the declutter list.) The clear floor is an L: a ≈ 1830-wide zone between the nook
wall and the fridge/tower fronts, and a ≈ 1830 × 2200 zone between the hob run, sink run and
the tower.

## 6. Soft furnishings & decor

| Item | Wall / place | Position (local) | Size (W × H) | Description | Texture source |
|---|---|---|---|---|---|
| **Peacock relief plaque** | nook wall pier | centre x 1640, z 1920 | 440 × 590, ≈ 35 relief | One-piece cast plaque in antique bronze-brown. Wavy scalloped "cartouche" outline with scrolled corners and a raised rolled border; inside, in high relief, a **peacock perched facing right, head turned back, long tail sweeping down to the lower left with overlapping eyed feathers**, surrounded by open roses and leaves and a few beaded dots. Sampled #5f5441 → neutral **#5c4b3a**, low-sheen metallic (metallic 0.6, roughness 0.5), darker in the recesses. | **f_0332**, quad TL (268,478) TR (497,478) BR (497,778) BL (268,778) in the 720×1280 frame (full-res: t = 331 s, multiply by 1.5). Use as albedo + derive a height/bump map; cut to the scalloped outline. Alt: f_0766 (460,318)–(605,525). |
| **Glass memo board** | hob wall, in the clear zone H0 | y 3350 → 2550, z 950 → 1950 | 800 × 1000, 5 thick | Frameless frosted pale-green/white glass board on 4 satin-chrome stand-off buttons 30 in from the corners; stands 15 off the wall. Sampled #c0c2b4 → neutral **#dfe6e0**, slight translucency, glossy. **Render it blank** — the hand-written meal planner must not be reproduced (privacy rule). A small black magnetic eraser 60 × 30 at the top right is optional. | none (do not crop) |
| Hanging stemware | nook, under soffit | see §4.5 | — | ≈ 14 clear wine glasses and 2 martini glasses hanging bowl-down in two rows. | — |
| **Shelf mugs and glassware** (owner: "lots of wine glasses, mugs" — required) | nook glass shelves | — | — | Upper shelf: a row of clear tumblers/tankards and three small blue-and-white patterned tea canisters at the +X end; a chrome cocktail shaker and a silver teapot at the −X end. **Lower shelf: ≈ 6 mugs (two lime-yellow, the rest white) plus ≈ 8 clear glass tankards** (f_0311, f_0314). No branded bottles. | — |
| **Stainless pedal bin** (owner: "there's a rubbish bin") | door wall, between the fridge housing and the hall door | centre (150, 2330) | 300 × 400 plan × 650 high | Rectangular brushed-stainless pedal bin, flat lid, black pedal bar at the foot (f_0385). Simple prop on a viewer toggle, default on. | — |
| **Black pedal bin** (owner: "another rubbish bin here") | against the nook-wall pier between the nook and the back door | centre ≈ (1680, 3250) | 330 × 400 plan × 620 high | Matt-black plastic pedal bin, slightly domed lid (f_0766, f_0756). Simple prop on the same toggle, default on. | — |
| White plates | plate rack T3 | — | Ø 270 | 10 plain white rimmed dinner plates on edge + 1 larger Ø 300 at the −X end. | — |
| Wine bottles | wine rack T4 | — | — | 5–6 dark-green bottles lying neck-out in random cells (foil caps: green, silver, one natural cork). | — |

No curtains, blinds, shutters, rugs, framed paintings, mirrors (other than the nook back-mirror)
or plants in this room. The door mat by the back door is excluded (§8).

## 7. Lighting

| Fitting | Position (local) | Details |
|---|---|---|
| **Recessed ceiling downlights × 4** | (x, y) = (1050, 950), (2150, 950), (1050, 2450), (2150, 2450) | Round white-bezel LED downlights, Ø 90 visible, flush, slightly frosted lens. Warm white **≈ 3000 K**, ≈ 600 lm each, 60° beam. They are the main light and blow out to white in the video. |
| **Under-cabinet LED strip** | under all wall units, behind the 35 pelmet, 40 back from the front edge | Continuous linear LED: hob wall under W1 (y 2508 → 1908) and under W2 (y 830 → 320); sink wall x 2730 → 325 unbroken (passes under the plate rack and wine rack); door-wall corner cupboard y 320 → 600. Neutral-cool white **≈ 4000 K**, strong — it makes a bright even band on the grey tiles and the worktop and is the dominant visual accent. |
| **Hood spotlights × 2** | in the hood underside, y = 1590 and y = 990, x ≈ 2850, z = 1545 | Ø 55 recessed LED spots, ≈ 3000 K, aimed down at the hob. |
| Nook shelf light (weak) | back of the nook under the upper glass shelf | Thin warm LED bar ≈ 600 long, visible as a bright line in f313; optional. |
| Appliance displays | oven tower | Small emissive details: white/blue digits on the compact-oven band; a round red/pink dot display on the main-oven band. Optional. |

Mood: bright, clean, slightly warm overall; darkest element is the cabinetry, so give the room
enough fill that the navy reads as navy-black rather than pure black.

## 8. Declutter list (deliberately excluded)

- Everything stuck on the fridge (magnets, photos, cards) and the drink cans on top of it —
  fridge doors are modelled plain (privacy rule).
- Hand-writing on the glass memo board (board kept, blank).
- All worktop clutter: spice rack and jars, knife block, chopping board and cleaver, pans and
  food on the hob, utensil pot, pressure cooker, blender, coffee grinder, espresso machine, juicer,
  dish rack, kettle, water bottles, soap/washing-up bottles, sponges, cloths, oven gloves, bread
  maker, toaster, soda maker, snack packets, foil/film dispenser on the nook tiles, cork trivet.
- Tea towel hanging on the oven handle.
- Black folding two-step stool in the middle of the floor; black folding step-ladder leaning at
  the hob-wall cabinet end. (The two pedal bins are owner-named and kept — §6.)
- Grey/black speckled door mat inside the back door (≈ 500 × 800).
- Stickers/energy labels on the oven doors and hob.
- Reflections of the person filming in the nook mirror and back-door glass.
- Condiment bottles and miscellaneous small ornaments on the nook's upper shelf (replace with
  the light glassware set in §6).

## 9. Reference frames

Camera positions are local (x, y) in mm, eye height ≈ 1450–1550; "looking" is the local direction.

| Frame | Shows | Camera roughly at / looking |
|---|---|---|
| f_0755 / f_0293 | First view through the hall door: nook on the left, memo board, W1, hood and hob run straight ahead, fridge side on the right | in the hall at (−600, 2950), looking +X |
| f_0756 | Nook in steep perspective, back-door corner, memo board, W1 + hood, two downlights, smoke alarm | (300, 2900), looking +X and slightly +Y |
| f_0758 | Hob wall elevation: clear zone with memo board, W1, hood + chimney, base units H2–H4, skirting, cornice | (900, 2600), looking +X |
| f_0348 | Near-frontal close elevation of W1, hood, base H2–H4 (best for door/drawer proportions, tile bond) | (950, 2150), looking +X |
| f_0760 | Hob, hood from the side, W2 and the hob-wall/sink-wall corner, corner knob doors | (1500, 2300), looking +X/−Y |
| f_0378 / f_0762 | Sink wall: T2, plate rack + flap, wine rack, T5, sink and taps, tower edge on the right | (1700, 2300), looking −Y |
| f_0385 | Door wall: oven tower, fridge-freezer in its housing with bridging flap door, wall strip and hall door on the right | (2300, 1700), looking −X |
| f_0396 / f_0404 | Oven tower stack close-up (oak filler strip, compact oven, main oven), blind-corner worktop | (1500, 700), looking −X |
| f_0402 | Nook wall from across the room with ceiling, cornice, downlight, plaque, chequer plate | (1900, 500), looking +Y/−X |
| f_0766 | Best elevation of the nook wall: nook base doors, shelves, black cornice + brass rack, plaque, thermostat, chequer plate, back door edge | (1500, 1700), looking +Y |
| f_0330 / f_0364 | Back door with toplight and cat flap, memo board beside it, W1 from below | (1700, 2500) looking +Y/+X; (2300, 1500) looking +Y |
| f_0388 / f_0437 | Looking back at the hall door from inside: glazed oak door open into the hall, threshold bar, floor plank direction, nook base units | (1800, 2800) looking −X; (700, 2900) looking −X |

## 10. Uncertainties

1. **Overall size** (3050 × 3420) is built from cabinet-module arithmetic that closes on all four
   walls to within ≈ 50 mm, but individual modules could be the next size up/down; expect
   ±150 mm on each room dimension. If `spec/house.json` fixes the kitchen footprint differently,
   keep the module widths and absorb the difference in the hob-wall clear zone H0 (y) and in the
   pier between nook and back door (x).
2. **Ceiling height 2950** (range 2800–3000). Wall-unit heights (900 doors, pelmet underside
   1420, cornice top 2400, tall units 2480) carry ±60: the phone was pitched in every elevation
   shot, so vertical scales are keystone-distorted; frontal f348 alone would suggest 1000-high
   wall doors.
3. **What is behind the back door**: assumed outdoors (side-return yard) because it is a
   weatherproof uPVC door with cat flap and toplight and the glass is black at night; it was never
   opened in the video. The utility-room frames show no matching door, which supports this.
4. **Nook depth** (520) and whether its base units are full 600-deep carcasses — not directly
   visible; shelf depth 300 and the appliances standing on the worktop suggest 450–600.
5. **Nook base door widths** (300 / 350 / 600): the third door is clearly about twice the others;
   exact split of the first two is a guess.
6. **Lower appliance in the oven tower** (z 150 → 550): black glass front with stainless trim —
   could be a warming drawer + storage drawer, or a second compact oven. Modelled as one
   drop-front.
7. **Hob-wall corner units** (H5 knob door 270, W2 pair of ≈ 245 doors): seen only obliquely;
   W2 could be a 300 single unit plus the 300 leaf of an L-corner bifold. Hood width 900 vs 800 is
   also not certain (hob is a 750 model either way).
8. **Downlight count/positions**: four are certain in a 2 × 2 pattern; a fifth/sixth nearer the
   hall door cannot be ruled out. Smoke-alarm position ±300.
9. **Socket positions** on the tiles are approximate (partly hidden by countertop appliances); a
   small white plate on the back-door reveal / NE corner at z ≈ 1300 seen in f757 was left out.
10. **Hall-door light sizes and rail positions** are estimated from oblique, motion-blurred frames
    (f292, f304–f308); the door type (2 frosted lights over 2 raised panels, brass lever on
    backplate, opening into the hall, hinged on the rear-side jamb) is certain.
11. **Cabinet colour**: reads near-neutral black in most frames (#272526) and blue-black where well
    lit (#3e3e40, #424143). The brief calls it navy/black; estimate #23252d. If the owner names a
    paint, use that.
12. **Tile size**: 100 mm courses are solid (5 courses under the wall units); the 300 length is
    from visual 3:1 proportion and could be 100 × 250.
13. Floor plank module (≈ 200 × 1200) ±30 on width; laying direction (long axis parallel to the
    door wall) is certain.

---

## Reconciled dimensions (from `spec/house.json`, see `spec/RECONCILE.md` D6, D13)
- Global rectangle: x 1.25..4.30, y 5.31..8.73 (3.05 x 3.42, exactly as measured here). Ceiling 2.95.
- Local to global: X = 1.25 + x/1000, Y = 5.31 + y/1000. No scaling; every module stays as specified.
- Bar nook: x 1.37..2.62, y 8.73..9.25. Hall door centre (1.12, 8.24) in a 0.26 m wall. Back door centre
  (3.725, 8.88) in the 0.30 m external wall; it opens onto the side return east of the flank wall.
- Behind the sink wall is a 0.58 m unseen zone, then the living room. Behind the door wall are the stairs
  (y < 7.58) and the lobby.

## Round 3 corrections (core owner, from build/rooms2_open.md)
- 2.2 Back door: the frame is built 0.84 wide at x 3.40..4.24 (the house.json notes said 0.86 at 3.37..4.23; outside,
  its west edge is on the flank-wall corner, x 3.40) in a reveal x 3.39..4.25; the leaf is 0.744. Obscure glass in
  the leaf's upper light and the toplight (corrections K5; v6 f_0073, v2 f_0366). The nook-wall pier stays about 0.77
  wide (the frames suggest 0.58-0.62): a reveal starting at x 3.24 would put the door into the flank wall outside.
- 3.2 The nook-wall skirting runs to the back-door reveal and returns into it along x 3.39.
- 6 The plaque centre is about 70 mm right of the pier centre (v1 f_0766, v6 f_0073); the nook-pier socket is a DOUBLE
  switched socket under the left part of the tread plate, behind the black bin (v2 f_0434, v7 f_0039-0041), not the
  single at 0.60 (that is the cat flap); the tread plate is 0.54 wide, centred on the pier.

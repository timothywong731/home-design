# Round 3 survey — rear garden, shed, rear elevation, balcony

Surveyor notes for the area "garden". Footage read: v13 f_0190–f_0225 (all), v11 f_0044–f_0060 and
f_0154–f_0196 (all), v13 f_0020–f_0049 (passage end only), and for cross-checks v2 f_0147–f_0170 and the
phase-2 stills `v2_t246`, `v2_t250`, `v2_t274`, `v2_t276`. Present model looked at: `spec/house.json`,
`spec/rooms/garden.md`, `shed.md`, `balcony.md`, `spec/phase2/rear_elevation.md`, `spec/plan_site.png` and
previews `build/preview/*_r3garden.jpg` (garden, shed, elev:rear, plan:X; foundation + garden, shed, balcony).

Scratch (not tracked): stills, gridded crops and overlays in `reference/work/r3_garden/`
(`v13_tNNN.jpg` = v13 at t = NNN s = frame f_(NNN+1); `v11_tNNN.jpg`, `v2_tNNN.jpg` likewise;
`snap_216*.jpg`, `snap_214_c.jpg`, `snap_221_c.jpg` show the measured lines); solver scripts in
`build/r3/garden/` (`stage.py`, `stage2.py`, `stage4.py`, `snap.py`, `manhattan.py`, `lines_t216.py`, …).

## 0. Headline

**The rear plot is about 1.1–1.8 m longer than modelled.** Phase 2 scaled everything north of the house from
one oblique frame with an unknown focal length (its own doubt D4) and took the shed French doors as 1.20 x 2.08.
The 21 Nov top-down views from the second-floor rear window (v13 f_0213–f_0225) give a calibrated plan:

| line (world y) | house.json now | measured | shift |
|---|---|---|---|
| deck north edge (main deck) | 20.50 | **21.40** ± 0.12 | +0.90 |
| deck step outer edge = lawn south edge | 20.80 | **21.70** ± 0.12 | +0.90 |
| fire pit centre | 22.26 | **23.45** ± 0.15 | +1.19 |
| veranda front edge = lawn north edge | 23.40 | **25.02** ± 0.18 | +1.62 |
| shed front wall, outer face | 25.00 | **26.70** ± 0.20 | +1.70 |
| shed rear wall, outer face | 28.90 | **30.75** ± 0.35 | +1.85 |

Widths barely change (the plot is 5.3–5.5 wide). The shed's openings and heights are also larger than modelled
(door 1.69 x 2.33, window 1.85 x 1.10, soffit 2.44 above the paving). No pergola exists: the "pergola" in the
v13 overview is the balcony rail seen from above.

## 1. How it was measured

### 1.1 Camera model for the top-down stills
Stills v13 t = 216 s (frame A, f_0217), t = 214 s (frame B, f_0215), t = 221 s (frame D, rolled 90 degrees),
1080 x 1920, pinhole, principal point at the image centre.

- **Rotation**: vertical vanishing point from ~190 automatic line segments on the east fence boards (nadir pixel
  (526, 1481) in A; the two balcony corner posts give (502, 1497), the shed door jamb agrees), plus hand-picked,
  edge-snapped house-aligned lines (balcony platform edges and rails, deck boards, deck edges).
- **Focal length**: f = 890 ± 30 px. Evidence: Manhattan self-calibration of the rolled frames t = 220–223 gives
  853–918; the house-aligned Y lines of frame A fit best at 900–940; the camera must be above the window board
  (Z 6.70) and 0.6 m above the conduit, which needs f ≥ 880; balcony rail height 1.10 and projection 1.05 want
  865–880. Far-field results move by less than 0.11 m over f = 860…920 (table in 1.3).
- **Position and scale**: fire pit top course as a 1.00 m square (9 headers), rear wall face y = 17.36 at the
  balcony platform / door cill junction, deck east edge x = 3.40 (flush with the flank wall), levels from
  house.json (deck −0.05, lawn −0.45, veranda −0.42, balcony 3.00). Result for A: camera (1.62, 17.54, 6.85),
  reprojection rms 2.1 px; B: (1.71, 17.52, 6.73), rms 1.9 px. A and B agree to 0.02 m on the deck edge and the
  fire pit y, 0.09 m on the fire pit x, 0.08 m on the shed door plane.
- Check of the registration: the wall lantern comes out at x 2.31 (house.json 2.33); the balcony door centre at
  1.27–1.30 (house.json 1.29).

### 1.2 Scale: five independent references
The fire pit alone is not a safe ruler (phase 2 used it too), so the scale was tested against everything else
that has a known size. All lengths below are what the pit-scaled camera gives:

| reference | measured with pit = 1.00 | expected | ratio |
|---|---|---|---|
| east fence bays between concrete posts (A, three bays) | 1.83 (shed–P1), 1.84, 1.77 | 1.83 panel + slot web ≈ 1.86 | 0.98 |
| east fence height above the path (three posts) | 1.93–1.96 | 1.83 board + 0.15 gravel board = 1.98 | 0.98 |
| deck board pitch (gap profile along x = 380, 450 in A: 14.7 px) | 0.145 | 140 board + 5 gap | 1.00 |
| veranda soldier-course pavers (FFT period 8.5–8.7 px along the front edge, A and t = 216.5) | 0.1006 | 100 + joint | 0.99 |
| camera height above the study window board (6.70) | 6.85 / 6.73 | just above the board | ok |
| shed door from brick courses (see 1.4) | 1.62–1.67 wide | 1.69–1.71 | 0.97 |

So the scale is right to about **± 3 %**, if anything 2 % small. The deck depth also closes by count: 28 boards
x 0.145 = 4.06 m against 4.04 m measured (v2 f_0154: 22 gaps visible to the far edge, 4 hidden behind the hand
and door, 2–4 under the camera).

Why phase 2 came out short: its shed door was assumed 1.20 x 2.08 (a standard leaf); the door is in fact
1.69 x 2.33, so everything scaled from the shed front was 0.72–0.89 of true, and the two trellis panels on the
neighbour's wall were taken as 0.9 wide where they are standard 1.83 m panels.

### 1.3 Sensitivity to the focal length (frame A)

| f | camera Z | deck step outer edge y | fire pit y | veranda edge y | shed door plane y | balcony W x D, rail |
|---|---|---|---|---|---|---|
| 860 | 6.46 | 21.58 | 23.33 | 24.94 | 26.72 | 1.92 x 1.04, 1.07 |
| **890** | 6.85 | 21.69 | 23.44 | 25.01 | 26.72 | 2.07 x 1.14, 1.18 |
| 920 | 7.24 | 21.79 | 23.53 | 25.07 | 26.73 | 2.21 x 1.22, 1.29 |

Near-field sizes (the balcony) depend on f, far-field positions hardly at all.

### 1.4 Shed front from the ground (v11 f_0055, frontal, 10 m away; v2 t = 274 close-up)
- v2 t274: bed joints located by intensity profile beside the window's right jamb (pitch 38→57 px): the window
  frame is **14.8 courses** = 1.11 m high (15.4 with the cill).
- v11 t54 (edges read at 4.2x): window frame 77.9 px high → 70–73 px/m in the wall plane. Door frame 167.9 px
  high, 122.6 px wide → **2.33 ± 0.05 high x 1.70 ± 0.04 wide** (31 courses x 7.5 bricks). Handles 1.11 above the
  threshold. Window 134.6 px → 1.85 ± 0.06 wide; its frame bottom is 1.19 above the paving, head 0.06 below the
  door head. Brick between window and door 32 px = 0.45 (two stretchers, also seen in v2 t274). Course pitch
  by autocorrelation in v11 t194 is 8.9–10 px against a 272.6 px door: 27–31 courses, not decisive alone.
- Heights (camera 1.15 above ground floor, fascia 1.7 m nearer than the wall): fascia bottom Z 1.98, fascia
  top 2.20, gutter rim 2.29; the pier caps / coping stand 0.35–0.40 above the gutter (v11 t194) → 2.70. The
  top-down views agree: the coping ends land on the front line y 25.0 only for Z 2.65–2.75, the gutter for
  Z 2.2–2.3.

## 2. Dimension table

Tolerances are 1 sigma of my estimate; "conf" = confidence that the proposed value is better than the present one.

| # | item | where in house.json | present | measured | method | conf |
|---|---|---|---|---|---|---|
| 1 | deck north edge | exterior.zones.deck polygon | y 20.50 | 21.40 ± 0.12 | A, B top-down; board count 28 x 0.145 | high |
| 2 | deck / plot west edge beside the deck | zones.deck, boundaries.west_neighbour_wall | x −0.75 | −0.88 ± 0.08 | wall coping edge at Z 2.95 and fence top, A | medium |
| 3 | deck north step | zones.deck_step_n | x −0.55..2.45, y 20.50..20.80 | x −0.30..2.75, y 21.40..21.70, Z −0.25 | A (visible tread 18 px = 0.30 − occlusion), v2 t250 for the ends | medium |
| 4 | lawn | zones.lawn | x −0.27..3.28, y 20.80..23.40 | x −0.36..3.15/3.28, y 21.70..25.02 | A, B | high (y), medium (x) |
| 5 | lavender bed | zones.lavender_bed | x −0.75..−0.27, y 20.50..23.40 | x −0.88..−0.36, y 21.40..25.02 | A | medium |
| 6 | fire pit | features.fire_pit.center / size | (1.27, 22.26), 1.01 | (1.30 ± 0.08, 23.45 ± 0.15), 1.00 | A (1.26, 23.44), B (1.35, 23.46) | high |
| 7 | garden path | zones.garden_path | y 17.55..23.40 | y 17.95..25.02; west edge x 3.40 (deck) then 3.15 → 3.28 | A | high (y) |
| 8 | passage step and drain | steps.passage_step.line, zones.side_passage | y 17.55 | 17.95 ± 0.10 (drain 17.95..18.08) | drain ends in A: (3.71, 18.00), (4.69, 17.91) | medium |
| 9 | east fence | boundaries.east_fence.line | (4.90, 9.88) → (4.45, 23.40) | → (4.42, 25.02); posts (4.73, 18.18) (4.62, 19.57) (4.58, 21.34) (4.48, 23.17) | A; four bays between the step and the shed (also v13 t212.5) | high (length) |
| 10 | east fence height | boundaries.east_fence.height | 2.0 on base −0.30 | top Z 1.50 ± 0.05 beside the garden (1.95 above the path) | post top / foot parallax, A | low — leave |
| 11 | neighbour's extension wall | boundaries.west_neighbour_wall.line | y 17.36..19.65 | y 17.36..21.40 ± 0.15, face x −0.88, top Z 2.95 | A (coping north end), two 1.83 trellis panels fit | high |
| 12 | west fence | boundaries.west_fence.line | y 19.65..23.40 | y 21.40..25.02, x −0.90 ± 0.08, top Z 1.35 (1.80 above the lawn) | A; two bays | high (y) |
| 13 | veranda | zones.shed_veranda | x −0.35..4.22, y 23.40..25.00 | x 0.06..4.22, y 25.02..26.70 (1.68 deep) | A, B, D | high (y), medium (x) |
| 14 | shed front wall | buildings.shed.walls.shed_w_front | centre y 25.14 | 26.84 (outer face 26.70 ± 0.20) | door threshold in A 26.72, B 26.80, D 26.77 | high |
| 15 | shed rear | buildings.shed.outline, shed_w_rear | y 28.90 (centre 28.76) | 30.75 ± 0.35 (centre 30.61) | coping corners in A at Z 2.70 (30.69 / 30.82) | medium |
| 16 | shed width | buildings.shed.outline | x −0.87..4.45 | −0.95..4.47 ± 0.10 | coping corners, gutter ends, fence lines | low — optional |
| 17 | shed French doors | buildings.shed.openings.shed_d1 | 1.20 x 2.08, centre x 3.35 | 1.69 x 2.33, centre x 3.33 | 1.4; top-down 1.62–1.67 | high |
| 18 | shed front window | buildings.shed.openings.shed_w1 | 1.30 x 1.00, sill 1.05, centre x 1.80 | 1.85 x 1.10, sill 1.19, centre x 1.10 | 1.4 | high (size), medium (x) |
| 19 | veranda soffit | buildings.shed.roof.verandaSoffitZ | 1.83 | 2.02 ± 0.06 (2.44 above the paving; door head 1.91, fascia bottom 1.98) | 1.4 | medium |
| 20 | shed roof | buildings.shed.roof.topZ, walls height | 2.25 / 2.67 | felt 2.30 at the gutter rising to ~2.50; coping top 2.70 ± 0.08; walls 3.12 above the paving | 1.4 + top-down | medium |
| 21 | store cupboard | buildings.shed.walls.shed_w_store, rooms.shed_store | door plane x −0.36; room y 23.75..24.98 | door plane x 0.06 ± 0.10; room x −0.68..0.04, y 25.35..26.68 | pier base corner in A (0.05), D (0.12–0.26); v11 t194: 1.1 m from the downpipe corner to the door plane | medium |
| 22 | balcony platform | rooms.balcony.polygon, features.balcony_structure.polygon | x 0.00..2.30, y 17.36..18.41 | x 0.22..2.34 (± 0.12), y 17.36..18.48 (± 0.07) | A: 0.22..2.29 x 1.14; B: 0.30..2.30 x 1.11; centred on the doors | medium-low |
| 23 | balcony rail height | features.balcony_structure.railing.height | 1.10 | 1.14–1.18 at f 890 (1.07 at 860) | A, B | keep 1.10 |
| 24 | trellis panels | features.trellis_panels | 2 x 0.90 wide from y 17.85 | 2 x 1.83 wide, y 17.65..21.31, arch top 1.50 above the deck, shoulders 1.25 | ~10 diamonds per panel, width : height 1.9 in v11 t188, wall length | high |
| 25 | trough planter | features.planters.trough_planter | y 18.20..20.05 | y 18.85..20.80 (ends at the square planter 20.82..21.26) | position from the square planter in A; length not re-measured | low |
| 26 | deck side step box | zones.deck_step_e | y 17.75..18.65 | y 18.08..18.98 (starts at the drain) | drain position in A, v11 f_0192–f_0194 | medium-low |
| 27 | study window lower lights | openings.w_study.sashes | lower_w / lower_e side_hung | both lower lights **top-hung**, opening outward on stays to ~40 degrees, brass handle on the bottom rail | v13 f_0197–f_0212 | high |
| 28 | plot / site extent | exterior.plot.polygon, siteBounds.maxY | to y 28.90 | to y 30.75; siteBounds.maxY 31.0 | follows 15 | medium |

Confirmed, no change: rear wall face y 17.36 and flank x 3.40 (used as gauge; lantern and door centre agree),
fire pit size 1.00 (9 headers, wall 0.215), west fence height 1.8, levels of deck / path / lawn / veranda (no
new evidence against them: the deck fascia still shows three boards to the path, the step tread hides exactly
what a 0.20 drop predicts), French doors, side windows, lantern x 2.33, second-floor window position.

### Knock-on effects
- Nothing has to give way: the plot is open to the north. Everything north of y 20.5 slides north (fire pit,
  bird feeder, veranda furniture, shed, workshop interior, plot polygon, `siteBounds.maxY`, site plan sheet
  extents, backdrop behind the shed).
- The neighbour's single-storey extension (west) now runs 4.04 m beyond our rear wall, not 2.3 (notes of
  `exterior.neighbours[west]` and its massing part); its flat roof carries a glazed roof lantern and its north
  end wall has a wide dark-framed window (backdrop only).
- The east neighbour's massing stops at y 17.0 and is not affected.
- `blender/rooms/garden.py` (2), `shed.py` (6) and `shed_workshop.py` (1) contain literal 23.4 / 28.9 / 20.5
  style coordinates: they must read the zones / building from the spec.
- The side passage zone grows 0.40 north (y 17.95); the hose reel, tap and plinth positions on the flank wall
  are not affected (they are keyed to the wall).

## 3. Inventory — what the footage shows that the model lacks or has wrong

Coordinates are world (x east, y into the garden, z up); sizes L x W x H.

### 3.1 Deck (unit garden)
| what | where / size | colour | frames |
|---|---|---|---|
| Deck 4.28 x 4.04, boards E–W, **28 boards at 0.145 pitch** (140 mm board, 5 mm gap), brushed wood-grain face, no deep reeding | x −0.88..3.40, y 17.36..21.40, Z −0.05 | sampled dry in sun #93929A–#A79F98, wet (v2) #614E40; estimate **#776860** weathered grey-brown (the model's #6B5645 is a little dark and red) | v11 f_0188–f_0195, v13 f_0213–f_0218 |
| North step: box tread two boards deep | x −0.30..2.75, y 21.40..21.70, Z −0.25; the eastern 0.65 m of the deck edge has no step (the terracotta pot and square planter stand above it) | as fascia | v2 t250, v13 f_0217 |
| Fascias (north 3 boards, east 3 boards to the path / 2 to the passage) | — | sampled #5F5A57, estimate **#554A44** | v11 f_0194 |
| **West planter**: one long slatted trough along the neighbour's wall under the trellis | x −0.86..−0.44, y 17.65..20.50, H 0.42 | sampled #8C765D, estimate **#7A6650** mid brown (lighter than the east planters); geraniums (red) at the south end, low green foliage | v11 f_0188–f_0190, v2 f_0154 |
| **Trellis panels x 2**, framed diamond lattice with a convex arched top | each 1.83 wide; y 17.65..19.48 and 19.48..21.31 at x −0.87; top of arch 1.50, shoulders 1.25 above the deck (panel 1.2 / 0.95 standing on the planter rim); ~10 diamonds across, laths 30 x 8 | sampled #7E6851, estimate **#6E5A44** | v11 f_0188–f_0190, v2 f_0154 |
| NW corner box planter (bare soil, a timber corner post) | x −0.85..−0.30, y 20.55..21.40, H 0.45 | dark brown | v13 f_0215–f_0217 |
| Cream stone-effect urn pot with lavender / thyme, and a potted standard shrub beside it | urn Ø 0.40 x 0.35 at (−0.05, 21.15); shrub pot at (−0.45, 20.45) | urn sampled #D0C2A3 | v11 f_0188, v13 f_0217 |
| Folding recliner chairs x 2, blue fabric on grey tube | (0.25, 18.9) and (0.25, 19.7), backs to the trellis | #5E7FA8 | v11 f_0188–f_0190 |
| **Trough planter** on four feet with black liner | x 2.95..3.37, y 18.85..20.80, H 0.45 (length to be checked, see 6) | sampled #584B46, estimate **#5A4A40** | v11 f_0194–f_0196 |
| Square planter with a small olive tree | x 2.93..3.37, y 20.82..21.26, H 0.50 | as trough | v11 f_0194, v13 f_0217 |
| Terracotta pot with a bare sapling | Ø 0.38 at (2.65, 21.10) | terracotta | v13 f_0217 |
| Black glazed pot with rosemary | Ø 0.30 at (2.75, 18.65) | #1E1E20 | v11 f_0188, f_0194 |
| Pebble planter with wisteria (as modelled) | x 2.30..3.30, y 17.40..17.82 | cobbles cream / grey | v11 f_0190–f_0192 |
| Side step box, weathered | x 3.40..3.75, y 18.08..18.98, top Z −0.25 | sampled #777575, estimate **#6E6862** grey-weathered | v11 f_0187, f_0193–f_0196 |

### 3.2 Lawn, path, boundaries (unit garden; ground and fences are the site unit)
| what | where / size | colour | frames |
|---|---|---|---|
| Lawn 3.5 x 3.3 | x −0.36..3.15/3.28, y 21.70..25.02 | sampled #656F47, estimate #6E8B4F | v13 f_0213–f_0225 |
| Fire pit, 3 courses, top course 9 headers per side, thin joints | centre (1.30, 23.45), 1.00 x 1.00, wall 0.215, H 0.20–0.225 | top sampled #C3B585, estimate #B79A6A | v13 f_0217, v2 t246 |
| Lavender hedge | x −0.88..−0.36, y 21.40..25.02 | sampled #999785 grey-green | v13 f_0217 |
| Bird-feeding station (optional) | pole at (3.19, 21.76) on the lawn's SE corner | black | v13 f_0217, v11 f_0194 |
| Path, grey sandstone flags in random courses | y 17.95..25.02 between the deck / lawn and the fence, 1.15–1.40 wide | sampled #B2B5BB / #9F9E9A, estimate #A3A4A6 | v11 f_0187, f_0194–f_0196 |
| Channel drain at the foot of the passage step | y 17.95..18.08, x 3.71..4.69 | black | v11 f_0191–f_0193 |
| **East fence**: feather-edge boards on our side, slotted concrete posts and gravel boards, **painted mid warm grey**; lattice topper on the neighbour's side only | posts as table row 9; top Z 1.50 beside the garden | sampled #858281–#9F9A95, estimate **#9A9590** (the present #BDB9B3 is too pale); posts and gravel boards concrete #A8A49C | v11 f_0059–f_0060, f_0187, f_0196, v13 f_0213–f_0217 |
| Passion-flower strands on the fence, a white cylindrical solar light on the post at the step (optional) | (4.73, 18.2), top 2.2 above the path | — | v11 f_0056–f_0060 |
| **West fence**: closeboard, three arris rails and the posts on our side, two bays | x −0.90, y 21.40..25.02, 1.80 high | sunlit #C8BFA4, overcast #A99A88; estimate **#B3A58C** pale weathered softwood (the model's dark brown #8A735C is wrong) | v11 f_0188, f_0195, v2 t246 |
| Neighbour's extension wall, stone coping 0.30 wide on top | x −0.88, y 17.36..21.40, top Z 2.95 | brick sampled #CDBD97, estimate #C2AE85; coping #B5B0A3 | v11 f_0188–f_0189, v13 f_0218–f_0225 |

### 3.3 Shed (units shed, site)
| what | where / size | colour | frames |
|---|---|---|---|
| Building outline | x −0.95..4.47, y 25.02..30.75 | brick #A8624A (shade sample #7C5948), mortar buff | v13 f_0211–f_0225, v11 f_0054–f_0060, f_0194–f_0196 |
| **Roof**: grey mineral felt falling to the front, with a pale concrete **coping 0.30 wide on the west, rear and east sides** (not only west and rear); the front ends of the side copings are the "pier caps"; leaf litter | coping top Z 2.70, felt 2.30 → 2.50 | felt #7D7E7A, coping #C9C5B8 | v13 f_0197, f_0211, f_0217, f_0221–f_0224 |
| White half-round gutter along the whole front, white round downpipe down the SW corner; white fascia 0.22 deep | gutter rim Z 2.29, fascia 1.98..2.20, y 25.0 | #F2F2F0 | v11 f_0194, v13 f_0217 |
| Soffit of stained T&G boards (as modelled) | Z 2.02 | #6A452C | v2 t274 |
| **French doors** much larger than modelled: white uPVC pair, each leaf one tall pane over one lower pane, mid-rail 0.93..1.06 above the threshold, brass lever handles at 1.11 | frame 1.69 x 2.33 at x 2.49..4.18 | white | v11 f_0055 (frontal), f_0194–f_0196, v2 t276 |
| **Window W1** wider and higher: two top-hung fanlights over one fixed pane | frame 1.85 x 1.10 at x 0.17..2.03, frame bottom 1.19 above the paving, white cill | white | v11 f_0055, v2 t274 |
| Brick between window and doors 0.45 (two stretchers) with the black doorbell at 1.25; 0.25 of brick east of the doors | — | — | v2 t274 |
| **Store cupboard block is 1.0 m wide**, not 0.5: its oxblood doors face east in the plane x 0.06, between the front pier (y 25.02..25.35) and the front wall | door pair 1.23 wide, y 25.40..26.63 | oxblood #7A3B2E | v11 f_0194–f_0196, v13 f_0217, f_0222 |
| Climber (wisteria) over the SW pier, the store roof edge and the west third of the fascia; bird box on the pier | — | yellow-green | v11 f_0194–f_0196 |
| Veranda paving: red block pavers, 45-degree herringbone with a **soldier course** along the front edge | x 0.06..4.22, y 25.02..26.70, Z −0.42 | #A8604E | v2 t246, v13 f_0217 |
| On the veranda: two folded teak chairs against the wall under the window (x 0.5..1.4), black pot (1.25, 25.8), two stone cat figures (1.75, 25.75), pine box (x 1.6..2.3, y 26.1..26.5), grey door mat 1.0 x 0.6 in front of the west leaf, softwood rack against the east wing wall (x 3.85..4.20, y 25.25..26.60) | — | — | v13 f_0215–f_0217 |
| Behind the shed (backdrop): a service yard and a three-storey yellow-brick block with a pitched tiled roof 20 m away, tall bamboo west of it, a large sycamore over the NE corner | — | — | v13 f_0196–f_0212, v11 f_0195 |

### 3.4 Balcony and rear elevation (units blue_ensuite, envelope, study)
| what | detail | frames |
|---|---|---|
| Platform | **chequer (durbar) plate** confirmed, screw-fixed along the edges with pale caps, 2.12 x 1.12, centred on the balcony doors; sunlit sample #727375, estimate **#3A3C40** | v13 f_0213–f_0218 |
| **Top rail and posts are round tube** (about 48 mm) with elbow and tee fittings and a visible joint collar, not a 60 x 40 box section; three posts on the front (two corners + middle), the side rails return to wall brackets | sampled #B2B1B7–#B7B8C1 from above (sky reflection); the bars and bottom rail read black. Estimate rail and posts **mid grey #6B7076**, bars #2A2C2E — see open question 3 | v13 f_0215–f_0217 |
| Infill bars | thin vertical bars; about 7 in the east half of the front and 6–7 on the east return, i.e. ~0.14 centres rather than 0.165 | v13 f_0217 |
| Planting | troughs along the front and the east side only (west side bare), variegated ivy covering the whole front rail and hanging outside; purple-blue flowers at the NE corner | v13 f_0213–f_0217 |
| Balcony doors | both **fanlights are top-hung openers** (open in v13 f_0213–f_0217), brass stay handles | v13 f_0215–f_0217 |
| Lantern | black four-sided coach lantern with a pagoda cap on the wall east of the doors, at x 2.31 | v13 f_0213–f_0217 |
| Conduits | two ribbed grey-black hoses with black saddle clips at ~0.9 m centres along the rear wall below the second-floor sill | v13 f_0213–f_0218 |
| Second-floor window (Rose Room) | four lights; the two **lower lights are top-hung** and open outward on friction stays (the owner opens both and holds the phone out under them); outer cill: white painted stone, weathered and lichen-stained; oak window board inside | v13 f_0197–f_0212 |

## 4. Per-unit notes

### garden
- Rebuild from the zones after the spec change; nothing is keyed to literal y values any more.
- Deck 28 boards at 0.145 E–W, colour #776860, fascia #554A44; north step x −0.30..2.75 only.
- West side: one long planter (x −0.86..−0.44, y 17.65..20.50, 0.42 high, #7A6650) with the two 1.83 m arched
  trellis panels standing on its rim against the wall (top of arch Z 1.45, shoulders Z 1.20); NW corner box
  planter, cream urn, potted shrub as 3.1.
- East side: black pot, trough (y 18.85..20.80), square planter with olive (20.82..21.26), terracotta pot.
- Fire pit centre (1.30, 23.45), 1.00 square, three courses, top course of 9 headers per side.
- Lavender hedge x −0.88..−0.36 from the deck to the shed pier; bird feeder at (3.19, 21.76).
- West fence colour #B3A58C with rails and posts on our side; east fence #9A9590, posts #A8A49C.

### shed
- Move with the building (+1.70 in y) and resize: French doors 1.69 x 2.33 (leaf 0.80; lower pane to 0.93,
  mid-rail 0.93..1.06, upper pane above; handles 1.11), window 1.85 x 1.10 with sill 1.19, veranda soffit 2.44
  above the paving, downlights with it.
- Store cupboard: doors in the plane x 0.06 facing east, y 25.40..26.63; the cupboard is 0.72 deep inside
  (x −0.68..0.04); shelves 0.40 deep stay on the west (back) wall.
- Veranda furniture positions as 3.3 (they were laid out for a 4.57 x 1.60 veranda; it is 4.16 x 1.68).
- Workshop interior: 4.88 wide x 3.49 deep (x −0.68..4.20, y 26.98..30.47); keep the layout, stretch the
  clearances; ceiling 2.45 above the floor is a guess (not filmed in round 3).

### site
- Zones, steps, boundaries as section 2. East fence: slotted concrete posts at the measured positions with
  1.83 m bays, gravel boards, top Z 1.50 beside the garden; west fence two bays from the wall end to the pier.
- Shed building: coping on three sides (0.30 wide, top Z 2.70), felt roof inside it falling to the front
  gutter; side copings end at the front as the pier caps (no separate taller piers).
- Passage step at y 17.95 with the channel drain 17.95..18.08 at its foot.

### envelope
- Balcony structure: round-tube top rail and posts with fittings, three front posts, chequer-plate deck with
  edge fixings; platform x 0.22..2.34, projection 1.12 (if accepted).
- Second-floor rear window: lower lights top-hung outward. Balcony door fanlights top-hung outward.

### blue_ensuite (balcony)
- Planters on the front and east rails only; ivy mass over the full front rail; deck colour #3A3C40.

### study (Rose Room)
- `w_study` lower lights are top-hung outward (handle on the bottom rail), not side-hung; oak window board.

### side_passage
- North end of the passage is the step at y 17.95, not 17.55; the fence at that point is at x 4.75.

## 5. What could not be settled
1. **Shed depth / rear wall** (30.75 ± 0.35): rests on the coping height (2.70) and on two frames in which the
   roof is near the image edge; frame D gives an inconsistent rear edge (28.6–30.2). The interior depth is as
   uncertain as before.
2. **Balcony width**: 2.0–2.2 from above (depends on f), 2.2–2.3 from the frontal v2 view including ivy.
   Proposed 2.12 centred on the doors; the west end is the uncertain one (0.0 or 0.22).
3. **Balcony rail colour**: from above the top rail and posts look mid grey, the bars black; a satin black tube
   reflecting the sky would look the same. Phase 2 sampled #505452 standing on it.
4. **Trough planter length** (1.85 in phase 2, possibly ~2.0): only its north end is visible from above.
5. **Store cupboard depth**: the 1.0 m block width is seen twice, but the doors themselves are under the
   climber in every round-3 frame.
6. **Scale** is good to ± 3 %; a tape measure on any one of: deck depth (4.04), a fence bay (1.83), the shed
   door (1.69 x 2.33) would remove it.
7. **Shed window x position** (centre 1.10 ± 0.10) and whether the brick between store and window is 0.10 or 0.20.
8. Levels were not re-measured (no new evidence); the deck-to-lawn drop could be 0.40–0.45.
9. The lawn's east edge is ragged (3.13 at the deck to 3.28 at the veranda); the path flags were not surveyed
   flag by flag.

## Verification

Verifier's own measurement of the 23 proposed changes (ids `garden-01` … `garden-23`), made before reading
sections 0–5 above. Scratch (not tracked): stills and gridded crops in `reference/work/r3_garden_v/`, scripts in
`build/r3/garden_v/` (`cam.py`, `fit.py`, `nadir.py`, `vpg.py`, `m215.py`, `m2165.py`, `m217.py`).

### V.1 What was done differently from the survey

- **Other frames, own calibration.** Top-down stills v13 t = 215 s (main), 216.5 s and 217 s (cross-checks); the
  survey used 214, 216, 221. Nadir from LSD line segments in six separate groups (east fence boards, shed door
  jambs, shed piers, neighbour-wall end, west fence, shed east side), stable to ± 6 px when any group is left
  out: (613, 1357) at t 215. Y vanishing point from platform sides, rail sides and the wall coping. Focal
  length from nadir x Y orthogonality: 928 (t 215), 939 (t 217), 955 (t 216.5), i.e. **920 ± 25**, a little
  above the survey's 890. A joint fit (nadir, Y point, fire pit as a 1.01 m square, wall face at the platform
  back edge, balcony door meeting stile at x 1.29) gives camera (1.68, 17.53, 7.14) at t 215 with the pit
  square to 1.5 %; t 216.5 and 217 fit less well (pit sides 0.95–1.06) and read 0.1–0.3 m longer, so t 215
  carries the result and the others bound it.
- **Scale references other than the pit**: the balcony door frame (1.64 in house.json) is 0.80 of the platform
  back edge, which puts the platform at 2.05 and f at about 912; east fence bays 1.80 / 1.82; trellis panels
  (below); the camera comes out 0.2–0.45 m above the second-floor window board (6.70) for f 910–928.
- **Ground-level counts**: brick courses on the neighbour's wall (v11 t 188: 31 courses in 349 px, wall
  2.98 m above the deck), on the shed window jamb (v2 t 271) and the shed door jamb (v2 t 274.5), a frontal
  shed view not used by the survey (v2 t 189), v11 t 195, v2 t 193 (store pier), v2 t 253 (looking back).

### V.2 Result for the lines the whole garden hangs on

| line (world y) | present | survey | verifier, t 215, f 890 / 910 / 928 | t 216.5 (f 909, pit N–S sides normalised) |
|---|---|---|---|---|
| deck north edge | 20.50 | 21.40 | 21.40 / 21.46 / 21.52 | 21.52 |
| step outer edge | 20.80 | 21.70 | 21.70 / 21.76 / 21.82 | 21.82 |
| fire pit centre | 22.26 | 23.45 | 23.40 / 23.46 / 23.51 | 23.53 |
| veranda front edge | 23.40 | 25.02 | 25.02–25.11 / 25.06–25.15 / 25.10–25.18 | 25.11 |
| shed door threshold | 25.14 | 26.72–26.80 | 26.77–26.84 / 26.79–26.86 / 26.81–26.88 | 26.84 |
| shed rear coping, outer edge (Z 2.70) | 28.90 | 30.69–30.82 | not in frame | 30.9–31.1 (t 217: 30.5–30.7) |

The survey's y values are confirmed; mine run 0.05–0.10 further (larger f), inside the stated tolerances. The
present values (phase 2) are refuted: at the present distances the camera would have to stand above the window
head for the pit to look as small as it does.

X values: my frame puts far points about 0.1 east of the survey's (yaw and anchor differ); near points agree
on the east side (fence post at y 19.6: 4.63 against 4.62). On the west side I do not confirm the shift to
−0.88: the trellis, which is fixed to the wall face, reads x −0.74 at its foot and −0.80 at its top; the coping
edge −0.77 ± 0.05 (it oversails the face); fence top −0.71…−0.85. Present −0.75 stands.

### V.3 Shed front: brick gauge

The door frame is **27.6 courses** high on its left jamb (v2 t 274.5, 28 bed joints between head and
threshold; phase 2 counted 27½), not 31. The window frame is 14.6 courses (v2 t 271; survey 14.8). In the
frontal view v2 t 189 (door left and right heights 331 / 328 px, so frontal to 1 %) the window frame is
295 x 177 px and the door frame 248 x 335 px with their heads level. The top-down door width is 1.71–1.75
(half width 77 px, clear of clutter, t 215; 1.75 at t 216.5), which agrees with the survey's 1.69. With the
door 1.69 wide its height is 1.35 x 1.69 = 2.28–2.33 and one course is 83–84 mm: this brickwork is not on a
75 mm gauge. The survey's window height (14.8 courses x 75 mm = 1.11) and sill were therefore scaled
differently from its door; in the same plane the window is 1.19 x the door width and 0.53 x its height.
Consequence: window about 2.00 x 1.22 with the sill 1.09 above the paving (13 courses), 0.48 m of brick to the
door, left edge at x 0.00. The store door plane cannot then be at x 0.06 (about 1½ stretchers of brick stand
between the store doors and the window frame in v2 t 268.5 / 269); it stays near the present −0.36 and the
front pier, whose east corner the survey located at +0.06, is wider than the cupboard is deep.

### V.4 Verdicts

| id | verdict | value to use | verifier's measurement |
|---|---|---|---|
| garden-01 | adjust | `[[-0.75,17.36],[3.40,17.36],[3.40,21.40],[-0.75,21.40]]` | North edge 21.40–21.52 (V.2); wall end foot lies on the deck-edge line. West edge: V.2, keep −0.75. Board pitch reads 0.13 in my model, so the board count is not an independent check. |
| garden-02 | accept | as proposed | Outer edge 21.70–21.82, tread 0.30 (13–14.5 px visible band + occlusion by the 0.20 drop). East end ≥ 2.63 (hidden by the pot beyond); v2 t 253 shows the step starting about 0.6 m west of the NE corner. West end not seen. |
| garden-03 | adjust | `[[-0.27,21.70],[2.75,21.70],[2.75,21.40],[3.15,21.40],[3.28,25.02],[-0.27,25.02]]` | Veranda edge 25.02–25.18; east edge 3.20–3.32. Bed width fence-to-lawn 0.54 in both surveys, so with the fence at −0.75 the lawn edge stays −0.27. |
| garden-04 | adjust | `[[-0.75,21.40],[-0.30,21.40],[-0.30,21.70],[-0.27,21.70],[-0.27,25.02],[-0.75,25.02]]` | Follows 01 / 03. |
| garden-05 | accept | centre [1.30, 23.45], 1.00 x 1.00 | (1.33–1.40, 23.40–23.53); nine headers on the near side counted in v2 t 190; inner : outer 0.56 = 1.00 − 2 x 0.215. |
| garden-06 | accept | as proposed | Drain 17.94–18.02; post feet (4.63, 19.60) (4.61, 21.43) (4.56, 23.23); lawn edge as 03. Note: the corner (4.75, 17.95) is 0.11 east of the straight fence line of garden-09 at that y. |
| garden-07 | accept | as proposed | Drain centre line (3.56, 17.96) – (4.77, 18.02); 0.13 wide gives 17.90…18.08. |
| garden-08 | accept | as proposed | Not measurable from above (under the balcony planting); v11 t 187 shows the box starting at the drain. Low. |
| garden-09 | accept | as proposed | Bays 1.80, 1.82; my post x are 0.03–0.08 east of the survey's. Either give the line a third point (4.75, 17.95) or accept that the path polygon oversails the fence line by 0.1 at the step. |
| garden-10 | adjust | line `[[-0.75,17.36],[-0.75,21.40]]`, height 3.0, coping 0.30 | North end top (−0.79, 21.50), foot on the deck-edge line; height 2.98 above the deck by courses (v11 t 188); top level with the balcony platform underside in v2 t 253. Face x: V.2. |
| garden-11 | adjust | line `[[-0.75,21.40],[-0.75,25.02]]`, 1.8, two bays, rails our side, about #B3A58C | Fence top from (−0.71, 21.44) to (−0.85, 25.08), mid post at 23.35: two bays of 1.8. Pale straw when dry (v11 t 187 / 188), brown when wet (v2). |
| garden-12 | adjust | `[[0.06,25.02],[4.22,25.02],[4.22,26.70],[-0.35,26.70],[-0.35,25.35],[0.06,25.35]]` | Front edge and depth confirmed (1.70). West end: pier corner at the front as proposed, paving runs behind the pier to the store doors (V.3). |
| garden-13 | adjust | outline `[[-0.87,25.02],[4.45,25.02],[4.45,30.75],[-0.87,30.75]]`; shed_w_front y 26.84; shed_w_rear y 30.61; shed_w_west x −0.735 and shed_w_east x 4.315 unchanged | Front: threshold 26.8–26.9. Rear: 30.5–31.1 from two weaker frames, consistent with 30.75 ± 0.35. Sides: gutter ends −0.75 / 4.52, coping corner −0.89 in my frame (0.1 east of the survey's); the optional 0.02–0.08 shifts are not supported, keep present. |
| garden-14 | accept | centre [3.33, 26.84], 1.69 x 2.33 | V.3: width 1.71–1.75 from above, H : W 1.35 in two frames (2.28–2.31). The frame stands half a brick from the east wing wall (v2 t 274.5–276). |
| garden-15 | adjust | centre [1.00, 26.84], width 2.00, sill 1.09, height 1.22 | V.3. Tolerance ± 0.06 on size, ± 0.10 on x. |
| garden-16 | accept | as proposed | Gutter lands on the front line for Z 2.3–2.36, the west coping corner for Z 2.70 (t 215) to 2.85 (t 216.5). Door head 2.30 above the paving and three courses of brick above it put the soffit at the wall near Z 2.1; 2.02 is inside tolerance. Ceiling is a guess, as stated. |
| garden-17 | adjust | shed_w_store x −0.36, y 25.35..26.68; doors centre [−0.36, 26.02], width 1.23; store polygon `[[-0.77,25.35],[-0.37,25.35],[-0.37,26.68],[-0.77,26.68]]`; front pier x −0.87..0.06, y 25.02..25.35 | V.3: only the y shift is supported. The pier corner at +0.06…+0.15 is real (3¼ stretchers east of the downpipe in v2 t 193) but the doors are not in its plane. |
| garden-18 | adjust | `[[-0.6,26.98],[4.18,26.98],[4.18,30.47],[-0.6,30.47]]`; shed_w2 centre [2.3, 30.61] | Follows 13 with the present x. Interior not filmed. |
| garden-19 | adjust | `[[-0.88,-5.2],[5.43,-5.2],[5.43,9.6],[4.9,9.88],[4.42,25.02],[4.45,25.02],[4.45,30.75],[-0.87,30.75],[-0.87,25.02],[-0.75,25.02],[-0.75,17.36],[-0.88,17.36]]`; siteBounds.maxY 31.0 | Follows 09, 10, 11, 13. |
| garden-20 | adjust | line `[[-0.74,17.39],[-0.74,21.05]]`, panels 2, panelSize [1.83, 1.5] | Panel 1.83: about ten lattice diamonds across against six to seven high; lath pitch fits a 1.83 panel, not 0.9. North end of the north panel 0.33–0.37 short of the wall end (49 px at 150 px/m in v11 t 188; from above 21.09–21.19 against a wall end of 21.46–21.52), not 0.09. South end not seen (behind the climber). |
| garden-21 | accept | as proposed | Square planter 2.9–3.3 x 20.9–21.3 from above. Trough length not measurable. Low. |
| garden-22 | accept | as proposed | Platform centred on the door meeting stile to 0.02. Width 1.95 / 2.04 / 2.12 and depth 1.09 / 1.15 / 1.21 for f 890 / 910 / 928; 2.05 from the door-frame ratio. W : D is 1.77–1.80 at any f, so the present 2.30 x 1.05 cannot be right in both. Round tube rail seen. wallPosts, rainPipe and lantern x should be re-derived with it. |
| garden-23 | accept | as proposed | Both lower lights hinge at the transom and open outward (f_0207–f_0210); at t 217 the sash bottom rail with its brass handle is over the camera. |

### V.5 Knock-on checks

- Along y on the west side: wall 17.36–21.40 (4.04) + fence 21.40–25.02 (3.62, two bays) + shed 25.02–30.75.
  Deck 4.04 + step 0.30 + lawn 3.32 + veranda 1.68 + wall 0.28 + workshop 3.49 + wall 0.28 = 30.75 − 17.36.
- Levels and risers unchanged: deck −0.05, tread −0.25, lawn −0.45 (two risers of 0.20); passage −0.30 to
  path −0.45 (one of 0.15); veranda −0.42.
- Shed front wall, x from west: store plane −0.36, brick 0.36, window 0.00–2.00, brick 0.485, door
  2.485–4.175, wing wall face 4.18. The survey's set (store 0.06, window 0.175–2.025) also closes, but only
  with a window 7 % narrower than the frontal view shows.
- Trellis ends before the wall end; fire pit 1.25 clear of the step and 1.07 of the veranda; planters inside
  the deck; step east end (2.75) clear of the square planter (2.93).
- Balcony: posts 0.22 / 1.28 / 2.34 are symmetric about the door centre 1.29 to 0.01.

### V.6 Not settled by the verifier

1. Focal length 890–930: moves far y by up to 0.12 and the balcony width by 0.17.
2. West boundary x: −0.75 to −0.87 depending on f and anchor; kept at the present value.
3. Shed brick gauge (83–84 mm) is inferred from the top-down door width, not measured directly; if the gauge
   were 75 mm the door would be 1.54 x 2.07 and the window 1.83 x 1.10, and the top-down width would be 10 %
   out, which the pit, paver and fence-bay checks do not allow.
4. Store door plane: between −0.16 and −0.36 from the front-wall budget; the doors were not seen in round 3.
5. Shed rear wall: ± 0.35, as the survey says. Step west end, trough length, side step box: not re-measured.

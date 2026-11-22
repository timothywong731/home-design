# garden - round-3 brief

Module `blender/rooms/garden.py` (fire pit, planters, trellis, furniture); zones, fences and steps are built by the site
stage. Decisions: `spec/RECONCILE3.md` (garden-01..-12, -19..-22, passage-02, envelope-13). **Rebuild from the zones: no
literal y values** (garden.py has two).

## (a) What moved

- **The garden is 0.90-1.62 longer than modelled.** Deck x -0.75..3.40, y 17.36..20.50 -> **17.36..21.40** (4.15 x 4.04);
  north step box `deck_step_n` x -0.30..2.75, y **21.40..21.70**, Z -0.25 (no step along the eastern 0.65 m); lawn y
  21.70..**25.02** (west edge -0.27, east edge 3.15 at y 21.4 to 3.28 at 25.02); lavender bed x -0.75..-0.27, y
  21.40..25.02; garden path from the passage step (y **17.95**, was 17.55) to the veranda edge 25.02, east edge on the
  fence line (x 4.74 at the step, 4.42 at the shed).
- **Passage step** line y 17.55 -> **17.95** (x 3.40..4.74), with a black channel drain y 17.95..18.08 at its foot (x
  3.71..4.69). Side step box `deck_step_e` y 17.75..18.65 -> **18.08..18.98** (immediately north of the drain).
- **East fence**: one straight line (5.13, 9.96) -> **(4.42, 25.02)** (was (4.9, 9.88) -> (4.45, 23.4)); slotted concrete
  posts at about y 18.18, 19.57, 21.34, 23.17 and the shed corner (1.83 m bays); height 2.0 kept (boards about 1.93).
- **West side**: the neighbour's extension wall `west_neighbour_wall` y 17.36..19.65 -> **17.36..21.40** (top Z 2.95, stone
  coping 0.30 wide; face x -0.75 kept); `west_fence` y 19.65..23.40 -> **21.40..25.02**, two bays, colour **#B3A58C**.
- **Fire pit** centre (1.27, 22.26) -> **(1.30, 23.45)**, 1.00 square, wall 0.215, height 0.225.
- **Trellis** two panels 0.9 -> **1.83** wide, line (-0.74, 17.39)..(-0.74, 21.05); arch top 1.50 above the deck.
- **Planters**: trough (2.95..3.37) y 18.20..20.05 -> **18.85..20.80**; new **square planter** x 2.93..3.37, y 20.82..21.26,
  0.50 high (small olive tree).
- Shed moved to y 25.02..30.75 (see shed.md). Plot rear 28.9 -> 30.75, siteBounds maxY 31.0.

Exact spec changes (old -> new):

<!-- diff:begin (generated from spec/house.json) -->
- `exterior.zones[garden_path].polygon`: [[3.4, 17.55], [4.652, 17.55], [4.47, 23.4], [3.28, 23.4], [3.28, 20.5], [3.4, 20.5]] -> [[3.4, 17.95], [4.74, 17.95], [4.42, 25.02], [3.28, 25.02], [3.15, 21.4], [3.4, 21.4]]
- `exterior.zones[deck].polygon`: [[-0.75, 17.36], [3.4, 17.36], [3.4, 20.5], [-0.75, 20.5]] -> [[-0.75, 17.36], [3.4, 17.36], [3.4, 21.4], [-0.75, 21.4]]
- `exterior.zones[deck_step_n].polygon`: [[-0.55, 20.5], [2.45, 20.5], [2.45, 20.8], [-0.55, 20.8]] -> [[-0.3, 21.4], [2.75, 21.4], [2.75, 21.7], [-0.3, 21.7]]
- `exterior.zones[deck_step_e].polygon`: [[3.4, 17.75], [3.75, 17.75], [3.75, 18.65], [3.4, 18.65]] -> [[3.4, 18.08], [3.75, 18.08], [3.75, 18.98], [3.4, 18.98]]
- `exterior.zones[lawn].polygon`: [[-0.27, 20.8], [2.45, 20.8], [2.45, 20.5], [3.28, 20.5], [3.28, 23.4], [-0.27, 23.4]] -> [[-0.27, 21.7], [2.75, 21.7], [2.75, 21.4], [3.15, 21.4], [3.28, 25.02], [-0.27, 25.02]]
- `exterior.zones[lavender_bed].polygon`: [[-0.75, 20.5], [-0.55, 20.5], [-0.55, 20.8], [-0.27, 20.8], [-0.27, 23.4], [-0.75, 23.4]] -> [[-0.75, 21.4], [-0.3, 21.4], [-0.3, 21.7], [-0.27, 21.7], [-0.27, 25.02], [-0.75, 25.02]]
- `exterior.boundaries[west_fence].line`: [[-0.75, 19.65], [-0.75, 23.4]] -> [[-0.75, 21.4], [-0.75, 25.02]]
- `exterior.boundaries[west_fence].colour` new: "#B3A58C"
- `exterior.boundaries[east_fence].line`: [[4.9, 9.88], [4.45, 23.4]] -> [[5.13, 9.96], [4.42, 25.02]]
- `exterior.steps[passage_step].line`: [[3.4, 17.55], [4.652, 17.55]] -> [[3.4, 17.95], [4.74, 17.95]]
- `exterior.features[fire_pit].center`: [1.27, 22.26] -> [1.3, 23.45]
- `exterior.features[fire_pit].size`: [1.01, 1.01] -> [1.0, 1.0]
- `exterior.features[trellis_panels].line`: [[-0.74, 17.85], [-0.74, 19.65]] -> [[-0.74, 17.39], [-0.74, 21.05]]
- `exterior.features[trellis_panels].panelSize`: [0.9, 1.5] -> [1.83, 1.5]
- `exterior.features[planters].items[trough_planter].polygon`: [[2.95, 18.2], [3.37, 18.2], [3.37, 20.05], [2.95, 20.05]] -> [[2.95, 18.85], [3.37, 18.85], [3.37, 20.8], [2.95, 20.8]]
- `exterior.features[planters].items[square_planter]` new: {"id": "square_planter", "polygon": [[2.93, 20.82], [3.37, 20.82], [3.37, 21.26], [2.93, 21.26]], "height": 0.5}
<!-- diff:end -->

## (b) Surveyors' notes (garden, passage, dims_envelope merged)

Frames: v13 f_0213-0225 (plan-like views from the Rose Room window), v11 f_0187-0196, v2 f_0154, t190-t253.

- **Deck** Z -0.05: 28 boards at 0.145 pitch running E-W, brushed wood-grain face, colour about #776860 (dry samples
  #93929A-#A79F98, wet #614E40; present #6B5645 a little dark / red), fascia #554A44.
- **West side**: ONE long slatted planter x -0.74..-0.44, y 17.65..20.50, 0.42 high, mid brown #7A6650 (red geraniums at
  the south end); the two arched diamond-lattice trellis panels (about 10 diamonds across, #6E5A44, shoulders 1.25) stand
  on its rim against the wall. Verified: the north panel ends 0.33-0.37 short of the wall end (v11 t188; from above t215).
  NW corner: box planter x -0.74..-0.30, y 20.55..21.40, 0.45 high; cream stone-effect urn dia 0.40 at (-0.05, 21.15)
  (#D0C2A3); potted standard shrub at (-0.45, 20.45). Two blue recliner chairs at (0.25, 18.9) and (0.25, 19.7).
- **East side**: black pot with rosemary dia 0.30 at (2.75, 18.65); trough planter on four feet with a black liner
  (#5A4A40); square planter with a small olive tree; terracotta pot dia 0.38 at (2.65, 21.10); pebble planter unchanged.
  Side step box grey-weathered #6E6862.
- **Fire pit**: three courses, top course 9 headers per side, thin joints.
- Lavender hedge #999785. Bird feeder pole at (3.19, 21.76).
- **Fences**: west fence pale straw when dry (#B3A58C; brown only when wet, v2), three arris rails, posts on our side.
  East fence (beside the garden and the passage) grey-painted feather-edge closeboard on slotted concrete posts with
  gravel boards (#A8A49C), mid warm grey about #8F887D-#9A9590 (present #BDB9B3 too pale); lattice topper on the
  neighbour's side only; optional white cylindrical solar light on the post at (4.73, 18.2) and a white weatherproof box
  0.22 x 0.30 x 0.10 on a post near y 17.2 with a black conduit to the ground (v11 f_0053-f_0060).
- Neighbour's wall: brick #C2AE85, coping #B5B0A3; 2.98 above the deck by courses (v11 t188).
- Path flags #A3A4A6.
- Garden length checks: veranda / lawn line 25.02-25.18 in four frames; deck edge 21.39-21.52.

## (c) New footage

- **v13** 207-225 (plan-like views down onto the balcony, deck, lawn and shed roof), **v11** 154-196 (back towards the
  garden; deck, planters, shed, trellis).

## Fallout after the foundation round

Gate check of the full build of the current tree (`build/r3/gate/home.blend`, BUILD OK) against `spec/house.json`.
Bounds are world metres of the built objects (x a..b, y c..d, z e..f), measured by `build/r3/gate/audit.py` and
`collide.py` (results in `build/r3/gate/audit_new.json` and `coll_cmp.txt`). Objects that already moved with the spec
are not listed.

- The shed moved north to y 25.02..30.75, and the backdrop pieces now intersect the shed walls, roof, felt, copings, rear
  window `shed_w2` and workshop floor and ceiling (11 to 81 triangles each):
  - `garden.backdrop` (x -1.7..8.76, y 19.16..30.95, z -0.51..8.87)
  - `garden.backdrop.hedge` (x -1.95..3.52, y 28.96..31.41, z to 4.12), which stands inside the workshop
  - `garden.backdrop.tree` (x 0.98..7.25, y 22.82..29.79, z 2.64..9.68)

  Move the hedge behind y 30.75 and keep the backdrop clear of the building.
- The deck is now y 17.36..21.40, and the lavender bed y 21.40..25.02.
  - `garden.lavender` (x -0.757..-0.21, y 20.566..23.38) and `garden.lavender.leaves` now start 0.83 inside the deck
    (y 20.57..21.40). They cross `garden.deck` and `neighbours.west_neighbour_wall` (which now runs to y 21.40).
  - `garden.bird_feeder` (x 2.979..3.487, y 20.772..21.233) now stands on the deck, its base 0.5 down through the boards.
- Under the balcony:
  - `garden.fairy_lights` with `.bulbs` and `.glow` (x 0.18..2.33, y 17.40..18.50, z 2.33..2.85) cross the new
    `balcony.structure` (57 triangles).
  - `garden.planter.pebble` (x 2.294..3.306, y 17.384..17.826; its plant reaches z 3.0) runs into the balcony's east post.
  - `garden.wisteria` (x 2.467..3.505, z to 3.0) stands against the same post; check it.
- `garden.shed_wisteria` (x -0.436..1.284, y 22.836..23.411) is still at the old shed front (y 23.40), so it now stands
  on the lawn and lavender bed 1.6 m in front of the shed.
- The east fence moved to the line (5.13, 9.96)-(4.42, 25.02).
  - `garden.climbers` and their leaves (x 4.413..4.604, y 18.12..22.49) stand 0.14..0.33 off the fence at y 18.2, and
    cross it near y 22.4.
  - `garden.bird_table` (x 4.15..4.49, y 22.37..22.64) is 0.05 off the fence.
- Not broken: the fire pit already follows its feature (centre (1.30, 23.45)). The trough (y 18.194..20.056) and the
  square planter (y 20.064..20.486) are still in the old layout; the brief already moves them.

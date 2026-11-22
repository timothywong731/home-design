# site (ground, steps, boundaries, gates, shed building) - round-3 brief

Foundation unit: `blender/lib/site.py` (+ materials). Decisions: `spec/RECONCILE3.md`. Pseudo-room detail is in
`front.md`, `side_passage.md`, `garden.md`, `shed.md`.

## (a) What moved

- **Plot** now x -0.88..5.80 at the front (east edge on the neighbour's wall across the alley), the measured fence line
  (5.13, 9.96)-(4.42, 25.02) on the east, shed sides -0.87 / 4.45, rear **30.75** (was 28.90); siteBounds maxY 31.0.
- **Front**: forecourt falls -0.06 -> -0.36 (was -0.14); setts x -0.72..4.40; `forecourt_alley_mouth` x 4.40..5.80,
  asphalt, -0.08 -> -0.36; new zone **`forecourt_alley_apron`** (asphalt, room front) x 4.25..5.80, y -0.12..1.70 with a
  notch round the bay return, falling -0.08 -> -0.30 towards the street gate; footway -0.38, road -0.50. Pier 1.40 high from
  -0.36 with a pyramid cap (new field `cap`: size 0.45, edge 0.085, rise 0.04); front wall from -0.36, brick top level at
  +0.54 (height 0.90 at the pier, the ground rising to -0.06 at the house) with a timber planter on top (new field
  `planter`: height 0.29, bottomZ 0.47, rimZ 0.76). Neither field is read by site.py yet.
- **Alley / passage**: `side_alley` x 4.65..5.80, **level -0.30** (fall removed), from y 1.70 to the garden gates; surface
  `concrete_or_flags` (an in-situ concrete texture is wanted); `side_passage` x 3.45 .. fence, ends at y 17.95; kitchen steps
  from x 3.45; `alley_neighbour_wall` x 5.80 (y 1.0..9.5), `stock_brick_yellow`; `alley_neighbour_gate` (5.13, 9.96)-(5.80,
  9.50), 1.75, colour #999690.
- **Gates**: `side_gate` (4.65, 9.03)-(5.13, 9.96), leaf 1.05 x 1.76, hinge on the K corner, colour #B7B6B2. The pivot
  offset 0.155 in `_gate` makes the 1.05 line a 0.91 leaf: shorten the offset (the hinge post can sit 0.03 off the wall)
  rather than move the post. New **`street_gate`** (5.80, 1.70)-(4.76, 1.70), hinge east, swingInto side_alley, leaf about
  0.88-0.92 x 1.83, base -0.30, colour #AEADAC, `overPanel` {top 2.75, feather_edge_grey, capping} (not read yet); the line
  stops 0.11 short of the house so that `_gate`'s latch post (placed beyond the line end) stays outside the envelope. The
  head rail is hard-coded at base + 1.95 in `_gate`: the street gate's head is about 1.86-1.9 with the panel above.
- **Garden**: deck to y 21.40; deck_step_n x -0.30..2.75, y 21.40..21.70; deck_step_e y 18.08..18.98; lawn and lavender to
  25.02; garden_path y 17.95..25.02; passage step at y 17.95 (channel drain 17.95..18.08 at its foot, x 3.71..4.69: no field,
  site or garden module); east fence straight to (4.42, 25.02) with posts at about 1.83 centres; west neighbour wall to y
  21.40 (new field `coping` 0.30); west fence y 21.40..25.02, colour #B3A58C (new field `colour`).
- **Shed building**: outline y 25.02..30.75; walls front 26.84 (height 2.82), rear 30.61, sides -0.735 / 4.315 (height 3.12
  = coping top 2.70 from -0.42); store wall x -0.36, y 25.35..26.68; openings `shed_d1` (3.33, 26.84) 1.69 x 2.33,
  `shed_w1` (1.00, 26.84) 2.00 x 1.22 sill 1.09, `shed_w2` y 30.61, store doors (-0.36, 26.02) opening onto the new zone
  `shed_store_apron`. Roof: topZ 2.40, verandaSoffitZ 2.02, new fields `coping` {west, rear, east; 0.30; topZ 2.70},
  `fascia` {z 1.98..2.20}, `gutterRimZ` 2.29, `felt` {frontZ 2.30, rearZ 2.50} (none read yet). Workshop y 26.98..30.47,
  ceilingZ 2.13; store ceilingZ 2.02.
- **Neighbours**: east massing +0.37 in x (wall face 5.80); the west note says the extension runs 4.04 beyond our rear wall.

**Tests**: `test_site.py` l.167 asserts the side gate's leaf bottom over the lower kitchen tread (-0.14); the gate now
hangs at x 4.65 and sweeps only the passage paving (-0.28): an old number. Everything else passes (SITE OK with that
assertion softened).

Exact spec changes (old -> new):

<!-- diff:begin (generated from spec/house.json) -->
- `exterior.plot.polygon`: [[-0.88, -5.2], [5.43, -5.2], [5.43, 9.6], [4.9, 9.88], [4.47, 23.2], [4.45, 23.4], [4.45, 28.9], [-0.87, 28.9], [-0.87, 23.4], [-0.75, 23.4], [-0.75, 17.36], [-0.88, 17.36]] -> [[-0.88, -5.2], [5.8, -5.2], [5.8, 9.5], [5.13, 9.96], [4.42, 25.02], [4.45, 25.02], [4.45, 30.75], [-0.87, 30.75], [-0.87, 25.02], [-0.75, 25.02], [-0.75, 17.36], [-0.88, 17.36]]
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
- `exterior.zones[side_alley].polygon`: [[4.53, 0.74], [5.43, 0.74], [5.43, 9.6], [4.9, 9.88], [4.5, 9.03], [4.53, 9.03]] -> [[4.65, 1.7], [5.8, 1.7], [5.8, 9.5], [5.13, 9.96], [4.65, 9.03]]
- `exterior.zones[side_alley].z`: -0.08 -> -0.3
- `exterior.zones[side_alley].fall` removed (was {"from": [4.98, 0.74], "to": [4.98, 9.6], "z": [-0.08, -0.3]})
- `exterior.zones[side_passage].polygon`: [[3.4, 9.03], [4.5, 9.03], [4.9, 9.88], [4.652, 17.55], [3.4, 17.55]] -> [[3.45, 9.03], [4.65, 9.03], [5.13, 9.96], [4.74, 17.95], [3.4, 17.95], [3.4, 17.36], [3.45, 17.36]]
- `exterior.boundaries[side_gate].line`: [[4.5, 9.03], [4.9, 9.88]] -> [[4.65, 9.03], [5.13, 9.96]]
- `exterior.boundaries[side_gate].height`: 1.75 -> 1.76
- `exterior.boundaries[side_gate].width`: 0.9 -> 1.05
- `exterior.boundaries[side_gate].hingeAt`: [4.5, 9.03] -> [4.65, 9.03]
- `exterior.boundaries[side_gate].colour` new: "#B7B6B2"
- `exterior.boundaries[street_gate]` new: {"id": "street_gate", "type": "gate", "line": [[5.8, 1.7], [4.76, 1.7]], "baseZ": -0.3, "height": 1.83, "width": 0.88, "hingeAt": [5.8, 1.7], "swingInto": "side_alley", "material": "ledged_braced_grey", "colour": "#AEADAC", "overPanel": {"top": 2.75, "material": "feather_edge_grey", "capping": true}, "connects": ["forecourt_alley_apron", "side_alley"], "room": "side_passage"}
- `exterior.steps[kitchen_steps].treads`: [{"polygon": [[3.4, 9.03], [4.33, 9.03], [4.33, 9.33], [3.4, 9.33]], "z": -0.02}, {"polygon": [[3.4, 9.03], [4.33, 9.03], [4.33, 9.65], [3.4, 9.65]], "z": -0.16}] -> [{"polygon": [[3.45, 9.03], [4.38, 9.03], [4.38, 9.33], [3.45, 9.33]], "z": -0.02}, {"polygon": [[3.45, 9.03], [4.38, 9.03], [4.38, 9.65], [3.45, 9.65]], "z": -0.16}]
- `exterior.zones[forecourt].polygon`: [[-0.72, -5.2], [4.53, -5.2], [4.53, -0.12], [-0.72, -0.12]] -> [[-0.72, -5.2], [4.4, -5.2], [4.4, -0.12], [-0.72, -0.12]]
- `exterior.zones[forecourt].fall.z`: [-0.06, -0.14] -> [-0.06, -0.36]
- `exterior.zones[forecourt_alley_mouth].polygon`: [[4.53, -5.2], [5.43, -5.2], [5.43, 0.74], [4.15, 0.74], [4.15, -0.12], [4.53, -0.12]] -> [[4.4, -5.2], [5.8, -5.2], [5.8, -0.12], [4.4, -0.12]]
- `exterior.zones[forecourt_alley_mouth].surface`: "concrete_setts_grey_buff" -> "asphalt"
- `exterior.zones[forecourt_alley_mouth].fall.from`: [4.98, -0.12] -> [5.1, -0.12]
- `exterior.zones[forecourt_alley_mouth].fall.to`: [4.98, -5.2] -> [5.1, -5.2]
- `exterior.zones[forecourt_alley_mouth].fall.z`: [-0.08, -0.14] -> [-0.08, -0.36]
- `exterior.zones[footway].z`: -0.16 -> -0.38
- `exterior.zones[road].z`: -0.28 -> -0.5
- `exterior.zones[forecourt_alley_apron]` new: {"id": "forecourt_alley_apron", "group": "front", "polygon": [[4.25, -0.12], [5.8, -0.12], [5.8, 1.7], [4.65, 1.7], [4.65, 0.74], [4.25, 0.74]], "z": -0.08, "surface": "asphalt", "room": "front", "fall": {"from": [5.2, -0.12], "to": [5.2, 1.7], "z": [-0.08, -0.3]}}
- `exterior.boundaries[front_wall_w].baseZ`: -0.1 -> -0.36
- `exterior.boundaries[front_wall_w].planter` new: {"height": 0.29, "bottomZ": 0.47, "rimZ": 0.76}
- `exterior.boundaries[front_pier_w].baseZ`: -0.14 -> -0.36
- `exterior.boundaries[front_pier_w].height`: 1.2 -> 1.4
- `exterior.boundaries[front_pier_w].cap` new: {"size": 0.45, "edge": 0.085, "rise": 0.04}
<!-- diff:end -->

## (b) Surveyors' notes for the site (merged)

- Setts: 160 courses parallel to the house, one darker border course (#7E7B75) lengthwise against the house; light warm
  grey #A6A29A with 15 % buff #B3AB95 and 10 % pinkish #A8958C units - the present pink chequer is too strong and regular.
  Tarmac #6B6A64 patched and cracked. Two recessed inspection covers side by side east-west at (4.67, -2.0) and (5.21,
  -2.0), 0.48 x 0.58, galvanised frames, concrete trays #8C8A86. Gullies 0.15 square at (-0.78, -0.25) and (2.4, -0.20).
  Footway flags 0.6 x 0.9 / 0.6 x 0.6 #A6A39F with tarmac patches; lamp column at about (7.5, -7.0), street tree about
  (-1.2, -7.0); east neighbour's dark corrugated raised planter 0.9 x 2.0 x 0.5 at about x 6.0..6.9, y -5.0..-3.0.
- Pier buff brick #BFAD84, cap exposed aggregate #A6A398; planter boards dark brown weathered silver (#5B4A3A-#8F7C65).
- Side passage paving: 600-series random course (900x600, 600x600, 600x290), pale 12-15 mm joints, courses along the
  passage, #A6A9B0; inspection cover 0.56 x 0.72 at x 4.50..5.06, y 10.25..10.97 against the fence; gully under the K
  downpipe dark grey #2A2A2C.
- Alley concrete #A6A8A0 with algae #7E8A72 along both walls, cracks, a 0.60 x 0.45 access cover 0.5 south of the flue,
  the passage flags stop on a diagonal cut along the garden gate. Neighbour's alley wall weathered London stock, Flemish
  bond, #A39A86, red-brick return at the street.
- Gates: framed, ledged and braced, '<' braces seen from the side they open to, tee hinges with 0.35-0.40 straps, rim lock
  and cabin hook on the latch stile; side gate #B7B6B2, street gate #AEADAC with a fixed feather-edge panel above (lead-grey
  capping), both operable.
- Fences: east fence closeboard (about 17 feather-edge boards a bay, capping rail) in slotted concrete posts (#A8A49C) at
  about 1.83-1.9, boards about 1.93 high, taupe-grey #8F887D, gravel boards beside the garden, lattice topper on the
  neighbour's side only; west fence two bays, rails and posts on our side, pale straw #B3A58C.
- Neighbour's west wall brick #C2AE85, coping #B5B0A3, top Z 2.95.
- Deck boards 28 at 0.145 E-W #776860, fascia #554A44; path flags #A3A4A6.
- Shed: brick gauge 84 mm; veranda red block herringbone with a soldier course along the front edge; coping #C9C5B8,
  felt #7D7E7A; white fascia and half-round gutter along the front, downpipe at the SW corner; the side copings end at the
  front as the pier caps.

## (c) New footage

- v8 1-138 (front, forecourt, gate and alley from the street), v9 7-20 and 45-68 (forecourt), v11 18-196 (passage, alley,
  gates, garden), v13 207-225 (garden and shed roof from above).

## Fallout after the foundation round

Gate check of the full build of the current tree (`build/r3/gate/home.blend`, BUILD OK) against `spec/house.json`.
Bounds are world metres of the built objects (x a..b, y c..d, z e..f), measured by `build/r3/gate/audit.py` and
`collide.py` (results in `build/r3/gate/audit_new.json` and `coll_cmp.txt`). Objects that already moved with the spec
are not listed.

These are clashes between the site stage and the envelope stage, found in the foundation-only build
(`build/r3/gate/found.blend`, checked with `fcollide.py`).
- The canopy downpipe `facade.pipes.upvc_white`, at (-0.78, -0.17), runs down through the end of `front.front_wall_w`
  (wall top 0.54, end at y -0.12; 32 triangles). End the planter wall at about y -0.21 (envelope request), or have the
  envelope move the pipe.
- Both gate frames clash with the envelope's east-wall base rail:
  - `side_passage.street_gate.frame` (14 triangles) and `side_passage.side_gate.frame` (8 triangles) cut
    `facade.east_E.sills` (the rail is x 4.618..4.685, z -0.09..-0.045).
  - The street gate frame also cuts `facade.east_E`, whose face is at x 4.65.

  Stop the posts at the rail or the new face.
- `facade.downpipe.1` crosses `side_passage.kitchen_steps` over x 3.92..4.39, y 9.18..9.35, z -0.28..-0.02 (42
  triangles), i.e. a pipe running through the treads. Agree with the envelope where this downpipe and its shoe go.

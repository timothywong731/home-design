# side_passage (side passage + alley along the east wall) - round-3 brief

Module `blender/rooms/side_passage.py` (fittings, pipes, lights, condensers); zones, gates and fences are built by the
site stage, wall skins and pipes on them by envelope. Decisions: `spec/RECONCILE3.md` (passage-01..-12, envelope-02, -03,
-08, -09, front-09, -10, garden-07).

## (a) What moved

- **Both house faces moved out**: flank x 3.40 -> **3.45**, east wall (now known to be EXTERNAL, facing the alley) x 4.53
  -> **4.65** (external insulation: render 0.10 proud of the old brick face 4.55, which shows black below a white base
  rail). Face K is x 3.45..4.65 (1.20 wide).
- **Side passage** x 3.45 .. fence: 1.68 wide at the gate narrowing to 1.30 at the step; it now ends at the step at y
  **17.95** (was 17.55). Kitchen steps start at x 3.45.
- **Garden gate `side_gate`**: (4.50, 9.03)-(4.90, 9.88), leaf 0.90 -> **(4.65, 9.03)-(5.13, 9.96), leaf 1.05 x 1.76**,
  hung on the K corner, latch post (5.13, 9.96), swings into the passage. lib/site._gate's pivot offset 0.155 turns a
  1.07 line into a 0.91 leaf: shorten the offset rather than move the post (site owner).
- **East fence** starts at the latch post (5.13, 9.96) and runs straight to the shed corner (4.42, 25.02).
- **Alley `side_alley`**: 0.90 -> **1.15 wide** (x 4.65..5.80, neighbour's wall face 5.43 -> **5.80**), **level at -0.30**
  (was a fall from -0.08), in-situ concrete (surface key `concrete_or_flags` until a concrete texture exists), open to the
  sky, from a **new street gate at y 1.70** to the garden gates. `alley_neighbour_wall` x 5.80, yellow stock with a red
  return. `alley_neighbour_gate` (5.13, 9.96)-(5.80, 9.50), bare timber #999690, 1.75 high.
- **New `street_gate`**: line (5.80, 1.70)-(4.76, 1.70) (it stops 0.11 short of our wall for the latch post), hinge on the
  east (neighbour's) post, leaf about 0.88-0.92 x 1.83, opens north into the alley to lie against the neighbour's wall;
  fixed feather-edge panel above to about 2.75 with a capping (field `overPanel`, not yet read by lib/site.py);
  base -0.30. Between the street gate and the bay return the tarmac apron `forecourt_alley_apron` falls from -0.08 to
  -0.30 (where the real step is was not established).
- **Condenser on the east wall** `condenser_east` (4.53, 8.4, 2.2) 0.3 x 0.8 x 0.7 -> **(4.65, 5.3, 2.35) 0.33 x 0.85 x
  0.80**. `condenser_flank` and `soil_stack` x 3.40 -> 3.45.

Exact spec changes (old -> new):

<!-- diff:begin (generated from spec/house.json) -->
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
- `exterior.features[condenser_flank].at`: [3.4, 15.3, 3.25] -> [3.45, 15.3, 3.25]
- `exterior.features[condenser_east].at`: [4.53, 8.4, 2.2] -> [4.65, 5.3, 2.35]
- `exterior.features[condenser_east].size`: [0.3, 0.8, 0.7] -> [0.33, 0.85, 0.8]
- `exterior.features[soil_stack].at`: [3.4, 12.35] -> [3.45, 12.35]
<!-- diff:end -->

## (b) Surveyors' notes (passage, front, dims_envelope, garden merged)

**Flank fittings** (v11 f_0021-f_0031, t63): white louvre vent to (3.45, 10.00, z 1.86..2.03), 0.155 square, 3 gravity
louvres - north of the WC window, not at y 9.25. Tap T2 to y 9.90, z 0.48 (brass bib tap, green click connector). Chain
hook y 10.02, z 0.75 (fine). **Delete `side_passage.wall_box`**: it was the WC sill block. Gully grate under the K downpipe
at about (4.45, 9.12): dark grey #2A2A2C, 0.15 square (model red-brown). Inspection cover 0.56 across x 0.72 along the
passage at x 4.50..5.06, y 10.25..10.97, against the fence, galvanised frame with a centre bar and a lifting slot on its
north edge, two flag infills (v13 t31, t33; v11 t63). Low pipe along the flank foot y 9.70..12.30: add the screw access cap
on its south end and a second 40 mm black pipe beside it. Flank condenser, thin 25 mm black drop pipe at y 15.87, tap T1
(y 16.50, z 0.20, black 2x2 distributor 0.17 x 0.12) and hose reel (y 16.7..17.2, z 0.75..1.25, grey with a yellow band)
are right. Face K: back-door frame 0.04-0.05 from the flank corner; black 68 mm downpipe on K between the door and the east
corner (x about 4.45) with three clips; louvre vent, small white box, tap and chain on the flank just north of the corner.

**East wall in the alley** (v11 f_0083-f_0105, f_0126-f_0149): blank render, no openings. Condenser light grey (#D8D8D4)
on galvanised brackets, y 5.3..6.15, z 2.35..3.15 (+/-0.5 in y), rotary isolator (grey box, red handle) at its north end.
Flue: white 100 mm round pipe from a grey lead slate 0.30 square on the floor at y 8.55, 0.10 off the wall, two white
clips, 90 deg elbow at z 2.6 and a 0.35 ribbed white terminal pointing north along the wall (model: grey 120 mm with a
cowl at y 7.78). Two anthracite cylinder down-lights 0.06 dia x 0.15 on 0.08 square plates, warm white and **lit** in v11,
at (4.65, 3.4, 2.65) and (4.65, 7.0, 2.65) - make them clickable; a smaller unlit black fitting at (4.65, 5.0, 1.75).
Black louvred extract grille 0.15 square at (4.65, 6.7, 1.85). Twin black ribbed conduits (45-50 mm, strapped every
0.5 m) rise from the base rail at y 3.5 to z 3.3 and run north to the condenser; a bundle of four black cables up the NE
corner; a thin black cable diagonally from the gate head to the front eaves (omit or keep thin); a black vent cowl about
0.25 x 0.3 at z 4.3 roughly 1 m behind the front corner; a black cable loop at 2.9 m (omit). Y positions on this wall are
+/-0.5. Base: white bell-cast strip 0.06 high, 0.03 proud, about 0.25 above the alley floor (z -0.09..-0.03 in the
envelope field), black plinth below, white vertical stop where it returns at the front corner (v8 f_0077-f_0079).

**Alley** (v11 f_0073-f_0083, f_0113-f_0127): in-situ concrete grey #A6A8A0 with green algae #7E8A72 along both walls,
cracks, a 0.60 x 0.45 concrete access cover 0.5 south of the flue, and the downpipe pad at the north end; the passage
flags stop on a diagonal cut along the garden gate. Neighbour's wall: weathered London stock in Flemish bond, true
#A39A86, two terracotta air bricks at z 0.9 and 1.2 near y 4-5; a white meter box on it by the street gate (omit, it is
theirs).

**Gates**: `side_gate` framed, ledged and braced: two stiles, three ledges, two braces forming a '<' seen from the garden
(both meet the latch stile at the middle ledge; the lib draws them rising from the hinge side), 9 vertical boards, three
galvanised tee hinges with 0.40 straps on the garden face, grey long-throw rim lock at 1.10 and galvanised cabin hook at
0.75 on the latch stile, plain boards on the alley face; light grey #B7B6B2; head rail top 1.97-2.00 above the paving
(v11 f_0062-f_0076, f_0150-f_0167; v13 t31-t33). `street_gate` same construction ('<' seen from inside, hinges on the
left / east), three tee hinges with 0.35 straps on the inside face, lock about 0.94-1.1 and cabin hook on the west
stile, brass cylinder escutcheon on the street face; fixed feather-edge panel above lapping 0.04 over the leaf on the
street face, lead-grey capping; weathered light grey #AEADAC (street face reads grey-mauve, alley face bare silver).
Operable. Its size was read 0.78 x 1.34 against bricks 0.6 m in front of the gate plane; the alley-width scale gives
0.92 x 1.83 with the panel top 2.74-2.77 (v8 t81.5, v11 t82, t106).

**Fence**: closeboard panels (about 17 feather-edge boards a bay, flat capping rail) in 0.10 concrete posts at about 1.9
centres, no gravel board in the passage, warm taupe-grey #8F887D, posts #A8A49C; boards about 1.93 high (posts 2.03).
Paving: **600-series** random course (900x600, 600x600, 600x290, 12-15 mm pale joints; the 560-series reading was on a
smaller scale), courses along the passage, flags #A6A9B0. Kitchen steps as modelled (risers 0.146 + 0.12 + cill, treads
0.295 / 0.61).

**Cameras**: the present 'alley' camera points at the old condenser position; add one looking each way along the alley,
e.g. pos (5.2, 2.2, 1.1) look (5.0, 8.5, 1.3) and pos (5.2, 8.3, 1.1) look (5.2, 1.9, 0.9) (alley floor -0.30).

## (c) New footage

- **v11** (PXL_20261121_124951560) 18-60 passage (paving, walls, windows, sills, downpipes, hose reel, tap); 61-76 and
  about 111 the timber gate and latch; **77-153 the alley towards the street** (flank, pipes, vents, lit wall lights,
  condenser, gates); 154-187 back towards the garden.
- **v8** (PXL_20261121_124142138) 67-89: the street gate, the rendered east wall and the neighbour's flank from the street.
- **v13** t28-38 (passage seen from the Lavender Room window), t29-33 (gate and fence from above).

## Fallout after the foundation round

Gate check of the full build of the current tree (`build/r3/gate/home.blend`, BUILD OK) against `spec/house.json`.
Bounds are world metres of the built objects (x a..b, y c..d, z e..f), measured by `build/r3/gate/audit.py` and
`collide.py` (results in `build/r3/gate/audit_new.json` and `coll_cmp.txt`). Objects that already moved with the spec
are not listed.

- The outer face of the flank wall moved from x 3.40 to x 3.45 (`facade.flank_F` is now x 3.185..3.45). The wall
  fittings built at x 3.40 now sit 0.05 inside it; move them to x 3.45:
  - `side_passage.tap.door` and its head (y 9.775..9.825)
  - `side_passage.tap.rear` with `.head`, `.splitter` and `.water` (y 16.465..16.645)
  - `side_passage.hose_reel` (y 16.58..17.198)
  - `side_passage.vent` (y 9.175..9.325, z 1.975..2.125)
  - `side_passage.wall_box` (y 9.15..9.25)
  - `side_passage.chain` (y 9.993..10.007)

  `side_passage.condenser.flank` already sits on 3.45.
- `side_passage.gully` (x 4.305..4.455, y 9.095..9.245) now sits at z -0.02, the level of the kitchen tread. Its east
  part hangs 0.29 above the passage floor (-0.30). Set it into the passage floor at about (4.45, 9.12), as the site note
  says.
- `side_passage.flue` (x 4.64..4.81, y 4.599..4.761, z -0.30..3.04) runs into the base rail of the east wall's
  insulation (`facade.east_E.sills`, x 4.618..4.685, z -0.09..-0.07). The living room's east wall is now 0.35 thick:
  its rendered outer face is at x 4.65, and the base rail projects to x 4.685. Stand the flue off the new face.
- The east fence moved. `side_passage.climbers` and their leaves (x 4.61..4.85, y 10.89..16.46) now stand up to 0.24
  off it: the fence is at x 5.09 at y 10.9 and x 4.82 at y 16.46.
- The envelope's flank conduits stop short of `side_passage.condenser.flank`; the inverted-U loop into its top is left
  to you (envelope request).

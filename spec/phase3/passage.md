# Round 3 survey — "passage": kitchen back door, side passage, side alley, flank elevation

Surveyor notes for the round-3 builders and the reconciler. World frame of `spec/BRIEF.md` (metres, +Y from the
front door into the house, +X to the right, Z up, ground-floor FFL = 0). Faces as in
`spec/phase2/rear_elevation.md`: **F** = flank of the back addition (x 3.40, faces +X), **K** = kitchen-door wall
(y 9.03, faces +Y), **E** = east wall of the main house (x 4.53, faces the alley).

Footage read: v11 frames 1-196 (every frame, as 4x2 montages, then about 90 full-resolution stills), v8 1-6 and
67-92, v13 20-51, plus the round-2 stills of v2 (`reference/work/p2_rear_ext/v2_t342.jpg`). Scratch (private,
git-ignored): `reference/work/r3_passage/` (`m11_NN.jpg` montages, `v11_tSSS.jpg` = v11 at t = SSS s = frame
SSS+1, `g_*.jpg` gridded crops), tools in `build/r3/passage/` (`met.py` ground-plane metrology, `fcal.py`
vanishing points, `period.py` brick-course period, `grid.py`). Model previews: `build/preview/*_r3passage.jpg`.

## 0. What changed in our knowledge

1. **The side alley is now filmed end to end** (v11 f_0070-f_0160, v8 f_0067-f_0084). It is a level concrete
   strip about 1.0 m wide between our rendered east wall and the neighbour's stock-brick wall, closed at the street
   end by a **low timber gate with a fixed boarded panel over it**, set back about 0.6 m from our wall's front
   corner. Nothing of this gate is in the model. The east wall has **no windows**; it carries a white boiler flue,
   an a/c condenser (mid-wall, not at the north end), twin black conduits, two lit wall lights, a black extract
   grille, and a white bell-cast strip over a black plinth.
2. **The garden gate is longer and its latch post stands further north and east** than modelled: the passage is
   about 1.58 m wide at the gate, not 1.50, and narrows faster (to about 1.15 m at the step).
3. **The back-door frame is 0.79 wide, not 0.84**; everything else about the door holds.
4. Paving is the **560-series** of Indian sandstone (modules 0.575 / 0.86 / 0.29 with joints), and the inspection
   cover is a 600 x 450 recessed tray lying along the passage against the fence, not across it.
5. On the flank: the louvre vent, the tap and the chain are **north** of the WC window (the model has the vent south
   of it and a spurious "small white box"); the outside frames of the WC and utility windows start lower than the
   interior openings in `house.json`.

## 1. Scale — read this before using any number below

There is no tape-measured object outdoors, so every plan dimension here hangs on one chain. I tested two
hypotheses for the slab module (600-series vs 560-series) and adopted the second:

| check | frame | result under the adopted scale |
|---|---|---|
| inspection cover, aspect 1.295 | v13 t32 (top-down) | 0.68 x 0.52 = a 600 x 450 recessed cover (overall 673 x 523) |
| slabs joint to joint | v13 t32 | 0.57-0.575 and 0.86-0.87 -> 560 x 560 / 845 x 560 / 560 x 275 with 12-15 mm joints |
| fence height by parallax | v13 t32 | 1.82 |
| K-wall width, flank corner to NE corner | v13 t32 | 1.10-1.17 (house.json 1.13) |
| kitchen steps | v13 t32 | treads 0.295 and 0.61 deep, to x 4.30 (house.json 0.30 / 0.62 / 4.33) |
| camera position under the Lavender Room window | v13 t32 | y 10.50 (window is y 9.875-10.625) |
| back-door clear opening height | v11 t63 | 2.00 (standard uPVC door) |
| downpipe on face K | v11 t63 | 0.073 (a 68 mm pipe) |
| lower step riser | v11 t63 | 0.146 |
| soil stack in the foreground against a slab | v11 t63 | slab 0.54-0.57 if the stack is 110 mm |

Method: `met.py` back-projects image points onto a horizontal plane from the vertical vanishing point and a focal
length (860 px on a 1080-wide still; results in the table move by under 2 % for 800-920). The top-down still
v13 t32 (frame 33, from the Lavender Room window, nadir at the foot of the flank) gives a near-plan view of the
passage from the kitchen steps to 4.7 m north of them; the level view v11 t63 (frame 64) gives heights.

**Residual ambiguity:** if the slabs were 600-series instead, every plan length in sections 3-5 grows by 4.5 %
(passage 1.65 at the gate, K wall 1.18, door frame 0.82). The ten checks above all favour the 560 reading; the
one thing against it is that it needs the v13 camera 0.3 m higher or its focal length 5 % longer than my nominal
values. Tolerances quoted below do **not** include this 4.5 %.

Alley dimensions come from a different chain: brick courses of the neighbour's wall (75 mm) read by
autocorrelation (`period.py`) in two frames, cross-checked by the top-down still.

## 2. Inventory — what the footage shows and the model lacks or has wrong

Colours: "sampled" is the median sRGB of a patch in an HDR video still (daylight, mostly open shade); "true" is my
estimate under neutral light.

### 2.1 Kitchen back door `d_back` (v11 f_0001-f_0020 inside, f_0062-f_0066, f_0166-f_0167 outside; v2 t342 closed)

| item | model | footage |
|---|---|---|
| frame | 0.84 x 2.64, x 3.40..4.24 | **0.79 x 2.68**, west edge 0.02 off the F/K corner: x 3.42..4.21; clear opening 0.68 x 2.00 |
| leaf | half-glazed | sash 0.72 x 1.98. Obscure (stippled) glass 0.525 x 0.98, glass z 0.96..1.91; mid-rail z 0.82..0.96 with a drip bar on the outside; lower flat panel 0.57 x 0.77 in a mitred bead |
| cat flap | 0.22 x 0.24, bottom 0.19 | 0.215 x 0.23 white frame with a clear arched flap and a small red rotary lock at lower right (inside); it sits **on the bottom bead of the panel: bottom z 0.14**, centre 0.06 east of the leaf centre |
| fanlight | to 2.64 | transom z 2.04..2.15, obscure pane 0.67 x 0.465, head 2.68 |
| trickle vent | - | white hooded slot vent 0.30 long in the leaf's top rail, both faces (f_0007, f_0008) |
| hinges, swing | east, inward | confirmed: three white flag hinges on the east jamb; shown open 95 deg against the east wall (f_0017-f_0020, f_0064) |
| handles | brass lever | lever on a 0.24 x 0.03 backplate with euro cylinder, both faces, on the west stile, lever z 1.00. Inside polished brass; outside brass (sampled gold) |
| threshold | - | white uPVC cill 0.035 high with a brush strip; outside it lands on the upper stone tread |
| colour | white | uPVC white, sampled #CDCED0 outside, true #F2F2EF |

Inside, beside the door (kitchen unit): aluminium chequer plate on the west return wall at low level (already in
`kitchen.md`); the wall-mounted glass memo board on the east wall stays **blank**.

### 2.2 Kitchen steps and the K wall (v11 f_0020-f_0024, f_0062-f_0068, t63; v13 t29, t32)

- Two sandstone treads, each a 30 mm slab with a 20 mm nosing on a grey rendered riser: lower tread top 0.146
  above the paving, upper 0.26-0.27, door cill 0.30. Plan as modelled (x 3.40..4.30, nosings 0.295 and 0.61 from K).
- **Downpipe on K** at x 4.38: black 68 mm round, three clips, shoe 0.03 above a **dark grey square gully grate**
  0.15 (the model's grate is red-brown: make it #2A2A2C).
- First-floor soil branch: black 110 mm, leaves K at x 4.25 z 3.30 through two swept bends under the security
  light, turns the corner, runs north on F on four brackets falling to the stack. On top of it, 0.6 m south of the
  stack, a short vertical capped stub (air-admittance / rodding cap, a 0.13 dome); under it a second 50 mm pipe
  1.0 m long with a capped south end, joining the stack through a boss.
- Security light: white twin-head flood with a camera between the heads, on K at x 3.95, z 3.45, under the
  first-floor sill (present; height fine).
- First-floor window on K (`w_gbath`): two lights, top-hung fanlight over a side-hung lower casement (standing
  open in v11 f_0039-f_0042), obscure glass, white stone sill. As modelled.
- A thin black cable crosses K at z 3.3 from the downpipe to the alley.

### 2.3 Flank F, ground storey, south to north (v11 f_0021-f_0035, f_0044-f_0056, f_0164-f_0186)

| item | y | z (FFL) | description | model |
|---|---|---|---|---|
| WC window | 9.41..9.75 | recess 1.10..1.94 | slot: uPVC frame 0.33 x 0.82 set **0.20 back** in a square rendered reveal, obscure glass; white-painted stone sill block 0.50 x 0.10, projecting 0.07, paint flaking | opening 0.34 x 0.70 from 1.22; reveal fine |
| tap T2 | **9.90** | 0.48 | brass bib tap, cross-head, hose-union nose with a green click connector | at 9.80, z 0.45 |
| chain | **10.02** | hook 0.75 | galvanised staple plate with 0.45 m of chain hanging to the low pipe | at 10.0 - fine |
| louvre vent | **10.00** | 1.86..2.03 | white plastic gravity-flap grille, 3 louvres, 0.155 square, 0.02 proud | at y 9.25, z 2.05: **move north of the window** |
| "small white box" | - | - | does not exist: it is the WC sill block | **delete** `side_passage.wall_box` |
| low pipe | 9.70..12.30 | top -0.17 | old black 110 mm pipe on the paving against the wall, screw access cap on its south end facing the steps, ring-seal collar every 2 m, one strap to the wall; a second 40 mm black pipe lies beside it on the passage side; it swings into the foot of the stack through a 45 deg junction | present (single pipe) |
| utility window | 11.3..12.05 | frame 0.92..1.90 | white uPVC, one top-hung light, slot trickle vent in the head, obscure glass, shallow reveal 0.06, **thin white uPVC stub cill** 0.03 x 0.80 (not a stone block) | 0.56 x 0.82 from 1.05, see 3 |
| soil stack | 12.30 | to above the eaves | black 110 mm with ring-seal sockets every 1.5-2 m and two brackets per storey; a capped boss 0.35 above the paving on its south side; the top third is paler grey with a cage cowl | present |
| en-suite waste | 12.4..13.4 | 3.45..4.05 | black 40 mm: from a boss on the stack 0.5 north, up 0.3, north 0.6, elbow into the wall | present as one sloping pipe |
| black plinth | from 12.4 to the rear corner | -0.30..-0.11 | starts north of the stack (south of it the low pipe covers the foot); 0.19 high | 0.22: fine |
| dining window S | 12.76..13.28 | sill block top 0.97 | fixed light in a 0.18 deep reveal, white stone sill block 0.10 thick projecting 0.07, 0.06 longer than the opening each side | fine |
| condenser | 15.0..15.85 | 3.2..3.85 | light grey unit on two galvanised angle brackets, fan grille to the passage; a 25 mm black pipe drops from it straight down the wall at y 15.87, three clips, to the plinth | fine |
| dining window N | 15.94..16.46 | as S | stippled obscure glass | fine |
| tap T1 | 16.50 | 0.20 | brass tap with a black 2 x 2 distributor box 0.17 x 0.12, three green/yellow hose tails | fine |
| hose reel | 16.7..17.2 | 0.75..1.25 | grey auto-reel with a yellow band over the top, on a dark grey wall bracket | fine |

Render: fine sand-textured stucco, strongly stippled at close range (v11 f_0024, f_0131). Sampled #CDC39C in the
open, #A8A28A in shade; true **#D2C596** stands. Plinth sampled #27272F, true #2A2A2C stands. Sills #D0D1D5,
true #EDEDE8. No wall lights on F.

### 2.4 Flank F, upper storeys (v11 f_0036-f_0043, f_0150-f_0160; v13 f_0030-f_0038)

- Twin black ribbed conduits (each 45-50 mm, strapped together every 0.5 m): from the K corner north at
  second-floor sill level, **down in a rectangular drop just north of the yellow-room window to z 3.9**, north
  under the small en-suite window and past the stack, then a 0.9 high inverted-U loop into the top of the
  condenser. The model has one straight pipe at z 6.2.
- Yellow-room window: wide two-light (top-hung fanlight over a top-hung main light), both ajar. En-suite window:
  small, single top-hung light. Second floor: Lavender Room window (fanlight over a side-hung light, the one the
  owner opens in v13) and the bathroom window, both right under the black eaves gutter. Positions not re-measured.
- From above (v13 f_0030-f_0038): the Lavender Room window has a 0.15 deep white external uPVC cill (weathered)
  and friction-stay hinges; the yellow-room window below shows as a white frame with its fanlight pushed out.

### 2.5 Side passage ground (v11 f_0017-f_0034, f_0044-f_0064, f_0161-f_0175; v13 t32)

- **Paving**: riven grey sandstone, random-coursed 560 series: 845 x 560, 560 x 560, 560 x 275, with 12-15 mm
  pale mortar joints, courses running along the passage, cut row against the flank. Sampled #99A0AF-#A4ABB6
  (sky reflection), true #9A9CA0 stands; joints #9CA2AC -> true #8C8A84.
- **Inspection cover**: recessed tray filled with two flag pieces, galvanised frame with a centre division and a
  lifting slot on its north edge. Overall 0.52 across x 0.67 along the passage: **x 4.41..4.93, y 10.44..11.10**,
  touching the fence. The model has it 0.60 x 0.80 at x 4.15..4.75, y 10.10..10.90.
- At the gate line the flags stop on a diagonal cut along the gate; beyond is the alley's concrete, flush.
- Step at y 17.55, channel drain, deck fascia, timber box step: as modelled (v11 f_0187-f_0193).

### 2.6 East fence (v11 f_0033, f_0045-f_0061, f_0172-f_0174; v13 t32, t36)

- Closeboard panels (feather-edge boards, about 17 to a bay, under a flat capping rail) slotted into **concrete
  posts 0.10 wide at about 1.9 centres**, post tops level with the capping; the boards run down to the paving (no
  gravel board seen). Top **1.80 above the paving** (parallax 1.82 in v13 t32, 1.67-1.70 in v11 t63); the model
  has 2.0.
- Colour: warm taupe-grey stain, darker and browner than the gate in every frame that shows both. Sampled
  #7E7970 (v11 t63), about #9A9488 in direct light (f_0061), #5E5E64 in shade; true **#8F887D** (the model's
  #BDB9B3 is nearer the gate's colour). Posts raw concrete #A8A49C.
- A small black solar light on the gate's latch post (present). A white weatherproof box 0.22 x 0.30 x 0.10 on the
  post at about y 17.2, top 1.9, with a black flexible conduit to the ground (optional; garden unit).
- Climbers on the bays north of y 14.

### 2.7 Garden gate (v11 f_0062-f_0076, f_0150-f_0167; v13 t29, t32)

- Posts: hinge post 0.075 x 0.10 fixed to K just east of the downpipe, centre **(4.48, 9.08)**; latch post 0.10
  square at the end of the fence, centre **(4.98, 10.21)**; head rail 0.045 x 0.095 between their tops, top 1.97-2.00
  above the paving. The neighbour's own gate (weathered bare timber, sampled #999690, framed, flat capped top,
  1.75 high) closes from the same latch post to their house corner.
- Leaf **1.05 wide x 1.76 high**, framed, ledged and braced: two stiles, three ledges, two braces forming a "<"
  as seen from the garden (both meet the latch stile at the middle ledge), 9 vertical boards. Three galvanised
  tee hinges with 0.40 straps on the garden face. Grey long-throw rim lock at z 1.10 and a galvanised cabin hook
  at 0.75 on the latch stile. Alley face: plain boards.
- Painted light grey, sampled #A4A5AA-#ABADB1, true **#B7B6B2**.
- Swing: about the house-end post, into the passage (shown open 95 deg in f_0072-f_0075 and f_0150-f_0160).

### 2.8 Side alley (v11 f_0070-f_0160)

- **Floor**: in-situ concrete, **level** (brick courses and floor share one vanishing point within 0.5 deg), flush
  with the passage flags at the garden gate. Weathered grey with green algae along both walls, cracks, cast-in
  patches; a 0.60 x 0.45 concrete access cover with a steel edge 0.5 south of the flue. Sampled #8D9392-#B7BFB8,
  true #A6A8A0 with #7E8A72 algae.
- **East wall base**: a white strip (bell-cast drip bead, 0.06 high, 0.03 proud, painted white, sampled #D2D4E4)
  with its top 0.25 above the floor, black plinth below it (#2E2E30). The strip returns down as a white stop at the
  wall's front corner. The flank has no such strip.
- **Flue**: white 100 mm round pipe coming up through a grey lead slate 0.30 square on the floor, 0.10 off the
  wall, at **y 8.55** (0.45 south of the NE corner); two white clips; 2.9 above the floor (z 2.6) a 90 deg elbow
  and a 0.35 long ribbed white terminal pointing north along the wall. The model has a grey 120 mm pipe with a conical cowl at
  y 7.78.
- **Cables at the NE corner**: a bundle of four black cables clipped up the corner from the floor to the eaves.
- **Condenser** (multi-split size): 0.85 x 0.33 x 0.80 high, light grey, on galvanised brackets, coil side to the
  alley; **y 5.3..6.15, z 2.35..3.15** (floor + 2.6..3.45); rotary isolator (grey box, red handle) on the wall at
  its north end. The model has it at y 8.4, z 2.2.
- **Conduits**: the twin black ribbed conduits rise from the bell-cast at y 3.5, lean north as they climb, and at
  z 3.3 run north to the condenser; a second pair continues up to the eaves.
- **Wall lights (both lit in v11)**: anthracite cylinder down-lights, 0.06 diameter x 0.15, on a 0.08 square
  plate, warm white, at **(4.53, 3.4, 2.65)** and **(4.53, 7.0, 2.65)** (floor + 2.9). A third, smaller black
  fitting (sensor or unlit lamp) at (4.53, 5.0, 1.75).
- **Extract grille**: black louvred square 0.15 at (4.53, 6.7, 1.85) - the kitchen hood outlet.
- A thin black cable runs diagonally across the wall from the street gate's head up to the front eaves.
- **Neighbour's wall**: weathered London stock in Flemish bond, sampled #A3A1A7-#ADA7A2, true #A39A86; two
  terracotta air bricks at z 0.9 and 1.2 around y 4-5; a white cable sagging along it at 1.5-2.0; a bulkhead light
  at its north end. Massing and texture only.

### 2.9 Street gate (v8 f_0067, f_0080-f_0084; v11 f_0106-f_0125) — not in the model

- Plane at **y 1.37**, between a 0.075 post on our wall and a 0.10 post on the neighbour's wall: 0.95 wall to wall.
- Leaf **0.78 wide x 1.34 high** (the owner stoops through it: the camera is at 1.05-1.15 in these frames), framed,
  ledged and braced like the garden gate ("<" seen from inside with hinges on the left). Three galvanised tee
  hinges with 0.35 straps on the inside face, **on the east (neighbour's) post**; opens **into the alley** and
  lies against the neighbour's wall (f_0121-f_0125). Grey long-throw lock at 0.94, cabin hook at 0.66, on the west
  stile; a brass cylinder escutcheon on the street face at 0.94.
- **Fixed panel above**: feather-edge boards from 1.30 to 2.05, lapping 0.04 over the leaf's head on the street
  face, with a lead-grey capping strip. Street face of leaf and panel: 11 vertical feather-edge boards, 0.086 cover.
- Painted light grey, more weathered than the garden gate: sampled #A8A8AB, true #AEADAC.
- Outside it: cracked concrete at the same level out to the forecourt; a white meter box low on the neighbour's
  wall (theirs: omit) and the white meter box on our bay cheek (front unit).

## 3. Dimension table

Tolerance is my reading error on the adopted scale (section 1).

| # | item | where in house.json | present | measured | method / frames | conf. |
|---|---|---|---|---|---|---|
| 1 | passage width at the gate latch post (y 10.21) | `east_fence.line[0]`, `side_passage` polygon | 1.49 (x 4.89) | **1.58 +/- 0.06** (x 4.98) | ground plane, v13 t32; gate length agrees in v11 t63 | medium |
| 2 | width at y 12.3 | same line | 1.42 | 1.46 +/- 0.05 | v13 t32; v11 t63 slab row at the stack gives 1.48 | medium |
| 3 | width at y 13.7 | same line | 1.37 | 1.40 +/- 0.05 | v13 t32 | medium |
| 4 | width at the step (y 17.55) | `east_fence`, `side_passage`, `garden_path` | 1.25 (x 4.65) | **1.16 +/- 0.07** (x 4.56) | extrapolation of 1-3 (1.19) and two slabs across in v11 t53 (1.06-1.18) | low-medium |
| 5 | passage length, K to the step | zones | 8.52 | not re-measured | - | - |
| 6 | garden gate line | `side_gate.line` | (4.50, 9.03)-(4.90, 9.88), 0.94 long | **(4.48, 9.08)-(4.98, 10.21)**, 1.23 between post centres | v13 t32; v11 t63 gives 1.17 leaf corner to hinge post | medium |
| 7 | garden gate leaf | `side_gate.width`, `height` | 0.90 x 1.75 | **1.05** x 1.76 +/- 0.04 | v11 t63 heights (validated on the door, 2.00) | medium |
| 8 | goal-post head | lib/site `_gate` 1.95 | 1.95 | 1.97-2.00 | v11 t63 | no change |
| 9 | east fence height | `east_fence.height` | 2.0 | **1.80 +/- 0.07** | parallax v13 t32 1.82; v11 t63 1.67-1.70 | medium |
| 10 | kitchen steps | `steps.kitchen_steps` | 2 x 0.15; treads 0.30 / 0.62; to x 4.33 | 0.146 + 0.12 + cill 0.035; 0.295 / 0.61; to 4.30 | v11 t63, v13 t32 | no change |
| 11 | K wall width | `facades.kitchen_K.extent` | 3.40..4.53 | NE corner 4.50-4.58 | v13 t32, v11 t63 | no change |
| 12 | back-door frame width | `openings.d_back.width` | 0.84 | **0.79 +/- 0.03** | v11 t63 on the door-cill plane; v2 t342 aspect 0.30 x 2.68 = 0.80 | medium-high |
| 13 | back-door heights | `d_back.height`, `transom.height` | 2.04 / 2.64 | opening 2.00 (+ frame = 2.04) / 2.68 +/- 0.04 | v11 t63, v2 t342 | no change |
| 14 | cat flap | `d_back.notes` | bottom 0.19 | bottom 0.14 +/- 0.02 | v2 t342, v11 f_0003-f_0005 | medium |
| 15 | WC window outside | `openings.w_wc` | 0.34 x 0.70, sill 1.22 | frame 0.33 x 0.82, bottom **1.10 +/- 0.06**, head 1.94 | v11 t63; agrees with rear_elevation.md 5.1 | medium |
| 16 | utility window outside | `openings.w_utility` | 0.56 x 0.82, sill 1.05 | frame bottom **0.92 +/- 0.07**, head 1.90-2.05, height 0.98-1.08; width 0.62-0.75 (poor) | v11 t63 heights, v2 t342 ratio | low-medium |
| 17 | dining east windows | `w_dining_e_s`, `_n` | 0.52 x 1.17, sill 1.10 | w/h 0.47 -> 0.55 x 1.17; stone sill top 0.97 | v11 t181 (depth-corrected), t44 | no change |
| 18 | plinth height on F | lib/envelope `PLINTH_TOP` -0.08 | 0.22 | 0.19 +/- 0.02 | v11 t44, slab scale | no change |
| 19 | alley width at the street gate | `alley_neighbour_wall.line`, `side_alley` | 0.90 | **0.95 +/- 0.05** | courses 42 px (autocorr 0.54) vs 532 px, v8 t81; the same 0.95 from inside, v11 t107 | medium |
| 20 | alley width mid-way | same | 0.90 | 1.05 +/- 0.08 (floor, plinth foot to brick foot) | courses 39 px vs 580 px, v11 t83 | low-medium |
| 21 | alley mouth at the garden gates | same | 0.90 | 0.97 +/- 0.17 | v13 t32 ground plane | low |
| 22 | alley floor level | `zones.side_alley.z`, `fall` | -0.08 falling to -0.30 | **level, -0.28 +/- 0.07** | floor parallel to brick courses, v11 t83; bell-cast 0.25 above the floor at both ends, v8 t81 | medium |
| 23 | street gate position | new boundary | none | plane y **1.37 +/- 0.10** (0.63 behind the wall's front corner) | ground plane, v8 t81 | medium |
| 24 | street gate leaf, panel | new boundary | none | leaf 0.78 x 1.34, panel to 2.05 +/- 0.06 | courses, v8 t81 and v11 t107; camera at bin-lid height in v11 t112 | medium |
| 25 | alley length, street gate to K | - | - | 7.66 | 23 and house.json | - |
| 26 | condenser on E | `features.condenser_east.at` | (4.53, 8.4, 2.2) | **(4.53, 5.3, 2.35)**, 0.33 x 0.85 x 0.80; y +/- 0.5 | depth ratio along the bell-cast, v11 t126 and t83 | low-medium |
| 27 | flue on E | side_passage.py | y 7.78, grey | y 8.55 +/- 0.2, white, elbow at z 2.6 | v11 t88-t91, t126 | medium |
| 28 | inspection cover | `side_passage.notes`, side_passage.py | 0.60 x 0.80 at x 4.15..4.75, y 10.1..10.9 | 0.52 x 0.67 at x 4.41..4.93, y 10.44..11.10 | v13 t32 | medium |

Knock-on effects of 1-4 and 6: the fence line moves east by 0.09 at the gate and west by 0.09 at the step, so
`side_passage`, `garden_path`, `plot.polygon`, `side_alley` (its north-east corner) and `alley_neighbour_gate`
must follow; nothing of the house moves. Whether the fence then kinks at the step or runs on straight to the shed
(which would make the lower path 0.2 narrower than modelled beside the lawn) is the garden survey's call.
Of 19-21: the neighbour's wall face moves from x 5.43 to 5.50 (alley 0.97), with `neighbours.east` and
`plot.polygon`; the forecourt's east strip follows.

## 4. Notes per unit

**kitchen** — back door: frame 0.79 wide (clear x 3.42..4.21), sash 0.72; glass 0.525 x 0.98 from z 0.96, obscure;
cat flap bottom 0.14, 0.06 east of centre; hooded trickle vent in the top rail; three flag hinges east; brass
lever both faces at z 1.00; white cill 0.035. Memo board blank.

**side_passage** — move the louvre vent to (3.40, 10.00, 1.94); tap T2 to y 9.90, z 0.48; delete the wall box;
gully grate dark grey; inspection cover 0.52 x 0.67 at x 4.41..4.93, y 10.44..11.10 with a centre bar; second
40 mm pipe beside the low pipe, access cap on its south end. East wall: condenser to y 5.3..6.15, z 2.35..3.15,
0.85 x 0.33 x 0.80, with isolator; flue white 100 mm at y 8.55 from a 0.30 lead slate to an elbow at z 2.6 and a
0.35 terminal pointing north; two cylinder down-lights at y 3.4 and 7.0, z 2.65, lit (interaction: click to
switch, default on at dusk only); black extract grille at (4.53, 6.7, 1.85); twin conduits from the bell-cast at
y 3.5 up to 3.3 and north to the condenser; cable bundle up the NE corner. Add a camera in the alley looking
each way (the present `alley` camera looks at where the condenser used to be).

**site** — `side_gate`: post centres (4.48, 9.08) and (4.98, 10.21); keeping the hinge end of the line on the wall
at (4.50, 9.03) as `lib/site._gate` expects, the latch end becomes (4.97, 10.18); leaf 1.05 x 1.76, braces "<" from the garden, three tee
hinges, light grey #B7B6B2. New **street gate** at y 1.37 from x 4.53 to 5.50: posts 0.075 (west) and 0.10
(east), leaf 0.78 x 1.34 hinged east opening into the alley, fixed feather-edge panel 1.30..2.05 with a capping,
lock at 0.94 on the west stile; it connects `forecourt_alley_mouth` and `side_alley` and should be operable.
`east_fence`: 1.80 high, colour #8F887D, concrete posts at 1.9 centres, line from (4.98, 10.21) through
(4.56, 17.55). `alley_neighbour_gate`: bare weathered timber, not painted grey. `side_alley`: concrete, level at
-0.28, polygon from the street gate; neighbour's wall face x 5.50. Paving texture: 560-series random course.

**envelope** — east wall base: white bell-cast strip z -0.09..-0.03 over the black plinth, with a white vertical
stop at the front corner (the flank keeps its plain black plinth, top -0.11). East wall is blank: no openings.
Conduit route on F as in 2.4 (drop beside the yellow-room window, loop into the condenser). First-floor soil
branch: add the capped stub and the 50 mm pipe under it; en-suite waste as a cranked 40 mm pipe. Soil stack top
third pale grey with a cage cowl. `w_wc` exterior: frame 0.33 x 0.82 from z 1.10, reveal 0.20, stone sill block.
`w_utility` exterior: thin uPVC stub cill, reveal 0.06, frame bottom about 0.92.

**shell** — `d_back` width 0.79; if `w_wc` / `w_utility` keep their interior sills (cistern ledge 1.22, window
board 1.05), let the outside frame run lower behind them.

**front** — the alley floor at the street gate is about -0.28, so the forecourt's east strip
(`forecourt_alley_mouth`, modelled at -0.08) must either fall to that or be lower throughout; the concrete runs
out through the gate without a step (v11 f_0113-f_0117).

**garden** — fence at the step x 4.56 (path there 1.16 wide); fence colour and height as above; white box on the
fence post near y 17.2.

## 5. Open questions

1. Slab series (560 vs 600): a 4.5 % scale ambiguity on every plan length in the passage (section 1).
2. Street gate leaf height 1.34: three brick-course readings and the camera height agree, but a gate one must
   stoop through is unusual. If the courses were mis-read by a factor of 1.3, the leaf is 1.75 high and the alley
   1.25 wide; the top-down still (0.97 +/- 0.17) argues against that.
3. Alley width: 0.95 at the street gate against 1.05 mid-way - taper or error.
4. Level of the forecourt at the alley mouth relative to the ground floor (item 22).
5. Utility window outside width (0.62-0.75) and whether its frame really starts 0.13 below the inside window
   board; the same for the WC window (0.12 below the cistern ledge).
6. Positions along Y of everything on the east wall are +/- 0.5 (depth ratios in two frames, camera position
   assumed).
7. East fence beyond the step: straight on at the same convergence, or a kink.
8. Upper-floor flank windows and the eaves were looked at but not measured.
9. Dining south window glass: reads clear in v11 f_0177 (leaves show sharply) and stippled in the north one.

## 6. Frame index

| subject | frames |
|---|---|
| back door inside: glass, handle, cat flap, hinges, trickle vent, fanlight | v11 f_0001-f_0016 |
| door opening, cill, steps from above | v11 f_0017-f_0024 |
| tap, chain, low pipe and cap | v11 f_0021-f_0031 |
| WC window, louvre vent | v11 f_0026-f_0029, f_0040-f_0042 |
| paving, inspection cover, fence foot | v11 f_0033-f_0034, f_0062-f_0064, f_0162 |
| soil stack, branches, upper windows, conduit | v11 f_0035-f_0043, f_0170-f_0171, f_0177 |
| flank north half: plinth, condenser, thin pipe, tap, reel | v11 f_0044-f_0056, f_0172-f_0186 |
| fence close up | v11 f_0061 |
| garden gate, lock, hook, hinges, head rail | v11 f_0062-f_0082, f_0150-f_0167 |
| alley floor, neighbour's wall, flue | v11 f_0070-f_0075, f_0083-f_0093, f_0145-f_0149 |
| east wall: lights, condenser, vent, conduits | v11 f_0085, f_0094-f_0105, f_0126-f_0144 |
| street gate inside, lock, opening | v11 f_0106-f_0113 |
| street gate outside, panel, east-wall base and corner | v8 f_0067, f_0077-f_0084; v11 f_0116-f_0125 |
| top-down: passage, both gates, steps, alley mouth | v13 f_0028-f_0038 (stills t29, t32, t36) |

## Verification

Independent re-measurement of the twelve proposed `house.json` changes (verifier, round 3). Each item was measured
before reading sections 0-6 above, on other stills where the footage allows: v13 t31, t33, t36 (frames 32, 34, 37)
for the look-down views; v11 t62, t64, t74, t82, t106, t126, t166, t170 and v8 t81.5 for the level views. Scratch:
`reference/work/r3_passage_v/` (stills, `g*_*.jpg` gridded crops), tools with self-checks in `build/r3/passage_v/`
(`ground.py` look-down back-projection, `level.py` hand-held ground plane and heights, `rect.py` rectangle
rectification, `vz.py` vertical vanishing point). Focal length 870 px on a 1080-wide still (vanishing-point triples
on ten v11 frames give 860-910), principal point = centre.

### V0. Four systematic findings (they decide most verdicts)

1. **Look-down scale: the slabs are the 600 series, not the 560.** Section 1 fixes the scale of v13 t32 on the
   cover being a 673 x 523 product. Three references that do not depend on a product guess give a scale 6.6 % larger:
   concrete fence posts in v13 t31 are **1.88 centre to centre** (a 1.83 panel in slotted posts; 1.77 on the 560
   scale); the three 240 L wheelie bins beyond the fence are **0.55-0.59 wide** on their lid plane (0.58; 0.53 on the
   560 scale); the camera is then **0.3 above the Lavender Room sill** (7.40 above the paving; the 560 scale puts it
   0.14 below the sill). Cross-checks on the 600 scale: first-floor window head under the camera 0.95 wide at 1.9 m
   depth (house.json 0.95 at 1.84); K wall 1.07-1.10; garden-gate bottom rail 1.01 against 1.03-1.09 from the level
   view. On it the cover is 0.72 x 0.56 and the slab modules 0.61 / 0.92. Every plan length taken from v13 t32 in
   sections 2-4 should be multiplied by 1.066 (open question 1 resolves to "600").
2. **"Face K" in the look-down still was taken at the door cill; the wall face is 0.29-0.33 m north of it.** The
   upper kitchen step lies inside the door reveal: the downpipe foot, the garden-gate hinge, the end of the gate head
   rail and the riser of the upper step are all on one line 35 px (0.29 m) north of the cill line in v13 t33, and
   the level view v11 t64 gives the same 0.31 (upper tread). The gate hangs on the wall face, so every "north of K"
   distance in sections 2-4 that came from v13 t32 is 0.25-0.30 too long when applied from y 9.03. (house.json has
   the frame only 0.115 behind K: either the reveal is 0.30 deep or K is nearer y 9.12 - not settled here, see V2.)
3. **Street-gate scale: the 42 px courses are 0.6 m in front of the gate plane.** In v8 t81.5 the red pier courses
   are 61 px (pier face 1.07 m from the camera) and the pier foot is below the frame, so the camera is higher than
   1.21 m (horizon y 935 +/- 10 from the convergence of those courses); the gate ground line then lies deeper than
   1.75 m, not at the 1.55 m of the 42 px courses. With the leaf taken as the standard 0.915 x 1.83 gate that its
   aspect suggests (0.52 in v11 t106), the camera is at 1.52 m in v8 and 1.49 m in v11 t106 - the height at which
   the same walker holds it elsewhere (1.37-1.64 from near-field brick courses in v11 t82 and t126, 1.57 in v11
   t64). On the low reading the alley would be only about 4.6 m long between its gates (v11 t82: street gate 5.1 m
   away with the flue 1.35 m ahead of the camera; v11 t126: flue 0.8 m short of the garden gates). Open question 2
   resolves to "mis-read by 1.39": leaf about 1.83 high, alley about 1.2 wide.
4. **Horizon of the level view.** In v11 t64 the fence top / base pair, the gate top / bottom pair and the alley
   brick courses put the horizon at y 972-989 (camera 1.57 above the paving); the vanishing point of flank-wall
   segments (y 1049, camera 1.23) is pulled down by the falling soil pipe. Heights read from v11 t63 with the door
   opening pinned at 2.00 are therefore low for anything nearer than the door (fence, gate).

### V1. Verdicts

| id | verdict | value to use | my measurement (reference, frames, ratio, result) |
|---|---|---|---|
| passage-01 | **adjust** | line (4.50, 9.03)-(5.03, 9.96) (latch-post centre (5.03, 9.96) +/- 0.07), hingeAt (4.50, 9.03), leaf 1.05, height 1.76 | Leaf: rectified aspect 0.60 +/- 0.015 (v11 t64, corners (408,888) (580,912) (577,1330) (393,1435)) x leaf height 1.72-1.79 = **1.03-1.07**: width 1.05 confirmed. Post: v13 t33 ground plane (600 scale), K-corner arris foot to latch-post foot **0.88-0.92 north, 0.45-0.50 east**; bottom rail, hinge corner to latch post, 1.01 long; v11 t64 ground plane gives the bottom rail (0.92 N, 0.57 E), 1.09 long. The proposed 1.15 north is the distance from the door cill (1.25 on my scale, 1.17 on the 560 scale), see V0.2. X of the post is right (4.97-5.03). `lib/site._gate` puts the pivot 0.155 along the line, so a 1.07 line models a 0.91 leaf: shorten that offset (the real hinge edge is about 0.07 from K) rather than push the latch post 0.2 north. |
| passage-02 | **adjust** | fence base (5.06, 9.96) -> (4.65, 17.55); `side_passage` (3.4,9.03)(4.5,9.03)(5.03,9.96)(4.65,17.55)(3.4,17.55); `garden_path` vertex stays (4.652, 17.55). Widths 1.66 at the gate, 1.57 at y 12, 1.49 at y 13.5, 1.25 at the step | v13 t33, fence base to the outer edge of the first-floor soil pipe (robust to the nadir within 0.01): 1.54 / 1.47 / 1.42 at 1.1 / 2.7 / 4.3 m north of K, plus 0.125 from that edge to the flank face (located by the door frame, east jamb + 0.79) = **1.67 / 1.59 / 1.54** (+/- 0.06). The 1.59 / 1.46 / 1.40 of items 1-3 x 1.066 = 1.69 / 1.56 / 1.49: same picture, other scale. At the step the count is two slabs across (v11 t52-t56): 2 x 0.61 = 1.22-1.25 on the 600 series, i.e. the **present** 1.25, not 1.16. Only the gate end moves (+0.15); the latch post stands about 0.07 inside the fence line. |
| passage-03 | **reject** | keep 2.0 | v13 t31 parallax of two concrete posts on the 600 scale: tops **2.02-2.10** above the paving (1.90-1.97 even on the 560 scale). v11 t64 with the horizon of V0.4: board top **1.91** at the gate end and 1.90 two metres north; gate head rail 2.05, leaf top 1.84 in the same frame. The 1.67-1.70 came from the low horizon. Best estimate boards 1.93 +/- 0.07, posts 2.03: inside tolerance of the present value. |
| passage-04 | **accept** | width 0.79, frame x 3.42..4.21, center (3.815, 8.88), hingeAt (4.21, 8.88) | v11 t166 (door open, near-frontal, a different still): clear opening rectified on its own plane, w/h **0.332** (f 840-900: 0.3315-0.3335, orthogonality error 0.8 deg). With the clear height 2.00 the frame top comes out at 2.638 (house.json 2.64), which fixes the scale; clear width **0.665**, frame members 0.055-0.06 -> frame **0.78 +/- 0.03**. Look-down (v13 t33): door east jamb to the K arris 0.29-0.31, so 3.40 + 0.02 + 0.79 + 0.29 closes on 4.50. Notes: the cat flap is **centred** in the lower panel (v11 f_0005: panel bead 350 px, flap 160 px, same centre; v13 t33: flap centre on the frame centre) - do not offset it 0.06; bottom about 0.14 is plausible. |
| passage-05 | **adjust** | gate exists, hinged on the east post, opens into the alley; but leaf **0.92 x 1.83**, fixed panel above to **2.75**, wall to wall **1.20**, plane y **1.6 +/- 0.15**; line (5.75, 1.6)-(4.53, 1.6), hingeAt (5.75, 1.6) | See V0.3. v11 t106: leaf 480 x 925 px, aspect 0.52 = a 3 ft x 6 ft gate; wall to wall 572-585 px = 1.13-1.16; course period at x 300 of that frame 45-50 px, predicted 45 px for a 1.83 leaf and 62 px for a 1.34 leaf. v8 t81.5: leaf 720 px high, opening 498 px (1.27 if the leaf is 1.83), panel top (1530 - 455) / 393 = 2.74. v11 t82 far view: assembly 155 x 340 px, leaf 225 px -> panel top 2.77, width 1.20. Ring latch then at 1.00 and lock at 1.38 (0.71 / 0.99 on the low reading). Plane: 0.8-0.9 m behind the front corners on this scale. |
| passage-06 | **adjust** | wall face of the house across the alley at x **5.75** (alley 1.22 +/- 0.08), not 5.50 | Three brick-scaled sections with the full camera model (75 mm courses counted at the wall foot beside the section): v11 t126, courses 36 px at x 900, floor between wall feet **1.18-1.22** about 2 m north of the camera for every horizon tried; v11 t82, 9 courses at x 100 (27 px each), **1.20-1.29** 2 m south of the camera; far end of v11 t126 against the bare timber gate taken as 1.75 high, 1.31-1.34. Look-down v13 t33 (600 scale): K arris foot to the opposite wall foot **1.25-1.29** (1.02 if the arris is dropped to the door-cill line, which is the 0.97 of item 21). Street gate wall to wall 1.13-1.27 (passage-05). The 39 px period of item 20 was read above the wall foot, where the courses are 1.3-1.45 times larger than at the foot. Follow-ons: `neighbours.east`, `plot.polygon`, `side_alley`, `forecourt_alley_mouth`, `alley_neighbour_wall`. |
| passage-07 | **accept** | level, no fall, in-situ concrete; z **-0.30** (flush with `side_passage`; the proposed -0.28 is the same within tolerance) | Not re-measured in absolute terms. v11 t82 and t126: floor line and bell-cast strip stay parallel over the whole visible length and the floor is cast concrete with patches. Paving at the back door from the steps in v11 t64: risers 0.17 + 0.13 + cill 0.04 = **0.33-0.345** below the threshold whatever horizon is used, so -0.30 stands (+/- 0.04). The step from the forecourt strip (-0.08) is still not established. |
| passage-08 | **adjust** | bare weathered timber gate, flat capped top, 1.75 high: accepted; line (5.03, 9.96)-(5.75, 9.5) | Material and form confirmed in v11 t126 / f_0127 and v13 t33. The line follows the adjusted latch post (passage-01) and wall face (passage-06); its far end is +/- 0.3 in y (v11 t126: projected widths of our opening and of that gate 0.49 and 0.54-0.60 at 134 px/m). |
| passage-09 | **accept** | (4.53, 5.3..6.0, 2.35..2.6), size as proposed (low confidence either way) | Size ratios only: v11 f_0127, unit 145 px high against the far gate 170 px (1.75 m) -> 47-53 % of the way from the camera to the garden gates, y 5.5-6.5; v11 f_0041 from the passage, unit 85 px -> 4.8-5.5 m from the camera, y 5.5-6.2, underside on the sight line over the gate head rail, 2.8-3.2 above the alley floor. Centre of my estimates y 6.0, z 2.6; both inside the tolerance stated for the proposal. The present y 8.4 is where the white flue stands, not the condenser. |
| passage-10 | **accept** | exterior frame 0.34 x 0.82, sill 1.10 | v11 t64 with the camera 1.57 above the paving and the window 3.2 m away: sill-block top **1.08**, recess head **1.85-1.92** above FFL (+/- 0.07). Keep the interior ledge at 1.22. |
| passage-11 | **accept** | sill 0.92, height 0.98 as proposed; exterior frame width **0.70** rather than 0.56 | v11 t170, frame rectified: w/h **0.714 +/- 0.02** (phase 2 had 0.66 x 0.90, the same aspect), so a 0.98 high frame is 0.70 wide outside; 0.56 x 0.98 would look wrong. Relative to the south dining window on the same wall (level lines through the vanishing point of the frame): frame bottom **0.07-0.13 below** the sill-block top of that window, i.e. 0.84-1.01 for a block top of 0.97-1.08; dining recess 1.04-1.16 x the frame height, i.e. frame 1.0-1.1. The proposal sits inside both ranges; the head may be nearer 1.95-2.0 than 1.90. |
| passage-12 | **adjust** | cover **0.56 across x 0.72 along**, x 4.44..5.00, y 10.25..10.97, against the fence, centre bar and lifting slot; paving **600 series** (900 x 600, 600 x 600, 600 x 290, joints 12-15 mm) | v13 t33 and t31 give the same 0.72 x 0.56 (aspect 1.27-1.29) on the 600 scale of V0.1; south edge 1.22 and north edge 1.94 north of the K face (not of the door cill); east edge 0.04-0.09 from the fence base, which is at x 5.03-5.05 there. A slab with all four joints visible reads 0.62 x 0.96. |

### V2. Knock-on checks

- **Along X at the gate**: 3.40 + 0.02 + 0.79 (door frame) + 0.29 (downpipe strip) = 4.50 (K corner); + 0.53 (gate, east
  component) = 5.03 (latch post); + 0.72 = 5.75 (wall across the alley). Passage 1.63-1.66 wide there, alley 1.22.
- **Fence**: bays of 1.88 between concrete posts; the last bay to the timber latch post is 1.97 centre to post foot.
- **Levels**: paving 0.33-0.345 below the back-door threshold (v11 t64), alley flush with it: -0.30 holds; no riser
  count changes.
- **Not settled**: (a) whether K is at y 9.03 with a 0.30 deep door reveal or at about y 9.12 with the frame where it
  is (the kitchen north wall would be 0.39 thick); all y values above are measured from the wall face and applied
  from 9.03. (b) The fence between y 14 and the step was not measured in metres, only the slab count at the step.
  (c) The step from the forecourt (-0.08) down to the alley floor (-0.30). (d) The wall across the alley may run
  0.05-0.10 out of parallel (1.19-1.22 at y 4, 1.25-1.3 at the garden end); one value is used.
- **Confidence**: the 600 / 560 decision rests on the fence bay, the bin width and the camera height against the
  catalogue size of the cover; if it were 560 after all, passage-01, -02 and -12 revert to the X values of section 3
  (the Y correction of V0.2 stands either way). The street-gate and alley verdicts rest on brick courses read at
  the wall foot in two frames plus the standard size of the gate and the alley-length argument; no frame shows the
  street-gate leaf and a brick course in one plane.

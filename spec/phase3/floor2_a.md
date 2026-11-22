# Phase 3 survey — floor2_a: second-floor hallway, Lavender Room (`purple_room`), bathroom with sauna (`bathroom2`)

Footage read: v13 f_0001–f_0129 (every frame, as 3-up montages, plus about 70 full-resolution stills), and the
phase-2 level stills of v4 (t 383, 389) and v5 (t 2) again for the measurements. Scratch: `reference/work/r3_floor2_a/`
(`hr_v13_<t>.jpg` = still at t seconds, frame f = t + 1; `*_g_*.jpg` gridded crops; `p2_*.jpg` copies of phase-2 stills),
tools and model previews in `build/r3/floor2_a/` (`tools.py`, `hom.py`, `model_*.jpg`; previews tagged `r3floor2a`).

Two things about the footage that every reader of v8–v13 should know:

- **The videos are HDR (HEVC 10-bit, BT.2020, HLG).** A plain `ffmpeg … -q:v 2 out.jpg` still is flat and
  desaturated, so colours sampled from such stills (and from the 1 fps frames) are wrong. Colours below were taken
  from frames decoded to scene-linear light (inverse HLG, BT.2020 → BT.709) — `tools.py linimg / view`.
- v13 is rectilinear but very wide and usually pitched down 25–60°. Lengths were therefore taken either (a) from a
  plane homography fitted to the bathroom floor-tile lattice, or (b) in the level v4 stills by ratio inside one plane.

## 1. What the survey changes (summary)

| # | finding | present | measured | confidence |
|---|---|---|---|---|
| 1 | Bathroom depth (south wall tiles → north wall) | 2.20 | **2.04 ± 0.04** | medium-high |
| 2 | Wall between Lavender Room and bathroom = the arch wall | 0.30 thick | **0.16 ± 0.02** | medium-high |
| 3 | Bathroom door leaf | 762 | **686** (clear 0.69) | high |
| 4 | Hallway width, stairwell corner → Rose Room door | 0.87 / 0.95 with a 0.08 step at the arch | **0.97 ± 0.03, one straight east wall** | medium-high |
| 5 | Arch: east jamb | flush reveal | **nib 0.07 proud, 0.16 thick**, clear 0.90, semicircle | medium-high |
| 6 | Lavender window, lower light | side-hung on the south jamb | **top-hung, opens out at the bottom** | high |
| 7 | Lavender window | 0.75 wide, transom bar 1.60 | **0.82 ± 0.04 wide, transom bar 1.50 ± 0.04** | medium |
| 8 | Sauna cabin | 1.33 × 0.88 × 2.02 | **1.366 × 0.753 × 2.02** (maker's size) | high |
| 9 | Shower tray | 1.20 × 0.80 | **≈ 1.10 × 0.76** (visible 1.07 × 0.75) | medium |
| 10 | Bathroom fittings along the south wall | — | all ≈ 0.10 further west, vanity plinth 0.30 deep | medium-high |
| 11 | Lavender radiator | 9 thin columns, 0.43 × 0.60 | **7 chunky round-topped sections, 0.52 × 0.45** | medium-high |

Confirmed and left alone: ceiling 2.60 in the hall and Lavender Room, dado top 0.98–0.99, Lavender Room width
1.95 ± 0.05 (present 1.91), Lavender door 610, Rose Room door 686 (clear 0.70), arch crown 2.14 ± 0.03 (present 2.17),
bathroom length 2.71 ± 0.04 (present 2.70), newel / handrail colour, sauna height.

## 2. Method notes

**Floor-tile lattice (bathroom).** The floor tiles are 600 × 300, long side east–west, laid in rows with *irregular*
stagger. Rows are named by the long joints J0 … J3 from south to north (300 apart); x is measured east from one
short joint ("a") in row J1–J2. Homographies were fitted by least squares (rms 4 mm) in two near-top-down stills,
t 103 (from inside the sauna) and t 123 (from the shower), and a rougher one at t 108 (at the door, rms 11 mm). The
three agree: vanity west leg (−86, −115) / (−92, −117); row offsets 133 / 146 and 356 / 380; door-leaf free edge
x −727 / −728; sauna south-west corner (−162, 809) / (−162, 818); tray front edge y 864 / 852–869. Scale checks: tile
aspect from the homography 0.95–0.98 of 2 : 1; vanity 0.57–0.59 wide (a 600 unit); bathroom scales 0.27 square;
WC pan foot 0.64 from the wall (pan front ≈ 0.69); door leaf 0.692 long. Lattice → room: south wall tile face at
y = −419, door-lining plane (west wall) at x = −1420.

**Sauna size.** Phase 2 read the maker as Oceanic and measured 1.33 × 0.88 × 2.02. The maker's one-person indoor
Finnish cabin is listed at 1366 (L) × 753 (D) × 2020 (H) mm (oceanic-saunas.co.uk, model "1020"): length and
height match what phase 2 measured independently, the depth does not — 0.88 was the room depth less the sauna-front
position, both of which the lattice now corrects. A top-down still into the cabin (t 86) gives interior depth ≈ 1.1 ×
the door opening, i.e. ≈ 0.68 inside, which also fits 0.753 outside and not 0.88.

**Level stills (hall, Lavender Room).** v4 t 383 looks north along the hall with a level camera. In the plane of the
arch wall's south face the scale is 407 px/m from the top of the adjacent door architrave (2.066); it reproduces the
ceiling (floor → cornice 2.50, + cove 0.10 = 2.60) and the dado top (0.98). v4 t 389 looks east in the Lavender Room;
the east wall is frontal, scale 300 px/m from floor → cornice (2.48–2.50).

## 3. Dimension table

World frame of the brief. "Local" = bathroom frame, origin at its south-west inside corner, x east, y north.

| item | where in house.json | present | measured (tolerance) | method / frames | conf. |
|---|---|---|---|---|---|
| Hall width at the arch (south side) | `landing2_head` polygon east edge x 0.22 | 0.87 | 0.987 (± 0.03) | v4 t 383: west wall x 404 px → east wall x 806 px at 407 px/m | med-high |
| Hall width at the Rose Room door wall | same, x 0.30 | 0.95 | 0.98 (± 0.04) | v4 t 383: 235 px at 239 px/m (scale: door opening 1.99) | medium |
| Hall width vs platform width | — | 0.87 / 0.80 | ratio 1.195 → 0.96 with a 0.80 platform | v5 t 2 top-down, far end | medium |
| Step in the east wall at the arch | polygon jog 0.22 → 0.30 | 0.08 | none: the pier between the two doors is one flat face | v13 f13–f17 | high |
| Arch clear width | `a_landing2.width` | 0.87 | 0.918 (± 0.03) | v4 t 383 | med-high |
| Arch east nib projection | — (new) | 0 | 0.069 (± 0.015) | v4 t 383: 28 px | med-high |
| Arch wall thickness | `w_arch2.thickness`, `landing2_arch.thickness` | 0.30 | 0.16 (± 0.02) | nib west face = 2.03 × an architrave (70–80 mm), v13 t 16; both door architraves butt it and rise past the springing | med-high |
| Arch crown | `a_landing2.crown` | 2.17 | 2.14 (± 0.03) | v4 t 383 | keep |
| Arch springing | `a_landing2.springing` | 1.74 | 1.68–1.72 (crown − half the clear width; the curve fits a semicircle r 0.46) | v4 t 383 | medium |
| Dado rail top | room spec | 0.99 | 0.98 (± 0.02) | v4 t 383 on the nib | keep |
| Hall ceiling | `ceilingZ` | 2.60 | 2.60 (± 0.03) | v4 t 383 | keep |
| Rose Room door clear width | `d_study.width` | 0.686 | 0.70 (± 0.02) | v4 t 383: 168 px at 239 px/m | keep |
| Lavender door leaf | `d_purple.width` | 0.61 | 610 (opening aspect 3.2 after pitch) | v13 t 42 | keep |
| Lavender door → north wall | `d_purple.center` | clear N edge 0.10 from the wall | 0.08–0.10 | v13 t 11, t 42; phase 2 | keep |
| Lavender Room width N–S | `purple_room` polygon | 1.91 | 1.95 (± 0.05) | v4 t 389: corners at x 318 and 902 px (the S-E corner is a faint tonal edge left of the A/C) | keep |
| Lavender Room length E–W | polygon x 0.32 … 3.10 | 2.78 | 2.68 by the hall change (old 2.78 ± 0.12 allows it; camera → wall 2.88 ± 0.2 from the hall side of the door) | — | medium |
| Lavender window width | `w_purple.width` | 0.75 | frame 0.85, board 0.85, reveal behind the curtains ≈ 0.82 (± 0.04) | v4 t 389: frame 237 px at 279 px/m (frame 0.22 behind the wall face); ratio to radiator agrees in v13 t 19 | medium |
| Lavender window centre | `w_purple.center` y 10.25 | centred | 1.02 from the N wall of a 1.95 wall → y 10.19 (± 0.04) | v4 t 389 | medium |
| Lavender window transom | `w_purple.transomBar` | 1.60 | 1.50 (± 0.04): bar at 48–49 % from the top of the frame | v4 t 389, v13 t 19 | medium |
| Lavender window sill / head | `sill` 0.76, `height` 1.42 | — | sill 0.78, reveal height 1.41 | v4 t 389 | keep |
| Lavender lower sash | `w_purple.sashes[0]` | side_hung, hinge south | top-hung on friction stays, bottom pushed out, brass handle on the bottom rail | v13 f25–f27, f39–f40 | high |
| Bathroom door leaf | `d_bath2.width` | 0.762 | 0.686 (clear 0.69 ± 0.02) | lattice t 108: threshold 0.65 + leaf 35; leaf 0.692 long in t 108 and t 123 | high |
| Bathroom door from the south wall | `d_bath2.center` | 0.07 | clear opening starts 0.05 north of the tiled south wall | lattice t 108 | medium |
| Bathroom depth N–S | `bathroom2` polygon | 2.20 | 2.04 (± 0.04) = 1.23 (sauna front) + 0.753 + 0.055 gap = 1.28 (tray edge) + 0.76 | lattice t 103, 108, 123; maker's depth; dark slot behind the cabin in t 120 | med-high |
| South wall → sauna front | room spec 1.32 | 1.32 | 1.23 (± 0.02) | lattice, two frames (809, 818 north of J1) | high |
| South wall → tray front edge | room spec 1.40 | 1.40 | 1.28 (± 0.02) | lattice, two frames | high |
| Bathroom length E–W | polygon x 0.40 … 3.10 | 2.70 | 2.71 (± 0.04) = 1.258 (sauna west face) + 1.366 + 0.08 gap | lattice + maker's length + phase-2 gap | keep |
| Sauna cabin | room spec | 1.33 × 0.88 × 2.02 | 1.366 × 0.753 × 2.02 | maker; see section 2 | high |
| Shower tray | room spec | 1.20 × 0.80 | visible 1.07 × 0.75 → an 1100 × 760 tray | lattice t 108, t 123 | medium |
| Shower west wall | — | flush with the door wall | boxed out 0.11–0.12 (marble slab face) from the door architrave to the north wall | lattice t 108: slab −1312, door plane −1420 | medium |
| Vanity | room spec x 1.43 … 2.03, 0.38 deep | — | local x 1.33 … 1.92, plinth 0.30 deep | lattice t 103, t 123 | med-high |
| Towel radiator | room spec x 0.85 … 1.35 | — | local x 0.76 … 1.29 | lattice t 123 | medium |
| Bathroom window centre | `w_bath2.center` y 12.48 | S wall + 0.98 | S wall + 0.91 (north jamb level with the sauna front, reveal 0.64 not re-measured) | chain | medium |
| Bathroom ceiling | `ceilingZ` 8.49 | 2.47 | not re-measured (cabin 2.02 + ≈ 0.3 to the cove fits) | v13 f77–f79 | keep |

Not measurable from this footage: absolute Y of anything on this floor (see open question 1), the bathroom window
size, the Lavender reveal depth (0.22–0.28).

## 4. Proposed geometry (one consistent set)

Anchor: the Lavender Room and its door stay where they are (they stack on the first floor and nothing new moves
them); the hall end wall (y 12.94) and the Rose Room stay.

- Hall east wall: one line, face x **0.32** from (0.32, 8.73) to (0.32, 12.94). `landing2_head` polygon:
  (−0.65, 8.13) (0.15, 8.13) (0.15, 8.73) (0.32, 8.73) (0.32, 12.94) (−0.65, 12.94). `w_hall_purple` and
  `w_hall_bath2` centreline x 0.37 (0.10 thick). Room west faces x 0.42.
- Arch wall `w_arch2` and room partition `w_purple_n`: one wall, faces y **11.20 … 11.36** (centreline 11.28, 0.16).
  East nib of the arch: x 0.25 … 0.32, y 11.20 … 11.36, full height below the springing; dado rail and skirting
  return round its three faces. Clear arch x −0.65 … 0.25 (0.90), centre x −0.20, crown 2.17, springing 1.72.
  West side: the arch dies into the party wall, no nib.
- `purple_room`: x 0.42 … 3.10, y 9.29 … 11.20 (2.68 × 1.91). `d_purple` unchanged in y (clear 10.49 … 11.10), wall
  centreline x 0.37.
- `bathroom2`: x 0.42 … 3.10, y **11.36 … 13.40** (2.68 × 2.04). `d_bath2`: 686, clear y 11.41 … 12.10, centre
  (0.37, 11.755), hinge south, hingeAt (0.37, 11.41).
- `w_bath2_study`: y 13.40 … 14.15 (0.75) — see open question 2.
- `bath2_pipe_boxing`: x 2.98 … 3.10, y 11.36 … 11.95. `bath2_niche`: x 0.90 … 1.50, y 13.40 … 13.50. New boxing
  on the west wall of the shower: x 0.42 … 0.54, y 12.19 … 13.40, full height, faced with the marble slab (the
  mitred external corner beside the door architrave).
- `w_bath2` centre y 12.27 (reveal 11.95 … 12.59); `w_purple` centre y 10.19, width 0.82, transomBar 1.50, lower
  sash top-hung.
- Pier north of the bathroom door: clear edge 12.10 → end wall 12.94 = 0.84 (was 0.61). The two double sockets
  stay at y 12.56 / 12.78 and switch S3 at 12.68.

## 5. Inventory — what the footage shows against the model (previews `build/preview/*_r3floor2a.jpg`)

### Hallway and stair head (`landing2_head`, `landing2_platform`; unit `stairs2`)
- **Arch nib** (above): the model has a flush east jamb. The pier between the two doors is the nib's west face
  (0.16 wide) with a dado-rail piece mitred and returned at both ends and a skirting block with returns; the door
  architraves stand on the east-wall plane either side, 0.07 behind it (v13 f12–f17, t 16 is frontal).
- Hall 0.10 wider: everything on the east wall moves 0.10 east (switch S1, painting E1, socket, door sets, pier
  sockets, S3).
- **Cat drawings**: N1 (sitting black-and-white cat) is on the stairwell's north wall; **N2 (lying tabby) is on the
  stairwell's east wall** just round the corner, about 0.35 lower, not on the north wall (v13 f5–f6, t 4). Both
  0.45 × 0.35, narrow brushed-gold frame, white mount with a dark red-brown line. Dado rail runs level on the
  north wall and rakes down the east wall from the corner.
- Wall below the dado reads darker and warmer than modelled: luminance 0.45–0.55 of the white above it in linear
  light (v13 t 4, t 7; model 0.64). Sampled (camera white balance) #C4B19C, normalised to the wall above #BFB5A8 /
  #BCB8AC; estimate under neutral light **#C0B9AD** (present #C8C5BB). It is the ground-floor hall paint, so change
  both or neither.
- Newel #37211E against the white wall (present #3B211A — keep). Carpet as present.
- Confirmed in place: W1, W2 (generic papyrus), W3, W4, E1, two ceiling discs, platform step with the dado /
  skirting kink, skylight, loft door open, brass thresholds. A white plug-in sits in the east-wall socket (omit).

### Lavender Room (`purple_room`)
- **Wall colour.** Linear-light samples, camera white balance, equal brightness: #B5B4C4 (reveal), #BCBFC4 and
  #BFBCC4 (west wall), #AAA9C4 (north wall), #C0B5C4 (east wall, back-lit); normalised to the skirting next to it
  #B8B7C8 with luminance 0.54 of the white. Estimate under neutral light **#B9B5C6** (LRV ≈ 47 %): a pale grey
  lavender, slightly lighter and less saturated than the present #B4AFC6. The published still looks darker and
  more purple only because of the 3000 K bake.
- **Window**: lower light top-hung (opens out ≈ 30°, stays on both jambs, two keeps on the sill member, brass
  espagnolette handle centred on the bottom rail); upper light fixed with a white trickle vent; transom at
  mid-height; frame 0.82–0.85 wide. Oak board about 0.85 × 0.27, 30 thick, rounded nose, small horns (camera
  #C4926D, true ≈ #B58A5E).
- **Radiator**: white sectional radiator with seven wide round-topped sections at ≈ 73 mm pitch, 0.52 wide × 0.45
  high × 0.10 deep, bottom level with the skirting top (z 0.17), top at 0.62, 0.09 under the board; valves at the
  south end low. Centred under the window (v13 f20–f24, v4 t 389).
- **Curtains**: eyelet heading on the pole (folds wrap the pole), off-white ground, very large dusty-rose peony
  heads 0.20–0.25 across, two to three per curtain width, with long sage and grey-green leaves; gold rope tie-backs
  with tassels at z ≈ 0.88; hem ≈ 0.30 above the floor. The model's motif is about half that size.
- **Pole**: mid-brown wood (≈ #8B5E3C, satin), not near-black; Ø 30–35, ball finials; 1.60 tip to tip (0.17 from
  the north wall to 0.155 from the south wall at 300 px/m, v4 t 389), on the window centre. To clear it the
  **A/C unit sits 0.25 from the east wall** (its east end is beside the finial, v13 f19; present 0.05).
- West wall: remote cradle and one-gang dimmer side by side at z ≈ 1.25–1.35, 0.10–0.20 south of the architrave;
  double socket at z 0.33, centre 0.74 from the south wall (by the 146 mm plate; ± 0.08). North wall socket and
  south wall twin plate as present.
- Carpet as present (camera #C4C2C0 → ≈ #BDB9B2). Room still unfurnished; the Chippendale chair may stay.

### Bathroom (`bathroom2`) — local frame, room 2.68 × 2.04
- **Layout** (replaces the positions in `bathroom2.md`): door clear y 0.05–0.74, leaf parks on the south wall with
  its free edge at x 0.69; towel radiator x 0.76–1.29; vanity x 1.33–1.92, plinth 0.30 deep, basin to ≈ 0.45;
  WC unit x 1.92–2.35, pan centre ≈ x 2.10–2.14, pan front y 0.69; tall cabinet x 2.35–2.68, y 0–0.30; boxing on
  the east wall y 0.30–0.59; window reveal y 0.59–1.23; shower boxing x 0–0.12 for y ≥ 0.83; tray x 0.12–1.19,
  y 1.28–2.04; strip 0.07; sauna x 1.26–2.62, y 1.23–1.98 (0.055 clear of the north wall, 0.06–0.08 of the window
  wall); bath mat 0.90 × 0.53 at x 0.31–1.22, y 0.73–1.26.
- **Sauna**: 1.366 × 0.753 × 2.02. Front: corner post + boarded panel ≈ 0.62 (five boards ≈ 100 face), glass door
  0.60, post 0.13; flat capping ≈ 90 high oversailing 20; base batten 45. Door: grey glass, two chrome hinges on
  the east edge, handle = vertical chrome cylinder Ø 30 × 0.25 outside and a timber bar inside at z ≈ 1.0.
  Inside (≈ 1.28 × 0.66): **the bench runs the whole depth along the east wall**, 0.50 wide, seven slats running
  north–south, top z ≈ 0.45 (the model has a small corner seat); three-slat backrest on the east wall z ≈ 0.80–1.10;
  one horizontal batten on the north wall above the bench (z ≈ 0.80, bench width); heater on the west wall, mid
  depth, 0.40 long × 0.25 deep, rocks at z ≈ 0.75, inside a timber guard of two rails on corner posts; timber
  sliding vent 0.25 × 0.10 on the north wall at z ≈ 1.75, **centre ≈ 0.40 from the north-east corner** (present
  0.86); white slotted sensor / vent 0.05 × 0.08 on the east wall at z ≈ 1.80; round chrome-bezel thermometer on
  the front wall east of the door at z ≈ 1.75; coved timber fillets at the ceiling; dark grey mat on the floor
  (≈ #6E6F6E); bucket and ladle on the bench. Boards outside: camera #C49A77 → ≈ #D2B48A (present fine).
- **Vanity** doors are shaker (flat recessed panel), two doors, dark bronze vertical bar handles 0.10 long — not
  V-grooved. **WC unit** front has vertical V-grooves; **tall cabinet** side is a plain flat panel (the model has
  the grooves on the wrong pieces). Glass soap dish in a chrome ring left of the tap, white double toothbrush
  holder right of it (v13 t 106).
- **Shower**: large round chrome rain head Ø ≈ 0.25–0.30 on a swan-neck riser, black-faced hand shower on the
  riser, exposed thermostatic bar valve, chrome wire basket; sliding leaf handle is a square-section brushed bar
  ≈ 0.30 long; rail clamps to the fixed glass return panel beside the sauna; niche with a polished steel frame.
- **Toilet-roll holder**: antique brass with a domed, embossed hood (model: chrome). Toilet brush: brushed steel
  cylinder. White pedal bin (declutter).
- **Window**: reveal head and jambs are **white**, not wall grey; marble-effect tiles return on both jambs up to
  the dado line; white quartz sill; fanlight handle brass-coloured, trickle vent in the head.
- **Extractor fan**: white square louvred wall fan ≈ 0.15 on the east wall above the window head, z ≈ 2.27,
  slightly south of the window centre (v13 f78, t 77). The ceiling grille of phase 2 was not seen in v13.
- **Wall paint**: cooler than modelled — against the white ceiling #BBC0C0 at luminance 0.58 (t 77, daylight side);
  estimate **#B5B8B8** (present #B9B7B1). Low confidence: the spots are on and bias other samples warm.
- Floor tile camera #C3C4C2 (present fine); bath mat cool grey #ABBBC4; towel radiator #191A1B; vanity #C1BFBD in
  shade (present fine). Floor bond is irregular (offsets 0.13–0.38 between rows), not a regular third bond.
- A white power-supply box and cables lie on the cabin roof (optional).

## 6. Open questions

1. **Absolute Y of the Lavender / arch / bathroom group** (± 0.15). Only relative chains are measured. The proposal
   keeps the Lavender Room and the hall end wall and so stretches the pier north of the bathroom door from 0.61 to
   0.84; my own reading of v5 t 2 (socket spacing as scale) gives 0.80–0.90 for that pier, phase 2 gave 0.56, and
   v13 t 50 (blurred) looks short. If the pier is 0.61, the whole group — Lavender Room, its door, the arch wall,
   the bathroom — moves 0.23 north instead and the solid zone south of the Lavender Room grows to 0.79.
2. **The 0.75 m between the bathroom's north wall and the Rose Room.** With the bathroom 2.04 deep and a thin arch
   wall, the unseen zones on this floor total about 1.3 m instead of 0.7 m. Either the Rose Room is deeper or its
   neck shorter than modelled (floor2_b), or there is a duct / old chimney, or the Lavender Room is wider than
   1.95. Check against the flank elevation: second-floor window centres should be **2.08 apart** (present 2.23).
3. Gap behind the sauna (0.055) and the tray depth (0.76) are a consistent pair, not two measurements; a 0.70 tray
   with the cabin tight to the wall (room 1.98) or a 0.80 tray with a 0.10 gap (2.08) are the limits.
4. Lavender Room length 2.68 follows from the hall width; it was not measured directly.
5. Bathroom window size and sill, the pipe-boxing width and the tall-cabinet depth share 1.23 m on the window
   wall and were not separated (cabinet 0.30 + boxing 0.29 + reveal 0.64 is the split used).
6. Sauna door position along the front (± 0.05), sand timer and cabin light (not seen in v13).
7. Arch crown 2.14 against 2.17 and the west springing detail: within tolerance, left alone.
8. Bathroom wall grey and the hall dado-zone colour: estimates from mixed daylight and spotlights.

## Verification

Verifier pass (floor2_a_v). Each item was measured again before the notes above were read; scratch stills in
`reference/work/r3_floor2_a_v/` (`hr_<video>_<t>.jpg`, gridded crops `*_g_*`, enhanced `*_e_g_*`), scripts and log in
`build/r3/floor2_a_v/` (`geo.py` + `test_geo.py` GEO OK, `hall_v4_384.py`, `hall_v13_6.py`, `chain.py`, `verify.log`).
Method: sub-pixel straight-edge fits, vanishing points, calibrated back-projection of floor and wall points (principal
point at the image centre; f 865 +/- 60 px for v4 / v5 from phase 2, 889 px for v13 from its own vanishing points).
Rulers: the dado (top 0.98, lower edge 0.925), 86 mm socket plates, door leaves 1981 high, 300 mm tile rows.

**Summary.** The sizes the survey found are right: hall 0.97 wide with a small nib at the arch, arch wall 0.16,
bathroom door 686, cabin about 0.75 deep, bathroom 2.04 deep, lower sash top-hung, window wider with its bar at 1.50.
**The placement along Y is not.** The proposal keeps the Lavender Room where it is and lets the pier north of the
bathroom door grow to 0.84 and the solid zone behind the bathroom to 0.75. That pier can be measured: 0.43 of flat
wall between the two architraves, 0.54 from the door's clear edge to the end wall (v5 t6, frontal; the two socket
plates on it are **single** 86 mm plates, 89 and 93 px, not doubles; the flat face is 461 px along the same row). So
the chain *end wall 12.94 - 0.54 - door 0.686 - 0.05 - arch wall 0.16* is rigid and puts the arch wall at
**y 11.50..11.66**, 0.30 north of the proposal; the bathroom then ends at 13.70 as it does now and nothing grows
behind it. Two other observations point the same way:

- v13 t6, floor projection: (arch south face -> Rose Room threshold) / (stair-head corner -> arch south face) =
  0.60 +/- 0.03 whatever the focal length; raw lengths 1.42 and 2.37 (the same solution makes the 0.70 Rose Room
  opening 0.63-0.67, so about 1.5 and 2.5 true). Present and proposed geometry give 0.72. My placement gives 0.60
  only if the stair-head corner is 2.45 south of the arch (knock-on 2); with the corner left at 8.73 it gives 0.53.
- v11 t151 from the passage: the Lavender window stands over the first-floor window below it, 0.0-0.2 north of its
  axis (rough: jambs read to 5 px, vertical vanishing point from the house corner and the soil stack). The present
  and proposed centres are 0.22 and 0.28 *south* of that axis; 10.47 is on it. This leans on the first-floor
  window being where the model has it.

v4 t384 alone does not decide: arch south face -> end wall comes out 1.44-1.88 for f 800-950 (proposal 1.74, chain 1.44).

| id | verdict | value to use | my measurement (reference, frames, ratio, result) |
|---|---|---|---|
| floor2a-01 | **adjust** | `bathroom2` polygon x 0.42..3.10, **y 11.66..13.70**, size [2.68, 2.04] | Depth 2.04 accepted. Cabin depth checked from the inside, v13 t87 (top-down through the cabin door, nadir at the feet): floor from the back batten to the inner edge of the front sill = 0.456 x camera height, a 0.28 slipper = 0.189 x camera height, so 0.67 inside (0.63-0.72 for a nadir 16-25 deg off the axis) = 0.72-0.81 outside: 0.753, not 0.88. South wall -> cabin front 1.23 is the survey's lattice, which I did not reproduce; my tile-row count at the threshold (v13 t108.5) gives the same scale. Placement: summary; the north wall stays at 13.70. |
| floor2a-02 | **adjust** | `w_arch2`, `w_purple_n` thickness **0.16**, centreline **y 11.58** (faces 11.50..11.66); `landing2_arch.thickness` 0.16 | Thickness accepted from a different effect: v4 t384, depth of the soffit in perspective. Crown of the south arris at row 617, of the north arris at row 646, horizon 994: depth = 0.083 x distance to the arch = 0.14-0.16 (f 800-950); the jamb strip (columns 913 / 933 against the vanishing column 667) gives 0.13-0.155. Position from the chain. |
| floor2a-03 | **adjust** | `d_bath2` width **0.686**, center **[0.37, 12.055]** (clear y 11.71..12.40), hingeAt **[0.37, 11.71]** | v13 t108.5: the visible threshold spans 2.2 tile rows of 300 between the open leaf and the north lining = 0.67 +/- 0.04, + 35 mm leaf = 0.70; a 762 door would show 2.4 rows. Same scale from the tile length (338 px per 600). The Rose Room opening is 185 x 530 px in v4 t384 = 0.70. Position from the pier (0.54 to the end wall). |
| floor2a-04 | **adjust** | Accepted: hall east face **x 0.32** from the stair-head corner to 12.94, partitions centreline **x 0.37**, room west faces **x 0.42**. Changed: `purple_room` polygon **x 0.42..3.10, y 9.55..11.50** (2.68 x 1.95), `d_purple` center **[0.37, 11.095]**, hingeAt **[0.37, 11.40]**. Not the 0.17 jog: the top nosing and the platform edge go with the wall (about x 0.27, jog 0.05), see knock-on 1 | Width: v4 t384 (level), dado top 0.98 as the ruler on both sides, edges fitted to 0.2-1.0 px: west skirting -0.435, nib arris +0.490, east wall +0.541 from the camera, so clear 0.925 + nib 0.051 = **0.976** skirting to wall, the same for f 800-1050. v13 t6 (pitched 38 deg, dado lower edge 0.925): 0.87 between skirtings raw, 0.91-0.95 after rescaling on the Rose Room opening. The east wall is one straight line from the stair-head corner to the nib (v13 t6: corner 0.36, wall 0.38-0.39, nib junction 0.37-0.38 from the camera). **Stair head:** in v13 t6 the nosing line (rms 0.2 px) runs into the foot of the wall's skirting, 0.03 west of the skirting face and 0.05 of the wall, not 0.17 (seen also in v13 t5.5 and t4.5, v4 t376 and t379). |
| floor2a-05 | **adjust** (position only) | `a_landing2` width **0.90**, center **[-0.20, 11.58]**, springing **1.72**, crown **2.17**; nib x 0.25..0.32, **y 11.50..11.66**, floor to springing, dado and skirting returned; west side dies into the party wall | v4 t384, twelve points of the south arris back-projected into the plane of the wall: circle r 0.48-0.49, centre 1.72 above the floor and 0.47 from the west wall, rms 7 mm; crown 2.19-2.22; clear 0.94 from the west wall to the nib arris, nib 0.05 (28 px at 543 px/m). Inside the survey's tolerances (0.92 / 0.07 / 2.14). The nib has its own dado return and skirting block. |
| floor2a-06 | **accept** | top_hung, swing out, about 30 deg, handle bottom; upper light fixed | v13 f_0021 (brass handle centred on the bottom rail), f_0023 (hand on it), f_0025-f_0027 (bottom rail pushed out, the passage seen between sill and sash), f_0026 and f_0039 (stays on the jamb, sash hanging from the bar). |
| floor2a-07 | **adjust** (centre only) | `w_purple` width **0.82**, transomBar **1.50**, center **[3.25, 10.47]** (1.03 from the room's north wall at 11.50) | v4 t389: glass of the fixed light 217 px = 0.76-0.78 at 279-286 px/m, so the frame is 0.85-0.90 and a 0.75 reveal cannot hold it; oak board 258 px = 0.86; 0.82-0.85 behind the curtains. Bar: v4 t390.5 (level), frame rows 372..932, bar centre 640 = 47.9 % from the top, 1.50-1.52. Centre: glass axis 617.5, north-east corner 305 at mid height (it leans 2 deg), 1.05 +/- 0.04 from the north wall with the set-back of the frame allowed for (survey 1.02). |
| floor2a-08 | **adjust** | `w_bath2` center **[3.25, 12.57]** (reveal 12.25..12.89) | Not measured on its own: south wall + 0.91 as proposed (north jamb level with the cabin front: v13 t14, t59), on the moved south wall. |
| floor2a-09 | **adjust** | `bath2_pipe_boxing` x 2.98..3.10, **y 11.66..12.25**; `bath2_niche` unchanged (y 13.70..13.80); new shower lining **x 0.42..0.47, y 12.48..13.70**, full height, slab face | The slab does stand proud of the door wall, with a mitred corner beside the north architrave (v13 t108.5, t109). But by 0.04-0.05, not 0.11: its foot is 21-26 px east of the bathroom-side edge of the threshold strip at about 500 px/m (t108.5), 19-21 px in t109 where the 20 mm architrave foot takes half of it. It is the build-up of the slab lining; the lattice x of the "door-lining plane" was probably taken at the hinge side of the lining. |
| floor2a-10 | **reject** | `w_bath2_study` stays thickness 0.45, centreline y 13.925 | Follows from the placement: with the arch wall at 11.50..11.66 the bathroom's north wall is at 13.70 as now. |

Knock-on and consistency (for the reconciler):

1. **Stair head and platform.** The hall is 0.97 wide and the nosing is flush with its east wall, so the strip
   beside the well is about 0.92 wide, not 0.80: `v_head_nosing`, `o_stairs2_head`, the east edge of
   `landing2_platform` / `v_platform_well`, the balustrade and the west edge of the `stairs2` well belong at about
   x 0.27. Independent sign: the loft door leaf is a 686, not a 610 (v4 t360, rectangle aspect gives 0.66-0.69 for
   f 750-1050), and its frame fills the platform: 0.686 + linings + two architraves = 0.90. Whether the second flight
   is then 0.72 wide or the well's east wall is further east I could not settle (one attempt, v13 t4.5, was
   ill-conditioned). If the stair is not re-fitted in this round, the survey's polygon with the 0.17 jog is the
   interim, as a known artefact: a ledge beside the top step that does not exist.
2. **Stair-head corner.** Stair-head corner -> arch south face is 2.37 raw, 2.45 +/- 0.10 scaled (v13 t6); the present
   model has 2.47. With the arch wall at 11.50 the corner belongs at about **9.05**: the stair head is about 0.9 deep,
   not 0.60 (rough top-down ratio in v4 t376: head depth = 0.9-1.05 x strip width; `dims_1` found the quarter landing
   below it 1.04 deep). Until the well's north wall moves, the plain hall wall between the corner and the Lavender
   door is 0.32 too long and `w_addition_s_2` is 0.82 thick (8.73..9.55) instead of about 0.50.
3. **Sums.** X at the bathroom: 0.32 + 0.10 + 2.68 = 3.10. Y from the end wall: 12.94 - 0.54 = 12.40; - 0.686 = 11.71;
   - 0.05 = 11.66; - 0.16 = 11.50; Lavender door clear 10.79..11.40 (0.10 from its north wall); pier between the two
   door openings 0.31 = 0.08 + 0.15 + 0.08. Bathroom 11.66 + 1.23 + 0.753 + 0.055 = 13.70. Flank windows 2.10 apart
   (survey 2.08). If the reconciler moves the hall end wall (floor2_b's short neck), this whole chain moves with it.
4. Inventory by the way: the two sockets on the pier north of the bathroom door are single switched sockets, centres
   0.14 and 0.275 from the end wall (0.13 apart), not two doubles 0.22 apart.

Not settled by me: the cabin-front position 1.23 (taken from the survey's lattice), the Lavender Room's north-south
size (1.95 in the survey; my corners in v4 t389 give 2.0), the width of the second flight, the depth of the stair
head (it needs its own measurement), the bathroom window size, and every absolute Y on this floor beyond the chain
above.

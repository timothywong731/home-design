# Rear and side elevations of the house (exterior)

Scope: every outside face of the house that can be seen from the garden and the side passage — the rear
face of the three-storey back addition (face **R**), its long east flank (face **F**), the short rear wall
of the main house that holds the kitchen back door (face **K**), and what little shows of the main house's
east wall (face **E**) — with the balcony structure, pipes, gutters and roof edges. Ground plan, levels,
fences and planters are in `spec/rooms/garden.md`; the balcony as a room is `balcony` (blue-bedroom
agent); interiors decide the final size of each window, this file decides the outer faces and what the
openings look like from outside.

Source: v2:f_0171–f_0181, f_0209–f_0221, f_0249–f_0255 (face R), v2:f_0311–f_0355 (faces F, K, E from
the side passage), v4:f_0422, f_0426, f_0467 and v3:f_0260–f_0284 (from above). Stills in
`reference/work/p2_rear_ext/`: `v2_t174.jpg`, `v2_t210.jpg` (R close), **`v2_t250.jpg` (R frontal, the
metrology frame)**, `v2_t318.jpg`, `v2_t332…t342.jpg` (F, K), `c_v2_342_gap.jpg` (E), `v4_t421.jpg`,
`v4_t425.jpg`, `v4_t466.jpg`. Owner (v2 03:26–06:05): "the house is in sandstone colour … this is how the
house looks like — only one half … the soil stack, the gutter, lots of windows … cat door is at the centre,
there's a tap here, this is a kitchen door"; "a metallic balcony"; "a light here in the middle".

**Dimension confidence.** Face R, X: ±0.10 (frontal still, 94–100 px/m, cross-checked on the 2.32 m
French-door frame and the interior window spacing). Heights: ±0.05 up to 2.5 m, ±0.15 at first-floor level,
±0.25 at the second floor and roof (single scale, no independent check — the floor-level agents' numbers
should override mine where they differ). Face F, along Y: ground-floor items inherit the interior positions
from `house.json` (±0.1 relative to those); upper-floor windows ±0.4. Pipe routes are schematic.

## 1. Faces, frame, heights

World axes (BRIEF). Z = 0 is the ground-floor finished floor. Outside ground: deck −0.05, side passage
−0.30, garden −0.45.

| face | plane | extent | height | what it is |
|---|---|---|---|---|
| **R** | y = **17.36**, faces +Y (the garden) | render x −0.50 → 3.45 (3.95 wide); exposed brick pier x −0.75 → −0.50 | wall top Z ≈ 8.55, fascia top 8.72 | rear of the back addition: dining room / blue bedroom + balcony / second-floor study |
| **F** | x = **3.45**, faces +X (the side passage) | y 9.03 → 17.36 (8.33 long) | eaves gutter Z ≈ 8.45 | flank of the back addition: WC, utility, dining below; bathrooms/landings above |
| **K** | y = **9.03**, faces +Y | x 3.45 → ≈ 4.62 (1.17 wide) | eaves Z ≈ 6.05 (two storeys), slate roof slope above | rear wall of the main house: kitchen back door, a first-floor window |
| **E** | x ≈ **4.62**, faces +X | only its north end is visible past the side gate | — | east wall of the main house, facing the narrow alley (garden.md D3) |

Both reference planes differ from `house.json` (R 17.16, F 3.30): the walls are thicker than modelled — see
garden.md §1 and D1. "Only one half": the back addition is half of a pair; the neighbour's half, in
bare stock brick, adjoins on the west at the same height.

Storey levels read off face R (for cross-checking only): balcony platform top 2.9–3.1 (balcony.md: 3.00); first-floor door head
5.30–5.40; second-floor window sill ≈ 6.30, head ≈ 7.95; top of wall ≈ 8.55.

## 2. Face R — openings, floor by floor

x ranges are frame outer edges; z is above ground-floor level.

| floor | id | x | z | description |
|---|---|---|---|---|
| G | **French doors** `d_french` | 0.56 → 1.89 (frame 1.33; axis 1.225) | 0 → 2.32 | White uPVC. Two leaves 0.60 × 1.97, each with **two clear panes** (upper 0.40 × 0.88, lower 0.40 × 0.72) and a 0.10 mid-rail at z 0.88–0.98; polished-brass lever handles on long backplates on both meeting stiles, lever z 1.02. Fixed single-pane **fanlight** 1.19 × 0.24 above a 0.07 transom. Frame set **0.10 behind the render face** in a square rendered reveal 1.45 wide to z 2.40. **Round cat flap** (clear flap in a white ring, Ø 0.26 overall) in the middle of the **west** leaf's lower pane, centre z 0.42. Below the frame a **dark brown sill board** (deck board, 1.55 × 0.15 × 0.10 high) forms the step onto the deck. Both leaves **open outward**. |
| G | east side window `w_dining_n_e` | 2.25 → 2.87 (frame 0.62; centre 2.555) | 0.37 → 2.20 | White uPVC, **two lights**: upper 0.48 × 0.72 over lower 0.48 × 0.92, transom centred z ≈ 1.40. Frame 0.05 behind the render. White painted sill 0.74 × 0.06, projecting 0.04, at z 0.31–0.37. Clear glass (the dining window seat and pot show through). |
| G | west side window `w_dining_n_w` | −0.40 → 0.22 (centre −0.09) | 0.37 → 2.20 | **Identical to the east one from outside** (same size, same transom line) — confirms ground_corrections D3. Its upper light is the top-hung opener. It looks straight at the neighbour's brick wall and the trellis. |
| 1 | **balcony doors** | 0.47 → 2.11 (frame 1.64, centre 1.29 — from `blue_bedroom.md`) | 3.05 → 5.39 | White uPVC pair with two fanlights over; open outward onto the balcony. Mostly hidden from the garden by the ivy. |
| 2 | **second-floor window** (study) | 0.43 → 1.98 (1.55 wide; centre 1.20) | 6.30 → 7.95 (1.65 high) | White uPVC, four lights: two casement-size lower lights (each 0.68 × 1.12) with **two top-hung fanlights** (0.68 × 0.36) above — both fanlights stand ajar in v2:f_0173–f_0175. White painted stone sill 1.75 × 0.09, projecting 0.07. Net curtains inside. |

There are **no other openings** in face R. Margins: the east side-window frame stops 0.58 short of the
east corner; the west one stops 0.10 short of the brick pier.

## 3. Face R — wall, trim and fittings

- **Render**: painted, fine roughcast / sand-textured stucco (visible stipple at close range, v2:f_0353),
  one colour over the whole house, no quoins, bands or string courses. Arrises at openings are square with
  a small pencil round. "The house is in sandstone colour".
- **West edge**: the render stops at x ≈ −0.50 against a **full-height exposed pier of old London-stock
  brick** (0.25 of it on our side of the party line), which continues up into a shared **chimney stack**
  0.45 × 0.9 rising ≈ 1.0 above the roof line with a stone cap (v2:f_0211, f_0251). Beyond it the
  neighbour's half of the back addition: same height, bare stock brick, one sash-proportioned window per
  floor — massing only. At ground level the neighbour's single-storey extension (new yellow stock brick,
  3.0 high, flat roof) projects 2.3 m beyond face R along the boundary (garden.md §3.3).
- **Top**: plain render up to a **white fascia board** 0.20 deep projecting ≈ 0.10, capped by a dark
  (black/dark green) flat-roof edge trim; no parapet. The roof behind is flat or a very low mono-pitch
  draining to the east (flank) gutter.
- **Black conduit** (air-conditioning pipe trunking, ≈ 0.07 wide, ribbed): runs horizontally across face
  R at Z ≈ 6.0 from the east corner to x ≈ 0.15, then turns straight up to the roof at x ≈ 0.15, 0.2 m
  west of the second-floor window. It wraps round the east corner and continues along face F.
- **Lantern**: black traditional coach lantern on a short scroll bracket, 0.18 × 0.35, at x 2.33,
  Z 5.10 — on the wall at the east end of the balcony (balcony.md).
- **Floodlight**: black LED flood (0.20 × 0.16 × 0.05) with a PIR sensor under it, on the door axis at
  Z 2.50–2.66, between the fanlight head and the balcony tray.
- **Video doorbell**: black, 0.06 × 0.13, at x 2.07, Z 1.25 (0.18 east of the French-door frame). Generic,
  no logo.
- **Wall wires** for the wisteria on the east margin (x 2.9–3.4, up to Z 3.0), two small cup hooks at
  x ≈ 3.2, Z 2.75.
- No plinth is visible on face R (the deck covers the base).

## 4. Balcony structure ("a metallic balcony")

**`spec/rooms/balcony.md` is authoritative for the balcony** (it was measured standing on it). Summary in
this file's planes, plus what only shows from below; all mild steel painted black-grey, satin.

| part | geometry |
|---|---|
| platform | 2.30 wide × 1.05 projection: **x 0.00 → 2.30, y 17.36 → 18.41** (balcony.md uses the old wall face 17.16 — it moves with face R). Steel **chequer (durbar) plate** floor, top **Z 3.00** (0.05 below the blue-bedroom floor 3.05); perimeter channel fascia ≈ 0.15 deep (underside Z 2.85); flat dark soffit with two cross members. From the garden the visible width including ivy is ≈ 2.45. |
| railing | 1.10 high on the front and both sides, returning to the wall; 50 mm square posts at the outer corners and mid-front; box top rail; plain vertical bars at 0.165 centres (5 per side return, 6 per front half; verification V2, was 0.115); no infill. |
| wall posts | two flat steel channels ≈ 100 × 40 fixed to the render with a line of bolts at ≈ 0.45 centres, from deck level (Z −0.05) to the platform underside, at **x 0.21 and x 2.20** — one each side of the French-door reveal; the east one runs just clear of the east side-window frame. |
| struts | one 60 mm square tube per post, from the post at **Z 1.90** rising at 45° to the platform's front edge beam (Z 2.85, 0.95 out from the wall). |
| rain pipe (exterior only) | black 68 mm round pipe from an outlet under the platform's west side, two offset bends back to the wall, then vertical at **x 0.42** (between the west wall post and the French-door frame) down to an open shoe just above the deck (Z 0.10); three black clips. |
| planters and ivy | black trough planters hooked on the rail: **variegated ivy** pours over and hangs as a curtain to about Z 1.9 at the front corners (1 m below the platform), thinner over the middle so the French doors stay clear; purple flowers at the north-east corner. |
| lights | white icicle fairy-light strings clipped along the platform fascia, drops 0.3–0.5. |

## 5. Face F — the flank (side passage side)

One flat rendered wall, 8.33 long, three storeys, with a **black-painted plinth band 0.22 high** along its
whole foot (Z −0.30 → −0.08) and a black half-round eaves gutter on a black fascia at Z ≈ 8.45.

### 5.1 Ground floor, south → north

| item | y (centre or range) | z | description |
|---|---|---|---|
| louvre vent | 9.25 | 2.05 | white plastic louvred grille 0.15 × 0.15 |
| small white box | 9.20 | 1.30 | 0.10 × 0.07 surface box by the door (chime/junction) |
| **WC window** `w_wc` | 9.58 (house.json) | frame 1.10 → 1.92 | narrow slot: uPVC frame 0.33 × 0.82 with obscure glass ≈ 0.19 × 0.58, in a square rendered reveal 0.11 deep; white-painted (flaking) sloping stone sill 0.50 × 0.09, projecting 0.07 |
| tap T2 ("there's a tap here") | 9.80 | 0.45 | brass bib tap on a wall plate, hose-union nose; a short galvanised chain hangs from a hook 0.2 further north at Z 0.75 |
| low drain pipe | 9.7 → 12.3 | −0.25 → −0.10 | old black/grey 110 mm pipe lying along the wall foot on a low kerb, open socket (capped) at the kitchen-step end, running to the foot of the soil stack |
| **utility window** `w_utility` | 11.61 (house.json) | 1.05 → 1.95 | white uPVC single casement ≈ 0.66 × 0.90 with a slot trickle vent in the head, **obscure glass**, opens outward (owner); reveal 0.10; white stone sill 0.80 × 0.09 |
| **soil stack** | 12.35 | −0.30 → ≈ 9.1 | black 110 mm PVC with ring-seal sockets about every 2 m, standing 0.03 off the wall on black brackets; vents ≈ 0.6 above the eaves gutter (the top 1.5 m is paler grey). Branches in §5.3. |
| **dining east window, south** `w_dining_e_s` | 13.02 | 1.10 → 2.27 | tall narrow fixed light, obscure glass (ceiling spotlights glow through), uPVC frame ≈ 0.60 × 1.25, reveal 0.10, white stone sill 0.78 × 0.10 projecting 0.07 |
| air-conditioning condenser | 14.9 → 15.7 | 3.25 → 3.90 | pale grey outdoor unit 0.80 × 0.30 × 0.65 on two galvanised wall brackets, fan grille facing the passage; a small rotary isolator 0.25 to its north; a 25 mm black pipe drops from it down the wall at y 15.8 to the ground |
| **dining east window, north** `w_dining_e_n` | 16.20 | 1.10 → 2.27 | as the south one; a potted plant shows through the obscure glass |
| tap T1 + splitter | 16.55 | 0.15 | brass bib tap with a black four-way distributor and green/yellow connectors |
| **hose reel** | 16.95 | 0.75 → 1.20 | grey automatic wall-mounted reel 0.45 × 0.25 × 0.45 with yellow trim on a pivot bracket, 0.35 from the rear corner. Generic, no logo. |

### 5.2 Upper floors (approximate — interior specs take precedence)

| floor | y | z | description |
|---|---|---|---|
| 1 | ≈ 10.3 | 4.05 → 5.10 | white uPVC window ≈ 0.60 wide, lower light with a top-hung fanlight (open in the video), white stone sill |
| 1 | ≈ 11.8 | 4.20 → 5.10 | white uPVC window ≈ 0.55 wide; the black conduit makes a rectangular detour around it |
| 2 | ≈ 11.2 | 6.9 → 7.7 | small white uPVC window ≈ 0.60 wide, directly under the eaves |
| 2 | ≈ 13.2 | 6.7 → 7.6 | white uPVC window ≈ 0.90 × 0.85, single top-hung light — the purple-room window from which v4:f_0414–f_0426 were filmed |

The north third of face F above the ground floor (y 13.8 → 17.36) is blank render except for the condenser.

### 5.3 Pipes on faces F and K

- **First-floor waste run**: a black 110 mm pipe starts on face K at x ≈ 4.25, Z 3.30 (two swept bends
  under the security light), turns the internal corner and runs north along face F, falling from Z 3.30 to
  3.10, into a junction on the soil stack at y 12.35; a capped access branch stands on it at y ≈ 11.6.
- **Second branch**: a black 50 mm waste leaves the wall at y ≈ 13.4, Z 4.05 with an elbow, runs south
  falling to the stack and enters it at Z ≈ 3.45 through a swept boss.
- **Conduit**: twin ribbed black/grey conduits clipped along face F at Z ≈ 6.0–6.4 from the rear corner
  south to y ≈ 11, with the detour noted above; from above they read as two grey corrugated hoses
  (v4:f_0422, f_0467).
- **Rainwater**: black half-round gutter along the eaves of face F; a black 68 mm downpipe comes down the
  internal corner of faces F/K from the upper eaves into the pipe group above the kitchen door. A second
  black 68 mm downpipe drops from the main roof's eaves on face K at **x 4.38** to a gully beside the
  kitchen steps.

## 6. Faces K and E — the kitchen-door wall

| item | x | z | description |
|---|---|---|---|
| **kitchen back door** `d_back` | frame west edge on the F/K corner (3.47), frame ≈ 0.85 wide | threshold 0 → door head 2.07 → fanlight head 2.64 | White uPVC. Leaf: obscure-glazed upper panel (0.52 × 0.98, from Z 0.98 to 1.96) over a flat solid lower panel with a moulded frame; **white cat flap 0.22 × 0.24 centred in the lower panel, centre Z 0.33** ("cat door is at the centre"); polished-brass lever handle on the **west** stile, Z 1.02; trickle vent in the head rail. Obscure **fanlight** 0.62 × 0.42 above a transom. Hinges east, opens inward. Rendered reveal 0.08. Two sandstone steps below (garden.md). |
| security floodlight / camera | 3.95 | 3.25 → 3.50 | white unit with two round lamp heads and a camera between them. Generic. |
| pipe group | 3.5 → 4.3 | 3.15 → 3.45 | see §5.3 |
| first-floor window | 3.55 → 4.35 | 4.00 → 5.35 | white uPVC, a tall lower light with a fanlight over (transom Z ≈ 5.0), white stone sill 0.95 × 0.09; net curtain |
| downpipe | 4.38 | 6.0 → −0.25 | black 68 mm, four clips |
| gate hinge post | 4.50 | −0.30 → 1.65 | 95 × 95 painted timber post bolted to the wall (garden.md §2) |
| eaves | 3.45 → 4.62 | 6.05 | black gutter on a black fascia; dark grey natural-slate roof slope of the main house rising behind it; face F carries on up past this eaves as a gable-like wall to its own gutter |

**Face E** (east wall of the main house, in the alley): rendered and painted like the rest. Visible items
only: a second **air-conditioning condenser** on a bracket at y ≈ 8.4, Z 2.2 → 2.9, and beside it a grey
120 mm round flue/duct rising from below to a cowl at Z ≈ 3.0 (crop `c_v2_342_gap.jpg`). Nothing else of
this wall was filmed from the rear.

## 7. Roof edges as far as visible

- Back addition: flat roof (no visible covering from the ground); white fascia + dark trim on the rear
  (north) edge at Z 8.5–8.7; black gutter along the east edge at Z ≈ 8.45; party-line chimney stack at the
  NW corner. From above (v4:f_0467) the second-floor window head has a rendered drip/ledge 0.25 deep — the
  camera looks down over it — and the grey conduits run just below the sill.
- Main house rear slope: dark slate, black gutter at Z ≈ 6.05 on face K (v4:f_0422).
- Everything else of the roof (ridge, front slope, Velux, loft) belongs to the roof / second-floor specs.

## 8. Colours

| surface | sampled sRGB | estimated true colour |
|---|---|---|
| **render ("sandstone")** | open sky light #D4CBAA, #CDC599, #D3CAA3, #D4CEAF; in the shaded passage #A49B72, #9A916C | **#D2C596** pale sandstone yellow (a warm straw cream), matt masonry paint, roughness 0.9; faint green-grey weathering low down on face F |
| plinth band | #49494B (HDR-lifted) | **#2A2A2C** black masonry/bitumen paint |
| uPVC frames, doors | #D2D1CD | **#F2F2EF** white, satin |
| painted stone sills | — | #EDEDE8 white, flaking at the edges |
| pipes, gutters, conduit | — | **#18181A** black PVC, semi-gloss; old low pipe #3A3B3E |
| balcony steelwork | #17171A | **#1E1E20** black satin; chequer plate top reads **#3A3C40** |
| French-door sill board | #706865 | #4A3F38 dark brown composite |
| brass handles | — | #C9A64B |
| stock-brick pier / neighbour's addition | #ADA584 | **#A99873** weathered yellow-grey stock, mortar #8E866F, soot-darkened patches |
| slate | — | #45474C |
| condenser | — | #D8D8D4 with a dark grey fan grille |

## 9. Reference frames

| subject | frames |
|---|---|
| Face R close, ground floor + balcony underside | v2:f_0171–f_0181 (still `v2_t174.jpg`) |
| Face R with second floor, east corner, conduit | v2:f_0209–f_0213 (still `v2_t210.jpg`) |
| Face R whole, frontal, with neighbours | v2:f_0249–f_0253 (still `v2_t250.jpg`) |
| East side window and pebble planter | v2:f_0215–f_0221 |
| Balcony from above / from inside | v4:f_0467; v3:f_0260–f_0284 |
| Face F north end: reel, tap, plinth, deck junction | v2:f_0231, f_0235, f_0321–f_0325 |
| Face F windows, condenser, conduit | v2:f_0327–f_0333 |
| Face F stack, branches, upper windows | v2:f_0335–f_0341 (still `v2_t336.jpg`, `v2_t340.jpg`) |
| Faces K + F corner: door, vent, WC slot, tap, utility window | v2:f_0343, f_0349–f_0355 (still `v2_t342.jpg`) |
| Face E through the gap | v2:f_0343 (crop `c_v2_342_gap.jpg`), v4:f_0422 |
| Faces F/K from above, eaves of the main roof | v4:f_0422, f_0426 |

## 10. Interactions (exterior side)

| object | action | evidence |
|---|---|---|
| French doors | both leaves open outward 0 → 100° | v2:f_0146–f_0153 |
| Cat flaps (French door west leaf; kitchen door) | swing both ways | v2:f_0147, f_0349 |
| Kitchen back door | opens inward 0 → 95°, hinge east | v2:f_0357–f_0359 |
| Balcony doors | open outward (see blue_bedroom.md) | v3:f_0263–f_0297 |
| Second-floor rear window | fanlights top-hung, 0 → 20° (shown ajar, v2:f_0173–f_0175); the owner also opens a lower light by its bottom handle to film straight down (v4:f_0458–f_0467) | hinge side of the lower lights: see the study spec |
| West side window fanlight, utility window | open outward (see ground_corrections.md) | — |
| Taps T1, T2 | water runs | "there's a tap here" v2:f_0353 |
| Floodlight, lantern, fairy lights | on/off | "there's a light here in the middle" v2:f_0178 |

## Doubts and things other areas must agree

1. **Outer planes** R = 17.36 and F = 3.45 (walls 0.50 and 0.35) are this file's decision; interior
   agents measured reveal depths 0.38 (dining north) and 0.25 (utility). F could be 3.55.
2. **French-door axis.** In the frontal still the door axis sits 1.80 m from the render/brick-pier
   junction and 2.35–2.5 m from the east corner. With the junction at −0.50 and the corner at 3.45 that puts
   the axis at 1.0–1.3; I kept the interior value 1.225. `blue_bedroom.md` puts the balcony-door centre at
   1.29 from the same still. The balcony is centred on the balcony doors.
3. **Side-window transom height**: ≈ 1.40 from outside on both windows; ground_corrections.md has 1.55 for
   the west one and "one tall pane" for the east one. From outside the east window clearly has a transom.
4. **Kitchen back door width**: its outer frame is 0.30 × its height in the frontal still
   (≈ 0.80–0.85 × 2.64), narrower than house.json's 0.95 frame; its west edge is on the F/K corner.
5. **Storey heights** from one still: wall top 8.55, second-floor sill 6.30, conduit 6.0, first-floor door
   head 5.3–5.4, balcony platform 3.00. Use the floor agents' levels and keep my offsets from each floor.
6. **Upper flank windows** (§5.2) are located only roughly and only from below.
7. **Roof of the back addition**: flat vs low mono-pitch not resolved; rear fascia is white, flank gutter
   is black.
8. **Face E / the alley**: the main house is free-standing on the east at least at its rear end
   (condenser and flue hang on its east wall, daylight through to the street). `front.md` describes the
   front as mid-terrace with no side gate. Needs reconciling (garden.md D3).
9. Rain-pipe routing from the flank gutter and the exact pipe bends above the kitchen door are schematic.
10. Balcony: my own reads were 2.1–2.3 wide and 1.1–1.25 projection (top-down still v4:f_0467), wall posts
    1.94–2.3 apart; balcony.md's 2.30 × 1.05 with posts at 0.21 / 2.20 is within that and is used here.
    balcony.md and blue_bedroom.md still carry the old wall face y 17.16.

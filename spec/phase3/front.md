# Phase 3 survey - front (forecourt and street elevation)

Surveyor notes for round 3. Footage: v8 (all 138 frames), v9 f1-20 and f45-68, the photo, with v4 f49-53 and
v11 f116-128 for cross-checks. Frame numbers are 1 fps frames (`f12` = t 11 s); stills and working crops are in
`reference/work/r3_front/` (`v8_tNN.jpg` = v8 at NN s = frame NN+1), scripts in `build/r3/front/`. Compared with
`spec/house.json`, `spec/rooms/front.md`, `spec/phase2/front_elevation.md`, `docs/renders/front_street.jpg` and
previews `build/preview/{elev_front,front_*}_r3front.jpg`.

Privacy: the transom lettering, the house number, both number plates, the council name on the bin lids and the
neighbours' door numbers are visible in this footage. None of them is written here; none may be modelled.

## 0. Method and what it is worth

- **Counting** (best): brick courses 75 mm and stretchers 225 mm on the pier and wall, sett courses, feather-edge
  boards. Good to one unit.
- **Ratio in one plane**: bay lights (pitch 0.69 from the living room), first-floor bay window (2.06 x 1.85, sill
  4.12, from the green bedroom), door leaves. Plane rectification by homography (`homo.py`) and a 1D projective
  scale along the bay centre line (`line1d.py`). Interpolation between the ground-floor lights and the first-floor
  window is good to about 0.05 m; extrapolation above the first-floor window head (the gable) to about 0.15 m.
- **The focal length of these clips could not be fixed** (estimates between 650 and 1100 px for the 1080 x 1920
  frame, depending on the method), so anything that needs the camera distance (depth of the gate along the
  alley, parallax of the verge overhang) carries the wide tolerances stated.
- Colours: median sRGB of a patch in a full-resolution still; sun was low and clear on 21 Nov, so sunlit whites
  clip and shaded surfaces go blue-grey.

## 1. Findings that change geometry (summary)

1. **The forecourt falls about 0.30 m from the house to the footway**, not 0.08. The boundary wall top is level;
   under the planter boards there are 7 brick courses at the house end (v8 f110, `wz1.jpg`) and 11 at the pier end
   (v8 f100 `pz1.jpg`, f11 `g14.jpg`); the convergence is visible along the wall in v8 f102 (`wz2.jpg`). Seen
   from the pier (v9 f15) the planter rim at the house end sits at Z 0.74 between the threshold (0) and the lever
   handles (1.03), which puts the paving at the pier at Z -0.38.
2. **Gate pier: 17 brick courses (1.275) plus a pyramidal cap, 1.40 high**, standing on paving at Z -0.36: cap top
   about Z +1.04 (the model's cap top, 1.06, is right in absolute level; its base is 0.22 too high).
3. **The bay is centred on x 2.40, not 2.55, and is 3.50 wide on both floors (x 0.65 .. 4.15).** The west fluted
   pilaster butts straight against the street-door frame; light 1 starts 0.08 east of it (x about 1.10, spec
   1.245). The east corner pilaster is as wide as the west one (0.50), not 0.195. The first-floor bay's west cheek
   stands over the east edge of the door frame (x about 0.65), not at 0.90, so the lean-to porch roof is 1.53 wide.
4. **Bay gable: pitch about 50 degrees, ridge about Z 8.75** (spec 43 degrees, 8.295), eave edges at 6.50 as
   modelled. Different timbering: king post with a forked head and two pairs of raking struts fanning OUT from its
   foot (the model's lean the other way).
5. **East side: not open.** A rendered, insulated flank wall (mustard), a **street gate** of feather-edge boards
   with a fixed boarded over-panel between that flank and the neighbour's brick wall about 1.1-1.5 m behind the
   flank corner, and a **tarmac strip** (not setts) from the footway to that gate, with two inspection covers side
   by side at its head.
6. Bay entablature: cornice Z 2.97 .. 3.34 (spec 2.90 .. 3.10); two raised hexagonal panels on the first-floor
   apron; corner piers with panels the full height of the window.

## 2. Inventory - what the footage shows and the model lacks or has wrong

World frame of BRIEF.md. "S" sampled sRGB, "T" my estimate of the true colour.

### 2.1 Ground and levels (site)

| item | where / size | colour | frames |
|---|---|---|---|
| Sett paving | x -0.72 .. about 4.40, y -5.2 .. -0.12. Courses 160 wide parallel to the house, units about 160 x 160 with some 160 x 240 and 160 x 120, joints 5-8 dark. **One border course of darker setts laid lengthwise against the house wall.** 30-32 courses from the threshold to the plot edge (photo, perspective fit) = 4.8-5.1 m: depth 5.08 stands | S #9D9B99 (shade), #B6AC90 (sun). T light warm grey **#A6A29A** with about 15 % buff #B3AB95 and 10 % pinkish #A8958C units, border #7E7B75. The model's pink / terracotta chequer is much too strong and too regular | v9 f63-68, f19; v8 f27-30, f93-99; photo |
| Fall | Z -0.06 at the house, **-0.36 at the plot edge** (1 in 17), even | | section 1 item 1 |
| Tarmac strip | from the footway to the street gate: x about 4.40 .. 5.66 (the neighbour's planter and wall), widening to the whole alley mouth north of y -1.6; patched, cracked black-grey asphalt with a concrete haunch round the covers. The bins stand at its north-west corner, half on setts | S #646057, #88867B. T **#6B6A64**, matt, lighter worn patches | v8 f31-35, f61-67, f93-95 |
| Sett patch at the bay return | x 4.15 .. 4.63, y 0.25 .. 0.74 and a 0.3 strip along the cheek: three courses of setts under the meter box, weeds | as setts | v8 f68-79 |
| Inspection covers | two recessed covers **side by side east-west**, about 0.48 x 0.58 each (long side along Y), 0.06 apart, centres about **(4.67, -2.0)** and **(5.21, -2.0)**; galvanised frames, grey concrete-filled trays with two key holes each | S #888683. T #8C8A86 | v8 f30-35, f61-65; v4 f52 |
| Gullies | square 0.15 gully with a grating at the foot of the canopy downpipe by the wall end, about (-0.62, -0.32); another at the bay foot about (2.4, -0.20), cut into the border course | dark | v9 f54-56, f62-68 |
| Footway | flags about 0.6 x 0.9 and 0.6 x 0.6, mixed greys, with **two black tarmac patches**: across the crossover in front of the pier (about x -1.3 .. -0.2) and a strip at the plot edge; kerb and road beyond | flags S #A6A39F | v8 f7-14, f43-57 |

### 2.2 West boundary (site)

- **Pier** `front_pier_w`: 1.5-brick (0.33) square, 17 courses, alternate stretcher + header on each face, buff
  brick S #A79975, T **#BFAD84**, mortar #CFC6B0. **Cap**: precast concrete with exposed aggregate, about 0.45
  square, edge 0.085 thick, shallow four-way pyramid rising 0.04, overhang 0.06; S #A9A699, T #A6A398 with lichen.
  On the street face, in the second course below the cap: a small black cast-metal plaque with two lines of raised
  white capitals (a cat warning), 0.22 x 0.065, two screws - a permanent ornament; no address on it.
  (v8 f11-18, f100-101, f121; v9 f13-15.)
- **Wall** `front_wall_w`: top level at Z about +0.54 (0.90 above the pier-end paving, 0.60 above the paving at the
  house), stretcher bond, S #CDBF96. **Planter troughs**: vertical boards 0.29 high (rim Z +0.76, bottom Z +0.47),
  dark brown stain weathered silver at the edges, S #8F7C65 median, #5B4A3A dark; trailing bellflower to about Z
  1.0. On the neighbour's side the same wall and boards; their paving is dark flags and lies 0.15-0.2 lower at the
  house end. (v8 f15-18, f100-103, f110, f117-119, f122-125; v9 f2-3, f16-18.)
- Wall length, thickness and x: no better evidence than phase 2; unchanged.

### 2.3 East side (site, envelope, side_passage)

| item | where / size | colour | frames |
|---|---|---|---|
| Bay east cheek | plane x 4.15, y -0.12 .. 0.74, white. Ground floor: window close to the back corner (about y 0.17 .. 0.69): lower light with white shutter behind, top light, own sill. First floor: one tall light with a hood and a sill, small raised panel on the apron below. Cornice and apron band return along the cheek | white | v8 f35-40, f66-74, f85-87 |
| Return (plane B east part) | y 0.74, x 4.15 .. about 4.63, white to the eaves, the bay cornice returns along it and stops against the render. Short length of the main front eaves gutter over it | white | v8 f61-67, f39 |
| Flank wall | from the corner (about 4.63, 0.74) north: **external wall insulation with a mustard through-colour render**, face about 0.10 proud of the old wall; at the base a white bead 0.05 high at Z about 0.25, a white corner board down to the ground at the south end, and below the bead the old wall face painted black, recessed. Rises to the verge of the main roof (dark verge trim). A black cable loops across it at 2.9 m (omit). Black vent cowl about 0.25 x 0.3 at Z about 4.3, 1 m behind the corner; air-conditioning condenser on brackets at Z about 2.6-3.2 a few metres behind the gate | S #B0A682 sun, #A39875 shade. T **#BFB388** (duller and greener than `render_sandstone` #D2C596; settle with the side-passage survey). Plinth S #28282A | v8 f36-42, f61-72, f78-84; v11 f117-128 |
| Meter box | white surface-mounted box 0.41 w x 0.56 h x 0.21 d on the cheek under the window sill, y about 0.28 .. 0.69, Z 0.02 .. 0.58; small white cable box 0.10 x 0.14 beside it at Z 0.15 | white | v8 f68-79 |
| Downpipe east | white 65 mm square pipe from the gable's east eaves gutter down the cheek 0.10 behind the front corner to a shoe at the ground | white | v8 f38-39, f76-77 |
| Security light | white unit with two round floodlight heads and a camera below them, on the return wall just under the cornice, about (4.32, 0.72, 2.72) | white, black lens | v8 f64-72 |
| **Street gate** | across the alley about 1.1-1.5 m behind the flank corner (y 1.8 +/- 0.4). Leaf about 1.85 high x 1.0 wide of 14 vertical feather-edge boards (about 75 cover), ring latch at 0.95 on the west side; **hinged on the east (neighbour's) side, opens north into the alley** against the brick wall (v11 f121-125). Above it a **fixed boarded over-panel** about 0.83 high with a weathered capping, standing 0.03 proud and overlapping the leaf head: top about 2.68 above the alley ground | street face painted grey-mauve S #68676C, T **#6F6D70**; alley face bare silvered softwood T #B4AEA2 | v8 f33-42, f61-67, f80-84; v11 f116-125 |
| Alley | 1.03 +/- 0.1 wide between the render face and the neighbour's stock-brick flank (14 boards at 75; gate against leaf height in v8 f30). Concrete, green with algae | | v11 f123-128 |
| Neighbour's things (massing only) | their white meter box on their wall at the gate; black cast downpipe; brick with white bands, canted bay, tile-hung gable; dark corrugated-steel raised planter about 0.9 x 2.0 x 0.5 with long side north-south at about x 5.75 .. 6.65, y -5.0 .. -3.0 | steel S #262427 | v8 f31-42 |

### 2.4 Street elevation (envelope)

- **Finish**: all white masonry paint over a fine roughcast / textured coat on the wall fields and mullions, smooth
  on sills, cornices and panels. S #DFDDDD shade, #F6F3E7 sun; T #F2F2EE stands.
- **Bay base**: one plane from the sill to the paving, textured; **no projecting plinth** (front_elevation.md 3.1
  is wrong). Sill 0.07 thick, 0.08 proud, squared ends, top Z 0.62 (0.60-0.65 above the paving by the bins: stands).
- **Ground-floor bay lights**: each of the eight openings has a raised moulded architrave about 0.04 wide round it,
  so only about 0.07 of plain mullion shows between architraves. **Lights 1 and 4 (both rows) are opening sashes**
  with a second frame (glass about 0.35 wide), lights 2 and 3 fixed (glass about 0.445 x 0.655 in the top row).
  Openings equal. (v8 f28-30 `g_v8_t28_top.jpg`, f26, f98.)
- **Pilasters**: west 0.38 wide (x 0.635 .. 1.02) against the door frame; east **0.50** (x 3.71 .. 4.21) wrapping the
  corner; each three convex reeds, moulded capital under the cornice, plain base block to sill level.
- **Entablature**: top-light architrave tops Z 2.77; plain band to 2.97; **cornice 2.97 .. 3.34** in four fillets,
  returning along the east cheek and return. (v8 f26 homography and f138 centre-line scale agree within 0.03.)
- **First-floor apron** Z 3.34 .. 3.98: **two raised flat panels, elongated hexagons** (both ends pointed), each
  1.47 long x 0.34 high, x 0.86 .. 2.33 and 2.47 .. 3.94, centre line Z 3.64, about 15 mm proud with a chamfered edge.
- **First-floor bay window**: frame 2.06 x 1.85 as spec, mullion centres 0.57 / 0.59 in from the jambs (centre
  light 0.88 between mullion centres), transom centre Z 5.44 (spec 5.42). Left and right lights are casements,
  centre fixed with a trickle vent in the top light. Hood mould over the head to Z 6.11; sill 3.98 .. 4.12 with
  squared ends 0.07 beyond the frame.
- **Corner piers** at first floor: sunk panel 0.30 wide from Z 4.08 to 6.14 (as tall as window plus hood), 0.20
  in from each corner. (front_elevation.md 3.5 gives 0.27 x 1.25.)
- **Gable**: white field; plain head band at Z about 6.3-6.4; struts about 0.09 wide, 0.025 proud: a **king post**
  on the axis from the band to the apex, a pair of short braces making a fork (Y) with it about 0.45 below the inner
  apex, a pair of **long struts from the king post's foot rising outward** at about 36 degrees from the vertical
  to the rafters (heads about 0.75 either side of the axis, Z 7.4), and a pair of **short struts parallel to them**
  0.9-1.2 out from the axis (foot Z 6.4, head Z 6.85). Deep white bargeboards (about 0.22) with a scrolled foot,
  white soffit, thin dark slate edge. No finial. (v8 f26 `g3.jpg`, f42 `g19.jpg`, f133-136.)
- **Lean-to porch roof**: four courses of large dark slates (about 0.6 x 0.3) in broken bond; dark upstand /
  flashing 0.15 high to Z about 3.98 under the window sill; lead-dressed junction against the bay cheek. S #4E5159,
  T #4B4E57 stands. Abutment (slate top) Z 3.83 +/- 0.07 (spec 3.90: no change). White fascia and square gutter,
  stop end at the east about x 0.95 (it runs on in front of the bay cornice's west end), running outlet at the west
  into a white square downpipe with a two-bend offset down the west jamb.
- **Canopy soffit**: white boards along X; **three round fittings in one row** about 0.2 out from the door frame at
  x about -0.38 / 0 / +0.38: the outer two small recessed downlights, the middle one a slightly larger domed unit
  (a PIR sensor or a different lamp). (v9 f46-52.)
- **West main eaves**: white gutter turning the internal corner onto the bay cheek; white downpipe down the cheek
  to a two-elbow shoe on the porch roof. **Party-wall kneeler**: one brick wide (0.23), corbelled out about 0.28 in
  five courses, weathered dark red brick S #4A3F43, T #7A4A3C, running from Z about 5.75 to **about 7.0, i.e. 0.5
  above the gutter**, with a dark sloping cap. (The model's block stops at the gutter.)
- **First-floor west window**: casement with a top light and trickle vent, projecting sill 1.1 wide; as spec.
- **Street doors**: each leaf 3 x 4 obscure lights over a plain moulded panel (photo, v9 f60; not 3 x 3); brass
  lever on a 0.24 x 0.03 backplate with a cylinder below, on both leaves at the meeting stiles; brass letter plate
  0.30 x 0.075 on the west leaf's mid rail, centre Z 0.93; white contact sensors on the east jamb at Z about 0.25
  and 1.45 and four white caps along the transom bead; plain frosted transom. Frame outer about 1.27-1.39 wide
  against 1.18 of leaves (v8 f98): the hall survey should settle the frame width.
- **Doorbell**: slim unit 0.045 x 0.125, satin-grey face with a black lens window, on the west pilaster between the
  reeds, centre Z 1.30. **Outdoor socket**: grey weatherproof box 0.16 x 0.10 under the west end of the sill at
  about (1.22, -0.14, 0.42) (spec x 1.45).
- **Flag**: bracket on the pilaster's east edge under the capital, pole about 45 degrees: as spec.

### 2.5 Movables (front)

- **Grey car**: as spec (tail about 1.0 from the threshold, nose just short of the pier). It stands on the slope:
  wheels at Z about -0.13 (rear) and -0.34 (front).
- **White car** on 21 Nov: tail 0.85 +/- 0.15 from the bay face (five sett courses, v9 f63), i.e. centre about
  (3.2, -2.7) against (3.15, -3.43) on 19 Nov. Details to add: red-orange door-mirror caps S T #C8452F, thin
  red-orange stripe low on each door, red lower lip on the front bumper, black A-pillar flash, short roof aerial.
- **Bins**: grey one against the house, navy one south of it, both just east of the bay's corner pilaster as spec;
  navy S #555E83 with lid #68759A, T #3F4868; grey T #4A4C4B. **Caddy is pale green** (S #677972, T #8FA79A), 0.3
  south-west of the navy bin. No lettering on any of them.

### 2.6 Backdrop

- **Lamp column**: black, about 6 m, at the kerb in front of the east neighbour, about (7.5, -7.0) - not in front
  of our bay as modelled at (3.3, -7.0). A plain sign plate at 2.4 m (blank). (v8 f43-47, f53-57; v4 f52.)
- **Street tree**: at the kerb about (-1.2, -7.0), trunk 0.2, crown from 2.5 m. (v8 f5-8, v9 f2-3.)
- West neighbour: red brick ground floor with a white round-arched open porch and a small bay beyond, white
  render above a dentilled brick band at about Z 3.3, black gutter and downpipe at the party line; a pair of white
  meter boxes by their porch. East neighbour: orange-red brick with white bands, canted two-storey bay, tile-hung
  gable with a clay finial, black rainwater goods. Massing only, no numbers.

## 3. Dimension table

| # | item | house.json | present | measured | method / frames | conf. |
|---|---|---|---|---|---|---|
| 1 | Forecourt depth, house face to plot edge | zones.forecourt polygon y | 5.08 | 4.8-5.1 | 30-32 sett courses x 0.16, perspective fit on the photo | med - keep |
| 2 | Forecourt fall | zones.forecourt.fall.z | -0.06 .. -0.14 | **-0.06 .. -0.36** (+/- 0.08) | brick courses under the level planter boards: 7 at the house (v8 f110), 11 at the pier (v8 f100, f11); v9 f15 rim level against the door | med-high |
| 3 | Pier height | boundaries.front_pier_w.height / baseZ | 1.20 / -0.14 | **1.40 / -0.36** (17 courses +/- 1, cap 0.125) | course count with alternating perpends, v8 f12 `pz2.jpg`; v9 f15 shows 15 with the base out of frame | high |
| 4 | Pier plan | front_pier_w.polygon | 0.33 sq | 0.33 (stretcher + header per face) | v8 f12 | high - keep |
| 5 | Wall top | boundaries.front_wall_w baseZ + height | +0.80 | **+0.54** (0.90 above the pier-end paving) | boards 0.29 over 11 visible courses at the pier; rim Z +0.76 | med |
| 6 | Bay lights group centre x | openings.w_bay_front.center | 2.55 | **2.40 +/- 0.05** | door frame edge to light 1 in three frames: v8 f98 (scale from the door and from the lights), v9 f19, v8 f29; pilaster 0.38 + 0.08 seen close in v9 f60; photo shows the vestibule's east wall 0.05-0.1 from the door frame | med-high |
| 7 | East corner pilaster width | (front_elevation.md 3.2) | 0.195 | **0.50 +/- 0.04** | v8 f29, f30 against the light pitch | high |
| 8 | Bay light pitch / width | w_bay_front.lightWidth, mullion | 0.54 / 0.15 | 0.52-0.54 / 0.14-0.15 | the run door frame .. bay corner = 3.69 at pitch 0.69 against 3.53-3.59 expected | low - keep |
| 9 | Bay sill top | w_bay_front.sill | 0.62 | 0.60-0.65 above the paving at the bins | against the 1.07 bin, v9 f63 | med - keep |
| 10 | Bay cornice | (front_elevation.md) | 2.90 .. 3.10 | **2.97 .. 3.34** | v8 f26 homography (rms 2.2 px), v8 f138 1D scale | med-high |
| 11 | First-floor bay west cheek x | exterior.envelope main level 1/2, walls w_bay_cheek_w_1, facades.bay_cheek_w.at | 0.90 | **0.65 +/- 0.07** | cheek corner over the door frame's east edge (v8 f20, v9 f19); v8 f26 homography 0.68 after the 0.15 shift | med |
| 12 | First-floor bay width | (as 11) | 3.25 | **3.50** (0.65 .. 4.15) | v8 f26: corners 0.68 / 4.10-4.14; piers 0.72 each side of the 2.06 window | med |
| 13 | First-floor bay window centre x | openings.w_green_bay.center | 2.53 | **2.40** (centred in the bay) | as 12 | med |
| 14 | First-floor sill / head | w_green_bay sill, height | 4.12 / 5.97 | 4.05-4.12 / 5.9-6.1 | ground-floor-only pose predicts the sill at 4.05-4.11 | med - keep (interior evidence is better) |
| 15 | Gable ridge Z | roof.gable.ridgeZ, roof.planes bay_gable_* | 8.295 | **8.75 +/- 0.15** | inner apex of the wall 8.35-8.5 (v8 f26 1D 8.34-8.40, homography 8.51; v8 f42 affine from the window 8.35-8.48) + 0.25 of bargeboard and slate; v8 f138 gives 8.0-8.1 (outlier, steep view) | med |
| 16 | Gable pitch | roof.planes bay_gable_*.pitchDeg | 43 | **50 +/- 3** | rise 2.25 over half-span 1.85-1.93; v8 f26 and f42 | med |
| 17 | Gable eave edge Z | roof.gable notes | 6.50 | 6.4-6.6 | v8 f26, f42 | med - keep |
| 18 | Gable axis x | roof.gable.ridge | 2.525 | **2.40** | follows 6, 12 | med |
| 19 | Main front eaves gutter | roof.eaves.front.gutterZ | 6.50 | 6.45-6.5 | 0.33 above the west window head, v9 f15 | med - keep |
| 20 | Lean-to abutment | roof.planes.porch_leanto | Z 3.90, pitch 38.5 | slate top 3.83 +/- 0.07, pitch 36 | 0.37 below the window sill, v8 f20 | low - keep |
| 21 | Lean-to roof width | porch_leanto.polygon x | -0.86 .. 0.93 | **-0.86 .. 0.65** | follows 11 | med |
| 22 | Alley width at the street gate | boundaries.alley_neighbour_wall.line x, plot | 0.90 (4.53 .. 5.43) | **1.03 +/- 0.1** from the render face 4.63: wall at 5.66 | 14 boards at 75 cover; gate width against a 1.85 leaf in v8 f30; v8 f64 gives 0.92-1.2 | low-med |
| 23 | Flank render face | facades.east_E.at | 4.53 | 4.63 (insulation 0.10 on a wall face at 4.53); return 0.50-0.55 from the cheek plane | v8 f42 against the bay lights; v8 f64 against the bin | low-med |
| 24 | Street gate | boundaries (none) | - | y 1.8 +/- 0.4; leaf 1.85 +/- 0.1 x 1.0; over-panel 0.83; top 2.68 | proportions lower : upper 2.2-2.3 in two far frames (v8 f30, f41); depth along the alley depends on the unknown focal length | low |
| 25 | East cheek window (ground) | openings.w_bay_cheek_e.center y | 0.37 | 0.43 (frame 0.05 from the back corner, 0.52 wide by the meter box) | v8 f68 | low |
| 26 | Covers | (site module) | (4.45, -2.3), (4.45, -3.0), N-S pair | **(4.67, -2.0), (5.21, -2.0), E-W pair**, 0.48 x 0.58 | v8 f30, f64; v4 f52 | med |
| 27 | Cars | features.car_grey / car_white | (0.78, -3.10), (3.15, -3.43) | grey unchanged; white (3.2, -2.7) on 21 Nov | sett courses, v9 f63 | med (movable) |
| 28 | Door leaves | openings.d_street | 2 x 0.59, frame 1.24 | glazing 3 x 4 confirmed; frame looks 1.27-1.39 outer | v8 f98 | low - hall survey |

Not re-measured (no better evidence than phase 2): wall x and thickness, plot width, flag pole length, footway
and road widths, storey heights (interior riser counts are better than anything from the street).

## 4. Knock-on effects

- **Item 6 (bay 0.15 west).** The outside fixes the window group, not the room. Inside, the simplest reading is
  that the living-room bay keeps its width and moves with the window (inner faces about 0.95 / 3.85): the
  **vestibule's east recess gives way** (its east wall at about 0.75 instead of 0.90 - that corner was "hidden by
  coats" in phase 2, and the photo shows the wall right beside the door frame), and the **east cheek wall becomes
  0.30 thick** (3.85 .. 4.15) instead of an implausible 0.15. The living room's nibs would then be 0.15 (west) and
  0.45 (east) unless the room itself is narrower; that is for the living and hall surveys to decide from inside.
- **Items 11-13 (first-floor bay).** With the east inner face kept at 3.90 and the west cheek 0.26 thick, the bay
  inside becomes 0.91 .. 3.90 and the 2.06 window sits exactly on its centre (2.40). The green bedroom's bay gains
  0.25 on the west; nothing else moves. The west cheek window moves with the cheek.
- **Items 15-18 (gable).** With the ridge at 8.75 the gable roof runs into the main front slope at y about 4.33
  (main slope z = 6.2528 + 0.57735 y), 0.4 below the main ridge. The loft eaves survey should check that the
  valley lines this gives do not cut the front eaves cupboards.
- **Item 2 (fall).** Footway, kerb and road drop with the plot edge (footway about -0.38). The alley mouth and the
  tarmac strip share the fall. The pier and the wall stand on the sloping ground; cars tilt 3 degrees nose down.
- **Item 22.** The east neighbour's massing and the plot's east edge move 0.23 east at the front. The side-passage
  survey sees the alley from inside and should overrule this if it differs.

## 5. Open questions

1. Depth of the street gate behind the flank corner (y 1.4-2.2) and the alley width (0.9-1.2): the focal length
   of the clips could not be fixed, and the two near views (v8 f67, f82) contradict the far views on the leaf /
   over-panel split. Side-passage footage (v11 f116-128) should settle both.
2. Whether the living-room bay inside is really symmetric about the window group at x 2.40 (section 4).
3. Gable apex: 8.75 is the middle of 8.6-8.9; one steep frame gives 0.3 less.
4. Bay light pitch 0.66-0.69: the outside cannot separate a narrower light from a wider bay.
5. The middle fitting in the canopy soffit: sensor or lamp.
6. Whether the mustard render is one colour all round (front #BFB388 here, rear `render_sandstone` #D2C596).
7. Door frame outer width (1.24 in the spec, 1.27-1.39 seen).
8. Car positions are as filmed; which day to model is the owner's choice.

## Verification

Independent re-measurement of the thirteen proposed `house.json` changes (verifier, round 3). Stills in
`reference/work/r3_front_v/`, helpers in `build/r3/front_v/` (`crop.py` grid crops, `line1d.py` 1D projective
fit along a facade line; both private scratch). Frames are named by time: v8 t13 = `f_0014`.

### V0. What decides the X layout: the street-door set is 1.47 wide, not 1.24

The survey scaled everything near the door on "leaves 1.18". That scale is wrong, and it is the whole of the
difference between its bay position and mine.

- **Door height as the scale** (camera level, verticals parallel): v9 t16 opening 355 px high (head 858, threshold
  1213) = 2.02 m -> 176 px/m; east leaf 126 px = **0.72**, transom glass 228 px = **1.30**, frame 272 px = **1.55**.
  v9 t15: opening 307 px -> 152 px/m; east leaf 109 px = 0.72, transom glass 208 px = 1.37, frame 227 px = 1.49. A
  1.24 frame would make the door opening 1.68 m high. (The open west leaf hides the west jamb in these frames; the
  dark opening is not the leaf width.)
- **Light pitch as the scale** (0.69, five reference points: L1 edge, three mullion centres, L4 edge; free
  vanishing point; rms 0.4-0.8 px): v9 t12 frame 1.42 wide, v9 t15 1.47. The two scales agree within 2 %, so
  pitch 0.69 and a 2.03 door stand; the 1.24 / 1.18 door (assumed in round 1, never opened) does not.
- **Inside**: v9 t58, tile cells 0.110 along the threshold row: west wall face to the meeting stile 6.1 cells =
  **0.67**. v1 t11 leaf w/h 0.355 (0.65-0.69 after the downward pitch). v1 t15 / t16 and the photo: the frame fills
  recess B wall to wall on both sides.
- So in the model frame (hall walls at -0.65 / +0.65): frame about **x -0.67 .. +0.80**, leaves 2 x 0.66-0.72,
  meeting stile at +0.02 to +0.07. `d_street` should become width about 1.35, frame 1.47, centre x about +0.065;
  recess B ends at x about 0.82 (present 0.90, proposed 0.75). Not in the proposal list; needed for 04 / 05 / 07.

Same fits, positions relative to the meeting stile (metres at pitch 0.69):

| frame | frame W | E leaf edge | frame E | W pilaster shaft | L1 outer edge | L4 outer edge | E pilaster shaft | bay corner |
|---|---|---|---|---|---|---|---|---|
| v9 t12 (from the pier, 9 deg) | -0.69 | 0.65-0.72 | 0.74 | 0.77 .. 1.05 | 1.17 | 3.78 | 3.96 .. 4.18 | 4.27 |
| v9 t15 (from the pier) | -0.67 | 0.71 | 0.79 | 0.81 .. 1.07 | 1.12 | 3.73 | - | - |
| v8 t27 (in front of the bay) | - | 0.73 | 0.82 | 0.83 .. 1.10 | 1.17 | 3.78 | 3.85 .. 4.25 | 4.30 |

Adding the +0.02 of the meeting stile (tiles): light 1 edge at x **1.175 +/- 0.04** (spec 1.245, proposed 1.095),
east corner 4.29. East-side check, independent of the door: the return from the cheek plane to the render face is
**0.40 +/- 0.05** (v8 t67, vanishing points of the cornice / bead / base lines give f 724 px; cheek window 0.52 as
the scale; also 0.40 from the projection ratio in v8 t60), not 0.50-0.55; render face 4.63 - 0.40 = cheek
**4.23**, which is the 4.285 corner less the 0.055 pilaster. West and east anchors agree on a bay axis of **2.48**.
The loft survey (east hatch 2.60 +/- 0.10, hatch centred on the tunnel within 0.08) is also against 2.40.

### Verdicts

| id | verdict | value to use | my measurement (reference, frames, result, tolerance) |
|---|---|---|---|
| front-01 | **accept** | pier 1.40 high (17 courses + cap 0.125), baseZ -0.36, cap 0.45 sq | v8 t13 (not the t11 of the survey): street face, perpends alternate right / left down to the asphalt: 9 right + 8 left (one behind the plaque) = **17 courses**. Forecourt face in v8 t100: 15 courses to the setts, so the setts at the pier stand about 2 courses above the crossover asphalt. Cap underside 2 courses above the trough rim (v8 t100) = +0.90, apex +1.03. +/- 1 course |
| front-02 | **accept** | forecourt -0.06 -> -0.36, alley mouth -0.08 -> -0.36, footway -0.38, road -0.50 | Courses under the planter cladding: house end **7** (v9 t54), 1.2 m from the pier **9**, at the pier junction **10.5** (v8 t100, pier courses 55 px beside it): 3.5 courses = 0.26 if the cladding foot is level, 0.15 if the rim is level (the cladding is shallower at the pier). Pier chain: setts at the inner face of the pier -0.21 .. -0.32, asphalt at its street face -0.36 .. -0.47. The proposed -0.36 at the plot edge lies inside that; present -0.14 does not. +/- 0.08. Camera height at the pier (v9 t12 / t15: 1.44-1.55 above FFL) argues for the shallow end of the range |
| front-03 | **accept** | brick top +0.54, baseZ -0.36, height 0.90; cladding 0.29, rim +0.76, foot +0.47 | Foot of the cladding 7 courses above the paving at the door (v9 t54) = +0.465. Rim between threshold and lever handle in v9 t15 (152 px/m): 0.6-0.8. Present top +0.80 with troughs to 1.28 is refuted. +/- 0.08 |
| front-04 | **adjust** | `w_bay_front.center` **[2.48, -0.06]**: lights 1.175 .. 3.785; bay inner faces 1.03 / 3.93; west cheek wall 0.82 .. 1.03; **east cheek outer face 4.23** (wall 0.30); recess B ends at 0.82; west pilaster shaft 0.83 .. 1.09 (0.26 reeded, zone 0.80 .. 1.175); east pilaster zone 3.785 .. 4.285 | V0: three frames, 5-point projective fits, door-independent east anchor. Direction right, half the size: the -0.15 of the survey comes from the 1.18 door scale (true 1.35-1.44) and from taking the door frame edge at 0.62 (true 0.80). With 2.48 the west cheek wall is 0.21 thick, which is what round 1 saw ("no deeper than 0.2", V7); with 2.40 and the true frame edge it would be 0.14. Living-room nibs become 0.23 / 0.37. +/- 0.04 |
| front-05 | **adjust** | first-floor bay outer faces **x 0.75 .. 4.23** (3.48); `facades.bay_cheek_w.at` 0.75, `bay_cheek_e.at` 4.23 on both floors; `front_B.extent` [-0.88, 0.75]; `w_green_bay` centre 2.48; interior bay width stays 2.74 (1.11 .. 3.85), cheek walls 0.36-0.38 | First-floor west arris over the east edge of the door frame: v9 t12 4 px west of it, v8 t131 4-9 px east of it after the lean (0.05 px/px): x 0.78 +/- 0.06. East arris over the ground-floor corner pilaster (v9 t12). Window centred in the bay (piers 89.5 / 88.5 px) and over the ground-floor lights within 0.07. The homography of the survey gives 0.83 / 4.25-4.29 in the lights-at-2.55 frame, the same as mine (0.78 / 4.35); only the shift to the model differs (-0.07, not -0.15). Widening the bay inside the room to 2.99 has no interior evidence: rejected. External 3.48 against internal 2.74 is not settled |
| front-06 | **adjust** (ridge x only) | ridge [[2.48,-0.42],[2.48,4.33]], **ridgeZ 8.75, pitch 50**; `bay_gable_w` [[0.61,-0.42],[2.48,-0.42],[2.48,4.33],[0.61,0.46]] z = 5.799 + 1.19 x; `bay_gable_e` [[2.48,-0.42],[4.35,-0.42],[4.35,0.46],[2.48,4.33]] z = 11.701 - 1.19 x; eave edges 6.52, at the cheeks 6.68 | Pitch read as an image angle, camera level: v9 t15 verges 48.4 / 52.5 deg, v9 t12 48.8 / 53.1: **50 +/- 2**. Heights, 1D projective along the bay axis (transom centre 1.865, top-light centre 2.315, window 4.12 / 5.97): v8 t60 wall apex 8.3-8.45, verge apex 8.9 after the 0.3 overhang; v9 t15 (uniform 133-134 px/m) verge underside apex 8.2-8.35 corrected. Ridge 8.6-8.9. 6.52 + 1.87 tan 50 = 8.75. +/- 0.15 |
| front-07 | **adjust** | `porch_leanto.polygon` [[-0.86,-0.58],[0.75,-0.58],[0.75,0.74],[-0.86,0.74]]; fascia and gutter to a stop end at x 0.88 | Follows 05. Gutter end 28 px east of the frame edge in v9 t12, less 9.5 % parallax for its 0.46 projection: 0.87 |
| front-08 | **adjust** (limits only) | forecourt x -0.72 .. 4.40 setts; alley mouth [[4.40,-5.2],[5.58,-5.2],[5.58,1.37],[4.63,1.37],[4.63,0.74],[4.23,0.74],[4.23,-0.12],[4.40,-0.12]] asphalt; sett patch x 4.23 .. 4.63, y 0.25 .. 0.74 | Setts end at a ragged edge by the two covers, tarmac to the gate, sett patch under the meter box: v8 t60, t63, t65, t67. West limit not re-measured (+/- 0.15). East and north limits from 09 / 10, cheek from 04 |
| front-09 | **adjust** | `front_side_gate`: line [[4.63,1.37],[5.58,1.37]], leaf **0.78 x 1.34**, hinged east, opens north; fixed boarded panel above to **2.05**; baseZ = alley floor | Brick courses of the neighbouring wall beside the gate, in the plane of the gate: 20 courses in 396 px = 19.8 px (v8 t65). Opening 245 px = **0.94**, leaf 360 px = **1.38**, top of the panel **1.95-2.0**. This is the gate of the passage survey (0.95; 0.78 x 1.34; 2.05; y 1.37 +/- 0.10 by ground plane), not a 1.85 leaf with a top at 2.68. Depth: course ratio front corner / gate 1.21 puts it 0.6-0.85 behind the neighbouring corner |
| front-10 | **adjust** | `alley_neighbour_wall` x **5.58**; plot and east neighbour +0.15 at the front | 0.94 clear from the render face 4.63 at the gate (above). The two readings of the passage survey give the same face: 0.95 at the gate from the render, 1.05 mid-way from the plinth foot 4.53. Not 5.66. +/- 0.05 |
| front-11 | **accept** | `east_E`: render face 4.63 from (4.63, 0.74) north to the verge, bead and white corner board, black plinth at 4.53; colour about #BFB388; return y 0.74 white to the eaves, **x 4.23 .. 4.63** | Return is a real south-facing wall (cornice mitres into an inside corner, base lines zig-zag, sunlit against the shaded cheek: v8 t67), **0.40 +/- 0.05** wide: this refutes "cheek 0.10 behind the east face, cheek at 4.55" in the envelope survey. Render #B2A884 (t67), #A49A78 (t65), #99927F (t60). Bead 0.30-0.34 above the tarmac at the corner; its absolute Z (+0.25) holds only if the ground there is -0.08 |
| front-12 | **accept** | `w_bay_cheek_e.center` y 0.43 | v8 t67 3D solve: frame 0.045 from the inside corner. Same adjacency in v8 t60 and t69. +/- 0.03 |
| front-13 | **accept** (optional) | `car_white.center` [3.2, -2.7] | v9 t61: five sett courses between the plinth and the rear bumper. Wheel Z from the forecourt fall as adopted, not hard-coded |

### Knock-on checks

- X chain at the front with the values above: party-wall face -0.65 | door frame -0.67 .. 0.80 | pilaster to 1.175 |
  lights 2.61 to 3.785 | corner 4.285 (cheek 4.23) | return 0.40 | render 4.63 | alley 0.95 | brick 5.58. Outside,
  frame west edge to render face measures 5.35-5.39 at pitch 0.69; the model gives 5.30. No interior wall moves
  except the bay (-0.07) and the east end of recess B.
- Stacking: ground-floor lights, first-floor window, gable ridge on one axis, 2.48. Porch roof abuts the cheek at
  0.75; the east edge of the door frame (0.80) and the pilaster stand just east of that line, as filmed.
- Roof: gable ridge 8.75 dies into the main slope at y 4.33, 0.39 under the main ridge; eave edges still meet the
  main gutter at 6.52.
- Levels: 17 pier courses, cap apex +1.04 and the wall top +0.54 fit a plot edge at -0.36. The alley floor at the
  street gate is -0.28 +/- 0.07 in the passage survey while the setts beside the bay are tied to the threshold at
  -0.06; the alley mouth needs a fall between them or one of the two is 0.1-0.2 out.

### Not settled

1. Bay axis 2.48 +/- 0.04 rests on the tile cell being 0.110 (west wall to meeting stile) and on the return
   width; 2.44-2.52 is possible, 2.40 and 2.55 are both at the edge.
2. First-floor bay: external 3.48 against the internal 2.74.
3. Forecourt fall: 0.15-0.30; which of rim and cladding foot is level was not established.
4. Level of the ground at the east corner against the alley floor and the base rail (0.27 between the front
   and the envelope / passage readings).
5. Sett edge x 4.40 and the surface east of it (tarmac at the mouth, concrete inside the gate) were not measured.

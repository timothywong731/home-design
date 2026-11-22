# Project brief — realistic 3D model of the owner's home (ground floor)

Read this fully before doing anything. Every agent on this project works from it.

## Goal
Build a realistic, accurately-coloured, intricately-detailed 3D model of the owner's home in
Blender from a 13-minute phone walkthrough video, and publish it as an interactive web viewer on
GitHub Pages (https://timothywong731.github.io/home-design/), with a 2D floor plan linked to the
3D scene that shows where the viewer is standing and looking.

The owner's words: "Realistic effect with intricate details. Use accurate colour and design
details. Focus on all: wall paint colour, dado, cornice, door/window frame, pediment, floor,
kitchen cabinets, laundry room layout, hallway, living room, sofa, book case... You can declutter
the house, focus on the actual furniture which I mentioned."

## Reference material (PRIVATE — in `reference/`, git-ignored, never copy into tracked dirs as-is)
- `reference/frames/f_0001.jpg … f_0797.jpg` — 1 frame per second, 720x1280 portrait. Frame N is
  at t = N-1 seconds.
- `reference/sheets/s_01.jpg … s_13.jpg` — contact sheets, 32 thumbnails each, yellow label L in
  the corner of each thumbnail. **Label L = frame file f_(2L-1)** (e.g. label 44 → f_0087.jpg).
  Start with the sheets for orientation, then Read individual frames.
- `reference/transcript.txt` — the owner's narration with timestamps/frame numbers (if present;
  the owner points at things while talking — treat what they say as authoritative).
- Full-resolution stills (1080x1920) on demand — the video is rotated, ffmpeg auto-rotates:
  `ffmpeg -v error -ss <seconds> -i "C:/Users/Timothy Wong/Downloads/PXL_20261118_173753601.mp4" -frames:v 1 -q:v 2 out.jpg`
  Put any extra stills/crops you extract under `reference/work/<your-area>/`.
- The camera is an ultrawide phone lens: strong perspective/barrel distortion. Straight lines near
  the frame edges bow, near objects look huge. Estimate sizes from known references instead:
  UK internal door leaf 1981 x 762 mm, door handle ~1000 mm above floor, light switch ~1200 mm,
  socket ~300-450 mm, kitchen worktop 900-910 mm high / 600 mm deep, base units in 300/400/500/600
  mm modules, washing machine 600 x 850 mm, American fridge-freezer ~910 mm wide x 1780 mm high,
  stair riser ~190-200 mm / going ~240-250 mm, metro tile 100x200 or 75x150 mm, oak planks
  ~180-220 mm wide, typical Victorian/Edwardian terrace ceiling ~2.6-2.9 m.
- Lighting in the video is warm LED at night and the phone HDR is aggressive — colours on walls
  drift warm/yellow. When you report a colour give the sampled sRGB AND your best estimate of the
  true paint/material colour under neutral light.

## Rooms and where they appear (frame file numbers, inclusive)
| id | room | frames |
|---|---|---|
| `vestibule` | entrance porch/vestibule: white glazed front double doors, Victorian geometric floor tiles, mahogany glazed inner double doors with transom | 1-47, 55-61, 795-797 |
| `hallway` | long hallway: oak floor, dado rail, dentil cornice, arch with corbels, mirror, console, paintings | 49-85, 235-285, 437-445, 545-567, 741-755, 769-781 |
| `stairs` | staircase off the hallway: mahogany newel/handrail, white spindles, grey carpet, panelled spandrel | 241-251, 773-777 |
| `living` | front living room: pedimented door surround (hall side), terracotta TV wall, pink walls with gallery of gold-framed paintings, tapestry, glazed bookcase, orange velvet scroll sofa, coffee table, rug, bay window with dark frames + white shutters + tartan curtains, armchairs, lamp table, chandelier | 87-233, 783-793 |
| `kitchen` | kitchen: navy/black shaker cabinets, white marble-effect worktop, grey metro tiles, steel angled hood, gas hob, plate rack, wine rack, built-in ovens, American fridge-freezer, glass-shelf bar nook with glass rack, wood-effect tile floor, white back door | 287-435, 755-767 |
| `utility` | laundry/utility room: grey shaker cabinets, oak worktop, Belfast sink, washer + dryer, marble metro tiles, tall cupboard, ceiling airer | 445-495, 529-533 |
| `wc` | cloakroom WC: grey walls, marble metro tiles half height, black towel radiator, wall-hung WC, basin, gilt mirror, pocket/oak doors | 497-543 |
| `dining` | rear dining room: long dark oak table, Chippendale-style chairs, carved dark fireplace + mantel, dark brown dado, cream walls, crest plaques frieze, carved panels, mirrors, wall TV, white French doors, check curtains, chandelier + ceiling rose, dark window frames | 569-741 |

Only the ground floor is filmed. The staircase is modelled going up to the first-floor opening;
nothing upstairs is modelled.

## Rules
- **Privacy (the site is public):** never reproduce the street name/address lettering on the
  front-door transom (use plain frosted glass), no faces or photos of people (the wedding portrait
  becomes a neutral framed artwork), no whiteboard writing, no fridge magnets/photos, no documents.
  Nothing from `reference/` may be committed, except small perspective-rectified crops of the
  *paintings/tapestry/rug patterns* used as textures (no people in them), saved under
  `blender/textures/art/`.
- **Declutter:** omit bags, clothes, shoes, laundry on the airer, the exercise bike/wheelchair,
  countertop mess, cat tree, pet bowls, heaters. Keep: architecture, mouldings, doors, windows,
  built-in cabinetry and appliances, all real furniture, rugs, curtains/shutters, light fittings,
  framed art/mirrors/plaques, and a few characterful permanent ornaments (mantel clock,
  candelabra, table lamp, barometer, statuette, plants in pots).
- **Do not run git commands that change state** (no add/commit/push/checkout/stash). The
  orchestrator commits.
- Only write inside the files/directories your task assigns to you. Other agents are working in
  the same checkout at the same time.
- Never use the live Blender MCP tools (`mcp__blender__*`) — one shared GUI instance cannot be
  used by parallel agents. Use headless Blender:
  `"C:/Program Files/Blender Foundation/Blender 5.1/blender.exe" -b --factory-startup --python <script.py> -- <args>`
  (Blender 5.1.1, Cycles on 2x RTX 4090 via OptiX; Python has numpy; system Python 3.13 has
  numpy, PIL, cv2, torch.)
- Temp/scratch output goes under `build/` (git-ignored) or `reference/work/`.

## Conventions
- Units metres. Z up. World origin = centre of the inside face of the front (street) door
  threshold, at finished floor level of the vestibule. **+Y runs from the front door into the
  house (toward the rear/dining room). +X is to your right as you walk in.** Finished floor level
  of the hallway oak floor is Z=0 unless the spec says a room steps up/down.
- Canonical geometry spec: `spec/house.json` (rooms, walls, openings, levels, heights) — the
  single source of truth for the shell, the 2D plan and the 3D↔2D mapping.
- Per-room detail specs: `spec/rooms/<id>.md`.

## Owner's spoken priorities (from the narration — authoritative, see reference/transcript.txt)
- "Remember all these paintings — got to be in place": every painting/frame/mirror in every room
  and along the hallway must be present at its real position and size, with its real picture
  (rectified crop) wherever a clean view exists.
- Kitchen: "the layout has to be exactly the same… especially the cabinets"; navy-blue cabinets,
  brass handles, marble top, wood-effect floor tiles, extractor hood, plate (dish) rack, wine rack,
  oven tower, fridge, mini bar on the left of the door, two taps, socket layout, door to garden.
- Laundry room: "remember the cabinet layout" — grey cabinets, wooden worktop, washing machine,
  tumble dryer, tap/sink, tall tower unit, window at the back, ceiling airer, under-cabinet lights
  as well as spotlights (same in the kitchen).
- WC: dark grey walls, grey radiator, plant, paintings, basin, mirror; a sliding door AND a normal
  door ("there are two doors here… make sure you get that right").
- Hallway: dado rail with white above / light grey below, cornice, spotlights, mirror, barometer,
  console table, lots of paintings, sockets, the half arch, round wall clock, Wi-Fi access point.
- Living room: red (terracotta) wall, TV cabinet with amplifier + speakers, two antique brass wall
  lights, chandelier, two armchairs, red tartan curtains, wooden window frames, red sofa, red
  stool, carpet (rug), coffee table, little chair, decanter table, plant stand, air-con unit,
  cotton artwork (tapestry), plant, big bookcase with antique clock, whisky glasses tray, bird
  ornament, round wooden table in the bay.
- Dining room ("the most important part"): massive dining table; 8 chairs — three per long side
  with the middle one of each side being an armchair, plus one at each end; TV; mounted sword;
  shields (crest plaques) along the top; cornice like hall/living; wooden window frames; wall
  lights; fireplace with two candlesticks + antique clock + centre picture; symmetrical identical
  windows left and right; curtains; chandelier (remember the design) with ceiling rose; mirror in
  the middle of the wall flanked by two wood carvings.
- Porch: outside lights, front door with two windows on top and an arch, floor tiles, light
  switch, red-coloured wooden door frame (the mahogany inner doors), cornice, spotlights.

## 2D floor plan — owner requirement
The viewer includes a 2D property layout linked to the 3D scene, showing where the viewer stands
and which way they look (position marker + view cone; click the plan to move there). **It must
look like an architectural CAD drawing as seen in a typical DWG file**, not a coloured diagram:
- thin precise vector linework (SVG/canvas), monochrome CAD palette (AutoCAD model-space look:
  near-black background with white/yellow/cyan/green layer colours; offer a paper-white toggle);
- walls drawn as double lines at true thickness with solid/hatched poché, cut cleanly at openings;
- doors as leaf line + quarter-circle swing arc (double doors: two arcs; sliding/pocket door:
  dashed leaf in the wall), windows as triple-line symbols in the wall, bay window drawn true;
- stairs as tread lines with direction arrow and "UP", break line where they pass the cut plane;
- fixed fittings in plan symbol form on their own layer: kitchen base units + worktop edge
  (wall units dashed), hob (burner circles), sink bowls, fridge, ovens, washer/dryer (circle in
  square), WC, basin, radiators, fireplace/chimney breast, arch as dashed lines;
- loose furniture as thin outline symbols (sofa, table + chairs, bookcase, rug dashed);
- dimension chains outside the plan with extension lines, tick/arrow terminators and values in
  mm; room name tags in capitals with internal dimensions and area (m²); level change marks;
- drafting furniture: north-less orientation note ("FRONT"/"REAR"), scale bar, drawing title
  block ("GROUND FLOOR PLAN", scale 1:50, drawn-from-video note) in a CAD monospace/ISO-style
  font — no address, no owner name.
Everything is generated from `spec/house.json` (+ fittings/furniture footprints exported from the
Blender scene) so it stays in exact registration with the 3D model.

### Floor plan downloads — owner requirement
The plan panel has download buttons:
- **DXF** (opens in AutoCAD/any CAD; DWG itself is proprietary): a real CAD file generated at
  build time from the same data as the on-screen plan — units mm, true scale, entities on named
  layers (e.g. A-WALL, A-DOOR, A-GLAZ, A-STRS, A-FURN, A-FIXT, A-DIMS, A-ANNO-TEXT) with layer
  colours matching the on-screen palette, proper LINE/LWPOLYLINE/ARC/HATCH/TEXT/DIMENSION
  entities (not an exploded picture). Written to `docs/assets/ground-floor-plan.dxf`; verify by
  re-reading it with `ezdxf` (audit passes, layer/entity counts sane) and rendering it back to an
  image to compare with the on-screen plan.
- **PDF**: vector PDF of the paper-white drawing sheet with title block at a stated scale (1:50 on
  A3, or the largest standard scale that fits), black linework with CAD lineweights. Either
  generated at build time to `docs/assets/ground-floor-plan.pdf` or produced client-side from the
  plan SVG — it must be vector, not a screenshot.
Neither file may contain the address, owner name or anything from the privacy list.

# Phase 2 — whole house, garden, front, and interactions

The owner asked (1) for things to be operable in the viewer — see `blender/INTERACT.md` — and
(2) to "complete whole house modelling including garden and front parking (street side)", and
supplied six more videos, filmed in daylight. Everything above still applies.

## Phase-2 reference material (PRIVATE, git-ignored)
`reference/v2 … v7/` each hold `frames/f_NNNN.jpg` (1 fps, 720x1280, frame N at t = N-1 s),
`sheets/s_NN.jpg` (32 thumbnails, **label L = frame f_(2L-1)**) and `transcript.txt` (narration
with frame numbers — authoritative). The original night video stays in `reference/frames`
(call it v1). Full-res still: `ffmpeg -v error -ss <seconds> -i "C:/Users/Timothy Wong/Downloads/<file>.mp4" -frames:v 1 -q:v 2 out.jpg`

| id | file | length | content (frame ranges approximate — check the transcript) |
|---|---|---|---|
| v2 | PXL_20261119_102350651 | 1016 s | daylight re-walk of the ground floor with corrections: dining 1-146 (switches, fireplace, deep windows, pelmets, cat door); French doors → patio, garden, fire pit, planting, shed / workshop interior, rear elevation, side passage 146-366; kitchen (everything opens: dishwasher, ovens, fridge, freezer, bins, pull-outs) 366-477; hallway arch, storage cabinet, steps 477-530; utility 530-600; WC 600-640; hallway 45-degree wall segments, picture rod, living room (bay splay, curtains, shutters, light controls, centring) 640-880; vestibule, front doors, front parking with two cars, brick walls, flag, pediment, switch mapping 880-1011 |
| v3 | PXL_20261119_104053938 | 703 s | stairs up 1-70; first floor: landing, middle yellow room (unoccupied) 70-150; rear blue bedroom, its wardrobe, bureau, balcony, en-suite with bath and shower 150-490; two steps up to the front green bedroom (double doors, wardrobes, bed, nightstands, bureau, TV, armchair) 490-703 |
| v4 | PXL_20261119_105304855 | 570 s | green bedroom with curtains open, bay windows and the view of the front parking 1-95; sliding door to its bathroom (double basin, shower) 95-180; first-floor landing, cat paintings, stairs to the second floor 180-355; second floor: skylight, arch, unused purple room 355-450; rear study / office 450-570 |
| v5 | PXL_20261119_110238920 | 346 s | second floor: bathroom with shower and free-standing sauna 1-135; hallway 135-170; front loft office (sloped ceiling, Velux, deep cabinet, desk) 170-260; triangular eaves storage either side 260-346 |
| v6 | PXL_20261119_111552021 | 306 s | walk down from second floor to ground 1-50; kitchen 50-95; door to the basement, narrow stair, basement (boiler, hot-water tank, racks, electrical box, network cabinet, gas meter) 95-298 |
| v7 | PXL_20261119_112257990 | 48 s | kitchen socket positions |

## Phase-2 scope
All levels: basement (-1), ground (0, exists), first (1), second / converted loft (2); the rear
garden (patio, fire pit, planting, shed with its workshop interior, side passage, balcony), the
front (parking area with two cars, brick walls, flag, front elevation), the rear elevation and a
roof. Upper floors stack on the ground-floor footprint (`spec/house.json` bounds; party walls are
continuous). Ground-floor corrections shown in v2/v6/v7 must be applied (notably wall segments at
about 45 degrees in the hallway / vestibule / bay, window reveal depths, socket and switch
positions, which switch controls which light).

## Phase-2 privacy and declutter additions
- Cars: two generic cars of the right type, size and colour, **no number plates, no badges**.
- Neighbouring houses and the street: plain low-detail massing / backdrop only; never a house
  number or street name; nothing that identifies neighbours.
- Certificates, documents, screens, family photographs: blank / neutral / abstract. Painted
  artwork (cat paintings, landscapes) may be rectified crops as before; no people.
- Declutter as before: bedding stays neat, no clothes, bags, toiletries clutter, cables, boxes.
  Wardrobes that open show a few plain hanging garments (generic), fridges generic food shapes.

## Phase-2 owner priorities (from the narration)
- "Make sure you get all the details right": corners, pediments, dado rails, arches, steps
  between levels ("two steps up", "a massive step"), smooth 45-to-90-degree transitions, deep
  window reveals, pelmets, radiators, sockets, switches.
- Everything that opens in reality opens in the model: all doors, wardrobe / cabinet / bureau
  doors and drawers, windows the owner opens in the video, shower and sauna doors, Velux, eaves
  storage doors, shed doors; curtains and shutters; taps run; toilets lift; lights switch from
  the switch the owner shows for them (including which gang controls spotlights / wall lights /
  chandelier / LED strips); the dining-room TV ("telly") turns on and off.
- Named pieces to keep: star-shaped chandelier, pineapple bedside lights, Queen Anne nightstand
  with marble top, bureaus, big mirror, bathtub, shower controls (same in every bathroom), sauna
  (one seat, heater with rocks, timer, gauge, bucket, tinted glass door), skylight, Velux, cat
  paintings, red chair, corner cabinet, computers (blank screens), boiler, hot-water tank, racks,
  network cabinet, gas meter, fire extinguisher, shed/workshop with racks and window, fire pit,
  planters, lavender, garden panel, metal balcony, flag.

# Phase 3 — detail and dimension round (21 Nov footage)

The owner's request: "Improve details across whole house. Make sure the dimensions are right." plus
a cross-sectional view of the house in the DXF / PDF drawing set, and three second-floor rooms
renamed. Everything above still applies. Round-3 notes go in `spec/phase3/` (briefs per room unit in
`spec/phase3/briefs/<unit>.md`), decisions in `spec/RECONCILE3.md`.

## Room names (ids do not change)
Owner correction (binding): the 2F front room (street side) is the Slate Room, the 2F rear room
(garden side) is the Rose Room. Anything written earlier this round that says otherwise is wrong.

| id | old name | name from now on |
|---|---|---|
| `loft_office` | Loft office (2F **front**, street side, under the roof slope) | **Slate Room** |
| `study` | Study (2F **rear**, garden side) | **Rose Room** |
| `purple_room` | Purple room | **Lavender Room** |

## Phase-3 reference material (PRIVATE, git-ignored)
`reference/v8 … v13/` hold `frames/f_NNNN.jpg` (1 fps, 720x1280, frame N at t = N-1 s) and
`sheets/s_NN.jpg` (label L = frame f_(2L-1)); `reference/work/overview_vN.jpg` shows 24 evenly spaced
frames of each. **These six videos are silent** (no narration: the frames are the only evidence).
Full-res still (1080x1920), also at times between the 1 fps frames:
`ffmpeg -v error -ss <seconds> -i "C:/Users/Timothy Wong/Downloads/<file>.mp4" -frames:v 1 -q:v 2 reference/work/<area>/<name>.jpg`

| id | file | length | content (frame ranges approximate — look at the overview and sheets) |
|---|---|---|---|
| v8 | PXL_20261121_124142138 | 138 s | street side in daylight: front bay and bins by the side gate 1-6; front elevation from the pavement with the brick gate pier, both cars, porch with the door open, flag, gable 13-66; the timber side gate, the rendered flank wall and the neighbour's brick flank 67-89; cars 90-101; the path between the brick planter wall and the grey car to the front door 102-113; porch canopy, fascia and gable from below and from the street 114-138 |
| v9 | PXL_20261121_124601813 | 68 s | out through the open front door 1-6; porch and front door from the forecourt 7-20; vestibule interior: inner mahogany doors and transom, ceiling and cove, side windows, frosted glazing 21-44; outside of the front door, side lights, canopy underside with its light, brick return and planter 45-58; forecourt along the bay base, shutters, bins 59-68 |
| v10 | PXL_20261121_124801398 | 65 s | living room table games: a Chinese chess (xiangqi) board with dark red disc pieces on the coffee table, an inlaid mosaic box of dominoes (the lid opens), a wooden solitaire board with marbles on the round table in the bay beside the lamp base; rug, sofa and armchairs in the background |
| v11 | PXL_20261121_124951560 | 196 s | kitchen back door from inside (frosted glass, cat flap) 1-17; out to the side passage: paving, rendered walls, windows and sills, downpipes, hose reel, outside tap, view to the garden and shed 18-60; timber gate and its latch 61-76 and about 111; the passage towards the street: flank wall, soil and rainwater pipes, vents, wall lights (lit), air-conditioning condenser, gates 77-153; back towards the garden 154-187; garden: deck, planters, shed, trellis 188-196 |
| v12 | PXL_20261121_125633444 | 122 s | loft eaves storage: low cupboard doors (open), panel mouldings, the triangular voids inside (sloping roof, floor finish, how far they run), and the room around them |
| v13 | PXL_20261121_132233957 | 225 s | second floor: hallway, dado, arch, balustrade 1-10; lilac room (door, floral curtains, radiator, window, view down onto the side passage) 11-49; bathroom: basin, WC, tall cabinet, window, marble tiles, sauna interior (bench, heater, panelling), shower, towel rail 50-127; the two office rooms: desks, monitors (blank), bench with red upholstery, pale pink walls, wall TV, air-conditioning unit, bean bag, plants 128-206; views straight down from the rear window onto the outrigger roof / balcony, garden (deck, lawn, pergola) and shed roof — plan-like views 207-225 |

Photo: `reference/photos/vestibule_front_door_open.jpg` (3072x4080) — from the vestibule out through
the open right-hand front door leaf: door leaf with 3x3 frosted lights and brass lever, transom,
shoe rack, floor tiles, block paving, the brick planter wall with lavender, the grey car.

## Phase-3 privacy reminder
v8, v9 and the photo show the street name on the transom, the house number, number plates and the
neighbours' houses. **Never write any of them down** — not in spec notes, file names, comments or
commit messages — and never model them. The whiteboard by the kitchen back door stays blank.

## Measuring (the owner's emphasis this round)
Ultrawide lens: measure by ratio against a known size in the same plane at a similar depth, from
more than one frame, and state reference, frames, ratio, result and tolerance. Useful scales
outdoors: brick course 75 mm (65 + 10 joint), brick 225 mm long with joint; block paver 200 x 100;
paving slabs 600 x 600 or 450 x 450 (decide by ratio first); 240 L wheelie bin 1.07 high x 0.58 wide
x 0.74 deep; fence panel 1.83 wide; the grey car is a supermini-class hatchback about 3.95 long x
1.70 wide x 1.51 high, the white one a city car about 3.46 x 1.62 x 1.46; number plate 520 x 111
(scale only). Indoors as listed under "Reference material" above, plus socket and switch plates
86 mm (double 146 x 86). Change a dimension in `spec/house.json` only when the new evidence is
better than the evidence behind the present value (`spec/RECONCILE.md`, `RECONCILE2.md`).

## Phase-3 owner instructions (binding)
- Living room table games (v10): the **domino box** stands on the **coffee table**; the **Chinese
  chess (xiangqi) set** also stands on the **coffee table** and is modelled in fine detail (board
  lines with river and palaces, every piece with its incised mark, correct count and layout); the
  **solitaire board** with its marbles stays on the **side table** (the round table in the bay).
- Walking: visitors can get into the narrow and low spaces, such as the **eaves storage** behind
  the low cupboard doors (open the door, duck through, move about inside under the roof slope with
  the eye height following the headroom), and likewise the sauna, shower enclosures, the shed store,
  the basement stair and other tight places. Stored things and furniture leave a lane free.

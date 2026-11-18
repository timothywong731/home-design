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

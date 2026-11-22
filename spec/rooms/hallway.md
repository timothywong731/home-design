# Hallway (`hallway`) — visual / dimensional specification

Source frames: f_0049–f_0085, f_0235–f_0285, f_0437–f_0445, f_0545–f_0567, f_0741–f_0755,
f_0769–f_0781, f_0793–f_0797 (all viewed) plus full-res stills in `reference/work/hall/full/`.
Owner narration (authoritative): console table "with a mirror and a barometer", "a lot of beautiful
paintings on the wall", light switch, "door frame with pediment", "the corners" (cornice), "dado rail…
this is a white colour, this is light grey colour", "beautiful corners and spotlight", "sockets", "a half
arch right here", "that's the Wi-Fi access point", "I put a clock here, a round shape… paintings, light
switch".

Colours: "sampled" = median sRGB under the warm LED/HDR video; "true" = neutral-light estimate — **use
"true"**. Related specs: inner doors → `vestibule.md` §2.2; staircase → `stairs.md`; pedimented living-room
doorcase → `living.md` §2.2; kitchen/utility door leaves → `kitchen.md` §2.1, `utility.md` §2.1.

Viewpoint convention: **"standing in the open inner (mahogany) doorway, back to the vestibule, looking
down the hall"** = facing +Y. Left = west wall (-X, party wall, mirror + paintings). Right = east wall
(+X: living door, stairs, kitchen door, utility door). Far end = dining-room door.

---

## 1. Shape & dimensions

### Room-local frame
- Origin = centre of the inner-door frame on its **hall face**, at floor level. +x east (house right),
  +y north (toward the rear), z up. Hall oak floor z = 0 (same level as vestibule tiles and all rooms).
- World (BRIEF) coordinates = local + (0, 1.83).
- South wall (-Y, y = 0) is the glazed inner-door screen; west wall x = -0.65 is one straight plane for
  the whole length (single sight line from the dining room to the inner doors, f_0741–f_0745); the east
  side steps; north wall (+Y, y = 10.70) holds the dining door.

### Plan — four zones
| zone | x range | y range | size (X x Y) | ceiling |
|---|---|---|---|---|
| A. Front hall | -0.65 → +0.65 | 0 → 2.50 | 1.30 x 2.50 | 2.90 flat |
| B. Passage beside the stairs | -0.65 → +0.15 | 2.50 → 6.10 | 0.80 x 3.60 | 2.90 flat (stairwell open on the east side) |
| (stairs, see `stairs.md`) | +0.15 → +0.99 | 2.50 → 6.10 | 0.84 x 3.60 | — |
| C. Lobby (kitchen door) | -0.65 → +0.99 | 6.10 → 7.15 | 1.64 x 1.05 | 2.90 over x < 0.15; **2.60 soffit** over x 0.15 → 0.99 |
| Arch wall | opening -0.59 → +0.35 | 7.15 → 7.45 | 0.94 clear, 0.30 thick | arch, see §2.5 |
| D. Rear corridor | -0.65 → +0.35 | 7.45 → 10.70 | 1.00 x 3.25 | 2.90 flat |

Total length 10.70 m.

- **Nib at the stair foot:** the front hall's east wall (x = +0.65) ends at y = 2.50; a return wall runs
  east 0.34 m to x = +0.99, and the staircase wall continues north on x = +0.99. The bottom of the
  staircase is tucked partly behind this nib (f_0243, f_0779; the cornice turns the corner in f_0084,
  f_0246).
- **Lobby/arch return:** at y = 7.15 the east wall steps back west from x = +0.99 to x = +0.35 (a
  0.64 m south-facing wall — the open kitchen door lies against it) forming the arch's east jamb.
- **West-wall pilasters** (shallow full-height piers, 0.06 m proud, square arrises; dado, skirting and
  cornice all break forward around them):
  - South pilaster y 6.95 → 8.30 (passes through the arch; the arch's west corbel is on it).
  - North pilaster y 10.00 → 10.70 (runs into the north-west corner).
  - Between them a recessed bay y 8.30 → 10.00 (1.70 long) opposite the utility door (f_0548).
- Reasoning for key numbers:
  - Front width 1.30: the inner door frame is wall to wall; in frontal still F_0057 the leaves scale as
    610 x 1981 mm and the frame as 1.30 m (see `vestibule.md` §1).
  - Passage 0.80: in still F_0751 (t = 750 s) the under-stairs door height (1.981 m) gives 394 px/m at
    the door plane; spandrel-to-west-skirting = 317 px → 0.80 m. Independent check: on the floor the
    passage/front-hall width ratio from vanishing-point geometry in the same still is 0.62 → 0.81 m.
  - Stair block 0.84: under-stairs door leaf ≈ 0.61 + two 70 mm architraves + ≈ 0.09 margin.
  - Lengths follow `spec/layout.md` (stairs 3.60, lobby 1.05, arch wall 0.30, corridor 3.25); the front
    hall is 2.50 rather than 2.40 so that the 1.32 m wide pedimented doorcase fits before the nib.
  - Ceiling 2.90: inner frame top scales to 2.83 m and sits just under the ceiling (F_0057).
  - Dado top 0.965 m and skirting 0.17 m scaled from the same still.

---

## 2. Openings

### 2.1 Inner doors (south wall, y = 0) — to vestibule
Mahogany glazed pair 2 x 610 x 1981 with clear fanlight to 2.79, frame 1.30 x 2.83 wall to wall; both
leaves swing **into the hall**; west leaf stands open ≈ 85° against the west wall, east leaf shut. Full
detail in `vestibule.md` §2.2. Hardware on the hall side: on each side wall's skirting, 0.60 m north of
the frame, a **brass door stop** (Ø 12 x 70 mm peg with black rubber tip, 60 mm above floor) and above it a
**brass cabin hook** (100 mm) hanging from an eye on the skirting top (f_0053, f_0001).

### 2.2 Living-room door D1 (east wall x = +0.65) — to living room
- Clear opening 0.78 wide x 2.00 high, **centre y = 1.78** (opening 1.39 → 2.17). Oak 4-panel leaf
  762 x 1981, **hinged on the north jamb, swings east into the living room**, stands open ≈ 95°
  (leaf detail in `living.md` §2.1).
- **Hall side has the white broken-pediment doorcase**: architrave, bed mould, two acanthus corbels,
  shelf, frieze with applied shell-and-scroll ornament, base cornice, two raking cornices and a central
  pedestal block — overall 1.32 m wide, top at z ≈ 2.71. **Build it exactly from `living.md` §2.2**
  (door centre u = 0 ↔ local y = 1.78). Its north end (y 2.44) stops 0.06 m short of the nib corner.

### 2.3 Under-stairs cupboard door (wall y = 6.10, faces north into the lobby)
- Oak 4-panel leaf **610 x 1981 x 35**, same pattern/colour as D1 (two tall panels over two short
  ones; golden oak **#B08A56**). Opening x 0.265 → 0.875 (centre x = +0.57).
- **Hinges on the east (+X) side**, brass butts, knuckles visible → **opens north into the lobby**.
  Brass lever on a rectangular backplate on the west side of the leaf, z 1.00. Modelled closed.
- White gloss architrave 70 mm (ogee + fascia) to z 2.07; east leg ≈ 20 mm from the lobby's east wall
  corner, west leg ≈ 45 mm from the spandrel corner (x 0.15).
- Above the architrave: white **vertical beaded tongue-and-groove boarding** (95 mm boards) z 2.07 →
  2.30, then the overhead cupboard (§4).

### 2.4 Kitchen door (east wall x = +0.99, lobby) — to kitchen
- Clear opening 0.762 x 1.981, **y 6.24 → 7.00 (centre 6.62)**. Oak leaf with the two upper panels glazed
  in obscure glass (see `kitchen.md` §2.1). **Hinged on the north jamb, opens west into the hall** and
  stands open 90° flat in front of the lobby's north return wall, its free edge overlapping the arch
  opening by ≈ 0.12 m (f_0751, f_0283). White 70 mm architrave both legs + head (z 2.07).
- Threshold: dark red-brown hardwood bar 60 mm wide, 8 mm proud, in the door line; kitchen tiles beyond.

### 2.5 Arch with corbels ("the half arch") — lobby ↔ rear corridor
- Plain square-edged plastered arch through the 0.30 m thick wall at y 7.15 → 7.45. Clear width 0.94 m
  between the west pilaster face (x = -0.59) and the east jamb (x = +0.35).
- **Segmental arch:** springing z = 2.40, crown z = 2.75 (rise 0.35 on a 0.94 span → radius 0.49 m);
  0.15 m of flat wall above the crown up to the ceiling. No archivolt moulding; arrises sharp.
- **Corbels:** one on each jamb face at the springing, projecting into the opening and centred in the
  wall thickness (so the profile reads from both sides). Each: **0.26 long (N–S) x 0.11 projection x
  0.38 high**, z 2.02 → 2.40. Top = stepped cap 90 mm high (three square fillets stepping out 15, 30 and
  45 mm, the uppermost 0.26 long); below it a **scrolled console body** 0.29 m high that curves back to
  the jamb in a concave S-profile, its end faces (north and south) carved with **three vertical flutes**,
  finishing in a small rounded drop 60 mm wide. White matt like the walls (f_0282–f_0285, f_0551–f_0557).
- The side-wall cornices stop against the arch wall on both sides; no cornice crosses the arch wall.

### 2.6 Utility door (east wall x = +0.35 here; +0.45 in `house.json`, rear corridor) — to utility room
- Clear opening 0.762 x 1.981, **y 8.72 → 9.48 (centre 9.10)**. Oak 4-panel leaf hinged on the south
  jamb, opening east into the utility (leaf in `utility.md` §2.1). White architrave 75 mm with an outer
  bead, head z 2.08. Dark red-brown hardwood threshold bar 75 mm wide.

### 2.7 Dining-room door (north wall y = 10.70) — to dining room
- Clear opening **0.838** x 1.981 centred at **x = -0.056** (opening -0.475 → +0.363; verification
  round — was 0.762 at -0.12). Oak 4-panel leaf hinged
  on the **west** jamb, opening north into the dining room, standing open ≈ 90° against the dining
  room's west wall. Hall side: **white gloss architrave 70–90 mm** (two stepped fascias + ogee + outer
  fillet), head top z 2.10; it nearly fills the end wall, which is **1.10 m** wide (east wall at
  x = +0.45 here): ≈ 45 mm of wall to the west pilaster, a 10–20 mm sliver to the east wall. Oak boards
  run straight through, no threshold strip. (Dining side is dark-stained — `dining.md`.)

### 2.8 Stairwell
Open on the east side of zone B from the nib to the lobby — see `stairs.md`.

---

## 3. Surfaces

### Paint
| element | sampled | true | finish |
|---|---|---|---|
| Walls **above** the dado — white | #cbc7be (f_0062), #b9b6ad (f_0263), #bcb8b2 (f_0550) | **#F2F0EA** | matt emulsion |
| Walls **below** the dado — light warm grey | #817b6a (f_0062), #938e7b (f_0263), #888373 (f_0550) | **#C8C5BB** (first estimate #B9B5A8 rendered a khaki band; lightened after the shell review, f_0770 lower/upper ≈ 0.78; `M.PAINT['hall_dado_grey']`) | matt emulsion |
| Dado rail, skirting, architraves, doorcase, spandrel — white | #e4e3e0 (rail), #b3afa9 (spandrel in shade) | **#F4F2EC** | gloss on joinery |
| Cornice, arch, corbels, ceiling | #9c988d (ceiling in shade) | **#F4F3EE** | matt |

The two wall colours apply to every wall of zones A–D, the nib, the pilasters, the arch jambs below
the corbels, and the lobby's north return wall. The video drifts both tones yellow-green; the lower colour
is a pale greige about 25 % darker than the upper white.

### Dado rail
- Top edge **z = 0.965**, 70 mm high x 30 mm projection, white gloss. Profile top to bottom: 12 mm square
  fillet, 28 mm half-round torus (the dominant roll), 6 mm quirk, 20 mm cavetto, 4 mm fillet
  (close-ups f_0254–f_0265).
- Runs along the whole west wall (breaking round both pilasters), the front east wall from the inner
  frame to the living-door architrave and from the doorcase to the nib, round the nib return, the west
  wall of the lobby, the lobby's north return wall, both arch jambs, and both sides + the short north
  wall stubs of the rear corridor. It stops square against every door architrave and the inner frame.
  On the staircase wall it continues as a raking rail (`stairs.md`). None on the panelled spandrel.

### Skirting
- 170 mm high x 20 mm, white gloss: 120 mm plain face, then a 50 mm moulded top (6 mm step, 30 mm
  ogee/torus, 10 mm top bead). Mitred round the nib and the pilasters; butts the architraves (no plinth
  blocks). The spandrel has its own matching skirting.

### Cornice — modillion ("block") cornice, plaster, white
- Overall **0.22 m drop x 0.20 m projection** on the ceiling. From the wall upward: 15 mm fillet + 35 mm
  cyma-reversa bed mould; a plain vertical band 75 mm high carrying the blocks; flat soffit of the
  corona; 40 mm corona fascia; 45 mm cyma recta + 10 mm fillet against the ceiling.
- **Modillion blocks:** 55 mm wide x 70 mm high x 60 mm projection, each a tiny fluted corbel — a 12 mm
  moulded cap, a front face carved with **three vertical flutes**, the bottom third curving back to the
  band. **Spacing 0.13 m centre to centre** (75 mm gaps); a block is centred on every internal/external
  corner mitre (f_0079–f_0082, f_0058).
- Extent: both long walls of zone A (it dies into the top corners of the inner frame — nothing crosses the
  frame); along the nib return, stopping against the staircase wall; the whole west wall (breaking round
  the pilasters); in the lobby along the west face of the landing bulkhead (x = +0.15, from the
  staircase's corner post at y 6.10 to the arch wall at y 7.15); no cornice along the open stairwell
  edge south of that post; in the rear corridor on the west, east and north walls. Not on
  either face of the arch wall.

### Ceiling
Flat white plaster, true **#F4F3EE**, 2.90 m. No ceiling rose, no picture rail. Lobby east part: flat
soffit at 2.60 (underside of the stair landing) with a 0.30 m vertical bulkhead face on x = +0.15.

### Floor
- **Engineered oak wide plank, rustic grade**, the same floor as the living and dining rooms: boards
  ≈ 220 mm wide, random lengths 1.2–2.2 m, micro-bevelled, **laid lengthwise along the hall (parallel to
  Y)**, continuous from the inner sill to the dining room. Sampled #b5a886, #c6bc9e, #988960;
  true **#C9B48A**, knots/filled cracks #6B4E32, satin lacquer (clear specular streaks under the
  downlights, roughness ≈ 0.35).
- One pale filler slip ≈ 30 mm wide and 0.9 m long is let in between two boards 0.25 m east of the hall
  centre just inside the inner doors (f_0053, f_0796) — optional detail.
- Thresholds: flush mahogany sill at the inner doors; hardwood bars at the kitchen and utility doors
  (§2.4, §2.6); none at the living and dining doors.

---

## 4. Fixed fittings

| item | position (local) | description |
|---|---|---|
| **Overhead cupboard** | lobby, above the under-stairs door: x 0.20 → 0.95, y 6.10 → 6.45, z 2.30 → 2.60 | White gloss box hung under the landing soffit, projecting 0.35 m from the door wall; one flat full-width top-hung door with a **polished-brass D-handle** 130 mm, centred, at z 2.36; 25 mm rounded bottom front edge (f_0753, f_0754). |
| 3-gang light switch | east wall, zone A, centre (y 0.98, z 1.27) — below the north-bottom corner of painting E1 | white plastic plate 86 x 86 mm, three rockers |
| PIR alarm sensor | west wall, y 0.20, z 2.45 | white box 60 W x 95 H x 45 D |
| Double socket | west wall, y 1.28, z 0.36 (just south of the console) | white plastic 146 x 86 mm |
| Heating thermostat/receiver | west wall, lobby, centre (y 6.85, z 1.42) | white rounded-square box 100 x 100 x 25 mm, small LCD window top-right (f_0281, f_0770) |
| Double socket | west wall, lobby, y 6.78, z 0.34 | white 146 x 86; a white plug-in device sits in it (omit the device) |
| Double socket | west wall, south pilaster north of the arch, y ≈ 7.95, z 0.34 | white 146 x 86 (plug-in extender omitted) |
| 1-gang light switch | east wall, rear corridor, centre (y 9.70, z 1.25) | white plastic 86 x 86 rocker |
| **Wi-Fi access point** | ceiling, rear corridor, (x +0.12, y 7.75) | white disc Ø 0.20 m x 35 mm, flush-mounted (f_0551–f_0557) |
| Smoke alarm | ceiling, lobby, (x -0.20, y 6.75) | white disc Ø 0.11 m x 40 mm |

No radiator anywhere in the hall.

---

## 5. Furniture

| item | position | size (W x D x H) | description |
|---|---|---|---|
| **Console / hall table** ("beautiful wooden console table") | against the west wall under the mirror, centred y = 1.75; projects to x = -0.29 | 0.72 x 0.36 x 0.76 | Antique dark oak/walnut, William-and-Mary style (true **#3A2619**, sampled #271f19, semi-gloss polish). **Top** 22 mm, rectangular with both front corners canted 45° (cut ≈ 110 mm), thumb-moulded edge. **Apron** 0.13 m deep, figured/burr veneer, lower edge cut in a cusped ogee scallop (centre lobe + two side lobes on the front, one on each canted side). **Four legs** (two at the front canted corners, two at the back): square block at the top, a short ring, a large **inverted-cup ("bell") turning** Ø 75 mm, then a long tapering octagonal shaft to a ring and a square block at stretcher height, **bun feet** Ø 60 mm. **Stretchers** 0.13 m above the floor: flat shaped boards 18 mm thick forming a concave-fronted X (two serpentine diagonals meeting at the centre) with a straight back rail (f_0067, f_0068, f_0236). Table top modelled empty. |

---

## 6. Soft furnishings & decor
Every picture hangs with its top edge ≈ 2.10 m above the floor unless stated. "Quad" = outer frame
corners TL, TR, BR, BL in the named 720 x 1280 frame, ±12 px, cast shadow excluded. No photos of people.
One painting (E1) includes a tiny painted figure: **when making the E1 texture for
`blender/textures/art/`, inpaint the girl with path colour and keep the geese** (BRIEF: art crops have no
people in them). All other pictures are figure-free.

### West wall (x = -0.65), front to rear
| id | item | centre y | outer W x H | z range | description | texture source |
|---|---|---|---|---|---|---|
| — | **Banjo barometer** | 0.78 | 0.14 x 0.52 | 1.36 → 1.88 | Carved mid-brown oak (true #6A4528): scrolled leaf crest, narrow neck with a brass-scaled thermometer (20 x 150 mm), round body with a **silvered dial Ø 0.115 m** in a brass bezel, black hands, carved leaf pendant at the bottom (f_0070, f_0071) | model, no crop |
| — | **Gilt mirror** | 1.75 (opposite the living door) | 1.20 x 0.85 | 1.16 → 2.01 | Landscape rectangle; **frame 95 mm wide x 45 mm deep**, antique gold (sampled #736543, true **#B0903C**) deeply moulded with a continuous diagonal **ribbon-and-acanthus-leaf** relief, plain 10 mm inner bead; plain silver glass (f_0069, f_0254, f_0267) | real mirror; frames show the owner — never crop |
| W1 | Painting — dark timber cottage in an overgrown garden | 3.20 | 0.78 x 0.58 | 1.52 → 2.10 | Landscape. Brown wooden house with dark roofs among birches and firs, white-flowered grass, grey picket fence, pale blue-grey sky. Frame: plain brushed **champagne gold** scoop 60 mm (true #B9A56A) | **f_0271**: (10,123) (590,355) (608,768) (30,822); fingers touch the frame's bottom edge only |
| W2 | Painting — whitewashed thatched farmhouse | 4.90 | 0.86 x 0.62 | 1.48 → 2.10 | Landscape. Long white house with brown plank double doors under deep thatch receding to the right, bare tree, yard with a white goose and dark hens, spring greens. Same champagne-gold scoop frame 65 mm | **f_0275** (frame's top-left corner is off-image): canvas-only quad (45,25) (520,290) (555,635) (90,668) |
| W3 | Painting — tumbledown thatched shed with hens | 6.45 (opposite the kitchen door) | 0.565 x 0.70 | 1.39 → 2.09 | Portrait. Grey thatched lean-to, ladder, haystack mound with a black cockerel, white and brown hens, big green tree, pale sky. Frame 55 mm: **dark bronze-black outer moulding with a gold inner slip** (true #2E261C / #A8893F) | **f_0770**: (307,397) (468,387) (468,583) (312,589) — frontal; or full-res still t = 769 s x1.5 |
| W4 | Painting — autumn birches by a lake | 9.02 (centre of the recessed bay) | 0.74 x 0.61 | 1.50 → 2.11 | Landscape. White birch trunks, orange/yellow foliage, violet distant trees, dark pond with reeds and blue reflections. Frame 60 mm: flat pale gold with a **dark beaded inner border** | **f_0550**: (109,221) (513,222) (508,562) (114,566) — frontal |

### East wall
| id | item | position | outer W x H | z range | description | texture source |
|---|---|---|---|---|---|---|
| E1 | Painting — cottages, girl with geese | zone A, x = +0.65, centre y = 0.71 (0.40 from the inner frame, 0.12 from the doorcase corbel) | 0.62 x 0.82 | 1.34 → 2.16 | Portrait. Tiled/thatched cottages centre, purple-grey clouds, tree at right, sandy path with a small girl driving white geese, pond and plank bridge lower left. Frame 70 mm: **antique gold scoop with a dark outer edge and a gold bead** (true #9C8440) | **f_0076**: (228,365) (576,282) (582,780) (243,752) |
| S1–S4 | four small stair prints | staircase wall | — | — | see `stairs.md` §6 | — |
| E2 | Painting — river with willow | rear corridor, x = +0.35, centre y = 10.12 (between utility architrave and north wall) | 0.70 x 0.55 | 1.55 → 2.10 | Landscape. Large willow-like tree on a rocky bank at left, blue river with lily pads, bright green far bank, cumulus sky. Frame 65 mm antique-gold scoop | **f_0564**: (86,176) (412,40) (400,520) (108,500) |

### North wall
| item | position | size | description | texture source |
|---|---|---|---|---|
| **Round wall clock** ("a clock here, a round shape") | centred over the dining door, centre (x -0.12, z 2.42) | Ø 0.28 m x 30 mm, dished like a plate | Middle-Eastern inlaid-mosaic clock: dark walnut ground (true #3A2A22), scalloped rim with mother-of-pearl dots, a ring of twelve small pearl rectangles as hour marks, central 12-point star rosette in red-brown and cream, small gold hands (f_0560–f_0562) | **f_0560**: circle centre (310,477), Ø 80 px |

No rugs, curtains or plants in the hall.

---

## 7. Lighting
All hall lights are **recessed LED downlights**: white fixed bezel Ø 85 mm, flush, lamp Ø 50 mm,
neutral-warm **≈ 3000–3500 K** (they read whiter than the brass chandelier), each ≈ 500 lm. One row down
the middle of each zone:

| # | x | y | zone |
|---|---|---|---|
| 1 | 0.00 | 0.65 | front hall |
| 2 | 0.00 | 1.85 | front hall, in front of the living door |
| 3 | -0.25 | 3.20 | passage (centred on the 0.80 m passage) |
| 4 | -0.25 | 4.40 | passage |
| 5 | -0.25 | 5.60 | passage |
| 6 | -0.10 | 6.65 | lobby |
| 7 | -0.15 | 8.40 | rear corridor |
| 8 | -0.15 | 9.70 | rear corridor |

No pendant, no wall lights in the hall itself. The vestibule's brass lantern chandelier is visible
through the inner doors' fanlight from everywhere in the hall and is the visual focus at the south end
(`vestibule.md` §7). The dining room beyond the north door is dark in the video.

---

## 8. Declutter list (deliberately excluded)
Everything on the console table (letter rack, papers, carrier bags, phone, sunglasses case, pouch) and the
clear bag of clothes on the floor beside it; the robot vacuum dock seen through the living door; plug-in Wi-Fi extenders in the sockets; laundry seen through the
utility door; the owner's reflection in the mirror, hands and feet. Kept: barometer, mirror, console,
all six paintings, clock, thermostat, sockets/switches, access point, smoke alarm, door stops.

---

## 9. Reference frames

| frame | shows | camera (local x, y, z) → looking |
|---|---|---|
| f_0057 | inner doors + fanlight square-on, cornice ends, dado, PIR | (0, 1.5, 1.75) → -Y |
| f_0064 | whole front hall: console, mirror, stairs foot, nib, open living door, far arch | (-0.1, 0.4, 1.6) → +Y |
| f_0071 / f_0069 | barometer, mirror, cornice on the west wall | (0.3, 1.2, 1.6) → -X, slightly up |
| f_0076 / f_0082 | painting E1, 3-gang switch, pedimented doorcase and modillion cornice | (-0.3, 1.5, 1.6) → +X (f_0082 tilted up 40°) |
| f_0273 | passage west wall with W2, W3, thermostat, south pilaster, arch, clock | (-0.2, 4.2, 1.6) → +Y |
| f_0283 / f_0285 | arch, both corbels, access point, lobby bulkhead and its cornice, rear corridor | (0, 6.3, 1.6) → +Y, tilted up 30° |
| f_0770 | lobby west wall: W3, thermostat, socket, south pilaster, cornice break, cupboard corner | kitchen doorway (0.9, 6.6, 1.6) → -X |
| f_0548 | rear corridor west wall: recessed bay with W4 between the two pilasters | utility doorway (0.8, 9.1, 1.6) → -X |
| f_0560 / f_0563 | dining door architrave, clock, E2 and its switch | (-0.1, 9.6, 1.6) → +Y / +X |
| f_0745 | full-length view back to the inner doors: utility door, arch, W4, E2, downlights, AP | dining doorway (-0.1, 10.9, 1.6) → -Y |
| f_0751 / f_0753 | under-stairs door, overhead cupboard, spandrel, passage, W3 | (0, 7.3, 1.6) → -Y |
| f_0781 | front hall looking back: doorcase, E1, switch, inner doors, barometer | (0.1, 2.6, 1.6) → -Y |

---

## 10. Uncertainties
1. **Widths differ from `spec/layout.md`.** Layout: hall 1.55 m wide throughout (stairs 0.82 + passage
   0.73), no nib. This spec: front hall **1.30**, passage **0.80**, stairs **0.84**, with a **0.34 m nib**
   at the stair foot. The nib itself is certain (wall corner + cornice return visible in f_0084, f_0243,
   f_0246, f_0779; also noted in `living.md` §2.2); its depth is ±0.10 and depends on the two width
   measurements. If `house.json` keeps one 1.55 m width, still model a nib ≥ 0.15 m at y = 2.50.
2. **Y positions** north of the living door are ±0.3 m (inherited from the layout chain). Picture
   centres W1/W2 are ±0.3 m along the wall (ordered and roughly evenly spaced: W1 just past the stair
   foot, W2 mid-passage, W3 opposite the kitchen door — that one is ±0.1).
3. **Rear-corridor width** was 1.00 from the layout with the arch's east jamb flush with the corridor's
   east wall; the verification round makes it **1.10** (east wall x = +0.45, arch jamb a 0.10 respond)
   — the corridor width at the arch end was not counter-checked; the arch springing/crown (2.40 / 2.75) come from the kitchen-door head in
   f_0552 and are ±0.08 (layout has 2.15 / 2.60).
4. **Pilaster lengths** on the west wall (±0.2 m) and their 0.06 m projection (±0.02).
5. **Cornice profile**: member sizes are a best reading from oblique views; block spacing 0.13 ± 0.02 m.
6. **Mirror size** 1.20 x 0.85 (±0.1): never seen square-on without being cropped.
7. **Lobby soffit height** 2.60 and the overhead cupboard's exact size (±0.1).
8. **Corridor sockets**: the one at y 7.95 is seen only as a small white plate with a blue LED
   (f_0552, f_0745); position ±0.4 m.
9. Downlight count is 8 ± 1; spacing is nominal.
10. Ceiling height 2.90 (`living.md` argues 3.05 for the adjoining room; the hall measurement here
    supports 2.85–2.95).

---

## Reconciled dimensions (from `spec/house.json`, see `spec/RECONCILE.md` D1-D5, D9, D10 and "Verification round")
Widths are unchanged except the rear corridor, now **1.10** (east wall x = +0.45; every rear-corridor
east-wall item in this spec given at x = +0.35 — utility door, switch, E2 — sits on x = +0.45). Lengths
change: front hall 3.00 (was 2.50), stair recess 2.85 (was 3.60), lobby 1.05, arch wall 0.30, rear
corridor **3.20** (this spec 3.25). Ceiling 2.95.

| zone | global x | global y |
|---|---|---|
| A front hall | -0.65..0.65 | 1.83..4.83 |
| B passage | -0.65..0.15 | 4.83..7.68 |
| C lobby | -0.65..0.99 | 7.68..8.73 |
| arch wall | clear -0.59..0.35 | 8.73..9.03 |
| D rear corridor | -0.65..0.45 | 9.03..12.23 |

Local to global: x unchanged. For y, add the offset of the element the item is keyed to:

| items (local y in this spec) | global y = local + |
|---|---|
| inner doors, door stops, cabin hooks, PIR | 1.83 |
| living door and doorcase (1.78), E1, 3-gang switch, mirror, console, barometer, socket at 1.28 | 2.31 (door centre 4.09) |
| nib (2.50) | 2.33 (4.83) |
| W1, W2 and downlights 3-5 in the passage | 4.83 + (local - 2.50) x 0.79 |
| under-stairs door wall (6.10), lobby, kitchen door, W3, thermostat, lobby sockets, smoke alarm, arch, corbels, south pilaster, access point, socket at 7.95 | 1.58 (kitchen door centre 8.24) |
| utility door (9.10), corridor switch, downlight 8 | 1.62 (door centre 10.72) |
| north pilaster, end wall (10.70), dining door, clock | 1.53 (end wall 12.23) |

- E2 sits centred between the utility architrave and the end wall: centre y 11.70 (1.05 m of wall;
  this spec had 1.22).
- The recessed bay between the west pilasters is y 9.88..11.53; W4 hangs at its centre, y 10.70,
  opposite the utility door.
- The overhead cupboard projects 0.45 (y 7.68..8.13); the 2.60 landing soffit covers y 8.13..8.73.
- Dining door 0.838 wide, centre x = -0.056; the clock is centred over it.
- The stainless pedal bin seen through the kitchen door is owner-named and kept; it stands inside the
  kitchen and belongs to `kitchen.md` §6.

## Round 3 corrections (core owner, from build/rooms2_open.md)
- Overhead cupboard: the box behind the flap is hollow (house.json lobby_cupboard_interior, x 0.212..0.942,
  y 7.92..8.13, Z 2.327..2.587, under tread R14).
- Kept: the cupboard face stays at y 8.13. A face at y 7.80 with the interior to the south (v2 f_0505, v6 f_0290) would
  put a 0.30 box at Z 2.30..2.60 into treads R12 / R13 (Z 2.28 / 2.47 over y 7.44..7.90) of the spec flight; it needs
  a re-survey of the top of the flight first.
- Hall arch a_hall: three-centred, springing 2.40, crown 2.75, haunch radius 0.32 (crown radius 0.71): the soffit rises
  vertically off the corbel caps (v1 f_0283, v2 f_0512-f_0516).
- The hall cornice does not run along x 0.15 over the open top of the flight (y 7.58..8.13); the 2.84 run along the
  lobby edge starts at the drop post's north face (y 8.18).
- Round-3 whole-house check: the front-hall cornice no longer runs across the screen wall over the inner-door frame head (lib/mouldings TRIM['hallway'] skip box moved from y 1.83 to 1.96 with the hall's south edge).

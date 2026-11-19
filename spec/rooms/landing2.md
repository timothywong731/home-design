# landing2 — second-floor landing and hallway (stair head, skylight, platform, arch, all doors)

Source: v4:f_0354–f_0388 and f_0440–f_0442, f_0540 (arriving, skylight, hallway to the rear), v5:f_0001–f_0008
and f_0128–f_0170 (sockets, artwork, switches, the "massive step"), v6:f_0001–f_0008 (walking back down).
Full-resolution stills and crops are in `reference/work/p2_second_rear/` (`hr_v<k>_<t>.jpg`, t = frame − 1).

Owner narration: "I'm now standing on the second floor of the house, there's a skylight here, a square shaped
skylight… there's a step here… towards the back of the house you see an arch on the second floor, really
simplistic arch" (v4 05:55–06:23); "more sockets, artwork, light switch… towards the front of the house… there's
a switch here, turn this on, you can turn on and off the spotlight for the 2nd floor hallway… there's a massive
step in here, remember you get this right" (v5 02:11–02:45); "make sure you get the sockets right" (v5 00:00).

**Dimension confidence.** Camera focal length was calibrated from vanishing points (f = 865 ± 60 px on the
1080-wide stills, so this is not the 0.5x lens — about 17 mm equivalent). Widths and heights hang on door
leaves (1981 high) and are good to ±0.05 m. Lengths along the hallway come from floor back-projection in three
independent stills (hr_v5_2 top-down, hr_v5_0 and hr_v4_383 level) and were then **scaled by 1.046 so the
chain closes between two fixed lines of `house.json`**: the old rear wall of the main house (inner face
y = 8.73, which is the north wall of the stairwell) and the rear wall of the back addition (inner face
y = 16.86). Before scaling the chain measured 7.77 m against 8.13 m, i.e. 4.4 % short, inside the focal-length
error. Individual stations along Y are ±0.12 m; the two ends are fixed by the ground-floor model. Levels: step
heights ±0.04 m; the absolute level Z2 is ±0.15 m and belongs to `stairs2` (riser count).

## 1. Shape, levels and dimensions

World frame is used directly (no local frame): +Y to the rear, +X to the right walking in, origin as in the
brief. The hallway runs along the **west party wall (x = −0.65)** from the loft-office door to the study door,
exactly over the ground-floor passage / rear corridor.

### Levels (four floors meet here)

| level | Z (world) | where |
|---|---|---|
| **Z2 — second-floor datum** | **6.02** (= first-floor front level F1f 3.42 + 13 risers × 0.20, the value `stairs2` publishes; my own count, 14 × 0.19 = +2.66, gives 6.08) | stair-head strip, the whole hallway, `purple_room`, `bathroom2`, `study` |
| platform | Z2 + 0.20 = **6.22** | 1.25 m long landing between the stair head and the loft-office door, one ordinary riser up |
| loft office floor | platform + 0.27 = **6.49** (Z2 + 0.47) | through the loft door — the owner's "massive step" (0.27 ± 0.04, measured in hr_v5_163: riser 245 px against the 0.67 m frame width at 13° pitch) |
| ceiling | Z2 + 2.60 = **8.62**, flat, the same plane over the platform, stair head and hallway | 2.40 clear over the platform; the loft door head architrave stops only ≈ 0.09 below it (hr_v4_361) |

There is **no step between the stair head and the rooms at the rear**: the carpet runs level from the study
threshold to the platform riser (hr_v5_0, hr_v5_2). "There's a step here" in v4:f_0371 is the platform step.

### Plan (inside faces, counter-clockwise)

```
(-0.65, 6.88) (0.15, 6.88) (0.15, 8.73) (0.22, 8.73) (0.22, 11.30) (0.22, 11.57)
(0.30, 11.57) (0.30, 12.94) (-0.65, 12.94)
```

| zone | x | y | floor Z | notes |
|---|---|---|---|---|
| A platform | −0.65 … 0.15 (0.80) | 6.88 … 8.13 (1.25) | 6.22 | loft door in the south wall; balustrade on the east edge over the stairwell |
| B stair head | −0.65 … 0.15 | 8.13 … 8.73 (0.60) | 6.02 | east edge (x 0.15) is the top nosing of `stairs2`: three kite winders turn down to the south inside x 0.15 … 0.99, y 8.13 … 8.73 |
| C hallway, front part | −0.65 … 0.22 (0.87) | 8.73 … 11.30 (2.57) | 6.02 | east wall carries switch, harbour painting, socket, then the purple-room door |
| arch wall | — | 11.30 … 11.57 (0.27 thick) | 6.02 | clear opening x −0.65 … 0.22 |
| D hallway, rear part | −0.65 … 0.30 (0.95) | 11.57 … 12.94 (1.37) | 6.02 | bathroom door, socket pier, study door in the end wall |

```
   y
 13.04 +----[ study door ]--+            STUDY (neck) beyond
 12.94 +--------------------+
       | 3-cat frame   pier | S3 + 2 dbl sockets     x 0.30
       |                    > bathroom2 door (hinge S)
 11.57 +--)  ARCH        (--+
 11.30 +--)   0.87       (--+  <- arch wall 0.27
       |                 > purple door (610, hinge N)
       | cottage         |
       | painting        | dbl socket                x 0.22
       |                 | harbour painting   [ purple room behind ]
       | papyrus         | S1
  8.73 |              +--+-----------+  <- old rear wall of main house
       |  stair head  | winders  \   |
  8.13 +==step up=====N...........\..|     N = newel (0.15, 8.13)
       | tree-of-life :  flight    | |
       |  platform    :  down to   | |     [skylight over x -0.10..0.75,
       |  Z 6.22      :  the south | |      y 6.98..7.83]
  6.88 +-[loft door]--+-(bulkhead)-+-+
     -0.65          0.15           0.99
```

Wall thicknesses assumed: hall / purple and hall / bathroom partitions 0.10 (room faces at x 0.32 and 0.40),
study door wall 0.10 (y 12.94 … 13.04), loft door wall 0.10 (y 6.78 … 6.88).

## 2. Openings

Heights are above the floor on the hallway side unless stated. All leaves are the same door as the ground
floor: **golden-oak veneer, Victorian 4-panel** (two tall upper panels over two short lower panels, raised and
fielded, ovolo bead), 35 mm, **polished-brass lever on a rectangular backplate** at 1.00 m, three brass butt
hinges. Sampled #C3B286 / #856F4F; true **#B8915A**. Every doorway has a **brass threshold strip** (carpet
both sides, tiles in the bathroom).

| id | wall | clear opening | leaf | hinge / swing | evidence |
|---|---|---|---|---|---|
| `d_loft` | south wall y 6.78 … 6.88 | x −0.555 … 0.055 (0.61), sill at **Z 6.49**, head Z 8.47 | 610 × 1981 (aspect 3.17 in hr_v5_0 — narrow door) | hinge **west** jamb, swings **south into the loft office** (leaf seen open on the right in hr_v5_163); handle on the east side | v5:f_0140, f_0160–f_0166; v4:f_0360–f_0362, f_0378 |
| `d_purple` | east wall x 0.22 … 0.32 | y 10.59 … 11.20 (0.61), head 1.99 | 610 × 1981 | hinge **north** jamb, swings **east into the purple room**, stands open ≈ 90° along that room's north wall | v4:f_0382–f_0388 (three hinges on the far jamb), f_0436; hr_v5_2 (threshold 0.56–0.62 long) |
| `d_bath2` | east wall x 0.30 … 0.40 | y 11.70 … 12.39 (0.69), head 1.99 | 686 × 1981 | hinge **south** jamb, swings **east into the bathroom** (leaf on the right as you enter) | v5:f_0001–f_0010, f_0128 |
| `d_study` | end wall y 12.94 … 13.04 | x −0.525 … 0.175 (0.70), head 1.99 | 686 × 1981 (opening aspect 2.78 → 0.70–0.72; a 711 leaf is possible, a 762 is not) | hinge **west** jamb, swings **north into the study**, parks flat against the west wall | v4:f_0382–f_0386, f_0442–f_0444; v5:f_0002 |
| arch | y 11.30 … 11.57 | x −0.65 … 0.22 (0.87) | — | open | v4:f_0370, f_0382–f_0388; v5:f_0001; v6:f_0001 |
| stairwell | east edge of zones A and B | — | — | balustrade (A) / top nosing (B) | v4:f_0354–f_0360, f_0374–f_0378; v5:f_0140–f_0144 |
| skylight | ceiling | x −0.10 … 0.75, y 6.98 … 7.83 (0.85 square) | fixed flat rooflight | not openable | v4:f_0360–f_0366; v5:f_0152–f_0156 |

Architraves: white, moulded (ogee + bead), ≈ 75–85 mm wide, top at 2.07, plinth-less (they run to the floor;
the skirting butts them). The `d_loft` frame fills the full 0.80 m width of the platform: its east architrave
stops against the handrail end, the west one against the party wall. The `d_study` frame fills the end wall the
same way (≈ 25 mm of wall each side).

### The "massive step" at `d_loft`
Below the loft door the wall shows a **white-painted, wood-grain-textured riser board 0.27 high × 0.67 wide**,
flush with the hallway face of the wall, between the two architraves which run on down to the platform floor.
On top of it a **polished-brass nosing strip** (≈ 30 mm) and the loft carpet. The closed leaf therefore stands
with its bottom edge 0.27 above the platform carpet (v5:f_0140, f_0164–f_0166, hr_v5_163).

### The arch ("really simplistic arch")
A plain plastered **semicircular arch**, radius 0.435, **springing at 1.74, crown at 2.17**, in a 0.27 m thick
cross wall; square arrises, no architrave, no imposts, no corbels, no keystone. On the west it dies straight
into the party wall face (no pier). On the east the jamb is the 0.27 deep reveal in line with the front
hallway's east wall (x 0.22); **dado rail and skirting return through that reveal**. North of the arch the
east wall steps back 0.08 to x 0.30, so the arch wall shows an 0.08 nib on its north face. 0.43 m of wall
stands above the crown and carries the cornice on both faces.

## 3. Architecture and trim

- **Platform step (zone A / B, y = 8.13).** One riser of 0.20, carpet wrapped over a rounded nosing, running
  from the newel to the west wall. The **dado rail and the skirting both jump up 0.20** at this line on the
  west wall (short vertical kinks, v5:f_0001 crop `c_v5_0_far.jpg`, v4:f_0374).
- **Balustrade (zone A east edge, x = 0.15, y 6.88 … 8.13).** Same joinery as the ground-floor stair: dark
  **mahogany-stained newel** 90 × 90 with chamfered square blocks, vase-turned shaft and a **ball finial**
  (top ≈ 1.20 above the platform) standing at (0.15, 8.13) on the corner of the platform nosing; mahogany
  handrail (≈ 65 × 55, moulded) at 0.95 above the platform, housed into the loft door wall beside the
  architrave; **13–14 white turned spindles** (41 mm square blocks top and bottom, vase turning) at ≈ 90 mm
  centres, on a white moulded landing string with cut brackets on the stairwell face (v5:f_0140, hr_v5_139;
  v4:f_0354, f_0378). True colours: mahogany **#3B211A**, white **#F4F2EC**.
- **Bulkhead over the flight.** The loft-office floor crosses the stairwell at the loft door wall line
  (y 6.88): seen from the stair head as a white band with a small moulding along its lower edge, soffit about
  0.60 above Z2, under which the flight descends (v4:f_0354–f_0358). Detail belongs to `stairs2`.
- **Dado rail**: white moulded rail ≈ 60 mm deep, **centre 0.96 above the floor** (top 0.99), on the west
  wall for the whole length, on the east wall of zones C and D, through the arch reveal, across the door pier,
  and round the stairwell walls where it rakes down with the flight (`stairs2`). It butts every architrave.
- **Skirting**: white, 0.17 high, torus-and-ogee top like the ground floor; returns round the arch jamb and
  the stairwell corner.
- **Cornice**: a plain white plaster **cove, ≈ 0.10 × 0.10**, no enrichment (the dentil / modillion cornice of
  the ground floor does not come up here). It runs along the west wall from the loft door wall to the study
  door wall, along the east wall of zones C and D, across both faces of the arch wall and across the end wall.
  At the stairwell corner (0.22, 8.73) it returns east along the stairwell's north wall. The stairwell's east
  wall has only a thin shadow bead at the ceiling (v4:f_0360, v5:f_0152–f_0154).
- **Skylight shaft**: square opening 0.85 × 0.85 with a plastered, white, vertical-sided shaft ≈ 0.35 deep up
  to a frameless flat glass rooflight (visible glass ≈ 0.75 square). Its south edge is ≈ 0.10 from the loft
  door wall; it straddles the balustrade, lighting both the platform and the flight (hr_v4_361, hr_v5_153).
  The roof over the landing is therefore **flat** at about Z 9.05.
- **Pier between `d_bath2` and the end wall** (east wall, y 12.47 … 12.94, ≈ 0.47 wide): flat, dado rail
  across it, carries switch S3 and two double sockets (v5:f_0004–f_0007).

## 4. Surfaces and colours

| surface | sampled sRGB | true colour (estimate) | finish |
|---|---|---|---|
| walls above the dado | #D1CEC2 (v4:f_0384), #B8B6AB (v5:f_0001), #E1E5EA (stairwell, daylight from the skylight) | **#F2F0EA** — same white as the ground-floor hall | matt emulsion |
| walls below the dado | #A4A293 (v4:f_0384), #A3A095 (v6:f_0001), #9B9B92 (v5:f_0001); lower / upper ≈ 0.78 | **#C8C5BB** — same light warm grey as the ground-floor hall (`hall_dado_grey`) | matt emulsion |
| dado rail, skirting, architraves, balustrade string and spindles, step riser at `d_loft` | #C2C2BB in shade | **#F4F2EC** | satin / gloss |
| ceiling, cove, arch soffit, skylight shaft | #C2C0B3 | **#F4F3EE** | matt |
| carpet (hall, platform, stair, all rooms on this floor) | #AEABA3, #9E9A8F, #C8C7C4, #B8B6B5 | **#B9B4AB** light grey-beige plush twist / saxony with strong pile shading (footprints read darker) | — |
| oak doors | #C3B286, #856F4F (shade) | **#B8915A** | satin lacquer |
| brass thresholds, levers, hinges | — | **#B08D3F** | polished |
| newel and handrail | — | **#3B211A** | gloss varnish |

## 5. Fixed fittings

| item | position (world x, y; z above local floor) | description | frames |
|---|---|---|---|
| Double socket (harbour-painting wall) | east wall x 0.22, y 10.28, z 0.30 | white 2-gang switched socket 146 × 86; a white plug-in unit sits in it (omit the plug-in) | v5:f_0132; v6:f_0001–f_0003 |
| Two double sockets (pier) | east wall x 0.30, y 12.56 and y 12.78, z 0.30 | two white 2-gang switched sockets side by side, 60 mm apart, bottom edge 0.10 above the skirting | v5:f_0002–f_0007 |
| Smoke alarm | ceiling (−0.22, 9.75) | white disc Ø 0.13 × 0.04 | v4:f_0370; v5:f_0001 |
| Second ceiling disc | ceiling (0.00, 10.60) | white disc Ø 0.12 with a dark rim (heat alarm or sounder) | v4:f_0370; v5:f_0152 |
| Ceiling fitting north of the arch | ceiling (−0.18, 12.25) | shallow white dome Ø 0.15 (seen only obliquely: downlight or detector, see doubts) | v5:f_0001 (top left) |

No radiator, no thermostat and no loft hatch were seen on this landing.

## 6. Furniture
None. The landing is kept clear.

## 7. Art, mirrors, decor

All frames hang 15–25 mm off the wall. None of them may show people: W2 has figurative panels and is therefore a
generic texture, not a crop. z is the frame centre above the local floor
(for item W1 that is the platform, Z 6.22). The owner's rule applies: every picture in place, with its real
image where a clean view exists.

| # | item | wall, centre | outer W × H (m) | z centre | description | best frames |
|---|---|---|---|---|---|---|
| W1 | Tree-of-life with birds | west wall x −0.65, y 7.62 (platform) | 0.56 × 0.76 portrait | 1.60 | black-ground painting on a papyrus / bark sheet with a deckled edge, a brown tree with eight pale birds; very wide cream mount; **ornate gold frame ≈ 45 mm with a rope-twist sight edge** (true #B79A4B) | v5:f_0146 (oblique, reflections of the skylight) |
| W2 | Egyptian papyrus — **GENERIC, no crop** | west wall, y 8.95 | 0.62 × 0.98 portrait | 1.58 | large painted papyrus floated on a cream mount; **plain black frame 25 mm**. The real sheet has figurative panels (stylised human figures), so **do not rectify it from the footage**: author a generic papyrus texture — fibrous tan ground (#C9B487) with a deckled edge and **abstract horizontal pattern bands only** (lotus / zigzag / chequer borders, columns) in turquoise (#3F8F8A), ochre (#B8862E) and red (#9C3B2A); no figures, no hieroglyph text | v4:f_0370 (hr_v4_369) for size, position and palette only |
| W3 | Thatched cottage with flowers | west wall, y 10.72 (opposite the purple-room door, its north edge 0.25 before the arch) | 0.65 × 0.52 landscape | 1.62 | bright impasto oil: thatched cottage on the right, big tree, flower beds, blue shadowed path; **gold swept frame 55 mm** (true #C2A24A) | v4:f_0386 (hr_v4_385), f_0384 |
| W4 | Three cat photographs | west wall, y 12.30 (between the arch and the study door) | 0.28 × 0.78 portrait | 1.72 | three sepia cat photographs stacked in one blue-grey mount with gold slips; **dark walnut moulded frame 30 mm** (true #3A281E). Cats only, usable as a crop | v4:f_0442 (hr_v4_441), v5:f_0001 |
| E1 | Harbour with junk | east wall x 0.22, y 9.75 | 0.98 × 0.68 landscape | 1.60 | blue-grey harbour scene: a dark-sailed junk at the left, a waterfront skyline with a clock tower, stormy sky, green-blue water; wide cream mount (≈ 90 mm); **bright gold frame 45 mm with a fine beaded sight edge** (true #C9AE55) | v5:f_0134–f_0136 (hr_v5_135, frontal), v6:f_0001–f_0003 |
| N1, N2 | Two cat drawings | stairwell north wall (y 8.73, facing south), x ≈ 0.45 and 0.85, stepping down to the east with the winders | 0.45 × 0.33 landscape each | ≈ 1.45 and ≈ 0.95 above Z2 | pencil / wash studies of a sitting cat and a lying tabby, white mount with a dark red-brown inner line, **narrow brushed-gold frame 18 mm** — part of the cat series up the stair (`stairs2` owns the rest) | v4:f_0370 (right edge), v5:f_0152–f_0156 (hr_v5_153) |

## 8. Lighting and switches

**Downlights** — recessed white-bezel LED spots Ø ≈ 85 mm, warm white (≈ 3000 K), flush in the flat ceiling:

| id | position (x, y) | zone |
|---|---|---|
| L1 | (−0.25, 8.40) | over the stair head |
| L2 | (0.57, 8.45) | over the winders (pair with L1, side by side) |
| L3 | (−0.22, 9.30) | hallway front part |
| L4 | (−0.22, 10.20) | hallway front part |
| L5 | (−0.22, 11.00) | hallway, just before the arch |

(v5:f_0152–f_0154 hr_v5_153, v4:f_0362, f_0368–f_0370, v5:f_0001.) There is no downlight over the platform —
the skylight is there. Whether a sixth spot sits north of the arch is not certain (see doubts).

**Switches** (white moulded plastic, square-edged rocker plates, z = centre above the local floor):

| id | plate | position | controls |
|---|---|---|---|
| S1 | 1-gang rocker | east wall x 0.22, **y 9.10**, z 1.20 — just south of painting E1 (v5:f_0138, v4:f_0380) | hallway downlights L1–L5 (two-way with S2 and with the first-floor landing plate — owner on the first floor: "here I can also turn on the second floor lights", v4:f_0311) |
| S2 | 1-gang rocker | west wall x −0.65, **y 7.02**, z 1.22 above the platform, tight against the loft door architrave (v5:f_0146–f_0150) | hallway downlights L1–L5 — the owner's demonstration: "there's a switch here… you can turn on and off the spotlight for the 2nd floor hallway" |
| S3 | 1-gang rocker | pier, east wall x 0.30, **y 12.68**, z 1.22 (above the dado, over the two sockets; v5:f_0005) | `bathroom2` lights (inferred: it is outside the bathroom door, and the owner turns the bathroom lights on right after showing it; `bathroom2` to confirm) |

Daylight: the skylight over the platform, plus borrowed light through whichever room doors stand open.

## 9. Reference frames

| frame (still) | shows | camera (world, approx.) |
|---|---|---|
| v4:f_0354–f_0358 (hr_v4_354) | looking down the flight from the stair head: winders, newel, landing string, bulkhead, cat prints | (0.0, 8.5), looking south and down |
| v4:f_0360–f_0362 (hr_v4_361) | newel, balustrade, loft door, **skylight**, two downlights | (−0.2, 8.6), looking south and up |
| v4:f_0364–f_0366 | skylight shaft close-up | under the skylight, looking up |
| v4:f_0368–f_0370 (hr_v4_369) | whole hallway to the rear: papyrus W2, arch, purple door, study door, ceiling fittings | platform (−0.2, 7.9), looking north |
| v4:f_0374 (hr_v4_373) | platform step from above, newel, winders, west-wall skirting jump | platform (−0.25, 7.8), looking north and down |
| v4:f_0378 (hr_v4_377) | platform, balustrade, loft door with its riser | (−0.3, 8.9), looking south-east and down |
| v4:f_0380 | switch S1, dado, stairwell corner | (−0.3, 9.2), looking east |
| v4:f_0382–f_0386 (hr_v4_383, _385) | **arch**, cottage painting W3, purple door (hinges), bathroom and study doors, cove cornice | (−0.25, 9.3), looking north; level camera at 1.51 m |
| v4:f_0388 (hr_v4_387) | arch jamb reveal with dado and skirting, purple door leaf | (−0.3, 10.3), looking north-east |
| v4:f_0440–f_0442 (hr_v4_441) | study door from the hall, W4 | (−0.2, 11.8), looking north |
| v4:f_0540 | looking back from the study door through the arch to the loft door | (−0.2, 13.1), looking south |
| v5:f_0001 (hr_v5_0) | the whole hallway to the front: arch from the north, bathroom door, W4, W3, platform step, loft door | (−0.2, 12.9), looking south, 26° down |
| v5:f_0002–f_0003 (hr_v5_2) | **top-down plan view**: study threshold, pier sockets, bathroom threshold, arch jamb, purple threshold, stairwell, platform riser | study doorway, looking south and 63° down |
| v5:f_0004–f_0007 | pier: S3, two double sockets, dado, both architraves | (−0.3, 12.6), looking east |
| v5:f_0132–f_0138 (hr_v5_135) | socket, painting E1, switch S1 | hallway, looking east |
| v5:f_0140–f_0144 (hr_v5_139) | **platform step, balustrade, loft door** | (−0.3, 9.0), looking south and down |
| v5:f_0146–f_0150 | W1, switch S2, loft door architrave | platform, looking west |
| v5:f_0152–f_0156 (hr_v5_153) | skylight from below, downlights L1–L5, cornice return at the stairwell, N1, N2 | platform, looking north and up |
| v5:f_0160–f_0166 (hr_v5_163) | **the massive step** square-on, loft door open | platform (−0.25, 7.6), low, looking south |
| v6:f_0001–f_0003 (hr_v6_0) | hallway to the rear, E1, socket, purple door open | (−0.2, 9.4), looking north |
| v6:f_0005–f_0007 | winders from the stair head | (0.0, 8.5), looking down |

## 10. Interactions

| object | type | detail |
|---|---|---|
| `d_loft` leaf | hinge | vertical axis at (−0.555, 6.83), opens ≈ 95° south into the loft office; modelled closed (v5:f_0140) — the owner opens it in v5:f_0158–f_0166. `blocks` the doorway; the visitor must climb 0.27 at the threshold |
| `d_purple` leaf | hinge | axis at (0.27, 11.20), modelled open 90° into the purple room (`on=True`), closes to the west |
| `d_bath2` leaf | hinge | axis at (0.35, 11.70), modelled open 90° into the bathroom; "doors can open and close" (v5:f_0009) |
| `d_study` leaf | hinge | axis at (−0.525, 12.99), modelled open 90° against the study's west wall |
| S1, S2 | light | each toggles `landing2` (L1–L5) |
| S3 | light | toggles `bathroom2` |
| skylight | — | fixed, no interaction |

Walking: the collision floor must carry the two level changes — +0.20 at y 8.13 (zone B → A) and +0.27 at the
loft door threshold (y 6.88) — and the stairwell opening east of x 0.15 between y 6.88 and 8.73 (guarded by
the balustrade in zone A, open to the winders in zone B).

## Doubts

1. **Z2 = 6.02** is taken from `stairs2` (F1f 3.42 + 13 risers × 0.20) and `landing1` (F1f = quarter
   landing 2.85 + 3 risers). My own count from hr_v4_354 and hr_v6_9 is 3 winders + about 10 straight goings
   + the top riser = 14 risers. `green_bedroom` and the front elevation still quote F1f 3.22–3.23; if that
   wins, Z2 drops by 0.20. All levels here are relative to Z2 so they follow whatever is settled.
2. **Massive step 0.27** (0.23–0.31). The platform step is taken as one stair riser (0.20) without an
   independent measurement.
3. **Depth of the stair-head opening** (zone B, y 8.13 … 8.73): three stills give 0.40, 0.47 and 0.61 m; 0.60
   is used because it equals the ground-floor half-landing and puts the newel on the ground-floor flight's top
   riser line. If `stairs2` needs a full 0.84 square for the winders, move the newel / platform step south
   (y 7.89) and shorten the platform, keeping the loft door wall at 6.88 ± 0.15.
4. **Platform length 1.25** (spindle count 13–14 × 90 mm; perspective gives 0.9–1.4) and so the position of
   the loft-office north wall (y 6.88 hallway face). `loft_office` must use the same line.
5. **Hallway width**: 0.80 on the platform (fixed by the 610 door set filling it), 0.87 in the front part,
   0.95 beyond the arch. The 0.08 step in the east wall at the arch is seen in the top-down still but is small;
   a single width of 0.90 would also be defensible.
6. **Door sizes**: loft and purple doors 610 (aspect and threshold length agree); study and bathroom doors
   686 (study opening measures 0.70–0.72).
7. **Arch**: crown 2.17 and springing 1.74 depend on the camera-to-arch distance (±0.10); wall thickness 0.27
   (0.20–0.30). Whether the west springing has a few-centimetre nib is not resolved.
8. **Sixth downlight / detector north of the arch**; exact x of all ceiling fittings (±0.15).
9. **S3 controlling the bathroom** is inferred. S1 / S2 two-way wiring is inferred from the owner using S2 and
   the first-floor plate.
10. **Skylight size** 0.85 square (0.75–0.95) and its exact x; it may be centred on the 1.64 m wide space
    (x 0.17) rather than at x 0.32.
11. Cornice on the stairwell's east wall and above the loft door: read as absent (shadow bead only).
12. What lies behind the east wall between y 8.73 and the purple room (old rear wall plus a ≈ 0.35 m void or a
    thicker wall) is unseen.
13. **Disagreements with neighbouring specs written in parallel** (for the reconciler):
    - `stairs2` / `landing1` put the stairwell north wall at **y 8.97** with a 0.84 square of winders
      (R13 along x 0.15 from y 8.13 to 8.97). Here the wall is at **8.73** (the ground-floor line) and the
      opening is 0.60 (measured 0.40–0.61). If 8.97 is adopted, slide the south end of the east wall and
      switch S1 / painting E1 north by up to 0.24 and keep everything from the purple door northwards.
    - `landing1` has the first-floor arch wall at y 11.10 … 11.45; the second-floor arch here is at
      11.30 … 11.57. They are almost certainly one wall line: a common 11.25 … 11.52 fits both within error.
    - Unscaled chain for re-anchoring (f = 865 px, metres south of the study threshold): bathroom door
      0.56–1.25, arch wall 1.36–1.62, purple door 1.70–2.30, stairwell corner 4.07, platform riser 4.25–4.55,
      loft door wall ≈ 5.8; study threshold to rear wall 3.5–3.7.

## Reconciled dimensions (house.next.json)

Added by the phase-2 reconcile step. `spec/house.next.json` is canonical; where the text above differs, the values below win. Reasons and evidence: `spec/RECONCILE2.md` (decision ids in brackets).

Levels unchanged: stair head and hallway 6.02, platform 6.22, loft 6.49, ceiling 8.62 [L3, L4]. In `house.next.json`
the landing is two rooms: `landing2_platform` and `landing2_head`.

| item | this spec | reconciled | why |
|---|---|---|---|
| platform | y 6.88..8.13 (1.25 long) | **y 6.23..8.13 (1.90 long)** | [S2] loft door wall from `loft_office.md` |
| loft door wall | y 6.78..6.88 | **y 6.13..6.23** | [S2] |
| `d_loft` | 610 leaf, x -0.555..0.055 | unchanged; step 0.27 | [S4] |
| stair head, north wall 8.73 | - | unchanged | [S1] confirmed for all floors |
| arch wall | y 11.30..11.57 | **y 11.20..11.50** | [P3] |
| hallway rear part | y 11.57..12.94 | y 11.50..12.94 | |
| `d_purple` | y 10.59..11.20 | **y 10.49..11.10** | moves with the purple room |
| `d_bath2` | y 11.70..12.39, 686 | **y 11.57..12.33, 762** | bathroom analyst's measurement |
| `d_study` | x -0.525..0.175 | x -0.518..0.168 (686) | |

- **Skylight x -0.20..0.70, y 6.38..7.28 (0.90 square)** [verification T2]: it is keyed to the loft-door wall, south
  edge 0.15 north of the wall face (section 3 says "about 0.10 from the loft door wall"; v4 stills t360 / t362 / t378),
  and moves with that wall if S2 is ever revised. The first reconcile had left it at y 6.98..7.83, 0.75 from the wall.
- **South side of the well** [verification T1]: the "(bulkhead)" drawn in the plan above is a flat wall in the plane of
  the loft-door wall (north face y 6.23) over x 0.15..0.99, from the first-floor landing ceiling to the second-floor
  ceiling (`w_well_s_2`). The platform handrail dies into it just east of the loft-door architrave. The loft's cabinet
  block is behind it and does not project into the well.
- Items on the platform walls keyed to the riser keep their y; switch S2 moves with the loft door to about y 6.37.
- **W2 (Egyptian papyrus): no crop** [verification INV-07] — see the note under section 7.
- Polygon of `landing2_head`: (-0.65, 8.13) (0.15, 8.13) (0.15, 8.73) (0.22, 8.73) (0.22, 11.50) (0.30, 11.50)
  (0.30, 12.94) (-0.65, 12.94).

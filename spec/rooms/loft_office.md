# loft_office — second-floor front office in the converted loft

Source: v5 f_0158–f_0262 and f_0306–f_0346 (daylight, lights on). Full-res stills, gridded crops and montages in
`reference/work/p2_second_front/` (`hr_NNN.jpg` = full-res still of v5 frame NNN). Owner narration
(v5 02:40–04:21, 05:11–05:36): "there's a massive step in here, remember you get this right … you can turn on
… this is the front office on the second floor … there's a radiator, this is a converted loft so you can see
that the ceiling is sloped … there's a Velux window here that can be opened, opened like this, and it can be
closed … this should be an empty wall with no decoration … a radiator, door can open and close, make sure you
get this right, this is a very deep cabinet with massive drawers, all these can open and close … there's a
telly and I got a massive computer screen, computer screen, workstation, plant, and a chair … there's a door
here, there's another door here, and there's a cabinet here, bookshelf … make sure you get the dimensions
right".

The two hatches in the front knee wall and the one in the rear knee wall lead to `eaves` (see `eaves.md`).

**Dimension confidence.** Heights and the roof pitch come from floor back-projection of three stills
(`hr_346` west wall, `hr_344` TV wall, `hr_183` east wall; f = 860 px) scaled by the built-in cabinet
(lever-arch files 0.318 m → cabinet 2.06 m high) and by the 1.981 m door: apex ceiling 2.12 ± 0.06, front knee
0.92 ± 0.05, rear knee 1.42 ± 0.06, **pitch 30° ± 3°** (the west wall gives 30.6°, the TV wall 29.7°; raw
image angles read 35–37° because the ultrawide stretches the upper part of the frame). Plan dimensions along
Y ± 0.15 internally; **the absolute Y of the whole room ± 0.3** (it is tied to the roof: see §1.3). X is the
full width between the party walls (± 0.05, from `house.json`).

## 1. Shape & dimensions

### 1.1 Frame and level
All coordinates are **world** X, Y (BRIEF frame). Heights `z` are above this room's finished floor.

- **Floor level: world Z = 6.45** (green-bedroom ceiling 6.17 + ≈ 0.28 floor). It is **0.45 above the
  second-floor hall**: one carpeted riser of ≈ 0.19 across the hall at the stair newel (hall 6.00 → strip
  beside the stairwell 6.19), then the **"massive step" of 0.26 ± 0.04 at the loft door** — a white-painted
  timber riser under the door threshold with a brass nosing strip (v5:f_0145, f_0162–f_0167, `hr_166`).
- Optional room-local frame: local x = X + 0.65, local y = Y − 2.54 (origin = SW corner of the front knee
  wall, axes parallel to world).

### 1.2 Plan
Full width between the party walls, under the main roof ridge, which runs **parallel to the street (along
X)**. The room is bounded front and rear by timber knee walls; its NW corner is taken out by the entrance
lobby and the built-in cabinet block (the stair dormer stands behind them).

Polygon (room faces, counter-clockwise):
`(-0.65, 2.54) (4.30, 2.54) (4.30, 6.59) (1.25, 6.59) (1.25, 5.38) (0.31, 5.38) (0.31, 6.13) (-0.65, 6.13)`

- Width **4.95** (x −0.65 … 4.30). Depth **4.05** in the east part (y 2.54 … 6.59), **3.59** along the west
  wall to the door (y 2.54 … 6.13).
- **Lobby**: x −0.65 … 0.31, y 5.38 … 6.13 (0.96 × 0.75), flat ceiling 2.08.
- **Cabinet block**: x 0.31 … 1.25, y 5.38 … 6.13 (the door-wall line; an earlier draft ran it to 6.59, into the
  stair well — see "Reconciled dimensions"); its south face is the cabinet front, its east face is the "TV wall",
  which continues north to the rear knee wall as the stair flank wall.

| wall | plane | height | what is on it |
|---|---|---|---|
| front knee wall | y = 2.54 | 0.92 | west hatch, bookcase, east hatch |
| W-east (party), **dark grey** | x = 4.30 | gable, apex 2.12 | air-con, periodic-table poster, prints, desk |
| rear knee wall | y = 6.59, x 1.25 → 4.30 | 1.42 | rear hatch, wall of framed certificates, Velux above |
| TV wall (block east face) | x = 1.25, y 5.38 → 6.59 | 2.12 → 1.42 | TV, medal rail, two small frames |
| cabinet front | y = 5.38, x 0.31 → 1.25 | 2.06 | "very deep cabinet with massive drawers" |
| lobby east wall | x = 0.31, y 5.38 → 6.13 | 2.08 | dimmer, remote cradle, gilt-framed carving |
| door wall | y = 6.13, x −0.65 → 0.31 | 2.08 | the door |
| W-west (party), white | x = −0.65 | gable | blue ensign, radiator, group photographs, Union flag |

```
        landing strip (Z 6.19)   | stairwell |        rear eaves void (hatch)
 6.59                            +===========+--[rear hatch]----certificates----+
 6.13 +--[door]--+  cabinet body |  TV wall  |          (Velux in slope above)  |
      |  lobby   |---------------+ x=1.25    |   (exercise bike - omitted)   plant
 5.38 +. . . . . +==CABINET===+                                                PC|
      |Union flag   front 0.33-1.23        . . . flat ceiling strip 4.62-5.38 . |a/c
 4.62 |                                                              stool  DESK|poster
      |radiator                                                      chair      |
      |                         coffee table                                    |
      |ensign  chair                                                    trolley |
 2.54 +--[west hatch]--[bookcase]--shredder--[east hatch]------radio------------+
     -0.65  -0.35..0.70   0.75..1.65          2.45..3.50                      4.30
                                front eaves void / bay-gable void
```

### 1.3 Section (ceiling) — and the roof it implies
Looking east (front on the right in the sketch is −Y):

```
                 flat 2.12 (y 4.62..5.38)
                ________
        30 deg /        \ 30 deg
              /          \______  rear knee 1.42 (y 6.59)
   front     /                  |
   knee 0.92|                   |
   (y 2.54) |___________________|____
```

- Ceiling height above the floor: `z(y) = min(2.12, 0.92 + 0.577·(y − 2.54), 1.42 + 0.577·(6.59 − y))`.
  The front slope runs 2.08 m in plan, the flat strip is 0.76 m wide (centre y = 5.00), the rear slope
  1.21 m. The flat meets the slopes with a soft radius (≈ 50 mm) and stops against the dark gable wall with
  rounded corners (v5:f_0183, f_0233).
- **Roof geometry for the exterior model.** The two ceiling planes extended reach the floor level at
  y ≈ 0.95 and y ≈ 9.05 — the inner faces of the front and rear walls of the main house body — and meet at
  y = 5.00, z 2.34. So the main roof is a **symmetric duo-pitch over the main body, ridge parallel to the
  street at y ≈ 5.00, pitch 30°**. Adding ≈ 0.31 m (vertical) for plasterboard, rafters and covering:
  - **ridge: world Z ≈ 9.15** (ceiling planes meet at 8.79; flat ceiling at 8.57);
  - **front eaves**: roof surface ≈ Z 6.64 over the outer face of the front wall (y 0.74), **gutter line
    ≈ Z 6.45–6.50** at y ≈ 0.47; the eaves is at loft-floor level, so the eaves voids are true triangles;
  - rear eaves would mirror it at y ≈ 9.5, but the rear slope is cut off (see `eaves.md` §1): on the west by
    the flat-roofed stair dormer (x < 1.25, starting at the ridge flat), on the east by the wall of the
    second-floor rear rooms.
  - The **bay gable** intersects the front slope: its ridge runs along Y at x ≈ 2.53 with the inside flat
    strip at z 0.90 (world 7.35), i.e. it dies into the main slope at the height of the front knee wall.
  - `front_elevation.md` infers the eaves gutter at Z 5.95; that is below the green bedroom's flat ceiling
    (6.17) and cannot be right for the main roof — it must be reconciled (see Doubts).

## 2. Openings

### 2.1 Door from the landing (door wall y 6.13–6.23)
- Clear opening **x −0.55 → 0.21** (0.762 × 1.981), centre (−0.17, 6.18). Standard oak-veneer 4-panel leaf,
  true **#B8905A**, polished-brass lever on backplate at z 1.00, three brass butt hinges.
- **Hinged on the west jamb (x −0.55), opens south into the lobby** and parks against the west party wall
  (it covers the north end of the Union flag when open) — v5:f_0160–f_0163, f_0210–f_0212.
- White moulded architrave 70 mm, head at z 2.05, both sides. Loft side: the lobby is exactly the width of
  door plus architraves.
- **Step**: threshold at loft-floor level; on the hall side a white-painted riser 0.26 high directly under
  the door with a brass nosing bar; the door frame stands on top of it.

### 2.2 Velux roof window (rear slope)
- One white-painted roof window, **0.78 wide × 1.18 long** (MK06 size), in the rear slope above the
  certificates: **x 2.76 → 3.54**, lower edge at y 6.45 / z 1.50, upper edge at y 5.48 / z 2.06 — it takes
  almost the whole slope between the knee wall and the flat. Plasterboard reveals: head reveal horizontal,
  sill reveal vertical, sides square; white.
- **Top-hung, opening outward**: the owner turns the handle bar on the **bottom** rail and pushes the sash
  out ≈ 30° ("opened like this, and it can be closed") — v5:f_0188–f_0200.
- Blinds on the sash: a dark grey blackout roller (parked across the top quarter when filmed) and a white
  pleated blind (drawn across in f_0190–f_0200).
- View out (north): the dark grey panel-clad cheek of the stair dormer on the left with white fascia and
  black gutter, a yellow-rendered rear wall with a felt flat roof beyond, aerial and dish; sky.

### 2.3 Knee-wall hatches (pairs of flush doors, all open outward into the room)
| hatch | wall | frame (outer) | leaves | notes |
|---|---|---|---|---|
| front west | y = 2.54 | x −0.35 → 0.70, z 0.15 → 0.85 | two, 0.45 × 0.60 each (z 0.20 → 0.80) | behind the Chippendale chair; "another door here" |
| front east | y = 2.54 | x 2.45 → 3.50, z 0.15 → 0.85 | two, 0.45 × 0.60 | opens onto the bay-gable void; "this goes to the front" |
| rear | y = 6.59 | x 1.40 → 2.45, z 0.17 → 1.20 | two, 0.47 × 0.95 (z 0.22 → 1.17) | beside the TV wall; "also going to a storage area" |

Leaves: plain flat white MDF, 18 mm, lay-on, on concealed sprung cup hinges fixed to the **outer** stiles
(each leaf swings away from the centre, ≈ 110°); small polished-brass mushroom knob Ø 30 on each leaf 60 mm
from the meeting edge, at mid height (front) / z 0.80 (rear). Frame: white moulded picture-frame architrave
≈ 60 mm, mitred, sitting on the skirting.

## 3. Architecture & trim
- **Skirting**: white, ≈ 0.15 high, torus/ogee top, on every wall and knee wall and round the cabinet block.
- **Front knee wall**: flat white, capped at z 0.88–0.92 by a small projecting moulded rail (like a dado
  rail, ≈ 35 mm proud) on which the slope lands (v5:f_0247–f_0254).
- **Rear knee wall**: flat white with **applied panel mouldings** (plain rectangular frames of 25 mm bead)
  on the part next to the TV wall and round the hatch; no capping rail, the slope starts at a plain arris at
  z 1.42 (v5:f_0312–f_0315, f_0336–f_0338).
- **Cabinet block** (§5.1): fluted pilasters, frieze and a stepped cornice; the cornice returns on the lobby
  side and dies into the rear slope on the TV side.
- **Lobby**: plain opening the full height of the lobby (no door, no architrave); its flat ceiling (2.08) is
  ≈ 40 mm below the main flat, giving a shallow downstand at y 5.38.
- No cornice, dado or picture rail anywhere in the room. No chimney breast shows on either party wall.
- West and east walls are full gables, cut by the knee walls and slopes exactly as §1.3.

## 4. Surfaces & colours
| surface | material | sampled sRGB (frame) | estimated true colour |
|---|---|---|---|
| east gable wall | matt emulsion, **dark blue-grey / anthracite** | #474D53, #34383B (hr_183) | **#3B4046** |
| west wall, knee walls, block, lobby | matt white with a hint of warmth | #AEAAA2 (hr_344), #A4A098 (hr_313) | **#EFEDE7** |
| slopes and flat ceiling | matt white (reads pale grey in the shade of the slope) | #C5C4BF, #9C9B99 | **#F2F1EC** |
| woodwork: skirting, hatches, cabinet, architraves, step riser | white satin | #C8C6BE, #D0D2D1 | **#F4F3EF** |
| floor | **carpet**, deep-pile saxony/velvet, pale silver-beige with a sheen (shows footprints and nap shading) | #CDC6B3, #DED4B9 | **#CFC9BC** |
| door | oak veneer | #C4B052 (under the spot) | **#B8905A** |
| radiator | white gloss | — | **#F5F5F3** |
| Velux frame and reveals | white | — | **#F4F3EF** |

## 5. Fixed fittings

### 5.1 Built-in cabinet — "a very deep cabinet with massive drawers"
- White painted joinery filling the south face of the block: **x 0.33 → 1.23 (0.90 wide), front at y 5.38,
  2.06 high**, carcass ≈ 0.75 deep (back at the door-wall line, y ≈ 6.13).
- **Pilasters**: 0.10 wide each side, three flutes, on a plain plinth block 0.15 high, with a small moulded
  cap at z 1.89. **Frieze** z 1.89 → 1.96 (plain). **Cornice** z 1.96 → 2.06: two fascias and a cyma,
  projecting 0.07, mitred round both ends.
- **Lower part — four drawers**, z 0.09 → 0.86, each front 0.68 wide × 0.185 high with 6 mm gaps, flat slab
  fronts set between the pilasters. Each has a **polished-brass card holder** (70 × 40 mm, top-centre) with a
  plain coloured card — from the top: dark red, mustard, dark green, pale blue (no writing) — and below it a
  **brass swan-neck bail pull** (100 mm centres). Boxes ≈ 0.62 wide × 0.70 deep on full-extension runners;
  the owner pulls the top drawer and the third drawer out ≈ 0.55 m (v5:f_0219–f_0227).
- **Ledge** at z 0.88, then an **open compartment** z 0.88 → 1.89, 0.68 wide, with two fixed 20 mm shelves
  at z 1.25 and z 1.50 (bays of 0.37 / 0.23 / 0.37). White inside. Contents to model generically: a white
  laser printer and a black box on the ledge, a black inkjet on the middle shelf, a row of black lever-arch
  files and coloured folders on the top shelf — **blank spines, no labels or logos**.

### 5.2 Radiator (west wall)
White horizontal **column radiator**, round-topped tubular sections (19–20 sections at ≈ 63 mm), **1.25 long
× 0.52 high × 0.10 deep**, y 3.25 → 4.50, z 0.13 → 0.65, 40 mm off the wall on two brackets; chrome/white
valves at both bottom ends, pipes into the floor. (The owner says "a radiator" twice, both times this one;
no second radiator is seen.)

### 5.3 Air-conditioning unit (east wall)
White split-system indoor unit **0.80 w × 0.29 h × 0.21 d**, rounded front, centred y 5.00 directly under the
flat ceiling, z 1.78 → 2.07; its white remote sits in a wall cradle in the lobby (§8).

### 5.4 Television (TV wall, x = 1.25)
50-inch flat TV, **1.11 × 0.64**, thin black bezel, on a flat bracket: y 5.46 → 6.57, z 0.75 → 1.39 (its top
north corner is just under the slope). **Screen blank.**

### 5.5 Sockets and switches
- Lobby east wall (x 0.31): white **rotary dimmer** (1-gang, round knob) at y 5.83, z 1.22; white remote
  cradle beside it at y 5.70, z 1.22.
- Rear knee wall: white double socket at x ≈ 3.95, z 0.30 (v5:f_0341–f_0342). The sockets behind the desk
  are hidden; assume one double socket on the east wall at y 4.2 and y 5.2, z 0.30.

## 6. Furniture
| item | footprint (world) | size (w × d × h) | description |
|---|---|---|---|
| **desk** ("workstation") | x 3.50 → 4.30, y 3.60 → 5.40 | 1.80 × 0.80, top z 0.74 | electric sit-stand desk, oak-effect top 40 mm (**#C9A66B**), black steel T-legs and crossbar, black felt desk mat 0.90 × 0.40 |
| **"massive computer screen"** | on the desk, centre y 4.25, 0.15 from the wall | 1.20 × 0.37 panel, top z 1.25 | 49-inch curved ultrawide on a black stand — **blank** |
| second monitor | on the desk, centre y 5.05 | 0.61 × 0.36, top z 1.25 | 27-inch on an arm — **blank**; black webcam on top |
| laptop + stand, keyboard, mouse | desk, centre y 4.45 | — | grey laptop (lid open, blank), slim grey keyboard |
| desk lamp | desk, y 5.30 | reach 0.5 | black architect lamp with a conical shade on a clamp |
| PC tower | floor, centre (4.05, 5.65) | 0.23 × 0.50 × 0.50 | black case, dark glass side, small status LEDs |
| **plant** | NE corner, centre (4.10, 6.32) | Ø 0.30 × 0.60 | artificial pothos in a woven seagrass basket |
| drawer trolley | x 3.75 → 4.30, y 2.75 → 3.20 | 0.45 × 0.55 × 0.85 | oak-effect frame with four white wire-mesh baskets |
| **office chair** ("a chair") | centre (3.05, 4.35), facing east | 0.68 × 0.68 × 1.25 | ergonomic mesh chair: white shell, grey mesh seat/back/headrest, flip-up arms, polished 5-star base on castors |
| stool | centre (3.15, 5.35) | 0.55 × 0.35 × 0.48 | piano-stool with hinged lid in cream/mauve check, dark tapered splayed legs |
| **bookshelf** | x 0.75 → 1.65, y 2.54 → 2.84 | 0.90 × 0.30 × 1.05 | rustic oak open bookcase, chunky 40 mm top with rounded corners, three shelves, T&G back (**#A9824F**); a few books and plain boxes; small incense burner on top |
| chair | centre (0.20, 3.00), facing north | 0.55 × 0.50 × 0.97 | Chippendale-style dining chair, dark mahogany (**#2B1A14**), pierced interlaced splat, cabriole front legs with ball-and-claw feet, drop-in seat in cream Jacobean floral (reds, teal, ochre) |
| coffee table | x 0.95 → 1.95, y 3.15 → 3.65 | 1.00 × 0.50 × 0.45 | rustic oak, square legs, low shelf |

Declutter (omit): the Wattbike exercise bike and its floor mat in front of the rear knee wall (centre
≈ (2.6, 5.9)), backpack, camera tripod, paper shredder, cutting mat, site radio, storage tubs, water jug,
throws on the floor, everything on the desk except the items listed, cables.

## 7. Art, flags, decor
**Privacy:** almost everything framed in this room is a group photograph of people or a personal certificate.
Keep the frames at their positions and sizes; fill them with neutral content (plain cream paper with a faint
border for certificates, soft abstract landscape for photographs). No names, crests, units or dates.

| wall | item | position | size | treatment |
|---|---|---|---|---|
| W-west | **blue ensign**, hung vertically | y 2.65 → 3.15, z 0.13 → 0.95 | 0.50 × 0.82 | navy field **#1B2247**, Union canton at the top; omit the badge |
| W-west | **Union flag**, hung vertically from two pins | y 4.60 → 5.58, z 0.13 → 1.65 | 0.98 × 1.52 | cloth with slight ripples; red **#B4262B**, blue **#232B5C**, white **#EDEBE4** |
| W-west | black shadow-box frame | y 2.95 → 3.20, z 1.00 → 1.32 | 0.25 × 0.32 | neutral |
| W-west | two walnut-framed photographs with cream mounts | y 3.30 → 3.88 and 3.93 → 4.38, z 0.78 → 1.26 | 0.58 × 0.48, 0.45 × 0.48 | neutral |
| W-west | panoramic photograph, black frame | y 3.40 → 4.38, z 1.32 → 1.58 | 0.98 × 0.26 | neutral |
| W-west | small black frame | y 4.12 → 4.50, z 1.62 → 1.92 | 0.38 × 0.30 | neutral |
| W-west | certificate, thin black frame | y 4.60 → 5.18, z 1.70 → 2.06 | 0.58 × 0.36 | blank cream sheet |
| W-east | framed **periodic table** poster | y 4.57 → 5.47, z 1.13 → 1.75 | 0.90 × 0.62 | generic periodic table grid is fine; thin dark frame |
| W-east | two small frames north of the poster | y 5.52 → 5.90, z 1.50 → 1.78 (gilt) and z 1.15 → 1.45 (burgundy mount) | 0.38 × 0.28, 0.38 × 0.30 | abstract colour blocks |
| W-east | certificate with a red seal | y 5.98 → 6.30, z 0.95 → 1.38 | 0.32 × 0.43 | blank sheet, red disc |
| rear knee | **seven framed certificates** | upper row of four x 2.62 → 4.18, z 0.80 → 1.30; lower row of three x 2.62 → 3.80, z 0.25 → 0.70 | each ≈ 0.34 × 0.48 | mixed black / gilt / walnut frames, dark mounts; blank cream sheets, small red disc on two |
| TV wall | two small photographs above the TV | y 5.47 → 5.79, z 1.50 → 1.77 (limed frame); y 5.88 → 6.14, z 1.48 → 1.73 (rustic dark frame) | 0.32 × 0.27, 0.26 × 0.25 | neutral |
| TV wall | **medal rail** | brass rail y 5.55 → 6.30 at z 0.72 | 0.75 long | ≈ 8 plain coloured ribbons 0.40 long with plain discs — no text |
| TV wall, floor | **three cat pictures** leaning against the wall | at y 5.45, 5.80, 6.15 | 0.30 × 0.38, 0.28 × 0.36, 0.17 × 0.22 | oak frames; cats among flowers — rectified crops allowed from v5:f_0344 / f_0336 (`hr_344.jpg`) |
| lobby east | **carved panel in a gilt frame** | x 0.31, centre y 5.72, z 1.42 → 2.02 | frame 0.40 × 0.60, moulding 0.09 wide, deep scoop | dark hardwood relief (bird among flowers and scrolling leaves) 0.19 × 0.40, wood **#57483B**, gilt **#C9B36B**; crop / normal map from v5:f_0175 (`hr_172.jpg`) |

"This should be an empty wall with no decoration" (v5:f_0204) is said while pointing at the west wall above
the radiator — the owner wants that wall **plain** in the model: keep the two flags and the radiator, and
treat every frame on the west wall as optional (default: omit them).

## 8. Lighting and switches
- **Recessed LED downlights**, white bezels Ø 85 mm, ≈ 3000 K: **six in the main room** — three along each
  edge of the flat ceiling strip, at about x 0.6 / 2.3 / 3.7 on y 4.75 and y 5.25 — and **one in the lobby
  ceiling** at (−0.17, 5.75). Count and positions ± 0.4 (seen: v5:f_0171–f_0172, f_0182–f_0188, f_0204–f_0206,
  f_0212, f_0346).
- **The rotary dimmer in the lobby (§5.5) switches and dims all of them** — the owner turns the knob on
  entering and the room lights come up ("you can turn on", v5:f_0169–f_0173).
- Desk lamp: own switch. No pendant, no wall lights.
- For reference (belongs to `landing2`): the single rocker on the landing's west wall just outside this door
  (v5:f_0147–f_0150) works "the spotlight for the second floor hallway".

## 9. Reference frames
| frame | shows | camera (world) |
|---|---|---|
| v5:f_0145, f_0162–f_0167 | the step and door from the landing, view through to the front knee wall | landing strip, looking −Y |
| v5:f_0169–f_0175 | lobby: dimmer, cradle, carved panel, lobby spot, slope beyond | (−0.2, 5.9) looking +X / up |
| v5:f_0177–f_0180, f_0204–f_0209, f_0346 | west wall: ensign, radiator, frames, Union flag, slope profile (`hr_346`, `hr_206`) | (2.3, 4.0) looking −X |
| v5:f_0181–f_0188, f_0233–f_0236 | east wall: gable shape, air-con, poster, desk (`hr_183`, `hr_235`) | (1.5, 4.5) looking +X |
| v5:f_0187–f_0200, f_0312–f_0314, f_0339–f_0342 | rear slope and knee wall: Velux closed/open, certificates, rear hatch, socket (`hr_313`, `hr_194`, `hr_198`) | (1.6, 4.6) looking +Y |
| v5:f_0202–f_0203, f_0343–f_0345 | TV wall, medal rail, cat pictures, block profile (`hr_344`) | (3.2, 4.6) looking −X / +Y |
| v5:f_0212–f_0216 | door closed from inside, lobby ceiling, cabinet front (`hr_212`, `hr_214`) | (0.0, 4.6) looking +Y |
| v5:f_0215–f_0231 | cabinet: pilasters, cornice, shelves, drawers opened (`hr_229`) | (0.9, 4.3) looking +Y |
| v5:f_0237–f_0246 | desk, screens, PC, plant, chair, trolley | by the desk |
| v5:f_0244–f_0250 | front knee wall, east hatch, capping rail (`hr_246`) | (2.8, 3.8) looking −Y |
| v5:f_0251–f_0261, f_0290–f_0294 | west hatch, Chippendale chair, bookcase (`hr_252`) | (0.6, 4.0) looking −Y |
| v5:f_0311 | whole room looking east from the chair (`hr_311`) | (0.3, 3.3) looking +X |

## 10. Interactions
| object | action | evidence |
|---|---|---|
| door | hinged west jamb, swings 90° into the lobby | "door can open and close" (f_0210) |
| dimmer | turn → all room and lobby downlights on / dim / off | f_0169–f_0173 |
| Velux | handle on the bottom rail, sash swings out ≈ 30° about its top edge; closes | "a Velux window here that can be opened" (f_0187–f_0200) |
| Velux blinds | pleated white blind and grey blackout blind slide along the sash | seen in two positions |
| cabinet drawers (4) | each slides out 0.55–0.65 m | "all these can open and close" (f_0219–f_0229) |
| front west hatch (2 leaves) | each leaf swings out ≈ 110° on its outer edge | f_0295–f_0310 (west leaf opened) |
| front east hatch (2 leaves) | same | f_0262–f_0266, f_0286–f_0289 (west leaf opened) |
| rear hatch (2 leaves) | same | f_0316–f_0320, f_0333–f_0335 (west leaf opened) |
| TV, monitors | on/off optional — always a blank or abstract screen | — |
| air-con | louvre opens (optional) | — |
| office chair | swivels | — |

## Doubts
1. **Absolute Y of the room (± 0.3).** It is set by making the two 30° ceiling planes land on the front and
   rear walls of the main house body (y 0.95 and 9.05; the measured internal section spans 8.09 m, the body
   is 8.1 m deep) — ridge at y 5.00, loft door wall y 6.13–6.23. If instead the door wall stacked on the
   green bedroom's rear wall (y 4.73–4.87) everything here would move 1.3 m toward the street and the front
   eaves void would have no depth, which contradicts the footage. `landing2` / `stairs2` must agree: landing
   strip beside the stairwell x −0.65 … ≈ 0.20, from the loft door (y 6.23) 2.0 m back to the top newel
   (y ≈ 8.2); the hall step is at the newel.
2. **Eaves level.** This spec gives the front gutter ≈ Z 6.45–6.50 and the ridge ≈ 9.15;
   `front_elevation.md` has the gutter at 5.95 (inferred) and the ridge ≈ 9.0. The interior cannot be
   reconciled with 5.95 unless the pitch is steeper than 30° or the loft floor lower than 6.45.
3. **Loft floor Z 6.45** = green-bedroom ceiling (6.17, `green_bedroom.md`) + 0.28; the hall at 6.00 follows
   from the two steps (0.19 + 0.26). `stairs2`' riser count should confirm 6.00.
4. Apex ceiling 2.12 could be 2.05–2.20 (scale from the cabinet); keep the pitch and the knee-height ratios
   (0.43 and 0.67 of the apex) if it changes.
5. Flat strip width 0.76 (0.70–0.85); soft radius at its edges not measured.
6. Cabinet depth 0.75 and drawer depth 0.70 are estimates; the carcass may run under the stair dormer.
7. Downlight count (6 + 1) and positions.
8. Radiator section count/pitch; 1.25 × 0.52 fits the frames between the flags.
9. Velux size (MK06 assumed) and its X (± 0.2); whether it is top-hung only or also pivots.
10. Hatch positions along the knee walls ± 0.15; knob heights.
11. The lobby ceiling being 40 mm lower than the main flat is a weak reading of v5:f_0213–f_0214.
12. "Empty wall with no decoration": taken to mean the west wall above the radiator; the owner may have
    meant only the group photographs.

## Reconciled dimensions (house.next.json)

Added by the phase-2 reconcile step. `spec/house.next.json` is canonical; where the text above differs, the values below win. Reasons and evidence: `spec/RECONCILE2.md` (decision ids in brackets).

- **Floor Z 6.49** (was 6.45): platform 6.22 + 0.27 [L4]; add +0.04 to every world Z in this spec (flat ceiling
  8.61, ceiling planes meet at 8.83, ridge **9.14**, front roof surface 6.68 over the wall face, gutter about 6.50).
- Plan polygon, knee walls, slopes, Velux and hatches: **unchanged**; this spec's Y anchor is adopted for the whole second
  floor front (ridge y 5.00, door wall y 6.13..6.23) [S2, E4].
- **Door: 610 leaf, clear x -0.555..0.055** (was 762, x -0.55..0.21) [S4]; the lobby stays 0.96 wide, so there is 0.25
  of wall east of the architrave.
- **Cabinet block: x 0.31..1.25, y 5.38..6.13** (0.75 deep; section 1.2 had y 5.38..6.59) [verification T1]. It stops
  at the loft-door wall line: its north side is the stair well's south wall (`w_well_s_2`, y 6.13..6.23), one flat plane
  with the loft-door wall, and the well is open to the ceiling north of y 6.23 (v4 stills t360 / t362 / t378). The
  drawers (0.70 deep, section 5.1) therefore run over the first-floor front landing only, not over the well. North of
  y 6.13 the "TV wall" is simply the stair flank wall (x 0.99..1.25) carried up, with the open well behind it; the room
  polygon is unchanged.
- Hall levels: second-floor hall 6.02, platform 6.22 (this spec had 6.00 / 6.19).
- East wall is external (side alley). Stair dormer: flat roof Z 8.87 over x -0.88..1.35 from y 5.47.

## Round 3 corrections (core owner, from build/rooms2_open.md)
- 3 There is no capping rail on the front knee wall (v5 f_0249, hr_246: a plain arris).
- 6 The bookshelf is 0.90 high, its top level with the 0.92 knee wall (hr_172, hr_252).
- 7 Delete the row 'W-east certificate with a red seal, y 5.98..6.30': it duplicates the rear knee wall's fourth upper
  certificate (x 3.84..4.18, with seal), seen across the corner in hr_183 / f_0240. The dark east wall is bare there.
- The 'very deep cabinet' has its hollow in loft_block now (house.json loft_cabinet_recess, x 0.44..1.12,
  y 5.38..6.08, Z 6.58..8.38): the 0.70 m drawers run north to y 6.05 (v5 f_0214-f_0216, hr_229).
- The roof window's frame and sash are white below the roof plane, with an operating bar on the low rail (hr_313,
  hr_194); its sash and the blackout blind exclude each other. The eaves-rear hatch's west leaf opens 95 degrees (its
  knob clears the TV).

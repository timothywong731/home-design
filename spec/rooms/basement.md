# basement — cellar stair and plant / store room (level -1)

Source: **v6** (`reference/v6`, daylight video PXL_20261119_111552021) frames **f_0095–f_0306**; full-res stills,
crops and 8-frame montages in `reference/work/p2_basement/` (`hr_N.jpg` / `t_N.jpg` are the still at t = N s,
i.e. frame **f_(N+1)**; `m_N.jpg` are montages starting at frame N). Owner narration (v6 transcript 01:33–05:05):
"this door leads to the basement … this goes further down, negative one floor … this one turns on the basement
light … this is very, really narrow, got a fire extinguisher here … these are wooden effect tiles and the walls
are all beige … if you look up the stairs it looks like that … this is the basement, I got the boiler and all the
pipe work here … a massive tanker here, hot water tank, all the water pipe controls are in here … there's a blue
storage rack in here … walls are white … I got two lights here … there is the electrical box here and there is a
network cabinet … a small gap towards here … these are the boiler controls … boiler is quite big … behind here
there's a gap that is disused, sealed off … there's a gas meter here … gas pipes … now let's walk back up to the
ground floor … remember this, you should get this part right, there's corners here … the corners design, the
corners ends this way".

**What it is.** The ground-floor "under-stairs cupboard door" (`d_understairs` in `spec/house.json`, centre
(0.57, 7.63), facing north into the kitchen lobby) is in fact the **basement door**. Behind it a very narrow
tiled stair runs **south, straight down under the main staircase** (8 treads), turns **east** through two winders
at the bottom, and passes through an opening in a thick spine wall into a single low room that lies **under the
kitchen**. There is no window and no other door.

**Dimension confidence.** Riser count 11 — certain (counted independently from above in f_0121 and from below in
f_0155). Riser height 0.21 ± 0.01 (one 200 mm plank per riser) → basement floor **Z = -2.31 ± 0.12**. Stair
clear width 0.665 ± 0.03 (threshold strip = door clear width; top riser 8 % wider). Going 0.21 ± 0.015. Room
ceiling height 2.00 ± 0.07 (cylinder 1.72 + plinth, 1.80 m racking + boxes touching the ceiling, double socket as
scale). Room plan: E–W 3.00 ± 0.20, N–S 3.63 ± 0.25 (sum of known objects along each wall; plank counts; the room
is assumed to stack under the kitchen walls where the evidence allows). Positions along walls ± 0.10–0.15,
heights ± 0.05. Colours: the video is LED-lit with HDR, all whites sample warm-grey.

## 1. Shape, levels and dimensions

**Frame.** World axes are used directly (no local frame): X to the right walking in from the street, Y into the
house, Z up, ground-floor finished floor Z = 0. Heights written **h** are above the basement finished floor;
**Z = h − 2.31**.

| part | plan (world x, y; inside faces) | floor Z | ceiling |
|---|---|---|---|
| **Stair shaft** (straight flight) | x 0.265 → 0.93 (0.665 clear), y 5.92 → 7.60 | steps, Z −0.21 … −1.68 | raked soffit of the main staircase, see 3.3 |
| **Stair foot / winders** | x 0.265 → 0.93, y 5.10 → 5.92 (0.665 × 0.82) | winder treads Z −1.89 and −2.10 | same raked soffit, coved into the south wall at Z ≈ +0.15 |
| **Opening in the spine wall** | x 0.93 → 1.25 (wall thickness 0.32), y 5.10 → 5.92 (0.82 wide) | winder tread W1, Z −2.10 | lintel soffit h 1.85 (Z −0.46) |
| **Basement room** | L-shaped, see polygon | **Z −2.31** | flat, **h 2.00 (Z −0.31)** |

Room polygon (counter-clockwise, inside faces):
`(1.25, 5.10) → (3.90, 5.10) → (3.90, 6.60) → (4.25, 6.60) → (4.25, 8.73) → (1.25, 8.73) → (1.25, 5.92)` and
back to the start across the stair opening. Main rectangle 3.00 × 3.63 (x 1.25 → 4.25, y 5.10 → 8.73) less the
projecting **chimney-breast base** in the SE corner (x 3.90 → 4.25, y 5.10 → 6.60, 0.35 × 1.50). Floor area
≈ 10.4 m².

| wall | plane | what is on it (detail in §5–7) |
|---|---|---|
| **W** (spine wall, stair behind it) | x = 1.25, y 5.92 → 8.73 (2.81) | stair opening at its south end; low double socket; key-board plaque; two stacked consumer units; network cabinet in the NW corner; trunking at the top; shoe racks on the floor |
| **N** | y = 8.73, x 1.25 → 4.25 (3.00) | blank rough-rendered wall; trunking at the top; red expansion vessel low at the east end |
| **E-north** (party-wall side) | x = 4.25, y 6.60 → 8.73 (2.13) | plywood backboard with boiler (north end), pipework, controls; hot-water cylinder standing in front of its south part; sealed recess ("the gap") high up at its south end |
| **breast return** | y = 6.60, x 3.90 → 4.25 (0.35) | plain |
| **E-south** (breast face) | x = 3.90, y 5.10 → 6.60 (1.50) | access hatch with a small blue cross hanging from it; low socket |
| **S** | y = 5.10, x 0.265 → 3.90 | two bays of blue racking (x 2.07 → 3.87); gas meter niche (x 1.55 → 1.85); gas valve and boxed bulkhead at the top (x 1.25 → 1.45); continues west as the end wall of the stair foot |

Plan (not to scale; top = +Y / rear of house, right = +X / party wall):

```
 y 8.73 +----------+-----------------------------------------------+
        | (solid   | NET   .  N wall: blank, trunking    red vessel|
        |  ground  | CAB                                   [BOILER]| y 8.17..8.61
        |  under   |                                       | ply   |
 y 7.60 +--door--+ | CU   (shoe racks)        light B      | board |
        |R1      | | CU                         o          | pipes |
        | T1..T8 | |                                       |( CYL )| axis (3.93, 7.20)
        |  down  | | plaque                                |(tank )|
        |   |    | |                                       +-recess| y 6.60..7.05 high level
        |   v    | | socket                            +---+ y 6.60
 y 5.92 +R9------+-+ pier          light A             | breast    |
        | W2  /    R11 (step up)     o                 | hatch +   |
        |   / W1   :          GAS    [ rack ][ rack ]  | cross     |
 y 5.10 +----------+---------METER--------------------+-----------+
        x 0.265  0.93 1.25   1.55..1.85   2.07 .. 3.87  3.90      4.25
```

Relationship to the ground floor (`spec/house.json`): the stair shaft is inside the `stairs` polygon
(x 0.15 → 0.99, y 4.83 → 7.58), under the main flight and behind the white panelled spandrel; the spine wall is
under `w_stair_kitchen` (faces 0.99 / 1.25); the room's W, N and E-north faces are under the kitchen's west
(1.25), north (8.73) and east (4.30, here lined to 4.25) faces. The south wall (5.10) is 0.21 south of the
kitchen's south face (5.31), i.e. under the unseen `cross_wall_zone` (4.73 → 5.31). West of the spine wall and
north of y 7.60 (under the lobby) is solid ground — nothing is excavated there.

## 2. Openings

### 2.1 Basement door — `d_understairs` (ground level, wall `w_understairs`, y 7.58 → 7.68)
- Clear opening x 0.265 → 0.875 (**0.61**), 1.981 high, threshold at Z = 0. **Hinged on the east jamb**
  (x 0.875; polished-brass butt hinges — two visible, assume three — f_0286, f_0290), **opens north into the kitchen lobby**; fully open
  it stands at ≈ 95–100° along x ≈ 0.88, in front of the kitchen doorway (f_0143, f_0270, f_0281).
- Leaf: light-oak veneer **Victorian 4-panel** (two tall upper panels over two short lower panels, raised and
  fielded, ovolo bead), 1981 × 610 × 35, satin lacquer, same door as the other oak 4-panel doors; sampled
  #776442, neutral **#B8915A**. Polished-brass **scroll lever on a shaped backplate** (≈ 150 × 45 mm) on both
  faces, lever axis h 1.00, on the west (latch) stile (f_0284, f_0276).
- Frame / architrave: white gloss moulded architrave ≈ 70 mm on the lobby face (existing spec) **and on the stair
  face** (f_0143, f_0270: architrave 70 mm, head at Z 2.06, the east leg is partly cut by the stair's east
  wall). White gloss lining ≈ 100 mm deep. Sampled #D8D7D2, neutral **#F4F3EF**.
- Threshold: hall oak boards run to the lining; a **ribbed aluminium stair-nosing strip** (two black anti-slip
  inserts, ≈ 55 mm wide, full clear width) caps the edge, then the first riser drops immediately — there is no
  landing inside the door (f_0121, f_0127, f_0272).

### 2.2 Opening from the stair foot into the room (through the spine wall)
- Plain plastered opening, **no door, no frame**: x 0.93 → 1.25 (0.32 reveal), y 5.10 → 5.92 (**0.82 wide**),
  head **h 1.85** (Z −0.46). North jamb = the square south end of the spine wall ("pier", f_0155, f_0157); south
  jamb = the south wall running straight through (f_0246, f_0259). Arrises square, slightly eased by the plaster.
- Seen from the stair side the wall above the opening rises ≈ 0.6 m to the raked soffit, so the head reads as a
  deep white lintel (f_0266); seen from the room the head is level with the underside of the trunking on wall W
  and the room ceiling is only 0.15 higher (f_0193).
- The bottom riser **R11** stands in the room-side face of the opening (x = 1.25), so from the room it is a
  single 0.21 step up into the opening (f_0193, f_0246, f_0259).

### 2.3 Windows
None. The only other "opening" is the **sealed recess** in wall E-north (§3.5) and the **access hatch** in the
breast (§5.6); neither leads anywhere.

## 3. Architecture and trim

### 3.1 Stair — 11 risers, 0.21 rise, 0.21 going
Straight tiled flight of **9 risers** (R1–R9) descending south, then **2 winder risers** (R10, R11) turning 90°
left (east). Pitch ≈ 45° — noticeably steeper than the main staircase above (39.6°).

| riser | plan position | lower level it drops to |
|---|---|---|
| R1 (top, under the aluminium nosing) | y = 7.60, x 0.265 → 0.93 | tread T1, Z −0.21 |
| R2 … R8 | y = 7.60 − 0.21 × (k − 1) → 7.39, 7.18, 6.97, 6.76, 6.55, 6.34, 6.13 | T2 … T8, Z = −0.21 k (T8 = −1.68) |
| R9 (last straight riser) | y = 5.92, x 0.265 → 0.93 | winder tread **W2**, Z −1.89 |
| R10 (diagonal winder riser) | straight line from the pier's room-side corner **(1.25, 5.92)** to the SW corner of the stair foot **(0.265, 5.10)** | winder tread **W1**, Z −2.10 |
| R11 (bottom) | x = 1.25, y 5.10 → 5.92, faces east into the room | room floor, Z −2.31 |

- **W2** is the polygon (0.265, 5.92) (0.93, 5.92) (1.25, 5.92) (0.265, 5.10): a triangle against the west wall
  plus a thin wedge in front of the pier's south face. **W1** is the triangle (1.25, 5.92) (1.25, 5.10)
  (0.265, 5.10) against the south wall. R10 and R11 both start at the pier's room-side corner (f_0157, f_0262,
  f_0264, f_0259, top view f_0129).
- Treads and risers are each faced with **one uncut plank of the wood-effect tile** (no joints across the 0.665
  width); square arris with a thin pale edge trim / grout line at every nosing; risers vertical, no overhang.
  On W1 and W2 the planks are laid parallel to R10 (diagonal joints, f_0129, f_0262).
- A **white stepped bead** (painted plaster / sealant, ≈ 15–25 mm) follows every tread and riser against both
  walls — visible as a white saw-tooth line (f_0121, f_0129, f_0264). No string, no skirting, **no handrail**.

### 3.2 Stair walls and ledges
- **West wall** (hall side). Lower wall (masonry, below hall floor level) face **x = 0.265**. At ground-floor
  level it steps back to the thin upper wall (the back of the panelled spandrel), forming a **level shelf at
  Z ≈ −0.03** that runs the full length from the south end wall to the door architrave, where it meets the
  architrave foot just under the threshold (f_0143, f_0272). Shelf depth **0.11** (upper face x ≈ 0.155) for
  y 5.10 → 6.45 and only ≈ 0.04 (upper face x ≈ 0.225) from y 6.45 to the door — there is a small square jog in
  the upper wall at y ≈ 6.45 (f_0121, f_0126). The shelf is capped with a **white-painted timber board ≈ 35 mm
  thick with a bullnose front edge and a small cavetto bed-mould under it**, oversailing the lower wall ≈ 20 mm;
  the paint is cracked and flaking just under it (f_0135–f_0137, f_0143). The owner's ornaments stand on the
  wide south part (§7).
- **East wall** (spine wall). Lower wall face **x = 0.93** up to a **level ledge at Z ≈ −0.50**; above it the
  wall is set back ≈ 0.05 (x ≈ 0.98, the ground-floor stair/kitchen wall). The ledge is plain plaster, square
  edged, no cap. It runs from the south end (over the stair opening, where it is the top of the lintel) north to
  y ≈ 7.15, where the rising treads (T3 nosing) pass through its level and it stops with a small square end
  (f_0143, f_0153, f_0268, f_0270).
- **South end wall** (y = 5.10): plain, full height to the cove.

### 3.3 Stair ceiling
The plastered **underside of the main staircase**: a raked plane parallel to the main flight (rise 0.19 in 0.23),
Z ≈ 2.10 at the door falling to ≈ 0.75 over R9 and ≈ 0.15 at the south wall, into which it turns with a soft
**cove of ≈ 0.15–0.20 radius** (f_0121, f_0127, f_0133). Just inside the door there is a flat strip ≈ 0.25 deep
at Z 2.10 and a small square downstand rib ≈ 40 × 40 mm across the shaft before the rake starts (f_0143,
f_0270). Because the basement stair is steeper than the main flight, headroom grows going down: ≈ 2.10 at the
door, ≈ 2.3 over T1, ≈ 2.45 over T8.

### 3.4 Room
- **No skirting, no cornice, no dado** anywhere; walls meet the tile floor with a 5–8 mm white sealant bead.
- **Ceiling**: flat plasterboard at h 2.00. It stops ≈ 0.12–0.20 short of wall E-north for the whole length of
  the plywood board (y 6.60 → 8.73), leaving a ragged-edged slot through which the pipes rise into the floor
  void, widening to a notch ≈ 0.30 × 0.45 in the NE corner over the boiler where the flue and cables go up
  (f_0165, f_0175, f_0217–f_0221). Dark void visible inside (model: a black-painted recess 0.2 deep).
- **Pier** = south end of the spine wall, x 0.93 → 1.25 at y 5.92, square, full height to the lintel.
- **Boxed bulkhead** ≈ 0.12 wide × 0.15 deep at the top of the south wall from x 1.45 west through the stair
  opening (it carries the gas pipe; the pipe enters its square open end at x ≈ 1.45, f_0246, f_0256). A slight
  vertical boxing ≈ 0.10 wide × 0.05 proud on the south wall at x ≈ 1.10 → 1.20, floor to head (f_0246, f_0259).
- **Chimney-breast base** (SE): plastered, square arrises, x 3.90 → 4.25, y 5.10 → 6.60, full height.
- **Low slab** on the floor against wall N near the NE corner (pale stone-coloured slab(s) ≈ 0.9 × 0.5 × 0.05,
  x ≈ 2.9 → 3.8) — loose spare paving, **omit**.

### 3.5 The sealed recess — "a gap that is disused, sealed off" (f_0227–f_0237, f_0179)
In wall E-north immediately north of the breast return, hidden behind the cylinder: a rough rendered niche
**y 6.60 → 7.05 (0.45 wide), h 1.25 → 1.85**, ≈ 0.45 deep. Its floor is a **slope rising away from the room at
≈ 35°** (front lip h 1.25, back h ≈ 1.55), the back and sides are vertical; above the main niche a rendered
shelf / lintel ≈ 0.10 thick with a second, shallow slot (≈ 0.08 high, broken edge) over it. Everything is
painted white masonry paint over coarse render; the slope is stained dusty brown (sampled #696047, neutral
**#8A7F66**). Two copper pipes cross in front of its head just under the ceiling and the right edge of the
plywood board (with a 22 mm copper pipe clipped down it) forms its left edge. Closed at the back — most likely
the trimmer arch / flue base of a former fireplace or an old coal chute. Model it as the stained niche only.

### 3.6 Ground level: door surround, overhead cupboard and "the corners" (v6:f_0280–f_0306)
The owner stops here on the way back up: "remember this, you should get this part right, there's corners
here … the corners design, the corners ends this way". This is the south-west corner of the kitchen lobby —
the wall holding the basement door (`w_understairs`, lobby face y 7.68) and the external corner at
(0.15, 7.68) where it meets the stair spandrel. It refines `hallway.md` §2.3 / §4 and `stairs.md`; build it
as below (heights here are world Z above the hall floor).

Reading the door wall from the floor up (f_0286, f_0288, f_0290):
1. **Door** in its 70 mm white moulded architrave; outer architrave edges x 0.195 and 0.945, head top Z 2.06.
   The east leg is ≈ 45 mm from the internal corner (x 0.99), where it almost touches the kitchen door's
   architrave at 90°; the west leg is ≈ 45 mm from the external corner.
2. **Boarded band** Z 2.06 → 2.30, from the east corner to the external corner: vertical white **V-jointed and
   beaded matchboarding**, boards ≈ 95 mm (8 boards), each joint a V with a small bead, gloss white.
3. **Overhead cupboard** Z 2.30 → 2.60, x 0.20 → 0.95, projecting 0.45 into the lobby (y 7.68 → 8.13). Its
   bottom is a ≈ 30 mm board whose front and west edges are worked with a **stepped / reeded moulding**
   (4–5 fine steps, ≈ 35 mm high) that oversails the box ≈ 15 mm; the front is one flat **top-hung flap**
   (shadow gap all round, ≈ 0.73 × 0.25) with a polished-brass **bow handle on two round rose plates**
   (≈ 115 mm long), placed slightly east of centre (handle centre x ≈ 0.62, Z ≈ 2.38). The west end of the box
   is a plain painted cheek.
4. **Small cornice** at Z 2.60 where the cupboard front meets the flat soffit of the half-landing: a plain run
   moulding ≈ 65 mm high × 55 mm projection (fillet, ogee, fillet, small cove) along the top of the cupboard
   front; at the cupboard's west end it **returns back along the cheek toward the door wall and dies against
   the pendant post** (mitred external corner at (0.20, 8.13)).

The external corner (f_0288, f_0298, f_0300, f_0302):
5. From the floor to Z ≈ 2.30 the corner is a plain square white arris: the boarded door wall on one side, the
   **panelled spandrel** (flat panels with a bolection bead, raked top rail following the stair string) on the
   west side.
6. Above that hangs a **square pendant post** ≈ 0.11 × 0.11 (the drop of the half-landing newel): it comes down
   the corner from the ceiling and **stops at Z ≈ 2.27**, its bottom cut square with eased (≈ 10 mm rounded)
   edges, standing ≈ 20 mm proud of both wall faces. The cupboard's reeded bottom moulding butts into its east
   face; the stair's outer string, its capping and the returned tread nosings (white blocks with a scotia
   under each) run into its south / west faces; white turned balusters and the mahogany handrail rise behind.
7. The **hall dentil (block-modillion) cornice** at ceiling level runs along the bulkhead face x 0.15 above the
   lobby and **ends against the pendant post** — the last modillion block stops ≈ 30 mm short of the post and
   the bed and crown mouldings butt into it; no return round the post is visible (f_0298, f_0300, f_0304;
   steep upward views, so treat the exact stop as ± 30 mm). On the lobby side the 2.60 soffit is flat and carries only the small cornice of item 4 along the
   cupboard; the soffit's other edges have no cornice (f_0302, f_0304).

Everything here is the same white gloss joinery paint (sampled #D8D7D2, neutral **#F4F3EF**).

## 4. Surfaces and colours

| surface | description | sampled sRGB | estimated true colour |
|---|---|---|---|
| **Stair walls and soffit** | smooth plaster, matt emulsion — the owner calls it **beige**: a warm off-white, slightly creamier than the room | #D4D3CC (E wall), #CAC7BE / #CECABF (W wall), soffit #AEA797 in shade | **#EDE7DA** walls and soffit |
| **Shelf cap, stepped bead, door joinery** | white gloss / satin | #D8D7D2 | **#F4F3EF** |
| **Room walls W, S, breast** | smooth plaster, **white** matt emulsion ("walls are white") | #D4D1C6, #D9D6CB, #D2CEC2 | **#F3F2EE** |
| **Room wall N and the wall behind the plywood** | paint over rough render / old brick — visibly **stippled, lumpy texture** (bump ≈ 2–3 mm) | #D1CDC1 | **#F1F0EB** |
| **Room ceiling** | flat plasterboard, white matt | #AEA899 (in shade) | **#F4F3F0** |
| **Floor, stair treads and risers** | **wood-effect porcelain plank ≈ 200 × 1200 mm**, weathered grey-brown oak print with dark knots and cracks, matt; in the room laid with the **long axis along Y** (north–south), random ≈ ⅓ stagger, **3 mm pale grey grout**; one plank per tread and per riser on the stair | room #665F4F, #766B52, #83765B; tread #645840, riser #4E493F / #736A5A | base **#7B6F5C**, dark streaks **#4A4339**, light areas **#9B8E77**, grout **#C6C2B8** |
| **Plywood backboard** | 18 mm softwood ply, unfinished, football-patch repairs, edge stamp lettering | #B9AC82 | **#C9B88A** |
| **Copper pipework** | 15 / 22 / 28 mm copper, lightly tarnished, soldered fittings | — | **#A86F45**, highlights #C98B5E |
| **Sealed recess slope** | render, stained | #696047 | **#8A7F66** over white |
| **Racking frame** | powder-coated steel, dark blue | #32374B | **#22306B**; shelf decks white-faced chipboard **#EDEBE2** |

Stair and room use the same tile; it is a little darker and greyer than the kitchen / utility plank
(`wc.md` base #857A68), so give it its own material.

## 5. Fixed fittings

Coordinates: world x, y; h = height above the basement floor (Z = h − 2.31).

### 5.1 Stair
- **Fire extinguisher** — red powder extinguisher ≈ Ø 0.11 × 0.37 with black hose and wall bracket, on the
  **west wall just inside the door**: centre y ≈ 7.38, on the upper wall face (x ≈ 0.23), body Z +0.38 → +0.75
  (its base ≈ 0.4 above the shelf). Red **#C8281E** (sampled #713F39 in shade), black base ring and hose
  (f_0121, f_0126, f_0143, f_0270). No readable label.
- **Light switch** — see §8.

### 5.2 Wall E-north: boiler, backboard, controls (f_0165–f_0177, f_0213–f_0225, f_0240)
- **Backboard**: plywood sheet on battens, y 7.05 → 8.70, h 0.12 → 2.00, face x ≈ 4.23.
- **Boiler** ("boiler is quite big"): white wall-hung gas system boiler, rounded-edge casing **0.44 w × 0.72 h ×
  0.34 d**, y 8.17 → 8.61, x 3.89 → 4.23, **h 0.90 → 1.62**. Satin white **#F2F2EF** (sampled #D9D7D2) with a
  **brushed-silver horizontal fascia band** ≈ 0.07 high across the full width, 0.26 above the base, dipping
  slightly at the centre (**#B9BBBD**); no badge. On top, centred, a white **Ø 100 flue turret and 87° elbow**
  rising to h 1.85 and turning north-west into the ceiling notch. Under the boiler five short pipe tails
  (copper plus one white plastic condensate) and white flex.
- **Pipework on the board** (model a believable manifold, not pipe-for-pipe): six vertical copper drops at
  y ≈ 7.42, 7.55, 7.68, 7.80, 7.92 and 8.02 from the ceiling slot to h ≈ 0.45; two horizontal headers at h 1.72
  and 1.84; diagonal sets at the top turning into the ceiling notch; **lever ball valves** with red and blue
  handles at h ≈ 1.35 on three of the drops; a grey **motorised valve head** (≈ 90 × 60 × 60) at h ≈ 1.70; a
  small **blue control box with red LEDs** (≈ 0.12 × 0.09) at y ≈ 7.45, h 1.82; a brass pressure-relief /
  tundish group beside the cylinder; white pipe clips. A **black 40 mm plastic waste pipe** runs horizontally
  along the board foot at h ≈ 0.18 for the full board length. Low on the board a red circulating-pump body
  (≈ 0.13) at y ≈ 7.85, h 0.35, and a grey galvanised adaptable box at y ≈ 7.55, h 0.30.
- **Electrical row** on the board at h ≈ 1.10: two white **fused connection units** (87 × 87) at y 7.98 and
  7.86, and a white **single 13 A socket** with a black plug-in adaptor at y 7.68.
- **"Boiler controls" sub-board**: a plywood offcut ≈ 0.50 w × 0.19 h × 18 mm screwed over the pipes,
  y 7.52 → 8.02, h 0.80 → 0.99, carrying north to south: a white **wireless receiver** ≈ 0.07 × 0.13 (tall,
  small LED), a white blank **wiring-centre box** ≈ 0.15 × 0.10, and **two white 1-gang double-pole switches
  with red neon indicators** side by side (the owner: "these are the boiler controls", f_0165, f_0175). White
  flex loops hang below.
- **Heating expansion vessel**: red steel vessel Ø 0.32 × 0.30 deep with a black cap, strapped to **wall N** at
  x ≈ 3.85, h 0.30 → 0.72 (centre 0.16 off the wall), joined by a black pipe along the wall foot. Red
  **#B43A2A** (sampled #873A2C).
- **Potable expansion vessel**: white Ø 0.27 × 0.38 vessel with a chrome band, hanging low on its pipe at
  y ≈ 7.55, x 3.95, lying on its side at h 0.05 → 0.35 (f_0165). White **#F0EFEA**.

### 5.3 Hot-water cylinder ("a massive tanker … hot water tank")
Unvented cylinder in a white casing with a **royal-blue domed top cap**: **Ø 0.555 × 1.72 high**, axis
**(3.93, 7.20)**, standing on a pale concrete paving slab 0.60 × 0.60 × 0.05 over a ply sheet (plinth top
h 0.07), so the top of the dome is at **h ≈ 1.79** (0.2 below the ceiling). Casing gloss white **#F3F2EC**
(sampled #EAE7DF), cap **#2D4FA3**, slab **#CFC8B4**. On its north-west side: a brass **temperature / pressure
relief valve** with a red cap at h 1.55, a 22 mm copper flow at h 1.60, a round white **immersion-heater cap**
(Ø 0.09) at h 0.75, a second white cap lower, and a brass **drain cock** at h 0.12 with a 22 mm copper feed
rising beside it. A rectangular label at h 1.35 (blank cream sticker, no brand text).

### 5.4 Wall W: electrical (f_0193–f_0211, f_0243–f_0245)
- **Double 13 A socket**, white, centre **y 6.21, h 0.30**.
- **Consumer units** ("the electrical box"): **two white enclosures stacked**, each ≈ 0.58 w × 0.36 h × 0.11 d
  with a curved flip-up lid split by a horizontal line, y 7.20 → 7.80; upper unit h 1.50 → 1.86, lower
  h 1.12 → 1.48, 15 mm gap; a small yellow warning label on the lower lid (plain yellow rectangle, no text).
  White **#EEEDE8** (sampled #C4C1B8).
- **Trunking**: white PVC trunking ≈ 100 × 50 along the top of wall W, h 1.88 → 1.98, from y ≈ 6.00 to the NW
  corner, with a 50 × 50 drop into the top of the upper consumer unit; it turns the corner and continues as
  ≈ 40 × 25 trunking along the top of wall N to the NE corner, where black cables leave it into the ceiling
  notch (f_0165, f_0175, f_0201). A second 50 × 25 run sits above it against the ceiling over y 7.0 → 8.73.
- **Network cabinet** ("network cabinet here"): black 19-inch wall cabinet **0.60 w × 0.50 h × 0.45 d**, back
  on wall W, y 7.98 → 8.58, x 1.25 → 1.70, **h 1.22 → 1.72**; its north side is ≈ 0.15 from wall N ("a small
  gap towards here"). **Glazed front door** (smoked glass in a 50 mm black steel frame, round chrome cam lock
  at mid-height on the south stile, hinged on the north side) facing east; removable **south side panel** with
  two slam latches and a round key lock near the top and a louvred vent slot near the bottom. Inside: a patch
  panel with blue patch leads at the top, a switch with green LEDs, loose cables (generic; emissive green
  dots). Textured black **#1B1B1D** (sampled #706C66 under glare).
- On top of the cabinet: black **6-bay NAS** ≈ 0.23 w × 0.17 h × 0.23 d, vertical drive trays facing east, no
  logo, x 1.42 → 1.65, y 8.15 → 8.38.
- Above-left of the cabinet on wall W, under the trunking: a white **brush-plate cable outlet** and a white
  **double socket**, centres y 7.83 and 7.95, h 1.84.

### 5.5 Wall S: gas meter and gas pipe (f_0182, f_0246–f_0257)
- **Meter niche**: rectangular recess in the wall, x 1.55 → 1.85 (0.30), h 1.45 → 1.88, ≈ 0.08 deep, lined with
  bare grey galvanised sheet (**#8C8C88**).
- **Gas meter**: pale grey smart meter ≈ 0.22 w × 0.20 h × 0.14 d hanging in the lower half of the niche
  (h 1.46 → 1.66, ≈ 0.07 proud of the wall face), with a small green LCD window, two round buttons and a yellow
  rectangle bottom-right (plain colour blocks, **no text or serial**). Body **#DAD9D6**. Above it a brass
  meter bar on two unions; at the top east side (left as you face it) a grey-and-green **regulator**; a
  vertical copper tail on the west side.
- **Flexible connector**: corrugated stainless pipe Ø 25 from the regulator at (x 1.78, h 1.80) sagging west
  across the niche and out along the wall to x 1.48, h 1.84, with a yellow tape band, into a brass **lever
  ball valve with a red handle** (≈ 0.11 long) at x ≈ 1.45; the pipe then disappears into the square open end
  of the boxed bulkhead (§3.4).
- Three old fixing holes in the plaster west of the niche (omit).

### 5.6 Breast face (wall E-south) (f_0179, f_0187)
- **Access hatch**: flush white plastic access panel **0.30 w × 0.45 h** with a thin frame, centre y 5.76,
  h 1.42 → 1.87.
- Low **single socket** (white) at y ≈ 5.60, h 0.42.

### 5.7 Not present
No radiator, sink, tap, extractor or smoke alarm seen in the basement.

## 6. Furniture

| item | position | size / description | keep? |
|---|---|---|---|
| **Blue storage racks** ("a blue storage rack") | two bays side by side against wall S: bay W x 2.07 → 2.97, bay E x 2.97 → 3.87; y 5.10 → 5.50 | boltless garage racking, each **0.90 w × 0.40 d × 1.80 h**, four dark-blue angle uprights with keyhole slots, blue beams, **5 white-faced chipboard shelves** at h 0.08, 0.50, 0.92, 1.34, 1.76 (f_0182, f_0184, f_0187) | **keep**; stock sparsely with a few generic items only: 8–10 plain paint tins (Ø 0.17 × 0.19, white / cream / dark lids) on the lowest shelf of bay E, 3 plain cardboard boxes, 2 white tubs — no labels, no brands |
| **Stools** | a stack of four at (3.25, 6.35); one single at (1.75, 5.45) | white round stool, seat Ø 0.32 with a ring of 8 finger holes, four splayed white steel legs, **0.45 high**; stack ≈ 0.60 high (f_0147–f_0151, f_0161, f_0184) | keep |
| **Shoe racks** | against wall W: rack 1 y 6.45 → 7.45, rack 2 y 7.50 → 8.40; depth 0.30 | rack 1: black steel-tube 4-tier, 1.00 w × 0.30 d × 0.65 h; rack 2: black 5-tier with fabric shelves, 0.90 w × 0.30 d × 0.85 h (f_0193, f_0197, f_0243) | keep the racks **empty** (shoes are declutter) or omit |
| **Brass wine cooler on stand** | floor in front of the board at (3.75, 7.95) | polished-brass bucket Ø 0.24 × 0.22 with two ring handles on a turned brass pedestal and round base, total **0.75 high** (f_0165, f_0175, f_0240). Polished brass **#C9A24A** | optional characterful piece; keep if cheap |

## 7. Art, mirrors, decor

No mirrors. Nothing here shows people.

| # | item | position | size | description | texture source |
|---|---|---|---|---|---|
| D1 | **Key-board plaque** | wall W, y 6.21 → 6.96, h 1.10 → 1.70 | 0.75 × 0.60 × 0.02 | an old **oak cathedral-arch cabinet door hung landscape** as a key board: 70 mm frame, raised panel with a shallow arched top rail, mid-brown lacquered oak (sampled #6F5639, neutral **#8A6A40**); two rows of small brass hooks (6 + 6) on the panel; a pierced brass drop handle centred on the bottom rail; hung on two brass screws above and resting on two below. Model 3–4 plain key rings only (or none) | geometry + wood material; f_0244 is frontal if a crop is wanted (keys carry no private data, but a plain panel is enough) |
| D2 | **Blue cross** | breast face, hanging on a thread from the hatch, centre y 5.76, h 1.12 → 1.25 | 0.09 × 0.13 | small plain royal-blue cross, **#2B3FA8** (f_0179) | none |
| D3 | **Green bottle** | stair west shelf, (0.21, 5.24), base Z −0.03 | Ø 0.075 × 0.30 | antique dark-green glass bottle with a long neck and a cork, translucent **#3F6B3A** (f_0134–f_0137) | none |
| D4 | **Wooden box** | stair west shelf, (0.21, 5.38) | 0.14 × 0.10 × 0.09 | old dark-oak box with a stepped moulded lid, **#4A3626** | none |
| D5 | **Card** | stair west shelf, leaning on the wall at y 5.52 | 0.14 × 0.10 | cream card — it is an old printed certificate: **render blank cream #EFE8D2** (document rule) | none |
| D6 | Small tile and block | shelf, y 5.62 and y 5.72 | 0.07 × 0.07 × 0.015; 0.08 × 0.08 × 0.03 | cream glazed tile leaning; dark wood block | none |
| D7 | Cork | shelf, y 5.15 | Ø 0.025 × 0.045 | wine cork lying on its side | none |
| D8 | **Gilt frame with fork** | stair west wall (upper face) above the shelf, centre y 5.50, Z +0.32 → +0.68, hung slightly askew | 0.09 × 0.36 × 0.03 | narrow reeded gilt frame (**#B8923F**) holding an antique two-pronged steel fork with a dark handle mounted vertically (f_0134–f_0137) | none |

## 8. Lighting and switches

| id | fitting | position | notes |
|---|---|---|---|
| L-S | round flush LED ceiling light, white body Ø ≈ 0.30 × 0.06, opal diffuser | on the raked stair soffit over the foot of the flight, plan (0.60, 5.95), Z ≈ +0.75 | f_0121, f_0127, f_0133 |
| L-A | round flush LED ceiling light, Ø ≈ 0.35 × 0.07, white, opal diffuser with a glowing side band | room ceiling, plan **(1.85, 5.95)** — in front of the gas meter / stair opening | f_0182, f_0193, f_0246 |
| L-B | same as L-A | room ceiling, plan **(2.20, 7.70)** — in front of the consumer units / cabinet | f_0155 (far), f_0197, f_0243 |

All three are cool-neutral white (≈ 4000 K), bright; "I got two lights here" refers to L-A and L-B.

**Switch SW-B** — one white **1-gang rocker switch** (86 × 86) on the stair's **east wall just inside the
basement door**: plan (0.98, 7.42), centre Z ≈ +1.20 (h is irrelevant here; it is 1.20 above the hall floor,
reached from the threshold), ≈ 0.12 south of the door architrave (f_0117, f_0119). The owner presses it and
says "this one turns on the basement light"; no other light switch is shown anywhere below, so **SW-B switches
L-S, L-A and L-B together**. The two neon switches on the boiler sub-board (§5.2) are plant isolators, not
lighting.

Sockets (none operated): wall W double at (y 6.21, h 0.30); double + brush plate by the cabinet (h 1.84);
breast single (y 5.60, h 0.42); board single and two fused spurs (§5.2).

## 9. Reference frames

All **v6**. Camera positions are world (x, y) with eye height above the local floor.

| frame | shows | camera |
|---|---|---|
| v6:f_0105 – f_0111 | basement door closed from the lobby, overhead cupboard, boarding, spandrel corner | lobby (0.3, 8.6) → south |
| v6:f_0117, f_0119 | switch SW-B, east wall, open leaf and frame | threshold, → south-east |
| v6:f_0121 | whole flight from the threshold: 8 treads + winders, both walls, shelf and ornaments, light L-S, extinguisher, nosing strip | (0.6, 7.7) eye 1.5, → south, pitched down |
| v6:f_0126, f_0127 | extinguisher and west ledge from above; flight | top steps |
| v6:f_0129 | treads from above, diagonal winder riser R10, opening on the east | on T2, → south and down |
| v6:f_0131 – f_0133 | foot of the stair: opening, end wall, coved soffit, L-S | T4 – T6 |
| v6:f_0134 – f_0137 | west shelf with cap moulding and cracked paint, ornaments D3–D8 | T5 – T7, → south-west |
| v6:f_0141 – f_0145 | "if you look up the stairs it looks like that": door, extinguisher, west shelf from below, east ledge and its end, soffit rib | T7 / T8, → north |
| v6:f_0146 – f_0151 | through the opening into the room: cylinder, racks, stools | winders, → east |
| v6:f_0152 – f_0155 | spine wall from the foot: east ledge, lintel, pier, flight going up, boiler wall beyond | W1, → north / north-east |
| v6:f_0157 | pier foot with R10 and R11 meeting at its corner | W1, → down |
| v6:f_0161 | room floor looking north: plank direction, wall N, vessel, board, cylinder plinth | (1.5, 5.6), → north, pitched down |
| v6:f_0165 – f_0177 | boiler, backboard, pipework, controls, vessels, cylinder | (2.6, 7.6), → east / north-east |
| v6:f_0179 | breast face: hatch, cross; sealed recess beside the cylinder | (2.8, 6.3), → east |
| v6:f_0182 – f_0187 | both rack bays, gas meter beyond the west bay, step up to the stair | (2.6, 6.6), → south |
| v6:f_0191 | light L-B | under it |
| v6:f_0193, f_0244 | wall W: opening with R11 / R10, socket, plaque, consumer units, trunking | (3.0, 6.6), → west |
| v6:f_0195 – f_0211 | consumer units, network cabinet, NAS, outlets, NW corner | (2.5, 7.6), → north-west |
| v6:f_0213 – f_0225 | boiler close, flue elbow, ceiling notch and void | under the boiler |
| v6:f_0227 – f_0237 | the sealed recess behind the cylinder | (3.4, 6.6), → north-east and up |
| v6:f_0240 | NE corner: boiler, vessel on wall N, board foot, cylinder plinth, floor | (2.7, 7.2), → north-east |
| v6:f_0242, f_0243 | NW corner: cabinet, trunking round the corner, shoe racks, L-B | (2.8, 7.2), → north-west |
| v6:f_0246 – f_0251 | wall S: rack end, meter niche and meter, flexible pipe, valve, bulkhead, R11 | (2.3, 6.3), → south-west |
| v6:f_0256 | gas valve entering the bulkhead; lintel junction | under it |
| v6:f_0259, f_0262, f_0264 | winders from the room side and from W1; flight seen from the foot | opening, → west / north |
| v6:f_0266, f_0267 | opening and deep lintel from the stair foot, room beyond | W2, → east |
| v6:f_0268 | east ledge and lintel head from W2 | → north-east |
| v6:f_0270, f_0272 | flight looking up; top riser, nosing strip, shelf end at the door, open leaf | T6 / T3, → north |
| v6:f_0274 – f_0284 | door leaf, lever handle, leaf closing | threshold / lobby |
| v6:f_0286, f_0288, f_0290 | door head, boarding, overhead cupboard, small cornice, pendant post | lobby (0.4, 8.5), → south, pitched up |
| v6:f_0298, f_0300, f_0302 | pendant post bottom, reeded cupboard moulding, dentil cornice end, string and nosing returns | lobby (-0.2, 8.3), → south-east, steeply up |
| v6:f_0304, f_0306 | lobby soffit, bulkhead cornice, arch and corbel beyond | lobby, → north |

## 10. Interactions

| id | object | action | notes |
|---|---|---|---|
| I1 | **Basement door** (`d_understairs`) | swing 0 → 95° about the east jamb hinge (0.875, 7.68), leaf into the lobby | opened and closed by the owner (f_0111 – f_0117, f_0274 – f_0284). Closed by default. It must now connect `hallway` to the basement stair — walkable |
| I2 | **Switch SW-B** | toggle L-S + L-A + L-B | owner demonstrates (f_0119). Default: on, so the basement is not black when first entered |
| I3 | Overhead cupboard flap (lobby) | top-hung flap lifts ≈ 80° outward-up, or leave fixed | owner points at it (f_0288) but does not open it; optional |
| I4 | Network cabinet glass door | swing 0 → 110° about its north-side hinges | not opened in the video; optional |
| I5 | Consumer-unit lids | flip up 90° | not opened; optional |
| I6 | Gas lever valve | quarter turn | not operated; optional, low value |

Nothing else is operated: the hatch, the recess and the boiler are static.

## Declutter (deliberately excluded)
All shoes and boots; coats, overalls and the tote bag hanging on the rack end; shopping bags, the yellow
carrier, plastic tubs and buckets on the floor; mop, bucket and steam mop; suitcase; cardboard boxes and the
glass pane leaning on wall W; rack contents apart from the few generic items in §6; loose cables on the
floor; the loose paving slab by wall N; the three fixing holes; yellow warning stickers' text; all brand
names and labels (boiler, cylinder, meter, NAS).

## Doubts and open points
1. **Floor level.** 11 risers is certain; the riser height is taken as 0.21 (one 200 mm plank + bed). At 0.20
   the floor is Z −2.20, at 0.22 it is −2.42. The ceiling (h 2.00) then leaves 0.31 for the kitchen floor
   structure, which is what makes 0.21 the preferred value.
2. **Plan extents.** E–W 3.00 and N–S 3.63 come from summing objects (two 0.90 racks, meter, 0.58 consumer
   units, 0.60 cabinet, 0.44 boiler, 0.555 cylinder) and from snapping W / N / E to the kitchen walls above.
   The south wall (y 5.10) follows from the stair (8 goings of 0.21 from the door, then a 0.82 opening); it
   lands 0.21 south of the kitchen's south face, inside the ground floor's unseen cross-wall zone. If the
   builder prefers walls to stack, y 5.31 is only reachable with a 0.18 going, which the treads do not support.
3. **East side.** The plywood wall is taken as the party wall lined to x 4.25, and the projecting SE block as
   a chimney-breast base 0.35 deep × 1.50 long. Depth ± 0.10, length ± 0.25. The hatch suggests a flue; the
   kitchen spec has no breast above it.
4. **The sealed recess**: what it was is a guess; only its shape (sloping floor, upper slot) is observed.
5. **Stair soffit**: taken as the underside of the main flight. The flat strip and rib at the door and the cove
   at the bottom are seen; the exact rake is inferred from the main stair (0.19 / 0.23), not measured.
6. **West shelf**: its level (≈ hall floor) and cap are clear; the jog at y ≈ 6.45 and the narrow northern part
   are read from one frame (f_0121) and could instead be a constant 0.11 shelf.
7. **Door width**: `house.json` says 0.61 clear; the stair below is 0.665 clear. Not re-measured here.
8. **SW-B wiring**: assumed to switch all three lights; a second switch at the bottom was never shown.
9. **Light positions** ± 0.25; the stair light is on the rake near the foot.
10. **Flue route**: the elbow turns into the ceiling void toward the north; the terminal is presumably on the
    side-return wall near the kitchen back door — not seen in v6 (check v2 rear / side-passage footage).
11. **Overhead-cupboard handle** is drawn here slightly east of centre; `hallway.md` §4 says centred.
12. **Pendant post**: bottom height 2.27 and section 0.11 are estimates from steep upward views.
13. Still numbering: `hr_N` / `t_N` stills are 1 frame later than the same-numbered file in `v6/frames`.

## Proposed `spec/house.json` entries (not applied — the orchestrator reconciles)
- Level −1 room `basement`: polygon as §1, `floorZ` −2.31, `ceilingZ` −0.31, floor
  `wood_effect_porcelain_plank_dark`, direction "y".
- Level −1 `basement_stair`: polygon [[0.265, 5.10], [0.93, 5.10], [0.93, 7.60], [0.265, 7.60]] plus the
  opening [[0.93, 5.10], [1.25, 5.10], [1.25, 5.92], [0.93, 5.92]]; `stairs`: start (0.60, 7.60), direction
  [0, −1], width 0.665, risers 11, rise 0.21, going 0.21, 9 straight + 2 winders turning east, bottom riser at
  x 1.25.
- `d_understairs`: `connects` → ["hallway", "basement_stair"]; notes "basement door"; `openAngle` 0, operable.
- The `stairs` room note "cupboard under the flight" and `stairs.md` §"Underside: not visible" should point
  here; the ground floor needs **no slab** over x 0.265 → 0.93, y 5.10 → 7.60 (the shaft is open up to the
  main-flight soffit) and the hall-side spandrel must be a thin panel with the shelf behind it.
- Kitchen floor build-up over the room: 0.31 (Z −0.31 → 0).

## Reconciled dimensions (house.next.json)

Added by the phase-2 reconcile step. `spec/house.next.json` is canonical; where the text above differs, the values below win. Reasons and evidence: `spec/RECONCILE2.md` (decision ids in brackets).

- **Levels unchanged**: floor Z -2.31, ceiling Z -0.31 (2.00 clear); 11 risers x 0.21.
- **South wall at y 5.19, not 5.10** [B1]: the going is taken as 0.20 (stated 0.21 +/- 0.015) so the wall sits under the
  living / kitchen cross wall. Straight risers R1..R9 at y = 7.60 - 0.20 (n-1), R9 at **6.00**; shaft x 0.265..0.93,
  y **5.19**..7.60; opening through the spine wall y **5.19..6.00** (0.81); R10 diagonal (1.25, 6.00)→(0.265, 5.19);
  R11 at x 1.25, y 5.19..6.00.
- **Room**: x 1.25..4.25, y **5.19**..8.73 (3.00 x 3.54). The polygon in `house.next.json` is the full rectangle; the SE
  block is feature `basement_breast_base`, x 3.90..4.25, y **5.19**..6.60.
- **Transform**: everything on or keyed to the south wall (racks, gas meter niche, gas valve, bulkhead, breast hatch
  centre y 5.76 → 5.85) moves **+0.09 in y**; stair items south of y 6.5 scale with the shorter going; everything keyed
  to the west, north and east walls is unchanged.
- **Door**: `d_understairs` is now **`d_basement`** (connects hallway ↔ basement_stair), width 0.61 kept.
- **Switch SW-B** is on the shaft's **east** wall, whose face is x **0.93** in `house.next.json`: plate centre
  (0.93, 7.42), 1.20 above the hall floor [verification INV-04; section 8 had x 0.98 on the pre-reconcile wall face].
- Ground floor above: no slab over the shaft (`basement_stair_void`); the hall diagonal and winders are as
  `ground_corrections.md` HA1 / `landing1.md` 11.

## Round 3 corrections (core owner, from build/rooms2_open.md)
- SW-B stands on the built wall face x 0.99 at (y 7.42, Z 1.20); x 0.93 is only the face below Z -0.01
  (feature basement_strip_e).
- 3.3 The flat soffit strip (0.25 deep at Z 2.10) and the 40 x 40 rib inside d_basement are not modelled: the carcass
  soffit reaches Z 2.086 at y 7.58.
- 7 The shelf ornaments D3..D8 stand about 0.40 north of the positions given (0.19 clear under the soffit at y 5.33
  is too low for a 0.30 bottle).
- 5.5 The smart meter is landscape, about 0.27 x 0.165, nearly filling the 0.30 niche (f_0247), not 0.22 x 0.20.
- 4 The racks render near f_0184 at #171B3E (the spec's #22306B reads royal blue).
- 3.1 The carcass (lib/stairs.py) now lays one uncut plank across every straight tread and riser and planks the
  winders along their long edge; riser R9 stops at x 0.93 (it no longer runs across the pier face).
- 5.5 The gas-meter niche is a real 0.08 recess in the south wall (house.json basement_meter_niche, x 1.55..1.85,
  h 1.45..1.88). The sealed recess (its floor rises about 35 degrees) and the black ceiling slot / boiler notch stay
  flat panels in rooms/basement_plant.py: a box recess cannot carry the slope or the black lining.

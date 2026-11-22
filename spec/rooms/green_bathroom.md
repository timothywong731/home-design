# green_bathroom — first-floor bathroom behind the green bedroom

Source: v4 f_0096–f_0172 and f_0243–f_0268 (daylight, lights on); glimpses in v3:f_0508 and v4:f_0194, f_0227,
f_0236. Full-res stills and crops in `reference/work/p2_green/` (`v4_fNNN.jpg`). Owner narration (v4
01:35–02:51, 04:04–04:29): "I got a sliding door right here … you can slide open it, turn on the light, this is
the bathroom … running tap … you can open this window, you can see the side walk at the back … radiator here …
there's a shower here, you can enter the shower, and this is exactly the same shower control … I got double basin
here … I can walk through this door … that goes to the second floor … this is how the bathroom looks like from
this angle … turn off the bathroom light".

The room has **two doors**: the oak sliding pocket door from `green_bedroom` (south wall) and an ordinary hinged
oak door to the front landing at the foot of the second-floor stair (west wall).

**All coordinates are WORLD coordinates** (metres, BRIEF frame); `z` = height above this room's finished floor.

Dimension confidence: outline ±0.10 m (walls taken from the kitchen directly below in `house.json` and checked
against the 0.88 m doorcase and the tile courses); fittings along a wall ±0.10; heights ±0.05 up to 2.1 m;
ceiling ±0.12 (see Doubts).

## 1. Shape & dimensions

Plain rectangle over the kitchen, between the second-floor stair (west) and the east party wall, running from
the bedroom partition back to the main house's rear wall.

- Polygon (inside faces, CCW): `(1.25, 4.87) (4.30, 4.87) (4.30, 8.73) (1.25, 8.73)` — **3.05 (X) × 3.86 (Y)**.
- **Floor level: world Z = +3.22**, the same as `green_bedroom` and the front landing (flat brass threshold
  bars at both doors; tiles run flush to the bedroom carpet and the landing carpet).
- **Ceiling 2.95 above the floor**, flat (door-height scale in v4_f164 gives 2.95; the north-wall view
  v4_f105 suggests 2.75 — use 2.95 unless the neighbouring rooms settle lower).
- Optional local frame: local x = X − 1.25, local y = Y − 4.87 (origin = SW inside corner).

| wall | plane | what is on it |
|---|---|---|
| W-south (bedroom partition, 0.14 thick) | y = 4.87 | sliding door with tall pediment, a carved panel each side, toilet-roll holder |
| W-east (party wall) | x = 4.30 | WC duct with three niches + wall-hung pan (south end), fan, bath filler, slipper bath, gilt mirror |
| W-north (main rear wall, external, ≈ 0.30) | y = 8.73 | shower slab (west), black towel radiator, window (east) |
| W-west (stair wall) | x = 1.25 | landing door (south end), clock over it, double vanity + mirror cabinet, shower (north end) |

Plan (not to scale; top = +Y / rear, right = +X):

```
              (side passage outside, yellow rendered back addition to the left of the window)
 8.73 +=====slab=====+--[towel rad]--+--[window]--+
      | SHOWER tray  :               (baskets)    |
      | 1.40 x 0.90  : glass                      |
 7.83 +--sliding glass+              +---------+  |
      |                              |  SLIPPER|  |  mirror on wall
 7.55 +------+                       |  BATH   |  |
      |VANITY|                       |         |  |
      |2 basins   (floor tiles N-S)  +---------+  |
 6.10 +------+                          (o) filler|  fan
 5.79 | door                                 +----+
      | to     >                      WC pan | duct  niches
 5.03 | landing                              |    |
 4.87 +--panel 2--+==[sliding door]==+-panel 1-+--+
     1.25       2.24  2.34..3.03   3.13      4.08 4.30
                     green_bedroom
```

## 2. Openings

### 2.1 Sliding pocket door (W-south)
- Clear opening **x 2.34 → 3.03 (0.69), head 1.98**, centred on the wall. Oak 4-panel leaf sliding **east**
  into a pocket x 3.03 → 3.80; oak lining; round brass flush pull at z 1.00. Details in `green_bedroom` §2.2.
- Bathroom-side doorcase: see §3.2. The tile dado is cut against its architrave.

### 2.2 Landing door (W-west)
- Clear opening **y 5.03 → 5.79** (0.762 × 1.981) in the 0.26 m stair wall (x 0.99–1.25); its south
  architrave sits tight in the SW corner.
- Oak-veneer Victorian 4-panel leaf, polished-brass scroll lever on a long backplate (bathroom lock type) at
  z 1.00, three brass hinges. **Hinged on the SOUTH jamb (y 5.03), swings EAST into the bathroom** and folds
  back flat against W-south, covering panel 2 (v4:f_0154–f_0156, v4_f252, v4:f_0246).
- Bathroom side: white moulded architrave 0.08 wide, top z 2.07, no pediment. Brass threshold bar; landing
  carpet beyond. On the landing side the first tread of the second-floor stair starts immediately north of the
  north architrave (≈ y 5.87) (v4:f_0194, f_0227, f_0243).

### 2.3 Window (W-north)
- Reveal **x 3.42 → 4.22 (0.80 wide)**, ≈ 0.20 deep, head soffit at z 2.45 with a painted downstand above;
  white uPVC frame x 3.47 → 4.17, **z 0.72 → 2.40**, transom at z 1.83. **Obscure (frosted stipple) glass** in
  both lights.
- Lower light: side-hung casement, **hinged on the EAST stile, opens OUTWARD** (white handle on the west stile
  at z 1.30) — opened in v4:f_0120–f_0128 ("you can open this window"); it gives onto the side passage, with the
  yellow rendered flank of the back addition immediately to the west (outer face x ≈ 3.30) and a black downpipe.
- Top light: top-hung vent, handle on its bottom rail (not operated).
- Sill: white gloss sill board at z 0.70, 0.22 deep; reveal sides tiled up to the dado line, painted above.

## 3. Architecture & trim

### 3.1 General
- **No skirting** — wall tiles run to the floor with a white silicone joint. **No dado rail**: the tile dado
  top (z 1.20) has a square polished edge.
- **Cornice**: plain white cove ≈ 0.10 × 0.10 on all walls, returning round the WC duct (v4_f162).
- Ceiling flat white, sampled #9B9889 (shade), true **#F5F4F0**.

### 3.2 Sliding-door pediment, bathroom side (different from the bedroom side)
White gloss, taller and plainer (v4_f164, v4:f_0158–f_0166):
- moulded architrave 0.10 wide (outer x 2.24 … 3.13, top z 2.08);
- frieze z 2.10 → 2.25 with an **egg-and-dart band** under a small cornice (z 2.25 → 2.33);
- a pair of large **acanthus scroll consoles** outside the architrave, 0.10 wide, z 1.80 → 2.33, projecting 0.10;
- a full **triangular pediment 1.30 wide** sitting on the consoles: horizontal cornice at z 2.33, raking
  cornices to an apex at **z 2.73**, faint relief in the tympanum. No volutes.

### 3.3 WC duct
Full-height boxing in the SE corner: **x 4.08 → 4.30 (0.22 deep), y 4.87 → 5.79 (0.92 wide), floor to
ceiling**, tiled all over in the wall tile, cornice returned round its head. It carries the pan, the flush plate
and **three open niches** (§5.2).

## 4. Surfaces & colours

| surface | finish | sampled sRGB | estimated true colour |
|---|---|---|---|
| walls above the tile (z 1.20 → cornice) | matt emulsion, **muted grey-green (sage grey)** | #707468, #7C8280, #83897F, #919897 | **#9AA59E** |
| tile dado, floor → z 1.20 on all four walls, and the whole WC duct | white **Carrara-effect ceramic metro, ≈ 100 × 400, gloss, flat edge, horizontal half-bond**, 12 courses, 2 mm pale grout | #C4C3C2 | body **#F0EFEC**, veining **#9FA0A0**, grout **#DDDBD6** |
| shower walls | two **large-format polished porcelain slabs, white with bold gold / ochre and grey Calacatta veining**: W-west slab y 7.70 → 8.73, W-north slab x 1.25 → 2.80, each z 0.04 → 2.48 (painted wall strip above) | #B1AEA3 | ground **#F1EEE6**, veins **#B79A55** and **#8E8A82** |
| floor | matt **porcelain tiles ≈ 400 × 800, long axis north–south, one-third stagger**, pale warm grey with a soft linear travertine grain, 3 mm grey grout | #C5C1B5, #CBC7BF | body **#CFCBC2**, grain **#B9B4A9**, grout **#A9A59C** |
| ceiling, cornice, door / window joinery paint | white | — | **#F5F4F0** |
| oak doors | oak veneer, satin | #A2885A | **#B8905A** |
| brassware | brushed / antique brass | — | **#A88D52** |

## 5. Fixed fittings

### 5.1 Bath and filler ("running tap")
- **Free-standing single-slipper bath**, white gloss acrylic with a rolled rim, **1.55 long × 0.72 wide**:
  x 3.42 → 4.14, y 6.15 → 7.70, 0.16 off the east wall; rim z 0.60 at the low (south) end rising to **0.78 at
  the raised north end**; chrome waste and overflow with a bead chain on the east side; four **gold ball-and-claw
  feet** (v4_f106, v4:f_0112–f_0118, v4_f252).
- **Floor-standing bath filler** in brushed brass at the south end of the bath, base Ø 0.14 at (3.92, 5.98):
  round column 0.75 tall, tall swan-neck spout rising to z 1.10 and arching 0.22 toward the bath, side lever
  mixer at z 0.78, pencil hand-shower in a cradle with a brass hose. The owner turns it on in v4:f_0112–f_0116
  (water stream from the spout into the bath).
- Small white wall shelf 0.30 × 0.10 on W-east at y 7.35, z 0.85 (holds a candle).

### 5.2 WC and niches (on the duct §3.3)
- **Wall-hung pan**, white, rounded D plan, 0.36 wide × 0.53 projection (x 3.55 → 4.08), centred **y 5.33**,
  rim z 0.42, underside 0.10 clear of the floor; slim wrap-over soft-close seat and lid (shown closed).
- **Flush plate**: polished-chrome rectangular dual-flush plate 0.25 × 0.16, centre (4.08, 5.33), z 1.02.
- **Three niches** in the duct face, each **0.60 wide (y 5.03 → 5.63) × 0.12 deep**, lined in the wall tile with
  brushed-steel edge trim: z 1.20 → 1.50, z 1.60 → 1.95, z 2.02 → 2.45. Styling: a rattan basket in the
  lowest; a long shallow wooden trough of moss / succulents in each of the upper two (v4_f162, v4:f_0108–f_0110).
- Toilet-brush holder: brushed-brass wall-mounted tube on the duct at y 5.02, z 0.20 → 0.62.
- **Toilet-roll holder**: brushed-brass holder with a small flat shelf, on W-south at x 3.85, z 0.72.
- **Extractor fan**: white square wall fan 0.16 × 0.16 with a round louvred grille, on W-east just north of the
  duct, centre y 5.95, z 2.45.

### 5.3 Double basin (W-west) — "I got double basin here"
- **Furniture vanity in dark charcoal (near-black, satin paint)**, traditional framed style: two **600 mm
  two-door cabinets** with a **250 mm centre unit** (one drawer over one door) between them; total
  **y 6.10 → 7.55 (1.45), x 1.25 → 1.70 (0.45 deep)**, carcass top z 0.80 on square legs (0.10 open below);
  doors with a beaded flat panel; dark bronze cup pull on the drawer and bow handles on the doors. The centre
  unit has a black glass / stone top at z 0.82 (a potted fern stands on it). Paint sampled #2B2D2B, true
  **#2A2D2E** (v4_f152, v4_f140).
- Two **white ceramic rectangular basins** sitting on / overhanging the cabinets, each 0.60 wide × 0.48
  front-to-back × 0.16 deep, rim z 0.94, front projecting to x 1.77, one tap hole, slot overflow, brushed-brass
  click waste. Basin centres y 6.40 and y 7.25.
- Two **brushed-brass monobloc basin mixers** (cylindrical body 0.16 tall, straight angled spout, top lever).
- **Mirror cabinet** above: three mirrored doors, mid-grey carcass (r3), **y 6.22 → 7.45 (1.23) × 0.72 high ×
  0.15 deep**, z 1.24 → 1.96, its underside just above the tile line (v4:f_0149–f_0152, f_0253–f_0260). Render a
  true reflection; never bake the video reflection (it shows the owner).
- Wall accessories on the tile between basins and cabinet (z ≈ 1.05): a brushed-brass ring tumbler holder
  with a glass and a brass soap dish by each basin — optional.

### 5.4 Shower (NW corner) — "exactly the same shower control"
- White low-profile stone-resin tray **1.40 × 0.90 × 0.04**: x 1.25 → 2.65, y 7.83 → 8.73, linear slot waste
  near the north edge.
- Enclosure of 8 mm clear glass, 1.95 high (top z 2.00), frameless with brushed-steel fittings:
  - **south face** (y 7.83): a fixed pane x 1.25 → 1.95 and a **sliding door pane x 1.95 → 2.65 that rolls
    WEST** in front of the fixed pane, hung by two rollers from a round steel top bar (Ø 25, x 1.25 → 2.65,
    z 1.93); vertical chrome bar handle 0.25 long on the door at x 2.02, z 1.05;
  - **east face** (x 2.65): fixed return pane y 7.83 → 8.73, clamped to the north wall.
- **Shower control** on W-west at y 8.30 — the same set as in every bathroom: exposed chrome **thermostatic
  bar valve** at z 1.10 (two end knobs) with a rigid riser to a swan-neck arm and a **round rain head Ø 0.25**
  at z 2.12, 0.35 off the wall; **hand shower** on a sliding bracket on the riser (z ≈ 1.55) with a chrome hose
  (v4:f_0138–f_0146, v4_f140).
- The marble-effect slabs (§4) line the two walls; the wire caddy and bottles are omitted.

### 5.5 Towel radiator (W-north) — "radiator here"
**Matt black straight ladder rail 0.60 wide × 1.60 high**, x 2.70 → 3.30, z 0.25 → 1.85, 0.09 off the wall:
two round uprights and ≈ 32 round bars in four groups; chrome valves at the bottom. True **#1E1F21**
(v4_f105, v4:f_0118).

## 6. Furniture
None (the two fabric laundry baskets under the window are decluttered).

## 7. Art, mirrors, decor

| # | item | wall / position | size (m) | description |
|---|---|---|---|---|
| B1 | **Gilt mirror** over the bath | W-east, centre y 6.95, z 1.48 → 1.90 | 1.00 w × 0.42 h | Landscape mirror in a 60 mm antique-gold frame with a running leaf / gadroon ornament (#B89B55) (v4_f106, v4:f_0116). |
| B2 | **Carved panel 1** | W-south, centre x 3.60, z 1.46 → 2.45 | 0.50 w × 1.00 h | Dark-walnut / bronzed **low-relief plaque** of a classical draped dancing figure in an arched niche, in a 45 mm frame painted dull gold over black. Model as generic low relief (draped figure silhouette or urn-and-foliage) — no recognisable face (v4_f164, v4_f162). |
| B3 | **Carved panel 2** | W-south, centre x 1.75, same height | 0.50 × 1.00 | The pair to B2, mirrored pose; hidden behind the landing door when that stands open (v4:f_0156, f_0166). |
| B4 | Wall clock | W-west above the landing door, centre y 5.41, z 2.38 | Ø 0.30 | Round quartz clock, thin gold rim, white dial with black numerals (v4:f_0166). |
| B5 | Plants | basin centre unit (1.48, 6.83); window sill (3.80, 8.83) | pots Ø 0.14 | Bird's-nest fern in a brown clay pot; peace lily in a ribbed dark-green pot. |

Bath mats (two pale-grey cotton mats with a border, ≈ 0.80 × 0.50, in front of the shower and beside the bath)
are optional soft furnishings; there is no blind or curtain.

## 8. Lighting and switches

- **Recessed LED downlights ×6**, white bezel Ø 90, in two rows: x 2.05 and x 3.55 at y 5.60, 6.85, 8.10
  (count 6 ± 2; v4_f105 shows the two northern ones, v4:f_0245 / f_0262 three more). Neutral white ≈ 3500 K.
- No wall lights; the mirror cabinet is unlit.
- **No switches inside the room.** The lights are switched two-way from:
  - the flat 1-gang plate in the bedroom, right of the sliding door (x 3.29, y 4.73 face, z 1.25) — pressed in
    v4:f_0102–f_0103 as the owner says "turn on the light, this is the bathroom";
  - a matching flat 1-gang (wide-rocker) plate on the **landing**, on the short wall between the landing door
    and bedroom door 1, **directly beside the bathroom-door architrave: (0.84, 4.95, z 1.27)** — pressed in
    v4:f_0265–f_0266 as the owner says "turn off the bathroom light". The **2-gang rocker to its west, next to
    the green-bedroom door, (0.70, 4.95, z 1.27)**, belongs to `landing1` (8.2): right (west) rocker = landing
    downlights, left (east) rocker = second-floor hall lights (v4:f_0270, f_0310–f_0311). The first draft had
    the two plates the other way round (corrected in the verification round, INV-03).
- The extractor fan runs with the lights (assumption).

## 9. Reference frames

| frames | shows | camera |
|---|---|---|
| v4:f_0096–f_0104 | sliding door from the bedroom, sliding open; switch | bedroom, looking +Y |
| v4:f_0105 (still) | whole room from the sliding door: vanity, shower, towel rail, window, bath; floor tiles; cornice | (2.7, 4.7) looking +Y |
| v4:f_0106 (still) | bath, filler, mirror B1, window, towel rail | (2.6, 5.6) looking NE |
| v4:f_0108–f_0110 (still 108) | WC duct: niches, flush plate, pan, brush, roll holder | (3.0, 5.4) looking +X |
| v4:f_0112–f_0116 | bath filler **running**; slipper end; mirror B1 | at the bath |
| v4:f_0118 (still) | towel radiator, window, sill, bath north end | (3.3, 7.0) looking +Y |
| v4:f_0120–f_0128 | **window opened**: handle side, hinge side, friction stay, side passage and yellow flank wall outside | at the window |
| v4:f_0130–f_0134 | window reveal tiles, sill, top-hung vent, reveal head | at the window, looking up |
| v4:f_0136–f_0146 (stills 138, 140) | shower: slabs, glass, top bar, handle, valve / riser / rain head; vanity north end | (3.2, 6.8) looking NW |
| v4:f_0148–f_0152 (stills 150, 152) | double vanity, basins, taps, mirror cabinet, landing door closed | (2.8, 6.4) looking −X |
| v4:f_0154–f_0156 | landing door: handle side, opening inward | at the door |
| v4:f_0158–f_0166 (stills 160, 162, 164) | W-south: pediment, panels B2 / B3, tile dado, WC duct, fan; clock; landing door open | (2.0, 6.5) looking −Y |
| v4:f_0168–f_0172 | view out of the landing door: bedroom door 1 to the left, second-floor stair to the right | in the doorway |
| v4:f_0194, f_0227, f_0243–f_0244 | landing door seen from the stair / bedroom / landing; bath and duct through it | landing |
| v4:f_0245–f_0252 (stills 246, 252) | room from the landing door; door leaf folding against W-south | in the doorway, looking +X |
| v4:f_0253–f_0260 | mirror cabinet side, basin, tap, tile close-ups | at the door, looking +Y |
| v4:f_0262–f_0264 | bath wall and duct wall overview | (1.8, 6.0) looking +X |
| v4:f_0266–f_0268 | landing switch plates (bathroom + hallway) | landing |

## 10. Interactions

| object | motion | evidence |
|---|---|---|
| Sliding door | translates east 0 → 0.69 m into the pocket | v4:f_0096–f_0104 |
| Landing door | hinge south jamb (1.25, 5.03), swings east into the room 0 → 100° (parks against W-south) | v4:f_0154–f_0166 "I can walk through this door" |
| Window, lower casement | hinge east stile, outward 0 → 60° | v4:f_0120–f_0128 "you can open this window" |
| Window top vent | top-hung, outward 0 → 20° | handle present, not operated — optional |
| Bath filler | lever → water stream from the spout into the bath | v4:f_0112–f_0116 "running tap" |
| Basin mixers ×2 | lever → water stream | Phase-2 rule (taps run) |
| Shower door | glass pane rolls west 0 → 0.65 m along the top bar | "you can enter the shower" (v4:f_0140–f_0146) |
| Shower control | valve knob → rain head runs | "exactly the same shower control" |
| WC | lid and seat lift, hinge at the wall, 0 → 95° | Phase-2 rule (toilets lift) |
| Mirror cabinet doors ×3, vanity doors ×5 and drawer ×1 | side-hung / sliding | not demonstrated — optional |
| Lights | both flat plates (bedroom side and landing side) toggle the downlights | v4:f_0102–f_0103, f_0266 |

## Declutter (deliberately excluded)
Two grey laundry baskets under the window, bathroom scales, white pedal bin, towels and cloths on the radiator,
shower caddy with bottles and sponge, toiletries, toothbrush, soap, spare rolls, phone on the basket lid.

## Doubts
1. **Ceiling height**: 2.95 by door-height scale (v4_f164) against ≈ 2.75 implied by the north-wall view
   (v4_f105) if the room is 3.05 wide. Either the ceiling is ≈ 2.75–2.85, or the room is up to 0.25 m wider
   (stair wall thinner than the 0.26 assumed, west face at x ≈ 1.05–1.10).
2. **West wall line** x 1.25 is the kitchen / stair wall carried up; the landing door reveal thickness and the
   landing-side architrave depend on it — `landing1` / `stairs2` must agree.
3. **Length** 3.86: fittings along W-west add up to ≈ 3.65 (door 0.96, vanity 1.45, shower 0.90, gaps); the
   vanity may be 1.50 and the tray 1.00 deep.
4. Tile format: wall metro reads ≈ 4 : 1 (100 × 400) in v4_f164, but could be the same 100 × 300 tile as the
   ground-floor WC; floor tile 400 × 800 could be 300 × 600.
5. Wall colour sage grey #9AA59E from shaded samples; it may be a little lighter / bluer.
6. Window width (frame 0.70) and sill height (0.70) ±0.08; it sits ≈ 0.08 off the east wall.
7. Bath length 1.55 vs 1.70; its exact offset from the wall.
8. Downlight count; whether the fan is wired to the lights.
9. Landing-door bathroom-side head: plain architrave assumed (only its jamb is seen clearly).
10. Carved panels B2 / B3 depict classical figures; modelled as generic relief for privacy / simplicity.

## Reconciled dimensions (house.next.json)

Added by the phase-2 reconcile step. `spec/house.next.json` is canonical; where the text above differs, the values below win. Reasons and evidence: `spec/RECONCILE2.md` (decision ids in brackets).

- **Floor Z 3.42** (was 3.22) [L2]; **ceiling 2.75** (Z 6.17; was 2.95) [L3] — the analyst's own north-wall reading.
- **Rectangle x 1.25..4.30, y 4.95..8.73 (3.05 x 3.78)** — south wall face was 4.87 [P7].
- **Transform**: items keyed to the south wall +0.08 in y (WC duct → y 4.95..5.87, pan centre 5.41, relief panels);
  landing door clear y **5.13..5.89** (was 5.03..5.79); items keyed to the north wall unchanged (shower, towel
  radiator, window x 3.42..4.22).
- North wall = rear wall of the main house (8.73..9.03); the back addition's flank outer face is x **3.40**, so the
  window reveal starts 0.02 east of it. East wall is external.

## Round 3 corrections (core owner, from build/rooms2_open.md)
- Upper wall paint #AAACA7 (measured against v4 f_0106 / f_0164 / f_0246, normalised to the tile) is now the
  shell finish; the room module's repaint is a no-op.

## Round 3 (21 Nov survey, re-fit and detail)

Shell moves that touch the room: window `w_gbath` centre x 3.82 -> **3.875** (frame / reveal x 3.475..4.275, still
0.80 x 1.68 from sill 0.72); the east wall thickens outwards (inner face x 4.30 unchanged); `w_green_rear_e` 2.77 high.
Ceiling 2.75 confirmed (dims_1: 2.69-2.77). From outside the sill may be 0.15 higher (dims_envelope, low confidence:
not applied). The room module follows the window through `opening_frame`; the sill board's east horn now stops at the
east wall (it ran 5 mm into it after the move).

Measured this round from the v4 stills (camera poses solved from known points: doorcase 0.69 opening and 0.10
architraves, duct corners, vanity module widths; ultrawide, ±0.03-0.05):
- **WC duct**: pan, flush plate and the three niches share one axis at **y 5.45** (v4 f_0108: 5.46-5.48, f_0162: 5.43),
  not the duct centre 5.41 - the pan sits 0.37 from the duct's north edge and leaves room for the brush on the south.
  Niches **0.58 wide (y 5.16..5.74)**, heights kept (f_0162: 1.20-1.47 / 1.58-1.88 / 1.99-2.32 against the 0.10 tile
  courses, within tolerance of 1.20-1.50 / 1.60-1.95 / 2.02-2.45). Niche linings are the gold-veined slab
  (`porcelain_calacatta_slab`, as the shower), the duct face stays metro.
- **Toilet brush**: low wall holder, dark bronze cup z 0.06..0.20 in a brass ring, handle to 0.44, y 5.19 (f_0108:
  cup bottom 0.05, handle top 0.44 against the tile line; it stood at 0.20..0.65 before).
- **Mirror B1**: z **1.36..1.78** (f_0106 / f_0246: the frame bottom is 0.14-0.15 above the 1.20 tile line; was
  1.48..1.90).
- **Mirror cabinet**: **y 6.22..7.62 (1.40), 0.15 deep**, z 1.24..1.96 (f_0152 pose solve: north end 7.63, south end
  over the vanity's; f_0150 also shows its north end at the shower glass; was 1.23 long, 0.13 deep). Carcass and the
  door boxes are **mid grey #8E908C** (f_0150 / f_0152: the side panel and the bottom edge read 0.63-0.65 x the wall;
  the pale #CDCFCD rendered whiter than the wall); the inside and shelves stay pale #F1F1EE.
- **Bath filler** carries plan symbol `pipe` (round post on the plan, solid for the walker; its box includes the spout
  over the bath end).
- **Towel rail** centre x **3.07** (2.77..3.37; f_0105 linear map between the shower corner 1.25 and the window reveal
  3.475: 2.76..3.39); north shower slab ends at **x 2.72** (f_0105: between the return pane and the rail).
- Relief B2 on the south wall checked in f_0164 (frontal): x 3.44..3.90, z 1.33..2.19 - the model (3.47..3.93,
  1.32..2.24) stands. Roll holder x 3.84 (model 3.85).
- Bath: brass centre waste, a brass overflow rose mid-length on the east inner wall and its bead chain (f_0106,
  f_0118; the spec said chrome at the tap end). New ball-and-claw feet: ball, three claws, swelling S-leg, acanthus
  leaf on the knee.
- New: brushed-brass tumbler ring (glass) north of the south tap and soap dish north of the north tap, z 1.06
  (f_0150). Niche styling as filmed: lidded rattan box at the north end of the lowest niche, pale wooden dough bowls
  with succulents (middle) and three bun-moss clumps (top). Bird's-nest fern remodelled with broad crinkled fronds.
  Bath mats in three tones (grey ground, pale band, grey field).

Not changed (no better evidence): vanity y 6.10..7.55, shower tray 1.40 x 0.90, bath x 3.42..4.14 / y 6.15..7.70,
landing door, downlights. The carved panels stay generic urn-and-foliage reliefs (the real ones show a figure).

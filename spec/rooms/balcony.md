# balcony — metal balcony off the rear blue bedroom (first floor, over the patio)

Sources: v3:f_0257–f_0311 (from inside through the glass, then standing on it; stills
`reference/work/p2_blue/v3_t262 … t306.jpg`, contact strip `sheet_balcony.jpg`), and from the garden
v2 stills `v2_t172.jpg` (close, from below), `v2_t210.jpg`, `v2_t250.jpg` (frontal, whole rear elevation),
`v2_t314.jpg` (from the side passage). Owner: "outside is a balcony … this is a balcony, you go outside, the
door can open, and you can see the surrounding, you can observe the outbuilding from here, you can see the shed
and the surrounding, I've got a light here"; in the garden video: "a metallic balcony".

**What it is.** A bolt-on black steel balcony on the yellow rendered rear wall, directly above the dining room's
French doors. It is **not** a roof terrace: nothing is built under it. It is carried by **two steel posts fixed
flat to the wall, one each side of the ground-floor French doors, each with a 45° strut** up to the outer edge
of the platform, and the posts stand on the patio deck. The only access is the bedroom's French doors.

**Dimension confidence.** Width and X position ±0.10 (frontal rear-elevation frame v2:f_0251 scaled at
64.5 px/m on the ground-floor French doors, 1.19 × 2.32, and corrected for the platform standing 1 m nearer the
camera). Projection ±0.10 (bar count on the side rails). Heights ±0.08. The rear-elevation spec
(`spec/phase2/rear_elevation.md`) describes the same structure from below; where the two differ in X, keep the
balcony centred as given here relative to the first-floor door frame.

## 1. Shape & dimensions

- **Local frame**: origin = on the rendered wall face, at deck level, at the platform's west end.
  **+x = world +X**, **+y = world +Y** (out from the house, toward the garden), z up from the deck top.
  **World = local + (0.00, 17.16); deck top z(world) = 3.00.**
- **Platform: x 0 → 2.30, y 0 → 1.05** (2.30 wide × 1.05 projection); world x 0.00..2.30, y 17.16..18.21.
  Rectangular, level.
- **Level**: deck top is **0.05 below the bedroom floor** (3.05) and 0.12 below the top of the door's uPVC cill;
  3.05 above the patio deck (world z −0.05, `garden`). Not roofed.
- Relative to the wall behind it: the bedroom door frame is at **x 0.47 → 2.11**, so the platform runs 0.47 past
  the frame on the west (where a chair stands) and 0.19 past it on the east. The neighbour's brick rear wall
  returns forward ≈ 0.35 at the party line, world x ≈ −0.77, i.e. 0.77 west of the platform (f_0287, f_0299).
- Ground-floor French doors below: world x 0.63..1.82 — the balcony overhangs them and the two posts flank them.

Plan (top = garden, right = +x):

```
 y 1.05  P====================P====================P     P = 50x50 post, == top rail, bars at 115 crs
         |  planter troughs hang outside the rail  |
         |            chequer-plate deck           |
         |  (chair)                                |
 y 0     B---[  door frame 0.47 .. 2.11  ]---------B  ( lantern on the wall at x 2.33, z 2.10 )
         x 0   ^post under at 0.21      ^post 2.20  2.30          B = wall bracket of the side rail
```

## 2. Openings
- **French doors** in the house wall (see `blue_bedroom` §2.3): white uPVC pair + two fanlights, frame
  x 0.47 → 2.11, cill top z +0.12, frame top z +2.39 (deck datum). **Both leaves open OUTWARD over the deck**; the
  east leaf, opened ≈ 85° in the video, then stands 0.20 inside the east rail (f_0293–f_0297). Polished-brass
  lever handles on long backplates outside as well as inside.
- No gate; the railing is continuous on three sides.

## 3. Architecture / structure

All steel, painted black-grey (see §4). Sizes from v2 t172 / t210 / t314:

- **Platform frame**: perimeter of ≈ 150 mm deep channel (z −0.15 → 0), toes inward, with cross bearers; the
  underside is closed with a dark flat soffit sheet. Fixed back to the wall along y = 0.
- **Wall posts (2)**: flat channel ≈ 100 wide × 40 deep, fixed flat to the render with through-bolts at ≈ 0.45
  centres (a line of bolt heads / holes down the face), at **x 0.21 and x 2.20** (world), from the patio deck
  (world z −0.05) up to the underside of the platform (world z 2.85). They sit between the French-door reveal
  and the ground-floor side windows.
- **Struts (2)**: square hollow section ≈ 60 × 60, one per post, in the vertical plane of its post: from the post
  at **world z 1.90** rising at 45° to the platform's front edge beam at y ≈ 0.95, world z 2.85, with a small
  gusset plate at each end.
- **Deck**: steel **chequer plate (five-bar "durbar" tread pattern)**, one sheet over the whole platform, edges
  flush with the frame, coated black; reads glossy when wet (f_0261, f_0285, still t296).
- **Railing** on the three free sides, **1.10 high** above the deck:
  - posts 50 × 50 square hollow section at the two outer corners and **one at the middle of the front** (x 1.15),
    welded to the platform frame;
  - **top rail** ≈ 60 wide × 40 high box section with a flat top and visible round fixing caps, mitred at the
    corners; the two side rails end at the house wall on small **plate brackets screwed to the render** at top-
    rail and bottom-rail height (f_0287, f_0295–f_0299);
  - **bottom rail** 40 × 10 flat on edge, 0.10 above the deck;
  - **infill: plain vertical bars 16 × 16 (square) at ≈ 165 mm centres** between top and bottom rail — **6 bars in
    each front half (12 on the front), 5 on each side** (counted in v3 stills t288 / t298 for the west return and
    t272 for the front; the first draft's 115 mm / 8 bars was too fine); no scrolls, no finials, no glass.
- **House wall behind**: smooth painted render (yellow), wall face world y 17.16. A black cable / conduit runs up
  the wall 0.25 west of the platform and joins a horizontal black cable at world z ≈ 6.0 (rear-elevation spec).
  The second-floor window (two casements with top lights, projecting cill at world z ≈ 6.3) is directly above the
  doors.

## 4. Surfaces & colours

| surface | sampled (tone-mapped stills) | **estimate** | finish |
|---|---|---|---|
| steel: frame, posts, struts, railing | #505452 (rail, wet daylight), #474B50 (post) | **#33373A** black-grey (weathered black / RAL 7021) | satin paint, slightly chalky; rain beads on it |
| deck chequer plate | #313233, #44474A | **#2E3033** | satin black, raised tread bars catch highlights |
| render | #C3A46F, #AA8853 (HLG frame #DBD5B5, #C7BE94) | **#D9C98A** soft primrose / straw yellow | smooth masonry paint, fine texture |
| uPVC door frame, cill | — | **#F4F3EE** | gloss |
| neighbour's brick return (backdrop only) | — | **#9A8262** London stock, mottled yellow-brown | — |

## 5. Fixed fittings
- **Wall lantern** ("I've got a light here"): on the render at the east end, **x 2.33, centre z 2.10** above the
  deck (world (2.33, 17.16, 5.10)): black traditional four-sided coach lantern (tapered body 0.16 × 0.16 × 0.25
  with a pagoda cap, clear panes, amber-tinted lamp) hanging from a black S-scroll bracket on a round backplate,
  projecting 0.22 (f_0293–f_0295; v2:f_0251). Switch assumed inside the bedroom on the north wall east of the
  curtain (`blue_bedroom` S3).
- Nothing else is fixed to the balcony. The PIR floodlight, the downpipe with its swan-neck and the door
  intercom are under / beside it on the ground-floor wall and belong to the rear-elevation spec.

## 6. Furniture
None to model. (A grey folding camping chair stands at the west end — declutter.)

## 7. Decor / planting — keep, it is what the balcony looks like from the garden
- **Rail planters**: dark-grey plastic trough planters ≈ 0.60 long × 0.18 × 0.16 hung on the **outside** of the
  top rail by over-the-rail hooks: three along the front and one on each side rail.
- **Ivy**: dense variegated (green with cream edges) trailing ivy spilling from all of them; it covers most of the
  outside of the front railing and hangs **1.0–1.5 m below the deck** as a curtain, longest at the east corner
  and over the front centre (v2 t172, t210). From inside it shows as a 0.3 m hedge on top of the rail.
- A clump of **purple-blue petunias** in the north-east planter (f_0277, still t284).
- Omit the white icicle fairy-light string hanging from the front edge.

## 8. Lighting and switches
- The wall lantern (§5), warm white; one switch (assumed `blue_bedroom` S3).
- No lighting on the structure itself.

## 9. Reference frames

| frames | shows | camera |
|---|---|---|
| v3:f_0259–f_0265 | balcony through the closed doors: deck, front and east rail, planters | bedroom, looking +y / down |
| v3:f_0267, f_0279–f_0281, f_0293–f_0297 (still t296) | east leaf opening outward, cill, deck pattern, east rail bracket | on the threshold / on the deck |
| v3:f_0269, f_0287–f_0289, f_0299 | west end: render, cable, neighbour's brick return, side-rail wall brackets | on the deck, looking −x |
| v3:f_0271–f_0277, f_0283–f_0285 (still t284) | top rail, bars, middle post, ivy, petunias; the view over the garden to the shed | on the deck, looking +y |
| v3:f_0291, f_0301 | door head, fanlights with trickle vents, second-floor window and cables above | looking up at the house |
| v3:f_0293–f_0295 | lantern | on the deck, looking −y / +x |
| v2:f_0173 (still t172) | underside: platform frame, soffit, both wall posts with bolt lines, both struts, ivy curtain | patio, looking −y and up |
| v2:f_0211, f_0251 (stills t210, t250) | whole rear elevation, frontal: balcony width and position against the ground-floor doors | garden, looking −y |
| v2:f_0315 (still t314) | side view from the passage: projection, side rail, east strut and post | looking −x / −y |

## 10. Interactions
| id | what | motion | evidence |
|---|---|---|---|
| I1 | French doors (east leaf, then west) | hinged at the outer jambs, swing outward over the deck 0 → 85° | "you go outside, the door can open", f_0263–f_0297 |
| I2 | wall lantern | on / off | "I've got a light here" |

The viewer should be able to walk out onto the deck (walkable area x 0.05..2.25, y 0.10..1.00 local) and look
over the rail at the garden.

## 11. Declutter
Folding chair, fairy lights, loose leaves on the deck.

## 12. Doubts
1. **Width / X**: 2.30 wide at world x 0.00..2.30. The frontal frame gives the platform ends at −0.05 and 2.25,
   the close frame gives post centres at 0.16 / 2.25 or 0.21 / 2.20; ±0.10. The east overhang past the door
   frame reads 0.15–0.30 in different frames.
2. **Projection 1.05** (0.95–1.15) from 8 side bars + corner post.
3. **Deck level**: world z 3.00 assumes the bedroom floor at 3.05 (see `blue_bedroom` doubt 1); the exterior
   frame alone gives 2.9–3.1. Keep the deck 0.05 below whatever the bedroom floor becomes.
4. Section sizes (150 channel, 60 strut, 100 wall post, 16 mm bars) are judged from proportions.
5. Whether the wall posts carry down to the patio deck or stop on a bracket just above it (hidden by planters in
   every frame) — modelled down to the deck.
6. Number and length of the rail planters (hidden by the ivy).
7. Lantern x (2.25–2.40) and which switch controls it.

## Reconciled dimensions (house.next.json)

Added by the phase-2 reconcile step. `spec/house.next.json` is canonical; where the text above differs, the values below win. Reasons and evidence: `spec/RECONCILE2.md` (decision ids in brackets).

- **Platform x 0.00..2.30, y 17.36..18.41** — every y in this spec moves **+0.20** with the rear wall face
  (17.16 → 17.36) [E1].
- Deck top Z **3.00**, 0.04 below the bedroom floor (3.04) [E6]; underside 2.85, 0.19 above the ground-floor floodlight.
- **Wall posts at x 0.27 and 2.20** (was 0.21 and 2.20): the west post is moved onto the rendered pier between the west
  side-window frame (outer edge x 0.22) and the French-door reveal (x 0.50).
- Lantern (2.33, 17.36, Z 5.10); rain pipe at x 0.42 (`rear_elevation.md`).
- It is a bolt-on platform: nothing of the ground floor projects beneath it.
- **Railing bars at 0.165 centres: 5 per side return, 6 per 1.15 front bay** (`railing.barCentres`, `barsPerSide`,
  `barsPerFrontBay`) [verification V2]; posts stay at x 0 / 1.15 / 2.30, depth 1.05.

## Round 3 corrections (core owner, from build/rooms2_open.md)
- 7 Planters: three along the front and ONE on the EAST side rail only; the west side rail is bare (v3 f_0269, f_0287,
  f_0299). The west-end ivy seen from the garden hangs from the front trough round the north-west corner.
- 7 In the frontal v2 f_0251 the lowest ivy at the centre hangs about 0.5 m below the deck top (modelled 0.6-1.0 m,
  longer at the north-west corner).
- 5 The lantern stands on top of its S-scroll bracket (f_0295). The envelope no longer builds a placeholder lantern.

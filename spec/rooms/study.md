# study (Rose Room) — second-floor rear room, garden side

The owner's name for this room is **Rose Room** (id `study` unchanged). The round-3 section at the end wins over
everything above it.

Source: v4:f_0442–f_0570 (plus v4:f_0382–f_0386 and v5:f_0001–f_0003 through the door). Full-resolution stills
in `reference/work/p2_second_rear/` (`hr_v4_443` … `hr_v4_567`, `m_windows.jpg`).

Owner narration (v4 07:03–09:24): "towards the back here, this is the second floor study, or called office.
You can see that these two windows can be open… outside you can see the balcony and the shed… there's a plant
here. Now this is the office: computers, working desk, certificates, paintings, artwork, decoration. This is a
corner cabinet. Got two computers. There's a telly, aircon and a vertical big radiator. There's some artwork,
there are some cats here… this thing, there's a skull… there's a beautiful red chair here, with the beautiful
inlay. Now there's a plant here, window. This is the light, can be on and off. There are six spotlights here
in the room."

The study closes the rear end of the second-floor hallway and spans the **full width of the back addition**,
over the dining room and the blue bedroom. Its window is in the rear wall, above the blue bedroom's balcony,
looking down the garden to the shed.

**Dimension confidence.** Total depth door wall → rear wall 3.82 m: (a) the 1.80 m vertical radiator on the
rear wall is 390 px tall seen from the doorway (hr_v4_443), f = 865 px, giving 3.5–3.7 m, (b) the west wall
carries, end to end, the 0.69 m door leaf, a 0.69 m painting, a 1.45 m TV, a 0.42 m frame and gaps, which
needs ≥ 3.8 m (hr_v4_509), (c) the hallway chain of `landing2` closes on the rear wall of `house.json`
(y 16.86) with the door wall at 13.04. ±0.15. Width 3.75 is the ground-floor width between the party wall and
the flank wall (not measured here; the north wall run AC + radiator + window + certificate fits it). The neck
length 1.26 is ±0.15. Ceiling 2.60 ± 0.06 (radiator and door leaf). Furniture positions ±0.2 m — the middle of
the room is crowded and only seen obliquely.

## 1. Shape and dimensions

L-shaped: a **neck** continuing the hallway width for 1.26 m inside the door, then the full-width room.
World coordinates are used directly (no local frame). Polygon, inside faces, counter-clockwise:

```
(-0.65, 13.04) (0.30, 13.04) (0.30, 14.30) (3.10, 14.30) (3.10, 16.86) (-0.65, 16.86)
```

- Neck: x −0.65 … 0.30 (0.95), y 13.04 … 14.30 (1.26). `bathroom2` is behind its east wall.
- Main part: x −0.65 … 3.10 (3.75), y 14.30 … 16.86 (2.56). Area ≈ 10.8 m² in all.
- **Floor Z = Z2 = 6.02** (level with the hallway, brass threshold strip). **Ceiling flat, 2.60** (Z 8.62),
  no slopes.

| wall | plane | what is on it |
|---|---|---|
| W (feature wall) | x −0.65, y 13.04 … 16.86 | parked door leaf, cottage painting, wall TV over a glazed cabinet, small frames, rooster box frame, goose and antler trophies; drawer unit at the north end |
| N (rear, external) | y 16.86 | a/c unit and vertical radiator at the west end, window with curtains, framed certificate and whiteboard at the east end |
| E (flank, external) | x 3.10, y 14.30 … 16.86 | blank |
| S | y 14.30, x 0.30 … 3.10 (`bathroom2` behind) | red settee at the west end, octagonal frame, two paintings, corner cabinet in the SE corner |
| neck E | x 0.30, y 13.04 … 14.30 | rotary dimmer and a/c remote cradle |
| door wall | y 13.04, x −0.65 … 0.30 | door |

```
  y 16.86 +AC/rad==[  window 0.76..1.76  ]==[cert]=========+
          |dr.                plant              (beanbag) |
          |unit    +--desk B--+--------+                   |
          |rooster |  (table) | desk A |                   |
          |  TV    +----------+ 2 PCs  |  chair            |
          |cabinet            |        |                   |
          |          kneeling +--------+                   |
          |cottage    chair                        corner  |
  y 14.30 |painting   +--settee--+ oct. small  green  cab. |
          |leaf   dim.+------------------------------------+
          |  ^        |           (bathroom2)
  y 13.04 +-[door]----+
        -0.65       0.30                                 3.10
```

## 2. Openings

### 2.1 Door from the hallway (`d_study`, door wall)
- Clear opening x −0.525 … 0.175 (0.70), head 1.99, in a 0.10 wall (y 12.94 … 13.04). The frame fills the
  width of the hallway.
- Leaf **686 × 1981 × 35 golden-oak 4-panel**, brass lever on a backplate at 1.00, three brass butts.
  **Hinged on the west jamb, swings north into the study** and stands open flat against the west wall
  (y 13.04 … 13.74) (v4:f_0444, f_0510). True **#B8915A**.
- White moulded architrave ≈ 80 mm both sides, top 2.07; brass threshold strip.

### 2.2 Window (N wall) — "these two windows can be open"
- One opening, **x 0.76 … 1.76 (1.00 wide, centre x 1.26 — over the dining-room French doors), sill board top
  z 0.68, head z 2.08** (1.40 high). Plastered reveal ≈ 0.20 deep, painted the wall colour; **oak window
  board** 30 mm thick with a rounded nose, ≈ 0.24 deep, 1.06 long (true **#B58F5E**; sampled #A7A396 in glare).
- Frame: white uPVC with a central mullion and a transom at z ≈ 1.72: **two lower casements** (each
  ≈ 0.44 × 0.98 of glass) and **two fanlights** (each ≈ 0.44 × 0.28). All four have brass-coloured lever
  handles on their bottom rails.
- **The two lower casements open** (v4:f_0456–f_0478): side-hung with friction stays on the bottom frame,
  read as hinged on the **outer jambs** and opening **outward** to ≈ 60–70°. The fanlights are top-hung
  openers but stay shut in the video.
- View: straight down onto the grey metal balcony of the blue bedroom, then the lawn with the square fire pit,
  paved path, fences and the flat-roofed shed at the end; trees and distant blocks beyond (backdrop only).

## 3. Architecture and trim
- **Skirting** white, 0.17 high, torus-and-ogee, all walls including the neck.
- **No dado rail** (the hallway dado stops at the door architrave), no picture rail.
- **Cornice**: plain white plaster cove with flat bands, ≈ 0.12 × 0.12, all walls, mitred round the internal
  corner of the neck (v4:f_0494–f_0500, f_0528–f_0538).
- Flat ceiling, no rose. No chimney breast.

## 4. Surfaces and colours

| surface | sampled sRGB | true colour (estimate) | finish |
|---|---|---|---|
| **W wall** (feature) | #8D746D (v4:f_0510), #80777A (v4:f_0444, cool), cornice-normalised #B3958F | **#BC9D99** — dusty rose / mauve-pink | matt emulsion |
| N, E, S walls, neck E wall, door wall | #CFCCC5 (S), #C1BCAA (E), #BCAE8F (N, back-lit) | **#EEE6DC** — warm off-white with a faint blush | matt emulsion |
| ceiling, cornice | #AFACA3 (shade) | **#F4F3EE** | matt |
| skirting, architrave, window frame | — | **#F4F2EC** | satin / uPVC |
| carpet | #999A9F (v4:f_0444) | **#B9B4AB** light grey-beige plush, as the hallway | — |
| oak door, window board | #856F4F (shade) | **#B8915A** / **#B58F5E** | satin |

## 5. Fixed fittings

| item | position (world; z above floor) | description | frames |
|---|---|---|---|
| **Vertical radiator** ("vertical big radiator") | N wall, x −0.24 … 0.20 (0.44 wide), z 0.15 … 1.95, 0.09 off the wall | white vertical column radiator, **8 round-ended oval tubes** in a single row, 1.80 high; chrome valves at both bottom corners (TRV at the east) | v4:f_0444, f_0512–f_0514, f_0558–f_0560 |
| **Air-conditioning unit** | N wall above the radiator, x −0.62 … 0.28 (0.90), z 2.17 … 2.47, projects 0.22 | white wall-mounted split indoor unit, rounded front, louvre along the bottom, indicator at the lower right | v4:f_0444, f_0512–f_0514, f_0560–f_0564 |
| A/c remote cradle | neck E wall x 0.30, y 13.95, z 1.24 … 1.40 | white cradle with a white remote (small screen, three buttons) | v4:f_0444, f_0562, f_0570 |
| Wall TV ("telly") | W wall, y 14.625 … 16.075 (1.45 wide), z 1.14 … 1.97, 0.05 thick on a flat bracket | 65-inch black flat panel, thin bezel, screen blank (dark glass) | v4:f_0446, f_0510, f_0516–f_0518 |
| Double socket | E wall, y ≈ 15.3, z 0.40 | white 2-gang switched socket (others are hidden behind furniture) | v4:f_0486 |
| Ceiling disc | ceiling (2.30, 16.30) | white round detector Ø 0.12 | v4:f_0560 (hr_v4_559) |

## 6. Furniture

Sizes are W (along the wall or long axis) × D × H in metres; positions are world footprints.

| item | footprint (x; y) | size | description | frames |
|---|---|---|---|---|
| **Glazed bookcase** under the TV | x −0.65 … −0.32; y 14.84 … 15.86 | 1.02 × 0.33 × 0.83 | dark mahogany (true **#3A1F18**, gloss): moulded overhanging top, **two glazed doors** (one pane each in a 45 mm frame, small brass knob and key escutcheon at the meeting stiles), plinth base; two shelves of books inside. Top modelled almost clear (see §7) | v4:f_0446–f_0450, f_0518 |
| **Drawer unit** | x −0.65 … −0.07; y 15.92 … 16.28 | 0.36 × 0.58 × 0.70 | white lacquered pedestal on four castors, **five drawers** with recessed finger grips (two shallow over three deeper); top modelled clear | v4:f_0444, f_0450, f_0512–f_0514 |
| **Desk A** (computer desk, "working desk") | x 1.35 … 2.15; y 14.75 … 16.35 | 1.60 × 0.80, top at 0.74 | white sit-stand desk: 25 mm white top with generously rounded corners, white electric frame with two rectangular columns on **T-feet** 0.70 long. On it "two computers" (blank screens): a **34-inch curved ultrawide** monitor (0.82 × 0.37, black) near the south-west of the top, turned to face north-east, and a **32-inch flat monitor** (0.72 × 0.42, silver edge, T-foot) at the north end turned to face south-east; each stands on a pale bentwood plywood riser (0.55 × 0.22 × 0.10); black keyboard and mouse. Everything else on the desk is clutter | v4:f_0486–f_0494, f_0508–f_0510, f_0566 |
| **Desk B** (side table) | x 0.15 … 1.35; y 15.50 … 16.20 | 1.20 × 0.70, top at 0.74 | second white sit-stand table of the same family, T-feet on glides, standing in front of the window and butting desk A to form an L. Top modelled clear (it carries a jigsaw in the video) | v4:f_0510, f_0558–f_0564 |
| **Office chair** | centre (2.60, 15.45) | 0.68 × 0.68 × 1.30 | black fabric gaming-style chair: tall winged back with integral headrest, bucket seat, adjustable black armrests, five-star base on castors; faces west to desk A | v4:f_0486–f_0488, f_0494 |
| **Kneeling chair** | centre (0.85, 15.05) | 0.52 × 0.72 × 0.55 | pale bentwood rocker frame (two curved plywood runners) with a dark grey seat pad and knee pad | v4:f_0542–f_0546, f_0564 |
| **Red settee** ("beautiful red chair… with the beautiful inlay") | against the S wall, x 0.38 … 1.43; y 14.30 … 14.82 | 1.05 × 0.52 × 0.93, seat 0.43 | Edwardian **inlaid mahogany two-seat salon settee** (true wood **#3B2218**). Back: serpentine top rail rising to a small central **fan / shell crest**, two upholstered back pads either side of a pierced, waisted centre splat **inlaid with scrolls, an urn and husks in boxwood and satinwood**; boxwood stringing lines on every member. Open arms: flat down-swept rests on scrolled supports. Stuffed-over seat. Slender square legs, the front pair slightly cabriole, joined by turned side and cross stretchers. Upholstery **deep burgundy wool / velvet (true #5A2226, sampled #4B2525)** outlined everywhere with **gold-and-cream braided gimp** | v4:f_0542–f_0556 (hr_v4_543) |
| **Corner cabinet** ("this is a corner cabinet") | SE corner, legs along S and E walls x 2.50 … 3.10; y 14.30 … 14.90 | 0.60 per wall side, front ≈ 0.62 wide, 1.82 high | rustic light oak (true **#B08A4E**, sampled #947D4D), two-part: **lower cupboard** 0.68 high with one panelled door (small knob, hinged on the right) on a plinth and a canted, overhanging waist shelf; **upper open section** with canted side stiles and **three triangular shelves**, flat overhanging cornice at 1.82. Ornaments to keep: a pale turned wooden bowl on the top; a white **owl figurine** with spread wings on the top shelf; a **kestrel figurine** on a round dark base on the middle shelf | v4:f_0486, f_0494, f_0500–f_0506 (hr_v4_501) |
| **Plant** ("there's a plant here") | pot at (1.15, 16.45) | pot Ø 0.30 × 0.27 on a saucer, plant to 1.05 | terracotta pot; upright shrub with glossy rounded mid-green leaves on a single staked stem (jade-plant / ficus habit) | v4:f_0452–f_0454, f_0482–f_0484, f_0558 |

Decluttered: rolled exercise mat, pink bean-bag in the NE corner, boxes and bags, headphones, microphone and
pop filter, tissue boxes, jigsaw and craft trays, cables, floor exerciser under the radiator, soft toys in the
corner cabinet, games console, everything on the cabinet top except the pressed-flower frame.

## 7. Art, mirrors, decor

Privacy: the **certificate frame, the whiteboard and the monitor / TV screens are modelled blank**; a
document with a person's photograph that leans on the cabinet top is omitted. Painted artwork and cat pictures
may use rectified crops. z = centre above the floor.

| # | item | wall, centre | outer W × H | z | description | best frames |
|---|---|---|---|---|---|---|
| W1 | Cottage with hens | W wall, y 14.15 | 0.69 × 0.62 | 1.63 | impasto oil: long low thatched cottage behind flower beds, big tree at left, blue sky with white cloud, hens on a pale path; **plain narrow gold frame 30 mm** (true #C2A24A) | v4:f_0528–f_0530 (close), f_0510 |
| W2 | Goose trophy ("this thing") | W wall, y 14.62 | 0.36 × 0.30, projects 0.30 | 2.25 | two taxidermy greylag goose heads and necks, one preening the other, on a dark shaped wooden shield | v4:f_0528–f_0532 |
| W3 | Antler trophy ("there's a skull") | W wall, y 15.40 (over the TV) | 0.16 × 0.42, projects 0.15 | 2.22 | small roe-deer skull cap with a pair of three-point antlers on a dark carved oak-leaf plaque | v4:f_0534–f_0538 |
| W4 | Small frame | W wall, y 15.02 | 0.14 × 0.16 | 1.06 | dark frame, gold slip, cream mount, tiny picture (neutral) | v4:f_0518 |
| W5 | Two cats | W wall, y 15.30 | 0.28 × 0.34 | 1.00 | **ornate gold rope-moulded frame**, burgundy mount, photograph of two cats (cats only — usable as a crop once the document in front of it is excluded) | v4:f_0524 |
| W6 | Cat portrait | W wall, y 15.60 | 0.19 × 0.21 | 1.04 | very wide stepped bronze-gold frame around a 60 mm portrait of a black-and-white cat | v4:f_0520–f_0522 |
| W7 | Rooster box frame | W wall, y 16.42 | 0.42 × 0.58 | 1.47 | deep gilt shadow-box frame with a rooster in relief / collage on a cream ground | v4:f_0514–f_0516, f_0450 |
| — | Pressed-flower frame | on the cabinet top at y 15.68 | 0.15 × 0.20 | 0.93 | brass-edged glass floating frame with pressed yellow flowers, standing | v4:f_0520–f_0522 |
| N1 | **Framed certificate — BLANK** | N wall, x 2.45 | 0.55 × 0.45 | 1.85 | gold moulded frame 40 mm, burgundy mount with two apertures and a small brass plaque; model the apertures as plain cream card and a plain neutral panel, no text, no portrait | v4:f_0496–f_0498, f_0560 |
| N2 | **Whiteboard — BLANK** | N wall, x 2.42 | 0.60 × 0.45 | 1.30 | frameless white board with a pen tray clip at the top; model plain white | v4:f_0496–f_0498 |
| S1 | Green foliage | S wall, x 2.05 | 0.52 × 0.78 portrait | 1.80 | oil of sunlit leaves and stems in greens and yellows; **dark walnut frame 50 mm with a carved inner edge** (true #4A3524) | v4:f_0488, f_0494, f_0500 (hr_v4_487) |
| S2 | Small green picture | S wall, x 2.00 | 0.20 × 0.25 | 1.22 | dark bronze frame, small green-gold image (window / foliage) | v4:f_0488, f_0508 |
| S3 | Octagonal frame | S wall, x 1.62 (above and east of the settee) | 0.36 × 0.47 | 1.42 | dark walnut **octagonal** moulded frame, cream ground with a pressed / embroidered leaf-and-flower spray | v4:f_0492, f_0542–f_0544 |

**Curtains**: a pair on the N wall, shown open. Fabric: **silver-grey damask / jacquard with a tone-on-tone
leaf pattern** (true **#C9C5BF**), lined, **eyelet heading** with brushed-steel rings. Each stack ≈ 0.32 wide,
top z 2.33, **full length to z 0.03**; each gathered at z ≈ 0.95 by a **cream-gold rope tie-back with a tassel**.
**Pole**: mid-brown wood Ø 30 mm with ball finials, x 0.40 … 2.12 (1.72 long), centre z 2.26, 0.09 off the wall
(v4:f_0452–f_0454, f_0480, f_0558–f_0560).

## 8. Lighting and switches
- **Six recessed LED downlights** ("there are six spotlights here in the room"), white bezel Ø 85 mm, warm
  white ≈ 3000 K. Best reading of the layout (v4:f_0444, f_0564–f_0568): one in the neck at (−0.18, 13.65);
  a row of three at y 15.05 (x −0.05, 1.25, 2.50); a row of two at y 16.15 (x 0.60, 1.90).
- **Control**: one white **rotary dimmer** (single plate, round white knob, push on / off) on the **neck east
  wall at x 0.30, y 13.82, z 1.25**, with the a/c remote cradle 0.13 north of it. The owner operates it at
  v4:f_0562–f_0570: "this is the light, can be on and off" — it switches all six downlights.
- No table or wall lamps are modelled (a small desk lamp is part of the desk clutter).
- Daylight from the north (rear) window.

## 9. Reference frames

| frame (still) | shows | camera (world, approx.) |
|---|---|---|
| v4:f_0444 (hr_v4_443) | **first view in**: door leaf, W wall, a/c, radiator, window, neck wall with dimmer and cradle | doorway (−0.2, 12.7, 1.5), looking north |
| v4:f_0446–f_0450 | W wall close: cottage painting, TV, small frames, glazed bookcase, drawer unit, rooster frame | neck, looking north-west |
| v4:f_0452–f_0454 | NE corner: curtain, tie-back, window board, plant, bean-bag | at the window, looking east |
| v4:f_0456–f_0478 (`m_windows.jpg`) | **both lower casements opened**, friction stays, handles, view down to balcony, garden, shed | at the window |
| v4:f_0480–f_0484 | window reveal and board, plant, cabinet beyond | looking west along the N wall |
| v4:f_0486–f_0494 (hr_v4_485, _487) | **desk A with both monitors, office chair, corner cabinet, S-wall pictures** | (1.0, 16.0) looking south-east; then (2.6, 15.6) looking south-west |
| v4:f_0496–f_0498 | certificate frame and whiteboard, NE corner cornice | (1.8, 15.8), looking north-east |
| v4:f_0500–f_0506 (hr_v4_501) | corner cabinet: shelves, ornaments, lower door | (2.3, 15.5), looking south-east |
| v4:f_0510 (hr_v4_509) | **W wall square-on** over the desks: door leaf in the neck, W1, TV, trophies, cabinet, drawer unit | (2.6, 15.5), looking west |
| v4:f_0512–f_0514 | a/c unit, vertical radiator, curtain, drawer unit | (1.0, 15.3), looking north-west |
| v4:f_0516–f_0524 | TV, frames W4–W6, cabinet top | close, looking west |
| v4:f_0528–f_0538 | goose trophy, W1, antler trophy, cornice | looking west and up |
| v4:f_0540 | door from inside, hallway through the arch | (−0.2, 13.3), looking south |
| v4:f_0542–f_0556 (hr_v4_543) | **red settee**: back, inlay, arms, stretchers; S3 above | (1.2, 15.4), looking south |
| v4:f_0558–f_0560 (hr_v4_559) | **window** with all four lights, curtains, pole, radiator, plant | (0.6, 15.0), looking north-east |
| v4:f_0562, f_0570 | dimmer and remote cradle | neck, looking east |
| v4:f_0564–f_0568 (hr_v4_563, _565) | overall room toward the NE, ceiling with the downlights | neck corner (0.2, 14.2), looking north-east and up |

## 10. Interactions

| object | type | detail |
|---|---|---|
| door leaf | hinge | vertical axis at (−0.525, 12.99); modelled open 90° against the W wall (`on=True`); `blocks` `d_study` |
| west lower casement | hinge | owner opens it: vertical axis at the west jamb (0.80, 17.06), opens outward (north) ≈ 65°; frame, glass and handle share the group |
| east lower casement | hinge | same, axis at the east jamb (1.72, 17.06), opposite sense |
| curtains (pair) | slide | modelled open; state 1 draws each half ≈ 0.55 to the centre and drops the tie-backs |
| dimmer plate | light | toggles `study` (six downlights) |
| TV | trigger + show | `trigger` on the set, screen quad `show when=1 fx=tv` |
| glazed bookcase doors | hinge | two leaves hinged on their outer stiles, open ≈ 100° toward the room; needs shelves and books inside (not opened in the video) |
| drawer unit | slide | five drawers, 0.35 out toward +X (not opened in the video) |
| corner cabinet lower door | hinge | hinged on its right stile, opens ≈ 100°; plain interior with one shelf (not opened in the video) |
| monitors | — | blank; no interaction |

## Doubts
1. **Depth 3.82** (door wall 13.04 → rear wall 16.86): the radiator scale alone gives ≈ 3.6; the west-wall
   inventory and the hallway chain give 3.8–3.9. If the upper rear wall is not on the ground-floor line the
   room shortens from the north.
2. **Neck length 1.26** (1.1–1.4) and with it the north wall of `bathroom2` (taken as y 14.20, wall 0.10).
3. **Width 3.75** assumes the flank wall at x 3.10 as on the ground floor; never measured upstairs.
4. **Window**: 1.00 × 1.40, sill 0.68 (±0.06); which side the lower casements hinge on (friction stays are
   seen on the bottom frame, so they are side-hung; outer-jamb hinges are assumed); x position ±0.10.
5. **Radiator** width (0.32–0.50) and tube count; height taken as the standard 1.80.
6. **Desks**: number, sizes and exact positions. Two white sit-stand tables forming an L is the reading; a
   single L-shaped top cannot be excluded. Monitor sizes are from proportions.
7. **Downlight layout**: six by the owner's count, positions approximate (±0.3).
8. **Wall colours**: the west wall is clearly a dusty rose-mauve; whether the other walls are pure white or
   a faint blush off-white is uncertain under mixed daylight (#EEE6DC used).
9. TV size (65-inch from its height against the ceiling); heights of the small frames W4–W6 (±0.05).
10. Art on the S wall: x positions ±0.15; S2's subject is not legible.
11. Sockets: only one seen; desks will hide the rest.
12. The door wall's inside face and the south part of the neck's west wall were never filmed square-on;
    assumed plain.

## Reconciled dimensions (house.next.json)

Added by the phase-2 reconcile step. `spec/house.next.json` is canonical; where the text above differs, the values below win. Reasons and evidence: `spec/RECONCILE2.md` (decision ids in brackets).

- **Polygon**: (-0.65, 13.04) (0.30, 13.04) (0.30, **14.15**) (3.10, **14.15**) (3.10, 16.86) (-0.65, 16.86) — neck
  0.95 x **1.11**, main room 3.75 x **2.71** (measured 1.26 and 2.56; both are now inside this spec's tolerances, neck
  1.1–1.4 and depth ±0.15) [P4 as revised in the verification round, INV-01]. `bathroom2` keeps its measured 2.20
  (y 11.50..13.70), so of the 0.50 that neither spec accounted for, 0.15 is taken here and 0.35 is an unseen zone in the
  wall between the two rooms (`w_bath2_study`, y 13.70..14.15, solid). The first reconcile had the wall face at 14.05.
- **Transform**: items on or keyed to the south wall of the main room **-0.15** in y (settee y 14.15..14.67, corner
  cabinet y 14.15..14.75, pictures S1–S3 on the wall face y 14.15); items on the neck's east wall keep their distance
  from the door wall (dimmer y 13.82, cradle y 13.95); everything else unchanged.
- **Window x 0.48..1.98** (1.50 wide, centre 1.23; was 0.76..1.76) [E7]; sill 0.68, head 2.08 unchanged.
- Rear wall outer face y **17.36** (0.50), flank outer face x **3.40**.
- Floor Z 6.02, ceiling 2.60: unchanged. Roof above: flat, Z 8.87.

## Round 3 corrections (core owner, from build/rooms2_open.md) — superseded
- ~~2.2 w_study is 1.00 wide (x 0.76..1.76) again~~: overruled by RECONCILE3 floor2b-02/03 (1.55 x 1.56 from 0.58), below.

## Round 3 — 21 Nov footage (v13 t127–t212), as built in `rooms/study.py`

Sources: `spec/phase3/floor2_b.md` section 1 (survey), `spec/phase3/briefs/study.md`, RECONCILE3 floor2b-01..05,
envelope-05/-06, garden-23. Stills in `reference/work/r3_floor2_b/` (`hr_v13_t127` … `hr_v13_t217`).

**Shell (house.json).** Neck x -0.65…0.32, y 13.04…13.84 (0.97 x 0.80); main room x -0.65…3.10, y 13.84…16.86
(3.75 x 3.02). `w_bath2_study` 0.14 (faces 13.70 / 13.84). Window `w_study` 1.55 wide x 1.56 from sill 0.58 (head
2.14), centre x 1.255, transom 1.70, four top-hung lights (lower pair 35 deg, brass espagnolette on each bottom rail),
interior reveal 0.24 (frame inner face y 17.102). Ceiling 2.60, skirting 0.17.

**Rule used to re-fit the room.** W-wall items keep their distance from the N wall (the survey tied them to it);
S-wall items moved 0.31 south with the wall; neck-wall items keep their distance from the door wall.

| item | as built (world; z above the floor 6.02) | evidence |
|---|---|---|
| W wall paint | `#C5ACA8` dusty rose-mauve (repaint of the shell's `#BC9D99`); other walls `#F0EDE6` (shell) | survey 1.1 #C6ABA3; render vs t193.4 / t166 ratios |
| radiator | 7 oval tubes, 0.49 x 1.78, x -0.30…0.19, bottom 0.21, 0.09 off the wall; top wall brackets | t148, v4 f_0444 |
| a/c | 0.80 x 0.30 x 0.22, x -0.62…0.18, z 2.10…2.40; louvre flap, sensor eye lower right | t147 / t148 / t193.4 |
| dimmer | satin-steel plate, round knob, neck E wall y 13.38, z 1.32 (0.34 N of the door wall); switches the six downlights only (`circuit='main'`; the plug-in desk lamp keeps its own circuit) | t127 (the plate reads grey-metallic beside the white cradle) |
| a/c remote cradle | neck E wall y 13.50 (0.12 further N), bottom z 1.25 | t127 |
| downlights | six, 3 x 2 grid: x 0.05 / 1.25 / 2.50, y 14.75 / 16.10; none in the neck | v4 f_0563 / f_0565, t193.4 |
| wall TV | 55-inch 1.23 x 0.71, W wall y 14.83…16.06, z 1.23…1.94, two bracket hooks under it | v4 f_0510, t193.4 |
| E wall plates | single outlet plate z 1.05 at y 14.68; double socket z 0.35 at y 14.98 — placed 0.24 / 0.54 N of the corner cabinet as filmed, not at the survey's absolute 14.95 / 15.25 (measured against the old S wall) | t160 |
| S wall socket | double, z 0.25, x 2.35 (just W of the corner cabinet) | f_0178 |
| window board | oak, 22 mm on the reveal bottom (top 0.602), 0.24 deep to the frame + 25 mm bull-nose, full opening width, ends housed 5 mm into the reveals | t206, t194.4 |
| curtains | pole 1.88 overall, x 0.315…2.195 (mid-brown wood `#7E6048`: 30 mm bar 1.80, two 40 mm ball finials, brackets and rosettes at x 0.445 / 2.065, outside the reveals; built in `study.py curtain_pole()`), centre x 1.255, axis z 2.30; eyelet heading (brushed steel), stacks 0.30 (outer edges x 0.335…2.175) covering both jambs, hem 0.03, tie z 0.95 with pale-gold rope and 0.20 tassel; cloth = generated pale silver jacquard `art/study_curtain.jpg` (repeat 0.64 m, `rooms/study_tex.py`) | t152, t193.4, hr_v4_563 |
| glazed bookcase | y 15.00…16.02, x -0.63…-0.33 (0.02 off the wall for the skirting), 0.90 high; plinth, bead under the top, two glazed doors with brass butts, catch and escutcheon; book rows stand on the bottom panel and shelf tops (0.089 / 0.353 / 0.607) | t142, t193.4 |
| frames under the TV | black 0.17 sq with a stepped gold slip and a grey-cat drawing (crop `art/study_cat_grey.jpg`, t142), y 15.08…15.25, z 0.98…1.15; gold rope frame, burgundy mount, 0.30 x **0.31**, y 15.33…15.63, z 0.908…1.218 (survey 0.34 high: does not fit between the 0.90 bookcase top and the TV at 1.23); stepped bronze 0.18 sq, y 15.71…15.89, z 0.97…1.15 | t142, t146, t193.4 |
| rooster shadow box | 0.34 x 0.58, y 16.25…16.59, z 1.25…1.83, champagne-gilt box frame 45 x 60 mm, glazed | t147, t193.4 |
| cottage painting | 0.70 x 0.58, y 13.98…14.68, centre z 1.61, plain gold 30 mm | v4 f_0510, hr_v4_527 |
| goose trophy | two geese (breast, neck, head, pink beaks) on a dark kidney plaque, a fanned wing behind the S bird; centre y 14.49, z 2.23 | hr_v4_527, t146 |
| antler plaque | carved leaf plaque, roe skull and antlers, y 15.42, plaque bottom 2.05, tips 2.38 | t193.4, t146 |
| drawer pedestal | x -0.31…0.05, y 16.08…16.66, top 0.72, castors, 3 shallow + 1 deep drawers facing S. Its W side lines up with the bookcase front (t127), so the drawers (0.20 out) clear the bookcase; `excl` with the N bookcase door | t127, t142, t193.4 |
| desk A | 1.60 x 0.80, long axis N–S, x 1.55…2.35, y 14.00…15.60 (S end 0.16 off the wall), top 0.74, r 0.08 corners, glides; black hand control under the NE front edge | t164, t170, t176 |
| desk B | 1.20 x 0.70, long axis E–W, x 0.35…1.55, **y 14.95…15.65**, butting desk A's W edge in its N half. Evidence: a PnP fit of t127 (threshold, dimmer, radiator foot, N-wall floor line; 6 px rms) puts its W foot centre at 15.21…15.31; t129 shows the ring lamp on desk A's NW corner near desk B's NE corner; the survey's N-tied 15.08…15.78 and the lamp in t128 lean up to 0.1 further N, but a N edge past 15.65 closes the 0.50 m walking lane between desk B's NW corner and the drawer pedestal (0.52 m as built). The kneeling chair fits between it and the settee (t128 / t129). Top 0.72, castors, hand control under its S edge just E of the W leg (x 0.58…0.78) | t127, t128, t129 |
| on desk A | 34-inch curved ultrawide on a bentwood riser at the S end facing N-NE, hexagonal ring foot; 32-inch flat monitor (silver edge) on a riser at the N end facing the chair; keyboard with key caps, leather mouse mat, mouse; gooseneck ring lamp (lamp group `study.desk_lamp`) at the NW corner. Screens blank | t129, t171, t176 |
| office chair | (2.66, 14.86) facing W: five-star base, twin castors; bucket seat with a dished centre panel and rolled side bolsters about 0.07 above it; U-section back - shoulder wings 0.11 forward easing to 0.04 at the lumbar, rounded wing tops (ears) beside a head section 0.72 of the shoulder width, a 0.016 lumbar bulge; padded channels with real grooves (five vertical over the shoulders, five horizontal over the lumbar), dark red stitching along both groove edges; oval arm pads. Under 1.30 high (soft in the walk layer) | t160, t176 |
| kneeling chair | (1.00, 14.68), sitter facing W, between the settee and desk B: 0.05 clear of the settee, 0.02 clear of desk B | t128, t129 |
| settee | x 0.38…1.43, back 0.025 off the S wall (y 13.865…14.38); front legs slightly cabriole | hr_v4_543, t129, t133 |
| corner cabinet | SE corner, 0.02 off both walls (skirting), legs 0.60; door hinged right, small pewter knob at the left | t160, hr_v4_501 |
| S-wall pictures | foliage x 2.05 z 1.80; small green x 2.00 z 1.22; octagon x 1.60 z 1.42 (1 cm clear of the foliage frame, as in v4 f_0492) — all on y 13.84 | t170, t171, t176, v4 f_0492 |
| plant | pot (1.00, 16.45), narrow staked shrub to 1.05, about 180 cupped oval leaves 0.055-0.08 long held upward on short rising shoots, muted mid-green, dark drip band under the light rim | t152, t166, t194.4 |
| bean bag | lounger, `#93566B` dusty raspberry (render-matched to t152 / t166 against the wall), x 2.26…3.06, y 16.05…16.81, back on the E wall, 0.55 high + crown, carry loop | t152, t166, f_0151–f_0158 |
| certificate / whiteboard | N wall E of the window, x 2.55 z 1.85 / x 2.52 z 1.30 — both **blank** | t128 |

Not modelled (clutter): yoga mat, gift bags and boxes, games console, photographs and the document on the bookcase
top, tissue boxes, jigsaw and craft trays, microphone, floor exerciser, foot massager, soft toys, yoga blocks.

Open: the cornice is still the shell's plain 0.12 cove (the survey reads a small stepped ogee, bottom edge 2.46,
projection 0.10) — a request to the trim owner.

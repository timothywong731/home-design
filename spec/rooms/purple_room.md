# purple_room — unused second-floor room (lilac walls, floral curtains)

Source: v4:f_0388–f_0440 (plus v5:f_0130 and v6:f_0001 through the open door). Full-resolution stills in
`reference/work/p2_second_rear/` (`hr_v4_387` … `hr_v4_437`, `m_windows.jpg`).

Owner narration (v4 06:23–07:03): "there's an unused room here with purple walls… you can turn on the lights
here, four spotlights and an aircon. This room is unfurnished. I got beautiful pink colour floral curtains. The
window can open, you can see all the way down… sockets, sockets, light switch."

The room is on the **east side of the second-floor hallway**, in the back addition directly behind the
hallway's harbour-painting wall; its window is in the east (flank) wall and looks across the side return at the
neighbour's brick back addition. It is entered at its north-west corner, immediately south of the hallway arch.

**Dimension confidence.** North–south width 1.91 ± 0.08 and the window / radiator sizes come from the frontal
view of the east wall (hr_v4_389), scaled by the ceiling height (2.60, itself tied to door leaves and to the
1.80 m radiator of the study). East–west length 2.78 ± 0.12 is the camera-to-wall distance in the same still
and independently the gap between the hallway partition and the flank-wall line of `house.json` (x 3.10).
Position along Y follows the hallway chain of `landing2` (±0.12). Fittings ±0.10.

## 1. Shape and dimensions

Plain rectangle. **World rectangle x 0.32 … 3.10, y 9.39 … 11.30** (2.78 × 1.91 m, 5.3 m²).
**Floor Z = Z2 = 6.02** (level with the hallway, brass threshold strip, no step). **Ceiling flat, 2.60** (Z 8.62).

Room-local frame, parallel to the world axes: origin = floor at the south-west inside corner (0.32, 9.39);
local x = X − 0.32 (toward the window), local y = Y − 9.39 (toward the rear of the house).

| wall | local plane | world | what is on it |
|---|---|---|---|
| W-door | x = 0 | x 0.32, hallway behind | door at the north end, dimmer, a/c remote cradle, double socket |
| N | y = 1.91 | y 11.30, `bathroom2` behind (0.27 wall in line with the hallway arch) | the open door leaf parks against it; double socket near the east corner |
| E-window | x = 2.78 | x 3.10, flank wall | window, radiator, curtains |
| S | y = 0 | y 9.39 | air-conditioning unit at the east end, twin outlet plate |

```
            N wall  (bathroom2 behind)                    local y
   1.91 +--leaf--------------------------[skt]--+
        | door \                                 |curtain
        | 1.20..1.81                             #
        |dimmer                                  W window 0.58..1.33
        |remote            (empty room)          # + radiator under
        |                                        |curtain
        |skt                    [plate]   [ A/C ]|
   0    +----------------------------------------+
        0            S wall                    2.78   local x
```

## 2. Openings

### 2.1 Door from the hallway (`d_purple`, wall W-door)
- Clear opening local y 1.20 → 1.81 (0.61 m; world y 10.59 … 11.20), head 1.99. Wall 0.10 thick.
- Leaf **610 × 1981 × 35 golden-oak 4-panel** (two tall panels over two short ones), brass lever on a
  backplate at 1.00, three brass butts. **Hinged on the north jamb, swings into the room** to ≈ 90–95° and
  stands along the N wall (the jamb is only 0.10 from the N wall). True **#B8915A** (sampled #C3B286 lit,
  #856F4F shaded).
- White moulded architrave ≈ 80 mm both sides, top 2.07; brass threshold strip (v4:f_0436, f_0438).

### 2.2 Window (wall E-window)
- Structural opening **local y 0.58 → 1.33 (0.75 wide, centred on the wall), sill board top z 0.76, head z
  2.18** (1.42 high). The frame is set toward the outside of a thick wall: **plastered reveal ≈ 0.22 deep**,
  reveal sides and soffit painted the wall colour.
- Frame: white uPVC, 70 mm sections. **Top light fixed**, 0.52 high, with a white slot **trickle vent** in the
  head. Transom at z ≈ 1.62. **Lower casement 0.78 high opens** — the owner unlocks the handle on its bottom
  rail (brass-coloured lever, centre of the rail), pushes it out and leans out (v4:f_0416–f_0428). Read as
  **side-hung on the south jamb, opening outward to ≈ 90°** (the open sash stands at the right when he looks
  south, v4:f_0428); see doubts.
- **Window board**: oak, 30 mm thick, rounded nose projecting 30 mm into the room, 0.80 long, ≈ 0.25 deep
  (true **#B58F5E**, satin).
- View: the neighbour's London-stock brick flank wall with white sashes ≈ 3 m away, the two side returns
  (ours paved, a fence, theirs with bins) below, slate rear slope of our own main roof to the south. Backdrop
  only — low-detail massing, nothing identifying.

## 3. Architecture and trim
- **Skirting**: white, 0.17 high, torus-and-ogee top, all four walls.
- **No dado rail, no picture rail.**
- **Cornice**: plain white plaster cove with a flat band top and bottom, ≈ 0.12 drop × 0.12 projection, all
  four walls (v4:f_0394–f_0400).
- Ceiling flat, no rose. No chimney breast, no alcoves, no steps.

## 4. Surfaces and colours

| surface | sampled sRGB | true colour (estimate) | finish |
|---|---|---|---|
| walls (all four, and the window reveal) | #B2B5C6 (N wall, raking daylight), #898789 (S wall), #7F7979 (W wall, warm white balance), #727286 (E wall, back-lit) | **#B4AFC6** — soft grey-lilac / lavender; S wall normalised against the cornice gives #B3B0B9, the owner calls it "purple" | matt emulsion |
| ceiling, cornice | #C6C9D1 | **#F4F3EE** | matt |
| skirting, architrave, window frame | — | **#F4F2EC** | satin / uPVC |
| carpet | #CDD0D6 (cool daylight) | **#B9B4AB** — the same light grey-beige plush as the hallway | — |
| oak door, window board | #C3B286, #856F4F | **#B8915A** / **#B58F5E** | satin |

## 5. Fixed fittings

| item | position (local) | description | frames |
|---|---|---|---|
| **Radiator** | E wall, centred under the window: y 0.74 … 1.17, z 0.11 … 0.71, 0.10 off the wall | white traditional **two-column steel column radiator, 9 sections** (≈ 0.43 wide × 0.60 high × 0.07), round-topped sections, chrome valve tails to the floor at both ends, TRV at the south end | v4:f_0390, f_0414–f_0418 |
| **Air-conditioning unit** | S wall, east end: x 1.93 … 2.73, z 2.18 … 2.47, projects 0.21 | white wall-mounted split indoor unit, rounded front, louvre along the bottom edge, small logo and indicator at the lower right; pipework leaves through the wall behind it (black lagged pipes run down the outside of the flank wall) | v4:f_0400–f_0402, hr_v4_399 |
| A/c remote cradle | W-door wall, y 0.95, z 1.22 … 1.38 | white wall cradle holding a white remote with a small screen, ≈ 0.07 × 0.16 | v4:f_0394–f_0398, f_0436–f_0438 |
| Double socket | W-door wall, y 0.55, z 0.33 | white 2-gang switched socket | hr_v4_393 |
| Double socket | N wall, x 2.35, z 0.33 | white 2-gang switched socket | hr_v4_389 |
| Twin outlet plate | S wall, x 1.25, z 1.25 | white single plate with two small outlets (aerial / data) | hr_v4_399 |
| Ceiling disc | ceiling (1.45, 0.30) | white round detector / vent Ø 0.12 | hr_v4_399 |

## 6. Furniture
**None — model the room empty** ("this room is unfurnished"). What stands in it in the video is storage and is
decluttered: carpet cleaner and hose, dismantled bed slats and a white frame leaning on the S wall, a grey
fabric-wrapped bundle in the SE corner, table legs and battens on the floor, three framed pictures leaning on
the skirting. One real piece is among it and may be kept if the room looks too bare: a **mahogany
Chippendale-style side chair** (pierced vase splat, cabriole front legs on ball-and-claw feet, drop-in seat in
cream fabric with red and green flowers), 0.52 w × 0.48 d × 0.97 h, seat 0.47, standing against the S wall at
local (1.55, 0.35) (v4:f_0400, f_0432). Its twin is in the loft office.

## 7. Art, mirrors, decor
- **Nothing hangs on the walls.**
- **Curtains** (the owner's "beautiful pink colour floral curtains"): a pair on the window wall, shown open.
  Fabric: white ground printed with large **dusty-pink and mauve chrysanthemum / peony heads** (≈ 0.18 across)
  on trailing stems with **sage, grey-green and blue-grey leaves**; lined; eyelet (ring) heading. Each curtain
  stacks ≈ 0.30 wide and 0.12 deep beside the reveal, top at z 2.38, **hem at z ≈ 0.32** (below-sill length,
  clear of the floor). Each is gathered at z ≈ 0.88 by a **gold rope tie-back with a tassel** on a hook at the
  reveal edge. Fabric colours: ground **#F1EEEA**, pink **#C9A0A8**, mauve **#A58AA6**, leaf **#8C9684**.
- **Pole**: dark-stained wood Ø 30 mm with ball finials Ø 55, length 1.50 (local y 0.20 … 1.70), centre z 2.33,
  on two brackets 0.09 off the wall (true **#4A3024**).
- Texture source for the print: v4:f_0406–f_0410 (close, the hand holds the cloth flat), v4:f_0392.

## 8. Lighting and switches
- **Four recessed LED downlights** ("four spotlights"), white bezel Ø 85 mm, in a 2 × 2 grid at local
  (0.90, 0.50), (0.90, 1.41), (1.90, 0.50), (1.90, 1.41); warm white ≈ 3000 K (v4:f_0390, f_0396, f_0400–f_0402).
- **Control**: one white **rotary dimmer** (single plate with a round white knob, push on / off, turn to dim)
  on the W-door wall at **y 1.04, z 1.25** — 0.07 south of the door architrave, with the a/c remote cradle
  0.09 further south. It switches all four downlights (the owner turns them on at v4:f_0396–f_0400; plate in
  v4:f_0394, f_0398, f_0436–f_0438).
- Daylight from the east window only.

## 9. Reference frames

| frame (still) | shows | camera (local, approx.) |
|---|---|---|
| v4:f_0388 (hr_v4_387) | door from the hallway, three hinges on the north jamb, lilac wall beyond | hallway, looking north-east |
| v4:f_0390 (hr_v4_389) | **whole room from the door**: window wall, radiator, curtains, N wall socket, a/c at right, two downlights | doorway (0.1, 1.5, 1.5), looking east |
| v4:f_0392 | window, pole, curtain print, a/c | (1.0, 1.2), looking east and up |
| v4:f_0394 (hr_v4_393) | **W-door wall**: architrave, dimmer, remote cradle, socket, cornice, skirting | (2.0, 0.6), looking west |
| v4:f_0396–f_0398 | ceiling with downlights, cornice, dimmer close | centre, looking up / west |
| v4:f_0400–f_0402 (hr_v4_399) | **S wall**: a/c unit, twin plate, ceiling disc, cornice | (1.6, 1.5), looking south |
| v4:f_0404–f_0410 | curtain fabric, tie-back, pole finial, reveal | at the window |
| v4:f_0414–f_0420 (hr_v4_415, _419) | window frame: fixed top light, trickle vent, lower casement, handle, oak board, radiator from above | at the window, looking east / down |
| v4:f_0422–f_0428 (hr_v4_427) | views out and down: side return, flank wall render, main-roof rear slope | leaning out |
| v4:f_0430–f_0434 | window board end, curtain foot, floor, N wall skirting | looking down |
| v4:f_0436–f_0440 (hr_v4_435, _437) | door leaf from inside (panels, lever), dimmer, hallway beyond | (0.9, 1.2), looking west |
| v5:f_0130 | glimpse through the door: window and radiator | hallway |

## 10. Interactions

| object | type | detail |
|---|---|---|
| door leaf | hinge | vertical axis at world (0.27, 11.20); modelled open 90° into the room (`on=True`); closing swings it west / south to the frame; `blocks` `d_purple` |
| window lower casement | hinge | "the window can open": vertical axis on the south jamb at world (3.32, 9.97), opens **outward** (east) ≈ 80°; handle and glass share the group; modelled closed |
| curtains (pair) | slide | modelled open (state 0); state 1 draws each half ≈ 0.40 toward the centre of the pole and releases the tie-backs (scale the folds rather than translate if the mesh allows) |
| dimmer plate | light | toggles `purple_room` (four downlights) |
| a/c unit | — | not operated in the video; optional `trigger` that opens the bottom louvre |

## Doubts
1. **South wall position** (y 9.39): from the measured 1.91 m width hung off the arch line. If the room in
   fact runs to the old rear wall of the main house, the south wall is at ≈ 9.05 and the room 2.25 wide; the
   frontal still does not support that, but it is the largest uncertainty. The window stays centred either way. The `yellow_room` directly below is specified as
   y 9.07 … 11.15 (2.08 wide); stacking the two rooms on one pair of walls (≈ 9.10 … 11.25) is within both errors.
2. **East wall line** x 3.10 is taken from the ground-floor flank wall; the reveal (0.22) suggests the upper
   wall is ≈ 0.30 thick (outer face ≈ x 3.40 against 3.30 on the ground floor) — `rear elevation / roof` to
   decide.
3. **Casement hinge side.** The handle is on the bottom rail (typical of a top-hung light) but the sash stands
   to the south when open; side-hung on the south jamb is the reading used. The top light is taken as fixed.
4. Window height 1.42 and sill 0.76 (±0.06); transom position ±0.05.
5. Radiator section count (8–10) and exact size.
6. Exact positions of the two sockets and the twin plate (±0.25); the twin plate's function.
7. Downlight grid positions (±0.2).
8. Curtain heading: eyelets are read from the regular deep folds; a pencil pleat on rings is possible.
9. Wall colour: samples vary strongly with exposure and white balance (#727286 … #B2B5C6); #B4AFC6 is the
   cornice-normalised estimate, a muted lavender rather than a saturated purple.

## Reconciled dimensions (house.next.json)

Added by the phase-2 reconcile step. `spec/house.next.json` is canonical; where the text above differs, the values below win. Reasons and evidence: `spec/RECONCILE2.md` (decision ids in brackets).

- **Rectangle x 0.32..3.10, y 9.29..11.20 (2.78 x 1.91)** — every world y in this spec moves **-0.10** (was 9.39..11.30),
  with the arch wall that forms its north side [P3, P5]. Window centre y 10.25; door clear y 10.49..11.10.
- Floor Z 6.02, ceiling 2.60: unchanged.
- South of it, y 8.73..9.29, is an unseen solid zone on the old rear wall of the main house.
- Flank wall outer face x **3.40** (0.30 thick; reveal 0.22 fits).

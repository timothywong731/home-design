# eaves — triangular storage voids either side of the loft office

Source: v5 f_0262–f_0289 (front void through the east hatch), f_0295–f_0305 (front void through the west
hatch), f_0316–f_0335 (rear void). Full-res stills in `reference/work/p2_second_front/` (`hr_271`, `hr_284`,
`hr_322`, `hr_327`; montages `n_eaves1.jpg`, `m_024`–`m_032`). Owner narration (v5 04:21–05:28): "if I open
it … this goes to the front, so this is a storage area, one light, it's a bit dark but you can see there's a
very narrow triangular storage area … sockets here, light switch here, this controls the light … you can
also open it from the other side, it goes to the same place … get in, this is triangular as you can see …
now this is also going to a storage area, this is also a slot, lights on, switch, triangular storage area,
there's a step here, you can see that".

One room id, **two separate spaces** reached only through the knee-wall hatches of `loft_office`
(`loft_office.md` §2.3):

- **`eaves_front`** — behind the front knee wall: a low triangular void along the whole width of the house,
  opening in its middle into the tent-shaped void under the **bay gable**. Both front hatches lead into it.
- **`eaves_rear`** — behind the rear knee wall, east of the stair dormer: a taller triangular void with a
  step in its floor. The rear hatch leads into it.

**Dimension confidence.** These spaces are derived from the loft office section (pitch 30° ± 3°, knee walls
0.92 and 1.42) plus what the camera sees through the hatches; nothing in them is measured against a known
object except the hatch leaves. Depths and the gable-void width ± 0.25, heights ± 0.10, the rear step
position ± 0.3. Absolute Y moves with `loft_office` (± 0.3).

All coordinates are **world** X, Y; `z` is height above the **loft office floor, world Z = 6.45**.

## 1. Shape & dimensions

### 1.1 `eaves_front` — main-roof part
- Plan: **x −0.65 … 4.30, y 0.95 … 2.44** (the knee wall is 0.10 thick: room face 2.54, back 2.44).
- Section: right-angled triangle — the knee-wall back is vertical, 0.92 high at y 2.44; the roof lining
  falls at 30° to the floor at the inside of the front wall: `z(y) = 0.577·(y − 0.95)`. Usable floor depth
  ≈ 1.5 m, headroom never more than 0.86. ("A very narrow triangular storage area.")
- West of the gable (x −0.65 … ≈ 1.43) and east of it (x ≈ 3.63 … 4.30) this simple section applies; the
  west hatch (leaves x −0.27 … 0.63) opens into the west stretch.
- Floor level Z 6.45, flush with the loft office (the hatch sill is the 0.15 skirting plus 0.05 frame).

### 1.2 `eaves_front` — bay-gable part
- The roof of the two-storey bay is a gable facing the street; inside it is an A-shaped tunnel running from
  the knee wall straight to the street gable: **floor x 1.43 … 3.63 (2.20 wide), y 0.14 … 2.44 (2.30 long)**.
- Section across X (constant along the tunnel): two linings rising at ≈ 43° from the floor at x 1.43 and
  3.63 to a **flat strip 0.30 wide at z 0.90**, centred x 2.53: `z(x) = min(0.90, 0.947·(1.10 − |x − 2.53|))`.
- South end: the street gable wall, a plastered triangle with its top cut by the flat strip (v5:f_0271,
  f_0284 — `hr_284.jpg` is the view along the tunnel). No window.
- Where the tunnel crosses the main-roof part (y 0.95 … 2.44) the main lining is cut away on the lines where
  the two roofs meet (valleys): the envelope there is `max(main z(y), gable z(x))`. The gable flat strip
  (0.90) meets the main lining at the knee-wall top, so the strip runs right up to the east hatch.
- The east hatch (leaves x 2.52 … 3.42) opens onto this tunnel, almost on its axis.

### 1.3 `eaves_rear`
- Plan: **x 1.35 … 4.30, y 6.69 … ≈ 9.05** (knee wall back 6.69). West end: the cheek wall of the stair
  dormer (x 1.25 … 1.35). East end: the party wall, a plain plastered triangle.
- Section: knee-wall back vertical, 1.42 high; lining falls at 30° toward the rear:
  `z(y) = 1.42 − 0.577·(y − 6.69)`, reaching the upper floor level at y ≈ 9.05. Headroom is under 0.6 m
  beyond y ≈ 8.2; the footage shows ≈ 1.3–1.5 m of used floor width.
- **Floor step**: the floor by the hatch (x 1.35 … ≈ 2.35) is at loft-office level; east of a line running
  front-to-back at **x ≈ 2.35** it is **≈ 0.12 m lower** (world Z ≈ 6.33). The edge has two parallel
  aluminium stair nosings with a dark insert (≈ 60 mm wide in all), and a short white upstand board closes
  the step where it meets the sloping lining. "There's a step here." With the lower floor the knee-wall back
  is 1.54 high in the east part.

### 1.4 What these spaces say about the outside (for the exterior model)
- Main roof: pitch 30°, ridge at y ≈ 5.00, world Z ≈ 9.15; front eaves at loft-floor level (gutter ≈ Z 6.45
  at y ≈ 0.47). See `loft_office.md` §1.3.
- Bay gable: ridge along Y at x ≈ 2.53; inside strip at world Z 7.35, so the outside ridge is ≈ **Z 7.7**
  and the gable roofs fall at ≈ 43° to eaves on the bay cheeks (x 0.90 and 4.15) at about the main eaves
  level; the gable roof dies into the main front slope about 2.4 m behind the bay front.
- Rear: the main roof's rear slope survives only east of x ≈ 1.35. West of that the **stair dormer** rises
  from the ridge flat: flat felt roof, white fascia with black gutter, cheeks clad in **dark grey flat
  panels** (≈ #3F4146), seen through the open Velux (v5:f_0194, f_0198). The rear slope ends against a
  **pale yellow rendered wall** (≈ #D9C97E, "sandstone colour") with its own white fascia, black gutter and
  felt flat roof — the south wall of the flat-roofed second-floor rear rooms — about 2.0–2.4 m north of the
  Velux, i.e. on the line of the main body's rear wall (y ≈ 9.0); a black downpipe stands in the corner
  between the dormer cheek and that wall. `rear` / `landing2` own these; this is only what the Velux shows.

## 2. Openings
- No doors of their own: the three double-leaf hatches belong to `loft_office` (§2.3 there). Seen from
  inside, each hatch is a rough-edged plasterboard opening with a softwood lining; the leaves' concealed
  hinges show on the outer stiles (v5:f_0303–f_0304).
- No windows, no rooflights.

## 3. Architecture & trim
- No skirting, cornice or joinery. All junctions are plain plasterboard arrises, taped and painted; the cut
  edge of the board round the east hatch opening is left rough (v5:f_0275–f_0282).
- Rear void: the step with its aluminium nosings (§1.3) and the white upstand board are the only trim.
- A loose white board leans against the knee-wall back in the front void (omit).

## 4. Surfaces & colours
| surface | material | sampled sRGB | estimated true colour |
|---|---|---|---|
| all linings, knee-wall backs, end walls | plasterboard, matt white emulsion | #D3D2CD (hr_271), #D1D2CD (hr_284) | **#EFEEEA** |
| front void floor (both parts) | grey sheet flooring (smooth vinyl / cushion floor) laid over the boards | #9E9A93 lit, #585551 unlit | **#8C8A85** |
| rear void floor | concrete-effect grey sheet vinyl, lightly mottled | #C1BCA8 near the hatch (lit), #6D6A5C beyond | **#8A8882**, mottling ± 8 % |
| step nosings | mill-finish aluminium with a dark grey rubber insert | — | **#B9BBBD** / **#3A3C3F** |
| hatch leaves, inside face | white melamine/painted MDF | — | **#F4F3EF** |

## 5. Fixed fittings
| item | space | position | notes |
|---|---|---|---|
| light switch, 1-gang white rocker | front | on the back of the knee wall just west of the east hatch opening, x ≈ 2.40, z 0.60 | "light switch here, this controls the light" (v5:f_0274–f_0282) |
| double socket, white | front | below that switch, x ≈ 2.40, z 0.25 | "sockets here" |
| light switch, 1-gang white rocker | rear | on the back of the knee wall east of the rear hatch, x ≈ 2.60, z 1.05 | v5:f_0322–f_0323, f_0331 |

## 6. Furniture
None. Declutter: the suitcases, vacuum-packed bedding, boxes, rucksacks, fans and bags that fill the voids are
omitted. If the voids look too bare with the hatches open, three or four plain closed cardboard boxes and two
plain hard-shell suitcases (no labels or stickers) may stand against the knee-wall backs.

## 7. Art, mirrors, decor
None.

## 8. Lighting and switches
| light | position | controlled by |
|---|---|---|
| front void: one round opal **LED bulkhead**, Ø 0.30, cool white ≈ 4000 K | on the flat strip of the bay-gable tunnel, centre (2.53, 1.60), z 0.90 | the rocker inside the east hatch (§5). "One light." It is the only light in the front void; the west stretch is lit only by spill — "it's a bit dark" |
| rear void: one round opal **LED bulkhead**, Ø 0.26, cool white | on the back of the knee wall, vertical, centre x ≈ 2.85, z 1.05 | the rocker beside it (§5). "Lights on, switch." |

Both are off by default; they are not on the loft office dimmer.

## 9. Reference frames
| frame | shows | camera |
|---|---|---|
| v5:f_0262–f_0266 | east front hatch opened (west leaf), first look into the gable tunnel, dark | loft office, (2.8, 3.2) looking −Y |
| v5:f_0267–f_0273, f_0283–f_0284 | gable tunnel lit: A-section, flat strip with the bulkhead light, gable end wall, floor | in the hatch, looking −Y |
| v5:f_0274–f_0282 | switch and double socket on the knee-wall back; the narrow main-roof void running west | in the hatch, looking −X |
| v5:f_0285–f_0289 | the same void again ("you can also open it from the other side") | in the hatch |
| v5:f_0295–f_0301 | west front hatch opened (west leaf); narrow triangular void, slope meeting the floor | loft office, (0.3, 3.2) looking −Y |
| v5:f_0302–f_0305 | from the west hatch looking east along the void to the gable tunnel; hatch hinges | in the hatch, looking +X |
| v5:f_0316–f_0321 | rear hatch opened (west leaf), dark then lights on | loft office, (1.9, 5.9) looking +Y |
| v5:f_0322–f_0324, f_0331 | rear void: bulkhead light and switch on the knee-wall back, slope, east end | in the hatch, looking +X |
| v5:f_0325–f_0330, f_0333 | the floor step: double aluminium nosing, upstand board, lower floor | in the hatch, looking down / +X |

## 10. Interactions
| object | action | notes |
|---|---|---|
| front void light | on/off from the rocker inside the east hatch | visible through either front hatch when a leaf is open |
| rear void light | on/off from the rocker beside it | visible through the rear hatch |
| hatch leaves (6) | see `loft_office.md` §10 | the viewer should be able to open a leaf and look in; walking in is optional (headroom ≤ 0.9 front, ≤ 1.5 rear) |

## Doubts
1. **Front void depth.** The 30° lining reaching the floor at the front wall (y 0.95) is a consequence of the
   roof model in `loft_office.md`; through the west hatch the void reads narrower (≈ 0.8–1.0 m) and there
   may be a low masonry upstand (0.2–0.4 m) at the front wall instead of a feather edge.
2. **Bay-gable tunnel**: floor width 2.20 (seen 1.8–2.4), lining pitch 43° (image reads ≈ 50° with the camera
   tilted up; `front_elevation.md` assumes 45°), strip height 0.90 (from the strip being as wide as the
   0.30 m light). Its length depends on the loft office Y anchor.
3. Whether the front void east of the gable (x 3.63 … 4.30) is open or blocked — not seen.
4. **Rear void**: how far north it really runs (the lining may stop at a low wall before y 9.05), and whether
   the step line is square to the knee wall; the step height 0.12 is judged from the nosing, the reason for
   the step is unknown.
5. Switch, socket and light positions are placed from oblique close-ups: ± 0.2.
6. Floor finishes are seen only under flash-like lighting; both are some grey sheet material.
7. The exterior notes in §1.4 (dormer cladding, yellow wall, their positions) come from one look through
   the open Velux and must be reconciled with the rear-elevation and landing specs.

## Reconciled dimensions (house.next.json)

Added by the phase-2 reconcile step. `spec/house.next.json` is canonical; where the text above differs, the values below win. Reasons and evidence: `spec/RECONCILE2.md` (decision ids in brackets).

- **Floor Z 6.49** (was 6.45) [L4]; rear void 6.37 east of x 2.35.
- Front void: unchanged (x -0.65..4.30, y 0.95..2.44; gable tunnel x 1.43..3.63, y 0.14..0.95).
- **Rear void: x 1.25..4.30, y 6.69..8.73** (was x 1.35.., y to about 9.05): its west side is the stair flank wall face
  (1.25) and its north limit the old rear wall of the main house; the roof plane is still 0.18 above the floor there.
- The green bathroom ceiling below is at Z 6.17, 0.20 under the lower part of the rear void's floor [L3].
- Roof planes: `house.next.json` `roof.planes` (`main_front`, `main_rear`, `bay_gable_w/e`).

# front_elevation — the street face of the house, all floors

Source: v2 frames f_0952–f_0971 (the owner stands on the forecourt 0.5–1.6 m from the wall and looks up and
along it), v4 frames f_0024–f_0066 (the same wall seen from inside the first-floor front room and looking
down out of its windows). v1 never goes outside. Full-res stills and crops: `reference/work/p2_front_ext/`
(`v2_tNNN.jpg` = v2:f_(NNN+1), `v4_tNN.jpg` = v4:f_(NN+1)). The ground in front is in `spec/rooms/front.md`;
the flag is specified there (§7.1).

Every item is tagged **[S] seen** in the footage or **[I] inferred** (house type, symmetry, or what the
interior implies). Nothing above the first-floor window heads is seen except one steep look up at the west
corner of the bay gable and the eaves over the door (v2:f_0955–f_0959).

**Privacy:** the transom over the street doors carries the house number and street name in gold letters.
It must be modelled as **plain frosted glass with no lettering**, and no number or name may appear anywhere
on the model. Neighbouring houses are plain massing only.

**Dimension confidence.** X positions at ground floor are taken from `house.json` / `vestibule.md` /
`living.md` (door frame, bay lights) and are good to ±0.05 m. Ground-floor heights ±0.05 m. First-floor
sill/head heights depend on the first-floor level (taken as Z 3.23) and are ±0.12 m. Everything from the
eaves upward (gable height, roof pitch, ridge) is inferred: ±0.4 m. Projections (cornice, canopy, sills)
±0.05 m.

## 0. What the house is

A two-storey-plus-attic **mid-terrace Edwardian house** (attached on both sides), frontage 5.41 m
(x −0.88 … 4.53). The elevation has two bays:

- **West, narrow "entrance bay"** (x −0.88 … 0.90): street doors at ground floor under a slated lean-to
  porch roof, one tall window above, main roof eaves over it.
- **East, wide "window bay"** (x 0.90 … 4.15): a two-storey **square** bay projecting 0.86 m in front of the
  main wall, four-light window at ground floor, three-light window at first floor, finished with its own
  **front gable**.

**The whole street face is painted white** — render, stonework, mullions, cornices, gable timbers,
bargeboards, gutters and window frames are all one brilliant white [S]. There is **no exposed brick on our
elevation** except the small red-brick party-wall kneeler at the west eaves [S]. (The owner calls the
*rear* of the house "sandstone colour"; that does not apply to the front.) The attached houses either side
are red brick with white dressings; ours reads as the all-white one in the row.

There is **no arch and no pediment on the outside** [S]. The original open porch arch survives *inside*
as the vestibule vault (old front-wall plane, y 0.74 … 1.29); the porch was enclosed by the white glazed
door screen in the plane of the bay front. The "pediment" the owner asks for at v2:f_0978–f_0998 is the
pedimented living-room door surround in the hall, not part of this elevation.

## 1. Planes, stations and levels

World frame as BRIEF. Seen from the street you look toward +Y, so **−X (door) is on the left, +X (bay) on
the right**.

### 1.1 Wall planes (Y of the outer face)

| plane | y | where |
|---|---|---|
| A — bay / door-screen face | **−0.12** | ground floor x −0.72 … 4.15 (door screen and bay front are flush [S]); first floor x 0.90 … 4.15 (bay front, stacked directly over the ground-floor bay [S]) |
| B — main front wall | **+0.74** | first floor x −0.88 … 0.90 (the window over the porch) and behind the bay; at ground floor it is the vestibule pier / arch line (internal) |
| bay west cheek | x = 0.90, y −0.12 … 0.74 | first floor only (at ground floor it is inside the vestibule) [S] |
| bay east cheek | x = 4.15, y −0.12 … 0.74 | both floors [S ground-floor corner only, I above]; 0.27 m short of the party line, facing the neighbour's bay |

### 1.2 Levels (Z above the vestibule floor)

| Z | what | tag |
|---|---|---|
| −0.06 | forecourt paving at the wall | S |
| 0.00 | threshold top / ground-floor floor | S |
| 0.55 – 0.62 | bay window stone sill (70 thick) | S |
| 0.62 – 1.80 | bay lower lights (white shutters behind) | S |
| 1.80 – 1.93 | bay transom | S |
| 1.93 – 2.70 | bay top lights | S |
| 2.03 – 2.12 | door head / transom bar | S |
| 2.12 – 2.50 | door transom light; frame top 2.57 | S |
| 2.52 – 2.65 | pilaster capital | S |
| 2.62 | porch canopy soffit; fascia 2.62 – 2.80 | S |
| 2.70 – 2.90 | bay lintel band (plain) | S |
| 2.90 – 3.10 | bay cornice (projects 0.18) | S |
| 3.10 – 3.95 | first-floor bay apron (plain, splayed corners, see §3.5) | S |
| 3.70 | top edge of the porch lean-to roof against wall B | S (height I) |
| (3.23) | first-floor floor level in the front room — from the stair: landing 2.85 + two risers | I — to be confirmed by the first-floor specs |
| 3.95 | first-floor sills (bay and porch window), top of the stone sill ledge | S (height I) |
| 5.12 | transom of the first-floor windows | I |
| 5.55 | first-floor window heads | I |
| 5.95 | eaves: gutter line of the main roof and of the bay gable | S (height I) |
| ≈ 7.7 | apex of the bay gable | I |
| ≈ 9.0 | main ridge | I |

### 1.3 Elevation sketch (not to scale; left = −X)

```
 Z                                             /\            <- gable apex ~7.7 [I]
                                              /  \
                              barge board -> / /\ \ <- white raking struts [S, partly]
 5.95 ===main eaves gutter===+              /_/__\_\
      [kneeler]              |pipe  +--+----------------+--+
 5.55      +--------+        |      |p |  3-light       |p |   p = corner pier with
           | top lt |        |      |a |  casement      |a |       sunk panel [S west]
 5.12      +--------+        |      |n |  window        |n |
           | porch  |        |      |e |  (top lights)  |e |
           | window |        |      |l |                |l |
 3.95      +--------+        |      +--+================+--+ <- stone sill ledge
 3.70 ~~~~slates~~~~~~~~~~~~~+       \ apron (corners splayed 45 below, square above) /
      ~~~lean-to porch roof~~|      +------------------------+
 3.10 =======================+======|=== bay cornice ========|
 2.80 [fascia + gutter, 3 downlights under]     |tl|tl|tl|tl |   tl = top light
 2.57 +----------------+ [pil]   +--+--+--+--+--+
      | frosted transom|  ||     |==|==|==|==|  transom 1.80-1.93
 2.03 +-------+--------+  ||     |  |  |  |  |
      | leaf  | leaf   |  ||     |  |  |  |  |  lower lights (shutters inside)
      | 3x4   | 3x4    |  ||     |  |  |  |  |
      | panel | panel  |  ||     +--+--+--+--+  sill 0.62
 0.00 +-------+--------+--++-----+   plinth   +---
     -0.62          0.62 0.68 1.07 1.22 ... 3.88 4.15        x
```

## 2. Openings

### 2.1 Street doors `d_street` [S] — centre (0.00, −0.06), frame 1.24 × 2.57
The door set is exactly as `vestibule.md` §2.1 (white uPVC, two 0.59 m leaves, each with a 3 × 4
Georgian-barred obscure-glazed upper panel over a solid lower panel; full-width transom light Z 2.12–2.50;
brass lever handles 1.02 m; brass letter plate on the mid rail of the **west** leaf). Seen from outside
(v2:f_0959–f_0965):

- The outside faces are the same white as inside; Georgian bars are inside the sealed unit (flat glass
  face); the glass reads grey-white frosted in daylight.
- The letter plate on the outside is a polished-brass flap 0.30 × 0.075 in a brass frame; the outside
  handles are the same brass levers on 240 × 30 backplates.
- The frame sits ≈ 40 mm behind the pilaster face, between the pilaster (east) and a 0.10 m strip of white
  rendered return against the party line (west), with a white square rainwater pipe in that strip.
- **Both leaves open outward** (hinged on the outer jambs, x ±0.59), to ≈ 100°. This corrects
  `house.json` (`swingInto` should be `outside`) and agrees with `ground_corrections.md` V3.
- Transom: one pane, **plain frosted, no lettering**.
- Threshold: low aluminium/uPVC sill, 60 mm above the paving.

### 2.2 Ground-floor bay window `w_bay_front` [S] — x 1.245 … 3.855, Z 0.62 … 2.70
- Four equal lights **0.54 m** wide separated by three **0.15 m** masonry mullions, crossed by a masonry
  transom at 1.80–1.93: a grid of 4 tall lower lights (1.18 high) and 4 top lights (0.77 high). End jambs
  0.15 (west, against the pilaster) and ≈ 0.10 (east, against the corner pilaster).
- Mullions, transom and jambs are painted stone/render, flush with the wall face, with a small ovolo /
  chamfer on the arrises toward the glass; depth to the window frames ≈ 60 mm.
- In each of the 8 openings a **white uPVC double-glazed frame** (55 mm sightline). Lower lights: fixed or
  side-hung casements — not opened in any video; treat as fixed. Top lights: top-hung fanlights with a
  slim aluminium trickle vent in the head (visible on lights 1 and 4) — not opened.
- Glass clear; the white plantation shutters of the living room show behind the lower lights, the top
  lights are unshuttered and reflect the sky.
- Sill: projecting painted stone sill Z 0.55–0.62, 60 mm proud, running the full width of the four lights
  with squared ends.
- The interior side of the same frames is the dark timber-look described in `living.md`; only the outside
  is white.

### 2.3 Ground-floor bay cheek windows
- West cheek: internal (looks into the vestibule), see `vestibule.md` §2.3 — not part of the elevation.
- East cheek `w_bay_cheek_e` [I outside]: light 0.50 wide centred y 0.37 on the face x 4.15, same sill,
  transom and head levels as the front lights. Never seen from outside (it faces the 0.5 m slot between
  our bay and the neighbour's bay).

### 2.4 First-floor windows [S from inside and outside; sizes I]
All white uPVC double-glazed casements, clear glass, with a horizontal transom ≈ 0.43 m below the head
(top lights above it). Sills at Z 3.95, heads 5.55.

| window | position | size | opening | evidence |
|---|---|---|---|---|
| **porch window** (over the street doors, wall B, y 0.74) | centre x ≈ 0.00 | 0.85 wide × 1.60 high: lower casement 3.95–5.12, top light 5.12–5.55 | **lower casement opens outward, hinged on its west (−X) jamb**; "this window can open" — the owner pushes it open ≈ 45° (v4:f_0030–f_0036). Top light not opened | v4:f_0024–f_0036, v2:f_0964 |
| **bay west cheek window** (face x 0.90) | y 0.19 … 0.64, close to wall B | 0.45 wide × 1.60 high, one tall pane, no transom seen | **fixed** — "this window cannot be opened" (v4:f_0038–f_0042); it looks west over the porch roof | v4:f_0040, v2:f_0956, f_0964 |
| **bay front window** (plane A) | x 1.35 … 3.70, centred 2.525 | 2.35 wide × 1.60 high in **three lights**: side lights 0.62, centre light ≈ 1.00, each with a top light | **both side lights are outward-opening casements**, each hinged on its **outer** jamb (west light on its west jamb, east light on its east jamb) — "this one at the front, this one can open" (west, v4:f_0044–f_0050), "and this one can also open" (east, v4:f_0057–f_0066), opened ≈ 50°. Centre light fixed. Top lights not opened | v4:f_0019, f_0044–f_0066, v2:f_0955–f_0957 |
| **bay east cheek window** (face x 4.15) | y 0.19 … 0.64 | as the west one | assume fixed | seen from inside only (v4:f_0019, f_0068) [I outside] |

- Each first-floor window has a **painted stone sill**; under the bay it is one continuous **ledge ≈ 0.25 m
  deep** (window frames set ≈ 0.13 m back from the wall face + 0.12 m projection), slightly weathered,
  rough white paint, running round the three sides of the bay at Z 3.88–3.95 (v4:f_0049, f_0062–f_0065).
  The porch window has its own sill 1.05 wide, 0.07 thick, 0.06 proud.
- Inside reveals, sill boards (oak), curtains and radiators belong to the first-floor room spec.

### 2.5 Roof level
No dormer, rooflight or gable window is visible on the street side [S for the gable field up to the
verge; I for the main slope, which cannot be seen from the forecourt]. The loft office's Velux looks out at
the *rear* (v5:f_0195 shows back additions through it), so the front slope is taken as unbroken.

## 3. Architecture & trim

### 3.1 Ground-floor plinth and wall [S]
- Below the bay sill the wall is plain smooth white render down to the paving, in two planes: an apron
  band Z 0.30–0.55 flush with the mullion face, and below it a plinth standing ≈ 20 mm proud with a
  weathered (splayed) top edge at Z 0.30 (v2:f_0953, f_0971). No air bricks seen.

### 3.2 Pilasters [S]
- **West pilaster** between the door frame and the bay: x 0.68 … 1.07 (0.39 overall), projecting ≈ 60 mm
  from plane A (face at y −0.18). Plain base block Z 0–0.62 (level with the bay sill, with a small
  moulded top), shaft Z 0.62–2.52 with **three convex reeds** (each ≈ 55 mm wide, 15 mm proud, rounded
  ends top and bottom) between flat margins, moulded capital Z 2.52–2.65 (fillet, cyma, fillet,
  projecting 40 mm), then a plain block up to the cornice. It carries the video doorbell (§5) and, at its
  top east edge, the flag bracket.
- **East corner pilaster**: x 3.955 … 4.15, narrower (0.195), plain shaft with the same capital, carrying
  a small fluted console block under the cornice return (v2:f_0954).

### 3.3 Bay entablature [S]
- Lintel band Z 2.70–2.90: plain, flush.
- **Cornice Z 2.90–3.10**, projecting 0.18 (nose at y −0.30): from the bottom a 30 mm fillet, a 50 mm
  cavetto, a 40 mm flat fascia, a 60 mm cyma recta and a 20 mm top fillet; flat lead-coloured (painted
  white) weathering on top falling outward. Runs x 0.93 … 4.15, returns along the east cheek, and at the
  west end dies against the end of the porch canopy.

### 3.4 Porch canopy = slated lean-to roof over the enclosed porch [S]
- Plan: x −0.86 … 0.93, from wall B (y 0.74) out over the door screen to a fascia at **y −0.55**
  (0.43 m beyond the door face); gutter to y −0.66.
- **Soffit** flat at Z 2.62, white uPVC boards running parallel to the door, with the **three recessed
  downlights** (§8). **Fascia** white uPVC 0.18 high (Z 2.62–2.80). **Gutter** white square-line uPVC,
  114 mm, with white brackets at ≈ 0.6 m centres and stop ends; outlet at the west end into a **white
  square (65 mm) downpipe** that drops beside the door frame at (−0.76, −0.20) to the paving.
- **Roof**: mono-pitch rising from the eaves (Z 2.85 at y −0.58) to the abutment under the porch-window
  sill (Z ≈ 3.70 at y 0.74), pitch ≈ 32°. Covered in **large-format dark blue-grey slates (fibre-cement
  type, ≈ 600 × 300, ≈ 250 gauge, ≈ 6 courses)**, straight bond; lead flashing at the head and lead
  soakers / cover flashing along the bay cheek (east) and the party wall (west). At the east end, forward
  of the bay face, the roof finishes with a small white triangular boxed verge.
- The downpipe from the main eaves (§3.8) discharges through a shoe onto this roof beside the bay cheek.
- (Inside, the 45° ceiling haunches of the vestibule front recess in `ground_corrections.md` V1 sit under
  this roof.)

### 3.5 First-floor bay: apron, splayed corners, corner piers [S]
- **Apron** Z 3.10–3.88: plain white render, in plane A, 3.25 m wide.
- **Corner transition** — the owner's "top is 90 degree but at the bottom is 45, and it's the same on the
  other side" is visible on the outside as well as on the interior piers: the two front corners of the bay
  are **splayed at 45° in the apron zone** (splay face ≈ 0.15 wide, from the cornice top Z 3.10 to
  ≈ 3.70) and return to a **square 90° arris above** through a pointed broach / lamb's-tongue stop
  (Z 3.70–3.88), seen as a V-shaped facet under the sill at each corner (v2:f_0954, f_0957, f_0964).
- **Corner piers** at window level: x 0.90 … 1.35 and 3.70 … 4.15 on the front face, square in plan, each
  with a **sunk flat panel ≈ 0.27 wide × 1.25 high** (15 mm deep, plain margin, Z 4.15–5.40) [S west,
  I east by symmetry].
- Front window head: a small moulded label / drip at Z 5.55–5.62 across the three lights.
- West cheek (x 0.90): plain render with the fixed window (§2.4) and the downpipe.

### 3.6 Bay gable [S west half and apex from below; proportions I]
- The bay is roofed with a **gable facing the street**, eaves at Z 5.95 on both cheeks, apex ≈ Z 7.7 over
  x 2.525 (pitch taken as 45°).
- The verge oversails the wall by ≈ 0.30 m: white **bargeboards** ≈ 0.20 deep with a moulded bed-mould
  under a white boarded soffit; the dark roof covering shows as a thin edge above them.
- **Gable field** (between the window head and the verges) is white render with **applied white-painted
  timber struts** (mock half-timbering, all white): a head rail at Z 5.62, and above it raking struts
  ≈ 90 mm wide and 25 mm proud — on the west half three parallel struts ≈ 0.35 m apart leaning in toward
  the centre at ≈ 60° to the horizontal; the east half mirrors them, with two short curved (concave)
  braces near the centre (v2:f_0956, f_0957; `crop_gable_t955.jpg`, `crop_gable_t956.jpg`). The exact
  pattern of the east half is hidden by the flag.

### 3.7 Entrance bay at first floor (wall B) [S]
- Plain smooth white render from the porch roof to the eaves; the porch window (§2.4) is the only feature.

### 3.8 Eaves, gutters, party-wall kneeler [S]
- Main roof eaves over the entrance bay at Z 5.95: white boarded soffit ≈ 0.25 wide, white fascia, white
  square-line gutter running x −0.70 … 0.78 at y ≈ 0.47, then **turning 90° to run forward along the bay's
  west cheek** (the west eaves of the gable roof) to the gable front. One **white square downpipe** drops
  from this gutter down the cheek at (0.83, 0.08), with a swan-neck at the top, to a shoe on the porch
  roof (v2:f_0959, f_0964; v4:f_0034).
- **Party-wall kneeler, west**: at the party line (x −0.88 … −0.66) a corbelled block of **unpainted
  orange-red facing brick**, six oversailing courses stepping out ≈ 0.30 m from wall B between Z ≈ 5.55 and
  6.00, with a lead/stone-capped top; our white gutter stops against its east side, the neighbour's black
  gutter against its west side (v2:f_0959, `crop_eaves_t958.jpg`).
- East party line: hidden between the two bays; assume the same kneeler behind the gable [I].

## 4. Surfaces & colours

Overcast daylight, near-neutral white balance. "Sampled" = median sRGB of a patch in the named still.

| surface | sampled | true colour / material |
|---|---|---|
| all masonry: render, stone mullions, pilasters, cornice, apron, piers, gable field, sills | #C4C4C0 (shade, v2:f_0956), #DCDCDA, #E8E8E3 (v2:f_0964), ledge #DADAD7 (v4:f_0063) | **brilliant white smooth masonry paint #F2F2EE**, matt, many coats (soft arrises, slightly orange-peel texture); faint grey dirt streaks under sills and on the ledge top |
| gable struts, bargeboards, soffits | same | white gloss on timber **#F4F4F0** |
| uPVC: window frames, door set, fascia, gutters, downpipes, canopy soffit | #CACAC4 – #E0E0DC | white uPVC **#F6F6F4**, satin |
| door / transom glass | grey-white | obscure (stippled) glass in the leaves; **plain acid-etched frosted** transom, colour reads #9A9A94 by day against the dark interior, glowing warm at night |
| window glass | reflects sky and the trees opposite | clear double glazing, slight green edge tint; ground-floor lower lights show the white shutters (#EDEDEA) behind |
| porch roof slates | wet #7F8084 (v4:f_0063), #848287 (v4:f_0034) | dark blue-grey fibre-cement slate **#4B4E57**, matt, light lichen at the laps |
| lead flashings | — | weathered lead **#7C8087** |
| door furniture | — | polished brass **#C9A44C** |
| party-wall kneeler brick | #7E6B69 (back-lit) | orange-red facing brick **#A4553A**, dark weathering on the upper faces |
| main roof and gable covering | only a dark edge is seen | **inferred**: dark grey slate / fibre-cement slate to match the porch roof, **#474A52** (the house to the east has dark grey interlocking concrete tiles, the ones opposite a mix of slate and red-brown clay tile) |
| neighbours (massing) | brick #82654D | red brick **#9A553C** with white bands #EDEDE8; west neighbour's first floor cream **#EFE8D2** |

## 5. Fixed fittings on the elevation

| item | position (x, y, Z) | description | tag |
|---|---|---|---|
| Video doorbell | on the west pilaster face, centre (0.86, −0.19, 1.28) | black rectangular unit 0.045 × 0.125 × 0.025, small lens at the top and a round button at the bottom, on a black backplate | S (v2:f_0953–f_0964) |
| Outdoor socket | under the bay sill, on the apron band below light 1, centre (1.45, −0.14, 0.42) | grey weatherproof (IP66) single socket enclosure 0.16 wide × 0.10 high × 0.08 deep with a hinged lid, slightly tilted; cable entry from behind. Light grey **#B9BBB8** | S (v2:f_0953, f_0971) |
| Rainwater pipe, canopy | (−0.76, −0.20), Z 0 … 2.75 | white square 65 mm uPVC with clips at 0.9 m, shoe at the paving | S |
| Rainwater pipe, main eaves | on the bay west cheek at (0.83, 0.08), Z 3.75 … 5.90 | white square 65 mm, offset bend at the top, shoe onto the porch slates | S |
| Canopy downlights | soffit Z 2.62 at (−0.38, −0.34), (0.00, −0.34), (0.38, −0.34) | recessed, white bezel Ø 90, see §8 | S |
| Security floodlight / camera | bay corner above the east end of the canopy ≈ (1.05, −0.25, 2.95) | small black unit on a short arm with a visible cable; optional | S (v2:f_0964) |
| Flag bracket, pole, flag | bracket (0.98, −0.15, 2.38) | see `front.md` §7.1 | S |
| Door-contact / alarm sensors | on the door frame's east jamb at Z ≈ 1.4 and 2.2, and one low on the pilaster | small white plastic boxes ≈ 25 × 70; omit (declutter) | S |
| Trickle vents | heads of the bay top lights and of the first-floor windows | slim white/aluminium strips; optional | S |

No house number plate, no knocker, no bell push other than the doorbell, no hanging baskets, no satellite
dish or aerial visible on our front.

## 6. Roof form (mostly inferred)

| element | description | tag |
|---|---|---|
| Main front slope | plain pitched slope rising from the eaves at Z 5.95 (y ≈ 0.50) toward a ridge parallel to the street; pitch taken as **42°**, dark slate. Only its lowest edge (soffit, fascia, gutter) is seen over the entrance bay | eaves S, rest I |
| Ridge | parallel to the street at Z ≈ 9.0, y ≈ 3.9 | I — must agree with the loft-office section (sloped ceilings both sides of that room, its Velux in the rear slope) |
| Bay gable roof | ridge perpendicular to the street at x 2.525, from the gable apex (Z ≈ 7.7, y −0.42) back into the main slope, forming two valleys; eaves Z 5.95 along both bay cheeks; verge overhang 0.30 at the front | S at the west eaves and verge, apex height I |
| Party walls at roof level | no raised parapet seen; slates assumed to run through with the neighbours' roofs, brick kneelers at the front eaves | I |
| Chimney | **none is visible from the forecourt or from the front windows.** For this house type a brick stack with clay pots normally stands on a party wall at or just behind the ridge; the living room and kitchen have no chimney breasts (`living.md`, `kitchen.md`), so if a stack is modelled put it on the ridge line where the rear / loft specs find one. Do not invent one on the front slope | I |
| Rooflights | none on the front slope | I |

## 7. Neighbouring houses on the elevation (massing only, no numbers, no detail)

- **West (x < −0.88)**: same storey heights. Ground floor red brick with an open round-arched porch
  (white-painted arch) beside the party line and a bay beyond; first floor cream-painted with a window
  directly beside the kneeler; black gutter at the same eaves height; black downpipe on the party line
  (v2:f_0959, f_0963, v4:f_0040). Its front wall is in plane B (y 0.74).
- **East (x > 4.53)**: red brick with white stone bands, a two-storey **canted** bay starting ≈ 0.5 m from
  ours, small-paned sash windows, a front gable with dark grey tiles and a red clay finial at the same
  height as ours (v2:f_0955, v4:f_0052).
- Model each as a simple extruded block in the right overall colour with a gable, at most; they exist to
  stop the façade looking free-standing.

## 8. Lighting & switches

- **Canopy downlights ×3** (the "outside lights"): warm white ≈ 3000 K, ≈ 5 W LED each, lighting the door
  screen and the threshold paving. Off in the daylight footage, on in the night video (seen through the
  transom). Controlled, by the assumption recorded in `ground_corrections.md`, from the **right-hand
  (south) rocker of the hall 3-gang switch at (0.65, 3.29, 1.27)** together with the vestibule lantern and
  recess downlights (owner: "this one also controls the porch light, the vestibule", v2:f_0998–f_1003).
- No other light fittings on the elevation (the black unit on the bay corner is treated as a camera).
- At night the elevation is otherwise lit only by what spills through the windows: living-room bay
  (shutters closed → slatted glow in the lower lights, clear top lights), door glazing and transom, the two
  first-floor windows.

## 9. Reference frames

| frame | still / crop | shows | camera |
|---|---|---|---|
| v2:f_0953, f_0954 | `v2_t952.jpg`, `v2_t953.jpg`, `crop_bay_t953.jpg` | ground-floor bay obliquely: plinth, sill, socket, mullion/transom grid, top-light vents, pilaster reeds and capital, doorbell, cornice profile, east corner pilaster, first-floor apron and its V-shaped corner stop | (−0.1, −0.8, 1.5) looking +X/+Y |
| v2:f_0955 – f_0957 | `v2_t954.jpg` – `v2_t956.jpg`, `crop_gable_t955.jpg`, `crop_gable_t956.jpg` | **the only views of the upper bay and gable**: west cheek window, downpipe, corner pier panel, front window, head rail, raking struts, bargeboard and apex, eaves gutter returning along the cheek | (−0.2, −1.0, 1.5) looking up, +X/+Y |
| v2:f_0959 | `v2_t958.jpg`, `crop_eaves_t958.jpg` | looking straight up at the door: canopy soffit with 3 downlights, fascia, gutter, west downpipe, transom (lettering — do not use), main eaves, **brick kneeler**, neighbour's black gutter | (0.2, −0.7, 1.5) looking up |
| v2:f_0961 | `v2_t960.jpg` | east leaf from outside, threshold, pilaster base | (0.5, −1.2) looking +Y |
| v2:f_0963 – f_0965 | `v2_t962.jpg`, `v2_t963.jpg`, `crop_upper_t963.jpg` | **best frontal view**: door set with both leaves open outward, canopy, pilaster, bay lights 1–2, porch window above, bay west cheek window, pipe and shoe, apron corner stop, flag; neighbour's arch at the left edge | (0.4, −1.7, 1.5) looking +Y, slightly up |
| v2:f_0971 | `v2_t970.jpg` | whole ground-floor face in one plane seen along it, plinth step, socket | (−0.4, −0.4) looking +X |
| v4:f_0019 | `reference/v4/frames/f_0019.jpg` | first-floor windows from inside: square bay, 3-light front window with top lights, east cheek window, porch window to the right of the pier | inside the front room looking −Y |
| v4:f_0034 | `v4_t33.jpg` | porch window opened outward (hinge west), stone sill, porch slates directly below, bay west cheek with the downpipe, flag | at the porch window looking −Y/+X |
| v4:f_0040 | `v4_t39.jpg` | through the fixed bay west cheek window: porch roof slates and flashings, the west neighbour's front wall | bay, looking −X |
| v4:f_0047, f_0049 | `v4_t46.jpg`, `v4_t48.jpg` | bay front window, **west light open (hinge west)**, friction stay, stone sill ledge depth, view straight down | bay front, x ≈ 1.8 |
| v4:f_0060 | `v4_t59.jpg` | bay front window, **east light open (hinge east)** | bay front, x ≈ 3.4 |
| v4:f_0062 – f_0064 | `v4_t61.jpg` – `v4_t63.jpg` | along the façade toward −X from the open east light: sill ledge, porch roof and its boxed east verge, flag pole, kneeler side of the neighbour | bay front, x ≈ 3.4, looking −X |
| v5:f_0195 | `sheet_v5_loft.jpg` | view out of the loft-office Velux = rear, so no rooflight on the front slope | — |

## 10. Interactions

| object | action | evidence |
|---|---|---|
| Street doors, both leaves | swing **outward** ≈ 100° about (±0.59, −0.12); west leaf first | v2:f_0941–f_0966, f_0978–f_0982 |
| First-floor porch window, lower casement | opens **outward**, side-hung on the **west** jamb, to ≈ 45° (friction stay) | v4:f_0030–f_0036 |
| First-floor bay front window, west light | opens outward, hinged on its west jamb, ≈ 50° | v4:f_0044–f_0050 |
| First-floor bay front window, east light | opens outward, hinged on its east jamb, ≈ 50° | v4:f_0057–f_0066 |
| First-floor bay west cheek window | **fixed** ("cannot be opened") | v4:f_0038–f_0042 |
| Ground-floor bay lights and top lights | not operated from outside or inside (the shutters and curtains inside are: see `ground_corrections.md` L5) | — |
| Canopy downlights | switch with the porch gang (§8) | assumption |
| Flag | optional sway | — |

Handles of the first-floor casements are brass/gold espagnolette levers on the inside (first-floor room
spec). Seen from outside an open casement shows its white frame edge and the stay arm at the sill.

## What other areas must agree with

1. **First-floor level and window heights** (front room spec): sill 3.95, head 5.55 assume the front-room
   floor is at Z ≈ 3.23 with inside sill boards ≈ 0.72–0.80 above it and heads ≈ 2.32 above it. If the
   first-floor spec fixes other values, move all first-floor windows, the sill ledge, the porch-roof top
   (0.15–0.25 below the porch-window sill) and the eaves (≈ 0.40 above the heads) together.
2. **First-floor bay plan**: square bay stacked on the ground-floor bay, outer faces x 0.90 / 4.15,
   front y −0.12, main wall outer face y 0.74; front window x 1.35 … 3.70; cheek windows y 0.19 … 0.64;
   porch window centred x ≈ 0.0 (±0.15), 0.85 wide.
3. **Street-door swing** outward: `house.json` `d_street.swingInto` → `outside` (already in
   `ground_corrections.md` V3).
4. **Roof**: ridge height/position, slope pitch, chimney stacks and the party-wall treatment must come
   from the loft-office / eaves and rear-elevation specs; the values here are placeholders consistent with
   what is visible from the street.
5. **Canopy lights** on the hall porch gang (ground corrections).

## Doubts

1. Everything above Z 5.6 is from two steep upward stills: gable pitch (40–50°), apex height (7.4–8.1),
   barge overhang (0.2–0.35) and the strut pattern (three raking struts per side seen on the west half
   only) are approximate.
2. The first-floor corner treatment (45° splay in the apron returning to a square corner with a pointed
   stop; sunk panels on the piers) is read from oblique views; the splay width (0.15) is taken from the
   matching interior chamfer.
3. Porch-roof pitch (≈ 32°) and the number of slate courses: its head is fixed by the porch-window sill
   and its eaves by the door head, the slate size is judged from v4:f_0040.
4. Depth of the first-floor sill ledge (0.25; range 0.20–0.35) and cornice projection (0.18).
5. West pilaster width 0.39 and the 0.15 jamb between it and light 1 share 0.54 m between the door frame
   (x 0.62) and light 1 (x 1.245); the split is ±0.05.
6. Whether the ground-floor bay lights open at all (uPVC casements normally do); not shown.
7. East cheek of the bay at both floors and the east party-line detail are never seen from outside.
8. Main-roof covering material and colour are inferred from a thin dark edge.
9. The black unit on the bay corner may be a floodlight rather than a camera.

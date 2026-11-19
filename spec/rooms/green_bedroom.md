# green_bedroom — first-floor front bedroom ("the green bedroom")

Source: v3 f_0490–f_0703 (lights on, curtains closed), v4 f_0001–f_0102 and f_0203–f_0245 (daylight, curtains
open). Full-res stills, crops and montage sheets in `reference/work/p2_green/` (`v3_fNNN.jpg`, `v4_fNNN.jpg` =
full-res still of frame NNN). Owner narration (v3 08:04–11:46, v4 00:00–01:42, 03:22–04:04):
"there's a two step up here … this is still on the first floor … towards the front of the house … this is the
green bedroom, double wooden door … I got the pediment, it's the same on either side … two wardrobes, this is the
big one … and a small wardrobe, wardrobe doors can open to see clothes … in the corner there's an aircon, clothes
hanger, look at the pelmet … green bed … nightstand, Queen Anne style, wood inlay, marble top … sockets in here …
storage cabinet, wooden, open and close … a bureau, the bureau can also open and close … storage cabinet, there's
a telly, whisky glasses, window, you can open it … another nightstand, side light, these are called the pineapple
lights … an armchair with a stool, a small coffee table, green … corner chair … the curtain can open … there's a
pelmet here" and (v4) "this window can open … this window cannot be opened … this one at the front can open …
radiator … this one can also open … there's a smooth transition here, top is 90 degree angle but at the bottom is
45, and it's the same on the other side … I got a sliding door right here".

**All coordinates in this file are WORLD coordinates** (BRIEF frame: +X right walking in, +Y into the house,
metres). Heights `z` are **above this room's finished floor**; add the floor level for world Z.

Dimension confidence: plan outline ±0.08 m (party walls, front wall line and bay are taken from `house.json`,
then checked against door-leaf scale in v3_f524 / v4_f95 and the furniture run on the east wall); positions of
doors and furniture along a wall ±0.08; heights ±0.05 below 2.1 m, ceiling ±0.08; floor level ±0.05.

## 1. Shape & dimensions

Full-width front room over the living room, the front hall and the vestibule's rear half, with the square bay
carried up. One level, flat ceiling.

- **Floor level: world Z = +3.22** (ground-floor stair lands at 2.85 after 15 risers of 0.19; the gallery then
  climbs "two steps" of ≈ 0.185 → 3.22 = living-room ceiling 2.95 + 0.27 floor). Same level as the front
  landing and `green_bathroom`; flush brass threshold strips at both doors.
- **Ceiling: 2.95 above the floor** (world Z 6.17), flat, in the bay too. Door-leaf scale gives 2.96 (v3_f524)
  and 2.95–3.05 (v4_f95); cornice underside at 2.85.
- Polygon (inside plaster faces, counter-clockwise):
  `(-0.65, 0.99) (1.16, 0.99) (1.16, 0.14) (3.90, 0.14) (3.90, 0.99) (4.30, 0.99) (4.30, 4.73) (-0.65, 4.73)`
- Main rectangle **4.95 (X) × 3.74 (Y)**; bay **2.74 wide × 0.85 deep** inside (x 1.16–3.90, y 0.14–0.99).
  The bay shell is solid upstairs (≈ 0.255 m walls with deep timber sills) so it is 0.16 narrower and 0.14
  shallower inside than the ground-floor bay, with the same outer faces (x 0.90 / 4.15, y −0.12).
- Optional room-local frame: local x = X + 0.65, local y = Y − 0.99 (origin = SW inside corner, axes parallel
  to world).

| wall | plane | what is on it |
|---|---|---|
| W-front (street) | y = 0.99, x −0.65 → 1.16 | west ("side") window, curtain, pier with 3-arm sconce, bureau |
| bay | x 1.16–3.90, y 0.14–0.99 | 3-light front window, cheek windows, radiator, armchair / drum table / corner chair |
| east nib | y = 0.99, x 3.90 → 4.30 | plain, chamfered arris |
| W-east (party) | x = 4.30 | S nightstand, bed + headboard, picture, pineapple lights, N nightstand, small wardrobe, air-con |
| W-rear | y = 4.73 | door 1 (landing), big wardrobe, sliding door (bathroom), coat rail, switches |
| W-west (party), **dark green** | x = −0.65 | plant, chest of drawers with TV above, tall mirror |

Plan (not to scale; top = +Y / rear, right = +X):

```
        landing      |            green_bathroom
 4.73 +--[door 1]--+========+--[sliding]-->pocket--+---+
      |m           | BIG    |            hooks    |SM |
      |i -0.28..0.48 WARDROBE  2.34..3.03         |WAR| a/c above
      |r           0.80..2.10                     |DR |
      |r                         (chandelier)     +---+
      |                                           [ns]|
      |CHEST                 +-------+----------------| pineapple light
      |+ TV                  | CHEST |   KING BED     | picture above
      |(dark green wall)     | (lid) |                |
      |                      +-------+----------------| pineapple light
      |plant                                      [ns]|
 0.99 +--[west win]--+bureau+ . . . . . . . . . . +nib+
     -0.65       0.23     1.16| chair  table  armch|3.90  4.30
                              |  [== radiator ==]  |
 0.14                         +--[W csmt|fix|E csmt]--+
```

## 2. Openings

### 2.1 Door 1 — landing ↔ bedroom (W-rear)
- Clear opening **x −0.28 → 0.48** (centre 0.10), 0.762 × 1.981. Wall is the stud partition y 4.73–4.87.
- Leaf: oak-veneer Victorian **4-panel** (two tall upper, two short lower panels, bead-moulded), satin lacquer,
  sampled #A2885A, true **#B8905A**. Polished-brass scroll lever on a long backplate at z 1.00, three brass
  butt hinges. **Hinged on the EAST jamb (x 0.48), swings SOUTH into the bedroom**; stands at ≈ 95° in front of
  the big wardrobe's west end (v3_f524, v3:f_0528). Brass threshold bar.
- Surround, bedroom side: moulded white architrave 0.10 wide (outer x −0.38 … 0.58, top z 2.08) carrying a
  **pedimented doorcase** — see §3.3. Landing side has its own pedimented doorcase (belongs to `landing1`).

### 2.2 Sliding pocket door — bedroom ↔ bathroom (W-rear)
- Clear opening **x 2.34 → 3.03** (0.69 m, centre 2.685), head 1.98. Centred on the bathroom's south wall.
- Oak 4-panel leaf (same pattern as door 1, ≈ 1981 × 762 × 35) hung from a concealed top track; **slides EAST**
  into a pocket in the wall at x 3.03 → 3.80 (behind the coat rail). Closed in v3; opened by hand in
  v4:f_0098–f_0104. Round polished-brass flush pull with privacy turn on each face, centre z 1.00, 60 mm from
  the leading (west) edge; brass finger pull in the edge. Oak lining 0.14 deep with a black brush seal.
- Surround: identical pedimented doorcase to door 1 on the bedroom side (outer architrave x 2.24 … 3.13);
  a different, taller pediment on the bathroom side (see `green_bathroom` §3).

### 2.3 Bay front window (y = 0.14 wall, frame set to the outside)
- White uPVC, clear double glazing. Frame **x 1.50 → 3.56 (2.06 wide), z 0.70 → 2.55**, centred on the bay
  (2.53); transom at z 2.00; two mullions. Solid wall 0.34 wide each side of the frame to the bay corners.
- Three lights below the transom, three top-lights above:
  - **west light** (x 1.50–2.05): side-hung casement, **hinged on its west (outer) stile, opens OUTWARD** —
    "this one at the front can open" (v4:f_0043–f_0053). Brass-finish espagnolette handle on the east stile at
    z 1.32. Opens to ≈ 60° on a friction stay.
  - **centre light** (x 2.07–2.99): fixed.
  - **east light** (x 3.01–3.56): side-hung casement, **hinged on its east (outer) stile, opens OUTWARD** —
    "and this one can also open" (v4:f_0054–f_0066). Handle on the west stile at z 1.32.
  - top-lights (z 2.03–2.52): outer two fixed; the **centre one is a top-hung vent** (handle at its bottom rail,
    white trickle vent in its head) — not operated in the video.
- Frame face ≈ 0.18 behind the plaster; **stained hardwood sill board** 0.20 deep, 25 mm thick with a rounded
  nosing, top at z 0.68, running the full bay width x 1.16–3.90 and returning along both cheeks. Plastered
  reveals and head (head soffit at 2.58). Sill colour sampled #9F8776, true **#8E5F3F** (mid mahogany stain).

### 2.4 Bay cheek windows (x = 1.16 and x = 3.90 walls)
- One light each: frame **y 0.32 → 0.80 (0.48 wide), z 0.70 → 2.55**, transom at 2.00 (lower light + top-light).
- **West cheek: fixed** — "this window cannot be opened" (v4:f_0033–f_0041); it looks down on the slate porch
  roof and the flag. East cheek: no handle seen; model fixed. Same sill board and reveals.

### 2.5 West ("side") window (W-front, x −0.65 … 1.16 part)
- Plaster reveal **x −0.41 → 0.23 (0.64 wide)**, 0.18 deep; frame z 0.78 → 2.58, transom at 2.03.
- Lower light: side-hung casement, **hinged on the WEST stile, opens OUTWARD** (handle on the east stile,
  z 1.35) — opened twice: v3:f_0624–f_0632 ("you can open it … you can see the two cars") and v4:f_0024–f_0034
  ("this window can open … you can see the flag outside"). Top-light: top-hung vent with handle (not operated).
- Hardwood sill board as the bay, top at z 0.75, x −0.43 … 0.25.
- Outside, 0.3 m below the sill: the grey-slate lean-to roof over the street doors, with the flag-pole bracket
  on the bay's north-west corner (front-elevation spec owns these).

## 3. Architecture & trim

### 3.1 Skirting, cornice, ceiling
- **Skirting**: white gloss, **0.17 high × 20 mm**, torus-and-ogee top moulding; all walls incl. bay. At the two
  chamfered bay corners it **follows the chamfer in three faces with two mitres** (v4 still t86,
  `reference/work/p2_reconcile/c_v4_t86_skirt.jpg`) — the chamfer runs down to the floor.
- **No dado rail, no picture rail** in this room (the landing has a dado; it stops at the door).
- **Cornice**: white plaster, ≈ 0.10 drop × 0.12 projection: plain cove between two fillets with a small
  enriched band (repeating leaf / bead ornament, ≈ 25 mm high) at the wall edge (v3:f_0568, v3:f_0530). Runs
  on all walls and **breaks forward round the two bay corners** as a square block (v4:f_0079–f_0083, v4_f1).
- **Ceiling rose**: cast plaster, Ø ≈ 0.60, acanthus leaves in a beaded ring, at the chandelier (v4:f_0023).
- Ceiling: flat white matt, sampled #BEB9A6, true **#F5F4F0**.

### 3.2 Bay corners — "top is 90 degree, bottom is 45, same on the other side"
- The two external arrises where the bay opens into the room — at **(1.16, 0.99)** and **(3.90, 0.99)** —
  are **chamfered at 45°, face ≈ 0.12 wide (legs ≈ 0.085; 0.10–0.15), from the floor up to z ≈ 2.30**, where
  the chamfer dies into the square arris through a **quarter-round ("lamb's tongue") stop ≈ 0.10 high**; above
  the stop (z 2.40) the corner is a plain 90° arris up to the cornice, which breaks forward round it as a square
  block (v4_f1, v4:f_0079–f_0093, v4 stills t86 / t92, v3:f_0638). The first draft said "≈ 60 mm, from the top
  of the skirting"; measured again in the verification round against the bedside switch plate and the skirting,
  the face is about twice that and the skirting mitres round it. Canonical: `house.next.json` feature
  `green_bay.chamfers`.
- East side: the corner belongs to a nib x 3.90–4.30 (0.40 wide, face y 0.99) standing 0.85 in front of the
  bay's east wall; west side: the bay's west wall simply meets the front wall.

### 3.3 Pedimented doorcases (bedroom side of both doors — "the same on either side")
Two identical white-gloss doorcases flank the big wardrobe (v3_f524, v4_f95, v3:f_0530, f_0568, v4:f_0096):
- moulded architrave 0.10 wide round the opening, top at z 2.08;
- plain frieze board z 2.10 → 2.30, as wide as the architrave, carrying an applied relief: a centre
  shell / anthemion with a leafy swag running out to each side;
- a pair of **acanthus scroll consoles** (≈ 0.09 wide × 0.36 high × 0.09 projection, z 1.95 → 2.31) hanging
  either side of the frieze, outside the architrave;
- moulded cornice shelf z 2.31 → 2.37, **1.30 m long**, projecting ≈ 0.10, resting on the consoles;
- low **triangular pediment** on the shelf: raking mouldings rising to an apex at **z 2.60**, tympanum filled
  with an anthemion (fan of palm leaves) and scrolling foliage; the raking mouldings end at each lower corner
  in a small **volute scroll** sitting on the shelf end.
- Overall 1.30 wide × 0.65 high above the door head. Door 1 case centred x 0.10; sliding-door case centred
  x 2.685. (Door 1's measures 1.40 wide in v3_f524 and the sliding one 1.26 in v4_f95 — use 1.30 for both.)

### 3.4 Pelmets — "look at the pelmet … let you get the pelmet right"
- **Bay**: a ceiling-fixed pelmet box follows the three bay walls, **0.15 deep × 0.17 drop** (underside
  z 2.78), faced with the room cornice profile so it reads as a deeper cornice; the curtain track is hidden
  behind it (v3:f_0686–f_0702, v4_f75, v4:f_0077).
- **West window**: the same boxed pelmet across the window, x −0.52 → 0.34, projecting 0.12 from the wall;
  the wall cornice steps forward round it (v4_f11, v4:f_0009).

## 4. Surfaces & colours

| surface | finish | sampled sRGB | estimated true colour |
|---|---|---|---|
| W-east, W-rear, W-front, bay, nib | matt emulsion, **pale sage / mint green** | #C4C4AD, #D1D6C7, #D5D9CB (daylight), #BAB79E (lamps) | **#D4E0D2** |
| W-west (TV wall), full height | matt emulsion, **deep teal green** ("green bedroom") | #344240, #3F4F47 (shade), #698871 (lit) | **#3F6B5C** |
| ceiling | white matt | #BEB9A6, #C7C7BE | **#F5F4F0** |
| cornice, rose, skirting, doorcases, pelmets | white (gloss on joinery) | #D1CABA, #E1DCD4 | **#F4F3EF** |
| floor | fitted cut-pile carpet, pale silver-beige, slight sheen and tread marks | #C7BDB4, #C4C0C1 | **#CFCAC3** |
| oak doors | oak veneer, satin | #A2885A | **#B8905A** |
| window frames | white uPVC | — | **#F2F2F0** |
| sill boards | stained hardwood, satin | #9F8776 | **#8E5F3F** |

The dark wall meets the pale walls in the two west corners; cornice and skirting stay white on it.

## 5. Fixed fittings

- **Radiator** (bay, under the front window): white vertical-tube radiator with domed tube tops — ≈ 28 flat-oval
  tubes at ≈ 50 mm pitch, **1.43 long × 0.48 high × 0.10 deep**, x 1.82 → 3.25, standing 30 mm off the wall
  y 0.14, z 0.12 → 0.60. White/chrome TRV at the east end (x 3.30), lockshield at the west end (v4_f71 crop,
  v4_f21). Sampled #AEAAA1, true #F0F0EE.
- **Air-conditioning unit**: white wall-mounted split indoor unit **0.80 w × 0.29 h × 0.22 d** on W-east above
  the small wardrobe, y 3.80 → 4.60, z 2.36 → 2.65, rounded front, louvre at the bottom (v3:f_0562–f_0564,
  v3_f522). Its white remote sits in a wall holder on W-rear at x 3.19, z 1.22–1.40 (immediately left of switch S4). A white fused-spur plate
  on W-rear at x 3.95, z 2.25.
- **Coat rail** ("clothes hanger"): oak board 0.50 × 0.09 with six polished-brass double hooks, on W-rear
  x 3.30 → 3.80, z 1.75 (v3:f_0566). Model empty.
- **TV**: ≈ 85-inch flat screen **1.90 × 1.08 × 0.04**, wall-mounted flush on W-west, y 1.50 → 3.40,
  z 1.10 → 2.18. Blank dark screen (v3:f_0612–f_0618, v4_f25).
- **Sockets** (white, double unless noted, centre z 0.30): W-east behind each nightstand at y 1.24 and
  y 3.34 ("there are sockets in here", v3:f_0588–f_0590); W-front under the west window at x 0.15; bay front
  wall west of the radiator at x 1.50 (z 0.45); W-west behind the chest at y 2.45; W-front east nib none.
- Switches: see §8.

## 6. Furniture

Footprints are plan rectangles in world coordinates; `h` = height above the floor. Everything dark is antique
/ reproduction dark oak (Jacobean "Old Charm" type) unless noted: sampled #523F36, true **#4A3426**, satin wax.

| # | item | footprint (x, y) | h | description |
|---|---|---|---|---|
| F1 | **Bed** (king) | divan x 2.20 → 4.20, y 1.54 → 3.04 | mattress top 0.65 | Dark-green velvet divan base 0.38 high on low castors; deep mattress. Bedding neat: sage-green fitted cover with a fine cream leaf-fleck (#7E8C5E), dark charcoal duvet and four pillows printed with large botanical leaves and pale pink / white flowers (ground #2B2630, leaves #5F8E7A, flowers #D9C9C4). |
| F2 | **Headboard** | x 4.20 → 4.30, y 1.47 → 3.11 | 1.29 | Floor-standing rectangular panel 1.64 wide × 0.10 thick, **dark bottle-green velvet, deep diamond buttoning** (5 rows, ≈ 0.20 pitch), plain piped edge. Sampled #282A24, true **#1F3A30**. |
| F3 | **Nightstand N** (shown first: "Queen Anne style, wood inlay, marble top") | x 4.00 → 4.30, y 3.16 → 3.52 | 0.70 | French-style bombé bedside chest: **three serpentine drawers** veneered in kingwood / rosewood laid in a chevron, each with a floral marquetry spray and a gilt-bronze rococo swing handle; gilt-bronze leaf mounts on the front corners; four slender **cabriole legs** with gilt sabots (drawer case z 0.33 → 0.67, shaped apron); **shaped cream / beige breccia marble top** 0.38 × 0.32 × 0.03 with an ogee edge, overhanging 15 mm. Wood #8A5A32, inlay #D8B77A, marble #E4D8BE with #B9A27C veining, mounts #B08D3C (v3:f_0572–f_0590). |
| F4 | **Nightstand S** | x 4.00 → 4.30, y 1.06 → 1.42 | 0.70 | Identical to F3 (v3:f_0640–f_0646, v4_f1). |
| F5 | **Blanket chest** ("storage cabinet, wooden, open and close") | x 1.70 → 2.16, y 1.69 → 2.89 | 0.52 | Dark-oak panelled coffer at the foot of the bed, 1.20 long × 0.46 deep: four fielded panels on the front, one on each end, stile feet; **hinged lid** with four sunk panels and a moulded edge, overhanging 20 mm (v3:f_0598–f_0600, v3_f520). |
| F6 | **Big wardrobe** | x 0.80 → 2.10, y 4.21 → 4.73 | 1.72 | Dark-oak two-door wardrobe 1.30 × 0.52: each door has a **linenfold-carved upper panel** (4 folds), a carved rosette / lunette rail at mid height (z ≈ 1.05) and two plain fielded panels below; black iron butterfly hinges, drop-ring handles at the meeting stiles (a cream tassel on the right-hand key); moulded cornice, shaped plinth with bracket feet (v4_f95, v3:f_0544–f_0548, v4:f_0218–f_0222). |
| F7 | **Small wardrobe** | x 3.80 → 4.30, y 3.60 → 4.62 | 1.80 | Same family, 1.02 wide × 0.50 deep, back to W-east in the NE corner, **doors face west**: two doors each with one linenfold upper panel, a carved rail and plain panels below. Inside: a top shelf at z 1.45 over a hanging rail (v3:f_0550–f_0564). |
| F8 | **Bureau** | x 0.32 → 1.08, y 0.99 → 1.44 | 1.02 | Dark-oak Jacobean-revival bureau on a stand, 0.76 × 0.45: sloping **fall front** (z 0.78 → 1.02 at ≈ 60°) with a mitred geometric moulded panel, brass escutcheon and a cream tassel on the key; **three long drawers** below (z 0.36 → 0.78) each with a geometric moulded front and two round turned knobs; open stand with four bulbous turned legs on bun feet joined by a low perimeter stretcher (z 0.08). Interior: a row of arched pigeonholes over small drawers, and a tooled dark-green / brown leather writing surface on the inside of the fall (v3:f_0602–f_0610, v4_f11, v4_f238). |
| F9 | **Chest of drawers** ("storage cabinet", under the TV) | x −0.65 → −0.15, y 1.55 → 3.35 | 0.86 | Mid-brown mahogany / cherry American-colonial-style block-front dresser 1.80 × 0.50: three bays of drawers — outer bays three deep drawers, centre bay slightly recessed with three drawers — top row of small drawers with two **carved fan / shell fronts** and an arched panel; polished-brass bat-wing back-plates with bail handles; moulded top edge; ogee bracket feet. Wood sampled #6A4630, true **#7A4B2C** (v3:f_0612–f_0618, v4_f25). |
| F10 | **Armchair** | centre (3.45, 0.85), 0.68 w × 0.75 d, facing north-west | seat 0.42, back 0.95 | c. 1920 mahogany show-wood armchair: square upholstered back with a shaped pierced top rail, outward-scrolled arms, sprung seat, carved apron, **ball-and-claw front feet**; covered in a cream-ground **tapestry weave with brown / olive flowers and urns** (#D9CFB8 ground, #7A6A52 pattern), cream gimp trim (v3:f_0662–f_0672, v4_f1). |
| F11 | **Footstool** ("with a stool") | centre (3.45, 0.85) — stored under the armchair seat | 0.20 | Low shaped (serpentine hexagon) stool 0.42 × 0.42 on short carved cabriole feet, top in **sage-green needlepoint with a centre bouquet of white / pink flowers** (v3:f_0670–f_0674). |
| F12 | **Small coffee table** | centre (2.75, 0.72), Ø 0.55 | 0.55 | Mahogany **octagonal drum table**: top inset with **green gilt-tooled leather**, 0.08 deep frieze, turned baluster pedestal on three splayed sabre legs with brass caps (v3:f_0676–f_0680). |
| F13 | **Corner chair** | centre (2.05, 0.80), 0.60 × 0.60, rotated 45° (back toward the bay's SW corner) | seat 0.45, rail 0.75 | Edwardian mahogany corner chair: curved top rail with a raised inlaid cresting, two panels of slim spindles, three turned uprights, square drop-in seat in cream floral tapestry with brass studs, four turned legs with an X stretcher (v3:f_0682–f_0684). |
| F14 | Plant | pot centre (−0.38, 1.30), Ø 0.30 | 1.15 | Bushy small-leaved ficus (weeping fig) in a ribbed celadon-green ceramic pot, between the west window and the chest (v4_f25). |

## 7. Art, mirrors, decor

| # | item | wall / position | size (m) | description |
|---|---|---|---|---|
| A1 | **Picture over the bed** | W-east, centre y 2.29, z 1.52 → 2.38 | 0.92 w × 0.86 h | Wide gilt frame (≈ 70 mm stepped, bright gold #C9B26A) with a 60 mm ivory mount. The real image is a monochrome photograph of a couple — **do NOT reproduce**; use a neutral grey-toned abstract / architectural wash (v3:f_0520, f_0656). |
| A2 | **Big mirror** ("there's a mirror in here") | W-west, y 3.62 → 4.40, z 0.28 → 2.08 | 0.78 w × 1.80 h | Plain mirror in a **90 mm dark-brown (espresso) stepped / ogee moulded frame**, hung flat on the dark wall next to door 1 (v3:f_0532–f_0534, v4:f_0205–f_0207). Render a real reflection; never bake the video reflection (it shows the owner). |
| A3 | Photo frames ×3 | on the bureau top, z 1.02 | 0.20 × 0.16, 0.26 × 0.22, 0.24 × 0.20 | Cream frame; frame with a grey / white diamond (ikat) pattern; dark-walnut frame. **Blank / abstract inserts** — family photographs are not reproduced. |
| A4 | **Tantalus** | on the chest, (−0.40, 2.05) | 0.32 × 0.15 × 0.33 | Oak and brass tantalus with two square cut-crystal decanters under a brass locking bar and handle (v3:f_0620). |
| A5 | **Whisky glasses** | on the chest, (−0.40, 1.75) | tray 0.34 × 0.24 | Oval pierced-rim silver tray carrying six cut-crystal tumblers / small stemmed glasses (v3:f_0620–f_0622). |
| A6 | Jewellery chests ×2 | on the chest, (−0.45, 2.45) and (−0.45, 2.80) | 0.30 × 0.20 × 0.25 | One plain cherry chest of eight small drawers; one carved oak casket. Omit the loose items around them. |

**Curtains** (same fabric everywhere): heavy woven jacquard, **cream ground with large upright feather-like
leaves in sage, olive and grey-green**, some leaves with a fine herringbone vein (#E3DFD0 ground; leaves #7C8B63,
#9AA57E, #5E6B50), cream lining; 75 mm pencil-pleat heading tucked under the pelmets; drop from z 2.78 to
z ≈ 0.62 (just below the sills, clear of the radiator top).
- Bay: one track round the three walls with **four drapes** — two on the front wall meeting at x 2.53, one
  across each cheek. Open state (v4): each cheek drape and its neighbouring front drape gathered together at the
  front corners of the bay — bundles at (1.30, 0.25) and (3.76, 0.25) — and held by **dark-green rope tie-backs
  with a large green tassel** on brass hooks at z 1.15. Closed state (v3:f_0636): continuous wall of fabric
  round the bay.
- West window: one drape, drawn to the **west** side — bundle at (−0.52, 1.02) — same tie-back at z 1.15
  (v4:f_0027); closed it covers x −0.50 → 0.32.
- A cream cord with a small acorn pull hangs at the east end of each track (v4_f75).

## 8. Lighting and switches

| # | fitting | position | description |
|---|---|---|---|
| L1 | **Chandelier** | ceiling, centre (1.85, 2.70) ±0.3 | Empire-style crystal **basket ("bag") chandelier**: gilt-brass ring Ø 0.70 with strings of faceted crystal beads sweeping down to a smaller bottom ring and up to a crown, ≈ 0.55 deep, on a short gilt rod (top of fitting z 2.80, bottom 2.10); warm white lamps inside. On the plaster rose (v4:f_0023, f_0217, v4_f15). |
| L2 | **Downlights** ×8 | ceiling: main room (−0.10, 1.60) (1.90, 1.60) (3.60, 1.60) (−0.10, 4.10) (1.90, 4.10) (3.60, 4.10); bay (1.85, 0.55) (3.20, 0.55) | Recessed LED, white bezel Ø 90, neutral-warm ≈ 3000 K (v4_f11, v4_f21, v3_f524). Count 8 ± 2. |
| L3 | **Pineapple light N** | W-east, y 3.34, back-plate z 1.20 → 1.42 | Cast-brass rococo back-plate (leaf cartouche, 0.07 × 0.22), scrolled swan-neck arm projecting 0.20 and turning down to a pierced brass gallery Ø 0.11, with a **cut-glass "pineapple" shade** (diamond-cut, acorn shaped, Ø 0.10 × 0.14) hanging below it, bottom at z 1.05. Polished brass #B5943E (v3:f_0644–f_0652). |
| L4 | **Pineapple light S** | W-east, y 1.24, same heights | Identical. |
| L5 | **Wall sconce** | W-front pier, centre (0.70, 0.99), z 1.75 → 2.05 | Antique-brass three-arm sconce: oval fluted back-plate with a leaf drop, three S-scroll arms spanning 0.36, candle tubes with drip pans, three **cream fabric bell shades** with a braid edge (v4:f_0210–f_0216, v4_f11). |

Switches (white plastic; z = centre):

| plate | position | controls |
|---|---|---|
| S1 — **3-gang, three round rotary dimmers** on one plate | W-rear between the NW corner and door 1: x −0.50, z 1.20 (v3_f524, v4:f_0223, f_0242) | left → **chandelier L1**, middle → **downlights L2**, right → **wall sconce L5**. The owner works this plate on entering ("I'll turn on the light", v3:f_0506–f_0517) and again in v4:f_0212–f_0219 ("lights … lights"); the gang order is not narrated — assumption. |
| S2 — 1-gang rocker | W-east under L3: y 3.34, z 0.98 (v3:f_0574–f_0580) | **pineapple light N (L3)** |
| S3 — 3-gang rocker | W-east under L4: y 1.24, z 0.98 (v3:f_0646–f_0648, v4_f1) | gang 1 → **pineapple light S (L4)**; gangs 2–3 → two-way for chandelier and downlights (assumption) |
| S4 — flat 1-gang plate, wide rocker | W-rear, right of the sliding door: x 3.29, z 1.25, beside the a/c remote holder (v4:f_0102–f_0103) | **bathroom lights** ("turn on the light, this is the bathroom") — two-way with the plate on the landing |

Both pineapple lights are lit in v3:f_0520 and only the south one in v4:f_0001 / f_0021, so they do switch
separately.

## 9. Reference frames

| frames | shows | camera |
|---|---|---|
| v3:f_0496–f_0502 | the two steps up in the gallery, dado stepping (landing spec) | gallery, looking −Y and down |
| v3:f_0504–f_0510 | door 1 from the landing, its landing-side doorcase, both doors at the landing corner, brass threshold | landing, looking −Y |
| v3:f_0512–f_0518 | W-west: chest, TV edge, mirror; first view to the bay with curtains closed | just inside door 1 |
| v3:f_0520 (still) | W-east: bed, headboard, picture A1, both pineapple lights, blanket chest, closed curtains, east nib chamfer | (0.6, 2.6) looking +X |
| v3:f_0522 (still) | NE corner: small wardrobe, air-con, coat rail | (0.8, 2.0) looking NE |
| v3:f_0524, f_0526 (stills) | W-rear: door 1 open 95°, doorcase, S1, big wardrobe, cornice, two downlights | (1.3, 2.4) looking +Y |
| v3:f_0528–f_0536 | door 1 swinging; doorcase relief; mirror A2; S1 | near (0.3, 3.8) |
| v3:f_0538–f_0554 | sliding door closed, flush pull, S4, remote, coat rail, small wardrobe, air-con | (2.5, 3.2) looking +Y / NE |
| v3:f_0556–f_0560 | small wardrobe opened: shelf and hanging rail | at the wardrobe |
| v3:f_0562–f_0570 | air-con, spur plate, coat rail, doorcase pediment close-up, cornice enrichment | below, looking up |
| v3:f_0572–f_0590 | nightstand N from all sides, marble top, S2, socket behind | (3.6, 3.6) |
| v3:f_0592–f_0600 | bed wall; blanket chest closed then **lid opened** | (2.0, 3.2) looking SE |
| v3:f_0602–f_0610 | bureau: closed, **fall front opened** (interior), drawers; sconce L5 above; west window | (0.7, 2.2) looking −Y |
| v3:f_0612–f_0622 | chest of drawers, TV, tantalus, whisky glasses | (1.2, 2.4) looking −X |
| v3:f_0624–f_0632 | **west window opened**: handle, hinge side, slate roof, flag | at the window |
| v3:f_0636–f_0638 (still 636) | bay with curtains closed, pelmet, east nib chamfer stop, bay furniture | (1.0, 2.0) looking SE |
| v3:f_0640–f_0656 | nightstand S, **pineapple light** close-ups (lit), S3, picture A1 frame | at the bed's south side |
| v3:f_0660–f_0674 | armchair, **footstool pulled out** from under it | in the bay |
| v3:f_0676–f_0684 | octagonal table, radiator, corner chair | in the bay |
| v3:f_0686–f_0702 | curtain heading, pelmet, fabric close-ups (flat enough for a pattern reference) | in the bay, looking up |
| v4:f_0001–f_0007 (still 1) | east nib chamfer + stop, cheek window, tie-back, sill board | bay, looking east |
| v4:f_0011–f_0025 (stills 11, 15, 21, 25) | W-front with curtains open: west window, pier, sconce, bureau; whole bay; TV wall | room centre, looking −Y / −X |
| v4:f_0027–f_0034 | west window opened again | at the window |
| v4:f_0038–f_0041 | bay west cheek window ("cannot be opened") | in the bay |
| v4:f_0042–f_0053 | bay front **west casement** opened; cars below | in the bay |
| v4:f_0054–f_0066 | bay front **east casement** opened | in the bay |
| v4:f_0071–f_0077 (stills 71, 75) | radiator, sill, window framing, top-hung centre vent, pelmet from below | in the bay |
| v4:f_0079–f_0093 | both bay corners: chamfer, stop, cornice break ("smooth transition") | room, looking up / down |
| v4:f_0095–f_0104 (still 95) | W-rear frontal (best for measuring); **sliding door operated**; S4 pressed | (2.0, 2.6) looking +Y |
| v4:f_0203–f_0224 | mirror A2, S1, sconce lit, chandelier, big wardrobe, doorcase | around the room |
| v4:f_0227 | view out of door 1: gallery left, second-floor stair right, bathroom door at its foot | in the doorway |
| v4:f_0229–f_0241 (stills 230, 236, 238) | room overview from the rear; sliding door standing open; bay west corner from inside the bay | various |

## 10. Interactions (everything the owner opens, or says can open)

| object | motion | evidence |
|---|---|---|
| Door 1 | hinge east jamb (0.48, 4.73), swings south into the room 0 → 95° | v3:f_0504–f_0530 "double wooden door" |
| Sliding door | translates east 0 → 0.69 m into the pocket | v4:f_0096–f_0104 "you can slide open it" |
| Big wardrobe doors ×2 | side-hung on the outer stiles, 0 → 110°; show a rail of plain hanging garments | "wardrobe doors can open to see clothes" (said at the big one; shown on the small one) |
| Small wardrobe doors ×2 | side-hung on the outer stiles (north door on its north stile, south door on its south stile), 0 → 110°; shelf + hanging garments | v3:f_0556–f_0560 |
| Blanket chest lid | hinged along the back (east) edge, 0 → 75°; folded towels / linen inside | v3:f_0598–f_0600 |
| Bureau fall front | hinged along its bottom edge (z 0.78), drops forward 0 → 120° to horizontal, carried on two pull-out lopers | v3:f_0606–f_0610 "the bureau can also open and close" |
| Bureau drawers ×3 | slide north 0 → 0.25 | Phase-2 rule (drawers) |
| Chest of drawers | every drawer slides east 0 → 0.30 (several stand ajar in the video; model closed by default) | v3:f_0612–f_0618 |
| Nightstand drawers ×3 each | slide west 0 → 0.18 | Phase-2 rule |
| West window, lower casement | hinge west stile, outward 0 → 60° | v3:f_0624–f_0632, v4:f_0027–f_0034 |
| Bay front, west casement | hinge west stile, outward 0 → 60° | v4:f_0042–f_0053 |
| Bay front, east casement | hinge east stile, outward 0 → 60° | v4:f_0054–f_0066 |
| Bay west cheek window | **fixed — must not open** | v4:f_0033–f_0041 |
| Bay centre top vent, west-window top vent | top-hung, outward 0 → 20° (handles present, not operated) | optional |
| Bay curtains, west-window curtain | open (tied back) ↔ closed | v3:f_0685–f_0703, v4:f_0001–f_0010 "curtains all opened" |
| Footstool | slides out from under the armchair toward the room, 0 → 0.6 m | v3:f_0668–f_0674 |
| Lights | S1–S4 as §8; each pineapple light on its own switch | v3:f_0642–f_0650, v4:f_0212–f_0219 |
| Air-con, TV | no motion (TV screen stays blank) | — |

## Declutter (deliberately excluded)
Black folding massage-table case leaning on the big wardrobe; coats on the rail; everything loose on the chest
of drawers and nightstands (chargers, bottles, hair dryer, books, cables, extension leads on the floor);
clothing on the blanket chest; tissue box on the drum table; open drawers; smart speaker on the bureau.

## Doubts
1. **Ceiling 2.95** rests on door-leaf scale in three stills; 2.85–3.05 possible.
2. **Bay inner size** (2.74 × 0.85) assumes solid 0.255 m walls on the ground-floor outer faces; the inner
   width measured 2.74 at H = 2.95. If the front-elevation spec fixes the first-floor bay differently, keep
   the front-window frame centred and 2.06 wide, with 0.34 of wall each side.
3. **West window x position** ±0.08 (reveal −0.41 → 0.23, from the pier : window : gap proportions
   0.94 : 0.64 : 0.23); it is probably centred over the street doors (x ≈ 0) within that tolerance.
4. **Rear wall line** y 4.73 is the living-room north face carried up; the partition is drawn 0.14 thick
   (pocket door). ±0.10.
5. Bed size: king (1.50) inferred from a 1.64 m headboard; a super-king would not fit between the nightstands.
6. East bay cheek window assumed fixed like the west one. Top vents never operated.
7. Dimmer-gang order on S1, and what gangs 2–3 of S3 do, are assumptions.
8. Downlight count / positions (8 ± 2); chandelier centre ±0.3.
9. Nightstands are French Louis-XV-style bombé pieces; the owner calls them "Queen Anne" — modelled as seen.
10. Dark wall colour: samples swing from #344240 to #698871 with exposure; #3F6B5C is the estimate.
11. Radiator tube count (≈ 28) and exact model; "double wooden door" is read as the two oak doors either
    side of the big wardrobe (door 1 and the sliding door), not a pair of leaves in one opening.
12. Landing side: door 1 sits in the landing's south wall, the bathroom's hinged door in its east wall at the
    foot of the second-floor stair, with a 0.4 m return between them carrying two switch plates
    (v4:f_0266–f_0268) — `landing1` must agree.

## Reconciled dimensions (house.next.json)

Added by the phase-2 reconcile step. `spec/house.next.json` is canonical; where the text above differs, the values below win. Reasons and evidence: `spec/RECONCILE2.md` (decision ids in brackets).

- **Floor Z 3.42** (was 3.22): add +0.20 to every world Z derived from the floor [L2].
- **Ceiling 2.85 above the floor** (Z 6.27; was 2.95) [L3]: the loft floor above is at 6.49. Scale the top-of-wall
  items with it: cornice underside about 2.75, pelmet boxes underside about 2.68; door pediments (apex 2.60) and window
  heads (2.55 / 2.58) are unchanged.
- **Polygon**: (-0.65, 0.99) (1.16, 0.99) (1.16, 0.14) (3.90, 0.14) (3.90, 0.99) (4.30, 0.99) (4.30, **4.83**)
  (-0.65, **4.83**) — main room 4.95 x **3.84** (rear wall face was 4.73) [P7]. Rear partition y 4.83..4.95.
- **Transform**: items on or keyed to the rear wall +0.10 in y (door 1, big wardrobe, sliding door, small wardrobe →
  y 3.70..4.72, switch plates, tall mirror); everything keyed to the front wall, bay and bed is unchanged.
- **Cheek windows: frame y 0.19..0.67** (was 0.32..0.80) [P8], so they stay in front of the main wall face (y 0.74).
- Door 1 clear x -0.281..0.481; sliding door clear x 2.34..3.03 (unchanged).
- East wall is external (side alley), not a party wall [E3].
- World heights for the elevation: bay sill Z 4.12, heads 5.97; west window Z 4.20..6.00.
- **Bay corners** [verification V1]: feature `green_bay` (x 1.16..3.90, y 0.14..0.99) now carries the two chamfers of
  section 3.2 — corners (1.16, 0.99) and (3.90, 0.99), face 0.12, world Z 3.42..5.72, quarter-round stop to 5.82, square
  above. They were missing from `house.next.json`, which would have built square nibs.

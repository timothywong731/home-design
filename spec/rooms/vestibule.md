# Vestibule / porch (`vestibule`) — visual / dimensional specification

Source frames: f_0001–f_0047, f_0055–f_0061, f_0795–f_0797 (all viewed), plus full-res stills in
`reference/work/hall/full/` (F_0012–F_0031, F_0057). Owner narration (authoritative): "this is the porch…
front door… two windows here on top, there's an arch… beautiful floor tiles… light switch… wooden door
frame in red colour… doors can open and close".

Colours: "sampled" = median sRGB of a clean patch under the warm LED/HDR video; "true" = neutral-light
estimate. **Use the "true" value.** Tolerance on dimensions ±5 % unless flagged.

Viewpoint convention: **"standing with your back to the front (street) door, looking into the house"** =
facing +Y. From there: left = -X (west, party-wall side), right = +X (east, living-room side), ahead = the
mahogany inner doors.

---

## 1. Shape & dimensions

### Room-local frame (identical to the BRIEF world frame)
- Origin = centre of the inside face of the front-door threshold, at tile level. +x = house right (east),
  +y = into the house (north/rear), z up. Tile floor is z = 0, level with the hall oak (flush threshold).
- You enter by the front doors in the wall y = 0. The wall facing the street is y = 0 (-Y); the inner
  doors are at y = 1.73 (+Y); left wall x = -0.65 (-X, party wall); right wall x = +0.65 (+X, backs onto
  the living-room bay).

### Plan (three zones front to back; symmetrical about x = 0)
| zone | y range | clear width | x range | ceiling |
|---|---|---|---|---|
| Recess B (front, by the street door) | 0.00 → 0.74 | 1.30 (1.55 in `house.json`: east side runs to x +0.90, see Reconciled dimensions) | -0.65 → +0.65 | flat, 2.85 |
| Arch zone between two piers | 0.74 → 1.29 | 1.10 | -0.55 → +0.55 | barrel vault, springing 2.43, crown 2.66 |
| Recess A (by the inner doors) | 1.29 → 1.73 | 1.30 | -0.65 → +0.65 | flat, 2.85 |
| Inner door frame (mahogany) | 1.73 → 1.83 | — | wall to wall | — |

- **Overall inside size 1.30 m wide x 1.73 m deep.**
- **Piers:** one on each side wall, **0.55 m long (y 0.74 → 1.29) x 0.10 m proud**, square arrises,
  rising to moulded imposts that carry the arch. Dado rail and skirting return around them.
- How the numbers were obtained:
  - Width: the inner door pair is wall to wall. In the near-frontal still F_0057 each leaf measures
    322 x 1052 px → w/h 0.306 → **610 x 1981 mm leaves** (standard 2'0" pair); the frame outer width is
    690 px on the same scale → 1.30 m. Floor-tile count across recess A gives 11.5–12 cells x 0.110 m
    = 1.27–1.32 m: the two agree.
  - Depth: 16 tile-cell rows between the two thresholds along the west wall (F_0013, F_0014, F_0029):
    7 rows in recess B (the last one cut to ~0.7), 5 rows beside the pier, 4 rows in recess A
    → 15.7 x 0.110 = 1.73 m.
  - Heights: scaled from the 1.981 m leaf in F_0057 (531 px/m): inner frame top 2.83 m, dado top 0.965 m.
- No steps. Tiles finish flush against a dark hardwood sill under the inner doors and against the white
  uPVC threshold of the street door (≈ 30 mm upstand, part of the door frame).

---

## 2. Openings

### 2.1 Street doors (wall y = 0) — outside ↔ vestibule
- White uPVC/composite **double door with a full-width transom light**, set in a white frame that fills the
  wall: frame outer 1.24 m wide (x -0.62 → +0.62) x 2.57 m high; ≈ 30 mm of painted reveal each side.
- Vertical build-up: threshold 0–0.03; leaves 0.03–2.03; head/transom bar 2.03–2.12 (two small white
  trickle-vent hoods 110 x 25 mm on the head, one over each leaf, 0.12 m from the meeting stile);
  **transom light 2.12–2.50: one pane 1.10 x 0.38 m of acid-etched frosted glass**; top frame 2.50–2.57.
  **Privacy: the real glass carries the address lettering — model plain frosted glass, no text.**
- **Leaves:** two equal leaves 0.59 m wide. Each: 70 mm white stiles/top rail; **upper glazed panel**
  0.44 x 1.00 m (z 0.95 → 1.95) divided by white integral Georgian bars (18 mm) into **3 columns x 4 rows**
  of panes ≈ 0.135 x 0.235 m, glass = obscure "stippled" texture, reads black at night; **mid rail**
  z 0.86–0.95; **lower solid panel** 0.44 x 0.68 m (z 0.16 → 0.84) with a planted rectangular bolection
  moulding 35 mm in from its edge; bottom rail to z 0.16.
- **Letterbox:** polished brass/gold flap 0.30 x 0.075 m, centred on the mid rail (centre z 0.90) of the
  **-X (west) leaf** — the right-hand leaf when you stand inside the vestibule looking out at the street
  doors, the left-hand leaf seen from the street (f_0012–f_0016; `layout.md` says "east" — see §10).
- **Handles:** gold/brass lever on a slim 240 x 30 mm backplate on each leaf, 60 mm from the meeting
  edge, lever axis 1.02 m above floor, levers pointing away from the meeting stile. Cylinder under the
  lever on the west leaf.
- Hinges on the outer edges (white flag hinges, 3 per leaf). Never opened in the video; assume both
  leaves **open inward**; model closed.
- Colour: sampled #acab99 (in shade), true **#F4F4F0**, satin plastic.

### 2.2 Inner doors + fanlight (frame y 1.73 → 1.83) — vestibule ↔ hallway
"Wooden door frame in red colour" — **dark red-brown mahogany, gloss varnish**, sampled #30251f / #1e1818
(night shots crush it), true **#4A2216** with redder highlights #6B3020. Same on both faces.
- **Frame** wall to wall, 1.30 m wide x 2.83 m high (top just under the hall cornice), 100 mm deep:
  jambs 58 mm face; **transom bar** z 2.01 → 2.07 (58 mm); head 75 mm. A 20 mm stepped bead runs round the
  outer edge on the hall face. Sill: 100 mm wide flush mahogany strip.
- **Fanlight:** one fixed sheet of **clear glass 1.14 x 0.72 m** (z 2.07 → 2.79), 12 mm glazing beads.
- **Leaves:** pair, each **610 x 1981 x 40 mm**, 2 x 5 = **10 clear bevelled panes** per leaf.
  Stiles: hanging stile 120 mm, meeting stile 98 mm; bottom rail 215 mm; top rail 125 mm at the sides,
  its underside cut to a **shallow segmental arch** (rise 20 mm) spanning both top panes; one vertical
  glazing bar 32 mm, four horizontal bars 36 mm, all ovolo-moulded. Panes ≈ 180 wide x 300 high; glass
  bevel 10 mm.
- **Hinges:** three 100 mm polished-brass butts per leaf at z 0.22, 1.00, 1.77, **on the wall-side
  stiles**. **Both leaves swing north into the hallway.** In the video the west (-X) leaf stands open
  ≈ 85° against the hall's west wall while the east leaf is mostly shut (f_0037–f_0045). Model the west
  leaf open 85°, east leaf closed.
- **Furniture:** polished-brass lever handles on **long shaped ("Georgian"/scalloped-end) backplates
  50 x 270 mm**, one on each leaf both faces, 30 mm from the meeting edge, lever axis z 0.98; keyhole below
  the lever on the east leaf. Scroll-end levers 115 mm long pointing away from the meeting stile. Two
  small round brass flush-bolt knobs (Ø 20 mm) on the bottom rails, z 0.12, 35 mm from the meeting edge.

### 2.3 Side window (recess B east wall; x = +0.65 here, +0.90 in `house.json`) — vestibule ↔ living-room bay return light
This is the back of the living-room bay's west return window (see `living.md` §2.3 for the room side).
Seen from the vestibule it is **two separate white-architraved lights, one above the other**, centred at
y = 0.37:
- **Lower light:** glass 0.50 wide x 1.18 high, z 0.62 → 1.80, clear glass with the living room's **white
  plantation shutter (closed louvres)** immediately behind it — reads as pale grey horizontal slats.
- **Upper light (fanlight):** glass 0.50 wide x 0.68 high, z 1.97 → 2.65, clear glass, shows the pink
  living-room wall and tartan curtain edge beyond.
- Each light has its own mitred **white gloss architrave 75 mm wide** (two fascias + ogee outer edge,
  ≈ 20 mm thick) and a 25 mm white inner lining; a 0.17 m band of white wall separates the two
  architraves. The dado rail and grey paint stop against the lower light's architrave.
- West wall (x = -0.65) has **no window** — plain wall.

### 2.4 Arch between the piers
- Three-centred ("basket") **barrel vault 0.55 m deep** spanning 1.10 m: quarter-round haunches of radius
  0.23 m rising from z 2.43 to a flat crown at z 2.66. Plain white plaster soffit.
- **Imposts:** a moulded plaster band z 2.20 → 2.43 wrapping three faces of each pier (north, inner,
  south): from the bottom a 12 mm astragal bead, 95 mm plain necking, 15 mm fillet, 60 mm cyma/ovolo
  swelling out, 45 mm square abacus on top; overall projection 50 mm beyond the pier face.
- **Archivolt:** on both the north and south faces a flat raised band 120 mm wide x 15 mm proud with a
  12 mm bead on its outer edge follows the arch outline from impost to impost. Above it plain wall up
  to the ceiling (≈ 0.19 m at the crown).

---

## 3. Surfaces

### Walls (all four, both recesses and the piers)
| element | sampled | true | notes |
|---|---|---|---|
| Above dado — white, matt emulsion | #e4e2d5 (f_0033), #cbc7be | **#F2F0EA** | includes the vault, imposts' background wall, ceilings |
| Below dado — light warm grey, matt | #ada892 (f_0033), #888373 | **#C8C5BB** (first estimate #B9B5A8 rendered a khaki band; lightened after the shell review, f_0770 lower/upper ≈ 0.78; `M.PAINT['hall_dado_grey']`) | same paint as the hallway dado |
| Dado rail, skirting, architraves — white gloss | #e4e3e0 | **#F4F2EC** | |

- **Dado rail:** top edge at **z = 0.965**, 70 mm high x 30 mm projection: 12 mm square top fillet,
  28 mm half-round torus, 6 mm quirk, 20 mm cavetto, 4 mm bottom fillet. Runs on the west wall, the east
  wall and both piers (returning round each pier with mitred external/internal corners), stops against
  the street-door frame, the inner-door frame and the lower window architrave. Not on the door walls.
- **Skirting:** 200 mm high x 22 mm: 140 mm plain board with a 60 mm moulded top (small step, ogee,
  10 mm top bead). Follows the piers like the dado.
- **No cornice** in the vestibule: walls meet the flat ceilings square (the owner's "cornice… spotlights"
  remark at f_0053–f_0060 is spoken while looking up at the hallway ceiling through the fanlight).
- **Ceilings:** flat white plaster at 2.85 in both recesses, sampled #9c988d in shade, true **#F4F3EE**.

### Floor — Victorian-style geometric porcelain tiles
- Printed matt porcelain tiles **331 x 331 mm** laid square to the walls (not diagonal), 2 mm light-grey
  grout (#C9C7C0). Each tile carries a 3 x 3 grid of **110 mm cells** with thin printed "joints"
  (1.5 mm, light grey) between every shape, so the floor reads as small individual pieces.
- **Pattern, by cell** (cell size c = 0.110 m; i counts cells toward +x, j toward +y; the pattern repeats
  every 3 cells both ways):

  | (i mod 3, j mod 3) | cell |
  |---|---|
  | (0, 0) | **U** — solid dusty blue-grey square |
  | (1, 1) (2, 1) (1, 2) (2, 2) | **K** — solid charcoal-black squares (a 2 x 2 black block) |
  | (1, 0) (2, 0) (0, 1) (0, 2) | **X** — square cut by both diagonals into four triangles |

  X-cell colouring: the triangle whose base touches a blue **U** square is **tan**; the opposite triangle
  is **black**; the two side triangles (touching K squares) are **white**. So every blue square has four
  tan triangles pointing away from it; the black triangles of two neighbouring X cells meet base to base
  and form a black diamond midway between blue squares; and each 2 x 2 black block is ringed by white
  triangles. (Each triangle has its base on a cell edge and its apex at the cell centre.) The physical 331 mm tile is the 3 x 3 block K-X-K / X-U-X / K-X-K (blue in the middle).
- **Registration:** blue squares are centred at x = -0.375, -0.045, +0.285, +0.615 and at
  y = 1.675, 1.345, 1.015, 0.685, 0.355, 0.025 (the row at the street threshold is cut to ≈ 0.08 m; the
  row at the inner sill is a full cell; the column against the west wall is an X/K column).
- Colours (k-means on F_0030, lit by the chandelier):

  | piece | sampled | true |
  |---|---|---|
  | black | #42403c | **#2E2E30** |
  | white | #d2cfc7 | **#EDEBE4** |
  | tan / mocha | #a89884, #b3a598 | **#A58F78** |
  | blue-grey | #abb0b6 | **#97A3AE** |

  Roughness ≈ 0.45 (soft sheen under the chandelier), flat surface, no relief.
- Threshold strips: mahogany sill of the inner frame (100 mm, flush, #4A2216); white uPVC sill at the
  street door.

---

## 4. Fixed fittings
Looking into the house from the street door; "east wall" = right-hand wall.

| item | position | description |
|---|---|---|
| Alarm keypad | east wall, recess A, centre (x 0.65, y 1.52, z 1.48) | white plastic box 150 W x 100 H x 22 D mm, numeric keypad left + round dial/button right, mounted landscape (f_0033, f_0034) |
| Light switch | east wall, directly below the keypad, centre z 1.22, y 1.52 | white plastic 1-gang rocker, 86 x 86 mm |
| Street-door trickle vents | on the door head | see §2.1 |

No radiator, no sockets seen.

---

## 5. Furniture

| item | position | size (W x D x H) | description |
|---|---|---|---|
| **Upholstered box stool** (sewing/piano stool) | recess A, pushed into the corner made by the east wall and the inner-door frame: footprint x 0.21 → 0.63, y 1.33 → 1.69 | 0.42 (E–W) x 0.36 (N–S) x 0.50 | Dark mahogany (#3B2418, satin) box 0.20 m deep on four square tapered legs 0.26 m high (35 mm at top → 22 mm at the foot). The west face has **two shallow drawers** one above the other, each with two small dark-bronze swan-neck drop handles. Lift-up padded lid 60 mm thick overhanging 10 mm, covered in **champagne crushed velvet**, sampled #c2b896, true **#D3C6A6**, strong sheen with mottled pile (f_0026, f_0031, f_0032). |

---

## 6. Soft furnishings & decor

| item | position | size | description / texture source |
|---|---|---|---|
| **Door rug** (flat-woven cotton, kilim style) | long axis N–S; covers x -0.43 → +0.19, y 0.08 → 1.06 (west edge two tile cells off the west recess wall, passes in front of the pier) | 0.62 x 0.98 m, 6 mm thick, rounded corners | Cream chunky-woven ground (true #E5DFCC). Down the centre a column of **three mustard elongated hexagons** (true #B89A45), each with a cream lozenge centre sprinkled with small taupe cross-dots; the hexagons are linked by **taupe X / chevron bands** (true #8A7860) whose arms enclose cream dotted panels; grey-brown plain triangles fill the long edges (true #7C7468). Sampled: mustard #9e8f59, taupe #746747, cream #b1ab90. Best frames for a rectified crop: **f_0027, f_0028** (camera looking straight down; feet and a bag cover the south-east quarter — mirror the clean half) and F_0013 / f_0014 for the street end. Approx. rug outline in f_0028 (720 x 1280): (15, 600) (215, 485) (625, 880) (305, 1230). |

No pictures, mirrors or plants in the vestibule.

---

## 7. Lighting

| fitting | position | description |
|---|---|---|
| **Brass hall-lantern chandelier** | recess A, on the ceiling centre (x 0, y 1.48); ceiling plate at z 2.85, lowest point z 2.16 | Polished brass (#C9A44C, gloss). Ceiling cup Ø 120 mm with gadrooned edge → 150 mm of chain (3 links) → **hexagonal lantern cage** Ø 0.20 x 0.36 m high: six clear bevelled glass panels in slim brass glazing bars, a crown of six small urn finials round the top, three candle lamps inside; from the cage's base ring **six S-scroll arms** sweep out and up to Ø 0.47 m, each ending in a dished brass drip pan and an ivory candle sleeve (25 x 90 mm) with a clear flame-tip LED; turned pendant finial under the cage. 9 lamps, **2700 K**, bright. Overall 0.47 Ø x 0.69 m drop (F_0057, f_0022, f_0023, f_0036). |
| **Recessed downlight** | recess B ceiling, (x +0.20, y 0.35) | white bezel Ø 85 mm, flush; off in the video (f_0012, f_0021). 3000 K. |
| **Outside lights** ("got the lights outside") | external porch canopy just outside and above the street door | Seen through the transom in the full-res still t=15 (f_0016), f_0012, f_0014: a **white uPVC-boarded canopy soffit** (board joints parallel to the door, underside ≈ z 2.65, projecting ≈ 0.8 m) holding **3 recessed downlights** (white bezel Ø ≈ 90 mm) in one row parallel to the door at x ≈ -0.38, 0, +0.38, ≈ 0.4 m out from the door face, 3000 K. They should read as soft discs / glow through the plain frosted transom. Heights and spacing are estimates from one oblique view. The transom stays plain frosted, no lettering. |

---

## 8. Declutter list (deliberately excluded)
Coats and bags hung over the east window and wall hooks, the pine shoe rack and all shoes/boots/crocs
along the east wall, umbrellas, loose packaging and the leaflet on the rug, the cabin-hook hardware noise
on the tiles, the owner's feet/hand. The address lettering on the transom glass (privacy).

---

## 9. Reference frames

| frame | shows | camera |
|---|---|---|
| f_0012 | street doors, transom, west wall with dado stepping round the pier, rug | in the inner doorway, ≈ (0.2, 1.7, 1.6) looking -Y, slightly down |
| f_0016 | street doors square-on: glazing bars, handles, letterbox, vents | recess A, ≈ (0, 1.4, 1.6) looking -Y |
| f_0019 | east side window (upper light + shuttered lower light), east impost | ≈ (-0.2, 0.9, 1.6) looking +X, tilted up |
| f_0021 / f_0022 | vault, archivolt, east impost, chandelier, inner doors + fanlight from inside | recess B, ≈ (0, 0.3, 1.5) looking +Y, tilted up 35° |
| f_0026 | whole floor looking north: tile pattern, west pier skirting, stool, inner sill | ≈ (-0.3, 0.5, 1.6) looking +Y, tilted down 45° |
| f_0029 / f_0030 | tile pattern close-up at the inner sill and the west pier corner | ≈ (-0.2, 1.1, 1.5) looking down |
| f_0033 | keypad + switch, dado, stool top | ≈ (0, 1.2, 1.5) looking +X |
| f_0057 | inner doors + fanlight square-on from the hall, vault and chandelier through the glass | hallway ≈ (0, 3.3, 1.75) looking -Y |
| f_0044 | inner doors from the vestibule with the west leaf open, stool, sill | ≈ (0, 0.9, 1.6) looking +Y |

---

## 10. Uncertainties
1. **Width 1.30 m vs `layout.md` 1.45 m.** My figure comes from the leaf aspect ratio in a frontal still
   and an independent tile count; if `house.json` keeps 1.45, scale x by 1.115 and keep the tile cell at
   0.110 (the pattern then just shows more columns).
2. **Ceilings.** The two recess ceilings are taken as flat at 2.85; the vault crown (2.66) and springing
   (2.43) are ±0.08. It is possible recess A's ceiling is 50–100 mm lower than recess B's.
3. **Tile module** assumed to be the common 331 mm tile (110 mm cells); real size could be 316–345 mm.
4. **Letterbox leaf:** frames show it on the -X leaf; `layout.md` §3 says east. Trust the frames.
5. **Street-door swing** and exact leaf/frame sizes (never opened; partly hidden by coats) — inward assumed.
6. **East pier** is hidden by coats below 2 m; assumed to mirror the west pier (its impost is visible).
7. **Side-window glass sizes** are taken from `living.md` (same window); the vestibule-side architraves
   were measured only by proportion.
8. Stool drawer face orientation (west vs south) is a best reading of f_0031/f_0032.
9. Rug pattern is described from oblique, partly covered views; a rectified crop will be approximate.

---

## Reconciled dimensions (from `spec/house.json`, see `spec/RECONCILE.md`)
- Global: x -0.65..0.65, y 0..1.73 (1.30 x 1.73) **plus recess B widened on the east to x 0.90**
  (polygon (-0.65,0) (0.90,0) (0.90,0.74) (0.65,0.74) (0.65,1.73) (-0.65,1.73)). Ceiling 2.85 flat, vault
  between the piers.
- Local to global: identity. Only the east wall of recess B moves (verification round): it is the bay's
  west cheek `w_bay_cheek_w`, a **thin 0.20 window wall with faces x 0.90 / 1.10** — the shutter louvres
  sit directly behind the glass (stills t=18, 19), so the wall cannot be 0.45 thick. The side window
  (§2.3) is therefore on x = 0.90, centre y 0.37; dado, skirting and cornice of recess B follow that wall.
  The front wall returns 0.28 east of the street-door frame, and the east pier stands 0.35 proud of the
  recess-B wall (0.10 proud of the recess-A wall, as specified). The recess-B downlight at x +0.20 is then
  near the recess centre (x 0.125). **Owner check:** coats hide this corner in every frame.
- Behind recess A and the pier is the living room's west wall (living front line y = 0.99).
- The inner screen is `w_screen_inner` (y 1.73..1.83); the hall starts at y = 1.83.

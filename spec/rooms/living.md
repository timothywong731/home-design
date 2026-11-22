# Living room (`living`) — visual / dimensional specification

Source frames: f_0087–f_0233, f_0783–f_0793 (room) and f_0073–f_0086 (pedimented surround, hall side).
Cross-checked against `reference/transcript.txt` in the verification round: all owner-named items are
present. All dimensions are estimates from reference objects (door leaf 762 x 1981,
85" TV 1.89 x 1.06 m, Daikin floor console 750 x 600 mm, UK socket 146 x 86 mm); tolerance about ±5 % unless
flagged. Colours: "sampled" = median sRGB of a clean patch under the warm LED/HDR video; "true" = my
neutral-daylight estimate. **Use the "true" value for materials.**

Viewpoint convention used throughout: **"standing in the doorway from the hall looking in"** = facing +X
(house right). From there: **left = rear wall (+Y)**, **ahead = party wall (+X)**, **right = bay window /
street (-Y)**, **behind = hall wall (-X, terracotta)**.

---

## 1. Shape & dimensions

### Room-local frame
- Axes parallel to the world axes of the BRIEF (local +x = world +X = house right; local +y = world +Y =
  toward the rear of the house; z up, z = 0 at finished floor, same level as the hallway oak floor — no
  step at the threshold).
- **Local origin = inside floor corner where the hall wall (-X wall, terracotta) meets the front wall
  line** (the room-side face of the two front-wall nibs that flank the bay).
- Main rectangle: x 0 → 3.60, y 0 → 3.80. Bay window projects to y = -0.85.
- The entry door is in the wall x = 0, at the far-rear end (y 2.77 → 3.55). So the door centre is at
  local (0, 3.16); in the hallway this is on the right-hand wall as you walk in from the front door,
  immediately before the foot of the stairs.

### Walls
| wall | plane | faces | length | finish |
|---|---|---|---|---|
| W (hall wall, "TV wall") | x = 0, y 0→3.80 | house left (-X) / hallway | 3.80 m | terracotta, full height |
| N (rear wall, "bookcase wall") | y = 3.80, x 0→3.60 | house rear (+Y) | 3.60 m | pale pink |
| E (party wall, "sofa wall") | x = 3.60, y 0→3.80 | house right (+X) | 3.80 m | pale pink |
| S (front wall) | y = 0 | house front (-Y) / street | two nibs 0.35 m each + 2.90 m bay opening | pale pink nibs |

- **Ceiling height 3.05 m** (flat, same in the bay). Reasoning: on the TV wall the door opening (2.00 m)
  scales the floor-to-cornice height to 2.95–3.07 m in f_0097 / f_0793 (near-level camera), plus cornice;
  the hall side gives 3.0–3.05 m by summing the overdoor. Defer to `spec/house.json` if it differs.
- Derivation of plan: TV wall solved by cross-ratio in f_0099 using TV width 1.89 m and door
  architrave-to-architrave 0.98 m → corner-to-corner 3.78 m. Width from f_0791: bay opening 2.9 m + nibs
  0.34 m each (focal-length/scale argument, calibrated on the 0.62 m lamp table and window lights) → 3.6 m.
- No chimney breast, no alcoves, no dado rail in this room. Wall between room and hall ≈ 0.15 m thick
  (depth of door lining).

### Bay window (square bay, front)
- Plan: rectangle x 0.35 → 3.25 (2.90 m wide inside), y 0 → -0.85 (0.85 m deep). Corners are 90°.
- Flanked by two **front-wall nibs (piers)**: west nib x 0→0.35, east nib x 3.25→3.60, both at y = 0,
  nib wall thickness ≈ 0.30 m (so the bay return walls start at the nib's bay-side face).
- The bay opening is full height — **no downstand beam**; ceiling and cornice run continuously into the bay.
- Each nib has its room-side/bay-side arris **chamfered** (45° chamfer ≈ 70 mm wide) from the top of the
  skirting up to z ≈ 2.25 m, where it finishes in a small **pointed "lamb's-tongue"/ogee chamfer stop**
  (reads as a little gothic-arch notch, ≈ 70 wide x 110 high); above the stop the arris is square. The
  skirting follows the chamfer as a 3-facet return (f_0226, f_0137, f_0211–213).
- Below the window sill the bay walls are plain plastered pink dado, z 0.17 → 0.53, with skirting.

---

## 2. Openings

### 2.1 Door D1 — hallway ↔ living room
- Wall W (x = 0). Structural/clear opening y 2.77 → 3.55 (0.78 m), head at z = 2.00. Architrave outer edge
  is 0.15 m from the rear (N) wall corner. Connects to the hallway (verified: camera walks through it in
  f_0086→0087 and f_0233→0235; hall console table, gilt mirror and dado are visible through it).
- **Leaf:** 762 x 1981 x 35 mm, **natural oak veneer, clear lacquer (satin)**, traditional **4-panel
  "Victorian" pattern**: two tall panels above (≈ 1.02 m high), two short panels below (≈ 0.48 m high),
  panels raised-and-fielded with a small bolection/ovolo bead. Stiles ≈ 100 mm, top rail ≈ 100, lock rail
  ≈ 190 (centre ≈ 0.95 m above floor), bottom rail ≈ 215, centre muntin ≈ 100. Oak colour sampled
  #927554 / #a48a56, true **#B08A56** (golden oak), stile slightly darker #9A7648. Vertical cathedral
  grain on stiles/panels, horizontal on rails.
- **Hinges:** on the **+Y (rear) jamb** — i.e. on the **left** jamb seen from the hall, **right** jamb seen
  from inside the room looking at the door. **Opens into the living room**, swinging back toward the rear
  wall. In the video it stands open ≈ 95°, lying parallel to and ≈ 0.12 m off the rear wall. Model it open
  at 95°. Three polished-brass butt hinges 100 mm (centres ≈ 0.20, 0.99, 1.75 m above floor).
- **Handle:** polished-brass lever on a rectangular brass latch backplate (≈ 45 x 150 mm, scroll-shaped
  "Victorian" lever ≈ 110 mm long), both faces, lever axis 1.00 m above floor, 60 mm from the leaf edge.
  No visible keyhole/escutcheon.
- **Lining/stop:** white gloss, lining depth ≈ 0.15 m, planted 12 mm stop.
- **Room-side architrave** (terracotta wall): white gloss, ≈ 100 mm wide x 25 mm thick, mitred, classical
  stepped profile from the opening outward: 8 mm bead/quirk, 30 mm flat fascia, 5 mm step, 30 mm flat
  fascia, then a 25 mm ogee (cyma reversa) rising to an 8 mm outer fillet. No plinth blocks; the skirting
  butts the architrave. No overdoor on the room side (a wall sconce sits above it — see §7).
- No transom/fanlight. Threshold: oak boards run straight through the opening with no threshold strip
  (same floor finish and level both sides).

### 2.2 Pedimented door surround — HALL side of D1
Everything is **white gloss paint** (noticeably shinier than the wall; sampled #dcd9d2, true **#F4F2EC**),
timber/plaster. It reads as a classical "broken (open) pediment" doorcase. Symmetric about the door
centre line. Dimensions below use the door centre as u = 0 (u along the hall wall), z from hall floor.
Scale derived in f_0082 from the half-opening (381 mm = 303 px).

Bottom to top:
1. **Architrave** — same 100 mm stepped profile as the room side (two fascias + ogee + fillet), mitred;
   opening edges at u = ±0.39, outer edges at u = ±0.49; head outer top at z = 2.10.
2. **Bed moulding** directly on top of the head architrave: 55 mm high cyma-recta + fillet, projecting
   ≈ 35 mm, spanning only between the corbels (u ±0.51). z 2.10 → 2.155.
3. **Plain flat band** (lower frieze) 70 mm high, flush with the wall-plate, between the corbels.
   z 2.155 → 2.225.
4. **Corbels (consoles)** — one each side, just outside the architrave: inner face at u = ±0.51, each
   **100 wide x 160 high x 75 projection** (tapering to ≈ 45 mm projection at the foot), z 2.065 → 2.225.
   Design: cast acanthus scroll bracket — rectangular top; body with a raised **oval cabochon/bead in the
   centre framed by two inward-curling acanthus leaves**, a small pendant husk below, finishing in a
   **three-lobed gadrooned (scalloped shell) foot**. Best views f_0078, f_0079, f_0081 (right-hand corbel),
   f_0084 (left-hand corbel, side-lit).
5. **Lower cornice shelf** sitting on the corbels and running the full width: 60 mm high (30 mm cavetto
   under a 30 mm square-edged shelf with small top bead), projecting ≈ 75 mm, ends returned to the wall;
   overall u = ±0.615 (1.23 m long). z 2.225 → 2.285.
6. **Main frieze** 110 mm high, z 2.285 → 2.395, plain flat, **breaking forward ≈ 25 mm at each end**:
   recessed centre section u -0.27 → +0.27, projecting end blocks u ±0.27 → ±0.595 (each ≈ 0.325 m wide,
   standing over the corbels). The vertical step is clearly visible in f_0081/f_0082.
   - **Applied ornament** centred on the recessed frieze: 350 wide x 75 high x ≈ 10 mm relief — a central
     **scallop shell / fan (≈ 70 mm)** flanked symmetrically by **foliate C-scrolls** tapering to leafy
     tendrils (f_0082 best; also f_0078).
7. **Pediment base cornice** (horizontal): 70 mm high cyma-recta-over-fascia profile, projecting ≈ 70 mm,
   following the same break-front (steps forward over the end blocks), ends returned; overall u = ±0.595
   at the bed, ±0.66 at the nose. z 2.395 → 2.465.
8. **Broken pediment** on top of the base cornice:
   - Two **raking cornices**, pitch ≈ 27°, same profile as the base cornice (≈ 90 mm deep measured square
     to the rake, 70 mm projection), each rising from the outer end (u = ±0.60, z 2.465) inward and
     **stopping at u = ±0.185** (top edge there at z ≈ 2.71), cut plumb with the moulding returned on the
     cut end. The open gap between the two inner ends is ≈ 0.37 m.
   - **Tympanum backboards**: flat 18 mm board behind/below each raking cornice, filling the triangle
     between rake and base cornice, whose inner end is cut to a **concave quarter-circle sweep (radius
     ≈ 90 mm)** curving down from the raking cornice's inner end to the base cornice (see f_0082 at the
     right raking piece, f_0084/f_0085 at the left).
   - **Central pedestal block** standing on the base cornice in the gap (intended for an urn/bust — it is
     empty): body an **inverted trapezoid** 105 mm wide at the bottom widening to 140 mm at the top, 100 mm
     high, 60 mm deep; crowned by a **3-step moulded cap** 205 mm wide x 40 mm high (fillet, cavetto,
     fillet), projecting ≈ 80 mm. z 2.465 → 2.605.
- Highest point of the surround z ≈ 2.71; ≈ 0.12 m of plain wall remains below the hallway's modillion
  cornice. Overall width 1.32 m (raking noses).
- The surround's rear (+Y) end is only ≈ 0.15 m from a wall return/corner in the hallway (f_0084); the
  front (-Y) end has a framed painting ≈ 0.12 m beyond the corbel and a 3-gang white light switch below
  that painting (hallway spec owns those).

### 2.3 Bay window W1 (front, street side)
Mock-Tudor style: **heavy dark-brown stained timber frame** (posts, mullions, transom, head, sill) with
**white uPVC double-glazed lights** set into each compartment, and **white plantation shutters** fitted
inside every lower light. Upper lights are left unshuttered.

- **Front (y = -0.85), 4 equal lights** between x 0.35 and 3.25:
  corner post 0.12 | light 0.54 | mullion 0.15 | light 0.54 | mullion 0.15 | light 0.54 | mullion 0.15 |
  light 0.54 | corner post 0.12 (sum 2.85; share the 0.05 slack into the posts).
- **Each side return (x = 0.35 and x = 3.25), 1 light**: jamb post 0.175 | light 0.50 | corner post 0.175.
- **Vertical build-up** (all six lights identical):
  - z 0.17–0.53 pink plaster dado under the sill
  - z 0.53–0.62 **sill / window board**: dark timber, 90 mm deep moulded front (ovolo–fillet–cavetto
    apron), projecting ≈ 60 mm into the room, continuous round the bay
  - z 0.62–1.80 **lower lights** (1.18 m): white uPVC casement frame (≈ 55 mm sightline) — fully covered
    on the room side by a shutter panel
  - z 1.80–1.93 **transom**, dark timber 0.13 m, flat with small chamfers
  - z 1.93–2.70 **fanlights** (0.77 m): white uPVC, clear glass, no shutters. On the front, the two
    **outer** fanlights and both return fanlights are top-hung openers (white frame-within-frame, white
    stay/handle at the bottom rail); the two centre fanlights are fixed.
  - z 2.70–2.90 dark timber head, cornice directly above.
  - Dark timber sections are ≈ 110 mm deep (room side stands ≈ 60 mm proud of the uPVC), plain square
    with slightly eased arrises, visibly brush-stained with grain.
- **Shutters:** one white hinged panel per lower light (6 panels), full-height of the lower light. Each:
  50 mm stiles, 90 mm top/bottom rails, no mid-rail, **≈ 17 elliptical louvres, 63 mm blade (≈ 60 mm
  pitch)**, shown tilted nearly closed (blades sloping down toward the room); hidden tilt rod. Mounted in
  a slim white L-frame (≈ 30 mm) fixed to the dark timber. Small **polished-brass lever catch** on the
  closing stile of the two outer front panels and the return panels, ≈ 0.95 m above floor.
- Glass shows black night sky with interior reflections — model as clear glass with a dark exterior.
- Colours: timber sampled #46362b / #3f342d, true **#3A2A20** (dark walnut/"Jacobean oak" stain, satin);
  uPVC/shutters sampled #dedcd6, true **#F5F4F0** (shutters satin).

---

## 3. Surfaces

### Wall paint (matt emulsion, smooth plaster, no dado rail, no panelling)
| surface | sampled sRGB (frames) | true estimate |
|---|---|---|
| W wall (hall wall, whole wall floor-to-cornice incl. above the door) — **terracotta / red-earth** | #9f6f5f, #a57567, #a87c69 mid-wall; #825244 in shade (h_0093, f_0099, f_0793) | **#A4685A** |
| N, E walls, both nibs, bay dado — **pale blush pink** | #dbd2cc, #ddd7cc, #d2cbc1, #d5cdbf (h_0093, f_0148, f_0156, h_0791) | **#E8D6CF** |
| Ceiling — white matt | #cec7ba, #bdb2a7 (f_0107, h_0791; strongly shaded) | **#F6F4EF** |
| All woodwork/plaster mouldings (cornice, skirting, architrave, rose) — white, gloss on timber, matt on plaster | #cbc2b8 (architrave, shaded), #dcd9d2 | **#F4F2EC** |

- The terracotta/pink change happens exactly at the two inside corners of the W wall (W/N corner next to
  the door, and W wall/west nib corner). The nibs are pink on all faces.

### Cornice (plain run plaster cornice — NOT the hallway's modillion cornice)
- Runs round the whole room, round both nibs and round the bay at ceiling level; white.
- ≈ **0.15 m drop x 0.13 m projection**. Profile from the wall up: 55 mm flat fascia (frieze member) with
  a 6 mm bead at its bottom edge → 10 mm fillet → 55 mm cyma recta (S-curve swelling outward) → 10 mm
  fillet → 20 mm ovolo → 10 mm fillet meeting the ceiling. Best views f_0126–f_0131, f_0169, h_0127.
- At each nib the cornice makes an inside corner (side wall → nib face) then an outside corner (nib end →
  bay return). In f_0127/f_0130 there is an extra ≈ 60 mm "ear" break at that outside corner (the cornice
  steps once more before entering the bay); optional detail.

### Brass picture rail (gallery hanging rod)
- **Polished brass tube Ø ≈ 19 mm**, centre z = 2.80 (≈ 100 mm below the cornice), standing ≈ 45 mm off
  the wall on small brass cup brackets with ball finials at the ends (bracket every ≈ 0.9 m).
- Two runs: N wall from x ≈ 0.95 to 3.55; E wall from y ≈ 3.75 to 0.45. They meet at the N/E corner.
- Every picture and the tapestry hang from it on **brass S-hooks + thin brass chain/wire** (two per
  frame); the lower picture of each column hangs from the upper one on short chains. Brass colour true
  **#C9A24A**, high gloss metallic.

### Skirting
- White gloss, **0.17 m high x 20 mm**: 115 mm plain face, then a 55 mm moulded top (small step, ogee /
  lamb's-tongue, 8 mm top fillet). Runs on all walls, round nib chamfers (3 facets), round the bay; butts
  the door architrave.

### Ceiling rose
- Centred on the room at local (1.80, 1.90). **Ø ≈ 0.75 m**, white plaster, relief ≈ 40 mm at the centre
  thinning to ≈ 10 mm at the rim. Motif: **two concentric whorls of radiating acanthus leaves** (inner
  ring ≈ 8 broad leaves around a small plain boss, outer ring ≈ 16 leaves whose curled tips form a
  scalloped outline). Best views f_0110–f_0112.

### Floor
- **Engineered oak wide plank, rustic grade**, matt/satin lacquer or oil, micro-bevelled edges, visible
  dark knots and filled cracks. Boards **≈ 220 mm wide**, random lengths 1.2–2.2 m, **laid parallel to the
  W wall (running along Y, front-to-back)**, continuous through the doorway into the hall with no
  threshold strip and continuous into the bay.
- Colour sampled #bcac88, #d0c094, #d9cea6; true **#C9B48A** (pale natural oak), knots #6B4E32, roughness
  ≈ 0.45.

---

## 4. Fixed fittings

| item | position (local) | description |
|---|---|---|
| **Wall-mounted TV** | W wall, y 0.45 → 2.34, z 0.72 → 1.80 | 85-inch flat panel, 1.89 x 1.08 x 0.05 m, thin black bezel, glossy black screen, mounted flat ≈ 40 mm off the wall. A white 40 x 16 mm cable trunking drops vertically from its bottom edge (at y ≈ 1.45) to the TV unit. |
| **3-gang dimmer plate** | W wall, centre y 2.47, z 1.21 | White plastic plate 146 x 86 mm, landscape, three round white rotary knobs Ø 25 mm in a row. |
| **A/C wall controller** | W wall, centre y 2.60, z 1.30 | White handset in a white wall cradle, 60 W x 150 H mm, small grey LCD at the top (Daikin). Optional. |
| **Thermostat** | room face of west nib (plane y = 0), x ≈ 0.27, z 1.50 | White box 85 x 85 x 25 mm. Optional. |
| **Air-conditioning floor console** | E wall, y 2.50 → 3.25, z 0.10 → 0.70 | Daikin "Perfera floor" style unit **750 W x 600 H x 235 D mm**, gloss white (#F3F3F1); front is a flat panel with five fine horizontal grooves; top has a full-width recessed air-outlet flap; small round power button on the top right corner; tiny grey logo centre-front. Wall-hung, bottom ≈ 100 mm above floor (skirting cut away behind). f_0156–f_0158. |
| **Double socket** | E wall, y ≈ 3.52, z 0.33 (bottom edge 0.29) | White 2-gang switched socket 146 x 86 mm, in the N/E corner behind the pedestal. |
| Sockets behind TV unit | W wall, low | Not visible; assume one double socket at y 1.3, z 0.35 (hidden). |

No radiator (the A/C console heats the room), no fireplace, no built-in joinery.

---

## 5. Furniture
Positions are the centre of the footprint in local (x, y); "long axis" is the plan direction of the
longest side. Velvet throughout is the same **burnt-orange / rust cotton velvet** (sampled #b8754b,
#a86443, highlights #cb8955; true **#B5683F**, strong sheen/nap variation), trimmed with **cream gimp
braid** (#E6D9B8) hiding the tacks. Dark show-wood is mahogany/dark oak, true **#3B261B**, satin polish.

1. **Scroll-end sofa (Regency / William IV style double-ended settee)** — against the E wall, centre
   (3.22, 1.10), long axis Y, facing -X (toward the TV). **1.80 L x 0.70 D x 0.86 H** (seat 0.42).
   Dark mahogany show-frame: straight moulded seat rail with a bead along the lower edge, each end a tall
   **outward-rolling S-scroll arm** faced in mahogany ending in a carved volute, a low straight
   upholstered back (0.75 high), on four **stout turned "bobbin/bun" legs** (three stacked rings,
   Ø 90 mm, 0.20 high). Upholstery: one long fixed seat squab, upholstered inner arms and back, cream
   gimp along the seat rail and following the scroll facings. Loose items: **two cylindrical bolsters**
   (Ø 0.17 x 0.40) lying against each scroll arm, each end gathered into a pleated rosette with a
   covered button; **two big square back cushions 0.55 x 0.55** leaning on the back; **two smaller
   scatter cushions 0.42 x 0.42**, one at each end, lighter orange (#C98958). f_0133–f_0136, f_0141.
2. **Coffee table** — centre (2.05, 1.85) on the rug, long axis Y. **1.60 L x 0.62 W x 0.46 H**. Dark
   stained oak with strong open grain (sampled #5e4d3b–#776047, true **#5A4330**, semi-gloss). Top 40 mm
   thick with rounded corners (R 40) and a **thumb-moulded/ogee edge**; two **solid slab trestle ends**
   (≈ 0.45 wide x 60 thick, splayed sabre outline, set 0.25 in from each end) joined by a low stretcher
   rail. f_0138–f_0142.
3. **Long upholstered bench / window stool** — centre (2.15, 3.02), long axis X, parallel to and ≈ 0.45 m
   in front of the bookcase. **1.15 L x 0.42 W x 0.46 H**. Flat orange-velvet padded top (80 mm thick,
   gimp at the bottom edge) on a dark oak frame: four **turned baluster legs** joined by an H-stretcher
   (two end rails + one centre rail). f_0144, f_0231.
4. **Glazed bookcase** — against the N wall, x 1.30 → 3.05, centre (2.18, 3.62). **1.75 W x 0.36 D x
   1.22 H**. Dark mahogany (true **#3A261C**; top surface mid-brown #6E5438, polished). Rectangular top
   with a **bold gadrooned (rope-twist "pie-crust") edge moulding** 35 mm; plain frieze 60 mm; **four
   glazed doors** (two pairs) each ≈ 0.41 x 0.83, door frames 45 mm, each door with **Gothic astragal
   glazing bars**: three vertical bars that branch near the top into interlaced pointed/ogee arches;
   clear glass; small brass escutcheons, a gold key tassel hanging from the second door. Plain plinth rail
   60 mm, on four short **cabriole legs with carved knees and ball-and-claw feet** (0.20 high) — front
   legs at the corners plus one under the centre. Inside: 3 shelves of books (mixed coloured spines —
   texture can be generic). f_0183–f_0186, f_0190–f_0192, f_0785.
5. **Pedestal plant stand (torchère)** — in the N/E corner, centre (3.38, 3.57). **Ø 0.32 top, 0.95 H**.
   Glossy red mahogany (#4A2218): round dished top with moulded rim, turned baluster column with ring
   collars, three small cabriole feet. Carries the bird ornament (§6).
6. **Side table (barley-twist occasional table)** — against the E wall between the A/C console and the
   sofa, centre (3.37, 2.22). **0.46 W x 0.36 D x 0.72 H**. Dark oak (#3F2C1E): rectangular top with a
   **scalloped / pie-crust wavy edge**, four **barley-twist legs** with square blocks top and bottom,
   plain box stretchers 0.12 above the floor. Carries the tantalus (§6). f_0146–f_0149.
7. **Pair of Victorian/Edwardian carved parlour armchairs** — in the bay, facing into the room and
   slightly toward each other: west chair centre (0.98, -0.30) rotated to face (+0.35, +1) direction;
   east chair centre (2.62, -0.30) facing (-0.35, +1). Each **0.62 W x 0.68 D x 1.05 H** (seat 0.38,
   arm 0.60). Dark carved oak/walnut frame: tall back with a **carved, shaped cresting rail (scrolls and
   a central shell/leaf)**, turned finial-topped back posts with ring turning, upholstered rectangular
   back panel (0.36 x 0.48) with cream cord edging; **open padded arms** (velvet arm pads 0.25 long on
   moulded arm supports ending in small turned knobs); deep sprung velvet seat with gimp; **short turned
   front legs with stacked rings**, plain raked back legs. f_0116, f_0117, f_0214, h_0117.
8. **Lamp table** — centred in the bay between the chairs, centre (1.80, -0.48). **Ø 0.62 x 0.64 H**.
   Mahogany (top #7B593C, true #6A452C): round top with a **carved foliate/gadrooned edge band** 30 mm
   deep, shallow plain apron, **four slender square tapered legs ending in spade feet**, splayed
   slightly. f_0118, f_0216–f_0223.
9. **Footstool** — centre (2.30, 0.55), in front of the east armchair. **0.55 x 0.45 x 0.40 H**:
   overstuffed orange-velvet cushion top with rounded corners and gimp, on four short dark **cabriole
   legs**. f_0137, f_0115.
10. **TV unit** — against the W wall, y 0.40 → 2.20, centre (0.23, 1.30). **1.80 L x 0.45 D x 0.56 H**.
    **Rustic solid oak, mid golden-brown waxed** (sampled #ab955b / #735838 in shade, true **#A98850**).
    Chunky 30 mm plank top overhanging 15 mm with eased edges; square 70 mm corner posts down to the
    floor; layout left→right as you face it: framed cupboard door (0.45) | open shelf over one shallow
    drawer (0.80) | framed cupboard door (0.45); doors are flat-panel in 60 mm frames; **black iron
    drop/bail handles** on doors and drawer. f_0204–f_0209.
    On it (keep as characterful A/V set): a pair of **black bookshelf speakers** 0.21 W x 0.33 H x 0.27 D
    at each end; a **valve (tube) amplifier** centre-left, 0.43 x 0.33 x 0.19 — champagne-silver front
    panel with two VU meters and two knobs, black perforated cage and three black transformer cans on
    top; a **Chinese chess (xiangqi) board** 0.38 x 0.42 in pale wood with dark-red round pieces lying
    flat at centre-right; a black disc player on the open shelf.
11. **Folding cake-stand / small dark folding stand** — closed and leaning against the E wall between the
    sofa's front end and the east nib, centre (3.52, 0.12), ≈ 0.25 W x 0.85 H, dark oak. Optional.

---

## 6. Soft furnishings & decor

### Rug
- Centre (1.85, 1.80), long axis Y, **1.40 x 2.00 m**, flat machine-woven Persian/Ziegler-style, pile
  ≈ 8 mm. **Cream/ivory field (#E4DDC8)** covered with an all-over scrolling vine of **navy (#1F2A44)**
  stems with **taupe/khaki (#8C7F62)** and grey-blue (#6F7C8C) palmettes and rosettes; framed by three
  borders — a narrow navy guard line, a 0.18 m main border of repeated palmettes on cream, another navy
  guard line — and a plain cream outer edge ≈ 60 mm. The coffee table hides the centre in every frame;
  rectify the visible corner from **f_0138**, quad TL(160,600) TR(440,440) BR(720,820) BL(330,1185)
  (approximate — re-detect the rug edges), then mirror/tile it to build the full rug.
  The coffee table stands on it; the sofa's front feet are just off its east edge.

### Curtains (bay)
- **Four full-length drops** of heavy wool-look **tartan/plaid**: warm taupe-grey ground (true
  **#8E8271**) with broad **brick-red (#A04A45)** bands, thin **cream (#E3DCCB)** double lines and thin
  **charcoal (#3C3836)** lines; check repeat ≈ 0.20 m (sampled in shade #6f5f54). Lined, pencil-pleat
  heading fixed to a concealed white track tight under the bay cornice (top z 2.88); hem ≈ 0.12 m above
  the floor.
- Positions: (1) on the west return wall beside the west nib (x 0.35, y -0.02 → -0.20); (2) on the front
  wall at the north-west bay corner, covering the outer half of the first front light (x 0.40 → 0.75,
  y -0.80); (3) mirror of 2 at the east corner (x 2.85 → 3.20); (4) mirror of 1 on the east return
  (x 3.25). Each drop is gathered to ≈ 0.40 m wide and **tied back at z ≈ 1.15** with a **cream twisted
  rope tie-back with a large champagne-gold tassel** (tassel 0.30 long, bulb head Ø 60 mm) on a small
  brass hook; drops 1 and 4 are pulled toward the nib, drops 2 and 3 toward the corner.
  f_0211–f_0213, f_0225, f_0226.
- Shutters: see §2.3. No pelmet, no pole.

### Wall art — all hung from the brass rail (§3)
Outer sizes are W x H in metres; z = centre height. Quads are pixel corners (TL, TR, BR, BL) of the
**outer frame** in the named 720x1280 frame, ±10 px — re-detect edges before rectifying. None contain
people.

**N wall (rear), left→right when facing it (centre x):**

| id | centre x, z | outer W x H | frame | subject | texture source |
|---|---|---|---|---|---|
| A1 | 1.28, 2.44 | 0.70 x 0.55 | bright gold, 60 mm, reeded with a beaded/rope inner course | oil: thatched cottage behind a picket fence, cottage-garden flowers in the foreground, green trees | f_0176: (222,347) (590,232) (660,553) (222,628) |
| A2 | 1.28, 1.71 | 0.66 x 0.86 | heavy antique-gold swept "rippled leaf" Baroque frame, 95 mm wide, deep | oil: white farm cottages by a pond with ducks, pink-blossom tree, blue sky | f_0176: (230,645) (620,588) (720,1205) (240,1150) |
| TAP | 2.20, 2.00 (top 2.73, bottom 1.28) | 0.95 x 1.45 | unframed textile hung from 6 brass hooks through its top edge | embroidered / appliqué folk tapestry — see below | f_0169: (100,298) (580,290) (720,930) (100,1105); lower-right corner is hidden by the flower vase, alternatives f_0172, f_0173 |
| A3 | 3.12, 2.45 | 0.62 x 0.52 | antique-gold swept leaf frame, 80 mm | oil: autumn mountain valley, stone bridge over a stream, orange/purple trees, bright clouds | f_0165: (65,312) (295,487) (272,678) (3,600) |
| A4 | 3.12, 1.78 | 0.54 x 0.70 | bright gold with beaded course, 60 mm | oil: yellow farmhouse beyond a field of red poppies and purple flowers | f_0165: (22,637) (250,700) (215,990) (0,1045) |

Tapestry design: brick-red centre field (#A8362B) crowded with stylised birds (hummingbirds in flight, two
long-necked birds at the bottom), pink fan-flowers and green fern leaves worked in pink, yellow, orange,
turquoise and cream satin-stitch; large scalloped "heart/leaf" lobes at the top-left and bottom-right
corners of the field filled with multicoloured daisies on dark green; a wide **navy border (#1B2145)**
carrying blue-and-white doves and red berries; a thin cream piping line; plain navy outer binding 40 mm.

**E wall (party wall), left→right when facing it (from the rear corner toward the bay; centre y):**

| id | centre y, z | outer W x H | frame | subject | texture source |
|---|---|---|---|---|---|
| B1 | 3.33, 2.43 | 0.62 x 0.52 | bright gold, rope-twist inner course, 55 mm | oil: gabled stone cottage under a dark stormy sky, big green tree left | f_0164: (187,512) (410,487) (430,683) (183,700) |
| B2 | 3.33, 1.86 | 0.66 x 0.58 | plain brushed pale-gold scoop moulding, 55 mm | oil: autumn woodland, yellow foliage, stepping-stone path through green grass | f_0164: (178,740) (432,716) (452,957) (186,960) |
| B3 | 2.50, 2.40 | 0.76 x 0.62 | bronze-gold mottled wide moulding 60 mm; glazed; double mount: wide white outer (95 mm), grey inner (45 mm) | watercolour: garden wall with round moon-gate and tiled pavilion roof, greenery | f_0788: (310,240) (575,300) (565,510) (308,470) — avoid f_0162, chandelier reflection |
| B4 | 2.50, 1.75 | 0.76 x 0.62 | as B3 | watercolour: thatched wooden hut among trees | f_0162: (70,716) (360,725) (360,937) (44,984) |
| B5 | 1.66, 2.18 | 0.66 x 0.92 | as B3 but a single wide white mount | watercolour: bouquet of white narcissus/anemones in a tall vase, grey-lilac wash background | f_0132: (148,318) (385,258) (415,628) (183,655) |
| B6 | 1.02, 2.42 | 0.42 x 0.52 | thin polished pale-gold 15 mm frame; wide white mount; glazed | botanical study: cluster of white blossoms (very pale) | f_0132: (428,225) (598,205) (603,415) (437,443) |
| B7 | 1.02, 1.88 | 0.42 x 0.52 | as B6 | botanical study: pale pink-white dog-rose spray with green leaves | f_0132: (433,470) (605,445) (608,622) (445,650) |

Frames stand ≈ 30–60 mm off the wall and tip forward ≈ 3° at the top (hung from chains). The W wall and
the nibs carry no pictures. Gold colours: bright gold #C8A64B, antique gold #9C8440, bronze-gold #8C7446.

### Plant
- **Dracaena (striped "Lemon-Lime" / Warneckii type)**: two woody canes, rosettes of strap leaves with
  dark-green centres and lime/cream margins, overall 1.10 m high, spread 0.75. **Matt black ribbed pot**
  Ø 0.30 x 0.28 on a low dark wooden wheeled caddy. Centre (1.02, 3.50) — on the N wall between the
  open door leaf and the bookcase. f_0179–f_0182.

### Permanent ornaments (keep)
- **Bookcase top, left→right when facing it:** oval silver-plated gallery tray 0.50 x 0.35 with ≈ 12
  cut-crystal tumblers and stem glasses; white porcelain reclining long-haired cat 0.25 long; **bronze
  "Flying Mercury" statuette** (after Giambologna: figure balanced on one toe, arm raised, caduceus) 0.55
  high on a black cylindrical marble socle; small celadon-green bowl; cut-crystal decanter with faceted
  ball stopper 0.30; **mahogany bracket clock** 0.26 W x 0.30 H x 0.15 D with stepped top and a brass
  carrying handle, square brass dial with silvered chapter ring, black Arabic numerals and gilt corner
  spandrels; two cut-crystal footed vases (0.20 and 0.12); glass vase of orange/red/pink flowers 0.45
  high; glass jar; low bamboo tea tray 0.40 x 0.25 with a small grey-green teapot and four cups; glass
  jar of potpourri tied with a cream ribbon. f_0186–f_0196.
- **Pedestal:** long-billed brown speckled bird (rail/woodcock type) perched on a pale driftwood branch on
  a stepped rectangular wooden base 0.22 x 0.14; overall 0.42 high. f_0154, f_0199.
- **Side table:** oak **three-bottle tantalus** 0.36 W x 0.15 D x 0.32 H with brass corner straps, lock
  plate and top handle bar; three square hobnail-cut crystal decanters with faceted ball stoppers; a
  small gold key tassel. f_0148.
- **Lamp table:** table lamp (§7); turned wooden **solitaire board** Ø 0.23 with ≈ 32 cream stone
  marbles; **mother-of-pearl / bone inlaid marquetry box** 0.20 x 0.13 x 0.07 with a geometric star
  pattern. f_0118, f_0218.
- TV unit items: see §5 item 10.

---

## 7. Lighting
All lamps are warm white (≈ 2700 K); the room reads distinctly warm/amber in the video.

1. **Chandelier** — hung from the centre of the ceiling rose at local (1.80, 1.90). Overall **Ø ≈ 0.85 m,
   drop ≈ 0.80 m** (lowest crystal at z ≈ 2.25). Polished/antique **brass** (#B8963E): short chain and
   turned baluster stem from a brass ceiling cup, a wide shallow **dished brass body/bowl** (Ø 0.28) at
   the bottom with a turned acorn finial below; **12 lights on two tiers** — 8 long S-scroll arms
   springing from the bowl (lower tier, on Ø 0.80) and 4 shorter arms above (upper tier, on Ø 0.40).
   Each arm ends in a brass drip pan hung with a ring of crystal drops, an ivory candle sleeve and a
   candle bulb under a small **pleated dusky-rose/terracotta-pink fabric clip-on shade** (bottom Ø 0.13,
   top Ø 0.07, height 0.11; outside #B4605A, lining cream — glows cream-white when lit). **Strings of
   faceted crystal beads** swag from arm to arm and up to the stem, with pear-shaped crystal pendants at
   each arm tip. f_0087, f_0110–f_0113, h_0791.
2. **Wall sconce S1** — W wall, centre y 0.67, z 2.45 (between the TV and the west nib, above TV height).
3. **Wall sconce S2** — W wall, centred over the door, centre y 3.16, z 2.45.
   Both identical: **five-light gilt "flowering branch" (tôle) bracket**, ≈ 0.55 W x 0.50 H x 0.22
   projection. A bunch of naturalistic leafy stems gathered at the bottom-centre by a ribbon bow (which
   hides the back-plate) fans upward and outward into five curving arms; long lanceolate leaves and
   small five-petal flowers sprout along the stems; each arm ends in a **white frosted-glass petal/tulip
   cup** holding a clear flame-tip candle LED. Metal colour antique gold with dark patina
   (#8A7340 base, #C6A85A highlights). They throw strong leaf shadows on the terracotta wall.
   f_0093 (S2 close), f_0105–f_0108, f_0099.
4. **Recessed downlights** — small white-bezel LED spots, Ø ≈ 85 mm, warm white ≈ 3000 K. Eight seen,
   forming a ring around the chandelier; best-fit grid: x ∈ {0.60, 1.80, 3.00} × y ∈ {0.55, 1.90, 3.25}
   **minus the centre position** (the chandelier). None inside the bay.
5. **Table lamp** on the bay lamp table, at local (1.80, -0.62). Total height 0.78. Base: **salmon-pink
   alabaster/marble urn** (Ø 0.13, 0.30 high; #C99A7A with paler veining) with **ormolu (gilt-brass)
   mounts** — two cherub/caryatid figures as handles on the shoulders, a rose-garland swag across the
   belly, a leafy gilt collar and a round gilt acanthus foot (Ø 0.16) on a pink marble disc; gilt reeded
   stem and candle cup above. Shade: slightly flared six-panel **bell/empire shade** (top Ø 0.24, bottom
   Ø 0.34, height 0.27), **cream fabric printed with a coral-red floral toile** (#F1E6DA ground, #C0544A
   print). Gold twisted flex. f_0118, f_0123, f_0124, f_0216.

---

## 8. Declutter list (deliberately excluded)
- Two folded bicycles and the folded black wheelchair/rollator parked in front of the A/C console and
  bookcase.
- Shopping bags, grey striped laundry/duvet bag and red garment on the floor and rug; white fleece
  blanket and grey throw on the east armchair; magazines/newspaper on the bench and in the brass magazine
  box by the east nib (the brass box itself may be omitted).
- Loose timber picture-stretcher frame leaning on the bookcase.
- Robot vacuum-mop dock (tall grey tower) beside the TV unit; black subwoofer on the floor between the
  TV unit and the west nib; DVD/Blu-ray boxes on the TV unit.
- Coffee-table clutter: tissue box, remotes, flask, coaster, small boxes. Remote and crocheted coaster on
  the side table.
- Greeting cards on the bookcase (handwriting/names — privacy), small dropper bottles.
- Small white alarm/contact sensors on the nib arrises; red plug-in device in the corner socket.
- All reflections of the person filming (TV screen, hall mirror seen through the door).

---

## 9. Reference frames
| frame | shows | camera (local x, y) → looking |
|---|---|---|
| f_0791 | Whole bay: 4+1+1 lights, shutters, four curtain drops, both armchairs, lamp table, coffee table, rug, chandelier, edge of TV wall | ≈ (1.6, 2.6), eye 1.5 m → -Y (toward the street) |
| f_0087 | First view from the doorway: E wall gallery, sofa, A/C console, side table, bench, coffee table, rug, chandelier + rose | ≈ (0.3, 3.2) in the doorway → +X/-Y diagonal |
| f_0099 | Entire W (terracotta) wall: both sconces, TV, switch, TV unit, door open with architrave, floor boards | ≈ (2.6, 2.2) → -X, slightly toward the front |
| f_0793 | W wall close: TV right half, switch + controller, door opening and architrave, hall beyond | ≈ (1.9, 2.3) → -X/+Y |
| f_0785 | N wall: bookcase with ornaments, tapestry, A1–A4, plant, pedestal, N/E corner with A/C | ≈ (0.6, 2.6) → +X/+Y |
| f_0133 | E wall: B1–B7 with brass rail, sofa with all cushions, side table + tantalus, downlights | ≈ (1.9, 1.0) → +X/+Y, tilted up |
| f_0115 | Bay from the side: window compartments, transom, fanlights, sill, armchairs, footstool, rug corner | ≈ (1.3, 1.5) → -Y/+X |
| f_0127 | West bay corner: curtain pair with tie-backs, return light, nib with chamfer stop, cornice breaks, terracotta beyond | ≈ (1.6, 0.2) → -X/-Y, tilted up |
| f_0139 | Coffee table, rug pattern, sofa, bench, N/E corner | ≈ (1.3, 0.9) → +X/+Y, tilted down |
| f_0082 (+ f_0078, f_0084) | Hall side: pedimented surround — frieze ornament, corbels, broken pediment, pedestal block, hall cornice | hallway, ≈ 0.9 m in front of the door, looking up at the head |

---

## 10. Uncertainties
- **Ceiling height** 3.05 m ± 0.10 (ultrawide vertical scale). Window vertical build-up (§2.3) scales with
  it; sill-top height could be anywhere 0.58–0.72 m.
- **Plan size** 3.60 x 3.80 m ± 0.15; bay depth 0.85 ± 0.10; nib width 0.35 ± 0.05. If `house.json`
  fixes different overall sizes, keep the *order and gaps* on each wall and scale proportionally.
- TV assumed 85-inch (height check against the door supports it); if it is 75-inch the W-wall gaps grow
  by ≈ 0.1 m each side.
- Whether the bay returns are exactly square (90°) — they read as square in f_0126–f_0131 and the cornice
  mitres look 90°, but a slight splay cannot be excluded. Best guess: square.
- Which fanlights open: outer-front and return fanlights show stays/handles; the two centre ones look
  fixed. Lower lights are hidden by shutters — assumed side-hung casements, irrelevant visually.
- Shutter louvre count/size (≈ 17 x 63 mm) and whether the centre panels have brass catches.
- Exact cornice profile (members and sizes are a best reading of oblique views); the "ear" break at the
  nibs is optional.
- Downlight layout: eight fittings were seen but never all in one frame; the 3 x 3-minus-centre grid is a
  best fit.
- Chandelier arm count (12 = 8 + 4) — could be 10 or 15; shades overlap in every frame.
- Picture sizes are ±10 %; relative order, stacking and frame styles are certain. A2 and A4 are portrait,
  the rest of the oils landscape.
- Door leaf could be 838 mm rather than 762 mm wide; hinge side and inward swing are certain (hinge
  knuckles visible on the rear jamb from both sides).
- Pedimented surround: member heights ±15 %; the break-forward of the frieze ends (≈ 25 mm) is read from a
  vertical step and matching notch in the cornice in f_0081/f_0082 — real, but its depth is a guess.
  Whether the pedestal block tapers exactly as described (inverted trapezoid) is from one view.
- Wall thickness at the door (0.15 m) and front-wall/nib thickness (0.30 m) are assumptions.
- True paint colours: the pink is certainly a pale warm blush and the W wall a muted terracotta; hexes
  are neutral-light estimates, not matched paint references.
- Socket/thermostat positions are approximate; the thermostat is on the west nib's room face (or at the
  very front end of the W wall — the two readings differ by 0.1 m).

---

## Reconciled dimensions (from `spec/house.json`, see `spec/RECONCILE.md` D4, D7, D8, D13)
- Main room: x 0.80..4.30, y 0.99..4.73 (3.50 x 3.74; this spec had 3.60 x 3.80). Ceiling 2.95 (was 3.05).
- Bay: x 1.10..4.00, y 0..0.99 (2.90 wide; 0.74 of return plus the 0.25 front wall). Nibs 0.30 x 0.25.
- Local to global, keeping each item's gap to the wall it sits on:
  - x: W-wall items + 0.80; E-wall items + 0.70; bay items and centre items (rose, chandelier, rug,
    coffee table) + 0.75; N-wall items keep their order between x 0.80 and 4.30.
  - y: N-wall and door-keyed items (door, TV, switches, sconces) + 0.93; front-wall items + 0.99;
    items in the bay + 0.85; centre items + 0.96.
- Door D1: opening y 3.70..4.48, centre (0.725, 4.09), wall 0.15 thick. TV y 1.38..3.27, leaving 0.39 to
  the west nib (was 0.45).
- Heights: scale items tied to the ceiling (cornice, picture rail, bay head) by 2.95 / 3.05; keep the
  door, TV and sill heights.
- Verification round: the bay's west cheek is a thin 0.20 window wall (faces x 0.90 vestibule / 1.10
  bay); the room side does not move. Floor direction re-checked and **kept along Y**: the full-res still
  t=114 (f_0115) shows long board edges receding toward the bay with short end joints across, and
  f_0234/f_0235 show long edges parallel to the door line, continuous with the hall boards.

## Round 3 corrections (core owner, from build/rooms2_open.md)
- L6: rose and chandelier at (2.55, 2.73). L3: brass rod x 1.33..4.255 on the north wall, east run to y 1.40, 4 brackets
  north and 5 east.
- L5 shutters: the outer front panels hinge at the corner posts, away from the brass catch (v1 f_0127); with the
  curtains tied back the panels may only swing 10 (return lights) and 5 degrees (front lights) before they touch the
  cloth, the tie-backs or the bay lamp table; drawn curtains open first.
- **Round 4 (IX-02):** that swing was invisible, so "open / close the shutters" now tilts the louvres, as the owner does
  in v2 f_0759-0766: the panels stay put (`trigger`), the louvres are modelled tilted open (12 degrees, the daytime
  look) and shut (75 degrees, the night look of 2.3) in state 1 (`lib/joinery.py SHUTTER_TILT`).
- L-02 (east-wall chain) is NOT changed: the filmed chain (A/C 0.75 about 0.15 off the NE corner, side table 0.46,
  sofa 1.8-2.0, sofa scroll about 0.1 off the nib, B5 and the sofa sharing a centre at about y 2.04) is about 3.3-3.6 m
  long against the 4.20 m wall, while L1 (north wall at y 5.19 from the chamfer and door) and L6 (axis 2.33) are
  each supported by their own frames. Until a re-survey settles the north wall, the room keeps L1 and L6.

## Round 3 (21 Nov footage v10; brief spec/phase3/briefs/living.md, survey spec/phase3/living_games.md)
Built by `blender/rooms/living.py` + `living_games.py` (textures: `living_games_tex.py`, run with the system Python;
all generated, nothing reference-derived, in `blender/textures/art/living/`).
- Shell moved: bay x 1.03..3.93 (lights centred on 2.48). The curtain track, the four drops, tie-backs and the drawn
  state read the bay from `features[living_bay]`; track x 1.095..3.865. The thermostat moved onto the flat part of the
  0.23 m west nib (x 0.82..0.905; its chamfer starts at 0.924).
- Owner instruction: **xiangqi set and domino box on the coffee table, solitaire on the lamp table**; the old copies on the
  TV unit and the lamp table are gone.
  - Xiangqi (`living.xiangqi`, one object): walnut board 0.43 x 0.475 x 0.015 at (2.845, 2.15, 0.46), rot -85 deg, one
    generated top texture (cells alternating tone and grain, 4.5 mm maple lines, inner files stop at the river, both
    palace crosses, 38 mm margin); 32 discs dia 38 x 15 with 2.5 mm round arrises on one lathed profile, characters in a
    1024 px atlas (DFKai-SB kaishu; red 車 馬 相 仕 帥 炮 兵 with #C8505C fill on the east army, upright for the east
    player; 車 馬 象 士 將 炮 卒 with #4FB3A6 fill on the west), UV per piece. Centres from survey table 2.1; two red
    back-rank pairs that overlapped by 1-4 mm are pushed apart (0.8 mm gap).
  - Domino box (`living.domino_box` + `.lid`, `.tiles_in`, `.tiles_out`): 145 x 97 x 42 (base 30, lid 12) at
    (2.85, 1.70, 0.46), rot -131 deg, hinge side south-east. Generated marquetry atlas: lid border pinstripes with dotted
    band and bone corner squares, bone / red-brown / bone lines, black field with the star-and-hexagon lattice (5 MOP
    stars in a quincunx + half stars at the short sides, 12 hexagon rosettes), side panels of two-row lozenge chevrons in a
    bone line, 6 mm striped corner posts, three stringing lines on the lid edge. Crimson velvet lining. 28 cream dominoes
    48 x 24 x 7.5 with pips, centre line and brass pin from a generated atlas, four layers of seven. Interaction
    `living.domino_box` (label Dominoes): lid hinge -100 deg; in state 1 the 6-6, 2-3 and 4-4 leave the top layer and lie
    face up in front of the box (survey positions). Not modelled: the underside bone border (never seen).
  - Solitaire (`living.solitaire`): burr-wood board dia 0.24 x 15 with field, bead, gutter and lip, 33 marbles of 20.5 mm
    at 23.8 mm (centre filled), cream / honey / tan / pink solids and banded onyx, lattice turned 9 deg. Placed at
    (2.56, 0.45) instead of the surveyed (2.57, 0.415): with the lamp at (2.62, 0.245) the two surveyed positions overlap
    by 33 mm (board r 0.12 + gilt foot r 0.09 > 0.177 apart); the board moved 0.035 m north-west to clear the foot by 4 mm.
- Table lamp rebuilt bottom to top as v10 (gilt acanthus ring foot dia 0.18, domed marble foot dia 0.145 x 35, marble
  torus neck dia 50, inverted-cone marble body 45 mm -> 0.13 at a gilt rose-garland collar 0.25 above the ring, swags,
  roses and pendants 40 mm below); the shoulder, gilt stem and toile shade above the collar kept (not in v10); moved to
  (2.62, 0.245). Marble map generated (#B5846B seen, base darkened because the room light lifts it).
- Curtains: hem 0.27 (was 0.12), both states; tartan red bands turned raspberry-wine (#9A4A55, `tartan_wine.jpg`);
  return-drop hooks reach the plaster (no window timber there).
- Rug centre x 2.65 (east edge 3.35, west edge 1.95). Footstool at (2.50, 1.05) in front of the lamp table (v10), which
  also frees the lane between the sofa and the coffee table. East armchair: no loose cushion (v10).
- Armchairs: two-tier arms (flat pad with gimp at its lower edge, a thick velvet roll on it), front post rising to a ball
  finial (g1309, t42).
- Brass magazine rack (`living.magazine_rack`) 0.30 x 0.15 x 0.26 against the east cheek by the nib (3.83, 0.78),
  empty; its divider top 0.258 stays 12 mm under the curtain hem in both curtain states.
- Coffee / side table top: generated long plain-sawn grain with broad cathedral arches over four boards, lower contrast,
  roughness 0.26 (`oak_top.jpg`). Velvet map turned from burnt orange toward the v10 daylight rose (median #8C4C42 base;
  `velvet_rose*.jpg`; low-medium confidence, as the survey says).
- Not changed here: shutter louvre pitch (joinery; survey 70 +- 8 mm vs 52 mm, low-medium confidence), rug texture (a
  daylight crop from t00_f0021 / g1309 would be better than the night crop; not done).
- Fixer pass (round 3 critic):
  - Xiangqi glyphs centred on their ink (DFKai-SB's textbbox was up to 46 px / 6 mm off), font 160 px: every glyph
    within r 90 px of the 118 px disc top, about 20 mm high (`games_pieces.jpg`).
  - Coffee / side table top regenerated: open cathedral arches along each of four boards (nested parabolas, never
    closed), straight grain at the board edges, dense dark pore streaks along the length (#4F3E30 ground, #1E150F
    pores); it tiles end to end, so the 1.60 m top no longer shows a seam at its middle (`oak_top.jpg`).
  - Solitaire board: burr map darker than the lamp table under it, as in t46 / g1369 (field #4E3121 in the map,
    mottled blotches and curling veins swirled round clusters of dark eyes, golden patches); roughness 0.25. Marbles
    12 x 6 (smooth-shaded); banded onyx marbles carry straight tilted strata by planar projection, not latitude rings.
  - Lamp foot: a gilt cove from the table (r 0.09) in and up to under the marble rim (r 0.073, z 0.019) with 22 lobed
    leaves standing on it tip-up, the dark core showing between them as the piercing; nothing above the marble rim.
    Collar swags thicker, two more cast roses on each.
  - Domino box base is a `trigger` of `living.domino_box` (clicking the box side opens it); the magazine rack has plan
    symbol `bin` (small, soft: on the plan, not a walk block).
  - Open (spec / foundation): the west return light. f_0127 shows it between the front-corner drop and the return drop,
    in a dark timber casing flush with the bay face; the spec (porch-07) puts it at y 0.63 behind a 0.20 m white reveal,
    wholly behind the return drop.

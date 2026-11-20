# stairs2 — staircase from the first floor to the second floor

Sources: **v4 f_0168–f_0200** (foot, newel, balustrade, first cat pictures, bathroom door beside the
foot), **v4 f_0305–f_0356** ("let's go up to the second floor … this is the staircase, this is a smooth
transition … got cats … this is a corner, this is smooth transition, all the details right … get the
dado rail right, get the colour right"), **v6 f_0004–f_0024** (walking down), plus v3:f_0073–f_0076,
f_0503–f_0508 (seen from the first-floor landings). Stills and crops in
`reference/work/p2_first_landing/`: `v4_f0192.jpg`, `v4_f0171.jpg`, `v4_f0320.jpg`, `v4_f0355.jpg`,
`v6_f0009.jpg`, `v6_f0013.jpg`, `c_v4_192.jpg`, `c_v4_355.jpg`.

One flight, directly **above the ground-to-first flight**, in the same 0.84 m wide slot between the
staircase wall (east) and the open well (west). It starts on the first-floor front landing, climbs
toward the rear (+Y) in ten straight risers, then turns **90 degrees to the left (west) on three
winders** and arrives on the second-floor landing, which lies over the first-floor upper strip.

**Dimension confidence.** Width ±30 mm (same strings as the flight below). **Riser count 13 ±1** (10
straight + 3 in the turn; counted from below in `c_v4_192.jpg`, from above in `c_v4_355.jpg` and
`v6_f0009.jpg`). Riser height 0.20 ±0.01, so the rise 2.60 is ±0.20. Going 0.23 ±0.02. Position along
Y ±0.20 (tied to the main flight: the winders sit exactly over its quarter landing).

---

## 1. Shape, levels and dimensions

Frame = **world frame**; Z is world Z.

- **Foot level**: first-floor front level **F1f = Z 3.42**.
- **Top level**: second-floor landing **F2 = Z 6.02** (13 risers x 0.20). The second-floor specs own
  that level; keep "F1f + 13 risers" if either changes.
- **Footprint**: x 0.15..0.99 (0.84 over the strings, 0.78 clear), y 6.06..8.97.
  - straight part y 6.06..8.13;
  - winder square x 0.15..0.99, y 8.13..8.97 — the same square as the quarter landing QL of the flight
    below (`landing1` 1.1).
- **Well**: the stair slot is open from F1f up to the second-floor ceiling over x 0.15..0.99,
  y 6.06..8.97. Its south end at y 6.06 is closed above Z 5.77 by the plastered **trimmer apron** of
  the second floor (a white band about 0.30 deep with a small coved return at its east end —
  v6:f_0010–f_0015, v4:f_0195–f_0197); the front-landing ceiling (Z 5.77) stops there. Its west side
  above Z 6.02 is the second-floor landing edge with a balustrade (second-floor spec).
- **Pitch**: 0.20 / 0.23 → 41 degrees.

### Risers (riser n = front face of step n; tread n is at Z 3.42 + 0.20 n)

| riser | plan position | tread it leads to |
|---|---|---|
| R1 | **bullnose**: straight at y 6.06 from the wall (x 0.99) to x 0.30, then a half-round end of radius 0.14 that wraps the south and west sides of the foot newel and projects 0.10 beyond the string line into the upper strip (v6:f_0022–f_0024, v4:f_0190, v3:f_0507) | T1 3.62 |
| R2 … R10 | straight, y = 6.06 + 0.23 (n - 1): 6.29, 6.52, 6.75, 6.98, 7.21, 7.44, 7.67, 7.90, **8.13** | T2 3.82 … T9 5.22; R10 leads to winder W1 5.42 |
| R11 | straight line from the turning newel (0.15, 8.13) to (0.99, 8.61) — 30 degrees | W2 5.62 |
| R12 | straight line from (0.15, 8.13) to (0.64, 8.97) — 60 degrees | W3 5.82 |
| R13 | along x = 0.15 from y 8.13 to y 8.97, facing east | second-floor landing 6.02, x < 0.15 |

So W1 is a kite against the east wall, W2 the corner kite (its outer edge runs round the north-east
corner), W3 a kite against the north wall; you leave W3 westward onto the second-floor landing
(`v4_f0320.jpg`, `v4_f0355.jpg`, v6:f_0005–f_0008). Nosings: rounded, 25 mm overhang, carpet wrapped.

- **Underside**: plastered. Under the straight part a sloping soffit parallel to the pitch (the
  ceiling of the flight below); under the winders a smooth curved quarter-vault over QL
  (v4:f_0300–f_0303). See `landing1` 11.5.
- **Headroom** over this flight is the full height of the well (second-floor ceiling with its
  skylight — second-floor spec).

---

## 2. Openings

None in the stair itself. Beside the foot, in the same east wall (x 0.99), is the **green-bathroom
door** `d_gbath` (clear y 5.13..5.89; `landing1` 2): its north architrave leg (outer edge y 5.97) is
0.09 south of riser 1, and the raking dado and the wall string of this stair both start against it
(v4:f_0194–f_0200, f_0308).

---

## 3. Architecture and trim

### 3.1 East wall (x 0.99) and north wall (y 8.97) — "smooth transition … get the dado rail right"

- **Wall string**: white gloss board 30 mm thick, about 0.28 deep, moulded top edge (15 mm bead),
  its top about 0.10 above the nosing line. It starts square against the bathroom-door architrave at
  floor level (as a 0.17 skirting for 0.09 m) and rakes up the straight part.
  **At the winders it does not kink: the top edge sweeps up in a continuous S-curve (swan-neck)**,
  steepening over W1, turning the internal north-east corner, flattening along the north wall over
  W2–W3, and finishing at the second-floor landing in a short **level bull-nosed capping block**
  (about 0.25 long, 40 mm thick, rounded end) at x 0.15, from which the second-floor skirting
  continues (v4:f_0319–f_0324, f_0332–f_0341, f_0343–f_0344). Model the string top as a smooth spline
  through: (y 8.13, Z nosing + 0.10) → (0.99, 8.61, 5.80) → corner (0.99, 8.97, 6.00) →
  (0.64, 8.97, 6.12) → (0.15, 8.97, 6.19 = F2 + 0.17).
- **Dado rail**: same 65 x 28 white moulding as the landings.
  - East wall: from the bathroom architrave (it meets the leg about 1.10 above the landing floor) it
    **rakes parallel to the pitch, top edge 0.975 above the nosing line**, in one straight run to the
    north-east corner, where it has reached about Z 6.50.
  - At the internal north-east corner the east rail meets the north-wall rail in a plain **mitred
    valley** — seen from the stair the two rails make a "V" / zig-zag (v4:f_0321–f_0328; v6:f_0005–
    f_0007). On the north wall the rail **rakes on upward to the west** at about 25 degrees for the
    0.84 m of the winders, then turns **level at F2 + 0.975 (Z 6.995)** with a mitred knee at x 0.15
    and carries on round the second-floor landing walls (v4:f_0345–f_0352: the knee, and the rail
    stepping round an external corner of the landing).
  - All changes of direction are mitres in the same section; no ramps or easings in the rail itself.
- **Paint**: below the rail light greige #C8C5BB; above it warm white #F1EEE6 up the full height of
  the well. Matt.
- No cornice on the well walls below the second-floor ceiling.

### 3.2 Open (west) side

- **Outer string**: white gloss **cut string** — the tread ends oversail it with a returned rounded
  nosing and a small scotia under, the riser ends are plain; no carved brackets (v4:f_0178–f_0181,
  f_0187–f_0189). Depth of the board below the tread line about 0.25, lower edge a straight rake.
  Seen from the upper strip this string is the top of the guarding described in `landing1` 5.1; the
  spindles under it stand on the strip edge.

---

## 4. Surfaces and colours

| surface | description | sampled sRGB | true (neutral daylight) |
|---|---|---|---|
| **Carpet** — treads, risers, winders (starts at riser 1; the bullnose is the join with the beige landing carpet, which continues on the second-floor landing) | short dense twist pile, **mid cool grey**, fitted wall to string, no runner or rods | #8f8e8c (lit), #6d675c (shade) | **#8E8B86**, roughness 1.0 |
| Wall above dado, well walls, apron, soffit | matt warm white | #dde5ed (cool daylight from the skylight) | #F1EEE6 |
| Wall below dado | matt light greige | #adb0b4 | #C8C5BB |
| Strings, spindles, dado, capping | white gloss | — | #F4F2EC |
| Newels, handrail | mahogany, gloss varnish | #2a221e, #1d1613 | **#4A2216** |

Light in the well is cool daylight from above; the same paints read warmer on the landings.

---

## 5. Fixed fittings — balustrade

### 5.1 Foot newel
- Centre **(0.20, 6.10)**, standing on the landing floor inside the curl of the bullnose step.
  Mahogany, gloss. Height **1.20** above F1f. Bottom to top (`v4_f0306.jpg`, v4:f_0170–f_0179,
  v6:f_0022–f_0024): square base 90 x 90, z 0 → 0.27, top shoulders chamfered; turned shaft
  z 0.27 → 0.85 — ring, long plain taper swelling slightly from dia 55 at the bottom to dia 70, two
  rings at the top; square block 90 x 90, z 0.85 → 1.06 (the handrail enters its north face), with a
  pyramidal chamfered top; neck and 15 mm collar; **ball finial dia 0.11**, top at 1.20.

### 5.2 Handrail
- Mahogany toad's-back section 65 wide x 55 high, **top 0.90 above the nosing line**, centred over the
  outer string (x 0.18). Straight rake from the foot newel block (Z 4.42) to the turning newel at the
  top of the straight part (Z about 6.25 at y 8.10).

### 5.3 Turning / top newel
- At the inner corner of the winders, centre **(0.20, 8.13)** in plan — directly above the top newel
  of the flight below. It rises from the outer string to about 1.05 above the second-floor landing
  (Z 7.07), same pattern as 5.1, and receives the stair handrail on its south face and the
  second-floor landing balustrade (running south along x 0.15 at Z 6.92) on the same face above it
  (`v4_f0355.jpg`, v6:f_0008–f_0012, v4:f_0171–f_0172). Below the string it ends in a short square
  drop with a moulded cap. The second-floor spec owns everything above Z 6.02.

### 5.4 Spindles
- White gloss, **two per tread** on the straight part (first 0.05 back from each riser line, 0.115
  apart), three on each winder tread end where they fit round the newel. 32 x 32 stock: square base
  block, turned middle (collar, slender vase, two rings, taper, collar), square top block cut to the
  rake — identical to the flight below (v4:f_0178–f_0181, f_0187–f_0189, f_0304–f_0305).

No radiator, socket or switch on the stair.

---

## 6. Furniture

None.

---

## 7. Art — the cat pictures ("I got a lot of cat paintings here … these are all cats")

Five matching pictures on this stair (more of the set hang on the second-floor landing). Each:
landscape, outer about **0.52 w x 0.38 h**; thin **brushed pale-gold** metal-look frame 20 mm (true
#C9B56E, satin); glazed; **double mount** — wide white outer mount, a narrow **burgundy inner band**
(12 mm, #5B2A30) forming a rectangle about 0.30 x 0.19, white inside it; a small **pencil / ink study
of a cat** on the white ground. Hung plumb, stepping up with the stair, centres about 1.40 above the
nosing line on the east wall.

| id | wall, position | centre Z | cat | texture source (720 x 1280, approximate quad TL, TR, BR, BL) |
|---|---|---|---|---|
| **C1** | east wall, y 6.35 — immediately north of the bathroom architrave, under the trimmer | 5.27 | black-and-white (tuxedo) cat sitting, turned to the left, grooming a raised paw | **v4:f_0316** (138,254) (717,273) (690,768) (120,746); v4:f_0196 (225,553) (528,543) (533,768) (228,783) |
| **C2** | east wall, y 7.05 | 5.88 | tabby sitting, seen from behind / three-quarter, head turned | **v4:f_0318** (192,192) (717,142) (717,600) (192,592) (right edge cut); v4:f_0317 |
| **C3** | east wall, y 7.75 | 6.49 | long-haired black-and-white cat crouching, facing the viewer | **v4:f_0326** (172,352) (720,292) (720,742) (180,720) |
| **C4** | east wall above the winders, y 8.50 | 7.50 (1.48 above F2) | striped tabby lying stretched out, head up, facing right | **v4:f_0331** (108,402) (717,348) (690,957) (90,818); v6:f_0006 (105,280) (518,280) (480,580) (188,588) |
| **C5** | north wall of the well, x 0.60 (y 8.97) | 7.55 | black-and-white cat sitting upright, white chest, looking right | **v4:f_0330** (150,363) (615,382) (618,698) (142,702); v4:f_0329 |

The drawings contain no people or text; rectified crops may be used. If a crop is too soft, draw a
grey pencil cat silhouette on white inside the burgundy band.

No mirrors, rugs or curtains.

---

## 8. Lighting and switches

- No fitting on the stair walls or soffit. The well is lit by daylight from the second-floor skylight
  and by the **second-floor landing lights**, which are switched from the first-floor front landing:
  **left rocker of the 2-gang plate** beside the green-bedroom door (`landing1` 8.2, "here I can also
  turn on the second floor lights", v4:f_0310–f_0311), and from the second floor (its spec).
- The foot is also lit by front-landing downlight L1 and strip downlights L2–L3 (`landing1` 8.1); a
  smoke alarm sits on the landing ceiling just west of the foot.

---

## 9. Reference frames

| frame | shows | camera (world x, y; Z) → looking |
|---|---|---|
| v4:f_0168–f_0169 | foot from the bathroom door: bullnose, newel, front landing | (1.5, 5.5; 4.9) → west |
| **v4:f_0170–f_0173** (`v4_f0171.jpg`) | whole flight from the foot: newel, handrail, spindles, raking dado, cat pictures, second-floor balustrade and apron overhead | (0.3, 5.6; 4.9) → north, up |
| v4:f_0176–f_0181 | newel, handrail, spindle turnings, cut string and tread-end nosings | upper strip (-0.2, 6.4) → east |
| v4:f_0187–f_0190 | spindles under the string, bullnose end, newel base | upper strip → east, down |
| **v4:f_0192–f_0193** (`v4_f0192.jpg`, `c_v4_192.jpg`) | riser count from below; wall string; dado valley at the corner; C1–C5 | (0.55, 5.8; 4.9) → north, up |
| v4:f_0194–f_0200 | C1, bathroom architrave, dado dying into it, trimmer above | foot → east |
| v4:f_0309, f_0313–f_0318 | climbing: string, dado, C1, C2 | on steps 1–4 → north / east |
| **v4:f_0319–f_0324** (`v4_f0320.jpg`) | the winders from below; swan-neck of the wall string; level capping block; turning newel | on step 6–7 (0.55, 7.4; 6.2) → north, down |
| v4:f_0321–f_0328 | dado valley at the north-east corner, rail raking on along the north wall | on steps 8–9 → north-east, up |
| v4:f_0325–f_0331 | C3, C5, C4 square-on | on the winders → east / north |
| v4:f_0332–f_0344 | string sweep and capping at the top, winder treads from above | on W2–W3 → down |
| v4:f_0345–f_0352 | dado knee to level at the second floor, external corner, C5 / C4 | second-floor landing → east |
| **v4:f_0353–f_0356** (`v4_f0355.jpg`, `c_v4_355.jpg`) | whole flight from the top: three winders, ten straight steps, well, apron, first-floor doors below | second-floor landing (0.0, 8.5; 7.6) → south, down |
| v6:f_0004–f_0012 (`v6_f0009.jpg`) | walking down: winders, C4, C3, C2, C1 on the left, balustrade on the right | on the winders / steps → south, down |
| v6:f_0013–f_0018 (`v6_f0013.jpg`) | foot seen from step 3: trimmer apron, front landing, green doorcase | (0.6, 6.7; 5.5) → south, down |
| v6:f_0022–f_0024 | bullnose step wrapping the newel, grey / beige carpet join | front landing → north-east, down |
| v3:f_0073–f_0076 | the stair from the rear corridor: outer string and spindles rising overhead | (-0.2, 9.0; 4.5) → south |

---

## 10. Interactions

None on the stair itself (no doors, windows or fittings). The well lights are toggled from
`landing1` S-front B (left rocker). The viewer's walk mesh must follow the treads: straight ramp
Z 3.42 → 5.22 over y 6.06..8.13, then the three winder treads, exit west at Z 6.02.

---

## 11. Doubts and things other areas must agree with

1. **Riser count 13** (range 12–14) and riser 0.20: F2 = 6.02 (range 5.8–6.2). Cross-check: a 2.35
   ceiling over the front landing (the green doorcase cornice is 0.10 below it) plus a 0.25 floor
   gives the same 2.60. The second-floor specs must take the landing level from here or correct it.
2. **Position of riser 1 (y 6.06)**: fixed by nine goings of 0.23 back from the winder square, itself
   placed over QL (8.13..8.97). If QL moves (see `landing1` 12.1) this stair moves with it; if the
   going is 0.25 the foot is at y 5.88. The headroom over the flight below (tread 6 of the main
   flight is under riser 1; soffit Z 3.17 → 2.03 clear) supports y about 6.0–6.1.
3. **Winder geometry**: three kites radiating from the turning newel at 30 / 60 / 90 degrees is the
   regular construction and matches `v4_f0320.jpg` and `v4_f0355.jpg`; the exact angles are not
   measurable.
4. **Dado on the north wall**: raking over the winders and levelling at F2 is read from oblique
   close-ups (v4:f_0321–f_0352); the precise height where east and north rails meet (about Z 6.5) is
   ±0.1.
5. **Turning newel**: whether it is one tall post from the string to above the second-floor rail, or
   a newel standing on the landing with a separate drop, is not clear; one post modelled.
6. **Second-floor landing edge / balustrade and the trimmer apron** belong to the second-floor
   landing spec; the well opening used here is x 0.15..0.99, y 6.06..8.97.
7. **Cat picture positions** follow the "1.40 above the nosing line" rule; C4 and C5 heights are
   relative to F2. Sizes ±0.05. Which cat is in which frame for C2 / C3 could be swapped.
8. **Carpet**: clearly greyer and darker than the landing carpet at the bullnose (v6:f_0022–f_0024);
   in v4:f_0319–f_0344 the winders look beige under warm light — one grey carpet assumed for the
   whole flight.

## Reconciled dimensions (house.next.json)

Added by the phase-2 reconcile step. `spec/house.next.json` is canonical; where the text above differs, the values below win. Reasons and evidence: `spec/RECONCILE2.md` (decision ids in brackets).

- Levels unchanged: 3.42 → 6.02, 13 risers x 0.20, R1 at y 6.06, R10 at y 8.13 [L3].
- **North wall of the well is y 8.73, not 8.97** [S1]: the three kite winders turn in x 0.15..0.99, y 8.13..**8.73**
  (0.84 x 0.60) above the quarter landing. Picture C5 and the swan-neck of the wall string move -0.24 with the wall.
- Well opening in the second floor: x 0.15..0.99, **y 6.23..8.73** (`stairwell_void_2`) [S2, verification T1]. Its south
  face is one flat plane with the loft-door wall (north face y 6.23, wall `w_well_s_2`), from the front-landing ceiling
  (Z 5.77 — this is the "trimmer apron") to the second-floor ceiling (Z 8.62); nothing projects into the well above the
  platform. R1 (y 6.06) and the first 0.17 of tread 1 are therefore under the landing ceiling (headroom 2.15). West side:
  the platform balustrade for y 6.23..8.13 (its handrail dies into the south face), the top nosing R13 for y 8.13..8.73.
- Headroom over the main flight 2.2-2.3 (validator).

## Round 3 corrections (core owner, from build/rooms2_open.md)
- Stair carpet: `carpet_silver_beige` #A9A397, the key of the main flight and first-floor landings (stairs S2;
  v4 f_0192 / v6 f_0024 show it nearly as light as the landing carpet). One carpet drops the grey/beige join at
  the bullnose (v6 f_0022-0024); R13 top nosing and the platform step nosing stay `carpet_grey_twist` with the
  landing2 floors. Newel and rails `stairs_mahogany` #2E211C (was #3B211A). Rails on x 0.19, spindles on x 0.185.
- The turning newel (0.20, 8.13) has no drop below the string: it would hang 0.37 below the QL ceiling (5.35)
  (v6 f_0033, v3 f_0029).
- Bullnose R1 stands 70 mm proud of the newel's south face with a 0.07 quarter round (a radius 0.14 about
  (0.30, 6.20) passes through the newel centre). Foot newel 1.40 high. Spindles 38 mm.
- W1 is at y 6.90 (not 7.62); C1 at y 6.24, Z 5.34 (v4 f_0196).
- The stairwell east wall carries an 18 mm shadow-bead cove at the ceiling (Z 8.62, y 6.23..8.73).
- The level strip rail falls toward the south (see landing1.md, round 3).
- Kept: the flight handrail dies into the platform apron about 0.57 m short of the turning newel (apron underside
  Z 5.75 crosses the 0.90 rail line at y ~7.5); v4 f_0171 shows it reaching the newel, so the apron depth or the
  stair's rise are still to be re-surveyed.
- Riser R10 (y 8.13) now has a back face where the quarter landing lies behind it (lib/stairs.py), so the gap between
  the T9 top and the QL ceiling is closed from both sides.

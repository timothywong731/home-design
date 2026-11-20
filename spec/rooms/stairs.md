# Staircase (`stairs`) — visual / dimensional specification

Source frames: f_0241–f_0251, f_0773–f_0777 (all viewed), supporting views f_0063–f_0065, f_0073,
f_0751–f_0753, f_0771–f_0779, stills `reference/work/layout/hr_243.jpg`, `reference/work/verify_dims/
t772–t776.jpg`, `reference/work/hall/full/F_0243, F_0245, F_0751, F_0753, F_0779`.
Owner narration: "there's a stair that goes upstairs… that's carpet, these are carpet here".
Only the ground-floor flight is filmed; model the flight up to the first landing and stop (BRIEF).

Colours: "sampled" = median sRGB under the warm LED/HDR video; "true" = neutral-light estimate — use "true".

Viewpoint convention: **"standing in the hall at the foot of the stairs, looking up the flight"** =
facing +Y (toward the rear of the house). **Left = open balustrade and the hall passage (-X, west).
Right = the staircase wall (+X, east).**

---

## 1. Shape & dimensions

### Frame
The staircase uses the **hallway's local frame** (`hallway.md` §1): origin = centre of the inner-door
frame's hall face, +x east, +y north, z up from the hall oak floor. World = local + (0, 1.83).

### Footprint
- Stair recess **x +0.15 → +0.99 (0.84 m over the strings), y 2.50 → 6.10 (3.60 m)**.
  - West side (x = +0.15): open cut string + balustrade above, panelled spandrel below, facing the
    0.80 m hall passage.
  - East side (x = +0.99): the staircase wall (kitchen behind it), carrying a raking dado and four prints.
  - South end (y = 2.50): the **nib** — the front hall's east wall (x = +0.65) returns 0.34 m east to
    the staircase wall, so the east 0.34 m of the bottom step is tucked behind that return.
  - North end (y = 6.10): wall with the under-stairs cupboard door, facing the kitchen lobby.
- The flight **rises toward +Y**. Clear tread width between strings 0.78 m.

### Steps
- **15 risers of 0.190 m → landing at z = 2.85** (count from `hr_243`: 13–14 nosings visible below a
  landing wall; `layout.md` uses 16 risers / 3.15 m — see §10). Straight goings 0.240 m, nosing
  overhang 25 mm, pitch 38.4°.
- Riser positions (riser n is the front face of step n; tread n is at z = n x 0.19):

  | riser | plan position |
  |---|---|
  | R1 | **curved**: south-west quadrant of an ellipse centred (0.65, 3.00) with semi-axes 0.53 (x) and 0.48 (y) — starts tangent to the nib return at its corner (0.65, 2.52), sweeps west and north, ends against the newel's west face at (0.13, 2.98). East of x = 0.65 the tread simply runs back to the nib return wall (y = 2.50). |
  | R2 | gentle arc from the newel's south-east corner (0.25, 2.97) to the wall at (0.99, 2.78), bowing south by 0.06 m |
  | R3 | almost straight, from (0.25, 3.03) at the newel to (0.99, 3.03) |
  | R4 | straight at y = 3.27 |
  | R5 … R15 | straight, y = 3.27 + 0.24 (n - 4): 3.51, 3.75, 3.99, 4.23, 4.47, 4.71, 4.95, 5.19, 5.43, 5.67, **5.91** |

  So the bottom three steps fan slightly round the newel (bullnose bottom step, not true winders) and
  steps 4–14 are plain rectangles. R15's top is the **landing nosing (y = 5.91, z = 2.85)**.
- **Landing:** level floor at z = 2.85 from y = 5.91 northward over the kitchen lobby's east part
  (x 0.15 → 0.99, to about y = 7.0), carpeted like the stairs. A wall faces you at the top (y ≈ 7.0)
  with white-over-grey paint and a dado rail 0.965 m above the landing (z 3.815). Stop the model there:
  cap the stairwell with a plain white ceiling at z ≈ 5.6 and leave the landing's west side as a plain
  white wall.
- **Stairwell opening in the hall ceiling:** x 0.15 → 0.99, y 2.50 → 6.10. The staircase wall and the nib
  return continue straight up through it, white. The hall ceiling stops at a plain square plaster edge
  along x = +0.15 (no cornice on that edge).
- Underside: not visible (boxed in by the spandrel and the cupboard). Landing soffit over the lobby at
  z 2.60 (see `hallway.md` §1, §4).

---

## 2. Openings
| opening | where | notes |
|---|---|---|
| Under-stairs cupboard door | north end wall y = 6.10, x 0.265 → 0.875 | oak 4-panel 610 x 1981, hinged east, opens north into the lobby; T&G boarding and overhead cupboard above — `hallway.md` §2.3, §4 |
| Open side of the flight | x = +0.15 above the string | balustrade, see §4 |
| Stair foot | between the newel and the nib corner, facing south-west | 0.52 m wide gap you step through onto the bullnose step |

---

## 3. Surfaces

### Carpet (treads, risers, landing — fitted wall to wall, no runner, no stair rods)
- Deep **saxony/plush twist pile, warm silver-grey ("mink")**, wrapped tight over rounded nosings; the pile
  shows lighter and darker brushed patches and footprints. Sampled #7d7668 (f_0249), #8f8877 (hr_243);
  true **#9C958A**; roughness 1.0, with a subtle large-scale mottling (±6 % value).
- On the bullnose step the carpet follows the curve of riser 1 down to the oak floor.

### Staircase wall (x = +0.99) and nib return
- **Wall string:** white gloss board 30 mm thick x 0.28 m deep, its moulded top edge (15 mm bead)
  ≈ 0.10 m above the nosing line, running parallel to the pitch. At the foot it **eases down in a
  concave sweep** (radius ≈ 0.6 m) to meet the 0.17 m skirting of the nib return (f_0242, f_0248).
- **Raking dado rail:** same 70 x 30 mm profile as the hall rail, white gloss, top edge **0.965 m above
  the nosing line measured vertically**, parallel to the pitch from the nib to the landing. At the nib's
  internal corner it meets the horizontal hall rail (z 0.965) through a short vertical knee: the
  horizontal rail returns round the nib corner, runs along the nib's north face, and turns up the rake.
- Paint: **below the raking rail light warm grey #C8C5BB** (`M.PAINT['hall_dado_grey']`, same as the hall dado) (a parallelogram band between string and
  rail), **above it white #F2F0EA** to the top of the stairwell. Matt emulsion.
- Sampled on the stair wall (hr_243, brightly lit): above #c8c5be, below #b6b3a7 — the same two paints
  as the hall; the contrast between them is gentle.

### Spandrel (plane x = +0.15, below the string, facing the passage)
- Flush **white gloss panelling** from the newel (y 3.00) to the north-west corner post (y 6.10); true
  **#F4F2EC** (sampled #b3afa9 in shade).
- **Outer (cut) string:** plain raking board 0.25 m deep directly under the tread ends; its lower edge
  is a straight line parallel to the pitch.
- **Panels:** one tier of **raised-moulding trapezoid panels** set out on a 0.52 m module along y
  (0.42 m panel + 0.10 m stile), six bays from the corner post southward. Each panel: vertical sides,
  horizontal bottom edge 0.10 m above the skirting (z 0.27), **top edge raking parallel to the string
  0.10 m below it**. Panel outline formed by a planted 30 mm ogee moulding standing 12 mm proud; the
  field inside is flat. The two bays nearest the newel are low (0.25–0.45 m high) and read almost as
  small squares (t776); the bay next to the cupboard corner is ≈ 2.0 m high on its tall side (t774).
- **Skirting** 170 mm, same profile as the hall, along the foot of the spandrel.

### Tread ends on the open side
Each step shows, beyond the string face: the **returned nosing** — a 30 mm rounded nosing with a 20 mm
scotia under it, mitred round the corner and running back 0.26 m along the tread end, projecting 30 mm —
above a plain flat riser end. No carved step brackets. All white gloss (t774, f_0773–f_0775).

---

## 4. Fixed fittings — balustrade

### Newel post (foot)
- Position: centre **(0.20, 3.00)**, standing on the oak floor; the bullnose step wraps its south and
  west sides. **Dark mahogany, gloss varnish**, sampled #2e231f, true **#4A2216** (same as the inner doors).
- Total height **1.45 m**. Bottom to top:
  1. square shaft 95 x 95 mm, z 0 → 0.70, arrises lightly eased, top shoulders chamfered into the turning;
  2. turned section z 0.70 → 1.10: 15 mm ring, short cove, a **fat vase/baluster bulb** Ø 95 mm
     (widest at z 0.82) tapering to a Ø 55 mm neck at z 1.00, then two stacked rings (Ø 80, Ø 70);
  3. square block 95 x 95, z 1.10 → 1.28 (the handrail tenons into its north face);
  4. cap: 15 mm moulded collar, short neck Ø 55, **flattened ball finial Ø 115 x 100 mm high**, top z 1.45
     (f_0241, f_0249, hr_243).

### Handrail
- Dark mahogany, gloss, **65 mm wide x 55 mm high**, rounded "toad's-back" top with a small bead each side,
  flat underside. Runs from the newel block parallel to the pitch with its **top 0.90 m above the nosing
  line** (top z 1.20 at the newel, rising 0.79 m per metre), over the centre line of the outer string
  (x = +0.18). It continues up through the stairwell to a matching newel at the landing (top z 3.75);
  seen from the hall it disappears above the ceiling plane at about y = 4.9 (f_0753).

### Spindles (balusters)
- **White gloss, two per tread**, 32 x 32 mm square stock, centres 0.12 m apart (first one 0.05 m back
  from each riser line), standing on the tread ends and housed into the handrail underside.
- Each: square base block (≈ 0.18 m on the front spindle of a tread, ≈ 0.30 m on the back one, so the
  turnings line up with the rake), **turned middle ≈ 0.42 m** — collar ring, long slender vase swelling
  to Ø 30 mm in its lower third, two thin rings at mid height, taper to Ø 18 mm, collar ring — then a
  square top block 0.10–0.15 m with its top cut to the rake (t774, f_0773–f_0776).

### North-west corner post
- At the top of the spandrel, corner (0.15, 6.10): a plain **white square post 0.10 x 0.10 m** rising
  from the spandrel/string line to the hall ceiling, with a small moulded block where the overhead
  cupboard's top line meets it. North of it the landing's apron/bulkhead face (x = +0.15, z 2.60 → 2.90)
  carries the hall cornice (`hallway.md` §3).

No radiator, switches or sockets on the stairs.

---

## 5. Furniture
None.

---

## 6. Soft furnishings & decor

### Four small framed prints on the staircase wall (x = +0.99), stepping up with the flight
| id | centre y | centre z | outer W x H |
|---|---|---|---|
| S1 | 2.80 | 1.84 | 0.34 x 0.46 |
| S2 | 3.65 | 2.51 | 0.34 x 0.46 |
| S3 | 4.45 | 3.14 | 0.34 x 0.46 |
| S4 | 5.25 | 3.77 | 0.34 x 0.46 |

- Rule: centres **1.45 m above the nosing line**, 0.80 m apart in plan, each hung plumb (frames vertical,
  not tilted to the rake); bottoms ≈ 0.25 m above the raking dado. S3 and S4 are above the hall ceiling
  level, visible up the stairwell from the stair foot.
- Each: portrait; **flat frame 42 mm wide with a slightly rounded outer edge, olive-bronze gold
  #7C7048, satin** (about 12 % of the outer width; full-res still t=246.5 and the hall-mirror reflection
  in f_0067/f_0068); sight size ≈ 0.25 x 0.37, filled by **pale off-white paper #ECEAE2** (no separate
  mount visible).
- Subject: a small central **ink-and-wash sketch of a dark sailing/fishing boat with its reflection**,
  grey-violet #5B5566, ≈ 0.12 x 0.10 on the pale paper. Vary the boat slightly across the four.
  No view is near enough to square-on for a rectified crop (best: f_0247 — S1 outer quad ≈ (470,60)
  (612,0) (612,420) (482,372), top edge cut off; f_0245), so **draw a stand-in to this description**.
  No people.

No rug or curtains. The carpet is covered in §3.

---

## 7. Lighting
- No fitting on the staircase itself in the filmed part. The flight is lit by the hall downlights over
  the passage (`hallway.md` §7, lights 3–5 at x = -0.25, y = 3.20 / 4.40 / 5.60) and by light from the
  first floor.
- For the model add one matching recessed downlight (Ø 85 mm white bezel, 3000–3500 K) in the stairwell
  cap ceiling above the landing nosing (x 0.57, y 5.9) so the upper flight is not black.

---

## 8. Declutter list
Nothing on the stairs was removed. Hands/feet of the owner in f_0249–f_0250 ignored.

---

## 9. Reference frames

| frame | shows | camera (hall-local x, y, z) → looking |
|---|---|---|
| f_0243 (still `layout/hr_243.jpg`) | whole flight from the foot: bullnose step, newel, wall string easing, raking dado, three prints, landing wall | (0.1, 1.9, 1.3) → +Y, slightly up |
| f_0241 / f_0242 | newel + first six steps, passage on the left to the arch, nib corner on the right | (-0.1, 2.0, 1.5) → +Y |
| f_0245 / f_0247 | staircase wall with all four prints, raking dado, nib cornice return | (0.3, 2.3, 1.5) → +Y, tilted up 30° |
| f_0248 / f_0249 | bullnose and fanned steps 1–3 from above, newel base, wall string sweep | (0.0, 2.3, 1.6) → +Y, tilted down 30° |
| f_0064 | stair foot in context from the front hall (console, nib, open living door) | (-0.1, 0.4, 1.6) → +Y |
| f_0773 / f_0774 | spandrel panels, cut string, tread-end nosings, spindles, handrail, corner post | passage (-0.3, 5.3, 1.5) → south-east, tilted up 35° |
| f_0776 / f_0777 | balustrade descending to the newel, low spandrel panels at the foot | passage (-0.3, 4.2, 1.5) → -Y |
| f_0753 | top of the balustrade meeting the ceiling, corner post, overhead cupboard, under-stairs door | lobby (-0.2, 7.5, 1.5) → -Y, tilted up 25° |
| f_0779 | nib return face with dado/skirting wrapping it, lowest print, newel from behind | on the passage (0.0, 3.4, 1.6) → -Y |

---

## 10. Uncertainties
1. **Riser count / landing level:** 15 x 0.190 = 2.85 m here; 13–14 nosings are countable plus the
   landing edge. `layout.md` has 16 risers / first floor 3.15 m with the top riser at the cupboard wall.
   What is certain: a landing with a facing wall and dado exists at the top of this flight, and the
   under-stairs door wall (2.07 m door + 0.5 m of boarding/cupboard above) sits under it. If
   `house.json` fixes a different floor-to-floor height, keep goings at 0.24 and adjust the riser.
2. **Stair width 0.84 and the 0.34 m nib** follow the hall width findings (`hallway.md` §10.1); the part
   of the bottom steps behind the nib is never seen — the plan of R1–R3 east of x = 0.65 is inferred.
3. **Shape of the bottom three risers** is read from oblique views (hr_243, f_0248); positions ±0.05 m.
4. **Newel and spindle turnings**: proportions ±10 %; the spindle's base-block lengths are approximate.
5. **Spandrel panel module** (six bays of 0.52 m) is estimated; only the tall bays near the top and the
   two low bays at the foot are clearly seen.
6. **Above the hall ceiling** (stair wall height, landing, upper newel, what the well's edge looks
   like) is largely unseen; treat everything above z = 2.9 as a plausible continuation.
7. **Print subjects** readable only as "small dark boat on pale paper"; sizes ±0.05 m; S3/S4 heights follow the rule, not a measurement.
8. Carpet colour: reads between warm grey and beige depending on the frame; #9C958A is the mid estimate.

---

## Reconciled dimensions (from `spec/house.json`, see `spec/RECONCILE.md` D5)
- Stair recess: x 0.15..0.99, y 4.83..7.58 (0.84 x 2.75); under-stairs door wall y 7.58..7.68.
- Local to global for everything keyed to the nib and newel (R1-R3, newel, wall-string easing, S1):
  x unchanged, y + 2.33. Newel centre (0.20, 5.33).
- Going is 0.23, not 0.24: R4 at y 5.60, Rn at 5.60 + 0.23 x (n - 4), R15 (landing nosing) at y 8.13.
- R13 (y 7.67) is over the under-stairs door wall. R14, R15 and the half-landing (z 2.85, y 8.13..8.73)
  are above the lobby, hidden from below by the overhead cupboard and the 2.60 soffit. The facing wall at
  the top is the arch wall line (y 8.73).
- Corner post at (0.15, 7.63). Spandrel runs y 5.33..7.58: use five 0.45 m bays instead of six 0.52 m.
- Prints S1-S4: keep the rule (1.45 above the nosing line), spaced 0.70 apart from S1 at y 5.13.
- Floor: `house.json` gives the stairs polygon floor `oak_plank` with `covering: carpet_mink_grey` on
  treads, risers and half-landing only. The Z=0 floor in front of the R1 bullnose (x 0.15..0.65, from
  y 4.83 to the R1 arc, including under the newel) is the hall's oak floor, not carpet.

## Round 3 corrections (core owner, from build/rooms2_open.md)
- Foot winders fan from the newel at (0.20, 5.42): R1 bullnose quarter-ellipse centre (0.65, 5.42), semi 0.53 x 0.37;
  R2 to (0.79, 5.19) on the diagonal; R3 to the internal corner (0.99, 5.39); R4 square at 5.60 (landing1.md 11.1,
  v3 f_0011-f_0013). The filmed 55 / 25 degrees cannot be reached with R3 on the internal corner and R4 at 5.60.
- The hall ceiling (Z 2.95) runs flat over the stair foot to a square edge at y 5.60 (house.json stairs ceilingZone
  stair_foot; v1 f_0245, v6 f_0041).
- One carpet for the flight and the first-floor landings: `carpet_silver_beige`, recoloured to #A9A397 (carpet :
  greige band 0.66 on the tread in v3 f_0021, 0.88 on the QL in v6 f_0037).
- Integration (circulation owner, round 3): the main-flight handrail no longer tenons into the top newel at Z 3.75. It
  dies about 25 mm into the underside of a white fascia under the strip capping at y ~7.62 (v6 f_0038; fascia 0.10
  deep, x 0.15..0.22, Z 3.32..3.42 by the strip, 3.13..3.23 by the step). Main spindles past the rail stop 5 mm into
  the fascia (tread 14: stubs).

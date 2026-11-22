# Phase 3 — dimension audit of the vertical stack (`dims_vert`)

Scope: basement, both staircases, the step sets between the split levels, storey heights and ceiling heights.
Footage read: v1 f_0241–0252, f_0739–0780; v3 f_0001–0072; v4 f_0165–0196; v6 f_0001–0050, f_0099–0178,
f_0286–0306; v13 f_0001–0049 (new, silent). Full-resolution stills and gridded crops are in
`reference/work/r3_dims_vert/` (`<video>_t<seconds>.jpg`, `g_*` gridded, `c_*` crops, `o_*` overlays);
the small tools used are in `build/r3/dims_vert/` (`vp.py` vanishing points, `sv.py` cross-ratio heights,
`pitchfit.py` pinhole fit to door leaves, `profile.py` luminance profiles for counting nosings).
Model preview: `build/preview/section_r3dimsvert.jpg`.

**Verdict.** The storey levels in `spec/house.json` hold to about ±0.05 on the ground → first floor chain and
±0.10 above it. Three things do not hold:

1. **The main flight has 14 risers, not 15** (three sharp whole-flight views agree). The quarter-landing level
   2.85 stays, so the rise becomes 0.2036 and, between the same end positions, the going 0.253.
2. **The hall arch is about 0.3 lower than modelled** (corbels 1.72–2.08, crown 2.47; two views, each scaled by
   the 1981 kitchen door leaf that stands beside it).
3. **The rear ground-floor corridor ceiling is lower than the 2.84 that was set by reasoning** (measured 2.6–2.8).

Everything else measured is inside its tolerance (table 3). What could not be settled is listed in section 7.

## 1. Method notes (so the numbers can be re-derived)

- Riser counts: only frames that show a whole flight, or its foot / head with a fixed landmark, were used.
  Nosings were marked on the stills and cross-checked with a luminance profile along the wall string.
- Heights: cross-ratio on one vertical image line with the vertical vanishing point (`sv.height`), reference =
  door leaf 1981 (lining head 1.99 above the floor). Where two door leaves at known plan distances are in one
  frame, camera height, pitch and distance were fitted with a pinhole model (`pitchfit.py`) and other heights
  read at their known depth.
- Focal length of the 1080 x 1920 stills of v1 and v6: **f ≈ 1000–1040 px** (two-door fits; 1017 with f free in
  v6 t50), principal point assumed at the centre. Useful to the other surveyors.
- A warning from this audit: three first attempts gave wrong heights because the reference point and the
  target were not on the same vertical of the same wall plane (door reveal against wall face; near against far
  jamb). Every value below was re-derived after that; the discarded ones are not quoted.

## 2. Riser counts, rise and going

| flight / step set | house.json | counted | frames | confidence |
|---|---|---|---|---|
| `stair_main` hall → quarter landing | 15 x 0.19, going 0.23 | **14** = 3 winders + 11 square (R4..R14) | v1 t242.0, t241.5 (night, low camera, whole flight: nosings T1..T14, T14 is the landing nosing with the landing wall and its dado directly behind); v3 t16.0 / t16.5 (daylight, same view); v3 t19 (11 square nosings above the winders); v6 t37.5 from the landing (12 edges landing..T3, then two winder edges) | high |
| `steps_ql_rear` | 1 | 1 | v3 t35 (riser on the west edge of the landing) | high |
| `steps_rear_front` | 2 | 2 | v4 t175 (two nosings; the dado steps once across them) | high |
| `stair_second` front landing → second floor | 13 = 10 square + 3 winder | **13** = 10 square (R1..R10) + 2 diagonal (R11, R12) + 1 on the landing edge | v4 t175 (foot: bullnose T1 at the newel, ten evenly progressing nosing shadows, the eleventh out of sequence = first diagonal riser at the turning newel); v4 t170.5, t191 and the earlier crop of t192 (eight square nosings T3..T10 below the first diagonal riser, two treads below the frame — the newel base is two risers under the frame edge); v6 t7 from the head (three winder treads, nine straight treads) | medium-high |
| `step_head_platform` | 1 | 1 | v13 t48 | high |
| loft door step | 1 (0.27) | 1 | v13 t48, v5 t163 | high |
| `stair_basement` | 11 = 9 + 2 winder | not recounted to the same standard; five straight risers and the threshold seen from below in v6 t142, the turn from above in v6 t121. The phase-2 count (twice, from above and below) is kept | — | medium (inherited) |

Rise and going:

| item | house.json | measured | how | result |
|---|---|---|---|---|
| main flight rise | 0.19 | **0.2036** = 2.85 / 14 | level chain: the rear first floor (15 risers up) must clear the dining ceiling, 2.75 ± 0.05, by a floor of at least 0.20 → 15 r ≥ 2.95, r ≥ 0.197; the balcony platform read at 2.9–3.1 in the phase-2 rear still agrees | change |
| main flight going | 0.23 | **0.253** = (8.13 − 5.60) / 10 | arithmetic from the unchanged end positions (R4 at y 5.60, landing nosing at y 8.13) | change |
| main flight pitch | 39.6° | 36 ± 2.5° | v1 t242: vanishing point of the nosing line (projective fit to 11 nosings) against the hall's horizontal vanishing point, f 970–1020. The new values give 38.8°; the horizontal vanishing point comes from lines at the frame edge, so this is weak evidence | not used, see 7.1 |
| basement top riser R1 | 0.21 | 0.219 ± 0.012 | v6 t142, cross-ratio on both door jambs against the opening height 1.99 (vertical VP from three verticals) | holds (11 x 0.215 = 2.37 against 2.31 ± 0.12) |
| loft door step | 0.27 | 0.24 ± 0.03 | v13 t48: cross-ratio against the loft door opening in the same wall (VP from five verticals, stable); v5 t163 re-read with the door clear width 0.61–0.67: 0.21–0.24 | holds (difference at the tolerance) |
| platform step | 0.20 | 0.20–0.24 | v13 t48, riser against the 0.80 passage width with pitch correction | holds |
| two steps rear → front | 2 x 0.19 | 0.28–0.40 for both | v4 t175, dado and skirting offsets on the west wall — the two readings disagree | not settled, kept |

## 3. Level chain and ceilings

Door-leaf ratio checks made in this round (reference 1.99 to the lining head; all on the door's own wall or
transferred with the fitted camera):

| level | where | house.json | measured | frames / method | result |
|---|---|---|---|---|---|
| G | hall, front part | 2.95 | 2.90–2.96 (cornice wall edge 2.76) | v1 t778, far jamb of the living-room door, level camera | holds |
| G | dining | 2.80 | **2.75 ± 0.05** (cornice wall edge 2.63) | v1 t740, door opening 740 px, pitch 5° down from the hall vanishing point | holds |
| G | rear corridor (north of the arch) | 2.84 | **2.6–2.8** | v1 t744: cornice band at the utility door 2.43–2.53, wall top over the arch 2.60 (two-leaf fit, residuals ≤ 4 px); v6 t50: cornice on the dining-door wall 2.65 (wall edge) to 2.78 (ceiling edge) (two-door fit, f free) | change, low confidence |
| G | lobby strip west of the stair (y 8.13–8.73, x < 0.15) | 2.84 | 2.59 (cross-ratio, dado 0.965) or 2.75 (level camera) at the west wall, v1 t768; v1 t752 shows this strip's ceiling running on from the front hall with no step, and a separate lower soffit with its own cornice over x > 0.15 | not settled |
| G | hall arch | springing 2.40, crown 2.75, corbels 2.02–2.40 | **corbel top 2.01–2.16, corbel bottom 1.72–1.86, crown 2.50 ± 0.06** | v1 t744 (from the north; kitchen leaf 0.25 beyond the arch): 2.14–2.16 / 1.85 / 2.50; v6 t50 (from the south; kitchen leaf beside the arch): corbel shelf 2.01, scroll 1.85, lowest drop 1.72 | change |
| 1 | front landing | 2.35 | 2.31 (hood top 2.26) | v6 t13, green door, cross-ratio | holds |
| 1 | rear corridor | 2.45 | 2.44–2.55 | v3 t53, blue door at the end + arch plane, constrained by arch width ≤ corridor width | holds |
| 2 | platform / hallway | 2.40 over the platform, 2.60 over the hall | 2.14 ± 0.02 above the loft threshold = 2.38–2.41 above the platform | v13 t48, cross-ratio on the loft door wall | holds |

Chain with the corrected riser count (levels unchanged):

| step | risers x rise | from → to | ceiling below + floor zone |
|---|---|---|---|
| hall → quarter landing | 14 x 0.2036 | 0 → 2.85 | lobby soffit 2.60 + 0.25 |
| → rear first floor | 1 x 0.19 | 2.85 → 3.04 | dining 2.75–2.80 + 0.24–0.29; rear corridor 2.6–2.8 + 0.24–0.44 |
| → front first floor | 2 x 0.19 | 3.04 → 3.42 | hall / living 2.95 + 0.47 (the deep apron is visible in v6 t13) |
| → second floor | 13 x 0.20 | 3.42 → 6.02 | front landing 5.75 + 0.47 to the platform 6.22; rear corridor 5.49–5.59 + 0.43–0.53 |
| → platform | 1 x 0.20 | 6.02 → 6.22 | — |
| → loft | 0.27 (measured 0.24 ± 0.03) | 6.22 → 6.49 | green bedroom 6.27 + 0.22 (not re-measured) |
| second-floor ceiling | — | 8.62 | 2.60 above 6.02, confirmed at the loft door wall |

The first three risers above the quarter landing are still 0.19 in the spec while the flight below is now
0.2036. Equal risers would put the rear floor at 3.05 and the front at 3.46; the evidence does not
distinguish, so they stay.

Headroom with the new main flight (soffit taken 0.27 under the nosing line): basement stair under the main
flight 2.15 at the door, 2.4 at mid flight, 2.6 at the turn; main flight under the front landing (soffit 3.17)
2.15 at y 6.06 (tread 5, Z 1.02; was 2.03 on tread 6); under the second flight 2.17–2.30. The basement door
head (2.03–2.06) still clears the flight: the soffit at y 7.60 is 2.15. The overhead cupboard (Z 2.33–2.59,
y 7.92–8.13) now sits under tread 13 (Z 2.646, y 7.877–8.13) — the same clearance as under the old tread 14.

Exterior: not measured in this round. The phase-2 rear still (`spec/phase2/rear_elevation.md`: balcony
platform 2.9–3.1, balcony door head 5.3–5.4, second-floor sill about 6.30, wall top about 8.55, each ± 0.15–0.25)
agrees with the first-floor level and is 0.15–0.3 low for the second floor and roof (a sill 0.28 above a 6.02
floor is unlikely; the wall top should be above the 8.62 ceiling). That is inside its stated tolerance but
it is the one piece of evidence that pulls against the second-floor level.

## 4. Proposed spec changes

| id | where in house.json | present | proposed | confidence |
|---|---|---|---|---|
| vert-01 | `stairs[stair_main]`: `risers`, `straightRisers`, `rise`, `going`, `walk.risers`, `notes` | 15, 12, 0.19, 0.23, R4..R15 at 5.60 + 0.23 k | 14, 11, 2.85 / 14 = 0.2035714286 (store it to ten places: the validator wants risers x rise = 2.85 to 1e-6), 0.253, three winder lines unchanged then R4..R14 at y 5.600, 5.853, 6.106, 6.359, 6.612, 6.865, 7.118, 7.371, 7.624, 7.877, 8.130 | high (count), medium (rise / going split) |
| vert-02 | `features[hall_arch]`: `springing`, `crown`, `corbelSize.z` | 2.40, 2.75, [2.02, 2.40] | 2.08, 2.47, [1.72, 2.08] | medium |
| vert-03 | `rooms[hallway].ceilingZones[rear_hall].z` for the corridor north of the arch wall (y ≥ 9.03); the strip y 8.13–8.73 is not settled | 2.84 | 2.70 (range 2.60–2.80) | low |

Knock-on of vert-01: `toZ`, `landingZ`, `lastRiserY`, the winders and every floor level are unchanged.
Tread n is at Z 0.2036 n; the raking dado on the 45-degree face now climbs two risers of 0.2036 (0.965 →
1.37); the note of `lobby_cupboard_interior` should say tread 13 (Z 2.646); `docs/test/geom.test.mjs` line
159 hard-codes the 15-riser flight (`2.85 * (8 + 0.11 / 0.23) / 14`) and must follow; `spec/rooms/stairs.md`
reconciled section; plan sheet stair symbol (label "UP 15R" → 14R). Spindles: two per tread on ten straight
treads (T4..T13).

Knock-on of vert-02 / vert-03: the arch crown has to stay under the ceilings either side (2.47 under 2.70);
`hall_pilaster_s` (y 8.53–9.88) should stop at the lower ceiling where it stands under it; the corridor cornice,
the utility and dining door heads (2.06) and the first-floor rear floor (3.04, floor zone 0.34) are not
affected.

## 5. Inventory (what the footage shows against the model)

- **Main flight**: one riser too many in the model; each step should be 14 mm higher and 23 mm deeper. The
  bottom three treads are winders as modelled; the fourth riser is the first square one. Carpet, string and
  balustrade unchanged. Frames: v1 t242, v3 t16.5.
- **Hall arch** (lobby ↔ rear corridor): the corbel shelf is level with the top of the open kitchen door leaf
  (within 0.05–0.15), not 0.4 above it; in the model it sits at 2.40. Three-part corbel on each jamb: moulded
  shelf (top about 2.05), scroll under it (to about 1.85) and a small drop (to about 1.72) — v6 t50, v1 t744.
- **Rear corridor ceiling**: lower than the front hall; with the arch crown at about 2.5 there is only about
  0.15–0.25 of wall over the crown on the corridor side (v1 t744), as the phase-1 hallway note already said.
- **Lobby**: the lower soffit over x > 0.15 carries its own dentil cornice along x = 0.15 (v1 t752); the strip
  west of it has the smoke alarm and downlights on a higher ceiling. Modelled so; heights of the strip not
  settled.
- **Second flight**: as modelled. Both diagonal risers start at the turning newel; the first one sits directly
  above the tenth square riser at the newel (v4 t170.5).
- **Second-floor platform** (v13 t48): turning newel cap about 1.05 above the platform (model 1.20), handrail
  about 0.95–1.0; dado steps up by the riser beside the step with a short ramp; loft door frame fills the
  platform width; ceiling line 0.15 above the loft door lining head.
- **Basement stair** (v6 t142): door opening seen from below, threshold nosing, R1 full width of the opening,
  ledge on the east wall, extinguisher on the west wall by the door — as modelled.

## 6. Notes per unit

- **stairs**: rebuild from the corrected `stair_main` (14 risers, rise 0.2036, going 0.253, R4..R14 at the y
  values of vert-01). Winder lines unchanged. Pitch 38.8°: string, raking dado, spandrel top and handrail
  follow it. Ten straight treads carry twenty spindles. Check the top newel and the handrail junction again:
  tread 13 is at Z 2.646 and the landing at 2.85.
- **stairs2**: no change. 13 risers confirmed. Its going (0.23) now differs from the flight below (0.253); see
  7.1 before moving anything.
- **landing1**: front landing ceiling 2.31–2.35 and rear corridor 2.45–2.55 confirmed. Riser counts 1 and 2
  confirmed. See 7.3 for the depth of the bay behind the arch.
- **hall**: lower the arch and its corbels (vert-02); corbel = shelf + scroll + drop, total about 0.36 high.
  Rear corridor ceiling as vert-03 if the reconcile accepts it; the cornice and the pilaster follow.
- **shell**: flight carcass of `stair_main`; `rear_hall` ceiling zone; arch feature. The hall cornice bulkhead
  at the lobby stays.
- **basement**: no change. Top riser 0.22 ± 0.01 measured against the door; plan, headroom (2.00) and plant
  positions were not re-surveyed in this round.
- **dining**: ceiling 2.75 ± 0.05 measured against the hall door; 2.80 stays.
- **loft_office / eaves**: loft door step measured 0.24 ± 0.03 against 0.27; floor level stays at 6.49.
- **bathroom2, purple_room, study**: second-floor ceiling 2.60 confirmed at the loft door wall only; the rooms
  themselves were not measured.

## 7. Open questions

1. **Going of the two flights.** With 14 risers between unchanged ends the main flight's going is 0.253; the
   second flight, stacked in the same well, has 0.23 (its foot at y 6.06 was itself derived from an assumed
   0.23). They should be equal. A common 0.24–0.25 needs one end to move by 0.1–0.2 (main flight R4 at about
   5.73, or second flight R1 at about 5.85–5.97, which shortens the front landing from 1.11 to 0.9–1.0 and
   brings the first treads under the 5.77 landing ceiling). The pitch measured in v1 t242 (36 ± 2.5°) would
   rather suggest a longer going or a lower rise; it is not reliable enough to act on. One riser and one going
   measured with a tape would settle this and the absolute storey height.
2. **Riser height above the quarter landing** (0.19 kept for three risers against 0.2036 below).
3. **First-floor bay behind the arch** (plan, not height): in v3 t53 the arch is 295 px wide where the blue
   door wall behind it is scaled at 208 px/m. An arch no wider than the corridor (≤ 1.0 m) is then at least
   1.3 m in front of the door wall; the model has 0.89. The short wall between the yellow door and the arch
   argues the other way. Needs the landing surveyor.
4. **Lobby strip ceiling** (y 8.13–8.73, x < 0.15): 2.59, 2.75 or the front hall's 2.95.
5. **Rear corridor ceiling**: the two views give 2.6 and 2.78.
6. **Second-floor level against the rear elevation** (sill and wall top 0.15–0.3 low in the phase-2 still). Not
   re-measured; the brick wall across the side passage (v13 f_0022–0038, courses clearly resolved) would give
   the height of the lilac-room window above the passage if someone counts the courses.
7. **Not done in this round**: basement plan, headroom and plant positions; stair widths; handrail heights on
   the two flights; kitchen, living, wc, utility, bedrooms and second-floor rooms' ceilings; any exterior
   measurement.

## Verification

Verifier pass on `vert-01` .. `vert-03`. Each item was measured again before reading sections 1-7, on stills the
survey did not use: v3 t15.5 / t16.37, v2 t520.5 / t520.9, v1 t751.33 / t774.0 / t776.25 (stair); v6 t303.1,
v2 t499, v2 t514.8 / t515.6 (arch and corridor). Scratch (private): `reference/work/r3_dims_vert_v/`; scripts in
`build/r3/dims_vert_v/` (`lsd.py` line segments, `vpfit.py` vanishing points and self-calibration, `hts.py` /
`plane.py` cross-ratio heights in a wall plane, `resect.py` camera from plan points). Focal length from each
frame's own orthogonal vanishing points came out 790-915 px (the two-door fits of section 1 gave 1000-1040);
results are quoted over that spread where they depend on it. A scratch copy of `house.json` with the three
verdicts applied passes `validate_house.py --no-draw`, and a foundation + hallway + stairs preview from it builds
(BUILD OK, tag `r3dimsvertv`).

| id | verdict | value to use | my measurement (reference, frames, ratio, result) |
|---|---|---|---|
| vert-01 | **accept** | as proposed: `risers` 14, `straightRisers` 11, `rise` 2.85 / 14, `going` 0.253, R4..R14 at y 5.600 .. 8.130; levels, `landingZ`, `lastRiserY`, winders unchanged. The end positions themselves are doubtful: see note 1 | **Count 14.** (a) Foot views v3 t15.5 and t16.37: luminance edges up the middle of the flight at y 187 (landing edge, wall above it), 235, 290, 352, 419, 496, 580, 671, 779, 887, 1000 px = eleven square nosings, spacings 48 .. 113 px growing steadily (no room for a hidden one), plus three winder nosings below. (b) Independent of the foot view: the hall side is a cut string; v2 t520.5 and t520.9 show **ten** tread-end returns between the bottom newel and the corner of the basement-door wall (T4..T13; the lowest one abuts the newel and stands about four risers above the floor in v1 t776.25). 3 winders + 10 square treads + landing = 14 risers; 15 would need eleven returns. **Landing level 2.85 holds, so the rise is 0.204.** v1 t751.33, cross-ratio in the plane of the string: floor line of the spandrel skirting, top of the basement door leaf (1.99) carried to the corner, vertical vanishing point. Top five returns at Z **2.66, 2.46, 2.26, 2.07, 1.85** (mean step 0.202); the same solution returns the hall ceiling at the corner as 2.95, and interpolating between leaf top and that ceiling instead gives 2.63-2.68 for the top return. 13 x 0.2036 = 2.647; 13 x 0.19 = 2.47 is excluded. This matters because the argument for the rise in section 2 (dining ceiling 2.75 + floor) is weakened by the `dims_G` verification (dining ceiling 2.62). **Going**: no direct measurement possible. Pitch of handrail / string / panel rails against the tread-end edges and the balusters, v1 t774.0 (close side view, the best conditioned): **38.6 deg** (37-39 for f 800-850); v2 t520.5 37-39, v1 t751.33 35.5-37; a second construction on the two grazing frames gives 40.6-42.4. So 36-42 deg: compatible with the proposed 38.8, weak against 41.5 (14 risers with the going left at 0.23). Accepted as the consequence of the count between the present ends. |
| vert-02 | **adjust** | `springing` **2.08** (as proposed), `crown` **2.55**, `corbelSize.z` **[1.75, 2.08]** (height 0.33). `openings[a_hall]` carries the same `springing` / `crown` / `height` and must follow | **Corbel shelf top 2.06 +/- 0.03.** v6 t303.1 from the lobby: the top of the open kitchen leaf (1.99, beside the arch) and the head of the dining door opening 3.6 m behind it lie on the same image row within 7 px, so the lens is at 1.99-2.00 and heights near that level hardly depend on distance: shelf top 2.04-2.08, lowest point of the corbel 1.82-1.90 for a camera 0.45-0.9 m from the leaf. v2 t499 from the north (kitchen leaf top and basement-door leaf top as the two references): shelf 2.07-2.10, bottom 1.77-1.83. **Corbel height 0.28-0.34** in two frontal daylight frames (v2 t514.8, t515.6), arch plane rectified with the vertical and hall vanishing points and scaled by the 0.94 between the feet of the arch (both shelf tops come out level to 0.005): lowest points 0.30 (east) and 0.34 (west) below the shelf top. Bottom 1.72-1.86 over the three views; 1.75 used. **Crown 0.53-0.55 above the shelf top** in the same two frontal frames (0.49-0.51 if the scale is taken from the 1.10 corridor width between the walls that carry the corbels) = **2.57-2.63**; from the close frame v6 t303.1 2.40-2.55 (distance dependent, weak); the single view of section 3 gave 2.50-2.52. A semicircle on the 0.94 span from 2.08 gives 2.55, which is inside all three and leaves 0.15 of wall under the 2.70 corridor ceiling (v2 t499 shows a strip of that order). The present 2.40 / 2.75 is outside everything. |
| vert-03 | **accept** | `rear_hall` zone split at the arch wall: corridor y 9.03..12.23 at **2.70**; the part south of it (y 8.13..9.03) keeps 2.84 until measured | The dining door stands in the corridor's north wall, so the reference is in the wall being measured. v2 t514.8: cross-ratio up the west jamb, floor at the lining foot (y 1747 px), lining head 1.99 (1230 px), vertical vanishing point from the door frames: lower edge of the cornice on that wall **2.60**, wall / ceiling line **2.71** (2.68-2.74 over the vanishing-point range; +/- 5 px on the head moves it 0.03). v2 t515.6, camera moved: **2.61 / 2.71**. Checks in both frames: architrave top 2.08 (model 2.06), clock centre 2.33-2.34. The low reading of section 3 (2.43-2.53 at the utility door, v1 t744) is not supported; its v6 t50 reading (2.65-2.78) is. First-floor rear floor 3.04 then has 0.33 under it. |

### Notes for the reconciler

1. **Where the main flight stands (open, outside the proposals).** The riser table of vert-01 keeps the present
   ends (R4 at 5.60, landing nosing at 8.13). The footage does not agree with the top end: on the hall side the
   top tread T13 (measured at Z 2.66, one riser under the landing) is visible on the string right up to the corner
   of the basement-door wall (v2 t520.5, v1 t751.33), so the landing nosing is within about 0.15 of that corner
   (y 7.68 in the model), not 0.45 north of it. With the proposed table the model shows T4..T11 complete on the
   spandrel and hides T12 and T13 above the cupboard; the real spandrel shows T4..T13. The first-floor survey
   reached the same line from above (`dims_1` item 11 and verification -10: quarter landing 1.04 +/- 0.06 deep,
   nosing at about 7.69 if the north wall stays at 8.73), and the overhead cupboard looks shallow from below (its
   underside is a thin strip in v1 t751.33; the hall spec had 0.35 before RECONCILE D5 stretched it to 0.45 from
   the 15-riser arithmetic). Ten goings then have to fit between R4 and about 7.7: either the going is 0.21-0.22
   with the foot where it is, or the going stays near 0.25 and the newel, winders and 45-degree face sit about
   0.4 further south. The second reading has more behind it: the pitch above; newel face to door-wall corner
   2.5-2.8 in the calibrated frame v1 t751.33 (grazing view, +/- 0.25) against 2.26 modelled; and `dims_G` open
   question 1 (bullnose read nearer the inner doors). Neither is good enough to move walls. Whoever takes the
   hall Y chain should treat the flight, the lobby soffit zones, the cupboard, the quarter landing and the well
   of the second flight as one block that probably moves south together.
2. **vert-01 knock-ons** as listed in section 4 (geom test line, cupboard note, dado rake 1.37, plan label,
   `stairs.md`). Two spindles per tread on T4..T13 is right (v1 t776.25: two on each full return).
3. **Arch, plan detail (not proposed).** In the frontal frames the corbels are fixed to the side walls, the
   walls are about 0.09 outside the feet of the arch on each side (1.12-1.21 wall to wall for 0.94 between the
   feet), and the arch soffit lands on the shelves near their tips; the shelf is about 0.14-0.16 wide and 0.07
   thick. The model puts the corbels inside a 0.94 opening with 0.72 between their tips.
4. **Lobby strip** (y 8.13..8.73, x < 0.15) and the arch-wall zone were not measured; in v1 t751.33 the passage
   ceiling runs on over the strip without a visible step, as section 3 says, which the 3.04 floor above does
   not allow at 2.95. Left at 2.84.

Not settled by me: the going (pitch only, 36-42 deg); the Y position of either end of the flight; the crown to
better than +/- 0.06; basement, stair widths, handrail heights and the second flight were not re-measured.

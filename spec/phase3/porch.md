# Phase 3 survey — porch: street doors, canopy, vestibule

Surveyor notes for round 3. Area: the outer door set, threshold, canopy, and the vestibule interior
(`rooms.vestibule`, `d_street`, `d_inner`, `w_bay_cheek_w`, the porch lean-to).
Frame of `spec/BRIEF.md`: metres, +Y from the street door into the house, +X to the right, Z up, origin at the
inside face of the street-door threshold. Nothing here names the street, the house number or a number plate.

## 0. What was looked at

| footage | frames read | used for |
|---|---|---|
| v9 (all 68 frames, plus 129 full-res stills at 2 fps, t 3–67 s) | f_0001–0068 | everything |
| photo `vestibule_front_door_open` (3072x4080) | whole + 5 crops | inside of the east leaf, handle, corner with the cheek wall |
| v8 f_0102–0138 (plus 75 full-res stills, t 100–137 s) | all | door set from the path, canopy, eaves, porch roof, west cheek |
| v1 f_0001–0061 (re-read), stills t 1.0, 25, 28–30 s | all in sheets, 6 singly | tile counts, inner doors, night views of the door set |
| v2 f_0880–0960 (re-read), stills t 899.5, 903.2 s | all in sheets, 9 singly | ceiling of the front recess, switch plate, tile count from the hall |

Current model: `build/preview/vestibule_*_r3porch.jpg`, `front_{door,canopy,facade}_r3porch.jpg`,
`elev_front_r3porch.jpg` (BUILD OK, no Traceback), `docs/renders/vestibule_inner.jpg`, `front_street.jpg`.

## 1. How the measuring was done, and how far it can be trusted

- **Single-frame focal length is not recoverable.** A rectangle of known shape (one 3x3 floor tile, v1 t30)
  comes out 5–8 % off square, and the leaf glazing gives f 900–1470 px depending on the frame: the video is
  electronically stabilised, so the principal point is not the frame centre. Nothing below relies on f.
  Straight edges fit to 0.1–0.3 px rms over 500–800 px, so lens distortion is negligible.
- **Heights** are cross-ratios along one vertical line (vanishing point from fitted vertical edges, checked
  against the two equal intervals between the three glazing bars), **widths** are ratios along one horizontal
  line in a frontal far view (v9 t12, camera about 9 m away) or along the threshold line.
- **Unit P.** Inside the door set everything is expressed in P = the vertical pitch of the leaf glazing bars.
  Proportions in P agree between frames to about 1.5 %.
- **Absolute size of P**, four routes:

  | route | P (m) | note |
  |---|---|---|
  | floor tiles: west half-opening at the threshold = 5.5 cells (v9 t20, v8 t106), cell 0.110 | 0.226 | model units (cell size rests on the 1.30 m vestibule width) |
  | outside: frame east edge to the first bay light = 2.28 P, frame 5.80 P, bay light at x 1.25, west reveal 0.02 | 0.233 | model units |
  | lever spindle level with the dado top 0.965 at the door (v1 f_0012), spindle 3.96 P above the threshold | 0.236 | model units, +-0.008 |
  | lever set: backplate / PZ = 2.66, screw centres / PZ = 2.38 in the photo = the common 92 PZ / 215 / 240 set; backplate = 1.00 P | 0.240 | hardware, independent of the model, +-0.004 |

  **Adopted: P = 0.232 m (model units), tolerance +-0.006.** The hardware route is 3.4 % larger. That is
  inside the combined tolerance, so no change of the house scale is proposed, but see open question 1.
- Tile cell: 0.110 m as in `vestibule.md` (re-checked: 11–12.4 cells across the rear recess).
- Paving: three sizes in ratio 3 : 4 : 6 in courses, the threshold opening = 8.0 "4"-stones: 160 mm course
  family (as `exterior.zones.forecourt` already says), not the 134 / 140 mm families.

## 2. Inventory — what the footage shows against the model

### 2.1 Street door set (`d_street`), from outside and inside
Frames: v9 f_0005–0007, f_0013 (t12), f_0017–0020, f_0043–0048, f_0059–0060; v8 f_0104–0106, f_0126–0129; photo.

| item | model now | footage |
|---|---|---|
| proportion leaf width : door height | 0.59 : 2.00 (0.295) | sash width / opening height 0.338 (v9 t12: 98 px / 289.5 px; v8 t105 agrees) — the modelled door is too slender by 11 % |
| frame, outer | 1.24 x 2.57 | 5.80 P x (10.26 P + 0.10) = **1.345 x 2.48**; fills the wall from the party wall to the corner with the cheek wall |
| leaves | 2 x 0.59, z 0.03–2.03 | 2 x **0.63** (2.715 P), hanging from z -0.04 to 1.905; head underside (top of the opening) **1.89** |
| glazing per leaf | 3 x 4 panes, 0.44 x 1.00, z 0.95–1.95 | **3 wide x 4 high confirmed** (seven frames and the photo; the task text says 3x3, that is wrong). Aperture 0.41 x 0.94, z **0.865–1.80**; bars 16 mm, inside the sealed unit, vertical pitch 0.232 (bottom pane about 5 % taller), horizontal pitch 0.137; glass obscure "stippled", white 20 mm beads |
| stiles and rails | 70 mm | hinge stile 0.095, meeting stile 0.125 (one leaf carries the astragal), top rail 0.105, mid rail zone 0.72–0.865, bottom rail to -0.04 |
| lower panel | 0.44 x 0.68, z 0.16–0.84 | flat panel with a raised moulding frame, outer 0.46 x 0.62, z 0.10–0.72 |
| transom bar zone | 2.03–2.12 | 1.89–2.045 (0.155: head of the leaves + transom member + bead) |
| transom light | 1.10 x 0.38, z 2.12–2.50 | **1.216 x 0.367** (5.24 P x 1.58 P), z 2.045–2.41; one fixed pane, acid-etched; keep it plain frosted (privacy) |
| lever handles | z 1.02, backplate 240 x 30 | spindle z **0.95**, backplate 232–240 x 30, top 0.09 above the spindle, cylinder 0.09 below, 0.055 from the meeting edge, levers 0.115 pointing to the hinge side; polished brass, both leaves, both faces |
| letter plate | west leaf, z 0.90 | west leaf, on the mid rail, centre z **0.80**, 0.30 x 0.07, polished brass frame and flap outside, brass flap inside |
| hinges | not modelled outside | three white flag hinges per leaf on the outer jambs, covers 0.115 high x 0.035 wide x 0.03 proud, centres z about 0.20, 0.97, 1.70 (v9 f_0044, f_0046; v8 t105) |
| keeps on the head | two hoods | as modelled: one white block about 0.11 x 0.03 on the head over each leaf, 0.10 from the meeting stile (photo) |
| side lights | — | **there are none**: two leaves and one transom light only. The "side windows" are the two lights in the bay cheek wall inside (2.3) |
| swing | outward, about 100 deg | confirmed, both leaves (v9 f_0005–0020, f_0042; photo) |
| threshold | 0.03 upstand, step 0.06 | low aluminium threshold strip on a white cill; inner upstand about 0.03 above the tiles; outside the cill face is about 0.07 above the setts; the leaves overlap the cill, their bottom edge 0.02–0.03 above its nose (v9 f_0021, f_0058–0060; v8 f_0107–0108). Paving -0.06 stays |
| colour | #F4F4F0 | white uPVC: #ddd8cd in sun (photo), #d6d6d8 in shade (v9 t20); true #F4F4F0 stays. Cill #e0ded8. Brass: polished, yellow, as modelled |

### 2.2 Canopy = the eaves of the lean-to (envelope)
Frames: v9 f_0013 (t12), f_0045–0052; v8 f_0112–0116, f_0126–0129; v2 f_0912, f_0915 (through the transom).

- The eaves are **low**. From 9 m the gutter crosses the top of the transom light and hides its upper 0.06 m
  (visible glass 1.32 P against 1.58–1.61 P from 1.3 m and 3 m; the three numbers agree only for an edge at
  z 2.33, 0.55 in front of the door). Gutter (white square-line, 114): **z 2.33–2.45**, y -0.62 … -0.73.
- The soffit meets the head of the door frame just above the transom light (z about 2.54) and drops to the
  fascia (about 2.31): it is **raked with the roof, not flat at 2.62**. White boards parallel to the door,
  three recessed downlights in one row (v2 f_0915 shows all three through the glass), white bezels about
  0.09–0.10; the west one looks larger and domed in v9 f_0049 (possibly a sensor light).
- Roof: dark blue-grey slate, **pitch about 27 deg** (far view: top of slate 2.46 at the gutter, 3.13–3.25 at
  the abutment; two camera distances give 25–30 deg). The model has 38.5 deg from 2.85 to 3.90.
- West end: stop end, running outlet, two offset bends back to the wall, 65 mm square white downpipe on the
  front face of the white strip between the door frame and the party line, centre x about -0.78, shoe at
  z 0.12 over a small gully in the setts (v9 f_0052–0056). The model has it at x -0.68.
- West flank of the porch: plain white render, exposed for about 0.45 m back from the front plane before it
  meets the neighbour's brick pier; the roof verge above it has a white boxed bargeboard (v8 f_0126–0128).
  The plaque on that pier belongs to the neighbour: omit.
- East of the door: reeded pilaster (0.43 wide: three flat reeds, plinth, the flag bracket above head
  height); slim black video doorbell about 0.115 x 0.048, centre (0.80, z 1.30) on the pilaster face.

### 2.3 Vestibule interior
Frames: v9 f_0021–0041; photo; v2 f_0903, f_0910–0927, t899.5; v1 f_0012, f_0026, f_0031, t25, t30.

1. **Front recess is deeper.** Tile rows from the street threshold to the south face of the piers, counted in
   three clean frames (v9 t20 from the south, v9 t57 from outside, v1 t25 from above):
   K (cut to 0.9), U, K, K, U, K, K, U, K = **8.9 cells = 0.98 m**. `vestibule.md` has 6.7 cells (0.74): it
   missed the cut dark row at the threshold and one more row. From the inner sill: U, K, K, U, K, K, U, K
   to the pier's south face = 8 cells. Total between the thresholds **16.9 cells = 1.86 m** (was 15.7, 1.73).
2. **The door frame stands in the corner with the cheek wall.** The dado stub seen beside the east jamb
   rises towards the door while the door's own horizontals fall towards it (photo; v9 f_0036–0039): the stub
   is on the cheek wall, not on a return of the front wall. There is no 0.28 m front-wall return. So the
   cheek wall's vestibule face is at the frame's east edge plus cover strips: **x about 0.71**, not 0.90.
3. **Cheek-wall lights sit next to the pier**, not next to the door: north architrave about 0.05 from the
   pier, then the lights, then about 0.30 of plain wall with the dado stub to the corner. Dado stub on the
   cheek wall from the lower light's architrave to 0.04 short of the corner, returned end; skirting likewise
   (behind the shoe rack). In the corner two white vertical strips (a flat cover board about 0.07 and a
   beaded strip about 0.035) between the plaster and the uPVC frame.
4. **Front-recess ceiling is the underside of the lean-to**: it starts just above the door frame (no band of
   wall over the frame: v9 f_0038–0039, v2 f_0912, f_0915, f_0919), rises at the roof pitch and turns flat
   before the arch wall with a soft crease (v2 f_0915, f_0923; v9 t31.5 looking straight up). The flat part
   meets the arch wall just above the archivolt. West junction with the party wall: a sharp line rising with
   the slope. East junction over the upper light: a soft cove, radius about 0.12. There are no separate 45
   degree haunches along the side walls: the two "creases" of round 2 are the wall line and the crease
   between slope and flat. Owner's words at v2 f_0907–0916 ("this is about 45 degree angle … can you work
   out the angle"): the slope is about 27 deg.
5. Two downlights, both in the sloping part, side by side (v9 t31.5), about (-0.30, 0.30) and (0.32, 0.30),
   white bezel 0.085–0.09, gimbal lamp.
6. Arch, imposts, archivolt, piers with dado and skirting returns, rear recess, keypad and switch, stool,
   lantern: as modelled. Archivolt band reads about 0.15 wide with a roll on its outer edge (v9 f_0029–0031).
   The alarm keypad is 1.85 x the width of the 86 mm switch plate below it (v2 t903.2), i.e. about 0.16 x
   0.11, slightly larger than modelled; keep it blank (no logo).
7. Inner doors (`d_inner`): confirmed in daylight — 2 x 5 panes per leaf, one clear transom pane, brass
   levers on long plates, brass butts, west leaf standing open into the hall. No change.
8. Tiles in daylight: dark cells read charcoal (#2a2b30 in shade, v9 t20), not brown-black; white, taupe
   triangles and blue-grey squares as specified. Registration, see section 4.
9. Door mat: same mat as modelled, but it runs from 0.04 behind the threshold to the third pattern row
   beside the pier: **0.60 x 1.10** (a standard size), x -0.44 … 0.16, y 0.04 … 1.14.
10. Clutter still hides the east pier below 2 m and the floor of the front recess on the east (coats, a
    four-tier honey-coloured slatted shoe rack about 0.70 x 0.27 x 0.75 against the cheek wall under the
    lower light, umbrellas). Leave out; the rack is optional.

## 3. Dimension table

Model units (cell 0.110, P 0.232). "tol" is one sigma.

| # | item | house.json | now | measured | tol | method | conf. |
|---|---|---|---|---|---|---|---|
| 1 | door pair width (2 leaves) | `openings.d_street.width` | 1.18 | 1.26 | 0.03 | sash 2.715 P each, v9 t12 profile; tiles 5.5 cells per half | high |
| 2 | frame outer width | `d_street.notes` | 1.24 | 1.345 | 0.035 | 5.80 P (v9 t12), 11.9 tile cells (v9 t20, v8 t106) | high |
| 3 | door centre x | `d_street.center[0]` | 0 | -0.02 … +0.02 | 0.03 | tiles: west wall to meeting stile | no change |
| 4 | top of the leaves (head underside) | `d_street.height` | 2.03 | 1.89 | 0.05 | 8.02 P above the threshold top (v9 t12, t18; v8 t105) | medium |
| 5 | transom light top | `d_street.transom.height` | 2.50 | 2.41 | 0.06 | 10.26 P (v8 t105 with vanishing point, v9 t18) | medium |
| 6 | transom light bottom | notes | 2.12 | 2.045 | 0.05 | 8.68 P | medium |
| 7 | frame top | notes | 2.57 | 2.48 | 0.06 | light top + 0.07 | medium |
| 8 | lever spindle | `vestibule.md` | 1.02 | 0.95 | 0.03 | 3.96 P; level with the dado top in v1 f_0012 | medium |
| 9 | leaf glazing z | `vestibule.md` | 0.95–1.95 | 0.865–1.80 | 0.03 | 3.60 P, 7.64 P | medium |
| 10 | threshold step to the paving | `exterior.steps.street_threshold.rise` | 0.06 | 0.06–0.08 | 0.02 | cill face in v9 t12, t58 | no change |
| 11 | front recess depth (threshold to pier south face) | `rooms.vestibule.polygon`, `features.vest_pier_*` | 0.74 | 0.98 | 0.04 | 8.9 tile cells, three frames | high |
| 12 | pier depth | `features.vest_pier_*` | 0.55 | 0.44–0.55 | 0.06 | 4–5 cells (v1 t25) | no change proposed alone |
| 13 | rear recess depth | polygon | 0.44 | 0.33–0.44 | 0.06 | 3–4 cells (v1 t25); switch plate gives 0.45–0.49 | no change |
| 14 | depth between the thresholds | polygon, `w_screen_inner` | 1.73 | 1.86 | 0.07 | 16.9 cells | medium |
| 15 | vestibule width at the rear recess | polygon | 1.30 | 11–12.4 cells | — | re-count only | no change |
| 16 | front recess east wall (cheek face) | polygon, `w_bay_cheek_w` | 0.90 | 0.71 | 0.05 | frame east edge 0.672 + cover strips; corner seen in the photo and v9 f_0036–0039 | high for "at the frame", medium for the value |
| 17 | cheek lights, centre y | `openings.w_bay_cheek_w.center[1]` | 0.37 | 0.63 | 0.06 | 0.05 from the pier at 0.98, 0.075 architrave | medium |
| 18 | cheek lights, glass width | `w_bay_cheek_w.width` | 0.50 | 0.40–0.50 | 0.05 | against the 75 mm architrave, v9 f_0025 | low |
| 19 | ceiling of the front recess at the door | `ceilingZ`, `features.vest_haunch_*` | 2.85 flat, haunch from 2.63 | 2.54 | 0.06 | frame top + 0.05 (v9 f_0038, v2 f_0915) | medium |
| 20 | flat part of that ceiling | same | 2.85 | 2.85, for the last 0.36 before the arch wall | 0.08 | meets the arch wall just over the archivolt (v2 f_0923); width from v9 t31.5 | medium |
| 21 | slope between them | — | — | 27 deg (0.31 over 0.62) | 4 deg | 19 + 20; roof pitch outside 25–30 | medium |
| 22 | gutter | envelope | eaves 2.85 | 2.33–2.45 | 0.05 | v9 t12, occlusion of the transom at 9 m against 3 m and 1.3 m | medium-high |
| 23 | porch roof | `roof.planes.porch_leanto.z` | c0 3.3111, cy 0.795 (38.5 deg, 2.85 → 3.90) | c0 2.76, cy 0.50 (26.6 deg, 2.46 at y -0.60 → 3.13 at y 0.74) | 0.08, 4 deg | v9 t12 | medium |
| 24 | canopy soffit | `envelope.PORCH_SOFFIT_Z` | 2.62 flat | 2.54 at the door head → 2.31 at the fascia | 0.06 | 22 + 7 | medium |
| 25 | inner doors | `d_inner` | 1.22 x 1.981, transom 2.79 | not re-measured (daylight views agree in proportion) | — | — | no change |

## 4. Floor tile registration (shell)

- Along Y, from the street threshold: a dark K row cut to 0.9 cell (y 0 … 0.10), then the blue-square rows
  centred at y **0.155, 0.486, 0.817, 1.148, 1.479, 1.810**, two dark rows between each; the row at the inner
  sill is a full blue-square row (v1 f_0031). (`vestibule.md` has the blue rows 0.13 further south and the
  threshold row as a cut blue row.)
- Along X: the north–south tile joint nearest the party wall is 0.4 cell from it at the street door (v9 t20,
  v8 t106) and 0.8 cell at the rear recess (v1 t30): blue-square columns centred at about
  x -0.425, -0.095, 0.235, 0.565 (was -0.375 …). Low confidence, +-0.03.

## 5. Notes per unit

**shell**
- Door set as section 2.1 / table rows 1–9. Frame x -0.672 … 0.672, z 0 … 2.48.
- Front recess: y 0 … 0.98, x -0.65 … 0.71. Piers from 0.98. East pier stands 0.16 proud of the recess wall
  (was 0.35).
- Ceiling of the front recess: z = 2.54 + 0.50 y for y 0 … 0.62, flat 2.85 for y 0.62 … 0.98, soft crease
  (radius about 0.05) between; east edge coved r 0.12 onto the cheek wall; west edge sharp. Delete the two
  haunch features. No cornice.
- Cheek wall trim: dado and skirting on the cheek wall from the lower light's architrave to 0.04 short of
  the corner, returned ends; two cover strips in the corner; no trim on a front-wall return (there is none).
- Cheek lights: opening centre y 0.63, each with its 75 mm architrave and a splayed lining about 0.05 deep;
  a dark gasket line about 15 mm round the glass; lower light z 0.62–1.80, upper 1.97–2.46.
- Tiles as section 4.

**hall (vestibule + hallway)**
- Downlights to (-0.30, 0.30) and (0.32, 0.30) on the slope (z about 2.69).
- Mat 0.60 x 1.10 at x -0.44 … 0.16, y 0.04 … 1.14.
- Stool, keypad, switch and lantern keep their place relative to the inner screen and the east wall of the
  rear recess (they move with the screen if the room is lengthened). Keypad about 0.16 x 0.11, blank.
- The corner trim built in `rooms/vestibule.py` (`vestibule.door_corner`) assumes a 0.28 m front-wall
  return: replace by the dado stub on the cheek wall.
- Hall side, seen through the transom of the inner doors (v9 f_0029–0030): a small white sensor box about
  0.06 x 0.09 on the hall's west wall just north of the inner frame at z about 2.25.

**envelope**
- Canopy: raked soffit 2.54 → 2.31, fascia about 0.12, gutter z 2.33–2.45 in front of it, three downlights at
  x -0.42, 0, 0.42, y about -0.33. Roof plane as table row 23. Downpipe centre (-0.78, -0.17).
- Door furniture outside: hinges, letter plate, levers as 2.1. Transom plain frosted.
- West flank render exposed about 0.45 m; boxed white verge.
- If the round-3 front survey keeps the first-floor sill at 3.95, the wall between the roof head (3.13–3.25)
  and that sill becomes 0.7 m; the footage shows about 0.3–0.5 (v8 f_0126): that sill datum looks high.

**front**
- Doorbell at (0.80, z 1.30) on the pilaster. Gully under the downpipe shoe at (-0.78, -0.25), about
  0.15 square. Setts: 160 course family confirmed at the threshold.

**site**
- Threshold step unchanged (0.06). If the front plane moves (section 6), the forecourt polygon follows it.

**living**
- The bay's west cheek is the pilaster seen from outside, about 0.39 thick (vestibule face 0.71, bay face
  1.10 if the bay does not move). The lights have a shallow lining on the vestibule side, so the reveal on
  the living side is about 0.3 deep with the shutter inside it. Round 2 made this wall 0.20.

## 6. Knock-on effects

- **Width.** The wider door frame needs no other wall to move: outside it now fills the gap between the white
  strip at the party line and the pilaster (0.68 in `front_elevation.md`); inside the cheek wall face comes
  in from 0.90 to 0.71. The vestibule gives way (front recess 1.55 → 1.36 wide), the living room does not.
- **Depth.** 1.86 against 1.73 between the thresholds. Two ways to take up the 0.13:
  (a) keep the origin at the threshold and move the piers (south face 0.98), the inner screen (1.86–1.96)
  and everything north of it by +0.13; or
  (b) keep the house where it is and move the front plane (street doors and the bay's outer face) 0.13
  further south: threshold inner face y -0.13, pier south face 0.85 (pier 0.44–0.46 deep instead of 0.55,
  north face unchanged at 1.29–1.31), bay front wall 0.25 thick instead of 0.12 (more plausible for a
  masonry bay), cheek lights centred y 0.50, forecourt 0.13 shorter. (b) touches far fewer objects but
  leaves the origin 0.13 inside the threshold; the numbers in sections 2–5 are in frame (a).
  The living and hall surveys decide which: (b) holds if the bay is 0.99 deep inside and the hall 3.22 long.

## 7. Open questions

1. **Absolute scale.** Hardware (92 PZ lever set) makes the door set 3.4 % larger than the tile-based model
   scale (leaf 0.65 x 2.01 instead of 0.63 x 1.945). If the hall survey finds the hall wider than 1.30 or the
   inner leaves larger than 610 x 1981, scale section 2.1 with it (then the present heights 2.03 / 2.50 /
   2.57 are nearly right and only the widths change).
2. Which side takes the 0.13 of depth (section 6).
3. Split between pier and rear recess: 4 + 4 or 5 + 3 cells; not resolved from v1 t25.
4. Soffit: raked is inferred from the gutter height and the door-head height; a flat soffit with a 0.2
   downstand fascia would fit the far view too, but not the soffit meeting the frame head.
5. Cheek wall thickness and the living-side reveal; glass width of its lights (0.40–0.50).
6. East–west tile registration (+-0.03).
7. East pier below 2 m, any hook rail, and the skirting in the south-east corner are still hidden.
8. Whether the west soffit fitting is a third downlight or a sensor light.
9. Dado grey was not re-sampled reliably in daylight; keep `hall_dado_grey`.

## Verification

Verifier pass (independent re-measurement; the survey text above was read only afterwards). Scratch:
`reference/work/r3_porch_v/`, `build/r3/porch_v/` (`fl.py` grids / homographies, `lines.py` sub-pixel line fits,
`pose.py` camera pose from floor-tile nodes). No model build was run: the present values were read from
`spec/house.json`.

### What was measured, with which frames

| quantity | my frames (survey's in brackets) | method | result |
|---|---|---|---|
| tile rows, street threshold -> pier south face | v9 t58, v2 t901 (v9 t20, v9 t57, v1 t25) | row count on gridded 5-6x crops | K (cut 0.86-1.0), U, K, K, U, K, K, U, K = **8.9 cells** in both |
| tile rows, pier and rear recess | v2 t901 | row count; pier feet located by the vertical arris | pier **4.0 cells**, rear recess **3.9 cells** (first row at the inner sill cut to about 0.87) |
| tile rows between the thresholds | v2 t901, v9 t58 | row count, joint lines at 3-cell spacing | **16.8-16.9 cells** |
| door proportions | v9 t13, v9 t18, v8 t105.5 | pixel profiles, fitted bars | opening (cill top to head underside) **8.00 P** (544 px / 68.0 px, v9 t18); frame **5.8 P** (5.5-6.0: the open west leaf hides the west jamb in every far view); sash 2.62-2.72 P; glazing 3 x 4, glass 3.8-4.05 P high, its bottom 3.53 P above the cill top |
| transom | v8 t105.5 (equal bar intervals 124.0 / 123.9 px: no vertical perspective on that line) | 1D ratio along a glazing bar | glass **1.56 P** high, bottom **0.72 P** above the head underside, top 2.28 P above it |
| absolute size of P | see below | five routes | **0.24 +/- 0.012** (routes scatter 0.222-0.262) |
| door centre, west jamb | v9 t58 pose (14 tile nodes, f 900, rms 1.2 px), v2 t901 pose (6 nodes) | points on the threshold line | meeting edges 0.61-0.70 from the west wall: centre x **+0.01 ... +0.05**; inside, the leaf edge is 0.04-0.06 from the west wall (jamb visible) |
| frame against the cheek wall | photo, v9 t40.5 | vanishing directions | dado stub and window architraves converge to the right (east wall), the door horizontals to the left: **no front-wall return**, frame in the corner (confirmed) |
| vestibule dado | v9 t21.5 (pose from 6 tile nodes; and against the inner-door hinges) | height at the inner screen | top **0.835-0.85**, not 0.965 (0.965-1.0 is the hall side, v1 t56). The mid hinge of the inner doors comes out at 0.99-1.03 from the tiles and 1.01 from the 1981 leaf: tile cell 0.110 and the leaf scale agree |
| ceiling of the front recess | v2 t911, v9 t26 | reading | sloping panel from the door head with both downlights, flat strip (about a third of the depth) by the arch wall, soft crease; no haunches along the side walls |
| lean-to | v8 t127 (zoomed), v9 t13 | brick courses on the neighbouring pier in the plane of the abutment (38.6 px per course); door-plane scale | slate top at the abutment **36.9 courses** above the pier plinth (plinth top 0.41 above its floor) = 3.1-3.35; by the door scale 3.2-3.3; gutter 2.31-2.38; first-floor sill top **41.5 courses** = 3.5-3.7 |
| canopy lights | v8 t105.5, v2 t911 | reading | three downlights in a row on a boarded underside |

**Absolute scale (the one thing I could not pin better than +/-5 %).** Proportions in P agree with the survey
to 1-2 %. For P itself:

| route | P |
|---|---|
| dado top 0.835-0.85 (above) = inside glass-bottom edge + 0.03 (photo, v1 t11); glass bottom = cill top + 3.53 P | 0.222-0.232 |
| letter plate 0.30 wide by the v2 t901 pose (a standard 12 in plate) = 0.50 sash (v1 t14) | 0.224-0.230 |
| clear half-opening 0.60-0.64 (jamb inner edge to meeting edge, tile poses) = 2.55 P | 0.235-0.251 |
| brick courses 75-77 mm on the neighbouring pier (v9 t13: 9.5 px per course), plane 0.86-1.10 behind the door, f 800-920 px | 0.234-0.257 |
| inner-door lever (0.985) and sill seen through the open leaf in v9 t18, depth 1.86, f 870 +/- 60 px | 0.242-0.262 |

The survey value 0.232 lies inside this spread, the present model value 0.25 (leaf 2.00 over 8 intervals) at its
upper edge. What settles the door set for me is that the frame is seen wall to wall inside a 1.30 m room with
its west jamb visible: a 2.03 opening would need a 1.45 frame. Width and height are locked by the 5.8 : 8.0
proportion, so porch-01, -02 and -03 stand or fall together. Note on route 3 of the survey: the lever is not
level with a 0.965 dado; the vestibule dado is about 0.84 and the lever is 0.3 P above it.

### Verdicts

| id | verdict | value to use | my measurement (reference, frames, ratio, result) |
|---|---|---|---|
| porch-01 | **accept** | width 1.26 (2 x 0.63), frame 1.345, centre x 0 | frame 5.8 P x (0.24 +/- 0.012) = 1.39 +/- 0.07; sash 2.62-2.72 P = 0.63-0.65; centre +0.01 ... +0.05 from the tile poses. Present 1.24 is excluded (the frame spans the recess; present leaf : height 0.295 against 0.33-0.34 seen) |
| porch-02 | **accept** (with 01) | 1.89 | 0.03 + 8.00 P = 1.95 +/- 0.10; 1.89 and 2.03 are both inside that, but 2.03 needs a 1.45 frame, which does not fit between the walls as seen (jamb 0.04-0.06 wide inside, centre within 0.05 of the axis). If the house scale is later found 5-8 % larger (open question 1 of the survey; the front survey works with such a scale), 2.03 / 2.50 / 2.57 come back and the frame goes to 1.45 |
| porch-03 | **accept** | transom light 2.045-2.41, frame top 2.48 | glass 1.56 P high (survey 1.58-1.61), bottom 0.72 P above the head underside: 1.89 + 0.17 = 2.06, top 2.42 (v8 t105.5) |
| porch-04 | **accept** | front recess y 0..0.98; piers 0.98..1.42 (1.44 as proposed is within tolerance) | 8.9 cells x 0.110 in v9 t58 and v2 t901; pier 4.0 cells. The old 6.7-cell count is refuted |
| porch-05 | **accept** (the length) | 1.86 between the thresholds; screen 1.86..1.96 | 16.8-16.9 cells (0.98 + 0.44 + 0.43). Which side gives way is not decidable from this footage. My reading favours frame (a) of the survey with only the first hall segment absorbing it (3.22 -> 3.09): the pier south face (0.98) then stands on the inner-face line of the main front wall (0.99) under `w_front_1_w`, the bay projection outside was re-measured at 0.86 by the envelope verification (door plane stays), and `dims_G.md` reads the front hall shorter than 3.22 |
| porch-06 | **accept** (wall face); thickness not measured | vestibule face x 0.71; set the wall centre and thickness from the living-side face that the living / front reconciliation adopts (1.10 gives 0.39 thick, 1.03 gives 0.32) | no front-wall return (photo, v9 t40.5: opposite vanishing directions for the dado stub and the door). Frame east edge = centre + half frame = 0.69-0.75, plus cover strips: 0.75 +/- 0.05. A 0.39 wall contradicts the round-1 reading "no deeper than 0.2 from either side"; the pier projection from that wall is hidden by coats |
| porch-07 | **accept** (low confidence, follows 04) | centre [wall centre, 0.63], width 0.45 | north architrave adjacent to the pier (v9 t26), 0.25-0.30 of plain wall with the dado stub to the corner (v9 t40.5, photo): centre 0.60-0.63. Unsettled: the glass then reaches y 0.855, 0.11 north of the main wall outer face (0.74), while the front verification puts the symmetric east cheek light at 0.17..0.69 |
| porch-08 | **accept** | as proposed (delete both haunches; slope from the door head, flat 2.85 by the arch; east cove, west sharp) | shape confirmed in v2 t911 and v9 t26 (both downlights on the slope; flat strip about a third of the depth). Heights not measured independently: 2.54 follows the frame top of porch-03, 2.85 is the present value |
| porch-09 | **accept** (heights), with a stack warning | c0 2.76, cy 0.50, 26.6 deg | abutment 3.1-3.35 by brick courses (v8 t127) and 3.2-3.3 by the door scale (v9 t13); gutter 2.31-2.38; rise from eaves to abutment 0.62-0.67. **Warning:** in the same frame the first-floor west window sill is only 4-5 courses above the flashing (3.5-3.7); `w_green_west` has it at 4.20. Lowering the lean-to alone leaves about 0.95 m of blank wall under that sill which the footage does not show; the front elevation needs one scale (this survey and the front survey differ by 8-9 %) |
| porch-10 | **accept** | raked soffit 2.54 -> 2.31, gutter 2.33-2.45, three downlights x -0.42, 0, 0.42 | three fittings in a row on a boarded underside rising to the frame head (v8 t105.5: at 0.0 and about +0.44 of the transom half-width, the third beside the open leaf; v2 t911 through the transom). From the street the gutter overlaps the top of the transom (v9 t13: 1.28 P of 1.56 P visible). Heights follow the door scale |

### Consistency checks and what stays open

- Y inside the vestibule: 0.98 + 0.44 + 0.43 = 1.85 (16.8 cells), 1.86 as proposed. X at the street door:
  frame -0.672 ... +0.672, walls -0.65 / +0.71: the plaster on the west is cut back about 0.02 at the frame
  (the "transition towards the front door" of the v2 narration).
- Z: frame top 2.48 < ceiling at the door 2.54 < roof plane 2.76 at y 0; flat ceiling 2.85 under the roof at
  3.07 (y 0.62). Consistent within the porch.
- Not consistent, and not settled here: (1) the absolute scale of the front elevation (front verification:
  frame 1.47, recess B to 0.82, bay light pitch 0.69; here 1.345, 0.71 and, by the same proportions, a light
  pitch of 0.63-0.64); (2) first-floor sill 4.20 against 3.5-3.8 seen from the street in either scale;
  (3) cheek light reaching y 0.855 against the main wall face at 0.74.
- New, outside the proposal list: vestibule dado top 0.835-0.85 (the 0.965 of the spec is the hall side);
  leaf glazing is 3 x 4; lever axis about 0.3 P above the dado (0.90-0.95); letter plate 0.30 wide on the
  west leaf.

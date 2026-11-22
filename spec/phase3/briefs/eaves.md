# eaves (front and rear eaves storage) - round-3 brief

Module `blender/rooms/eaves.py` (`eaves_front`, `eaves_rear`). Owner instruction: visitors can open the low doors, duck
through and move about inside under the slope (eye height following the headroom). Decisions: `spec/RECONCILE3.md`
(eaves_loft-01..-09, floor2b-06, front-06).

## (a) What moved in the shell

- **Front void**: lining offset under the roof -0.31 -> **-0.17**, so the lining is **1.00** above the void floor at the
  knee-wall back (y 2.44) falling to nothing at the front wall; knee wall 0.92 -> **1.08** (seen from the room).
- **Bay-gable tunnel** `eaves_bay_tunnel`: top Z 7.39 -> **8.19** (flat strip 0.40 wide at **1.70** above the floor, was
  0.90 - below the camera); linings 50 deg; polygon now the whole bay x **1.11..3.85**, y 0.14..0.95 (was 1.43..3.63); axis
  x **2.48** (gable ridge, was 2.525). The knee-wall back stands vertical to **1.20** above the east hatch, then a lined ramp
  rises to the strip, ending in a dark slot about 0.4 x 0.03. The gable above is now 50 deg with the ridge at 8.75 (was
  43 / 8.295): the tunnel fits under it (8.19 + 0.20 tan 50 + 0.25 = 8.68).
- `eaves_front` polygon follows the first-floor bay (bay part x 1.11..3.85, was 1.43..3.63); ceilingZ 8.0 -> 8.19.
- **Front hatches** 0.70 / 0.15 -> 0.90 / 0.03; the east one at x 2.48 (was 2.975), on the tunnel axis.
- **Rear void**: the main rear slope is now 35 deg (ridge unchanged), knee wall 1.42 -> **1.23**; lining 1.16 above the floor
  at the knee-wall back (ceilingZ 7.91 -> 7.65), falling at 35 deg towards the rear wall and landing on the lower floor at
  about y 8.4-8.5 (inside the polygon; the north edge stays 8.73). Rear hatch 1.03 / 0.17 -> 0.91 / 0.15. `eaves_rear_step`
  unchanged (x 2.35, drop 0.12).
- East wall 0.23 -> 0.35 thick outwards (inner face 4.30).

Exact spec changes (old -> new):

<!-- diff:begin (generated from spec/house.json) -->
- `rooms[eaves_front].polygon`: [[-0.65, 0.95], [1.43, 0.95], [1.43, 0.14], [3.63, 0.14], [3.63, 0.95], [4.3, 0.95], [4.3, 2.44], [-0.65, 2.44]] -> [[-0.65, 0.95], [1.11, 0.95], [1.11, 0.14], [3.85, 0.14], [3.85, 0.95], [4.3, 0.95], [4.3, 2.44], [-0.65, 2.44]]
- `rooms[eaves_front].ceilingZ`: 8.0 -> 8.19
- `rooms[eaves_front].ceiling.offset`: -0.31 -> -0.17
- `rooms[eaves_rear].ceilingZ`: 7.91 -> 7.65
- `walls[w_east_2a].a`: [4.415, 0.865] -> [4.475, 0.865]
- `walls[w_east_2a].b`: [4.415, 2.49] -> [4.475, 2.49]
- `walls[w_east_2a].thickness`: 0.23 -> 0.35
- `walls[w_east_2c].a`: [4.415, 6.64] -> [4.475, 6.64]
- `walls[w_east_2c].b`: [4.415, 8.88] -> [4.475, 8.88]
- `walls[w_east_2c].thickness`: 0.23 -> 0.35
- `walls[w_knee_front].b`: [4.415, 2.49] -> [4.475, 2.49]
- `walls[w_knee_front].height`: 0.92 -> 1.08
- `walls[w_knee_rear].b`: [4.415, 6.64] -> [4.475, 6.64]
- `walls[w_knee_rear].height`: 1.42 -> 1.23
- `openings[h_eaves_front_w].height`: 0.7 -> 0.9
- `openings[h_eaves_front_w].sill`: 0.15 -> 0.03
- `openings[h_eaves_front_e].center`: [2.975, 2.49] -> [2.48, 2.49]
- `openings[h_eaves_front_e].height`: 0.7 -> 0.9
- `openings[h_eaves_front_e].sill`: 0.15 -> 0.03
- `openings[h_eaves_rear].height`: 1.03 -> 0.91
- `openings[h_eaves_rear].sill`: 0.17 -> 0.15
- `features[eaves_bay_tunnel].polygon`: [[1.43, 0.14], [3.63, 0.14], [3.63, 0.95], [1.43, 0.95]] -> [[1.11, 0.14], [3.85, 0.14], [3.85, 0.95], [1.11, 0.95]]
- `features[eaves_bay_tunnel].z`: [6.49, 7.390000000000001] -> [6.49, 8.19]
<!-- diff:end -->

## (b) Surveyors' notes (eaves_loft, front, floor2_b, dims_envelope merged)

- **Front tunnel** (v12 f19-25, f29): knee-wall back vertical white to about 1.20 above the east hatch, 1.12-1.22 wide at
  that height; above it a lined ramp rises north between the linings to the flat strip and ends in a dark slot about 0.4
  x 0.03 with a batten. Plain white trapezoid gable end, no window; one round opal bulkhead with a deep rim, about 0.28
  diameter, on the strip. Valley cuts in the main lining are closed by a white fascia band 0.28 high (lining underside 1.00,
  top 1.28 at the knee wall), from x 1.85 / 3.35 at the knee wall outwards to the bay cheeks (f25, f26, f34-36, f57-59).
  The valleys of the 50-deg gable now start at (0.61, 0.46) and (4.35, 0.46) and meet at (2.48, 4.33): check them against
  what the front voids show.
- **Front low voids**: lining 1.00 at the knee-wall back; the west end is the party wall, unpainted cream plaster (estimate
  #D8D2BE; f51-53); the east stretch is open and used (f23, f30-32). Switch (1-gang rocker) centre z 0.79 and double socket
  centre z 0.37, both at x 2.23 on the knee-wall back (f25, f26, f36) - with the east hatch moved to 2.48 they sit just
  west of its frame. Hatch seen from inside: rough plasterboard edge 1.16 wide, white lining, sill ledge 0.11 above the
  floor.
- **Rear void** (f76-118): platform x 1.35..2.35 from the knee wall to a white upstand board about 0.13 high under the
  lining at about y 8.7, with a short return and a dark triangular gap at the step end; step at x 2.35 with two aluminium
  nosings side by side, each with a dark grey insert about 30 mm (78 mm in all) and an aluminium riser face; the lower
  floor continues 0.3-0.4 beyond the upstand to where the lining lands on it; plain white end walls at x 1.35 and 4.30.
  The upstand board and the lower floor running on beyond it belong in the module (the spec polygon was not moved:
  eaves_loft-08 rejected); the step drop stays 0.12 (the 0.07 reading was not better supported). Rear switch at x 2.58
  and bulkhead centre x 2.83 on the knee-wall back, height about 1.0 (not re-measured); bulkhead only 0.17 diameter
  (model 0.26).
- **Floors**: one grey concrete-effect sheet vinyl in both voids and on both rear levels, estimate #807D77 lightly mottled
  (the pale / charcoal split in the model was lighting).
- **Storage**: a few plain closed boxes and two plain suitcases; an open plain carton by the rear step and flattened
  cartons leaning on the rear east wall. Leave a lane free.

## (c) New footage

- **v12** (PXL_20261121_125633444) whole video: doors open, mouldings, the triangular voids inside, floor finish, how far
  they run (front tunnel f19-36, front voids f23-59, rear void f76-118).

## Fallout after the foundation round

Gate check of the full build of the current tree (`build/r3/gate/home.blend`, BUILD OK) against `spec/house.json`.
Bounds are world metres of the built objects (x a..b, y c..d, z e..f), measured by `build/r3/gate/audit.py` and
`collide.py` (results in `build/r3/gate/audit_new.json` and `coll_cmp.txt`). Objects that already moved with the spec
are not listed.

- Front. `eaves_front.ceiling` still has the old geometry.
  - The main void lining runs from z 6.49 at y 0.95 to 7.35 at y 2.44, which is 0.86 above the floor at the knee-wall
    back. The brief wants 1.00 there (offset -0.17).
  - The tunnel lining closes at a 0.30 strip at z 7.39 (x 2.33..2.63). The new tunnel rises to 8.19, with 50-degree
    linings, a 0.40 strip and the ramp off the knee-wall back.
  - The shell's knee-wall back now stands to 1.00, and up to 1.70 inside the tunnel. Rebuild the lining from the spec.
- Front, moved east hatch. The hatch is now x 1.955..3.005, z 6.52..7.42. `eaves_front.socket` (x 2.257..2.403,
  z 6.70..6.78), `eaves_front.switch` (x 2.287..2.373, z 7.05..7.13) and `eaves_front.kneecap` (x 1.40..3.63,
  z 6.94..7.35), all on the void side of the knee wall (y 2.43..2.44), now sit in or across the opening. Move the socket
  and switch off the hatch, and rebuild the kneecap around it.
- Rear, past the lower floor.
  - `eaves_rear.ceiling` is a single quad from z 7.646 at y 6.69 down to z 6.218 at y 8.73. It follows the new 35-degree
    slope but runs on past the lower floor: it reaches 6.37 (the level of `eaves_rear.floor_low`) at y about 8.53, and
    ends 0.15 below that floor.
  - `eaves_rear.floor_low` (x 2.354..4.30, z 6.37) and `eaves_rear.nosing.0`..`.3` (x 2.29..2.353, y 6.69..8.73,
    z 6.455..6.495) run under or into `roof.main_rear` beyond y about 8.36..8.53.
  - Clip all of these where the slope lands: the roof underside reaches 6.49 at y about 8.36 and 6.37 at y about 8.53.
- Rear, bulkhead. The top of `eaves_rear.bulkhead` and its base (x 2.72..2.98, y 6.69..6.753, z 7.41..7.67) is 0.02
  inside the roof slab (the lining is at 7.65 at y 6.69). Lower it by 0.03.

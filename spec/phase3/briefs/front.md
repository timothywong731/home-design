# front (forecourt, cars, bins, flag) - round-3 brief

Module `blender/rooms/front.py` (cars, bins, flag, fittings); zones, front wall and pier are built by the site stage.
Decisions: `spec/RECONCILE3.md` (front-01..-04, -08, -11..-13; porch-09; envelope-01, -08).

## (a) What moved

- **The forecourt falls 0.30, not 0.08**: `forecourt` fall z -0.06 (house) -> **-0.36** (plot edge y -5.20); footway -0.16
  -> **-0.38**; road -0.28 -> **-0.50**. The pier, the wall, cars and the tarmac strip all sit on that slope. Car wheel Z
  comes from the adopted fall (grey car about -0.13 rear, -0.34 front, 3 deg nose down) - do not hard-code it.
- **Setts stop at x 4.40** (was 4.53). East of them a patched tarmac strip (#6B6A64): `forecourt_alley_mouth` x 4.40..5.80,
  y -5.20..-0.12 (fall -0.08 -> -0.36, surface asphalt) and the new `forecourt_alley_apron` between the bay's east return
  and the street gate (x 4.25..5.80, y -0.12..1.70, falling -0.08 -> -0.30 to the alley floor) with a small sett patch kept
  at x 4.25..4.65, y 0.25..0.74 under the meter box.
- **Pier `front_pier_w`**: height 1.20 -> **1.40** (17 courses = 1.275 + cap 0.125), base -0.14 -> **-0.36**, cap 0.45
  square, edge 0.085, shallow four-way pyramid rising 0.04 (apex about Z +1.04) - new field `cap`.
- **Front wall `front_wall_w`**: base -0.10 -> **-0.36**, height 0.90 at the pier end, brick top **level at Z +0.54** (0.60
  showing at the house, where the ground has risen to -0.06); timber planter troughs on top, boards 0.29 high, bottom Z
  +0.47, rim Z **+0.76** - new field `planter` (was top 0.80 with troughs to 1.28).
- **Bay**: lights centred on x **2.48** (was 2.55): west pilaster zone x 0.80..1.175 (shaft about 0.83..1.09) against the
  door frame, east corner pilaster zone 3.785..4.285; the bay's east cheek outer face is 4.25 (was 4.15), 0.40 behind the
  east wall face 4.65, joined by a white south-facing return (y 0.74, x 4.25..4.65). The east cheek window moved to y
  0.17..0.69.
- **Street door** frame 1.39 wide (x -0.67..0.72), leaves 0.63, head 1.95 (see hall.md).
- **White car** centre (3.15, -3.43) -> **(3.2, -2.7)** (21 Nov; tail 0.85 from the bay face).

Exact spec changes (old -> new):

<!-- diff:begin (generated from spec/house.json) -->
- `exterior.zones[forecourt].polygon`: [[-0.72, -5.2], [4.53, -5.2], [4.53, -0.12], [-0.72, -0.12]] -> [[-0.72, -5.2], [4.4, -5.2], [4.4, -0.12], [-0.72, -0.12]]
- `exterior.zones[forecourt].fall.z`: [-0.06, -0.14] -> [-0.06, -0.36]
- `exterior.zones[forecourt_alley_mouth].polygon`: [[4.53, -5.2], [5.43, -5.2], [5.43, 0.74], [4.15, 0.74], [4.15, -0.12], [4.53, -0.12]] -> [[4.4, -5.2], [5.8, -5.2], [5.8, -0.12], [4.4, -0.12]]
- `exterior.zones[forecourt_alley_mouth].surface`: "concrete_setts_grey_buff" -> "asphalt"
- `exterior.zones[forecourt_alley_mouth].fall.from`: [4.98, -0.12] -> [5.1, -0.12]
- `exterior.zones[forecourt_alley_mouth].fall.to`: [4.98, -5.2] -> [5.1, -5.2]
- `exterior.zones[forecourt_alley_mouth].fall.z`: [-0.08, -0.14] -> [-0.08, -0.36]
- `exterior.zones[footway].z`: -0.16 -> -0.38
- `exterior.zones[road].z`: -0.28 -> -0.5
- `exterior.zones[forecourt_alley_apron]` new: {"id": "forecourt_alley_apron", "group": "front", "polygon": [[4.25, -0.12], [5.8, -0.12], [5.8, 1.7], [4.65, 1.7], [4.65, 0.74], [4.25, 0.74]], "z": -0.08, "surface": "asphalt", "room": "front", "fall": {"from": [5.2, -0.12], "to": [5.2, 1.7], "z": [-0.08, -0.3]}}
- `exterior.boundaries[front_wall_w].baseZ`: -0.1 -> -0.36
- `exterior.boundaries[front_wall_w].planter` new: {"height": 0.29, "bottomZ": 0.47, "rimZ": 0.76}
- `exterior.boundaries[front_pier_w].baseZ`: -0.14 -> -0.36
- `exterior.boundaries[front_pier_w].height`: 1.2 -> 1.4
- `exterior.boundaries[front_pier_w].cap` new: {"size": 0.45, "edge": 0.085, "rise": 0.04}
- `exterior.features[car_white].center`: [3.15, -3.43] -> [3.2, -2.7]
<!-- diff:end -->

## (b) Surveyors' notes (front, porch, dims_envelope merged)

- **Setts**: courses 0.16 wide parallel to the house, units mostly 0.16 x 0.16 with some 0.24 and 0.12 long (three sizes
  3 : 4 : 6; the door opening is 8.0 of the middle size), dark joints 5-8 mm; ONE border course of darker setts (#7E7B75)
  laid lengthwise against the house wall. Colour light warm grey #A6A29A with about 15 % buff #B3AB95 and 10 % pinkish
  #A8958C units: the present pink / terracotta chequer is far too strong and too regular (v9 f63-68, t20; photo).
- **Inspection covers**: two recessed covers side by side **east-west** at about (4.67, -2.0) and (5.21, -2.0), each 0.48 x
  0.58 with the long side along Y, galvanised frames, grey concrete trays #8C8A86 with two key holes, a concrete haunch
  round them (v8 f30, f64; v4 f52). Gullies 0.15 square at about (-0.78, -0.25) under the canopy downpipe shoe and at
  about (2.4, -0.20) at the bay foot (v9 f54-56, f62-68).
- **Pier**: 0.33 square, buff brick #BFAD84, stretcher + header per face; precast cap in exposed aggregate #A6A398 (v8
  f12, f121). Pier plaque: small black cast-metal plate 0.22 x 0.065 with two lines of raised white capitals (a cat
  warning, nothing identifying), two screws, on the street face in the second course below the cap.
- **Planter troughs**: vertical boards, dark brown weathered silver (#5B4A3A to #8F7C65); bellflower to about Z 1.0 (v8
  f100-103). The planter wall ends against the house at the downpipe; the open west door leaf (about 100 deg) stands
  parallel to it.
- **Footway**: flags 0.6 x 0.9 / 0.6 x 0.6 #A6A39F with two black tarmac patches (crossover in front of the pier, x
  -1.3..-0.2, and a strip along the plot edge). Lamp column belongs at about (7.5, -7.0) in front of the east neighbour, not
  (3.3, -7.0); street tree about (-1.2, -7.0). East neighbour's raised planter (massing): dark corrugated steel #262427,
  0.9 x 2.0 x 0.5, long side north-south, at about x 6.0..6.9, y -5.0..-3.0 (the survey placed it at 5.75..6.65 against a
  5.66 wall; the wall is now 5.80).
- **Cars**: grey car position as spec. White car on 21 Nov: add red-orange mirror caps #C8452F, a thin red-orange stripe
  low on each door, a red lower lip on the front bumper, black A-pillar flash, short roof aerial; **no plates, no badges**.
- **Bins** as placed (grey against the house, navy south of it, just east of the corner pilaster), navy #3F4868 with lid
  #68759A, grey #4A4C4B; the caddy is PALE GREEN #8FA79A, 0.3 south-west of the navy bin; no lettering.
- **Door fittings**: video doorbell, slim black / satin-grey unit about 0.045-0.048 x 0.115-0.125 with a black lens window,
  on the west pilaster face at centre z 1.30, about x 0.80-0.85 (v8 t105, v9 f_0044-0048). Outdoor socket: grey box 0.16 x
  0.10 at about (1.22, -0.14, 0.42) under the west end of the bay sill (was x 1.45). Flag bracket stays on the west
  pilaster (bracket x 0.98).
- **Bay cheek** (east): white surface gas-meter box 0.41 x 0.56 x 0.21 under the ground-floor cheek sill (y 0.28..0.69, z
  0.02..0.58) with a small white cable box beside it; white twin-floodlight security camera on the return at about (4.40,
  0.72, 2.72) (v8 f64-79, t39, t70).

## (c) New footage

- **v8** (PXL_20261121_124142138): front bay and bins 1-6; front elevation from the pavement with the pier, both cars,
  porch, flag, gable 13-66; side gate and east wall 67-89; cars 90-101; the path to the door 102-113; canopy, fascia,
  gable 114-138.
- **v9** (PXL_20261121_124601813): 7-20 porch and door from the forecourt; 45-58 outside of the door, canopy, brick return,
  planter; 59-68 forecourt along the bay base, bins.
- Photo (grey car, planter wall, setts).

## Fallout after the foundation round

Gate check of the full build of the current tree (`build/r3/gate/home.blend`, BUILD OK) against `spec/house.json`.
Bounds are world metres of the built objects (x a..b, y c..d, z e..f), measured by `build/r3/gate/audit.py` and
`collide.py` (results in `build/r3/gate/audit_new.json` and `coll_cmp.txt`). Objects that already moved with the spec
are not listed.

- `front.planter` (x -0.966..-0.694, y -4.825..-0.255, z 0.458..0.726) now sinks into the top of `front.front_wall_w`
  (84 triangles): its bottom is 0.08 below the brick top at 0.54. The module follows `planter.bottomZ` 0.47, which is
  below the wall top (site note). Sit it on 0.54, or settle the spec value with the reconciler.
  `front.planter.bellflower` follows it.
- The bins `front.bin.0` and `front.bin.1` float 0.015..0.027 above the forecourt at the wheels, and `front.caddy` dips
  0.014 below it. Snap each wheel to `ctx.ground_z`.
- The new `forecourt_alley_mouth` ground cuts `front.cover.0` and `front.cover.1` (x 4.065..4.515, y -3.30..-2.0)
  obliquely (3 triangles each). The site note puts the covers at (4.67, -2.0) and (5.21, -2.0), each 0.48 x 0.58.
- Cars, wheels, lamp column, tree and flag followed the new ground and front. Nothing else is broken.

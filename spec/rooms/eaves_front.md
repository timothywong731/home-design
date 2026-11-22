# eaves_front / eaves_rear - round-3 module notes (blender/rooms/eaves.py, eaves_parts.py)

Notes only; the room spec is `spec/rooms/eaves.md`, the survey `spec/phase3/eaves_loft.md`, the brief
`spec/phase3/briefs/eaves.md`. Frame: world X, Y; `z` = height above the loft floor (world Z 6.49).

## What the module builds (round 3)

### Front void
- **Linings** (`eaves_front.ceiling`), one closed white surface:
  - main slope over the low voids: the `main_front` plane at the spec's lining offset -0.17 (1.00 at the knee-wall
    back, 0.14 at the front wall face), **but never higher than 1 cm under the slab underside** (`ctx.ceil_z`). With
    the present envelope (slab 0.30 thick over the eaves) that is offset -0.31: **0.86 at the knee-wall back**. The
    lining follows automatically when the slab gets thinner (see "Open").
  - tunnel under the bay gable: flat strip 0.40 wide at 1.70 (world 8.19) on the axis x 2.48, linings at 50 deg
    reaching the bay walls (x 1.11 / 3.85) at 0.31; 2 cm under the gable slab underside.
  - valley cuts: a vertical white fascia band from the main lining up to the spec lining + 0.20, so that its top
    meets the crease corner at the knee wall (1.20 there), along the line where the tunnel lining reaches that height:
    x 1.86 / 3.10 at the knee wall, 1.14 / 3.82 at the front wall. Fixer round: f25 shows the crease running straight
    into the band's top corner and the band's end standing over the switch (x ~1.82-1.84 measured on the 86 mm plate);
    the survey's 0.28 / 1.28 left a sloped strip between them and put the band 7 cm east. A small closing face at
    y 0.95 between the bay walls and the band feet.
  - above the knee wall's vertical part (1.20 above the floor inside the tunnel) a **ramp** rising north at 35 deg
    over the Slate Room ceiling, between the tunnel linings, to a **dark slot** 0.40 x 0.03 under the strip at
    y 3.11..3.18 with a softwood batten in it. The shell carried the knee-wall back up to the tunnel lining; the
    module deletes that part of `eaves_front.walls` above 1.20 for faces centred within x 1.68..3.28 (9 faces) so the
    ramp shows.
- `eaves_front.kneecap`: white patches 1 mm proud of the knee-wall back where the shell clips the wall below the
  main lining (it takes the bay-gable plane for x 1.25..1.45 and 3.51..3.85).
- `eaves_front.h_eaves_front_w.edge` / `.h_eaves_front_e.edge`: rough-cut plasterboard margin round the hatch
  holes on the void side (jagged, a shade darker than the wall), 55 mm wide at both hatches (the valley bands now
  stand 95 mm outside the east hole).
- `eaves_front.h_eaves_front_w.soffit`: only while the lining sits under the west hatch head (0.86 < 0.93): a white
  soffit from the head at the room face of the hole sloping down to the lining edge, so the strip above the lining
  does not show the lining's culled back face from the room. Not built once the lining is at 1.00.
- Switch (1-gang rocker) centre x 1.84, z 0.79; double socket centre x 1.86, z 0.37; white cover strip 32 x 360 mm
  upright at x 1.72 (f26, f36).
- Hidden light panels standing in for the room light through the open hatches (unseen by the camera, 4 W/m):
  `eaves_front.spill` in the west hatch facing into the void, and (fixer round) `eaves_front.spill_e`, a 0.55 m
  upright panel at the east hatch's east jamb throwing light east under the valley band: the east stretch is shaded
  from the tunnel bulkhead by the band and baked near black once its lane along the knee wall was cleared.
- Bulkhead: round opal, deep rim, 0.28 diameter, on the strip at y 1.05 (f20 shows it from below with the gable end
  behind it; f25, taken from about y 1.2 looking north, does not show it, so it hangs south of y 1.2). Old spec y 1.60.

### Rear void
- Lining (`eaves_rear.ceiling`) on the 35-deg `main_rear` plane, 1 cm under the slab: 1.16 at the knee-wall back,
  landing on the 0.13 upstand board on the platform (x 1.35..2.35) at y 8.157 and on the lower floor (x 2.35..4.30)
  at y 8.514 (brief: 8.4-8.5).
- Upstand board 18 mm, 0.13 high, x 1.35..2.35 at y 8.157. Return board at the step end (fixer round, f95 / f97):
  18 mm, standing on the LOWER floor against the riser end (x 2.351..2.369), from the upstand's top corner (0.25 above
  the lower floor) down past the riser; 20 mm wide at the top, its north edge raking down to the floor 0.20 north of
  the upstand, steeper than the lining, so a dark triangle opens between it and the lining down to where the lining
  lands (y 8.514).
- A hidden 0.75 m panel in the rear hatch (`eaves_rear.spill`, 4 W/m, as `eaves_front.spill` in the west hatch) stands
  in for the room light through the open hatch.
- Double nosing on the platform edge (x 2.272..2.353), y 6.69..8.157: two mill-finish aluminium plates with two 30 mm
  dark inserts (78 mm in all), aluminium leg 36 mm down the riser. Drop 0.12 (spec).
- The dark `floor_low` overlay is gone: both levels show the shell's one grey sheet vinyl (eaves_loft 2.6).
- Switch x 2.58 centre z 1.00, bulkhead 0.17 diameter centre x 2.83, z 1.01 (both 0.13 / 0.38 east of the hatch's
  east jamb at 2.45); the bulkhead top is 6 cm under the lining.

## Measurements made this round
- **Switch / socket x** (v12 f25, crop `reference/work/r3_eaves_loft/c25_hatch.jpg`): switch plate 59 px wide at
  full resolution = 86 mm (1.46 mm/px); switch centre 139 px = 0.20 m west of the void-side lining arris, socket
  centre about 0.165 m (verticals converge: camera above, yaw about 10 deg). With the verifier's void-side opening of
  0.90 (arris at x 2.03) that is x 1.83 / 1.865; used 1.84 / 1.86, +/- 0.05.
- **Bulkhead y**: from f20 / f25 as above, +/- 0.25.
- **Storage** placed from the frames (no sizes measured beyond typical): two lidded 0.46 x 0.36 x 0.24 plastic boxes
  stacked at the gable end on the east side (left looking south in f19-21), a pale carton west of the middle (f21),
  the silver cabin case standing in the tunnel's east side at (2.92, 1.50) (f25 foreground, f29), two black cases
  lying on their backs under the slope in the east stretch, x 3.06..3.64 and 3.66..4.29, y 1.45..1.89, wheels east
  (f23 / f31 show black cases lying there; f25 / f29 also show cases standing at the knee wall east of the hatch, which
  is the only walkable strip there, so the owner's lane wins), one carton at the party-wall end (f51-53: soft bags there, left out). Rear: the open
  carton by the step (f86-93; its body 0.34 east of the nosing, centre x 2.90, a little further than filmed, so its
  west flap clears the line from the bulkhead to the step-end corner, which baked near black), a bundle of
  eight flattened cartons about 0.1 thick leaning on the east wall (f87, f100-101), two small boxes and a
  long low box at the north end of the platform (f103-110).

## Lanes (owner: visitors walk in)
Checked on the saved build (`build/rooms3/eaves/scripts/check.py`): no plan-symbol footprint enters
- front: x 2.205..2.755 from the east hatch to the gable end (the tunnel stays free 1.83..2.93 down the middle);
- front: y 1.89..2.44 along the knee wall from the party wall to the tunnel (the west hatch lane), and from the east
  hatch along the knee wall to the east wall (x 2.20..4.30);
- rear: x 1.65..2.20, y 6.69..7.24 from the hatch onto the platform, and y 6.69..7.24 along the whole knee wall.
Stored things carry `plan_sym='box'` (drawn as a plain outline, a solid obstacle for the walker).

## Open
- **Envelope slab over the eaves.** `lib.envelope` builds the roof slab 0.30 thick over eaves_front, its black
  underside 0.87 above the void floor at the knee-wall back, while the spec, the shell walls and the hatches assume
  the lining at offset -0.17 (1.00). The hatch holes (head 0.93, frames to 0.97) therefore cut into the slab and the
  lining has to stay at 0.86: it crosses the top 7 cm of the west hatch hole seen from the room (closed by the
  soffit above), it reaches the floor at the front wall (0.00, not 0.14), the band's foot hides the top half of the
  switch from the tunnel, and the low voids have no 0.8 m headroom for the viewer's walk. Once the slab is 0.16 thick there (and `ctx.roof_under` / `ceil_z`
  agree), the module puts the lining at 1.00 by itself.
- The end walls of the front void are capped at 7.42 (0.93) for y 2.316..2.44 by the shell; the kneecap patch closes
  the gap whenever the lining is above them.

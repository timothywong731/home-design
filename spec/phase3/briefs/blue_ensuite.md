# blue_ensuite (with the balcony) - round-3 brief

Modules `blender/rooms/blue_ensuite.py`, `balcony.py`; the balcony steel is built by envelope from `features.balcony_structure`.
Decisions: `spec/RECONCILE3.md` (dims_1-04, garden-22, envelope-06).

## (a) What moved in the shell

- **En-suite west wall 0.07 east**: room x 0.50..2.90 -> **0.57..2.90** (2.40 -> **2.33** x 1.70). Fittings keyed to the
  west wall (the bath runs along it) move with it; a 0.70 bath gives 2.35, inside tolerance. Partitions `w_bay_ensuite`,
  `w_recess_ensuite` on centreline 0.52 (2.60 high on the corridor side).
- Flank: `w_flank_1_ensuite` (flank 0.35 + the 0.20 false wall, faces 2.90 / 3.45) centre 3.15 -> 3.175, 0.55 thick;
  `w_ensuite` keeps y 11.48.
- **Balcony** 2.30 x 1.05 at x 0.00..2.30 -> **2.12 x 1.12 at x 0.195..2.315**, y 17.36..18.48, centred on the door axis
  1.255 (was 0.14 off the door). Front posts at x 0.195 / 1.255 / 2.315, y 18.48; top rail and posts **round tube about
  48 mm** with elbow / tee fittings (`railing.section` "round_tube"); bars at about 0.14 centres, 7 per side and per front
  bay; wall posts (0.21, 17.36) / (2.30, 17.36); rain pipe x 0.36. Railing height 1.10 and deck level unchanged. Walkable
  area x 0.27..2.29, y 17.46..18.43 roughly.

Exact spec changes (old -> new):

<!-- diff:begin (generated from spec/house.json) -->
- `rooms[blue_ensuite].polygon`: [[0.5, 11.15], [2.9, 11.15], [2.9, 12.85], [0.5, 12.85]] -> [[0.57, 11.15], [2.9, 11.15], [2.9, 12.85], [0.57, 12.85]]
- `rooms[blue_ensuite].size`: [2.4, 1.7] -> [2.33, 1.7]
- `rooms[balcony].polygon`: [[0.0, 17.36], [2.3, 17.36], [2.3, 18.41], [0.0, 18.41]] -> [[0.195, 17.36], [2.315, 17.36], [2.315, 18.48], [0.195, 18.48]]
- `rooms[balcony].size`: [2.3, 1.05] -> [2.12, 1.12]
- `walls[w_yellow_n].a`: [0.3, 11.1] -> [0.52, 11.1]
- `walls[w_yellow_n].b`: [3.25, 11.1] -> [3.275, 11.1]
- `walls[w_bay_ensuite].a`: [0.45, 11.1] -> [0.52, 11.1]
- `walls[w_bay_ensuite].b`: [0.45, 12.455] -> [0.52, 12.455]
- `walls[w_bay_ensuite].height`: 2.5 -> 2.6
- `walls[w_recess_ensuite].a`: [0.45, 12.455] -> [0.52, 12.455]
- `walls[w_recess_ensuite].b`: [0.45, 12.9] -> [0.52, 12.9]
- `walls[w_ensuite_n].a`: [0.45, 12.9] -> [0.52, 12.9]
- `walls[w_ensuite_n].b`: [3.25, 12.9] -> [3.275, 12.9]
- `walls[w_flank_1_ensuite].a`: [3.15, 11.1] -> [3.175, 11.1]
- `walls[w_flank_1_ensuite].b`: [3.15, 12.9] -> [3.175, 12.9]
- `walls[w_flank_1_ensuite].thickness`: 0.5 -> 0.55
- `openings[d_balcony].center`: [1.29, 17.11] -> [1.255, 17.11]
- `openings[w_ensuite].center`: [3.15, 11.48] -> [3.175, 11.48]
- `features[balcony_structure].polygon`: [[0.0, 17.36], [2.3, 17.36], [2.3, 18.41], [0.0, 18.41]] -> [[0.195, 17.36], [2.315, 17.36], [2.315, 18.48], [0.195, 18.48]]
- `features[balcony_structure].railing.post`: 0.05 -> 0.048
- `features[balcony_structure].railing.posts`: [[0.0, 18.41], [1.15, 18.41], [2.3, 18.41]] -> [[0.195, 18.48], [1.255, 18.48], [2.315, 18.48]]
- `features[balcony_structure].railing.barCentres`: 0.165 -> 0.14
- `features[balcony_structure].railing.barsPerSide`: 5 -> 7
- `features[balcony_structure].railing.barsPerFrontBay`: 6 -> 7
- `features[balcony_structure].railing.section` new: "round_tube"
- `features[balcony_structure].supports.wallPosts`: [[0.27, 17.36], [2.2, 17.36]] -> [[0.21, 17.36], [2.3, 17.36]]
- `features[balcony_structure].rainPipe`: [0.42, 17.36] -> [0.36, 17.36]
<!-- diff:end -->

## (b) Surveyors' notes (garden, dims_1, dims_envelope merged)

- En-suite: west face about 0.57 is a knock-on of the corridor wall; nothing measured inside the room (2.25-2.40 by
  fixture arithmetic in blue_ensuite.md); length, ceiling and window not audited.
- Balcony (v13 f_0213-0217 from above, low confidence on the width; the frontal v2 t250 reads 2.2-2.3 including ivy):
  platform centred on the door meeting stile to 0.02; width:depth 1.77-1.80 at any focal length. Rail and posts read mid
  grey from above (sample #B2B1B7, estimate #6B7076), bars black - colour open. Side rails return to wall brackets; thin
  vertical bars at about 0.14; chequer-plate deck screw-fixed along its edges, plate reads #727375 in sun, estimate
  #3A3C40 (present #2E3033 slightly dark). Wall posts / struts not seen from above.
- Planting: troughs on the front and **east** rails only (west side bare); variegated ivy covers the whole front rail and
  hangs outside it; purple-blue flowers at the NE corner.
- Balcony door fanlights are top-hung openers (both open in v13 f_0213-0217). Lantern on the wall east of the doors at x
  2.31 (black four-sided coach lantern with pagoda cap) - check it against the new platform edge 2.315. Small grey square
  unit on a bracket east of the balcony doors at first-floor head height (v13 f_0214-f_0217).

## (c) New footage

- v13 207-225 (balcony from above, plan-like), v11 188-196 (from the garden).

## Fallout after the foundation round

Gate check of the full build of the current tree (`build/r3/gate/home.blend`, BUILD OK) against `spec/house.json`.
Bounds are world metres of the built objects (x a..b, y c..d, z e..f), measured by `build/r3/gate/audit.py` and
`collide.py` (results in `build/r3/gate/audit_new.json` and `coll_cmp.txt`). Objects that already moved with the spec
are not listed.

- The west wall face moved from x 0.50 to x 0.57. Shift the west-wall set 0.07 east; affected:
  - `blue_ensuite.bath` (x 0.50..1.255, y 11.15..12.85): 0.07 inside the wall along its whole length
  - `blue_ensuite.bath_tap` (x 0.522..0.663) and `blue_ensuite.bath_tap.hose` (x 0.519..0.635)
  - `blue_ensuite.bath_tap.handset` (x 0.50..0.558): entirely inside the wall
  - `blue_ensuite.shelf` (x 0.55..1.10, y 12.73..12.85)
  - `blue_ensuite.tile_trim` (starts at x 0.50)
- Balcony module. The deck grew to x 0.195..2.315, y 17.36..18.48 (it was x 0..2.30, y to 18.41), and the envelope
  rebuilt the railing (`balcony.structure`: 48 mm tubes, top about 4.12).
  - These now intersect the rail tubes (28 to 121 triangles each): `balcony.planter.0`, `.planter.1` and `.planter.2`
    (y 18.348..18.60, z 3.89..4.104), `balcony.petunias` (x 1.817..2.184, y 18.415..18.604) and `balcony.planter.3`
    (x 2.238..2.49, y 17.63..18.23).
  - Re-hang them on the new front rail (y about 18.48) and the new east rail (x about 2.315..2.35).
  - `balcony.ivy.0`, `.ivy.1` and `.ivy.2` now hang through the edge of `balcony.floor`, which reaches y 18.48.

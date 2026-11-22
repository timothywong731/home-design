# green_bathroom - round-3 brief

Module `blender/rooms/green_bathroom.py`. Decisions: `spec/RECONCILE3.md` (envelope-02, -03; knock-on for `w_gbath`).

## (a) What moved in the shell

- **Window `w_gbath`** (face K) centre x 3.82 -> **3.875** (frame x 3.475..4.275), staying over the back door below
  (which moved to 3.885); at 3.82 its frame would have passed the moved flank corner (3.45). Size 0.80 x 1.68, sill 0.72
  unchanged.
- East wall `w_east_1b` 0.23 -> 0.35 thick outwards; K wall `w_main_rear_1c` runs to x 4.475; inner faces unchanged. Room
  3.05 x 3.78, ceiling 2.75 unchanged. `w_green_rear_e` is 2.77 high (green bedroom ceiling).

Exact spec changes (old -> new):

<!-- diff:begin (generated from spec/house.json) -->
- `walls[w_east_1b].a`: [4.415, 4.89] -> [4.475, 4.89]
- `walls[w_east_1b].b`: [4.415, 8.88] -> [4.475, 8.88]
- `walls[w_east_1b].thickness`: 0.23 -> 0.35
- `walls[w_green_rear_e].b`: [4.415, 4.89] -> [4.475, 4.89]
- `walls[w_green_rear_e].height`: 2.85 -> 2.77
- `walls[w_main_rear_1b].b`: [3.25, 8.88] -> [3.275, 8.88]
- `walls[w_main_rear_1c].a`: [3.25, 8.88] -> [3.275, 8.88]
- `walls[w_main_rear_1c].b`: [4.415, 8.88] -> [4.475, 8.88]
- `openings[w_gbath].center`: [3.82, 8.88] -> [3.875, 8.88]
<!-- diff:end -->

## (b) Surveyors' notes (dims_1, dims_envelope merged)

- Ceiling 2.75 stands (2.69-2.77 from v4 t164.5), the same plane as the bedroom ceiling. Plan size, window and fittings
  were not audited.
- From outside (v11 t62-64, low confidence): window frame about 0.76 wide, sill about Z 4.30 (model 4.14); the black
  eaves gutter sits directly over its head (v13 t28); the rear roof slope is now 35 deg with the gutter at about 6.15.

## (c) New footage

- Outside only: v11 61-66 (face K from the passage), v13 t28 (from the Lavender Room window).

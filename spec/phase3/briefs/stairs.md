# stairs (main flight, ground to first floor) - round-3 brief

Module `blender/rooms/stairs.py`; the flight carcass is `lib/stairs.py` (shell). Decisions: `spec/RECONCILE3.md` (vert-01;
dims_1-10 rejected).

## (a) What moved in the shell

- **`stair_main`: 15 risers -> 14**, rise 0.19 -> **0.2036** (stored as 2.85 / 14 = 0.20357142857), going 0.23 ->
  **0.253**, straightRisers 12 -> 11. The three kite winders are unchanged (bullnose from (0.65, 5.05), R2 to (0.79,
  5.19), R3 to (0.99, 5.39), turning newel (0.20, 5.42)). Square risers R4..R14 at y **5.600, 5.853, 6.106, 6.359, 6.612,
  6.865, 7.118, 7.371, 7.624, 7.877, 8.130**; R14 is the nosing of the quarter landing (Z 2.85). Tread n at Z 0.2036 n
  (tread 13 = 2.646 for y 7.877..8.13). Pitch 38.8 deg (was 39.6 with 0.19 / 0.23 - the flight looks the same; the
  treads are fewer and taller).
- toZ, landingZ, lastRiserY, winders, the well and all floor levels are unchanged. Headroom rechecked: 2.15 at the
  basement door, 2.15 under the front landing at y 6.06, 2.17-2.30 under the second flight.
- Knock-ons in the spec notes: `lobby_cupboard_interior` sits under tread 13 (Z 2.646; cupboard top 2.587, same gap as
  before); `hall_stair_diag` dado rake 0.965 -> 1.37. Plan label 15R -> 14R comes from the spec.
- Outside this unit: `docs/test/geom.test.mjs` line 159 hard-codes the 15-riser flight (viewer owner), and
  `blender/test_ctx.py` / `test_shell.py` assert the old tread heights (foundation owners).

Exact spec changes (old -> new):

<!-- diff:begin (generated from spec/house.json) -->
- `stairs[stair_main].risers`: 15 -> 14
- `stairs[stair_main].rise`: 0.19 -> 0.20357142857142857
- `stairs[stair_main].going`: 0.23 -> 0.253
- `stairs[stair_main].straightRisers`: 12 -> 11
- `stairs[stair_main].walk.risers`: [[[0.2, 5.42], [0.65, 5.05]], [[0.2, 5.42], [0.79, 5.19]], [[0.2, 5.42], [0.99, 5.39]], [[0.15, 5.6], [0.99, 5.6]], [[0.15, 5.83], [0.99, 5.83]], [[0.15, 6.06], [0.99, 6.06]], [[0.15, 6.29], [0.99, 6.29]], [[0.15, 6.52], [0.99, 6.52]], [[0.15, 6.75], [0.99, 6.75]], [[0.15, 6.98], [0.99, 6.98]], [[0.15, 7.21], [0.99, 7.21]], [[0.15, 7.44], [0.99, 7.44]], [[0.15, 7.67], [0.99, 7.67]], [[0.15, 7.9],  ... -> [[[0.2, 5.42], [0.65, 5.05]], [[0.2, 5.42], [0.79, 5.19]], [[0.2, 5.42], [0.99, 5.39]], [[0.15, 5.6], [0.99, 5.6]], [[0.15, 5.853], [0.99, 5.853]], [[0.15, 6.106], [0.99, 6.106]], [[0.15, 6.359], [0.99, 6.359]], [[0.15, 6.612], [0.99, 6.612]], [[0.15, 6.865], [0.99, 6.865]], [[0.15, 7.118], [0.99, 7.118]], [[0.15, 7.371], [0.99, 7.371]], [[0.15, 7.624], [0.99, 7.624]], [[0.15, 7.877], [0.99, 7.877 ...
<!-- diff:end -->

## (b) Surveyors' notes (dims_vert, dims_1 merged)

- Rebuild from the corrected stair_main: wall string, raking dado, spandrel top edge and handrail follow the 38.8 deg
  pitch. Ten straight treads T4..T13 carry twenty spindles (two per tread). Recheck the top newel / handrail junction at
  tread 13 and the overhead cupboard clearance. Carpet, string, newel and balustrade materials unchanged.
- Count evidence: v1 t242.0 / t241.5 (whole flight from the foot: 14 nosing lines, the 14th with the landing wall and
  dado behind; 11 square nosings above 3 winders), v3 t15.5 / t16 / t16.37 / t19, v6 t37.5 (from the landing); the
  hall-side cut string shows ten tread-end returns T4..T13 (v2 t520.5, t520.9; v1 t776.25). Rise: v1 t751.33 puts the top
  five returns at Z 2.66, 2.46, 2.26, 2.07, 1.85 (step 0.202). Annotated count: `reference/work/r3_dims_vert/a_v1_t242_count.jpg`.
- Pitch measured 36-39 deg by vanishing points (weak); the top nosing may really be nearer y 7.7 than 8.13 - the end
  positions need a hall Y-chain pass (open question).
- Quarter landing measured 0.84 x 1.04 (v3 t36.5, floor rectification) against 0.60 modelled - **not placed** (rejected
  this round): a deeper landing needs either the first-floor north wall at about 9.17 or the top nosing about 0.44
  further south, and neither fits the present chains. If adopted later, the landing, the well and the flat soffit over the
  lobby (y 7.68..8.73) have to be reconciled with the top nosing.

## (c) New footage

- None (the flight is not in v8-v13; the audit re-read v1, v2, v3, v6).

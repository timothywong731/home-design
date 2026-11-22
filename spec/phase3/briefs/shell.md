# shell (walls, floors, ceilings, joinery, trim) - round-3 brief

Foundation unit: `blender/lib/shell.py`, `lib/stairs.py`, `lib/joinery.py`, `lib/mouldings.py`, `lib/materials.py`.
Decisions: `spec/RECONCILE3.md`. Room-by-room re-fit notes are in the room briefs; this lists what the shell has to follow.

## (a) What moved in the shell

**Outer walls thicken outwards on unchanged inner faces**
- East wall of the main house (ids `w_party_e_*`, `w_east_1*`, `w_east_2*`; it is external, facing the alley): 0.23 ->
  **0.35**, centre 4.415 -> 4.475, outer face 4.65.
- Back-addition flank walls (`w_flank_*`): 0.30 -> **0.35**, centre 3.25 -> 3.275, outer face 3.45; `w_flank_1_ensuite`
  0.50 -> 0.55 (centre 3.175). Openings on these walls keep their along-wall positions.

**Ground floor**
- Vestibule 1.86 deep between the thresholds (inner screen at 1.91), front recess 0..0.99, piers / vault 0.99..1.44, east
  face of the front recess x 0.75; `w_bay_cheek_w` 0.28 thick (centre 0.89). Haunch features `vest_haunch_w/_e` deleted;
  new `vest_ceiling_slope` (ceiling_haunch along y: 2.62 at y 0 -> 2.85 at y 0.62); no cornice in the vestibule. Street
  door 1.26 leaves / 1.39 frame, head 1.95; transom and frame top unchanged.
- Living bay 1.03..3.93 (nib chamfer corners (1.03, 0.99), (3.93, 0.99)); `w_bay_cheek_e` 0.32 thick (faces 3.93 / 4.25);
  new feature `living_bay_cheek_w_reveal` (type reveal, 0.20 deep).
- Hall arch `a_hall` / `hall_arch`: semicircle springing 2.08, crown 2.55, corbels 1.75-2.08 (haunch field removed).
  Hallway ceiling zones: `rear_hall` now only y 8.13..9.03 (2.84), new `rear_corridor` y 9.03..12.23 at **2.70**;
  `lib/mouldings.py` hangs `cornice_hall` on zone `rear_hall` - add `rear_corridor`. Pilaster tops 2.84 (s) / 2.70 (n).
- Main flight `stair_main` **14 risers** of 0.2036, going 0.253 (lib/stairs carcass, soffit 0.27 under the nosing line).
- Dining: west face -0.59 (`w_party_w_dining` 0.29 thick), ceiling and walls **2.62**; cornice lower edge should be at
  **2.53**: reduce `cornice_dining` (mouldings.py) from a 0.150 drop to about 0.09 (projection about 0.12). North wall
  openings on axis 1.255 (side windows 0.65 x 2.00, transom 1.32).
- Back door `d_back` 0.79 wide at x 3.885 (frame 3.49..4.28), `kitchen_backdoor_reveal` x 3.48..4.29.
- `w_wc` exterior frame 0.82 from sill 1.10 (interior cistern ledge 1.22); `w_utility` frame 0.70 x 0.98 from 0.92
  (interior board 1.05): where the joinery draws the frame from the opening, let the outside frame run lower behind the
  interior sill / ledge.

**First floor**
- Green bedroom ceiling **6.19** (2.77; cornice underside 2.69); bay 1.11..3.85; first-floor bay cheek walls 0.36 / 0.40.
- Rear corridor / arch bay east wall x 0.47, partition centreline 0.52 (`w_corr_yellow`, `w_bay_ensuite`,
  `w_recess_ensuite`, `w_main_rear_1a`, `w_yellow_n`, `w_ensuite_n`, `w_blue_s`, `v_ql_n`), ceiling **5.64** (2.60);
  `w_arch1` 0.12 thick at 11.42; `a_landing1` 1.00 wide, crown 2.12, springing 1.62; chamfer (0.54, 8.73)-(0.47, 8.80);
  `steps_ql_rear` riser line to x 0.54.
- Yellow room 0.57..3.10; en-suite 0.57..2.90; blue-bedroom recess to 0.47.
- Balcony 2.12 x 1.12 at x 0.195..2.315 (balcony door axis 1.255).

**Second floor and loft**
- Hall east wall x 0.32, partitions on 0.37; `w_arch2` / `w_purple_n` 0.16 thick on 11.58; `a_landing2` 0.90, springing
  1.72; the east nib x 0.25..0.32 (dado and skirting returned round its south, west and north faces) has no spec field.
  The first- and second-floor arch walls no longer stack (validator stack check removed with a comment).
- Lavender Room 0.42..3.10 x 9.55..11.50; `w_addition_s_2` 0.70 thick on 9.20 (8.85..9.55; the zone 8.73..8.85 above the
  old rear wall is unbuilt - check that the shell closes it, it lies under nothing but the main rear roof).
- Bathroom2 0.42..3.10 x 11.66..13.70; `d_bath2` 686 leaf; new `bath2_shower_lining` (boxing 0.05); `bath2_pipe_boxing`
  y 11.66..12.25.
- Rose Room neck 0.97 x 0.80, main room 13.84..16.86; `w_bath2_study` 0.14 on 13.77; window 1.55 x 1.56 from 0.58,
  transom 1.70, lower lights top-hung. Lavender window 0.82 wide, lower light top-hung.
- Slate Room: front knee wall **1.08**, front ceiling stopgap z = 6.30 + 0.50 y; rear slope 35 deg (z = 12.33 - 0.70 y),
  flat strip to y 5.31 east of x 1.25; rear knee wall **1.23**; hatches front 0.90 / 0.03 (east one at x 2.48), rear 0.91
  / 0.15; Velux 7.82..8.49. Eaves front lining offset -0.17 (1.00 at the knee-wall back); bay tunnel to Z 8.19 over x
  1.11..3.85; eaves rear lining 1.16 at the knee-wall back. Inside the tunnel the knee-wall back must stand to 1.20 above
  the floor (it is clipped to the old gable planes at 0.86-0.90). Slate Room skirting 0.09.

**Library tests that assert old numbers** (foundation owners; none edited here):
`test_shell.py` l.97 (hallway ceiling set now includes 2.70), l.113 (`vestibule.haunch.vest_haunch_w/_e` ->
`vestibule.haunch.vest_ceiling_slope`), l.119 (loft ceiling min 7.41 -> 7.57), l.131 (stair_main tread heights 0.2036 n),
l.190 (downlight z on the old front plane 5.9435 + 0.57735 y -> 6.30 + 0.50 y); `test_joinery.py` l.62 (living bay corner
(1.1, 0.99) -> (1.03, 0.99)); `test_ctx.py` (chamfer, bay corners, eaves / shed ceilings, porch plane, stair, falls,
zones_of('front'), side_alley has no fall any more).

Exact spec changes (old -> new; walls and flights of every unit):

<!-- diff:begin (generated from spec/house.json) -->
- `.bounds.maxX`: 4.53 -> 4.65
- `.siteBounds.maxY`: 28.9 -> 31.0
- `walls[w_green_rear].height`: 2.85 -> 2.77
- `walls[w_main_rear_1a].a`: [0.3, 8.88] -> [0.52, 8.88]
- `walls[w_corr_yellow].a`: [0.3, 8.88] -> [0.52, 8.88]
- `walls[w_corr_yellow].b`: [0.3, 11.35] -> [0.52, 11.42]
- `walls[w_corr_yellow].height`: 2.45 -> 2.6
- `walls[w_arch1].a`: [-0.765, 11.35] -> [-0.765, 11.42]
- `walls[w_arch1].b`: [0.45, 11.35] -> [0.52, 11.42]
- `walls[w_arch1].thickness`: 0.3 -> 0.12
- `walls[w_arch1].height`: 2.45 -> 2.6
- `walls[w_bay_ensuite].a`: [0.45, 11.1] -> [0.52, 11.1]
- `walls[w_bay_ensuite].b`: [0.45, 12.455] -> [0.52, 12.455]
- `walls[w_bay_ensuite].height`: 2.5 -> 2.6
- `walls[w_blue_s].b`: [0.45, 12.455] -> [0.52, 12.455]
- `walls[v_ql_n].b`: [0.35, 8.73] -> [0.54, 8.73]
- `stairs[stair_main].risers`: 15 -> 14
- `stairs[stair_main].rise`: 0.19 -> 0.20357142857142857
- `stairs[stair_main].going`: 0.23 -> 0.253
- `stairs[stair_main].straightRisers`: 12 -> 11
- `stairs[stair_main].walk.risers`: [[[0.2, 5.42], [0.65, 5.05]], [[0.2, 5.42], [0.79, 5.19]], [[0.2, 5.42], [0.99, 5.39]], [[0.15, 5.6], [0.99, 5.6]], [[0.15, 5.83], [0.99, 5.83]], [[0.15, 6.06], [0.99, 6.06]], [[0.15, 6.29], [0.99, 6.29]], [[0.15, 6.52], [0.99, 6.52]], [[0.15, 6.75], [0.99, 6.75]], [[0.15, 6.98], [0.99, 6.98]], [[0.15, 7.21], [0.99, 7.21]], [[0.15, 7.44], [0.99, 7.44]], [[0.15, 7.67], [0.99, 7.67]], [[0.15, 7.9],  ... -> [[[0.2, 5.42], [0.65, 5.05]], [[0.2, 5.42], [0.79, 5.19]], [[0.2, 5.42], [0.99, 5.39]], [[0.15, 5.6], [0.99, 5.6]], [[0.15, 5.853], [0.99, 5.853]], [[0.15, 6.106], [0.99, 6.106]], [[0.15, 6.359], [0.99, 6.359]], [[0.15, 6.612], [0.99, 6.612]], [[0.15, 6.865], [0.99, 6.865]], [[0.15, 7.118], [0.99, 7.118]], [[0.15, 7.371], [0.99, 7.371]], [[0.15, 7.624], [0.99, 7.624]], [[0.15, 7.877], [0.99, 7.877 ...
- `stairs[steps_ql_rear].riserLines`: [[[0.15, 8.13], [0.15, 8.73], [0.35, 8.73]]] -> [[[0.15, 8.13], [0.15, 8.73], [0.54, 8.73]]]
- `walls[w_hall_purple].a`: [0.27, 9.01] -> [0.37, 9.2]
- `walls[w_hall_purple].b`: [0.27, 11.35] -> [0.37, 11.58]
- `walls[w_arch2].a`: [-0.765, 11.35] -> [-0.765, 11.58]
- `walls[w_arch2].b`: [0.35, 11.35] -> [0.37, 11.58]
- `walls[w_arch2].thickness`: 0.3 -> 0.16
- `walls[w_hall_bath2].a`: [0.35, 11.35] -> [0.37, 11.58]
- `walls[w_hall_bath2].b`: [0.35, 12.99] -> [0.37, 12.99]
- `walls[w_study_door].b`: [0.35, 12.99] -> [0.37, 12.99]
- `walls[v_head_jog].b`: [0.22, 8.73] -> [0.32, 8.73]
- `walls[w_east_1a].a`: [4.415, 0.865] -> [4.475, 0.865]
- `walls[w_east_1a].b`: [4.415, 4.89] -> [4.475, 4.89]
- `walls[w_east_1a].thickness`: 0.23 -> 0.35
- `walls[w_front_1_w].b`: [1.03, 0.865] -> [0.93, 0.865]
- `walls[w_front_1_e].a`: [4.025, 0.865] -> [4.05, 0.865]
- `walls[w_front_1_e].b`: [4.415, 0.865] -> [4.475, 0.865]
- `walls[w_bay_front_1].a`: [1.03, 0.01] -> [0.93, 0.01]
- `walls[w_bay_front_1].b`: [4.025, 0.01] -> [4.05, 0.01]
- `walls[w_bay_cheek_w_1].a`: [1.03, 0.01] -> [0.93, 0.01]
- `walls[w_bay_cheek_w_1].b`: [1.03, 0.865] -> [0.93, 0.865]
- `walls[w_bay_cheek_w_1].thickness`: 0.26 -> 0.36
- `walls[w_bay_cheek_e_1].a`: [4.025, 0.01] -> [4.05, 0.01]
- `walls[w_bay_cheek_e_1].b`: [4.025, 0.865] -> [4.05, 0.865]
- `walls[w_bay_cheek_e_1].thickness`: 0.25 -> 0.4
- `walls[w_green_rear_e].b`: [4.415, 4.89] -> [4.475, 4.89]
- `walls[w_green_rear_e].height`: 2.85 -> 2.77
- `walls[w_east_1b].a`: [4.415, 4.89] -> [4.475, 4.89]
- `walls[w_east_1b].b`: [4.415, 8.88] -> [4.475, 8.88]
- `walls[w_east_1b].thickness`: 0.23 -> 0.35
- `walls[w_main_rear_1b].b`: [3.25, 8.88] -> [3.275, 8.88]
- `walls[w_main_rear_1c].a`: [3.25, 8.88] -> [3.275, 8.88]
- `walls[w_main_rear_1c].b`: [4.415, 8.88] -> [4.475, 8.88]
- `walls[w_yellow_n].a`: [0.3, 11.1] -> [0.52, 11.1]
- `walls[w_yellow_n].b`: [3.25, 11.1] -> [3.275, 11.1]
- `walls[w_flank_1_yellow].a`: [3.25, 8.88] -> [3.275, 8.88]
- `walls[w_flank_1_yellow].b`: [3.25, 11.1] -> [3.275, 11.1]
- `walls[w_flank_1_yellow].thickness`: 0.3 -> 0.35
- `walls[w_recess_ensuite].a`: [0.45, 12.455] -> [0.52, 12.455]
- `walls[w_recess_ensuite].b`: [0.45, 12.9] -> [0.52, 12.9]
- `walls[w_ensuite_n].a`: [0.45, 12.9] -> [0.52, 12.9]
- `walls[w_ensuite_n].b`: [3.25, 12.9] -> [3.275, 12.9]
- `walls[w_flank_1_blue].a`: [3.25, 12.9] -> [3.275, 12.9]
- `walls[w_flank_1_blue].b`: [3.25, 17.11] -> [3.275, 17.11]
- `walls[w_flank_1_blue].thickness`: 0.3 -> 0.35
- `walls[w_rear_1].b`: [3.25, 17.11] -> [3.275, 17.11]
- `walls[w_flank_1_ensuite].a`: [3.15, 11.1] -> [3.175, 11.1]
- `walls[w_flank_1_ensuite].b`: [3.15, 12.9] -> [3.175, 12.9]
- `walls[w_flank_1_ensuite].thickness`: 0.5 -> 0.55
- `walls[w_addition_s_2].a`: [0.27, 9.01] -> [0.37, 9.2]
- `walls[w_addition_s_2].b`: [3.25, 9.01] -> [3.275, 9.2]
- `walls[w_addition_s_2].thickness`: 0.56 -> 0.7
- `walls[w_purple_n].a`: [0.35, 11.35] -> [0.37, 11.58]
- `walls[w_purple_n].b`: [3.25, 11.35] -> [3.275, 11.58]
- `walls[w_purple_n].thickness`: 0.3 -> 0.16
- `walls[w_flank_2_purple].a`: [3.25, 9.01] -> [3.275, 9.2]
- `walls[w_flank_2_purple].b`: [3.25, 11.35] -> [3.275, 11.58]
- `walls[w_flank_2_purple].thickness`: 0.3 -> 0.35
- `walls[w_neck_bath2].a`: [0.35, 12.99] -> [0.37, 12.99]
- `walls[w_neck_bath2].b`: [0.35, 13.925] -> [0.37, 13.77]
- `walls[w_bath2_study].a`: [0.35, 13.925] -> [0.37, 13.77]
- `walls[w_bath2_study].b`: [3.25, 13.925] -> [3.275, 13.77]
- `walls[w_bath2_study].thickness`: 0.45 -> 0.14
- `walls[w_flank_2_study].a`: [3.25, 13.925] -> [3.275, 13.77]
- `walls[w_flank_2_study].b`: [3.25, 17.11] -> [3.275, 17.11]
- `walls[w_flank_2_study].thickness`: 0.3 -> 0.35
- `walls[w_rear_2].b`: [3.25, 17.11] -> [3.275, 17.11]
- `walls[w_flank_2_bath].a`: [3.25, 11.35] -> [3.275, 11.58]
- `walls[w_flank_2_bath].b`: [3.25, 13.925] -> [3.275, 13.77]
- `walls[w_flank_2_bath].thickness`: 0.3 -> 0.35
- `walls[w_east_2b].a`: [4.415, 2.49] -> [4.475, 2.49]
- `walls[w_east_2b].b`: [4.415, 6.64] -> [4.475, 6.64]
- `walls[w_east_2b].thickness`: 0.23 -> 0.35
- `walls[w_knee_front].b`: [4.415, 2.49] -> [4.475, 2.49]
- `walls[w_knee_front].height`: 0.92 -> 1.08
- `walls[w_knee_rear].b`: [4.415, 6.64] -> [4.475, 6.64]
- `walls[w_knee_rear].height`: 1.42 -> 1.23
- `walls[w_east_2a].a`: [4.415, 0.865] -> [4.475, 0.865]
- `walls[w_east_2a].b`: [4.415, 2.49] -> [4.475, 2.49]
- `walls[w_east_2a].thickness`: 0.23 -> 0.35
- `walls[w_east_2c].a`: [4.415, 6.64] -> [4.475, 6.64]
- `walls[w_east_2c].b`: [4.415, 8.88] -> [4.475, 8.88]
- `walls[w_east_2c].thickness`: 0.23 -> 0.35
- `walls[w_party_w_vest].b`: [-0.765, 1.78] -> [-0.765, 1.91]
- `walls[w_party_w_hall].a`: [-0.765, 1.78] -> [-0.765, 1.91]
- `walls[w_front_vest].b`: [1.0, -0.06] -> [0.89, -0.06]
- `walls[w_bay_cheek_w].a`: [1.0, -0.06] -> [0.89, -0.06]
- `walls[w_bay_cheek_w].b`: [1.0, 0.865] -> [0.89, 0.865]
- `walls[w_bay_cheek_w].thickness`: 0.2 -> 0.28
- `walls[w_front_nib_w].b`: [1.1, 0.865] -> [1.03, 0.865]
- `walls[w_screen_inner].a`: [-0.765, 1.78] -> [-0.765, 1.91]
- `walls[w_screen_inner].b`: [0.725, 1.78] -> [0.725, 1.91]
- `walls[w_vest_living].b`: [0.725, 1.78] -> [0.725, 1.91]
- `walls[w_hall_living].a`: [0.725, 1.78] -> [0.725, 1.91]
- `features[vest_ceiling_slope]` new: {"id": "vest_ceiling_slope", "level": "G", "type": "ceiling_haunch", "room": "vestibule", "polygon": [[-0.65, 0], [0.75, 0], [0.75, 0.62], [-0.65, 0.62]], "z": [2.62, 2.85], "wallAt": 0.0}
- `walls[w_front_bay].a`: [1.0, -0.06] -> [0.89, -0.06]
- `walls[w_front_bay].b`: [4.075, -0.06] -> [4.09, -0.06]
- `walls[w_bay_cheek_e].a`: [4.075, -0.06] -> [4.09, -0.06]
- `walls[w_bay_cheek_e].b`: [4.075, 0.865] -> [4.09, 0.865]
- `walls[w_bay_cheek_e].thickness`: 0.15 -> 0.32
- `walls[w_front_nib_e].a`: [4.0, 0.865] -> [4.09, 0.865]
- `walls[w_front_nib_e].b`: [4.415, 0.865] -> [4.475, 0.865]
- `walls[w_cross].b`: [4.415, 5.25] -> [4.475, 5.25]
- `walls[w_party_e_living].a`: [4.415, 0.865] -> [4.475, 0.865]
- `walls[w_party_e_living].b`: [4.415, 5.25] -> [4.475, 5.25]
- `walls[w_party_e_living].thickness`: 0.23 -> 0.35
- `walls[w_party_w_dining].a`: [-0.765, 12.295] -> [-0.735, 12.295]
- `walls[w_party_w_dining].b`: [-0.765, 17.11] -> [-0.735, 17.11]
- `walls[w_party_w_dining].thickness`: 0.23 -> 0.29
- `walls[w_party_w_dining].height`: 2.8 -> 2.62
- `walls[w_flank_dining].a`: [3.25, 12.295] -> [3.275, 12.295]
- `walls[w_flank_dining].b`: [3.25, 17.11] -> [3.275, 17.11]
- `walls[w_flank_dining].thickness`: 0.3 -> 0.35
- `walls[w_flank_dining].height`: 2.8 -> 2.62
- `walls[w_dining_s_utility].b`: [3.25, 12.295] -> [3.275, 12.295]
- `walls[w_dining_s_utility].height`: 2.8 -> 2.62
- `walls[w_dining_n].b`: [3.25, 17.11] -> [3.275, 17.11]
- `walls[w_dining_n].height`: 2.8 -> 2.62
- `walls[w_party_e_kitchen].a`: [4.415, 5.25] -> [4.475, 5.25]
- `walls[w_party_e_kitchen].b`: [4.415, 8.88] -> [4.475, 8.88]
- `walls[w_party_e_kitchen].thickness`: 0.23 -> 0.35
- `walls[w_kitchen_n].b`: [3.25, 9.045] -> [3.275, 9.045]
- `walls[w_kitchen_n_ext].a`: [3.25, 8.88] -> [3.275, 8.88]
- `walls[w_kitchen_n_ext].b`: [4.415, 8.88] -> [4.475, 8.88]
- `walls[w_wc_utility].b`: [3.25, 10.2] -> [3.275, 10.2]
- `walls[w_flank_wc].a`: [3.25, 8.88] -> [3.275, 8.88]
- `walls[w_flank_wc].b`: [3.25, 10.2] -> [3.275, 10.2]
- `walls[w_flank_wc].thickness`: 0.3 -> 0.35
- `walls[w_flank_utility].a`: [3.25, 10.2] -> [3.275, 10.2]
- `walls[w_flank_utility].b`: [3.25, 12.295] -> [3.275, 12.295]
- `walls[w_flank_utility].thickness`: 0.3 -> 0.35
<!-- diff:end -->

## (b) Surveyors' notes for the shell (merged)

- Trim: hall dado top 0.965-0.99 everywhere it was checked; skirting 0.17 (Rose Room, second-floor hall); second-floor
  hall cove about 0.10; Rose Room cornice a small stepped ogee (fillet, cyma, bead, fillet), bottom edge 2.46, drop and
  projection about 0.10 - not a plain 0.12 cove (t147, t193.4); first-floor rear corridor small plain cove; dining cornice
  drop at most 0.13-0.14.
- Floors: oak boards along Y at **0.24 pitch** in hall, living and dining (not 0.22; dims_G); kitchen tiles about 0.245
  wide (not 0.20), white 3-4 mm grout, planks along Y; second-floor carpets as modelled; eaves voids one grey
  concrete-effect sheet vinyl (#807D77).
- Bay shutters (living): blade pitch about 70 +/- 8 mm (76 or 89 mm blades, 13-15 per lower panel) against 52 mm in
  `lib/joinery._shutter` - low-medium confidence (v10 t42, t56).
- Windows with top-hung lower lights: `w_study` (both lower lights, about 35 deg, brass espagnolette centred on each bottom
  rail, lock keeps on the bottom frame member) and `w_purple` (about 30 deg); joinery.py supports `top_hung` with an angle.
- Doors: all hinged first-floor leaves 762 x 1981; second-floor bathroom, Rose Room and loft doors 686 leaves.
- Wall below the hall dado (ground and second floor, one paint) reads darker and warmer, estimate #C0B9AD against #C8C5BB
  (change both or neither).
- Porch / vestibule: no front-wall return beside the street door; the dado / skirting stub is on the cheek wall
  (vestibule module).

## (c) New footage

- All six videos (v8-v13) touch the shell somewhere; see the room briefs. No new footage of the basement, ground-floor
  hall, kitchen interior beyond the back door, or first floor.

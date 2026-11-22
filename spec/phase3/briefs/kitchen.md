# kitchen - round-3 brief

Module `blender/rooms/kitchen.py`. Decisions: `spec/RECONCILE3.md` (passage-04, envelope-02, -03, -14).

## (a) What moved in the shell

- **Back door `d_back`**: frame 0.84 -> **0.79** wide; centre x 3.82 -> **3.885**; hinge (east) x 4.24 -> **4.28**. Frame
  x 3.49..4.28: outside 0.04 from the moved flank corner (3.45) and 0.37 from the east corner (4.65); inside 0.02 from the
  kitchen's east wall (4.30). Height 2.04 and transom 2.64 unchanged. `kitchen_backdoor_reveal` follows (x 3.48..4.29,
  y 8.73..8.85). The hinge-side return to the east wall is now almost nil: re-fit anything between door and east wall.
- **East wall** (`w_party_e_kitchen`, external, facing the alley): 0.23 -> 0.35 thick outwards, inner face 4.30
  unchanged. Room 3.05 x 3.42, ceiling 2.95 unchanged.
- Kitchen steps outside start at the flank x 3.45 (were 3.40).

Exact spec changes (old -> new):

<!-- diff:begin (generated from spec/house.json) -->
- `walls[w_cross].b`: [4.415, 5.25] -> [4.475, 5.25]
- `walls[w_party_e_kitchen].a`: [4.415, 5.25] -> [4.475, 5.25]
- `walls[w_party_e_kitchen].b`: [4.415, 8.88] -> [4.475, 8.88]
- `walls[w_party_e_kitchen].thickness`: 0.23 -> 0.35
- `walls[w_kitchen_n].b`: [3.25, 9.045] -> [3.275, 9.045]
- `walls[w_kitchen_n_ext].a`: [3.25, 8.88] -> [3.275, 8.88]
- `walls[w_kitchen_n_ext].b`: [4.415, 8.88] -> [4.475, 8.88]
- `openings[d_back].center`: [3.82, 8.88] -> [3.885, 8.88]
- `openings[d_back].width`: 0.84 -> 0.79
- `openings[d_back].hingeAt`: [4.24, 8.88] -> [4.28, 8.88]
- `features[kitchen_backdoor_reveal].polygon`: [[3.39, 8.73], [4.25, 8.73], [4.25, 8.85], [3.39, 8.85]] -> [[3.48, 8.73], [4.29, 8.73], [4.29, 8.85], [3.48, 8.85]]
<!-- diff:end -->

## (b) Surveyors' notes (passage, dims_G merged)

**Back door** (v11 f_0001-f_0020 inside; v11 f_0062-f_0066 and v2 t342 outside): frame 0.79 x 2.68 high; sash 0.72 x
1.98; clear opening 0.68 x 2.00. Obscure stippled glass 0.525 x 0.98, glass z 0.96..1.91; mid-rail z 0.82..0.96 with a
drip bar outside; lower flat panel 0.57 x 0.77 in a mitred bead. **Cat flap** white frame 0.215 x 0.23 sitting on the
panel's bottom bead, bottom z 0.14 (model 0.19), **centred in the lower panel** (the 0.06 east offset was not confirmed:
v11 f_0005, v13 t33), clear arched flap, small red rotary lock at lower right inside. Transom z 2.04..2.15, obscure
fanlight pane 0.67 x 0.465. White hooded slot trickle vent 0.30 long in the leaf's top rail (f_0007, f_0008). Three white
flag hinges on the east jamb; opens inward to 95 deg against the east wall (f_0017-f_0020). Lever on a 0.24 x 0.03
backplate with euro cylinder on the west stile, both faces, lever z 1.00, polished brass. White uPVC cill 0.035 high with
a brush strip. uPVC true #F2F2EF (sampled #CDCED0 in shade). Glass memo board on the east wall beside the door stays
blank (no writing). Chequer plate on the west return wall is already in kitchen.md.

**Floor tiles** are about 0.245 +/- 0.015 wide, not 0.20: 4.9 tile widths across the 1.25 nook at its plinth (v6 t73.1);
at the sink wall a 196 px door stands against a 103 px tile (v6 t100.7; 0.236 if that door is 450). White grout 3-4 mm,
planks along Y, irregular stagger; tile length not measured. Room size, nook and ceiling not re-checked.

## (c) New footage

- **v11** (PXL_20261121_124951560) **1-17**: back door from inside (frosted glass, cat flap, hinges, cill); 61-66 the
  door from the passage.

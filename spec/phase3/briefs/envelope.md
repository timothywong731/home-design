# envelope (facades, reveals, roof, roof windows, balcony structure) - round-3 brief

Foundation unit: `blender/lib/envelope.py`. Decisions: `spec/RECONCILE3.md` (front-04..-07, -11; porch-09, -10;
envelope-01..-14; floor2b-06; garden-22; eaves_loft-02, -06, -07).

## (a) What moved

- **Faces**: east wall `east_E` 4.53 -> **4.65** (external insulation: render 0.10 proud of the old face 4.55; new field
  `insulation` {proud 0.1, oldFace 4.55, baseRailZ [-0.09, -0.03], below plinth_black}); flank `flank_F` 3.40 -> **3.45**;
  face K x 3.45..4.65; rear `rear_R` to 3.45 (render from the party line to the flank corner, **no exposed brick pier** on
  our side); envelope blocks follow (main G/1/2 to 4.65, rear addition to 3.45). `east_E` keeps extent [0.74, 9.03]
  (envelope-11 rejected) and has **no openings** (blank gable end, black dry-verge trim).
- **Bay**: outer faces on both floors x **0.75..4.25** (was 0.90 / 1.03 .. 4.15); `bay_cheek_w` at 0.75, `bay_cheek_e` at
  4.25 (0.40 behind the east face, joined by a white south-facing return y 0.74, x 4.25..4.65 that carries the security
  light); `front_A` extent to 4.25, `front_B` to 0.75. The ground-floor lights are centred on 2.48 (x 1.175..3.785), the
  first-floor window `w_green_bay` on 2.48; cheek windows `w_bay_cheek_e` y 0.17..0.69, `w_green_cheek_w` x 0.93.
- **Bay gable** 43 deg / ridge 8.295 / x 2.525 -> **50 deg / 8.75 / x 2.48**: `bay_gable_w` [[0.61,-0.42],[2.48,-0.42],
  [2.48,4.33],[0.61,0.46]] z = 5.799 + 1.19 x; `bay_gable_e` [[2.48,-0.42],[4.35,-0.42],[4.35,0.46],[2.48,4.33]] z = 11.701 -
  1.19 x; eave edges at 6.52 (the main gutter level) at x 0.61 / 4.35, 6.64-6.69 at the cheek walls (`gable.eavesZ` 6.69);
  the ridge dies into the main front slope at y 4.33 (was 3.54); valleys from (0.61, 0.46) / (4.35, 0.46).
- **Main roof**: front slope unchanged (30 deg, gutter 6.50); **rear slope 30 -> 35 deg** about the unchanged ridge (y 5.00,
  Z 9.14): z = 12.64 - 0.70 y; it meets the old rear wall head at 6.49 and puts the rear eaves over face K at about 6.15
  (`rear_K.gutterZ` 6.65 -> 6.15 - note envelope.py hangs pitched-eaves gutters on the plane's free edge and does not read
  gutterZ). `stair_dormer` starts at y **5.385** (was 5.47), where the 35-deg plane reaches its flat top 8.87; main_rear's
  notch follows. Velux z 7.82..8.49. Eaves lines follow the faces (flank line x 3.53, rear fascia to 3.45, front eaves to
  0.75).
- **Porch lean-to** `porch_leanto`: c0 3.3111 / cy 0.795 (38.5 deg, slate top 2.85 at the eaves, 3.90 at the abutment) ->
  **c0 3.14 / cy 0.933 (43 deg): 2.58 at y -0.60, 3.83 at the abutment** (0.37 under the first-floor west sill). Polygon x
  to 0.88 (was 0.93): the slates abut the first-floor cheek at 0.75, but the fascia and gutter run on to a stop end at about
  0.88, and `PIPES` hangs a downpipe on the lean-to at x 0.83 (it would crash with the plane ending at 0.75). That
  downpipe ("main eaves, bay west cheek") now runs inside the 0.36 cheek wall (x 0.75..1.11): move it to about x 0.68 (0.07
  west of the cheek face) and let the lean-to stop at 0.75 behind y -0.12.
- **Porch soffit**: raked boarded soffit from 2.63 at the door head (y -0.12) to 2.40 at the fascia (y -0.55) with three
  downlights in a row at x -0.42, 0, 0.42 - `PORCH_SOFFIT_Z = 2.62` (flat) in envelope.py and `CANOPY_Z` in vestibule.py
  have to follow. Gutter Z about 2.42-2.54 (it lies across the top of the transom seen from the street).
- **Openings on the faces**: `d_back` 0.79 at x 3.885; `w_gbath` x 3.875; `w_wc` 0.82 from 1.10; `w_utility` 0.70 x 0.98
  from 0.92; `w_purple` 0.82 at y 10.47; `w_bath2` y 12.57; rear: `d_french` x 1.255, side windows -0.185 / 2.695 (0.65 x
  2.00, heads 2.37, transoms 1.32), `d_balcony` and `w_study` (1.55 x 1.56 from 0.58 above the floor 6.02, transom 1.70) on
  the same axis 1.255. extReveal: `w_study` 0.19, `w_wc` 0.265, `w_utility` 0.06, `w_purple` 0.07, `w_bath2` 0.06, dining
  east windows 0.15, `w_yellow` 0.15.
- **Balcony structure**: platform x 0.195..2.315, y 17.36..18.48 (2.12 x 1.12, centred on 1.255); posts x 0.195 / 1.255 /
  2.315 at y 18.48; round tube about 48 mm (`railing.section` "round_tube", post 0.048), bars 0.14 centres, 7 per side / per
  front bay; wall posts (0.21, 17.36) / (2.30, 17.36); rain pipe x 0.36.
- **Rear chimney** `rear_chimney` x -0.98..-0.53, top 9.87 -> **x -1.17..-0.86, top 9.55**: the brick shaft (0.26 wide, x
  -1.17..-0.91) stands on the neighbour's side of the party line, with a grey sloping haunch on its east side reaching
  about x -0.62 at roof level; the polygon keeps 0.02 on our roof for the generator.
- **New feature `front_party_kneeler`** (type kneeler, not built by any stage yet): party-wall kneeler / stack stub at the
  front eaves on the west party line, x -0.88..-0.55, y 0.30..0.75, Z 5.75..7.3, dark red brick, corbelled; the white front
  gutter stops against it.
- **Neighbours**: east massing +0.37 in x (face 5.80 across the 1.15 alley).

**Test**: `test_envelope.py` fails 3 checks (main_front 23 vertices, bay_gable_w 5, bay_gable_e 4 inside the Slate Room): the measured front knee wall (1.08 at y 2.54) leaves only about 0.15 between the loft ceiling and the 30-deg
roof top, where the roof slab is modelled 0.30 thick. This is the unresolved loft section (RECONCILE3 open question 1),
not an old number: either model the roof build-up over the loft at about 0.15 vertical, or wait for the section to be
re-fitted. (main_rear no longer cuts the loft lobby ceiling since the dormer edge moved to 5.385.)

Exact spec changes (old -> new):

<!-- diff:begin (generated from spec/house.json) -->
- `exterior.envelope.blocks[main].levels`: [{"level": "B", "polygon": [[0.135, 5.07], [4.53, 5.07], [4.53, 8.85], [0.135, 8.85]], "z": [-2.31, 0.0], "below_ground": true}, {"level": "G", "polygon": [[-0.88, -0.12], [4.15, -0.12], [4.15, 0.74], [4.53, 0.74], [4.53, 9.03], [-0.88, 9.03]], "z": [0.0, 3.42]}, {"level": "1", "polygon": [[-0.88, 0.74], [0.9, 0.74], [0.9, -0.12], [4.15, -0.12], [4.15, 0.74], [4.53, 0.74], [4.53, 9.03], [-0.88, 9. ... -> [{"level": "B", "polygon": [[0.135, 5.07], [4.53, 5.07], [4.53, 8.85], [0.135, 8.85]], "z": [-2.31, 0.0], "below_ground": true}, {"level": "G", "polygon": [[-0.88, -0.12], [4.25, -0.12], [4.25, 0.74], [4.65, 0.74], [4.65, 9.03], [-0.88, 9.03]], "z": [0.0, 3.42]}, {"level": "1", "polygon": [[-0.88, 0.74], [0.75, 0.74], [0.75, -0.12], [4.25, -0.12], [4.25, 0.74], [4.65, 0.74], [4.65, 9.03], [-0.88,  ...
- `exterior.envelope.blocks[rear_addition].levels`: [{"level": "G", "polygon": [[-0.88, 9.03], [3.4, 9.03], [3.4, 17.36], [-0.88, 17.36]], "z": [0.0, 3.04]}, {"level": "1", "polygon": [[-0.88, 9.03], [3.4, 9.03], [3.4, 17.36], [-0.88, 17.36]], "z": [3.04, 6.02]}, {"level": "2", "polygon": [[-0.88, 8.73], [3.4, 8.73], [3.4, 17.36], [-0.88, 17.36]], "z": [6.02, 8.87]}] -> [{"level": "G", "polygon": [[-0.88, 9.03], [3.45, 9.03], [3.45, 17.36], [-0.88, 17.36]], "z": [0.0, 3.04]}, {"level": "1", "polygon": [[-0.88, 9.03], [3.45, 9.03], [3.45, 17.36], [-0.88, 17.36]], "z": [3.04, 6.02]}, {"level": "2", "polygon": [[-0.88, 8.73], [3.45, 8.73], [3.45, 17.36], [-0.88, 17.36]], "z": [6.02, 8.87]}]
- `exterior.facades[front_A].extent`: [-0.88, 4.15] -> [-0.88, 4.25]
- `exterior.facades[front_B].extent`: [-0.88, 0.9] -> [-0.88, 0.75]
- `exterior.facades[bay_cheek_w].at`: 0.9 -> 0.75
- `exterior.facades[bay_cheek_e].at`: 4.15 -> 4.25
- `exterior.facades[east_E].at`: 4.53 -> 4.65
- `exterior.facades[east_E].insulation` new: {"proud": 0.1, "oldFace": 4.55, "baseRailZ": [-0.09, -0.03], "below": "plinth_black"}
- `exterior.facades[kitchen_K].extent`: [3.4, 4.53] -> [3.45, 4.65]
- `exterior.facades[flank_F].at`: 3.4 -> 3.45
- `exterior.facades[rear_R].extent`: [-0.88, 3.4] -> [-0.88, 3.45]
- `exterior.neighbours[east].polygon`: [[5.43, -0.5], [10.8, -0.5], [10.8, 17.0], [5.43, 17.0]] -> [[5.8, -0.5], [11.17, -0.5], [11.17, 17.0], [5.8, 17.0]]
- `exterior.neighbours[east].parts`: [{"polygon": [[5.43, 0.74], [10.8, 0.74], [10.8, 5.0], [5.43, 5.0]], "top": {"c0": 6.0728, "cx": 0, "cy": 0.57735}, "covering": "slate"}, {"polygon": [[5.43, 5.0], [10.8, 5.0], [10.8, 9.26], [5.43, 9.26]], "top": {"c0": 11.8467, "cx": 0, "cy": -0.57735}, "covering": "slate"}, {"polygon": [[5.43, 9.26], [10.8, 9.26], [10.8, 14.0], [5.43, 14.0]], "top": 8.9, "covering": "flat_felt", "walls": "stock_ ... -> [{"polygon": [[5.8, 0.74], [11.17, 0.74], [11.17, 5.0], [5.8, 5.0]], "top": {"c0": 6.0728, "cx": 0, "cy": 0.57735}, "covering": "slate"}, {"polygon": [[5.8, 5.0], [11.17, 5.0], [11.17, 9.26], [5.8, 9.26]], "top": {"c0": 11.8467, "cx": 0, "cy": -0.57735}, "covering": "slate"}, {"polygon": [[5.8, 9.26], [11.17, 9.26], [11.17, 14.0], [5.8, 14.0]], "top": 8.9, "covering": "flat_felt", "walls": "stock_ ...
- `roof.planes[main_front].polygon`: [[-0.88, 0.44], [4.53, 0.44], [4.53, 5.0], [-0.88, 5.0]] -> [[-0.88, 0.44], [4.65, 0.44], [4.65, 5.0], [-0.88, 5.0]]
- `roof.planes[main_rear].polygon`: [[-0.88, 5.0], [4.53, 5.0], [4.53, 9.33], [1.35, 9.33], [1.35, 5.47], [-0.88, 5.47]] -> [[-0.88, 5.0], [4.65, 5.0], [4.65, 9.33], [1.35, 9.33], [1.35, 5.385], [-0.88, 5.385]]
- `roof.planes[main_rear].z.c0`: 12.0267 -> 12.64
- `roof.planes[main_rear].z.cy`: -0.57735 -> -0.7
- `roof.planes[main_rear].pitchDeg`: 30 -> 35
- `roof.planes[stair_dormer].polygon`: [[-0.88, 5.47], [1.35, 5.47], [1.35, 8.73], [-0.88, 8.73]] -> [[-0.88, 5.385], [1.35, 5.385], [1.35, 8.73], [-0.88, 8.73]]
- `roof.planes[rear_flat].polygon`: [[-0.88, 8.73], [3.4, 8.73], [3.4, 17.46], [-0.88, 17.46]] -> [[-0.88, 8.73], [3.45, 8.73], [3.45, 17.46], [-0.88, 17.46]]
- `roof.planes[bay_gable_w].polygon`: [[0.6, -0.42], [2.525, -0.42], [2.525, 3.54], [0.6, 0.44]] -> [[0.61, -0.42], [2.48, -0.42], [2.48, 4.33], [0.61, 0.46]]
- `roof.planes[bay_gable_w].z.c0`: 5.9405 -> 5.799
- `roof.planes[bay_gable_w].z.cx`: 0.9325 -> 1.19
- `roof.planes[bay_gable_w].pitchDeg`: 43 -> 50
- `roof.planes[bay_gable_e].polygon`: [[2.525, -0.42], [4.45, -0.42], [4.45, 0.44], [2.525, 3.54]] -> [[2.48, -0.42], [4.35, -0.42], [4.35, 0.46], [2.48, 4.33]]
- `roof.planes[bay_gable_e].z.c0`: 10.6496 -> 11.701
- `roof.planes[bay_gable_e].z.cx`: -0.9325 -> -1.19
- `roof.planes[bay_gable_e].pitchDeg`: 43 -> 50
- `roof.planes[porch_leanto].polygon`: [[-0.86, -0.58], [0.93, -0.58], [0.93, 0.74], [-0.86, 0.74]] -> [[-0.86, -0.58], [0.88, -0.58], [0.88, 0.74], [-0.86, 0.74]]
- `roof.planes[porch_leanto].z.c0`: 3.3111 -> 3.14
- `roof.planes[porch_leanto].z.cy`: 0.795 -> 0.933
- `roof.planes[porch_leanto].pitchDeg`: 38.5 -> 43
- `roof.ridge.line`: [[-0.88, 5.0], [4.53, 5.0]] -> [[-0.88, 5.0], [4.65, 5.0]]
- `roof.eaves[front].line`: [[-0.88, 0.47], [0.9, 0.47]] -> [[-0.88, 0.47], [0.75, 0.47]]
- `roof.eaves[rear_K].line`: [[3.4, 9.25], [4.53, 9.25]] -> [[3.45, 9.25], [4.65, 9.25]]
- `roof.eaves[rear_K].gutterZ`: 6.65 -> 6.15
- `roof.eaves[flank].line`: [[3.48, 9.03], [3.48, 17.36]] -> [[3.53, 9.03], [3.53, 17.36]]
- `roof.eaves[rear_fascia].line`: [[-0.88, 17.46], [3.4, 17.46]] -> [[-0.88, 17.46], [3.45, 17.46]]
- `roof.gable.ridge`: [[2.525, -0.42], [2.525, 3.54]] -> [[2.48, -0.42], [2.48, 4.33]]
- `roof.gable.ridgeZ`: 8.295 -> 8.75
- `roof.gable.eavesZ`: 6.78 -> 6.69
- `roof.gable.pitchDeg` new: 50
- `exterior.features[rear_chimney].polygon`: [[-0.98, 16.46], [-0.53, 16.46], [-0.53, 17.36], [-0.98, 17.36]] -> [[-1.17, 16.46], [-0.86, 16.46], [-0.86, 17.36], [-1.17, 17.36]]
- `exterior.features[rear_chimney].z`: [0.0, 9.87] -> [0.0, 9.55]
- `exterior.features[front_party_kneeler]` new: {"id": "front_party_kneeler", "type": "kneeler", "polygon": [[-0.88, 0.3], [-0.55, 0.3], [-0.55, 0.75], [-0.88, 0.75]], "z": [5.75, 7.3], "material": "red_brick_dark"}
<!-- diff:end -->

## (b) Surveyors' notes for the envelope (front, porch, passage, garden, floor2_a, floor2_b, dims_envelope merged)

**Front bay, ground floor**: west pilaster against the door frame (zone x 0.80..1.175, shaft about 0.83..1.09), east corner
pilaster zone 3.785..4.285 (about 0.50, wraps the corner), each with three convex reeds, a capital under the cornice and a
plain base block to sill level. Lights 4 x 0.54 with 0.15 mullions; each of the 8 openings has a raised moulded
architrave about 0.04 wide, leaving 0.07 of plain mullion; lights 1 and 4 in both rows are opening sashes with a second
frame (glass about 0.35 wide), 2 and 3 fixed (top-row glass 0.445 x 0.655) (v8 f29). Bay base is ONE textured plane from
sill to paving: remove the projecting plinth. Sill 0.07 thick, 0.08 proud, top Z 0.62. Entablature: architrave tops 2.77,
plain band to 2.97, cornice 2.97..3.34 in four fillets (was 2.90..3.10), returning along the east cheek and the return
(v8 f26, f138).

**Front bay, first floor**: apron 3.34..3.98 with two raised flat hexagonal panels (both ends pointed) 1.47 x 0.34,
centre line Z 3.64, 15 mm proud, about x 0.94..2.41 and 2.55..4.02 (survey 0.86..2.33 / 2.47..3.94 on a 2.40 axis). Window
frame 2.06 wide centred on 2.48 (x 1.45..3.51) x Z 4.12..5.97, mullion centres 0.58 in from each jamb, transom centre
5.44, hood mould to 6.11, sill 3.98..4.12; corner piers each with a sunk panel 0.30 wide from Z 4.08 to 6.14, 0.20 in
from the corner. Side lights casements, centre fixed with a trickle vent. From the street the frame may run from Z 3.98
(low confidence).

**Gable**: 50 deg, ridge Z 8.75 on x 2.48; bargeboards 0.22 deep with a scrolled foot, no finial; timbering (0.09 wide,
0.025 proud, white): king post on the axis from a head band at Z 6.35 to the apex, two short braces forking from it 0.45
below the inner apex, two LONG struts from the king post's foot rising outward at 36 deg from vertical to heads 0.75
either side at Z 7.4, two SHORT struts parallel to them, foot Z 6.4 at 0.9 out, head Z 6.85 at 1.2 out (v8 f26, f42,
f133-136). **The present struts lean the wrong way.**

**East side**: bay cheek white with the ground-floor window (lower light + top light, own sill), a tall first-floor light
with hood and sill and a small raised panel on the cheek apron; the white return to the eaves; from the corner (4.65,
0.74) the mustard insulated render (sampled #B0A682 / #B2A884 sun, #A39875 / #A49A78 shade at the front, #C1BDA6 /
#CEC59E overcast; keep one colour #D2C596 for all render), white bell-cast base rail about 0.25 above the alley floor with
a white corner board / stop at the south end, the old face below painted black (#2A2A2C). Fittings: white meter box 0.41 x
0.56 x 0.21 on the cheek under the sill (y 0.28..0.69, Z 0.02..0.58) with a small white cable box; white 65 mm square
downpipe from the gable's east eaves gutter down the cheek 0.10 behind the front corner to a ground shoe; white twin-head
security light on the return at about (4.45, 0.72, 2.72) (v8 f64-79). On `east_E`, south to north: black cable from the
cornice end, vertical twin black conduit, black vent grille 0.15 at Z about 1.8, two cylindrical wall lights at Z about
2.3-2.65, condenser on brackets (spec feature), white 110 downpipe with swan neck on a concrete pad at the north end (v11
f_0083-f_0105, f_0127-f_0149).

**West / porch**: lean-to x -0.86..0.75 slated, four courses of dark slates 0.6 x 0.3 #4B4E57, dark upstand 0.15 to Z
3.98, lead at the cheek; white square-line gutter 114 (Z about 2.42-2.54, y -0.62..-0.73, brackets about 0.6 apart, stop
end east) on a white fascia about 0.12 behind it; running outlet at the west, two offset bends back to the wall, 65 mm
square white downpipe on the white strip between the frame and the party line, centre about (-0.78, -0.17), clips at
about 0.9 / 1.75, shoe at 0.12 (now at (-0.68, -0.20)). Main eaves gutter turns the internal corner onto the cheek and its
downpipe ends in a two-elbow shoe on the porch roof (v8 f20). West flank of the porch: plain white render about 0.45 back
from the front plane, white boxed bargeboard on the verge; the plaque on the adjoining brick pier is the neighbour's,
omit. Door set outside: frame fills from the white strip to the pilaster, pilaster about 0.43 wide with three flat reeds
and a plinth. The porch survey measured the abutment at 3.13-3.25 and saw only 0.3-0.5 of wall above it (v8 f_0126): the
first-floor west sill datum (4.20) is the open question behind the 3.83 adopted.

**Party-wall kneeler**: 0.23 wide, corbelled 0.28 in five courses, dark red brick (#7A4A3C; dims_envelope: unpainted red
#A4553A, flat stone cap, top about 7.7, x -0.88..-0.55, y 0.3..0.75), from Z about 5.75-6.1 to 7.0-7.7 (0.5 above the
gutter) with a dark sloping cap (v8 f_0015-f_0024, f_0113-f_0115, v9 t15).

**Flank and face K** (v11 f_0035-f_0043, f_0170-f_0179): conduits are twin black ribbed pipes - from the K corner north at
second-floor sill level, down in a rectangular drop just north of the yellow-room window to Z 3.9, north under the en-suite
window and past the stack, then a 0.9 high inverted-U loop into the top of the flank condenser. First-floor soil branch
(110 mm, Z 3.30 falling to 3.10): a vertical capped stub with a 0.13 dome 0.6 south of the stack, and a 50 mm pipe 1.0
long under it with a capped south end joining the stack through a boss. En-suite waste 40 mm from a stack boss 0.5 north,
up 0.3, north 0.6, elbow into the wall. Soil stack at y 12.35: ring-seal sockets every 1.5-2 m, capped boss 0.35 above the
paving on its south side, top third pale grey with a cage cowl. K downpipe 68 mm (measured 0.073), three clips. Flank keeps
a plain black plinth, top about -0.11 (0.19 high), starting north of the soil stack. Windows outside: `w_wc` set 0.20 back
with a white-painted stone sill block 0.50 x 0.10 projecting 0.07; `w_utility` shallow 0.06 reveal with a thin white uPVC
stub cill 0.03 x 0.80 and a slot trickle vent in the head; dining east windows reveal 0.18, stone sill block top z 0.97,
0.10 thick, 0.06 longer than the opening each side; sills #EDEDE8. Face K: black gutter right over the first-floor window
head; main rear slope over K in large-format fibre-cement slates 600 x 300 broken bond, black verge trim on the east edge
(v13 t28). Seen from the Lavender window (v13 f28-f38): black lagged A/C pipes along the flank below the sill level, a
white louvred terminal further north; a white square extractor outlet above the bathroom2 window head.

**Rear**: render to the party line (junction 4.22 from the flank corner), no pier; fascia Z 8.56..8.73 white (#DBD9DB) under
a dark trim to 8.84 (#5F6066); study window frame 1.53 x 1.63 outside with a stone sill 1.75 x 0.14, in a shallow rendered
reveal (about 0.08); wall face flush from the study sill down to the balcony doors (v13 f_0215). Two black corrugated
conduits clipped to the render: a horizontal run about 0.35 below the study sill across the wall and a vertical run up the
west (party) side of the window to the roof edge (v2 t210; v13 f_0213-f_0218); two ribbed hoses with saddle clips at about
0.9 centres below the second-floor sill. Small grey square unit on a bracket east of the balcony doors at first-floor head
height. Render reads pale primrose in sun (#DDD7B6). Balcony door fanlights are top-hung openers; balcony door frame 1.62
wide, head Z 5.34. Rear lantern (black four-sided coach lantern, pagoda cap) at x 2.31. Rear ground-floor openings are
measured from outside at axes 0.875 / 2.342 / 3.767 from the flank corner (x 2.575 / 1.11 / -0.32): the interior screen
puts the axis at 1.255 (adopted); the 0.15 difference is an open question.

**Balcony steel**: top rail and the three front posts round tube about 48 mm with elbow / tee fittings and a visible joint
collar, side rails returning to wall brackets, thin vertical bars at about 0.14, chequer-plate deck screw-fixed along its
edges (estimate #3A3C40); rail colour open (mid grey from above, estimate #6B7076; bars black).

## (c) New footage

- v8 (front elevation, gable, east side from the street, canopy from below), v9 (porch, canopy, door, gable), v11
  (flank, face K, east wall, pipes), v13 207-225 (rear wall, balcony, rear roofs from above).

## Fallout after the foundation round

Gate check of the full build of the current tree (`build/r3/gate/home.blend`, BUILD OK) against `spec/house.json`.
Bounds are world metres of the built objects (x a..b, y c..d, z e..f), measured by `build/r3/gate/audit.py` and
`collide.py` (results in `build/r3/gate/audit_new.json` and `coll_cmp.txt`). Objects that already moved with the spec
are not listed.

These are clashes between the envelope stage and the site stage, found in the foundation-only build
(`build/r3/gate/found.blend`, checked with `fcollide.py`). The details are in site.md under the same heading.
- The canopy downpipe (`facade.pipes.upvc_white`, at (-0.78, -0.17)) runs through the end of `front.front_wall_w`.
- The `facade.east_E.sills` base rail (x 4.618..4.685) runs through both gate frames, `side_passage.street_gate.frame`
  and `side_passage.side_gate.frame`.
- `facade.downpipe.1` runs through `side_passage.kitchen_steps` (x 3.92..4.39, y 9.18..9.35, z -0.28..-0.02).
- The porch soffit is now raked, and the vestibule's outside downlights, still at z 2.62, sit inside the canopy. This is
  hall fallout (see hall.md); it needs no envelope change.

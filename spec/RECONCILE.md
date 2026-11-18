# Reconciliation of room specs and layout into `spec/house.json`

Inputs: `spec/layout.md`, `spec/rooms/*.md` (8 rooms), `reference/transcript.txt`, and my own re-inspection
of frames (stills and scratch scripts in `reference/work/reconcile/`, git-ignored).
Outputs: `spec/house.json` (canonical), `spec/plan_preview.png`, `spec/validate_house.py`, this file, and a
"Reconciled dimensions" section appended to each room spec.

`python spec/validate_house.py` passes: 8 rooms, 34 walls, 21 openings, 21 features, every room reachable
from the vestibule. The same script redraws the preview.

**Sections 1-4 are the first pass. Section 5 ("Verification round") changed the rear half of the house
and the vestibule; where they differ, section 5 and `house.json` win.**

## 1. Result

Footprint over the outer wall faces: **5.41 wide x 17.03 long** (x -0.88..4.53, y -0.12..16.91).
All floors Z = 0 (every analyst agrees there is no step). Rectangles are inside faces.

| room | x | y | size | ceiling | room spec said | layout.md said |
|---|---|---|---|---|---|---|
| vestibule | -0.65..0.65 | 0..1.73 | 1.30 x 1.73 | 2.85 flat + vault | 1.30 x 1.73 | 1.45 x 1.75 |
| hallway, front | -0.65..0.65 | 1.83..4.83 | 1.30 x 3.00 | 2.95 | 1.30 x 2.50 | 1.55 x 2.40 |
| hallway, passage | -0.65..0.15 | 4.83..7.68 | 0.80 x 2.85 | 2.95 | 0.80 x 3.60 | 0.73 x 3.60 |
| stairs | 0.15..0.99 | 4.83..7.58 | 0.84 x 2.75 | open, cap 5.6 | 0.84 x 3.60 | 0.82 x 3.60 |
| hallway, lobby | -0.65..0.99 | 7.68..8.73 | 1.64 x 1.05 | 2.95 / 2.60 soffit | 1.64 x 1.05 | 1.55 x 1.05 |
| hallway, arch wall | clear -0.59..0.35 | 8.73..9.03 | 0.94 clear | crown 2.75 | same | 0.925, crown 2.60 |
| hallway, rear corridor | -0.65..0.35 | 9.03..11.98 | 1.00 x 2.95 | 2.95 | 1.00 x 3.25 | 1.00 x 3.25 |
| living | 0.80..4.30 | 0.99..4.73 | 3.50 x 3.74 | 2.95 | 3.60 x 3.80, 3.05 | 3.60 x 4.10 |
| living bay | 1.10..4.00 | 0..0.99 | 2.90 x 0.99 | 2.95 | 2.90 x 0.85 | 3.40 x 0.70 |
| kitchen | 1.25..4.30 | 5.31..8.73 | 3.05 x 3.42 | 2.95 | 3.05 x 3.42 | 3.60 x 4.02 |
| kitchen nook | 1.37..2.62 | 8.73..9.25 | 1.25 x 0.52 | soffit 2.03 | 1.25 x 0.52 | 1.75 x 0.45 |
| wc | 0.50..3.00 | 9.36..10.14 | 2.50 x 0.78 | 2.40 | 2.50 x 0.78 | 2.675 x 0.95 |
| utility | 0.50..3.00 | 10.26..11.98 | 2.50 x 1.72 | 2.40 | 2.50 x 1.72 | 2.675 x 1.95 |
| dining | -0.65..3.00 | 12.11..16.61 | 3.65 x 4.50 | 2.80 | 3.775 x 4.50 | 3.775 x 5.22 |

Wall thicknesses: party walls 0.23; front line and bay 0.12 (door and timber window framing); old front
wall (nibs) 0.25; inner glazed screen 0.10; hall/living 0.15; stair/kitchen 0.26; under-stairs door wall
0.10; living/kitchen cross zone 0.58 (see D6); old rear wall at the arch 0.30; kitchen north wall with the
nook zone 0.63; corridor/WC/utility 0.15; WC/utility partition 0.12; flank wall 0.28; dining south wall
0.13; dining north wall 0.30; bay west cheek 0.45 (see open question 2).

## 2. Decisions

Principle: a room keeps the size its own analyst measured from fixed modules or direct counts (kitchen
units, utility tiles, vestibule tiles, door leaves). Chain lengths that nobody measured directly
(layout.md's hall lengths, which the hall spec inherited) give way. What cannot be reconciled goes into
wall thickness that is never seen.

**D1. Hall and vestibule are 1.30 wide (layout 1.55 / 1.45).** Re-measured on the frontal still
`hall/full/F_0057`: leaves 323 and 317 px wide by 1050 px high (ratio 0.306, so 610 x 1981 leaves) and the
frame 687 px wide at 523 px/m = 1.31 m. Keystone in that still is under 3 %. The vestibule tile count
agrees. Layout's 0.335 ratio is not reproducible.

**D2. Passage 0.80, stair 0.84, nib 0.34 (hall spec).** The nib is visible in four frames and both width
figures were measured two ways. The stair wall is at x = 0.99 and the lobby is 1.64 wide.

**D3. Camera focal length.** Vanishing-point calibration (`reconcile/vp.py`) on the two well-conditioned
stills gives f = 883 px (F_0751) and 853 px (F_0064) at 1080 px width, not the 550-670 px obtained from
the tile frames. All distance checks below use f = 870 +/- 40. This is why earlier depth estimates along
the hall were short.

**D4. Front hall is 3.00 long (hall spec 2.50, layout 2.40).** Neither figure was measured; the hall spec
states it took layout's lengths. Three constraints fix it:
- The living TV wall carries 0.25 + 0.78 door + 0.43 + an 80-85 inch TV (its height checks at 1.0-1.08 m
  against the door head beside it), so it cannot be shorter than about 3.46; the living spec measured
  3.80 by cross-ratio.
- The bay cheek window is in the vestibule's recess B, right against the pier (f_0019, f_0021), so the
  old front wall starts at y = 0.74 and the living room's front line cannot be south of about 0.99.
- Ground-plane measurement in F_0751 (horizon row 661, pitch 18.7 deg, camera height 1.40 from the two
  door heights) puts the newel 3.7 m from the inner doors; F_0781 puts the living door centre about
  2.0-2.1 m from them. Together: nib 2.7-3.2 m from the inner doors.

Adopted: nib at y = 4.83, living north face 4.73, living main length 3.74 (within the living spec's
+/-0.15), living door centre y = 4.09. Items on the front-hall walls keep their offsets from the living
door, not from the inner doors (see the hallway appendix).

**D5. Stair recess is 2.85 long, not 3.60, and the top of the flight is over the lobby.** F_0751 puts the
under-stairs door wall about 5.9 m from the inner doors and 2.2-2.4 m beyond the newel. Fifteen risers
(counted again in `layout/hr_243`: 14 nosings plus the landing edge) with a 0.23 going run 3.30 m from
the nib, so riser 13 is over the under-stairs door wall and risers 14-15 plus the half-landing are above
the lobby. That is exactly what the overhead cupboard hides: stair soffit about 2.27 at that wall
(boarding 2.07-2.30, cupboard 2.30-2.60), landing soffit 2.60 over the rest of the lobby. The overhead
cupboard therefore projects 0.45 (hall spec 0.35). Landing level 2.85 (15 x 0.19) is a half-landing; the
first floor is higher and is not modelled.

**D6. Kitchen stays exactly 3.05 x 3.42; the difference becomes a thick cross wall.** The owner's
priority is the cabinet layout, and the module arithmetic closes on all four walls. Layout.md counted
about 3.5 from modules too and then stretched the room to 4.02 to fill its chain. Both the kitchen and
hall specs put the kitchen door tight against the kitchen's north wall / the lobby's north return wall,
so the kitchen north face is y = 8.73 and its south face 5.31. The living north face is 4.73. The
0.58 m between them (`w_cross`) is never seen; neither room shows a chimney breast, so a flush-lined
stack in the cross wall is the likely content. In x the stair/kitchen wall is 0.26 thick so that the
kitchen (3.05) and the living room share the east party wall.

**D7. Living room 3.50 wide, east party wall face x = 4.30 (living spec 3.60, layout 4.50).** The living
width came from a focal-length argument (+/-0.15); the kitchen width from unit modules. Bay stays 2.90
wide, nibs become 0.30.

**D8. Front of the house.** Street doors and bay front share the line y = 0. The bay's west return is the
vestibule's recess B (y 0-0.74) with the cheek light centred at y = 0.37 (vestibule spec). The old front
wall is y 0.74-0.99 and the living front line is 0.99, so the bay is 0.99 deep from the nib room face
(0.74 of return plus the 0.25 wall). Layout's bay at -0.05..0.65 with the room starting at 0.65 is
rejected: it would put the cheek window north of the vestibule pier. The vestibule piers (0.55 long)
stay as the vestibule spec has them; they are longer than the wall is thick.

**D9. Arch.** Arch wall y 8.73-9.03. Springing 2.40, crown 2.75 (hall spec, scaled from the kitchen door
head); layout's 2.15 / 2.60 dropped.

**D10. Rear corridor is 2.95 long (hall spec and layout 3.25).** Its east side must hold, from the arch
wall: 0.33 (nook zone and wall) + WC 0.78 + partition 0.12 + utility 1.72 = 2.95, with the utility north
face flush with the corridor end because both are the south face of the dining wall. Measured from the
arch, the utility door lands within 0.03 m of where the hall spec has it. The wall north of the utility
door is 0.88 (hall spec 1.22, utility spec "about 0.65").

**D11. WC 2.50 x 0.78 and utility 2.50 x 1.72 (room specs).** Tile and unit counts beat layout's
2.675 x 0.95 / 1.95.

**D12. Dining 3.65 x 4.50.** Length 4.50 from the dining spec (measured independently on both long walls;
layout's 5.22 leaves 1.25 m clear at each table end, which the frames contradict). Width 3.65 rather than
3.775 so that the dining east wall and the utility east wall are one flank wall (inner face x = 3.00);
the utility's 2.50 is a tile count, the dining width was "TV plus door". Chimney breast 1.62 x 0.18 added
(layout had none). French doors 1.19 wide and symmetric, per the owner's "identical window on each side".

**D13. Ceilings.** Main body (hall incl. rear corridor, living, kitchen) 2.95: the hall measures
2.85-2.95, the inner frame top (2.83) and the doorcase top (2.71) must clear the cornice, the kitchen
measures 2.95 and the living 3.05 +/- 0.10. Vestibule 2.85 flat with the vault between the piers
(springing 2.43, crown 2.66). Dining 2.80. Utility and WC 2.40.

**D14. Details taken from the room specs over layout.md.** Letterbox on the west leaf. Living boards run
along Y. Under-stairs door 0.61 wide. Kitchen back door hinged on the east jamb, opening in.

**D15. Door states as filmed.** Inner west leaf open 85 deg; living door 95 deg; kitchen door 90 deg into
the lobby; utility and dining doors 90 deg; under-stairs, back, street and French doors closed.

## 3. Local to global transforms

| spec | transform |
|---|---|
| vestibule | identity |
| hallway, stairs | x unchanged; y piecewise, see the appendix in `hallway.md` / `stairs.md` |
| living | W-wall items x + 0.80; E-wall items x + 0.70; bay and centre items x + 0.75. N-wall and door-keyed items y + 0.93; front-wall items y + 0.99; bay items y + 0.85; centre items y + 0.96 |
| kitchen | x/1000 + 1.25, y/1000 + 5.31 (no scaling) |
| utility | x + 0.50, y + 10.26 (no scaling) |
| wc | x + 0.50, y + 9.36 (no scaling) |
| dining | W-wall and S-wall items x - 0.65; E-wall items x - 0.775; N-wall and centre items x - 0.7125; y + 12.11 |

## 4. Open questions

1. **Cross zone between living and kitchen (0.58 m).** Is there really a chimney stack or void there, or
   is one of the chain lengths still off? It is invisible in the model, but it sets the absolute Y of
   everything behind the stairs (+/- 0.3 m).
2. **Bay west cheek wall.** Plan arithmetic makes it 0.45 thick (vestibule face x 0.65, bay face 1.10),
   but the window looks no deeper than about 0.2 from either side. Either recess B is wider on its east
   side than the vestibule spec says (east wall hidden by coats), or the west nib is shallower than 0.30.
3. **Front hall 3.00 and stair recess 2.85** come from single-still photogrammetry (+/- 0.25). One tape
   measurement of the hall from the inner doors to the newel would settle D4-D6.
4. **Rear corridor 2.95** and with it the wall north of the utility door (0.88): painting E2 only just
   fits there.
5. **Dining width 3.65 vs 3.775**, and whether the dining west wall is exactly in line with the hall's.
6. **Main ceiling 2.95**: the living spec prefers 3.05, the hall spec 2.90.
7. **Stairs above 2.9 m**: half-landing at 2.85 with a facing wall is certain; everything above is a
   plausible continuation capped at 5.6.
8. Carried over from the room specs: street-door and French-door swing (never opened), stair prints
   S1-S4 unreadable (neutral stand-ins), crest plaques as real crops or generic shields, east vestibule
   pier assumed to mirror the west one, side return never filmed.

## 5. Verification round

Independent verifiers raised 15 issues. Each was re-checked against the frames (my stills and crops in
`reference/work/reconcile/v2/`, git-ignored). 12 accepted, 1 accepted in part, 1 superseded, 1 rejected.
`python spec/validate_house.py` passes after the changes (8 rooms, 34 walls, 21 openings, 21 features) and
the preview was regenerated and inspected.

### 5.1 Rectangles now (inside faces; supersedes the table in section 1)

Footprint **5.41 x 17.28** (x -0.88..4.53, y -0.12..17.16).

| room | x | y | size | change |
|---|---|---|---|---|
| vestibule | -0.65..0.65, recess B (y 0..0.74) to 0.90 | 0..1.73 | 1.30 x 1.73 | recess B widened east (V7) |
| hallway, front | -0.65..0.65 | 1.83..4.83 | 1.30 x 3.00 | - |
| hallway, passage | -0.65..0.15 | 4.83..7.68 | 0.80 x 2.85 | - |
| stairs | 0.15..0.99 | 4.83..7.58 | 0.84 x 2.75 | floor oak, carpet on steps only (V3) |
| hallway, lobby | -0.65..0.99 | 7.68..8.73 | 1.64 x 1.05 | - |
| hallway, arch wall | clear -0.59..0.35 | 8.73..9.03 | 0.94 clear | east jamb now a 0.10 respond |
| hallway, rear corridor | -0.65..0.45 | 9.03..12.23 | **1.10 x 3.20** | was 1.00 x 2.95 (V5, V6) |
| living | 0.80..4.30 | 0.99..4.73 | 3.50 x 3.74 | - |
| living bay | 1.10..4.00 | 0..0.99 | 2.90 x 0.99 | west cheek wall 0.20 thick (V7) |
| kitchen | 1.25..4.30 | 5.31..8.73 | 3.05 x 3.42 | - |
| kitchen nook | 1.37..2.62 | 8.73..9.25 | 1.25 x 0.52 | - |
| wc | 0.60..3.10 | 9.36..10.14 | 2.50 x 0.78 | moved +0.10 in x |
| utility | 0.60..3.10 | 10.26..12.23 | **2.50 x 1.97** | was 1.72 wide; +0.10 in x |
| dining | -0.65..3.10 | 12.36..16.86 | **3.75 x 4.50** | was 3.65; +0.25 in y |

Wall changes: corridor/WC/utility wall centreline x 0.525; flank wall inner face 3.10, **0.20 thick**
(was 0.28); dining south wall centreline y 12.295, north wall 17.01; bay west cheek centreline x 1.00,
0.20 thick (was 0.45). Transforms replacing section 3: utility X = x + 0.60, Y = y + 10.26 for items keyed
to W-wc and y + 10.51 for items keyed to W-rear; wc X = x + 0.60, Y = y + 9.36; dining W/S-wall items
x - 0.65, E-wall items x - 0.675, N-wall and centre items x - 0.6625, Y = y + 12.36.

### 5.2 Issues

| # | issue | verdict | what I saw / what changed |
|---|---|---|---|
| V1 | Dining NE side window is tall | accepted | Stills t=694, 700: bottom rail far below the dado; NW window (t=681, 683) has its board at about 1.1-1.3. `w_dining_n_e` sill 0.30, height 1.90; `w_dining_n_w` unchanged. Centres moved to x -0.09 / 2.54 by V5. dining.md 2.3. |
| V2 | Dining door 5 cm too far east | superseded by V4/V5 | The concern (east architrave buried in the wall) is real, but the cause is the door width and corridor width, not the centre. With V4 + V5 the east jamb is 0.087 from the east wall and the west jamb 0.115 from the pilaster. Proposed centre -0.14 not used. |
| V3 | Stairs polygon floor is carpet | accepted | `stairs.floor` = oak_plank, new `stairs.covering` = carpet on treads, risers, half-landing. stairs.md appendix. |
| V4 | Dining door is 0.838, not 0.762 | accepted | My reads: 0.78-0.82 from the hall side (t=290), 0.85-0.9 from the dining side (t=740, 741). `d_dining` width 0.838, centre (-0.056, 12.295), hinge (-0.475, 12.295). TV moved to local x 1.51..3.40, switch to 1.32. |
| V5 | Rear corridor 1.10 wide, dining about 3.75 | accepted, flank wall my own choice | End wall is 1.28 x the door opening in t=290, so 1.07 clear of the pilaster with a 0.838 door. Corridor east face 0.45; WC and utility +0.10; dining 3.75. Flank wall made 0.20 (outer 3.30) rather than 0.28 or 0.14: it keeps the 0.12 window reveals and the back-door clear opening (3.30..4.15); the door frame laps 0.05 behind the wall end. |
| V6 | Rear corridor 3.20 long | accepted | Stronger than the verifier thought. Ground-plane check in t=290 (pitch 25 deg, camera 1.40) puts the utility door's north architrave 1.0-1.2 m from the end wall (model had 0.81). And the verifier's counter-evidence is wrong: in t=534 the tiled strip between the utility door architrave and the worktop is about 1.4 tiles of 300 = 0.42 m, not 0.2, which makes the W-hall chain 0.08 + 0.762 + 0.07 + 0.42 + 0.62 = 1.95. Utility 1.97 wide; tall cupboard 0.60, base doors 0.37 each; W-rear run unchanged, moved +0.25. Dining +0.25 in y. |
| V7 | Bay west cheek wall is thin | accepted | t=17-19: shutter louvres directly behind the glass. Cheek centreline 1.00, 0.20 thick; vestibule recess B runs to x 0.90. Supporting detail: the recess-B downlight at x +0.20 is then near the recess centre. Flagged for the owner. |
| V8 | Living boards run along X | **rejected** | Full-res still t=114 (f_0115, facing the bay): long board edges recede toward the bay, with a short end joint across them. f_0234/f_0235 at the door: long edges and grain run parallel to the door line, same as the hall boards. t=137: joints parallel to the rug's long edge. Boards run along Y as living.md and D14 say; nothing changed. |
| V9 | Outside lights are filmed | accepted | Through the transom at t=15: boarded canopy soffit with three recessed downlights. vestibule.md section 7. Transom stays plain frosted. |
| V10 | WC wall grey too dark | accepted | #A5A5A8, floor #999A9E. wc.md section 3 and 10. |
| V11 | Stair print frames and subject | accepted | Crop confirms flat olive-bronze frames, pale paper, small dark boat with reflection. stairs.md section 6. |
| V12 | Cat flaps inconsistent | accepted | Round flap visible in the west French-door leaf (t=681). Kept in both doors; removed from the dining declutter list. |
| V13 | E1 contains a figure | accepted, option (b) | hallway.md section 6: inpaint the girl with path colour when making the texture, keep the geese. |
| V14 | Bins and shelf mugs | accepted | Transcript names both bins and the mugs. kitchen.md sections 5, 6, 8; hallway.md section 8. Bins on a viewer toggle, default on. |
| V15 | Text errors | accepted | utility.md (single glazed oak door; "most important part" is the dining room); living.md and kitchen.md transcript notes. |

### 5.3 Open questions after this round (replaces the affected items in section 4)

1. **Back-door corner.** Corridor 1.10 + wall 0.15 + utility 2.50 puts the flank wall's inner face at x 3.10,
   and the back-door frame starts at x 3.25, so a normal 0.25-0.28 external wall does not fit. One of
   those numbers is about 0.1 too big, or the kitchen sits about 0.1 further east. Modelled with a 0.20
   wall. Never filmed; owner check.
2. **Vestibule recess B, east side** (x 0.65 to 0.90, a 0.28 front-wall return east of the street-door
   frame, east pier 0.35 proud on its south face). Follows from the thin cheek wall; coats hide it.
3. **Rear corridor width at the arch end** was not measured; 1.10 comes from the far end only. The arch
   east jamb is kept at 0.35 as a 0.10 respond.
4. **Rear corridor length 3.20 / utility width 1.97.** Three independent reads now agree within about
   0.1, but one tape measurement from the arch to the dining door would settle it. The utility far-wall
   unit split (0.60 tall cupboard, 2 x 0.37 base doors) is the least certain part of that room.
5. **Dining width 3.75** (verifier's chain gives 3.74-3.82; the dining spec had 3.775).
6. Section 4 items 1, 3, 6, 7 and 8 stand. Items 2, 4 and 5 are replaced by the above. Stair prints are
   no longer "unreadable" (V11).

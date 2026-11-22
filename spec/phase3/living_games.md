# Phase 3 survey - living room table games (`living_games`)

Footage: v10 (PXL_20261121_124801398, 65 s, 30 fps, silent, daylight). All 65 one-per-second frames were read,
plus the sharpest full-resolution frame of every second and a few picked ones (scratch only:
`reference/work/r3_living_games/tSS_fNNNN.jpg`, `gNNNN.jpg`; N = 30 fps frame index, time = N / 30 s).
Helper scripts (scratch): `build/r3/living_games/{sharp,grab,crop,rect,circ,sample,swatch}.py`.
Present model checked from `docs/renders/living_bay.jpg` and `build/preview/living_table_r3livinggames.jpg`
(`--levels G --only shell,living --cam table`, BUILD OK, no Traceback).

Frame guide (v10 `frames/f_00NN`): 01-08 coffee table from W / NW / N with the xiangqi board, the box at the south
end, rug, sofa, bay corner; 09-31 the box: closed, lid opened, dominoes taken out (1 at f16, 2 at f17-19, 3 at f20),
put back (f21-24), closed (f25), opened again (f26-27), closed (f28-31); 32-37 low close views of the box sides;
38 its underside; 39 lid; 40 open with a chess piece held beside it; 41-42 top-down, closed (as left); 43 wide: box,
sofa end, east nib, curtain, magazine rack, east armchair; 44 east armchair, lamp-table legs, rug corner, stool;
45-65 lamp table: solitaire board and lamp base.

World frame as in `spec/BRIEF.md`. Model positions used below: coffee table centre (2.80, 2.33), top 1.60 (Y) x 0.62
(X), top surface z 0.46, so east edge x 3.11, south end y 1.53; lamp table centre (2.55, 0.37), top z 0.64.

## 1. How the sizes were measured

No object of certified size lies on either table, so the scale is a chain of ratios, closed five ways.

Ratios (plane homographies fitted to the xiangqi grid, 8 x 9 square cells, in t03_f0105 and t00_f0021; cells are
square to 1 %, both frames):

| ratio | value | frames | note |
|---|---|---|---|
| board outer / cell | 9.7 x 10.7 (margin 0.85 +- 0.07 cell all round) | t03, t00 | |
| piece diameter / cell | 0.85 +- 0.03 | t03 rectified | body, not the top face |
| coffee-table width / cell | 14.0 +- 0.6 | t03 (13.3-14.4), t00 (13.75-14.4) | edges extrapolated 2-4 cells beyond the grid |
| box length / cell | 3.2 +- 0.15 | t00 (base 2.97, lid 3.39 raw, lid 4 % nearer the lens) | extrapolated 5 cells |
| box length / domino length | 2.95 +- 0.1 | g0604 (box front 385 px, tile 137 px, depth corrected) | same plane |
| box interior / domino length | 2.63 | g1183 | |
| lid long / short | 1.49 | t40_f1219 (568 / 380 px, top-down) | |
| piece / box lid length | 0.25 | g1183 (piece held beside the open lid) | depth guess +-10 % |
| piece thickness / diameter | 0.40 +- 0.05 | t03 (ellipse 55 x 43 px, wall 11 px) | |

Absolute scale, five references:

| reference | assumed | cell mm | piece | box lid | domino | table width |
|---|---|---|---|---|---|---|
| coffee table width (spec, v1) | 0.62 m | 44.3 | 37.7 | 142 | 48 | 0.62 |
| domino, standard club size | 48 mm | 45 | 38 | 144 | 48 | 0.63 |
| inlaid box, the common 15 x 10 cm size | 150 mm | 47 | 40 | 150 | 51 | 0.66 |
| chess piece, the common 38 mm size | 38 mm | 44.7 | 38 | 143 | 48.5 | 0.63 |
| fingers / thumb beside the piece (g1183) | 17-21 mm | 41-43 | 34-37 | 132-137 | 45 | 0.58-0.60 |

Adopted: **cell 44.5 mm (+-2.5, i.e. +-6 %)**. The hand is the outlier and the weakest (close range, a few cm of
depth changes the scale by 10 %). Camera height recovered from the t03 pose with this scale is 0.55 m above the
table, 1.0 m above the floor, which is a plausible hand-held height.

Lamp table: plane-from-circle on g1369 (the only frame with nearly the whole top; focal length 700-900 px, tilt
37-40 degrees) gives table diameter / solitaire-board diameter = 2.4 (+-0.15); the marble lattice homography
(33 centres, rms 0.08 pitch, t56_f1690) gives board radius 5.06 pitches, field radius 3.97, lip 4.54; marble /
pitch = 0.86 (t60_f1816, top-down). With the 0.62 m table: board 0.24-0.25 m. A hand holding the rim (t52) cannot
be used: it is far nearer the lens than the board. Adopted: **board diameter 0.24 m (+-0.02)**.

## 2. Inventory (what the footage shows against the present model)

### 2.1 Xiangqi set - on the coffee table (model: on the TV unit, pale board without lines, 32 small discs)

- **Board**: one flat slab, **0.43 (north-south, across the files) x 0.475 (east-west, along the files) x 0.015 m**,
  square edges just eased, no feet, no fold. American-walnut look, oiled, satin. The playing area is built like a
  chess board: walnut blocks whose tone alternates slightly from cell to cell (grain turned), divided by **inlaid
  pale maple strips 4.5 mm wide**, flush. Plain walnut margin 38 mm; the river is one unbroken walnut band.
- **Line pattern**: 9 file lines x 10 rank lines, cell 44.5 mm (grid 356 x 400.5 mm). The two outer file lines run the
  full length; the 7 inner file lines stop at the river (ranks 5 and 6 counted from either end), so the river is a
  clear band one cell wide. Two palaces: an X of two maple diagonals over files 4-6 (the middle three), ranks 1-3
  at each end, crossing at the middle point of rank 2. No cannon / soldier corner marks, no lettering in the river.
  (t03_f0105 rectified: `b03_rect1.jpg`; f_0002-f_0007.)
- **Pieces**: **32 discs, diameter 38 mm, thickness 15 mm**, top and bottom arrises rounded about 2.5 mm, all the same
  dark maroon rosewood colour, satin. One face carries an engraved character filled with paint, the other face is
  blank (g1183). 16 have **rose-red** fill (east side, towards the sofa), 16 **turquoise-green** fill (west side).
  Characters need only be 3-5 incised strokes in the fill colour, 20 mm high, readable from the owner's side of
  each army (red upright seen from the east, green upright seen from the west).
- **Layout as left**: the standard opening array, set down casually. Board coordinates: file u = 0..8 from the
  north end to the south end, rank v = 0 (red back rank, east) .. 9 (green back rank, west); positions are the disc
  centres on the board, from the t03 top-face centres corrected for the 15 mm height with the recovered camera
  pose (+-0.07 cell):

  | red (east) | u | v | | green (west) | u | v |
  |---|---|---|---|---|---|---|
  | chariot | 0.47 | 0.01 | | soldier | 0.31 | 6.05 |
  | horse | 1.31 | 0.34 | | soldier | 2.39 | 5.71 |
  | elephant | 2.19 | 0.54 | | soldier | 4.00 | 5.85 |
  | adviser | 3.03 | 0.76 | | soldier | 6.24 | 5.93 |
  | general | 4.00 | 0.72 | | soldier | 7.85 | 5.91 |
  | adviser | 5.08 | 0.63 | | cannon | 1.20 | 7.02 |
  | elephant | 5.90 | 0.52 | | cannon | 7.20 | 7.11 |
  | horse | 6.76 | 0.67 | | chariot | 0.09 | 8.97 |
  | chariot | 7.43 | 0.28 | | horse | 1.02 | 9.00 |
  | cannon | 1.07 | 1.72 | | elephant | 2.23 | 8.74 |
  | cannon | 7.17 | 2.19 | | adviser | 3.14 | 8.94 |
  | soldier | 0.29 | 2.84 | | general | 4.02 | 8.88 |
  | soldier | 2.12 | 3.10 | | adviser | 4.87 | 8.70 |
  | soldier | 4.29 | 3.12 | | elephant | 6.02 | 8.56 |
  | soldier | 6.35 | 3.06 | | horse | 6.89 | 8.87 |
  | soldier | 7.76 | 3.24 | | chariot | 7.91 | 9.03 |

  The red back rank is bowed: its ends sit on the line, its middle up to 0.75 cell towards the river, and the two
  chariots stand half a cell in from the corners.
- **Where**: board centre **(2.86, 2.15)**, z 0.46 (bottom). Its red (east) edge lies on the table's east edge and
  the board is twisted 5 degrees (south end further east), so its south-east corner overhangs the table edge by
  about 13 mm and its west edge is 0.14 m short of the table's west edge. With local +x = files north to south and
  local +y = towards the red side: rot_z = -85 degrees. (To keep it wholly on the table use centre x 2.845.)
  A piece at (u, v) is at board-local x = (u - 4) * 0.0445, y = (4.5 - v) * 0.0445; in the world that is
  centre + (0.087 x + 0.996 y, -0.996 x + 0.087 y). Check: the red chariot at (0.47, 0.01) lands 0.19 m east and
  0.17 m north of the board centre, the north-east corner.
  Along the table the board centre is 0.63 m (+-0.08, extrapolated) from the south end, i.e. 0.18 m south of the
  table centre.
- Colours (sampled sRGB -> estimate): walnut cells #705F5A-#927B69 (sky glare) -> **#6B4F3C**, lighter cells #7E6350,
  darker #5C4436; maple #CCBBAA -> **#D9C7A6**; pieces #473D47 / #4D3944 on the table, #462B2D held in the hand ->
  **#4A2428**; red fill #B1859A (thin strokes on dark) -> **#C8505C**; green fill #8FADBE -> **#4FB3A6**.

### 2.2 Inlaid mosaic box of dominoes - on the coffee table (model: on the lamp table, 0.20 x 0.13 x 0.07, plain)

- **Size 0.145 x 0.097 x 0.042 m** (lid 12 mm of the height, base 30 mm). Lid flush with the base all round, hinged
  on one long side; left to itself it stands open at about 100 degrees (f_0020, f_0022: no hand on it).
- **Carcass**: red-brown hardwood (mahogany / walnut colour, polished) 7-8 mm thick; seen on the rim of the base
  and lid when open, on the 5 mm band between lid and base, and as the plain polished underside, which has a
  6 mm white bone border strip all round, mitred (f_0038).
- **Lid top** (t40_f1219, t38_f1159; rectified in scratch `lid_rect.jpg`): from the edge inwards
  1. border 11 mm of fine black / white pinstripes at right angles to the edge, in blocks of about 7 stripes with a
     row of dots through the middle of each block; the four corners are plain white bone squares with a mitre line;
  2. white line 1 mm, **red-brown band 2 mm**, white line 1 mm;
  3. field 0.117 x 0.066 m, black ground: a star-and-hexagon lattice drawn in 3 mm bands (white with a row of black
     dots, black edges). **Five large six-pointed stars of mother-of-pearl** (each six lozenges, 19 mm across) in a
     quincunx - centre, and four at +-30 mm along / +-22 mm across - with half stars cut by the frame at mid-height
     on the two short sides; around each star six **hexagon rosettes** (12 in all, 14 mm across, four per row in
     three rows), each a six-pointed star of red-brown triangles round a hexagon of tiny black and white triangles.
- **Sides**: each of the four faces has an inset panel (long sides 0.118 x 0.020, short 0.070 x 0.020) of a
  two-row lozenge mosaic - white bone lozenges 8 mm long leaning alternately left and right with black and grey
  triangles between (a tumbling-block chevron) - framed by a white line in the dark wood; the four vertical corners
  are 6 mm posts of horizontal black / white stripes; the lid edge shows three white stringing lines (f_0032-f_0036).
- **Inside**: lid and base lined with **crimson velvet**; the lid lining is a slightly pillowed pad.
- **Dominoes**: a double-six set, 28 tiles **48 x 24 x 7.5 mm**, cream ivory with rounded corners, black pips, a
  black centre line with a small brass pin. They lie flat in four layers (7 per layer: five on the short way plus two
  on the long way fills the 0.129 x 0.081 interior; the footage shows them a little jumbled, top tiles at slight
  angles, one face down).
- **On the table**: at most three at once (g0604 / f_0020: 6-6, 3-2 and 4-4 as far as they can be read), lying
  face up 20-85 mm in front of the open box and towards its right-hand end: centres, in the box frame (x along the
  box, distance in front of the front face): (+0.03, 0.085) parallel to the box, (+0.10, 0.035) turned 55 degrees,
  (+0.17, 0.02) turned 10 degrees. All were put back before the end of the footage.
- **Where, as left** (t40, t42): centre **(2.85, 1.70)**, z 0.46; 0.26 m from the table's east edge and 0.17 m from
  its south end (0.33 / 0.17 at the start of the footage, 0.23 / 0.17 at the end); long axis diagonal, north-east to
  south-west, 42-54 degrees off the table axis; hinge side facing south-east, the opening side north-west. With
  local +x = long axis and local +y = hinge side: rot_z = -131 degrees (+-10).
- Colours: bone #E3E3E1 -> **#EDE9DF**; mother-of-pearl #EFF0F5, glossy with a faint pink / green sheen; black
  #24272B; red-brown #815A58 / #8B6D60 -> **#7A4A3C**; carcass #493E36 (shade) -> **#5E3A2C**; lining #611A1E-
  #6D1E24 (the phone crushes the red) -> **#A01C24**; tiles #E5E6DE -> **#EEEADB**; pips #1D2026; pin brass.
- Texture source: the lid is the only part that needs a real pattern. Either generate it from the description
  above, or - if a marquetry lid counts as an art pattern under the rule for rectified crops (no people, nothing
  private in it) - rectify t40_f1219 with the lid quad (480,782) (930,1090) (735,1425) (255,1080). Decision for
  the orchestrator.

### 2.3 Solitaire board - on the round table in the bay (model: diameter 0.23, 32 ivory domes, off-centre)

- **Turned board of burr wood, diameter 0.24 m, 15 mm thick**, high polish. Profile from the centre: flat field
  diameter 0.188 m ending in a fine 1.5 mm bead; a concave groove (gutter) 13 mm wide and about 4 mm deep (radius
  94-107 mm); a rounded outer lip 12 mm wide, level with the field (radius 107-120 mm).
- **Hole pattern**: the English cross, 33 holes on a square lattice of **23.8 mm** pitch: rows of 3, 3, 7, 7, 7, 3, 3.
- **33 marbles - every hole filled, the centre too** (counted in t60_f1816, t64_f1942 and the 33-point lattice fit of
  t56_f1690). **Diameter 20.5 mm** (0.86 pitch), polished onyx / alabaster: about one third plain cream-white, one
  third plain honey to tan, one third banded or mottled brown and cream, mixed at random.
- **Where**: board centre at the table centre + (0.02, 0.045) -> **(2.57, 0.415)**, z 0.64; lattice turned about
  9 degrees. The model has it at (-0.15, +0.06) from the centre.
- Colours: burr rim #4D362F / #957360, field median #9E9396 under glare, dark eyes #523D33 -> **mid red-brown
  #7A5238 with darker swirls #4A3226 and golden patches #A07850**; marbles cream #DBDCDB -> #E6E1D3, honey #C4BDA2
  -> #CDBF9C, tan #A38F6C -> #A8906A, brown bands #9A836C -> #8E7359, a few pinkish #A18775.
- Scale-independent facts are certain; the absolute size is +-8 % (section 1).

### 2.4 Lamp on the round table

- Base, bottom to top (t46_f1385, t56, t64, g1369): a **pierced gilt acanthus-leaf ring foot, diameter 0.18 m**,
  standing directly on the table; on it a **domed foot of rose-brown mottled marble, diameter 0.145 m, 35 mm high**;
  a torus neck ring diameter 50 mm at about z 0.06 above the table; then the body, a **plain inverted cone of the same
  marble** widening steadily from 45 mm at the ring to about 0.13 m at a gilt rose-garland collar some 0.25 m above
  the ring, garland pendants hanging 40 mm below the collar. The top of the body and the shade are not in v10.
- Model: marble disc at the bottom, gilt above it, ovoid urn widest at 60 % of its height, garland 0.15 m above
  the neck. Wrong order of foot members and too short a taper.
- Position: table centre + (0.07, -0.125) -> (2.62, 0.245) (model (0, -0.13)); gilt edge 0.06 m inside the table
  edge. Gold twisted flex leaves the foot towards the window.
- Colours: marble #A58E74 / #B29F8E -> **#B5846B**, mottled +-15 %; gilt median #716148, highlights #BCB79A ->
  **#A8914F**, antique.

### 2.5 Coffee table

- Width 14.0 +- 0.6 cells = 0.62 +- 0.05 m: agrees with the model (0.62). Length not in frame. Corner radius 30-45
  mm (model 45). Moulded edge with three parallel members and a top about 50 mm thick: as modelled.
- Position along the room: the sofa's south front leg is 0.03 m north to 0.2 m south of the table's south end (t40
  crude, t03 and t00 by ray casting; model 0.03 m south). Gap table east edge to sofa front legs 0.5 +- 0.1 m (t03,
  t00; model 0.52). No change.
- Wood: dark stained oak, open pores nearly black over mid brown, broad cathedral arches along the length, satin
  to gloss (the window reflects in it), small pale wear specks. Sampled #4B3D35 / #544334 / #695A4D -> #5A4330 as in
  the spec. The model's grain map is more regular and higher in contrast than the real top.

### 2.6 Rug

- Pattern as in the spec and the model. Border order at the west edge, outside in (t00): plain cream 60-80 mm,
  navy line, narrow rosette border, navy line, main palmette border about 0.18 m, navy line, narrow rosette
  border, navy line, field.
- **Bare floor shows between the coffee table and the sofa** (t03 and t40, crops `t03_gap.jpg`, `t40_gap.jpg`): the
  rug's east edge is less than 0.2-0.28 m east of the table's east edge, i.e. at x <= 3.35, where the model has 3.50.
  The west edge is 1.1 +- 0.1 m west of the table's east edge (ray casting in t00), x about 2.0 (model 2.10). So the
  rug lies about 0.10-0.15 m further west than modelled (centre x about 2.68), or is 1.4 wide and the table stands
  east of its centre line. Medium-low confidence; a 1.60 m wide rug is not excluded by the west-edge figure alone.
- Better texture sources than the night video: t00_f0021 (field and all borders, no people in that part), g1309
  (corner with all borders, sharp).

### 2.7 Sofa, armchairs, stool, rack

- Sofa as modelled: dark show-wood (#392628), S-scroll ends with a carved volute, moulded seat rail, front legs of
  three stacked bulbs on a small white glide (t40), bolster with pleated rosette and covered button, cream-gold
  scalloped gimp along the rail and the scroll. The grey throw is clutter.
- Armchairs (g1309, t42): the arms are **not open**: a thick roll pad sits on a second, flat upholstered pad with
  gimp along its lower edge, on the dark arm rail between the back post and a turned front post with a ball finial.
  Back panel upholstered with gimp between spiral-turned posts, deep square seat, short bobbin front legs on
  castors. The east chair carries no loose cushion in v10 (it did in v2).
- The footstool stands in front of the lamp table, west of the east armchair, about (2.5, 1.05) (g1309, g1369;
  it stood in front of the east armchair in v2). Movable; low priority.
- A **brass magazine rack** stands on the floor between the east nib and the east armchair, about (3.80, 0.85):
  embossed sheet brass, 0.30 wide x 0.15 deep x 0.26 high, sides splayed (t42, f_0009-f_0012, f_0038). It is where
  the room spec lists an optional "folding cake-stand". Its magazines are printed matter: leave it empty or with
  two blank ones. A white plastic box beside the other chair is a pet item: omit.

### 2.8 Curtains and shutters

- **Curtain hem 0.27 +- 0.04 m above the floor**, about 0.10 m above the top of the skirting (t42: floor line,
  skirting top 0.17 and window board 0.62 as the scale; f_0010; v2 f_0873 shows the same). The model has 0.12.
- Tartan in daylight: taupe-grey ground, broad raspberry-wine bands (sampled #885458 in shade, estimate #9A4A55,
  a little bluer than the spec's brick #A04A45), cream double lines, thin charcoal lines; sett about 0.20 m.
  Tie-backs: cream rope with a champagne tassel, as modelled.
- Shutter louvres: 11 blades span 0.68-0.83 m of the east return panel (t42); blade pitch / stile width = 1.35-1.5
  (t56, g1369). Pitch 70 +- 8 mm, so blades of 76 or 89 mm and 13-15 per panel, against 63 mm blades at 52 mm pitch
  (about 19) in `lib/joinery._shutter`. Needs a frontal view (v9) to settle.

### 2.9 Floor, colours

- Boards run along Y: the long joints in the floor strip between table and sofa are parallel to the table's long
  edge, the butt joints square to it (t40_gap, t03_gap). Width not measurable here (only a lower bound).
- Floor in daylight #C9BEA8 lit, #A8987A in shade: as the spec's #C9B48A, slightly greyer.
- Velvet in daylight: sofa #A35451, armchair seat #A65F5D / #A7625D - a dusty terracotta rose (hue 4-8 degrees),
  redder than the model's nap map (median #8B5631, hue 25 degrees). Phone white balance differs between the
  videos; estimate **#A2584A**. Low-medium confidence.
- Lamp table top #7A6257 / #836346 (straight-grained boards, mid walnut brown, satin, one pale heat mark that is
  not worth modelling), carved edge #463B3F; as modelled.

## 3. Dimension table

`spec/house.json` fixes, for this room, the plan polygon, the ceiling, the door, the bay windows and the floor
direction. v10 is table-top footage: it shows none of the walls or openings well enough to measure.

| item | where | present | measured | method | confidence |
|---|---|---|---|---|---|
| living polygon, ceilingZ | rooms.living | 3.50 x 4.20, 2.95 | not visible | - | no evidence |
| door | openings.d_living | 0.762 x 1.981 | not visible | - | no evidence |
| bay sill height | openings.w_bay_front / cheeks sill | 0.62 | level with the lamp-table top (0.64) within about 0.03 | table rim against the window board, t55, t56, g1369 | low; consistent |
| floor direction | rooms.living floor.direction | y | y | joint directions, t40, t03 | high; confirmed |
| nib chamfer | features.living_bay | 0.15 wide | visible at the skirting (t42), not measurable | - | no evidence |

Not in `house.json` (room module / lib):

| item | present | measured | method, frames | confidence |
|---|---|---|---|---|
| coffee table width | 0.62 | 0.62 +- 0.05 | 14.0 cells x 44.5 mm | medium; keep |
| xiangqi board | 0.38 x 0.42, on the TV unit | 0.43 x 0.475 x 0.015, on the coffee table | section 1 | high for ratios, +-6 % for size |
| xiangqi piece | 32 x 9.5 mm | 38 x 15 mm | 0.85 cell; ellipse / wall ratio | medium-high |
| inlaid box | 0.20 x 0.13 x 0.07, on the lamp table | 0.145 x 0.097 x 0.042, on the coffee table | 3.2 cells; aspect 1.49; height 0.29 of length (t33, g0604) | medium-high |
| domino | - | 48 x 24 x 7.5 | box / 2.95 | medium |
| solitaire board | 0.23, 32 marbles of 17 mm at 25 mm | 0.24, 33 marbles of 20.5 mm at 23.8 mm | lattice fit; table ratio 2.4 | high for count and ratios, +-8 % size |
| lamp foot | disc 0.17 under gilt 0.16 | gilt 0.18 under marble dome 0.145 | 0.76 and 0.57 of the board diameter, g1369 | medium |
| lamp position on table | (0, -0.13) | (+0.07, -0.125) +- 0.03 | plane back-projection, g1369 | medium |
| curtain hem | 0.12 | 0.27 +- 0.04 | t42, f_0010, v2 f_0873 | medium-high |
| rug east edge | x 3.50 | x <= 3.35 | bare floor visible, t03, t40 | medium |
| rug west edge | x 2.10 | x 2.0 +- 0.1 | ray casting, t00 | low |
| shutter louvre pitch | 52 mm | 70 +- 8 mm | t42 count, t56 / g1369 ratio | low-medium |
| gap coffee table - sofa legs | 0.52 | 0.5 +- 0.1 | ray casting t03, t00 | low; keep |

No change to `spec/house.json` is proposed from this area.

## 4. Notes per unit

**living**
1. Xiangqi: take it off the TV unit, rebuild as 2.1, place on the coffee table. Board top as one generated image
   (walnut cells, maple lines, river, palaces); 32 lathed discs; glyphs as a small generated decal or a few
   incised strokes, red on the east army and turquoise on the west.
2. Inlaid box: take it off the lamp table, rebuild as 2.2 on the coffee table; lid as its own object hinged on the
   south-east long side (`ix`: opens to about 100 degrees), crimson lining, 28 tiles inside; optionally two or
   three tiles on the table that show when the lid is open.
3. Solitaire: 33 marbles, centre filled; sizes, profile, burr wood and onyx colours as 2.3; move to the middle of
   the lamp table.
4. Lamp: foot order and body taper as 2.4; move 0.07 m east.
5. Curtains: hem 0.27 (was 0.12); check the closed-curtain state uses the same hem.
6. Rug: 0.10-0.15 m west, so that bare floor shows between the coffee table and the sofa; consider a new texture
   crop from t00 / g1309.
7. Armchairs: two-tier arm pads (2.7). East-chair cushion and footstool position are movable items: owner's call.
8. Brass magazine rack at the east nib (2.7), empty.
9. Coffee table: no dimension change; soften the grain contrast, raise the gloss a little.
10. Velvet hue: see 2.9 before changing.

**shell** (joinery): shutter louvre pitch 70 +- 8 mm instead of 52 (2.8), if the v9 survey agrees.

**site, envelope**: nothing from this area.

## 5. Open questions

1. Absolute scale of the games: +-6 % (xiangqi, box, dominoes), +-8 % (solitaire). Every chain passes through an
   assumed size (table 0.62, domino 48, piece 38, box 150). A tape on the board (0.43 x 0.475?) would settle all.
2. Is the set on the coffee table the same one the earlier videos showed on the TV unit? v10 never shows the TV
   unit. Assumed yes (one set): moved.
3. Coffee table length (1.60) and the board's position along it: the north end of the table is never in frame;
   the board centre is 0.63 +- 0.08 m from the south end by extrapolation.
4. Rug: 1.40 wide and shifted west, or wider? Only its east limit is firm.
5. Lamp-table diameter (0.62) could not be checked to better than 10 %; the solitaire size hangs on it.
6. Lamp body above the garland and the shade: not in v10.
7. Shutter blade size: 76 or 89 mm.
8. Lid texture: generated, or a rectified crop (rule decision).
9. Velvet hue: v10 daylight reads redder than the model; white balance between videos is not controlled.
10. Which long side of the box carries the hinge in its final position was followed through f_0040-f_0042 by the
    camera turn, not seen directly: +-180 degrees possible.

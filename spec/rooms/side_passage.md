# side_passage — side passage (flank F, x 3.45; K wall, y 9.03) and side alley (east wall E, x 4.65)

Round-3 notes for `blender/rooms/side_passage.py`. Positions in world metres; sources in
`spec/phase3/briefs/side_passage.md`, `spec/phase3/passage.md` (survey + verification) and `spec/RECONCILE3.md`
(passage-01..-12). Zones, gates, fence and kitchen steps are site; facade skin, base rail, downpipes, soil stack,
old drain and the flank conduits up to the condenser are envelope.

## Flank F and K (passage, flags at -0.30)

| item | position | notes |
|---|---|---|
| tap T2 | (3.45, 9.90, 0.48) | brass double bib tap (cross head; a plain second spout turns down by the plate), grey / green click connector on the nose; water falls onto the old drain |
| chain | plate (3.45, 10.02, 0.75) | galvanised links hang to a strap on the old drain (v11 f_0021, f_0031) |
| louvre vent | (3.45, 10.00, 1.945) | white, 0.155 square, 3 gravity louvres, north of the WC window |
| old drain | envelope | module adds a socketed end (y 9.668..9.79) with a 45-degree branch rising toward the steps under a round screw cap (raised bar, two slots; v11 f_0022), the strap, a 40 mm black pipe beside it y 9.80..12.18; the cap clears the tread nosing (y 9.665) |
| gully | (4.475, 9.12), 0.15 sq | dark grey #2A2A2C, under the K downpipe shoe, clear of the tread nosing (x 4.395) |
| inspection cover | x 4.50..5.06, y 10.25..10.97 | galvanised frame, centre bar, lifting slot on the north edge, two flag infills |
| condenser (flank) | spec `condenser_flank` | isolator at its north end, 25 mm drop pipe at y 15.86 (clear of the N dining sill end 15.88); conduit loop (v11 f_0045, f_0047): turns up off the envelope run at the unit's back south corner (y 14.975 / 15.025), rises to 0.9 above the lid (z 4.80), runs diagonally down north along the wall to y 15.62, z 4.0, then over the lid's back edge into it at x 3.61, y 15.60 / 15.65 (glands); straps every 0.5 m |
| tap T1 | (3.45, 16.50, 0.20) | brass double tap with a flat lever (points north along the wall, turns out when opened: hinge -90 deg) and a plain second spout; black water-timer box 0.17 x 0.12 with rounded edges and a round dial, three outlets under it (v11 f_0051): yellow = loose tail, teal = reel feed, green = water |
| hose reel | centre (3.45, 16.95, 1.0) | spans y 16.60..17.22, z 0.76..1.24; feed hose from the timer's teal outlet |
| security light | (3.95, 9.03, 3.55) | twin head, click to light |
| solar light | latch post top of `side_gate` | click to light |
| climbers | east fence y 14.45..17.8 | 12 strands, each over the capping (or down through the lattice topper where the site builds one) and down the boards 10 mm off the face (25 mm below z -0.1, clear of the gravel board), four to the paving; kept 0.11 from post centres (site BAY / POST); 0.10 leaves densest at the top, 0.11 leaves bunched along the capping y 16.0..17.3 (v11 f_0045, f_0053, f_0055) |

## East wall E (alley, concrete at -0.30)

| item | position | notes |
|---|---|---|
| condenser (east) | y 5.30..6.15, z 2.35..3.15 | spec `at` read as south end + underside; 0.33 x 0.85 x 0.80; valve cover north, coil guard south |
| isolator | (4.65, 6.29, 3.03) | grey box, red rotary handle, two cables into the service cover |
| twin conduits | base rail y 3.50 -> (3.98, 3.30) -> north at z 3.3 -> down into the lid at the back south corner | one carries on to z 3.70, elbow, thin cable (f_0102, f_0127) |
| wall lights | (4.65, 3.40, 2.65), (4.65, 7.00, 2.65) | anthracite cylinders 0.06 x 0.15 on 0.08 plates; one click group `side_passage.alley_light` |
| small black fitting | (4.65, 5.00, 1.75) | unlit |
| extract grille | (4.65, 6.70, 1.85) | black, 0.15 square, 4 louvres |
| flue | (4.755, 8.55) | white 100 mm, lead slate 0.30 sq + collar, sockets, two clips, elbow at z 2.6, 0.35 ribbed terminal to y 8.985 |
| access cover | x 4.70..5.15, y 7.73..8.33 | concrete with steel edge, 0.5 south of the flue |
| corner cables | NE corner, y 8.97..9.01 | four black cables from the floor over the base rail to z 6.07 |
| vent cowl | (4.65, 1.75, 4.30) | black, 0.25 x 0.30, open below |

## Deviations from the brief

- Positions on E follow the brief (+/- 0.5 in y). v11 f_0096-f_0100 seem to put the small fitting south of the
  conduits; f_0127 (looking north from the street end) agrees with the brief, which was kept.
- Wall lights are off as modelled (lit in state 1), like the other exterior lights; no Cycles lamps (sky-lit area).
- Alley thin cables (gate head to eaves, the loop at 2.9 m) omitted.

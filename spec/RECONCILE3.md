# Phase 3 reconciliation: dimension audit and 21 Nov footage into `spec/house.json`

Inputs: the twelve round-3 surveys with their verification sections (`spec/phase3/{front, porch, passage, garden,
eaves_loft, floor2_a, floor2_b, living_games, dims_envelope, dims_G, dims_1, dims_vert}.md`), the verdict list of the
verifiers (112 proposed changes), `spec/RECONCILE.md`, `spec/RECONCILE2.md` and the spec as it stood.

Outputs: `spec/house.json` (schema house/2, edited in place), `spec/plan_{B,G,1,2,site,section}.png` (redrawn by the
validator), this file and one brief per build unit in `spec/phase3/briefs/<unit>.md` (shell changes old -> new, the
surveyors' notes merged, the footage). `spec/validate_house.py` lost one check (section 3). The spec was written by a
scratch script (`build/r3/reconcile/apply_r3.py`, from `house.before.json` in the same folder) - **it is stale now: edit
the JSON directly**. Room names were already set: `loft_office` = Slate Room, `study` = Rose Room, `purple_room` =
Lavender Room (ids unchanged).

Checks run on the result: `python spec/validate_house.py` OK (28 rooms on 4 levels, 108 walls, 51 openings, 57
features, 6 flights, every room reachable from the vestibule); foundation build `--only shell,site,envelope` BUILD OK, no
Traceback; previews plan:G / 1 / 2, section, elev:front / rear / flank (`build/preview/*_r3reconcile.jpg`); library tests
- see section 5.

## 1. Are the dimensions right?

Mostly yes, and better than before; the interior plan was already close and the biggest errors were outside. In plain
numbers, after this round:

- **Main body**: 4.95 wide inside (party wall -0.65 to east wall 4.30, unchanged) and **5.53 outside** (party line -0.88 to
  the rendered east face 4.65: the east wall is an external wall 0.35 thick with 0.10 of insulation, facing a 1.15 m alley,
  not a 0.23 party wall). Back addition 3.75 inside, **4.33 outside** (flank face 3.45).
- **Length**: 17.48 from the front face (y -0.12) to the rear face (17.36), unchanged. Plot from the footway edge (-5.20)
  to the back of the shed (30.75): **35.95 m**, 1.85 longer than modelled.
- **Storeys**: ground floor 0; first floor 3.04 (rear) / 3.42 (front); second floor 6.02, platform 6.22, loft 6.49 - all
  unchanged and still tied together by the stairs, now **14 risers of 0.2036** on the main flight (not 15 of 0.19).
  Ceilings: ground front 2.95, rear corridor 2.70, dining **2.62** (was 2.80), utility / WC 2.40; first-floor front
  **2.77** (was 2.85), rear corridor **2.60** (was 2.45), yellow room 2.45; second floor 2.60; loft apex 2.12. Main ridge
  9.14; bay gable ridge **8.75** (was 8.295).
- **Largest corrections**: the garden and shed are **1.62-1.85 m further back** (shed front wall 25.14 -> 26.84, rear 28.76
  -> 30.61; deck 0.90 longer); the side alley is **1.15 wide, not 0.90**, and the east wall face 0.12 further out; the bay
  gable is **50 deg with its ridge 0.455 higher**; the Rose Room's main part is **0.31 deeper**; the second-floor arch
  wall and Lavender Room are **0.30 further north**; the first-floor rear corridor is **0.22 wider** (1.12); the forecourt
  falls **0.30**, not 0.08; the Rose Room window is **1.55 wide, not 1.00**; the vestibule is 0.13 deeper (1.86) with a
  0.25 deeper front recess; the bay shifted 0.07 west; the porch eaves dropped 0.25; the rear roof slope is 35 deg.
- **Still uncertain** (section 6): the front half of the loft section (knee-wall position versus roof slope), the
  absolute scale at the front door (frame 1.39 or 1.47), the 0.15 m between the inside and outside axis of the rear
  openings, the depth of the first-floor quarter landing and the second-floor stair head, and where the forecourt strip
  steps down to the alley floor.

## 2. Decision table

Decision: **A** applied as the verdict; **ADJ** applied with another value (said why); **REJ** rejected (present value
kept); **MRG** merged into another item. Values in metres, world frame.

### 2.1 Front (street side)

| id | what | old | new | dec. | why |
|---|---|---|---|---|---|
| front-01 | pier `front_pier_w` | h 1.20, base -0.14 | h 1.40 (17 courses + cap 0.125), base -0.36; cap 0.45, edge 0.085, rise 0.04 (field `cap`) | A | course count verified (17 +/- 1) |
| front-02 | forecourt / mouth / footway / road levels | fall -0.06 -> -0.14; mouth -0.08 -> -0.14; footway -0.16; road -0.28 | -0.06 -> -0.36; mouth -0.08 -> -0.36; footway -0.38; road -0.50 | A | courses under the planter; present was an assumption. The strip beside the bay became its own zone (front-08) |
| front-03 | front wall `front_wall_w` | base -0.10, h 0.90, top 0.80 | base -0.36, h 0.90 at the pier, brick top level +0.54; planter 0.29, bottom 0.47, rim 0.76 (field `planter`) | A | verified; follows front-02 |
| front-04 | bay lights / living bay / cheek walls / door frame | lights centre 2.55; bay 1.10..4.00; cheeks 0.90-1.10 / 4.00-4.15; frame 1.24 | centre **2.48**; bay **1.03..3.93**; west cheek faces **0.75** / 1.03; east 3.93 / **4.25**; frame x -0.67..0.72 | ADJ | verdict's centre and bay faces; west cheek face 0.75 sits between porch-06 (0.71), the porch verifier (0.75) and the front verifier (0.82); east face 4.25 from envelope-01; frame width from porch-01 |
| front-05 | first-floor bay outside / window | outer 0.90..4.15; window 2.53; cheek window 1.03 | outer **0.75..4.25**; `w_green_bay` 2.48; inner bay 1.11..3.85 (2.74 kept); `w_green_cheek_w` 0.93; facades follow | ADJ | verdict, with the east face 4.25 (envelope-01) instead of 4.23 |
| front-06 | bay gable | ridge x 2.525, Z 8.295, 43 deg | ridge x 2.48, **Z 8.75, 50 deg**; planes as verdict; eave edges 6.52, 6.69 at the cheeks | A | three street readings 8.6-8.9, pitch 50 +/- 2 |
| front-07 | porch lean-to extent | x to 0.93 | x to **0.88** | ADJ | slates abut the cheek at 0.75 but fascia / gutter run to a stop end at about 0.88, and lib/envelope.py hangs a downpipe on the plane at x 0.83 (build crashed at 0.75); Z from porch-09 |
| front-08 | forecourt / tarmac strip | setts to 4.53; mouth setts, x 4.15..5.43 to y 0.74 | setts to **4.40**; `forecourt_alley_mouth` x 4.40..5.80 asphalt; new `forecourt_alley_apron` x 4.25..5.80, y -0.12..1.70, falling -0.08 -> -0.30; sett patch in notes | ADJ | limits follow the adopted alley (5.80) and street gate (1.70); split because one linear fall cannot run both to the street and to the alley |
| front-09 | new side gate at the street | - | see passage-05 (`street_gate`) | MRG | one gate, three proposals |
| front-10 | alley wall x | 5.43 | 5.80 | MRG | envelope-08 / passage-06 measured the alley 1.15-1.22 wide; 5.58 rests on a 1.34 leaf read against bricks in front of the gate plane |
| front-11 | east face finish | 4.53 sandstone, "openings unknown" | face **4.65** with insulation (field `insulation`), white return x 4.25..4.65, render kept #D2C596 | A | with envelope-02's 4.65 |
| front-12 | `w_bay_cheek_e` y | 0.37 | **0.43** | A | frame 0.045 from the re-entrant corner |
| front-13 | white car | (3.15, -3.43) | (3.2, -2.7) | A | 21 Nov position; wheel Z from the adopted fall |

### 2.2 Porch and vestibule

| id | what | old | new | dec. | why |
|---|---|---|---|---|---|
| porch-01 | `d_street` width / frame | leaves 1.18, frame 1.24, centre 0 | leaves **1.26**, frame **1.39** (x -0.67..0.72), centre 0.025 | ADJ | verifier's scale P = 0.24 (frame 5.8 P) rather than the survey's 0.232 (1.345); the frame fills from the party wall to the cheek wall |
| porch-02 | `d_street` height | 2.03 | **1.95** | ADJ | 0.03 + 8.0 P at P = 0.24; consistent with the adopted frame width (the survey's 1.89 is at P = 0.232) |
| porch-03 | transom / frame top | 2.12-2.50 / 2.57 | unchanged | ADJ | at P = 0.24 the measured proportions give 2.11-2.49 / 2.57, i.e. the present values |
| porch-04 | front recess depth, piers, vault | 0..0.74; 0.74..1.29 | **0..0.99**; 0.99..1.44 | A | 8.9 tile cells (0.98), snapped to the bay nib line 0.99 |
| porch-05 | vestibule depth | 1.73 (screen 1.73..1.83) | **1.86** (screen 1.86..1.96); front hall 3.22 -> 3.09 | A | 16.9 cells; the hall's first segment absorbs it (verifier's suggestion) |
| porch-06 | east face of the front recess / cheek wall | 0.90; wall 0.20 at x 1.0 | **0.75**; wall 0.28 at 0.89 (faces 0.75 / 1.03) | ADJ | see front-04; the 0.28 is a difference of faces, not measured |
| porch-07 | `w_bay_cheek_w` | (1.00, 0.37) w 0.50 | **(0.89, 0.63) w 0.45** | A | north architrave 0.05 from the pier |
| porch-08 | front-recess ceiling | flat 2.85 + two haunches | haunches deleted; `vest_ceiling_slope` 2.62 at y 0 -> 2.85 at y 0.62 | ADJ | shape verified; 2.62 (not 2.54) because the frame top stays 2.57 (porch-03) |
| porch-09 | lean-to plane | c0 3.3111, cy 0.795 (38.5 deg): eaves 2.85, abutment 3.90 | c0 **3.14**, cy **0.933** (43 deg): 2.58 at y -0.60, **3.83** at the abutment | ADJ | eaves lowered (gutter seen across the transom top); abutment kept 0.37 under the first-floor west sill, which front-07 measured and dims_envelope reads at 4.20 outside; the porch's own 3.13-3.35 would leave 0.95 of wall the footage does not show (verifier's stack warning) |
| porch-10 | porch soffit | flat 2.62 | raked 2.63 at the door head -> 2.40 at the fascia, three downlights (notes) | ADJ | heights on the kept frame top; `PORCH_SOFFIT_Z` is lib (request) |

### 2.3 Side passage and alley

| id | what | old | new | dec. | why |
|---|---|---|---|---|---|
| passage-01 | `side_gate` | (4.50, 9.03)-(4.90, 9.88), w 0.90 | **(4.65, 9.03)-(5.13, 9.96)**, w 1.05, h 1.76 | ADJ | latch post measured from the K corner, which moves to 4.65 (envelope-02) |
| passage-02 | east fence (passage) / side_passage | (4.9, 9.88) -> (4.45, 23.4) | one straight line **(5.13, 9.96) -> (4.42, 25.02)** | ADJ | passes every measured point within 0.05 (1.68 from the flank at the gate, 4.75 at the step, post feet 19.6 / 21.4 / 23.2) |
| passage-03 | fence height | 2.0 | 2.0 | REJ | verifier: boards 1.93, posts 2.03 |
| passage-04 | `d_back` | w 0.84, centre 3.82, hinge 4.24 | w **0.79**, centre **3.885**, hinge 4.28 | ADJ | with envelope-14: frame 0.04 from the moved flank corner (3.45) and 0.02 from the kitchen's east wall; the cat flap stays centred |
| passage-05 | street gate (new) | none | `street_gate` (5.80, 1.70)-(4.76, 1.70), hinge east, leaf about 0.88-0.92 x 1.83, panel to 2.75, base -0.30 | ADJ | merges front-09 (y 1.37), passage-05 (1.6) and envelope-09 (2.0): y 1.70; sizes on the alley-width scale (the gate fills a 1.15-1.22 alley); the line stops 0.11 short of our wall for lib's latch post |
| passage-06 | alley width | wall 5.43 (0.90) | **5.80** (1.15 from 4.65) | ADJ | 5.75 measured from the old face 4.53 and 5.80 from the render (envelope-08) agree within 0.05 |
| passage-07 | `side_alley` level | fall -0.08 -> -0.30 | **level -0.30**, in-situ concrete (key concrete_or_flags) | A | flush with the passage at the garden gate |
| passage-08 | `alley_neighbour_gate` | (4.9, 9.88)-(5.43, 9.6), h 1.9 | (5.13, 9.96)-(5.80, 9.50), h 1.75, bare timber | A | follows the adopted latch post and wall |
| passage-09 | `condenser_east` | (4.53, 8.4, 2.2) 0.3 x 0.8 x 0.7 | **(4.65, 5.3, 2.35)** 0.33 x 0.85 x 0.80 | A | y 8.4 was the flue |
| passage-10 | `w_wc` outside | 0.70, sill 1.22 | **0.82, sill 1.10** | A | interior ledge stays 1.22 |
| passage-11 | `w_utility` outside | 0.56 x 0.82, sill 1.05 | **0.70 x 0.98, sill 0.92** | A | width from the verifier's rectification; interior board 1.05 |
| passage-12 | inspection cover / paving | 0.60 x 0.80 | 0.56 x 0.72 at x 4.50..5.06, y 10.25..10.97; 600-series paving (notes) | ADJ | verifier's 600 scale; x moved 0.06 with the fence |

### 2.4 Garden and shed

| id | what | old | new | dec. | why |
|---|---|---|---|---|---|
| garden-01 | deck | y to 20.50 | y to **21.40** (x -0.75 kept) | ADJ | west edge not confirmed at -0.88 |
| garden-02 | deck_step_n | y 20.5..20.8 | x -0.30..2.75, y 21.40..21.70 | A | |
| garden-03 | lawn | to 23.4 | to 25.02 (west -0.27 kept) | ADJ | west fence kept at -0.75 |
| garden-04 | lavender bed | 20.5..23.4 | 21.40..25.02 | ADJ | as garden-03 |
| garden-05 | fire pit | (1.27, 22.26) | **(1.30, 23.45)** | A | |
| garden-06 | garden_path | 17.55..23.4 | 17.95..25.02, east edge on the fence line (4.74 at the step) | A | |
| garden-07 | passage step | y 17.55 | **17.95**; drain 17.95..18.08 (notes) | A | |
| garden-08 | deck_step_e | 17.75..18.65 | 18.08..18.98 | A | |
| garden-09 | east fence end | (4.45, 23.4) | (4.42, 25.02); posts in notes | A | start from passage-01's latch post |
| garden-10 | west neighbour wall | to 19.65 | to **21.40**, coping 0.30 | ADJ | face -0.75 kept; also settles envelope-13 |
| garden-11 | west fence | 19.65..23.4 | 21.40..25.02, colour #B3A58C | ADJ | x -0.75 kept |
| garden-12 | shed veranda | 23.4..25.0 | 25.02..26.70 (x 0.06..4.22) + `shed_store_apron` x -0.35..0.06, y 25.35..26.70 | ADJ | the verdict's notch as a second zone (one zone per surface rectangle) |
| garden-13 | shed outline / walls | 23.4..28.9; front 25.14, rear 28.76 | **25.02..30.75**; front 26.84, rear 30.61; sides kept | ADJ | side shifts not supported |
| garden-14 | `shed_d1` | (3.35, 25.14) 1.2 x 2.08 | (3.33, 26.84) **1.69 x 2.33** | A | |
| garden-15 | `shed_w1` | (1.8, 25.14) 1.3 x 1.0, sill 1.05 | (1.00, 26.84) **2.00 x 1.22**, sill 1.09 | ADJ | verifier's frontal ratios; brick gauge 84 mm |
| garden-16 | shed roof / walls | topZ 2.25, soffit 1.83, walls 2.67 | topZ 2.40, soffit 2.02, coping 2.70 on three sides (walls 3.12), fascia 1.98-2.20, gutter 2.29, felt 2.30-2.50 (new fields); workshop ceiling 2.13 | A | ceiling is a guess |
| garden-17 | shed store | y 23.75..24.98, doors 24.365 | y **25.35..26.68**, doors (-0.36, 26.02) w 1.23; x -0.36 kept | ADJ | the door plane does not move to +0.06 (brick between window and doors) |
| garden-18 | workshop / `shed_w2` | 25.28..28.62; w2 y 28.76 | 26.98..30.47; w2 y 30.61 | ADJ | x kept |
| garden-19 | plot / siteBounds | rear 28.9 | rear 30.75 (shed sides -0.87 / 4.45), east edge 5.80 at the front and the fence line; maxY 31.0 | ADJ | follows the adopted boundaries |
| garden-20 | trellis | 2 x 0.9 at 17.85..19.65 | 2 x **1.83** at 17.39..21.05 | ADJ | north panel ends 0.35 short of the wall end |
| garden-21 | planters | trough 18.2..20.05 | trough 18.85..20.80 + square planter 20.82..21.26 | A | |
| garden-22 | balcony | x 0..2.30, depth 1.05 | x **0.195..2.315**, y 17.36..**18.48** (2.12 x 1.12), round tube 48 | ADJ | centred on the adopted door axis 1.255 (verdict 1.28, inside +/-0.12) |
| garden-23 | `w_study` lower lights | side-hung | top-hung, out about 40 (35 adopted, floor2b-04) | A | |

### 2.5 Loft and eaves

| id | what | old | new | dec. | why |
|---|---|---|---|---|---|
| eaves_loft-01 | front knee wall | 0.92 | **1.08** | A | verified 1.05-1.07 |
| eaves_loft-02 | raise front roof 0.16 / ceiling plane | front_slope 5.9435 + 0.57735 y | front_slope **6.30 + 0.50 y** (stopgap), eaves_front offset -0.31 -> -0.17; roof unchanged | REJ | outside gutter measured 6.4-6.6; the verifier's stopgap applied so that the 1.08 knee wall shows; front section open |
| eaves_loft-03 | front hatches | 0.70, sill 0.15 | **0.90, sill 0.03** | A | |
| eaves_loft-04 | east front hatch x | 2.975 | **2.48** | ADJ | = gable ridge x (verdict: follow the ridge) |
| eaves_loft-05 | rear hatch | 1.03, sill 0.17 | 0.91, sill 0.15 | ADJ | with the rear knee wall 1.23 (floor2b-06) |
| eaves_loft-06 | bay tunnel top | 7.39 | **8.19** (strip 1.70); polygon over the whole bay 1.11..3.85 | ADJ | verifier's 1.70 / 50 deg |
| eaves_loft-07 | gable ridge / pitch | 8.295 / 43 | 8.75 / 50 | MRG | front-06 (street readings); contains the tunnel |
| eaves_loft-08 | rear void north edge | 8.73 | 8.73 | REJ | derived, contradicts the measured rear slope |
| eaves_loft-09 | rear step drop | 0.12 | 0.12 | REJ | 0.07 not better supported |

### 2.6 Second floor

| id | what | old | new | dec. | why |
|---|---|---|---|---|---|
| floor2a-01 | bathroom2 | 0.40..3.10 x 11.50..13.70 | **0.42..3.10 x 11.66..13.70** (2.68 x 2.04) | ADJ | verifier's placement from the end wall (pier 0.54); north wall unchanged |
| floor2a-02 | arch wall / `w_purple_n` | 0.30 on 11.35 | **0.16 on 11.58** | ADJ | thickness measured twice; position from the end-wall chain |
| floor2a-03 | `d_bath2` | 0.762, centre y 11.951 | **0.686**, centre y 12.055 | ADJ | position as floor2a-02 |
| floor2a-04 | hall east wall / partitions / Lavender Room | 0.22 / 0.30; partitions 0.27 / 0.35; room 0.32..3.10 x 9.29..11.20 | **0.32**; partitions 0.37; room **0.42..3.10 x 9.55..11.50** | ADJ | as verdict; the stair-head jog (0.15 -> 0.32) kept as an interim artefact until stairs2 is re-fitted with its edge at 0.27 |
| floor2a-05 | `a_landing2` | 0.87 at 11.35, springing 1.74 | 0.90 at (-0.20, 11.58), springing 1.72, crown 2.17; east nib in notes | ADJ | y with the arch wall |
| floor2a-06 | `w_purple` lower light | side-hung | top-hung, about 30 deg | A | |
| floor2a-07 | `w_purple` size | 0.75, y 10.25, bar 1.60 | **0.82, y 10.47, bar 1.50** | ADJ | centre moved with the room |
| floor2a-08 | `w_bath2` | y 12.48 | **12.57** | ADJ | south wall at 11.66 |
| floor2a-09 | bathroom2 boxings | boxing 11.50..12.16 | boxing 11.66..12.25; niche kept; new `bath2_shower_lining` 0.05 x 12.48..13.70 | ADJ | slab lining 0.05, not a 0.12 boxing |
| floor2a-10 | `w_bath2_study` 0.75 | 0.45 | 0.14 (floor2b-01) | REJ | consequence of a placement not adopted |
| floor2b-01 | Rose Room door wall / neck | neck 0.97 x 1.11, main room 14.15..16.86 | door wall kept (13.04); neck **0.80**; main room **13.84..16.86** (3.02); `w_bath2_study` 0.14 on 13.77 | ADJ | verifier: total 3.80 door wall to north wall; a door wall at 13.32 contradicts the painting |
| floor2b-02 | `w_study` width | 1.00 | **1.55** | ADJ | merged with envelope-05 (1.50-1.59 by four routes) |
| floor2b-03 | `w_study` height / sill | 1.40 / 0.68 | **1.56 / 0.58** (head 2.14), transom 1.70 | ADJ | merged with envelope-05: interior board 0.545-0.62, head 2.12-2.15 |
| floor2b-04 | `w_study` lower sashes | side-hung | top-hung, about 35 deg; fanlights top-hung | A | |
| floor2b-05 | `w_study` extReveal | 0.24 | **0.19** (reveal 0.24 inside) | A | real wall maybe 0.39; error kept outside |
| floor2b-06 | loft slopes 35 deg | 30 deg both | **rear plane 35 deg** about the ridge (main_rear c0 12.64, cy -0.70; loft rear_slope 12.33 - 0.70 y, flat to 5.31); rear knee **1.23**; velux 7.82..8.49; rear_K gutter 6.15; front unchanged | ADJ | as verdict; knock-on: `stair_dormer` starts at 5.385 where the new slope reaches its flat top |

### 2.7 Envelope

| id | what | old | new | dec. | why |
|---|---|---|---|---|---|
| envelope-01 | bay east cheek outer face | 4.15 | **4.25** (0.40 behind the east face); notch at 0.74 | ADJ | as verdict; gable east eave 4.35 and ridge 2.48 follow front-06 instead of 4.55 / 2.575 |
| envelope-02 | east face / wall | 4.53, 0.23 | **4.65, 0.35** (inner 4.30) | A | |
| envelope-03 | flank face / wall | 3.40, 0.30 | **3.45, 0.35** (inner 3.10) | A | |
| envelope-04 | rear render / chimney | render -0.50..3.40 with a pier; stack -0.98..-0.53, top 9.87 | render to the party line; stack **-1.17..-0.86**, top **9.55** | ADJ | shaft wholly west of the junction; polygon keeps 0.02 on our roof |
| envelope-05 | `w_study` outside | 1.00 x 1.40 | 1.55 x 1.56 from 0.58 (see floor2b-02/03) | MRG | |
| envelope-06 | rear axis | d_french 1.225, windows -0.09 / 2.54 (0.52), d_balcony 1.29, study 1.26 | all on **1.255**: windows **-0.185 / 2.695**, 0.65 wide | ADJ | 1.255 = centre of the dining room with its west wall at -0.59 (dimsG-02) and the verified symmetric screen; outside reads 1.11 (open question) |
| envelope-07 | dining side-window heights | 1.83, bar 1.40 | **2.00, bar 1.32** | A | |
| envelope-08 | alley | 0.90 | **1.15** (4.65..5.80), concrete, open to the sky | A | |
| envelope-09 | alley street gate | - | `street_gate` y 1.70 | MRG | passage-05 |
| envelope-10 | bay gable | 8.295 / 43 | 8.75 / 50 | MRG | front-06 (within the verdict's 8.70-8.77) |
| envelope-11 | `east_E` extent | [0.74, 9.03] | kept; openings [] and "blank gable end" recorded | REJ | cheek ends at 0.74 |
| envelope-12 | rear_K gutter | 6.65 | 6.15 via floor2b-06 | REJ | not applied as proposed; the plane change moves it |
| envelope-13 | west neighbour wall end / fence | 19.65 | 21.40 (garden-10); fence material kept | ADJ | alignment rule gives the new deck edge 21.40 |
| envelope-14 | `d_back` | 3.82 / 0.84 | 3.885 / 0.79 | MRG | passage-04 |

### 2.8 Ground, first floor, verticals

| id | what | old | new | dec. | why |
|---|---|---|---|---|---|
| dimsG-01 | dining ceiling | 2.80 | **2.62** (walls 2.62, chimney breast to 2.62) | ADJ | verdict; the cornice lower edge at 2.53 needs `cornice_dining` reduced to a 0.09 drop (request) |
| dimsG-02 | dining west wall | -0.65 (wall 0.23) | **-0.59** (wall 0.29, outer face -0.88) | A | |
| dims_1-01 | green bedroom ceiling | 6.27 (2.85) | **6.19 (2.77)** | A | |
| dims_1-02 | rear corridor east wall | 0.25 / 0.40 | **0.47** (partition 0.52), chamfer (0.54, 8.73)-(0.47, 8.80), riser return to 0.54 | ADJ | chamfer legs 0.07 |
| dims_1-03 | yellow room west face | 0.35 | **0.57** | A | |
| dims_1-04 | en-suite / blue recess | 0.50 / 0.40 | **0.57 / 0.47** | A | |
| dims_1-05 | `a_landing1` width | 0.80 at -0.18 | **1.00 at -0.09** | A | |
| dims_1-06 | `a_landing1` heights | 1.65 / 2.05 | springing **1.62**, crown **2.12** | ADJ | semicircle on 1.00 |
| dims_1-07 | rear landing ceiling | 5.49 (2.45) | **5.64 (2.60)** | A | |
| dims_1-08 | `w_arch1` | 0.30 on 11.35 | **0.12 on 11.42** | ADJ | thin wall, bay about 0.91 |
| dims_1-09 | green bay window heights | head 2.55, bar 2.00 | kept | REJ | the 2.43 read was the fanlight glass |
| dims_1-10 | quarter landing depth | 0.60 | kept | REJ | cannot be placed (section 6) |
| vert-01 | main flight | 15 x 0.19, going 0.23 | **14 x 0.2036**, going 0.253, R4..R14 from 5.600 by 0.253 | A | |
| vert-02 | hall arch | springing 2.40, crown 2.75, corbels 2.02-2.40 | springing **2.08**, crown **2.55** (semicircle, `haunch` removed), corbels **1.75-2.08** | ADJ | verdict |
| vert-03 | rear corridor ceiling | 2.84 | **2.70** north of the arch wall (new zone `rear_corridor`); 8.13..9.03 keeps 2.84 | A | |

## 3. Knock-on changes made here (not proposed as such)

- East wall (`w_party_e_*`, `w_east_*`, ids kept; notes say "external") centre 4.415 -> 4.475, flank walls 3.25 -> 3.275
  (0.35), `w_flank_1_ensuite` 3.15 -> 3.175 (0.55); every wall end that met them followed; openings on them keep their y.
- Envelope blocks, facades (`front_A`, `front_B`, `bay_cheek_w/_e`, `kitchen_K`, `flank_F`, `rear_R`), roof planes,
  ridge and eaves lines, `bounds.maxX` 4.65, east neighbour massing +0.37, kitchen steps from x 3.45, `condenser_flank`
  and `soil_stack` x 3.45.
- `w_gbath` x 3.82 -> **3.875**: stays over the back door; at 3.82 its frame passed the new flank corner (validator error).
- `kitchen_backdoor_reveal` follows `d_back` (x 3.48..4.29).
- Vestibule: walls meeting the screen (`w_party_w_vest`, `w_party_w_hall`, `w_vest_living`, `w_hall_living`) to y 1.91;
  `d_inner` y 1.91; hallway starts at 1.96.
- Hall pilasters: `hall_pilaster_n` top 2.95 -> 2.70, `hall_pilaster_s` 2.95 -> 2.84 (they stand under those ceilings).
- `living_bay` chamfer corners; new feature `living_bay_cheek_w_reveal` (the west return light sits near the vestibule
  face of the 0.28 cheek wall).
- Dining north recesses follow the windows; pelmet note says it ends under 2.53.
- First floor: `landing1_pier_w`, `landing1_chamfer` to 5.64; `landing1_downstand` z 5.64..5.77; `w_corr_yellow`,
  `w_bay_ensuite` 2.60 high; `w_green_rear(_e)` 2.77 high; `d_yellow` x 0.52.
- Second floor: `w_addition_s_2` 0.56 -> 0.70 thick on 9.20 (8.85..9.55: the old rear wall plus an unseen zone south of
  the moved Lavender Room; the validator caps walls at 0.70, so 8.73..8.85 is an unbuilt strip under the main rear roof),
  `w_hall_purple` from 9.20; `v_head_jog` to x 0.32; `w_flank_2_*` split points 11.58 / 13.77.
- Loft: `w_knee_front` / `w_knee_rear` run to the thicker east wall (b x 4.475); `eaves_rear.ceilingZ` 7.91 -> 7.65
  (lining 1.16 at the knee-wall back on the 35-deg plane); `eaves_front` polygon follows the first-floor bay (bay part x
  1.11..3.85) and `ceilingZ` 8.19.
- Roof: `stair_dormer` south edge (and `main_rear` notch) 5.47 -> **5.385**, where the 35-deg slope reaches the dormer's flat
  top 8.87 (the old 5.47 was the same rule at 30 deg; at 5.47 the slope cut 0.06 into the loft lobby ceiling).
- Porch lean-to polygon to x 0.88 (front-07 row).
- `street_gate` line stops at 4.76 (lib/site._gate puts the latch post beyond the line end, which was inside the house).
- Surface key of `side_alley` is `concrete_or_flags` (the build fails on an unknown material; `concrete_insitu` wanted).
- New fields carried for the site / envelope stages (not read by lib yet): `front_pier_w.cap`, `front_wall_w.planter`,
  `west_neighbour_wall.coping`, `west_fence.colour`, `side_gate.colour`, `alley_neighbour_gate.colour`,
  `street_gate.overPanel`, `east_E.insulation`, shed `roof.coping / fascia / gutterRimZ / felt`,
  `balcony_structure.railing.section`; new exterior feature `front_party_kneeler` (type kneeler, not built yet).
- Notes rewritten where the numbers changed (vestibule dado is 0.965, as in the hall).
- `spec/validate_house.py`: the stack check "upper arch wall" (w_arch1 -> w_arch2) is removed; the two arch walls are thin
  partitions measured 0.14 apart (dims_1-08 at 11.36..11.48, floor2a-02 at 11.50..11.66) and need not stack.

## 4. Coherence

Rooms fit between their walls (validator), walls stack where they carry (party, east, flank, rear, old rear wall, stair
flank), the party wall is continuous at -0.88 / -0.765 on every floor (dining 0.29 thick from the same outer face),
openings moved with their walls, all flights still land (main 14 x 0.20357 = 2.85; second 13 x 0.20 = 2.60; basement 11 x
0.21), the exterior zones still tile the plot (site stage: two small gaps filled at their level, 0.81 m2 beside the
footway under the front wall and 0.10 m2 beside the path), and the roof sits on the walls (eaves at 6.50 front, about
6.15 over face K, dormer and rear flat at 8.87). Known artefacts: the 0.17 jog at the second-floor stair head (until
stairs2 is re-fitted to x 0.27), the loft front stopgap against the 0.30 roof slab (section 5), the downpipe at x 0.83
now inside the first-floor cheek wall (envelope request).

## 5. Tests and requests

`python blender/test_ctx.py`, `test_shell.py`, `test_site.py`, `test_joinery.py` fail **only on assertions of old numbers**
(a softened copy of each runs to its OK sentinel with only those lines reported):
- test_ctx: landing1 chamfer (0.35, 8.73)-(0.25, 8.83), living / green bay chamfer corners 1.10 / 4.00 / 1.16 / 3.90, shed
  store ceiling 1.83, eaves ceilings 7.68 / 7.41, porch plane c0 3.3111, stair_main rise 0.19 and tread 13 = 2.66, riser
  y 6.06 / 6.29, forecourt fall -0.14, side_alley fall (KeyError: the zone has no fall now; level -0.30), zones_of('front')
  (now also `forecourt_alley_apron`), zone_at(4.8, 9.5) (now side_passage), d_balcony x 1.29, alley-mouth level.
- test_shell l.97 (hallway ceilings now {2.3, 2.6, 2.7, 2.84, 2.95}), l.113 (`vestibule.haunch.vest_haunch_w/_e` ->
  `vestibule.haunch.vest_ceiling_slope`), l.119 (loft ceiling min 7.41 -> 7.57), l.131 (tread heights 0.2036 n), l.190
  (downlight on the old front plane).
- test_site l.167 (the side gate no longer sweeps the lower kitchen tread: leaf bottom -0.28, not -0.14).
- test_joinery l.62 (living bay corner (1.1, 0.99) -> (1.03, 0.99)).
- test_envelope: 3 failures, a real conflict, not an old number - roof vertices of main_front (23), bay_gable_w (5),
  bay_gable_e (4) lie inside the Slate Room because the stopgap front ceiling (1.08 knee wall at y 2.54) is only about 0.15
  under the 30-deg roof top where the slab is 0.30 thick. (A fourth, main_rear cutting the loft lobby ceiling, was
  cleared by moving the dormer edge to 5.385.)

Requests for the owners after this round are listed in the orchestrator report; the briefs repeat each one where it
belongs.

## 6. Open questions for the owner with a tape measure

1. **Loft section, front half** (Slate Room): distance from the front knee wall to the front of the flat ceiling strip and
   to the gable-end wall, the knee-wall height (1.05-1.08?) and the front gutter height outside. The gable walls read 35
   deg; the roof outside reads 30 deg with the gutter at 6.4-6.6; the knee wall 1.08 at y 2.54 does not fit both.
2. **Front door**: outer width of the white door frame and the height of a leaf (1.39 / 1.95 adopted; 1.47 / 2.03 if the
   street scale is right).
3. **Bay**: inside width of the first-floor bay and of the living-room bay at the windows, and the depth of the west cheek
   wall from the vestibule (east wall of the front recess) to the living-room window board (0.28 adopted; outside the bay
   is 3.48 wide, inside 2.74 / 2.90).
4. **Rear openings**: from the dining room's west wall to the middle of the French doors (1.85 adopted; outside the axis
   is 2.34 from the flank corner, which puts it 0.15 further west).
5. **Stairs**: depth of the first-floor quarter landing (0.60 adopted, 1.04 measured) and the distance from the main
   flight's top nosing to the hall's rear wall; depth of the second-floor stair head (0.60 modelled, about 0.9 likely).
6. **Second floor**: the Lavender Room's depth (1.95 adopted) and the distance from its south wall to the rear wall of the
   main house below (the unseen 0.82 zone); the pier between the bathroom door and the Rose Room door (0.54 adopted).
7. **Porch roof**: height of the slates where they meet the wall under the first-floor west window, and that window's
   sill height outside (3.83 / 4.20 adopted; the porch survey read 3.1-3.35).
8. **Alley**: the step between the tarmac by the bay return (-0.08) and the alley floor (-0.30), and the street gate's
   distance from the front of the house (1.70 adopted, readings 1.37-2.0).
9. **Shed**: depth of the shed from the veranda doors to the back wall (rear 30.75 +/- 0.35) and the store doors' plane.
10. **Dining cornice**: its depth on the wall (drop), which fixes the ceiling (2.62 +/- 0.04).
11. **Bay lights**: width of one bay light / shutter panel inside (about 0.2 m is unaccounted for between light 4 and the
    east wall).

## Follow-ups

Round-3 follow-ups of the whole-house check, group C (spec, ctx, envelope, site; `build/r3/followups.md`). Each spec
change with its evidence; `python spec/validate_house.py` OK after each. Scratch: `build/r3/fu/C/`.

| id | what | old | new | dec. | evidence / why |
|---|---|---|---|---|---|
| check-0 | `w_bay_cheek_w` (west return light), frame side | centre y 0.63 (glass 0.405..0.855), frame near the vestibule face, `living_bay_cheek_w_reveal` 0.20 deep on the living side | centre y **0.37** (glass 0.145..0.595), width 0.45; reveal feature **deleted**: timber casing, posts and the bay sill board at the living face (x 1.03), uPVC near the vestibule face, as the east return | A | v1 f_0127 and the full-res still t126.4: the light stands between the front-corner drop and the return drop in a dark timber casing flush with the bay face, the shutter wholly visible south of the return drop, plain white wall between that drop and the nib; at 0.63 the glass was wholly behind `living.curtain.0` (y 0.392..0.872). **Conflict left open**: from the vestibule (v9 t26 / t40.5, photo) the north architrave reads against the pier with 0.25-0.30 of plain wall to the corner (glass about 0.40..0.86); a straight hole cannot satisfy both sides; the living side is the one most seen. Owner tape: the light's distance from the bay front corner on the living side. |
| check-1 | kitchen nook (K1) | x 1.37..2.62 (1.25) | x **1.37..2.86** (1.49): kitchen polygon, `kitchen_nook`, `nook_soffit` | A | `reference/work/critic_kitchen/full_765.jpg`, frontal, 2.3 mm/px confirmed on the 0.245 floor tiles at the wall (105 px a tile): three nook doors 653 px = 1.50, pier 270 px = 0.62, tread plate 0.54; the chain 1.25 + 0.12 + 1.49 + 0.62 = 3.48 closes on the back-door reveal (x 3.48), which 1.25 left 0.24 short |
| check-3 | `basement_shelf_w` south edge | y 5.19 | **y 5.30**, just behind the R1 bullnose (riser at y 5.297 / 5.19 / 5.166 at x 0.15 / 0.235 / 0.265) | ADJ | geometry (stair_main R1 quarter-ellipse, centre (0.65, 5.42), semi 0.53 x 0.37). The proposed diagonal edge left a sunk triangle in front of the riser (lib/shell rasterises a diagonal floor_void edge by cell centres; seen in the stairs `bullnose` preview), so the edge is straight at 5.30: the hall floor runs to the riser, the strip behind it lies under tread 1. `stairs.floor_patch` deleted from rooms/stairs.py |
| check-4 | `basement_meter_niche` z | -0.86..-0.43 | **-0.74..-0.31** (top on the ceiling) | A | hr_249, v6 f_0256: the niche is open up to the ceiling; 0.30 x 0.43 by ratio (400 x 575 px) |
| check-5 | `basement_sealed_recess` (new) | - | recess x 4.25..4.48, y 6.60..7.05, z -1.06..-0.46 | A | v6 f_0179: the recess left of the pier, its floor sloping away; basement_plant._recess builds the 35-deg slope in it |
| check-6 | `soil_stack` y | 12.35 (in front of the south 0.15 of `w_bath2`) | **12.13** (stack 12.075..12.185, 0.065 clear of the frame); PIPES branch ends in lib/envelope follow (12.07 / 12.20) | A | v11 t37 / t42 (full-res) and f_0043: the stack runs up beside the south jamb of the bathroom2 window with the whole frame visible north of it, gap about 5 cm (12 px on a 160 px frame); the camera stands south of the stack, so the true position is if anything further south. The top-hung fanlight no longer meets it |
| check-7 / web-0 | front eaves headroom | lining 0.862 at the knee-wall back (the 0.30 slab held it down); ctx.ceil_z = slab underside | `eaves_front.ceiling.planes` (four lining planes, see the room notes); ctx.ceil_z for under_roof rooms = min(ceilingZ, roof_z + offset, ceiling.planes); lib.envelope keeps the slab underside 1 cm above that (0.16 thick over the eaves_front main lining) | A | owner instruction (visitors get into the eaves); the main lining is 1.00 at the knee-wall back as measured (eaves_loft-01/-02); the tunnel keeps its measured section (strip 0.40 at 1.70, 50-deg linings 0.32 under the gable planes, the 0.20 valley band), which roof + offset alone would overstate by 0.15 on the tunnel slopes and up to 0.35 beside the valley band, hence the explicit planes. eaves_rear: roof - 0.31 (unchanged lining). rooms/eaves.py builds exactly ctx.ceil_z and asserts it on a 5 cm grid (3640 / 1796 points, worst < 1 mm) |
| check-8 / web-2 | shed store depth | polygon x -0.77..-0.37 inside `shed_w_west` (0.27, inner face -0.60); `walk: false` | `shed_w_west` split: **`shed_w_west_store`** 0.10 (faces -0.87 / -0.77) along the pier and the store (y 25.02..26.68), `shed_w_west` 0.27 from 26.68; polygon x -0.77..**-0.38** (the door wall's inner face); `walk: true`. Store **0.39 deep** inside | ADJ | No round-3 frame shows the door plane (the climber covers it, garden V.6 4; RECONCILE3 question 9 stays open). Kept the depth the site shell already carved and the room module furnishes: v2 f_0264 shows shelves holding 2.5 l paint tins and a bowl (shed.md: 0.34 deep) on a store block about 1.0 m wide from the boundary (garden survey, v11 f_0194-0196, v13 f_0217); a 0.27 back wall would leave 0.22, too shallow for those shelves. The thinner wall is a half-brick skin on the boundary |
| check-10 | stair-head jog | - | not changed | REJ (left) | v13 t4.5 / t5.5 / t6 do show the top nosing running into the hall wall's skirting (no 0.17 ledge), but the fix moves the platform edge, balustrade, `v_head_nosing`, `o_stairs2_head` and the second flight's west string to about x 0.27, and the frames do not settle whether the flight becomes 0.72 wide or the well's east wall moves (floor2_a knock-on 1: "could not settle"); the stair-head corner near y 9.05 hangs on the quarter-landing depth, left to the owner this pass (open question 5). Needs the stairs2 owner and the owner's tape |
| check-17 | vestibule ceiling in ctx | ceil_z 2.85 over the slope | ctx.ceil_z includes `ceiling_haunch` slopes: 2.62 + 0.371 y for y 0..0.62 | A | lib change only (vest_ceiling_slope, porch-08) |
| check-28 | envelope odds | main_rear underside dipped to 8.58 at y 5.371..5.38 | each underside vertex reads the ceiling of its own face's side: the slab steps 8.62 / 8.58 at y 5.38 | A | the `loft_office.step_cover` stand-in is no longer needed (room owner). The gable-face triangle (y 3.90..4.33, Z 8.25..8.465) is the shell's grid (the Slate Room end-wall faces, see rooms/loft_office.py), not the envelope: left for the shell owner. The front return trim on the cheek window head: no frame cited and v8 f_0031 / f_0061 do not show the east cheek window head and the cornice in one view; not changed |
| check-30 | shed SW downpipe | x -0.76 | **-0.53** | A | lib/site took the west parapet thickness from the last vertical wall on the west half (the store's 0.04 door wall), so the felt field, the fascia and the downpipe started at -0.83; now the thickest wall whose outer face lies on the outline (0.27). v2 f_0193 / f_0194: the downpipe drops down the pier face east of the nest box, about 0.3 of the pier width from its west end |
| web-1 | sauna bench and heater | outline only | `bathroom2.sauna.seat` plan_sym `bench`, `bathroom2.sauna.heater` plan_sym `heater` | A | viewer pen rule (MULTILEVEL 11.2: inside a pen only footprints of their own block) |
| found-2 | `side_passage.gully` | - | no change | - | already set into the passage flags at -0.30 (built top -0.297), x 4.40..4.55 under the K downpipe shoe (4.45, 9.15); centre 4.475 keeps it clear of the lower tread's east end (4.395) |
| check-29 | stair_main waist over the basement shaft | - | not done | - | lib/stairs is not a group-C file |

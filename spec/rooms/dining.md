# Dining room (`dining`) — visual / dimensional specification

Sources: every frame f_0569–f_0741 (viewed), 43 full-res stills in `reference/work/dining/full/`
(`F_NNN.jpg` = still at t = NNN s = frame f_(NNN+1)), owner narration 09:24–12:18.
Owner: "this is the most important part".

**Accuracy.** Ultrawide lens, no measured dimension. Heights are scaled from the hall door (opening
2.00 m, still F_741) and cross-checked on three walls; lengths along walls come from the
dado-to-cornice pixel height at each point (gives depth) — the two identical carved panels at opposite
ends of the west wall come out the same size by this method, which validates it. Expect +/-5 % on
heights, +/-0.15 m on room size, +/-0.05 m on positions along a wall.

## 1. Shape & dimensions

### Room-local frame
- Origin = **south-west inside corner at floor level** (the corner immediately on your LEFT as you step in
  through the hall door). **+x = east = world +X** (to your right as you enter). **+y = north = world +Y**
  (straight ahead as you enter, toward the garden). z up, floor z = 0 (level with the hall, no step).
- World mapping (layout.md): local (0, 0) = world (-0.775, 12.58).
- Walls: **S** (y = 0) backs onto utility + rear corridor, faces the house front; **N** (y = L) is the rear
  external wall to the garden; **W** (x = 0) is the party wall (house-left); **E** (x = 3.775) is the
  external flank wall to the side return (house-right).

### Size
| item | value | note |
|---|---|---|
| width (x), W wall to E alcove wall | **3.775 m** | agrees with layout.md (85-inch TV + door add up to 3.78) |
| length (y), S wall to N wall | **4.50 m** | **differs from layout.md (5.22)** — see section 10, item 1 |
| ceiling | **2.80 m** flat | cornice bottom at 2.65 |
| plan | plain rectangle + chimney breast on E wall | no bay, no nibs, no alcove cupboards |

If the canonical length in `house.json` stays different from 4.50, keep every element size given here and
keep the E-wall and W-wall arrangements **centred on mid-length**; stretch only the plain gaps.

### Chimney breast (E wall)
- Projects **0.18 m** into the room, **1.62 m** wide, centred on mid-length: y 1.44 .. 3.06, front face
  at x = 3.595. Full height; cornice, dado rail and skirting all return around it (seen f_0634, f_0639,
  F_638).
- The two alcoves either side (y 0 .. 1.44 and y 3.06 .. 4.50) are the plain E wall at x = 3.775; each holds
  one tall narrow window and one wall light.

### N wall build-up
The N wall is a ~0.30 m external wall. Its whole width is treated as one dark timber screen (section 2):
windows and French doors sit ~0.22 m back from the room face in dark-lined reveals. Above the screen a
plain white boxed pelmet runs wall to wall under the cornice.

### Floor levels
None. Oak boards run straight through the hall doorway with no threshold strip (F_741). French-door
threshold: white uPVC cill, ~40 mm upstand.

## 2. Openings

All heights above floor. "Left/right" are as seen from inside the room facing that wall.

### 2.1 Hall door — S wall, west end
| item | value |
|---|---|
| clear opening | x 0.175 .. 1.013 (**0.838 wide**, a 2'9" leaf — measured 0.82–0.88 in stills t=290, 740, 741), 1.981 high; wall 0.13 thick. Scale the leaf's panel and stile widths below by 1.10. |
| leaf | oak veneer, 4 panels: two tall upper (0.24 x 0.93) over two short lower (0.24 x 0.52), flat recessed panels with a small bolection bead; stiles/top rail 0.10, lock rail 0.20 (centre 0.92), bottom rail 0.22; 35 mm thick; satin lacquer |
| hinge / swing | hinged on the **west** jamb, swings **north into the dining room** and parks parallel to the W wall about 0.12 m off it (free edge at y ~0.80). Model it open at 90 deg. Brass projecting door stop on the W skirting at y ~0.72. |
| handle | polished-brass lever on a short rectangular backplate (0.045 x 0.12), both faces, lever axis at 0.95; lever 0.11 long pointing away from the hinge |
| lining | white painted on the hall half, dark stained on the dining half |
| dining-side surround | dark stained (section 3 "joinery stain"). Side architraves 0.11 wide, reeded (three 12 mm half-round reeds on the outer half, flat inner half), running to the floor (skirting butts into them). Head: plain frieze board 0.08 high, the same width as the outside of the architraves, then a projecting cornice cap 0.09 high (fillet 15, cyma recta 45, fillet 12, cavetto 18 mm) projecting 0.06 at front and 0.035 past each end. Cap top at **2.20** (level with the TV top). Only ~0.06 of the west architrave shows before the W wall. |
| connects | rear corridor of the hall (one straight sight line to the vestibule doors, f_0741) |

### 2.2 E-wall windows (2, identical, mirror-symmetric about mid-length)
| item | value |
|---|---|
| centres | y = **0.66** (south alcove) and y = **3.84** (north alcove); outside of architrave 0.30 from the room corner and 0.42 from the breast |
| surround | full-height dark stained "aedicule", 0.72 wide over the architraves, standing on the floor. Architraves 0.10 wide, same reeded section as the door. Entablature: frieze 0.08 + cap 0.10 (same profile as door), cap 0.80 long, top at **2.45** (0.20 below the cornice). |
| reveal | 0.52 wide between architraves, dark-stained lining ~0.12 deep, head soffit at 2.27 |
| sill | dark stained board 30 mm thick, top at **1.10**, nosing 40 mm proud of the apron, fitted between the architraves |
| apron | flat dark stained panel from under the sill to the floor, set 15 mm behind the architrave face, no skirting or dado rail across it (rail and skirting stop against the architraves) |
| window | white uPVC fixed/casement, single light, visible frame 0.50 x 1.14 (z 1.11 .. 2.25), frame face 45 mm, **obscure stippled glass** (reflective at night; nothing visible through it) |
| connects | side return (outside), not filmed |

### 2.3 N wall — dark timber screen with French doors and two side windows
Narration: "there's an identical window on each side". Model symmetric about x = 1.8875.

| item | value |
|---|---|
| screen frame | dark stained architrave 0.10 wide on the room face around the whole group: outer edges x 0.08 and 3.70, head top at **2.50**. Reveal linings (jambs, soffit) dark stained, **0.22 deep**. Soffit at 2.38. |
| posts | two dark stained posts (mullions) 0.12 wide on the room face, centred x 1.19 and 2.585 (beside the door frame); between each post and the nearer side-window frame (x 0.83 .. 1.13 and 2.645 .. 2.945) a flat dark stained infill panel, full height. Posts and infills are hidden behind the tied-back curtains. |
| French doors | white uPVC, frame x 1.29 .. 2.48 (**1.19 wide**), frame top **2.32**. Two leaves 0.535 x 1.95, meeting at x 1.8875. Each leaf: 70 mm stiles/rails, a mid rail 90 mm centred at 0.95, clear glass above (0.40 x 0.86) and below (0.40 x 0.62). Transom 70 mm at 1.97 .. 2.04; fanlight above, one clear pane 1.07 x 0.20. Polished-brass lever handles on long backplates (0.035 x 0.22) either side of the meeting stiles, lever at 1.02. Hinged at the outer edges, **swing out** to the garden (never opened on camera). **Round cat flap** in the lower pane of the west leaf (fixed fitting, keep — same rule as the kitchen back door): white ring ~0.26 outer diameter with a clear/smoked flap, centre ~0.33 above the floor, centred in the pane (f_0681). |
| side windows | white uPVC single light, both 0.52 wide, centres x **0.57** and **3.205**, clear glass (dark at night). **They are not the same height** (stills t=681/683 vs t=694/700): **west** frame z 1.10 .. 2.23 with a white uPVC window board 25 mm at 1.10; **east** frame z 0.30 .. 2.20, one continuous clear pane, trickle vent at the head, bottom rail far below the dado. Dark timber fills between window head and soffit. |
| aprons | dark stained flat panels below both side windows down to the floor: full height (to 1.10) under the west window, only 0.30 high under the east one |
| pelmet | plain white painted box, z 2.50 .. 2.65, projecting 0.12 from the wall face, running x 0 .. 3.775; the room cornice runs along its top front edge; curtain track fixed under it |
| connects | garden |

### 2.4 Fireplace opening
See section 4 (E wall, on the chimney breast, centred y = 2.25).

## 3. Surfaces

### Colours (sampled = median sRGB of a clean patch in the still named; "wb" = white-balanced against the
white dado rail in the same still; estimate = best guess under neutral light)
| surface | sampled | wb | **estimate** | finish |
|---|---|---|---|---|
| walls above dado | #c9c1b3 (F_741), #aba491 (F_635), #c3bfb1 (F_719) | #e3dcd5 / #ddd4c6 / #e0dbce | **#dfd8cb** pale warm stone-cream | matt emulsion |
| walls below dado | #382a2a (F_741), #2c2323 (F_635), #3b312f (F_719) | #3f3032 / #392d30 / #443837 | **#40302f** dark aubergine-brown | dead matt, fine woven/felt-like texture (textured wallcovering; grain ~2 mm) |
| dado rail | #d8d4c6 (F_741), #bdbbad (F_635) | reference | **#f2f0ea** white | satin |
| cornice, pelmet | #bcb094 (F_741) | #d4c9b0 (in shadow) | **#f3f1eb** white | matt |
| ceiling | #b8ad95 (F_741), #c4bdaf (F_719) | #d0c5b2 / #e2d9cb (in shadow) | **#f3f1eb** white | matt |
| joinery stain (skirting, architraves, window surrounds, aprons, N screen) | #40372d, #42392d (skirting), #39302b, #382f28 (architrave) | #483f36 / #403733 | **#3b2e26** very dark walnut/Jacobean oak, grain just visible | satin-gloss varnish (clear highlights) |
| floor | #cdc0a0 (F_741), #cbbe9e, #c7b996, #c0b291 | #e8dbbf | **#d6c7a6** pale natural/limed oak | matt lacquer, slight sheen |
| hall door leaf | #beab7f (F_741), #b5a174 (F_719) | #d7c397 / #d0b987 | **#cfb682** light oak | satin |
| uPVC frames | #e3dfd2 (F_680) | — | **#f4f3ee** | gloss plastic |

### Walls
- Same scheme on all four walls and the chimney breast: dark aubergine-brown from the skirting to the
  dado rail, pale stone-cream from the rail to the cornice.
- **Dado rail**: top at **1.05**, 55 mm high, 22 mm projection, white. Profile: reeded — five 8 mm
  half-round reeds between a 6 mm top bead and a small bottom cove. Runs on all walls, returns around the
  breast, stops square against every dark architrave (door, 2 E windows, N screen). Hidden behind the
  fire surround.
- **Skirting**: **0.18** high (round 3; was 0.15), 20 mm thick, joinery stain. Profile: plain 0.135 face, then a torus
  (15 mm), fillet and ogee (25 mm) top. Runs on all walls and around the breast; stops against
  architraves and the fire-surround plinths.
- No picture rail, no wall panelling.

### Cornice (all walls, around the breast, along the pelmet front on the N wall)
- White plaster, drop **0.15**, projection **0.13**. From the ceiling down: 15 mm flat on the ceiling,
  cyma recta 30 mm, fillet 8 mm, **enriched band 55 mm high** on the 45 deg face, 10 mm bead, cavetto
  25 mm, 10 mm fillet to the wall.
- Enriched band: **not dentils** — a continuous run of upright acanthus/water leaves in relief, one broad
  ribbed leaf alternating with a narrow dart-like leaf, repeat ~**75 mm**, relief ~6 mm (sharpest in
  f_0636, f_0637, f_0687, f_0732; crop `reference/work/dining/c/n636_cornice.jpg`). A normal/bump
  texture tiled at 75 mm is adequate.

### Ceiling
- Flat, white matt. **Ceiling rose** centred on the room (x 1.8875, y 2.25): white plaster, diameter
  **0.90**, max relief ~45 mm.
  - Outer ring (radius 0.36 .. 0.45): ~36 radiating pointed acanthus leaves forming a serrated outer edge,
    each leaf ~75 mm long, a small round boss/rosette (25 mm) between neighbouring leaf bases.
  - Plain raised moulding ring at radius 0.34 .. 0.36 (bead + cove).
  - Centre dish (radius < 0.34), slightly recessed: asymmetric naturalistic relief of large open flowers
    (roses/peonies) and fruit with curling leaves, 3 main blooms, filling the dish.
  - Best views: f_0711, f_0714, f_0715, f_0672 (crop `c/rose.jpg`).

### Floor
- Engineered oak boards, **~0.21 wide**, random lengths 0.6–2.0 m, laid **north–south** (parallel to the
  long walls, continuous with the hall corridor boards), micro-bevelled edges, visible knots and filled
  splits, brushed grain. Colour pale natural oak (table above), board-to-board variation +/-6 % lightness.
- Hearth slab in front of the fireplace (section 4). Two grey door mats exist at the French doors — omit.

## 4. Fixed fittings

### 4.1 Fireplace (E wall, on the breast, centred y = 2.25) — "beautiful fireplace"
Dark carved oak surround with a cast-iron tiled insert. Depths are measured out from the breast face
(x = 3.595) toward the room.

| part | size / position |
|---|---|
| overall | body 1.39 wide (y 1.555 .. 2.945), mantel shelf 1.51 wide, shelf top at **1.19**, body depth 0.18, shelf depth 0.24 |
| plinth blocks (2) | 0.24 wide x 0.18 deep x 0.30 high, plain with a moulded top and a shallow pyramid ("diamond point") on the front face |
| columns (2) | free-standing **barley-twist** (rope) columns, diameter 0.11, z 0.30 .. 0.90, one full twist per ~0.16; carved gadrooned cup base (0.10 high, widest 0.14) and a turned ring capital |
| lower cornice | moulded band z 0.90 .. 0.96 across the full body, breaking forward 0.04 over each column |
| frieze | z 0.96 .. 1.15. Three scrolled console brackets carry the shelf: one at each end (0.12 wide x 0.19 high, projecting 0.10, S-scroll with vertical fluting) and a narrower one (0.07) in the centre. Between them two recessed panels 0.42 x 0.15 carved in relief with scrolling acanthus foliage. |
| mantel shelf | 40 mm thick, ogee-moulded front and ends, z 1.15 .. 1.19 |
| colour | #52463a, #655849 sampled on lit faces (F_641, F_643); estimate **#3f3025** dark oak, satin varnish, slightly redder than the wall joinery |
| insert | fills the 0.91 x 0.90 opening between the jambs. Cast iron, **antique-bronze finish** (est #6b5a3a on relief, #2a2622 in recesses). 30 mm moulded outer frame; a 0.10 high top bar with a running geometric relief (lozenges/scrolls). |
| tile strips | one each side of the fire opening, 0.152 wide: **5 tiles of 152 x 152 mm** stacked (z 0.10 .. 0.86). Tube-lined Art-Nouveau tiles: **yellow sunflowers** (est #e2b93b, brown centres #6a4320) with green leaves (#5d7a3a) on a dark green-black ground (#1d241b), gloss glaze. |
| fire opening | 0.40 wide between the tile strips, arched top; a relief-cast bronze **canopy hood** 0.40 wide x 0.25 high at the top; matt black fireback (#151515); at the bottom a black cast grate front with horizontal bars and ash-pan cover, 0.20 high, projecting 0.08 |
| hearth | polished cream marble/travertine slab, 1.50 wide (centred) x **0.50** deep from the breast face (so ~0.30 beyond the plinths), 20 mm thick, laid on top of the oak floor. Sampled #c5bfb4, #d3cfc5; estimate **#e2dccf** with faint beige veining, semi-gloss. |

### 4.2 Television (S wall)
- 85-inch flat TV, **1.89 x 1.08 m**, 30 mm thick on a slim wall mount (back ~40 mm off the wall),
  x 1.51 .. 3.40 (0.39 clear of the door architrave, 0.35 from the E wall of the 3.75 room), z **1.15 .. 2.23** (bottom 0.10 above the dado rail). Black glossy screen (#0b0b0c),
  5 mm black bezel. No soundbar, shelf or cabinet below it.

### 4.3 Switches and sockets (all white moulded plastic, 86 mm high)
| item | wall | position (centre) |
|---|---|---|
| 3-gang switch, 146 x 86 plate with three small round push/toggle buttons in a row | S | x 1.32, z 1.37 (midway between TV and door architrave) |
| double socket 146 x 86 | E, south alcove | y 1.25, z 0.25 |
| double socket 146 x 86 | E, north alcove | y 3.25, z 0.25 |
| single socket (uncertain) | W | y ~4.0, z 0.45 (behind the cat tree, f_0737) |

No radiator in the room. Omit: wireless thermostat (E wall, y 0.15, z 1.50), alarm PIR (E wall, y 0.15,
z 2.52), small white sensor bar by the TV top-left corner, cable from the socket.

## 5. Furniture

### 5.1 Dining table — "massive dining table"
Antique dark oak **draw-leaf refectory table**, shown with both end leaves pulled out.

| item | value |
|---|---|
| position | long axis north–south, centreline x = **1.80**, centred y = **2.25**; top spans y 0.88 .. 3.62. Clear ~1.33 to the W wall, ~1.14 to the fire surround, ~0.88 to the S and N walls. |
| overall (extended) | **2.74 long x 0.90 wide x 0.77 high** |
| main top | 1.50 x 0.90, 35 mm thick, three or four wide oak boards lengthwise with visible joints, thumb-moulded (rounded) edge, heavily French-polished: high gloss with strong highlights, worn/rubbed patches |
| leaves (2) | 0.62 x 0.90 each, same thickness and edge; top surface ~8 mm below the main top, so a clear straight seam/step shows at y 1.50 and y 3.00. The N leaf (toward the French doors) and S leaf (toward the TV) are identical. |
| frieze / apron | 0.11 deep under the main top, inset 0.07 from the edge; carved along its length with a band of lunettes/strapwork and finished with a **scalloped (wavy) lower edge**, ~0.12 per scallop (f_0599, f_0600, f_0608) |
| legs (4) | at the corners of the main section (y 2.25 +/- 0.60, x 1.80 +/- 0.32). Massive Elizabethan-style **cup-and-cover (melon bulb) legs**: 0.13 square block at top (0.12 high), carved bulb 0.21 max diameter x 0.30 high with gadrooned upper half and acanthus-leaf lower half, ringed neck, 0.13 square block at the bottom (0.14 high) on a 0.03 bun/pad foot |
| stretchers | low box stretcher joining the four bottom blocks, 0.07 x 0.05 section, top 0.13 above the floor |
| colour | sampled #68523e (F_574), #604c3c (F_702), highlights #9d8363 (F_672); estimate **#5e4631** dark-medium brown oak, legs and frieze darker **#3a2a1e** |

### 5.2 Chairs — 8, Chippendale style, dark mahogany
Owner: three per long side with the **middle one an armchair**, plus one at each end.

Common design: frame dark red-brown mahogany, estimate **#3b241a**, semi-gloss. Back: serpentine
"cupid's-bow" crest rail with upturned carved ears and a carved shell/leaf at the centre; **pierced vase
splat** of interlaced ribbons/Gothic loops between crest and a shoe on the back seat rail; back uprights
gently raked. **Drop-in seat** upholstered in tapestry (section 6), sitting inside a moulded seat frame.

| type | qty | size W x D x H | details |
|---|---|---|---|
| side chair | 6 | 0.53 x 0.50 x 0.97, seat height 0.47 | straight square front legs 45 mm (moulded outer faces, chamfered inside), plain H-stretcher 0.15 above the floor, back legs splayed rearward |
| armchair (carver) | 2 | 0.64 x 0.56 x 0.99, seat 0.47, arm 0.69 | **cabriole front legs with carved acanthus knees and ball-and-claw feet**; open scrolled arms sweeping down from the back uprights to curved arm supports set back from the front legs; carved leaf on the hand-rests; no stretchers (f_0581–0584, f_0640) |

Positions (seat centre, facing the table; all tucked in so the seat front is ~0.10 under the top):
| chair | x | y | faces |
|---|---|---|---|
| south end, side chair | 1.80 | 0.63 | +y |
| north end, side chair | 1.80 | 3.87 | -y |
| west side, side chair (at S leaf) | 1.17 | 1.18 | +x |
| west side, **armchair** (middle) | 1.12 | 2.25 | +x |
| west side, side chair (at N leaf) | 1.17 | 3.32 | +x |
| east side, side chair (at S leaf) | 2.43 | 1.18 | -x |
| east side, **armchair** (middle) | 2.48 | 2.25 | -x |
| east side, side chair (at N leaf) | 2.43 | 3.32 | -x |

(In the video the west armchair is pulled out toward the W wall and the east armchair sits in front of the
hearth; model both tucked.)

### 5.3 Nothing else is furniture
No sideboard, no dresser, no rug. The grey multi-level cat tree in the NW corner is excluded.

## 6. Soft furnishings & decor

### 6.1 Chair seat fabric
Woven tapestry, Jacobean "tree of life" floral: cream ground with scrolling stems, large stylised flowers
and leaves. Sampled (f_0583): ground #e8e3d1, red #a67161, blue #7b8c86, green #929a7e; estimates:
ground **#ebe4d0**, terracotta red **#b4513f**, dusty teal **#5f8e98**, sage green **#7d9160**, small
ochre accents **#c9a24a**. Motif scale: main flowers ~0.10 across, repeat ~0.30. Texture source: f_0583
quad approx (144,670) (353,674) (475,850) (130,922); also f_0582, f_0588, f_0594.

### 6.2 Curtains (N wall)
- Two full-length curtains, one in front of each post between a side window and the French doors,
  permanently tied back. Stack width ~0.50 at the heading narrowing to ~0.30 at the tie-back, then
  falling straight to the floor. West curtain centred x **1.03**, east curtain centred x **2.75**; they
  hang ~0.10 in front of the screen.
- Heading: pencil pleat, 75 mm tape, on a white track under the pelmet (top of curtain z 2.50); bottom
  hem 10 mm above the floor.
- Fabric: large woven check (owner: "curtains"; BRIEF: check). Ivory ground with broad taupe-grey bands
  both ways: band ~0.09 wide, pitch ~0.20, darker squares where bands cross, a fine paler line through
  the middle of each band. Sampled F_680: light #d7d0c2, dark #898272; estimates ivory **#e7e1d3**,
  taupe **#9a9382**, crossing squares **#7f7868**. Soft matt weave. Texture source f_0681/f_0685.
- Tie-backs at z ~1.00: twisted cream cord looped round the curtain to a small brass hook on the post,
  with a turned cream bead (40 mm) and a long **gold tassel** 0.30 long x 0.07 wide (est #c9b45a).
- No shutters, no blinds (thin white blind-pull cords visible in f_0694/0698 — omit).

### 6.3 Plants (keep)
| plant | position | description |
|---|---|---|
| Monstera (Swiss cheese plant) x 2 | one on each E-window sill (y 0.66 and 3.84) | 8–10 glossy split leaves 0.15–0.22 across on long arching stems, overall 0.55 wide x 0.45 high; green crackle-glazed ceramic pot, 0.15 dia x 0.15 high, mottled jade/teal (est #5f8f7a) on a small cork mat |
| citrus tree (lemon/calamondin) | NE corner, pot centre x 3.35, y 4.10 | single bare stem 0.75 then a round leafy head 0.70 dia, top at ~1.75; glossy mid-green leaves (est #3f6b2e), some bronze new growth; olive-green embossed glazed pot 0.33 dia x 0.30 high (est #6f7a45) on a low dark wooden stand 0.08 high |

### 6.4 Wall-hung pieces
Quads are pixel corners TL, TR, BR, BL in the 720x1280 frame `reference/frames/f_NNNN.jpg`.

**W wall** (standing at the table facing west: door leaf at far left, garden at right). "Mirror in the
middle of the wall … two wood carvings around it".

| piece | centre (y, z) | outer W x H | description | texture source |
|---|---|---|---|---|
| carved panel A (south) | y **1.15**, z 1.70 (bottom 1.26, top 2.14) | 0.44 x 0.88, 45 mm thick | dark stained frame 45 mm wide with flat outer band and a 6 mm **gilt inner slip**; inside it a moulded border and a fielded oak panel carved in high relief (to 30 mm) with a **hanging grapevine**: vine leaves at the top, a long tapering bunch of grapes down the centre, more leaves and tendrils below, a small moulded base. Est #2f2a26, satin. | f_0724 (125,262) (383,311) (369,785) (99,796); also f_0732 close-up |
| triptych mirror | y **2.275**, z 1.685 (bottom 1.26, top 2.11) | 1.47 x 0.85, 40 mm thick | dark oak bolection-moulded frame, members 75 mm; divided by two 90 mm mullions into three **bevelled** mirror plates: left 0.30, centre 0.52, right 0.30 wide, all 0.70 high, 20 mm bevel. Frame sampled #362f2a, est **#3e3027**. Hangs from two small brass hooks just above the top edge. Reflects the fireplace opposite. | geometry only (real mirror material) |
| carved panel B (north) | y **3.36**, z 1.71 | 0.44 x 0.88 | same as A (a pair; carving differs slightly, also grapes and vine leaves) | f_0739 (326,258) (559,342) (578,852) (331,942) |

**Crest plaques ("shields … along the top")** — regimental/naval wall plaques: a wooden shield-shaped
board (mid-brown or dark varnished, est #7a5230 / #3a2a20) ~**0.15 wide x 0.18 high x 20 mm**, flat top
with small shoulders and pointed base, carrying an enamelled/gilt relief crest and usually a small scroll
below. A few are different shapes (below). Each one differs; a generic shield with a rectified crop is
ideal, otherwise vary crest colours (navy, red, black, gold, light blue).

| group | count | positions |
|---|---|---|
| W wall, top row | 16 | centre z **2.50**; y = 0.20 + 0.265 k, k = 0..15 (last at 4.18). From the south: 3 round black "ship's badge" style crests (rope-ring with crown, 0.17 dia), 1 diamond/lozenge naval badge (white and blue), then 12 shields |
| W wall, lower row | 12 | centre z **2.27**; y = 0.865 + 0.265 j, j = 0..11 (first is just north of the open door leaf, last at 3.78), staggered half a pitch against the top row |
| S wall, over the door | 5 | centre z 2.50; x = 0.22, 0.50, 0.78, 1.06, 1.34 (the one at x 0.50 — dark blue with a gilt royal coat of arms — is centred over the door) |
| S wall, east of the sword | 3 | smaller shields 0.11 x 0.14, centre z 2.50; x = 2.98, 3.26, 3.54 |

Sources: whole W wall F_719/f_0720; close-ups f_0731–f_0736, f_0722–0724, f_0727; S wall f_0741, f_0629,
f_0613. Total 36.

**Mounted sword (S wall, above the TV)** — dark stained wooden board **1.24 x 0.22 x 20 mm**, long edges
straight, ends cut to a shallow point/ogee, x 1.67 .. 2.91, z 2.32 .. 2.54. On it, horizontally and
parallel, held by two pairs of black iron hooks: an infantry officer's **sword** (straight polished-steel
blade, nickel/steel basket hilt at the east end, ~1.0 long) above its **steel scabbard** (~0.85 long).
Best views f_0613, f_0624, f_0629, f_0630.

**Framed picture over the mantel (E wall, breast)** — the original is a signed wedding portrait:
**do not reproduce**. Keep the frame, replace the picture with a neutral landscape.
- Outer **0.61 x 0.85**, centre y 2.25, z 1.96 (bottom 1.54, top 2.39), hung flat, 35 mm thick.
- Frame: ornate gilt, 60 mm wide, running leaf-and-bead ornament, est #b9a160 with darker recesses.
  Wide cream mount (~0.11, est #ece7da — leave plain, no signatures), thin gilt fillet, dark-red inner
  slip (5 mm, #7a2a2a), picture window ~0.27 x 0.40.

### 6.5 Mantel ornaments (keep; on the shelf top z 1.19, symmetric about y 2.25)
| item | position | description |
|---|---|---|
| antique mantel clock | centre | black slate/marble architectural clock, 0.32 wide x 0.16 deep x 0.37 high: stepped plinth, body with small green-marble colonnettes at the corners, stepped top with a low dome; cream enamel dial 0.11 dia with brass bezel, black Roman numerals. Est #1d1b1a polished. |
| candelabra x 2 | y 2.25 +/- 0.48 | dark wood barley-twist pedestal 0.07 square x 0.20 high with a gilt-brass acanthus mount on the front, carrying a cast-brass **5-light candelabrum** 0.26 wide x 0.40 high: central baluster stem with a tall urn/flame finial, four scrolled arms with drip pans and candle cups plus a centre cup. Antique brass, est #a8873d. Total height 0.60. |
| candlesticks x 2 | y 2.25 +/- 0.68 | small brass candlestick 0.08 high with a tall white taper candle 22 mm dia x 0.36 high |

The green garland with gold baubles and cream poinsettias draped along the shelf is seasonal — omit.

## 7. Lighting (all lamps warm white ~2700 K)

### 7.1 Chandelier — "remember the design"
Hangs from the centre of the ceiling rose (x 1.8875, y 2.25), over the table.
- Overall diameter **0.80**, height of the fitting 0.55; polished-brass ceiling cup (0.12 dia, pierced
  ring of dots) at the ceiling, short brass stem 0.12, shade tops at z ~2.45, lowest crystal at z ~2.00.
- Frame: polished gold-brass (est #c9a44c). Central baluster stem wrapped by a cut-crystal column; at
  the top of the stem a spray ("fountain") of thin brass wires each ending in a crystal drop; bottom
  finial a faceted crystal ball with a long teardrop.
- **12 lights in two tiers** (best count from f_0709–0715): 8 long S-scroll arms springing from the
  bottom hub, sweeping out and up to radius 0.40; 4 shorter arms to radius 0.22 set ~0.12 higher,
  between alternate long arms.
- Each light: cut-glass **bobeche dish** (0.11 dia, star-cut) with 6 faceted spear drops (60 mm) hanging
  from its rim, a white candle tube, and a clip-on **fabric shade**: bell/empire shape with six panels,
  top 0.07, bottom 0.15, height 0.13, **scalloped lower edge**, ivory fabric (est #f0e6cf, glowing
  #fff3d6 when lit) with **gold braid** at top and bottom.
- Strings of 10 mm crystal beads swag from arm to arm (two tiers of swags); a large teardrop (50 mm)
  hangs under each long arm.

### 7.2 Wall lights (2) — E wall alcoves, between each window and the breast
- Positions: y **1.23** and y **3.27**, backplate centre z **1.80**.
- Twin-arm polished-brass bracket, 0.36 wide x 0.33 high overall, projecting 0.16: oval backplate 0.07 x
  0.12 with a small urn finial above; two S-curved arms each ending in a round drip pan (55 mm) and a
  cream candle tube 0.08 high; clip-on shades like the chandelier's (ivory, scalloped edge, gold braid,
  bottom 0.13, height 0.12), shade tops at z ~2.10. Lit.

### 7.3 Downlights
Recessed white-bezel LED downlights, 85 mm, flush. Best reconstruction is **8** on a 3 x 3 grid with the
centre left free for the rose: x in {0.65, 1.89, 3.12}, y in {0.65, 2.25, 3.85}, omitting (1.89, 2.25).
Seen: SE and S-centre (f_0611–0615, f_0633), SW/W (f_0617–0621, F_719), N row (f_0689–0702), E (f_0704).

## 8. Declutter list (deliberately excluded)
- Grey plush multi-level cat tree and cat beds (NW corner), two steel pet
  bowls (SE corner floor), pet water fountain and its cable (floor by the south alcove socket), cats.
- White bladeless fan/heater standing on the hearth; small white air freshener / gadgets on the floor by
  the citrus pot; two grey door mats at the French doors.
- Everything on the table: portable gas stove, cruet set on a brass stand, black cat ornament, tissue box,
  remote controls, leather desk mats, papers, small bottles, cardboard box.
- Christmas garland, baubles and poinsettias on the mantel; fairy lights seen through the windows.
- Wedding portrait content and the signatures on its mount (privacy) — frame kept, picture replaced.
- Thermostat, alarm PIR sensor, sensor bar beside the TV, blind cords, door-stop cable clips.
- The camera operator's reflection in the mirror and TV.

## 9. Reference frames (for matching review renders)
Camera positions are room-local (x, y), eye height ~1.45, ultrawide (~105 deg vertical in portrait).

| frame | shows | camera stands / looks |
|---|---|---|
| f_0574 | first lit view: table, chairs, fireplace, French doors, chandelier + rose | in the doorway (0.6, 0.3), looking north-east |
| f_0589 | table from its south end, east wall with portrait, north wall | (1.5, 0.5), looking north-north-east, slightly down |
| f_0613 | S wall: TV, sword board, small shields, switch, door surround, SE window head | (2.7, 2.2), looking south-west, tilted up |
| f_0636 | south-alcove window surround, sill, apron, wall light, cornice enrichment, breast return | (2.4, 1.3), looking east, close |
| f_0643 | fireplace surround, insert, tiles, hearth, mantel ornaments | (2.6, 1.2), looking north-east and down |
| f_0675 | whole E wall elevation: both windows, both wall lights, breast, portrait, mantel | (0.9, 2.5), looking due east across the table |
| f_0681 | N wall west half: side window in dark reveal, post, curtain + tassel, French doors, pelmet + cornice | (1.6, 3.3), looking north-west, tilted up |
| f_0705 | whole room looking north: table length, N wall, curtains, W wall plaques, chandelier | (2.2, 0.4), looking north |
| f_0714 | chandelier and ceiling rose from below, W wall mirror and plaques behind | (2.6, 2.0), looking west and steeply up |
| f_0720 | W wall: door leaf, panel A, triptych mirror, panel B, both plaque rows, dado, skirting | (2.05, 0.8), looking west-north-west |
| f_0741 | S wall west end: door surround + open leaf, five shields over the door, hall beyond | (1.5, 2.2), looking south |

## 10. Uncertainties (best guess already used above)
1. **Room length.** Measured 4.50 (range 4.3–4.7) on both long walls independently; layout.md has 5.22
   (its own range 4.8–5.8). W wall: perpendicular foot of the camera in F_719 falls at the door-leaf edge,
   wall runs 3.6 m beyond it to the NW corner. E wall (F_672): window + 0.42 + breast 1.62 + 0.42 + window
   plus two 0.30 corner gaps = 4.50. If 5.22 is kept the corner gaps become ~0.65 and the table has ~1.25
   clear at each end, which does not match f_0613 (S end chair ~0.45 from the wall).
2. **Ceiling height** 2.80 (2.70–2.82 from the door in F_741; a socket-plate scale suggests ~2.6).
   All heights scale with it.
3. **N wall symmetry.** Modelled symmetric per the narration and layout.md. In F_705 the French doors
   measure ~0.19 west of the midpoint between the two side windows (west pier ~0.3, east pier ~0.7);
   curtains hide both piers so this cannot be confirmed. Side-window sill 1.10 could be up to 1.25.
4. **Width of the French doors**: 1.19 by proportion (leaf 0.535 x 1.95); layout.md says 1.50.
5. **Chimney-breast depth** 0.18 (range 0.12–0.28) and whether the flue is real; no chimney breast is
   listed in layout.md.
6. **Table**: total length 2.74 (range 2.6–3.1), main/leaf split, 8 mm leaf step; frieze carving and leg
   carving seen only obliquely.
7. **Side-chair legs**: straight square legs with H-stretcher is the best reading (f_0587, f_0599); they
   might be cabriole like the armchairs on the two end chairs.
8. **Chandelier**: 12 lights (8 + 4) is a best count; could be 10 or 15. Rose leaf count ~36.
9. **Downlights**: count and grid (8 assumed) — never all seen in one frame.
10. **Dado-zone finish**: reads as a dark textured wallcovering rather than paint; exact material unknown.
11. **Plaques**: counts are from F_719/f_0741 (+/-1 on the W top row behind the door leaf); individual
    crests are not catalogued.
12. **Hall door width**: now 0.838 (verification round; it measured 0.83 by proportion in F_741 and
    0.82–0.88 in three further stills). The other internal doors stay 0.762.
13. **W-wall single socket** behind the cat tree, and the door swing of the French doors (outward
    assumed).
14. **Hearth depth** 0.50 and tile count (5 per side) from oblique views only.

---

## Reconciled dimensions (from `spec/house.json`, see `spec/RECONCILE.md` D12 and "Verification round")
- Global rectangle: x -0.65..3.10, y 12.36..16.86 (**3.75 x 4.50**; this spec had 3.775 x 4.50). Ceiling 2.80.
  The length, the chimney breast and the plan-symmetric French doors are adopted as specified here.
- The east wall is the same flank wall as the utility's (inner face x 3.10, 0.20 thick).
- Local to global: Y = y + 12.36. For X keep each item's gap to the wall it is keyed to:
  W-wall and S-wall items (door, switch, TV, plaques) x - 0.65; E-wall items (windows, breast,
  fireplace, wall lights) x - 0.675; N-wall group and centre items (French doors, side windows, rose,
  chandelier, table) x - 0.6625.
- Hall door: 0.838 wide, centre (-0.056, 12.295), clear x -0.475..0.363. TV x 0.86..2.75 (0.35 from
  the east wall); 3-gang switch x 0.67.
- East windows at y 13.02 and 16.20. Chimney breast x 2.92..3.10, y 13.80..15.42, fireplace centred
  y 14.61. French doors centred x 1.225; side windows at x -0.09 (short, z 1.10..2.23) and 2.54
  (tall, z 0.30..2.20).

## Round 3 corrections (core owner, from build/rooms2_open.md)
- 6.2 Curtain centres x 0.41 / 2.0625 on the D1 piers; the closed pair covers only the French-door recess, x 0.28..2.195.
- 6.5 Mantel shelf at 1.21 (the surround stands on the 20 mm hearth).
- 6.3 Monstera: about 0.50 wide x 0.58 high above the sill board, about 12 leaves 0.11-0.15 across, kept inside the
  window surround (v2 f_0061, v1 f_0675).
- The boxed pelmet projects 0.18 (ground_corrections D5; lib mouldings).
- d_french leaves open 100 degrees (garden.md 10).

## Round 3 re-fit (21 Nov, dining unit; supersedes the heights above where they differ)
Shell: west face x -0.59 (+0.06), ceiling 2.62, cornice lower edge 2.53 (dimsG-01/02), N openings on the axis x 1.255
(windows -0.51..0.14 and 2.37..3.02, French doors 0.66..1.85; piers 0.14..0.66 and 1.85..2.37, centres 0.40 / 2.11).

**Why the heights changed.** The heights in sections 2-7 were scaled from the hall door without a vertical vanishing
point and came out too high toward the cornice (2.65 read for 2.53). Round 3 re-measured every wall piece column by
column between the dado rail bottom (1.003, top 1.047; dims_G 8) and the 2.53 cornice edge, in frames where the camera
is level (horizontal vanishing lines meet near the image centre), plus a 1D cross-ratio along the wall for positions.
The 16:9 TV corners in F_613 calibrate the lens: f = 1000-1100 px on a 1080 x 1920 still (vertical FOV about 85 deg,
not 105). Widths along the walls from the earlier method hold (mirror and panel aspects at f 1050 agree with them).

| item | was | round 3 | evidence |
|---|---|---|---|
| W-wall plaques, top row | centre 2.50 | **2.40** (2.30-2.51), 0.15 x 0.19 | v1 t719 cols 185 / 255: rail bottom 1199-1216 px, cornice 390-419 px |
| W-wall plaques, lower row | 2.27 | **2.18** (2.09-2.28), rows 0.22 apart | same |
| carved panels A / B | 0.44 x 0.88, z 1.26-2.14 | **0.42 x 0.77, z 1.29-2.06** | t719 col 210 (panel 651-1057 px, 530 px/m); aspect 0.52 from the f_0724 / f_0739 quads at f 700 (720 px frames) |
| mirror | one frame, 2 mullions, 1.47 x 0.85, z 1.26-2.11 | **three framed mirrors edge to edge** 0.385 + 0.68 + 0.385 = 1.45 x 0.79, z 1.26-2.05 | t719 col 600 (745-1032 px); t724 quad W/H 1.81 at f 1050; junctions at 27 % / 75 % of the width; t739 shows the two inner members meeting in a V |
| S-wall shields over the door | x -0.43 .. 0.69 (0.28), z 2.50 | **door centre -0.056 + 0.265 k, k -1..3; z 2.37** (2.27-2.47), 0.15 x 0.19 | dims_G verify (v2 t27.0); f_0741 (frontal, 317 px/m); F_613 cross-ratio 0.52 / 0.78 |
| three small shields | x 2.33 / 2.61 / 2.89, z 2.50 | **2.335 / 2.59 / 2.845, z 2.35** | F_613 cross-ratio |
| sword board | 1.24 x 0.22, ogee-pointed ends, x 1.02-2.26, z 2.32-2.54 | **1.14 x 0.22, square ends, bevelled edge, x 1.10-2.24, z 2.24-2.46**; sword X 1.19 (tip) .. 2.22 (pommel), scabbard 0.92 long, hooks at board-local -0.27 / +0.15 | F_613 close-up (rectangular board); cross-ratio along the S wall (SE corner 3.10, door architrave 0.448, switch 0.64, TV west edge 0.89; residuals < 1 px); rail / cornice scale in its column |
| TV | 1.89 x 1.08, x 0.86-2.75, z 1.15-2.23 | **1.81 x 1.02 (82 in, 16:9), x 0.89-2.70, z 1.13-2.15** | east edge 2.695 by the same cross-ratio; top 2.15-2.17 (F_613 cols 630 / 745) |
| 3-gang switch | (0.67, 1.30) | **(0.64, 1.35)** | dims_G 9 |
| picture over the mantel | 0.61 x 0.85, z 1.54-2.39 | **0.60 x 0.81, z 1.575-2.385** (fixer: was 0.58 x 0.77 at 1.63-2.40, a 5 cm gap over the clock) | v1 t674: the clock finial (top 1.58) overlaps the frame bottom (938 px); 284 px/m between the breast cornice (2.53, 667 px) and the frame bottom; frame 171 x 230 px (aspect 1.345); candelabrum finials 0.675 of the frame height down from its top (model 1.81 -> 1.82 projected on the breast) |
| wall lights | backplate centre 1.80 | **1.75** (shade tops 2.05) | v1 t674: body centre 898 px, shade tops 817 px, alcove-wall scale 281 px/m |
| chandelier | lowest crystal 0.79 under the ceiling (1.83) | **0.68 under (1.94)**: hub 0.45 below the cup, crystal column shortened | v1 t704: cup top 433 px, lowest drop 750 px, 398 px across the outer shades (0.80) -> 0.64-0.66; tiers (shade tops 0.10 / 0.23 under the cup, hub 0.45) match the model's shape |
| curtains | piers 0.41 / 2.0625, headings 2.50 | **piers 0.40 / 2.11**; headings hang from the pelmet underside; closed pair 0.27..2.24 meeting on x 1.255, folds 65 mm deep (y 16.724..16.801, under the pelmet face 16.68) | shell |
| table top colour | map median #362C22 | **#4E4232** (map x 1.44 / 1.5 / 1.5 in sRGB; grain, rubbed patches and roughness map kept) | rendered top against the frames at matching wall exposure: entry 124,102,76 vs f_0574 123,100,78; east 140 vs f_0675 130 (wall 182 vs 172); table cam 136 vs f_0608 157 (lit part); north 129 vs f_0705 94 (the gloss there picks up the ceiling) |
| citrus | pot (2.62, 16.62), dense round head 1.12-1.81 | **(2.695, 16.62)**, centred on the widened NE recess; open head 0.87-1.84 of 560 larger leaves (98 mm), kept out of the E-window surround and the recess architraves | v2 f_0067 |
| downlights | x -0.0125 / 1.2275 / 2.4575 | **1.255 +/- 1.24** | room centre |
| door stop | x -0.63 (in the wall) | from the skirting face (-0.57) to the parked leaf's wall face (-0.474) | joinery leaf |

Not changed, but measured: the E-window aedicule caps stand **2.34-2.39** high in v1 t674 (cornice 679 px, cap top
719.5 px, rail bottom 1108 px; 2.34 with the cap 0.14 nearer than the wall), 0.14-0.19 under the cornice; the model has
2.45 (joinery; requested). The room length 4.50 was not re-measured. The skirting is built 0.18 high since the round-3
follow-up (dims_G; the door stop at 0.074..0.106 and the sockets from 0.287 stay clear of it).
- Round-3 whole-house check: `mo.ROSE_AT['dining']` is now (1.255, 14.61), the room centre on the French-door axis; rose, chandelier, table and chairs moved 0.03 east with it.

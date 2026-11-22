# Phase 3 survey — floor2_b: the two second-floor office rooms

Units: `study` (rear room, named **Rose Room**) and `loft_office` (front room under the roof, named **Slate Room**).
Footage read: v13 f_0120–f_0225 (all frames), v4 f_0536–f_0544 and the stills of f_0440–f_0570, v5 f_0166–f_0262 (all
frames), and for the state of the front room on 21 Nov the two contact sheets of v12 plus v12 f_0003 / f_0043.
Full-resolution stills, gridded crops and the measuring scripts are in `reference/work/r3_floor2_b/` and
`build/r3/floor2_b/` (`manh.py` = Manhattan-frame plane metrology, `rect.py`, `grid.py`, `calib_f.py`). Previews of the
present model: `build/preview/study_*_r3floor2b.jpg`, `build/preview/loft_office_*_r3floor2b.jpg`.

Still names below: `t127` = v13 at 127 s (= frame f_0128); `v4-443` = the existing still `hr_v4_443.jpg` (v4 f_0444).

## 0. Which room is which in v13

| v13 frames | shows |
|---|---|
| 120–124 | `bathroom2` (shower, basin, towel rail, door) |
| 125–126 | hallway outside the bathroom and the study door |
| **127–206** | **`study` only** (rear room): door, neck, W wall with TV, N wall with a/c + radiator + window, desks, settee, corner cabinet, bean bag |
| 207–225 | out of / straight down from the `study` window: rear wall, balcony, garden, shed roof, outrigger roof |

**The front room (`loft_office`) does not appear in v13 at all.** Its state on 21 Nov is only seen in v12 (eaves video:
frames 1–7, 37–43, 71–75): unchanged from v5.

Evidence that 127–225 is the rear room: flat ceiling with cornice (the front room has slopes and no cornice); the window
is a vertical two-light casement in the rear wall looking down on the balcony, deck, lawn with the square fire pit and
the shed (f_0197–f_0225) — the front room has only a roof window; the door is at the end of the hallway past the arch.

### Names against colours (needs the owner)
The footage of 19 and 21 Nov shows:
- `study` (rear, named **Slate** Room): its feature wall (W) is **dusty rose pink**; the other walls are soft white.
  No grey / slate surface anywhere in the room.
- `loft_office` (front, named **Rose** Room): its gable wall (E) is **dark blue-grey / slate**; everything else is
  white. No pink surface anywhere in the room.

So by wall colour the two names read swapped against the ids. The present model already has the pink wall in `study` and
the dark wall in `loft_office`, as filmed. Nothing in the footage settles whether the owner intends the names as given
(names need not follow the wall colour) or meant them the other way round. I describe each room as filmed; **no repaint
is proposed.**

## 1. `study` (Rose Room) as filmed on 21 Nov

### 1.1 Surfaces (sampled sRGB → estimate under neutral light)

White references in the same frames: ceiling #D6D6CB (t147), #AFABA1 (t193.4); N wall #CFCCBB; drawer unit #CCCABD.

| surface | sampled (frame) | true estimate | present model | verdict |
|---|---|---|---|---|
| W wall (feature) | #C2B5A4, #AA9986 (t147), #B8A498 (t142), #917767, #998479 (t193.4), #978777 (t166), #A69BA0 (t127) | **#C6ABA3** dusty rose, matt. Ratio to the white surfaces of each frame averages (0.86, 0.77, 0.74). v13 reads warmer than v4 (#BC9D99 there) | `#BCA3A5` | same paint; at most a touch lighter / warmer. No change needed |
| N, E, S walls, door wall | #E2DFD9 (E, t160), #E1DDD6 / #E0DBCC (S, t160 / t133), #CFCCBB (N, t147) | **#F0EDE6** soft white, no visible blush | `#EEE6DC` | slightly less yellow; optional |
| neck E wall | #9F9276 (t133), #958471 (t127), #ACA592 (t134.5) | reads beige because it faces away from the window and takes the bounce of the oak door leaf opposite; taken as the same soft white | same | unverified (see open questions) |
| ceiling, cornice | #D6D2C6, #D6D6CB; cornice #E5E7DC | #F4F3EE | same | ok |
| carpet | #C6C6C7 (t152), #D4D4D1 (t142), #CFCFD1 (t166), #BFBDB6, #969492 (shade) | **#C6C4C0** pale silver-grey plush (saxony), neutral — not beige | `carpet_pale` #B9B4AB | a little lighter and more neutral |
| curtains | #D2D3CD (t193.4), #B3B2AA (t166) | **#CECDC7** pale silver-grey jacquard with a large tone-on-tone leaf / flower relief | `#BBB8B4` plain | lighter; pattern missing |
| settee velvet | #592D2E, #552B2C | #6A2A2E burgundy; gimp #C9A94E | #5A2226 | ok |
| bean bag | #A86475 (t152), #BB8895 (t166, lit) | **#B36A7C** dusty raspberry pink, matt woven nylon | not modelled | add |
| oak door / board | #897251 (shade) / glare | #B8915A / #B48A58 | same | ok |
| bookcase | #533B29 (top, reflections), #39312F | #3F241A | #3A1F18 | ok |
| corner cabinet | #7F6946 | #A98A56 | #B08A4E | ok |
| outside render (rear wall) | #DDD7B6 (t214, sun) | pale primrose / cream | envelope | for the envelope unit |

### 1.2 Inventory — what the model lacks or has wrong

World frame; z = above the room floor (6.02). y values on the W wall are tied to the N wall face (16.86).

| # | item | footage | present model | frames |
|---|---|---|---|---|
| 1 | **Window size** | frame ≈ **1.58 wide**, x 0.47…2.05, ≈ 1.50 high (sill board top 0.68, head ≈ 2.18). The curtains hide both jambs in every earlier interior frame; 1.10 of glass shows between them | 1.00 × 1.40 | t194.4, t203–t208, v2 t210 |
| 2 | **Lower sashes** | both are **top-hung**, opening outward ≈ 35° from the transom; friction stays on the jambs; brass espagnolette handle at the **middle of the bottom rail**; small steel lock keeps on the bottom frame member (two per light) | side-hung on the outer jambs | t203, t204, t206, t207, t208 |
| 3 | Fanlights | top-hung, brass handles on their bottom rails (shut on 21 Nov, ajar on 19 Nov from outside) | ok | t206, v2 t210 |
| 4 | Reveals and board | square plastered reveals **0.24 deep**, white; oak board 0.24 deep + 25 mm rounded nose, full width of the opening, ends housed into the reveals; wall below the board plain down to the skirting | reveal 0.19 (from extReveal 0.24) | t194.4, t206 |
| 5 | Curtain pole | wood, ball finials, **≈ 1.88 long**, x 0.27…2.15, z 2.30, eyelet heading; stacks ≈ 0.30 wide cover the jambs; tie-backs = pale-gold rope with a 0.2 long tassel at z ≈ 0.95, on hooks outside the reveals | 1.72 long | v4-563, t193.4, t208 |
| 6 | **Radiator** | **7** round-topped oval tubes (not 8), **0.49–0.51 wide × 1.75–1.80 high**, x −0.30…0.19, bottom 0.21 above the floor, 0.09 off the wall; two small top brackets; chrome valves at both bottom ends | 8 tubes, 0.44 wide | t148, v4-443, v4-445 |
| 7 | **A/C indoor unit** | **0.80 wide** × 0.30 high × 0.22 deep, x −0.62…0.18, z 2.10…2.40, top just under the cornice, left end 30 mm from the W wall; louvre flap along the bottom front, round sensor eye at the lower right | 0.90 wide | t147, t148, t193.4 |
| 8 | **Wall TV** | **55-inch class: 1.23 × 0.71** (aspect 1.73), y 14.83…16.06, z 1.23…1.94, on a flat bracket (two small hooks show under the bottom edge), thin bezel, screen blank | 65-inch 1.45 × 0.83, y 14.625…16.075, z 1.14…1.97 | v4-509, t193.4 |
| 9 | Rooster shadow box | **0.34 × 0.58**, y 16.25…16.59, z 1.25…1.83, rustic gilt-wood box frame ≈ 45 mm wide, ≈ 60 mm deep | 0.42 × 0.58 | t193.4, t147 |
| 10 | Cottage painting (W1) | 0.70 × 0.58, centre z 1.61, right edge 0.15 S of the TV: y 13.98…14.68 | 0.69 × 0.62, y 14.15 centre | v4-509 |
| 11 | Goose trophy | centre z 2.23, 0.34 S of the TV's S edge (y ≈ 14.49) | y 14.62 | v4-509, f_0146 |
| 12 | Antler skull plaque | plaque bottom 2.05, antler tips 2.38, centre y ≈ 15.42 (60 mm S of the TV centre) | ok (15.40) | t193.4, v4-509 |
| 13 | Three small frames under the TV | S: flat black frame with gold slip 0.17 × 0.17, y 15.08…15.25, z 0.98…1.15; middle: ornate gold frame, burgundy mount 0.30 × 0.34, y 15.33…15.63, top z 1.18; N: stepped bronze frame 0.18 × 0.18, y 15.71…15.89, z 0.97…1.15 | centres 15.02 / 15.30 / 15.60 | t142, t193.4 |
| 14 | Glazed bookcase | 1.02 wide, y 15.00…16.02 (0.16 N of the model), **0.90 high** (0.88–0.94 by two frames), two glazed doors (one pane each), brass catch at the meeting stiles, plinth, moulded top | y 14.84…15.86, 0.83 high | t142, t193.4, v4-509 |
| 15 | Drawer pedestal | white, castors, top ≈ 0.72, N of the bookcase in front of the radiator, drawer fronts facing S: three shallow + one deep | ok | t142, t148 |
| 16 | **Desk A** | 1.60 × 0.80 white top, generously rounded corners (r ≈ 80 mm), white two-leg electric frame, T-feet, black control strip under the N-E front edge (up/down, four presets). **Its S end stands 0.15–0.20 from the S wall** (t170, t176), not 0.60: y ≈ 14.32…15.92, x ≈ 1.55…2.35 | y 14.75…16.35 | t170, t176, t164 |
| 17 | **Desk B** | white sit-stand table ≈ 1.20 × 0.70 on T-feet with castors, long axis E–W, W leg at x ≈ 0.50 with its foot from y 15.16 to 15.69; top y ≈ 15.08…15.78, x ≈ 0.35…1.55, butting desk A's W edge in its N half (an L) | y 15.50…16.20 | v4-443, v4-445, t128, t129 |
| 18 | On desk A | S end: 34-inch curved ultrawide on a black V-foot, on a bentwood riser, facing NE; N end: 32-inch flat monitor with silver edge and T-foot on a second riser, facing SE; dark full-size keyboard (0.43 × 0.13), mouse on a brown leather mat; black gooseneck ring lamp at the NW corner. Screens blank | present, blocky | t171–t177 |
| 19 | Office chair | black fabric bucket chair with winged, ribbed back, red contrast stitching, flip-up padded arms, black five-star base; at ≈ (2.75, 15.2) facing W | present, low-poly | t160 |
| 20 | Kneeling chair | bentwood rocker, dark grey seat and knee pads, at ≈ (0.85, 14.75) | present | t129 |
| 21 | Settee | against the S wall with its W arm at the neck corner (x 0.38…1.43) | ok | t129–t137 |
| 22 | Corner cabinet | as modelled; ornaments: pale turned bowl on top, white owl (top shelf), kestrel (middle); small pewter knob at the left of the door | ok | t160, f_0180–f_0183 |
| 23 | **Bean bag** | lounger-shaped, dusty raspberry pink, in the NE corner: back against the E wall, seat toward W; footprint x 2.20…3.05, y 16.05…16.80, 0.55 high at the back, 0.25 at the front, carry loop at the top | omitted | t152, f_0151–f_0158, t166 |
| 24 | Plant | terracotta pot Ø 0.30 on a saucer, staked shrub with glossy round leaves to 1.05; on 21 Nov at ≈ (1.00, 16.45), between desk B and the window | present | t152, t166, t194.4 |
| 25 | E wall plates | single white plate at z ≈ 1.05, y ≈ 14.95 (just N of the cabinet) **and** a double socket at z ≈ 0.35, y ≈ 15.25 | only the upper plate | t160 |
| 26 | S wall plate | white double socket just W of the corner cabinet, z ≈ 0.25, x ≈ 2.35 | none | f_0178 |
| 27 | Dimmer and remote cradle | neck E wall: dimmer plate (86 mm, round knob) **0.34 N of the door-wall face**, cradle 0.12 further N; z ≈ 1.30–1.40 | 0.78 N of the door wall | t127, f_0134–f_0135 |
| 28 | **Downlights** | six, in a **3 × 2 grid over the main room**: columns x ≈ 0.05 / 1.25 / 2.50, rows y ≈ 14.75 and 16.10 (in-row spacing 1.27, row spacing 1.35–1.47); none proven in the neck | 1 neck + 3 + 2 | v4-565, v4-563, t193.4 |
| 29 | Cornice | not a plain cove: small stepped ogee — fillet, cyma, bead, fillet — bottom edge at 2.46, drop ≈ 0.10, projection ≈ 0.10; runs behind the a/c | plain cove 0.12 | t147, t193.4 |
| 30 | Skirting | 0.17 high (door-leaf scale), torus / ogee top | ok | v4-509, t170 |
| 31 | N wall, E of the window | framed certificate over a frameless whiteboard with a pen clip — **both blank** | ok | t128 |
| 32 | Door | oak 4-panel leaf (two tall panels over two short), scroll lever on a brass backplate, three brass butts, hinged W, parks ≈ 95° open with its free edge ≈ 0.09 off the W wall; brass threshold strip; white ogee architrave | ok | t127, v4-443 |

Left out as clutter: yoga mat roll, gift bags and boxes, games console, framed photographs and the document on the
bookcase top, tissue boxes, jigsaw and craft trays, microphone, floor exerciser, foot massager, soft toys, yoga blocks
box on the window board, cables.

### 1.3 Dimensions

Method: pinhole model of the stabilised ultrawide video, principal point at the centre. Focal length from 17
well-conditioned Manhattan fits over v13: **f = 852 ± 10 px** at 1080 px width (median 855, sd 24; v4: 834 ± 12, n = 10).
Each frame's room axes come from LSD line segments (RANSAC); points are then intersected with a wall or floor plane and
scaled by a reference **in that plane**. References: door leaf 1981 high; a/c unit 0.80 wide (cross-check only);
radiator 1.74–1.80 high (derived, see below); 86 mm plates.

| item | house.json | present | measured | method / frames | conf. |
|---|---|---|---|---|---|
| **Neck length** (door wall face → corner of the main room) | `rooms.study` polygon y 13.04…14.15 | 1.11 | **0.82 ± 0.05** | t127: threshold → corner = 1.154 × plan length of the parked leaf (0.686) = 0.79–0.80; v4-443: hinge axis → corner 0.82–0.84. In both frames the corner is only 0.11–0.13 beyond the leaf's free edge | high for the length |
| Main room depth (corner → N wall) | y 14.15…16.86 | 2.71 | 2.72 ± 0.10 | v4-443 floor projection 2.55–2.64 (radiator 1.74–1.80), first pass 2.77; chain leaf edge → bookcase 1.04–1.12 (v4-443, v4-509) + bookcase → N wall 1.63–1.86 (v4-443, v4-445, t193.4) − 0.12 | medium; no change |
| Door wall → N wall | 13.04…16.86 | 3.82 | **3.55 ± 0.11** | floor projection 3.38–3.61; W-wall chain (leaf 0.70 + 1.02…1.12 + bookcase / TV → N wall) 3.63–3.75 | medium |
| Neck width | x −0.65…0.30 | 0.95 | 0.90–1.00 | v4-443, t127 | ok |
| Room width | x −0.65…3.10 | 3.75 | 3.85–4.2 ? | N-wall chain in v4-563 (blurred; the NE corner cannot be placed better than ± 0.15) | low; not settled |
| Ceiling | `ceilingZ` 8.62 | 2.60 | 2.55 ± 0.05 | door leaf in the W-wall plane (v4-509): cornice bottom 2.46, ceiling 2.53–2.57 (pitch ± 2°, f 830–870); TV scale (t193.4) 2.49; radiator scale 2.55–2.68 if it is 1.74–1.80 | no change (inside tolerance) |
| Skirting | shell | 0.17 | 0.17 | v4-509, t193.4 | ok |
| **Window width** | `openings.w_study.width` | 1.00 | **1.58 ± 0.08** | (a) v2 t210 from the garden, wall-plane: frame / French-door leaf pair = 1.35 → 1.61 with the pair at 1.19; frame / rendered wall width 0.386 → 1.52–1.62. (b) t206: board depth = 0.30 × (W reveal → mullion centre); board 0.24 deep → 1.6. (c) pole 1.86–1.92. (d) t194.4 and t208 show the reveals beyond the curtains | high |
| Window centre | `center` x | 1.26 | 1.28–1.34 (inside), 1.16–1.29 (outside) | v4-563 mullion from the NW corner; v2 t210 against the French doors | keep 1.26 |
| Sill (board top) | `sill` | 0.68 | 0.58–0.70 | v4-445 0.68, v4-563 0.58, outside 0.64–0.70 | keep |
| **Window head** | `height` 1.40 → head 2.08 | 2.08 | **2.18 ± 0.07** | v4-445 and v4-563: frame top 2.10–2.18 after correcting for the 0.24 set-back; outside (door leaf 1.97 scale) 2.23–2.31 | medium-low |
| Transom | `transomBar` | 1.75 | 1.71–1.79 | v4-445, v4-563; outside 1.70 | keep |
| **Interior reveal** | `extReveal` 0.24 in a 0.50 wall → 0.19 inside | 0.19 | **0.24 ± 0.03** | t206: two 102 mm blocks plus their box span the board; t194.4 | medium |
| Lower sashes | `sashes` | side-hung | **top-hung** | t203–t208 | high |
| Door leaf | `d_study.width` | 0.686 | 0.69–0.72 | plan length of the leaf in v4-443; threshold strip = 1.04 × leaf in t127; a 762 leaf would need a 1.09 neck | keep |
| Door position | `center` x −0.175 | — | hinge line 0.10–0.20 from the W wall, E lining ≈ 0.03 from the neck E wall | t127 (W wall line weak) | keep |
| Radiator | room module | 0.44 × 1.80, 8 tubes | 0.49–0.51 × 1.75–1.80, 7 tubes | H/W = 3.48 in v4-443, 3.55 in v4-445 (top width); count in t148 and v4-445 | high (count), medium (size) |
| A/C | room module | 0.90 | 0.80–0.84 | v4-443, v4-445, v4-563 | medium |
| TV | room module | 1.45 × 0.83 | 1.23 × 0.71 | door-leaf scale in v4-509 | high |

**Knock-on of the short neck.** Interior total 3.55 ± 0.11 against 3.82. With the rear wall face kept at 16.86 (it
stacks on the ground floor; f_0213–f_0218 show one flush rendered face from the window sill down to the balcony doors)
and the main room's S wall kept at 14.15 (2.72 measured against 2.71), **the door wall is 0.28 further north than
modelled**: inner face y 13.32, hall face 13.22. The hallway (`landing2_head`) gives way by growing 0.28 north; the
hall partition `w_hall_bath2` and the party-wall segments follow. The other reading — door wall kept, the main room's
S wall 0.28 further south — makes the main room 3.0 deep, outside what the floor projection and the W-wall chain allow,
though it would remove most of the "unseen zone" between `bathroom2` and the study (RECONCILE2 P4). The hall survey of
this round has to say how far the study door is from the arch and the bathroom door.

**Rear wall thickness.** Interior reveal 0.24 + frame 0.07 + an exterior reveal that looks shallow from the garden
(0.05–0.15, v2 t210) gives 0.36–0.46, not 0.50. If the outer face is right, the room could be up to 0.1 deeper to the
north; not settled from inside.

## 2. `loft_office` (Slate Room)

Not in v13. v12 (21 Nov) shows it as in v5: white knee walls, slopes and W wall, dark blue-grey E gable wall
(#474D53 / #34383B sampled in v5, true ≈ #3B4046), pale silver carpet, both flags and the framed pictures still on the W
wall, built-in cabinet, exercise bike in front of the rear knee wall, bookcase and wire-basket trolley by the front knee
wall. No change of furniture between 19 and 21 Nov worth modelling.

### 2.1 Model against footage
- The model's inventory matches v5 (cabinet with four card-holder drawers, a/c, poster, certificates blank, TV wall with
  medal rail and cat pictures, stool, desk, chair, bookcase, coffee table, Chippendale chair, ensign, Union flag, radiator).
- Lower level of detail than a visitor would expect: the **mesh office chair** (white shell, grey mesh back with
  headrest, flip-up arms, polished five-star base — v5 f_0233–f_0244) is a blocky stand-in; the 49-inch curved monitor
  reads as a flat slab; the desk lamp is a black architect lamp with a domed metal shade (f_0238), not a cone.
- Roof window (v5 f_0189–f_0200): white frame and sash below the roof plane, grey handle bar on the bottom rail, the sash
  swings out from the top; dark grey blackout blind parked across the upper quarter, white pleated blind below it. As
  modelled.
- Carpet reads the same pale silver plush as the rest of the floor (#CFC9BC in v5, neutral #C6C4C0 in v12).

### 2.2 Dimension check — ceiling pitch
The slope angle read **in the plane of a gable wall that is nearly parallel to the sensor** (so neither the focal length
nor a scale enters):

| still | wall | rear slope | front slope |
|---|---|---|---|
| v5 f_0183 (`hr_183`) | E gable, yaw 12°, pitch 1° | 37.0° | 34.9° (raw image 33.7° / 39.5°) |
| v5 t = 232.5 s (sharp) | E gable, camera pitched 17° down | 32.1° | 34.3° |
| v5 f_0346 (`hr_346`) | W wall | — | 36° |

Mean **35° ± 2.5°** against 30° ± 3° in the spec (which came from floor back-projection scaled by the cabinet). In the
same stills the a/c (0.80) gives the flat strip 0.76–0.80 wide and the rise from the rear knee to the flat 0.73 — both as
modelled — but the rear slope's run 0.97–1.10, not 1.21.

If the knee heights (0.92 / 1.42) and the apex (2.12) stand, a 35° pitch shortens the slope runs to 1.71 (front) and
1.00 (rear), so the room would be ≈ 3.5 deep between the knee walls instead of 4.05, and the roof over it steeper. I
could not check the plan depth independently from v5 (the W-wall chain in `hr_346`, scaled by the apex, puts the cabinet
front 2.71 from the front knee wall against 2.84 in the model, i.e. no large shortfall there). **Not settled**: the
eaves footage (v12, triangular voids: depth against height) and the street views (v8) decide it.

No other `loft_office` dimension was re-measured: there is no new footage of the room.

## 3. Notes per unit

**study** — see 1.2 (items 5–28) and 1.3. In short: TV 55-inch; radiator 7 tubes × 0.50; a/c 0.80; bookcase 0.90 high
and 0.16 further N; desks re-placed (A to within 0.2 of the S wall, B 0.4 further S); bean bag in the NE corner; six
downlights as a 3 × 2 grid; second E-wall socket and an S-wall socket; curtains lighter, patterned, pole 1.88; dimmer
0.34 from the door wall. Everything keyed to the door wall moves with it if the neck is shortened.

**loft_office** — better office chair, curved monitor and lamp; nothing else. Geometry waits for the pitch decision.

**shell** — `w_study` 1.58 wide with top-hung lower sashes and centred bottom-rail handles; 0.24 reveals and board;
study cornice as a small stepped ogee (drop 0.10, projection 0.10); study door wall position.

**envelope** — rear wall, second floor: window 1.58 wide in a shallow rendered reveal with a white projecting sill
(v2 t210); two **black corrugated conduits** (the a/c pipes) clipped to the render: a horizontal run ≈ 0.35 below the
sill across the whole wall and a vertical run up the W (party) side of the window to the roof edge (v2 t210, v13 f_0213–f_0218);
a small grey square unit on a bracket E of the balcony doors at first-floor head height (v13 f_0214–f_0217). Roof pitch
question from 2.2.

**stairs2** (second-floor landing) — the study door wall probably 0.28 further north; socket plate(s) on the hall E wall
below the dado just S of the study door (t127).

**bathroom2** — the wall between the bathroom and the study stays about 0.45 thick on this survey's numbers.

**eaves** — pitch question from 2.2: with 35° the voids are shallower in section for the same knee heights.

## 4. Open questions
1. Names: the room with the rose wall is `study` (named Rose Room) and the room with the slate wall is `loft_office`
   (named Slate Room). Intended, or swapped?
2. Is the study door wall 0.28 further north (hall longer), or is the main room deeper to the south? The neck is 0.82
   either way.
3. Study width: the N-wall chain suggests 3.85–4.2, the model has 3.75; the NE corner is not clear in any frame.
4. Study ceiling 2.55 (door leaf) or 2.60–2.65 (radiator, if it is a 1.78–1.80 model): the radiator's catalogue height is
   unknown.
5. Thickness of the second-floor rear wall (0.36–0.46 from the reveals against 0.50) and the window's exterior reveal.
6. Loft ceiling / roof pitch: 35° ± 2.5° here against 30°; and with it the depth of the Slate Room.
7. Whether the neck's E wall is the same soft white as the rest (it reads beige in shadow).
8. Whether there is a downlight in the neck in addition to the six of the main room.


## Verification

Measured by the verifier before reading sections 1-4 (each item was read only after my own number for it existed).
Stills: `reference/work/r3_floor2_b_v/`; scripts: `build/r3/floor2_b_v/` (`vp3.py` focal length from three vanishing
points, `cam.py` floor back-projection, `vwall.py` metric measurement on a vertical wall, `wallplane.py` plate method,
`pitch.py` slope of a line lying in a wall, `courses.py` brick-course pitch). Nothing in the model was changed and no
preview was built.

### V1. Method

Pinhole camera with fixed intrinsics per video, orientation of each frame from the nadir vanishing point (vertical
edges) plus one horizontal line; points are intersected with the floor or with a vertical wall and scaled by a known
size **in that plane**. Focal length from 61 frames of v13 with three finite vanishing points: **f = 854 px** (IQR
837-871) at 1080 px width, principal point about (570, 1020), not the centre; v5: median 895 (IQR 830-915, 24 frames), (558, 980) - 860 used, 830-900 tried. Every result
below was repeated with f +/- 20-40 px, the principal point at the centre and the vanishing points shifted; the ranges
quoted include that.

Frames of my own (different instants from the survey's): v13 t 126.7, t 134.2-134.5 (30 fps frames `p_021`-`p_031`),
t 203.5, 205.5, 206.5, 208.5, 211.5; v4 t 508.8, 509.2, 509.5, 558.6; v2 t 249 (rear elevation square-on from the shed
end of the garden, the survey used t 210 from close by); v5 t 185.0, 233.6.

### V2. What I measured

**Neck (01).** Four routes, three references:
1. v13 t 126.7, floor plane, scale = brass threshold strip between the door linings (0.69): the neck corner
   (skirting arris at the carpet) lies **0.79 north of the strip's north edge** (0.75-0.83 over all calibrations), 0.80
   east of the west lining (model 0.82: the plan comes out square). East skirting from the door architrave to the
   corner 0.70. Bottom free corner of the parked leaf 0.70-0.74: the corner is 0.05-0.09 beyond the leaf.
2. v4 t 509.2, from the far side of the room: the sight line past the neck corner leaves 0.62-0.64 of the 0.686 leaf
   visible; with the camera 2.5 from the west wall and 2.05 north of the leaf edge (same solution as route 4 below)
   the corner is **0.80 +/- 0.08** from the door wall. The present 1.11 would leave 0.21 of the leaf visible.
3. v13 `p_026`, the 86 mm dimmer plate on the neck's east wall with the corner arris and the door architrave both in
   frame: 0.78 if the plate is taken as square in the wall plane, 0.63 if the wall yaw is taken from the plate and
   remote edges. Too sensitive to settle the value; it excludes 1.11 (which needs the plate 1.23 times wider than
   tall).
4. **Door wall to north wall**, v4 t 509.5, west-wall plane, scale = the parked door leaf (1.99 floor to top, 0.08 in
   front of the wall). Along the wall from the leaf's free edge: cottage painting 0.16-0.90, TV 1.06-2.32, rooster
   frame 2.48-2.87, last pink wall visible beside the radiator **3.06** (2.93-3.22), the corner itself 0.03-0.08
   further (hidden by the radiator and the a/c). Checks inside the same solution: TV 1.26 x 0.71, aspect 1.77-1.79 (a
   55-inch set is 1.23 x 0.71), cornice line 2.50-2.55 above the floor. So the leaf edge is 3.10 from the north wall
   and **the door wall 3.80 +/- 0.09** (3.75 if the TV is forced to 1.23). The present model has 3.82; the survey's
   3.55 is the mean of its own west-wall chain (3.63-3.75) and a floor projection to a wall 4 m away scaled by a
   radiator of unknown height (from t 126.7 I get 3.9 +/- 0.3 for that distance: it carries no weight).
   The survey's inventory agrees with this, not with its proposal: painting y 13.98-14.68 and TV 14.83-16.06, tied to
   the north wall, put the painting's south edge 2.88 from the north wall; the leaf's free edge is 0.16 south of it (a
   plain strip of wall shows between them in t 509.2 and t 509.5), i.e. at 13.80-13.82, and a door wall at 13.32 would
   put the leaf edge at 14.04, **0.06 behind the painting**.

Result: neck **0.80 +/- 0.05**, total 3.80 +/- 0.09, hence main room **3.00 +/- 0.10** deep. The neck is short because
the main room's south wall is further south, not because the door wall is further north.

**Window (02, 03, 05).**
- v2 t 249, image plane parallel to the wall within 1 degree in yaw and 1.6 in pitch (roof line level, corners
  parallel): opening 149 px wide, frame 154 px high; ground-floor door set (white frame) 111.7 x 195.6 px;
  threshold to the window frame bottom 609 px; neighbour's brick 8.0 px per course. Three scales in or beside the
  wall plane: door set as a 1.19 x 2.09 frame 93.9 px/m; level difference 6.56-6.62 m 92.0-92.9 px/m; brick at 84 mm
  per course (the envelope survey's value for the old walls; the 75 mm of the brief gives 107 px/m and would make the
  door set 1.05 x 1.83 and the storeys 10 % too low) 95 px/m. **Width 1.59 +/- 0.03**, frame **1.62-1.68 high**
  outside, W / H 0.97. Centre 0.08 +/- 0.05 east of the French-door axis, i.e. x 1.30.
- v4 t 558.6, north-wall plane, scale = floor to cornice line 2.46-2.50: board front edge **0.61-0.62** above the
  floor (0.59-0.64), reveal head **2.12-2.15**, transom 1.75-1.78, pole 2.25-2.29; the soffit comes out level
  between its room edge and the frame for a reveal **0.245** deep (0.22-0.31); board from nose to frame 0.215
  (0.18-0.23). Frame width by symmetry about the mullion 1.50-1.53 (1.40-1.63 with the horizontal vanishing point
  moved); width / (head to board) = 1.02 (0.95-1.09). Opening height above the board **1.51 +/- 0.04**.
- Outside reveal: from the garden the head soffit shows about 0.04 under the render edge at a 0.53 slope (0.08 deep)
  and the sill does not hide the bottom rail; from above (v13 t 211.5) the stone sill band is about 1.5-2 frame depths
  wide. Exterior reveal about 0.08, so the real wall is about 0.39, not 0.50.

**Sashes (04).** v13 t 203.5, 205.5, 206.5, 208.5: both lower sashes hang from the transom with the bottom rail pushed
out, friction stays on the jambs, brass handle at the middle of each bottom rail, keeps on the bottom frame member.
Bottom rail roughly 0.5-0.6 out on a sash about 1.05 high: 28-35 degrees (a rough reading, not a measurement).

**Loft pitch (06).** Slope of the ceiling / gable junction lines as 3D directions in the gable plane (`pitch.py`):
v5 t 185.0 (camera level, wall square within 1-4 degrees) **rear 35.5-36.6, front 34.6-35.5**; v5 t 233.6 (pitched
18 down, wall 10-17 oblique) front 34.3-35.5, rear 31.6-33.3 (short line at the frame edge). **35.5 +/- 1.5**, as the
survey and the eaves verifier found.
The same frame t 185.0 has **both knee corners in view** (rear at x 169, front at x 1072), which neither the survey
nor the eaves verifier had. In the wall plane, roll taken out: flat : rear run : front run = 157 : 292 : 458 px (0.17 :
0.32 : 0.51), rear rise : front rise = 215 : 315, rear knee (floor at the skirting foot to the slope start) 298 px,
so rear knee / apex 0.58. Scales: apex 2.12 gives 242 px/m (then the a/c is 0.77 wide and the poster frame 0.87); a/c
0.80 gives 232; the poster as 24 x 36 in gives 225.

| | apex 2.12 | a/c 0.80 | poster 0.94 | present | proposed |
|---|---|---|---|---|---|
| flat strip | 0.65 | 0.68 | 0.70 | 0.76 | 0.76 |
| rear run | 1.21 | 1.26 | 1.30 | 1.21 | 1.00 |
| front run | 1.89 | 1.97 | 2.04 | 2.08 | 1.71 |
| between the knee corners | **3.75** | **3.91** | **4.03** | 4.05 | 3.47 |
| rear knee | 1.23 | 1.28 | 1.32 | 1.42 | 1.42 |
| apex | 2.12 | 2.21 | 2.28 | 2.12 | 2.12 |
| front knee (apex - rise) | 0.82 | 0.85 | 0.88 | 0.92 | 0.92 |

### V3. Verdicts

| id | verdict | value to use | my measurement | reason |
|---|---|---|---|---|
| floor2b-01 | **adjust** | Door wall stays: inner face y **13.04**; `w_study_door`, `d_study`, `landing2_head`, `w_hall_bath2` and the party-wall split unchanged. Move the main room's south wall instead: `rooms.study` polygon (-0.65,13.04) (0.30,13.04) (0.30,**13.84**) (3.10,**13.84**) (3.10,16.86) (-0.65,16.86), size 3.75 x 3.02, neck 0.95 x **0.80**; `w_bath2_study` centreline y 13.77, thickness 0.14 (faces 13.70 / 13.84); `w_neck_bath2` b y 13.77; `w_flank_2_bath` b and `w_flank_2_study` a y 13.77 | neck 0.80 +/- 0.05 (floor 0.79, sight line 0.80, plate 0.63-0.78); door wall to north wall 3.80 +/- 0.09; main room 3.00 +/- 0.10 | The short neck is confirmed three ways. The total is not short: the leaf-scaled west wall gives 3.80 against 3.82 present and 3.55 proposed, and a door wall at 13.32 puts the parked leaf 0.06 behind the cottage painting, which hangs 0.16 clear of it. Moving the hall end wall would also stretch the pier north of the bathroom door beyond what `floor2_a` measured with that wall fixed. |
| floor2b-02 | **accept** | width **1.58**, centre x 1.26 | 1.59 +/- 0.03 outside (v2 t 249, three scales), 1.50-1.53 between the plaster reveals inside, W / H 0.97 outside and 1.02 inside | The present 1.00 gives W / H 0.71. Fits the wall: 0.28 between the radiator and the west reveal, the 1.88 pole overlaps both sides, and the frame lines up with the balcony door set below (0.47-2.11). |
| floor2b-03 | **accept** | height **1.50** (sill 0.68, head 2.18) | 1.51 +/- 0.04 from board to head inside; the frame is 1.62-1.68 outside because it runs about 0.06 below the board and into the head | My levels are 0.62 for the board and 2.13-2.15 for the head on a 2.46-2.50 cornice line, 0.64 / 2.19 if the ceiling is 2.60; 0.68 / 2.18 is inside that. If one number moves later it should be the sill, down to 0.64. |
| floor2b-04 | **accept** | both lower sashes `top_hung`, swing out, angle about 35, handle mid bottom rail | direct, four stills of my own; angle 28-35 | No doubt about the hinge side. The 19 Nov frames that were read as side-hung show the same stays from the side. |
| floor2b-05 | **accept** | `extReveal` **0.19** | interior reveal 0.22 +/- 0.04 (head soffit 0.245, board 0.19-0.215) | Within tolerance of 0.24 inside. The outside reveal is really about 0.08; with the wall modelled 0.50 thick one side has to be wrong and the room side is the one a visitor stands next to. The wall thickness itself (about 0.39) is not part of this change. |
| floor2b-06 | **adjust** | **Rear plane only, turned about the present ridge:** `roof.planes.main_rear` pitchDeg **35**, z c0 **12.64**, cy **-0.700** (ridge y 5.00 z 9.14 kept); `rooms.loft_office` `rear_slope` c0 **12.33**, cy -0.700, south edge y **5.31** (the `flat` plane ends there for x >= 1.25); `w_knee_rear.height` **1.23**; rear knee wall stays at y 6.59. **Front plane, both knee-wall positions and the apex 2.12: no change** (no move to 2.91 / 6.38) | pitch 35.5 +/- 1.5 on both slopes; rear run 1.21-1.30, rear knee 1.23-1.32, 3.75-4.03 between the knee corners | The pitch is right; the plan consequence drawn from it is not. As proposed the rear run would be 1.00 under a 1.42 knee: I measure 1.21-1.30 under 1.23-1.32 (eaves verifier: 1.24 under 1.23), so the rear half fits the **present plan** at 35 degrees once the knee drops. The same plane lands on the head of the old rear wall (z 6.49 at y 8.79) and puts the rear eaves at 6.16, where the envelope verifier measured the gutter (6.1-6.3 against 6.65 modelled). The front half does not close: 35 degrees through the ridge with the knee wall kept at 2.54 gives a 0.62 knee and eaves at 5.97 against a gutter at 6.4-6.6 from the street; my front run 1.89-2.04 puts the knee wall at 2.6-2.8, the survey's chain at 2.67, the proposal at 2.91. That needs the street data and is left as it is. |

### V4. Knock-on consistency

- **01.** Y sum in the west strip: 13.04 + 0.80 + 3.02 = 16.86; nothing south of the door wall moves, no level or riser
  count is touched. The solid zone between `bathroom2` and the study shrinks from 0.45 to 0.14 with the bathroom as
  modelled (13.70), which answers RECONCILE2 open question 3; `bath2_niche` (0.10 deep) still fits, with 0.04 behind
  it. If `floor2_a`'s bathroom (north wall 13.40) is adopted the zone is 0.44 again and stays unexplained. Room
  module: everything on the south wall (settee, corner cabinet, south socket) and desk A go 0.31 south with the wall;
  the west-wall items keep the positions of section 1.2, which were tied to the north wall (door leaf edge 13.76,
  painting 13.92-14.66, TV 14.82-16.08, rooster 16.24-16.63 by my chain); the dimmer and cradle stay on the neck wall.
  Six downlights over a 3.02 room: rows at 14.6 and 16.1 would be symmetric (0.76 from each wall, 1.50 apart; the
  survey read 1.35-1.47 apart).
- **02 / 03.** Window 0.47-2.05 by 0.68-2.18 in a wall 3.75 wide and 2.60 high: 0.42 to the ceiling, pole at 2.27
  between head and cornice. The first-floor balcony door set (0.47-2.11) and the ground-floor French doors (axis
  1.225) stay on one axis within 0.05.
- **06.** Needs with it: `velux` z from the new plane (ceiling 8.49 at y 5.48, 7.82 at y 6.45); `h_eaves_rear` no
  taller than the 1.23 wall (the eaves verifier's eaves_loft-05: height 0.91, sill 0.15, valid only together with this
  knee height); the `eaves_rear` lining follows the plane and meets the lower floor at about y 8.5, inside the present
  polygon; `roof.eaves.rear_K` gutter about 6.15; `w_east_2c` top 7.99 already equals the new roof at y 6.64. The
  flat strip becomes 0.69 wide (4.62-5.31), which is what I measure (0.65-0.70; survey 0.76-0.80). Until the front is
  solved the roof is asymmetric (30 front, 35 rear) with the ridge where it is; the front slope stays about 5 degrees
  too shallow inside the room.

### V5. Not settled

1. **Front half of the loft section.** One reading closes everything with no wall moved: a symmetric 35 degree roof
   with the ridge at y 4.85, z 9.33, flat strip 0.70 wide at 2.28 above the floor, front knee 0.92 at 2.54, rear knee
   1.31 at 6.59, eaves 6.25 front and rear. It needs the apex 0.16 higher than round 2 measured and the poster to be
   24 x 36 in; with the apex at 2.12 the knee corners are 3.75 apart and the front knee wall would be about 0.25
   further north. The a/c unit's catalogue width (0.77 or 0.80) or a tape on the flat ceiling would decide it.
2. Front knee height: 0.82-0.88 by difference in t 185.0, at least 0.92 of white wall visible below the corner in the
   same frame, 1.07 by the eaves verifier's hatch proportions.
3. Absolute y of the study door wall: 13.00-13.16 from the leaf-scaled chain; kept at 13.04. The hall length from the
   arch to that wall was not measured here.
4. Study width (survey open question 3) and ceiling height (2.55-2.60) were not re-measured; my west-wall solution
   has the cornice line at 2.50-2.55.
5. The 86 mm plate route for the neck (0.63-0.78) would need a sharper, squarer frame than the footage has.
6. Sash opening angle to better than 28-35 degrees.

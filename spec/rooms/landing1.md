# landing1 — first-floor landings, corridor and level changes

Sources (Phase 2, daylight): **v3 f_0001–f_0078, f_0140–f_0160, f_0478–f_0510** (stairs up, quarter
landing, rear corridor, arch, two steps, front landing), **v4 f_0166–f_0200, f_0265–f_0311** (front
landing from the green bathroom door, switches, paintings, corridor), **v6 f_0012–f_0047** (walking
down). Full-resolution stills, grid crops and montages are in `reference/work/p2_first_landing/`
(`v3_f0054.jpg`, `v3_f0075.jpg`, `v6_f0026.jpg`, `v6_f0028.jpg`, `v3_f0047.jpg`, `v6_f0013.jpg` are the
key ones).

Owner narration (authoritative): "there's a landing area here, and painting 4 … this is a square angle
here, but this is 45 degree, make sure you get the shape right … sockets and radiators, paintings … this
is towards the back of the house … radiator … this is the first floor, there's a beautiful arch here,
and corners, smooth corners … spotlight … got an empty socket here … now two steps here … so this is the
middle room" (v3 00:00–01:10); "beautiful painting, and a beautiful pediment … this one controls the
hallway, hallway is now light off" (v3 02:16–02:28); "I'll turn the hallway lights back on … sockets …
now there's a two step up here … this is still on the first floor … this is towards the front of the
house … this is the green bedroom, double wooden door" (v3 08:04–08:48); "this way goes up to the second
floor and I got a lot of cat paintings … I'll turn off the hallway light, remember paintings … here I
can also turn on the second floor lights" (v4 03:02–05:10).

**Dimension confidence.** Heights of doors, dado and skirting: ±30 mm (door leaf 1981 used as the
scale). Widths across the corridor: ±60 mm. **Positions along Y: ±0.20 m** — they come from dividing
the 4.10 m between the top riser of the main flight (y 8.13, ground model) and the rear end wall
(y 12.23, the line of the dining-room south wall below) in the proportions measured in `v3_f0054` and
`v6_f0028`, with the yellow-room door set (0.92 m over architraves) as the depth scale. Levels: riser
counts are firm to ±1 riser, the riser height (0.19) to ±0.01, so floor levels are ±0.20 m absolute but
the **differences between them (1 riser, 2 risers) are certain**.

---

## 1. Shape, levels and dimensions

Room-local frame = **world frame** (metres, origin at the street-door threshold, +Y to the rear, +X to
the right walking in). Z values are world Z (ground-floor finished floor = 0).

The first floor is split-level. Three floor levels meet at the top newel of the main staircase:

| level | world Z | how it is reached | what is on it |
|---|---|---|---|
| **QL** quarter landing | **2.85** | 15 risers x 0.19 from the hall floor | top of the main flight only |
| **F1r** rear level | **3.04** | 1 riser west (left) from QL | rear corridor, yellow room, arch bay, blue bedroom |
| **F1f** front level | **3.42** | 2 risers south from F1r ("two steps up") | upper landing strip, front landing, green bedroom, green bathroom, foot of the stair to the second floor |

### 1.1 Zones (plan polygons, internal faces)

| zone | polygon / rectangle (x, y) | floor Z | ceiling Z (height) | notes |
|---|---|---|---|---|
| **QL** quarter landing | x 0.15..0.99, y 8.13..8.97 (0.84 x 0.84) | 2.85 | curved soffit 4.95..5.35 (underside of the winders of `stairs2`) | walls on E (x 0.99) and N (y 8.97); open to the main flight on the S; one riser up on the W |
| **Rear corridor, south part** | x -0.65..0.15, y 8.13..8.97 | 3.04 | 5.49 (2.45) | beside QL; its east edge is the riser down to QL |
| **Rear corridor** | x -0.65..0.25, y 8.97..11.10 (0.90 wide) | 3.04 | 5.49 (2.45) | the west wall has a pier 0.10 proud from y 8.53 to 9.95, so it is 0.80 wide there |
| **Arch wall** | y 11.10..11.45, clear opening x -0.58..0.22 | 3.04 | arch crown 5.09 (2.05) | 0.35 thick, see 3.4 |
| **Arch bay** | x -0.60..0.49, y 11.45..12.23 (1.09 x 0.78) | 3.04 | 5.49 (2.45) | blue-bedroom door in its north wall |
| **Upper strip** | x -0.65..0.15, y 6.06..7.88 (0.80 wide) | 3.42 | 5.77 (2.35) | balustrade on the east side, stairwell beyond |
| **Two steps** | x -0.65..0.15, risers at y 8.13 and y 7.88 | 3.04 → 3.23 → 3.42 | — | going 0.25, see 3.1 |
| **Front landing** | x -0.65..0.99, y 4.95..6.06 (1.64 x 1.11) | 3.42 | 5.77 (2.35) | green-bedroom door S, green-bathroom door E, first step of `stairs2` on the N side between x 0.15 and 0.99 |

Corner between QL and the corridor (the owner's "45 degree"): the QL north wall (face y 8.97) and the
corridor east wall (face x 0.25) meet in an **external corner cut by a 45-degree chamfer** from
(0.25, 9.07) to (0.35, 8.97) (face 0.14 wide, full height; dado, skirting and paint line all mitre round
it in two 135-degree turns). The QL's north-east corner (0.99, 8.97) is an ordinary square internal
corner ("this is a square angle here").

ASCII plan (not to scale; +Y up the page, +X right; `=` riser, `B` balustrade, `>`/`^` door):

```
 y
12.23 +--[ blue door ^ ]--+              blue bedroom beyond (F1r 3.04)
      | W5   ARCH BAY  sw |  x -0.60..0.49
11.45 +-+               +-+
11.10 +-+   (  arch  )  +-+  arch wall 0.35 thick, clear 0.80
      |                 |
      | W4              >  yellow-room door, clear y 10.15..10.91 (hinge N, opens E)
      | [radiator]      |
      |                 |  thermostat (y 9.72) + switch (y 9.40) on this wall
 9.95 |_                |
      | | pier 0.10     |
      | | W3 + socket   \   45-degree chamfer
 8.97 | |               +=======+-------------+ 8.97
      | |   F1r 3.04    =  QL   |  P4         |
 8.53 |_|               = 2.85  |  (stair wall x 0.99)
 8.13 |======(riser)====N=======+  <- top riser of the main flight; N = top newel (0.15, 8.13)
 7.88 |======(riser)====B   main flight below, rising toward +Y
      |                 B   (open stairwell; stairs2 climbs above it)
      | W2  UPPER STRIP B
      |     F1f 3.42    B
 6.06 |                 n-------+  n = stairs2 newel; first riser of stairs2 at y 6.06
      | W1  FRONT LANDING       >  green-bathroom door, clear y 5.13..5.89 (hinge S, opens E)
 4.95 +--[ green door v ]--sw---+
    -0.65     0.09     0.15    0.99   x
```

### 1.2 How the levels were worked out

- Main flight: 14 treads plus the landing are countable looking down from the top (`v6_t37.5.jpg`,
  crop `c_v6_t375.jpg`), 14 riser faces looking up from the foot with the top one cut by the frame
  (`c_v3_17_stairs.jpg`) → **15 risers** (14 or 16 not excluded). 15 x 0.19 = 2.85 matches the 2.60
  soffit over the ground-floor lobby (0.25 floor zone).
- One riser from QL up to the corridor: seen from above in v3:f_0043–f_0048 and from the side in
  v6:f_0028 (dark carpet edge) → F1r = 3.04.
- Two risers from the corridor to the upper strip (v3:f_0073–f_0076, f_0494–f_0501; v6:f_0026): the
  dado rail on the west wall rakes up by exactly the same amount → F1f = 3.42.
- Consequences for other specs: (a) F1r 3.04 sits 0.24 above the 2.80 dining ceiling — fine; it is only
  0.09 above the 2.95 that `house.json` gives the ground-floor **rear** corridor, so that ceiling must
  be nearer 2.75–2.80 (see section 11); (b) F1f 3.42 leaves a 0.47 floor zone over the 2.95 hall /
  living ceilings (deep joists plus a dropped ceiling for the downlights), or the risers are a little
  shallower than 0.19 — keep the riser counts and the differences whatever absolute value is adopted.

---

## 2. Openings (doors off the landings)

All four doors are the same leaf: **oak-veneer Victorian 4-panel** (two tall upper panels over two
short lower panels, raised and fielded), 1981 x 762 x 35, satin lacquer, true colour #B8915A (sampled
#887248 in shade); polished-brass lever on a rectangular brass backplate at 1.00 m; three brass butt
hinges; a **brass carpet-threshold strip** across every doorway. Architraves are white gloss, 80 mm,
ogee-moulded, on both faces unless a doorcase is described.

| id | wall | clear opening (world) | hinge / swing | doorcase on the landing side |
|---|---|---|---|---|
| `d_yellow` | corridor east wall, x 0.25..0.35 | y 10.15..10.91, head 1.98 above F1r (Z 5.02) | hinge on the **north** jamb, leaf swings **east into the yellow room** to about 100 degrees against a brass floor-level door stop on the room's north wall (v3:f_0130–f_0139) | plain architrave only, outer edges y 10.07 and 10.99, head top 2.06 |
| `d_blue` | bay north wall, face y 12.23 | x -0.44..0.32 (centred in the bay), head 1.98 above F1r | hinge on the **west** jamb, swings **north into the blue bedroom** (leaf seen inside at the left, `v3_f0054`) | **pedimented doorcase**: 90 mm architrave; plain frieze 60 mm; moulded cornice shelf 1.03 m wide (almost wall to wall) with its top at 2.14; low **triangular pediment** above it, raking mouldings, plain tympanum, apex at 2.26 above F1r. White gloss. (v3:f_0147–f_0149; "a beautiful pediment") |
| `d_green` | front-landing south wall, face y 4.95 (wall y 4.83..4.95) | x -0.29..0.47 (centre 0.09), head 1.98 above F1f (Z 5.40) | hinge on the **east** jamb, swings **south into the green bedroom** (v4:f_0306, v3:f_0507, v6:f_0013) | **bracketed cornice hood**: architrave 80 mm, plain frieze 110 mm, then a deep moulded cornice shelf 1.25 m wide x 0.10 high projecting 0.11, carried on two carved **acanthus console brackets** (0.09 w x 0.17 h) set just outside the architrave; top of the shelf 2.25 above F1f, i.e. 0.10 below the ceiling. No pediment on this side (v6:f_0014–f_0018, v3:f_0504). "It's the same on either side" — the room side is the green-bedroom spec's. |
| `d_gbath` | front-landing east wall = staircase wall, x 0.99..1.25 | y 5.13..5.89 (centre 5.51), head 1.98 above F1f | hinge on the **south** jamb, swings **east into the bathroom** (v4:f_0306–f_0307, f_0157–f_0167) | plain architrave, outer edges y 5.05 and 5.97; the raking dado of `stairs2` dies into its north leg |

Other openings:

- **Arch** between corridor and bay — see 3.4.
- **Stairwell edge**: the east side of the upper strip (x 0.15, y 6.06..8.13) is open to the main
  flight below and to `stairs2` above; guarded as described in 5.1.
- The main flight arrives through the open south side of QL (x 0.15..0.99 at y 8.13).

---

## 3. Architecture and trim

### 3.1 The two steps (F1r → F1f)

- Two risers of 0.19 across the full 0.80 width between the west wall and the top newel: **riser A at
  y 8.13** (in line with the top riser of the main flight and the north face of the newel), **riser B
  at y 7.88**. One intermediate tread 0.25 deep at Z 3.23. Square nosings wrapped in the landing
  carpet, 25 mm overhang. (v3:f_0075, f_0496–f_0501.)
- On the **west wall** the skirting and the dado rail **rake** over the two steps at the stair pitch
  (about 37 degrees), with mitred knees top and bottom: dado top 0.975 above F1r north of y 8.13,
  0.975 above F1f south of y 7.88, straight rake between.
- On the east side the steps die against the newel base and the stairwell balustrade.

### 3.2 The riser between QL and the corridor

One riser of 0.19 along **x = 0.15 from the newel (y 8.13) to y 8.97**, then returning 0.10 east along
y 8.97 to the foot of the chamfered corner (v3:f_0044, f_0047). Carpeted, square nosing. You step up
westwards from QL onto the corridor.

### 3.3 West (party) wall along the corridor

Not one plane (v3:f_0050–f_0052, `v3_f0054`, v4:f_0293):

| y range | face x | notes |
|---|---|---|
| 4.95..8.53 | -0.65 | front landing, upper strip, the two steps |
| 8.53..9.95 | **-0.55** | pier 0.10 proud (the same projection as the ground-floor `hall_pilaster_s`, y 8.53..9.88); carries painting W3 and a double socket |
| 9.95..11.10 | -0.65 | recess with the radiator and painting W4 |
| 11.10..11.45 | arch pier, face -0.58 | |
| 11.45..12.23 | **-0.60** | bay wall 0.05 proud (ground `hall_pilaster_n`); painting W5 |

Skirting, dado and cornice return round every break.

### 3.4 Arch ("a beautiful arch")

- Plain plastered **semicircular** arch in a 0.35 m thick wall (y 11.10..11.45), no archivolt, no
  corbels, no keystone; arrises slightly eased (about 10 mm radius — "smooth corners").
- Clear width **0.80** (x -0.58..0.22); springing **1.65** above F1r, radius 0.40, crown **2.05**
  (lower than it looks: the blue door's pediment apex at 2.26 is only just visible under it from the
  corridor).
- Jambs: square piers standing 0.07 (west) and 0.03 (east, corridor side) proud of the corridor walls;
  on the bay side the bay walls are wider apart, so the piers read as 0.02 (west) and 0.27 (east)
  returns. Dado rail and skirting run **through the arch on the reveals** (v3:f_0061–f_0063).
- Wall above the arch is plain to the cornice.

### 3.5 Trim

- **Skirting**: white gloss, 170 mm, ogee/torus top moulding, everywhere including round the chamfer
  and the piers. On the QL walls it is the same board, so its top is 0.17 above QL.
- **Dado rail**: white gloss, 65 x 28 mm (astragal over a cavetto), top edge **0.975** above the local
  floor. One continuous level rail on the corridor east wall, round the chamfer and along the QL north
  wall (so 1.165 above the QL floor there); on the QL east wall it turns down into the raking rail of
  the main staircase. Present on every landing wall, both sides of the arch, the bay and the front
  landing; it stops against door architraves.
- **Cornice**: small plain plaster cove, about 70 mm drop x 70 mm projection, on all landing walls. It
  returns round the wall breaks. At the change of ceiling level above the two steps (y about 8.0) there
  is a **plastered downstand** 0.28 deep across the corridor with the cove returned on both faces
  (v4:f_0277–f_0280).
- **Ceilings** flat, white. Front landing and upper strip Z 5.77; rear corridor and bay Z 5.49. Over
  the stairwell there is no first-floor ceiling (see `stairs2`).

---

## 4. Surfaces and colours

| surface | description | sampled sRGB | true (neutral daylight) |
|---|---|---|---|
| Walls above the dado, arch, soffits | matt emulsion, warm white | #dbd7cb, #cfccbd, #dde5ed (cool window light) | **#F1EEE6** |
| Walls below the dado | matt emulsion, light greige — same paint as the ground-floor hall dado | #c7c1b3, #adb0b4 | **#C8C5BB** |
| Ceilings | matt white | #b7b3a7 (shade) | **#F6F5F2** |
| Skirting, dado, architraves, doorcases, cornice | white gloss | #c4bdac (shade) | **#F4F3EF** |
| Carpet — QL, corridor, steps, strip, front landing and the whole main flight | deep plush saxony, pale silver-beige, visible brush marks and footprints; fitted wall to wall, no runner | #cac3b2, #dcd6c8 (lit), #999381 (shade) | **#C9C2B3**, roughness 1.0, large soft mottling ±6 % |
| Doors | oak veneer, satin | #887248 | **#B8915A** |
| Newels, handrails | mahogany, gloss | #2a221e, #1d1613 | **#4A2216** |
| Spindles, strings | white gloss | — | #F4F2EC |
| Brass (levers, hinges, threshold strips) | polished | — | #C9A24A, metallic |

The carpet of `stairs2` is a different, greyer carpet and starts at its first riser (see `stairs2`).

---

## 5. Fixed fittings

### 5.1 Newel and stairwell guarding (east edge of the upper strip, x = 0.15)

- **Top newel of the main flight**, centre **(0.20, 8.13)**: mahogany, same pattern as the hall newel
  (95 mm square base, turned vase, square block, flattened ball finial). It stands at the meeting point
  of the top riser of the main flight, riser A of the two steps and the QL / corridor riser. Its base
  is on the main-flight string at Z 2.85; top of the finial is about 1.05 above the upper strip
  (Z 4.47), so it is about 1.6 m tall overall (v3:f_0075, v6:f_0026, v4:f_0183–f_0186). The main-flight
  handrail tenons into its south-east side at Z 3.75.
- **Level balustrade** from that newel south along the strip edge for about 0.9 m (y 8.08 → 7.20):
  mahogany toad's-back handrail, top 0.90 above the strip (Z 4.32), white turned spindles at 0.11 m
  centres standing on a white capping at floor level. At y 7.20 the rail **ramps up in a short knee and
  dies into the underside of the outer string of `stairs2`** (v4:f_0181–f_0186).
- **South of y 7.20** the guard is the raking white outer string of `stairs2` itself, which comes down
  to the floor at y 6.06; the triangle between the strip floor and the underside of that string is
  filled with white spindles of increasing length (v4:f_0187–f_0190). The foot newel of `stairs2`
  stands at (0.20, 6.10) (see `stairs2`).

### 5.2 Radiator (corridor west wall, in the recess)

White **vertical oval-tube column radiator, 16 tubes** at 45 mm centres: **0.72 long x 0.57 high**,
standing 0.10 off the wall on concealed brackets, bottom 0.13 above the floor; y 10.12..10.84, opposite
the yellow-room door (seen framed by that door in v3:f_0141). Rounded tube tops. White TRV head at the
south end, chrome lockshield at the north end, 15 mm chrome tails into the floor. Gloss white #F2F2F0.

### 5.3 Sockets

| item | position (x, y, Z above local floor) | evidence |
|---|---|---|
| double switched socket, white | west wall pier, (-0.55, 9.60, 0.28) — just above the skirting | v3:f_0046, f_0050–f_0052, v4:f_0293 ("sockets and radiators") |
| double switched socket, white | front-landing south wall, east of the green door, (0.77, 4.95, 0.28) | v3:f_0507, v6:f_0015–f_0018 |

(The white plug-in device in the pier socket is clutter — omit.)

### 5.4 Other

- **Heating thermostat**: white wireless thermostat about 90 x 120 x 25 with a small display window
  (blank), corridor east wall at **(0.25, 9.72, 1.45)** above F1r (v3:f_0054, v6:f_0028–f_0030).
- **Blank plate in the ceiling** ("got an empty socket here"): white square 86 mm blank electrical
  plate flush on the corridor ceiling at about **(-0.20, 9.30)** (v3:f_0069–f_0071, v4:f_0280, f_0294).
- **Smoke alarm**: white disc dia 0.12 on the front-landing ceiling at about (-0.25, 6.30)
  (v4:f_0170–f_0173, f_0276–f_0277).

---

## 6. Furniture

None. The landings are clear. (Removed as clutter: a cat toy on the floor, the plug-in device.)

---

## 7. Art ("remember paintings, paintings, paintings")

All oil / acrylic landscapes on the **west (party) wall**, hung flat, 20–25 mm off the wall, no people.
Sizes are outer frame sizes, ±0.05 m. Centre heights are above the local floor.

| id | wall point (x, y) | centre height | W x H | frame | subject | texture source (720 x 1280 frame, quad TL, TR, BR, BL — approximate, re-pick on the frame) |
|---|---|---|---|---|---|---|
| **W1** | (-0.65, 5.50) front landing | 1.60 above F1f | 0.50 x 0.60 portrait | dark walnut moulding 50 mm with a narrow gilt slip | Venice canal: stone bridge with balustrade, pink and ochre houses, moored boat, dark rippled water | **v4:f_0273** (333,363) (665,370) (656,779) (308,758); also f_0274 |
| **W2** | (-0.65, 6.95) upper strip | 1.60 above F1f | 0.55 x 0.70 portrait | bright gold 55 mm with a rope-twist sight edge | snow scene: watermill / cottage, bare snow-laden trees, orange sunset sky reflected in a stream | **v4:f_0278** (12,68) (353,173) (365,575) (60,585); squarer but partial in `v4_f0279.jpg` |
| **W3** | (-0.55, 9.25) on the pier | 1.70 above F1r | 0.95 x 0.70 landscape | black 60 mm outer with a 25 mm gold inner band | white clapboard church with a spire, purple-leaved tree, autumn trees, green hills, path | **v4:f_0283** (26,65) (548,270) (522,657) (30,656); v3:f_0052, f_0071 |
| **W4** | (-0.65, 10.48) above the radiator | 1.62 above F1r | 0.72 x 0.56 landscape | gold 50 mm with a beaded sight edge | thatched cottages, big tree, blue cloudy sky, duck pond with white ducks, flowers | **v4:f_0287** (170,251) (608,285) (596,641) (165,623); v4:f_0286 |
| **W5** | (-0.60, 11.84) arch bay | 1.55 above F1r | 0.72 x 0.56 landscape | antique gold-bronze 60 mm, stepped | cottage with a lilac-blue roof and lit windows among purple and red blossom, stream in the foreground, white garden bench | **v3:f_0145** (72,282) (630,318) (620,758) (78,768); v4:f_0291 |
| **P4** | QL east wall (0.99, 8.55) | 1.75 above QL (Z 4.60) | 0.50 x 0.40 landscape | ornate antique-gold moulding 55 mm (egg-and-dart outer, beaded inner), wide white mount | watercolour: a pile of rocks in the sea, gulls ("painting 4"). The original has a small seated angler with a long rod on the rocks: **the figure and rod must be painted out of the crop (mandatory, privacy rule: no people)** — fill with sky wash and extend the rock silhouette; keep rocks, sea and gulls | **v3:f_0039** (30,338) (567,222) (573,795) (45,735); v4:f_0302 |

P1–P3 of the same set hang on the main staircase wall — see section 11.4.

No mirrors, rugs or curtains on the landings.

---

## 8. Lighting and switches

### 8.1 Lights

Recessed LED **downlights**, white bezel dia 85 mm, about 3000–3500 K, one circuit ("the hallway"):

| # | (x, y) | ceiling Z |
|---|---|---|
| L1 | (0.17, 5.50) front landing | 5.77 |
| L2 | (-0.25, 6.60) upper strip | 5.77 |
| L3 | (-0.25, 7.50) upper strip | 5.77 |
| L4 | (-0.20, 8.70) rear corridor | 5.49 |
| L5 | (-0.20, 9.75) rear corridor | 5.49 |
| L6 | (-0.20, 10.75) rear corridor, before the arch | 5.49 |

Count is firm to ±1 (two over the strip in `v3_f0075`, one over the front landing in v6:f_0014–f_0016,
two to three in the corridor in v3:f_0054–f_0068, v6:f_0026–f_0027); positions ±0.3 m. No pendant, no
wall lights. The arch bay has no fitting of its own. Daylight reaches the landings only through open
doors and down the well of `stairs2`.

### 8.2 Switch plates (white plastic rockers, plate centres; Z above the local floor)

| plate | position | type | gang → lights | evidence |
|---|---|---|---|---|
| **S-bay** | bay east wall, (0.49, 11.86, 1.25), right of the blue door as you face it | 1-gang | all landing downlights L1–L6 | "this one controls the hallway, hallway is now light off" v3:f_0149–f_0152; pressed again f_0485 ("I'll turn the hallway lights back on") |
| **S-stair** | corridor east wall, (0.25, 9.40, 1.25), between the chamfered corner and the thermostat | 1-gang | the same landing downlights (multi-way) — they also light the main staircase; this is the upstairs end of the ground-floor hall plate's left gang ("goes to the first floor") | "this is the first floor, I'm going to turn it on here" v6:f_0030–f_0035 |
| **S-front A** | front-landing south wall, (0.84, 4.95, 1.27), next to the bathroom door | 1-gang (wide rocker) | **green-bathroom** lights | "turn off the bathroom light" v4:f_0264–f_0267 |
| **S-front B** | same wall, (0.70, 4.95, 1.27), next to the green door | 2-gang | **right rocker (west, nearest the green door)** = landing downlights L1–L6; **left rocker (east)** = second-floor landing lights | "I'll turn off the hallway light" v4:f_0270–f_0271 (right rocker); "here I can also turn on the second floor lights" v4:f_0310–f_0311 (left rocker) |

So L1–L6 are switched from four places: the ground-floor hall plate, S-stair, S-bay and S-front B
(right). In the viewer any of them toggles the group.

---

## 9. Reference frames

| frame | shows | camera (world x, y; eye Z) → looking |
|---|---|---|
| v3:f_0036–f_0038 | QL from the last steps: square landing, east and north walls, chamfered corner, corridor carpet above | main flight, (0.6, 7.6; 4.0) → north, down |
| v3:f_0039, v4:f_0302 | painting P4 over QL, level dado turning into the stair rake | QL / corridor → east |
| v3:f_0041–f_0044 | "square angle" NE corner of QL; **45-degree chamfer** with dado and skirting mitres; riser up to the corridor | QL (0.5, 8.4; 4.3) → north / north-west |
| v3:f_0045–f_0048 (`v3_f0047.jpg`) | plan view of QL, newel, the riser line and its return, west-wall pier break | above QL, looking straight down (image top = west) |
| v3:f_0050–f_0052 | west wall: pier, socket, radiator, W3, W4, W5 beyond the arch | QL / corridor → west and north-west |
| **v3:f_0054** (`v3_f0054.jpg`, grids `g_v3_54a/b/c.jpg`) | level view of the whole rear corridor: radiator, yellow door edge, thermostat, arch, bay, pedimented blue door, ceiling | (-0.25, 8.3; 4.45) → north |
| v3:f_0061–f_0063, f_0147–f_0149 | arch and blue doorcase close up; cove cornice | corridor (−0.2, 10.3) → north |
| v3:f_0066–f_0071 | ceiling: downlights, blank plate | corridor → up |
| **v3:f_0073–f_0076** (`v3_f0075.jpg`) | the two steps, top newel, QL below on the left, upper strip to the green door, W2 and W1, raking dado, `stairs2` string overhead | (-0.2, 9.0; 4.5) → south |
| v3:f_0140–f_0146 | yellow door threshold, radiator opposite, W4, W5 | yellow doorway → west / north-west |
| v3:f_0150–f_0152 | S-bay switch | bay → east |
| v3:f_0487–f_0495 | corridor looking south from the arch: yellow door, thermostat wall, QL, newel, two steps | (-0.2, 11.3; 4.5) → south |
| v3:f_0496–f_0502 | two steps and raking skirting / dado close up; upper strip | on the steps → south-west, down |
| v3:f_0503–f_0509 (`v3_f0507.jpg`) | front landing: `stairs2` newel and bullnose, bathroom door, switches, socket, green door | (-0.2, 6.3; 4.9) → south / south-east |
| v4:f_0166–f_0169 | front landing seen through the bathroom door: green doorcase, W1, dado | bathroom (1.6, 5.5) → west |
| v4:f_0181–f_0190 | level balustrade, knee into the `stairs2` string, spindles under the string | upper strip → east, down |
| v4:f_0265–f_0271, f_0310–f_0311 | S-front A and B being pressed | front landing → south-east |
| v4:f_0273–f_0292 | W1 … W5 one by one; ceiling downstand at f_0277–f_0280 | walking north along the west wall |
| v4:f_0293–f_0303 | radiator and W4 from the arch; S-bay; chamfered corner, switch, curved soffit over QL | (-0.1, 11.0) → south-west, then corridor → south-east |
| v4:f_0304–f_0307 (`v4_f0306.jpg`) | bathroom and green doors side by side with their hinges, switch plates, socket | upper strip (-0.3, 6.6) → south-east |
| v6:f_0012–f_0020 (`v6_f0013.jpg`) | front landing from `stairs2`: green doorcase with console brackets, switches, W1, low ceiling and the well trimmer | on `stairs2` (0.6, 6.7; 5.5) → south, down |
| v6:f_0025–f_0030 (`v6_f0026.jpg`, `v6_f0028.jpg`, grid `g_v6_28.jpg`) | strip → two steps → corridor → arch; thermostat and S-stair; chamfer | (-0.3, 7.3; 4.9) → north |
| v6:f_0031–f_0036 | S-stair pressed; QL and curved soffit; P4 | corridor (0.0, 9.3) → south-east |

---

## 10. Interactions

| object | action | notes |
|---|---|---|
| `d_yellow` | hinge about the north jamb, 0 → 100 degrees into the yellow room | owner opens and closes it (v3:f_0079, f_0132–f_0140) |
| `d_blue` | hinge about the west jamb, 0 → 90 degrees into the blue bedroom | "doors can open and close" (blue spec owns the leaf) |
| `d_green` | hinge about the east jamb, 0 → 90 degrees into the green bedroom | opened at v3:f_0508–f_0510 |
| `d_gbath` | hinge about the south jamb, 0 → 90 degrees into the bathroom | opened at v4:f_0156–f_0167 |
| S-bay, S-stair, S-front B right | toggle landing downlights L1–L6 | any of them, plus the ground-floor hall plate |
| S-front B left | toggle second-floor landing lights | |
| S-front A | toggle green-bathroom lights | |

Nothing else on the landings moves (radiator valve and thermostat are static).

---

## 11. Corrections to the ground-to-first staircase (`spec/rooms/stairs.md`, `house.json` `stairs`)

The night video stopped at the hall ceiling; daylight v3:f_0001–f_0048 and v6:f_0036–f_0047 show the
whole flight. `spec/phase2/ground_corrections.md` HA1 already covers the 45-degree wall at the foot;
the points below add to it.

1. **Foot: 45-degree wall, and three true winders.** "45 degree angle here, like I told you before, do
   the steps" (v3:f_0001–f_0013). The square nib does not exist; the hall east wall turns through a
   diagonal face to the staircase wall (HA1: (0.65, 5.05) → (0.99, 5.39)). Painting P1 almost fills
   that face (frame 0.50 wide, about 0.03 of wall each side in v3:f_0009), so the face is **0.55 ± 0.07
   long** rather than 0.48 — worth 0.05 on each leg. Seen from above (v3:f_0011–f_0013) the first
   three treads are **kite winders radiating from the newel**: riser 1 is a quarter-round bullnose that
   starts at the external corner of the diagonal and sweeps to the newel; risers 2 and 3 are **straight
   lines from the newel** fanning at about 55 and 25 degrees to the square risers, landing on the
   diagonal face and on the internal corner; riser 4 is the first square one. The existing
   "R2 gentle arc, R3 almost straight" should become two straight radiating risers.
2. **Riser count 15 confirmed**, top riser R15 = landing nosing at Z 2.85 (y 8.13 in the existing
   chain). 14 treads between floor and landing.
3. **The top is a square quarter landing, not a 0.6 m half-landing facing a wall.** QL is 0.84 x 0.84
   (x 0.15..0.99, y 8.13..8.97) with walls on the east and north only; the stair does not end against
   a "facing wall with dado at Z 3.815" — you turn left (west) up one riser onto the rear corridor, or
   left again up two more risers along the west wall to the front. `house.json` `stairs.landing.polygon`
   → [[0.15, 8.13], [0.99, 8.13], [0.99, 8.97], [0.15, 8.97]], z 2.85. The ground-floor lobby soffit
   feature should grow to the same footprint.
4. **Paintings on the staircase wall (x 0.99): four landscape-format watercolours in matching ornate
   antique-gold frames, not four small portrait boat prints.** Each about 0.50 w x 0.40 h outer, 55 mm
   egg-and-dart moulding with a beaded sight edge, wide white mount, image about 0.30 x 0.20.
   Hung plumb, centres about 1.55 above the nosing line.

   | id | where | centre (y, Z) | subject | texture source (720 x 1280, approximate quad) |
   |---|---|---|---|---|
   | P1 | on the **45-degree face** at the foot | face centre, Z 1.85 | winter river: dark trees, snow banks, small boat, pale yellow sky | v3:f_0024 (frontal) (15,300) (640,315) (600,765) (95,750); v3:f_0009 |
   | P2 | stair wall | (6.25, 3.05) | red-brown rowing boat at anchor on blue-grey water | v3:f_0027 (10,335) (715,345) (700,880) (40,870) |
   | P3 | stair wall | (7.30, 3.95) | curved wooden jetty with a seated angler and three gulls, pale blue water | v3:f_0033 (5,340) (715,350) (700,905) (35,895) |
   | P4 | QL east wall | (8.55, 4.60) | angler on rocks (section 7) | v3:f_0039 |

5. **Stairwell is not a plain shaft capped at Z 5.6.** Over the bottom five treads (y < 6.06) the
   ceiling is the flat soffit of the first-floor front landing at Z 3.17; from there north a **sloping
   plaster soffit** — the underside of `stairs2` — rises parallel to the pitch about 2.25 above the
   nosing line (v6:f_0037–f_0042); over QL it becomes a smooth **curved quarter-vault** under the
   winders of `stairs2`, springing from the QL east and north walls at about Z 4.95 (v4:f_0300–f_0303,
   v6:f_0033–f_0036). The west side of the well above the hall ceiling is open to the upper strip
   through the balustrade described in 5.1.
6. **Balustrade**: the mahogany handrail and white spindles continue unbroken to the top newel at
   (0.20, 8.13); spindles and cut string as `stairs.md`. Newel drop below the string as HA3.
7. **Wall string and dado**: as `stairs.md`; at the top the raking dado on the east wall turns level
   at the south edge of QL and runs round QL at Z 4.015 (0.975 above the corridor floor, 1.165 above
   QL).
8. **Carpet colour**: the same pale silver-beige as the landings, **#C9C2B3**, not #9C958A (that was
   the night exposure).
9. **Levels to add to `house.json`**: QL 2.85, F1r 3.04, F1f 3.42. The ground-floor **rear corridor**
   ceiling (given as 2.95) lies under F1r 3.04 and must come down to about 2.78; the ground-floor
   agent should confirm from v2.

---

## 12. Doubts and things other areas must agree with

1. **Absolute Y of everything** (±0.20). Chain used: main-flight top riser 8.13 → QL north wall 8.97 →
   yellow door clear 10.15..10.91 → arch 11.10..11.45 → blue door wall 12.23. An end-anchored reading
   of `v6_f0028` alone puts the QL north wall 0.2 further north (9.15), which would also move the top
   riser to 8.35. If the ground-floor stair is shifted north (HA1 moved its foot by 0.22), shift QL,
   the two steps and `stairs2` with it and shorten the wall between QL and the yellow door.
2. **Front-landing south wall at y 4.95** (range 4.85–5.30). It is fixed here by `stairs2` (first
   riser 6.06) minus the bathroom door set (0.92) and margins. `ground_corrections.md` L1 puts the
   living-room north wall below at 5.19–5.31; if the green bedroom's north wall must stack on that,
   the front landing is only about 0.8 deep and the bathroom door must sit partly beside the first
   step — the stills (v6:f_0013, v4:f_0306) show it clear of the step, hence 4.95. Green-bedroom and
   green-bathroom specs must use the same line and the same two door openings (section 2).
3. **Corridor width 0.90** (x -0.65..0.25) and **bay width 1.09** (x -0.60..0.49): from the level frame
   `v3_f0054`; the bay is wider on the east. What is behind the bay's east wall (x > 0.49, y
   11.45..12.23) and behind the arch pier is the blue en-suite's or the yellow room's business — the
   yellow room's north wall is taken as y 11.15..11.25.
4. **Arch size**: clear 0.80, crown 2.05, thickness 0.35 — each ±0.08. It is low and narrow compared
   with the ground-floor arch.
5. **Riser height / levels**: 0.19 assumed for all 18 risers. Direct measurement of the two steps in
   `v3_f0075` gives 0.17–0.23. If the ground-floor ceilings stay at 2.95, F1f 3.42 implies a 0.47 floor
   zone at the front.
6. **Ceiling heights**: 2.35 on the front landing / strip (the green doorcase cornice at 2.25 is 0.10
   below it), 2.45 in the rear corridor; the downstand between them above the two steps is read from
   v4:f_0277–f_0280 only. ±0.10.
7. **West-wall pier** y 8.53..9.95: ends taken from the ground-floor pilaster and from the radiator
   position; ±0.15 each.
8. **Radiator length 0.72**: from the view through the yellow door (16 tubes counted); 0.70–0.80.
9. **Downlight positions** are schematic; the count 6 is ±1.
10. **Switch S-stair**: what exactly came on at v6:f_0034 is not visible; mapped to the landing
    downlights.
11. Green doorcase: flat cornice hood on consoles on the landing side; the owner's "pediment … the
    same on either side" may mean the green-bedroom side has the triangular pediment seen in
    v4:f_0205–f_0207.
12. Painting sizes ±0.05; W2 and W1 heights are from oblique views.

## Reconciled dimensions (house.next.json)

Added by the phase-2 reconcile step. `spec/house.next.json` is canonical; where the text above differs, the values below win. Reasons and evidence: `spec/RECONCILE2.md` (decision ids in brackets).

Levels as section 1: quarter landing 2.85, rear 3.04, front 3.42 [L1, L2]. In `house.next.json` the landing is three
rooms: `landing1_ql`, `landing1_rear`, `landing1_front`.

| item | this spec | reconciled | why |
|---|---|---|---|
| quarter landing | y 8.13..8.97 (0.84 square) | **y 8.13..8.73 (0.84 x 0.60)** | [S1] its north wall is the old rear wall of the main house, as on the ground and second floors |
| 45-degree chamfer | (0.25, 9.07)-(0.35, 8.97) | **(0.25, 8.83)-(0.35, 8.73)** | moves with that wall |
| strip beside QL | y 8.13..8.97 | y 8.13..8.73 | riser returns along y 8.73 for x 0.15..0.35 |
| corridor | y 8.97..11.10 | y 8.73..11.20 | |
| arch wall | y 11.10..11.45 | **y 11.20..11.50** | [P3] one line with the second-floor arch |
| arch bay | x -0.60..0.49, y 11.45..12.23 | **x -0.65..0.40, y 11.50..12.39** | [P2] en-suite west wall is x 0.40..0.50; blue door wall moved |
| `d_blue` | wall face y 12.23, clear x -0.44..0.32 | **wall y 12.39..12.52, clear x -0.481..0.281** | [P2] |
| `d_green` | wall 4.83..4.95, clear x -0.29..0.47 | same wall, clear x -0.281..0.481 | [P7] |
| `d_gbath`, `d_yellow` | - | unchanged (y 5.13..5.89; y 10.15..10.91) | |
| yellow room north wall | y 11.15..11.25 | y 11.05..11.15 | [P1] |

- Fittings keyed to the bay move with it: switch S-bay → (0.40, 11.95, 1.25); painting W5 → y 11.95. Items between the
  quarter landing and the yellow door (W3, socket, S-stair, thermostat, radiator, W4) keep their world y.
- Section 11 (main stair): accepted, except the quarter-landing size above; `stairs.landing` stays y 8.13..8.73 and the
  ground-floor lobby soffit keeps its footprint. The main flight is not shifted north.
- Ground-floor rear hall ceiling (section 11.9): set to **2.84** from y 8.13 northward [G2].

## Round 3 corrections (core owner, from build/rooms2_open.md)
- 3.1 The two steps: the level trim of `landing1_front` stops on the top riser (y 7.88) and that of `landing1_rear`
  starts at the foot of the rake, y 7.88 + 0.38 / (0.19 / 0.25) = 8.38 (lib `mouldings.steps_skip`); the raking dado and
  skirting (37 degrees through the nosings) run y 7.88..8.38 (rooms/landing1.py). The carpet nosings are rounded
  bullnoses (v3 f_0497, f_0037, v4 f_0183), not square.
- 3.2 Same: rounded bullnose on the QL riser.
- 5.1 The level strip rail falls toward the south (knee about y 7.32, falling 0.70 per metre, dying into the string
  underside near y 7.0, top Z 4.0; v4 f_0183); it does not ramp up.
- 5.2 The radiator's TRV is at its north end.
- 8.2 S-stair is at (0.25, 8.93, 1.25) above F1r (the reconcile moved the chamfer to y 8.83), not y 9.40.
- The front-landing dado on the stairwell east wall (x 0.99) stops at the d_gbath architrave (y 5.96); the stairs2
  raking rail starts there (v4 f_0190, f_0196, v6 f_0014).
- Integration (circulation owner, round 3): the main-flight handrail no longer tenons into the top newel at Z 3.75. It
  dies about 25 mm into the underside of a white fascia under the strip capping at y ~7.62 (v6 f_0038; fascia 0.10
  deep, x 0.15..0.22, Z 3.32..3.42 by the strip, 3.13..3.23 by the step). Main spindles past the rail stop 5 mm into
  the fascia (tread 14: stubs).

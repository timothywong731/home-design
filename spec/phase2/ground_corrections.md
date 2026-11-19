# Ground-floor corrections and additions (Phase 2, daylight re-walk)

Sources: v2 f_0001-0146 (dining), v2 f_0366-1011 (kitchen, hall, utility, WC, dining again, hall,
living, vestibule, front doors, hall switch), v6 f_0028-0110 and f_0286-0306 (stair foot, kitchen,
basement door, lobby corners), v7 f_0001-0048 (kitchen sockets), plus the three transcripts.
Stills and montages used are in `reference/work/p2_ground_fix/` (private).
Frame references are written `v<k>:f_NNNN` (720x1280 frame files); `v2:t=701` means a full-res
still extracted at 701 s.

Compared against `spec/house.json` and `spec/rooms/{vestibule,hallway,stairs,living,kitchen,utility,
wc,dining}.md` as they stand. **Nothing in those files was edited.** Every item below gives: what the
spec says now -> what the video shows -> the corrected value. Coordinates are **world** (BRIEF frame:
metres, Z up, +Y into the house, +X to the right walking in) unless a room-local frame is named.
All ground-floor finished floors stay Z = 0.

Confidence tags: **[A]** seen clearly and/or said by the owner, **[B]** measured from one or two
oblique views (+/-0.05-0.10 m), **[C]** inferred, check in a preview render.

---

## 0. Headline list (what must change in `house.json` / the build)

| # | change | conf |
|---|---|---|
| H1 | The square "nib" at the stair foot does not exist. The hall east wall turns through a **45 degree wall segment** (0.48 long) between the living-room door and the staircase wall. | A (shape), B (position) |
| H2 | The living room's north-west corner is **chamfered at 45 degrees** (face 0.58 long) behind the door; the living-room north wall is therefore about **0.46 m further north** (y 5.19, not 4.73) and the unexplained 0.58 m "cross wall zone" between living room and kitchen shrinks to a normal 0.12 m wall. | A (chamfer), B (0.46) |
| H3 | Living door opens to **135 degrees**, parallel to the chamfer, onto a brass door stop. | A |
| H4 | Bay-window pier arrises: chamfer is **0.15 wide** (not 0.07) from skirting to z 2.20, lamb's-tongue stop to z 2.40, square above ("45 degree at the bottom, 90 degree at the top"). | A |
| H5 | Vestibule front recess: the ceiling is not a flat box. A **splayed haunch at about 45 degrees** runs along both side walls (wall top 2.63, flat ceiling 2.85). Two downlights, not one. | B |
| H6 | **Street doors open outward**, both leaves (spec: inward, assumed). French doors confirmed outward, both leaves. | A |
| H7 | The "under-stairs cupboard door" is **the door to the basement**: a stair goes down southward behind it, under the main flight. Position, hinge and swing in the spec are right. | A |
| H8 | Dining north wall: it is **not** one dark timber screen. Three separate dark-lined recesses (window, French doors, window) with **plastered wall piers carrying the dado rail** between them; reveals are **about 0.38 deep** (spec 0.22); **both** side windows run from a low window-seat sill (0.33) to the head; the west one was specified with a sill at 1.10. | A |
| H9 | Switch plates: kitchen switch is **2-gang** (spec 1-gang); dining and living plates are **3-gang rotary dimmers**; the utility's own lights are on the 3-rocker plate by the hall door and the 1-gang next to the WC door is the **WC** light. Which gang does what: section 1. | A |
| H10 | Sockets: 2 added in the kitchen, 1 in the living room (on the chamfer), 1 in the rear corridor, utility corner socket is a double. Section 9. | A/B |
| H11 | WC has **3** downlights (spec 2). Utility hanging rail runs **wall to wall**. Utility window is **obscure glass, top-hung, opening outward**, with a dark timber sill board. | A |
| H12 | Living-room furniture is on **one east-west axis**: TV, TV unit, amplifier, coffee table, sofa and the big floral painting share a centre line; the chandelier is about 0.4 m north of it. | A (axis), B (0.4) |
| H13 | There is **no teddy lamp**. "Teddy" in the v2 transcript at f_0655 is "telly": the dining-room TV turns on and off. | A |

---

## 1. Which switch controls which lights (authoritative, from the owner's demonstration)

"Left/right" are as you face the plate. Positions are plate centres.

| plate | position (world x, y, z) | type | gang -> lights | evidence |
|---|---|---|---|---|
| **Vestibule** | east wall of the rear recess, (0.65, 1.52, 1.22), directly under the alarm keypad (keypad centre z 1.48) | 1-gang rocker | vestibule lantern chandelier (2-way with the hall plate) | "light switch, this one turns on this light" v2:f_0903-0906 (lantern lights at f_0906) |
| **Hall, front** | east wall, (0.65, 3.29, 1.27), under the lower north corner of painting E1 | 3-gang rocker, 86 x 86 | **right (south, nearest the inner doors)** = vestibule / porch lights (lantern, and by assumption the two recess downlights and the three canopy lights outside); **middle** = hallway downlights (all eight, front hall to rear corridor); **left (north)** = first-floor landing / stair light | "this one also controls the porch light, the vestibule" v2:f_0998-1003 (thumb on the right rocker f_1001-1002, lantern lit through the fanlight f_1003); "this one controls the hallway" f_1005-1010 (middle rocker f_1006-1007); "and the other one goes to the first floor" f_1011 |
| **Hall, rear corridor** | east wall x 0.45, (0.45, 11.32, 1.25), just north of the utility door architrave, under painting E2 | 1-gang rocker | hallway downlights (2-way with the hall plate's middle gang) | "this one turns on and off the hallway lights" v2:f_0477-0490 (pressed f_0485, hall lit f_0490-0500) |
| **Living room** | west (terracotta) wall, (0.80, 3.40, 1.21), between the TV and the door architrave; A/C handset cradle beside it at y 3.53 | 3-gang **rotary dimmer**, 146 x 86 landscape, three round white knobs dia 25 | **right (north, nearest the door)** = ceiling spotlights; **middle** = the two brass wall lights; **left (south, nearest the TV)** = chandelier | "the controls here turns on the spotlight" v2:f_0802-0806; "this one turns on the wall light" f_0807-0809; "this one turns on the chandelier" f_0810-0816 |
| **Kitchen** | west (door) wall strip between the fridge housing and the hall-door architrave, (1.25, 7.65, 1.25) | **2-gang** rocker (spec: 1-gang) | one rocker = ceiling spotlights, the other = under-cabinet LED strips. Best reading: **right (north, nearest the door) = spotlights**, left = LED strips (v6:f_0056 thumb on the right rocker, then spots on and LED strips off in v6:f_0060-0100) [C for the order] | "this is for the spotlight and the other one is for the LED light" v2:f_0366-0375; v7:f_0043-0045 |
| **Basement stair** | inside the basement door, on the **east (left-hand) wall** of the stair shaft, about 0.12 m south of the door architrave: (0.93, 7.42), z 1.20 above the hall floor (the west wall carries the extinguisher and shelf, no switch; corrected in the verification round, INV-04) | 1-gang rocker | basement stair light L-S and both basement ceiling lights L-A, L-B (`basement.md` 8) | "this one turns on the basement light" v6:f_0117-0119 (belongs to the basement spec) |
| **Utility** | west (hall) wall, tiled, immediately left (north) of the door as you enter, (0.60, 11.30, 1.27) | plate with 3 small rockers (as `utility.md` 4.6, where it is called "appliance isolators") | gang 1 = two ceiling spotlights; gang 2 = under-cabinet LED strip ("it comes with LED as well" - it came on late, f_0533-0548); gang 3 unknown (leave inert) [C for the order] | "here I'll turn on the lights" v2:f_0529-0533 (hand on this plate f_0531) |
| **WC** (plate is in the utility) | utility south wall, between the pocket-door architrave and the tall cupboard, (2.32, 10.26, 1.22), under the bronze horse plaque | 1-gang rocker | the three WC downlights. **Not the utility lights** | "this one turns on the bathroom lights" v2:f_0603-0610 |
| WC fan isolator | same wall, (2.34, 10.26, 2.02) | fused / isolator plate | fan only, inert | `utility.md` 4.6 |
| **Dining room** | south wall, (0.67, 12.36, 1.30), midway between the TV and the door architrave | 3-gang **rotary dimmer**, 146 x 86 landscape (spec: "three small round push/toggle buttons") | **left (east, nearest the TV)** = the two wall lights; **middle** = chandelier; **right (west, nearest the door)** = ceiling spotlights | "turn on this light" v2:f_0009-0012 (wall lights lit f_0011); "turn on the middle light" f_0013-0015; "turn on all the spotlights" f_0016-0018 |

For `blender/INTERACT.md`: the viewer's `light` type toggles whole rooms. If per-circuit switching is
wanted, each plate above needs one tagged knob/rocker per gang; if only room-level toggling is kept,
tag the plate with these rooms: vestibule plate -> `vestibule`; hall plate -> `hallway` (+ `vestibule`
on the south rocker); corridor plate -> `hallway`; living -> `living`; kitchen -> `kitchen`;
utility 3-rocker -> `utility`; WC plate -> `wc`; dining -> `dining`.

---

## 2. Vestibule

**V1. Front-recess ceiling - splayed haunches ("this is about 45 degree angle... can you work out the angle") [B]**
- Spec: recess B (y 0 .. 0.74) has a flat ceiling at 2.85 meeting the walls square.
- Video: looking up beside the street door the owner points at the junction of side wall and ceiling
  on both sides. The west wall is vertical up to about the top of the street-door frame, then a
  sloping plane rises to the flat ceiling (two clear creases, v2:t=917, t=919). The east side over the
  cheek window does the same with a softer, slightly coved, lower crease (v2:t=911, t=913, t=927).
- Corrected: flat ceiling z 2.85 only between x -0.43 and +0.68. Along the west wall (x -0.65) and the
  east cheek wall (x +0.90) model a **haunch plane 0.22 wide in plan x 0.22 high**, i.e. 45 degrees:
  wall top z 2.63, meeting the flat ceiling 0.22 out from the wall. Both haunches run the full depth
  of the recess (y 0 .. 0.74) and die into the street-door head wall and the south face of the arch
  wall. Angle read from the stills is 40-50 degrees; 45 is the owner's own figure.
- The rear recess (y 1.29 .. 1.73) and the basket-arch vault between the piers are as specified.

**V2. Front-recess downlights [A]**
- Spec: one downlight at (0.20, 0.35). Video: two (v2:t=911, f_0924, f_0926), set diagonally.
- Corrected: (-0.25, 0.28) and (+0.35, 0.50), white bezel dia 85, in the flat part of the ceiling.
  Three more are visible through the transom in the outside canopy soffit, as `vestibule.md` 7.

**V3. Street doors open outward, both leaves [A]**
- Spec (`house.json` d_street): `swingInto: vestibule`, never opened, modelled closed.
- Video: the owner pushes the west (letterbox) leaf out and walks onto the paving (v2:f_0941-0946);
  from outside both leaves stand open outward in turn (f_0959-0966, "both doors can open");
  closed again from inside f_0978-0982 ("the one can close, the other one can also close").
- Corrected: `swingInto: outside`, hinges on the outer edges, each leaf swings out about 100 degrees.
  Letterbox on the west leaf is confirmed. The transom keeps plain frosted glass (privacy).

**V4. East cheek wall of the front recess - two lights, dado, transition to the door [A]**
- Confirms `vestibule.md` 2.3: two separate white-architraved lights one above the other, the lower
  with the living-room shutter behind it, the upper clear ("two windows, about here" v2:f_0927-0930).
- Addition: the dado rail carries on from the cheek wall round the corner onto the short piece of
  front wall between the cheek (x 0.90) and the street-door frame (x 0.62), and **stops with a mitred
  return end about 40 mm short of the door frame** ("the dado rail all the way and then I got a
  transition towards the front door", v2:f_0933-0939). A plain white 70 mm vertical cover board
  stands in the corner between cheek wall and front wall. Skirting does the same.
- The east pier is square in plan and the old front-wall face runs on behind it to the cheek, as in
  `house.json` (v2:f_0974, f_0975). Coats, shoe rack and boots in this corner are clutter.

**V5. Inner doors [A]** - both mahogany leaves open into the hall and close ("both of them can open
and close", v2:f_0895-0900, f_0982-0986). No change to geometry.

**V6. Lantern** is switched from two places (section 1).

---

## 3. Hallway and stair foot

**HA1. The 45 degree wall segment at the stair foot (replaces the square nib) [A shape, B position]**
- Spec: `house.json` feature `hall_nib` is a square return, polygon (0.65, 4.73) (0.99, 4.73)
  (0.99, 4.83) (0.65, 4.83); hallway polygon steps at y 4.83; `hallway.md` "a return wall runs east
  0.34 m to x = +0.99"; cornice, dado and skirting "turn the corner".
- Video: "this wall is quite special... this segment is about 45 degree... this is not a right angle"
  (v2:f_0671-0702, best v2:t=701 and f_0692, f_0694, f_0698; also v6:f_0044 from above). North of the
  living-room doorcase there is a piece of **flat** wall in the plane of the hall east wall carrying a
  level dado rail, then an external corner, then a wall face running diagonally back to the
  staircase wall, then an internal corner.
- Corrected plan (hall-side faces):
  - hall east wall x = 0.65 continues north past the doorcase to **y = 5.05** (0.40 of flat wall
    beyond the doorcase architrave's outer edge at y 4.65; measured 0.40-0.50 against the 170 mm
    skirting and 70 mm dado rail in v2:t=701);
  - **diagonal face from (0.65, 5.05) to (0.99, 5.39)**: 0.48 long, at 45 degrees to both walls
    (external corner 135 degrees at the south end, internal corner 135 degrees at the north end);
  - staircase flank wall x = 0.99 from y 5.39 northward, unchanged.
  - Full height: it rises to the hall ceiling and on up the stairwell.
- New hallway polygon: (-0.65, 1.83) (0.65, 1.83) **(0.65, 5.05) (0.15, 5.05)** (0.15, 7.68)
  (0.99, 7.68) (0.99, 8.73) (0.45, 8.73) (0.45, 12.23) (-0.65, 12.23).
  New stairs polygon: (0.15, 5.05) (0.65, 5.05) (0.99, 5.39) (0.99, 7.58) (0.15, 7.58).
  Delete `hall_nib`; delete wall `w_nib`; `v_stair_foot` becomes (0.15, 5.05) -> (0.65, 5.05).
- Steps: the existing riser chain still fits. R3 (straight, y 5.36) meets the **internal** corner;
  R2's east end lands on the diagonal at about (0.80, 5.20) instead of on the stair wall; the bullnose
  R1 ends at the **external** corner (0.65, 5.05) and sweeps round to the newel at (0.20, 5.33) - use
  a quarter-ellipse centred (0.65, 5.33) with semi-axes 0.53 (x) x 0.28 (y) instead of 0.53 x 0.48.
  R4-R15, newel, balustrade unchanged (v2:f_0690-0700).
- Trim on the segment (v2:t=701, f_0692):
  - **Dado rail**: level at z 0.965 on the flat wall, mitres round the external corner, then **rakes
    up the diagonal at the stair pitch** (about 40 degrees) from 0.965 to about 1.36 at the internal
    corner, makes a short level piece 0.10-0.15 long there, and continues raking up the staircase
    wall as in `stairs.md`. Lower wall colour (greige) follows the rail.
  - **Skirting**: the 170 mm hall skirting returns round the external corner for about 60 mm and
    then becomes the wall string of the stair, curving up over the three bottom steps along the
    diagonal.
  - **Cornice**: follows the diagonal with two 135 degree mitres [C - the cornice above this corner
    is not in a v2 frame; v1 f_0084/f_0246 showed it "turning the corner"].
- Painting S1 (small gilt-framed winter scene) hangs on the diagonal / start of the stair wall just
  above the dado rake (v2:f_0692, f_0700), consistent with `stairs.md` 6.

**HA2. Basement door (the spec's "under-stairs cupboard door") [A]**
- Spec: `d_understairs`, oak 4-panel 0.61 x 1.981 in wall y 7.63, centre (0.57, 7.63), hinge east,
  swings north into the lobby, "cupboard under the flight; modelled closed", `connects:
  [hallway, stairs]`.
- Video: "this door leads to the basement... this goes further down, negative one floor"
  (v6:f_0094-0125). Hinge knuckles on the east (left as you face it), lever handle on the west,
  leaf swings north into the lobby (v6:f_0105-0115) - **position, hinge and swing are correct**.
  Behind it: a metal threshold strip, then the first step down immediately inside; a straight narrow
  flight (about 0.68 between white walls) descending **south**, under the main flight, with
  wood-effect tile treads; a 1-gang switch on the right-hand (west) wall; a fire extinguisher on the
  floor against the west wall on the top step (v6:f_0117-0125).
- Corrected: rename to `d_basement`, `connects: [hallway, basement]` (stair down), `openAngle` 0 as
  modelled, state 1 = 90 degrees into the lobby. When open it stands across the kitchen doorway (the
  two doors cannot both be open: kitchen door open 90 degrees parks against the lobby north wall,
  so there is no clash in the modelled state). Stair well below the door: x 0.22 .. 0.90, running
  south from y 7.58. Level, riser count and the lower end are the basement spec's.
- White beaded tongue-and-groove boarding between the door head and the overhead cupboard, as spec.

**HA3. Storage cabinet with brass handle (overhead cupboard) and "the corners" [A]**
- Spec: `lobby_overhead_cupboard` x 0.20 .. 0.95, y 7.68 .. 8.13, z 2.30 .. 2.60, one flat
  full-width top-hung door with a brass D-handle.
- Video (v2:f_0500-0510, f_0520-0522; v6:f_0286-0302 "there's corners here... the corners ends this
  way"): confirmed. Details to add:
  - the handle is a polished-brass **bow (cup-less D) pull about 110 mm**, centred on the width,
    about 60 mm above the bottom edge of the flap;
  - the flap is **top-hung and lifts outward** (hinge line under the soffit); tag it `hinge` about
    the top edge, about 80 degrees;
  - the flap face is a plain flat white panel; the cupboard's underside is a plain flat board; its
    west end butts the square **drop of the upper newel / corner post**, which hangs about 0.25 m
    below the landing string with a moulded cap, and the modillion cornice of the bulkhead face
    (x = 0.15) stops against that post with a mitred return (v6:f_0298-0302). Keep the post square,
    0.10 x 0.10, with a small ogee cap at its bottom end.
  - the soffit over the lobby east part (z 2.60) and the bulkhead cornice are as specified.

**HA4. Arch [A]** - "make sure you get the arch right... arch details... that's the arch on this
side" (v2:f_0488-0518; v6:f_0304). The description in `hallway.md` 2.5 holds: plain plastered arch,
no archivolt, one fluted scroll corbel with a three-step cap on each jamb, visible from both sides.
Two refinements from the daylight views: (a) the curve reads as a **semi-ellipse / three-centred
arch** rather than a flat segment - keep springing 2.40 and crown 2.75 but round the haunches
(haunch radius about 0.30, crown radius about 0.75) so the soffit leaves the corbel caps vertically;
(b) only about 0.10 of flat wall remains between crown and cornice level. No cornice crosses the
arch wall (confirmed f_0512-0516).

**HA5. Sockets and fittings on the hall walls** - see section 9. The lobby socket and the
thermostat sit on the plain west wall just **south** of the south pilaster break (v2:f_0675),
as specified.

**HA6. Steps** - "steps" (v2:f_0520-0524) is the owner showing the cut-string tread ends and the
panelled spandrel; nothing differs from `stairs.md`. There are **no level changes** on the ground
floor (kitchen and utility thresholds are flat bars, v2:f_0474, f_0528).

**HA7. Inner-door hardware, console, mirror, barometer, paintings W1-W4, E1, E2, clock, Wi-Fi access
point, smoke alarm** - all re-seen in daylight where specified (v2:f_0486-0526, f_0666-0686,
f_0893-0895, f_0988-1010). No position changes.

---

## 4. Living room

**L1. North-west corner is a 45 degree chamfer; the north wall moves north [A chamfer, B size]**
- Spec: main rectangle x 0.80 .. 4.30, y 0.99 .. 4.73; door architrave "0.15 m from the rear (N) wall
  corner"; "the terracotta/pink change happens exactly at the two inside corners of the W wall".
- Video: "and same for the other side... this is the door, this is about 45 degree angle... behind
  the door there's a socket" (v2:f_0702-0724; v2:t=717; cornice f_0722-0726; also f_0882-0888).
  North of the door architrave the terracotta west wall continues for about 0.20 m, then the wall
  turns 45 degrees: a **pale-pink diagonal face 0.58 long** (0.53-0.64 measured against the 146 mm
  socket and the 170 mm skirting on it), then a second 135 degree corner into the north wall. The
  corner where terracotta changes to pink - which v1 took for the room corner - is the **start of
  the chamfer**, so the north wall is one chamfer leg (0.41) further north.
- Corrected plan (room-side faces):
  - west wall x = 0.80 from the west nib to **y = 4.78** (door opening y 3.70 .. 4.48, architrave to
    4.58, terracotta strip 4.58 .. 4.78);
  - **chamfer from (0.80, 4.78) to (1.21, 5.19)**;
  - **north wall y = 5.19** from x 1.21 to 4.30 (was y 4.73);
  - east wall x = 4.30 now runs y 0.99 .. 5.19.
  New living polygon: (0.80, 0.99) (1.10, 0.99) (1.10, 0) (4.00, 0) (4.00, 0.99) (4.30, 0.99)
  **(4.30, 5.19) (1.21, 5.19) (0.80, 4.78)**. Main room is 3.50 wide x **4.20** deep at the east
  wall (was 3.74; `layout.md` originally estimated 4.10).
  The wall between living room and kitchen (kitchen south face y 5.31) becomes a plain **0.12 m
  partition**; `cross_wall_zone` and the 0.58 m thick `w_cross` go away (`w_cross` centreline
  y 5.25, thickness 0.12, x 1.25 .. 4.415).
  Solid poche remains in the triangle between the living chamfer, the hall diagonal (HA1) and the
  staircase wall: the two diagonal faces are parallel and about 0.30 m apart.
- Everything specified against the north wall moves **+0.46 in y** with it: bookcase, tapestry,
  paintings A1-A4, plant, pedestal with bird, north end of the brass rod, the NE-corner socket, and
  the A/C console / side table at the north end of the east wall keep their distance from the NE
  corner. The plant pot stands in front of the chamfer / north-wall corner at about (1.35, 4.85)
  (v2:f_0714-0720).
- Trim: skirting (0.17, white) and the plain run cornice both follow the chamfer with two 135
  degree mitres (v2:f_0716-0718, f_0722-0724). Colours: terracotta on the west wall up to the first
  corner, pale blush pink on the chamfer and north wall.

**L2. The door opens wide, to the chamfer [A]**
- Spec: leaf stands open about 95 degrees "parallel to and about 0.12 m off the rear wall".
- Video: "the door opens quite wide" (v2:f_0879-0890, also f_0704-0712); "I can shut the door"
  f_0710-0714. Hinges on the north jamb (three brass butts) confirmed.
- Corrected: `openAngle` **135**: the open leaf lies parallel to the chamfer, about 0.07 off it,
  resting on a **wall-mounted brass door stop** (square brass rose 40 x 40, 70 mm stem, black rubber
  tip) fixed on the chamfer 0.47 m from its west corner at z 0.30 (v2:t=717), i.e. at about
  (1.13, 5.11). State 1 = closed.

**L3. Brass picture rod [A]**
- "The metal rod goes from about here for all these paintings... it goes all the way to this side...
  make sure you've got the spacing right" (v2:f_0726-0736).
- North-wall run: starts with a ball finial about 0.12 east of the chamfer corner, **x 1.33 -> 4.25**
  at y 5.19; east-wall run: from the NE corner south to **y 1.40** (finial about 0.40 short of the
  east nib). Height, diameter, brackets and S-hooks as `living.md` 3. Bracket spacing about 0.9 m:
  4 brackets on the north run, 5 on the east run [B].

**L4. Bay piers - chamfer size and stop ("smooth transition from 45 degree at the bottom to 90
degree at the top") [A]**
- Spec: chamfer about 70 mm wide to z 2.25, stop 70 x 110.
- Video: v2:f_0736-0750 (east pier; the west one matches in f_0798, f_0808). At floor level the
  skirting turns the corner in three facets with the middle one about as long as the skirting is
  high.
- Corrected: on each front-wall nib the arris between its room face (y 0.99) and its bay-side end
  face (x 1.10 west nib, x 4.00 east nib) is cut by a **45 degree chamfer 0.15 wide (legs 0.105)**
  from the floor to **z 2.20**; from 2.20 to **2.40** a pointed lamb's-tongue stop (the chamfer
  face narrows to a point on the arris in a concave ogee each side); above 2.40 the arris is square
  up to the cornice, which keeps its square break round the nib.

**L5. Bay, shutters, curtains [A]**
- Bay confirmed square in plan (corner posts and 90 degree cornice mitres, v2:f_0752-0756). The
  west return light looks into the vestibule: "this one is special, this one goes to the vestibule,
  you can see the tiles and the front door" (v2:f_0779-0788) - as `house.json`.
- Shutters: "you can open and close all these shutters" - each of the six lower-light panels is a
  hinged leaf that swings **into the room** like a casement (v2:f_0760-0770, f_0778-0782), and the
  louvres of each panel **tilt together** when one slat is pushed (hidden tilt rod; open louvres
  show the street / the vestibule, f_0762, f_0774, f_0784). Operable: panel swing (`hinge`,
  about 100 degrees, hinged on the frame side away from the brass catch) and, if cheap, a louvre
  state (closed / horizontal).
- Curtains: "curtains can open and close" (v2:f_0750-0758) - four tartan drops with rope tie-backs,
  one at each nib and one at each bay corner, as `living.md` 6.

**L6. Furniture centring [A for the axis]**
- Owner: "I got an amplifier and a PlayStation, this is centred... right at the centre is also the
  coffee table, this is centred to the sofa, centred to the painting... the chandelier is slightly
  off to one side... we are about centring at the chandelier, about here" (v2:f_0823-0866).
- Spec (reconciled world values): TV centre y 2.33, TV unit centre 2.23, amplifier left of centre,
  coffee table centre (2.80, 2.81), sofa centre y about 2.05, rose/chandelier (2.55, 2.86).
- Corrected: one **east-west axis at y = 2.33**:
  - TV centre (0.80 wall, y 2.33) - unchanged; white cable trunking drops at y 2.33;
  - TV unit centre y **2.33**; valve amplifier **centred** on the unit top; the black games console
    ("PlayStation") lies centred on the open shelf below it; speakers at the two ends; the xiangqi
    board sits between the amplifier and the north speaker, DVD cases between the amplifier and the
    south speaker (cases are clutter);
  - coffee table centre **(2.80, 2.33)**, long axis north-south (parallel to the sofa); rug centred
    under it;
  - sofa centre y **2.33** against the east wall;
  - on the east wall the **large gold-framed floral painting** is centred on y 2.33; the two
    landscape prints (stacked) hang to its north and the two small white floral prints (stacked) to
    its south, with the oil landscapes at the north end (v2:f_0836-0850);
  - ceiling rose and chandelier at **(2.55, 2.73)**, about 0.40 north of the axis [B: 0.3-0.5 from
    v2:f_0846-0854].
  - long bench: just north of the coffee table, long axis east-west, centre about (2.90, 3.75) - it
    is 1.0-1.2 m in front of the bookcase now that the north wall has moved, not 0.45 [B].
  - armchair + footstool ("armchair and a stool, this is the stool", f_0861-0876): footstool in
    front of the east bay armchair, as specified.

**L7. Switch plate, wall lights** - plate and its three circuits in section 1. The two five-arm
gilt wall lights are confirmed over the door and near the bay end of the west wall (v2:f_0794-0798,
f_0808). They are one circuit.

**L8. Sockets** - double socket on the chamfer (section 9).

---

## 5. Kitchen (kitchen-local mm as `kitchen.md`: world = local/1000 + (1.25, 5.31))

**K1. Light switch is 2-gang [A]** - see section 1. Position unchanged (door wall, y 2340, z 1250).

**K2. Sockets [A]** - v7 is a dedicated socket tour. Full list in section 9; two are new (hob wall
behind the spice rack; sink wall at the far corner) and one low socket by the back door.

**K3. Everything opens - real divisions and hinge sides [A unless noted]**
The owner opens almost every front in v2:f_0375-0470 and v6:f_0090-0096. The unit list in
`kitchen.md` 4.2-4.5 is right except H3.

| unit (spec id) | what it is | how it opens | inside (keep simple) | frames |
|---|---|---|---|---|
| H2, 600 base, hob wall north end | one door | hinged on its +Y (back-door) side, T-bar on the -Y edge | one shelf | v2:f_0458-0464 |
| **H3, 200** | spec says "narrow pull-out". It is a **narrow hinged door** over a tray space | hinged +Y like H2 (handle on the -Y edge) | chopping boards / trays on edge, no shelf | v2:f_0460-0466 [B for the hinge side] |
| H4, 800 pan drawers | three drawers | slide out 0.40: top = cutlery tray (grey insert, 5 compartments), middle = plates and bowls, bottom = glass containers and pans | - | v2:f_0446-0456 ("roll out, roll out") |
| H5, corner knob door | door | hinged -Y | - | v6:f_0070 |
| W1 wall unit | one door | hinged +Y | two shelves | v2:f_0468 |
| W2 | pair of narrow doors | hinged on the outer edges | two shelves | v7:f_0011-0013 |
| S1 dishwasher | integrated dishwasher, immediately right of the hob-wall corner | door drops down 90 degrees about its bottom edge; horizontal T-bar | lower rack, upper rack and a shallow top cutlery tray; steel tub; the control strip is on the top edge of the door | v2:f_0380-0388 |
| S2 sink base | pair of doors | hinged on the outer edges | centre divider; left bay under the bowls (waste disposer, filter), right bay with a bucket | v2:f_0390-0396 |
| S3 | single door | hinged -X | - | v2:f_0392 |
| T1 / T6 corner knob doors, T2, T5 | doors | as spec | two shelves | v6:f_0078-0086 |
| T3 plate rack | upper **lift-up flap** over the open rack | top-hung, lifts about 90 degrees | one shelf | v6:f_0092-0094 |
| oven tower, bottom | **warming drawer** (black glass front) | slides out 0.35 | - | v2:f_0398 |
| oven tower, middle | **main oven** | door drops down about 85 degrees, bar handle at the top | chrome side racks, two wire shelves, fan at the back; interior light | v2:f_0398-0400 |
| oven tower, upper | **compact combi oven** | door drops down about 85 degrees | two round fans at the back, one shelf | v2:f_0402-0404 |
| oven tower, top cupboard | framed door above the oak filler strip | hinged -Y (sink side), long T-bar on the +Y edge | one shelf, oven trays | v2:f_0406-0410 |
| fridge-freezer, **left (-Y) door = freezer** with the ice / water dispenser | door | hinged on its outer (-Y) edge, about 110 degrees | white ice-maker housing on the inside of the door, four door bins; five shelves over two drawers; cool-white LED | v2:f_0418-0424 |
| fridge-freezer, **right (+Y) door = fridge** | door | hinged on its outer (+Y) edge | five door bins (cans, eggs, bottles); four glass shelves over two crisper drawers; cool-white LED | v2:f_0412-0418, f_0424-0426 |
| niche above the fridge | open, cans on top of the fridge | - | - | v2:f_0422 |
| bridging cupboard over the fridge | one wide flap, horizontal T-bar | top-hung lift-up | - | v2:f_0422-0424 |
| nook base, 300 (next to the hall door) | door | hinged -X | - | v2:f_0442 |
| nook base, 350 | door | hinged -X | bottles | v2:f_0438 |
| nook base, 600 | door | hinged +X | - | v2:f_0440 |
| hob | five gas burners, five knobs | knob = trigger, flame per burner | - | v2:f_0380 |
| taps | spring-neck mixer **and** the small boiling / filter tap both run | lever on the mixer; the small tap's top lever | - | v6:f_0060-0068 ("I'm going to have some tea here") |

Generic fridge contents only (no branded packaging, no magnets or photographs on the doors).

**K4. Bins [A]** - "bin, you can open it... open the bin, you can open all that" (v2:f_0428-0436;
v7:f_0037-0043).
- **Stainless pedal bin** (rectangular, brushed steel, flat lid hinged at the back, steel pedal bar
  at the front, 0.26 w x 0.40 d x 0.65 h): on the floor against the door-wall strip between the
  fridge housing's end panel and the hall-door architrave, long side along the fridge side panel,
  centre about world (1.47, 7.64). Lid opens about 70 degrees about its back edge.
- **Black plastic pedal bin** (0.40 w x 0.30 d x 0.60 h, flat lid with a silver label strip, hinged
  at the back, foot pedal): on the floor against the nook-wall pier in front of the chequer plate,
  centre about world (2.90, 8.55). Lid opens toward the wall.
  Both are owner-named and operable; keep them (they are not "countertop mess").

**K5. Back door [A]** - "cat door is at the center... this is a kitchen door" (v2:f_0356-0366).
- Spec: cat flap "centred about 80 right of panel centre". Corrected: flap **centred on the leaf's
  lower panel**, bottom of its frame at z 0.19; white frame about 0.22 x 0.24, smoked flap.
- Hinge on the +X (east) jamb, opens **into** the kitchen against the clear wall H0 (the owner comes
  in through it, f_0358-0362): as specified. Upper glazing is **obscure (frosted)**, not clear
  (f_0358, f_0366; v6:f_0070-0074); the toplight too.
- Outside this door there is a step down and a tap on the wall (rear-exterior spec).

**K6. Chequer plate on the pier [B]** - spec 540 wide (x 1410 .. 1950). With a socket to its right
before the door reveal (v2:f_0434-0436; v7:f_0037-0041) it is narrower: **x 1410 .. 1830**
(0.42 x 0.265, z 0.52 .. 0.785).

**K7. Lighting [A]** - four ceiling spotlights on one rocker; under-cabinet LED strips (hob wall
under W1 and W2, sink wall, corner cupboard) on the other (v2:f_0375-0380 both on; v6:f_0070-0100
spots only).

---

## 6. Utility (world; room x 0.60 .. 3.10, y 10.26 .. 12.23)

**U1. Switching [A]** - section 1: the 3-rocker plate on the tiled hall wall just inside the door
is the utility's own light switch; the 1-gang under the horse plaque is the WC light.

**U2. Window [A]** - `w_utility`, centre (3.20, 11.61), 0.56 x 0.82, sill 1.05.
- Spec: "one clear pane", "top-hung opener assumed", plastered reveal about 0.12 deep.
- Video: "this window opens to the outside" (v2:f_0564-0578). The sash is **top-hung and swings
  outward** from the bottom (brass handle on the bottom rail, pushed out in f_0570-0574); glass is
  **obscure / frosted**; the bottom of the reveal is a **dark-stained timber window board about
  0.25 deep** (same stain as the dining joinery) sitting one tile course above the oak worktop;
  side and head reveals are white plaster, about 0.25 deep.
- Corrected: glass obscure; `slide`/`hinge` tag: hinge about the top edge of the sash, 25 degrees
  outward; reveal depth 0.25; timber sill board.

**U3. Hanging rail runs wall to wall [A]** - "there's a metal rod all the way through, from wall
to wall" (v2:f_0588-0592). Spec: x 0.90 .. 2.80 on three drop rods. Corrected: chrome tube dia 25
from the hall wall (x 0.60) to the window wall (x 3.10) with a round wall flange at each end,
y 11.26, z 2.10, plus two chrome ceiling drop rods at about x 1.45 and x 2.45. Model it empty.

**U4. Tall storage tower [A]** - "you can open these cabinet doors separately" (v2:f_0576-0588):
upper and lower doors are separate leaves, both hinged on the wall (south) side, as specified.
Upper compartment has one shelf.

**U5. Sockets [A]** - two **double** switched sockets on the north-wall splashback (the corner one
was specified as a single): section 9.

**U6. "A small gap on the other side, really tiny gap" [C]** - v2:f_0554-0566: at the east end of
the wall-cabinet run the last cabinet side stops about 20 mm short of the plastered return beside
the window, leaving a narrow shadow gap from the tile line to the ceiling. Keep the cabinets as
specified and make sure that gap is a thin dark slot, not a wide strip of wall.

**U7. Operable [A]** - all five wall-cabinet doors and the base doors open ("all these cabinets can
open"), the Belfast-sink tap runs ("water can run", f_0552-0556), the under-cabinet LED strip is a
separate circuit, the hall door swings and the WC pocket door slides ("doors you can slide open
and close", f_0598-0602).

---

## 7. WC (world; room x 0.60 .. 3.10, y 9.36 .. 10.14)

**W1. Three downlights [A]** - "got three spot light here" (v2:f_0608-0610). Spec: two.
Corrected: on the centre line y 9.75 at x 1.05, 1.85 and 2.65.

**W2. Operable [A]** - "toilet to lift up" (lid, then seat, v2:f_0614-0620: two groups hinged about
the back hinge line); "water can run" (single-lever chrome basin mixer, f_0624-0626); pocket door.

**W3. Soap dish [A]** - "there's a soap dish" (v2:f_0624-0626): a frosted-glass dish in a chrome
ring holder fixed to the marble tiles on the basin wall, about 0.18 left of the tap centre line and
0.16 above the basin's top edge (dish dia 0.11). Add it.

**W4. Small fixed accessories seen in daylight [B, optional]** - black double toilet-roll holder on
the south wall beside the pan at z 0.65; brushed-steel toilet-brush holder on the floor beside the
pan (v2:f_0614-0622). The grey pedal bin is clutter.

Everything else (grey walls, half-height marble tiles, wall-hung pan with chrome flush plate, ledge
with plant, two prints, fan, obscure window, black towel radiator, gilt mirror) is confirmed by
v2:f_0604-0626.

---

## 8. Dining room (world; room x -0.65 .. 3.10, y 12.36 .. 16.86)

**D1. North wall is three separate recesses with plastered piers between [A]**
- Spec (`dining.md` 2.3, `house.json` feature `dining_n_screen`): one dark timber screen across the
  whole wall with two dark posts and flat dark infill panels beside the French doors.
- Video: "this is curtain... behind the curtain there's the dado rail, this is what's behind the
  curtain... remember all the dado rail has got across here" (v2:f_0076-0108; v2:t=87). Behind each
  tied-back curtain is an ordinary **wall pier**: cream above, aubergine below, the white reeded
  dado rail and the dark skirting running across it, between the dark architrave of the French-door
  recess and the dark architrave of the window recess.
- Corrected layout along the wall (world x; each recess has its own 0.10 dark reeded architrave on
  the room face, as the door surround):

  | x from | x to | element |
  |---|---|---|
  | -0.65 | -0.44 | wall (dado, skirting) |
  | -0.44 | -0.34 | architrave |
  | -0.34 | 0.18 | **west window recess**, 0.52 clear |
  | 0.18 | 0.28 | architrave |
  | 0.28 | 0.54 | **wall pier 0.26** with dado rail (behind the west curtain) |
  | 0.54 | 0.64 | architrave |
  | 0.64 | 1.83 | **French-door recess**, 1.19 clear |
  | 1.83 | 1.93 | architrave |
  | 1.93 | 2.195 | **wall pier 0.265** with dado rail (behind the east curtain) |
  | 2.195 | 2.295 | architrave |
  | 2.295 | 2.815 | **east window recess**, 0.52 clear |
  | 2.815 | 2.915 | architrave |
  | 2.915 | 3.10 | wall |

  Opening centres stay as `house.json` (-0.09, 1.225, 2.54 within 0.02). The dark head member over
  the three recesses (z 2.38 .. 2.50, under the pelmet) may stay continuous [C]; below it the piers
  are plaster.

**D2. Reveals are deep [A]** - "the window goes quite deep... here it goes quite deep" (v2:f_0086-0098,
f_0128-0138).
- Spec: reveal 0.22. Video: the dark-stained jamb linings and the window-seat board measure
  **0.35-0.42** (against the 0.52 window width, the 0.33 pot and the cushions, v2:t=73, t=87,
  f_0128, f_0134-0136). Corrected: **0.38** from the room face of the architraves to the uPVC
  frame, for both window recesses and the French-door recess; head soffit lining the same depth.
- Consequence: the north wall must be at least about 0.47 thick (0.38 + frame). Either thicken
  `w_dining_n` to 0.50 (outer face y 17.36, `bounds.maxY` 17.36) or keep the outer face and move
  the room face. The interior measurement (room length 4.50 to the room face) is the one to keep;
  the rear-elevation spec decides the outer face.

**D3. Both side windows run from a low window seat to the head [A]**
- Spec: west window frame z 1.10 .. 2.23 with a full-height dark apron; east window z 0.30 .. 2.20;
  "not the same height".
- Video: east - "a whole big window, all the way to the bottom" (v2:f_0066-0076); west - "the
  window also goes all the way from the top to the bottom, it goes quite deep" (f_0128-0140, seen
  behind the cat tree in f_0140).
- Corrected, both windows: white uPVC frame 0.52 wide, **z 0.37 .. 2.20**.
  - **East**: one tall pane, trickle vent at the head (fixed; a possible side-hung opener cannot be
    excluded) [B].
  - **West**: a transom at about z 1.55; **top-hung opening fanlight** above it (white handle on
    its bottom rail, f_0128-0132) and a fixed pane below [A]. Fanlight opens outward about 20 degrees.
  - **Window seat / sill** in each recess: dark-stained board 40 mm thick, top at **z 0.33**, as
    deep as the reveal (0.38), rounded nosing projecting 30 mm past a flat dark apron panel that
    drops to a 60 mm plinth at the floor (v2:t=73). No skirting or dado across the recess.
  - Clear glass in both. Outside: garden to the east window, the neighbour's brick flank wall and a
    trellis to the west one.

**D4. French doors and cat door [A]**
- "This door is openable, open both doors, it goes to the patio" (v2:f_0146-0158): both leaves
  swing **outward** (confirmed; spec had it as an assumption). Brass lever handles both leaves.
- "There's a cat door here, a transparent cat door" (v2:f_0118-0124, f_0146): round white-rimmed
  flap with a clear flap and two red catches, in the **lower pane of the west leaf**, centred on the
  pane width, centre z about 0.30, outer dia about 0.26 - as `dining.md` 2.3. Tag it as a small
  hinged flap if cheap.

**D5. Pelmet and curtains [A]** - "there's a pelmet that holds the curtain... same for this side"
(v2:f_0108-0118). White boxed pelmet under the cornice, wall to wall, z 2.50 .. 2.65 as specified,
but projecting about **0.18** from the wall face (it clears the 0.10 architraves and the curtain
heading; spec 0.12) [B]. Corded track under it: two thin white pull cords with weights hang at the
outer edge of each curtain (f_0066-0070, f_0080). Two check curtains, each tied back with a gold
rope and tassel onto its wall pier; operable open / closed.

**D6. Dado rail has ribbon crossings [A]** - "got this shape right" (v2:f_0100-0108, f_0643-0650,
v2:t=87). The white reeded rail (`dining.md` 3: five reeds, 55 mm high, top 1.05) is a
**reed-and-ribbon** moulding: every 0.30-0.35 m a pair of thin raised ribbons crosses the reeds in
an X about 45 mm wide. A normal map tiled at 0.32 m is enough. It runs on all walls including the
two north-wall piers and stops square at every dark architrave.

**D7. Switch plate [A]** - a 3-gang rotary dimmer (section 1), centre z about 1.30 (spec 1.37).

**D8. Television; there is no teddy lamp [A]** - "I have put a sword in here; there's a telly, the
telly can turn on and off" (v2:f_0655-0660 - the transcript prints "teddy"; the owner is holding
his hand in front of the TV, and the first line of the video is "the telly, you can turn on the
lights here"). No teddy-shaped object appears in any dining frame. The only animal-shaped object is
a white cat-eared **pet drinking fountain** on the floor by the south end of the hearth
(v2:t=41, t=661) - a pet item, omit. Action: the dining TV is the on/off `trigger` (`fx tv`);
no lamp to add.
- The sword board above the TV (dark wood board with two crossed/parallel sabres, f_0006-0008,
  f_0656-0658) is confirmed.

**D9. Sockets [A]** - one double in each east alcove between the window surround and the chimney
breast, and one low on the west wall near the north-west corner ("there is a socket here",
v2:f_0040-0042, f_0058-0060, f_0142-0144): section 9.

**D10. Confirmed without change** - hall door hinged west, opening into the room, dark reeded
surround with cornice head ("doors, behind the door", v2:f_0019-0030); fireplace, barley-twist
columns, sunflower tiles, hearth; the two obscure east windows with sills at 1.10 and plants; brass
twin wall lights with cream shades in both alcoves; chandelier and rose; crest plaques; carved
panels and mirrors on the west wall.

---

## 9. Sockets and small wall fittings (all white plastic unless noted; z = plate centre)

| room | wall / place | world (x, y, z) | type | status | evidence |
|---|---|---|---|---|---|
| hall | west wall, front hall, just south of the console | (-0.65, 3.59, 0.36) | double | as spec, re-seen | v2:f_0894 |
| hall | west wall, lobby, just south of the south pilaster | (-0.65, 8.36, 0.34) | double (white plug-in night light in it: omit) | as spec | v2:f_0675, f_0479 |
| hall | same place | (-0.65, 8.43, 1.42) | heating thermostat / receiver | as spec | v2:f_0675 |
| hall | west wall, rear corridor, in the recessed bay about 0.13 south of the north pilaster | (-0.65, 11.40, 0.35) | single or double (small) | **new** [B] | v2:f_0668-0670 |
| hall | west wall "south pilaster north of the arch" (spec local y 7.95) | (-0.59, 9.53, 0.34) | double | not seen in v2 - keep only if a v1 frame is unambiguous [C] | - |
| living | on the NW chamfer, 0.30 along it from its west corner | (1.01, 4.99, 0.31) | double switched | **new** | "behind the door there's a socket" v2:f_0714-0720, t=717 |
| living | east wall at the NE corner | (4.30, 5.03, 0.33) | double | spec item, moves north with the wall | - |
| kitchen | hob wall (x 4.30), under wall unit W1, behind the spice rack | (4.30, 7.56, 1.12) | double switched, on the tiles | **new** | "there's a socket at the back" v7:f_0001-0009 |
| kitchen | hob wall near the sink-wall corner, under W2 | (4.30, 5.87, 1.13) | double switched | as spec | "towards here there's one socket here" v7:f_0011-0015 |
| kitchen | sink wall (y 5.31), behind the dish rack, left of the sink | (3.95, 5.31, 1.13) | double switched | as spec | "a socket there... this is the sink" v7:f_0017-0021 |
| kitchen | sink wall | (4.15, 5.31, 1.13) | small 1-gang fused switch | as spec | v7:f_0013 |
| kitchen | sink wall at the far (oven-tower) corner, behind the coffee machine | (1.60, 5.31, 1.13) | double switched | **new** | "behind at the far corner there's the socket" v7:f_0022-0031 |
| kitchen | nook-wall pier, right of the chequer plate, before the back-door reveal | (3.15, 8.73, 0.60) | single (white plug-in device in it: omit) | **new** [B] | "behind the bin there are also sockets" v7:f_0037-0041; v2:f_0434-0436 |
| kitchen | nook reveal / pier | (2.95, 8.73, 1.43) | room thermostat | as spec | v7:f_0037 |
| utility | north-wall splashback above the washing machine | (1.00, 12.23, 1.10) | double switched | spec item, 0.15 further from the corner | "there's a socket here" v2:f_0538-0550 |
| utility | north-wall splashback at the NE corner | (2.90, 12.23, 1.10) | **double** switched (spec: single) | corrected | v2:f_0558-0560, f_0580 |
| dining | east wall, south alcove, between window surround and breast | (3.10, 13.59, 0.33) | double switched | as spec | v2:t=41, f_0662 |
| dining | east wall, north alcove, between breast and window surround | (3.10, 15.63, 0.33) | double switched | as spec | v2:f_0058-0060 |
| dining | west wall near the NW corner | (-0.65, 16.35, 0.40) | double | spec "single, uncertain" -> confirmed present | v2:f_0142-0144 |
| vestibule, WC | - | - | none | as spec | - |

Plug-in devices, chargers and cables are clutter.

---

## 10. Interactions the owner demonstrated or named (ground floor)

Doors: street doors (2 leaves, **outward**); inner mahogany doors (2 leaves, into the hall); living
door (closed <-> 135 degrees); basement door (into the lobby); kitchen door; kitchen back door
(inward) and its cat flap; utility door; WC pocket door (slide); dining door; French doors (2 leaves,
outward) and the round cat flap.
Windows: utility window (top-hung, out); dining NW fanlight (top-hung, out); living-bay shutters (6
hinged panels, louvre tilt); bay fanlights as `living.md`.
Curtains: living bay (4 drops), dining (2 drops).
Lights: every plate in section 1; no lamp in the dining room; the living-room bay table lamp stays
a `lamp` as specified.
Kitchen: every unit in K3 (doors, 3 drawers, dishwasher, warming drawer, 2 ovens, freezer door,
fridge door, 3 lift-up flaps), 2 pedal bins, 5 hob burners, 2 taps.
Utility: wall and base doors, tower doors (2), washer and dryer portholes, tap.
WC: toilet lid and seat, basin tap.
Hall: overhead storage flap. Dining: TV on/off. Living: TV (as specified).

---

## 11. Patch list for `spec/house.json` (apply in the reconcile step, not done here)

1. `rooms.hallway.polygon` and `rooms.stairs.polygon`: as HA1. Remove feature `hall_nib` and wall
   `w_nib`; add a wall or feature for the diagonal (0.65, 5.05) -> (0.99, 5.39), full height.
   `stairs.winders`: R1 ellipse semi-axes 0.53 x 0.28, R2 ends on the diagonal.
2. `rooms.living.polygon`: as L1 (north wall y 5.19, chamfer (0.80, 4.78) -> (1.21, 5.19)); size
   [3.5, 4.2]. `w_cross`: centreline y 5.25, thickness 0.12. Remove feature `cross_wall_zone`.
   `w_hall_living` now ends at y 4.78 (living face) / 5.05 (hall face); `w_party_e_living` to y 5.25.
3. `d_living.openAngle`: 135.
4. `living_bay` notes: chamfer 0.15 wide to z 2.20, stop to 2.40.
5. `d_street.swingInto`: `outside`.
6. Vestibule: add feature `vest_haunch_w` / `vest_haunch_e` (y 0 .. 0.74, 0.22 x 0.22 at 45 degrees,
   wall top 2.63).
7. `d_understairs` -> `d_basement`, `connects: [hallway, basement]`.
8. `dining_n_screen`: replace by three reveals 0.38 deep at x -0.34 .. 0.18, 0.64 .. 1.83,
   2.295 .. 2.815; `w_dining_n_w`: sill 0.37, height 1.83, style top-hung fanlight over fixed pane;
   `w_dining_n_e`: sill 0.37, height 1.83; `w_dining_n.thickness` 0.50 (or as agreed with the
   rear elevation).
9. `w_utility`: style `white_upvc_obscure_top_hung`.

---

## 12. Dimension confidence and doubts

**Confidence.** Shapes and "what is where" in this file are from clear daylight views and the
owner's words. Sizes come from in-plane references in the same still (146 mm socket plates, 170 mm
skirting, 70 mm dado rail, 0.52 m window, 86 mm switch plates) and are good to about +/-0.05 m for
the chamfers and reveals. Absolute y positions inherit the +/-0.3 m chain tolerance of `layout.md`.

**Doubts.**
1. **Position of the hall diagonal (HA1).** The flat wall between the doorcase and the external
   corner measures 0.40-0.50; I used 0.40 because it lands riser R3 exactly on the internal corner
   with the existing stair chain. If the stair chain is re-derived from the first-floor work, keep
   "R1 ends at the external corner, R3 at the internal corner" and move the diagonal with it.
2. **Living north wall at y 5.19 (L1).** It follows from door position + 0.20 strip + 0.41 chamfer
   leg. The strip could be 0.15-0.30, so y is 5.14-5.29. Any value above 5.19 needs the kitchen
   south wall (5.31) to move too. The hall-side and living-side diagonal faces come out about 0.30
   apart - thicker than a stud partition; treat the triangle as solid.
3. **Rose / chandelier offset (L6)**: 0.40 north of the furniture axis is an estimate from two
   hand-held views; the owner only says "slightly off to one side". With the longer room the rose
   is no longer at the geometric centre of the room - not verified.
4. **Vestibule haunches (V1)**: real, but the angle (40-50 degrees), the 0.22 size and whether the
   east one is flat or slightly coved are from upward ultrawide views. The owner himself is unsure
   of the angle.
5. **Kitchen 2-gang order and utility 3-rocker order** (section 1): which rocker is spots and which
   is LED is a best reading; the third utility rocker is unknown.
6. **Hall plate, middle vs left rocker**: the middle rocker is under the owner's thumb while he
   says "hallway"; "first floor" is the left one by elimination.
7. **H3 narrow unit**: hinged door rather than pull-out, hinge side +Y - from two oblique frames.
8. **Dining north wall head**: whether the dark head member is continuous over the two piers or the
   plaster runs up to the pelmet there; whether the east window has an opener.
9. **Dining reveal depth vs wall thickness (D2)**: 0.38 is the interior measurement; the outer face
   of the rear wall is for the rear-elevation spec.
10. **Utility "tiny gap" (U6)** and the low kitchen socket by the back door (exact plate type).
11. **Rear-corridor socket** at y 11.40 - seen once at the edge of a frame; and the spec's pilaster
    socket at y 9.53 was not re-seen.
12. Cornice over the hall diagonal was not filmed in daylight.

**Things other areas must agree with.**
- **Basement**: door `d_basement` at (0.57, 7.63), 0.61 clear, hinge east, opening north; stair
  starts immediately inside and descends south in a well x 0.22 .. 0.90; switch on the west wall.
- **First-floor landing / stairs**: the 45 degree segment and the staircase wall carry up through
  the stairwell; the hall plate's north rocker switches the first-floor landing light.
- **Front exterior**: street doors open outward; three canopy downlights outside on the same
  circuit as the vestibule (assumed); bay front and door screen in one plane; plain frosted transom.
- **Rear exterior / garden**: French doors open outward onto the deck; north wall thickness (D2);
  dining side windows are full height from z 0.37, the west one with an opening fanlight; kitchen
  back door opens inward, has a centred cat flap, a step and a tap outside; utility window opens
  outward and is obscure.
- **Upper floors**: if they stack on the ground-floor walls, the front room's rear wall is at
  y 5.19 .. 5.31, not 4.73, and there is no 0.58 m thick zone to use for a chimney stack.

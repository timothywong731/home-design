# yellow_room — first-floor middle room ("yellow themed", unoccupied)

Sources: **v3 f_0077–f_0140** (all viewed; montages `m_v3_0079_0084` … `m_v3_0139_0144` and stills
`v3_f0085.jpg`, `v3_f0130.jpg`, tiles `t_yellow_a.jpg`, `t_yellow_b.jpg` in
`reference/work/p2_first_landing/`), plus glimpses through the door in v3:f_0054–f_0058, v4:f_0296,
f_0299, v6:f_0001–f_0003.

Owner narration (v3 01:10–02:16): "so this is the middle room, and this is yellow themed, you can see
that this room is unoccupied. I got an air con here, sockets, and a small radiator towards here, and the
curtains can open, and the window can also open … this is how it looks like, doors can open and close,
there's nothing behind the door … nothing behind the door."

A small plain room off the east side of the rear corridor, on the **rear level F1r (floor Z 3.04)**, in
the back addition above the ground-floor WC / utility. One door (west), one window (east, onto the side
passage), an air-conditioning unit, a small radiator and three pieces of furniture.

**Dimension confidence.** North–south width 2.08: ±0.10 (the west wall measured against the door leaf
in `v3_f0130`: 1.12 of wall + 0.91 door set + about 0.10). East–west length 2.75: **±0.25** (it is the
distance from the corridor wall to the flank wall of the back addition, x 3.10 in `house.json`; the
room was never filmed square-on along its length). Ceiling 2.45: ±0.05 (door-height scale). Window
size and sill ±0.08. World Y position ±0.20 (shared with `landing1`).

---

## 1. Shape and dimensions

Plain rectangle. **Room-local frame** parallel to the world axes:

- local **+x = world +X** (from the door wall toward the window wall),
- local **+y = world +Y** (toward the rear of the house),
- origin = floor-level inside corner of the door wall and the south wall, i.e. the corner on your
  **right** as you stand in the doorway looking in.
- **World = local + (0.35, 9.07, 3.04).**

Interior **x 0 → 2.75, y 0 → 2.08, ceiling 2.45** (flat). World rectangle x 0.35..3.10, y 9.07..11.15,
floor Z 3.04, ceiling Z 5.49.

| wall | local plane | world | what is on it |
|---|---|---|---|
| W-door (west) | x = 0 | x 0.35; corridor behind (wall 0.10) | door at the north end; light switch + air-con remote; cabinet; one socket |
| W-south | y = 0 | y 9.07; the stair quarter landing and the green bathroom are behind it | blank; one socket |
| W-window (east) | x = 2.75 (recess) / 2.65 (pier) | flank wall of the back addition, external | window with Roman blind and timber sill, radiator under it, one socket |
| W-north | y = 2.08 | y 11.15; the corridor arch wall line continues along it; blue en-suite / bay beyond | door stop, chair, ottoman, air-con unit, sockets |

Standing in the doorway looking in (facing +x): window ahead on the left half of the far wall, air-con
high on the left wall, long blank wall on the right, cabinet immediately behind you on the right.

Plan (not to scale; top = +y / north, right = +x / east):

```
 y=2.08 +--------[chair]---[ ottoman ]--(A/C above)--+
        |stop                         sk sk          |.. window recess
  door  >  (leaf opens against the N wall)           [=] window  y 0.93..1.88
 1.08.. |                                            [=]  + radiator under
 1.84   |sw                                          |.. y 0.75
        |[cab]                                   sk |##| pier 0.10 proud, y 0..0.75
 y=0    +----inet-----------------sk?----------------+
        x=0                                      2.65 2.75
```

Floor level is the corridor's (Z 3.04): carpet runs through under a brass threshold strip, no step.

---

## 2. Openings

### 2.1 Door `d_yellow` (W-door, x = 0)

- Clear opening **y 1.08 → 1.84 (0.762), head 1.98**. World: wall x 0.25..0.35, y 10.15..10.91.
- Leaf: oak-veneer Victorian **4-panel** (two tall panels over two short), 1981 x 762 x 35, satin; true
  #B8915A (sampled #887248). Polished-brass lever on a brass backplate at 1.00 m, three brass butts.
- **Hinged on the north jamb (y 1.84), swings into the room** through about 100 degrees until the
  leaf meets a small **brass door stop** screwed to the skirting of the north wall at x 0.72
  (v3:f_0133–f_0134, f_0138–f_0139). Open, the leaf stands almost flat against the north wall with a
  0.15–0.20 gap behind it — "nothing behind the door".
- Architrave: white gloss, 80 mm ogee, both sides; outer edges y 1.00 and 1.92, top 2.06.
- Brass carpet-threshold strip on the door line.

### 2.2 Window (W-window)

- The window wall is **recessed 0.10** between the north wall and a full-height pier that fills the
  south end of the east wall (pier face x 2.65, y 0 → 0.75; recess face x 2.75, y 0.75 → 2.08;
  v3:f_0083, f_0085, f_0090). The recess runs floor to ceiling.
- Window frame: white uPVC, **y 0.93 → 1.88 (0.95 wide), sill 0.92, head 2.22 (1.30 high)**; world
  centre (3.10..3.30 wall, y 10.47). Set about 0.12 back from the recess face, plastered reveals.
- Two lights, one above the other (v3:f_0109–f_0112): a **fanlight 0.30 high** over a **main light
  0.95 high**, with a 70 mm transom. Both are **top-hung, opening outward** on friction stays; each
  has a satin-gold lever handle at the centre of its bottom rail. The owner opens the **main light**
  to about 30 degrees (v3:f_0113–f_0125, "the window can also open"). Clear double glazing.
- **Sill board**: dark-stained softwood (walnut tone, true #5A3A22, knots visible, satin), 1.10 long x
  0.20 deep x 30 mm, bullnosed front edge, projecting 0.05 into the room and 0.07 beyond each side of
  the frame (v3:f_0095–f_0112, f_0125–f_0127).
- View out: the side passage and, 3–4 m away, the neighbour's yellow-stock brick flank wall with white
  sash windows and a grey downpipe; looking down, the paved passage, a slatted fence and gate, the
  kitchen back door at the internal corner to the south, and a ground-floor obscure-glazed window with
  a white hood board directly below (v3:f_0105–f_0124).

---

## 3. Architecture and trim

- **Skirting**: white gloss, 170 mm with an ogee top, all walls; it steps round the pier.
- **No dado rail, no picture rail.**
- **Cornice**: small plain plaster cove, about 70 x 70 mm, all round, returned round the pier and
  across the head of the window recess (v3:f_0085–f_0089, f_0130).
- **Ceiling**: flat, white, no rose.
- No steps, no arches, no pediments inside the room (the plain architrave only).

---

## 4. Surfaces and colours

| surface | description | sampled sRGB | true (neutral daylight) |
|---|---|---|---|
| Walls, pier, reveals | matt emulsion, **pale primrose / cream yellow** — distinctly yellower than the corridor's white when both are in one frame (v3:f_0129–f_0131) | #cfcbc0, #cbc4b1, #afa989 (shade) | **#EEE7C6** |
| Ceiling, cove | matt white | #b2aea2 (shade) | #F6F5F2 |
| Skirting, architrave | white gloss | #c1bbaf | #F4F3EF |
| Carpet | the same pale silver-beige plush saxony as the landing, fitted wall to wall | #afaba1 (shade), #cac3b2 | **#C9C2B3** |
| Door | oak veneer | #887248 | #B8915A |
| Window frame | white uPVC | — | #F5F5F3 |
| Sill board | dark walnut-stained softwood, satin | #bdb693 (glare) | #5A3A22 |

---

## 5. Fixed fittings

### 5.1 Air-conditioning unit ("I got an air con here")
White wall-mounted split indoor unit, about **0.80 w x 0.29 h x 0.22 d**, on **W-north**, x 1.85 → 2.65
(centre 2.25), top 0.10 below the ceiling (z 2.06 → 2.35). Smooth flat front, hinged outlet flap along
the bottom, small round sensor window at the bottom right. A short white trunking (60 x 40) leaves its
right-hand end and runs to the north-east corner (v3:f_0091–f_0093, f_0099). Matt white #ECECEA.

### 5.2 Radiator ("a small radiator")
White **vertical oval-tube column radiator, 8 tubes**: 0.36 wide x 0.60 high, centred under the window
at y 1.40 on the recess face, bottom 0.13 above the floor, top 0.19 below the sill board. Chrome valve
with a white TRV head at the south end, chrome lockshield at the north end (v3:f_0090, f_0095–f_0097).

### 5.3 Sockets and plates (white plastic)

| item | wall, position (local), z | evidence |
|---|---|---|
| double switched socket + single plate (fused spur for the air-con) side by side | W-north, x 2.33 and x 2.52, z 0.50 | v3:f_0092–f_0094 |
| double switched socket | W-window pier face, y 0.40, z 0.30 | v3:f_0083, f_0085 |
| single socket | W-door, y 0.85, z 0.45 (just right of the cabinet) | v3:f_0130 |
| double switched socket | W-south, x about 2.0, z 0.30 | v3:f_0082, f_0088 (position uncertain) |
| light switch, 1-gang | W-door, y 0.82, z 1.25 | v3:f_0129–f_0131 |
| air-con remote in a white wall cradle (about 0.05 x 0.16) | W-door, y 0.93, z 1.33, between the switch and the architrave | v3:f_0129–f_0131 |

---

## 6. Furniture (the room is "unoccupied" — only these)

| item | position (local) | size | description |
|---|---|---|---|
| **Small mahogany cabinet** | against W-door, y 0.15 → 0.75, depth 0.40 | 0.60 w x 0.40 d x 1.02 h | dark mahogany two-door cupboard on four short **cabriole legs** (0.25 high), moulded top with a slight overhang, two flat panelled doors with a central brass escutcheon / drop handle; true #3A2218, satin (v3:f_0081–f_0087, f_0129–f_0131). Doors may be made to open (plain empty shelves). |
| **Chippendale-style side chair** | against W-north, centre x 1.15, facing south | 0.50 w x 0.48 d x 0.95 h | dark mahogany, pierced interlaced-ribbon splat, carved cresting rail with ears, cabriole front legs on ball-and-claw feet; drop-in seat upholstered in cream linen printed with a **Jacobean tree-of-life floral** in red, blue and green (v3:f_0079, f_0085, f_0130–f_0139). Same family as the dining chairs. |
| **White storage ottoman** | against W-north, x 1.62 → 2.38, under the air-con | 0.76 w x 0.38 d x 0.38 h | white faux-leather box ottoman, lid buttoned in a 4 x 2 grid of shallow tufts (v3:f_0092–f_0094) |

Declutter: hair-dryer and flex on the ottoman, the bag and papers on the cabinet, the plug in the socket.

---

## 7. Soft furnishings and decor

- **Roman blind** in the window recess ("the curtains can open"): flat-fold blind 1.05 wide, head rail
  at the top of the recess (z 2.36, just under the cove), dropping to the sill board when down (drop
  1.44). Fabric: cream linen-look ground (true #EFE9D6) with an all-over **trailing-leaf print in
  olive, sage and ochre** (leaves 30–50 mm, on thin curling stems; #7F7C45, #A9A565, #C2B36A). Lined.
  **Bead chain on the right-hand (south) side.** Raised, it stacks in four soft folds about 0.30 deep
  at the head (v3:f_0103–f_0111). Repeat about 0.30. Texture source: **v3:f_0100** (frontal, fills the
  frame; crop about (100,150)–(650,1000)) or f_0098.
- **No pictures, no mirror, no rug, no curtains.** The walls are bare.

---

## 8. Lighting and switches

- **Four recessed LED downlights**, white bezel dia 85 mm, about 3000–3500 K, in a 2 x 2 grid at
  (x 0.75, y 0.55), (0.75, 1.55), (2.00, 0.55), (2.00, 1.55) (v3:f_0083–f_0086, f_0130–f_0131;
  three are visible at once, the fourth is inferred — ±1).
- **Switch**: the 1-gang rocker on W-door at (0, 0.82, 1.25), on your right as you walk in → all four
  downlights. (The lights are already on in the video; the owner does not operate it.)
- The air-con is controlled from the wall-mounted remote; not operated in the video.

---

## 9. Reference frames

| frame | shows | camera (local x, y; eye z) → looking |
|---|---|---|
| v3:f_0079 | door opening inward, threshold strip, chair behind the leaf | corridor (-0.4, 1.3; 1.5) → east, down |
| v3:f_0080–f_0084 | first view in: cabinet on the right, south wall, east wall with blind, radiator | doorway (0.2, 1.4; 1.5) → south-east |
| **v3:f_0085** (`v3_f0085.jpg`) | east wall (window recess, pier, socket), south wall, cove, downlight | (0.4, 1.5; 1.5) → east-south-east |
| v3:f_0086–f_0089 | south wall and south-east corner, ceiling | (0.6, 1.4) → south |
| v3:f_0090 | window recess square-on: blind down, sill board, radiator, pier on the right, air-con edge on the left | (1.3, 1.3; 1.5) → east |
| v3:f_0091–f_0094 | air-con unit, sockets, ottoman, chair on the north wall | (1.6, 0.8; 1.5) → north |
| v3:f_0095–f_0097 | radiator, valve, sill board, skirting stepping into the recess | (1.9, 1.0; 1.5) → east, down |
| v3:f_0098–f_0108 | blind pattern; chain on the right; blind being raised | (2.0, 1.3) → east |
| v3:f_0109–f_0112 | window: fanlight over main light, handles, reveals, view of the neighbour's wall | (2.2, 1.3; 1.5) → east |
| v3:f_0113–f_0125 | main light pushed open; stays; view down into the side passage | leaning out of the window |
| v3:f_0126–f_0128 | radiator and sill from above, sockets | (2.3, 1.2) → down |
| v3:f_0129 | west wall from the far end: cabinet, switch, remote, door, corridor radiator and W4 beyond | (2.3, 0.6; 1.5) → west |
| **v3:f_0130–f_0132** (`v3_f0130.jpg`) | west wall square-on: door set with the leaf open, cabinet, chair; ceiling and cove | (1.9, 1.2; 1.5) → west |
| v3:f_0133–f_0139 | door leaf swung to show the wall and door stop behind it; hinge side | (0.9, 1.2) → north-west |
| v3:f_0140–f_0141 | leaving: threshold, corridor radiator opposite | doorway → west |

---

## 10. Interactions

| object | action | notes |
|---|---|---|
| Door `d_yellow` | hinge about the north jamb, 0 → 100 degrees inward | opened and closed by the owner (v3:f_0079, f_0132–f_0140) |
| Roman blind | raise / lower (drop 1.44 → 0.30 stack) | pulled up with the chain at v3:f_0098–f_0109 |
| Window main light | top-hung, swings outward 0 → 30 degrees | opened at v3:f_0113–f_0125 |
| Window fanlight | top-hung, outward 0 → 20 degrees | has its own handle; not opened on camera — optional |
| Light switch | toggles the four downlights | |
| Cabinet doors | optional: two side-hung doors 0 → 100 degrees | not opened on camera |

---

## 11. Doubts

1. **Length 2.75** assumes the room runs from the corridor wall (x 0.35) to the flank wall of the back
   addition (inner face x 3.10). Appearance in v3:f_0083–f_0086 and f_0129 fits 2.6–3.0.
2. **World Y** (9.07..11.15) follows `landing1` (±0.20). The window centre then falls at world y 10.47,
   between the ground-floor WC window (9.58) and utility window (11.61). The stills looking down
   (v3:f_0121–f_0124) show an obscure-glazed window with a white hood **directly below**, a black soil
   pipe elbow just south of it and the kitchen back door close by at the corner — the rear-elevation /
   ground-floor agents should place the ground-floor flank windows so one of them is under this
   window, or tell me this room is further south.
3. **South wall**: taken as a 0.10 partition shared with the stair quarter landing (west part) and the
   green bathroom (east part). If the old rear wall of the main house (ground y 8.73..9.03, 0.30
   thick) carries up here, the room loses nothing but the wall is thicker.
4. **North wall** at world y 11.15: on the line of the corridor arch wall (11.10..11.45). What lies
   north of it (blue en-suite?) must agree.
5. **East wall break**: recess 0.10 with a 0.75 m pier at the south end — depths ±0.05, pier width
   ±0.15. It may equally be a boxed-in service duct.
6. **Window**: both lights top-hung outward is read from the handle positions and the opened main
   light; fanlight opening is assumed. Frame size ±0.08, sill ±0.05.
7. **Socket on the south wall** and the exact socket positions on the pier: glimpsed only.
8. **Downlight count** 4 (3 seen).
9. Wall colour: all frames are lit by warm downlights plus cool window light; #EEE7C6 is a "pale
   yellow-cream" estimate from the contrast with the corridor white.
10. Cabinet interior never shown.

## Reconciled dimensions (house.next.json)

Added by the phase-2 reconcile step. `spec/house.next.json` is canonical; where the text above differs, the values below win. Reasons and evidence: `spec/RECONCILE2.md` (decision ids in brackets).

- **Rectangle x 0.35..3.10, y 9.03..11.05 (2.75 x 2.02)** — was y 9.07..11.15 (2.08) [P1]: the south wall is the old rear
  wall of the main house (face 9.03) and the room gives up 0.06 so that the en-suite and the blue bedroom fit behind it.
- Floor Z 3.04, ceiling 2.45 (Z 5.49): unchanged.
- **Transform**: local → world is now (x + 0.35, y + 9.03). Items keyed to the south wall move -0.04 in world y, items
  keyed to the north wall -0.10; the door (clear y 10.15..10.91) and the window frame (y 10.00..10.95) keep their world
  positions, so the window is 0.10 from the north wall and the door architrave 0.06 from it.
- Flank wall: inner face 3.10, outer face **3.40** (0.30) [E2].

## Round 3 corrections (core owner, from build/rooms2_open.md)
- East wall: one face at x 3.00 along the whole wall except a window-wide niche y 10.00..10.95, 0.10 deep, from the
  floor to a soffit at Z 5.32 (house.json yellow_pier_e, yellow_pier_ne, yellow_niche_head; v3 f_0083, f_0085, f_0090,
  f_0093, f_0109). The cornice runs straight at x 3.00; the skirting steps into the niche.
- d_yellow opens 95 degrees (at 100 it ran 12 mm into the north wall and swallowed the door stop; v3 f_0130 / f_0138).
- Wall paint #F0EBD6 (the spec's #EEE7C6 rendered mustard) is now the shell finish.

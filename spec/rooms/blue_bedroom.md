# blue_bedroom — rear "blue" bedroom, first floor (above the dining room)

Sources: v3:f_0150–f_0490 (every odd frame viewed as 6-up montages in `reference/work/p2_blue/m/`), full-res
stills `reference/work/p2_blue/v3_tNNN.jpg` (t = frame − 1), gridded measurement crops in
`reference/work/p2_blue/g/`, rear-elevation stills `v2_t172/t210/t250/t314.jpg`. Owner narration v3 02:28–08:04
("this is the rear blue bedroom … big radiator, a big telly at the centre … doors can open and close, pediment,
hook … a beautiful light here … inside this is a toilet … there's a wardrobe, there's a mirror in the middle, all
these can also open and close … small gap, make sure you get the corners right, get the pediment right … the lights
can turn on and off individually, beautiful bed, blue bedding … outside is a balcony … a bureau, the bureau can open
and close, the drawers can also open and close … aircon, painting, telly … a big mirror, get the pattern right …
curtains can also open and close, the pelmet, get the pelmet right … a TV cabinet, this is empty, just for storage …
a beautiful star-shaped chandelier … ceiling rose").

**How it was measured.** Single-view metrology on the floor plane (`reference/work/p2_blue/met.py`: focal length
560 px at 720p from Manhattan vanishing points, gravity from the vertical vanishing point, scale from a 1981 mm door
leaf in the same frame). Two independent frames agree on the entrance-recess depth (0.38–0.46) and the run of the
south wall; two frames give 3.9–4.3 from the en-suite wall to the French-door wall; the rear elevation (v2:f_0251,
64.5 px/m, checked on the ground-floor French doors 1.19 × 2.32) fixes the French-door frame and the balcony in X.

**Dimension confidence.** Room width assumed = dining room below (party wall and flank wall continuous): ±0.05.
Length ±0.15. Positions along a wall ±0.10 (±0.15 on the west wall). Heights ±0.05 (door-leaf scale). Absolute
floor level ±0.10 — see §1 "Level" and doubt 1.

**Colour warning (applies to every phase-2 video).** The v2–v7 files are HLG / BT.2020 10-bit; the 1 fps frames
were extracted without colour conversion, so sRGB sampled from them is desaturated. "Sampled" values below come
from tone-mapped stills in `reference/work/p2_blue/sdr/` (zscale + hable), which are correct in hue but about one
stop dark and warm wherever the chandelier / downlights hit; "estimate" is the judged paint colour in neutral light.

## 1. Shape & dimensions

### Room-local frame
- Origin = floor-level inside corner of the **door wall and the west (party) wall** — the corner immediately on
  your LEFT as you step in from the landing. **+x = world +X** (toward the en-suite / bed side),
  **+y = world +Y** (straight ahead, toward the balcony). z up from this room's floor.
- **World = local + (−0.65, 12.36).** The room sits exactly over the dining room (world x −0.65..3.10,
  y 12.36..16.86), minus the en-suite block that bites into its south-east corner.

### Polygon (inside faces, counter-clockwise, local)
`(0, 0) (0.97, 0) (0.97, 0.40) (3.75, 0.40) (3.75, 4.50) (0, 4.50)`
world: `(−0.65, 12.36) (0.32, 12.36) (0.32, 12.76) (3.10, 12.76) (3.10, 16.86) (−0.65, 16.86)`.

| part | local | size | note |
|---|---|---|---|
| main room | x 0..3.75, y 0.40..4.50 | 3.75 × 4.10 | bed, wardrobe, TV wall |
| entrance recess | x 0..0.97, y 0..0.40 | 0.97 wide × 0.40 deep | the landing door fills its whole width; the en-suite block's west face is its east side |
| chimney breast (feature, not in polygon) | x 0..0.10, y 0.70..2.86 | 2.16 wide, **0.10 proud** | on the WEST wall; cornice and skirting return round it; carries the TV and the radiator |
| south alcove (W wall) | y 0..0.70 | — | behind the open door leaf; hook rail |
| north alcove (W wall) | y 2.86..4.50 | 1.64 | bureau + landscape painting |

| wall | local plane | what is on it |
|---|---|---|
| W-door | y = 0, x 0..0.97 | landing door with pediment |
| W-recess | x = 0.97, y 0..0.40 | 3-gang light switch + air-con remote cradle (faces west) |
| W-south ("block face") | y = 0.40, x 0.97..3.75 | TV cabinet under the mermaid wall light, switch, socket, **en-suite door with pediment**; wardrobe corner |
| W-east | x = 3.75 | wardrobe, nightstand, bed head under the octagonal mirror, nightstand (flank wall, no window) |
| W-north | y = 4.50 | air-con, dark painting, curtains + pelmet, French doors to the balcony in a dark timber-lined recess |
| W-west | x = 0 (breast face x = 0.10) | NAVY wall: hooks, TV over radiator, landscape painting over the bureau |

Plan (not to scale; top = +y / balcony, right = +x):

```
 y 4.50 +--AC--[blk ptg]--|curt|==== FRENCH DOORS ====|curt|--sw--+
        | bureau                                         nightst |
        | (painting      stool                       +-----------+
   2.86 |_ over it)                                  |   BED     | mirror
        ||                                           | (head E)  | over
        || TV                 chandelier (1.93,2.45) |           | head
        || over                     *                +-----------+
        || radiator                                      nightst |
   0.70 ||_                                           +----------+
        | hooks                                       | WARDROBE |
   0.40 | door      +--cabinet/light--sw--[EN-SUITE DOOR]--------+
        | swing     | 3-gang + a/c remote on this face
      0 +-[DOOR]----+ 0.97                1.99..2.68          3.75
        x 0
```

### Level, ceiling
- **Floor z(world) = 3.05** (first-floor rear level, same as the rear gallery outside the door — no step at the
  door; the "two steps up" are further south on the gallery, toward the front). Evidence: dining ceiling 2.80 +
  0.25 structure; rear elevation (French-door frame top 5.30–5.41 above the ground floor = 2.30–2.36 above this
  floor; balcony deck top 2.9–3.1). **This disagrees with `house.json` stairs.landingZ = 2.85 (15 risers) and with
  `green_bedroom` (front level 3.22 = 2.85 + two steps)** — doubt 1. Everything in this file is relative to the
  room floor, so only one number changes if the level is reconciled differently.
- **Ceiling 2.60, flat** (cornice underside 2.47), measured at the en-suite door from its 1981 leaf (v3:f_0353).
  No slopes, no beams. The balcony deck is 0.05 below this floor, 0.12 below the door cill (see `balcony`).

## 2. Openings

### 2.1 Landing door (W-door, y = 0) — "doors can open and close, pediment, close, hook"
| item | value |
|---|---|
| clear opening | local x 0.105 → 0.867 (0.762), head 1.981; world centre (−0.164, 12.30); wall ≈ 0.12 thick (local y −0.12..0) |
| leaf | light golden-oak veneer **4-panel** (two tall over two short, raised-and-fielded, same pattern as the ground-floor doors), 1981 × 762 × 35; polished-brass lever on a rectangular backplate both sides, lever axis z 1.00 |
| hinge / swing | hinged on the **west** jamb (x 0.105), swings **north into the bedroom** and lies against the navy west wall; brass projecting door stop on the west skirting at y ≈ 0.35. Model open at 90°; shown open 75–90° in f_0173–f_0179, closed in f_0183, f_0475 |
| surround, bedroom side | white gloss architrave 70 wide filling the recess wall to wall, with a **triangular pediment** (§3). Same pediment on the landing side (v3:f_0147, landing spec) |
| threshold | carpet both sides, brass carpet bar under the leaf |
| connects | rear gallery of `landing1`; on axis through the door you see the gallery arch and the two steps (f_0177–f_0179) |

### 2.2 En-suite door (W-south, y = 0.40) — "inside this is a toilet … the toilet door can also open and close"
| item | value |
|---|---|
| clear opening | local x 1.99 → 2.676 (**0.686**, a 2'3" leaf — measured 0.68 twice), head 1.981; world centre (1.68, 12.71); wall 0.10 |
| leaf | same oak 4-panel, 1981 × 686; brass lever handles, privacy turn on the en-suite face |
| hinge / swing | hinged on the **east** jamb (x 2.676), swings **north into the bedroom** toward the wardrobe (f_0187, f_0199, f_0409). Model closed (f_0315, f_0353); it stops ≈ 85° clear of the wardrobe |
| surround | bedroom side: architrave + **pediment** identical to 2.1 (overall 0.83 over architraves, cornice shelf 0.93). En-suite side: plain mitred architrave |
| threshold | polished-brass strip, carpet ↔ tile flush (f_0425, f_0429) |

### 2.3 French doors to the balcony (W-north, y = 4.50) — "you go outside, the door can open"
| item | value |
|---|---|
| wall | ≈ 0.30 thick (inner face world y 16.86, render face 17.16). Ground-floor corrections found the dining reveals ≈ 0.38 deep; use the same wall thickness as the dining north wall once reconciled |
| reveal | plastered opening local x 1.15 → 2.73 (1.58), floor to z 2.40, **jambs and head lined with dark-stained boards** (same stain as the dining joinery, est. #3B2E26, vertical grain, satin), ≈ 0.24 deep from the room face to the frame (f_0237, f_0303–f_0311). No architrave on the room face — the curtains cover the arrises |
| frame | white uPVC, outer 1.64 wide × 2.34 high: world x 0.47 → 2.11 (centre **1.29**), local x 1.12 → 2.76; frame top z 2.34. 70 mm frame members, 70 mm transom at z 1.90–1.97 |
| leaves | a pair, each ≈ 0.75 × 1.83 overall, meeting at local x 1.94; each with a 90 mm mid-rail centred z ≈ 0.95, clear double glazing above and below. Polished-brass lever handles on long backplates on both leaves, both faces, lever z 1.02. **Both hinged at the outer jambs and opening OUTWARD onto the balcony**; the owner opens the east leaf to ≈ 85° (f_0263–f_0297), the west leaf is the slave (shoot bolts). White uPVC cill / threshold upstand 70 mm |
| fanlights | two, side by side over the leaves (z 1.97 → 2.27), each a top-hung opening vent with a white handle on the bottom rail and a slot trickle vent in the head (f_0347, f_0291). Not opened in the video |
| pelmet | see §3 |
| connects | `balcony`; view over the garden to the shed |

No other windows. (The flank wall behind the bed is blank; the room is lit only from the north.)

## 3. Architecture & trim

- **Pediments (both doors, bedroom face)** — measured on the en-suite door, v3:f_0353 / f_0221 / f_0183:
  architrave 70 wide × 20 (flat inner fillet, ogee, outer bead), mitred, outer top at z 2.05; above it a flat
  frieze 30 mm and a moulded **cornice shelf** z 2.08 → 2.12 projecting 40 at the front and 50 beyond each
  architrave (ends cut square against the side walls at the landing door, where the recess is only as wide as the
  surround); then an **open-bed triangular pediment**: raking cornices 45 mm (fillet + ogee) meeting at the apex
  at **z 2.35** (pitch ≈ 27°), flat tympanum set back 15 mm carrying a centred applied **floral-scroll swag**
  (resin appliqué, a central rosette with leaf scrolls each side, ≈ 0.26 × 0.07). All white gloss.
- **Cornice**: white plaster, drop 0.13 (z 2.47 → 2.60), projection ≈ 0.13: cove and ogee with a small enriched
  (egg-and-leaf) band near the top and a plain bottom bead (f_0219, f_0221). Runs on every wall, returns round the
  chimney breast (f_0171, f_0463), round the en-suite block's corner into the recess (f_0177, f_0353) and
  breaks forward round the pelmet.
- **Skirting**: white gloss, 0.17 high × 20, torus + ogee top; returns round the breast (f_0477) and into the
  recess; butts the architraves.
- **No dado rail, no picture rail** in this room (the landing has a dado rail; it stops at the door).
- **Chimney breast** on the west wall, 0.10 proud, square arrises, no fireplace, no vents.
- **Pelmet** ("get the pelmet right", f_0343–f_0349, f_0453): a white painted box over the curtains, local
  x 0.85 → 3.05 (2.20 long), projecting 0.16 from the wall; a plain fascia board z 2.30 → 2.47 with the room
  cornice mitred round it on three sides (front and both returns), so the cornice simply steps forward 0.16 over
  the window. Curtain track inside. Its west end stops 30 mm short of the air-con unit.
- **Ceiling rose** (§8).

## 4. Surfaces & colours

| surface | sampled (tone-mapped) | **estimate** | finish |
|---|---|---|---|
| west wall, both alcoves + breast (the "blue" wall) | #1F2528, #212A31, #192124 (lower wall, clean); #38332E under the downlight | **#2B3B4C** deep navy with a little teal (Hague-/Stiffkey-blue family) | flat matt emulsion, slightly velvety |
| all other walls (door wall, recess, block face, east, north) | #B2AFB3, #AD9D90 (warm-lit), #837B69 (daylight, under-exposed) | **#C9CAD4** pale cool grey with a lilac cast | matt emulsion |
| ceiling | #AE8C69 (warm-lit) | **#F4F2EC** white | matt |
| cornice, rose, pelmet, skirting, architraves, pediments | #AD8965 | **#F4F3EE** white | plaster matt / joinery gloss |
| carpet | #B9997C, #B8A889 | **#CFCBC3** pale silver-grey with a warm cast | deep-pile saxony / plush, shows footprints and sweep marks; fitted wall to wall, also through the recess |
| doors | #793D07 (over-saturated), frame value (134,101,50) | **#B8894F** light golden oak | satin lacquer |
| French-door reveal lining | #585A59 | **#3B2E26** dark walnut stain | satin varnish |
| uPVC | — | **#F4F3EE** | gloss |
| radiator | #A89177 | **#F2F1EC** white | gloss powder coat |

Carpet runs under all furniture; there is no rug.

## 5. Fixed fittings

| # | item | position (local) | size / description |
|---|---|---|---|
| X1 | **Radiator** ("a big radiator") | breast face (x 0.10), y 1.16 → 2.49, z 0.15 → 0.75, 0.10 off the wall | white horizontal designer column radiator, **1.33 × 0.60**: ≈ 21 vertical oval tubes at ≈ 62 mm pitch, double row, rounded tops and bottoms, hidden headers. Chrome angle valves at both bottom ends, white TRV head on the north one (f_0171, f_0175, f_0447) |
| X2 | **TV** ("a big telly at the centre") | breast face, centred on the breast: y 1.165 → 2.395, z 1.20 → 1.91 | ≈ 55-inch flat screen 1.23 × 0.71 × 0.05 on a flat wall bracket, thin black bezel, small logo tab at the bottom centre. **Screen blank** (near-black glossy; do not bake the reflection — it shows the owner) |
| X3 | **Air-con indoor unit** ("aircon") | W-north, x 0.02 → 0.82, z 2.10 → 2.39, 0.22 deep | white wall-mounted split unit with a flat front and a round sensor at its lower right; top 80 mm under the cornice; white condensate trunking not visible (f_0347, f_0157) |
| X4 | Air-con remote in a white wall cradle | W-recess (x 0.97, faces west), y 0.29, z 1.30 → 1.48 | white remote with a small LCD, 0.06 × 0.16 (f_0161–f_0165, f_0483) |
| X5 | **Coat-hook rail** ("hook") | W-west south alcove (x 0), y 0.28 → 0.66, centre z 1.62 | dark-stained board 0.38 × 0.10 with four polished-brass double hooks; hidden when the door is open (f_0181–f_0183, f_0257) |
| X6 | Door stop | west skirting, y 0.35, z 0.08 | brass projecting stop, rubber tip, 70 long (f_0477) |
| X7 | Double socket (white) | W-south, x 1.80, z 0.30 | between the cabinet and the en-suite architrave (f_0431, f_0433) |
| X8 | Bedside sockets | W-east, y 1.95 (z ≈ 0.85) and y 3.62 (z ≈ 0.75) | small white plates either side of the headboard (f_0231, f_0235) |
| X9 | Fan isolator | W-south, x 1.85, z 2.11 | white rectangular plate 85 × 70 just right of the en-suite pediment (f_0195, f_0353) |

Switches are in §8. No fireplace. No visible smoke alarm.

## 6. Furniture (all loose; keep all — the owner names each piece)

| # | piece | footprint (local) | h | description |
|---|---|---|---|---|
| F1 | **Wardrobe** ("there's a mirror in the middle … all these can open and close … small gap") | x 3.23 → 3.75, y 0.46 → 1.66 (1.20 wide × 0.52 deep), back to the east wall, 60 mm gap to the block face on its south side | 2.05 | Edwardian dark walnut / stained-oak wardrobe, satin varnish (est. #3F2E22). Moulded cavetto cornice 80 high overhanging 40; frieze; body in three bays divided by **reeded pilasters**: side bays fixed, each a square **carved panel** (urn with scrolling foliage, 0.26 × 0.30) over a tall plain fielded panel; centre bay = **door 0.42 wide with a bevelled mirror** (0.32 × 1.25), brass escutcheon with a tassel-drop pull on its left stile, hinged right. Base 0.42 high: **two short drawers side by side over one long drawer**, moulded fronts, brass swan-neck plate handles, on a plain plinth (f_0203–f_0215, f_0219) |
| F2 | **Bed** ("beautiful bed, blue bedding") | x 1.67 → 3.72, y 2.08 → 3.54 (2.05 long × 1.46 wide, a 4'6" double), head against the east wall | head 1.45, foot 0.98, mattress top 0.62 | Edwardian dark mahogany bedstead (est. #4A3026). **Headboard**: two square posts with block caps, an arched crest rail with a **pierced scroll-carved cresting** (interlaced C-scrolls), below it seven flat vertical slats with a centre burr-veneer panel. **Footboard** the same design, lower, with a shaped pierced crest, slats and a centre panel, on square legs; deep side rails, 0.30 clear underneath. **Bedding** (neat): dark navy / charcoal duvet and two pillows printed with pale cream-lilac bamboo leaves and small sprays (ground #2A2B3A, leaves #C9C3CF); across the foot a 0.5 m band of large orange-and-cream chrysanthemums on black (ground #1A1A1E, flowers #D98A4A / #E9E2D0) (f_0225–f_0235, f_0329–f_0341, f_0453) |
| F3 | Nightstand, south | x 3.39 → 3.73, y 1.66 → 2.08 | 0.60 | French provincial light-oak bedside cabinet (est. #B8904E): moulded top with rounded corners, one door carved with a bull's-head / scroll cartouche, shaped apron, short cabriole legs. **Door opens** (hinged right, f_0319) |
| F4 | Nightstand, north | x 3.39 → 3.73, y 3.56 → 3.98 | 0.60 | pair to F3 |
| F5 | **Bureau** ("the bureau can open and close, the drawers can also open") | x 0 → 0.42, y 3.20 → 3.96 (0.76 wide), back to the navy wall in the north alcove | 1.00 | 1920s Jacobean-revival dark oak bureau (est. #4A3A28, golden highlights on the mouldings): sloping **fall front** with applied geometric mouldings (two cushion crosses flanking a centre panel) and a tasselled key, opening forward on brass butt hinges to a writing surface on pull-out lopers, **pigeonholes** inside (six vertical dividers + small shelves, f_0245); two full-width **drawers** below with geometric moulded fronts and brass drop handles; on **barley-twist legs** with bun feet joined by a bobbin-turned front stretcher (f_0241–f_0253, f_0463) |
| F6 | Stool | centre (0.42, 3.02), 0.50 × 0.34 | 0.50 | mahogany stool on four slim square tapered legs, drop-in seat in navy fabric with a cream piped edge; stands in front of the breast's north cheek, used with the bureau (f_0171, f_0463) |
| F7 | **TV cabinet** ("this is empty, just for storage") | x 1.07 → 1.66, y 0.40 → 0.85 (0.59 × 0.45), against the block face | 1.02 | Georgian-style flame-mahogany cabinet (est. #6B3324, satinwood stringing): moulded top, **two doors** (flame veneer, cross-banded, brass drop pulls) over **two long drawers** with brass swan-neck handles, reeded quarter columns, bracket feet. Inside the cupboard: burgundy-painted lining and one fixed shelf, empty (f_0433–f_0445). TV remote on top; omit the paper sheet taped to the door |

## 7. Art, mirrors, decor

Privacy: the wardrobe mirror, the octagonal mirror and the TV all reflect the owner — render plain reflections.

| # | item | wall, position (local) | outer W × H | description / texture source |
|---|---|---|---|---|
| A1 | **Landscape painting** ("painting") | W-west north alcove, centre y 3.65, z 1.40 → 2.15 | 0.88 × 0.75 | oil in a moulded gold frame ≈ 70 wide (neutral #C8A84B) with a pale liner: a country lane beside thatched cottages under a large bare-branched tree, cart on the road, flowers in the foreground. Rectify from **v3:f_0255** (720p quad TL (222,472) TR (582,505) BR (570,802) BL (202,790), re-pick on the still t = 254); oblique alternatives f_0463, f_0169. Paint out any figure |
| A2 | **Dark painting** | W-north, x 0.25 → 0.75, z 1.25 → 1.95 (between the west corner and the curtain, under the air-con) | 0.50 × 0.70 portrait | near-black canvas in a narrow gold frame (≈ 30 mm); subject unreadable in every frame (possibly a dark portrait) — use a plain dark abstract (#17181A with faint umber). v3:f_0167 (85..183, 205..337) |
| A3 | **Octagonal mirror** ("a big mirror … get the pattern right") | W-east, centred over the headboard: centre y 2.81, z 1.58 → 2.18 | 0.86 × 0.60 | 1920s oak wall mirror, a rectangle with the four corners cut at 45° (cut ≈ 0.16), frame 55 wide, dark oak (est. #3E2C20) with a beaded inner edge, small carved paterae on the two vertical sides and a carved tablet at the bottom centre; **bevelled plate**; hangs on a chain from one hook, tilted ≈ 3° forward (f_0225–f_0233, f_0325–f_0329) |
| D1 | Bedside lamps (2) | centred on F3 and F4 | h 0.55 | gilt-metal figural lamps: a winged cherub standing on a scrolled rococo base (Ø 0.16) holding up a torch that ends in a **frosted-glass flower shade** (tulip, Ø 0.10). See §8 |
| D2 | Alarm clock | on F4, toward the bed | 0.10 | small black twin-bell clock |
| D3 | On the bureau top | back of F5 | — | clear glass vase with dried **cotton stems** (reaching z ≈ 1.75), a black ceramic oil burner, a glass tea-light on a cork coaster. Omit the lavender sachets |
| D4 | **Curtains** ("curtains can open and close") | W-north, on the pelmet track | drop 2.30 | a pair of full-length lined curtains, pencil pleat: navy-black ground with a dense cream / pale-gold Art-Nouveau stylised-flower repeat (Liberty "Ianthe" type; ground #1E2230, motif #CFC29A), ivory lining. Shown **tied back** at z ≈ 1.00 with navy rope tie-backs with tassels, stacks at x 0.90–1.25 and 2.65–3.00; closed they cover x 0.85–3.05. Pattern source v3:f_0347, f_0345 |
| D5 | Folding chair seen through the glass | balcony | — | omit (see `balcony`) |

Omit: grey soft toy on the floor, slippers, the paper on the cabinet door, towels.

## 8. Lighting and switches

| # | light | position (local) | description |
|---|---|---|---|
| L1 | **Star chandelier** ("beautiful star-shaped chandelier") | ceiling, centre of the main room (1.93, 2.45); world (1.28, 14.81) | brass frame forming an **eight-pointed star** in plan, ≈ 0.75 across the points; strings of faceted crystal beads drape from a small top crown out to the star rim and then swag inward to a bottom finial, making a shallow star-shaped basket ≈ 0.30 deep; six candle lamps inside. Hung on a 0.25 brass rod + chain from a brass ceiling cup: top of the star z ≈ 2.25, bottom z ≈ 1.95 (f_0465–f_0473) |
| L1r | **Ceiling rose** | same centre | white plaster, Ø 0.55: plain centre boss, a ring of radiating acanthus leaves, an outer egg-and-dart band (f_0471, f_0473) |
| L2 | Recessed downlights | ceiling | white-bezel LED downlights Ø 85, warm white. **Six assumed**, two rows of three at x 0.75 and 3.05, y 1.0, 2.45, 3.9; four are positively seen (f_0345, f_0347, f_0461, f_0467) — doubt 6 |
| L3 | **Mermaid wall light** ("a beautiful light here") | W-south, x 1.37, backplate centre z 1.66, shade top z 2.05 | cast gilt-brass sconce: round gadrooned backplate Ø 0.13, an S-scrolled arm formed as a **winged mermaid / siren** holding a torch up in both hands, candle socket and a cream fabric tulip shade (Ø 0.17) with scalloped braid-trimmed rim. Projects 0.28 (f_0187–f_0193) |
| L4 | Bedside lamps D1 | on F3, F4 | each on its own in-line switch ("the lights can turn on and off individually") |
| L5 | Balcony lantern | outside | see `balcony`; probably switched from S3 |

| # | switch | position (local) | controls |
|---|---|---|---|
| S1 | **3-gang** white rocker plate | W-recess (x 0.97, facing west), centre y 0.14, z 1.30 — first thing on your right as you step in | owner works it at f_0160–f_0166 and f_0481–f_0483: all off → downlights on (f_0163) → chandelier on (f_0165); the wall light is on from f_0172. **Gang nearest the room (north) = wall light L3, middle = downlights L2, gang nearest the door (south) = chandelier L1** — the order of the first two is the best reading of the hand position, not certain |
| S2 | 1-gang | W-south, x 1.80, z 1.30 (between cabinet and en-suite door) | **en-suite lights** ("this one turns on and off the toilet light", f_0355) |
| S3 | 1-gang | W-north, x 3.20, z 1.25 (right of the east curtain) | not demonstrated; assumed the balcony lantern (f_0453, t166) |
| S4 | landing switch outside the door | `landing1` | "this one controls the hallway" (f_0149–f_0151) |

## 9. Reference frames

| frames | shows | camera |
|---|---|---|
| v3:f_0157–f_0159, f_0167 (still t166) | whole room from the doorway: French doors, bed, bureau, stool, air-con, dark painting, cabinet side | in the door, looking +y |
| v3:f_0161–f_0165, f_0481–f_0483 | 3-gang switch and remote cradle on the recess wall | in the recess, looking +x |
| v3:f_0169–f_0175, f_0257, f_0447 | TV, radiator, breast and cornice breaks | mid-room, looking −x |
| v3:f_0173 (still t172), f_0177–f_0183, f_0475–f_0479 | landing door, pediment, hooks, door stop, breast cheek | looking −y / down the west wall |
| v3:f_0185–f_0197, f_0315, f_0353–f_0357 | block face: cabinet, mermaid light, switch, socket, en-suite door + pediment, isolator | looking −y |
| v3:f_0203–f_0221 | wardrobe, its drawers, the gap to the wall, cornice, pediment close-up | looking +x |
| v3:f_0225–f_0235, f_0317–f_0341 | bed, nightstands, lamps, mirror, under the bed | looking +x |
| v3:f_0237–f_0239, f_0303–f_0311, f_0343–f_0349 | French doors, dark reveal lining, curtains, tie-backs, pelmet, air-con | at the north wall |
| v3:f_0241–f_0255, f_0463 | bureau (closed, open, drawer), landscape painting, north alcove | looking −x |
| v3:f_0425, f_0427, f_0449–f_0461 | "another view": from the en-suite door and from the north-east corner back to both doors | looking +y / −y |
| v3:f_0433–f_0445 | TV cabinet doors and drawer | looking −y, down |
| v3:f_0465–f_0473 | chandelier from below and from the side, ceiling rose | looking up |
| v2:f_0251 (still t250) | rear elevation: French-door frame position, lantern | garden, looking −y |

## 10. Interactions

| id | what | motion | evidence |
|---|---|---|---|
| I1 | landing door | hinge west jamb, 0 → 90° into the room | opened / closed f_0177–f_0183, f_0475–f_0479 |
| I2 | en-suite door | hinge east jamb, 0 → 85° into the bedroom | f_0187, f_0199–f_0201, f_0357 |
| I3 | French doors, east leaf (and west leaf) | hinge outer jamb, 0 → 85° **outward** | f_0263–f_0297 |
| I4 | curtains | draw along the pelmet track; tie-backs release | "curtains can also open and close" f_0337–f_0349 |
| I5 | wardrobe mirror door; three base drawers | door hinge right 0 → 100°; drawers slide 0.30 | "all these can also open and close"; a short drawer pulled f_0211–f_0213. Inside: a few plain hanging garments |
| I6 | bureau fall front; two drawers | fall rotates forward 0 → 90° about its bottom edge onto the lopers; drawers slide 0.25 | f_0245, f_0249–f_0251 |
| I7 | nightstand doors (both) | hinge right, 0 → 100° | "this one can also open and close" f_0319 |
| I8 | TV cabinet: two doors, two drawers | doors hinge at the outer edges 0 → 100°; drawers slide 0.30 | f_0435–f_0443 |
| I9 | lights | S1 gangs → L3 / L2 / L1; S2 → en-suite; bedside lamps individually | §8 |
| I10 | TV | toggle blank / neutral glow | named only |
| I11 | fanlight vents, air-con flap | optional (not operated) | — |

## 11. Declutter
Soft toy, slippers, paper sheet on the cabinet, lavender sachets, towels, the folding chair visible outside.

## 12. Doubts
1. **Floor level 3.05 vs the stair spec's 2.85.** A floor at 2.85 cannot sit over the dining ceiling at 2.80, and
   the exterior puts this floor at 2.95–3.10. Either the stair has 16 risers (3.04) or the dining ceiling is
   ≈ 2.60. Must be reconciled with `landing1`, `stairs`, `green_bedroom` (3.22) and the rear elevation.
2. **Chimney breast is on the WEST (party) wall here**, with the neighbour's stack visible on that line in
   v2:f_0251, but `dining` has its breast and fireplace on the EAST wall. Flues do not cross the room: one of the
   two is boxing rather than a real breast (or the dining side needs re-checking). The second floor should follow
   the west breast.
3. **Length**: block face → north wall 4.10 (measurements 3.9–4.3). If the en-suite block is deeper or shallower
   keep the east-wall furniture run fixed from the north wall and move the block face.
4. **Recess depth 0.40** (0.33–0.46) and its width 0.97; breast extent y 0.70–2.86 (±0.15) and projection 0.10
   (0.07–0.12).
5. French-door leaf height: frame top 2.34 and transom 1.90 are from the exterior scale and one interior frame
   that over-reads heights by ≈ 10 %; ±0.08. Reveal depth 0.24–0.38.
6. Downlight count and grid; which of the first two gangs of S1 is the wall light; what S3 controls.
7. Dark painting A2 subject; bed size (4'6" assumed, footboard measured 1.40–1.55).
8. En-suite door 686 vs 762 (two measurements say 0.68); its x position ±0.10 (shared with `blue_ensuite`).
9. Wall colours: navy and pale lilac-grey are estimates through an HLG tone-map under mixed daylight and warm
   LED; the owner calls the room "blue".

## Reconciled dimensions (house.next.json)

Added by the phase-2 reconcile step. `spec/house.next.json` is canonical; where the text above differs, the values below win. Reasons and evidence: `spec/RECONCILE2.md` (decision ids in brackets).

- **Floor Z 3.04** (was 3.05) [L1]; ceiling 2.60 (Z 5.64).
- **Polygon**: (-0.65, 12.52) (0.40, 12.52) (0.40, 12.95) (3.10, 12.95) (3.10, 16.86) (-0.65, 16.86) — main room
  **3.75 x 3.91** (was 4.10), entrance recess 1.05 x 0.43 (was 0.97 x 0.40) [P1, P2].
- **Landing door**: wall y **12.39..12.52**, clear x **-0.481..0.281** (was wall face 12.36, x -0.545..0.217).
- **En-suite door**: wall y **12.85..12.95**, clear x 1.34..2.026 (unchanged in x).
- **Rear wall**: inner face 16.86, outer (render) face **17.36** [E1]. French-door frame x 0.47..2.11 unchanged; with a
  0.24 reveal the frame stands about 0.19 behind the render.
- **Transform** (world y): items on or keyed to the south walls +0.19 (switch plates → recess east wall x 0.40, y 12.69,
  and block face y 12.95; TV cabinet F7, socket X7, wall light L3 on the block face); items keyed to the north wall
  unchanged (bureau, French doors, pelmet); west wall: breast → y 13.20..15.30 (`blue_breast_w`), TV centre y 14.25,
  radiator y 13.6..14.9; ceiling rose / chandelier → (1.28, 14.90).
- **East-wall run moves as one piece, +0.19** [verification INV-02] — wardrobe, nightstand, bed, nightstand stand side
  by side with no gaps (v3:f_0203–f_0223), so they shift together with the block face (the first reconcile moved only
  the wardrobe and left it overlapping the south nightstand by 0.19):

  | piece | world y | world x |
  |---|---|---|
  | wardrobe F1 | **13.01..14.21** (0.06 clear of the block face 12.95) | 2.58..3.10 |
  | south nightstand F3 (+ cherub lamp) | **14.21..14.63** | 2.74..3.08 |
  | bed F2 | **14.63..16.09** | 1.02..3.07 |
  | north nightstand F4 (+ cherub lamp, clock) | **16.11..16.53** (0.33 clear of the north wall) | 2.74..3.08 |

  With them: octagonal mirror A3 centre y **15.36** (over the headboard), bedside sockets X8 at y **14.50** and
  **16.17**, the two bedside lamps D1 on their nightstands.
- The west "chimney breast" is modelled as a first-floor feature only [S3].

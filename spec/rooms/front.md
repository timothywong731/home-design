# front — front forecourt / parking area (street side, y < 0)

Source: v2 frames f_0943–f_0973 (the owner opens both street doors and steps out: "you can see the two cars
in here … brick walls … and the front I got a flag, that's how it looks like … both doors can open … bricks
and then I got Victorian tiles"), v4 frames f_0024–f_0066 (looking down from the first-floor front windows:
"you can see the flag outside, there's a UK flag … you can see the two cars in here and the surrounding
area"). v1 frames 1–47 never leave the house (they show the street doors from the inside only), so there is
no night view of the outside. Full-res stills and crops are in `reference/work/p2_front_ext/`
(`v2_tNNN.jpg` = v2 frame f_(NNN+1), `v4_tNN.jpg` = v4 frame f_(NN+1)).

The street face of the house itself (bay, door screen, canopy, upper floors, roof) is specified in
`spec/phase2/front_elevation.md`; this file is the ground in front of it.

**Dimension confidence.** Widths (X) are tied to `house.json` (party walls, door, bay) and are good to
±0.10 m. The forecourt depth (Y) comes from the two cars of known length parked nose-out between the house
and the back of the footway: ±0.30 m. Paving module ±10 mm (sandal 0.27 m long = 1.7 courses, v2:f_0973).
Wall and pier heights from brick courses (75 mm): ±0.08 m. Footway/road widths are backdrop estimates
(±0.5 m). Car positions ±0.25 m, yaw ±5°.

## 1. Shape & dimensions

Frame: **the BRIEF world frame is used directly** (no local frame): +X to the right walking into the house,
+Y into the house, so the street is at −Y. Standing in the street doorway looking out you face −Y; the buff
brick wall is on your **right (−X, west)**, the grey car is immediately to your **left (+X)**, the white car
beyond it, the bins at the far left against the house.

| element | world extent | notes |
|---|---|---|
| house face (bay front + door screen, one plane) | y = −0.12, x −0.72 … 4.15 | outer face of `w_front_vest` / `w_front_bay`; bay east return runs back to y 0.74 at x 4.15 |
| **forecourt paving** (block paving) | x −0.72 … 4.42 (5.14 m), y −5.20 … −0.12 (5.08 m) | one open rectangle, no gate, no front wall, no step; ≈ 26 m² |
| unmarked strip east of the party line | x 4.42 … ≈ 4.90, y −5.20 … −0.12 | same level, **no boundary marker of any kind on the east side**: the bins straddle the line and the neighbour's dark paving starts somewhere in this strip (v4:f_0052). Model our block paving out to x 4.90 and stop the modelled ground there (or continue as plain dark asphalt) |
| west boundary wall | inner face x −0.72, outer face x −0.935 (215 thick), y −4.87 … −0.12 | buff brick, timber planter troughs on top; butts the house at the party line just west of the door frame |
| wall-end pier | x −0.99 … −0.66, y −5.20 … −4.87 (0.33 square) | at the back of the footway, flat concrete cap |
| back of footway = plot edge | y = −5.20 | blocks meet the public paving flush, irregular cut line, no edging kerb, fully open (vehicle crossover) |
| public footway | y −7.20 … −5.20 (2.0 m) | large grey paving flags, backdrop |
| kerb | y −7.35 … −7.20 | 150 mm granite/concrete kerb, dropped along the frontage |
| carriageway | y ≈ −15.3 … −7.35 (≈ 8 m) | asphalt, backdrop; opposite footway and house fronts beyond (≈ y −22) |

**Levels** (Z = 0 is the vestibule tile floor):

- Street-door threshold: low white/aluminium uPVC sill, top at Z ≈ 0.00, ≈ 70 mm deep in Y.
- Paving against the house: **Z = −0.06** (one 60 mm drop off the threshold, v2:f_0961, f_0973). There is no
  step, plinth or mat well.
- Paving at the back of the footway (y −5.20): **Z = −0.14** (assumed even fall of ≈ 1:65 to the street;
  not measurable — a flat plane at −0.06 … −0.10 is equally defensible).
- Footway: −0.14 at the plot edge to −0.18 at the kerb; kerb upstand 0.10 (0.025 where dropped);
  carriageway channel ≈ −0.28.
- No ceiling: sky. Things overhead near the house: the porch canopy (soffit Z 2.62, x −0.85 … 1.10,
  projecting to y −0.55), the bay cornice (Z 2.90–3.10, projecting to y −0.30), the flag pole.

Plan (not to scale; top of page = house / +Y, right of page = +X):

```
        party line                                   bay east return   party line
  x: -0.94 -0.72   -0.62      0.62 0.68 1.07 1.22 ......... 3.88 4.15  4.42     4.90
        |  |  [== street doors ==][pil][j][==== 4-light bay ====]  |     :
 y -0.12+--+--+------------------+---+-+--------------------------+--+- - : - - - -
        |W |   canopy over (to y -0.55)   ^flag bracket (0.95,-0.15)  [GREY BIN ] :
        |A |                                                         [BLUE BIN ] :
        |L |  path     +-----------+  gap                             [caddy]    :
        |L |  0.5-0.9  | GREY      |  0.70  +-----------+               []covers  :
        |  |  clear    | hatchback |        | WHITE     |               []        :
        |+ |           | 3.89x1.70 |        | city car  |                         :
        |p |           | nose-out  |        | 3.46x1.62 |              (neighbour's
        |l |           |  (0.78,   |        |  (3.15,   |               planter and
        |a |           |   -3.10)  |        |   -3.43)  |               dark paving)
        |n |           +-----------+        |           |
 y -4.87|t |                                +-----------+                         :
        [PIER]- - - - - - - back of footway  y = -5.20 - - - - - - - - - - - - - -
 y -5.20      F O O T W A Y   (flags, 2.0 m)        (o) cover
 y -7.20 ====(tree)=========== kerb ===================(lamp post)================
              C A R R I A G E W A Y
```

## 2. Openings (what the forecourt connects to)

| id | where | size | notes |
|---|---|---|---|
| `d_street` street doors | house face, centre (0.00, −0.06) | clear 1.18 × 2.03, frame 1.24 × 2.57 | the only way in. **Both leaves swing OUT over the forecourt** (correction to `house.json`, which assumed inward): hinges on the outer jambs at x ±0.59; see §10 and `front_elevation.md` §2.1. Open leaves sweep quarter-circles of radius 0.59 centred (±0.59, −0.12): keep that paving clear |
| plot edge | y = −5.20, full width | 5.14 m open | no wall, gate, chain or kerb between forecourt and footway; this is the vehicle entrance for both cars |
| east side | x ≈ 4.42 | open | no wall or fence; see §1 |
| bay windows | house face x 1.22 … 3.88, Z 0.62 … 2.70 | — | not opened in any video; see `front_elevation.md` §2.2 |

No side gate at the front: this is a mid-terrace frontage (attached houses both sides), the "side entrance"
the owner mentions in v2 is at the rear.

## 3. Architecture & trim

### 3.1 West boundary wall (x −0.935 … −0.72)
- **Buff / yellow stock facing brick**, 215 mm (one brick) thick, **stretcher bond** on the visible face,
  flush light-buff mortar joints 10 mm. Coursing 225 × 75.
- Height above the paving: **9 stretcher courses (0.675) + 1 soldier course (bricks on end, 0.225) =
  0.90 m**. The soldier course is the top course and is mostly hidden behind the planter boards
  (v2:f_0949, f_0951; crop `crop_pier_t948.jpg`).
- Length 4.75 m from the house face to the pier (≈ 21 stretchers). It dies into the house face at the
  party line, immediately west of the white square rainwater pipe that comes down beside the door frame.
- The far (west) face belongs to the neighbour's forecourt and is the same brick; no coping (the planter
  troughs cover the top).

### 3.2 Pier at the footway end
- 1½-brick square, **0.33 × 0.33 m**, same buff brick, 13 courses = **0.975 m**, alternate courses showing a
  stretcher + header on each face (v2:f_0951, v4:f_0065).
- **Cap**: flat cast-concrete / reconstituted-stone pier cap, 0.40 × 0.40 × 0.075, 35 mm overhang all round,
  very shallow four-way weathering (reads as flat), weathered grey-buff. Top of cap **Z ≈ +0.95** above the
  local paving (≈ 1.05 m tall overall).
- The pier is centred on the wall centreline, so it projects ≈ 55 mm proud of the wall face on our side.

### 3.3 Paving
- **Tumbled concrete block paving ("Tegula"-type setts)**: all blocks 160 mm wide, in three lengths
  **120 / 160 / 240 mm**, 50–60 thick, rounded/tumbled arrises, sand-filled joints 3–5 mm that have gone
  dark with moss and dirt.
- Laid in **straight courses 160 mm wide running parallel to the house front (along X)**, lengths mixed at
  random within each course so that cross joints never line up for more than two courses (v2:f_0947, f_0973,
  v4:f_0049 — `crop_between_cars.jpg`). 32 courses from the house to the plot edge.
- Cut blocks against the house plinth, the wall and the pier; no soldier border, no drainage channel, no
  inset mat.
- Colour mix is a three-tone blend, roughly 55 % warm light grey-buff, 25 % mid grey, 20 % brindle
  (pinkish-brown), randomly distributed, with oil/tyre darkening in the two wheel tracks of each car and
  green-black algae in the joints along the wall and the house plinth.
- Leaf litter collects in the corner by the pier and along the wall foot (declutter: omit or a few leaves).

### 3.4 Footway, kerb, road (plain backdrop)
- Footway: **large rectangular paving flags** (mixed 600 × 900 and 600 × 600 concrete/York-type slabs, some
  replaced so the greys do not match), laid in courses parallel to the kerb, 3 flags deep = 2.0 m. One small
  square iron cover in the flags roughly in front of the gap between the cars (≈ (1.9, −5.7)).
- Kerb: 150 mm wide grey granite/concrete kerb with a narrow channel; a white painted line on the
  carriageway ≈ 0.3 m off the kerb across the frontage (crossover / bay marking) — plain white line only.
- Carriageway: dark asphalt, patched. Cars parked on it are NOT modelled.
- Street furniture seen (optional, low detail): a slim **black steel lamp column** ≈ 6 m high at the kerb
  at ≈ (3.3, −7.0) with a small blank sign plate at 2.2 m; a **young street tree** (trunk Ø 0.15, crown from
  3 m, ≈ 7 m tall, sparse yellow-green autumn leaves) in a pit at the kerb at ≈ (−0.6, −6.9), i.e. straight
  out from the pier. A second larger tree stands further east (≈ x 9).

### 3.5 Neighbouring frontages (massing only)
- West (−X): beyond the brick wall a similar forecourt with dark paving, a clipped hedge and shrubs;
  model nothing more than a ground plane (dark grey) and, optionally, a 1.0 m green hedge block along the
  footway edge. The attached house on that side is red brick at ground floor with a cream-painted first
  floor and keeps its open arched porch — massing box only, no number, no door detail.
- East (+X): open dark-paved forecourt; a dark brown corrugated-steel raised planter (≈ 2.0 × 0.9 × 0.45)
  about 1 m in from the footway at ≈ x 4.6 … 6.6, y −4.4 … −3.5 — optional plain box. The attached house on
  that side is red brick with white stone bands and a canted bay under a dark-tiled gable — massing only.
- Opposite side of the street: a continuous row of similar gabled two-storey-plus-attic houses in red
  brick and white render ≈ 22 m away — a flat backdrop card or simple extruded blocks, no detail.

## 4. Surfaces & colours

Daylight, overcast, everything wet after rain; the phone HDR lifts shadows and the white balance is close to
neutral, so the samples are much nearer the truth than in the night video. "Sampled" = median sRGB of a
patch in the named still; "true" = estimate dry, under neutral light.

| surface | sampled (still) | true colour / material |
|---|---|---|
| block paving, light blocks | #B8B5A4 (v2:f_0949), #B0AC9E (v2:f_0973), wet from above #817B71 (v4:f_0049) | warm light grey-buff concrete **#B3AE9F**, fine exposed aggregate, matt, roughness 0.9 |
| block paving, mid-grey blocks | p15 of the same patches #837E69 | **#8C887C** |
| block paving, brindle blocks | pinkish blocks in v2:f_0947, f_0973 | **#A98C7C** (muted pink-brown) |
| paving joints | #585549 | dark moss/dirt **#4B4A40**, 4 mm, slightly recessed |
| boundary wall brick | #CAB996 (v2:f_0949), shadow side #A89975 | buff/yellow stock **#C9B58C**, smooth-faced with light drag texture and small dark pits, slight brick-to-brick variation (±6 % value); mortar **#CFC6B0** |
| pier brick | #A59373 (wet, v2:f_0951) | same brick, a little dirtier: **#BFA982** |
| pier cap | #746D63 (wet) | weathered cast stone **#9A958A**, darker algae streaks |
| planter troughs | #4F4948, #665A56 (v2:f_0949) | dark brown-black stained softwood **#4A3F3A**, weathered grey on the top edges (#8C857C), matt |
| planter foliage | #A3B48D (mixed with flowers) | fresh mid-green small leaves **#6E9450**; flowers violet-blue **#6B5BB5** |
| house walls (all render, stone and joinery on the front) | #C4C4C0 – #E8E8E3 | brilliant white masonry paint **#F2F2EE**, smooth, slight sheen on joinery (see `front_elevation.md` §4) |
| footway flags | light #B0AA9E, dark/wet #86837F (v4:f_0049) | mixed concrete flags **#A9A59B** and **#8E8B86**, joints dark |
| kerb | — | grey granite **#8A8A88** |
| carriageway | #ACA8A4 is wet sky sheen | asphalt **#55565A**, lighter patches #6A6A6C; road line white #E6E6E2 |

## 5. Fixed fittings

- **Planter troughs on the wall**: a continuous run of rough-sawn timber troughs fixed along the top of the
  wall for its whole length (4.75 m, made of ≈ 4 boxes butted end to end). Section ≈ 0.26 wide × 0.25 high;
  the long sides are made of **vertical boards ≈ 95 mm wide** (pallet / feather-edge style, slightly uneven
  top line). The inner side board laps ≈ 70 mm down over the face of the soldier course, so on our side the
  timber runs from Z ≈ +0.83 to +1.08 above the paving and stands ≈ 25 mm proud of the brick face. The
  troughs stop ≈ 30 mm short of the pier.
- **Access covers** (optional detail): two rectangular recessed concrete/steel inspection covers,
  ≈ 0.60 × 0.45 each, light grey (#949490), set flush in the paving near the east edge at ≈ (4.45, −2.3) and
  (4.45, −3.0), long side along Y (v4:f_0049, f_0052).
- On the house face at ground level (detailed in `front_elevation.md` §5): weatherproof outdoor socket box
  under the bay sill, video doorbell on the pilaster, white rainwater pipe beside the door.
- No gate, post box, house number plaque, bollard or chain. (The address is lettered on the door transom —
  **never reproduce it**; the transom is plain frosted glass.)

## 6. Furniture / movable objects

### 6.1 The two cars (generic, **no number plates, no badges, no stickers**)
Both are parked **nose-out** (bonnet toward the street, tailgate toward the house), side by side, slightly
skewed with their noses turned a few degrees toward the brick wall.

| | grey car (nearer the door) | white car (nearer the bins) |
|---|---|---|
| type | B-segment 5-door hatchback, early-2010s Japanese supermini shape: short sloping bonnet, steeply raked windscreen, rising waistline, roof spoiler over the tailgate, wrap-round tail-lamps | A-segment 5-door city car, mid-2010s: very short overhangs, upright tail with an **all-glass frameless tailgate**, tall vertical tail-lamps, blacked-out C-pillar |
| size L × W × H | **3.89 × 1.70 × 1.51 m**, wheelbase 2.51, track 1.47 | **3.46 × 1.62 × 1.46 m**, wheelbase 2.34, track 1.42 |
| wheels | 15-inch, tyre Ø 0.60, five-twin-spoke alloys, dark grey with machined faces | 15-inch, tyre Ø 0.57, black alloys with machined faces |
| paint | **dark metallic grey** — sampled #4E4C4F (side, v2:f_0945), #85848B (wet roof reflecting sky); true **#4A4B50**, metallic 0.8, clearcoat | **solid white** — sampled #E5E6E7; true **#F0F1F1**, clearcoat |
| details to keep | privacy-tinted rear glass (#15171A), black short roof aerial at the rear of the roof, body-colour door handles and mirrors, chrome strip on the tailgate (plain), red reflectors low in the rear bumper, clear/red tail-lamps | **orange-red door-mirror caps** (#D2452F), black tailgate glass, black C-pillar and window frames, red tail-lamps (#C9281E), black lower bumper insert, body-colour door handles |
| blank out | plate recess = plain body colour or blank dark panel; no maker's emblem, no model script, no "hybrid" tag | plate recess blank; no emblem; no country sticker |
| position: centre (x, y) | **(0.78, −3.10)** | **(3.15, −3.43)** |
| yaw | nose points −Y turned **5° toward −X** | nose points −Y turned **6° toward −X** |
| resulting corners | tail at y ≈ −1.17 (rear-west corner ≈ (0.11, −1.09): 0.83 m from the wall, 1.0 m out from the threshold), nose at y ≈ −5.04; nose-west corner ≈ 0.50 m from the wall | tail at y ≈ −1.71, nose at y ≈ −5.15 (reaches the back of the footway) |
| clear gaps | 0.5–0.85 m path between the car and the brick wall (the walking route from the door to the street); 0.70 m between the two cars | ≈ 0.45 m between its east flank and the unmarked east edge |

Both stand on the paving at their local level (wheels at Z ≈ −0.08 … −0.13). Windows up, doors shut,
interiors dark and simple.

### 6.2 Bins (keep: a permanent feature of the frontage; plain, no lettering)
Standing in a row against the house at the east end, beyond the end of the bay, fronts facing west:
- **Wheelie bin, dark grey** (240 L: 0.58 wide × 0.73 deep × 1.07 high, two 200 mm wheels on the back,
  hinged lid): centre (4.21, −0.45), 0.58 dimension along Y. Body and lid **#3A3B3F**.
- **Wheelie bin, navy blue**, same size: centre (4.21, −1.06). Body and lid **#2F3550** (sampled #343746,
  lid #6B7087 wet).
- **Food caddy**, small grey kerbside caddy 0.32 × 0.40 × 0.40 with a carrying handle and a paler lid:
  centre (4.40, −1.60), just clear of the white car's rear-east corner. Body **#6F7A7C**, lid #96A0A5.
They overlap the party line by ≈ 0.15 m (seen in front of the neighbour's brick pier in v2:f_0953, f_0971).

## 7. Decor: flag, planting

### 7.1 Flag ("in the front I got a flag … a UK flag")
- **Bracket**: white powder-coated cast-aluminium 45° wall bracket (base plate ≈ 0.07 × 0.11, tube socket
  ≈ 0.10 long with a thumbscrew), screwed to the **east edge of the fluted pilaster between the door and the
  bay, just under its capital**: base at **(0.98, −0.15, Z 2.38)** (v2:f_0954, f_0956, f_0964).
- **Pole**: white aluminium tube Ø 25 mm, **1.80 m** long, leaving the wall square to the façade (pointing
  −Y) at **45° above horizontal**; silver-grey ball finial Ø 45 mm at the tip. Tip at ≈ (0.98, −1.42, 3.65).
  It clears the east end of the porch canopy gutter by a few centimetres.
- **Flag**: Union Flag ≈ **0.91 × 1.52 m** (3 × 5 ft) printed polyester, fixed by its 0.91 m hoist to the
  top half of the pole (two clips), hanging limp: the fly falls in soft vertical folds, lowest corner at
  Z ≈ 2.55, roughly above x 0.9 … 1.3, y −1.3 … −0.6. The lower fly corner is slightly frayed. It hangs in
  front of the first-floor bay apron when seen from the street, and is seen from above through the
  first-floor windows (v4:f_0034, f_0062–0065).
- Colours (a little sun-faded): red **#C23B3A**, blue **#2B3A78**, white **#F0EFEC**. Standard Union Flag
  geometry; cloth simulated or modelled as a draped mesh with a two-sided material. A slow sway animation
  is welcome but not required.

### 7.2 Planting on the wall
- The troughs are filled end to end with **trailing bellflower (Campanula)**: a dense cushion of small
  round fresh-green leaves ≈ 0.20 m high above the trough rim and spilling 0.10–0.25 m over both sides,
  sprinkled with small 5-pointed **violet-blue** star flowers (Ø ≈ 25 mm), densest along the top and the
  outer edge. Overall the wall reads as brick 0.83 m, a dark timber band, then a soft green-and-purple top
  to ≈ 1.25–1.30 m. Model as a low-poly cushion mesh with an alpha-card or particle scatter of leaves and
  flowers; from the first floor it reads as a continuous green ribbon ≈ 0.45 m wide (v4:f_0063).
- One or two weeds in the paving joints at the wall foot (omit).
- No other planting, pots or lawn in the forecourt.

## 8. Lighting & switches

- **No light fittings in the forecourt itself** (no bollards, wall lights or floodlights on the wall).
- The only owner lighting over the forecourt is the **three recessed downlights in the porch canopy
  soffit** (white bezels Ø ≈ 90 mm, in a row at y ≈ −0.34, x ≈ −0.38 / 0.00 / +0.38, Z 2.62, warm white),
  the "outside lights" of `vestibule.md` §7. They were lit in the night video (seen through the transom,
  v1:f_0012–0016) and are off in daylight (v2:f_0959). **Switching:** the owner says of the 3-gang switch in
  the hall (v2:f_0998–f_1011) "this one also controls the porch light, the vestibule … this one controls the
  hallway … the other one goes to the first floor"; no switch is ever shown operating the canopy lights on
  their own. `spec/phase2/ground_corrections.md` (switch table and V2/V3) assigns the canopy lights, by
  assumption, to the **right-hand (south) rocker of the hall 3-gang at (0.65, 3.29, 1.27)** together with
  the vestibule lantern and recess downlights; use that. See doubts.
- A small black security floodlight / camera unit sits on the bay corner above the east end of the canopy
  (≈ (1.05, −0.25, 2.95)); model as an unlit black box or omit.
- Street lighting: the lamp column at the kerb (backdrop). For the daylight bake use the sky only; if a
  night mode is ever added, one warm-white (≈ 3000 K) source at 6 m at (3.3, −7.0).
- Baking note: the forecourt is open to the sky on the −Y side of the model; the façade gets no direct sun
  in the reference footage (overcast), shadows are soft.

## 9. Reference frames

| frame | still | shows | camera |
|---|---|---|---|
| v2:f_0945 | `v2_t944.jpg` | grey car tail three-quarter view, white car beyond, paving pattern, street | in the doorway (0.1, −0.2, 1.5), looking −Y/+X and down |
| v2:f_0947 | `v2_t946.jpg` | path between car and wall, wall + planter + pier, west door leaf open outward with its letter flap | doorway, looking −Y |
| v2:f_0949 | `v2_t948.jpg` | wall brick bond, soldier course, planter boards, bellflowers, pier and cap, paving close-up | (−0.2, −0.9, 1.4) looking −Y, down |
| v2:f_0951 | `v2_t950.jpg` | pier courses, path narrowing to the street, street tree, opposite houses (backdrop) | (−0.2, −1.2, 1.6) looking −Y |
| v2:f_0953, f_0954 | `v2_t952.jpg`, `v2_t953.jpg` | bay plinth, sill, outdoor socket, pilaster, doorbell, flag bracket; bins at the east end | (−0.1, −0.7) looking +X along the façade |
| v2:f_0955–f_0957 | `v2_t954.jpg` … `v2_t956.jpg` | flag and pole from below, canopy end, upper façade | (−0.2, −0.9, 1.5) looking +X/+Y and up |
| v2:f_0961 | `v2_t960.jpg` | threshold, 60 mm drop to the paving, paving at the door | (0.3, −1.0) looking +Y |
| v2:f_0963–f_0965 | `v2_t962.jpg` … `v2_t963.5.jpg` | both leaves open outward; canopy, pilaster, grey car's tail corner at the bottom right | (0.3 … 0.6, −1.6) looking +Y |
| v2:f_0969 | `v2_t968.jpg` | grey car tail and the path, wall, pier | doorway looking −Y |
| v2:f_0971 | `v2_t970.jpg` | strip between house and car tails, bins at the far end, white car's tail, bay plinth and socket | (−0.4, −0.4, 1.5) looking +X |
| v2:f_0973 | `v2_t972.jpg` | paving module against a 0.27 m sandal, threshold, grey car bumper ≈ 1.0 m out | doorway looking straight down |
| v4:f_0034 | `v4_t33.jpg` | flag from above, porch roof slates, pier, footway | first-floor window over the porch (0.0, 0.8, 4.7) looking −Y |
| v4:f_0049 | `v4_t48.jpg` | **plan view of both cars**, gap between them, paving courses, back-of-footway line, flags, kerb, lamp column | first-floor bay front window (≈ 2.0, −0.1, 4.8) looking down |
| v4:f_0051–f_0053 | `v4_t50.jpg`, `v4_t51.jpg`, `v4_t52.jpg` | east side: bins, caddy, access covers, neighbour's planter, open boundary; street backdrop | same window looking −Y/+X |
| v4:f_0062–f_0065 | `v4_t61.jpg` … `v4_t64.jpg` | west side: whole wall with planting and pier, grey car in plan, flag and pole, tree at the kerb, footway and road | bay front window (≈ 3.2, −0.1, 4.8) looking −X/−Y |

Crops: `crop_pier_t948.jpg` (pier, soldier course, planter), `crop_between_cars.jpg` and `crop_blocks_a.jpg`
(paving courses from above), `crop_wall_t62.jpg`, `crop_t62_wall.jpg` (wall from above).

## 10. Interactions

| object | action | notes |
|---|---|---|
| **Street doors** (`d_street`) | each leaf opens **outward** to ≈ 100° and closes ("both doors can open … the one can close, the other one can also close") | west leaf (letter plate) is the first to open, by its lever handle; the east leaf is the slave leaf with its own lever. Pivots at (−0.59, −0.12) and (+0.59, −0.12). Leaves need 0.6 m of clear paving; the grey car's tail corner is 1.0 m out, so there is no clash. |
| Flag | optional idle sway | not operated by the owner |
| Letter plate flap on the west leaf | optional | not operated in the video |
| Cars, bins | none | static props (bin lids are not opened) |
| First-floor windows seen opening over the forecourt | see the `green_bedroom` spec and `front_elevation.md` §2.4 | porch window, bay front left and right casements open outward |

## Doubts

1. **Forecourt depth 5.08 m (plot edge at y −5.20)** rests on the grey car being 3.89 m long with ≈ 1.05 m
   behind it and ≈ 0.15 m in front of it level with the pier (v4:f_0062–0065). Range 4.8–5.4 m. If changed,
   keep the car-to-house gaps and move pier, plot edge and footway together.
2. **East side has no physical boundary.** The party line (x ≈ 4.42) is taken as the plot edge; the bins
   and the paving run ≈ 0.5 m past it. Whether that strip is ours or the neighbour's is not knowable from
   the video.
3. **Wall thickness and exact x**: the inner face is put at x −0.72 so that the open west door leaf (pivot
   x −0.59, 0.59 m long) lies just clear of it, as it does in v2:f_0947; the wall is assumed one brick thick
   and centred near the party line. ±0.05 m.
4. **Wall height**: 9 stretcher + 1 soldier course counted obliquely (could be 8 + 1 = 0.825 m); pier 13
   courses (12–14).
5. **Paving block size**: 160 mm courses is solid; the 120/160/240 length set is the common product range
   and matches the look, not individually measured. Fall toward the street assumed.
6. **Car yaw** (5–6°) and exact centres are from oblique views through an ultrawide lens; the cars are of
   course movable, so positions are "as filmed".
7. **White car size**: identified by shape as an A-segment city car (3.46 m); if it is in fact the larger
   crossover version of the same model line (3.70 × 1.74 m) the gaps shrink by ≈ 0.1 m each side.
8. **Canopy-light switching** is not demonstrated (see §8); to be agreed with the ground-floor corrections
   (vestibule / hallway switch mapping).
9. Footway and carriageway widths, lamp column and tree positions are backdrop estimates only.
10. The flag: pole length (1.8 m) and flag size (3 × 5 ft) are the standard kit sizes that fit the
    proportions; bracket height ±0.1 m.

## Reconciled dimensions (house.next.json)

Added by the phase-2 reconcile step. `spec/house.next.json` is canonical; where the text above differs, the values below win. Reasons and evidence: `spec/RECONCILE2.md` (decision ids in brackets).

- **Not mid-terrace on the east** [E3]: there is a side alley about 0.9 wide beyond the east wall of the main house
  (outer face x **4.53**). The forecourt paving is modelled to x 4.53 with a `forecourt_alley_mouth` strip to x 5.43
  (the "0.5 m past the party line" of this spec); x 4.42 is not a party line.
- **First floor is at Z 3.42**, not 3.23 [L2]: first-floor window sills Z **4.12** (bay) / **4.20** (west window), heads
  **5.97 / 6.00**; the porch lean-to abuts at Z **3.90**.
- **Roof** [E4]: main eaves gutter about Z **6.50**, ridge Z **9.14** at y 5.00, pitch 30 degrees; bay-gable apex
  Z 7.70. (`front_elevation.md` section 1.2 / 6 values of 5.95, 9.0, 42 degrees are superseded.)
- First-floor bay window frame x 1.50..3.56 (interior measurement; this elevation read 1.35..3.70); cheek windows
  y 0.19..0.67 as `front_elevation.md`.
- Street doors swing outward (`d_street.swingInto = outside`), threshold 0.06 above the paving: unchanged.
- Forecourt, wall, pier, cars, bins, flag: unchanged (`exterior.zones`, `boundaries`, `features`).

# Interaction contract — Blender tags → GLB extras → viewer

The viewer lets the visitor operate things: doors, cabinet fronts, drawers, fridge, toilet seat,
bins, taps, hob, TVs, clocks, curtains, light switches. The Blender side only **tags** objects;
`docs/js/interact.js` does every animation. One custom property carries everything:

```python
from lib import interact as IX
IX.tag(obj, 'hinge', g='kitchen.base.sink.d1', label='Cupboard', p=(x, y, z), a=(0, 0, 1), deg=-95)
```
`IX.tag` validates and writes `obj['ix'] = '<json>'`; the exporter passes it through as glTF node
extras untouched. All points / vectors are **Blender world coordinates in metres** (Z up) of the
object *as modelled*; the viewer converts with (x, z, -y).

## Rules for tagged objects
- A tagged object is its own Blender object (never joined into a carcass), named `<room>.<what>`,
  added with `ctx.add(..., lm='dynamic')` unless it is a door leaf (those may stay static).
- Everything that moves together shares one group id `g` (a door front + its handle + its glass;
  a tap lever + nothing else). `IX.tag_many([front, pull], 'hinge', g=..., ...)` tags several.
- The **modelled pose is state 0**. State 1 is the toggled pose. A door modelled standing open is
  still state 0; give it `on=True` so the tooltip says "Close".
- What is revealed must exist: a cupboard that opens needs a carcass with a real interior
  (`P.cabinet_carcass(open_front=True, shelves=n)`), a fridge needs shelves and door bins, a bin
  needs a rim and liner. Interiors are `lm='dynamic'`.
- Nothing may collide through neighbours in state 1 (handles into the next door, a fridge door
  into the housing, a drawer through the plinth). Check both states in a render:
  `IX.pose(objs_in_scene, state=1)` applies state 1 in Blender for a preview render.
- Budget: interiors are simple (boxes, a few shelves, a handful of props).

## Types (`t`)
| t | params | viewer behaviour |
|---|---|---|
| `hinge` | `p` point on the axis, `a` axis (default `(0,0,1)`), `deg` signed angle state 0→1 (right-hand rule about `a`), `dur` s (default 0.7) | eased rotation about the axis |
| `slide` | `d` (dx, dy, dz) translation state 0→1, `dur` | eased translation (drawers 0.35 m out, pocket door, sash) |
| `show` | `when` 0 or 1, `fx` one of `none water flame tv glow` | visible only in that state. `water`: stream mesh, UVs scroll downward along V. `flame`: flickering additive blue flame. `tv`: screen quad (0..1 UVs, +V up) plays an animated picture. `glow`: fades emissive in |
| `trigger` | — | does not move; clicking it toggles its group (tap body, hob knob, TV set, bin pedal, remote) |
| `clock` | `hand` `h` `m` or `s`, `p` centre of the dial, `a` unit axis pointing **out of the dial toward the viewer** | hand is modelled pointing at 12; the viewer turns it clockwise to the visitor's local time, continuously. No group needed |
| `light` | `rooms` list of room ids, `circuit` optional | a switch plate. Toggles those rooms between the lights-on and lights-off bake and turns their lamp emissives off; with `circuit`, only that circuit of them (see Circuits) |
| `lamp` | `rooms` optional, `circuit` optional | a table lamp / wall light that can be clicked: same as `light` when `rooms` is given, else its own circuit when Cycles lamps belong to it (see Circuits), else toggles only its own emissive parts (group `g`) |

Common optional keys: `g` group id (default: the object name), `label` short tooltip noun
("Fridge", "Hot tap", "Oven"), `on` True when state 0 is the open/on state, `reach` metres within
which Space / E operates it (default 1.6), `blocks` opening id of house.json for door leaves: the
doorway is passable only while the leaf is open, `excl` list of group ids whose swings cross this
one: the viewer shuts them before this group opens (tag both sides; `IX.pose` ignores it),
`needs` group id (or list) this group rests on: opening it opens that group first, closing that
group closes this one first (toilet seat `needs='wc.pan.lid'`), `circuit` see Circuits.
**[round 3]** `lib/interact.py` and the viewer take both keys (the WC and `bath.toilet` lids and
seats are now two groups: `<name>.lid`, `<name>.seat` with `needs` the lid).

## What each kind of thing needs
- **Doors** (joinery, automatic): every hinged leaf = `hinge` about its hinge axis with `blocks`;
  leaf modelled at `openAngle` → state 1 is closed (`on=True`), a leaf modelled closed swings to
  ~90° open. Double doors: one group per leaf. The pocket door = `slide`. Glass, handles and
  letter plates share the leaf group.
- **Cabinet doors / drawers**: door hinges on the side opposite its handle, opens 95–110° outward
  (wall-unit lift-up flaps hinge on the top edge); drawers `slide` 0.30–0.40 m. Oven doors drop
  down ~85° on a bottom hinge. Washer / dryer portholes hinge on their real side.
- **Fridge-freezer**: each door `hinge` 100° on its outer edge, shelves + door bins inside, and an
  interior light as a `show when=1 fx=glow` emissive strip in the same group.
- **Toilet**: lid `hinge` ~95° about the back hinge line; the seat ring is a second group.
- **Bins**: lid `hinge` 60–75° about its back edge; the pedal is a `trigger` in the same group.
- **Taps**: lever = `hinge` (15–25°) or `trigger`; the water is a separate thin stream mesh from
  the spout to the bowl, `show when=1 fx=water`, same group, plus an optional flat splash ring.
  A mixer with two controls still gets one stream.
- **Hob**: per burner a ring of flame geometry (short cones or a crown strip, ~12 mm high) just
  above the burner cap, `show when=1 fx=flame`; its knob is the `trigger` of that burner's group.
- **TV**: the screen face is its own quad with 0..1 UVs: `show when=1 fx=tv` 1 mm in front of the
  black glass; the set itself is the `trigger`.
- **Clocks**: hour and minute hands (and second hand if the real clock has one) as separate small
  objects modelled pointing to 12, each `clock`. Remove any hands baked into a dial texture.
- **Curtains**: model both states as separate objects in one group: the tied-back pair is
  `show when=0`, a closed pair hanging straight across the window is `show when=1`
  (`fx='none'`); the tie-backs / tassels get `show when=0`. The pole or the cloth itself may be
  the trigger (`show` objects are clickable).
- **Light switches**: every switch plate that exists in the room = `light` with the room(s) it
  controls. Table lamps and wall lights = `lamp`. One tagged object (knob, rocker) per gang when
  the gangs switch different lamps, each with its `circuit`.

## Circuits (one room, several switches for different lamps)
A room whose lamps are on several switches (dining: spotlights / chandelier / wall lights; living:
spotlights / chandelier / wall lights / table lamp; kitchen: spotlights / LED tapes) gets one bake
per circuit, so a switch dims only its own lamps and their light. The export finds the circuits
from the tags and the Cycles lamps; nothing else has to be modelled:
- A Cycles lamp belongs to a lamp group (`t='lamp'`) when its name extends a member's name
  (`dining.chandelier.bulb.3` -> member `dining.chandelier`), else when it lies within 8 cm of a
  member's box (an LED strip at its tape). Name a fitting's lamps `<fitting>.<anything>`.
- Its circuit: the group's `circuit`; without one, a lamp group with no `rooms` is a circuit of its
  own named after the group (a table lamp on its plug, a desk lamp, LED tapes on their own rocker);
  every other lamp of the room is circuit `main` (a lamp group WITH `rooms` and no `circuit` still
  switches the whole room).
- Who switches it: a `light` / `lamp` with `circuit` switches that circuit of its `rooms` only
  (the knobs of a multi-gang dimmer: `IX.tag(knob, 'light', g='dining.switch.chandelier',
  rooms=['dining'], circuit='chandelier')`, and the fitting itself with the same `circuit`); a
  lamp group with no `rooms` switches its own circuit; every other switch of the room switches all
  its circuits (a single plate, two-way hall switches).
- `CIRCUIT` in `blender/export.py` (empty) maps group ids to circuits for tags without the key;
  a tag's own key wins.
- A room with one circuit changes nothing. Export: `lightmaps_circuits/<room>.<circuit>.jpg` (the
  room's atlas at half size, lit by that circuit's lamps alone: no sun, sky, ambient or emissive
  surface) and manifest `circuits` (MULTILEVEL.md 10). Viewer: a room shows its lights-off atlas
  plus the lit circuits, the lights-on atlas while all are lit; its probe-lit objects take the lit
  circuits' `share` of the lamp light; untagged emissive meshes glow with the circuit whose
  fitting their name extends (else `main`), tagged ones with their group.

## Void rooms (eaves)
- A switch of a room of kind `void` (behind a knee wall, looked into through a hatch) works with
  Space / E without a line of sight while a hatch of that room is open (a group whose `blocks`, or
  whose id `<room>.<opening>.leaf.N`, names an opening that `connects` the void room).
- Void rooms start with their lights off (eaves.md 8); their switches turn them on.

## Export and viewer notes
- `export.py` copies `ix` verbatim, never merges or instances a tagged object away, keeps tagged
  objects out of the static lightmap unless they are door leaves, and bakes a second lightmap set
  with the room's lights off (`lightmaps_off/<room>.jpg`, listed in `manifest.json`): **[round 4]** the lamps of
  the room and of every room a switch names with it are off, the others stay lit. Plus one atlas per circuit in
  rooms with several (Circuits), scaled so that lights-off + all circuits = the lights-on atlas. Closed fronts,
  drawers, lids and seats are hidden from the lightmap bakes, so the static carcass or bowl behind them is lit
  when they open.
- `reach` and the 35-degree test of Space / E are measured on each member's own box, not the
  group's union box: a group spread over a room (a chandelier and its wall knob, wall lights along a
  wall) is not "within reach" everywhere inside the box they span.
- The viewer re-parents each group under a pivot at load, so tagged objects must not rely on a
  parent at runtime (the export already flattens the hierarchy).

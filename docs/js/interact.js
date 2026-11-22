// Interaction engine. Every GLB node whose extras carry `ix` (a JSON string, schema in blender/INTERACT.md) becomes
// operable: hinge / slide objects are re-parented under a pivot and eased between state 0 (as modelled) and state 1;
// show objects appear in one state with an effect (water, flame, tv, glow, cross-fade); clock hands follow the
// visitor's local time; light / lamp switch room lighting between the lights-on and lights-off bakes (main.js wires
// the roomLight registry into the materials). Points in tags are Blender world metres -> three (x, z, -y).
import * as THREE from 'three';
import { hull, setObstacle, layerOfLevel, zAt, isFree, penDoor, edgeDist } from './geom.js';

const B2T = (a) => new THREE.Vector3(a[0], a[2], -a[1]);
const ease = (t) => t * t * (3 - 2 * t);
const HL = new THREE.Color(0.08, 0.062, 0.036);               // hover tint as seen (after main.js's white balance)
const WARM = (c) => c.r > 0 && c.r >= c.g && c.g >= c.b;      // lamp light (warm white / amber), not a red or blue LED
const DUR = { hinge: 0.7, slide: 0.5, show: 0.35, light: 0.4, lamp: 0.4 };
const NOUN = [[/fridge|freezer/, 'fridge'], [/drawer/, 'drawer'], [/bin/, 'bin'], [/seat/, 'seat'], [/lid/, 'lid'], [/oven/, 'oven'], [/curtain/, 'curtains']];
// what a mover does, by its label, when not open / close: [state 0, state 1], {} = the label. A tag may carry its own
// (`verb: ['Turn over', 'Turn back']`, INTERACT.md), which wins.
const VERB = [[/air con|\bfan\b|heater/, ['Turn {} on', 'Turn {} off']], [/footstool/, ['Pull out {}', 'Push in {}']], [/timer/, ['Turn over {}', 'Turn over {}']],
  [/chair/, ['Swivel {}', 'Swivel {} back']], [/seat|lid/, ['Lift {}', 'Lower {}']]];
const visibleChain = (o) => { for (; o; o = o.parent) if (!o.visible) return false; return true; };
const cloneMat = (m) => Object.assign(m.clone(), { onBeforeCompile: m.onBeforeCompile, customProgramCacheKey: m.customProgramCacheKey });   // clone() drops them
const mapMat = (mesh, f) => { mesh.material = Array.isArray(mesh.material) ? mesh.material.map(f) : f(mesh.material); };
const matsOf = (o) => { const out = []; o.traverse((m) => m.isMesh && out.push(...[].concat(m.material))); return out; };

// walk: geom.js walk (portal.open is switched here); roomLight(id) -> registry entry
// { on: {value}, target, ratio, pratio?, wait?, mats: [{m, k}], lamps: [{light, k}], ems: [], circuits: [], bright() };
// circuitRooms: rooms with several lighting circuits - a group named in a circuit's `groups` switches that circuit
// only, another switch of the room every circuit (INTERACT.md, Circuits); via: {void room: [opening ids]} - a switch of
// a void room (the eaves, behind a knee wall) works with Space / E through an open hatch; castRay(origin, dir, far) -> hit;
// onClone(material, clone): a tagged object got its own copy of a material; onPortals(): a doorway changed state;
// onLights(rooms): a switch is about to change these rooms (main.js loads their lights-off bake, holding the fade with
// `wait` meanwhile); feetY(): the walker's floor height in three Y (reach is measured from the body above it).
// emissiveToView(color): the shader's emissive white balance, inverted, so the hover tint shows as HL (main.js).
// lmProbe(object, material, side): for a baked door leaf, the scale of its probe light once it has faded from its
// lightmap (main.js matches the brightness the bake gave its face on `side`, the way it swings).
// Door leaves (hinge / slide groups with `blocks`) are walk obstacles at their resting pose on the layers of their
// doorway (else of their level): see syncPortals. So are the hatch leaves `<room>.<hatch>.leaf.N` (no `blocks`: they
// open the walk portal of the hatch they are named for, g.hatch, and nothing else changes for them) and the door of a
// pen (a sauna cabin, geom.js penDoor: a vertical hinge hung in the pen's outline).
// Incremental: `add(model)` takes one more glTF scene (one per level as it arrives, `model` is the first); each node is
// processed once, and switches reach rooms of any level - lamps of a room that arrives later are registered then.
// ponytail: axes and pivots are set in the parent's frame, which is the world frame because the export flattens the
// hierarchy (INTERACT.md) and level scenes sit at the origin; transform them by the parent's inverse if that changes.
export function initInteract({ model, walk, roomLight, castRay, onClone = () => {}, onPortals = () => {}, onLights = () => {}, emissiveToView = (c) => c, feetY = () => 0, lmProbe = () => 1, circuitRooms = [], via = {} }) {
  const groups = new Map(), clocks = [], tagged = new Map(), fx = [], v = new THREE.Vector3(), q = new THREE.Vector3(), hl = new THREE.Color();
  const piv = new THREE.Vector3(), rot = new THREE.Quaternion();
  const tint = emissiveToView(HL.clone());
  const own = (m) => { const c = cloneMat(m); onClone(m, c); return c; };
  const roots = [], rooms = new Map(), lightRooms = [], emClone = new Map(), registered = new WeakSet();
  const pivot = (o, at) => {          // re-parent o under a pivot at `at` (world), keeping its world transform
    const pv = new THREE.Object3D(), par = o.parent;
    par.add(pv); pv.position.copy(par.worldToLocal(at.clone())); pv.updateMatrixWorld(true); pv.attach(o);
    return pv;
  };
  function add(model) {
    if (roots.includes(model)) return;
    roots.push(model); model.updateMatrixWorld(true);
    const list = [], touched = new Set();
    model.traverse((o) => typeof o.userData.ix === 'string' && !tagged.has(o) && list.push(o));
    for (const o of list) {
      let d;
      try { d = JSON.parse(o.userData.ix); } catch { console.warn('ix: bad tag on', o.name); continue; }
      o.traverse((m) => m.isMesh && mapMat(m, own));                // own materials: highlight / fades stay per object
      const it = { o, d, mats: matsOf(o).map((m) => ({ m, e0: m.emissive?.clone(), k: m.emissiveIntensity ?? 1, op: m.opacity, tr: m.transparent })) };
      tagged.set(o, it);
      if (d.t === 'clock') { it.pv = pivot(o, B2T(d.p)); it.axis = B2T(d.a).normalize(); clocks.push(it); continue; }
      const id = d.g || o.userData.name || o.name;      // GLTFLoader strips dots from o.name; userData.name is the Blender name
      const g = groups.get(id) || groups.set(id, { id, items: [], state: 0, p: 0, dur: 0, hold: 0, on: false, label: '', reach: 1.6, blocks: new Set(), excl: new Set(), needs: new Set(), rooms: [], circ: [] }).get(id);
      it.g = g; g.items.push(it); touched.add(g);
      g.dur = Math.max(g.dur, d.dur ?? DUR[d.t] ?? 0);
      g.on ||= !!d.on; g.label ||= d.label || ''; if (d.reach) g.reach = d.reach; if (Array.isArray(d.verb)) g.verb ||= d.verb;
      g.home ??= o.userData.room; g.level ??= model.userData.level ?? 'G';
      if (d.blocks) g.blocks.add(d.blocks);
      for (const x of d.excl || []) g.excl.add(x);
      for (const x of [].concat(d.needs || [])) g.needs.add(x);
      for (const r of d.rooms || []) if (!g.rooms.includes(r)) g.rooms.push(r);
      if (d.t === 'hinge') { it.pv = pivot(o, B2T(d.p)); it.axis = B2T(d.a || [0, 0, 1]).normalize(); it.rad = (d.deg * Math.PI) / 180; }
      else if (d.t === 'slide') { it.pv = pivot(o, o.getWorldPosition(v)); it.base = it.pv.position.clone(); it.dv = B2T(d.d); }
      else if (d.t === 'show') setupShow(it);
      if (it.pv && d.t !== 'show') for (const x of it.mats) if (x.m.lightMap) {     // baked mover: own lmMix (main.js shader)
        const ob = x.m.onBeforeCompile, u = (it.lmMix ||= { value: 1 }), k = (it.lmProbe ||= { value: lmProbe(o, x.m, swingSide(it)) });
        x.m.onBeforeCompile = function (sh, r) { ob.call(this, sh, r); sh.uniforms.lmMix = u; sh.uniforms.lmProbe = k; };
      }
      const vert = d.t === 'slide' || (d.t === 'hinge' && Math.abs(it.axis.y) > 0.9);
      const hatch = !d.blocks && d.t === 'hinge' && /^[^.]+\.([^.]+)\.leaf\.\d+$/.exec(id)?.[1];
      if (hatch && walk?.portals.some((p) => p.id === hatch)) g.hatch = hatch;
      const pen = !d.blocks && !g.hatch && vert && d.t === 'hinge' && walk?.pens?.some((pn) => !pn.open && pn.layer === layerOfLevel(g.level) && edgeDist(d.p[0], d.p[1], pn.poly) < 0.1);
      if (vert && (d.blocks || g.hatch || pen)) {          // a door leaf: its plan outline
        const pts = [];
        o.traverse((m) => { if (!m.isMesh) return; const a = m.geometry.attributes.position, st = Math.max(1, Math.floor(a.count / 4000));
          for (let k = 0; k < a.count; k += st) { v.fromBufferAttribute(a, k).applyMatrix4(m.matrixWorld); pts.push([v.x, v.z]); } });
        it.foot = hull(pts).map(([x, z]) => new THREE.Vector3(x, 0, z));            // three x, z at the modelled pose
        if (pen && penDoor(walk, layerOfLevel(g.level), footAt(it, d.on ? 1 : 0))) g.pen = true;   // its outline shut
      }
    }
    for (const g of touched) {
      const ts = new Set(g.items.map((it) => it.d.t)), fxs = new Set(g.items.filter((it) => it.d.t === 'show').map((it) => it.d.fx || 'none'));
      g.kind = ts.has('light') ? 'light' : ts.has('lamp') ? 'lamp' : fxs.has('tv') ? 'tv' : fxs.has('water') ? 'water' : fxs.has('flame') ? 'flame'
        : ts.has('hinge') || ts.has('slide') ? 'move' : fxs.has('none') ? 'curtain' : fxs.has('glow') ? 'glow' : 'move';
      if (g.kind === 'light' && !g.rooms.length) g.kind = 'lamp';
      const name = g.id.toLowerCase();
      g.label ||= { light: 'lights', lamp: 'lamp', tv: 'TV', water: 'tap', flame: 'burner', curtain: 'curtains', glow: 'light' }[g.kind]
        || NOUN.find(([re]) => re.test(name))?.[1] || 'door';
      g.label = g.label.replace(/\b[A-Z][a-z]+\b/g, (w) => w.toLowerCase());     // "Front door" -> "front door", keeps "WC", "TV"
      if (g.kind === 'lamp' || g.kind === 'light') for (const it of g.items) it.glow = it.mats.filter((x) => x.m.emissive && WARM(x.m.emissive) && x.k > 0);
      for (const r of circuitRooms) for (const c of roomLight(r).circuits) if (c.groups?.includes(g.id) && !g.circ.some((x) => x.c === c)) g.circ.push({ r, c });
    }
    // ---- lights: rooms with a switch (on any level so far) get their warm emissive meshes registered ----
    for (const g of groups.values()) for (const r of roomsOf(g)) if (!rooms.has(r)) { const L = roomLight(r); L.x ??= L.target; rooms.set(r, L); lightRooms.push(L); }
    for (const root of roots) root.traverse((m) => {
      if (!m.isMesh || registered.has(m) || itemOf(m)) return;
      const r = m.userData.room ?? m.parent?.userData.room, L = rooms.get(r);
      if (!L) return;                                   // no switch for its room (yet): looked at again on the next add
      registered.add(m);
      const name = m.userData.name || m.parent?.userData.name, cs = L.circuits || [];   // its circuit, else the room's main one
      const c = cs.find((x) => x.emissive.has(name)) || cs.find((x) => x.name === 'main');
      mapMat(m, (mat) => {
        if (!mat.emissive || !WARM(mat.emissive) || !(mat.emissiveIntensity > 0)) return mat;
        const k = mat.uuid + r + (c ? c.name : '');
        if (!emClone.has(k)) { const e = own(mat); emClone.set(k, e); (c || L).ems.push({ m: e, k: e.emissiveIntensity }); e.emissiveIntensity *= (c || L).on.value; }
        return emClone.get(k);
      });
    });
    syncLights();
    nameBurners();
    for (const g of touched) {          // a lamp on its own plug that arrives while its room is switched off starts off
      if (g.kind === 'lamp' && !g.rooms.length && !g.circ.length && rooms.get(g.home)?.target < 0.5 && g.state === 0) g.state = g.p = 1;
      apply(g);
    }
    syncPortals();
  }
  if (model) add(model);

  function swingSide(it) {              // world direction a hinge / slide item moves toward, state 0 -> 1
    if (it.d.t === 'slide') return it.dv.clone().normalize();
    const c0 = new THREE.Box3().setFromObject(it.o).getCenter(new THREE.Vector3()), pv = B2T(it.d.p);
    const c1 = c0.clone().sub(pv).applyAxisAngle(it.axis, it.rad).add(pv);
    return c1.sub(c0).normalize();
  }
  function setupShow(it) {
    const f = (it.fx = it.d.fx || 'none');
    it.phase = Math.random() * 100;
    if (f === 'tv') {
      const c = Object.assign(document.createElement('canvas'), { width: 320, height: 180 });
      const tex = Object.assign(new THREE.CanvasTexture(c), { flipY: false, colorSpace: THREE.SRGBColorSpace });  // glTF UVs
      it.tv = { c, g: c.getContext('2d'), tex, t0: -1e9, last: 0 };
      const mat = new THREE.MeshBasicMaterial({ map: tex, toneMapped: false });
      it.o.traverse((m) => m.isMesh && (m.material = mat));
    } else if (f === 'flame') {          // its own emissive hue (blue gas, an orange fire pit), else gas blue
      it.o.traverse((m) => m.isMesh && mapMat(m, (mat) => new THREE.MeshBasicMaterial({
        color: mat.emissive && mat.emissive.r + mat.emissive.g + mat.emissive.b > 0.05 ? mat.emissive : new THREE.Color(0x3f7cff),
        transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false, side: THREE.DoubleSide })));
      const box = new THREE.Box3().setFromObject(it.o);       // flicker scales about the burner cap
      it.pv = pivot(it.o, box.getCenter(v).setY(box.min.y));
    } else if (f === 'water') {
      // the streaks keep one density whatever the mesh: a tap stream ~1-2 cm across gets the texture once around, a
      // shower spray (a wide cone, tens of cm) gets it repeated round its girth and down its length, with clear gaps
      // between the jets. Size from the mesh as modelled (the tag has no size key, INTERACT.md): girth = surface area /
      // height, which a curved stream or a splash ring at its foot hardly changes.
      const s = new THREE.Box3().setFromObject(it.o).getSize(q), girth = areaOf(it.o) / Math.max(s.y, 0.05), spray = girth > 0.2;
      it.tex = waterTex(spray).clone();
      it.tex.repeat.set(Math.max(1, Math.round(girth / 0.04)), Math.max(2, Math.round(s.y / 0.12)));
      it.o.traverse((m) => m.isMesh && mapMat(m, (mat) => Object.assign(mat, { transparent: true, depthWrite: false, alphaMap: it.tex, side: THREE.DoubleSide, ...(spray ? { opacity: mat.opacity * 0.7 } : {}) })));
    }
    if (f !== 'none') fx.push(it);
    it.mats = matsOf(it.o).map((m) => ({ m, e0: m.emissive?.clone(), k: m.emissiveIntensity ?? 1, op: m.opacity, tr: m.transparent }));
  }

  // ---- state ----
  function isOpen(g) { return (g.state === 1) !== g.on; }
  function apply(g) {
    const e = ease(g.p);
    for (const it of g.items) {
      const d = it.d;
      if (d.t === 'hinge') it.pv.quaternion.setFromAxisAngle(it.axis, it.rad * e);
      else if (d.t === 'slide') it.pv.position.copy(it.base).addScaledVector(it.dv, e);
      if (it.lmMix) it.lmMix.value = 1 - e;
      else if (d.t === 'show') {
        const a = (it.a = d.when ? e : 1 - e);
        it.o.visible = it.fx === 'tv' ? (d.when ? g.state === 1 || g.p > 0 : g.state === 0 || g.p < 1) : a > 0.01;
        if (it.fx === 'glow') for (const x of it.mats) x.m.emissiveIntensity = x.k * a;
        else if (it.fx === 'none') for (const x of it.mats) {
          const fading = a < 0.999;
          if (x.m.transparent !== (fading || x.tr)) { x.m.transparent = fading || x.tr; x.m.needsUpdate = true; }
          x.m.opacity = x.op * a;
        }
      }
      for (const x of it.glow || []) x.m.emissiveIntensity = x.k * (1 - e);      // lamps: state 0 = lit, as baked
    }
  }
  function roomsOf(g) { return g.circ.length ? [...new Set(g.circ.map((x) => x.r))] : g.rooms; }
  function syncLights() {               // a switch shows the state of the first circuit / room it controls
    for (const g of groups.values()) {
      if (g.circ.length) g.state = g.circ[0].c.target > 0.5 ? 0 : 1;
      else if (g.rooms.length) g.state = rooms.get(g.rooms[0]).target > 0.5 ? 0 : 1;
    }
  }
  // doorways: passable while any leaf blocking them is open; every leaf is a solid outline at the pose it is heading
  // for (a double door's shut leaf keeps its half of the doorway shut, an open leaf is not walked through)
  function footAt(it, state) {         // plan outline [[x, y]] of a leaf item in a state
    if (it.d.t === 'slide') return it.foot.map((q) => [q.x + it.dv.x * state, -(q.z + it.dv.z * state)]);
    piv.copy(B2T(it.d.p)); rot.setFromAxisAngle(it.axis, it.rad * state);
    return it.foot.map((q) => { v.copy(q).setY(piv.y).sub(piv).applyQuaternion(rot).add(piv); return [v.x, -v.z]; });
  }
  const opens = (g) => (g.hatch ? [g.hatch] : [...g.blocks]);      // the walk portals a group's leaves open
  function syncPortals(notify = true) {
    if (!walk) return;
    const ids = new Set([...groups.values()].flatMap(opens));
    for (const id of ids) {
      const p = walk.portals.find((x) => x.id === id);
      if (p) p.open = [...groups.values()].some((g) => opens(g).includes(id) && isOpen(g));
    }
    for (const g of groups.values()) {
      const its = g.items.filter((it) => it.foot);
      if (!its.length || !(g.blocks.size || g.hatch || g.pen)) continue;
      const pts = its.flatMap((it) => footAt(it, g.state));
      const p = walk.portals.find((x) => opens(g).includes(x.id));
      setObstacle(walk, g.id, p ? [...new Set(p.layers)] : [layerOfLevel(g.level)], hull(pts));
    }
    if (notify && ids.size) onPortals();
  }
  function toggle(g) {
    if (g.circ.length) {                // its own circuit(s) of a room with several; the room is lit while any circuit is
      const on = g.circ[0].c.target < 0.5;
      onLights(roomsOf(g));
      for (const { c } of g.circ) c.target = on ? 1 : 0;
      for (const r of roomsOf(g)) { const L = rooms.get(r); L.target = L.circuits.some((c) => c.target > 0.5) ? 1 : 0; }
      syncLights();
    } else if (g.rooms.length) {        // the whole room: every circuit of it
      const on = rooms.get(g.rooms[0]).target < 0.5;
      onLights(g.rooms);
      for (const r of g.rooms) { const L = rooms.get(r); L.target = on ? 1 : 0; for (const c of L.circuits || []) c.target = L.target; }
      syncLights();
      // a lamp on its own plug (no `rooms`, no circuit) goes off with its room - the lights-off bake has no lamp in it - and back on
      for (const l of groups.values()) if (l.kind === 'lamp' && !l.rooms.length && !l.circ.length && g.rooms.includes(l.home)) l.state = on ? 0 : 1;
    } else {
      const first = (x) => { x.state ^= 1; g.hold = Math.max(g.hold, x.dur * Math.abs(x.state - x.p)); if (x.blocks.size || x.hatch || x.pen) syncPortals(); };
      if (!isOpen(g)) {                 // swings that cross this one shut first, what it rests on (`needs`) opens first;
        for (const id of g.excl) { const x = groups.get(id); if (x && isOpen(x)) first(x); }      // this one waits for them
        for (const id of g.needs) { const x = groups.get(id); if (x && !isOpen(x)) first(x); }    // (toilet seat: the lid)
      } else for (const x of groups.values()) if (x.needs.has(g.id) && isOpen(x)) first(x);     // shutting: what rests on it first
      g.state ^= 1;
    }
    for (const it of g.items) if (it.tv && g.state === it.d.when) it.tv.t0 = performance.now();
    if (g.blocks.size || g.hatch || g.pen) syncPortals();
    return g.state;
  }
  const verb = (g) => {
    const n = g.label, open = isOpen(g);
    switch (g.kind) {
      case 'light': return n === 'lights' ? (g.state ? 'Lights on' : 'Lights off') : `Turn ${n} ${g.state ? 'on' : 'off'}`;
      case 'lamp': return `Turn ${n} ${g.state ? 'on' : 'off'}`;
      case 'tv': return `Switch ${n} ${open ? 'off' : 'on'}`;
      case 'water': case 'glow': return `Turn ${n} ${open ? 'off' : 'on'}`;
      case 'flame': return open ? `Turn ${n} off` : `Light ${n}`;
      case 'curtain': return g.state ? `Open ${n}` : `Close ${n}`;     // state 0 = tied back, as modelled
      default: {
        const v = g.verb ? g.verb.map((x) => `${x} {}`) : VERB.find(([re]) => re.test(n))?.[1];
        return v ? v[open ? 1 : 0].replace('{}', n) : `${open ? 'Close' : 'Open'} ${n}`;
      }
    }
  };
  // Burners of one hob (kitchen.hob.0..4, all labelled "hob"): named by where their flames sit for the cook - "back-right
  // burner", "left burner". Left as they are unless every name differs.
  function nameBurners() {
    const sets = new Map();
    for (const g of groups.values()) if (g.kind === 'flame' && /\.\d+$/.test(g.id) && !g.named) { const k = g.id.replace(/\.\d+$/, ''); (sets.get(k) || sets.set(k, []).get(k)).push(g); }
    for (const list of sets.values()) {
      if (list.length < 2 || new Set(list.map((g) => g.label)).size > 1 || !walk) continue;
      const at = (g) => { const b = new THREE.Box3(); for (const it of g.items) if (it.d.t === 'show') b.expandByObject(it.o); return b.isEmpty() ? groupBox(g) : b; };   // the flame, not the knob
      const c = list.map((g) => { const p = at(g).getCenter(new THREE.Vector3()); return [p.x, -p.z]; }), L = layerOfLevel(list[0].level);
      const mx = c.reduce((a, p) => a + p[0], 0) / c.length, my = c.reduce((a, p) => a + p[1], 0) / c.length;
      // the front: toward the control knobs (the groups' other items), else the one side with free floor 0.7 m out
      const kb = new THREE.Box3(); for (const g of list) for (const it of g.items) if (it.d.t !== 'show') kb.expandByObject(it.o);
      const kc = !kb.isEmpty() && kb.getCenter(new THREE.Vector3()), kx = kc ? kc.x - mx : 0, ky = kc ? -kc.z - my : 0;
      const fronts = Math.hypot(kx, ky) > 0.03 ? [Math.abs(kx) > Math.abs(ky) ? [Math.sign(kx), 0] : [0, Math.sign(ky)]]
        : [[1, 0], [-1, 0], [0, 1], [0, -1]].filter(([dx, dy]) => isFree(walk, L, mx + dx * 0.7, my + dy * 0.7));
      if (fronts.length !== 1) continue;
      const [fx, fy] = fronts[0], rx = -fy, ry = fx;               // the cook faces -front; their right hand
      const names = c.map(([x, y]) => {
        const dp = (x - mx) * fx + (y - my) * fy, sd = (x - mx) * rx + (y - my) * ry;
        return [Math.abs(dp) > 0.04 ? (dp > 0 ? 'front' : 'back') : '', Math.abs(sd) > 0.06 ? (sd > 0 ? 'right' : 'left') : 'centre'].filter(Boolean).join('-');
      });
      if (new Set(names).size !== names.length) continue;
      list.forEach((g, i) => { g.label = `${names[i]} burner`; g.named = true; });
    }
  }

  // ---- pointing ----
  function itemOf(o) { for (; o; o = o.parent) { const it = tagged.get(o); if (it) return it; } return null; }
  let hov = null;
  function highlight(g, on) {
    for (const it of g.items) if (!it.fx || it.fx === 'none') for (const x of it.mats) {
      if (!x.e0) continue;
      x.m.emissive.copy(x.e0);
      if (on) x.m.emissive.add(hl.copy(tint).multiplyScalar(1 / Math.max(x.m.emissiveIntensity, 0.05)));
    }
  }
  function hover(hit, range = 4) {
    const it = hit && hit.distance <= range ? itemOf(hit.object) : null, g = it?.g || null;
    if (g !== hov) { if (hov) highlight(hov, false); if (g) highlight(g, true); hov = g; }
    return g;
  }
  const box = new THREE.Box3();
  function groupBox(g) {
    box.makeEmpty();
    for (const it of g.items) if (visibleChain(it.o)) box.expandByObject(it.o);
    return box;
  }
  // reach is measured from the body (a column from 0.2 m above the floor up to the eye), so a drawer at the knees is as
  // near as one at the chest - on whatever floor the walker stands - to the nearest MEMBER's box: a group spread over a
  // room (a chandelier with its wall knob, wall lights along a wall) is not within reach everywhere inside its union box
  const w = new THREE.Vector3(), clampN = (x, a, b) => Math.min(b, Math.max(a, x));
  const memberBoxes = (g) => g.items.filter((it) => visibleChain(it.o)).map((it) => new THREE.Box3().setFromObject(it.o)).filter((b) => !b.isEmpty());
  const colDist = (b, pos) => b.distanceToPoint(w.set(pos.x, clampN(clampN(pos.y, b.min.y, b.max.y), Math.min(feetY() + 0.2, pos.y), pos.y), pos.z));
  const reachTo = (g, pos) => memberBoxes(g).reduce((m, b) => Math.min(m, colDist(b, pos)), Infinity);
  // a switch of a void room (eaves) sits behind the knee wall: usable without a line of sight while a hatch is open
  const hatchOpen = (g) => g.rooms.length > 0 && g.rooms.every((r) => via[r]) && g.rooms.some((r) => via[r].some((id) =>
    [...groups.values()].some((x) => (x.blocks.has(id) || x.id.includes(`.${id}.`)) && isOpen(x))));
  // the doorway a door group closes (three frame), floor to 2 m, from its walk portal; null for a door without one
  const portalOf = (g) => walk && [...g.blocks].map((id) => walk.portals.find((p) => p.id === id)).find(Boolean);
  function doorBox(g) {
    if (g.door !== undefined) return g.door;
    const p = portalOf(g), z = p && zAt(walk, p.layers[0], ...p.center);
    if (!p || z === null) return (g.door = null);
    const [cx, cy] = p.center, [nx, ny] = p.normal, ux = -ny, uy = nx, hw = p.width / 2, hd = p.depth + 0.02, b = new THREE.Box3();
    for (const s of [-1, 1]) for (const t of [-1, 1]) b.expandByPoint(v.set(cx + ux * hw * s + nx * hd * t, z, -(cy + uy * hw * s + ny * hd * t)));
    return (g.door = b.expandByPoint(v.setY(z + 2.0)));
  }
  const roomOf = (o) => o.userData.room ?? o.parent?.userData.room;
  const ray = new THREE.Ray(), hitP = new THREE.Vector3();
  // best group in front of the camera: within its reach, within 35 deg of the view direction, not behind a wall or a
  // window - all measured on its members' own boxes (a door also by its doorway: an open leaf stands beside it)
  function best(camera) {
    const pos = camera.position, fwd = camera.getWorldDirection(new THREE.Vector3()), cands = [];
    const ahead = castRay(pos, fwd, 3, true), ga = ahead && itemOf(ahead.object)?.g;     // dead ahead wins, glass stops it
    // ... but an open doorway dead ahead, nearer than that, is its door's (not within the doorway: what is beyond it)
    ray.set(pos, fwd);
    let gd = null, td = ahead ? ahead.distance : 3;
    for (const g of groups.values()) {
      const b = g.blocks.size && doorBox(g);
      if (!b || b.containsPoint(pos) || !ray.intersectBox(b, hitP)) continue;
      const t = hitP.distanceTo(pos);
      if (t < td && reachTo(g, pos) <= g.reach) { gd = g; td = t; }
    }
    if (gd) return gd;
    if (ga && reachTo(ga, pos) <= ga.reach) return ga;
    // seen: nothing but the group on the way to that point, glass included; or, within 12 cm of the target, a surface of
    // its own room (a jamb, the wall it hangs on) - not the far face of a partition between rooms
    const sees = (g, t) => {
      const dir = t.clone().sub(pos), far = dir.length(), hit = castRay(pos, dir.normalize(), far + 0.05, true);
      if (!hit || itemOf(hit.object)?.g === g) return true;
      const r = roomOf(hit.object);
      return !hit.object.userData.glass && hit.distance > far - 0.12 && (r === g.home || !!portalOf(g)?.cells.includes(r));
    };
    for (const g of groups.values()) {
      let top = null;
      const db = g.blocks.size ? doorBox(g) : null, boxes = memberBoxes(g);
      for (const b of db && boxes.some((m) => colDist(m, pos) <= g.reach) ? [...boxes, db] : boxes) {
        if (b !== db && colDist(b, pos) > g.reach) continue;
        const d = b.distanceToPoint(pos);
        b.clampPoint(q.copy(fwd).multiplyScalar(Math.max(d, 0.3)).add(pos), q);   // box point nearest the line of sight
        const to = q.clone().sub(pos), ang = to.lengthSq() > 1e-6 ? to.angleTo(fwd) : 0, s = ang * 2 + d * 0.5;   // what you face beats what is merely near
        if (ang < 0.61 && (!top || s < top.s)) top = { g, s, q: q.clone() };
      }
      if (top) cands.push(top);
    }
    cands.sort((a, b) => a.s - b.s);
    for (const c of cands.slice(0, 4)) if (sees(c.g, c.q) || sees(c.g, groupBox(c.g).getCenter(v)) || hatchOpen(c.g)) return c.g;
    return null;
  }

  // ---- per frame ----
  function update(dt, now) {
    for (const g of groups.values()) {
      if (g.hold > 0) { g.hold -= dt; continue; }
      if (g.p !== g.state) { g.p += Math.sign(g.state - g.p) * Math.min(Math.abs(g.state - g.p), dt / (g.dur || 0.01)); apply(g); }
    }
    const step = (o) => { o.x += Math.sign(o.target - o.x) * Math.min(Math.abs(o.target - o.x), dt / DUR.light); return (o.on.value = ease(o.x)); };
    for (const L of lightRooms) {
      L.x ??= L.target;
      const cs = L.circuits || [];
      if (L.wait || (cs.length ? cs : [L]).every((o) => o.x === o.target && o.on.value === ease(o.x))) continue;   // wait: its lights-off bake is loading
      if (cs.length) {                  // each circuit eases on its own; the lights-on atlas shows only while all are lit
        L.on.value = cs.reduce((a, c) => a * step(c), 1);
        for (const c of cs) for (const x of c.ems) x.m.emissiveIntensity = x.k * c.on.value;
        if (cs.every((c) => c.x === c.target)) L.x = L.target;
      } else step(L);
      const e = L.on.value, f = L.bright ? L.bright() : (L.pratio ?? L.ratio) + (1 - (L.pratio ?? L.ratio)) * e;
      for (const x of L.mats) x.m.envMapIntensity = x.k * f;
      for (const x of L.lamps) x.light.intensity = x.k * e;
      for (const x of L.ems) x.m.emissiveIntensity = x.k * e;
    }
    const t = now / 1000;
    for (const it of fx) {
      if (!it.o.visible) continue;
      // glTF stores v = 1 - Blender v, so a falling offset moves the streaks toward Blender -V (down the stream)
      if (it.fx === 'water') { it.tex.offset.y = 1 - ((t * 1.6) % 1); for (const x of it.mats) x.m.opacity = x.op * it.a * (0.82 + 0.1 * Math.sin(t * 23 + it.phase) + 0.06 * Math.sin(t * 37)); }
      else if (it.fx === 'flame') {
        const n = 0.5 + 0.3 * Math.sin(t * 31 + it.phase) + 0.2 * Math.sin(t * 57 + it.phase * 2);
        it.pv.scale.set(1, 0.85 + 0.35 * n, 1);
        for (const x of it.mats) x.m.opacity = it.a * (0.65 + 0.35 * n);
      } else if (it.fx === 'tv' && now - it.tv.last > 60) { it.tv.last = now; drawTV(it, now); }
    }
    if (clocks.length) {
      const d = new Date(), s = d.getSeconds(), m = d.getMinutes() + (s + d.getMilliseconds() / 1000) / 60, h = (d.getHours() % 12) + m / 60;
      for (const it of clocks) it.pv.quaternion.setFromAxisAngle(it.axis, -2 * Math.PI * { h: h / 12, m: m / 60, s: s / 60 }[it.d.hand]);
    }
  }

  // ---- api (also window.viewer.ix for tests) ----
  const angleOf = (it) => {             // clockwise angle of a hand from 12, read back from its pivot
    const { x, y, z, w } = it.pv.quaternion, s = x * it.axis.x + y * it.axis.y + z * it.axis.z;
    return ((-2 * Math.atan2(s, w)) % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI);
  };
  return {
    add, hover, best, update, verb, isOpen,
    models: () => roots.length,
    tagged: (o) => !!itemOf(o),
    groupOf: (o) => itemOf(o)?.g?.id ?? null,
    box: (id) => (groups.has(id) ? groupBox(groups.get(id)).clone() : null),
    hovered: () => hov,
    click(hit, range = 4) { const g = hover(hit, range); if (g) toggle(g); return g; },
    use(camera) {                       // Space / E: the group under the pointer if it is within reach, else the best in front
      const g = hov && reachTo(hov, camera.position) <= hov.reach ? hov : best(camera);
      if (g) toggle(g);
      return g;
    },
    toggle: (id) => (groups.has(id) ? toggle(groups.get(id)) : null),
    shut() {                            // doorways whose every leaf is shut and still (main.js: the view does not pass them)
      const shut = new Set(), open = new Set();
      for (const g of groups.values()) if (g.blocks.size) { const c = g.on ? 1 : 0, o = g.state !== c || g.p !== c; for (const id of g.blocks) (o ? open : shut).add(id); }
      for (const id of open) shut.delete(id);
      return shut;
    },
    state: (id) => groups.get(id)?.state ?? null,
    groups: () => [...groups.values()].map((g) => ({ id: g.id, kind: g.kind, label: g.label, state: g.state, p: g.p, open: isOpen(g), hint: verb(g),
      blocks: [...g.blocks], hatch: g.hatch ?? null, pen: !!g.pen, excl: [...g.excl], needs: [...g.needs], rooms: g.rooms, home: g.home, circuits: g.circ.map((x) => `${x.r}.${x.c.name}`), types: [...new Set(g.items.map((it) => it.d.t))], fx: g.items.filter((it) => it.fx).map((it) => it.fx),
      nodes: g.items.map((it) => it.o.userData.name || it.o.name), dur: g.dur })),
    clocks: () => clocks.map((it) => ({ name: it.o.userData.name || it.o.name, hand: it.d.hand, angle: angleOf(it) })),
    tvCanvas: (id) => groups.get(id)?.items.find((it) => it.tv)?.tv.c ?? null,
  };
}

// ---- effects ----
const ta = new THREE.Vector3(), tb = new THREE.Vector3(), tc = new THREE.Vector3();
function areaOf(o) {                     // world surface area of an object's meshes
  let a = 0;
  o.updateMatrixWorld(true);
  o.traverse((m) => {
    if (!m.isMesh) return;
    const p = m.geometry.attributes.position, ix = m.geometry.index, n = ix ? ix.count : p.count, at = (k) => (ix ? ix.getX(k) : k);
    for (let k = 0; k + 2 < n; k += 3) {
      ta.fromBufferAttribute(p, at(k)).applyMatrix4(m.matrixWorld); tb.fromBufferAttribute(p, at(k + 1)).applyMatrix4(m.matrixWorld); tc.fromBufferAttribute(p, at(k + 2)).applyMatrix4(m.matrixWorld);
      a += tb.sub(ta).cross(tc.sub(ta)).length() / 2;
    }
  });
  return a;
}
const WATER = {};
function waterTex(spray) {               // streaky alpha for running water (a spray: jets with clear gaps); scrolled along V
  if (WATER[spray]) return WATER[spray];
  const c = Object.assign(document.createElement('canvas'), { width: 32, height: 128 }), g = c.getContext('2d');
  g.fillStyle = spray ? '#141414' : '#8c8c8c'; g.fillRect(0, 0, 32, 128);
  for (let i = 0; i < 70; i++) {
    const x = Math.random() * 32, y = Math.random() * 128, h = 12 + Math.random() * 50, w = 1 + Math.random() * 2;
    g.fillStyle = `rgba(255,255,255,${0.25 + Math.random() * 0.6})`; g.fillRect(x, y, w, h); g.fillRect(x, y - 128, w, h);
  }
  return (WATER[spray] = Object.assign(new THREE.CanvasTexture(c), { wrapS: THREE.RepeatWrapping, wrapT: THREE.RepeatWrapping }));
}

// An original abstract picture: drifting landscape bands under a slowly turning sky, a sun, a clock widget.
// Power on: a CRT line opens into the picture over 0.6 s; power off plays the same backwards (group progress).
function drawTV(it, now) {
  const { c, g, tex, t0 } = it.tv, W = c.width, H = c.height, t = now / 1000;
  const k = it.g.state === it.d.when ? Math.min(1, (now - t0) / 600) : 0.6 * (it.d.when ? it.g.p : 1 - it.g.p);
  const hue = 205 + 25 * Math.sin(t / 23), sky = g.createLinearGradient(0, 0, 0, H * 0.7);
  sky.addColorStop(0, `hsl(${hue}, 55%, 38%)`); sky.addColorStop(1, `hsl(${hue + 120}, 60%, 72%)`);
  g.fillStyle = sky; g.fillRect(0, 0, W, H);
  g.fillStyle = 'rgba(255, 236, 190, 0.9)'; g.beginPath(); g.arc(((t * 6) % (W + 60)) - 30, 46 + 10 * Math.sin(t / 7), 17, 0, Math.PI * 2); g.fill();
  for (let b = 0; b < 4; b++) {                  // far -> near: lighter and slower
    const base = H * (0.5 + b * 0.13), amp = 8 + b * 5, sp = 6 + b * 11, wl = 60 - b * 8;
    g.fillStyle = `hsl(${150 + b * 18 + 10 * Math.sin(t / 11)}, ${30 + b * 12}%, ${62 - b * 13}%)`;
    g.beginPath(); g.moveTo(0, H);
    for (let x = 0; x <= W; x += 8) g.lineTo(x, base + amp * Math.sin((x + t * sp) / wl + b * 1.7) + amp * 0.4 * Math.sin((x + t * sp) / (wl * 0.37)));
    g.lineTo(W, H); g.closePath(); g.fill();
  }
  const d = new Date(), hm = `${String(d.getHours()).padStart(2, '0')}${d.getSeconds() % 2 ? ':' : ' '}${String(d.getMinutes()).padStart(2, '0')}`;
  g.fillStyle = 'rgba(10, 14, 20, 0.45)'; g.beginPath(); g.roundRect(W - 92, 12, 78, 30, 8); g.fill();
  g.fillStyle = '#f4f1ea'; g.font = '600 20px system-ui, sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(hm, W - 53, 28);
  if (k < 1) {                                   // power effect over the finished picture
    const band = k < 0.25 ? 2 : (H * Math.min(1, (k - 0.25) / 0.35)), line = k < 0.25 ? W * (k / 0.25) : W;
    g.fillStyle = '#000'; g.fillRect(0, 0, W, (H - band) / 2); g.fillRect(0, (H + band) / 2, W, H);
    if (k < 0.25) { g.fillRect(0, (H - band) / 2, (W - line) / 2, band); g.fillRect((W + line) / 2, (H - band) / 2, W, band); }
    g.fillStyle = `rgba(255, 255, 255, ${0.85 * (1 - k)})`; g.fillRect((W - line) / 2, (H - band) / 2, line, band);
  }
  tex.needsUpdate = true;
}

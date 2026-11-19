// Interaction engine. Every GLB node whose extras carry `ix` (a JSON string, schema in blender/INTERACT.md) becomes
// operable: hinge / slide objects are re-parented under a pivot and eased between state 0 (as modelled) and state 1;
// show objects appear in one state with an effect (water, flame, tv, glow, cross-fade); clock hands follow the
// visitor's local time; light / lamp switch room lighting between the lights-on and lights-off bakes (main.js wires
// the roomLight registry into the materials). Points in tags are Blender world metres -> three (x, z, -y).
import * as THREE from 'three';
import { hull, setObstacle, layerOfLevel } from './geom.js';

const B2T = (a) => new THREE.Vector3(a[0], a[2], -a[1]);
const ease = (t) => t * t * (3 - 2 * t);
const HL = new THREE.Color(0.08, 0.062, 0.036);               // hover tint as seen (after main.js's white balance)
const WARM = (c) => c.r > 0 && c.r >= c.g && c.g >= c.b;      // lamp light (warm white / amber), not a red or blue LED
const DUR = { hinge: 0.7, slide: 0.5, show: 0.35, light: 0.4, lamp: 0.4 };
const NOUN = [[/fridge|freezer/, 'fridge'], [/drawer/, 'drawer'], [/bin/, 'bin'], [/seat/, 'seat'], [/lid/, 'lid'], [/oven/, 'oven'], [/curtain/, 'curtains']];
const visibleChain = (o) => { for (; o; o = o.parent) if (!o.visible) return false; return true; };
const cloneMat = (m) => Object.assign(m.clone(), { onBeforeCompile: m.onBeforeCompile });   // clone() drops it
const mapMat = (mesh, f) => { mesh.material = Array.isArray(mesh.material) ? mesh.material.map(f) : f(mesh.material); };
const matsOf = (o) => { const out = []; o.traverse((m) => m.isMesh && out.push(...[].concat(m.material))); return out; };

// walk: geom.js walk (portal.open is switched here); roomLight(id) -> registry entry
// { on: {value}, target, ratio, pratio?, wait?, mats: [{m, k}], lamps: [{light, k}], ems: [] }; castRay(origin, dir, far) -> hit;
// onClone(material, clone): a tagged object got its own copy of a material; onPortals(): a doorway changed state;
// onLights(rooms): a switch is about to change these rooms (main.js loads their lights-off bake, holding the fade with
// `wait` meanwhile); feetY(): the walker's floor height in three Y (reach is measured from the body above it).
// emissiveToView(color): the shader's emissive white balance, inverted, so the hover tint shows as HL (main.js).
// lmProbe(object, material, side): for a baked door leaf, the scale of its probe light once it has faded from its
// lightmap (main.js matches the brightness the bake gave its face on `side`, the way it swings).
// Door leaves (hinge / slide groups with `blocks`) are walk obstacles at their resting pose on the layers of their
// doorway (else of their level): see syncPortals.
// Incremental: `add(model)` takes one more glTF scene (one per level as it arrives, `model` is the first); each node is
// processed once, and switches reach rooms of any level - lamps of a room that arrives later are registered then.
// ponytail: axes and pivots are set in the parent's frame, which is the world frame because the export flattens the
// hierarchy (INTERACT.md) and level scenes sit at the origin; transform them by the parent's inverse if that changes.
export function initInteract({ model, walk, roomLight, castRay, onClone = () => {}, onPortals = () => {}, onLights = () => {}, emissiveToView = (c) => c, feetY = () => 0, lmProbe = () => 1 }) {
  const groups = new Map(), clocks = [], tagged = new Map(), fx = [], v = new THREE.Vector3(), q = new THREE.Vector3(), hl = new THREE.Color();
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
      const g = groups.get(id) || groups.set(id, { id, items: [], state: 0, p: 0, dur: 0, hold: 0, on: false, label: '', reach: 1.6, blocks: new Set(), excl: new Set(), rooms: [] }).get(id);
      it.g = g; g.items.push(it); touched.add(g);
      g.dur = Math.max(g.dur, d.dur ?? DUR[d.t] ?? 0);
      g.on ||= !!d.on; g.label ||= d.label || ''; if (d.reach) g.reach = d.reach;
      g.home ??= o.userData.room; g.level ??= model.userData.level ?? 'G';
      if (d.blocks) g.blocks.add(d.blocks);
      for (const x of d.excl || []) g.excl.add(x);
      for (const r of d.rooms || []) if (!g.rooms.includes(r)) g.rooms.push(r);
      if (d.t === 'hinge') { it.pv = pivot(o, B2T(d.p)); it.axis = B2T(d.a || [0, 0, 1]).normalize(); it.rad = (d.deg * Math.PI) / 180; }
      else if (d.t === 'slide') { it.pv = pivot(o, o.getWorldPosition(v)); it.base = it.pv.position.clone(); it.dv = B2T(d.d); }
      else if (d.t === 'show') setupShow(it);
      if (it.pv && d.t !== 'show') for (const x of it.mats) if (x.m.lightMap) {     // baked mover: own lmMix (main.js shader)
        const ob = x.m.onBeforeCompile, u = (it.lmMix ||= { value: 1 }), k = (it.lmProbe ||= { value: lmProbe(o, x.m, swingSide(it)) });
        x.m.onBeforeCompile = function (sh, r) { ob.call(this, sh, r); sh.uniforms.lmMix = u; sh.uniforms.lmProbe = k; };
      }
      if (d.blocks && (d.t === 'slide' || (d.t === 'hinge' && Math.abs(it.axis.y) > 0.9))) {   // a door leaf: its plan outline
        const pts = [];
        o.traverse((m) => { if (!m.isMesh) return; const a = m.geometry.attributes.position, st = Math.max(1, Math.floor(a.count / 4000));
          for (let k = 0; k < a.count; k += st) { v.fromBufferAttribute(a, k).applyMatrix4(m.matrixWorld); pts.push([v.x, v.z]); } });
        it.foot = hull(pts).map(([x, z]) => new THREE.Vector3(x, 0, z));            // three x, z at the modelled pose
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
    }
    // ---- lights: rooms with a switch (on any level so far) get their warm emissive meshes registered ----
    for (const g of groups.values()) for (const r of g.rooms) if (!rooms.has(r)) { const L = roomLight(r); L.x ??= L.target; rooms.set(r, L); lightRooms.push(L); }
    for (const root of roots) root.traverse((m) => {
      if (!m.isMesh || registered.has(m) || itemOf(m)) return;
      const r = m.userData.room ?? m.parent?.userData.room, L = rooms.get(r);
      if (!L) return;                                   // no switch for its room (yet): looked at again on the next add
      registered.add(m);
      mapMat(m, (mat) => {
        if (!mat.emissive || !WARM(mat.emissive) || !(mat.emissiveIntensity > 0)) return mat;
        const k = mat.uuid + r;
        if (!emClone.has(k)) { const c = own(mat); emClone.set(k, c); L.ems.push({ m: c, k: c.emissiveIntensity }); c.emissiveIntensity *= L.on.value; }
        return emClone.get(k);
      });
    });
    syncLights();
    for (const g of touched) {          // a lamp on its own plug that arrives while its room is switched off starts off
      if (g.kind === 'lamp' && !g.rooms.length && rooms.get(g.home)?.target < 0.5 && g.state === 0) g.state = g.p = 1;
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
    } else if (f === 'flame') {
      it.o.traverse((m) => m.isMesh && mapMat(m, (mat) => new THREE.MeshBasicMaterial({
        color: mat.emissive && mat.emissive.b > mat.emissive.r ? mat.emissive : new THREE.Color(0x3f7cff),
        transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false, side: THREE.DoubleSide })));
      const box = new THREE.Box3().setFromObject(it.o);       // flicker scales about the burner cap
      it.pv = pivot(it.o, box.getCenter(v).setY(box.min.y));
    } else if (f === 'water') {
      it.o.traverse((m) => m.isMesh && mapMat(m, (mat) => Object.assign(mat, { transparent: true, depthWrite: false, alphaMap: waterTex() })));
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
  function syncLights() {               // a switch shows the state of the first room it controls
    for (const g of groups.values()) if (g.rooms.length) g.state = rooms.get(g.rooms[0]).target > 0.5 ? 0 : 1;
  }
  // doorways: passable while any leaf blocking them is open; every leaf is a solid outline at the pose it is heading
  // for (a double door's shut leaf keeps its half of the doorway shut, an open leaf is not walked through)
  const piv = new THREE.Vector3(), rot = new THREE.Quaternion();
  function syncPortals(notify = true) {
    if (!walk) return;
    const ids = new Set([...groups.values()].flatMap((g) => [...g.blocks]));
    for (const id of ids) {
      const p = walk.portals.find((x) => x.id === id);
      if (p) p.open = [...groups.values()].some((g) => g.blocks.has(id) && isOpen(g));
    }
    for (const g of groups.values()) {
      const its = g.items.filter((it) => it.foot);
      if (!its.length) continue;
      const pts = its.flatMap((it) => {
        if (it.d.t === 'slide') return it.foot.map((q) => [q.x + it.dv.x * g.state, -(q.z + it.dv.z * g.state)]);
        piv.copy(B2T(it.d.p)); rot.setFromAxisAngle(it.axis, it.rad * g.state);
        return it.foot.map((q) => { v.copy(q).setY(piv.y).sub(piv).applyQuaternion(rot).add(piv); return [v.x, -v.z]; });
      });
      const p = walk.portals.find((x) => g.blocks.has(x.id));
      setObstacle(walk, g.id, p ? [...new Set(p.layers)] : [layerOfLevel(g.level)], hull(pts));
    }
    if (notify && ids.size) onPortals();
  }
  function toggle(g) {
    if (g.rooms.length) {
      const on = rooms.get(g.rooms[0]).target < 0.5;
      onLights(g.rooms);
      for (const r of g.rooms) rooms.get(r).target = on ? 1 : 0;
      syncLights();
      // a lamp on its own plug (no `rooms`) goes off with its room - the lights-off bake has no lamp in it - and back on
      for (const l of groups.values()) if (l.kind === 'lamp' && !l.rooms.length && g.rooms.includes(l.home)) l.state = on ? 0 : 1;
    } else {
      if (!isOpen(g)) for (const id of g.excl) {      // swings that cross this one shut first; this one waits for them
        const x = groups.get(id);
        if (x && isOpen(x)) { x.state ^= 1; g.hold = Math.max(g.hold, x.dur * Math.abs(x.state - x.p)); if (x.blocks.size) syncPortals(); }
      }
      g.state ^= 1;
    }
    for (const it of g.items) if (it.tv && g.state === it.d.when) it.tv.t0 = performance.now();
    if (g.blocks.size) syncPortals();
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
      default: return /seat|lid/.test(n) ? `${open ? 'Lower' : 'Lift'} ${n}` : `${open ? 'Close' : 'Open'} ${n}`;
    }
  };

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
  // near as one at the chest - on whatever floor the walker stands
  const w = new THREE.Vector3(), clampN = (x, a, b) => Math.min(b, Math.max(a, x));
  const reachTo = (g, pos) => { const b = groupBox(g); return b.distanceToPoint(w.set(pos.x, clampN(clampN(pos.y, b.min.y, b.max.y), Math.min(feetY() + 0.2, pos.y), pos.y), pos.z)); };
  // best group in front of the camera: within its reach, within 35 deg of the view direction, not behind a wall
  function best(camera) {
    const pos = camera.position, fwd = camera.getWorldDirection(new THREE.Vector3()), cands = [];
    const ahead = castRay(pos, fwd, 3), ga = ahead && itemOf(ahead.object)?.g;          // dead ahead wins
    if (ga && reachTo(ga, pos) <= ga.reach) return ga;
    // seen: nothing but the group (or a jamb within 12 cm of the target) on the way to that point
    const sees = (g, t) => { const dir = t.clone().sub(pos), far = dir.length(), hit = castRay(pos, dir.normalize(), far + 0.05); return !hit || itemOf(hit.object)?.g === g || hit.distance > far - 0.12; };
    for (const g of groups.values()) {
      const b = groupBox(g);
      if (b.isEmpty() || reachTo(g, pos) > g.reach) continue;
      const d = b.distanceToPoint(pos);
      b.clampPoint(q.copy(fwd).multiplyScalar(Math.max(d, 0.3)).add(pos), q);   // box point nearest the line of sight
      const to = q.clone().sub(pos), ang = to.lengthSq() > 1e-6 ? to.angleTo(fwd) : 0;
      if (ang < 0.61) cands.push({ g, s: ang * 2 + d * 0.5, q: q.clone() });    // what you face beats what is merely near
    }
    cands.sort((a, b) => a.s - b.s);
    for (const c of cands.slice(0, 4)) if (sees(c.g, c.q) || sees(c.g, groupBox(c.g).getCenter(v))) return c.g;
    return null;
  }

  // ---- per frame ----
  function update(dt, now) {
    for (const g of groups.values()) {
      if (g.hold > 0) { g.hold -= dt; continue; }
      if (g.p !== g.state) { g.p += Math.sign(g.state - g.p) * Math.min(Math.abs(g.state - g.p), dt / (g.dur || 0.01)); apply(g); }
    }
    for (const L of lightRooms) {
      L.x ??= L.target;
      if (L.wait || (L.x === L.target && L.on.value === ease(L.x))) continue;    // wait: its lights-off bake is loading
      L.x += Math.sign(L.target - L.x) * Math.min(Math.abs(L.target - L.x), dt / DUR.light);
      const e = (L.on.value = ease(L.x)), r = L.pratio ?? L.ratio, f = r + (1 - r) * e;
      for (const x of L.mats) x.m.envMapIntensity = x.k * f;
      for (const x of L.lamps) x.light.intensity = x.k * e;
      for (const x of L.ems) x.m.emissiveIntensity = x.k * e;
    }
    const t = now / 1000;
    for (const it of fx) {
      if (!it.o.visible) continue;
      // glTF stores v = 1 - Blender v, so a falling offset moves the streaks toward Blender -V (down the stream)
      if (it.fx === 'water') { WATER.offset.y = 1 - ((t * 1.6) % 1); for (const x of it.mats) x.m.opacity = x.op * it.a * (0.82 + 0.1 * Math.sin(t * 23 + it.phase) + 0.06 * Math.sin(t * 37)); }
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
    state: (id) => groups.get(id)?.state ?? null,
    groups: () => [...groups.values()].map((g) => ({ id: g.id, kind: g.kind, label: g.label, state: g.state, p: g.p, open: isOpen(g), hint: verb(g),
      blocks: [...g.blocks], excl: [...g.excl], rooms: g.rooms, home: g.home, types: [...new Set(g.items.map((it) => it.d.t))], fx: g.items.filter((it) => it.fx).map((it) => it.fx),
      nodes: g.items.map((it) => it.o.userData.name || it.o.name), dur: g.dur })),
    clocks: () => clocks.map((it) => ({ name: it.o.userData.name || it.o.name, hand: it.d.hand, angle: angleOf(it) })),
    tvCanvas: (id) => groups.get(id)?.items.find((it) => it.tv)?.tv.c ?? null,
  };
}

// ---- effects ----
let WATER = null;
function waterTex() {                    // streaky alpha for running water; scrolled along V
  if (WATER) return WATER;
  const c = Object.assign(document.createElement('canvas'), { width: 32, height: 128 }), g = c.getContext('2d');
  g.fillStyle = '#8c8c8c'; g.fillRect(0, 0, 32, 128);
  for (let i = 0; i < 70; i++) {
    const x = Math.random() * 32, y = Math.random() * 128, h = 12 + Math.random() * 50, w = 1 + Math.random() * 2;
    g.fillStyle = `rgba(255,255,255,${0.25 + Math.random() * 0.6})`; g.fillRect(x, y, w, h); g.fillRect(x, y - 128, w, h);
  }
  WATER = Object.assign(new THREE.CanvasTexture(c), { wrapS: THREE.RepeatWrapping, wrapT: THREE.RepeatWrapping });
  WATER.repeat.set(1, 2);
  return WATER;
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

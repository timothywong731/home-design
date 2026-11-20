// End-to-end check of the viewer in Chromium. Serves docs/ under /home-design/ (like GitHub Pages), drives the page,
// writes screenshots + console log to build/e2e/, exits non-zero on console errors or failed checks.
// Setup once:  npm install --prefix build/e2e playwright@1.65.1   (npx playwright install chromium if no browser yet)
// Run:         node docs/test/e2e.mjs [--headed] [--only desktop,ref,realtime,phone,ix,levels,cull,nav] [--assets <dir>]
//   --assets serves assets/ from another folder (e.g. a fresh export under build/, before it is copied into docs/)
// Two runs (blender/MULTILEVEL.md 12.g): schema-1 assets (docs/assets today) run the phase-1 blocks; schema-2 assets run
// only `levels` (tabs, sheets, marker on every sheet, sheet follows the stairs, layers, routes, dollhouse cut per level,
// interactions per level). The fixture: node docs/test/make_fixture.mjs && node docs/test/e2e.mjs --assets build/e2e/assets2
// (its screenshots go to build/e2e/levels/, so the phase-1 ones are kept).
import { createServer } from 'node:http';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { extname, join, normalize, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = fileURLToPath(new URL('../', import.meta.url));
const arg = (k) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : null; };
const ASSETS = arg('--assets') && resolve(arg('--assets'));
const MANIFEST = JSON.parse(await readFile(join(ASSETS || join(ROOT, 'assets'), 'manifest.json')).catch(() => readFile(join(ROOT, 'assets/manifest.json'))));
const SCHEMA = MANIFEST.schema === 2 ? 2 : 1, FIXTURE = !!MANIFEST.fixture;   // the fixture pairs the phase-1 GLB with the new house
const OUT = fileURLToPath(new URL(SCHEMA === 2 ? '../../build/e2e/levels/' : '../../build/e2e/', import.meta.url));
// schema 1: the phase-1 blocks; the schema-2 fixture: `levels` only; a real schema-2 export: everything
const ONLY = arg('--only')?.split(','), run = (b) => (!ONLY || ONLY.includes(b)) && (b === 'levels' ? SCHEMA === 2 : SCHEMA === 1 || !FIXTURE);
const { chromium } = createRequire(OUT)('playwright');
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json',
  '.glb': 'model/gltf-binary', '.jpg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp', '.ktx2': 'image/ktx2', '.dxf': 'image/vnd.dxf', '.pdf': 'application/pdf' };
const server = createServer(async (req, res) => {
  const url = decodeURIComponent(req.url.split('?')[0]);
  if (!url.startsWith('/home-design/')) { res.writeHead(404).end(); return; }
  const rel = normalize(url.slice('/home-design/'.length) || 'index.html').replace(/^([/\\]|\.\.)+/, '');
  const file = join(ROOT, rel.endsWith('/') || !rel ? join(rel, 'index.html') : rel);   // --assets: that folder first, then docs/assets
  try {
    const body = await (ASSETS && rel.replace(/\\/g, '/').startsWith('assets/') ? readFile(join(ASSETS, rel.slice(7))).catch(() => readFile(file)) : readFile(file));
    res.writeHead(200, { 'content-type': TYPES[extname(rel)] || 'application/octet-stream', 'content-length': body.length });
    res.end(req.method === 'HEAD' ? undefined : body);
  } catch { res.writeHead(404).end(); }
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const BASE = `http://127.0.0.1:${server.address().port}/home-design/`;
await mkdir(OUT, { recursive: true });

const logs = [], fails = [];
const check = (ok, what) => { console.log(`${ok ? 'PASS' : 'FAIL'}  ${what}`); if (!ok) fails.push(what); };
const launch = (channel) => chromium.launch({ channel, headless: !process.argv.includes('--headed'), args: ['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist'] });
const browser = await launch(undefined).catch(() => launch('chrome'));    // bundled browser, else the installed Chrome

async function open(ctxOpts, query = '', setup) {
  const ctx = await browser.newContext(ctxOpts), page = await ctx.newPage();
  if (setup) await setup(page);
  page.on('console', (m) => {
    const loc = m.location()?.url || '', line = `[${m.type()}] ${m.text()} ${loc}`;
    logs.push(line);
    if (m.type() === 'error') fails.push('console: ' + line);          // every asset is real now: a 404 is a failure
  });
  page.on('pageerror', (e) => { console.log('[pageerror]', e.message); logs.push('[pageerror] ' + e.message); fails.push('pageerror: ' + e.message); });
  await page.goto(BASE + query);
  await page.waitForSelector('#loader.done', { timeout: 60000 });
  await page.waitForTimeout(800);
  return { ctx, page };
}
const info = (page) => page.evaluate(() => window.viewer.info());
// wait until nothing moves (room jump / walk, door swings, light fades): frames are dt-clamped, so when the GPU is
// shared with Cycles bakes an animation can take longer than its nominal time
const idle = (page, ms = 150) => page.waitForFunction(() => {
  const v = window.viewer;
  return !v.S.anim && !v.S.glide && v.ix.groups().every((g) => g.p === g.state) && [...v.roomLights.values()].every((L) => (L.x ?? L.target) === L.target
    && !L.wait && (L.circuits || []).every((c) => c.x === c.target));
}, null, { timeout: 20000, polling: 50 }).catch(() => {}).then(() => page.waitForTimeout(ms));
const shot = (page, name, el) => (el ? page.locator(el).screenshot({ path: OUT + name }) : page.screenshot({ path: OUT + name }));

// ---- desktop ----
if (run('desktop')) {
  // gallery: fake renders/index.json + images via request interception (nothing written into docs/renders)
  const fakeRenders = async (page) => {
    await page.route('**/renders/index.json', (r) => r.fulfill({ json: [{ file: 'a.jpg', title: 'Hallway (test image)' }, 'b.jpg'] }));
    await page.route(/renders\/[ab]\.jpg$/, async (r) => r.fulfill({ contentType: 'image/jpeg',
      body: await readFile(join(ROOT, 'assets/probes', r.request().url().endsWith('a.jpg') ? 'hallway.jpg' : 'living.jpg')).catch(() => Buffer.alloc(0)) }));
  };
  const { ctx, page } = await open({ viewport: { width: 1440, height: 900 } }, '', fakeRenders);
  let i = await info(page);
  console.log('info', JSON.stringify(i));
  check(i.room === 'hallway', `spawns in the hallway (${i.room})`);
  check(i.realtime || i.lightmapped > 0, `lightmaps applied when a manifest exists (${i.lightmapped} meshes)`);
  // baked lighting on the real export: every manifest object found with uv1 (no warnings), probes on everything
  const bake = await page.evaluate(async () => {
    const m = await (await fetch('assets/manifest.json')).json(), all = [];
    const { scene, ring, ix } = window.viewer;          // the model only: not the floor ring, not effect materials (TV, flame)
    scene.traverse((o) => o.isMesh && o !== ring && !ix.tagged(o) && all.push(...[].concat(o.material).map((mat) => ({ o, mat }))));
    const lit = all.filter((a) => a.o.userData.baked);
    return { listed: m.lightmaps.reduce((n, l) => n + l.objects.length, 0), probes: m.probes.length, standin: !!m.standin,
      noEnv: all.filter((a) => !a.mat.envMap).length, noUv1: lit.filter((a) => !a.o.geometry.attributes.uv1).length,
      badLm: lit.filter(({ mat }) => !(mat.lightMap?.channel === 1 && mat.lightMap.flipY === false && mat.lightMap.colorSpace === 'srgb' && mat.lightMapIntensity > 0)).length };
  });
  check(!bake.standin && bake.listed > 50 && bake.probes >= 7, `real export manifest (${bake.listed} lightmapped objects, ${bake.probes} probes)`);
  check(bake.noUv1 === 0 && bake.badLm === 0, 'lightmaps on uv1, flipY off, sRGB, intensity x PI');
  check(i.probed > 0 && bake.noEnv === 0, `room probes on every material (${i.probed} meshes lit by probe alone)`);
  check(!logs.some((l) => /not found in the GLB|no second UV|image missing|shader changed/.test(l)), 'no lightmap / probe warnings');
  await shot(page, 'walk_spawn.png');

  // keyboard walking: W for 1 s moves forward (+Y) and stays inside the walkable area
  await page.locator('#scene').focus();      // held until 0.6 m (frames crawl while levels stream in or Cycles shares the GPU)
  await page.keyboard.down('KeyW');
  await page.waitForFunction((y0) => window.viewer.S.y > y0 + 0.6, i.y, { timeout: 6000, polling: 50 }).catch(() => {});
  await page.keyboard.up('KeyW');
  const j = await info(page);
  check(j.y > i.y + 0.5 && Math.abs(j.x - i.x) < 0.05, `W walks into the house (y ${i.y.toFixed(2)} -> ${j.y.toFixed(2)})`);
  check(await page.evaluate(() => { const v = window.viewer; return !v.walk || v.G.isFree(v.walk, v.S.layer, v.S.x, v.S.y); }), 'position is inside the walkable area');
  // walking into a wall is blocked: face east (-90deg) in the front hall and push for 2 s
  await page.evaluate(() => { const S = window.viewer.S; S.x = 0; S.y = 3; S.yaw = -Math.PI / 2; });
  await page.keyboard.down('KeyW'); await page.waitForTimeout(2000); await page.keyboard.up('KeyW');
  i = await info(page);
  check(i.room === 'hallway' && i.x < 0.5, `wall stops the walker (x = ${i.x.toFixed(2)})`);

  // real openings: W through the open living-room door; the closed under-stairs door stays shut
  await page.evaluate(() => Object.assign(window.viewer.S, { x: 0, y: 4.09, yaw: -Math.PI / 2 }));
  await page.keyboard.down('KeyW'); await page.waitForTimeout(1500); await page.keyboard.up('KeyW');
  i = await info(page); check(i.room === 'living', `walks through the living-room doorway (${i.room}, x = ${i.x.toFixed(2)})`);
  await page.evaluate(() => Object.assign(window.viewer.S, { x: 0.57, y: 8.2, yaw: Math.PI }));
  await page.keyboard.down('KeyW'); await page.waitForTimeout(1200); await page.keyboard.up('KeyW');
  i = await info(page); check(i.room === 'hallway' && i.y > 7.68, `closed under-stairs door blocks (y = ${i.y.toFixed(2)})`);

  // room jump buttons + keys, and a walk-mode screenshot of every room
  await page.getByRole('button', { name: /^Living/ }).click(); await idle(page);
  i = await info(page); check(i.room === 'living', `room button -> living (${i.room})`);
  await page.keyboard.press('Digit6'); await idle(page);   // 6th room in the list
  i = await info(page); check(i.room === 'utility', `key 6 -> utility (${i.room})`);
  for (const id of await page.evaluate(() => Object.keys(window.viewer.vps))) {
    await page.evaluate((id) => window.viewer.jump(id), id); await idle(page);
    i = await info(page); check(i.room === id, `jump -> ${id} (${i.room})`);
    await shot(page, `walk_${id}.png`);
  }
  await page.evaluate(() => { const { S, G } = window.viewer; Object.assign(S, { anim: null, x: -0.3, y: 3.6, pitch: 0.12, yaw: G.dirYaw(0.87, 2.6) }); });
  await page.waitForTimeout(300); await shot(page, 'walk_stairs.png');      // the staircase, seen from the hall

  // 3D <-> plan registration: stand in every open doorway. The GLB's jambs must sit half a clear width either side
  // (model = house.json), the plan's wall poche must be open there and solid just past the jambs (plan = house.json),
  // and the plan marker must be drawn on that spot.
  const doors = await page.evaluate(async () => {
    const house = await (await fetch('assets/house.json')).json();       // a pocket door's leaf stands ~0.09 m out of its pocket
    return window.viewer.walk.portals.filter((q) => q.open !== false && q.layers.every((l) => l === 'G') && house.openings.some((o) => o.id === q.id && o.level !== 'X'))
      .map((q) => ({ id: q.id, c: q.center, n: q.normal, w: q.width, pocket: house.openings.find((o) => o.id === q.id).slideToward ? 0.1 : 0 }));
  });
  for (const d of doors) {
    const r = await page.evaluate(async (d) => {
      const { THREE, G, S, scene, planView: p } = window.viewer, [cx, cy] = d.c, ux = d.n[1], uy = -d.n[0], h = d.w / 2;
      Object.assign(S, { anim: null, x: cx, y: cy, pitch: -1.2, yaw: G.dirYaw(d.n[0], d.n[1]) });   // look down at the threshold
      Object.assign(p.v, { cx, cy, s: p.c.height / 4.5 }); p.dirty = true;        // zoom the plan on the doorway
      await new Promise((f) => requestAnimationFrame(() => requestAnimationFrame(f)));
      const ray = new THREE.Raycaster(); ray.far = 3;
      const jambs = [1, -1].map((s) => {
        ray.set(new THREE.Vector3(cx, 1.0, -cy), new THREE.Vector3(s * ux, 0, -s * uy));
        return ray.intersectObject(scene, true)[0]?.distance ?? 9;
      });
      const hatch = p.entities.filter((e) => e.type === 'hatch' && e.layer === 'A-WALL-PATT');
      const solid = (x, y) => hatch.some((e) => G.pointInPoly(x, y, e.pts));
      const [X, Y] = p.toScreen(S.x, S.y), px = p.c.getContext('2d').getImageData(Math.round(X), Math.round(Y), 1, 1).data;
      return { jambs, open: !solid(cx, cy), ends: [1, -1].map((s) => solid(cx + s * ux * (h + 0.04), cy + s * uy * (h + 0.04))),
        marker: px[0] > 200 && px[1] < 140 && px[2] < 110, room: document.querySelector('#plan-room').textContent };
    }, d);
    // linings / frames narrow the hole by up to 60 mm a side; nothing may stand inside the clear width or beyond the wall face
    const ok3d = r.jambs.every((j) => j > d.w / 2 - 0.065 - d.pocket && j < d.w / 2 + 0.01);
    check(ok3d && r.open && r.ends.every(Boolean) && r.marker,
      `doorway ${d.id}: 3D jambs ${r.jambs.map((j) => Math.round(j * 1000))} mm vs half width ${Math.round(d.w * 500)}; plan open ${r.open}, jambs solid ${r.ends}; marker on spot ${r.marker}`);
    await shot(page, `door_${d.id}.png`);
  }
  await page.evaluate(() => { window.viewer.planView.fit(); window.viewer.S.pitch = 0; });
  await page.evaluate(() => window.viewer.jump('dining')); await idle(page);

  // plan marker sits at the camera position (dot centre pixel = marker colour)
  const px = await page.evaluate(() => {
    const { planView: p, S } = window.viewer, [X, Y] = p.toScreen(S.x, S.y), d = p.c.getContext('2d').getImageData(Math.round(X), Math.round(Y), 1, 1).data;
    return [...d];
  });
  check(px[0] > 200 && px[1] < 140 && px[2] < 110, `plan marker drawn at the camera position (rgb ${px.slice(0, 3)})`);
  check((await page.textContent('#plan-room')).toLowerCase().includes('dining'), 'plan names the current room');
  await shot(page, 'plan_cad.png', '#plan');
  await page.click('#plan-theme'); await page.waitForTimeout(200);
  await shot(page, 'plan_paper.png', '#plan');
  await page.click('#plan-theme');

  // click-to-teleport into the kitchen
  const target = await page.evaluate(() => {
    const p = window.viewer.planView, r = p.c.getBoundingClientRect(), [X, Y] = p.toScreen(2.8, 7.0);
    return [r.left + (X * r.width) / p.c.width, r.top + (Y * r.height) / p.c.height];
  });
  await page.mouse.click(...target); await idle(page);
  i = await info(page); check(i.room === 'kitchen', `plan click teleports to the kitchen (${i.room} @ ${i.x.toFixed(2)},${i.y.toFixed(2)})`);
  await shot(page, 'teleport_kitchen.png');
  // click into a wall lands on the nearest free point
  await page.evaluate(() => window.viewer.teleport(0.725, 3.0)); await idle(page);
  i = await info(page); check(['hallway', 'living'].includes(i.room), `teleport into a wall snaps to a free spot (${i.room})`);

  // dollhouse
  await page.click('#mode-orbit'); await page.waitForTimeout(1200);
  i = await info(page); check(i.mode === 'orbit', 'dollhouse mode on');
  await shot(page, 'orbit.png');
  await page.evaluate(() => window.viewer.jump('living')); await page.waitForTimeout(600);
  await shot(page, 'orbit_living.png');
  await page.evaluate(() => { const { orbit, camera } = window.viewer; orbit.target.set(0.7, 1.5, -4); camera.position.set(-0.6, 4.2, -2.4); });
  await page.waitForTimeout(600); await shot(page, 'orbit_closeup.png');           // section caps on the cut walls
  const before = await page.evaluate(() => window.viewer.orbit.target.toArray());
  await page.mouse.click(...target); await page.waitForTimeout(300);
  const after = await page.evaluate(() => window.viewer.orbit.target.toArray());
  check(Math.hypot(after[0] - before[0], after[2] - before[2]) > 0.5, 'plan click moves the dollhouse target');
  await page.keyboard.press('KeyO'); await page.waitForTimeout(500);
  i = await info(page); check(i.mode === 'walk' && i.room === 'kitchen', `back to walk where the dollhouse pointed (${i.room})`);

  await page.keyboard.press('Shift+Slash'); await page.waitForTimeout(300);
  check(await page.evaluate(() => document.querySelector('#help').open), 'help opens with ?');
  await shot(page, 'help.png'); await page.keyboard.press('Escape');
  await page.click('#plan-max'); await page.waitForTimeout(400); await shot(page, 'plan_max.png');
  await page.click('#plan-theme'); await page.waitForTimeout(300); await shot(page, 'plan_max_paper.png'); await page.click('#plan-theme');
  // downloads: the buttons hand over the real files
  const stem = SCHEMA === 2 ? 'house-plans' : 'ground-floor-plan';           // schema 1 ships the single ground-floor drawing
  for (const [sel, name, magic] of [['#dl-dxf', `${stem}.dxf`, 'SECTION'], ['#dl-pdf', `${stem}.pdf`, '%PDF']]) {
    const [dl] = await Promise.all([page.waitForEvent('download'), page.click(sel)]);
    const body = await readFile(await dl.path());
    check(dl.suggestedFilename() === name && body.length > 10000 && body.toString('latin1', 0, 24).includes(magic), `${name} downloads (${body.length} bytes)`);
  }
  await page.click('#plan-max');
  check(await page.isVisible('#btn-gallery'), 'Renders button shown when renders/index.json exists');
  await page.click('#btn-gallery'); await page.waitForTimeout(300); await shot(page, 'gallery.png');
  await page.click('#gallery .grid button'); await page.waitForTimeout(300); await page.keyboard.press('ArrowRight'); await page.waitForTimeout(300);
  check((await page.getAttribute('#gallery .lightbox img', 'src')).endsWith('b.jpg'), 'lightbox opens and arrow keys step through renders');
  await shot(page, 'lightbox.png'); await page.keyboard.press('Escape');
  await ctx.close();
}
// ---- views matching the Cycles reference stills (960x540, vfov 70, UI hidden) for lightmap calibration ----
if (run('ref')) {
  const { ctx, page } = await open({ viewport: { width: 960, height: 540 } });
  await page.addStyleTag({ content: '#topbar,#plan,#hint,#pad{display:none!important}' });
  for (const [tag, pos, room] of [['hall', [0, 3], null], ['living', [1.25, 4.09], 'living']]) {
    await page.evaluate(([pos, room]) => {
      const { S, G, rooms } = window.viewer, c = room ? G.centroid(rooms.find((r) => r.id === room).polygon) : [pos[0], pos[1] + 1];
      Object.assign(S, { anim: null, x: pos[0], y: pos[1], pitch: 0, yaw: G.dirYaw(c[0] - pos[0], c[1] - pos[1]) });
    }, [pos, room]);
    await page.waitForTimeout(400); await shot(page, `ref_${tag}_viewer.png`);
  }
  await ctx.close();
}
// ---- real-time fallback lighting ----
if (run('realtime')) {
  const { ctx, page } = await open({ viewport: { width: 1280, height: 800 } }, '?lighting=realtime');
  check((await info(page)).realtime, 'realtime fallback active with ?lighting=realtime');
  await page.evaluate(() => window.viewer.jump('living')); await page.waitForTimeout(1500);
  await shot(page, 'realtime_living.png');
  await ctx.close();
}
// ---- phone ----
if (run('phone')) {
  const { ctx, page } = await open({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true });
  check(await page.evaluate(() => document.body.classList.contains('touch')), 'touch UI on a phone');
  const lmMax = await page.evaluate(() => { let m = 0; window.viewer.scene.traverse((o) => { if (o.isMesh) for (const x of [].concat(o.material)) if (x.lightMap?.image) m = Math.max(m, x.lightMap.image.width, x.lightMap.image.height); }); return m; });
  check(lmMax > 0 && lmMax <= 1024, `phone: lightmap atlases over 1024 px are drawn down on load (largest ${lmMax} px)`);
  await shot(page, 'phone.png');
  // move pad: hold the knob forward for 1 s
  const i0 = await info(page), pad = await page.locator('#pad').boundingBox();
  const cdp = await ctx.newCDPSession(page), cx = pad.x + pad.width / 2, cy = pad.y + pad.height / 2;
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: cx, y: cy }] });
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: cx, y: cy - 40 }] });
  await page.waitForTimeout(1000);
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
  const i1 = await info(page);
  check(i1.y > i0.y + 0.3, `touch pad walks forward (y ${i0.y.toFixed(2)} -> ${i1.y.toFixed(2)})`);
  await page.tap('#plan-toggle'); await page.waitForTimeout(200); await shot(page, 'phone_plan_collapsed.png');
  await page.tap('#plan-toggle'); await page.tap('#plan-max'); await page.waitForTimeout(400); await shot(page, 'phone_plan_max.png');
  // tap the plan: teleports on touch too
  const tap = await page.evaluate(() => {
    const p = window.viewer.planView, r = p.c.getBoundingClientRect(), [X, Y] = p.toScreen(1.2, 14.6);
    return [r.left + (X * r.width) / p.c.width, r.top + (Y * r.height) / p.c.height];
  });
  await page.touchscreen.tap(...tap); await idle(page);
  const i2 = await info(page); check(i2.room === 'dining', `tap on the plan teleports (${i2.room})`);
  await page.tap('#plan-max'); await page.tap('#mode-orbit'); await page.waitForTimeout(800); await shot(page, 'phone_orbit.png');
  await ctx.close();
}
// ---- interactions + mouse navigation, on the real tags of the published GLB (node extras `ix`, blender/INTERACT.md) ----
// up to 60 triangle centres on a group's visible meshes, spread over its surface (largest triangles first): points a
// ray can really hit, unlike box samples that fall inside a carcass or between curtains
const surf = (id) => {
  const { THREE, scene, ix } = window.viewer, tris = [], a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3();
  scene.traverse((m) => {
    if (!m.isMesh || ix.groupOf(m) !== id) return;
    for (let o = m; o; o = o.parent) if (!o.visible) return;
    const pos = m.geometry.attributes.position, idx = m.geometry.index, n = (idx ? idx.count : pos.count) / 3, step = Math.max(1, Math.floor(n / 400));
    for (let t = 0; t < n; t += step) {
      const [i, j, k] = [0, 1, 2].map((q) => (idx ? idx.getX(3 * t + q) : 3 * t + q));
      a.fromBufferAttribute(pos, i).applyMatrix4(m.matrixWorld); b.fromBufferAttribute(pos, j).applyMatrix4(m.matrixWorld); c.fromBufferAttribute(pos, k).applyMatrix4(m.matrixWorld);
      tris.push([b.clone().sub(a).cross(c.clone().sub(a)).length(), a.clone().add(b).add(c).multiplyScalar(1 / 3)]);
    }
  });
  tris.sort((p, q) => q[0] - p[0]);
  const out = [], k = Math.max(1, Math.floor(tris.length / 60));
  for (let i = 0; i < tris.length && out.length < 60; i += k) out.push(tris[i][1]);
  return out;
};
const inPage = (page) => page.evaluate(`window.__surf = ${surf}`);
const settle = (page, ms = 0) => page.evaluate((ms) => new Promise((f) => setTimeout(() => requestAnimationFrame(() => requestAnimationFrame(f)), ms)), ms);
// stand 0.8..2.4 m from a group where some point of it is in plain sight at eye height and look at that point; [x, y] or null
const approach = (page, id) => page.evaluate((id) => {
  const { THREE, G, S, walk, ix, castRay } = window.viewer, pts = window.__surf(id).slice(0, 50), [tx, ty] = G.threeToPlan(ix.box(id).getCenter(new THREE.Vector3()));
  for (const R of [1.1, 0.8, 1.4, 1.8, 2.4]) for (let k = 0; k < 36; k++) {
    const a = (k / 36) * 2 * Math.PI, x = tx + R * Math.cos(a), y = ty + R * Math.sin(a), eye = new THREE.Vector3(x, 1.6, -y);
    if (!G.isFree(walk, S.layer, x, y)) continue;
    for (const p of pts) {
      const dir = p.clone().sub(eye), hit = castRay(eye, dir.clone().normalize(), dir.length() + 0.3);
      if (!hit || ix.groupOf(hit.object) !== id) continue;
      const [hx, hy] = G.threeToPlan(hit.point);
      Object.assign(S, { anim: null, glide: null, x, y, yaw: G.dirYaw(hx - x, hy - y), pitch: Math.atan2(hit.point.y - 1.6, Math.hypot(hx - x, hy - y)) });
      return [x, y];
    }
  }
  return null;
}, id);
// a screen pixel whose ray really hits the group (tried over points on its surface), or null
const pixelOf = (page, id) => page.evaluate((id) => {
  const { camera, castAt, ix, renderer } = window.viewer, r = renderer.domElement.getBoundingClientRect();
  camera.updateMatrixWorld();
  for (const p of window.__surf(id)) {
    p.project(camera);
    if (Math.abs(p.x) > 0.95 || Math.abs(p.y) > 0.95 || p.z > 1) continue;
    const X = r.left + ((p.x + 1) / 2) * r.width, Y = r.top + ((1 - p.y) / 2) * r.height;
    if (document.elementFromPoint(X, Y) !== renderer.domElement) continue;        // under the plan, the top bar, the pad
    const hit = castAt(X, Y);
    if (hit && ix.groupOf(hit.object) === id) return [X, Y];
  }
  return null;
}, id);
// mean luminance (0..255) of the frame as rendered right now (render + read back in one task, so the buffer is valid)
const meanLum = (page) => page.evaluate(() => {
  const { renderer, scene, camera } = window.viewer, c = Object.assign(document.createElement('canvas'), { width: 192, height: 120 }), g = c.getContext('2d');
  renderer.render(scene, camera); g.drawImage(renderer.domElement, 0, 0, 192, 120);
  const d = g.getImageData(0, 0, 192, 120).data; let s = 0;
  for (let i = 0; i < d.length; i += 4) s += 0.2126 * d[i] + 0.7152 * d[i + 1] + 0.0722 * d[i + 2];
  return s / (d.length / 4);
});
// first pixel down column X whose ray hits bare floor (not a step or a skirting); to = where a double-click should end
const floorAim = (page, X, Ys) => page.evaluate(([X, Ys]) => {
  const { castAt, G, walk, renderer, S } = window.viewer;
  for (const Y of Ys) {
    const hit = document.elementFromPoint(X, Y) === renderer.domElement && castAt(X, Y);
    const n = hit?.face?.normal.clone().transformDirection(hit.object.matrixWorld);
    if (n && n.y > 0.7 && hit.point.y < 0.3) { const p = G.threeToPlan(hit.point); return { X, Y, to: G.nearestFree(walk, S.layer, p[0], p[1], 1.5) }; }
  }
  return { X, Y: Ys[0], to: null };
}, [X, Ys]);
const groups = (page) => page.evaluate(() => window.viewer.ix.groups());
const stateOf = (page, id) => page.evaluate((id) => window.viewer.ix.state(id), id);
const centreOf = (page, id) => page.evaluate((id) => window.viewer.ix.box(id).getCenter(new window.viewer.THREE.Vector3()).toArray(), id);
const skip = (what) => console.log(`SKIP  ${what}`);

if (run('ix')) {
  let i;
  const { ctx, page } = await open({ viewport: { width: 1440, height: 900 } });
  await inPage(page);
  await page.evaluate(() => window.viewer.streaming);     // every level's groups (the bedroom TVs are on level 1)
  const gs = await groups(page), byId = new Map(gs.map((g) => [g.id, g])), kinds = {};
  for (const g of gs) kinds[g.kind] = (kinds[g.kind] || 0) + 1;
  console.log(`ix: ${gs.length} groups ${JSON.stringify(kinds)}, ${(await page.evaluate(() => window.viewer.ix.clocks())).length} clock hands`);
  check(gs.length > 50 && gs.every((g) => typeof g.hint === 'string' && g.hint), 'interaction groups built from the GLB tags, each with a hint label');
  check(['move', 'light', 'lamp', 'tv', 'water', 'flame', 'curtain'].every((k) => kinds[k]), `every kind of thing is operable (${Object.keys(kinds)})`);
  const shown = await page.evaluate(() => { const bad = []; window.viewer.scene.traverse((o) => { if (typeof o.userData.ix !== 'string') return; const d = JSON.parse(o.userData.ix); if (d.t === 'show' && o.visible !== (d.when === 0)) bad.push(o.userData.name); }); return bad; });
  check(!shown.length, `at load every state-1 object is hidden and every state-0 one shown (${shown})`);
  const hintOf = (id) => byId.get(id)?.hint;
  check(hintOf('vestibule.d_street.leaf.0') === 'Open front door' && hintOf('utility.switch.light') === 'Turn WC light off' && hintOf('wc.pan.seat') === 'Lift toilet seat'
    && hintOf('kitchen.switch') === 'Lights off' && hintOf('living.tv') === 'Switch TV on', `hint labels (${['vestibule.d_street.leaf.0', 'utility.switch.light', 'wc.pan.seat', 'kitchen.switch', 'living.tv'].map(hintOf)})`);
  await page.mouse.move(700, 450);
  await page.locator('#scene').focus();
  const toggle = (id) => page.evaluate((id) => window.viewer.ix.toggle(id), id);
  const openOf = (id) => page.evaluate((id) => window.viewer.ix.groups().find((g) => g.id === id).open, id);
  const visible = (names) => page.evaluate((names) => { const v = {}; window.viewer.scene.traverse((o) => { if (names.includes(o.userData.name)) v[o.userData.name] = o.visible; }); return names.map((n) => v[n]); }, names);

  // A. a door: hover hint + pointer, click toggles leaf and doorway (shut = impassable), Space toggles it back
  const portalIds = await page.evaluate(() => window.viewer.walk.portals.map((p) => p.id));
  const doors = gs.filter((g) => g.blocks.some((b) => portalIds.includes(b)));
  const door = doors.find((g) => g.blocks.includes('d_kitchen')) || doors[0];
  if (!door) skip('door: no leaf blocks a walkable doorway');
  else {
    const pid = door.blocks.find((b) => portalIds.includes(b));
    const doorway = () => page.evaluate((id) => { const { walk, G } = window.viewer, p = walk.portals.find((q) => q.id === id); return { open: p.open !== false, free: G.isFree(walk, p.layers[0], ...p.center) }; }, pid);
    check(!!(await approach(page, door.id)), `stands in sight of ${door.id}`); await settle(page, 100);
    const d0 = await doorway(), c0 = await centreOf(page, door.id), px = await pixelOf(page, door.id);
    check(d0.open === door.open && d0.free === d0.open, `doorway ${pid} starts ${d0.open ? 'passable' : 'shut'}, like its leaf`);
    if (!px) check(false, `a pixel on ${door.id}`);
    else {
      await page.mouse.move(...px); await settle(page, 120); await shot(page, 'ix_door_0.png');
      const tip = await page.evaluate(() => ({ text: document.querySelector('#ix-tip').textContent, shown: !document.querySelector('#ix-tip').hidden, cursor: document.querySelector('#scene').style.cursor }));
      check(tip.shown && /^(Open|Close) door$/.test(tip.text) && tip.cursor === 'pointer', `hover: pointer cursor and label "${tip.text}"`);
      await page.mouse.click(...px); await page.waitForTimeout(400); await idle(page);
      const d1 = await doorway(), c1 = await centreOf(page, door.id), moved = Math.hypot(c1[0] - c0[0], c1[2] - c0[2]);
      check((await stateOf(page, door.id)) === 1 && d1.open === !d0.open && d1.free === d1.open, `click toggles the leaf and its doorway (passable ${d0.open} -> ${d1.open})`);
      check(moved > 0.15, `the leaf swings (centre moves ${Math.round(moved * 1000)} mm)`);
      await page.mouse.move(700, 20); await settle(page, 120); await shot(page, 'ix_door_1.png');   // pointer off the scene
      await approach(page, door.id); await page.evaluate(() => { window.viewer.S.pitch -= 0.25; }); await settle(page, 250);  // in reach of the shut leaf, aimed a little off it
      const pre = await groups(page);
      await page.locator('#scene').focus(); await page.keyboard.press('Space'); await idle(page);
      const changed = (await groups(page)).filter((g, k) => g.state !== pre[k].state).map((g) => g.id);
      check((await stateOf(page, door.id)) === 0 && (await doorway()).open === d0.open, `Space toggles the door in front back (toggled: ${changed})`);
    }
    // shut on a walker standing in the doorway: they are let out, and a shut door is no route
    if (!(await openOf(door.id))) { await toggle(door.id); await idle(page); }
    const inDoor = await page.evaluate((id) => { const { S, walk } = window.viewer, p = walk.portals.find((q) => q.id === id); Object.assign(S, { anim: null, glide: null, x: p.center[0], y: p.center[1] }); return p.center; }, pid);
    await toggle(door.id); await idle(page, 300);
    const out = await page.evaluate((c) => { const { S, G, walk } = window.viewer; return { free: G.isFree(walk, S.layer, S.x, S.y), d: Math.hypot(S.x - c[0], S.y - c[1]) }; }, inDoor);
    check(out.free && out.d > 0.1, `closing the door on the walker moves them out of the doorway (${Math.round(out.d * 1000)} mm)`);
    if (pid === 'd_kitchen') {
      const shut = await page.evaluate(() => window.viewer.G.route(window.viewer.walk, { x: 0, y: 3, layer: 'G' }, { x: 2.8, y: 7.0, layer: 'G' }));
      await toggle(door.id); await idle(page);
      const open = await page.evaluate(() => window.viewer.G.route(window.viewer.walk, { x: 0, y: 3, layer: 'G' }, { x: 2.8, y: 7.0, layer: 'G' }));
      check(shut === null && !!open, 'no route into the kitchen while its door is shut, one once it is open');
    } else { await toggle(door.id); await idle(page); }
  }

  // A2. the pocket door slides shut across its doorway and back
  {
    const id = 'utility.d_wc.leaf', c0 = await centreOf(page, id);
    await toggle(id); await idle(page);
    const c1 = await centreOf(page, id), shut = await page.evaluate(() => window.viewer.walk.portals.find((p) => p.id === 'd_wc').open === false);
    check(shut && Math.hypot(c1[0] - c0[0], c1[2] - c0[2]) > 0.4, `${id} slides shut (${Math.round(Math.hypot(c1[0] - c0[0], c1[2] - c0[2]) * 1000)} mm) and closes d_wc`);
    await toggle(id); await idle(page);
  }

  // B. a cupboard door: hover label, click opens it about its hinge
  {
    const id = 'kitchen.base.hob.h2';
    check(!!(await approach(page, id)), `stands in sight of ${id}`); await settle(page, 100);
    const c0 = await centreOf(page, id), px = await pixelOf(page, id);
    if (!px) check(false, `a pixel on ${id}`);
    else {
      await page.mouse.move(...px); await settle(page, 120);
      const tip = await page.evaluate(() => document.querySelector('#ix-tip').textContent);
      await shot(page, 'ix_cupboard_0.png');
      await page.mouse.click(...px); await page.waitForTimeout(400); await idle(page);
      const c1 = await centreOf(page, id), moved = Math.hypot(c1[0] - c0[0], c1[1] - c0[1], c1[2] - c0[2]);
      check(tip === 'Open cupboard' && (await stateOf(page, id)) === 1 && moved > 0.08, `"${tip}": click opens ${id} (centre moves ${Math.round(moved * 1000)} mm)`);
      await page.mouse.move(700, 20); await settle(page, 120); await shot(page, 'ix_cupboard_1.png'); await toggle(id); await idle(page);
    }
  }
  // B2. a drawer at knee height is within reach of Space (reach is measured from the body, not the eye)
  {
    const id = 'vestibule.stool.drawer.0';
    check(!!(await approach(page, id)), `stands in sight of ${id}`); await page.mouse.move(700, 20); await settle(page, 100);
    const c0 = await centreOf(page, id);
    await page.locator('#scene').focus(); await page.keyboard.press('Space'); await idle(page);
    const c1 = await centreOf(page, id), moved = Math.hypot(c1[0] - c0[0], c1[2] - c0[2]);
    check((await stateOf(page, id)) === 1 && moved > 0.25, `Space opens the low ${id} (slides ${Math.round(moved * 1000)} mm)`);
    await shot(page, 'ix_drawer.png'); await toggle(id); await idle(page);
  }
  // B3. excl: fronts whose swings cross are never open together - opening one shuts the other first
  {
    await toggle('kitchen.dishwasher'); await idle(page);
    await toggle('kitchen.base.hob.drawer.2'); await idle(page);
    check(!(await openOf('kitchen.dishwasher')) && (await openOf('kitchen.base.hob.drawer.2')), 'opening the hob drawer shuts the dishwasher (excl)');
    await toggle('kitchen.base.hob.drawer.2'); await idle(page);
  }

  // C. both TVs: the picture is drawn by code, moves, and goes away again
  for (const tv of gs.filter((g) => g.kind === 'tv')) {
    await toggle(tv.id); await page.waitForTimeout(400);
    await approach(page, tv.id); await page.waitForTimeout(1000);
    const frame = () => page.evaluate((id) => {
      const c = window.viewer.ix.tvCanvas(id), d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data; let s = 0, h = 0;
      for (let i = 0; i < d.length; i += 4) { s += d[i] + d[i + 1] + d[i + 2]; h = (h * 31 + d[i] + d[i + 1] * 7 + d[i + 2] * 13) | 0; }
      return { mean: s / (d.length * 0.75), h };
    }, tv.id);
    const a = await frame(); await page.waitForTimeout(700); const b = await frame();
    const pic = tv.nodes.filter((n) => /picture/.test(n));
    check(a.h !== b.h && a.mean > 30 && (await visible(pic)).every(Boolean), `${tv.id}: picture shown and animating (mean ${a.mean.toFixed(0)}, two frames differ)`);
    await shot(page, `ix_${tv.id.replace(/\W+/g, '_')}_on.png`); await toggle(tv.id); await idle(page);
    check((await stateOf(page, tv.id)) === 0 && !(await visible(pic)).some(Boolean), `${tv.id} switches off`);
  }

  // C2. every other effect group - taps (water), hob burners (flame), fridge / oven lights (glow), curtains (cross-fade):
  // its state-1 objects appear and its state-0 objects go, and back
  const fxg = gs.filter((g) => g.fx.length && g.kind !== 'tv');
  const shows = await page.evaluate((ids) => { const o = {}; window.viewer.scene.traverse((n) => { if (typeof n.userData.ix !== 'string') return; const d = JSON.parse(n.userData.ix); if (d.t === 'show' && ids.includes(d.g)) (o[d.g] ||= []).push([n.userData.name, d.when]); }); return o; }, fxg.map((g) => g.id));
  // what each group shows must match the state it is in: opening one may shut another (`excl`: the fridge door shuts the
  // ovens it would hit), so the check follows the states rather than assuming every group ended up open
  const fxState = async () => { const bad = [], st = new Map((await groups(page)).map((g) => [g.id, g.state])); for (const g of fxg) { const v = await visible(shows[g.id].map((s) => s[0])); shows[g.id].forEach(([n, w], k) => { if (v[k] !== (w === st.get(g.id))) bad.push(n); }); } return bad; };
  for (const g of fxg) if ((await stateOf(page, g.id)) === 0) await toggle(g.id);
  await idle(page, 300);
  const opened = (await groups(page)).filter((g) => g.state === 1 && fxg.some((f) => f.id === g.id)).length, badOn = await fxState();
  await page.evaluate(() => window.viewer.jump('kitchen')); await idle(page);
  await page.evaluate(() => { const { S, G } = window.viewer; Object.assign(S, { x: 3.0, y: 6.65, yaw: G.dirYaw(0.8, -0.05), pitch: -0.55 }); }); await settle(page, 150);
  await shot(page, 'ix_hob_on.png');
  for (const g of fxg) if ((await stateOf(page, g.id)) === 1) await toggle(g.id);
  await idle(page);
  const badOff = await fxState();
  check(!badOn.length && !badOff.length && opened > fxg.length / 2 && (await groups(page)).filter((g) => fxg.some((f) => f.id === g.id)).every((g) => g.state === 0),
    `${fxg.length} effect groups (${[...new Set(fxg.map((g) => g.kind))]}): ${opened} on at once, each shows its state-1 objects and hides them again (${badOn}${badOff})`);

  // C3. the toilet seat lifts
  {
    const id = 'wc.pan.seat', c0 = await centreOf(page, id);
    await toggle(id); await idle(page);
    const c1 = await centreOf(page, id);
    check(c1[1] - c0[1] > 0.12, `${id} lifts (centre rises ${Math.round((c1[1] - c0[1]) * 1000)} mm)`);
    await toggle(id); await idle(page);
  }

  // D. clock hands follow the visitor's local time
  const hands = await page.evaluate(() => {
    const d = new Date(), m = d.getMinutes() + (d.getSeconds() + d.getMilliseconds() / 1000) / 60, h = (d.getHours() % 12) + m / 60;
    return window.viewer.ix.clocks().map((c) => {
      const want = 2 * Math.PI * { h: h / 12, m: m / 60, s: d.getSeconds() / 60 }[c.hand];
      return { ...c, err: Math.abs(Math.atan2(Math.sin(c.angle - want), Math.cos(c.angle - want))) };
    });
  });
  if (!hands.length) skip('clock: no clock hands');
  else check(hands.every((c) => c.err < (c.hand === 's' ? 0.12 : 0.01)), `clock hands at local time (${hands.map((c) => `${c.name} ${c.hand} err ${c.err.toFixed(4)} rad`).join(', ')})`);

  // E. a light switch: the room's bake dims to the lights-off set and comes back
  const light = gs.find((g) => g.kind === 'light' && g.rooms.includes('kitchen')) || gs.find((g) => g.kind === 'light');
  if (!light) skip('lights: no switch');
  else {
    await page.evaluate((r) => window.viewer.jump(r), light.rooms[0]); await idle(page, 400);
    const on = await meanLum(page); await shot(page, 'ix_lights_on.png');
    await toggle(light.id); await idle(page);
    const off = await meanLum(page), hint = (await groups(page)).find((g) => g.id === light.id).hint; await shot(page, 'ix_lights_off.png');
    check(off < on * 0.75 && hint === 'Lights on', `${light.id}: ${light.rooms} lights off darkens the view (mean ${on.toFixed(1)} -> ${off.toFixed(1)}), hint "${hint}"`);
    await toggle(light.id); await idle(page);
    const back = await meanLum(page);
    check(Math.abs(back - on) < on * 0.04, `... and back on (${back.toFixed(1)})`);
  }
  // E2. switches act on the rooms they are wired to (the WC light switch is in the utility); lamps go dark with their room,
  // the table lamp on its own plug included, and come back
  {
    const lit = () => page.evaluate(() => Object.fromEntries([...window.viewer.roomLights].map(([r, L]) => [r, L.target])));
    await toggle('utility.switch.light'); await idle(page);
    const l1 = await lit();
    check(l1.wc === 0 && l1.utility === 1, `utility.switch.light switches the WC (wc ${l1.wc}, utility ${l1.utility})`);
    await toggle('utility.switch.light'); await idle(page);
    await page.evaluate(() => window.viewer.jump('living')); await idle(page, 200);
    // with circuits (manifest.circuits) the dimmer's spotlight knob switches the downlights only; then the room goes dark
    // through each lamp's own circuit instead
    const own = (await groups(page)).find((g) => g.id === 'living.dimmer')?.circuits.length > 0;
    const lamps = (await groups(page)).filter((g) => g.kind === 'lamp' && (g.rooms.includes('living') || g.home === 'living'));
    for (const id of own ? ['living.dimmer', ...lamps.filter((g) => g.circuits.length).map((g) => g.id)] : ['living.dimmer']) await toggle(id);
    await idle(page);
    const glow = await page.evaluate(() => { let s = 0; window.viewer.scene.traverse((o) => { if (o.isMesh && /living\.(sconce|table_lamp)/.test(o.userData.name || o.parent?.userData.name || '')) for (const m of [].concat(o.material)) s += m.emissiveIntensity > 0 && m.emissive && m.emissive.r + m.emissive.g > 0 ? m.emissiveIntensity : 0; }); return s; });
    await shot(page, 'ix_living_off.png');
    check(lamps.length >= 3 && (await groups(page)).filter((g) => lamps.some((l) => l.id === g.id)).every((g) => g.state === 1) && glow < 1e-3,
      `living lights off${own ? ' (each circuit)' : ''}: ${lamps.map((g) => g.id)} dark (emissive sum ${glow.toFixed(3)})`);
    for (const id of own ? ['living.dimmer', ...lamps.filter((g) => g.circuits.length).map((g) => g.id)] : ['living.dimmer']) await toggle(id);
    await idle(page);
    check((await groups(page)).filter((g) => lamps.some((l) => l.id === g.id)).every((g) => g.state === 0), '... and lit again with the room');
  }
  // E3. per-circuit lights (manifest.circuits): a dining knob switches only its own fittings and their part of the bake
  const circ = await page.evaluate(() => (window.viewer.roomLights.get('dining')?.circuits || []).map((c) => c.name));
  if (circ.length < 2) skip('per-circuit lights: no circuits in this manifest');
  else {
    const view = () => page.evaluate(() => Object.assign(window.viewer.S, { anim: null, glide: null, x: -0.35, y: 14.6, yaw: -Math.PI / 2, pitch: 0.05 }));  // facing the sconce wall (+X)
    await page.evaluate(() => window.viewer.jump('dining')); await idle(page, 300); await view(); await idle(page, 300);
    const st = () => page.evaluate(() => ({ c: Object.fromEntries(window.viewer.roomLights.get('dining').circuits.map((c) => [c.name, c.target])),
      g: Object.fromEntries(window.viewer.ix.groups().filter((g) => /^dining\.(sconce|chandelier|switch)/.test(g.id)).map((g) => [g.id, g.state])) }));
    // glow of the fittings' own emissive parts, by fitting
    const glow = () => page.evaluate(() => { const s = { sconce: 0, chandelier: 0 }; window.viewer.scene.traverse((o) => { const n = o.userData.name || o.parent?.userData.name || '', k = /^dining\.sconce/.test(n) ? 'sconce' : /^dining\.chandelier/.test(n) ? 'chandelier' : null;
      if (o.isMesh && k) for (const m of [].concat(o.material)) s[k] += m.emissive && m.emissive.r > 0 ? m.emissiveIntensity : 0; }); return s; });
    const on = await meanLum(page), g0 = await glow(); await shot(page, 'ix_dining_circuits_on.png');
    await toggle('dining.switch.wall_lights'); await idle(page);
    const wall = await st(), g1 = await glow(); await shot(page, 'ix_dining_wall_off.png');
    check(wall.c.wall === 0 && wall.c.main === 1 && wall.c.chandelier === 1 && wall.g['dining.sconce.0'] === 1 && wall.g['dining.sconce.1'] === 1 && wall.g['dining.chandelier'] === 0
      && wall.g['dining.switch'] === 0 && g0.sconce > 0 && g1.sconce < 1e-3 && Math.abs(g1.chandelier - g0.chandelier) < 1e-6,
      `dining wall-light knob: only the wall circuit off (${JSON.stringify(wall.c)}), sconces dark (glow ${g0.sconce.toFixed(2)} -> ${g1.sconce.toFixed(3)}), chandelier lit (${g1.chandelier.toFixed(2)})`);
    await toggle('dining.switch'); await idle(page);
    const spots = await st(), ls = await meanLum(page); await shot(page, 'ix_dining_chandelier_only.png');
    check(spots.c.main === 0 && spots.c.chandelier === 1 && ls < on * 0.9 && ls > 1, `spotlight knob: the chandelier alone lights the room (${JSON.stringify(spots.c)}; view ${on.toFixed(1)} -> ${ls.toFixed(1)})`);
    await toggle('dining.chandelier'); await idle(page);
    const dark = await st(), ld = await meanLum(page), g2 = await glow(); await shot(page, 'ix_dining_all_off.png');
    check(dark.c.chandelier === 0 && dark.g['dining.switch.chandelier'] === 1 && g2.chandelier < 1e-3 && ld < ls, `clicking the chandelier switches its circuit, its knob follows (view ${ld.toFixed(1)})`);
    await toggle('dining.switch.wall_lights'); await idle(page);
    const lw = await meanLum(page); await shot(page, 'ix_dining_wall_only.png');
    check(lw > ld, `the wall lights alone add their light to the dark room (view ${ld.toFixed(1)} -> ${lw.toFixed(1)})`);
    for (const id of ['dining.switch', 'dining.switch.chandelier']) await toggle(id);
    await idle(page);
    const back = await meanLum(page);
    check(Math.abs(back - on) < on * 0.04, `... all circuits back on: the lights-on bake again (${back.toFixed(1)})`);
  }

  // F. double-click on the floor walks there (ring under the cursor first); the double-click operates nothing
  await page.evaluate(() => Object.assign(window.viewer.S, { anim: null, glide: null, x: 0, y: 3, yaw: 0, pitch: -0.3 })); await settle(page, 100);
  const states = (await groups(page)).map((g) => g.state).join();
  const aim = await floorAim(page, 720, [640, 680, 720, 600]);
  await page.mouse.move(aim.X, aim.Y); await settle(page, 80);
  const ring = await page.evaluate(() => window.viewer.ring.visible); await shot(page, 'ix_ring.png');
  await page.mouse.dblclick(aim.X, aim.Y); await page.waitForTimeout(300);
  await page.waitForFunction(() => !window.viewer.S.glide, null, { timeout: 10000 }).catch(() => {});
  i = await info(page);
  check(ring && aim.to && Math.hypot(i.x - aim.to[0], i.y - aim.to[1]) < 0.15,
    `double-click walks to the floor point (${aim.to?.map((v) => v.toFixed(2))} -> ${i.x.toFixed(2)}, ${i.y.toFixed(2)}; ring ${ring})`);
  check((await groups(page)).map((g) => g.state).join() === states, 'the double-click operated nothing');
  // ... on a wall: to the floor in front of it
  await page.evaluate(() => { const { S, G } = window.viewer; Object.assign(S, { anim: null, glide: null, x: 0, y: 3.3, yaw: G.dirYaw(-1, 0), pitch: 0 }); }); await settle(page, 100);
  await page.mouse.dblclick(720, 450); await page.waitForTimeout(300);
  await page.waitForFunction(() => !window.viewer.S.glide, null, { timeout: 10000 }).catch(() => {});
  i = await info(page);
  check(i.x < -0.1 && i.x > -0.52 && Math.abs(i.y - 3.3) < 0.1, `double-click on a wall walks up to it (x ${i.x.toFixed(2)})`);
  await page.evaluate(() => window.viewer.walkTo(1.2, 14.6)); await page.waitForTimeout(300);
  await page.keyboard.press('ArrowLeft');
  check(await page.evaluate(() => !window.viewer.S.glide), 'a key press stops the walk');
  // K. after a click on a toolbar button, Space uses the thing in front instead of pressing the button again
  await page.getByRole('button', { name: /^Kitchen/ }).click(); await idle(page);
  await approach(page, 'kitchen.wall.w1'); await page.mouse.move(700, 20); await settle(page, 100);
  await page.keyboard.press('Space'); await idle(page);
  check((await stateOf(page, 'kitchen.wall.w1')) === 1 && (await info(page)).room === 'kitchen', 'Space after clicking a room button opens the cupboard in front');
  await toggle('kitchen.wall.w1'); await idle(page);

  // G. wheel zoom (field of view, eased, clamped); the plan's view cone follows
  await page.mouse.move(720, 450); await page.mouse.wheel(0, -800); await page.waitForTimeout(700);
  const z1 = await page.evaluate(() => { const { camera, planView, G } = window.viewer; return { fov: camera.fov, hfov: planView.viewer.hfov, want: G.hfov(camera.fov, camera.aspect) }; });
  check(z1.fov < 45 && z1.fov >= 21.99 && Math.abs(z1.hfov - z1.want) < 0.02, `wheel zooms in (fov ${z1.fov.toFixed(1)}), the plan cone follows`);
  await shot(page, 'ix_zoom.png');
  await page.mouse.wheel(0, 5000); await page.waitForTimeout(900);
  const z2 = await page.evaluate(() => window.viewer.camera.fov);
  check(z2 > 85 && z2 <= 90.01, `wheel zooms out to the 90 deg limit (${z2.toFixed(1)})`);
  await page.evaluate(() => { window.viewer.S.fovT = window.viewer.FOV; }); await page.waitForTimeout(700);

  // H. narrow gaps, walked for real: both long sides of the dining table, past the kitchen bins, into the WC
  const gaps = await page.evaluate(async () => {
    const foot = await (await fetch('assets/footprints.json')).json(), list = Array.isArray(foot) ? foot : foot.items || [];
    const o = list.find((f) => f.name === 'dining.table')?.obb, xs = o?.map((p) => p[0]), ys = o?.map((p) => p[1]), ty = o && (Math.min(...ys) + Math.max(...ys)) / 2;
    return [...(o ? [['west side of the dining table', [Math.min(...xs) - 0.25, ty]], ['east side of the dining table', [Math.max(...xs) + 0.25, ty]]] : []),
      ['kitchen bins', [2.88, 8.5]], ['WC', [1.75, 9.75]], ['gap between the sofa and the coffee table', [2.2, 2.0]]];
  });
  for (const [what, p] of gaps) {
    const ok = await page.evaluate((p) => window.viewer.walkTo(...p), p);
    await page.waitForTimeout(300); await page.waitForFunction(() => !window.viewer.S.glide, null, { timeout: 15000 }).catch(() => {});
    i = await info(page);
    check(ok && Math.hypot(i.x - p[0], i.y - p[1]) < 0.2, `walks to the ${what} (${i.x.toFixed(2)}, ${i.y.toFixed(2)})`);
    await shot(page, `ix_gap_${what.replace(/\W+/g, '_')}.png`);
  }

  // I. the dollhouse: click operates too
  const target = door;
  if (target) {
    await page.evaluate(() => window.viewer.setMode('orbit')); await page.waitForTimeout(500);
    let px = null;
    for (const az of [0.8, 2.4, 3.9, 5.5]) {
      await page.evaluate(([id, az]) => {
        const { ix, orbit, camera, THREE } = window.viewer, c = ix.box(id).getCenter(new THREE.Vector3());
        orbit.target.copy(c); camera.position.set(c.x + 2.6 * Math.cos(az), c.y + 3.6, c.z + 2.6 * Math.sin(az)); orbit.update();
      }, [target.id, az]);
      await settle(page, 300);
      if ((px = await pixelOf(page, target.id))) break;
    }
    if (!px) check(false, `a pixel on ${target.id} in the dollhouse`);
    else {
      const s0 = await stateOf(page, target.id);
      await page.mouse.click(...px); await page.waitForTimeout(100); await idle(page);
      check((await stateOf(page, target.id)) !== s0, `click in the dollhouse toggles ${target.id}`);
      await shot(page, 'ix_dollhouse.png'); await toggle(target.id);
    }
    await page.evaluate(() => window.viewer.setMode('walk'));
  }
  await ctx.close();

  // J. touch: tap operates, double-tap walks
  {
    const { ctx, page } = await open({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
    await inPage(page);
    if (door && (await approach(page, door.id))) {
      await settle(page, 100);
      const px = await pixelOf(page, door.id), s0 = await stateOf(page, door.id);
      if (px) { await page.touchscreen.tap(...px); await page.waitForTimeout(400); await idle(page); }
      check(!!px && (await stateOf(page, door.id)) !== s0, 'a tap toggles the door on a phone');
      await shot(page, 'ix_phone_door.png');
    }
    await page.evaluate(() => Object.assign(window.viewer.S, { anim: null, glide: null, x: 0, y: 3, yaw: 0, pitch: -0.3 })); await settle(page, 100);
    const aim = await floorAim(page, 230, [700, 740, 660, 780, 620]);
    await page.touchscreen.tap(aim.X, aim.Y); await page.touchscreen.tap(aim.X, aim.Y); await page.waitForTimeout(300);
    await page.waitForFunction(() => !window.viewer.S.glide, null, { timeout: 10000 }).catch(() => {});
    i = await info(page);
    check(aim.to && Math.hypot(i.x - aim.to[0], i.y - aim.to[1]) < 0.15, `double-tap walks there (${aim.to?.map((v) => v.toFixed(2))} -> ${i.x.toFixed(2)}, ${i.y.toFixed(2)})`);
    // pinch: two fingers apart zoom in, together zoom out; nothing is operated
    const cdp = await ctx.newCDPSession(page), states = (await groups(page)).map((g) => g.state).join();
    const pinch = async (x0, dx) => {
      await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: 195 - x0, y: 620, id: 1 }, { x: 195 + x0, y: 620, id: 2 }] });
      for (let k = 1; k <= 8; k++) { await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: 195 - x0 - k * dx, y: 620, id: 1 }, { x: 195 + x0 + k * dx, y: 620, id: 2 }] }); await page.waitForTimeout(30); }
      await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] }); await page.waitForTimeout(800);
      return page.evaluate(() => window.viewer.camera.fov);
    };
    const f1 = await pinch(40, 8), f2 = await pinch(104, -8);
    check(f1 < 40 && f2 > 65 && (await groups(page)).map((g) => g.state).join() === states, `pinch zooms in and out (fov ${f1.toFixed(0)} -> ${f2.toFixed(0)}) and operates nothing`);
    await shot(page, 'ix_phone_hint.png');
    await ctx.close();
  }
}

// ---- schema 2: levels, layers, sheets, routes, dollhouse cut (MULTILEVEL.md 11.2, 11.3) ----
// the room bar: open group, the current room in view, floor chips, digits, PageUp / PageDown
const barState = (page) => page.evaluate(() => {
  const nav = document.querySelector('#rooms'), r = nav.getBoundingClientRect(), b = nav.querySelector('button[data-room][aria-current="true"]'), q = b?.offsetParent && b.getBoundingClientRect();
  return { open: [...nav.querySelectorAll('.grp.open')].map((g) => g.dataset.level).join(), shown: [...nav.querySelectorAll('button[data-room]')].filter((x) => x.offsetParent).map((x) => x.dataset.room),
    cur: b?.dataset.room ?? null, inView: !!q && q.left >= r.left - 1 && q.right <= r.right + 1 };
});
async function roomBar(page, tag) {
  const press = (sel) => (tag === 'phone' ? page.tap(sel) : page.click(sel));
  await page.evaluate(() => window.viewer.jump('hallway')); await idle(page, 200);
  const rooms = await page.evaluate(() => Object.fromEntries(['G', '1', 'X'].map((lv) => [lv, window.viewer.rooms.filter((r) => r.level === lv && window.viewer.vps[r.id]).map((r) => r.id)])));
  let b = await barState(page);
  check(b.open === 'G' && b.shown.join() === rooms.G.join() && b.cur === 'hallway' && b.inView, `${tag} room bar on G: only the ground-floor rooms, the hallway marked and in view (${b.shown.length} shown)`);
  await page.evaluate(() => window.viewer.jump('blue_bedroom')); await idle(page, 300);
  b = await barState(page);
  check(b.open === '1' && b.shown.join() === rooms['1'].join() && b.cur === 'blue_bedroom' && b.inView, `${tag} room bar follows to level 1, the blue bedroom marked and in view (${b.cur}, in view ${b.inView})`);
  await shot(page, `${tag}_roombar_1.png`);
  await press('#rooms .grp[data-level="X"] .lv'); await page.waitForTimeout(200);
  b = await barState(page);
  check(b.open === 'X' && b.shown.join() === rooms.X.join(), `${tag}: the OUT chip opens the outside rooms (${b.shown})`);
  if (tag === 'phone') {
    await press('#rooms button[data-room="garden"]'); await idle(page, 300);
    b = await barState(page); const i = await info(page);
    check(i.room === 'garden' && b.cur === 'garden' && b.inView, `${tag}: a tap on Garden jumps there, its button in view (${i.room})`);
  } else {
    await page.locator('#scene').focus(); await page.keyboard.press(`Digit${rooms.X.indexOf('garden') + 1}`); await idle(page, 300);
    const i = await info(page); check(i.room === 'garden', `a digit in the open OUT group jumps to the garden (${i.room})`);
    await page.keyboard.press('PageDown'); await page.waitForTimeout(150);
    b = await barState(page); check(b.open === '2', `PageDown opens the floor below in the bar (${b.open})`);
    await page.keyboard.press('PageUp'); await page.keyboard.press('PageUp'); await page.waitForTimeout(150);
    b = await barState(page); check(b.open === 'X', `PageUp opens the floor above, stopping at the last group (${b.open})`);
  }
  await shot(page, `${tag}_roombar_X.png`);
  await page.evaluate(() => window.viewer.jump('hallway')); await idle(page, 200);
}
// dollhouse state: what is drawn, and where the level's box lands in the part of the view the plan panel leaves free
const dollState = (page, id) => page.evaluate((id) => {
  const { THREE, camera, levelBox, dhMeshes, renderer, orbit, LEVELS } = window.viewer, b = levelBox(id), xs = [], ys = [];
  const plan = document.querySelector('#plan').getBoundingClientRect(), wide = innerWidth > 760;
  camera.updateMatrixWorld();
  for (const x of [b.minX, b.maxX]) for (const y of [b.minY, b.maxY]) for (const z of [b.z0, b.z1]) { const p = new THREE.Vector3(x, z, -y).project(camera); xs.push((p.x + 1) / 2 * innerWidth); ys.push((1 - p.y) / 2 * innerHeight); }
  const free = { l: wide ? plan.right : 0, t: wide ? 0 : plan.bottom, r: innerWidth, b: innerHeight }, dz = LEVELS.find((l) => l.id === id)?.datumZ ?? 0;
  const vis = dhMeshes.filter((d) => d.o.visible);
  return { inside: Math.min(...xs) >= free.l - 2 && Math.max(...xs) <= free.r + 2 && Math.min(...ys) >= free.t - 2 && Math.max(...ys) <= free.b + 2,
    fill: Math.max((Math.max(...xs) - Math.min(...xs)) / (free.r - free.l), (Math.max(...ys) - Math.min(...ys)) / (free.b - free.t)),
    neighbours: vis.filter((d) => d.room === 'neighbours').length, roofOver: vis.filter((d) => d.room === 'roof' && d.maxY > dz + 1.2).length, roof: vis.filter((d) => d.room === 'roof').length,
    planes: renderer.clippingPlanes.map((p) => p.constant), ty: orbit.target.y, d: camera.position.distanceTo(orbit.target) };
}, id);
// The owner's walking requests ("double click to move like street view", "zoom in/out", "walk through narrow areas") on
// the new floors and outside, with every door leaf open: W through the narrow doorways (the open leaves stand beside
// them), double-click to go on the stairs, a landing, the garden, the shed and the forecourt, wheel zoom on the stairs.
async function walkChecks(page) {
  for (const id of ['o_stair_foot', 'd_basement', 'd_loft', 'd_balcony', 'shed_d1', 'side_gate']) {
    // start 0.4 m off the wall on a free side, square to the opening, on its centre line; hold W
    const st = await page.evaluate((id) => {
      const { S, G, walk } = window.viewer, p = walk.portals.find((q) => q.id === id);
      for (const s of [1, -1]) for (const L of p?.layers || []) {
        const x = p.center[0] - s * p.normal[0] * (p.depth + 0.4), y = p.center[1] - s * p.normal[1] * (p.depth + 0.4);
        if (!G.isFree(walk, L, x, y)) continue;
        Object.assign(S, { anim: null, glide: null, x, y, layer: L, z: G.zAt(walk, L, x, y), yaw: G.dirYaw(s * p.normal[0], s * p.normal[1]), pitch: 0 });
        return { s, L, depth: p.depth, other: p.layers[0] === L ? p.layers[1] : p.layers[0], width: p.width };
      }
      return null;
    }, id);
    if (!st) { check(false, `W through ${id}: no free spot in front of it`); continue; }
    // how far past the opening's centre line the walker is, on the far side
    const past = `((() => { const { S, walk } = window.viewer, p = walk.portals.find((q) => q.id === ${JSON.stringify(id)}); return ((S.x - p.center[0]) * p.normal[0] + (S.y - p.center[1]) * p.normal[1]) * ${st.s}; })())`;
    await page.locator('#scene').focus(); await page.keyboard.down('KeyW');    // held until 0.6 m past the opening, 6 s at most
    await page.waitForFunction(`${past} > ${st.depth + 0.6}`, null, { timeout: 6000, polling: 50 }).catch(() => {});
    await page.keyboard.up('KeyW');
    const r = await page.evaluate(`({ across: ${past}, layer: window.viewer.S.layer, room: window.viewer.info().room })`);
    check(r.across > st.depth + 0.15 && r.layer === st.other, `W walks through ${id} (${Math.round(st.width * 1000)} mm): ${st.L} -> ${r.layer}, ${r.room}, ${r.across.toFixed(2)} m past its centre`);
    await shot(page, `gap_${id}.png`);
  }
  const pose = (s) => page.evaluate((s) => {
    const { S, G, walk } = window.viewer;
    if (s.portal) {                       // stand `back` m out of a doorway on the side that is not the target room, facing in
      const p = walk.portals.find((q) => q.id === s.portal);
      for (const k of [1, -1]) {
        const x = p.center[0] - k * p.normal[0] * s.back, y = p.center[1] - k * p.normal[1] * s.back, c = G.cellAt(walk, 'G', x, y);
        if (c && c.room !== s.room && G.isFree(walk, 'G', x, y)) return Object.assign(S, { anim: null, glide: null, x, y, layer: 'G', z: c.z, yaw: G.dirYaw(k * p.normal[0], k * p.normal[1]), pitch: s.pitch }) && true;
      }
      return false;
    }
    Object.assign(S, { anim: null, glide: null, x: s.x, y: s.y, layer: s.L, z: G.zAt(walk, s.L, s.x, s.y), yaw: s.yaw, pitch: s.pitch });
    return true;
  }, s);
  // the first pixel (scanning the lower middle of the view) whose double-click target lands on the wanted layer / room
  // at least `min` m away
  const aim = (want, min) => page.evaluate(([want, min]) => {
    const { castAt, targetOf, G, walk, S, renderer } = window.viewer;
    for (let fy = 0.5; fy < 0.96; fy += 0.04) for (const fx of [0.5, 0.42, 0.58, 0.34, 0.66, 0.26, 0.74]) {
      const X = innerWidth * fx, Y = innerHeight * fy;
      if (document.elementFromPoint(X, Y) !== renderer.domElement) continue;
      const t = targetOf(castAt(X, Y)), room = t && G.cellAt(walk, t.layer, ...t.p)?.room;
      if (t && (!want.layer || t.layer === want.layer) && (!want.room || room === want.room) && Math.hypot(t.p[0] - S.x, t.p[1] - S.y) >= min) return { X, Y, to: t.p, layer: t.layer, room };
    }
    return null;
  }, [want, min]);
  for (const [what, s, want, min] of [
    ['stairs', { L: 'G', x: 0.55, y: 4.4, yaw: 0, pitch: 0.25 }, { layer: 'stair_main' }, 1.0],
    ['landing', { jump: 'landing1_rear' }, { layer: '1' }, 1.0],
    ['garden', { jump: 'garden' }, { room: 'garden' }, 1.5],
    ['shed', { portal: 'shed_d1', back: 2.2, pitch: -0.35, room: 'shed' }, { room: 'shed' }, 2.5],
    ['forecourt', { jump: 'front' }, { room: 'front' }, 1.5]]) {
    if (s.jump) { await page.evaluate((id) => window.viewer.jump(id), s.jump); await idle(page, 200); await page.evaluate(() => { window.viewer.S.pitch = -0.3; }); }
    else check(await pose(s), `${what}: stands in front of it`);
    await settle(page, 150);
    const a = await aim(want, min);
    if (!a) { check(false, `double-click on the ${what}: no pixel lands on ${JSON.stringify(want)}`); await shot(page, `dbl_${what}_none.png`); continue; }
    await page.mouse.move(a.X, a.Y); await settle(page, 60);
    await page.mouse.dblclick(a.X, a.Y); await page.waitForTimeout(300);
    await page.waitForFunction(() => !window.viewer.S.glide, null, { timeout: 30000 }).catch(() => {});
    const i = await info(page);
    check(Math.hypot(i.x - a.to[0], i.y - a.to[1]) < 0.2 && i.layer === a.layer, `double-click on the ${what} walks there (${a.room} on ${a.layer} at ${a.to.map((v) => v.toFixed(2))} -> ${i.room} on ${i.layer} at ${i.x.toFixed(2)}, ${i.y.toFixed(2)})`);
    await shot(page, `dbl_${what}.png`);
    if (what === 'stairs') {              // wheel zoom works on the flight like anywhere else
      await page.mouse.move(720, 450); await page.mouse.wheel(0, -700); await page.waitForTimeout(700);
      const f = await page.evaluate(() => window.viewer.camera.fov);
      check(f < 50 && i.layer === 'stair_main', `wheel zooms in on the stairs (fov ${f.toFixed(1)})`);
      await page.evaluate(() => { window.viewer.S.fovT = window.viewer.FOV; }); await page.waitForTimeout(600);
    }
  }
}
// Interaction types the new rooms bring (blender/INTERACT.md), on test objects handed to the engine like a level GLB
// arriving: a shower spray (wide water cone), a fire pit flame (warm emissive), a glass sauna door, a bin lid on a
// horizontal axis, a clock hand, a TV, a lamp on its own plug, and a switch for rooms on two floors. The switch must
// fetch the lights-off bake of exactly its rooms and dim an upper floor like the ground floor.
async function syntheticIx(page) {
  const made = await page.evaluate(() => {
    const { THREE, ix, scene } = window.viewer, lv = new THREE.Group(), T = (x, y, z) => [x, z, -y];   // Blender -> three
    lv.name = 'level_test'; lv.userData.level = '2';
    const add = (name, geo, mat, at, tag, room = 'bathroom2') => { const m = new THREE.Mesh(geo, mat); m.position.set(...T(...at)); m.name = name.replace(/\./g, ''); Object.assign(m.userData, { name, room, ix: JSON.stringify(tag) }); lv.add(m); return m; };
    const std = (o = {}) => new THREE.MeshStandardMaterial({ color: 0x888888, ...o });
    add('test.shower.spray', new THREE.CylinderGeometry(0.02, 0.15, 0.9, 24, 1, true), std({ color: 0xb8d4e3, transparent: true, opacity: 0.45 }), [1.0, 12.0, 7.0], { t: 'show', when: 1, fx: 'water', g: 'test.shower' });
    add('test.shower.valve', new THREE.BoxGeometry(0.08, 0.08, 0.03), std(), [1.0, 12.3, 7.1], { t: 'trigger', g: 'test.shower', label: 'Shower' });
    add('test.firepit.flame', new THREE.ConeGeometry(0.12, 0.3, 12), std({ emissive: 0xff6a10 }), [1.5, 26.0, -0.2], { t: 'show', when: 1, fx: 'flame', g: 'test.firepit' }, 'garden');
    add('test.firepit.bowl', new THREE.CylinderGeometry(0.3, 0.2, 0.2, 16), std(), [1.5, 26.0, -0.4], { t: 'trigger', g: 'test.firepit', label: 'Fire pit' }, 'garden');
    add('test.sauna.door', new THREE.BoxGeometry(0.6, 1.9, 0.04), std({ name: 'sauna_glass' }), [1.5, 12.5, 7.0], { t: 'hinge', p: [1.2, 12.5, 7.0], a: [0, 0, 1], deg: 95, g: 'test.sauna', label: 'Sauna door' });
    add('test.bin.lid', new THREE.BoxGeometry(0.3, 0.02, 0.3), std(), [2.0, 12.5, 6.6], { t: 'hinge', p: [2.0, 12.65, 6.61], a: [1, 0, 0], deg: -70, g: 'test.bin', label: 'Bin lid' });
    add('test.wc.lid', new THREE.BoxGeometry(0.36, 0.02, 0.45), std(), [2.6, 12.0, 6.92], { t: 'hinge', p: [2.6, 12.22, 6.93], a: [1, 0, 0], deg: -90, g: 'test.wc.lid', label: 'Toilet lid' });
    add('test.wc.seat', new THREE.BoxGeometry(0.36, 0.02, 0.45), std(), [2.6, 12.0, 6.9], { t: 'hinge', p: [2.6, 12.22, 6.91], a: [1, 0, 0], deg: -90, g: 'test.wc.seat', label: 'Toilet seat', needs: 'test.wc.lid' });
    add('test.clock.minute', new THREE.BoxGeometry(0.01, 0.12, 0.005), std(), [2.2, 13.0, 8.0], { t: 'clock', hand: 'm', p: [2.2, 13.0, 7.94], a: [0, -1, 0] });
    add('test.tv.picture', new THREE.PlaneGeometry(0.8, 0.45), std(), [2.2, 13.2, 7.5], { t: 'show', when: 1, fx: 'tv', g: 'test.tv' });
    add('test.tv', new THREE.BoxGeometry(0.82, 0.47, 0.04), std({ color: 0x111111 }), [2.2, 13.22, 7.5], { t: 'trigger', g: 'test.tv' });
    add('test.lamp.shade', new THREE.SphereGeometry(0.1), std({ emissive: 0xffc27a, emissiveIntensity: 2 }), [1.0, 13.0, 7.0], { t: 'lamp', g: 'test.lamp', label: 'Lamp' });
    add('test.switch', new THREE.BoxGeometry(0.08, 0.08, 0.01), std({ color: 0xffffff }), [0.2, 9.0, 7.4], { t: 'light', rooms: ['green_bedroom', 'landing2_head'], g: 'test.switch' }, 'landing2_head');
    scene.getObjectByName('house').add(lv); ix.add(lv);
    return ix.groups().filter((g) => g.id.startsWith('test.')).map((g) => `${g.id}:${g.kind}`);
  });
  check(made.join() === 'test.shower:water,test.firepit:flame,test.sauna:move,test.bin:move,test.wc.lid:move,test.wc.seat:move,test.tv:tv,test.lamp:lamp,test.switch:light', `test objects added to the engine as one more level (${made})`);
  const toggle = (id) => page.evaluate((id) => window.viewer.ix.toggle(id), id);
  const centre = (id) => page.evaluate((id) => window.viewer.ix.box(id).getCenter(new window.viewer.THREE.Vector3()).toArray(), id);
  const c0 = { sauna: await centre('test.sauna'), bin: await centre('test.bin') };
  for (const id of ['test.shower', 'test.firepit', 'test.sauna', 'test.bin', 'test.tv', 'test.lamp']) await toggle(id);
  await idle(page, 900);
  const fx = await page.evaluate(() => {
    const { scene, ix } = window.viewer, mat = (n) => { let r = null; scene.traverse((o) => { if (o.userData.name === n) r = [].concat(o.material)[0]; }); return r; };
    const spray = mat('test.shower.spray'), tap = mat('kitchen.sink.mixer.water'), fire = mat('test.firepit.flame'), hob = mat('kitchen.hob.flame.0'), lamp = mat('test.lamp.shade');
    const tv = ix.tvCanvas('test.tv').getContext('2d').getImageData(160, 90, 1, 1).data;
    return { spray: spray.alphaMap && [spray.alphaMap.repeat.x, spray.alphaMap.repeat.y, spray.side, spray.opacity], tap: tap?.alphaMap && [tap.alphaMap.repeat.x, tap.alphaMap.repeat.y], sprayShown: scene.getObjectByName('testshowerspray')?.visible,
      fire: [fire.color.r, fire.color.b], hob: hob && [hob.color.r, hob.color.b], lamp: lamp.emissiveIntensity, tv: tv[0] + tv[1] + tv[2], clock: ix.clocks().find((c) => c.name === 'test.clock.minute') };
  });
  const c1 = { sauna: await centre('test.sauna'), bin: await centre('test.bin') }, d = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
  const mins = new Date().getMinutes() + new Date().getSeconds() / 60, err = fx.clock && Math.abs(Math.atan2(Math.sin(fx.clock.angle - (2 * Math.PI * mins) / 60), Math.cos(fx.clock.angle - (2 * Math.PI * mins) / 60)));
  check(fx.sprayShown && fx.spray[0] >= 8 && fx.spray[2] === 2 && (!fx.tap || fx.tap[0] <= 2), `shower spray: water fx repeated round the cone (repeat ${fx.spray}), a tap stream keeps one or two (${fx.tap})`);
  check(fx.fire[0] > 2 * fx.fire[1] && (!fx.hob || fx.hob[1] > fx.hob[0]), `fire pit flame keeps its warm emissive (r ${fx.fire[0].toFixed(2)} b ${fx.fire[1].toFixed(2)}), the hob stays blue (${fx.hob?.map((v) => v.toFixed(2))})`);
  check(d(c0.sauna, c1.sauna) > 0.3 && c1.bin[1] - c0.bin[1] > 0.05 && fx.lamp < 1e-3 && fx.tv > 30 && err < 0.02,
    `sauna door swings (${Math.round(d(c0.sauna, c1.sauna) * 1000)} mm), bin lid lifts (${Math.round((c1.bin[1] - c0.bin[1]) * 1000)} mm), lamp off (${fx.lamp}), TV on (${fx.tv}), clock at local time (err ${err?.toFixed(4)})`);
  for (const id of ['test.shower', 'test.firepit', 'test.sauna', 'test.bin', 'test.tv', 'test.lamp']) await toggle(id);
  await idle(page, 300);
  // `needs`: lifting the seat lifts the lid first; lowering the lid lowers the seat first; the lid alone lifts alone
  const wc = () => page.evaluate(() => ['test.wc.lid', 'test.wc.seat'].map((id) => window.viewer.ix.state(id)).join(''));
  await toggle('test.wc.seat'); await idle(page); const w1 = await wc();
  await toggle('test.wc.lid'); await idle(page); const w2 = await wc();
  await toggle('test.wc.lid'); await idle(page); const w3 = await wc();
  await toggle('test.wc.lid'); await idle(page);
  check(w1 === '11' && w2 === '00' && w3 === '10', `needs: seat lifts the lid with it (${w1}), the lid lowers the seat first (${w2}), the lid lifts alone (${w3})`);
  // the real roof window, eaves hatches and shed store doors of the export (hinges on other levels and axes)
  const real = (await groups(page)).filter((g) => /^roof\.velux|h_eaves|shed_store_doors|shed_w1/.test(g.id)).map((g) => g.id);
  const r0 = await Promise.all(real.map(centre));
  for (const id of real) await toggle(id);
  await idle(page, 300);
  const moved = (await Promise.all(real.map(centre))).map((c, k) => Math.round(d(c, r0[k]) * 1000));
  for (const id of real) await toggle(id);
  await idle(page, 300);
  check(!real.length || moved.every((m) => m > 40), `Velux, eaves hatches, shed doors and windows open (${real.map((id, k) => `${id} ${moved[k]} mm`).join(', ')})`);
  // a void room's light (the eaves, switch and bulkhead behind the knee wall) answers Space / E through an open hatch only
  const hatch = (await groups(page)).filter((g) => /h_eaves_front_e\.leaf/.test(g.id)).map((g) => g.id), eavesIds = ['eaves_front.switch', 'eaves_front.bulkhead'];
  if (!hatch.length || !(await groups(page)).some((g) => g.id === eavesIds[0])) skip('eaves light through the hatch: no eaves switch or hatch');
  else {
    await page.evaluate(() => window.viewer.jump('loft_office')); await idle(page, 300);
    // in front of the middle of the east hatch (jambs x 2.52 / 3.43, knee wall y 2.575), facing the bulkhead in the void
    // (2.53, 1.60) past the open leaves; shut, the leaf in front is the thing to use
    await page.evaluate(() => { const { S, G } = window.viewer; Object.assign(S, { anim: null, glide: null, x: 2.975, y: 2.95, yaw: G.dirYaw(-0.445, -1.35), pitch: -0.22 }); }); await settle(page, 200);
    const bestId = () => page.evaluate(() => window.viewer.ix.best(window.viewer.camera)?.id ?? null);
    const shut = await bestId();
    for (const id of hatch) await toggle(id);
    await idle(page, 300);
    const open = await bestId();
    for (const id of hatch) await toggle(id);
    await idle(page, 300);
    check(!eavesIds.includes(shut) && eavesIds.includes(open), `eaves light: Space / E reaches it through the open hatch (${open}), not through the shut one (${shut})`);
  }
  // the two-floor switch: only its rooms' lights-off images are fetched, both rooms go dark, the green bedroom dims
  await page.evaluate(() => window.viewer.jump('green_bedroom')); await idle(page, 300);
  const offs = () => page.evaluate(() => performance.getEntriesByType('resource').filter((r) => /lightmaps_off|probes_off/.test(r.name)).map((r) => r.name.split('/assets/')[1]));
  const before = await offs(), lum0 = await meanLum(page), mem0 = await page.evaluate(() => window.viewer.texStats());
  await toggle('test.switch'); await idle(page);
  const lum1 = await meanLum(page), mem1 = await page.evaluate(() => window.viewer.texStats()), fetched = (await offs()).filter((n) => !before.includes(n));
  const lit = await page.evaluate(() => ['green_bedroom', 'landing2_head', 'blue_bedroom'].map((r) => window.viewer.roomLights.get(r)?.target ?? null));
  await shot(page, 'ix_upper_lights_off.png');
  check(fetched.length && fetched.every((n) => /\/(green_bedroom|landing2_head)\.jpg$/.test(n)) && lit[0] === 0 && lit[1] === 0 && lit[2] !== 0 && lum1 < lum0 * 0.75,
    `two-floor switch: fetched only ${fetched}; green bedroom and level-2 head off, blue bedroom untouched (${lit}); view ${lum0.toFixed(0)} -> ${lum1.toFixed(0)}; textures ${mem0.MB} -> ${mem1.MB} MB`);
  await toggle('test.switch'); await idle(page);
  const lum2 = await meanLum(page);
  check(Math.abs(lum2 - lum0) < lum0 * 0.04, `... and back on (${lum2.toFixed(0)})`);
  await page.evaluate(() => { const lv = window.viewer.scene.getObjectByName('level_test'); lv.visible = false; });
}
// Interactions as each level arrives: with the upper levels held back, the ground floor's doors already work; a door
// of a level that arrives later works once it is there.
async function incremental() {
  let release; const gate = new Promise((f) => { release = f; });
  const { ctx, page } = await open({ viewport: { width: 1280, height: 800 } }, '', (page) => page.route(/glb\/[X12B]\.glb$/, async (r) => { await gate; await r.continue(); }));
  const s0 = await page.evaluate(() => ({ loaded: [...window.viewer.levelScenes.keys()], ix: window.viewer.ixLevels.slice() }));
  const door = await page.evaluate(() => { const { ix, walk } = window.viewer, g = ix.groups().find((q) => q.blocks.includes('d_kitchen')) || ix.groups().find((q) => q.blocks.length); const p = walk.portals.find((q) => g.blocks.includes(q.id)); const o0 = p.open; ix.toggle(g.id); return { id: g.id, pid: p.id, o0, o1: p.open }; });
  check(s0.loaded.join() === 'G' && s0.ix.join() === 'G' && door.o1 === !door.o0, `before the other levels arrive (${s0.loaded}), ${door.id} already opens / shuts ${door.pid} (${door.o0} -> ${door.o1})`);
  release(); await page.evaluate(() => window.viewer.streaming);
  const up = await page.evaluate(() => { const { ix, walk } = window.viewer, p = walk.portals.find((q) => q.id === 'd_green'), g = ix.groups().find((q) => q.blocks.includes('d_green')); if (!g) return null; const o0 = p.open; ix.toggle(g.id); return { loaded: [...window.viewer.levelScenes.keys()], o0, o1: p.open }; });
  check(!up || (up.loaded.length === 5 && up.o1 === !up.o0), `after the upper levels arrive (${up?.loaded}), the level-1 door d_green works (${up?.o0} -> ${up?.o1})`);
  await ctx.close();
}
if (run('levels')) {
  let i;
  const { ctx, page } = await open({ viewport: { width: 1440, height: 900 } });
  await page.evaluate(() => window.viewer.streaming);
  const st = await page.evaluate(() => { const v = window.viewer; return { order: v.ORDER, loaded: [...v.levelScenes.keys()], ix: v.ixLevels, models: v.ix.models(),
    groups: v.ix.groups().length, root: v.scene.getObjectByName('house')?.children.map((c) => c.name), glbs: v.LEVELS.filter((l) => l.glb).map((l) => l.id) }; });
  console.log('levels', JSON.stringify(st));
  const want = st.order.filter((id) => st.glbs.includes(id));
  check(st.order.join() === 'G,X,1,2,B' && st.loaded.join() === want.join() && st.root.join() === want.map((l) => `level_${l}`).join() && want.length > 1,
    `levels load in loadOrder under one root (${st.root}); levels without a GLB are skipped`);
  check(st.ix.join() === st.loaded.join() && st.models === st.loaded.length && st.groups > 50, `each level is handed to the interaction engine as it arrives (${st.ix}; ${st.groups} groups)`);
  check(await page.evaluate(() => document.querySelector('#chip').hidden), 'the streaming chip is gone once every level has arrived');
  // a switch of one level (X, loaded 2nd) controls a lamp of a level that arrived after it (1, loaded 3rd)
  if (FIXTURE && st.loaded.includes('X') && st.loaded.includes('1')) {
    const lamp = () => page.evaluate(() => { let v = null; window.viewer.scene.traverse((o) => { if (o.isMesh && o.userData.name === 'landing1_rear.lamp_test') v = [].concat(o.material)[0].emissiveIntensity; }); return v; });
    const l0 = await lamp();
    await page.evaluate(() => window.viewer.ix.toggle('garden.switch_test')); await idle(page);
    const l1 = await lamp(), hint = await page.evaluate(() => window.viewer.ix.groups().find((g) => g.id === 'garden.switch_test').hint);
    await page.evaluate(() => window.viewer.ix.toggle('garden.switch_test')); await idle(page);
    const l2 = await lamp();
    check(l0 > 0.5 && l1 < 1e-3 && Math.abs(l2 - l0) < 1e-6 && hint === 'Turn landing lights on', `cross-level switch: X switch turns the level-1 lamp off and on (${l0} -> ${l1} -> ${l2}; "${hint}")`);
    const door = () => page.evaluate(() => window.viewer.walk.portals.find((p) => p.id === 'd_ensuite').open);
    const d0 = await door(); await page.evaluate(() => window.viewer.ix.toggle('blue_ensuite.door_test')); await idle(page);
    const d1 = await door(); await page.evaluate(() => window.viewer.ix.toggle('blue_ensuite.door_test')); await idle(page);
    check(d0 === false && d1 === true && (await door()) === false, 'a door leaf of a later level opens and shuts its doorway (d_ensuite)');
    // probes: own room's probe, else the nearest of the same exterior-ness (the neighbour block is nearer the dining probe)
    const env = await page.evaluate(() => { const o = {}; window.viewer.scene.traverse((m) => { if (m.isMesh && /test_/.test(m.userData.name)) o[m.userData.name] = [].concat(m.material)[0].envMap?.source?.data?.src?.split('/assets/')[1] ?? null; }); return o; });
    check(env['garden.test_deck'] === 'probes/garden.jpg' && env['neighbours.test_block'] === 'probes/garden.jpg' && env['landing1_rear.test_floor'] && env['landing1_rear.test_floor'] !== 'probes/garden.jpg',
      `probe choice by room, then by exterior-ness (${JSON.stringify(env)})`);
  }
  await page.waitForFunction(() => window.viewer.scene.background?.isTexture, null, { timeout: 5000 }).catch(() => {});
  const bg = await page.evaluate(() => { const { scene, THREE } = window.viewer, b = scene.background; return { tex: !!b?.isTexture, eq: b?.mapping === THREE.EquirectangularReflectionMapping, cs: b?.colorSpace }; });
  check(bg.tex && bg.eq && bg.cs === 'srgb', 'manifest.sky.image is the walk-mode background (equirect, sRGB)');
  i = await info(page);
  check(i.layer === 'G' && i.level === 'G' && i.room === 'hallway' && Math.abs(i.z) < 1e-6 && Math.abs(i.eye - 1.6) < 0.01 && i.sheet === 'G',
    `spawn: layer ${i.layer}, level ${i.level}, ${i.room}, z ${i.z}, eye ${i.eye.toFixed(2)}, sheet ${i.sheet}`);
  check(!(await page.evaluate(() => performance.getEntriesByType('resource').some((r) => /lightmaps_off|probes_off/.test(r.name)))), 'no lights-off image is fetched at load');
  await shot(page, 'spawn.png');

  // GLB textures: one texture per image name + size across the five level scenes (E-TEXMEM); the numbers go in the log
  const tex = await page.evaluate(() => {
    const { scene, texStats } = window.viewer, src = new Map();
    scene.traverse((o) => { if (o.isMesh) for (const m of [].concat(o.material)) for (const k of ['map', 'normalMap', 'roughnessMap', 'metalnessMap', 'aoMap', 'emissiveMap']) {
      const t = m[k]; if (!t?.name || !t.image) continue; const key = `${t.name}|${t.image.width}x${t.image.height}`; (src.get(key) || src.set(key, new Set()).get(key)).add(t.source); } });
    return { dup: [...src].filter(([, s]) => s.size > 1).map(([k]) => k), images: src.size, ...texStats() };
  });
  console.log('textures desktop', JSON.stringify({ ...tex, dup: tex.dup.length }));
  check(!tex.dup.length && tex.images > 20, `level scenes share one texture per GLB image (${tex.images} images, ${tex.sources} sources, ${tex.MB} MB decoded; duplicates: ${tex.dup.slice(0, 5)})`);

  // room buttons grouped by level; only the open group (the visitor's floor unless a chip picked another) lists its
  // rooms, the current one scrolled into view; digits jump within the open group, PageUp / PageDown change it
  const grp = await page.$$eval('#rooms .grp', (gs) => gs.map((g) => [g.dataset.level, g.querySelectorAll('button[data-room]').length, g.classList.contains('cur')]));
  check(grp.map((g) => g[0]).join() === 'B,G,1,2,X' && grp.find((g) => g[0] === 'G')[2] && grp.reduce((n, g) => n + g[1], 0) >= 25, `room buttons grouped by level (${grp.map((g) => `${g[0]}:${g[1]}`)})`);
  await roomBar(page, 'desktop');

  // plan tabs; marker on every sheet (full on the visitor's floor, hollow on SITE while indoors, none on other floors)
  const tabs = await page.$$eval('#plan-tabs button', (bs) => bs.map((b) => [b.textContent, b.getAttribute('aria-pressed')]));
  check(tabs.map((t) => t[0]).join() === 'B,G,1,2,SITE' && tabs.find((t) => t[0] === 'G')[1] === 'true', `plan tabs ${tabs.map((t) => t[0])}, G pressed`);
  const place = (L, x, y) => page.evaluate(([L, x, y]) => { const { S, G, walk } = window.viewer; Object.assign(S, { anim: null, glide: null, x, y, layer: L, z: G.zAt(walk, L, x, y), pitch: 0 }); }, [L, x, y]);
  // the marker on the plan canvas at the visitor: full = a solid dot (3x3 core in the marker colour), hollow = a ring
  // (core clear, ring pixels 3..7 px out on the four sides), none = neither
  const marker = () => page.evaluate(() => {
    const { planView: p, S } = window.viewer; p.fit();
    const [X, Y] = p.toScreen(S.x, S.y).map(Math.round), g = p.c.getContext('2d', { willReadFrequently: true }), d = p.dpr;
    const at = (dx, dy) => { const c = g.getImageData(X + dx, Y + dy, 1, 1).data; return c[0] > 200 && c[1] < 140 && c[2] < 110 ? 1 : 0; };
    let core = 0, ring = 0;
    for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++) core += at(dx, dy);
    for (let r = Math.round(3 * d); r <= Math.round(7 * d); r++) ring += at(r, 0) + at(-r, 0) + at(0, r) + at(0, -r);
    return { sheet: p.sheetId, full: core >= 7, hollow: core <= 2 && ring >= 2, none: core === 0 && ring === 0 };
  });
  const frames = (n = 3) => page.evaluate((n) => new Promise((f) => { const k = () => (--n ? requestAnimationFrame(k) : f()); requestAnimationFrame(k); }), n);
  for (const [sheet, L, x, y] of [['B', 'B', 2.5, 7.0], ['G', 'G', 0, 3], ['1', '1', -0.2, 10.0], ['2', '2', -0.2, 10.0], ['X', 'G', 1.9, -3.0]]) {
    await place(L, x, y); await frames(4);
    const m = await marker(); i = await info(page);
    check(i.level === sheet && m.sheet === sheet && m.full, `on level ${sheet}: the plan follows to sheet ${m.sheet}, marker drawn (${i.room})`);
    await shot(page, `plan_${sheet}.png`, '#plan');
    if (sheet !== 'X') {
      await page.click('#plan-tabs button:last-child'); await frames(3);
      const h = await marker();
      if (sheet === 'G') await shot(page, 'plan_site_indoors.png', '#plan');
      await page.click(`#plan-tabs button[data-sheet="${sheet === 'B' ? 'G' : 'B'}"]`); await frames(3);
      const o = await marker();
      check(h.sheet === "X" && h.hollow && o.none, `tab click overrides: SITE shows a hollow marker indoors, another floor none (${JSON.stringify([h, o])})`);
    }
  }

  // the sheet follows the stairs: walk from the hall up the main flight to the quarter landing
  await place('G', 0.4, 4.4); await page.evaluate(() => { const { S } = window.viewer; S.yaw = 0; }); await frames(3);
  const climb = await page.evaluate(async () => {
    const v = window.viewer, seen = [];
    if (!v.walkTo(0.57, 8.42, '1')) return null;
    await new Promise((f) => { const k = () => { const s = `${v.S.layer}/${v.S.level}/${v.planView.sheetId}`; if (seen[seen.length - 1] !== s) seen.push(s); v.S.glide ? requestAnimationFrame(k) : f(); }; k(); });
    await new Promise((f) => setTimeout(f, 600));
    return { seen, ...v.info() };
  });
  check(climb && climb.layer === '1' && climb.sheet === '1' && Math.abs(climb.z - 2.85) < 0.02 && climb.seen.includes('stair_main/G/G') && climb.seen.includes('stair_main/1/1'),
    `walks up the main flight: ${climb?.seen.join(' > ')}; z ${climb?.z.toFixed(2)}`);
  await shot(page, 'stairs_landing.png');

  // routes across layers: to the loft office (two flights, two step sets, the loft door) and to the basement
  const go = (x, y, L, ms = 40000) => page.evaluate(async ([x, y, L, ms]) => {
    const v = window.viewer, t0 = performance.now();
    if (!v.walkTo(x, y, L)) return null;
    let zmax = -9, zmin = 9, eyeMin = 9;
    await new Promise((f) => { const k = () => { zmax = Math.max(zmax, v.S.z); zmin = Math.min(zmin, v.S.z); eyeMin = Math.min(eyeMin, v.camera.position.y - v.S.z); v.S.glide && performance.now() - t0 < ms ? requestAnimationFrame(k) : f(); }; k(); });
    await new Promise((f) => setTimeout(f, 600));
    return { ...v.info(), zmax, zmin, eyeMin };
  }, [x, y, L, ms]);
  i = await go(2.0, 3.2, '2');
  check(i && i.layer === '2' && i.room === 'loft_office' && Math.abs(i.z - 6.49) < 0.02 && i.eye < 1.6 && i.eye > 1.0,
    `double-click route climbs to the loft office (${i?.room}, z ${i?.z.toFixed(2)}, eye ${i?.eye.toFixed(2)} under the slope)`);
  await page.evaluate(() => { window.viewer.S.yaw = Math.PI; }); await frames(3); await shot(page, 'loft.png');
  await page.evaluate(() => {   // open the basement door: its leaf (a shut leaf is solid), else (the fixture GLB has none) the doorway
    const { ix, walk } = window.viewer, g = ix.groups().find((q) => q.blocks.includes('d_basement'));
    if (g) { if (!g.open) ix.toggle(g.id); return; }
    walk.portals.find((p) => p.id === 'd_basement').open = true;
  });
  await idle(page, 300);
  i = await go(2.5, 7.0, 'B');
  check(i && i.layer === 'B' && i.room === 'basement' && Math.abs(i.z + 2.31) < 0.02 && i.level === 'B' && i.sheet === 'B',
    `route from the loft down three flights to the basement (${i?.room}, z ${i?.z.toFixed(2)}, sheet ${i?.sheet})`);
  // a plan click lands on the layer of the sheet shown: sheet 1 while standing in the basement
  await page.click('#plan-tabs button[data-sheet="1"]'); await frames(3);
  const pt = await page.evaluate(() => { const p = window.viewer.planView; p.fit(); const r = p.c.getBoundingClientRect(), [X, Y] = p.toScreen(1.2, 14.5); return [r.left + (X * r.width) / p.c.width, r.top + (Y * r.height) / p.c.height]; });
  await page.mouse.click(...pt); await idle(page, 300); i = await info(page);
  check(i.layer === '1' && i.room === 'blue_bedroom' && i.sheet === '1' && Math.abs(i.z - 3.04) < 1e-6, `plan click on sheet 1 from the basement lands on that floor (${i.layer}, ${i.room}, z ${i.z})`);
  // the double-click layer choice: a floor hit at a height picks the layer whose floor is there
  const tl = await page.evaluate(() => {
    const { targetOf, THREE } = window.viewer, hit = (x, y, h) => ({ point: new THREE.Vector3(x, h, -y), face: { normal: new THREE.Vector3(0, 1, 0) }, object: new THREE.Object3D() });
    return [[0.57, 7.0, 1.85], [0.57, 7.0, -0.7], [0, 3, 0], [-0.2, 10, 3.04], [2.0, 4.0, 6.49]].map(([x, y, h]) => targetOf(hit(x, y, h))?.layer);
  });
  check(tl.join() === 'stair_main,stair_basement,G,1,2', `double-click target layer by hit height (${tl})`);

  // room jumps to another layer cut through black instead of flying through floors
  const jmp = await page.evaluate(() => { const v = window.viewer; v.jump('loft_office'); return !!v.S.anim?.cut; });
  await idle(page, 300); i = await info(page);
  check(jmp && i.layer === '2' && i.room === 'loft_office' && Math.abs(i.z - 6.49) < 1e-6, `room jump to another floor is a fade cut (${i.room}, z ${i.z})`);
  await page.evaluate(() => window.viewer.jump('garden')); await idle(page, 300); i = await info(page);
  check(i.layer === 'G' && i.level === 'X' && i.room === 'garden' && i.sheet === 'X', `jump to the garden: layer G, level X, SITE sheet (${i.room}, z ${i.z.toFixed(2)})`);
  await shot(page, 'garden.png');
  await page.keyboard.press('Digit1'); await idle(page, 200); i = await info(page);
  check(i.level === 'X' && i.room === 'front', `key 1 outside -> first room of the Outside group (${i.room})`);

  // the route traces of blender/MULTILEVEL.md section 16 on a REAL export: every shut door leaf of the GLBs is opened
  // through its own `blocks` tag, then the walker goes there on foot (stairs, steps, thresholds, the side passage)
  if (!FIXTURE) {
    const opened = await page.evaluate(() => {
      const ix = window.viewer.ix, ids = ix.groups().filter((g) => g.blocks.length && !g.open).map((g) => g.id);
      ids.forEach((id) => ix.toggle(id)); return ids;
    });
    await idle(page, 1500);
    const shut = await page.evaluate(() => window.viewer.walk.portals.filter((p) => p.open === false).map((p) => p.id));
    check(shut.every((id) => id === 'side_gate' || /^d_wc|^d_pocket/.test(id)) || shut.length < 3, `door leaves open their portals (still shut: ${shut.join(' ') || 'none'})`);
    for (const [name, from, to, room, z] of [
      ['1 front door to basement', ['G', 0, 0.9], [2.5, 7.0, 'B'], 'basement', -2.31],
      ['2 front door to balcony', ['G', 0, 0.9], [1.15, 17.9, '1'], 'balcony', 3.0],
      ['3 front door to loft office', ['G', 0, 0.9], [2.0, 3.2, '2'], 'loft_office', 6.49],
      ['4 kitchen to side passage, garden, shed', ['G', 3.0, 7.0], [2.0, 27.0, 'G'], 'shed', -0.32],
      ['5 dining French doors to deck', ['G', 1.2, 16.6], [1.2, 19.0, 'G'], 'garden', -0.05],
      ['6 street doors to forecourt', ['G', 0, 0.9], [1.9, -3.0, 'G'], 'front', null]]) {
      await place(...from); await frames(3);
      i = await go(...to, 240000);      // frames crawl while Cycles shares the GPU
      check(i && i.room === room && (z === null || Math.abs(i.z - z) < 0.02), `route ${name} walked on the real model (${i?.room}, z ${i?.z?.toFixed(2)})`);
      await shot(page, `route_${name[0]}.png`);
    }
    // door leaves are solid where they stand: no free spot within 0.10 m of an open leaf's mesh (eye height band)
    const near = await page.evaluate(() => {
      const { ix, G, walk, THREE, scene } = window.viewer, out = [], v = new THREE.Vector3();
      for (const g of ix.groups().filter((q) => q.blocks.length && q.open && q.types.includes('hinge'))) {
        const pts = [];
        scene.traverse((o) => { if (!o.isMesh || ix.groupOf(o) !== g.id) return; const a = o.geometry.attributes.position; for (let k = 0; k < a.count; k += Math.max(1, a.count >> 8)) pts.push(v.fromBufferAttribute(a, k).applyMatrix4(o.matrixWorld).clone()); });
        const b = ix.box(g.id);
        for (let x = b.min.x - 0.3; x <= b.max.x + 0.3 && out[out.length - 1]?.[0] !== g.id; x += 0.05) for (let z = b.min.z - 0.3; z <= b.max.z + 0.3; z += 0.05) {
          const L = walk.layers.find((l) => G.isFree(walk, l, x, -z) && Math.abs(G.zAt(walk, l, x, -z) + 1 - (b.min.y + b.max.y) / 2) < 1.2);
          const d = L ? Math.min(...pts.map((q) => Math.hypot(q.x - x, q.z - z))) : Infinity;
          if (d < 0.1) { out.push([g.id, +x.toFixed(2), +(-z).toFixed(2), +d.toFixed(3)]); break; }
        }
      }
      return out;
    });
    check(!near.length, `no free spot within 0.10 m of an open door leaf (${JSON.stringify(near)})`);
    await walkChecks(page);
    await page.evaluate((ids) => ids.forEach((id) => window.viewer.ix.toggle(id)), opened); await idle(page, 1500);
    // a double door with one leaf open: its shut leaf keeps its half of the doorway shut, the open half is a route
    const half = await page.evaluate(() => {
      const { ix, G, walk } = window.viewer, st = (id) => ix.groups().find((g) => g.id === id)?.open;
      if (st('hallway.d_inner.leaf.1') === undefined) return null;
      if (!st('hallway.d_inner.leaf.1')) ix.toggle('hallway.d_inner.leaf.1');
      if (st('hallway.d_inner.leaf.0')) ix.toggle('hallway.d_inner.leaf.0');
      const b = ix.box('hallway.d_inner.leaf.0'), x = (b.min.x + b.max.x) / 2, y = -(b.min.z + b.max.z) / 2;
      const r = G.route(walk, { x, y: y - 0.5, layer: 'G' }, { x, y: y + 0.8, layer: 'G' });
      return { shut: !G.isFree(walk, 'G', x, y), route: !!r && r.every((p, i) => !i || [0.25, 0.5, 0.75].every((f) => { const q = r[i - 1], px = q.x + (p.x - q.x) * f, py = q.y + (p.y - q.y) * f; return Math.abs(px - x) > (b.max.x - b.min.x) / 2 || Math.abs(py - y) > 0.2; })) };
    });
    check(!half || (half.shut && half.route), `d_inner with one leaf open: the shut leaf's half is solid, the route goes round it (${JSON.stringify(half)})`);
  }

  // lights: a switch fetches the lights-off bake on first use and still dims the room
  await page.evaluate(() => window.viewer.jump('kitchen')); await idle(page, 300);
  const before = await meanLum(page);
  await page.evaluate(() => window.viewer.ix.toggle('kitchen.switch')); await idle(page);
  const after = await meanLum(page), offs = await page.evaluate(() => performance.getEntriesByType('resource').filter((r) => /lightmaps_off|probes_off/.test(r.name)).map((r) => r.name.split('/assets/')[1]));
  check(after < before * 0.75 && offs.some((n) => n.startsWith('lightmaps_off/kitchen')), `kitchen switch: lights-off loaded on first use (${offs}) and the view darkens (${before.toFixed(0)} -> ${after.toFixed(0)})`);
  await page.evaluate(() => window.viewer.ix.toggle('kitchen.switch')); await idle(page);
  if (!FIXTURE) await syntheticIx(page);

  // dollhouse: one cut plane per level at its cutZ, orbit target on its datumZ; B also hides the outside; All clips nothing
  await page.evaluate(() => window.viewer.jump('hallway')); await idle(page, 200);
  await page.click('#mode-orbit'); await page.waitForTimeout(600);
  const levels = await page.evaluate(() => window.viewer.LEVELS.filter((l) => l.id !== 'X').map((l) => [l.id, l.cutZ, l.datumZ]));
  check(await page.isVisible('#dh-levels') && (await page.$$eval('#dh-levels button', (bs) => bs.map((b) => b.textContent))).join() === 'B,G,1,2,All', 'dollhouse level buttons B G 1 2 All');
  for (const [id, cut, datum] of [...levels, ['all', null, null]]) {
    await page.click(`#dh-levels button[data-level="${id}"]`); await page.waitForTimeout(700);
    const d = await page.evaluate(() => { const { renderer, orbit, levelScenes } = window.viewer; return { planes: renderer.clippingPlanes.map((p) => p.constant), ty: orbit.target.y, out: levelScenes.get('X')?.visible ?? null }; });
    const ok = id === 'all' ? d.planes.length === 0 : d.planes.length === 1 && Math.abs(d.planes[0] - cut) < 1e-6 && Math.abs(d.ty - datum) < 1e-6;
    check(ok && (d.out === null || d.out === (id !== 'B')), `dollhouse ${id}: cut ${d.planes} (want ${cut ?? 'none'}), target y ${d.ty.toFixed(2)}, outside shown ${d.out}`);
    // no neighbours; a cut shows no roof over its level; "All" keeps the roof; the level (All: the plot) is framed in
    // the part of the view the plan panel leaves free, filling at least half of it one way
    const f = await dollState(page, id);
    check(!f.neighbours && (id === 'all' ? f.roof > 5 : !f.roofOver) && f.inside && f.fill > 0.5,
      `dollhouse ${id}: neighbours hidden (${f.neighbours}), roof ${id === 'all' ? `shown (${f.roof})` : `over the level hidden (${f.roofOver})`}, framed inside the free view (fill ${f.fill.toFixed(2)}, distance ${f.d.toFixed(1)} m)`);
    await shot(page, `dollhouse_${id}.png`);
  }
  await page.click('#dh-levels button[data-level="1"]'); await page.waitForTimeout(300);
  await page.click('#mode-walk'); await page.waitForTimeout(500); i = await info(page);
  check(i.mode === 'walk' && i.layer === '1' && await page.evaluate(() => window.viewer.renderer.clippingPlanes.length === 0), `back to walk on the dollhouse level (${i.layer}, ${i.room})`);
  await ctx.close();
  if (!FIXTURE) await incremental();

  // phone: tabs, grouped room buttons and the dollhouse level control fit the screen
  {
    const { ctx, page } = await open({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
    await shot(page, 'phone.png');
    // phones: GLB colour maps drawn down to 512 px before upload, shared across levels like on the desktop
    await page.evaluate(() => window.viewer.streaming);
    const pt = await page.evaluate(() => {
      const { scene, texStats } = window.viewer; let big = 0, maps = 0;
      scene.traverse((o) => { if (o.isMesh) for (const m of [].concat(o.material)) for (const k of ['map', 'emissiveMap']) { const im = m[k]?.image; if (im && m[k].name) { maps++; if (Math.max(im.width, im.height) > 512) big++; } } });
      return { big, maps, ...texStats() };
    });
    console.log('textures phone', JSON.stringify(pt));
    check(pt.maps > 0 && !pt.big && (!tex || pt.MB < tex.MB), `phone: GLB colour maps <= 512 px (${pt.big} of ${pt.maps} over), ${pt.MB} MB decoded vs ${tex?.MB} MB on the desktop`);
    await roomBar(page, 'phone');
    await page.tap('#mode-orbit'); await page.waitForTimeout(600);
    const fit = await page.evaluate(() => [...document.querySelectorAll('#dh-levels, #plan-tabs')].map((e) => { const r = e.getBoundingClientRect(); return r.left >= 0 && r.right <= innerWidth; }));
    check(fit.every(Boolean), 'phone: plan tabs and dollhouse levels fit the screen');
    for (const id of ['G', 'all']) {
      await page.tap(`#dh-levels button[data-level="${id}"]`); await page.waitForTimeout(700);
      const f = await dollState(page, id);
      check(f.inside && f.fill > 0.5 && !f.neighbours, `phone dollhouse ${id}: framed below the plan panel (fill ${f.fill.toFixed(2)}, ${f.d.toFixed(1)} m)`);
      await shot(page, `phone_dollhouse_${id}.png`);
    }
    await ctx.close();
  }
}

// ---- walk-mode culling + static batching (NAV-PERF-DRAWCALLS): at every room viewpoint, four ways, the culled frame is
// the full frame (no hole) for far fewer draw calls; a shut solid door hides the room behind; the dollhouse draws all ----
if (run('cull')) {
  const { ctx, page } = await open({ viewport: { width: 1440, height: 900 } });
  await page.evaluate(() => window.viewer.streaming);
  check((await info(page)).batches > 100, `static meshes batched per room and material (${(await info(page)).batches} batches)`);
  const rows = [];
  for (const id of await page.evaluate(() => Object.keys(window.viewer.vps))) for (const k of [0, 1, 2, 3]) {
    await page.evaluate((id) => window.viewer.jump(id), id); await idle(page, 50);
    await page.evaluate((k) => { window.viewer.S.yaw += (k * Math.PI) / 2; }, k); await settle(page);
    const r = await page.evaluate(() => {
      const v = window.viewer, { renderer, scene, camera } = v, W = 240, H = 150, c = Object.assign(document.createElement('canvas'), { width: W, height: H }), g = c.getContext('2d', { willReadFrequently: true });
      const grab = (on) => { v.setCull(on); renderer.render(scene, camera); const n = renderer.info.render.calls; g.drawImage(renderer.domElement, 0, 0, W, H); return [g.getImageData(0, 0, W, H).data, n]; };
      const [a, on] = grab(true), [b, off] = grab(false); v.setCull(true);
      let d = 0; for (let i = 0; i < a.length; i += 4) if (Math.abs(a[i] - b[i]) + Math.abs(a[i + 1] - b[i + 1]) + Math.abs(a[i + 2] - b[i + 2]) > 40) d++;
      return { room: v.info().room, on, off, diff: (100 * d) / (W * H) };
    });
    rows.push({ id, k, ...r });
    if (r.diff > 0.3) await shot(page, `cull_hole_${id}_${k}.png`);
  }
  const worst = rows.reduce((a, b) => (b.diff > a.diff ? b : a)), most = rows.reduce((a, b) => (b.on > a.on ? b : a)), sum = (k) => rows.reduce((n, r) => n + r[k], 0);
  console.log('cull', JSON.stringify({ views: rows.length, calls: sum('on'), uncut: sum('off'), most, worst }));
  check(worst.diff <= 0.3, `culling leaves no hole: ${rows.length} views (every room viewpoint, four ways), worst ${worst.diff.toFixed(2)} % of pixels changed (${worst.id} ${worst.k})`);
  check(sum('on') < 0.45 * sum('off') && most.on <= 1200, `draw calls ${sum('on')} vs ${sum('off')} without culling; most ${most.on} (${most.id} ${most.k}, was ${most.off})`);
  // a shut solid door: the study, facing its door - the landing behind is not drawn until the door opens
  await page.evaluate(() => window.viewer.jump('study')); await idle(page, 100);
  const door = await page.evaluate(() => {
    const { ix, walk, S, G } = window.viewer, g = ix.groups().find((q) => q.blocks.includes('d_study')), p = walk.portals.find((q) => q.id === 'd_study');
    if (g.open) ix.toggle(g.id);
    const k = G.cellAt(walk, '2', p.center[0] + p.normal[0], p.center[1] + p.normal[1])?.room === 'study' ? 1 : -1;
    Object.assign(S, { anim: null, glide: null, x: p.center[0] + k * p.normal[0] * 1.2, y: p.center[1] + k * p.normal[1] * 1.2, yaw: G.dirYaw(-k * p.normal[0], -k * p.normal[1]), pitch: 0 });
    return g.id;
  });
  await idle(page, 100); await settle(page);
  const shutSeen = await page.evaluate(() => [...window.viewer.seen().keys()]);
  await page.evaluate((id) => window.viewer.ix.toggle(id), door); await settle(page);
  const openSeen = await page.evaluate(() => [...window.viewer.seen().keys()]);
  await idle(page);
  check(!shutSeen.includes('landing2_head') && openSeen.includes('landing2_head'), `the shut study door hides the landing (${shutSeen}), opening it shows it (${openSeen.includes('landing2_head')})`);
  await page.evaluate(() => window.viewer.setMode('orbit')); await settle(page);
  check(await page.evaluate(() => window.viewer.cullList.every((c) => c.o.layers.mask === 1)), 'the dollhouse draws every mesh (no walk culling)');
  await page.evaluate(() => window.viewer.setMode('walk'));
  await ctx.close();
}

// ---- round-3 navigation fixes (Q4, Q5, Q13, Q14 / IX-11, NAV-*), on the real export ----
if (run('nav')) {
  const { ctx, page } = await open({ viewport: { width: 1440, height: 900 } }, '', async (page) => {
    // the level-G lightmaps arrive 1.2 s after the GLB: the loader must say so instead of standing at 100 %
    await page.route(/lightmaps\/(hallway|living)\.jpg$/, async (r) => { await new Promise((f) => setTimeout(f, 1200)); await r.continue(); });
    await page.addInitScript(() => { window.__msgs = []; new MutationObserver(() => { const t = document.querySelector('#loader-msg')?.textContent; if (t && window.__msgs.at(-1) !== t) window.__msgs.push(t); })
      .observe(document, { subtree: true, childList: true, characterData: true }); });
  });
  await page.evaluate(() => window.viewer.streaming);
  const msgs = await page.evaluate(() => window.__msgs);
  check(msgs.some((m) => /^Loading model \d+%/.test(m)) && msgs.some((m) => /^Loading lighting (9\d|[1-8]\d)%/.test(m)), `loader: model then lighting progress over the first view (${msgs.filter((m, i) => !i || /lighting/.test(m)).slice(0, 4).join(' | ')})`);
  await page.mouse.move(700, 12);
  const best = () => page.evaluate(() => { const v = window.viewer, g = v.ix.best(v.camera); return g?.id ?? null; });
  const turn = async (id, k) => { await page.evaluate((id) => window.viewer.jump(id), id); await idle(page, 100); await page.evaluate((k) => { window.viewer.S.yaw += (k * Math.PI) / 2; }, k); await settle(page, 100); };
  // Q4: Space never reaches through a partition (the study's wall to bathroom2) or a window (vestibule -> living shutters)
  await turn('study', 3); const b1 = await best();
  await turn('vestibule', 3); const b2 = await best();
  check(!/^bathroom2\./.test(b1 ?? '') && !/^living\./.test(b2 ?? ''), `Space stays in the room: study facing the bathroom wall -> ${b1}; vestibule facing the bay window -> ${b2}`);
  // NAV-SPACE-OPEN-DOOR-CLOSE-RANGE: 0.6 m inside the dining room facing its open door, Space closes it
  const near = await page.evaluate(() => {
    const { S, G, walk, ix } = window.viewer, p = walk.portals.find((q) => q.id === 'd_dining'), g = ix.groups().find((q) => q.blocks.includes('d_dining'));
    if (!g.open) ix.toggle(g.id);
    for (const k of [1, -1]) { const x = p.center[0] - k * p.normal[0] * 0.6, y = p.center[1] - k * p.normal[1] * 0.6; if (G.cellAt(walk, 'G', x, y)?.room === 'dining' && G.isFree(walk, 'G', x, y)) { Object.assign(S, { anim: null, glide: null, x, y, layer: 'G', z: 0, yaw: G.dirYaw(k * p.normal[0], k * p.normal[1]), pitch: -0.05 }); return g.id; } }
    return null;
  });
  await idle(page, 100); await settle(page, 100);
  const b3 = await best(); await page.locator('#scene').focus(); await page.keyboard.press('Space'); await idle(page);
  const shutNow = await page.evaluate((id) => !window.viewer.ix.groups().find((g) => g.id === id).open, near);
  check(near && b3 === near && shutNow, `0.6 m inside the dining room facing its open door: Space picks ${b3} and closes it (${shutNow})`);
  await page.evaluate((id) => window.viewer.ix.toggle(id), near); await idle(page);
  // Q5: mirrors read the room probe box-projected; the hall mirror at the spawn shows the stair (a varied picture, not a blank panel)
  await page.evaluate(() => window.viewer.jump('hallway')); await idle(page, 200);
  const mir = await page.evaluate(() => {
    const { scene, camera, renderer, castAt } = window.viewer; let n = 0, box = 0; scene.traverse((o) => { if (o.isMesh) for (const m of [].concat(o.material)) if (m.name === 'mirror') { n++; box += m.userData.boxProbe ? 1 : 0; } });
    const c = Object.assign(document.createElement('canvas'), { width: innerWidth, height: innerHeight }), g = c.getContext('2d', { willReadFrequently: true }); renderer.render(scene, camera); g.drawImage(renderer.domElement, 0, 0);
    const lum = []; for (let X = 20; X < 460; X += 12) for (let Y = 200; Y < 820; Y += 12) { const h = castAt(X, Y); if (h?.object.material.name !== 'mirror') continue; const d = g.getImageData(X, Y, 1, 1).data; lum.push(0.2126 * d[0] + 0.7152 * d[1] + 0.0722 * d[2]); }
    const mean = lum.reduce((a, b) => a + b, 0) / lum.length, sd = Math.sqrt(lum.reduce((a, b) => a + (b - mean) ** 2, 0) / lum.length);
    return { n, box, samples: lum.length, sd };
  });
  await shot(page, 'nav_spawn_mirror.png');
  check(mir.n > 5 && mir.box === mir.n && mir.samples > 20 && mir.sd > 18, `mirrors box-projected (${mir.box} of ${mir.n}); the hall mirror at the spawn shows a picture (luminance sd ${mir.sd?.toFixed(1)} over ${mir.samples} px)`);
  // Q14 / IX-11: verbs that say what the thing does
  const hint = Object.fromEntries((await groups(page)).map((g) => [g.id, g.hint]));
  const burners = Object.entries(hint).filter(([id]) => /^kitchen\.hob\.\d$/.test(id)).map(([, h]) => h);
  check(hint['loft_office.office_chair'] === 'Swivel chair' && hint['bathroom2.sauna.timer'] === 'Turn over sand timer' && hint['green_bedroom.armchair.footstool'] === 'Pull out footstool'
    && hint['loft_office.aircon'] === 'Turn air conditioning on' && burners.length === 5 && new Set(burners).size === 5 && burners.every((h) => /^Light [a-z-]+ burner$/.test(h)),
  `hints: ${['loft_office.office_chair', 'bathroom2.sauna.timer', 'green_bedroom.armchair.footstool', 'loft_office.aircon'].map((id) => hint[id]).join(', ')}; ${burners.join(', ')}`);
  // NAV-W-SNAG-CORNER: W due south past the side-passage downpipe gully, tangent to its footprint, and 3 deg either side
  for (const a of [0, 3, -3]) {
    await page.evaluate((a) => { const { S, G, walk } = window.viewer; Object.assign(S, { anim: null, glide: null, x: 4.84, y: 7.95, layer: 'G', z: G.zAt(walk, 'G', 4.84, 7.95), yaw: Math.PI + (a * Math.PI) / 180, pitch: 0 }); }, a);
    await page.locator('#scene').focus(); await page.keyboard.down('KeyW');
    await page.waitForFunction(() => window.viewer.S.y < 6.6, null, { timeout: 4000, polling: 50 }).catch(() => {}); await page.keyboard.up('KeyW');
    const y = (await info(page)).y; check(y < 6.75, `W south past the side-passage gully (heading ${a} deg): from y 7.95 to ${y.toFixed(2)}`);
  }
  // NAV-PLAN-HEADER-STAIR-NAME: half-way up the main stair the header names the flight, not the stairwell above it
  await page.evaluate(() => { const { S, G, walk } = window.viewer; Object.assign(S, { anim: null, glide: null, x: 0.58, y: 7.69, layer: 'stair_main', z: G.zAt(walk, 'stair_main', 0.58, 7.69), yaw: 0 }); }); await settle(page, 100);
  const head = await page.textContent('#plan-room');
  check(/^Stairs, ground floor to first floor$/.test(head), `on the main flight the plan header reads "${head}"`);
  // NAV-STAIR2-FOOT-TARGET: walking to the first tread of the second-floor stair ends on that flight, facing up it
  await page.evaluate(() => { const { S, G, walk } = window.viewer; Object.assign(S, { anim: null, glide: null, x: -0.31, y: 6.81, layer: '1', z: G.zAt(walk, '1', -0.31, 6.81), yaw: 0 }); }); await settle(page);
  await page.evaluate(() => window.viewer.walkTo(0.61, 6.22, 'stair_second')); await idle(page, 200);
  const foot = await page.evaluate(() => { const { S, G, walk } = window.viewer, c = walk.cells.find((q) => q.id === 'stair_second'), [a, b] = c.risers[0], up = [-(b[1] - a[1]), b[0] - a[0]], [fx, fy] = G.yawDir(S.yaw); return { layer: S.layer, dot: (fx * up[0] + fy * up[1]) / Math.hypot(...up) }; });
  check(foot.layer === 'stair_second' && foot.dot > 0.7, `double-click on the first tread: ends on ${foot.layer}, facing up the flight (${foot.dot.toFixed(2)})`);
  await shot(page, 'nav_stair2_foot.png');
  // NAV-PLAN-FOLLOW-ZOOM: a zoomed plan follows the walker to another room
  await page.evaluate(() => window.viewer.jump('hallway')); await idle(page, 200);
  const pb = await page.locator('#plan-canvas').boundingBox();
  const m0 = await page.evaluate(() => { const p = window.viewer.planView, [X, Y] = p.toScreen(p.viewer.x, p.viewer.y); return [X / p.c.width, Y / p.c.height]; });
  await page.mouse.move(pb.x + m0[0] * pb.width, pb.y + m0[1] * pb.height);
  for (let k = 0; k < 6; k++) { await page.mouse.wheel(0, -200); await page.waitForTimeout(60); }
  await page.mouse.move(900, 600);
  const zoomed = [];
  for (const r of ['dining', 'kitchen', 'blue_bedroom', 'loft_office']) {
    await page.evaluate((r) => window.viewer.jump(r), r); await idle(page, 200);
    zoomed.push(await page.evaluate(() => { const p = window.viewer.planView, [X, Y] = p.toScreen(p.viewer.x, p.viewer.y); return { s: p.v.s, inside: X > 0 && X < p.c.width && Y > 0 && Y < p.c.height }; }));
  }
  await shot(page, 'nav_plan_follow.png', '#plan');
  check(zoomed.every((z) => z.inside) && zoomed[0].s > 2 * (await page.evaluate(() => { const p = window.viewer.planView, b = p.bounds; return Math.min(p.c.width / (b.maxX - b.minX), p.c.height / (b.maxY - b.minY)); })),
    `zoomed plan keeps the marker in view in dining, kitchen, blue bedroom, loft (${zoomed.map((z) => z.inside)})`);
  // NAV-PLAN-FOOTER-TRUNC: the scale is never cut off; the coordinate readout clears when the pointer leaves the plan
  await page.mouse.move(pb.x + pb.width / 2, pb.y + pb.height / 2); await page.waitForTimeout(100);
  const xy0 = await page.textContent('#plan-xy'), cut = await page.evaluate(() => { const t = document.querySelector('#plan-title'); return t.scrollWidth > t.clientWidth + 1; });
  await page.mouse.move(900, 600); await page.waitForTimeout(100);
  check(/^X -?\d+ +Y -?\d+$/.test(xy0) && !cut && (await page.textContent('#plan-xy')) === '', `plan footer: "${await page.textContent('#plan-title')}" whole while the readout shows "${xy0}"; readout cleared on leave`);
  // Q13: the dollhouse on level 2 over the stairwell names no ground-floor room
  await page.evaluate(() => window.viewer.setMode('orbit')); await page.waitForTimeout(400);
  await page.click('#dh-levels button[data-level="2"]'); await page.waitForTimeout(300);
  await page.evaluate(() => { const { orbit, camera } = window.viewer, d = camera.position.clone().sub(orbit.target); orbit.target.set(0.57, 6.02, -7.0); camera.position.copy(orbit.target).add(d); orbit.update(); }); await settle(page, 100);
  const dh = await page.evaluate(() => ({ room: document.querySelector('#plan-room').textContent, sheet: window.viewer.planView.sheetId }));
  check(dh.sheet === '2' && !/kitchen|hall|living|dining/i.test(dh.room), `dollhouse level 2 over the stairwell: sheet ${dh.sheet}, header "${dh.room}"`);
  await page.evaluate(() => window.viewer.setMode('walk'));
  await ctx.close();
  // phones: 1.5x pixels at most
  {
    const { ctx, page } = await open({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true });
    const pr = await page.evaluate(() => window.viewer.renderer.getPixelRatio());
    check(pr <= 1.5, `phone: renderer pixel ratio ${pr} (device 3)`);
    await ctx.close();
  }
}

await browser.close(); server.close();
await writeFile(OUT + 'console.txt', logs.join('\n'));
console.log(`\nscreenshots + console.txt in ${OUT}`);
console.log(fails.length ? `FAILED (${fails.length}):\n  ${fails.join('\n  ')}` : 'ALL CHECKS PASSED');
process.exit(fails.length ? 1 : 0);

// End-to-end check of the viewer in Chromium. Serves docs/ under /home-design/ (like GitHub Pages), drives the page,
// writes screenshots + console log to build/e2e/, exits non-zero on console errors or failed checks.
// Setup once:  npm install --prefix build/e2e playwright@1.65.1   (npx playwright install chromium if no browser yet)
// Run:         node docs/test/e2e.mjs [--headed]
import { createServer } from 'node:http';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { extname, join, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = fileURLToPath(new URL('../', import.meta.url)), OUT = fileURLToPath(new URL('../../build/e2e/', import.meta.url));
const { chromium } = createRequire(OUT)('playwright');
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.json': 'application/json',
  '.glb': 'model/gltf-binary', '.jpg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp', '.ktx2': 'image/ktx2', '.dxf': 'image/vnd.dxf', '.pdf': 'application/pdf' };
const server = createServer(async (req, res) => {
  const url = decodeURIComponent(req.url.split('?')[0]);
  if (!url.startsWith('/home-design/')) { res.writeHead(404).end(); return; }
  const rel = normalize(url.slice('/home-design/'.length) || 'index.html').replace(/^([/\\]|\.\.)+/, '');
  try {
    const body = await readFile(join(ROOT, rel.endsWith('/') || !rel ? join(rel, 'index.html') : rel));
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
  page.on('pageerror', (e) => { logs.push('[pageerror] ' + e.message); fails.push('pageerror: ' + e.message); });
  await page.goto(BASE + query);
  await page.waitForSelector('#loader.done', { timeout: 60000 });
  await page.waitForTimeout(800);
  return { ctx, page };
}
const info = (page) => page.evaluate(() => window.viewer.info());
const shot = (page, name, el) => (el ? page.locator(el).screenshot({ path: OUT + name }) : page.screenshot({ path: OUT + name }));

// ---- desktop ----
{
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
    window.viewer.scene.traverse((o) => o.isMesh && all.push(...[].concat(o.material).map((mat) => ({ o, mat }))));
    const lit = all.filter((a) => a.o.userData.baked);
    return { listed: m.lightmaps.reduce((n, l) => n + l.objects.length, 0), probes: m.probes.length, standin: !!m.standin,
      noEnv: all.filter((a) => !a.mat.envMap).length, noUv1: lit.filter((a) => !a.o.geometry.attributes.uv1).length,
      badLm: lit.filter(({ mat }) => !(mat.lightMap?.channel === 1 && mat.lightMap.flipY === false && mat.lightMap.colorSpace === 'srgb' && mat.lightMapIntensity > 3)).length };
  });
  check(!bake.standin && bake.listed > 50 && bake.probes >= 7, `real export manifest (${bake.listed} lightmapped objects, ${bake.probes} probes)`);
  check(bake.noUv1 === 0 && bake.badLm === 0, 'lightmaps on uv1, flipY off, sRGB, intensity x PI');
  check(i.probed > 0 && bake.noEnv === 0, `room probes on every material (${i.probed} meshes lit by probe alone)`);
  check(!logs.some((l) => /not found in the GLB|no second UV|image missing|shader changed/.test(l)), 'no lightmap / probe warnings');
  await shot(page, 'walk_spawn.png');

  // keyboard walking: W for 1 s moves forward (+Y) and stays inside the walkable area
  await page.locator('#scene').focus();
  await page.keyboard.down('KeyW'); await page.waitForTimeout(1000); await page.keyboard.up('KeyW');
  const j = await info(page);
  check(j.y > i.y + 0.5 && Math.abs(j.x - i.x) < 0.05, `W walks into the house (y ${i.y.toFixed(2)} -> ${j.y.toFixed(2)})`);
  check(await page.evaluate(() => { const v = window.viewer; return !v.walk || v.G.isFree(v.walk, v.S.x, v.S.y); }), 'position is inside the walkable area');
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
  await page.getByRole('button', { name: /^Living/ }).click(); await page.waitForTimeout(1200);
  i = await info(page); check(i.room === 'living', `room button -> living (${i.room})`);
  await page.keyboard.press('Digit6'); await page.waitForTimeout(1200);   // 6th room in the list
  i = await info(page); check(i.room === 'utility', `key 6 -> utility (${i.room})`);
  for (const id of await page.evaluate(() => Object.keys(window.viewer.vps))) {
    await page.evaluate((id) => window.viewer.jump(id), id); await page.waitForTimeout(1100);
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
    return window.viewer.walk.portals.map((q) => ({ id: q.id, c: q.center, n: q.normal, w: q.width, pocket: house.openings.find((o) => o.id === q.id).slideToward ? 0.1 : 0 }));
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
      const hatch = p.plan.entities.filter((e) => e.type === 'hatch' && e.layer === 'A-WALL-PATT');
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
  await page.evaluate(() => window.viewer.jump('dining')); await page.waitForTimeout(1200);

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
  await page.mouse.click(...target); await page.waitForTimeout(1200);
  i = await info(page); check(i.room === 'kitchen', `plan click teleports to the kitchen (${i.room} @ ${i.x.toFixed(2)},${i.y.toFixed(2)})`);
  await shot(page, 'teleport_kitchen.png');
  // click into a wall lands on the nearest free point
  await page.evaluate(() => window.viewer.teleport(0.725, 3.0)); await page.waitForTimeout(900);
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
  for (const [sel, name, magic] of [['#dl-dxf', 'ground-floor-plan.dxf', 'SECTION'], ['#dl-pdf', 'ground-floor-plan.pdf', '%PDF']]) {
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
{
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
{
  const { ctx, page } = await open({ viewport: { width: 1280, height: 800 } }, '?lighting=realtime');
  check((await info(page)).realtime, 'realtime fallback active with ?lighting=realtime');
  await page.evaluate(() => window.viewer.jump('living')); await page.waitForTimeout(1500);
  await shot(page, 'realtime_living.png');
  await ctx.close();
}
// ---- phone ----
{
  const { ctx, page } = await open({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true });
  check(await page.evaluate(() => document.body.classList.contains('touch')), 'touch UI on a phone');
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
  await page.touchscreen.tap(...tap); await page.waitForTimeout(1200);
  const i2 = await info(page); check(i2.room === 'dining', `tap on the plan teleports (${i2.room})`);
  await page.tap('#plan-max'); await page.tap('#mode-orbit'); await page.waitForTimeout(800); await shot(page, 'phone_orbit.png');
  await ctx.close();
}
await browser.close(); server.close();
await writeFile(OUT + 'console.txt', logs.join('\n'));
console.log(`\nscreenshots + console.txt in ${OUT}`);
console.log(fails.length ? `FAILED (${fails.length}):\n  ${fails.join('\n  ')}` : 'ALL CHECKS PASSED');
process.exit(fails.length ? 1 : 0);

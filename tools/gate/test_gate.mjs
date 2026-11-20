// Check of the password gate: seals docs/ into build/gate_test with a throwaway password, serves it under /home-design/
// like GitHub Pages and drives Chromium: the stored files are ciphertext, a wrong password is refused, the right one
// loads the house (interaction groups appear, the PDF decrypts), a reload remembers the key, ?lock asks again.
// Run: node tools/gate/test_gate.mjs   (Playwright from build/e2e, as docs/test/e2e.mjs)          -> GATE OK
import { execFileSync } from 'node:child_process';
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { extname, join, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';

const REPO = fileURLToPath(new URL('../../', import.meta.url));
const SITE = join(REPO, 'build/gate_test'), PW = 'gate-test-password';
execFileSync('python', [join(REPO, 'tools/gate/seal.py'), '--out', SITE], { env: { ...process.env, VIEWER_PASSWORD: PW }, stdio: 'inherit' });

const fails = [];
const check = (ok, what) => { console.log(`${ok ? 'PASS' : 'FAIL'}  ${what}`); if (!ok) fails.push(what); };
const head = async (f) => (await readFile(join(SITE, f))).subarray(0, 4).toString('latin1');
check(await head('assets/glb/G.glb') !== 'glTF', 'stored G.glb is not a readable glTF');
check(!(await head('assets/manifest.json')).startsWith('{'), 'stored manifest.json is not readable JSON');

let stale = true;          // first: a plain manifest from 'before the deploy', cached by the browser (Pages sends max-age 600)
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json' };
const server = createServer(async (req, res) => {
  const url = decodeURIComponent(req.url.split('?')[0]);
  if (!url.startsWith('/home-design/')) { res.writeHead(404).end(); return; }
  const rel = normalize(url.slice(13) || 'index.html').replace(/^([/\\]|\.\.)+/, '');
  try {
    const old = stale && rel.replace(/\\/g, '/') === 'assets/manifest.json';
    const body = await readFile(old ? join(REPO, 'docs/assets/manifest.json') : join(SITE, rel));
    res.writeHead(200, { 'content-type': TYPES[extname(rel)] || 'application/octet-stream', 'content-length': body.length, 'cache-control': 'max-age=600' });
    res.end(req.method === 'HEAD' ? undefined : body);
  } catch { res.writeHead(404).end(); }
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const BASE = `http://127.0.0.1:${server.address().port}/home-design/`;

const { chromium } = createRequire(join(REPO, 'build/e2e/'))('playwright');
const launch = (channel) => chromium.launch({ channel, args: ['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist'] });
const browser = await launch(undefined).catch(() => launch('chrome'));
const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 }, acceptDownloads: true }), page = await ctx.newPage();
const errors = [];
page.on('pageerror', (e) => errors.push(String(e)));
const loaded = () => page.waitForFunction(() => window.viewer?.ix?.groups?.().length > 0, null, { timeout: 240000 }).then(() => true, () => false);

await page.goto(BASE + 'assets/manifest.json');   // no worker yet: the plain copy lands in the HTTP cache
stale = false;
await page.goto(BASE);
await page.waitForSelector('#gate:not([hidden])', { timeout: 30000 });
check(true, 'gate shown on the first visit');
await page.fill('#gate-pw', 'not-the-password');
await page.click('#gate button');
await page.waitForFunction(() => document.querySelector('#gate-msg').textContent.includes('Wrong'), null, { timeout: 30000 });
check(await page.isVisible('#gate'), 'wrong password refused, gate stays');
await page.fill('#gate-pw', PW);
await page.click('#gate button');
check(await loaded(), 'right password: the house loads, past a stale cached manifest (interaction groups present)');
const pdf = await page.evaluate(() => fetch('assets/house-plans.pdf').then((r) => r.arrayBuffer()).then((b) => new TextDecoder().decode(b.slice(0, 4))));
check(pdf === '%PDF', `plan PDF decrypts through the worker (${pdf})`);
await page.screenshot({ path: join(REPO, 'build/gate_test_open.png') });
for (const [sel, magic] of [['#dl-pdf', '%PDF'], ['#dl-dxf', '  0']]) {   // the download buttons, as a visitor clicks them
  const [dl] = await Promise.all([page.waitForEvent('download', { timeout: 30000 }), page.click(sel)]).catch(() => [null]);
  const got = dl ? (await readFile(await dl.path())).subarray(0, 4).toString('latin1') : 'no download';
  check(got.startsWith(magic), `${sel} downloads a readable file (${JSON.stringify(got)})`);
}

await page.reload();
check(await loaded() && !(await page.isVisible('#gate')), 'reload: key remembered, no gate');
await page.goto(BASE + '?lock');
await page.waitForSelector('#gate:not([hidden])', { timeout: 30000 }).then(() => check(true, '?lock forgets the key'), () => check(false, '?lock forgets the key'));
await page.screenshot({ path: join(REPO, 'build/gate_test_locked.png') });

check(!errors.length, `no page errors${errors.length ? ': ' + errors.join(' | ') : ''}`);
await browser.close(); server.close();
console.log(fails.length ? `GATE FAILED: ${fails.length}` : 'GATE OK');
process.exit(fails.length ? 1 : 0);

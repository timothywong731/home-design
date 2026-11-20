// Service worker of a sealed site (tools/gate/seal.py): files under assets/ and renders/ are AES-256-GCM ciphertext
// (12-byte IV in front). It decrypts them with the key js/gate.js derived from the password, so the viewer code loads
// them as usual. The key (non-extractable) is kept in IndexedDB: a return visit does not ask again until the site is
// re-sealed (new salt) or the page is opened with ?lock.
const SEALED = /\/(assets|renders)\//;
const TYPES = { glb: 'model/gltf-binary', json: 'application/json', jpg: 'image/jpeg', png: 'image/png', webp: 'image/webp',
  ktx2: 'image/ktx2', dxf: 'image/vnd.dxf', pdf: 'application/pdf' };
let key = null;

const db = () => new Promise((ok, no) => {
  const r = indexedDB.open('gate', 1);
  r.onupgradeneeded = () => r.result.createObjectStore('k');
  r.onsuccess = () => ok(r.result); r.onerror = () => no(r.error);
});
const store = async (v) => { const t = (await db()).transaction('k', 'readwrite');
  if (v) t.objectStore('k').put(v, 'key'); else t.objectStore('k').delete('key');
  return new Promise((ok, no) => { t.oncomplete = ok; t.onerror = () => no(t.error); }); };
const stored = async () => { const r = (await db()).transaction('k').objectStore('k').get('key');
  return new Promise((ok) => { r.onsuccess = () => ok(r.result || null); r.onerror = () => ok(null); }); };
const open = (k, buf) => crypto.subtle.decrypt({ name: 'AES-GCM', iv: buf.slice(0, 12) }, k, buf.slice(12));
const unb64 = (s) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0)).buffer;

self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (e) => e.waitUntil(self.clients.claim()));
self.addEventListener('message', (e) => {
  reply(e.data).then((r) => e.ports[0].postMessage(r), (err) => e.ports[0].postMessage({ ok: false, error: String(err) }));
});

async function reply(m) {
  if (m.op === 'claim') { await self.clients.claim(); return { ok: true }; }
  if (m.op === 'lock') { key = null; await store(null); return { ok: true }; }
  if (m.op === 'key') { key = m.key; await store(key); return { ok: true }; }
  if (m.op === 'has') {                                 // does the remembered key open this seal?
    key ||= await stored();
    if (!key) return { ok: false };
    try { await open(key, unb64(m.check)); return { ok: true }; } catch { key = null; return { ok: false }; }
  }
  return { ok: false, error: 'unknown op' };
}

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  const scope = new URL(self.registration.scope).pathname;
  if (url.origin !== location.origin || !url.pathname.startsWith(scope) || !SEALED.test(url.pathname.slice(scope.length - 1))) return;
  e.respondWith(serve(e.request, url));
});

async function serve(req, url) {
  key ||= await stored();
  if (!key) return new Response('locked', { status: 401 });
  const type = TYPES[url.pathname.split('.').pop().toLowerCase()] || 'application/octet-stream';
  // The HTTP cache (Pages: max-age 600) can still hold a copy from before the last deploy - plain, or sealed with an
  // older salt - which this key cannot open: then fetch it again past the cache, once.
  for (const cache of ['default', 'reload']) {
    const r = await fetch(req.url, { method: req.method, cache });
    if (!r.ok) return r;
    if (req.method === 'HEAD') return new Response(null, { headers: { 'Content-Type': type } });
    try {
      const body = await open(key, await r.arrayBuffer());
      return new Response(body, { headers: { 'Content-Type': type, 'Content-Length': String(body.byteLength) } });
    } catch { /* stale copy: retry */ }
  }
  return new Response('wrong key', { status: 403 });
}

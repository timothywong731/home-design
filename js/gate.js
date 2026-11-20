// Password gate (tools/gate/seal.py). On a sealed site gate.json carries the PBKDF2 salt and a sealed check string;
// assets/ and renders/ are ciphertext that ../sw.js decrypts with the key derived here. docs/gate.json is
// {"sealed": false} (local dev, tests): nothing to do.
const unb64 = (s) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0));

export async function unlock(form, input, note) {
  const gate = await fetch('gate.json', { cache: 'no-cache' }).then((r) => (r.ok ? r.json() : null)).catch(() => null);
  if (!gate?.salt) return;
  const sw = navigator.serviceWorker;
  if (!sw || !crypto.subtle) throw new Error('This browser cannot open the private walkthrough (needs HTTPS, service workers and Web Crypto).');
  const reg = await sw.register('sw.js');
  await sw.ready;
  const ask = (m) => new Promise((ok) => {
    const c = new MessageChannel();
    c.port1.onmessage = (e) => ok(e.data);
    reg.active.postMessage(m, [c.port2]);
  });
  if (!sw.controller) {                                 // first visit or a hard reload: the worker must take this page
    const claimed = new Promise((r) => sw.addEventListener('controllerchange', r, { once: true }));
    await ask({ op: 'claim' });
    await Promise.race([claimed, new Promise((r) => setTimeout(r, 3000))]);
    if (!sw.controller) { location.reload(); await new Promise(() => {}); }
  }
  if (new URLSearchParams(location.search).has('lock')) await ask({ op: 'lock' });
  else if ((await ask({ op: 'has', check: gate.check })).ok) return;

  const check = unb64(gate.check), salt = unb64(gate.salt);
  form.hidden = false;
  input.focus();
  for (;;) {
    await new Promise((r) => form.addEventListener('submit', (e) => { e.preventDefault(); r(); }, { once: true }));
    note.textContent = 'Checking…';
    const base = await crypto.subtle.importKey('raw', new TextEncoder().encode(input.value), 'PBKDF2', false, ['deriveKey']);
    const key = await crypto.subtle.deriveKey({ name: 'PBKDF2', hash: 'SHA-256', salt, iterations: gate.iter },
      base, { name: 'AES-GCM', length: 256 }, false, ['decrypt']);
    try {
      await crypto.subtle.decrypt({ name: 'AES-GCM', iv: check.slice(0, 12) }, key, check.slice(12));
    } catch {
      note.textContent = 'Wrong password';
      input.select();
      continue;
    }
    await ask({ op: 'key', key });
    form.hidden = true;
    note.textContent = '';
    return;
  }
}

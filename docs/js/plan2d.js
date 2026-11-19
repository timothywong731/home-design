// CAD-style 2D plan on a <canvas>: draws assets/plan.json (world metres, +X right, +Y = rear, drawn UP the sheet)
// with layer colours, lineweights, linetypes, hatches, text and dimensions; pan/zoom/pinch; live viewer marker
// with view cone; current-room highlight; click/tap = pick (teleport). No three.js dependency.
// plan.json schema 2 holds several sheets (B G 1 2 X) in one world frame: setSheet(id) switches; schema 1 = one sheet G.

const LT = { dashed: [0.12, 0.06], hidden: [0.06, 0.04], center: [0.3, 0.06, 0.06, 0.06] };   // metres
const THEME = {
  cad: { bg: '#1c1f23', ink: '#e8e8e8', hl: 'rgba(90,170,255,0.16)', hlEdge: 'rgba(120,190,255,0.85)', mark: '#ff6a3d', cone: 'rgba(255,106,61,0.22)' },
  paper: { bg: '#fbfaf6', ink: '#111111', hl: 'rgba(0,105,230,0.09)', hlEdge: 'rgba(0,90,200,0.75)', mark: '#e0401a', cone: 'rgba(224,64,26,0.16)' },
};
export const CAD_FONT = '"ISOCPEUR","osifont","Consolas","Menlo","DejaVu Sans Mono",monospace';

export class PlanView {
  constructor(canvas, plan, { onPick, onHover, sheet } = {}) {
    Object.assign(this, { c: canvas, ctx: canvas.getContext('2d'), plan, onPick, onHover });
    this.layers = new Map((plan.layers || []).map((l) => [l.name, l]));
    this.sheets = plan.sheets?.length ? plan.sheets : [{ ...plan, id: 'G', level: 'G' }];
    this.theme = 'cad'; this.cache = document.createElement('canvas');
    this.v = { cx: 0, cy: 0, s: 1 }; this.dpr = 1; this.fitted = false; this.dirty = true;
    this.viewer = null; this.room = null; this.key = ''; this.ptr = new Map(); this.pinched = false;
    this.setSheet(this.sheets.some((s) => s.id === sheet) ? sheet : (this.sheets.find((s) => s.id === 'G') || this.sheets[0]).id);
    new ResizeObserver(() => this.resize()).observe(canvas);
    this.bind();
  }
  // switch sheet: its entities, rooms, bounds and the style tables that are model metres at its scale. The view stays
  // where it is between floor sheets (one world frame); to or from the site sheet it refits. -> true if it changed
  setSheet(id) {
    const s = this.sheets.find((q) => q.id === id), was = this.sheet;
    if (!s || s === was) return false;
    Object.assign(this, { sheet: s, sheetId: s.id, entities: s.entities || [], rooms: s.rooms || [], bounds: s.bounds });
    this.lt = { ...LT, ...(s.linestyles || {}) };                          // plan.json may carry its own styles
    this.ds = { tick: 0.065, extGap: 0.06, extBeyond: 0.08, ...(s.dimstyle || {}) };
    this.hsp = s.hatch?.spacing || 0.09;
    this.key = '';
    if (was && (was.id === 'X') !== (s.id === 'X')) this.fitted = false;
    if (!this.sized) return true;                            // the first resize() fits
    if (!this.fitted) this.fit(); else { this.dirty = true; this.draw(); }
    return true;
  }

  // ---- view ----
  resize() {
    const r = this.c.getBoundingClientRect(); if (!r.width || !r.height) return;
    this.dpr = Math.min(devicePixelRatio || 1, 3);
    const w = Math.round(r.width * this.dpr), h = Math.round(r.height * this.dpr);
    if (w === this.c.width && h === this.c.height && this.sized) return;
    const keep = this.fitted && this.c.width ? this.toWorld(this.c.width / 2, this.c.height / 2) : null;
    this.c.width = this.cache.width = w; this.c.height = this.cache.height = h; this.sized = true;
    if (!this.fitted) this.fit(); else { [this.v.cx, this.v.cy] = keep; this.dirty = true; this.draw(); }
  }
  fit() {
    const b = this.bounds, W = this.c.width, H = this.c.height, pad = 14 * this.dpr;
    if (!W || !H) return;
    this.v.s = Math.min((W - 2 * pad) / (b.maxX - b.minX), (H - 2 * pad) / (b.maxY - b.minY));
    this.v.cx = (b.minX + b.maxX) / 2; this.v.cy = (b.minY + b.maxY) / 2;
    this.fitted = true; this.dirty = true; this.draw();
  }
  zoomAt(X, Y, f) {
    const [wx, wy] = this.toWorld(X, Y), b = this.bounds;
    const fitS = Math.min(this.c.width / (b.maxX - b.minX), this.c.height / (b.maxY - b.minY));
    this.v.s = Math.min(Math.max(this.v.s * f, fitS * 0.3), fitS * 40);
    const [X2, Y2] = this.toScreen(wx, wy); this.v.cx += (X2 - X) / this.v.s; this.v.cy -= (Y2 - Y) / this.v.s;
    this.dirty = true; this.draw();
  }
  toScreen(x, y) { return [(x - this.v.cx) * this.v.s + this.c.width / 2, this.c.height / 2 - (y - this.v.cy) * this.v.s]; }
  toWorld(X, Y) { return [(X - this.c.width / 2) / this.v.s + this.v.cx, this.v.cy - (Y - this.c.height / 2) / this.v.s]; }
  setTheme(t) { this.theme = t; this.dirty = true; this.draw(); }
  // viewer = { x, y, dir:[dx,dy] (plan frame), hfov (rad), mark: 'full' (default) | 'hollow' | null (not drawn) };
  // room = room object or null (highlighted with this sheet's polygon for it; a plan without rooms uses room.polygon)
  setViewer(viewer, room) {
    const k = `${viewer.x.toFixed(3)},${viewer.y.toFixed(3)},${viewer.dir[0].toFixed(3)},${viewer.dir[1].toFixed(3)},${viewer.hfov.toFixed(3)},${room?.id},${viewer.mark}`;
    this.viewer = viewer; this.room = room;
    if (k !== this.key) { this.key = k; this.draw(); }
  }

  // ---- drawing ----
  worldTx(g) { const s = this.v.s; g.setTransform(s, 0, 0, -s, this.c.width / 2 - this.v.cx * s, this.c.height / 2 + this.v.cy * s); }
  draw() {
    if (!this.c.width) return;
    if (this.dirty) { this.renderStatic(); this.dirty = false; }
    const g = this.ctx, T = THEME[this.theme], s = this.v.s;
    g.setTransform(1, 0, 0, 1, 0, 0); g.drawImage(this.cache, 0, 0);
    const poly = this.room && (this.rooms.length ? this.rooms.find((r) => r.id === this.room.id)?.polygon : this.room.polygon);
    if (poly) {
      this.worldTx(g); g.beginPath(); poly.forEach(([x, y], i) => (i ? g.lineTo(x, y) : g.moveTo(x, y))); g.closePath();
      g.fillStyle = T.hl; g.fill(); g.strokeStyle = T.hlEdge; g.lineWidth = (1.5 * this.dpr) / s; g.setLineDash([]); g.stroke();
    }
    const vw = this.viewer; if (!vw || vw.mark === null) return;
    const hollow = vw.mark === 'hollow';                     // the site sheet while indoors: outline marker
    g.setTransform(1, 0, 0, 1, 0, 0);
    const [X, Y] = this.toScreen(vw.x, vw.y), a = Math.atan2(-vw.dir[1], vw.dir[0]), h = vw.hfov / 2;
    const R = Math.max(3 * s, 46 * this.dpr), grad = g.createRadialGradient(X, Y, 0, X, Y, R);
    grad.addColorStop(0, T.mark + (hollow ? '44' : 'aa')); grad.addColorStop(1, T.mark + '00');
    g.beginPath(); g.moveTo(X, Y); g.arc(X, Y, R, a - h, a + h); g.closePath(); g.fillStyle = grad; g.fill();
    g.strokeStyle = T.mark; g.lineWidth = this.dpr; g.beginPath();
    g.moveTo(X + Math.cos(a - h) * R, Y + Math.sin(a - h) * R); g.lineTo(X, Y); g.lineTo(X + Math.cos(a + h) * R, Y + Math.sin(a + h) * R); g.stroke();
    g.beginPath(); g.arc(X, Y, 5 * this.dpr, 0, Math.PI * 2);
    if (hollow) { g.lineWidth = 2 * this.dpr; g.strokeStyle = T.mark; g.stroke(); return; }
    g.fillStyle = T.mark; g.fill();
    g.lineWidth = 1.5 * this.dpr; g.strokeStyle = T.bg; g.stroke();
  }

  renderStatic() {
    const g = this.cache.getContext('2d'), T = THEME[this.theme], s = this.v.s, px = this.dpr / s;
    g.setTransform(1, 0, 0, 1, 0, 0); g.fillStyle = T.bg; g.fillRect(0, 0, this.cache.width, this.cache.height);
    g.lineCap = 'round'; g.lineJoin = 'round';
    const texts = [];
    for (const e of this.entities) {
      const L = this.layers.get(e.layer) || {}, col = (this.theme === 'paper' ? L.paper : L.color) || T.ink;
      if (e.type === 'text') { texts.push([e, col]); continue; }
      this.worldTx(g);
      g.strokeStyle = g.fillStyle = col;
      g.lineWidth = Math.min(Math.max((L.lineweight || 0.18) * 3.2, 0.7), 3.2) * px;
      const d = this.lt[e.ls]; g.setLineDash(d ? d.map((m) => Math.max(m, (m / d[0]) * 6 * px)) : []);
      if (e.type === 'dim') { this.dim(g, e, col, px); continue; }
      g.beginPath();
      if (e.type === 'line') { g.moveTo(...e.p1); g.lineTo(...e.p2); g.stroke(); }
      else if (e.type === 'polyline') { this.path(g, e.pts, e.closed); g.stroke(); }
      else if (e.type === 'arc') { g.arc(e.c[0], e.c[1], e.r, (e.a0 * Math.PI) / 180, (e.a1 * Math.PI) / 180, false); g.stroke(); }
      else if (e.type === 'circle') { g.arc(e.c[0], e.c[1], e.r, 0, Math.PI * 2); g.stroke(); }
      else if (e.type === 'hatch') this.hatch(g, e, px);
    }
    g.setTransform(1, 0, 0, 1, 0, 0); g.setLineDash([]); g.textBaseline = 'middle';
    for (const [e, col] of texts) this.text(g, e.p, e.h, e.text, e.align, e.rot, col);
  }
  path(g, pts, closed) { pts.forEach(([x, y], i) => (i ? g.lineTo(x, y) : g.moveTo(x, y))); if (closed) g.closePath(); }
  hatch(g, e, px) {
    this.path(g, e.pts, true);
    if (e.pattern !== 'ANSI31') { g.fill(); return; }
    g.save(); g.clip(); g.lineWidth = 0.8 * px; g.setLineDash([]);
    const xs = e.pts.map((p) => p[0]), ys = e.pts.map((p) => p[1]);
    const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
    // 45 deg lines x - y = k through the world origin (adjacent hatches line up); thinned out when < 3 px apart
    const step = this.hsp * Math.SQRT2 * Math.max(1, Math.ceil((3 * px) / this.hsp)); g.beginPath();
    for (let k = Math.floor((x0 - y1) / step) * step; k <= x1 - y0; k += step) { g.moveTo(k + y0, y0); g.lineTo(k + y1, y1); }
    g.stroke(); g.restore();
  }
  text(g, p, h, str, align = 'left', rot = 0, col) {
    const size = h * this.v.s; if (size < 3 * this.dpr || !str) return;
    const [X, Y] = this.toScreen(p[0], p[1]);
    g.save(); g.translate(X, Y); g.rotate((-(rot || 0) * Math.PI) / 180);
    g.font = `${size}px ${CAD_FONT}`; g.textAlign = align || 'left'; g.fillStyle = col; g.fillText(str, 0, 0); g.restore();
  }
  // dimension: extension lines, dimension line at `offset` (+ = left of p1->p2), 45deg ticks, value above the line
  dim(g, e, col, px) {
    const [x1, y1] = e.p1, [x2, y2] = e.p2, L = Math.hypot(x2 - x1, y2 - y1); if (!L) return;
    const ux = (x2 - x1) / L, uy = (y2 - y1) / L, nx = -uy, ny = ux, o = e.offset || 0, sg = Math.sign(o) || 1;
    const a = [x1 + nx * o, y1 + ny * o], b = [x2 + nx * o, y2 + ny * o], gap = this.ds.extGap * sg, ext = this.ds.extBeyond * sg;
    const tk = Math.max(this.ds.tick, 5 * px);
    g.setLineDash([]); g.beginPath();
    g.moveTo(x1 + nx * gap, y1 + ny * gap); g.lineTo(a[0] + nx * ext, a[1] + ny * ext);
    g.moveTo(x2 + nx * gap, y2 + ny * gap); g.lineTo(b[0] + nx * ext, b[1] + ny * ext);
    g.moveTo(a[0] - ux * tk, a[1] - uy * tk); g.lineTo(b[0] + ux * tk, b[1] + uy * tk);
    for (const [cx, cy] of [a, b]) { g.moveTo(cx - (ux + nx) * tk * 0.7, cy - (uy + ny) * tk * 0.7); g.lineTo(cx + (ux + nx) * tk * 0.7, cy + (uy + ny) * tk * 0.7); }
    g.stroke();
    let ang = (Math.atan2(uy, ux) * 180) / Math.PI; if (ang > 90.01 || ang < -89.99) ang += 180;   // keep text readable
    const ar = (ang * Math.PI) / 180, up = [-Math.sin(ar), Math.cos(ar)], h = e.h || this.ds.h || 0.1;
    const m = e.tp || [(a[0] + b[0]) / 2 + up[0] * h * 0.7, (a[1] + b[1]) / 2 + up[1] * h * 0.7];
    g.save(); g.setTransform(1, 0, 0, 1, 0, 0); g.textBaseline = 'middle';
    this.text(g, m, h, e.text ?? String(Math.round(L * 1000)), 'center', ang, col); g.restore();
  }

  // ---- input ----
  pos(e) { const r = this.c.getBoundingClientRect(); return [((e.clientX - r.left) * this.c.width) / r.width, ((e.clientY - r.top) * this.c.height) / r.height]; }
  bind() {
    const c = this.c;
    c.addEventListener('wheel', (e) => { e.preventDefault(); this.zoomAt(...this.pos(e), Math.exp(-e.deltaY * 0.0015)); }, { passive: false });
    c.addEventListener('pointerdown', (e) => {
      c.setPointerCapture(e.pointerId); c.focus({ preventScroll: true });
      this.ptr.set(e.pointerId, { x: e.clientX, y: e.clientY, x0: e.clientX, y0: e.clientY, moved: false });
      if (this.ptr.size > 1) this.pinched = true;
    });
    c.addEventListener('pointermove', (e) => {
      const p = this.ptr.get(e.pointerId);
      if (!p) { this.onHover?.(...this.toWorld(...this.pos(e))); return; }
      const k = this.dpr / this.v.s;
      if (this.ptr.size === 1) {
        if (Math.hypot(e.clientX - p.x0, e.clientY - p.y0) > 5) p.moved = true;
        if (p.moved) { this.v.cx -= (e.clientX - p.x) * k; this.v.cy += (e.clientY - p.y) * k; this.dirty = true; this.draw(); }
      } else if (this.ptr.size === 2) {
        const [q] = [...this.ptr.values()].filter((v) => v !== p);
        const d0 = Math.hypot(p.x - q.x, p.y - q.y), d1 = Math.hypot(e.clientX - q.x, e.clientY - q.y);
        const r = c.getBoundingClientRect(), mx = ((e.clientX + q.x) / 2 - r.left) * this.dpr, my = ((e.clientY + q.y) / 2 - r.top) * this.dpr;
        this.v.cx -= ((e.clientX - p.x) / 2) * k; this.v.cy += ((e.clientY - p.y) / 2) * k;
        if (d0 > 0) this.zoomAt(mx, my, d1 / d0); else { this.dirty = true; this.draw(); }
      }
      p.x = e.clientX; p.y = e.clientY;
    });
    const up = (e) => {
      const p = this.ptr.get(e.pointerId); this.ptr.delete(e.pointerId);
      if (p && !p.moved && !this.pinched && e.type === 'pointerup') this.onPick?.(...this.toWorld(...this.pos(e)));
      if (!this.ptr.size) this.pinched = false;
    };
    c.addEventListener('pointerup', up); c.addEventListener('pointercancel', up);
    c.addEventListener('keydown', (e) => {
      const st = 40 * this.dpr, mid = [c.width / 2, c.height / 2], pan = { ArrowLeft: [-st, 0], ArrowRight: [st, 0], ArrowUp: [0, -st], ArrowDown: [0, st] }[e.key];
      if (e.key === '+' || e.key === '=') this.zoomAt(...mid, 1.25);
      else if (e.key === '-' || e.key === '_') this.zoomAt(...mid, 0.8);
      else if (e.key === '0') this.fit();
      else if (pan) { this.v.cx += pan[0] / this.v.s; this.v.cy -= pan[1] / this.v.s; this.dirty = true; this.draw(); }
      else return;
      e.preventDefault(); e.stopPropagation();
    });
  }
}

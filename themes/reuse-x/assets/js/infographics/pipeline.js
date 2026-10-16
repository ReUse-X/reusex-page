// Infographic "pipeline": scan → AI labels every point → material list.
// 12 s loop on the near-black scan canvas (same in both themes). Quantities
// are drawn as bars, not numbers: the list is illustrative. The figure
// (≈ 1,700 m² · 30 min) is the documented survey from the public deck.
import { clamp, ease, el, mix, rgb, seeded, show, token } from './lib.js';

export const duration = 12;
export const still = 10.5;
export const layouts = { wide: { w: 1920, h: 1080 }, tall: { w: 640, h: 1300 } };

const CLASSES = ['floor', 'wall', 'window', 'door', 'radiator', 'table'];
const ROWS = [
  ['window', 'Windows', 0.55, 'Reuse'],
  ['door', 'Doors', 0.3, 'Reuse'],
  ['radiator', 'Radiators', 0.4, 'Reuse'],
  ['table', 'Furniture', 0.7, 'Reuse'],
  ['floor', 'Floor finish', 0.95, 'Recycle'],
  ['wall', 'Partition walls', 0.8, 'Keep'],
];

// Layout: everything in stage px.
const L = {
  wide: {
    title: { left: 120, top: 84, size: 64 }, sub: { top: 172, size: 26, width: 1100 },
    canvas: { left: 60, top: 150, w: 1120, h: 800 }, room: { S: 84, OX: 560, OY: 330, dot: 2.6 },
    list: { right: 120, top: 250, width: 600, row: 74, size: 26, head: 22, bar: 150 },
    steps: { left: 120, bottom: 96, size: 26, gap: 56, dot: 46 },
    stat: { right: 120, bottom: 90, size: 64, note: 22 },
  },
  tall: {
    title: { left: 40, top: 40, size: 50 }, sub: { top: 104, size: 26, width: 560 },
    canvas: { left: 0, top: 190, w: 640, h: 500 }, room: { S: 41, OX: 320, OY: 150, dot: 1.8 },
    list: { left: 40, top: 610, width: 560, row: 56, size: 26, head: 20, bar: 110 },
    steps: { left: 40, bottom: 40, size: 22, gap: 22, dot: 36 },
    stat: { left: 40, bottom: 160, size: 50, note: 20 },
  },
};

export function mount(stage, layout = 'wide') {
  const c = L[layout];
  const { w: W0, h: H0 } = layouts[layout];
  Object.assign(stage.style, { position: 'relative', width: `${W0}px`, height: `${H0}px`, overflow: 'hidden',
    background: 'var(--color-canvas)', color: 'var(--color-on-chrome)', fontFamily: 'var(--font-sans)' });
  const disp = { fontFamily: 'var(--font-display)', fontWeight: '600', letterSpacing: '0.01em', lineHeight: '1', margin: '0' };

  const head = el(stage, 'div', { position: 'absolute', left: `${c.title.left}px`, top: `${c.title.top}px` });
  el(head, 'p', { ...disp, fontSize: `${c.title.size}px` }, 'From scan to material list');
  el(head, 'p', { margin: '0', position: 'absolute', top: `${c.sub.top - c.title.top}px`, width: `${c.sub.width}px`,
    fontSize: `${c.sub.size}px`, lineHeight: '1.3', color: 'var(--color-on-chrome-muted)' },
    'One walk-through with an iPhone or iPad. The AI does the sorting.');

  const canvas = el(stage, 'canvas', { position: 'absolute', left: `${c.canvas.left}px`, top: `${c.canvas.top}px`,
    width: `${c.canvas.w}px`, height: `${c.canvas.h}px` });
  canvas.width = c.canvas.w;
  canvas.height = c.canvas.h;

  const list = el(stage, 'div', { position: 'absolute', top: `${c.list.top}px`, width: `${c.list.width}px`,
    ...(c.list.right != null ? { right: `${c.list.right}px` } : { left: `${c.list.left}px` }) });
  const listHead = el(list, 'p', { margin: '0 0 14px', fontSize: `${c.list.head}px`, fontWeight: '600',
    letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--color-on-chrome-muted)' }, 'Material list');
  const rows = ROWS.map(([cls, name, q, t]) => {
    const r = el(list, 'div', { display: 'grid', gridTemplateColumns: `22px 1fr ${c.list.bar}px ${Math.round(c.list.size * 4.4)}px`, alignItems: 'center',
      gap: '16px', height: `${c.list.row}px`, borderTop: '1px solid var(--color-chrome-border)', fontSize: `${c.list.size}px` });
    el(r, 'span', { width: '22px', height: '22px', borderRadius: '4px', background: `var(--viz-${cls})` });
    el(r, 'span', {}, name);
    const bar = el(r, 'span', { height: '10px', width: `${q * c.list.bar}px`, borderRadius: '5px', justifySelf: 'start',
      background: 'var(--color-on-chrome-muted)', opacity: '0.55', transformOrigin: 'left' });
    el(r, 'span', { justifySelf: 'end', fontSize: `${Math.round(c.list.size * 0.74)}px`, fontWeight: '600',
      padding: '5px 14px', borderRadius: '999px',
      background: t === 'Reuse' ? 'var(--color-accent)' : 'var(--color-chrome-raised)',
      color: t === 'Reuse' ? 'var(--color-on-accent)' : 'var(--color-on-chrome)' }, t);
    return { r, bar };
  });

  const steps = el(stage, 'div', { position: 'absolute', left: `${c.steps.left}px`, bottom: `${c.steps.bottom}px`,
    display: 'flex', flexWrap: 'wrap', gap: `14px ${c.steps.gap}px`, right: `${c.steps.left}px` });
  const stepEls = ['Scan', 'AI labels every point', 'Structured inventory'].map((label, i) => {
    const s = el(steps, 'div', { display: 'flex', alignItems: 'center', gap: '14px', fontSize: `${c.steps.size}px`,
      color: 'var(--color-on-chrome-muted)' });
    const dot = el(s, 'span', { width: `${c.steps.dot}px`, height: `${c.steps.dot}px`, borderRadius: '50%',
      display: 'grid', placeItems: 'center', border: '2px solid currentColor', boxSizing: 'border-box',
      fontFamily: 'var(--font-display)', fontSize: `${Math.round(c.steps.dot * 0.48)}px` }, String(i + 1));
    el(s, 'span', {}, label);
    return { s, dot };
  });

  const stat = el(stage, 'div', { position: 'absolute', bottom: `${c.stat.bottom}px`,
    ...(c.stat.right != null ? { right: `${c.stat.right}px`, textAlign: 'right' } : { left: `${c.stat.left}px` }) });
  el(stat, 'p', { ...disp, fontSize: `${c.stat.size}px` }, '≈ 1,700 m² · 30 min');
  el(stat, 'p', { margin: '6px 0 0', fontSize: `${c.stat.note}px`, color: 'var(--color-on-chrome-muted)' },
    'documented on a real survey');

  // ---- the scene: an isometric room as labelled surface samples
  const rand = seeded(42);
  const pts = [];
  const surf = (cls, n, f) => { for (let i = 0; i < n; i++) { const p = f(rand(), rand()); if (!p) continue; p.cls = cls; p.k = rand(); pts.push(p); } };
  const W = 7, D = 5, H = 3;
  surf('floor', 5200, (u, v) => ({ x: u * W, y: v * D, z: 0 }));
  surf('wall', 4600, (u, v) => { const x = u * W, z = v * H; return x > 2.2 && x < 4.8 && z > 1 && z < 2.3 ? null : { x, y: 0, z }; });
  surf('window', 900, (u, v) => ({ x: 2.2 + u * 2.6, y: 0.02, z: 1 + v * 1.3 }));
  surf('radiator', 500, (u, v) => ({ x: 2.4 + u * 2.2, y: 0.12, z: 0.2 + v * 0.5 }));
  surf('wall', 3700, (u, v) => { const y = u * D, z = v * H; return y > 1.4 && y < 2.4 && z < 2.1 ? null : { x: 0, y, z }; });
  surf('door', 650, (u, v) => ({ x: 0.03, y: 1.4 + u * 1.0, z: v * 2.1 }));
  surf('table', 900, (u, v) => ({ x: 3.6 + u * 1.8, y: 2.2 + v * 1.1, z: 0.75 }));
  for (const [lx, ly] of [[3.7, 2.3], [5.3, 2.3], [3.7, 3.2], [5.3, 3.2]])
    surf('table', 70, (u, v) => ({ x: lx + u * 0.08, y: ly + v * 0.08, z: u * 0.75 }));
  const { S, OX, OY, dot } = c.room;
  const C30 = Math.cos(Math.PI / 6);
  for (const p of pts) {
    p.sx = OX + (p.x - p.y) * C30 * S;
    p.sy = OY + (p.x + p.y) * 0.5 * S - p.z * S;
    p.sweep = (p.x + p.y) / (W + D);
  }

  const ctx = canvas.getContext('2d');
  let colours = null;
  const readColours = () => {
    colours = { scan: rgb(token(stage, '--viz-scan')) };
    for (const k of CLASSES) colours[k] = rgb(token(stage, `--viz-${k}`));
  };

  return function renderAt(t) {
    t = ((t % duration) + duration) % duration;
    if (!colours || stage.dataset.themeStale) { readColours(); delete stage.dataset.themeStale; }
    // Sharp at any scale: draw at the canvas's real pixel size.
    const k = canvas.width / c.canvas.w;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.setTransform(k, 0, 0, k, 0, 0);
    const out = ease((t - 11.2) / 0.8);            // fade out → loop
    const scan = clamp((t - 0.6) / 3.2);            // 0.6–3.8 s: points appear in a sweep
    const label = (t - 4.2) / 2.4;                  // 4.2–6.6 s: colour by class
    for (const p of pts) {
      const a = ease((scan * 1.25 - p.sweep) * 6);
      if (a <= 0) continue;
      const [r, g, b] = mix(colours.scan, colours[p.cls], ease(label * 1.4 - p.k * 0.4));
      ctx.fillStyle = `rgba(${r},${g},${b},${a * (1 - out) * 0.9})`;
      ctx.fillRect(p.sx, p.sy, dot, dot);
    }
    rows.forEach(({ r, bar }, i) => {
      show(r, ease((t - 7 - i * 0.35) / 0.6) * (1 - out), 40, 0);
      bar.style.transform = `scaleX(${ease((t - 7.3 - i * 0.35) / 0.8)})`;
    });
    listHead.style.opacity = String(ease((t - 6.7) / 0.5) * (1 - out));
    const step = t < 4 ? 0 : t < 7 ? 1 : 2;
    stepEls.forEach(({ s, dot }, i) => {
      const on = i === step && out < 0.5;
      s.style.color = on ? 'var(--color-on-chrome)' : 'var(--color-on-chrome-muted)';
      Object.assign(dot.style, on
        ? { background: 'var(--color-accent)', borderColor: 'var(--color-accent)', color: 'var(--color-on-accent)' }
        : { background: 'transparent', borderColor: 'currentColor', color: 'inherit' });
    });
    head.style.opacity = String(1 - out);
    stat.style.opacity = String(ease((t - 8.6) / 0.8) * (1 - out));
  };
}

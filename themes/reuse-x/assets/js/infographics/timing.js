// Infographic "timing": the transform-or-demolish decision comes first, the
// data usually last. From the public deck ("Too late", "New build wins by
// default"). 10 s loop, on the page surface — follows the site theme.
// Wide: horizontal timeline. Tall (phones): vertical timeline.
import { brand, ease, el, show } from './lib.js';

export const duration = 10;
export const still = 8.5;
export const layouts = { wide: { w: 1920, h: 1080 }, tall: { w: 640, h: 1180 } };

const PHASES = ['Idea & brief', 'Feasibility', 'Design', 'Tender', 'Demolition'];
const DEC = 0.4, EARLY = 0.14, LATE = 0.9;

export function mount(stage, layout = 'wide') {
  const tall = layout === 'tall';
  const { w: SW, h: SH } = layouts[layout];
  Object.assign(stage.style, { position: 'relative', width: `${SW}px`, height: `${SH}px`, overflow: 'hidden',
    background: 'var(--color-surface)', color: 'var(--color-text)', fontFamily: 'var(--font-sans)' });
  const disp = { fontFamily: 'var(--font-display)', fontWeight: '600', letterSpacing: '0.01em', lineHeight: '1.05', margin: '0' };
  const pad = tall ? 40 : 120;

  const title = el(stage, 'p', { ...disp, position: 'absolute', left: `${pad}px`, top: `${tall ? 40 : 90}px`,
    width: `${SW - 2 * pad}px`, fontSize: `${tall ? 46 : 64}px` },
    'The decision comes first. The data usually comes last.');
  const sub = el(stage, 'p', { margin: '0', position: 'absolute', left: `${pad}px`, top: `${tall ? 156 : 176}px`,
    width: `${SW - 2 * pad}px`, fontSize: '26px', lineHeight: '1.35', color: 'var(--color-text-muted)' },
    'Transform or demolish is settled early. A manual resource survey arrives when it can no longer change it.');

  // Timeline geometry: position f ∈ [0, 1] → stage px along the track.
  const T = tall ? { x: 250, y0: 340, y1: 1110 } : { y: 520, x0: 120, x1: 1800 };
  const at = (f) => (tall ? T.y0 + (T.y1 - T.y0) * f : T.x0 + (T.x1 - T.x0) * f);

  const track = el(stage, 'div', tall
    ? { position: 'absolute', left: `${T.x - 3}px`, top: `${T.y0}px`, width: '6px', height: `${T.y1 - T.y0}px`, transformOrigin: 'top' }
    : { position: 'absolute', left: `${T.x0}px`, top: `${T.y - 3}px`, width: `${T.x1 - T.x0}px`, height: '6px', transformOrigin: 'left' });
  Object.assign(track.style, { borderRadius: '3px', background: 'var(--color-border-strong)' });

  const phases = PHASES.map((name, i) => {
    const f = i / (PHASES.length - 1);
    const p = el(stage, 'div', { position: 'absolute', fontSize: '24px', color: 'var(--color-text-muted)', whiteSpace: 'nowrap' });
    const dot = el(stage, 'span', { position: 'absolute', width: '20px', height: '20px', borderRadius: '50%', boxSizing: 'border-box',
      background: 'var(--color-surface)', border: '4px solid var(--color-border-strong)' });
    if (tall) {
      Object.assign(p.style, { right: `${SW - T.x + 30}px`, top: `${at(f) - 15}px`, textAlign: 'right' });
      Object.assign(dot.style, { left: `${T.x - 10}px`, top: `${at(f) - 10}px` });
    } else {
      Object.assign(p.style, { left: `${at(f)}px`, top: `${T.y + 28}px`, transform: 'translateX(-50%)' });
      Object.assign(dot.style, { left: `${at(f) - 10}px`, top: `${T.y - 10}px` });
    }
    p.textContent = name;
    return [p, dot];
  });

  // The decision: a mark across the track.
  const dec = el(stage, 'div', tall
    ? { position: 'absolute', left: `${T.x - 40}px`, top: `${at(DEC) - 2}px`, width: `${SW - pad - T.x + 40}px`, height: '4px', transformOrigin: 'left' }
    : { position: 'absolute', left: `${at(DEC) - 2}px`, top: '300px', width: '4px', height: `${T.y - 300 + 70}px`, transformOrigin: 'bottom' });
  dec.style.background = 'var(--color-text)';
  const decLabel = el(stage, 'p', { ...disp, position: 'absolute', fontSize: `${tall ? 30 : 34}px`, whiteSpace: 'nowrap' },
    'Transform or demolish?');
  Object.assign(decLabel.style, tall
    ? { left: `${T.x + 30}px`, top: `${at(DEC) + 16}px` }
    : { left: `${at(DEC)}px`, top: '252px', transform: 'translateX(-50%)' });

  const card = (f, kind, head, body) => {
    const colour = kind === 'early' ? 'var(--color-accent)' : 'var(--color-status-failed)';
    const pin = el(stage, 'span', { position: 'absolute', width: '30px', height: '30px', borderRadius: '50%', background: colour });
    const stem = el(stage, 'span', { position: 'absolute', background: colour });
    const box = el(stage, 'div', { position: 'absolute', padding: '24px 28px', borderRadius: '10px', boxSizing: 'border-box',
      fontSize: '24px', lineHeight: '1.35', background: 'var(--color-surface-raised)', boxShadow: 'var(--shadow-md)',
      border: kind === 'early' ? '2px solid var(--color-accent)' : '1px solid var(--color-border)' },
      `<p style="margin:0 0 8px;font-family:var(--font-display);font-weight:600;font-size:32px;line-height:1.1;color:${colour}">${head}</p>${body}`);
    if (tall) {
      Object.assign(pin.style, { left: `${T.x - 15}px`, top: `${at(f) - 15}px` });
      Object.assign(stem.style, { left: `${T.x + 15}px`, top: `${at(f) - 1.5}px`, width: '25px', height: '3px', transformOrigin: 'left' });
      Object.assign(box.style, { left: `${T.x + 40}px`, width: `${SW - pad - T.x - 40}px`,
        top: kind === 'early' ? `${at(f) - 60}px` : 'auto', bottom: kind === 'late' ? `${SH - at(f) - 60}px` : 'auto' });
    } else {
      Object.assign(pin.style, { left: `${at(f) - 15}px`, top: `${T.y - 15}px` });
      Object.assign(stem.style, { left: `${at(f) - 1.5}px`, top: `${T.y + 15}px`, width: '3px', height: '150px', transformOrigin: 'top' });
      Object.assign(box.style, { top: '690px', width: '520px',
        left: kind === 'early' ? `${at(f) - 30}px` : `${at(f) - 520 + 30}px` });
    }
    return { pin, stem, box };
  };
  const late = card(LATE, 'late', 'Manual survey: too late',
    'Costly, specialist work — done just before demolition, when only sorting is left to decide.');
  const early = card(EARLY, 'early', `${brand}: before the decision`,
    'A 30-minute scan gives a material list while reuse is still an option.');

  const grow = (node, f) => { node.style.transform = tall ? `scaleY(${f})` : `scaleX(${f})`; };
  return function renderAt(t) {
    t = ((t % duration) + duration) % duration;
    const k = 1 - ease((t - 9.2) / 0.8);
    title.style.opacity = sub.style.opacity = String(ease(t / 0.6) * k);
    grow(track, ease((t - 0.3) / 1.4)); track.style.opacity = String(k);
    phases.forEach(([p, dot], i) => { const f = ease((t - 0.5 - i * 0.2) / 0.5) * k; p.style.opacity = dot.style.opacity = String(f); });
    const d = ease((t - 1.8) / 0.7) * k;
    dec.style.opacity = decLabel.style.opacity = String(d);
    dec.style.transform = tall ? `scaleX(${d})` : `scaleY(${d})`;
    const sideways = tall ? [30, 0] : [0, 24];
    for (const [c, t0] of [[late, 2.8], [early, 5.2]]) {
      const f = ease((t - t0) / 0.6) * k;
      c.pin.style.opacity = String(f);
      c.stem.style.transform = tall ? `scaleX(${f})` : `scaleY(${f})`;
      show(c.box, ease((t - t0 - 0.4) / 0.6) * k, ...sideways);
    }
    // The late path greys out once the early one is there.
    late.box.style.opacity = String(ease((t - 3.2) / 0.6) * k * (1 - 0.55 * ease((t - 6.8) / 0.8)));
  };
}

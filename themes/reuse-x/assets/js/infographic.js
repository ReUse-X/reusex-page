// Native infographics: <div data-infographic="timing"> → the module in
// ./infographics/ drawn into a fixed stage, scaled to the box (crisp text and
// canvas at any size), tall layout on narrow boxes, played while in view,
// redrawn when the theme changes. Reduced motion: the complete still frame.
// Without JS the element shows its poster image.
import * as pipeline from './infographics/pipeline.js';
import * as timing from './infographics/timing.js';

const REGISTRY = { pipeline, timing };
const TALL_BELOW = 640; // box width (CSS px) under which the tall layout is used

export function initInfographics() {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  for (const host of document.querySelectorAll('[data-infographic]')) {
    const mod = REGISTRY[host.dataset.infographic];
    if (!mod) continue;
    let stage = null, render = null, layout = null, raf = 0, playing = false, t0 = 0;
    let now = reduce ? mod.still : 0;

    const build = () => {
      const width = host.clientWidth;
      if (!width) return;
      const want = width < TALL_BELOW ? 'tall' : 'wide';
      if (want !== layout) {
        host.querySelector('.infographic__fallback')?.remove();
        stage?.remove();
        stage = document.createElement('div');
        stage.setAttribute('aria-hidden', 'true');
        host.appendChild(stage);
        render = mod.mount(stage, want);
        layout = want;
      }
      const { w, h } = mod.layouts[layout];
      const scale = width / w;
      host.style.aspectRatio = `${w} / ${h}`;
      Object.assign(stage.style, { position: 'absolute', left: '0', top: '0', transformOrigin: '0 0', transform: `scale(${scale})` });
      const dpr = window.devicePixelRatio || 1;
      for (const c of stage.querySelectorAll('canvas')) {
        c.width = Math.round(parseFloat(c.style.width) * scale * dpr);
        c.height = Math.round(parseFloat(c.style.height) * scale * dpr);
      }
      render(now);
    };

    const loop = (ts) => {
      now = ((ts - t0) / 1000) % mod.duration;
      render(now);
      raf = requestAnimationFrame(loop);
    };
    const play = (on) => {
      if (on === playing || reduce) return;
      playing = on;
      if (on) { t0 = performance.now() - now * 1000; raf = requestAnimationFrame(loop); }
      else cancelAnimationFrame(raf);
    };

    new ResizeObserver(build).observe(host);
    new IntersectionObserver(([e]) => play(e.isIntersecting), { threshold: 0.25 }).observe(host);
    new MutationObserver(() => { if (stage) { stage.dataset.themeStale = '1'; render?.(now); } })
      .observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    build();
  }
}

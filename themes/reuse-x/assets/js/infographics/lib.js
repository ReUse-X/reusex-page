// Shared helpers for infographics (themes/reuse-x/assets/js/infographics/).
//
// An infographic module exports:
//   duration   loop length in seconds (state at duration === state at 0)
//   still      t (s) of the most complete frame — reduced motion, posters
//   layouts    { wide: {w, h}, tall: {w, h} } stage sizes in stage px
//   mount(stage, layoutName) → renderAt(t)   build the DOM, return a pure
//                                            function of t that draws it
// The same module runs on the site (infographic.js scales the stage to its
// box, plays it in view, follows the theme) and in render.py (frame-exact
// video via media/infographics/<id>.html). Colours are tokens only.

export const clamp = (x) => Math.max(0, Math.min(1, x));
export const ease = (x) => (x <= 0 ? 0 : x >= 1 ? 1 : 0.5 - 0.5 * Math.cos(Math.PI * x));

/** Deterministic random numbers (same picture on every run). */
export function seeded(seed) {
  let s = seed;
  return () => (s = (s * 16807) % 2147483647) / 2147483647;
}

/** Create an element with inline style (stage px) and optional text/HTML. */
export function el(parent, tag, style = {}, html = '') {
  const e = document.createElement(tag);
  Object.assign(e.style, style);
  if (html) e.innerHTML = html;
  parent.appendChild(e);
  return e;
}

/** Read a token's current value (follows the theme). */
export function token(node, name) {
  return getComputedStyle(node).getPropertyValue(name).trim();
}

/** '#rrggbb' or 'rgb(r g b)' → [r, g, b]. */
export function rgb(colour) {
  if (colour.startsWith('#')) {
    const h = colour.length === 4 ? colour.replace(/#(.)(.)(.)/, '#$1$1$2$2$3$3') : colour;
    return [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
  }
  const m = colour.match(/[\d.]+/g) || ['0', '0', '0'];
  return m.slice(0, 3).map(Number);
}

export const mix = (a, b, f) => a.map((v, i) => Math.round(v + (b[i] - v) * f));

/** Fade + slide a node in: f = 0 hidden … 1 shown. */
export function show(node, f, dx = 0, dy = 0) {
  node.style.opacity = String(f);
  node.style.transform = `translate(${(1 - f) * dx}px, ${(1 - f) * dy}px)`;
}

/** The brand name, never one uppercase word. */
export const brand = 'ReUse<span style="color:var(--color-accent);margin-left:.06em">X</span>';

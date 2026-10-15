// Deck (layout: deck): one slide at a time, keyboard / buttons / dots /
// swipe, deep links (#slide-3), fullscreen, and scale-to-fit (CSS zoom) of
// the fixed 1000×562.5 slide canvas on wide screens. Without JS all slides
// show in order.
const DESIGN_W = 1000;
const DESIGN_H = 562.5;

export function initDeck() {
  const deck = document.querySelector('[data-deck]');
  if (!deck) return;
  const slides = [...deck.querySelectorAll('.slide')];
  const total = slides.length;
  if (!total) return;
  const controls = deck.querySelector('.deck__controls');
  const dots = deck.querySelector('[data-deck-dots]');
  const counter = deck.querySelector('[data-deck-counter]');
  let current = 1;

  deck.classList.add('deck--active');
  controls.hidden = false;
  slides.forEach((_, i) => {
    const li = document.createElement('li');
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'deck__dot';
    b.setAttribute('aria-label', `${i + 1} / ${total}`);
    b.addEventListener('click', () => show(i + 1));
    li.append(b);
    dots.append(li);
  });

  function fit() {
    const stage = deck.querySelector('.deck__stage');
    const scale = Math.min(stage.clientWidth / DESIGN_W, stage.clientHeight / DESIGN_H);
    deck.style.setProperty('--deck-scale', String(scale));
    fitContent(slides[current - 1]);
  }

  // Too much content for the fixed canvas: shrink it (down to MIN_FIT)
  // instead of clipping. Below that the slide should be split.
  const MIN_FIT = 0.75;
  function fitContent(slide) {
    const canvas = slide?.querySelector('.slide__canvas');
    const content = slide?.querySelector('.slide__content');
    if (!canvas || !content) return;
    content.style.zoom = '';
    if (!matchMedia('(min-width: 60rem)').matches) return; // phones: natural height
    const room = canvas.clientHeight - parseFloat(getComputedStyle(canvas).paddingTop) * 2;
    const need = content.scrollHeight;
    if (need > room) {
      const z = Math.max(MIN_FIT, room / need);
      content.style.zoom = String(z);
      if (room / need < MIN_FIT) console.warn(`deck: slide ${current} has too much content even at ${MIN_FIT} — split it`);
    }
  }

  function show(n, push = true) {
    current = Math.min(Math.max(1, n), total);
    slides.forEach((s, i) => { s.hidden = i + 1 !== current; });
    dots.querySelectorAll('.deck__dot').forEach((d, i) => d.toggleAttribute('aria-current', i + 1 === current));
    counter.textContent = `${current} / ${total}`;
    deck.querySelector('[data-deck-prev]').disabled = current === 1;
    deck.querySelector('[data-deck-next]').disabled = current === total;
    if (push) history.replaceState(null, '', `#slide-${current}`);
    fit();
  }
  window.goToSlide = (n) => show(n);
  window.nextSlide = () => show(current + 1);
  window.prevSlide = () => show(current - 1);

  deck.querySelector('[data-deck-prev]').addEventListener('click', () => show(current - 1));
  deck.querySelector('[data-deck-next]').addEventListener('click', () => show(current + 1));
  deck.querySelector('[data-deck-fullscreen]').addEventListener('click', () => {
    if (document.fullscreenElement) document.exitFullscreen();
    else deck.requestFullscreen?.();
  });
  document.addEventListener('fullscreenchange', fit);
  document.addEventListener('keydown', (e) => {
    if (e.target.closest('input, textarea, select')) return;
    const keys = { ArrowRight: 1, PageDown: 1, ' ': 1, ArrowLeft: -1, PageUp: -1 };
    if (e.key in keys) { e.preventDefault(); show(current + keys[e.key]); }
    if (e.key === 'Home') { e.preventDefault(); show(1); }
    if (e.key === 'End') { e.preventDefault(); show(total); }
  });
  let x0 = null;
  deck.addEventListener('touchstart', (e) => { x0 = e.changedTouches[0].clientX; }, { passive: true });
  deck.addEventListener('touchend', (e) => {
    if (x0 === null) return;
    const dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 50) show(current + (dx < 0 ? 1 : -1));
    x0 = null;
  }, { passive: true });
  addEventListener('resize', fit);
  addEventListener('hashchange', () => show(parseInt(location.hash.replace('#slide-', ''), 10) || 1, false));

  show(parseInt(location.hash.replace('#slide-', ''), 10) || 1, false);
}

// Silent looping clips: respect reduced motion (pause, show controls).
export function initVideo() {
  if (!matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  for (const v of document.querySelectorAll('video[data-clip]')) {
    v.pause();
    v.removeAttribute('autoplay');
    v.controls = true;
  }
}

// Silent looping clips: respect reduced motion. A clip pauses and gets
// controls; an ambient loop (data-clip="ambient", decorative hero visuals)
// just stops on its first frame / poster.
export function initVideo() {
  if (!matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  for (const v of document.querySelectorAll('video[data-clip]')) {
    v.pause();
    v.removeAttribute('autoplay');
    if (v.dataset.clip !== 'ambient') v.controls = true;
  }
}

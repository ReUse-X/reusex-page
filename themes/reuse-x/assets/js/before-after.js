// before-after slider: a native range input drives a CSS variable that
// clips the "after" picture. The input gives keyboard + touch for free.
export function initBeforeAfter() {
  for (const el of document.querySelectorAll('[data-before-after]')) {
    const range = el.querySelector('.before-after__range');
    if (!range) continue;
    el.classList.add('before-after--active');
    range.hidden = false;
    const set = () => el.style.setProperty('--before-after-pos', `${range.value}%`);
    range.addEventListener('input', set);
    set();
  }
}

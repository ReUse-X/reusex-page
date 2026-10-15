// Theme toggle. Same storage key and values as the app (reusex-theme =
// light | dark | system); the pre-paint snippet in head.html applies the
// stored choice before first paint, this module only handles the button.
const KEY = 'reusex-theme';

function apply(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  try { localStorage.setItem(KEY, theme); } catch (e) { /* private mode */ }
}

export function initTheme() {
  for (const button of document.querySelectorAll('[data-theme-toggle]')) {
    button.addEventListener('click', () => {
      const dark = document.documentElement.getAttribute('data-theme') === 'dark';
      apply(dark ? 'light' : 'dark');
    });
  }
}

// Mobile menu: the toggle opens the nav as a full-screen sheet below the
// header. Escape and following a link close it.
export function initMenu() {
  const header = document.querySelector('.site-header');
  const toggle = header?.querySelector('[data-menu-toggle]');
  if (!toggle) return;
  const openLabel = toggle.getAttribute('aria-label');
  const closeLabel = toggle.dataset.labelClose;

  const set = (open) => {
    header.toggleAttribute('data-menu-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? closeLabel : openLabel);
    document.body.style.overflow = open ? 'hidden' : '';
  };

  toggle.addEventListener('click', () => set(!header.hasAttribute('data-menu-open')));
  header.querySelectorAll('.site-nav a').forEach((a) => a.addEventListener('click', () => set(false)));
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && header.hasAttribute('data-menu-open')) { set(false); toggle.focus(); }
  });
}

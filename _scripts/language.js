// Real links work without JavaScript. Enhance them with filters and a saved choice.
window.addEventListener('DOMContentLoaded', () => {
  const root = document.documentElement;
  const locale = root.dataset.locale || 'en';
  for (const link of document.querySelectorAll('[data-language-switch]')) {
    const target = new URL(link.href, window.location.href);
    target.search = window.location.search;
    target.hash = window.location.hash;
    link.href = target.href;
    link.addEventListener('click', () => {
      const current = new URL(window.location.href);
      const destination = new URL(link.href);
      destination.search = current.search;
      destination.hash = current.hash;
      link.href = destination.href;
      try { localStorage.setItem('lab-language', link.dataset.targetLocale); }
      catch (_) { /* Language links also work when storage is unavailable. */ }
    });
  }
  // Only revisit the chosen language on the home page; explicit deep links stay valid.
  try {
    if (locale === 'en' && window.location.pathname === root.dataset.home &&
        localStorage.getItem('lab-language') === 'zh') {
      const target = new URL(root.dataset.chineseHome, window.location.href);
      target.search = window.location.search;
      target.hash = window.location.hash;
      window.location.replace(target.href);
    }
  } catch (_) { /* Storage access is optional. */ }
});

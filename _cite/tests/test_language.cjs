// Exercise the actual language switch with deep links, changing filters and blocked storage.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../../_scripts/language.js'), 'utf8');
function page(url, locale, saved, blocked = false, base = '') {
  const events = {}, clicks = {};
  const link = { href: `https://lab.test${base}${locale === 'zh' ? '/research/' : '/zh/research/'}`,
    dataset: { targetLocale: locale === 'zh' ? 'en' : 'zh' },
    addEventListener: (name, callback) => { clicks[name] = callback; } };
  let replaced, stored;
  const window = { location: { ...Object.fromEntries(['href','pathname','search','hash'].map(k => [k, new URL(url)[k]])),
    replace: value => { replaced = value; } }, addEventListener: (name, cb) => { events[name] = cb; } };
  const document = { documentElement: { dataset: { locale, home: `${base}/`, chineseHome: `${base}/zh/` } },
    querySelectorAll: () => [link] };
  const localStorage = {
    getItem() { if (blocked) throw Error('blocked'); return saved; },
    setItem(_, value) { if (blocked) throw Error('blocked'); stored = value; },
  };
  vm.runInNewContext(source, { window, document, localStorage, URL });
  events.DOMContentLoaded();
  return { link, window, clicks, replaced: () => replaced, stored: () => stored };
}
const member = page('https://lab.test/zh/research/?orcid=0009-0005-8355-0183#2026', 'zh');
assert.equal(member.link.href, 'https://lab.test/research/?orcid=0009-0005-8355-0183#2026');
member.window.location.href = 'https://lab.test/zh/research/?orcid=0009-0005-8355-0183&search=control#2025';
member.clicks.click();
assert.equal(member.link.href, 'https://lab.test/research/?orcid=0009-0005-8355-0183&search=control#2025');
assert.equal(member.stored(), 'en');
const home = page('https://lab.test/preview/?search=control#highlights', 'en', 'zh', false, '/preview');
assert.equal(home.replaced(), 'https://lab.test/preview/zh/?search=control#highlights');
assert.equal(page('https://lab.test/research/', 'en', 'zh').replaced(), undefined, 'Explicit English deep links remain English');
const blocked = page('https://lab.test/zh/research/?search=planning', 'zh', null, true);
assert.doesNotThrow(() => blocked.clicks.click());
assert.equal(blocked.link.href, 'https://lab.test/research/?search=planning');
console.log('Language links, live filters, saved choice, base URL and blocked-storage checks passed');

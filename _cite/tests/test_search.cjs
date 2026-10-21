// Exercise the real browser search script without a browser or dependencies.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function createPage(query) {
  const orcid = '0000-0001-5121-2677';
  const other = '0000-0002-1825-0097';
  const cards = [
    { text: 'Ze Wang adaptive control', orcids: orcid },
    { text: 'Ze Wang adaptive control', orcids: other },
    { text: 'Shared robotics paper', orcids: `${other} ${orcid}` },
    { text: `Unrelated mention of ${orcid}`, orcids: '' },
  ].map(({ text, orcids }) => ({ innerText: text, dataset: { orcids }, style: {}, querySelectorAll: () => [] }));
  const input = { value: '' }, button = { disabled: true }, icon = {};
  const box = { querySelector: (selector) => ({ input, button, 'button i': icon }[selector]) };
  const info = { style: {}, innerHTML: '' };
  const events = {};
  const window = {
    location: new URL(`http://localhost:4000/research/${query}`),
    addEventListener: (name, callback) => { events[name] = callback; },
    setTimeout: (callback) => { callback(); return 1; },
    clearTimeout: () => {},
  };
  window.history = { replaceState: (_, __, url) => { window.location = new URL(url); } };
  const document = { querySelectorAll: (selector) => ({
    '.card, .citation:not([data-search-exclude]), .post-excerpt': cards,
    '.search-box': [box], '.search-info': [info], '.tag': [],
  }[selector] || []) };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../../_scripts/search.js'), 'utf8'),
                     { window, document, URL, URLSearchParams });
  events.load();
  return { window, cards, button, info, visible: () => cards.flatMap((card, i) => card.style.display === 'none' ? [] : [i]) };
}

const page = createPage('?orcid=0000-0001-5121-2677');
assert.deepEqual(page.visible(), [0, 2], 'Exact membership, not text or author name, selects papers');
assert.equal(page.button.disabled, false, 'ORCID filter can be cleared even with an empty search box');
assert.match(page.info.innerHTML, /ORCID/);
assert.match(page.info.innerHTML, /Showing 2 of 4 results/, 'Highlight cards do not inflate the result count');
page.window.onSearchInput({ value: 'control' });
assert.deepEqual(page.visible(), [0], 'Keyword search narrows the selected member papers');
assert.equal(page.window.location.searchParams.get('orcid'), '0000-0001-5121-2677');
page.window.onSearchClear();
assert.deepEqual(page.visible(), [0, 1, 2, 3]);
assert.equal(page.window.location.searchParams.has('orcid'), false);
assert.equal(page.window.location.searchParams.has('search'), false);
assert.equal(page.button.disabled, true);
assert.deepEqual(createPage('?search=control').visible(), [0, 1], 'Ordinary text search still works');
assert.deepEqual(createPage('?orcid=0000-0001-5121-267').visible(), [], 'Partial ORCID cannot match');
console.log('ORCID search, shared papers, keyword narrowing and clear-filter checks passed');

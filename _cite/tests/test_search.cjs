// Exercise the real browser search script without a browser or dependencies.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function createPage(query, chinese = false) {
  const orcid = '0000-0001-5121-2677';
  const other = '0000-0002-1825-0097';
  const tags = [0, 1, 2, 3].map((_, i) => ({
    innerText: chinese ? (i < 2 ? '控制' : '机器人') : (i < 2 ? 'control' : 'robotics'),
    dataset: { searchTag: i < 2 ? 'control' : 'robotics' },
    setAttribute(name) { this[name] = true; },
    removeAttribute(name) { delete this[name]; },
  }));
  const cards = [
    { text: 'Ze Wang adaptive control', orcids: orcid },
    { text: 'Ze Wang adaptive control', orcids: other },
    { text: 'Shared robotics paper', orcids: `${other} ${orcid}` },
    { text: `Unrelated mention of ${orcid}`, orcids: '' },
  ].map(({ text, orcids }, i) => ({ innerText: text, dataset: { orcids }, style: {}, querySelectorAll: (selector) => selector === '.tag' ? [tags[i]] : [] }));
  const input = { value: '' }, button = { disabled: true }, icon = {};
  const box = { querySelector: (selector) => ({ input, button, 'button i': icon }[selector]) };
  const info = { style: {}, innerHTML: '', dataset: chinese ? {
    resultsTemplate: '共 __TOTAL__ 条记录，显示 __SHOWN__ 条结果',
    orcidLabel: '已按成员 ORCID 筛选', clearLabel: '清除筛选',
  } : {} };
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
    '.search-box': [box], '.search-info': [info], '.tag': tags,
  }[selector] || []) };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../../_scripts/search.js'), 'utf8'),
                     { window, document, URL, URLSearchParams, normalizeTag: (tag) => window.normalizeTag(tag) });
  events.load();
  return { window, cards, button, info, tags, visible: () => cards.flatMap((card, i) => card.style.display === 'none' ? [] : [i]) };
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

const chinese = createPage('?orcid=0000-0001-5121-2677&search=%22tag%3A+control%22', true);
assert.deepEqual(chinese.visible(), [0], 'Translated labels retain canonical tag filters and exact ORCID');
assert.match(chinese.info.innerHTML, /共 4 条记录，显示 1 条结果/);
assert.match(chinese.info.innerHTML, /已按成员 ORCID 筛选/);
assert.match(chinese.info.innerHTML, /清除筛选/);
assert.equal(chinese.tags[0]['data-active'], true, 'Chinese tag is highlighted for its canonical key');
console.log('Chinese result labels and canonical tag filtering passed');

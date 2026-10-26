"""Check rendered bilingual routes, shared data, publication membership and links.
Run after jekyll build; requires the existing PyYAML citation dependency.
"""
import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import yaml

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.elements, self.text = [], []
        self.feed(path.read_text())
    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))
    def handle_data(self, text):
        self.text.append(text)
    def select(self, tag=None, cls=None, **attrs):
        return [a for t, a in self.elements if (not tag or tag == t)
                and (not cls or cls in a.get('class', '').split())
                and all(a.get(k.replace('_', '-')) == v for k, v in attrs.items())]
    def visible_source(self):
        return ' '.join(self.text)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--site-dir', type=Path, default=Path('_site'))
    parser.add_argument('--baseurl', default='')
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[2]
    built = args.site_dir.resolve()
    base = args.baseurl.rstrip('/')
    def output(url):
        path = unquote(urlsplit(url).path)
        assert not base or path.startswith(base + '/'), (url, base)
        path = path[len(base):].lstrip('/')
        return built / (path + 'index.html' if not path or path.endswith('/') else path)
    def read(route):
        path = output(base + route)
        assert path.is_file(), f'Missing page: {route}'
        return Page(path)
    records = yaml.safe_load((source / '_data/citations.yaml').read_text())
    formal = [c for c in records if c.get('metadata_verified') is True and
              c.get('publication_type') in ('journal', 'conference', 'book-chapter', 'correction')]
    for route in ['/', '/team/', '/research/', '/projects/', '/contact/', '/blog/', '/404.html']:
        en, zh = read(route), read('/zh' + route)
        assert en.select('html')[0]['lang'] == 'en'
        assert zh.select('html')[0]['lang'] == 'zh-CN'
        for page, other, locale in [(en, '/zh' + route, 'en'), (zh, route, 'zh')]:
            switches = [a for t, a in page.elements if t == 'a' and 'data-language-switch' in a]
            assert len(switches) == 1 and switches[0]['href'] == base + other, (route, switches)
            alternate = page.select('link', rel='alternate', hreflang='zh-CN')
            assert len(alternate) == 1 and urlsplit(alternate[0]['href']).path == base + '/zh' + route
            assert len(page.select('link', rel='canonical')) == 1
            assert len([a for t,a in page.elements if t=='a' and a.get('data-tooltip') in (
                'Published works','Research themes and applications','About our team',
                'Lab news and research updates','Email and affiliation',
                '已发表论文与研究成果','研究主题与应用','认识课题组成员','课题组新闻与研究动态','邮箱与所属单位')]) == 5
    en_team, zh_team = read('/team/'), read('/zh/team/')
    assert len(en_team.select('a', 'portrait')) == len(zh_team.select('a', 'portrait')) == 11
    for member in source.glob('_members/*.md'):
        data = yaml.safe_load(member.read_text().split('---', 2)[1])
        slug = member.stem
        en, zh = read(f'/members/{slug}.html'), read(f'/zh/members/{slug}.html')
        assert data['name'] in en.visible_source()
        assert data['name_zh'] in zh.visible_source()
        assert zh.select('meta', name='title')[0]['content'] == data['name_zh']
        assert en.select('meta', name='title')[0]['content'] == data['name']
        assert data['description_zh'] in zh.visible_source()
        assert zh.select('html')[0]['lang'] == 'zh-CN'
        orcid = data.get('links', {}).get('orcid', '')
        expected = [r for r in formal if orcid and orcid in
                    (r.get('orcids', []) + ([r['orcid']] if r.get('orcid') else []))]
        en_citations, zh_citations = en.select('div','citation'), zh.select('div','citation')
        assert len(en_citations) == len(zh_citations) == len(expected), (slug, len(en_citations),len(zh_citations),len(expected))
        assert [a.get('data-orcids') for a in en_citations] == [a.get('data-orcids') for a in zh_citations]
        for page in (en,zh):
            assert not any('orcid.org' in a.get('href','') for a in page.select('a'))
            if data.get('ieee_ras_pin'):
                assert data['ieee_ras_pin'] not in page.visible_source()
        if orcid:
            assert zh.select('a', href=f'{base}/zh/research/?orcid={orcid}')
    for route in ['/research/', '/zh/research/']:
        assert len(read(route).select('div','citation')) == len(formal)
    for page in [en_team, zh_team, read('/'), read('/zh/'), read('/projects/'), read('/zh/projects/'), read('/blog/'), read('/zh/blog/')]:
        for tag, attr in [('a','href'),('img','src'),('script','src'),('link','href')]:
            for element in page.select(tag):
                url = element.get(attr,'')
                if url.startswith('/') and not url.startswith('//'):
                    assert output(url).is_file(), f'Broken internal {attr}: {url}'
    for post in source.glob('_posts/*.md'):
        data = yaml.safe_load(post.read_text().split('---',2)[1])
        year, month, day, slug = post.stem.split('-', 3)
        route = f'/zh/{year}/{month}/{day}/{slug}.html'
        page = read(route)
        assert data['title_zh'] in page.visible_source()
        assert not page.select('p', 'translation-notice')
        for a in page.select('a'):
            url = a.get('href', '')
            if url.startswith('/') and not url.startswith('//'):
                assert output(url).is_file(), f'Broken post navigation: {url}'
    assert read('/zh/testbed.html').select('p', 'translation-notice'), 'Missing translation uses explicit fallback'
    print(f'Bilingual pages, 11 Team members, 12 profiles, shared {len(formal)} publications, ORCID membership, assets and fallback passed (baseurl={base!r})')

if __name__ == '__main__':
    main()

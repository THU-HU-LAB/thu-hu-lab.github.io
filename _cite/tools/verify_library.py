"""Download public registry metadata and compare it with an exported paper list.

This first stage never changes the website library. Review the JSON/CSV output
before importing records. Uses only Python's standard library.
"""
import argparse
import csv
import hashlib
import html
import json
import re
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from difflib import SequenceMatcher
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote, urlencode, unquote
from urllib.request import Request, urlopen


def normalized_title(value):
    value = html.unescape(re.sub('<[^>]+>', '', str(value or '')))
    return ''.join(c for c in unicodedata.normalize('NFKC', value).lower() if c.isalnum())


def normalized_doi(value):
    value = unquote(str(value or '').strip())
    value = re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)', '', value, flags=re.I)
    return value.lower().strip()


def title_similarity(a, b):
    return SequenceMatcher(None, normalized_title(a), normalized_title(b)).ratio()


def hu_author(message):
    for a in message.get('author', []):
        family = normalized_title(a.get('family', ''))
        given = normalized_title(a.get('given', ''))
        names = {family, given, family + given, given + family}
        if names & {'chuxionghu', 'huchuxiong', 'andchuxionghu', '胡楚雄'}:
            return True
        if family == 'hu' and given in ('chuxiong', 'c', 'cx'):
            return True
        if '胡楚雄' in a.get('name', '') + a.get('given', '') + a.get('family', ''):
            return True
    return False


class Registry:
    def __init__(self, cache):
        self.cache = Path(cache)
        self.cache.mkdir(parents=True, exist_ok=True)

    def get(self, url):
        path = self.cache / (hashlib.sha256(url.encode()).hexdigest() + '.json')
        if path.exists():
            return json.loads(path.read_text())
        for attempt in range(3):
            try:
                request = Request(url, headers={'User-Agent': 'THU-HU-LAB bibliography verification/1.0', 'Accept': 'application/json'})
                with urlopen(request, timeout=25) as response:
                    data = json.load(response)
                path.write_text(json.dumps(data, ensure_ascii=False))
                return data
            except Exception as error:
                if isinstance(error, HTTPError) and error.code == 404:
                    raise
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)

    def crossref(self, doi):
        return self.get('https://api.crossref.org/works/' + quote(normalized_doi(doi), safe=''))['message']

    def search(self, title):
        query = urlencode({'query.bibliographic': title, 'rows': 3})
        return self.get('https://api.crossref.org/works?' + query)['message']['items']

    def author_works(self, author):
        works, cursor = [], '*'
        while cursor:
            params = urlencode({'filter': 'author.id:' + author, 'per-page': 200, 'cursor': cursor})
            data = self.get('https://api.openalex.org/works?' + params)
            works.extend(data['results'])
            cursor = data.get('meta', {}).get('next_cursor') if len(data['results']) == 200 else None
        return works


def verify_row(registry, row):
    result = {'excel_row': row['序号'], 'input': row, 'input_doi': normalized_doi(row.get('DOI'))}
    try:
        if result['input_doi']:
            candidates = [registry.crossref(result['input_doi'])]
        else:
            candidates = registry.search(row['论文标题'])
        candidates.sort(key=lambda m: title_similarity(row['论文标题'], ' '.join(m.get('title', []))), reverse=True)
        if not candidates:
            return {**result, 'status': 'unresolved', 'reason': 'No Crossref candidates'}
        message = candidates[0]
        score = title_similarity(row['论文标题'], ' '.join(message.get('title', [])))
        result.update(crossref=message, title_similarity=round(score, 4), hu_author=hu_author(message), resolved_doi=normalized_doi(message.get('DOI')))
        if score >= .90 and result['hu_author']:
            result['status'] = 'verified'
        else:
            result['status'] = 'review'
            result['reason'] = 'Check title/author mismatch or missing author metadata'
    except Exception as error:
        result.update(status='unresolved', reason=str(error))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rows', required=True)
    parser.add_argument('--cache', default='_cite/.cache/library-import')
    parser.add_argument('--output', default='_cite/reports/2026-10-18')
    args = parser.parse_args()
    registry = Registry(args.cache)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    rows = json.loads(Path(args.rows).read_text())
    verified = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(verify_row, registry, row) for row in rows]
        for future in as_completed(futures):
            verified.append(future.result())
            if len(verified) % 20 == 0:
                print(f'Checked {len(verified)}/{len(rows)} Excel records', flush=True)
    verified.sort(key=lambda r: r['excel_row'])
    (output / 'verification.json').write_text(json.dumps(verified, ensure_ascii=False, indent=2))
    fields = ['excel_row', 'status', 'input_doi', 'resolved_doi', 'title_similarity', 'hu_author', 'reason']
    with (output / 'verification.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields + ['input_title', 'registry_title', 'registry_url'], extrasaction='ignore')
        writer.writeheader()
        for r in verified:
            writer.writerow({**r, 'input_title': r['input']['论文标题'], 'registry_title': ' '.join(r.get('crossref', {}).get('title', [])), 'registry_url': 'https://doi.org/' + r.get('resolved_doi', r['input_doi'])})
    try:
        works = registry.author_works('A5079033650')
        (output / 'openalex-works.json').write_text(json.dumps(works, ensure_ascii=False, indent=2))
    except Exception as error:
        works = []
        (output / 'openalex-status.json').write_text(json.dumps({'author': 'A5079033650', 'error': str(error), 'note': 'No works imported from this endpoint; no authentication bypass attempted.'}, indent=2))
    print('Finished:', {s: sum(r['status'] == s for r in verified) for s in ('verified', 'review', 'unresolved')}, 'OpenAlex works:', len(works), flush=True)


if __name__ == '__main__':
    main()

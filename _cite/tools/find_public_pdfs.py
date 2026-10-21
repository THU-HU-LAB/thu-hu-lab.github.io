"""Find explicit open-access PDF links in Europe PMC by the verified DOI list."""
import json
from pathlib import Path
from urllib.parse import urlencode
from verify_library import Registry, normalized_doi


if __name__ == '__main__':
    report = Path('_cite/reports/2026-10-18')
    records = json.loads((report / 'verification.json').read_text())
    dois = {normalized_doi(r['citation_id']) for r in records
            if r.get('import_status') == 'imported' and r.get('citation_id', '').startswith('doi:')}
    dois.update(normalized_doi(d['doi']) for d in json.loads((report / 'review-decisions.json').read_text())['additional'])
    dois = sorted(dois)
    registry = Registry('_cite/.cache/library-import')
    matches, errors, queries = [], [], []
    for start in range(0, len(dois), 40):
        query = ' OR '.join('DOI:' + d for d in dois[start:start+40])
        url = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?' + urlencode(dict(query=query, format='json', resultType='core', pageSize=100))
        queries.append(url)
        try:
            response = registry.get(url)
            for item in response.get('resultList', {}).get('result', []):
                doi = normalized_doi(item.get('doi'))
                if doi not in dois:
                    continue
                pdfs = [u['url'] for u in item.get('fullTextUrlList', {}).get('fullTextUrl', [])
                        if u.get('availabilityCode') == 'OA' and u.get('documentStyle') == 'pdf']
                if pdfs:
                    matches.append(dict(doi=doi, pmcid=item.get('pmcid'), title=item.get('title'),
                                        url=pdfs[0], version='Open-access publisher/PMC version',
                                        filename=(item.get('pmcid') or doi.replace('/', '_')) + '.pdf'))
        except Exception as error:
            errors.append(dict(query=url, error=str(error)))
        print(f'Checked {min(start+40,len(dois))}/{len(dois)} DOIs; {len(matches)} OA PDFs', flush=True)
    (report / 'open-access-search.json').write_text(json.dumps(dict(checked_at='2026-10-18', provider='Europe PMC', dois_checked=len(dois), queries=queries, matches=matches, errors=errors), ensure_ascii=False, indent=2))
    manifest = json.loads((report / 'public-pdfs.json').read_text())
    known = {x['url'] for x in manifest}
    manifest += [m for m in matches if m['url'] not in known]
    (report / 'public-pdfs.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))

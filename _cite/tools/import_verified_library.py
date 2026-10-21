"""Import reviewed registry records; keep ambiguous Excel rows out of the public library.

Run after verify_library.py, using the saved review decisions and registry snapshot.
Requires PyYAML (already installed in the site's Docker image).
"""
import argparse
import csv
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from urllib.parse import quote

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from citation_members import merge_sources, has_verified_metadata
from verify_library import normalized_doi, normalized_title, title_similarity

HU = '0000-0002-3504-3065'
MEMBERS = {HU, '0000-0001-5121-2677', '0009-0005-1788-6148'}


def plain(value):
    return re.sub(r'\s+', ' ', re.sub('<[^>]+>', '', html.unescape(str(value or '')))).strip()


def author_name(author):
    given, family = plain(author.get('given')), plain(author.get('family'))
    if ' ' in given and normalized_title(given) == normalized_title(family):
        given = ''
    # A few older IEEE deposits store the entire name in family/given.
    name = ' '.join(filter(None, (given, family))) or plain(author.get('name'))
    name = re.sub(r'^and\s+', '', name, flags=re.I)
    if normalized_title(name) in {'huchuxiong', 'chuxionghu'}:
        return 'Chuxiong Hu'
    return name


def publication_date(message):
    candidates = []
    for field in ('published', 'published-online', 'published-print', 'issued'):
        parts = message.get(field, {}).get('date-parts', [[]])[0]
        if parts and parts[0]:
            candidates.append((tuple(parts), field))
    if not candidates:
        raise ValueError('No publication date: ' + message['DOI'])
    parts, field = min(candidates)
    value = date(*(list(parts) + [1] * (3 - len(parts)))).isoformat()
    return value, {1: 'year', 2: 'month', 3: 'day'}[len(parts)], field


def from_crossref(message, decision, checked_at):
    doi = normalized_doi(message['DOI'])
    containers = message.get('container-title', [])
    category = {'journal-article': 'journal', 'proceedings-article': 'conference', 'book-chapter': 'book-chapter', 'posted-content': 'preprint'}.get(message.get('type'), 'paper')
    if message.get('type') == 'book-chapter' and any('Proceedings' in x for x in containers):
        category = 'conference'
    if decision.get('record_type') == '勘误':
        category = 'correction'
    when, precision, date_field = publication_date(message)
    orcids = [HU]
    for author in message.get('author', []):
        oid = author.get('ORCID', '').rstrip('/').rsplit('/', 1)[-1]
        if oid in MEMBERS and oid not in orcids:
            orcids.append(oid)
    result = dict(
        id='doi:' + doi, title=plain(message['title'][0]),
        authors=[author_name(a) for a in message.get('author', [])],
        publisher=plain(containers[-1] if containers else message['publisher']),
        date=when, date_precision=precision, link='https://doi.org/' + doi,
        type='preprint' if category == 'preprint' else 'book' if category == 'book-chapter' else 'paper',
        publication_type=category, tags=[category], orcids=orcids,
        metadata_verified=True,
        verification=dict(checked_at=checked_at,
                          sources=['https://api.crossref.org/works/' + quote(doi, safe=''), *decision.get('sources', [])],
                          decision=decision.get('note', 'Excel DOI/title and author metadata agree'),
                          member_association='Hu: reviewed seed list and author identity; coauthors: explicit registry ORCID only',
                          date_field=date_field))
    if decision.get('excel_row'):
        result['verification']['excel_row'] = decision['excel_row']
    result.update(decision.get('override', {}))
    return result


def build(report, output):
    checked_at = report.name
    records = json.loads((report / 'verification.json').read_text())
    decisions = json.loads((report / 'review-decisions.json').read_text())
    metadata = json.loads((report / 'registry-supplement.json').read_text())
    by_doi = {normalized_doi(m['DOI']): m for m in metadata}
    sources, pending = [], []
    for record in records:
        decision = decisions['rows'].get(str(record['excel_row']), {})
        if record['status'] != 'verified' and not decision.get('approve'):
            record['final_status'] = 'pending'
            record['review_note'] = decision.get('note', 'Needs an exact primary-source match; not imported')
            pending.append(record)
            continue
        decision = {**decision, 'excel_row': record['excel_row'], 'record_type': record['input']['记录类型']}
        if decision.get('standalone'):
            source = decision['standalone']
            source.update(metadata_verified=True, orcids=[HU], verification=dict(checked_at=checked_at, sources=decision['sources'], excel_row=record['excel_row'], decision=decision['note']))
        else:
            message = by_doi[normalized_doi(decision['doi'])] if decision.get('doi') else record['crossref']
            source = from_crossref(message, decision, checked_at)
            record['crossref'] = message
            record['resolved_doi'] = normalized_doi(message['DOI'])
        record['import_status'] = 'imported'
        record['final_status'] = 'verified'
        record['review_note'] = decision.get('note', 'DOI/title/author match')
        record['citation_id'] = source['id']
        sources.append(source)
    for decision in decisions['additional']:
        sources.append(from_crossref(by_doi[normalized_doi(decision['doi'])], decision, checked_at))
    sources = merge_sources(sources)
    ns = {'a': 'http://www.w3.org/2005/Atom', 'x': 'http://arxiv.org/schemas/atom'}
    versions = []
    for entry in ET.parse(report / 'arxiv-records.xml').findall('a:entry', ns):
        versioned = entry.findtext('a:id', '', ns).rsplit('/', 1)[-1]
        aid = re.sub(r'v\d+$', '', versioned)
        title = plain(entry.findtext('a:title', '', ns))
        doi = normalized_doi(entry.findtext('x:doi', '', ns))
        target = next((s for s in sources if doi and s['id'] == 'doi:' + doi), None)
        if target is None:
            # Near-title matches require a recorded review decision, never auto-merge.
            explicit = decisions.get('arxiv_versions', {}).get(aid)
            target = next((s for s in sources if explicit and s['id'] == explicit), None)
        pdf = dict(text='PDF · arXiv', tooltip='Download arXiv preprint PDF', icon='fa-solid fa-file-pdf', link='https://arxiv.org/pdf/' + versioned)
        if target:
            target.setdefault('buttons', []).append(pdf)
            target['verification']['sources'].append('https://arxiv.org/abs/' + aid)
            versions.append(dict(arxiv=aid, citation_id=target['id'], decision='Preprint linked to published version; not counted twice'))
        else:
            sources.append(dict(id='arxiv:' + aid, title=title,
                                authors=[plain(a.findtext('a:name', '', ns)) for a in entry.findall('a:author', ns)],
                                publisher='arXiv (preprint)', date=entry.findtext('a:published', '', ns)[:10],
                                date_precision='day', link='https://arxiv.org/abs/' + aid,
                                type='preprint', publication_type='preprint', tags=['preprint'],
                                orcids=[HU], buttons=[pdf], metadata_verified=True,
                                verification=dict(checked_at=checked_at, sources=['https://arxiv.org/abs/' + aid],
                                                  decision='Official arXiv author metadata; Hu identity reviewed against coauthors and research context. Other members not inferred from names.')))
    assert len({s['id'] for s in sources}) == len(sources)
    oa_path = report / 'open-access-search.json'
    if oa_path.exists():
        for match in json.loads(oa_path.read_text()).get('matches', []):
            target = next((s for s in sources if s['id'] == 'doi:' + match['doi']), None)
            if target is not None:
                target.setdefault('buttons', []).append(dict(text='Full text · PMC', tooltip='Open official PMC full text', icon='fa-solid fa-file-lines', link='https://pmc.ncbi.nlm.nih.gov/articles/' + match['pmcid'] + '/'))
                target['verification']['sources'].append('https://pmc.ncbi.nlm.nih.gov/articles/' + match['pmcid'] + '/')
    assert all(has_verified_metadata(s) for s in sources)
    output.write_text(yaml.safe_dump(sources, allow_unicode=True, sort_keys=False, width=110))
    (report / 'verification.json').write_text(json.dumps(records, ensure_ascii=False, indent=2))
    (report / 'versions.json').write_text(json.dumps(versions, ensure_ascii=False, indent=2))
    fields = ['excel_row', 'status', 'final_status', 'import_status', 'citation_id', 'input_doi', 'resolved_doi', 'title_similarity', 'review_note']
    for filename, rows in [('verification.csv', records), ('pending.csv', pending)]:
        with (report / filename).open('w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields + ['input_title', 'registry_title'], extrasaction='ignore')
            writer.writeheader()
            writer.writerows({**r, 'input_title': r['input']['论文标题'], 'registry_title': ' '.join(r.get('crossref', {}).get('title', []))} for r in rows)
    print(f'Imported {len(sources)} Hu citations; {len(records)-len(pending)} Excel rows accepted; {len(pending)} pending; {len(versions)} arXiv versions linked.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, default=Path('_cite/reports/2026-10-18'))
    parser.add_argument('--output', type=Path, default=Path('_data/sources-huchuxiong.yaml'))
    args = parser.parse_args()
    build(args.report, args.output)

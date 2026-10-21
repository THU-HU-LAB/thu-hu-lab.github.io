"""Download only explicitly selected public PDF URLs; never follows a login flow."""
import csv
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import Request, urlopen


def download(entry):
    entry = dict(entry)
    path = Path('_downloads/papers') / entry['filename']
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        if path.exists():
            data = path.read_bytes()
        else:
            request = Request(entry['url'], headers={'User-Agent': 'THU-HU-LAB bibliography/1.0'})
            with urlopen(request, timeout=45) as response:
                data = response.read(50 * 1024 * 1024 + 1)
            if not data.startswith(b'%PDF-') or len(data) > 50 * 1024 * 1024:
                raise ValueError('Response is not a PDF or exceeds 50 MiB')
            path.write_bytes(data)
        entry.update(status='downloaded', bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), local_path=str(path))
    except Exception as error:
        entry.update(status='unavailable', error=str(error))
    print(entry['filename'], entry['status'], flush=True)
    return entry


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest')
    parser.add_argument('--output', default='_cite/reports/2026-10-18/downloads.csv')
    args = parser.parse_args()
    entries = json.loads(Path(args.manifest).read_text())
    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(download, entries))
    fields = ['filename', 'title', 'doi', 'pmcid', 'url', 'version', 'status', 'bytes', 'sha256', 'local_path', 'error']
    with Path(args.output).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(results)

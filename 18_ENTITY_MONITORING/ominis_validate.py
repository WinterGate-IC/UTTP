#!/usr/bin/env python3
"""Ominis-OSINT validation helper for entity monitoring.

Uses Ominis' page-inspection/username validation logic to re-check domain
leads. The script is opt-in: run it manually or set OMINIS_VALIDATE=1 before
run_pipeline.sh.

Usage:
    python3 ominis_validate.py [ENTITY ...] [--limit N]
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

OMINIS_ROOT = Path('/var/tmp/opencode/Ominis-OSINT')
if not (OMINIS_ROOT / 'ominis_src').exists():
    print(json.dumps({'error': 'Ominis not found at ' + str(OMINIS_ROOT)}))
    sys.exit(1)

sys.path.insert(0, str(OMINIS_ROOT))
DEPS_ROOT = Path('/var/tmp/opencode/ominis-deps')
if DEPS_ROOT.exists():
    sys.path.insert(0, str(DEPS_ROOT))

from ominis_src import username  # noqa: E402

ENTITY_HANDLES = {
    'UTTP': 'uttp',
    'UTTP-EMPIRE': 'uttpempire',
    'CIRCUSFALL': 'circusfall',
    'OFFICERSLAPPY': 'officerslappy',
    'DPOS': 'dpos',
    'AFR': 'afr',
    'BN0R': 'bn0r',
    'RDF': 'rdf',
    '764': '764',
    'O9A': 'o9a',
    'HARMNATION': 'harmnation',
    'SPAWNISM': 'spawnism',
    'FPE': 'fpe',
    'FPE-POLICE': 'fpepolice',
    'TNM': 'tnm',
    'ENCLAVE': 'enclave',
}


def load_register(path: Path):
    return list(csv.DictReader(path.open(newline='', encoding='utf-8')))


def save_register(path: Path, rows):
    fieldnames = list(rows[0].keys())
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def template_from_url(url: str, handle: str):
    """Turn an exact handle URL into an Ominis URL template."""
    if not url or not handle:
        return None
    pattern = re.compile(re.escape(handle), re.IGNORECASE)
    if not pattern.search(url):
        return None
    return pattern.sub('{username}', url, count=1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('entities', nargs='*', help='Entity IDs to validate')
    parser.add_argument('--limit', type=int, default=25,
                        help='Max URLs checked per entity (default 25)')
    args = parser.parse_args()

    reg_path = Path(__file__).resolve().parent.parent / '22_UTTP_DOMAINS' / 'DOMAINS_REGISTER.csv'
    rows = load_register(reg_path)

    entities = set(args.entities) if args.entities else set(ENTITY_HANDLES)
    updated = 0

    for entity_id in sorted(entities):
        handle = ENTITY_HANDLES.get(entity_id)
        if not handle:
            continue
        ent_rows = [r for r in rows if r['entity_id'] == entity_id]
        if not ent_rows:
            continue

        templates = []
        seen = set()
        for r in ent_rows:
            tpl = template_from_url(r.get('url', ''), handle)
            if tpl and tpl not in seen:
                seen.add(tpl)
                templates.append(tpl)
        templates = templates[:args.limit]
        if not templates:
            continue

        print(f'Validating {entity_id} handle "{handle}" against {len(templates)} URL(s)...')
        try:
            report = username.run_sync(handle, platforms=templates,
                                       concurrency=8, timeout=10.0)
        except Exception as exc:
            print(f'  Ominis error: {exc}')
            continue

        for hit in report.found:
            dom = (urlsplit(hit.url).hostname or '').lower()
            if dom.startswith('www.'):
                dom = dom[4:]
            if not dom:
                continue
            for r in rows:
                if r['entity_id'] != entity_id:
                    continue
                if r['domain'].lower().lstrip('www.') != dom:
                    continue
                r['link_confirmed'] = 'True'
                r['validation_status'] = (
                    f'ominis-verified ({hit.match}); HTTP {hit.status}; '
                    'ownership confirmed')
                r['entity_match'] = 'ominis-verified'
                updated += 1

    if updated:
        save_register(reg_path, rows)
    print(json.dumps({'entities': sorted(entities), 'updated_rows': updated}))


if __name__ == '__main__':
    main()
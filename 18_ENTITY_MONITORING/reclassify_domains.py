#!/usr/bin/env python3
"""Re-classify domains and split verified links from unverified leads."""
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from entity_registry import DOMAIN_TOKENS

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REGISTER = ROOT / '22_UTTP_DOMAINS' / 'DOMAINS_REGISTER.csv'
LEADS = BASE / 'domain_validation_queue.csv'
PER_ENTITY_DIR = ROOT / '22_UTTP_DOMAINS'
SUMMARY_JSON = PER_ENTITY_DIR / 'SUMMARY.json'
DEFAULT_FIELDS = [
    'entity_id', 'domain', 'url', 'platform', 'status', 'confidence',
    'source', 'occurrences', 'link_confirmed', 'notes', 'validation_status',
    'entity_match',
]


def has_exact_token(url, entity_id):
    text = (url or '').lower()
    for tok in DOMAIN_TOKENS.get(entity_id, set()):
        if re.search(r'\b' + re.escape(tok) + r'\b', text):
            return True
    return False


def read_rows(path):
    if not path.exists():
        return []
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def write_rows(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def main():
    register_rows = read_rows(REGISTER)
    lead_rows = read_rows(LEADS)
    fieldnames = list(register_rows[0].keys()) if register_rows else (
        list(lead_rows[0].keys()) if lead_rows else list(DEFAULT_FIELDS))

    combined = {}
    for row in lead_rows + register_rows:
        key = (row.get('entity_id'), row.get('url'), row.get('domain'))
        combined[key] = row
    rows = list(combined.values())

    for row in rows:
        entity = row.get('entity_id', '')
        url = row.get('url', '')
        if row.get('source') == 'User-provided':
            continue
        if 'ominis-' in (row.get('validation_status') or ''):
            continue
        exact = has_exact_token(url, entity)
        row['link_confirmed'] = 'False'
        row['entity_match'] = 'exact-handle-token' if exact else ''
        if exact:
            row['validation_status'] = 'unverified: awaiting Ominis page validation'
        else:
            row['validation_status'] = 'unverified: no exact handle token'
        if row.get('notes', '').startswith('Passive username-search lead'):
            row['notes'] = 'Auto-extracted from StyxNet; verify before citation.'

    for row in rows:
        if row.get('link_confirmed') == 'True':
            if row.get('source') != 'User-provided':
                row['notes'] = 'Ominis page-level handle linkage; entity-linked domain.'
                status = row.get('validation_status', '')
                if 'ominis-verified' in status:
                    match = re.search(r'ominis-verified \(([^)]+)\)', status)
                    signal = match.group(1) if match else 'strong-signal'
                    http = re.search(r'HTTP (\d+)', status)
                    code = http.group(1) if http else row.get('status', '')
                    row['validation_status'] = (
                        f'ominis-verified ({signal}); HTTP {code}; confirmed handle linkage')
        else:
            row['notes'] = 'Unverified lead; internal validation queue only.'

    verified = [r for r in rows if r.get('link_confirmed') == 'True']
    leads = [r for r in rows if r.get('link_confirmed') != 'True']

    write_rows(REGISTER, verified, fieldnames)
    write_rows(LEADS, leads, fieldnames)

    grouped = defaultdict(list)
    for row in verified:
        grouped[row.get('entity_id', '')].append(row)
    for stale in PER_ENTITY_DIR.glob('*/domains.csv'):
        stale.unlink()
    for entity_id, ent_rows in grouped.items():
        if not entity_id:
            continue
        write_rows(PER_ENTITY_DIR / entity_id / 'domains.csv', ent_rows, fieldnames)

    unique_domains = len({r.get('domain') for r in verified if r.get('domain')})
    entity_counts = {}
    for row in verified:
        entity = row.get('entity_id', '')
        entity_counts[entity] = entity_counts.get(entity, 0) + 1
    lead_counts = {}
    for row in leads:
        entity = row.get('entity_id', '')
        lead_counts[entity] = lead_counts.get(entity, 0) + 1

    summary = {
        'total_rows': len(verified),
        'unique_domains': unique_domains,
        'confirmed_links': len(verified),
        'unverified_leads': len(leads),
        'entities': entity_counts,
        'unverified_by_entity': lead_counts,
    }
    with SUMMARY_JSON.open('w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print(json.dumps({'verified_rows': len(verified),
                      'unverified_leads': len(leads),
                      'unique_domains': unique_domains,
                      'entities': entity_counts}, indent=2))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Re-classify domains register using exact-token (word-boundary) matching."""
import csv, json, re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from discover import TOKENS

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REGISTER = ROOT / '22_UTTP_DOMAINS' / 'DOMAINS_REGISTER.csv'
PER_ENTITY_DIR = ROOT / '22_UTTP_DOMAINS'
SUMMARY_JSON = PER_ENTITY_DIR / 'SUMMARY.json'

def has_exact_token(url, entity_id):
    """Return True if any token for entity_id appears as whole word in lowercased URL."""
    text = (url or '').lower()
    tokens = TOKENS.get(entity_id, set())
    for tok in tokens:
        # Use regex word boundary; token may contain non-word chars like digits.
        if re.search(r'\b' + re.escape(tok) + r'\b', text):
            return True
    return False

def main():
    with REGISTER.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    # Re-evaluate each row
    for r in rows:
        entity = r['entity_id']
        url = r.get('url', '')
        # Preserve user-provided verified rows as-is
        if r.get('source') == 'User-provided':
            continue
        exact = has_exact_token(url, entity)
        status_ok = r.get('status', '') in {'200', '206', '204'}
        confirmed = exact and status_ok
        r['link_confirmed'] = 'True' if confirmed else 'False'
        r['entity_match'] = 'exact-handle-token' if exact else ''
        if confirmed:
            r['validation_status'] = 'handle-token present; HTTP 2xx; ownership unverified'
        else:
            r['validation_status'] = 'unverified: no exact handle token or non-2xx response'
        # Update notes for unverified StyxNet rows
        if not confirmed and r.get('notes', '').startswith('Passive username-search lead'):
            r['notes'] = 'Auto-extracted from StyxNet; verify before citation.'

    # Write updated register
    with REGISTER.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Group by entity and write per-entity CSVs
    from collections import defaultdict
    grouped = defaultdict(list)
    for r in rows:
        grouped[r['entity_id']].append(r)

    for entity_id, ent_rows in grouped.items():
        out_path = PER_ENTITY_DIR / entity_id / 'domains.csv'
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(ent_rows)

    # Update SUMMARY.json
    unique_domains = len({r['domain'] for r in rows})
    confirmed = sum(1 for r in rows if r['link_confirmed'] == 'True')
    entity_counts = {}
    for r in rows:
        entity_counts[r['entity_id']] = entity_counts.get(r['entity_id'], 0) + 1

    summary = {
        'total_rows': len(rows),
        'unique_domains': unique_domains,
        'confirmed_links': confirmed,
        'entities': entity_counts,
    }
    with SUMMARY_JSON.open('w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print(json.dumps({
        'updated_rows': len(rows),
        'unique_domains': unique_domains,
        'confirmed_links': confirmed,
        'entities': entity_counts,
    }, indent=2))

if __name__ == '__main__':
    main()
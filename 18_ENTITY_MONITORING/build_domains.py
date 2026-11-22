#!/usr/bin/env python3
"""Publish the UTTP domains register as a site data file."""
import csv, json
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REGISTER = ROOT / '22_UTTP_DOMAINS' / 'DOMAINS_REGISTER.csv'
OUT = Path('/var/www/html/data/domains.json')

rows = list(csv.DictReader(REGISTER.open(newline='', encoding='utf-8')))
data = {
    'updated': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'count': len(rows),
    'confirmed': sum(1 for r in rows if r.get('link_confirmed') == 'True'),
    'entities': sorted({r['entity_id'] for r in rows}),
    'domains': rows,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
print(json.dumps({'domains': len(rows), 'confirmed': data['confirmed'], 'entities': len(data['entities'])}, indent=2))

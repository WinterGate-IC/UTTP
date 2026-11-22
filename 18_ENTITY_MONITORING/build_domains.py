#!/usr/bin/env python3
"""Publish the UTTP domains register as a site data file."""
import csv, json, os, tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REGISTER = ROOT / '22_UTTP_DOMAINS' / 'DOMAINS_REGISTER.csv'
OUT = Path('/var/www/html/data/domains.json')


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + '.', suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        os.chmod(path, 0o644)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)

rows = list(csv.DictReader(REGISTER.open(newline='', encoding='utf-8')))
summary_path = REGISTER.parent / 'SUMMARY.json'
try:
    summary = json.loads(summary_path.read_text(encoding='utf-8'))
except Exception:
    summary = {}
signals = {}
for r in rows:
    status = r.get('validation_status', '')
    if 'ominis-verified (' in status:
        inner = status.split('ominis-verified (', 1)[1].split(')', 1)[0]
        for signal in inner.split('+'):
            signal = signal.strip()
            if signal:
                signals[signal] = signals.get(signal, 0) + 1
    if r.get('source') == 'User-provided' or r.get('entity_match') == 'user-verified':
        signals['user-verified'] = signals.get('user-verified', 0) + 1
data = {
    'updated': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'count': len(rows),
    'confirmed': sum(1 for r in rows if r.get('link_confirmed') == 'True'),
    'lead_count': summary.get('unverified_leads', 0),
    'lead_counts': summary.get('unverified_by_entity', {}),
    'signals': signals,
    'entities': sorted({r['entity_id'] for r in rows}),
    'domains': rows,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
atomic_write(OUT, json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n')
print(json.dumps({'domains': len(rows), 'confirmed': data['confirmed'], 'entities': len(data['entities'])}, indent=2))

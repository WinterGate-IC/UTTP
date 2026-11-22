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
REGISTER = ROOT / '22_ENTITY_DOMAINS' / 'DOMAINS_REGISTER.csv'
LEADS = BASE / 'domain_validation_queue.csv'
PER_ENTITY_DIR = ROOT / '22_ENTITY_DOMAINS'
SUMMARY_JSON = PER_ENTITY_DIR / 'SUMMARY.json'
DEFAULT_FIELDS = [
    'entity_id', 'domain', 'url', 'platform', 'status', 'confidence',
    'source', 'occurrences', 'link_confirmed', 'notes', 'validation_status',
    'entity_match', 'alternate_urls',
]


def has_exact_token(url, entity_id):
    text = (url or '').lower()
    for tok in DOMAIN_TOKENS.get(entity_id, set()):
        if re.search(r'\b' + re.escape(tok) + r'\b', text):
            return True
    return False


def norm_url(value):
    value = (value or '').strip().lower().rstrip('/')
    value = re.sub(r'^https?://', '', value)
    value = re.sub(r'^www\.', '', value)
    return value


def source_occurrences():
    """Count exact-URL appearances across the passive source stores."""
    counts = {}

    def bump(url, n=1):
        key = norm_url(url)
        if key:
            counts[key] = counts.get(key, 0) + n

    for name in ('styxnet_osint.json', 'styxnet_profiles.json'):
        path = BASE / name
        if not path.exists():
            continue
        try:
            items = json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            continue
        for item in items:
            bump(item.get('url'))
    discovered = BASE / 'discovered_sources.json'
    if discovered.exists():
        try:
            items = json.loads(discovered.read_text(encoding='utf-8'))
        except Exception:
            items = []
        for item in items:
            bump(item.get('url'), max(1, len(item.get('source_files') or [])))
    raw = ROOT / '09_STYXNET_REPORTS' / 'styxnet_UTTP_csv_1789803261.csv'
    if raw.exists():
        try:
            with raw.open(newline='', encoding='utf-8') as fh:
                for item in csv.DictReader(fh):
                    bump(item.get('url'))
        except Exception:
            pass
    return counts


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
    # Merge verified rows that point at the same entity/domain but different
    # handle URLs. Preserve every URL in alternate_urls and keep the strongest
    # signal set. Unverified leads are merged separately from verified rows.
    def _signals(status):
        if 'ominis-verified (' in (status or ''):
            return {x for x in status.split('ominis-verified (', 1)[1].split(')', 1)[0].split('+') if x}
        return set()

    def _occ(row):
        try:
            return max(1, int(row.get('occurrences') or 1))
        except ValueError:
            return 1

    merged = {}
    for row in rows:
        key = (row.get('entity_id'), (row.get('domain') or '').lower(), row.get('link_confirmed'))
        base = merged.get(key)
        if base is None:
            merged[key] = row
            continue
        urls = [base.get('url') or ''] + [u for u in (base.get('alternate_urls') or '').split(';') if u]
        urls += [row.get('url') or ''] + [u for u in (row.get('alternate_urls') or '').split(';') if u]
        seen, unique = set(), []
        for url in urls:
            key_url = norm_url(url)
            if key_url and key_url not in seen:
                seen.add(key_url)
                unique.append(url)
        primary = base.get('url') or (unique[0] if unique else '')
        if primary and norm_url(primary) not in seen:
            unique.insert(0, primary)
        base['url'] = primary
        base['alternate_urls'] = ';'.join(u for u in unique if norm_url(u) != norm_url(primary))
        alt_count = len([u for u in base['alternate_urls'].split(';') if u])
        base['occurrences'] = str(max(_occ(base), _occ(row), 1 + alt_count))
        sigs = _signals(base.get('validation_status')) | _signals(row.get('validation_status'))
        if sigs:
            http = row.get('status') or base.get('status') or ''
            base['validation_status'] = (
                f"ominis-verified ({'+'.join(sorted(sigs))}); HTTP {http}; confirmed handle linkage")
            base['entity_match'] = 'ominis-verified'
            base['link_confirmed'] = 'True'
            base['notes'] = 'Ominis page-level handle linkage; entity-linked domain.'
        try:
            if int(row.get('confidence') or 0) > int(base.get('confidence') or 0):
                base['confidence'] = row.get('confidence')
        except ValueError:
            pass
        base['status'] = row.get('status') or base.get('status')
        sources = {x for x in ((base.get('source') or '') + ' + ' + (row.get('source') or '')).split(' + ') if x}
        base['source'] = ' + '.join(sorted(sources))
    rows = list(merged.values())
    if 'alternate_urls' not in fieldnames:
        fieldnames.append('alternate_urls')
    for row in rows:
        row.setdefault('alternate_urls', '')

    occurrences = source_occurrences()
    for row in rows:
        try:
            current = max(1, int(row.get('occurrences') or 1))
        except ValueError:
            current = 1
        alt_count = len([u for u in (row.get('alternate_urls') or '').split(';') if u])
        found = occurrences.get(norm_url(row.get('url')), 0)
        row['occurrences'] = str(max(current, found + alt_count, 1))

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
        folder = PER_ENTITY_DIR / entity_id
        write_rows(folder / 'domains.csv', ent_rows, fieldnames)
        (folder / 'README.md').write_text(
            f"""# {entity_id} domains

Verified domain links confirmed through Ominis-OSINT page inspection.

- Verified domains: {len(ent_rows)}
- Validation: strong page-level handle linkage
- Publication: verified-only

A verified domain is treated as either owned by the entity or a domain/platform
the entity operates in. Validation confirms entity handle linkage, not legal
ownership. Unverified leads remain in the internal validation queue and are not
listed here.
""", encoding='utf-8')
    keep = set(grouped)
    for folder in PER_ENTITY_DIR.iterdir():
        if folder.is_dir() and folder.name not in keep:
            for child in sorted(folder.rglob('*'), reverse=True):
                if child.is_file() or child.is_symlink():
                    child.unlink()
                elif child.is_dir():
                    child.rmdir()
            folder.rmdir()

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
    (PER_ENTITY_DIR / 'README.md').write_text(
        f"""# Entity Domains

Verified domain links for every tracked entity. This folder is no longer
UTTP-specific because it covers the full monitored ecosystem.

- Verified domains: {len(verified)}
- Unique domains: {unique_domains}
- Entities with verified domains: {len(entity_counts)}
- Internal unverified leads: {len(leads)}

Only domains confirmed through Ominis-OSINT page-level validation are listed.
A verified domain is treated as either owned by the entity or a domain/platform
the entity operates in. Validation confirms entity handle linkage, not legal
ownership. Unverified leads remain in `18_ENTITY_MONITORING/domain_validation_queue.csv`
and are not published in this folder or on the Explore tab.

- `occurrences` counts exact URL appearances across the passive source stores
  plus distinct handle URLs found on the same domain.
- `alternate_urls` preserves additional profile URLs on the same domain for
  the same entity instead of stopping after the first handle.
""", encoding='utf-8')

    print(json.dumps({'verified_rows': len(verified),
                      'unverified_leads': len(leads),
                      'unique_domains': unique_domains,
                      'entities': entity_counts}, indent=2))


if __name__ == '__main__':
    main()

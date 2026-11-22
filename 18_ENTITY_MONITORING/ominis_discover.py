#!/usr/bin/env python3
"""Discover entity profiles with Ominis-OSINT username checks.

Runs Ominis against its platform templates for entity handles that currently
have few or no verified domains. Only strong page signals are added to the
verified register; everything else is ignored.
"""
import argparse
import csv
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlsplit

OMINIS_ROOT = Path(os.environ.get('OMINIS_ROOT', '/var/tmp/opencode/Ominis-OSINT'))
DEPS_ROOT = Path(os.environ.get('OMINIS_DEPS', '/var/tmp/opencode/ominis-deps'))
if not (OMINIS_ROOT / 'ominis_src').exists():
    print(json.dumps({'error': 'Ominis not found at ' + str(OMINIS_ROOT)}))
    sys.exit(1)
if DEPS_ROOT.exists():
    sys.path.insert(0, str(DEPS_ROOT))
sys.path.insert(0, str(OMINIS_ROOT))

from ominis_src import username  # noqa: E402

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REGISTER = ROOT / '22_ENTITY_DOMAINS' / 'DOMAINS_REGISTER.csv'
QUEUE = BASE / 'domain_validation_queue.csv'
CACHE = BASE / 'ominis_discovery_cache.json'

from entity_registry import ENTITY_HANDLES

STRONG = {'metadata', 'structured', 'redirect', 'canonical'}
REFRESH_AFTER = timedelta(days=7)
FIELDS = [
    'entity_id', 'domain', 'url', 'platform', 'status', 'confidence',
    'source', 'occurrences', 'link_confirmed', 'notes', 'validation_status',
    'entity_match',
]


def stamp():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def load_rows(path):
    if not path.exists():
        return []
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def save_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def fresh(entry):
    if not entry:
        return False
    checked = entry.get('checked_at')
    if not checked:
        return False
    try:
        dt = datetime.fromisoformat(checked.replace('Z', '+00:00'))
    except Exception:
        return False
    return datetime.now(timezone.utc) - dt < REFRESH_AFTER


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('entities', nargs='*', help='Optional entity IDs')
    parser.add_argument('--budget', type=int, default=1,
                        help='Maximum entities to discover per run')
    parser.add_argument('--concurrency', type=int, default=8)
    parser.add_argument('--timeout', type=float, default=8.0)
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()

    combined = {}
    for row in load_rows(QUEUE) + load_rows(REGISTER):
        combined[(row.get('entity_id'), row.get('url'), row.get('domain'))] = row
    rows = list(combined.values())
    cache = json.loads(CACHE.read_text(encoding='utf-8')) if CACHE.exists() else {}

    verified_counts = Counter(r.get('entity_id') for r in rows if r.get('link_confirmed') == 'True')
    wanted = set(args.entities) if args.entities else set(ENTITY_HANDLES)
    candidates = []
    for entity in wanted:
        if entity not in ENTITY_HANDLES:
            continue
        if not args.force and fresh(cache.get(entity)):
            continue
        candidates.append((verified_counts.get(entity, 0), entity))
    candidates.sort()
    selected = [entity for _, entity in candidates[:max(0, args.budget)]]
    if not selected:
        print(json.dumps({'discovered': 0, 'entities': [], 'reason': 'no eligible entities'}))
        return

    platforms = username.load_platforms()
    added = 0
    for entity in selected:
        handle = ENTITY_HANDLES[entity]
        print(f'Discovering {entity} handle "{handle}" across {len(platforms)} platforms...')
        try:
            report = username.run_sync(handle, platforms=platforms,
                                       concurrency=args.concurrency,
                                       timeout=args.timeout)
        except Exception as exc:
            print(f'  Ominis discovery error: {exc}')
            continue

        found_urls = []
        for hit in report.found:
            if hit.match not in STRONG:
                continue
            domain = (urlsplit(hit.url).hostname or '').lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            if not domain:
                continue
            found_urls.append(hit.url)
            existing = None
            for key, row in combined.items():
                if row.get('entity_id') == entity and (row.get('domain') or '').lower().lstrip('www.') == domain:
                    existing = row
                    break
            if existing:
                existing['url'] = hit.url
                existing['platform'] = hit.platform or existing.get('platform', '')
                existing['status'] = str(hit.status)
                existing['confidence'] = str(hit.confidence or existing.get('confidence', ''))
                existing['source'] = 'Ominis discovery'
                existing['link_confirmed'] = 'True'
                existing['notes'] = 'Ominis page-level handle linkage; entity-linked domain.'
                existing['validation_status'] = (
                    f'ominis-verified ({hit.match}); HTTP {hit.status}; '
                    'confirmed handle linkage')
                existing['entity_match'] = 'ominis-verified'
                added += 1
                continue
            key = (entity, hit.url, domain)
            combined[key] = {
                'entity_id': entity,
                'domain': domain,
                'url': hit.url,
                'platform': hit.platform or '',
                'status': str(hit.status),
                'confidence': str(hit.confidence or ''),
                'source': 'Ominis discovery',
                'occurrences': '1',
                'link_confirmed': 'True',
                'notes': 'Ominis page-level handle linkage; entity-linked domain.',
                'validation_status': (
                    f'ominis-verified ({hit.match}); HTTP {hit.status}; '
                    'confirmed handle linkage'),
                'entity_match': 'ominis-verified',
            }
            added += 1

        cache[entity] = {
            'checked_at': stamp(),
            'handle': handle,
            'platforms_checked': len(platforms),
            'strong_matches': len(found_urls),
            'urls': found_urls,
        }

    rows = list(combined.values())
    save_rows(REGISTER, rows)
    CACHE.write_text(json.dumps(cache, indent=2) + '\n', encoding='utf-8')
    try:
        from reclassify_domains import main as reclassify
        reclassify()
    except Exception:
        pass
    print(json.dumps({'entities': selected, 'new_or_updated': added,
                      'cache': str(CACHE)}, indent=2))


if __name__ == '__main__':
    main()

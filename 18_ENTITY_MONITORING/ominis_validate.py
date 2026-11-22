#!/usr/bin/env python3
"""Automated Ominis-OSINT validation for domain leads.

Reads each page and uses Ominis page-inspection primitives: metadata,
canonical URL, redirect, embedded JSON handles, structured data, and visible
body. A 200 response alone is never enough. Runs incrementally with a cache
and per-run budget so the normal pipeline stays gentle.
"""
import argparse
import asyncio
import csv
import json
import os
import re
import sys
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

import httpx  # noqa: E402
from ominis_src import platforms, username  # noqa: E402

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REGISTER = ROOT / '22_UTTP_DOMAINS' / 'DOMAINS_REGISTER.csv'
LEADS = BASE / 'domain_validation_queue.csv'
CACHE = BASE / 'ominis_validation_cache.json'

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
    'AUTTP': 'auttp',
    '148': '148',
    'SPWN': 'spwn',
    'E11': '11thstreet',
    'KKTK': 'kktk',
    'YFGA': 'yfga',
    'VGCP': 'vgcp',
    'AFF': 'aff',
    'TND': 'tnd',
    'ZETA': 'zeta',
    'YTDESTROYERS': 'ytdestroyers',
    'C09A': '09a',
    'TYRANNYRUTTP': 'tyrannyruttp',
    'RDFPARTY': 'rdfparty',
    'THEFARTKNOCKERSTFK': 'thefartknockers',
}

ENTITY_TERMS = {
    'UTTP': ('utube troll police', 'youtube troll police', 'uttp empire'),
    'DPOS': ('degeneracy police', 'degeneracy police order state',
             'police order state', 'degenerate police'),
    'O9A': ('order of nine angles', 'nine angles', 'ona'),
    'FPE': ('fundamental paper education', 'fundamental paper'),
    'SPAWNISM': ('spawnism',),
    'AFR': ('antifandom resistance', 'anti fandom resistance'),
}

STRONG_SIGNALS = {'metadata', 'structured', 'redirect', 'canonical', 'json'}
SKIP_MARKERS = (
    '/search', 'search?', 'keywords=', 'author=', '?q=', '&q=', 'query=',
    'filter?search', '/find?', 'search-index', '/login', '/signup',
    '/register', '/password', '/account/',
)
REVALIDATE_AFTER = timedelta(days=7)
DEFAULT_BUDGET = 40
DEFAULT_CONCURRENCY = 4
DEFAULT_TIMEOUT = 10.0
MAX_BODY = 2_000_000

JSON_HANDLE_RE = re.compile(
    r'"(?:username|handle|login|screen_name|uniqueId|vanityChannelUrl|'
    r'canonicalBaseUrl|alternateName|author|owner|account|user)"\s*:\s*'
    r'"@?([^"]{1,200})"', re.IGNORECASE)


def now():
    return datetime.now(timezone.utc)


def stamp():
    return now().strftime('%Y-%m-%dT%H:%M:%SZ')


def load_json(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            return default
    return default


def load_rows(path):
    if not path.exists():
        return []
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def load_register():
    combined = {}
    for row in load_rows(LEADS) + load_rows(REGISTER):
        key = (row.get('entity_id'), row.get('url'), row.get('domain'))
        combined[key] = row
    return list(combined.values())


def save_register(rows):
    fieldnames = list(rows[0].keys())
    with REGISTER.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def json_handle_match(body, handle):
    for match in JSON_HANDLE_RE.finditer(body[:MAX_BODY]):
        value = match.group(1).strip().lstrip('@~')
        value = value.split('?', 1)[0].split('#', 1)[0]
        if '/' in value:
            value = [part for part in value.split('/') if part][-1]
        if value.casefold() == handle.casefold():
            return True
    return False


def entity_terms_present(body, title, entity):
    terms = ENTITY_TERMS.get(entity, ())
    haystack = (title + ' ' + body).casefold()
    return [term for term in terms if term in haystack]


def is_candidate(row):
    if row.get('source') == 'User-provided':
        return False
    if not row.get('url') or not row.get('domain'):
        return False
    entity = row.get('entity_id')
    if entity not in ENTITY_HANDLES:
        return False
    low = row['url'].lower()
    if any(marker in low for marker in SKIP_MARKERS):
        return False
    if (row.get('entity_match') != 'exact-handle-token'
            and not (row.get('entity_match') or '').startswith('ominis-')
            and row.get('link_confirmed') != 'True'):
        return False
    return True


def cache_fresh(entry):
    if not entry or entry.get('error'):
        return False
    checked = entry.get('checked_at')
    if not checked:
        return False
    try:
        dt = datetime.fromisoformat(checked.replace('Z', '+00:00'))
    except Exception:
        return False
    return now() - dt < REVALIDATE_AFTER


async def inspect_url(client, entity, handle, url, timeout):
    try:
        response = await client.get(url, timeout=timeout, follow_redirects=True)
    except Exception as exc:
        return {'error': str(exc)}

    status = response.status_code
    body = response.text[:MAX_BODY]
    info = username.parse_page_info(body)
    title = info.title or info.og_title
    meta_text = ' '.join(part for part in (
        info.title, info.og_title, info.description, info.og_description) if part)
    visible = info.visible

    if any(marker in title.casefold() for marker in username._MISSING_MARKERS):
        return {'status': status, 'signals': [], 'title': title,
                'final_url': str(response.url), 'missing': True}
    if info.embedded_missing:
        return {'status': status, 'signals': [], 'title': title,
                'final_url': str(response.url), 'missing': True}
    if any(marker in visible.casefold() for marker in username._BODY_MISSING_MARKERS):
        return {'status': status, 'signals': [], 'title': title,
                'final_url': str(response.url), 'missing': True}

    signals = []
    requested = urlsplit(url)
    final = urlsplit(str(response.url))
    path_changed = final.path.rstrip('/') != requested.path.rstrip('/')
    if path_changed and username._mentions(final.path, handle):
        signals.append('redirect')
    if username._mentions(meta_text, handle):
        signals.append('metadata')
    if any(h.casefold() == handle.casefold() for h in info.handles):
        signals.append('structured')
    if json_handle_match(body, handle):
        signals.append('json')
    canonical = username._canonical_handle(info)
    if canonical and username._mentions(canonical, handle):
        signals.append('canonical')
    if username._mentions(visible, handle):
        signals.append('body')

    detected = platforms.detect_profiles(str(response.url)) or platforms.detect_profiles(url)
    platform_confidence = int(detected[0].get('confidence') or 0) if detected else 0
    related = entity_terms_present(body, title, entity)

    return {
        'status': status,
        'signals': sorted(set(signals)),
        'title': title,
        'final_url': str(response.url),
        'platform_confidence': platform_confidence,
        'related_terms': related,
    }


def mark_row(row, result):
    if result.get('error'):
        row['validation_status'] = f"ominis-error; {result['error']}; previous status retained"
        return False

    signals = set(result.get('signals') or [])
    status = result.get('status')
    strong = sorted(signals & STRONG_SIGNALS)
    if strong:
        row['link_confirmed'] = 'True'
        row['validation_status'] = (
            f"ominis-verified ({'+'.join(strong)}); HTTP {status}; handle verified, ownership unverified")
        row['entity_match'] = 'ominis-verified'
        return True
    if 'body' in signals:
        related = result.get('related_terms') or []
        label = 'ominis-body-related' if related else 'ominis-body-only'
        row['link_confirmed'] = 'False'
        row['validation_status'] = f"{label}; HTTP {status}; unverified"
        row['entity_match'] = label
        return True
    row['link_confirmed'] = 'False'
    row['validation_status'] = f"ominis-no-match; HTTP {status}; unverified"
    row['entity_match'] = 'ominis-no-match'
    return True


async def validate(all_rows, target_rows, budget, concurrency, timeout):
    cache = load_json(CACHE, {})
    candidates = []
    for row in target_rows:
        if not is_candidate(row):
            continue
        key = f"{row['entity_id']}|{row['url']}"
        if cache_fresh(cache.get(key)):
            continue
        candidates.append((row, key))

    verified_counts = {}
    for row in all_rows:
        if row.get('link_confirmed') == 'True':
            entity = row.get('entity_id', '')
            verified_counts[entity] = verified_counts.get(entity, 0) + 1
    candidates.sort(key=lambda item: (
        verified_counts.get(item[0].get('entity_id', ''), 0),
        0 if item[0].get('link_confirmed') == 'True' else 1,
        item[0].get('entity_id', ''),
        item[0].get('domain', ''),
    ))
    candidates = candidates[:budget]
    if not candidates:
        return 0, 0

    headers = {
        'User-Agent': ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/126.0 Safari/537.36"),
        'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8',
    }
    semaphore = asyncio.Semaphore(max(1, concurrency))

    async with httpx.AsyncClient(headers=headers, follow_redirects=True,
                                 timeout=timeout) as client:
        async def worker(row, key):
            async with semaphore:
                entity = row['entity_id']
                handle = ENTITY_HANDLES[entity]
                result = await inspect_url(client, entity, handle,
                                           row['url'], timeout)
                result['checked_at'] = stamp()
                result['url'] = row['url']
                cache[key] = result
                return row, result

        tasks = [worker(row, key) for row, key in candidates]
        results = await asyncio.gather(*tasks)

    checked = 0
    updated = 0
    for row, result in results:
        checked += 1
        if mark_row(row, result):
            updated += 1

    save_register(all_rows)
    CACHE.write_text(json.dumps(cache, indent=2) + '\n', encoding='utf-8')
    return checked, updated


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('entities', nargs='*', help='Optional entity IDs')
    parser.add_argument('--budget', type=int, default=DEFAULT_BUDGET)
    parser.add_argument('--concurrency', type=int, default=DEFAULT_CONCURRENCY)
    parser.add_argument('--timeout', type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument('--force', action='store_true',
                        help='Ignore cache freshness')
    args = parser.parse_args()

    all_rows = load_register()
    target_rows = all_rows
    if args.entities:
        wanted = set(args.entities)
        target_rows = [r for r in all_rows if r['entity_id'] in wanted]

    if args.force:
        cache = load_json(CACHE, {})
        for r in target_rows:
            cache.pop(f"{r['entity_id']}|{r['url']}", None)
        CACHE.write_text(json.dumps(cache, indent=2) + '\n', encoding='utf-8')

    checked, updated = asyncio.run(
        validate(all_rows, target_rows, args.budget, args.concurrency, args.timeout))

    if updated:
        try:
            from reclassify_domains import main as reclassify
            reclassify()
        except Exception:
            pass

    print(json.dumps({
        'checked': checked,
        'updated_rows': updated,
        'budget': args.budget,
        'cache': str(CACHE),
    }, indent=2))


if __name__ == '__main__':
    main()

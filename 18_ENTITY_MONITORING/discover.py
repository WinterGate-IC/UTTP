#!/usr/bin/env python3
"""Incremental discovery layer.

Passively discovers new source URLs, platform surfaces, rebrands, watch leads,
potential claims, tactical indicators, and migration timing. Every output is
append-only and stateful so counts grow over time instead of resetting.
"""
import csv
import hashlib
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
OUT = BASE
DATA = BASE / 'entity-intelligence.json'
GENERAL_LIST = ROOT / '02_CORE_INVESTIGATION' / 'Members_List' / 'General_List_v2_Structured_2026-11-19.md'
AREA_REGISTER = ROOT / '02_CORE_INVESTIGATION' / 'AREA_INTELLIGENCE' / 'UTTP_AREA_REGISTER.csv'
STYXNET_RAW = ROOT / '09_STYXNET_REPORTS' / 'styxnet_UTTP_csv_1789803261.csv'
STYXNET_CANDIDATES = ROOT / '09_STYXNET_REPORTS' / 'validation' / 'styxnet_handle_candidates.csv'
OSINT_PATH = BASE / 'styxnet_osint.json'

STATE_PATH = OUT / 'discovery_state.json'
SOURCES_PATH = OUT / 'discovered_sources.json'
AREAS_PATH = OUT / 'discovered_areas.json'
CLAIMS_PATH = OUT / 'potential_claims.json'
WATCHLIST_PATH = OUT / 'discovered_watchlist.json'
TACTICS_PATH = OUT / 'discovered_tactics.json'
EVENTS_PATH = OUT / 'discovery_events.json'
REBRANDS_PATH = OUT / 'rebrands.json'
MIGRATIONS_PATH = OUT / 'migration_events.json'
STYXNET_PROFILES_PATH = OUT / 'styxnet_profiles.json'

URL_RE = re.compile(r'https?://[^\s\)\]\}"\'<>]+')
SCAN_GLOBS = [
    '00_READ_FIRST/*.md',
    '12_TRACKING/*.md',
    '13_UTTP_764_OVERLAP/*.md',
    '14_O9A_764_TRACE/*.md',
    '15_VALIDATED_CLAIMS/*.csv',
    '16_VALIDATED_FALSE_CLAIMS/*.csv',
    '17_CURRENT_STATE_PACKAGE/*.md',
    '18_ENTITY_MONITORING/*.md',
    '02_CORE_INVESTIGATION/AREA_INTELLIGENCE/*.csv',
    '02_CORE_INVESTIGATION/Members_List/General_List_v2_Structured_2026-11-19.md',
    '09_STYXNET_REPORTS/*.csv',
]

TOKENS = {
    'UTTP': {'uttp', 'utube', 'troll', 'police'},
    'UTTP-EMPIRE': {'empire', 'nuuttp'},
    'CIRCUSFALL': {'circusfall'},
    'OFFICERSLAPPY': {'officerslappy', 'slappy', 'forum'},
    'AFR': {'afr', 'antifandomresistance'},
    'BN0R': {'bn0r', 'empire'},
    'RDF': {'rdf', 'reddit', 'defence', 'defense', 'rdfparty'},
    'DPOS': {'dpos', 'degeneracy', 'police', 'order', 'state'},
    '764': {'764'},
    'O9A': {'o9a', 'ona', 'nine', 'angles'},
    'HARMNATION': {'harmnation', 'harm'},
    'SPAWNISM': {'spawnism', 'spawn'},
    'FPE': {'fpe', 'fundamental', 'paper', 'education'},
    'FPE-POLICE': {'fpepolice', 'police'},
    'TNM': {'tnm', 'militia'},
    'ENCLAVE': {'enclave', 'imperium'},
}

ALIASES = {
    'uttputubetrollpolice': 'UTTP',
    'uttpempirenuuttp': 'UTTP-EMPIRE',
    'circusfallfaction': 'CIRCUSFALL',
    'officerslappyfactionuttpforum': 'OFFICERSLAPPY',
    'dposdegeneracypoliceorderstate': 'DPOS',
    'antifandomresistanceafr': 'AFR',
    'bn0rempire': 'BN0R',
    'redditdefenceforcerdf': 'RDF',
    'kktkkukluxtrollklan': 'KKTK',
    'yfga': 'YFGA',
    'vgcpvideogamecartoonpolice': 'VGCP',
    'affantifandomfront': 'AFF',
    'auttpantiuttp': 'AUTTP',
    '764': '764',
    'harmnation': 'HARMNATION',
    'o9aona': 'O9A',
    'spawnism': 'SPAWNISM',
    'fpepolice': 'FPE-POLICE',
    'fpeecosystem': 'FPE',
    'tnmthemilitia': 'TNM',
    '1481488': '148',
    'imperiumoftheenclavegrs': 'ENCLAVE',
}


def nkey(value):
    return re.sub(r'[^a-z0-9]+', '', (value or '').lower())


def norm_url(value):
    value = (value or '').strip().rstrip('.,;:').lower()
    value = re.sub(r'^https?://', '', value)
    value = re.sub(r'^www\.', '', value).rstrip('/')
    return value


def domain_of(url):
    m = re.match(r'^(?:https?://)?(?:www\.)?([^/\s]+)', url or '')
    return m.group(1).lower() if m else ''


def now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def load_json(path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            return default
    return default


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def scan_files():
    urls = {}
    files = {}
    for pattern in SCAN_GLOBS:
        for path in sorted(ROOT.glob(pattern)):
            if not path.is_file() or '.git' in path.parts or '__pycache__' in path.parts:
                continue
            try:
                text = path.read_text(encoding='utf-8', errors='replace')
            except Exception:
                continue
            rel = str(path.relative_to(ROOT))
            files[rel] = hashlib.sha256(text.encode('utf-8')).hexdigest()
            for raw in URL_RE.findall(text):
                url = raw.rstrip('.,;:')
                entry = urls.setdefault(norm_url(url), {'url': url, 'files': set()})
                entry['files'].add(rel)
    return files, urls


def read_register_names():
    names = []
    if not GENERAL_LIST.exists():
        return names
    section = None
    for line in GENERAL_LIST.read_text(encoding='utf-8').splitlines():
        if line.startswith('#'):
            section = line.lstrip('#').strip()
            continue
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 2:
            continue
        name = cells[0].strip()
        if not name or name.lower() in {'group', 'name', 'campaign', 'handle'} or set(name) <= set('-: '):
            continue
        if section and section.startswith(('2.', '3.')) and not section.startswith('###'):
            names.append(name)
    return names


def read_area_snapshot():
    snapshot = {}
    if not AREA_REGISTER.exists():
        return snapshot
    for row in csv.DictReader(AREA_REGISTER.open(newline='', encoding='utf-8')):
        platform = row.get('platform', '').strip()
        if not platform:
            continue
        item = snapshot.setdefault(platform, {'rows': 0, 'statuses': {}, 'confidence': row.get('confidence', '')})
        item['rows'] += 1
        status = row.get('presence_status', 'unknown')
        item['statuses'][status] = item['statuses'].get(status, 0) + 1
    return snapshot


def next_id(prefix, values, width=3):
    nums = []
    for value in values:
        m = re.search(r'(\d+)$', str(value.get('id', '')))
        if m:
            nums.append(int(m.group(1)))
    return f'{prefix}{(max(nums, default=0) + 1):0{width}d}'


def platform_for_row(row):
    return (row.get('platform') or row.get('aliases') or row.get('similar_username') or 'Unknown').strip()


def add_state_items(state, key, items, id_prefix, dedup):
    existing = state.setdefault(key, {})
    added = 0
    for item in items:
        k = dedup(item)
        if not k or k in existing:
            continue
        existing[k] = {'id': next_id(id_prefix, list(existing.values())), **item, 'first_seen': item.get('first_seen', now())}
        added += 1
    return added


def main():
    data = json.loads(DATA.read_text(encoding='utf-8'))
    state = load_json(STATE_PATH, {})
    for key in ('files', 'discovered', 'discovered_areas', 'potential_claims', 'discovered_watchlist', 'discovered_tactics', 'discovery_events', 'area_snapshot', 'styxnet_profiles', 'previous_counts'):
        state.setdefault(key, {} if key != 'discovery_events' else [])
    state.setdefault('last_run', None)

    existing_urls = {norm_url(s.get('url', '')) for s in data.get('sources', []) if s.get('url')}
    existing_ids = {e['id'] for e in data.get('entities', [])}
    files, urls = scan_files()

    # Merge archive URLs, StyxNet profile URLs, and OSINT finding URLs.
    all_urls = dict(urls)
    if STYXNET_RAW.exists():
        for row in csv.DictReader(STYXNET_RAW.open(newline='', encoding='utf-8')):
            if row.get('status') not in {'200', '206', '204'}:
                continue
            url = (row.get('url') or '').strip()
            key = norm_url(url)
            if not key or any(marker in key for marker in ('/search', 'search?', 'keywords=', 'author=', '?q=', '&q=', 'query=', 'filter?search', '/find?', 'search-index')):
                continue
            entry = all_urls.setdefault(key, {'url': url, 'files': set()})
            entry['files'].add('09_STYXNET_REPORTS/styxnet_UTTP_csv_1789803261.csv')
    osint_findings = load_json(BASE / 'styxnet_osint.json', [])
    for finding in osint_findings:
        url = (finding.get('url') or '').strip()
        key = norm_url(url)
        if not key or any(marker in key for marker in ('/search', 'search?', 'keywords=', 'author=', '?q=', '&q=', 'query=', 'filter?search', '/find?', 'search-index')):
            continue
        entry = all_urls.setdefault(key, {'url': url, 'files': set()})
        entry['files'].add('styxnet_osint')

    stamp = now()
    added_sources = 0
    for key, item in sorted(all_urls.items()):
        if key in existing_urls or key in state['discovered']:
            if key in state['discovered']:
                state['discovered'][key]['last_seen'] = stamp
            continue
        source_id = f"D{len(state['discovered']) + 1:03d}"
        state['discovered'][key] = {
            'id': source_id,
            'url': item['url'],
            'domain': domain_of(item['url']),
            'first_seen': stamp,
            'last_seen': stamp,
            'source_files': sorted(item['files']),
        }
        added_sources += 1
    state['files'] = files
    state['last_run'] = stamp
    discovered = sorted(state['discovered'].values(), key=lambda x: x['id'])
    write_json(SOURCES_PATH, discovered)

    # Rebrands from the structured register.
    rebrands = []
    seen_rebrands = set()
    for name in read_register_names():
        key = nkey(name)
        mapped = ALIASES.get(key)
        entity_id = mapped if mapped in existing_ids else None
        if not entity_id:
            low = key
            for eid, tokens in TOKENS.items():
                if eid not in existing_ids:
                    continue
                if any(token in low for token in tokens):
                    entity_id = eid
                    break
        if not entity_id:
            continue
        pair = (entity_id, key)
        if pair in seen_rebrands:
            continue
        seen_rebrands.add(pair)
        rebrands.append({'name': name, 'entity_id': entity_id, 'basis': 'name_token', 'first_seen': stamp})
    write_json(REBRANDS_PATH, rebrands)

    # Area surfaces: curated snapshot plus discovered StyxNet/OSINT surfaces.
    current_area = read_area_snapshot()
    previous = state.get('area_snapshot') or {}
    migrations = list(state.get('migration_events') or [])
    for platform in sorted(set(previous) | set(current_area)):
        before = previous.get(platform)
        after = current_area.get(platform)
        if before is None and after is not None:
            migrations.append({'date': stamp, 'platform': platform, 'change': 'added_surface', 'detail': f'{after["rows"]} rows'})
        elif after is None and before is not None:
            migrations.append({'date': stamp, 'platform': platform, 'change': 'removed_surface', 'detail': f'{before["rows"]} rows'})
        elif before is not None and after is not None and before['statuses'] != after['statuses']:
            migrations.append({'date': stamp, 'platform': platform, 'change': 'status_change', 'detail': f'{before["statuses"]} -> {after["statuses"]}'})
    state['area_snapshot'] = current_area

    def area_key(item):
        return f"{item['platform'].lower()}|{norm_url(item.get('surface_url', ''))}"

    new_areas = []
    if STYXNET_RAW.exists():
        for row in csv.DictReader(STYXNET_RAW.open(newline='', encoding='utf-8')):
            if row.get('status') not in {'200', '206', '204'}:
                continue
            url = (row.get('url') or '').strip()
            key = norm_url(url)
            if not key or any(marker in key for marker in ('/search', 'search?', 'keywords=', 'author=', '?q=', '&q=', 'query=', 'filter?search', '/find?', 'search-index')):
                continue
            new_areas.append({'platform': (row.get('platform') or 'Unknown').strip(), 'surface_url': url, 'status': 'discovered', 'confidence': 'D/S', 'why': 'Auto-discovered from StyxNet export; verify before citation.'})
    for finding in osint_findings:
        url = (finding.get('url') or '').strip()
        key = norm_url(url)
        if not key or any(marker in key for marker in ('/search', 'search?', 'keywords=', 'author=', '?q=', '&q=', 'query=', 'filter?search', '/find?', 'search-index')):
            continue
        new_areas.append({'platform': (finding.get('platform') or 'Unknown').strip(), 'surface_url': url, 'status': 'discovered', 'confidence': 'D/S', 'why': 'Auto-discovered from StyxNet OSINT; verify before citation.'})

    added_areas = add_state_items(state, 'discovered_areas', new_areas, 'A_D', area_key)
    # Treat newly discovered platforms as migration events.
    previous_area_keys = {k for k in (state.get('previous_counts') or {})}
    discovered_areas = list(state['discovered_areas'].values())
    new_platforms = []
    seen_platforms = {str(x).lower() for x in state.get('seen_migration_platforms', [])}
    for area in discovered_areas:
        plat = str(area.get('platform', '')).lower()
        if plat and plat not in seen_platforms:
            new_platforms.append(plat)
            seen_platforms.add(plat)
    for plat in new_platforms:
        migrations.append({'date': stamp, 'platform': plat, 'change': 'discovered_surface', 'detail': 'Auto-discovered platform surface'})
    write_json(AREAS_PATH, discovered_areas)
    # Preserve historical migration events instead of replacing them each run.
    if not migrations and state.get('seen_migration_platforms'):
        for plat in sorted(state.get('seen_migration_platforms', [])):
            migrations.append({'date': stamp, 'platform': plat, 'change': 'discovered_surface', 'detail': 'Auto-discovered platform surface'})
    write_json(MIGRATIONS_PATH, migrations)
    state['area_snapshot'] = current_area
    state['seen_migration_platforms'] = sorted(seen_platforms)
    state['migration_events'] = migrations

    # StyxNet profile surfaces.
    styxnet_profiles = []
    if STYXNET_RAW.exists():
        next_p = 1
        for item in state['styxnet_profiles'].values():
            m = re.search(r'(\d+)$', item.get('id', ''))
            if m:
                next_p = max(next_p, int(m.group(1)) + 1)
        existing_profiles = set(state['styxnet_profiles'])
        for row in csv.DictReader(STYXNET_RAW.open(newline='', encoding='utf-8')):
            if row.get('status') not in {'200', '206', '204'}:
                continue
            url = (row.get('url') or '').strip()
            key = norm_url(url)
            if not key or key in existing_profiles:
                continue
            if any(marker in key for marker in ('/search', 'search?', 'keywords=', 'author=', '?q=', '&q=', 'query=', 'filter?search', '/find?', 'search-index')):
                continue
            pid = f'P{next_p:03d}'
            next_p += 1
            state['styxnet_profiles'][key] = {
                'id': pid,
                'url': url,
                'platform': (row.get('platform') or '').strip(),
                'first_seen': stamp,
                'last_seen': stamp,
            }
            existing_profiles.add(key)
        styxnet_profiles = sorted(state['styxnet_profiles'].values(), key=lambda x: x['id'])
    write_json(STYXNET_PROFILES_PATH, styxnet_profiles)

    # Potential claims: OSINT, rebrands, migration, candidate handles.
    potential = state['potential_claims']
    next_claim = next_id('P', list(potential.values()))
    def add_claim(claim, ctype, confidence, basis, source):
        nonlocal next_claim
        key = nkey(claim)
        if not key or key in potential:
            return False
        potential[key] = {
            'id': next_claim,
            'claim': claim,
            'type': ctype,
            'confidence': confidence,
            'basis': basis,
            'source': source,
            'first_seen': stamp,
        }
        next_claim = f'P{int(next_claim[1:]) + 1:03d}'
        return True

    added_claims = 0
    for finding in osint_findings:
        if int(finding.get('confidence') or 0) < 70:
            continue
        claim = f"Potential UTTP-linked handle observed: {finding.get('similar_username') or finding.get('username')} on {finding.get('platform')} ({finding.get('url')})"
        if add_claim(claim, 'potential', 'D/S', 'Auto-discovered from StyxNet OSINT; not ownership-confirmed.', finding.get('url', '')):
            added_claims += 1
    for rebrand in rebrands:
        claim = f"Potential rebrand or alias observed: {rebrand['name']} linked to {rebrand['entity_id']}."
        if add_claim(claim, 'potential', 'D', 'Auto-derived from General List v2 name-token matching.', 'General List v2'):
            added_claims += 1
    if STYXNET_CANDIDATES.exists():
        for row in csv.DictReader(STYXNET_CANDIDATES.open(newline='', encoding='utf-8')):
            claim = f"Candidate handle observed: {row.get('handle')} ({row.get('classification')}) on {row.get('platforms')}."
            if add_claim(claim, 'potential', row.get('confidence', 'D/S'), 'StyxNet handle candidate; structural only, not ownership-confirmed.', 'styxnet_handle_candidates.csv'):
                added_claims += 1
    potential_claims = sorted(potential.values(), key=lambda x: x['id'])
    write_json(CLAIMS_PATH, potential_claims)

    # Watch leads.
    watchlist = state['discovered_watchlist']
    next_watch = next_id('W', list(watchlist.values()))
    def add_watch(name, wtype, status, confidence, indicators, limits):
        nonlocal next_watch
        key = nkey(name)
        if not key or key in watchlist:
            return False
        watchlist[key] = {
            'id': next_watch,
            'name': name,
            'type': wtype,
            'status': status,
            'confidence': confidence,
            'watch_indicators': indicators,
            'limits': limits,
            'first_seen': now(),
        }
        next_watch = f'W{int(next_watch[1:]) + 1:03d}'
        return True

    added_watch = 0
    for finding in osint_findings:
        if int(finding.get('confidence') or 0) < 70:
            continue
        name = f"{finding.get('platform')} handle cluster ({finding.get('similar_username') or finding.get('username')})"
        if add_watch(name, 'discovered handle cluster', 'intake', 'D/S', 'Auto-discovered from StyxNet OSINT.', 'Public handle lead; not ownership-confirmed.'):
            added_watch += 1
    for rebrand in rebrands:
        if add_watch(rebrand['name'], 'rebrand lead', 'watch', 'D', 'Name-token match to a tracked entity.', 'Unverified alias or rebrand.'):
            added_watch += 1
    if STYXNET_CANDIDATES.exists():
        for row in csv.DictReader(STYXNET_CANDIDATES.open(newline='', encoding='utf-8')):
            if add_watch(row.get('handle', ''), 'candidate handle', 'watch', row.get('confidence', 'D/S'), row.get('classification', ''), 'Structural candidate; not ownership-confirmed.'):
                added_watch += 1
    discovered_watchlist = sorted(watchlist.values(), key=lambda x: x['id'])
    write_json(WATCHLIST_PATH, discovered_watchlist)

    # Tactical indicators.
    tactics = state['discovered_tactics']
    def add_tactic(label):
        key = nkey(label)
        if not key or key in tactics:
            return False
        tactics[key] = label
        return True

    added_tactics = 0
    for label in ('username enumeration', 'similar-username discovery', 'mention scan', 'exact profile discovery', 'platform probing', 'rebrand tracking', 'platform migration'):
        if add_tactic(label):
            added_tactics += 1
    if STYXNET_CANDIDATES.exists():
        for row in csv.DictReader(STYXNET_CANDIDATES.open(newline='', encoding='utf-8')):
            if add_tactic(row.get('classification', '')):
                added_tactics += 1
    for finding in osint_findings:
        for value in (finding.get('detection_in') or []):
            if add_tactic(str(value).replace('_', ' ')):
                added_tactics += 1
        if finding.get('search_type'):
            if add_tactic(f"{finding.get('search_type')} profile discovery"):
                added_tactics += 1
    discovered_tactics = sorted(tactics.values())
    write_json(TACTICS_PATH, discovered_tactics)

    # Discovery events: append only when a category grows.
    events = state['discovery_events']
    previous = state.get('previous_counts') or {}
    current_counts = {
        'discovered_sources': len(discovered),
        'styxnet_profiles': len(styxnet_profiles),
        'osint_findings': len(osint_findings),
        'discovered_areas': len(discovered_areas),
        'potential_claims': len(potential_claims),
        'discovered_watchlist': len(discovered_watchlist),
        'discovered_tactics': len(discovered_tactics),
        'migration_events': len(migrations),
        'rebrands': len(rebrands),
    }
    event_specs = [
        ('discovered_sources', 'source discovery', 'New source URLs discovered.'),
        ('styxnet_profiles', 'StyxNet profile discovery', 'New StyxNet profile surfaces discovered.'),
        ('osint_findings', 'OSINT collection', 'New StyxNet OSINT findings collected.'),
        ('discovered_areas', 'area discovery', 'New platform surfaces mapped.'),
        ('potential_claims', 'claim discovery', 'New potential claims identified.'),
        ('discovered_watchlist', 'watchlist discovery', 'New watch leads identified.'),
        ('discovered_tactics', 'tactic discovery', 'New tactical indicators identified.'),
        ('migration_events', 'migration detection', 'New platform surface changes detected.'),
        ('rebrands', 'rebrand discovery', 'New rebrand or alias leads identified.'),
    ]
    for key, etype, detail in event_specs:
        if current_counts[key] > previous.get(key, 0):
            events.append({'date': stamp, 'type': etype, 'detail': detail, 'count': current_counts[key], 'delta': current_counts[key] - previous.get(key, 0)})
    state['discovery_events'] = events
    write_json(EVENTS_PATH, events)
    state['previous_counts'] = current_counts

    state['files'] = files
    state['last_run'] = stamp
    STATE_PATH.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')

    print(json.dumps({
        'scanned_files': len(files),
        'new_sources': added_sources,
        'discovered_sources_total': len(discovered),
        'rebrands': len(rebrands),
        'migration_events': len(migrations),
        'styxnet_profiles': len(styxnet_profiles),
        'discovered_areas': len(discovered_areas),
        'potential_claims': len(potential_claims),
        'discovered_watchlist': len(discovered_watchlist),
        'discovered_tactics': len(discovered_tactics),
        'discovery_events': len(events),
    }, indent=2))


if __name__ == '__main__':
    main()

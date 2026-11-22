"""Accuracy scoring for verified domain links.

The score is not ownership. It measures how strongly the page evidence links
the entity handle to the domain, plus source corroboration, stability, and
domain specificity.
"""
from entity_registry import ENTITY_HANDLES

SIGNAL_WEIGHTS = {
    'canonical': 30,
    'jsonld': 30,
    'metadata': 28,
    'redirect': 25,
    'structured': 25,
    'json': 22,
    'json_api': 25,
    'user_activity': 24,
    'microdata': 20,
    'author_meta': 20,
    'rel_author': 20,
    'js_state': 20,
}

GENERIC_DOMAINS = {
    'youtube.com', 'music.youtube.com', 'x.com', 'twitter.com', 'facebook.com',
    'instagram.com', 'tiktok.com', 'reddit.com', 'discord.com', 'discord.gg',
    'telegram.org', 't.me', 'twitch.tv', 'github.com', 'gist.github.com',
    'steamcommunity.com', 'soundcloud.com', 'spotify.com', 'bandcamp.com',
    'pinterest.com', 'tumblr.com', 'threads.net', 'bsky.app', 'mastodon.social',
    'vk.com', 'weibo.com', 'line.me', 'wa.me', 'linktr.ee', 'medium.com',
    'deviantart.com', 'furaffinity.net', 'archiveofourown.org', 'wattpad.com',
    'roblox.com', 'open.spotify.com', 'music.amazon.com',
}

GENERIC_SUFFIXES = (
    'youtube.com', 'x.com', 'twitter.com', 'facebook.com', 'instagram.com',
    'tiktok.com', 'reddit.com', 'discord.com', 'twitch.tv', 'github.com',
    'steamcommunity.com', 'soundcloud.com', 'bandcamp.com', 'tumblr.com',
)


def signals_from_status(status):
    status = status or ''
    if 'ominis-verified (' not in status:
        return set()
    return {x for x in status.split('ominis-verified (', 1)[1].split(')', 1)[0].split('+') if x}


def _int(value, default=1):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _urls(value):
    return [u for u in (value or '').split(';') if u]


def _sources(value):
    return {x.strip() for x in (value or '').split('+') if x.strip()}


def _specificity(row, handle):
    domain = (row.get('domain') or '').lower().lstrip('www.')
    platform = (row.get('platform') or '').lower()
    if domain in GENERIC_DOMAINS or any(domain.endswith('.' + s) for s in GENERIC_SUFFIXES):
        return 40
    labels = domain.split('.')
    if handle and any(handle in label for label in labels):
        return 90
    if domain.count('.') >= 2 and handle and domain.startswith(handle + '.'):
        return 90
    if platform and platform not in ('unknown', 'web'):
        return 72
    return 62


def score_domain(row):
    source = row.get('source') or ''
    entity = row.get('entity_id') or ''
    handle = ENTITY_HANDLES.get(entity, '')
    signals = signals_from_status(row.get('validation_status'))
    if source == 'User-provided' or row.get('entity_match') == 'user-verified':
        return {
            'accuracy_score': 100,
            'accuracy_level': 'User-verified',
            'accuracy_types': 'linkage:user-verified;corroboration:user-provided',
            'linkage_score': 100,
            'corroboration_score': 100,
            'stability_score': 100,
            'specificity_score': 100,
        }

    linkage = min(100, 50 + sum(SIGNAL_WEIGHTS.get(s, 8) for s in signals)) if signals else 0
    occ = max(1, _int(row.get('occurrences')))
    alt = len(_urls(row.get('alternate_urls')))
    source_count = len(_sources(source))
    corroboration = min(100, min(40, occ * 8) + min(30, source_count * 15) + min(30, alt * 15))

    status_ok = str(row.get('status') or '') in {'200', '206', '204'}
    stability = (70 if status_ok else 20)
    if 'canonical' in signals:
        stability += 5
    if 'redirect' in signals:
        stability += 10
    if occ > 1:
        stability += 5
    stability = min(100, stability)

    specificity = _specificity(row, handle)
    overall = round(linkage * 0.55 + corroboration * 0.20 + stability * 0.15 + specificity * 0.10)
    if overall >= 85:
        level = 'Corroborated'
    elif overall >= 72:
        level = 'Confirmed'
    elif overall >= 55:
        level = 'Linkage-confirmed'
    elif overall >= 45:
        level = 'Provisional'
    else:
        level = 'Weak'

    types = []
    types.append('linkage:multi-signal' if len(signals) >= 2 else 'linkage:single-signal')
    if source_count > 1:
        types.append('corroboration:multi-source')
    elif occ > 1 or alt:
        types.append('corroboration:repeat-observation')
    else:
        types.append('corroboration:single-record')
    types.append('stability:canonical' if 'canonical' in signals else 'stability:http')
    types.append('specificity:unique-domain' if specificity >= 80 else 'specificity:platform')

    return {
        'accuracy_score': overall,
        'accuracy_level': level,
        'accuracy_types': ';'.join(types),
        'linkage_score': linkage,
        'corroboration_score': corroboration,
        'stability_score': stability,
        'specificity_score': specificity,
    }

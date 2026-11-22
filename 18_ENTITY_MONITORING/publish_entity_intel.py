#!/usr/bin/env python3
"""Publish organized per-entity intelligence folders to the GitHub archive.

This is a periodic mirror, not a real-time sync. It writes one folder per
group-level entity, then makes at most one git commit/push per run. GitHub API
rate limits are checked before any push and the token is never logged.
"""
import json
import os
import random
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
DATA = BASE / 'entity-intelligence.json'
OUT = ROOT / '19_ENTITY_INTEL_PUBLISH'
MIN_CORE_REMAINING = 200
COMMIT_MESSAGE = 'Update per-entity intelligence mirror'


def now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def run(cmd, **kw):
    env = os.environ.copy()
    env.update({'GIT_TERMINAL_PROMPT': '0', 'GH_PROMPT_DISABLED': '1'})
    return subprocess.run(cmd, cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=120, **kw)


def redact(text):
    return re.sub(r'(gh[pousr]_[A-Za-z0-9]+)', '<redacted>', text or '')


def rate_limit():
    try:
        r = run(['gh', 'api', 'rate_limit', '--jq', '.resources.core'])
        if r.returncode != 0:
            return None
        return json.loads(r.stdout.strip())
    except Exception:
        return None


def source_map(data):
    return {s['id']: s for s in data.get('sources', [])}


def claims_for(entity, claims):
    name = (entity.get('name') or '').lower()
    eid = entity.get('id') or ''
    out = []
    for c in claims:
        src = str(c.get('source', ''))
        text = str(c.get('claim', ''))
        if eid in src or name in text.lower() or any(r in src for r in entity.get('related', [])):
            out.append(c)
    return out


def write_entity(entity, data, sources):
    folder = OUT / entity['id']
    folder.mkdir(parents=True, exist_ok=True)
    srcs = [sources.get(sid, {'id': sid, 'name': 'unknown'}) for sid in entity.get('sources', [])]
    claims = claims_for(entity, data.get('claims', []))
    record = {
        'id': entity.get('id'),
        'name': entity.get('name'),
        'type': entity.get('type'),
        'status': entity.get('status'),
        'confidence': entity.get('confidence'),
        'summary': entity.get('summary'),
        'origin': entity.get('origin'),
        'current_state': entity.get('current_state'),
        'watch_priority': entity.get('watch_priority'),
        'related': entity.get('related', []),
        'tactics': entity.get('tactics', []),
        'areas': entity.get('areas', []),
        'evolution': entity.get('evolution', []),
        'sources': srcs,
        'claims': claims,
        'not_supported': entity.get('not_supported', []),
        'learning': entity.get('learning', {}),
        'published': now(),
    }
    (folder / 'record.json').write_text(json.dumps(record, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    lines = [
        f"# {entity.get('name')}",
        '',
        f"- **ID:** `{entity.get('id')}`",
        f"- **Type:** {entity.get('type')}",
        f"- **Status:** {entity.get('status')}",
        f"- **Confidence:** {entity.get('confidence')}",
        f"- **Watch priority:** {entity.get('watch_priority')}",
        f"- **Origin:** {entity.get('origin')}",
        '',
        f"> {entity.get('summary')}",
        '',
        f"**Current state:** {entity.get('current_state')}",
        '',
        '## Tactics',
        '',
    ]
    lines += [f"- {x}" for x in entity.get('tactics', [])] or ['- None recorded']
    lines += ['', '## Areas', '']
    lines += [f"- {x}" for x in entity.get('areas', [])] or ['- None recorded']
    lines += ['', '## Related', '', ', '.join(entity.get('related', [])) or 'None']
    lines += ['', '## Evolution', '']
    for ev in entity.get('evolution', []):
        lines.append(f"- **{ev.get('date')}** — {ev.get('event')} ({ev.get('confidence')})")
    lines += ['', '## Sources', '', '| ID | Source | Confidence |', '| --- | --- | --- |']
    for s in srcs:
        lines.append(f"| {s.get('id')} | {s.get('name')} | {s.get('confidence')} |")
    lines += ['', '## Claims', '']
    for c in claims:
        lines.append(f"- **{c.get('id')} ({c.get('type')}, {c.get('confidence')})** — {c.get('claim')}")
    lines += ['', '## Not supported', '']
    lines += [f"- {x}" for x in entity.get('not_supported', [])] or ['- None recorded']
    lines += ['', '## Learning model', '', '```json', json.dumps(entity.get('learning', {}), indent=2), '```', '']
    (folder / 'README.md').write_text('\n'.join(lines), encoding='utf-8')


def write_index(data):
    OUT.mkdir(parents=True, exist_ok=True)
    index = []
    for e in data.get('entities', []):
        index.append({k: e.get(k) for k in ['id', 'name', 'type', 'status', 'confidence', 'watch_priority']})
    (OUT / 'INDEX.json').write_text(json.dumps(index, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    lines = ['# Per-Entity Intelligence Mirror', '', f"Last generated: {now()}", '', '| Entity | Type | Status | Confidence | Folder |', '| --- | --- | --- | --- | --- |']
    for e in index:
        lines.append(f"| [{e['name']}]({e['id']}/README.md) | {e['type']} | {e['status']} | {e['confidence']} | `{e['id']}/` |")
    lines += ['', 'Group-level intelligence only. No target list, no private identifiers.', '']
    (OUT / 'README.md').write_text('\n'.join(lines), encoding='utf-8')


def git_has_changes():
    r = run(['git', 'status', '--porcelain'])
    return bool(r.stdout.strip())


def git_commit_push():
    r = run(['git', 'add', '-A'])
    if r.returncode != 0:
        return {'pushed': False, 'reason': 'git add failed: ' + redact(r.stderr)}
    r = run(['git', 'diff', '--cached', '--quiet'])
    if r.returncode == 0:
        return {'pushed': False, 'reason': 'no changes'}
    r = run(['git', 'commit', '-m', COMMIT_MESSAGE])
    if r.returncode != 0:
        return {'pushed': False, 'reason': 'git commit failed: ' + redact(r.stderr)}
    rl = rate_limit()
    if not rl:
        return {'pushed': False, 'reason': 'rate limit unavailable', 'committed': True}
    remaining = int(rl.get('remaining', 0))
    if remaining < MIN_CORE_REMAINING:
        return {'pushed': False, 'reason': f'rate limit low ({remaining})', 'committed': True, 'rate_limit': rl}
    time.sleep(random.uniform(1.0, 3.0))
    r = run(['git', 'push', 'origin', 'main'])
    if r.returncode != 0:
        return {'pushed': False, 'reason': 'git push failed: ' + redact(r.stderr), 'committed': True, 'rate_limit': rl}
    return {'pushed': True, 'rate_limit': rl}


def main():
    data = json.loads(DATA.read_text(encoding='utf-8'))
    sources = source_map(data)
    for entity in data.get('entities', []):
        write_entity(entity, data, sources)
    write_index(data)
    run([sys.executable, str(BASE / 'update_manifest.py')])
    result = {'generated': len(data.get('entities', [])), 'updated': now()}
    if git_has_changes():
        result.update(git_commit_push())
    else:
        result['pushed'] = False
        result['reason'] = 'no changes'
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

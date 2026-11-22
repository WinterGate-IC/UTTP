#!/usr/bin/env python3
import subprocess, sys
from pathlib import Path
BASE = Path(__file__).resolve().parent
steps = [
 [sys.executable, str(BASE / 'discover.py')],
 [sys.executable, str(BASE / 'strict_validate.py')],
 [sys.executable, str(BASE / 'monitor.py')],
 [sys.executable, str(BASE / 'styxnet_osint.py')],
 [sys.executable, str(BASE / 'build_entity_intelligence.py')],
 [sys.executable, str(BASE / 'build_domains.py')],
 [sys.executable, str(BASE / 'update_manifest.py')],
]
for step in steps:
    print('RUN', ' '.join(step))
    subprocess.run(step, check=True)
print('PIPELINE OK')

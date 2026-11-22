#!/usr/bin/env bash
set -euo pipefail
LOCK=/var/tmp/opencode/entity-pipeline.lock
exec 9>"$LOCK"
if ! flock -n 9; then
  echo "entity pipeline already running; skipping"
  exit 0
fi
set -a
source /opt/tel/.env
set +a
cd /var/tmp/opencode/O9A-work
DIR=18_ENTITY_MONITORING
/usr/bin/python3 "$DIR/discover.py" >/var/tmp/opencode/discover.log 2>&1
/usr/bin/python3 "$DIR/strict_validate.py" >/var/tmp/opencode/strict-validate.log 2>&1
/usr/bin/python3 "$DIR/monitor.py" >/var/tmp/opencode/monitor.log 2>&1
/usr/bin/python3 "$DIR/styxnet_osint.py" >/var/tmp/opencode/styxnet-osint.log 2>&1
/usr/bin/python3 "$DIR/fill_tel.py" >/var/tmp/opencode/fill-tel.log 2>&1
/usr/bin/python3 "$DIR/sync_tel_intake.py" >/var/tmp/opencode/sync-tel-intake.log 2>&1
if [ "${OMINIS_DISCOVER:-1}" = "1" ]; then
  /usr/bin/python3 "$DIR/ominis_discover.py" --budget "${OMINIS_DISCOVER_BUDGET:-1}" --concurrency "${OMINIS_DISCOVER_CONCURRENCY:-8}" >/var/tmp/opencode/ominis-discover.log 2>&1 || true
fi
if [ "${OMINIS_VALIDATE:-1}" = "1" ]; then
  /usr/bin/python3 "$DIR/ominis_validate.py" --budget "${OMINIS_BUDGET:-40}" --concurrency "${OMINIS_CONCURRENCY:-4}" >/var/tmp/opencode/ominis-validate.log 2>&1 || true
fi
/usr/bin/python3 "$DIR/reclassify_domains.py" >/var/tmp/opencode/reclassify-domains.log 2>&1
/usr/bin/python3 "$DIR/build_entity_intelligence.py" >/var/tmp/opencode/build-json.log 2>&1
/usr/bin/python3 "$DIR/build_domains.py" >/var/tmp/opencode/build-domains.log 2>&1
/usr/bin/python3 /var/tmp/opencode/entity-work/build_page.py >/var/tmp/opencode/build-page.log 2>&1
/usr/bin/python3 "$DIR/cold_storage.py" >/var/tmp/opencode/cold-storage.log 2>&1
/usr/bin/python3 "$DIR/update_manifest.py" >/var/tmp/opencode/update-manifest.log 2>&1
/usr/bin/python3 "$DIR/strict_validate.py" >/var/tmp/opencode/strict-validate-final.log 2>&1
/usr/bin/python3 "$DIR/update_manifest.py" >/var/tmp/opencode/update-manifest.log 2>&1

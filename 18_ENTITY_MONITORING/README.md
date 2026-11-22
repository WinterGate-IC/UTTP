# 18_ENTITY_MONITORING

Single-folder entity intelligence, validation, and overtime monitoring layer.

All monitored entities are group-level records, not people or targets. Every
entity is tracked through the links and registers below:

| What is tracked | Link / file |
| --- | --- |
| Entity register and live page | [`entity-intelligence.json`](entity-intelligence.json) · [Live entity page](https://wintergate.org/entities.html) · [Backend JSON](https://wintergate.org/data/entity-intelligence.json) |
| Area/platform surfaces | [UTTP_AREA_REGISTER.csv](https://github.com/WinterGate-IC/UTTP/blob/main/02_CORE_INVESTIGATION/AREA_INTELLIGENCE/UTTP_AREA_REGISTER.csv) |
| Group/offshoot register | [General_List_v2_Structured_2026-11-19.md](https://github.com/WinterGate-IC/UTTP/blob/main/02_CORE_INVESTIGATION/Members_List/General_List_v2_Structured_2026-11-19.md) |
| Source index | [UTTP_INVESTIGATION_SOURCE_INDEX.json](https://github.com/WinterGate-IC/UTTP/blob/main/10_SOURCES/UTTP_INVESTIGATION_SOURCE_INDEX.json) |
| Validated claims | [VALIDATED_CLAIMS.csv](https://github.com/WinterGate-IC/UTTP/blob/main/15_VALIDATED_CLAIMS/VALIDATED_CLAIMS.csv) |
| Rejected/false claims | [FALSE_CLAIMS.csv](https://github.com/WinterGate-IC/UTTP/blob/main/16_VALIDATED_FALSE_CLAIMS/FALSE_CLAIMS.csv) |
| Tracking board | [TRACKING_BOARD.md](https://github.com/WinterGate-IC/UTTP/blob/main/12_TRACKING/TRACKING_BOARD.md) |
| StyxNet validation | [StyxNet site](https://wintergate.org/styxnet/) · [`strict_validation_summary.json`](strict_validation_summary.json) · [`styxnet_profiles.json`](styxnet_profiles.json) |
| Ominis-OSINT validation | [`ominis_validate.py`](ominis_validate.py) · [Ominis-OSINT](https://github.com/AnonCatalyst/Ominis-OSINT) |
| Internal domain validation queue | [`domain_validation_queue.csv`](domain_validation_queue.csv) — unverified leads only; not published as domain intelligence |
| Backend status feeds | [monitor-feed.json](https://wintergate.org/data/monitor-feed.json) · [tel-intake.json](https://wintergate.org/data/tel-intake.json) · [cold-storage-status.json](https://wintergate.org/data/cold-storage-status.json) |
| TEL threat register | Local TEL API, synced by `fill_tel.py` and `sync_tel_intake.py` |

## Automated flow

1. `discover.py` scans the archive for new source URLs, rebrands, and area
   surface changes; writes `discovered_sources.json`, `rebrands.json`,
   `migration_events.json`, and `discovery_state.json`.
2. `strict_validate.py` validates JSON/CSV/manifest integrity and filters the
   raw StyxNet export into strict/rejected profile sets.
3. `monitor.py` checks public source availability and writes `monitor_feed.json`.
4. `fill_tel.py` pushes the group-level register to TEL.
5. `sync_tel_intake.py` pulls newly listed TEL names into `tel_intake.json` as
   review leads.
6. `ominis_validate.py` automatically re-checks domain leads in small batches
   (default 40 per run) using Ominis-OSINT page reads. It requires a strong
   signal (metadata, canonical, redirect, embedded JSON, or structured data);
   HTTP 200 alone is not accepted, and visible-body-only matches stay
   unverified. Disable with `OMINIS_VALIDATE=0`; tune with `OMINIS_BUDGET` and
   `OMINIS_CONCURRENCY`.
7. `reclassify_domains.py` keeps only Ominis-verified or user-verified rows in
   `22_UTTP_DOMAINS/DOMAINS_REGISTER.csv`. Unverified leads move to the internal
   `domain_validation_queue.csv` and are not published in the domain archive or
   Explore tab. Per-entity domain CSVs and the summary contain verified rows
   only.
8. `build_entity_intelligence.py` rebuilds `entity-intelligence.json` from the
   registers, sources, claims, areas, discovery outputs, and validation state.
9. `cold_storage.py` writes hashed compressed snapshots under
   `/var/lib/wintergate/cold_storage/`.
10. `publish_entity_intel.py` writes one folder per entity under
    `19_ENTITY_INTEL_PUBLISH/`, refreshes the manifest, and pushes at most once
    every 6 hours after checking the GitHub rate limit.
11. `update_manifest.py` regenerates `00_READ_FIRST/MANIFEST.csv` and its SHA-256.

This is the backend of record; the GitHub repository is an archive mirror. Run everything with `bash run_pipeline.sh`.

## Evidence and safety boundary

Evidence is SHA-256 hashed in the manifest and preserved in cold storage.
Records survive deletion, migration, and abandonment. Claims are labelled as
validated, assessed, alleged, or rejected. Offshoots and new brands are tracked
against behaviour and platform surfaces, not identity. This is monitoring and
documentation only: no target list, no private identifiers, no contact or
infiltration instruction.

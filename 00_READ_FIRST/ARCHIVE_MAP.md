# Archive Map

This is the navigation map for the reorganized archive. Every original file is
preserved; only top-level placement changed.

---

## 00_READ_FIRST

| File | Use |
| --- | --- |
| `START_HERE.md` | Entry point, warnings, reading order. |
| `ARCHIVE_MAP.md` | This map. |
| `READING_ORDER.md` | Paths for journalists, researchers, platforms, and authorities. |
| `TIMELINE.md` | Dated events with confidence labels. |
| `ENTITY_MAP.md` | Group-level relationship map. |
| `CLAIM_LEDGER.md` | Claim-by-claim accuracy review and corrections. |
| `DATA_DICTIONARY.md` | File formats and fields. |
| `GLOSSARY.md` | Terms used in the archive. |
| `PATH_MAP.md` | Old path → new path for external links. |
| `CHANGELOG.md` | What changed in this pass. |
| `MANIFEST.csv` | Size and SHA-256 for every archived file. |

---

## 01_ARCHIVE_RELEASE

`6GB_Public_Archive/Release_2026-09-19/`

The public release notice, download pointer, supplier notice, and audience
warning. **The public release is 6 GB.** The “10 GB total / 4 GB pending” wording
in older copies is superseded by the correction ledger.

---

## 02_CORE_INVESTIGATION

| Subfolder | Contents |
| --- | --- |
| `Historical/` | WIC dossiers, historical records, 764/O9A hierarchy analysis, Operation Crown Drop record. |
| `Tactics/` | Tactical analysis of UTTP and 764 methods, burner profiles. |
| `Observations/` | Phase 1 reception/observation report. |
| `Members_List/` | Entity/alias registry, indicator lists, burner profile material, the structured General List v2, and the expanded members/groups register. |
| `AREA_INTELLIGENCE/` | 200-row platform/surface register of UTTP areas; no handles or account IDs. |
| `Defenders/` | Material about people or accounts that defended UTTP or disputed the archive. |

---

## 03_AFFILIATIONS

Grouped by named network or community:

- `148-1488/` — 148corps material, archives, screenshots, exports.
- `764/` — placeholder/lead folder for 764 material.
- `FPE - Fundamental Paper Education/` — FPE ecosystem assessment and branding/infiltration notes.
- `SPWN - Spawnism/` — placeholder/lead folder.
- `SRA - Spam Report Army/` — screenshots and README.
- `TM-TNM - The Militia/` — 2025 investigation, exports, media, Discord captures.
- `UETR-GSR - Imperium of Enclave/` — UID lists and related material.
- `UU - Universal Union/` — images, videos, propaganda material.

## 04_OFFSHOOTS

- `11th STREET/` — unverified lead, explicitly marked.
- `DPOS - Degeneracy Police Order State/` — DPOS 2025 material, UTTP/DPOS targeting document, and `ANALYSIS/DPOS_DEEP_DIVE_2026-11-19.md`.

## 05_PARENT_ENTITIES

- `09A Cult/` — data sheet, images, and a new `README.md` explaining that
  "09A Cult" is a legacy archive label, not a central O9A headquarters. See
  `14_O9A_764_TRACE/` for the sourced O9A profile.

## 06_COMMUNITY_NOTES

- `Endorsements/` — AUTTP endorsement document.
- `Petitions/` — AUTTP petition support document.
- `SOYJAK WIKI/` — response to a Soyjak Wiki rebrand narrative.
- `README.md` — community context and standards.

## 07_DONATED_DOCUMENTS

Donated text notes, links, supplementary intelligence, and videos. Treat
donated material as **lead evidence**, not automatically verified fact.

## 08_DTAD_2025

DTAD 2025 datasets: malicious Discord server lists, user exports, global
blacklist snapshot. These are bulk exports; read the data dictionary before
parsing.

## 09_STYXNET_REPORTS

StyxNet CSV/PDF/Markdown exports and the deep-recon identity-mapping report.

`validation/` contains the 2026-11-19 accuracy pass:

- `STYXNET_VALIDATION_2026-11-19.md` — counts, corrections, limits.
- `styxnet_platform_name_blocklist.csv` — 47 platform variants (37 normalized keys).
- `styxnet_handle_candidates.csv` — 15 structural candidates, not ownership-confirmed.
- `styxnet_handle_class_counts.csv` — 54 unique handle values by class.
- `styxnet_row_class_counts.csv` — 823 rows by structural class.
- `styxnet_validation_summary.json` — machine-readable counts and raw SHA-256.
- `validate_styxnet.py` — reproducible review script.

## 10_SOURCES

- `UTTP_INVESTIGATION_SOURCE_INDEX_ANALYSIS.md`
- `UTTP_INVESTIGATION_SOURCE_INDEX.json`
- `UTTP_AFFILIATED_NETWORKS_LAW_ENFORCEMENT_SOURCES.json`

These are source maps. A link existing in the JSON does not mean the claim it
supports has been independently verified by WIC; see the source index's own
verification notice.

## 11_RESEARCH_EXPANSION

New public-source research added in the 2026-11-19 pass:

- `README.md` — scope and standards.
- `UTTP_THREAT_LANDSCAPE_2026.md` — current landscape, structure, tactics, and confidence labels.
- `SOURCE_LEDGER_2026.md` — source-by-source table.
- `FPE_CROWN_OPERATION.md` — WIC's own FPE record, separated from independent findings.
- `VERIFICATION_QUEUE.md` — claims that still need primary-source confirmation.
- `OPEN_QUESTIONS.md` — research gaps.

---

## 12_TRACKING

Group-level tracking product added 2026-11-19:

- `README.md` — scope, non-negotiables, headline.
- `SNAPSHOT_2026-11-19.md` — current assessment.
- `TRACKING_REGISTER.csv` — group/faction register.
- `TRACKING_BOARD.md` — operational watch board.
- `COLLECTION_PLAN.md` — ethical public-source collection.
- `OPEN_LEADS.md` — gaps and verification priorities.
- `INBOX/` — drop folder for new group-level tracking notes and template.
- `METHODS/` — method tracker (group-level tactics, not people).

No private individuals and no individual tracking.

## 13_UTTP_764_OVERLAP

Dedicated UTTP and 764 profiles plus the evidence test for overlap:

- `UTTP_FULL_PROFILE.md` — history, structure, factions, methods, targets.
- `764_PROFILE.md` — designation, structure, victim pattern, legal record.
- `TACTIC_OVERLAP_MATRIX.md` — tactic-by-tactic comparison.
- `EVIDENCE_AND_LIMITS.md` — what is proven, assessed, or unsupported.
- `ANALYSIS_2026.md` — why the overlap matters.
- `SOURCES.md` — source list.

## 14_O9A_764_TRACE

Dedicated trace from 764 to the Order of Nine Angles, added 2026-11-19:

- `README.md` — purpose, bottom line, reading order.
- `O9A_FULL_PROFILE.md` — names, origins, structure, ideology, designations.
- `764_TO_O9A_TRACE.md` — the sourced nexus/nexion finding and its limits.
- `O9A_STRUCTURE_AND_IDEOLOGY.md` — nexions, acolytes/adherents, radicalisation logic.
- `DESIGNATIONS_AND_LEGAL.md` — NZ and Canada instruments; what is not designated.
- `EVIDENCE_AND_LIMITS.md` — claim-by-claim confidence and corrections.
- `TIMELINE.md` — dated events.
- `SOURCES.md` — primary and independent sources.

## 15_VALIDATED_CLAIMS

Approved claims that survived source review:

- `README.md` — confidence key and rules.
- `SUMMARY.md` — short topic summary.
- `VALIDATED_CLAIMS.csv` — machine-readable register.

## 16_VALIDATED_FALSE_CLAIMS

Quarantine for false/superseded claims removed from analysis documents:

- `README.md` — handling rules.
- `FALSE_CLAIMS.csv` — machine-readable register.
- `QUARANTINE.md` — grouped rejected claims and approved replacements.

## 17_CURRENT_STATE_PACKAGE

Short, separate handoff product for platforms, researchers, and authorities:

- `README.md` — scope and headline.
- `UTTP_CURRENT_STATE_2026-11-19.md` — 2–5 page current-state assessment.
- `HANDOFF_BRIEF.md` — platform/authority priorities.
- `EVIDENCE_PACK.md` — key claims and limits.
- `OFFSHOOT_WATCHLIST.csv` — 2026 offshoot/campaign watchlist.
- `METRICS.md` — how to measure pressure and success.

## 18_ENTITY_MONITORING

Single-folder entity intelligence, validation, and overtime monitoring layer:

- `README.md` — monitored-entity links, flow, and safety boundary.
- `entity-intelligence.json` — entities, areas, sources, claims, watchlist, evolution model.
- `build_entity_intelligence.py` — rebuilds the JSON from archive registers.
- `discover.py` — incremental source/rebrand/migration discovery.
- `strict_validate.py` — manifest/JSON/CSV and StyxNet strict validation.
- `monitor.py` — lightweight StyxNet/source watch feed.
- `styxnet_osint.py` — passive StyxNet username-hunt poller and OSINT findings.
- `fill_tel.py` / `sync_tel_intake.py` — TEL register sync and intake leads.
- `cold_storage.py` — hashed compressed snapshots.
- `run_pipeline.py` / `run_pipeline.sh` — automated pipeline.
- Validation/monitoring outputs: `strict_validation_summary.json`, `archive_integrity.json`, `monitor_feed.json`, `tel_intake.json`, `cold_storage_status.json`.

## 19_ENTITY_INTEL_PUBLISH

GitHub mirror of per-entity intelligence, generated by
`18_ENTITY_MONITORING/publish_entity_intel.py`:

- `README.md` / `INDEX.json` — index of every monitored entity.
- `<ENTITY_ID>/README.md` — human-readable entity record.
- `<ENTITY_ID>/record.json` — structured group-level record.

The mirror updates at most once every 6 hours through a locked, rate-limited
cron job. It uses git push rather than per-file API writes, checks the GitHub
rate limit before pushing, and never logs the token.

## Root files

- `README.md` — public front page and warnings.
- `LICENSE` — repository license.

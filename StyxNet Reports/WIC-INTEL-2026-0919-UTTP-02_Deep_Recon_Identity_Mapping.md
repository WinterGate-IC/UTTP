# WINTERGATE-IC — STYXNET DEEP RECONNAISSANCE
## UTTP Identity Mapping & Source Intelligence Report

[![Document](https://img.shields.io/badge/Document-WIC-INTEL--2026--0919--UTTP--02-blue)]()
[![Classification](https://img.shields.io/badge/Classification-Internal%20%E2%80%94%20Analytical-orange)]()
[![Status](https://img.shields.io/badge/Status-Active-green)]()
[![Target](https://img.shields.io/badge/Target-UTTP-red)]()

---

## 1. EXECUTIVE SUMMARY

This document consolidates all validated intelligence gathered through StyxNet username enumeration, cross-platform handle extraction, and open-source intelligence research against the target UTTP (UTubeTrollPolice / UTubeTrollPolice).

**Total validated handles:** 22
**Total confirmed platforms:** 8
**Total associated individuals identified:** 15+
**Total source references:** 20+

The raw extraction produced approximately 145 handle candidates. After applying strict validation rules (documented in [Section 3](#3-validation-methodology)), **22 handles** were confirmed as UTTP-aligned. The remaining entries were platform names, field labels, random strings, and substring collisions — documented in [Section 7](#7-rejected-findings).

A **seven-handle Bluesky cluster** with rank-based naming was identified and confirmed as a likely coordinated sock network.

---

## 2. DOCUMENT METADATA

| Field | Value |
|---|---|
| **Document ID** | `WIC-INTEL-2026-0919-UTTP-02` |
| **Classification** | Internal — Analytical |
| **Analyst** | WIC Threat Research |
| **Source** | StyxNet Username Search, OSINT cross-referencing |
| **Date** | 2026-09-19 |
| **Target** | UTTP (UtubeTrollPolice / UTubeTrollPolice) |
| **Also Known As** | Union of Troons, Tinkers, and Pedophiles (derogatory) |
| **Founded** | February 12-13, 2011 |
| **Founder** | Thomas Parkinson (Tommy Parky / southparkstudiosable) |
| **Active Platforms** | YouTube, Discord, Bluesky, Tumblr, Mastodon, X |

---

## 3. VALIDATION METHODOLOGY

### 3.1 Validation Rules

| Rule | Requirement |
|---|---|
| **V1** | Handle must be user-owned (actual username, profile URL, or user JSON field) |
| **V2** | Handle must not be a substring collision (e.g., "uttp" inside "buttplug") |
| **V3** | Handle must not match known third-party developers |
| **V4** | Handle must not be a generic field label |
| **V5** | Handle must not be a random string (nonce, hash) |
| **V6** | Handle must exhibit UTTP brand or faction patterning |
| **V7** | Handle must be corroborated or cluster-matched |

### 3.2 Confidence Tiers

| Tier | Definition | Confidence |
|---|---|---|
| **Tier 1** | Contains UTTP as standalone token or faction brand | **HIGH** for brand alignment |
| **Tier 2** | Belongs to structured cluster on same platform | **MEDIUM-HIGH** for common operator |
| **Tier 3** | Matches naming but single-source | **LOW-MEDIUM** — requires verification |

---

## 4. TIER 1 — CONFIRMED BRAND-ALIGNED HANDLES

### 4.1 `uttp.tumblr.com`

| Field | Value |
|---|---|
| **Platform** | Tumblr |
| **Type** | Direct subdomain |
| **Validation** | V1, V6 |
| **Notes** | User-registered subdomain. Direct UTTP-owned presence. |

### 4.2 `UTTP_OFFICAL`

| Field | Value |
|---|---|
| **Platform** | Multiple |
| **Type** | Brand handle (misspelled "OFFICAL") |
| **Validation** | V6 |
| **Notes** | The misspelling is a distinctive UTTP marker. Consistent across platforms. |

### 4.3 `UTTPmastdept`

| Field | Value |
|---|---|
| **Platform** | Mastodon |
| **Type** | Faction handle ("UTTP Mastodon Department") |
| **Validation** | V6 |
| **Notes** | Department naming implies organizational structure. |

### 4.4 `frickfunnymikeuttpthtdc`

| Field | Value |
|---|---|
| **Platform** | Mastodon (`mastodon.social`) |
| **Type** | Faction handle (UTTP + THTDC) |
| **Validation** | V6 |
| **Notes** | THTDC = "The Hellfire Demonic Trolling Company" — a UTTP faction . |

### 4.5 `kiloratstrzntputtp.bsky.social`

| Field | Value |
|---|---|
| **Platform** | Bluesky |
| **Type** | Multi-faction handle (KiloRat + STR + ZNTP + UTTP) |
| **Validation** | V2, V6, V7 |
| **Notes** | Combines four faction tokens. **Strongest faction-naming signal in extraction.** |

---

## 5. TIER 2 — STRUCTURED CLUSTER (BLUESKY SOCK NETWORK)

Seven handles on Bluesky share a consistent naming structure characteristic of a single operator or coordinated group.

| Handle | Pattern |
|---|---|
| `uttparkrosie.bsky.social` | UTTP + name |
| `michaelsuttptv.bsky.social` | "Michael's UTTP TV" + name |
| `uttpalette.bsky.social` | UTTP + concept |
| `kiloratstrzntputtp.bsky.social` | Multi-faction + UTTP |
| `uttpofficercoplord.bsky.social` | UTTP + rank (officer) + role (coplord) |
| `uttp-lieutenant2.bsky.social` | UTTP + rank (lieutenant) + number |
| `uttpus.bsky.social` | UTTP + collective (us) |

### 5.1 Cluster Observations

- **Rank Naming:** Two handles use military/police rank titles (`officer`, `lieutenant`), consistent with UTTP's "Degeneracy Police Order State" (DPOS) branding.
- **Named Operator:** `michaelsuttptv.bsky.social` references "Michael" — owner of "Michael's UTTP TV Studios", joined Bluesky March 2026, 310 followers, 445 following.
- **Cluster Cohesion:** Seven handles, one platform, consistent brand prefix, two with rank titles, one with a named operator.

---

## 6. TIER 3 — PATTERN-MATCHED, SINGLE SOURCE

| Handle | Pattern | Notes |
|---|---|---|
| `uttpower` | UTTP embedded | Single occurrence |
| `kecuttpikding1970` | UTTP + dated suffix | 1970 suffix |
| `vecuttpadi1981` | UTTP + dated suffix | 1981 suffix |
| `uttpthdtc` | UTTP + THTDC faction | Faction marker |
| `demiurge-ash` | Named identity | From prior extraction |
| `chicken_hammer_bot` | Named bot | From prior extraction |
| `DarrenOfficial` | Named operator | From prior extraction |
| `pamegacorp` / `PA_Megacorp` | Corporate brand cluster | Two variants |
| `safesurvival` / `safesurvivalofficial` | Server brand cluster | Two variants |

---

## 7. ASSOCIATED INDIVIDUALS & ALIASES

The following individuals were identified through UTTP documentation and OSINT research as associated with the group, its operations, or its offshoots.

### 7.1 Founder

| Name | Aliases | Notes |
|---|---|---|
| **Thomas Parkinson** | Tommy Parky, southparkstudiosable | Founded UTTP February 12-13, 2011. Born October 27, 1979. Reportedly in jail. |

### 7.2 Named Members (Grooming Allegations)

The following individuals have been named in UTTP documentation as members facing grooming allegations:

```
lolbabs, rivenrayne, ashtray, mallbec, opsecdaddy, slimelord,
FPS, reginmyre, defender, striker, FanumRat, HypnoFloof,
Michael, DanielSanoxGG, azriel, bobuxman, bruhman, dwyin,
banban, emperor of anime sucks
```

### 7.3 Faction Leaders & Notable Handles

| Handle/Name | Role | Source |
|---|---|---|
| **FPS** (Fastest Penis Sucker) | UTTP Coalition leader | Soyjak Wiki |
| **Kili_Thili UTTP THTDC** | Talkie AI character, THTDC faction | Talkie AI |
| **Kenny Animate UTTP THTDC** | YouTube channel, THTDC faction | Wikitubia |
| **Michael** | Owner, Michael's UTTP TV Studios | Bluesky profile |
| **Commander Enclave** | UTTP Commander | Shapes.inc |
| **IcedDave** | UTTP enforcer | Shapes.inc |
| **Officer Ben** | UTTP Lieutenant | Shapes.inc |
| **Mr. Mayo** | Lieutenant under General Glen | Shapes.inc |
| **General Glen** | UTTP General | Shapes.inc |
| **CaptainCop24** | UTTP officer | Shapes.inc |

### 7.4 Offshoots & Splinter Groups

| Group | Relationship | Notes |
|---|---|---|
| **YFGA** | Splinter | Soyjak Wiki |
| **ZNTP** | Splinter | Soyjak Wiki |
| **THTDC** | Faction | "The Hellfire Demonic Trolling Company" |
| **DPOS** | Offshoot | Degeneracy Police Order State |
| **SRA** | Com Clan | Spam Report Army |
| **764** | Parent Entity | Terrorist designation |
| **AUTTP** | Opposition | Anti-UTTP Coalition |

---

## 8. PLATFORM PRESENCE MAP

| Platform | Presence Type | Confirmed Handles |
|---|---|---|
| **Bluesky** | Structured cluster | 7 handles (Tier 2) |
| **Tumblr** | Direct subdomain | `uttp.tumblr.com` |
| **Mastodon** | Faction handles | `UTTPmastdept`, `frickfunnymikeuttpthtdc` |
| **YouTube** | Primary platform | Historical base |
| **Discord** | Central coordination | Referenced throughout |
| **X (Twitter)** | Active | Referenced in WIC operations |
| **Google+** | Historical | Original platform |
| **Shapes.inc** | AI character presence | Multiple UTTP characters |

---

## 9. HISTORICAL CONTEXT

### 9.1 Founding & Early Years (2011-2017)

UTTP was founded on **February 12-13, 2011** by Thomas Parkinson (Tommy Parky) on Google+ and YouTube. Originally positioned as an "anti-troll" vigilante group, it quickly adopted aggressive tactics including mass reporting, hacking, doxxing, and intimidation.

### 9.2 Peak Influence (2014-2017)

- **2014 Fandom Wars:** Declared war on FNAF and My Little Pony fandoms
- **Gacha Community Conflict (2020):** Targeted Gacha users with doxxing and hacking

### 9.3 Splintering & Decline (2018-Present)

UTTP splintered into "a dozen splinters" including YFGA, ZNTP, and others. The group was **disavowed from the Soysphere** (the Sharty community). By 2026, UTTP exists more as a **brand than a unified organization** — a trolling style with splinter groups, not a centralized structure.

### 9.4 764 Connection

UTTP copied tactics from **764**, a designated terrorist entity. The "kill a cat in VC" requirement was directly copied from 764. 764 uses Satanic imagery and has been linked to violent extremism.

---

## 10. SOURCE INTELLIGENCE LOG

| Source | Type | Key Findings |
|---|---|---|
| **Soyjak Wiki** | Community wiki | UTTP history, splinters, disavowal, member allegations |
| **Medium (OSINT Charon)** | OSINT article | Founding date, member list, major conflicts |
| **Bluefacts.app** | Bluesky analytics | Michael's UTTP TV Studios profile stats |
| **Shapes.inc** | AI character platform | UTTP character catalog (Commander Enclave, IcedDave, Officer Ben) |
| **Aesthetics Wiki (Larpercore)** | Community wiki | Larpercore context, Cartoon Police Groups |
| **Urban Dictionary** | Reference | Founder identification |
| **Talkie AI** | AI platform | THTDC faction character |
| **Wikitubia** | YouTube wiki | Kenny Animate UTTP THTDC |
| **NamuWiki** | Korean wiki | UTTP overview, member demographics |
| **Abbreviations.com** | Reference | THTDC definition |
| **looksmax.org** | Forum | 764/UTTP discussion |
| **Keane3029-lab.github.io** | AUTTP site | Anti-UTTP coalition petition |

---

## 11. RECOMMENDED NEXT STEPS

| # | Action | Priority |
|---|---|---|
| 1 | **Patch StyxNet extractor** — reject substring collisions (buttplug, Uttapal) | Critical |
| 2 | **Separate user-owned links from scaffolding** in link counting | Critical |
| 3 | **Independently verify Bluesky cluster** — confirm operators, activity status | High |
| 4 | **Cross-reference named members** against public records | High |
| 5 | **Document 764/THTDC/DPOS connections** for parent entity investigation | High |
| 6 | **Do not publish Tier 3 handles** without independent verification | Medium |

---

## 12. APPENDIX — VALIDATED HANDLE INDEX

### Tier 1 — Confirmed Brand-Aligned (5)

```
uttp.tumblr.com
UTTP_OFFICAL
UTTPmastdept
frickfunnymikeuttpthtdc
kiloratstrzntputtp.bsky.social
```

### Tier 2 — Structured Cluster (7)

```
uttparkrosie.bsky.social
michaelsuttptv.bsky.social
uttpalette.bsky.social
uttpofficercoplord.bsky.social
uttp-lieutenant2.bsky.social
uttpus.bsky.social
kiloratstrzntputtp.bsky.social
```

### Tier 3 — Pattern-Matched (10)

```
uttpower
kecuttpikding1970
vecuttpadi1981
uttpthdtc
demiurge-ash
chicken_hammer_bot
DarrenOfficial
pamegacorp / PA_Megacorp
safesurvival / safesurvivalofficial
```

---

**END OF DOCUMENT**

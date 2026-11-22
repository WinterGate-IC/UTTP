# Entity Domains

Verified domain links for every tracked entity. This folder is no longer
UTTP-specific because it covers the full monitored ecosystem.

- Verified domains: 641
- Unique domains: 158
- Entities with verified domains: 31
- Internal unverified leads: 487

Only domains confirmed through Ominis-OSINT page-level validation are listed.
A verified domain is treated as either owned by the entity or a domain/platform
the entity operates in. Validation confirms entity handle linkage, not legal
ownership. Unverified leads remain in `18_ENTITY_MONITORING/domain_validation_queue.csv`
and are not published in this folder or on the Explore tab.

- `occurrences` counts exact URL appearances across the passive source stores
  plus distinct handle URLs found on the same domain.
- `alternate_urls` preserves additional profile URLs on the same domain for
  the same entity instead of stopping after the first handle.

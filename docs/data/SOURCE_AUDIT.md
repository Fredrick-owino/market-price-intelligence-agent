# P08.1 — KAMIS public source feasibility audit

Audit date: 7 October 2026. Owner: Fredrick Onyango, temporary solo contributor.
Scope: independent preparation only. Practitioner validation, official dates,
colleague review and data redistribution permission remain pending. P08 and all
gates remain incomplete; implementation is disabled.

## Finding

Direct public HTML provides candidate same-date records for at least three
markets for Dry Maize classified as White Maize. Wholesale and retail are
separate columns, price cells show `/Kg`, and embedded chart configuration
labels the price axis `KES/KG`. Grade is missing, so matching product, date and
displayed basis does not establish quality equivalence. Historical replay is
conditionally feasible after source/grade validation and permission checks.
This audit does not establish current maize prices or approve a production feed.

## Access method and actual results

Sources:

- [S1: public price search](https://kamis.kilimo.go.ke/site/market_search).
- [S2: market listing /200](https://kamis.kilimo.go.ke/site/market/200).
- [S3: market listing /500](https://kamis.kilimo.go.ke/site/market/500).
- [S4: linked About page](https://kamis.kilimo.go.ke/index.php/site/about).

Initial web-tool opens of S1, S2 and S3 each returned the tool diagnostic
`(400) Timeout fetching`; that is a tool failure, not an observed origin HTTP
400 response. A later web-tool open of the site root returned Internal Error
without usable content. These failures did not prove the site was unavailable.

One sandboxed curl request to S1 failed with exit 6,
`Could not resolve host: kamis.kilimo.go.ke`; HTTP code 000, zero bytes.
An approved outside-sandbox retry succeeded. The other three curl requests used
the same approved network access. Each request used HTTPS, a 5-second connection
timeout, 15-second total timeout and 524,288-byte cap; no redirects or automatic
retries. Only the three requested pages and the About link observed in their
HTML were fetched. No export, pagination traversal, form submission or API was
requested. Python standard-library HTMLParser inspected the returned HTML;
embedded scripts were read as data, never executed.

| Source | Receipt time UTC on 2026-10-07 | HTTP / curl exit | Bytes | Elapsed seconds |
|---|---|---|---:|---:|
| S1 | 20:15:24 | 200 / 0 | 46,184 | 4.105559 |
| S2 | 20:16:57 | 200 / 0 | 47,207 | 3.169923 |
| S3 | 20:17:02 | 200 / 0 | 47,184 | 3.174852 |
| S4 | 20:17:57 | 200 / 0 | 13,343 | 0.218540 |

Receipt times are temporary response-file modification times, not observation
or source publication times. At the original audit, the HTML responses were
retained outside the repository in `/tmp/p081-market-search.html`,
`/tmp/p081-market-200.html`, `/tmp/p081-market-500.html` and
`/tmp/p081-about.html`. All four files were absent at the 9 October 2026
preservation review, so their contents and hashes could not be independently
rechecked then. No full dataset was downloaded, and no raw response is included
in these deliverables.

SHA-256 of the received HTML bytes (provenance only, not dataset hashes):

```text
S1 59e9d3e2feab18e7252613c94e0ce88bddc308babc2e82e9f7342a6cba938310
S2 88279148a43d96cae093c541d90856e2c23bcee76499398eb68c8c5b3e90aaf3
S3 f4bfa85823efba6185881e43aed1cea38fd84f495098282540d3b02783be1ab0
S4 8cb5d25cd43e4d7114c586439ac748a59bb4f1bc86722c65bda44b4ee7d0712a
```

## Directly observed evidence

S1 returned a search form and a default ten-row livestock table dated
2026-10-07, not a maize result. Its controls expose county, market, product and
date filters. No current-maize claim can be inferred from that unrelated table.

The following is a small manually selected feasibility sample, not an approved
dataset. Every row below has commodity Dry Maize, classification White Maize,
and grade `-`. Price text is preserved; the KES interpretation rests on the
same page's chart-axis label, not a currency field in each table row.

| Source | Exact market name | County | Observation date shown | Wholesale text | Retail text |
|---|---|---|---|---|---|
| S2 | Kutus | Kirinyaga | 2026-08-31 | 37.00/Kg | 40.00/Kg |
| S2 | Eldoret Main | Uasin-Gishu | 2026-08-31 | 40.00/Kg | 50.00/Kg |
| S2 | Kerugoya | Kirinyaga | 2026-08-31 | 33.00/Kg | 60.00/Kg |
| S3 | Holo | Kisumu | 2026-06-23 | 35.56/Kg | 50.00/Kg |
| S3 | Kawangware | Nairobi | 2026-06-23 | 55.00/Kg | 65.00/Kg |
| S3 | Ngurubani Market | Kirinyaga | 2026-06-23 | 50.00/Kg | 55.00/Kg |

Use either wholesale or retail consistently; never mix columns in a ranking.
The first triple demonstrates a common historical date; the second supplies an
alternative. They are candidate sets, not selected reachable markets for a
named practitioner or origin. No sack weight or conversion was assumed.

Missingness and anomalies:

- Grade and sex fields display `-`; grade remains unknown, not a shared verified
  standard. Moisture, quality specification, collection time, tax/fee inclusion,
  row-level currency, stable quote IDs and revision history were not supplied
  in the inspected table. A date is displayed; its collection/publication
  semantics require confirmation.
- Supply volume is blank for Kutus, Holo and Kawangware. Its unit is not stated
  in the table header. A blank or dash is missing, never zero, and volume is not
  proof of buyer capacity.
- S3 contains two White Maize entries for Isebania Market on 2026-06-23:
  wholesale `35.56/Kg`, retail `-`, volume `100000.00`; and wholesale
  `31.67/Kg`, retail `48.00/Kg`, volume `25000.00`. Their distinguishing metadata
  are insufficient. Quarantine the conflict; do not average or choose one.
- S2 and S3 chart source labels the axis `KES/KG`, but the tooltip appends `KG`
  and generated series include epoch-date zero points. Do not use those chart
  points as observed prices/dates or allow them to override the table.

## Search-index evidence — separate from direct retrieval

Before successful curl access, search returned indexed representations of the
same URLs, marked crawled five months ago. These are not live verification:

- S2's excerpt showed Gikomba, Kawangware and Gakoromone on 2026-03-06, with
  wholesale/retail pairs `53.33/70.00`, `55.00/65.00`, `38.89/40.00`, all displayed
  per Kg for White Maize. Direct S2 instead returned August/September records.
- S3's excerpt showed Kangemi Market on 2026-01-16 at `4500.00/Kg` wholesale
  and `5000.00/Kg` retail. These magnitudes are suspicious relative to adjacent
  displayed prices, but a sack-price/unit-entry error is only a hypothesis.
  Neither price was converted, corrected or accepted as a usable observation.
  Direct S3 instead returned June records and did not corroborate that row.

Both suffix URLs contain multiple markets and pagination links. They must not
be interpreted as market IDs or immutable historical records. The difference
between indexed and fetched content makes URL-only provenance inadequate;
retain retrieval time and content hash for any later permitted snapshot.
Unrelated third-party search results and their currency/licence claims were
not used to validate KAMIS rows or permissions.

## Access, attribution and reuse terms

Permissions: **UNVERIFIED** for automated retrieval, storage, public
redistribution and derived demo snapshots. The reviewed HTML/navigation and
linked About page did not provide an explicit reuse licence, attribution rule
or access policy. Targeted public searches for KAMIS terms, copyright, licence
and attribution did not establish one. This is absence of evidence in the
bounded audit, not proof that no terms exist anywhere.

S4 describes KAMIS's agricultural price-information purpose, but its real-time
service claim is not validation of this sample's freshness. The source is the
KAMIS public service on the Ministry's `kilimo.go.ke` domain; the exact rights
holder and permission-granting contact need confirmation. Proposed attribution
for a later approved sample: KAMIS, source URL, market/date/basis and retrieval
timestamp/hash. This is a project proposal, not a discovered licence condition.
An export button or public accessibility is not permission to republish.

## Decision and next preparation steps

- **Three-market coverage:** observed for common historical dates; full
  comparability remains conditional on unknown grade/quality and price-basis
  validation. No records are approved for advisory calculations by this audit.
- **Current prices:** not established. Inspected maize rows range from June to
  September 2026, while the audit is in October. No freshness threshold is set,
  and this bounded sample cannot show whether newer maize data exist elsewhere.
- **Historical replay:** technically promising using an explicit historical
  as-of date, but a redistributable replay dataset is not yet cleared.
- Fredrick can prepare a permission/metadata inquiry for the published source
  owner; do not send it without authorization. Ask about permitted automated
  access, attribution, redistribution, grade, currency, volume units and
  duplicate/revision handling.
- Resume practitioner validation of one crop, origin, reachable markets and
  freshness policy. Obtain source clarification before selecting or normalizing
  anomalous/conflicting rows; then review a small permitted snapshot and manifest.
- Official implementation dates and peer review remain pending. This document
  does not mark P08, G0, G1 or any other gate complete.

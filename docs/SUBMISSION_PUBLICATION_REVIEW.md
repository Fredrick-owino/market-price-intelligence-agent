# Licence and publication review — 13 October 2026

Scope: original project source and retained public evidence, direct dependency
licences/notices, model/runtime terms, current data tree and reachable local Git
history. No history rewrite, destructive cleanup, dataset import or publication
was performed. This is a factual scoped review, not an all-transitive legal opinion.

## Concrete findings

- Root [LICENSE](../LICENSE) contains standard MIT terms. MIT is
  [OSI-approved](https://opensource.org/license/mit); anonymous GitHub repository
  metadata reports `license.spdx_id: MIT`, `private: false`; README returned 200.
  [Public check](../evals/results/I01.13-submission-public-repository-check.json).
- [Direct-component inventory](../evals/results/I01.13-submission-license-inventory.json)
  records installed versions, declared licences and local notice hashes.
  [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) adds the missing consolidated
  attribution/boundary summary. Source licence does not replace upstream terms.
- Isolated Fetch 2026.8.18's installed MIT licence is byte-identical to retained
  `infra/borrowed-fetch/UPSTREAM-LICENSE` (SHA-256
  `8cc7c6e33b24ed4ee8fcccc33eccf102549d04fa4cb9737cecc9770dad1080ff`).
  Current upstream MCP licensing transition is separate; no whole-source-release
  equivalence or blanket current-MIT claim. An initial metadata check in the
  application environment correctly found no Fetch distribution; the actual
  isolated environment was then inspected and matched.
- Qwen's publisher and the exact Ollama tag identify Apache-2.0. The installed
  licence-layer bytes match SHA-256
  `d18a5cc71b84bc4af394a31116bd3932b42241de70c77d2b76d69a314ec8aa12`.
  Pinned Ollama 0.40.2's upstream licence is MIT; compiled library notices must
  accompany any future runtime distribution. Neither runtime nor weights are
  tracked in this source repository.
- Current and reachable `data/` history contain only the project-authored
  synthetic fixture (introduced 10 October). No raw KAMIS dataset or response
  was located. [SOURCE_AUDIT.md](data/SOURCE_AUDIT.md) and its reachable history
  do contain six small attributed historical aggregate-price examples plus
  source observations. They are real public-source excerpts, not synthetic
  records, and are not used by the application.
- That audit did not establish KAMIS storage/redistribution terms. Its bounded
  permission uncertainty remains for larger source reuse; this review neither
  grants permission nor concludes that those attributed factual notes constitute
  a prohibited dataset. The official brief allows aggregate market data and
  own synthetic data. No real household records/personal farmer details were
  identified in the reviewed scope. No automatic history rewrite is justified
  by the mere existence of the notes; owner can seek source-owner clarification
  before any broader real-data use.
- A check of 326 reachable Git blobs found no exact current private-token or
  private tunnel-allowlist literals and no tracked private credential/database/
  weight filenames. [Scope/result](../evals/results/I01.13-submission-publication-review.json).
  This was exact-literal/name inspection, not a comprehensive secret-history
  scanner or a guarantee about all unknown secrets. New package files received
  the same local review before staging.

## Publication questions kept separate

1. Source/fixture publication is already public and MIT-labelled. Dependency
   environments/binaries/weights are not being repackaged; future bundles need
   their actual notices retained. Original source changes here need no licence
   replacement or Git-history rewrite.
2. Video public upload remains explicitly unauthorised. Native WebM and its
   byte-identical upload copy are local/private; no actual watch URL exists.
3. The recorded automated demo identity must not be advertised as a named human
   officer or institutional endorsement. Owner confirmed no named office/human.
   Intended Kenyan maize-extension users/workflow may be stated with that limit.
4. Read-only form access required Google sign-in. Owner supplied the first
   applicant section; later required fields remain unknown. Private contact
   values stay in the owner’s browser.
5. Official FAQ verifies 15 October 2026, not a cutoff hour/timezone. Do not
   freeze now, invent a timestamp, or claim a final submission receipt.

Internal peer-review/gate checkboxes are not additional official publication
requirements. An unresolved evaluation case does not force implementation; it
is required to be reported honestly with a proposed next step.


## 15 October publication update

Fredrick explicitly requests committing and pushing all pending project changes.
The owner-reported organiser cutoff is 15 October 2026 23:59 Africa/Nairobi
(20:59 UTC); see docs/STATUS.md for source/verification limits. Earlier cutoff-
unknown and no-commit wording records the historical preparation state.
This source publication does not upload a video, submit the form, expose a
network route, establish named-human review or complete a release gate.

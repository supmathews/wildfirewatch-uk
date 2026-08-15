# Remaining incident gap review

This review records the current source-verification status before expanding the modelling dataset. It avoids upgrading seed records without durable, source-backed facts.

## Findings

- **Stourbridge**: still has an approximate Osmaston Road coordinate and source-backed incident date from news reporting, but no durable exact ignition/start time was found in this pass.
- **New Forest**: still has an approximate A31/Ringwood coordinate and source-backed incident date/cause from BBC reporting, but no durable exact ignition/start time was found in this pass.
- **Porth**: still has an approximate Pleasant Heights coordinate and source-backed incident date from BBC/WalesOnline reporting, but no durable exact ignition/start time was found in this pass.
- **Cannock Chase**: source-backed July 30 call time remains usable, but a source-backed centroid/perimeter for the July 30 Brocton/Sherbrook Valley incident remains unresolved.
- **Tamworth**: remains unverified; no durable source URL good enough to promote it into the modelling dataset was found in this pass.

## Additional source encountered

BBC published a separate Cannock Chase / Sherbrook Valley article for a later, larger fire reported at about 14:30 BST on Wednesday 5 August 2026 and published on 6 August 2026:

- https://www.bbc.com/news/articles/c0l59yn404eo

This is useful background, but it should not be silently merged into the existing July 30 Cannock Chase seed record. If used, it should become a separate incident record with its own provenance.

## Decision

No remaining seed incidents were upgraded in this PR. The safer improvement for the modelling path is to harden controls so generated non-fire points cannot sit too close to known positive incident locations.

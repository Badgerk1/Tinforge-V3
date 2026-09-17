# Purolator NP 2026 — Stage 1 binary observations

Raw file size: 446650 bytes

SHA-256: `423926032d368d2ebce9ffa9acfba3c5e467f200a13b1470d214962b45cb3207`

## VERIFIED

- Bytes 0 through 9 are ASCII `Topcon TP3`.
- UTF-16LE project-name bytes for `Purolator NP 2026` begin at byte offset 30.
- Surface name `design grade` is present as UTF-16LE at offset 433778.
- Seven layer-name strings were found:
  - 400068: `UTIL - Storm Structures`
  - 400408: `SITE - Silt fence`
  - 400748: `DES - Top of Slope`
  - 401088: `DES - GRAVEL`
  - 401428: `SITE - Mudd Mats`
  - 401768: `Original Ground`
  - 402108: `DES - Property lines`
- These seven layer-name offsets are spaced exactly 340 bytes apart, strong evidence of a fixed-size or regularly indexed layer-record region.
- Searches found no plain ASCII or UTF-16LE text for `MTM`, `NAD83`, or `CSRS`. The CRS is therefore not stored as those obvious text strings and remains to be mapped.

## UNVERIFIED / NEXT TARGETS

- Header field meanings after the `Topcon TP3` signature.
- The field immediately before the project name.
- Exact start and full layout of the apparent layer records.
- Location/encoding of the known design-grade vertex and triangle topology.
- CRS identifier/localization representation.

No unknown bytes have been assigned TP3 semantics in this report.

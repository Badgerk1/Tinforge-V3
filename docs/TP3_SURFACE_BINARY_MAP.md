# TP3 Surface Binary Map — Purolator NP 2026

Status: evidence from the professional golden TP3 only. Do not generalize offsets to other TP3 files.

## Golden file

- Size: 446650 bytes
- Raw SHA-256: `423926032d368d2ebce9ffa9acfba3c5e467f200a13b1470d214962b45cb3207`
- Surface name `design grade` (UTF-16LE): byte offset 433778

## VERIFIED: triangle topology table

A contiguous table begins at byte offset **431906** and occupies exactly **1824 bytes**.

It decodes as **456 little-endian signed 32-bit integers**, which partitions exactly into **76 records x 6 integers**.

For each record:

- integers 0..2 are vertex indices
- integers 3..5 are neighboring-triangle indices, with `-1` used at an exterior/boundary edge

Evidence:

- There are exactly 76 six-integer records.
- The first three fields span exactly vertex IDs **0 through 52**, with all 53 IDs represented.
- The final three fields contain triangle IDs in **0 through 75** plus `-1` sentinels.
- This independently reproduces the previously observed 53-vertex / 76-triangle surface counts from the binary itself.

First records:

```text
triangle 0: vertices [0,1,2]   neighbors [30,42,34]
triangle 1: vertices [3,4,5]   neighbors [-1,58,59]
triangle 2: vertices [6,7,8]   neighbors [19,-1,-1]
triangle 3: vertices [9,10,11] neighbors [18,4,17]
triangle 4: vertices [10,12,11] neighbors [21,-1,3]
```

## VERIFIED: nearby coordinate triple

At byte offset **431844**, three consecutive little-endian IEEE-754 float64 values decode to:

```text
4843976.009
295334.679
170.621
```

These are geographically/plausibly shaped as northing/easting/elevation values for the project. Their exact semantic role is not yet proven; they are therefore **not** labeled as a surface vertex.

## Current unknown

The 53 XYZ vertex payloads have not yet been proven. They may be stored in another record table or encoded through an indirect/delta representation. The parser must not invent a vertex layout until that relationship is demonstrated.

## Next decoding target

Locate the vertex payload referenced by IDs 0..52 and prove XYZ values against source design geometry. Once proven, add topology reciprocity tests and coordinate/elevation tolerance tests.

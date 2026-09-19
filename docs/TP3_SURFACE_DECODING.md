# TP3 Surface Decoding Evidence

Golden file: `Purolator NP 2026.tp3`

Raw SHA-256: `423926032d368d2ebce9ffa9acfba3c5e467f200a13b1470d214962b45cb3207`
Size: 446650 bytes

## Verified count anchor

Byte-level inspection has now independently located the expected surface counts immediately before the UTF-16LE surface name `design grade`.

Offsets (zero-based):

- `0x069E64` / decimal 433764: little-endian uint32 = **53**
- `0x069E68` / decimal 433768: little-endian uint32 = **76**
- `0x069E72` / decimal 433778: UTF-16LE string begins: **design grade**

This is direct binary evidence tying the previously reported 53-vertex / 76-triangle counts to the `design grade` surface record. These values are no longer merely prior observations.

## Verified topology evidence

The bytes beginning at decimal offset `431906` decode as exactly `76 × 24-byte` triangle records:

`vertex_0, vertex_1, vertex_2, neighbor_0, neighbor_1, neighbor_2`

All triangle references validate against the 53-vertex set, neighbor indexes remain in `-1..75`, and reciprocal adjacency has been reproduced in automated tests.

## Verified coordinate evidence

A contiguous region beginning at decimal offset `380120` decodes as exactly `53 × 24-byte` vertex records, each three little-endian float64 values:

`local_x, local_y, elevation_z`

The reconstructed surface uses local XY values around the stored origin doubles at offsets `433908` and `433916`, yielding plausible project easting/northing extents and a valid 76-triangle TIN with no zero-area triangles.

## Acceptance gate for Stage 1

Stage 1 surface decoding is complete only when code can deterministically:

1. identify the `design grade` surface record;
2. read 53 vertices with proven X/Y/Z field positions;
3. read exactly 76 triangle records;
4. prove every triangle index references a valid vertex;
5. reject truncated/corrupt variants safely; and
6. reproduce these facts in automated golden-file tests.

Current status: **surface geometry and topology decoded for the golden `design grade` surface**. Remaining work is the enclosing TP3 container/metadata structure needed for broader parser/export coverage.

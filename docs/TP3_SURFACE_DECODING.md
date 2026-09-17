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

## Nearby topology evidence

The bytes immediately preceding the surface header contain long runs of small integer values plus `0xFFFF` sentinels. The values are consistent with index/topology data, but their exact field semantics and record width are not yet proven. Do not label these as triangle connectivity until the parser reproduces all 76 triangles and all references validate against the 53-vertex set.

## Coordinate evidence

A nearby region beginning around decimal offset 426880 contains repeated IEEE-754 little-endian doubles in realistic project-coordinate ranges, including northings around 4,844,234 and eastings around 295,315. The surrounding bytes are structured and repeat, but the complete XYZ record layout is not yet proven.

## Acceptance gate for Stage 1

Stage 1 surface decoding is complete only when code can deterministically:

1. identify the `design grade` surface record;
2. read 53 vertices with proven X/Y/Z field positions;
3. read exactly 76 triangle records;
4. prove every triangle index references a valid vertex;
5. reject truncated/corrupt variants safely; and
6. reproduce these facts in automated golden-file tests.

Current status: **in progress**. The surface count anchor is verified; vertex and topology record layouts remain under investigation.

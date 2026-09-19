# TP3 Surface Decoding Evidence

Golden file: `Purolator NP 2026.tp3`

Raw SHA-256: `423926032d368d2ebce9ffa9acfba3c5e467f200a13b1470d214962b45cb3207`
Size: 446650 bytes

## Verified count anchor

Independent reads from the original professional bytes show:

- decimal `433766`: `uint32LE = 53`
- decimal `433770`: `uint32LE = 76`
- decimal `433778`: UTF-16LE `design grade` surface name begins

This directly ties the verified `53`-vertex / `76`-triangle counts to the `design grade` surface record context.

## Verified vertex and topology evidence from original bytes

- Vertex block: `380120:381392` (exactly `1272` bytes = `53 * 24`)
- Vertex record layout: little-endian `<3d` (`local_x, local_y, elevation_z`)
- Exact byte round-trip: decode 53 records and re-encode => byte-for-byte equality with original block
- Vertex block SHA-256: `045e128e0b7774a819e434055e0fc3d75d3b7b168b259df5283895e7cbbfa08a`

Triangle table:

- starts at `431906`
- `76` records of `24` bytes each, layout `<6i` (`v0,v1,v2,n0,n1,n2`)
- all vertex indexes valid and all 53 vertices used
- reciprocal neighbor topology valid and each stored neighbor corresponds to the geometrically correct shared edge
- reconstructed TIN metrics: `V=53`, `F=76`, `E=128`, boundary edges `=28`, Euler `=1`
- no zero/near-zero XY triangles and no non-manifold edges

## Origin-candidate doubles

Read directly from original bytes:

- `float64LE @ 433908 = 295399.97869873`
- `float64LE @ 433916 = 4843987.442024235`

Interpretation as actual surface/project origin remains **SUPPORTED HYPOTHESIS**, not VERIFIED, until structural linkage is proven.

## Remaining UNKNOWNs

- Exact enclosing TP3 container structure around the verified surface blocks.
- Definitive field-level proof for origin semantics at `433908`/`433916`.
- Additional unknown TP3 structures required for complete native TP3 emission.

## Acceptance gate for Stage 3

Stage 1 surface decoding is complete only when code can deterministically:

1. identify the `design grade` surface record;
2. read 53 vertices with proven X/Y/Z field positions;
3. read exactly 76 triangle records;
4. prove every triangle index references a valid vertex;
5. reject truncated/corrupt variants safely; and
6. reproduce these facts in automated golden-file tests.

Current status: **in progress**. Vertex/triangle/count decoding and topology checks are now verified from original bytes; container semantics outside those verified blocks remain UNKNOWN.

# TP3 Research Notebook

## Golden reference
Use `Badgerk1/tinforge/real_survey_data/Purolator NP 2026.tp3` as the principal authentic sample because it was professionally produced for the project represented by the supplied PDFs.

Raw golden-file identity independently verified from the user-supplied binary:
- size: 446,650 bytes
- SHA-256: `423926032d368d2ebce9ffa9acfba3c5e467f200a13b1470d214962b45cb3207`
- signature: `Topcon TP3`

## Verified surface topology discovery — 2026-09-17
The professional file contains a surface named `design grade` as UTF-16LE beginning at byte offset 433,778.

Immediately before that surface name, two little-endian uint32 values independently reproduce the expected topology counts:
- byte 433,766: 53 vertices
- byte 433,770: 76 triangles

A contiguous topology table begins at byte 431,906 and contains exactly 76 records of 24 bytes each. Each record decodes as six little-endian signed int32 values:

`vertex_0, vertex_1, vertex_2, neighbor_0, neighbor_1, neighbor_2`

Validation across all 76 records:
- all three vertex fields are in 0..52
- collectively the topology references every vertex index 0..52
- all three neighbor fields are either -1 or in 0..75
- -1 occurs 28 times in neighbor slots and is consistent with an exterior/boundary edge sentinel
- no vertex field contains -1

Example first records:
- triangle 0: vertices `(0,1,2)`, neighbors `(30,42,34)`
- triangle 1: vertices `(3,4,5)`, neighbors `(-1,58,59)`
- triangle 2: vertices `(6,7,8)`, neighbors `(19,-1,-1)`

Confidence: VERIFIED for record boundaries, counts, integer layout, vertex-index interpretation and neighbor-index interpretation. The exact edge-to-neighbor ordering should still be tested geometrically once XYZ coordinates are decoded.

## Verified surface vertex block discovery — 2026-09-19
The professional file contains a contiguous 53-record vertex block beginning at byte offset 380120.

Each record is 24 bytes and decodes as three little-endian IEEE-754 float64 values:

`local_x, local_y, elevation_z`

Validation across all 53 records:
- offsets 380120..381391 contain exactly `53 × 24 = 1272` bytes
- decoded local X values span `-56.881774900015444 .. 56.881774900015444`
- decoded local Y values span `-77.34722137451172 .. 77.34722137544304`
- decoded elevation Z values span `168.65 .. 171.25`
- when indexed by the verified triangle table, the reconstructed mesh has no zero-area triangles and satisfies reciprocal adjacency/boundary expectations

Verified examples:
- vertex 0: `(29.948791500006337, -44.49799347482622, 170.45)`
- vertex 1: `(28.356750489969272, -54.3188858050853, 170.2)`
- vertex 52: `(47.70098876999691, 62.317619315348566, 170.5)`

Two little-endian float64 values at byte offsets 433908 and 433916 decode to `295399.97869873` and `4843987.442024235`. Adding the local XY values above yields plausible project easting/northing extents `295343.09692383 .. 295456.86047363` and `4843910.09480286 .. 4844064.78924561`. For this golden file, the evidence now supports treating those doubles as the stored surface/project origin used by the decoded local XY vertex coordinates.

## Reverse-engineering method
1. Preserve an untouched hash-identified copy.
2. Identify container/signature/version/endianness and offsets.
3. Inventory strings, numeric blocks, tables, counts and relationships.
4. Locate XYZ records using known drawing values.
5. Locate surface vertices and triangle connectivity.
6. Locate layers/features and metadata.
7. Locate CRS/unit metadata.
8. Where legitimate Topcon tooling is available, change one property at a time and binary-diff outputs.
9. Repeat with minimal synthetic projects to isolate fields.
10. Convert every confirmed discovery into parser assertions/tests.

## Confidence labels
VERIFIED = confirmed by multiple observations or authoritative tooling/docs. STRONG = consistent evidence not fully isolated. HYPOTHESIS = plausible but unconfirmed. UNKNOWN = data exists but semantics are unknown. Production serialization should rely only on VERIFIED behavior unless explicitly experimental.

## Parser requirements
Expose raw offsets/record IDs with normalized objects so unknown data can be investigated. Validate lengths/counts/index bounds before dereferencing. Preserve existing triangle topology exactly unless explicitly rebuilding the surface.

## Export routes
A) Native TP3 serialization only after required structures are sufficiently verified.
B) Verified civil interchange (LandXML/MAXML where supported) followed by a verified Topcon conversion/import path. Prefer this over guessing proprietary bytes.

Both require post-export validation.

## Open questions
The major next target is the exact surrounding surface/container record structure beyond the now-verified vertex block, origin doubles, count fields and triangle table. Continue with CRS/localization representation, breaklines/boundaries, layers/features, checksums/object IDs/cross-reference tables, compatibility among Pocket3D/3D-MC/MC-X versions, and safe LandXML/MAXML round-trip behavior.

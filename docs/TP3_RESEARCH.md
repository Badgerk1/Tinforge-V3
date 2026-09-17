# TP3 Research Notebook

## Golden reference
Use `Badgerk1/tinforge/real_survey_data/Purolator NP 2026.tp3` as the principal authentic sample because it was professionally produced for the project represented by the supplied PDFs.

Raw golden-file identity independently verified from the user-supplied binary:
- size: 446,650 bytes
- SHA-256: `423926032d368d2ebce9ffa9acfba3c5e467f200a13b1470d214962b45cb3207`
- signature: `Topcon TP3`

## Verified surface topology discovery — 2026-09-17
The professional file contains a surface named `design grade` as UTF-16LE beginning at byte offset 433,778.

Immediately before that surface name, two little-endian uint16 values independently reproduce the expected topology counts:
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

Two plausible project/surface coordinate doubles also occur in surface metadata after the topology table/name: approximately E=295399.97869873 and N=4843987.442024235. Their exact semantic role is not yet proven, so they remain STRONG/HYPOTHESIS rather than production serialization facts.

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
The major next target is the 53-entry XYZ coordinate storage referenced by the now-verified topology table. After XYZ is mapped, validate triangle geometry, neighbor edge ordering, surface bounds/elevation range, then continue with CRS/localization representation, breaklines/boundaries, layers/features, checksums/object IDs/cross-reference tables, compatibility among Pocket3D/3D-MC/MC-X versions, and safe LandXML/MAXML round-trip behavior.

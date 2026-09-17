# TP3 Research Notebook

## Golden reference
Use `Badgerk1/tinforge/real_survey_data/Purolator NP 2026.tp3` as the principal authentic sample because it was professionally produced for the project represented by the supplied PDFs.

Previously observed: metric; MTM Zone 10; NAD83(CSRS v7); `design grade`; 53 vertices; 76 triangles; seven layers. Independently verify all observations.

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
Exact TP3 variants; required/optional records; CRS/localization representation; surface structure/indexing; breaklines/boundaries; layers/features; checksums/object IDs/cross-reference tables; compatibility among Pocket3D/3D-MC/MC-X versions; and what can safely round-trip through LandXML/MAXML.

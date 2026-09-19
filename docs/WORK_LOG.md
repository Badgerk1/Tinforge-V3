# Tinforge V3 — Work Log / ChatGPT Handoff

## 2026-09-17 — V3 reset
Decision: scrap the previous TinForge TP3-generation approach and rebuild the proper pipeline. Extensive testing is required at every stage.

### Inputs
Prior repo `Badgerk1/tinforge/real_survey_data` contains professional `Purolator NP 2026.tp3`, `63287_001-C1.1 -R1.pdf`, and `63287_002-TB1-ElevationsOn-24x30-Horiz-Topo.pdf`. This comparison set is the foundation for reverse engineering and validation.

### Prior authentic TP3 observations
`design grade`; 53 vertices; 76 triangles; seven layers; metric; MTM Zone 10, NAD83(CSRS v7). These must be reproduced by tests rather than hard-coded.

### Architecture decision
Trusted pipeline: structural TP3 parser -> canonical project model -> PDF calibration/tracing/import -> constrained TIN -> validation -> verified interchange/Topcon conversion or verified native TP3 -> round-trip verification.

A guessed/custom TP3 writer is rejected.

### Acceptance decision
Desktop success is insufficient. Designs must be checked in the Topcon workflow and initially tested guidance-only before any automatic blade-control use.

### Immediate next tasks
1. Bring authorized golden fixtures into the V3 test environment without altering originals.
2. Hash/inventory them.
3. Build a TP3 inspection utility before a writer.
4. Produce a machine-readable structural dump of the professional TP3.
5. Add tests for verified counts/metadata/coordinates.
6. Build canonical geometry model.
7. Prototype PDF calibration against known project coordinates.
8. Implement constrained-TIN synthetic tests.
9. Verify Topcon-supported LandXML/MAXML conversion/import behavior for target versions.
10. Decide on native TP3 serialization only when evidence supports it.

## Future log rule
Append dated entries with evidence, code changes, exact tests/results, failures, unresolved questions and next action. Avoid vague statements like "works."

## 2026-09-19 — Stage 2 review fixes
### Code changes
- Added canonical `SurfaceTIN`, `SurfaceVertex`, and `SurfaceTriangle` dataclasses in `src/tinforge/surface.py`.
- Added deterministic triangle-adjacency generation with explicit non-manifold rejection.
- Strengthened `validate_tin()` so every interior edge must have reciprocal neighbor references on both triangles, boundary edges must keep `-1`, invalid indexes fail fast, and XY degeneracy uses a documented scale-aware absolute twice-area tolerance instead of exact `== 0.0`.
- Added `src/tinforge/tp3/writer.py` with verified 24-byte triangle-record serialization/parsing only; generated triangle-record reparsing now rejects invalid vertex/neighbor indexes, duplicate vertex indexes, and invalid neighbor topology, and full TP3 serialization still fails closed at the first UNKNOWN field.

### Tests
- Added synthetic Stage 2 fixture coverage plus negative regression tests for missing neighbors, wrong neighbors, non-reciprocal neighbors, incorrect-edge neighbors, degenerate/near-degenerate triangles, invalid indexes, malformed triangle-record reparsing, and non-manifold geometry.
- Full suite result: `python -m pytest -vv` -> 24 passed.

### Remaining UNKNOWN TP3 fields
- Exact surface vertex XYZ storage layout in the golden TP3.
- Exact enclosing surface/container record boundaries and byte layout around the verified triangle table.
- Exact semantic mapping for surrounding TP3 metadata needed before a complete native TP3 file can be emitted safely.

## 2026-09-19 — Stage 3 original-byte surface verification
### Code changes
- Added `src/tinforge/tp3/surface_decoding.py` with deterministic original-byte decoding/verification for:
  - vertex block at `380120:381392` (`53 * 24` bytes, `<3d`);
  - triangle block at `431906` (`76 * 24` bytes, `<6i`);
  - `uint32LE` count reads at `433766` and `433770`;
  - double reads at `433908` and `433916` (kept as hypothesis-level semantics).
- Added `tests/test_tp3_surface_stage3.py` to validate required Stage 3 assertions from the original professional TP3 bytes, including exact vertex-byte round-trip and geometric neighbor-edge correctness.
- Added `original_professional_tp3_bytes` session fixture in `tests/conftest.py` to load the authentic TP3 from `TINFORGE_GOLDEN_TP3_PATH` (or known local fallback paths).
- Updated `tests/fixtures/golden/REFERENCE_MANIFEST.json` with verified vertex block fields and corrected count-header key names to `*_u32le_offset`.

### Evidence/results
- Original file SHA-256 confirmed: `423926032d368d2ebce9ffa9acfba3c5e467f200a13b1470d214962b45cb3207`.
- Vertex block SHA-256 (`380120:381392`): `045e128e0b7774a819e434055e0fc3d75d3b7b168b259df5283895e7cbbfa08a`.
- Exact decode/re-encode byte equality for all 53 `<3d` vertex records: PASS.
- TIN reconstruction from original bytes proves:
  - `V=53`, `F=76`, `E=128`, boundary edges `=28`, Euler `=1`;
  - valid triangle indexes and all vertices used;
  - no zero/near-zero triangles;
  - no non-manifold edges;
  - reciprocal adjacency and geometric neighbor-edge correspondence.
- Header checks from original bytes:
  - `uint32LE @ 433766 = 53`
  - `uint32LE @ 433770 = 76`
- Candidate doubles read:
  - `float64LE @ 433908 = 295399.97869873`
  - `float64LE @ 433916 = 4843987.442024235`
  - semantic role remains **SUPPORTED HYPOTHESIS**, not VERIFIED.

### Tests
- `TINFORGE_GOLDEN_TP3_PATH=/tmp/Purolator_NP_2026.tp3 python -m pytest`
- Result: `29 passed`.

### Remaining UNKNOWN structures
- Exact enclosing TP3 surface/container record structure outside the verified vertex/triangle/count blocks.
- Definitive structural proof that doubles at `433908` and `433916` are canonical surface/project origin fields.
- Remaining TP3 container/object-link/checksum structures required for safe complete native TP3 serialization.

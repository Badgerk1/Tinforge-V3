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

## 2026-09-19 — Stage 3 surface decoding analysis
### Code changes
- Added `src/tinforge/tp3/surface_decoder.py` to decode the verified golden `design grade` surface from raw TP3 bytes or a sliced byte window using exact absolute offsets plus bounds checks.
- Added `tools/tp3_surface_dump.py` and exported the decoder from `src/tinforge/tp3/__init__.py` for reproducible binary-analysis dumps.
- Added `tests/test_tp3_surface_stage3.py` plus the derived evidence fixture `tests/fixtures/golden/Purolator_NP_2026.design_grade_surface.json`, which captures the verified offsets, decoded vertices, decoded triangle topology, and verified bounds needed to reconstruct the golden surface window in tests.

### Verified binary findings
- The golden `design grade` vertex block begins at byte offset `380120` and contains `53` records of `24` bytes each.
- Each vertex record is three little-endian float64 values interpreted as `local_x`, `local_y`, and `elevation_z`.
- Surface/project origin doubles appear at byte offsets `433908` and `433916` with values `295399.97869873` and `4843987.442024235`.
- Reconstructing the surface from the verified vertex block plus the verified 76-record triangle table yields a valid TIN with reciprocal adjacency and no zero-area triangles.

### Remaining UNKNOWN TP3 fields
- Exact enclosing container record boundaries and semantic meaning of the bytes surrounding the verified surface block.
- CRS/localization representation beyond the decoded local-origin relationship.
- Remaining project/layer/feature/checksum/object-ID structures required for a complete native TP3 writer.

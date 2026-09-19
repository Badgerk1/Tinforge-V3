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

## 2026-09-19 — Stage 2 foundation (canonical TIN + verified TP3 triangle serializer)

### Code changes
- Added canonical TIN model in `src/tinforge/surface.py` with explicit `Vertex`, `Triangle`, `SurfaceTIN` dataclasses.
- Added deterministic adjacency construction and fail-closed geometry validation gates for:
  - finite XYZ coordinates,
  - vertex-index bounds,
  - reciprocal neighbor references,
  - non-manifold edge rejection,
  - zero-area triangle rejection.
- Added Stage 2 writer foundation in `src/tinforge/tp3/writer.py` for VERIFIED fields only:
  - TP3 signature constant,
  - 24-byte triangle-record encoder/decoder (`<6i` little-endian int32),
  - deterministic triangle-table serializer/deserializer.
- Added explicit fail-closed project-writer gate (`Tp3SerializationBlockedError`) that stops at the first UNKNOWN required field.

### Fixtures and tests
- Added tiny synthetic fixture: `tests/fixtures/synthetic/tiny_surface.json`.
- Added Stage 2 tests in `tests/test_stage2_tin_and_tp3_writer.py` covering:
  - deterministic adjacency output,
  - manifold/boundary and reciprocal-neighbor invariants,
  - out-of-range and zero-area rejection,
  - deterministic serializer output and reparse validation,
  - truncation/corruption rejection,
  - golden-reference regression anchors from `REFERENCE_MANIFEST.json`.

### Unknown fields that block full TP3 serialization
Full TP3 container output is intentionally blocked pending VERIFIED evidence for:
1. exact byte offsets/record structure of the 53-entry vertex XYZ payload;
2. proven local-XY-plus-origin encoding layout as stored in TP3 records;
3. enclosing surface/container record boundaries and required cross-reference/check fields necessary to emit a valid TP3 project artifact.

### Next action
- Decode and prove the golden vertex table and enclosing surface-container structure, then replace the fail-closed blocker with verified field serializers incrementally.

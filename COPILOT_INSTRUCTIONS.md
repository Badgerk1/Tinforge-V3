# Tinforge V3 — GitHub Copilot Instructions

## Mission
Build Tinforge V3 as a reliable engineering application for producing Topcon-compatible machine-control design deliverables from survey/design source data. Immediate target: proper TP3 workflow for Topcon Pocket3D and MC-X3/XCM3 dozer workflows.

## Non-negotiable
Do not revive, patch, or depend on the previous custom/fake TinForge TP3 writer. The old TP3-generation approach is rejected. Build the pipeline from verified evidence.

## Reference evidence
Prior project `Badgerk1/tinforge/real_survey_data` contains:
- `Purolator NP 2026.tp3` — professionally generated authentic reference.
- `63287_001-C1.1 -R1.pdf` — source project drawing.
- `63287_002-TB1-ElevationsOn-24x30-Horiz-Topo.pdf` — source survey/topographic/elevation drawing.

Previously observed in the authentic TP3: metric; MTM Zone 10, NAD83(CSRS v7); `design grade` surface; 53 vertices; 76 triangles; seven layers. Reverify these facts; do not treat them as a universal TP3 specification.

## Engineering rules
1. Reverse-engineer authentic TP3 structure and document verified fields/relationships.
2. Preserve stored topology when parsing an existing TP3; never silently retriangulate it.
3. Separate project data, geometry, CRS metadata, surface topology, layers/features, and serialization.
4. Keep PDF calibration/tracing/import separate from TP3 serialization.
5. Generate constrained TIN surfaces from verified source geometry.
6. Use a verified interchange/conversion path (LandXML/MAXML or other supported Topcon path) where appropriate instead of inventing undocumented TP3 bytes.
7. Add round-trip verification: parse -> model -> serialize/convert -> parse/inspect -> compare.
8. Reject exports when required CRS, units, geometry, topology, or validation information is missing.
9. A `.tp3` extension alone never means a file is machine-ready.

## Testing
Testing is required at every stage. Add fixtures and automated tests before moving a stage into the trusted pipeline. Test parser bounds, deterministic serialization, units/CRS, XYZ values, triangle topology, breaklines/boundaries/layers, degeneracy, constrained TIN, PDF calibration, round trips, malformed input, and golden-reference regressions.

## Machine-control gate
Production readiness requires software validation plus controlled Topcon import/visual inspection. Initial field testing is guidance-only with automatic control disabled. Automatic blade control is a later gate after independent coordinate/elevation/surface checks.

## Copilot behavior
Read all files under `docs/` before architectural changes. State assumptions. Mark unknown TP3 fields UNKNOWN rather than inventing semantics. Isolate experimental reverse-engineering from trusted exporters. Keep modules small/testable/deterministic. Never delete raw evidence. Every format discovery should create a reproducible test or documented observation.

# Tinforge V3 — Architecture

## Principle
Keep acquisition, engineering geometry, validation and vendor serialization separate. A proprietary exporter is never the source of truth.

## Canonical model
Explicit units, CRS/localization metadata, XYZ points/IDs, 2D/3D polylines, breaklines, boundaries, layers/features, surfaces, vertices, triangle topology and source provenance. Use double precision and never silently transform units/CRS.

## Suggested modules
- `core/`: domain objects, units, CRS descriptors, validation types.
- `importers/`: PDF calibration/tracing, point/CSV and civil-format imports.
- `surface/`: constrained triangulation, boundaries, breaklines, topology checks, sampling/comparison.
- `formats/tp3/`: structural parser, raw inspection, known-field mapping, experimental serializer and validators.
- `formats/landxml/`, `formats/maxml/`: verified interchange paths.
- `validation/`: project, geometry, CRS, topology and export gates.
- `ui/`: project setup, calibration, layer/feature editing, surface inspection, validation and export.
- `tests/fixtures/`: synthetic fixtures plus metadata/hashes for authorized golden references.

## Pipeline
Source -> calibrated geometry -> canonical model -> constrained TIN -> validation -> vendor/interchange export -> round-trip verification -> Topcon acceptance test.

## Fail-closed export
Require known units, CRS/localization state, finite XYZ coordinates, valid topology and triangle indices, no forbidden degeneracy, and explicit export target/profile.

## Reproducibility
Identical project data and export profile should produce deterministic output where the format permits it. Store validation reports and tool/version information with test artifacts.

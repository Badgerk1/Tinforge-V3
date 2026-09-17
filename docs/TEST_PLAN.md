# Tinforge V3 — Test and Acceptance Plan

Testing is mandatory at every build stage.

## Stage 0 — Golden integrity
Hash reference TP3/PDFs, preserve originals read-only, record sizes/metadata, independently confirm expected observations.

## Stage 1 — TP3 parser
Test signature/container detection, bounds/length safety, malformed/truncated files, deterministic parsing, known strings/metadata, vertex XYZ/counts, triangle indices/counts, layers, CRS/units and unknown-record preservation.

## Stage 2 — Canonical geometry
Test unit round trips, finite/range checks, stable IDs, layer ownership, breakline/boundary invariants and vertex/triangle references.

## Stage 3 — PDF calibration/import
Test multi-point calibration, rotation/scale, known-coordinate residuals, elevations, page transforms and save/reload. Establish an explicit project tolerance before acceptance.

## Stage 4 — Surface construction
Test planes/slopes, boundaries/holes, breaklines, duplicate/collinear/near-coincident points, constrained edges, triangle orientation/index validity and sampled elevations.

## Stage 5 — Export
Test deterministic output, units/CRS, layers/features, surface topology, round trips and comparison with an independent reader/tool where available.

## Stage 6 — Golden project reconstruction
Rebuild the Purolator reference as far as source PDFs allow and compare extents, representative XYZ, sampled surface elevations, boundaries/breaklines and layer semantics. Do not force identical triangulation just to match counts unless the same constraints/algorithm should reproduce it.

## Stage 7 — Topcon acceptance
Import using target Topcon workflow. Verify CRS/units, plan/3D surface, known points/elevations, cut/fill direction/magnitude, boundaries and linework. Initial machine test is guidance/display only with automatic control disabled.

## Stage 8 — Controlled machine validation
After Stage 7: independently verify machine calibration/localization, occupy known control, compare machine-derived elevations to known values, and test in a non-production area before automatic blade control.

## Regression rule
Every discovered bug gets a reproducing automated test before the fix is considered complete.

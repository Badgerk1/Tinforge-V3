# Tinforge V3 — GitHub Copilot Instructions

## Mission
Build a reliable Tinforge V3 pipeline for Topcon-compatible machine-control project data. The professional `Purolator NP 2026.tp3` is the golden reference. Do not revive or copy the rejected Tinforge TP3 writer from earlier versions.

## Current stage: Stage 2 — TP3 writer
Stage 1 established a verified reader-side model for the professional `design grade` TIN. Stage 2 reverses that proven representation into a writer.

### Verified surface facts from the golden reference
- TP3 is binary and begins with the Topcon TP3 signature.
- The golden `design grade` surface has 53 vertices and 76 triangles.
- Surface vertices use local XY coordinates relative to a stored surface/project origin plus elevation Z.
- Each verified triangle record is 24 bytes and contains three vertex indexes and three neighboring-triangle indexes.
- Golden vertex indexes span 0–52 and all 53 vertices are used.
- Golden neighboring-triangle references span 0–75 where present and reciprocal adjacency has been validated.
- The reconstructed golden mesh has no zero-area triangles and satisfies its expected planar TIN topology.

Treat only facts backed by repository research/tests as VERIFIED. Label anything else HYPOTHESIS or UNKNOWN.

## Required implementation order
1. Read `COPILOT_INSTRUCTIONS.md`, `docs/PROJECT_CONTEXT.md`, `docs/TP3_RESEARCH.md`, `docs/ARCHITECTURE.md`, `docs/TEST_PLAN.md`, and `docs/WORK_LOG.md` before changing format code.
2. Keep the canonical surface/TIN model independent of TP3 serialization.
3. Implement deterministic TIN validation and triangle adjacency generation first.
4. Create a deliberately tiny synthetic surface fixture with known XYZ vertices and known triangles.
5. Implement serialization only for TP3 fields whose meaning and encoding are verified.
6. Parse every generated artifact back through Tinforge and compare geometry/topology to the input model.
7. Reconstruct the golden Purolator `design grade` surface from decoded data and compare counts, coordinates, triangle connectivity, adjacency, extents, elevations and topology.
8. Fail closed if any required TP3 field is still unknown. Never fill undocumented fields with guessed constants merely to produce a file.

## Testing gates
No Stage 2 writer is considered complete unless tests cover:
- deterministic output for identical inputs;
- vertex count and XYZ round trip within documented tolerances;
- triangle count and vertex-index round trip;
- reciprocal neighbor adjacency;
- no invalid/out-of-range indexes;
- no zero-area triangles;
- edge/manifold and boundary consistency;
- corrupt/truncated input rejection;
- golden-reference regression;
- generated-file reparse validation.

Every discovered bug gets a reproducing regression test before the fix is accepted.

## Safety / machine-control gate
A generated file passing unit tests is NOT automatically safe for machine control. Do not claim Topcon compatibility until the file has also passed controlled import/visual verification in appropriate Topcon software. Initial machine testing must be guidance-only with automatic blade control disabled until coordinates, units, elevations, boundaries and surface behavior are independently confirmed.

## Coding rules
- Preserve raw evidence and exact offsets used to justify binary-format conclusions.
- Separate parser, writer, geometry/TIN, validation and UI code.
- Prefer explicit dataclasses/types over opaque dictionaries for binary records.
- Binary reads/writes require bounds checks and explicit endianness.
- Never silently repair invalid geometry during serialization.
- Do not modify or overwrite the professional golden TP3.
- Keep experimental reverse-engineering code isolated from production export code.
- Append meaningful discoveries and validation results to `docs/WORK_LOG.md`.
- Update `docs/TP3_RESEARCH.md` when a hypothesis becomes verified or disproven.

## Immediate Copilot assignment
Implement the Stage 2 foundation: canonical TIN structures, validation, deterministic adjacency construction, a tiny synthetic fixture, and comprehensive unit tests. Then prepare the writer interfaces/record serializers only for fields already marked VERIFIED. Do not invent the remaining TP3 container fields. Stop at the first unverified field and document exactly what evidence is still required.

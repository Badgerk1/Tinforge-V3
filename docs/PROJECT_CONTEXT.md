# Tinforge V3 — Project Context

Tinforge V3 is a clean rebuild of the TinForge design-file workflow. Its immediate purpose is to take real civil/survey/design information and produce a verified Topcon-compatible design workflow suitable for Pocket3D and machine-control equipment such as dozers and excavators.

## Reference project
The prior `Badgerk1/tinforge` repository contains the comparison set under `real_survey_data`: professional `Purolator NP 2026.tp3`, source drawing `63287_001-C1.1 -R1.pdf`, and topo/elevation drawing `63287_002-TB1-ElevationsOn-24x30-Horiz-Topo.pdf`.

Prior authentic-file inspection observed a `design grade` surface, 53 vertices, 76 triangles, seven layers, metric units, and MTM Zone 10 / NAD83(CSRS v7). Revalidate these during implementation.

## Why V3
The previous TinForge custom TP3-generation path is not the baseline. A file that merely resembles TP3 is unacceptable for machine-control work. V3 is evidence-driven and continuously tested.

## Intended workflow
Create/open project -> verify units/CRS -> import source data -> calibrate PDFs -> trace/import points, elevations, linework, breaklines, boundaries and layers -> build constrained TIN -> validate -> export through a verified Topcon-compatible path -> round-trip inspect -> controlled Topcon acceptance testing.

## Success criterion
Success is not simply writing a file. The design must represent intended engineering geometry and CRS, survive round-trip validation, import correctly into the target Topcon workflow, and pass independent spot checks against the source design.

# Stage 1 Research Findings — 2026-09-17

## Verified from Topcon public documentation

Topcon's current Data Converter API explicitly recognizes TP3 as a 3DMC project format and exposes both TP3 upload and TP3 output/conversion operations. The same converter supports LandXML and MAXML, confirming that a standards/interchange conversion path is a legitimate architecture option rather than an invented workaround.

Topcon's current 3D-MC documentation states that 3D-MC can import TP3 projects and allows selecting the entire project or selected items, including surfaces and linework. This supports treating TP3 as a project/container rather than merely a single TIN surface file.

Topcon Pocket-3D documentation describes Topcon Project (TP3) alongside separate component formats. Current Topcon training material describes TP3 as capable of containing localization, linework, control, surfaces and related project data.

## Consequence for V3

The canonical V3 model must not equate TP3 with TN3. TP3 is the project-level artifact; component concepts remain separate internally. Export remains dual-path: verified native serialization after sufficient reverse engineering, or verified Topcon Data Converter/interchange conversion.

## Binary access status

The GitHub connector confirms the authentic golden TP3 exists in `Badgerk1/tinforge/real_survey_data` with Git blob SHA `5667f26aa160bf00735d6c08f0cde21c49633bb3` and size 446650 bytes. Attempting to read that blob through the text-oriented connector failed because TP3 is binary. No structural byte claims are inferred from that failure. A byte-capable local/CI fixture staging step is required before the structural inspector can generate the first real dump.

## Next evidence targets

1. Stage the golden TP3 as raw bytes in a development/CI runtime.
2. Compute raw SHA-256 and compare size/blob identity with the manifest.
3. Run the non-semantic inspector and preserve its JSON output.
4. Search exact string offsets for known project/surface/layer/CRS terms.
5. Locate candidate coordinate/elevation blocks using values independently read from source design.
6. Infer record boundaries only after repeated patterns/differential evidence support them.
7. Add each verified discovery as an automated golden-fixture assertion.

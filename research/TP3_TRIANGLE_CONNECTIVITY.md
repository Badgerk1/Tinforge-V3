# TP3 triangle connectivity — verified from Purolator NP 2026

Golden reference SHA-256: `423926032d368d2ebce9ffa9acfba3c5e467f200a13b1470d214962b45cb3207`
File size: 446,650 bytes.

## Verified surface header

Immediately before the UTF-16LE surface name `design grade`:

- byte 433766: little-endian uint32 = **53** (vertex count)
- byte 433770: little-endian uint32 = **76** (triangle count)
- byte 433774: little-endian uint32 = 0
- byte 433778: UTF-16LE `design grade`

This proves the previously observed 53/76 values are actual fields adjacent to the named surface, not coincidental search hits.

## Verified triangle table

A contiguous triangle table starts at byte **431906** and contains exactly **76 records**, each exactly **24 bytes** / six little-endian signed int32 values:

`<vertex0, vertex1, vertex2, neighbor0, neighbor1, neighbor2>`

Validation over all 76 records:

- first three values are always in range 0..52
- every vertex ID 0..52 is referenced at least once (53 unique vertices)
- last three values are always -1 or 0..75
- -1 acts as a boundary/no-neighbor sentinel
- maximum neighbor index is 75, exactly matching 76 zero-based triangles

Examples:

- triangle 0: `(0, 1, 2, 30, 42, 34)`
- triangle 1: `(3, 4, 5, -1, 58, 59)`
- triangle 2: `(6, 7, 8, 19, -1, -1)`
- triangle 3: `(9, 10, 11, 18, 4, 17)`
- triangle 4: `(10, 12, 11, 21, -1, 3)`
- triangle 5: `(1, 13, 14, 28, 38, 43)`
- triangle 6: `(15, 16, 17, 25, 8, 56)`
- triangle 7: `(18, 19, 20, 23, 69, 22)`
- triangle 75: `(15, 19, 10, 56, 23, 18)`

The table ends at byte **433730**. A small metadata block follows before the count fields at 433766.

## Important distinction

The 19 obvious XYZ triples at bytes 427092..431844 are survey/control point records at a 264-byte cadence. They are not the 53 design-surface vertices. The design vertices therefore use a different representation or reside elsewhere in the TP3. Do not incorrectly treat these 19 survey points as the TIN vertex table.

## Next reverse-engineering target

Locate and decode the 53 surface vertex coordinates referenced by the triangle table, then validate geometric adjacency and elevations against the professional design. Only after that should Tinforge attempt TN3/TP3 surface serialization.

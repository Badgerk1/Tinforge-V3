# TP3 Surface Binary Map — Purolator NP 2026

Status: evidence from the professional golden TP3 only. Do not generalize offsets to other TP3 files.

## Golden file

- Size: 446650 bytes
- Raw SHA-256: `423926032d368d2ebce9ffa9acfba3c5e467f200a13b1470d214962b45cb3207`
- Surface name `design grade` (UTF-16LE): byte offset 433778

## VERIFIED: triangle topology table

A contiguous table begins at byte offset **431906** and occupies exactly **1824 bytes**.

It decodes as **456 little-endian signed 32-bit integers**, which partitions exactly into **76 records x 6 integers**.

For each record:

- integers 0..2 are vertex indices
- integers 3..5 are neighboring-triangle indices, with `-1` used at an exterior/boundary edge

Evidence:

- There are exactly 76 six-integer records.
- The first three fields span exactly vertex IDs **0 through 52**, with all 53 IDs represented.
- The final three fields contain triangle IDs in **0 through 75** plus `-1` sentinels.
- This independently reproduces the previously observed 53-vertex / 76-triangle surface counts from the binary itself.

First records:

```text
triangle 0: vertices [0,1,2]   neighbors [30,42,34]
triangle 1: vertices [3,4,5]   neighbors [-1,58,59]
triangle 2: vertices [6,7,8]   neighbors [19,-1,-1]
triangle 3: vertices [9,10,11] neighbors [18,4,17]
triangle 4: vertices [10,12,11] neighbors [21,-1,3]
```

## VERIFIED: surface vertex block

A contiguous vertex table begins at byte offset **380120** and occupies exactly **1272 bytes**.

It decodes as **53 records x 24 bytes**, where each record is three little-endian IEEE-754 float64 values:

`local_x, local_y, elevation_z`

Validation:

- the 53 decoded records align exactly with the verified 53-vertex count near the surface name;
- local X spans `-56.881774900015444 .. 56.881774900015444`;
- local Y spans `-77.34722137451172 .. 77.34722137544304`;
- elevation Z spans `168.65 .. 171.25`;
- when indexed through the verified 76-triangle table, the reconstructed mesh has no zero-area triangles and satisfies reciprocal adjacency/boundary expectations.

Examples:

```text
vertex 0:  (29.948791500006337, -44.49799347482622, 170.45)
vertex 1:  (28.356750489969272, -54.3188858050853, 170.2)
vertex 52: (47.70098876999691, 62.317619315348566, 170.5)
```

## VERIFIED: stored local-origin doubles

Two consecutive little-endian float64 values at byte offsets **433908** and **433916** decode to:

```text
295399.97869873
4843987.442024235
```

Adding the verified local XY vertex coordinates to those values yields plausible project easting/northing extents `295343.09692383 .. 295456.86047363` and `4843910.09480286 .. 4844064.78924561`. For this golden surface, the evidence now supports treating those doubles as the stored local-origin coordinates.

## Remaining unknown

The exact enclosing surface/container structure around the verified vertex table, triangle table, count fields and origin doubles still needs to be mapped before any full native TP3 writer can be considered safe.

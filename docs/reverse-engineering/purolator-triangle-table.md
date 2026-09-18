# Purolator NP 2026.tp3 — verified triangle table

Golden reference SHA-256: `423926032d368d2ebce9ffa9acfba3c5e467f200a13b1470d214962b45cb3207`

Verified from the raw 446,650-byte TP3 binary.

## Surface summary anchor

Near the UTF-16LE string `design grade` at byte offset 433778, the binary contains little-endian counts `53` and `76`, matching the known design surface vertex and triangle counts.

## Triangle connectivity table

A contiguous table begins at byte offset **431906** and contains exactly **456 signed little-endian int32 values = 76 records × 6 int32 fields**.

For every one of the 76 records:

- fields 0, 1, 2 are in the range 0..52, exactly matching zero-based references to 53 vertices;
- fields 3, 4, 5 are in the range -1..75 and behave like triangle-neighbor/adjacency references, where -1 represents no neighbor/boundary.

First records:

```
triangle 0: vertices [0,1,2], neighbors [30,42,34]
triangle 1: vertices [3,4,5], neighbors [-1,58,59]
triangle 2: vertices [6,7,8], neighbors [19,-1,-1]
triangle 3: vertices [9,10,11], neighbors [18,4,17]
triangle 4: vertices [10,12,11], neighbors [21,-1,3]
triangle 5: vertices [1,13,14], neighbors [28,38,43]
triangle 6: vertices [15,16,17], neighbors [25,8,56]
triangle 7: vertices [18,19,20], neighbors [23,69,22]
```

This is strong structural proof of the TP3 TIN triangle record layout for this reference file, not a heuristic guess.

## Remaining Stage 1 item

The exact 53-record vertex/XYZ table still needs to be mapped and correlated to these zero-based indices before Stage 1 is declared complete. Do not hard-code an assumed vertex offset/stride until that mapping is proven.

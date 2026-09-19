# TP3 Container Map — Stage 4 reconstruction (2026-09-19)

Golden source: original professional `Purolator NP 2026.tp3`

- SHA-256: `423926032d368d2ebce9ffa9acfba3c5e467f200a13b1470d214962b45cb3207`
- size: `446650` bytes

## VERIFIED container-header layout (surface-region chain)

From byte offset `374918` to EOF, the file decodes deterministically as a contiguous chain of container records with 18-byte headers:

- header struct: `<HHHHHii>`
- header size field (`u16 #2`) is `18` for every record in this chain
- payload bytes start immediately after each 18-byte header
- payload size equals `record_count * record_size`
- next header starts exactly at current `payload_end`
- final record ends exactly at EOF

Verified records:

| offset | type (`u16 #1`) | `u16 #3` | record_count (`u16 #4`) | record_size (`u16 #5`) | `i32 #1` | `i32 #2` | payload_end |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 374918 | 2  | 1024 | 269 | 24  | -2 | 350324 | 381392 |
| 381392 | 6  | 1024 | 293 | 10  | -2 | -2 | 384340 |
| 384340 | 7  | 1024 | 165 | 18  | -2 | -2 | 387328 |
| 387328 | 8  | 512  | 43  | 34  | -2 | -2 | 388808 |
| 388808 | 9  | 256  | 17  | 66  | -2 | -2 | 389948 |
| 389948 | 10 | 128  | 5   | 130 | -2 | -2 | 390616 |
| 390616 | 5  | 1024 | 523 | 18  | -2 | -2 | 400048 |
| 400048 | 11 | 128  | 7   | 340 | -2 | -2 | 402446 |
| 402446 | 13 | 128  | 77  | 4   | -2 | 349794 | 402772 |
| 402772 | 12 | 1024 | 752 | 32  | -2 | -2 | 426854 |
| 426854 | 15 | 32   | 19  | 264 | -2 | -2 | 431888 |
| 431888 | 14 | 1024 | 76  | 24  | -2 | -2 | 433730 |
| 433730 | 17 | 32   | 1   | 332 | -2 | -2 | 434080 |
| 434080 | 21 | 1024 | 523 | 24  | -2 | -2 | 446650 |

## VERIFIED linkage to Stage 3 surface blocks

- Type-14 record at `431888` encloses `76 * 24` payload bytes.
- That payload starts at `431906` and matches the verified Stage 3 triangle block exactly.
- Type-17 record at `433730` encloses a single `332`-byte payload.
- Inside that payload:
  - `uint32LE @ 433766 == 53`
  - `uint32LE @ 433770 == 76`
  - UTF-16LE `design grade` name starts at `433778`
  - candidate doubles at `433908` and `433916` are present (semantics still not fully proven)

## HYPOTHESIS / UNKNOWN

- Semantic meaning of `u16 #3` and the two `i32` header fields.
- Full object graph semantics between type IDs (2,5,6,...,21).
- Definitive semantic role of candidate doubles at `433908` / `433916` (still SUPPORTED HYPOTHESIS).
- Any additional TP3 structures before `374918` that may participate in global container/object linking.

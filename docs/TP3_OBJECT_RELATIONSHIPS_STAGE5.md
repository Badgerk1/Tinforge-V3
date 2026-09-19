# TP3 Object Relationships — Stage 5 differential research (2026-09-19)

Golden source authority: original professional `Purolator NP 2026.tp3`

- SHA-256: `423926032d368d2ebce9ffa9acfba3c5e467f200a13b1470d214962b45cb3207`

## VERIFIED

1. **surface metadata -> vertex geometry linkage**
   - Type-17 payload contains `uint32LE` vertex count at absolute offset `433766` (relative `+18`).
   - Value is `53`, matching the verified vertex block (`380120:381392`, `53 * 24` bytes).

2. **surface metadata -> triangle geometry linkage**
   - Type-17 payload contains `uint32LE` triangle count at absolute offset `433770` (relative `+22`).
   - Value is `76`, matching type-14 `record_count=76` and the verified triangle block (`431906:433730`, `76 * 24` bytes).

3. **type-17 payload anchors**
   - Type-17 header at `433730`, payload start `433748`, payload size `332`.
   - UTF-16LE surface name `design grade` starts at absolute `433778` (relative `+30`) inside this payload.
   - Candidate doubles are at absolute `433908` / `433916` (relative `+160` / `+168`) inside this payload.

4. **18-byte container header structure**
   - Surface-region chain remains reproducibly decodable as `<HHHHHii>` with `header_size=18`.
   - Type-14 payload still byte-identical to the verified triangle block.

## SUPPORTED HYPOTHESIS

1. **container link fields as cross-region references**
   - Non-sentinel link values in the surface-region chain:
     - `type-2.link_next = 350324`
     - `type-13.link_next = 349794`
   - Both are in file bounds and both point before the Stage-4 surface-region start offset (`374918`).
   - These are plausible cross-region object-directory/table references, but target semantics remain unproven.

2. **candidate origin/localization fields**
   - `float64LE @ 433908 = 295399.97869873`
   - `float64LE @ 433916 = 4843987.442024235`
   - Placement inside type-17 metadata and numeric plausibility support origin/localization semantics, but proof is still incomplete.

## UNKNOWN

1. Semantic meaning of container-header `u16 #3` (`field_2`) values.
2. Directionality/meaning of `i32 #1` (`link_prev`) and `i32 #2` (`link_next`) beyond sentinel behavior.
3. Definitive identity and layout of any pre-`374918` object directory/table structures referenced by link fields.
4. Full verified field map for the remaining bytes of the 332-byte type-17 payload.

## REJECTED HYPOTHESIS

1. **"Surface name is outside type-17 payload."**
   - Rejected: `design grade` at `433778` is inside type-17 payload range `433748:434080`.

## Evidence still required for next verification step

1. Differential pair(s) from authoritative Topcon tooling where only one object-linking property changes.
2. Byte-level diffs proving the target structures for link values `350324` and `349794`.
3. Controlled edits proving exact semantics for type-17 bytes outside currently verified count/name/candidate-origin anchors.

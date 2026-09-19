"""Stage 2 TP3 writer foundation for VERIFIED fields only."""

from __future__ import annotations

from dataclasses import dataclass
import struct

from tinforge.surface import SurfaceTIN, validate_tin, with_deterministic_adjacency

TP3_SIGNATURE = b"Topcon TP3"
TRIANGLE_RECORD_SIZE_BYTES = 24


class Tp3SerializationBlockedError(RuntimeError):
    """Raised when serialization reaches an UNKNOWN TP3 field."""


@dataclass(frozen=True)
class TriangleRecord:
    """VERIFIED triangle layout: 3 vertex indices + 3 neighbor indices (int32 LE)."""

    vertex_indices: tuple[int, int, int]
    neighbor_indices: tuple[int, int, int]


def _as_int32(value: int, *, label: str) -> int:
    if value < -(2**31) or value > 2**31 - 1:
        raise ValueError(f"{label}={value} does not fit signed int32")
    return value


def encode_triangle_record(record: TriangleRecord) -> bytes:
    """Encode one VERIFIED 24-byte TP3 triangle record."""

    fields = (*record.vertex_indices, *record.neighbor_indices)
    for i, value in enumerate(fields):
        _as_int32(value, label=f"field_{i}")
    return struct.pack("<6i", *fields)


def decode_triangle_record(data: bytes, offset: int = 0) -> TriangleRecord:
    """Decode one VERIFIED 24-byte TP3 triangle record."""

    if offset < 0 or offset + TRIANGLE_RECORD_SIZE_BYTES > len(data):
        raise ValueError("triangle record offset outside buffer")
    values = struct.unpack_from("<6i", data, offset)
    return TriangleRecord(vertex_indices=values[:3], neighbor_indices=values[3:])


def serialize_triangle_table(surface: SurfaceTIN) -> bytes:
    """Serialize VERIFIED triangle table bytes from canonical TIN input."""

    surface_with_neighbors = with_deterministic_adjacency(surface)
    validate_tin(surface_with_neighbors, require_neighbors=True)

    chunks: list[bytes] = []
    for tri in surface_with_neighbors.triangles:
        neighbors = tuple(-1 if n is None else n for n in tri.neighbor_indices)
        record = TriangleRecord(vertex_indices=tri.vertex_indices, neighbor_indices=neighbors)
        chunks.append(encode_triangle_record(record))
    return b"".join(chunks)


def deserialize_triangle_table(data: bytes, triangle_count: int) -> tuple[TriangleRecord, ...]:
    """Decode VERIFIED triangle table bytes into triangle records."""

    if triangle_count < 0:
        raise ValueError("triangle_count must be >= 0")
    expected_bytes = triangle_count * TRIANGLE_RECORD_SIZE_BYTES
    if len(data) != expected_bytes:
        raise ValueError(
            f"triangle table length {len(data)} does not match expected {expected_bytes} bytes"
        )
    return tuple(
        decode_triangle_record(data, offset=i * TRIANGLE_RECORD_SIZE_BYTES) for i in range(triangle_count)
    )


def build_tp3_project_bytes(surface: SurfaceTIN) -> bytes:
    """Fail closed: block full TP3 serialization when required fields are UNKNOWN."""

    serialize_triangle_table(surface)
    raise Tp3SerializationBlockedError(
        "TP3 serialization blocked at first UNKNOWN field: vertex XYZ payload and surface/container "
        "record boundaries are not VERIFIED, including the exact local-XY-plus-origin encoding, "
        "surface object headers, and project-level container cross-reference/check fields. "
        "Required evidence: byte offsets and field layouts in golden TP3 proving the 53-vertex XYZ "
        "table and all enclosing record lengths/links needed to emit a valid TP3 container."
    )

from __future__ import annotations

import struct
from dataclasses import dataclass

from tinforge.surface import (
    SurfaceTIN,
    SurfaceTriangle,
    validate_tin,
    validate_triangle_topology,
)

TRIANGLE_RECORD_STRUCT = struct.Struct("<6i")
UNKNOWN_VERTEX_LAYOUT_EVIDENCE = (
    "UNKNOWN TP3 field: surface vertex XYZ storage layout and enclosing surface/container "
    "records. Evidence still required: exact byte offsets, record boundaries, endianness, "
    "and semantic mapping for the golden surface vertex table and surrounding metadata."
)


class UnknownTP3FieldError(RuntimeError):
    """Raised when serialization reaches an unverified TP3 field."""


@dataclass(frozen=True)
class TP3TriangleRecord:
    vertex_0: int
    vertex_1: int
    vertex_2: int
    neighbor_0: int
    neighbor_1: int
    neighbor_2: int

    @classmethod
    def from_triangle(cls, triangle: SurfaceTriangle) -> "TP3TriangleRecord":
        return cls(*triangle.vertices, *triangle.neighbors)

    def to_bytes(self) -> bytes:
        return TRIANGLE_RECORD_STRUCT.pack(
            self.vertex_0,
            self.vertex_1,
            self.vertex_2,
            self.neighbor_0,
            self.neighbor_1,
            self.neighbor_2,
        )


def triangle_records_from_surface(surface: SurfaceTIN) -> tuple[TP3TriangleRecord, ...]:
    validate_tin(surface)
    return tuple(TP3TriangleRecord.from_triangle(triangle) for triangle in surface.triangles)


def serialize_triangle_records(surface: SurfaceTIN) -> bytes:
    return b"".join(record.to_bytes() for record in triangle_records_from_surface(surface))


def parse_triangle_records(
    data: bytes,
    *,
    vertex_count: int,
) -> tuple[TP3TriangleRecord, ...]:
    if len(data) % TRIANGLE_RECORD_STRUCT.size != 0:
        raise ValueError("triangle record buffer is truncated")
    records = tuple(
        TP3TriangleRecord(*record)
        for record in TRIANGLE_RECORD_STRUCT.iter_unpack(data)
    )
    triangle_count = len(records)
    for record_index, record in enumerate(records):
        vertex_indexes = (record.vertex_0, record.vertex_1, record.vertex_2)
        for vertex_index in vertex_indexes:
            if not 0 <= vertex_index < vertex_count:
                raise ValueError(
                    f"triangle record {record_index} references invalid vertex {vertex_index}"
                )
        neighbor_indexes = (record.neighbor_0, record.neighbor_1, record.neighbor_2)
        for neighbor_index in neighbor_indexes:
            if neighbor_index != -1 and not 0 <= neighbor_index < triangle_count:
                raise ValueError(
                    f"triangle record {record_index} references invalid neighbor {neighbor_index}"
                )
    validate_triangle_topology(
        vertex_count,
        tuple(
            SurfaceTriangle(
                vertices=(record.vertex_0, record.vertex_1, record.vertex_2),
                neighbors=(record.neighbor_0, record.neighbor_1, record.neighbor_2),
            )
            for record in records
        ),
    )
    return records


def serialize_tp3(surface: SurfaceTIN) -> bytes:
    validate_tin(surface)
    raise UnknownTP3FieldError(UNKNOWN_VERTEX_LAYOUT_EVIDENCE)

from __future__ import annotations

import struct

from tinforge.surface import SurfaceTIN, SurfaceTriangle, SurfaceVertex, TINValidationError, validate_tin
from tinforge.tp3.writer import TRIANGLE_RECORD_STRUCT, parse_triangle_records

GOLDEN_DESIGN_GRADE_VERTEX_BLOCK_OFFSET = 380120
GOLDEN_DESIGN_GRADE_VERTEX_COUNT_OFFSET = 433766
GOLDEN_DESIGN_GRADE_TRIANGLE_COUNT_OFFSET = 433770
GOLDEN_DESIGN_GRADE_TRIANGLE_TABLE_OFFSET = 431906
GOLDEN_DESIGN_GRADE_NAME_OFFSET = 433778
GOLDEN_DESIGN_GRADE_ORIGIN_X_OFFSET = 433908
GOLDEN_DESIGN_GRADE_ORIGIN_Y_OFFSET = 433916
GOLDEN_DESIGN_GRADE_NAME = "design grade"
GOLDEN_DESIGN_GRADE_VERTEX_COUNT = 53
GOLDEN_DESIGN_GRADE_TRIANGLE_COUNT = 76
TP3_VERTEX_RECORD_STRUCT = struct.Struct("<3d")
U32LE = struct.Struct("<I")
F64LE = struct.Struct("<d")


class TP3SurfaceDecodeError(TINValidationError):
    """Raised when a verified TP3 surface block cannot be decoded safely."""


def _slice_bytes(data: bytes, *, absolute_offset: int, size: int, base_offset: int) -> bytes:
    relative_offset = absolute_offset - base_offset
    if relative_offset < 0 or relative_offset + size > len(data):
        raise TP3SurfaceDecodeError(
            f"buffer does not contain verified bytes at absolute offset {absolute_offset}"
        )
    return data[relative_offset : relative_offset + size]


def _read_u32le(data: bytes, *, absolute_offset: int, base_offset: int) -> int:
    return U32LE.unpack(_slice_bytes(data, absolute_offset=absolute_offset, size=4, base_offset=base_offset))[0]


def _read_f64le(data: bytes, *, absolute_offset: int, base_offset: int) -> float:
    return F64LE.unpack(
        _slice_bytes(data, absolute_offset=absolute_offset, size=F64LE.size, base_offset=base_offset)
    )[0]


def _read_utf16le_null_terminated(data: bytes, *, absolute_offset: int, base_offset: int) -> str:
    relative_offset = absolute_offset - base_offset
    if relative_offset < 0 or relative_offset >= len(data):
        raise TP3SurfaceDecodeError(
            f"buffer does not contain verified bytes at absolute offset {absolute_offset}"
        )
    end = relative_offset
    while end + 1 < len(data):
        if data[end : end + 2] == b"\x00\x00":
            return data[relative_offset:end].decode("utf-16le")
        end += 2
    raise TP3SurfaceDecodeError(f"unterminated UTF-16LE string at absolute offset {absolute_offset}")


def parse_vertex_records(
    data: bytes,
    *,
    offset: int,
    count: int,
    base_offset: int = 0,
) -> tuple[SurfaceVertex, ...]:
    records = []
    for record_index in range(count):
        record_offset = offset + (record_index * TP3_VERTEX_RECORD_STRUCT.size)
        local_x, local_y, elevation = TP3_VERTEX_RECORD_STRUCT.unpack(
            _slice_bytes(
                data,
                absolute_offset=record_offset,
                size=TP3_VERTEX_RECORD_STRUCT.size,
                base_offset=base_offset,
            )
        )
        records.append(SurfaceVertex(x=local_x, y=local_y, z=elevation))
    return tuple(records)


def decode_golden_design_grade_surface(data: bytes, *, base_offset: int = 0) -> SurfaceTIN:
    vertex_count = _read_u32le(
        data,
        absolute_offset=GOLDEN_DESIGN_GRADE_VERTEX_COUNT_OFFSET,
        base_offset=base_offset,
    )
    triangle_count = _read_u32le(
        data,
        absolute_offset=GOLDEN_DESIGN_GRADE_TRIANGLE_COUNT_OFFSET,
        base_offset=base_offset,
    )
    if vertex_count != GOLDEN_DESIGN_GRADE_VERTEX_COUNT:
        raise TP3SurfaceDecodeError(
            f"expected {GOLDEN_DESIGN_GRADE_VERTEX_COUNT} vertices, found {vertex_count}"
        )
    if triangle_count != GOLDEN_DESIGN_GRADE_TRIANGLE_COUNT:
        raise TP3SurfaceDecodeError(
            f"expected {GOLDEN_DESIGN_GRADE_TRIANGLE_COUNT} triangles, found {triangle_count}"
        )

    surface_name = _read_utf16le_null_terminated(
        data,
        absolute_offset=GOLDEN_DESIGN_GRADE_NAME_OFFSET,
        base_offset=base_offset,
    )
    if surface_name != GOLDEN_DESIGN_GRADE_NAME:
        raise TP3SurfaceDecodeError(
            f"expected surface name {GOLDEN_DESIGN_GRADE_NAME!r}, found {surface_name!r}"
        )

    origin_x = _read_f64le(
        data,
        absolute_offset=GOLDEN_DESIGN_GRADE_ORIGIN_X_OFFSET,
        base_offset=base_offset,
    )
    origin_y = _read_f64le(
        data,
        absolute_offset=GOLDEN_DESIGN_GRADE_ORIGIN_Y_OFFSET,
        base_offset=base_offset,
    )

    vertices = parse_vertex_records(
        data,
        offset=GOLDEN_DESIGN_GRADE_VERTEX_BLOCK_OFFSET,
        count=vertex_count,
        base_offset=base_offset,
    )
    triangle_buffer = _slice_bytes(
        data,
        absolute_offset=GOLDEN_DESIGN_GRADE_TRIANGLE_TABLE_OFFSET,
        size=triangle_count * TRIANGLE_RECORD_STRUCT.size,
        base_offset=base_offset,
    )
    triangle_records = parse_triangle_records(triangle_buffer, vertex_count=vertex_count)
    surface = SurfaceTIN(
        name=surface_name,
        origin_x=origin_x,
        origin_y=origin_y,
        vertices=vertices,
        triangles=tuple(
            SurfaceTriangle(
                vertices=(record.vertex_0, record.vertex_1, record.vertex_2),
                neighbors=(record.neighbor_0, record.neighbor_1, record.neighbor_2),
            )
            for record in triangle_records
        ),
    )
    validate_tin(surface)
    return surface

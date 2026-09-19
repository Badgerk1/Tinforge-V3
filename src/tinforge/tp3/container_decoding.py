from __future__ import annotations

import struct
from dataclasses import dataclass

from tinforge.surface import TINValidationError

CONTAINER_HEADER_STRUCT = struct.Struct("<HHHHHii")
SURFACE_REGION_START_OFFSET = 374918


@dataclass(frozen=True)
class TP3ContainerHeader:
    offset: int
    object_type: int
    header_size: int
    field_2: int
    record_count: int
    record_size_bytes: int
    link_prev: int
    link_next: int

    @property
    def payload_offset(self) -> int:
        return self.offset + self.header_size

    @property
    def payload_size(self) -> int:
        return self.record_count * self.record_size_bytes

    @property
    def payload_end_offset(self) -> int:
        return self.payload_offset + self.payload_size


def decode_container_header(data: bytes, offset: int) -> TP3ContainerHeader:
    end = offset + CONTAINER_HEADER_STRUCT.size
    if offset < 0 or end > len(data):
        raise TINValidationError(f"container header {offset}:{end} exceeds TP3 bounds")

    (
        object_type,
        header_size,
        field_2,
        record_count,
        record_size_bytes,
        link_prev,
        link_next,
    ) = CONTAINER_HEADER_STRUCT.unpack_from(data, offset)

    if header_size != CONTAINER_HEADER_STRUCT.size:
        raise TINValidationError(
            f"container header at {offset} reports unsupported header size {header_size}"
        )
    header = TP3ContainerHeader(
        offset=offset,
        object_type=object_type,
        header_size=header_size,
        field_2=field_2,
        record_count=record_count,
        record_size_bytes=record_size_bytes,
        link_prev=link_prev,
        link_next=link_next,
    )
    if header.payload_end_offset > len(data):
        raise TINValidationError(
            f"container payload {header.payload_offset}:{header.payload_end_offset} exceeds TP3 bounds"
        )
    return header


def slice_container_payload(data: bytes, header: TP3ContainerHeader) -> bytes:
    return data[header.payload_offset : header.payload_end_offset]


def decode_surface_region_containers(
    data: bytes,
    *,
    start_offset: int = SURFACE_REGION_START_OFFSET,
) -> tuple[TP3ContainerHeader, ...]:
    if start_offset < 0 or start_offset >= len(data):
        raise TINValidationError("surface-region start offset is outside TP3 bounds")

    headers: list[TP3ContainerHeader] = []
    offset = start_offset
    while offset < len(data):
        header = decode_container_header(data, offset)
        headers.append(header)
        offset = header.payload_end_offset

    if offset != len(data):
        raise TINValidationError(
            f"surface-region decoding ended at {offset}, expected file end {len(data)}"
        )
    return tuple(headers)

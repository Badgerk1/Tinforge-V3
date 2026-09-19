from __future__ import annotations

import hashlib
import struct
from dataclasses import dataclass
from typing import Literal

from tinforge.surface import TINValidationError
from tinforge.tp3.container_decoding import (
    SURFACE_REGION_START_OFFSET,
    TP3ContainerHeader,
    decode_surface_region_containers,
    slice_container_payload,
)
from tinforge.tp3.surface_decoding import (
    TRIANGLE_RECORD_COUNT,
    VERTEX_BLOCK_OFFSET,
    VERTEX_RECORD_COUNT,
)

ConfidenceLabel = Literal[
    "VERIFIED",
    "SUPPORTED HYPOTHESIS",
    "UNKNOWN",
    "REJECTED HYPOTHESIS",
]

DEFAULT_LINK_SENTINEL = -2
SURFACE_NAME_UTF16LE = "design grade"
EXPECTED_FILE_SHA256 = "423926032d368d2ebce9ffa9acfba3c5e467f200a13b1470d214962b45cb3207"
TRIANGLE_RECORD_SIZE_BYTES = 24
TYPE17_VERTEX_COUNT_RELATIVE_OFFSET = 18
TYPE17_TRIANGLE_COUNT_RELATIVE_OFFSET = 22
TYPE17_SURFACE_NAME_RELATIVE_OFFSET = 30
TYPE17_SURFACE_NAME_BYTES = 24
TYPE17_ORIGIN_CANDIDATE_X_RELATIVE_OFFSET = 160
TYPE17_ORIGIN_CANDIDATE_Y_RELATIVE_OFFSET = 168


@dataclass(frozen=True)
class ClassifiedFinding:
    subject: str
    classification: ConfidenceLabel
    evidence: str


@dataclass(frozen=True)
class ContainerLinkReference:
    container_type: int
    container_offset: int
    field_name: str
    value: int
    is_in_bounds: bool
    matches_container_header_offset: bool
    inside_known_container_payload: bool
    points_before_surface_region: bool


@dataclass(frozen=True)
class Type17MetadataEvidence:
    payload_offset: int
    payload_size: int
    vertex_count: int
    triangle_count: int
    surface_name: str
    origin_candidate_x: float
    origin_candidate_y: float
    vertex_count_relative_offset: int
    triangle_count_relative_offset: int
    surface_name_relative_offset: int
    origin_candidate_x_relative_offset: int
    origin_candidate_y_relative_offset: int


@dataclass(frozen=True)
class Stage5ObjectRelationshipEvidence:
    file_sha256: str
    headers: tuple[TP3ContainerHeader, ...]
    link_references: tuple[ContainerLinkReference, ...]
    type17_metadata: Type17MetadataEvidence
    type14_payload_matches_verified_triangle_range: bool
    type14_payload_matches_verified_triangle_bytes: bool
    findings: tuple[ClassifiedFinding, ...]


def _u32_at(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def _f64_at(data: bytes, offset: int) -> float:
    return struct.unpack_from("<d", data, offset)[0]


def _find_type(headers: tuple[TP3ContainerHeader, ...], object_type: int) -> TP3ContainerHeader:
    try:
        return next(header for header in headers if header.object_type == object_type)
    except StopIteration as exc:
        raise TINValidationError(f"required container type {object_type} not found") from exc


def _require_range_in_payload(
    *,
    payload_start: int,
    payload_end: int,
    absolute_offset: int,
    size: int,
    label: str,
) -> None:
    end = absolute_offset + size
    if not (payload_start <= absolute_offset and end <= payload_end):
        raise TINValidationError(f"{label} range {absolute_offset}:{end} is outside type-17 payload")


def analyze_stage5_object_relationships(data: bytes) -> Stage5ObjectRelationshipEvidence:
    file_sha = enforce_golden_reference_identity(data)
    headers = decode_surface_region_containers(data)
    type2 = _find_type(headers, 2)
    type14 = _find_type(headers, 14)
    type17 = _find_type(headers, 17)

    type14_payload = slice_container_payload(data, type14)
    expected_triangle_payload_size = TRIANGLE_RECORD_COUNT * TRIANGLE_RECORD_SIZE_BYTES
    if type14.payload_size != expected_triangle_payload_size:
        raise TINValidationError(
            "type-14 payload size no longer matches verified triangle-record extent "
            f"({type14.payload_size} != {expected_triangle_payload_size})"
        )
    verified_triangle_payload_offset = type14.payload_offset
    verified_triangle_payload_end = type14.payload_end_offset
    verified_triangle_block = data[verified_triangle_payload_offset:verified_triangle_payload_end]
    type14_matches_verified_range = (
        verified_triangle_payload_offset == 431906
        and verified_triangle_payload_end == 433730
    )
    type14_matches_verified_bytes = type14_payload == verified_triangle_block

    type17_payload = slice_container_payload(data, type17)
    payload_start = type17.payload_offset
    payload_end = type17.payload_end_offset
    vertex_count_abs = payload_start + TYPE17_VERTEX_COUNT_RELATIVE_OFFSET
    triangle_count_abs = payload_start + TYPE17_TRIANGLE_COUNT_RELATIVE_OFFSET
    surface_name_abs = payload_start + TYPE17_SURFACE_NAME_RELATIVE_OFFSET
    origin_x_abs = payload_start + TYPE17_ORIGIN_CANDIDATE_X_RELATIVE_OFFSET
    origin_y_abs = payload_start + TYPE17_ORIGIN_CANDIDATE_Y_RELATIVE_OFFSET
    _require_range_in_payload(
        payload_start=payload_start,
        payload_end=payload_end,
        absolute_offset=vertex_count_abs,
        size=4,
        label="vertex count",
    )
    _require_range_in_payload(
        payload_start=payload_start,
        payload_end=payload_end,
        absolute_offset=triangle_count_abs,
        size=4,
        label="triangle count",
    )
    _require_range_in_payload(
        payload_start=payload_start,
        payload_end=payload_end,
        absolute_offset=surface_name_abs,
        size=TYPE17_SURFACE_NAME_BYTES,
        label="surface name",
    )
    _require_range_in_payload(
        payload_start=payload_start,
        payload_end=payload_end,
        absolute_offset=origin_x_abs,
        size=8,
        label="origin-candidate X",
    )
    _require_range_in_payload(
        payload_start=payload_start,
        payload_end=payload_end,
        absolute_offset=origin_y_abs,
        size=8,
        label="origin-candidate Y",
    )

    name_relative = TYPE17_SURFACE_NAME_RELATIVE_OFFSET
    surface_name = type17_payload[name_relative : name_relative + TYPE17_SURFACE_NAME_BYTES].decode(
        "utf-16le"
    ).rstrip("\x00")
    type17_metadata = Type17MetadataEvidence(
        payload_offset=type17.payload_offset,
        payload_size=type17.payload_size,
        vertex_count=_u32_at(data, vertex_count_abs),
        triangle_count=_u32_at(data, triangle_count_abs),
        surface_name=surface_name,
        origin_candidate_x=_f64_at(data, origin_x_abs),
        origin_candidate_y=_f64_at(data, origin_y_abs),
        vertex_count_relative_offset=TYPE17_VERTEX_COUNT_RELATIVE_OFFSET,
        triangle_count_relative_offset=TYPE17_TRIANGLE_COUNT_RELATIVE_OFFSET,
        surface_name_relative_offset=name_relative,
        origin_candidate_x_relative_offset=TYPE17_ORIGIN_CANDIDATE_X_RELATIVE_OFFSET,
        origin_candidate_y_relative_offset=TYPE17_ORIGIN_CANDIDATE_Y_RELATIVE_OFFSET,
    )

    references: list[ContainerLinkReference] = []
    for header in headers:
        for field_name, value in (("link_prev", header.link_prev), ("link_next", header.link_next)):
            if value == DEFAULT_LINK_SENTINEL:
                continue
            references.append(
                ContainerLinkReference(
                    container_type=header.object_type,
                    container_offset=header.offset,
                    field_name=field_name,
                    value=value,
                    is_in_bounds=0 <= value < len(data),
                    matches_container_header_offset=any(other.offset == value for other in headers),
                    inside_known_container_payload=any(
                        other.payload_offset <= value < other.payload_end_offset for other in headers
                    ),
                    points_before_surface_region=value < SURFACE_REGION_START_OFFSET,
                )
            )

    findings = (
        ClassifiedFinding(
            subject="18-byte container header size",
            classification="VERIFIED",
            evidence="All surface-region headers decode as <HHHHHii with header_size=18 from 374918 to EOF.",
        ),
        ClassifiedFinding(
            subject="type-14 triangle payload anchor",
            classification="VERIFIED",
            evidence=(
                f"type-14 payload range is {verified_triangle_payload_offset}:{verified_triangle_payload_end} "
                f"({expected_triangle_payload_size} bytes)."
            ),
        ),
        ClassifiedFinding(
            subject="surface metadata to vertex geometry linkage",
            classification="SUPPORTED HYPOTHESIS",
            evidence=(
                f"type-17 vertex_count={type17_metadata.vertex_count} matches verified "
                f"vertex block record count={VERTEX_RECORD_COUNT} at offset {VERTEX_BLOCK_OFFSET}, "
                "but no explicit type-17 pointer/reference to that vertex container is proven."
            ),
        ),
        ClassifiedFinding(
            subject="surface metadata to triangle geometry linkage",
            classification="SUPPORTED HYPOTHESIS",
            evidence=(
                f"type-17 triangle_count={type17_metadata.triangle_count} matches type-14 record_count "
                f"and verified triangle block count={TRIANGLE_RECORD_COUNT}, but no explicit type-17 "
                "pointer/reference to type-14 ownership is proven."
            ),
        ),
        ClassifiedFinding(
            subject="type-17 surface metadata payload anchors",
            classification="VERIFIED",
            evidence=(
                f"Inside the 332-byte payload: vertex_count@+{type17_metadata.vertex_count_relative_offset}, "
                f"triangle_count@+{type17_metadata.triangle_count_relative_offset}, "
                f"name@+{type17_metadata.surface_name_relative_offset}='{type17_metadata.surface_name}'."
            ),
        ),
        ClassifiedFinding(
            subject="container link fields as cross-region object references",
            classification="SUPPORTED HYPOTHESIS",
            evidence=(
                "Two non-sentinel link values are in-bounds and point before surface-region start "
                f"({SURFACE_REGION_START_OFFSET}): type-2.link_next=350324 and type-13.link_next=349794."
            ),
        ),
        ClassifiedFinding(
            subject="candidate origin/localization doubles in type-17",
            classification="SUPPORTED HYPOTHESIS",
            evidence=(
                f"float64 values at +{type17_metadata.origin_candidate_x_relative_offset} and "
                f"+{type17_metadata.origin_candidate_y_relative_offset} are "
                f"{type17_metadata.origin_candidate_x} and {type17_metadata.origin_candidate_y}."
            ),
        ),
        ClassifiedFinding(
            subject="semantic meaning of container field_2 and link directionality",
            classification="UNKNOWN",
            evidence="field_2 values and link_prev/link_next semantics are not proven by current evidence.",
        ),
        ClassifiedFinding(
            subject="type-17 name location outside container payload",
            classification="REJECTED HYPOTHESIS",
            evidence="Surface-name bytes at 433778 are proven to lie within the type-17 payload range.",
        ),
    )

    return Stage5ObjectRelationshipEvidence(
        file_sha256=file_sha,
        headers=headers,
        link_references=tuple(references),
        type17_metadata=type17_metadata,
        type14_payload_matches_verified_triangle_range=type14_matches_verified_range,
        type14_payload_matches_verified_triangle_bytes=type14_matches_verified_bytes,
        findings=findings,
    )


def enforce_golden_reference_identity(data: bytes) -> str:
    file_sha = hashlib.sha256(data).hexdigest()
    if file_sha != EXPECTED_FILE_SHA256:
        raise TINValidationError(
            "unexpected TP3 SHA-256 for stage-5 object-relationship evidence: "
            f"{file_sha} (expected {EXPECTED_FILE_SHA256})"
        )
    return file_sha

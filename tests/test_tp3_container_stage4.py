import hashlib

import pytest

from tinforge.surface import TINValidationError
from tinforge.tp3.container_decoding import (
    SURFACE_REGION_START_OFFSET,
    decode_container_header,
    decode_surface_region_containers,
    slice_container_payload,
)
from tinforge.tp3.surface_decoding import (
    COUNT_TRIANGLE_OFFSET,
    COUNT_VERTEX_OFFSET,
    ORIGIN_CANDIDATE_X_OFFSET,
    ORIGIN_CANDIDATE_Y_OFFSET,
    TRIANGLE_BLOCK_OFFSET,
    TRIANGLE_RECORD_COUNT,
)

EXPECTED_FILE_SHA256 = "423926032d368d2ebce9ffa9acfba3c5e467f200a13b1470d214962b45cb3207"

EXPECTED_HEADERS = (
    (374918, 2, 1024, 269, 24, -2, 350324),
    (381392, 6, 1024, 293, 10, -2, -2),
    (384340, 7, 1024, 165, 18, -2, -2),
    (387328, 8, 512, 43, 34, -2, -2),
    (388808, 9, 256, 17, 66, -2, -2),
    (389948, 10, 128, 5, 130, -2, -2),
    (390616, 5, 1024, 523, 18, -2, -2),
    (400048, 11, 128, 7, 340, -2, -2),
    (402446, 13, 128, 77, 4, -2, 349794),
    (402772, 12, 1024, 752, 32, -2, -2),
    (426854, 15, 32, 19, 264, -2, -2),
    (431888, 14, 1024, 76, 24, -2, -2),
    (433730, 17, 32, 1, 332, -2, -2),
    (434080, 21, 1024, 523, 24, -2, -2),
)


def test_surface_region_headers_decode_from_original_professional_tp3(
    original_professional_tp3_bytes: bytes,
):
    assert hashlib.sha256(original_professional_tp3_bytes).hexdigest() == EXPECTED_FILE_SHA256

    headers = decode_surface_region_containers(original_professional_tp3_bytes)
    assert len(headers) == len(EXPECTED_HEADERS)

    for parsed, expected in zip(headers, EXPECTED_HEADERS, strict=True):
        (
            expected_offset,
            expected_type,
            expected_field_2,
            expected_record_count,
            expected_record_size,
            expected_link_prev,
            expected_link_next,
        ) = expected
        assert parsed.offset == expected_offset
        assert parsed.object_type == expected_type
        assert parsed.header_size == 18
        assert parsed.field_2 == expected_field_2
        assert parsed.record_count == expected_record_count
        assert parsed.record_size_bytes == expected_record_size
        assert parsed.link_prev == expected_link_prev
        assert parsed.link_next == expected_link_next


def test_surface_region_headers_are_contiguous_to_file_end(
    original_professional_tp3_bytes: bytes,
):
    headers = decode_surface_region_containers(original_professional_tp3_bytes)

    assert headers[0].offset == SURFACE_REGION_START_OFFSET
    for current_header, next_header in zip(headers, headers[1:]):
        assert current_header.payload_end_offset == next_header.offset
    assert headers[-1].payload_end_offset == len(original_professional_tp3_bytes)


def test_triangle_container_payload_matches_verified_triangle_block(
    original_professional_tp3_bytes: bytes,
):
    headers = decode_surface_region_containers(original_professional_tp3_bytes)
    triangle_header = next(header for header in headers if header.object_type == 14)

    assert triangle_header.offset == 431888
    assert triangle_header.record_count == TRIANGLE_RECORD_COUNT
    assert triangle_header.record_size_bytes == 24

    payload = slice_container_payload(original_professional_tp3_bytes, triangle_header)
    assert payload == original_professional_tp3_bytes[
        TRIANGLE_BLOCK_OFFSET : TRIANGLE_BLOCK_OFFSET + TRIANGLE_RECORD_COUNT * 24
    ]


def test_type2_payload_contains_vertex_block_as_final_53_records(
    original_professional_tp3_bytes: bytes,
):
    assert hashlib.sha256(original_professional_tp3_bytes).hexdigest() == EXPECTED_FILE_SHA256

    type2_header = decode_container_header(original_professional_tp3_bytes, 374918)
    assert type2_header.object_type == 2
    assert type2_header.offset == 374918
    assert type2_header.payload_offset == 374936
    assert type2_header.payload_end_offset == 381392
    assert type2_header.record_count == 269
    assert type2_header.record_size_bytes == 24
    assert type2_header.payload_size == 269 * 24

    payload = slice_container_payload(original_professional_tp3_bytes, type2_header)
    assert len(payload) == 269 * 24

    vertex_block = original_professional_tp3_bytes[380120:381392]
    assert len(vertex_block) == 53 * 24

    first_vertex_record_index = (380120 - type2_header.payload_offset) // 24
    assert first_vertex_record_index == 216
    assert payload[216 * 24 : 269 * 24] == vertex_block
    assert payload[216 * 24 : 269 * 24] == payload[-53 * 24 :]
    assert 216 + 53 - 1 == 268


def test_count_name_and_origin_candidates_are_inside_type17_payload(
    original_professional_tp3_bytes: bytes,
):
    headers = decode_surface_region_containers(original_professional_tp3_bytes)
    metadata_header = next(header for header in headers if header.object_type == 17)

    assert metadata_header.offset == 433730
    assert metadata_header.record_count == 1
    assert metadata_header.record_size_bytes == 332

    payload = slice_container_payload(original_professional_tp3_bytes, metadata_header)
    payload_start = metadata_header.payload_offset
    assert payload[COUNT_VERTEX_OFFSET - payload_start : COUNT_VERTEX_OFFSET - payload_start + 4] == b"\x35\x00\x00\x00"
    assert payload[COUNT_TRIANGLE_OFFSET - payload_start : COUNT_TRIANGLE_OFFSET - payload_start + 4] == b"\x4c\x00\x00\x00"
    assert payload[30:54].decode("utf-16le").rstrip("\x00") == "design grade"
    assert ORIGIN_CANDIDATE_X_OFFSET - payload_start == 160
    assert ORIGIN_CANDIDATE_Y_OFFSET - payload_start == 168


def test_decode_surface_region_containers_rejects_truncated_payload(
    original_professional_tp3_bytes: bytes,
):
    with pytest.raises(TINValidationError, match="exceeds TP3 bounds"):
        decode_surface_region_containers(original_professional_tp3_bytes[:-1])


def test_decode_container_header_rejects_invalid_header_size(
    original_professional_tp3_bytes: bytes,
):
    tampered = bytearray(original_professional_tp3_bytes)
    tampered[SURFACE_REGION_START_OFFSET + 2 : SURFACE_REGION_START_OFFSET + 4] = b"\x10\x00"

    with pytest.raises(TINValidationError, match="unsupported header size"):
        decode_container_header(bytes(tampered), SURFACE_REGION_START_OFFSET)


def test_decode_surface_region_containers_rejects_out_of_bounds_start_offset(
    original_professional_tp3_bytes: bytes,
):
    with pytest.raises(TINValidationError, match="outside TP3 bounds"):
        decode_surface_region_containers(
            original_professional_tp3_bytes,
            start_offset=len(original_professional_tp3_bytes) + 1,
        )


def test_decode_surface_region_containers_allows_eof_start_offset(
    original_professional_tp3_bytes: bytes,
):
    assert (
        decode_surface_region_containers(
            original_professional_tp3_bytes,
            start_offset=len(original_professional_tp3_bytes),
        )
        == ()
    )

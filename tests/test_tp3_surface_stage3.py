import hashlib

from tinforge.tp3.surface_decoding import (
    COUNT_TRIANGLE_OFFSET,
    COUNT_VERTEX_OFFSET,
    ORIGIN_CANDIDATE_X_OFFSET,
    ORIGIN_CANDIDATE_Y_OFFSET,
    TRIANGLE_BLOCK_OFFSET,
    TRIANGLE_RECORD_COUNT,
    VERTEX_BLOCK_OFFSET,
    VERTEX_RECORD_COUNT,
    VERTEX_RECORD_STRUCT,
    build_surface_tin_from_original,
    float64le_at,
    verify_stage3_surface_evidence,
)
from tinforge.tp3.writer import UnknownTP3FieldError, serialize_tp3

EXPECTED_FILE_SHA256 = "423926032d368d2ebce9ffa9acfba3c5e467f200a13b1470d214962b45cb3207"
EXPECTED_VERTEX_BLOCK_SHA256 = "045e128e0b7774a819e434055e0fc3d75d3b7b168b259df5283895e7cbbfa08a"


def test_original_professional_tp3_surface_stage3_verification(
    original_professional_tp3_bytes: bytes,
):
    assert hashlib.sha256(original_professional_tp3_bytes).hexdigest() == EXPECTED_FILE_SHA256

    evidence = verify_stage3_surface_evidence(original_professional_tp3_bytes)
    assert evidence.vertex_block_sha256 == EXPECTED_VERTEX_BLOCK_SHA256
    assert evidence.vertex_round_trip_exact

    assert evidence.vertex_count_header == 53
    assert evidence.triangle_count_header == 76
    assert evidence.vertex_count == 53
    assert evidence.triangle_count == 76
    assert evidence.edge_count == 128
    assert evidence.boundary_edge_count == 28
    assert evidence.euler_characteristic == 1
    assert evidence.all_vertices_used
    assert not evidence.has_zero_or_near_zero_triangles
    assert not evidence.has_non_manifold_edges
    assert evidence.reciprocal_adjacency_ok
    assert evidence.geometric_neighbor_edge_mapping_ok


def test_original_vertex_and_triangle_blocks_match_expected_lengths(
    original_professional_tp3_bytes: bytes,
):
    vertex_block = original_professional_tp3_bytes[
        VERTEX_BLOCK_OFFSET : VERTEX_BLOCK_OFFSET + VERTEX_RECORD_COUNT * VERTEX_RECORD_STRUCT.size
    ]
    triangle_block = original_professional_tp3_bytes[
        TRIANGLE_BLOCK_OFFSET : TRIANGLE_BLOCK_OFFSET + TRIANGLE_RECORD_COUNT * 24
    ]
    assert len(vertex_block) == 1272
    assert len(triangle_block) == 1824


def test_original_surface_count_headers_are_uint32le(
    original_professional_tp3_bytes: bytes,
):
    evidence = verify_stage3_surface_evidence(original_professional_tp3_bytes)
    assert evidence.vertex_count_header == 53
    assert evidence.triangle_count_header == 76
    assert COUNT_VERTEX_OFFSET == 433766
    assert COUNT_TRIANGLE_OFFSET == 433770


def test_origin_candidates_are_read_but_semantics_remain_hypothesis(
    original_professional_tp3_bytes: bytes,
):
    origin_candidate_x = float64le_at(original_professional_tp3_bytes, ORIGIN_CANDIDATE_X_OFFSET)
    origin_candidate_y = float64le_at(original_professional_tp3_bytes, ORIGIN_CANDIDATE_Y_OFFSET)
    assert origin_candidate_x == 295399.97869873
    assert origin_candidate_y == 4843987.442024235


def test_serialize_tp3_remains_fail_closed(
    original_professional_tp3_bytes: bytes,
):
    surface = verify_stage3_surface_evidence(original_professional_tp3_bytes)
    assert surface.vertex_round_trip_exact

    decoded_surface = build_surface_tin_from_original(original_professional_tp3_bytes)
    try:
        serialize_tp3(decoded_surface)
    except UnknownTP3FieldError:
        pass
    else:
        raise AssertionError("serialize_tp3() unexpectedly succeeded despite unknown TP3 fields")

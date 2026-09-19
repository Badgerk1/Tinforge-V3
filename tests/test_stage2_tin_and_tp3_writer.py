import json
from pathlib import Path

import pytest

from tinforge.surface import (
    SurfaceTIN,
    TinValidationError,
    Triangle,
    Vertex,
    build_triangle_adjacency,
    validate_tin,
    with_deterministic_adjacency,
)
from tinforge.tp3.writer import (
    TP3_SIGNATURE,
    TRIANGLE_RECORD_SIZE_BYTES,
    TriangleRecord,
    Tp3SerializationBlockedError,
    build_tp3_project_bytes,
    decode_triangle_record,
    deserialize_triangle_table,
    encode_triangle_record,
    serialize_triangle_table,
)


FIXTURE_PATH = (
    Path(__file__).resolve().parent / "fixtures" / "synthetic" / "tiny_surface.json"
)
GOLDEN_MANIFEST = (
    Path(__file__).resolve().parent / "fixtures" / "golden" / "REFERENCE_MANIFEST.json"
)


def _load_tiny_surface() -> tuple[SurfaceTIN, list[list[int | None]]]:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    surface = SurfaceTIN(
        name=fixture["name"],
        vertices=tuple(Vertex(*xyz) for xyz in fixture["vertices"]),
        triangles=tuple(Triangle(tuple(tri)) for tri in fixture["triangles"]),
    )
    return surface, fixture["expected_neighbors"]


def test_tiny_fixture_adjacency_is_deterministic_and_expected():
    surface, expected_neighbors = _load_tiny_surface()
    adjacency_a = build_triangle_adjacency(tri.vertex_indices for tri in surface.triangles)
    adjacency_b = build_triangle_adjacency(tri.vertex_indices for tri in surface.triangles)

    assert adjacency_a == adjacency_b
    assert [list(row) for row in adjacency_a] == expected_neighbors


def test_validate_tin_accepts_fixture_with_deterministic_neighbors():
    surface, _ = _load_tiny_surface()
    surface = with_deterministic_adjacency(surface)
    validate_tin(surface, require_neighbors=True)


def test_validate_tin_rejects_zero_area_triangle():
    surface = SurfaceTIN(
        name="degenerate",
        vertices=(Vertex(0.0, 0.0, 1.0), Vertex(1.0, 1.0, 2.0), Vertex(2.0, 2.0, 3.0)),
        triangles=(Triangle((0, 1, 2), (None, None, None)),),
    )
    with pytest.raises(TinValidationError, match="zero XY area"):
        validate_tin(surface)


def test_validate_tin_rejects_out_of_range_vertex_index():
    surface = SurfaceTIN(
        name="bad-index",
        vertices=(Vertex(0.0, 0.0, 0.0), Vertex(1.0, 0.0, 0.0), Vertex(0.0, 1.0, 0.0)),
        triangles=(Triangle((0, 1, 3), (None, None, None)),),
    )
    with pytest.raises(TinValidationError, match="out-of-range vertex"):
        validate_tin(surface)


def test_validate_tin_rejects_non_manifold_edge():
    surface = SurfaceTIN(
        name="non-manifold",
        vertices=(
            Vertex(0.0, 0.0, 0.0),
            Vertex(1.0, 0.0, 0.0),
            Vertex(0.0, 1.0, 0.0),
            Vertex(1.0, 1.0, 0.0),
            Vertex(0.5, 2.0, 0.0),
        ),
        triangles=(
            Triangle((0, 1, 2)),
            Triangle((1, 0, 3)),
            Triangle((0, 1, 4)),
        ),
    )
    with pytest.raises(TinValidationError, match="non-manifold edge"):
        with_deterministic_adjacency(surface)


def test_triangle_record_encode_decode_round_trip():
    record = TriangleRecord(vertex_indices=(10, 11, 12), neighbor_indices=(-1, 4, 5))
    encoded = encode_triangle_record(record)
    decoded = decode_triangle_record(encoded)
    assert len(encoded) == TRIANGLE_RECORD_SIZE_BYTES
    assert decoded == record


def test_triangle_table_serialization_is_deterministic_and_reparseable():
    surface, _ = _load_tiny_surface()
    bytes_a = serialize_triangle_table(surface)
    bytes_b = serialize_triangle_table(surface)

    assert bytes_a == bytes_b
    records = deserialize_triangle_table(bytes_a, triangle_count=len(surface.triangles))

    assert len(records) == len(surface.triangles)
    assert {i for rec in records for i in rec.vertex_indices} == set(range(len(surface.vertices)))

    decoded_neighbors = [list(rec.neighbor_indices) for rec in records]
    assert all(-1 <= n < len(surface.triangles) for row in decoded_neighbors for n in row)


def test_triangle_table_rejects_truncated_input():
    with pytest.raises(ValueError, match="does not match expected"):
        deserialize_triangle_table(b"\x00" * (TRIANGLE_RECORD_SIZE_BYTES - 1), triangle_count=1)


def test_decode_triangle_record_rejects_out_of_bounds_offset():
    with pytest.raises(ValueError, match="outside buffer"):
        decode_triangle_record(b"\x00" * TRIANGLE_RECORD_SIZE_BYTES, offset=1)


def test_writer_fails_closed_at_unknown_tp3_fields():
    surface, _ = _load_tiny_surface()
    with pytest.raises(Tp3SerializationBlockedError, match="UNKNOWN field"):
        build_tp3_project_bytes(surface)


def test_golden_reference_regression_anchors_are_unchanged():
    manifest = json.loads(GOLDEN_MANIFEST.read_text(encoding="utf-8"))
    entry = manifest["files"][0]
    observations = entry["verified_binary_observations"]

    assert entry["sha256"] == "423926032d368d2ebce9ffa9acfba3c5e467f200a13b1470d214962b45cb3207"
    assert observations["signature"] == TP3_SIGNATURE.decode("ascii")
    assert observations["triangle_record_size_bytes"] == TRIANGLE_RECORD_SIZE_BYTES
    assert observations["triangle_record_count"] == 76
    assert observations["triangle_vertex_index_range"] == [0, 52]
    assert observations["triangle_neighbor_index_range"] == [-1, 75]


def test_stage2_fixture_xyz_and_triangle_counts_round_trip():
    surface, _ = _load_tiny_surface()
    rebuilt = SurfaceTIN(
        name=surface.name,
        vertices=tuple(Vertex(v.x, v.y, v.z) for v in surface.vertices),
        triangles=tuple(Triangle(t.vertex_indices, t.neighbor_indices) for t in surface.triangles),
    )

    assert len(rebuilt.vertices) == len(surface.vertices)
    assert len(rebuilt.triangles) == len(surface.triangles)
    for a, b in zip(surface.vertices, rebuilt.vertices):
        assert a.x == pytest.approx(b.x)
        assert a.y == pytest.approx(b.y)
        assert a.z == pytest.approx(b.z)

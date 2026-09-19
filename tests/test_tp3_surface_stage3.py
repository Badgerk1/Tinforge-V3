import json
from pathlib import Path
import struct

import pytest

from tinforge.tp3.surface_decoder import (
    GOLDEN_DESIGN_GRADE_NAME,
    GOLDEN_DESIGN_GRADE_NAME_OFFSET,
    GOLDEN_DESIGN_GRADE_ORIGIN_X_OFFSET,
    GOLDEN_DESIGN_GRADE_ORIGIN_Y_OFFSET,
    GOLDEN_DESIGN_GRADE_TRIANGLE_COUNT,
    GOLDEN_DESIGN_GRADE_TRIANGLE_COUNT_OFFSET,
    GOLDEN_DESIGN_GRADE_TRIANGLE_TABLE_OFFSET,
    GOLDEN_DESIGN_GRADE_VERTEX_BLOCK_OFFSET,
    GOLDEN_DESIGN_GRADE_VERTEX_COUNT,
    GOLDEN_DESIGN_GRADE_VERTEX_COUNT_OFFSET,
    TP3_VERTEX_RECORD_STRUCT,
    TP3SurfaceDecodeError,
    decode_golden_design_grade_surface,
    parse_vertex_records,
)


FIXTURE_DIRECTORY = Path(__file__).parent / "fixtures" / "golden"
EVIDENCE_PATH = FIXTURE_DIRECTORY / "Purolator_NP_2026.design_grade_surface.json"


def load_surface_evidence() -> dict:
    return json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))


def load_surface_window() -> bytes:
    evidence = load_surface_evidence()
    window = bytearray(evidence["window_size_bytes"])

    vertex_offset = GOLDEN_DESIGN_GRADE_VERTEX_BLOCK_OFFSET - evidence["window_absolute_offset"]
    for index, vertex in enumerate(evidence["vertices"]):
        struct.pack_into(
            "<3d",
            window,
            vertex_offset + (index * TP3_VERTEX_RECORD_STRUCT.size),
            *vertex,
        )

    triangle_offset = GOLDEN_DESIGN_GRADE_TRIANGLE_TABLE_OFFSET - evidence["window_absolute_offset"]
    for index, (vertices, neighbors) in enumerate(
        zip(
            evidence["triangle_vertices"],
            evidence["triangle_neighbors"],
            strict=True,
        )
    ):
        struct.pack_into(
            "<6i",
            window,
            triangle_offset + (index * 24),
            *vertices,
            *neighbors,
        )

    struct.pack_into(
        "<I",
        window,
        GOLDEN_DESIGN_GRADE_VERTEX_COUNT_OFFSET - evidence["window_absolute_offset"],
        GOLDEN_DESIGN_GRADE_VERTEX_COUNT,
    )
    struct.pack_into(
        "<I",
        window,
        GOLDEN_DESIGN_GRADE_TRIANGLE_COUNT_OFFSET - evidence["window_absolute_offset"],
        GOLDEN_DESIGN_GRADE_TRIANGLE_COUNT,
    )
    name_bytes = (GOLDEN_DESIGN_GRADE_NAME + "\x00").encode("utf-16le")
    name_offset = GOLDEN_DESIGN_GRADE_NAME_OFFSET - evidence["window_absolute_offset"]
    window[name_offset : name_offset + len(name_bytes)] = name_bytes
    struct.pack_into(
        "<d",
        window,
        GOLDEN_DESIGN_GRADE_ORIGIN_X_OFFSET - evidence["window_absolute_offset"],
        evidence["origin_x"],
    )
    struct.pack_into(
        "<d",
        window,
        GOLDEN_DESIGN_GRADE_ORIGIN_Y_OFFSET - evidence["window_absolute_offset"],
        evidence["origin_y"],
    )
    return bytes(window)


def test_parse_vertex_records_matches_verified_window():
    evidence = load_surface_evidence()
    vertices = parse_vertex_records(
        load_surface_window(),
        offset=GOLDEN_DESIGN_GRADE_VERTEX_BLOCK_OFFSET,
        count=GOLDEN_DESIGN_GRADE_VERTEX_COUNT,
        base_offset=evidence["window_absolute_offset"],
    )
    assert len(vertices) == GOLDEN_DESIGN_GRADE_VERTEX_COUNT
    assert TP3_VERTEX_RECORD_STRUCT.size == 24
    assert (vertices[0].x, vertices[0].y, vertices[0].z) == pytest.approx(tuple(evidence["vertices"][0]))
    assert (vertices[-1].x, vertices[-1].y, vertices[-1].z) == pytest.approx(tuple(evidence["vertices"][-1]))


def test_decode_golden_design_grade_surface_matches_evidence():
    evidence = load_surface_evidence()
    surface = decode_golden_design_grade_surface(
        load_surface_window(),
        base_offset=evidence["window_absolute_offset"],
    )
    assert surface.name == GOLDEN_DESIGN_GRADE_NAME
    assert surface.origin_x == pytest.approx(evidence["origin_x"])
    assert surface.origin_y == pytest.approx(evidence["origin_y"])
    assert len(surface.vertices) == GOLDEN_DESIGN_GRADE_VERTEX_COUNT
    assert len(surface.triangles) == GOLDEN_DESIGN_GRADE_TRIANGLE_COUNT
    for actual, expected in zip(surface.vertices, evidence["vertices"], strict=True):
        assert (actual.x, actual.y, actual.z) == pytest.approx(tuple(expected))
    assert [list(triangle.vertices) for triangle in surface.triangles] == evidence["triangle_vertices"]
    assert [list(triangle.neighbors) for triangle in surface.triangles] == evidence["triangle_neighbors"]


def test_decode_golden_design_grade_surface_reproduces_verified_bounds():
    evidence = load_surface_evidence()
    surface = decode_golden_design_grade_surface(
        load_surface_window(),
        base_offset=evidence["window_absolute_offset"],
    )
    xs = [vertex.x for vertex in surface.vertices]
    ys = [vertex.y for vertex in surface.vertices]
    zs = [vertex.z for vertex in surface.vertices]
    global_xs = [surface.origin_x + value for value in xs]
    global_ys = [surface.origin_y + value for value in ys]
    assert min(xs) == pytest.approx(evidence["local_bounds"]["min_x"])
    assert max(xs) == pytest.approx(evidence["local_bounds"]["max_x"])
    assert min(ys) == pytest.approx(evidence["local_bounds"]["min_y"])
    assert max(ys) == pytest.approx(evidence["local_bounds"]["max_y"])
    assert min(zs) == pytest.approx(evidence["elevation_bounds"]["min_z"])
    assert max(zs) == pytest.approx(evidence["elevation_bounds"]["max_z"])
    assert min(global_xs) == pytest.approx(evidence["global_bounds"]["min_easting"])
    assert max(global_xs) == pytest.approx(evidence["global_bounds"]["max_easting"])
    assert min(global_ys) == pytest.approx(evidence["global_bounds"]["min_northing"])
    assert max(global_ys) == pytest.approx(evidence["global_bounds"]["max_northing"])


def test_decode_golden_design_grade_surface_rejects_truncated_window():
    evidence = load_surface_evidence()
    truncated = load_surface_window()[:-1]
    with pytest.raises(TP3SurfaceDecodeError, match="absolute offset"):
        decode_golden_design_grade_surface(
            truncated,
            base_offset=evidence["window_absolute_offset"],
        )


def test_decode_golden_design_grade_surface_rejects_count_corruption():
    evidence = load_surface_evidence()
    corrupted = bytearray(load_surface_window())
    relative_offset = GOLDEN_DESIGN_GRADE_VERTEX_COUNT_OFFSET - evidence["window_absolute_offset"]
    corrupted[relative_offset : relative_offset + 4] = (52).to_bytes(4, byteorder="little")
    with pytest.raises(TP3SurfaceDecodeError, match="expected 53 vertices"):
        decode_golden_design_grade_surface(
            bytes(corrupted),
            base_offset=evidence["window_absolute_offset"],
        )


def test_decode_golden_design_grade_surface_rejects_name_corruption():
    evidence = load_surface_evidence()
    corrupted = bytearray(load_surface_window())
    relative_offset = evidence["surface_name_absolute_offset"] - evidence["window_absolute_offset"]
    corrupted[relative_offset : relative_offset + 2] = "x".encode("utf-16le")
    with pytest.raises(TP3SurfaceDecodeError, match="expected surface name"):
        decode_golden_design_grade_surface(
            bytes(corrupted),
            base_offset=evidence["window_absolute_offset"],
        )

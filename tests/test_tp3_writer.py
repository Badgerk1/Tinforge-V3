import pytest

from tinforge.surface import SurfaceTIN
from tinforge.tp3.writer import (
    TRIANGLE_RECORD_STRUCT,
    UNKNOWN_VERTEX_LAYOUT_EVIDENCE,
    UnknownTP3FieldError,
    parse_triangle_records,
    serialize_tp3,
    serialize_triangle_records,
    triangle_records_from_surface,
)


def test_triangle_record_serialization_round_trips(tiny_surface: SurfaceTIN):
    data = serialize_triangle_records(tiny_surface)
    assert len(data) == len(tiny_surface.triangles) * TRIANGLE_RECORD_STRUCT.size

    records = parse_triangle_records(data)
    assert records == triangle_records_from_surface(tiny_surface)


def test_triangle_record_serialization_is_deterministic(tiny_surface: SurfaceTIN):
    first = serialize_triangle_records(tiny_surface)
    second = serialize_triangle_records(tiny_surface)
    assert first == second


def test_parse_triangle_records_rejects_truncated_input():
    with pytest.raises(ValueError, match="truncated"):
        parse_triangle_records(b"\x00" * (TRIANGLE_RECORD_STRUCT.size - 1))


def test_serialize_tp3_fails_closed_on_unknown_fields(tiny_surface: SurfaceTIN):
    with pytest.raises(UnknownTP3FieldError, match="UNKNOWN TP3 field"):
        serialize_tp3(tiny_surface)
    with pytest.raises(UnknownTP3FieldError, match="vertex XYZ storage layout"):
        serialize_tp3(tiny_surface)
    assert "surrounding metadata" in UNKNOWN_VERTEX_LAYOUT_EVIDENCE

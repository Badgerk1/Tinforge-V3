"""TP3 research and structural inspection/writer tools."""

from .inspector import Inspection, StringHit, candidate_f64, inspect_bytes, inspect_file, to_json
from .writer import (
    TP3_SIGNATURE,
    TRIANGLE_RECORD_SIZE_BYTES,
    Tp3SerializationBlockedError,
    TriangleRecord,
    build_tp3_project_bytes,
    decode_triangle_record,
    deserialize_triangle_table,
    encode_triangle_record,
    serialize_triangle_table,
)

__all__ = [
    "Inspection",
    "StringHit",
    "candidate_f64",
    "inspect_bytes",
    "inspect_file",
    "to_json",
    "TP3_SIGNATURE",
    "TRIANGLE_RECORD_SIZE_BYTES",
    "Tp3SerializationBlockedError",
    "TriangleRecord",
    "build_tp3_project_bytes",
    "decode_triangle_record",
    "deserialize_triangle_table",
    "encode_triangle_record",
    "serialize_triangle_table",
]

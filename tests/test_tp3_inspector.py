import hashlib
import pytest
from tinforge.tp3.inspector import candidate_f64, inspect_bytes, to_json


def test_inspection_is_deterministic():
    data = b"TP3?\x00design grade\x00A\x00B\x00C\x00D\x00"
    a = inspect_bytes(data)
    b = inspect_bytes(data)
    assert a == b
    assert a.sha256 == hashlib.sha256(data).hexdigest()
    assert to_json(a) == to_json(b)


def test_extracts_printable_string_with_offset():
    data = b"\x00\x01xxxxdesign grade\x00"
    r = inspect_bytes(data)
    assert any(h.value == "xxxxdesign grade" and h.offset == 2 for h in r.strings)


def test_extracts_utf16le_candidate_without_claiming_semantics():
    text = "Layer One"
    data = b"\xff" * 5 + text.encode("utf-16le") + b"\x01"
    r = inspect_bytes(data)
    assert any(h.encoding == "utf-16le" and h.value == text and h.offset == 5 for h in r.strings)


def test_candidate_f64_rejects_out_of_bounds():
    with pytest.raises(ValueError):
        candidate_f64(b"1234567", 0)
    with pytest.raises(ValueError):
        candidate_f64(b"12345678", -1)


def test_empty_input_is_safe():
    r = inspect_bytes(b"")
    assert r.size_bytes == 0
    assert r.strings == []
